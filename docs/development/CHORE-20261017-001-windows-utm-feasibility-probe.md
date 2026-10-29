# Windows UTM Feasibility Probe

ID: CHORE-20261017-001
Date: 2026-10-17
Owner: Human Owner
Driver: Codex
State: DR-0007 v0.10 S1–S8/A1–A15 accepted; follow-up plan prepared; execution pending
Source baseline: `a93f71c359c4f0a9d57fcfb50d5999160e870f77`
Current contract: [DR-0007 v0.10 Accepted](../decisions/DR-0007-windows-native-runtime-contract.md) — implementation contract accepted; no product activation

## Purpose And Authorization

Owner는 2026-10-17 B안을 유지하고 Windows UTM에서 제품 외부 격리 실험을 실행하도록 승인했다. 복구점·실행 경계·명령·시간 예산을 먼저 고정하고 실제 결과와 필요한 계약 변경안을 정리한다. 제품 구현은 시작하지 않는다. 이 기록은 이번 probe 실행의 단일 진행 정본이다. 이전 [계획과 R0](windows-utm-preliminary-plan.md#cross-agent-review-and-discussion)는 그대로 보존하며 정책·제품 구현의 승인으로 확대하지 않는다.

R0의 static request-changes와 Driver 처분을 입력으로 사용한다. Reviewer의 원래 Windows 가설은 정적 추론이었다. 아래 실제 관측과의 비교는 Driver가 수행했으며 Reviewer의 독립 재현으로 표시하지 않는다. 이번 probe는 최종 제품 runner나 full suite가 아니며 제품 지원·환경 qualification·계약 발효·결과 수락을 대신하지 않는다. DR-0003 intake 중 Windows Admission의 기준은 source baseline의 Development Index에서 읽었다. 해당 admission 기준과 시점 자체는 이번 기록으로 수정하지 않는다.

## Scope And Exclusions

제품을 import하지 않는 독립적인 Win32/CPython probe를 task-owned NTFS 합성 경로에서 실행한다. 확인할 묶음은 (1) runtime/ABI와 오류 전달, (2) lock 경합·handle 상속·process 종료, (3) file/directory flush, (4) 열린 reader와 replace/delete, (5) reparse·ancestor·mode·발행 상태, (6) 명시적 Python 및 합성 batch launcher다. 실제 선택한 API 후보에 필요한 관측만 수행한다.

제품 source/contract/capability 변경, Colvia lifecycle/full suite, 실제 adopter, 다른 작업/VM, credential 수집, 새 지원 선언과 Git publication은 제외한다. 결과 정리를 위한 source-only 문서와 private 실행 입력/출력만 작성한다. 신규 record ID는 현재 등록 worktree와 retained Git history에서 해당 날짜의 기존 ID 부재를 확인한 뒤 배정했다.

## Recovery And Execution Boundary

- 지정 VM을 정상 종료한 일관된 복구점을 먼저 만들고 실제 bytes/metadata와 복구 경로를 확인한다. 기존 clone이라는 설명만으로 복구 가능성을 인정하지 않는다.
- 표준 사용자·무자격증명 실행 profile, guest 내부 NTFS, task inputs/fixtures/logs, 합성 외부 canary와 child 회수를 확인한다. 개인 profile은 보존하며 credential 내용을 읽지 않는다.
- 입력은 먼저 로컬에 복사해 digest를 확인한다. probe 실행 중 host shared folder를 분리하고 VM network를 차단한다. 제품/원래 source checkout은 probe 실행 입력에서 제외한다.
- 불명확한 경계나 실패한 preflight는 실행을 막는다. 결과 회수 전에 VM rollback을 하지 않으며, 원출력을 보존한 뒤 필요한 설정 복원 범위를 기록한다.

## Commands And Budget

실행할 script bytes, 고정 명령, interpreter, cwd, 환경, 출력과 digest는 첫 mutating probe 전에 고정한다. 아직 미정인 명령을 실행한 것으로 기록하지 않는다.

각 family의 최대 실행 시간은 300초, 전체 runner는 1,800초다. child는 더 짧은 고정 timeout을 적용하고 종료 결과를 기록한다. 준비·작성 시간은 실행 예산 밖에서 따로 기록한다. 상한 초과는 incomplete이며 자동 증액하거나 반복하여 PASS를 만들지 않는다. 관측에 필요한 실패·거절·unavailable를 그대로 결과로 남긴다.

## Completion Criteria

1. 복구점과 실행 전후 경계의 증거를 보존한다.
2. 명령·시간·환경·입력·원출력·실행하지 못한 항목을 구분한다.
3. 잠금·경로·flush·replace·mode·launcher의 실제 관측을 R0 가설과 비교한다.
4. 필요한 계약 변경안과 여전히 미결인 부분을 구분하고 B의 후속 x64/물리 검증 방향을 유지한다.
5. 제품 구현이 없고 기존 source 및 다른 작업을 보존했음을 확인한다.

## Result And Next Decision

제품 외부 probe 1회를 완료했다. B안은 유지하되, 실측에 맞춘 계약 변경안과 아래 미해결 항목을 제품 구현 전에 검토해야 한다. 6개 family가 모두 종료됐다는 뜻이지 Windows 제품 지원이나 전체 검증 PASS가 아니다. 제품 source·계약·capability는 변경하지 않았다. 기존 R0 원문을 보존한 채 R1-P01 후속 정적 리뷰와 Driver 판단을 아래에 추가했다. Owner 결과/계약 수락과 제품 R1 qualification은 아직 없다. 따라서 이 record를 수락 완료나 closed로 표시하지 않는다.

```text
R0 가설 → probe 관측 → 후속 리뷰·Driver 판단 (완료)
         → 계약 초안·Owner 선택 (미결) → 별도 구현 승인 → 제품 검증·admission
```

### Execution And Evidence

| 항목 | 실제 결과 |
| --- | --- |
| 실행 환경 | Windows 11 Pro 26H2, build 26300.9711, ARM64 OS / ARM64 process, 내부 Fixed NTFS, Windows PowerShell 5.1.26100.9711 |
| Runtime | 공식 final GIL-enabled CPython 3.14.7 ARM64. PE `0xaa64`; 실행 파일 SHA-256 `5663411fd4dc477ea1d3b3dc1b61ae50745e13001507b3abf241fa167ef5e936` |
| Git | 기존 관측 2.56.0.windows.2. 이번 합성 index 실험은 사전 고정한 절대 경로의 실행 파일을 hash 확인 후 호출; SHA-256 `73b0434c5ff9e42491fea77c96cff73af7b6e8b0d54ae83372d9bc36ffd03ac3` |
| 계정·경계 | 전용 로컬 표준 계정. SYSTEM/elevated/admin SID 및 Administrators 직접 membership 없음. Credential Manager count 0, 검사한 private material 경로·auth override 변수 없음. 전체 시스템의 무자격증명을 증명한 것은 아님 |
| 실행 전 격리 | host VM config의 network device 0, directory sharing None. guest connected adapter·nonloopback IP·default route·SMB 연결 없음, Z 공유 접근 불가. Clipboard integration은 유지됐으며 probe는 clipboard를 읽지 않음 |
| 실행 명령 | 준비·해시 검사 후 로컬 `boundary-and-run.ps1`이 전용 `runtime\python.exe -I -B winprobe.py run` 실행. child는 `family <name> <local-fixture> <gate>`로 실행; Job Object 배정 후 fixture 시작. 제품 import 없음 |
| 실행 시각·예산 | 2026-10-17 13:58:52–13:58:57 UTC, 합계 4.985252초. family 300초 / 전체 1,800초 고정; 작성·환경 준비·UI 복구는 별도 |
| 종료 | ABI / locking / flush / replace / paths / launcher 6개 family exit 0, timeout 0, 종료 후 Job Object active process 모두 0. 개별 API 실패는 원출력에 그대로 기록 |
| 반출 검증 | 주 출력 18개와 사전검사 2개, 총 20개 파일의 크기·SHA-256 대조. 75개 top-level 관측 event. 실행 입력 3개가 실행 후에도 동일; 반출 시 task Python process 0 |

Exact 명령·입력과 복구 사용 절차는 private task의 `probe-01/host-boundary-plan.md`, 호스트 재검증은 `probe-01/verify-results.py`와 `verified-results.json`에 보존했다. 원출력은 private `guest-transfer/probe-01/guest-output-01/`의 JSONL·summary·boundary·console과 export/supplement manifest가 정본이다. 이 source 문서는 공개 가능한 해석이며 private 경로나 환경 식별정보를 복사하지 않는다.

| 고정 입력 | SHA-256 |
| --- | --- |
| `winprobe.py` | `3248e5e82a83b7c50057aeb99da1f7c8e1d0b714ee4ac8b78f83b8b6d6456cd2` |
| `boundary-and-run.ps1` | `b9bf0f4fa2cbc656a7d75f851c026bdbf4c769288c8be2c193438e945da9eb39` |
| `export-results.ps1` | `25480dcf4cb7105d1eb3bdb813a10f26155f9b8eae69bd9ede94761511dc9d98` |
| main export manifest | `d48671b78c13ccce5c484f493231da056bebadd88f55e5eb76a597e6d5a75d81` |

### Observations And R0 Comparison

| 영역 / R0 연결 | 실제 관측 | 의미와 한계 |
| --- | --- | --- |
| ABI·handle / F2·F8 | HANDLE 8, DWORD/LONG 4, OVERLAPPED 32 bytes, hEvent offset 24. missing CreateFile error 2, invalid flush error 6. handle inherit flag false, child의 같은 handle 값 조회 error 6 | ARM64의 선택한 ctypes 선언·오류 경로 관측. 비상속 flag 0은 직접 증거지만 child는 close_fds=True여서 error 6만으로 비상속을 입증할 수 없음. 명시적 전달·x64·전체 ABI는 미검증 |
| 잠금 / F2 | LockFileEx flags=3(EXCLUSIVE + FAIL_IMMEDIATELY) 잠금 중 contender는 error 33. 1-byte 파일의 잠긴 byte 0 read는 errno 13으로 거절(winerror 미포착). 해제 후·holder 강제 종료 후 다음 child에서 재획득 | 단일 관측의 종료 후 재획득 성공. 기존 blocking 대기·interrupt·해제 지연 상한·재진입은 미검증. 제품의 empty anchor와 이번 1-byte fixture를 구별 |
| 잠금 이름의 유지 / F2 | share=3(read/write)에서 잠긴 파일 unlink는 error 32. share=7(+delete)에서는 unlink와 같은 이름 재생성 후 별도 lock 획득 성공 | byte lock만으로 pathname의 동일 객체 유지가 보장되지 않음. lock anchor는 삭제 공유를 제외하고 사용 중 unlink/recreate를 금지하는 후보가 필요 |
| flush / F1 | 파일 fsync와 native flush 성공. Python directory open은 errno 13. BACKUP_SEMANTICS directory handle의 access=0/read flush는 error 5, write/readwrite flush는 성공 | 공통 helper의 POSIX directory open 문제를 재현. 표준 사용자의 쓰기 가능한 자체 NTFS directory에서 native 후보를 찾았음. API 성공을 POSIX 동등성·power-loss persistence나 D3 qualification으로 승격하지 않음 |
| replace·delete / F4 | Python reader, native share=3 및 share=7 reader가 열린 경우 모두 os.replace error 5. reader close 후 모두 성공. 실패 때 source가 남아 있고 destination은 OLD였음. readonly destination도 error 5 | share-delete opener만으로 교체 문제를 해결한다는 가설은 이 조합에서 성립하지 않음. error 5만 보고 sharing으로 단정할 수도 없음. 외부 reader·백신 원인이나 모든 rename API의 성질을 확정한 실험은 아님 |
| delete 이름 관측 / F4 | share-delete reader 상태에서 DeleteFile 성공, 재open error 2 및 exists=false | 이번 tuple에서는 이름이 즉시 사라짐. delete-pending이면 언제나 PermissionError라는 가설은 재현되지 않음; 다른 API/build까지 일반화하지 않음 |
| reparse / F2 | 표준 계정의 junction 생성 성공. attrs 1040, tag `0xa0000003`, is_symlink=false. 같은 process의 하위 경로 resolve/read는 합성 외부 canary로 이어짐. canary bytes는 유지. symlink 생성은 privilege error 1314 | is_symlink 검사만으로 junction을 막지 못함을 관측. st_mode/S_ISDIR 자체는 미기록이므로 제품 _require_kind 통과는 추론. unknown tag·cloud provider·hardlink·ACL은 미시험 |
| ancestor 유지 / F2 | access=0, share=3, BACKUP_SEMANTICS로 연 directory가 handle 보유 중 rename됨. close 후 재rename은 원래 이름 부재로 error 2 | 이 metadata-only handle 조합은 이름 고정에 실패. close 전후 두 번의 독립 성공/실패 비교로 읽으면 안 됨. data-access pinning 후보는 시험하지 못함. 기존 trusted-local 검사 수준과 추가 hardening을 구별하고, 더 강한 보장을 자동 선행 조건으로 만들지 않음 |
| mode·발행 / F3 | chmod 0600/0755 모두 stat 0666, 0444는 0444. Git index 100755인데 같은 확장자 없는 파일 stat는 0666. stage→없는 이름 rename 성공, 기존 nonempty directory 교체 error 5 | POSIX mode를 상태·Git mode의 근거로 사용하면 안 됨. staging/완성 rename은 후보일 뿐 중단 지점별 복구 계약은 아직 없음 |
| launcher / F5 | Python subprocess list → CreateProcess → Python argv 경로에서 공백·따옴표·메타문자·환경변수 표기·한글 10개를 그대로 반환. 합성 batch 내용 덮어쓰기(`batch_self_replace`)는 exit 0이지만 ORIGINAL-TAIL이 사라졌고 self-delete는 exit 1. 둘 다 EDIT-DONE은 출력 | programmatic 진입에 한정된 증거이며 PowerShell/cmd 인용 보장은 미시험. 실행 중 batch의 atomic replace는 미시험이며 이 case는 write_text 덮어쓰기다. 제품 launcher, CWD 독립·stdin·잘못된 runtime 거절·inventory lifecycle도 미시험 |
| batch 인자 harness / F5 | 두 wrapper command는 각각 exit 255/1; echo까지 정상 왕복하지 못함. 한 오류에 합성 `%COLVIA_PROBE_TOKEN%`의 치환값이 나타남 | 정상 .cmd argv 왕복 증거는 없음. list2cmdline의 내부 quote escape가 cmd 인용과 맞지 않는다는 정적 진단을 기록. 원출력은 보존하고 정상 인자·보안 취약점 재현으로 주장하지 않음 |

[CreateFileW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew)는 desired access와 share mode를 별도 인자로 정의하며, directory handle에는 BACKUP_SEMANTICS가 필요하다. [FlushFileBuffers](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers)의 write access 조건은 access별 이번 관측을 해석하는 근거다. 문서의 일반 설명과 단일 guest에서의 실제 결과를 구별한다. [LockFileEx](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-lockfileex)의 종료 후 해제 지연 가능성도 단일 재획득 성공으로 지우지 않는다.

F6의 successor/inventory/old-writer 판단은 기존 정적 분석 상태로 남는다. 이번 probe는 old product를 실행하지 않았다. F7의 실행 경계는 아래 증거로 보완했지만 제품 suite의 declared/discovered/executed ID ledger나 runner qualification은 아직 없다. F8의 B안과 후속 focused x64/물리 보완 방향은 유지하며, 이번 ARM64 관측을 x64 실행 증거로 쓰지 않는다. F9 timing amendment는 미수락 상태다. F10의 실행 예산과 고정 Git 호출은 이번에 구체화했고, 제품 구현은 통합된 기준 commit 확인 뒤에 제안한다.

### Contract Proposals — Not Accepted

다음은 이번 결과에 따른 Driver 변경안이다. 기존 규범 문서나 accepted DR을 수정하지 않았으며 각 안의 정확한 clause와 적용 window는 후속 검토에서 고정한다.

| 변경 대상 | 제안 | 구현 전에 남은 것 |
| --- | --- | --- |
| Lock·safe path: jsonio/workspace 및 Workspace Contract | Windows 전용 typed Win32 API와 비상속 handle; 안정된 lock anchor는 FILE_SHARE_DELETE 제외. 모든 ancestor/leaf reparse를 기본 거절하고 unknown은 non-pass. metadata-only ancestor handle을 race 방지 근거로 쓰지 않음 | 기존 trusted-local 검사·거절 수준을 보존하는 계약 목표와 최종 경로/identity 검증 후보를 명시. race-proof pinning을 필수로 올리지 않음. 선택한 설계의 보존·대기·interrupt 증거는 별도 구현/qualification 계획에서 검증 |
| Common durability와 transition D3 | file flush, write-access directory handle flush, rename 결과와 recovery를 별도 관측으로 둠. 필요한 directory flush 실패는 non-pass; NTFS이므로 자동 N/A 또는 PASS 금지 | 성공 관측이 어느 기능의 계약을 충족하는지 정의. 최초 Windows 범위에서 과거 checkout-1→entry-1 전환을 제외하는 안과 공통 helper는 분리. macOS D3 유지 |
| Replace·reader share와 exact retry | 우선 실패 phase·native error·보존된 old/new 상태를 남기는 안정 non-pass + 명시적 exact retry. delete-then-copy fallback과 무한 자동 retry 금지. 전체 reader 교체를 기본 해법으로 채택하지 않음 | error 5의 원인 구분과 실패 지점별 상태 분류. 제품에서 실제 선택한 API로 concurrent reader·중단·복구 oracle 확인 |
| Windows 상태·권한·Git mode | 상속 ACL 유지, 새 기밀성 주장 없음. 완성 상태는 검증된 staging/발행 관측으로 정의하고 0600/0755 흉내 금지. tracked mode는 index/manifest에서 가져옴 | standalone non-Git mode 표현, 부분 발행 상태·retry/repair 계약. 일반 ACL 안전성은 이번 시험으로 입증되지 않음 |
| Launcher·lifecycle·inventory | 명시적 지원 Python의 `-I -B` 진입을 최초안으로 권고. 새 상태/managed membership이 필요하면 successor window; fresh successor와 같은 window lifecycle을 우선 범위로 비교 | native-launcher criteria 충족 여부의 Owner 결정, 정확한 inventory와 audited old-writer fence. `.cmd`를 선택하면 정상 인자 harness와 자기 교체 대응을 별도로 검증 |
| B 지원 정책·timing | Windows 11 ARM64/x64 공통 정책과 대표 UTM 전체 검증 방향 유지. 실제 OS/process tuple을 따로 표시하고 x64·물리 보완은 후속 focused로 둠. formal admission은 live macOS Preview 이후 | B 및 timing named amendment 수락, 통합 기준 재확인, 제품 runner qualification/전체 검증의 정확한 계획. 추가 full matrix에는 구체 실패 메커니즘과 focused 불충분 이유 필요 |

### Boundary History And Recovery

1. Owner 승인으로 시험 VM만 task의 durable `vm/` 경로로 이동했다. 정상 종료 상태의 APFS 복구 사본 5개 파일, logical 92,160,170,768 bytes에 대해 SHA-256·크기·mode·owner·mtime·xattrs 일치를 확인했다. 읽기 전용 QCOW2 검사 오류 0. active VM boot는 확인했으나 복구 사본의 restore boot는 수행하지 않았다.
2. 첫 preflight는 WAN Miniport 표시와 접근 가능한 Z 공유 때문에 HOLD였다. probe fixture는 시작하지 않았다. exact pseudo-adapter를 기록하고 다른 Up adapter·nonloopback IP·default route를 검사하도록 입력을 보정했으며 이전 bytes와 새 manifest를 보존했다. 최종 실행 때 connected adapter 자체는 없었다.
3. UTM 4.7.5의 빈 registry만으로 active WebDAV가 분리되지 않았다. 재시작 뒤에도 Z가 기본 공유 root를 보여 두 번째 preflight가 HOLD였다. 공유 root 검사를 완화하지 않고 VM을 정상 종료해 directory share mode 자체를 None으로 설정했다. 그 뒤 host config와 guest 경계를 함께 확인한 preflight만 실행을 허용했다.
4. Owner가 직접 전용 계정의 인증정보를 설정하고 로그인했다. Driver는 인증정보를 읽거나 기록하지 않았다. 승인된 Process-scope RemoteSigned만 사용했고 실험·반출 shell 종료로 해제했다. persistent execution policy는 변경하지 않았다.
5. 실행 종료와 child 회수를 확인한 후 task 전송 폴더만 재연결해 원출력을 반출했다. 20개 파일과 입력 불변성을 검증한 뒤 shell을 종료하고 VM을 정상 종료했다. 최종 저장 config는 Network=[], DirectoryShareMode=None; registry 비움 및 stopped를 확인했다. Clipboard sharing 설정은 그대로다. rollback은 하지 않았다.

### Completion, Retention And Remaining Work

| 완료 조건 | 처분 |
| --- | --- |
| 복구점·실행 전후 경계 | 증거 보존. restore boot는 미수행으로 명시 |
| 명령·시간·환경·입력·원출력 | 6개 family 1회, 입력 3개 불변, 반출 20개 파일 검증. 준비 시간과 실행 예산 구분 |
| R0와 실제 관측 비교 | F1–F5 구체 관측 및 반증/한계 기록. F6–F10의 정적·정책·qualification 잔여 범위 구분 |
| 계약안·B 방향 | 위 변경안 작성. 수락·구현·admission은 미결 |
| 제품과 타 작업 보존 | source HEAD 동일, tracked diff는 Development Index의 navigation 2줄뿐. 본 record와 이전 plan은 source-only untracked 문서. 제품·다른 worktree·다른 VM을 수정하지 않음 |

보존 대상은 고유 입력·원출력·검증 기록, source worktree, active VM과 마지막 검증 복구 사본이다. consumer는 Owner의 결과/계약 판단, 필요한 후속 검토와 선택 시 재현·복구다. 종료 조건은 결과 처분과 구체 후속/복구 의존성 해소다. guest installer 임시 항목 2개는 task의 durable process-temp에 있고 metadata만 확인했으므로, 설치 복구/보존 조건 해소 전에는 삭제하지 않았다. 새 전체 source archive나 추가 복구 사본을 만들지 않았다.

변경된 active 경로는 위 승인된 VM 이동 1건이며 이번 반출 단계에서는 경로를 옮기지 않았다. 이번 probe 종료 단계에서 삭제한 파일은 없다. 이는 완료된 cleanup 주장과 다르다. 불필요한 host/guest 자료는 Owner 결과 처분과 구체 후속 필요가 확정될 때 기존 task record에서 다시 판단한다.

제품 변경이 없으므로 현재 adopter 업데이트는 필요하지 않다. 실제 adopter 설치 상태는 이번에 조사하지 않았다. 다음 판단 대상은 후속 리뷰를 반영한 계약 초안의 미결 선택이며, 새 실험·제품 구현·계약 발효·Git publication을 이 기록으로 자동 시작하지 않는다.

후속 리뷰 전 문서 검증: `marked 17.0.5`의 GFM으로 변경 문서 5개를 렌더링하여 code 밖 literal 강조 기호가 없음을 확인했다. local links 27개, 작성 부분 whitespace와 Git diff 검사, 기존 R0 원문·frozen packet 불변, source 결과의 private 식별정보 검사를 통과했다. 이는 문서 검증이며 제품 시험이 아니다.

## Cross-Agent Review And Discussion — R1-P01

### Request, Input Identity And Limits

2026-10-17 Owner 요청: “실측 결과와 계약 변경안을 Claude에게 후속 리뷰받고, 네 판단과 함께 정리해줘. B안은 유지하고 제품 구현은 아직 시작하지 마.” 이 요청으로 후속 정적 리뷰 1회와 해당 결과 기록을 수행했다. 제품 구현·VM 재실험·계약 수락·Git publication은 포함하지 않는다. Toolstead cross-review의 기록 형식을 사용하고, Owner의 직접 요청과 공통 review procedure에 따라 Claude CLI를 직접 호출했다.

- Driver: Codex. Reviewer: fresh Claude Code session의 `claude-opus-5-5`. Owner: human user.
- Round: R1-P01. 독립 probe 결과와 계약안의 후속 검토이며 제품 구현 R1/qualification이 아니다.
- 인증·과금 경로: `claude.ai` / `firstParty` subscription. provider override 없음. 키·토큰·계정 email은 기록하지 않았다.
- 도구·파일 접근·네트워크 조회·시험 실행을 허용하지 않았다. 고정 packet만 읽었고 실제 reported tools와 tool events 모두 0이었다. 구독 서비스로의 리뷰 요청 외 실행 권한은 주지 않았다.
- 고정 상한 1,200초; 실제 379.770초, exit 0, 1 turn. 입력 26개를 호출 전후 대조했고 drift 없음.
- Source baseline은 이 문서 상단 commit과 동일. tracked diff는 Development Index의 navigation 2줄뿐이며 SHA-256 `91f501b2077cfc175ae80edbddd2f56a32b71c2bcb6c6b7c1659d01c3e42a7ef`.
- 검토 당시 이 record SHA-256 `4cc5d752647a8d76f112b6dfb9a965b1f7ef87e58ca9c5f2a7b64406f7f02843`. 후속 문서 보정은 아래 Driver 처분이며 Claude가 다시 검토한 bytes가 아니다.
- Packet SHA-256 `a17230e61a48f33bdabe84f5ad5b819723311acdc7c5c785c4e7929b0f40f806`, 220,092 bytes. Request SHA-256 `2b31129ac998b3d1396d86fea9d44dcb805d0a1d651b4ea14d2dbce5157a513a`.
- Response SHA-256 `fbe384a05394c1f0eb6bccc0c70a2750136e28fc98b3af5d5fe70d2c0cb54066`, 21,958 bytes. private `r1-probe-review-01/`에 request, exact packet/inputs, final, 최소 CLI metadata를 보존했다.

Reviewer는 probe 코드·제공된 JSONL·기존 R0·계약안을 읽었지만 실제 Windows를 재실행하거나 host file digest/복구 사본을 직접 확인하지 않았다. fresh session과 다른 모델은 관점 분리를 제공할 뿐 독립 재현이나 완전한 검토를 증명하지 않는다.

### Verdict And Driver Judgment

| 대상 | Reviewer 판정 | Driver 판단 |
| --- | --- | --- |
| 실험 보고서 | conditional: 해석 보정 후 수락 가능한 수준 | 동의. 아래 범위 보정을 적용했으며 원출력은 불변. Owner 결과 수락을 대신하지 않음 |
| 계약 초안 작성 | conditional: 미결 slot을 남겨 지금 작성 가능 | 동의. 새 probe를 기본 선행 단계로 삼지 않고 현재 근거로 문안과 선택지를 작성하는 방향 권고 |
| 제품 구현 계획 | request-changes 수준: 아직 미완성 | 동의. 이번 작업은 구현을 시작하지 않음 |
| B안 | 반박할 architecture별 mechanism 없음, 유지 타당 | Owner 지시대로 유지. x64·물리 보완은 후속 focused; 현행 admission 기준의 발효 변경은 별도 수락 |

### Driver Disposition

`accept`는 지적의 반영, `revise`는 취지 수용과 권고 수정이다. 이 표는 Owner의 계약 선택을 대신하지 않는다.

| Finding | 판단 | 근거·처분·남은 항목 |
| --- | --- | --- |
| F1 · P1 · ancestor와 순환 gate | revise | 보안 모델은 trusted local account/cooperating agents이고 완전한 적대 race 방어를 약속하지 않는다. 검사 시점 reparse 거절과 기존 file identity 보존을 목표로 둔다. metadata-only 실험을 data-access pinning의 반증으로 확대하지 않는다. 제안 표의 과도한 구현 선행 조건을 보정했다. 다만 `GetFinalPathNameByHandleW` 문자열 비교만으로 모든 create/replace/alias/race가 해결됐다고 채택하지 않는다. 최종 경로·identity 검증은 설계 후보이며 추가 pinning은 선택한 경우에만 좁은 관측을 제안한다. P1의 핵심 위험을 거부한 것은 아님 |
| F2 · P2 · 잠금과 상속 증거 | accept | 모든 LockFileEx가 flags=3인 점, blocking/interrupt 미시험, close_fds=True 대조군의 한계, 1-byte fixture와 empty 제품 anchor 차이를 결과 표에 반영했다. delete-share 제외·비상속·고정 range·기존 대기 의미 보존을 계약 초안에 제안할 수 있다. 구현 방식이나 timeout은 자동 확정하지 않음 |
| F3 · P2 · flush 어휘·persist | revise | method/result/phase를 구별하고 errno 13을 성공으로 바꾸지 않는 방향 수용. 추가 정적 확인상 현재 flush 결과 dict는 typed record에 저장되지 않고 진단 CLI에 반환된다. 단순한 새 진단 어휘만으로 successor가 필수라는 결론은 아니다. 반면 read-only fsync는 fresh init에도 남아 있어 transition 제외만으로 해결되지 않는다. 아래 정적 표를 계약 입력으로 삼음 |
| F4 · P2 · replace 원인·retry | revise | os.replace 조합 한정의 반증, error 5 원인 단정 금지, PermissionError를 부재로 취급하지 않는 방향 수용. 기존 nonempty directory 교체 실패는 Windows 특유 증거로 쓰지 않는다. 자동 재시도 0회 + 명시적 exact retry를 계속 우선 권고한다. bounded 자동 retry는 이번에 추가하지 않으며 별도 필요가 있을 때 Owner가 선택. 실패 후 상태/digest를 읽을 수 없으면 unknown으로 보존해야 함 |
| F5 · P2 · launcher 범위·harness | revise | programmatic argv만 관측했고 cmd 정상 왕복 증거는 없다는 보정을 적용했다. explicit interpreter 우선안은 유지한다. 그러나 “shell 인용은 호출자 책임”만으로 native 진입 기준을 충족했다고 보지 않는다. 선택한 shell의 정확한 사용 예·필요한 인자·stdin·exit 검증은 제품 qualification에 포함해야 한다. 기존 인자를 축소하거나 새 stdin schema를 이번 리뷰로 자동 채택하지 않음 |
| F6 · P2 · mode와 window | accept | 구현 전에 module 배치·persist·도달 경로·old-reader 의미를 정적으로 비교한다. 아래 표는 현재 baseline의 판단이며 integrated 후보에서 다시 고정해야 한다. successor를 우선 권고하되 새 module/상태 의미 없이 entry-1을 보존할 수 있는 대안을 사실 확인 없이 배제하지 않음. 최종 window/membership은 Owner 미결 |
| F7 · P3 · 용어·경계 한계 | accept | junction st_mode 미기록, 같은 process의 하위 경로 resolve/read, errno 13만 포착한 read 거절을 명확히 했다. event 75개와 selected ABI layout의 정합성은 static 확인으로 구별한다. clipboard·restore boot의 한계는 보존하며 제품 runner qualification에서는 별도 경계 처분 필요 |

### Additional Static Checks By Driver

아래는 리뷰 수신 뒤 Driver가 같은 source baseline을 직접 읽은 추가 판단이다. Reviewer의 재검토나 Windows 재실행 결과가 아니다.

| 질문 | source 근거와 판단 | 계약에 미치는 영향 |
| --- | --- | --- |
| flush 결과 어휘가 typed record에 persist되는가? | `jsonio.py:100–129,186–234`의 반환값 사용과 전 source 호출 지점을 확인했다. `product.py:39–44`, `workspace.py:375–384`는 write helper 반환값을 버리고, 다른 `_sync_fd` 호출도 결과 dict를 저장하지 않는다. `sync_directory` 결과를 판정하는 별도 consumer는 transition `_entry_sync`다. `cli.py:128–132`는 durability diagnostic을 반환한다. 현재 이 결과 fields를 typed record에 저장하는 경로는 발견하지 못했다 | method/result를 진단에 명시하는 변화와 persisted schema 변경을 분리한다. 미래 receipt에 추가하면 그때 새 schema/window 영향 검토 필요 |
| transition 제외로 read-only fsync가 사라지는가? | 아니다. `product.py:1168`의 fresh init launcher, `workspace.py:380–382`의 기존 immutable member 재확인에 남는다. `product.py:610,756–762`의 transition 경로와 별개다 | 지원할 fresh/recovery 경로에 write-capable flush handle 설계를 포함해야 한다. 그대로 read-only fsync를 유지하려는 후보라면 그 경로의 좁은 실행 확인 필요 |
| 0600/0755 문제가 transition에만 있는가? | 부분/완성 prefix predicate는 transition에 집중돼 있지만 fresh init의 `product.py:1167`, same-window replace의 `1407–1420`, repair의 `1558–1563,1746`에도 chmod/fchmod·mode 관측이 있다 | 과거 transition 제외만으로 mode 문제가 모두 없어지지 않는다. Windows에서 지원할 경로별 상태·관측 의미를 초안에 명시 |
| 새 module과 old reader | `colvia:63–84`의 exact 11-module 검사, `product.py:329–347`의 exact inventory, `895–908`의 retained release 검증이 영향을 받음 | 새 module/managed member 또는 상태 의미 변경이면 successor 우선. 어느 과거 writer까지 안전하게 거절되는지는 exact 후보와 audited reader 집합으로 후속 검증 |
| 재시도와 경로 보장의 범위 | `SECURITY-AND-SUPPORT.md:5`, `WORKSPACE-CONTRACT.md:101–102,308`은 trusted-local boundary와 non-cooperating 변경 한계를 이미 둠. 기존 `jsonio.py:177`은 blocking flock | 완전한 race 방어를 추가 의무로 삼거나 잠금 timeout/자동 replace retry를 리뷰만으로 신설하지 않는다. 기존 의미 보존과 선택한 보강을 분리 |

### Recommended Next Scope And Owner Choices

권고는 추가 실험부터 반복하는 대신, 위 정적 판단을 반영해 미결 선택이 표시된 계약 초안을 작성하는 것이다. 이 리뷰 정리가 그 초안을 이미 수락하거나 제품 구현을 승인한 것은 아니다.

| 선택 | Driver 우선안 | 대안·판단 영향 |
| --- | --- | --- |
| 최초 lifecycle / window | fresh successor 및 같은 window lifecycle; Windows의 과거 transition/entry-1 이주는 최초 범위에서 제외 | 더 넓은 이주를 원하면 D3·mode·old-writer 범위가 커짐. successor 이름과 membership은 통합 후보에서 고정 |
| 경로 보장 | 기존 trusted-local 검사 수준 보존 + reparse 기본 거절 + handle identity/최종 경로 검증 후보 | data-access ancestor pinning을 추가 선택하면 B-1을 별도 좁은 probe로 제안. 지금은 필수 선행 실험으로 삼지 않음 |
| 진입·retry | explicit Python 진입, 자동 replace retry 0회 + 명시적 exact retry | `.cmd` 또는 bounded 자동 retry를 원하면 그 동작의 필요·새 증거·범위를 별도로 명시 |
| durability·mode | API method/result/phase 구별, power-loss 미주장, 상속 ACL 유지·Git index/manifest 의미 보존 | mandatory sync로 인정할 기능, Windows 상태 표식과 non-Git mode 표현은 정확한 clause로 Owner 선택 |
| B·timing | B 유지, formal admission은 live macOS Preview 이후 | B·timing의 named amendment 수락과 제품 실행 승인은 별개. 추가 full matrix는 구체 mechanism과 focused 불충분 근거가 있어야 함 |

추가 격리 관측은 선택 의존적이다. ancestor pinning, POSIX rename 또는 `.cmd`를 실제 후보로 고를 때만 필요한 최소 항목을 다시 제안한다. blocking lock/interrupt, empty anchor, 실제 shell 진입, 중단·복구, full normal/parent-optimized regression과 ID ledger는 선택한 제품 구현/qualification 계획의 시험으로 둔다. probe의 약 5초를 전체 suite 예산으로 사용하지 않는다.

### Actual Owner Decision And Retention

확인된 Owner 결정은 후속 리뷰 실행, Driver 판단 정리, B 방향 유지, 제품 구현 금지다. 결과 수락·계약안 수락·새 probe·제품 구현·publication은 아직 없다. Toolstead STATUS나 다른 task의 진행 상태는 변경하지 않았다. 기존 CHORE record 하나가 계속 진행을 소유한다.

request/packet/input identity/final/최소 metadata는 Owner의 이번 처분과 필요한 다음 비교가 consumer다. 최종 응답과 byte-identical인 partial stream, 0-byte stderr, 비어 있는 tool-temp는 process 종료·lsof 사용 없음·원문 반영을 확인한 뒤 삭제했다. 필수 request/packet/inputs/final/metadata/호출 script는 유지하며 active 경로는 바꾸지 않았다. probe 원출력, active VM과 마지막 복구점의 기존 결과/복구 의존성은 유지된다. 새 VM 실행·이동·rollback은 수행하지 않았다.

### Verbatim Reviewer Response

다음 fenced block은 최종 응답 21,958 bytes를 그대로 보존한다. 끝의 문서 구분 newline은 원문 밖이다. 위 Driver 보정을 재검토한 응답으로 해석하지 않는다.

````markdown
# R1-P01 후속 정적 검토: Probe 01 결과와 Windows 계약 변경안

**검토 경계.** 이 검토는 제공된 frozen packet의 bytes만 읽은 정적 검토 1회입니다. 도구 실행, 파일 접근, VM 접근, 시험 실행, 네트워크 조회는 하지 않았습니다. packet, manifest, raw 출력의 digest는 독립적으로 대조하지 못했습니다. 아래의 Windows/CPython 동작 설명 중 "추론"으로 표시한 부분은 공개 문서와 알려진 동작에 근거한 판단이며, 제가 재현한 결과가 아닙니다. 이 검토는 Owner 승인, 제품 qualification, admission을 대신하지 않습니다.

---

## 1. Verdict

- **실험 보고서: conditional (정정 후 수락 가능).** 기록된 관측은 대체로 raw JSONL과 probe 코드로 뒷받침됩니다. 실패, 거절, 한계도 정직하게 보존되어 있습니다. 다만 일부 행은 판별력이 없는 대조군이거나 harness 결함을 포함합니다. 증거가 허용하는 범위도 아래처럼 좁혀 적어야 합니다(F1, F2, F5, F7).
- **계약 초안 작성: 지금 착수 가능 (conditional).** lock anchor, reparse 거절, replace non-pass, mode/Git, 진입 형태 조항은 현재 증거와 공식 문서만으로 문안화할 수 있습니다. ancestor 경계와 durability 어휘는 Owner 선택 지점을 명시한 slot으로 남겨야 합니다.
- **제품 구현 계획: 아직 준비되지 않음 (request-changes 수준).** D1, D2, D4, D5, D6과 ancestor 경계 수준이 미결입니다. 일부 제안 문구는 구현이 끝나야 판단할 수 있는 조건을 gate로 두고 있습니다(F1, F6).
- **B안:** 이번 증거에서 B를 반박할 architecture별 failure mechanism은 나오지 않았습니다. B는 유지가 타당합니다.

---

## 2. Findings

### R1-P01-F1 (P1): ancestor 고정 실험은 후보 설계를 판별하지 못했고, 제안 문구는 순환 gate가 될 수 있음

- **위치:** CHORE 기록 86행, 101행; `winprobe.py:169–174`; `paths.jsonl:6–8`; 계획 115행; `SECURITY-AND-SUPPORT.md:5`; `jsonio.py:132–183`.
- **관측:**
  - access=0, share=3, BACKUP_SEMANTICS로 연 directory handle을 보유한 동안 다른 process의 rename이 성공했습니다.
  - close 후의 error 2는 첫 rename으로 원래 이름이 사라진 결과일 뿐이며, 독립적인 대조 실험이 아닙니다. 보고서도 이 점을 올바르게 적었습니다.
- **추론:**
  - 문서와 알려진 동작상, READ/WRITE/DELETE data access를 요청하지 않은 open은 share-access 검사에 참여하지 않습니다.
  - 따라서 이번 case는 "share 제한으로 ancestor를 고정한다"는 후보의 반례가 아닙니다. 그 후보를 애초에 시험하지 않은 것입니다.
  - "metadata-only handle은 근거로 쓰지 않는다"는 보고서의 결론은 맞습니다. 그러나 후보 설계가 가능한지는 여전히 미정입니다.
- **위험:**
  - 제안 101행은 "실제 안전한 ancestor open/identity 유지 방식"이 확정되기 전에는 write 구현을 승인할 수 없다고 둡니다.
  - 현 보안 모델은 same-account 적대 process를 배제합니다. POSIX 구현도 경로 기반 `lstat`/identity 비교에 머물며 ancestor race를 완전히 막지 않습니다.
  - Windows에만 race-proof 고정을 요구하면, 구현해 보아야 알 수 있는 조건이 계약의 선행 gate가 됩니다.
- **권고:** 계약 목표를 "POSIX와 동등한 검사 시점 거절, 기존 거절 조건의 약화 금지"로 고정하고 두 후보를 명시합니다.
  - (가) 모든 component의 reparse 속성을 검사합니다. 그다음 leaf를 handle로 열고 `GetFinalPathNameByHandleW` 결과를 기대 spelling과 비교합니다. 이후 쓰기와 flush는 그 handle로 수행합니다. 이 안은 문서 근거로 지금 문안화할 수 있습니다.
  - (나) data-access ancestor handle을 share-delete 없이 보유하는 pinning을 추가 hardening으로 둡니다. 이 안을 택할 때만 아래 B-1 관측이 필요합니다.
  - 어느 안이든 남는 race는 cooperating-account 한계로 명시합니다.
- **영향 gate:** 계약 초안의 workspace 경로 조항(초안 작성 자체는 막지 않음), 제품 write 구현.

### R1-P01-F2 (P2): lock 관측은 제안을 지지하지만, 시험한 것은 FAIL_IMMEDIATELY 단건임

- **위치:** `winprobe.py:43`, `:52`, `:74`, `:98`, `:220`; `locking.jsonl`; `abi.jsonl:4–5`; `jsonio.py:153–183`; `WORKSPACE-CONTRACT.md:308`.
- **관측:**
  - contender는 error 33을 받았습니다.
  - 잠금 byte에 대한 다른 process의 read는 errno 13으로 거절됐고, winerror는 포착되지 않았습니다.
  - unlock 후와 TerminateProcess 후에는 다음 child가 재획득했습니다.
  - share=3에서는 unlink가 error 32로 실패했습니다.
  - share=7에서는 unlink, 같은 이름 재생성, 별도 잠금이 모두 성공했습니다. 따라서 delete share를 제외하는 anchor 후보는 이 관측으로 뒷받침됩니다.
- **해석 한계:**
  - 모든 `LockFileEx` 호출이 flags=3(EXCLUSIVE|FAIL_IMMEDIATELY)입니다. 기존 `flock(LOCK_EX)`의 무기한 대기 의미는 관측되지 않았습니다.
  - 대기 중 ctypes 호출이 Ctrl+C 처리를 지연시킬 가능성도 관측되지 않았습니다(추론).
  - handle 비상속의 증거는 `GetHandleInformation` flag 0 하나입니다. child의 같은 값 조회 error 6은 판별력이 없습니다. `close_fds=True`에서는 상속 가능한 handle이라도 전달되지 않기 때문입니다.
  - mandatory byte-range가 read를 막은 결과는 1-byte 파일의 byte 0을 잠근 상태에서 나왔습니다. 현재 계약의 anchor는 empty regular file입니다.
- **권고:** 다음을 계약 문안으로 고정합니다.
  - anchor open은 read|write share(delete 제외), reparse 미추적, 비상속으로 합니다.
  - 고정 lock range를 명시합니다. anchor는 empty로 유지하고 그 내용의 read/write를 금지합니다.
  - 대기 의미는 기존과 같은 무기한 blocking으로 하며 timeout을 신설하지 않습니다.
  - 인터럽트 처리 방식(overlapped wait 또는 무기한 poll)은 구현 선택으로 남기되, 의미는 계약에 둡니다.
  - open 후 handle의 file identity와 경로 `lstat` 대조를 유지합니다.
  - delete 제외가 anchor 자체의 rename까지 막는지, 재획득 지연 상한, 같은 process 재진입은 (d) 단계 시험으로 둡니다.
- **영향 gate:** 계약 초안(작성 가능), 이후 focused 구현 시험.

### R1-P01-F3 (P2): directory flush 성공의 의미와 결과 어휘가 미정이며, window 결정과 연결됨

- **위치:** `flush.jsonl:4–13`; `winprobe.py:107–121`; `jsonio.py:100–129`, `:197`, `:215`, `:226–234`; `product.py:563–586`, `:609–610`; `WORKSPACE-CONTRACT.md:331`; CHORE 82행, 102행.
- **관측:**
  - Python의 directory open은 errno 13으로 실패했습니다. 이로써 R0-F1의 추론이 확인됐습니다. `sync_directory`의 `os.open`은 try 밖에 있으므로 lock 획득 전에 그대로 raise됩니다.
  - BACKUP_SEMANTICS handle의 flush는 write/readwrite access에서 성공했고, zero/read access에서는 error 5였습니다.
  - file fsync는 `r+b` handle에서만 관측했습니다.
- **판단:**
  - 보고서는 이 성공을 power-loss나 D3로 승격하지 않았으며, 이는 정확합니다.
  - 증거가 허용하는 것은 "표준 사용자 소유 NTFS directory에서 write-access handle open과 API 성공"까지입니다.
  - `product.py:610`의 read-only handle `os.fsync` 형태는 미관측입니다.
- **위험:**
  - Windows에서 같은 `"pass"` 토큰을 반환하면, 메커니즘이 다른 POSIX directory fsync와 같은 의미로 읽힙니다.
  - 반대로 새 토큰을 쓰면, 그 값이 기록에 persist되는 경우 old reader 기준의 의미 변경이 됩니다(F6).
  - 결과가 persist되는지는 packet만으로 판단할 수 없습니다.
- **권고:**
  - 어휘를 지금 문안화합니다. 결과에 method를 구분해 남기고, open 실패와 flush 실패를 각각 sync 단계의 non-pass로 둡니다. errno 13을 `unavailable`로 재분류하는 것은 금지하고, `power_loss_claim: not-claimed`는 유지합니다.
  - persist 여부와 read-only fsync 호출 지점은 정적 call-graph audit로 결정합니다. probe는 필요하지 않습니다.
  - D1에서 Windows transition을 제외하면 D3는 macOS 전용으로 남습니다. 제외하지 않는다면 Windows의 flush 성공이 D3를 충족하는지는 Owner가 결정합니다.
- **영향 gate:** D5, D1, D2.

### R1-P01-F4 (P2): replace 반증은 os.replace 경로에 한정되며, error 5는 원인을 구분하지 못함

- **위치:** `replace.jsonl:1–15`; `paths.jsonl:13`; `winprobe.py:126–157`; CHORE 83–84행, 103행.
- **관측:**
  - 세 가지 reader 조합 모두 error 5였고, reader close 후에는 성공했습니다.
  - 실패 시 source는 존속했고 destination은 OLD였습니다.
  - readonly destination과 비어 있지 않은 directory 교체도 같은 error 5였습니다.
  - share-delete reader가 열린 상태에서 `DeleteFile`이 성공했고, 이름은 즉시 사라졌습니다.
- **판단:**
  - R0-F4의 "share-delete opener로 해결" 가설은 이 tuple의 `os.replace`(MoveFileExW 경로)에서 반증됐습니다.
  - POSIX rename semantics 경로는 시험하지 않았습니다.
  - 같은 winerror 5가 sharing, readonly, nonempty 세 원인에 공통으로 나타났고 sharing violation(32)도 아니었습니다. 따라서 원인 분류는 불가능합니다.
  - 비어 있지 않은 directory 교체는 POSIX에서도 실패하는 연산이므로 Windows 특이 근거가 아닙니다.
  - delete 즉시 소멸은 POSIX delete 의미가 기본값인 build 성질로 추정되며, build/filesystem에 의존할 수 있습니다(추론).
- **권고:**
  - 계약을 다음처럼 문안화합니다. replace 실패는 phase, winerror, 관측된 source/destination 존재와 digest, destination readonly 속성을 남기는 안정 non-pass로 처리합니다. 원인 추정 문구와 delete-then-copy fallback은 금지합니다. 이름 관측 중의 PermissionError도 "부재"가 아니라 안정 non-pass로 다룹니다.
  - 자동 재시도는 Owner 선택입니다. 0회로 할지, 기록되는 bounded 결정적 재시도로 할지 정하며, 무한 재시도는 금지합니다.
  - POSIX rename 관측은 optional입니다. 현재 Python reader(launcher bootstrap의 `read_bytes` 포함)는 delete share 없이 열기 때문에, rename API만 바꿔서는 효과가 제한적입니다(추론).
- **영향 gate:** D6.

### R1-P01-F5 (P2): launcher 증거는 programmatic argv까지만 입증하며, cmd case는 harness 결함임

- **위치:** `launcher.jsonl:1–5`; `winprobe.py:196–209`; CHORE 88–89행, 105행; 계획 129행.
- **관측과 판단:**
  1. **명시적 Python argv:** 10개 인자의 왕복은 Python list → CreateProcess → CRT 파싱 경로에서만 관측됐습니다. 사람이나 agent가 PowerShell 5.1 또는 cmd에서 입력하는 진입은 시험하지 않았습니다. PowerShell 5.1의 legacy native 인자 전달(내부 `"` 처리)과 cmd의 `%VAR%` 확장 및 메타문자 처리는 shell 계층의 문제입니다(추론). 따라서 이 결과를 "명시적 interpreter 진입은 임의 인자를 보존한다"로 확대하면 안 됩니다.
  2. **cmd wrapper:** command 문자열을 list 원소로 전달했기 때문에 `list2cmdline`이 내부 따옴표를 `\"`로 escape했습니다. cmd는 이 escape를 해석하지 않습니다. case 1의 stderr에 `\"`가 그대로 나타난 것이 그 흔적입니다. 따라서 `.cmd` argv에 대한 증거는 0입니다. `%...%` 치환값이 나타난 것은 `cmd /c` 명령줄 자체의 확장입니다.
  3. **batch_self_replace:** 덮어쓴 내용이 원래 2행 끝의 offset보다 짧았습니다. 그래서 cmd가 offset 기준으로 재개했을 때 EOF를 만나 tail을 실행하지 않았는데도 exit 0이었습니다. 이는 offset 기반 재읽기를 지지하며, "명령이 조용히 빠졌는데 성공 exit"이라는 false-success 위험을 보여 줍니다. 새 bytes를 같은 offset에서 실행하는 경우와 rename 기반 교체는 관측되지 않았습니다. self-delete의 exit 1은 R0의 메커니즘을 재현합니다.
- **권고:**
  - 보고서를 정정합니다.
  - 계약은 "절대 경로의 지원 interpreter + `-I -B`" 진입으로 하고, argv 보존 보장 범위를 "표준 Windows 인용 규칙으로 구성한 명령줄"로 명시합니다. shell 인용은 호출자 책임으로 하고, 특수 payload는 stdin JSON으로 받습니다.
  - `.cmd`는 Owner가 선택할 때만, 문자열 명령줄을 쓰는 정상 harness와 rename 교체 관측을 추가합니다.
  - 이번 결과는 `.cmd`의 위험을 오히려 강화했으므로 explicit 진입 우선안을 지지합니다.
- **영향 gate:** D4.

### R1-P01-F6 (P2): mode/Git 문제는 확인됐고, window 결정은 구현 없이 정적으로 닫아야 함

- **위치:** `paths.jsonl:9–12`, `:19–20`; `work.py:128`; `colvia:71–79`; `product.py:329–347`; CHORE 87행, 104–105행.
- **관측:**
  - chmod 0600/0755는 stat 0666, chmod 0444는 0444(attrs 33)였습니다.
  - Git index는 100755인데 같은 파일의 stat은 0666이었습니다. 따라서 `work.py:128`은 이 파일을 100644로 유도합니다. R0-F3이 확인됐습니다.
  - staging directory를 없는 이름으로 rename하는 것은 성공했습니다.
- **위험:**
  - 제안 105행의 "필요하면 successor window"는 조건부라는 점에서 옳습니다.
  - 그러나 window 결정은 몇 가지 축에 좌우됩니다. Windows 코드를 새 module에 두면 11-module 검사 때문에 entry-1을 유지할 수 없습니다. 기존 module 안에 두는 경우와는 결론이 다릅니다. persist되는 결과 어휘(F3)와 0600/0755 predicate의 지원 경로 도달 여부(D1)도 같은 축입니다.
  - 이를 "구현 후 판단"으로 미루면 순환이 생깁니다.
- **권고:**
  - 계약 초안 전에 정적 결정표를 만듭니다. 항목은 module 배치, persist 어휘, predicate 도달 여부, Git으로 운반된 Windows 생성 상태를 old entry-1 macOS reader가 만났을 때의 의미입니다.
  - 하나라도 semantic change가 있으면 successor로 갑니다. 아니면 entry-1 유지도 비교 후보로 둡니다.
  - standalone non-Git target의 실행 bit 표현은 Owner 선택입니다.
  - staging rename은 발행 primitive의 후보일 뿐입니다. 중단 지점별 상태표는 계약 작업으로 남습니다.
- **영향 gate:** D1, D2, 계약 초안.

### R1-P01-F7 (P3): 보고서 정정 사항과 경계 잔여

- **보고서 정정:**
  - handle 대조군의 판별력 한계를 적습니다(F2).
  - junction의 `lstat` st_mode/`S_ISDIR`는 기록되지 않았습니다. attrs 0x410으로 directory임은 강하게 추정되지만, `_require_kind`를 통과한다는 것은 추론으로 표시해야 합니다.
  - "child 접근"은 같은 process 안에서 경로 아래 파일을 읽은 것이므로 용어를 정정합니다.
  - `resolve()`가 외부 canary로 해석된 결과는 `safe_target`의 strict resolve에 직접 관련되므로 명시하는 편이 좋습니다.
  - read 거절은 winerror 없이 errno 13만 나왔으므로 lock violation으로 단정하지 않습니다.
- **확인된 정합성:**
  - 제공된 JSONL의 event 수는 5+14+13+15+22+6=75로 보고서와 일치합니다.
  - 조기 return으로 빠진 관측은 보이지 않습니다.
  - OVERLAPPED와 Job Object 구조체 layout(32/144 bytes)은 64-bit 선언으로 타당합니다.
- **경계 잔여:**
  - symlink 생성이 1314로 실패한 것은 권한/Developer Mode에 의존하는 환경 성질입니다.
  - clipboard 유지와 restore boot 미수행은 이번 probe에서는 수용 가능합니다. 다만 제품 qualification runner의 경계에서는 명시적인 처분이 필요합니다.
- **영향 gate:** 보고서 정정만 해당합니다.

---

## 3. R0 처분 갱신 (요약)

| R0 | 갱신 |
| --- | --- |
| F1 | 일부 확인. directory open errno 13 확인, write-access directory flush의 API 성공 관측. read-only fsync와 내구성은 미관측. D1/D5 결정이 남음 |
| F2 | junction의 `is_symlink=false`와 외부 경로 해석 확인. `S_ISDIR`는 미기록, unknown tag는 미시험. 해제 지연은 단건이라 반증 아님. ancestor pinning은 판별되지 않음 |
| F3 | 확인 |
| F4 | 과장. share-delete opener 해법은 `os.replace`에서 반증, delete-pending PermissionError는 미재현, sharing 원인 단정 불가. (나)안 지지 |
| F5 | self-delete 재현, offset 재읽기 지지. 인자 재해석은 harness 결함으로 미관측. explicit 진입 지지 |
| F6 | 변화 없음. 정적 결정이 남음(F6) |
| F7 | probe 경계 충족. runner qualification과 ID ledger가 남음 |
| F8 | B를 반박할 메커니즘 없음. ARM64 layout만 관측. x64는 B 방향대로 후속 focused |
| F9 | 미수락 유지 |
| F10 | Git 절대 경로 고정으로 해소. 측정된 실행 약 5초는 P4 예산의 근거가 아님 |

---

## 4. 분류

### (a) 지금 가능한 보고서 정정

- F1: ancestor case가 후보 설계를 판별하지 못한 이유.
- F2: FAIL_IMMEDIATELY 단건, handle 대조군의 판별력 한계.
- F3: 증거가 허용하는 범위.
- F4: winerror 5의 원인 구분 불가, MoveFileExW 경로에 한정.
- F5: programmatic argv에 한정, harness 결함의 원인, self_replace의 실제 의미.
- F7: 위에 열거한 항목.

### (b) 추가 격리 관측

어느 것도 지금 실행하거나 승인하지 않습니다.

- **B-1 (조건부 필수).** ancestor pinning 후보 (나)를 택할 때만 필요합니다. 내용은 다음과 같습니다. 이는 F1의 계약 선택을 직접 가르는 관측입니다.
  - data-access directory handle(share=3)을 보유한 상태에서 해당 ancestor의 rename을 시도합니다.
  - descendant 파일을 data-access handle로 연 상태에서 ancestor rename을 시도합니다.
  - junction을 경유해 연 handle의 `GetFinalPathNameByHandleW` 결과를 확인합니다.
- **Optional (필요성이 낮음).**
  - read-only handle의 fsync. 정적 audit로 해당 호출이 지원 경로에 남는다고 확인될 때만 필요합니다.
  - POSIX rename semantics. Owner가 reader opener안을 원할 때만 필요합니다.
  - 정상 `.cmd` argv harness. `.cmd`를 선택할 때만 필요합니다.

### (c) Owner 선택

- D1: 최초 lifecycle 범위(Windows transition 제외 여부).
- D2: window. 정적 결정표에 근거합니다.
- D4: 진입 형태와 argv 보장 범위(programmatic 호출 vs shell 입력).
- D5: durability 어휘, 그리고 Windows flush를 mandatory sync 충족으로 인정할지.
- D6: 재시도 정책.
- ancestor 경계 수준: parity + 최종 경로 검증 vs pinning.
- standalone non-Git target의 mode 표현.
- B와 timing amendment의 수락.

### (d) 이후 승인된 구현·qualification 단계의 시험

- lock: 대기형 잠금과 인터럽트, 재획득 시간 oracle, 같은 process 재진입.
- 경합과 중단 지점별 복구(W06).
- reparse/unknown tag, 8.3, case, ADS, hardlink(W04). symlink fixture를 어떻게 공급할지 포함.
- 백신이나 열린 reader가 있을 때의 replace.
- PowerShell 5.1/7과 cmd 입력 예시, CWD 독립 실행, stdin, 잘못된 runtime의 거절.
- full normal/parent-optimized suite와 ID ledger.

---

## 5. 계약 초안 가능성과 다음 단계

**지금 작성할 수 있는 조항.** lock anchor(F2), 모든 component의 reparse 기본 거절과 open 후 handle identity 검증(F1의 (가)안), replace 안정 non-pass(F4), mode/Git 원천(F6), explicit 진입(F5).

**slot으로 남길 조항.** D1, D2, D5, D6과 ancestor 경계 수준.

**구현이 필요하지 않은 결정.** D2와 D5의 persist 여부는 정적 audit로 닫을 수 있습니다. 구현 완료를 선행 조건으로 두지 않아도 됩니다.

**권고하는 최소 다음 단계.**

1. (a)의 정정을 반영합니다.
2. module 배치, persist 어휘, predicate 도달, read-only fsync 호출 지점에 대한 정적 결정표를 작성합니다.
3. 위 조항으로 slot이 명시된 계약 초안을 작성합니다.
4. Owner가 (c)를 결정합니다.

probe-02는 pinning, POSIX rename, `.cmd` 중 하나를 선택할 때만 범위를 좁혀 제안합니다. 제품 구현은 시작하지 않습니다.

---

## 6. 타당한 점과 독립 검증의 한계

**타당한 점**

- preflight HOLD를 완화하지 않고 공유 모드 자체를 None으로 바꿨습니다.
- 입력을 동결하고 digest를 검증했으며, 결과가 이미 있으면 자동 재시도를 거부했습니다.
- Job Object를 배정한 뒤에 fixture를 시작하는 gate를 두었습니다.
- 개별 API 실패를 그대로 보존했습니다.
- scope event(`power-loss 미시험`, `product_launcher_tested=false` 등)를 명시했습니다.
- `batch_self_replace`가 atomic 교체가 아니라는 점과 directory flush가 power-loss 주장이 아니라는 점을 스스로 적었습니다.
- B와 후속 focused 방향을 유지하고, ARM64 결과를 x64 증거로 쓰지 않았습니다.

**한계**

- 저는 raw 출력이 probe 코드의 실제 실행 결과인지 재현하지 않았습니다. 20개 파일과 3개 입력의 digest도 대조하지 않았습니다.
- share-access 비참여, MoveFileExW와 POSIX rename의 차이, cmd의 offset 재읽기, PowerShell 5.1의 인용 동작, `list2cmdline`의 escape에 관한 설명은 문서와 알려진 동작에 근거한 추론입니다.
- packet에 없는 source 경로(persist 여부, `_write_exact`, 지원 call graph 전체)는 판단하지 못했습니다.
````

### Follow-Up Record Verification

R1-P01 final 21,958 bytes의 SHA-256와 본문 내 verbatim 일치를 확인했다. 기존 R0 원문·frozen packet도 불변이다. GFM 렌더링·code 밖 literal 강조 기호·local link·작성 whitespace·private 식별정보·Git diff 검사를 통과했다. 제품 tracked diff는 없고, 이번 변경은 기존 source-only record의 증거 범위 보정·후속 리뷰·Driver 판단 및 이전 plan의 pointer 현행화다. 별도 제품 시험이나 재리뷰 PASS를 주장하지 않는다.

## Contract Draft Preparation — 2026-10-17

Owner는 후속 리뷰와 Driver 판단을 반영한 계약 초안, 미결 선택별 권고안·근거 작성을 승인했으며 B 유지·추가 실험 금지·제품 구현 금지를 명시했다. 이 범위에서 [DR-0007: Windows Native Runtime Contract](../decisions/DR-0007-windows-native-runtime-contract.md) revision 0.1을 작성했다. 기존 R1-P01은 이 새 Draft bytes를 리뷰한 결과가 아니다.

DR-0007은 계약 선택을 소유하고, 이 CHORE record는 계속 진행·검증·Owner 처분을 소유한다. 새 Work나 두 번째 progress registry를 만들지 않았다. DR-0007은 등록 worktree의 현재 문서와 retained all-ref history에서 미사용을 확인한 뒤 배정했다. 이는 원자적 예약이 아니므로 통합 전에 번호 충돌을 재확인한다.

작성 범위는 S1–S8의 제안 문안, 대안·근거·미검증 항목, named amendment map과 승격 조건이다. B는 유지하며, 지원 대상과 관측 tuple을 나누고 formal admission은 live macOS Preview 이후로 제안했다. successor 이름·membership·mode·필수 sync phase·native 진입 및 나머지 계약 선택은 Owner 미결이다. 현행 기술 계약·Development Index의 admission criteria는 바꾸지 않았다.

이번 검증 계획은 변경 문서의 GFM·local link·whitespace·disclosure 검사, R0/R1 원문·frozen inputs 보존과 제품 tracked diff 없음 확인이다. 추가 probe·제품 suite·reviewer 호출은 하지 않는다. STATUS/PLAN cascade는 Draft이므로 발동하지 않으며 다른 task의 상태도 변경하지 않는다. 제품 변화가 없으므로 현재 adopter update는 필요하지 않고 실제 설치 상태는 미확인이다.

초안과 기존 원출력·리뷰 증거는 Owner 선택과 다음 exact 비교의 입력으로 보존한다. 이번 단계에서는 active 경로 변경이나 삭제가 없으며, VM/마지막 복구 사본은 기존 결과·복구 처분을 위해 유지한다. 초안 작성 완료는 계약 수락·task close·publication이 아니다.

### Draft Verification

DR-0007 revision 0.1은 UTF-8 28,302 bytes, SHA-256 `8053b06be2ec8d2c79cf74e20eae9aa56d5e7cb8cac8c7b97d2263e099ec194a`다. GFM 렌더링·code 밖 literal 강조 기호·local path/heading links 21개·작성 whitespace·disclosure 검사를 통과했다. 문서 3개를 검사했고 R0/R1 원문·frozen packet/request 불변과 제품 tracked diff 없음을 확인했다. 첫 링크 검사에서 발견한 anchor 1개를 고친 뒤 재검증했다. Draft의 Decision/Rationale/Consequences는 비어 있고 S1–S8은 미결 상태다.

검증 결과는 문서 품질과 입력 보존에 한정된다. 새 제품 실행·실험·독립 리뷰 결과는 없다. 원문·초안과 최소 입력 식별/검증 자료는 Owner 선택 및 다음 exact 비교를 위해 기존 task 위치에 보존하며, 이 consumer가 해소되면 정리 필요를 다시 판단한다. 별도 전체 source 사본은 만들지 않았다.

## Cross-Agent Review And Discussion — R1-D01

Recorded: 2026-10-18 KST
Target: [DR-0007 Draft 0.1](../decisions/DR-0007-windows-native-runtime-contract.md)
State: Review completed; Driver recommendations recorded; Owner choices pending

### Request And Exact Review Boundary

Owner는 DR-0007을 Claude에게 리뷰받고 지적별 Driver 판단과 미결 선택별 최종 권고를 정리하되, B 유지·추가 실험 금지·제품 구현 금지를 명시했다. 이 라운드는 그 요청에 따른 정적 문서 리뷰다. Driver는 Codex, Reviewer는 fresh Claude Code session의 `claude-opus-5-5`, arbiter는 human Owner다. 공통 review procedure와 cross-review 기록 형식을 따랐다.

광범위한 source/code·실험 원출력을 포함하려던 호출은 자동 승인 심사가 외부 전송 범위 부족을 이유로 거절했고 실행되지 않았다. 실제로 전송한 것은 Owner가 지정한 DR-0007 한 문서뿐이다. 도구·추가 파일/링크 접근·웹·시험을 허용하지 않았으며 실제 tools와 tool events는 0이었다. Reviewer는 이전 실측·코드·R1-P01을 재확인하지 않았고 초안에 적힌 주장으로만 읽었다. 아래 Driver의 로컬 정적 대조는 그 한계를 보완한 별도 판단이며 Claude가 검토한 입력에 소급 포함하지 않는다.

- Exact target: Draft 0.1, 28,302 bytes, SHA-256 `8053b06be2ec8d2c79cf74e20eae9aa56d5e7cb8cac8c7b97d2263e099ec194a`. 리뷰 뒤에도 이 bytes를 유지했다.
- Packet: 문서 한 개의 line-numbered text와 검토 경계, 29,763 bytes, SHA-256 `202b6ff362093ea763c4b2b35d5b8bfcb5fc3c564a77bbd96b97580630745148`.
- Request SHA-256: `c0428a8172d9cc4fe09649212029744b3a4635fe7a9aee2bce40c6476d2feaf7`.
- Final response: 26,127 bytes, SHA-256 `7af67b21922878134381c9a01d6e1374ba5cd4c674f417fcef3edb700e41c78b`.
- CLI 2.1.302; non-secret auth는 `claude.ai` / `firstParty` subscription. provider override 없음. 키·토큰·계정 email은 기록하지 않았다.
- 2026-10-17 14:59:30–15:03:30 UTC, 240.062초, exit 0. 고정 상한 1,200초. 입력 한 개와 source HEAD·tracked diff를 호출 전후 비교했고 drift 없음.

DR-0007의 “이 bytes 자체의 Claude 리뷰는 아직 없다”는 작성 시점의 문구로 보존했다. 현행 리뷰 상태는 이 dated record가 설명한다. 이번 요청은 초안 개정 적용을 요구한 것이 아니므로 원안의 조항·revision·미결 표기는 바꾸지 않았다. 아래는 차기 문안에 반영할 권고이며 아직 수락된 계약이 아니다.

### Verdict And Driver Judgment

| 판단 대상 | Claude 판정 | Driver 판단 |
| --- | --- | --- |
| 의사결정 자료로서 초안 | approve | 동의. 정책·대안 선택을 논의할 근거는 충분하다 |
| exact 계약 수락 준비 | request-changes | 동의. 관측 가능한 의미와 범위의 빈칸을 채우기 전 일괄 수락을 권고하지 않는다 |
| 구현 계획 준비 착수 | conditional | 취지 수용, 순서는 수정. 읽기·계약 보완·실행 계획의 문서 작성 자체를 계약 최종 수락 뒤로만 묶지 않는다. 설계와 계획은 문서로 함께 구체화할 수 있고, 실제 제품 mutation은 필요한 계약 수락과 실행 승인 뒤에만 한다. 이번 요청은 그 계획 작성/실행을 자동 시작하지 않는다 |
| B 방향 | 유지 | 유지. x64·물리 PC 전체 반복이나 물리 PC 선행 gate를 추가하지 않는다 |

### Findings And Driver Disposition

P1 3개, P2 5개다. `accept`는 지적 취지·처분을 수용하고, `revise`는 취지를 수용하되 일부 해석·권고를 수정한다. 지적 수용은 Owner의 계약 선택이 아니다. P1을 근거 없이 방어하거나 무시한 항목은 없다.

| Finding | 판단 | Driver 처분과 이유 |
| --- | --- | --- |
| F1 · P1 · 계약 의미와 구현 메커니즘의 순환 | accept | 의미와 메커니즘의 표를 아래에 제시한다. API·flag·poll 간격까지 계약 수락의 선행 조건으로 만들지 않는다. 반대로 취소·실패·복구의 관측 가능한 의미를 구현자 재량으로 미루지 않는다. 문서화와 제품 mutation의 승인 경계를 구분해 순환을 없애는 방향을 권고한다 |
| F2 · P1 · fresh successor의 old-writer·교차 OS 노출 | revise | 이주를 제외해도 audited cooperating writer의 successor 거절은 필요하다. 거절을 확인하지 못한 조합은 미지원으로 남기며 단순 잔여 위험 표기로 qualification을 통과시키지 않는다. 최초 Windows fresh/same-window와 기존 macOS 기본 동작 보존을 권고한다. 다만 모든 OS 이주를 반드시 새 DR 하나로 분리하라는 요구는 과하다. 이주는 별도 명시 범위/수락으로 다루고 기존 DR의 named amendment도 가능하다 |
| F3 · P1 · blocking과 취소 의미 | revise | 무기한 대기·사용자 interrupt 종료 의미를 계약에 넣는 데 동의한다. “한 번도 lock을 획득하지 않고 mutation 없음”은 지나치다. 획득과 interrupt가 경합할 수 있고 기존 helper는 대기 전 scratch anchor를 만들 수 있다. mutation section 진입 전 취소라면 종료 시 lock/handle을 남기지 않고 authority·content를 쓰지 않는다고 정한다. 이미 진입한 작업에는 실제 prefix·복구 규칙을 적용한다. POSIX/Windows interrupt 동작을 새로 재현한 것은 아니다 |
| F4 · P2 · 진단 전용 실패 phase와 재flush | revise | 디스크 보존과 실패 출력 보존을 구분하고, 승인된 exact apply/recovery에서 재검증·필요한 재flush를 하는 방향을 권고한다. read-only status/doctor에서 재flush하지 않는다. 재flush 성공은 그 시점의 새 관측이며 과거 durability 성공을 소급 증명하지 않는다. 또한 기존 “필수”와 “unsupported 반환을 허용하는 공통 helper”를 구분해야 하므로 모든 namespace flush가 이미 mandatory라는 해석은 채택하지 않는다 |
| F5 · P2 · explicit Python 진입의 전제 | revise | 절대 interpreter·지원 build 확인·실제 shell/argv/stdin·동시 실행 및 self-update 검증을 포함한다. 그러나 `-I` import 경로가 현재 빠졌다는 결론은 아니다. 현 launcher는 검증 후 `sys.path`를 구성하고 이미 isolated/no-bytecode를 요구한다. CPython 파일 공유 설명은 Reviewer의 일반 지식이며 이번 tuple의 재현으로 쓰지 않는다. PowerShell 7.3+를 즉시 새 필수 의존성으로 정하지 않고 현재 5.1 tuple을 최초 qualification 대상으로 권고한다 |
| F6 · P2 · ancestor 검사 경계 | accept | volume root부터 target root까지의 절대 경로 chain과 실제 검사 대상 경로까지의 chain을 명시한다. 기존 content membership/ignore·Git topology 범위를 바꾸거나 모든 무관한 디렉터리를 재귀 조사하는 계약으로 확대하지 않는다. reparse·판별 불가는 거절하고 리디렉션/cloud 배치의 비지원 사례를 문서화한다 |
| F7 · P2 · mode 미결이 숨은 범위 축소가 됨 | revise | 새 untracked/non-Git 파일에 문서화된 논리 mode 기본값을 두는 안을 우선한다. 다만 “retained manifest가 있으면 재사용”은 어느 manifest가 현재 mode authority인지 불명확하다. 일반 snapshot이 임의 과거 manifest를 고르지 않게 한다. Git은 검증한 index/tree, 일반 Windows non-Git/untracked는 공개된 기본 규칙, exact recovery는 원래 참조한 manifest의 계약을 따른다. non-Git `100755` 생성·변경/복구를 지원하려면 별도 명시 입력·provenance 계약이 필요하며 최초 범위에서 이를 미지원으로 명시하는 제한안을 권고한다 |
| F8 · P2 · retry 호출·token 의미 | revise | 새 retry 명령 없이 기존 operation과 그 operation의 recover 조건을 재사용한다는 방향은 수용한다. 현재 lifecycle token은 request digest로 계산되고 init exact recovery는 같은 request·candidate·confirmation을 요구한다. “소비된 token이면 새 preview”라는 가정은 현재 근거가 없어 추가하지 않는다. operation/state가 달라지면 기존 stale/refusal 규칙을 따르며 token을 임의 갱신해 pending 상태를 우회하지 않는다 |

### Local Static Cross-Checks By Driver

아래는 같은 `a93f71c359c4f0a9d57fcfb50d5999160e870f77`에서 Driver가 직접 읽은 근거다. Reviewer에게 전송하지 않았으며 새 실험이나 실행 결과가 아니다.

| 질문 | 로컬 source 근거 | 판단 범위 |
| --- | --- | --- |
| 잠금 취소 전에 scratch가 생기는가? | `jsonio.py:135–181`의 parent 준비, O_CREAT anchor open, directory sync가 blocking flock보다 앞선다 | “아무 파일도 바뀌지 않는다”를 취소 보장으로 쓰지 않는다. 실제 interrupt 전달/지연은 미검증 |
| 모든 sync 결과가 같은 의무인가? | `jsonio.py:100–129`: file fsync는 예외 전파, macOS fullfsync는 unavailable/error를 반환값에 기록. directory는 EINVAL/ENOTSUP만 unavailable로 반환하고 다른 오류는 전파. 공통 callers는 반환값을 버리는 경우가 있고 transition `_entry_sync`는 pass를 요구한다 | method·phase별 필수/허용 unavailable 구분이 필요하다. Windows directory flush를 NTFS라는 이유로 자동 PASS/N/A로 바꾸지 않는다 |
| Windows에서 Git mode가 이미 기록에 쓰이는가? | `work.py:213–263`은 index mode를 검사하지만 members만 모은 뒤 `_stable_file`이 반환한 stat-derived mode를 TreeEntry에 쓴다. `snapshot`은 Work/manifest ref를 인자로 받지 않고 whole-project 두 관측을 비교한다 | index mode의 실제 사용과 untracked/non-Git 기본 정책이 필요하다. 임의 retained manifest fallback은 새 authority 선택 규칙을 만들 수 있으므로 비권고 |
| isolated import 경로가 없는가? | `colvia:49–83,87–110`은 installed 경로의 isolated/bytecode 조건과 exact module bytes를 확인하고 검증된 payload/src를 sys.path에 추가한다. explicit source 경로도 직접 구성한다 | 기존 보호를 Windows에 보존·검증할 대상이다. 새 동작이 이미 성공한 것은 아님 |
| lifecycle token이 단회 소비형인가? | `product.py:1024,1123,1371,1431,1625,1693,1868,1941`에서 canonical request digest의 앞 16자를 사용한다. Workspace Actual Init And Recovery는 같은 request/source/confirmation의 recover와 completed replay를 명시한다 | 현재 lifecycle 경로에 단회 소비 규칙을 발명하지 않는다. 각 operation의 상태·recover 옵션·허용 prefix는 그대로 검증해야 한다 |

### Contract Meaning And Plan Detail

| 계약에서 선택할 의미·범위 | 구현 계획에서 고정할 메커니즘 |
| --- | --- |
| B와 지원/미관측 표시, 최초 Windows lifecycle, predecessor 거절, macOS 기본 동작 유지 | exact window 이름·ordered membership, module 배치, audited artifact 집합과 구체 pair 검증 |
| reparse 검사 경계·unknown 거절·기존 trusted-local 비보장 | handle API, identity fields, final-path/alias 비교 순서, 필요 시 pinning 방식 |
| timeout 없는 대기, interrupt 후 비보유·authority/content 보존, 재진입 거절 | polling/overlapped 여부, 대기 간격, fixed range·empty-anchor handling, handle 정리 구현 |
| 필수/선택 sync 구분, failure 범주, 명시적 recovery의 새 관측 의미 | 호출 지점별 phase 대응표, API/flag, diagnostic 이름, 오류 code 매핑과 주입 지점 |
| mode 출처·기본값·지원하지 않는 mode 변경, 기존 replay 의미 | policy/schema의 exact 표현, index 관측 안정성, prefix predicate, mode 적용·검사 순서 |
| native 진입 허용 형태와 필요한 입력 보존, 자동 retry 0 | exact interpreter/shell tuple, 명령 예, argv/stdin/exit oracle, 기존 recover 인자별 표 |

의미 결정과 이 표의 구체 설계는 문서로 함께 준비할 수 있다. 최종 contracted schema/reader 의미나 지원 범위를 바꾸는 계획 세부가 발견되면 그 부분을 다시 Owner에게 올린다. 별도 매개변수마다 반복 승인을 만들지는 않는다. 지금은 리뷰와 권고 정리만 수행했다.

### Final Driver Recommendations For S1–S8

“최종”은 이번 라운드의 Driver 권고를 뜻한다. Owner가 선택했거나 제품이 지원한다는 뜻이 아니다. B 방향은 이미 지시됐으며 다시 선택을 요구하지 않는다.

| 선택 | 이번 최종 권고와 이유 | Owner에게 남는 선택 | 계획·qualification에 남길 항목 |
| --- | --- | --- | --- |
| S1 | B 유지. ARM64/x64는 공통 정책 대상, exact tuple은 실측, 나머지는 미관측으로 표시한다. 대표 UTM 전체 검증과 x64 ABI/API 집중 보완을 사용하고 물리 PC는 필수 gate가 아니다. formal admission은 live macOS Preview 이후다 | 이 방향의 named admission 문안·표시 범위 수락. 미관측 x64를 실측 완료라고 표시하지 않음 | 기존 열 가지 criteria를 항목별로 매핑. 실제 x64 검사 전 x64 실측 표기 금지. full matrix 추가에는 mechanism·focused 불충분 근거 필요 |
| S2 | Windows는 fresh successor + same-window lifecycle을 우선한다. 기존 macOS 기본 window/init/update를 이 작업으로 바꾸지 않는다. Windows predecessor mutation과 cross-window 이주는 최초 범위에서 거절한다. 알려진 cooperating old writers가 successor를 거절하는 경계는 fresh에도 필요하다 | 최초 범위, 기존 macOS 유지, predecessor 진단/쓰기 거절 정책. 이주는 별도 명시 범위이며 새 DR를 무조건 요구하지 않음 | source→target→operation 표, exact window/membership/reader 집합, 실패 prefix와 거절 전 write 범위. macOS regression 의무 유지 |
| S3 | volume root→target root 및 실제 검사 대상까지의 경로 chain을 검사하고 reparse/판별 불가를 거절한다. 기존 trusted-local 경계를 유지하며 pinning이나 완전한 race 차단을 필수화하지 않는다 | 검사·unsupported 경계의 문안 수락 | identity와 final-path 검증, 별칭·junction·mount/cloud 사례, 기존 membership/ignore 범위 보존 |
| S4 | 안정 anchor·delete share 제외·비상속 handle·timeout 없는 대기·재진입 거절을 권고한다. mutation section 전 interrupt는 최종 lock/handle 비보유와 authority/content 무기록으로 정의한다. 정상 scratch anchor는 남을 수 있다 | 취소 의미와 scratch 예외 수락 | polling/overlapped 등 메커니즘, empty anchor·range·Ctrl+C·획득 경합·child 비상속·종료 정리. 새 계약 전 필수 probe로 올리지 않음 |
| S5 | 기존 필수/허용 unavailable 구분을 phase별로 대응한다. 필수 sync 실패는 non-pass, 출력은 method/result/phase를 구분한다. 새 receipt 필드 없이 진단을 우선하고, 승인된 exact recovery에서 필요 단계 재flush를 새 관측으로 수행한다 | 필수 의미의 대응 원칙·진단 전용·복구 관측 의미. 모든 directory flush를 새로 mandatory로 올리려면 별도 정책 선택 | file fsync·common directory unavailable·macOS fullfsync·D3의 차이를 call-site 표로 고정. read-only status에서는 flush 금지. 필요한 read-only fsync 경로를 write-capable 후보로 대체·검증 |
| S6 | Git tracked mode는 검증한 index/tree에서 가져온다. Windows 일반 untracked/non-Git에는 `100644`라는 문서화된 논리 기본값을 권고하고 preview/진단에 출처를 드러낸다. 이는 권한·기밀성·실행 가능성 판정이 아니다. 일반 snapshot은 임의 과거 manifest를 mode authority로 삼지 않는다 | 공개된 기본값과 제한된 최초 범위 수락. non-Git에서 `100755` 의도 생성·변경/그 의미가 필요한 복구는 최초 미지원으로 명시하는 안을 권고. 이를 지원하려면 별도 명시 입력·provenance 의미 선택 | exact recovery는 원 참조 manifest의 의미를 보존하고 지원 불가면 거절. mode 기본 정책·새 파일·index 안정성·snapshot/worker/replay 영향과 policy/schema를 고정. 원본·과거 record를 100644로 재작성하지 않음 |
| S7 | 절대 경로의 지원 Python + `-I -B`를 native 진입으로 인정하는 안을 권고한다. `.cmd`는 최초 범위에서 제외하고 현재 guest의 Windows PowerShell 5.1을 최초 qualification 대상으로 삼는다. 5.1 지원이 입증됐다는 뜻은 아니다 | native criterion 해석, 최초 shell 대상. 필요한 입력을 5.1에서 보존하지 못하면 지원을 선언하지 않고 PowerShell 7 계열의 exact 대안 또는 기존 입력 경로 설명을 다시 제시 | 기존 `--input` file/stdin과 argv를 실제로 확인. 새 stdin schema나 입력 축소는 금지. interpreter/runtime gate·isolated import·concurrent reader·self-update 검증 |
| S8 | 자동 retry 0, delete-then-copy 금지, 기존 operation의 명시적 재호출을 사용한다. 원 request·token·candidate와 각 recover 규칙을 유지하고 새 token 소비/새 retry 명령을 만들지 않는다 | 이 재시도 정책과 실패 분류 의미 수락 | pre-publication / post-publication-pre-flush / post-required-flush / unknown의 API별 매핑. completed replay와 pending recovery 차이, 실패 후 bytes/identity 재검증. 기존 승인이 포괄하는 재호출에 별도 human 승인 단계를 자동 추가하지 않음 |

S6의 `100644` 기본값은 v0.1의 “모르면 조용히 100644”와 구별되는 공개 정책 제안이다. 여기서 100644/100755는 content manifest의 논리 mode이며 Windows 파일 실행 가능성이나 ACL 권한을 뜻하지 않는다. non-Git 전체를 제외하는 대신 특정 mode 의도의 최초 지원 한계를 명시하는 절충안이다. 이는 새로운 Driver 권고로서 Owner가 선택해야 하며, Claude가 이 제한안까지 검토·승인한 것은 아니다. 별도 mode registry나 sidecar를 기본으로 신설하지 않는다.

### Recommended Next Document Changes And Remaining Decisions

다음 문서 개정 후보는 F1의 의미/메커니즘 구분, S2의 old-writer·macOS 경계, S3의 ancestor 범위, S4의 취소 문구, S5의 보존/재flush·필수 phase 구분, S6의 명시 기본값·지원 제한, S7의 정확한 qualification 대상, S8의 operation별 재호출 의미다. “모든 S가 미결” 대신 B는 지시됨, named 문안과 나머지 선택은 미결로 표시하고, B-1 설명·열 가지 admission criteria의 상세 매핑도 포함한다. 이 목록은 이번에 DR-0007 v0.1을 수정했다는 뜻이 아니다.

권고안의 핵심 정책을 Owner가 선택한 뒤 그 선택으로 Draft와 구현 계획의 문서를 함께 구체화하는 것이 다음 범위다. 정확한 계약 수락과 제품 실행 승인은 그 준비 결과를 보고 판단한다. pinning·대체 rename·`.cmd`는 실제로 선택할 때만 좁은 추가 관측 필요를 검토한다. 현재 권고안 때문에 새 probe를 즉시 시작할 필요는 없으며, 제품 qualification의 lock/flush/argv/중단/복구 검증은 그대로 남는다.

확인된 Owner 결정은 리뷰 실행·Driver 판단과 권고 정리·B 유지·추가 실험/제품 구현 금지다. S1–S8의 named 계약 수락, 초안 개정 적용, 구현 계획 실행, 결과 수락, activation, Git publication은 아직 없다. source 제품과 VM은 변경하지 않았다. 새 Work·registry·STATUS 갱신이나 adopter 적용도 없다. 제품 변경이 없으므로 현재 adopter update는 필요하지 않고 실제 설치 상태는 미확인이다.

### Verbatim Reviewer Response

아래 fenced block은 최종 응답 26,127 bytes를 그대로 보존한다. 구분용 newline은 원문 밖이다. 위 Driver 권고와 추가 정적 대조를 재리뷰한 응답으로 해석하지 않는다.

````markdown
# R1-D01 — DR-0007 Draft 0.1 독립 리뷰 (Reviewer: Claude)

**검토 대상**: `docs/decisions/DR-0007-windows-native-runtime-contract.md`, Draft 0.1. 패킷이 기재한 SHA-256은 `8053b06b…194a`, 크기는 28302 bytes입니다. 저는 해시를 직접 재계산하지 않았습니다.

**권한 경계**: 이 리뷰는 정적 텍스트 검토 결과입니다. 계약 수락·발효, 구현 승인, 제품 검증이 아닙니다(문서 l.172의 "리뷰 verdict는 선택이 아니다"와 같은 취지). Driver 처분과 Owner 결정을 대신하지 않습니다.

**표기 규칙**
- [추론: 소스 필요]: 패킷 밖 source 증거가 있어야 확정되는 판단입니다.
- [일반 지식]: Windows/CPython의 일반적 동작에 근거한 판단이며 이 패킷으로 검증하지 않았습니다.

---

## 1. Verdict

| 축 | 판정 | 요지 |
| --- | --- | --- |
| 의사결정 유용성 | **승인** (경미한 문서 정정 권고) | 선택지, 권고, 대안 비용, 미결이 S1–S8로 분리돼 있습니다. B 유지, 미관측 비승격, 권한 경계가 일관되게 지켜집니다. Owner가 선택을 내리기에 충분합니다. |
| exact 계약 수락 준비도 | **변경 요청** | 설계상 S1–S8이 모두 미결입니다(l.161). 계약이 고정할 의미와 구현 계획이 고정할 메커니즘의 경계도 일관되지 않습니다(F1). fresh 범위의 old-writer 노출(F2), 잠금 취소 의미(F3), flush 실패 후 복구(F4)가 의미 수준에서 비어 있습니다. |
| 구현 계획 준비 착수 준비도 | **조건부** | 새 실험은 필요 없습니다. 아래 두 가지가 충족되면 계획 준비가 가능하다고 봅니다. (a) Owner가 §3의 "지금 필요한 결정"을 exact revision에 기록, (b) F1 계층 표와 F2–F4 의미 문안 반영. 계획 착수의 권한 근거는 l.175의 설계 수락이며, 이 리뷰가 그 근거가 될 수는 없습니다. |

---

## 2. 핵심 Findings

### R1-D01-F1 · P1 · 계약 의미와 구현 메커니즘의 경계 불일치 (순환 위험)

**위치**: S3 l.90, S4 l.100, S5 l.108, S8 l.144, Open Points l.164–166, Promotion l.173·175, 흐름도 l.26

**근거 문안**
- 같은 성격의 결정이 서로 다른 단계로 배정돼 있습니다.
  - S4: "최종 acquisition/cancellation 방식… 구현 계획에서 고정"(l.100)
  - S8: "판정 표는 제품 계획에서 고정"(l.144)
  - S3: identity·검사 순서는 "구현 계획 전 확정"(l.90)
- 반면 Promotion은 "필수 flush phase·실패 prefix·native 진입을 실제 구현 계획이 소비할 만큼 구체화"를 계약 승격 조건으로 둡니다(l.173).
- 그런데 구현 계획은 설계 수락 이후에만 준비됩니다(l.175, l.26).

**결과**
- 취소 가능성, 실패 phase 분류처럼 사용자가 관측할 수 있는 **의미**가 구현 계획으로 밀려나면, 수락된 계약이 의미를 고정하지 못합니다.
- 반대로 API·flag 같은 **메커니즘**까지 계약 수락 조건으로 요구하면, 수락에는 계획이 필요하고 계획에는 수락이 필요한 순환이 생깁니다.

**최소 정정**: "계약 고정 항목 / 구현 계획 고정 항목" 2열 표를 Open Points에 추가합니다.
- 계약: 관측 가능한 의미 전부. 예: 무기한 대기와 취소 시 미획득·무변경, 필수 phase 집합, 실패 분류 범주, mode 출처 규칙, window 정책.
- 계획: Win32 API·flag·range·poll 간격·진단 어휘의 exact 이름.

### R1-D01-F2 · P1 · fresh successor에도 old-writer·교차 OS 노출이 남음

**위치**: S2 l.74–80, Options l.48, Amendment Map l.156

**근거 문안**
- old-writer refusal은 "이주 포함안"의 요구로만 서술됩니다(l.80).
- 동시에 l.80은 "단일 이름을 붙인 것만으로 과거 writer가 안전하게 거절되는 것은 아니다"라고 인정합니다.
- macOS 후보와의 호환·전환은 미결입니다(l.80).

**결과**
- Windows에서 fresh init한 successor workspace를 entry-1 writer가 만나는 경로가 있습니다. 예: 같은 checkout을 macOS 기존 설치로 여는 경우, 관리 상태가 Git으로 이동하는 경우 [추론: 관리 상태 추적 여부는 소스 필요].
- 이 경로는 이주를 제외해도 사라지지 않습니다.
- successor를 OS 공통으로 두면 live macOS Preview 이전에 macOS 기본 init이 바뀔 수 있습니다. 이는 S1의 admission 순서(l.66)와 충돌할 위험이 있습니다.
- Windows 빌드가 entry-1 workspace를 만났을 때의 동작(status/doctor 허용 여부, mutation 거절)도 정의돼 있지 않습니다.

**최소 정정**: S2에 다음 세 조항을 추가합니다.
1. entry-1 writer가 successor workspace를 변경 없이 거절함을 정적 대조와 qualification으로 확인합니다. 확인하지 못하면 잔여 위험을 명시하고 Owner가 수락하는 대상으로 둡니다.
2. live macOS Preview 이전에는 macOS의 기본 window와 init/update 동작을 바꾸지 않습니다.
3. Windows 빌드는 predecessor window를 만나면 진단 외 mutation을 거절하고 상태를 보존합니다.

### R1-D01-F3 · P1 · "기존 blocking 의미 보존"과 취소 의미의 충돌

**위치**: S4 l.96, l.98, l.100, Open Points l.168

**근거 문안**
- "기존 blocking 의미를 보존… 기본 timeout 또는 자동 takeover를 추가하지 않는다"(l.96)
- "interrupt… 미검증"(l.98)
- 취소 방식은 구현 계획에서 정한다고 합니다(l.100).

**결과**
- ctypes로 `LockFileEx`를 즉시 실패 flag 없이 호출하면 커널 대기 중에는 메인 스레드가 Ctrl+C로 깨어나지 않을 가능성이 높습니다 [일반 지식].
- POSIX의 blocking 잠금이 사용자 interrupt로 취소 가능하다면 [추론: 기존 구현의 취소 의미는 소스 필요], Windows 구현은 "blocking"을 보존하면서도 취소 의미를 잃게 됩니다.
- 그러면 사용자는 프로세스 종료 외에 빠져나갈 길이 없습니다.

**최소 정정**: 계약 문안에 다음을 넣습니다.
- 대기는 무기한이다.
- 사용자 interrupt 시 잠금을 획득하지 않고 mutation 없이 non-pass로 종료한다.

메커니즘은 계획에 맡깁니다. 후보는 두 가지입니다.
- 즉시 실패 호출(관측된 flags=3 경로) + 짧은 대기의 polling 루프. timeout 없이 호출자 관점의 blocking을 유지합니다.
- overlapped 호출 + 취소.

### R1-D01-F4 · P2 · "실패 phase 보존"과 진단 전용 권고의 긴장, post-publication flush 실패 후 복구 미정

**위치**: S5 l.106, l.112, Open Points l.168

**근거 문안**
- "실제 관측 prefix와 실패 phase를 보존하고 기존 exact recovery 규칙으로 판정"(l.106)
- 동시에 "진단으로만 노출하는 최소안을 우선 권고"(l.112)

**결과**
- 진단 전용이면 프로세스가 끝난 뒤 실패 phase가 기록으로 남지 않습니다.
- 디스크상 prefix만으로는 "발행했으나 flush 실패"와 "발행·flush 완료"를 구별할 수 없습니다. 이후 exact repair나 retry가 무엇을 근거로 판정할지 정의돼 있지 않습니다.
- Windows에서 read-only handle로 fsync하면 실패할 가능성이 큽니다(l.110의 error 5 관측과 같은 성격) [일반 지식]. l.106, l.168의 read-only fsync 경로는 방치하면 정상 경로에서 non-pass를 낼 수 있습니다.

**최소 정정**
- "보존"을 두 가지로 정의합니다. 디스크 상태를 되돌리지 않는 것, 그리고 실패 명령 출력에 phase와 오류를 보고하는 것입니다.
- 복구 규칙을 추가합니다. exact recovery·retry의 재검증 단계에서 bytes·identity가 일치하면 write-capable handle로 **재flush**하고, 성공해야 pass로 판정합니다. 이렇게 하면 receipt schema를 바꾸지 않고도 durability 요청을 회복할 수 있습니다.
- 이 규칙은 immutable member 재확인의 read-only fsync를 대체하는 설계와 합쳐 기술합니다.

### R1-D01-F5 · P2 · 명시적 Python 진입의 전제가 서술되지 않음

**위치**: S7 l.128–134, Options l.53

**근거 문안**
- `.cmd`에 대해서는 "자기 교체 문제를 추가로 해결"하라고 요구합니다(l.53, l.134).
- explicit Python 진입의 자기 교체·sys.path·shell 차이에 대한 전제는 없습니다.

**결과**: 다음 위험이 문서에 드러나지 않습니다 [일반 지식].
- `-I`는 스크립트 디렉터리를 `sys.path`에 넣지 않습니다. launcher가 형제 module을 import하는 구조라면 경로를 스스로 구성해야 합니다 [추론: 기존 POSIX 진입이 이미 `-I`를 쓰는지는 소스 필요].
- CPython은 메인 스크립트를 파싱하는 동안 delete share 없이 파일을 엽니다. 그 짧은 구간에 self-update replace가 sharing 오류를 낼 수 있습니다.
- Windows PowerShell 5.1과 PowerShell 7.3 이상은 native 인자 전달 규칙이 다릅니다. 빈 문자열과 내부 큰따옴표에서 특히 차이가 납니다.
- `py` launcher는 exact build 선택을 보장하지 않습니다.

**최소 정정**: S7에 다음을 명시합니다.
- 절대 경로 interpreter를 진입 형식으로 둡니다.
- launcher가 지원 버전을 스스로 확인합니다.
- `-I` 하의 import 경로 책임을 명시합니다.
- 실행 중 self-update 조건을 qualification 대상으로 둡니다.
- PowerShell 기준선 선택을 Owner 결정 항목으로 올립니다.

### R1-D01-F6 · P2 · reparse 검사의 ancestor 경계가 정의되지 않음

**위치**: S3 l.84, l.90, S5 l.104

**근거 문안**: "검사 대상 경로의 ancestor와 leaf"(l.84). 어느 ancestor까지인지는 정하지 않았습니다.

**결과**
- 드라이브 루트부터 전체 체인을 거절하면, 알려진 폴더 리디렉션(OneDrive 등 cloud reparse tag)이나 mount point 아래의 사용자 배치가 기본 거절됩니다 [일반 지식].
- workspace root 아래만 검사하면 root 상위의 alias가 identity 검사를 우회할 수 있습니다.
- S5의 write-capable directory handle 열기와 S3 검사 순서 사이의 상호작용도 정해져 있지 않습니다.

**최소 정정**: Owner 정책으로 경계를 정합니다(권고는 §3 S3). 거절되는 대표 배치를 unsupported로 문서화합니다.

### R1-D01-F7 · P2 · non-Git·untracked mode의 fail-closed가 사실상 범위 축소

**위치**: S6 l.120, l.124, S2 l.74

**근거 문안**
- S2 범위에 "current-format intent/Work/worker integrity"가 포함돼 있습니다(l.74).
- S6은 "표현을 확정하지 못한 경로는 affected writer를 거절"한다고 합니다.
- 동시에 "몰래 범위를 축소하지 않는다"고도 합니다(l.124).

**결과**: S6-A/B가 결정되지 않은 채 구현하면, 새 파일이나 non-Git Work의 쓰기가 런타임에서 일괄 거절됩니다. 이는 문서가 금지한 묵시적 축소와 같은 효과를 냅니다.

**최소 정정**: 두 안 중 하나를 Owner가 **명시적으로** 선택하게 합니다. 권고는 §3 S6을 보십시오.
- (a) 문서화된 기본 논리 mode 규칙
- (b) 최초 범위에서 non-Git 제외를 명문화

### R1-D01-F8 · P2 · exact retry의 호출 형태와 token 의미가 미정

**위치**: S8 l.140, l.144

**근거 문안**: "caller가 원 요청·token·candidate를 다시 지정"(l.140), "기존 token 의미"(l.144)

**결과**
- token이 단회 소비형이라면 "같은 token으로 retry"는 기존 의미와 충돌합니다 [추론: token 수명·소비 규칙은 소스 필요].
- 새 retry 명령이나 flag가 생기면 CLI와 문서 표면이 확장됩니다.

**최소 정정**
- exact retry를 "기존 명령(apply 또는 exact repair)을 같은 입력으로 다시 호출하는 것"으로 정의합니다. 새 표면은 만들지 않습니다.
- token 재사용 가능 여부는 기존 token 규칙을 그대로 따릅니다. 소비된 token은 새 preview를 요구합니다.

---

## 3. S1–S8 최종 권고

| S | 최종 권고 | 근거 | 지금 필요한 Owner 결정 | 구현 계획에 남길 세부 |
| --- | --- | --- | --- | --- |
| **S1** | B 유지. 지원 표시는 세 층으로 나눕니다: 정책 대상(ARM64/x64), 실측 tuple, 미관측. help/capabilities/docs가 같은 어휘를 씁니다(S1-B). 준비 단계와 정식 admission을 분리하는 named amendment를 수락합니다(S1-A). 대표 UTM ARM64에서 full suite를 수행합니다. x64는 정책 대상으로 두되, **"x64 실측" 표기 전에 ABI 민감 표면(ctypes Win32 signature·pointer width, 잠금, replace, handle 상속, process 진입)만 focused 검사**합니다. full suite는 요구하지 않습니다. 물리 PC는 gate가 아닙니다. | 문서 자체가 typed Win32 signature와 pointer width를 x64에서 별도 검증해야 한다고 적고 있습니다(l.100). 이것이 B가 요구하는 "구체 mechanism"이므로 focused 검사를 요구할 근거가 됩니다. full suite가 필요할 실패 mechanism은 없습니다(l.68). flush는 power-loss 보장을 부인하므로(l.104) 가상 디스크와 물리 디스크의 차이가 gate 근거가 되지 않습니다. | S1-A 문안 수락 의사. 열 가지 criteria 각각의 유지·수정 매핑 승인(문서 정정 후). x64가 미관측인 상태로 public claim을 허용할지 여부(권고: "정책 대상·미관측"으로만 허용). | tuple ledger 형식, runner identity, discovery/executed ID 고정, budget(l.184) |
| **S2** | 최초 Windows 범위는 fresh + same-window lifecycle로 한정합니다. entry-1→successor 이주는 **모든 OS에서** 별도 DR로 미룹니다. live macOS Preview 전에는 macOS 기본 window를 바꾸지 않습니다. successor는 Windows fresh init만 씁니다. entry-1 writer의 successor 거절을 필수 조건으로 둡니다. 조건부 판단: Windows 코드가 기존 member 안에 들어가고 persist 의미·membership이 변하지 않음을 소스로 입증하면 entry-1 유지를 재검토합니다. 그렇지 않으면 successor로 갑니다. | 11-module exact 검사(l.78)가 사실이라면 새 Win32 module은 membership 변경을 뜻하고, 따라서 successor가 필요할 가능성이 높습니다 [추론: 소스 필요]. 이주를 제외해도 교차 OS 노출은 남습니다(F2). | (a) 최초 범위 = fresh/same-window. (b) 이주는 별도 DR. (c) Preview 전 macOS 불변. (d) predecessor workspace를 만났을 때의 거절 정책. | exact window 이름, ordered membership, reader/writer 집합, schema, pair 검증 |
| **S3** | 기존 trusted-local 경계를 유지합니다. reparse 검사 경계는 **workspace root와 그 아래 전부, 그리고 root 확정 시점의 전체 절대 경로 체인**입니다. 체인의 reparse는 기본 거절합니다. cloud/리디렉션 폴더는 unsupported로 문서화합니다. 판별 불가는 거절합니다. handle identity(volume + file ID)와 경로를 대조하고 쓰기 직전에 재검증합니다. data-access pinning은 미채택하며 race 비보장을 명시합니다(l.86). | 관측상 junction은 `is_symlink=False`로 보였습니다(l.88). 경로 문자열만으로는 alias를 해결할 수 없습니다. 완전한 race 방어는 기존 위협 모델 밖이며, 이를 요구하면 범위가 묵시적으로 확장됩니다. | 경계 정책(권고안 수락 여부). race 비보장 재확인. | identity 필드와 API, final-path 비교, 8.3 short name·대소문자·normalization 처리 순서, S5 directory handle과의 순서 |
| **S4** | 안정 anchor, `FILE_SHARE_DELETE` 제외, 비상속 handle을 채택합니다. **무기한 대기 + 사용자 interrupt 시 미획득·무변경 non-pass**를 계약 의미로 둡니다. timeout과 takeover는 없습니다. 같은 thread 재진입은 즉시 거절합니다. read-only 경로에서는 lock 파일을 만들지 않습니다. | 관측: delete share를 허용하면 lock이 이중화됐습니다(l.98). 취소 의미는 메커니즘 선택(blocking 호출 vs polling)에 따라 달라지는 의미 사항입니다(F3). | 취소 의미 수락. 기존 POSIX 취소 의미와 같은지 소스로 확인을 지시(필요 시 문안 조정). | polling vs overlapped+cancel, poll 간격, range 0/1의 빈 anchor(EOF 너머) 동작, 재진입 registry, 종료 시 handle 정리 |
| **S5** | Windows의 필수 sync phase 집합은 **기존 POSIX 필수 phase와 1:1로 대응**시킵니다. 새로 추가하지도 삭제하지도 않습니다. 파일 내용은 발행 전에 flush하고, namespace를 바꾼 뒤에는 parent directory를 flush합니다. 모두 write-capable handle을 씁니다. read-only fsync는 write-capable 재열기 flush로 대체합니다. 실패나 unavailable은 non-pass입니다. 발행 후 flush 실패는 되돌리지 않고, exact recovery·retry의 재검증 단계에서 재flush해 판정합니다(F4). 결과는 진단 전용이며 receipt schema는 바꾸지 않습니다. | 1:1 대응은 새 durability 정책을 발명하지 않으면서 macOS D3 의무를 보존합니다(l.112). 재flush 규칙은 진단 전용 기록과 복구 판정을 schema 변경 없이 양립시킵니다. | 1:1 대응 원칙. 진단 전용 선택. post-publication flush 실패의 처분(되돌리지 않음 + 재검증 시 재flush). | API 선택(FlushFileBuffers, write-through rename 여부), share flag, read-only attribute 파일 처리, 진단 어휘 exact 이름 |
| **S6** | ACL·ownership 불변, 완성 판정은 bytes·identity·prefix로 합니다(l.118). Git tracked 파일은 index/tree를 기준으로 합니다. untracked·non-Git은 다음 순서로 정합니다. (1) retained manifest에 기록된 mode를 보존합니다. (2) 새 파일은 **문서화된 기본 논리 mode `100644`를 provenance와 함께 preview/진단에 표시**합니다. (3) 실행 의도는 명시 입력으로만 받습니다. stat bit는 절대 쓰지 않습니다. 조건부 판단: provenance 기록이 기존 manifest 의미 안에서 가능하면 window는 유지되고, 불가능하면 S2 schema 결정으로 넘깁니다. | "조용히 확정" 금지(l.120)는 공개되고 문서화된 규칙까지 금지하지 않습니다. fail-closed 일괄 거절은 묵시적 범위 축소가 됩니다(F7). | 문서화된 기본 규칙(권고)과 non-Git 최초 범위 제외 중 하나를 명시적으로 선택. 실행 의도 입력 허용 여부. | 상태 predicate 표(S6-C), 필드 표현, index–Work 일관성 검사 순서 |
| **S7** | PowerShell에서 **절대 경로 interpreter + `-I -B`**를 최초 진입으로 둡니다. explicit Python을 native-launcher criterion의 허용 구현으로 해석하는 문안을 수락합니다. `.cmd`는 최초 범위에서 제외합니다. launcher는 버전을 자체 확인합니다. 조건부 판단: 기존 문서가 빈 문자열이나 내부 큰따옴표를 포함한 argv를 허용한다면 PowerShell 7.3 이상(Standard 전달)을 기준선으로 하거나 해당 입력 경로를 별도로 문서화해야 합니다. 그런 입력이 없다면 in-box 5.1을 기준선으로 할 수 있습니다. | 관측 근거는 Python→Python 10-인자 왕복뿐입니다(l.132). 입력 축소 금지(l.130)를 지키려면 shell 차이를 의미 수준에서 다뤄야 합니다(F5). | criterion 해석 수락. PowerShell 기준선(위 조건에 따라). | 정확한 실행 예, `-I` 하 import 경로, 실행 중 self-update 시점, qualification 입력 집합 |
| **S8** | 자동 retry는 0회입니다. delete-then-copy는 금지합니다. exact retry는 **기존 명령을 같은 입력으로 다시 호출하는 것**이며 새 표면은 만들지 않습니다. token은 기존 수명 규칙을 따릅니다. 계약에는 실패 범주(pre-publication / post-publication·pre-flush / post-flush / unknown)를 고정하고, API별 매핑은 계획에서 정합니다. 읽기 실패는 unknown으로 처리하고 부재로 간주하지 않습니다. | 관측: reader가 열려 있는 동안 replace가 실패했고 close 후 성공했습니다(l.142). 일시적 sharing 실패의 빈도는 아직 근거가 없으므로, bounded retry는 qualification에서 빈도 증거가 나온 뒤 별도 개정으로 다룹니다. | retry 0과 "새 retry 표면 없음" 확인. | native error 매핑, 범주별 판정 표, 진단 출력 |

---

## 4. 구분 목록

### 4.1 문서만 고칠 사항 (실험·구현 불필요)

1. **F1**: "계약 고정 / 계획 고정" 2열 표를 추가합니다.
2. **F2–F4, F7, F8**: 의미 문안 보강.
   - S2의 old-writer·predecessor 조항
   - S4의 취소 의미
   - S5의 "보존" 정의와 재flush 규칙
   - S6의 선택지 명시
   - S8의 retry 정의
3. **l.161 정정**: "모든 S 선택은 미결"을 다음처럼 고칩니다. "S1의 B 방향은 지시됨(l.21, l.47, l.163). S1-A/B 문안과 S2–S8은 미결."
4. **l.66, l.152**: 열 가지 Windows criteria 각각을 유지·수정·S7 해석 대상으로 나눈 매핑 표를 추가합니다. 현재 문안은 네 가지만 열거합니다.
5. **l.90**: "B-1 probe"는 문서 안에 정의가 없습니다. 정의하거나 출처를 인용합니다.
6. **l.78, l.110, l.122**: source 사실 진술(11-module 검사, flush helper 결과 미저장, `_stable_file` 동작)에 "baseline `a93f71c` 기준 Driver 정적 확인"을 명시합니다. 저는 이 진술들을 검증하지 못했습니다.
7. **l.31**: "이 bytes 자체의 Claude 리뷰는 아직 없다"는 이 리뷰 이후 갱신이 필요합니다. 다음 revision에서 R1-D01과 처분을 인용합니다.
8. **S7 l.53**: `.cmd`에만 붙어 있는 자기 교체 문제를 explicit Python 경로에도 대칭으로 서술합니다.

### 4.2 Owner 결정 (§3 "지금 필요한" 열 요약)

1. S1-A amendment 수락 의사, criteria 매핑, x64 미관측 표기 정책
2. S2 범위 4항: fresh/same-window, 전 OS 이주 별도 DR, Preview 전 macOS 불변, predecessor 거절
3. S3 ancestor 경계 정책
4. S4 취소 의미
5. S5 1:1 phase 대응, 진단 전용, post-publication flush 실패 처분
6. S6 기본 규칙과 non-Git 제외 중 택일
7. S7 criterion 해석과 PowerShell 기준선
8. S8 retry 0과 새 표면 없음

이 결정들은 의미 정책입니다. 구현 승인은 아니며 별도로 남습니다(l.178).

### 4.3 선택적 추가 관측 (해당 설계를 택할 때만)

- **S7 `.cmd` 채택 시**: 정상 quoting harness와 self-update·delete 시점 비교(l.134). 채택하지 않으면 불필요합니다.
- **S3 data-access pinning 채택 시**: 권한·share 조합별 좁은 probe(l.90).
- **S8 대체 rename API 채택 시**: 해당 API의 sharing 동작(l.168).
- **S4 blocking 호출 + 취소 방식 채택 시**: Ctrl+C 동작을 확인하는 좁은 관측. polling 방식을 택하면 이미 관측된 flags=3 경로를 재사용하므로 계약 전 관측은 불필요합니다.
- **S2 entry-1 유지 검토 시**: 새 member가 없고 양방향 의미가 보존된다는 정적 입증(l.80). 실험이 아니라 source 대조입니다.

위 항목 중 어느 것도 B의 full matrix나 물리 PC gate를 요구하지 않습니다.

### 4.4 향후 구현·qualification 테스트 (승인된 범위 안에서)

- **잠금**: 무기한 대기, interrupt 시 미획득·무변경, 빈 anchor, 재진입 거절, child의 handle 비상속, 종료 후 정리
- **sync**: 필수 phase별 성공·실패 주입, 발행 후 flush 실패 → 재검증 재flush, read-only fsync 대체 경로
- **경로**: junction, mount point, cloud tag 거절, 판별 불가 거절, identity 불일치 시 mutation 거절
- **mode**: index 기준 판정, manifest 보존, 새 파일 기본값과 provenance 표시, 실행 의도 입력
- **진입**: 선택한 PowerShell에서 공백·한국어·quote·빈 문자열·metacharacter·stdin·exit code 검증, 실행 중 launcher 교체
- **retry**: reader가 연 상태에서의 replace 실패 → 범주 판정 → 동일 입력 재호출, token 규칙 확인
- **lifecycle**: fresh / same-window init·update·rollback·repair·detach의 중단·복구 prefix
- **교차 window**: entry-1 writer의 successor 거절, Windows 빌드의 predecessor 거절
- **매트릭스**: 대표 UTM ARM64 normal + parent-optimized full suite, x64 ABI 표면 focused 검사, macOS regression/reuse 판단(l.184)

---

## 5. 잔여 위험과 한계

**잔여 위험**
- 계약이 power-loss persistence를 보장하지 않습니다(l.104). 같은 계정의 비협조적 race도 막지 않습니다(l.86). 이 두 가지는 의도된 비보장입니다. public 문서와 지원 표시가 이를 정확히 반영하지 않으면 사용자가 보장 범위를 과대평가할 수 있습니다.
- x64를 정책 대상으로 두되 미관측인 채 admission하는 경우, ABI 결함이 사용자에게 먼저 발견될 수 있습니다. 따라서 S1의 focused 검사를 "x64 실측" 표기의 선행 조건으로 두기를 권고합니다.
- auto retry 0은 백신·인덱서 같은 일시적 sharing 간섭으로 non-pass가 잦아질 위험이 있습니다. qualification에서 빈도를 기록해 개정 근거로 삼으십시오.
- successor window를 수락한 뒤 durable record로 사용하면 되돌리기 비용이 큽니다(l.188). F2의 교차 OS 조항은 그 전에 고정해야 합니다.

**정적 단일 문서 리뷰의 한계**
- 이 리뷰는 패킷에 포함된 Draft 텍스트의 내부 일관성만 분석했습니다.
- 링크된 DR-0002/0003/0004, Workspace·Structure 문서, CHORE 관측 기록, R1-P01 원응답, 소스 코드, 원시 실험 출력은 읽지 않았고 읽을 수 없었습니다.
- probe 관측(l.68, 88, 98, 110, 122, 132, 142)과 source 사실 진술은 보고된 주장으로만 다뤘습니다. 독립적으로 검증하지 않았습니다.
- [일반 지식]으로 표시한 Windows/CPython 동작은 이 baseline이나 tuple에서 확인한 것이 아닙니다. F3·F5·F6의 결론은 해당 확인 결과에 따라 조정될 수 있습니다.
- 도구 실행, 해시 재계산, 링크 확인, 테스트는 수행하지 않았습니다.
````

### R1-D01 Record Verification And Retention

GFM 렌더링·code 밖 literal 강조 기호·local path/heading links 22개·작성 whitespace·disclosure 검사를 통과했다. 변경 기록을 포함한 문서 3개를 검사했다. DR-0007 v0.1, R1-D01 request/packet/final의 digest와 source 내 verbatim 일치, 기존 R0/R1-P01 원문·frozen 자료 보존, 제품 tracked diff 없음도 확인했다. 이는 문서 검사이며 제품 또는 새로운 정책의 실행 검증이 아니다.

필수 request/packet/inputs/final/최소 metadata와 호출 script는 Owner 선택 및 reviewed Draft와 Driver 권고의 다음 exact 비교를 위해 보존한다. Reviewer 종료, final byte 일치, lsof 사용 없음 확인 뒤 중복 partial 응답·0-byte stderr·빈 tool-temp만 삭제했다. active 경로는 바뀌지 않았다. source worktree·기존 실측 증거·VM과 마지막 복구 사본은 기존 결과/복구 처분과 구체 후속 비교를 위해 유지하며, 이번 단계에서 새 사본·VM 변경·branch 삭제는 없었다.


## Contract Draft Revision 0.2 — 2026-10-18

Owner는 리뷰 결과와 Driver 최종 권고를 DR-0007 v0.2에 반영하고 S6의 논리 mode 기본값·최초 지원 제한을 명확히 쓰도록 요청했다. B 유지와 추가 실험·제품 구현 금지를 지켰다. 기존 R1-D01 시점의 “v0.1 미변경/초안 개정 미승인”은 당시 기록이며, 이번 문서 개정 승인과 결과는 이 dated entry가 설명한다. 문서 보완 승인은 계약 수락이 아니다.

[DR-0007 Draft 0.2](../decisions/DR-0007-windows-native-runtime-contract.md)는 F1–F8의 Driver 처분을 반영했다. 계약 의미와 계획 방법, old-writer·macOS 경계, ancestor chain, 취소·scratch, sync 의무·재flush, native 진입 대상, 기존 retry/token 의미를 보완했다. 열 가지 admission 기준의 대응표를 추가했다. S6은 일반 Windows untracked/non-Git의 공개 논리 기본값 100644, preview/진단의 출처 표시, non-Git 100755 의도 생성·변경/그 의미가 필요한 복구의 최초 미지원, 원본·과거 기록과 exact 원참조 보존을 명시한다. 별도 mode registry나 임의 과거 manifest fallback은 권고하지 않는다.

S6 제한을 포함한 v0.2는 아직 Claude 재리뷰·Owner 계약 선택/수락을 받지 않았다. 현재 normative 문서·Decision Catalog·STATUS·제품 source·VM·실험과 Git publication은 변경하지 않았다. v0.1 28,302 bytes와 SHA-256 8053b06be2ec8d2c79cf74e20eae9aa56d5e7cb8cac8c7b97d2263e099ec194a는 기존 R1-D01 frozen packet에서 byte-identical 복구가 가능하다. 과거 리뷰 원문과 Driver 판단을 새 권고로 덮어쓰지 않았다.

v0.2 identity: 45,332 bytes; SHA-256 `ebe30bbaeae01c58105a3439506a7ed5c1081a734da434a810cdad2bf4b294db`. 아래 문서 검증 결과는 이 identity를 대상으로 기록한다.

### Revision 0.2 Verification And Retention

문서 3개의 GFM 렌더링과 code 밖 literal 강조 기호, local path/heading links 27개, 작성 whitespace, disclosure를 검사해 통과했다. S1 원문 유지, S1–S8 및 열 가지 admission 기준, Draft 상태와 accepted-only 빈 섹션, v0.1의 줄 번호 제거 후 28,302 bytes 복구, 과거 CHORE 본문과 R0/R1-P01/R1-D01 원문·frozen 자료 보존을 확인했다. 제품 HEAD와 source 입력은 그대로이며 제품 tracked diff는 없다. 이는 문서 검사이며 제품 지원·qualification PASS가 아니다.

개정 입력 identity, v0.1→v0.2 bounded diff, 검증 helper/report는 Owner 비교·다음 exact 리뷰의 consumer를 위해 보존한다. 결과가 source와 diff에 보존됐고 사용 process가 없음을 확인한 뒤 이번 개정의 일회용 적용 helper와 중복 작성 입력만 삭제했다. active 경로 이동은 없다. 기존 source worktree·실측 증거·VM과 마지막 복구 사본은 기존 결과/복구 처분 및 후속 비교 의존성이 남아 유지한다. 제품 변경이 없으므로 현재 adopter update는 필요하지 않으며 실제 설치 상태는 미확인이다.

## R1-D02 Draft 0.2 Re-review And Driver Judgment — 2026-10-18

Owner는 “DR-0007 v0.2를 Claude에게 재리뷰받고, 특히 S6의 기본값·지원 제한·기존 기록 보존이 일관되는지 확인해줘. 네 판단과 계약 수락 전에 남은 사항도 정리해. B안은 유지하고 추가 실험이나 제품 구현은 아직 시작하지 마.”라고 요청했다. 이번 범위는 지정 Draft의 재리뷰와 Driver 판단 기록이다. 아래 처분의 accept/revise는 다음 문안에 대한 Driver 권고이며 계약 채택이나 지금의 Draft 수정이 아니다. v0.2 reviewed bytes는 그대로 보존한다.

### R1-D02 Request, Identity And Limits

| 항목 | 실제 입력·결과 |
| --- | --- |
| 대상 | DR-0007 Draft 0.2 한 문서, 45,332 bytes; SHA-256 `ebe30bbaeae01c58105a3439506a7ed5c1081a734da434a810cdad2bf4b294db` |
| source identity | baseline `a93f71c359c4f0a9d57fcfb50d5999160e870f77`; tracked diff SHA-256 `91f501b2077cfc175ae80edbddd2f56a32b71c2bcb6c6b7c1659d01c3e42a7ef`. 대상 Draft는 untracked이므로 위 별도 bytes/digest와 frozen packet으로 식별 |
| request / packet | request SHA-256 `f4e3e51615c454c6c66ee8be0a021ea3b8b5c1b64ea5382b76b09ed3238dc957`; packet 47,152 bytes, SHA-256 `94324aae47755dc33f96b863c7dc85149b0c4eadaf0301f78c60169f591fde53` |
| 실제 Reviewer | Claude CLI 2.1.302, model `claude-opus-5-5`, fresh session `77db2dea-e391-4739-aedd-b569e344c757`; Driver Codex; Owner 최종 판단 |
| 실행 경계 | 지정 문서만 전달, 도구 0개, source·링크 문서·이전 리뷰·실험 원출력 미전달. 1,200초 상한, 실제 219.059초, exit 0, tool events 0 |
| input drift | 한 입력을 실행 전후 검증, 변화 없음. 이번 단계에서도 Draft 미수정 |
| final identity | 18,597 bytes; SHA-256 `5a96a66aacafd64228c604a64e2a2486da8375fb44b6ed845c3584d7e87e1ef5` |
| 결과의 한계 | 정적 단일 문서 리뷰. Reviewer는 실행·재현·source 검증을 하지 않았다. 아래 Driver의 source 대조와 추가 finding도 새로운 실험 결과가 아님 |

비밀값·계정 주소를 기록하지 않고 subscription 인증 경로 `claude.ai / firstParty / pro` 및 provider override 부재를 확인한 뒤 호출했다. Reviewer는 S6의 여섯 가상 사례를 문안으로 대조했다. 이 사례들은 실행한 테스트가 아니다.

### R1-D02 Verdict And Driver Position

Reviewer 판정은 전체 계약 수락 준비도 request-changes, S6 내부 일관성 conditional, 문서 기반 계획 준비 conditional이다. 필수 보완은 7개(P1 3개, P2 4개), 선택적 보완은 4개다.

Driver도 v0.2를 지금 exact 수락하기는 이르다고 판단한다. 공개 기본값 100644, non-Git 100755 최초 제한, 과거 기록 보존은 함께 유지할 수 있다. 다만 “어떤 관측의 mode인가”, “어떤 operation을 거절하는가”, “원기록과 실제 결과를 어떻게 구별하는가”를 문안으로 고정해야 한다. 여기에 아래 D02-D1의 worker mode 변경 충돌이 추가된다. B 방향을 바꾸거나 새 실험을 해야만 이 의미 선택을 할 수 있는 상황은 아니다.

### R1-D02 Finding Dispositions

| Finding | Driver 처분 | 다음 문안 권고와 근거 |
| --- | --- | --- |
| R2-F1 · P1 · index와 bytes 일관성 | accept | 일반 snapshot에서 index는 tracked membership·mode의 출처이고 bytes는 working-tree 관측값이다. unstaged content 수정은 이 이유만으로 거절하지 않는다. exact retained tree가 입력인 작업만 tree bytes 일치를 요구한다. index 관측의 안정성은 별도 검증한다. |
| R2-F2 · P1 · Windows 범위·macOS | revise | S6 규칙을 승인된 Windows successor의 OS/runtime·window 조합에 한정하고 macOS·기존 window 의미를 바꾸지 않는다. window 이름 하나만으로 OS별 mode 출처가 충분히 증명된다고 단정하지 않는다. 기존 binding/profile에서 구분 가능한지 계획에서 확인하고, 새 persisted 의미가 필요하면 S2와 함께 제시한다. 항목별 새 provenance field는 기본 요구가 아니다. |
| R2-F3 · P1 · unknown fallback | accept | Git 분류 실패, index 읽기·안정성 실패, unmerged/허용 외 mode는 untracked/non-Git 기본값으로 바꾸지 않는다. 실제 원인에 따라 unknown 또는 unsupported로 보존하고 관련 mutation을 거절한다. stage-0 판정 등 세부는 계획에서 정하되 현재의 unmerged·120000·160000 거절을 약화하지 않는다. |
| R2-F4 · P2 · 기존 non-Git 100755 | revise | 기존 기록 읽기·진단과 의미를 대체·발행하는 mutation을 나눈다. 기존 100755를 100644 delta로 조용히 흡수하지 않고, 그 의미를 보존·검증할 수 없는 재개·pending recovery는 stable non-pass로 보존한다. old-window·교차 OS·topology 변경은 정상 fresh 지원 경로로 새로 인정하지 않는다. Windows에서 미지원인 해소 경로를 약속하거나 receipt 삭제·detach·대체 request로 우회하지 않는다. |
| R2-F5 · P2 · replay·recovery·단위 | revise | affected mutation은 해당 mode 의미에 의존하는 기존 operation 전체다. 파일 일부만 적용하거나, 무관한 operation까지 project 전체에서 차단하지 않는다. completed replay는 기존 runtime·graph·ticket 등 검증을 통과하는 읽기 경로를 유지하며 mode만을 이유로 새 mutation 거절을 추가하지 않는다. 무조건 성공을 약속하지 않는다. pending recovery의 unsupported와 기존 stale 조건은 각각 보존한다. |
| R2-F6 · P2 · 발행 predicate | accept | permission bit만 달랐던 prefix는 bytes·membership·binding·receipt 등 독립 durable 근거로 구분하지 못하면 unknown으로 둔다. Windows stat mode를 managed member 무결성의 대용 증거로 삼지 않는다. 새 표식이 필요하면 S2 선택에 포함하고 구체 predicate는 계획에서 작성한다. |
| R2-F7 · P2 · 같은 규칙·역방향 | revise | 같은 규칙은 각 관측에서 같은 분류 함수를 재평가한다는 뜻으로 정한다. tracked 100755→untracked 100644도 출처와 함께 실제 delta로 표시한다. exact 원참조는 기대값의 authority이며 현재 관측을 대신하지 않는다. expected와 actual이 다르면 유리한 쪽을 선택하지 않고 기존 stale/refusal과 명시 unsupported를 적용한다. |

선택적 보완도 다음처럼 구분한다.

| Finding | Driver 처분 | 판단 |
| --- | --- | --- |
| R2-P3-a · Windows stat 확장자 | accept, 근거 한정 | CPython 3.14.7 공식 구현의 Windows 경로에는 exe/bat/cmd/com 확장자에 execute bit를 더하는 처리가 있다. 기존 probe의 0666 관측을 모든 파일명으로 일반화하지 않는다. 이는 source 확인이며 guest 확장자별 재실측이나 old-window 지원 입증이 아니다. 공개 기본값은 그 휴리스틱에 의존하지 않는 새 Windows 정책이다. |
| R2-P3-b · 명시 mode 입력 | accept | 최초 미제공은 제품의 untracked/non-Git mode 의도 입력이다. 사용자의 표준 Git staging/mode 표현 자체를 금지하거나 제품에 index 변경 권한을 주는 뜻이 아니다. 실제 결과 적용 범위는 D02-D1과 함께 제한한다. |
| R2-P3-c · 알림 표면 | accept | preview뿐 아니라 status·worker 결과·capabilities의 관련 표시도 같은 정책·출처를 설명해야 한다. 항목별 새 필드나 모든 명령의 장문 알림을 의무화하지 않고, 필요한 표면과 형식은 계획에서 정한다. |
| R2-P3-d · 재리뷰 상태 문구 | accept, 다음 개정 대상 | v0.2의 “아직 재리뷰하지 않았다”는 작성 시점 기록으로 둔다. 이번 dated entry가 현재 재리뷰 상태를 설명하며, 다음 Draft에서 해당 pointer를 갱신한다. 이번에 reviewed bytes를 바꾸지 않는다. |

### R1-D02 S6 Case Assessment

| 사례 | Driver 최종 판단 |
| --- | --- |
| 새 untracked/non-Git | 공개 100644 기본값은 일관된다. 먼저 분류가 확정돼야 하며 unknown을 이 행으로 흡수하지 않는다. |
| untracked ↔ tracked 100755 | 매번 같은 정책을 재평가하고 양방향 delta와 출처를 알린다. 이 관측 규칙만으로 worker가 그 delta를 적용할 수 있다는 뜻은 아니다. |
| 기존 non-Git 100755 기록 | 원문·mode·참조를 보존한다. 읽기와 의미를 바꾸는 재개를 나누며, 지원하지 않는 의미를 100644 결과로 재발행하지 않는다. |
| completed replay / pending recovery | 기존 완료 replay의 읽기 조건을 유지한다. mode의 적용·재검증이 필요한 pending recovery는 미지원 상태를 보존할 수 있다. |
| affected mutation 범위 | 기존 operation 전체를 단위로 하며 부분 파일 성공을 신설하지 않는다. 해당 의미와 무관한 operation은 이 사유만으로 막지 않는다. |
| 원참조·현재 index·기본값 | 원참조는 exact 기대값, 현재 index·filesystem은 독립 관측이다. 어느 한쪽으로 다른 쪽을 덮어쓰거나 임의 과거 manifest를 고르지 않는다. |

### D02-D1 Driver Finding — Worker Mode Change Under An Unchanged Index

D02-D1 · P1 · needs-user. 이 finding은 Claude의 문서 리뷰 이후 Driver가 현행 source와 기존 계약을 대조해 발견했다. 아직 실행하거나 Reviewer에게 재검증받은 결과가 아니다. 현행 POSIX 구현의 재현된 버그로 표시하지 않는다.

기존 worker apply는 파일을 적용해도 control의 Git index를 바꾸지 않으며, 완료 전에 전체 관측 결과가 manifest result와 같아야 한다. Windows의 새 snapshot이 index만으로 mode를 읽으면 다음 경우가 충돌한다.

```text
control index: 100644
retained worker result: 같은 bytes, 100755
apply: 파일 교체/chmod, control index는 100644 유지
다음 Windows snapshot: index에서 100644 관측
결과: 기대한 100755와 일치하지 않음
```

반대 방향 100755→100644와 새 untracked 100755 결과도 같은 종류의 문제를 가진다. 현재 apply 흐름은 durable decision을 먼저 쓴 뒤 파일을 적용하므로, 이 경계를 사전에 정하지 않으면 의미상 완료 불가능한 pending을 만들 수 있다. 단순히 result manifest의 mode를 현재 관측으로 채택하면 기대값으로 성공을 입증하는 순환이 생긴다.

| 정적 근거 | 확인한 사실 |
| --- | --- |
| [현행 snapshot·mode](../../src/hv2ref/work.py), `_snapshot_once`, lines 213–263 | 현재는 stage/mode를 검사하고 실제 bytes·mode는 filesystem에서 얻는다. ordinary snapshot은 index blob bytes와 동일할 필요가 없다. 새 index-only 정책은 아직 구현되지 않았다. |
| 같은 파일, `observe_recovery` lines 358–375; `_worker_content_state` lines 1068–1081 | entry 전체(mode 포함)를 비교하며 final은 전체 result 일치를 요구한다. |
| 같은 파일, `_apply_worker_path` lines 1084–1115; `apply` lines 1411–1426 | worker 적용은 Git index를 갱신하지 않고 파일 bytes/chmod를 처리한다. durable decision 이후 apply loop, 그 뒤 final 확인 순서다. |
| [General Work의 Worker Publication Development Checkpoint](../GENERAL-WORK.md#worker-publication-development-checkpoint) | add/delete/executable-mode 적용 시 HEAD·index·refs 불변과 whole-result 완료 조건을 명시한다. |

최초 범위 권고는 index 불변·독립 재관측을 유지하고, 그 정책으로 post-mode를 관측할 수 없는 새 operation은 durable decision 또는 content 발행 전에 전체 거절하는 것이다. 대표 제한은 mode 변경 결과와 새 untracked 100755 결과다. stable tracked 100755의 content-only 변경이나 새 100644 파일까지 모두 제외하는 권고는 아니다. 실제 preflight 거절 위치·정확한 대상 판정·physical 관측 정합성은 승인 후 계획과 qualification에서 입증해야 한다.

대안은 적용된 논리 mode를 독립적으로 입증하는 명시적 authority·durable identity·reader/recovery 의미를 설계하는 것이다. 이는 schema/window 영향과 구현 범위를 키운다. 새 registry·sidecar, 원참조를 실제 관측으로 쓰는 규칙, control index 자동 변경을 여기서 채택하지 않는다. 위 제한도 아직 Owner가 수락하지 않은 추가 제안이므로 admission criterion을 조용히 축소하거나 기존 worker 계약을 이미 바꾼 것으로 기록하지 않는다.

### R1-D02 Source Checks And Evidence Boundaries

Driver는 baseline의 다음 사실만 추가로 정적 확인했다. 이 source는 이번 Claude packet에 포함하지 않았다.

- R2-F1/F3: `work.py`의 snapshot은 실제 파일 bytes를 기록하고, unmerged 또는 100644/100755 외 tracked entry를 거절한다. 이를 Windows fallback으로 약화할 이유가 없다.
- R2-F4/F5: 기존 graph는 manifest를 검증하며 완료 selection의 replay는 이미 존재하는 runtime/graph/decision/ticket 검증 뒤 읽기로 돌아간다(`apply`, lines 1368–1388). 이 동작은 임의 외부 기록의 import나 old-window admission을 허용하지 않는다.
- R2-F7/D02-D1: 원참조의 기대값 보존과 실제 snapshot 비교는 분리해야 한다. 기존 실패·stale·outside drift 조건을 지워서 mode 지원을 만드는 것은 범위 밖이다.
- P3-a의 CPython source 확인은 runtime 구현 근거다. 기존 guest probe tuple의 추가 관측으로 세지 않으며 “모든 파일에서 stat 0666”이라는 일반화만 피한다.

### R1-D02 Remaining Decisions Before Contract Acceptance

권고하는 다음 산출물은 실험 결과가 아니라 아래 의미를 반영한 exact 계약 문안이다. 관련 계획 방법은 문서로 병행 정리할 수 있으며, 모든 세부 구현 설계를 끝내야만 의미 선택을 할 수 있는 순환 gate를 만들지 않는다.

| 수락 전에 정할 의미 | Driver 권고 | 뒤의 계획·qualification으로 넘길 방법 |
| --- | --- | --- |
| 적용 범위·기본값 | Windows successor의 명시 OS/runtime·window 범위; 100644는 기존 TreeEntry 논리값과 같되 Windows 기본값 출처를 표시. ACL·실행 가능성 의미를 추가하지 않음 | binding/profile의 충분성, 관측 안정성, 알림 위치·형식 |
| unknown·과거 기록·replay 경계 | unknown fallback 금지; 과거 100755 의미 보존; 기존 완료 replay 유지; 의미를 재현할 수 없는 mutation/pending recovery는 operation 전체 거절·상태 보존 | stage-0/intent-to-add 등 분류, 기존 stale와 unsupported 진단, 구체 case 검증 |
| worker mode 변경 D02-D1 | 최초에는 index 불변으로 post-mode를 독립 관측할 수 없는 결과의 적용을 사전 거절. 이를 명시 지원 제한으로 함께 수락할지 선택 필요 | 입력/result mode 사전 검사, durable decision 전 거절, 반복·중단·복구·whole-result 검증 |
| permission 기반 발행 구별 | 독립 durable 근거가 없으면 unknown. 새 persisted 의미가 필요하면 S2와 함께 제시 | 실제 상태별 predicate, crash prefix·오류 매핑 |
| 기존 S1–S8와 ten-criteria amendment | B 유지. 선택된 문구를 named amended/replaced clauses와 유지 조항에 연결하고 exact 대상 식별. S1의 admission 시점/표시와 S2–S8의 나머지 선택도 여전히 Owner 미결 | 선택한 launcher·lock·flush·path 검증 세부와 대표 UTM full suite / x64 focused 검사 계획 |

D02-D1 제한을 채택하려면 worker 관련 지원 설명·admission 기준의 영향도 exact 문안에 드러내야 한다. 이 기록은 기존 기준을 면제하지 않는다. 의미 선택을 수락한 뒤에도 제품 실행 승인, integrated qualification, 결과 수락, activation, live macOS Preview 뒤 Windows admission은 구별된다. 이번 요청으로 추가 실험이나 제품 구현을 시작하지 않았다.

### R1-D02 Actual Owner Decision

현재 Owner가 승인한 것은 재리뷰와 Driver 판단 정리이며, B 유지와 추가 실험·제품 구현 금지는 계속 유효하다. S6 추가 의미 선택, D02-D1 최초 제한, exact 계약 수락·activation·제품 실행·Git publication은 미승인이다. DR-0007은 reviewed Draft 0.2로 유지한다. 다음 개정 승인이나 수락을 받은 것으로 기록하지 않는다.

### R1-D02 Reviewer Final — Verbatim

````markdown
# R1-D02 — DR-0007 Draft 0.2 재리뷰 (Reviewer 의견)

검토 대상은 packet에 포함된 DR-0007 Draft 0.2 한 문서입니다(45,332 bytes, SHA-256 `ebe30bba…294db`, baseline `a93f71c3…`). 근거는 이 문서의 내부 정합성, 정적 추론, 일반 지식입니다. source, 링크 문서, 이전 리뷰, 실험 원출력은 읽지 않았습니다. source 사실에 기대는 판단은 **[조건부]**로 표시했습니다. 아래 판정은 Reviewer 의견이며 Owner의 계약 선택이나 수락을 대신하지 않습니다.

## 1. Verdict

| 대상 | 판정 | 요지 |
| --- | --- | --- |
| 전체 계약 수락 준비도 | **request-changes** | 방향(B 유지, fresh successor, 공개 기본값과 최초 제한)은 수락 가능한 형태입니다. 그러나 문서 스스로 exact named clauses가 아직 없다고 밝힙니다(266행). S6에는 의미 수준의 누락이 남아 있어 exact 수락 대상으로는 이릅니다. |
| S6 내부 일관성 | **conditional** | 핵심 구조(공개 `100644` 기본값, non-Git `100755` 최초 미지원, 원기록 보존, 임의 과거 manifest fallback 금지)는 서로 모순되지 않습니다. 다만 unknown 분류, Git tracked의 "일관성" 의미, macOS 적용 범위, 기존 `100755` 기록이 있는 Work 재개, completed replay와 pending recovery 구분이 비어 있습니다. 이 공백은 구현 단계에서 서로 다른 해석을 낳습니다. |
| 문서 기반 계획 준비 | **conditional** | S1–S5와 S7–S8은 문안대로 계획 세부를 병행 작성할 수 있습니다. S6 계획(snapshot/replay 비교, 발행 predicate)은 R2-F1–F3을 먼저 문안으로 고정하거나, Owner 질문으로 명시한 뒤 진행하기를 권합니다. |

## 2. Findings

### Must-fix

**R2-F1 · P1 · Git tracked 행의 "bytes·membership 일관성 재확인"(174행)**
- **문제:** 일반 working-tree snapshot에서 수정됐지만 stage하지 않은 tracked 파일은 원래 index blob과 bytes가 다릅니다. "tree/index와 bytes의 일관성 재확인"을 문자 그대로 읽으면 이런 파일이 모두 불일치로 거절될 수 있습니다. 이는 숨은 지원 축소입니다.
- **반대 오독:** 일관성 검사를 아예 무의미하게 만드는 해석도 가능합니다.
- **최소 수정:** 일반 snapshot과 retained tree 입력 작업을 나눠 적습니다.
  - 일반 snapshot에서 index는 tracked membership과 mode의 출처일 뿐이고, bytes는 working-tree 관측값입니다. 일관성은 경로의 index entry 존재와 관측 중 안정성을 뜻합니다.
  - exact retained tree가 계약상 입력인 작업에서만 bytes와 tree의 일치를 요구합니다.

**R2-F2 · P1 · Git index 규칙의 적용 범위와 macOS 무변경(100행, 174행, 191행)**
- **문제:** 191행은 현재 Git 경로가 index를 검사한 뒤 stat에서 얻은 mode를 쓴다고 보고, "변경·검증이 필요"하다고 적습니다. 이를 공통 module에서 바꾸면 macOS 의미도 바뀝니다.
- **반례 [조건부]:** macOS에서 chmod만 하고 stage하지 않은 파일은 지금 stat delta로 보입니다. index 규칙에서는 stage 전까지 보이지 않거나, 현재처럼 불일치 거절이 사라집니다. 100행의 "macOS 기본 동작을 바꾸지 않는다"와 충돌합니다.
- **최소 수정:** S6 mode 출처 규칙 전체(index mode, `100644` 기본값)를 Windows successor window의 규칙으로 한정합니다. macOS와 기존 window는 현행 stat 규칙을 유지합니다.
- **부수 효과:** 규칙이 window의 속성이 되면 window identity 자체가 provenance 단위가 됩니다. 그러면 항목별로 새 persisted provenance 필드를 둘 필요가 크게 줄어듭니다(R2-F4, §4 참고).

**R2-F3 · P1 · unknown·분류 불가 행이 없음(172–179행)**
- **문제:** 179행은 "source를 알 수 없을 때 숨겨서 쓰는 fallback이 아니다"라고 밝힙니다. 그런데 표에는 tracked/untracked를 판별할 수 없는 경우가 없습니다. 구현자는 판별에 실패하면 "untracked"로 간주하고 `100644`를 부여하게 됩니다. 이는 179행이 금지한 바로 그 fallback입니다.
- **구체 사례:**
  - Git 저장소 여부 또는 index 읽기 실패
  - index가 관측 중에 바뀜(외부 git은 cooperating writer가 아님)
  - merge conflict로 stage 1–3만 있고 stage-0 entry가 없음
  - index mode가 `120000`/`160000`인 경우. 예: `core.symlinks=false`인 Windows에서는 symlink가 일반 파일로 checkout되어 S3 reparse 검사를 통과하므로, stat이나 기본값을 쓰면 symlink가 `100644` 일반 파일로 둔갑합니다.
- **최소 수정:** 표에 한 행을 추가합니다. "Git 분류·index entry·mode를 판별할 수 없거나, 허용된 두 mode가 아니거나, 관측 중 바뀜 → 기본값으로 대체하지 않고 unknown/unsupported로 보존, affected mutation 거절." 이 문안은 S3(117행)과 S5(150행)의 unknown 원칙과도 맞습니다. "tracked"의 정확한 판정(stage-0 entry, intent-to-add 처리 등)은 계획 세부로 둡니다.

**R2-F4 · P2 · 기존 non-Git `100755` 기록이 있는 Work 재개(179행, 185–187행)**
- **문제:** 179행은 "같은 Work는 같은 mode 규칙"을 요구합니다. 그런데 base manifest가 다른 규칙으로 만들어진 경우의 처리가 없습니다.
- **반례:** 기존 non-Git manifest에 `100755`가 있습니다. Windows의 새 snapshot은 `100644`를 산출합니다. 비교 결과 아무도 만들지 않은 `100755→100644` delta가 생깁니다. 이 결과가 apply/publish되면 과거 bytes는 보존되어도 `100755` 의미는 조용히 사라집니다. 즉 bytes 보존만으로는 의미 보존이 성립하지 않습니다.
- **탐지 가능성:** Windows 기본 규칙은 non-Git에서 `100755`를 결코 만들지 않습니다. 따라서 "non-Git 기록에 `100755`가 있음"은 provenance 필드 없이도 "다른 규칙에서 온 기록"으로 판정할 수 있습니다.
- **도달 경로:** fresh successor 안에서는 정상적으로 도달할 수 없습니다. old window, 교차 OS 복사, Git→non-Git topology 변경 같은 범위 밖 경로에서만 생깁니다 [조건부]. 이 점을 적어 두면 지원 경로처럼 읽히지 않습니다.
- **최소 수정:** "non-Git base·참조 manifest에 `100755`가 있는 Work는 읽기·진단만 하고, 그 entry를 `100644`로 대체·발행하게 되는 재개·mutation·recovery는 거절한다."
- **출구 명시:** 이 거절로 pending이 Windows에서 해소되지 않을 수 있습니다. 이때 receipt 삭제, detach, 새 request로 우회하지 않으며(98행, 185행), 해소는 최초 범위 밖이라고 명시합니다. 이렇게 해야 복구 모순(진행 불가인데 우회도 금지)이 의도된 stable non-pass로 읽힙니다.

**R2-F5 · P2 · completed replay, pending recovery, affected mutation 단위(177행, 185행; 211행과 대조)**
- **문제:** S8(211행)은 completed replay와 pending recovery를 구분합니다. 반면 S6의 177행("exact recovery/replay")과 185행("복구")은 둘을 묶어 거절합니다.
- **오해 경로:** 새 쓰기 없이 기존 receipt로 결과만 재확인하는 completed replay가 mode 이유로 거절되면, 사용자는 완료된 작업을 미완료로 오인해 다시 실행할 수 있습니다.
- **"적용 불가"의 기제:** Windows에는 실행 bit가 없으므로 디스크에 `100755`를 적용한다는 것 자체가 없습니다. 실제 문제는 복구 후 검증과 다음 snapshot이 `100755`를 재현하지 못한다는 점입니다. 이 기제를 적어 두면 거절 경계가 명확해집니다.
- **최소 수정:**
  1. affected mutation은 해당 mode 의미를 쓰기·발행하거나, 그 의미에 대해 검증해야 하는 **기존 operation 전체**입니다. 파일 단위 부분 적용은 도입하지 않습니다.
  2. 그 의미에 의존하지 않는 다른 operation은 이 이유만으로 거절하지 않습니다.
  3. 새 쓰기 없는 completed replay는 기존 replay 규칙대로 결과를 보고하고, mode는 unsupported 진단으로만 덧붙입니다 [조건부: 기존 replay 계약].
  4. pending recovery는 stale과 구별되는 unsupported 사유로 거절하고 상태를 보존합니다.
- 계약 수락 전에 이 정도는 정의해야 합니다. 단위가 정의되지 않으면 "100755 entry가 하나라도 있으면 project 전체 차단"과 "해당 파일만 건너뜀" 사이에서 해석이 갈립니다.

**R2-F6 · P2 · launcher·managed member의 mode와 발행 predicate(164–170행, 193행)**
- **문제:** 170행은 launcher 발행 상태와 content mode의 출처를 "구별한다"고만 하고, launcher 쪽 규칙을 주지 않습니다.
- **반례 [조건부]:** 기존 prefix가 bytes가 같은 두 상태(staged와 published)를 권한 bit로만 구별한다고 합시다. Windows stat은 모두 0666을 보이므로 두 상태가 구별되지 않습니다. 이때 "정상 상태"로 분류하면 미완성 상태를 완성으로 판정하게 됩니다.
- **최소 수정:** "권한 bit로만 구별되던 상태는 다른 durable 근거(bytes, membership, binding, receipt)가 없으면 unknown으로 보존한다. 새 표식이 필요하면 S2 window 결정과 함께 다시 제시한다. managed member mode를 Windows stat에서 관측해 무결성 판정에 쓰지 않는다." 정확한 predicate는 계획 세부로 남깁니다.

**R2-F7 · P2 · "같은 mode 규칙"의 의미, 역방향 전환, 복구 시 우선순위(179–181행, 174/177행)**
- **역방향 전환:** 문서는 untracked→tracked `100755`만 다룹니다. 반대 방향인 tracked `100755`→untracked(예: `git rm --cached`)는 Windows 정책 때문에 `100755→100644` delta가 됩니다. macOS stat 규칙이었다면 생기지 않았을 delta입니다. 숨기지 않되, worker가 chmod한 것처럼 보이지 않도록 기본값 출처와 함께 표시해야 합니다.
- **"같은 규칙"의 의미:** 매 snapshot마다 같은 분류 함수를 다시 평가한다는 뜻인지, Work 시작 시점의 경로별 출처를 동결한다는 뜻인지 정해야 합니다. 앞의 해석을 권합니다.
- **복구 시 우선순위:** exact recovery/replay에서는 원참조 manifest가 mode authority입니다. 현재 index나 retained tree는 기존 계약이 요구하는 범위에서 그 manifest와 대조만 합니다. 불일치하면 어느 한쪽을 고르지 않고 기존 stale/refusal을 따른다는 한 문장이 필요합니다.

### 선택적 보완 (P3)

- **R2-P3-a [일반 지식, 조건부]:** CPython의 Windows `os.stat`은 `.exe/.bat/.cmd/.com` 확장자에 실행 bit를 붙이는 것으로 알려져 있습니다.
  - 191행의 "stat execute bit" 근거와 probe의 0666 관측은 그 외 확장자에 국한됐을 수 있습니다.
  - 그렇다면 181행 "확장자에 상관없이 `100644`"는 현재 Windows 동작을 바꾸는 것이며, old window 기록에 `100755`가 존재할 수 있습니다(R2-F4의 도달 경로).
  - 근거 문장을 보완하기를 권합니다.
- **R2-P3-b:** Git 저장소에서는 `git update-index --chmod=+x`처럼 기존 Git 입력으로 `100755`를 표현할 수 있습니다. 175행의 "명시 의도 입력 미제공"이 제품 쪽 입력에 한정된다는 점을 밝히면 지원 범위가 정확해집니다.
- **R2-P3-c:** 출처 알림의 범위를 정합니다. preview가 없는 표면(status, worker 결과, capabilities)도 S1-B와 기준 8에 맞춰 동일하게 표시해야 합니다. 알림 단위는 snapshot 단위 요약으로 충분합니다. 분류 규칙이 결정적이기 때문입니다.
- **R2-P3-d:** 36행과 193행의 "Claude 재리뷰 없음"은 작성 시점의 기록으로 유효합니다. 다음 개정에서 R1-D02 기록을 참조하도록 갱신합니다.

## 3. S6 Case Table

| # | 현재 문안 해석 | 판정 | 필요한 의미 선택·계획 검증 |
| --- | --- | --- | --- |
| 1 | 새 untracked/non-Git 파일은 공개 기본값 `100644`이며 preview/진단에 출처를 알립니다(175–176, 179행). | 기본값 자체는 일관됨. **unknown과의 경계는 누락** | R2-F3의 unknown 행 추가. 알림 단위와 표면은 계획 세부(P3-c). |
| 2 | untracked→tracked `100755`는 실제 delta(181행). 역방향은 언급 없음. | **부분 일관** | R2-F7: 역방향 delta를 출처와 함께 표시. "같은 규칙"은 매 snapshot 재평가. index 안정성은 계획에서 검증. |
| 3 | 원기록 보존과 읽기는 허용(187행). 재개·비교 시 의미 손실은 미규정. | **bytes 보존만으로는 불충분** | R2-F4. 구분: 일반 새 snapshot은 `100644`로 정상 진행. 기존 `100755` Work 재개·mutation은 거절. replay는 R2-F5. recovery는 거절하고 출구를 명시. |
| 4 | 읽기·진단은 허용. "복구"와 "replay"를 묶어 거절(177, 185행). | **S8과 불일치 소지** | R2-F5: completed replay(새 쓰기 없음)와 pending recovery를 분리하고, unsupported 사유를 stale과 구별합니다 [조건부: 기존 replay 계약]. |
| 5 | "affected mutation"의 단위가 미정의. | **수락 전 정의 필요** | R2-F5: 기존 operation 전체를 단위로 하고, 부분 성공은 신설하지 않으며, 관련 없는 operation은 차단하지 않습니다. 새 per-file 기능은 전제하지 않습니다. |
| 6 | 원참조 manifest 우선(177행), 임의 과거 manifest fallback 금지(179, 191행), 의미 변경 시 window 결정(109, 193행). | **대체로 일관.** macOS 범위와 우선순위는 누락 | R2-F2(Windows window로 범위 한정), R2-F7(manifest 우선, 불일치 시 거절). 교차 OS와 old-reader는 S2(100, 106행)의 미지원 표시로 처리됩니다. |

## 4. 계약 수락 전 Owner 선택과 문서 보완

**Owner가 고를 의미**
1. **S6 규칙의 적용 단위(R2-F2):** Windows successor window에 결합할지, OS 단위로 할지. 권고는 window 결합입니다. 그러면 provenance를 window identity로 표현할 수 있고, 항목별 persisted 필드는 원칙적으로 필요 없습니다.
2. **Windows 기본값 `100644`의 의미:** 다른 `100644`와 같은 "비실행 논리 mode"로 볼지, 출처가 다른 별도 의미로 볼지. 권고는 같은 의미 + window 단위 출처입니다. 별도 의미를 택하면 schema와 window를 수락할 때 함께 결정해야 합니다(109, 193행).
3. **범위 밖 기록의 처리(R2-F4):** non-Git `100755` 기록이 있는 Work를 Windows에서 stable non-pass로 두고, Windows 쪽 우회를 제공하지 않는 것. 문안은 이미 이 방향이지만 명시적 선택으로 기록합니다.
4. **completed replay의 처리(R2-F5):** mode 이유로 거절하지 않는다는 원칙.

**문서 보완 (계약 문안)**
- R2-F1, F3, F5, F6, F7의 문장을 추가하거나 고칩니다.

**구현·qualification 단계로 넘길 세부 (수락 전 불필요)**
- tracked 판정 세부(stage-0, intent-to-add, skip-worktree)
- index 관측 전후 비교 방식
- 출처 진단의 형식과 위치
- launcher 발행 predicate의 정확한 상태 표
- `_stable_file`/TreeEntry 수정 지점
- Git tracked `100755` 보존과 unknown 거절, 두 autocrlf 아래 digest 검증(기준 5·9)

## 5. 최소 권고 문안

S6 표에 추가할 행:

> | Git 분류·index entry·mode를 판별할 수 없음, 두 허용 mode가 아님, 관측 중 변경 | 기본값 `100644`로 대체하지 않음 | unknown/unsupported로 보존하고 affected mutation 거절 |

174행 보완:

> 일반 snapshot에서 index는 tracked membership과 mode의 출처이며 bytes는 working tree 관측값이다. bytes와 tree의 일치는 exact retained tree가 계약상 입력인 작업에서만 요구한다.

S6 첫 단락 뒤에 추가:

> 이 mode 출처 규칙은 Windows successor window에만 적용한다. macOS와 기존 window의 현행 규칙은 바꾸지 않는다.

Initial Support Limits에 추가:

> affected mutation은 해당 mode 의미를 쓰기·발행하거나 그 의미에 대해 검증해야 하는 기존 operation 전체를 말하며, 파일 단위 부분 적용을 도입하지 않는다. 새 쓰기가 없는 completed replay는 이 사유만으로 거절하지 않고 unsupported 진단을 덧붙인다. non-Git 기록에 `100755`가 있는 Work의 재개·mutation·pending recovery는 stale과 구별되는 unsupported 사유로 거절하고 상태를 보존한다. 이를 Windows에서 해소하는 경로는 최초 범위 밖이다.

## 6. 해결됐거나 반례를 찾지 못한 항목

- **반례를 찾지 못함:**
  - 임의 과거 manifest fallback 금지(179, 191행)와 원참조 우선(177행)
  - 과거 manifest와 bytes를 `100644`로 재작성하지 않음
  - mode registry/sidecar를 기본으로 두지 않음(189행)
  - non-Git Work 전체를 제외하지 않음(176행)
  - 확장자, association, chmod를 근거로 쓰지 않음(181행)
  - `100644`로 바꾼 대체 request를 exact recovery로 표시하지 않음(185행)
- **S6 대조 범위에서 새 authority나 승인 단계를 찾지 못함:** S2의 fresh old-writer 거절과 macOS 유지, S5의 unknown 유지와 재flush 비권한, S8의 새 명령·단회 token 미가정, 반복 승인을 만들지 않는 원칙(253, 264행)과 충돌하지 않습니다.
- **R1-D01 지적:** v0.2 본문에 적힌 범위에서 F1–F8의 반영 문장이 각 조항에 존재합니다. 실제 해결 여부를 이전 리뷰 원문과 대조하지는 않았습니다.
- **새 실험 불필요:** 위 finding은 모두 문안 수정이나 Owner 선택으로 처리할 수 있으며, 새 probe나 x64 전체 suite를 요구하지 않습니다.

## 7. 검토하지 못한 근거와 잔여 한계

- source를 읽지 않았으므로 다음 사항은 확인하지 못했습니다. 문서의 191행 서술과 R2-F2·F6의 반례는 모두 조건부입니다.
  - `_stable_file`과 Git 경로의 실제 동작
  - 기존 replay/recovery 계약
  - launcher 발행 predicate가 mode에 의존하는지 여부
- CPython Windows stat의 확장자 동작(P3-a)은 일반 지식이며, 이번 probe tuple에서 검증되지 않았습니다.
- 링크된 DR-0002/0003/0004, WORKSPACE-CONTRACT, CHECKOUT-1-STRUCTURE, 이전 리뷰 R1-P01/R1-D01, 실험 원출력은 대조하지 않았습니다.
- 어떤 도구, 실행, 테스트, 파일 수정도 하지 않았습니다. 이 결과는 Driver의 accept/revise/defend/needs-user 처분과 Owner의 결정을 기다리는 Reviewer 의견입니다.
````

### R1-D02 Record Verification And Retention

문서 3개의 GFM 렌더링, code 밖 literal 강조 기호, local path/heading links 29개, 작성 whitespace와 disclosure 검사를 통과했다. DR-0007 v0.2의 reviewed bytes, R1-D02 request/packet/final digest와 source 내 verbatim 일치, packet에서 exact Draft 복구, 기존 CHORE 본문 및 R0/R1-P01/R1-D01 원문·frozen 자료 보존을 확인했다. source HEAD와 기존 tracked diff는 그대로다. 제품 변경·새 실험은 없다. 이는 문서·정적 확인이며 Windows 제품 검증 PASS가 아니다.

Owner 선택과 다음 exact 문안 비교에 필요한 request/packet/inputs/final/최소 metadata/호출 script는 보존한다. Reviewer 종료와 source 내 final 보존, 중복 partial의 byte 일치, stderr·tool-temp의 비어 있음, process 사용 없음을 확인한 뒤 중복 응답·빈 로그·빈 tool-temp를 삭제했다. 일회용 문서 검증 helper/report도 결과를 이 기록에 남기고 최종 검사 후 삭제했다. active 경로는 바뀌지 않았다. 기존 worktree·실측 증거·VM·마지막 복구 사본은 미결 결과/복구 처분과 구체 후속 비교의 의존성이 남아 유지한다. 제품 변경이 없어 현재 adopter update는 필요하지 않으며 실제 설치 상태는 미확인이다.


## Contract Draft Revision 0.3 — 2026-10-18

Owner는 R1-D02와 Driver 권고를 DR-0007 v0.3에 반영하고, worker mode 변경의 최초 지원 제한과 기존 계약·admission 기준 영향을 명확히 쓰도록 요청했다. B 유지와 추가 실험·제품 구현 금지를 지켰다. 문서 보완 승인은 계약 수락이 아니다. 이전 dated entry의 v0.2 유지·다음 개정 미승인은 그 당시 범위이며, 이번 개정 승인과 결과는 이 entry가 설명한다.

[DR-0007 Draft 0.3](../decisions/DR-0007-windows-native-runtime-contract.md)은 R2-F1–F7, P3-a–d와 Driver D02-D1을 반영한다. Windows OS/runtime·window 범위, working-tree bytes와 index mode, unknown 거절, 과거 100755 의미·completed replay·pending recovery를 구분했다. S6에 worker 적용 경계 표를 추가했다. index 불변으로 post-mode를 독립 관측할 수 없는 mode-change와 새 untracked 100755 결과는 최초 적용 미지원으로 제안하며 새 accept prepare/apply에서 decision/content 발행 전에 전체 operation을 거절한다. stable tracked 100755 content-only·삭제와 새 100644는 기존 조건 아래 qualification 대상으로 남긴다.

기존 계약·admission 영향 표는 Windows 지원 집합의 축소 제안과 index 불변·whole-result·정확한 원기록·기존 replay/cancellation 의무를 분리한다. criterion 5의 지원 범위 변경과 criteria 6–9의 거절·전체 회귀·지원 표시·identity 영향을 명시했다. 전체 regression이나 macOS mode 성공 의무를 면제하지 않았다. S1의 B 문안은 byte-identical하게 유지했다.

v0.3과 worker 최초 제한의 exact 문안은 아직 Claude 재리뷰·Owner 계약 수락을 받지 않았다. normative 문서·Decision Catalog·STATUS·제품 source·VM·추가 실험·Git publication은 변경하지 않았다. 기존 R1-D02 원응답과 처분을 보존하며, v0.2 45,332 bytes/SHA-256 ebe30bbaeae01c58105a3439506a7ed5c1081a734da434a810cdad2bf4b294db는 기존 frozen packet에서 byte-identical하게 복구된다.

v0.3 identity: 60267 bytes; SHA-256 `4a6ec954a348133950bc6db42ee488dda434888ffc99206296d268594662e181`. 실제 문서 검증 결과와 정리는 아래에 기록한다.

### Revision 0.3 Verification And Retention

문서 3개의 GFM 렌더링, code 밖 literal 강조 기호, local path/heading links 37개, 작성 whitespace와 disclosure 검사를 통과했다. S1(B)·S2–S5·S7–S8, Question·기존 v0.2 개정표·Reversal Cost, 기존 heading과 인용을 유지했다. 열 가지 admission 기준의 대응, Draft와 accepted-only 빈 섹션, v0.2 exact 복구 및 개정 diff, 기존 CHORE·private context와 R0/R1-P01/R1-D01/R1-D02 원문·frozen 자료 보존을 확인했다. 입력 source와 HEAD·기존 tracked diff도 그대로다. 이는 문서·정적 검증이며 Windows 제품 qualification PASS가 아니다.

Owner 선택과 다음 exact 문안 비교를 위해 개정 입력 identity와 v0.2→v0.3 diff를 보존한다. 결과가 source·diff와 기존 v0.2 frozen packet으로 복구 가능하고 process 사용이 없음을 확인한 뒤, 이번 개정의 일회용 적용 helper·중복 작성 입력·문서 검증 helper/report는 삭제했다. active 경로 이동은 없다. 기존 worktree·실측 증거·VM·마지막 복구 사본은 미결 결과/복구 처분과 구체 후속 비교 의존성이 남아 유지한다. 제품 변경이 없어 현재 adopter update는 필요하지 않으며 실제 설치 상태는 미확인이다.


## R1-D03 Draft 0.3 Re-review And Driver Judgment — 2026-10-18

Owner는 “DR-0007 v0.3을 Claude에게 재리뷰받고, 특히 worker mode 변경의 최초 지원 제한과 기존 계약·admission 기준이 일관되는지 확인해줘. 네 판단과 계약 수락 전에 남은 사항도 정리해. B안은 유지하고 추가 실험이나 제품 구현은 아직 시작하지 마.”라고 요청했다. 이번 범위는 재리뷰와 Driver 판단 기록이다. 아래 accept/revise는 다음 문안에 대한 처분이며 계약 수락이나 지금의 DR 개정이 아니다. reviewed Draft 0.3 bytes를 그대로 보존한다.

### R1-D03 Request, Identity And Limits

| 항목 | 실제 값·경계 |
| --- | --- |
| Review input | DR-0007 Draft 0.3 한 문서, 60,267 bytes, SHA-256 `4a6ec954a348133950bc6db42ee488dda434888ffc99206296d268594662e181` |
| Source baseline | `a93f71c359c4f0a9d57fcfb50d5999160e870f77`; reviewed Draft는 untracked이며 tracked diff만으로 식별되지 않음 |
| Packet | 62,447 bytes, SHA-256 `54aa92d92e2404e104233e8a5cfbdc8f8a5e47e179f2951e0c0052b448293138` |
| Request | SHA-256 `9938c283ee54e9717f95cbb24bd5c1d2e0c1d2e8f74c7d3fba99566a0972fb46` |
| Reviewer | Claude Code `2.1.302`, actual model `claude-opus-5-5`, fresh session `1ebeafd6-6feb-4cfa-9485-f131e4621d72` |
| Execution | 2026-10-17 21:02:23–21:06:15 UTC; 231.416 seconds; exit 0; tool events 0; before/after input 1개 동일 |
| Final response | 13,404 bytes, SHA-256 `759cb62596a5574c6e9d6c1bb8102d6cfc6d6d3d3c89871077a0927ef88b6877` |
| Independence | 지정 Draft만 전달. Reviewer는 기존 source·계약 원문·과거 리뷰를 직접 확인하지 않았으며, 해당 사실의 독립 확인은 아래 Driver 대조와 구별 |

비밀값·계정 주소를 남기지 않고 subscription `claude.ai / firstParty / pro`와 provider override 부재를 확인했다. 직접 CLI의 no-tools 세션에 고정 문서만 전달했다. 요청한 아홉 사례는 문안상의 가상 사례이며 실행한 테스트가 아니다. 새 실험·VM 제어·제품 suite나 제품 구현은 없었다.

### R1-D03 Verdict And Driver Position

Reviewer는 전체 계약 수락 준비도, worker mode 최초 제한의 내부 일관성, 기존 계약·admission과의 일관성을 모두 conditional로 판정했다. 문서 기반 계획 준비는 approve다. P1은 없고 필수 보완은 P2 두 건, 선택적 보완은 P3 세 건이다. 이는 exact 계약 수락이나 실행 승인이 아니다.

Driver도 최초 제한의 방향은 유지하도록 권고한다. index 불변과 whole-result를 동시에 지키기 위한 제한은 타당하며, 이번 source 대조에서 이 방향을 뒤집는 새 반례는 확인하지 않았다. 다만 삭제 관측의 문구와 전체 지원 집합의 정의를 보완한 다음 exact 수락 문안을 만드는 편이 맞다. 지금 v0.3 전체를 수락 완료로 처리하지 않는다.

### R1-D03 Finding Dispositions

| Finding | Driver disposition | 판단·다음 문안 권고 |
| --- | --- | --- |
| R3-F1 · P2 · index membership과 삭제 | revise | 문구 보완을 수용한다. 현행 snapshot은 index entry가 있어도 실제 경로가 정확히 부재하면 TreeEntry에서 제외한다. 따라서 현행 source의 삭제 불가능 결함으로 보지 않는다. Windows 문안은 index를 후보 membership·존재하는 tracked 파일 mode의 출처로 설명하고, 실제 namespace 부재와 alias/type/관측 실패를 구별해야 한다. skip-worktree 등 특수 분류를 무조건 삭제로 간주하지 않는다. |
| R3-F2 · P2 · 지원 predicate와 criterion 5 | revise | 표만으로 전체 집합을 정의하는 대신 공통 mode 적용 조건과 예시 표를 함께 둔다. 현재 검증한 control 분류로 index를 바꾸지 않은 적용 후 mode/부재를 예측하고, result와 다르거나 분류가 불명확하면 전체 operation을 non-pass로 둔다. 이것은 추가 필요조건이며 기존 baseline·retained source·scope·membership·ignore·physical occupant·최종 whole-result 검증을 대체하는 충분조건이 아니다. source 읽기 실패·unmerged·허용 외 mode를 default로 바꾸지 않는다. |
| R3-F3 · P3 · pending drift와 unsupported | accept | 원래 적용 가능했던 결과가 prepare 또는 decision 이후 control index/membership drift로 불일치한 경우는 기존 drift/stale 규칙을 따른다. 정책상 unchanged index/default로 요구 post-mode를 만들 수 없는 결과의 최초 미지원, 분류 불가 unknown과 구분한다. 기존 exact 조건을 회복한 재호출 가능성을 영구 unsupported로 덮지 않는다. 복원 행위 자체에 새 권한을 부여하지 않는다. |
| R3-F4 · P3 · 비적용 처분과 drift 검증 | revise | 현재 존재하는 reject 경로를 유지한다. 새 decline 명령이나 느슨한 cancellation을 만들지 않는다. 구조·retained source·runtime·graph 검증을 충족한 review submission의 존재와 accept 가능성은 구별한다. prepare 통과 후 index/membership 변화가 생긴 경우 apply가 새 decision/content 발행 전에 거절하는 검증 사례를 계획에 명시한다. |
| R3-F5 · P3 · 리뷰 상태 문구 | accept | 다음 개정에서 R1-D03와 이 처분을 연결한다. 현재 reviewed v0.3의 작성 시점 문구는 byte-preservation 때문에 고치지 않고, 실제 재리뷰 완료 상태는 이 dated entry에 기록한다. |

F2의 rename/move/copy 설명도 좁혀 쓴다. `100755`를 유지한 결과가 control의 새 untracked destination에 놓이면 그 destination의 기본값은 `100644`여서 최초 적용 미지원이다. 모든 rename/copy를 일괄 금지하는 별도 기능 규칙은 아니다. 실제 manifest의 delete/add/modify와 각 destination 분류로 판정한다.

### R1-D03 Source Checks And Evidence Boundaries

아래는 Reviewer에게 추가로 전달하지 않은 Driver의 로컬 정적 대조다. 제품 함수를 실행하거나 반례를 재현한 결과가 아니다.

| 확인한 source·계약 | 확인한 내용과 한계 |
| --- | --- |
| [work.py](../../src/hv2ref/work.py), `_snapshot_once` 213–263행 | index와 non-ignored untracked로 후보를 만들고, 후보에서 실제 regular file 집합과의 교집합만 TreeEntry로 기록한다. 없는 후보는 `lstat`의 FileNotFoundError만 부재로 처리하며 alias/type mismatch는 거절한다. F1은 이 기존 의미를 Windows 문안에 명시할 문제다. 현재 mode는 여전히 stat에서 오므로 Windows index/default 규칙의 구현 완료 증거는 아니다. |
| 같은 파일, `_verify_worker_sources` 469–568행 및 `_worker_record_preflight` 1045–1066행 | retained Git tree의 전체 membership·mode·bytes, control baseline, worker result를 대조한다. 기존 untracked `100644` content 변경/삭제를 mode 정책만 보고 곧바로 지원한다고 선언할 수 없다. 그 current 분류에서도 기존 retained base·result와 다른 모든 선행조건을 만족하는 경우만 qualification 대상이다. 새 기본값이 uncommitted worker provenance를 허용하지 않는다. |
| 같은 파일, `_worker_content_state` 1069–1081행, `prepare/apply` 1343–1445행 | 새 acceptance는 exact baseline을 요구하고, apply는 durable decision 전에 confirmation을 반복한다. changed-path physical 관측·outside drift·whole-result를 별도 검사한다. F2의 control index drift 예시는 이 기존 의미를 Windows 분류에도 보존해야 하는 확인 항목이며 현재 baseline guard가 없다는 증거가 아니다. |
| 같은 파일, `publish` 1262–1340행 및 `_worker_confirmation` 1433–1445행; [General Work — Pending Operations](../GENERAL-WORK.md#pending-operations-and-exact-recovery) | review submission은 pending 자체가 아니며 일반 reject와 pending accept의 cancellation은 다르다. 새 mode 제한만으로 valid reject를 막지 않되 기존 runtime/record/pending guard를 유지한다. “무관한 operation을 이 사유만으로 막지 않는다”는 문구가 이미 존재하는 worker pending의 다른 writer 차단을 해제하지 않는다. |
| [General Work — Worker Publication](../GENERAL-WORK.md#worker-publication-development-checkpoint), [Structure — Content Trees](CHECKOUT-1-STRUCTURE.md#content-trees-and-manifests), [Windows Admission](README.md#windows-admission) | control HEAD/index/refs 불변, 전체 결과 검증, 과거 기록·replay/cancellation 보존과 열 가지 admission 의무를 원문에서 확인했다. criterion 5의 Windows 지원 집합 변경과 criterion 8의 제한 표시를 exact 문안으로 연결해야 하며 criteria 6–9, macOS 성공 기대와 B의 전체/집중 검증 배정은 면제되지 않는다. |

병렬 상태의 제한된 대조도 했다. 이 worktree의 baseline은 `a93f71c`이고, 조회 시 primary checkout HEAD `98ef91f`는 그 ancestor였다. 위 worker source·General Work·Structure와 Windows Admission 본문은 그 두 revision 사이에서 동일했다. README의 다른 절과 Workspace 계약에는 차이가 있어 primary 경로 이름만으로 더 최신이거나 통합 완료라고 간주하지 않았다. 이는 모든 active worktree와 uncommitted 병렬 변경을 대조한 통합 승인 검사가 아니다. exact 수락·통합 대상 revision이 정해지면 다시 대조해야 한다.

### R1-D03 Case Assessment And Final Recommendation

| 사례 | Driver 권고·근거 |
| --- | --- |
| tracked `100644`/`100755`의 안정된 mode + content 변경 | 기존 모든 guard와 새 Windows 관측/physical 일치 검증 아래 qualification 대상 유지. 실행 가능성·ACL 증거로 mode를 해석하지 않음 |
| `100644↔100755` 결과 또는 새 untracked `100755` destination | unchanged control index/default로 post-mode를 관측할 수 없으므로 최초 전체 적용 미지원. 새 decision/content 전 거절 |
| add-`100644`, tracked `100644`/`100755` 삭제 | qualification 대상 유지. 삭제는 실제 namespace 부재로 판정하고 index entry 잔존 자체를 파일 존재로 간주하지 않음 |
| 기존 untracked `100644`의 content 변경·삭제 | 공통 mode 조건으로는 배제하지 않지만 retained Git provenance·exact baseline 등 기존 worker 자격을 만족하는 경우에만 대상. 일반 local/non-Git snapshot 지원과 worker 자격을 혼합하지 않음 |
| 지원·미지원 경로가 섞인 결과 | 한 경로라도 mode 적용 조건을 만족하지 못하면 기존 operation 전체 거절. 일부 파일만 성공 처리하지 않음 |
| prepare 이후 drift·이미 pending·completed replay | 각각 새 발행 전 재검증, 원 prefix 보존 및 기존 복구/취소, 기존 read-only replay 조건 유지. 모두를 unsupported 한 종류로 묶지 않음 |
| valid unsupported-to-apply submission | 기존 검증으로 review 기록을 읽고 처분할 수 있는 것과 적용 가능성은 별개. ordinary reject는 원래 조건 아래 유지하며 pending cancellation의 all-pre/no-selection 조건은 넓히지 않음 |
| 기준 5–9와 B | criterion 5의 지원 집합·거절 의무와 criterion 8의 표시를 exact 문안으로 고정. 전체 회귀·interruption·inventory identity·macOS 기대와 formal Windows admission 시점 유지 |

다음 문안에서의 핵심은 “기존 worker 자격과 독립적인 결과 검증을 모두 유지한 채, 현재 control의 unchanged-index/default 정책으로 요구 post-mode를 실현할 수 있는 결과만 최초 적용 대상으로 삼는다”이다. mode 예측은 실제 bytes·membership·부재의 사후 검증을 대신하지 않는다. result manifest는 목표값이며 현재 관측의 근거가 아니다. 미지원·drift·unknown의 구별과 valid non-apply 처분을 함께 설명하면 제한이 안전성과 사용 흐름 양쪽에서 명확해진다.

### R1-D03 Remaining Matters Before Contract Acceptance

1. F1·F2를 반영한 삭제 의미와 공통 적용 조건을 exact 문안으로 고정한다. criterion 5의 검증 목록에는 tracked 644/755 content-only, 자격을 만족하는 기존 untracked 644 변경·삭제, add-644, tracked 삭제, mixed-result 거절과 prepare→apply drift를 일관되게 대응한다. 새 untracked destination에 755가 필요한 rename/copy의 파생 제한도 관련 표시 범위에 넣는다.
2. 네 대상의 실제 amendment 문안을 준비한다: Windows Admission criterion 5, criterion 8의 공개 표시, General Work worker checkpoint의 Windows 단락, Structure의 mode·membership 관측 단락. criteria 6–9의 유지 의무와 macOS 범위는 보존한다. 문안 준비 자체가 normative 파일의 즉시 발효를 뜻하지 않는다.
3. Windows OS/runtime·successor window 조합을 기존 binding/profile로 확실히 구분할 수 있는지 설계에서 판정한다. 새 persisted 의미나 reader 호환 변경이 필요하면 S2와 함께 exact 수락 대상에 포함한다. API/flag·알림 형식까지 모두 수락 선행조건으로 올리는 순환은 만들지 않는다.
4. Owner는 Windows `100644` 기본값, 기존 기록/replay 보존, non-Git 및 worker 최초 제한과 named scope를 exact revision에 대해 선택한다. B 유지 지시를 다시 승인받는 항목으로 만들지 않는다. 이번 review verdict는 그 선택을 대신하지 않는다.
5. 수락 대상 baseline과 병렬 변경을 다시 고정하고 findings 처분을 연결한다. 구현 방법과 qualification 계획은 계약 문안과 함께 준비할 수 있지만, 실제 mutation은 필요한 계약 수락과 실행 승인을 받은 범위에서만 진행한다.

계약을 바꾸지 않는 분류 세부·index 안정성 기법·검사 위치·오류 코드·물리 occupant 대응은 계획에서 구체화한다. 실제 Windows qualification에는 supporting/refusal 양쪽 사례, pending·동시성·macOS 회귀와 B의 UTM 전체 및 x64 focused 검증이 남는다. 위 문서 보완을 위해 지금 추가 실험을 강제할 이유는 확인하지 않았다.

### R1-D03 Actual Owner Decision

이번 Owner 승인은 지정 Draft의 Claude 재리뷰와 Driver 판단 정리다. B 유지와 추가 실험·제품 구현 금지가 계속 유효하다. DR-0007 v0.3은 reviewed bytes 그대로이며, 새 개정·계약 수락·activation·제품 실행·Git publication은 이 재리뷰에서 수행하지 않았다.

### R1-D03 Reviewer Final — Verbatim
````markdown
# R1-D03 — DR-0007 Draft 0.3 정적 재리뷰

입력은 packet의 DR-0007 Draft 0.3 한 문서(60,267 bytes, SHA-256 `4a6ec954…2e181`)뿐입니다. source, 기존 계약 원문, D02-D1 기록, 이전 리뷰는 읽지 않았습니다. 문서가 요약한 기존 계약과 source 사실은 보고된 주장으로만 다뤘습니다. 판정은 문서 내부 정합성과 정적 추론에 근거합니다.

## 1. Verdict

| 대상 | 판정 | 요지 |
| --- | --- | --- |
| 전체 계약 수락 준비도 | **conditional** | P1은 없습니다. 의미 선택(S1–S8)을 Owner에게 제시할 수준입니다. 다만 exact 수락 전에 R3-F1·F2 보완, criterion 5와 worker checkpoint의 amendment 문안, S2 binding/profile 충분성 판단이 남아 있습니다. |
| worker mode 최초 제한의 내부 일관성 | **conditional** | D02-D1 논리와 prepare/apply 발행 전 거절은 타당합니다. 그러나 지원 집합이 base→result 열거식이라 공백이 있고(F2), 삭제 행이 index-derived membership과 충돌할 여지가 있습니다(F1). |
| 기존 계약·admission과의 일관성 | **conditional** | index 불변, whole-result, 기록 보존, criteria 6–9 비면제, macOS 기대 유지, B 시점이 모두 보존됩니다. 다만 criterion 5 검증 목록(314행)이 지원 집합의 일부만 지정합니다. |
| 문서 기반 계획 준비 | **approve** | 336행의 병행 원칙대로 계획 문서는 지금 준비할 수 있습니다. F1·F2는 계획 작성 중 함께 고정하면 됩니다. |

이 판정은 Owner의 계약 수락, 제품 실행 승인, 발효를 대신하지 않습니다. approve 항목도 마찬가지입니다.

## 2. Must-fix 및 선택적 보완

### R3-F1 · P2 · 조건부 — 삭제 행과 "index에서 membership" 규칙의 충돌 가능성

- **위치**
  - 195행: "검증한 index에서 membership·mode를 얻고 bytes는 working tree에서 관측"
  - 228행: "기존 tracked `100755` 파일의 삭제 … 부재를 결과로 검증하는 기존 삭제 경로"
  - 314행: "delete 경로"
- **반례·오해 경로**
  - worker 적용은 index를 바꾸지 않으므로 삭제 후에도 control index에는 entry가 남습니다.
  - 195행을 문자 그대로 읽어 membership을 index에서 얻으면 적용 후 snapshot은 그 경로를 여전히 member로 봅니다. 그러면 bytes 관측 실패로 199행의 unknown 거절에 걸리거나 whole-result의 "부재"와 영원히 불일치합니다.
  - 이는 D02-D1과 같은 구조의 결함입니다. 불변 index가 결과 관측을 막는 것입니다.
  - 202행은 skip-worktree 등을 계획으로 미뤘지만, 일반 stage-0 entry의 working-tree 부재(unstaged deletion)는 어디에도 정의되어 있지 않습니다. skip-worktree는 반대로 부재를 삭제로 보면 안 되는 사례이므로, 기본 규칙이 문서에 있어야 계획 세부가 안전하게 갈립니다.
- **조건**: 현행 snapshot이 이미 unstaged deletion을 부재로 관측한다면 문구만 명시하면 됩니다. Driver가 source를 대조해 확정해야 합니다.
- **최소 수정** (195행 출처·보존 조건 열에 추가)
  > index의 stage-0 entry는 존재하는 경로의 mode 출처다. entry가 있어도 working-tree 경로가 없으면 그 경로는 부재(삭제)로 관측한다. skip-worktree 등 부재가 삭제를 뜻하지 않는 분류는 계획에서 별도로 정하고, 판별할 수 없으면 unknown이다.

### R3-F2 · P2 — 지원 집합을 예측 predicate로 정의하고 criterion 5 검증 목록을 맞출 것

- **위치**
  - 224–231행 표 (base→result 변경 유형 열거)
  - 314행: "stable tracked 100755 content-only/add-100644/delete 경로"
- **공백 1 — 판정되지 않는 사례가 있습니다**
  - 기존 untracked 100644 파일의 content-only 변경과 그 삭제가 표에 없습니다.
  - 기존 tracked 100644 삭제도 명시되지 않았습니다.
  - 231행의 "그 밖에" 행은 "독립 관측할 수 없는 결과"만 거절하므로 이 사례들을 잡지 않습니다. 이들은 관측 가능한 사례라 지원 여부가 열린 채로 남습니다.
- **공백 2 — "기존 mode"의 기준이 worker base인지 현재 control인지 불명확합니다**
  - 예: worker 시작 후 사용자가 control에서 `git update-index --chmod=+x`를 실행하고, result는 100644 content-only인 경우입니다.
  - worker 관점에서는 "mode 유지"이지만, 적용 후 관측은 100755 ≠ 100644입니다.
  - 기존 drift 규칙이 prepare 전에 이를 거절하는지는 문서만으로 확정할 수 없습니다.
- **공백 3 — 314행이 qualification 검증 목록을 좁힙니다**
  - 314행은 tracked 100644 content-only, 즉 가장 흔한 경로를 명시하지 않습니다.
  - 316행의 full suite가 보완하더라도, criterion 5의 "지원 결과의 실제 integrity 검증" 목록이 지원 집합보다 좁으면 합의된 범위가 흐려집니다.
- **최소 수정** (222행 뒤에 규범 문장 추가, 표는 "예"로 강등)
  > Windows successor의 worker 결과는 각 경로마다 적용 후 control에서 관측될 논리 entry를 현재 검증한 control 분류로 예측한다. index stage-0 entry가 있으면 그 mode, 없으면 기본값 `100644`, 결과가 부재면 부재다. 모든 경로의 예측이 result entry와 같을 때만 적용 대상이다. 하나라도 다르면 operation 전체를 거절하고, 예측할 수 없으면 unknown으로 보존한다. prepare·apply의 발행 전 검사와 완료 전 whole-result 관측은 같은 분류 함수를 쓰며 result manifest의 기대값을 관측값으로 쓰지 않는다.
- 314행은 "S6 predicate가 허용하는 결과 집합(tracked 100644/100755 content-only, 기존 untracked content 변경, add-100644, tracked/untracked 삭제 포함)"으로 바꾸십시오.
- **파생 결과의 공개**: 이 predicate 아래에서 tracked 100755 파일의 worker 내 rename/move/copy는 새 경로가 control에서 untracked이므로 미지원이 됩니다. "rename = delete + add, 삭제는 지원"이라는 오해를 막도록 317행 parity 목록에 이 결과를 적으십시오. 의미 변경은 아니고 공개 범위만 보완하는 것입니다.

### R3-F3 · P3 — pending 상태에서 drift로 생긴 불일치와 unsupported를 구분

- **위치**: 237행 "mode 의미를 독립적으로 검증할 수 없으면 unsupported로 멈춘다", 214행
- **경로**
  - Windows successor에서는 새 결과를 사전 거절하므로, pending 상태의 mode 불일치는 주로 decision 발행 후 사용자의 index 변경(drift)에서 생깁니다.
  - 이 경우 mode는 독립 관측 가능하며 단지 불일치할 뿐입니다. 따라서 기존 stale/outside-drift 범주에 속하고, 상태를 복원하면 기존 재호출 규칙으로 복구될 수 있어야 합니다.
  - 237행 문구는 이를 "unsupported"로 영구 분류한다고 읽힐 수 있습니다.
- **최소 수정**
  > 관측 가능한 불일치는 기존 drift/stale 규칙을 따른다. unsupported는 정책상 post-mode를 관측할 수 없는 결과에 한정한다.

  오류 코드 매핑은 계획 세부로 두어도 됩니다.

### R3-F4 · P3 — 미지원 submission의 비적용 처분과 drift 재검증 시험

- 214행 "무관한 operation을 이 사유만으로 차단하지 않는다"의 원칙상, 미지원 결과에 대한 기존 reject/decline 처분은 계속 가능해야 합니다. 그래야 Work가 해소 불가능한 submission에 묶이지 않습니다. 원칙은 충분하므로 예시 한 줄만 권고합니다.
- 314·315행에 "prepare 통과 → index/membership 변경 → apply 발행 전 거절" 사례를 추가하십시오. 235행의 재검증 의무에 대응하는 검증이 현재 목록에 없습니다.

### R3-F5 · P3 — 상태 기록 갱신 (housekeeping)

- 36행과 354행의 "Claude 재리뷰 미수행"은 작성 시점의 기록입니다.
- 다음 개정에서 R1-D03의 존재와 disposition을 기록하되, 이것이 v0.3 승인으로 읽히지 않게 338행의 형식을 따르십시오.

## 3. 사례별 compact table

| # | 현재 규칙 (줄) | 일관성 | 남은 의미 선택 / 구현 검증 |
| --- | --- | --- | --- |
| 1 | 226행 지원. mode는 불변 index에서, bytes는 working tree에서(195). 확장자·stat·chmod로 추정하지 않음(191·206·243) | 일관됨. 실행 가능성과 논리 mode가 분리되어 있음 | base와 control 중 어느 기준인지(F2). 물리 chmod와 occupant 일치는 계획(247) |
| 2 | 229행 미지원. prepare는 ticket을 발급하지 않고, apply가 재검증해 decision·selection·current·content 발행 전 거절(235). 기대 mode를 관측값으로 재사용 금지(233) | 순환 없음. D02-D1의 영구 pending 위험을 차단함 | 검사 위치와 발행 predicate는 계획. predicate 규범화 권고(F2) |
| 3 | 새 untracked 100644 지원(227), 100755 미지원(230), 기본값 100644(197·206). tracked 100755 삭제 지원(228) | 기본값 기준으로 일관됨. 100755 삭제를 불필요하게 제외하지 않음 | 삭제 관측 의미(F1). rename/copy 결과의 공개(F2) |
| 4 | operation 전체 거절(214·231), 부분 성공 금지(294), 원본·retained 보존(218·294) | 충분함 | 혼합 결과 시험은 314행이 포괄함 |
| 5 | apply 재검증(235), pending은 prefix 보존 후 non-pass(237·295), completed replay에 새 거절 추가 없음(216), scratch/lock 예외(235·S4) | 대체로 일관됨. scratch 예외가 보존 대상을 침범하지 않음 | drift와 unsupported 구분(F3), prepare→apply drift 시험(F4) |
| 6 | 원 mode로 읽기(216), 100755 기록이 지원을 뜻하지 않음(218), old-window는 진단만(124), 원참조 기대값은 독립 대조(200) | 읽기·진단, 적용 지원, 새 authority가 분리되어 있음 | 없음 |
| 7 | criterion 5 amendment 후보로 명시(279·296·314). 6–9는 유지 의무와 함께 대응(297–298·315–318) | 명시적이며, 6–9의 면제나 의미 변경은 없음 | criterion 5의 exact amendment 문안 미작성(§4) |
| 8 | 예상 거절과 stable-mode 성공을 함께 요구(314), macOS mode 성공 유지(316), skip을 PASS로 바꾸지 않음(300), B와 시점 유지(302) | 충족함 | 314행 검증 목록 확장(F2) |
| 9 | Named Map(277–285)과 Impact 표(291–298), 미수락 상태(24·289·325) | scope와 유지 조항이 식별됨 | 아래 §4 |

## 4. 계약 수락 전 vs 구현·qualification 세부

### 수락 전 — Owner 선택

- 327–334행의 S1–S8 의미 선택.
- worker 최초 제한을 "Windows 초기 지원 범위의 축소"로 수락할지 여부와, 그에 따른 criterion 5 범위 변경.

### 수락 전 — 문서 보완

- F1(삭제 관측)과 F2(지원 predicate, 314행 목록)를 반영합니다.
- 다음 named clause의 exact 문안 초안을 작성합니다. 지금은 "amendment 후보"라는 서술만 있습니다.
  - Windows Admission criterion 5와 8
  - GENERAL-WORK worker checkpoint의 Windows 단락
  - Structure의 TreeEntry 출처 단락
- 기존 binding/profile로 Windows successor 조합을 식별할 수 있는지 판정합니다(189행). 부족해서 새 persisted 표식이 필요하면 S2의 window/reader 의미와 함께 수락 대상이 되므로, 계획으로 넘기면 안 됩니다.
- baseline 이후 병렬 변경을 대조합니다(44행).

### 계획·qualification 세부 (계약을 바꾸지 않는 한)

- stage-0, intent-to-add, skip-worktree 분류. index 안정성 확인 방법.
- 사전 검사 위치, 오류 코드 매핑, 알림 단위와 위치.
- Windows에서의 물리 chmod 처리와 occupant 일치 확인.
- 시험 목록:
  - tracked 100644/100755 content-only
  - 기존 untracked content 변경
  - add-100644
  - tracked/untracked 삭제
  - 혼합 결과의 decision/content 무발행
  - prepare→apply drift
  - pending 보존
  - 100755 rename 거절
  - macOS mode 성공 회귀
  - UTM full suite와 x64 focused 검증

## 5. 해결·무반례 항목과 한계

### 반례를 찾지 못했거나 해결된 항목

- index 불변 의무 유지. index 자동 변경, registry/sidecar, manifest fallback을 채택하지 않음(239).
- whole-result 유지. 무결성 완화가 아니라 지원 집합 축소임(300).
- 새 approval 층이나 단회 token이 없음(267·325).
- 기대값 순환 금지(233).
- macOS의 worker mode 계약은 축소하지 않음(239·316).
- R2-F3(unknown을 기본값으로 대체하지 않음)과 R2-F4–F7(과거 기록 보존, replay와 recovery 구분, 관측마다 정책 재평가)은 v0.3이 설명한 범위 안에서 해소된 것으로 봅니다.
- S5 phase 분류와 S8 재호출 규칙은 S6의 pending/replay 구분과 충돌하지 않습니다.

### 읽지 못한 근거와 잔여 한계

- 현행 snapshot이 unstaged deletion을 어떻게 다루는지 확인하지 못했습니다. F1은 이 확인에 달려 있습니다.
- worker base와 control 사이의 drift 규칙, prepare/ticket의 실제 존재와 persisted 여부, README의 criteria 원문을 확인하지 못했습니다.
- D02-D1 기록과 `_stable_file` 동작은 245행의 보고만 근거로 삼았습니다.
- 이 리뷰는 정적 검토이며 실행 증거를 만들지 않았습니다. 계약 수락, 제품 실행, 발효를 대신하지 않습니다.
````


### R1-D03 Record Verification And Retention

문서 3개의 GFM 렌더링, code 밖 literal 강조 기호, local path/heading links 42개, 작성 whitespace와 disclosure 검사를 통과했다. reviewed v0.3의 exact bytes와 frozen packet 복구, request/packet/final digest 및 source 내 verbatim 일치, 기존 CHORE 본문과 R0/R1-P01/R1-D01/R1-D02 원문·frozen 자료 보존을 확인했다. source HEAD·기존 tracked diff·다른 고정 입력은 그대로다. 이는 문서·정적 확인이며 Windows 제품 실행 또는 qualification PASS가 아니다.

Reviewer 종료, final/partial 동일 bytes, 빈 stderr·tool-temp 및 lsof 사용 주체 없음 확인 뒤 중복 partial, 빈 stderr와 빈 tool-temp를 삭제했다. request/packet/inputs/final/metadata/invocation 여섯 파일은 Owner 처분과 다음 exact 비교를 위해 보존한다. 소비가 끝나면 기존 정리 기준으로 재평가한다. active 경로 변경은 없으며 기존 worktree·VM·raw evidence·마지막 recovery 자료는 결과 수락·복원 확인·후속 작업의 기존 소비자와 종료 조건 때문에 유지한다.

최종 기록 검사 후 일회성 문서 검사기와 재생성 가능한 검사 출력도 삭제했다. 검증 결과는 이 진행 기록과 기존 private task context에 남겼으며 삭제 뒤 최종 문안을 다시 렌더링·확인했다.


## Contract Draft Revision 0.4 — 2026-10-18

Owner는 R1-D03와 Driver 권고를 DR-0007 v0.4에 반영하고, 삭제 관측·worker 공통 적용 조건·관련 exact amendment와 기존 binding/profile의 식별 충분성을 확인하도록 요청했다. B 유지와 추가 실험·제품 구현 금지를 지켰다. 문서 보완 승인은 계약 수락이나 발효가 아니다.

[DR-0007 Draft 0.4](../decisions/DR-0007-windows-native-runtime-contract.md)은 index 후보 membership과 실제 namespace 부재를 구별하고, worker 적용 가능성을 현재 control 분류로 판단하는 공통 필요조건을 추가했다. base/result 경로의 합집합을 대조하되 기존 retained source·exact baseline·scope·ignore·physical occupant·whole-result 의무를 유지한다. 기존 untracked 644 변경·삭제는 worker 자격도 충족할 때만 대상이고, 새 untracked destination의 755와 혼합 결과는 전체 사전 거절한다. drift/stale·policy unsupported·unknown, ordinary reject·pending cancellation·completed replay도 구분했다.

Exact Proposed Contract Amendments의 A1–A5는 Structure content 관측, General Work Windows worker, Windows criteria 5/8, Structure Windows policy identity의 정확한 삽입·교체 위치와 영어 본문이다. 현재 normative 파일은 바꾸지 않았다. criterion 5의 최초 지원 집합과 거절 검증, criterion 8의 표시를 보완하며 criteria 6–9·macOS 회귀·B 배정·formal admission 시점은 면제하지 않는다.

binding/profile의 정적 판정: 현행 entry-1/CLI profile 값만으로 Windows mode 정책을 식별할 수 없다. `product.py`의 binding·release/inventory 검증과 runtime gate, `cli.py`의 profile 분기, `workspace.py`의 runtime 및 target fingerprint, root `colvia` bootstrap과 Structure shape를 대조했다. profile은 persisted binding/plan field가 아니고 현행 runtime check는 CPython 조건만 본다. 기존 release/window/digest 구조에 Windows 전용 successor 의미를 결합하고 실제 native runtime을 재검증하면, mode 정책 식별만을 위해 새 record field를 넣지 않는 설계를 권고할 수 있다. 이는 구현 PASS가 아니다. exact window literal·membership·schema/window pairs·reader/writer 집합과 그 의미의 Owner 수락은 미결이다.

v0.4는 85,672 bytes, SHA-256 `3901b4c5f6edbc21be065bf900e6ee7fbb610ba5bdf9dacb3d196ef49d2e62ff`이다. v0.3 exact 60,267 bytes와 SHA-256 `4a6ec954a348133950bc6db42ee488dda434888ffc99206296d268594662e181`는 R1-D03 frozen packet에서 복구할 수 있다. 이전 리뷰 원문과 당시 판단을 수정하지 않았다. v0.4의 Claude 재리뷰·Owner 계약 수락은 아직 없다. STATUS·Decision Catalog·현재 normative 계약·제품 source·VM·Git publication은 변경하지 않았다.

### Revision 0.4 Verification And Retention

최종 문서 3개의 GFM 렌더링, code 밖 literal 강조 기호, local path/heading links 53개, 작성 whitespace·disclosure 검사를 통과했다. A1–A5의 삽입/교체 위치를 현재 계약에서 확인하고, 대상 문서 3개의 개정 미리보기를 메모리에서만 만들어 렌더링했다. 실제 normative 파일에는 쓰지 않았다. S1(B)·S3–S5·S7–S8, Question·기존 개정표·Reversal Cost·기존 heading과 인용, 열 가지 admission 대응과 Draft의 accepted-only 빈 섹션을 확인했다.

v0.3 exact 복구와 개정 diff, 기존 CHORE/private context 본문 및 모든 이전 리뷰의 원문·frozen 자료를 보존했다. 다른 23개 입력 중 변경 대상 외 파일, source HEAD와 기존 tracked diff도 그대로다. 이 결과는 문서·정적 검증이며 Windows 제품 qualification PASS가 아니다.

입력 identity와 v0.3→v0.4 diff는 Owner 비교·다음 exact review를 위해 보존한다. 검증과 lsof 사용 주체 없음 확인 뒤 일회성 revision payload·적용 script·문서 검사기·재생성 가능한 검사 출력을 삭제하고 최종 기록을 다시 확인했다. active 경로 변경은 없다. 기존 worktree·VM·raw evidence·마지막 recovery 자료는 결과 수락·복원 확인·후속 작업의 기존 소비자와 종료 조건 때문에 유지한다.


## R1-D04 Draft 0.4 Re-review And Driver Judgment — 2026-10-18

### Authorization, Input And Evidence Boundary

Owner는 “DR-0007 v0.4를 Claude에게 재리뷰받고, 특히 삭제 관측·worker 공통 적용 조건, A1–A5 개정 문안과 binding/profile 식별 방안의 일관성을 확인해줘. 네 판단과 계약 수락 전에 남은 사항도 정리해. B안은 유지하고 추가 실험이나 제품 구현은 아직 시작하지 마.”라고 요청했다. 이번 작업은 고정 Draft의 정적 리뷰 1회, Driver의 source/계약 대조와 이 진행 기록 갱신이다. DR v0.4, 현행 normative 계약·admission 및 제품 source는 수정하지 않는다.

- 검토 대상: [DR-0007 Draft 0.4](../decisions/DR-0007-windows-native-runtime-contract.md), 85,672 bytes, SHA-256 `3901b4c5f6edbc21be065bf900e6ee7fbb610ba5bdf9dacb3d196ef49d2e62ff`. source baseline `a93f71c359c4f0a9d57fcfb50d5999160e870f77`; 이 Draft는 tracked diff 밖의 untracked 입력이다.
- 기존 tracked diff SHA-256: `91f501b2077cfc175ae80edbddd2f56a32b71c2bcb6c6b7c1659d01c3e42a7ef`. 이번 검토로 변경하지 않았다.
- request SHA-256: `71b01e20ea15df966040164f66a6b00618c903a92dde333f3baf741de9b6d632`; numbered single-document packet SHA-256: `773c66d25ff8ea74a89504a6dadc82055b6cd3e6232f2bad2c84c06bb7f32585`.
- Reviewer: Claude Code `2.1.302`, 실제 model `claude-opus-5-5`, fresh session `a6cd3c9a-7184-4f2a-a2d4-b8b2c11d077e`. 비밀값 없는 사전 확인은 `claude.ai / firstParty / pro`, provider override 없음이다.
- 2026-10-17 21:37:05–21:41:06 UTC, 241.036초, exit 0, tool event 0, 입력 1개 전후 일치. 최대 1,200초의 no-tools 정적 요청이며 제품 test/probe는 실행하지 않았다.
- 최종 원문: 15,862 bytes, SHA-256 `871e0d851ced07ffea01fa086fdf24e57623ea8926e7716fe1479cb6b9b59929`.

Reviewer에게 보낸 자료는 지정 DR 하나뿐이다. linked source·현행 target 계약·probe 원출력·이전 private 리뷰는 보내지 않았다. 따라서 아래 조건부 source 판단은 Reviewer의 독립 확인이 아니며, Driver가 뒤에서 별도로 대조한다. 이 dated record는 v0.4 작성 당시의 “재리뷰 없음” 문구 이후 실제 리뷰가 완료됐음을 기록한다. 리뷰 대상을 고정하기 위해 그 문구를 이번 라운드에서 소급 수정하지 않는다. Owner 계약 수락·제품 실행·activation은 여전히 없다.

### Verdict And Driver Judgment

| 구분 | Reviewer | Driver 판단 |
| --- | --- | --- |
| 전체 exact 계약 수락 준비도 | conditional | 동의. 남은 exact identity·named clause와 아래 문안 처분을 포함한 수락 대상이 필요 |
| 삭제·worker 공통 조건 | conditional | 핵심은 일관됨. 부재 아닌 관측의 non-pass를 명시하고, 조건으로 정의한 지원 범위를 A2/A3에도 동일하게 표현할 것을 권고 |
| A1–A5 내부 정합성 | conditional | target 위치·원 fragment는 로컬에서 확인. 범위·참조·동시 수락 관계를 보완해야 함 |
| binding/profile 식별 설계 방향 | conditional, 방향 타당 | 기존 shape 재사용 권고 유지. pre-binding chain은 source에 이미 존재. detach 뒤 진단 한계와 old-writer 실패 분기를 명시해야 함 |
| 문서 기반 계획 준비 | approve | 동의. 계약 문안과 필요한 계획 세부는 함께 준비 가능. 제품 실행 승인은 아님 |

P1은 없고 P2 4건·P3 4건이다. 이 숫자는 실행 결함 개수가 아니다. F1은 문안 명확성, F3/F4/F8은 source 조건부 판단을 포함한다. 아래 `accept/revise`는 후속 문안에 대한 Driver 처분이며 계약 수락이나 이번 DR 자동 수정이 아니다.

### R1-D04 Finding Dispositions

| ID | Severity | Driver | 판단과 후속 권고 |
| --- | --- | --- | --- |
| D04-F1 | P2 | revise | 부재 아닌 관측을 non-pass로 명시하고 S3의 경로·ancestor 검사와 연결하는 취지는 수용. 다만 v0.4는 이미 해당 관측을 부재가 아니라고 하며 현행 source도 tracked type/alias 불일치를 거절한다. 현재 구현의 삭제 오판을 재현했다고 하지 않는다. 해당 관측을 통과한 snapshot으로 반환하거나 삭제로 기록하지 않는다는 문장으로 보완 |
| D04-F2 | P2 | revise | 권고 (a)의 닫힌 목록으로 자동 축소하지 않는다. S6는 명시적으로 공통 조건과 기존 모든 guard로 지원을 판정하고 표를 예시로 둔다. 그 방향을 보존하는 (b)를 권고: A2에 비열거 결과도 같은 조건으로 판정함을 명시하고 A3에 index-only tracked 경로의 복원/add 대표 사례를 포함. exact 범위는 Owner 수락 대상 |
| D04-F3 | P2 | revise | fresh 선택 규칙·profile과 candidate 검증의 결합 설명을 보완. 원 init plan의 candidate release에는 이미 window가 있고 canonical request token에 결속된다. pre-binding 구간에 새 field가 필요하다는 조건부 우려는 현행 source에서 성립하지 않는다. detach receipt는 prior binding/삭제 inventory의 digest를 보존하지만 제거된 window literal을 자체 복구하지는 않는다. 재초기화 차단과 정책 출처 진단의 한계를 분리해 적을 것을 권고 |
| D04-F4 | P2 | revise | 알려진 cooperating old writer의 실제 발행을 “미지원” 표기만으로 통과시키지 않는다는 취지는 수용. 이미 S2에 같은 원칙이 있으므로 실패 시 분기를 직접 연결. 다만 실패 하나로 기존 record shape 전체가 불충분하거나 format 변경이 필수라고 단정하지 않는다. 해당 candidate의 qualification/activation을 막고, 유효한 최소 거절 장치 또는 검증 가능한 비노출 근거를 선택하며 persisted 의미 변경은 exact 수락 대상으로 돌린다 |
| D04-F5 | P3 | revise | OS/process architecture·에뮬레이션·32-bit·POSIX 호환 환경의 지원/미지원 범위를 문서로 명시하는 취지 수용. native 64-bit ARM64/x64 경로를 최초 대상으로 두고 다른 조합을 자동 지원으로 읽지 않는 방향을 권고. 구체 포함 여부는 S1/S2/S7에 일치시킬 계약 선택이며 관측 tuple 하나의 자동 allowlist, 새 full matrix·물리 PC gate 또는 지금의 추가 probe로 확대하지 않음 |
| D04-F6 | P3 | accept | A1의 Windows 한정 scope를 하위 heading 또는 동일 범위 문구로 명시. A2의 index 불변은 operation이 HEAD/index/refs를 변경하지 않는다는 문장으로 보완하여 외부 drift가 불가능하다는 뜻과 구별 |
| D04-F7 | P3 | revise | A3의 A1/A2 참조·add 용어를 정렬하고 S1 allocation의 exact amendment와 함께 수락할 관계를 명시. source-only DR 식별자를 shipped 문서의 작동에 필요한 링크로 추가하지 않는다. target 안에서 해석 가능한 범위를 적고 수락 기록이 named clause를 연결하도록 할 것을 권고 |
| D04-F8 | P3, source 조건부 | revise | 현행 source상 retained commit에 있는 644 파일이 control index에서만 제거되고 같은 bytes로 non-ignored untracked에 남는 구성이 가능하므로 범주를 삭제하지 않는다. 그 경우에도 commit/refs·whole baseline·필수 참조 등 모든 guard가 필요하다. 도달 가능성은 아래 정적 논증이며 실행 PASS가 아니다. 후속 qualification에 구체 fixture를 두고 미실행을 N/A/PASS로 바꾸지 않음 |

### Driver Source Cross-checks

1. **삭제와 common condition.** `work.py:132–155, 213–263`의 actual file enumeration과 candidate membership, missing tracked path의 `lstat` 분기가 분리돼 있다. 실제 type/alias mismatch를 단순 deletion으로 숨기지 않는다. Windows reparse/ancestor 거절의 통합 구현은 아직 검증하지 않았다. `work.py:469–553, 1045–1081`은 retained whole Git tree·mode·변경 집합, control baseline, physical occupant와 snapshot 일치를 별도로 요구한다. `1342–1445`는 prepare/apply 재검증, 완료 replay와 pending 처분을 구분한다. A1/A2는 이 의무를 보존하는 새 Windows 제안이다.
2. **비열거 tracked add의 정적 사례.** retained base와 actual base snapshot에는 P가 없지만 control index에 정상 stage-0 755 P가 있고 실제 파일은 부재인 구성을 가정한다. worker candidate가 같은 P를 755로 추가하면 Windows 제안의 관측은 적용 후 index 755와 실제 bytes를 사용할 수 있다. mode 변경이나 새 untracked 755와 다른 사례다. 현재 baseline/retained-source 검사는 index의 파일 존재 자체를 baseline tree로 강제하지 않으므로 이 사례를 문안에서 다룰 필요가 있다. 필요한 모든 다른 guard가 성립하는 구체 qualification은 별도이며 이번에 실행하지 않았다.
3. **eligible untracked의 정적 사례.** retained base commit에는 P가 644로 존재하되 control index에서만 제거됐고 bytes는 같은 non-ignored regular file로 남아 있으면, `ls-files --others`를 포함하는 snapshot은 P를 유지한다. worker candidate의 P 변경·삭제도 retained commit으로 검증할 수 있다. 최초 baseline의 control HEAD 조건과 whole-tree·mode/bytes 조건은 그대로 만족해야 한다. index와 commit이 항상 같은 membership이어야 한다는 신규 의무를 추정해 이 범주를 없애지 않는다.
4. **binding 이전 chain.** `product.py:1011–1034`의 init plan은 `candidate_release={id, sha256, inventory_id}`를 포함한다. `workspace.py:342–352`는 그 shape를 검사하고, `product.py:1115–1138`은 전체 canonical request의 token, candidate와 plan release 일치, 원 plan을 재검증한다. 따라서 기존 shape는 pre-binding policy identity를 운반한다. 현재 source/profile/allowlist는 entry-1뿐이며 새 Windows 선택·검사 경로가 이미 구현됐다는 의미는 아니다.
5. **detach 이후의 보존과 한계.** `product.py:1773–1858, 1882–1919`의 detach plan은 candidate null, expected binding ref와 제거할 inventory/launcher/binding의 digest를 가지며 receipt는 plan과 prior binding ref를 보존한다. 완전 제거 뒤 그 digest만으로 window literal을 역산할 수 없다. 다만 `workspace.py:291–312`와 `product.py:1058–1087`은 기존 root/detach prefix를 fresh init으로 인정하지 않는다. [Detached lifecycle 계약](../WORKSPACE-CONTRACT.md#receipt-bound-detach)과 [General Work](../GENERAL-WORK.md#detach-without-removing-project-truth)의 재초기화 금지는 Windows라는 label을 알아야만 집행되는 규칙이 아니다. successor의 exact detach schema/window pair와 허용 진단에서 필요한 정책 provenance는 수락 범위에 포함하며, 추론 불가는 unknown으로 남긴다. 별도 새 field나 외부 mode registry를 지금 채택하지 않는다.
6. **old writer와 native runtime.** `product.py:329–395, 969–1008`은 inventory/payload와 현재 entry-1 writer를 검증한다. `workspace.py:37–46`은 CPython version/final/GIL을 검사하며 OS/architecture를 검사하지 않는다. 이 확인은 모든 과거 writer의 거절 또는 미래 Windows runtime gate의 실행 증거가 아니다. exact source·installed·retained writer 조합을 고정하고 결과가 실패하면 activation을 막는다는 의무를 문서화하되 실제 qualification은 승인된 구현 뒤 수행한다.
7. **A1–A5 target.** Structure의 Content Trees And Manifests 마지막과 Exact Managed Membership 다음, General Work의 Worker Publication 끝·Git Integration 직전이 존재한다. Windows Admission ten-criteria 문장의 5번·8번 fragment가 제안의 교체 전 원문과 정확히 일치한다. 나머지 8개 criterion, criteria 6–9의 회귀·복구·inventory 및 두 autocrlf 의무, B 배정과 formal timing은 변경하지 않았다. 이것은 정적 대조이며 실제 normative 파일에 amendment를 적용한 결과가 아니다.

### Focused Case Disposition

| 사례 | Driver 결론 | 아직 필요한 것 |
| --- | --- | --- |
| tracked 삭제와 잔존 index | 실제 부재를 관측하는 의미는 일관됨 | 비부재/non-pass 명문, ancestor 및 특수 flag의 Windows 검증 |
| stable tracked·eligible untracked·add-644 | common condition과 기존 guard를 함께 적용 | 비열거 tracked add까지 문안·검증 사례를 일치시킴 |
| mode-change·새 untracked 755·mixed | operation 전체 사전 거절과 macOS 기존 동작 보존이 일관됨 | 실제 prepare/apply 발행 경계 검증 |
| drift·pending·ordinary reject·replay | 서로 다른 기존 의미를 유지 | exact 복구·취소·완료 replay의 구현 qualification |
| A1–A5 | 위치와 원 fragment 확인, 의미 방향 정합 | 범위·참조·S1 동시 수락 정리 |
| fresh/pre-binding | 기존 plan/token에 release/window 결속 확인 | successor 선택/profile과 실제 native runtime 검증 |
| detach·old writer | generic detach barrier와 policy diagnosis를 구분해야 함 | exact detach pair·진단 한계·거절 실패 분기 |
| admission/B | 5·8의 변경 제안과 6–9의 유지 의무가 일관됨 | 모든 나머지 named clause와 exact candidate qualification |

### Remaining Before Contract Acceptance

권고는 B를 유지하고 공통 조건 중심 지원 정의와 기존 release/binding shape 재사용을 계속 준비하는 것이다. 새 field, 닫힌 지원 목록 또는 additional probe를 자동 선택하지 않는다. full exact 계약 수락 전에 남는 것은 다음이다.

1. F1의 non-pass·ancestor 연결, F2의 조건 정의형 범위, F6/F7의 scope·참조를 A1–A5/S6에 일치시키고 exact 개정 bytes를 고정한다. 닫힌 목록을 선택하려면 그 축소를 Owner가 명시적으로 선택해야 한다.
2. Windows 전용 successor의 literal·ordered membership·lifecycle schema/window pairs·source/installed/retained reader-writer 집합을 고정한다. fresh 후보 선택과 profile/원 plan 결합, detach 이후 필요한 policy 진단의 한계를 함께 적는다. 현재 shape로 충분한 pre-binding chain과 아직 설계하지 않은 successor detach 표현을 혼동하지 않는다.
3. old-writer 거절 실패 시 candidate qualification/activation을 멈추는 처분과 필요한 최소 대안을 명시한다. native OS/process architecture·에뮬레이션 등 포함 범위를 S1/S2/S7에 맞춘다. 이는 지금 모든 조합의 실행을 요구하거나 B에 새 full-suite gate를 만드는 뜻이 아니다.
4. S1/S3–S5/S7–S8의 나머지 named amendment를 exact 문안으로 준비하고 최종 통합 baseline을 다시 대조한다. Owner가 전체 의미·범위·남은 exclusion을 exact revision으로 선택·수락해야 한다. 구현 방법의 모든 매개변수마다 별도 승인을 요구하지 않는다.

계약·계획 문서는 함께 구체화할 수 있다. 실제 old-writer refusal, Windows 삭제·mode·lifecycle, full regression과 환경 tuple 검증은 승인된 구현·qualification의 일이며 이번 정적 재리뷰의 완료 조건이 아니다. 계약 수락, 제품 실행 승인, 제품 결과 수락/activation, live macOS Preview 이후 Windows formal admission은 대상과 범위를 구별한다. 이번 요청은 리뷰·판단·기록에 한정하며 DR 자동 개정이나 그 다음 실행을 허용하지 않는다.

### Reviewer Final Response — Verbatim

````markdown
# R1-D04 — DR-0007 Draft 0.4 정적 재리뷰

**검토 범위:** 지정된 v0.4 한 문서(SHA-256 `3901b4c5…2ff`)를 정적으로 한 번 읽었다. 도구 실행, source·target 문서 열람, 실행 검증은 하지 않았다. 문서가 전하는 기존 계약과 source 사실은 보고된 주장으로만 다룬다. 이 리뷰는 Owner의 계약 수락을 대신하지 않는다.

## 1. Verdict

| 항목 | 판정 | 요지 |
| --- | --- | --- |
| 전체 exact 계약 수락 준비도 | **conditional** | 방향은 수락할 수 있다. 다만 아래 항목이 아직 없어서 full exact 수락은 아직 성립하지 않는다(L362, L438, L327).<br>• exact window literal, membership, schema/window pairs, reader-writer 집합<br>• S1, S3–S5, S7–S8의 exact clause<br>• 아래 F1–F4 |
| 삭제·worker 공통 조건 | **conditional** | index 불변, 독립 최종 관측, whole-result, 원기록 보존은 일관된다. 남은 것은 F1(부재가 아닌 관측의 결과 미규정)과 F2(예시 목록과 공통 조건의 관계)다. |
| A1–A5 내부 정합성 | **conditional** | S2/S6, impact, mapping과 의미 충돌은 없다. F1·F2의 문안 공백, F6·F7의 범위 표기를 보완해야 한다. |
| binding/profile 식별 설계 방향 | **conditional** (방향은 타당) | "window에 고정 정책을 묶고 runtime을 따로 검사"하는 논리는 새 writer에 대해 성립한다. 다음 세 가지가 미정이다.<br>• fresh init의 window 선택 근거와 binding 이전 identity 운반(F3)<br>• known old writer가 거절하지 않을 때의 대안(F4)<br>• runtime 범위(F5) |
| 문서 기반 계획 준비 | **approve** | 계약 의미와 계획 메커니즘의 분리, 순환 회피(L472)가 명확하다. 계획 문서 작성에 장애는 없다. |

P1은 없다.

## 2. Must-fix 및 선택적 보완

### D04-F1 · P2 · 부재가 아닌 관측의 결과가 규정되지 않음

**위치:** L218, A1 L369. 같은 경계가 A2 L385의 재관측에도 이어진다.

**문제:**
- A1은 "only safely observed regular files"만 snapshot에 넣는다고 하면서, alias·type·reparse·inaccessible은 "not absence"라고만 쓴다.
- 이 경로가 어떤 결과가 되는지(거절 또는 non-pass)는 special index state에만 적혀 있다.

**반례:** tracked `tools/run.ps1`이 directory나 junction으로 바뀌었다고 하자.
- 문언대로 구현하면 regular file이 아니므로 TreeEntry가 없다.
- 그 결과 tree digest는 삭제와 같아지고, Work가 삭제를 기록하는 오해가 생긴다.
- worker 최종 관측에서도 tracked 삭제 결과가 "부재"로 통과할 수 있다.

**인접 공백:** S3(L152)는 ancestor chain 검사를 요구하지만, A1의 "confirmed absent"는 그 chain에 묶여 있지 않다. 예를 들어 parent가 reparse이거나 file로 바뀌어 ENOTDIR가 나는 경우가 이에 해당한다.

**최소 수정** (A1 L369 끝, S6 L218에 같은 의미로):
> Such a path makes the observation non-pass for the affected operation; it is neither omitted from the snapshot nor recorded as a deletion. Absence counts only when the exact path and its examined ancestors are observed under the path-observation rules.

### D04-F2 · P2 · 지원 집합이 "공통 조건으로 판정"인지 "닫힌 목록"인지 불일치

**위치:**
- S6 L246, L257: 표에 없는 결과는 공통 조건과 기존 검증으로 판정한다.
- A2 L387: "initial qualification covers …" 목록만 있고 L257에 해당하는 문장이 없다.
- A3 L405: 그 목록만 검증한다.

**반례:**
- control index에 stage-0 `100755` entry P가 있다(staged 후 파일 삭제, 반영 전 commit). base와 control snapshot에는 P가 없어 baseline이 일치한다.
- worker result가 P를 `100755`로 add한다.
- 공통 조건은 충족한다(예측 mode가 index의 755). 그러나 A2 목록(tracked content 변경, new untracked)에는 없다.
- S6로는 지원, A2/A3로는 미검증, A4로는 설명 대상이 아니다. 결과적으로 criterion 8이 "unqualified 지원"을 노출하거나, 반대로 구현자가 거절하는 해석 분기가 생긴다.

**최소 수정 (Owner 선택):**
- **(a) 권고:** 최초 지원 = 열거 범주 ∩ 공통 조건 ∩ 기존 검증. 그 밖의 결과는 발행 전 unsupported로 거절한다.
  - A2에 추가: "Results outside these categories are initially refused as unsupported even when the condition holds."
  - S6 L257을 이에 맞춘다.
- **(b) 조건 정의형:** A2에 L257 문장을 옮긴다. A3에 index-only tracked path add 같은 대표 사례를 추가한다.

어느 쪽이든 예시 목록이 충분조건이 아니라는 점은 이미 A2 "Subject to all those checks"(L387)로 보장된다.

### D04-F3 · P2 · fresh init의 window 선택과 binding 이전·detach 이후 identity chain

**위치:** L319, A5 L433, L133.

**문제 1 — 선택 근거:** binding 이전에는 "candidate release와 원 request/plan"이 정책을 식별한다고 했다. 그런데 source init이 Windows에서 어떤 근거로 successor candidate를 고르는지는 정하지 않았다. 후보는 host 자동, 새 profile 값, 명시 request 필드다. CLI profile·OS 단독은 증명이 아니라고 했으므로 선택과 검증의 결합 규칙이 필요하다.

**문제 2 — persisted identity:**
- 중단된 init의 exact recovery가 같은 window에 묶이려면, canonical request/plan(token digest의 입력)이 candidate의 `inventory_id`나 release identity를 포함해야 한다.
- 이 사실은 source 확인이 필요하다(조건부).
- 포함하지 않는다면 "기존 shape로 충분"이라는 결론이 pre-binding 구간에서 깨진다. 이것은 구현 세부가 아니라 persisted 의미다.

**문제 3 — detach 이후:** L133은 "detach/reinstall 우회 금지"를 말한다. 하지만 receipt-bound detach 뒤에 Windows window였다는 흔적이 어디에 남는지가 없어 규칙의 집행 가능성을 판단할 수 없다.

**최소 수정:** S2와 A5에 다음을 명시한다.
- native Windows fresh init은 designated successor만 대상으로 삼고 다른 window candidate를 거절한다.
- 필요한 profile 값을 정한다.
- 원 request/plan이 candidate window를 포함하는지 source로 확인하고, 아니라면 S2 수락 대상인 persisted 변경으로 제시한다.
- detach 이후 window identity를 어디서 읽는지(또는 집행 범위의 한계)를 적는다.

### D04-F4 · P2 · known old writer가 거절하지 않을 때의 처분이 없음

**위치:** L141, L321, L323, A5 L435.

**문제:**
- 문서는 unknown-window guard만으로 거절을 단정하지 않는다. 이 점은 정확하다.
- 그러나 확인 결과 거절하지 않는 경우의 결론이 "미지원" 표기(L141)로만 남아 있다.
- 기존 writer는 바꿀 수 없으므로 표기만으로는 실제 오염을 막지 못한다.

**반례:** 현재 source나 기존 release의 Work, intent, worker 경로 중 일부가 binding 단계에서만 window를 확인하고 project record 쓰기에서는 확인하지 않는다면(source 조건부), new window 값만으로는 successor record에 대한 기존 writer의 쓰기를 막을 수 없다.

**새 field나 format 변경이 실제로 필요한 경우:** 바로 이런 경우다. 기존 reader가 거절하는 format/schema 표지가 필요해진다.

**최소 수정** (L321, A5에):
> If a known cooperating old writer would publish authority or content into the successor without refusal, the existing record shapes are insufficient; a format change that old readers reject, or a reasoned non-exposure argument, is required before acceptance. A residual-risk label alone does not satisfy this.

L148의 "잔여 위험 표기만으로 통과시키지 않는다"를 이 분기에 연결하면 된다.

### D04-F5 · P3 · "native Windows and allowed CPython runtime"의 범위가 S1 tuple에 연결되지 않음

**위치:** A5 L433, L319 ↔ S1 L121.

**문제:** `runtime_supported`는 버전만 검사한다(L310). 그래서 다음 조합이 "native Windows"로 통과할 수 있다.
- ARM64 위 x64 에뮬레이션 CPython
- x64 위 32-bit CPython. S4가 pointer width를 qualification 대상으로 둔 것과 충돌한다.
- MSYS·Cygwin Python

**최소 수정:** 정책 대상 OS·process architecture와 에뮬레이션·32-bit 허용 여부를 Owner 선택으로 명시한다. 검사 방법은 계획으로 넘긴다.

### D04-F6 · P3 · A1 2–3단락의 적용 범위가 단락 단위로 표시되지 않음

**위치:** L371, L373.

**문제:**
- 첫 단락만 "For the designated Windows successor"로 시작한다.
- 2단락("logical mode comes from the validated index", 100644 default)과 3단락(non-Git 755 제한)은 일반 절 끝에 붙으므로 단독으로 읽으면 macOS에도 적용된다.
- 마지막 문장이 이를 해소하지만, normative 문서에서는 하위 heading이 안전하다.

**최소 수정:** `#### Windows Successor Content Observation` heading을 두거나 각 단락 앞에 범위를 반복한다.

같은 맥락에서 A2 L383의 "The control HEAD, index and refs remain unchanged"는 동시 변경 금지 invariant로 오독될 수 있다. "The operation does not change…"로 바꾸는 편이 낫다.

### D04-F7 · P3 · A3 문언의 참조와 용어

**위치:** L399, L405, L407.

- **용어:** "initial mode/application contract"를 A1과 A2 heading으로 정확히 참조한다.
- **약어:** A3의 "add-100644"는 A2의 "new untracked 100644"와 같은 범주로 맞춘다. F2와도 관련이 있다.
- **허공 참조:** L407의 "approved representative-UTM/full-suite and focused-follow-up allocation"은 S1의 exact amendment가 아직 없으므로(L106, L438) target 문서 안에서 참조 대상이 없을 수 있다. "the allocation accepted under DR-0007 S1"로 바꾸거나 S1 문안과 동시에 수락하도록 묶는다.

### D04-F8 · P3 (source 조건부) · "eligible existing untracked 100644" 범주의 도달 가능성

**위치:** L251, L387, L405.

**문제:**
- worker base가 retained Git commit이라면, control의 untracked 파일이 base에 들어가 이 범주가 기존 자격상 성립하는지 불확실하다.
- 성립하지 않는다면 criterion 5의 필수 검증 대상이 비게 되고, "N/A→PASS" 오해가 생길 수 있다.

**최소 수정:** Driver가 source로 도달 가능성을 확인한다. 도달할 수 없다면 목록에서 빼고, 해당 결과가 기존 자격 검사로 거절된다는 사실을 검증 대상으로 둔다.

## 3. Focused Cases

| # | 이미 정합한 의미 (근거 줄) | 남은 계약 선택 / 구현·검증 |
| --- | --- | --- |
| 1 | index는 후보, 부재는 별도 관측. 잔존 entry ≠ 존재. special flag는 unknown. S6 L218 = A1 L369 = A2 L385 = A3 L405 | 부재가 아닌 관측의 결과(non-pass, 누락 금지)와 ancestor chain 연결(F1). 특수 flag 분류는 계획 |
| 2 | 공통 조건은 "추가 필요조건"이며 기존 guard를 대체하지 않는다(L244, A2 L383/L387, A3 L405). 예시는 충분조건이 아니다 | 닫힌 목록인지 조건 정의형인지(F2). untracked 644 범주 도달성(F8) |
| 3 | mode-only, bytes+mode, 새 untracked 755(rename 포함), mixed는 prepare에서 ticket 미발급, apply에서 발행 전 전체 거절(L254–261, A2 L387–389). index 불변·독립 최종 관측과 충돌 없음. L259 반례 설명 정확. zero-write 미주장 | apply 검사 이후 index drift는 기존 pending 규칙을 따르며 index 안정성은 계획(L269 이하) |
| 4 | drift/stale ≠ 정책 unsupported ≠ unknown(L263, A2 L389). pending 보존, cancellation 경계 유지(A2 L391). ordinary reject·review submission 비차단(L265). completed replay에 새 gate 없음(A1 L373). read 계열은 non-pass 보고일 뿐 mutation이 아님 | 구체 오류 매핑은 계획. pending 중 drift 시 사용자의 index 복원 외 탈출 경로가 없는 것은 기존 계약의 결과(새 경로를 만들지 않음이 정합) |
| 5 | A1–A5의 의미는 S2/S6, Impact(L347–354), Mapping(L450–454)과 일치. A3/A4는 fragment 교체, 나머지 순서 유지 | 범위 표기와 참조(F6·F7). target heading·anchor·원 fragment 일치는 미검증 |
| 6 | entry-1/profile 불충분 논증(L303–314) 타당. Binding→ReleaseRef→Inventory→payload 재사용 + 독립 runtime 검사는 새 writer에 대해 충분 | fresh init 선택 근거, request/plan의 window 포함, detach 이후(F3). runtime 범위(F5) |
| 7 | 방향 권고와 exact 수락 구분(L327, L362 "고정 전 수락 미완료"). unknown-window guard만으로 단정하지 않음(L321, A5) | 거절 실패 시 format 변경 분기(F4). 새 field가 필요한 경우: 한 window 내 OS별 정책(L323 명시), old writer 미거절(F4), 권한 bit를 대체할 publication 표지(L201) |
| 8 | criteria 5/8 교체와 6–9 유지, autocrlf 두 설정, macOS 성공 기대 유지, skip→PASS 금지(A3 L407, L451–454). B 배정과 정식 timing 유지(L358, L483) | S1 exact 문안이 없어 L407 참조가 허공에 뜸(F7) |

## 4. 계약 수락 전 남는 항목

### Owner 선택 및 문서 보완 (수락 전 필수)

1. Windows 전용 successor라는 의미를 선택하고, exact window literal, ordered membership, schema/window pairs, source·installed·retained reader-writer 집합을 고정한다.
2. fresh init의 window 선택 규칙, profile 값, request/plan의 window 운반, detach 이후 identity(F3).
3. old writer 미거절 시 처분: format 변경 또는 비노출 논증(F4).
4. worker 최초 지원 집합의 성격: 닫힌 목록 또는 조건 정의(F2).
5. runtime 정책 범위: OS·process architecture, 에뮬레이션, 32-bit(F5).
6. F1 문안 보완과 F6·F7 표기 정리.
7. S1(timing, native 해석), S3–S5, S7–S8의 exact clause 작성. L438이 스스로 인정한 미비다.
8. 이번 R1-D04의 처분 기록과 v0.4(또는 개정판) identity 갱신. L36과 L492의 "재리뷰 없음"을 현재 상태로 갱신한다.

### 구현·qualification 세부 (계획에서 고정)

- index와 특수 flag의 분류 및 안정성 검사
- alias 비교, 검사 순서, physical occupant와 snapshot 일치
- 발행 predicate와 거절 위치, 오류 매핑, 알림 단위
- native OS/runtime 검사의 방법과 위치
- old-writer 거절, fresh/same-window, worker pair의 실제 확인
- criterion 5의 drift 시나리오와 삭제 부재 검증
- full regression의 budget과 ledger

## 5. 해결됐거나 반례가 없는 부분, 한계

### 해결 또는 반례 없음 (v0.4 설명 범위 기준)

- **R3-F1:** 삭제 관측. F1의 잔여 공백은 있다.
- **R3-F2:** 공통 필요조건과 기존 의무 유지.
- **R3-F3·F4:** drift/unsupported/unknown 구별, ordinary reject와 cancellation 구별(L263, L265).
- **R3-F5:** 상태 표시(L36).
- **기타 원칙:**
  - index 자동 변경, registry/sidecar, manifest fallback, 새 명령을 도입하지 않는다(L267, A2 L391).
  - macOS worker mode 계약을 축소하지 않는다.
  - 과거 기록과 원참조를 보존한다(A1 L373).
  - 새 full matrix나 물리 gate를 전제하지 않는다.
  - "designated Windows successor"가 runtime wildcard가 아니라는 경계(L362)가 있다.

### 읽지 못한 근거와 잔여 한계

다음은 독립 검증하지 않았으며, 일부 판단은 이에 따라 조건부다(F3·F4·F8).

- source(`product.py`, `cli.py`, `workspace.py`)
- target 문서의 실제 heading, anchor, A3/A4 원문 fragment, A2의 기존 문단 위치와 heading level
- DR-0002/0003/0004 원문, 이전 리뷰와 probe 원출력
- worker base 구성
- request digest 입력
- detach 이후 남는 기록
- 기존 writer의 window 확인 지점

A1–A5의 실제 target 적용성은 검증했다고 주장하지 않는다.
````

### Record Verification And Retention

검토한 DR의 exact bytes와 이전 review 원문은 보존한다. 이번 최종 원문과 Driver 처분은 이 record에 함께 유지하며, frozen packet/request/input identity/minimal metadata/invocation은 Owner 처분과 다음 exact 비교를 위해 기존 private task 경로에 보존한다. 중복 partial·빈 stderr·tool-temp 및 일회성 문서 검사 출력은 통합 검증과 사용 종료 확인 뒤 정리한다. 기존 worktree·VM·probe 원출력·마지막 복구본은 앞서 기록한 결과 수락·설정 복원·후속 비교의 consumer와 종료 조건이 남아 있으므로 유지한다. 새 registry나 전체 source backup을 만들지 않는다. Active path 이동·제품 변경·VM 작업·Git publication은 없다.

최종 문서 검증은 PASS다: marked 17.0.5 GFM으로 현재 문서 3개와 local path/heading link 56개를 확인했다. code 밖 literal 강조 기호·whitespace·disclosure 문제는 없었다. DR v0.4 unchanged, packet에서 exact 원문 복구, 8개 선택·10개 admission 항목·비어 있는 accepted-only 절, 기존 R0/R1-P01/R1-D01–D04 원문과 frozen 입력, 이번 추가 전 CHORE bytes, 다른 고정 source 입력·HEAD·tracked diff 보존을 확인했다. 제품 실행 검증은 아니다.

정리도 완료했다. Reviewer 종료·partial/final 동일·빈 stderr/tool-temp·lsof 사용 없음 확인 뒤 중복 partial, 빈 stderr와 tool-temp, 일회성 checker/report 5개 대상을 제거했다. 필요한 review 파일 6개와 source 기록은 보존했다. Active path는 바뀌지 않았다. 기존 worktree·VM·probe raw·마지막 복구본은 결과 수락·복원·후속 비교의 기존 소비자가 남아 있어 유지한다. 정리 후 최종 기록을 다시 렌더링·검사했으며 재현 가능한 report를 다시 남기지 않았다.


## Contract Draft Revision 0.5 — 2026-10-18

Owner는 R1-D04와 Driver 권고를 반영한 v0.5 문서 보완을 요청했다. 공통 조건 중심 worker 지원과 B를 유지하고, 삭제 관측·detach 이후 식별·old-writer 거절 실패 처분·남은 exact 문안을 구체화했다. 변경은 DR와 이 진행 기록에 한정하며 normative 계약·admission·제품 source·STATUS/catalog는 수정하지 않았다.

DR-0007 Draft 0.5는 122770 bytes, SHA-256 `d5f407c0710f5d215a29c9851e67b85271b21def0e7dbc8716c208f18afcb7ee`다. 이전 v0.4 exact bytes는 R1-D04 frozen packet에서 복구할 수 있다. 앞선 review 원문과 당시 판단은 그대로 보존한다.

A1–A5를 공통 조건·비부재 non-pass·tracked index-only add·eligible untracked에 맞췄고 A6–A15에 S1–S8의 나머지 named 문안을 추가했다. windows-1 window/profile·기존 29-member 경로·init1/switch2/repair1/detach4를 구체 후보로 제시했다. detach4는 기존 field set을 유지하면서 inventory 삭제 뒤 window 정책을 구별하기 위한 새 persisted 의미다. 과거 detach1/2/3은 변환하지 않는다. 이것은 계약 수락·구현·검증 PASS가 아니다.

old writer가 실제 authority/content를 발행하면 candidate qualification/activation을 멈추고 최소 유효 거절 장치 또는 검증 가능한 비노출 근거를 선택하도록 했다. native runtime의 OS/process architecture 범위를 명시하되 B의 대표 UTM full·x64/물리 focused 배정과 formal timing은 보존했다. 미래 artifact digest·실행 결과는 만들어 넣지 않았으며 source/installed/retained 조합은 실제 qualification 입력과 구별했다.

문서 입력과 bounded diff는 기존 private task의 contract-draft-05에 보존해 Owner 비교/다음 exact 리뷰에 사용한다. 일회성 작성·검사 파일은 결과 검증과 사용 종료 확인 뒤 정리한다. 기존 worktree·VM·probe raw·마지막 복구본은 결과 수락·복원·후속 비교의 기존 소비자 때문에 유지한다. 새 리뷰·실험·제품 실행·VM 작업·계약 발효·Git publication은 수행하지 않았다.

검증 완료: GFM(marked 17.0.5)으로 변경 문서 3개를 렌더링하고 code 밖 literal 강조 기호 없음·로컬 경로/heading 링크 69개·whitespace/disclosure를 확인했다. A1–A15를 메모리상의 대상 문서 11개에만 적용해 삽입/교체 위치와 렌더링을 검증했다. 실제 normative 파일은 변경하지 않았다. 제안한 29-member 목록은 product source의 ENTRY_MANAGED_PATHS를 import 없이 AST로 읽은 목록과 일치한다. 이는 제안 membership 정합성 검사이며 제품 실행 증거가 아니다.

입력 30개 중 허용된 DR/진행 기록/append-only private task 기록 외 bytes는 유지됐다. B/S1 등 보호 구간 11개, 8개 선택·10개 admission 대응·비어 있는 수락 전용 절, R0/R1-P01/R1-D01–D04의 frozen packet·request·최종 원문, v0.4 exact 복구와 bounded diff를 확인했다. source HEAD와 기존 navigation diff도 유지됐다. 기존 문구와 Windows 전용 override의 적용 범위를 명확히 했으며 제품 suite·VM·reviewer는 실행하지 않았다.

정리 완료: 이번 revision의 일회성 작성 데이터·적용 script·검사기·중간 report 4개는 검증 결과를 이 기록에 보존하고 사용 프로세스가 없음을 확인한 뒤 삭제했다. revision 입력과 diff는 Owner 비교/다음 exact 리뷰를 위해 유지한다. 활성 경로 변경은 없으며 기존 리뷰·probe·마지막 복구본은 그대로 보존했다. 정리 뒤 같은 검증을 메모리에서 다시 수행해 통과했다.


## R1-D05 Draft 0.5 Re-review And Driver Judgment — 2026-10-18

### Authorization And Fixed Input

Owner는 “DR-0007 v0.5를 Claude CLI로 재리뷰해줘. 공통 조건 중심 worker 지원, windows-1·detach4 식별, old writer 실패 처분과 A1–A15의 일관성을 확인하고 네 판단도 정리해줘. B안은 유지하고 추가 실험이나 제품 구현은 시작하지 마.”라고 요청했다. 이번 작업은 고정 문서의 정적 리뷰 1회, Driver의 로컬 source/계약 대조와 이 진행 기록 갱신이다. 아래 accept/revise는 후속 문안에 대한 권고이며 DR 개정·계약 수락·제품 실행 승인이 아니다.

| 항목 | 실제 입력·결과 |
| --- | --- |
| 대상 | DR-0007 Draft 0.5, 122,770 bytes, SHA-256 `d5f407c0710f5d215a29c9851e67b85271b21def0e7dbc8716c208f18afcb7ee` |
| Source base | `a93f71c359c4f0a9d57fcfb50d5999160e870f77`; DR는 tracked diff 밖의 untracked 입력 |
| Existing tracked diff | SHA-256 `91f501b2077cfc175ae80edbddd2f56a32b71c2bcb6c6b7c1659d01c3e42a7ef`; 기존 Development Index navigation만 포함 |
| Frozen packet | 126,993 bytes, SHA-256 `b291da430199a47ffd1bc3d208e423a0685504099b3d62e5478d4cd4f63501e0`; 줄 번호를 제거하고 마지막 newline을 복원하면 대상 exact bytes를 복구 |
| Request / transmitted input | Request SHA-256 `d2655807ddf4b0bf0b3c12f701f7eb6caaf2bc4e235add418e73e5e2bbb9175f`; 전체 stdin SHA-256 `e8d93238a3eb1c58f34b3817c3fe11b928ddabd9d15eae569f4a10135a9bd3e7` |
| 실제 Reviewer | Claude CLI 2.1.302, model `claude-opus-5-5`, fresh session `f4c9748e-72ac-4d9d-b75a-cfc3ae2f16b7`; model override 없음 |
| 인증·과금 경로 | `claude.ai` / `firstParty` / `pro`; provider override 없음. secret·계정 이메일을 기록하지 않음 |
| 제한 | `--safe-mode --print`, tools 없음, empty strict MCP, slash commands·Chrome·session persistence 비활성, permission `dontAsk` / prompts `none`; 도구 event 0 |
| 실행 | 2026-10-17 22:06:58–22:10:12 UTC, 193.649초, 상한 1,200초, exit 0, 1 turn |
| Final response | 14,265 bytes, SHA-256 `f7e54388cf3ed00ad4f58d2861580942f9579178b2da33283aaa24a702d5bac7` |
| 전후 확인 | 대상 입력 1개·source HEAD·기존 tracked diff 동일, input drift 없음 |

Reviewer에게 전달한 문서는 v0.5 한 개뿐이다. 공통 조건 worker·삭제·drift/replay, pre-binding·installed identity, detach4 제거 전/중/후, old-writer 실패/미확인, A1–A15와 기존 의미, B·runtime·admission의 8사례를 요청했다. linked target 문서·제품 code·이전 리뷰 원문·probe raw는 전달하지 않았다. fresh session과 다른 모델은 컨텍스트 공유를 줄이지만, Driver 작성 packet만 읽은 정적 리뷰라는 한계를 없애지는 않는다. Reviewer가 실행·source 대조·렌더링·hash 재계산을 했다고 보고하지 않는다.

### R1-D05 Verdict And Driver Assessment

| 대상 | Reviewer | Driver 판단 |
| --- | --- | --- |
| 전체 exact 계약 수락 준비도 | conditional | 동의. core 방향은 유지하되 F1–F3의 최소 문안과 아래 exact-repair mode 연결을 먼저 고정 |
| 공통 조건 worker | approve | 동의. 기존 모든 guard와의 교집합이며 예시는 비폐쇄 목록. fixture 실행·지원 qualification을 통과했다는 의미는 아님 |
| windows-1 / detach4 식별 | conditional | 방향 유지. 기존 remove/preserve path 목록이 실제 있으므로 새 field 필요성의 조건부 전제는 성립하지 않음. 제거 뒤 검증 대상을 더 분명히 명시 |
| old-writer 실패 처분 | conditional | 발행 확인 시 중단 의미는 충분. 노출된 known writer의 거절 미확인도 완료 처리할 수 없다는 기존 의무를 A5/A13에 직접 연결 |
| A1–A15 내부 정합성 | conditional | 실제 닫힌 entry-1/current-schema 문장이 존재. Windows override 대상과 repair의 persisted mode 의미를 좁게 지정할 필요 |
| 문서 기반 계획 준비 | approve | 동의. 계약 문안과 계획을 함께 준비할 수 있으나 추가 실행 권한은 없음 |

Claude finding은 P1 0건, P2 3건, P3 7건이다. 이것은 재현된 제품 bug 수가 아니다. F2/F3/F9에 포함된 source 전제는 아래 Driver 정적 대조로 각각 좁혔다. Driver가 발견한 D05-D1은 별도의 P2 문서 의미 보완사항이며 Claude가 지적하거나 재현한 것으로 합산하지 않는다. Reviewer 원문의 “normative인 A5/A13”은 수락 후 대상이 될 exact 제안 문안이라는 뜻으로만 읽는다. 현재 A1–A15는 Draft이며 효력이 없다.

### R1-D05 Finding Dispositions

| Finding | 처분 | Driver 판단과 후속 문안 권고 |
| --- | --- | --- |
| D05-F1 · P2 · 미검증 known old writer | revise | A5의 “Known cooperating old writers must refuse”와 A13의 검증 의무, Promotion의 missing qualification non-pass는 이미 미확인 PASS를 허용하지 않는다. 다만 해당 대상에 노출되는 known writer의 거절을 확인하지 못했으면 candidate qualification/activation을 완료하지 못한다는 문장을 A5/A13에 직접 넣는 편이 명확하다. 실제 노출 조합과 근거 있는 비노출 처분을 연결하되 모든 역사적 writer의 회수를 무조건 요구하는 새 전수 gate로 확대하지 않음 |
| D05-F2 · P2 · 제거 뒤 detach4 검증 | revise | source와 Structure에 `remove`/`preserve`의 path·sha256·size 목록과 전체 plan을 담은 receipt가 이미 있다. “목록이 없으면 새 field 필요”라는 조건부 우려는 현행 shape에는 해당하지 않는다. A8/A9에 기존 검증을 풀어 적는다. 제거목록 전체가 29개라는 뜻은 아니며 launcher·init plan·binding·각 receipt·각 release inventory와 그 release의 29 payload paths로 확장한 집합을 비교한다. 남은 bytes·directory/prefix, 실제 제거 경로의 부재, 보존 bytes를 독립 관측하며 삭제된 payload를 현재 다시 hash했다고 주장하지 않음 |
| D05-F3 · P2 · 닫힌 현재형 문장과 override | accept | 실제 Workspace의 profile/repair/planning, Structure의 Window·pair·current-writer 목록, Reference의 source profile/window/schema 문장이 존재한다. A8/A9/A12에서 바꾸는 named clause를 명시하고 windows-1에만 우선하는 qualifier를 둔다. Security A10은 runtime/CRLF의 Windows 추가 의미를 이미 명시하므로 같은 boilerplate를 무조건 추가하지 않고 실제 남은 충돌만 한정한다 |
| D05-F4 · P3 · CRLF retains/extends | accept | A9도 windows-1로 “extends”한다는 표현으로 통일할 수 있다. 현재 Draft 맥락이 기존 Windows 지원을 주장한 것은 아니므로 기존 qualification 오표시로 판정하지 않음 |
| D05-F5 · P3 · 관측 규칙 참조 | accept | A1에서 Workspace의 Windows Native Observation And Publication을 정확한 이름으로 지정. 새 정책이나 추가 문서 gate가 아니라 찾기 쉬운 참조 보완 |
| D05-F6 · P3 · index-only add 문구 | accept | “exact base와 실제 control namespace 모두에 부재”로 명시. existing exact-baseline·physical guard 때문에 이미 두 관측이 필요하나 한 문장으로 연결하면 오독이 줄어듦 |
| D05-F7 · P3 · schema4의 미래 재사용 | defend | A9는 이미 “that version admits no other window or membership”이라고 고정하며 같은 window 안의 의미 변경도 금지한다. 다른 window가 schema4를 재사용해도 된다는 허용은 없다. 예약 표현을 더할 수는 있으나 별도 미결 선택이나 신규 version 정책을 요구할 근거는 없음 |
| D05-F8 · P3 · runtime/standard-user | revise | CPython 범위는 Security runtime clause를 공통 참조하고 exact revision의 두 값이 일치하도록 한다. standard-user는 B의 지원·admission/qualification 환경 조건으로 유지하고, actual OS/process gate와 구별해 설명하는 안을 권고한다. 이를 새로운 매 writer 권한 검사로 자동 승격하거나 elevated 실행을 qualified로 인정하지 않는다. 이 구분은 다음 exact 문안에서 드러내고 Owner의 계약 수락 범위에 포함 |
| D05-F9 · P3 · detach profile 인자 | defend | `cli.py:81–93,111–117`에서 source detach가 이미 `--profile`을 받고 source dispatcher가 명시 profile을 요구한다. repair에는 profile이 없으며 A11이 별도로 구분했다. windows-1 값을 추가하는 후보 의미와 기존 option 재사용은 다르다. 현재 조건부 반례는 성립하지 않아 A11을 불명확한 조건부 문장으로 되돌리지 않음 |
| D05-F10 · P3 · old-window mutation 의미 | revise | 주체를 나누어 설명한다. 새 windows-1 경로는 old target mutation/이주를 거절하는 제안이고, 기존 entry-1 source에 새 OS gate를 소급 설치한다는 뜻은 아니다. old writer가 windows-1 target에 접근하는 문제는 F1의 별도 거절/비노출 qualification 대상이다. 기존 macOS/default 보존과 연결하며 old window 전반을 수정하는 새 작업을 만들지 않음 |

### Driver Source And Contract Cross-checks

아래는 baseline의 직접 읽기 결과이며 제품 import·실행·재현이 아니다.

- [Structure — Plans, Bindings And Receipts](CHECKOUT-1-STRUCTURE.md#plans-bindings-and-receipts)에서 `remove`/`preserve`는 `InventoryEntry` 배열이고 receipt는 complete plan을 보존한다. [Detach Plan And Receipt](CHECKOUT-1-STRUCTURE.md#detach-plan-and-receipt)는 launcher·metadata·각 retained release의 실제 membership, truth 기반 보존 집합과 exact removal prefix를 규정한다. `product.py:1760–1826`의 `_detach_entries`/`_detach_plan_shape`, `1829–1838`의 receipt/order, `1882–1920`의 관측이 이 구조와 대응한다.
- 제거 뒤 새 schema4 reader가 확인할 것은 원 canonical plan/receipt의 pair·operation/home/target·binding ref·집합 내부 digest 관계, Windows 전용 fixed membership으로 확장한 remove set, truth/format/ignore preserve set, 남은 파일 bytes와 제거 suffix·directory prefix다. 이미 제거된 inventory/payload의 bytes를 digest만으로 복원하거나 현재 다시 검증할 수는 없다. 기존 trusted-local/cooperating-writer 경계 아래 제거 전에 결속한 원 plan에 의존한다. namespace 부재는 A7의 안전한 관측을 따라야 한다. 이것을 “29개 목록을 자기 자신과 비교”하거나 version만 보고 PASS하는 규칙으로 바꾸지 않는다.
- [Workspace — Actual Init And Recovery](../WORKSPACE-CONTRACT.md#actual-init-and-recovery-development)의 source-profile/repair 문장(`134`), [Planning Preservation](../WORKSPACE-CONTRACT.md#planning-preservation)의 current-writer(`289`), [Structure — Common Types](CHECKOUT-1-STRUCTURE.md#common-types-and-exact-bytes)의 Window(`28`), plans/receipt/current-writer/detach(`359–390`), [Reference — Source Utilities](../REFERENCE.md#source-utilities)와 [Checkout Compatibility Limits](../REFERENCE.md#checkout-compatibility-limits)(`95–113`)에 실제 닫힌 현재형이 있다. 이 위치가 F3의 구체 보완 범위다. 문서 위치·렌더링 검증 성공이 이런 의미상의 override 완결성을 증명하지는 않는다.
- [Security — Runtime And Scope](../SECURITY-AND-SUPPORT.md#runtime-and-scope)의 기존 OS-neutral gate(`9`)와 CRLF exception(`30`)은 A10이 Windows 추가 의미를 이미 밝힌 대상이다. 버전·standard-user·native architecture의 역할을 명확히 하되 기존 window를 소급 해석하지 않는다.
- `cli.py:81–93,111–117`의 source detach profile과 `69–79,109–110`의 profile 없는 repair를 확인했다. parser 실행은 하지 않았다.
- `work.py:213–265,1045–1081,1387–1449`에 baseline equality·retained source·linked worker·physical occupant·whole-result와 decision-before-content/selection-before-current 경계가 존재한다. 공통 mode 조건은 여기에 더해질 제안이다. index-only tracked add와 eligible untracked 예시는 모든 guard가 만족한다는 조건이 붙은 정적 사례로 유지한다. 새 Windows 성공 fixture를 실행하거나 도달 가능성을 실험으로 입증하지 않았다.

### D05-D1 — Exact Repair Mode Meaning Needs A Named Windows Clause

Driver 정적 보완사항, P2. [Structure — Exact Repair Request](CHECKOUT-1-STRUCTURE.md#exact-repair-request)는 `FileObservation.mode`를 정수로 저장하고 launcher after mode를 `0755`, 다른 파일은 이전 mode 또는 missing default `0644`로 정한다. `product.py:1558–1563`은 실제 stat mode를 관측하고, `1608–1612,1658–1664`는 위 after 값과 exact before/after 비교를 사용한다. `1723–1729`의 completed repair replay도 실제 observation과 after의 일치를 요구한다.

v0.5 S6/A7은 managed Windows stat mode를 무결성·완료의 대용 근거로 쓰지 않도록 하며, A8/A9는 repair plan/receipt 1과 기존 shape를 재사용한다. 그러나 `RepairFile.before/after.mode`를 Windows에서 어떻게 관측·기록·예측·비교할지와 기존 `0755` 목표의 한정 문안은 A1–A15에 직접 없다. 이는 TreeEntry의 100644/100755 정책과 별개의 persisted observation 의미다. 현행 코드의 mode 비교를 그대로 유지하는 해석과, 그 필드의 의미를 임의 숫자로 바꾸거나 무시하는 해석을 모두 막아야 한다. Windows에서 실제 repair가 실패했다고 재현한 것은 아니다.

권고는 schema 1을 곧바로 폐기하거나 새 field를 추가하는 것이 아니다. Windows-only Exact Repair Request 보완에서 mode의 출처와 before/after 일치 기준, 실제 bytes/prefix 기반 완료, drift·backup·replay 보존을 함께 고정한다. 변경된 필드 의미는 `candidate_release.inventory_id=windows-1`에 묶어 기존 window의 원기록을 재해석하지 않는다. 선택한 방식이 shape 변경이나 새 durable 표식을 필요로 하면 그 부분을 exact 수락 대상으로 제시한다. API/값의 실제 실현 가능성과 interrupted prefix 검증은 그 뒤 qualification에 속한다. F3의 문구 정합성 보완에 이 named clause를 함께 연결하는 것이 최소 후속 범위다.

### R1-D05 Remaining Before Contract Acceptance

핵심 권고는 B·공통 조건 중심 worker·windows-1 전용 의미·기존 binding/plan shape와 detach4 방향을 유지하는 것이다. 닫힌 worker 사례 목록이나 추가 실험, 새 field, 다른 full matrix를 지금 도입할 근거는 없다.

계약 수락 전 문서 보완은 (1) exposed known old writer의 거절 미확인 처분을 A5/A13에 연결, (2) detach4 제거 뒤 무엇을 대조하는지 exact 집합·관측·과거 결속으로 구분, (3) 기존 entry-1/current-schema 문장에 대한 Windows 우선 적용 범위 지정, (4) Windows exact-repair mode의 persisted 의미 명시다. standard-user는 지원/qualification 환경 조건으로 유지하는 권고를 문안에 드러내고 actual OS/process gate와 분리해 Owner가 exact 범위를 수락할 수 있게 한다. 작은 참조·표현 보완은 같은 문서 개정에 묶을 수 있다.

실제 reader/writer artifact 고정·old-writer refusal/비노출 근거·detach prefix·repair/lock/flush/replace·PowerShell 입력·autocrlf·normal/parent-optimized/macOS 검증과 x64/물리 focused 보완은 구현·qualification에서 필요한 증거다. 미래 artifact가 아직 없다는 이유로 계약 문안과 계획 준비를 서로 막지 않으며, 그 증거가 없어도 activation을 완료할 수 있다는 뜻은 아니다.

본 라운드의 계약·결과에 대한 Owner 수락은 아직 없다. DR v0.5 exact bytes와 현행 normative 계약·admission·제품 source·STATUS/catalog를 유지했다. 새 probe·VM 작업·제품 suite·다른 reviewer·계약 발효·Git publication을 수행하지 않았다.

### R1-D05 Reviewer Final — Verbatim

````markdown
# R1-D05 — DR-0007 Draft 0.5 정적 재리뷰

**범위:** 이번 리뷰는 packet으로 받은 DR-0007 Draft 0.5 한 문서만 정적으로 읽은 결과입니다. 문서 식별값은 122,770 bytes, SHA-256 `d5f407c0…cb7ee`입니다. 도구·source·target 원문·실험 원출력은 사용하지 않았습니다. 문서에 적힌 source 사실과 현행 계약 사실은 보고된 주장으로만 다뤘습니다. 아래 판정은 Reviewer 의견이며 Owner의 계약 수락이나 실행 승인을 대신하지 않습니다.

## 1. Verdict

| 대상 | 판정 | 요지 |
| --- | --- | --- |
| 전체 exact 계약 수락 준비도 | **conditional** | P2 세 건(F1–F3)의 짧은 문안 보완 뒤 수락 가능. P1 없음 |
| 공통 조건 worker | **approve** | 공통 조건과 기존 모든 guard의 교집합, 비폐쇄 예시, 분류 구분이 본문·A2·A3·매핑에서 일관됨. P3 문구 1건 |
| windows-1/detach4 식별 설계 | **conditional** | 제거 전·중·후 식별 구조는 성립. 제거 뒤 "membership 검증"이 무엇과 무엇을 대조하는지 불명확(F2) |
| old-writer 실패 처분 | **conditional** | "발행한다"가 확인된 경우의 처분은 충분함. "알려졌으나 거절이 확인되지 않은" 경우의 처분이 A문안에 없음(F1) |
| A1–A15 내부 정합성 | **conditional** | heading 참조와 29-member 목록은 정합함. entry-1-only 일반 문장에 대한 Windows override가 문서마다 고르지 않을 가능성(F3, target 원문 확인 필요)과 P3 문구 몇 건 |
| 문서 기반 계획 준비 | **approve** | 계약 의미와 계획·qualification 세부의 경계가 분명함. 미래 artifact digest와 미검증 상태가 수락을 막지 않도록 정리됨(345, 727) |

## 2. Findings

### Must-fix (수락 전 문안 보완)

**D05-F1 · P2 · 알려졌지만 미검증인 old writer의 처분 공백**

- **근거:**
  - L159 "확인하지 못한 조합은 미지원"
  - L166 "미검증 조합의 잔여 위험 표기만으로 통과시키지 않는다"
  - L376 "미확인 항목을 통과로 닫지 않는다"
  - L739 "missing required qualification을 … 미지원 표기만으로 통과시키지 않는다"
  - 반면 normative인 A5(L505)와 A13(L670)은 "one would publish / can publish"인 경우만 qualification·activation 중단을 규정합니다.
- **오해 경로:**
  - 예: retained predecessor `8bd0…`처럼 exact bytes를 회수하지 못했거나 실행할 수 없는 알려진 writer가 있다고 합시다.
  - 이 writer를 matrix에서 빼고 L159의 "미지원 조합"으로 표기하면, A5/A13 문언상 중단 사유에 해당하지 않습니다.
  - 그러면 미지원 label 하나로 activation까지 진행할 수 있습니다. 이는 L166·L739와 충돌합니다.
- **최소 수정:** A5 마지막 단락과 A13 둘째 단락에 한 문장을 추가합니다. 새 field·절차는 필요 없습니다.
  - 예시 문장: "A known exposed cooperating old writer whose pre-publication refusal is not verified is treated as one that may publish, unless an evidenced non-exposure boundary covers it."
  - 정확한 "노출됨"의 판정 범위를 좁히고 싶다면 그 기준은 Owner 선택입니다.

**D05-F2 · P2 · 제거 뒤 detach4 검증 내용의 의미 불명확 (persisted reader 의미)**

- **근거:**
  - L335는 "receipt는 prior binding ref와 제거할 binding/inventory의 **digest**를 보존"한다고 씁니다.
  - L356과 L553은 "exact managed remove inventory, preserved … inventory"가 bound된다고 씁니다.
  - A5(L503)는 "complete receipt, membership, digest and prefix checks pass"일 때만 version 4가 windows-1을 지정한다고 합니다.
  - A8(L555)은 "wrong membership … remain non-pass"라고 합니다.
- **오해 경로:**
  - plan/receipt가 제거 대상 경로 목록 없이 inventory digest만 가진다면, product 제거 뒤에는 대조할 대상이 없습니다.
  - 이 경우 "membership 검증"은 고정 29 list를 자기 자신과 비교하는 것이 됩니다.
  - "digest 검증"도 제거된 bytes에 대해서는 불가능합니다(L555도 이 점을 인정).
  - 결과적으로 구현자는 둘 중 하나를 택할 수 있습니다: (a) version 숫자와 필드 형태만으로 PASS 처리, (b) 검증할 수 없다며 영구 non-pass 처리. 이는 사례 5가 경계하는 "version label만으로 정상 판단"으로 이어집니다.
- **최소 수정:** A8 또는 A9에 제거 뒤 검증의 구성요소를 한 단락으로 고정합니다.
  1. plan/receipt가 실제로 담고 있는 remove/preserve 경로 목록이 고정 29 list 및 preserve 집합과 정확히 일치하는지
  2. 제거된 경로의 실제 namespace 부재와 남은 managed directory 상태를 A7 규칙으로 관측
  3. preserve 대상 bytes가 preserve digest와 일치하는지
  4. 제거된 payload의 digest는 재검증하지 않으며 "pre-removal에서 검증됨"이라는 plan 결속에 의존한다는 점
- **확인 필요:** 기존 detach shape가 경로 목록을 포함하는지는 source로 확인할 사항입니다(조건부). 목록이 없다면 새 field가 필요한지가 계약 선택 문제가 됩니다.

**D05-F3 · P2 (조건부) · entry-1-only 일반 문장에 대한 Windows override 범위가 문서마다 다름**

- **근거:**
  - 명시적 override가 있는 곳:
    - A2(L447): General Work의 entry-1 source-profile, repair, schema-3 detach 문장
    - A13(L668): Maintaining의 Checkout Proof·Entry-1 Candidate 문장
    - A15(L692): `./colvia` prefix
  - 같은 형식의 override가 없는 곳:
    - A8(Workspace): "entry-1/First B1 semantics remain unchanged"만 있음
    - A9(Structure): "현재 window 목록과 schema 설명은 역사적 의미 그대로"
    - A12(Reference): "where that command already accepts --profile"
- **반례 가능성:** target에 "profile은 `entry-1`이어야 한다", "detach는 schema 3을 쓴다", "허용 window는 …이다" 같은 닫힌 현재형 문장이 있다고 합시다. 그러면 A8·A9·A12의 Windows 절과 문자 그대로 충돌합니다. 그 결과 어느 쪽이 우선하는지 reader마다 다르게 읽힙니다.
- **최소 수정:** Driver가 Workspace·Structure·Reference·Security의 해당 절을 대조합니다. 닫힌 entry-1-only 문장이 있으면 A2와 같은 한 문장 qualifier를 그 A절에 추가합니다: "For windows-1 only, this clause qualifies …; those statements retain their entry-1 and historical meanings."
- **한계:** target 원문을 받지 않았으므로 반례가 실재하는지는 단정하지 않습니다.

### 선택 보완 (P3)

| ID | 근거 | 문제 | 최소 수정 |
| --- | --- | --- | --- |
| D05-F4 | A9 L612 "retains" ↔ A2 L447 "extend", A10 L624 "is extended" | CRLF 예외가 windows-1에 이미 있는 것처럼 읽힘 | A9도 "extends … to windows-1"로 통일 |
| D05-F5 | A1 L431 "Windows path-observation rules" | 다른 문서(Workspace)의 어느 절인지 이름이 없음 | "Workspace Contract's Windows Native Observation And Publication"으로 명시 |
| D05-F6 | A2 L451 "whose actual path is absent in the exact base" | L269의 "exact base에도, 실제 control 경로에도 없음"이 하나로 뭉쳐짐 | "absent from both the exact base and the actual control namespace" |
| D05-F7 | A9 L610 "that version admits no other window" | 이후 다른 window(예: windows-2)가 schema 4를 재사용해도 되는지 열려 있음 | "Detach schema 4 is reserved to windows-1; another window requires its own version or design" |
| D05-F8 | A6 L517은 3.14.6/3.14.7을 고정, A10 L622는 기존 요구를 참조 | runtime 집합이 두 곳에 있어 갱신 시 어긋날 수 있음. "standard-user"가 runtime gate 조건인지 지원 범위인지 불명확 | A6은 Security runtime 절을 참조. standard-user는 지원·qualification 범위이고 gate 조건이 아님을 명시(gate로 둘지는 Owner 선택) |
| D05-F9 | A11 L640은 detach에 `--profile windows-1`을 지정, A12 L654는 "where … already accepts" | detach source 경로가 `--profile`을 받지 않는다면 A11이 새 인자를 만드는 것이 됨 (조건부) | source 대조 뒤 A11 문구를 A12의 조건부 형태로 맞춤 |
| D05-F10 | L158·S2 "old-window mutation 미지원" | 새 entry-1 release가 Windows host에서 mutation을 실제로 거절하는지(L329: OS gate 없음), 아니면 지원 주장만 하지 않는 것인지 불명확 | "지원 주장 경계이며 이 DR은 old window에 새 gate를 추가하지 않는다"(또는 반대)를 한 문장으로. 의미 선택은 Owner |

## 3. 8사례 compact table

| # | 이미 정합한 의미 (근거) | 남은 계약 문안·Owner 선택 | 구현·qualification 세부 |
| --- | --- | --- | --- |
| 1 worker | 공통 조건은 추가 필요조건이며 기존 guard를 대체하지 않음 (L262, L445, L449). 예시는 닫힌 목록이나 충분조건이 아님 (L264, L451, L471). 네 분류가 구별됨: stable tracked, eligible untracked 644, new untracked 644, index-only add(755 포함) (L268–272, L451) | F6 문구 | index-only add와 eligible untracked가 실제로 도달 가능한지는 source 없이 미확인(조건부). 해당 fixture가 필요 |
| 2 삭제 | 후보 membership과 실제 존재를 분리 (L236, L431). alias·type·reparse·접근 실패·불안정 관측은 non-pass이며 생략·삭제로 처리하지 않음. parent 문제를 leaf 부재로 처리하지 않음. 특수 flag는 non-pass/unknown. 독립 재관측 뒤 whole-result 일치 (L449) | F5 참조 명시 | stage-0·skip-worktree·intent-to-add 분류와 안정성 검사 방법 (L238) |
| 3 거절·drift·replay | prepare는 ticket 미발급, apply는 decision·selection·current·content 발행 전 재검사 (L455). drift/stale, policy unsupported, unknown 구별. pending 보존, all-pre cancellation 불변. reject·submission은 막지 않음. completed replay에 새 gate 없음 (L435, L457) | 없음 | 실제 발행 경계 위치와 오류 매핑 |
| 4 identity 근거 | installed chain, source-init plan/token/candidate, 실제 OS/process gate를 분리 (L501, L622). profile·OS 단독으로는 증명이 아님. window 내 고정 정책과 양방향 reader (L499, L614) | F8 (standard-user 성격) | emulation 판별 방법, Q→P reader fixture |
| 5 detach4 | candidate null, 기존 필드 유지 (L553). 제거 전 window 검증, receipt 선발행, 이후 schema 4로 식별. historical 1/2/3 불변. label은 qualification이 아님 (L503, L555, L682) | **F2**, F7 | 중단 prefix별 식별, 구 reader의 unavailable 보고 |
| 6 old writer | 발행이 확인되면 중단. label·경고로는 통과 불가. 최소 유효 거절 또는 근거 있는 비노출. 새 field를 자동 도입하지 않음. 의미가 바뀌면 재수락 (L378, L505, L670) | **F1** (미검증 writer). 비노출 근거 기준은 Owner 선택 | 실제 writer identity 고정과 거절 시험 |
| 7 A1–A15 | 교차 heading 일치: A3→A1/A2, A5→A9, A8→A7, A2→A8/A11. 29-member는 개수·UTF-8 순서·11 module/11 docs가 L164·L725와 일치. pair 표가 L349–360 및 S2와 일치. unchanged-CRLF 범위 일관 | **F3**, F4, F9 | target 원문에 메모리상 적용 결과(L745)를 Driver가 재확인 |
| 8 B·admission | 대표 UTM 전체 + x64/물리 focused. 자동 full matrix·물리 gate 없음. 미관측 tuple 보존. formal admission은 Preview 이후. 5.1은 대상일 뿐 qualified 아님. criteria 5/8 교체와 6–9 유지 (L475, L517–519, L674) | F8 (버전 중복) | 실제 tuple, 5.1 입력 보존, 예산·ledger |

## 4. 수락 전 보완 vs 이후 실제 증거

### 수락 전 문서 보완 / Owner 선택

- **F1:** 미검증 known old writer를 "발행 가능"과 같게 취급할지. 권고는 같게 취급하는 것입니다.
- **F2:** 제거 뒤 detach4 검증 구성요소를 고정. 기존 shape에 경로 목록이 없다면 새 field가 필요한지가 계약 선택이 됩니다.
- **F3:** target 대조 결과에 따른 qualifier 추가.
- P3(F4–F10)는 선택입니다. F8의 standard-user 성격과 F10의 old window 거절 의미는 Owner가 고를 문제입니다.

### 해결됐거나 반례가 없는 부분

- 공통 조건 worker 정의와 비폐쇄 예시
- 삭제와 index 잔존의 구별
- whole-operation 거절, drift, unknown, pending, reject, replay의 상호 경계
- source-init이 binding 이전에도 기존 plan/token/candidate로 결속된다는 점 (L333)
- 동일 window의 고정 mode 의미
- B 배정과 admission timing
- 29-member 목록 자체
- 미래 digest를 수락 전제조건으로 삼지 않는 순서

### 수락 뒤 실제 증거 (문서 결함으로 승격하지 않음)

- Win32 lock, flush, replace의 API 대응표와 실패 주입
- 실제 OS/process gate 구현
- 정적 사례(eligible untracked, index-only add)의 도달 가능성과 성공 fixture
- known old writer bytes 회수와 거절 시험
- detach4 중단 prefix 시험
- PowerShell 5.1 입력 보존
- 두 autocrlf 설정 시험
- normal/parent-optimized 전체 회귀와 macOS 회귀·재사용 판단
- x64·물리 PC focused 보완

## 5. 읽지 못한 근거와 잔여 한계

- **target 원문 미제공:** A1–A15의 실제 삽입 위치와 대체 대상 문장을 확인하지 못했습니다. 따라서 적용 가능성과 F3 반례의 실재 여부는 검증하지 않았습니다.
- **source 대조 불가:** 다음 사실은 모두 문서의 보고만 받아들였습니다.
  - L326–335의 code 위치·allowlist·plan/receipt shape
  - detach plan에 경로 목록이 있는지(F2 전제)
  - `--profile` 수용 범위(F9)
  - eligible worker 사례의 도달 가능성
- **이전 자료 미열람:** 이전 리뷰 원문, R1-D04 처분 기록, probe 원출력, release digest의 실제 bytes를 읽지 않았습니다.
- **수행하지 않은 검증:** 실행 재현, 렌더링 검증, hash 재계산을 하지 않았습니다. 이 리뷰는 어떤 지원 PASS도 만들지 않습니다.
- **효력 범위:** 이 판정은 Driver의 accept/revise/defend/needs-user 처분과 Owner의 exact 계약 수락을 대신하지 않습니다. 제품 실행이나 계약 발효를 허용하지도 않습니다.
````

### R1-D05 Record Verification And Retention

GFM(marked 17.0.5)으로 DR·이 진행 기록·private task 기록 3개를 렌더링하고 code 밖 literal 강조 기호 없음, 로컬 경로/heading 링크 78개, whitespace/disclosure를 확인했다. R0/R1-P01/R1-D01–D05의 7개 frozen packet·request·최종 응답 및 기존 기록의 verbatim 보존, D05-F1–F10 처분, 별도 Driver D05-D1을 확인했다. 리뷰 전 진행 기록은 이번 append와 State 한 줄 변경을 제외하고 byte-identical이다. DR v0.5 exact 복구와 hash, 비어 있는 수락 전용 절, 8개 선택·10개 admission·A1–A15, source HEAD와 기존 navigation diff, 나머지 source/계약 입력의 무변경을 확인했다. 이는 문서 기록 검증이며 제품 qualification이 아니다.

원 request·packet·입력 식별자·최종 응답·실행 metadata는 Owner 처분과 다음 exact 문안 비교의 소비자가 있어 보존한다. bounded runner는 같은 제한을 재사용할 후속 문서 리뷰 준비 입력으로 두되 새 실행은 별도 요청이 필요하다. Owner 처분/후속 비교 시 남은 사용 목적을 재평가한다. 기존 VM·worktree·probe raw·마지막 복구본의 수락/복원/후속 비교 목적과 종료 조건은 유지한다.

정리 완료: final과 동일한 partial, 빈 stderr, 빈 tool-temp, 일회성 문서 검사기와 report의 사용 종료를 확인하고 5개 대상을 삭제했다. 필요한 원문·입력·metadata와 위 재사용 입력은 보존했으며 활성 경로 변경은 없다. 정리 후 메모리에 둔 검사기로 같은 검증을 다시 수행해 통과했다. DR·제품 구현·실험 상태는 변경하지 않았다.


## Contract Draft Revision 0.6 — 2026-10-18

Owner는 R1-D05와 Driver 권고를 반영해 old writer 거절 미확인 처분, detach4 제거 후 검증, A1–A15 Windows 범위와 exact repair mode를 명확히 하도록 요청했다. B와 공통 조건 중심 worker 지원을 유지하며 새 실험·제품 구현·reviewer 호출은 하지 않는다.

[DR-0007 Draft 0.6](../decisions/DR-0007-windows-native-runtime-contract.md)의 변경은 다음과 같다.

| 입력 | 반영 |
| --- | --- |
| F1 | 노출된 known old writer의 거절 미확인·실행 불가도 qualification/activation 미완료. 검증된 거절 또는 검증 가능한 비노출 처분 필요. 모든 역사 writer 회수를 자동 gate로 만들지 않음 |
| F2 | 기존 전체 remove/preserve path·digest·size, release별 29 payload와 metadata, 내부 hash 관계, 실제 suffix/안전한 부재·preserve bytes를 제거 뒤에도 대조. 삭제된 bytes의 재해시를 주장하지 않음 |
| F3–F6 | A1의 named path clause, A2의 base·실제 namespace 부재, A8/A9/A12의 실제 closed entry-1 문장에 Windows 한정 qualifier, unchanged-CRLF의 동일 증명 아래 확장을 명시 |
| F7/F9 | detach4는 windows-1 전용, 기존 detach profile interface 유지. repair 새 profile option 없음 |
| F8/F10 | Security runtime 정본, 표준 사용자 qualification 환경과 OS/process mutation gate 구별. 새 Windows 경로의 거절을 기존 entry-1 source의 소급 OS gate로 확대하지 않음 |
| D05-D1 | repair1의 mode를 native read-only 관측 integer 0/1로 제안. before·after·backup·drift·recovery/replay 비교를 고정하고 POSIX/TreeEntry/completion 의미와 구별 |

0/1은 아직 구현되지 않은 Windows 한정 persisted 의미의 제안이다. 기존 integer field와 repair1 pair를 유지하되 windows-1 exact candidate로 구별하며 같은 window reader의 양방향 qualification이 필요하다. 원 read-only를 임의 해제해 replace를 강행하지 않고 실패는 원 request/backup/prefix를 보존한다. 다른 window의 과거 mode와 accepted 문서는 수정하지 않았다.

이번 source 정적 대조는 기존 repair의 stat-derived before, launcher 0755 after, exact before/after drift 및 completed replay 비교와 현재 detach의 완전한 inventory 구조를 근거로 했다. 새 Windows mode의 실행 성공이나 runtime 반례 재현으로 표시하지 않는다. v0.6 변경 bytes는 아직 외부 재리뷰·Owner exact 수락·qualification·activation을 받지 않았다.

Draft identity: 140,365 bytes; SHA-256 `8d595d93d57855903cf0ee28d13b94838a4d5679afb72a445fe7ea5bc7e767ef`. v0.5 exact bytes는 기존 R1-D05 frozen packet에서 복구 가능하다. 이전 리뷰 원문과 처분은 그대로 보존했다.

검증: 작성 문서 3개를 marked 17.0.5 GFM으로 렌더링하고 local path/heading link 80개, code 밖 literal 강조 기호, whitespace와 공개용 식별자 경계를 확인했다. A1–A15를 실제 파일에 쓰지 않고 11개 target 사본에만 적용해 위치·heading·렌더링을 확인했다. 13개 보호 절(B·worker 공통 조건 포함), Owner 원문, 29-member source AST 목록, S1–S8과 열 가지 기준, 비어 있는 accepted-only 절, 7개 frozen 리뷰와 원문, 이전 v0.5 복구·bounded diff 및 기존 CHORE bytes 보존을 확인했다. 나머지 고정 입력·source HEAD·기존 navigation diff는 변하지 않았다. 문서/정적 검증이며 제품 실행 PASS가 아니다.

정리 범위: 이 개정의 입력 식별자와 revision diff는 Owner 비교·다음 exact 리뷰 처분까지 유지한다. 작성·보완·검사 helper 및 일회성 검사 보고서는 결과 기록과 no-use 확인 뒤 정리한다. 기존 작업 경로는 바꾸지 않으며 VM·probe 원출력·마지막 복구 사본의 기존 결과 수락·복원 확인 목적은 유지한다.

정리 완료: no-use 확인 후 이 개정의 apply/refine/check helper 3개와 일회성 보고서 1개를 삭제했다. 입력 식별자·revision diff와 필수 기존 증거는 보존했고 active path 변경은 없다. 삭제 후 최종 기록을 포함해 같은 검증을 재실행했으며 보고서는 재생성하지 않았다.


## R1-D06 Draft 0.6 Re-review And Driver Judgment — 2026-10-18

### Request, Identity And Execution

Owner는 “DR-0007 v0.6을 Claude CLI로 재리뷰해줘. old writer 거절 미확인 처분, detach4 제거 후 검증, Windows repair mode 0/1 의미와 A1–A15의 일관성을 확인하고 네 판단도 정리해줘. B안과 공통 조건 중심 worker 지원은 유지하고 추가 실험이나 제품 구현은 시작하지 마.”라고 요청했다. 이 라운드는 지정 Draft 한 건의 정적 리뷰와 Driver 판단이며 계약 수정·실험·제품 실행·추가 reviewer·publication은 승인하지 않는다.

| 항목 | 실제 입력·결과 |
| --- | --- |
| 역할 | Driver Codex, Reviewer fresh Claude CLI, Owner 최종 선택·수락 |
| 대상 | [DR-0007 Draft 0.6](../decisions/DR-0007-windows-native-runtime-contract.md), 140,365 bytes, SHA-256 `8d595d93d57855903cf0ee28d13b94838a4d5679afb72a445fe7ea5bc7e767ef` |
| source / diff | baseline `a93f71c359c4f0a9d57fcfb50d5999160e870f77`, tracked diff SHA-256 `91f501b2077cfc175ae80edbddd2f56a32b71c2bcb6c6b7c1659d01c3e42a7ef`. 대상은 이 tracked diff 밖의 untracked 문서로 packet에 전부 포함 |
| 전송 범위 | 번호를 붙인 해당 문서만 전송. 링크된 계약·제품 source·실험 원출력·이전 리뷰 원문은 미전송 |
| packet / request | packet 144,853 bytes, SHA-256 `a233eb495be0d840a4256ca72ac3cc7c43154a93e544c74273cc9a0f781bd0ba`; request SHA-256 `1ce71e1598f8a441d6bf926e4e5d289c2afec2848b89db5f9d9593de3757e84e` |
| Reviewer identity | Claude Opus 5.5, reported model `claude-opus-5-5`; CLI `2.1.302`; fresh session `0c349da1-847c-4ab9-8ba7-ddb6545b7fd1` |
| 인증·과금 경로 | `claude.ai / firstParty / pro` 확인. provider override 없음; 키·토큰·이메일 미기록 |
| 실행 경계 | 고정 packet stdin, no tools, strict empty MCP, no Chrome/session persistence, permission prompts none. 실행 상한 1,200초. 제품/test/web/file access 없음 |
| 실행 결과 | 2026-10-17 22:48:49–22:53:39 UTC, 289.618초, exit 0, tool events 0, 입력 전후 drift 없음 |
| 최종 응답 | 15,100 bytes, SHA-256 `c1636bca4d96e3d37381db4b15ad0bfd930ac4510178a952df7630e7204edd13`. 아래 원문 그대로 보존 |

Reviewer는 source나 target 계약을 독립적으로 읽지 않았다. 아래 source 대조는 Driver의 별도 정적 확인이며 Windows 실행·재현·qualification이 아니다. fresh session과 도구 제한은 context 공유를 줄였지만 검토의 완전성이나 source 독립 검증을 보증하지 않는다.

### R1-D06 Verdict And Driver Assessment

| 검토 대상 | Reviewer | Driver 판단 |
| --- | --- | --- |
| 전체 exact 수락 준비도 | conditional | 유지. read-only lifecycle 의미와 local NTFS mutation 경계를 먼저 명확히 하고 실제 상태 문구 오류를 수정할 필요 |
| old-writer 미확인 처분 | approve | 동의. 실제 노출된 writer의 미확인·실행 불가·발행을 통과시키지 않으며 모든 역사적 writer 회수를 새 gate로 만들지 않음 |
| detach4 제거 후 검증 | conditional | 목록·내부 링크·실제 suffix/부재·preserve·삭제 bytes 재해시 불가의 핵심은 동의. read-only 제거 정책과 embedded plan 설명은 보완 후보 |
| Windows repair mode | conditional | 0/1의 field 의미와 candidate 기반 선택·backup/drift/replay는 정합. “영구 막힘” 일반화는 source 대조 결과 좁혀야 함 |
| A1–A15 | conditional | Windows qualifier의 방향 유지. filesystem gate, 오래된 상태 문구와 일부 map/reader 설명 보완 |
| 공통 조건 worker / 문서 계획 | approve / approve | 동의. B·worker 공통 조건은 유지하고 새 전체 matrix나 실험을 기본 해결책으로 추가하지 않음 |

Reviewer는 P1 없음, P2 두 건과 P3 여섯 건을 제시했다. F1·F2·F3은 must-fix, F4–F8은 선택 보완으로 분류했다. 이는 제품 defect 수나 재현된 runtime failure 수가 아니다. Driver는 아래처럼 각 지적을 따로 처분하며 이 리뷰 승인만으로 DR을 수정하지 않는다.

### R1-D06 Finding Dispositions

| Finding | Driver disposition | 판단·권고 | 남은 범위 |
| --- | --- | --- | --- |
| F1 · P2 · read-only lifecycle / 영구 막힘 | revise | lifecycle 전체의 생성·교체·제거 속성 정책을 명시할 취지는 수용한다. 다만 v0.6은 replace 실패의 stable non-pass를 이미 허용하며 기존 repair backup은 product pending authority가 아니다. 따라서 같은 request의 재호출 실패 가능성을 모든 복구의 영구 교착으로 단정하지 않는다. 자세한 source 근거는 아래에 둔다. 권고는 Windows writer가 새 관리/runtime·authority 파일을 read-only clear로 만들고 immutability 표식으로 쓰지 않으며, 기존 read-only 교체·제거 대상은 첫 durable publication 전 operation 전체를 사전 거절하는 최초 범위다. 검사 뒤 drift로 생긴 partial failure까지 없어진다고 약속하지 않는다 | 이 사전 거절은 v0.6의 성공 미보장과 다른 명시 지원 제한이므로 exact 계약 선택으로 제시해야 함. 속성 해제 전이는 기본 추가하지 않음. 기존 원 request·backup 보존 및 허용된 새 preview와 진짜 pending barrier의 구별 필요 |
| F2 · P2 · NTFS gate | revise | native local NTFS를 실제 관측하는 mutation 경계로 명시하는 권고에 동의한다. S3가 이미 한정한 지원 경로를 evidence-only로 오인하지 않도록 A7/A10과 연결한다. 표준 사용자 qualification 조건과 filesystem 조건을 한 문장으로 묶지 않는다. Reviewer의 `fixed`까지 자동 추가해 지원 범위를 더 좁히지는 않는다 | target·staging·external backup 등 operation이 의존하는 지원 경로와 관측 불가/비NTFS의 non-pass를 exact 문안으로 고정. 새 admin-token gate나 B matrix 변경 없음 |
| F3 · P3 · 오래된 상태 문구 | accept | v0.6 Open Points 끝에 v0.5 미리뷰/R1-D04 문장이 실제 남아 있다. 이전 개정에서 Driver가 놓친 현재성 오류다. 작성 시점의 v0.6·R1-D05로 바로잡되 현재 리뷰 결과는 이 record로 식별 | 다음 승인된 문서 보완에서 수정. 이번 리뷰에서는 reviewed bytes 고정 |
| F4 · P3 · A14 target map | accept | A14 본문·위치는 존재하지만 첫 Named Amendment Map에 Manual Operation이 빠져 있다. map에 retained-evidence target을 연결하는 보완은 유용 | navigation·대응표 보완이며 새 contract target 추가 아님 |
| F5 · P3 · detach 판독 입력 | revise | receipt가 plan을 담지 않을 수 있다는 조건부 전제는 현 source/Structure와 맞지 않는다. receipt는 complete plan을 내장한다. read-only 검증은 이 내장 plan과 실제 보존·잔존 상태로 가능하며 mutation recovery는 original exact plan/token과 원 target을 확인한다 | 이 차이를 한 문장으로 드러내는 보완 권고. 새 field나 별도 외부 plan을 read-only의 필수 입력으로 만들지 않음 |
| F6 · P3 · 과거 auditor 행동 | revise | 과거 코드에 규범만으로 새 동작을 보장할 수 없다는 취지 수용. 그러나 read-only auditor의 false PASS와 old writer의 authority/content 발행은 다르므로 A5/A13의 writer 처분을 그대로 복사하지 않는다 | detach4를 모르는 reader의 결과는 detach4 검증 근거로 인정하지 않으며 compatible qualified reader가 필요하다고 서술. 그 reader가 필수 qualification 증거에 쓰이면 해당 증거를 non-pass로 처분 |
| F7 · P3 · launcher literal 생성 | revise | 현 source는 root launcher literal을 읽어 candidate를 만들고 profile은 bytes를 생성하지 않는다. Windows 후보의 literal/payload가 언제 고정되는지 계획에 필요하다는 지적 수용. verified windows-1 source/artifact를 candidate 생성 전에 명시적으로 준비하고 runtime에서 OS/profile만 보고 payload bytes를 바꾸지 않는 방향 권고 | default macOS entry-1은 유지. 별도 Windows artifact를 만드는 build/packaging 방법은 계획 세부이며 identity/지원 의미가 달라지면 exact 문안에 올림. 아직 artifact/구현 미생성 |
| F8 · P3 · S2·criterion 2 요약 | revise | old-writer 상세 처분은 이미 405행/A5/A13에 있으므로 요약 불일치로 보지 않는다. 상세 조항 pointer와 repair qualification의 연결은 개선할 수 있다 | 현행 criterion 2는 repair를 열거하지 않으므로 그 기준 원문을 수정한 것처럼 쓰지 않음. S2의 추가 same-window repair 검증 의무로 mapping에 명확히 연결 |

### R1-D06 Local Static Cross-Checks By Driver

1. **Repair의 pending과 backup:** [Workspace — Exact Active Repair](../WORKSPACE-CONTRACT.md#exact-active-repair)는 external receipt를 binding-selection chain 밖의 evidence로 정의한다. `product.py:888–892`는 product lifecycle pending이 없고 exact active candidate일 것을 요구하며, `1602–1624`는 현재 repair 관측으로 새 preview를 만든다. `1710–1729`는 original backup과 그 exact request의 completed replay를 검증한다. 별도 외부 repair backup의 존재가 target에 새 pending authority를 만드는 경로는 이 확인 범위에 없다. 원 request의 after/before와 달라진 상태를 같은 exact recovery로 인정할 수 없다는 점은 유지한다. 모든 다른 guard를 충족하는 새 preview 가능성까지 금지됐거나 Windows에서 영구 교착이 재현됐다고 주장하지 않는다. 실제 Windows candidate는 미구현이다.
2. **READONLY 관측의 한계:** 기존 probe 기록에는 readonly destination의 `os.replace` error 5가 있다. 이것은 당시 fixture의 과거 관측이며 이번에 재실행하지 않았다. 모든 native API·read-only 파일·retry가 반드시 실패한다고 일반화할 수 없다. read-only 사전 거절을 택하더라도 관측 뒤 다른 process의 drift와 unexpected failure에 대한 원 prefix 보존은 남는다. `S6/A9`의 0/1 비교 자체에 새 반례는 발견하지 않았다.
3. **Detach 내장 plan:** [Structure — Plans, Bindings And Receipts](CHECKOUT-1-STRUCTURE.md#plans-bindings-and-receipts)의 receipt는 complete plan을 포함한다. `product.py:1829–1831`은 plan을 receipt의 `plan`에 넣고, `1882–1919`는 canonical receipt·원 truth·preserve bytes·남은 file/dir suffix를 대조한다. F5의 “외부 plan 없으면 읽을 수 없음”은 실제 구조에 해당하지 않는다. 이 source는 schema 1/2/3이며 새 detach4 구현 성공 증거가 아니다.
4. **Candidate 생성:** `colvia:4`의 현재 literal은 entry-1이다. `product.py:249–284`는 launcher AST 선언을 읽고 `349–370`는 exact payload bytes와 그 선언으로 inventory/digest를 만든다. `cli.py:111–117`의 profile 검사는 요청 선택이며 literal 생성기가 아니다. Windows-1은 현재 allowlist에 없다. F7은 이미 동작하는 기능 설명이 아니라 앞으로의 packaging/identity 계획에서 고정할 사항이다.
5. **NTFS와 현재성:** [S3](../decisions/DR-0007-windows-native-runtime-contract.md#s3--path-observation-and-identity)는 native local NTFS를 지원 경로로 한정하지만 A7/A10에서 실제 filesystem 관측과 mutation 거절을 명시적으로 연결하면 혼동을 줄일 수 있다. Open Points의 784행 상태 문구는 R1-D05 사실과 상충함을 직접 확인했다. 이 오류는 지난 GFM/링크 검증 PASS와 별개의 의미 검토 누락이다.

### R1-D06 Remaining Before Contract Acceptance

Driver 권고는 B, 공통 조건 worker, windows-1 identity, detach4 inventory 검증, repair mode 0/1의 기본 설계를 유지하는 것이다. 다음 문서 보완에서는 아래 범위만 우선 다룬다.

- read-only를 Windows immutability/발행 완료 표식으로 쓰지 않는 생성 정책과 교체·제거 대상의 사전 거절 범위를 exact 문안으로 선택한다. 뜻밖의 drift·실패 이후의 stable non-pass는 계속 허용하며 복구 성공을 약속하지 않는다.
- 표준 사용자 evidence 조건과 native local NTFS mutation 검사를 구별하고 검사 대상 경로·unknown 처분을 명시한다.
- F3 상태 오류를 수정하고 A14 map, embedded-plan 읽기, 과거 reader 결과의 증거 자격, Windows artifact 준비 시점, repair mapping을 정렬한다.

그 뒤 실제 writer 노출/거절, API·PowerShell 입력 보존, target/artifact bytes와 전체/focused qualification을 입증해야 한다. 문서 보완으로 그 실행을 대신하지 않는다. known old writer 미확인 처분, worker 공통 조건과 B 자체를 다시 선택하거나 새 full matrix를 만들 이유는 이번 리뷰에서 발견하지 않았다.

이번 Owner 요청은 리뷰와 판단 정리까지다. 위 보완안은 권고이며 계약 수락·DR 개정·새 실험·제품 구현·결과 activation을 승인한 것으로 기록하지 않는다. DR-0007 v0.6 bytes와 normative 문서는 그대로 유지한다.

### R1-D06 Reviewer Final — Verbatim

````markdown
# R1-D06 — DR-0007 Draft 0.6 정적 재리뷰 (Reviewer: fresh Claude CLI session)

**범위:** 제공된 DR-0007 Draft 0.6 packet 한 건만 정적으로 읽었습니다. 도구·파일·source·링크 target·이전 리뷰 원문·실험 원출력은 보지 않았습니다. 문서에 인용된 source·계약 사실은 보고된 주장으로 취급했습니다. Windows API 동작은 재현하지 않았습니다. 아래 판정은 Owner의 계약 수락·실행 승인·activation을 대신하지 않습니다.

---

## 1. Verdict

| 대상 | 판정 | 요지 |
|---|---|---|
| 전체 exact 계약 수락 준비도 | **conditional** | P1 없음. P2 두 건(D06-F1 read-only 속성 처분, D06-F2 filesystem gate)과 상태 문구 오류 한 건(F3)을 고치면 수락 가능한 수준 |
| old-writer 미확인 처분 | **approve** | 405행, A5, A13, 792행 사이에 실질 상충 없음. S2 요약의 정렬만 선택 보완(F8) |
| detach4 제거 후 검증 | **conditional** | 제거 전·중·후, 내부 링크, 재해시 불가, trusted-local 설명은 정합. read-only 관리 파일 제거 처분 공백(F1)을 보완해야 함. 판독 주체별 입력 명확화(F5)는 선택 |
| Windows repair mode | **conditional** | 0/1 정의, POSIX와의 구별, before/after·backup·replay 규칙은 정합. 다만 read-only 대상의 중간 prefix 실패가 영구 non-pass로 빠지는 경로가 있음(F1) |
| A1–A15 내부 정합성 | **conditional** | 상호 참조 heading은 문서 내부에서 모두 실재함. filesystem gate 모호성(F2), 784행의 오래된 상태 문구(F3), map 누락(F4) |
| 공통 조건 worker | **approve** | 공통 필요조건과 기존 guard의 교집합, 열린 예시, 정적 반례 처리가 S6·A1·A2·A3·A13·mapping에서 일치 |
| 문서 기반 계획 준비 | **approve** | 남은 finding은 짧은 문안 결정이며 계획 준비를 막지 않음 |

---

## 2. Findings

### Must-fix

#### D06-F1 · P2 · Windows read-only 속성의 lifecycle 전반 처분 공백과 repair 중간 prefix 영구 막힘

**근거 문구**
- 311행: "read-only flag drift도 exact request의 drift다."
- 313/661행: original의 read-only를 임의 해제하지 않으며, "발행할 수 없으면 원 request·backup·실제 prefix를 보존한 non-pass"로 둔다.
- 657행: 복구 시 관측은 before 또는 after만 허용한다.
- 564행(A7): ACL·ownership만 금지 대상으로 열거한다.
- 578행(A8 switch), 580–584행(detach): read-only 관리 파일을 교체하거나 제거할 때의 규칙이 없다.

**정적 반례 1 — repair**
1. 두 파일 repair를 시작한다. A는 쓰기 가능하고, B는 before.mode=1이다.
2. A는 after로 교체되고, B 교체는 실패한다. 실패 가능성 자체는 문서(313행)가 인정하므로 API 재현과 무관하게 경로가 존재한다.
3. 같은 request로 재호출해도 해제 금지 규칙 때문에 B 교체는 다시 실패한다.
4. 사용자가 B의 속성을 직접 해제하면 B는 mode 0이 된다. 이는 before(1)도 after(1)도 아니므로 drift이고 non-pass다.
5. 새 repair request가 pending prefix 위에서 허용되는지는 "existing narrow pending-record exception"(578행)에 달려 있고, 문서 안에서 정해지지 않았다.

따라서 exit 경로가 정의되지 않은 영구 non-pass가 생길 수 있습니다.

**정적 반례 2 — 다른 lifecycle**
- repair는 의도적으로 after.mode=before.mode=1을 보존합니다.
- 이후 same-window update가 root `colvia`를 교체하거나 detach가 제거할 때 read-only 처리 규칙이 없습니다.
- 그래서 구현마다 속성을 해제하거나, 실패시키거나, 중간 prefix에서 멈추는 서로 다른 동작이 나올 수 있습니다.
- 또한 init/update가 관리 파일을 read-only로 만드는지도 정해져 있지 않습니다. 예를 들어 현행 POSIX chmod를 Windows에 이식하면 쓰기 bit 없는 mode가 READONLY 속성으로 바뀔 수 있습니다. 이는 일반적 플랫폼 지식이며 여기서 확인하지 않았습니다.
- 이 경우 missing→0 규칙과 init이 만든 상태가 어긋나고, 모든 설치 파일이 repair 불가가 될 수 있습니다.

**최소 수정 (A8/A9에 두세 문장)**
1. windows-1 writer는 launcher·payload·lifecycle 기록을 READONLY clear 상태로 만들고, 이 속성을 immutability 표식으로 쓰지 않는다.
2. repair에서 기존 target 중 하나라도 before.mode=1이면, backup이나 첫 교체 전에 operation 전체를 거절한다. 기본안은 preview에서 미지원으로 보고하는 것이다. 이렇게 하면 "성공을 보장하지 않음"이 중간 prefix 실패가 아니라 결정적인 사전 거절이 된다.
3. update/rollback/detach는 첫 발행 전에 교체·제거 대상의 read-only 속성을 검사한다. read-only면 발행 없이 non-pass로 두고 속성을 해제하지 않는다.

대안은 속성 해제를 허용하는 전이를 별도로 수락하는 것이며, 이는 Owner 선택입니다. 이 수정은 B 방향이나 worker 방향을 바꾸지 않습니다.

#### D06-F2 · P2 · local NTFS가 mutation gate인지 evidence 경계인지 모호함

**근거 문구**
- 187행(S3): "지원 경로는 native local NTFS로 한정"
- 389/546행: "Standard-user local/guest NTFS is the initial support/admission evidence boundary… does not introduce an administrator-token refusal gate"
- 672행(A10)의 비허용 목록은 emulated pair, 32-bit, POSIX 호환 runtime, 다른 OS뿐이다.
- A7 첫 단락에는 filesystem 종류나 local volume 조건이 없다.

**오해 경로**
- windows-1 target이 ReFS Dev Drive, SMB share, exFAT 위에 있는 경우를 생각해 봅니다.
- 문안상 NTFS가 표준 사용자 조건과 함께 "evidence boundary" 쪽으로 묶여 있습니다.
- 그래서 구현자는 이런 volume에서 mutation을 허용할 수 있습니다.
- 그러면 lock(byte-range), flush, file identity, reparse 의미가 qualification 밖에서 동작합니다.

이 문제는 case 6이 요구한 "표준 사용자 evidence 대 OS/process mutation gate" 구별이 filesystem 차원에서 닫히지 않은 사례입니다.

**최소 수정 (A7 또는 A10에 한 문장, Owner 선택)**
- **(a) 권고:** target root와 검사 대상 volume이 local fixed NTFS임을 실제로 관측하고, 아니면 mutation을 non-pass로 둔다. 판별 불가는 unknown이다.
- **(b)** filesystem을 support 경계로만 두고 gate는 두지 않는다. 이 경우 그 결과를 명시적 잔여 위험으로 문서화해야 하며 S3 문구도 그에 맞게 낮춘다.

#### D06-F3 · P3 · 784행의 오래된 리뷰 상태 문구

**근거**
- 784행: "v0.5는 아직 Claude 재리뷰를 받지 않았다. R1-D04는 v0.4의 정적 리뷰이며…"
- 이는 36·66행(R1-D05가 v0.5를 검토함, v0.6 bytes는 재리뷰 전)과 직접 상충한다.

**오해 경로:** 리뷰 이력을 근거로 수락 범위를 판단하는 사람이 v0.5 상태를 잘못 읽을 수 있습니다.

**최소 수정:** "v0.6 bytes는 작성 시점에 Claude 재리뷰를 받지 않았다. R1-D05는 v0.5의 정적 리뷰이며 v0.6 변경분을 승인한 것이 아니다."로 교체합니다.

### 선택 보완

#### D06-F4 · P3 · Named Amendment Map에 A14 target 누락

409–419행의 named scope 표에 `MANUAL-OPERATION.md`(A14 target)가 없습니다. 428행의 A13–A15 행이 보완하지만, map은 "수정할 named scope 초안"으로 제시되어 있으므로 Manual Operation — Retained Evidence 행 하나를 추가하는 것이 좋습니다.

#### D06-F5 · P3 · 조건부 · detach4 판독 주체별 필요 입력

**근거**
- 582행: "validate the complete canonical plan/receipt pair"
- 586행: "A valid complete receipt supports read-only completed replay"
- 734행(A14): "only a paired detach4 receipt validated"

**모호한 점:** plan이 target 밖에만 보존된다면(692행), clone이나 read-only 판독자는 plan 없이 무엇을 검증할 수 있는지 문서만으로 알 수 없습니다. receipt가 canonical plan 전체나 그 digest를 내장하는지는 source 확인이 필요합니다.

**최소 수정:** 구별을 한 문장으로 적습니다. mutation recovery는 외부 plan/token과 원 target을 사용하고, read-only audit는 receipt 내부 목록·링크·실제 prefix만 사용한다.

#### D06-F6 · P3 · A14가 과거 코드에 행동 의무를 부과함

**근거:** 734행 "an older plain-audit fixture that does not understand detach4 must report it unavailable, not PASS"는 이미 존재하는 과거 reader의 동작을 계약으로 강제하는 형태입니다.

**최소 수정:** 이를 qualification 확인 항목으로 바꿉니다. 과거 reader가 PASS류 결과를 내면 A5/A13의 노출 처분(검증된 거절 또는 비노출 근거)을 적용한다고 연결합니다.

#### D06-F7 · P3 · 조건부 · windows-1 launcher literal의 생성 경로

**근거**
- 360행: source init은 launcher declaration을 읽어 candidate를 만든다.
- 600행: windows-1 launcher literal
- 720행: "Package its literal launcher window"
- 170행: macOS 기본 동작 불변

**우려:** 한 source checkout의 root `colvia`가 entry-1을 선언한다면, `--profile windows-1` init이 windows-1 candidate를 만드는 방식이 문서에 없습니다. 가능한 방식은 별도 windows-1 source·artifact이거나 profile 기반 literal 생성입니다.

**영향:** 이 선택은 macOS default 불변성과 A13의 byte identity에 영향을 줍니다.

**처분:** Driver의 source 대조가 필요합니다. 어느 방식이든 artifact identity 의미가 바뀌면 문안에 넣고, 바뀌지 않으면 계획 세부로 둡니다.

#### D06-F8 · P3 · 요약 정렬

- **S2 요약:** 176·183행의 old-writer 요약은 "실행 불가"와 "노출 불명은 비노출이 아님"을 생략합니다. 405행과 A5의 표현으로 맞추는 것이 좋습니다.
- **criterion 2 mapping:** 754행 행이 repair를 빠뜨립니다. S2 범위와 A13에는 포함되어 있으므로 맞춰 적는 것이 좋습니다.

---

## 3. 8사례 compact table

| # | 이미 정합한 의미 | 남은 문안 / Owner 선택 | 이후 구현·qualification 증거 |
|---|---|---|---|
| 1 old writer | 미확인·실행 불가·실제 발행 모두 qualification/activation을 닫지 못함. 검증된 거절 또는 증거 있는 비노출. unknown≠비노출. bounded 집합과 전체 역사 회수 gate 구별 (405, A5, A13, 792) | S2 요약 정렬(F8), A14 과거 reader 문구(F6) | 실제 노출 writer 집합·identity 고정, 경로별 거절 실행 결과 |
| 2 detach4 | 기존 complete 목록 재사용. 29는 release별 payload. launcher/init plan/binding/receipt/inventory 포함. 내부 링크. suffix·안전한 부재·ordered directory prefix·보존 bytes/graph. 재해시 불가와 trusted-local의 durable 결속. clone 대 mutation recovery 구별 (580–586, 643) | read-only 관리 파일 제거 규칙(F1). 판독 주체별 입력(F5) | delete-pending·열린 handle 상태가 unknown/non-pass로 남고 재호출로 해소되는지, 중단 suffix, 디렉터리 순서 |
| 3 repair mode | windows-1 repair1 한정 READONLY 0/1, bool·다른 값·unavailable 거절, stat·TreeEntry·ACL·실행 의미와 분리, 기존 field 유지, 같은 window 양방향 reader (651–655) | 없음. F1이 lifecycle 연결부를 다룸 | window를 먼저 확정한 뒤 mode를 판독하는 순서, old source가 windows-1 request를 거절하는지 |
| 4 before/after | missing=null, after=candidate bytes, mode=before.mode 또는 0, launcher 동일 규칙, before≠after, permission-only repair 없음, drift, initial-before/recover-before-or-after, backup+request, all-after 뒤 receipt, 독립 검사 (653–659) | 반례 없음 | 속성 drift fixture, replay 실패 사례 |
| 5 replace 불가 | ACL·ownership·delete-copy 금지는 정상적인 좁은 범위 | **중간 prefix 영구 막힘(F1)**. 사전 거절안 또는 해제 전이 수락 중 선택 | read-only 대상에서의 실제 API 결과(미재현) |
| 6 A1–A15 qualifier | Workspace(A8), Structure(A9), Reference(A12)가 지정 문장을 한정. 상호 참조 heading이 내부에 모두 존재. CRLF는 A2·A9·A10에서 같은 증명 아래 확장. Security가 runtime 정본. 새 Windows 경로와 entry-1 source 구별 (175, 400, A8, A12) | filesystem gate(F2), 784행(F3), map(F4) | target 원문 heading·위치 대조(미제공) |
| 7 worker | 공통 조건과 모든 guard의 교집합, 열린 예시, index-only add, tracked 삭제와 잔존 index, alias·type·reparse non-pass, whole-result 재관측, mode-change와 새 untracked 755 거절, drift·reject·pending·cancel·replay (275–301, A2) | 반례 없음 | 분류와 특수 flag, 성공·거절 fixture |
| 8 B | 대표 UTM 전체, x64·물리 focused, Preview 이후 formal admission, 미관측 tuple 보존, criteria 5/8 교체와 6–9 유지 (A6, A3, A4, A13) | 반례 없음. 새 matrix·gate 불필요 | 실제 tuple과 budget |

---

## 4. 수락 전 보완 대 이후 증거

**수락 전 문서 보완 또는 Owner 선택**
- F1: read-only lifecycle 규칙. 사전 거절안 또는 해제 전이 중 선택.
- F2: filesystem gate. 권고는 (a).
- F3: 784행 상태 문구 교체.
- 선택 보완: F4–F8. 이 중 F7은 Driver의 source 대조 결과에 따라 문안으로 올릴지 정합니다.

**이후 실제 증거 (문서 결함 아님)**
- artifact digest
- 노출 writer 실행 결과
- Windows API 동작: replace, delete-pending, flush, lock
- runtime·emulation 판별
- PowerShell 5.1 입력 보존
- 전체 regression과 focused 검증

**반례가 없는 부분**
- 공통 조건 worker 전체
- B 배정과 timing
- old-writer 처분의 핵심 의미
- detach4의 재해시 불가와 trusted-local 설명
- repair 0/1의 field 의미와 POSIX 보존
- A1–A15 상호 참조의 내부 존재
- CRLF 확장과 Security 정본 참조

---

## 5. 읽지 못한 근거와 잔여 한계

**제공되지 않아 읽지 못한 것**
- 링크된 target 원문: Structure, Workspace, General Work, Reference, Maintaining, Manual Operation, Security, Development Index
- 제품 source
- R1-D05 원문과 D05-D1
- probe 원출력

**그 결과 확인하지 못한 사항**
- heading 실재, 삽입 위치, 기존 문장(entry-1-only profile, schema-3 detach, launcher-0755, pending 예외)의 정확성
- receipt가 plan을 내장하는지(F5)
- launcher declaration 생성 방식(F7)
- 현행 설치가 chmod를 쓰는지(F1의 보조 우려)

**추가 한계**
- Windows API 동작은 일반 지식 수준으로만 언급했고 재현하지 않았습니다.
- F1의 핵심 반례는 API 결과와 무관하게 문서 자체의 "실패 가능 + 해제 금지 + drift" 조합에서 성립합니다.
- activation 이후에 새로 발견되는 노출 writer의 처분은 이 문서 범위 밖입니다.

이 리뷰는 PASS나 재현 결과를 만들지 않았으며, Driver의 개별 처분과 Owner 수락을 대신하지 않습니다.
````

### R1-D06 Record Verification And Retention

검증: 작성 기록을 포함한 3개 문서의 marked 17.0.5 GFM 렌더링, code 밖 literal 강조 기호·whitespace·공개용 식별자 경계, local path/heading link 84개를 확인했다. 8개 frozen review round의 request/packet/final hash와 원문, 8개 Driver 처분, reviewed v0.6의 불변·packet exact 복구, 기존 CHORE bytes, S1–S8·열 가지 기준·15개 amendment·비어 있는 accepted-only 절과 나머지 baseline/source/navigation diff 보존을 확인했다. 제품 실행이나 Windows qualification은 하지 않았다.

Owner 처분과 다음 exact revision 비교를 위해 request/packet/inputs/final/metadata/고정 실행기를 유지한다. 실행기는 동일한 제한을 확인할 다음 리뷰 준비의 입력이며 새 호출 권한을 만들지 않는다. duplicate partial, empty stderr/tool-temp, 일회성 checker/report는 최종 응답·기록 검증과 no-use 확인 뒤 정리한다. 기존 worktree·VM·probe 원출력·마지막 복구 사본은 기존 결과 수락·복원 확인·구체 후속 작업 목적을 유지한다.

정리 완료: CLI 종료·partial/final 일치·stderr/temp 비어 있음·no-use를 확인해 위 일회성 항목 5개를 삭제했다. 필수 리뷰 6개 파일과 기존 증거는 보존했으며 active path는 바꾸지 않았다. 삭제와 최종 기록 갱신 뒤 동일 검증을 다시 실행했고 일회성 출력은 재생성하지 않았다.


## Contract Draft Revision 0.7 — 2026-10-18

Owner는 “리뷰 결과와 네 권고를 반영해 DR-0007을 v0.7로 보완해줘. read-only 파일의 생성·교체·제거 정책과 NTFS mutation 검사 경계를 명확히 하고, repair 재시도와 새 preview의 구분, 남은 상태 문구·대응표도 정리해줘. B안과 공통 조건 중심 worker 지원은 유지하고 추가 실험이나 제품 구현은 시작하지 마.”라고 요청했다. 변경은 DR-0007과 이 기존 진행 기록·private 보존 맥락에 한정한다. Draft 수락·발효, 제품 실행, 추가 reviewer·실험·Git publication은 포함하지 않는다.

[DR-0007 Draft 0.7](../decisions/DR-0007-windows-native-runtime-contract.md)의 현재 identity는 161,600 bytes, SHA-256 `3fc5737cc87fe7e07649d31e5298b7dde7598cff087980f0821ad5c4e4a75afe`다. R1-D06의 v0.6 exact 입력·원문·Driver 처분은 그대로 보존했다. 새 문안은 미리뷰·미수락 후보다.

### Revision Scope And Remaining Authority

- D06-F1: 새 Windows 파일의 read-only clear 생성, 교체·제거 대상 전체의 durable publication 전 거절을 제안한다. existing/preserve-only 파일 정규화나 read-only 해제 동작은 추가하지 않는다. 검사 뒤 drift·부분 실패는 보존한 non-pass다.
- D06-F1의 repair 해석: mode 0/1 관측은 유지하되 실행 가능한 request는 writable/missing before와 after 0이다. 원 request·token·backup의 exact 재시도와, 실제 product pending이 없고 모든 기존 guard를 만족할 때 별도 새 preview가 가능한 경우를 구별한다. 원 evidence 보존·새 operation/request/token/backup·해당 apply 승인을 명시하며 영구 교착이나 자동 복구 성공은 주장하지 않는다.
- D06-F2: native local NTFS를 target·staging·lock/scratch·외부 backup의 실제 mutation 검사 조건으로 명시했다. 표준 사용자 qualification 조건, fixed drive 조건, 모든 backup의 단일 volume 요구와 혼동하지 않는다.
- D06-F3/F4: 오래된 v0.5 미리뷰 문장을 수정하고 R1-D06/v0.7 상태 및 A14의 첫 named map을 정렬했다.
- D06-F5/F6: detach4의 embedded complete plan 읽기와 original-plan/token mutation recovery를 구별했다. 과거 reader의 실제 동작을 규범만으로 바꾸지 않고 compatible qualified reader 증거를 요구한다.
- D06-F7/F8: Windows literal/payload는 candidate 생성 전 명시적으로 준비하고 OS/profile로 bytes를 변경하지 않는다. 공통 source로부터 Windows source를 준비하는 단계가 있으면 이를 먼저 식별하고 이후 source/artifact/published/refetched bytes의 기존 equality 의무를 유지한다. S2 repair는 기존 criterion 2의 원 열거와 구별되는 추가 검증 의무로 대응했다.

B, 공통 조건 중심 worker, windows-1/29 paths/pairs, old-writer 미확인 처분, 기존 quote·review 원문과 historical revision은 유지했다. 새 read-only 사전 거절과 NTFS 문안도 exact 계약 수락 대상이다. 지원 증거·제품 구현·Windows qualification·activation은 여전히 없다. STATUS/catalog/PLAN 및 normative 문서 cascade는 Draft 단계여서 수행하지 않는다.

### Revision Verification And Preservation

- PASS: 세 문서 GFM(marked 17.0.5) 렌더링, code 밖 literal 강조 기호 없음, local path/heading link 88개, whitespace/disclosure 검사.
- PASS: A1–A15를 11개 target의 메모리 사본에만 적용해 정확한 위치·block·렌더링 확인. 실제 normative 파일은 변경하지 않았다. old-reader/repair/NTFS/read-only와 상태 문구의 의미는 Driver가 정적으로 대조했으며 자동 검사가 의미의 완전성을 증명하지는 않는다.
- PASS: 29-member 목록은 source AST와 일치하며 제품 import 없이 확인. 8개 선택·10개 admission 대응·빈 수락 전용 절, 12개 보호 절과 기존 Owner 인용을 유지했다.
- PASS: R0/R1-P01/R1-D01–D06 frozen packet/request/최종 응답과 source 내 원문 보존. v0.6 exact packet 복구와 v0.7 bounded diff 대조. baseline 42개 중 승인된 세 기록 밖의 input bytes, source HEAD와 기존 tracked navigation diff는 불변.
- 실행 경계: 새 probe·VM·제품 suite·reviewer·지원 qualification을 실행하지 않았고 product/normative/STATUS/catalog/PLAN/Git publication 변경은 없다. v0.7은 여전히 Draft·미리뷰·미수락이다.

revision 입력·diff와 이전 리뷰/실험 원증거는 Owner 비교·다음 exact 문안 판단에 필요해 보존한다. 현재 worktree와 마지막 복구 copy는 기존 수락·복구점 확인·후속 작업의 구체 consumer가 남아 있어 유지한다. 일회성 작성·검사 파일은 결과를 이 기록에 남긴 뒤 no-use 확인 후 정리하며 active path는 변경하지 않는다.

정리 완료: 사용 중인 프로세스가 없음을 확인하고 이번 개정의 일회성 작성 스크립트 2개·검사 스크립트·중복 검사 보고서 총 4개를 삭제했다. 검증 결과는 위에 보존했다. 비교 입력과 revision diff, 현재 Draft, 원 리뷰·실험·필요한 복구 자료는 유지했고 active path 변경은 없다. 삭제 뒤 같은 문서/보존 검사를 메모리에서 다시 실행해 PASS를 확인했다.


## R1-D07 Draft 0.7 Re-review And Driver Judgment — 2026-10-18

### Request, Identity And Execution

Owner는 “DR-0007 v0.7을 Claude CLI로 재리뷰해줘. read-only 생성·교체·제거 정책, NTFS mutation 검사 경계, repair 재시도와 새 preview 구분, A1–A15의 일관성을 확인하고 네 판단도 정리해줘. B안과 공통 조건 중심 worker 지원은 유지하고 추가 실험이나 제품 구현은 시작하지 마.”라고 요청했다. 지정 Draft 한 건의 정적 재리뷰와 Driver 판단만 수행한다. 계약 개정·수락·제품 구현·추가 실험·후속 reviewer 실행은 이 요청에 포함하지 않는다.

| 항목 | 실제 입력·결과 |
| --- | --- |
| 역할 | Driver Codex, Reviewer fresh Claude CLI, Owner 최종 선택·수락 |
| 대상 | [DR-0007 Draft 0.7](../decisions/DR-0007-windows-native-runtime-contract.md), 161,600 bytes, SHA-256 `3fc5737cc87fe7e07649d31e5298b7dde7598cff087980f0821ad5c4e4a75afe` |
| source / diff | baseline `a93f71c359c4f0a9d57fcfb50d5999160e870f77`, tracked diff SHA-256 `91f501b2077cfc175ae80edbddd2f56a32b71c2bcb6c6b7c1659d01c3e42a7ef`; untracked 대상 문서는 packet에 전부 포함 |
| 전송 범위 | 번호를 붙인 지정 Draft만 전송. 링크된 계약·제품 source·실험 원출력·이전 리뷰 원문 미전송 |
| packet / request | packet 166,408 bytes, SHA-256 `eac7da4fecbd7421208cdeea2b056f5c8879b1eb48821d7bfa15fdb7a3c0ceae`; request SHA-256 `9eebe3a72251d42cba650298c9f98e6b0cd60d4301016ee255e9c4d1f23d4283` |
| Reviewer identity | Claude Opus 5.5, reported model `claude-opus-5-5`; CLI `2.1.302`; fresh session `7c69a461-a33f-4d48-807c-5b6dcd1f0fc8` |
| 인증·과금 경로 | `claude.ai / firstParty / pro`; provider override 없음. 키·토큰·이메일 미기록 |
| 실행 경계 | 고정 packet stdin, no tools, strict empty MCP, no Chrome/session persistence, permission prompts none; 상한 1,200초 |
| 실행 결과 | 2026-10-17 23:59:41–2026-10-18 00:03:09 UTC, 207.757초, exit 0, tool events 0, 입력 전후 drift 없음 |
| 최종 응답 | 16,177 bytes, SHA-256 `0d1fc7e4200315058078351a6bbf421df0d9c7db7897da9bca0dc22bc0dfe44a`; 아래 원문 그대로 보존 |

Reviewer는 source·target 원문·플랫폼 문서를 독립 확인하지 않았다. 아래 source와 Microsoft 문서 대조는 Driver의 별도 정적 확인이다. 새 Windows 실행·반례 재현·qualification PASS를 만들지 않았다. 직접 CLI 호출은 Owner의 명시 요청에 따른 것이며 fresh session과 도구 제한이 리뷰의 완전성을 보장하지는 않는다.

### R1-D07 Verdict And Driver Assessment

| 범위 | Reviewer | Driver 판단 |
| --- | --- | --- |
| 전체 exact 수락 준비도 | conditional | 동의. A12 수락 본문 범위, repair 예시, 필수 flush 대상의 사전 검사 범위를 문서에서 먼저 보완할 필요 |
| read-only 생성·교체·제거 | conditional | 생성 clear·operation 전체 사전 거절·detach 발행 순서는 유지. 필수 write-capable flush만 하는 기존 파일도 검사 범위에서 빠지지 않아야 함 |
| NTFS mutation 경계 | approve | 동의. 실제 target·staging·guard scratch·external backup 경계, 다른 admitted backup volume, unknown non-pass가 정합. 새 fixed-drive/admin-token gate 불필요 |
| repair retry / 새 preview | conditional | 설계 방향 유지. read-only 교체 대상이 남으면 새 preview도 non-pass임을 예시에 직접 명시해야 함 |
| A1–A15 | conditional | A12 영어 단락이 exact fence 밖인 실제 결함 확인. 나머지 map·window·pair·본문 관계에서 이번 범위의 새 반례는 찾지 못함 |
| B / 공통 조건 worker / 문서 계획 | approve | 동의. 대표 UTM full과 필요한 focused 보완, 열린 worker 예시와 공통 조건 유지. 새 전체 matrix나 실험을 기본 해결책으로 추가하지 않음 |

Reviewer는 P1 없음, P2 세 건(F3은 source 조건부), P3 네 건을 제시했다. 이는 재현한 제품 defect 수가 아니다. Driver는 F1·F2·F4·F7 accept, F3 revise, F5·F6 defend로 처분한다. reviewed v0.7 bytes는 고정하며 아래 권고를 자동 반영하지 않는다.

### R1-D07 Finding Dispositions

| Finding | Driver disposition | 판단·권고 | 경계 |
| --- | --- | --- | --- |
| F1 · P2 · A12 fence 밖 본문 | accept | 771행 영어 단락이 769행 닫힌 fence 뒤에 있다. A1–A15를 exact 영어 개정 본문으로 정의했으므로 수락 대상이 모호하다. 다음 문서 개정에서 A12 fence 안으로 옮길 것을 권고 | 지난 in-memory 적용·GFM 검증은 fence 안 추출분의 위치·렌더링을 확인했지만 바깥의 의도된 본문 누락을 잡지 못했다. 이전 PASS를 의미적 완전성 검증으로 확대하지 않음 |
| F2 · P2 · read-only drift와 새 preview | accept | 교체가 필요한 mode 1 파일이 남아 있으면 새 preview도 non-pass이며 실행 request/token이 없다. 새 preview는 현재 상태의 모든 guard를 충족하고 남은 손상 집합에 read-only 교체 대상이 없을 때만 후보가 된다. 외부에서 flag가 원 before로 되돌아오면 원 exact retry도 다시 판정할 수 있으나 전체 before/after·backup·candidate·binding·prefix 일치가 필요 | 속성 복원을 제품 기능이나 권장 우회로 만들지 않는다. 복원만으로 retry 성공을 보장하지 않으며 자동 새 preview·기존 evidence 삭제·원 request 변경도 없음 |
| F3 · P2 · 비교체 기존 파일의 필수 flush | revise | 문제의 범주는 source에서 확인된다. 기존 exact 파일에 fsync하는 helper가 init의 기존 staging/receipt/launcher와 repair의 외부 request/original 재확인에 쓰인다. 따라서 교체·제거 집합 외에 해당 operation의 필수 flush 때문에 write-capable open이 필요한 기존 파일도 첫 durable publication 전 사전 검사 대상으로 명시할 것을 권고 | 모든 retained release를 switch2/repair가 flush한다는 Reviewer 예시는 이 source 확인으로 입증되지 않는다. 필요한 동기화를 조용히 생략하지 않으며 순수 read/preserve 파일 전체로 gate를 확장하지 않는다. 정확한 call-site 목록은 계획에서 닫고 Windows 실행은 이후 qualification |
| F4 · P3 · read-only 면제와 completed replay | accept | read/preserve-only 면제는 새 mutation gate의 면제일 뿐, repair의 bound before/after 관측을 면제하지 않는다고 명시하면 좋다. 완료 뒤 after.mode 0이 1로 바뀌면 completed replay는 drift non-pass다 | completed replay에 새 mutation/flush를 추가하지 않음. 기존 exact 관측 의미를 분명히 하는 문안 |
| F5 · P3 · 디렉터리 read-only 제거 | defend | Microsoft File Attribute Constants는 READONLY가 디렉터리에는 적용되지 않는다고 명시한다. 따라서 파일 flag만으로 managed directory 제거를 사전 거절하는 새 정책을 넣을 근거가 없다 | type·empty·identity·access 검사와 실제 RemoveDirectory 실패 보존은 유지. 문서 대조는 실제 guest/API 실행 증거가 아니며 이후 선택 API의 qualification에서 확인 |
| F6 · P3 · repair receipt 위치 | defend | 현 Workspace 계약과 product source 모두 `receipt.json`을 external backup 안에 둔다. target lifecycle history의 receipt라는 조건부 전제는 해당하지 않는다. external backup/receipt가 pending authority가 아니라는 현 문구를 유지 | lifecycle-receipt record type과 binding-selection authority 소속은 다르다. detach의 target remove set에 외부 repair backup을 넣지 않음 |
| F7 · P3 · standard-user policy 문장 | accept | A6 첫 문장은 native local NTFS를 지원 경계로 두고 standard-user는 qualification 환경이라고 분리하면 A7/A10과 더 명확히 맞는다 | 이미 명시된 의미를 정리하는 보완. elevated 실행의 qualification 미충족과 제품 admin-token 거절을 혼동하지 않음 |

### R1-D07 Local Static And Platform-Document Checks By Driver

1. **필수 flush 범위:** `workspace.py:375–383`의 `_write_exact`는 bytes가 같은 기존 파일에도 read-only descriptor로 `os.fsync`를 호출한다. `product.py:1154,1163,1165,1168,1171`의 init 경로와 `1731,1736`의 repair recovery backup 경로가 이를 사용한다. `1471–1495`의 same-window switch 기존 staging/receipt 경로도 이 helper를 사용하지만, 이미 게시된 retained release 전체를 항상 reflush한다고 읽지는 않는다. transition 전용 `_entry_write_exact`와 resync는 별도 경로다. existing immutable file을 “교체하지 않으므로 순수 read-only”로 일괄 분류하면 필요한 동기화가 누락될 수 있다.
2. **플랫폼 근거와 한계:** Microsoft의 [FlushFileBuffers](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers)는 file handle에 `GENERIC_WRITE`가 필요하다고 규정한다. [File Attribute Constants](https://learn.microsoft.com/en-us/windows/win32/fileio/file-attribute-constants)는 READONLY 파일의 쓰기·삭제 제한과 디렉터리에는 그 속성이 적용되지 않는다는 의미를 구별한다. 2026-10-18 조회한 공식 API 계약에 근거해 F3의 사전 검사 범주를 권고하고 F5의 무조건 확장을 채택하지 않았다. 실제 선택 handle/API·guest에서의 오류·순서는 재실행하지 않았다. [RemoveDirectoryW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-removedirectoryw)의 디렉터리 제거 조건과 실제 access 실패는 파일 속성 gate와 별도로 남는다.
3. **Repair receipt와 재시도:** [Workspace — Exact Active Repair](../WORKSPACE-CONTRACT.md#exact-active-repair)는 external backup의 request, originals, 성공 후 receipt와 read-only replay를 명시한다. `product.py:1555–1556` 주석 및 `1709,1726–1729,1753`의 위치·검사는 이를 구현한다. 외부 backup 존재는 target pending authority가 아니지만, 새 preview는 현재 product/candidate/prefix와 v0.7 read-only 지원 조건을 모두 만족해야 한다. mode drift를 새 preview로 자동 우회하는 의미는 아니다.
4. **A1–A15와 검증 한계:** v0.7의 15개 target mapping과 당시 고정된 11개 target 원문은 변하지 않았다. A12 fence 밖 영어 문단은 실제 확인된 exact-본문 위치 오류다. 이전 11개 in-memory 사본의 구조/렌더링 확인은 이 누락을 검출하지 못했다. Windows window/pair, embedded complete detach plan, old-reader 증거 처분, explicit Windows source/payload 준비의 핵심 의미에 이번 확인 범위의 추가 반례는 없다. 이 서술은 전 계약의 완전성 증명이나 실제 제품 상호운용 PASS가 아니다.

### R1-D07 Remaining Before Contract Acceptance

Driver 권고는 B안과 공통 조건 중심 worker 지원, windows-1·detach4·repair mode 0/1의 현재 방향을 유지하고 아래 문안만 먼저 다듬는 것이다.

- A12 누락 단락을 exact fence 안에 넣는다.
- repair 예시에서 read-only가 남은 새 preview도 non-pass라는 점과, 원 before가 복원돼도 원 retry의 모든 guard를 다시 판단해야 한다는 점을 명시한다. read/preserve 면제가 bound observation 비교를 없애지 않음도 함께 적는다.
- 교체·제거 외에 필수 write-capable flush가 필요한 기존 파일을 operation 전체 사전 검사 범위에 포함하는 권고를 S3/S6/A7과 대응 문안에 일관되게 제시한다. 새 read-only 동작·동기화 생략·모든 reader의 NTFS gate로 바꾸지 않는다. 이는 exact 계약 보완 대상이며 아직 Owner가 선택한 실행 정책이 아니다.
- A6의 filesystem 지원 경계와 standard-user qualification 표현을 분리한다. 디렉터리 파일-flag gate나 repair receipt 위치 변경은 넣지 않는다.

이후 실제 API·PowerShell 입력·old-writer 노출/거절·artifact 및 B의 full/focused qualification 증거가 필요하다. 이번 리뷰에서 새 실험·새 full matrix·추가 worker 제한을 기본 gate로 추가할 이유는 찾지 못했다. S1–S8 및 열 가지 admission 기준의 최종 선택은 그대로 남는다.

이번 라운드는 리뷰와 판단 정리로 끝낸다. DR-0007 v0.7, normative 계약, 제품 source, STATUS·catalog·PLAN, VM과 기존 probe 결과는 변경하지 않았다. 계약 수락·구현·Git publication·추가 reviewer를 수행하거나 승인한 것으로 기록하지 않는다.

### R1-D07 Reviewer Final — Verbatim

````markdown
# R1-D07 — DR-0007 Draft 0.7 정적 재리뷰 (Reviewer)

이번 리뷰는 packet에 포함된 DR-0007 v0.7(161,600 bytes, 지정 SHA-256) 한 문서만 정적으로 읽은 결과입니다. 도구 실행, 파일 접근, source 대조, test는 하지 않았습니다. 문서에 인용된 source와 계약 사실은 독립 확인 결과가 아니라 보고된 주장으로 취급했습니다. 아래 판정은 Owner의 계약 수락, 제품 실행 승인, activation 중 어느 것도 대신하지 않습니다.

## 1. Verdict

| 범위 | 판정 | 요지 |
| --- | --- | --- |
| 전체 exact 수락 준비도 | **conditional** | P1은 없습니다. P2 세 건 가운데 두 건은 짧은 문안 수정이고, 한 건은 source 확인 뒤 필요할 경우 Owner 선택이 필요합니다. |
| read-only 생성·교체·제거 | **conditional** | 생성 규칙, operation 전체 사전 거절, detach와 recovery 순서는 정합합니다. 다만 교체하지 않는 기존 파일의 필수 flush 경계(F3)가 비어 있습니다. |
| NTFS mutation 경계 | **approve** | 반례를 찾지 못했습니다. fixed-drive 조건이나 admin-token gate가 몰래 추가되지도 않았습니다. |
| repair retry/새 preview | **conditional** | 의미 구조는 맞습니다. 그러나 대표 예시가 새 preview로 해소된다고 오해하게 만듭니다(F2). |
| A1–A15 정합성 | **conditional** | A12의 영어 단락 하나가 exact fence 밖에 있습니다(F1). 나머지 상호 참조는 정합합니다. |
| B/공통 조건 worker | **approve** | read-only와 NTFS 보완이 이 방향을 닫지 않습니다. |
| 문서 기반 계획 준비 | **approve** | 계약과 계획을 함께 준비하는 데 막힘이 없습니다. 미래 artifact digest를 이유로 한 순환 의존도 없습니다. |

## 2. Findings

### D07-F1 · P2 · Must-fix (문안 위치)

- **위치:** A12의 markdown fence는 759–769줄에서 닫힙니다. 그 바로 뒤 771줄의 영어 단락 “An existing read-only replacement/removal target is policy-level unsupported … no new command, automatic fallback or generic permission-clearing action is introduced.”는 **fence 밖**에 있습니다.
- **오해 경로:**
  - 485줄은 A1–A15를 “지정 위치에 넣을 정확한 영어 개정 본문”이라고 정의합니다.
  - 862줄은 영어 amendment를 메모리 사본에 적용해 검증했다고 적습니다.
  - fenced block만 기계적으로 적용하면 Reference에서 다음 내용이 빠집니다: read-only의 policy-level unsupported/unknown/drift/실제 실패 구분, guard scratch·backup의 NTFS 적용, repair retry와 새 preview의 구분.
  - 반대로 단락 전체를 포함하면, 같은 수준의 Korean 설명문들과 권위 구분이 흐려집니다.
  - 그 결과 수락 대상 bytes가 모호해집니다.
- **최소 수정:** 771줄을 A12 fence 안(768줄 뒤)으로 옮깁니다. 의도적으로 비규범 설명이라면 한국어 주석으로 바꿉니다.

### D07-F2 · P2 · Must-fix (구체 오해 경로)

- **위치:**
  - 374줄: “두 번째 파일의 read-only flag가 달라지면 … 같은 recovery는 거절한다 … 이것만으로 모든 새 preview를 금지하거나 영구 교착이라고 단정하지 않는다.”
  - 344줄: “원 request와 맞지 않는 속성 변경은 … 허용하지 않는다. 외부 backup은 … 별도 새 preview를 만들 가능성은 남는다.”
  - A11 750줄도 같은 결합을 씁니다.
- **반례:**
  1. 실행 가능한 원 request에서 해당 파일의 before는 0입니다(707줄).
  2. 따라서 “flag가 달라졌다”는 현재 값이 1이라는 뜻입니다.
  3. 그런데 A9 707줄에 따르면, 교체가 필요한 mode 1 파일이 있는 preview는 non-pass이고 실행 request/token이 없습니다.
  4. 결국 문서가 든 바로 그 예시에서는 새 preview도 실행 불가입니다.
  5. 사용자가 product 밖에서 flag를 0으로 되돌리면 원 before와 다시 일치합니다. 이때는 원 request의 exact 재시도가 길이 되고, 새 preview는 필요 없습니다.
- **결과:** 본문은 “가능성은 남는다”, “단정하지 않는다”로 표현이 조건부라서 직접 모순은 아닙니다. 하지만 예시와 결론의 결합은 독자에게 “read-only drift는 새 preview로 우회할 수 있다”는 잘못된 경로를 줍니다. 영구 교착을 주장하지 않는다는 목표 자체는 맞습니다.
- **최소 수정:** 374줄(그리고 344·750줄)에 한 문장을 추가합니다.
  - 교체가 필요한 대상이 read-only로 남아 있는 동안에는 새 preview도 non-pass이며 token이 없습니다.
  - 새 preview 경로는 남은 손상 집합에 read-only 교체 대상이 없을 때(예: bytes drift, 다른 손상)에만 해당합니다.
  - flag가 원 before로 복원되면 원 request의 exact 재시도가 다시 판정 대상입니다. 이 복원은 product 동작이 아닙니다.
  - 새 절차나 새 명령은 필요 없습니다.

### D07-F3 · P2 · 조건부 (source 확인 뒤 Owner 선택 가능)

- **위치:**
  - 236줄: “fresh init launcher와 immutable member 재확인에 남아 있는 read-only fsync도 계획에 포함한다.”
  - A7 600줄: “File and required directory flushes use explicit results from appropriate write-capable handles … including init launcher and immutable-member revalidation”, “Required failure or unavailable is non-pass.”
  - A7 608·610줄: 사전 검사 대상은 replace/remove 집합뿐이고, “Files only read or preserved unchanged are not refused solely for being read-only.”
- **반례:**
  1. windows-1 writer가 만든 기존 retained release member에 사용자가 나중에 read-only를 설정합니다.
  2. switch2나 repair가 이 파일을 교체하지는 않고, immutable 재확인에서 필수 flush만 수행합니다.
  3. Windows에서는 read-only 속성 파일에 write-capable handle을 열 수 없으므로 필수 flush가 실패합니다. 이 플랫폼 동작은 qualification에서 확인해야 합니다.
  4. 이 파일은 사전 거절 집합에 없습니다. 그래서 실패가 “policy-level unsupported”로 분류되지 않습니다.
  5. 대신 sync failure로 나타납니다. 그 call site가 발행 뒤라면 race가 아닌데도 예측 가능한 부분 prefix가 생깁니다.
  6. 동시에 610줄의 “read-only라는 이유만으로 실패하지 않는다”와 실질적으로 충돌합니다.
- **조건:** 재확인 flush가 교체되지 않는 기존 파일에 대해 mutation operation 안에서 수행되는지는 source에서 확인해야 합니다. 해당 call site가 없다면 문서 결함이 아닙니다.
- **최소 수정(해당 시):** A7에 한 문장을 둡니다.
  - 필수 flush 때문에 write-capable open이 필요한 기존 비교체 파일도 첫 durable publication 전 사전 검사 집합에 포함합니다(read-only면 operation 전체 unsupported).
  - 또는 Owner가 다른 대응을 선택합니다.
  - 정확한 call site 목록은 계획 세부로 둡니다.

### D07-F4 · P3 · 선택 보완

- **위치:** A7 610줄 “Files only read or preserved unchanged are not refused solely for being read-only”와 A9 711줄 “Completed replay requires … each actual target observation equal to its after.”
- **오해 경로:** repair 완료 뒤 사용자가 복구된 파일을 read-only로 바꾸면, completed replay는 after.mode 0과 불일치하므로 non-pass입니다. 이는 POSIX의 chmod drift와 같은 기존 의미이므로 올바릅니다. 그러나 610줄을 문자 그대로 읽으면 “읽기만 하는 replay인데 read-only라서 거절됐다”는 충돌로 보일 수 있습니다.
- **최소 수정:** 610줄에 “this exemption concerns the mutation gate; it does not waive bound observations such as Windows Exact Repair Observation”을 추가합니다.

### D07-F5 · P3 · 조건부 (플랫폼 확인 필요)

- **위치:** 334·610줄 “디렉터리는 기존 type·empty·identity·access 검사를 따르며 …”와 A8 630줄 “remove … verified-empty managed directories”.
- **우려:**
  - Windows에서 read-only 속성 디렉터리의 RemoveDirectory가 거절될 수 있습니다. 이번 리뷰에서는 확인하지 않았습니다.
  - 그 경우 detach4는 detached.json 발행 뒤에 race가 아닌 예측 가능한 실패를 겪습니다.
  - 문서는 이를 “사전 검사 뒤 예상치 못한 실패”로만 다루므로, 사전 거절 원칙과 결이 다릅니다.
- **최소 수정:**
  - 플랫폼 동작이 확인되면, 제거할 managed directory의 속성도 detach 사전 검사에 포함합니다.
  - 아니면 발행 후 non-pass로 수용한다는 사실을 한 줄로 명시합니다.
  - 동작이 확인되지 않으면 qualification 항목으로 둡니다.

### D07-F6 · P3 · 선택 보완 (source 조건부)

- **위치:** A9 715줄 “The external repair backup/receipt is evidence, not a pending node”와 A8 628줄 “every lifecycle receipt”(remove set).
- **오해 경로:** 완료된 repair receipt가 target 안의 lifecycle receipt라면, 그것을 “external … evidence”로 묶는 것은 부정확합니다. 실패한 repair 상황에서 남는 것은 외부 backup과 request뿐입니다.
- **최소 수정:** “The external repair backup and its request copy …”로 한정합니다. receipt의 위치는 source로 확인합니다.

### D07-F7 · P3 · 선택 보완

- **위치:** A6 580줄 “The initial policy targets … on standard-user local/guest NTFS.”
- **오해 경로:**
  - 582줄과 A10 726줄은 standard-user를 증거 경계로 분리하고, admin-token gate를 부정합니다.
  - 그런데 580줄은 standard-user를 policy target 문장 안에 넣었습니다.
  - 그래서 “elevated 실행은 정책상 거절한다”로 읽힐 여지가 있습니다.
- **최소 수정:** 580줄을 “on native local NTFS; standard-user execution is the qualification environment (below)”로 바꿉니다.

## 3. 8사례 compact table

| 사례 | 이미 정합한 의미 | 남은 문안 / Owner 선택 | 이후 구현·qualification 증거 |
| --- | --- | --- | --- |
| 1 read-only 생성 | 330·606줄에서 대상(runtime·authority·receipt·content·staging/scratch·backup)을 열거합니다. immutability·confidentiality·완료와 구별하고, 기존 파일·source·preserve-only는 정규화하지 않습니다. | F3(비교체 파일의 필수 flush)과 F4(면제 범위). 다른 integrity 의무와의 문구 충돌은 찾지 못했습니다. | 새 파일 read-only clear 관측, staging after=0 |
| 2 교체/제거 | 첫 durable publication 전 operation 전체 검사. detach는 detached.json 전에 complete remove set을, recovery는 남은 suffix를 검사합니다. unknown, drift, 실제 실패, 디렉터리, preserve-only, completed replay를 구별하고 scratch 예외를 둡니다. 626·610줄은 “race나 부분 실패가 없다”는 증명이 아니라고 명시합니다. | F5(디렉터리 속성). 사전 검사가 race를 제거한다고 오인할 여지는 없습니다. | 사전 거절, 검사 뒤 drift, 중단 prefix fixture |
| 3 NTFS gate | target·staging·lock/scratch·backup의 mutation 전 검사, nearest ancestor와 creation chain, scratch 이전·guard 안·발행 시 재검사, remote/non-NTFS/unknown 거절, replace의 same-volume, backup의 다른 admitted volume 허용, read-only 경로에는 새 조건 없음. fixed-drive·admin gate 없음(596·726줄). | F7(문장 정리만) | volume drift, 미존재 경로, remote 거절 |
| 4 repair mode | windows-1 candidate에서만 0/1을 선택하고 bool은 금지합니다. before null/0, after 0, mode 1 preview는 token 없이 non-pass입니다. flag-only repair 금지, unlisted 파일, 독립 완료 조건, POSIX/TreeEntry/ACL 재해석 금지(707줄). | 없음 | 관측 일관성, 양방향 reader |
| 5 retry/새 preview | 원 request/token/backup 불변, drift 시 거절, 외부 evidence는 pending authority가 아님, 실제 barrier 유지, 새 identity/request/token/backup, 자동 재시도 금지. 영구 교착도 성공 보장도 주장하지 않습니다(374·713줄). | F2(예시 오해), F6(receipt 표현). repair 쪽 pending 예외의 실제 범위는 source 조건부입니다. | 외부 evidence만 남은 상태의 새 preview와 실제 pending 거절 |
| 6 detach4 | 내장 complete plan으로 read-only 검증. mutation에는 원 target과 request/token이 필요합니다. old-reader false PASS는 증거 부적격이고 old-writer gate와 별개입니다. canonical pair·내부 링크·suffix·preserve 검사 유지, 재해시 불가(630–636·788·798줄). | 없음 | 제거 전후·suffix fixture |
| 7 A1–A15 | Windows 한정 범위, R1-D06→v0.7 상태(36·848줄), 첫 map의 A14(451줄), S2 old-writer pointer(198줄), criterion 2와 추가 repair 의무의 구분(818줄), literal/payload 사전 준비와 equality(652·780줄), 상호 참조 절 이름 일치. | F1(fence 밖 단락) | target 원문과의 위치 대조(Driver) |
| 8 B·worker | 대표 UTM full 검증, x64·물리 focused 보완, formal timing, 미관측 tuple 표시, 열 가지 criteria 유지, 공통 조건 + 모든 guard, 예시는 닫힌 목록 아님, index-only add와 실제 삭제, mixed 거절. read-only 거절은 worker apply에도 operation 전체로 적용되지만 지원 방향을 닫지 않으며, 새 matrix·권한층·probe를 기본 gate로 만들지 않습니다(786줄). | 선택 사항: A2·A3에서 A7 read-only gate를 교차 참조하는 정도 | read-only control 파일을 대상으로 한 worker 거절 fixture |

## 4. 수락 전 보완과 이후 증거의 분리

**수락 전 문서 보완**
- F1: fence 안으로 이동.
- F2: 예시에 한 문장 추가.
- F3: source 확인 뒤 해당하면 사전 검사 집합을 확장하거나 Owner가 다른 대응을 선택.
- F4–F7: 선택 보완. 모두 한두 문장 범위입니다.
- 새 절차, 명령, field, 실험은 필요하지 않습니다.

**Owner 선택**
- F3이 해당될 경우 그 대응 방식.
- 기존 S1–S8 미결 선택은 그대로 남아 있습니다. 이번 리뷰가 새로 추가하는 선택은 없습니다.

**이후 증거 (문서 결함이 아님)**
- Win32 동작: write open, RemoveDirectory, LockFileEx.
- PowerShell 5.1 입력 보존.
- 실제 tuple, artifact, old-writer 노출 집합.
- detach4·repair fixture.

**해결됐거나 반례가 없는 부분**
- v0.6에서 지적된 영구 교착 표현은 좁혀졌습니다.
- 첫 map의 A14 연결과 현재 상태 문구가 바로잡혔습니다.
- detach4의 read/mutation 입력 구분이 정리됐습니다.
- old-reader 증거 처분이 정리됐습니다.
- literal/payload 사전 준비가 고정됐습니다.
- NTFS·standard-user 구분, backup volume 허용, 디렉터리를 파일 flag로 대체하지 않는 규칙, completed replay에 새 gate를 붙이지 않는 규칙도 정합합니다.

## 5. 읽지 못한 근거와 잔여 한계

- **target 원문 미확인:** A1–A15가 한정·교체하는 target 원문(Structure, General Work, Workspace, Operations, Reference, Maintaining, Manual, Security, README의 Windows Admission, Getting Started, SKILL)을 보지 못했습니다. 삽입 위치, 기존 문장과의 정확한 대응, criterion 4의 CRLF 포함 여부는 Driver가 대조해야 합니다.
- **source 미확인:** product source를 보지 못했습니다. 따라서 다음은 모두 조건부입니다.
  - repair receipt의 위치와 pending 예외의 범위(F6, 사례 5)
  - immutable 재확인 flush가 수행되는 call site(F3)
  - token 계산 방식과 기존 detach shape
- **Windows API 동작 미검증:** read-only 속성 파일의 write open, 디렉터리 제거 동작은 확인하지 않은 플랫폼 사실이며 F3·F5의 전제입니다.
- **이전 기록 미확인:** 이전 리뷰 원문과 실험 원출력을 보지 못했습니다. 변경표(72–150줄)는 역사로만 읽었습니다.
- 이 리뷰는 정적 1회 판독이며, 재현이나 PASS를 만들지 않았습니다.
````

### R1-D07 Record Verification And Cleanup

검증: 작성 문서 3개를 marked 17.0.5 GFM으로 렌더링해 local path/heading link 90개, code 밖 literal 강조 기호, whitespace와 공개용 식별자 경계를 확인했다. 9개 frozen 리뷰의 packet/request/final hash 및 verbatim, 7개 Driver 처분, 변경 없는 v0.7 bytes와 exact packet 복구, 42개 기존 입력 중 허용 기록 외 불변, 기존 CHORE의 State 외 historical bytes와 private context 보존, source HEAD·tracked navigation diff·untracked 범위를 확인했다. 모두 PASS이며 제품 실행·플랫폼 재현 PASS가 아니다. A12 exact 본문 범위 문제는 이 기록에서 공개했으며 DR은 수정하지 않았다.

정리 완료: reviewer 종료와 결과 통합·검증 후 lsof no-use 및 bytes/empty 확인을 거쳐 최종 응답과 같은 partial 1개, 빈 stderr 1개, 빈 tool-temp 디렉터리 1개, 일회성 checker와 검사 보고서 2개를 삭제했다. request·packet·입력 식별자·final·최소 실행 metadata·호출 script 6개는 Owner 처분과 다음 exact 비교/준비를 위해 유지한다. 추가 reviewer 호출은 승인하지 않았다. 기존 active path는 바꾸지 않았으며 worktree·VM·probe 증거·마지막 복구 사본의 기존 결과 수락/복원/구체 후속 소비자는 그대로다. 삭제 후 최종 기록을 포함해 메모리에 보관한 checker로 재검증했고 출력 파일은 재생성하지 않았다.


## Contract Draft Revision 0.8 — 2026-10-18

Owner는 “R1-D07과 네 판단을 반영해 DR-0007 v0.8로 보완해줘. A12 본문 위치, read-only가 남은 새 preview의 거절, 필수 flush 대상의 사전 검사 범위를 명확히 하고 관련 문구도 정렬해줘. 채택하지 않은 지적은 반영하지 말고, B안과 공통 조건 중심 worker 지원은 유지해. 추가 실험이나 제품 구현은 시작하지 마.”라고 요청했다. 기존 Draft와 이 진행 기록의 보완만 수행하며 계약 수락·실행·실험·reviewer 호출 승인은 포함하지 않는다.

- D07-F1: A12의 누락 영어 단락을 exact fence 안으로 옮기고 관련 정책 문구를 정렬했다. 이전 in-memory 검증의 누락은 R1-D07 기록대로 보존한다.
- D07-F2/F4: read-only 교체 대상이 남으면 새 preview도 non-pass이며 실행 request/token이 없다. 외부에서 원 속성이 복원돼도 원 retry의 모든 exact 관측·backup·candidate·binding·prefix 검사가 필요하다. read/preserve 면제는 completed replay의 bound after 관측을 면제하지 않는다.
- D07-F3 revise: 교체·제거와 필수 write-capable flush 기존 파일을 첫 durable publication 전 operation 전체 검사에 포함하고, recovery에서는 남은 교체·제거와 해당 prefix의 필수 재flush를 검사한다. 순수 읽기/보존과 구별하며 기존 필수/허용 unavailable 의무를 바꾸지 않는다. S3/S5/S6와 A7/A8/A9/A10/A11/A12/A13·admission mapping을 정렬했다. source에서 실제 확인한 init/staging/receipt 및 외부 backup 경로만 근거로 쓰고 모든 retained release 재flush를 가정하지 않는다.
- D07-F7: A6의 native local NTFS 지원 경계와 standard-user qualification 표현을 분리했다. 새 admin-token gate는 없다.
- D07-F5/F6 defend: 디렉터리를 파일 READONLY로 거절하는 정책과 repair receipt 위치 변경을 추가하지 않았다. external backup/receipt는 그대로 evidence이며 pending authority가 아니다.

B, worker 공통 필요조건과 A1–A5, window/member/pair, 디렉터리 검사, 기존 Owner 원문·리뷰·개정 이력을 보존했다. Draft와 accepted-only 빈 절은 유지한다. normative 계약·제품 source·STATUS·catalog·PLAN·VM·probe·Git publication은 변경하지 않는다. v0.8 bytes는 아직 독립 재리뷰·Owner exact 수락·qualification·activation을 받지 않았다.

Draft identity: 172,048 bytes; SHA-256 `c3a16bf378a02e56975f1665bcecaf9f6cc6e7a581ee160a65784322d8ee890d`. v0.7 exact bytes는 R1-D07 frozen packet에서 복구할 수 있다. 이번 입력 식별자와 bounded revision diff는 Owner 비교 및 다음 exact 리뷰 처분까지 보존한다.

검증: 작성 문서 3개를 marked 17.0.5 GFM으로 렌더링해 local path/heading link 91개, code 밖 literal 강조 기호, whitespace와 공개용 식별자 경계를 확인했다. A1–A15의 exact 영어 본문 fence 범위와 블록 밖 누락 여부를 확인하고 11개 실제 target의 메모리 사본에 전체 본문을 적용해 위치·누락/중복·heading·렌더링을 검사했다. A12 마지막 단락도 Reference 사본에 전부 들어간다. 13개 보호 절, A1–A5·B·worker 공통 조건, 기존 Owner 원문, 29-member source AST 목록, S1–S8·열 가지 criteria·비어 있는 accepted-only 절, 9개 frozen 리뷰와 verbatim, 48개 고정 입력 중 허용 기록 외 불변, v0.7 exact 복구·bounded diff와 기존 CHORE/private context 보존을 확인했다. source HEAD와 기존 navigation diff·untracked 범위는 변하지 않았다. 모두 문서/정적 검사 PASS이며 제품 실행·Windows qualification PASS가 아니다.

정리 완료: 검증과 lsof no-use 확인 뒤 이번 개정의 apply/refine/check helper 3개와 일회성 검사 보고서 1개를 삭제했다. 입력 식별자와 revision diff는 Owner 비교·다음 명시적으로 선택한 exact 리뷰 처분을 위해 유지한다. 기존 worktree·VM·probe 원출력·필수 리뷰 증거·마지막 복구 사본의 결과 수락/복원/구체 후속 목적은 유지하며 active path 변경은 없다. 삭제 후 최종 기록을 포함해 메모리에 보관한 checker로 재검증했고 출력 파일은 재생성하지 않았다. STATUS·catalog·PLAN은 Draft 개정만으로 변경하지 않는다.


## R1-D08 — Draft 0.8 Static Re-review — 2026-10-18

Owner는 “DR-0007 v0.8을 Claude CLI로 재리뷰해줘. A12 본문 범위, read-only가 남은 새 preview 거절, 필수 flush 사전 검사와 A1–A15의 일관성을 확인하고 네 판단도 정리해줘. B안과 공통 조건 중심 worker 지원은 유지하고 추가 실험이나 제품 구현은 시작하지 마.”라고 요청했다. 이번 범위는 선택한 Draft의 독립 정적 리뷰와 Driver의 근거 대조·처분 기록이다. Draft·normative 계약·제품 source 수정, 계약 수락·qualification·activation은 포함하지 않는다.

### Invocation And Evidence Boundary

- `review-procedure.md`와 cross-review 절차를 읽고 Owner가 지정한 직접 Claude CLI 경로를 사용했다. CLI 2.1.302, `claude.ai / firstParty / pro`와 provider override 부재를 확인했다. 비밀값·계정 email은 기록하지 않았다.
- 실제 모델은 `claude-opus-5-5`, 새 session은 `d4c24f47-9c68-4725-832b-176865be1596`다. 모델 override 없이 단일 문서·no-tools·strict empty MCP·세션 비보존으로 실행했다. 1,200초 상한 내 197.846초, exit 0, tool event 0, input drift false였다.
- 입력은 exact Draft 0.8 한 개다. 172,048 bytes; SHA-256 `c3a16bf378a02e56975f1665bcecaf9f6cc6e7a581ee160a65784322d8ee890d`. 줄 번호를 붙인 frozen packet은 176,951 bytes; SHA-256 `396d9cb40861a49b903f92bf217214f1e67b507d34dc9e31f5608bef354d8d39`다. 링크된 target 문서, source, 이전 리뷰 원문·probe 원출력은 Reviewer에게 제공하지 않았다.
- 최종 응답은 13,515 bytes; SHA-256 `c6be232f058b76b0b5d27e15e1e725cc993565f8bbb6172635fa875b9e4bad7f`다. request·packet·입력 식별자·final·최소 metadata·runner를 기존 task-owned R1-D08 경로에 보존한다. 아래 source 대조는 Driver의 별도 정적 확인이며 Claude의 실행·독립 재현으로 표시하지 않는다.

### Reviewer Verdict

전체 exact 수락 준비도는 **conditional** 판정이다. P1은 없고, source 전제가 맞을 때만 성립하는 P2 1개와 선택 P3 4개다. A12 본문 범위, read-only가 남은 새 preview 거절, NTFS/runtime, B·공통 조건 worker 및 문서 기반 계획은 approve다. 필수 flush/completed replay와 A1–A15의 최종 판정은 F1 처분에 종속된다. Reviewer 판정은 Owner 수락이 아니다.

### Driver Dispositions

| Finding | Driver 처분 | 근거와 권고 |
| --- | --- | --- |
| D08-F1 · P2 조건부 completed replay sync | defend | 이번 Windows fresh/same-window 범위에 대해 우려의 전제가 확인되지 않았다. init·repair·detach 완료 replay는 해당 immutable-file write/flush 전에 반환한다. switch의 기존 completed-replay file sync는 `remove`가 있는 First B1 전환 분기이며, same-entry switch는 `remove: []`다. Draft S2/A8은 old-window→windows-1 전환을 제외하고 기존 entry-1/First B1 의미를 보존한다. 일반 read-only replay에 새 필수 flush/gate를 넣지 않는다. 기존 guard scratch·directory 동기화까지 없다고 주장하거나 First B1 sync를 생략하는 처분은 아니다. |
| D08-F2 · P3 현재 권고 묶음의 v0.7 잔존 | accept | Draft 425행의 현재형 문구에 `v0.7`이 남아 있다. 다음 문서 보완에서 `현재 revision`으로 고치는 것을 권고한다. 과거 개정 이력은 그대로 둔다. 이번 리뷰 범위에서는 Draft를 수정하지 않는다. |
| D08-F3 · P3 A9/A12 fence의 후행 빈 줄 | accept | 닫는 fence 직전의 빈 줄은 실제 fence content다. 다음 exact 문안 보완에서 두 불필요한 빈 줄을 제거하는 최소안을 권고한다. 직전 in-memory 적용 검사는 추출 본문의 `trimEnd()` 결과를 사용했으므로 전체 논리 본문의 포함·위치·렌더링은 확인했지만 raw fence의 후행 bytes까지 동일하게 적용했다는 증거는 아니다. 기존 검증 기록을 고쳐 쓰지 않고 여기서 그 한계를 명시한다. |
| D08-F4 · P3 preview에서 알려진 required-flush read-only 진단 | revise · 선택 명확화 | 발행 전 apply gate는 이미 존재한다. 현재 fresh repair preview는 새 backup 목적지를 요구하므로 기존 backup 재flush 사례를 그대로 fresh-preview 반례로 쓸 수 없다. 실제 call-site 계획에서 preview가 read-only 필수 flush 대상을 이미 알 수 있으면 조기 non-pass 진단을 허용한다는 설명은 유용하다. 이를 새 필수 preview mutation 검사나 완전한 미래 apply 성공 증명으로 확대하지 않는다. |
| D08-F5 · P3 worker 설명의 Windows preflight 참조 | accept · 선택 명확화 | A7은 이미 intent/Work/worker/planning writes에 적용된다. A2의 `existing guard` 또는 A4에 A7의 Windows NTFS/read-only preflight가 함께 적용된다는 참조를 추가하면 읽기 쉽다. worker 공통 필요조건, 비닫힌 지원 예시, B 검증 배정이나 matrix는 바꾸지 않는다. |

### Driver Source Check

기준은 기존 source HEAD `a93f71c359c4f0a9d57fcfb50d5999160e870f77`다. 아래는 코드 읽기와 문서 대조 결과이며 Windows 실행 결과가 아니다.

- [product.py](../../src/hv2ref/product.py) 745–767행: `_entry_replay_result`의 file sync와 transition directory sync는 `plan["remove"]`와 current binding operation 일치 조건 안에 있다. 818–830행은 checkout-1 predecessor와 retirement 유무를 묶고, [Workspace — Entry-1 Admission And Publication](../WORKSPACE-CONTRACT.md#entry-1-admission-and-publication)은 same-entry switch의 empty remove를 명시한다. 1442–1458행의 완료 switch 경로와 Draft S2/A8의 fresh/same-window 한정을 함께 읽어 F1을 처분했다. 모든 기존 replay가 sync-free라는 주장은 하지 않는다.
- 같은 source 1133–1141행은 init 완료를 write 단계 전에 반환한다. 1723–1729행의 repair 완료는 backup/receipt membership과 after 관측을 검사한 뒤 반환하며, 기존 backup request/original의 `_write_exact` 재flush는 1731·1736행의 미완료 recovery 경로다. 1960–1969행의 detach 완료도 receipt `_write_exact` 전에 반환한다.
- `workspace_candidate` 349–372행, `verify_workspace_product` 963–966행, `_init_partial_tree` 1037–1055행, `_workspace_observe` 1287–1295행 및 `workspace_detached_status` 1923–1931행은 이 대조에서 읽기/관측 경로로 확인했다. [workspace.py](../../src/hv2ref/workspace.py) 366–382·475–501행의 기존 guard directory 준비·sync와 immutable exact-file sync는 구별한다. guard의 기존 scratch/동기화 의미를 제거하거나 새 gate로 승격하지 않는다.
- `workspace_repair_preview` 1597–1603행은 backup 부재를 요구한다. source observation·unlisted files를 읽는 것만으로 모두 mandatory flush 대상이 되지 않으며, F4의 구체 사례는 실제 operation별 대응표에서 확인해야 한다. partial recovery의 기존 backup flush 검사는 이미 A7/A9 범위다.
- A12 마지막 규범 단락은 실제 777–790행 fence 안에 있다. A9 736행과 A12 789행은 후행 빈 줄이다. F2/F3는 실제 문서 관측이며 실행 결함이나 계약 모순으로 과장하지 않는다.

### Driver Recommendation And Remaining Boundary

B와 공통 조건 중심 worker 지원은 유지한다. source 조건부 F1은 범위를 한정해 defend하므로, 이번 대조에서 추가 확인된 P1/P2 계약 결함은 없다. 다음 문서 정리의 우선순위는 F2 버전 표기와 F3 exact 후행 bytes다. F5는 짧은 참조 보완을 권고하고 F4는 계획에 맞춘 선택 진단 설명으로 한정한다. 새 replay gate, 추가 full matrix, 디렉터리 파일-flag gate나 receipt 위치 변경을 도입할 사유는 없다.

이는 전체 의미 완전성이나 수락·구현 준비의 자동 판정이 아니다. S1–S8과 exact 문안에 대한 Owner 선택, 실제 artifact/tuple, old-writer 거절 또는 증명된 비노출, API phase·실패 주입·reader qualification은 기존 경계대로 남는다. reviewed Draft 0.8 bytes와 accepted-only 빈 절을 유지하며, normative 문서·제품 source·STATUS·catalog·PLAN·VM·probe·Git publication은 변경하지 않았다. 추가 reviewer 호출도 수행하지 않는다.

### Verbatim Reviewer Response

````markdown
# R1-D08 — DR-0007 Draft 0.8 정적 재리뷰

이 판정은 패킷으로 받은 단일 문서(172,048 bytes, SHA-256 `c3a16bf3…890d`)만을 대상으로 한 정적 리뷰입니다. 계약 수락, 구현 허가, activation은 Owner가 결정합니다. 도구 실행, 파일 접근, source 대조, Windows API 실행은 하지 않았습니다.

## 1. 판정

| 대상 | 판정 | 요지 |
|---|---|---|
| 전체 exact 수락 준비도 | **conditional** | P1 없음. source 조건부 P2 한 건(F1)만 처분하면 수락 후보로 충분합니다. 나머지는 P3 선택 보완입니다. |
| A12 본문 범위 | **approve** | 마지막 read-only/flush/NTFS/retry 단락(788)이 네-backtick fence(777–790) 안에 있습니다. 후행 빈 줄 문제는 F3(P3)입니다. |
| read-only 새 preview 거절 / 원 retry | **approve** | S6·S8·A9·A11·A12·A13이 같은 의미입니다. F4는 선택 명확화입니다. |
| 필수 flush 사전 검사 / recovery / read-only 면제 | **conditional** | 합집합 검사, 발행 전 시점, unknown 처리, recovery 재flush, 면제 범위는 정합합니다. completed replay와 기존 필수 sync의 관계만 source 확인이 필요합니다(F1). |
| NTFS / runtime | **approve** | 실제 mutation 경로, scratch 사전 검사, same-volume replace, 별도 volume backup, 표준 사용자 qualification 구분이 일치합니다. fixed-drive·admin gate는 추가되지 않았습니다. |
| A1–A15 | **approve** (F1 처분에 종속) | 상호 참조 heading, 삽입·교체 설명, Korean 요약, mapping 사이에 모순이 없습니다. |
| B / 공통 조건 worker | **approve** | 대표 UTM full, x64/물리 focused, formal timing, 비닫힌 예시, index-only add, whole-result 거절, pending/cancel/replay가 유지됩니다. 새 matrix·권한층은 없습니다. |
| 문서 기반 계획 준비 | **approve** | 계약 후보와 계획 세부, 미래 qualification 증거가 구별되어 있습니다. |

## 2. Findings

### Must-fix (source 확인 조건부)

**F1 · P2 · completed replay와 기존 필수 sync의 충돌 가능성**

- 관련 문구
  - 254: "fresh init launcher와 기존 exact staging/receipt·외부 repair backup 등의 재확인에 남아 있는 read-only descriptor fsync도 call site별로 대응한다"
  - 618: "including init launcher and immutable-member revalidation"
  - 626: "Do not omit a required flush to avoid this gate"
  - 628: "Completed read-only replay keeps its existing exact observations and gains no mutation gate or reflush."
  - 265: 재flush는 "exact apply/recovery의 해당 단계에서만"
- 오해 경로: 현행 source의 completed replay가 immutable-member 재확인 중에 필수 fsync를 수행한다고 가정합니다. POSIX에서는 read-only fd로 가능합니다. Windows로 옮기면 write-capable open이 필요해지므로 구현자는 둘 중 하나를 골라야 합니다.
  - fsync를 유지하면 그 파일이 626의 사전 검사 대상이 되어, 628이 금지한 "mutation gate"가 replay에 생깁니다.
  - "gains no reflush"를 근거로 fsync를 빼면, 626·S5의 "필수 동기화 생략 금지"를 어깁니다.
  - 해당 파일이 read-only라면 두 해석의 결과가 replay PASS와 replay non-pass로 갈립니다.
- 성격: 문안만으로는 replay 경로에 필수 sync가 있는지 판단할 수 없으므로 source 조건부 우려입니다. Driver의 로컬 대조에서 completed replay 경로에 필수 sync가 없다고 확인되면 defend로 닫아도 됩니다.
- 최소 수정: A7 628에 한 문장을 추가하고 S6 350·A11 766의 replay 문구에 같은 뜻을 반영합니다.
  - 예: "This adds no new reflush; if an existing completed-replay call site already performs a mandatory synchronization, map that existing step under the preceding preflight instead of omitting it."
  - 또는 반대로, read-only replay로 분류되는 경로에는 현행 필수 sync가 없다는 확인 결과를 문안에 고정합니다.

### 선택 보완 (P3)

**F2 · P3 · 현재 상태 문구의 버전 잔존**
- 425: "아래는 v0.7의 단일 권고 묶음이다"
- v0.8에서 A7·A9·A11·A12 등 묶음의 exact 문안이 바뀌었으므로, 이 표가 v0.7 기준 묶음이라고 읽힐 수 있습니다.
- 최소 수정: "v0.8의" 또는 "현재 revision의"로 고칩니다.

**F3 · P3 · fence 안 후행 빈 줄**
- A9 fence의 736과 A12 fence의 789가 닫는 fence 직전의 빈 줄입니다. CommonMark 기준으로 이 빈 줄은 code block 내용, 즉 exact 삽입 bytes에 포함됩니다.
- A12는 Reference "끝"에 추가되므로 대상 파일의 EOF에 여분의 빈 줄이 생길 수 있습니다. 다른 A 조항에는 이런 빈 줄이 없습니다.
- 의미 결함은 아니지만 "exact 본문"의 bytes가 흔들립니다.
- 최소 수정: 두 빈 줄을 제거하거나, 삽입 시 후행 공백 처리 규칙을 한 줄로 명시합니다.

**F4 · P3 · 새 repair preview와 필수 flush 대상의 비대칭**
- 733: preview가 실행 요청을 막는 조건은 "remaining damaged file requiring replacement is read-only"뿐이고, required-flush 대상은 "its apply must also pass"로 넘깁니다.
- 반면 A12 788은 required-flush read-only 파일도 "policy-level unsupported for the whole proposed operation"으로 표현합니다.
- 오해 경로: preview 시점에 이미 관측 가능한 read-only required-flush 파일(예: 재확인해야 할 기존 파일)이 있어도 token이 발급되고, apply에서 확정적으로 거절됩니다. 안전 문제는 없습니다. apply gate가 발행 전 거절을 보장하기 때문입니다.
- 최소 수정(선택): A9 733에 "Preview may also report a known read-only required-flush file as non-pass; apply remains authoritative" 정도를 추가합니다. 새 gate를 만들 필요는 없습니다.

**F5 · P3 · worker 지원 설명과 read-only preflight의 parity**
- A2 532와 A3 552는 eligibility를 "common condition together with every existing guard"로 정의합니다.
- 그러나 read-only preflight(A7 626, "intent/Work/worker/planning writes" 포함)는 windows-1에서 새로 생기는 guard입니다. "existing"이라는 말 때문에 그 guard가 빠진다고 읽을 여지가 있습니다.
- A4의 parity 목록에도 "기존 read-only project 파일이면 operation 전체 거절"이 들어 있지 않습니다.
- 번들 전체를 읽으면 의미는 명확하므로 결함은 아닙니다.
- 최소 수정(선택): A2 끝이나 A4에 "Windows Native Observation And Publication's NTFS/read-only preflight also applies" 수준의 참조 한 줄을 추가합니다. 새 qualification matrix는 필요하지 않습니다.

반례를 찾지 못한 항목은 finding으로 올리지 않았습니다. 디렉터리 gate, receipt 위치, B·worker 방향, NTFS/runtime이 여기에 해당합니다.

## 3. Focused cases 요약

| # | 정합한 의미 | 남은 문안 / Owner 선택 | 이후 실제 증거 |
|---|---|---|---|
| 1 A12 범위 | 777–790 fence가 788 단락을 포함합니다. 775의 한정 대상(Source Utilities, Checkout Compatibility Limits, Human Review)이 780 본문과 일치합니다. 503–829 구간에서 fence 밖 영어 규범 문장은 정적으로 발견되지 않았습니다. 166·881은 v0.7 누락을 R1-D07 기록에 보존하고, 문서 검증을 의미 완전성으로 주장하지 않습니다. | F3 후행 빈 줄. 외부 target heading·anchor 정합은 미제공입니다. | 실제 target 파일에 적용한 bytes·렌더링 확인(Driver 로컬) |
| 2 read-only 새 preview | 362·392·394·725·733·768·788·805가 같은 뜻입니다. 남은 교체 대상이 read-only이면 preview는 non-pass이고 request/token이 없습니다. 외부 backup은 pending authority가 아니지만 product/truth/candidate/pending guard는 유지됩니다. flag 복원 뒤에도 원 retry는 모든 조건으로 재판정되며, 속성 해제 기능·복원 지시·성공 보장이 아닙니다. | F4(선택) | read-only 남은 preview 거절, 복원 후 retry, 새 identity/backup 경로의 qualification |
| 3 필수 flush 사전 검사 | 626이 핵심입니다. 합집합을 첫 durable 발행 전에 검사하고, call-site 기준이며 retained release를 자동 포함하지 않습니다. scratch 예외, guard 안 재검사, unknown 분리, permitted-unavailable 승격 금지, 생략 금지가 모두 있습니다. S3·S5·S6·A8·A9·A10·A12와 일치하며, 뒤의 flush 실패 진단으로 대체하지 않습니다. | F1(completed replay sync) | call-site별 phase 대응표, 실패 주입 |
| 4 recovery/read/replay | recovery는 남은 교체·제거와 prefix의 필수 재flush를 검사하고, 이미 발행된 파일도 포함합니다(626·644·731). 면제는 bound 관측을 면제하지 않습니다(628·729). after.mode 0→1은 replay non-pass입니다. 새 파일 clear와 원 evidence 비정규화는 backup이 원 mode를 request에 기록하는 방식(729)으로 충돌 없이 공존합니다. | F1 | bound replay drift, backup 재flush 대상 |
| 5 NTFS·runtime | S3 224–228, A6 600, A7 612–614, A10 744, A13 805가 일치합니다. 없는 경로는 ancestor/creation chain으로, scratch는 생성 전에 검사합니다. replace는 same-volume, backup은 다른 admitted NTFS volume을 허용합니다. 표준 사용자 qualification은 별개이고 fixed-drive·admin gate는 없습니다. | 없음 | 실제 volume·remote·unknown 거절 관측 |
| 6 A1–A15 일관성 | 아래 항목이 모두 유지됩니다(A9 721·725, A8 646–654, A13 807, A9 670·A13 799). 상호 참조 heading 7종도 모두 실재합니다. | F2(425 상태 문구) | 양방향 reader, detach4 suffix 검증 |
| 7 채택하지 않은 지적 | 디렉터리 파일-flag gate는 추가되지 않았습니다(352·628). external receipt는 binding-selection chain 밖으로 유지됩니다(392·733). | 구체 반례 없음. 아래 API 조건부 관찰 참고. | 해당 API 동작 확인은 qualification |
| 8 B·worker | S1 191, A6 600, A13 809, A2 532–538, A3 552–556이 유지됩니다. 805가 "not extra mandatory full matrices"를 명시합니다. | F5(선택) | 대표 UTM full, focused x64/물리 |

6번에서 확인한 유지 항목은 다음과 같습니다.
- Windows-only window/pairs
- verified candidate에 근거한 repair mode 0/1
- 독립 completion
- detach4의 complete plan, inventory, 내부 링크, suffix, preserve
- 제거된 bytes의 재해시 불가
- old-reader 증거 부적격과 old-writer gate의 구분
- 명시적 literal/payload 준비

7번 관련 API 조건부 관찰입니다. 확인하지 않은 전제입니다.
- 만약 Windows에서 디렉터리 속성이 필수 parent flush용 write-capable open을 막는다면, 발행 후 flush 실패 경로가 생길 수 있습니다.
- 문서는 이 경우를 "after publication but before required flush" phase로 이미 처분하고 prefix를 보존합니다(620). 따라서 계약 모순은 아닙니다.
- 이 전제가 확인되더라도, 파일 READONLY flag를 디렉터리 gate로 쓰는 것은 적절한 수정이 아닙니다.

## 4. 수락 전 보완, Owner 선택, 이후 증거의 구분

**수락 전 문서 보완**
- F1: source 확인 결과에 따라 한 문장을 추가하거나 defend합니다.
- 권장: F2(한 단어), F3(공백).
- 선택: F4, F5.

**Owner 선택**
- S1–S8의 각 미결 항목이 그대로 남아 있습니다(196·248·271·382·398 등). 이번 revision에서 새로 생긴 Owner 선택은 없습니다.
- 필수 flush 사전 검사의 범위 자체가 이번 exact 수락 후보에 포함된다는 점(166)은 명시되어 있습니다.

**이후 실제 증거(문서 결함 아님)**
- artifact digest
- runtime tuple
- PowerShell 5.1 입력 보존
- 노출된 old writer의 거절 또는 비노출
- 실제 API phase 대응
- 실패 주입
- detach4 reader

**해결되었거나 반례가 없는 부분**
- R1-D07의 F1(A12 위치), F2(read-only 남은 preview), F3(필수 flush 범위), F4/F7(면제와 bound 관측, NTFS/qualification 정렬)이 문안에 반영되었습니다.
- 그 과정에서 B·worker 조건, permitted-unavailable 의미, 디렉터리 검사가 바뀌지 않았습니다.

**참고(반례 아님)**
- 새 repair가 성공한 뒤 원 request를 다시 호출하면, 모든 관측이 after와 같아져 기존 recovery 규칙상 완료로 판정될 수 있습니다.
- 문서는 이를 막거나 허용하는 새 규칙을 두지 않고 기존 exact 규칙과 "명시적 처분 전 보존"(733)에 맡깁니다. 새 gate를 만들 사유는 아닙니다.

## 5. 읽지 못한 근거와 한계

- 제공되지 않은 자료: 링크된 target 문서(Structure, Workspace, Reference, Operations, Maintaining, Security, Getting Started, adapter, Development Index), 제품 source, R1-D07 원문과 Driver 처분, 이전 packet, probe 원출력.
- 따라서 다음은 확인하지 못했습니다.
  - 삽입 위치의 heading 수준과 anchor 실재 여부
  - 한정 대상 문장의 정확한 원문
  - completed replay와 재확인 call-site의 실제 fsync 유무(F1의 전제)
  - FlushFileBuffers의 접근 요구와 디렉터리 READONLY 동작 같은 Windows API 동작
- 문서에 인용된 source·계약 내용은 보고된 주장으로만 취급했습니다.
- 줄 번호는 패킷 주석 기준입니다.
- 이 리뷰는 재현, PASS, 의미 완전성의 증명이 아니며, 계약 수락·구현·activation을 허용하지 않습니다.
````

### R1-D08 Record Verification And Retention

검증 PASS: 작성 문서 3개를 marked 17.0.5 GFM으로 렌더링해 local path/heading link 94개, code 밖 literal 강조 기호, whitespace와 공개용 식별자 경계를 확인했다. R0·R1-P01·R1-D01–D08의 frozen request/packet/final 및 verbatim 10회, Driver 처분 5개, exact v0.8 packet 복구와 Draft 불변, 허용 기록 외 baseline 입력 48개 불변, 이전 CHORE·private context 보존, S1–S8·열 가지 criteria·15개 named clause·빈 accepted-only 절과 기존 source HEAD/navigation/untracked 범위를 확인했다. F2/F3는 reviewed bytes에 그대로 있으며 별도 보완 권고로 기록했다. 이번 검증은 문서/정적 검증이고 제품 실행·Windows qualification이 아니다.

정리 완료: CLI 종료, final 통합·중복 bytes 일치, 빈 stderr/tool-temp 및 lsof no-use를 확인한 뒤 partial·빈 stderr·빈 tool-temp·일회성 checker·검사 보고서 5개를 삭제했다. request·packet·입력 식별자·final·최소 실행 metadata·호출 script 6개는 Owner 처분 및 다음 exact 비교/준비를 위해 보존한다. 이후 reviewer 호출은 승인하지 않았다. 기존 worktree·VM·probe 증거·마지막 복구 사본의 결과 수락/복원/구체 후속 소비자는 유지하며 active path 변경은 없다. 삭제 후 최종 기록을 포함해 메모리에 보관한 checker로 재검증했고 출력 파일은 재생성하지 않았다.


## Contract Draft Revision 0.9 — 2026-10-18

Owner는 “R1-D08과 네 판단을 반영해 DR-0007을 v0.9로 보완해줘. 버전 표기와 A9/A12 후행 빈 줄을 정리하고, worker preflight 참조와 preview 조기 진단 설명도 최소 범위로 반영해줘. defend한 지적은 반영하지 말고, B안과 공통 조건 중심 worker 지원은 유지해. 추가 실험이나 제품 구현은 시작하지 마.”라고 요청했다. 이 요청은 Draft와 기존 진행 기록의 보완을 승인하며 계약 수락·제품 실행·추가 실험·reviewer 호출은 포함하지 않는다.

D08-F2의 현재 버전 표기를 정리하고 F3의 A9/A12 후행 빈 줄만 제거했다. F5는 A2에 A7의 Windows NTFS/read-only preflight 참조 한 문장으로 반영했다. F4는 A9에 이미 확인한 read-only 필수 flush 대상의 선택 조기 non-pass 진단을 설명하는 한 문장으로 반영했다. preview mutation이나 새 필수 gate를 요구하지 않으며 apply의 전체 사전 검사와 token의 증거 한계를 유지한다. D08-F1은 채택하지 않았고 completed replay·First B1·기존 동기화 문안은 그대로다.

B와 S1–S8, 공통 조건 중심 worker 지원·비닫힌 예시, 기존 Owner 원문·리뷰·개정 이력과 accepted-only 빈 절을 보존했다. 되돌리기 비용은 문서 Draft 단계에서 Low다. v0.8 exact bytes는 R1-D08 frozen packet에서 복구할 수 있다. v0.9는 아직 독립 재리뷰·Owner exact 수락·qualification·activation을 받지 않았다. STATUS·catalog·PLAN·normative 계약·제품·VM·probe·Git publication은 변경하지 않는다.

Draft identity: 174,893 bytes; SHA-256 `fac6d6fd2b314403561c571d5620c9e9aba959bd40e1b23a062f9c378d690386`. 이번 입력 식별자와 bounded revision diff는 Owner 비교 및 다음 명시적으로 선택한 exact 리뷰 처분까지 보존한다. 일회성 작성·검사 파일은 검증·no-use 확인 후 정리한다. 기존 필수 evidence/last recovery의 소비자·종료 조건과 active path는 유지한다.

검증 PASS: 문서 3개, local path/heading link 95개, marked 17.0.5 GFM 렌더링·code 밖 literal 강조 기호·whitespace·disclosure 검사를 통과했다. A1–A15의 raw fence 본문을 trim/후행 공백 정규화 없이 11개 실제 target의 메모리 사본에만 적용해 전체 bytes·위치·누락/중복·heading·렌더링을 확인했다. 한 줄 text 조각은 구분 newline만 제외했다. 17개 보호 절과 기존 Owner 원문, S1–S8·B·공통 worker 조건, 29-member AST 목록, 10개 frozen 리뷰/verbatim, 54개 입력 중 허용 기록 외 불변, v0.8 exact 복구·bounded diff, 기존 CHORE/private context·source HEAD/navigation/untracked를 확인했다. 두 설명 문장과 두 빈 줄 외의 A1–A15 bytes는 동일하며 defend한 F1 계약은 바꾸지 않았다. 이는 문서/정적 검사이며 제품 실행·Windows qualification PASS가 아니다.

정리 완료: 검증과 lsof no-use 확인 뒤 일회성 apply/check helper 2개와 검사 보고서 1개를 삭제했다. 입력 식별자와 revision diff는 Owner 비교 및 다음 명시적으로 선택한 exact 리뷰 처분까지 보존한다. 기존 worktree·VM·probe·필수 리뷰·마지막 복구 사본은 결과 수락/복원/구체 후속 소비자를 위해 유지한다. active path 변경은 없다. 삭제 뒤 최종 기록을 포함해 메모리에 보관한 checker로 재검증했으며 출력 파일은 재생성하지 않았다. Draft 보완만으로 STATUS·catalog·PLAN은 변경하지 않는다.


## R1-D09 — Draft 0.9 Static Re-review — 2026-10-18

Owner는 “DR-0007 v0.9를 Claude CLI로 재리뷰해줘. A9/A12 exact 본문, worker preflight 참조, preview 조기 진단 설명과 A1–A15의 일관성을 확인하고 네 판단도 정리해줘. B안과 공통 조건 중심 worker 지원은 유지하고 추가 실험이나 제품 구현은 시작하지 마.”라고 요청했다. 이번 범위는 지정 문서의 독립 정적 리뷰, Driver 대조와 기존 기록의 처분이다. Draft 본문·normative 계약·제품 수정이나 계약 수락·qualification·activation은 포함하지 않는다.

### Invocation And Evidence Boundary

- 공통 review procedure와 cross-review 기록 절차를 읽고 Owner가 명시한 직접 Claude CLI 경로를 사용했다. CLI 2.1.302, `claude.ai / firstParty / pro`, provider override 부재를 확인했다. 비밀값·계정 email은 기록하지 않았다.
- 실제 모델은 `claude-opus-5-5`, 새 session은 `4a09088a-2e1b-455e-aed8-be3cb5b57ee9`다. 모델 override 없이 no-tools·strict empty MCP·세션 비보존으로 호출했다. 1,200초 상한 내 149.253초, exit 0, tool event 0, input drift false였다.
- 유일한 review 입력은 exact Draft 0.9, 174,893 bytes; SHA-256 `fac6d6fd2b314403561c571d5620c9e9aba959bd40e1b23a062f9c378d690386`다. numbered frozen packet은 179,861 bytes; SHA-256 `e5b96cc21b0d2a1df35773730559e08f77d3fb56cb9cc8fafe88f7d776168b48`다. source와 linked target, 이전 review 원문·probe 원출력은 Reviewer에게 제공하지 않았다.
- 최종 응답은 13,199 bytes; SHA-256 `444574d042968e3f3e5e34531cb07716b057fe8e6762a83fe1eea867eeef48ee`다. request·packet·입력 식별자·final·최소 metadata·runner를 기존 task의 R1-D09 경로에 보존한다. 아래 source/target 대조와 byte 확인은 Driver의 별도 정적 확인이며 Claude의 실행 결과가 아니다.

### Reviewer Verdict

전체 exact 수락 준비도는 **conditional** 판정이다. P1/P2는 없고 P3 두 건이다. F1은 경미하지만 수락 전에 고칠 상태 문구, F2는 선택 보완이다. A9/A12 exact 본문, worker preflight 참조, preview 조기 진단, A1–A15 규범 본문, B/공통 조건 worker와 문서 기반 계획 준비는 모두 approve다. Review verdict는 Owner 수락이 아니다.

### Driver Dispositions

| Finding | Driver 처분 | 확인 결과와 권고 |
| --- | --- | --- |
| D09-F1 · P3 현재 상태 잔존 | revise | 문제는 확인했다. 845행 Mapping의 `v0.8`, 864행 Open Points의 이전 revision 중심 설명, 880행의 `v0.8은 아직 독립 재리뷰를 받지 않았다`는 현재 설명과 맞지 않는다. 특히 880행은 이미 수행한 R1-D08과 직접 충돌하며 v0.9 정리에서 Driver가 놓쳤다. Mapping은 `현재 revision`으로, Open Points는 현 후보의 보완 범위로 정렬하고 마지막 상태 단락은 실제 완료한 리뷰와 새 개정의 상태를 구별할 것을 권고한다. Reviewer의 예시인 `v0.9 bytes는 아직 독립 재리뷰를 받지 않았다`를 이 라운드 완료 뒤 그대로 복사하면 다시 stale이 되므로 채택하지 않는다. 현재 v0.9는 R1-D09를 받았고, 이후 변경 bytes의 리뷰/수락은 그 exact revision 기준으로 별도 기록해야 한다. |
| D09-F2 · P3 조기 진단의 출력·범위 | revise · 선택 보완 | A9의 enclosing Windows Exact Repair Observation과 fresh-preview 문맥상 현재 문장이 모든 lifecycle preview를 넓힌다고 판단하지는 않는다. 대문자 `Preview` 자체는 확장의 근거가 아니다. 다만 `A fresh repair preview`로 대상을 명시하고, 선택 진단을 operation의 non-pass 결과로 반환한다면 executable request/token을 내지 않는다고 명시하는 최소 보완은 권고한다. 이는 조기 진단 실행을 새 필수 검사로 만들거나 apply preflight를 약화하는 변경이 아니다. 미수행 optional 진단과 실제 non-pass 반환을 구별하고, 그 출력 조건은 다음 exact 문안에서 명시적으로 제시한다. |

### Driver Static Check And Limits

- v0.8과 이번 frozen v0.9를 대조하면 A2는 참조 한 문장(+142 bytes), A9는 조기 진단 한 문장과 빈 줄 제거(+282 bytes), A12는 빈 줄 한 개 제거(-1 byte)만 다르다. 나머지 12개 amendment와 S1–S8은 동일하다. 이 byte 차이는 의미적 완전성의 증명이 아니다.
- A2 raw Markdown 본문은 4,206 bytes/SHA-256 `af38eb247497cebd8aa97ce0ff47d4c94d9375b7501e8d10104ca9047ed7c737`, A9는 12,035 bytes/`280e78f4bc10c69974b9e41dcc92ea24a073df170194f78ab86c25979b060cc6`, A12는 3,547 bytes/`569f9be5974cbe00abb9f9d5b6661f3f537a90016eb65b809d9021b0562b1cf4`다. 각 본문의 마지막 LF를 포함했고 trim하지 않았다. A9/A12는 닫는 fence 앞 여분 빈 줄이 없고 의도한 마지막 단락도 안에 있다.
- A2의 참조는 A7의 operation별 writes에 연결되며, A7 자체가 intent/Work/worker/planning을 열거한다. 순수 read/preserve와 completed replay 면제 및 bound 관측은 그대로다. A9의 필수 read-only 교체 거절/no-token과 선택 required-flush 조기 진단, apply의 전체 preflight는 구별된다.
- [Workspace — Root Primitives](../WORKSPACE-CONTRACT.md#root-primitives)는 `##`이고 뒤의 [Record Encoding And Shape Boundaries](../WORKSPACE-CONTRACT.md#record-encoding-and-shape-boundaries)도 `##`다. A7의 `##` 삽입이 다음 절을 하위 절로 옮기지 않는다. [General Work — Worker Publication Development Checkpoint](../GENERAL-WORK.md#worker-publication-development-checkpoint)는 `##`이고 A2 `###`는 그 안, 다음 [Git Integration And Candidate Reuse](../GENERAL-WORK.md#git-integration-and-candidate-reuse)의 `##` 앞에 놓인다.
- 실제 11개 target에 대한 raw body 메모리상 적용·렌더링은 직전 v0.9 작성 검증에서 수행했다. 이 라운드 시작 시 허용 기록을 뺀 51개 입력의 bytes가 그 baseline과 같음을 재확인했다. Reviewer가 그 target을 읽거나 직접 검증한 것은 아니다.
- [product.py](../../src/hv2ref/product.py) 1622–1625행의 현재 repair preview 성공은 request와 confirm_token을 반환한다. 미구현 Windows 조기 non-pass의 출력이 이미 실행 검증됐다는 뜻은 아니다. F2는 그 미래 계약 문구를 분명히 하는 선택 보완이며 확인된 token 발급 bug나 안전성 반례로 기록하지 않는다.
- F1의 잔존 현재형 문구는 실제 Draft에서 확인했다. 앞선 렌더링·link·raw-body 검사가 이런 상태 서술의 의미적 완전성을 검증하지 못했다는 한계를 그대로 남긴다. 이전 기록이나 reviewed bytes를 고쳐 쓰지 않는다.

### Driver Recommendation And Remaining Boundary

계약 구조를 다시 열거나 새 실험·gate를 추가할 근거는 이번 리뷰에 없다. B와 공통 조건 중심 worker 지원을 유지한다. 수락 전에 F1의 현재형 상태 문구 세 곳을 정리하고, F2는 fresh repair 범위와 선택 non-pass 출력의 request/token 귀결만 명확히 하는 최소안을 권고한다. D08-F1 completed replay와 기존 디렉터리/receipt defend 처분은 유지한다.

이번 reviewed v0.9 bytes는 그대로다. S1–S8과 A1–A15의 Owner exact 수락, 실제 artifact/tuple·old-writer 노출/거절·API phase·실패 주입·reader qualification은 별도다. normative 문서·제품 source·STATUS·catalog·PLAN·VM·probe·Git publication은 변경하지 않았으며 추가 reviewer 호출도 수행하지 않는다.

### Verbatim Reviewer Response

````markdown
# R1-D09 — DR-0007 Draft 0.9 정적 재리뷰

## 1. 판정 요약

이 판정은 정적 문서 리뷰 결과입니다. Owner의 계약 수락, 제품 실행 승인, activation을 뜻하지 않습니다.

| 항목 | 판정 | 근거 요약 |
| --- | --- | --- |
| 전체 exact 수락 준비도 | **conditional** | 계약 본문(A1–A15)에는 실질 모순이 없습니다. 다만 주변 Korean 상태 문구 세 곳이 v0.7/v0.8 기준으로 남아 있고, 그중 한 곳은 현재 리뷰 상태와 직접 상충합니다(F1). F1만 정리하면 approve로 볼 수 있습니다. |
| A9/A12 exact 본문 | **approve** | packet 기준으로 의도한 본문이 모두 fence 안에 있습니다. 닫는 fence 직전에 여분 빈 줄이 없습니다. 실제 target 적용은 확인하지 못했습니다. |
| worker preflight 참조 | **approve** | 별도 범위나 확장으로 읽히는 반례가 없습니다. |
| preview 조기 진단 | **approve** | 기존 필수 규칙을 보존합니다. F2는 선택 보완입니다. |
| A1–A15 일관성 | **approve** (규범 본문) | F1은 규범 본문 밖의 상태 문구 문제입니다. |
| B/공통 조건 worker | **approve** | |
| 문서 기반 계획 준비 | **approve** | |

## 2. Findings

### F1 — P3 · Must-fix(경미) · 현재 상태 문구가 v0.7/v0.8에 머물러 있고 현재 리뷰 상태와 상충

**정확한 위치**

- **880행:** "v0.7은 R1-D07 정적 리뷰를 받았다. 그 판정과 Driver 처분 중 채택한 범위를 반영한 v0.8의 변경 bytes는 아직 독립 재리뷰·Owner 계약 수락을 받지 않았다."
- **845행:** "이 표는 현행 열 가지 기준을 **v0.8** 및 A1–A15 문안과 대응한다."
- **864행:** Open Points 도입부가 "v0.8은 그 방향 아래 … 보완했다"로 끝납니다. v0.9의 현재 상태는 언급하지 않습니다.

**구체 상충**

- 36·78행은 R1-D08이 v0.8을 리뷰했다고 기록합니다. 그런데 880행은 v0.8 bytes가 아직 독립 재리뷰를 받지 않았다고 현재형으로 말합니다.
- 176행(D08-F2 accept)은 "현재 상태·검증 범위를 v0.9에 맞춤"이라고 변경 범위를 밝혔습니다. 하지만 Mapping 표 머리말, Open Points, 마지막 상태 단락에는 반영되지 않았습니다. D08-F2와 같은 종류의 잔존 표기입니다.

**오해 경로**

Owner나 후속 reviewer가 "Open Points And Decision Order" 절만 읽으면 다음처럼 오인할 수 있습니다.

- 현재 수락 후보가 v0.8이라고 판단함
- R1-D08이 수행되지 않았다고 판단함

그러면 수락 대상 revision이나 리뷰 이력을 잘못 식별하게 됩니다. 계약 의미는 바뀌지 않으므로 P3로 분류했습니다. 다만 Owner가 exact revision을 수락하는 문서의 상태 서술이므로 수락 전에 정리하는 편이 맞습니다.

**최소 수정**

- **845행:** "v0.8" → "현재 revision"
- **864행:** v0.8 문장은 역사로 두고, 끝에 한 문장을 추가합니다. 예: "v0.9는 R1-D08 처분에 따라 버전·exact 본문 공백·worker preflight 참조·선택 preview 진단만 보완했다."
- **880행:** 첫 두 문장을 다음 취지로 교체합니다. "v0.8은 R1-D08 정적 리뷰를 받았다. 채택한 처분을 반영한 v0.9 bytes는 아직 독립 재리뷰·Owner 계약 수락을 받지 않았으며, defend한 D08-F1과 채택하지 않은 D07-F5/F6은 반영하지 않았다."
- 나머지 문장(이전 판정 재사용 금지, 실행 미시작)은 유지합니다.
- 새 gate나 절차는 필요 없습니다.

### F2 — P3 · 선택 보완 · A9 조기 진단의 출력 귀결과 적용 범위

**정확한 위치**

748행: "Preview may also report a known read-only file requiring a write-capable open for that operation's mandatory flush as non-pass without mutation; this optional early diagnostic neither replaces …"

**오해 경로**

1. **출력 귀결이 모호합니다.** 740행의 교체 대상 규칙은 "reports unsupported/non-pass **and produces no executable repair request/token**"이라고 결과를 둘 다 고정합니다. 새 문장은 "non-pass"만 씁니다. 그래서 구현자가 "non-pass 진단을 경고로 붙이고 token도 함께 발급"하는 출력을 정상으로 읽을 수 있습니다.
   - 안전성 반례는 아닙니다. apply의 전체 preflight가 유지되고, 발급 token은 admissibility 증거가 아니라는 단서도 있기 때문입니다.
   - 다만 같은 preview가 non-pass이면서 실행 token을 내는 출력은 진단 범주상 어색합니다.
2. **적용 범위가 넓게 읽힐 수 있습니다.** 문장 첫 단어 "Preview"가 대문자로 시작합니다. 또 Revision 0.9 Changes 표(178행)는 이를 일반 "preview"로 설명합니다. 그래서 repair의 fresh preview뿐 아니라 init/update/detach preview 전반의 허용으로도 읽힐 수 있습니다.
   - 선택적·비변경 진단이므로 실질 위험은 낮습니다.
   - 의도가 repair fresh preview라면 문맥상 한정하는 편이 명확합니다.

**최소 수정(선택)**

"A fresh repair preview may also report … as non-pass without mutation **and without an executable request/token**; …"

이렇게 고쳐도 의무는 늘지 않습니다. 진단을 하지 않는 구현은 계속 허용됩니다. 이미 없는 fresh backup 경로를 검사하라는 요구도 생기지 않습니다("known" 유지).

### 검토했으나 finding으로 올리지 않은 사항

- **A2 "to these writes"(541행)의 선행사 모호성**
  - 이 문장은 accept/apply 쓰기로 좁게 읽힐 여지가 있습니다.
  - 그러나 A7 641행이 "intent/Work/worker/planning writes"를 독립적으로 열거합니다. A13 818행도 "authority/worker publication"을 qualification에 포함합니다.
  - 따라서 reject나 decision 기록이 preflight 밖으로 빠지는 실제 공백은 없습니다. 반례가 없으므로 결함이 아닙니다.
- **A9 748행 문장 순서**
  - 조기 진단 문장이 "its apply must also pass…"와 "Use a new operation identity…" 사이에 끼어 있습니다.
  - 흐름이 약간 끊기지만, "Use a new…"의 주체(허용된 fresh preview/apply)는 오독되지 않습니다. 편집 취향의 문제입니다.
- **A7과 A8의 prefix 표현 차이**
  - A7 641행은 "admitted original prefix", A8 659행은 "actual prefix"라고 씁니다.
  - 실제 prefix는 admitted prefix 안에 있어야 하므로 상충하지 않습니다.
- **489–490행의 연속 빈 줄**
  - GFM 렌더링에 영향이 없는 서식 문제입니다.

## 3. 여섯 사례 대조

| 사례 | 정합한 의미 | 남은 문안 / Owner 선택 | 이후 실제 증거 |
| --- | --- | --- | --- |
| **1. A9/A12 exact 본문** | A9(678–751)에 새 preview 문장(748)과 Qualify 단락(750)이 fence 안에 있습니다. 내부 ```` ```text ```` (687–717)는 4-backtick 안에서 안전합니다. A12(791–803)의 마지막 read-only 단락(802)도 포함됩니다. 두 fence 모두 닫기 직전 빈 줄이 없습니다. 894행은 raw 본문의 trim/공백 정규화 금지와 text 조각의 구분 newline 제외를 구별합니다. 181행은 v0.8 `trimEnd()` 한계를 과거 PASS로 덮지 않고 보존합니다. | 없음(F1은 다른 위치) | 실제 target 문서에 적용했을 때의 heading 계층·위치·렌더링. 예: A7 `##`를 Record Encoding 앞에 넣을 때 후속 `###`가 재부모화되는지. Driver가 로컬에서 대조합니다. |
| **2. Worker preflight 참조** | 참조 한 문장일 뿐 새 범위를 만들지 않습니다. 공통 조건과 기존 guard(541·547)는 그대로입니다. "writes"로 한정되므로 순수 읽기·completed replay에는 미치지 않습니다(A7 643: replay에 gate 없음). 553행 "this mode condition alone does not forbid"도 유지됩니다. 모든 unchanged/retained path 검사로 확장되지도 않습니다(A7 627·641). A3/A4 문구와 criterion 5/8 대응(853·856행)도 유지됩니다. | 없음 | worker accept/apply의 read-only 교체·필수 flush 대상 거절 fixture(A13 818 범위) |
| **3. Preview 조기 진단** | 교체가 필요한 read-only 파일에 대한 필수 규칙은 유지됩니다(740·748 앞부분, A11 782, A12 802: non-pass·no token). 새 문장은 필수 flush 전용 파일에만 적용되는 선택 진단입니다. apply의 전체 preflight를 대체하지 않고, 발급 token의 admissibility 증거성을 명시적으로 부정합니다. pending barrier, 새 identity/backup, 원 retry의 exact 조건은 변하지 않았습니다. 새 backup 경로 사전 검사나 preview mutation은 요구되지 않습니다. | F2(선택): 출력 귀결과 범위 한정 | 진단을 구현한다면 non-pass 출력 형식, 그리고 진단 없이 발급한 token으로 apply가 거절되는 사례 |
| **4. A1–A15 일관성** | 다음 항목들 사이에 규범 상충이 없습니다. <br>• Windows-only window/pairs(A9 681) <br>• verified candidate 기반 repair mode 0/1(736) <br>• 독립 completion(744) <br>• detach4 complete inventory/links/suffix/preserve(A8 661–669, A9 728) <br>• old-reader 증거(A13 820, A14)와 old-writer 거절의 구별 <br>• 명시적 Windows literal/payload 준비와 equality(A9 685, A13 812) <br>Korean S6/S8 요약도 A7/A9와 일치합니다. | F1: 845·864·880행의 상태 문구 | 외부 target 원문과의 대조는 하지 않았습니다(미제공). |
| **5. read-only/flush/NTFS 경계** | 다음이 그대로 유지됩니다. <br>• 교체·제거 대상과 필수 write-capable flush 기존 파일의 합집합을 첫 durable publication 전에 검사(A7 641) <br>• recovery에서 실제 prefix의 required reflush 포함 <br>• pure read/preserve 면제가 bound after 관측을 면제하지 않음(643, A9 744) <br>• allowed-unavailable를 mandatory로 승격하지 않고 flush 생략도 금지(633·641) <br>• same-volume replace와 별도 NTFS backup 구분(629) <br>• scratch·runtime·standard-user 구분(615·758) <br>• 디렉터리 file-flag gate 미도입(643), external receipt 위치 불변 | 없음 | 호출 phase별 API/flag 대응, 실제 flush 실패·drift·중단 prefix(A13 818) |
| **6. B와 공통 조건 worker** | 다음이 유지됩니다. <br>• 대표 UTM full + x64/physical focused, live macOS Preview 이후 formal admission(A6) <br>• 미관측 tuple 표시, 열 가지 criteria(A3/A4는 5·8번만 교체) <br>• 비닫힌 예시, index-only add, 실제 삭제 부재, whole-result 거절, pending/cancel/replay(A2 547–553) <br>새 full matrix, 자동 probe, 권한층은 없습니다. | 없음 | 실제 qualification의 성공·거절 fixture와 tuple 기록 |

## 4. 수락 전 보완, Owner 선택, 이후 증거의 구별

**수락 전 문서 보완**

- F1(필수, 경미): 상태 문구 세 곳을 정리합니다.
- F2(선택): 조기 진단 문장을 다듬습니다.
- 둘 다 계약 의미나 gate를 바꾸지 않습니다.

**Owner 선택**

- 이번 v0.9가 새로 만든 선택은 없습니다.
- 기존 S1–S8 의미와 A1–A15 exact 묶음의 수락 여부는 여전히 Owner가 정합니다. 여기에는 windows-1, 29 paths, pairs, detach4, repair 0/1, read-only/NTFS 경계, PowerShell 5.1 대상이 포함됩니다.
- D08-F1(completed replay)은 Driver가 defend했습니다. 이번 리뷰에서 새 구체 모순은 찾지 못했으므로 재제기하지 않습니다.

**이후 실제 증거(수락을 막는 사유 아님)**

- 실제 target에 적용한 bytes·위치·렌더링
- source/API 대응(flush call site 목록, ticket 발급 경로)
- old-writer 노출 집합
- Windows tuple별 qualification 결과

**해결됐거나 반례가 없는 부분**

- A9/A12 후행 빈 줄 제거
- 새 문장의 fence 내 포함
- raw 검증 설명의 정확성
- A2 참조의 비확장성
- 조기 진단의 선택성과 기존 필수 규칙 보존
- completed replay 무-gate 유지
- 디렉터리 gate·receipt 위치 불변
- B 배정 유지

## 5. 읽지 못한 근거와 잔여 한계

- **입력 범위:** 입력은 frozen packet 한 문서뿐입니다. 링크된 target 문서(Structure, Workspace, General Work, Operations, Reference, Maintaining, Security, Manual, Getting Started, adapter), 제품 source, R1-D08 원문과 Driver 처분, 실험 원출력은 읽지 않았습니다.
- **미검증 주장:** 다음은 확인하지 않은 Driver 보고로만 취급했습니다.
  - 문서 안의 source 인용(`_stable_file`, `candidate_release`, detach plan null 등)과 D08-F1 defend 근거
  - 894행의 메모리상 적용·렌더링 검사 결과
- **byte 수준 확인 한계:** packet의 줄 번호와 fence는 주석입니다. 각 줄 끝의 후행 공백·탭이나 CR 유무는 packet 표시만으로 확인할 수 없습니다. 174,893 bytes와 SHA-256 일치도 재계산하지 않았습니다.
- **heading 계층:** 삽입 위치의 heading 계층 정합성은 target 원문 없이 판단할 수 없습니다. 예: A7 `##`와 A2 `###`가 주변 절과 맞는지.
- **판정의 성격:** 이번 판정은 재현이나 PASS가 아닙니다. 계약 수락, 제품 실행, activation의 근거로 쓰지 않습니다.
````

### R1-D09 Record Verification And Retention

검증 PASS: 작성 문서 3개, local path/heading link 100개, marked 17.0.5 GFM·code 밖 literal 강조 기호·whitespace·disclosure를 확인했다. R0·R1-P01·R1-D01–D09의 frozen request/packet/final과 verbatim 11회, Driver 처분 2개, exact v0.9 packet 복구·Draft 불변, 허용 기록 외 baseline 입력 54개 불변, 이전 CHORE/private context 보존, S1–S8·열 가지 criteria·15개 clause·빈 accepted-only 절, A2/A9/A12 raw bytes와 기존 source HEAD/navigation/untracked를 확인했다. F1/F2의 reviewed 문구는 그대로 남아 있으며 이 기록 검증이 그 지적의 해결이나 전체 의미 정합성을 뜻하지 않는다. 제품 실행·Windows qualification은 수행하지 않았다.

정리 완료: CLI 종료와 최종 응답 통합·중복 bytes 일치, 빈 stderr/tool-temp, lsof no-use를 확인한 뒤 partial·빈 stderr·빈 tool-temp·일회성 checker·검사 보고서 5개를 삭제했다. request·packet·입력 식별자·final·최소 metadata·호출 script 6개는 Owner 처분과 다음 exact 비교/준비를 위해 보존한다. 후속 reviewer 호출은 승인하지 않았다. 기존 worktree·VM·probe 증거·마지막 복구 사본의 결과 수락/복원/구체 후속 소비자와 종료 조건은 유지하며 active path 변경은 없다. 삭제 후 최종 기록을 포함해 메모리에 보관한 checker로 재검증했고 출력 파일은 재생성하지 않았다.


## Contract Draft Revision 0.10 — 2026-10-18

Owner는 “R1-D09과 네 판단을 반영해 DR-0007을 v0.10으로 보완해줘. 상태 문구 세 곳을 실제 리뷰 이력에 맞추고, 조기 진단을 fresh repair preview로 한정해 non-pass일 때 실행 request/token이 없음을 명시해줘. B안과 공통 조건 중심 worker 지원은 유지하고 추가 실험이나 제품 구현은 시작하지 마.”라고 요청했다. 이 요청은 Draft와 기존 진행 기록의 문서 보완을 승인하며 계약 수락·제품 실행·추가 실험·reviewer 호출은 포함하지 않는다.

D09-F1의 실제 오류 세 곳을 고쳤다. admission 대응표는 현재 revision을 가리킨다. Open Points의 개정 설명과 리뷰 상태는 v0.9가 R1-D09 리뷰를 받았다는 이력, v0.10이 그 처분을 반영했으나 아직 독립 재리뷰·Owner 계약 수락을 받지 않았다는 상태를 명시한다. 리뷰 당시 제시된 v0.9 미재리뷰 예문을 그대로 복사하지 않았다. 현재 개요·promotion·검증 문구도 같은 상태에 맞췄다.

D09-F2는 A9의 기존 선택 진단 한 문장만 보완했다. fresh repair preview가 이미 확인한 read-only 필수 flush 대상을 non-pass로 알릴 때 mutation과 실행 request/token이 없음을 명시했다. 선택 진단을 새 필수 sweep/gate로 만들지 않았으며 apply의 전체 사전 검사와 token의 증거 한계는 유지한다. A9의 해당 문장 외 A1–A15 본문, B·S1–S8·공통 조건 중심 worker 지원·비닫힌 예시와 기존 defend 처분은 그대로다.

기존 Owner 원문·리뷰·개정 이력과 accepted-only 빈 절을 보존했다. v0.9 exact bytes는 R1-D09 frozen packet에서 복구할 수 있다. v0.10은 아직 독립 재리뷰·Owner exact 수락·qualification·activation을 받지 않았다. STATUS·catalog·PLAN·normative 계약·제품·VM·probe·Git publication은 변경하지 않는다.

Draft identity: 177,174 bytes; SHA-256 `cd6f3bf06d842afb8f71aac98e95382acc04b4524ee54b80af179b11ad0c3add`. 이번 입력 식별자와 bounded revision diff는 Owner 비교 및 다음 명시적으로 선택한 exact 리뷰 처분까지 보존한다. 일회성 작성·검사 파일은 검증·no-use 확인 후 정리한다. 기존 필수 evidence/last recovery의 소비자·종료 조건과 active path는 유지한다.

문서 검증: 3개 문서·local link 101개·GFM 강조 렌더링·whitespace·disclosure 확인 PASS. A1–A15 raw fence 본문을 trim/공백 정규화 없이 11개 메모리상 target에 적용해 16개 배치(A15는 두 곳)의 bytes·위치·heading 중복과 A12의 파일 끝을 확인했다. A9의 허용한 한 문장만 역치환하면 15개 기존 절 모두 일치하고, 18개 보호 절·기존 Owner 원문 순서·S1–S8·열 가지 admission 대응·accepted-only 빈 절을 보존했다. 현재 상태 세 곳과 개요·promotion·검증 문구는 실제 v0.9/R1-D09 및 새 v0.10의 미재리뷰·미수락 경계에 맞는다. 역사적 revision 이력은 수정하지 않았다.

60개 입력 중 허용된 Draft·진행 정본·task record 외에는 drift가 없었다. 11개 기존 review의 request/packet/final hash와 원문, v0.9 exact 복구 및 bounded diff, 이전 진행 기록 bytes와 task record prefix를 확인했다. 제품을 import하지 않고 AST로 확인한 membership은 기존 29개와 동일하다. source HEAD·기존 navigation diff·untracked 집합이 유지됐다. 이 PASS는 문서 검증이며 독립 리뷰·Owner 수락·제품 qualification을 뜻하지 않는다.

정리: 소유·no-use와 필요한 검증 기록 보존을 확인한 뒤 이번 일회성 작성 스크립트·검사기·중간 JSON 보고서 3개를 삭제했다. 입력 식별자와 revision diff 2개는 Owner 비교 및 다음 명시적으로 선택한 exact 리뷰 처분까지 보존한다. 기존 worktree·VM·probe·review 원출력·last recovery는 기록된 소비자와 종료 조건이 남아 유지한다. active path는 변경하지 않았다. 삭제 후 메모리에 보유한 검사기를 다시 실행해 같은 문서 검증 PASS와 정리 결과를 확인했다.


## R1-D10 — Draft 0.10 Static Re-review — 2026-10-18

Owner는 “DR-0007 v0.10을 Claude CLI로 재리뷰해줘. 상태 문구와 실제 리뷰 이력, fresh repair preview의 non-pass 시 실행 request/token 부재, A1–A15 정합성을 확인하고 네 판단도 정리해줘. B안과 공통 조건 중심 worker 지원은 유지하고 추가 실험이나 제품 구현은 시작하지 마.”라고 요청했다. 이번 범위는 지정 Draft의 정적 재리뷰, 실제 리뷰 이력 대조, Driver 판단과 기존 진행 기록의 갱신이다. Draft 본문 수정·계약 수락·추가 실험·제품 구현은 포함하지 않는다.

### Invocation And Evidence Boundary

- 공통 review procedure와 cross-review 기록 절차를 읽고 Owner가 명시한 직접 Claude CLI 경로를 사용했다. CLI 2.1.302의 `claude.ai / firstParty / pro`와 provider override 부재를 확인했다. sandbox 내부 인증 조회에서는 로그인 상태를 읽지 못했으나 scoped credential 접근으로 기대한 구독 경로를 확인한 뒤 호출했다. 비밀값·계정 email은 기록하지 않았다.
- 실제 모델은 `claude-opus-5-5`, 새 session은 `0d3eaee2-4fb8-47e0-ab21-8e342fba77e8`다. 모델 override 없이 no-tools·strict empty MCP·세션 비보존으로 호출했다. 1,200초 상한 내 97.897초, exit 0, tool event 0, 입력 두 개의 전후 drift false였다.
- 주 입력은 exact Draft 0.10, 177,174 bytes; SHA-256 `cd6f3bf06d842afb8f71aac98e95382acc04b4524ee54b80af179b11ad0c3add`다. 실제 이력 대조를 위해 이 정본의 R1-D09 라운드 2726–2911행을 함께 제공했다. 해당 발췌 안의 reviewer 원문은 기존 final/hash와 대조했다. numbered frozen packet은 206,047 bytes; SHA-256 `fbc0538205697b20da5a6620b4827d3cca01a3259164f425165d53c6e9aba112`다.
- request SHA-256은 `211b3f720e849080fcc611a806ca976330a9a92ca73a9eabac15286ad241fb0a`, 최종 응답은 10,936 bytes/SHA-256 `a5e719d52df72969bb0d2e2f613a6e30c4647ffb11c8378e01013b36be867f77`다. request·packet·입력 식별자·final·최소 metadata·runner는 기존 task의 R1-D10 경로에 보존한다.
- Reviewer는 linked target·제품 source·실험 원출력·v0.9 원문·다른 라운드 원문을 읽지 않았다. R1-D09 기록을 문맥으로 제공했으므로 완전한 blind review도 아니다. 아래 byte/source 대조는 Driver의 별도 정적 확인이며 Claude의 실행 결과나 Windows qualification이 아니다.

### Reviewer Verdict

전체 exact 문서 수락 준비도, 상태와 실제 이력, fresh repair preview의 non-pass 출력, A1–A15 규범 본문, B/공통 조건 worker, 문서 기반 계획 준비가 모두 **approve** 판정이다. 신규 P1/P2/P3 finding, must-fix, 선택 보완은 모두 없다. Reviewer는 R1-D09 F1/F2가 해소됐고 추가 문서 개정은 필요 없다고 판단했다. 이 verdict는 Owner 계약 수락이나 제품 실행 승인과 구별한다.

### Driver Judgment And Disposition

신규 finding이 없어 개별 finding 처분은 없다. Driver는 이번 approve와 추가 개정 불필요 권고에 동의한다. 근거와 적용 범위는 다음과 같다.

| 검토 대상 | Driver 판단 |
| --- | --- |
| 실제 리뷰 이력 | v0.9/R1-D09의 완료 metadata와 원응답 hash를 대조했다. 전체 conditional·세부 approve·P1/P2 0·P3 2라는 v0.10 설명은 실제 결과와 맞는다. Mapping은 현재 revision을 가리키며 Open Points는 완료한 v0.9 리뷰와 당시 새 v0.10의 상태를 구별한다. |
| 조기 진단의 범위와 출력 | A9 761행은 fresh repair preview가 이미 확인한 mandatory write-capable flush 대상의 read-only 상태를 선택적으로 non-pass로 반환할 때 mutation과 executable request/token이 없음을 명시한다. 선택 진단을 수행하지 않았다는 사실과 non-pass 결과를 반환했다는 사실은 다르다. 발급 token이 apply 가능성을 보장하지 않으며 전체 preflight는 apply에 유지된다. |
| 필수 거절·기존 계약 | 교체가 필요한 read-only 파일이 남은 fresh preview의 필수 non-pass/no-token은 A9/A11/A12에 남는다. optional 진단과 상충하지 않으며 original exact retry, pending, 새 identity/backup, 이전 evidence 보존, 자동 fallback 금지도 유지된다. 기존 completed replay·First B1 defend 처분을 바꿀 새 반례는 확인하지 못했다. |
| 현재 기록과 후속 선택 | v0.10 본문의 미재리뷰 문구는 작성 당시 상태로 보존하고 이 dated 라운드가 그 이후의 실제 완료를 기록한다. 이 이유만으로 v0.11을 만들 필요는 없다. Owner가 exact 계약을 수락할 때 해당 범위와 수락 기록을 정리하며, 이번 리뷰 자체로 상태를 Accepted로 바꾸지 않는다. |

### Driver Static Check And Limits

- R1-D09 frozen packet에서 v0.9를 정확히 복구해 v0.10과 비교했다. A1–A15 중 A9의 선택 진단 한 문장만 +55 bytes이며 그 문장을 역치환하면 기존 본문과 일치한다. 나머지 14개 amendment와 S1–S8은 동일하다.
- A2 raw Markdown은 4,206 bytes/SHA-256 `af38eb247497cebd8aa97ce0ff47d4c94d9375b7501e8d10104ca9047ed7c737`, A9는 12,090 bytes/`2fe8b9a267156f4ab380a4e71e565c7cdf3f575e9c8b1df90948ebc4047aab6f`, A12는 3,547 bytes/`569f9be5974cbe00abb9f9d5b6661f3f537a90016eb65b809d9021b0562b1cf4`다. 마지막 LF를 포함하고 trim하지 않았다. A9/A12의 마지막 단락은 fence 안에 있고 여분 후행 빈 줄이 없다.
- v0.10 작성 단계의 15개 raw clause·11개 메모리상 target·16개 배치 검증 결과를 재사용한다. 이번 라운드 시작에 허용된 기록을 뺀 57개 입력이 그 baseline과 동일함을 확인했으며 검토 대상 Draft도 불변이다. 실제 normative 파일에 적용하거나 제품을 실행한 결과가 아니다.
- [product.py](../../src/hv2ref/product.py)의 1597–1603행은 현재 fresh repair backup 목적지가 없어야 함을 요구하고, 1622–1625행의 성공 경로는 request/confirm_token을 반환한다. 이 정적 확인은 미구현 Windows 조기 진단의 실제 출력·허용 조건을 검증한 것이 아니다. 새 문안이 기존 backup의 존재를 강제하거나 없던 실행 성공을 주장하지 않는다는 경계로만 사용했다.
- 열 가지 admission 기준, B의 대표 UTM full·x64/physical focused 배정, live macOS Preview 이후 formal admission과 공통 조건 중심 worker 지원은 유지한다. source/artifact·tuple·API/실패 주입·old writer·reader 양방향 검증은 이후 qualification에서 다룰 실제 증거다.

### Recommended Next Boundary

추가 문구 개정 없이 [DR-0007 v0.10](../decisions/DR-0007-windows-native-runtime-contract.md)을 exact Owner 계약 수락 검토 대상으로 제시할 수 있다. 대상은 S1–S8의 구체 의미와 A1–A15 named amendment 묶음이다. 이 판정은 B 방향 유지 외에 미수락 세부를 자동 채택하지 않으며 제품 실행 승인은 별도로 남는다. 문서 기반 계획 준비는 가능하지만 이번 요청으로 새 계획·제품 작업을 시작하지 않는다.

Draft 0.10은 검토한 bytes 그대로 유지했다. 추가 reviewer·실험·제품 suite·VM/probe·normative 계약·STATUS·catalog·PLAN·Git publication 변경은 없다.

### Reviewer Response Verbatim

````markdown
# R1-D10 — DR-0007 Draft 0.10 정적 재리뷰

## 1. 판정 요약

이 판정은 제공된 packet만 읽은 정적 리뷰입니다. Owner의 계약 수락, 제품 실행 승인, qualification 또는 activation이 아닙니다.

| 항목 | 판정 | 근거 요약 |
| --- | --- | --- |
| 전체 exact 문서 수락 준비도 | **approve** | 수락 전에 고칠 결함이 없습니다. R1-D09의 F1/F2가 의도한 범위에서 해소됐고, 새 상충 문구나 정적 반례가 없습니다. Owner가 exact 수락 여부를 판단할 수 있는 상태입니다. |
| 상태 문구와 실제 리뷰 이력 | **approve** | 36·82·191·858·877·893·899행이 R1-D09 기록(2739행)과 맞습니다. R1-D09는 v0.9에 대해 전체 conditional, 세부 항목 approve, P1/P2 0건, P3 2건으로 판정했습니다. v0.10은 작성 시점에 미재리뷰·미수락 후보로 구별됩니다. |
| fresh repair preview의 non-pass 출력 | **approve** | 761행이 대상을 fresh repair preview로 한정합니다. non-pass이면 mutation과 executable request/token이 모두 없다고 명시합니다. 진단은 선택이고, apply preflight를 대체하지 않으며, 발급 token은 apply 허용 증거가 아니라는 단서도 유지됩니다. |
| A1–A15 정합성 | **approve** (규범 본문, packet 한정) | 실질 상충이 없습니다. 실제 target에 적용한 결과는 확인하지 않았습니다. |
| B / 공통 조건 worker | **approve** | 변경이 없고, 확장이나 축소도 없습니다. |
| 문서 기반 계획 준비 | **approve** | 문서 수락 준비와 실제 지원 선언이 구별돼 있습니다. |

## 2. Findings

**Must-fix: 없음. 선택 보완: 없음.**

후속 revision을 만들 만한 구체 상충이나 오해 경로를 찾지 못했습니다. 아래는 검토했지만 finding으로 올리지 않은 사항입니다.

- **"아직 독립 재리뷰를 받지 않았다"(36·893·899행)는 결함이 아닙니다.**
  - D09-F1의 결함은 달랐습니다. v0.9 작성 시점에 이미 R1-D08이 끝났는데도 v0.8을 미리뷰로 적어, 작성 당시에도 거짓이었습니다.
  - 이번 문구는 v0.10 작성 시점에는 사실입니다.
  - 이번 R1-D10 완료로 이 서술이 역사적 설명이 되는 것은 개정 사유가 아닙니다. 진행 정본에 기록하면 충분합니다. 이를 이유로 v0.11을 요구하면 리뷰할 때마다 새 revision이 필요한 순환이 생깁니다.
- **36행의 "A1–A15 정합성 … approve"**
  - R1-D09 원문(2779행)은 "approve (규범 본문)"이라는 한정을 붙였습니다.
  - 36행은 같은 문장 뒤에서 상태 문구 세 곳의 오류를 따로 적습니다. 따라서 규범 본문 밖까지 승인받았다는 오해 경로는 약합니다.
  - 압축 표현의 차이일 뿐 결함은 아닙니다.
- **A11(795행)과 A12(815행)는 선택 조기 진단을 언급하지 않습니다.**
  - 선택 진단이므로 Operations/Reference가 반복할 의무가 없습니다.
  - A12는 필수 flush 대상 read-only 파일을 이미 "policy-level unsupported for the whole proposed operation"으로 분류합니다. 조기 non-pass 보고와 상충하지 않습니다.
- **A9 761행의 문장 인접 관계**
  - "without an executable request/token" 바로 뒤에 "Use a new operation identity, canonical request/token…"이 이어집니다.
  - 뒤 문장의 주체는 앞에서 허용된 fresh preview/apply이므로 오독 경로가 없습니다. R1-D09와 같은 편집 취향 문제입니다.
- **194행의 한국어 설명** "이미 확인한 read-only 필수 flush 대상"은 영어 본문의 "known"과 같은 범위입니다.
- **502–503행의 연속 빈 줄**은 GFM 렌더링에 영향이 없는 서식 문제입니다.

## 3. 여섯 사례 대조

| 사례 | 정합한 의미 | 남은 문안 / Owner 선택 | 이후 실제 증거 |
| --- | --- | --- | --- |
| **1. 상태와 실제 이력** | 36행은 R1-D09의 판정 구성, P3 두 건, Driver 처분(상태 오류 인정, F2 최소 보완), D08-F1 defend 유지를 기록(2739–2746행)과 일치하게 요약합니다. 82행의 v0.9 bytes·SHA와 R1-D09 응답 SHA는 기록 2734·2735행과 같습니다. 858행 Mapping은 "현재 revision"을 가리킵니다. 877행 Open Points는 "v0.9는 R1-D09를 받았고 v0.10은 … 보완"이라고 적습니다. 893행은 실제 완료 리뷰와 v0.10 미리뷰를 구별하고, defend·비채택 항목의 미반영을 명시합니다. 899행은 이전 판정을 재사용하지 않습니다. 이전 revision 표와 Owner 인용(40–82, 84–194행)은 역사로 남습니다. | 없음. R1-D10 완료는 진행 정본에 기록하면 됩니다. | 없음 |
| **2. fresh repair preview 조기 진단** | 761행에서 "A fresh repair preview may"는 대상을 repair로 한정합니다. "known"이므로 존재하지 않는 새 backup 경로를 검사할 의무가 생기지 않습니다. "may"이므로 모든 lifecycle preview의 필수 sweep이나 gate가 되지 않습니다. non-pass 시 mutation과 executable request/token이 모두 없습니다. "neither replaces apply's whole-operation preflight nor makes an issued token proof of apply admissibility"가 그대로입니다. 진단 없이 발급한 token이 apply에서 거절될 수 있다는 의미도 유지됩니다. 192·194행의 설명도 같은 범위입니다. | 없음 | 진단을 구현할 경우 non-pass 출력 형식. 진단 없이 발급한 token으로 apply 시 전체 preflight 거절이 일어나는 fixture |
| **3. 필수 refusal과 retry** | read-only 교체 대상이 남은 fresh preview는 필수로 non-pass이며 token이 없습니다(753·761 앞부분, A11 795, A12 815, S6 390, S8 420/422). 표현은 "is non-pass"로, "may"를 쓰는 선택 진단과 구별됩니다. 다음 의미도 보존됩니다. <br>• 원 exact retry: 외부 복원 뒤 재판정할 수 있으나 모든 exact 조건이 필요 <br>• 실제 pending barrier를 우회하지 않음 <br>• 새 identity, request/token, backup 사용 <br>• previous evidence 보존 <br>• 자동 re-preview/apply와 속성 해제 금지 | 없음 | read-only가 남은 fresh-preview 거절, admissible fresh preview, pending 거절, 외부 복원 뒤 retry fixture(A9 763, A13 831) |
| **4. A1–A15 정합성** | 다음 사이에 상충이 없습니다. <br>• Windows-only window/pairs(694) <br>• verified candidate 기반 repair 0/1(749–753) <br>• 독립 completion(757) <br>• detach4 inventory/links/suffix/preserve(A8 674–682, A9 741) <br>• old-reader 증거(A13 833, A14)와 old-writer 거절의 구별 <br>• 명시적 literal/payload 준비와 equality(698, A13 825) <br>• Korean S6/S8 요약, Mapping 2·6행, Open Points repair 행 <br>A9(691–764)와 A12(804–816)는 마지막 단락까지 fence 안에 있고, 닫는 fence 앞에 여분 빈 줄이 없습니다. 내부 ```` ```text ````(700–730)는 4-backtick 안에서 안전합니다. 907행은 raw 적용 검사를 Driver 검증으로 설명할 뿐 target heading이나 byte 적용을 Reviewer가 검증했다고 표시하지 않습니다. | 없음 | 실제 11개 target에 적용한 bytes, 위치, heading 계층, 렌더링(Driver 담당) |
| **5. worker / read-only / flush / NTFS** | 다음이 그대로 유지됩니다. <br>• A2 554행의 operation-specific preflight 참조 <br>• 비닫힌 예시(560) <br>• 교체·제거 대상과 필수 write-capable flush 기존 파일의 합집합 검사(654) <br>• recovery에서 실제 prefix의 required reflush <br>• pure read/preserve 면제가 bound after 관측을 면제하지 않음(656, 757) <br>• allowed-unavailable를 mandatory로 승격하지 않고 flush 생략도 금지 <br>• completed replay에 gate나 reflush를 추가하지 않음 <br>• First B1 보존 <br>디렉터리 file-flag gate는 도입하지 않았고(656), external receipt 위치도 바뀌지 않았습니다(761). | 없음 | phase별 API/flag 대응, 필수 flush call site 목록, 실제 flush 실패·drift·중단 prefix |
| **6. B와 계획 준비** | 대표 UTM full과 x64/physical focused 배정, live macOS Preview 뒤 formal admission(A6, 221)이 유지됩니다. 미관측 tuple 표시와 열 가지 기준(A3/A4는 5·8번만 교체)도 유지됩니다. Owner exact 수락, 실행 승인, qualification, activation이 서로 분리됩니다(29–31, 897–903). 문서 수락 준비와 지원 선언이 구별됩니다(24, 36, 911). | 기존 S1–S8, A1–A15 exact 수락 여부 | 실제 tuple별 qualification 결과와 old-writer 노출 집합 |

## 4. 추가 개정 필요성과 남은 경계

**추가 문서 개정은 필요 없습니다.**
- R1-D09가 제기한 상태 문구 세 곳(현재 858·877·893행)과 F2 최소안(761행)이 반영됐습니다.
- 새 gate나 절차는 추가되지 않았습니다.
- 이번 R1-D10의 완료 사실, 판정, Driver 처분은 기존 진행 정본(CHORE-20261017-001)에 dated 기록으로 남기면 충분합니다.

**나중에 정리할 서술:** Owner가 수락하면 status와 Decision/Rationale/Consequences를 채우는 수락 개정에서 bytes가 어차피 바뀝니다. 그때 36·893·899행의 "아직 … 받지 않았다"를 역사 서술로 정리하면 됩니다. 지금 이를 위해 revision을 만들 필요는 없습니다. 그 수락 개정의 리뷰 범위는 기존 source procedure와 Owner 판단에 따릅니다.

**남은 exact Owner 선택:**
- S1–S8의 의미
- A1–A15 묶음: windows-1/profile, 29 paths, init1/switch2/repair1/detach4, repair 0/1, read-only/NTFS 경계, PowerShell 5.1 대상, old-writer 처분
- 별도의 제품 실행 승인

**이후 실제 qualification:**
- 실제 artifact와 tuple
- old-writer 노출과 거절
- API phase와 실패 주입
- reader 양방향 검증
- 조기 진단 구현 시 출력 형식

이 항목들은 문서 수락을 막는 사유가 아닙니다.

## 5. 읽지 못한 근거와 잔여 한계

- **입력 범위:** 입력은 Draft 0.10 전문과 R1-D09 기록 발췌뿐입니다. linked target 문서, 제품 source, 실험 원출력, v0.9 원문, 다른 라운드 원문은 읽지 않았습니다.
- **diff 범위:** "v0.10의 기술 본문 변경은 A9 한 문장뿐"이라는 설명은 v0.9 bytes 없이 확인할 수 없는 Driver 보고입니다. 저는 현재 문안의 내부 정합성과 R1-D09가 지적한 위치의 해소만 확인했습니다.
- **byte 수준:** 177,174 bytes와 SHA-256은 재계산하지 않았습니다. 줄 끝의 후행 공백, 탭, CR 유무는 packet 표시로 판단할 수 없습니다.
- **Driver 보고로만 취급한 내용:**
  - 80행의 Owner 원문 인용
  - 907·911행의 메모리상 적용과 렌더링 검사
  - source 인용(`_stable_file`, `candidate_release` 등)
- **판정의 성격:** 이 판정은 재현이나 Windows PASS가 아니며, 계약 수락, 제품 실행, activation의 근거가 아닙니다.
````

### R1-D10 Record Verification And Retention

검증 PASS: 작성 문서 3개·local path/heading link 103개, marked 17.0.5 GFM·code 밖 literal 강조 기호·whitespace·disclosure를 확인했다. R0·R1-P01·R1-D01–D10의 request/packet/final hash와 verbatim 12회, 신규 finding 없음과 Driver 판단의 구별, exact v0.10 packet 복구 및 Draft 불변, 실제 제공한 R1-D09 발췌의 원래 줄·bytes·범위, 기존 CHORE/task record 보존을 확인했다. 60개 baseline 입력 중 허용된 기록을 뺀 57개가 불변이며 A1–A15·S1–S8·열 가지 criteria·accepted-only 빈 절, A2/A9/A12 raw bytes와 source HEAD/navigation/untracked도 유지됐다. 이전 v0.10의 raw 11-target 검증을 재사용했으며 제품 실행·Windows qualification은 하지 않았다.

정리 완료: CLI 종료·partial/final bytes 일치·빈 stderr/tool-temp·lsof no-use를 확인한 뒤 중복 partial, 빈 stderr와 tool-temp, 일회성 검사기와 JSON 보고서 5개를 삭제했다. request·packet·입력 식별자·final·최소 metadata·runner 6개는 Owner의 exact 계약 처분과 그 수락 준비 시 비교를 위해 보존한다. 새 reviewer 호출 권한은 포함하지 않는다. 기존 worktree·VM·probe·리뷰 원출력·마지막 복구 자료는 기록된 결과 수락/복원/구체 후속 소비자와 종료 조건이 남아 유지한다. active path 변경은 없다. 최종 기록과 실제 삭제 뒤 메모리상 checker를 다시 실행해 PASS를 확인했고 출력 파일은 재생성하지 않았다.


## Owner Contract Acceptance And Follow-Up Plan — 2026-10-18

Owner는 “DR-0007 v0.10의 S1–S8과 A1–A15 계약을 수락할게. 수락 기록을 정리하고 후속 구현·검증 계획을 작성해줘. B안과 공통 조건 중심 worker 지원은 유지하고, 추가 실험이나 제품 구현은 아직 시작하지 마.”라고 요청했다.

### Accepted Scope And Effect

[DR-0007 수락 기록](../decisions/DR-0007-windows-native-runtime-contract.md#owner-contract-acceptance--2026-10-18)은 R1-D10 대상 v0.10의 177,174 bytes, SHA-256 `cd6f3bf06d842afb8f71aac98e95382acc04b4524ee54b80af179b11ad0c3add` 중 S1–S8과 A1–A15를 식별한다. 그 raw 본문과 referenced exact 의미를 유지하며 status를 Accepted로 바꾸고 Decision/Rationale/Consequences를 채웠다. 수락 metadata를 추가한 현재 문서 identity는 원 수락 대상과 구별한다. 기존 R1-D10 packet에서 원 v0.10 전체 bytes를 복구할 수 있다.

수락은 후속 Windows 구현·검증의 계약 기준을 확정한다. entry-1·First B1의 현재 activation, 실제 normative 기술 본문·runtime allowlist·제품 source·managed payload는 변경하지 않았다. 제품 실행·qualification·결과 수락·별도 activation, live macOS Preview 이후 formal admission과 Git/adopter action은 남아 있다. 기존 probe 결과 수락·VM 복구나 정리도 이번 요청에서 추정하지 않는다.

### Follow-Up Plan Prepared

[계획 v0.1](windows-native-implementation-plan.md)은 P0 통제/입력 → P1 native 기반 → P2 lifecycle·content·worker → P3 문서/artifact 통합 → P4 qualification → R1·결과 수락/activation 순서를 제시한다. 실제 source 책임, A1–A15와 admission 1–10의 검증 대응, tuple·노출 writer·ID ledger·예산·macOS 회귀·보존/중단 조건을 포함한다. API 문서는 정적 설계 입력이며 실행 성공을 주장하지 않는다.

이 계획은 아직 R0·실행 승인을 받지 않았다. 새 구현 task ID나 runtime Work를 만들지 않았으며 문서 준비의 진행 정본은 이 CHORE다. 향후 선택 때 기존 source procedure에 따라 하나의 구현 진행 기록을 지정한다. 자동으로 reviewer·제품·VM을 실행하지 않는다.

### Prepared Document Identities

| 파일 | UTF-8 bytes | SHA-256 |
| --- | ---: | --- |
| `docs/decisions/DR-0007-windows-native-runtime-contract.md` | 181284 | `e7679a8e11b5e38171888ab6da748cabd6ad5e46dc84e48205733a8e0e6d9ede` |
| `docs/development/windows-native-implementation-plan.md` | 22882 | `64e17e0a01cb2e2246f7efcb78090c789b5cb67dcf81a95845abe0fb4b609d9b` |
| `docs/DECISION-GUIDE.md` | 11761 | `19a548aacc74fd743bb3ea614315e8fb3848aeca043a44ccfaf08d7e24145238` |
| `docs/development/README.md` | 47761 | `600fe244becb5535487dfd9360440fa003a0138790794a31b83fe4a1415e9fec` |

위 값은 수락 기록·계획 준비 시점의 결과이며 이후 자체 검증 기록을 덧붙이는 이 CHORE의 hash를 순환 참조하지 않는다. Decision Catalog는 DR-0007 한 행만 추가했다. Development Index는 기존 Windows probe navigation 한 문단만 교체했고, admission의 기술 기준은 그대로다. bounded diff는 source-owned 문서 네 건의 변경을 복구 가능하게 보존한다. 기존 이력·원문과 나머지 source 입력의 불변은 아래 검증 결과에서 확인한다.

### Acceptance Record And Plan Verification

- GFM parser `marked 17.0.5`로 source 문서 5개와 private 보존 기록 1개를 렌더링했다. 로컬 링크/anchor 170개, code 밖 literal 강조 기호, trailing whitespace, source 문서의 식별 정보 노출 검사에서 오류 0개였다.
- 수락된 S1–S8 전체와 A1–A15 전체(placement 설명 포함), 이전 Owner 인용·개정 이력의 세 구간이 원 v0.10 bytes와 동일하다. R1-D10 packet에서 원 177,174 bytes와 지정 SHA-256을 복구했다. 네 문서 bounded diff를 메모리에서 역적용해 변경 전 문서와 새 계획의 부재를 정확히 복구했다.
- 기존 R0·R1-P01·R1-D01–D10의 12개 리뷰 원문과 frozen 입력/응답 identity를 확인했다. 이전 CHORE는 현재 상태 두 줄을 역치환하고 이번 append를 제외하면 변경 전 SHA-256과 같으며 private 기존 기록도 불변이다.
- 허용된 기록 변경을 제외한 입력 238개가 동일하다. 제품 source·tests·launcher·managed payload와 기존 normative 기술 본문은 불변이다. tracked 변경은 Decision Catalog와 Development Index뿐이고, 기존 미추적 문서 세 개에 새 계획 한 개만 추가되었다. `git diff --check`도 통과했다.
- 계획은 12개 검증 묶음으로 수락 계약과 admission 기준을 연결했다. 이는 계획의 문서 확인이며 의미적 완전성을 증명하는 독립 R0나 실제 Windows/macOS test 결과가 아니다. 계획 R0·실행 승인, 구현·qualification·activation은 남아 있다.
- 보존: 수락 입력 identity와 기존 navigation diff, 네 문서 bounded diff, 문서 검증 결과/검사기는 exact 수락 복구와 계획 R0 입력 고정 때의 drift 확인을 위해 유지한다. 다음 검토 입력이 고정되어 소비가 끝나면 필요성을 다시 평가한다. 기존 source·probe·review·VM recovery의 소비자는 그대로다.
- 정리: 다른 process가 사용하지 않음을 확인한 일회성 수락 기록 작성 script 한 개를 삭제했다. source/활성 입력·출력 경로 이동, worktree·VM·branch 삭제는 없었다. 필수 계약·계획과 마지막 복구 근거는 보존했다.


## R0-I01 — Implementation Plan v0.1 Review And Driver Judgment — 2026-10-18

Owner는 “후속 구현·검증 계획 v0.1을 Claude CLI로 R0 리뷰해줘. DR-0007 v0.10과의 정합성, 구현 순서·검증 범위·실행 경계를 확인하고 네 판단도 정리해줘. B안과 공통 조건 중심 worker 지원은 유지하고, 추가 실험이나 제품 구현은 아직 시작하지 마.”라고 요청했다. 이번 범위는 지정 계획의 Claude CLI 정적 R0 한 회와 Driver의 대조·처분 기록이다. 계획/계약 개정, 제품·test·runner 구현, 추가 실험·VM 실행과 Git publication은 포함하지 않는다.

### Verdict And Driver Assessment

Reviewer의 전체 판정은 conditional이다. P1 must-fix 2건(F1/F2), P2 must-fix 8건(F3–F10), P3 선택 보완 3건(F11–F13)을 제시했다. 계약 정합성·구현 순서·검증 범위·실행 경계·실행 승인 검토 준비도는 모두 conditional이며, DR-0007을 바꿔야 할 계약 충돌은 찾지 못했다.

Driver도 계획 보완 후 실행 승인을 검토하는 순서에 동의한다. 핵심은 다섯 묶음이다.

1. 플랫폼별 test 기대값·적용 범위를 정하고 native import/discovery를 먼저 성립시킨다.
2. Windows source 준비와 최초 candidate를 lifecycle 검증 전에 놓고, flush 의무·실제 노출 old writer를 초기에 확인한다.
3. doctor/status/view, worker mode 변경, repair·detach의 필수 사례를 exact 계약과 실제 test ID에 연결한다.
4. Windows fixture·macOS runner·증거 반출·재시도 한도를 실행 전에 고정한다.
5. 개발 검증, published/refetched artifact 검증, activation·formal admission의 완료 범위를 구별하고 shared managed 문서 변경을 추적한다.

B안과 공통 조건 중심 worker 지원은 그대로 유지한다. Reviewer의 처방을 전부 그대로 채택하지는 않는다. 모든 test ID에 새 분류 체계를 강제하거나, 실제 노출과 무관한 모든 old-writer 경로를 시험하거나, 새 worktree·관리자/네트워크 권한·local commit을 자동으로 허용하는 확대는 권고하지 않는다.

### Invocation And Exact Inputs

- 공통 review procedure와 workflow-cross-review 기록 절차를 따랐고, Owner가 명시한 직접 Claude CLI 경로를 사용했다. CLI 2.1.302 (Claude Code)의 기존 `claude.ai / firstParty / pro` 인증을 확인했다. sandbox 내부 조회에서는 로그인 정보를 읽지 못했지만 scoped Keychain 접근에서 정상임을 확인했으며 provider override는 없었다. 계정 email·비밀값은 기록하지 않았다.
- 실제 model은 `claude-opus-5-5`, fresh session은 `a3512ac1-bc49-4a8a-ba58-cb0217f51fc1`다. model override 없이 no-tools·strict empty MCP·세션 비보존으로 호출했다. 1,200초 상한 내 335.563초, exit 0, tool event 0, 입력 6개 전후 drift false였다.
- 주 대상은 계획 v0.1의 22,882 bytes, SHA-256 `64e17e0a01cb2e2246f7efcb78090c789b5cb67dcf81a95845abe0fb4b609d9b`다. 현재 수락 metadata를 포함한 DR은 181,284 bytes/`e7679a8e11b5e38171888ab6da748cabd6ad5e46dc84e48205733a8e0e6d9ede`이며, 원 수락 대상 v0.10의 177,174 bytes/`cd6f3bf06d842afb8f71aac98e95382acc04b4524ee54b80af179b11ad0c3add`와 구별한다.
- source baseline은 `a93f71c359c4f0a9d57fcfb50d5999160e870f77`, reviewed tracked diff SHA-256은 `fd2677e7a3e737d72036d694a5b223304cf53645883c4c2e0aefb6a6bcdb2058`다. 미추적 계획·DR과 나머지 입력의 exact identity는 packet/manifest에 별도로 고정했다.
- numbered packet은 261,193 bytes/`b6c8d3dccc5af41b2093d5386788f4a2229e32ea98e7956e703b972b6f583eca`, request SHA-256은 `b6ae60cb7ad876c8f1291cd2603f7b11e78fb22d6b502e1f04aadd285d3f219e`다. 최종 응답은 20,028 bytes/`735595333dd3a9d7898915e29ae54f01da56ddf505b64021629dde6cfc4eb376`다. request·packet·입력 식별자·final·metadata·runner는 이 라운드의 Owner 처분과 후속 계획 revision 비교를 위해 보존한다.

Reviewer가 읽은 것은 계획·DR 전문, Maintaining·Source Workflow 전문, Windows Admission 및 Decision Guide의 관련 절이다. 제품 source/tests/runner·실험 원출력·이전 reviewer 원문·Microsoft 링크 본문은 제공하지 않았다. 따라서 아래 source 대조는 Driver의 별도 정적 확인이다. 단일 fresh Claude 세션과 고정 packet은 문맥을 제한하지만 완전한 독립성이나 망라성을 증명하지 않는다.

### Finding Dispositions

아래 accept/revise는 후속 문안 보완에 대한 Driver의 처분이다. 이번에는 계획 v0.1과 수락 계약을 수정하지 않았다. 리뷰 판정과 Driver 권고를 Owner의 실행 승인으로 기록하지 않는다.

| Finding | Reviewer 분류 | Driver 처분 | 판단과 권고 범위 |
| --- | --- | --- | --- |
| F1 · platform test | P1 · must-fix | revise | 문제는 실제다. 현재 test에 무조건 fcntl import와 POSIX mode 기대가 있다. platform에 따라 달라지는 사례의 import/discovery·기대값·대응 Windows 사례를 test source/검증 계획에서 고정한다. 모든 ID에 새 registry를 만들 필요는 없다. 사전 근거가 있는 비적용 항목·예상 거절·unexpected skip을 구별하고 계약 필수 사례를 N/A나 PASS로 바꾸지 않는다. |
| F2 · 준비 순서 | P1 · must-fix | accept | P1–P3가 겹칠 수 있다는 문구만으로 선행 입력을 충분히 고정하지 못한다. 최소 Windows prepared source/candidate는 첫 P2 init 전에, P/Q는 첫 switch·reader 검증 전에 필요하다. P3는 최종 freeze/equality를 맡는다. 필수/허용 unavailable sync 및 write-capable open의 operation/phase 대응은 P1에서 준비한다. |
| F3 · old writer | P2 · must-fix | revise | 계획은 이미 P0에 노출 writer, P2에 거절을 배치했다. 전부 P4로 미뤘다는 해석은 좁혀야 한다. 다만 writer×실제 접근 경로·family별 guard 대조와 fresh/incomplete init 직후의 조기 거절 확인을 명시할 필요가 있다. POSIX 호환 runtime·복사/동기화는 실제 노출 분석 대상일 때 다루며 모든 역사·교차 OS 경로를 새 필수 matrix로 만들지 않는다. |
| F4 · 읽기 경로 | P2 · must-fix | revise | doctor/status가 V1/V8에 명시되지 않은 누락을 인정한다. 지원되는 installed/source/retained 읽기 경로의 성공 또는 정확한 진단·거절과 anchor/재flush/authority-content 쓰기 부재를 검증한다. fresh/detached 상태의 모든 명령에 성공을 요구하거나 제거된 launcher 실행을 새 지원으로 만들지 않는다. |
| F5 · worker mode 변경 | P2 · must-fix | accept | V7의 “index 불일치 mode 변경”은 범위가 좁다. 기존 경로 mode 변경 결과의 거절을 index 일치 여부에 대한 추정 없이 명시하고 실제 guard·분류 근거를 확인한다. 이는 새 닫힌 지원 목록이나 별도 mode registry를 요구하지 않는다. 기존 공통 조건·exact baseline guard, drift/stale와 unsupported의 구별을 유지한다. |
| F6 · 필수 사례 추적 | P2 · must-fix | accept | V행이 요약임을 밝히고 A3/A8/A9/A13/A14의 열거 사례를 최소 coverage로 연결한다. P2의 실제 test ID에 대응시키되 unreachable fixture·기록 파싱·부분 성공으로 닫지 않는다. 아래 Driver 추가 확인처럼 현행 Maintaining의 의무도 함께 추적한다. |
| F7 · refusal fixture | P2 · must-fix(P0) | revise | 환경 준비·실제 거절 경로·관측 불가 처분을 P0에서 정해야 한다. 다만 A13이 “두 번째 volume·remote share를 반드시 새로 생성”하라고 쓰지는 않았다. 다른 NTFS volume의 backup 허용과 same-volume replace를 구별해 필요한 증거를 고른다. 관리자 준비나 network/share 개방은 자동 승인하지 않으며 이미 제한된 경계 안의 거절 검증과 추가 환경이 필요한 검증을 구별한다. 필수 증거가 없으면 미검증으로 남긴다. |
| F8 · macOS runner | P2 · must-fix | accept | shared 변경의 macOS full 회귀를 정했지만 runner 경계는 Windows VM 중심이다. macOS의 exact runtime·policy·쓰기/network canary·child 회수·ledger·측정 근거와 budget을 연결한다. 재사용 가능한 기존 통제가 있으면 identity와 적용성을 확인하며 검증 체계를 새로 복제하지 않는다. |
| F9 · shared 문서·Preview | P2 · must-fix | revise | shared managed 문서 변경이 macOS artifact identity에도 영향을 주는 것은 맞다. 현재 격리 작업 경로를 유지하고 다른 Preview 후보로 자동 통합하지 않는 경계를 명시하면 되며 새 worktree를 필수화할 이유는 없다. A15의 조건부 정책 문구 자체는 qualification 순환을 만들지 않는다. 이후 shipped 설명을 고치면 새 identity와 Maintaining의 영향·소비 경로 검증을 적용한다. |
| F10 · 보존·반출 | P2 · must-fix(P0) | revise | guest restore 전에 필요한 증거를 durable host 경로로 회수하고 bytes를 대조할 방법이 필요하다. base commit + exact diff/필요한 미추적 bytes 등 회수 가능한 입력을 유지한다. 일반 실행 승인에 local commit이 포함된다고 추정하지 않는다. commit은 source procedure의 별도 명시 승인 경계를 지키며 host share/clipboard를 임의로 열지 않는다. |
| F11 · x64 focused | P3 · 선택 | accept | ABI/구조체·pointer/error 전달, lock 취소·replace sharing·native argv를 초기 focused 후보로 적는 것은 유용하다. 실제 차이와 확보한 환경에 맞춰 고르고, 미관측 x64/물리 환경은 그대로 표시한다. B를 full matrix나 물리 장비 보유 gate로 바꾸지 않는다. |
| F12 · identity·완료 용어 | P3 · 선택 | revise | 원 수락 hash와 “11개 기술 문서/11 Python modules/29 managed paths”를 구별하고 P/Q가 실제로 입증한 호환 범위를 표시하는 보완에 동의한다. 특히 개발 검증과 published/refetched equality·criterion 10·formal admission의 완료 경계는 실행 범위에서 명확히 해야 한다. publication 미승인 상태를 해당 증거 완료로 바꾸지 않는다. |
| F13 · 승인·시도 한도 | P3 · 선택 | revise | 계획 24행은 이미 범위 내 반복 승인을 만들지 않도록 한다. P0–P4의 실행 승인과 통제 canary 문구를 그 의미로 정렬하고 단계별 유한 시도 한도를 제안하는 보완은 유용하다. P0 값마다 새 승인을 만들지 않으며 Reviewer의 “재실행 1회” 예시는 아직 선택된 계약·실행 한도가 아니다. |

### Driver Static Cross-Checks

- **F1의 조건부 전제:** [test_entry_window_transition.py](../../tests/test_entry_window_transition.py) 11행과 [test_worktree_process_recovery.py](../../tests/test_worktree_process_recovery.py) 7행에 fcntl의 무조건 import가 있다. [test_general_work.py](../../tests/test_general_work.py) 245–252행은 chmod 뒤 snapshot mode가 100644→100755가 되는 것을 기대한다. 따라서 platform 처리와 collection 검토는 실제 source에 근거한 계획 과제다. Windows에서 실패를 재현하거나 실제 discovery를 실행한 것은 아니다.
- **F2/F3의 source 경로:** [product.py](../../src/hv2ref/product.py)의 247–299행은 후보 launcher의 허용 literal을 실행 없이 파싱하며, 349행의 candidate 생성은 source managed bytes를 읽어 inventory를 만든다. 969행 이후 installed gate는 entry-1과 loaded payload를 확인한다. root [colvia](../../colvia) 4행은 entry-1 literal이고, [workspace.py](../../src/hv2ref/workspace.py) 37–42행의 현재 runtime 검사는 별도 OS gate가 없다. 이는 준비 순서·old-writer family별 확인의 필요성을 뒷받침하지만 모든 old writer가 안전하게 거절한다는 증거는 아니다.
- **F4의 기존 읽기 의미:** [test_runtime_admission.py](../../tests/test_runtime_admission.py) 43–54행은 unsupported identity에서 status의 진단·정확한 exit와 target 불변을 검사한다. 이 기존 형태를 Windows actual OS/process·지원 읽기 경로에 연결할 수 있다. 아직 Windows용 case가 구현·실행됐다는 뜻은 아니다.
- **F5의 계약 경계:** DR S6의 공통 필요조건·기존 모든 guard와 mode-change 미지원 예시, A2의 “Mode-changing results … initially unsupported”, A3의 whole-operation refusal을 직접 대조했다. 공통 조건을 만족했다는 이유만으로 기존 guard를 면제할 수 없으며 index 변화의 drift/stale를 새 영구 unsupported 규칙으로 흡수해서도 안 된다.
- **F7의 처방 범위:** A7은 replacement source/destination의 same-volume과 다른 검증된 local NTFS volume에 둘 수 있는 external backup을 구별한다. A13은 remote/non-NTFS/unknown 거절과 volume drift를 요구하지만 특정 fixture 생성 방법을 지정하지 않는다. 구체 setup·권한·접근 방법은 P0에서 검토할 구현/검증 입력이다.
- **F9/F10의 권한:** A15의 문장은 “For a qualified windows-1 target”이라는 조건부 안내이며 실측 tuple을 그 문장에 미리 박아 넣으라는 의무가 아니다. [Maintaining](../MAINTAINING.md#evidence-reuse-and-selection)은 shipped prose 변경 뒤 새 inventory와 관련 소비 경로 검증을 이미 규정한다. [Source Workflow](WORKFLOW.md#publication-and-adopter-authorization)는 local commit을 포함한 Git action을 명시 승인 대상으로 두므로 일반 실행 승인으로 확대하지 않는다.
- **F12의 문서 집합:** [DR-0002의 역사적 11-document table](../decisions/DR-0002-checkout-1-contract-baseline.md#original-m2-contract-set-historical-revision)은 기술 계약 집합의 출처다. 현재 적용 revision은 entry-1/First B1을 따라야 한다. 이 집합은 11 Python modules나 A1–A15의 target/placement 수와 같은 개념이 아니므로 계획에서 구별하는 편이 명확하다.

### Additional Driver Coverage Finding

**R0-I01-D1 · P2 · 계획 보완 권고:** F6의 coverage 연결을 Windows 추가 조항에만 한정하지 말고 현재 Maintaining의 기존 의무까지 포함해야 한다. 37행은 lifecycle의 secret-sentinel 불변, 44/56행은 managed 문서·adapter의 installed/update/repair/detach 및 entry/resume 소비 검증, 79행은 고정 tokenizer의 AGENTS/combined reading budget과 fresh-reader exercise의 구별을 규정한다. A15가 Getting Started와 adapter를 변경하므로 V12의 “parity”만으로 이 항목을 완료 처리하면 안 된다.

권고는 P3/V12에 해당 검증 연결을 명시하고, lifecycle fixture에는 sentinel 불변을 연결하는 것이다. 새 기준을 만들거나 현재 tokenizer 측정·실제 reader exercise를 수행하는 요청이 아니다. 실제 test/측정 입력과 결과는 후속 승인된 실행에서 고정한다.

### Recommended Next Boundary

수락된 DR-0007은 유지하고, 계획 v0.2에서 위 지적의 채택 범위만 보완하는 것을 권고한다. 우선순위는 F1/F2의 test·준비 의존성, F4–F6/D1의 검증 누락, F8/F10의 실행·증거 경계다. F3/F7/F9/F12/F13은 기존 단계·권한·완료 의미를 정확히 정리하는 방식으로 좁힌다. F11의 focused 후보는 환경 확보를 강제하지 않는 선택 보완이다.

현재는 R0 완료와 Driver 처분까지다. 계획 v0.1과 수락 계약의 bytes는 그대로이며 새 구현·실험·VM 실행·후속 reviewer·Git action은 하지 않았다. 이 결과는 실행 승인이나 제품 qualification PASS가 아니다.

### Reviewer Response Verbatim

````markdown
# R0-I01 — Windows Native Implementation Plan v0.1 정적 리뷰

## Overall verdict: **conditional**

계획의 방향은 수락된 DR-0007 v0.10과 정합합니다. B안 배정, 공통 조건 중심 worker, formal admission 시점, 자동 retry 0회, old-writer 중단 처분도 그대로 유지합니다. 다만 아래 must-fix를 계획 문안에 보완해야 실행 승인 검토에 들어갈 수 있습니다. 이 판단은 아직 시작하지 않은 제품 test의 통과를 요구하지 않습니다.

| 관점 | 판정 | 요지 |
| --- | --- | --- |
| 계약 정합성 | conditional | 큰 방향은 일치합니다. 다만 V7의 mode-change 거절 표현이 계약보다 좁고, status/doctor 경로가 빠져 있으며, A3·A9·A13이 열거한 사례와의 추적성이 부족합니다. 개정이 필요한 계약 충돌은 찾지 못했습니다. |
| 구현 순서 | conditional | Windows source preparation과 candidate P/Q가 P3에 있지만 P2 lifecycle 검증의 선행 입력입니다. flush call-site 대응표와 old-writer 노출 분석의 시점도 정해져 있지 않습니다. |
| 검증 범위 | conditional | Windows full suite에서 platform별 기대값을 어떻게 처리할지 정의되지 않았습니다. 필수 사례의 추적성도 부족합니다. |
| 실행 경계 | conditional | Windows VM 경계는 충분합니다. macOS 회귀 runner, guest 증거 반출, source identity 보존, refusal fixture 준비가 정해지지 않았습니다. |
| 실행 승인 검토 준비도 | conditional | F1–F10을 문안에 보완하면 검토할 수 있습니다. 정확한 값은 P0에서 고정해도 됩니다. |

## Findings

### R0-I01-F1 · P1 · must-fix — Windows full suite의 platform 의존 test 처리 미정

- **위치:** plan L54, L72, L90, L104, L120, L136, L140. DR A3 L600(macOS mode-change 성공 기대 유지, Windows 기대 거절), A13 L851. Maintaining L60.
- **실패 경로:**
  - 같은 test 경로에서 macOS는 mode-change 성공을, windows-1은 발행 전 거절을 기대해야 합니다. 이는 계약에서 확정된 사실입니다.
  - 기존 suite에는 POSIX 전제 사례가 있을 가능성이 큽니다. 예를 들어 launcher 0755, D3 fullfsync, `./colvia` 직접 실행이 그렇습니다. 실제 test 내용은 읽지 못했으므로 이 부분은 조건부 판단입니다.
  - 계획은 skip을 PASS로 보지 않는다고만 정합니다. platform 전용 기대값을 표현하는 규칙은 없습니다.
  - 그 결과 두 경로 중 하나로 갈 수 있습니다. (a) full run이 영구히 non-pass로 남아 실행 중에 skipUnless를 임의로 추가하게 됩니다. (b) 일괄 platform skip 때문에 discovery 개수는 같아도 Windows 대응 사례가 비게 됩니다.
- **권고:** 계획에 다음 규칙을 명시합니다.
  - test source를 freeze하기 전에 각 test ID의 적용 범위를 test source 안에서 정적으로 분류합니다. 분류는 공통, macOS 전용, windows-1 전용 중 하나이고, 전용 사례에는 대응 사례를 연결합니다. runner에서 분류하지 않습니다.
  - Windows run은 사전 선언한 platform-not-applicable ID 목록을 unexpected skip과 분리해 보고합니다. 선언하지 않은 skip은 non-pass입니다.
  - 분류를 바꾸는 것은 Maintaining의 test/oracle 변경으로 다룹니다.
  - 정확한 ID 목록은 P2 산출물로 둡니다.

### R0-I01-F2 · P1 · must-fix — 선행 입력이 늦게 배치됨

- **위치:** plan L51–53, L57, L76, L84, L98, L101. DR A9 L714, A13 L841, S5 L315.
- **실패 경로:**
  - P2의 완료 근거는 "실제 제품 lifecycle"입니다. 그런데 fresh init에는 launcher literal과 payload를 candidate 생성 전에 준비한 windows-1 candidate가 필요합니다.
  - V5와 V8의 P→Q update/rollback에도 두 candidate가 필요합니다.
  - 이 준비가 P3에 있으면 P2는 test 전용으로 합성한 candidate를 쓰게 됩니다. 그러면 최종 준비 경로와 어긋날 위험이 생기고, A9/A13이 금지하는 숨은 변환과 경계가 모호해집니다. 그렇지 않으면 P2를 완료할 수 없습니다.
  - L84의 flush 의무 call-site 대응표도 "먼저 매핑"이라고만 되어 있고, 어느 단계의 산출물인지 정해져 있지 않습니다. 이 표가 P2의 전체 사전 검사 집합(교체·제거 및 필수 write-capable flush 파일)과 V4의 실패 주입 지점을 결정합니다.
- **권고:**
  - 준비 메커니즘의 정의, 최소 source-only 도구, P/Q 구성 규칙을 P1 또는 P2 진입 조건으로 옮깁니다. P3에는 최종 freeze와 source/artifact/refetch 일치만 남깁니다.
  - phase별 필수/허용 unavailable 및 write-capable open 대상 대응표를 P1의 완료 근거에 추가합니다.
  - 새 승인은 필요하지 않습니다.

### R0-I01-F3 · P2 · must-fix — old-writer 노출 분석의 방법과 시점

- **위치:** plan L42, L50, L52, L57, L98, L148. DR L500–502, A5 L630, A13 L843. Maintaining L87, L113. 아래 old reader의 거절 동작은 문서 주장이며 직접 확인하지 않았습니다.
- **실패 경로:**
  - 계획은 seed identity만 나열하고 노출 경로를 열거하지 않습니다. 고려해야 할 경로는 다음과 같습니다.
    - native Windows에서 old source를 실행하는 경우. POSIX import 실패가 발행 전에 일어나는지 관측해야 합니다.
    - 같은 NTFS에서 POSIX 호환 runtime이 old entry-1을 실행하는 경우. DR L453에 따르면 entry-1 runtime 검사에는 OS 조건이 없습니다.
    - target을 macOS로 복사하거나 동기화하는 경우.
  - binding이 없는 incomplete init에서, 그리고 intent/Work/worker/planning writer가 window를 확인하는 경로도 정해져 있지 않습니다.
  - 이 문제가 P4에서야 발견되면 format/schema amendment가 필요해져 P2·P3를 재작업하고 재검증해야 합니다.
- **권고:**
  - P0 산출물에 노출 경로 표를 둡니다. writer×경로별로 노출 여부와 증거 방법을 기록합니다.
  - P1 또는 P2 초기에 seed writer의 쓰기 family별 window 검사 위치를 정적으로 대조합니다.
  - windows-1 init과 partial-init fixture가 생기는 즉시 거절 실행 검사를 수행합니다. P4까지 미루지 않습니다.
  - 미흡하면 L57에 따라 해당 부분을 멈추고 최소 장치를 제안합니다.
  - 모든 역사적 writer의 회수는 요구하지 않습니다.

### R0-I01-F4 · P2 · must-fix — status/doctor/view 읽기 경로 누락

- **위치:** plan L34, L94, L101. DR S2 L245, S5 L309, A7 L660/L664, A10 L787. README L164 criterion 2.
- **실패 경로:**
  - criterion 2와 S2는 doctor/status를 명시하지만 계획 어디에도 나오지 않습니다.
  - 읽기 경로에는 다음 의무가 있습니다. anchor를 만들지 않고(A7), 재flush하지 않으며, 미지원 runtime에서 쓰기 없이 진단합니다(A10).
  - 이 의무는 mutation gate만 검증해서는 드러나지 않습니다.
- **권고:** V8 또는 V1에 다음을 추가합니다. PowerShell 5.1에서 fresh, same-window, detach4 이후, 미지원·emulated runtime 각각에 대해 doctor/status/view를 실행하고, anchor·reflush·mutation이 없는지 검증합니다.

### R0-I01-F5 · P2 · must-fix — V7의 mode-change 거절 표현이 계약보다 좁음

- **위치:** plan L100. DR A2 L578, S6 L375, A3 L598.
- **실패 경로:**
  - "index 불일치 mode 변경"이라는 표현은 index가 result mode와 일치하면 허용된다고 읽힐 수 있습니다.
  - 그러나 계약은 기존 경로의 mode 변경을 mode-only이든 bytes 동반이든 범주 전체로 미지원으로 둡니다.
  - 예를 들어 control index가 이미 result mode인 경우 공통 조건의 예측은 일치합니다. 이때 거절은 baseline guard나 범주 규칙에 의존합니다. baseline drift로 거절될 가능성은 높지만 추정일 뿐입니다.
- **권고:**
  - V7을 "기존 경로의 mode 변경(index 일치 여부와 무관)"으로 고칩니다.
  - index가 result와 일치하는 사례를 추가하고, 어떤 guard가 거절하는지 기록합니다.
  - base에 없는 경로의 index-only tracked add와는 계속 구분합니다.
  - 계약 변경은 필요하지 않습니다.

### R0-I01-F6 · P2 · must-fix — 계약이 열거한 qualification 사례의 추적성

- **위치:** plan L90, L99–103, L107–109. DR A3 L596–598, A8 L688/L694, A9 L769/L779, A11 L807, A13 L845–849, A14 L859.
- **누락 예:**
  - **V7:** 두 mode의 tracked 삭제, 새 untracked 100644, 새 untracked 100755 destination으로의 rename/copy, worker 분류 불가, 중단된 accept apply를 원 ticket으로 재개하는 사례.
  - **V9:** 순수 read-only 보존·미열거 파일의 비거절, backup·교체 전후 중단, 재flush가 필요한 기존 backup 파일, 외부 속성 복원 뒤 원 retry, 새 identity/backup을 쓰는 허용 가능한 새 preview, 실제 pending에 의한 거절, read-only 교체를 포함해 제출된 request의 발행 전 거절.
  - **V10:** `.hrn/detached.json` 발행 전 전체 remove set 사전 검사, 내장 plan을 쓰는 읽기 검증과 원 token·독립 source가 필요한 mutation recovery의 구분, 보존 bytes 변경, 역사적 schema를 다시 붙이지 않음.
  - **A14:** old reader의 false PASS를 증거에서 제외하는 처분.
- **실패 경로:** V행은 요약입니다. 여기에 "기존 suite 우선 재사용"이 겹치면 열거 항목이 빠진 채 V9 등을 닫을 수 있습니다. R1도 완전성을 판정하기 어렵습니다.
- **권고:**
  - "V행은 요약이며 A3·A8·A9·A13·A14의 열거 사례가 최소 checklist"라는 한 문장을 추가합니다.
  - P2 test 계획에서 각 사례를 discovery ledger의 ID에 대응시킵니다. 기존 task record 안에서 하면 되고, 새 registry는 필요 없습니다.

### R0-I01-F7 · P2 · must-fix(P0 입력) — refusal fixture 환경과 실행 경계의 충돌

- **위치:** plan L40, L95, L113. DR A7 L656–658, A13 L847.
- **실패 경로:**
  - A13은 다음 fixture를 요구합니다. non-NTFS 경로, remote 경로, volume identity drift, 외부 backup용 두 번째 local NTFS volume, mount point와 junction.
  - 표준 사용자는 volume 생성이나 share 개설을 할 수 없습니다. 또 remote 검사는 L113의 host share·network 제한과 충돌합니다.
  - 실행 중에 share를 임의로 열거나 "환경 없음"을 N/A로 처리할 위험이 있습니다.
- **권고:**
  - P0에서 fixture 준비 방법을 고정합니다. 예를 들어 Owner가 VM 구성으로 추가 disk를 사전에 준비하고 관리자 단계를 미리 기록합니다. remote 검사는 guest 내부 loopback이나 범위를 명시한 격리 경로로 합니다.
  - 준비할 수 없는 사례는 미검증 non-pass로 보고합니다.

### R0-I01-F8 · P2 · must-fix — macOS 회귀의 실행 경계 미정

- **위치:** plan L111–136(Windows VM 중심), L140. Maintaining L37, L64–67. WORKFLOW L108.
- **실패 경로:**
  - shared writer 변경 때문에 macOS normal과 `-O` full run이 필수입니다.
  - 계획은 VM 경계만 정의합니다. macOS 쪽에는 constrained runner, network 거부, 쓰기 경계 canary, child interpreter identity, budget, ledger가 없습니다.
  - 그러면 worktree를 sandbox로 오인한 상태에서 실행하거나 실행이 막힐 수 있습니다.
- **권고:** macOS 행을 추가해 다음을 담습니다. runner·policy identity, 쓰기·network canary, Python identity, 측정치에 여유를 더한 budget, discovery/executed ledger, Maintaining의 네 가지 재사용 판단. 정확한 값은 P0에서 정합니다.

### R0-I01-F9 · P2 · must-fix — 공통 source와 managed 문서 통합을 macOS Preview·activation과 분리

- **위치:** plan L53, L73, L76, L146. DR L48, L547, A15 L864. Maintaining L56, L60, L91. README L160.
- **실패 경로:**
  - A2·A7·A8·A10–A15의 대상은 entry-1과 공유하는 managed 문서와 adapter입니다. 따라서 macOS artifact의 bytes와 identity도 바뀝니다. 또 Windows activation 전에 Windows 조항이 Preview 후보에 섞일 수 있습니다.
  - 관측한 tuple이나 지원 상태 문구를 shipped bytes에 쓰려면 같은 bytes를 qualification하기 전에 그 내용이 확정되어야 합니다. 이는 순환입니다.
- **권고:**
  - Owner 결과 수락과 activation 전까지 통합을 분리된 branch나 worktree에 둔다고 명시합니다.
  - macOS Preview 후보와의 관계를 밝힙니다. 제외할지, 포함하고 macOS 재검증을 할지 정합니다.
  - shipped 문구는 정책 문구와 미검증 label로 한정하고, 실측 tuple은 qualification 증거에 둡니다.
  - qualification 뒤 문구를 보정해야 하면 Maintaining의 prose-only 경로를 따릅니다. 즉 새 inventory를 만들고 install/update/repair/detach 소비 검사를 합니다.
  - Git publication은 지금 요구하지 않습니다.

### R0-I01-F10 · P2 · must-fix(P0 입력) — 증거 보존과 반출 경로

- **위치:** plan L14, L115, L136, L150. WORKFLOW L68. Maintaining L54.
- **실패 경로:**
  - Git publication이 범위에서 제외되어 있습니다. 그런데 anchor와 R1에는 commit이나 회수 가능한 고정 bytes가 필요합니다.
  - guest의 durable root에서 host로 증거를 옮기는 방법이 정해져 있지 않습니다. host share와 clipboard가 제한된 상태이므로, VM restore 때 증거가 사라지거나 반출을 위해 host 쓰기 경로를 열게 될 수 있습니다.
- **권고:** P0 입력에 다음을 추가합니다.
  - source identity 보존 방식: 실행 승인 범위 안의 local commit, 또는 base commit과 diff digest 및 보존 bytes.
  - restore 이전에 child 회수를 마친 뒤 수행하는 단방향 반출 방식과 양측 digest 대조.

### R0-I01-F11 · P3 · 선택 — x64·물리 장비 focused 범위와 환경

- **위치:** plan L54, L104, L142. DR S1 L235, A6 L644.
- **경로:**
  - "필요한"이라는 표현이 있고 환경 입력은 없습니다. 이 때문에 x64가 끝내 관측되지 않을 수 있습니다.
  - policy gate는 x64 mutation을 허용하지만 ctypes ABI는 x64에서 시험되지 않습니다.
  - 계약상 미검증 label은 허용되므로 위반은 아닙니다.
- **권고:**
  - 초기 focused 후보를 적습니다. ctypes 구조체·pointer·last-error, LockFileEx overlapped와 취소, replace sharing, PowerShell argv가 해당합니다.
  - P0에서 환경 확보 여부를 기록합니다. 확보하지 못하면 결과에 unobserved로 표시합니다.
  - full matrix는 추가하지 않습니다.

### R0-I01-F12 · P3 · 선택 — 식별과 완료 용어의 정밀화

- **위치:** plan L6, L53, L98, L105, L146. DR L44. README L164 criterion 10.
- **권고:**
  - header에 원 수락 대상 identity(177,174 bytes, `cd6f3bf…`)를 함께 적어 현재 metadata가 포함된 파일과 구별합니다.
  - "11-member 기술 계약"은 packet 안에서 정의되지 않았으므로 정의합니다. "11 Python modules"와 혼동될 수 있습니다.
  - "관련 필수 증거" 가운데 이번 실행에서 해소할 것과 formal admission으로 넘길 것(criterion 10 전달 경로, admission 시점의 재사용 판단)을 구분합니다.
  - P/Q가 같은 code의 변형이라면 양방향 reader 검증이 plumbing만 입증한다는 한계를 명시합니다.

### R0-I01-F13 · P3 · 선택 — 승인 전이와 시도 한도

- **위치:** plan L50, L119–125. WORKFLOW L52, L84.
- **경로:**
  - L50의 "통제 canary는 별도 실행 승인 후"가 추가 승인 단계로 읽힐 수 있습니다.
  - P0에서 고정한 값이 승인 범위 안에 있는지 판단하는 규칙이 없습니다.
  - canary를 제외하면 시도 한도가 없습니다.
- **권고:**
  - "실행 승인은 범위 안에서 P0–P4를 포괄한다. P0 값은 task record에 기록하고, 범위를 벗어나면 멈춘다"라고 명시합니다.
  - full과 focused의 초기 재실행 상한을 제안값으로 둡니다. 예: frozen candidate·mode당 원인 기록 재실행 1회.

**계약 충돌:** 수정이 필요한 실제 충돌은 없습니다. A2의 공통 조건과 범주형 mode-change 미지원은 함께 적용되는 필요조건이며, F5의 계획 표현 문제일 뿐입니다.

**충분하다고 판단한 문안:**
- L24: 반복 승인을 만들지 않는 경계.
- L35, L107: worker 예시 비폐쇄.
- L109: repair 진단과 apply preflight.
- L113: worktree와 Job Object를 sandbox로 보지 않음.
- L120, L136: discovery/executed ID 기록.
- L125, L134: 시간 상한이 측정치가 아님을 명시, `-O`가 child에 전파되지 않음을 명시.
- L57, L148: old-writer와 unknown의 중단 처분.
- L142: full matrix를 강제하지 않음.

## 교차표

| 영역 | 계약 근거 | 계획 반영 | 빈틈 | 처리 시점 |
| --- | --- | --- | --- | --- |
| 공통 worker | S6, A2, A3 | L35, L100, L107 비폐쇄 | mode-change 표현(F5), 사례 추적(F6) | 계획 보완 |
| repair | A9, A11, S8 | L102, L109 | 중단·reflush·외부 복원·pending 사례(F6) | 계획 보완 → 실측 |
| detach4 | A8, A9, A14 | L103 | 사전 검사·읽기/복구 구분·old reader 처분(F6) | 계획 보완 → 실측 |
| old writer | A5, A13 | L42, L57, L98 | 노출 경로 열거와 조기 검사(F3) | P0 → P1/P2 |
| source/artifact | A9, A13, Maintaining | L53, L76 | 준비 단계 순서(F2), macOS·Preview 분리(F9) | 계획 보완 |
| 읽기 lifecycle | S2, S5, A10, crit. 2 | 없음 | doctor/status/view(F4) | 계획 보완 |
| NTFS fixture | A7, A13 | L95 | 환경과 경계 충돌(F7) | P0 |
| Windows runner | A13, Maintaining | L111–136 | platform test 처리(F1), 반출(F10), 시도 한도(F13) | 계획 보완 + P0 |
| macOS runner | Maintaining L37, L64–67 | L140 | 경계·ledger·budget(F8) | 계획 보완 + P0 |
| x64·물리 | S1, A6 | L142 | 후보와 환경(F11) | P0 |

## 권고 분리

**계획 문안 보완(실행 승인 검토 전):** F1 규칙, F2 단계 재배치, F3 노출 분석 방법과 시점, F4·F5·F6 V행 수정과 checklist 문장, F8 macOS 행, F9 분리 원칙. 선택 사항으로 F11–F13 문장 정리.

**P0에서 고정할 입력:**
- exact tuple, VM과 recovery identity, restore 실측.
- 노출 writer와 경로 표.
- fixture volume과 remote 준비.
- source identity 보존 방식, guest 반출 방식.
- Windows·macOS runner identity와 budget, 시도 상한.
- platform-not-applicable 분류 규칙의 적용 위치.
- x64·물리 장비 환경 확보 여부.

**이후 실측으로만 입증할 것:**
- Win32 lock 취소와 completion.
- flush·replace의 phase별 결과.
- PowerShell 5.1 입력 보존.
- old-writer의 실제 거절.
- worker·repair·detach4 성공과 거절 prefix.
- 양방향 reader 동작.
- 두 autocrlf 설정.
- Windows normal/`-O` full run과 macOS 회귀.
- x64 focused 결과.
- shipped 문구 parity.

## 읽지 못한 근거와 한계

- **제공되지 않은 근거:** linked CHORE 기록, CHECKOUT-1-STRUCTURE, WORKSPACE/GENERAL-WORK 원문, 실제 source·tests·runner, probe 원출력, 이전 reviewer 응답, Microsoft 문서 본문. source와 API에 관한 서술은 모두 packet 속 문서의 주장으로 다뤘습니다.
- **조건부 판단:** F1의 POSIX 전제 test 존재 여부와 F3의 old reader 거절 동작은 code를 대조해야 확정됩니다.
- **식별값:** packet의 hash와 날짜는 Driver가 제공한 값이며 재계산하지 않았습니다.
- **실행하지 않음:** tool 실행, 파일 접근, 실험은 하지 않았습니다. 실행 불가를 PASS로 보지 않았습니다.
- **독립성 한계:** 이 판단은 단일 세션(Claude Opus 5.5, `claude-opus-5-5`)의 정적 판단입니다. Driver가 구성한 packet에 의존하므로 독립성과 망라성은 제한됩니다.
````


### R0-I01 Record Verification And Retention

문서 검증 PASS: source 문서 5개와 private 기록 1개, 로컬 path/heading link 180개, marked 17.0.5 GFM·code 밖 literal 강조 기호·whitespace·disclosure를 확인했다. 신규 R0-I01을 포함한 13개 리뷰의 원문·frozen identity, 입력 6개의 원래 행 범위·packet bytes, finding 13개 처분과 별도 Driver D1을 확인했다. 이전 CHORE/private 기록은 이번 append 앞의 bytes가 동일하며, 허용된 두 기록 외 242개 입력이 불변이다.

계획 v0.1과 DR-0007 Accepted v0.10, catalog/navigation·제품 source·tests·managed payload·기존 기술 계약은 바뀌지 않았다. 이전 수락 단계의 S1–S8/A1–A15·이력 보호 구간, exact v0.10 복구와 네 문서 bounded diff 역복구도 유지된다. `git diff --check`와 기대 tracked/untracked 범위를 확인했다. 이 검증은 문서·식별자 확인이며 제품 test·새 probe·Windows/macOS qualification이 아니다.

request·packet·입력 식별자·final·최소 metadata·runner는 Owner의 지적 처분과 v0.1 후속 revision 비교에 필요한 근거로 보존한다. 소비가 끝나고 accepted successor가 필요한 근거를 보존하면 필요성을 다시 평가한다. 수락 단계의 input manifest와 bounded diff는 수락 기록의 복구에 계속 필요하다. 원 v0.10 packet과 기존 probe·VM 복구 자료는 기록된 소비자·종료 조건이 남아 있으며 계약 리뷰 완료만으로 삭제하지 않는다.

정리 완료: CLI 종료, partial/final bytes 일치, 빈 stderr/tool-temp와 lsof no-use를 확인한 뒤 중복 partial·빈 stderr, 일회성 작성 script, 이번 및 이전 수락 단계의 검사기/JSON 보고서 등 파일 7개와 빈 tool-temp 디렉터리 1개를 삭제했다. 이전 수락 검사의 소비 조건인 R0 입력 고정은 완료됐고 필요한 검증 사실은 기존 기록에 편입했다. 리뷰 근거 6개와 수락 입력/diff, unique source 문서·원출력·마지막 복구 자료는 보존했다. 활성 입력·출력 경로 이동과 worktree·VM·branch 삭제는 없었다.

## Implementation Plan Revision 0.2 — 2026-10-18

Owner는 “R0-I01과 네 판단을 반영해 후속 구현·검증 계획을 v0.2로 보완해줘. 구현 순서·검증 범위·실행 경계를 구체화하고, 과도한 권고는 네가 좁힌 범위로 반영해. DR-0007 v0.10과 B안, 공통 조건 중심 worker 지원은 유지하고 추가 실험이나 제품 구현은 시작하지 마.”라고 요청했다.

### Scope And Result

[후속 구현·검증 계획](windows-native-implementation-plan.md)을 v0.2로 보완했다. R0-I01-F1–F13의 Driver 처분과 추가 지적 D1을 계획의 [Revision 0.2 Response Map](windows-native-implementation-plan.md#revision-02-response-map)에 연결했다. 이 요청은 문서 보완 승인이다. R0-I01의 conditional·원문·처분을 수정하지 않았고, v0.2 재검토나 실행 승인으로 기록하지 않는다.

- P1에서 platform test import/discovery·기대값, flush 의무/phase와 첫 Windows prepared candidate를 준비하고 P2의 첫 switch/reader 전에 P/Q를 둔다. P3는 문서·수정 완료 후 최종 freeze를 맡는다.
- doctor/status/view의 무쓰기 진단, worker mode 변경 거절·drift, A3/A8/A9/A13/A14의 실제 필수 사례를 구체화했다. Maintaining의 secret-sentinel·shipped consumer·entry/resume·token budget·fresh-reader 의무도 연결했다.
- 실제 노출 writer와 fixture 범위, Windows/macOS runner·회수·guest 증거 반출, 시간/시도 한도 제안을 명시했다. 모든 test ID의 새 registry, 모든 old-writer 경로, 새 worktree·관리자/네트워크·물리 환경 의무는 추가하지 않았다.
- shared managed 문서가 macOS artifact에 미치는 영향과 개발 결과·published/refetched 검증·activation·formal admission을 구별했다. 일반 실행 승인에 local commit·publication 권한을 넣지 않았다.

DR-0007 v0.10 수락 본문·metadata, B안, 공통 조건 중심 worker 지원, 자동 replace retry 0회, entry-1/First B1의 현행 발효 상태를 유지했다. 제품·tests·runner 구현, 새 실험·VM 실행·후속 reviewer 호출·Git action은 수행하지 않았다. 구현 task ID나 runtime Work를 새로 만들지 않았다.

### Exact Revision And Preservation

v0.1은 22,882 bytes / SHA-256 `64e17e0a01cb2e2246f7efcb78090c789b5cb67dcf81a95845abe0fb4b609d9b`이며 R0-I01 frozen packet에서 원 bytes를 회수할 수 있다. v0.2는 45,337 bytes / SHA-256 `8feaadab9f0158ff7f0d16f1c26145243eb95631696efc689d413f835d44e332`다. 이전 문안에 대한 exact diff와 변경 위치/근거를 보존했고, 기존 진행 기록은 append-only로 유지했다. source baseline은 `a93f71c359c4f0a9d57fcfb50d5999160e870f77`다.

이번 산출물의 소비자는 계획 v0.2 검토·실행 범위 선택이며, 이후 exact 입력이 고정되면 일회성 작성/검사 파일을 재평가한다. 수락 계약과 리뷰 원문·복구 입력의 보존은 제품 실행이나 task 완료 승인을 뜻하지 않는다. 다음은 v0.2의 검토·처분과 별도의 bounded 실행 승인이다.

### Document Verification And Retention

2026-10-18 문서 검증에서 GFM parser(marked 17.0.5)의 문서 6개·로컬 링크/anchor 183개가 통과했다. code 밖 literal emphasis·trailing whitespace·source 문서의 private 식별자 노출을 찾지 못했다. v0.1의 frozen packet 복원과 v0.2 diff의 reverse-apply check가 통과했고, 28개 지정 편집 외의 문안은 보존됐다. 이전 리뷰 13개 라운드의 원문·고정 입력, 수락 DR 전체, 두 진행/맥락 기록의 기존 prefix를 확인했다. 변경 대상 세 파일을 제외한 249개 source/evidence 입력은 동일하다. tracked Git diff와 HEAD도 그대로이며 diff-check를 통과했다.

변경은 계획 v0.2와 기존 CHORE/private 맥락의 추가 기록뿐이다. 제품·tests·runner·normative 기술 문서·catalog/navigation은 이번에 바뀌지 않았다. 이는 문서 정적 검증이며 Windows/macOS 제품 실행이나 v0.2의 독립 R0 재검토가 아니다.

계획의 현재 bytes, v0.1 원본을 담은 기존 R0-I01 packet, 변경 전 입력 식별자와 exact diff는 v0.2 검토·실행 입력 고정/복구를 위해 보존한다. 별도 full source 복사본은 만들지 않았다. 작성 payload·편집 helper·상세 edit map·검사 helper·중간 검사 JSON은 이 검증 결과가 기존 기록에 남고 사용 종료를 확인하면 정리한다. 기존 worktree·VM·마지막 recovery·probe/리뷰 근거의 소비자는 계속 계획 검토와 후속 qualification·복구이며, 활성 경로는 유지한다.

정리 완료: 사용 중인 process가 없고 복구 근거가 남아 있음을 확인한 뒤 일회성 작성/검사 파일 5개를 삭제했다. 변경 전 입력 식별자와 exact diff 2개, 현재 계획 및 기존 frozen packet/리뷰/복구 근거는 보존했다. 활성 경로·worktree·VM·branch는 변경하거나 삭제하지 않았다. 이 보존분은 v0.2 검토·실행 입력 고정 시 다시 평가한다.

## R0-I02 — Implementation Plan v0.2 Re-review And Driver Judgment — 2026-10-18

Owner는 “후속 구현·검증 계획 v0.2를 Claude CLI로 R0 재리뷰해줘. R0-I01 지적과 네 처분의 반영 여부, DR-0007 v0.10과의 정합성, 실행 승인 검토 준비도를 확인하고 네 판단도 정리해줘. B안과 공통 조건 중심 worker 지원은 유지하고, 추가 실험이나 제품 구현은 아직 시작하지 마.”라고 요청했다. 이번 범위는 고정 계획의 Claude CLI 정적 R0-I02 한 회, Driver 대조와 기록이다. 계획·계약 수정, 추가 실험·제품/test/runner 구현, VM 실행과 Git action은 포함하지 않는다.

### Verdict And Driver Assessment

Reviewer의 전체 판정은 conditional이다. 계약 정합성과 구현 순서는 approve이며, 이전 지적 반영·검증 범위/실행 경계·실행 승인 검토 준비도는 conditional이다. DR-0007을 바꿔야 할 충돌은 찾지 못했다. R0-I01의 F1–F13/D1 중 12건은 resolved(일부 선택 잔여 포함), F6(사례 추적)·F13(한도)은 partial로 판정했다.

Driver도 소규모 계획 보완 뒤 bounded 실행 승인을 검토하는 것이 적절하다고 본다. 우선할 것은 두 가지다.

1. P1/P2의 개발 반복과 candidate freeze 후 증거 실행에 같은 “묶음당 3회”를 적용하지 않도록 한도의 대상을 정한다. macOS 회당 예비 ceiling과 단계/전체 누적 상한도 승인 대상 범위에 있어야 P0가 그 안에서 값을 구체화할 수 있다.
2. V1–V12의 모든 필수 하위 사례와 최소 coverage를 실제 test 또는 native exercise 증거에 연결한다. unittest 밖의 PowerShell/argv 사례도 ID·명령·transcript로 추적하며, 별도 registry는 만들지 않는다.

Activation 전에는 A13 qualification 전체가 필요하다는 연결도 명확히 해야 한다. published/refetched equality가 빠진 개발 결과만으로 activation할 수 없다는 뜻이며, 새 조건이 아니라 이미 수락한 계약의 의무다.

Runtime·filesystem fixture와 tokenizer/reader의 입력을 명시할 권고는 유용하지만, 모든 추가 runtime·volume·share 설치와 내부 구현 선택을 Owner의 일괄 사전 결정으로 만들 필요는 없다. 승인된 경계 안의 가용성 확인·구체화는 P0가 맡고, 실제 설치·권한/전송 경계 확대가 필요할 때 그 최소 변경만 결정한다. 필요한 증거가 없으면 qualification은 미완료로 남는다. B안과 공통 조건 중심 worker 지원은 유지한다.

### Invocation And Exact Inputs

- 공통 review procedure와 workflow-cross-review의 기록 경계를 따랐다. Owner가 직접 Claude CLI 재리뷰를 명시해 이 라운드의 고정 packet을 전달했다. CLI 2.1.302, `claude.ai / firstParty / pro` 구독 인증을 scoped Keychain 조회에서 확인했고 provider override는 없었다. sandbox 내부의 로그인 조회 실패를 재인증 필요로 오인하지 않았으며 email·비밀값은 기록하지 않았다.
- 실제 model `claude-opus-5-5`, fresh session `eca0723a-12d4-4f5d-8f2f-eabb8fc656c8`. model override 없이 no-tools·strict empty MCP·세션 비보존으로 호출했다. 1,200초 상한 내 333.112초, exit 0, tool event 0, 입력 8개 전후 drift false였다.
- 대상 계획 v0.2는 45,337 bytes / SHA-256 `8feaadab9f0158ff7f0d16f1c26145243eb95631696efc689d413f835d44e332`다. 수락 metadata 포함 DR은 181,284 bytes / `e7679a8e11b5e38171888ab6da748cabd6ad5e46dc84e48205733a8e0e6d9ede`이며 원 수락 v0.10 identity와 구별한다.
- source baseline은 `a93f71c359c4f0a9d57fcfb50d5999160e870f77`다. tracked diff와 untracked 입력은 manifest에서 각각 식별했다. packet은 375,971 bytes / `89abb63ce84b95e9d3a6d423603d0f1814082db46c9d95b599ce13e8882f4b57`, request는 `163f58e9f15f48937236a3582ed66f9a2ebabd6c39c49fe48b29c854f543cc45`다.
- final은 24,703 bytes / `4b20d9a83f2c2b49c82cf56043415a8db20ae988034ad0a2ec510dd91655bad7`다. streamed partial과 final bytes도 일치했다.

Packet에는 계획 v0.2·수락 DR·Maintaining·Source Workflow 전문, Windows Admission·Decision Guide 관련 절, 이 CHORE의 R0-I01 원문/처분과 v0.2 작성 기록(당시 3104–3448행), v0.1→v0.2 exact diff를 포함했다. 제품 source/tests/runner, 원 probe 출력, DR-0002 본문과 외부 API 링크 본문은 제공하지 않았다. 이전 리뷰를 포함한 재리뷰이므로 blind review가 아니며 fresh session만으로 완전한 독립성·망라성을 주장하지 않는다.

### Finding Dispositions

새/잔여 지적은 9건이다. Reviewer는 F1/F2를 실행 승인 전 P2 must-fix, F3을 P2 승인 시 선택, F4를 closeout 전 P2 must-fix, F5–F9를 P3 선택 보완으로 분류했다. 아래 처분은 후속 계획 문안·실행 입력에 대한 Driver 권고이며 이번 요청에서 계획을 수정하거나 선택을 대신한 것이 아니다.

| Finding | Driver 처분 | 판단과 반영할 최소 범위 |
| --- | --- | --- |
| F1 · 한도 적용·누적 상한 | revise | 개발 iteration과 freeze 후 증거 실행을 구별한다. 개발 반복은 단계별 유한 시간/실행 예산, 증거 실행은 고정 candidate와 재시도 한도로 묶는 방향을 권고한다. macOS·전체 누적 예비 상한은 승인 대상에 넣고 P0는 그 이하에서 native 측정에 맞춰 구체화한다. 측정값을 꾸미거나 작은 correction마다 새 승인을 만드는 방식은 피한다. |
| F2 · 전체 사례와 exercise 추적 | accept | 현재 109행의 일반 의도와 74/68행의 일부 연결만으로 147행의 “이 최소 사례” 범위가 충분히 선명하지 않다. 모든 V1–V12 하위 필수 사례와 최소 coverage에 test/exercise ID·mode·명령·독립 oracle/결과를 연결하도록 명시한다. 기존 ledger를 활용하고 새 registry를 만들지 않는다. |
| F3 · runtime 거절 fixture | revise | filesystem 중심인 표에 필요한 거절 유형·기존 가용성·미확보 처분·추가 반입이 필요한 경우의 exact 입력/경계를 포함한다. 모든 unsupported runtime을 미리 설치하거나 emulated 상태의 모든 read 명령에 성공을 요구하지 않는다. 기존 가용성은 P0에서 확인할 수 있으며 추가 설치/권한은 필요한 범위만 명시 승인한다. 필수 미관측은 PASS가 아니다. |
| F4 · activation 전제 | accept | A13의 source/artifact/published/refetched equality와 DR Consequences의 qualification 누락 시 activation 금지를 확인했다. P4는 통합 검증의 일부이고 전체 qualification 완료와 같지 않음을 명시하며 activation 행에 연결한다. 이는 계약 amendment가 아니다. criterion 10의 전달 경로·증거 구별 의무와 formal timing은 기존 계약대로 유지한다. |
| F5 · 비적용 집계 | accept | 사전 근거가 있는 비적용 ID를 실행 전에 고정하고 실제 PASS에 더하지 않는 별도 범주로 보고한다. 계약 필수 Windows 사례는 제외 목록에 넣지 않으며 unexpected skip·unknown·missing은 non-pass다. 사후 skip 재분류로 완전 실행을 만들지 않는다. |
| F6 · 함축된 변형 사례 | revise | rename/move/copy의 실제 destination 분류, 원 ticket worker 재개/pending, detach marker 전 read-only gate, 역사적 pair 보존을 명시한다. tracked destination이라고 성공을 보장하지 않고 모든 baseline/physical guard를 유지한다. index가 이미 result mode인 변형은 실제 도달 경로와 선행 stale/unsupported 원인을 확인하며 guard를 우회한 fixture로 특정 오류 label을 강제하지 않는다. |
| F7 · tokenizer·fresh reader | revise | 고정 tokenizer 의존성/인코딩 자료의 가용성과 수행자·데이터 범위를 실행 입력으로 정한다. Reviewer가 일반 지식으로 언급한 cache 다운로드 동작은 이번에 확인·실행하지 않았다. 기존 환경을 먼저 확인하고 설치/network가 필요하면 그 범위만 결정한다. fresh-reader가 human인지 agent인지 정하고 agent인 경우 해당 invocation 인증·disclosure를 지키며 새 호출을 묵시적으로 허용하지 않는다. |
| F8 · probe 문구 복원 | accept | v0.1 P1의 “독립 probe 통과를 제품 통합 PASS로 재사용하지 않음”이 표 교체에서 빠진 것은 diff로 확인했다. 한 문장 복원이 적절하다. 수락 DR의 Rationale과 실제 제품 검증 의무는 계속 유효하므로 이 누락이 probe를 제품 PASS로 승격할 권한을 만든 것은 아니다. |
| F9 · 준비 변환과 P/Q 역할 | revise | 첫 candidate 생성 전 P1에서 기대 변환·출력 bytes를 고정하고 P3에서 P/Q 중 activation 대상과 test 전용 역할을 식별한다. “launcher literal 한 줄만”을 지금 새 계약으로 고정하지 않는다. 승인된 의미/범위 안의 명시 변환을 기록하고, 다른 persisted 의미·지원·권한 변경이 생길 때 해당 scope/계약 결정으로 돌린다. |

### Driver Cross-Checks And Bounded Decisions

- **Runtime와 read 진단:** [DR A10](../decisions/DR-0007-windows-native-runtime-contract.md#a10--security-runtime-scope) 787행은 실제 OS/process·NTFS 조건 검사와 unsupported mutation 거절을 요구하고, read-only diagnostics는 unsupported/unknown을 보고할 수 있다고 한다. 모든 비지원 runtime 설치나 모든 read 명령의 성공 의무는 아니다. F3의 fixture 가용성·증거 공백은 인정하되 조달 방법을 새 공통 gate로 만들지 않는다.
- **Activation:** [DR A13](../decisions/DR-0007-windows-native-runtime-contract.md#a13--maintaining-windows-qualification) 841행과 [Consequences](../decisions/DR-0007-windows-native-runtime-contract.md#consequences) 962행을 함께 읽으면 전체 qualification을 남긴 activation은 허용되지 않는다. 계획 60행의 “P4 qualification”과 220–221행의 분리만 읽을 때 생길 오해를 F4의 최소 문구로 막을 수 있다.
- **Worker:** [DR A2](../decisions/DR-0007-windows-native-runtime-contract.md#a2--general-work-worker-application) 578–582행은 rename 일반 금지 대신 실제 결과/분류, mode-changing/new untracked 100755 거절, 기존 baseline/drift·원 retry/pending 보존을 규정한다. F6 예시는 이 공통 조건 안에서만 검증하며 성공 목록이나 새 mode registry로 바꾸지 않는다.
- **Budget와 coverage:** 계획 174–180행은 finite 횟수를 제안하지만 개발 반복과 evidence run의 적용 단위 및 macOS/전체 예비 상한은 덜 정해졌다. 147행의 ID 연결을 V1–V12 전체와 native exercise까지 명시하는 보완은 기존 검증 의무의 집행을 선명하게 하는 일이다.
- **변경 보존:** v0.1→v0.2 diff로 F8의 삭제를 확인했다. Source Change Map과 Native Implementation Decisions의 기존 문안, 수락 계약 전체 및 제품 source identity는 그대로다. 새 제품 테스트·원인 재현·API 호출 결과를 얻은 것은 아니다.

Reviewer가 4절에 열거한 승인 전 선택 여섯 묶음을 모두 별도 승인 gate로 채택하지 않는다. 실행 승인에는 개발/증거 예산과 허용 환경·쓰기/전송·호출 경계를 한 번 구체적으로 담고, 그 안의 ordinary 구현·fixture 가용성 확인·exact 입력 선정은 P0–P3에서 진행할 수 있어야 한다. 예를 들어 계약 의미를 바꾸지 않는 최소 old-writer 거절 장치가 승인 범위 안에 있으면 계획 25행의 일반 승인 원칙을 적용한다. 실제 계약/지원/신뢰 경계 변경은 여전히 별도 결정이다. 새 runtime·volume·network/share·agent 사용을 무조건 포함시키거나 비관측을 완료로 처리하지 않는다.

### Next Boundary

권고는 F1/F2의 승인 전 명료화, F4의 activation 연결, F3의 runtime fixture 처분과 저비용 선택 보완을 한 번의 작은 계획 개정에 모으는 것이다. 새로운 제품 계약을 다시 설계하거나 B·worker 지원을 바꿀 이유는 이번 리뷰에서 찾지 못했다. 필요한 입력을 승인된 범위 안에서 단계별로 고정하되 현재 v0.2가 무조건 실행 준비를 마쳤다고 표시하지 않는다.

이번에는 계획 v0.2와 DR bytes를 그대로 유지했다. 문서의 작성 당시 “not re-reviewed” 표기는 그 고정 입력에 남기고, 후속 R0-I02 상태는 이 dated 기록에서 확인한다. 추가 실험·제품 구현·후속 reviewer·VM 실행·Git action은 수행하지 않았다. R0-I02는 정적 의견이며 Owner의 계획/실행/결과 수락을 대신하지 않는다.

### Reviewer Response Verbatim

````markdown
# R0-I02 — Windows Native Implementation And Verification Plan v0.2 정적 재리뷰

## 0. 범위와 한계

- **검토 대상:** 계획 v0.2(45,337 bytes, `8feaadab…e332`), DR-0007 v0.10(현재 파일 `e7679a8e…`), Maintaining·Workflow 전문, Windows Admission·Decision Guide 관련 절, CHORE의 R0-I01 원문·처분, v0.1→v0.2 diff. hash·날짜는 packet 값을 그대로 썼고 재계산하지 않았습니다.
- **수행하지 않은 것:** tool 실행, 파일 접근, 실험, 제품 test를 하지 않았습니다. 아래 판단은 모두 문안 대조입니다. 실행이나 재현으로 표시하지 않습니다.
- **packet에 없는 근거:** 제품 source/tests/runner, DR-0002 본문, Microsoft API 문서 본문, probe 원출력. 이에 관한 서술은 packet 속 Driver 주장으로만 다룹니다. R0-I02-F7의 tiktoken 동작은 packet 밖 일반 지식에 기반한 의견이므로 확인 대상으로 표시합니다.
- **독립성 한계:** 단일 fresh 세션입니다. 이전 리뷰와 Driver 처분을 함께 받았으므로 anchoring 가능성이 있습니다. blind 또는 완전 독립 검증이 아닙니다.

---

## 1. Overall verdict: **conditional**

v0.2는 R0-I01의 must-fix 대부분을 본문 문안으로 실제 반영했습니다. Driver가 좁힌 범위도 계약 근거로 뒷받침됩니다. DR-0007 v0.10과 충돌해 amendment가 필요한 지점은 찾지 못했습니다.

다만 두 가지가 실행 승인 검토 전에 남아 있습니다.

- **시간·시도 한도:** 적용 대상과 상한에 공백이 있습니다.
- **추적 의무:** V행 사례를 test ID에 연결할 의무의 범위가 좁습니다.

이 둘을 짧은 문안으로 보완하거나 Owner가 승인 시점에 값을 직접 정하면 승인 검토로 넘길 수 있습니다.

| 관점 | 판정 | 요지 |
| --- | --- | --- |
| 계약 정합성 | **approve** | 다음 항목이 S1–S8/A1–A15와 일치합니다: worker 공통 조건·기존 guard·mode change와 drift 구별, fresh-repair 조기 진단과 필수 거절/no token, whole-operation preflight, detach4 reader, old-writer gate, P/Q, 준비 bytes, B 배정. 계약 충돌 없음 |
| 이전 지적 반영 | **conditional (대부분 resolved)** | F2/F3/F4/F7–F11/D1은 resolved입니다. F6·F13은 partial입니다. F1·F5·F12는 resolved이며 작은 잔여만 있습니다 |
| 구현 순서 | **approve** | P1(import/discovery·첫 init candidate·flush phase map) → P2(lifecycle/old-writer 조기 거절·P/Q) → P3 final freeze → P4 순서가 선행 조건을 만족합니다. 미결 의미를 구현 도중으로 숨긴 곳은 없고, 발견 시 정지·exact 변경안으로 돌립니다 |
| 검증 범위·실행 경계 | **conditional** | 다음 세 가지가 남아 있습니다(R0-I02-F1–F3): 한도의 적용 대상과 macOS·누적 상한 공백, V행 ID 연결 범위, runtime fixture 확보 경로 |
| 실행 승인 검토 준비도 | **conditional** | F1–F3을 보완하거나 승인 시 결정하면 넘길 수 있습니다. F4는 closeout 전에 고치면 되지만 지금 한 문장으로 정리하기를 권합니다 |

---

## 2. R0-I01-F1–F13 / D1 반영 표

| 지적 | 판정 | v0.2 근거 line | 핵심 근거 |
| --- | --- | --- | --- |
| **F1** platform test | **resolved** (잔여 → R0-I02-F5) | L54, L72–74, L57, L193 | fcntl import·chmod→100755 기대를 출발점으로 둡니다. 재현 주장은 금지합니다. import guard·assertion을 platform 의미에 맞추고 macOS 성공 기대는 보존합니다. "사전 근거가 있는 비적용 / 예상 거절 / unexpected skip"을 구별하고, 계약 필수 사례의 skip/N/A 종결을 금지합니다. 전체 ID registry를 만들지 않은 Driver 축소는 Maintaining L54(새 registry 아님)·L58(별도 파일 불요)로 뒷받침됩니다. 남은 것은 선언된 비적용 skip을 full-run 판정에서 어떻게 집계하는지입니다 |
| **F2** 선행 입력 순서 | **resolved** | L54–56, L62–68 | 첫 P2 init 전에 prepared source와 candidate를 확보하고, 미확보 시 init을 시작하지 않습니다(L64). 첫 switch/reader 전에 P/Q를 둡니다(L55, L66). P1에서 operation×phase flush map을 만들고 P2 첫 publication 전에 성립시킵니다(L68). P3는 final freeze만 맡습니다(L56). 초기 candidate 증거를 무조건 이월하지 않습니다(L66) |
| **F3** old writer | **resolved** | L55, L60, L76, L226 | P0에서 writer exact bytes×접근 경로와 family별 guard 대조를 합니다. fresh/incomplete init부터 조기 거절을 확인하고 switch·detach4 prefix도 다룹니다. 단일 unknown-window 사례로 전체를 대신하지 않습니다. P4로 미루지 않습니다(L55). POSIX 호환/복사 경로는 실제 노출에 해당할 때만 포함하며, 이 축소는 A13 L843 끝문장·DR L502와 일치합니다 |
| **F4** doctor/status/view | **resolved** | L113, L143 | 지원 read 경로의 성공 또는 정확한 진단, anchor·재flush·쓰기 부재를 확인합니다. 제거된 launcher의 성공을 요구하지 않은 축소는 A8 L694/A10 L787("may report")로 뒷받침됩니다. emulated runtime 아래 read 경로의 fixture 확보는 R0-I02-F3로 분리했습니다 |
| **F5** worker mode change | **resolved** (선택 잔여 → R0-I02-F6) | L119, L126, L135 | "기존 경로의 mode-changing result"로 고쳤습니다. "index 일치 시 허용" 해석을 금지하고 drift와 다른 원인으로 확인합니다. 이는 A2 L578·S6 L375·A3 L598과 일치합니다. "control index가 이미 result mode인 기존 경로" variant는 coverage에 명시되지 않았습니다 |
| **F6** 필수 사례 추적 | **partial** → R0-I02-F2, F6 | L109, L130–147 | A3/A8/A9/A13/A14와 Maintaining 사례를 최소 coverage 표로 연결했고, record parse·도달 불가 fixture·mock으로 닫지 않습니다(L147). 그러나 ID 대응 의무(L147)는 "이 최소 사례"에만 걸립니다. V1–V4/V11의 열거 사례(lock·PS5.1·CRLF 등)에는 대응 의무가 명시되지 않았고, 일부 A2/A8 열거 사례는 함축에 머뭅니다 |
| **F7** refusal fixture | **resolved** (Reviewer의 Owner 사전 disk 준비 처방은 not-adopted, 근거 타당) | L151–162 | 표준 사용자 경계와 추가 환경 필요를 구별합니다. 없는 fixture는 미완료로 남기고 최소 조정만 제시하며, 관리자·share·runtime 설치를 묵시적으로 허용하지 않습니다. A13 L847이 특정 fixture 생성 방법을 요구하지 않으므로 축소는 타당합니다 |
| **F8** macOS runner | **resolved** (상한 공백 → R0-I02-F1) | L195–199, L174, L177 | exact CPython과 child identity, cwd/env, write root·network denial·credential 부재, process-group 회수, ledger, 기존 통제의 적용성·canary 확인을 고정합니다. 역사적 `/dev/fd`·424-ID 시간을 정책으로 복사하지 않으며, 이는 Maintaining L62–67과 일치합니다 |
| **F9** shared 문서·Preview | **resolved** (새 branch/worktree 필수화는 not-adopted, 근거 타당) | L207–211 | 기존 격리 경로를 쓰고 Preview에 자동 통합하지 않습니다. 통합 시 inventory·lifecycle·entry/resume 소비를 검증합니다. A15 조건부 문구로 qualification 순환을 만들지 않습니다. Maintaining L56과 일치합니다 |
| **F10** 보존·반출 | **resolved** (local commit 포함 처방은 not-adopted, Workflow L98로 타당) | L168, L170 | base commit + exact diff + untracked bytes·mode·runner·payload를 보존하고 digest-only를 금지합니다. guest→host 반출 후 bytes·size·readable을 대조하기 전에는 restore하지 않습니다. 반출 수단이 없으면 실행을 시작하지 않습니다. 구체 반출 수단의 선택은 §4 승인 전 선택으로 남습니다 |
| **F11** x64 focused | **resolved** | L205 | ABI/구조체·pointer·last-error, lock 취소·handle, replace sharing·flush, argv/stdin/exit를 초기 후보로 둡니다. 미관측은 그대로 표시하고 full matrix나 장비 보유 gate로 만들지 않습니다 |
| **F12** identity·완료 용어 | **resolved** (잔여 → R0-I02-F4) | L31, L56, L66, L215–224 | 원 수락 identity와 현재 파일을 구별합니다. 11 문서·11 modules·29 paths·15 amendments를 구별하고, P/Q 증거 범위를 한정합니다. 개발 결과·배포 artifact·activation·formal admission의 4단 경계를 둡니다. activation이 A13 qualification(published/refetched 포함) 완료를 전제한다는 연결은 명시되지 않았습니다 |
| **F13** 승인·시도 한도 | **partial** → R0-I02-F1 | L25, L172–182 | 한 번의 bounded 승인이 P0 canary와 P1–P4를 포괄하고, 구체화와 확대를 구별합니다. 횟수 초기화도 금지합니다. 그러나 한도가 개발 반복에도 적용되는지 불명확하고, macOS full·누적 상한에 수치가 없습니다 |
| **D1** Maintaining 의무 | **resolved** (환경 입력 잔여 → R0-I02-F7) | L124, L144, L145, L149 | secret-sentinel·scope 밖 canary(Maintaining L37)를 포함합니다. shipped inventory·installed/update/repair/detach 소비·entry/resume(L44/L56)도 연결했습니다. tokenizer 수치는 Maintaining L79와 정확히 일치하며, fresh-reader exercise를 별도 증거로 둡니다 |

**추가 확인:** Response Map(L232–251)의 각 위치가 본문 line에 실제로 존재함을 대조했습니다. 판정은 Map이 아니라 본문 문안 기준입니다.

---

## 3. 새·잔여 finding

### R0-I02-F1 · P2 · must-fix (실행 승인 전) — 시간·시도 한도의 적용 대상과 상한 공백

- **근거:**
  - plan L176: focused batch에 "회당 20분·초회 1회 + 원인/수정이 있는 2회 이내"를 두고, 이를 P1/P2에 적용합니다.
  - L177: macOS full suite는 "해당 native 측정·여유로 별도 설정"이라고만 하고 수치가 없습니다.
  - L180: 누적 한도는 "P0에서 고정"이라고만 하고 수치가 없습니다.
  - L25: P0 구체화는 경계 집행이고 확대는 별도 결정이라고 정합니다.
  - Maintaining L50: "Use focused checks during iteration." Maintaining L67: 시작 전에 측정에 여유를 더한 budget을 둡니다.
  - Workflow L52: 승인된 record가 time/attempt limits를 명시합니다.
- **실패·오해 경로:**
  - **(a) 적용 대상이 불명확합니다.** P1/P2는 Win32 backend와 lifecycle을 새로 구현하는 단계라 focused test를 여러 번 반복하는 것이 정상입니다. L176의 묶음당 3회 한도가 이 개발 반복에도 적용되면 두 결과 중 하나가 됩니다.
    - 구현 초기에 곧바로 한도에 도달해 범위 결정이 반복됩니다. 이는 L25가 피하려는 반복 승인입니다.
    - "batch 이름 변경 금지(L180)"를 우회하려는 압력이 생깁니다.
    - 반대로 한도가 qualification 증거용 실행에만 적용된다고 읽으면, 개발 반복에는 상한이 전혀 없습니다.
  - **(b) 상한이 비어 있습니다.** macOS full과 누적 한도에 승인 시점의 상한이 없습니다. 그러면 P0가 어떤 값이든 "구체화"로 정할 수 있어, L25의 확대/구체화 구분이 성립하지 않습니다.
- **최소 수정:** 두 가지를 정하면 됩니다.
  1. **한도의 이원화.** 하나는 개발 반복(P1/P2의 iteration)입니다. 이는 단계별 총 시간 상자 또는 총 실행 수 상한으로 묶습니다. 다른 하나는 증거 실행(collection·freeze 후 focused·full·canary)입니다. 기존 시도 한도는 이쪽에 적용합니다.
  2. **승인용 상한 추가.** macOS full 회당 예비 ceiling과, 전체 실행의 누적 상한(또는 단계별 상한의 합)을 넣습니다. P0는 그 이하에서만 값을 고정합니다.
- **시점:** 수치는 Owner가 승인 시 직접 정해도 됩니다. 다만 "적용 대상" 구분 문장은 승인 전에 계획에 있어야 합니다.

### R0-I02-F2 · P2 · must-fix (실행 승인 전, 한 문장) — ID·실행 기록 연결 의무가 최소 coverage 표에만 걸림

- **근거:**
  - L109: V행 하나의 성공으로 하위 사례를 닫지 않는다고 정합니다.
  - L147: "이 최소 사례를 … 실제 ID에 대응"이라고 정합니다.
  - 그러나 최소 coverage 표(L134–145)에는 다음 사례의 행이 없습니다. 모두 V1/V3/V4/V11에만 있습니다.
    - V3 lock: empty anchor, Ctrl+C·강제 종료·재획득, 비상속
    - V1: PS5.1 argv/stdin/file/exit, 한글·quote·metacharacter(A12 L827)
    - V11: 두 autocrlf 설정과 CRLF 예외(A9 L759)
    - V4: A12 L829의 실패 범주 구별 보고
- **실패 경로:**
  - 이 V행 사례들에는 ID 대응 의무가 명시되지 않았습니다. 그래서 R1이 완전성을 판정할 기준이 없고, F6의 원래 실패 경로(요약 행이 부분 증거로 닫힘)가 V1/V3/V11에 남습니다.
  - PS5.1 입력 보존처럼 unittest ID가 아닌 shell 수준 exercise는 L147의 "test의 실제 ID"에 맞지 않습니다. 따라서 증거 형태 자체가 정의되지 않습니다.
- **최소 수정:** L147의 대응 대상을 "V1–V12 행의 열거 사례와 최소 coverage"로 넓힙니다. unittest가 아닌 native exercise는 runner가 부여한 exercise ID·argv·transcript로 같은 ledger에 연결한다고 한 문장을 추가합니다. 새 registry는 필요 없습니다.

### R0-I02-F3 · P2 · 승인 전 Owner 선택 필요 — runtime 거절 fixture의 확보 경로 부재

- **근거:**
  - V1(L113)은 emulation·unsupported Python 거절과 emulated 상태의 read 진단을 요구합니다.
  - DR L483, A6 L642, A10 L787은 x64-on-ARM64 emulation·32-bit·POSIX 호환 runtime의 mutation 거절을 정하고, 실제 조건 검증을 요구합니다.
  - fixture 표(L155–160)는 filesystem 계열만 다룹니다.
  - L162: "runtime 설치는 … 묵시적 권한이 아니다."
  - L147: mocked 성공으로 native 의무를 닫지 않습니다.
- **실패 경로:**
  - 대표 ARM64 guest에 x64 CPython(emulated), 32-bit CPython, 허용 외 patch, free-threaded build가 이미 있는지 계획은 다루지 않습니다.
  - 없으면 V1의 거절 증거는 승인된 경계 안에서 미완료가 됩니다. 이 결과 qualification이 막히거나, mock·주입 identity로 대체하려는 압력이 생깁니다.
  - 계획은 이 경우를 일반 규칙(L162)으로만 처리하므로, 승인 검토자가 이 공백을 미리 알 수 없습니다.
- **최소 수정:** fixture 표에 "runtime 거절" 행을 추가합니다. 담을 내용은 다음과 같습니다.
  - 필요한 interpreter 종류
  - 이미 확보됐는지 여부
  - 필요 시 설치 방법: exact installer identity와 network를 쓰지 않는 반입 경로
  - 미확보 시 처리: 미완료로 남김
- **Owner 결정:** 설치를 이번 실행 범위에 포함할지 승인 때 정합니다.

### R0-I02-F4 · P2 · must-fix (closeout 전, 지금 한 문장 권장) — activation 전제와 A13 qualification의 관계 불명

- **근거:**
  - plan L60은 P4 완료를 "P4 qualification"이라고 부릅니다.
  - L56/L220은 published/refetched equality를 별도 배포 단계로 넘깁니다.
  - L221 activation 행은 "qualified 환경·남은 조건"만 적습니다.
  - A13 L841: "verify exact source/artifact/published/refetched bytes" — qualification 범위에 포함됩니다.
  - DR L962: "qualification 누락을 남긴 채 activation하지 않는다."
- **실패 경로:**
  - Owner가 개발 결과를 수락한 뒤 activation 기록이 "P4 qualification 완료"를 근거로 작성될 수 있습니다.
  - 그 경우 published/refetched equality가 없는 artifact가 activation될 수 있습니다.
  - 계획 문안만으로는 이것이 금지된다는 점이 드러나지 않습니다.
- **최소 수정:** 다음 두 가지를 반영합니다.
  - 용어: L60의 "P4 qualification"을 "P4 통합 검증"으로 바꾸거나, P4 검증이 A13 qualification의 일부라고 명시합니다.
  - activation 행: "A13 qualification 전체 완료가 전제이며, 여기에는 activation 대상 exact artifact의 published/refetched equality가 포함된다"를 추가합니다. criterion 10의 anonymous 증거는 formal admission에 남깁니다.

### R0-I02-F5 · P3 · 선택 — 선언된 비적용 skip의 full-run 판정 규칙 (F1 잔여)

- **근거:** L74는 "사전 근거가 있는 비적용 POSIX 메커니즘"과 unexpected skip을 구별합니다. 반면 L57·L193·A13 L851·A3 L600은 "skip은 PASS가 아님"이라고 정합니다.
- **오해 경로:** macOS 전용 사례(예: fullfsync)가 Windows에서 선언된 skip으로 남을 수 있습니다. 이때 R1에서 해석이 갈립니다.
  - 한쪽은 L57에 따라 "full run 미완료"로 봅니다.
  - 다른 쪽은 L74에 따라 "선언된 비적용"으로 봅니다.
  - 안전 문제는 아니지만 판정 분쟁과 사후 재분류 압력이 생깁니다.
- **최소 수정:** 한 문장으로 정합니다.
  - 선언된 비적용 ID 목록은 집계 대상 실행 전에 근거와 함께 고정합니다.
  - 이 ID들은 실행 PASS로 세지 않고 별도 범주로 보고합니다.
  - 계약 필수 Windows 사례는 이 목록에 넣을 수 없습니다.
  - 그 밖의 skip은 non-pass입니다.

### R0-I02-F6 · P3 · 선택 — 최소 coverage의 함축 사례 명시 (F5·F6 잔여)

다음은 모두 계약 열거 사례입니다. 현재는 일반 문구에 묻혀 있습니다(L134–140).

- **A2 L578·A4 L614·L885:** rename/move/copy 결과가 새 untracked `100755` destination을 만드는 거절 사례와, 일괄 rename 금지가 아님을 보여주는 대조 사례(같은 mode로 tracked destination에 가는 경우).
- **F5 variant:** control index가 이미 result mode와 같은 기존 경로의 mode 변경 사례. 어느 guard가 거절하는지(policy-level unsupported 또는 baseline stale) 원인 label을 A12 L829의 범주로 고정합니다.
- **A2 L582·A11 L807:** 중단된 worker accept apply를 원 ticket으로 재개하는 사례(lifecycle `--recover` 없음)와, 다른 writer에 대한 pending barrier.
- **A8 L688:** read-only preflight가 `.hrn/detached.json` 발행 **전에** 전체 remove set과 필수 flush 대상을 덮는 사례.
- **A8 L698:** historical detach 1/2/3 기록을 4로 재해석하거나 다시 발행하지 않는 사례.

**최소 수정:** 해당 coverage 행에 위 항목을 단어 수준으로 추가합니다.

### R0-I02-F7 · P3 · 선택 / 승인 시 확인할 실행 입력 — tokenizer 환경과 fresh-reader 수행자

- **근거:** L149, L145, L162(runtime 설치 묵시 권한 아님), Maintaining L79, Workflow L108(agent 호출에는 인증·disclosure 확인 필요).
- **경로 (의견, packet 밖 일반 지식):**
  - `tiktoken==0.13.0`을 설치해야 하고, `o200k_base` 인코딩 파일은 캐시가 없으면 network에서 받는 것으로 알고 있습니다. 실제 동작은 실행 측에서 확인할 사항입니다.
  - 이 측정 환경의 출처가 계획에 없으면, P3에서 network나 설치 권한이 필요해져 정지할 수 있습니다.
  - fresh-reader exercise를 새 agent 세션으로 수행한다면 그것은 agent 호출입니다. 따라서 별도 인증과 disclosure 확인이 필요합니다. 계획은 누가, 어떤 수단으로 수행하는지 정하지 않았습니다.
- **최소 수정:** 실행 승인 요청에 두 가지를 명시합니다.
  - tokenizer 환경: 기존 고정 환경 또는 승인된 1회 반입.
  - fresh-reader 수행자와 수단: human 또는 지정 agent 세션, 그리고 전달 데이터 범위.

### R0-I02-F8 · P3 · 선택 — v0.1 문구의 무표시 삭제

- **근거:**
  - diff L59: v0.1 P1 근거에 "macOS 기존 경로 보존. 독립 probe 통과를 제품 통합 PASS로 재사용하지 않음"이 있었습니다. v0.2 L54에서는 이 문구가 빠졌습니다.
  - Response Map(L236–251)에는 이 삭제에 대한 표시가 없습니다.
  - L182는 probe의 *시간*만 다루고, A13 L851은 timing과 source inspection만 다룹니다.
- **경로:** P1 focused 결과를 정리할 때, 이전 probe 관측(예: replace 실패, delete share 거절)을 제품 증거로 끌어올 여지가 문안상 약해졌습니다.
- **최소 수정:** P1 근거 열이나 L147에 위 문장을 복원합니다.

### R0-I02-F9 · P3 · 선택 — prepared source 변환 범위와 P/Q 역할 명확화

- **근거:** L64, L66, L95, A9 L714("future build/packaging plan must identify … explicit preparation step"), A9 L761.
- **경로 1 (변환 범위):** 준비 도구의 원칙은 있습니다. 그러나 common source 대비 기대 차이 범위가 없습니다. 예를 들어 launcher literal 한 줄만 다른지 명시되어 있지 않습니다. 그래서 R1이 "숨은 변환 없음"을 판정할 기준이 약합니다.
- **경로 2 (P/Q 역할):** P와 Q 중 어느 쪽이 activation 후보이고 어느 쪽이 test 전용 fixture release인지 표시가 없습니다. fixture 쪽 identity가 배포나 activation 대상으로 혼동될 수 있습니다.
- **최소 수정:**
  - 기대 변환 범위를 적고, 그 밖의 차이는 범위 결정 대상으로 둡니다.
  - P/Q의 역할 구분을 P3 freeze 기록 항목에 추가합니다.

---

## 4. 실행 승인 검토로 넘길 수 있는 범위·남은 선택·residual risk

### 넘길 수 있는 범위

R0-I02-F1·F2를 문안으로 보완하거나 Owner가 승인 시 직접 정하고, F3의 runtime fixture 처분을 결정하면 다음 범위를 승인 검토 대상으로 볼 수 있다고 판단합니다.

- P0 canary와 입력 고정
- P1–P3 구현·검증
- P4 대표 UTM 전체 검증, macOS focused·full 회귀, 가능한 x64/물리 focused 보완
- Closeout의 개발 결과 제시

F4–F9는 승인을 막지 않습니다. F4는 closeout 전 필수입니다.

**제한:** 이 판단은 계획 문안의 준비도에 대한 의견입니다. 제품 실행 PASS, Owner 승인, Git·publication·adopter 권한을 뜻하지 않습니다.

### 승인 전 Owner가 선택할 것

1. **시간·시도 한도:** 개발 반복과 증거 실행의 한도 체계, macOS full ceiling, 누적 상한 (F1).
2. **runtime fixture 설치 여부:** emulated x64·32-bit·허용 외 CPython을 guest에 반입할지 (F3).
3. **guest→host 반출 수단:** 다음 중 무엇을 허용할지 정합니다.
   - 실행 중 차단과 양립하는 수단
   - 실행 종료와 child 부재 확인 뒤 잠시 쓰는 share 경로(L170은 평가 대상으로만 둠)
   - L162에 따라 일반 승인에 묵시적으로 포함되지 않으므로, 승인문에 명시해야 합니다.
4. **remote·non-NTFS·다른 volume fixture:** 사전 준비(UTM host 쪽 disk 추가 등)를 범위에 넣을지, 미완료로 둘지.
5. **tokenizer 환경과 fresh-reader 수행자** (F7).
6. **old-writer 최소 거절 장치의 승인 경계:** 계약 의미를 바꾸지 않는 장치는 실행 승인 안에서 구현한다고 확인할지 정합니다. L60의 "먼저 제안한다"가 추가 승인 단계로 읽히지 않게 하려는 것입니다. 의미를 바꾸는 장치는 계획대로 amendment로 갑니다.

### 승인 후 P0에서 고정할 실행 입력

이 항목들은 승인된 경계 안의 구체화입니다.

- exact tuple, VM/recovery identity, restore 실측
- old writer exact bytes×접근 경로 표
- Windows/macOS runner·policy·canary 결과
- focused 묶음 목록과 phase budget
- 반출 수단의 합성 파일 확인
- base+diff 보존 방식
- 선언된 비적용 목록의 위치(F5)

### residual risk

- **old-writer 처분:** P0/P2에서 노출 old writer의 거절이 성립하지 않으면 amendment로 돌아갈 수 있습니다. 계획은 이 경우 정지하도록 정했지만 일정 위험은 남습니다.
- **PS5.1 입력 보존:** 실패하면 S7에 따라 미지원으로 남고, PowerShell 7 대안을 별도로 선택해야 합니다.
- **x64·물리 장비:** 계속 미관측일 수 있습니다. 계약상 허용되며, unobserved로 표시해야 합니다.
- **remote/non-NTFS fixture:** 미확보 시 A13 qualification이 미완료로 남아 activation이 늦어질 수 있습니다.
- **P/Q 호환 증거:** 두 fixture release와 관측한 record family에 한정됩니다. 미래 release 호환은 보증하지 않습니다(L66).
- **미확인 source 주장:** 제품 source에 관한 주장(fcntl import, product.py 경로, DR-0002의 11-document 집합)은 이 리뷰에서 직접 확인하지 않았습니다. Driver의 정적 대조로 남습니다.
````

### Document Verification And Retention

2026-10-18 정적 문서 검증에서 GFM parser(marked 17.0.5)의 문서 6개·로컬 link/anchor 187개가 통과했다. code 밖 literal emphasis·trailing whitespace·source 문서의 private 식별자 노출을 찾지 못했다. 입력 packet의 8개 span과 원 파일 identity, 리뷰 14개 라운드의 원문·고정 hash, 기존 CHORE/private record prefix를 확인했다. 기록 두 파일을 제외한 252개 source/evidence 입력은 동일하다. 계획 v0.2·수락 DR 전체와 제품/tests/runner·normative 문서·catalog/navigation은 이번에 바뀌지 않았다.

HEAD와 tracked diff도 그대로이며 diff-check를 통과했다. 이번 reviewed tracked diff SHA-256은 `fd2677e7a3e737d72036d694a5b223304cf53645883c4c2e0aefb6a6bcdb2058`다. 문서 검증은 제품 test 실행, 새로운 실험이나 독립 재현이 아니다.

정리 완료: final과 동일한 partial, 빈 stderr, 검사 helper·중간 JSON 4개 및 빈 tool-temp 디렉터리 1개를 사용 종료 확인 후 삭제했다. request·packet·입력 manifest·final·metadata·runner 6개는 이 라운드의 Owner/Driver 처분과 후속 계획·실행 승인 입력 비교를 위해 보존하며 해당 입력이 고정되면 재평가한다. 기존 v0.2 diff·작성 입력은 후속 개정 비교/복구 소비자가 남아 유지한다. worktree·VM·마지막 recovery·probe·기존 review 근거와 활성 경로는 바꾸지 않았다.

## Implementation Plan Revision 0.3 — 2026-10-18

Owner는 “R0-I02와 네 판단을 반영해 후속 구현·검증 계획을 v0.3으로 보완해줘. 개발 반복과 증거 실행의 한도, 전체 검증 사례의 증거 연결, activation 전제를 명확히 하고 과도한 권고는 좁혀 반영해. DR-0007 v0.10과 B안, 공통 조건 중심 worker 지원은 유지하고 추가 실험이나 제품 구현은 시작하지 마.”라고 요청했다. 이에 [후속 계획](windows-native-implementation-plan.md)을 v0.3으로 보완했다. 이 절이 준비 작업의 진행 정본이며 새 구현 task를 선택하거나 계약을 다시 수락한 기록이 아니다.

### Changes And Preserved Boundaries

- R0-I02-F1: P1/P2 개발 반복은 단계별 활성 시간으로 묶고, 입력을 고정한 canary와 최종 candidate 증거 실행에는 회당·횟수 한도를 적용했다. P0 2시간·P1 8시간·P2 12시간·P3 4시간·P4 12시간·중단/보존 2시간, 총 40시간과 양 OS full suite 회당 120분을 승인 검토용 예비 상한으로 제안한다. 측정된 예상 시간이나 이미 승인된 실행값은 아니다. 먼저 도달하는 한도를 적용하고 revision·batch·세션·단계 변경으로 초기화하지 않는다. 실제 budget은 native 관측과 여유로 상한 이하에서 고정한다.
- F2: V1–V12의 모든 필수 하위 사례와 최소 coverage에 실제 test/exercise ID·mode·명령·입력·독립 oracle·transcript/결과 연결을 요구했다. 새 registry나 지금 실행한 것처럼 보이는 가상 ID는 만들지 않았다.
- F4: P4 통합 검증과 A13 전체 qualification을 구별하고, activation 대상 artifact의 published/refetched equality를 포함한 전체 증거가 activation에 선행함을 명시했다. criterion 10과 live macOS Preview 이후 formal admission이라는 기존 경계는 유지했다.
- F3/F5–F9: runtime 거절 fixture와 tokenizer/reader 입력, 사전 비적용 집계, worker 변형·원 ticket 재개·detach 사전 gate/역사 pair, probe 증거 제한, 준비 변환/P/Q 역할을 보완했다. 모든 unsupported runtime·volume/share 설치, 특정 오류 label 강제, launcher 한 줄 변환, 별도 내부 선택 승인 gate는 채택하지 않았다. 실제 미확보 필수 관측은 미완료로 남긴다.

반영 위치는 계획의 [Revision 0.3 Response Map](windows-native-implementation-plan.md#revision-03-response-map)에 정리했다. 기존 R0-I01/R0-I02 Reviewer 원문·Driver 처분과 conditional 판정은 그대로다. 수락 DR 전체, B 배정, 공통 조건과 모든 기존 guard로 판단하는 worker 지원, macOS 보존, 제품 자동 replace retry 0회는 바꾸지 않았다. Source Change Map과 Native Implementation Decisions 본문도 그대로 유지했다.

### Identity And Next Boundary

출발 계획 v0.2는 45,337 bytes / SHA-256 `8feaadab9f0158ff7f0d16f1c26145243eb95631696efc689d413f835d44e332`이며 R0-I02 frozen packet에서 exact bytes를 회수했다. 결과 v0.3은 56,070 bytes / `ba465032e0a4c8e5a2112157d90631eb28fcb0798b7cbfa72a249bf85315413a`다. 변경은 R0-I02 처분과 현행 revision 표시를 위한 총 23개 지정 변경(반영표 추가 포함)으로 한정했다.

수락 metadata 포함 DR-0007은 181,284 bytes / `e7679a8e11b5e38171888ab6da748cabd6ad5e46dc84e48205733a8e0e6d9ede`로 동일하다. source baseline `a93f71c359c4f0a9d57fcfb50d5999160e870f77`과 기존 tracked diff도 바꾸지 않았다. 이번 수정 대상은 계획과 이 기록, private 실행 맥락 기록뿐이다.

다음 검토 대상은 v0.3과 그 실행 범위다. v0.3의 새 R0나 미래 구현 R1은 아직 수행하지 않았고, 구현·검증 실행 승인도 아직 없다. 예비 한도와 실제 환경/전송/호출 경계를 한 번의 bounded 실행 승인에 담되 승인 범위 안의 구체화마다 Owner 결정을 반복 요구하지 않는다. 새 실험·제품/tests/runner 구현·VM/reviewer 실행·Git action은 수행하지 않았다. 기존 STATUS·catalog/navigation 갱신이나 새 task ID는 필요하지 않다.

### Verification And Retention

2026-10-18 정적 검사에서 GFM parser(marked 17.0.5)의 문서 7개·로컬 link/anchor 197개를 확인했다. code 밖 literal emphasis가 없고 신규 문안의 trailing whitespace·private 식별자 유입이 없다. 기존 CHORE의 과거 명칭 두 건과 preliminary 원문의 whitespace는 이번 변경과 구별해 보존했으며, 전체 이력의 공개 적합성을 새로 승인한 검사는 아니다. 공개 준비 시 기존 노출 항목의 별도 처분이 필요하다.

260개 이전 입력 중 계획·기록 두 파일을 제외한 257개가 동일하다. 수락 DR 전체·기존 record prefix·리뷰 14개 라운드 원문/고정 입력은 보존됐고, v0.2 frozen bytes·23개 변경 재적용·diff 역적용을 대조했다. Source Change Map·Native Implementation Decisions·v0.2 반영표와 Owner 수락 인용도 그대로다. HEAD·tracked diff·Git status는 변경 전과 같으며 diff-check를 통과했다. 이는 문서 검사이며 제품 실행이나 새 R0/R1 증거가 아니다.

작성 입력 manifest와 v0.2→v0.3 exact diff는 후속 v0.3 검토·실행 입력 비교와 rollback에 필요해 보존한다. 결과와 복구 자료를 확인하고 열린 파일이 없음을 확인한 뒤 작성 중간 파일 edit-map.json 1개를 삭제했다. 검사 helper·추가 전체 source 복사본은 만들지 않았다. 기존 worktree·VM/마지막 recovery·probe·리뷰 근거는 가까운 후속 구현/계획 검토와 복구 소비자가 남아 유지했으며 활성 경로는 바꾸지 않았다.

## R0-I03 — Implementation Plan v0.3 Re-review And Driver Judgment — 2026-10-18

Owner는 “후속 구현·검증 계획 v0.3을 Claude CLI로 R0 재리뷰해줘. R0-I02 지적과 네 처분의 반영 여부, 개발 반복·증거 실행 한도와 activation 전제, 실행 승인 검토 준비도를 확인하고 네 판단도 정리해줘. B안과 공통 조건 중심 worker 지원은 유지하고 추가 실험이나 제품 구현은 아직 시작하지 마.”라고 요청했다. 이번 범위는 고정 계획의 Claude CLI 정적 R0-I03 한 회와 Driver 대조·기록이다. 계획·계약 수정, 새 실험·제품/tests/runner 구현, VM 실행과 Git action은 포함하지 않는다.

### Verdict And Driver Assessment

Reviewer 판정은 conditional(좁은 범위)이다. R0-I02의 F1–F9는 모두 resolved이며 이전 지적 반영·계약 정합성·activation 전제는 approve다. 개발/증거 한도와 실행 승인 검토 준비도는 아래 두 항목 때문에 conditional이다. 수락 DR-0007 v0.10을 바꿔야 할 충돌은 찾지 못했다.

Driver도 두 실행 규칙을 명확히 한 뒤 bounded 실행 승인을 검토하는 것이 적절하다고 본다.

1. 사전 비적용·import-safe 규칙을 Windows와 macOS 양쪽에 적용한다. 각 OS에서 반드시 입증해야 할 계약 사례와 기존 성공 기대는 그 OS의 비적용 목록으로 빼지 않는다.
2. R1 처분에 따른 수정·재검증도 기존 P4 시간과 증거 시도 한도를 이어 쓰도록 한다. R1 준비·검토·처분의 시간 귀속, CLI 호출 방식·범위·한도도 실행 승인에 한 번 명시한다. 일반 구현 승인으로 reviewer 호출이 자동 허용되거나 Closeout이 새 예산을 만드는 것으로 해석하지 않는다.

이는 계획의 집행 규칙 보완이다. 현재 macOS 실패를 재현한 것이 아니며, 이미 수락한 Windows 계약이나 B 배정·공통 조건 중심 worker 지원을 다시 설계할 근거도 아니다. 선택 지적 네 건은 실제 환경 입력이나 짧은 기대값/집계 설명으로 좁혀 반영할 수 있다. 이 요청에서는 문안을 수정하거나 실행을 시작하지 않는다.

### Invocation And Exact Inputs

- 공통 review procedure와 workflow-cross-review의 기록 경계를 적용했다. Owner의 직접 CLI 요청에 따라 고정 packet을 전달했다. CLI 2.1.302, `claude.ai / firstParty / pro` 인증을 scoped Keychain 조회에서 확인했으며 provider/OAuth override는 없었다. account email·비밀값은 기록하지 않았다.
- 실제 model `claude-opus-5-5`, fresh session `20f8259c-bb29-4cb2-8d0d-e755d5521c1a`. model override 없이 no-tools·strict empty MCP·세션 비보존으로 실행했다. 1,200초 상한 내 258.695초, exit 0, tool event 0, 입력 8개 전후 drift false였다.
- 계획 v0.3: 56,070 bytes / SHA-256 `ba465032e0a4c8e5a2112157d90631eb28fcb0798b7cbfa72a249bf85315413a`. 수락 metadata 포함 DR: 181,284 bytes / `e7679a8e11b5e38171888ab6da748cabd6ad5e46dc84e48205733a8e0e6d9ede`.
- source baseline `a93f71c359c4f0a9d57fcfb50d5999160e870f77`, tracked diff SHA-256 `fd2677e7a3e737d72036d694a5b223304cf53645883c4c2e0aefb6a6bcdb2058`; 그 밖의 untracked 입력은 manifest에 별도 식별했다.
- packet: 389,698 bytes / `cba86fe87402b040af016ffc4c135c226c0ee7e055a334d44554956a7aa6761e`; request: `6f8de19524784b7dd142af28543f48498f0cfe08ea498de08a8bd194ba249822`.
- final: 21,485 bytes / `77030f152a4e4823f13264cfa8ab9fc6b5fdd9413c53a4af044c7d56719c65bf`; streamed partial과 bytes가 일치했다.

Packet은 계획 v0.3·DR·Maintaining·Source Workflow 전문, admission/Decision Guide 관련 절, 이 CHORE의 R0-I02 원문/처분과 v0.3 작성 기록(당시 3450–3779행), v0.2→v0.3 diff의 8개 입력이다. Reviewer 원문에는 “이전 리뷰 두 회”라고 되어 있으나 직접 제공한 이전 리뷰 전문은 R0-I02 한 회이며 그 안에 R0-I01 반영 요약이 있다. 제품 source/tests/runner·원 probe 출력·DR-0002 본문·외부 API 본문은 제공하지 않았다. fresh session만으로 blind/완전 독립 검증을 주장하지 않는다.

### Finding Dispositions

Reviewer는 F1/F2를 P2 must-fix(승인 전 문안 또는 승인문), F3–F6을 P3 선택 보완/실행 입력으로 분류했다. 아래는 Driver의 후속 반영 판단이며 실제 계획 변경이나 Owner 실행 승인 기록이 아니다.

| Finding | Driver 처분 | 판단과 최소 반영 범위 |
| --- | --- | --- |
| F1 · 양방향 비적용/import | revise | 양 OS의 import-safe collection·사전 비적용 집계를 명시할 취지는 수용한다. 계획 73/75행은 platform별 의미와 macOS 성공 보존을 이미 요구하지만 “POSIX 메커니즘”과 Windows 한정 제외 금지가 역방향 기대를 흐린다. Windows 필수 사례는 Windows에서, macOS 기존 mode-change 등은 macOS에서 제외하지 않는다고 명료화한다. 앞으로 작성할 Windows 전용 test가 실제 macOS 실패/skip을 냈다는 주장은 하지 않는다. |
| F2 · R1 후 수정/호출 한도 | revise | R1 지적의 source/test 수정·재검증은 P4 누적 시간과 기존 증거 시도에 귀속시키는 방향을 채택한다. R1 준비·검토·처분 자체의 시간 및 reviewer 호출 횟수/시간도 실행 승인에서 명시해 Closeout을 한도 밖 단계로 만들지 않는다. CLI는 명시 승인된 범위에서만 호출하며 manual relay도 가능하다. 모든 작은 correction마다 별도 승인을 추가하거나 현 40시간을 자동 증액하지 않는다. |
| F3 · x64/물리 실행 경계 | revise | 추가 환경을 실제 사용할 때 그 환경의 통제·복구·반출·canary 입력과 시간 귀속을 정한다. P4에서 추가로 준비하면 P4 시간에 포함한다. 물리 환경에 VM snapshot을 요구하지 않고 해당 환경의 회수 가능한 입력과 격리 통제를 확인한다. 실제 사용할 환경/권한만 승인 범위에 넣으며 장비를 반드시 확보해야 하는 gate는 만들지 않는다. 미관측 tuple은 그대로 남긴다. |
| F4 · fixture 범주와 잔여 결과 | accept | A13의 non-NTFS/remote/unknown 등 각 필수 범주는 자체 관측 또는 unavailable로 개별 처분하며 서로 대체하지 않는다. 개발 결과에 실제 실행·식별된 상속·미확보/미해결을 함께 제시하고 “개발 범위”라는 표현으로 필수 공백을 삭제하지 않는다. 새 mount/share 생성이나 전체 지원 외 runtime matrix를 자동 승인하는 처방은 아니다. |
| F5 · 보존 여유와 첫 full budget | revise | 통상 결과 보존은 단계 시간, 2시간 여유는 정지 조건 이후의 회수·보존으로 귀속을 명확히 하는 것이 적절하다. 첫 full의 근거는 측정한 native focused/collection 비용과 명시된 추정·여유이며, 완전 suite를 이미 실측했다고 하지 않는다. Maintaining 67행이 첫 full 전에 별도 full을 반드시 요구한다고 해석하지 않는다. 시도 사이 budget 조정은 원 실패·새 근거를 보존하고 승인 ceiling·P4/전체 잔여·기존 시도 안에서만 가능하도록 명료화한다. timeout만 보고 자동 증액하거나 시험 도중 올리지 않는다. |
| F6 · worker 재개 기대값 | accept | “거절” 행에 성공 대조 사례와 원 ticket 재개가 함께 있어 oracle 기대를 혼동할 수 있다. 지원 결과가 원 조건과 모든 guard를 만족하면 exact 재개 성공, 조건 불충족/unknown은 해당 stable non-pass, 다른 writer는 pending barrier로 거절한다는 기대값을 구별한다. 원 ticket과 whole-result 의미를 바꾸거나 lifecycle --recover를 추가하지 않는다. |

### Driver Cross-Checks And Limits

- **한도:** 계획 174–202행은 회당·횟수·단계·전체 상한 중 먼저 도달한 제한을 적용한다. 두 OS·두 mode·각 두 번의 full이 모두 120분을 쓰면 16시간으로 P4 12시간을 넘지만, 198행은 모든 슬롯 사용을 보장하지 않는다. 이 산술은 상한 증액 근거가 아니라 승인 시 알아야 할 배정의 성질이다. R1 뒤 correction의 귀속만 명시적으로 닫는 편이 좋다.
- **기존 macOS 의미:** DR A3 600행은 macOS 성공적인 mode-change 기대를 유지한다. 양방향 비적용 문구를 보완해도 이 요구와 Windows 필수 native 관측을 제외할 수 없다. 예상 거절 검증의 성공과 skip/N/A는 서로 다른 결과다.
- **Worker:** DR A2 582행은 pending/replay/cancellation·exact recovery input·기존 macOS worker 의미를 보존한다. 계획 136행은 원 ticket 재개를 “거절” 행에 배치했으므로 F6처럼 기대값을 붙이면 충분하다. 현재 구현이 잘못됐다고 재현한 지적은 아니다.
- **Activation:** 계획 61/241/244행과 DR A13 841–851행·Consequences 962행은 published/refetched equality를 포함한 전체 qualification을 요구한다. criterion 10의 authenticated/anonymous 증거 구별과 formal admission 시점도 유지한다. Reviewer 표의 “그 뒤에 criterion 10”은 anonymous 증거를 반드시 activation 이후에만 수집한다는 새 순서로 채택하지 않는다. 각 증거의 확보 시점과 formal 지원 결정은 원 계약을 따른다.
- **환경:** DR A6 640–644행은 대표 UTM full과 차이가 있는 x64/물리 focused 배정을 유지하며, 미관측을 추가 full matrix·물리 장비 보유 gate로 만들지 않는다. non-NTFS mount나 SMB 설정의 실제 권한 필요 여부는 이번에 조사·실행하지 않았다. Reviewer의 일반 환경 추론은 P0 가용성 확인 대상으로만 둔다.
- **호출:** Source Workflow 64/108행의 R1과 명시 CLI authorization을 함께 적용한다. 지금 요청은 R0-I03 한 회에 대한 것이며 미래 R1·fresh-reader나 제품 실행까지 승인하지 않는다.

Reviewer가 승인 입력으로 열거한 항목을 각각 새 approval gate로 만들지 않는다. 실제 사용할 환경·호출·전송 경계와 한도, 구현 task/단일 진행 기록을 한 번의 실행 승인에서 구체화하고, 그 안의 가용성 확인과 ordinary correction은 맡은 단계에서 진행할 수 있어야 한다. 필수 관측을 확보하지 못하면 qualification/activation은 완료되지 않는다.

### Next Boundary

권고는 F1/F2의 두 집행 규칙을 계획 본문 또는 exact 실행 승인문에 명시하고, F3–F6의 필요한 기대값·집계·환경 입력을 같은 범위에서 정리하는 것이다. 새 계약 amendment나 B/worker 지원 변경을 요구할 근거는 없다. 40시간과 회당 120분은 여전히 채택 여부를 결정할 예비 상한이며, 환경과 권한도 실제 선택 범위로 고정해야 한다.

이번 요청에서는 계획 v0.3과 DR bytes를 보존했다. 작성 당시 “not re-reviewed” 표기는 고정 입력에 유지하고, 후속 재리뷰 상태는 이 dated 기록이 설명한다. 추가 실험·제품 구현·VM·후속 reviewer·Git action은 수행하지 않았다. 이 판정과 Driver 처분은 Owner의 계획/실행/결과 수락을 대신하지 않는다.

### Reviewer Response Verbatim

````markdown
# R0-I03 — Windows Native Implementation And Verification Plan v0.3 정적 재리뷰

## 0. 범위와 한계

- **검토 대상:** 계획 v0.3(56,070 bytes, `ba465032…413a`)을 읽었다. 대조 자료는 다음과 같다.
  - 수락 metadata 포함 DR-0007(`e7679a8e…`) 전문
  - Maintaining·Workflow 전문
  - Windows Admission·Decision Guide 해당 절
  - CHORE의 R0-I02 원문·Driver 처분·v0.3 작성 기록(3450–3779행)
  - v0.2→v0.3 exact diff
- **식별값:** hash·byte 수는 packet 값을 인용했을 뿐 재계산하지 않았다.
- **수행하지 않은 것:** tool 실행, 파일 접근, 실험, 제품 test, VM 실행을 하지 않았다. 아래 판단은 모두 문안 대조와 의견이다. 실행·재현 결과로 읽으면 안 된다.
- **packet에 없는 근거:** 제품 source/tests/runner, DR-0002 본문, Microsoft API 문서 본문, probe 원출력은 packet에 없다. 따라서 다음은 Driver의 정적 주장으로만 다뤘다.
  - `fcntl` import와 chmod 기대값의 현재 위치
  - 실제 sync 호출 지점
  - 11-document 집합
- **독립성 한계:** 단일 fresh session이며 이전 리뷰 두 회와 Driver 처분을 함께 받았다. anchoring 가능성이 있고 blind 또는 완전 독립 검증이 아니다.

---

## 1. Overall verdict: **conditional (좁은 범위)**

R0-I02-F1–F9는 모두 본문 문안에 실제로 반영됐다. Driver가 범위를 좁힌 부분도 수락 계약 근거로 뒷받침되며, DR-0007 v0.10과 충돌하는 지점은 찾지 못했다.

남은 것은 승인 전에 한 문장씩 보완하거나 승인문에서 정하면 되는 두 가지다.

- **R0-I03-F1:** 사전 비적용 범주가 한 방향(Windows에서 POSIX)만 정의되어 있다. 이 때문에 macOS 전체 회귀의 판정이 막힐 수 있다.
- **R0-I03-F2:** Closeout·R1 이후의 수정 반복이 어떤 한도에 속하는지 정해져 있지 않다.

| 관점 | 판정 | 요지 |
| --- | --- | --- |
| 이전 지적 반영 | **approve** | F1–F9 모두 resolved. 좁힌 반영 범위가 계약 의무를 누락하지 않았다. 불필요한 신규 gate도 만들지 않았다 |
| 계약 정합성 | **approve** | 다음이 S1–S8/A1–A15와 일치한다. 실제 충돌은 없다.<br>- B 배정, worker 공통 조건·기존 guard·mode-changing 거절과 drift 구별<br>- fresh repair 필수 거절/선택 조기 진단/no token<br>- whole-operation preflight<br>- detach4 reader·역사 pair, old-writer gate<br>- P/Q 양방향, prepared source·artifact equality |
| 개발/증거 한도 | **conditional** | 개발 반복과 증거 실행의 이원화, 활성 시간 정의, 먼저 도달한 한도 적용, 재분류에 의한 초기화 금지는 집행 가능하다. 다만 Closeout/R1 이후 수정 루프가 어느 한도에도 속하지 않는다(F2) |
| activation 전제 | **approve** | P4 통합 검증과 A13 전체 qualification(published/refetched 포함)을 구별한다. 그 뒤에 별도 Owner activation, 그 뒤에 criterion 10과 live macOS Preview 이후 formal admission이 오는 순서를 명시했다. Git·publication·adopter 권한으로 자동 확대하지 않는다 |
| 실행 승인 검토 준비도 | **conditional** | F1·F2를 문안으로 보완하거나 Owner가 승인문에서 정하면 검토로 넘길 수 있다. 나머지는 선택 보완 또는 승인 시 입력 사항이다 |

---

## 2. R0-I02-F1–F9 반영 표

| 지적 | 판정 | v0.3 근거 line | 핵심 근거 |
| --- | --- | --- | --- |
| **F1** 한도 적용 대상·누적 상한 | **resolved** (잔여 → R0-I03-F2, F5) | L174, L176, L178–184, L186, L188–196, L198, L200, L202 | 아래 별도 설명 참조 |
| **F2** 전체 사례·exercise 추적 | **resolved** | L110, L148, L75 | 대응 대상이 "V1–V12의 모든 필수 하위 사례와 최소 coverage"로 넓어졌다. 독립 oracle·mode·명령·결과 위치를 기존 ledger에 연결한다. unittest 밖 native exercise는 exercise ID·argv·stdin/file identity·transcript로 연결한다. lock 중단/회수, PS5.1, CRLF·autocrlf 두 설정, A12 실패 범주를 명시했다. P3 문서/reader 사례도 실행 전에 대응한다. 가상 ID·새 registry를 금지한 것은 Maintaining L54/L58과 일치한다 |
| **F3** runtime 거절 fixture | **resolved** (입력 잔여 → §4) | L162, L164 | runtime 거절 행을 추가했다. 기존 가용성은 미확인으로 두고 P0에서 확인한다. 추가 반입 시 exact installer/package·방법·권한·network·회수 경계를 승인 대상에 넣는다. 모든 비지원 runtime 설치와 모든 read 명령 성공은 요구하지 않는다. 이 축소는 A10 L787("Read-only diagnostics may report unsupported or unknown")로 뒷받침된다. mock/fault injection과 native 관측을 구별하고 공백을 남긴다 |
| **F4** activation 전제 | **resolved** | L22, L61, L241, L244 | "P4 qualification" 표현을 "P4 통합 검증은 A13 qualification의 일부"로 정정했다(L61). activation 행은 A13 전체 완료와 그 artifact의 source/artifact/published/refetched equality를 선행 조건으로 둔다(L241). 이는 A13 L841, Consequences L962와 일치한다. criterion 10의 별도성과 formal 시점도 유지했다(L244) |
| **F5** 사전 비적용 집계 | **resolved** (역방향 공백은 새 R0-I03-F1) | L75 | 실행 전에 ID·근거를 고정하고, PASS에 합산하지 않으며, 별도 범주로 보고한다. 필수 Windows 사례는 넣을 수 없고 사후 재분류를 금지한다. 그 밖의 skip·unknown·missing은 non-pass다. 원 지적의 범위(Windows에서 macOS/POSIX 전용 사례)는 닫혔다 |
| **F6** 함축 변형 사례 | **resolved** (표현 잔여 → R0-I03-F6) | L127, L136, L141 | 다음 사례가 모두 명시됐다.<br>- rename/move/copy의 실제 destination 분류와 대조 결과<br>- control index가 이미 result mode인 변형<br>- 원 ticket 재개(lifecycle `--recover` 아님)와 pending barrier<br>- detached marker 발행 전 전체 remove set·필수 flush preflight(A8 L688)<br>- detach 1/2/3 재해석·재발행 금지(A8 L698)<br>오류 label 강제를 채택하지 않은 처분은 타당하다. A12 L829의 범주 구별은 L148의 ID 연결 의무로 여전히 검증된다 |
| **F7** tokenizer·fresh-reader | **resolved** | L150 | P0에서 기존 환경을 먼저 확인한다. 설치·반입·network가 필요하면 그 변경만 승인받는다. 미확보 상태를 PASS로 쓰지 않는다. 수행자(human/명시 승인 agent)·수단·전달 범위를 실행 입력으로 둔다. agent 사용 시 Workflow L108의 인증·disclosure를 적용한다. 신규 gate는 만들지 않았다 |
| **F8** probe 문구 복원 | **resolved** | L55 | "독립 probe 통과를 제품 통합 PASS로 재사용하지 않음"을 복원했다. diff L47로 확인된다 |
| **F9** 준비 변환·P/Q 역할 | **resolved** | L65, L67, L96 | 첫 candidate 전에 파일별 기대 변경·명령·출력을 고정한다. 나머지 파일 보존을 exact diff로 확인한다. 목록과 다르면 멈추고 범위 안의 누락인지 계약/범위 변경인지 판단한다. P3에서 activation 대상과 시험 전용 release를 구별하고 대체 사용을 금지한다. "launcher 한 줄" 고정을 채택하지 않은 처분은 A9 L714("preparation mechanism remains a plan detail")와 일치한다 |

**F1의 근거 상세.**
- 개발 반복: P1/P2 구현·진단·focused·collection과 P3 문서·도구 보완. 단계 누적 시간과 회당 20분으로 묶는다.
- 증거 실행: canary와 최종 candidate collection/focused/full. 회당·횟수 한도를 적용한다.
- 양 OS full 회당 120분 예비 ceiling, 단계 2/8/12/4/12/2시간, 합계 40시간을 둔다.
- 활성 wall time을 정의했다. 작업과 child가 모두 멈춘 대기만 제외하고, 병행 구간은 중복 계산하지 않는다.
- 먼저 도달한 한도를 적용한다. P4에서 P1/P2로 돌아가도 P4 시간에 포함한다.
- revision·batch·세션·단계명 변경이나 개발 반복으로의 재분류로 한도를 초기화할 수 없다.
- phase 간 이동이나 상한 상향은 별도 결정이다.
- 숫자는 측정값이나 예측이 아니라고 명시했다(L198).

**Response Map 대조.** L282–290의 각 위치가 본문에 실제로 존재함을 확인했다. 판정은 Map이 아니라 위 본문 line을 기준으로 했다.

**한도 정합성 추가 확인 (finding 아님).** 최악의 경우 P4 full suite만으로 2 OS × 2 mode × 2회 × 120분 = 16시간이 들 수 있어 P4 12시간을 넘는다. 그러나 L198이 "먼저 도달하는 한도 적용, 모든 재시도 슬롯 사용 보장 아님"을 명시하므로 모순은 아니다. 이는 승인자가 알아야 할 성질이다. 실제 budget이 ceiling에 가까우면 재실행 슬롯은 사실상 쓸 수 없고, 그때는 L200의 조정 결정으로 간다. 이를 이유로 상한 증액을 요구하지 않는다.

---

## 3. 새·잔여 finding

### R0-I03-F1 · P2 · must-fix (실행 승인 전, 한 문장) — 사전 비적용 범주가 한 방향만 정의되어 macOS 전체 회귀가 판정 불능 또는 사후 재분류 압력에 놓임

**근거:**
- L75는 비적용 범주를 "사전 근거가 있는 비적용 **POSIX 메커니즘**"으로 정의한다. 같은 문단은 "그 밖의 skip·unknown·missing은 non-pass"라고 한다.
- L58은 "unknown·skip·timeout·missing은 PASS가 아님"이라고 한다.
- L73은 Windows에서 import할 수 없는 POSIX 의존성만 다룬다.
- 반면 L183·L219·L223은 macOS normal·parent-optimized 전체 회귀를 요구한다.
- Maintaining L64의 과거 anchor는 "no skips"였다.

**실패·오해 경로:**
- P1/P2에서 추가될 Win32 lock·handle·read-only attribute·PS5.1 사례는 macOS에서 `skipUnless` 등으로 skip되는 것이 보통이다.
- 문언대로라면 이 skip은 "그 밖의 skip"이므로 macOS 전체 회귀가 구조적으로 non-pass가 된다.
- 그러면 R1에서 판정 분쟁이 생기거나, L75가 금지하는 사후 재분류("어차피 Windows 전용") 압력이 생긴다.
- macOS에서 Windows 전용 test module을 import하는 단계 자체가 실패하면(예: `ctypes.windll` 모듈 수준 참조), 수집 실패가 0-test PASS 논란으로 이어질 수도 있다. L213은 이를 금지한다.

**최소 수정:** L75 또는 L73에 다음 취지의 한 문장을 둔다.
- 사전 비적용 범주는 양방향 platform 비적용(Windows의 POSIX/macOS 전용 사례, macOS의 Windows 전용 사례)에 같은 규칙을 적용한다.
- Windows 전용 test도 macOS에서 import-safe여야 한다.
- 이때 Windows 계약 필수 사례를 Windows 실행에서, macOS 기존 성공 기대(mode-change 포함, A3 L600)를 macOS 실행에서 비적용으로 둘 수 없다.

새 registry는 필요 없다.

**시점:** 문안은 승인 전 한 문장으로 충분하다. 실제 ID 목록은 승인 후 P1 discovery에서 고정할 입력이다.

### R0-I03-F2 · P2 · must-fix (승인 전 문안 또는 승인문에 명시) — Closeout/R1 이후 수정·재검증 루프의 한도 귀속과 R1 호출 경계가 비어 있음

**근거:**
- 단계 표 L188–196에는 Closeout 행이 없다. 전체 40시간은 "publication·activation·adopter 작업은 포함하지 않음"이라고만 하고 R1과 그 처분은 언급하지 않는다.
- L198의 "P4에서 보정을 위해 P1/P2로 돌아가도 P4 누적 시간에 포함"은 P4 안의 복귀만 다룬다.
- L59와 L239에 따르면 R1·Driver 처분은 Closeout에 있다.
- Workflow L64: R1 기본 적용. Workflow L108: CLI review는 명시 authorization이 필요하다.
- L15·L252는 reviewer 자동 실행을 하지 않는다고만 한다.

**실패·오해 경로:**
- R1이 source 결함을 지적하면 수정 결과는 새 candidate가 된다. 그러면 P4 증거를 다시 판정해야 한다(L213, Maintaining L60).
- 이 수정·재검증이 어느 단계 시간과 증거 시도 계수에 속하는지 문안에 없다. 그래서 두 해석이 갈린다.
  - 한도 밖이므로 무제한이다. 이는 L198의 재분류 금지 취지를 우회한다.
  - 한도가 없으니 즉시 정지다. 이는 L26이 피하려는 반복 승인을 만든다.
- R1을 CLI로 호출할지 Owner가 packet을 중계할지도 정해지지 않았다. 따라서 실행 승인이 R1 호출을 포함하는지 불명확하다.

**최소 수정:** 다음 한 문장으로 충분하다.
- R1 처분에 따른 source/test 수정과 재검증은 P4 누적 시간과 기존 증거 시도 계수를 그대로 이어서 쓴다(또는 중단·보존 여유와 같은 명시 칸에 둔다).
- 한도를 넘으면 정지하고 조정안을 제시한다.
- R1의 CLI 호출은 실행 승인에 포함하거나 별도로 확인한다.

자원 증액을 요구하지 않는다.

**시점:** 승인 전 문안으로 고치거나, Owner가 승인문에서 정하면 된다.

### R0-I03-F3 · P3 · 선택 / 승인 시 범위 입력 — x64·물리 focused 보완의 실행 경계 입력이 단일 VM 전제

**근거:**
- L168·L172의 P0 입력(VM identity·guest root·반출·restore·개인 계정/자격증명 부재)은 대표 UTM VM 하나를 전제로 한다.
- L58·L225는 x64/물리 focused를 P4에 배정한다.
- L180은 canary를 "각 실행 경계"에서 하도록 한다.
- A6 L640에 따르면 환경 제공은 Owner 책임이다.

**경로:**
- 물리 PC는 VM snapshot 복구가 없다. 개인 계정·자격증명이 있을 가능성도 높다. 이 경우 L168의 경계 조건을 충족하기 어렵다.
- x64 VM이나 물리 PC가 나중에 확보되면, 그 경계 입력·canary·반출 확인 시간이 P0 2시간 밖의 P4 12시간에 들어간다. 이 점이 명시되어 있지 않다.

**최소 수정 또는 승인 입력:**
- 이번 실행에서 x64/물리 보완을 범위에 넣을지, 미관측으로 둘지 승인 시 정한다.
- 넣는다면 해당 경계의 L168/L172 입력과 canary를 사용 전에 고정하고 P4 시간에 계상한다고 적는다.
- 격리 경계를 만들 수 없으면 미관측으로 표시한다. 계약상 허용된다(S1, A6 L644).

새 gate는 아니다.

### R0-I03-F4 · P3 · 선택 — 거절 fixture 범주의 비대체성과 "개발 범위 필수 결과"의 잔여 표시

**근거:**
- L159는 "실제로 도달 가능한 거절 경로를 선택"이라고 한다.
- A13 L847은 non-NTFS/remote/unknown 거절을 각각 열거한다.
- L239는 개발 결과에 "V1–V12의 개발 범위 필수 결과"를 요구한다.

**오해 경로:**
- "도달 가능한 경로 선택"을 범주 간 대체로 읽을 수 있다. 예를 들어 reparse 거절 하나로 remote 거절을 대신하는 식이다.
- "개발 범위"의 뜻이 정의되지 않아, fixture를 확보하지 못한 필수 사례가 범위 밖으로 조용히 빠질 수 있다.
- 참고로 non-NTFS VHD mount나 SMB share는 관리자 권한이나 host share가 필요할 가능성이 높다. 이는 일반 지식에 따른 의견이며 실제 가용성은 P0 확인 사항이다.

**최소 수정:** 한 문장이면 된다.
- 각 열거 범주는 자체 native 관측 또는 unavailable로 따로 처분하며 서로 대체하지 않는다. 이는 L77의 "단일 unknown-window 사례를 모든 family의 증거로 쓰지 않는다"와 같은 원칙이다.
- 개발 결과에는 실행·상속·미확보 필수 사례를 Maintaining L60의 세 범주로 나열한다.

### R0-I03-F5 · P3 · 선택 — 예비 한도 집계의 경계 사례 두 가지

**(a) 중단·보존 여유 2시간의 귀속이 불명확하다.**
- L195는 이 여유를 child 회수·증거 보존용으로 두는데, 같은 활동이 각 단계 시간(L186의 "필요한 결과 보존 포함")에도 들어갈 수 있다.
- 그러면 보존 성격의 작업을 여유 칸으로 옮겨 단계 한도를 사실상 늘릴 여지가 생긴다.
- 제안: 여유는 정지 조건(L248)이나 한도 초과가 발생한 뒤의 회수·보존에만 쓰고 귀속을 ledger에 기록한다.

**(b) 첫 full 실행의 budget 근거.**
- 개발 반복은 회당 20분이므로 freeze 전 full 실행은 사실상 없다.
- 따라서 첫 Windows full budget은 focused timing에서 추정한 값이다(L202). Maintaining L67이 말하는 "measured duration"이 아니다.
- 첫 실행이 budget 초과로 incomplete가 되면, 두 번째 시도에서 ceiling 이하로 budget을 다시 고정할 수 있는지가 문언상 분명하지 않다. L202가 금지하는 것은 "시험 도중"의 상향이다.
- 제안: 시도 사이에 기록된 근거로 120분 이하에서 budget을 다시 고정할 수 있다고 한 구절을 둔다.

### R0-I03-F6 · P3 · 선택 — 최소 coverage의 기대 결과 표시

**근거:** L136의 "거절" 행에 "원 ticket으로 중단된 worker accept apply 재개"가 들어 있다.

**오해 경로:**
- 지원 결과의 중단 재개는 성공이 기대된다. 거절 기대값은 이미 발행된 pending의 drift나 미지원 원인에만 해당한다.
- 거절 행에 놓이면 재개 사례가 거절되어야 한다고 oracle이 작성될 수 있다. 이는 A2 L582의 "Preserve ... exact recovery inputs"와 어긋난다.

**최소 수정:** "(지원 결과는 exact 재개 성공, 원 조건 불충족은 stable non-pass)"처럼 기대 결과를 괄호로 표시한다.

---

## 4. 실행 승인 검토로 넘길 수 있는 범위, 남은 선택·전제, residual risk

### 넘길 수 있는 범위 (정적 의견)

R0-I03-F1·F2를 한 문장씩 보완하거나 Owner가 승인문에서 정하면, 다음을 하나의 bounded 실행 승인 검토 대상으로 볼 수 있다고 판단한다.

- P0 통제 canary와 입력 고정
- P1–P3 구현·개발 반복·freeze
- P4 대표 UTM 전체 검증, macOS focused·full 회귀, 범위에 포함할 경우의 x64/물리 focused 보완
- Closeout의 개발 결과 제시

F3–F6은 승인을 막지 않는다. 이 판단은 계획 문안의 준비도에 대한 의견이다. 제품 실행 PASS, Owner 승인, Git·publication·activation·adopter 권한을 뜻하지 않는다.

### 승인 시 명시할 실제 권한 확대 후보

아래 항목만 별도로 확인하면 된다. 나머지 가용성 확인은 승인된 경계 안의 P0 작업이다.

1. **예비 상한 채택:** 40시간·단계 상한·회당 120분·시도 계수를 그대로 채택할지 조정할지. 측정되지 않은 자원 상한이며 소요 예측이 아니다.
2. **runtime 반입:** emulated x64·32-bit·허용 밖 patch/free-threaded CPython을 반입할지(L164). 반입하지 않으면 해당 native 거절 관측은 미완료로 남는다.
3. **filesystem fixture:** non-NTFS·remote·다른 volume fixture에 관리자 권한·host disk/share가 필요한 경우 범위에 넣을지, 미완료로 둘지.
4. **반출 수단:** guest→host 반출 수단, 특히 L172의 "실행 종료 후 잠시 쓰는 전달 경로" 선택지를 허용할지. P0에서 차단과 양립하는 수단이 확인되면 불필요하다.
5. **tokenizer 반입·network:** 기존 환경이 없을 때만 해당한다.
6. **agent 호출:** fresh-reader에 agent를 쓸 경우와 R1 CLI 호출(R0-I03-F2)의 인증·disclosure 범위.
7. **x64/물리 환경:** 이번 범위에 포함할지와 Owner 제공 여부(R0-I03-F3).
8. **진행 기록:** 구현 task ID와 단일 진행 기록의 지정(L28, Workflow L48/L52).

### 승인 후 P0–P3에서 고정할 입력 (권한 확대 아님)

- **P0:**
  - exact tuple, VM/recovery identity, restore 실측
  - old writer exact bytes×접근 경로×family 표
  - Windows/macOS runner·policy·canary 결과
  - 반출 수단의 합성 파일 확인
  - 단계 budget(상한 이하)과 증거 묶음 목록
  - tokenizer·runtime·fixture 가용성
- **P1:**
  - operation×phase flush 대응표
  - 실제 discovery ID와 V1–V12 대응
  - 양방향 사전 비적용 목록
  - prepared source 기대 변경 목록
- **P2:**
  - 새 사례 ID 대응
  - P/Q identity
- **P3:**
  - 최종 P/Q의 역할 기록
  - tokenizer 측정
  - fresh-reader 입력

### residual risk

- **old-writer 처분:** 노출된 old writer의 거절이 성립하지 않으면 qualification/activation이 멈추고 amendment로 돌아갈 수 있다. 계획은 정지 규칙을 갖췄지만 일정 위험은 남는다.
- **PS5.1 입력 보존:** 실패하면 S7에 따라 미지원으로 남고, PowerShell 7 대안은 별도 선택이 된다.
- **fixture 미확보:** runtime 거절과 remote/non-NTFS fixture를 확보하지 못하면 A13 qualification이 미완료로 남아 activation이 늦어질 수 있다. 이는 계약에 맞는 결과다.
- **x64·물리 미관측:** 계속 미관측일 수 있다. 계약상 허용되지만 unobserved로 표시해야 한다.
- **예비 상한:** 측정 근거가 없다. P0 2시간(writer 노출 분석 포함)이나 P4 12시간이 빠듯하면 한도 도달로 정지하고 조정 결정이 필요해진다. 이는 결함이 아니라 의도된 동작이다.
- **P/Q 호환 증거의 한계:** 두 fixture release와 관측된 record family에 한정된다(L67).
- **미확인 source 주장:** 제품 source에 관한 진술(fcntl import, chmod 기대, sync 호출 지점, DR-0002 11-document 집합)과 Win32 API 동작은 이 리뷰에서 직접 확인하지 않았다. Driver의 정적 대조로 남는다.
````

### Document Verification And Retention

2026-10-18 문서 검증에서 marked 17.0.5 GFM의 문서 7개·로컬 link/anchor 197개, code 밖 literal emphasis, 신규 문안 whitespace/disclosure를 확인했다. 기존 역사 기록의 식별자 두 건은 보존된 별도 공개 준비 항목이며 이번 신규 유입은 없다. 계획·수락 DR을 포함한 비변경 입력 260개, frozen packet 8개 span·metadata·final identity, Reviewer 원문 15개 라운드와 기존 두 record prefix가 보존됐다. source HEAD·tracked diff·Git status도 같고 diff-check를 통과했다. 제품 실행·재현 결과가 아니다.

최종 원문과 같은 partial·빈 stderr 2개 및 빈 tool-temp 디렉터리 1개는 CLI 완료와 열린 파일 없음 확인 뒤 삭제했다. request·packet·입력 manifest·final·metadata·runner 6개는 R0-I03 처분과 후속 계획/실행 승인 입력 비교에 필요해 보존하며 그 입력이 고정되면 재평가한다. v0.3 작성 입력/diff는 원문 비교와 rollback 소비자로 유지한다. 기존 worktree·VM/마지막 recovery·probe·리뷰 근거와 활성 경로는 변경하지 않았다.

## Implementation Plan v0.4 — R0-I03 Follow-Up — 2026-10-18

Owner는 “R0-I03과 네 판단을 반영해 후속 구현·검증 계획을 v0.4로 최소 보완해줘. 양방향 비적용 규칙과 R1 이후 수정·재검증의 한도 귀속, reviewer 호출 경계를 명확히 하고 선택 보완은 필요한 범위로 좁혀 반영해. DR-0007 v0.10과 B안, 공통 조건 중심 worker 지원은 유지하고 추가 실험이나 제품 구현은 시작하지 마.”라고 요청했다.

[계획 v0.4](windows-native-implementation-plan.md)는 [R0-I03 원문·Driver 처분](#r0-i03--implementation-plan-v03-re-review-and-driver-judgment--2026-10-18)을 다음 범위로 반영했다. 변경은 계획과 기존 준비 기록에 한정한다.

| 구분 | 반영 내용 |
| --- | --- |
| F1 · 양방향 비적용 | 양 OS의 import-safe collection과 사전 비적용 집계를 명시했다. Windows 필수 native 사례와 macOS 기존 성공 기대는 각 OS의 비적용 목록에 넣을 수 없다. 실제 실패를 재현한 주장으로 바꾸지 않았다. |
| F2 · R1 한도·호출 | R1 준비·검토·처분, Closeout과 이후 수정·재검증 모두 P4 12시간/전체 40시간 및 기존 증거 시도에 귀속했다. CLI를 쓴다면 reviewer·인증/billing·전달 범위·tools 여부·후속 라운드 포함 횟수·회당 시간은 같은 실행 승인에 명시한다. 정해진 승인 범위 안의 correction마다 새 승인을 만들지 않는다. |

F3–F6은 추가 환경을 실제 사용할 때의 통제·회수·반출·canary와 P4 준비 비용, 필수 거절 범주별 자체 관측 또는 unavailable, 통상 보존과 정지 후 2시간 여유의 구별, native 구성요소 측정에 근거한 첫 full budget과 시도 사이 재산정, 원 ticket worker 재개 성공/non-pass/pending 기대값으로 좁혔다. 물리 장비 보유나 첫 full 전 별도 full 실측을 새 gate로 만들지 않았다.

40시간·회당 120분은 기존 실행 승인용 예비 상한으로 유지한다. DR-0007 v0.10·B안·공통 조건 중심 worker 지원, published/refetched equality를 포함한 A13 전체 qualification과 별도 activation, live macOS Preview 이후 formal admission 경계는 그대로다. 이번 문안은 v0.4 재리뷰·계획 수락·실행 승인·결과 수락을 뜻하지 않는다.

### Document Verification And Retention

- v0.3은 56,070 bytes / SHA-256 `ba465032e0a4c8e5a2112157d90631eb28fcb0798b7cbfa72a249bf85315413a`, v0.4는 60,560 bytes / `d522f2c6039eb837c65917c198f0e868c163839f011248f51e92be85eebb2ffc`다. 23개 지정 치환과 Response Map 추가만 적용했다.
- v0.3→v0.4 diff는 30,353 bytes / `cd4c87fbe82ab2b164815a2c0d9227481647b9a771720e11c537caee3782bb7f`다. 정·역적용을 메모리에서 대조했고 R0-I03의 frozen packet에서도 v0.3 원문을 복원해 일치시켰다. 수락 DR의 SHA-256 `e7679a8e11b5e38171888ab6da748cabd6ad5e46dc84e48205733a8e0e6d9ede`는 불변이다.
- GFM 렌더링·로컬 링크/anchor·신규 문안의 emphasis/whitespace/disclosure, 비변경 입력 267개, 과거 리뷰 15개 원문·R0-I03 입력 8개, 기존 기록 prefix와 Git HEAD/status/tracked diff를 확인했다. 과거 CHORE의 외부 명칭 2건은 역사적 prefix와 함께 보존된 publication 준비 항목이며 이번 신규 유입이 아니다.
- 입력 식별과 diff 2개는 v0.4 검토·실행 입력 비교 및 v0.3 복구 소비자에 필요해 기존 durable task 경로에 보존한다. 후속 입력이 고정되면 다시 판단한다. 별도 작성 helper·임시 결과 파일은 만들지 않아 이번 정리 대상은 없다. 기존 source worktree·계약/probe/review 근거·마지막 VM recovery는 후속 구현/실측 비교/복구 소비자가 남아 유지하며 활성 경로를 바꾸지 않았다.

추가 실험·제품 코드/tests/runner 변경·제품 test·VM·reviewer 호출·Git action은 수행하지 않았다. 다음 판단 대상은 v0.4 반영 내용과 한 번의 bounded 실행 승인 범위다. 이 준비 기록은 기존 CHORE에만 두며 새 task/STATUS나 별도 진행 정본을 만들지 않는다.

## R0-I04 — Implementation Plan v0.4 Re-review And Driver Judgment — 2026-10-18

Owner는 “후속 구현·검증 계획 v0.4를 Claude CLI로 R0 재리뷰해줘. R0-I03 지적과 네 처분의 반영 여부, R1 이후 한도와 reviewer 호출 경계, 실행 승인 검토 준비도를 확인하고 네 판단도 정리해줘. DR-0007 v0.10과 B안, 공통 조건 중심 worker 지원은 유지하고 추가 실험이나 제품 구현은 시작하지 마.”라고 요청했다. 이번 범위는 고정 계획의 Claude CLI 정적 R0-I04 한 회와 Driver 대조·기록이다. 계획·계약 수정, 추가 실험·제품/tests/runner 구현, VM 실행과 Git action은 포함하지 않는다.

### Verdict And Driver Assessment

Reviewer 판정은 approve다. R0-I03-F1–F6은 모두 resolved이며, 이전 지적 반영·계약 정합성·R1 이후 한도·reviewer 호출 경계·실행 승인 검토 준비도 모두 approve다. 승인 전 필수 수정은 없고 P3 선택 의견 두 건만 남았다.

Driver도 [계획 v0.4](windows-native-implementation-plan.md)를 추가 문안 수정 없이 bounded 실행 승인 검토로 넘길 수 있다고 본다. 양 OS 필수 사례의 비적용 제외 금지와 R1/Closeout 이후 한도 귀속은 본문에서 집행 가능하게 닫혔다. 실행 승인 때 실제 사용할 환경·호출·권한·한도를 한 번 명시하면 되며, 그 안의 입력 구체화와 ordinary correction마다 작은 승인을 추가할 이유는 없다. 40시간·회당 120분을 채택하는 결정은 아직 남아 있고, 이 리뷰는 해당 시간 안의 완료를 보장하지 않는다.

현재 v0.4를 그대로 승인 검토에 넘기기 위한 추가 R0는 필요하지 않다는 판단이다. 다만 Reviewer의 “한 문장 보완이면 문서 검증으로 충분” 또는 재리뷰 필요 상황의 열거를 Source Workflow의 R0/R1 적용 범위를 면제하는 일반 규칙으로 채택하지 않는다. 현재 계획 안의 실행 입력 선택과 실제 계획/계약 변경을 구별하고, 이후 변경에는 기존 review·Owner 권한 경계를 적용한다.

### Invocation And Exact Inputs

- 공통 review procedure와 workflow-cross-review의 기록 경계를 적용했다. Owner가 직접 CLI 호출을 요청했으며 새 reviewer 세션 1회에 고정 packet만 전달했다. CLI 2.1.302, `claude.ai / firstParty / pro` 인증을 scoped Keychain 조회로 확인했고 provider/OAuth override는 없었다. account email·비밀값은 출력·저장하지 않았다.
- 실제 model `claude-opus-5-5`, session `9904cd24-d3f9-4708-aeb0-cd5b392cffd1`. model override 없이 no-tools·strict empty MCP·세션 비보존으로 실행했다. 1,200초 상한 내 163.139초, exit 0, tool event 0, 입력 8개 전후 drift false였다.
- 계획 v0.4: 60,560 bytes / SHA-256 `d522f2c6039eb837c65917c198f0e868c163839f011248f51e92be85eebb2ffc`. 수락 metadata 포함 DR: 181,284 bytes / `e7679a8e11b5e38171888ab6da748cabd6ad5e46dc84e48205733a8e0e6d9ede`.
- source baseline `a93f71c359c4f0a9d57fcfb50d5999160e870f77`, tracked diff SHA-256 `fd2677e7a3e737d72036d694a5b223304cf53645883c4c2e0aefb6a6bcdb2058`; 그 밖의 untracked 입력은 manifest에 별도 식별했다.
- packet: 370,004 bytes / `2e0bc62c1da5897f14c51a7ba854ba18d5f93de47daab7790894b51af7f18331`; request: 7,294 bytes / `47f61b5a916d6204b4034eda0592ed2fc93a2eaa96159653775812363a63a407`.
- final: 18,254 bytes / `2bdc872f914557356ba70b65706b653b38ace7c94612d76df26fdee0736b124e`. streamed partial과 bytes가 일치했다.

Packet은 계획·DR·Maintaining·Source Workflow 전문, admission/Decision Guide 관련 절, 이 CHORE의 R0-I03 원문/처분과 v0.4 작성 기록(당시 3781–4107행), v0.3→v0.4 diff의 8개 입력이다. 이전 리뷰 전문은 R0-I03 한 회이며 그 안의 이전 라운드 요약을 여러 리뷰 전문 제공으로 부르지 않는다. 제품 source/tests/runner·원 probe 출력·DR-0002 본문·외부 API 본문은 제공하지 않았다. fresh session이어도 이전 결론을 함께 받은 반영 재리뷰이므로 blind/완전 독립 검증이 아니다.

### Finding Dispositions

두 finding은 모두 P3 선택 의견이며 현재 계획의 실행 승인 검토를 막지 않는다. 아래는 Driver의 실행 입력/후속 문안에 대한 판단이다. 이번 요청에서는 계획을 수정하지 않는다.

| Finding | Driver 처분 | 판단과 좁힌 반영 범위 |
| --- | --- | --- |
| R0-I04-F1 · platform 비적용과 window 의미 | revise | P1의 실제 ID·비적용 목록에서 Windows 관련 test라는 이유만으로 macOS 사례를 통째로 제외하지 않는 취지는 채택한다. V1의 wrong-OS mutation 거절과 제공되는 read/diagnostic 경로의 기대 결과·무쓰기를 platform 메커니즘과 구별한다. 다만 비적용을 Win32/NTFS 두 종류에만 한정하거나 모든 macOS 경로에서 windows-1 read 성공·교차 OS 지원을 새로 보장하지 않는다. 수락된 읽기 계약에 따라 성공 또는 정확한 진단/non-pass를 판단한다. 이는 기존 V1·shared 회귀·필수 사례 제외 금지를 실행 입력에 적용하는 일이다. |
| R0-I04-F2 · reviewer/agent 호출 입력 | revise | agent fresh-reader를 실제 선택할 때 호출 횟수·회당 시간과 범위를 실행 승인에 명시하는 취지, tools 실행을 허용하면 Source Workflow의 명령·인자·runtime·cwd·timeout·출력/쓰기·network/credential 경계를 함께 고정하는 취지를 채택한다. fresh-reader는 이미 P3 문서/reader와 P3 4시간에 배정되어 있으며, P4/R1 이후 재수행은 기존 P4 한도를 따른다. relay 대기는 해당 작업과 child 실행이 모두 멈춘 경우에만 제외하고 packet 준비·처분은 경로와 무관하게 포함한다. 이후 별도 명시 승인도 가능하므로 “같은 실행 승인”을 영구 금지로 읽지 않는다. 매 라운드 재승인·외부 human reviewer 시간의 별도 계측 제도를 새로 만들지 않는다. |

F2의 “단계 귀속이 적혀 있지 않음”은 계획 57/150/193행의 P3 배정을 함께 보면 실제 누락으로 보지 않는다. 200행의 R1 규칙은 tool 허용 여부 하나만으로 실행 권한을 완결하지 않으며, 연결된 Source Workflow 108행의 정확한 실행 경계가 계속 적용된다. 현재 R0 호출 승인은 미래 R1·fresh-reader의 호출을 허용하지 않는다.

### Driver Cross-Checks And Limits

- 계획 73/75행과 DR A3 600행은 양 OS import-safe·사전 비적용을 허용하면서 각 OS의 필수 native 사례와 macOS 성공 mode-change 기대를 보존한다. 계획 114/136/148행의 wrong-OS·worker 재개·실제 ID 대응도 유지한다.
- 계획 194–204행은 R1 준비·검토·처분·Closeout 및 이후 수정/재검증을 P4 12시간/전체 40시간과 기존 증거 시도에 귀속한다. 회당·횟수·단계·전체 중 먼저 닿은 한도가 우선이며, 정지 후 2시간 여유를 구현 연장에 쓸 수 없다. 두 OS×두 mode의 첫 full만 각 120분을 쓰면 8시간이다. 남은 P4 시간에 collection/focused·R1·보정이 함께 들어가므로 모든 재시도 슬롯이나 완료를 보장하지 않는다. 이는 자동 증액 사유가 아니다.
- 계획 159/237/241행은 필수 거절 범주의 자체 관측과 실행/상속/미해결 결과를 구별한다. 실제 선택한 candidate의 필수 관측이 없으면 qualification/activation은 미완료다. 그러나 Reviewer의 “fixture·추가 환경 미확보”라는 요약을 x64/물리 환경 부재 자체가 대표 UTM qualification을 막는 새 gate로 읽지 않는다. DR A6 644행과 계획 227행의 B 배정에 따라 미관측 tuple을 남긴다.
- DR A9 710행의 readable window와 A10 787행의 실제 mutation OS gate·읽기 진단은 서로 다른 의무다. F1은 이 구별을 사례 대응에 적용하되 cross-OS rollback이나 모든 reader 성공을 새 지원으로 넣지 않는다.
- DR A2 582행·S6 384–386행과 계획 127/136행은 원 ticket의 exact 재개 성공 또는 stable non-pass, 다른 writer의 pending barrier, whole-result와 기존 guard를 유지한다.
- 계획 243/244/246행과 DR A13 841–851행은 published/refetched equality를 포함한 전체 qualification, 별도 Owner activation, criterion 10과 live macOS Preview 이후 formal admission을 구별한다. anonymous evidence의 수집 시점을 activation 뒤로 강제하지 않는다.
- old-writer 거절 미확인 또는 발행은 영향을 받는 검증·qualification을 멈추게 한다. 모든 구현 실패가 곧 계약 amendment를 요구하는 것은 아니다. 승인 범위의 결함 보정은 기존 한도에서 다루고, 의미·지원·신뢰 경계 변경이 필요한 경우에만 해당 계약 결정으로 돌아간다.

이 확인은 현재 문서의 정적 대조다. 실제 source의 Windows import 실패나 Win32 API 동작, native runner·환경·fixture 가용성을 새로 실행/재현한 증거가 아니다.

### Next Boundary

권고는 v0.4를 유지하고 한 번의 bounded 실행 승인에 사용할 입력을 구체화하는 것이다. 구현 task/단일 기록, 제안 시간·시도 한도의 채택 여부, 실제 사용할 환경·회수/반출 범위, R1 방식·호출 한도와 fresh-reader 수행 방식을 정한다. 추가 권한·반입이 실제로 필요한 항목만 구별하고, 승인된 경계 안의 가용성·ID·budget 구체화는 P0–P3에 남긴다. Reviewer의 열거 항목 각각을 별도 approval gate로 만들지 않는다.

계획 v0.4의 “not re-reviewed” 표기는 frozen 입력에 보존하고, 이번 재리뷰 결과는 이 dated 기록으로 설명한다. 계획·DR·제품은 변경하지 않았으며 추가 실험·제품 test·VM·후속 reviewer·Git action도 수행하지 않았다. approve는 계획의 정적 준비도 판정이며 Owner의 실행 승인·개발 결과 수락을 대신하지 않는다.

### Reviewer Response Verbatim

````markdown
# R0-I04 — Windows Native Implementation And Verification Plan v0.4 정적 재리뷰

## 0. 범위와 한계

**읽은 자료**
- 대상: 계획 v0.4 (60,560 bytes, `d522f2c6…2ebffc`)
- 대조 자료:
  - DR-0007 수락 metadata 포함본 (`e7679a8e…`) 전문
  - Maintaining·Workflow 전문
  - Windows Admission·Decision Guide 해당 절
  - CHORE의 R0-I03 원문·Driver 처분·v0.4 작성 기록 (3781–4107행)
  - v0.3→v0.4 exact diff

**수행하지 않은 것**
- hash와 byte 수는 packet 값을 인용했을 뿐 재계산하지 않았다.
- tool 실행, 파일 접근, 실험, 제품 test, VM 실행을 하지 않았다.
- 아래 판단은 모두 문안 대조와 의견이다. 실행이나 재현 결과가 아니다.

**packet 밖이라 확인하지 못한 것**
- 제품 source/tests/runner의 현재 상태: `fcntl` import, chmod 기대, sync 호출 지점
- DR-0002의 11-document 집합
- Microsoft API 문서 본문

이 항목들은 Driver의 정적 주장으로만 다뤘다.

**독립성 한계**
- 단일 fresh session이다.
- R0-I03 결론과 Driver 처분을 함께 받았으므로 anchoring 가능성이 있다.
- blind 검증이나 완전 독립 검증이 아니다.

---

## 1. Overall verdict: **approve**

R0-I03-F1·F2는 계획 본문에 집행 규칙으로 반영됐다. F3–F6은 필요한 설명 범위로 좁혀 반영됐다. 좁힌 반영이 계약 의무를 빠뜨리지 않았고, 물리 장비 보유나 첫 full 전 별도 full 실측 같은 새 gate도 만들지 않았다.

새로 찾은 사항 두 건은 모두 P3 선택 보완이다. 승인문에 넣거나 P1에서 실행 입력으로 고정하면 되며, 실행 승인 검토를 막지 않는다.

| 관점 | 판정 | 요지 |
| --- | --- | --- |
| 이전 지적 반영 | **approve** | F1–F6 모두 resolved. Response Map(L298–305)이 가리키는 위치에 실제 문안이 있음을 본문으로 확인했다 |
| 계약 정합성 | **approve** | 다음이 S1–S8/A1–A15와 일치하며, 실제 충돌은 찾지 못했다.<br>- B 배정과 공통 조건·기존 모든 guard 중심 worker 지원<br>- whole-result, A13 전체 qualification(source/artifact/published/refetched)<br>- 별도 Owner activation, criterion 10, live macOS Preview 이후 formal admission |
| R1 이후 한도 | **approve** | 다음이 모두 서로 모순 없이 닫혔다.<br>- R1 준비·검토·처분, Closeout, 이후 수정·재검증의 P4/전체 귀속<br>- 기존 증거 시도의 연속 계수<br>- 먼저 닿는 한도 적용<br>- 2시간 여유의 정지 후 전용<br>- 재분류에 의한 초기화 금지 |
| reviewer 호출 경계 | **approve** (선택 보완 R0-I04-F2) | 다음이 성립한다.<br>- 일반 구현 승인, Owner relay, 명시 승인된 CLI의 구별<br>- 값이 없으면 호출하지 않음<br>- 후속 라운드는 재승인 없이 매회 입력·drift 확인<br>- 이전 R0 승인은 미래 R1/fresh-reader 승인이 아님<br>tool 사용 reviewer와 fresh-reader agent의 대칭성은 보완하면 좋다 |
| 실행 승인 검토 준비도 | **approve** | 승인 전 필수 문안 수정은 없다. 실행 승인에서 정할 범위와 한도는 §4에 정리했다 |

---

## 2. R0-I03-F1–F6 반영 표

| 지적 | 판정 | v0.4 근거 line | 핵심 근거 |
| --- | --- | --- | --- |
| **F1** 양방향 비적용·import-safe | **resolved** | L73, L75 | 아래 별도 설명 참조 |
| **F2** R1/Closeout 이후 한도와 호출 경계 | **resolved** | L194, L195, L198, L200, L202 | 아래 별도 설명 참조 |
| **F3** 추가 환경 실행 경계 | **resolved** | L227 (L168/L172/L180 연계) | 추가 환경을 "실제 사용할 때만" 다음을 고정한다.<br>- 통제·회수 가능한 입력·증거 반출·canary·시간 귀속<br>- P4에서 추가로 준비하면 P4 시간에 포함<br>물리 장비에 VM snapshot을 요구하지 않고 실제 환경에 맞는 복구·격리 경계를 확인한다. "새 장비 확보 자체를 gate로 만들지 않는다." A6 L644, S1 L235와 일치한다. 어느 추가 환경을 범위에 넣는지는 L26의 "경계를 넓히는 것은 별도 범위 결정"에 따라 승인 입력이 된다(§4) |
| **F4** 거절 범주 비대체·잔여 표시 | **resolved** | L159, L164, L237, L241 | non-NTFS·remote·unknown 등 각 필수 범주는 "자체 관측 또는 unavailable로 개별 처분하며 서로 대체하지 않음"(L159). A13 L847의 열거와 맞는다.<br>개발 결과는 "필수 사례별 실제 실행·식별된 상속·미확보/미해결"(L241)로, Maintaining L60의 세 범주와 같다.<br>"개발 범위" 문구로 공백을 제외하지 않고 criterion 잔여로 제시한다(L237).<br>새 mount/share 생성은 여전히 의무가 아니다(L160, L164) |
| **F5** 보존 여유·첫 full budget | **resolved** | L186, L195, L204 | 아래 별도 설명 참조 |
| **F6** worker 재개 기대값 | **resolved** | L136 | 행 이름을 "거절·재개"로 바꾸고 기대값을 셋으로 나눴다.<br>- 지원 결과이고 원 조건·모든 guard가 유지되면 exact 재개 성공(lifecycle `--recover` 아님)<br>- 조건 불충족/unknown이면 stable non-pass<br>- 다른 writer는 pending barrier로 거절<br>S6 L384, A2 L580–582, Initial Support Limits L350·L354와 맞는다. prepare 뒤 drift로 인한 stale은 "조건 불충족"에 포함되어 L127의 원인 구별과도 모순이 없다 |

**F1 근거 상세**
- **L73:** "Windows의 POSIX 의존성과 macOS의 Windows 전용 의존성을 모두 import-safe하게 분리"한다. 아직 실패를 재현했다고 주장하지 않으며, 앞으로 추가할 test가 macOS에서 실패했다는 관측도 없다고 명시한다.
- **L75:** "같은 사전 비적용 규칙"을 양방향에 적용한다. 각 OS의 필수 사례를 그 OS의 비적용 목록에 넣거나 사후 재분류하는 것을 금지한다. "Windows 필수 native 관측과 macOS의 기존 성공 기대 모두 skip/N/A로 닫을 수 없다"고 쓴다.
- **세 결과의 구별:** 근거 있는 비적용, 예상 거절의 성공적 검증, unexpected skip/unknown/missing(non-pass)을 따로 둔다.
- **계약 정합성:** A3 L600의 macOS 성공 mode-change 유지와 "skip을 pass로 바꾸지 않음"에 맞는다.
- **잔여:** 해석 여지가 조금 남는다(R0-I04-F1, 선택).

**F2 근거 상세**
- **L194:** P4 활동에 R1 준비·검토·Driver 처분, R1 이후 보정·재검증, closeout을 포함한다.
- **L198:** "Closeout/R1 처분 뒤 … 앞 단계로 돌아가도 수정·재검증 시간은 P4에 포함하고 기존 증거 시도를 이어 센다." 또 "Closeout이 별도 예산을 만들지 않는다."
- **L200:**
  - "일반 구현 승인만으로 reviewer 호출이 허용되지는 않는다"
  - CLI를 쓰면 reviewer, 인증/billing, 전달 범위, no-tools 여부, 후속 라운드 포함 횟수, 회당 시간을 "같은 실행 승인에 명시"하고, "정해지지 않으면 호출하지 않는다"
  - 후속 라운드는 재승인하지 않되 매회 exact 입력·disclosure·인증과 drift를 확인한다
  - "이전 R0 호출 승인은 미래 R1·fresh-reader 호출 승인이 아니다"
- **L202:** 한도 안의 ordinary correction마다 새 승인을 요구하지 않는다.
- **Workflow와의 정합성:** L64, L108과 충돌하지 않는다. 자원 증액도 자동으로 요구하지 않는다(L198 "모든 허용 재시도 슬롯을 반드시 사용할 수 있다는 뜻은 아니다").

**F5 근거 상세**
- **L195:** 2시간 여유는 "정지 조건이나 한도 도달 후" 회수·보존·복구 판단 전용이다. "통상 보존은 각 단계 시간에 포함"하고, 이 여유로 연장하거나 재개하지 않는다.
- **L204, 첫 full budget:** "native 구성요소 실측에 근거한 추정이며 첫 full 전에 별도 full 실측을 요구하지 않는다."
- **L204, 시도 사이 재산정:** 원 실패와 새 근거를 기록하고, 120분 ceiling·P4/전체 잔여·기존 시도 한도를 모두 지킨다. "timeout만으로 자동 증액" 하거나 시험 도중 상향하는 것은 금지한다.
- **Maintaining L67과의 관계:** "measured duration"을 구성요소 측정으로 읽는 해석은 Driver 판단이다. 이 해석은 L204에 명시되어 있고 새 gate를 만들지 않는다.

---

## 3. 새·잔여 finding

승인 전 필수(must-fix) finding은 **없다.** 아래 두 건은 모두 P3 선택 보완이다.

### R0-I04-F1 · P3 · 선택 (P1 비적용 목록 고정 시 입력) — macOS에서의 "Windows 전용 메커니즘"과 "windows-1 window 의미"의 경계

**근거 (확인된 문안)**
- L75는 macOS 쪽 비적용 대상을 "macOS에서의 Windows 전용 메커니즘"으로 정의한다.
- A10 L787은 "other operating systems are not admitted for Windows-1 mutation. Verify actual conditions"라고 하고, 읽기 진단은 허용한다.
- 계획 V1(L114)과 runtime 거절 fixture(L162)는 "wrong OS/OS·process 불일치 거절"을 요구한다.
- A9 L710은 windows-1을 admitted readable window로 추가하며, 이는 shared reader 경로 변경이다.

**오해 경로 (의견)**
P1에서 macOS 비적용 목록을 "windows-1 관련 test 전체"로 넓게 잡을 수 있다. 그러면 두 가지가 동시에 사라진다.
1. macOS에서 windows-1 candidate나 target의 mutation을 거절하는지에 대한 native 관측이다. 이는 "다른 OS" 거절을 가장 직접 관측할 수 있는 경로다.
2. shared reader가 macOS에서 windows-1 기록을 읽거나 진단하는 동작에 대한 확인이다.

이 경우 V1의 wrong-OS 거절이 mock 증거나 POSIX 호환 runtime 사례 하나로만 남을 수 있다. L75의 "메커니즘"이라는 단어는 Win32 API·NTFS 관측만을 가리키도록 읽히므로 문언상 위반은 아니다. 그러나 목록 작성자에 따라 해석이 갈릴 수 있다.

**최소 수정 (선택)**
L75에 다음 취지의 한 구절을 둔다.
- 비적용은 Win32/NTFS 관측 메커니즘에 한정한다.
- macOS에서 windows-1 mutation을 거절하는 사례와 읽기 진단 사례는 macOS 적용 대상(예상 거절의 성공적 검증)이다.

문안을 고치지 않는다면 P1의 사전 비적용 목록 고정 때 이 구분을 적용하면 된다. 새 registry나 새 사례 gate는 필요 없다.

**참고 (finding 아님)**
기존 chmod→100755 성공 test는 Windows에서 "POSIX 메커니즘 N/A"로만 닫힐 위험이 있다. 그러나 이는 L136의 mode-changing 필수 거절 사례와 L75의 "각 OS 필수 사례 제외 금지"로 이미 막혀 있다.

### R0-I04-F2 · P3 · 선택 (실행 승인 입력) — reviewer/agent 호출 경계의 대칭성

**근거 (확인된 문안)**
- L200은 R1 CLI에 대해서는 횟수·회당 시간과 "값 미정이면 호출하지 않음"을 둔다. 실행 조건으로는 "no-tools 여부"만 열거한다.
- Workflow L108은 실행을 허용하면 "commands, arguments, runtime, working directory, timeout and output/write boundary"를 고정하고, 불필요한 network와 credential을 거부하도록 요구한다.
- L150의 fresh-reader agent는 인증/billing·disclosure 확인과 "새 호출 권한 없음"만 둔다. 횟수·시간 상한, 값 미정 시 불호출, 시간 귀속 단계는 적혀 있지 않다.
- L186은 "작업과 child 실행이 모두 멈춘 대기"를 시간 계산에서 제외한다.

**실패·오해 경로 (의견)**
- **(a) tool 사용 reviewer:** 승인문이 "R1 CLI, tools 허용"만 적고 Workflow L108의 실행 경계를 빠뜨릴 수 있다. Workflow가 상위 authority이므로 계약 충돌은 아니다. 다만 계획만 읽은 승인자가 경계 고정을 놓칠 수 있다.
- **(b) fresh-reader agent:** 승인이 "agent fresh-reader 허용"만 적으면 호출 횟수에 명시 상한이 없다. 단계 시간이 상한 역할을 하므로 위험은 작다. 그래도 R1과 비대칭이고, 어느 단계(P3 또는 P4) 시간에 귀속되는지도 문안에 없다.
- **(c) 시간 계산:** Owner relay R1에서 외부 reviewer가 검토하는 시간은 L186에 따라 대기로 제외되는 것이 자연스럽다. CLI 실행 구간은 포함된다. 모순은 아니지만 L194의 "검토"가 경로마다 다르게 집계된다는 점을 ledger 해석에서 알아두면 좋다.
- **(d) 승인 시점:** "같은 실행 승인에 명시"를 엄격히 읽으면, 나중에 Owner가 별도로 명시 승인하는 CLI 호출도 막힌다. Owner의 명시 결정이 우선하므로 실해는 작다.

**최소 수정 (선택)**
L200 또는 L150에 다음 취지의 한 문장을 둔다.
- fresh-reader agent에도 R1 CLI와 같은 규칙을 적용한다(횟수·회당 시간 명시, 값 미정이면 호출하지 않음, 귀속 단계 시간 안에서 진행).
- tools나 실행을 허용하는 reviewer/agent는 Workflow L108의 명령·인자·runtime·cwd·timeout·출력/쓰기 경계와 network/credential 거부를 함께 고정한다.
- 원하면 "또는 이후 별도의 명시 승인"을 덧붙인다.

문안을 고치지 않는다면 실행 승인문에 위 값을 적으면 된다. ordinary correction이나 라운드마다 재승인을 요구하는 처방은 아니다.

---

## 4. 실행 승인 검토로 넘길 수 있는 범위, 남은 선택·전제, residual risk

### 넘길 수 있는 범위 (정적 의견)

v0.4는 추가 문안 수정 없이 하나의 bounded 실행 승인 검토 대상으로 넘길 수 있다고 판단한다. 대상 범위는 다음과 같다.
- P0 통제 canary와 입력 고정
- P1–P3 구현·개발 반복·freeze
- P4 대표 UTM 전체 검증과 macOS focused·full 회귀
- 범위에 넣을 경우 x64/물리 focused 보완
- R1과 처분, 개발 결과 closeout

이 판단은 계획 문안의 준비도에 대한 의견이다. 제품 실행 PASS, Owner 승인, Git·publication·activation·adopter 권한을 뜻하지 않는다.

### 승인 전 필수 문안·결정

없음.

### 한 번의 실행 승인에 명시할 범위·한도·권한

1. **예비 상한:** 단계 2/8/12/4/12/2시간, 전체 40시간, 회당 한도(canary 10분, collection 10분, focused 20분, full 120분)와 시도 계수를 그대로 채택할지 조정할지 정한다. 이 값들은 측정값이나 소요 예측이 아니다.
2. **R1 방식:**
   - Owner relay로 할지 CLI로 할지 정한다.
   - CLI라면 reviewer, 인증/billing, 전달 범위, tools 여부, 후속 라운드 포함 횟수, 회당 시간을 정한다.
   - tools를 허용하면 Workflow L108 실행 경계를 함께 고정한다(F2).
   - **값을 아직 정하지 않았다는 것은 허점이 아니다.** L200에 따라 그 상태에서는 호출하지 않는다.
3. **fresh-reader:** 수행자(human 또는 agent), 전달 범위, agent라면 횟수와 시간을 정한다(L150, F2).
4. **추가 환경:** x64나 물리 환경을 이번 범위에 넣을지, 미관측으로 둘지 정한다. 넣는다면 Owner가 제공하는 환경과 그 권한 범위를 명시한다(L227, A6 L640).
5. **반입·권한:** 다음 각 항목을 범위에 넣을지, 미완료로 남길지 정한다.
   - runtime 거절 fixture 반입(exact package·방법·network, L164)
   - non-NTFS/remote fixture에 필요한 관리자 권한·host disk/share
   - tokenizer 설치나 network(L150)
6. **반출 수단:** "실행 종료 후 잠시 쓰는 전달 경로"(L172)를 허용할지 정한다.
7. **진행 기록:** 구현 task ID와 단일 진행 기록을 지정한다(L28, Workflow L48/L52).
8. **별도 확인 대상:** local commit을 포함한 Git action은 계속 별도 확인 대상임을 재확인한다(L26).

### 승인된 경계 안에서 P0–P3가 구체화할 실제 입력 (권한 확대 아님)

- **P0:**
  - exact tuple, VM/recovery identity, restore 실측
  - old writer exact bytes × 접근 경로 × family 표
  - Windows/macOS runner·policy·canary 결과
  - 반출 수단의 합성 파일 확인
  - 상한 이하의 단계 budget과 증거 묶음 목록
  - fixture·runtime·tokenizer 가용성
- **P1:**
  - operation × phase flush 대응표
  - 실제 discovery ID와 V1–V12 대응
  - 양방향 사전 비적용 목록(F1의 구분 적용)
  - prepared source 기대 변경 목록과 첫 init candidate
- **P2:** 새 사례 ID 대응, P/Q identity
- **P3:** 최종 P/Q 역할 기록, tokenizer 측정, fresh-reader 입력, 첫 full budget 산정 근거

### residual risk (실행 중 위험)

- **P4 압박이 커졌다:**
  - 이제 R1과 R1 이후 보정까지 P4 12시간에 들어간다.
  - full suite 첫 시도만으로도 두 OS × 두 mode × 120분이면 최대 8시간이 든다.
  - 두 번째 full 슬롯을 이미 썼거나 P4 잔여가 부족한 상태에서 R1이 source 결함을 지적하면, 계획대로 정지하고 조정 결정을 해야 한다.
  - 다만 Maintaining의 reuse 판단으로 focused 재검증만으로 충분할 수도 있다(L225).
  - 이는 의도된 동작이며 증액 요구 근거가 아니다. 승인자가 미리 알아야 할 성질이다.
- **old-writer 거절:** 노출된 old writer의 거절이 성립하지 않으면 qualification/activation이 멈추고 amendment로 돌아갈 수 있다.
- **PS5.1 입력 보존:** 실패하면 미지원으로 남고, PowerShell 7은 별도 선택이 된다(S7).
- **fixture·추가 환경 미확보:** A13 qualification이 미완료로 남는다. 이는 계약에 맞는 결과이며, 미관측 tuple은 unobserved로 표시된다.
- **P/Q 호환 증거:** 두 fixture release와 관측된 record family에 한정된다(L67).
- **미확인 source 주장:** 제품 source의 현재 상태와 Win32 API 동작은 이 리뷰에서 확인하지 않았다.

### 추가 문안 재리뷰 필요 여부

필요 없다고 본다. F1·F2를 반영한다면 기존 의미를 좁게 명료화하는 한 문장 수준이다. Driver의 문서 검증과 diff 기록으로 충분하며, 의미를 넓히지 않는 한 새 R0 라운드는 불필요하다. 별도 재리뷰가 필요한 경우는 다음뿐이다.
- 실행 승인문이 계획의 한도나 경계를 넓히는 경우
- 수락 계약의 의미를 건드리는 경우

이 경우의 재리뷰 여부도 Owner가 판단할 몫이다.
````

### Verification And Retention

GFM 렌더링 7문서·로컬 link/anchor 202개, 신규 문안의 emphasis·whitespace·disclosure, 비변경 입력 270개, 과거 리뷰 16개 원문, frozen 입력 8개와 CLI 결과 metadata를 확인했다. 기존 두 기록의 prefix·계획/DR bytes·Git HEAD/status/tracked diff는 그대로이며 diff-check도 통과했다. 과거 CHORE의 외부 명칭 2건은 보존된 역사적 publication 준비 항목으로 구별했고 신규 유입은 없다. 제품 검증을 실행한 결과는 아니다.

필수 request/packet/입력 manifest/final/metadata/runner 6개는 이번 처분과 v0.4 실행 입력 비교를 위해 durable task 경로에 보존하며, 후속 입력이 고정되면 다시 판단한다. final과 동일한 partial·빈 stderr 2개 및 빈 tool-temp 디렉터리 1개는 CLI 종료·열린 파일 없음·원문 보존 확인 뒤 삭제했다. 별도 검사 helper나 QA 결과 파일은 만들지 않았다.

기존 계획 입력/diff·계약/리뷰/probe 근거·source worktree와 마지막 VM recovery는 후속 구현·정확한 비교·복구 소비자가 남아 유지한다. 활성 경로 변경·worktree/branch/VM 정리는 하지 않았다. 다음은 현 계획의 bounded 실행 승인 범위를 구체화하는 판단이며, 이 기록 자체는 실행을 시작하지 않는다.

## Execution Approval Proposal v0.1 — 2026-10-18

### Owner Request And Scope

Owner 요청: “R0-I04와 네 판단을 반영해 v0.4 기준 실행 승인안을 구체화해줘. 실제 사용할 환경, R1·fresh-reader 호출 방식과 횟수·시간, 단계별 한도와 중단 조건을 한 번에 승인할 수 있게 정리해. DR-0007 v0.10과 B안, 공통 조건 중심 worker 지원은 유지하고 실제 실행은 아직 시작하지 마.”

이 요청에 따라 [Execution Approval Proposal v0.1](windows-native-execution-approval.md)을 작성했다. v0.4와 수락된 DR v0.10의 bytes는 바꾸지 않았다. R0-I04의 optional 두 항목은 실행 입력의 선택과 해석 범위를 구체화하는 데 반영했다. 이 작성 기록은 실행 승인, 제품 구현, 추가 R0/R1 또는 개발 결과 수락이 아니다.

### Concrete Proposal

- 실제 실행은 기존 ARM64 Windows UTM·전용 standard account·native CPython 3.14.7·PowerShell 5.1·local NTFS와 현재 macOS ARM64·pyenv CPython 3.14.7을 사용하도록 제안했다. x64·물리 장비는 미관측으로 남기며 B의 focused 후속 배정을 바꾸지 않는다.
- R1은 host Claude CLI의 기존 구독 인증 경로, tools 없는 fresh context, 필요한 source/test/runner/doc·계약·합성 결과 packet으로 총 3회·회당 20분을 제안했다. 준비부터 이후 보정·재검증까지 P4에 포함한다.
- Fresh-reader는 같은 CLI의 별도 no-tools context로 총 4회·회당 10분, 최대 2개 exercise다. Driver가 고정한 합성 target·명령 범위에서 실제 실행하고 결과를 검증한다. 초기 작업은 P3, P4/R1 이후 재수행은 P4에 포함하며 호출 수를 초기화하지 않는다. 문서에 긍정적으로 답한 것만으로 PASS를 만들지 않는다.
- v0.4의 단계 상한 2/8/12/4/12시간과 정지 후 회수·보존 전용 2시간, 전체 40시간을 유지했다. 회당·횟수·단계·전체 중 먼저 도달한 한도를 적용하며 여유 시간의 자동 이전이나 재분류 초기화는 허용하지 않는다.
- 현재 VM의 복구 입력·검증 clone, clipboard 차단·통제 전달, 새 1 GiB 이하 합성 VHDX의 NTFS/FAT32 volume, guest 내부 loopback SMB, 한정한 관리자 준비·회수, task venv의 tiktoken 0.13.0 wheel 준비를 같은 승인안에 명시했다. 아직 성공한 환경 준비로 주장하지 않으며 P0 2시간 안에서만 수행하도록 제안했다.
- macOS Windows 관련 사례의 일괄 N/A 처리를 허용하지 않고, 실제 wrong-OS 거절·제공되는 read/diagnostic 기대와 비적용 platform 메커니즘을 구별했다. 공통 worker 조건·원 ticket·whole-result·기존 guard와 old-writer barrier는 그대로다.
- Git/publication/adopter action, 계약 변경, 개발 결과 수락·activation·formal admission은 이 실행 승인 범위에 넣지 않았다. A13 전체 qualification·published/refetched equality와 live macOS Preview 이후 formal admission의 별도 판단도 유지했다.

### Exact Inputs And Current State

Source proposal v0.1: 24,865 bytes, SHA-256 `66a45c754e8208bb0b17c5298cbce29368668bd3c0516fc2671efd65d055dc66`.
Local Execution Bindings v0.1: 10,153 bytes, SHA-256 `e9602a17bd6c5fc164283f065c62c60ac98fa5b5321405b1f83ef1d71e70c273`. 실제 local 경로·VM·runtime은 Owner가 보관하는 해당 문서와 입력 manifest에만 둔다.

현재 계약/계획은 각각 DR `e7679a8e11b5e38171888ab6da748cabd6ad5e46dc84e48205733a8e0e6d9ede`, plan `d522f2c6039eb837c65917c198f0e868c163839f011248f51e92be85eebb2ffc`로 유지했다. source base·기존 tracked diff와 제품 파일도 유지했다. 실행 record ID는 배정하지 않았고 Development Index·STATUS를 수정하지 않았다.

읽기 전용 host 관측과 기존 guest evidence를 구별했다. 현재 VM은 stopped였고 저장 config의 clipboard 공유는 아직 true다. 새 runner·restore·filesystem fixture·tokenizer·제품 동작은 실행하지 않았다. 이전 probe의 guest tuple·권한·연결 결과는 과거 근거이며 P0 재확인 대상으로 남겼다. 외부 근거는 승인안의 Microsoft/PyPI 직접 링크에 연결하고 해당 guest 성공 증거로 바꾸지 않았다.

### Verification And Retention

문서 QA에서 GFM 렌더링·강조·local link, 신규 public-intent disclosure, 기존 계약/계획과 16개 review 원문·8개 R0-I04 frozen 입력, 이전 record prefix와 source Git 상태를 확인했다. 입력 manifest의 기존 276개 중 진행 record 2개 외 274개 입력은 동일했다. VM config와 host interpreter bytes도 동일했고 신규 implementation 경로는 존재하지 않았다. 제품 test·실험·reviewer 호출은 없었다.

이번 신규 보존 대상은 승인안, local bindings와 입력 manifest다. Owner의 exact 실행 승인 검토 및 승인 후 P0 입력 비교에 필요하며 해당 실행 기록이 인수할 때 소비자를 재평가한다. 별도 helper·QA 결과 파일을 만들지 않아 이번 단계에 새로 삭제할 임시 사본은 없다. 기존 worktree·계획 diff·review/probe 근거·마지막 VM recovery는 가까운 구현·비교·복구 용도로 유지하고 활성 경로를 바꾸지 않았다.

Owner execution decision: not recorded.

## R0-A01 — Execution Approval Proposal Review And Driver Judgment — 2026-10-18

### Owner Request And Scope

Owner 요청: “실행 승인안 v0.1과 Local Execution Bindings v0.1을 Claude CLI로 R0 리뷰해줘. 환경 준비·복구 경계, 호출·시간 한도와 중단 조건이 일관되고 실행 가능한지 확인하고 네 판단도 정리해줘. DR-0007 v0.10·B안·공통 조건 중심 worker 지원은 유지하고 제품 구현이나 추가 실험은 아직 시작하지 마.”

이번 범위는 두 v0.1 문서의 고정 입력을 검토하는 Claude CLI 정적 R0 한 회와 Driver 판단이다. 검토 대상 문서·v0.4·DR은 수정하지 않았고 제품 구현·추가 실험·VM 조작·후속 reviewer 호출을 수행하지 않았다.

### Verdict And Driver Assessment

Reviewer는 conditional, 필수 보정 2건(P1 1건·P2 1건), optional 4건으로 판정했다. 호출·시간·중단 한도와 DR/B/worker 보존은 정합하다고 판단했다. Driver도 실행 승인 전에 guest 제어/반복 전달 경계와 외부 packet용 비식별화 규칙을 명시해야 한다고 본다. 보정 범위는 이 두 운영 연결점이며 계약이나 v0.4 단계 계획을 다시 설계하는 일이 아니다.

F1의 “제어 채널이 문서에 없다”는 지적은 유효하지만, 실제 채널이 없거나 새 guest agent/저장 credential이 필요하다는 결론으로 확대하지 않는다. Driver가 보존된 이전 probe 기록을 대조하니 UTM console에 CUA click·개별 key 입력을 전달한 경로, 표준 비관리자 token의 실제 preflight, guest-local runner의 Job Object 회수가 기록되어 있었다. 이는 과거 관측이다. clipboard off 조건에서의 현재 동작은 P0에서 확인해야 하며 새 PASS로 간주하지 않는다.

“한 번의 승인”은 40시간 무인 실행을 약속하지 않는다. Owner의 부팅 로그인/UAC 입력 의존성은 이미 있었고, 반복 횟수와 시간을 줄이기 위해 candidate/batch 단위의 전달과 실행을 묶어야 한다. 이를 승인 문안에 보이게 하는 것이 F1의 핵심이다.

### Invocation And Exact Inputs

- Claude CLI 2.1.302, 기존 `claude.ai / firstParty / pro` 인증 경로, provider/OAuth override 없음. sandbox 조회의 미인증 결과 뒤 scoped Keychain 조회로 실제 경로를 확인했다. email·비밀값은 출력·기록하지 않았다.
- 실제 model `claude-opus-5-5`, session `0abb7e7f-ae42-4a77-8875-bbc6ca4872b1`. fresh session·safe-mode·no-tools·strict empty MCP·세션 비보존, 1,200초 상한에서 312.828초, exit 0, tool event 0, 고정 입력 10개 전후 drift false.
- 승인안 v0.1: 24,865 bytes / SHA-256 `66a45c754e8208bb0b17c5298cbce29368668bd3c0516fc2671efd65d055dc66`. Local Execution Bindings v0.1: 10,153 bytes / `e9602a17bd6c5fc164283f065c62c60ac98fa5b5321405b1f83ef1d71e70c273`.
- plan v0.4: 60,560 bytes / `d522f2c6039eb837c65917c198f0e868c163839f011248f51e92be85eebb2ffc`. DR v0.10: 181,284 bytes / `e7679a8e11b5e38171888ab6da748cabd6ad5e46dc84e48205733a8e0e6d9ede`.
- source base `a93f71c359c4f0a9d57fcfb50d5999160e870f77`, 기존 tracked diff SHA-256 `fd2677e7a3e737d72036d694a5b223304cf53645883c4c2e0aefb6a6bcdb2058`. untracked 입력은 별도 manifest에 식별했다.
- packet: 365,023 bytes / `cd000c99e4c993ac3953e2c0d5a0d368e1f78cc59e9a0ff13c5641be35ff38b4`; request SHA-256 `53aefef95ecae581bcd79c19727a1cfe29b29c26dcbd4d75cbcd9c51ef73afc4`.
- final: 16,775 bytes / `690ae9242e2919f3e4aa8c732bcf59359795470e44fe142278c18074195827db`; partial과 bytes 동일.

Packet에는 두 대상 전문, 계획·DR·Maintaining·Source Workflow 전문, R0-I04 final 전문, 이 기록의 Driver 판단(4109–4166행), admission/Decision Guide 관련 절을 제공했다. Owner가 Local Execution Bindings 자체를 명시해 검토를 요청했으므로 이번 한 회에 해당 private 문서를 포함했다. 이는 미래 R1에 private 경로를 전송하는 포괄 승인이 아니다. 답변에서는 private 경로/계정/VM 식별값을 반복하지 않도록 요청했고 final에도 해당 식별값이 없음을 확인했다.

Reviewer는 raw probe·실제 제어 채널 기록·제품 source/tests/runner·외부 API 본문을 받지 않았다. Driver의 아래 역사적 대조는 리뷰 종료 후 추가 확인이며 Reviewer가 확인한 것처럼 합치지 않는다. 이전 R0 결론도 packet에 있었으므로 fresh session을 완전 독립 검증이라 부르지 않는다.

### Finding Dispositions

| Finding | 처분 | Driver 판단과 최소 후속 범위 |
| --- | --- | --- |
| F1 · P1 guest 제어/반복 transfer 의존성 | revise | 문서상 누락은 승인 전 명시할 필요가 있다. 보존 기록에는 기존 UTM console의 CUA 개별 key 입력, ordinary interactive standard token, guest-local runner/Job Object 회수가 있다. 기존 console·관리 경로와 차단할 파일/clipboard/network 경로를 구분해 binding하고, Owner 로그인/UAC 입력·batch 전달·같은 VHDX 재-attach 범위를 명시한다. 새로운 guest agent·remote shell·저장 credential이나 표준 계정 승격을 제안하지 않는다. “실행 채널 부재”, “Owner가 모든 명령을 직접 입력해야 함”, “40시간 무인 실행 약속”은 현재 근거로 채택하지 않는다. |
| F2 · P2 실제 출력과 private 경로 전송 금지 | accept | private 원출력은 그대로 보존하고 외부 packet은 고정한 중립 경로 placeholder로 파생한다. 대응표·원본/파생 identity·치환 사실을 private 기록에 남기고, separator·case·공백/Unicode 등 검증 의미를 유지한다. 새 중립 fixture root로 이동하는 대안은 불필요하다. reviewer 출력의 임의 명령을 역치환해 실행하는 권한을 추가하지 않는다. 기존 target·allowlist·관측값 검사 뒤 실제 값에 대응시키는 절차만 허용한다. |
| O1 · canary 보정과 안전 정지 | defend | 합성 위치라는 이유만으로 실제 경계 위반을 일반 보정 실패로 낮추는 예외는 채택하지 않는다. 계획의 즉시 정지와 원인·필요 권한 판단을 유지한다. 기대한 거절을 관측한 성공, 측정/입력 오류, 실제 통제 위반을 구별하고 후자는 제품 실행 전이라도 자동 재개하지 않는다. 기존 재검증 1회가 안전 정지를 면제하지 않는다. |
| O2 · reader의 Driver 개입 | accept | P3 실행 입력에서 관측 ID/token·명시된 합성 응답·고정 경로 대응 외의 Driver 보완을 별도 기록한다. reader가 찾지 못한 명령/문서를 Driver가 대신 알아내야 진행된다면 reader 막힘/non-pass로 남긴다. 실제 완료·재개 관측과 제한된 합성 경험이라는 기존 기준을 유지하며 독립 사용자 성공으로 올리지 않는다. |
| O3 · Owner 문안에 FEAT/Index 재열거 | defend | 승인안 29행의 단일 실행 기록·이관 pointer·탐색 link와 문서 전체를 승인 대상으로 삼는 16/151행에 이미 포함되어 있다. 이를 반복하지 않은 것은 누락된 권한이나 실행 blocker가 아니다. 실제 시작일과 보존 history 확인 뒤 ID를 배정하는 기존 절차를 유지한다. |
| O4 · timeout/quota 후 재호출 | revise | 자동 재호출 금지·실패 호출 계산·기존 횟수/시간은 유지한다. 원인이 해소됐다는 근거와 남은 한도가 있을 때 이미 승인된 범위의 후속 호출을 판단할 수 있다는 뜻으로 한정한다. quota가 그대로인데 재호출하거나 provider/billing·전달 범위를 바꾸는 허용으로 읽지 않는다. |

### Bounded Correction Recommendation

아래는 적용하지 않은 보정 제안이다. 별도 승인안 버전이나 새 계획을 이 리뷰에서 만들지 않는다.

1. **Guest 제어·반복 운영:** “제품 실행은 전용 표준 계정의 UTM console에서 Driver가 CUA의 개별 key 입력으로 고정한 guest-local runner를 시작·관측하고, 그 runner가 child를 회수한다. 지정 VM의 화면·keyboard/mouse 및 정상 VM 관리는 허용된 제어 경로이며, 제품 실행 중 host 파일 공유·clipboard·외부 network·guest-agent exec는 허용하지 않는다. clipboard off·현재 token·통제 조건에서 이 경로가 성립하는지는 P0에서 확인한다. 반입/반출은 candidate/batch 단위로 묶고, 로그인/UAC 비밀 입력은 Owner가 한다. 재부팅 뒤 fixture가 필요한 batch에서 동일 identity의 VHDX만 재-attach하는 제한적 관리자 준비를 포함하며, token 복귀를 확인한다. 최초 환경 준비는 P0, 이후 승인된 반복 전달·동일 fixture 연결은 실제 수행 단계의 시간에 포함하고 모든 기존 상한을 유지한다.”
2. **외부 전달용 파생 출력:** “원출력은 private로 보존하고, reviewer/fresh-reader에는 고정 prefix 대응으로 비식별화한 파생 출력을 전달한다. 대응표와 원본/파생 identity를 보존하고 치환 사실을 명시한다. 경로 문법·검증상 특징·record ID·digest·결과를 임의로 바꾸지 않는다. 필요한 의미를 보존할 수 없는 경우에는 전달하지 않고 해당 관측 한계를 남긴다. Driver의 실제 실행은 기존 target/allowlist와 관측값 검사를 통과한 명령에 한정한다.”

같은 F1의 환경 문안에서 “개인 profile 비접근/비복사”는 guest에서 개별 자료를 열람·수집하거나 실행 namespace로 반입하지 않는 경계와, 이미 제안한 전체 VM package의 local recovery 보존을 구별해 적는 것이 정확하다. 전체 VM 복구본에 원 profile의 bytes가 포함될 수 있음을 숨기지 않으며, 이것을 개인 파일 열람·외부 packet 반출 권한으로 확대하지 않는다. 관리자 준비 shell도 고정 명령·profile script 미로딩 범위로 제시한다. 별도 제품 계약 변경이나 추가 실험 항목을 만드는 제안은 아니다.

이 보정 문구의 실제 적용은 현재 리뷰 요청에서 수행하지 않는다. 현재 두 v0.1 문서는 위 보정이 반영된 것으로 간주할 수 없다.

### Further Review Judgment And Remaining Risk

Reviewer는 F1이 새 trust/연결 경계를 정의하므로 보정 diff에 대한 추가 R0 한 회를 권고했다. Driver는 모든 F1 보정이 반드시 새 채널 도입이라는 전제에는 동의하지 않는다. 보존된 기존 console 경로를 정확히 연결하고 금지된 통신 경로와 구분하는 보정으로 좁힐 수 있다. 따라서 전면 재리뷰나 추가 호출을 자동 다음 단계로 정하지 않는다. 실제 보정 diff가 새 권한·통신·token·판정 의미를 도입하는지 확인해 Source Workflow의 적용 범위를 따르고, 필요한 Owner review 결정을 대신하거나 일반 면제를 만들지 않는다. 이번에는 추가 reviewer를 호출하지 않았다.

P0 2시간에 복구·부팅·fixture·전달·도구·양 OS 통제가 모두 들어가는 일정 위험은 남는다. 준비가 안 되면 P0에서 멈추도록 설계된 사실과 준비가 성공했다는 주장은 다르다. VHDX 재부팅 후 상태, guest 공유 서비스, MOTW, SMB loopback, clipboard off 입력, restore boot는 현재 실행하지 않았으므로 확정하지 않는다. Reviewer의 일반 platform 지식도 이 guest의 재현 결과로 옮기지 않는다.

두 OS×두 mode의 첫 full이 각각 120분을 쓰면 P4 12시간 중 8시간을 쓴다. 남은 4시간에 R1·보정·정리가 들어가며 모든 재시도 슬롯이나 완료를 보장하지 않는다. 이 위험 때문에 예산을 자동 확대하지 않는다. DR-0007 v0.10·B·공통 worker 조건·원 ticket/whole-result·기존 guard, A13 전체 qualification·별도 activation/live Preview 이후 formal admission은 유지한다.

### Reviewer Response Verbatim

````markdown
# R0-A01 — Execution Approval Proposal v0.1 + Local Execution Bindings v0.1 정적 리뷰

## 1. Verdict: **conditional**

두 문서는 범위, 한도, 정지 조건, 계약 보존 측면에서 v0.4와 DR-0007 v0.10에 대체로 정합합니다. 새로 고른 환경 준비 방식(APFS recovery·restore clone, VHDX/loopback SMB, process-scope 정책, tokenizer venv)과 no-tools reader 방식도 기존 계획 범위와 모순되지 않습니다. 계획 L150·L164·L172·L200이 바로 이런 명시 승인을 요구했고, APPROVAL은 그 요구를 채우는 형태입니다.

다만 **이대로 한 번의 bounded 실행 승인에 쓰기에는 결함 두 건을 먼저 닫아야 합니다.**
- **F1:** Driver가 offline guest에서 표준 계정으로 명령을 실행하고 회수하는 **제어 채널**과, 반복 transfer/reboot 주기의 운영 의존성이 정해지지 않았습니다. 이 채널이 "차단된 host 연결"과 "standard token" 주장을 집행할 수 있는지를 결정합니다.
- **F2:** guest 실행 출력을 fresh-reader와 R1에 전달하는 일과 BINDINGS의 disclosure 금지가 구성상 충돌합니다.

두 건 모두 보정 범위는 작습니다. 수정 방향은 아래와 같습니다.

## 2. Must-fix findings

### R0-A01-F1 · P1 — guest 실행·제어 채널과 transfer 주기의 운영 의존성이 정해지지 않음

**근거**
- APPROVAL L45, L53: 제품 실행 중 Network=[]·share None·clipboard off·USB off를 유지하고 "차단된 host 연결"을 검증한다고 합니다.
- APPROVAL L56: 모든 반입·반출은 다음 순서를 거칩니다. 정상 shutdown → transfer 설정 → 전용 계정에서 복사 → 정상 shutdown → 공유 차단 → 재기동.
- APPROVAL L60, BINDINGS L52: 로그인과 UAC 비밀 입력은 Owner가 UI에서 직접 처리합니다.
- APPROVAL L58: 관리자 권한은 VHDX·SMB의 "준비/회수"에만 허용됩니다.
- APPROVAL L49: 준비 권한 표가 허용 범위 전체이며, 그 밖의 설치·계정·정책 변경은 허용하지 않습니다.
- APPROVAL L133: 범위 밖 연결 변경은 정지 사유입니다.
- APPROVAL L88: Driver가 "같은 W1 경계에서 실행"합니다.
- APPROVAL L130: child 회수를 확인하지 못하면 정지합니다.
- BINDINGS L46: host 쪽 VM 조회 수단만 있고, guest 안에서 명령을 시작·관측·회수하는 수단은 두 문서 어디에도 없습니다.
- PLAN L168: "자식 실행과 회수 방법"을 P0에서 고정한다고 했습니다.

**실패 경로**
1. offline이고 clipboard·share가 꺼진 guest에서 Driver가 명령을 내리려면 host↔guest 제어 채널이 반드시 하나 있어야 합니다.
2. 그 채널이 guest agent류라면 그것 자체가 host 연결이며, 보통 표준 계정이 아닌 상위 token으로 실행됩니다. 이 경우 L43·L45·L60의 "전용 standard token에서 제품 실행" 주장과 충돌합니다. run-as를 하려면 저장 credential이 필요한데 이는 금지되어 있습니다(L59, BINDINGS L52).
3. 그 채널이 Owner의 console 조작이라면, 40시간 동안 Driver가 자율적으로 반복할 수 있다는 전제(L12)가 성립하지 않습니다.
4. L56의 transfer 주기는 재부팅을 두 번 포함합니다. 매 부팅마다 Owner의 로그인 입력이 필요합니다.
5. DiskPart로 attach한 VHDX는 일반적으로 재부팅 뒤 분리됩니다. 재부팅 때마다 관리자 재-attach와 Owner UAC가 필요할 수 있습니다. 이것이 "준비/회수"에 포함되는지도 문서상 불명확합니다.
6. P1/P2의 Windows 개발 반복은 source 반입과 결과 반출을 여러 번 요구합니다. 따라서 반입 빈도가 Owner 대기와 재부팅 비용으로 곧바로 이어집니다.
7. P0에 와서야 채널이 L49 표 밖의 연결이나 token이라는 사실이 드러나면, L133에 따라 W1 제품 실행 전체가 멈춥니다.

**승인 전에 닫아야 하는 이유**

이것은 P0에서 정하는 매개변수가 아니라 **신뢰·연결·권한 경계 자체**입니다. Owner가 승인 시점에 이 경계를 볼 수 없으면 L45의 "차단된 host 연결" 판정 기준이 없습니다. 또한 승인한 범위 안에서 실행이 실제로 가능한지도 판단할 수 없습니다.

**최소 보정**

BINDINGS에 한 행, APPROVAL L53 또는 L56에 한 문장을 추가합니다. 내용은 다음과 같습니다.
- 2026-10-17 probe에서 실제로 쓴 guest 실행 채널을 식별합니다. 채널 종류, 실행 token/계정, 운반할 수 있는 데이터, 제품 실행 중 허용 여부를 적습니다.
- 그 채널을 제품 실행 중 허용되는 유일한 host↔guest 경로로 명시하고, P0 canary의 검사 대상에 넣습니다.
- 반입·반출을 candidate 또는 batch 단위로 묶는 원칙과, 부팅마다 필요한 Owner 입력을 적습니다.
- 재부팅 뒤 같은 VHDX identity를 다시 attach하는 일이 L58·L60의 준비 권한에 포함되는지, 아니면 fixture가 필요한 batch에서만 한 번 attach하는지를 정합니다.

채널이 없거나 Owner console 방식이라면 그 사실과 그에 따른 진행 방식을 그대로 적으면 됩니다. 새 권한을 만들 필요는 없습니다.

### R0-A01-F2 · P2 — 실제 실행 출력의 전달과 disclosure 금지의 구성상 충돌

**근거**
- APPROVAL L78, L90: fresh-reader 두 번째 호출에 "실제 저장 상태와 출력"을 전달합니다.
- APPROVAL L77: R1에 "식별된 합성 실행 결과"를 전달합니다.
- BINDINGS L73: 전송 packet에 "실제 local 경로와 … 계정 정보"를 넣지 않습니다.
- BINDINGS L38–L43: guest 실행 root, fixture, 합성 프로젝트가 모두 전용 계정 profile 아래에 있습니다. 따라서 절대 경로마다 계정명이 들어갑니다.
- macOS 쪽 fixture와 log도 host 계정 경로 아래에 있습니다(BINDINGS L17–L24).
- WORKFLOW L108·L116: 실제 전송 범위는 명시 승인되어야 하고, 불일치하면 호출을 멈춥니다.

**실패 경로**

제품의 view/status/오류 출력과 runner log는 대상 절대 경로를 포함할 가능성이 높습니다. 그러면 결과는 둘 중 하나입니다.
- 호출 직전 disclosure 검사에서 호출이 막힙니다. 그러면 fresh-reader와 V12가 unavailable이 됩니다.
- Driver가 승인되지 않은 즉석 치환으로 출력을 바꿉니다. 그러면 reader가 본 입력과 실제 출력이 달라지는데, 그 차이가 증거 의미에 기록되지 않습니다.

어느 쪽이든 L92가 말하는 "실제 관측에 근거한 exercise"의 근거가 흐려집니다.

**승인 전에 닫아야 하는 이유**

이번 승인이 곧 외부 provider로의 데이터 전송 승인입니다. 전송할 출력이 구조상 금지 대상을 포함하므로, 처리 규칙이 승인 안에 있어야 합니다.

**최소 보정**

다음 중 하나를 한 문장으로 정합니다.
- (a) 결정적 placeholder 치환 규칙: host·guest 절대 경로 prefix와 계정명을 고정된 중립 토큰으로 바꿉니다. 대응표는 private로 보존합니다. reader가 치환된 출력을 받았다는 사실을 exercise와 R1 기록에 남깁니다. Driver가 reader의 명령을 실행할 때 역치환하는 일은 L88의 동적 값 채우기와 같은 범주로 기록합니다.
- (b) fresh-reader 합성 프로젝트를 중립 경로에 둡니다. 예를 들어 이미 승인된 합성 NTFS fixture volume 등 계정명이 드러나지 않는 위치입니다. 이때 그 경로가 A7의 local NTFS 조건을 만족하는지 P0에서 확인합니다.

## 3. Optional notes (실행 승인 blocker 아님)

- **O1 · canary 실패와 안전 정지의 경계.**
  - 충돌하는 두 조건: APPROVAL L111과 PLAN L180은 canary를 "근거 있는 보정 뒤 1회" 다시 검증하도록 허용합니다. 반면 APPROVAL L129·L135는 "허용 밖 쓰기/network 노출"을 즉시 정지 사유로 두고 재시도 사유로 쓰지 않습니다.
  - 해석상 문제: task 소유의 합성 outside-write canary가 성공해 버린 경우가 어느 쪽인지 문언만으로는 갈립니다.
  - 기본 동작: 정지가 기본이므로 안전 측면의 결함은 아닙니다.
  - 제안: 다음을 한 문장으로 구분해 두면 Owner를 불필요하게 다시 부르는 일을 줄일 수 있습니다.
    - task 소유의 합성 위치나 non-routable 대상에 국한된 통제 미성립은 보정 가능한 control 실패입니다. 제품 실행 전이며 재검증 1회 범위 안에서 다룹니다.
    - 비합성 자료, credential, host에 노출된 경우와 두 번째 실패는 정지 후 Owner 판단입니다.
  - 덧붙여 network canary의 목적지는 실제 외부로 트래픽이 나가지 않는 대상으로 P0에서 고정하는 것이 좋습니다.
- **O2 · fresh-reader에서 Driver 개입의 판정 규칙.**
  - 구조상 한계: exercise당 호출이 2회이므로, reader는 첫 호출에서 view/manual 출력을 보지 못한 채 전체 경로를 제안해야 합니다(L86, L90).
  - 위험: 그만큼 Driver가 보완하는 몫이 커집니다.
  - 제안: P3 실행 전에 Driver 개입의 허용 범위를 고정합니다. 관측된 ID/token 대입, 합성 human 응답, F2의 역치환만 허용합니다. 그 밖의 수정이 필요하면 reader의 막힘(non-pass)으로 기록합니다.
  - L92가 "긍정 답변만으로 PASS 불가"를 이미 막고 있으므로 이 항목은 P3 입력으로 충분합니다.
- **O3 · Owner 문안(L151).**
  - L29의 단일 FEAT 진행 기록 지정, CHORE pointer, Index link를 문안에 명시적으로 언급하면 WORKFLOW L48의 "Owner 선택·계획 승인" 근거가 더 분명해집니다.
- **O4 · timeout·quota 뒤 재호출.**
  - L80의 "자동으로 새 process를 띄우지 않는다"가 원인을 기록한 수동 재호출(한도 안)까지 막는지 한 단어로 정리하면 해석이 갈리지 않습니다.

## 4. 영역별 짧은 판정

**환경/복구: F1을 빼면 정합합니다.**
- 기존 마지막 recovery를 boot하지 않고 덮어쓰지 않음, 새 pre-product recovery, restore clone에만 새 UUID와 차단 설정 적용, 다른 VM unregister 금지가 서로 맞물립니다(APPROVAL L54, BINDINGS L48).
- 다음도 일관됩니다.
  - APFS clone과 15GiB floor(L55, L132)
  - 이전 recovery가 pre-probe 상태라서 현재 입력을 대체하지 않는다는 인식(BINDINGS L48)
  - VM 전체 rollback은 별도 판단이라는 경계(L67, L145)
- 권한 경계도 정합합니다. 관리자 권한은 exact 신규 VHDX·SMB에만 한정되고, 표준 사용자 qualification은 별도로 유지됩니다(L60, L63; DR A6 L644). Job Object를 filesystem sandbox와 구별합니다(L45). 계정 정리로 우회하는 것을 금지합니다(L43).

**calls/time/stop: 정합합니다.**
- 단계 합: 2+8+12+4+12+2 = 40시간입니다.
- R1은 3회×20분(합계 60분), fresh-reader는 4회×10분(합계 40분)·exercise 최대 2개입니다.
- 실패한 호출도 1회로 세고, 사전 검사에서 중단된 경우는 호출 수에서 빼되 시간은 포함합니다(L80).
- P4/R1 이후 보정은 P4에 귀속하고, 재분류로 한도를 초기화하지 않습니다(L119).
- 먼저 닿은 한도를 적용합니다(L117).
- 정지 후 2시간 여유는 구현 연장에 쓰지 않습니다(L105).
- 모두 PLAN L194–L204와 일치합니다. 모든 재시도 슬롯을 다 쓸 수 있다는 보장이 없다는 점은 L119가 직접 밝힙니다.

**DR/B/worker 보존: 문제없습니다.**
- B 배정을 유지하고, x64·물리 부재를 gate로 만들지 않습니다(L41, L137).
- macOS 사례를 통째로 N/A 처리하지 않고, wrong-OS 거절과 read 진단을 구별하면서 cross-OS 지원은 추가하지 않습니다(L123). R0-I04-F1에 대한 Driver 처분과도 정합합니다.
- 공통 조건, 원 ticket, whole-result, pending barrier를 유지합니다(L125).
- A13의 published/refetched equality, 별도 activation, live Preview 이후 formal admission을 구별합니다(L141).

## 5. P0에서 확인할 조건과 잔여 위험 (승인 전 필수 아님)

- **P0 2시간의 현실성.** 다음 작업이 모두 2시간 안에 들어갑니다. recovery와 restore boot, VHDX와 SMB 준비, 두 차례 transfer 주기(재부팅 포함), tokenizer 반입, 두 OS의 canary, old-writer bytes×경로 표(PLAN L77), runtime tuple 확인. 넘기면 정지하는 설계(L69)가 맞지만, 승인 전체가 P0에서 끝날 위험이 있습니다.
- **restore clone boot는 1회뿐입니다.** 실패했을 때 W1 제품 실행을 시작하지 않는다는 결론은 PLAN L54·L172를 함께 읽어야 나옵니다. 식별값 변경 때문에 guest 쪽 복구 절차(디스크 암호화 등)가 요구될 가능성은 미확인입니다.
- **clipboard false 전환과 recovery 생성의 순서.** 어느 쪽이 먼저인지에 따라 recovery 설정이 달라집니다. 순서를 ledger에 기록하는 것이 좋습니다.
- **transfer 경로의 guest 쪽 기존 구성요소.** host 공유를 guest가 받으려면 guest 쪽 서비스나 도구가 필요할 수 있습니다. L57(guest tools 설치 금지)과 L59(서비스 일시 start는 SMB만 허용)의 범위 안에서 실제로 동작하는지 확인해야 합니다. 동작하지 않으면 반출 수단이 없으므로 제품 실행을 시작하지 않습니다.
- **반입 script의 Mark-of-the-Web.** 공유를 통해 반입한 script에 MOTW가 붙으면 process-scope RemoteSigned에서 차단될 수 있습니다. 이를 Bypass로 바꾸지 않아야 합니다.
- **SMB loopback fixture.** backing folder가 NTFS이므로 filesystem 이름만으로는 remote 판별이 통과될 수 있습니다. remote 판별 oracle이 FS 이름에만 의존하지 않는지 확인해야 하며, 이는 fixture로서 오히려 유용한 점입니다.
- **VHDX 볼륨 경로.** folder mount를 쓰면 reparse 관측이 섞이므로 drive 경로를 쓰는 편이 해석이 깨끗합니다.
- **tokenizer dependency.** dependency 버전은 해석 결과에 따라 정해집니다. 실제 wheel의 이름·version·hash를 설치 전에 고정하고(L65), counting은 offline cache로만 수행하는지 확인해야 합니다.
- **관리자 shell의 profile 로드.** 관리자 shell이 원 관리자 계정의 profile을 로드하는 것은 "원 개인 profile 비접근"(L43)의 엄밀한 해석과 긴장이 있습니다. script를 고정 명령으로 제한하는 방식으로 관리하면 됩니다.
- **old-writer와 PS 5.1 입력 보존.** old-writer 거절 미확인과 PS 5.1 입력 보존 실패는 qualification을 미완료로 남깁니다. 계약에 맞는 결과입니다.
- **P4 압박.** 첫 full 네 번에 최대 8시간이 들어 R1과 보정에 쓸 시간이 좁습니다. 의도된 성질이며 증액 사유가 아닙니다.

## 6. 권고 next step

1. Driver가 F1과 F2를 APPROVAL v0.2와 BINDINGS v0.2에 반영합니다. 필요하면 O1–O4도 함께 반영합니다.
2. F1의 보정은 host↔guest 신뢰·연결 경계를 새로 명시하는 **material change**입니다. 따라서 변경 diff와 새로 binding된 채널에 한정한 R0 한 회를 권고합니다. 전면 재검토는 필요 없다고 봅니다. F2만 반영하는 경우라면 범위는 더 좁아집니다.
3. 추가 R0의 실시 여부와 범위는 WORKFLOW L64에 따라 Owner가 정합니다. 이 리뷰는 면제를 선언하지 않습니다.
4. 그 뒤 Owner가 실행 승인 여부를 결정합니다. 제품 구현과 VM 작업은 그 승인 전까지 시작하지 않습니다.

## 7. Static-only 한계와 제공받지 않은 증거

- 이 리뷰는 packet 문안만 대조한 정적 리뷰입니다. hash와 byte 수는 packet 값을 인용했을 뿐 재계산하지 않았습니다. 도구, VM, test는 실행하지 않았습니다.
- 다음은 제공받지 않았습니다.
  - raw probe 출력과 2026-10-17 guest 상태
  - probe에서 실제로 쓴 guest 제어·전송 채널. F1은 이것이 문서에 binding되지 않았다는 지적이며, 채널이 없다고 단정하는 것이 아닙니다.
  - UTM 공유와 guest 서비스 구성
  - 제품 source, tests, runner
  - Microsoft·PyPI 문서 본문
  - 현재 host·guest의 credential과 profile ACL
- VHDX 재부팅 후 분리, 공유 설정 변경에 VM 정지가 필요한지, MOTW 동작은 일반적인 플랫폼 지식에 근거한 위험 지적이며 이 guest에서 확인한 사실이 아닙니다.
- 독립성 한계: fresh session 1회이며 R0-I04 결론과 Driver 처분을 함께 받았으므로 anchoring 가능성이 있습니다.
- 이 verdict는 Owner의 실행 승인이나 개발 결과 수락이 아닙니다.
````

### Verification And Retention

두 v0.1 대상·plan v0.4·DR v0.10의 exact bytes를 유지하고 문서 GFM/링크·신규 disclosure·review 원문·frozen 입력·기존 record prefix·Git/VM config를 확인한다. 제품 test/추가 실험으로 보고하지 않는다. 필수 request/packet/입력/final/metadata/runner는 Owner 처분과 exact 승인 보정 입력 비교에 필요하며 후속 입력 고정 시 재평가한다. 동일 partial·빈 stderr·빈 tool-temp만 원문 보존과 사용 종료 확인 뒤 정리한다. 기존 worktree·계획/승인 입력·review/probe 근거·마지막 recovery는 가까운 보정·구현·비교·복구 소비자가 남아 유지하며 활성 경로는 바꾸지 않는다.

최종 문서 QA는 marked 17.0.5 GFM 9문서·207개 local links, 기존 비기록 입력 277개, 17개 review 원문·이번 frozen 입력 10개, 두 v0.1 대상·plan·DR bytes, 기존 record prefix·Git/VM config 불변을 확인했다. 제품 검증은 실행하지 않았다. 종료된 CLI와 lsof의 사용 없음, 원문 보존을 확인한 뒤 final과 동일한 partial·빈 stderr 2개와 빈 tool-temp 1개를 삭제했다. 필수 6개 리뷰 자료와 기존 근거·복구본은 유지했고 활성 경로는 변경하지 않았다.

## Execution Approval Proposal v0.2 — 2026-10-18

Owner는 R0-A01 F1·F2와 Driver 판단을 반영해 실행 승인안과 Local Execution Bindings를 v0.2로 보정하되, DR-0007 v0.10·B안·공통 조건 중심 worker 지원을 유지하고 추가 리뷰·제품 구현·실험은 시작하지 말라고 요청했다.

[실행 승인안 v0.2](windows-native-execution-approval.md)와 기존 local binding 문서를 같은 경로에서 수정했다. 승인 상태는 Proposed이며 v0.2의 추가 리뷰·실행 승인은 없다. v0.4 계획과 DR의 bytes는 그대로다.

| 보정 | 반영 내용 |
| --- | --- |
| F1 | 기존 UTM console·CUA 개별 key 입력·interactive standard token·guest-local runner/Job Object를 명시했다. 허용된 console/VM 관리와 차단할 host 파일 공유·clipboard·외부 network·guest-agent exec를 구분했다. 과거 clipboard true 관측과 P0의 clipboard off 검증을 구별했다. |
| F1 반복 운영·복구 | Owner 로그인/UAC 입력 의존성, candidate/batch 전달, 동일 VHDX identity의 re-attach와 standard token 복귀, 관리자 shell의 -NoProfile을 명시했다. 최초 준비는 P0, 이후 승인된 반복 운영은 실제 단계/P4에 귀속하며 미완료 최초 준비를 뒤로 넘기지 않는다. 개별 개인 파일 접근 금지와 전체 VM package의 local recovery 보존을 구별했다. |
| F2 | private 원출력·고정 경로/계정 대응표·원본/파생 identity를 보존하고 외부에는 비식별화한 파생 입력과 치환 사실을 전달한다. exact prefix/field·가장 긴 prefix 우선·의미 보존·미처리 private 문자열의 전송 중단을 규정했다. 임의 명령 역치환 실행은 허용하지 않는다. |
| Driver 처분 | reader가 찾지 못한 명령/문서를 Driver가 보완하면 막힘/non-pass를 기록한다. 원인 해소·기존 한도 안의 후속 호출과 자동 quota/timeout 재시도를 구별했다. 합성 canary의 실제 경계 위반도 중단한다. 단일 실행 기록/Index 권한은 중복 확장하지 않았다. |

승인안: 30,759 bytes, SHA-256 `f93fc8ad35daed742cfcbb7ee3340eda007ba70c8acda3e080fe429f31b5d089`.
Local bindings: 15,970 bytes, SHA-256 `182fe397f6fab3e516006c3f8eff319182989c444fc33916e27f8c7d21f19c9a`.

23개 승인안·12개 binding의 한정 치환을 원문과 대조했다. v0.1 원문은 R0-A01 frozen packet으로 회수 가능하며 두 bounded diff와 v0.2 입력 manifest를 보존했다. 과거 manifest나 review 원문을 현재 의미로 다시 쓰지 않았다. 현재 local binding의 경로는 유지하고 새 manifest 위치만 연결했다.

GFM 렌더링 9문서·207개 local links, 기존 비변경 입력 281개, 17개 review 원문·R0-A01 frozen 입력 10개, 원문→허용 치환→결과의 exact 일치, plan/DR·기존 record prefix·Git/VM config 불변과 diff-check를 확인했다. 이는 문서 검증이며 native 실행·비식별화 프로그램 실행·추가 리뷰가 아니다. 시간/호출/시도 수, B 배정, 원 ticket·whole-result·guard, qualification/publication/activation/formal admission의 기존 경계를 유지했다.

이번 보존 대상은 현재 두 문서와 입력 manifest·두 diff다. Owner의 v0.2 비교/실행 승인과 이후 exact 입력 확인이 소비자이며 후속 입력 고정 시 재평가한다. 새 helper·QA 파일이나 disposable 사본을 만들지 않아 이번 단계 삭제 대상은 없다. 기존 리뷰·probe·worktree·마지막 recovery는 가까운 보정/구현·비교·복구에 필요해 유지하며 활성 경로 변경은 없다. STATUS·Index·새 FEAT ID·Git action·VM 조작은 수행하지 않았다.

## Execution Owner Handoff — 2026-10-18

Owner가 실행 승인안 v0.2와 Local Execution Bindings v0.2를 승인했다. 후속 P0–P4 구현·검증의 단일 진행 정본은 [FEAT-20261018-003-windows-native-implementation](FEAT-20261018-003-windows-native-implementation.md)이다. 이 CHORE는 기존 준비·probe·계약 수락·R0 근거의 역사적 소유자로 남고 이후 실행 진행을 중복 기록하지 않는다. 승인 대상 bytes와 B안·공통 조건 중심 worker, 호출·시간·중단 경계는 새 기록에 연결했다. 이 이관은 Git/publication/adopter action이나 결과 수락·activation을 포함하지 않는다.
