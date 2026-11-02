# 공식 실행 경고 처리와 읽기 후 취소의 제품 소스 반영

- 상태: Done — 제품 소스 반영과 오프라인 검증 결과 Owner 수락
- 시작일: 2026-11-02
- 완료일(actual_end): 2026-11-02
- Owner: 사용자 / Driver: Codex / Reviewer: Claude
- 기준: [공식 실행 조합의 제한 수락과 후속 계획](CHORE-20261102-003-official-runtime-confirmation.md#product-source-follow-up-proposal)

Owner는 제품 소스 반영 묶음 전체를 선택했다. 시작 HEAD는 c1270391a0e9f262a4e05fc925c6424619171cb6이며 기존 미커밋 운영 진단 변경은 보존한다. 앞선 정상과 취소 관측은 서로 다른 격리 후보에 속한다. 이 Work는 최종 후보의 제품 변경과 제품 소스에서의 오프라인 검증을 소유한다.

## 범위와 완료 기준

1. 공식 실행 어댑터와 Host에 고정 0.165.0 경고의 1회 허용, 초기화 진단과 후속 stderr 거부, worker_limit=1 읽기 후 최대 5초의 취소 접수 및 같은 턴 응답 확인을 반영한다. 구조화된 실행 결과와 보존된 journal/status 계약을 구분한다.
2. 저장소의 합성 fixture로 정상 완료·외부 취소·거부 및 보존/종료 경로를 대조하고 제품 문서를 동기화한다. macOS 공식 패키지를 로컬에 준비해 관리 파일과 생성 진입 파일을 대조한다. 운영 설치나 공식 모델 호출은 하지 않는다.
3. 계획 및 결과 리뷰, 범위 내 보정과 영향 검사까지 한 묶음으로 처리한다. 새 공식 증거를 요구하거나 권한·핀·시간 계약 확대가 필요한 경우 중단한다. 결과 수락은 Owner 판단이다.

예상 60–90분, 총 경과 상한 120분(준비와 리뷰 대기 포함). 기존 구독 경로 비식별 정적 리뷰 2회 이내, 각 240초, 공식 모델 실행 0회. Windows·실제 설치·adopter 적용·커밋·Git 게시·공개는 보류한다.

## R0 계획 리뷰와 Driver 처분

Claude Opus 5.5, 세션 ee1aaf34-a108-4e74-b60a-06dc42608e29, 53.701초. 비식별 변경안과 계획에 대한 정적 리뷰로 실행 도구는 제공하지 않았다. 입력 digest 59aa181b07af768629d2b4e30ba785381b8208b88fc9c242fe44267541b3b06d. Owner가 승인한 범위에서 다음과 같이 처분했다.

- 차단 1·2 defend. 기존 run의 finally는 Host.fail이 내구적인 terminal 상태를 반환하면 예외를 해제한다. 이때만 결과 진단을 붙이며 미해결 예외는 기존 실패로 남긴다. Rpc 생성자는 stdout/stderr를 모두 비차단으로 설정한다. 두 전제는 원본과 실제 합성 Host 검사에서 확인한다.
- interrupt 상태 defend. 기존 interrupted는 시도 표시이며 새 interrupt_confirmed는 같은 턴의 interrupted 응답 확인이다. 기존 cancelled 사유와 capsule 형식을 재사용한다.
- suffix 대기 중 취소·마감 revise. 기존 권한의 취소 검사는 유지하고 대기를 중단한 원인을 보존한다. 이후 close가 같은 stderr를 다시 판정해 원인을 바꾸지 않도록 거부 상태를 고정한다.
- 나머지 필수·선택 accept. 5초 대기 중 실패의 완료 계수·문서 효과·결과 송신, close 실패, 결과 필드 위치 및 이전 기록 호환을 검사한다. 5초 동안 새 stdout 콜백을 처리하지 않는 한계, 두 시간창이 기존 마감을 연장하지 않는 점과 진단 바이트 수의 의미를 문서화한다. 독립적인 기한 및 실제 파이프/Host 검사를 결합한다.

~~~~markdown
# R0 정적 계획 리뷰 (diff sha256 0926…14 기준, 원본 미열람)

**처분: 조건부 보류.** 아래 차단 2건을 해소하거나 원본에서 반증한 뒤 이식하십시오.

## 차단

1. **`runtime_first_failure` 도달 불가.** 결과 키는 `if error is not None: raise error` 다음에만 붙습니다. 초기화 실패는 항상 예외로 끝나므로 이 기록은 사실상 생성되지 않습니다. 실패 시 기록을 남기는 다른 경로가 원본에 없다면, raise 전에 journal이나 예외에 기록해야 합니다. 이 기록이 어디에 남는지가 상태 계약에 해당하므로 변경 여부를 명시하십시오.
2. **stderr non-blocking 전제.** `next()`는 매 루프 `check_stderr()`를 무조건 호출하고, `BlockingIOError`로만 빠져나옵니다. 그런데 diff에서 `set_blocking(False)`는 close에만 있습니다. 원본 spawn에서 stderr가 O_NONBLOCK이 아니면 `os.read`가 블록되어 RPC 전체가 정지합니다. 원본에서 확인하고, 없으면 spawn 직후 설정을 추가하십시오. `__new__` fixture에도 같은 fd 상태가 필요합니다.

## 필수

- **`rpc.interrupted` 속성.** `__init__`에 추가된 필드에 없습니다. 원본에 없으면 AttributeError가 납니다. 다른 곳은 `getattr`을 쓰므로 일관성을 맞추십시오. `interrupt_confirmed`와는 의미가 다르다는 점도 테스트로 고정하십시오.
- **suffix 대기 중 예외 상태 미정.** `remaining()`이 `CancelRequested`나 `TimeoutError`를 던지면 `stderr_refused`와 `path_warning_mode`가 미설정인 채 101+바이트가 소비된 상태로 남습니다. 그러면 close의 `require_eof` 경로에서 나머지 바이트가 `protocol_refused`로 재분류됩니다. 또 취소는 read 이후에만 허용한다는 계획과도 충돌합니다. suffix 대기 중에는 취소를 검사하지 않거나, 예외 시 `stderr_refused=True`와 `_init_failure`를 확정해야 합니다.
- **`read_limit_reason`의 사후 실패.** 성공한 read 뒤 `state.need(...'deadline'/'protocol_refused')`가 host의 except로 들어가 `worker_failed`로 바뀝니다. 다음을 테스트하십시오.
  - `completed` 이중 계상이 없는지
  - `effect_status`가 none으로 유지되는지
  - 응답이 미송신 상태인지
- **`'cancelled'` revoke 사유.** `reason_code`나 문서의 열거에 없으면 상태 계약 변경입니다. 확인 후 문서화하십시오.
- **close의 `check_stderr(require_eof=True)` 실패.** `close_result`가 미설정인 채 finally로 빠집니다. close failure 경로의 기존 기록 fixture에 미치는 영향을 검증하십시오.
- **신규 public 결과 키 문서화.** 대상 키는 `runtime_first_failure`, `initialize_path_warning_*`, `cancel_seen_after_read`, `runtime_interrupt_confirmed`입니다. 기존 결과 객체를 엄격 비교하는 fixture를 갱신하십시오.
- **스크립트형 런타임 결함 경로.**
  - 핀 불일치 시 경고 거부
  - 경고 2회째 거부
  - 101바이트 후 suffix의 분할 도착, 불일치, 초과, EOF, 50ms 초과
  - 경고와 stdout이 같은 select에 도착하는 경우: stdout 미처리 확인
  - 초기화 외 stderr
  - held/queued 메시지 경로의 stderr 선검사
  - 다른 grant 표식, 4.9s/5.1s 취소 경계, grant 만료가 5s보다 먼저 오는 경우

## 선택

- `_init_failure`의 `byte_count`(=size)와 diagnostic의 `refused_bytes`가 다릅니다. 의도라면 주석을 남기십시오.
- 50ms 경계 테스트는 실제 시간 대신 monotonic 주입이나 pipe 쓰기 제어로 결정적으로 만드십시오. CI 부하 시 flaky해질 수 있습니다.
- `read_limit_reason`의 5s 동안 stdout을 drain하지 않습니다. 64KB를 넘으면 CLI가 블록됩니다. 허용 범위로 판단하면 문서에 명시하십시오.

## 명시 사항

- **시간:** 기존 마감에 신규 상한 50ms(suffix)와 5s(read 후)가 추가됩니다.
- **핀:** 0.165.0 두 해시를 하드코딩하며 핀 자체는 변경하지 않습니다.
- **원문 미보존:** 경고 바이트는 비교만 하고 저장하지 않습니다(적절).
- **상태 계약:** `'cancelled'` 사유, 신규 결과 키, 실패 기록 위치가 변경 가능 지점입니다.
- **개인 경로:** diff에는 없습니다. 생성 payload 비교 시에도 다시 확인하십시오.
~~~~

## 제품 반영과 검증 결과

제품 소스 반영과 오프라인 검증을 마쳤다. 수락 대상은 이번 두 모듈, 관련 테스트, 공식 실행 문서와 이 소스에서 생성한 패키지의 정적 일치다. 두 선행 후보의 공식 관측 범위는 기존 Work에 유지한다.

- 초기화 첫 stderr가 지정 CLI/helper의 104바이트 경고와 일치한 경우와 정확한 101바이트 뒤 50ms 미만에 3바이트를 완성한 경우를 구분한다. 다른 접두부, 불일치, 중복, 여분, EOF와 기한 도달은 거부한다. 진단에는 고정 분류와 크기만 사용한다. 과거 첫 읽기 101바이트 관측은 계속 미분류다.
- 단일 읽기 worker가 성공하고 종료된 뒤 최대 5초 동안 같은 grant의 취소를 받는다. 이 구간에 확인한 취소에는 읽기 결과를 보내지 않는다. 읽기 완료 기록·문서 원본을 보존하고 사유만 응답한 뒤 턴 중단을 요청한다. 기한 도달 시에는 정상적으로 끝난 읽기 결과와 한도 소진 사유를 사용한다. 접수, 동일 턴 런타임 확인, 문서 효과와 프로세스 종료는 서로 다른 근거다.
- 수락된 격리 후보에서 가져온 동작에 세 가지를 보정했다. 접미부를 기다리는 중 취소·마감이 먼저 오면 거부를 고정해 종료 처리에서 원인을 바꾸지 않는다. 프로세스 부재 확인이 실패하면 기존 종료 미확인 근거를 보존한다. 대기 중 외부 취소를 확인한 뒤에는 문서 본문을 런타임에 전달하지 않는다. 보정 후 두 제품 모듈은 마지막 정적 리뷰 입력과 동일하다.

### 오프라인 검사

기존 macOS 네트워크 차단 프로파일, 격리된 합성 프로젝트, Python 3.14.7로 실행했다. 정상·취소 연결 검사는 실제 Host와 파이프, 로컬 스크립트 런타임 및 worker를 사용한다. 외부 취소는 별도 CLI 프로세스로 게시했다. 최초 Git 준비 실패는 실패 원장에 남겼다. 같은 격리에 이미 허용된 Xcode Git 경로를 우선한 뒤 해당 4건이 전부 통과했다.

| 검사 기록 | 결과 | 판정 범위 |
| --- | --- | --- |
| core-01 | 83건 중 79 통과, 4건 fixture 준비 오류 | admission, 프로세스 정리, 송신, 상태 판독, 정상·취소 Host 경로. 오류 4건은 합성 프로젝트의 git init 단계 |
| focus-01 | 12/12 통과 | 위 4건, 단일·분할 stderr 및 거부 경계, 단일 읽기 취소·만료 |
| optimized-01 | 29/29 통과 | 부모 Python 최적화 모드의 경고, 정상·취소, 내용 검사와 운영 진단 |
| port-final / entry-final | 각각 4/4 통과 | 취소 뒤 본문 미전달, 미취소 대조, 다른 턴 응답, 초기화 첫 실패, 제품 진입점·lock·마감·읽기 실패. entry-final은 부모 최적화 모드 |
| review-edges | 2/2 통과 | 대기 중 실제 stderr 수신 후 추가 송신 0건. grant 벽시계만 만료 지점으로 이동해 실제 읽기·실패 응답·같은 턴 중단·종료 확인 |

집중 검사 전체에서 중복을 제외한 테스트 이름 116개가 통과했고 건너뛴 사례는 없었다. 첫 검사 83건 전체를 최종본으로 되풀이한 수치가 아니다. 기존 v1 기록과 v2 journal/status 판독 검사를 재사용했다. 실행 시점에만 반환하는 추가 필드는 과거 기록으로부터 복원하지 않는다.

### 패키지와 기존 작업 보존

공급 파일과 소스에서 설치 대상 형태의 macOS 패키지를 오프라인으로 생성했다. 기본 프로필 30개, 공식 실행 프로필 48개 관리 파일을 생성 입력과 대조하고 product.tar의 78개 멤버 내용을 전부 비교했다. 기존 격리 후보와 공식 프로필의 44개는 바이트 단위로 동일하다. 차이 4개는 생성 진입 파일의 배포 헤더, 공식 실행 문서, 두 제품 모듈이다. 진입 파일은 격리 위치를 가리키는 헤더를 제외한 본문이 같고, 소스에 격리 진입 파일을 복사하지 않았다.

- 최종 공식 프로필: product-release-3fc49083937edb3955b597d0
- 매니페스트 SHA-256: 2285b801db75f43eb3ea15f9408860bbda2122f2fa72cbf39f44d645e4663c36
- 이전에 수락된 미커밋 파일·기록 10개를 시작 기준과 대조했다. 안내서와 인덱스의 이번 추가분을 분리하면 기존 내용이 모두 일치한다. 기존 검증 실패 및 소비 원장은 그대로 유지한다.

## R1 결과 리뷰와 Driver 처분

Claude Opus 5.5, 세션 b69cb9eb-5db1-40aa-8190-5d720b3e1035, 70.771초. 입력 SHA-256 7908dfb520dd8a4897a110b6f1e5b3bff384c7a6f28861bc1ff81e6996fe1ea1. 두 회차 모두 기존 Pro 경로, 단일 턴, 도구·테스트 실행 없이 종료했다. 리뷰 전후 입력 digest가 일치했다.

~~~~markdown
# R1 정적 리뷰 (재현 없음)

모든 판단은 발췌 코드의 정적 추론입니다. 직접 실행하거나 재현한 항목은 없습니다. Driver 검사 결과는 보고된 그대로 참조했으며, 이 리뷰는 승인이나 독립 실행 증거가 아닙니다.

## 차단 사항

발췌 범위에서 동작상 차단 결함은 찾지 못했습니다.

## 기존 방어로 충족되는 R0 지적

- **50ms 접미부**: `remaining()`이 취소·RPC/실행 마감·grant 만료를 50ms보다 먼저 검사합니다. `CancelRequested`와 `TimeoutError`는 `stderr_refused`를 고정한 뒤 다시 던집니다. `reason_code`가 `cancelled`/`deadline`을 보존하고, 기한은 `min`으로만 계산되어 연장이 없습니다.
- **추가·불일치·EOF·두 번째 stderr**: 각각 고정 코드로 거부됩니다. 이후 읽기에서는 `first`와 `path_warning_mode` 때문에 재허용되지 않습니다.
- **5초 구간 실패**: `pending`이 이미 비어 있어 `complete_pending`이 다시 계수하지 않습니다. 응답은 `ok:false` 1회이며 내용이 없습니다. `stderr` 거부 시에는 `send` 내부의 `check_stderr`가 송신을 막습니다.
- **취소 확인 시**: 문서 내용 없이 사유만 응답합니다.
- **인터럽트**: `interrupted`(시도)와 `interrupt_confirmed`(같은 턴의 `interrupted` 확인)가 분리되어 있습니다.

## 명시적 수락 조건

1. **파이프 순서 비보장**: 경고가 initialize 응답보다 늦게 도착하면 `in_initialize=False` 상태라 거부됩니다. 첫 읽기가 101바이트 미만이어도 `path_warning_prefix`로 거부됩니다. 둘 다 "미래 출력 비예측"을 수락해야 성립합니다.
2. **5초 경계**: 정확히 5.0초에 본 취소는 `worker_budget_consumed`가 됩니다. 구간 밖 취소에서는 읽기 내용이 전송됩니다.
3. **접미부 마감 실패의 원인 표기**: `runtime_first_failure`가 `source:'other'`로 남고, 접미부 취소 시에는 기록이 없습니다. stop_reason은 보존됩니다. 진단 세분화가 필요하면 별도 과제입니다.

## 증거 공백 (차단 아님, 확인 권고)

- 최종 송신 차단 적용 후 재검사는 4건뿐입니다. 83건 전체를 최종 모듈로 다시 통과시킨 기록이 없습니다.
- 5초 구간 중 stderr 거부는 단위 테스트에서 `check_stderr`를 mock 처리해 통합 경로로 검증되지 않았습니다.
- grant 만료(실행 마감 이전) 직후의 실패 응답과 인터럽트 송신도 실제 경로로 검증되지 않았습니다. 정리 동작이라 기한 연장으로 보지는 않습니다.

## 범위 밖 기존 문제 (이번 변경과 무관)

- `run`의 except 블록에서 `host.cancelled()` 예외가 원 오류를 대체할 수 있습니다.
- `close` 중 EOF 확인이 거부되면 `close_result`가 남지 않아, 재호출 시 `previous-close-unconfirmed`가 됩니다. 보수적 결과입니다.
- finally의 스트림 `close` 예외가 `sel.close()`를 건너뛸 수 있습니다.
~~~~

- 차단 없음. R0의 두 전제는 실제 소스와 Host 연결 검사로 확인했다. 초기화 단계 거부에 고정된 runtime_first_failure가 실행 결과에 나타나고 원문이 capsule에 없는 것을 검사했다.
- 세 수락 조건을 유지한다. 초기화 응답 처리 뒤 도착한 경고나 101바이트 미만의 첫 읽기는 거부한다. 5초 경계에 도달하면 worker 한도 소진 경로를 따른다. 접미부 대기를 취소하거나 실행 기한이 앞선 경우 최종 사유로 확인하며 stderr 상세 분류는 제한된다.
- 두 검증 공백을 review-edges로 보완했다. 실제 파이프로 보낸 stderr가 문서 송신을 막았고 종료도 확인했다. 별도 검사에서는 어댑터의 벽시계만 제어해 실행 마감보다 grant 만료가 먼저 오는 조건에서 내용 없는 실패 응답 1회와 인터럽트 확인을 검증했다. 전체 검사의 재실행은 영향 범위에 따라 생략했다.
- 리뷰 후 변경은 테스트·합성 fixture·안내 문구에 한정했다. 제품 동작은 리뷰한 두 모듈과 같다. 리뷰가 언급한 기존 예외 처리와 보수적인 close 재호출 결과는 이번 범위 밖으로 구분한다.

## Owner 판단과 보존

2026-11-02 Owner가 두 제품 모듈의 반영과 오프라인 검증 결과를 수락해 이 Work를 완료했다. 수락 범위에는 정상·취소·거부 경로의 합성 관측, 기존 기록 판독, 최종 패키지 두 프로필의 관리 파일 대조, 문서 검사와 Claude 계획·결과 리뷰 처분이 포함된다. 위 완료 기준 1–3은 이 범위로 충족했다.

최종 공식 프로필 `product-release-3fc49083937edb3955b597d0`의 공식 재실행은 미검증이다. 선행 정상 완료와 분할 경고 수신 후 외부 취소는 각각 다른 격리 후보에서 관측했다. 이번 묶음의 공식 세션·턴은 0회, Claude 리뷰는 2/2회다. 기존 실패와 소비량은 이월한다. Windows 착수·실제 설치·adopter 적용·커밋·Git 게시·공개는 계속 보류한다.

기존 Work와 격리 관측 증거는 원래 위치에 보존했다. 비공개 작업 기록 colvia-official-runtime-source-port-20261102에 실패·리뷰·검사 원장과 최종 패키지(lab/reviewed-package/distribution)가 있다. 다음 통합 담당자가 수락한 변경과 최종 패키지를 대조할 때까지 해당 기록과 패키지를 보존한다. 중간 빌드 두 개는 각각의 고유 매니페스트·제품 아카이브·진입 도구와 결과를 보존했다. 아카이브 또는 최종 공급 파일과 바이트·파일 모드가 일치한 중간 복사본 166개와 종료된 빈 검사 디렉터리를 정리했다. 사용 중인 작업 트리와 최종 배포본 위치는 유지했다.

## 로컬 커밋 범위와 순서 (제안)

기준 HEAD는 `c1270391a0e9f262a4e05fc925c6424619171cb6`이다. 선행 두 Work가 수락된 시점의 추적 파일 패치와 미추적 파일 목록을 경계로 삼는다. 두 커밋에 공통인 문서는 공식 실행 안내와 개발 인덱스다. 10개와 13개 경로에서 이 두 문서가 겹쳐 전체는 21개 경로다.

1. `feat(doctor): 공식 실행 입력의 로컬 진단 추가` — 선행 수락분 10개 경로. 공통 실행·운영 진단(FEAT-002)과 서로 다른 격리 후보의 공식 관측 기록(CHORE-003)을 함께 묶는다.
   - 구현·테스트 5개: `distribution/macos.py`, `distribution/manager.py`, `src/hv2ref/cli.py`, `src/hv2ref/official_entry.py`, `tests/test_runtime_diagnosis.py`.
   - 문서 5개: `docs/REFERENCE.md`, `docs/OFFICIAL-EXECUTION.md`의 ‘실행 도구 구성 확인’, `docs/development/FEAT-20261102-002-common-execution-operations.md`, `docs/development/CHORE-20261102-003-official-runtime-confirmation.md`, `docs/development/README.md`의 두 선행 Work 완료 행과 당시의 제품 반영 후보 행. 이 시점의 후보 행은 CHORE-003의 제안으로만 연결한다.
2. `fix(runtime): 초기화 경고와 읽기 후 외부 취소 처리` — 이번 수락분 13개 경로.
   - 제품 2개: `src/hv2ref/official_adapter.py`, `src/hv2ref/official_host.py`.
   - 테스트·fixture 8개: `tests/fixtures/official_rpc_fixture.py`, `tests/fixtures/official_scripted_server.py`, `tests/test_official_adapter_v2.py`, `tests/test_official_admission.py`, `tests/test_official_payload_v2.py`, `tests/test_official_process_v2.py`, `tests/test_official_s1b.py`, `tests/test_official_startup_stderr.py`.
   - 문서 3개: `docs/OFFICIAL-EXECUTION.md`의 ‘초기화 중 경고 처리’와 ‘취소와 상태’의 읽기 후 취소 설명, 이 PATCH-004 Work, `docs/development/README.md`의 PATCH-004 완료 행과 기존 후보 행의 완료 연결.

두 메시지에 제안하는 공동작성자 표기는 다음과 같다.

```text
Co-authored-by: Claude Opus 5.5 <noreply@anthropic.com>
Co-authored-by: Codex <noreply@openai.com>
```

외부 실행·리뷰 원장, 관찰 스크립트, 생성 배포본은 커밋 경로에서 제외한다. 이 순서는 변경 분리 계획이며 실제 커밋은 별도 결정이다.
