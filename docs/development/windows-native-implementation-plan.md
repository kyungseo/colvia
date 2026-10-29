# Windows Native Implementation And Verification Plan

Revision: 0.4
Date: 2026-10-18 (KST)
State: Revised after R0-I03; v0.4 not re-reviewed; execution not approved
Contract: [DR-0007 v0.10 acceptance](../decisions/DR-0007-windows-native-runtime-contract.md#owner-contract-acceptance--2026-10-18)
Preparation record: [CHORE-20261017-001](CHORE-20261017-001-windows-utm-feasibility-probe.md#owner-contract-acceptance-and-follow-up-plan--2026-10-18)
Source baseline: `a93f71c359c4f0a9d57fcfb50d5999160e870f77`
Review basis: [R0-I01 and Driver dispositions](CHORE-20261017-001-windows-utm-feasibility-probe.md#r0-i01--implementation-plan-v01-review-and-driver-judgment--2026-10-18); [R0-I02 and Driver dispositions](CHORE-20261017-001-windows-utm-feasibility-probe.md#r0-i02--implementation-plan-v02-re-review-and-driver-judgment--2026-10-18); [R0-I03 and Driver dispositions](CHORE-20261017-001-windows-utm-feasibility-probe.md#r0-i03--implementation-plan-v03-re-review-and-driver-judgment--2026-10-18)

## Outcome And Authority

목표는 수락된 S1–S8과 A1–A15를 구현하고, Windows 전용 `windows-1`의 fresh init과 같은 window 안의 lifecycle·Work·worker가 계약대로 동작하는지 통합 검증하는 것이다. B안은 대표 UTM에서 전체 검증을 수행하고, x64·물리 장비는 차이가 있는 메커니즘을 focused 검증으로 보완하는 방향이다. 실제로 관측하지 않은 tuple을 qualified로 표시하지 않는다.

2026-10-18 Owner는 “DR-0007 v0.10의 S1–S8과 A1–A15 계약을 수락할게. 수락 기록을 정리하고 후속 구현·검증 계획을 작성해줘. B안과 공통 조건 중심 worker 지원은 유지하고, 추가 실험이나 제품 구현은 아직 시작하지 마.”라고 요청했다. v0.1부터 v0.3까지 R0-I01–I03의 conditional 판정과 Driver 처분에 따라 보완했다. Owner의 후속 요청에 따라 이 v0.4는 R0-I03-F1/F2의 집행 규칙과 F3–F6의 필요한 설명만 반영한다. 수락 계약과 B안·공통 조건 중심 worker 지원은 유지한다. 이번 변경은 계획과 그 작성 기록에 한정한다. 새 probe, 제품 코드·test·runner 구현, VM 실행, 후속 reviewer 호출과 Git action은 수행하지 않는다.

```text
완료: exact 계약 수락 → v0.1 R0-I01 → v0.2 R0-I02 → v0.3 R0-I03
현재: R0-I03 지적을 반영한 계획 v0.4 준비
다음: v0.4 검토·처분 → 범위·검증 계획의 실행 승인
      → 구현·통합 검증 → R1·Owner 개발 결과 수락
      → 별도 승인된 배포·A13 전체 qualification → exact activation
      → live macOS Preview 이후 Windows formal admission
```

R0/R1은 [Source Workflow](WORKFLOW.md#review-and-evidence)의 기존 경계다. R1-D10은 계약 문서를, R0-I01–I03은 각각 계획 v0.1–v0.3을 검토했다. 어느 결과도 v0.4의 재검토나 미래 구현의 R1을 대신하지 않는다. 실행 승인 때 한 번 합의한 범위 안의 구현·검증·보완은 그 승인으로 진행한다. P0의 통제 canary와 P1–P4의 bounded 검증·수정은 실행 승인에 포함할 범위이며 단계·API 매개변수마다 반복 승인을 만들지 않는다. P0에서 값을 구체화하는 것은 승인된 경계를 집행하는 일이고, 경계를 넓히거나 한도를 올리는 것은 별도 범위 결정이다. local commit을 포함한 Git action·publication·실제 adopter 적용은 해당 명시 승인을 따로 확인한다. 계약 의미·실행 경계·지원 범위 변경이나 안전성 불일치는 해당 부분을 멈추고 필요한 변경만 제시한다.

현재 기술 계약은 entry-1과 First B1이다. DR-0007은 앞으로 구현할 정확한 Windows 계약을 수락한 상태이며 제품 allowlist·설치물·기존 normative 파일에 자동 적용되지 않았다. 이 계획의 작성·수락과 실제 구현 실행 승인은 별도다. 구현 task ID와 진행 정본은 실행 범위를 선택할 때 지정하고, 그 전까지 이 계획의 준비 결과는 기존 CHORE에 둔다.

## Fixed Scope And Remaining Inputs

수락 대상 원문은 DR-0007 v0.10의 177,174 bytes, SHA-256 `cd6f3bf06d842afb8f71aac98e95382acc04b4524ee54b80af179b11ad0c3add`다. 수락 metadata를 추가한 현재 DR은 181,284 bytes, SHA-256 `e7679a8e11b5e38171888ab6da748cabd6ad5e46dc84e48205733a8e0e6d9ede`다. 이 계획 보완은 그 계약의 revision·S1–S8·A1–A15를 변경하지 않는다.

| 구분 | 이 계획의 범위 |
| --- | --- |
| 고정 계약 | windows-1/profile, 기존 29 managed paths·11 Python modules, init1/switch2/repair1/detach4, 명시 Python 진입, 자동 replace retry 0회 |
| Runtime | native Windows 11 ARM64/ARM64 또는 x64/x64의 64-bit final·GIL-enabled CPython 3.14.6/3.14.7, isolated/no-bytecode |
| 최초 lifecycle | fresh Git/non-Git init, 같은 window update·직전 release rollback·exact repair·detach와 계약상 중단 복구 |
| Worker | 변경 경로 집합 전체에서 base/result·실제 상태와 독립 post-mode 또는 부재 관측이 일치하는 공통 조건. 예시를 닫힌 allowlist로 구현하지 않음 |
| 유지할 의미 | authority·scope·retained source·whole-result·원 request/token·completed replay·cancellation·macOS 기존 동작 |
| 제외 | old-window 이주·cross-window/cross-OS rollback, 새 mode-policy field·registry·managed module, .cmd launcher, 비관측 tuple의 qualification, 실제 adopter 적용 |
| 이후 고정할 입력 | 통합 source·prepared source와 P/Q candidate, 환경 tuple·fixture·노출 writer×접근 경로·runner/policy, 실제 discovery/test ID와 phase별 유한 시간·시도 한도 |

대표 환경의 제안은 기존 UTM 계열 Windows 11 ARM64와 ARM64 CPython 3.14.7, 표준 사용자·local NTFS·Windows PowerShell 5.1이다. 이전 probe의 Windows 11 Pro 26H2/build 10.0.26300.9711 관측은 과거 입력일 뿐 새 실행 시의 tuple을 증명하지 않는다. OS edition/build, process architecture, Python executable/version/build mode, Git, shell, filesystem과 VM/recovery identity를 새 실행 전에 고정한다. 3.14.6과 x64가 계약상 허용되어도 실제 관측 없이 qualified로 올리지 않는다.

비교 seed는 DR-0007의 [Reader And Writer Combinations](../decisions/DR-0007-windows-native-runtime-contract.md#reader-and-writer-combinations)에 있는 baseline·entry-1·First B1·checkout-1 identity다. 실행 전에 정확한 bytes와 실제 접근 경로를 회수·확인한다. source commit과 release digest는 서로 다른 종류의 식별값으로 관리한다. 모든 역사적 writer 회수를 요구하지 않으며 실제 노출이 불명확한 writer를 임의로 비노출 처리하지도 않는다.

## Delivery Stages

아래 단계는 의존 순서이며 각각 새로운 승인 절차를 뜻하지 않는다. 지금은 전부 미실행이다.

| 단계 | 구현·검증할 일 | 완료를 판단할 근거 |
| --- | --- | --- |
| P0 · 실행 입력과 통제 | baseline drift, Windows/macOS runtime·runner·권한·fixture·writer 노출·회수 경로·시간/시도 한도를 고정. 승인된 실행 범위에서 통제 canary 수행 | 회수 가능한 source/VM 입력과 증거 반출 경로, 실제 통제 관측. 불명확한 경계에서는 제품 실행 시작 금지 |
| P1 · native 기반과 시험 진입 | runtime/window·import-safe backend·path·lock·flush/replace 구현, platform별 test import/discovery·기대값 정렬, operation/phase별 sync 의무 대응. 명시 Windows source 준비 경로와 첫 init용 candidate 확보 | 실제 native collection, focused 성공/거절/경합/중단, 첫 P2 init에 쓸 고정 payload. 초기 candidate는 개발 입력이며 최종 qualification이 아님. 독립 probe 통과를 제품 통합 PASS로 재사용하지 않음 |
| P2 · lifecycle와 content | fresh init 직후부터 exposed old-writer 거절, init/switch/repair/detach와 read-only 경로, snapshot·worker 공통 조건·whole-operation preflight. 첫 switch/양방향 reader 검증 전에 P/Q 준비 | 아래 최소 coverage와 실제 test ID 연결, 필수 prefix의 독립 관측, 원 기록·전체 결과 보존. old-writer gate를 P4로 미루지 않음 |
| P3 · 문서와 candidate freeze | A1–A15 named placement·help/capability/entry parity, 기술 계약 11개 문서·managed membership, 읽기 예산과 소비 경로. 수정된 source를 명시 준비하여 최종 P/Q와 artifact 고정 | 공통 source의 명시 변환 기록, prepared Windows source↔local artifact equality, managed 29 paths·Python 11 modules의 구별. published/refetched equality는 별도 승인된 배포 단계에 남김 |
| P4 · 통합 검증 | 대표 Windows normal·parent-optimized 전체 suite, focused lifecycle/환경 사례, shared 변경의 macOS focused·전체 회귀, 필요한 x64/물리 focused 보완 | 최종 candidate의 discovery/execution ledger와 결과, cumulative reuse 판단. unknown·skip·timeout·missing은 PASS가 아님 |
| Closeout · 개발 결과와 후속 발효 | R1·Driver 처분, exact 개발 결과·residual criteria 제시, Owner 결과 수락과 별도 activation 대상 준비 | 개발 결과, published/refetched 검증, activation, formal admission을 아래 완료 기준대로 구별. formal Windows admission은 live macOS Preview 이후 별도 결정 |

P1–P3의 변경이 겹치면 작게 통합하되 단독 파일 통과로 단계 완료를 선언하지 않는다. P4 통합 검증은 A13 qualification의 일부이며 published/refetched equality까지 끝난 전체 qualification과 같지 않다. 실제 노출 old writer의 거절을 확인할 수 없거나 발행 가능성이 남으면 영향을 받는 통합 검증과 qualification/activation을 완료하지 않는다. 검증 가능한 비노출 경계 또는 최소 거절 장치를 기존 실행 계획에 구체화한다. 수락된 의미와 승인 범위 안의 구현은 그 실행 승인으로 진행하고, 의미·지원·신뢰 경계를 바꾸면 해당 amendment로 돌아간다.

### Candidate And Flush Prerequisites

P1에서 common source의 macOS entry-1 입력을 보존하면서 Windows literal·payload를 별도 prepared source로 만드는 명시적 개발 도구를 준비한다. 첫 candidate 생성 전에 입력 파일별 기대 변경·변환 명령·출력 경로와 bytes를 고정한다. Windows literal 선언과 수락 계약에 필요한 payload 차이를 명시하며, 공통 구현·문서 수정은 준비 입력에 먼저 반영한다. 해당 준비 단계가 나머지 파일을 보존하는지도 exact diff로 확인한다. 실제 차이가 이 목록과 다르면 candidate 생성을 멈추고 범위 안의 누락인지 계약/범위 변경인지 판단한다. 변환을 지금 “launcher 한 줄만”으로 제한하지 않으며, launcher literal만 사후 변경해 digest를 맞추거나 OS/profile 선택 중 packaging bytes를 바꾸지 않는다. 기존 격리 작업 경로를 사용하며 새 worktree를 필수 조건으로 만들지 않는다. 첫 init에 필요한 import/runtime/profile 경로와 candidate가 준비되지 않으면 P2 init을 시작하지 않는다.

첫 switch/양방향 reader 사례에는 서로 다른 exact windows-1 release P/Q를 사용한다. 각 source/prepared payload·inventory·artifact를 회수할 수 있어야 하며 Q가 생성한 local/worker/parent/planning 기록을 P에서 읽고, 반대 방향도 확인한다. 차이는 같은 수락 계약 안에 있어야 한다. 두 fixture release의 통과는 그 P/Q와 관측된 record family의 호환 증거이며 모든 미래 release의 호환 보증이 아니다. P3에서 문서·관련 수정을 마친 최종 P/Q를 freeze할 때 각 release의 exact identity와 역할을 기록한다. activation 대상으로 제시할 candidate와 호환성 시험 전용 release를 구별하고, 시험 전용 identity를 publication/activation 대상에 대신 쓰지 않는다. 초기 candidate 증거는 누적 변경에 대한 재사용 판단 없이 최종 증거로 옮기지 않는다.

P1에서 현재 호출 경로를 operation×phase별로 정리한다. init/switch/repair/detach 및 authority/worker publication에 대해 필수 file flush, 필수 또는 계약상 unavailable이 허용된 directory sync, 첫 durable publication, 기존 write-capable-open 대상, 실패 시 가능한 prefix와 검증 ID를 연결한다. 이는 개발 기록의 표이며 새 제품 registry가 아니다. launcher·parent init·staging·external backup request/original·회수 시 reflush 대상까지 실제 의무를 추적한다. P2 첫 publication 검증 전에 이 대응이 성립해야 하며, 모든 directory failure를 허용하거나 pure reading에 flush 의무를 새로 만들지 않는다.

### Platform Tests And Early Writer Checks

P1에서 Windows의 POSIX 의존성과 macOS의 Windows 전용 의존성을 모두 import-safe하게 분리하고 각 OS의 mode 기대값을 정렬한다. 현재 `tests/test_entry_window_transition.py`·`tests/test_worktree_process_recovery.py`의 무조건 `fcntl` import, `tests/test_general_work.py`의 chmod→100755 기대는 정적 조사에서 확인한 출발점이다. 실제 native collection 전에는 실패를 재현했다고 쓰지 않으며, 앞으로 추가할 Windows 전용 test가 macOS에서 실패했다는 관측도 아직 없다. import guard·fixture·assertion을 platform 의미에 맞추고 Windows 대응 사례를 준비하되 macOS의 기존 mode-change 등 성공 기대값은 보존한다.

플랫폼 차이가 있는 사례만 기존 test source와 이 계획의 검증 대응에 연결한다. 공통 사례는 양쪽에서 실행하고, Windows가 거절해야 하는 동작은 거절 코드·publication 부재·원 상태 보존을 실제 assertion으로 확인한다. Windows에서의 POSIX 전용 메커니즘과 macOS에서의 Windows 전용 메커니즘에 같은 사전 비적용 규칙을 적용한다. 근거 있는 비적용, 예상 거절의 성공적인 검증, unexpected skip/실패를 구별한다. 비적용 ID·근거는 집계 대상 실행 전에 고정하고 실행 PASS에 더하지 않는 별도 범주로 보고한다. 적용 대상이 모두 실행됐는지와 사전 비적용 목록을 함께 제시하며, 각 OS의 필수 사례를 그 OS의 비적용 목록에 넣거나 실행 뒤 skip을 재분류해 완료로 만들지 않는다. Windows 필수 native 관측과 macOS의 기존 성공 기대 모두 skip/N/A로 닫을 수 없다. 그 밖의 skip·unknown·missing은 non-pass이며 모든 ID에 별도 registry를 강제하지 않는다. P1의 실제 import/discovery에서 얻은 ID와 실행 대상이 맞는지 확인하고, P2의 새 사례도 실행 전에 같은 방식으로 연결한다.

P0에서 source/installed/retained old writer의 exact bytes와 실제 target 접근 경로를 고정하고, local·intent·worker·parent·planning·lifecycle family별 관련 guard를 대조한다. POSIX 호환 runtime이나 복사·동기화 경로는 실제 노출 분석에 해당할 때만 포함한다. P2의 fresh/incomplete init부터 조기 거절을 확인하고, same-window switch와 detach4 prefix를 만든 뒤 그 상태에 노출되는 경로도 확인한다. 단일 unknown-window 사례를 모든 family의 증거로 쓰지 않는다. exposed writer는 첫 authority/content publication 전 거절을 관측하거나 해당 접근 경로의 검증된 비노출 경계가 있어야 한다. 노출 불명·거절 미확인·실제 발행은 영향을 받는 실행과 qualification/activation을 막는다.

## Source Change Map

아래는 현재 source의 책임을 기준으로 한 예상 변경 위치다. 새 managed module·의존성을 기본안에 넣지 않는다. 실제 호출 관계와 baseline drift를 확인한 뒤 필요한 최소 위치를 고른다.

| 현재 위치 | 계획한 책임 | 연결 계약 |
| --- | --- | --- |
| root `colvia` | import 전 native runtime·window 선언 검사, 명시 Python argv 진입, prepared Windows 선언 검증 | S2/S7, A5/A9–A12/A15 |
| `src/hv2ref/jsonio.py` | POSIX import의 조건 분기, Win32 handle/lock/flush backend, 원 오류와 unknown 분류 보존 | S3–S5/S8, A7/A9 |
| `src/hv2ref/workspace.py` | 실제 OS/process/runtime, local NTFS·ancestor/reparse·target identity, publication 관측 | S3/S5/S6, A7/A10 |
| `src/hv2ref/product.py` | windows-1/profile와 record pair, candidate/binding 검증, init/switch/repair/detach, 모든 필수 flush 기존 파일의 사전 검사 | S2/S5/S6/S8, A5/A8/A9 |
| `src/hv2ref/work.py` | index/default provenance, 실제 삭제 관측, worker base/result 전체 공통 조건과 pending/replay/cancellation | S6, A1–A4 |
| `src/hv2ref/intent.py`, `candidates.py`, `view.py`, `cli.py` | 공통 helper의 적용 window·관측 결과·preflight 오류를 실제 호출 경로에 전달, 출력·help 일치 | S3/S5–S7, A1/A7/A12 |
| `src/hv2ref/umbrella.py` | shared helper 영향이 있는 parent 호출 경로만 정렬. 기존 parent 의미·지원 범위 보존 | S6, A1/A2 |
| `tests/` 및 `tests/fixtures/product_plain_auditor.py` | native 성공/거절·실제 prefix와 독립 record 검사. 제품 helper를 그대로 호출해 기대값을 만드는 oracle 금지 | S1–S8, A1–A15 |
| A1–A15 target 문서·managed adapter·`PRODUCT-CAPABILITIES.json` | 수락 본문의 exact placement, 현재 지원·미관측·사용법·refusal parity | A1–A15 |
| source-only preparation/verification 도구 | 명시 Windows source 준비, runner·ID ledger·evidence 수집. managed membership 밖의 개발 도구로 한정 | A9/A13, Maintaining |

root `colvia`의 기본 entry-1 선언과 macOS 준비 경로는 유지한다. Windows candidate는 product import 전에 명시적으로 준비된 source의 windows-1 선언과 payload를 사용한다. 실행 OS를 보고 packaging 때 몰래 bytes를 바꾸거나 파일만 바꿔 digest를 보정하지 않는다. 준비 입력·변환·완성 bytes를 고정한 뒤 candidate를 만들고 source/artifact/refetch를 비교한다.

## Native Implementation Decisions To Validate

Win32 사용은 현재 계약을 구현할 후보 메커니즘이다. 아래 API 설명은 공식 문서에 대한 정적 확인이며 실제 제품 실행 증거가 아니다. `ctypes`의 wide API, 명시 `argtypes/restype`, pointer 크기와 `use_last_error`를 고정해 구조체·오류 전달을 검증한다.

- Path/identity: handle 기반 file ID·attribute/reparse 관측과 volume filesystem 확인을 조합한다. volume root부터 target까지 필요한 ancestor를 확인하고 absent target은 가장 가까운 existing parent와 새 경로를 다룬다. NTFS라는 이름만으로 local 경로를 입증하지 않는다. remote·reparse·alias·관측 불가를 별도로 거절하며 handle 하나가 ancestor 전체를 고정한다고 가정하지 않는다. [GetFileInformationByHandleEx](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getfileinformationbyhandleex), [GetVolumeInformationByHandleW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getvolumeinformationbyhandlew).
- Lock: stable anchor의 offset 0, length 1, non-inheritable handle과 삭제 공유 금지를 검사한다. `LockFileEx`의 overlapped 대기·event 완료를 이용하는 후보를 검토하며 lock 자체의 시간 초과는 두지 않는다. Ctrl+C는 취소 요청 후 실제 completion을 확인하고 획득 여부에 따라 unlock/close한다. `CancelIoEx` 호출 성공만으로 종료 완료를 가정하지 않는다. [LockFileEx](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-lockfileex), [CancelIoEx](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-cancelioex).
- Flush/publication: 기존 필수·허용 unavailable 의무와 실제 호출 phase를 먼저 매핑한다. `FlushFileBuffers`의 write-access 요구를 반영해 교체·제거 파일뿐 아니라 기존 launcher·parent init·staging·backup을 포함한 모든 필수 flush 기존 regular file을 첫 durable publication 전에 검사한다. 디렉터리에 파일 read-only gate를 추가하지 않는다. 실제 flush 실패·unknown prefix를 success로 바꾸지 않으며 전원 장애 내구성을 과장하지 않는다. [FlushFileBuffers](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers).
- Replace/recovery: 자동 retry·copy/unlink fallback을 추가하지 않는다. 공유 위반·권한·예기치 않은 오류와 실제 발행 상태를 구별하고 원 request/token과 exact candidate를 쓰는 기존 재시도만 허용한다.
- Native entry: PowerShell 5.1에서 절대 Python 경로, space·한글·quote·metacharacter 인자, file/stdin/exit를 검증한다. 실패하면 해당 입력 계약을 미지원으로 남기며 PowerShell 7 전환은 exact 대안 선택으로 다룬다.

## Verification Matrix

각 V행은 검증 묶음의 요약이며 그 행 하나의 성공으로 모든 하위 사례를 닫지 않는다. 실제 성공·거절·보존을 입증하고, 기존 suite의 관련 사례를 우선 재사용하며 새 platform 경계와 누락 prefix에 필요한 사례만 더한다. 아래 최소 coverage는 수락 계약과 Maintaining에서 요구한 사례를 빠뜨리지 않기 위한 연결이다. 실제 test ID는 아직 구현·수집하지 않았으며 P1/P2에서 source/fixture·독립 oracle·실행 mode와 함께 고정한다.

| 검증 묶음 | 필수 성공·거절 또는 보존 사례 | 계약 / admission 기준 |
| --- | --- | --- |
| V1 · runtime/entry/read | native ARM64/ARM64·x64/x64 식별, wrong OS/process·emulation·unsupported Python 거절, isolated/no-bytecode, PS5.1 argv/stdin/file/exit, 지원된 doctor/status/view 진단과 쓰기 부작용 부재 | S1/S2/S7; A5/A6/A10–A12/A15; 1/2/8 |
| V2 · path/identity | local NTFS existing/absent target·staging·backup, ancestor/reparse/remote/unknown 거절, case·reserved·trailing dot/space, 검사 후 drift | S3; A7/A10; 4 |
| V3 · lock | empty anchor, 두 writer의 직렬화·장기 대기, handle 비상속, Ctrl+C·강제 종료·재획득, anchor 교체/삭제·race 거절 | S4; A7; 3/6 |
| V4 · publication/flush | 필수·허용 unavailable phase별 실패 주입, read-only 교체/제거/필수 flush 파일 전체 사전 거절, 새 regular file clear, 실제 prefix 분류·보존 | S5/S6/S8; A7–A9/A12; 3/6 |
| V5 · window/readers | exact 29 membership·pairs, 두 windows-1 release P/Q의 update·rollback과 Q 기록의 P reader 해석, unknown window/pair 거절, 실제 노출 old-writer 발행 전 거절 | S2/S6; A5/A8/A9/A13; 5/6/9 |
| V6 · snapshots | tracked index mode + working bytes, 공개 100644 default, tracked actual absence, unknown/unmerged/type·특수 flag 처분, non-Git 과거 100755 기록 보존·non-pass | S6; A1/A3/A9; 5 |
| V7 · worker | tracked mode 유지·tracked add·eligible untracked의 성공, 기존 경로의 mode-changing result·새 untracked 100755·mixed result 전체 거절, index/HEAD/refs 불변, prepare/apply drift·pending cancellation·completed replay | S6; A2–A4; 5/6/8 |
| V8 · lifecycle | fresh Git/non-Git init, P→Q update·Q→P 직전 rollback, preview/apply/refusal, 전후 binding·inventory·artifact 검증, 기존 창 이주 거절 | S2/S5/S8; A5/A8/A9/A11; 2/5/6 |
| V9 · repair | mode 0/1 관측과 실행 before null/0·after 0, read-only가 남은 fresh preview 거절, 선택 조기 진단 non-pass 시 실행 request/token 없음, apply 필수 preflight, backup 불변·원 retry·새 preview·bound replay drift | S5/S6/S8; A8/A9/A12; 2/3/6 |
| V10 · detach | paired4 complete plan·내부 digest·remove/preserve inventory 검증, 제거 전/후 각 중단 prefix와 남은 bytes, inventory 제거 후 qualified reader, unknown/corrupt non-pass·재init 금지 | S2/S6/S8; A5/A8/A9/A14; 2/5/6 |
| V11 · environment/regression | 두 autocrlf 설정, CRLF·open handle, exact bytes/digest, normal·parent-optimized full Windows, shared code macOS 회귀, 필요한 x64/물리 focused 보완 | S1/S5–S8; A6/A13; 3/4/7/9 |
| V12 · claims/evidence | A1–A15 placement·기술 문서 11개·help/capability/entry parity, reading budget·fresh reader·shipped consumer 검증, 실제 tuple/미관측 표시, 개발·authenticated prerelease·anonymous evidence 구별 | S1/S7; A3/A4/A6/A10–A15; 8/10 |

Worker의 성공·거절 기대값은 base/result entry의 합집합과 각 경로의 post-mode 또는 부재를 독립적으로 판정한다. 기존 경로의 mode-changing result는 처음부터 미지원이며 “index가 일치하면 허용”으로 해석하지 않는다. 그 거절과 prepare 후 index/membership drift에 대한 stale 거절은 서로 다른 원인으로 확인한다. tracked add 등 예시에 없는 결과도 공통 조건을 만족하면 허용하며 예시에 있더라도 조건이 없으면 거절한다. 한 파일의 미지원이나 unknown을 부분 성공으로 축소하지 않는다. source/retained base/result·scope·physical 상태와 원참조 digest 검사는 유지한다. rename/move/copy도 실제 base/result와 destination 분류로 판단한다. 새 untracked 100755 destination은 거절하지만 rename이라는 이름 자체를 금지하지 않으며, 같은 mode의 tracked destination도 baseline·scope·physical guard를 모두 만족해야 한다. control index가 이미 result mode인 mode-changing 변형은 실제 도달 경로와 선행 stale/unsupported 원인을 기록한다. 특정 오류 label을 얻으려고 guard를 우회한 fixture를 만들지 않는다.

Repair의 선택 조기 진단은 fresh preview만을 대상으로 한다. 진단을 수행하지 않은 preview가 executable request를 만들더라도 apply의 필수 검사를 생략하지 않는다. 원 request의 mode 1을 새 의미로 고쳐 재시도하지 않으며, 외부 수정 뒤 새 preview는 새로운 관측·request identity를 사용한다. completed replay를 fresh preview와 동일하게 바꾸지 않는다.

### Minimum Case Coverage

| 근거 / 묶음 | 빠뜨리지 않을 최소 사례와 관측 |
| --- | --- |
| A3/A13 · V6/V7 | 안정된 tracked 100644/100755 내용 수정, eligible existing untracked 100644 수정·삭제, new untracked 100644 결과, 두 tracked mode의 실제 삭제, base와 안전하게 관측한 control namespace 양쪽에 없는 index-only tracked path의 동일 index-mode 추가. 예시 밖도 공통 조건과 모든 guard로 판단하며 닫힌 allowlist로 바꾸지 않음 |
| A3/A13 · V6/V7 거절·재개 | 기존 경로 mode 변경(control index가 이미 result mode인 변형 포함), rename/move/copy가 만드는 새 untracked 100755와 공통 조건을 만족하는 대조 결과, supported/unsupported 혼합의 whole-operation prepublication refusal. 원 ticket으로 중단된 worker accept apply는 지원 결과와 원 조건·모든 guard가 유지되면 exact 재개 성공(lifecycle --recover 아님), 조건 불충족/unknown이면 해당 stable non-pass, 다른 writer는 pending barrier로 거절. prepare 성공 뒤 index/membership drift→apply 거절, unknown 분류, index entry가 남은 실제 삭제·안전하게 확인할 수 없는 부재, retained provenance와 전체 결과 불일치. 거절 전후 decision·project content·index/HEAD/refs 보존 |
| A8/A9 · V5/V8 | init1/switch2/repair1/detach4 pair·binding·window 검증, fresh Git/non-Git·같은 창 update/직전 rollback·old/cross-window refusal, P/Q 양방향 local/worker/parent/planning 기록, pending/replay/cancellation. fresh clone/worktree의 실제 namespace와 truth 보존을 fixture로 확인 |
| A9 · V9 관측과 apply | missing/damaged launcher/member, 안전한 writable mode 0·read-only mode 1 관측과 invalid bool/other integer/unknown 거절, before null/0·after 0, byte/size/identity와 독립 completion. replace/remove/필수 write-capable flush 대상 전체 preflight, pure preserved/unlisted read-only의 별도 처분, 기존 backup request/original reflush 대상 |
| A9 · V9 중단과 재개 | backup 전/후·replacement 전/후 중단, attribute drift·replace/flush 실패, 원 backup/request/token의 exact recovery, completed replay 뒤 bound after attribute 0→1 non-pass, 외부 attribute 원복 뒤에도 모든 exact guard를 요구하는 원 retry eligibility |
| A9 · V9 fresh preview | read-only replacement target이 남으면 필수 non-pass·실행 request/token 없음. 허용 가능한 새 preview는 이전 외부 evidence를 보존하고 새 operation/request/token/backup을 사용하며 실제 pending·기존 guard는 계속 거절. 필수 flush 대상의 선택 조기 진단은 non-pass 시 token 없음; 조기 진단을 생략해도 apply preflight 필수 |
| A8/A14 · V10 | detached marker 발행 전 전체 remove set·필수 flush 파일의 read-only preflight, 첫 제거 전 detach4 durable publication과 remove/preserve 전체 검증, 파일·디렉터리 제거 순서의 모든 도달 가능한 prefix, 안전한 실제 부재/남은 suffix·보존 bytes, pair·내부 digest link·binding/launcher/release membership 검사, corrupt/unknown/mixed/out-of-order·unsafe occupant 거절. 역사적 detach 1/2/3 pair를 4로 재해석·재발행하지 않고 원 bytes/의미 보존 |
| A14/A13 · V10 reader | inventory/binding이 제거된 뒤에도 embedded complete plan과 실제 상태로 compatible qualified reader 검증. read-only에는 외부 원 plan/token을 강제하지 않고 mutation recovery에는 원 request/token/target 유지. old/unknown reader의 PASS는 증거가 아니며 필요한 proof는 non-pass. completed receipt는 새 init/attach 권한을 만들지 않음 |
| A13 · V2/V4/V11 | existing/absent target·staging·guard scratch·external backup·필수 flush 파일의 local NTFS, non-NTFS/remote/unknown 거절, volume identity drift·same-volume replacement와 다른 검증된 local NTFS volume의 backup 허용 구별. 새 파일 read-only clear, 사후 drift·실제 flush 실패와 operation별 중단 prefix |
| S4/A7 · V1/V3/V8 | 지원된 source/installed/retained doctor/status/view와 읽기 전용 replay·auditor에서 기대한 성공 또는 정확한 진단/거절. anchor 생성·재flush·authority/content 쓰기 없음. fresh/partial/detached는 해당 상태에서 제공되는 진입 경로만 시험하며 제거된 launcher 실행 성공을 요구하지 않음 |
| Maintaining · V8/V9/V10 | 합성 secret-sentinel과 scope 밖 canary의 exact bytes 보존, lifecycle round trip·refusal·중단/복구 후 확인. 실제 credential을 fixture로 읽거나 사용하는 검증은 하지 않음 |
| Maintaining/A15 · V12 | 최종 shipped 문서·adapter의 inventory와 installed/update/repair/detach 소비, 변경된 entry/resume 행동, 명령/help/capability/문서의 의미·제한·경로 일치. 고정 tokenizer 측정과 fresh-reader exercise를 각각 별도 증거로 남김 |

P1/P2에서는 V1–V12의 모든 필수 하위 사례와 최소 coverage를 기존/추가 test의 실제 ID에 대응시키고, 성공·예상 거절·보존·미검증을 구별하는 독립 oracle과 mode·명령·결과 위치를 기존 ledger에 연결한다. unittest 밖의 native exercise는 runner가 부여한 exercise ID, 실행 argv·stdin/file 입력 identity와 transcript를 같은 기록에 연결한다. lock의 각 중단/회수 사례, PS5.1 입력, CRLF·autocrlf 두 설정과 A12의 실패 범주도 이 의무에 포함된다. P3의 문서/reader 사례까지 해당 실행 전에 대응을 완성하며, ID를 지금 만들어 실행한 것처럼 쓰거나 새 registry를 만들지 않는다. 같은 test가 여러 항목을 입증할 수 있지만 record parse·도달 불가능한 fixture·mocked 성공만으로 native 의무를 닫지 않는다. 실제 filesystem 사례와 정해진 phase의 fault injection을 구별하며 후자는 native admission을 대신하지 않는다. 문서 정합성 검사만으로 제품 test가 통과했다고 쓰지 않는다.

P3의 reading budget은 현행 Maintaining대로 `tiktoken==0.13.0`, `o200k_base`, `AGENTS.md` 2,000 tokens 이하, `AGENTS.md + README.md + docs/GETTING-STARTED.md` 4,000 tokens 이하·필수 읽기 세 파일이다. exact 파일·도구·count를 기록하고 제품 runtime dependency로 추가하지 않는다. fresh-reader exercise는 이 수치와 별개로 Windows 진입·verified view/manual·첫 작업과 재개 경로를 실제로 따라가는 검증이다. 합성 fixture의 writer 동작은 승인된 실행 경계 안에서만 한다. P0에서 기존 고정 tokenizer 환경·의존성과 인코딩 자료의 가용성을 확인하고 exact 실행 경로와 입력을 기록한다. 설치·자료 반입·network가 필요하면 필요한 변경만 명시 승인하며, 미확보 상태를 token-budget PASS로 쓰지 않는다. fresh-reader의 수행자(human 또는 명시 승인된 agent), 수단과 전달 문서·합성 데이터 범위도 실행 입력에 둔다. agent를 쓸 경우 기존 인증/billing·disclosure 확인을 적용하고, 이 계획만으로 새 호출 권한을 얻지 않는다.

### Refusal Fixtures And Environment Availability

P0에서 필요한 fixture의 생성·읽기·회수 방법과 실제 권한을 확인한다. 표준 사용자 경계에서 준비할 수 있는지와 추가 환경이 필요한지를 구별하며, 아래 표는 환경이 이미 확보됐다는 주장이 아니다.

| Fixture 묶음 | 준비와 증거 경계 |
| --- | --- |
| local NTFS·read-only·open handle·CRLF/case/name | guest task root의 합성 existing/absent 파일·staging·guard scratch·backup과 두 autocrlf 설정. 원 bytes·attribute·volume/file identity를 독립 관측 |
| reparse·alias·non-NTFS·remote | 이미 승인된 경계 안에서 실제로 도달 가능한 거절 경로를 선택. non-NTFS·remote·unknown 등 각 필수 범주는 자체 관측 또는 unavailable로 개별 처분하며 서로 대체하지 않음. 필요한 권한·도구·mount/share가 없으면 공백을 남기고 mock/문자열 검사로 native observation 증거를 대체하지 않음 |
| volume drift·다른 volume의 backup | 실제 관측 경로와 phase별 fault injection의 범위를 구분. 검증된 다른 local NTFS volume의 backup을 같은-volume 규칙으로 거절하지 않는 사례를 계획하되 새 volume/share 생성 방법을 계약 의무로 만들지 않음 |
| 읽기 불가·unknown·중단 prefix | 필요한 오류를 낼 수 있는 합성 fixture와 주입 지점을 고정하고 원 오류·prefix·보존 내용을 기록. 접근 불가를 삭제로 해석하지 않음 |
| runtime 거절 | OS/process 불일치·x64-on-ARM64 emulation·32-bit·허용 밖 CPython patch/prerelease/free-threaded·POSIX 호환 runtime 등 계약상 거절 유형과 실제 필요한 관측을 연결. 기존 interpreter/fixture 가용성은 현재 미확인이며 P0에서 exact identity·도달 경로를 확인. 모든 비지원 runtime을 미리 설치하는 matrix는 요구하지 않음 |

관리자 권한, network/share·clipboard 개방, 새 volume이나 runtime 설치는 이 계획 작성 또는 일반적인 제품 검증의 묵시적 권한이 아니다. 승인된 경계 안에 fixture가 없으면 해당 필수 증거와 qualification은 미완료로 남기고, 필요한 최소 환경 조정만 제시한다. 추가 runtime 반입이 실제로 필요하면 exact installer/package identity·반입/설치 방법·권한·network 사용 여부와 회수 경계를 승인 대상에 포함한다. 기존 경계 안의 가용성 확인은 P0에서 진행할 수 있다. runtime 거절의 mock/fault injection 증거와 실제 native 관측을 구별하며 필수 관측의 공백은 남긴다. 비지원 runtime의 read 경로는 제공되는 진단/거절과 무쓰기 여부를 확인하며 모든 명령의 성공을 요구하지 않는다. 모든 역사적 writer·교차 OS 경로·물리 장비를 새 필수 matrix로 확장하지 않는다.

## Runner, Bounds And Evidence

실제 실행 전 P0에서 VM identity·guest task root·Python 절대 경로·source preparation·환경변수·자식 실행과 회수 방법을 고정한다. VM과 guest의 합성 데이터 범위가 승인된 실행 경계이며, 단순 worktree나 Windows Job Object를 filesystem sandbox라고 부르지 않는다. 개인 계정·자격증명·실제 adopter가 없는 경계를 확인하고 network·host share·clipboard·host write 접근을 제한·관측한다. 더 좁은 path 쓰기 제한을 요구하면서 이를 집행할 수 없다면 실행 전에 그 한계를 보고한다.

입력·스크립트·로그·ID ledger와 필요한 failure prefix는 task의 durable root에 둔다. P0에서 base commit과 exact diff, 필요한 untracked bytes·file mode·runner/policy·prepared payload를 회수 가능한 형태로 고정한다. digest만 남기거나 mutable checkout만 가리키지 않으며, 이미 있는 immutable evidence를 또 복제하지 않는다. 이 보존은 local commit 권한을 뜻하지 않는다.

Guest에서 나온 필수 로그·prefix·input identity는 실행 중 durable guest 경로에 기록하고, checkpoint·중단/restore 전에 지정 host durable 경로로 반출한다. P0에서 실행 중 share/network/clipboard 차단과 양립하는 정확한 전송 수단·허용 시점·path를 고정하고 합성 파일로 확인한다. 실행을 끝내고 child 부재를 확인한 뒤 허용된 전달 경로를 잠시 사용하는 안도 별도 통제 대상으로 평가한다. 공유를 임의로 열거나 회수 전에 VM을 rollback하지 않는다. host 복사본의 bytes/size·회수에 필요한 metadata를 guest 원본과 대조하고 readable함을 확인한 뒤에만 원본 수명·restore를 판단한다. 반출 수단이나 복구 입력이 없으면 영향을 받는 제품 실행을 시작하지 않는다. 도구가 지원하면 per-process TEMP를 같은 task 경계로 지정한다. 실행 중인 파일과 기존 VM recovery를 이동·정리하지 않는다. 기존 backup의 bytes 보존과 restore boot 실측은 별개이며 이전 backup만으로 새 복구 검증이 끝났다고 기록하지 않는다.

개발 반복과 증거 실행은 한도를 다르게 적용한다. 개발 반복은 P1/P2의 구현·진단·focused test와 변경 중의 collection, P3의 문서·준비 도구 보완이다. 각 반복을 세 번으로 제한하지 않고 아래 단계별 누적 시간 안에서 진행한다. 반복 실행 하나는 20분 이하로 두며, 실패 후에는 원인 가설·수정 또는 다음 관측 목적을 남긴다. 개발 중 관측은 단계 선행 조건을 확인하는 데 쓰되 최종 candidate의 qualification PASS로 자동 이월하지 않는다.

증거 실행은 입력을 고정한 통제 canary와 최종 candidate의 collection·focused·full 검증이다. 각 실행 동안 source/tests/runner/policy를 고정하고 아래 회당·횟수 한도를 적용한다. 원인과 수정이 있는 후속 candidate를 검증하더라도 이미 쓴 시도를 지우지 않는다. 초기 candidate 증거의 재사용은 Maintaining의 exact 입력·누적 위험 대조를 따른다.

| 증거 실행 단위 | 계획한 상한과 완료 판정 |
| --- | --- |
| 통제 canary | Windows/macOS 각 실행 경계에서 회당 10분·초회 1회 + 근거 있는 보정 뒤 재검증 1회. child 회수·외부 canary·쓰기/network 경계와 종료 상태 확인. 안전 경계 위반은 재시도 한도와 무관하게 중단 |
| 최종 suite collection | OS/mode별 회당 10분·초회 1회 + 수정 뒤 2회 이내. 실제 import/discovery ordered ID 저장; AST·과거 개수로 대체하지 않음 |
| 최종 focused batch | 사전 열거한 OS·묶음별 회당 20분·초회 1회 + 원인/수정이 있는 2회 이내. P1/P2의 개발 반복에는 이 횟수를 적용하지 않음 |
| full suite | Windows와 macOS 모두 OS/mode별 회당 예비 ceiling 120분, 초회 1회 + 원인·수정·위험 근거가 있는 전체 재실행 1회 이내. 실제 budget은 native 근거와 여유로 실행 전에 이 상한 이하에서 고정 |
| 중단·회수 | controller deadline과 제품 lock의 timeout 없는 대기를 구별. 자연 완료·deadline·강제 회수·미회수 process를 별도 결과로 기록 |

단계별 누적 상한도 승인 검토용으로 제안한다. 여기서 시간은 날짜가 지난 시간이 아니라 기록된 활성 작업 구간의 wall time 합이며 구현·분석·test/controller 실행·필요한 결과 보존을 포함한다. 작업과 child 실행이 모두 멈춘 대기만 제외한다. 같은 단계의 병행 구간을 중복 계산하지 않되 각 실행의 회당 시간·횟수는 따로 집계한다. 별도 시간 registry 대신 기존 진행 기록과 runner ledger에 사용량·잔여량을 남긴다.

| 단계 | 누적 예비 상한 | 포함하는 활동 |
| --- | --- | --- |
| P0 | 2시간 | 통제·가용성·복구/반출 확인, canary와 실행 입력 고정 |
| P1 | 8시간 | native 기반·시험 진입·첫 candidate 개발, 반복 collection/focused 확인 |
| P2 | 12시간 | lifecycle·worker 구현, 반복 focused 확인·실패 분석·수정 |
| P3 | 4시간 | 문서/reader·tokenizer·준비 변환 확인과 final freeze |
| P4 | 12시간 | 두 OS의 최종 증거 실행, R1 준비·검토·Driver 처분, R1 이후를 포함한 승인 범위 내 보정·재검증과 개발 결과 closeout |
| 중단·보존 여유 | 2시간 | 정지 조건이나 한도 도달 후 child 회수·증거 보존·복구 판단 전용. 통상 보존은 각 단계 시간에 포함하며 이 여유로 구현·검증을 연장하거나 재개하지 않음 |
| 전체 | 40시간 | 위 상한의 합. publication·activation·adopter 작업은 포함하지 않음 |

이 숫자는 예상 소요 시간이나 측정 결과가 아니라 실행 승인에 제시할 자원 상한이다. 회당 시간·시도 횟수·단계 누적·전체 누적 중 먼저 도달하는 한도를 적용한다. 따라서 모든 허용 재시도 슬롯을 반드시 사용할 수 있다는 뜻은 아니다. P4 또는 Closeout/R1 처분 뒤 source·test·runner 보정을 위해 앞 단계로 돌아가도 수정·재검증 시간은 P4에 포함하고 기존 증거 시도를 이어 센다. R1 준비·검토·처분과 개발 결과 정리도 P4/전체 한도에 포함하며 Closeout이 별도 예산을 만들지 않는다. Source/control revision·batch 이름·세션·단계명을 바꾸거나 개발 반복으로 다시 분류해 예산을 초기화하지 않는다.

R1은 Owner relay 또는 명시 승인된 CLI로 진행한다. 일반 구현 승인만으로 reviewer 호출이 허용되지는 않는다. CLI를 선택하면 reviewer·인증/billing 경로·전달 범위와 no-tools 여부, 후속 라운드를 포함한 호출 횟수·회당 시간 상한을 같은 실행 승인에 명시한다. 이 값이 정해지지 않으면 호출하지 않는다. 승인된 후속 라운드와 입력 변경은 매번 재승인하지 않되 각 회의 exact 입력·disclosure·인증과 전후 drift를 확인한다. 호출과 후속 처분도 P4 잔여 시간 안에서 진행하며, 횟수·시간 또는 전달/실행 범위를 넓히는 호출은 자동 허용하지 않는다. 현재 계획 보완과 이전 R0 호출 승인은 미래 R1·fresh-reader 호출 승인이 아니다.

P0는 이 상한 이하의 단계 예산과 증거 묶음 범위를 고정하며, P1/P2 측정으로 각 증거 실행의 실제 budget을 더 좁힌다. phase 간 시간을 옮겨 어느 상한을 높이거나 전체를 확대하려면 필요한 조정만 결정한다. 한도 안의 ordinary correction마다 새 승인을 요구하지 않는다. 제품의 자동 replace retry는 여전히 0회다.

첫 full suite의 budget은 각 OS에서 측정한 collection/focused 비용·실제 test 수·spawn/중단 사례 비용을 바탕으로 예상 전체 시간과 여유를 명시해 실행 전에 확정한다. 이는 native 구성요소 실측에 근거한 추정이며 첫 full 전에 별도 full 실측을 요구하지 않는다. macOS의 검증 가능한 native anchor도 해당 입력의 적용성을 확인한 경우에만 보조 근거로 쓴다. 이 근거가 예비 ceiling 안의 충분한 budget을 뒷받침하지 못하면 전체 실행 전 조정안을 제시한다. 시도 사이 budget을 조정할 때도 원 실패·새 근거를 기록하고 회당 120분 ceiling·P4/전체 잔여 시간·기존 시도 한도를 모두 지킨다. timeout만으로 자동 증액하거나 시험 도중 한도를 올리지 않으며 모든 child timeout을 일괄 치환하지 않는다. 기존 6-family probe 시간이나 과거 macOS suite 시간을 Windows 예측값으로 쓰지 않는다. 한도 초과는 incomplete/non-pass로 남기고 현재 상태·핵심 로그를 보존한다. 로그가 조용하다는 이유만으로 hang을 확정하지 않는다. 동일 실패를 무한 재실행하지 않으며 원인·수정·재실행 범위가 있는 경우에만 승인된 한도 안에서 반복한다.

실행할 suite의 기본 형태는 현재 Maintaining을 따른다. 아래는 실행하지 않은 template이며, 고정된 runner가 CWD·source import 경로와 no-bytecode 환경을 설정한 뒤 호출한다.

```text
<qualified-python> -B -m unittest discover -s tests -v
<qualified-python> -B -O -m unittest discover -s tests -v
```

두 번째는 parent-optimized 실행이다. 자식 Python까지 자동으로 optimized가 된다는 주장을 하지 않는다. 실제 자식 argv와 검증 의도를 기록한다. 제품 launcher 자체의 isolated/no-bytecode admission은 suite runner 설정과 별도로 검사한다.

증거에는 source/tests/runner identity, 환경 tuple, ordered discovery ID, 실제 시작·종료 ID와 상태, 총수·누락·skip·실패·시간·exit·child 회수를 남긴다. import 실패·collection timeout·누락을 0 tests PASS로 처리하지 않는다. 실패 전 마지막 durable checkpoint와 controller의 종료 경로를 분리한다. 통제·test oracle·runner가 바뀌면 영향을 받는 증거를 다시 판정한다.

### macOS Runner Boundary

macOS 회귀도 Windows와 같은 수준으로 입력·policy·통제 결과를 기록한다. 정확한 final GIL-enabled CPython executable/version/digest와 child identity, cwd·env, 쓰기 허용 root·network denial·credential 부재, process-group 회수와 ID ledger를 고정한다. 기존 runner/policy를 재사용할 수 있으면 현재 입력에 대한 적용성과 외부 write/network canary를 확인하고 그대로 활용한다. worktree만으로 격리됐다고 하지 않는다.

Maintaining에 있는 과거 `/dev/fd` 원인 분석과 424-ID 시간은 역사적 설명이다. 당시 exact evidence를 회수해 비교하지 않고 현재 정책·예산으로 복사하지 않는다. 새 macOS budget은 현재 focused/collection 관측과 확인 가능한 native anchor에 여유를 더해 정하고, 자연 완료와 강제 회수 후 process 부재를 구분한다. normal과 parent-optimized 전체 회귀를 계획하며 실제 child argv를 함께 기록한다.

## Regression And Reuse

이번 구현은 shared writer·snapshot·lifecycle을 바꾸므로 macOS에서는 관련 focused 검증과 normal·parent-optimized 전체 회귀를 계획한다. 기존 macOS PASS를 새 변경의 무조건 anchor로 쓰지 않는다. [Maintaining의 evidence reuse](../MAINTAINING.md#evidence-reuse-and-selection)에 따라 exact 변경 영향·입력 identity·남은 누적 위험을 비교해 재사용 여부를 기록한다.

대표 Windows 전체 검증과 x64/물리 focused 보완은 B의 배정을 유지한다. 후자의 필요 여부와 사례는 architecture/ABI·filesystem·shell 등 실제 메커니즘 차이로 결정한다. 모든 조합의 full matrix나 물리 PC 보유를 새로운 공통 gate로 만들지 않는다. 추가 tuple을 주장하려면 그 범위의 실제 증거가 필요하다. 초기 x64 focused 후보는 Win32 ABI/구조체·pointer 크기·last-error 전달, lock 대기/취소·handle lifetime, replace sharing violation·required flush, native argv/stdin/exit다. 물리 장비는 VM과 차이가 나는 filesystem/handle/중단 경계를 우선 살핀다. 실제 차이와 이용 가능한 환경에 따라 선택하고 미관측 항목은 그대로 표시한다. 추가 환경을 실제 사용할 때만 해당 환경의 통제·회수 가능한 입력·증거 반출·canary와 시간 귀속을 고정하며, P4에서 추가 준비하면 P4 시간에 포함한다. 물리 장비에 VM snapshot을 요구하지 않고 실제 환경에 맞는 복구·격리 경계를 확인한다. 새 장비 확보 자체를 gate로 만들지 않는다.

### Shared Shipped Documents And Preview

A15와 help/capability 등 shared managed 문서를 바꾸면 macOS payload/release identity도 달라질 수 있다. 현재 Windows 격리 작업 경로에서 source와 prepared artifacts를 관리하고, 다른 macOS Preview 후보에 자동 통합하지 않는다. 새 worktree를 필수로 만들거나 기존 Preview 결과를 이 후보의 PASS로 옮기지 않는다. 통합이 나중에 선택되면 누적 변경 영향과 새 inventory·lifecycle·entry/resume 소비를 검증한다.

A15의 “For a qualified windows-1 target”은 조건부 사용 안내다. 문서 freeze 때 아직 없는 qualified tuple을 만들어 쓰지 않고, 실제 tuple·artifact·미관측 범위는 결과/지원 표시의 exact 대상과 연결한다. qualification 뒤 shipped 설명을 다시 바꾸면 새 artifact identity와 Maintaining의 관련 재검증이 필요하지만, 조건부 정책 문구 자체를 고치기 위해 qualification을 무한 반복하는 절차를 만들지 않는다.

## Completion, Stop And Retention

개발 결과 수락과 전체 admission 완료는 다음처럼 구별한다. 아래 후속 항목이 남은 상태에서 개발 결과를 수락할 수는 있지만, 미완료 항목을 PASS나 발효로 바꾸지 않는다. “개발 범위”라는 표현으로 필수 관측의 공백을 제외하지 않고 해당 criterion의 잔여 항목으로 제시한다.

| 결과 경계 | 필요한 증거·결정 |
| --- | --- |
| 개발 구현·검증 결과 | 수락 계약을 구현한 exact source/prepared source/local artifact·문서 parity, V1–V12의 필수 사례별 실제 실행·식별된 상속·미확보/미해결 결과, old-writer 노출 처분, Windows·macOS 결과, R1/Driver 처분과 Owner 결과 수락. 계획 작성·정적 검사만으로 완료 불가 |
| 배포 artifact 검증 | 명시 승인된 publication 대상·artifact bytes와 published/refetched equality, authenticated prerelease 검증 및 criterion 10의 anonymous evidence 구별. 미승인/미실행이면 후속 미완료로 표시하고 source/local artifact equality로 대신하지 않음 |
| 기술 activation | activation 대상 exact source/artifact·문서 revision·환경에 대해 A13 qualification 전체 완료가 선행 조건이며 그 artifact의 source/artifact/published/refetched equality도 포함. 필수 관측·old-writer 거절·qualification 누락을 남긴 activation은 불가. 그 근거에 대한 별도 Owner activation 기록으로 발효하며 현재 entry-1/First B1을 계획 승인만으로 교체하지 않음 |
| Windows formal admission | live macOS Preview 이후의 별도 Owner 결정과 10개 기준의 실제 충족. 개발 결과·계약 수락·일부 native PASS만으로 formal 지원 선언 불가 |

Criterion 10의 authenticated prerelease와 anonymous public evidence는 각각 실제 전달 경로·대상 identity로 구별한다. published/refetched equality가 있더라도 anonymous evidence가 자동 확보된 것은 아니며, 전체 10개 기준과 live macOS Preview 이후라는 formal admission의 시점은 그대로 유지한다.

P3의 “기술 계약 11개 문서”는 DR-0002가 식별한 현행 entry-1/First B1 기술 계약 집합을 말한다. 이것은 Python 11 modules, managed 29 paths, A1–A15의 15개 amendment/각 placement와 서로 다른 집합이다. 구현 때 현행 기술 문서 identity에 A1–A15의 exact diff를 연결하고, 과거 11-document table의 hash를 현재값으로 재사용하지 않는다. 실행 완료가 public 지원 선언이나 Git/adopter action을 자동 승인하지 않는다.

다음 상황에서는 영향을 받는 실행을 멈춘다: source/control drift, 경계 밖 mutation, recovery 입력 손실, known exposed old writer의 발행 또는 거절 미확인, required flush/identity/prefix unknown, whole-result 불일치, 정한 시간/시도 상한 초과. 계약으로 설명되지 않는 상태나 새 field/schema/membership이 필요하면 먼저 exact 변경안과 영향 범위를 제시한다. 실패·미관측을 unsupported label로 바꿔 통과시키지 않는다.

현재 source worktree와 수락한 v0.10 frozen packet, probe/리뷰 근거 및 마지막 VM recovery는 각각 계획 검토·계약 재현·실측 비교·복구 소비자가 남아 있다. 계약 수락만으로 probe 결과 수락이나 VM 복구·삭제가 승인된 것은 아니다. 이후 단계 완료 때 재사용·복구·Owner 수락 조건을 다시 확인하고 불필요한 일회성 파일만 standing cleanup 조건에 따라 정리한다. 마지막 필요한 evidence와 unique deliverable은 보존한다.

현재 다음 검토 대상은 지적 반영 후의 v0.4와 실행 범위다. 이 수정으로 R0-I01–I03의 conditional을 approve로 바꾸거나 새 리뷰를 수행한 것으로 쓰지 않는다. 계획 보완에서 멈추며 추가 실험·제품 구현·reviewer/VM 실행을 자동 시작하지 않는다.

## Revision 0.2 Response Map

이 표는 계획 문안에 반영한 위치를 찾는 용도다. Reviewer 원문과 Driver 처분은 기존 CHORE의 R0-I01 기록을 그대로 유지한다.

| 지적 | 반영 위치와 채택 범위 |
| --- | --- |
| F1 | Platform Tests And Early Writer Checks: 실제 import/discovery·platform 기대값·Windows 대응 사례. 전체 ID용 registry는 만들지 않음 |
| F2 | Delivery Stages / Candidate And Flush Prerequisites: 첫 init 전 prepared candidate, 첫 switch/reader 전 P/Q, P1 phase별 flush 대응, P3 최종 freeze |
| F3 | Platform Tests And Early Writer Checks: 실제 writer×접근 경로·family와 fresh/incomplete init부터 조기 거절. 모든 역사 경로 회수는 요구하지 않음 |
| F4 | V1 / Minimum Case Coverage: doctor/status/view와 지원 read-only 경로의 진단·무쓰기 확인. 제거된 launcher 성공을 새 지원으로 만들지 않음 |
| F5 | V7 / Worker 설명 / Minimum Case Coverage: mode-changing result 거절과 prepare/apply drift 구별. 공통 조건과 기존 guard 유지 |
| F6 | Minimum Case Coverage: A3/A8/A9/A13/A14와 실제 test ID 연결을 실행 선행 입력으로 지정 |
| F7 | Refusal Fixtures And Environment Availability: 실제 fixture·권한·unavailable 처분. 새 volume/share·관리자 권한을 필수화하거나 자동 승인하지 않음 |
| F8 | macOS Runner Boundary / Runner 표: runtime·policy·canary·child·ledger·native 근거/예산. 검증 가능한 기존 통제 재사용 |
| F9 | Shared Shipped Documents And Preview: 기존 격리 경로, Preview 자동 통합 금지, shared bytes·후속 shipped prose의 영향 검증 |
| F10 | Runner, Bounds And Evidence: recoverable base+diff/필요한 bytes, guest→host 검증·restore 전 보존. local commit·share 개방은 별도 권한 |
| F11 | Regression And Reuse: x64/물리 focused 초기 후보. full matrix·환경 보유 gate로 확대하지 않음 |
| F12 | Fixed Scope / P3 / Completion: 원 수락 identity, 집합 구별, P/Q 증거 범위, 개발·published/refetched·activation·formal admission 구별 |
| F13 | Outcome And Authority / Runner 표: 한 번의 bounded 실행 승인, 시간·시도 초기안과 누적 한도. Reviewer의 재시도 예시를 계약으로 채택하지 않음 |
| D1 | P3 / Minimum Case Coverage / V12: sentinel 불변, shipped 소비·entry/resume, 고정 reading budget과 fresh-reader exercise |


## Revision 0.3 Response Map

R0-I02 원문과 Driver 처분은 [기존 CHORE 기록](CHORE-20261017-001-windows-utm-feasibility-probe.md#r0-i02--implementation-plan-v02-re-review-and-driver-judgment--2026-10-18)에 보존한다. 아래는 문안 반영 위치이며 Reviewer의 재판정이나 실행 승인이 아니다.

| 지적 | 반영 위치와 채택 범위 |
| --- | --- |
| F1 | Runner, Bounds And Evidence: 개발 반복은 단계 시간, 고정 후보 증거는 회당·횟수로 구별. 양 OS full 회당 120분, 단계 합계 40시간을 승인용 예비 상한으로 제안. 측정값이나 자동 실행 권한은 아님 |
| F2 | Verification Matrix / Minimum Case Coverage: V1–V12 전체 하위 필수 사례와 test/exercise ID·mode·argv·입력·독립 oracle·transcript/결과 연결. 기존 ledger 사용 |
| F3 | Refusal Fixtures And Environment Availability: runtime 거절 유형·기존 가용성·추가 반입이 필요한 경우의 exact 입력/경계·미완료 처분. 모든 unsupported runtime 설치와 모든 read 명령 성공은 요구하지 않음 |
| F4 | Outcome / Delivery Stages / Completion: P4는 통합 검증 일부, activation은 published/refetched equality를 포함한 A13 전체 완료 뒤 별도 Owner 기록. criterion 10과 formal admission 시점 유지 |
| F5 | Platform Tests And Early Writer Checks: 사전 비적용 ID·근거 고정과 별도 집계, PASS 합산·사후 skip 재분류 금지. 필수 Windows 사례는 제외 불가 |
| F6 | Worker 설명 / Minimum Case Coverage: rename/mode 변형·원 ticket 재개/pending, detach marker 전 preflight·역사 pair 보존. 실제 공통 조건/guard를 유지하고 특정 오류 label을 강제하지 않음 |
| F7 | Reading budget 문단: tokenizer 의존성/인코딩 자료와 human/agent 수행자·전달 범위의 실행 입력화. 기존 가용성부터 확인하고 필요한 설치/network/agent 권한만 따로 확인 |
| F8 | P1 완료 근거: 독립 probe 통과를 제품 통합 PASS로 재사용하지 않는 문장 복원 |
| F9 | Candidate And Flush Prerequisites: 첫 candidate 전 변환 목록/bytes, P3에서 P/Q activation 후보와 시험 전용 역할. 변환을 launcher 한 줄이나 새 계약으로 임의 고정하지 않음 |

## Revision 0.4 Response Map

R0-I03 원문과 Driver 처분은 [기존 CHORE 기록](CHORE-20261017-001-windows-utm-feasibility-probe.md#r0-i03--implementation-plan-v03-re-review-and-driver-judgment--2026-10-18)에 보존한다. F1/F2는 집행 규칙, F3–F6은 필요한 설명으로 좁혀 반영했다. 계약 amendment나 새 실행 승인이 아니다.

| 지적 | 반영 위치와 채택 범위 |
| --- | --- |
| F1 | Platform Tests And Early Writer Checks: 양 OS import-safe·사전 비적용 규칙과 각 OS 필수 사례 제외 금지. 실제 실패를 재현한 주장 없음 |
| F2 | Runner, Bounds And Evidence: R1·Closeout 및 이후 수정·재검증을 P4/전체 시간과 기존 증거 시도에 귀속. CLI는 한 번의 명시된 호출 범위·횟수·시간 승인 안에서만 진행 |
| F3 | Regression And Reuse: 추가 환경을 실제 사용할 때 통제·복구·반출·canary 입력 고정. P4의 추가 준비는 P4 시간, 물리 장비 보유·VM snapshot gate 없음 |
| F4 | Refusal Fixtures / Completion: 필수 거절 범주별 자체 관측 또는 unavailable, 실행·상속·잔여 결과 구별. 필수 공백을 scope 문구로 삭제하지 않음 |
| F5 | Runner, Bounds And Evidence: 통상 보존과 정지 후 2시간 여유 구별, 첫 full은 native 구성요소 측정에 근거한 추정. 시도 사이 재산정도 기존 상한·잔여·시도 안에서만 허용 |
| F6 | Minimum Case Coverage: 원 ticket worker exact 재개 성공·조건 불충족/unknown non-pass·다른 writer pending 거절을 분리. 공통 조건과 whole-result 의미 유지 |

## Integration Amendment — 2026-10-22

이 문서의 v0.4와 기존 Windows-1 실행 계획·근거는 원 이력으로 보존한다. Owner가 2026-10-22에 수락한 [DR-0007 Windows Integration Amendment 01](../decisions/DR-0007-windows-native-runtime-contract.md#windows-integration-amendment-01--accepted-2026-10-22)이 다음 통합 후보의 window·membership·lifecycle pair를 대체한다. 실제 anchor와 exact proposal SHA는 DR의 수락 기록을 따른다.

최신 위임·lifecycle 관측 보정·U1을 pinned main `7d012f5297de1d9a77aa0b8187406f4785221573`에서 통합한다. 공통 source는 continuation-1/schema5를 유지하며, 명시 준비된 Windows source는 windows-2/30 managed files/12 Python modules와 모든 lifecycle action의 schema6 pair를 사용한다. Windows-1·기타 이전 window·cross-OS migration은 추가하지 않는다. 기존 B안, 공통 조건 worker 범위, native NTFS·읽기 전용·flush·원 복구 입력·권한 경계는 유지한다.

Windows-1 결과는 원 입력의 근거로만 재사용한다. 통합 단계는 Mac 집중 검사, 역방향 old-writer portable 거부, Q에서 만든 continuation 기록의 P 읽기, 문서와 명시 preparation bytes 확인 후 source를 동결한다. 새 후보의 native Win32/repair·모든 노출 writer family·normal/parent-optimized 최종 행렬, R1·Owner 결과 수락·qualification·activation은 각각 남은 단계다. 이번 Mac 보정 승인으로 그 실행·수락을 시작하지 않는다. native 재개 시 개발 채널의 source·deadline을 새로 결속하고, no-share qualification과 개발 실행을 구별한다. 기존 queue 사용량은 초기화하지 않는다.

진행·검사별 근거 재사용·남은 의무는 [기존 구현 Work](FEAT-20261018-003-windows-native-implementation.md)가 단독 소유한다. 이 amendment는 별도 tracker나 새 검증 상한을 만들지 않는다.


## Windows Verification Amendment 02 — Execution Allocation

2026-10-28 Owner가 [DR-0007 Amendment 02](../decisions/DR-0007-windows-native-runtime-contract.md#windows-verification-amendment-02--accepted-2026-10-28)를 수락·발효했다. 이번 Work의 지정 후보·환경에 한해 P4와 V11의 normal/parent-optimized 전체 반복 요구를 source-aware normal 전체 누적 대사와 고정 parent-optimized 133개 ID 및 네 종류 실제 mode 경계 확인으로 바꾼다. 그중 final P/Q 6개는 같은 고정 artifact의 최종 호환성 근거로 함께 사용한다. 원 계획은 당시의 범위로 보존한다.

나머지 V1–V12·old-writer·qualified reader·중단/경쟁/복구·exact artifact·macOS 누적 영향 의무와 별도 결과 수락/admission 경계는 유지한다. 누적 source/fixture/oracle/runner 차이를 설명하지 못하면 재사용을 확정하지 않는다. Maintaining의 개정 절은 대체 근거가 무효가 되는 조건을 정한다. 현재 선택과 실행/회수·실패 원문은 기존 Work가 소유하며, 검사 PASS만으로 Work Done을 선언하지 않는다.
