# Colvia로 첫 프로젝트 진행하기

현재 macOS 배포·첫 Work·재개는 [여기서 시작하세요](getting-started.md). 이 후보는 최종 검증과 공개를 앞두고 있으며, 아래의 이전 관측은 당시 기록으로 유지합니다.

이 진입 안내는 continuation-1을 기준으로 합니다. 정확한 설치본의 검증과 설치 승인이 필요합니다. 연결된 단계별 실습에는 entry-1 예제가 남아 있으므로 명령은 현재 운영 문서를 따르세요. 아래의 과거 checkout-1 실습은 이 설치본의 검증 근거가 아닙니다.

[실습 시작](getting-started.md) · [핵심 개념](concepts.md)

[English](../en/README.md)

AI와 진행하던 프로젝트를 다시 열면, 지난 대화만으로는 어떤 요청을 승인했고 결과까지 수락했는지 알기 어려울 수 있습니다. Colvia는 그 기록을 프로젝트에 남깁니다. 작업 범위와 결과 수락은 사람이 결정하고, agent는 기록을 준비하고 승인된 작업을 수행합니다.

이 안내는 작은 프로젝트 하나를 준비해 첫 작업(Work)을 완료한 뒤, 이전 대화 없이 파일과 기록으로 재개하는 과정을 다룹니다. 예제는 할 일을 추가하고 순서대로 조회하는 Python CLI입니다. 사용자가 Colvia JSON을 직접 작성할 필요는 없습니다.

관리형 macOS arm64 배포 후보는 정확히 고정한 CPython 3.14.10 트리·명세와 격리 진입을 별도로 확인합니다. 기존 3.14.6·3.14.7 버전 허용 목록과 Windows 정책은 유지합니다. 상태의 admission_path는 현재 허용 경로를, supported_versions는 기존 버전 목록을 나타냅니다. 손상된 전용 Python은 원본을 보존하고 [복구 절차](../../docs/OPERATIONS.md#onboarding-update-recovery-and-removal)를 확인하세요.

## 시작하기 전에

지속적으로 보관할 수 있는 디렉터리에 새 실습 프로젝트를 준비합니다. 실습 내용은 버려도 되지만, 작업 중인 프로젝트를 임시 디렉터리에 두지는 않습니다. 이 수동 소스 실습에는 Git과 정식 GIL 활성화 빌드의 **CPython 3.14.6 또는 3.14.7이** 필요합니다. launcher가 사용하는 `python3` 명령도 해당 runtime을 가리켜야 합니다. 이 소스 실습 경로에서는 이후 patch 버전, prerelease, free-threaded 빌드가 거부됩니다. 관리형 macOS 배포는 위의 별도 진입 조건을 따릅니다.

`continuation-1` profile에 맞는, 신뢰할 수 있고 검증된 별도 Colvia source checkout도 필요합니다. 이 private 개발판에는 공개 installer나 다운로드 경로가 없습니다. 시작하기 전에 maintainer에게 source checkout과 정확한 continuation-1 artifact를 식별하는 별도 qualification receipt를 받으세요. Preview는 아래의 과거 checkout-1 digest가 아니라 그 receipt와 일치해야 합니다. 이 문서 후보는 새로운 qualification receipt를 제공하지 않습니다. 사용할 환경이 그 기록의 검증 범위에 들어가는지도 확인합니다. 이 안내의 합성 실습은 해당 qualification을 대신하지 않습니다. agent는 로컬 파일을 읽고 승인된 명령을 실행할 수 있어야 합니다.

예시는 프로젝트 대화에서 Codex에게 요청하는 문안입니다. 실제 대화의 인용이나, 해당 문안으로 항상 같은 agent 행동을 얻는다는 검증 결과는 아닙니다. 프로젝트 지침과 실행 권한은 그대로 적용됩니다.

## 가장 짧은 경로

| 읽을 문서 | 할 일 | 다음 단계로 가기 전 확인할 결과 |
| --- | --- | --- |
| [프로젝트 준비](getting-started.md) | 프로젝트 준비, Colvia 설치, 초기 계획 작성 | 설치가 정상이며, 설치만으로 작업 요청서나 Work가 생기지 않음 |
| [첫 Work 완료](first-work.md) | 요청 하나를 수락하고, 정해진 범위를 구현해 결과 검토 | 수락한 결과가 선택돼 있고 현재 파일도 그 결과와 일치함 |
| [새 세션에서 재개](resume.md) | 이전 대화 없이 프로젝트와 Colvia 기록 읽기 | 완료한 것, 미확인 사항, 새 결정이 필요한 일을 설명할 수 있음 |
| [핵심 개념](concepts.md) | 책임, 용어, 진행을 멈춰야 할 상황 확인 | 제안·수락된 작업 요청서·완료된 Work를 구별함 |

앞의 세 문서는 이전 entry-1 실습을 보존하고 있습니다. 현재 source에 그 profile 명령을 실행하지 마세요. 현재 설치는 [Getting Started](../../docs/GETTING-STARTED.md)를 따르고, 이후 설치본의 view와 adapter를 읽습니다. 낯선 용어는 핵심 개념을 참고하세요. 실습에서는 local Work 하나만 편집합니다. worker worktree나 병렬 실행은 다루지 않습니다.

## 선택한 후속 작업으로 재개하기

새 세션에는 이렇게 요청할 수 있습니다. “프로젝트 진입 지침, 현재 Colvia view와 이 Work가 참조하는 계획을 읽고, 수락한 결과·남은 계획 항목·내가 선택한 다음 행동을 설명해줘.” 이 문안은 권장 예시이며, 사용성 검증을 완료했다는 뜻은 아닙니다.

agent는 완료된 Work도 `./colvia view continuation WORK_ID`로 확인합니다. 후속 제안에는 작업 요청서 수락이 더 필요하고, 기존 Work는 그 Work의 현재 상태와 권한을 따릅니다. ‘후속 없음’은 후속을 두지 않기로 한 결정이고, ‘미정’은 아직 선택이 없다는 뜻입니다. 후속 선택만으로 대상 작업이 시작되거나 수락되지는 않습니다. 유효한 프로젝트 후보 선택과 후속 선택이 다르면 둘을 보여주고 어떤 행동을 원하는지 확인하며, 어느 쪽도 임의로 덮어쓰지 않습니다.

착수 전에는 기존 계획의 어느 항목을 수행하는지 밝힙니다. 결과 검토 때는 완료 처리 제안과 실제 수락을 구분하고, 수락 후에는 달성한 내용·잔여·아직 필요한 계획 문서 수정을 설명합니다. 문서 수정에는 기존 범위·참조·내용 검증 규칙이 그대로 적용되며 별도 진행 장부는 필요하지 않습니다. 계획 누락이나 오래된 참조는 해결할 공백이며, 계획 정렬이 끝났다는 근거가 아닙니다.

view에는 Work별 일반 연산 256회 중 사용량과 잔여 횟수가 나옵니다. 저장된 선택·철회는 나중에 취소해도 사용량에 포함되며, 조회·동일 요청 재시도·중단 연산 취소는 일반 연산을 추가로 쓰지 않습니다. 상한에서는 정확한 복구·취소는 가능하지만 새 선택은 거부됩니다. 확인할 수 없는 사용량은 ‘확인 불가’로 표시합니다. 횟수를 되돌리려고 이력을 지우거나 Work를 억지로 나누지 않습니다.

“검사가 통과할 때까지 계속 개선해줘”라는 요청에서는 기존 Work의 범위·검증 방법·예산·정지 조건을 먼저 확인합니다. 별도 결과와 수락 경계가 있을 때 새 Work를, 자식 결과의 개별 수락과 통합 결과 검증이 모두 필요할 때 parent를 제안합니다. agent는 선택 이유와 착수 조건을 설명하며, 이 문구를 무제한 실행 권한으로 해석하지 않습니다. [현재 adapter](../../adapters/colvia-work/SKILL.md#follow-up-and-plan-alignment)를 참고하세요.

## 확인한 범위

과거 checkout-1 후보로 2026-10-05 macOS·CPython 3.14.7의 합성 Git 프로젝트에서 준비, 실제 source 설치, 정해진 형식의 작업 요청서 수락, local Work 제출·수락, 읽기 전용 재개를 실행했습니다. 예제 CLI는 빈 목록 조회, 순서를 지키는 추가·조회, 파일을 쓰지 않는 빈 할 일 거부, 데이터를 바꾸지 않는 조회의 네 가지를 검사했습니다. 각각 새로 실행한 CLI 프로세스에서 완료 기록과 변경되지 않은 결과를 읽었습니다.

실습의 수락 결정은 스크립트로 처리했습니다. **독립된 새 agent 세션과 실제 사람의 이해도는 시험하지 않았습니다.** Windows, Linux, 클라우드 배포, 잘못된 할 일 데이터의 복구, 일반적인 온보딩 사용성도 이번 실습에서 시험하지 않았습니다. runtime 버전 허용과 운영체제 검증은 별개입니다. [Security and Support](../../docs/SECURITY-AND-SUPPORT.md)를 참고하세요.

이 문서는 repository에서 읽는 검토판이며, 설치 프로젝트의 managed payload에 복사되지 않습니다. 설치된 프로젝트에서는 `./colvia view`가 현재 설치본의 manual과 adapter를 안내하고, `./colvia status`가 검증된 `documentation_root`를 보여줍니다. 실제 운영은 그 설치본 문서를 기준으로 합니다. 아래 상대 링크는 이 source checkout이나 전체 사본에서 열 수 있습니다.

## 함께 볼 문서

- [프로젝트 규칙 확장과 Colvia 제거](rules-and-removal.md): 자체 지침, runtime 갱신과 detach 후 진입 지침 정리.
- [설치 절차](../../docs/GETTING-STARTED.md): 설치와 프로젝트 준비.
- [명령 참조](../../docs/REFERENCE.md): 정확한 명령, 입력 계약, 진단.
- [운영 안내](../../docs/OPERATIONS.md): 갱신, 복구, 수리, 제거.
- [핵심 개념](concepts.md#진행을-멈춰야-할-때): 첫 경로를 계속 진행할 수 없을 때의 짧은 안내.

연결된 `docs/`의 기술·운영 문서는 영어입니다.

과거 실습 — 판본: private 개발판, `checkout-1`; 확인일 2026-10-05.

| 과거 checkout-1 실습 식별값 | 값 |
| --- | --- |
| Source revision | `2536c3106494d2b409e522ff4decb39f88d4aaf5` |
| Release SHA-256 | `a5a9c5b408e40cd0bfdd6bf3c5d8d23676c138504e278417ecb656729c1b8456` |

위 source revision과 digest는 과거 Harness v2 checkout-1 실습을 식별하며, 현재 continuation-1 source나 매뉴얼 페이지의 식별값이 아닙니다. 이 페이지들은 해당 commit과 managed release 밖에 있습니다. 과거 식별값은 당시 근거로 보존하고 continuation-1 설치 승인에 사용하지 마세요. 새 preview는 별도로 받은 정확한 continuation-1 qualification receipt와 대조합니다. HEAD가 다르다는 사실만으로 release qualification이 성립하지는 않습니다.

---

[실습 시작](getting-started.md) · [핵심 개념](concepts.md)

<!-- en_content_sha256: e6b02cca8cb0ddb810b231e41ada4f11823c7ee59aeec69169e1ca89fb99558a -->
