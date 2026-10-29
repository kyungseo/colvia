# 공식 CLI 정책의 소스 소유와 합성 U2 검증

## 상태와 승인 범위

상태: 공식 CLI의 합성 정상·취소·폐기권한 복원 거절·새권한 완료 검증 통과. 아래 Owner Result Acceptance에서 source-only 결과 수락을 기록했다. Driver는 Codex다. 최신 Owner 승인은 공식 helper 하나의 읽기·실행과 임시 기능 활성화, 누적 180분 중단/160분 신규 시작 제한, 기존 실패 보존과 범위 내 보정·재시도를 포함한다. 추가 권한은 중단 조건이다. 결과 수락·Git·설치·제품 기본 경로 전환 승인은 아니다. 별도 Reviewer는 이번 범위에 없다. 초기 승인과 후속 변경은 아래 단계별 기록에 보존한다.

목적은 검증된 공식 CLI 정책을 source가 소유하도록 하고 외부 Host를 통해 합성 문서 작업의 정상·취소·복원을 관측하는 것이다. 기존 native·Core·worker 의미는 유지한다. 이전 task의 수락된 성과를 다시 열거나 새로운 runtime Work를 만들지 않는다.

시작 입력은 source base `3ff38f1fff4c3bb5641d1a3405f63e3d8695133c`, 공식 배포 CLI 0.165.0, 고정 모델 gpt-6.1-sol/low다. 이전 누적 활성 시간 97.87357775분을 이어받고 Owner 대기는 제외한다. 작업별 정책/명령/고정입력/실패 원장은 지정된 비공개 실행 증거에 보존하며 이 source 문서는 개인 경로나 계정정보에 의존하지 않는다.

## 계획과 완료 기준

정책 파일·경로 검사 모듈·집중 테스트·사용 설명을 추가하고 task-local runner가 이를 사용하게 한다. 새 path에서 보호 parent/exec child를 검사한 뒤 정상 → 쓰기 직전 취소 → 별도 Host의 폐기권한 복원 거절 → 새 권한 완료를 순서대로 관측한다. 입력 drift나 보호 실패·routing/auth/TLS/network/timeout·종료 불명확 시 중단하고 같은 live 호출을 재시도하지 않는다.

상한: 정책1, 집중검사2묶음/합계5분, 보호2process/각30초, AppServer3·계정RPC3·thread3·turn3, 계획취소1, live worker11/각60초, 별도Host복원1/30초. 추가 OS로그·DNS/TLS helper·Rust build·offline worker는0. turn 수는 공식 내부 inference·HTTP·비용 상한이 아니다.

정책/loader/runner 연결10–15분, 집중·보호3–5분, live/복원12–18분, 보존·정리·보고5–7분으로 추가30–45분을 예상한다. 판단 추정이며 모델 latency는 미측정이다. 단계 대기를 포함하고 겹치는 시간은 한 번만 센다. 누적180분 상한과 별개다.

## 검증 선택

누적 변경은 source-only 정책 binding과 task-local 공식 CLI 검증 경로에 한정된다. 설치·Core lifecycle·기존 native/worker source는 바꾸지 않는다. 기존 Host focused22개/당시 worker6회는 원래 source/function/fixture identity를 대조한 한정된 재사용 근거이고 새 실행 pass가 아니다. 새 loader의 parameter/경로/alias/정책 변경 거절과 runner의 admission·시간·예약·종료 연결을 집중 확인한다.

새 테스트는 tests.test_u2_official_runtime_policy.OfficialRuntimePolicyTests의 전체12개 ID를 normal/parent-O 각1회 실행한다. task-local admission·runner 집중 검사는 같은 묶음에 포함한다. 보호2process와 실제 U2 세 시나리오가 변경된 경로의 실증을 담당한다. 전체 regression 또는 새 OS/설치 runtime qualification으로 보고하지 않는다. 이 제한된 개발검증은 새 플랫폼/제품 지원의 완전 검증을 대신하지 않는다.

완료 기준은 정책 소스 반영, 고정 identity/거절 검증, 새 경로 보호, 정상/취소/복원/새권한 결과와 process 종료의 각각 명시다. 실패하면 남은 기준을 미완료로 보존한다. Owner 수락은 실행 결과와 별도로 남는다.

## Initial Execution — Historical

정책·경로 검사·집중 테스트·사용 설명을 작성했다. 첫 집중 묶음의 source-normal process가 SIGABRT(-6)로 종료했다. timeout은 아니며 stdout/stderr는 모두0bytes다. 완료한 테스트 ID가 관측되지 않았으므로 코드 assertion 실패 또는 성공으로 판정하지 않는다. 별도 process group 부재는 확인했다.

실패·timeout 재시도 금지에 따라 같은 검사를 재실행하지 않았고, parent-O·admission/runner 합성 검사·보호 helper·공식 App Server·모델·worker·복원은 시작하지 않았다. 이 프로세스 실패의 원인은 미확정이다. 테스트 실행용 프로필과 공식 CLI runtime 정책은 별개이며, 이 결과가 공식 계정 연결의 재실패라는 뜻은 아니다.

새 loader·test·runner는 AST 문법/고정입력/정책 parameter 대응·변경 범위와 문서 링크를 정적으로 확인한다. 이 정적 확인은 미실행 테스트를 대체하지 않는다. 정책 template에 이전 검증 경로를 재결합하면 성공 정책과 byte-identical이다. 과거 Host22개/worker6회는 함수 AST·native source identity를 대조한 재사용 근거로만 남는다.

소스 반영은 완료했지만 집중·보호·U2 전체 완료 기준은 미달이다. 추가 runtime OS grant0, 실제 Core 적용0, Git commit/push/PR/merge0이다. 신규 기록은 Owner의 결과 검토와 실패 원인 축소·다음 실행 판단을 위해 보존한다. 원인 확인 없이 실패 호출을 반복하지 않는다.

## Initial Follow-Up And Impact — Historical

다음 검토 대상은 결과 출력 전 종료된 focused Python process의 원인이다. 기존 로그만으로 원인을 단정하거나 runtime 정책에 추가 예외를 넣지 않는다. 정상/취소/복원/새권한 검증은 집중·보호 gate 통과 뒤에만 가능하다. 이번 실행 묶음은 종료하며 미소비 횟수를 자동으로 재개하지 않는다.

일반 도입 권고는 현재 업데이트 불필요다. 이 변경은 source-only 검증 후보이며 설치 payload/기존 native/Core를 바꾸지 않았고, 공식 기본 경로 또는 제품 지원을 입증하지 않았다. 설치 상태와 Windows 적격성을 새로 확인한 것도 아니다. Owner의 결과 수락과 실제 도입은 별도다.


## 보정 재실행과 공식 Thread 시작 경계 — 2026-10-29

Owner가 보정 검사 프로필로 새 실행1회와 범위 내 실패·timeout 보정 재시도를 승인했다. 이전 누적108.105821분을 이어받고180분 중단/160분 신규시작·추가OS권한0을 유지했다. 이전 실패 원장과 source 복구본은 그대로 보존했다.

첫 보정에서도 Python이 SIGABRT(-6)로 종료했다. 검사 runner의 초기화용 directory-data와 결과 출력 경계를 기존 검증 범위에 맞추고 site 초기화를 제외한 뒤 테스트가 실제 실행됐다. 합성 실행 파일의 X_OK가 테스트 sandbox에 거절되는 fixture 문제는 이미 허용된 Python을 사용하는 방식으로 고쳤다. 실제 runtime 정책이나 loader를 완화하지 않았다. source 테스트13개가 normal/parent-O 각각 통과했고, 비실행 파일 거절도 포함했다.

task module directory 검색과 결과 저장 경계도 보정했다. admission7개 assertion은 정제 오류 관측 보정 후 통과했으나 summary 교체의 .next 파일 쓰기가 거절되어 해당 child는 exit1이었다. attempt-local 성공 결과를 보존하고 trusted parent가 summary를 기록하도록 고쳤다. 이 결과를 전체 process 성공으로 바꾸어 기록하지 않는다. 성공 단계 참조를 포함한 runner10개 검사는 별도 process에서 통과했다. 각 실패와 보정 입력을 유지했으며 통과한 source 검사를 반복하지 않았다.

새 위치의 실제 parent/exec child 보호 read/write12건, 허용I/O·미등록exec차단, 원문/identity 불변과 process 종료가 통과했다. 이 결과는 고정 공식CLI 정책과 해당 경로의 보호 검사다.

공식 배포CLI AppServer3회에서 계정과 고정 모델 catalog는 확인했지만 thread/start가 모두 실패했다. 두 보정 재시도는 URL·header·body·계정·오류 원문을 남기지 않는 고정 오류 분류를 보강했다. 마지막 실제 응답은 exec-policy-load·exec-policy-directory·user-rules-path·permission-error, errno1로 사용자 config home의 rules directory 열거 차단을 확인했다. 고정 공식 source에서도 thread 시작의 ExecPolicyManager::load가 rules directory를 읽으며 NotFound 이외의 오류를 반환하는 경로와 대응한다.

모델 turn0, worker0이므로 정상 편집·취소·복원·새권한 완료는 미실행이다. 계정 성공을 모델 작업 성공으로 확대하지 않는다. 현재 권한 밖의 rules 읽기를 추가하지 않았으며, 기존 규칙 삭제/변경/비활성화·인증 home 변경으로 우회하지 않았다. 이 지점에서 실행을 종료한다.

현재 source-only 정책·검사 구현과 focused/보호 근거는 확보했으나 U2 전체 완료 기준은 미달이다. 필요한 다음 범위는 기존 사용자 실행 규칙의 exact read 접근 여부 결정이다. directory 읽기 차단은 관측했으며 다음 개별 rules 파일 읽기는 source에서 추론한 후속 요구다. 제안은 비공개 실행 기록에만 있고 source 정책에는 적용하지 않았다. 충분성은 미검증이다. 기존 native/Core·설치 payload·제품 기본값·Windows·Git 통합은 그대로다. 일반 도입 업데이트는 현재 권고하지 않는다.


## Exact Rules Read Applied And Global Instructions Boundary — 2026-10-29

Owner가 기존 rules directory와 현재 파일 하나의 읽기 예외를 승인했다. 누적124.0200643분에서180분 중단/160분 신규시작 제한을 이어받고 기존 실패와 성공 근거를 보존했다. 범위 내 보정·재시도는 승인됐으며 이 두 경로 외의 추가 권한은 중단 조건이다. 앞의 초기 승인 설명에 있던 재시도 금지는 이 후속 실행에는 적용하지 않는다.

source 정책에 directory와 file의 literal parameter 두 개를 추가했다. loader는 canonical 기존 경로와 파일의 직접 부모 관계·보호 경계 중첩을 검사한다. 실제 경로/파일 집합/digest는 trusted Driver가 고정하며 모델이 선택하지 않는다. 재귀 읽기·쓰기·exec·네트워크 권한은 추가하지 않았다. 정책과 loader hash도 함께 고정했다.

변경된 loader의15개 테스트가 normal/parent-O 각각 통과했고, 새 path parent/exec child 보호 read/write12건·허용I/O·미등록exec차단과 process 종료가 통과했다. 이전 admission7assertion·runner10개 및 Host22개/당시worker6회는 변경하지 않은 함수와 입력에 한정해 재사용했으며 이번에 새로 실행한 결과로 계산하지 않는다.

공식 AppServer3회 모두 계정/catalog 및 thread/start를 통과했다. 첫2회는 turn/start 요청 뒤 도착한 startup warning에서 중단했고 turn 응답이나 모델 완료를 확인하지 못했다. 보정3회차는 startup 알림을 turn/start 전에 확인하여 모델 요청을 추가하지 않았다. 오류 분류 보강으로 global-instructions-read·global-agents-path·read-operation·permission-error 및 errno1을 직접 관측했다. 기존 전역 사용자 지침 파일 읽기 거절이며 rules 문제의 재발은 아니다. 정책 범위를 넓히거나 경고를 무시하지 않았다.

쓰기/검증 worker0, 정상 편집/취소/별도Host복원/새권한완료는 미실행이다. turn/start 요청2회는 이미 소비됐으며 결과 미확인으로 남긴다. 계정이나 스레드 성공을 모델 작업 성공으로 보고하지 않는다. 모든 소유 processgroup·관측child 종료와 identity·rules·기존 실패/binary/config/native 불변을 확인한다.

추가 후보는 전역 사용자 지침의 실제 대상 파일 하나에 대한 exact read다. 심볼릭 링크와 canonical target을 확인하고 metadata/digest를 task-private 기록에 고정했다. 허용하면 공식 CLI가 그 지침을 모델 문맥에 포함하므로 읽기뿐 아니라 그 입력 효과도 Owner 판단에 포함한다. 후보는 미적용이고 충분성도 미검증이다. 지침 삭제·변경·비활성화나 home 우회는 하지 않는다.

현 source-only 변경은 미커밋이며 결과 미수락이다. 기존 native/Core·설치payload·제품기본값·Windows 지원과 Gitrefs는 유지한다. 변경 파일은 bytes/mode/mtime를 검증한 외부 복구본으로 보존한다. 고유 실패·보정전코드·protocol·통과 근거는 Owner 결과/추가접근 판단과 후속검증까지 유지한다. 일반 도입 업데이트는 현재 권고하지 않는다.


## Global Instructions Read Applied; Code Mode Host Boundary — 2026-10-29

Owner가 전역 지침의 실제 파일 하나 읽기와 공식 모델 문맥 포함을 승인했다. 누적134.4364946167분에서180분 중단/160분 신규시작 제한과 기존 실패 기록을 이어받았다. scope 내 보정/재시도는 허용됐고 후보 외 권한은 중단 조건이다.

source 정책에 canonical GLOBAL_INSTRUCTIONS 파일 하나의 literal read를 추가했다. trusted Driver가 기존 symlink와 실제 target의 metadata/digest를 고정했다. loader의 기존 canonical/file-alias/protected-overlap 검사를 그대로 적용하며15개 normal/O 테스트와 보호12건이 통과했다. 사용자 지침 내용은 진단 로그에 저장하지 않았다. 이전 전역 지침 읽기 경고는 해소됐다.

공식App2회에서 계정/catalog/thread가 성공했다. turn/start 요청2회 중1회 응답을 관측했고 모델 완료는0이다. 두 실행 모두 Code Mode 경고로 worker 전에 종료했다. 관측 보정은 정확한 공개 direct-fallback 안내 하나만 구분하고 fail-closed/unknown/permission 경고는 계속 거절하도록 했다. 합성8건이 통과했다. 숫자 threadID에401이 포함되면 auth 오류로 오인하던 정제기의 부분문자열 분류도 보정했으며 첫 기록은 그대로 보존했다. 실제 다음 경고는 code-mode-fail-closed·code-mode-host-disabled였고 허용분기에 들어가지 않았다.

고정 source와 설치에서 별도 공식 Code Mode helper가 존재함을 확인했다. 현재 runtime 정책은 그 helper의 exec를 허용하지 않는다. 읽기/exec와 임시 feature 활성화 후보는 미적용이다. helper가 모델의 도구 호출 코드를 실행하는 의미와 기존정책상속·외부Host의 효과통제 경계를 다음 판단에 명시한다. 모델/metadata를 바꾸거나 경고를 무시하지 않았다.

정상편집·취소·폐기권한복원거절·새권한완료와 worker는0이다. 소유process/관측child종료, 기존기록·binary/config/native/rules/global instructions/identity불변과 source복구를 확인한다. source-only 변경은 미커밋/결과미수락이고 실제Core·설치payload·제품기본값·Windows·Gitrefs를 유지한다. 일반도입 업데이트는 현재 권고하지 않는다. 고유실패/보정/통과근거는 Owner결과·helper범위판단 및 후속U2검증까지 보존한다.


## Official Helper And Synthetic U2 Verification Passed — 2026-10-29

Owner가 같은 공식 CLI 설치의 Code Mode helper 파일 하나 읽기·실행과 임시 기능 활성화를 승인했다. 누적141.0494195333분부터 180분 중단/160분 신규 시작 제한을 이어받았다. 이전 실패와 미확인 turn 소비는 그대로 보존했고, 이번 실행에는 새 실패·보정 재시도가 없었다.

source 정책에 helper의 exact read/exec parameter를 추가했다. loader는 canonical 파일·중복 inode·보호 경계와 실행 비트를 검사하고, trusted Driver는 실제 helper의 hash/metadata와 실행 가능 여부를 고정했다. source 테스트16개가 normal/O 각각 통과했다. 임시 launch 설정은 code_mode_host=true·code_mode_host_grpc=false만 바꾸고 기존 shell/MCP/추가 도구 차단을 유지했다. 영구 config는 변경하지 않았다. effective config 검사에서 이 조합을 확인했다.

새 경로 parent/exec child의 보호 read/write12건, 허용 I/O와 미등록 exec 차단이 통과했다. 정상 실행은 문서 읽기→승인 구간 쓰기→DOC-LINKS→DOC-GFM→DOC-CLAIMS의 실제 worker5회와 모델 completed, 결과 봉인을 확인했다.

취소 실행은 읽기 worker1회 뒤 실제 write callback을 worker 시작 전에 보류하고 권한을 폐기했다. 같은 call과 새 call을 실제 dispatch에 주입해 모두 거절했고 문서 불변을 확인했다. 공식 turn/interrupt의 interrupted 완료와 process 종료도 확인했다. 늦은 요청 거절은 Host 주입 검사이며 모델이 실제 늦은 요청을 생성했다는 뜻은 아니다.

별도 Host process는 종료된 취소 실행의 journal/checkpoint를 검증해 복원했다. 폐기된 권한으로 같은 call과 새 call이 모두 거절됐으며 worker0, 원 journal/checkpoint·문서 불변을 확인했다. 이후 같은 합성 문서에 새 권한을 발급한 실행은 worker5회, 세 검증, 모델 completed와 봉인까지 통과했다. 복원된 과거 권한을 다시 연 것이 아니다.

이번 소비는 focused1묶음, 보호2process, AppServer/계정RPC/catalog/thread/turn 각3회, helper admission3회, 계획취소1회, 별도Host복원1회, 실제문서worker11회다. 각 AppServer에서 관측한 자식1개씩과 소유 processgroup의 종료를 확인했다. descendant sampling은 보이지 않은 detached daemon 부재의 증명은 아니다. helper admission은 예약한 session 수이며 kernel 전체 spawn 추적과 구분한다.

기존 입력·binary/config/native/rules/global instructions/helper/identity 불변, 최종 문서 내용·reference/sentinel 불변과 source 복구본을 확인한다. 합성 기능 검증은 통과했으나 별도 Reviewer 검토와 Owner 결과 수락을 대체하지 않는다. 공식 adapter의 제품 entry 연결·설치 payload·기본값 전환, 실제 업무/Core 적용, Git 통합·Windows·제품 전체 지원은 이번 결과에 포함되지 않는다.

현재 정책/loader/test/설명은 source-only 미커밋 후보다. 다음 판단은 이 개발 결과의 수락과 공식 adapter의 제품 연결 범위다. 일반 도입 업데이트는 현재 권고하지 않는다. 고유 성공·실패·실행 입력과 마지막 복구본/worktree는 결과 검토 및 구체적인 source 통합/공식 adapter 후속 결정까지 유지한다. 소비가 끝나거나 후속이 거절·대체되면 standing cleanup 기준으로 재평가한다.


## Owner Result Acceptance — 2026-10-29

Owner가 합성 source-only 공식 U2 정상·취소·폐기권한복원거절·새권한완료 결과를 수락했다. 제품연결·설치payload·실제업무/Core·Git·Windows의 수락으로 확대하지 않는다. 후속은 [공식adapter제품연결](FEAT-20261029-002-official-adapter-product.md)이 소유한다. 이전실패와당시미수락상태는 역사로 보존한다.
