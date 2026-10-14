# 프로젝트와 첫 계획 준비하기

이 문서는 활성화 전 `entry-1` 후보를 설명합니다. 사용하려면 정확한 artifact의 별도 qualification과 설치 승인이 필요하며, 아래의 과거 checkout-1 실습은 현재 명령의 검증 근거가 아닙니다.

[이전: 소개](README.md) · [목차](README.md) · [다음: 첫 Work](first-work.md)

[English](../en/getting-started.md)

`todo-lab`이라는 새 실습 프로젝트로 시작합니다. 이 문서를 마치면 Colvia가 설치되고, 프로젝트 목적·초기 계획·agent 진입 안내가 준비됩니다. 설치만으로 작업이 생성되거나 수락되지는 않습니다.

## 1. 프로젝트와 작업 경로 정하기

Colvia source 밖의 지속 보관 가능한 경로에 새 primary Git checkout을 준비합니다. request와 ticket 파일은 프로젝트 밖의 별도 보관 디렉터리에 둡니다. 상위 경로에 symlink가 없는 실제 물리 경로를 사용하세요. confirmation view가 경로를 읽지 못하면 실제 경로를 확인합니다. 입력 파일을 지우거나 검사를 완화하지 마세요. 고객 프로젝트를 실습에 재사용하지 마세요. 먼저 [runtime과 source 준비 조건](README.md#시작하기-전에)을 확인합니다.

Codex에게 요청합니다.

> 내가 정한 보관 경로에 todo-lab이라는 새 실습 프로젝트를 준비해 줘. 목적은 Python 표준 라이브러리만으로 JSON 파일에 할 일을 추가하고 순서대로 조회하는 CLI를 만드는 거야. 프로젝트 경로, Colvia request와 ticket을 보관할 별도 경로, 신뢰할 source 경로와 준비 절차를 제안하고 Python과 Git을 확인해 줘. 파일 생성과 Colvia 설치는 내 승인을 기다려 줘.

경로와 source를 검토한 뒤, 준비 범위가 맞으면 승인합니다. 대상에 기존 프로젝트 파일이나 설치본이 있으면 멈춥니다. 이 신규 프로젝트 실습은 그 경우를 다루지 않습니다. [프로젝트 ignore 준비 안내](../../docs/GETTING-STARTED.md#prepare-project-ignore-rules)는 기존 프로젝트 파일의 보존 규칙을 설명하며, 기존 설치본을 갱신하는 절차는 아닙니다.

agent는 `python3 --version`, 정식 GIL 활성화 빌드 여부, `git --version`, 대상의 Git 구조를 확인합니다. linked Git worktree에서는 control 기록을 쓸 수 없으므로 이 실습은 primary checkout을 사용합니다. 버전 확인에 성공했다고 source나 운영체제 검증까지 끝난 것은 아닙니다.

## 2. 첫 Work 전에 프로젝트 파일 준비하기

agent가 Git을 초기화하고 다음 파일을 준비합니다.

| 파일 | 역할 |
| --- | --- |
| `README.md` | 할 일 프로젝트의 목적과 계획 위치 |
| `docs/plan.md` | 프로젝트 목표, 첫 기능, 나중에 검토할 기능 |
| `AGENTS.md` | 공통 프로젝트 지침, 목적·계획 pointer, 고정 진입 명령 `./colvia view` |
| `.gitignore` | 해당 프로젝트에 적용할 개인 IDE·OS·임시 파일·Python 생성 파일 규칙 |
| `docs/first-work.md` | 첫 Work의 제안 범위와 검사 방법 |

파일명은 이 실습을 위한 선택입니다. Colvia가 프로젝트 문서 구조를 강제하거나 이 파일들을 생성하지는 않습니다. Claude Code도 사용한다면, agent는 프로젝트 `AGENTS.md`를 읽도록 안내하는 짧은 `CLAUDE.md`를 준비할 수 있습니다. 도구에만 적용되는 고유 지침은 보존합니다.

[작은 ignore 기본값](../../docs/GETTING-STARTED.md#prepare-project-ignore-rules)을 사용하고, 이 Python 예제에는 `__pycache__/`와 `*.pyc`를 추가합니다. 재생성 가능한 임시 파일이 필요하면 root `temp/`를 만듭니다. `.hrn/` 전체를 ignore하지 마세요. 기록과 runtime은 Git으로 보존할 수 있어야 합니다. 대표 IDE·임시 파일이 ignore되는지 확인하고, `.hrn/format.json`, intents, Work, planning, product 파일, `colvia`, 프로젝트 Markdown이 실제 적용 규칙에 숨겨지지 않는지도 확인합니다. ignore 규칙은 이미 커밋된 파일을 추적 해제하지 않습니다.

이 준비는 Work의 비교 기준을 기록하기 전에 마칩니다. global Git ignore 규칙을 포함한 ignore 정책 변경은 이번 Work에 포함할 수 없습니다. 중요한 ignored 산출물은 작업을 멈추거나 정리하기 전에 지속 보관 가능한 사본이 필요하며, 비어 있는 `temp/`는 clone으로 복원되지 않습니다.

프로젝트 문서·검증 규칙은 필요한 것만 선택하고, agent 진입 문서에서 정본 위치를 가리킵니다. 설치나 이후 runtime update가 프로젝트 소유 규칙까지 자동 설치·갱신하지는 않습니다. [Repository-Owned Rules](../../docs/REFERENCE.md#repository-owned-rules)를 참고하세요.

## 3. 설치 내용을 검토하고 적용하기

agent에게 합의한 대상과 검증된 source로 설치를 미리 확인하도록 요청합니다. preview는 읽기 전용입니다. 정확한 요청을 승인하기 전에 대상, source, runtime profile, 생성할 파일, 보존·복구 조건을 검토합니다. agent에게 preview의 `request.plan.candidate_release.sha256`을 별도로 받은 정확한 entry-1 artifact의 qualification receipt와(README의 과거 checkout-1 digest가 아님) 대조하고 결과를 보여달라고 요청하세요. 일치하지 않으면 승인 전에 멈춥니다.

agent는 preview 응답 중 `request` 객체만 프로젝트 밖에 저장하고, 짝인 confirmation token을 함께 보관합니다. 응답 전체를 apply 입력으로 쓰지 않습니다. 사용자가 정확한 설치 요청을 승인하면 저장한 요청을 적용하고 결과를 확인합니다. token은 요청을 식별할 뿐, 사용자의 결정을 대신하지 않습니다.

<details>
<summary>agent가 사용하는 설치 명령</summary>

아래는 명령 형식입니다. agent는 검토한 경로와 실제 preview를 바탕으로 모든 `/absolute/path/...`, `UTC_TIME`, `TOKEN`을 바꿔야 합니다. 그대로 붙여 넣지 마세요. 실행 위치는 신뢰할 source checkout입니다.

```sh
./colvia --source-checkout init --profile entry-1 \
  --target /absolute/path/todo-lab --source /absolute/path/trusted-source \
  --authority-home-id todo-home --operation-id init-todo --observed-at UTC_TIME
```

정확한 요청을 승인한 뒤, 저장한 canonical request JSON으로 실행합니다.

```sh
./colvia --source-checkout init --profile entry-1 \
  --target /absolute/path/todo-lab --source /absolute/path/trusted-source \
  --apply --input /absolute/path/todo-lab-inputs/init-request.json --confirm TOKEN
```

지원되는 복구에 사용할 정확한 source와 원래 요청을 보존합니다. apply가 실패하면 대상과 입력을 보존하고 [Operations](../../docs/OPERATIONS.md)를 확인합니다. 설치를 자동 반복하거나 `.hrn/`를 삭제하지 마세요.

</details>

이후 agent가 프로젝트 root에서 실행합니다.

```sh
./colvia status
./colvia view
```

기대 결과는 정상 설치, pending 작업 없음, 수락된 작업 요청서와 Work 없음입니다. `view`가 현재 설치본의 manual과 자연어 adapter 경로를 알려줍니다. agent에게 그 경로를 읽도록 요청하세요. `AGENTS.md`에는 `./colvia view`를 유지하고 특정 release 경로를 복사하지 않습니다.

## 4. 목표를 작은 계획으로 바꾸기

Codex에게 요청합니다.

> 프로젝트 README, AGENTS.md, 현재 Colvia adapter와 docs/plan.md를 읽어 줘. todo-lab의 첫 기능은 명시적으로 선택한 JSON 파일에 비어 있지 않은 할 일을 추가하고 입력 순서대로 조회하는 것이야. Python 표준 라이브러리만 사용하고, 수정·삭제, 네트워크, 추가 의존성, 배포는 이번 Work에서 제외해 줘. 아래 CLI 규격과 네 가지 동작 검사를 사용해 줘. 이 내용과 제안 파일 범위, 검증 명령, 실행 환경, 시간·시도 한도, 중단 조건을 docs/first-work.md에 기록해 줘. 아직 작업 요청서를 publish하거나 구현을 시작하지는 마.

첫 구현은 `todo.py`, `tests/test_todo.py`, `README.md`, `docs/first-work.md`만 바꿉니다. 명령은 `python3 todo.py --file PATH add TEXT`와 `python3 todo.py --file PATH list`로 정합니다. PATH는 선택한 JSON 경로로 바꾸고 할 일 문구는 따옴표로 감쌉니다. 추가하면 `Added: TEXT`를 출력하고, 조회하면 `1. TEXT`, `2. TEXT`처럼 한 줄에 할 일 하나를 출력합니다. 초기 계획에는 네 가지 동작 검사를 적습니다. 빈 목록은 아무것도 출력하지 않고 파일도 만들지 않음, 할 일 두 개를 추가하면 입력 순서를 유지함, 빈 문자열이나 공백만 있는 할 일은 파일을 쓰지 않고 종료 코드 2로 거부함, 조회는 데이터를 바꾸지 않음입니다. 네 항목은 동작 기준이며 테스트 함수가 반드시 네 개여야 한다는 뜻은 아닙니다. 시연이 설명되지 않은 결과 변경으로 남지 않도록 테스트 데이터는 프로젝트 밖이나 이미 ignore된 임시 디렉터리에 둡니다.

다음 단계로 가기 전에 사용자와 agent가 목표, 네 파일, 제외 범위, CLI 규격, 검사, 실행 한도, 결과 보관 위치를 같은 내용으로 이해하고 있는지 확인합니다. 프로젝트 계획은 아직 제안입니다. 다음 문서에서 이를 정확한 수락 대상인 작업 요청서로 만듭니다.

과거 실습 — 판본: private 개발판, `checkout-1`; 확인일 2026-10-05.

---

[이전: 소개](README.md) · [목차](README.md) · [다음: 첫 Work](first-work.md)

<!-- en_content_sha256: 02fa67561ad487949d8ba784ebb8f3db0baeab2a8b652b689f079e8a5b535bd1 -->
