# 공식 문서 실행

이 진입점은 명시적으로 준비하고 설치한 macOS `official-execution-1` 후보에서만 사용할 수 있다. 기본 `continuation-1` 설치나 Windows 설치에는 실행 기능을 추가하지 않는다. 설치된 payload의 검증과 실행 결과 수락은 별도다. 이 후보의 검증 범위와 남은 한계는 소스 개발 기록에 따른다.

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

## 준비와 실행

설치된 프로젝트에서 `./colvia run --input request.json` 또는 `./colvia run prepare --input request.json`으로 preview를 만든다. 입력은 canonical JSON이며 실제 Work ID, worker root, 읽을 문서 ID 순서, 단일 출력 문서와 UTF-8 byte 편집구간, 근거 문구, 요청 prompt, Owner 승인 문구, 실행시간과 만료, 고정 runtime 입력을 포함한다.

Agent가 입력을 준비하더라도 trusted operator가 전송할 문서·구간·prompt와 실행범위를 확인해야 한다. 모델이 경로·실행파일·정책·argv를 선택하지 않는다. 읽기는 승인된 문서 view만 전달하며 출력은 한 번의 구간 교체만 허용한다. `DOC-LINKS`, `DOC-GFM`, `DOC-CLAIMS`를 순서대로 실행한다. 문서 최대 크기는 파일당 128 KiB이며 실제 전송 view 전체가 단일 64,000-byte 도구 응답에 들어가야 한다. 문서 ID는 ASCII 영숫자이고 정렬된 순서로 지정한다.

preview의 `spec`만 별도 canonical JSON 파일에 저장한 뒤 `./colvia run execute --input spec.json --confirm DIGEST`로 실행한다. 승인과 실행 사이에 문서, Work 선택, intent, 설치 release, runtime 입력이 달라지면 거절한다. 같은 grant는 한 번만 소비한다. 실행 후에는 기존 grant를 재사용하지 않고 현재 문서에 결속한 새 preview와 승인이 필요하다.

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
| `documents.approved_external_links` | 허용할 HTTPS 또는 mailto 링크 목록. |
| `documents.link_targets` | 선택 필드. 초기 출력 전체에서 참조하지만 files에 없는 로컬 대상의 `{path, anchors}` 목록. 최대64개이며 빈 목록은 생략한다. anchor가 있는 대상은 최대8개, 대상별 anchor는 최대32개·각512 UTF-8 byte다. |
| `read_ids` | files의 모든 ID를 정렬한 목록. 문서는 1–8개이며 근거를 위한 참조 문서가 필요하다. |
| `prompt`, `owner_statement` | 수행 지시와 로컬 운영자의 승인 선언. 각각 최대 32 KiB와 4,096자. |
| `runtime` | 아래 고정 `paths`, `sha256` 집합. 임의 인자는 받지 않는다. |
| `runtime_root` | 프로젝트와 겹치지 않는 기존 전용 폴더. 소유자 외 권한이 없어야 한다. grant별 runtime 자료가 남는다. |
| `expires_wall_ns` | 현재 이후 24시간 이내의 Unix nanosecond 시각. |
| `seconds`, `worker_limit` | 30–600초와 worker 1회 또는 5회. 1회는 읽기 후 취소 검증용이다. |

`runtime.paths`에는 `BIN`, `CODE_MODE_HOST`, `CODEX_CONFIG`, `CODEX_AUTH`, `INSTALLATION_ID`, `CODEX_RULES_DIR`, `CODEX_RULES_FILE`, `GLOBAL_INSTRUCTIONS`를 모두 지정한다. 설정·인증·installation ID는 기본 사용자 `.codex` 파일이어야 하며, rules 파일은 기본 rules 폴더의 직접 자식이어야 한다. 전역 지침의 논리 경로가 symlink이면 지정하는 값은 실제 대상 파일이다. `runtime.sha256`에는 이 중 `CODEX_AUTH`, `INSTALLATION_ID`, `CODEX_RULES_DIR`를 제외한 다섯 파일의 SHA-256을 지정한다. 인증 파일의 내용은 요청에 복사하지 않는다.

예를 들어 `Editable`의 byte `[9, 17)`만 바꾸고 `Reference`를 근거로 사용하면 `read_ids`는 `["Editable", "Reference"]`, output은 `"Editable"`이다. preview에서 결속된 실제 경로·구간·근거와 digest를 확인한 뒤 spec을 승인한다. `--grant`는 status/cancel/resolve, `--confirm`은 execute 또는 resolve에만 사용한다.

## 취소와 상태

`./colvia run status --grant DIGEST`는 만료 뒤에도 기록을 읽는다. `./colvia run cancel --grant DIGEST --reason "중단 사유"`는 다른 CLI에서 immutable 취소 marker를 게시한다. 요청 접수는 효과 중단 확인과 다르며, 이미 허용된 worker는 완료될 수 있다. Host는 이후 worker를 거절하고 공식 turn interrupt와 관측된 프로세스 종료를 확인한다. 이미 반영된 문서를 자동으로 되돌리지 않는다. turn 시작 전 취소는 runtime 종료 확인 후 `revoked-before-launch`로 남는다. `turn/start`를 보냈지만 turn ID를 받기 전에 취소되면 interrupt 대상을 확정할 수 없어 `unknown`으로 보존한다.

`.hrn/executions/DIGEST/`에 원 승인, hash-chain journal, 원문 복구본, worker 결과와 종료 근거를 보존한다. Host는 공통 writer lock을 실행과 자식 종료까지 보유한다. 취소 marker 게시만 lock 없이 허용되는 별도 쓰기다. 미종결·unknown 기록은 새 실행, Work·intent·candidate·continuation의 일반 쓰기와 lifecycle 변경을 막는다. 같은 계정의 악의적인 파일 변조나 관측되지 않은 detached daemon의 부재까지 보장하지 않는다.

## 확인할 수 없는 결과

전체 deadline이 소진되면 추가 interrupt를 시도할 시간 없이 runtime을 종료하고 unknown으로 기록한다. 문서 변경 뒤 검증기가 실패한 경우에도 이미 반영된 문서를 보존하고 unknown으로 남긴다. Host 중단이나 부분 기록은 성공·효과 없음으로 처리하지 않는다. `./colvia run resolve --grant DIGEST`로 현재 문서, journal head와 기록된 프로세스 부재를 확인하는 preview를 만든다. 확인 후 같은 명령에 `--confirm DIGEST`를 붙이면 `operator-resolved-unknown`을 기록한다. 이는 문서 복원·재시도·원 승인 재활성화가 아니다. Host가 runtime 또는 worker 시작을 예약한 뒤 프로세스 identity를 기록하기 전에 사라졌거나, 상태 관측이 불가능하면 resolve를 거절하고 자료를 보존한다. 이 경우 일반 쓰기와 detach도 계속 막히며 자동 해제 경로는 없다. 동기적인 runtime·worker spawn 실패나 Host가 직접 종료를 확인한 identity 관측 실패는 이 경우와 구분해 resolve할 수 있다.

update와 rollback은 검증된 동일 window 사이에서만 가능하다. 지정된 exact predecessor에서 새 window로 가는 update는 별도 전환 검사를 따른다. downgrade와 Windows 교차 전환은 거절한다. detach는 실행 기록과 원문 복구본을 남기며 retained `.hrn` 위에 fresh init을 덮어쓰지 않는다. runtime 제거 뒤에도 JSON 원문을 읽을 수 있다. 종료된 Host의 읽기 전용 복원은 기존·새 callback을 모두 거절하며 worker나 실행 권한을 되살리지 않는다. 공식 window의 변경 작업과 detach는 macOS에서 수행하며 다른 OS의 clone은 원문 판독 범위로 제한된다. 실행 기록은 Git 제외 대상이 아니므로 프로젝트를 commit하기 전에 원문 복구본·진단·로컬 경로를 검토해야 한다.

## Runtime 입력과 지원 경계

공식 CLI 0.165.0의 고정 binary/helper identity, 허용된 Python, 기존 기본 ChatGPT 로그인, 설정·rules·전역 지침의 명시적 읽기 경로를 사용한다. 임의 API key/provider, 추가 도구·MCP, 별도 권한 profile은 허용하지 않는다. 고정 macOS 정책은 App Server와 문서 worker를 분리하며 문서 읽기와 쓰기는 Host가 허용한 worker만 수행한다. 네트워크는 공식 runtime의 정상 TLS transport에 한정된 정책 경계를 사용한다. 다른 OS나 CLI 버전의 제품 지원을 이 결과로 추론하지 않는다.

## 추가 로컬 링크 검증

`documents.link_targets`는 모델이 읽을 문서 목록을 늘리지 않는다. 각 `path`는 worker root 아래의 존재하는 일반 파일을 가리키는 절대 실제 경로다. symlink·hardlink·dev/inode 중복·문서와의 중복, 대소문자를 달리한 `.git`/`.hrn` 및 `colvia` 경로는 거절한다. 초기 출력 전체의 로컬 링크에서 참조한 추가 대상과 anchor를 빠짐없이 정확히 지정해야 하며, 참조하지 않은 추가 경로나 anchor도 거절한다. 폴더 링크는 지원하지 않는다. anchor는 `#` 없이 URL decode된 정확한 문자열이며 대소문자를 유지한다. 중복은 거절하고 spec에는 정렬해 저장한다.

예를 들어 출력에 `[설치](guide.md#설치)`가 있고 guide.md가 files에 없으면, 그 파일의 절대 실제 경로와 `anchors: ["설치"]`를 지정한다. fragment 없는 링크만 있으면 `anchors: []`다. 추가 링크 metadata 처리와 문서 worker는 이런 대상의 파일 identity·권한·크기·mtime만 결속하고 본문 읽기 권한을 추가하지 않는다. 기존 trusted Host의 Work snapshot은 프로젝트 파일 내용을 읽어 digest를 확인하며 이 변경으로 제거하거나 축소하지 않는다. 그 내용은 모델에 보내지 않는다. 내용 동일성을 보장하지 않으며 같은 크기로 내용을 바꾸고 mtime을 복원하면 검출하지 못한다. anchor 대상만 최대128KiB UTF-8 본문을 읽어 digest와 지정 anchor를 확인한다. 어느 경우도 추가 본문을 모델에 전송하지 않는다.

prepare는 원본 출력 전체의 DOC-LINKS를 in-process 읽기 전용으로 실행하며 파일·capsule·worker를 만들지 않는다. 초기 출력의 로컬 링크 대상 누락·범위 밖 경로·anchor 누락·미승인 외부 링크·query 또는 절대 경로 링크는 편집 구간 안에 있어도 기존 요청을 거절한다. 따라서 그런 링크를 고치는 작업은 이 제한된 진입점의 지원 범위 밖이다. 사전검사는 링크 오류만 거절하므로 active HTML 제거 작업을 새로 막지 않으며, 수정 뒤에는 기존 전체 검증이 남은 active HTML도 거절한다. files에 없는 새 metadata 대상이나 기존 metadata 대상의 새 anchor는 초기 링크에서 승인할 수 없다. 이미 files에 포함된 문서와 그 유효한 anchor는 기존 범위다. 모델이 새 범위 밖 링크를 쓰면 사후 검증이 실패하며 자동으로 재시도하지 않는다.

실행 전에 preview의 대상·anchor·metadata를 확인하고, 실행 중에는 링크 대상도 변경하지 않는다. metadata 변경은 drift로 중단될 수 있으며 모델 오류로 간주하지 않는다. 마지막 확인 뒤 파일이 사라지지 않는다는 보장은 없다. 이미 남은 capsule의 status/cancel/resolve/closed restore는 링크 대상의 현재 상태를 다시 승인 조건으로 삼지 않으며, 원 기록은 보존한다.

추가 대상의 경로·inode·크기·mtime과 anchor 본문 digest도 capsule에 남아 Git commit에 포함될 수 있다. 기존 원문·진단 검토에 이 metadata도 포함한다. 새 link_targets를 쓰는 실제 adopter 실행 전에는 opaque/anchor·하위 폴더·opaque 본문 읽기 거절을 포함한 합성 native sandbox worker 검증이 필요하다. 소스의 in-process 검증이나 profile 검사만으로 이 OS 실행 경로를 입증하지 않는다.
