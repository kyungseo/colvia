# 첫 Work 완료하기

이 문서는 활성화 전 `entry-1` 후보를 설명합니다. 사용하려면 정확한 artifact의 별도 qualification과 설치 승인이 필요하며, 아래의 과거 checkout-1 실습은 현재 명령의 검증 근거가 아닙니다.

[이전: 준비](getting-started.md) · [목차](README.md) · [다음: 재개](resume.md)

[English](../en/first-work.md)

프로젝트에 초기 계획이 준비됐습니다. 이제 그중 한 범위를 작업 요청서로 수락하고, 합의한 작업을 수행한 뒤 결과에 대한 결정을 기록합니다. 편집하는 Work는 한 번에 하나만 유지하고, 실습 동안 프로젝트와 외부 request 파일을 보존합니다.

## 1. 작업 요청서 초안 기록하기

첫 초안을 publish하기 전에 agent에게 선언할 수락 권한자를 보여달라고 요청하고 맞는지 확인합니다. 같은 작업 요청서의 이후 초안과 연결된 Work도 같은 권한자를 유지합니다. 이 값은 역할 선언이며 인증된 신원이 아닙니다. publish 후 권한자가 잘못된 것을 발견했다면 수락하거나 기록을 고치지 말고, agent에게 지원되는 교정 절차를 확인하도록 요청하세요.

Codex에게 요청합니다.

> docs/plan.md와 docs/first-work.md를 바탕으로 todo-lab 추가·조회 기능의 작업 요청서(intent) 초안을 준비해 줘. 합의한 CLI 규격, 네 가지 동작 기준, 중요한 검증 조건을 정해진 형식의 요청서에 담아 줘. 목표, 정확한 파일 범위, 기대 결과, 수락 검사, 결과 보관 위치, 제외 범위, 미해결 질문을 보여주고 내가 무엇을 수락하게 되는지 설명해 줘. publish 전에 선언할 수락 권한자를 보여주고 내 확인을 기다려 줘. 내가 확인한 뒤 초안을 publish해 줘. 아직 초안을 수락하거나 구현을 시작하지는 마.

agent는 설치본의 `colvia intent draft`를 사용하고, 실제 ID를 넣어 `./colvia view intent INTENT_ID`로 초안을 보여줍니다. 아직 수락되지 않은 초안으로 표시돼야 합니다. 제안 기록을 publish한 것과 사용자가 수락한 것은 다릅니다.

여섯 항목을 확인합니다.

| 항목 | 이번 실습 |
| --- | --- |
| 목표 | 작은 로컬 할 일 목록 관리 |
| 범위 | `todo.py`, `tests/test_todo.py`, `README.md`, `docs/first-work.md` |
| 기대 결과 | `python3 todo.py --file PATH add TEXT`는 `Added: TEXT` 출력. `python3 todo.py --file PATH list`는 입력 순서대로 `1. TEXT`, `2. TEXT`처럼 한 줄에 하나씩 출력 |
| 수락 검사 | 빈 목록: 출력·파일 생성 없음. 순서를 지키는 추가·조회. 빈 문자열이나 공백만 있는 할 일: 쓰기 없이 exit 2. 조회: 데이터 불변. 합의한 검증 조건 사용 |
| 결과 목적지 | 현재 프로젝트. 임시 테스트 데이터는 프로젝트 밖이나 이미 ignore된 임시 디렉터리 |
| 금지 범위 | 수정·삭제, 새 의존성, 네트워크, 배포, Git commit·push |

이번 실습에서는 중요한 범위와 검사를 정해진 형식의 작업 요청서에 담습니다. 계획과 편집할 Work 문서는 설명 자료이며, digest에 결속된 필수 입력으로 두지 않습니다. 다른 문서를 필수 입력으로 선택한다면, 수정 시 재수락이 필요한 비용을 먼저 검토합니다.

수락에 영향을 주는 미확인 사항은 먼저 해결합니다. agent는 새 초안을 publish할 수 있지만, 이미 publish한 불변 초안을 고쳐 쓰면 안 됩니다. 프로젝트 계획과 Markdown Work 문서는 제안을 이해하도록 돕고, 정해진 형식의 작업 요청서는 정확히 어느 판본을 수락했는지 식별합니다.

## 2. 정확한 작업 요청서 수락하기

agent에게 수락을 준비하고 confirmation을 읽을 수 있는 형태로 보여달라고 요청합니다. agent는 응답의 `ticket`만 프로젝트 밖에 저장한 뒤 실행합니다.

```sh
./colvia view confirmation --input /absolute/path/todo-lab-inputs/intent-ticket.json
```

경로는 예시이므로 실제 저장한 ticket을 사용합니다. 프로젝트, 작업 요청서 판본, 수락 권한을 가진 사람, 범위, 제외 항목, 필수 참조 문서를 확인하세요. 이 안내의 ID·hash·token을 실제 결정에 복사하지 않습니다.

수락하기 전에 `docs/first-work.md`에서 합의한 CLI 규격, 동작 기준, 중요한 검증 조건이 초안에 담겼는지 확인합니다. 빠진 조건을 해결했다면 정확한 수락 ticket을 다시 준비합니다. 재개할 때는 이미 사용한 한도를 이어서 계산하며, 실패한 수락·설치 등의 apply를 자동 재시도하지 않습니다.

내용이 맞으면 agent에게 말합니다.

> 이 confirmation에 표시된 추가·조회 기능의 작업 요청서 판본을 수락해. 이 정확한 intent ticket을 적용해 줘. 그다음 네 파일 범위에서 Work를 시작하고 구현과 합의한 검사를 진행해 줘. 범위나 필수 입력이 달라지거나, 검증 실패를 범위 안에서 고칠 수 없거나, 수락·설치 등 기록 적용이 실패하면 멈춰 줘. commit과 push는 하지 마.

이 결정 뒤에만 agent가 정확한 ticket·token으로 `colvia intent apply`를 실행합니다. 현재 수락된 작업 요청서를 확인하고 Work의 시작 기준을 publish합니다. [machine 입력 계약](../../docs/GENERAL-WORK.md#installed-machine-commands-development)은 agent가 따르는 자료입니다. 사용자는 JSON을 작성하는 대신 제안과 confirmation을 검토합니다.

## 3. 구현하고 결과 확인하기

agent가 프로젝트에서 기능을 구현하고 정해진 검사를 실행합니다. 수락된 범위 안에서는 승인된 보정을 이어갈 수 있습니다. 기능 확대, 수락 기준 변경, ignore 정책 변경은 별도 결정이 필요합니다. Colvia가 자율 반복 실행기를 제공하거나 다른 편집기의 파일 변경을 막아주지는 않습니다.

이 예제에서는 프로젝트 root에서 실행합니다.

```sh
python3 -B -m unittest discover -s tests -v
```

기대 결과는 앞에서 정한 네 가지 동작 기준 충족입니다. 합성 실습에서는 테스트 함수 네 개로 검사했으며 실제 작성한 테스트 수는 다를 수 있습니다. 예제 애플리케이션의 검사이며 Colvia 회귀 테스트가 아닙니다.

agent에게 외부 실습 입력 디렉터리의 새 데이터 파일로 CLI를 시연하도록 요청합니다. 상위 디렉터리는 미리 있어야 합니다. 실행 전에 예시 경로를 바꿉니다.

```sh
python3 todo.py --file /absolute/path/todo-lab-inputs/tasks.json add "Read manual"
python3 todo.py --file /absolute/path/todo-lab-inputs/tasks.json add "Review result"
python3 todo.py --file /absolute/path/todo-lab-inputs/tasks.json list
```

두 추가 명령은 각각 `Added: Read manual`, `Added: Review result`를 출력합니다. 마지막 명령의 출력은 다음과 같습니다.

```text
1. Read manual
2. Review result
```

이 동작은 선택한 데이터 파일만 씁니다. 예제 애플리케이션의 잘못된 JSON, 동시 쓰기, 중단 후 복구는 이번 실습에서 검사하지 않습니다.

제출 전에 agent가 범위 안의 README와 Work 문서에 구현 내용, 검사, 한계, 다음 제안을 기록합니다. 이후 전체 결과 manifest와 검토용 판본을 publish합니다. 제출한 뒤에는 검토하는 동안 프로젝트 내용을 그대로 유지합니다. 설명 문서만 고쳐도 제출한 결과가 현재 내용과 일치하지 않게 되어, 그 결과를 그대로 수락할 수 없게 될 수 있습니다. 고칠 내용이 있으면 지원되는 rework 절차를 요청하세요. [Check Before Writing](../../docs/REFERENCE.md#check-before-writing)에 전체 내용 비교 경계가 설명돼 있습니다.

## 4. 결과를 검토하고 수락하기

Codex에게 요청합니다.

> 이번 Work에서 바뀐 내용과 관련 코드·검사 결과를 보여주고, 수락된 작업 요청서와 대조해 줘. 시험하지 않은 부분도 밝혀 줘. 선택된 Work 판본과 그 판본의 정확한 결과 confirmation을 함께 보여줘. 기록된 미관측 항목을 내 수락 기준에 하나씩 대조해 설명하고 내 결정을 기다려 줘.

agent는 반환된 Work `ticket`만 프로젝트 밖에 저장하고, 같은 선택 판본의 두 조회 화면을 보여줍니다. 여기서 선택 판본은 검토용으로 제출된 판본이며, 아직 결과를 수락한 상태는 아닙니다.

```sh
./colvia view work WORK_ID --revision REVISION_ID
./colvia view confirmation --input /absolute/path/todo-lab-inputs/work-ticket.json
```

실제 ID와 저장한 ticket 경로를 사용합니다. Work view에는 작성자가 선언한 관측 범위(`observed_scope`)와 미관측 범위(`unavailable_scope`)가 있으며, confirmation view에는 이 항목들이 반복 표시되지 않습니다. agent는 미관측 항목을 수락 기준에 하나씩 대조해 설명합니다. 범위 밖인지, 증거가 더 필요한지, 새 범위·작업 요청서 수락이 필요한지는 사용자가 결정합니다. 미관측 목록이 비어 있어도 수락 기준을 통과했다는 증거는 아닙니다. 판본이나 선택이 바뀌면 결정 전에 두 조회 화면과 ticket을 다시 준비합니다.

실제 파일도 확인하세요. manifest는 메타데이터를 보여주며 과거 파일 내용을 복원해주지 않습니다. 테스트 통과나 리뷰의 권고만으로 결과가 수락되지는 않습니다.

합의한 기준에 맞으면 agent에게 말합니다.

> 이 confirmation에 표시된 결과 판본을 수락해. 이 정확한 Work 수락 ticket을 적용하고, 적용 후 상태와 현재 파일을 확인해 줘. Git commit이나 push는 하지 마.

agent가 ticket을 적용한 뒤 Work view와 status를 확인합니다. 이번 local Work에서는 구현 내용이 이미 control checkout에 있습니다. 수락은 결정을 기록하고 수락된 결과를 선택하는 과정입니다. worker 파일을 가져오거나 구현을 다시 실행하는 과정은 아닙니다.

기대 결과는 다음과 같습니다.

- Work의 저장된 상태가 `completed`이고 pending 작업이 없습니다.
- Work와 수락된 작업 요청서의 연결이 유효합니다.
- 현재 파일 관측에 `matches stored result`가 표시됩니다.
- Git 게시는 별도 결정으로 남아 있습니다.

이전 판본의 필드에 `progress: review`나 “Owner result review”가 남아 있을 수 있습니다. 이는 agent가 제출 당시 기록한 값입니다. 저장된 완료 상태는 선택된 수락 결정으로 판단합니다. 오래된 설명을 “완료”로 보이게 하려고 기록이나 프로젝트 파일을 고치지 마세요.

apply가 실패하거나 현재 내용이 일치하지 않으면 요청과 파일을 보존하고 멈춥니다. agent에게 정확한 상태와 지원되는 복구 방법을 설명하도록 요청하세요. 화면을 완료로 만들기 위해 새 승인을 만들어내거나 기록을 삭제하지 않습니다.

## 5. 보존 방법 결정하기

Colvia는 `.hrn/`에 완료를 기록하며 commit이나 push를 수행하지 않습니다. agent에게 Git diff와 status, 보존할 파일 목록, 중요한 ignored 산출물을 보여달라고 요청하세요. 프로젝트 정책에 맞게 설치 파일, 권위 기록, source, 프로젝트 문서를 모두 확인해야 합니다.

원한다면 commit과 원격 게시를 별도로 승인합니다. 이 실습은 그 전에 멈춥니다. 프로젝트와 정확한 source·request 파일을 보관한 채 [새 세션](resume.md)으로 이동하세요.

[Records And Retention](../../docs/REFERENCE.md#records-and-retention)에 따라 검사·중요 한계·리뷰·결정은 알맞은 기존 문서 한 곳에 모으고, 원본 출력이나 사본은 구체적인 조사·복구·재사용·전달에 필요할 때만 추가로 보존합니다. 이 local 실습에는 worker checkout이 없으며, worker를 사용하는 프로젝트에서는 agent가 정리 권한과 보존 상태를 별도로 확인한 뒤 사용이 끝난 적격 checkout을 정리하거나 남은 사용처와 정리 조건을 설명합니다.

과거 실습 — 판본: private 개발판, `checkout-1`; 확인일 2026-10-05.

---

[이전: 준비](getting-started.md) · [목차](README.md) · [다음: 재개](resume.md)

<!-- en_content_sha256: 1044d764f8fa88b048cc4ebbed69d86924a3f8377946f3e1cfa58d82047cbdcb -->
