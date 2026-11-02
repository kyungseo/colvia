# 공식 문서 실행

이 진입점은 명시적으로 준비하고 설치한 macOS `official-execution-2` 후보에서만 사용할 수 있다. 기본 `continuation-1` 설치나 Windows 설치에는 실행 기능을 추가하지 않는다. 설치된 payload의 검증과 실행 결과 수락은 별도다. 이 후보의 검증 범위와 남은 한계는 소스 개발 기록에 따른다.

## 실행과 수락의 구분

```text
수락된 intent + 현재 active Work + 현재 문서
                    ↓
             run prepare (읽기 전용)
                    ↓ exact digest와 실행 승인
             run execute (문서 효과)
                    ↓
           실행 기록과 검증 결과 보존
                    ↓ 별도 Owner 판단
            기존 Work의 결과 수락 절차
```

`run execute`는 지정 문서의 한 구간을 즉시 변경할 수 있다. Core의 accept/apply를 호출하지 않으며, 실행 완료가 Work 완료나 Owner 수락을 뜻하지 않는다. 호출자는 한 로컬 OS 계정 안에서 협력하는 trusted operator다. `owner_statement`와 확인 digest는 승인 선언을 기록하지만 인간 신원을 인증하지 않는다.

## 실행 도구 구성 확인

에이전트에게 “실행 도구 구성을 확인해줘”라고 요청할 수 있다. 에이전트가 기존 실행 입력을 갖고 있다면 `./colvia doctor --runtime-input FILE`로 파일과 설정을 읽기 전용으로 확인한다. 프로젝트에 검증된 `official-execution-2`가 연결되어 있을 때 제공하며, 기본 `doctor`는 기존 프로젝트 상태 조회를 유지한다.

화면은 프로젝트 상태와 실행 입력 상태를 따로 설명한다. 예를 들어 입력이 달라졌다면 “현재 파일과 보존된 실행 입력이 다릅니다. 입력의 원래 출처와 파일 변경 내용을 함께 확인하세요.”라고 안내한다. 검사는 이번 명령의 프로세스 환경을 기준으로 하며, 계정·모델 연결은 실제 실행 준비 단계에서 확인한다.

새 CLI 버전이나 다른 헬퍼는 별도의 자격 확인이 필요하다. 기존 입력의 해시를 바꾸는 것으로 검증 조합이 늘어나지 않는다. 사용자에게 JSON 작성을 요구하는 기본 사용 흐름은 추가하지 않는다. 입력 크기·응답 필드·종료코드의 의미는 [선택형 로컬 진단](REFERENCE.md#optional-local-execution-input-check)에 있다.

## 준비와 실행

설치된 프로젝트에서 `./colvia run --input request.json` 또는 `./colvia run prepare --input request.json`으로 preview를 만든다. 입력은 canonical JSON이며 외부 전용 `host_control_root`, 실제 Work ID, worker root, 읽을 문서 ID 순서, 단일 출력 문서와 UTF-8 byte 편집구간, 근거 문구, 요청 prompt, Owner 승인 문구, 실행시간과 만료, 고정 runtime 입력을 포함한다.

Agent가 입력을 준비하더라도 trusted operator가 전송할 문서·구간·prompt와 실행범위를 확인해야 한다. 모델이 경로·실행파일·정책·argv를 선택하지 않는다. 읽기는 승인된 문서 view만 전달하며 출력은 한 번의 구간 교체만 허용한다. `DOC-LINKS`, `DOC-GFM`, `DOC-CLAIMS`를 순서대로 실행한다. 문서 최대 크기는 파일당 128 KiB이며 실제 전송 view 전체가 단일 64,000-byte 도구 응답에 들어가야 한다. 문서 ID는 ASCII 영숫자이고 정렬된 순서로 지정한다.

preview의 `spec`에는 prompt·근거 문구 등 승인 원문이 있으므로 Git 밖의 승인된 private 저장소에서 취급한다. `spec`만 별도 canonical JSON 파일에 저장한 뒤 `./colvia run execute --input spec.json --confirm DIGEST`로 실행한다. 승인과 실행 사이에 문서, Work 선택, intent, 설치 release, runtime 입력이 달라지면 거절한다. 같은 grant는 한 번만 소비한다. 실행 후에는 기존 grant를 재사용하지 않고 현재 문서에 결속한 새 preview와 승인이 필요하다.

실행 spec은 1 MiB, claim 문구와 evidence의 각 quote는 4,096 UTF-8 byte 이내다.

전체 기록은 256 capsule·4,096파일·128 MiB 이내이며 새 실행은 최대 한 회분의 공간이 남아 있을 때만 준비할 수 있다. 여유가 부족해도 기존 결과의 판독과 lifecycle은 유지한다.

각 실행의 상한은 30–600초, App Server·계정 조회·모델 목록·thread·turn 각각 1회다. worker 상한은 5회 또는 읽기 후 중단을 위한 1회다. 자동 재시도·자동 수정·추가 모델 turn은 없다. 고정 모델과 low effort의 목록 확인은 실제 사용 권한이나 성공을 보장하지 않는다.

## 요청 필드

Agent는 다음 필드만 포함한 JSON을 준비한다. 누락·추가 필드는 거절한다. 경로는 존재하는 절대 실제 경로이며 symlink나 경로 별칭을 허용하지 않는다. 파일별 내용과 digest는 실행 직전 다시 확인한다.

| 필드 | 입력과 제한 |
| --- | --- |
| `work_id`, `worker_root` | 현재 active Work와 그 local 프로젝트 또는 등록된 isolated worktree. 출력은 Work scope 안에 있어야 한다. |
| `documents.files` | ID별 `{path, view}`. 참조는 `{kind: "full"}`, 출력은 `{kind: "replace-range", ranges: [[시작 byte, 끝 byte]]}`. 끝 위치는 포함하지 않는다. |
| `documents.output` | 파일 ID 하나. 서로 다른 ID가 같은 파일을 가리킬 수 없다. |
| `documents.claims` | 출력 ID 아래 `required`, `forbidden`, `evidence`. evidence 각 항목은 참조 문서의 `file_id`와 실제 존재하는 `quote`다. |
| `documents.approved_external_links` | 링크 verifier가 허용할 HTTPS 또는 mailto 링크 목록. 내용 검사 예외는 아니므로, mailto 주소는 목록에 넣어도 이메일 식별자 검사에서 거부된다. |
| `documents.link_targets` | 선택 필드. 초기 출력 전체에서 참조하지만 files에 없는 로컬 대상의 `{path, anchors}` 목록. 최대64개이며 빈 목록은 생략한다. anchor가 있는 대상은 최대8개, 대상별 anchor는 최대32개·각512 UTF-8 byte다. |
| `read_ids` | files의 모든 ID를 정렬한 목록. 문서는 1–8개이며 근거를 위한 참조 문서가 필요하다. |
| `prompt`, `owner_statement` | 수행 지시와 로컬 운영자의 승인 선언. 각각 최대 32 KiB와 4,096자. |
| `runtime` | 아래 고정 `paths`, `sha256` 집합. 임의 인자는 받지 않는다. |
| `runtime_root` | 프로젝트 및 host control root와 겹치지 않는 기존 전용 폴더. 소유자 외 권한이 없어야 한다. grant별 runtime 자료가 남는다. |
| `host_control_root` | 운영자가 미리 준비한 Git 밖의 `0700` 폴더. target·worker root·runtime root·App Server 읽기 범위와 겹치지 않고 출력 문서와 같은 device에 있어야 한다. 아래 marker가 필요하며 자동 생성·대체 경로를 제공하지 않는다. |
| `expires_wall_ns` | 현재 이후 24시간 이내의 Unix nanosecond 시각. |
| `seconds`, `worker_limit` | 30–600초와 worker 1회 또는 5회. 1회는 읽기 후 취소 검증용이다. |

host control root의 `store.json`은 소유자만 읽고 쓸 수 있는 `0600` 일반 파일이며 canonical JSON이어야 한다. 필드는 `schema_version: 1`, `store_id: "<32자리 소문자 hexadecimal 식별자>"` 두 개다. 기존 저장소 식별자를 임의로 교체하지 않는다. 저장소 경로와 identity는 full live spec의 승인 digest에 결속되며 capsule에는 경로 대신 `store_id`·grant·ordinal로 된 locator만 남는다. status는 locator만으로 외부 저장소를 탐색하지 않는다.

`runtime.paths`에는 `BIN`, `CODE_MODE_HOST`, `CODEX_CONFIG`, `CODEX_AUTH`, `INSTALLATION_ID`, `CODEX_RULES_DIR`, `CODEX_RULES_FILE`, `GLOBAL_INSTRUCTIONS`를 모두 지정한다. 설정·인증·installation ID는 기본 사용자 `.codex` 파일이어야 하며, rules 파일은 기본 rules 폴더의 직접 자식이어야 한다. 전역 지침의 논리 경로가 symlink이면 지정하는 값은 실제 대상 파일이다. `runtime.sha256`에는 이 중 `CODEX_AUTH`, `INSTALLATION_ID`, `CODEX_RULES_DIR`를 제외한 다섯 파일의 SHA-256을 지정한다. 인증 파일의 내용은 요청에 복사하지 않는다.

예를 들어 `Editable`의 byte `[9, 17)`만 바꾸고 `Reference`를 근거로 사용하면 `read_ids`는 `["Editable", "Reference"]`, output은 `"Editable"`이다. preview에서 결속된 실제 경로·구간·근거와 digest를 확인한 뒤 spec을 승인한다. `--grant`는 status/cancel/resolve, `--confirm`은 execute 또는 resolve에만 사용한다.

### 초기화 중 경고 처리

고정된 macOS CLI 0.165.0과 대응 helper 조합에서는 초기화 응답 대기 중 알려진 PATH 보조 명령 생성 경고를 한 번 허용한다. 첫 stderr 읽기가 줄바꿈까지 104바이트 전부와 일치하거나, 정확한 앞 101바이트에 이어 남은 3바이트가 첫 읽기부터 50ms 안에 완성돼야 한다. 분할 대기 중에는 stderr만 읽는다. 취소, 기존 실행 마감, grant 만료가 먼저 오면 대기를 끝낸다. 첫 읽기가 101바이트보다 짧거나 초기화 응답을 처리한 뒤 경고가 도착하면 거부한다. 그 밖의 내용, 불완전한 줄, 여분 또는 두 번째 stderr도 거부한다. 이 처리는 파일·네트워크 권한을 추가하지 않는다.

허용을 사용한 `run execute` 결과에는 `initialize_path_warning_allowed=true`와 수신 방식 `initialize_path_warning_mode`가 표시된다. 값은 한 번에 읽은 `single_read` 또는 101바이트 뒤 완성한 `joined_101`이다. 초기화 실패에서 실행 결과를 반환할 수 있으면 `runtime_first_failure`에 첫 관측의 단계·출처·고정 코드와 해당되는 바이트 수만 표시한다. stderr 진단의 바이트 수는 첫 읽기의 크기이며 journal의 거부 바이트 합계와 다를 수 있다. 원문·발췌·원문 해시는 기록하지 않는다. 이 필드들은 실행 결과에만 있고 이전 기록의 조회 형식은 그대로다.

## 취소와 상태

`./colvia run status --grant DIGEST`는 만료 뒤에도 기록을 읽는다. `./colvia run cancel --grant DIGEST --reason cancelled`는 다른 CLI에서 immutable 취소 marker를 게시한다. v2의 reason은 고정 코드이며 자유문구를 저장하지 않는다. 기본값은 `cancelled`다. 요청 접수는 효과 중단 확인과 다르며, 이미 허용된 worker는 완료될 수 있다. Host는 이후 worker를 거절하고 공식 turn interrupt와 관측된 프로세스 종료를 확인한다. 이미 반영된 문서를 자동으로 되돌리지 않는다. turn 시작 전 취소는 runtime 종료 확인 후 `revoked-before-launch`로 남는다. `turn/start`를 보냈지만 turn ID를 받지 못했어도 모든 알려진 효과와 실제 프로세스 종료를 확인하면 `interrupted`로 닫을 수 있다. 종료나 효과를 확인하지 못하면 `unknown`으로 보존한다.

`.hrn/executions/DIGEST/`의 v2 기록은 `grant.json`, `journal.jsonl`, 선택적인 `cancel.json`·`receipt.json`만 허용한다. 승인 scope·문서 identity·고정 상태 코드·로컬 순번·효과 및 종료 근거를 저장한다. prompt, Owner 선언 원문, claim·quote·링크·anchor, 거절한 내용, 외부 callback ID, stderr·RPC·예외 원문은 capsule에 저장하지 않는다. 문서 경로와 원문 digest 등 승인 metadata는 남으며 같은 계정의 파일 변조를 방어하는 경계는 아니다. hash chain은 기록의 일관성을 검사하며 서명이나 인간 신원 인증이 아니다.

Host는 공통 writer lock을 실행과 자식 종료까지 보유한다. 취소 marker 게시만 lock 없이 허용되는 별도 쓰기다. 미종결·unknown 기록은 새 실행, Work·intent·candidate·continuation의 일반 쓰기와 lifecycle 변경을 막는다. 관측되지 않은 detached daemon의 부재까지 보장하지 않는다.

읽기 worker 한도가 1회이면 첫 읽기가 성공하고 해당 worker 종료와 callback 완료가 기록된 뒤 최대 5초 동안 취소를 받는다. 이때 다음 worker를 시작하거나 stdout 콜백을 처리하지 않으며, 전체 실행 마감과 grant 만료가 우선한다. 해당 grant의 유효한 표식을 기한 안에 확인하면 `cancelled`로, 없으면 `worker_budget_consumed`로 권한을 철회한다. Host가 이 구간에서 취소를 확인하면 읽기 완료 기록은 남기고, 런타임에는 문서 내용 없이 취소 사유만 응답한 뒤 턴 중단을 요청한다. 5초에 도달하면 접수 구간이 끝난다. 그때까지 취소를 확인하지 못했다면 완료한 읽기 결과를 전달하고 worker 한도 소진으로 중단을 요청한다. 대기 중 stderr에도 같은 거부 규칙이 적용된다.

취소 명령의 `cancel_requested=true`는 요청 접수다. `run execute`의 `cancel_seen_after_read=true`는 Host가 그 표식을 읽기 후 접수 구간에서 확인했다는 뜻이다. `runtime_interrupt_confirmed=true`는 런타임에서 같은 턴의 `interrupted` 응답을 확인했을 때만 표시된다. 이 값들을 철회 사유, 최종 상태, 문서 효과 및 프로세스 종료와 함께 확인한다. 필드가 없는 과거 실행에는 이 관측을 소급하지 않는다.

## 효과와 종료 상태

상태와 문서 효과는 별도로 읽는다. `completed`는 read→write→세 검증→seal과 모든 종료 근거를 요구한다. `interrupted`는 권한이 철회되고 pending callback·미해결 worker·unknown 효과가 없으며 runtime 종료가 확인된 상태다. `revoked-before-launch`는 여기에 turn 시작 예약·callback 예약·worker intent가 없어야 한다. Host가 사라지고 terminal 기록이 없으면 `incomplete`로 남는다.

| `document_write_effect` | 판정 |
| --- | --- |
| `none` | write intent가 없거나 모든 write spawn이 동기적으로 실패해 재수거가 확인됐다. |
| `applied` | Host가 실제 출력의 사후 조건과 identity를 확인했다. 이후 검증·프로토콜 거절이 발생해도 이미 반영된 효과는 유지한다. |
| `unknown` | write가 시작됐으나 성공 사후 조건을 확인하지 못했다. 관측된 bytes가 이전과 같다는 이유만으로 `none`으로 낮추지 않는다. |

execute 오류의 고정 코드는 효과가 없었다는 증거가 아니다. 오류 안내에 따라 `run status`에서 효과·종료 상태를 확인한 뒤 후속 작업을 판단한다. 효과 시작 전 내용 거절은 write 예약을 만들지 않는다. read 또는 verifier의 알려진 실패는 종료 확인 뒤 `interrupted`로 닫을 수 있다. deadline·취소·오류 자체가 효과를 되돌리거나 자동으로 unknown을 해제하지 않는다. 부분 journal이나 확인하지 못한 효과·종료 근거는 계속 쓰기를 차단한다.

`./colvia run resolve --grant DIGEST`는 현재 문서, journal head, 기록된 프로세스 부재를 확인하는 preview를 만든다. 같은 명령에 `--confirm DIGEST`를 붙이면 `operator-resolved-unknown`을 기록한다. 이는 문서 복원·재시도·원 승인 재활성화 또는 기존 효과의 재분류가 아니다. runtime·worker의 spawn intent가 있는데 PID와 birth를 확정하지 못했으면, 현재 group이 없다는 관측만으로 resolve할 수 없다. v2 process 시작 시각은 C locale·UTC로 관측한다. v1 기록의 child 시작 시각은 언어가 고정되지 않았으므로, 해당 PID가 현재 존재하면 부재로 확정하지 않는다. PID가 재사용된 경우에도 실제 부재가 확인될 때까지 resolution이 보류될 수 있다. 기존 기록의 상태나 원문은 바꾸지 않는다. 부분 journal도 자동 수리하지 않는다. 이런 경우 일반 쓰기와 detach가 계속 막히며 자동 해제 경로는 없다. 동기적인 spawn 실패는 별도의 실패 근거로 자동 종료할 수 있다.

## 외부 복구본과 정리

출력 원문은 write preflight를 통과한 뒤, write 예약 전에 `host_control_root/recovery/GRANT/1/`의 `original.bin`과 `manifest.json`으로 내구성 있게 저장한다. 읽기만 하거나 내용이 거절된 실행에는 원문 복구본을 만들지 않는다. 저장 실패는 효과를 시작하지 않으며 부분 파일은 조사 대상으로 보존한다. 복구본은 Owner의 실행 결과 수락 전까지 보존하고 자동 만료·복원·재생하지 않는다.

worker spec·sandbox profile·swap은 `host_control_root/transient/GRANT/worker-NNN/`에 둔다. 요청 본문은 stdin pipe로 보내며 별도의 request·stderr 파일을 만들지 않는다. 모든 worker/runtime 종료와 자동 closed 상태가 확인된 뒤 transient를 정리한다. 정리 실패는 `cleanup_pending`으로 알리며 실행 효과를 재분류하지 않는다. `operator-resolved-unknown` 뒤의 transient 정리는 별도 수동 판단이다.

기본 status의 `recovery_availability`, `transient_presence`, `cleanup_marker_presence`는 `not_checked`다. 명시적 root 조회는 잔존 transient와 cleanup marker를 `present`·`absent`로 보고하며 root나 파일을 확인할 수 없으면 `unavailable`로 보고한다. 이 조회는 정리하거나 실행 권한을 복원하지 않는다. `./colvia run status --grant DIGEST --host-control-root PATH`로 명시하면 `recovery_availability`는 `not_required`, `present`, `missing`, `mismatch`, `orphan_candidate` 중 하나를 보고한다. resolve preview와 확정에도 같은 옵션을 사용할 수 있으며 관측 결과는 확인 digest에 결속된다. 복구본의 분실·불일치가 과거 실행 상태나 효과를 바꾸지는 않는다.

## 설치 전환과 기록 보존

`official-execution-2`는 기존 window와 분리된 48경로 inventory와 lifecycle schema8을 사용한다. 검증된 exact `official-execution-1` predecessor에서만 update하며, 첫 새 전환 receipt 이후 구 window rollback을 거절한다. 그 밖의 update·rollback은 검증된 동일 window 안에서만 허용하고 Windows 교차 전환도 거절한다. detach의 잔존 이력 판독은 `continuation-1`과 공식 실행 두 window로 제한된다. 더 오래된 `delegation-1` 등 이력을 보존한 프로젝트는 전환 뒤에도 detach가 거절될 수 있다. 이 기존 제한을 자동 이력 삭제나 허용 범위 확대로 우회하지 않는다. v1 기록은 기존 의미로 읽고, 구 reader는 v2를 거절한다. v1 raw 기록을 자동 이관하거나 삭제하지 않는다.

detach는 실행 capsule을 보존하며 외부 host control 저장소를 변경하지 않는다. retained `.hrn` 위에 fresh init을 덮어쓰지 않는다. runtime 제거 뒤에도 JSON 원문을 읽을 수 있다. 종료된 Host의 읽기 전용 복원은 기존·새 callback을 모두 거절하며 worker나 권한을 되살리지 않는다. 공식 window의 변경 작업과 detach는 macOS에서 수행하며 다른 OS의 clone은 원문 판독 범위로 제한된다. capsule은 Git 제외 대상이 아니므로 commit 전에 남은 로컬 경로·identity metadata와 기존 v1 원문을 검토한다.

## Runtime 입력과 지원 경계

공식 CLI 0.165.0의 고정 binary/helper identity, 허용된 Python, 기존 기본 ChatGPT 로그인, 설정·rules·전역 지침의 명시적 읽기 경로를 사용한다. 임의 API key/provider, 추가 도구·MCP, 별도 권한 profile은 허용하지 않는다. 고정 macOS 정책은 App Server와 문서 worker를 분리하며 문서 읽기와 쓰기는 Host가 허용한 worker만 수행한다. 문서 worker에는 network 권한을 주지 않지만 공식 CLI는 인증·통신을 수행하는 신뢰 구성요소로 TCP/DNS 등을 사용할 수 있다. 이를 TLS 목적지 allowlist나 전체 외부 전송 보호로 해석하지 않는다. 다른 OS나 CLI 버전의 제품 지원을 이 결과로 추론하지 않는다.

## 추가 로컬 링크 검증

`documents.link_targets`는 모델이 읽을 문서 목록을 늘리지 않는다. 각 `path`는 worker root 아래의 존재하는 일반 파일을 가리키는 절대 실제 경로다. symlink·hardlink·dev/inode 중복·문서와의 중복, 대소문자를 달리한 `.git`/`.hrn` 및 `colvia` 경로는 거절한다. 초기 출력 전체의 로컬 링크에서 참조한 추가 대상과 anchor를 빠짐없이 정확히 지정해야 하며, 참조하지 않은 추가 경로나 anchor도 거절한다. 폴더 링크는 지원하지 않는다. anchor는 `#` 없이 URL decode된 정확한 문자열이며 대소문자를 유지한다. 중복은 거절하고 spec에는 정렬해 저장한다.

예를 들어 출력에 `guide.md#설치`를 가리키는 로컬 링크가 있고 guide.md가 files에 없으면, 그 파일의 절대 실제 경로와 `anchors: ["설치"]`를 지정한다. fragment 없는 링크만 있으면 `anchors: []`다. 추가 링크 metadata 처리와 문서 worker는 이런 대상의 파일 identity·권한·크기·mtime만 결속하고 본문 읽기 권한을 추가하지 않는다. 기존 trusted Host의 Work snapshot은 프로젝트 파일 내용을 읽어 digest를 확인하며 이 변경으로 제거하거나 축소하지 않는다. 그 내용은 모델에 보내지 않는다. 내용 동일성을 보장하지 않으며 같은 크기로 내용을 바꾸고 mtime을 복원하면 검출하지 못한다. anchor 대상만 최대128KiB UTF-8 본문을 읽어 digest와 지정 anchor를 확인한다. 어느 경우도 추가 본문을 모델에 전송하지 않는다.

prepare는 원본 출력 전체의 DOC-LINKS를 in-process 읽기 전용으로 실행하며 파일·capsule·worker를 만들지 않는다. 초기 출력의 로컬 링크 대상 누락·범위 밖 경로·anchor 누락·미승인 외부 링크·query 또는 절대 경로 링크는 편집 구간 안에 있어도 기존 요청을 거절한다. 따라서 그런 링크를 고치는 작업은 이 제한된 진입점의 지원 범위 밖이다. 사전검사는 링크 오류만 거절하므로 active HTML 제거 작업을 새로 막지 않으며, 수정 뒤에는 기존 전체 검증이 남은 active HTML도 거절한다. files에 없는 새 metadata 대상이나 기존 metadata 대상의 새 anchor는 초기 링크에서 승인할 수 없다. 이미 files에 포함된 문서와 그 유효한 anchor는 기존 범위다. 모델이 새 범위 밖 링크를 쓰면 사후 검증이 실패하며 자동으로 재시도하지 않는다.

실행 전에 preview의 대상·anchor·metadata를 확인하고, 실행 중에는 링크 대상도 변경하지 않는다. metadata 변경은 drift로 중단될 수 있으며 모델 오류로 간주하지 않는다. 마지막 확인 뒤 파일이 사라지지 않는다는 보장은 없다. 이미 남은 capsule의 status/cancel/resolve/closed restore는 링크 대상의 현재 상태를 다시 승인 조건으로 삼지 않으며, 원 기록은 보존한다.

추가 대상의 경로·anchor·metadata는 승인된 live spec과 외부 transient에서 취급하며 v2 capsule에는 복사하지 않는다. 기존 v1 capsule에 남은 metadata와 원문은 그대로 보존한다. 새 link_targets를 쓰는 실제 adopter 실행 전에는 opaque/anchor·하위 폴더·opaque 본문 읽기 거절을 포함한 합성 native sandbox worker 검증이 필요하다. 소스의 in-process 검증이나 profile 검사만으로 이 OS 실행 경로를 입증하지 않는다.

## Completed History After Git Checkout

같은 canonical target에서는 무결성과 기존 종료 상태가 확인된 journal을 `0600` 또는 `0644`로 읽을 수 있다. Git checkout 결과도 이 두 권한일 때만 허용한다. 검증한 umask `022`와 `077`에서는 각각 `0644`와 `0600`으로 재생성된다. `0640`·`0664` 등 다른 결과는 계속 거절하며, 읽을 수 없는 이력이 있으면 일반 쓰기와 lifecycle도 차단된다.

판독기는 파일 권한을 바꾸거나 실행 권한을 복원하지 않는다. 종료 이력에는 append 가능한 journal 객체를 반환하지 않으며, 늦은 callback·cancel·resolve가 종료된 실행을 다시 열지 못한다. 미종결·unknown 실행은 기존 private control-file 판정을 유지하고 일반 쓰기를 계속 막는다. 소유권·link·파일 변경·hash chain·종료 근거가 부적합한 기록도 거절한다. 기존 generic private mask가 허용하던 종료 이력의 `0400`·`0700`·특수 권한 역시 새 종료 이력의 허용 집합에 포함되지 않는다.

checkout으로 파일·디렉터리가 `0644`·`0755`가 되면 journal뿐 아니라 grant 등의 metadata도 다른 로컬 사용자에게 읽힐 수 있다. v1 복구본은 기존 capsule에 남지만 v2 외부 복구본은 Git checkout 대상이 아니다. 이번 판독 허용은 기밀성 보장이 아니다. 다른 경로의 clone은 기존 grant-target 검사에서 계속 거절되며, 승인 경로를 재결속하거나 실행을 이전하지 않는다. 구 window의 reader는 v2를 거절하므로 구 window로 rollback하지 않는다. 동일 window rollback도 정확한 대상 reader와 현재 기록 상태의 호환성을 확인해야 한다.


## Local Payload Checks And Remaining Boundaries

공식 v2 경로는 신뢰하는 로컬 호출자·Host·runtime·인증 CLI를 전제로 모델과 문서가 요청하는 효과를 제한한다. 최초 confirm은 인간 인증이 아니며, 같은 계정의 다른 agent가 Host나 검사기를 수정하거나 직접 파일·네트워크를 사용하는 행위를 차단하지 않는다. 일반 desktop 전체 보호는 이 경로의 지원 범위가 아니다.

초기 prompt와 고정 문서 view, 출력에서 그대로 보존할 prefix/suffix는 prepare와 CLI 시작 전에 검사한다. 보존 영역 자체에서 이미 거절될 내용은 CLI를 시작하거나 문서를 전달하기 전에 거부하며, 이 검사가 보존 영역을 모델에 전송하는 것은 아니다. 이후 Colvia가 제공하는 도구 결과는 JSON 문자열 안의 내용을 풀어 검사하고 실제 송신 frame의 첫 byte를 쓰기 전에 판정한다. 출력 교체 내용과 보존된 문자의 경계에서 비밀 패턴이 만들어질 수 있으므로, 쓰기 예약 전에 합성한 전체 출력도 검사한다. 이에 따라 편집 구간 밖에 기존 비밀 후보나 허용되지 않은 식별자가 있는 문서는 편집이 거부될 수 있다. 자동 마스킹·예외 승인·검사 끄기 fallback은 없다.

검사 대상은 크기·깊이·항목 수가 제한된 UTF-8 JSON/text다. private-key 표식, 기존 sk-/Bearer/token 패턴과 명시적 password/secret 할당, 일부 token 형식 등의 제한된 로컬 탐지이며 범용 비밀 탐지가 아니다. 미지원 형식·크기 초과·검사 오류·deadline은 해당 전달/의존 효과를 거부한다. password/secret 등의 할당 검사는 제한된 평면 문자열 패턴이며, 민감 키 아래의 임의 구조를 해석하는 분류기가 아니다. 예를 들어 password 값이 배열·객체이거나 짧은 접두사 뒤 쉼표가 있는 값, 추가 escape가 남은 문서 문자열은 놓칠 수 있다. 암호화·인코딩·분할·의미 은닉·임의 비밀번호의 미탐과 오탐은 남는다. `task-management-system`, `Bearer authentication`, `password: required`, 코드 안의 Windows 경로처럼 보이는 escape, `/home/`가 든 정상 URL도 거부될 수 있다. 승인 목록에 넣은 mailto 주소도 이메일 식별자 검사에 걸리므로 현재 v2 문서 payload에서는 사용할 수 없다. 이는 알려진 보수적 오탐이며 예외 승인으로 통과시키지 않는다. 허용 목록 밖 원천 접근 거부와 허용 문서 내부의 내용 탐지는 다른 보호다. Host/worker는 view 밖 원본을 읽을 수 있다.

송신은 고정된 request method와 initialized notification, 정확한 result/item 형태만 허용하며 임의 error frame과 추가 필드는 거부한다. protocol metadata의 필요한 runtime 경로 허용은 그대로이며 모든 params의 의미를 새로 인증하는 기능은 아니다. 부분 frame이 한 번 쓰인 뒤 실패하면 interrupt를 포함한 이후 모든 send를 거부하고 기존 부분 전달 관측을 유지한다. 이미 CLI에 전달한 frame이나 일부 bytes는 이후 거절로 회수되지 않는다. 로컬 pipe의 byte/frame 관측은 실행 중 메모리에만 있고 기존 capsule schema에는 추가하지 않는다. durable 상태만으로 provider 수신 여부나 비전송을 재구성할 수 없다. document_write_effect가 none이어도 이전 문서 payload가 전달됐을 수 있으며, 쓰기 뒤 전달 실패라면 확인된 applied 효과를 유지한다. CLI의 추가 문맥·인증·실제 TLS 목적지/계정·저장 전체는 이 검사 밖이다. 승인된 문서 링크 목록도 network 목적지 제한이 아니다.

소스·합성 검증, 실제 OS 정책 집행, 독립 승인, provider 전송 검증은 별도 근거를 요구한다. 모델이 공격을 자발적으로 거절한 응답은 강제 차단 증거로 사용하지 않는다.
