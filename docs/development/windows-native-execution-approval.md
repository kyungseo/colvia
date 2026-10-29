# Windows Native Execution Approval Proposal

Revision: 0.2
Date: 2026-10-18 (KST)
State: Proposed; execution not approved
Basis: [Implementation Plan v0.4](windows-native-implementation-plan.md)
Review basis: [R0-A01 on v0.1 and Driver dispositions](CHORE-20261017-001-windows-utm-feasibility-probe.md#r0-a01--execution-approval-proposal-review-and-driver-judgment--2026-10-18)
Contract: [DR-0007 v0.10 acceptance](../decisions/DR-0007-windows-native-runtime-contract.md#owner-contract-acceptance--2026-10-18)

## Decision Requested

v0.4의 P0–P4 구현·검증과 R1 처분을 아래 환경·호출·시간·중단 경계 안에서 한 번 승인받는 제안이다. 승인되면 Driver가 단계 안의 입력 구체화, 통제 준비, 구현, 필요한 검증과 원인 있는 보정을 진행한다. 승인 범위 안의 단계 이동·실행 매개변수 구체화·후속 packet 변경마다 다시 승인을 받지 않는다. 아직 실행 승인은 기록되지 않았으며 이 문서 작성은 실행을 시작하지 않는다.

R0-I04는 v0.4를 approve로 판단했고 필수 수정은 없었다. v0.2는 그 계획의 선택 입력을 정한 v0.1에 R0-A01 F1·F2와 Driver 처분을 반영한다. 기존 콘솔 제어·반복 운영과 외부 packet의 비식별화 규칙을 명시했으며, v0.2의 추가 리뷰와 실행 승인은 아직 없다. DR-0007 v0.10·B안·공통 조건 중심 worker 지원, 29 managed paths·11 Python modules와 원 ticket·whole-result·기존 guard를 유지한다. 계약 의미·지원·신뢰 경계 변경은 포함하지 않는다.

승인 대상은 이 문서 v0.2와 Owner가 보관하는 Local Execution Bindings v0.2의 결합이다. 전자는 범위와 한도, 후자는 실제 host/guest 경로·VM·runtime 식별값을 맡는다. private 경로는 source 문서나 외부 reviewer packet에 복사하지 않는다.

| 고정 근거 | Identity |
| --- | --- |
| Source baseline | `a93f71c359c4f0a9d57fcfb50d5999160e870f77` |
| 계획 v0.4 | 60,560 bytes; SHA-256 `d522f2c6039eb837c65917c198f0e868c163839f011248f51e92be85eebb2ffc` |
| 수락 metadata 포함 DR v0.10 | 181,284 bytes; SHA-256 `e7679a8e11b5e38171888ab6da748cabd6ad5e46dc84e48205733a8e0e6d9ede` |
| R0-I04 final | 18,254 bytes; SHA-256 `2bdc872f914557356ba70b65706b653b38ace7c94612d76df26fdee0736b124e` |
| R0-A01 final on v0.1 | 16,775 bytes; SHA-256 `690ae9242e2919f3e4aa8c732bcf59359795470e44fe142278c18074195827db` |

## Scope And Ownership

승인할 제품 범위는 v0.4 Source Change Map과 V1–V12다. native Windows 기반, lifecycle/content/worker, prepared Windows source·P/Q candidate, 관련 test·runner·독립 oracle, A1–A15 문서/help/capability 정렬을 포함한다. 기존 macOS 동작과 기본 entry-1 준비 경로를 보존한다. 새 managed module·제품 dependency·.cmd launcher·old/cross-window 이주·cross-OS rollback은 포함하지 않는다.

현재 CHORE는 계획·리뷰 준비 기록을 계속 소유한다. 실행 승인 후 실제 시작일의 네 prefix 공통 sequence와 보존 history를 다시 확인하고, 다음 미사용 FEAT ID로 구현 기록 하나를 만든다. 2026-10-18 현재 후보는 `FEAT-20261018-003`이며 아직 배정하지 않았다. 실행 기록은 이 승인안·v0.4·R0-I04·R0-A01/Driver 처분·Windows admission의 정확한 입력에 연결하고 구현 진행·한도 사용·미해결 결과를 한 곳에 둔다. 기존 CHORE에는 이관 pointer만 남기고 Development Index에는 탐색 link만 추가한다. 별도 STATUS나 runtime Work/intent를 만드는 승인이 아니다.

기존 source worktree와 task artifact root를 사용한다. 새 source worktree나 다른 프로젝트 변경은 포함하지 않는다. 합성 프로젝트·worker fixture는 고정된 시험 경계 안에서 생성할 수 있다. 실제 adopter, 개인 파일, 다른 작업의 checkout·VM·backup은 대상이 아니다.

local commit, push, PR, merge, publication, 실제 adopter 적용, 개발 결과 수락·기술 activation·formal admission은 이번 실행 승인에서 제외한다. 이 경계는 [Source Workflow](WORKFLOW.md#publication-and-adopter-authorization)를 따른다.

## Selected Environments

| 환경 | 이번 실행에 사용할 범위 | 현재 근거와 P0 확인 |
| --- | --- | --- |
| W1 · Windows | 기존 task-owned ARM64 UTM 1대, 기존 전용 local standard account, local NTFS, Windows PowerShell 5.1, native ARM64 64-bit final/GIL-enabled CPython 3.14.7 | 과거 probe에서 Windows 11 Pro 26H2/build 10.0.26300.9711, PS 5.1.26100.9711, 지정 interpreter를 관측했다. 2026-10-18 host 조회에서는 VM stopped·Network=[]·folder share None, clipboard 공유 true다. guest의 현재 tuple·token·credential/경로 경계는 P0에서 재확인한다. |
| M1 · macOS | 현재 macOS 27.0.1 ARM64 host, 기존 pyenv final/GIL-enabled CPython 3.14.7, task 경계의 새 runner/policy | interpreter와 digest를 읽기 전용으로 확인했다. 과거 Homebrew qualification의 동일 runtime이라고 하지 않는다. P0에서 현재 executable/child identity와 쓰기·network canary를 검증하고 이번 candidate의 focused·normal·parent-optimized 전체 회귀를 수행한다. |
| x64·물리 장비 | 이번 실행 대상에서 제외하고 미관측·미qualified로 남김 | B의 focused 후속 배정은 유지한다. 실제 장비를 추가하거나 해당 tuple의 지원을 주장하려면 필요한 환경 범위를 별도로 선택한다. 부재 자체를 W1의 새 full-suite/물리 장비 gate로 만들지 않는다. |

W1 전체 VM에 개인 계정이나 자료가 없다고 주장하지 않는다. 기존 전용 표준 계정·합성 실행 namespace를 사용하고 원래 개인 profile의 개별 파일을 열람·수집·변경하거나 실행 namespace로 복사하지 않는다. 아래의 전체 VM package 복구본에는 원 profile의 bytes가 포함될 수 있다. 그 package는 task의 local recovery에만 보존하며 개인 파일 열람·외부 packet 반출에 사용하지 않는다. P0에서는 비밀값을 읽지 않는 계정/권한·credential 존재 여부·실제 접근 경계와 합성 canary를 확인한다. 실자료나 credential이 실행 경계에 노출되거나 해당 분리를 입증할 수 없으면 제품 실행을 시작하지 않는다. Driver가 계정 정리·credential 삭제로 이를 우회하지 않는다.

macOS 제품 test에는 검증한 sandbox runner를 적용한다. 읽기는 고정 source/runtime/필수 도구, 쓰기는 task fixture·output 경계로 제한하고 network·credential 접근을 차단한다. Windows Job Object는 child 회수 장치이며 filesystem sandbox라고 부르지 않는다. Windows에서는 전용 표준 계정·합성 namespace·offline VM·host 파일 공유/clipboard/외부 network 차단·실제 canary를 함께 검증한다. 더 좁은 path confinement을 집행했다고 주장하지 않는다.

### Guest Console And Repeated Operations

Driver는 지정 VM의 UTM 화면과 keyboard/mouse 제어를 사용한다. 전용 표준 계정의 console에 CUA의 개별 key 입력으로 고정된 guest-local runner를 시작하고, 화면과 guest-local 로그에서 상태를 관측한다. child의 시간 제한·Job Object 회수는 guest-local runner가 집행하고 결과를 남긴다. 정상 기동/종료와 아래 승인 범위의 설정 변경에는 기존 UTM UI·utmctl·공식 scripting API를 사용한다. 이 console/VM 관리 경로는 허용된 제어 수단이며, 제품 실행 중 파일 공유·clipboard·외부 network·guest-agent exec를 허용하는 뜻은 아니다. 입력을 clipboard paste나 파일 drag-and-drop으로 바꾸지 않는다.

2026-10-17 보존 기록에는 UTM console의 개별 key 입력, interactive standard token과 guest-local Job Object 회수가 있다. 당시 clipboard 설정은 true였으므로 현재 clipboard off에서의 입력·관측·회수를 검증했다고 하지 않는다. P0에서 실제 UI 입력 대상·token·고정 runner·차단 조건을 확인하고 성립하지 않으면 해당 실행을 멈춘다. console 입력을 잃어도 child 회수는 runner의 책임이며, 회수 미확인은 기존 중단 조건이다. 강제 VM 종료나 새 guest agent/remote shell을 대체 수단으로 도입하지 않는다.

로그인/UAC 비밀 입력은 필요할 때 Owner가 UI에서 처리하고 Driver는 입력·저장하지 않는다. 한 번의 승인이 무인 40시간 실행을 약속하는 것은 아니다. source 반입과 결과 반출을 candidate/batch 단위로 묶고 실행 중 입력을 바꾸지 않는다. 최초 환경 준비는 P0에, 이후 같은 승인 범위의 전달·기동/종료·고정 fixture 재연결·통제 확인은 해당 작업 단계에 시간을 귀속한다. P4/R1 이후에는 모두 P4에 포함한다. Owner 입력 대기도 작업과 child가 모두 멈춘 구간만 활성 시간에서 제외하며, 단계 상한이나 시도 횟수는 초기화하지 않는다.

## Explicit Preparation Permissions

아래는 승인될 경우 P0에서 수행할 최초 환경 준비와, 같은 경계 안에서 반복할 운영 동작이다. 현재는 하나도 수행하지 않았다. 제품 실행과 환경의 관리자 준비를 구별하며, 범위 밖 설치·계정/정책 변경은 허용하지 않는다.

| 준비 항목 | 제안하는 허용 범위와 제한 |
| --- | --- |
| VM 통제 | 지정 VM만 정상 기동/종료하고 clipboard 공유를 false로 바꾼다. 제품 실행 중 Network=[]·folder share None·clipboard off·USB sharing off를 유지한다. 정상 종료 실패는 강제 종료 승인으로 바꾸지 않는다. |
| 복구 준비 | 현재 stopped VM의 pre-product recovery 1개와 restore 검증용 disposable clone 1개를 기존 task root에 APFS clone으로 만든다. 입력 bytes·복구 metadata를 검증하고 원 recovery를 직접 boot하지 않는다. 검증 clone에만 새 UUID와 차단 설정을 명시적으로 적용해 정상 boot·전용 계정/필수 입력 회수를 1회 확인한다. 기존 마지막 recovery를 덮어쓰거나 현재 VM을 자동 rollback하지 않는다. |
| 용량·복구 제한 | APFS clone을 사용할 수 없거나 host 여유가 15 GiB 미만이면 복사/제품 실행을 멈춘다. 전체 VM의 일반 복사나 다른 저장소로의 fallback은 포함하지 않는다. clone 검증이 끝나고 결과가 반출된 뒤 일회성 검증 clone만 standing cleanup 조건으로 정리한다. 원 VM과 필요한 recovery는 유지한다. |
| 입력·증거 전달 | 지정 task transfer 하위 경로만 잠시 공유한다. import는 read-only share, export는 필요한 output 경로의 쓰기 share로 제한한다. product/runner/child가 모두 종료됐음을 확인한 뒤 정상 shutdown→transfer 설정→전용 계정에서 hash 검증·복사→정상 shutdown→share None/empty registry→재기동·실제 차단 확인 순서를 따른다. registry가 비었다는 사실만으로 차단 성공을 선언하지 않는다. candidate/batch별로 전달을 묶고 각 부팅의 로그인 입력은 필요할 때 Owner가 한다. clipboard를 전송 수단으로 쓰지 않는다. |
| PowerShell | 전용 실행/전달 shell에만 `Set-ExecutionPolicy -Scope Process RemoteSigned`를 허용하고 종료로 해제한다. persistent execution policy, PATH, association, system Python을 바꾸지 않는다. 기존 Windows CPython 3.14.7과 Git을 재사용하며 다른 interpreter·PS7·guest tools를 설치하지 않는다. |
| Filesystem fixture | guest task root에 최대 1 GiB expandable VHDX 1개를 새로 만들고 NTFS/FAT32 합성 volume을 각각 1개 준비한다. 다른 local NTFS backup 허용과 non-NTFS 거절의 실제 관측에 쓴다. 새 VHDX identity와 그 volume만 최초 mount/format 대상으로 고정한다. 재부팅 뒤 fixture가 필요한 batch에서 재연결이 필요하면 같은 파일·disk/volume identity를 확인해 re-attach만 수행한다. 재-format·새 disk 선택이나 기존 disk·partition·filesystem 변경은 허용하지 않는다. |
| Remote-path fixture | 같은 guest의 합성 폴더 1개를 전용 계정에만 허용하는 SMB share 1개로 제공하고 loopback UNC로만 접근한다. VM NIC는 계속 없으며 host share나 외부 서버를 remote fixture로 쓰지 않는다. 필요한 기존 SMB service의 일시 start/원상 복구만 허용하고 새 기능 설치·방화벽 완화·guest/anonymous 인증 허용·credential 저장은 제외한다. 실제 loopback 접근이 성립하지 않으면 remote 관측을 unavailable로 남긴다. |
| 관리자 준비 경계 | VHDX·SMB 준비/회수와 위의 동일 VHDX re-attach에 필요한 guest 관리자 권한만 허용한다. script와 exact 대상·기존 상태·복구 명령을 먼저 고정하고, 관리자 PowerShell은 `-NoProfile`로 시작해 profile script를 로드하지 않는다. Owner가 필요한 UAC/로그인 비밀 입력을 직접 처리한다. 제품/test는 관리자 shell에서 실행하지 않고 전용 standard token으로 돌아와 확인한다. 전용 계정의 group membership을 올리지 않는다. |
| Tokenizer 도구 | host task 전용 venv에 `tiktoken==0.13.0`의 CPython 3.14 macOS ARM64 wheel과 그 필수 dependencies만 설치한다. PyPI/files.pythonhosted.org에서 wheel만 받고 이름·version·hash를 설치 전에 고정한다. source build·전역 설치·다른 버전 대체는 하지 않는다. `o200k_base` 자료는 해당 version이 지정한 공식 encoding URL/hash로 task cache에 준비하고 실제 계수는 offline으로 수행한다. 제품 dependency에 넣지 않는다. |

VHD/SMB의 준비 권한은 표준 사용자 qualification을 관리자 실행으로 바꾸지 않는다. DiskPart의 관리자 요구와 SMB share의 지정 폴더·권한 설정은 [Microsoft DiskPart](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/diskpart), [New-SmbShare](https://learn.microsoft.com/en-us/powershell/module/smbshare/new-smbshare?view=windowsserver2025-ps)를 근거로 한 준비안이며, 이 guest에서 성공한 실행 증거는 아니다.

선택한 host interpreter에는 tiktoken이 설치되어 있지 않았다. [PyPI 0.13.0](https://pypi.org/project/tiktoken/0.13.0/)에 게시된 `tiktoken-0.13.0-cp314-cp314-macosx_11_0_arm64.whl`의 SHA-256은 `ca8b310bd93b3772cb1b7922d915446864860f562bdfe4825c63a0aed3fb28cd`다. dependency·encoding 자료의 실제 선택과 hash는 승인된 반입 범위 안에서 P0가 고정한다. 자료 확보와 offline 확인은 P0, 실제 문서 계수는 P3 시간에 포함한다.

환경 준비에는 아직 확인하지 않은 loopback SMB 접근·새 runner 통제·복구 clone의 기동 가능성이 있다. 복구 비용은 해당 task의 변경·volume/share·임시 VM 설정을 회수하는 범위이며, 기존 VM 전체를 되돌리는 동작은 별도 판단으로 남긴다.

최초 환경 준비는 모두 P0 2시간 안에서 수행한다. 이후 반복 전달·동일 fixture 재연결은 위에서 정한 실제 단계에 귀속하며, 미완료 최초 준비를 뒤 단계로 옮겨 P0 상한을 피하지 않는다. 한도 안에서 최초 준비를 끝내지 못하면 그 사실과 남은 입력을 보존하며 시간·권한을 자동 확대하지 않는다. non-NTFS·remote·unknown 각각의 필수 관측은 서로 대체하지 않고, 준비 실패를 PASS나 해당 사례의 사후 비적용으로 바꾸지 않는다.

## Reviewer And Fresh-Reader Calls

두 역할 모두 host의 Claude CLI를 사용한다. 현재 관측한 인증 경로는 `claude.ai / firstParty / pro`이고 API key/provider override는 허용하지 않는다. model override 없이 계정 기본 모델을 사용하며 매회 실제 model/session을 기록한다. 최근 R0-A01의 실제 모델은 `claude-opus-5-5`였고 이후 호출의 모델을 미리 관측한 것은 아니다. 인증·과금 경로가 다르거나 불명확하면 호출하지 않는다.

| 목적 | 방식과 입력 | 호출 한도 | 시간 귀속 |
| --- | --- | --- | --- |
| R1 결과 리뷰 | tools/MCP/browser/shell/test/edit가 없는 fresh Claude CLI static review. 변경 source/test/runner/doc의 필요한 원문·diff, 관련 수락 계약, 식별된 합성 실행 결과·한계를 고정 packet으로 전달 | 최초 1회 + 원인 있는 수정/재검증 후 최대 2회, 총 3회. 회당 20분, CLI 실행 합계 최대 60분 | 준비·호출·판독·처분·후속 수정/재검증 모두 P4 12시간 및 전체 40시간 안에 포함 |
| Fresh-reader exercise | R1과 분리한 fresh CLI context, no-tools. shipped 진입 문서와 합성 사용자 요청만으로 첫 경로를 제안받고, Driver가 승인된 fixture에서 실행한 실제 상태·출력을 후속 입력으로 전달 | 최초 exercise의 2회 호출 + 관련 문서 보정 후 재검증용 2회, 총 4회. 회당 10분, CLI 실행 합계 최대 40분. 최대 2개 exercise | 최초 문서/reader 작업은 P3 4시간. P4/R1 이후 재수행은 P4에 귀속하며 이미 쓴 호출을 초기화하지 않음 |

호출 한도는 자동 소진할 횟수가 아니다. R1이 필요한 근거를 충족하면 후속 호출하지 않으며, fresh-reader도 관련 수정이 없으면 재실행하지 않는다. CLI process를 시작한 뒤 실패·timeout·quota로 끝난 호출도 1회로 센다. auth/disclosure 사전 검사에서 중단되어 CLI 리뷰 process를 시작하지 않은 경우는 호출 횟수에는 넣지 않되 활성 작업 시간에는 포함한다. timeout·quota 뒤 새 process를 자동으로 띄우지 않는다. 원인이 해소됐다는 근거, 기존 승인 범위와 남은 호출·시간 한도를 확인한 경우에만 후속 호출을 판단하며, quota 지속 중 반복 호출이나 provider/billing 변경은 허용하지 않는다. 후속 라운드와 payload 변경은 이 명시 범위 안에서만 재승인 없이 진행한다.

매회 exact request/packet·원본 identity·disclosure·인증·전후 drift, actual model/session·도구 0회·종료 상태를 기록한다. stream partial은 durable task 경로에 저장하고 final을 기존 실행 기록에 원문으로 보존한다. tools를 켜거나 reviewer가 직접 제품 명령을 실행하는 전환, 다른 provider/API billing, 외부 raw 개인 데이터 전송은 이번 승인 대상이 아니다.

### External Packet De-identification

실제 출력의 원본은 private로 보존한다. R1과 fresh-reader에는 Local Execution Bindings의 고정 prefix/계정 역할 대응을 적용한 파생 출력만 전달하며, 원본과 동일한 bytes라고 하지 않는다. 각 호출의 기존 private 입력 기록에 원본·파생본 identity, 대응표와 치환 사실을 남긴다. 외부 packet에는 중립 토큰과 검토에 필요한 합성 내용만 포함한다.

경로 field/명령 인자의 정확한 root-prefix를 경로 경계에서 치환하고, 겹치면 가장 긴 prefix를 먼저 적용한다. 계정명은 지정한 계정 식별 field에서만 중립 역할로 바꾼다. 무차별 문자열 치환이나 경로 정규화는 하지 않는다. suffix의 separator·case·공백/Unicode, record ID·digest·관측 결과를 유지하고 원본 hash를 파생본 hash로 바꿔 주장하지 않는다. 검증 의미가 치환된 prefix 자체에 달렸거나 남은 private 문자열을 안전하게 처리할 수 없으면 해당 자료를 전송하지 않고 영향받는 검토/reader 관측을 unavailable 또는 non-pass로 남긴다.

placeholder는 실제 실행 경로가 아니다. Driver는 reviewer가 낸 임의 명령을 역치환해 바로 실행하지 않는다. 기존 shipped 명령·allowlist·합성 target·현재 상태·exact request/token 검사를 통과한 인자만 고정 대응표와 실제 관측값에 연결한다. 모호한 토큰이나 다른 target은 실행하지 않는다.

### Fresh-Reader Exercise Boundary

첫 호출은 고정한 `AGENTS.md`, `README.md`, `docs/GETTING-STARTED.md`와 합성 목표를 받는다. 목표는 새 합성 프로젝트에서 안내를 따라 시작하고 목표/계획·작업 요청서(intent)를 정리한 뒤, 지정한 sample 파일의 짧은 내용 수정 작업을 시작·확인하고 중단 지점에서 재개하는 것이다. 내부 구현 계획·R0/R1 결론·Driver의 정답 경로는 주지 않는다. 실제 출력에 private 경로가 있으면 위 비식별화 규칙에 따른 파생 입력과 치환 사실을 제공한다. 실제 verified view가 안내한 manual/adapter는 그 단계에서 필요한 입력으로 추가할 수 있다.

Driver는 제안된 명령을 그대로 임의 실행하지 않는다. 현재 shipped 명령 집합과 고정한 실행 allowlist, 합성 target·scope·현재 상태·exact request/token에 맞는지 확인한 뒤 같은 W1 경계에서 실행한다. 동적 ID/token은 실제 관측값으로만 채우며 stale·unsupported 상태를 우회하지 않는다. 예시로 제공되는 수락/거절은 이 승인에 포함된 합성 fixture의 검증 행위에 한정하고 실제 프로젝트나 Owner 결과 수락을 대신하지 않는다. Driver의 대입은 관측된 ID/token·명시된 합성 응답·고정 경로 대응으로 제한한다. reader가 찾지 못한 명령이나 문서를 Driver가 대신 알아내야 진행된다면 개입과 reader의 막힘/non-pass를 기록한다. Driver의 지식으로 보완한 완료를 reader 성공으로 보고하지 않는다.

두 번째 호출은 별도 fresh context에서 해당 shipped 문서·합성 목표·실제 저장 상태와 출력으로 재개 경로와 관측된 막힘을 판단한다. Driver는 필요한 재개를 실제로 실행하고 결과를 독립 검증한다. 원문 명령·실행 argv·기대/실제 결과·미완료를 남긴다. 첫 exercise에 문제가 있으면 같은 기준의 두 호출을 한 번 더 사용할 수 있다. native 실행 묶음은 회당 20분 이내이며 P3/P4 잔여 시간과 아래 증거 시도 한도도 함께 적용한다.

CLI가 문서를 읽고 긍정적으로 답한 것만으로 exercise PASS를 만들지 않는다. 실제 진입·작업·재개의 관측이 필요하고, 이 결과는 agent와 Driver 대리 실행의 합성 경험이다. 비기술 사용자의 독립 사용성이나 실제 고객 acceptance를 입증하지 않는다. fresh-reader와 R1은 서로 다른 context를 쓰지만 같은 provider/model일 수 있으므로 완전 독립 검증이라고 하지 않는다.

## Time And Attempt Limits

실행 승인 후 첫 준비부터 활성 작업 wall time을 누적한다. 이번 승인안 작성과 이전 R0 시간은 이미 수행한 준비 이력이며 새 40시간에서 실행한 것으로 소급하지 않는다. 구현·분석·controller/child·리뷰·통상 결과 보존을 포함하고, 해당 작업과 child 실행이 모두 멈춘 대기만 제외한다. 병행 구간은 단계 wall time에 중복 계산하지 않되 개별 실행 시간과 시도는 각각 센다.

| 단계 | 누적 상한 | 포함 범위 |
| --- | --- | --- |
| P0 | 2시간 | 최초 runtime·VM·runner/console 경계, 현재 recovery·restore 확인, fixture/도구 준비·전달, 통제 canary·실행 입력 고정 |
| P1 | 8시간 | native 기반·import-safe collection·첫 prepared candidate, 반복 개발/진단 |
| P2 | 12시간 | lifecycle·content·worker 구현, old-writer 조기 확인·반복 focused 검증/보정 |
| P3 | 4시간 | A1–A15·help/capability·token 계수·fresh-reader·P/Q final freeze |
| P4 | 12시간 | 두 OS의 최종 증거, R1·처분, 이후 수정/재검증과 개발 결과 closeout |
| 정지 후 회수·보존 | 2시간 | child 회수·필수 증거 보존·복구 판단 전용. 구현/검증 연장·재개에는 사용하지 않음 |
| 전체 | 40시간 | 단계 상한의 합. unused 시간을 다른 단계로 자동 이전하지 않음 |

| 실행 단위 | 회당 상한 | 횟수 상한 |
| --- | --- | --- |
| 개발 중 개별 실행 | 20분 | P1/P2/P3 단계 누적 안에서 원인·다음 관측 목적을 남기며 반복 |
| 통제 canary | 10분 | Windows/macOS 각 실제 실행 경계에서 최초 1회 + 근거 있는 보정 뒤 1회 |
| 최종 collection | 10분 | OS/mode별 최초 1회 + 수정 뒤 2회 |
| 최종 focused batch | 20분 | 사전 고정 OS·묶음별 최초 1회 + 원인/수정 뒤 2회 |
| 전체 suite | 120분 이하 | Windows/macOS 각각 normal·parent-optimized별 최초 1회 + 근거 있는 재실행 1회 |
| R1 / fresh-reader | 20분 / 10분 | 각 총 3회 / 4회. 위 역할 표의 단계 시간에 포함 |

회당·횟수·단계·전체 중 먼저 닿은 제한을 적용한다. 첫 full은 native collection/focused·실제 test 수·spawn/중단 비용에서 추정한 시간에 명시 여유를 더해 120분 이하로 고정한다. 첫 full 전 다른 full 실측을 요구하지 않는다. 원인과 새 근거에 따른 시도 사이 재산정은 기존 ceiling·남은 시간·남은 시도를 모두 지켜야 하며, 실행 도중 증액하거나 timeout만 보고 자동 재시도하지 않는다.

P4/R1 뒤 앞 단계로 돌아가는 수정·재검증도 P4에 포함한다. source/control revision, batch 이름, session, 단계명이나 개발 반복 재분류로 시간·횟수를 초기화하지 않는다. 네 첫 full이 모두 120분을 쓰면 8시간이므로 나머지 P4 4시간에 collection/focused·R1·보정·정리가 들어가야 한다. 모든 재실행 슬롯이나 40시간 내 완료를 보장하는 예산은 아니다.

## Verification And Stop Conditions

v0.4의 모든 필수 하위 사례를 실제 test/exercise ID·mode·명령·독립 oracle·결과에 연결한다. macOS에서 Windows 관련 사례를 통째로 N/A 처리하지 않는다. 비적용 platform 메커니즘과 wrong-OS mutation 거절·제공되는 read/diagnostic 결과를 구별하며, 어떤 OS의 필수 관측도 해당 OS의 비적용 목록으로 빼지 않는다. 모든 macOS 경로의 windows-1 read 성공이나 cross-OS 지원을 추가하는 뜻도 아니다.

공통 worker 조건과 기존 guard로 원 ticket 재개의 성공 또는 stable non-pass를 판정하고 다른 writer의 pending barrier를 검증한다. 예시는 닫힌 지원 목록이 아니며, 한 경로의 미지원/unknown을 부분 성공으로 축소하지 않는다. source/artifact equality·P/Q 양방향·old-writer 노출/거절·prepublication/flush·repair/detach prefix와 보존을 v0.4대로 확인한다.

다음은 해당 실행을 즉시 멈추고 상태·남은 시간/시도·핵심 증거를 보존할 조건이다.

- 계약/승인 범위와 다른 동작, source/test/runner/policy drift, 실제 개인 자료·credential 노출, 제품 실행 중 host 파일 공유·clipboard·외부 network 접근, 그 밖의 허용 범위 밖 쓰기/통신.
- recoverable 입력·필수 원출력 손실, child 회수 미확인, unknown path/identity/flush/prefix·whole-result 불일치.
- 노출된 old writer의 authority/content 발행 또는 거절 미확인. 알려지지 않은 노출을 비노출로 분류하지 않음.
- 회당·호출·시도·단계·전체 상한 도달, host 여유 15 GiB 미만, 승인한 runtime/provider/권한과 불일치.
- 현재 범위 밖 계정/권한/설치·방화벽/연결 변경, 새 지원 의미·schema/membership·계약 amendment가 필요한 경우.

안전성 불일치나 exhausted bound를 단순 재시도 사유로 쓰지 않는다. 합성 canary라도 예상 밖 쓰기/통신이 실제로 성공하면 경계 위반으로 멈추며, 재검증 1회 허용이 이 정지를 면제하지 않는다. 일반 실패는 원인·수정·재실행 범위를 기록하고 이미 승인된 경계와 남은 한도 안에서만 보정한다. 중단 원인을 해소하려고 한도·기준을 낮추거나 scope를 넓히면 필요한 변경만 Owner 판단에 올린다. 독립적으로 안전한 남은 작업은 기존 승인 안에서 진행할 수 있지만, 실패한 선행 조건을 필요로 하는 제품 실행은 시작하지 않는다.

통제나 필수 환경 준비가 안 되면 영향을 받는 관측을 unavailable/non-pass로 남긴다. 그 결과로 전체 qualification/activation을 완료할 수 없을 수 있다. x64·물리 환경 부재 자체는 새 공통 gate가 아니며, 현재 선택한 candidate의 필수 증거 공백과 미관측 tuple을 구별한다.

## Completion And Retention

개발 결과는 exact source/prepared source/local artifact와 문서, 실제 실행·식별된 상속·미해결 결과, R1 원문·Driver 처분·잔여 기준을 제시한다. Owner의 개발 결과 수락은 별도다. published/refetched equality를 포함한 A13 전체 qualification과 별도 Owner activation 없이는 Windows 계약을 발효하지 않으며 formal admission은 live macOS Preview 이후의 별도 판단이다.

입력·scripts·logs·필수 failure prefix는 처음부터 task의 durable 경로에 남긴다. source 변경은 base+exact diff와 필요한 untracked bytes로 회수 가능하게 보존하고 digest만으로 복구를 대신하지 않는다. guest 원출력은 실행 중 guest에 보존하고 checkpoint·restore 전에 지정 host 경로로 반출·검증한다.

단계 완료·handoff에서 소비자가 끝난 중복/빈 파일·disposable fixture만 기존 standing cleanup 조건으로 정리한다. 필요한 입력/결과·마지막 recovery·구체적인 후속 사용이 있는 worktree는 유지하며 경로·소비자·종료 조건을 기존 실행 기록에 남긴다. 복사만 한 것을 cleanup이라고 보고하지 않는다. branch 삭제·최종 recovery 삭제·VM 자동 rollback·관련 없는 task 정리는 이번 범위가 아니다.

## Proposed Owner Wording

아래는 승인 시 사용할 수 있는 문안이며 현재 Owner 승인 기록이 아니다.

> Windows Native Execution Approval Proposal v0.2와 Local Execution Bindings v0.2의 P0–P4 범위, W1/M1 환경과 명시된 환경 준비, R1 최대 3회·회당 20분, fresh-reader 최대 4회·회당 10분, 단계별 상한과 전체 40시간·중단 조건을 승인한다. 그 범위의 입력 구체화·구현·검증·원인 있는 보정과 합성 fixture 검증은 반복 승인 없이 진행한다. DR-0007 v0.10·B안·공통 조건 중심 worker 지원은 유지한다. Git/publication/adopter action, 계약 변경, 개발 결과 수락·activation·formal admission은 포함하지 않는다.

Owner decision: not recorded.
