# P1 정적 리뷰: storage 게시와 세대 복구

**STATIC, not reproduced.** 제공된 소스만 읽고 판단했습니다. 실행, 재현, 전원 차단이나 플랫폼 검증은 하지 않았습니다.

**문제를 찾지 못한 부분:**
- 같은 head CAS가 최종 쓰기 잠금 안에서 다시 확인됩니다.
- `quiesce`, `retire`, 포인터 교체, `cancel_quiescence`, `pending` 제거가 이 순서로 진행됩니다.
- 펜스는 SQL 트리거로 되돌릴 수 없습니다.
- 포인터는 임시 파일 fsync, `os.replace`, 디렉터리 fsync 순서로 교체됩니다.

---

### 1. [High] 세대가 바뀌면 같은 작업이 다시 적용될 수 있음
**함수:** `Authority.activate` / `Authority._finish`, `GenerationStore.operation_result` / `commit_heads`

**실패 순서:**
1. 클라이언트가 g1에 `commit_heads(operation='X')`를 보냅니다. 커밋은 됐지만 `store-outcome-unknown`을 받습니다.
2. 운영자가 g2로 전환합니다. g2는 `prepare_empty`로 만들었거나, 작업 맵을 옮기지 않은 채 채워졌습니다. `validate_target`은 호출자 콜백이라 이 점을 보장하지 않습니다.
3. 클라이언트가 새 활성 저장소에서 `operation_result('X')`를 호출하면 `None`이 반환됩니다. 옛 g1은 `generation-retired` 때문에 조회할 수 없습니다.
4. 클라이언트가 X를 다시 커밋하고, 결정이 두 번 적용됩니다.

**최소 수정:** `activate`와 `recover`의 봉인(`_seal_target`) 전에 래퍼가 직접 검사해야 합니다. 대상 루트의 작업 맵 키가 `old_root`의 작업 맵 키를 모두 포함하는지 확인합니다. 아니면 대상 루트에 원본 루트 계보를 기록하고, `operation_result`와 `commit_heads`가 그 계보까지 조회하게 합니다. 이 검사를 `validate_target`에 맡기면 안 됩니다.

### 2. [Medium] 검증기가 읽은 head는 CAS로 보호되지 않음
**함수:** `GenerationStore.commit_heads`

**실패 순서:**
1. 검증기 A가 잠금 밖에서 `store.head('k')`를 읽고, 그 값을 근거로 변경이 유효하다고 판단합니다. 키 `k`는 `expected`에 넣지 않았습니다.
2. 다른 작업 B가 `k`를 바꿉니다.
3. A의 최종 트랜잭션은 `expected` 키만 다시 확인하므로 커밋에 성공합니다.

결과적으로 낡은 의존성 위에 결정이 게시됩니다. docstring은 "changed shared dependency 거부"를 약속하지만, 실제로는 `expected`에 넣은 키만 보호됩니다.

**최소 수정:** `validate`에 고정된 루트 스냅샷과 head 읽기 함수를 함께 넘깁니다. 검증기가 읽은 키를 래퍼가 기록하고, 최종 잠금 안에서 그 키들도 `expected`처럼 다시 비교합니다. 더 간단하게는 "검증에 쓴 루트와 `old.ref`가 같아야 함"을 선택 옵션으로 둡니다.

### 3. [Medium] `operation_result`가 SQL 투영의 `after_root`를 계보 확인 없이 믿음
**함수:** `GenerationStore.operation_result`

**실패 순서:**
1. 작업 맵에는 `X → before`가 있습니다.
2. 오염되었거나 남아 있던 `operations` 행이 이미 게시된 다른 루트 객체를 가리킵니다. 그 객체의 payload에는 `operation=X`, `previous=before`가 들어 있습니다.
3. 이 값은 객체의 자기 서술만으로 통과해 결과로 반환됩니다. 현재 루트의 계보에 속하는지는 확인하지 않습니다.

모듈 머리말의 "SQL projection을 검증된 root/map 대신 받지 않음"이라는 원칙에 어긋납니다.

**최소 수정:** 현재 루트에서 `previous` 링크를 따라 `before.sequence + 1`까지 내려갑니다. 그 지점의 루트가 SQL 행의 `after_root`와 같은지 확인합니다. 탐색 길이는 시퀀스 차이로 제한합니다.

### 4. [Medium] 복구 경로가 핫 저널을 스스로 롤백하지 못함
**함수:** `Authority.recover`, `Authority._finish`

**실패 순서:**
1. `source.retire`의 COMMIT 도중 크래시가 나서 g1에 핫 저널이 남습니다.
2. `recover()`는 맨 처음 `_open_recorded(old, readonly=True, retired=True)`로 g1을 엽니다. 결과는 `recovery-required`입니다.
3. 복구 경로에는 쓰기 가능한 열기가 없습니다(`retired-read-only` 제약). 그래서 다시 시도해도 계속 실패합니다.
4. 결국 lifecycle 잠금 밖에서 일반 클라이언트가 `authority.store()`로 쓰기 가능하게 열 때에만 롤백이 일어납니다. 대상 g2의 봉인 커밋 중 크래시가 난 경우도 같습니다.

**최소 수정:** lifecycle 잠금 안에서 `recovery-required`가 나오면, 펜스를 요구하지 않는 쓰기 가능 열기로 저널을 롤백합니다. 열기 직후 `_guard`가 거부해도 롤백은 이미 끝난 상태입니다. 그다음 읽기 전용으로 다시 열어 상태를 판정합니다.

### 5. [Low] 핫 저널 판정이 저널 파일 존재 여부에만 기댐
**함수:** `_sql_error`

**실패 순서:**
- 모든 `SQLITE_READONLY*` 오류가 `-journal` 경로가 있기만 하면 `recovery-required`로 분류됩니다. 존재 여부는 잠금 밖에서, 심볼릭 링크를 따라가며 확인됩니다.
- 그래서 핫 저널이 아닌 파일이나 경합 중에 생긴 파일이 오분류될 수 있습니다.
- `SQLITE_READONLY_DBMOVED`(파일 교체)도 같은 식으로 섞입니다.

**최소 수정:** 확장 오류 이름이 정확히 `SQLITE_READONLY_ROLLBACK`일 때만 `recovery-required`로 분류합니다. `SQLITE_READONLY_DBMOVED`는 `store-file-replaced`로 보냅니다. 나머지는 `store-io-unavailable`로 둡니다.

### 6. [Low] 커밋되지 않은 BUSY가 "결과 불명"으로 보고됨
**함수:** `GenerationStore._transaction`

**실패 순서:**
1. 프로세스 잠금을 기다리느라 시간이 지나 `busy_timeout`이 0 근처로 설정됩니다.
2. 다른 프로세스의 읽기 연결이 SHARED 잠금을 잡고 있어 COMMIT이 `SQLITE_BUSY`를 반환합니다. 이때 트랜잭션은 열린 채로 남아 있어 실제로 커밋되지 않았습니다.
3. ROLLBACK은 성공하지만, `committing=True` 때문에 `store-outcome-unknown`이 보고됩니다.

결과 불명 응답이 불필요하게 늘고, 클라이언트는 1번의 재적용 위험이 있는 확인 경로를 더 자주 타게 됩니다.

**최소 수정:** COMMIT에서 BUSY 계열 오류가 났고 ROLLBACK이 성공했다면 `store-busy`(커밋 안 됨)로 보고합니다. 또 `busy_timeout`에 최소 하한을 둡니다.

---

이번 리뷰는 SQL과 세대 경계에만 한정됩니다. 다른 모듈, P2/P3 검증, 실제 전원 차단·macOS·Windows 검증을 대신하지 않습니다.
