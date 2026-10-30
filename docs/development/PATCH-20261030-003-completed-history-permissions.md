# Completed History Permission Compatibility

현재 상태: Owner 결과 수락 및 source 작업 Done. [수락 범위와 후속 경계](#owner-result-acceptance-and-source-completion--2026-10-30)를 따른다.

## Approved Scope

2026-10-30 Owner가 완료된 실행 journal의 판독 보정과 관련 회귀 보강을 선택하고, 이번 작업에 한정한 전체 회귀 미재실행 예외를 승인했다. 시작 기준은 main `78d2a49c0dbd26b1cd908f4fc10fbe52e125a519`다. 예상 60–90분, 누적 중단 120분에는 구현·집중 normal/parent-O 검사·정적 R0/R1·문서·마무리가 포함된다. 사람의 승인 대기는 제외한다. 신규 작업은 110분에서 멈추고 종료 기록에 10분을 남긴다. Git commit/통합, 실제 도입 프로젝트 설치, 모델 실행, 다른 경로 clone 지원, Windows qualification은 제외한다.

이 작업은 기존 First B1 보정 원칙을 journal에 적용한다. 종료 상태 의미와 canonical JSON/hash chain은 바꾸지 않는다. 종료 후보를 읽기 전용으로 관측하고 기존 상태기로 검증한 뒤 정확한 0600/0644를 허용한다. 종료 결과에는 append 가능한 journal 객체가 없다. live 기록은 기존 private-mode 판정과 EffectJournal을 유지한다. 생성/append/global checked_open은 바꾸지 않는다. 자동 chmod, 새 기록/schema, 경로 재결속은 없다.

## Completion Criteria And Evidence Selection

- 기존 terminal 종류, 0600/0644 허용, 내용·mode·mtime 불변, closed callback/append authority 부재.
- live/unknown/incomplete 0644 거절과 기존 private 판정 유지. type/owner/link/alias/관측 drift, 비표준 종료 mode, 손상/부분/잘못된 terminal 거절.
- 합성 Git checkout/복귀 및 FF를 umask022/077에서 실행하고 installed status/view, 실행 기록과 완료 Work를 검사한다. 종료코드만 성공 근거로 쓰지 않는다.
- official execution/guard 소비 경로와 새 회귀를 normal/parent-O로 실행한다. exact 후보의 update/rollback, repair/detach는 기존 transition05/07/08을 선택한다.
- 기존 guard 집중 검사와 lifecycle 근거는 비교·선택 근거로 재사용한다. 변경 경로의 PASS를 이전하지 않는다. 변하지 않은 RPC/model/platform에 대한 기존 결과는 원 한계 안에서만 유지한다. 기존 전체 회귀 실패와 Windows 제외는 해소되었다고 하지 않는다.
- 전체 재실행 예외는 이 보정에만 적용된다. 새 공유상태·기록 의미·동시성 변경이 필요하면 확대 없이 중단한다.

## R0 Review

Driver Codex, Reviewer Claude (`claude-opus-5-5`), Owner 인간의 역할을 구분한다. fresh session `3beb5c2a-be89-45c5-806c-4d3bdbabb2a5`, 도구 없는 고정 packet 정적 리뷰, 106.14초. 실행/재현 근거가 아니다. Reviewer의 수락 표현은 Owner 수락이 아니다. 아래 응답은 원문이다.

# R0 정적 검토: 완료 이력 판독 권한 보정 최소 설계

## 판정

**조건부 승인입니다. blocking 결함은 없습니다.**

제안 구조는 이전 B1 원칙과 일치합니다. 구조는 rows를 먼저 관측하고, 기존 상태기로 종결을 판정한 뒤, mode를 결정합니다. 종결된 경우 append 가능한 객체를 반환하지 않고, 미종결이면 `0600` 상태에서 기존 `EffectJournal`의 rows와 대조합니다. 이 구조에서 `0644` 관측은 권한으로 승격되지 않습니다.

- `ClosedHost`는 `status`/`head`만 소비합니다.
- `resolve`는 `resolution_preview`가 비종결을 강제한 뒤에만 `value['journal']`을 사용합니다. 따라서 `journal=None`이 append 경로로 새지 않습니다.
- `Host.finish`/`fail`은 자기 `self.journal`만 append합니다.

아래 Medium 1건은 구현 전에 결정을 기록해야 하지만, 설계를 바꿀 필요는 없습니다.

## Findings

### M1. 정확 mode 집합이 기존 허용 범위보다 좁아짐 (Medium, 결정 기록 필요)

**위치**
- `src/hv2ref/official_documents.py`: `checked_open`의 `S_IMODE & 0o077`
- 신규 observer
- `src/hv2ref/official_state.py`: `read_capsule`

**문제**
- 기존 `checked_open`은 `0400`, `0700`, `04600`과 소유자 불일치도 통과시켰습니다. 신규 observer는 정확히 `{0600, 0644}`만 허용하고 owner도 검사합니다. 그 결과 두 가지가 바뀝니다.
- **종결 이력:** 기존에 읽히던 `0400`/`0700` 이력이 새로 거절됩니다. 그러면 `capsules()`가 실패하고, 이어서 `require_no_open`/`execution_truth`가 프로젝트 전체를 막습니다.
- **미종결 capsule:** `0700`이면 판독은 거절되지만 append(`checked_open`)는 여전히 허용합니다. 이 비대칭 때문에 해당 capsule은 `resolve`로 해소할 수 없는 고착 상태가 됩니다.

**요구사항**
- 이 강화가 의도된 것인지 계획에 명시해 주세요.
- regression 3번에 `0400`/`0700` 종결 이력 거절을 기대값으로 고정해 주세요.
- 완료보고 한계에 "기존에 허용되던 비표준 private mode 이력이 이제 거절된다"를 적어 주세요.
- 미종결 경로는 둘 중 하나를 택해 결정을 기록해 주세요.
  - 기존 `checked_open` 의미로 판독 gate를 맞춘다(종결만 정확 집합 적용).
  - 고착 가능성을 한계로 수용한다.

### L1. 노출되지 않은 consumer의 0644 경로 (Low, 범위 규칙으로 처리 가능)

**위치:** `product.status`, workspace guard, lifecycle/detach, installed "current files match" 경로. 모두 이번 발췌에 없습니다.

**문제:** 이 경로들이 checkout된 다른 파일(receipt, worker 산출물, 문서 파일)에 `checked_open`/`control_read`를 쓰면, journal을 보정해도 installed 검사가 실패합니다.

**요구사항:** 설치 검사 4번이 이를 드러내도록 되어 있으므로 blocking은 아닙니다. 다만 발견 시 기존 계획대로 중단하고 재산정해야 하며, 판독 보정을 다른 파일로 몰래 확장하면 안 됩니다.

### L2. 미종결 경로의 path 재결속 (Low)

**위치:** `read_capsule`의 비종결 분기

**문제:** `EffectJournal`은 path로 다시 엽니다. rows 동등성 검사는 내용 변경을 잡지만, 같은 내용의 다른 inode로 교체된 경우는 잡지 못합니다. 기존 append의 path 기반 재검증과 같은 수준이고 `resolve`는 `writer_guard` 아래에서 실행되므로 새 위험은 아닙니다.

**선택 사항:** 관측 identity(dev/ino)를 `EffectJournal` 생성 직후 `lstat`과 대조하면 비용 없이 닫을 수 있습니다.

### L3. 미종결 0644 거절의 오류 계약 (Low)

**문제:** 기존에는 `checked_open`의 `HostRefusal`로 거절했습니다. 신규 observer나 상태 분기가 `ContractError`를 던지면 status/guard의 오류 매핑이 달라질 수 있습니다.

**요구사항:** 테스트 2번에서 예외 class와 code를 정확히 assert해 주세요. 통과 기준이 "어떤 예외든 발생"이어서는 안 됩니다.

### L4. 파서 분리 시 동일성 (Low)

**위치:** `official_documents.py`의 `EffectJournal.read`

**문제:** 발췌본에는 `threading` import와 `reject_duplicate_keys` 정의가 없습니다. 발췌 과정의 누락으로 보이지만 확인할 수 없습니다.

**요구사항:** module-level 파서가 다음을 그대로 유지하고, `read()`가 `parse(control_read(...))`의 순수 위임이 되도록 해 주세요.
- duplicate-key 거절
- 16MiB 상한, 후행 개행 검사, 8192행 제한
- 거절 code

### L5. 상태기의 비계약 예외 (Low, 기존 동작)

**문제:** 형식이 잘못된 `value`(dict가 아니거나 hash 불가능한 `status`)는 `TypeError`/`KeyError`로 실패합니다. fail-closed이므로 안전하지만, 이제 `0644` 수락이 이 상태기에 의존합니다.

**요구사항:** "잘못된 종결" 테스트는 이 경로에서 거절과 비수락만 assert하고, 특정 code를 요구하지 마세요.

### L6. Git과 빈 디렉터리 (Info)

**문제:** Git은 빈 디렉터리를 추적하지 않으므로, 비어 있던 `workers/`나 `scratch/`는 checkout 후 복원되지 않습니다. 발췌의 `execution_truth`는 파일만 inventory하므로 영향이 없습니다.

**요구사항:** 설치 검사에서 기록된 inventory 일치를 assert할 때 이 차이가 숨겨지지 않는지 확인해 주세요.

## 범위 판단

- 다른 경로 clone의 `grant-target` 거절 유지, 전체 회귀 미재실행, 120분 상한은 Owner 승인 범위 안에 있습니다. 이 정적 검토에서 집중 검사로 한정할 수 없는 새 공유상태, 기록 의미, 동시성 위험은 발견하지 못했습니다.
- 같은 결과로, 전체 suite나 clone 재설계를 요구할 구체적 근거도 없습니다.

## 한계

- 실행, 도구 사용, 테스트는 하지 않은 정적 검토입니다. 구현 코드가 아직 없으므로 제안 문장과 발췌만 대상으로 했습니다.
- 다음 경로는 보지 못했으며, "All consumers checked"를 독립적으로 검증하지 못했습니다.
  - `official_os`(`create_journal`/`append_journal`)
  - `product.status`, `workspace.writer_guard`, lifecycle/detach, `official_entry`
- macOS의 Git checkout/FF 동작, umask 결과, ctime 관측 특성, 측정 시간과 Test ID 선택은 검증하지 않았습니다.

## Driver R0 Disposition

- M1 revise: 종료 이력의 0400/0700/특수 mode 거절은 이번 정확한 allowlist의 의도된 범위다. live 관측은 기존 private mask 판정을 유지하고 EffectJournal의 기존 검사를 다시 적용한다. 비표준 private live 기록의 해소를 이 보정 때문에 막지 않는다. owner/single-link 안전 검사는 관측에 적용한다.
- L1 accept: installed status/view/Work와 guard/lifecycle 검사를 수행하며 다른 파일의 완화는 하지 않는다.
- L2 accept: live 객체 생성 후 관측 identity까지 대조한다.
- L3 accept: live0644는 기존 HostRefusal과 이유를 유지하고 정확히 검사한다.
- L4 accept: 기존 parser를 그대로 공통 함수로 추출하고 크기·canonical·duplicate·행 제한을 검사한다.
- L5 accept: 잘못된 terminal은 비수락을 검사하되 기존 비계약 예외를 이번에 재설계하지 않는다.
- L6 accept: Git의 빈 디렉터리 비보존을 고려해 파일 내용과 typed 상태를 검사한다.

## Current Disposition

구현/검증 진행 중. R1과 Owner 결과 수락은 아직 없다. 결과·권한은 자동 수락하지 않는다. 새 source record 한 개가 진행을 소유하며 Development Index에는 링크만 추가한다. task 산출물·오류·검사 결과는 리뷰와 Owner 결과 처분에 필요해 보존하고 그 처분 후 재평가한다.


## R1 Review And Driver Disposition

R1은 같은 Claude 구독 경로의 fresh session `c821e29d-e256-4884-9f8f-06cbbd3799f7`, 모델 `claude-opus-5-5`로 수행했다. 도구 없는 정적 리뷰 208.85초이며 Reviewer가 검사를 재현한 결과가 아니다. 전달한 소스·packet은 리뷰 전후 불변이었다. 아래는 원문이다.

# R1 정적 리뷰: 터미널 저널 권한 수정 (PATCH-20261030-003 후보)

**근거 구분**
- **[정적]**: 제공된 diff와 최종 소스를 직접 읽고 판단한 내용입니다. 저는 아무것도 실행하지 않았습니다.
- **[실행-보고]**: 패킷의 EXECUTED EVIDENCE에 적힌 결과입니다. 제가 재현하지 않았고, 보고된 그대로 해석만 했습니다.

## 요약

- **[정적] 차단 수준(High/Medium) 문제는 없습니다.** Owner가 승인한 범위(터미널 0600/0644만 허용, 미해결 상태는 기존 private gate 유지, chmod·schema 변경 없음) 안에서 구현과 R0 M1 처리가 서로 맞습니다.
- 아래 Low 항목들은 문서 정확성, 증거 강도, 확인 공백에 관한 것입니다.
- **이 판정은 Owner acceptance가 아닙니다.**

---

## 정적으로 확인한 정합성 (문제 없음)

1. **`observe_journal`** (`src/hv2ref/official_documents.py:574-593`)
   - lstat로 다음을 확인합니다: 일반 파일, 소유자 uid, nlink==1, `mode == 0o644 or not mode & 0o077`.
   - 그 뒤 `O_NOFOLLOW|O_NONBLOCK`로 열고, fstat로 식별값(dev/ino/mode/uid/nlink/size/mtime/ctime)을 비교합니다. 읽은 뒤에는 fstat, lstat, `resolve`를 다시 확인합니다.
   - 열기 직전에 FIFO나 다른 파일로 바뀌어도 블로킹 없이 drift로 거절됩니다. 같은 바이트로 교체해도 inode가 달라 거절됩니다.
   - 기존 `checked_open`(open 후 fstat)보다 약하지 않습니다.
2. **special bit 처리**: `S_IMODE`는 setuid 계열 비트를 포함합니다.
   - `0o4644`는 관측 단계에서 거절됩니다(`0o4644 != 0o644`이고 `& 0o077 ≠ 0`).
   - `0o4600`은 관측은 통과하지만 터미널 판정에서 `closed-journal-mode`로 거절됩니다(`official_state.py:188`).
   - 비터미널 `0o4600`은 기존 live mask대로 허용됩니다. R0 처리와 같습니다.
3. **`read_capsule` 분기** (`official_state.py:186-194`)
   - `'unknown'`은 `TERMINAL`에 속하지 않으므로 live 경로로 갑니다. 그래서 0644이면 기존과 같은 `HostRefusal('aliased or nonprivate control file')`이 납니다.
   - live 경로는 `EffectJournal`을 만든 뒤 rows가 같은지와 lstat 식별값이 같은지 다시 확인합니다. 이 검사는 `test_live_identity_is_rechecked_after_private_journal_construction`가 덮습니다.
4. **터미널 상태의 `journal=None`**
   - `cancel`은 `execution-already-terminal`, `resolution_preview`는 `resolution-requires-unresolved-state`로 먼저 막히므로 append 경로에 닿지 않습니다.
   - `ClosedHost`는 `read_capsule`만 사용합니다.
   - `execution_truth`는 `root`만 쓰고 sha256만 기록하므로 mode 변경이 truth에 영향을 주지 않습니다. 그래서 transition 07/08에서 chmod 0644를 해도 `before`/after 비교가 유효합니다.
5. **`writer_guard`**: `require_no_open`이 `read_capsule`의 status만 보므로, 터미널 0644는 guard를 풀어 주고 미해결 0644는 계속 막습니다. 의도한 동작입니다.
6. **parser 추출**: `journal_rows`는 기존 `EffectJournal.read` 본문과 같고, `append`와 `checked_open`은 바뀌지 않았습니다. 패킷의 static 비교 결과와도 일치합니다.

---

## Findings

### L1 (Low, 문서 정확성): checkout 결과 mode가 umask에 따라 달라진다는 점이 빠짐
- 위치: `docs/OFFICIAL-EXECUTION.md:89` "including when Git checkout recreates it"
- **[정적]** Git은 100644만 기록합니다. 따라서 checkout으로 생기는 mode는 umask에 따라 결정됩니다.
  - umask 022 → 0644
  - umask 077 → 0600
  - umask 002 → **0664**
  - umask 027 → **0640**
- 뒤의 두 경우는 `closed-journal-mode`로 거절되고, status는 unavailable, 모든 writer가 차단됩니다.
- fail-closed이므로 안전 문제는 아닙니다. 하지만 문서는 checkout으로 생긴 history 전반이 허용되는 것처럼 읽힙니다. 테스트도 022와 077만 덮습니다.
- 권고: "0600/0644가 생기는 umask(예: 022/077)에서만 허용되고, 그 밖의 결과(0664/0640 등)는 계속 거절된다"고 한 줄 추가하십시오. 코드 변경은 필요 없습니다.

### L2 (Low, 증거 강도): special-mode fixture 테스트가 거절 사유를 확인하지 않음
- 위치: `tests/test_official_history_permissions.py` `test_actual_special_mode_terminal_files_are_refused`
- **[정적]** `assertRaises((HostRefusal, ContractError))`만 검사하고, 같은 fixture가 정상 mode에서 통과하는지 보는 positive control도 없습니다.
- 이 fixture는 샌드박스 밖에서 준비됐습니다. 만약 `grant.json`의 `spec.target`이 현재 경로와 다르면 `grant-target` 같은 다른 이유로 거절되어도 테스트가 PASS합니다. 즉 R0 M1(special bit 거절)의 실행 증거가 공허할 수 있습니다.
- 위 정적 항목 2에서 보듯 코드 자체는 두 mode를 올바르게 거절합니다. 그래서 이것은 결함이 아니라 증거의 품질 문제입니다.
- 권고(선택): 사유를 단언하십시오. `0o4644`는 `'unsafe journal observation'`, `0o4600`은 `'closed-journal-mode'`입니다.

### L3 (Low, 확인 공백): `value['journal']`이 None이 된 데 따른 소비자 전수 확인 근거 없음
- 위치: `official_state.py:186`, 반환 dict의 `'journal'`
- **[정적]** 터미널 capsule에서 반환값이 `EffectJournal`에서 `None`으로 바뀐 것은 API 변경입니다. 제공된 소비자(`official_host.py`, `product.py`, `workspace.py`, `official_state.resolve`)에는 문제가 없습니다.
- 하지만 `official_entry.py` 등 제공되지 않은 모듈에 `capsule['journal'].rows` 같은 사용처가 있는지는 정적으로 확인할 수 없습니다.
- **[실행-보고]** official_execution 51건과 guard_history 5건이 PASS했으므로 간접 증거는 됩니다. 다만 전수 증거는 아닙니다.
- 권고: `src/`에서 `['journal']` / `.get('journal')` / `"journal"` grep 결과를 증거로 첨부하십시오. 결과가 0건이거나 비터미널 경로만이면 종결됩니다.

### L4 (Low, 정보성·기존 문제 완화): `resolve()`가 두 번째 `read_capsule` 결과를 다시 검증하지 않음
- 위치: `official_state.py` `resolve()`의 `value['journal'].append(...)`
- **[정적]** 두 시점의 결과를 맞춰 보지 않습니다.
  - `resolution_preview` 시점과 두 번째 `read_capsule` 사이에 head나 status가 바뀌는지 직접 확인하지 않습니다. 이 TOCTOU는 기존부터 있던 것입니다.
  - 이번 변경 후에는 그 사이 terminal이 되면 `AttributeError`가 나며 fail-closed됩니다. 이전에는 이 경우 무효한 row를 append해 history를 오염시킬 수 있었으므로, 오히려 개선입니다.
- 이번 범위의 차단 사유는 아닙니다. 다만 오류 타입이 `ContractError`가 아닙니다.
- 권고(선택, 후속): `need(value['journal'] is not None and value['head'] == observed['observation']['journal_head'], 'stale-resolution-confirmation')`

### L5 (Low, 호환성 고지): 기존 터미널 0400/0700/04600 history가 workspace 전체 writer를 막게 됨
- 위치: `official_state.py:188`, 문서 `:91`
- **[정적]** 이전에는 private mask로 허용되던 터미널 저널(예: 보관 목적으로 수동 chmod 0400한 경우)이 이제 `closed-journal-mode`로 거절됩니다. 그 결과 `require_no_open`을 거치는 모든 ordinary writer가 차단됩니다.
- Owner가 승인했고 문서에도 있는 동작 변경입니다. 다만 영향이 workspace 단위의 쓰기 차단이라는 점은 문서에 명시되어 있지 않습니다.
- 권고: 문서에 "해당 history가 있으면 ordinary write도 차단된다"를 한 구절 추가하십시오.

### Nit
- `docs/OFFICIAL-EXECUTION.md:85-91`
  - 기존 문서는 한국어인데 새 절은 영어입니다. 빈 줄도 2개 들어가 있습니다.
  - 또 checkout(umask 022)은 journal뿐 아니라 capsule 디렉터리(0755)와 `grant.json` 등도 다른 사용자가 읽을 수 있게 만듭니다. 그런데 기밀성 고지는 journal만 언급합니다.
- `test_grant_digest_and_target_mismatch_remain_refused`: 실제로는 digest 검사(`grant-record`)만 확인합니다. `grant-target` 경로는 transition 05의 clone 단언이 덮습니다. 테스트 이름이 실제 범위보다 넓습니다.
- transition 07/08 subTest는 이제 항상 0644로 바꿉니다. 그래서 같은 경로의 0600 변형은 이 테스트에서 빠지고, `test_detach_preserves_execution_capsule` 등 다른 테스트에만 의존합니다.

### 조건부 참고 (요구사항 아님)
- update/rollback 경로에는 0644 터미널 저널을 쓰는 변형이 없습니다. diff는 07(repair)와 08(detach)에만 chmod를 추가했습니다.
- rollback 이후 predecessor reader가 0644를 거절하는 것은 수정 전과 같은 상태이고, 문서에도 고지되어 있습니다.
- **다만** rollback 트랜잭션 내부 검증이 predecessor reader를 호출한다면 상황이 다릅니다. 트랜잭션 도중 실패해 상태가 부분적으로 남을 위험이 있으므로, 그런 구조인지 한 번 확인하십시오. 그렇지 않다면 추가 실행은 필요 없습니다.

---

## 실행 증거 해석 [실행-보고, 미재현]

- **normal 70건 PASS는 단일 실행이 아니라 여러 실행을 합친 결과입니다.**
  - `history-normal-01`(전체 결과는 실패)의 unit 10건
  - `checkout-normal-03`의 2건
  - `focused-normal-04`의 58건
  - 따라서 unit 10건의 normal 증거는 fixture를 고치기 전의 테스트 파일 리비전에서 나온 것입니다.
  - 최종 파일 전체 70건은 `focused-optimized-01` 단일 실행에서 PASS했습니다. 이 테스트들은 `assert`가 아니라 `require`/unittest 단언을 쓰므로 `-O`로 인해 검사가 빠지지 않습니다.
- 초기 실패 2건, NameError 2건과 그 원인(fixture 순서와 import)은 보존되어 있습니다. 제품 소스가 바뀌지 않았다는 점(`source_unchanged`)은 보고와 일치합니다.
- transition 05/07/08은 normal과 parent-O 모두 3/3 PASS입니다.
- 범위 밖으로 유지되는 것:
  - full suite와 Windows: `full_suite_claim: false`
  - 실제 모델이나 새 adopter 실행
  - 합성 Work/callback 데이터는 모델 실행 증거가 되지 않습니다.

---

## 판정 (R1 정적)

- **차단 사유 없음.** 안전성과 정확성 면에서 수용 가능한 상태로 판단합니다.
- L1과 L5(문서 한 줄씩), L3(grep 증거)은 Owner 결정 전에 반영하기를 권합니다.
- L2와 L4는 선택 사항입니다.
- 이 판정은 Owner acceptance를 대신하지 않습니다.

### Driver Disposition

- L1/L5/Nit revise: 사용문서의 새 절을 주변 한국어에 맞추고, umask022/077만 실행 검증했으며 다른 mode는 거절·workspace 쓰기 차단으로 이어짐을 명시했다. capsule의 다른 파일·디렉터리도 기밀성을 보장하지 않는다는 설명을 보완했다. 실행 코드 변경은 없다.
- L2 revise: 실제4600/4644 fixture의 거절 예외와 이유를 각각 closed-journal-mode, unsafe journal observation으로 고정했다. target/digest 오류로 공허하게 통과할 수 없게 하고 이 한 검사만 두 모드로 다시 실행한다.
- L3 accept: src 전체의 journal subscript/get AST 검색과 journal 문자열 검색에서 반환 journal의 사용은 official_state.resolve 한 곳이다. official_entry는 상태·cancel·resolve를 위임하고 반환 journal을 직접 쓰지 않는다. Host/adapter의 journal 속성은 살아 있는 Host가 보유한 별도 객체다.
- L4 defend/defer: 기존 resolve의 두 관측 사이 변경은 정적 후속 관찰이며 이번에 재현하지 않았다. 이번 보정은 terminal의 append 객체 제거로 fail-closed한다. 새 동시성 변경은 추가하지 않는다.
- Nit test name: grant digest 검사는 해당 코드만 검사하며 grant-target의 별도 실행 증거는 transition05 clone 거절이다. 명칭 때문에 별도 PASS를 주장하지 않는다. 기존600 detach/other consumers의 결과와 새644 repair/detach 결과를 구분한다.
- 조건부 rollback 참고 accept: 현재 실행 중인 source의 workspace_switch_apply/체크포인트와 _lifecycle_truth가 검증한다. verify_workspace_release는 retained inventory/bytes를 읽고 이전 payload reader를 실행하지 않는다. 이전 reader 호출에 의한 트랜잭션 중도 실패는 이 정적 경로에 없다. 644 rollback 자체를 추가 실행했다고 주장하지 않는다.

R1의 실행 코드 판정은 차단 지적 없음이다. 이후 변경은 위에서 제안한 문구·거절 사유 assertion·결과 기록뿐이다. 추가 Reviewer 호출이나 코드 변경은 없다. 사용문서 변경으로 managed identity가 바뀌므로 새 artifact의 inventory/소비 경로를 확인하며, 실행 코드 양 모드 근거와 이전 artifact의 양 모드 interruption 근거는 구분해 재사용한다. 전체 suite를 다시 돌리지 않는다.


## Implementation, Verification And Review Result

구현·승인된 집중 검증·R0/R1과 지적 처분을 완료했다. Owner 결과 수락 전이므로 Done으로 처리하지 않는다. 실행 코드는 journal 관측/공통 parser와 capsule 판독 두 파일만 바뀌었다. 종료 이력은 검증 뒤 0600/0644로 읽고, live private gate와 append·상태 전이는 유지한다. 같은 canonical target의 실제 Git checkout/FF와 완료 Work 판독을 확인했다. 결과는 전용 source branch에 미커밋 상태로 보존하며 Git 통합과 실제 프로젝트 설치는 수행하지 않았다.

| Evidence | Result And Boundary |
| --- | --- |
| 집중 normal | 고유70개 누적 PASS. 최초 run의10unit 중 특수-mode1개는 R1 후 정확한 거절 사유로 대체 검증; checkout2개 보정 후 PASS; 기존 소비경로56개와 새2개 PASS를 합산했다. 단일70개 실행이 아니다. |
| 집중 parent-O | 70개 단일 실행 PASS; R1 후 특수-mode1개(4600/4644 하위 사례)의 정확한 거절 사유를 추가 PASS했다. |
| code 후보 전환 | test_05/test_07/test_08 normal3/3, parent-O3/3 PASS. rollback/clone·repair·detach와 기존 interruption cases를 포함한다. |
| 최종 문서 후보 | 관리 파일44개 중 사용문서1개만 변경, 실행 bytes 모두 동일. 최종 exact artifact의 위3개 전환을 normal로 다시 PASS했다. parent-O·집중 실행 근거는 동일 실행 코드에서 재사용하며 문서 후보에서 새 전체 실행했다고 하지 않는다. |
| 초기 오류 | Git을 nonGit Work 뒤에 만든 fixture 순서 오류2건, 복사한 setup의 참조 오류2건을 보존했다. 영향 있는 fixture만 보정했고 제품 코드 추가 수정은 없었다. |
| 안전 경계 | credential-free/network-denied canary, 보호 sentinel 불변, 각 실행 source 불변·자연 종료·프로세스 그룹 부재 확인. timeout 재시도/상한 확장 없음. |
| 정적 확인 | 기존 canonical parser 본문·checked_open·append AST 동일. journal 반환값 소비는 resolve1곳. R0/R1 차단 지적0; Reviewer 실행/재현은 없음. |

최종 후보는 `6bf0d829b473c9f31f3d4be50a6a4ddb74ed5493b09fa86997b8651a41a501fc` (`official-execution-1`)다. 독립 R1은 실행 코드가 같은 이전 문구 후보 `85c1a1cbd9278aa804daf63ef96c29038054b2b4969d73a510e7778a0e242252`를 검토했으며, 이후 delta는 리뷰에서 제시한 문구·특수-mode assertion·본 기록뿐이다. 새 Reviewer round나 최종 문구에 대한 독립 재검토를 주장하지 않는다. 코드와 판정 경계는 그대로이며 추가 assertion 한 메서드만 바뀐 것을 AST로 대조했다.

현재 보수적 wall-clock 사용량은 41.04분/120분이다. 사람의 짧은 승인 대기까지 포함하고 병렬 실행은 한 번만 계산한 값이다. 문서 render·diff/공개 문구 검증과 최종 정리 시각은 private 결과 기록에서 확인한다. 추가 실행·시간 확장 권한은 만들지 않는다.

## Remaining Limits And Adopter Impact

전체 회귀와 Windows qualification을 수행하지 않았고, 이전 전체 실행의 알려진 실패·제외를 해결했다고 하지 않는다. 다른 경로 clone은 기존 grant-target 거절을 유지한다. 이전 exact reader는 새600 이력을 읽지만644에서는 unavailable/ready false이며, 이 거절을 호환성 PASS로 바꾸지 않는다. 비표준 종료 권한0400/0700/특수 mode와0640/0664도 거절하고 workspace 쓰기를 막는다. 기존 resolve 관측 사이 경합은 재현하지 않은 정적 후속 관찰로 남으며 이번에 동시성 동작을 변경하지 않았다.

같은 경로 checkout 뒤 완료 이력 판독을 위해 이 보정의 도입을 권고한다. 다만 알려진 실제 설치 상태는 이번에 다시 조회하지 않아 현재값으로 확정하지 않는다. 실제 도입은 Owner 결과 수락 뒤 정확한 대상·binding·후보·기록 권한과 이전 reader 호환성, 복구 경로를 확인해 별도 승인으로 진행한다. source 결과와 합성 검증은 실제 설치·모델 실행·일반 제품 지원의 증거가 아니다.

전용 source worktree는 고유한 미커밋 소스·검사·작업 기록과 후속 Owner/Git 판단에 필요해 유지한다. 최종 후보와 검증·리뷰·최초 오류 근거도 그 판단까지 유지하고 수락/보존 처분 후 재평가한다. 완료된 합성 실행 fixture·등록 worker worktree와 중복 초안은 조건 확인 후 정리한다. 실제 도입 프로젝트나 primary source checkout의 활성 경로는 바꾸지 않았다.


## Owner Result Acceptance And Source Completion — 2026-10-30

Owner가 2026-10-30 이 작업의 최종 결과를 명시적으로 수락하고 수락 기록 반영과 후속 Git·도입 순서/범위 정리를 요청했다. PATCH-20261030-003의 승인된 구현·집중 검증·리뷰 및 지적 처분을 수락된 결과로 기록하고 source 작업을 Done으로 종료한다. 앞의 진행 중·수락 대기 문구는 각 단계의 역사이며 현재 상태는 이 절을 따른다.

수락 대상은 main `78d2a49c0dbd26b1cd908f4fc10fbe52e125a519`에서 보정한 실행 코드2개·검사2개·사용문서1개와 작업 기록/인덱스다. 검증한 최종 artifact는 `6bf0d829b473c9f31f3d4be50a6a4ddb74ed5493b09fa86997b8651a41a501fc`, inventory는 `official-execution-1`이다. 이번 수락 기록과 인덱스 탐색 링크는 source-only 변경이며 관리 payload·검사 assertion·실행 코드를 바꾸지 않는다.

완료 기준은 위 Implementation, Verification And Review Result의 근거로 충족했다. normal70개는 누적 결과, parent-O70개는 단일 실행이며 특수 권한의 정확한 거절 사유는 두 모드에서 추가 확인했다. 같은 실행 코드의 전환3개씩과 최종 문서 후보 normal3개 결과를 구분한다. R0/R1은 정적 리뷰이며 차단 지적0이다. 최초 fixture 실패, 전체 회귀 미재실행 예외, Windows/다른 경로 clone/실제 모델 실행 미검증과 이전 reader의0644거절은 수락 후에도 남는다. 비표준 종료 권한 거절과 workspace 쓰기 차단도 유지한다.

Owner의 이번 수락은 source 결과에 한정한다. 커밋·push·PR·merge·실제 설치·public release를 승인한 것으로 해석하지 않는다. 후속 순서는 수락된7개 파일의 source commit → main PR 통합 → 정확한 후보의 도입 프로젝트 update preview·별도 승인·apply·검증이다. 도입 프로젝트의 Git 기록과 통합도 별도 범위다. 일반적인 적용 권고는 같은 canonical target에서 완료 실행 이력을 보유한 공식 실행 설치를 대상으로 하며, private 대상의 현재 설치 관측과 상세 적용 계획은 기존 private 운영 기록에 둔다.

인덱스의 이 작업 링크만 이 수락 절로 연결했다. 별도 STATUS/작업 registry·typed Work·새 기술 계약을 만들지 않았다. 전용 source checkout은 아직 고유한 미커밋7파일을 보유하며 예정된 커밋/통합의 입력이므로 유지한다. 검토 당시 후보와 최종 후보, 최초 실패 및 실행 근거는 수락 근거 재사용과 다음 정확한 도입 판단을 위해 유지하며 그 단계 종료 시 재평가한다. 이 기록 반영은 기존 실행 시간/재시도 권한을 연장하지 않는다.
