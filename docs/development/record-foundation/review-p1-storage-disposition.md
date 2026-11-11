# P1 저장·복구 리뷰 처분

2026-11-07. Reviewer Claude Opus 5.5, Driver Codex. [리뷰 원문](review-p1-storage.md)은 새 CLI 세션의 도구 없는 정적 검토다. 첫 180초 호출은 응답 없이 시간 종료됐다. Owner가 추가 1회와 시간 확대를 승인한 뒤 360초 상한으로 핵심 파일 7개를 전달했고 133초에 종료했다. 입력 drift는 없었다. 이 검토는 재현이나 Owner 수락이 아니다. 원 패킷·실패·응답·session 식별값은 기존 비공개 근거에 보존한다.

| 지적 | Driver 처분·검사 |
| --- | --- |
| 1. 세대 교체 시 완료 이력 누락 | 채택. 같은 instance의 v1 세대 교체는 canonical root 전체가 같아야 한다. operation 키만 보존하고 다른 head를 잃는 전환도 허용하지 않는다. 새 store 초기화는 갱신이 아니다. 별도 instance로 복원하는 P7 경로와 구분한다. 빈 후보로 완료 이력을 잃는 반례를 재현했고 보정 후 거부한다. 기록을 보존한 후보의 전환·완료 조회·중복 실행 거부도 통과했다. |
| 2. 검증 중 읽은 head 변경 | 채택. 검증은 고정 root에서 읽고 읽은 head 집합을 최종 CAS에 포함한다. 전체 root를 읽으면 root도 비교한다. 같은 inode의 공개 head/root 조회를 검증 context에 연결한다. 변경된 의존성 거부와 무관한 head 병합을 각각 시험했다. 검증기는 동기 호출이며 SQL 직접 읽기·별도 thread 검증은 application 계약 밖이다. |
| 3. 파생 operation 인덱스 | 채택. 자기 설명만으로 같은 sequence의 다른 branch root를 고르는 반례를 고정했다. 저장된 root 계보와 대조하고 각 조회는 짧은 transaction으로 수행한다. 긴 이력은 명시적 resource bound 초과 시 unavailable이며 일반 Work 조회에 전체 계보 탐색을 넣지 않는다. |
| 4. lifecycle hot journal 복구 | 채택. 정확한 pending plan과 lifecycle 잠금 아래에서만 기록된 양쪽 DB를 SQLite가 복구하게 하고 읽기 전용으로 다시 판정한다. retired writable handle은 노출하지 않는다. 실제 별도 process를 중단해 두 세대에 hot journal을 만든 뒤 복구·본문/root 보존·integrity를 확인했다. 전원 장애 qualification은 아니다. |
| 5. hot journal 오류 분류 | 채택. 파일 존재 추정 대신 SQLite 확장 코드 READONLY_ROLLBACK/DBMOVED를 구분한다. 합성 오류 분류와 실제 killed-writer 사례를 검사했다. |
| 6. COMMIT busy의 불명 오분류 | 채택. busy 뒤 열린 transaction의 rollback 성공이 확인된 때만 미커밋 busy로 처리한다. 그 외 불명 효과는 유지한다. 경과 한도 뒤 최소 대기시간을 더하지 않고 즉시 busy로 끝낸다. 실제 SHARED lock으로 거부와 행 미생성을 확인했다. |

리뷰 반례 시험은 보정 전에 6건 실패·1건 통과했다. 보정 후 추가 lifecycle/완료 이력 시험을 포함한 foundation 95건이 일반·최적화 실행에서 각각 통과했다. 기존 제품 전체, 실제 설치본, Windows primitive, 전원 차단, 호스트 격리 통과를 뜻하지 않는다. P1의 API를 P2/P3에 연결하고 통합 리뷰에서 변경분을 다시 다룬다.
