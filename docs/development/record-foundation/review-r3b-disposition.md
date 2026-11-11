# R3b 처분과 구현 진입 판단

상태: 2026-11-06 Driver 처분. [원문](review-r3b.md)은 그대로 보존했다. 새 대화 Reviewer Claude Opus 5.5, session ID 확인 불가, 지정 6개 입력만 읽었다고 보고했다. 수신 시 Driver도 6개 hash/크기를 대조했다. 정적 검토이며 실행 재현이나 플랫폼 qualification은 아니다. 허용 범위를 넘긴 읽기는 보고되지 않았다.

## 결론

구조 방향은 유지한다. 아래 보정을 해당 단계에 넣으면 구현에 들어갈 수 있으며, 새 전면 설계 리뷰를 요청하지 않는다. 본문 제거 정책과 실제 진단/초기 실행 범위는 Owner 선택으로 남긴다. [초기 구현 제안](implementation-start.md)이 이번 결정용 문서이고 [C1–C8](implementation-contracts.md)이 보정된 기술 계약이다. 기존 R3a 제안문은 역사적 처분이며 현행 계약을 대신하지 않는다.

| 항목 | 처분 | 반영과 종료 조건 |
| --- | --- | --- |
| M1 opaque entry | revise | C2/RF에서 추가·제거·종류 변경·조상 경로 쓰기를 거부한다. unchanged 링크는 whole tree/index에 보존한다. submodule 숨김 설정을 고정 override하고 내부 정책 변화를 검사한다. nested/dirty/불명은 첫 구현에서 거부한다. Windows placeholder는 Git mode와 bytes를 함께 판단한다. P1 표현, P2 관측, P8 통합 검사. |
| M2 참조·순서 | accept with clarification | kind/version/field의 역할 하나와 operation 필수 closure 표를 공용 validator가 소유한다. 의미 있는 순서는 hash된 필드/edge/head에 두고 local ordinal로 결정하지 않는다. 전체 import/audit는 반복 graph 검사이며 decision depth 64를 적용하지 않는다. unknown payload의 의미를 완전히 검사할 수 있다는 주장은 하지 않는다. P1. |
| M3 store 활성화 | accept, protocol strengthened | DB/journal 이름을 세대별 디렉터리로 분리하고 active pointer만 전환한다. 원본 quiesce, 대상 검증, 원본 fence, pointer 교체, 옛 세대 정리를 각각 기록한다. fence 뒤 pointer 전환 전 실패도 명시적 복구 대상이다. 열린 DB 이름을 덮지 않는다. P1 fault harness/P7 재사용. |
| M4 조기 진단 | accept | 결과 전이표·설정 원복·sibling/app worktree·실패한 목표 축소의 Owner 결정·OS별 미실행 표시를 초기 실행안에 포함했다. 실제 설치본을 대체하지 않는다. |
| M5 Git lock | revise | 의도와 실제 소유 증명을 구분한다. index 재획득 경로 하나와 I1 실제 bytes 검증을 고정한다. ref 자식 process lock은 자동 삭제하지 않는다. 무한 대기나 일괄 kill 대신 제한된 취소와 불명 효과를 보존한다. Windows 교체 실패는 첫 구현에서 자동 재시도 없이 알려진 N/I0 복구 상태로 종료한다. P8. |
| M6 기존 정보 노출 guard | revise | RF-27에 data identifier, prelaunch retained context, complete output, 구조 한도, zero-new-byte와 late-effect 조건을 명시했다. Driver가 확인한 nested JSON decode 주체는 safe_text가 아니라 RPC.send다. P5. |

M1의 index 보존은 개별 binary offset이 아니라 parsed mode/OID/지원 flag와 전체 결과 I1 bytes로 검사한다. Git index serialization 자체가 달라질 수 있는데 개별 entry raw bytes가 항상 같다고 요구하지 않는다. 관련 [Git link 설정](https://git-scm.com/docs/git-config#Documentation/git-config.txt-coresymlinks), [submodule 상태](https://git-scm.com/docs/git-status)를 대조했다. 새 플랫폼 시험은 하지 않았다.

M3의 위험은 [SQLite의 열린 DB rename/unlink 및 journal 짝 규칙](https://www.sqlite.org/howtocorrupt.html)에 근거가 있다. 단순히 “page 시작 때 fence 확인”만으로 활성화 전체가 원자적이라고 주장하지 않는다. C4는 진행 중 쓰기·예상 root·복구 intent·pointer 내구성도 함께 확인한다. 파일 시스템/프로세스별 동작은 구현 시험과 실제 qualification에서 확인한다.

## 본문 제거 권장안 변경

앞선 Driver는 최소 개별 제거를 권했지만, R3b와 Owner의 과설계 제한을 반영해 첫 공개는 보존과 고지를 유지하는 쪽으로 권장안을 바꾼다. 삭제 기능을 위해 지금 overlay·공유 chunk 제거·각 소비자의 의도적 부재 처리를 전부 구현하지 않는다. M3는 삭제와 무관하게 업데이트/복원 때문에 필요하므로 구현한다.

이는 “나중에 넣어도 어떤 구버전이든 계속 동작한다”는 뜻이 아니다. 후속 제거는 required capability/schema migration을 요구할 수 있고, 구버전은 그 store를 거부할 수 있다. 저장된 이력을 파괴하지 않는 확장과 모든 구버전의 읽기/쓰기 호환은 다르다. 승인 파일의 전후 본문이 보존되고 개별 제거가 없다는 조건을 연결/사용 안내에 명시한다. 민감정보 전송·PII 기능의 보강 후보와 혼동하지 않는다. Owner가 개별 제거를 공개 필수로 선택하면 그때 증가분을 분리하고 해당 코드만 추가한다.

## 연결 경계와 후속 후보

[연결 범위](connection-edge-scope.md)의 판단을 C1/C5에 반영했다. root 연결과 하위 폴더 실행은 구분하고, Git 유무 전환과 실제 scope/policy 변경은 감지·보존·안내한다. 독립 monorepo 하위 연결, 활성 Work를 유지하는 Git 자동 전환, 같은 Work 기준점 갱신은 후속 후보다. 기본 root/linked/app worktree와 수락·보존·관리 실행기 기능은 유지한다.

같은 기준으로 첫 공개에서 submodule 편집·dirty/nested submodule 자동 해결, 광범위 파일시스템 지원, 동시 편집 scheduler, 과거 시험본 이관을 추가하지 않는다. Linux/후속 에이전트 및 민감정보 기능은 기존 후속 기록을 유지한다. 구조는 identity/observation/store/OS/host port와 capability 경계까지만 만들고 범용 프레임워크는 만들지 않는다.

## 근거와 남은 결정

R3b 원문, 요청과 manifest 및 기존 실패 기록을 보존한다. 보정으로 바뀐 R3b 입력 3개의 정확한 이전 bytes만 비공개 수신 경로에 유지한다. 소비자는 Owner의 변경 대조와 P0 회귀 추적이며 이 범위 수락 및 회복 가능한 저장 후 보존 필요를 재평가한다. 전체 소스 복제본은 추가하지 않았다.

남은 선택은 (1) 첫 공개 본문 보존/개별 제거, (2) 초기 P0–P3 및 조기 호스트 진단 실행 범위·한도다. 100시간 도달 시에는 안전한 경계에 멈춰 결과·소비·잔여를 보고하고 추가 범위만 승인받는 방식을 권한다. 무조건 완주하거나 보호를 생략하지 않는다. 기존 75–120과 Reviewer 90–145는 전체 구현의 불확실한 판단 범위로 남기며, 현재 결정은 측정 가능한 초기 묶음에 한정한다.
