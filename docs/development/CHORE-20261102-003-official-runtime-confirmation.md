# Official Runtime Confirmation

- 상태: Done — Owner가 두 격리 후보에서 각각 관측한 결과를 수락함
- 완료일(actual_end): 2026-11-02
- 시작일: 2026-11-02
- Owner: 사용자 / Driver: Codex / Reviewer: Claude
- 기준: [수락된 공통 실행 Work와 후속 r2](FEAT-20261102-002-common-execution-operations.md#official-runtime-follow-up-plan--r2-proposal-only). 해당 Work의 Done과 수락 범위는 유지한다.

## Authorization And Scope

Owner가 r2대로 추가 4시간, Claude 최대 2회·각 240초, 공식 실행 최대 2세션·2턴·총 10분을 승인했다. 진입 준비 45분, 범위 내 준비·검사·안내 보정과 정상/취소 검증·결과 리뷰를 한 묶음으로 수행한다. 앞 Work의 R0 재리뷰와 5개 계획 보완을 재사용하며 같은 계획 리뷰를 반복하지 않는다.

기존 CLI/helper 핀, 실행 정책, ChatGPT 인증 유형과 고정 모델·effort, 권한·승인 의미를 유지한다. 전용 합성 검증 공간과 실제 제품 run 경로만 사용한다. Windows 착수·실제 설치·adopter 적용·커밋·Git 게시·공개는 보류한다. 기존 실패·소비량을 보존하고 미계측 총량을 새로 주장하지 않는다.

시작시각 2026-11-02 14:46:28 KST(최초 기록, 진입 읽기 포함), 추가 상한 18:46:28 KST, 진입 준비 상한 15:31:28 KST. 예상 1.5–3시간이며 검사·리뷰 대기를 포함한다. 통신·권한·종료 불명·인증/모델 불일치·입력 drift·한도 도달은 남은 live 전체를 재시도 없이 중단한다. 라이브 전 바이트 고정, 요청/fixture/digest, 취소와 판정 조건은 승인된 r2를 그대로 따른다.

## Completion Criteria

1. 실제 사용할 기존 조합과 현재 입력·제품 후보·정책 identity 확인 또는 정확한 진입 중단 사유.
2. 가능할 때만 실제 제품의 정상 1회·읽기 후 취소 1회와 효과/종료/범위 밖 보존 확인. 미실행/실패를 구분.
3. 필요한 집중 검사와 결과 리뷰·Driver 처분, 원장과 실패 보존, 정확한 다음 판단. 결과 수락은 Owner에게 남긴다.

## Current Evidence

- 현재 source HEAD와 수락된 변경면을 확인했다. 이전 Work에서 수락한 제품 코드·문서 바이트를 재사용한다.
- 과거 공식 제품 입력에 기록된 보존 CLI/helper가 존재하고 현재 제품의 두 핀과 일치한다. 일반 설치 경로의 두 파일은 다른 해시다. 보존 경로가 실제 사용할 후보이며 설치 경로를 교체하지 않는다.
- binary identity 확인은 설정/계정/모델/실행 성공 근거가 아니다. 현재 입력 준비와 실제 제품 진입 확인을 이어간다.

## Entry Stop

보존된 공식 입력의 다섯 pinned 파일을 읽어 대조했다. CLI/helper 두 파일과 rules/전역 지침은 일치하지만 CODEX_CONFIG가 과거 입력 digest와 다르다. 현재 설정의 provider 조건은 허용 형태이고 별도 instructions 값도 없으나, 이는 전체 유효 설정·원래 승인·실행 성공의 증거가 아니다. 변경 원인과 변경 시점은 확인하지 않았다.

r2의 필수 digest 불일치 중단 조건을 적용하여 live를 시작하지 않았다. binary 다운로드, 설정 수정, 핀 교체, 임의 digest 갱신은 없다. 계정/모델 preflight, 정상/취소 실행 모두 미실행이며 2세션·2턴을 보존한다. 현재 선택된 새 runtime 입력도 아직 만들지 않았다.

이 관찰은 설정이 위험하거나 제품 결함이라는 판정이 아니다. 과거 입력을 그대로 재사용할 수 없다는 증거다. 최소 재개 후보는 현 설정을 유지한 채 비밀정보를 출력하지 않는 계약 관련 정적 비교 후, 변경된 설정 digest를 새 실행 입력으로 명시적으로 고정하는 것이다. 이 새 입력 확정은 이번 중단을 자동 해제하지 않는다. 설정이 계약을 만족하지 않으면 변경하거나 완화하지 않고 계속 중단한다.

## Entry Review And Disposition

Claude Opus 5.5, session 33c7c14d-2682-4efc-a57d-9db42d33412f, 48.922초. 정적 리뷰 1/2회, 정상 종료·입력 drift 없음. Driver는 과거 입력 재사용 불가를 전체 중단으로 넓혀 해석했던 처분을 revise했다. 실행 중 불일치나 권한 실패는 발생하지 않았다. r2가 현재 입력을 준비 단계에서 고정하도록 이미 승인했으므로 새 승인을 만들거나 실패 live를 재시도하는 것이 아니다.

필수 보완 1–4 accept: 과거 전체 실행 근거는 새 설정 조합의 성공 증거로 쓰지 않는다. 현재 제품 계약과 비교하고 키 이름·분류만 보존한다. 실제 계정/모델 조건은 기존 단회 preflight에서만 관측한다. 다섯 파일 중 현재 설정 digest만 달랐으며 설정 자체는 바꾸지 않고 별도 runtime 입력 파일에 한 번 고정했다. 이후 변경은 재고정 없이 중단한다. 기존 원문·최초 관찰·보수적 일시 중단 기록과 시간은 보존한다.

정적 분류: 모델/effort/tier/notify는 고정 인수, plugin/MCP/hook/memory/context 기능은 기존 비활성화, TUI/desktop은 UI 설정, project trust는 고정 실행 권한을 대체하지 않는다. shell 환경 설정은 비활성화된 shell 도구에 해당하며 Host의 CLI 환경은 별도로 제한한다. 남은 구형 js_repl feature 키는 지정 CLI 버전의 소스와 제거 키 테스트에서 무시되는 키로 확인했다. 이 대조는 정적 근거이며 실제 effective config 판정을 대체하지 않는다.

~~~~markdown
## 판정: 조건부 재개 가능, Owner 재승인 불필요

**중단 처분:** 과거 runtime-input을 그대로 쓰는 경로만 중단하는 것이 맞습니다. 묶음 전체를 중단할 사유는 아닙니다.
- r2의 고정 기준은 payload identity, CLI/helper 핀, macOS 정책입니다. 다섯 입력 digest는 "준비 중 고정"하도록 되어 있어, 과거 config digest는 r2의 필수 digest가 아닙니다.
- 과거 입력으로 실행하면 `runtime-input-drift:CODEX_CONFIG`가 나지만, 이는 오래된 입력과 현재 설정의 차이입니다. 실행 중 drift로 기록하면 안 됩니다.
- 새로 고정하는 것은 r2가 지시한 준비 단계이고 핀 교체도 아닙니다. live가 0회라 슬롯 소비도 없습니다.

제안한 순서(비교→명시적 고정→미사용 슬롯 재개)를 승인합니다. 단, 아래 보정이 필요합니다.

## 필수 보정

1. **근거 재사용 축소:** r2는 원래 공식 실행 근거를 tuple 해시가 같을 때만 재사용하도록 합니다. config가 달라졌으므로 과거 공식 정상/취소/권한 복원 거절 근거는 새 tuple의 근거로 쓸 수 없습니다. 과거 관측으로만 표시하고, 빠지는 항목은 새 관측 또는 미관측으로 보고합니다.
2. **비교 기준 변경:** 과거 config 원문이 없으면 diff로 원인을 밝힐 수 없습니다. 따라서 과거 설정이 아니라 현재 제품 계약과 비교하고, 원인/시점은 미확인으로 남깁니다.
3. **비교 범위 확대:** `runtime_input()`의 provider/instructions 검사만으로는 부족합니다. 아래 항목도 정적으로 분류합니다.
   - 모델·effort, 승인·sandbox, profile
   - base URL, MCP·hook·notify, shell 환경, feature 설정
   - 알 수 없는 키: 분류가 안 되면 통과시키지 않고 중단

   출력은 키 이름과 판정만 남깁니다. config 값에 비밀이 있을 수 있으므로 값은 기록하거나 전송하지 않습니다.
4. **판정 시점 분리:** 정적 비교로는 계정과 모델 목록을 판정할 수 없습니다. 기존 preflight에서 세션당 1회만, `type=chatgpt`와 low 지원 여부만 확인합니다. 별도 probe는 추가하지 않고, 동일 개인 계정과 실제 응답 모델은 미관측으로 둡니다.

## 재개 조건

- **고정:** 비교한 bytes와 고정한 digest가 같아야 합니다. 다르면 다시 고정하지 않고 중단합니다.
- **일회성:** 재고정은 이번 1회뿐입니다. 이후 어떤 불일치든 실제 drift로 보고 남은 live 전체를 중단합니다. CLI가 세션 중 config를 다시 쓴 경우도 같습니다.
- **기록:** 과거 runtime-input은 덮어쓰지 않고 새 파일로 만듭니다. 새 파일에는 과거·현재 digest와 변경 입력이 `CODEX_CONFIG` 하나뿐임을 남깁니다.
- **순서:** 새 입력 identity를 고정한 다음 preview digest를 기록하고, 그 뒤 첫 live를 시작합니다.
- **시계:** 45분과 240분 시계는 리셋하지 않습니다. 재승인 대기가 없으므로 이 중단 시간도 포함되며, 45분을 넘겼다면 live 없이 중단합니다.
- **Claude 슬롯:** 이번 판단은 실질적 계획 변경이 아니므로 추가 계획 리뷰는 없습니다. 이 리뷰가 슬롯을 썼다면 남은 슬롯은 결과 리뷰에 씁니다.

**Owner 판단으로 넘길 경우:** 계약 비교에서 불일치나 미분류 키가 나오면 설정을 고치지 않고 중단한 뒤 Owner에게 보고합니다. 이 경우 현재 설정을 수정하거나 별도 자격 검증을 하려면 새 결정이 필요합니다.

~~~~

## Actual Product Entry Result

현재 입력의 최종 격리 배포본 doctor는 pass였다. 합성 Work 준비는 legacy interpreter를 사용한 보조 코드 때문에 HV2-WORKSPACE-RUNTIME으로 한 번 거절됐고, 정확한 managed Python으로 보정한 뒤 두 fixture와 미리보기를 준비했다. 권한 실패가 아니라 결정적인 fixture 진입 오류였으며 실패·종료 근거를 보존했다. 제품/정책 바이트는 바꾸지 않았다.

정상 시나리오 단회 execute는 initialize RPC만 예약한 뒤 protocol_refused로 종료됐다. account/read, model/list, thread/start, turn/start와 worker는 실행하지 않았다. public status는 revoked-before-launch, document_write_effect=none, process_observation=closed다. 외부 controller group과 기록된 runtime process 부재도 확인했다. 호출 프로세스 exit 0은 정상 작업 완료의 근거가 아니다.

지정 문서·참조·루트 sentinel과 설치 진입 파일은 준비 때 digest와 일치하며 고정 runtime 입력도 그대로다. 한편 넓은 파일 보존 비교는 false였다. 새 실행 lock을 제외하지 않은 oracle이며 비교 전 전체 map을 내구성 있게 저장하지 않아, 모든 control metadata가 동일했다는 독립 주장은 하지 않는다. expected lock은 제품이 만드는 경로로 확인했으며 이 결과를 승인 밖 문서 변경으로 단정하지 않는다.

기록의 runtime diagnostic 101 bytes는 원문을 남기지 않으며 stderr, RPC error, runtime diagnostic이 같은 reason/phase로 축약된다. retained runtime log는 0행이다. 따라서 네트워크·설정·초기 이벤트/응답 중 어느 원인인지 확정할 수 없다. raw 인증/설정 원문을 추가 수집하거나 재실행하지 않는다.

정상 1세션을 소비했고 모델 turn은 0회다. 정상 실행의 선행 조건이 실패하여 취소 시나리오도 시작하지 않는다. 공개 지원·실제 설치·adopter 자격은 그대로 미확인이다.

### Minimal Next Decision

현재 조합을 바꾸거나 재시도하기 전에, 보존 코드에서 초기화 진단의 최소 구분(예: stderr/RPC error/notification 및 허용된 고정 코드만)을 추가할 위치와 원문 미보존 조건을 읽기 전용으로 확정하는 것이 다음 후보다. 초기화 원인 구분이 가능한 입력을 만든 뒤 별도 승인된 단회 관측을 판단한다. 넓은 보존 oracle도 예상 lock을 구분하고 비교 전 map을 durable하게 남기도록 보완해야 한다. 새로운 제품 바이트를 만들면 이번 live를 그 바이트의 근거로 재사용하지 않는다.

## Final Review And Bounded Closeout

Claude Opus 5.5, session d1a3e056-bfce-49fa-a89f-02197efa84bc, 81.860초. 마지막 정적 리뷰 2/2회, 입력 drift 없음·정상 종료. packet SHA-256 4755f17f8ba84fb6ecf93117a03d646643e637592a523df74c51cd055dbd5e39. 결과는 조건부 수용이며 제품 runtime 확인은 미완료다.

Driver 처분:
- 보고 범위 보완 accept. App Server는 실제 시작했지만 turn은 시작하지 않았다. initialize 1회는 예약 근거이며 응답 성공을 뜻하지 않는다. 효과 none은 문서 쓰기 효과, closed는 관측한 프로세스 트리의 종료다. detached daemon 부재나 프로젝트 밖 파일 보존은 주장하지 않는다. diagnostic phase=worker는 고정된 분류값이며 worker 실행 증거가 아니다.
- 원인 후보 축소 accept. terminal row의 protocol_refused, schema REASONS, Host.fail/state.need, preflight를 추가로 읽기 대조했다. RPC-refused와 runtime-diagnostic-refusal은 REASONS에 없고 preflight는 예외를 삼키지 않는다. 따라서 정적 경로 대조상 stderr 거부가 유력하다. stderr 내용·근본 원인·무해성은 미확정이며 네트워크/인증/제품 결함/CLI 비호환 중 어느 것으로도 판정하지 않는다.
- 보존 oracle 보완 accept, 범위 내 task-local 수정. before map을 spawn 전에 exclusive create·fsync하고 started 기록에 hash를 연결하도록 후속용 runner를 보정했다. path별 type/mode/size/file hash/symlink target을 기록하고 exact root output, 해당 grant capsule과 빈 0600 lock만 구분한다. added/removed/changed를 별도 기록한다. 정상 lock·허용 출력 두 사례와 추가 파일·mode 변경·하위 Document.md 변경·다른 capsule·잘못된 lock mode·참조 삭제·symlink 변경의 7개 거부 사례를 오프라인으로 확인해 9/9 통과했다. 원래 실패 runner/result를 보존했고 수정 runner로 live를 반복하지 않았다. 마지막 보정 코드 자체의 추가 독립 리뷰는 하지 않았다.
- 진단 source/phase/code 보강은 별도 후속 계획으로 유지한다. 원문·발췌·원문 hash를 남기지 않고 허용된 코드만 보존하며 기존 stderr 즉시 거부·권한/핀 의미를 유지해야 한다. 이 변경은 이번에 구현하지 않았다.

공식 실행 소비는 1/2세션, turn 예약 1회·실제 전송 0회, 4.587초다. 취소 사례는 미사용이지만 선행 실패 때문에 자동으로 시작하지 않는다. Claude 2/2회, 합계 130.782초다. 기존 실패·소비량과 모든 제한은 그대로 유지한다. 마지막 경과시간은 private 원장에 기록한다.

Adopter impact: installation state unverified. 실제 적용을 권고할 근거가 아직 없으며 현재 runtime 확인을 완료한 뒤 정확한 대상·후보로 별도 판단한다. 제품 코드·CLI/helper 핀·정책·기존 수락 Work는 변경하지 않았다. Windows 착수·실제 설치·adopter 적용·커밋·Git 게시·공개는 계속 보류한다.

다음 판단은 새 실행을 바로 반복하는 것이 아니라, 이번 실패 경로에 한정한 원문 없는 진단 보강과 오프라인 확인 범위를 정하는 것이다. 새 제품 바이트의 지원·실행 성공은 기존 실패 관측으로 대신할 수 없다.

~~~~markdown
## 판정: 조건부 수용
중단과 `cause_confirmed=false`는 타당합니다. 다만 보고 문구를 보정해야 하며, 원인을 "구분 불가"로 끝내면 안 됩니다. 제공된 코드상 stderr 경로가 유력합니다. 다음 설명은 제공된 코드만 대조한 결과이며, `preflight`, `schema.REASONS`, `state.need`, `public_status`는 확인하지 못했습니다.

### 1. Bounded result 보고
결과 필드는 수용하되, 다음 문구는 보정이 필요합니다.
- **`revoked-before-launch`:** turn 시작 전 철회라는 뜻입니다. App Server 프로세스 미기동이나 무실행으로 쓰면 안 됩니다.
- **`initialize_reserved=1`:** 예약 기록일 뿐, 전송·응답 여부를 증명하지 않습니다.
- **`effect=none`:** 문서 write effect 범위로 한정합니다. 비출력 파일 전체 보존의 근거가 아닙니다.
- **`closed`:** 관측된 프로세스 트리의 종료만 뜻합니다. 보이지 않는 detached daemon의 부재는 증명하지 않습니다.
- **diagnostic `phase=worker`:** adapter에 하드코딩된 값이므로 worker 관련 증거가 아닙니다.
- **예산:** `live_sessions_started=1`, `live_turns_reserved=1`, 실제 turn 0으로 구분해 적습니다.
- **판정 문구:** "제품 runtime 확인 미완료"입니다. 제품 결함, 인증 문제, CLI 비호환 중 어느 것으로도 판정하지 않습니다.
- **보존 oracle:** 현재 단서는 정확합니다. 추가로 이 oracle은 파일 내용 hash만 비교하며, root 밖 파일의 불변도 입증하지 않습니다.

### 2. 원인 미확정과 중단
**중단은 타당합니다.** 재시도하면 원인 정보 없이 남은 live 예산만 소모하고, cancel 시나리오의 선행 조건도 실패했습니다.

**필수 보정:** 원인 후보를 다음처럼 좁혀 기록합니다.
- `diagnostic_bytes=101`은 stderr, RPC error, runtime diagnostic 중 한 이벤트를 가리킵니다. 세 경로 모두 기록 직후 예외로 중단되므로, `preflight`가 예외를 삼키지 않는다면 단일 이벤트입니다.
- `Host.fail()`은 `reason_code(error)`의 기본값 `internal_error`로 `stop_reason`을 덮어씁니다.
- 따라서 `RuntimeError`나 JSON 오류는 terminal 값이 `internal_error`가 됩니다. `RPC-refused`와 `runtime-diagnostic-refusal`도 `REASONS`에 없다면 마찬가지입니다.
- terminal `stop_reason`이 정확히 `protocol_refused`이면, diagnostic이 있는 경로 중 남는 것은 `err()`뿐입니다.

보존된 journal의 terminal row와 `REASONS`를 읽어 `protocol_refused`가 terminal 값이고 두 토큰이 `REASONS`에 없음을 확인하면, **"stderr 경로 유력, 내용과 원인은 미확정"**으로 적습니다. 값이 `revoked` row에서 온 것이면 이 추론은 성립하지 않으며, 그때는 세 후보를 유지합니다. stderr가 맞더라도 내용이 무해하다는 뜻은 아니며, stderr 허용 여부는 별도 정책 결정입니다.

### 3. 다음 최소 보정안
방향은 수용합니다. 제품 바이트와 핀이 바뀌므로 새 승인과 baseline이 필요하며, 이 리뷰는 실행이나 정책 변경을 승인하지 않습니다.

**진단**
- **source:** `stderr`, `rpc_error`, `runtime_notification`, `stdout_parse`, `runtime_exit`, `send_failed`, `other`
- **phase:** `initialize`, `initialized`, `config_read`, `account_read`, `model_list`, `thread_start`, `turn_start`, `turn_interrupt`, `stream`, `close`
- **code:** RPC 표준 정수 코드 allowlist만 보존하고 나머지는 `other`로 둡니다. notification은 method allowlist 값만 보존합니다. stderr는 `unclassified`와 byte 수만 남깁니다.
- **금지:** 원문, 발췌, 원문 hash, 임의 method명, 예외 문자열은 보존하지 않습니다. 저엔트로피 원문의 hash는 대조로 복원될 수 있습니다.
- **첫 실패 보존:** 첫 실패를 1회만 기록하고, terminal `stop_reason`과 `revoked` reason을 함께 보고합니다. 기존 reason 매핑과 stderr 즉시 거부 동작은 바꾸지 않습니다.

**Oracle**
- **기록 시점:** before map을 Popen 전에 exclusive create로 저장하고 fsync합니다. 그 hash를 started 기록에 넣으며, 실패하면 시작하지 않습니다.
- **항목:** 경로별 type, mode, size, 정규 파일 hash, symlink target을 기록합니다. mtime과 ctime은 비교하지 않습니다.
- **예외:** 정확히 다음만 허용합니다.
  - root의 `Document.md`
  - 해당 grant의 capsule
  - 해당 grant의 lock(빈 정규 파일, `0600`)
  - 그 생성으로 바뀌는 부모 디렉터리 metadata
- **현재 코드 수정:** 임의 깊이의 `Document.md`를 제외하는 이름 기준 필터와 모든 `.hrn/executions/`를 제외하는 필터를 없앱니다.
- **결과:** added, removed, changed를 분리해 저장합니다. 범위 밖 metadata는 계속 보존 주장에서 제외합니다.

**재실행 전 조건**
- 가짜 runtime으로 각 source 경로를 재현하고, sentinel 원문이 journal, status, stdout, result에 남지 않음을 확인합니다. 모델 호출은 0회여야 합니다.
- oracle은 lock만 생긴 경우 통과하고, 추가 파일이나 mode 변경은 실패해야 합니다.

~~~~

## 초기화 진단 후보 — 오프라인 경계와 다음 판단

공식 실행 1회에서 어느 경로가 거부됐는지 식별하기 위한 변경안을 전용 증거 공간에만 보존했다. 제품 작업 트리와 기존 배포본은 그대로다. 후보는 초기화 RPC가 실패하여 실행 결과를 반환할 때만 고정된 출처·단계·허용 코드와 필요한 바이트 수를 덧붙인다. 실행 기록 형식이나 과거 status는 변경하지 않는다. stderr 즉시 거부, 기존 예외, 권한, CLI/helper 핀, 승인 의미를 유지한다.

- 네트워크 차단 상태의 파이프 비교: 원본과 후보를 같은 입력 11개에 대조했다. 성공/거부 결과, 예외와 기존 진단·예약 호출이 같았다. 초기화 실패만 구분했고, 미등록 RPC 코드와 boolean은 정해진 기타 값으로 축약했다. 실패를 거듭 기록해도 최초 진단을 유지했다. 파이프 비교는 Host 전체, 설치본 또는 실제 서비스 검증이 아니다.
- 전체 Host를 거치는 별도 합성 검사: 첫 사례가 초기화에 도달하기 전 끝났다. 문서 쓰기 효과는 없었고 프로세스 관측 값은 not_requested였다. 첫 실패에서 중단해 1건 실패, 나머지 9건 미실행이다. 시작한 런타임의 종료 확인, 전체 결과/캡슐 원문 미노출 또는 공식 실행 성공으로 세지 않는다.
- 원인 분리: 같은 격리 프로파일에서 런타임을 시작하지 않고 Host 자신의 프로세스 시작 시각을 읽는 선행 조건만 확인했다. 이 지점에서 PermissionError를 관측하고 중단했다. 첫 합성 실패의 원래 예외는 보존되지 않아 둘이 동일 예외였다고 단정하지 않는다. 앞선 공식 실행에서 관측한 초기화 거부와도 별개다.
- 중단 조건: 이후 재시도·권한 변경 없이 보존했다. 제품 적용·새 배포본·Claude·추가 공식 실행은 없다. 직전 공식 1/2세션, 실제 모델 턴 0회, 4.587초와 Claude 2/2회, 130.782초를 이월한다. 이번 관측을 정상/취소 성공으로 대체하지 않는다.
- 다음 순서: 같은 네트워크 차단과 기존 권한으로 프로세스 식별을 관측한 격리 경로의 선행 근거를 먼저 찾는다. 해당 경로를 고정할 수 있을 때만 전체 합성 검사에 실패 단계·허용 사유를 assertion 전에 보존하고 집중 검증한다. 통과 시 후보 패치·보존 판정·관측 범위를 독립 리뷰한 뒤 새 후보와 새 정상용 grant에 한해 단회 재관측한다. 남은 1세션을 사용하면 취소는 계속 미검증이다. 적합한 환경이 없거나 권한/통신/종료 불명 실패가 생기면 중단한다.

## 공식 정상 시나리오 단회 재관측

Owner가 재개와 필요한 추가 리뷰·세션을 허용했다. 오프라인 합성 환경에는 고정된 프로세스 관찰 명령 한 곳에만 이전에 검증된 예외를 적용했다. 같은 호출에서 로컬 TCP 연결 거절과 Host 자신의 PID·시작 시각 조회 성공을 확인했다. 제품의 실행 정책은 기존과 같다.

- 기존 실패에서 멈춘 Host 전체 합성 검사 10건이 모두 통과했다. 원본과 후보를 대조한 이전 파이프 11건은 재사용했다. 실제 공식 재관측에는 기존 배포본의 어댑터 한 파일만 변경한 전용 후보를 사용했다. 제품 작업 트리에는 패치를 적용하지 않았다.
- 첫 추가 리뷰에 따라 보존 판정기를 수정했다. root 및 상위 디렉터리의 링크, 기존 실행 기록·lock, 유효하지 않은 capsule 유형을 거부한다. 문서 변경 허용에는 적용 효과 확인이 필요하다. 시작 전 전체 비교표를 별도 경로에 배타적으로 보존하고, 종료 후 해시와 내용을 다시 대조한다. 이전 9건과 추가 7건, 총 16건을 수정 코드로 확인했다.
- stderr 동시 수신에 대한 지적은 실제 함수 뒷부분에서 비어 있지 않은 입력을 즉시 거부하는지 대조했다. 같은 읽기 주기의 정상 응답과 stderr, 초기화 성공, 취소를 원본·후보에 각각 적용한 3건이 통과했다. 어댑터 바이트는 그대로여서 이미 통과한 Host 10건과 파이프 11건을 재사용했다. 추가 리뷰는 모두 도구 없는 독립 정적 리뷰다.
- 재리뷰의 조건을 적용했다. 두 조회의 유효한 head 일치, 기대한 실제 문서 바이트, 0바이트 진단 여부, 종료, 효과 및 보존으로 판단한다. capsule 내부는 제품의 journal 판정으로, 외부 합성 트리는 별도 비교표로 확인했다. 새 grant와 실행 전 기록은 배타 생성한다.
- 공식 실행은 새 합성 Work와 새 grant로 정상 사례 1회를 관측했다. 초기화 RPC만 예약했고 stderr 첫 청크 101바이트를 확인했다. 기존 journal의 runtime 진단 바이트 수도 101이며 철회와 terminal 사유 모두 protocol_refused다. 모델/계정 확인과 모델 턴에 이르지 않았다. 효과 none, 문서 불변, 범위 밖 비교 통과, 입력 drift 없음, 관측된 프로세스 종료다.
- 이전 실패에서는 stderr가 유력하다는 정적 추론이었다. 이번 후보에서 직접 확인한 것은 stderr의 출처·단계·크기다. 원문은 수집하지 않았으며 출력의 내용·발생 이유와 두 실행의 바이트 동일성은 미확정이다. 통신 또는 인증 오류로 단정하지 않는다.
- 중단 조건에 따라 재시도와 취소 시나리오 없이 종료했다. 누적 공식 2세션, 실제 모델 턴 0회, 8.959초다. Claude 누적 4회, 325.270초다. 두 추가 리뷰의 실측은 124.868초와 69.620초다. 시간은 원래 4시간 창에 이월한다. 정상/취소 및 실제 적용 자격은 미검증으로 유지한다.
- 다음 판단은 고정 버전의 초기화 진입 코드와 실제 실행 인수·설정 계약을 오프라인으로 대조해 stderr를 낼 수 있는 경로를 좁히는 것이다. 정상 출력의 무해성, 허용 정책 변경 또는 실제 환경 지원은 별도 근거가 필요하다. Windows·실제 설치·adopter 적용·커밋·Git 게시·공개는 보류한다.

### review 독립 리뷰 원문

Claude Opus 5.5, session 0a12c638-251b-4d0f-b2ae-e1eba50f8c4b, 입력 digest 157f0985abb64e316ab63f993b96da1133e0d36f4e7b2a96f27ba86ba8ab5d3f.

~~~~markdown
# 독립 정적 리뷰 결과

**판정: 현재 후보로는 공식 재관측에 진입하면 안 됩니다.** 아래 보정 3건을 적용하고 전체 재검사를 통과한 뒤에 진입하십시오. 나머지 어댑터 변경(폐쇄 값 진단, 원 예외 재전파, 비초기화 경로 분리)에서는 차단 사항을 찾지 못했습니다.

## 차단 사항

1. **stderr 기록 후 초기화가 성공할 수 있음 (`err`, `request`)**
   - 보이는 `err()`는 한도 초과 때만 예외를 냅니다. diff에 없는 뒷부분이나 호출부가 즉시 거부하지 않으면, 같은 읽기 주기의 응답으로 initialize가 성공할 수 있습니다.
   - 이 경우 성공 결과에 `runtime_first_failure`가 붙어 stderr 즉시 거부와 성공 시 필드 없음 계약을 모두 어깁니다.
   - Host 10건의 목록에는 stderr와 정상 응답의 동시 도착, 초기화 성공 시 필드 부재가 없습니다.

2. **보존 판정이 검사 없이 통과할 수 있음 (`snapshot`, `compare`)**
   - root가 심볼릭 링크이면 한 행만 기록되어 트리를 순회하지 않고 통과합니다.
   - `.hrn` 계열 부모가 전후 동일한 심볼릭 링크여도, 외부 쓰기를 탐지하지 못한 채 통과합니다.

3. **grant 재사용과 실패 시 문서 변경을 거르지 못함 (`compare`)**
   - before에 capsule이나 lock이 이미 있어도 통과하므로 소비된 grant를 잡지 못합니다.
   - capsule 경로가 일반 파일이나 심볼릭 링크여도 통과합니다.
   - `Document.md`는 내용 변경을 무조건 허용하므로, effect none 실패에서 문서가 바뀌어도 통과합니다.

## 구체적 최소 보정

**어댑터 `request`:** 모순 상태를 성공으로 반환하지 않고 거부합니다.

```python
try:
    value = self._request(method, params, seconds)
    state.need(self.initialize_failure is None, 'initialize-diagnostic-conflict')
    return value
```

**`snapshot`:** 함수 시작 부분에 추가합니다.

```python
if not stat.S_ISDIR(Path(root).lstat().st_mode): raise ValueError('root-not-directory')
```

**`compare`:** 시그니처를 바꾸고, `capsule`·`lock`·`parents` 정의 직후에 검사를 넣습니다. `document_may_change`는 실행 결과의 effect가 none이면 `False`로 넘깁니다.

```python
def compare(before, after, grant, document_may_change=False):
    ...
    if lock in before or any(n == capsule or n.startswith(capsule + '/') for n in before):
        raise ValueError('grant-already-present')
    if any(p in m and m[p]['type'] != 'directory' for m in (before, after) for p in parents):
        raise ValueError('parent-not-directory')
    if capsule in after and after[capsule]['type'] != 'directory':
        raise ValueError('capsule-not-directory')
```

`Document.md` 분기 조건도 다음과 같이 바꿉니다.

```python
elif n == 'Document.md' and kind == 'changed' and document_may_change:
```

**재검사:** 두 파일의 해시가 바뀌므로 기존 통과 결과는 재사용할 수 없습니다. 파이프 11건, Host 10건, 비교 9건을 새 해시로 다시 실행하고 다음 사례를 추가합니다.
- stderr와 정상 응답의 동시 도착
- 초기화 성공 시 필드 부재
- 초기화 중 취소
- root·부모 심볼릭 링크
- 기존 grant·lock
- effect none에서 문서 변경

## 단회 공식 재관측 진입 판단

**진입 전 확인:** 아래 항목은 grant 소비 전에 정적으로 확인합니다. 하나라도 어긋나면 진입하지 않습니다.
- 격리 배포본의 실제 호출부가 결과의 추가 키를 거부하거나 저널·status에 복사하지 않는지 확인합니다.
- 초기화 실패가 `raise error`로 빠지지 않고 결과 반환까지 도달하는지 확인합니다. 예외로 나가면 이 패치의 진단은 사라집니다.
- 교체 후 어댑터 해시가 후보와 일치하고, 나머지 배포본과 CLI/helper가 고정값과 일치하는지 확인합니다.
- before map을 root 밖에 spawn 전에 저장하고, 비교 때 해시를 재검증하는지 확인합니다.

**실행 후 해석:**

| 관측 | 판정 |
|---|---|
| 초기화 실패, 진단이 기존 진단과 일치, 종료 확인, effect none, 보존 통과 | 관측된 최초 거부 출처만 기록하고 원인은 미확정 유지 |
| `runtime_exit` | 프로세스 종료를 먼저 관측했다는 뜻이며, 읽지 못한 출력이 없었다는 증거는 아님 |
| 초기화 실패인데 진단 없음, 진단 불일치, 종료 불명 | 보류 |
| 필드 없이 초기화 통과 후 기존 흐름의 정상 완료 | 이때만 공식 성공으로 인정 |
| 초기화 이후 실패 | 공식 성공이 아니며, 초기화 실패 출처로도 해석하지 않음 |

어느 결과든 재시도하지 않으며, 추가 관측에는 별도의 새 합성 작업과 승인이 필요합니다.

## 한계

- **미검증 범위:** 파일 접근과 실행 없이 제시된 diff와 helper만 읽었습니다. SHA-256은 재계산하지 않았고, 11/10/9건 결과는 제시된 보고로만 받아들였습니다. `err()` 뒷부분, `next()`의 읽기 순서, `send()`, 결과 조립부도 보지 못했습니다.
- **출처의 의미:** `source`는 어댑터가 처음 관측한 순서이지 인과 순서가 아닙니다. 한 청크의 메시지를 먼저 모두 파싱하므로, 앞선 RPC 오류보다 뒤의 잘못된 줄이 먼저 기록될 수 있습니다. 응답 전 stderr도 phase는 `initialize`로 찍힙니다.
- **코드 분류:** `other`는 예약·저널 실패와 타임아웃을 포함하므로 전송 여부를 말해 주지 않습니다. stderr의 `byte_count`는 첫 청크 길이라서 101과 달라도 총량과 곧바로 비교할 수 없으며, 이 경우 보류합니다.
- **최종 상태:** 이 필드는 terminal/revoked를 증명하지 않습니다. 최종 상태는 기존 status와 저널로만 판단합니다.
- **보존 범위:** root 내부의 유형, 권한, 크기, 해시만 봅니다. mtime, inode, 소유자, xattr/ACL과 root 밖 변경은 탐지하지 못합니다. capsule 내부는 검사에서 제외되고, 판정은 프로세스 종료 확인 후에만 유효합니다.
- **환경 차이:** 합성 Host와 파이프 검사는 공식 런타임의 동작이나 공식 성공을 증명하지 않습니다.
~~~~

### review-corrections 독립 리뷰 원문

Claude Opus 5.5, session b7ef1d01-096c-4e80-a090-8abd7b4ec4ed, 입력 digest eaff8f2cd8c2b5a057887db4ec24f2620d81ff5303a128815f45bfed3ba8271e.

~~~~markdown
## 판정: 실제 차단 사항 없음, 공식 단회 재관측 진행 가능
선행 게이트를 모두 통과한 경우에만 진행하며, 후보 hash는 변경하지 않습니다. 이 판단은 제공 코드의 정적 대조에 근거합니다. 테스트 결과는 보고 내용으로만 반영했고 직접 확인하지 않았습니다. 실제 CLI/helper/모델 동작은 아직 미관측입니다.

| 이전 우려 | 판정 | 근거 |
|---|---|---|
| **stderr 동시 응답** | 해소 | `err`는 비어 있지 않은 `raw`를 받으면 항상 `need`에서 예외를 내므로, 같은 호출 흐름에서 성공으로 이어지지 않습니다. 취소는 필드 기록 없이 다시 raise됩니다. |
| **root/부모 링크, 기존 grant/capsule** | 해소 | root는 canonical 경로와 디렉터리 여부를 검사합니다. `lstat` 기반이라 링크를 따라가지 않으며, 부모 링크와 기존 lock/capsule은 깨진 링크까지 fail-closed로 거부합니다. 실행 후 부모와 capsule의 유형도 재검사합니다. |
| **효과 none의 문서 변화** | 해소 | `applied`가 아니면 `document_may_change=False`이므로 `Document.md` 변화는 `unexpected`로 기록됩니다. |

## 코드 변경 없이 판정에 적용할 조건
- **문서 효과 불일치:** `compare`는 `applied`인데 문서가 그대로인 경우와, 양쪽 `head`가 모두 없는 경우(`None==None`)를 걸러내지 않습니다. 둘 다 `pass`가 나와도 미확정으로 처리해야 합니다.
- **빈 stderr 진단:** `host.diagnostic`은 `raw`가 비어 있어도 호출됩니다. EOF 등으로 `err(b'')`가 호출되면 성공 실행에도 `protocol_refused`, 0바이트 진단이 남을 수 있습니다. 이 경우 `runtime_first_failure`는 없으므로 stderr 수신 근거로 쓰지 말고, 예상과 다른 marker로 보아 미확정 처리합니다.
- **capsule 내부:** `compare`는 capsule 하위 항목을 검사하지 않습니다. 따라서 `pass`는 capsule 외부 보존만 뜻하며, 내부 정합성의 근거가 되지 않습니다.

## 제공 코드로 확인할 수 없는 부분
- **`_request`와 selector 순서:** 동시 응답 시 즉시 예외가 난다는 점은 보고된 테스트에만 근거합니다.
- **`host.fail`/`host.finish`와 호출부:** 초기화 예외를 삼키거나 재시도하지 않는다는 점, 반환 dict가 저장 상태와 별칭이 아니라는 점은 정적으로 확정할 수 없습니다. 보고된 Host 10건과 public status 결과가 이를 뒷받침합니다.
- **단회성 보장:** `save_before`는 `O_EXCL`을 쓰지만 `once` 구현은 제공되지 않았고, `live_sessions_started==1`의 의미도 발췌만으로는 알 수 없습니다. 재실행 차단은 `once`도 같은 배타 생성을 쓴다는 전제에 의존하므로, 선행 게이트에서 확인해야 합니다.
~~~~

## 읽기 후 외부 취소의 인과관계 — 격리 후보 단회 검증

이전 허용 후보의 공식 정상 작업은 읽기와 지정 구간 수정, 문서 검사 3건, 효과 적용 및 프로세스 종료까지 완료했다. 이 근거를 재사용했다. 같은 후보로 앞서 시도한 취소 사례에서는 읽기 worker 1회가 끝나자마자 한도 소진으로 중단이 예약됐고 외부 요청은 접수되지 않았다. 이번 과제는 외부 요청이 실제 중단을 일으켰는지를 확인하는 것이다.

- 범위와 한도. Owner가 60분 묶음, 합성 검사 통과 후 공식 최대 1세션·1턴·300초, 범위 내 보정 및 재시도 없는 중단을 승인했다. 60분은 중단 상한이다. 합성 실행 6건과 결과 점검을 한 번에 수행하고 기존 정상 사례와 원문 미보존 근거를 재사용했다.
- 보정 범위. 부모 후보 26b116cd735f3a3a193faf999d9598e7aaf52d96d41a0d3fdcff57224bd81e39에서 Host와 stdio 어댑터만 변경하여 격리 후보 6191e0d6f3f5fd22ed819c2054e6ff9734997a06ba3b781c91433729d1d71236를 생성했다. 읽기 worker 한도는 1회다. 성공한 읽기의 종료와 완료 기록 후 최대 5초 동안 다음 worker를 시작하지 않고 같은 grant의 취소 표식을 확인한다. 기존 실행 마감·grant 만료와 stderr 거부도 적용한다. 기한 내 유효한 표식을 보면 cancelled, 없으면 worker_budget_consumed로 철회한다. 같은 턴의 interrupted 응답을 검증한 뒤 실행 결과에 확인 여부만 표시한다.
- 판정. 읽기 성공 후 공개 취소 요청이 1회 접수되고, 그 grant의 표식을 Host가 접수 구간 안에서 확인해야 한다. 철회 사유 cancelled, interrupt 예약 1회, 같은 턴의 실제 interrupted 응답, 문서 불변과 프로세스 종료를 모두 요구한다. 취소 요청의 응답과 런타임의 중단 응답은 별개다.
- 합성 결과. 기존 네트워크 차단 프로파일에서 스크립트형 런타임과 실제 Host·읽기 worker를 사용했다. 별도 합성 프로세스는 제품의 취소 함수를 호출했다. 요청 없음은 worker_budget_consumed로, 기한 내 올바른 요청은 cancelled로 종료됐고 두 경우 모두 동일 턴 중단 응답을 확인했다. 종료 후 요청과 다른 grant 요청은 접수되지 않았다. 응답 누락과 다른 턴 응답은 요청이 접수돼도 중단 확인값을 얻지 못했다. 6건 모두 기대한 결과였으며 문서 보존과 관측 프로세스 종료를 확인했다.
- 공식 결과. 새 grant에서 4.197초 동안 1회 관측했다. initialize 예약 후 런타임 stderr 첫 읽기 101바이트가 알려진 경고의 접두부와 일치했다. 완전 일치 예외를 사용하지 않고 protocol_refused로 즉시 종료했다. 모델 턴·읽기 worker·취소 명령은 각각 0회다. 공식 접수 구간 및 실제 외부 취소의 인과관계는 미검증이다. 쓰기 효과 none, 지정 문서와 보호 파일 보존, 관측 프로세스 종료, 입력 불변을 확인했다.
- 증거 구분. 이전 101바이트는 기존 unclassified 기록으로 보존했다. 이번 101바이트의 접두부 판정은 이번 후보와 실행에만 적용한다. 실행 원문 대신 고정 분류·길이·결과만 기록했다. 누적 공식 실행 6세션, 실제 모델 턴 2회, 누적 실측 64.119초다. 추가 모델 리뷰와 공식 재시도는 0회다.
- 현재 판단. 합성 환경에서의 인과관계와 공식 초기화 거부를 각각 관측 범위로 유지한다. 공식 외부 취소 항목은 열어 둔다. 공식 적용·설치 또는 결과 수락은 별도 판단이다.

## 분할 경고 수신과 읽기 후 외부 취소 — 공식 관측 결과

45분 묶음에서 격리 후보의 stdio 어댑터 한 파일을 보강했다. 정상 작업은 앞서 공식 관측한 결과를 재사용했다. 이번 후보의 공식 관측 대상은 읽기 후 취소다. 후보 식별값은 f2af29e7daba2317f7e4503c80aaf1ff990f1dcd17a66eeac9417bb77d9e52d5이며 부모 후보는 6191e0d6f3f5fd22ed819c2054e6ff9734997a06ba3b781c91433729d1d71236다.

- 경고 판정. 고정 CLI와 helper의 초기화에서 첫 stderr가 알려진 경고의 앞 101바이트와 정확히 같을 때만, 나머지 3바이트를 최장 50ms 기다린다. 단조 시계의 기한은 첫 읽기에서 한 번 정한다. 대기 중에는 초기화 응답·콜백을 보류하고 실행 마감과 취소를 확인한다. 기한 경계·초과, EOF, 불일치, 여분 또는 반복 출력은 거부한다. 전체 104바이트가 한 번에 도착한 경우와 분할 수신으로 완성한 경우를 고정값으로 구분한다.
- 합성 검증. 바이트 판정 213건, 제어 시계 17건, 파이프 4건, Host 2건을 통과했다. 기한 직전·정각·직후와 여러 조각을 확인했고, stdout 응답이 이미 대기해도 불완전한 경고로 진행하지 않았다. 조기 EOF는 worker 실행 전에 종료됐다. 분할 수신이 완성된 합성 사례에서는 외부 요청 접수부터 같은 턴 중단까지 확인했다. 읽기 후 접수 구간과 취소 실패 대조군은 앞선 6건의 근거를 재사용했다.
- 공식 수신. 1세션·1턴에서 첫 101바이트에 이어 나머지 3바이트까지 기한 안에 일치해 경고를 한 번 허용했다. 수신 방식은 joined_101이다. 조각 원문·해시와 개별 도착 간격은 보관하지 않았다. 이전 실행의 미분류 101바이트와 접두부 일치 101바이트는 각각 기존 판정대로 보존했다.
- 접수와 중단. 저널 17번에서 읽기 성공을 확인한 시점에는 권한 철회·interrupt 예약·쓰기 예약이 없었다. 공개 취소 명령 1회가 코드 0으로 같은 grant의 요청을 접수했고, 접수 응답은 cancel_requested=true, effects_stopped=false였다. Host가 5초 접수 구간 안에서 그 표식을 확인한 뒤 18번에서 cancelled로 철회하고 19번에서 interrupt를 예약했다. 런타임의 같은 턴 interrupted 응답을 대조한 뒤 22번에서 최종 상태 interrupted와 사유 cancelled를 기록했다. 외부 취소에 의한 중단을 확인했다.
- 효과와 종료. 읽기 worker 1회, 쓰기·검증 worker 0회였다. 문서 효과 none, 대상·참조·보호 파일 바이트 일치와 합성 프로젝트 내부에서 허용된 실행 기록·lock 이외의 예상 밖 변경이 없음을 확인했다. 실행 부모 그룹, 관측한 프로세스 식별자 3개, 취소 명령 그룹의 종료를 확인했다.
- 한도와 처분. 공식 관측은 14.762초에 종료됐다. 추가 리뷰와 공식 재시도는 0회다. 누적 공식 7세션·실제 모델 턴 3회, 실측 78.881초다. 결과 수락은 Owner 판단으로 남긴다. 실제 설치·adopter 적용·Windows 자격·Git 게시·공개는 별도 범위다.

## Owner Acceptance and Work Completion

2026-11-02 Owner가 다음 두 관측을 각 후보와 시나리오의 범위로 수락했다. 완료 기준 1–3에 대한 진입 조건, 문서 효과, 종료, 검증·리뷰 처분 및 실패 기록은 앞 절들에 보존한다. 공식 실행기 조합 확인 Work를 Done으로 닫는다.

| 수락 대상 | 공식 관측 및 수락 범위 |
|---|---|
| 선행 정상 작업 후보 `26b116cd735f3a3a193faf999d9598e7aaf52d96d41a0d3fdcff57224bd81e39` | 초기화 중 알려진 경고 한 줄을 한 번 허용했다. 읽기 → 지정 구간 쓰기 → DOC-LINKS·DOC-GFM·DOC-CLAIMS 통과 → 완료를 확인했다. 문서 효과는 applied였고, 범위 밖 파일 보존과 관측 프로세스 종료를 확인했다. |
| 최종 격리 취소 후보 `f2af29e7daba2317f7e4503c80aaf1ff990f1dcd17a66eeac9417bb77d9e52d5` | 첫 101바이트와 50ms 안에 수신한 나머지 3바이트가 일치해 경고 한 줄을 한 번 허용했다. 읽기 후 5초 접수 구간에서 같은 grant의 외부 요청을 확인했고, 권한 철회 사유 cancelled와 동일 턴의 interrupted 응답을 대조했다. 문서 효과는 none이었고 대상·참조·보호 파일의 바이트 및 관측 프로세스 종료를 확인했다. |

두 행은 서로 다른 배포 바이트에서 얻은 합성 문서 공식 관측이다. 최종 후보에서 정상 작업을 별도로 공식 재검증한 근거는 없다. 과거 101바이트 중 미분류와 접두부 일치로 남긴 기록 및 실패·소비량을 그대로 보존한다. 제품 소스 반영과 플랫폼 자격은 별도 판단이다. Adopter impact: installation state unverified.

기존 비공개 증거 경로의 기준 후보, 단회 입력·결과, 수정 전후 보존 근거는 후속 제품 소스 대조에서 사용한다. 후속 처분 시 보존 필요성을 재평가한다.

## Product Source Follow-up Proposal

다음은 실행 승인을 받기 전의 단일 후속 묶음이다. 기준 소스는 HEAD `c1270391a0e9f262a4e05fc925c6424619171cb6`와 선행 수락 후 진행 중인 작업 트리 변경이다. 최종 격리 후보의 관리 파일 48개를 이 소스와 읽기 전용으로 대조했다. 제품 모듈 차이는 `src/hv2ref/official_adapter.py`와 `src/hv2ref/official_host.py`에 있다. 세 번째 차이인 `colvia`는 격리 배포용 생성 진입 파일이며 테스트 저장소 위치와 관리 런타임 설정을 포함한다.

1. 반영 기준 고정 및 계획 리뷰. 두 모듈의 누적 차이를 검토하고 이번에 제품 계약으로 채택할 동작을 명시한다. 특히 worker_limit=1인 읽기 완료 후 최대 5초 대기는 제품에서 관측 가능한 시간 변경이다. 경고 허용은 지정 CLI/helper와 초기화 1회에 한정하고, 분할 수신의 50ms 기한·추가 stderr 거부·실제 턴 중단 확인·기존 실행 결과 호환성을 리뷰한다. 이전에 수락한 미커밋 변경은 별도 기준으로 보존한다.
2. 범위 내 반영. 두 모듈의 필요한 변경과 해당 제품 테스트·공식 실행 문서를 함께 반영한다. 생성 진입 파일, 개인 경로, 실행 원장, 단회 관찰 스크립트는 제품 파일에 복사하지 않는다. 재사용할 합성 검사는 저장소의 fixture에 맞춘다.
3. 집중 검증 및 패키지 대조. 소스에서 정상 흐름과 읽기 후 취소를 합성으로 연결한다. 완전 일치/101+3/기한·EOF·여분·추가 stderr, 기존 기록 판독, 외부 취소의 접수/동일 턴 응답/문서·프로세스 보존을 확인한다. 새 격리 배포본을 생성해 두 모듈과 나머지 관리 파일의 동일성, 생성 진입 파일의 기대 차이를 대조한다. 새 바이트와 달라진 경로에는 기존 공식 관측을 소급하지 않는다.
4. 결과 리뷰와 처분. 범위 내 보정 및 영향받은 검사까지 같은 묶음에서 처리한 뒤 제품 소스 결과를 별도로 수락 요청한다. 권한·핀·시간 계약 확대, 예상 밖 배포 차이 또는 공식 확인이 꼭 필요한 차이가 발견되면 근거를 보존하고 그 지점에서 판단을 요청한다.

예상 60–90분, 중단 상한 120분을 제안한다. 소스 이식과 테스트 정리, 합성·패키지 대조, 리뷰 대기를 포함한 판단 추정이다. 최신 분할·취소 합성 검사의 짧은 실행 시간은 재사용할 수 있으나 저장소 fixture 적응과 리뷰 소요는 아직 실측하지 않았다. Claude 계획·결과 리뷰 최대 2회, 각 240초를 총 시간에 포함하고 공식 모델 실행은 0회로 계획한다. Windows 착수, 실제 설치·adopter 적용, 커밋·Git 게시·공개는 별도 승인 범위다.
