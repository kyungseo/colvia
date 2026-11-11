# 실행환경 계약과 다음 Claude 구조 리뷰 입력

상태: 2026-11-06 Owner의 기존 범위 확인을 반영한 구현 요구사항. 구현·설치·실행 검증 완료를 뜻하지 않는다. R1 입력은 그대로 보존한다. 이 저장소 문서가 실행환경·지원 목표·확장 경계의 현행 작성 위치다. 다음 집중 리뷰 패킷은 이 문서를 입력으로 참조한다. 나머지 R1 보정 명세를 대신하는 전체 패킷은 아니다.

## 공개 전 갖춰야 할 사용자 경험

사용자는 특정 Python 버전을 설치하거나 pyenv와 PATH를 맞추지 않고 Colvia를 설치하고 사용한다. 지원 Python 버전 확대는 후속으로 둘 수 있지만, 이 설치 부담 해소는 첫 공개 조건이다. 개발자가 소스에서 실행하는 경로는 별도로 안내하며 일반 사용자 경로의 대안으로 떠넘기지 않는다.

앱과 CLI는 같은 제품 설치본에 연결된 전용 실행기를 사용한다. Codex 앱·CLI와 Claude Code 데스크톱·CLI마다 다른 Python 탐색 규칙을 두지 않는다. 실행기는 검증된 설치 binding을 통해 전용 Python과 제품 payload를 선택한다. PATH의 python/python3, pyenv shim, shell 활성화, 다른 프로젝트의 가상환경으로 조용히 대체하지 않는다. 동일한 설치 binding이면 GUI 실행과 login/non-login shell에서 같은 제품·Python·SQLite 조합이 선택돼야 한다. 업데이트 시점에 기존 실행이 있다면 실행별로 고정한 조합을 유지하고, 호환되는 새 실행부터 검증된 새 binding을 사용한다.

## 첫 공개 설치 진입과 완료 기준

Owner 확정 요구: 플랫폼별로 문서에 안내된 명령 하나로 설치 또는 업데이트를 시작한다. OS별 shell 문법은 달라도 된다. 같은 진입이 현재 설치 상태와 호환 가능한 공개 버전을 확인해 신규 준비 또는 갱신으로 연결한다. 정확한 명령 이름과 공개 URL은 배포 설계에서 정하며, 아직 존재하지 않는 주소를 사용 가능하다고 안내하지 않는다.

도구가 OS·아키텍처와 배포 채널/버전 호환성을 판단하고, 배포 파일 다운로드·무결성 검증·전용 Python 준비·제품/runtime binding 활성화를 처리한다. 일반 사용자는 Python ZIP, 개별 해시, 내부 profile, Python 경로를 직접 고르거나 대조하지 않는다. 선택된 버전과 변경 내용은 사람이 이해할 수 있게 보여 준다. 전문가용 버전 지정·오프라인 공급은 일반 경로의 선행 조건이 아니다.

자동 검증은 bootstrap 자체의 신뢰 확인을 없앤다는 뜻이 아니다. 공식 배포 진입의 신뢰 경로와 manifest/자산 검증 계약을 정의하고, 불일치·다운로드 실패·지원 밖 조합을 적용 전에 거부한다. 같은 변조 경로에서 받은 hash만으로 공급 진위를 보장한다고 주장하지 않는다. 공급·서명 방식이 확정되지 않은 부분은 미결로 남겨 실제 경로 검증 전에 해결한다.

한 명령은 무인 완료를 뜻하지 않는다. OS 실행 허용, 알림 허용, 에이전트 설치나 구독 로그인처럼 본인이 해야 하는 조작은 발생 지점에서 목적과 다음 행동을 짧게 안내한다. Colvia 준비와 에이전트 설치/로그인 상태를 구별하고, 인증 정보를 대신 수집하거나 새 결제·보안 설정 완화를 자동 수행하지 않는다. 자동 처리할 다운로드·runtime 선택을 수동 단계로 돌려놓지 않는다.

업데이트는 기존 기록·설정·본문·수락 이력과 capability 선택을 보존한다. 중단·손상·용량 부족 등 실패 시 검증된 이전 실행 조합 또는 명시된 복구 경로를 제공한다. 데이터 형식이 진전된 뒤 무조건 이전 runtime으로 되돌리지 않는다. 실패 후 사용자가 Python이나 내부 파일을 손으로 조합해야 하는 상태를 정상 복구로 보지 않는다.

완료 기준은 사용자가 보게 될 실제 배포 주소와 실제 명령에서 신규 설치 및 기존 설치 업데이트를 수행하는 것이다. 다운로드 → 검증 → runtime 준비 → 활성화 → 앱/CLI 첫 Work → 결과 확인·알림 진입·새 대화 재개를 연결하고, 대표 실패와 복구를 확인한다. 로컬 파일 공급·소스 실행·모의 서버 검사는 선행 근거이며 실제 배포 경로 완료를 대신하지 않는다. 실제 URL 검증에 배포 자산 게시가 필요하면 그 게시 승인을 별도로 받고, 검증 이전에는 공개 경로 미검증으로 남긴다.

## 지원 목표와 판정 단위

첫 공개 목표는 아래 세 플랫폼과 두 필수 에이전트의 CLI·데스크톱 앱이다. 제품 구현 목표, 상위 에이전트가 제공하는 OS/아키텍처 지원 가능 여부, Colvia 실제 검증 상태를 별도 열로 관리한다. 아래 표는 목표를 고정하며 아직 상위 제품의 지원 여부나 시험 완료를 주장하지 않는다.

| 첫 공개 플랫폼 목표 | 필수 호스트 목표 | 지원 가능 여부 확인 | 새 최종 후보 검증 상태 |
| --- | --- | --- | --- |
| macOS Apple Silicon ARM64 | Codex CLI·앱, Claude Code CLI·데스크톱 | 호스트/버전별 확인 | 기존 후보 근거 재사용 가능, 새 배포 경로 최종 판정 전 |
| Windows 11 ARM64 | Codex CLI·앱, Claude Code CLI·데스크톱 | 호스트/버전별 확인 | 기존 후보 근거 재사용 가능, 새 배포 경로 최종 판정 전 |
| Windows 11 x64 | Codex CLI·앱, Claude Code CLI·데스크톱 | 호스트/버전별 확인 | 개발 후보·에뮬레이션 근거와 실제 x64 OS 설치/실행 판정 구분 |

검증 원장은 OS × 아키텍처 × 호스트 네 종류의 12개 조합을 분리한다. 각 조합에서 호스트 버전, 실행 모드/권한, 전용 runtime, 프로젝트 위치와 관측 기능을 기록한다. 지원 가능성은 가능/제약 있음/상위 도구 미제공/미확인으로, 검증은 통과/실패/미실행/해당 없음과 이유로 구분한다. 기능별 일부 통과를 해당 조합 전체 지원으로 올리지 않는다. 상위 도구가 없거나 기능이 부족하면 목표를 조용히 삭제하거나 에뮬레이션 성공으로 대체하지 않고 Owner에게 근거와 선택지를 제시한다. 플랫폼별 최종 수락은 별도로 한다.

## 확장을 위해 지금 고정할 경계

확장 대상을 미리 정하는 목적은 미래 기능 선행 구현이 아니라, 새 플랫폼/에이전트 때문에 기록 형식·수락 의미·이력을 다시 설계하지 않도록 하기 위함이다. 필요한 좁은 계약만 두고 범용 plugin registry, 동적 code loading, 자동 adapter 생성, 미래 scheduler를 만들지 않는다.

| 경계 | 현재 소유 책임 | Core에 넣지 않을 차이 |
| --- | --- | --- |
| Core/domain | 프로젝트·Work·결과 identity, 승인/수락, 참조·본문 보존, 상태/경쟁·무결성 규칙 | OS명·모델명·제품명에 따른 수락 의미 변경 |
| 플랫폼 구현 | 설치/runtime 준비, 경로·파일 특성, 잠금·내구성, 권한 진단, OS 알림·클릭 연결 | Windows/macOS 경로와 OS API 호출을 domain에 직접 삽입 |
| 에이전트 연결 구현 | 지침 전달, 도구 호출 규약, 실행 시작/상태/취소, 승인 연계, 결과·오류 전달 | 특정 CLI flag, 앱별 session format, 제품별 출력 해석을 Work 상태 정의로 사용 |
| 모델/provider 연결 | 실제 에이전트가 사용하는 모델의 호출·가용성 등 필요한 정보 | 모델만 연결하면 파일 작업·취소·재개까지 가능하다고 추론 |
| 설치 조립·연결 | 검증된 플랫폼/에이전트 구현과 runtime/capability 조합 선택 | Core 내부에서 제품명에 따라 실행 경로를 분기 |

에이전트는 파일과 도구를 다루며 작업을 수행하는 실행 주체다. 로컬 모델은 그 주체가 사용할 수 있는 추론 수단이며 모델 자체를 파일/도구 실행 에이전트와 동일시하지 않는다. 모델 공급자가 로컬이라는 이유만으로 접근 격리·취소·알림·안전성이 보장되는 것도 아니다.

연결 계약은 기능 이름·버전과 검증된 제약을 표현한다. 최소한 지침 수신 방식, 프로젝트 읽기/쓰기 및 sandbox, 도구 호출, 실행 관측, 취소 요청과 실제 종료 확인, 결과의 정확한 식별·전달, 재개 가능 여부를 구분한다. 제품명/버전은 adapter 선택과 진단 근거로 기록하되 Core의 의미를 결정하지 않는다. 에이전트가 주장한 능력만으로 권한을 부여하지 않으며, 실제 권한과 연동 검증을 확인한다. 없는 능력을 추정하거나 더 넓은 권한으로 조용히 우회하지 않는다.

OS 잠금 구현은 플랫폼에서 제공하되 공용 authority의 transaction/CAS 및 수락 불변식은 저장 계층과 Core의 계약이다. 에이전트 실행 성공이나 취소 요청 접수는 Work 결과 수락·실제 종료와 별개다. 결과 schema는 에이전트 고유 transcript나 session ID를 필수 권위로 삼지 않는다. 외부 실행 식별자는 보조 provenance이며 앱 대화가 사라져도 보존된 결과와 사람 결정은 읽을 수 있어야 한다.

새 adapter 추가는 등록된 기능 구현의 추가로 처리하고, 기존 Work·본문·수락을 다시 쓰거나 제품명을 바꾸기 위해 이관하지 않는다. 같은 프로젝트 authority와 유효 workspace에서 다른 에이전트가 같은 Work의 상태·보존 결과·남은 결정을 읽고 이어갈 수 있어야 한다. 에이전트 간 비공개 채팅 맥락 자동 이관이나 서로 다른 기기/clone의 자동 동기화는 약속하지 않는다. 권한·능력 부족, 이전 실행의 미확정 효과, workspace 차이가 있으면 그 경계에서 안전하게 멈추고 설명한다.

미래에 실제 의미 변경이 필요할 때는 첫 공개 호환·migration 정책을 따른다. 단순 OS/에이전트 추가 때문에 그 의미 변경이 필요하지 않도록 의존 방향과 중립적인 데이터 계약을 지금 검증한다.

## 후속 후보 — 현재 구현 제외

| 후보 | 의도 | 착수/지원 선언 조건 |
| --- | --- | --- |
| EXT-PLATFORM-LINUX | Linux 설치·경로·잠금·권한·알림 구현 | 별도 범위·대상 환경 결정 후 실제 배포·연동 검증 |
| EXT-AGENT-LOCAL | 로컬 모델을 사용하는 파일/도구 실행 에이전트 연결 | 모델과 실행 에이전트 구분, 실제 작업·취소·결과·재개 검증 |
| EXT-AGENT-ANTIGRAVITY | Antigravity 연결 | 당시 제공 능력·제약 확인, 같은 Work 재개와 상태/권한 검증 |
| EXT-AGENT-PROJECT-TOOLS | 그 밖의 프로젝트 작업 가능한 AI 도구 | 필요한 지침/도구/실행 계약 충족 및 실제 연동 검증 |

이 표는 잊지 않기 위한 현재 설계의 후속 후보 목록이다. 착수 승인·지원 선언이 아니며 제품 코드의 기능 ID를 미리 고정하지 않는다. 개발 인덱스의 후속 후보가 이 표를 참조한다. 착수 시 해당 후보와의 연결을 유지한다. 이번 구현은 첫 공개 플랫폼·에이전트에 필요한 경계만 구현하며 미래 도구 전용 코드와 시험을 포함하지 않는다.

## 구현 계약

1. 설치기는 OS·아키텍처에 맞는 전용 실행환경을 준비한다. 최초 준비가 미리 설치된 사용자 Python을 요구해서는 안 된다. 온라인 공급과 전달받은 오프라인 자산 모두 manifest의 버전·크기·해시 등 해당 공급 계약을 검증한다. Git 등 다른 필수 도구가 필요하면 별도로 감지·안내하며 준비됐다고 가정하지 않는다.
2. 제품 버전, Python 버전, SQLite library 버전, OS·아키텍처, store/protocol/capability 호환성을 구분한다. 여러 Python 버전의 공개 지원 확대 없이도 검증된 전용 조합으로 동작해야 한다. 소스 실행의 runtime 요구는 설치 사용자에게 전가하지 않는다.
3. 업데이트는 새 payload와 runtime을 먼저 준비·검사한 뒤 binding을 활성화한다. runtime 재사용이 가능하면 불필요한 재다운로드를 하지 않는다. 다운로드·무결성 검사·압축 해제·권한·중단 실패에서 이전 사용 가능한 조합과 기록을 보존한다. 새 기록을 읽지 못하는 이전 버전으로 자동 rollback하지 않는다.
4. 프로젝트 연결과 앱 worktree의 연결은 프로젝트 identity·workspace identity·authority와 runtime binding을 따로 다룬다. worktree에 복사된 옛 경로나 PATH의 다른 실행기로 성공한 척하지 않는다. 일반 폴더, linked worktree, 프로젝트 내부의 앱 생성 worktree 모두 정확한 authority와 전용 실행기를 찾아야 한다. 같은 이름의 다른 프로젝트와 섞이지 않아야 한다.
5. 실행환경이 올바르더라도 sandbox 접근이 막힐 수 있다. runtime/payload 읽기·실행, 프로젝트 범위 읽기·쓰기, authority DB와 journal/잠금 생성·교체·복구, 선택한 전달/알림 기능의 쓰기 경로를 구분한다. source success나 shell에서의 접근 가능성을 앱 권한의 증거로 삼지 않는다.
6. 저장 위치 설계는 이 권한 계약과 함께 정한다. R1에서 제안했던 .git 내부 저장은 Codex 기본 sandbox 보호와 충돌하므로 기본 경로로 확정하지 않는다. 경로를 옮기기만 하거나 매번 권한 상승을 요구하는 것으로 해결됐다고 하지 않는다. 설정 변경이 필요한 경우 정확한 범위·이유·회수 방법을 설명하고 기존 승인 범위를 따른다. 보안 기능 전체 해제나 전체 디스크 권한 확대를 기본 해법으로 두지 않는다.
7. 연결 전 진단은 실제 사용할 실행기와 권한으로 확인한다. 읽기 전용 조회에서 몰래 파일을 쓰지 않는다. 필요한 쓰기 probe는 명시된 진단 단계에서 작업 소유의 한정 경로만 사용하고, 실제 사용자 기록을 수정하지 않는다. 진단 자체가 추가 권한을 받았으면 기본 앱 모드 통과로 기록하지 않는다.
8. runtime 누락·손상·지원 밖 조합·잘못된 workspace 연결·쓰기 차단을 구별해 짧게 안내한다. 예: “Colvia 실행환경이 준비되지 않았습니다. 설치 도구에서 복구를 실행해 주세요.” 또는 “이 앱에서 작업 기록 폴더에 쓸 수 없습니다. 아래 폴더의 접근을 허용한 뒤 다시 실행해 주세요.” 실제 해결 조작과 필요한 경로만 제시하고 토큰·내부 지침·긴 traceback은 진단 상세로 분리한다. 원인 확인 없이 재설치를 권하지 않는다.

## 최종 검증 행렬

호스트는 Codex CLI, Codex 앱, Claude Code CLI, Claude Code 데스크톱으로 구분한다. 작업 위치는 비 Git 일반 폴더, Git 일반 checkout, 외부 linked worktree, 앱이 프로젝트 내부에 만든 등록 worktree로 구분한다. 모든 호스트가 worktree를 직접 생성해야 한다는 뜻은 아니다. 실제 생성 주체와 해당 폴더를 여는 주체를 기록한다.

| 검사 | 필요한 확인 | 근거의 한계 |
| --- | --- | --- |
| 개인 Python 설정 없는 최초 설치 | pyenv·사용자 venv·사용자 Python 없이 installer가 runtime을 준비하고 첫 명령 실행 | env를 비운 합성 검사는 탐색 규칙 근거다. 실제 새 사용자 설치를 대체하지 않는다. OS 기본 Python이 남아 있으면 존재 여부와 미사용을 기록한다. |
| 앱·CLI 실행기 선택 | 위 네 호스트와 네 위치에서 설치 binding·실제 executable·Python·SQLite·제품 identity 대조 | process 이름이나 source version 출력만으로 installed payload 선택을 판단하지 않는다. |
| 최소 읽기·쓰기 경로 | 조회, 합성 Work 등록/제출/수락, journal 생성·복구, 선택 기능의 전달 경로 | 앱 sandbox와 CLI sandbox를 각각 기록한다. 상위 권한으로 통과한 결과는 기본 권한 통과가 아니다. |
| 다른 Python이 먼저 보이는 환경 | PATH 앞에 지원 밖 Python/가짜 shim이 있어도 전용 실행기를 사용 | 실제 개인 설정 변경 없이 합성 process 환경으로 재현한다. |
| worktree와 이동·재개 | 올바른 authority/Work 조회, 다른 workspace 결과 혼합 거부, 유효 binding 유지 | 앱 생성 nested 경계를 단순 폴더 이름 제외 규칙으로 처리하지 않는다. |
| 업데이트와 중단·복구 | 준비 실패, 활성화 직전/직후 중단, 기존 실행, 호환/비호환 rollback | 공개 이후 기록·설정·본문·수락 이력 보존 계약과 함께 검증한다. |
| runtime/권한 실패 안내 | 잘못된 상태를 성공으로 보고하지 않고 필요한 다음 조작·이유를 짧게 표시 | 모델이 우연히 올바른 설명을 한 것과 제품 진단 출력의 정확성을 구분한다. |

제품 unit/통합 검사는 실행기 선택·binding·실패 상태를 집중 검증하고, 설치본 검사는 실제 패키지와 실제 앱 권한 경로를 확인한다. 최종 OS/아키텍처별 공개 후보는 해당 플랫폼의 설치본으로 판정한다. macOS 또는 Windows ARM64 근거를 x64 성공으로 넓히지 않는다.

각 셀은 재사용/신규 통과/거부 관측/미실행을 구분한다. 최소 기록은 후보 버전·해시, host 및 실행 모드, 작업 위치 종류, 선택된 runtime/binding, 읽기·쓰기 결과와 필요한 사용자 조작이다. 인증 정보와 개인 계정 값은 수집하지 않는다. 동일 원리의 반복 대용량 검사는 생략할 수 있으나 앱별·위치별 실행기 선택과 권한 차이는 확인해야 한다.

## Host Approval Modes

[Codex·Claude 권한 모드별 접근·승인 기준](validation.md#codexclaude-권한-모드별-접근승인-경로)을 실제 호스트 검증에 적용한다. 선택한 승인 절차로 완료 가능한지를 판정하며, 계획 모드의 쓰기 제한을 실패로 보거나 호스트 도구 승인을 Colvia 범위 승인·결과 수락으로 대체하지 않는다. 실제 실행 조건이 같은 작성·제출·재개 근거는 재사용하고 차이가 있는 경로만 추가 확인한다. 모드 이름·제공 여부는 host/버전에서 확인하며 전체 권한 전환을 필수로 요구하지 않는다. 설정 미반영과 명령별 사용자 승인을 통한 실행 가능성은 별도 관측이다.

## 기존 근거와 범위

기존 source/PATH의 데스크톱 작성·재개·수락 결과는 에이전트 사용 흐름 근거로 재사용한다. 기존 managed 설치·갱신·알림 근거는 해당 후보와 관측한 경로에 한해 재사용한다. 새 authority 위치, runtime binding, SQLite와 권한 경계가 바뀐 부분은 새로운 설치본 검증으로 채운다. 기존 실패·측정 기록은 보존하며 성공으로 덮어쓰지 않는다.

새 Python 버전 지원 확대, 실제 개인 Python 설정 변경, 임의 OS 권한 확대는 이번 정렬에 포함하지 않는다. 실제 설치·앱/VM·모델 실행은 기존 보류와 승인 경계를 유지한다. 이번 문서화가 그러한 실행의 추가 승인이 되지는 않는다. 실행환경 구현 비용은 기존 연결·패키징·갱신 항목에 명시하고 중복 산정하지 않는다. 새 전용 과제로 확장하지 않는다.

## 다음 Claude 패킷에 넣을 검토 질문

- 플랫폼별 명령 하나에서 실제 배포 파일 검증·전용 runtime·호환 버전 선택까지 연결되는가? 수동 Python ZIP·해시·profile 조합이 일반 경로에 남아 있지 않은가?
- 세 플랫폼 × 두 에이전트 × CLI/데스크톱 목표와 실제 지원 가능성/검증 상태를 분리했는가? 실제 배포 신규 설치·업데이트/복구가 완료 기준에 있는가?
- OS adapter와 agent adapter가 Core 밖에 있으며, 능력·제약 차이가 수락 의미를 바꾸지 않는가? 로컬 모델과 파일/도구를 다루는 에이전트를 구별했는가?
- 미래 adapter가 기존 기록과 같은 Work를 읽고 이어갈 수 있는가? 그 목적을 넘어 미래 기능이나 과도한 범용 계층을 미리 만들고 있지 않은가?

- 개인 Python이 전혀 없어도 최초 준비가 가능한가? bootstrap 자체가 그 Python을 요구하는 순환 의존은 없는가?
- 앱과 CLI가 동일한 검증된 binding을 사용하며 PATH·pyenv·shell 차이에 기대지 않는가?
- runtime은 실행되지만 authority/journal 또는 전달 경로에서 쓰기가 막히는 경우를 놓치지 않았는가? 일반/linked/nested workspace에서 최소 권한으로 가능한가?
- 업데이트·중단·복구 중 runtime과 payload가 다른 세대로 섞이거나, 첫 공개 이후 기록을 읽지 못하는 rollback이 가능한가?
- source 성공, 정리된 env 성공, 실제 설치본 성공이 각각 구분되는가? 짧은 실패 안내가 실제로 필요한 조작을 알려 주는가?

위 질문은 R1 F1/F4/F7의 보정 검토에 함께 넣는다. 새 독립 실행환경 리뷰를 추가로 만드는 요청이 아니다. 기존 실행환경 방향이 구현 명세·리뷰·최종 수락 기준에서 빠지지 않게 하는 Owner의 확인이다.


## R2 설계 보정과 미결 정책

[R2 처분](review-r2-disposition.md)의 M1·M2·M8의 기록 위치·권한·백업·공급 신뢰 정책은 2026-11-06 Owner가 설계 기준으로 채택했다. 실제 설정 변경·설치·key 생성 권한은 아니다. 플랫폼별 사용자 데이터의 프로젝트별 기록 폴더를 권장하고, 호스트의 좁은 추가 쓰기 허용 가능 여부를 실제 조합별로 확인한다. 전체 authorities나 home 접근을 기본값으로 확대하지 않는다.

실행기 진입은 작업 폴더에 복사된 branch 파일에 의존하지 않는 사용자별 managed entry로 설계한다. 사용자 상대 경로의 해석도 앱별로 확인한다. Git executable/version과 필요한 config provenance를 관측 context에서 한 번 고정하며, 12개 조합 원장에 그 결과를 남긴다. 개인 Python과 Git의 존재를 혼동하지 않는다. Git 부재·CLT 준비·권한 차이는 각각 안내한다.

첫 공개부터 갱신 서명 key·서명된 channel/release metadata, freshness/expiry·관측한 순서·명시적 rollback·key 교체/회수/복구를 설계하는 안을 권장한다. 첫 취득의 HTTPS 신뢰와 OS 코드 서명/실행 허용은 별개다. 서명된 오래된 metadata도 재전송될 수 있으므로 서명 성공만으로 최신성을 판단하지 않는다. 실제 key 생성이나 유료 서명 선택은 여기서 수행하지 않는다.

runtime slot은 현재·실행 중·필요한 마지막 복구본을 보존한다. 고정된 두 개만 남기려고 실행 중인 구 slot을 삭제하지 않는다. 호환 읽기/쓰기와 필요한 capability를 별도로 판정하고, 알 수 없는 수락 의존 객체를 생략한 채 정상으로 읽지 않는다. 모델/provider는 현재 소비자가 요구하는 경계만 구현하며 미래용 범용 interface를 선행 구현하지 않는다.


## Windows/WSL qualification boundary

현재 Windows 목표는 native Windows 프로세스다. WSL/Linux CLI는 Linux 후속 대상으로 분리하고, Linux mount 경유로 Windows authority를 공유해 쓰는 경로는 미검증으로 차단·안내한다. WSL에서 Windows executable을 호출하는 상호 운용 경로도 별도로 확인하기 전 native 호스트 통과와 합치지 않는다. 모든 WSL 파일시스템의 잠금이 잘못됐다고 단정하지 않는다.

호스트 접근 설정의 저장 위치는 user-level에서 프로젝트별 authority만 허용하는 방식을 우선 비교하되, 실제로 지원하는지와 앱 worktree에 상속되는지를 P2에서 확인한다. 프로젝트 전체/사용자 데이터 전체를 허용하거나 설정 파일이 branch에 복사될 것이라고 가정하지 않는다. 아직 실제 설정 변경은 없다. 최초 bootstrap과 갱신의 신뢰 경계는 [C7/C8](implementation-contracts.md)을 따른다.


## Supply, Candidate And VM Reuse

다음 후보를 준비할 때는 [담당 Work](../FEAT-20261106-002-record-foundation.md)의 수락 범위와 기존 공급·조립·설치 근거를 먼저 확인한다. 원본 입력과 실패 기록은 보존하고, 아래 구분에 따라 달라진 부분만 검사한다.

| 바뀐 내용 | 재사용과 다음 작업 |
| --- | --- |
| 제품 코드·설치 지침만 변경 | 고정한 전용 Python·검증기 의존성을 재사용한다. [후보 조립기](../../../distribution/foundation_bundle.py)로 새 후보를 만들고 변경 영향에 해당하는 검사와 inventory 대조를 수행한다. |
| 실행환경·의존성 변경 | 기존에 검증된 공급 생성 절차의 고정 입력·도구 버전·원격 실행 기록을 확인하고, 변경된 공급물만 다시 생성·검증한다. 원격 실행과 비용은 별도 승인 범위를 따른다. |
| 실제 설치·갱신·복구·호스트 사용 확인 | 기존 VM 등록·디스크·계정·설치 기준점을 먼저 확인한다. VM에 빌드 환경부터 다시 구성하지 않는다. |
| 개인 설정 없는 환경 확인 | 필요에 따라 별도 계정이나 복제본을 사용한다. 개발 측 공급 생성에 쓰는 빌드 도구를 일반 사용자의 설치 조건에 넣지 않는다. |

재개 기록에는 고정 입력의 digest와 도구 버전, 실행 순서, 산출물 위치와 검증 방법, 재사용 가능한 조건, 알려진 실패와 중단 조건을 함께 둔다. 파일 전달은 실제 크기와 측정한 처리량으로 제한 시간을 정하고, 성공 종료뿐 아니라 회수한 바이트까지 대조한다. 다른 실행 조건의 성공이나 부분 전송을 현재 설치 성공으로 표시하지 않는다.

공개 가능한 절차·제품 계약은 저장소가 관리한다. 개인 경로·계정·비공개 실행 정보와 원 실패 로그는 [기존 문서 배치 기준](../document-ownership.md)에 따라 내부 기록에 보존한다. 정확한 내부 실행 경로는 해당 작업의 기존 실행안과 결과에서 연결한다. 이 절차의 존재나 과거 성공은 새로운 실행·비용·설치·공개를 승인하지 않는다.

### Windows runtime creation checkpoint

The native runtime-directory creation correction uses the existing platform lifecycle adapter and retains the private ACL checks. The prepared candidate reuses its qualified runtime, verifier and native entry. Native directory ACLs passed; installation then stopped before runtime activation at root-metadata reauthentication because the Windows cache uses a verified two-path hardlink while that reader still requires a single link. Keep this separate from the earlier directory-creation failure. Reuse the supplied runtime and existing known-pair validation evidence when planning that correction; do not rebuild dependencies, weaken generic hardlink checks, reset trust or report installation/recovery qualification. The owning record links the private execution evidence.


### Root reauthentication and redirected-output checkpoint

The subsequent correction reuses the exact current-root pair reader while retaining strict single-link reads for historical roots and ordinary files. The Windows ARM64 fixture now passes installation, private runtime ACL checks, native status and Korean connection preview. Installed Python entry wrappers set UTF-8 output and preserve each stream's existing error handler; runtime, verifier and native executable inputs are reused.

The remaining connection attempt was refused before operation creation because the test harness wrote canonical JSON through Windows text mode. Preserve that failure, emit machine inputs as exact UTF-8/LF bytes, and validate them through the actual codec before a further approved attempt. Reuse the successful installed slot; do not reinstall to correct a test-input writer. Work retention and interrupted-update recovery remain unqualified for this fixture until the remaining sequence passes. Static root-rotation tests are not native Windows rotation qualification; the offline fixture does not qualify public-network distribution.

### Windows effect-record boundary checkpoint

The follow-up reused the same installed slot and passed native canonical-input validation. Connection then stopped at the common effect-manifest validator: Windows emits a three-part native identity list while the shared validator accepts only the Darwin identity dictionary. Keep this product-record boundary separate from installation, UTF-8 output and the earlier test-input failure. Direct port tests do not establish lifecycle-record publication compatibility; the next focused regression must connect those layers and retain malformed-identity refusals.

No Work or interrupted-update recovery ran in this follow-up. Preserve any incomplete connection journal, authority and staged originals; do not delete or silently replay them. A post-stop readback remains pending because the diagnostic used a regular-file identity API on a directory. Previous preservation checks retain their original observation time. The owning Work records the next authorization boundary.

### Windows identity publication and update checkpoint

The identity correction retains exact Windows/Darwin variants and malformed/mixed-variant refusals. Focused lifecycle-record tests passed; native Windows subsequently stored and read the connect plan/state with valid reference closure. The corrected installed slot was selected through the official update path and the former slot remains available for recovery.

Qualification is still partial. A long SQLite audit/journal path failed; a shorter fixture operation name enabled update without fixing the general path limitation. Connection then stopped before its first generated file was applied. Its persisted intent remains pending, all four targets read as pre-state, and original bytes are preserved. The generic manager error does not retain the underlying OS exception, so it is not evidence of a permission-policy failure. Diagnose that boundary before a separately approved resume. Work retention and interrupted-update recovery remain unexecuted. Preserve both failed operations and the pending authority; do not reset or reinstall to hide them. Existing-name NTFS replacement identity remains a separate qualification gap.

### Pending connection blocks corrective runtime update

The narrow rename and backup-path correction passed focused source checks and candidate verification. Native qualification stopped before selecting that candidate: the installed manager rejects updates while a project effect is pending. A prepared slot is not an activated runtime, and a validated candidate is not evidence that its native fix ran. Readback preserved the prior selected/recovery slots, pending connection closure, original data and failure records.

Before resuming this state, define an explicit recovery contract for a broken runtime with an incomplete effect. Do not clear pending records, edit selection pointers, bypass the selected-runtime entry or weaken the ordinary update guard. A separate clean test home can qualify the candidate but cannot establish recovery of the original pending connection. Reuse existing runtime/dependency supplies; no remote rebuild is justified by this source-only correction. The owning Work and private connection-correction result identify the exact preserved checkpoint and consumed execution limits.

### Draft: verified recovery of an unapplied connection

Planning status, 2026-11-09: not implemented, activated or authorized for a native run by this draft. The ordinary pending-effect update refusal remains unchanged.

Reuse the independent verified bootstrap recovery entry to finish one exact previously approved connection without first selecting the corrective runtime. This is an explicit recovery command, not an alternative ordinary launcher. Prefer this to deleting/cancelling the connection or permitting arbitrary runtime updates with pending effects. Reuse ProjectSetup/ConnectFiles ordered effects and their existing record kinds; do not add general pending-effect recovery or an automatic fallback.

Admission requirements:

- Authenticate the repair payload externally before executing it; then bind its inventory, dedicated interpreter, platform, release descriptor and digest to the existing home's signed target/trust chain. A caller-supplied manifest hash or successful payload verification alone is not the distribution trust root. Keep channel, root anchor and rollback counters unchanged; refuse stale, expired, mismatched or unavailable trust. Use existing verified transport/staging, never an unchecked source import or a new trust anchor.
- Bind the review to the home, selected/recovery pointers, exact connection operation, project instance/generation, plan and state references, topology, native entry and all effect targets. Initial admission is limited to an unapplied connection (ready/intent at index zero, every target proven pre). Reject unrelated pending effects, activation/native/app pending, incompatible schemas/capabilities, changed original bytes, ambiguous identity and unsupported partial states.
- Acquire the existing management/runtime/project effect locks in one defined order with one owner; do not recursively reacquire non-reentrant locks. Revalidate receipt, trust, identities and expected references under those locks. Recovery records never grant ordinary application writes from an unselected runtime.
- Preserve the original journal, staged originals and failure evidence. Create a verified recovery snapshot/receipt using existing preservation facilities before mutation; logical export alone must not be treated as preservation of staged native-effect bytes.
- Before each effect, revalidate the current pending reference and exact native pre/post state. Reuse the ordered effect writer and its CAS publication. Clear the pending head only through its normal final completed state, never by direct deletion or state editing. Persist repair identity and progress in the manager's existing operation area; no authority schema change.
- Keep signature expiry checks throughout recovery. If retained metadata expires after an effect, use the existing metadata-only renewal bound to the same release operation, preparation receipt and exact target; pass its explicit renewal reference when resuming. Do not skip expiry or prepare a different target to continue the admitted connection. Preserve original plan, snapshot and progress references.
- A process stop requires explicit recovery inspection. Only validated progress from the exact admitted connection state, with the same plan/native identities, expected lifecycle operation lineage and remaining pre-state targets, may be resumed under an authorized bounded run. The record proves valid progress, not which process produced it; unknown, foreign or inconsistent partial state refuses without writes.
- Prove completed connection closure and every after-file byte before returning. Preserve selected/recovery runtime pointers and unrelated authority state throughout connection repair. Then leave recovery execution and use the normal verified update/backup path; it must continue rejecting all other pending effects.

Qualification requirements: preserve refusal tests for pending ordinary updates; cover wrong receipt/operation/home/selection/target, stale signature, incompatible reader/writer capabilities, changed ancestor/original, unrelated pending and interrupted repair. Verify pre-effect refusal, crash-after-effect/before-record handling and final exact post-bytes. Native Windows qualification must exercise the corrected exact-handle rename in disposable scratch before the original connection, then prove ordinary update, Work/body/config/export and separate interrupted-update recovery. Existing source-only and native evidence retain their original limits. An isolated new home is not recovery evidence for the original home.

Out of scope: cancellation records, general effect repair, new trust anchors, key rotation, relaxed no-replace/identity checks, direct pointer or pending edits, permissions, notification registration, remote builds and publication. A safe public entry must fit the existing independently authenticated bootstrap contract; if it cannot, stop before applying to the original installation and report the missing trust boundary.


### Windows Original-Connection Recovery Qualification

The narrow verified-bootstrap recovery contract above is implemented and passed a native Windows ARM64 qualification on the original interrupted installation. The corrective payload completed the exact four-file connection and validated its record closure without changing runtime selection. Normal signed update/backup then passed, followed by synthetic ordinary Work publication/acceptance, new-process before/after body lookup, configuration, logical export, a deliberate interrupted download and a separate normal recovery update. Pending-effect guards and trust checks remained enabled. Existing installations, source files and failed operations were retained; normal pre-update export receipts could advance.

The old selected runtime's long resume operation generated an over-limit audit path and stopped before selection. A bounded fresh normal update with a short operation completed; the exact hidden OS cause is inferred from the old producer and prior native path counterexample, not newly traced. The corrected candidate uses bounded audit/export names. Preserve that first failure instead of relabelling the entire run as first-attempt success.

This evidence covers dedicated installed runtime/native entry calls with the exact generated launcher arguments, not execution of the generated command script itself, model-host usability, public network delivery, native expired-metadata renewal, arbitrary pending effects, replacement of existing user targets or Windows x64. Source/refusal evidence and actual native results remain separate. The owning Work records pending Owner acceptance and points to private inputs, unchanged suppliers, review disposition and consumed execution limits. Do not repeat completed Work/body checks or infer permission for another run from this qualification.
