# Harness v2로 첫 프로젝트 진행하기

[실습 시작](getting-started.md) · [핵심 개념](concepts.md)

[English](../en/README.md)

AI와 진행하던 프로젝트를 다시 열면, 지난 대화만으로는 어떤 요청을 승인했고 결과까지 수락했는지 알기 어려울 수 있습니다. Harness v2는 그 기록을 프로젝트에 남깁니다. 작업 범위와 결과 수락은 사람이 결정하고, agent는 기록을 준비하고 승인된 작업을 수행합니다.

이 안내는 작은 프로젝트 하나를 준비해 첫 작업(Work)을 완료한 뒤, 이전 대화 없이 파일과 기록으로 재개하는 과정을 다룹니다. 예제는 할 일을 추가하고 순서대로 조회하는 Python CLI입니다. 사용자가 Harness JSON을 직접 작성할 필요는 없습니다.

## 시작하기 전에

지속적으로 보관할 수 있는 디렉터리에 새 실습 프로젝트를 준비합니다. 실습 내용은 버려도 되지만, 작업 중인 프로젝트를 임시 디렉터리에 두지는 않습니다. Git과 정식 GIL 활성화 빌드의 **CPython 3.14.6 또는 3.14.7이** 필요합니다. launcher가 사용하는 `python3` 명령도 해당 runtime을 가리켜야 합니다. 이후 patch 버전, prerelease, free-threaded 빌드는 거부됩니다.

`checkout-1` profile에 맞는, 신뢰할 수 있고 검증된 별도 Harness source checkout도 필요합니다. 이 private 개발판에는 공개 installer나 다운로드 경로가 없습니다. 시작하기 전에 maintainer에게 managed release가 아래 digest와 일치하는 source checkout과 해당 artifact의 qualification receipt를 받으세요. 사용할 환경이 그 기록의 검증 범위에 들어가는지도 확인합니다. 이 안내의 합성 실습은 해당 qualification을 대신하지 않습니다. agent는 로컬 파일을 읽고 승인된 명령을 실행할 수 있어야 합니다.

예시는 프로젝트 대화에서 Codex에게 요청하는 문안입니다. 실제 대화의 인용이나, 해당 문안으로 항상 같은 agent 행동을 얻는다는 검증 결과는 아닙니다. 프로젝트 지침과 실행 권한은 그대로 적용됩니다.

## 가장 짧은 경로

| 읽을 문서 | 할 일 | 다음 단계로 가기 전 확인할 결과 |
| --- | --- | --- |
| [프로젝트 준비](getting-started.md) | 프로젝트 준비, Harness 설치, 초기 계획 작성 | 설치가 정상이며, 설치만으로 작업 요청서나 Work가 생기지 않음 |
| [첫 Work 완료](first-work.md) | 요청 하나를 수락하고, 정해진 범위를 구현해 결과 검토 | 수락한 결과가 선택돼 있고 현재 파일도 그 결과와 일치함 |
| [새 세션에서 재개](resume.md) | 이전 대화 없이 프로젝트와 Harness 기록 읽기 | 완료한 것, 미확인 사항, 새 결정이 필요한 일을 설명할 수 있음 |
| [핵심 개념](concepts.md) | 책임, 용어, 진행을 멈춰야 할 상황 확인 | 제안·수락된 작업 요청서·완료된 Work를 구별함 |

앞의 세 문서를 순서대로 읽고, 낯선 용어가 나오면 핵심 개념을 참고하세요. 실습에서는 local Work 하나만 편집합니다. worker worktree나 병렬 실행은 다루지 않습니다.

## 확인한 범위

2026-10-05 macOS·CPython 3.14.7의 합성 Git 프로젝트에서 준비, 실제 source 설치, 정해진 형식의 작업 요청서 수락, local Work 제출·수락, 읽기 전용 재개를 실행했습니다. 예제 CLI는 빈 목록 조회, 순서를 지키는 추가·조회, 파일을 쓰지 않는 빈 할 일 거부, 데이터를 바꾸지 않는 조회의 네 가지를 검사했습니다. 각각 새로 실행한 CLI 프로세스에서 완료 기록과 변경되지 않은 결과를 읽었습니다.

실습의 수락 결정은 스크립트로 처리했습니다. **독립된 새 agent 세션과 실제 사람의 이해도는 시험하지 않았습니다.** Windows, Linux, 클라우드 배포, 잘못된 할 일 데이터의 복구, 일반적인 온보딩 사용성도 이번 실습에서 시험하지 않았습니다. runtime 버전 허용과 운영체제 검증은 별개입니다. [Security and Support](../../docs/SECURITY-AND-SUPPORT.md)를 참고하세요.

이 문서는 repository에서 읽는 검토판이며, 설치 프로젝트의 managed payload에 복사되지 않습니다. 설치된 프로젝트에서는 `./hv2 view`가 현재 설치본의 manual과 adapter를 안내하고, `./hv2 status`가 검증된 `documentation_root`를 보여줍니다. 실제 운영은 그 설치본 문서를 기준으로 합니다. 아래 상대 링크는 이 source checkout이나 전체 사본에서 열 수 있습니다.

## 함께 볼 문서

- [설치 절차](../../docs/GETTING-STARTED.md): 설치와 프로젝트 준비.
- [명령 참조](../../docs/REFERENCE.md): 정확한 명령, 입력 계약, 진단.
- [운영 안내](../../docs/OPERATIONS.md): 갱신, 복구, 수리, 제거.
- [핵심 개념](concepts.md#진행을-멈춰야-할-때): 첫 경로를 계속 진행할 수 없을 때의 짧은 안내.

연결된 `docs/`의 기술·운영 문서는 영어입니다.

판본: private 개발판, `checkout-1`; 확인일 2026-10-05.

| 이 판본의 source 식별값 | 값 |
| --- | --- |
| Source revision | `2536c3106494d2b409e522ff4decb39f88d4aaf5` |
| Release SHA-256 | `a5a9c5b408e40cd0bfdd6bf3c5d8d23676c138504e278417ecb656729c1b8456` |

Source revision은 이 안내를 검증할 때 사용한 Harness 기준이며, 매뉴얼 페이지 자체의 판본은 아닙니다. 이 페이지들은 해당 commit과 managed release에 포함되지 않으므로, 매뉴얼만 추가한 이후 checkout의 HEAD는 다를 수 있습니다. 설치를 승인하기 전에 agent에게 preview의 candidate release digest를 위 값 및 해당 artifact의 qualification receipt와 대조해 달라고 요청하세요.

---

[실습 시작](getting-started.md) · [핵심 개념](concepts.md)

<!-- en_content_sha256: 42d4726708a5d818e04e5f3d4afa0aaca3a7b5e993b0e94f3f1d679b272cd8fb -->
