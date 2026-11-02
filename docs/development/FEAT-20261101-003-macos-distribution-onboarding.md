# macOS 배포·관리·온보딩 구현

상태: Done — Owner가 2026-11-02 승인된 macOS 구현·격리 검증·제한된 첫 작업 및 제출 후 재개 결과를 수락했다. bounded PASS의 합성 관측 한계와 공개 전 자격 조건은 유지한다. Driver Codex, Reviewer Claude, 결과 수락 Owner. 정본 진행은 이 Work가 소유한다. 이전 계획/R0는 [preliminary record](macos-onboarding-distribution-plan-review.md)에 보존한다.

## 현재 결과와 남은 조건 — 2026-11-02

| 범위 | 현재 결과 |
| --- | --- |
| 배포·관리 구현 | clone 없는 bootstrap, 고정 전용 Python, update·rollback·repair·detach·관리 명령 제거/복원, EN/KO 첫 작업·재개 안내를 구현했다. public build15를 유지하고 동일 제품 소스로 별도 저장소를 쓰는 build16 fixture를 검증했다. 공유 Python 자동 제거는 포함하지 않는다. |
| runtime·안내 | 기존3.14.6/3.14.7 목록과 managed macOS3.14.10 exact-tree 경로를 구분한다. 진입3문서3349tokens, CLAUDE projection 포함3500tokens·물리4reads. 조건부 OPERATIONS/adapter/manual/프로젝트 읽기와 실제 설치 경로 전체 비용은 별도다. |
| 격리 검증 | 기존 관리/복구·합성 품질·실제 signal·predecessor·build15 reader 근거를 재사용했다. 새 고정 store의 Python/bootstrap·프로젝트 연결13관측, 관찰기 집중25건, typed 첫 작업·새 세션 재개가 통과했다. public HTTPS transport와 실제 사용자 설치는 미실행이다. |
| 회귀검사 | 현재1401 ID에 mode별1301 PASS 근거·Windows100skip·잔여0을 연결한 기존 합성 근거를 재사용했다. 제품 소스가 이번 묶음에서 바뀌지 않았으므로 full run을 반복하지 않았다. current artifact의 새로운 full run은 아니다. |
| 정상 작업·행동 | B01 모델2턴이 계획·정확한 합성 승인·baseline·수정·검사·review 제출을 중간 대행 없이 완료했다. B02 새 세션1턴은 실제 Work/intent/PLAN/README/continuation을 읽고 수락 대기·계획의 과거 진행 문구·다음 결정과 이유를 구분했다. 두 합성 사례에서 도구 오거절·반복 승인·뜻밖의 중단0, B02 파일/모드 변경0. |
| 리뷰·수락 | Claude 계획 리뷰 지적을 관찰기/fixture에 보정하고 결과 리뷰를 받았다. 정적 리뷰와 실제 관측을 구분하며 아래 처분을 따른다. Owner가 이 제한된 결과를 수락하여 source Work를 완료했다. |

남은 자격 확인은 실제 설치/clean Mac/Gatekeeper·공개 다운로드·실제 adopter 적용과 Windows 공개 대상 전체 기능/설치다. Windows는 공개 전 필수다. 새 스레드 관측은 자동 컨텍스트 압축이나 임의의 긴 세션 재개를 검증하지 않는다. 실제 업무 품질·사용성은 합성 결과만으로 보장하지 않는다.

사용성 후속: 기술 ID보다 작업 제목을 앞세우기, 반복되는 부정형·자격 한계 설명 줄이기, 승인된 계획의 과거 진행 문구를 현재 Work 상태와 혼동하지 않는 안내, 생성된 한국어 강조 렌더링. 정상 작업의 내용·형식·편집 범위는 이번 표본에서 충족했으며 일반 사용자 완료율로 환산하지 않는다.

이 macOS 구현·격리 검증·제한된 행동 결과는 Owner가 수락했다. 남은 실제 적용·공개 전 자격 확인은 별도 후속 범위다. 완료한 회귀13/23·signal·predecessor1·문서 검사와 이번 두 모델 사례를 다시 열지 않는다. 남은 예비 세션은 사용하지 않았다. 실제 설치·adopter·commit/push/PR/merge·공개는 계속 보류한다. 이전 L01 실패와 Driver 개입 L02, 이번 준비 오류/비교 순서 한계는 아래 기록과 외부 자료에 그대로 보존한다.

## 승인 범위와 기준

공급·실행 진입 확인 → 수락 View/Guardrails 로컬 결합 → 전용 Python/설치·update/remove/recovery → EN/KO 첫 작업·재개 → 격리 artifact/정상 품질/회귀 → Claude 결과 리뷰·범위 내 보정. 실제 설치·adopter·commit/push/PR/merge·공개는 보류. Windows 공개 대상 전체 기능/설치는 공개 전 필수이며 이번 구현에서 제외한다.

View base e411c4af9df0402b4542600d3e9cdc8624c9a15e. Guardrails base ff299095ba450ef199392ce2f6d92ee5e8f3918b 및 보존된47파일 patch와 Owner 수락 delta를 integration 입력으로 사용한다. 통합 전 identity와 원격 차이를 확인한다. S0 전에는 결합하지 않는다.

## 한도

최신 행동 마무리 승인: 기존2040분 안에서 이번90분. 행동3세션5턴1080초 중2세션3턴122.488초, Claude2회×240초 중2회를 사용했다. 예비1세션2턴은 미사용이다. 이전 실패·소비량을 이월했다. 최종 시간은 아래 closeout 기록을 따른다.

이전 마무리 승인(역사): 기존 추가2040분 안에서 당시180분, mode별 회귀 추가1800초, Claude 추가2회×240초, 행동 추가2세션4턴720초. 이번 Claude2/2회, 행동2/2세션·3/4턴·112.903/720초를 사용했다. 이전 행동 포함4세션6턴273.523초이며 실패·소비량을 초기화하지 않았다. 아래 최초 승인 수치는 역사로 보존한다.

2026-11-01T13:08:26Z 시작, 추가2040분. 공급·진입 확인 최대150분. 기존449.29분 비교값/실패는 보존(과거15분 예약 등 측정 한계 포함); 새 시간과 이중 계상하지 않는다. Claude 추가5회·각240초(기존1회 소비), 행동2세션·4턴·합계720초. 통신·권한·종료 불명은 재시도 없이 중단. 사용자 대기는 계상하지 않고 도구/리뷰/검사 대기는 포함한다.

## 검증 선택

원 View와 Guardrails 근거는 원 identity의 증거로 보존. 변경한 launcher/runtime/통합/lifecycle은 집중검사 후 고정 후보 normal/parent-O 전체1쌍과 artifact 검사. D01–09 각 경로9개, A01/02 두 세션, L01 설치 마찰은 서로 별도 집계. 정상 입력 누락/과잉 거절/같은 유효 승인 반복 요청은 실패로 기록한다. 기존 실패/skip은 새 PASS로 덮지 않는다. 구체 명령/선택ID/timeout/격리 경계는 실행 전에 이 Work에 기록한다.

## 초기 진행 기록

- 승인과 한도 고정, 새 전용 worktree를 수락된 View base에서 생성했다. source 진행 기록과 기존 preliminary review만 준비했다. 제품 변경·통합·설치·시험·모델 호출0.
- 다음: bounded delta R0, 고정 공급 metadata와 archive/라이선스 확보, B1/pre-Python 확인. 초기 공급에3.14.10을 사용하되 자격 불가 시 임의 patch/자체 build로 전환하지 않는다.

## 보존

원 handoff/실패/후보·리뷰 증거는 원 경로에 보존. 이번 private 실행 자료는 기존 계획 artifact의 execution 하위에 두고 이 Work의 공급·리뷰·검증/Owner 수락·복구에 사용한다. 소비가 끝난 중복/임시 자료는 보존 확인 후 정리한다. 새 worktree는 현재 구현과 후속 검증의 소비 경로다.


### S0 공급 metadata / delta R0 준비

공식 tag20261026의 GIL3.14.10 arm64 install_only 및 대응 full metadata 자산을 식별했다. bytes/hash/license/실행은 아직 확인 전이다. 최초10-release 응답이 로컬8MiB 수집 상한을 넘어 assertion 실패했다. 통신 오류는 관측되지 않아 수집 한도 유지·1-release로 범위 축소한 조회를 수행했고 성공했다. 원 실패는 private record에 보존했다.

R0 delta는 계획만, 제품 diff 없음. 고정 packet eda07e5288b20ee5fcc278f0b4a09b1d9a6d910c1675f1727eb0ea78e23f3f69 (9470bytes), base e411c4af9df0402b4542600d3e9cdc8624c9a15e. 위임 도구/시험0, 기존 구독 확인 후1회240초. 입력 drift 전후 확인. 원문과 처분은 이 Work에 기록한다.


## Delta R0 결과 및 Driver 처분

Claude CLI claude-opus-5-5, fresh session f5f45221-d08f-49bf-9c77-628ac45edecf, 기존 claude.ai Pro/firstParty 구독. 170.805초/240, exit0, process group absent, 입력 drift0. 추가1/5 소비(전체2/6). 정적 계획 리뷰이며 실행 증거가 아니다. 판정 CHANGES_REQUESTED; M1–M8 반영 후 S0를 진행하고 S0 진입을 위한 전체 재리뷰는 불필요하다는 의견이다.

<!-- BEGIN VERBATIM DELTA R0 -->
# Colvia macOS 배포/온보딩 실행 계획 delta 정적 리뷰

## 판정: **CHANGES_REQUESTED**

전체 방향과 경계는 유지할 수 있으며 범위 재결정 사유도 없습니다. 다만 아래 M1~M8을 계획에 반영한 뒤 S0에 들어가야 합니다. 반영은 Driver 재량 범위이고, S0 진입만을 위해 전체 재검토를 반복할 필요는 없습니다. B1의 실제 동작은 S0 증거로만 판단할 수 있습니다.

이 리뷰는 Driver의 정적 관찰만 근거로 합니다. 소스, 테스트, 아티팩트는 확인하지 않았으며, 아래 macOS 도구 동작에 대한 언급도 모두 S0 확인 대상입니다. 이 판정은 어떤 권한도 부여하지 않습니다.

## 필수 설계 수정

### M1. source 모드와 header의 분기 충돌 (B1)
- **문제:** root `colvia`가 source checkout에도 있으면 `./colvia --source-checkout` 실행 시 header가 먼저 돕니다. 이때 managed runtime이 없으면 실패하고, header가 argv를 보고 시스템 Python으로 분기하면 금지된 fallback 경로가 생깁니다. 인자 값 위치의 문자열로 우회될 위험도 있습니다.
- **수정:** header는 argv를 해석하지 않고 interpreter도 argv로 선택하지 않습니다. source 모드의 호출 형식은 하나로 고정합니다(예: `<명시 interpreter> -I -B colvia --source-checkout`). 기존 호출 형식이 달라지면 문서와 테스트도 함께 갱신합니다.
- **음성 테스트:**
  - runtime이 없을 때 `./colvia --source-checkout`이 시스템 Python을 실행하지 않음
  - 외부 interpreter로 직접 실행한 installed 호출이 거부됨

### M2. 테스트 주입이 production 선택 경로가 되면 안 됨
- **문제:** "custom root는 테스트 전용"과 "HOME 덮어쓰기 금지"를 함께 지키면서 production bytes를 그대로 실행할 방법이 현재 없습니다. 환경변수 주입은 mutable 입력이 runtime을 선택하는 경로가 되므로 금지입니다.
- **수정:**
  - release bytes에는 override 경로를 두지 않습니다.
  - 테스트는 root 경로 한 줄만 다르게 렌더링한 fixture 변형을 쓰고, production bytes와의 diff가 정확히 그 줄뿐임을 검증합니다.
  - 그 결과는 "production 경로 literal 실행 미증명"으로 기록합니다. 실제 설치, clean Mac, Gatekeeper 증거로 대체하지 않습니다.
- **`$HOME` 해석:** header와 Python이 같은 규칙으로 경로를 해석해야 합니다. HOME이 비었거나 상대 경로이면 fail-closed로 처리합니다. HOME 값은 위치 입력일 뿐 신뢰 근거가 아니며, 무결성은 digest pin으로만 판단합니다.

### M3. pin의 단방향 DAG와 단일 원천
현재 체인은 배포 쪽만 정의되어 있고, launch 시점의 pin 위치와 저장 위치가 빠져 있습니다. 다음을 확정해야 합니다.

```
verifier + tree metadata (product release ID 미포함)
  → root header pin
  → inventory ID
  → product release
  → manifest → bootstrap → SHA256SUMS
```

- **cycle 방지:** verifier와 tree metadata는 product release 식별자를 포함하지 않습니다. 그래야 cycle이 없고 release 간 runtime 공유도 가능합니다.
- **디렉터리 키:** runtime 디렉터리는 archive digest가 아니라 tree metadata digest를 키로 합니다. 설치 후 archive가 사라져도 launch 검증이 가능해야 하기 때문입니다. archive digest는 설치 시점에만 사용합니다.
- **launch 순서:** header의 pin으로 verifier를 해시 확인하고, tree metadata를 해시 확인한 뒤, 전체 tree를 검증하고 exec합니다.
- **중복 pin 처리:** shell 변수와 Python 쪽 값, 그리고 manifest의 pin이 어긋나면 안 됩니다. Python이 자신의 root bytes에서 고정 형식으로 읽게 하거나, build에서 동등성을 강제합니다. 새 assignment가 기존 parser의 "정확히 하나" 규칙이나 `-OO` 조건과 충돌하지 않는지도 확인합니다.

### M4. 플랫폼 pin과 Windows 격리
- **문제:** root bytes가 플랫폼 간 공유되면 macOS pin 추가가 Windows inventory와 release identity를 바꿉니다. 이것은 기존 Windows 증거를 조용히 무효화하거나, 반대로 잘못 승계하는 경로입니다.
- **수정:** 플랫폼별 release로 할지, 플랫폼 키가 있는 pin table로 할지 구현 전에 하나로 정합니다. 어느 쪽이든 기존 Windows 증거는 새 bytes에 승계하지 않습니다.
- **범위 확인:** 이 선택에 새 authority schema나 migration이 필요하면 계획의 중단 조건에 해당합니다.
- **아키텍처:** `uname -m`이 arm64가 아니면(Intel, Rosetta 포함) 복구 안내와 함께 거부합니다.

### M5. 3.14.10 gate는 tuple로 표현
- **수정:** 버전 상수 확장 대신 `(platform, arch, implementation, GIL, exact version, runtime tree digest, 모드)` 전체를 비교합니다.
- **필수 음성 테스트:**
  - Windows + 3.14.10 거부
  - macOS installed 모드 + 3.14.10 시스템 Python 거부
  - 다른 tree digest의 3.14.10 거부
  - 기존 아티팩트의 적격성 불변
  - source 모드 gate의 의도치 않은 변화 없음

### M6. header 필수 규칙
다음을 설계 조건으로 고정합니다.

| 항목 | 규칙 |
|---|---|
| 문법 | 후보 `"""":` 형식은 쓸 수 있으나 POSIX sh 기준으로 작성하고, header 안에 `"""`, 백슬래시, 비ASCII를 금지. Python은 `-W error`로 컴파일 확인(잘못된 escape 경고 방지) |
| 종료 | 모든 shell 경로는 `exec` 또는 명시적 `exit`로 끝나 닫는 `"""`에 도달하지 않음 |
| 스트림 | 검증 단계의 stdin은 `/dev/null`, stdout은 비움. 오류는 stderr와 고유 종료 코드로 출력 |
| 환경 | 도구는 절대 경로로 호출하고 검증 단계는 정제된 환경(`env -i` 등)에서 실행. 특히 `PERL5*`, `DYLD_*`, 내보낸 shell 함수, `IFS`를 차단. 검증용 locale은 exec되는 Python으로 새지 않음 |
| 경로 | `$0`이 상대 경로이거나 `-`로 시작하거나 symlink이거나 `sh colvia`로 호출된 경우를 정의. 기존 `main.__file__` 정확 일치 검사를 약화하지 않음 |
| 인자 | argv, 공백, 빈 인자, 종료 코드, 신호 동작을 현재와 동일하게 유지 |

### M7. tree 검증 기준 보강
현재 금지 목록에 다음을 추가합니다. 위반하면 계획대로 중단하며 검사를 완화하지 않습니다.

- **Case-fold 충돌:** APFS 기본 볼륨에서 archive 대비 파일이 조용히 줄어들 수 있습니다. 대소문자가 다른 항목이 많은 terminfo류를 특히 확인합니다.
- **Hardlink:** archive의 hardlink 항목과 추출 후 link count의 처리 규칙을 정합니다.
- **Mode 정규화:** umask에 따라 결과가 달라지지 않도록 추출 플래그와 canonical mode를 고정합니다. 비교할 mode 범위도 정합니다.
- **`.pyc` drift:** `-B`가 빠진 자식 프로세스 하나가 다음 launch를 실패시킬 수 있습니다. worker, probe, 모든 내부 subprocess의 `-I -B` 전파를 테스트합니다. tree는 활성화 후 쓰기 권한을 제거하고, 삭제 시 권한 복원 절차도 둡니다.
- **Ancestor 범위:** no-follow 검사는 관리 root 아래로 한정합니다. `/var`→`/private/var`나 사용자 환경의 상위 symlink로 인한 오탐을 막기 위함입니다.
- **활성화 경쟁:** `mv staging final`은 대상이 존재하면 그 안으로 들어가 중첩될 수 있습니다. 활성화 프리미티브를 S0에서 확정하고, 패배한 쪽은 승자를 재검증한 뒤 자신의 staging만 정리합니다.
- **비교 대상 외 항목:** `.DS_Store` 같은 추가 파일은 drift로 처리합니다. xattr 처리(`com.apple.provenance` 등)는 비교 대상 여부를 명시합니다.

### M8. EN/KO 범위와 행동 예산 불일치
- **문제:** A1은 목표부터 다음 권고까지 단계가 많고, A2는 fresh session이 필요합니다. 2 sessions/4 turns로는 A1과 A2를 각각 한 번, 한 언어로 돌리면 거의 소진됩니다. EN/KO 양쪽 실행도, 수정 후 재실행도 수용할 수 없습니다.
- **수정:** 예산을 늘리지 않고 실행 전에 턴 배분과 언어를 고정합니다. 실행하지 않은 언어는 결정론적 검사만 거친 것으로 표기하고 "agent 품질 미검증"으로 기록합니다.
- **재실행 불가 시:** 수정 후 재실행 예산이 없으면 수정은 결정론적 증거로만 뒷받침하고, 행동 결과는 first-attempt 값을 그대로 보고합니다.

## 구현 중 수집할 증거 (설계 차단 아님)

### Supply (S0)
- archive 실제 해시와 크기가 metadata 및 upstream 체크섬과 일치하는지 확인합니다. 값의 형식은 세 digest 모두 64 hex이고, product release ID도 sha256 접두와 일치합니다.
- install_only와 pgo+lto-full의 역할을 분리합니다. 기본안은 **install_only만 실행 및 배포, full은 출처와 메타데이터 참조용**입니다. 라이선스 자료가 install_only에 없으면 재배포 요건을 별도로 충족해야 합니다.
- 비변형 byte-identical 배포인지 확인합니다. Mach-O 서명을 깨는 패치가 필요해지면 중단합니다.
- 초과 metadata 실패 기록과 1-release 성공 기록을 함께 보존합니다. 8MiB 상한은 유지합니다.

### 도구 (S0)
- 기본 macOS의 `find`, `stat`, `xargs`, `tar`, `curl`, 해시 도구의 실제 플래그와 NUL 처리를 확인합니다.
- 해시 도구는 하나로 고정하고 도구 간 fallback chain은 두지 않습니다. `shasum`이 Perl 의존인지도 함께 기록합니다.
- `shasum` 출력 경로의 escape가 비교 로직과 충돌하지 않는지 확인합니다. restricted grammar로 완화됩니다.
- `curl`은 HTTPS 전용, 리다이렉트 프로토콜 제한, 크기 상한을 적용합니다.

### 성능
launch마다 전체 tree를 검증하는 비용을 실측합니다. 특히 Guardrails hook 등 **자주 호출되는 경로가 root entry를 재진입하는지** 확인합니다. 시간 제한을 넘기면 임의 stamp cache를 넣지 말고, 그 최적화가 "mutable cache에 권한 없음" 경계 안에 있는지 판단한 뒤 필요하면 범위 결정으로 올립니다. worker와 probe는 계획대로 resolved `sys.executable`을 쓰므로 재검증 대상이 아닙니다.

### Runtime 동작
- `bin/python3` symlink 해석 후 `sys.prefix`, stdlib, dylib 탐색이 `-I`에서 정상인지 확인합니다.
- Seatbelt 프로파일이 공백 포함 경로(`Application Support`)와 realpath를 처리하는지, 최소 읽기와 실행 권한으로 충분한지 확인합니다. runtime root는 쓰기 허용 경로와 겹치지 않아야 합니다.
- parser와 writer가 docstring 선행 구조 및 변경된 shebang을 수용하는지 실제 코드로 확인합니다. 기존 shebang 문자열에 의존하는 테스트와 문서도 찾습니다.

### Lifecycle
- **P/Q 호환:** official1 reader가 새 root bytes를 파싱하고 거부 또는 전이하는 동작을 **실제 predecessor 코드**로 확인합니다. 후보 쓰기 전에 전이를 시작하는 interpreter가 어느 쪽인지 기록합니다. 전환 중 old 진입점(시스템 Python)과 new 진입점(전용 runtime)이 공존하는 구간이 위험 지점입니다.
- **적격성:** official1→2 적격성은 통합된 target 기준으로 재검증합니다.
- **Runtime 제거:** consumer 식별이 불완전하면 제거를 거부하거나 unknown으로 보고합니다.

## 항목별 평가

| 영역 | 평가 |
|---|---|
| Pre-Python 순서 | **타당.** digest pin이 maintainer 사전 검사 결과를 고정하므로 검증된 archive만 추출하고 interpreter 실행 전에 tree를 검사하는 순서가 옳음. M3, M7 필요 |
| 신뢰 진술 | **적절.** 같은 provider 체크섬을 서명 인증으로 주장하지 않고, same-UID TOCTOU도 보장하지 않음. 이 문구를 공개 문구까지 유지할 것 |
| B1 후보 | **구현 가능성 있음, 미증명.** M1, M2, M4, M6 필요 |
| Runtime patch 격리 | **의도는 옳으나 표현 미확정.** M5 필요 |
| Lifecycle | **경계 양호.** 금지 경로와 fallback 차단이 명확함. predecessor 실물 검증 필요 |
| D1~D9, 판정 규칙 | **타당.** 시나리오별 분리, baseline 일치 조건, first-attempt 분리가 적절함 |
| 예산 | **시간은 현실적, 행동 예산은 빠듯함.** 18~28h 대 34h로 시간 여유는 있으나 M8 필요 |

## 진행 조건

1. M1~M8을 Driver disposition으로 계획에 반영합니다.
2. S0(≤2.5h)와 tiny entry/verifier를 **제품 통합 전에** 실행합니다.
3. 다음 중 하나라도 발생하면 의존 통합을 시작하지 말고 중단하여 범위 결정으로 올립니다.
   - archive가 검증 규칙과 맞지 않음
   - 동등한 계약을 유지하는 header를 만들 수 없음
   - M4 해결에 새 schema나 migration이 필요함
   - 기본 도구만으로 검증할 수 없음
4. macOS 완료는 중간 단계로만 기록합니다. Windows 증거 없이는 공개 기능 완료로 표현하지 않습니다.

<!-- END VERBATIM DELTA R0 -->

### Driver dispositions (실행 승인 범위 내 계획 보정)

| ID | 처분 | 적용 조건 |
|---|---|---|
| M1 | accept | header는 argv로 interpreter를 선택하지 않는다. source 호출은 explicit interpreter -I -B colvia --source-checkout으로 고정하고 기존 문서/테스트 영향 확인. installed의 외부 Python 호출 거절. |
| M2 | accept | 생산 override 없음. fixture는 root literal만 변경한 별도 렌더링과 exact diff 검사. 생산 literal/clean-Mac/Gatekeeper 실행은 미검증으로 보고. HOME은 위치 입력이며 절대경로·동일 해석 확인, 테스트에서 HOME을 바꾸지 않는다. |
| M3 | accept | runtime archive digest와 설치 tree metadata digest를 구분. runtime 저장 키는 tree metadata digest로 고정하고 product identity를 verifier/tree에 포함하지 않는다. verifier/tree→header→inventory→release→manifest→bootstrap→외부checksum DAG; build 시 shell/Python pin 동등성 검사. |
| M4 | accept | 이번 배포는 macOS 전용 release 변형. 원 source/Windows 준비 경로와 bytes를 구분하며 새 Windows 지원을 주장하지 않는다. 새로운 schema/migration이 필요하면 중단. Intel/Rosetta 실행은 거절. |
| M5 | revise | macOS3.14.10 자격은 OS/arch/implementation/GIL/exact patch/tree pin/installed-source mode를 함께 확인. 기존 지원3.14.6/7의 계약은 유지하고 Windows3.14.10은 거절. source mode qualification과 installed pin을 구분하며 전체 gate 변경은 검사 후에만 인정. |
| M6 | accept | header의 ASCII/escape/종료 경로·argv/stdin/exit/signal·절대 도구 경로·환경 정제·root identity를 tiny fixture에서 확인. -W error 컴파일 포함. caller environment를 실행 정책 없이 넓히지 않는다. |
| M7 | revise | casefold/Unicode 충돌·archive hardlink·추출 nlink·mode·pyc drift·동시 활성화·추가파일 거절. 관리 root를 canonical anchor로 정하고 상위 alias가 허용되는 경우도 동일 resolved root인지 확인; 기존 제품 no-follow 계약을 일괄 완화하지 않는다. xattr는 identity 목록에서 제외하되 실행 차단/Gatekeeper 상태는 별도 기록, 이를 제거해 실행하지 않는다. 활성화 primitive는 기본 도구에서 확인 후 선택. |
| M8 | accept | A1 한국어 세션 최대3턴, A2 한국어 fresh session 최대1턴, 합계12분. 영어 agent 품질과 재시험은 미검증으로 남기고 결정적 EN/KO 검사와 구분. 사용한 실패/턴을 초기화하지 않는다. |

변경 기록/실패·권한·효과 경계는 원 승인 그대로다. B1·검증 방법의 실행 증거는 아직 없다. S0에서 규칙을 충족하지 못하면 통합에 들어가지 않는다.


## S0 중단 checkpoint — 2026-11-01T13:28:25.895246+00:00

상태: Suspended — 승인된 중단 조건 적용. 추가 실행/권한 확대/통합/제품 구현을 진행하지 않았다. 범위 내 보정 권한은 보존하되 이번 종료의 원인과 실행 환경 차이를 먼저 판단해야 한다. Owner 수락/완료가 아니다.

### 확인한 결과

- 공식 Python Build Standalone tag20261026의 CPython3.14.10 GIL arm64 install_only26,891,793bytes, SHA-256 `30a18bcb9ab75e485b4bf4e5d783dde165571e7e42c56dff47a2d2c5345183a4`. metadata와 downloaded bytes, upstream SHA256SUMS 일치.
- full archive63,780,424bytes, SHA-256 `137db511241f7693ddc57586af1744c7b6375982ab4c31c4a82d10115657d462`. 대응 metadata/license 자료를 보존. install_only1,701항목은 full의 동일 경로와 bytes/mode/link 일치; full-only1,742항목은 install_only에서 빠진 별도 항목으로 기록했다. 이를 binary 차이로 세지 않는다.
- archive 경로·casefold·외부 symlink·hardlink·특수 파일·특수 mode 검사에서 해당 거절사항0. 재배포 문서 구성의 최종 적합성은 아직 완료하지 않았다.
- 실제 사용자 설치 위치가 아닌 private fixture에서 전개. canonical mode 적용 후 OS 기본 find/stat/awk/sort/cmp/shasum으로 전체 membership·파일 hash 대조 PASS,0.2349초. 이 시간은 해당 fixture1회 관측이며 일반 성능 보장은 아니다.
- codesign verify exit0. 이는 파일 서명 무결성 관측이며 notarization/제작자 신뢰/Gatekeeper/제품 자격 PASS가 아니다.

### 실패와 원인 한계

고정 Seatbelt/정제 환경에서 interpreter1회 실행: 0.7305초, returncode -6(SIGABRT), stdout/stderr 없음. Python 기본 모듈 결과는 미관측이다. 프로세스 wait는 완료했다. 재실행0.

실행 시각과 Mach-O UUID `4c4c4494-5555-3144-a12b-6979c6db7c05`가 일치한 crash report에서 dyld CacheFinder/boot_boot/ignition_halt→abort stack을 확인했다. Python 코드에 진입하기 전 동적 로더 단계 중단을 뒷받침한다. 동일 PID37658·4초 구간의 log 조회는0건으로 구체 거절 원인은 미확정이다. 최초 report path 확인은 macOS가 USER/*로 마스킹해 불일치했다. 이 로컬 assertion은 재실행이 아니며 UUID/시각 대조로 소유를 확인한 뒤 필요한 진단 필드만 보존했다.

Driver가 작성한 최소 smoke policy에는 기존 worker/official 실행 policy의 일부 dyld/Cryptex cache 및 ancestor metadata 읽기 규칙이 없다. 검증 harness의 환경 차이가 원인 후보이며 공급 binary 자체 결함으로 단정하지 않는다. 기존 policy의 제안/활성 주석 차이도 있으므로 파일을 그대로 복사해 허가된 확장으로 처리하지 않는다.

후속 ps 조회는 sandbox에서 `operation not permitted`(exit127)로 거절됐다. 우회/권한 확대/반복 조회를 하지 않았다. wait의 종료 확인과 별도 전체 process-query 확인 불가를 구분한다. crash 진단·보고서 원문은 device 식별자 없이 필요한 필드만 task evidence에 보존했다.

B1 실제 header/인수·negative 검증, stdlib/TLS·worker/probe/Seatbelt 적합성, 최종 license package, 공급 활성화 경합은 아직 미완료다. 공급·진입 gate가 통과되지 않아 Guardrails47파일은 결합하지 않았다. 소스 변경은 Work/index/preliminary 기록뿐이며 제품 코드0이다.

### 다음 재개 제안

재다운로드·추가 모델 호출 없이 보존된 profile과 새 smoke profile의 OS-loader 읽기 차이를 확정한다. 실제 deny 근거가 없으므로 특정 path가 원인이라고 확정하지 않는다. 기존 허용 경계를 넘지 않는 검증 환경 보정안을 먼저 고정한 뒤, 재개가 승인되면 같은 archive/검증 tree로 bounded smoke1회를 수행하는 안이다. 네트워크·실사용 파일/credential 차단을 유지하며 넓은 root read/네트워크 허용이나 sandbox 제거로 시험하지 않는다. 필요 권한이 기존 범위보다 넓으면 정확한 추가 path/action을 별도로 제시한다.

예상15–25분은 정적 대조·최소 환경 보정안·1회 실행/정리의 판단치이며 기존 잔여 안에서만 수행하는 제안이다. 실패 시 반복 없이 중단한다. 성공해도 S0의 남은 B1/기본 모듈/선택 profile 확인을 끝내야 통합으로 간다. 지금은 재개/재시험을 실행하지 않았다.

### 소비·보존

이번 승인 묶음 실측 20.00/2040분, 잔여 2020.00분. S0도 같은 20.00/150분, 잔여 130.00분. 기존449.29분 비교값을 이월하면 469.29분이며 이전 예약분 불확실성을 유지한다. 중단 후 대기는 새 active time에 더하지 않는다.

Claude 추가1/5 소비(기존 포함2/6), 잔여4회. 행동0/2세션·0/4턴·0/720초. runtime smoke1회는 모델 행동 호출과 별도이며 실패를 소모0으로 지우지 않는다.

공급 archives/metadata/licenses/checksums·fixture tree·검증 명세/runner/policy·실패/진단은 S0 재개와 원인 비교의 입력이므로 보존한다. 원 Guardrails/View 증거는 수정하지 않았다. 전용 worktree는 구체적 후속 통합/구현에 필요하여 유지한다. 활성 경로 이동/삭제 없음. 기존 Review raw envelope는 원문과 metadata 보존 대조 후 중복만 정리한다. 실제 설치·adopter·Git commit/push/PR/merge·공개0; Windows 필수 공개 조건 유지.


## Owner 승인 S0 재개 — 2026-11-01

Owner가 보존된 근거로 최소 profile 보정을 고정한 뒤 S0 1회만 재개하고, 통과하면 기존 승인 통합·구현·검증·리뷰를 계속하도록 승인했다. 추가 실패는 재시도 없이 중단한다. 기존 소비·실패·실제 설치/adopter/Git 게시/공개 보류는 유지한다.

검증 변경은 native 결과에서 실제 사용된 loader 읽기 규칙 중 현재 존재하는 exact path, runtime 부모의 metadata, `/`의 directory-only read다. 사용자 파일 본문·네트워크·쓰기 규칙은 추가하지 않았다. 보존 original policy와 diff·입력 identity를 고정했다. 정확한 원인은 미확정이므로 이 조합이 통과해도 각 규칙의 최소 필요성을 따로 입증했다고 하지 않는다. source template SHA e7dc8888ad7e5e1d54798892204363bba816644e043f9a7e61d9dc149e6d1dc4, 새 정책 SHA 80ec4c989176b44a49fdfdf26b3d116e413707ff2480001277835206bbd7f183.


## S0 재개 결과와 새 중단 — 2026-11-01T13:39:54.579278+00:00

승인된 Python 최소 실행 재개1회는 PASS: exit0,0.132초, stderr0, process group absent.3.14.10 final GIL·arm64·isolated1·bytecode 비생성 및 ssl/ctypes/sqlite/hash/bz2/lzma/zstd import를 관측했다. 원 binary identity와 사전 tree 검증 유지. stdout의 `gil:false` 필드는 Py_GIL_DISABLED=false를 뜻하며 GIL이 꺼졌다는 뜻이 아니다. 최초 SIGABRT가 사라졌다는 사실은 보정 profile 조합의 근거이며 각 추가 rule의 단독 필요성을 입증하지 않는다.

다음 B1 tiny fixture의 Python 문법/실제 source declaration parser는 통과했다. 고정 native batch3행은 인수(공백/빈 문자열/한글/--source-checkout/선행dash),stdin,flags 보존과 missing runtime/bad verifier pin의 exit65를 관측했다. 그러나 각 행 stderr에 `/private/var/select/sh: Operation not permitted`가 있어 S0 전체는 NON-PASS다. runner의 기존 pass oracle이 stderr를 누락하여 raw3행이 pass=true로 기록됐다. 원 결과를 수정하지 않고 Driver 처분으로 qualification 부적합을 명시한다. batch가 원 고정3행까지 진행한 사실도 보존하며 같은 case/전체 batch 재실행은0이다.

정적 관측: selector는 root 소유 symlink이고 대상은 root 소유 `/bin/bash`다. 이번 header profile은 `/bin/sh`를 읽도록 했지만 selector/resolved bash의 정확한 읽기 규칙이 없다. 이는 검증 harness의 셸 startup 경계 누락이며 제품 Python 결함으로 보지 않는다. 네트워크·실사용 자료·사용자 설정을 바꿀 필요는 확인되지 않았다.

최소 보정 제안은 selector와 `/bin/bash` exact read, selector 부모 exact metadata, 그리고 정상/거절 모든 사례에서 예상 밖 stderr를 NON-PASS로 판정하고 즉시 batch를 중단하는 것이다. policy diff와 oracle diff만 준비했으며 적용/재실행0이다. 기존 runtime/probe/원 실패/원문과 source parser 입력은 보존했다. 다음 재개는 보존된 B1 batch1회 및 남은 S0 확인을 기존 한도 내에서 수행하는 안이며 예상10–20능동분의 판단 추정이다. 다시 실패하면 재시도 없이 중단한다.

현재 공급·진입 checkpoint는 미완료다. 제품 통합/구현은 시작하지 않았다. 실제 설치/adopter/Git commit/push/PR/merge/공개0, Windows 공개 전 필수 조건 유지. 이번 재개 8.76분, 새 묶음 누적 28.76/2040분·잔여 2011.24분. S0 누적 28.76/150분·잔여 121.24분. 기존 비교값 포함 478.05분이며 과거 예약 불확실성 유지. Claude 추가1/5 소비 유지, 행동0/2세션·0/4턴·0/720초.

재개한 runtime PID45469와 header batch3개 모두 각 wait와 같은 group의 부재를 확인했다. ps 재조회는 하지 않았다. 실패 원인 비교/후속 qualification에 필요한 fixture/scripts/policy/identity/output은 현재 경로에 보존한다. 새 중복 전체 source archive나 새 tracker를 만들지 않았다. 실제 실행한 것과 제안만 한 diff를 분리한다.


## Owner 승인 진입점 재개 — 2026-11-01

준비된 exact selector/bash 읽기와 stderr 판정 보정을 적용해 고정3행 batch1회 재개를 승인받았다. 기존 실패·원본 정책·runner·결과는 보존하고 새 시도 디렉터리로 scratch literal만 분리했다. 제품/권한 계약 변경은 없다. 새로운 예상 밖 실패는 즉시 중단하고 재시도하지 않는다. 프로파일 SHA d78063bc8ca4efe5aec5ba5fd5852e43ecd57cd9bc54d5ea972c1e0117e3245b, runner SHA 3fa40406c02ae0a65ea82912944c05fd7af37ba27f8e18d7b2ad8005b05062b6.


## View/Guardrails 로컬 결합

원격 main은 수락 View e411c4a와 일치했다. 원 handoff patch의17개 새 파일 구간에 git extended new-file mode header가 없어 git apply --check가 dev/null 오류로 끝났다. 원 patch는 보존하고 적용용 사본에 해당 header만 추가했다. payload 본문은 변경하지 않았으며 check 통과 뒤 로컬 결합했다. 공통7개 외 파일은 manifest bytes와 일치하고 수락 문서 추가문도 owner-acceptance identity와 일치한다. 이는 source file 결합이며 Git commit/staging/merge는 아니다.

### 통합 후 구현 경계

진입점 재개 3/3 PASS 이후 47파일 결합 완료. 기존 patch의17개 신규 파일 header 누락은 별도 파생 patch로 보정했으며 원 실패와 원본은 보존했다. 신규 파일/비공통 파일 identity 및 Owner 수락 delta 대조를 완료했다. 공식 실행 활성화와 실제 설치는 수행하지 않았다. Guardrails 후속7개는 기존 index에 연결하고 첫 통합 항목의 실행 담당만 이 Work로 연결한다.

배포 구현은 source-only distribution 준비/관리 도구와 기존 managed workspace runtime gate의 최소 변경으로 나눈다. 기존 inventory 목록·schema·승인 요청/확인 계약은 유지한다. macOS arm643.14.10은 version-only 허용 대신 고정 공급 tree·실제 executable/prefix·최종 GIL CPython tuple을 확인한다. Windows 기존 gate는 확장하지 않는다.

### 집중 검사 선택 — macOS 배포 준비 1차

기존 View/Guardrails 원 입력의 증거를 보존한다. 새 공급 catalog·launcher·runtime gate는 그 근거로 대체할 수 없어 offline boundary → `test_macos_distribution` 7개 normal → 고정 공급을 이용한 build-01을 각각180초 상한으로 실행한다(예상 합계1–3분). source 읽기, 현재 task 입력 읽기, 새 fixture lab 쓰기만 허용하고 네트워크/사용자 데이터·자격증명 읽기를 차단한다. HOME을 변경하지 않으며 per-process TMPDIR만 durable lab으로 둔다. canary의 의도된 거절은 예상 결과이고 예기치 않은 권한·통신·종료 실패는 재시도 없이 중단한다. 기본 entry/native/S0 통과 근거는 재실행하지 않는다.

### 구현 checkpoint와 검사 중단 — 2026-11-01

진입점 재개 3/3 성공 후 수락 Guardrails47파일 결합과 최소 배포 구현을 진행했다. 신규 distribution 준비/관리/verifier, source-only prepare-macos, workspace의 exact macOS runtime 확인, 설치본의 외부 interpreter 거절, 집중검사7개를 작성했다. 제품 구현·배포 artifact 생성·lifecycle·정상 품질·행동·최종 회귀의 통과를 주장하지 않는다. 새 구현은 검증 전이다. 기존 S0 결과와 통합 byte 대조는 그대로 보존한다.

첫 offline boundary-01에서 기존 trusted CPython3.14.7 실행기가 Python 코드 전 dyld SIGABRT(-6)로 종료됐다. stderr는 gettext libintl.8.dylib 경로의 `file system sandbox blocked open()`을 명시한다. 기존 검사 프로파일을 좁혀 준비하면서 이 실행기의 라이브러리 읽기 의존을 누락한 Driver의 검사 환경 오류다. 정상/차단 canary는 미실행, unit/build/native/model 호출 모두 미실행. 0.025초, timeout 없음, process group absent. 같은 실행/다른 실행기로 재시도하지 않았다. 원 runner/policy/시작·종료 metadata/로그를 private 실행 자료에 보존한다.

재개 제안: 기존 실행기의 필요한 dylib와 실제 symlink 목적지만 읽기 전용으로 대조하고 고정 프로파일에 반영한 뒤 boundary/unit/build를 통과하면 남은 통합·macOS lifecycle·온보딩·품질/행동·회귀·Claude 결과 리뷰를 동일 실행 묶음과 기존 잔여 한도에서 이어간다. 광범위한 사용자 데이터/네트워크/쓰기 권한 확장은 제안하지 않는다. 추가 모델 호출·실제 설치·Git·공개는 수행하지 않았다.

중단 시 새 실행 누적 53.21/2040분, 잔여 1986.79분; 과거 비교값 포함 502.50분. 새 Claude1/5(잔여4), 행동0/2세션·0/4턴·0/720초. 이번 segment에는 도구/검사/작성 대기를 포함하며 사용자 대기는 제외했다.

### 검사 실행기 의존 경로 보정 재개

Owner가 정확한 실행기 의존 경로 확인·보정과 격리 검사 재개를 승인했다. 기존 프로파일·runner·실패는 보존하고 새 버전에 실제 Mach-O 의존의 외부 dylib lexical/resolved 파일만 읽기 허용했다. 전체 Homebrew 폴더·네트워크·새 쓰기 범위는 추가하지 않았다. 기존 boundary/unit/build 선택·상한을 유지하며 통과하면 승인된 전체 묶음을 이어간다.

### 집중 검사 결과 및 artifact 단계 선택

boundary-02 PASS: 범위 밖 읽기/쓰기와 네트워크 거절. unit-01 7/7 PASS, 0.182초. build-01 PASS, 0.617초: 고정 archive에서 normalized tree catalog 일치와 license 준비, 두 profile payload·manifest·bootstrap 생성. fixture 결과이며 공개 origin bytes·설치 성공이 아니다. 원 boundary-01 실패는 유지한다.

다음 B01 미리보기 무변경, B02 틀린 확인값 거절/무변경, B03 fixture 전용 Python·배포 도구 준비, B04 관리 entry/help를 같은 offline profile에서 실행한다. 각120초·묶음180초, 예상3–15초. 같은 신뢰 코어의 고정 asset-directory fixture만 사용하며 실제 HOME·프로젝트·네트워크에는 쓰지 않는다. 최초 결과를 보존하고 예기치 않은 권한/종료 실패 시 후속 실행을 멈춘다.

### Fixture 활성화 중단 checkpoint

B01 preview와 B02 잘못된 확인값 거절/무변경 PASS. B03은 고정 공급 hash·OS tree 검증과 Python 실행 뒤 준비된 제품 디렉터리를 최종 releases 위치로 이동할 때 PermissionError(errno13)로 종료했다. process group absent, timeout 없음; B04 이후는 실행하지 않았다. 원 코드의 준비 tree 디렉터리 chmod500이 rename보다 앞선 순서와 일치하는 실패이며, 실제 platform 원인 분리 재현은 하지 않았다. source root release directory500, 양 parent는700인지 metadata를 private partial-state 기록으로 확인했다.

격리 fixture의 전용 Python store는 이미 준비되었지만 제품 release·관리 명령·프로젝트 연결은 완료되지 않았다. 실제 사용자 저장 위치·adopter에는 쓰지 않았다. 해당 fixture와 원 build-01/실패 코드·입출력·runner를 다음 활성화/복구 검증의 입력으로 보존한다. 소비자가 남아 있어 정리하지 않는다.

최소 보정 제안은 준비된 release root를 이동 가능한 소유자 모드로 유지하고 원자적 이동 뒤 readonly 고정을 하는 것이다. 모든 payload 검사는 이동 전에 유지하며, final mode 확인·재진입/partial recovery·동시 준비 경합을 묶어 검증해야 한다. 현재 Owner의 권한 실패 중단 조건에 따라 코드 보정·재시험은 수행하지 않았다. 기존 정상 결과를 반복하지 않고 영향받는 activation부터 후속 lifecycle/온보딩/품질/리뷰 묶음을 재개할 수 있다.

새 실행 누적 56.90/2040분, 잔여 1983.10분. 이전 실패·소비량 유지. 추가 Claude1/5, 행동0/2세션·0/4턴·0/720초로 동일하다.

### 활성화 순서 보정과 재개 선택

Owner가 이동 뒤 권한 고정 및 부분 복구부터 기존 묶음 재개를 승인했다. source manager의 release 디렉터리 readonly 고정을 rename 뒤로 옮기고, 이미 게시된 exact release도 검증 후 같은 mode로 마무리한다. 원 build-01과 실패한 stage는 변경하지 않는다. 새 build-02는 동일 product/runtime/catalog/license 자산을 확인해 재사용하며 바뀐 manager/manifest/bootstrap만 다시 렌더링한다. 공급·unit·B01/B02는 반복하지 않는다.

B03R: 기존 runtime만 준비된 partial store에 새 bootstrap 적용, 원 실패 stage 불변, 최종 release mode500/manager 존재 확인. B04: 관리 entry/help. B05: 같은 identity 재진입 완료와 product/runtime 내용 불변. 각120초·묶음180초, 예상3–15초, 기존 offline profile 그대로. 최초 결과와 보정 후 결과를 구분한다. 실제 설치/adopter/Git/공개 없음.

### 활성화 보정 결과와 프로젝트 진입 선택

B03R 부분 store 복구, B04 관리 entry, B05 동일 배포 재진입 모두 PASS(묶음5.13초). 원 실패 stage 불변 및 최종 release 디렉터리500, 기존 product/runtime 내용 불변을 확인했다. 기존 B03 실패는 그대로 남는다. 다음 L02–08은 한글/공백 non-Git 프로젝트에서 preview 무효과·exact input 적용·직접 human/agent View·첫 작업/재개 안내·외부 interpreter 거절이다. 각120초·묶음180초, 예상10–30초. 같은 네트워크/사용자 데이터 거절 profile과 새 durable fixture를 사용한다. 이 결과만으로 agent 행동 품질을 주장하지 않는다.

L02 최초 preview가 exit65로 실패했으며 `--save` 처리의 일반 오류가 하위 결과를 가렸다. 프로젝트 적용은 미시작, 후속 cases 미실행. 원 결과를 보존한다. 먼저 runtime admission과 Git topology를 읽기 전용으로 분리 관찰한다(각30초, 같은 profile, 쓰기는 진단 결과만). 설치 preview 재시도나 적용을 수행하지 않는다. 권한/통신/종료 불명 발견 시 중단한다.

### Git 진입 권한 실패 중단 checkpoint

읽기 전용 진단에서 managed runtime=true, runtime_supported=true를 확인했다. Git topology 호출은71로 실패했다. stderr는 Apple git shim/xcrun의 시스템 임시 위치 cache 생성 거절과 xcodebuild SharedFrameworks 읽기 거절을 명시했다. 이 환경에서 시스템 Git shim이 추가 Xcode 경로로 진입함을 사전 반영하지 못한 검사/실행 진입 설정의 문제다. 사용자 Xcode 설정 오류로 확정하거나 global xcode-select/시스템 설정을 바꾸지 않는다. 진단 후 설치 preview나 기타 실행을 재시도하지 않았다.

L02의 manager `--save`가 원 실패 JSON을 일반 저장 오류로 가리는 별도 제품 결함도 확인했다. 다음 보정은 원 오류 유지, 실제 사용 가능한 macOS Git 실행 경로 선택과 작업 전용 임시 위치 전달을 함께 다루어야 한다. 실제 Git 미제공 Mac의 non-Git 흐름에서 CLT 설치 UI나 숨은 다운로드를 시작하지 않는 조건도 유지한다. 임의의 Homebrew/Xcode 전체 또는 시스템 임시 위치 쓰기 허용은 제안하지 않는다.

보존: build-01/02와 기존 실패 stage, activation-02 통과/입력, project-01 최초 실패, read-only 진단, 현재 source manager 보정. 원 stage는 복구 검증 동안 불변이었다. fixture store는 관리 도구·Python·두 배포 profile 준비가 완료되었고 프로젝트 .hrn 생성/적용은 미시작이다. 모두 현재 복구·후속 qualification 소비가 남아 유지한다. 온보딩/프로젝트 lifecycle/품질/행동/최종 회귀/Claude 결과 리뷰는 미완료다. 실제 설치/adopter/Git 게시/공개 없음.

새 누적 64.18/2040분, 잔여 1975.82분. 과거 실패·소비량 유지, Claude 추가1/5·잔여4, 행동0/2세션·0/4턴·0/720초.

### Git 진입·임시 경로·오류 안내 보정

Owner가 해당 보정과 기존 전체 묶음 재개를 승인했다. macOS PATH가 Apple shim을 선택하는 경우 xcode-select의 읽기 전용 결과에서 실제 Git을 선택한다. CLT 미설치의 명시 오류는 Git 없음으로 처리하여 non-Git 기본 흐름을 유지하고, 다른 오류는 unavailable로 보존한다. Windows 및 명시 PATH의 기존 Git 선택은 유지한다. 실제 Git은 시스템 dylib만 사용함을 정적으로 확인했다.

배포 entry/관리 도구는 HOME을 바꾸지 않고 per-process TMPDIR/XDG_CONFIG_HOME을 Colvia checks 아래로 전달한다. 닫힌 caller의 정확한 config-disable 세 값만 git_environment에서 유지하고 임의 GIT 설정은 계속 제거한다. 이 배포 모드의 Git 정책은 프로젝트 자체 config/ignore가 대상이며 사용자/system config를 자동 가져오지 않는다. 기존 일반 source caller는 원 환경 의미를 유지한다. 제품/ignore 정책 영향은 Git fixture·최종 회귀와 결과 리뷰에 포함한다. 실패 preview의 --save는 파일을 쓰지 않으면서 원 JSON/exit를 그대로 반환하도록 보정했다.

변경 영향 검사: MacOSGitEntryTests5개와 변경 header의 문법/inventory·fixture root 차이2개만 실행한다. 각 묶음180초, 예상1초 미만. 통과하면 기존 고정 공급에서 변경된 source/header를 포함한 build-03을 준비한다. 기존 공급·격리 경계·활성화 회귀 검사는 반복하지 않고 원 identity 근거로 재사용한다.

Git/오류/header 집중7건 PASS(0.182초). build-03은 동일 공급과 변경 source의 새 identity다. 기존 fixture store에 새 관리 도구/제품을 준비하는 B06 후, 원 실패했던 비어 있는 합성 프로젝트에서 L02–08을 재개한다. B01–05는 반복하지 않는다. 상한/격리 경계는 앞선 프로젝트 검사와 같다.

### 온보딩 작성 범위

WQE를 적용해 기존 installed Getting Started에 macOS 배포·첫 작업·재개·관리의 EN/KO 안내를 추가했다. source manual의 준비/첫 Work/재개6페이지는 현재 continuation 흐름으로 정리하고 index에서 새 경로를 우선 안내한다. 이전 checkout 관측은 역사적 범위로 남기며 새 PASS로 쓰지 않는다. 불변 조건은 명시 버전/digest, exact preview 승인, 기본/official 분리, 기록 보존, 프로젝트/도구/Python 제거 차이, 유효 승인 이월, 후속 추천과 이유, Git 별도 결정, Windows 공개 전 필수다. 구조 변경 이유는 기존 첫 사용 안내가 entry-1 source clone/수동 runtime과 과거 실습을 기본으로 보여 현재 배포 사용 순서를 설명하지 못했기 때문이다.

문서 집중 검증: 기존 macOS GFM source 문서 검사1개, 바뀐 manager 저장 실패 보존1개, 변경 안내9문서의 GFM 출력/로컬 링크/코드 밖 별표와 EN/KO marker4쌍을 같은 격리 경계에서 확인한다. 180초 상한, 예상1–5초. 원문 의미·양언어 동등성은 Driver 대조와 이후 Claude 리뷰 대상이며 해시 일치를 의미 동등성으로 보고하지 않는다.

온보딩 문서 검사 PASS: source GFM 검사, manager 오류 보존, 안내9문서 렌더/파일 링크, EN/KO4쌍 marker. 다음 Q는 바뀐 안내/manager를 포함한다. 기존 P 설치를 보존하고 Q 준비→P/Q update→Q repair→Q/P rollback→P reader→detach/retained 조회를 각각 exact preview/apply로 확인한다. 원 프로젝트의 일반 파일/Work·intent 기록은 전후 대조한다. fresh official2도 별도 target에서 확인한다. 각120초·묶음180초(예상30–90초), 같은 격리 경계이며 프로젝트 Git 게시/외부 설치는 없다.

### Lifecycle 결과 및 R1-a 선택

L09–18 PASS, 묶음168.029초. P/Q update39.642초, Q repair6.2초, Q/P rollback7.779초, detach82.936초; 보존 대상 불변과 retained 재설치 거절을 확인했다. 새 original failure/skip를 덮지 않는다. 제거 지연은 사용 마찰 기록이며 성능 보장으로 표현하지 않는다.

R1-a는 공급·pre-Python verifier·header·runtime/Git selection의 정적 코드 발췌와 실제 결과/미검증 경계를 고정한다. 구독 인증 확인 후 fresh CLI, 도구0/MCP0/시험0, 240초·1회, input drift 전후 대조. 관리 lifecycle/온보딩 최종 결합은 R1-b에서 별도 검토한다. packet 6bdfa57e824dc4434c96e6c48da35f2e50d97207f2ba2c2fcc6a41f94e39e98e (21265bytes). 기존 추가5회 상한 안에서 실행하며 Owner 수락은 별도다.


### 재개 진단 권한 실패 및 보존 checkpoint

Git 보정 이후 B06/L02–08, 문서 집중 검사, P/Q update·repair·rollback·detach와 fresh official2 L09–18의 통과 증거를 재사용한다. 통과한 검사는 다시 실행하지 않았다. R1-a의 request/identity/runner는 준비되어 있지만 재개 시 call-started/execution/response/verdict 파일이 없었고 ledger도 추가1/5였다. 호출 또는 완료를 입증할 수 없으므로 리뷰 완료나 미사용 확정으로 바꾸지 않는다. 재호출하지 않았다.

실행 여부를 확인하려고 Driver가 선택한 ps 조회가 바깥 실행 sandbox에서 `operation not permitted`로 거절되었다(exit1). 제품 Git 실패나 테스트 실패가 아니라 진단 명령 선택에 따른 권한 실패다. Owner의 중단 조건에 따라 ps 권한 확대/재시도, 추가 제품 변경·검사·모델 호출을 중단했다. 기록 보존만 수행했다. 이전 리뷰 실행을 확인할 때 새 프로세스 탐색보다 보존된 도구 반환값/시작·종료 기록을 우선해야 한다.

이번 segment 29.33분, 새 누적 93.51/2040분·잔여 1946.49분. 과거 비교값 포함 542.80분이며 이전 측정 한계는 유지한다. Claude 기록 추가1/5, R1-a 호출 상태 미확정, 행동0/2세션·0/4턴·0/720초. 실제 설치·adopter·Git 게시·공개는 수행하지 않았다.

남은 순서는 R1-a 실행 상태를 보존된 기록으로 확정 → 공급/관리 보정과 정상 품질·predecessor/native 검증 → 최종 normal/parent-O 검사 → 제한된 첫 작업·재개 행동 관찰 → Claude 결과 리뷰/범위 내 보정이다. 통과한 공급/진입/lifecycle 증거는 변경 영향이 없는 한 재사용한다.

현재 worktree의 변경 source/문서/신규 파일과 private 실행 자료는 모두 기존 durable 경로에서 후속 검증·리뷰·복구의 입력으로 유지한다. fixture의 실패 stage와 P/Q release/store는 복구 및 predecessor 비교 소비가 남아 삭제하지 않았다. active 경로 이동·정리·새 전체 사본 생성은 없다.


### 공통 기준 반영과 기존 묶음 재개

Owner가 갱신한 세 공통 기준을 지정 revision에서 읽고 현재 Work와 대조한 뒤 재개했다. private intake에 원문 identity를 보존한다. 정상 작업 품질/완료율·불필요한 거절/재승인·중단, 현재 상태/다음 행동/재개 설명을 기존 D/A/L 검증에 반영한다. 새 팀 협업·보안 확장이나 별도 전역 장부/완료 기준은 추가하지 않는다. 공개 플랫폼의 최종 선택은 별도이며 이번 Work의 Windows 공개 전 검증 조건을 임의 완화하지 않는다.

R1-a runner는 모델 Popen 전에 exclusive call-started 파일을 반드시 생성한다. 시작/결과 파일이 모두 없고 ledger 추가1회도 그대로여서 이 runner의 모델 launch에는 도달하지 않은 것으로 판단한다. 과거 auth/preflight의 종료 결과는 미관측이며 성공으로 기록하지 않는다. 준비 packet/입력 identity를 재사용하고 이번 실행은 auth 전 outer 시작 기록과 stdout/stderr를 남긴다. ps 재시도·권한 확대는 하지 않는다. 기존 리뷰/행동/시간 상한 그대로, 현재 재개 준비 읽기5분은 보수적 추정으로 이월한다.


### 관리 payload 검사 최소 보강

정적 대조에서 기존 manager가 파일 hash/목록만 비교해 extra empty directory와 파일 mode drift를 거절하지 않는 공백을 확인했다. 정확한 directory membership, 소유자와 파일 mode를 추가 확인한다. 준비 단계700 및 게시500 디렉터리는 기존 이동/복구 순서를 유지한다. 내용이나 lifecycle 계약은 변경하지 않는다. ManagedPayloadTests4건으로 정상/빈 디렉터리/권한/링크·hardlink를 확인하고 마지막 artifact 검증에 반영한다. 기존 P/Q lifecycle 결과를 새 manager 전체 검증으로 승격하지 않는다. R1-a의 고정3입력에는 변경이 없다.


### R1-a 결과 및 Driver 처분

Claude claude-opus-5-5, session b890ca42-4f64-47f5-a955-3a2a3cfd5a27, 기존 claude.ai Pro/firstParty 구독, 도구/시험0. 220.304초/240, exit0, group absent, input drift0, permission denials0. 추가2/5 소비. 정적 조건부 통과이며 새 runtime 전체·정상 품질·행동/공개 자격의 PASS가 아니다.

<!-- BEGIN VERBATIM R1-a -->
# Colvia R1-a 정적 검토

제공된 패킷만 읽었으며 실행과 해시 재계산은 하지 않았습니다. 생략된 소스와 R1-b 범위는 판단하지 않았습니다. 차단 수준의 무결성 우회는 발견하지 못했습니다.

## 발견 사항

### 중간
1. **`env -i`가 설치 entry의 소비자 호환성을 깨뜨릴 수 있음 (`header`, 추론):** `HOME`, `PATH=/usr/bin:/bin`, `LC_ALL`, `TMPDIR` 등 고정값만 남아 인증 환경변수, `SSH_AUTH_SOCK`, `HTTPS_PROXY`가 사라집니다. `/usr/bin`, `/bin` 밖의 CLI도 찾지 못합니다. 모델 실행기가 이들에 의존한다면 A01/A02와 네이티브 통합에서 실패합니다.
   - **수정:** 실제 소비자가 쓰는 변수와 절대 경로만 고정 allowlist로 전달합니다. 전달이 불필요하면 그 사실을 회귀 테스트로 고정합니다.
   - **프록시:** bootstrap의 `curl`도 같은 이유로 프록시 환경에서 실패합니다. 미지원으로 명시하거나 프록시 변수를 고정 전달합니다.

2. **Git 사용자·시스템 설정 차단이 불완전함 (`git_environment`, `header`):**
   - `GIT_CONFIG_*`는 `/etc/gitattributes`를 막지 않습니다. `GIT_ATTR_NOSYSTEM=1`을 header와 closed 분기에 모두 추가합니다. `git_environment`가 `GIT_*`를 지우므로 두 곳 모두 필요합니다.
   - managed entry는 `XDG_CONFIG_HOME`을 바꾸지만, 다른 closed caller는 `~/.config/git/ignore`와 `attributes`를 계속 읽습니다. closed caller 계약에 빈 `XDG_CONFIG_HOME`을 포함합니다.
   - 전역 설정 차단으로 global excludes와 LFS filter가 빠져 status나 checkout 결과가 달라질 수 있습니다 (추론). 정책은 유지하되 D01–D09에 해당 사례를 포함합니다.

3. **bootstrap의 실패 계약이 일부 경로에서 지켜지지 않음 (`bootstrap`):** `mkdir -p`, `mktemp`, `mv`, `tar`, `find`, `chmod`, `fetch` 안의 `shasum`이 실패하면 `set -e`로 멈춥니다. 안전하게 중단되지만 Colvia 안내 없이 종료 코드 65가 아닌 값이 나옵니다.
   - **수정:** 각 명령에 `|| fail`을 붙이거나 `ERR` trap으로 통일합니다. Python 단계의 종료 코드 전파 방식은 별도로 정합니다.

4. **상대 경로 `HOME`에서 무한 루프 발생 (`bootstrap`, verifier):** `parent=${parent%/*}`는 슬래시가 없으면 값이 바뀌지 않아 `/`에 도달하지 못합니다. verifier의 `scratch_parent`도 같고, `root`만 절대 경로를 확인합니다.
   - **수정:** bootstrap 진입 시 `store`의 절대 경로를 확인합니다. verifier는 네 인수 모두 절대 경로를 요구합니다. `cd` 후 상대 catalog 경로가 깨지는 문제도 함께 막힙니다.

### 낮음
5. **Python 전 mode 검증에 특수 비트 누락 (verifier):** `%OLp`는 하위 9비트만 보여 주므로 `4500`도 `500`으로 통과합니다. 이후 Python 검증이 거부하지만, Python 실행 전 경계로는 불완전합니다.
   - **수정:** `%OMp`를 함께 출력해 `0`인지 확인합니다.

6. **Git 선택의 예외 처리와 source 호환성 (`git_executable`):**
   - `subprocess.TimeoutExpired`가 `ContractError`로 변환되지 않습니다. 호출부 처리는 생략되어 확인하지 못했습니다.
   - `xcode-select` 환경에서 `DEVELOPER_DIR`을 제거해, 이를 쓰는 source caller의 Git이 shim과 달라질 수 있습니다 (추론). 값이 있으면 전달합니다.
   - 관찰 기록만으로는 CLT와 Xcode 선택을 각각 확인했는지 알 수 없습니다. 둘 다 회귀 테스트에 포함합니다.

7. **고정 `--max-time 120`:** 26.9MB 파일은 약 224KB/s 미만에서 항상 실패합니다.
   - **수정:** 전체 제한을 파일 크기에 비례시키거나 `--connect-timeout`과 `--speed-limit`/`--speed-time`으로 바꿉니다.

8. **builder 입력 검증:**
   - origin 정규식의 `github.com`에서 `.`이 이스케이프되지 않았습니다. `github\.com`으로 고칩니다. 런타임 `case`가 잘못된 host를 막으므로 영향은 작습니다.
   - `bootstrap()`이 `manifest_sha`와 `canonical(manifest)`의 일치를 확인하지 않아, 불일치가 설치 시점에야 드러납니다. 인수 대신 내부에서 계산하거나 일치를 assert합니다.
   - 표시된 코드에는 `RUNTIME_ID == SHA256(objects + files)` 확인이 없습니다. `runtime_catalog` 끝에 assert를 추가합니다. 이 값 자체는 재계산하지 못했습니다.

9. **activation 환경이 entry와 다름 (`bootstrap`):** header와 달리 `TMPDIR`, `XDG_CONFIG_HOME`, Git 차단 변수를 설정하지 않고 stdin도 닫지 않습니다. `--bootstrap-activate`가 Git이나 임시 파일을 쓰면 다르게 동작합니다 (추론, R1-b와 교차 확인 필요).
   - **수정:** 같은 고정 환경을 적용하고 stdin은 `/dev/null`로 닫습니다.

10. **적용 안내가 모호함:** "이 파일을 … 실행"만으로는 브라우저로 받은 비실행 파일의 실행 방법을 알 수 없습니다.
    - **수정:** 바깥 shell의 `$0`를 preview에 전달해 `/bin/sh <경로> --apply --confirm <값>` 형태로 정확히 출력합니다.

## 문제를 찾지 못한 부분 (표시된 코드 기준)
- **shell/Python 경계:** polyglot 파싱, 인수 전달, `-I -B`, 환경 정화 후 Python 실행 순서에서 문제를 찾지 못했습니다.
- **membership/link 검증:** 정렬과 catalog 형식은 builder, shell, Python에서 일치합니다. `|`나 개행이 든 이름, hardlink, type 불일치도 거부됩니다.
- **archive:** 고정 해시 확인이 먼저 수행되므로 symlink 체인의 어휘적 검사 한계는 현재 악용 대상이 아닙니다.
- **다운로드와 잠금:** redirect allowlist, 크기·해시 확인, lock trap, 실패한 stage 보존에서 결함을 찾지 못했습니다. 다만 비정상 종료로 남은 잠금의 복구 경로는 R1-b에서 확인해야 합니다.

## 판정: **조건부 통과, 공개 준비 완료 아님**
- **현재 판정:** 고정 공급과 Python 전 검증 구조는 승인 범위에 부합합니다. 1–4번은 수정 후 해당 단위·오프라인 테스트로 확인해야 하고, 5–10번도 일반 수정으로 처리하면 됩니다. 추가 승인 게이트는 필요 없습니다.
- **미완료:** 새 런타임 전체 회귀, D01–D09와 네이티브 통합, A01/A02 모델 동작은 아직 끝나지 않아 통과로 간주하지 않습니다.
- **실행 불가:** 공개 URL 실행과 clean Mac 관찰은 수행할 수 없었습니다.
- **범위 밖:** Windows 지원은 공개 릴리스 차단 항목으로 남아 있으며 여기서 검증하지 않았습니다. 게시자 서명·notarization도 주장하지 않습니다.

<!-- END VERBATIM R1-a -->

Driver: 1 revise — inherited credential/proxy 변수를 자동 전달하지 않는다. official runtime_input은 고정 절대 실행기/인증 파일을 별도로 검증하고 API/proxy override를 원래 거절한다. 기본 A01/A02의 agent도 Colvia launcher가 실행하는 대상이 아니다. 프록시/임의 PATH·사용자 Git 설정을 요구하는 환경은 현재 managed 경로의 한계로 명시하고 정상 대조를 추가한다. 2 accept — closed Git에 GIT_ATTR_NOSYSTEM과 /dev/null XDG 경로를 설정한다. 프로젝트 자체 ignore/config는 유지한다. 3–6 accept — bootstrap ERR 안내/65, 절대 HOME/4개 verifier 인수, 특수 mode bit, xcode-select timeout 변환과 source DEVELOPER_DIR 보존. 7 defend — 고정120초 다운로드 상한은 유지한다. 느린 연결은 미완료로 보존하며 조용한 재시도·상한 확대 없이 향후 선택한다. 8–10 accept — literal host/manifest/catalog identity, activation 닫힌 환경/stdin, 정확히 인용한 bootstrap 명령 안내를 보강한다. 관측 전 보정이며 해당 집중 검사 후만 해소로 기록한다.


R1-a 보정에서 verifier bytes가 바뀌면 기존 runtime 위치의 pinned verifier와 충돌함을 정적으로 확인했다. 신규 store slot은 catalog identity와 verifier digest를 함께 결속하고 기존 slot/launcher는 그대로 보존한다. runtime의 CPython bytes/공급 pin/지원 tuple 변경은 없다. 관리 payload4·리뷰 보정6·영향 header2의 총12개 집중 검사와 새 build-05를 실행한다. 각180초, 예상1–5초. 이후 새 verifier의 실제 정상/특수 비트/상대 인수 거절·bootstrap 환경/오류 안내를 offline fixture로 확인한다. 과거 supply/download/S0를 재실행하지 않는다.


리뷰 보정12건 PASS(0.183초), 새 build-05 PASS(0.615초). 다음 R01–11은 tiny tree 정상/특수 bit·상대 인수 거절, 상대 HOME 즉시 거절(하위 입력만 주입, 전역 HOME/인증 경로 변경 없음), 정확한 preview 명령, 의도된 missing asset 오류65/자료 보존·동시 activation 거절, 신규 verifier slot activation과 구 Q entry 보존이다. 각120초/묶음180초, 예상5–15초. 기존 fixture store만 사용하고 외부 다운로드/실제 설치 없이 실행한다. 의도된 잘못된 입력 거절은 통제 결과이며 예상 밖 권한·통신·종료 오류는 즉시 중단한다.


R01 tiny tree positive PASS. R02의 setuid-file 거절 예상은 exit0으로 실패했다. 직후 read-only stat/Python 관찰에서 실제 파일 mode가500임을 확인했다. 요청한4500이 실현되지 않아 특수 비트 거절 조건을 충족하지 못한 fixture 오류이며 kernel/volume 원인은 미확정이다. 제품 우회 재현으로 기록하지 않는다. 원 runner/출력/fixture/진단을 보존한다. 일반 assertion 실패의 범위 내 보정으로 새 디렉터리 sticky bit1500과 stat precondition을 사용한 R02R부터 재개한다. R01은 재사용하며 R03–11은 미실행 입력 그대로다. 환경·권한·시간 상한은 변경하지 않는다.


R02R–R11 PASS(6.673초). R01 기존 통과와 함께 특수 bit/상대 경로 거절·정확한 명령 안내·일반 IO 실패65·경합 거절·신규 verifier slot과 구 Q entry 보존을 확인했다. 원 R02는 fixture 실패로 유지한다.

다음은 수락 S1b의 고정 worker/probe 사례를 새 managed3.14.10 runtime/통합 source에 대조한다. 기존 native 입력/판정·runner를 재사용하고 경로/runtime identity만 바꾼다. W1읽기/W2쓰기/W3–5검사, P1–5읽기/쓰기/exec/reexec/외부접근 거절. controller는 고정 trusted 합성 driver, 실행 worker와 probe는 제품의 deny-default native profile 그대로다. Positive control은 task 내부 합성 파일·loopback만이며 외부 네트워크·credential·provider 호출은 없다. HOME/전역 설정을 변경하지 않는다. 각 child30초·coordinator360초, 예상10–40초(새 runtime 비용 미측정). 프로필/권한 완화 없이 실제 closure와 입력 drift를 확인하고 예상 밖 권한·통신·종료 불명은 재시도 없이 중단한다. 전체 Host admission·D/A 품질과 구분한다.


새 runtime native W1–W5/P1–P5 PASS(1.2837초), 실제 읽기/범위 편집/3개 검사와 정해진 접근·exec/reexec 거절, 정상 종료와 source drift0 확인. 합성 Controller seam의 결과이며 Host/provider·D/A 전체 관측의 대체 근거가 아니다.

관리 lifecycle 정적 보강: 라이선스 pin을 runtime/release 게시 전에 확인하고, remove-tool도 동일 activation 잠금으로 갱신과 직렬화한다. 제거 도구 복구는 같은 버전 bootstrap 재적용이며 프로젝트 재부착과 구분한다. 기존 손상 runtime은 보존/거절한다는 복구 한계와 closed 환경·프록시/다운로드120초 한계를 Getting Started에 명시했다. 자동 손상 원본 덮어쓰기·상한 확대는 추가하지 않는다.


D01–D09를 각 profile N=9로 고정했다. D01–08은 동일 한글 상태/alpha→beta/두 bullet/인용/HTTPS 링크/가상 token/구간 밖 보존/실제 문서 checker 전후 판정이다. continuation은 설치된 Core 프로젝트와 명시적으로 제공한 source 문서 helper를 이용하는 수동 편집 흐름이며 official2 활성화로 부르지 않는다. official2는 실제 Controller/materialize/native worker seam을 사용하며 Host/provider admission은 제외한다. D09는 실제 installed intent ticket의 유효 적용·소비된 exact replay의 무변경·변경 입력 거절이다. 동일 승인 요청0은 결정적 harness 관측이며 agent 부담은 A01/A02에서 별도로 확인한다. 최초 결과/통제 사례/미실행을 분리한다. 각 worker30초·전체600초, 예상30–120초. 기존 offline parent 경계와 native worker 정책을 유지한다.


D 최초 실행: continuation D01–D08 PASS, D09 FAIL, official2 9건 미실행. D09는 source 모듈을 먼저 import한 driver가 runpy로 installed entry를 실행하여 `module outside bound payload: hv2ref`로 거절됐다. 제품의 출처 검사가 올바르게 작동한 시험 연결 불일치다. 권한이나 guard를 완화하지 않는다. 원 runner/result를 보존하고 D09부터 실제 installed CLI의 독립 subprocess로 연결한다. 설치본 provenance 검사는 그대로 유지하며 이전 거절에서 intent publication이 없었음을 확인한다. D01–08은 재사용한다. 각 호출60초/전체600초·기존 offline 경계 유지.


D09의 actual installed subprocess 경로 PASS: 기존 유효 ticket 적용, exact 재실행 무변경, 변경 input 거절. continuation 보정 후9/9(최초8/9와 fixture 실패 유지). official2 D01 준비 단계에서 시험 driver가 control-store marker를 protocol compact JSON으로 써 canonical emission 오류가 났다. worker/모델/수락 실행 전이며 제품의 canonical 검사 유지. 원 fixture는 그대로 보존하고, 기존 native 준비와 같은 canonical_json_bytes로 새 official2 cohort를 준비한다. continuation9건은 재실행하지 않는다. source/권한/한도 변경 없음.


### 정상 품질 native 실행 경계 중단 — 2026-11-01 UTC

quality-03의 official2 D01 첫 읽기 child는 `sandbox-exec: sandbox_apply: Operation not permitted`로 exit71, stdout0이었다. Controller가 바깥 offline sandbox 안에서 제품 native sandbox를 다시 적용하는 지점에서 거절됐다. 해당 worker는 문서 작업에 진입하지 않았고, child와 controller의 group absent를 확인했다. timeout이나 종료 불명이 아니다. 제품 기능/계정/통신 실패로 확정하지 않는다. 같은 후보의 별도 trusted coordinator→native worker/probe 실행은 이미 PASS였으며, 시험 runner의 중첩 격리 구성 불일치가 원인 후보다. Owner의 권한 실패 조건에 따라 재시도·권한 완화·후속 검사/모델 호출을 중단했다.

완료/미완료 분리: continuation 최초8/9, 시험 연결 보정 후9/9. official2는0/9이며 D01 환경 차단, D02–09 미실행. 별도 native W1–W5/P1–P5 PASS는 이 품질 cohort의 대체 근거가 아니다. A01/A02는0/2 미실행이다. 정적/합성 결과를 실제 사용자 완료율·Host/provider 자격으로 확대하지 않는다.

이번 재개 구간 실측 25.41분과 초기 읽기 보수적 예약5분을 이월해 새 묶음 누적 123.92/2040분, 잔여 1916.08분이다. 과거 비교값 포함 573.21분, 기존 측정 불확실성 유지. Claude 추가2/5 소비·잔여3(각240초), 행동0/2세션·0/4턴·0/720초. 기존 실패 기록과 미실행 슬롯은 초기화하지 않는다.

다음 최소 보정은 이미 통과한 native-managed coordinator/child 분리를 재사용해 official2 품질에 중첩 sandbox가 적용되지 않도록 runner를 연결하는 것이다. 실제 native worker의 deny-default 권한/고정 입력/상한을 유지하며 무제한 test shell이나 제품 보호 완화로 대체하지 않는다. 기본9건과 native10건은 반복하지 않는다. 그 뒤 exact predecessor·기록을 만든 P/Q·관리 제거/복구, 최종 normal/parent-O, A01/A02와 Claude 결과 리뷰/범위 내 보정은 기존 승인 묶음의 미완료 순서로 남는다. 전체 회귀와 old predecessor의 정확한 구 interpreter 연결은 아직 준비/실행 전이며 통과로 기록하지 않는다.

보존: 기존 source worktree의 미커밋 변경, build-01–05와 필요한 실패 stage/원 runtime·새 runtime, R1-a request/원문/처분, native 결과, quality-01/02/03의 runner/결과/부분 fixture를 기존 durable 경로에 유지했다. 소비자는 최종 qualification·실패 비교·복구이며 결과 수락/잔여 처분 전까지 필요하다. 실제 사용자 설치·adopter·commit/push/PR/merge·공개·Windows 실행은0이다. active 경로 이동/삭제는 없다.


### 잔여 묶음 재개 승인 — 2026-11-02 KST

Owner가 실행 조정기와 native child 격리를 분리하는 보정, 기존 task 경로 쓰기/실행·정확한 이전 source/runtime 읽기, 시험 전용 로컬 소켓과 child 종료 확인용 읽기 전용 관찰을 승인했다. 제품 worker 격리와 시스템 전역 정책은 유지한다. 기존 통과 근거를 재사용하여 official2 정상 품질, 관리 lifecycle 잔여, 정확한 이전 버전/채워진 기록 전환, 최종 normal/parent-O, A01/A02와 Claude 결과 리뷰·범위 내 보정을 재승인 없이 이어간다. 통신·권한·종료 불명 실패의 해당 실행은 재시도하지 않고 보존하며 영향 없는 오프라인 작업만 계속한다. 추가 권한/한도는 자동 확대하지 않는다. 실제 사용자 설치·adopter·Git 게시·공개는 보류, Windows는 공개 전 필수 유지.

재개 시 소비123.9249/2040분·잔여1916.0751분, Claude2/5·행동0/2세션0/4턴0/720초를 이월한다. 예상4–8시간은 기존 회귀 비용과 잔여 보정에 대한 판단이며 상한과 다르다. 도구/리뷰 대기 포함, 사용자 대기 제외, 겹친 wall time은 한 번 계상한다.


official2 D01–D09 PASS(14.567초), 실제 native child와 조정기 정상 종료. 기본9건과 native10건 재사용. 원 중첩 sandbox 실패 보존. 후속 관리 제거/경합/승인/복구본과 라이선스 사전 거절 집중검사, exact predecessor 구 interpreter 명시 연결. 코드 편집 스크립트의 예상 문자열 assertion 1건은 파일 쓰기 이전 실패로 남기며 시험 실행 실패와 구분한다. 제품 runtime 허용 범위 변경 없음.


R1-b는 관리 lifecycle/안내에 한정한 정적 결과 리뷰다. 고정 packet 772610bc43fa0e6ce2aba4d94579433213552e34a1f6c70bea99f88a9d138fe1 (43822bytes), manager 원문과 Getting Started, 합성 근거/남은 검사 한계를 제공한다. 실제 실행 권한0·도구0, 기존 구독 확인 후 최대240초/1회. 관리 집중16건과 build-06 PASS. 원문·처분은 이 Work에 이어 기록한다.

R1-b 전송 전 packet을 manager 원문과 안내35–57행으로 축소했다: faea8f5e0a64654ccbebb9dab16b73f1fcf777d2cdd50a439f769dec24bab487, 25667bytes. 앞선 큰 packet은 호출하지 않았다.


회귀 환경 준비 import root 누락을 모델/worker 호출 전 보정했다. 환경 검사6건 중3건 실행에서 과거 U2 검증기 artifact의 실행 파일 mode700/755 계약이 managed Python500을 거절했다(제품 guard 유지). managed runtime은 변경하지 않고 과거 U2 고정 fixture 자원의 Python/binary를 기존 trusted3.14.7 실제 파일로 명시한다. 전체 suite parent와 제품 fixture의 sys.executable은 새 managed3.14.10을 유지하며, 이미 별도 확인한 native worker10건과 구분한다. 해당 원 환경 실패는 보존한다.


## R1-b 결과와 처분

Claude claude-opus-5-5 fresh session e3edbc8c-b656-4e86-9cac-d52950d7463e, 139.572초/240, exit0·정상 종료·입력 drift0, 구독 경로 확인. 추가3/5 소비. 정적 리뷰이며 실행 증거가 아니다.

<!-- BEGIN VERBATIM R1-b -->
# Colvia R1-b 정적 리뷰

## 판정: 조건부 미수용
소유자 수용 전에 **F1~F3 수정 또는 반증**이 필요합니다. 설계 경계(런타임 제거 거부, 손상 보존, 정확한 요청 적용)에서는 데이터 파괴 경로를 찾지 못했습니다. 다만 프로젝트 CLI 소스가 범위 밖이어서 F1 등의 실제 영향은 확정할 수 없습니다.

이 판정은 제공된 `manager.py`와 문서 발췌만 읽은 결과이며, 아무것도 실행하지 않았습니다.

## 구현 결함

### 높음

**F1. 기존 프로젝트에도 기본 프로필이 `continuation-1`로 적용됨 (`lifecycle`, `--profile`)**
- **트리거:** `official-execution-2` 프로젝트에서 프로필 없이 `status`, `doctor`, `repair`, `update`, `rollback`, `remove`를 실행합니다.
- **영향:** 프로젝트의 기록과 무관하게 continuation 배포본의 CLI가 실행됩니다. `repair`는 `--profile` 없이 continuation 경로를 `--source`로 넘깁니다. 안내 메시지에도 프로필 지정 방법이 없어, 거부되면 오분류와 불필요한 중단으로 이어지고 수용되면 프로필이 잘못 바뀔 수 있습니다.
- **수정:** 기본값은 `install`에만 적용합니다. 나머지 명령은 프로젝트에 기록된 프로필을 읽어 쓰거나, 판별할 수 없으면 명시를 요구합니다. official2 프로젝트의 `repair`와 `status` 음성 fixture도 추가합니다.

**F2. 비원자적 쓰기로 재시도가 영구히 막힘 (`write_new`, `activate`)**
- **트리거:** `notices/<sha>.tar` 또는 `tools/<id>/colvia-manage`를 쓰는 중 디스크 부족, 강제 종료, 전원 차단이 발생합니다.
- **영향:** 최종 경로에 일부만 쓴 파일이 남습니다. 재실행하면 "기존 라이선스 자료/도구 복사본이 달라졌습니다"로 거부되며, 지원되는 복구 경로가 없습니다.
- **수정:** 같은 디렉터리의 임시 파일에 쓰고 fsync와 chmod를 거친 뒤 `os.link` 또는 `os.replace`로 게시하고 디렉터리를 fsync합니다. 부분 파일 잔존 fixture도 추가합니다.

### 중간

**F3. 적용 결과가 불명확한 실패로 보고됨 (`lifecycle`)**
- **시간 초과:** `timeout=300`을 넘으면 변경 중인 CLI가 강제 종료됩니다. 이때 사용자에게는 영어 `TimeoutExpired` 메시지만 보이고, 이 문구에 `--confirm` 값을 포함한 argv가 그대로 드러납니다. 복구 안내도 없습니다.
- **stderr 출력:** 경고 한 줄만 있어도 stdout JSON과 returncode를 버리므로, 적용이 성공했어도 실패로 보입니다.
- **stdout 오류:** 비어 있거나 JSON이 아니면 영어 `JSONDecodeError`가 그대로 출력됩니다.
- **수정:**
  - apply에는 고정 시간 제한을 두지 않거나 충분히 늘립니다.
  - 시간 초과 시 "결과 미확인, 재시도 전 status 확인"을 한국어로 안내합니다.
  - stdout을 먼저 파싱해 결과를 표시한 뒤 stderr 존재를 별도로 알립니다.

**F4. 안내된 복구가 실제로 동작하지 않음 (`validate_payload`, `activate`, 문서)**
- **배포본 손상:** 메시지는 "같은 버전의 검증된 배포본으로 복구"를 안내합니다. 그러나 bootstrap을 다시 실행해도 기존 대상의 `validate_payload`에서 같은 오류로 거부됩니다.
- **런타임 손상:** `main`이 모든 명령 전에 `verify_runtime`을 실행하므로 `status`와 `doctor`도 쓸 수 없습니다. 활성화도 거부되는데, 문서는 "복구 경로 확인"만 안내합니다.
- **관리 도구 손상:** 활성화와 `remove-tool`이 모두 거부됩니다.
- **수정:** 보존 정책은 유지합니다. 다만 메시지와 문서에는 자동 복구가 없다고 명시하고, 손상본을 격리 이름으로 옮긴 뒤 재설치하는 절차를 제공합니다.

**F5. 분리된 프로젝트에 설치를 안내함 (`start`/`resume`, 문서)**
- **트리거:** `./colvia`가 없는 분리 프로젝트에서 `start` 또는 `resume`을 실행합니다.
- **영향:** "프로젝트 연결부터 시작하세요: … install"이 출력되는데, 영문 문서는 분리된 프로젝트가 새 설치 대상이 아니라고 합니다. 한국어 문서에는 이 제한이 빠져 있습니다. `./colvia` 제거 여부는 CLI 소스로 확인해야 합니다.
- **수정:** 먼저 `status` 분류로 분기하고, 한국어 문서에 제한을 추가합니다. "보존한 도구로 기록 조회"에는 실제 명령을 적습니다.

**F6. 안내 명령이 PATH에 없음 (`start`/`resume`)**
- **트리거:** 설치 후 안내대로 `colvia-manage install …`을 실행합니다.
- **영향:** 설치가 shell 설정을 바꾸지 않으므로 일반 환경에서는 command not found가 납니다.
- **수정:** `activate`처럼 `store/bin/colvia-manage`의 절대 경로를 quote해서 출력합니다.

**F7. 활성화 완료 메시지가 항상 신규 설치 기준임 (`activate`)**
- **트리거:** 버전 갱신 또는 `remove-tool` 후 복원에서 bootstrap을 실행합니다.
- **영향:** 항상 `install`을 안내합니다. 기존 프로젝트의 다음 단계인 `update`가 안내되지 않고, 문서의 "관리 도구 복구는 재연결이 아님"과도 어긋납니다.
- **수정:** 신규 연결, 기존 프로젝트 갱신, 도구 복원을 구분해 출력합니다.

**F8. 사람이 본 미리보기를 적용할 수 없음 (`lifecycle`)**
- **트리거:** `--save` 없이 미리보기를 실행한 뒤 안내대로 "이대로 적용해줘"라고 요청합니다.
- **영향:** 요청과 operation ID가 저장되지 않습니다. 에이전트가 미리보기를 다시 만들어야 하므로, 적용 범위가 사용자가 본 것과 달라질 수 있고 확인도 반복됩니다. `store/requests`는 만들어지지만 이 파일에서는 쓰이지 않는데도, 제거 안내는 "요청"을 보존한다고 합니다.
- **수정:** 미리보기 성공 시 요청을 `store/requests/<operation-id>.json`에 자동 저장하고, 경로와 확인값을 출력합니다.

**F9. 상태와 무관한 고정 문구 (`lifecycle`)**
- **미리보기:** `classification`이나 CLI 응답과 무관하게 항상 "보존: 작업·승인·결과 기록과 외부 복구 자료"와 적용 권유를 출력합니다. 미리보기 응답이 `preview`가 아니어도 동일합니다.
- **상태 조회:** `uninitialized`, `partial`, `unsupported`가 returncode 0으로 돌아오면 `./colvia view`를 안내합니다.
- **오류 메시지:** `message`가 있으면 `next_action`이 가려집니다.
- **수정:** `preview`일 때만 적용을 권유하고, 보존 범위는 응답 값에서 가져오며, 상태별로 안내를 나눕니다. 두 필드는 모두 출력합니다.

**F10. 공유 Python 제거 문구가 조건부로 읽힘 (`remove-runtime`, 문서)**
- **트리거:** 사용자가 "전체 사용처가 확인될 때까지 남깁니다"를 읽고 제거 가능 시점을 기다립니다.
- **영향:** 코드는 무조건 거부하므로 그런 시점이 오지 않습니다. 거부 자체는 의도된 동작이지만 문구가 이를 잘못 전달합니다.
- **수정:** "현재 버전은 이 명령으로 공유 Python을 제거하지 않습니다"로 바꾸고, 저장소에 남는 항목도 안내합니다.

### 낮음

- **`mkdir(parents=True, mode=0o700)` (`activate`):** 중간 부모 디렉터리는 기본 권한으로 생성됩니다. 현재 fixture는 통과했지만 tar 순서에 의존할 수 있고, 순서가 바뀌면 안전하게 거부되긴 해도 빌드가 실패합니다. 부모를 명시적으로 0o700으로 만드세요.
- **`verify_runtime`의 30초 제한:** 시간 초과 시 영어 예외가 출력되고, 느린 디스크에서는 손상과 구분되지 않습니다. 한국어 "검증 시간 초과"로 분리하세요.
- **이전 버전 bootstrap:** 새 관리 도구를 경고 없이 이전 버전으로 교체합니다. 복사본은 남지만, 교체 전후 버전을 출력해야 합니다.
- **`lifecycle`의 stdin:** `verify_runtime`과 달리 stdin을 상속합니다. `stdin=subprocess.DEVNULL`로 통일하세요.

## 실행 증거 공백 (결함과 별개)

| 항목 | 현재 상태 |
|---|---|
| 기록이 쌓인 프로젝트의 update, repair, rollback, detach와 정확한 이전 버전 복귀 | 미완료 |
| v1 작업 중단 뒤 v2 활성화 상태에서 `--recover` | 근거 없음. 문서는 "정확한 배포본 보존"만 요구하고, `tools/<id>/colvia-manage` 사용 절차가 없음 |
| 활성화 재시도 | 재시도마다 새 stage를 쓰는지 bootstrap으로 확인 필요. 같은 stage는 `prepared.mkdir`에서 실패하므로 "부분 stage 복구 가능"이라는 docstring은 새 stage를 전제로 함 |
| official2 프로젝트의 lifecycle (F1) | fixture의 프로필 범위를 전달 내용에서 확인할 수 없음 |
| 최종 회귀 테스트와 에이전트 세션 | 미완료. 스크립트 사례로 모델 동작이나 "이대로 적용해줘" 흐름의 품질을 추론할 수 없음 |
| clean Mac, 공개 다운로드, Gatekeeper, Windows | 미검증이며, 문서도 별도 검증 대상으로 올바르게 구분함 |

<!-- END VERBATIM R1-b -->

Driver: F1 프로필은 binding 기반 reader 선택 후 제품 검증을 유지한다. F2 완성 파일만 no-overwrite 게시, F3 고정300초 유지(무제한 제안은 defend)·timeout 결과미확인 안내와 child group 정리, JSON 먼저 표시·stderr 별도 안내. F4 자동 손상 덮어쓰기 대신 보존/복구 한계 명확화, F5/F6 기존 기록과 절대 명령 안내, F7 신규/기존/복구 흐름 구분, F8 미리보기 요청 자동 보존, F9 상태별 안내, F10 제거 미지원 명시를 반영한다. 저위험 부모 권한/입력 종료·검증 timeout 안내는 함께 보정한다. 현재 activation 검사는 build-06 고정 artifact라 source 후속 보정과 독립이다.


관리 보정 집중29건 PASS·build-07 준비. build-06의 실제 fixture 활성화/기록 있는 intent의 update/rollback/repair/detach·관리 도구 제거/복원은43.894초 PASS. Work 기록은 해당 fixture에서 비어 있으므로 별도 전환 검사로 남긴다. 환경 검사 최초2건 재사용+남은4건 PASS; private proxy fixture mode600 보정과 초기 실패 유지. R2 보정 정적 리뷰 packet 174b94bf011c64975eefb6f0cb7a750e0ed722371f9ba7ac4d5d49ea4a9c04c5 (23327bytes), manager diff·현재 복구 안내·검사 요약을 제공한다. 최대240초/1회, 도구/시험0.


## R2 결과와 처분

Claude claude-opus-5-5 fresh e933fba5-f365-4b91-be86-6a5ea07dbb04,106.791초/240,exit0·group absent·drift0. 추가4/5 소비·잔여1.

<!-- BEGIN VERBATIM R2 -->
# Colvia R2 정적 검토

**판정: 수정 필요 (blocking 2건).** F1-F10의 수정 방향은 대체로 타당하지만, 아래 2건은 F1·F3 수정에서 새로 생겼거나 남은 문제입니다. 제공된 diff와 문서만 읽었고 실행하지 않았습니다. diff 밖의 `main` 예외 처리, payload shebang, `store/requests` 생성 여부는 확인하지 못했습니다. 수락 여부는 Human Owner가 결정합니다.

## Blocking

### B1. 관리 도구가 중단되면 apply가 감독 없이 계속될 수 있음 (회귀)
- **위치:** `run_lifecycle`
- **원인:** `start_new_session=True`로 자식이 별도 세션에서 실행되므로 터미널의 SIGINT·SIGHUP이 자식에게 가지 않습니다. 정리 코드도 `TimeoutExpired`만 처리합니다. R1b의 `subprocess.run`은 같은 세션에서 실행됐고, 예외가 나면 자식을 kill했습니다.
- **트리거:** `update --apply` 중 Ctrl-C, 터미널 종료, 또는 에이전트 도구의 SIGTERM.
- **결과:** 관리 도구만 종료되고 product CLI는 프로젝트를 계속 변경할 수 있습니다. 사용자는 중단됐다고 믿고 `status`나 `--recover`를 실행해, 진행 중인 상태를 중단 상태로 오판할 수 있습니다. 파이프가 닫혀 최종 응답도 잃습니다.
- **최소 수정:**
  - SIGTERM·SIGHUP 핸들러에서 예외를 발생시킵니다.
  - `except BaseException`에서 기존 TERM→KILL 프로세스 그룹 정리를 수행합니다.
  - 그 뒤 "적용 결과 미확인, 요청·파일 보존, status 확인" 안내를 출력합니다.
  - SIGKILL로 관리 도구가 죽는 경우는 막을 수 없으므로 "미확인" 한계로 문서화합니다.
  - 인터럽트와 SIGTERM에 대한 자식 그룹 정리 테스트를 추가합니다.

### B2. 연결 기록이 손상되면 문서가 안내한 `status`까지 실패함
- **위치:** `selected_profile`
- **원인:** 문서는 "손상·불완전하면 상태를 확인한 뒤 프로필을 지정"하라고 안내합니다. 하지만 binding 파싱은 `status`·`doctor`에도 먼저 적용되고, 실패를 처리하지 않습니다.
- **트리거와 결과:**

| `binding.json` 상태 | 발생 결과 |
|---|---|
| 잘린 JSON | `JSONDecodeError` 원문 또는 main 처리에 따른 오류 |
| `active_release` 누락, 최상위 비객체 | `KeyError`/`TypeError`, main이 잡지 않으면 traceback |
| `inventory_id`가 list | `TypeError` |
| 알 수 없는 ID | `--profile` 지정 요구 |

- **영향:** 사용자는 판정 전에 어떤 프로필을 지정해야 하는지 알 수 없습니다. 복구 안내가 순환하며, 이는 F3의 응답 명확성 수정과도 어긋납니다.
- **최소 수정:**
  - binding 읽기를 `try`로 감싸고 `OSError, ValueError, KeyError, TypeError`를 처리합니다.
  - `status`·`doctor`는 기본 판독기로 넘겨 product CLI가 손상을 분류하게 합니다.
  - 변경 명령은 고정 문구로 거부하고 `status --details`를 안내합니다.
  - 값이 `str`인지 먼저 확인합니다.

## 조건부 blocking: 실제 코드 확인 필요

### C1. 연결 해제 후 기록 조회 안내
`status`의 detached 분기에는 두 가지 위험이 있습니다.
- **실행 경로:** 안내 명령은 `source/colvia`를 직접 실행합니다. 검증된 경로는 `python3.14 -I -B source/colvia`입니다. shebang이 PATH에 의존하면 F6가 재발합니다.
- **판독기 선택:** detach 후 binding이 없으면 판독기가 항상 continuation-1로 정해집니다. official 프로젝트를 detach하면 `status`와 안내 명령이 다른 프로필의 판독기를 사용합니다. 이 판독기가 official 기록을 읽지 못하면 "보존 기록 조회" 안내가 거짓이 됩니다.

**최소 수정:** 전용 Python 경로와 `-I -B`를 포함한 전체 명령을 출력합니다. official detached fixture로 조회가 되는지 검증하고, 안 되면 프로필 선택 근거를 추가합니다.

## 비차단이지만 수정 권장

1. **`--apply --save`의 성공 후 오류:** 초기 검증에서 막지 않는다면, 적용이 끝난 뒤 "미리보기만 저장 가능" 오류가 납니다. 실제 변경은 성공했으므로 오판을 부릅니다. 이 검사는 실행 전으로 옮기세요.
2. **pending 파일이 private하지 않음:** `pending.open("xb")`는 umask 기본 권한으로 파일을 만들고, 내용을 쓴 뒤에 `fchmod`합니다. `--save`를 공유 디렉터리에 지정한 상태에서 중단되면 요청 파일이 0644로 남을 수 있습니다. `os.open(O_CREAT|O_EXCL|O_WRONLY|O_NOFOLLOW, 0o600)`으로 만든 뒤 최종 mode를 적용하세요.
3. **비중단 실패에서 pending 잔존:** 기존 파일로 인한 `EEXIST`나 SMB·exFAT 등의 `ENOTSUP`이면 `.pending-*`가 남습니다. 중단이 아니라 게시 실패가 확정된 경우이므로 pending을 삭제하고 고정 문구로 안내하세요.
4. **내구성 표현:** 주석의 "crash cannot leave partial bytes"는 프로세스 중단에 대한 설명으로 한정해야 합니다. macOS의 `fsync`는 `F_FULLFSYNC`가 아니므로 전원 손실까지 보장하지 않습니다.
5. **`--save` 경로 검사:** `.hrn`만 차단하므로 `<project>/req.json`이 허용됩니다. 이는 "프로젝트 밖에 요청 파일만 저장"한다는 문서와 다릅니다. target 하위 경로 전체를 거부하세요.
6. **이전 문구 잔존:** `verify_runtime`의 "원본을 보존하고 복구해 주세요"는 자동 복구 미지원 한계와 맞지 않습니다. "에이전트에게 손상 위치 확인을 요청"으로 통일하세요.
7. **문서의 프로필 설명:** "기존 프로젝트는 프로필을 이어받음"은 official1→official2 전환과 맞지 않습니다. 예외를 한 문장으로 명시하세요.
8. **`install` 기본값:** 기존 official 프로젝트에 `--profile` 없이 `install`을 실행하면 binding을 읽지 않고 continuation-1 판독기를 씁니다. 중단된 official install의 `--recover`도 같습니다. product CLI가 거부할 것으로 보이지만, 거부 문구가 올바른 다음 행동을 안내하는지 fixture로 확인하세요.
9. **비정상 응답 처리:**
   - `rc≠0`인데 `message`와 `next_action`이 모두 없으면 안내가 사라집니다. R1b의 기본 문구를 되살리세요.
   - `confirm_token`이 없는 preview는 `KeyError`가 납니다. `run_lifecycle`의 `killpg`에서 나는 `PermissionError`도 고정 문구로 처리하세요.

## 문제를 찾지 못한 항목 (정적 기준)
- `renamex_np(RENAME_EXCL)` 호출 형식과 게시 순서
- 디렉터리 생성 시 prepared 하위 mode 처리
- 300초·30초 제한 유지와 타임아웃 시 TERM→KILL 순서
- 비정상 JSON의 고정 문구 처리와 정상 응답 + stderr 공존
- 상태별 메시지 분기, `start`·`resume`의 절대 경로 안내
- `remove-runtime` 현재형 거부 문구와 저장 구성요소 복구 한계 문서

## 수락 전 남은 조건
- B1과 B2 수정 및 회귀 테스트
- C1 확인
- 사용자가 pending으로 밝힌 새 산출물 검사와 전체 회귀·행동 검증

fixture 통과 결과는 수정 전 산출물 기준이므로 이번 변경의 증거로 이어지지 않습니다. 실제 설치, adopter, 게시, Windows, 일반 품질은 계속 미주장 상태로 두어야 합니다.

<!-- END VERBATIM R2 -->

Driver accept: B1 SIGINT/TERM/HUP 및 BaseException에서 child group 정리·종료 관측 후 결과미확인 안내, B2 손상 binding은 진단 reader로 전달·writer는고정안내거절. C1 직접 header는 pinned shell이라 PATH fallback은 없지만 명시적 Python/I/B 안내로 정렬하고 official detached 검사를 추가한다. 추가 지적: pending600 생성·확정된 EEXIST/ENOTSUP 폐기, 전원손실 한계, target 하위 요청 저장 거절, 프로필 전환 예외/기존 install·apply exact request 선택, 확인값/오류 응답 검사 보강. apply+save는 이미 최초검사에서 거절하여 변경 없음. 원 API·실행 상한·제품 승인 경계 유지. 마지막 결과 리뷰는 잔여 검증 근거와 이 보정을 합쳐1회로 진행한다.


### 신호 종료 검사 실패와 독립 작업 계속

관리 집중31건에서 SIGINT/SIGTERM의 두 subcase가10초 안에 응답하지 않아 실패했다. 시험 부모는 finally에서 종료/reap했고 wrapper group absent였으나 별도 세션 child의 즉시 종료 관측이 없었다.16:01:01Z 정확한 합성 marker에 대한 읽기 전용 관찰에서 잔존 프로세스0을 확인했다. 정상 종료로 소급하지 않는다. CPython selectors의 InterruptedError 처리 경로가 handler 예외를 삼키는 것이 정적 원인 후보이며 RuntimeError로 최소 보정했다. 원 함수/실패 출력 보존. 해당 실제 신호 실행은 재시험하지 않는다. handler→cleanup의 오프라인 mock 검사와 영향 없는 lifecycle/Core·행동 검증을 계속한다. 최종 전체 pair에는 이 미재실행 신호 사례1개(2subcase)를 명시적으로 남겨 전체 qualification 완료를 주장하지 않는다.


최종 검사 선택: 새 runtime/launcher/Git 경계 및 Guardrails 통합의 누적 영향 때문에 기존 정상 품질·native/focused만으로 core 전체 회귀를 대체하지 않는다. 회귀 normal/parent-O 두 mode의 전체 발견 목록을 고정하되 실제 신호 실패1개는 재실행하지 않아 명시적 미검증으로 남긴다. 나머지 고유 test IDs, import alias, skip/실패/시간을 원문에 저장한다. 환경6건의 최신 보정근거 재사용, timeout 치환 없음. 모드당7200초 상한·과거 약71분/모드(새 조합 추정불확실), 전체상한 내. exact artifact lifecycle10건은 이전3.14.7/새3.14.10의명시연결, 각 기존child상한 유지·coordinator7200초(기존소비포함)로 별도 실행한다. 실패 시 미실행을 PASS로 바꾸지 않는다.


해당 배포본에서 Work/intent 기록을 채운 F02–F15 PASS(원 fixture worker=None 전달만 보정, 원실패보존). official2 fresh init의 저장 요청은 {format,plan}인데 manager의 apply가 최상위 candidate_release만 읽어 continuation을 선택했다. 제품은 source-changed로 적용 전 거절(정상 안전 경계). plan.candidate_release reader 선택을 추가하고 원요청/프로젝트 보존, 그 apply부터재개한다. normal 회귀는1394선택 중31PASS 뒤32번째 actual shebang 검사에서 PATH의시스템 Python이 선택되어 AttributeError로 실패했다. parent는managed3.14.10, shell child는시스템버전이었던연결오류다. 고정 PATH 선두에 이미승인된managed bin을 추가하며 source guard/상한 유지. 첫31건의src/fixture/import는불변이므로 동일test ID/원result로이월하고 나머지normal을실행한다. 새관리요청검사와opt모드는별도기록.


행동 A01/A02 준비: 기존 보정된 stdin framing/연결 분류와 고정 native 정책을 재사용했다. A01은 설치안내 계획1turn→합성 Owner 승인 뒤 README bounded 편집/검사/Work 서술 기록1turn, A02는 같은 결과/기록을 새 session에서 읽고 모호한 이어가기 요청에 현재 상태·다음추천을 제시하는1turn이다. 최대2세션4턴720초 중 계획3턴, session360초·turn180초, 계정/admission 시간포함. 원장은실제호출직전에소비하며 실패 재시도0. 모델 native도구·MCP·추가network파일접근0, parent의화이트리스트합성read/write/check만. 자료에절대개인경로/비밀0 확인. 공통guide는실제후보bytes이나 Work는plain합성서술이며typedauthority생성·실제adopter/compaction·일반사용자완료율증거로확대하지않는다. 호출전에고정입력/실행파일hash와기존ChatGPT계정을확인하며구독불일치시모델을호출하지않는다.


A01은143.678초·1세션2턴, ChatGPT계정확인/고정모델·native0/MCP0, 보존입력/계정metadata불변·종료확인. 계획turn의README/검사보류, 승인후bounded편집/체크/WORK기록 완료·동일승인재요청0. 다음추천은현재범위결과확인후종료, 이유는WORK.md마지막단락에명시되어기능적합성기준PASS. 최종채팅의이유는축약됐고부정형경계문구가보여UX보완한계로남긴다. typedauthority/실제설치/Owner결과수락으로확대하지않는다. A02는같은결과와기록으로새세션1turn을관측한다.


exact predecessor lifecycle의첫초기화는Git classification failed로거절됐다. 구정본git_environment가GIT_*차단변수까지제거하는것을읽기전용대조로확인했다. 구source/권한정책을변경하지않고테스트전용Git wrapper에서시스템/사용자config차단을재고정한다. HOME은유지하고네트워크/쓰기경계그대로다. 이는구명령을현재격리환경에연결하는입력보정이며원실패보존, 제품guard완화없음. wrapper source/고정Git경로를보존하고lifecycle10건을독립실행한다. actualsignal재시험과무관하다.


### 야간 묶음 진행 기록 — 2026-11-02

- A02: 새 세션 1턴, 16.942초. 완료한 README·검사와 남은 Owner 결과 확인을 복원하고 현재 범위 종료를 추천했다. 읽기 5회, 쓰기·추가 검사·범위 확장 0, 위반 0, 종료 확인. A01/A02 합계 2세션·3턴·160.620초이며 합성 기능 관측이다. 추천 이유가 최종 채팅에서는 간접적이고 부정형 경계 문장이 반복되는 UX 한계는 실사용 보완 후보로 유지한다.
- L01은 부분 근거만 확보했다. 격리 bootstrap·전용 Python·프로젝트 lifecycle과 A01 결과는 각각 관측했지만, 하나의 설치 프로젝트에서 typed Work로 이어지는 전체 경로를 관측하지 않았다. 전체 완료율·사용자 마찰 합산값을 만들지 않는다.
- exact predecessor lifecycle은 7건 통과 뒤 same-window fixture의 copytree가 읽기 전용 파일 mode를 보존하여 문서 변경 시 PermissionError로 중단했다. 제품 호출 전 시험 준비 오류이며 원 실패·산출물을 보존한다. 해당 사례는 재시도하지 않고 독립된 미실행 2건만 별도 실행한다. 이미 통과한 populated Work/intent 관리 경로 근거는 유지하되 이 사례를 대신했다고 주장하지 않는다.
- 추가 Git 설정 대조군은 개인 `.gitconfig` 조회가 격리 정책에 거절되어 실행을 중단했다. 설정 내용은 얻지 못했고 권한 확대·재시도는 없다. 기존 Git 선택·환경 단위검사와 실제 fixture lifecycle 통과는 유지하되, 해당 별도 대조 검사는 미완료다.
- 온보딩/Work 10문서 GFM 렌더링·로컬 링크, EN/KO 4쌍 hash marker, 집중 2검사 통과. 전체 normal 회귀가 진행 중이며 신호 실패 사례는 명시적으로 제외한다.

시간은 현재 재개 구간의 실제 경과를 한 번만 더하며 병렬 검사·리뷰 시간을 중복 합산하지 않는다. 기존 대기/실패와 예약 오차는 유지한다. 신호·권한 실패를 PASS로 바꾸거나 완료 범위를 넓히지 않는다.


normal/parent-O 모드는 각각 별도 durable 임시 경로와 결과 파일을 사용한다. 공통 special-mode fixture는 읽기 전용이고 Unix socket fixture는 고유 TemporaryDirectory를 사용함을 확인했다. 두 모드를 병행하되 각 기존 child timeout과 7,200초 coordinator 상한을 유지한다. 실행 시간은 mode별 기록하고 누적 한도는 겹친 wall time을 한 번만 센다. 자원 경합이 실패 원인 후보가 되면 원 실패를 보존하며 시간 상한을 늘리지 않는다.


일반 회귀는 첫 구간31 PASS + 둘째 구간106 PASS 뒤 Git 기본 무시 규칙 assertion으로 종료했다. parent-O는137 PASS 뒤 같은 assertion으로 종료했다. 두 실행 모두 input drift0·process group absent이며 원 결과를 보존했다. 원인은 closed Git environment의 XDG와 content fingerprint의 원 환경 참조 불일치, 일반 설정 fixture에 inherited closed tuple이 섞인 것이다. 기본 ignore 경로를 git_environment에서 읽도록 한 곳 보정하고, 기존 합성 HOME fixture에 명시적 합성 Git config 경로를 지정해 일반/closed 계약을 구분했다. 실제 사용자 HOME·설정·권한은 바꾸지 않는다. Content·Lifecycle 관련 집중 검사와 closed/global 대조를 추가한다. 이 변경과 무관한 선행 PASS만 ID별 이월한다.

중단 처리의 별도 정적 경합도 보정했다. Popen handle 생성 중 signal은 pending으로 기억하고 handle 확보 뒤 같은 종료 정리 경로로 전달한다. 생성·통신·결과 반환 경계가 같은 exception 처리 안에 있고, 생성 전/중 미확인 상태는 고정 안내로 남긴다. 직접 handler 호출의 오프라인 mock만 추가하며 실패했던 실제 signal 재시험은 계속 보류한다.


### Git 정책·중단 정리 보정과 새 배포본 근거

관리되는 Python 3.14.10에서 관련 집중 검사 59건을 실행해 모두 통과했다(53.447초, 입력 불변, 종료 확인). 일반 Git 설정, 명시적 프로젝트 excludes, closed 설정의 fingerprint, lifecycle visibility와 신호 callback 모의 검사를 포함한다. 새 closed-ignore 검사를 이전 함수로 실행한 의도된 반례는 예상한 fingerprint 동등성 지점에서 실패했다(0.297초). 보정한 함수의 동일 검사는 통과했다. 이 반례는 소스 파일을 바꾸지 않는 별도 프로세스에서 수행했으며 예상 밖 실패 또는 실제 신호 재시험이 아니다.

새 fixture 배포본의 manifest는 7520b7fc46b3b8d428cace856c4bb4419121b9ecc568d9969f7187acc11d2768, bootstrap은 e3f02b3cdc01de76a011db95d6693a2df7aa9ca86f57bbf1afdb0c2a6d914297이다. continuation 배포본은 product-release-5d2e168f989ede076697aac1, official2는 product-release-3cd9c033c71ef16ce7fe4714다. 공개·실제 설치 산출물로 수락하지 않았다.

해당 배포본에서 활성화, Work·intent 기록을 채운 프로젝트의 update·이전 reader·rollback·재update·repair·detach·보존 기록 조회, official2의 저장 요청 초기 설치·프로필 자동 선택·repair·detach·보존 기록 조회·재개 안내가 통과했다(370.201초, 종료 확인). 변경 없는 관리 명령 제거·복원과 runtime 제거 거절은 이전 F08–F13 근거를 재사용했다. 새 코드의 실제 signal 중단 검사는 계속 미검증이다.

남은 normal/parent-O 회귀는 1,397개 고유 선택 ID를 기준으로 진행 중이다. import alias 20개는 중복 실행하지 않고, 실제 signal 실패 사례 1개는 명시적으로 제외한다. normal은 영향 없는 이전 134 PASS와 새 집중 59 PASS를 이월하고, parent-O는 영향 없는 같은 모드의 이전 134 PASS만 이월한다. 변경한 Content/Lifecycle fixture의 이전 결과는 이월하지 않는다. Git 정책 분기는 이월한 사례의 원 XDG와 effective XDG가 모두 /dev/null로 같았으므로 변경 영향이 없다. 전체 source·test·launcher·shipped docs·runtime 입력은 각 모드에서 고정한다.

모드별 7,200초 중단선도 실패 후 초기화하지 않는다. normal 이전 소비 1,301.462초, parent-O 1,282.560초를 차감했으며, 진행 중인 각 실행의 중단 시각은 원장에 고정했다. 남은 원래 상한과 Claude 마지막 1회를 유지한다.


다음 회귀 구간은 normal 424 PASS, parent-O 483 PASS 뒤 같은 source module dispatch 사례에서 멈췄다. 전용 3.14.10에 기존 비격리 -m 호출을 사용하여 runtime gate가 65로 정상 거절한 검사 기대값 문제다. 양쪽 모두 기존 결과와 합쳐 같은 617 PASS를 확보했고 입력 불변·프로세스 종료를 확인했다. 제품 gate는 바꾸지 않는다. 해당 한 검사만 비격리 거절/대상 보존을 먼저 확인한 뒤 -I -B와 명시적 trusted source import로 dispatch를 확인하도록 보정했다. 이전 617개 ID를 각각 이월하고 남은 780개를 실행한다. 새 실행기의 timeout도 기존 실패·집중 검사 시간을 7,200초에서 차감한 값으로 고정한다. 배포 bytes는 같아 새 package 또는 이미 통과한 lifecycle을 다시 만들지 않는다.


다음 구간은 양쪽 158 PASS 뒤 비격리 runtime 거절 문구 assertion으로 종료했다. 관리 tuple은 isolated 조건을 runtime 자격 단계에서 검사하므로 기존 isolated-import 오류보다 앞서 HV2-WORKSPACE-RUNTIME으로 거절된다. 두 실행 모두 exit65를 확인했지만 legacy 문구만 기대한 검사 한 곳이 실패했다. 제품 조건·오류 문구는 그대로 두고 managed macOS 3.14.10의 실제 거절 코드/사유와 대상 bytes 보존을 검사하도록 보정한다. 같은 775 PASS를 모드별 이월하고 남은622개를 수행하며, 이전 소비는 normal 5544.528초, parent-O 5602.758초로 이월한다. 실제 신호·권한 실패는 재시험하지 않는다.


비격리 문구 보정은 두 모드 모두 통과했다. 이어진17 PASS 뒤 installed child 버전 검사가 legacy3.14.6/7만 기대하여 관리3.14.10에서 실패했다. 제품은 정상 supported=true와 parent와 같은 버전을 반환했다. 해당 기대값 한 곳만 관리3.14.10에서는 전체 managed tuple 검증을 요구하도록 보정하고 legacy/Windows allowlist·child 일치·supported 검사는 그대로 유지한다. 미실행 runtime/U2/Work 관련 버전 literal도 함께 읽어 대조했으며 추가 변경은 필요하지 않았다. 모드별792 PASS와 모든 실패·소비를 이월하고 남은605개를 계속한다. 제품 배포 bytes는 변하지 않았다.


다음 구간은 각407 PASS·Windows조건30 skip 뒤 Windows API double이 host3.14.10을 받아 native-arm64 supported 기대값에서 실패했다. Windows3.14.10 거절은 정상이다. 해당 모의 검사 한 곳의 Python/implementation을 명시적3.14.7/CPython으로 고정하고, 같은 모의 OS 조건에서3.14.10 거절도 추가 확인한다. Windows 제품 정책은 그대로다. 각1199 PASS·30 skip을 별도 이월하고 남은168개를 기존7200초 잔여 안에서 수행한다. native Windows 실행 증거로 확대하지 않는다. 보정 준비 스크립트는 test 수정 뒤 runner 문자열 탐색 오류로 종료했으며, 파일 상태를 확인한 뒤 runner만 완성했다. 그 오류 당시 검사·모델 호출은 없었다.


### 회귀 시간 한도 종료와 결과 보존

일반 모드는 실패·집중 검사 시간을 포함해7199.757초, parent-O는7199.252초를 사용한 뒤 각7200초 상한에서 종료했다. 마지막 구간은 coordinator SIGTERM으로 종료되어 unittest 최종 집계가 없다. 각 PASS/skip은 고정 source identity, 명시적 unittest ok/skipped 행과 완료 progress 이벤트를 함께 대조한 관측이다. 일반은 마지막155개 중85 PASS·70 skip, 최적화는145개 중75 PASS·70 skip이며, 이전1199 PASS·30 skip과 합산했다. 이월 ID는 서로 겹치지 않으며 미완료·중단된 ID13/23개는 별도 보존했다. 원 실패를 성공으로 바꾸지 않는다.

양쪽 coordinator process group absent를 확인했다. 종료 뒤18:36:23Z의 정확한 현 작업 경로 marker 읽기 전용 관찰은 잔존0이었다. 이는 그 시점 관측이며 과거 실제 signal 실패의 즉시 종료 증거를 소급하지 않는다. 시간 한도 실행은 재시도하지 않는다. R3 packet은23599bytes, SHA256 f9ab8d56c311d45d16eb0b5a2cccc2af6e222bdecb340e916555ac2a634e7639로 고정했다. 첫 자료 집계는24000bytes 자체 상한을 초과해 호출 전에 멈췄고, 중복된 이전 module fixture 패치를 전달 자료에서만 제외했다. 로컬 원본 증거는 보존했다. 구독 확인 뒤 추가5번째 리뷰를240초·도구/시험0으로 실행 중이다.


## R3 결과와 범위 내 보정

Claude CLI claude-opus-5-5, fresh session972ae39e-7341-4330-936d-a2588621361f, claude.ai Pro/firstParty.117.184초/240, exit0·group absent·입력 drift0·권한 거절0. 추가5/5 소비. 정적 리뷰이며 Reviewer 실행 테스트0. 원문은 다음과 같다.

<!-- BEGIN VERBATIM R3 -->
~~~text
# Colvia R3 정적 리뷰 결과

**판정: 조건부 미통과.** 코드 차단 항목 1건과 같은 계열의 소규모 결함 1건이 남아 있습니다. 공급된 코드와 증거만 읽었고 도구나 테스트는 실행하지 않았습니다. 이 의견은 Owner 수락을 대신하지 않습니다.

## 코드 차단 항목

### B1. `run_lifecycle`: 연속 신호가 자식 정리를 우회함 (R2 차단 항목의 잔여)
- **발생 조건:**
  - 첫 신호의 `RuntimeError`로 `except BaseException`에 들어간 뒤, 세 신호가 모두 `SIG_IGN`으로 바뀌기 전에 다음 신호가 도착하는 경우입니다. 예를 들어 SIGINT 직후 SIGTERM 또는 SIGHUP이 올 수 있습니다.
  - 300초 `TimeoutExpired`로 같은 구간에 들어간 뒤 첫 신호가 도착해도 마찬가지입니다.
- **결과:** 처리기가 `except` 절 안에서 다시 `RuntimeError`를 던져 `killpg` 루프에 도달하지 못합니다. 자식은 별도 세션에서 계속 실행될 수 있고, 안전한 `ValueError` 안내 대신 처리되지 않은 `RuntimeError`가 올라갑니다. 구간은 짧지만 R2에서 막으려던 결과와 같습니다.
- **최소 수정:** 처리기는 플래그만 설정하고 예외를 던지지 않게 합니다. `communicate`는 짧은 timeout(예: 0.2초)으로 반복 호출하면서 플래그와 300초 기한을 확인합니다.
  - 비동기 예외가 사라져 Popen 생성 구간, 성공 복귀 직후, 정리 시작 구간을 하나의 경로로 처리할 수 있습니다.
  - 처리기가 예외를 던진다고 가정한 mock은 함께 수정해야 합니다.
  - 일회성 플래그만 추가하면 timeout 경로의 구간이 남으므로 권장하지 않습니다.

### B2. `selected_profile`: 깊게 중첩된 JSON이 진단 경로를 벗어날 수 있음 (경미)
- **발생 조건:** `binding.json`이나 입력 요청이 깊게 중첩되어 `json.loads`가 `RecursionError`를 내는 경우입니다.
- **결과:** except 튜플에 없어 `status`/`doctor`의 `continuation-1` 대체 경로를 건너뜁니다. 다만 `regular()`의 크기 제한이나 상위 예외 처리가 있으면 영향이 줄어드는데, 이 부분은 공급되지 않았습니다.
- **최소 수정:** except 튜플에 `RecursionError`를 추가하고 회귀 케이스 1건을 둡니다.

## 차단은 아니지만 남는 코드 사항
- **`write_new`:** `EEXIST`/`ENOTSUP` 외의 게시 실패나 쓰기 실패 시 `.pending-*` 파일이 남습니다. 대상 파일이 손상되지는 않습니다. 이후 무결성 검사가 이 파일을 거부하는지는 미확인입니다.
- **`sync_directory` 실패:** 게시가 끝난 뒤 실패를 보고하므로, 재시도하면 `EEXIST`가 납니다. 내구성을 보장하지 않는다는 주석과는 일치합니다.
- **`status` 출력:** `python=3.14.10`, `supported=true`인데 `supported_versions`는 `["3.14.6","3.14.7"]`입니다. 고지된 진단 문구 문제와 달리 기계가 읽는 출력의 불일치이므로, 후속 계약 정리 대상으로 기록해야 합니다. 게이트가 약해진 것은 아닙니다.
- **`_default_git_ignore_path`:** XDG 분기는 수정이 타당합니다. 다만 잘린 HOME 분기가 `git_environment()`와 같은 HOME을 쓰는지는 이 발췌로 확인할 수 없습니다.

## 수정 자체에 대한 정적 판단
- **`RuntimeError` 전환:** selector가 재시도하던 `InterruptedError`와 달리 전파되므로, 원래 시간 초과의 원인은 논리적으로 해소됩니다. 단, 이는 정적 추론이며 실제 신호 검증이 아닙니다.
- **`renamex_np`:** `RENAME_EXCL=0x4`와 사전 `fchmod`/`fsync` 순서는 타당합니다.
- **`selected_profile`:** 중첩 저장 요청 선택과 독자 전용 대체 경로는 의도에 맞습니다.
- **fixture 수정 3건:** 거부 여부와 대상 보존을 계속 단언하므로 oracle 약화로 보이지 않습니다. Windows mock의 3.14.7 고정도 정책을 바꾸지 않습니다.

## 미검증 범위 (실패로 재분류하지도, 통과로 승격하지도 않음)
- **실제 신호:** 원래 실제 SIGINT/SIGTERM 하위 케이스는 **시간 초과 실패** 상태입니다. 이후 수정의 재시험은 없고 양쪽 모드 모두 보류됐습니다. 자식 즉시 종료는 관찰되지 않았고, 나중의 무잔존 관찰이나 mock 통과로 이를 대체할 수 없습니다. **R2 중단 차단 항목은 아직 해소 확인 상태가 아닙니다.**
- **회귀 매트릭스:** 양쪽 모드 모두 **미완료**이며 최종 집계가 없습니다.

  | 모드 | PASS | SKIP | 남음/중단 |
  |---|---|---|---|
  | normal | 1284 | 100 | 13 |
  | optimized | 1274 | 100 | 23 |

  세 값의 합은 양쪽 모두 1397로 맞습니다. 이는 ID별 텍스트 판정 관찰이지 전체 회귀 자격이 아닙니다.
- **회귀 증거에서 불명확한 점 3가지:**
  - 마지막 구간의 **skip 70건은 사유가 공급되지 않았습니다.** macOS에서 필요한 검증이 포함되지 않았는지 사유별 분류가 필요합니다.
  - 보류된 신호 테스트가 1397 안의 13/23에 포함되는지, 분모 밖에 있는지 명시되지 않았습니다.
  - 수정된 Git 테스트의 optimized 모드 실행 여부가 불명확합니다. 59건 PASS는 normal 경로의 증거이며, 해당 ID가 23건 안에 있다면 optimized 증거는 없습니다.
- **기타 실패 및 미실행:**
  - exact-predecessor 케이스는 제품 호출 전 `copytree` 불변 모드 문제로 실패해 미검증입니다(9/10).
  - Git control probe는 실제 HOME 접근이 거부되어 결과가 없습니다.
  - module-dispatch 전체 패치는 이번 리뷰에서 읽지 못했습니다.
- **환경:** 실제 설치 루트, 깨끗한 Mac, Gatekeeper, 실제 사용자 저장소, Windows를 검증하지 않았습니다. Host/provider 전체 자격도 없습니다. native worker와 cohort 통과는 Controller/worker 경계까지만의 증거입니다.
- **제품 경험:**
  - L01은 **PARTIAL**입니다. A01/A02는 합성 narrative Work이며 typed 권한이 아닙니다.
  - 네이티브 compaction, 영어 에이전트 동작, 실제 채택자, 일반 작업 품질은 미관찰입니다.
- **문서:** Maintainer 토큰 예산은 측정되지 않았습니다. 34097은 바이트 수이며 예산 통과가 아닙니다. Work 전용 추가분의 문서 검사도 아직 남아 있습니다.

## 증거 재사용 판단
B1 또는 B2를 수정하면 `manager.py` 해시가 바뀌므로, 이번 build11 artifact 증거를 그대로 재사용할 수 없습니다. 최소 재검증은 다음과 같습니다.
1. 재빌드한 artifact 기준으로 manager 관련 ID와 lifecycle 경로 artifact를 다시 실행합니다.
2. 연속 신호와 생성 구간의 offline 케이스를 추가합니다.
3. 실제 신호 재시험은 Owner 승인을 받아 경계를 정한 뒤 1회 실행합니다.

manager를 사용하지 않고 `work.py`와도 무관한 단위 테스트는 신원 감사를 거쳐 이월해도 합리적입니다. 이 이월이 완료되더라도 플랫폼 또는 공개 배포 자격의 근거가 되지는 않습니다.
~~~
<!-- END VERBATIM R3 -->

Driver accept B1/B2: signal handler는 flag만 기록하고0.2초 이하 communicate polling과 기존300초 절대기한으로 동기 중단한다. cleanup에도 같은 flag-only handler를 유지한다. selected_profile은 RecursionError를 고정 진단 경로로 처리한다. 실제 신호 재시험은 하지 않는다. 이전 함수에 대한 연속신호 cleanup 반례를 오프라인으로 확인하고, 생성/통신/timeout/반복신호/성공출력/깊은 JSON 집중 검사를 실행한다. manager가 달라져 새build12와 관련 artifact lifecycle을 확인하며 이전build11은 원 identity의 증거로 보존한다. 미변경 Core/worker/View 근거는 유지하고 시간 한도 회귀를 재시도하지 않는다. 예상 추가 작업8–15분(기존 artifact370초와 짧은 build/unit 측정, 보정/기록은 판단치), 기존2040분 총상한 안에서 수행한다. Claude 잔여0으로 보정 후 독립 재리뷰는 이번 범위에서 미실행이다.


### R3 보정 근거와 리뷰 질문 해소

보존한 이전 run_lifecycle에 연속 신호 callback 반례를 적용했을 때 timeout cleanup 도중 RuntimeError가 전파되어 종료 정리를 건너뛰는 조건을 오프라인에서 재현했다. 현재 flag-only 처리·절대기한·생성 중 중단·통신 완료 직후 중단·timeout cleanup 중 반복 callback·출력 보존·깊은 JSON을 포함한10검사가 모두 통과했다(0.044초, coordinator0.148초, 종료 확인). 실제 OS 신호나 모델 호출은 없었다. 이는 실제 signal 실패의 재시험이 아니다.

R3의 근거 질문은 보존 자료로 대조했다. 마지막70 skip은 native Windows mechanism46·publication22·native-only2이며 macOS 필수 검사를 skip한 것이 아니다. 선행30 skip도 Windows content5·environment6·lifecycle18·Windows predecessor gate1이다. 실제 signal 보류1개는1397 선택 ID의 분모 밖이다(발견1418−중복alias20−보류1). 새 Git closed-ignore 검사는 parent-O r8 구간에서0.476초로 실제 통과했고 잔여23개에 없다. HOME 분기는 Git에 기본 경로 확장을 맡기는 _git 호출이며, 그 호출도 같은 git_environment를 사용한다. 코드 정적 대조이며 새 실행 증거가 아니다.

기존 matrix 수치는 R3 보정 전 identity의 결과다. manager를 사용하지 않는 Core/worker/View·Git 근거는 같은 product payload identity로 재사용하고, 변경된 manager는 새로운 집중10검사와 build12 artifact 결과로 구분한다. manifest ee114be7ec5b97e71e1d6ac20766f6fc509fb0ea09e1bec4e7c2fb322874033d, bootstrap cadecd47e1c4c3f3c926e001252b938a3c95f165c74be6fc0619785e12db4cdf. 제품 payload의 두 release ID는 build11과 같지만 관리 명령과 배포 envelope는 새 identity다.

후속 계약 정리: status가 관리3.14.10에 supported=true를 반환하면서 supported_versions는 legacy3.14.6/7 목록인 점은 기계 소비자가 구분할 수 있도록 정리해야 한다. 목록을 무조건 넓히지 않고 관리 tuple/legacy 자격을 명시하는 최소 계약안을 다음 macOS 마무리 범위에 포함한다. 기존 진단 문구도 함께 맞춘다. write_new의 미확정 pending 보존과 게시 후 sync 실패는 기존 복구 한계를 유지하며 전원손실 내구성을 새로 주장하지 않는다.


## 이번 실행의 최종 결과와 다음 묶음

R3 보정 후 build12의 격리 활성화, Work·intent가 있는 프로젝트의 update·이전 reader·rollback·재update·repair·detach·보존 기록 조회, official2 정확 요청 설치·자동 프로필·깊은 binding 진단·복구·분리·재개 안내가 모두 기대 결과를 충족했다.29개 CLI 관측,336.301초/600, exit0·process group absent. 깊은 binding은 degraded/exit10으로 진단하고 입력 bytes를 보존했다. 분리 후 resume은 예상한 안내/exit15다. 실제 사용자 설치는 하지 않았다.

이 결과로 구현 및 범위 내 보정을 보존한다. 전체 Work는 Active로 유지하며 완료나 Owner 수락을 기록하지 않는다. R3의 조건부 미통과 원문은 유지한다. B1/B2는 Driver 보정과 오프라인/산출물 근거가 생겼지만 실제 signal과 독립 Reviewer의 보정 후 확인은 아직 없다. Claude 추가5/5, 행동2세션/2·3턴/4·160.620초/720을 사용했고 추가 호출은 하지 않는다. 행동 잔여1턴은 새 세션을 허가하지 않는다.

다음은 잔여 macOS 마무리를 한 묶음으로 재개하는 것이 우선이다. 현재 중단 조건의 재개 범위와 필요한 실행·리뷰 한도를 먼저 합의한 뒤, (1) 고정된 잔여 회귀13/23개, (2) 실제 신호 종료 및 predecessor fixture1개의 제한된 재관측, (3) L01의 설치부터 첫 typed Work까지 연결과 token budget 확인, (4) 관리 runtime의 기계 출력/진단 계약 정리, (5) 통합 결과 리뷰를 연결한다. 이미 통과했고 변경 영향이 없는 검사와 자료는 다시 만들지 않는다. 이 문단은 다음 작업의 제안이며 새 재시험·모델 호출 권한이 아니다. Windows는 공개 전 전체 기능/설치 검증의 별도 필수 단계다.

Adopter 영향: 설치 상태 미확인. 관리·온보딩 개선의 후보는 고정됐지만 전체 qualification과 실제 대상의 설치 identity를 확인하기 전 자동 업데이트를 권고하지 않는다. 실제 대상 적용은 상태 확인·정확 후보·복구 한계와 별도 Owner 승인을 거친다. 실제 설치·adopter·commit/push/PR/merge·공개는 이번에 수행하지 않았다.

보존: 현재 전용 source worktree와 task artifact 경로를 그대로 유지한다. 미커밋 구현, 이전/새 산출물, 실패·시간 한도 원문, callback 반례, 리뷰 입력/원문, 행동 입력/결과는 Owner 검토·남은 검증의 근거 재사용·복구를 위한 자료다. 이 소비가 끝나고 Owner의 보존 조건이 해소될 때 정리 여부를 다시 판단한다. 필수 증거 또는 복구 의존성이 끝났다고 확인된 삭제 대상은 없고, 경로 이동·삭제도 하지 않았다.


마감 확인: Work와 인덱스의 GFM 렌더링·로컬 링크 검사는 통과했고 변경한 tracked 파일의 git diff --check도 통과했다. 이후 추가한 이 문단은 링크·강조·코드 없는 일반 텍스트이며 기존 검사 대상 구조는 그대로다. 변경 source 파일 68개와 필수 실행/리뷰/실패 자료 18개는 durable 경로에서 읽을 수 있음을 확인했다. HEAD는 시작 revision 그대로이고 staged 변경0, Git commit/게시0이다. 추가 승인 구간 누적 318.12분/2040분, 잔여 1721.88분이며 병렬 대기는 한 번만 계상했다. 기존449.29분 비교값과 그 측정 한계는 유지한다. 현재 실행 중인 작업은 없으며 Work 완료·Owner 수락은 보류다.


## macOS 마무리 묶음 승인과 재개 — 2026-11-02

Owner가 상태 출력 보정, 잔여 회귀13/23개, 제한된 실제 신호·predecessor 재검증, 격리 설치부터 typed 첫 Work·재개 연결, 읽기 분량, Claude 계획·결과 리뷰와 범위 내 보정을 한 묶음으로 승인했다. 기존 실패와318.1152분 소비를 이월하고 사용자 대기는 제외한다. 이번 구간은1–2시간 예상·180분 중단 상한, 기존2040분 총상한 안에서 진행한다. 기존 측정된 artifact 약6분, 리뷰 약2분, 잔여 검사와 연결 준비의 불확실성을 반영한 판단치이며 대기 포함·병렬 wall time 중복0이다. 회귀 각 모드 추가1800초, Claude 추가2회 각240초, 행동 추가2세션4턴720초다. 지난 미사용 턴을 새 세션 권한으로 전환하지 않는다.

고정 계수 도구가 없으면 작업 전용 위치에 tiktoken0.13.0/o200k_base만 준비한다. 실제 사용자 설치·adopter·Git commit/push/PR/merge·공개는 계속 보류한다. 통신·권한·종료 불명 실패는 해당 실행을 재시도하지 않고 보존한다. R3 보정의 기존10검사·build12 관리 경로와 영향 없는 증거를 재사용하며 변경된 상태 계약·문서·새 연결 경로만 보강한다. 새 제품/검사 변경 전에 고정한 계획을 Claude에 리뷰한다.

### 마무리 계획 리뷰와 Driver 반영

Claude opus-5-5, 새 세션8931d4ba-7a68-4b10-9dbb-ee515949691a,134.109초/240,exit0·group absent·입력 drift 없음. 구독 claude.ai/firstParty/pro, 도구·시험 허용0. 이번 추가2회 중1회 사용. 정적 리뷰이며 Owner 수락과 별도다. 입력 base e411c4af, packet840ce2cea4c768046295f1aa7ce8589f86f299da4b038f31c3647a4d5bebbfca; untracked 파일은 개별 해시로 식별했다.

~~~text
# Plan review: static only, nothing executed

**Verdict: not ready to execute as written.** The approach and scope hold, and no redesign or budget increase is needed. Apply the corrections below before freezing the source. No additional review of the plan is needed if they are applied as stated.

## Blocking findings

### B1. Item 6: the behavior bridge has no read path
The model has no native filesystem tools, and the bridge only exposes the installed CLI and allowlisted writes. It therefore can't read AGENTS, README, GettingStarted, the conditional guide, or the synthetic target with its quote, link and sentinel. Pre-injecting those files would stop the run from testing onboarding entry.

**Correction:**
- Add one fixed read-only handler, limited to those exact installed entry files, the guide and the synthetic targets.
- Log the read order.
- Have offline bridge validation cover the full read, preview, apply and typed-Work sequence.
- Have offline validation also confirm that non-allowlisted, pre-approval and out-of-range writes are refused.

### B2. Items 2, 5 and 6: reused lifecycle evidence is not unchanged if the guide joins the managed inventory
A new managed file changes the file lists and release identity. Update, rollback, repair and detach then have to add, remove or restore a file they never handled in the reused runs. That leaves a real uncovered risk in those flows.

**Correction:**
- If the inventory changes, run one focused same-artifact sequence on the installed fixture: update from the predecessor, rollback, repair of the guide, then detach. Assert that the guide and its links are correct at each step.
- Cover every profile that ships the file, and declare the Windows inventory impact as unqualified.
- Reuse the other evidence only if the delta shows no dependency on the inventory.

### B3. Items 5 to 7: artifact identity is not precise enough
- **Fixture bytes differ:** a `fixture_root` build has different header and manager bytes, so it isn't the "exact final artifact".
- **Later fixes can detach evidence:** item 7 allows fixes after the behavior and regression runs, which can leave that evidence bound to an older artifact.

**Correction:**
- Record the release and fixture hashes separately, and show that their only difference is the store literal.
- Bind each result to its source and artifact hash.
- After any post-freeze change, record the delta and rerun only the affected consumers.
- If a change affects model-facing entry material, mark the behavior evidence as belonging to the earlier artifact, because the behavior budget has no rerun.

### B4. Item 1: the admission contract is not total, and the negative case is ambiguous
- **`windows-2` has no correct path:** `runtime_supported("windows-2")` uses a separate gate, so support plus tuple can't map it correctly onto the three proposed values.
- **A full copy passes by design:** a complete tree copy with sibling `objects.txt` and `files.sha256` passes `managed_macos_runtime_supported()`, because the location isn't pinned. A negative test for a "copied" interpreter could therefore fail, or could misdescribe what the check guarantees.
- **Failure text misdirects managed users:** the unsupported `next_action` and the `require_supported_runtime` error still point only to the legacy versions. A managed user with a drifted tree would be told to use the wrong remedy.

**Correction:**
- Return `managed-macos-exact-tree` only for a supported darwin process on 3.14.10.
- Add a separate value such as `windows-window-policy` that makes no qualification claim.
- Define the negatives as an interpreter without the matching tree or manifests, plus a one-byte or one-mode drift.
- Document that an exact relocated copy is admitted by tree identity, and that this isn't interpreter authentication or install provenance.
- Update both failure messages to cover the managed path.

### B5. Item 4: the single-shot signal test has a false-failure race
The child uses `Path.write_text`, which creates the file before writing to it. The parent polls `exists()` and then runs `int(read_text())`, so it can hit `int("")`. Under the no-retry rule, that would halt the batch without saying anything about signal behavior.

**Correction:** before the single run, make the parent wait for non-empty content, or have the child publish the file with an atomic rename. Leave the signal assertions unchanged, and record the test hash change.

### B6. Item 2: the token budget isn't reproducible or tied to what users read
- **Encoding data isn't pinned:** tiktoken pins can leave out the `o200k_base` data file, which may be fetched at runtime.
- **The wrong files could be measured:** status directs readers to `payload/docs/README.md`, while the plan's inputs are source files.

**Correction:**
- Hash-pin the encoding file and load it from a task-local cache, with no runtime fetch.
- Fix the encode options, including how special tokens are handled.
- Apply the pass/fail gate to the installed files from the final artifact, for both the AGENTS and CLAUDE entry paths.
- Confirm that the guide is conditional and not reachable as a mandatory fourth read.

## Required clarifications

- **Item 3:** "correct mode" should mean chmod the copied document writable, write it, then restore `0400`. A leftover `0600` could cause a false failure in the single allowed run. Also confirm that the fixture cleanup can remove any copied `0500` directories.
- **Budget:** read "each additional 1800s" as per suite, for 3,600s in total. Read per ID, it would allow up to 18 hours and exceed the 180-minute bundle. Record this reading and enforce the bundle limit as a hard stop.

## Reviewed without blocking findings

- **Items 1 and 4:** the legacy allowlist is preserved, and path derivation adds no second tree verification. Treating a `killpg` `PermissionError` as unknown is the right conservative result, and mocks are not promoted to real signal proof.
- **Items 5 and 7:** old failures and deadlines are retained, the matrix is not presented as a single fresh run, and the review call cap and pending acceptance are preserved.
- **Item 6 and limitations:** the Owner and model roles stay separate, and the stated limitations match the claims being made.

## Review limits

I reviewed only the supplied excerpts and did not independently check the hashes. I did not see `windows_runtime_observation`, the inventory code, the current docs, or the rest of the factory test. B2, B6 and the item 3 cleanup check depend on those unseen parts, so the Driver should resolve them against the frozen source.
~~~

Driver: B1–B6를 반영한다. 실제 설치 파일의 allowlisted read handler와 읽기 순서, 사전 승인·범위 밖 쓰기 거절을 offline에서 확인한다. 새 관리 파일은 추가하지 않고 기존 OPERATIONS.md에 상세를 이동하므로 inventory membership은 유지한다. 배포용/fixture 산출물과 source identity를 각각 기록하고 후속 변경은 영향 소비자를 재검증한다. Windows 경로를 별도 표기하고 exact relocated tree는 위치 인증이 아님을 명시한다. signal ready 파일을 원자적으로 게시한다. 고정 encoding sha446a9538…를 작업 전용 cache에서 offline 사용한다. 이전 원본과 복사한 fixture 모드 보존을 확인한다. 각 mode 추가1800초는 suite 전체 상한이며 합계3600초다. 실제 사용자 설치와 Git은 계속 보류한다.

문서 보정은 진입3문서6798tokens(1129+505+5164)의 읽기 비용을 줄이는 structural Revise다. 상세 명령·제약·버전·권한은 기존 Operations에 보존하고 기존 진입 앵커를 유지한다. 필수 초기 읽기에 상세 전체를 추가하지 않는다.

### 마무리 구현·집중 검증 결과

- runtime 상태는 기존 supported_versions를 유지하고 legacy-version-allowlist 범위, admission_path 및 별도 managed macOS tuple을 표시한다. Windows는 windows-window-policy로 구분하며 지원 자격을 새로 주장하지 않는다. 손상된 전용 Python의 보존·정확 복구 안내를 맞췄다. 집중15검사 통과(42.877초), source admission을 넓히지 않았다.
- Getting Started의 상세 절차는 기존 OPERATIONS.md로 이동했다. 기존 섹션 앵커·명령·권한·복구 조건은 유지하고 inventory membership은 그대로다. 설치된 두 프로필의 AGENTS1129 + README544 + GettingStarted1661 =3334tokens, tiktoken0.13.0/o200k_base(encoding sha446a9538…) offline 계수. canonical3파일 기준은 통과했다. CLAUDE projection151까지 포함하면3485tokens·물리4reads이며, 이를3reads 통과로 적지 않는다. 실제 adapter/manual 탐색의 전체 토큰이나3회 이내 동작을 보장하는 수치도 아니다.
- GFM 강조·파일/앵커 링크8문서와 기존 공통/정밀 문서 검사2개 통과. 최초 새 anchor 검사기는 percent-encoded 한글을 해독하지 못해 실패했고 입력 문서는 정상임을 확인한 뒤 남은 검사만 보정·완료했다.
- 남은 normal13/13(440.283초), parent-O23/23(492.852초) 통과. 현재 신규·이름 변경5개 parent-O도0.677초에 통과했다. 이전 실패와 mode별7199.757/7199.252초를 이월했다. 현재 발견1422−alias20−별도signal1=1401 ID를 대조해 mode별1301개에 유효 근거, Windows100skip, 잔여0으로 연결했다. 이는 재사용+집중+잔여 결과의 합성이며 새 full run이 아니다.
- 실제 SIGINT/SIGTERM1묶음은1.102초에 통과하고 각각 자식 그룹 부재를 확인했다. 준비 파일은 원자적으로 게시해 빈 파일 경합을 없앴다. 미완료 predecessor factory1건은112.547초 통과했다. 복사한 합성 문서만 임시 쓰기 모드로 열고 원 모드를 복원했으며 원본 bytes/mode는 보존했다. 기존9건 근거는 재사용한다.
- build14 public manifest84c8eed6b6ba00c9c3aab55ede0bd89f99d5e42ffa8e96e0ec4516a2cd1bc6bd, fixture manifest3c6323f58a50b4c00a049874b8eecb9117ae6bd04dab0385a805f9df28953f42. payload 차이는 launcher store literal, 관리 logic은 같다. manager config/manifest의 fixture 위치·파생 identity와 bootstrap의 HTTPS 다운로드 대 local asset copy 차이도 명시했다. public delivery는 실행하지 않았다. fixture payload를 검증한 결과를 public bootstrap 실행 결과로 부르지 않는다.
- 격리 bootstrap·2프로젝트 연결·status·View9개 관측 통과. 중간 결과 저장기의 release_ref KeyError는 실제 연결 성공 뒤 발생했다. 성공 prefix를 재실행하지 않고 저장과 남은 프로젝트만 이어갔다. 실행 전 import 이름 충돌·누락 인수도 별도 보존했고 모델/검사 child 소비0으로 구분했다.

### 실제 typed Work 행동 관측과 사용 마찰

기존 A01/A02(2세션3턴160.620초)와 새 구간을 분리한다. L01은 계획·typed intent 미리보기 뒤 명시적 합성 Owner 승인을 받았으나 Work 생성 전 정상 조회의 exit65를 관찰기가 fatal로 처리해 중단했다(1세션2턴57.554초). 통신·권한·종료 불명 실패가 아니며 group absent, 설정·인증 metadata 불변이었다. 원래 STOP와 입력·출력은 보존했다.

정상 미생성 상태만 설명하는 최소 보정 후, Driver가 이미 승인된 정확한 intent와 baseline을 기록했다. L02 새 세션은 실제 active typed Work·계획·현재 파일을 읽고 기존 승인 재요청 없이 Install만 수정·검사·결과 제출했다(1세션1턴55.349초, model gpt-6.1-sol, group absent, 위반0). 결과는 review이며 사용자 결과 수락은 없다. 외부 section의 정상 인용·링크·ID를 보존했고 마지막 답변에 다음 추천과 이유가 있었다.

L02에서는 관찰기의 고정 intent 조회 누락1건과 정상 설명의 “준비 중입니다”를 빈 placeholder로 본 오탐1건도 관측했다. exact intent 조회만 추가하고 전체 Install이 원래 placeholder인지만 판정하도록 보정했다. 오프라인6건 통과, 모델 재시험은 하지 않았다. L02는 완료했지만 L01 중단과 Driver baseline 개입이 있으므로 clean end-to-end 2/2 또는 일반 완료율100%로 보고하지 않는다. 생성 안내의 부정형 설명 반복은 실사용 보완 후보로 남긴다.

이번 행동 소비는 추가2세션3턴112.903초/2세션4턴720초다. 이전 소비 포함4세션6턴273.523초를 보존한다. 세션 한도는 소진했고 남은1턴은 새 세션을 허가하지 않는다. 실제 adopter, native compaction, 공개 다운로드, clean Mac/Gatekeeper, Windows 전체 기능 검증은 계속 별도다. 현재 Work와 Owner 수락은 아직 Active/대기이며 최종 결과 리뷰를 남겼다.

### 최종 Claude 결과 리뷰와 Driver 보정

Claude opus-5-5, 새 세션593bca99-0edf-4547-8a67-354809dac98e,91.012초/240,exit0·group absent·input drift 없음. packet3b034b3ea266a93922e1c27b72d213325aaeaac6175d1a5d03218900b405745d, base e411c4af와 개별 uncommitted 해시를 고정했다. 기존 구독 claude.ai/firstParty/pro, 도구·시험0. 추가2회 모두 사용했다. 판정은 bounded PASS이며 Owner 수락과 배포 자격은 별도다.

~~~text
# Verdict: bounded PASS, no blocking product bugs

This PASS covers only the excerpts and reported evidence for this macOS finalization. I did not recompute any hashes or see the full diff. It isn't Owner acceptance, release readiness, or evidence of general quality.

## Prior findings
- **B1 and B5:** Closed. The excerpts show the read handler, and the test's atomic readiness publication removes the race. `run_lifecycle` keeps flag-only signal handlers in place during cleanup and reports the child group as closed only after `killpg(pid, 0)` returns `ProcessLookupError`.
- **B2:** Closed on the reported evidence. Detail moved to OPERATIONS, and the Driver reports that old anchors and managed membership are unchanged.
- **B3:** Closed by reported evidence. Rejecting the "differ only by a literal" claim is correct. Fixture delivery does not prove public transport, and the limits say so.
- **B4:** Closed.
    - `runtime_admission_path` only describes an already computed result and cannot widen the gate.
    - The legacy allowlist and Windows path stay separate.
    - An exact relocated copy is admitted, and this is correctly described as tree identity, not authentication.
    - `managed_macos_runtime_supported` fails closed on the variations visible in the excerpt.
- **B6:** The gate is met only as the fixed three-file maintenance budget, and it must not be read as an onboarding limit. See non-blocking finding 2.

The reported totals reconcile:

| Evidence | Reconciliation |
|---|---|
| Collection | 1401 + 20 + 1 = 1422 |
| Test IDs | 1397 − 1 + 5 = 1401, and 1301 + 100 = 1401 |
| Tokens | 1129 + 544 + 1661 = 3334, and 3334 + 151 = 3485 |
| Behavior time | 57.554 + 55.349 = 112.903, and 112.903 + 160.620 = 273.523 |

## Non-blocking findings

### Documentation and evidence corrections
1. **README wording conflicts with the clone-free path.** `README.md` says "Fresh setup uses an independent trusted source and the explicit `continuation-1` profile", while Getting Started separates source setup from managed bootstrap.
    - **Fix:** Change the sentence to "Source-based fresh setup uses an independent trusted source and the explicit `continuation-1` profile; the macOS managed candidate uses the bootstrap procedure in Getting Started."
    - **If applied:** Rerun the token and document checks, and update the identity hashes.
2. **The token disclosure omits OPERATIONS.** B2 kept the budget by moving install detail there, and Getting Started sends installers to it. The disclosure lists only adapter and manual reads as outside the measurement.
    - **Fix:** Add this sentence to the evidence: "Procedure-triggered OPERATIONS reads are also excluded; actual installation-path read cost is unmeasured."
3. **The assessment verdict reads stronger than the run.** `PASS_WITH_OBSERVER_LIMITATIONS` understates that L01 stopped and the Driver recorded the baseline. The detail fields are honest, but the top-level label could be quoted alone.
    - **Fix:** Rename it `RESUMED_COMPLETION_WITH_DRIVER_INTERVENTION`.

### Test and evidence gaps
4. **The corrected observer has no model retest.** Its offline checks are the only evidence for the correction, and the session cap rules out a retest in this segment. This remains an open limit.
    - The placeholder oracle accepts a section that keeps the placeholder alongside the four keywords, so it shows only that the sections are distinguishable, not content quality.
    - Pre-start `show` relies on `.hrn/work/first-work` being the real Work location. This excerpt can't confirm that path, and if it's wrong, the guard never triggers.
5. **Bridge hashes may not match the runs.** The identity binds the post-run `bridge.py`, but L01 and L02 ran on earlier observer versions. Unless the manifest already records the per-session hashes, label the current hash as post-correction only.
6. **The offline oracle baseline can drift.** `Bridge('offline')` takes its original from `live/README.md`, which L02 edited. The outside-section bytes still compare correctly, but this is not a pristine baseline.
7. **Full-tree hashing latency is unmeasured.** `managed_macos_runtime_supported` rehashes the full tree on each gate call. This is an intentional design with no writable stamp, so it's not a defect, but the evidence gives no latency figure for an interactive `./colvia view`.

### Product follow-up
8. **Generated prose repeats negative qualifications.** Keep this as a usability follow-up, as you proposed. One synthetic trace is not enough to change product policy.

## Still unproven
- **Distribution:** public transport, a clean Mac, Gatekeeper, and the entire Windows public scope.
- **Behavior:** first-pass model end-to-end runs, behavior in a fresh post-submission session, native platform compaction, and actual adopter quality.
- **Test qualification:** a fresh full-suite run on the current artifact. The composed evidence is acceptable for this review because the changes are focused and the manager SHA is reused exactly, but it can't be reported as full qualification.
- **Unsupported operations:** shared-runtime removal and store repair.

The source Work stays Active. Owner decisions, installation, commit, push, PR, merge, and publication all remain withheld.
~~~

Driver: 지적1 README의 source-based setup/관리형 bootstrap 구분을 반영한다. 지적2 canonical 토큰 측정에는 절차에 따라 읽는 OPERATIONS도 포함되지 않으며 실제 설치 경로 전체 읽기 비용은 미측정임을 명시한다. 지적3 L02 이름을 RESUMED_COMPLETION_WITH_DRIVER_INTERVENTION으로 보정했다. 지적4 oracle은 범위·구조 확인이고 내용 품질을 자동 보장하지 않는다. actual .hrn/work/first-work와 source 계약을 대조하며 모델 재시험은 없다. 지적5 원래 session별 identity와 실행 당시 bridge 원문 사본의 해시를 대조해 일치함을 확인했다. 현재 bridge 해시는 post-model 보정만 가리킨다. 지적6 offline baseline은 다른 live 파일 대신 자체 보존 original을 사용하도록 보정한다. 지적7 이미 측정된 두 fixture View의 전체 process wall time을 추출하되 hashing 단독·일반 interactive 성능으로 부르지 않는다. 지적8 부정형 설명 반복은 기존 실사용 보완 사항으로 유지한다.

README만 바뀌는 후속 build15의 source/payload 차이를 고정하고 해당 문서·토큰·배포 산출물 소비자만 확인한다. 회귀와 L01/L02는 원래 identity의 관측이며 새 모델 관측으로 재표기하지 않는다. source Work의 수락·완료 및 실제 설치·Git 게시·공개는 계속 보류한다.

### 리뷰 후 보정 확인과 보존

build14→build15의 두 profile/public·fixture payload 대조에서 변경 파일은 README.md 하나뿐이었다. 최종 canonical 계수는 AGENTS1129 + README559 + GettingStarted1661 =3349tokens, CLAUDE151 포함3500tokens다. 변경 없는7문서 hash와 기존 공통/정밀 검사 근거를 재사용하고 README GFM/링크·설치된 bytes·두 profile 계수만 확인했다. 별도 reader1개에서 bootstrap·preview·apply·status·View5개 관측이 통과했다(14.314초). 해당 실행기 마지막 출력의 “Two”는 이전 template 문구이며 실제 결과 목록5개/reader1개를 기준으로 기록한다. 모델은 재호출하지 않았다.

최종 public manifest99195df10261d6a92e8bcd239c1899e270a27f076efd471030ef75a2f3e81d37, fixture manifest30ebca1f93e3fe2a297756eedc52a7dff3cb0804bc7578204d22bcc910bf4910. public continuation release d45fe0b9e7340034e97a67ac314b2931eb83ddafbbd7f5740fd122c4011f8233, official2 7f7cda4e62f436d7f29765048d14f145dab47bbf96b55a6142269f10bd888715. L01/L02는 build14 관측으로 유지한다. source README 보정과 post-model 관찰기 baseline 보정은 결과 리뷰 이후 Driver가 좁은 검사를 수행했으며 별도 Claude/모델 재리뷰는 없다.

기존 오류·STOP·per-session input identity와 실행 당시 bridge bytes를 보존했다. offline은 자체 saved original을 읽고 실제 Work directory가 guard의 경로와 일치함을 확인했다. 기존 fixture View2회 wall time은4.257/4.348초다. 당시 회귀검사와 병행한 두 관측으로, full-tree hashing 단독 시간이나 일반 interactive 성능으로 해석하지 않는다. 모든 완료 실행의 그룹 부재와 2026-11-02T00:30:39Z 작업 경로 프로세스0건을 확인했다.

보존 대상은 현재 source worktree, 원 실패/수락·회귀 근거, build14 행동 fixture/관측 입력, 최종 build15 공급/산출물, 고정 tokenizer/encoding 및 review 기록이다. 현재 소비자는 Owner 수락 검토와 남은 자격 확인 계획이다. 사용자 명시 외부 증거 보존 조건을 유지하며, 해당 검토와 재사용 필요가 끝날 때 작업 소유권·복구 가능성을 확인해 정리한다. 활성 경로 이동·삭제·Git 변경은 하지 않았다.


## 첫 작업·제출 후 재개 마무리 승인 — 2026-11-02

Owner가 첫 작업의 모델 계획/승인/baseline/수정/검사/제출과 새 세션 조회를 한 묶음으로 승인했다. 기존2040분 안에서 이번90분, 예상25–45분(기존 근거 재사용에 따른 판단; 대기 포함), 행동 추가3세션5턴1080초와 Claude2회×240초. 실패·소비량을 이월한다. 완료한 회귀·signal·predecessor·문서 검사는 재사용하고 변경된 관찰기와 미완료 흐름만 집중 확인한다. 통신·권한·종료 불명 실패는 재시도하지 않는다. 실제 설치·adopter·Git 게시·공개는 보류하며 Windows는 공개 전 필수다. Source Work 결과 수락과 Done은 이번 실행 승인과 별개다.


### 행동 마무리 R0 계획 리뷰와 처분

Claude claude-opus-5-5, fresh session 6407691a-072e-4127-a52f-b4a296b2c943, 기존 구독, 도구/시험0, 172.136초/240, exit0·group absent·drift0. 정적 판정 CHANGES_REQUESTED. 사용자 명시 승인으로 합성 관찰기 코드와 계획을 비식별 전송했다.

~~~text
# 판정: CHANGES_REQUESTED

계획의 순서, 예산 총량, 권한 경계와 과거 실패 기록 보존 방침은 타당합니다. 다만 L01 실패와 같은 유형의 경로가 남아 있고, 예비 세션이 현재 구조로는 실행되지 않으며, B02 증거도 오판될 수 있어 이대로 실행하면 안 됩니다.

정적 검토만 했고 CLI, `hv2ref`, `matrix.sb`는 패킷에 없습니다. 따라서 CLI 동작과 store 결정 방식에 관한 내용은 추정이며, 구현 전에 계약을 확인해야 합니다.

## 실질 지적

### 1. 사전 조회가 세션을 다시 중단시킬 수 있음 (차단)
- **문제:** 수정된 것은 `work('show')`뿐입니다. `read()`의 `view work first-work`와 `view continuation first-work`는 baseline 전에도 실제 CLI로 바로 갑니다.
- **영향:** CLI가 0이 아닌 코드로 끝나면 `RuntimeError`로 세션이 끝납니다. `project_read` 설명이 이 경로들을 광고하고 있어, 모델이 정상적으로 호출할 수 있습니다.
- **계획이 키우는 위험:** 2단계에서 `view intent first-intent`까지 광고하면, propose 전 조회도 같은 실패를 낼 수 있습니다.
- **최소 수정:**
  - Work와 continuation 조회는 baseline 전이면 `show`와 같은 not-started 결과를 돌려줍니다.
  - Intent 조회는 draft 전이면 not-started 결과를 돌려줍니다.
  - baseline 후의 누락이나 손상은 계속 치명적 실패로 둡니다.
  - 4단계 oracle에 `project_read`의 세 경로를 사전 상태와 사후 손상 상태로 나눠 추가합니다.

### 2. PLAN이 없을 때의 처리와 바인딩 순서 (차단)
- **읽기:** `PLAN.md`가 없으면 `read()`가 `FileNotFoundError`를 내고, 이는 `Refused`가 아니라서 세션이 끝납니다.
- **propose:** PLAN 없이 호출하면 draft와 prepare를 수행한 뒤에야 `read_bytes()`에서 실패합니다. 이때 부작용이 이미 남습니다.
- **바인딩:** `plan_sha`를 prepare 뒤에 계산하므로, 2단계의 PLAN ref를 그대로 넣을 수 없습니다. fixture에 PLAN.md가 미리 있으면 모델이 쓰지 않은 파일에 바인딩될 수도 있습니다.
- **최소 수정:**
  - 계획 단계에서 PLAN.md가 없으면 읽기 결과를 `absent`로 돌려줍니다.
  - PLAN 쓰기 성공 시 상태를 기록하고, `proposal()` 첫머리에서 이 상태를 확인한 뒤 해시를 계산합니다.
  - 같은 해시를 prepare와 Work에 사용합니다.
  - prepare가 ref를 지원하지 않으면 "Work에서만 바인딩"으로 기록하고, intent 바인딩을 통과로 표시하지 않습니다.

### 3. 관찰자 상수 교체가 일부만 되면 판정이 약해짐 (차단)
- **문제:** `L01/L02`, `2/4/720`, `range(2 if case=='L01')`, 제출 확인, `L01/assessment.json` 게이트, `input.json`의 limits가 모두 하드코딩되어 있습니다.
- **영향:** 이름만 B01로 바꾸면 B01이 1턴으로 끝나고 미제출도 통과합니다.
- **최소 수정:** 관찰자 맨 앞에 case 표를 둡니다.
  - 각 case의 턴 수, submitted 필요 여부, 선행 평가를 표에서 읽습니다.
  - 예산 한도 `3/5/1080`과 이전 사용량은 `authorization.json`에서 읽습니다.
  - 정적 검사로 옛 상수가 남지 않았음을 확인합니다.

### 4. 예비 세션이 현재 구조로는 실행 불가 (차단)
- **STOP 차단:** `STOP.json`이 있으면 관찰자가 무조건 중단하고, 내용도 항상 `retry:false`입니다.
- **프로젝트 재사용 불가:** `Bridge`는 `offline`과 `live`만 받습니다. 이미 사용한 live의 상태와 파일은 처음부터 다시 쓸 수 없습니다.
- **범위 미정의:** "결정적 범위 내 수정"의 범위가 정해져 있지 않습니다. 제품 소스를 고치면 1301 PASS 재사용 근거도 사라집니다.
- **최소 수정:**
  - 1단계에서 미사용 `reserve` 프로젝트와 상태 파일을 미리 만듭니다.
  - 수정 범위는 bridge, observer, fixture 배선으로 한정합니다. 제품 소스를 고쳐야 하면 예비 세션을 쓰지 않고 중단합니다.
  - 기존 STOP은 그대로 두고, 실패 B-case의 STOP 해시와 `deterministic` 분류를 담은 별도 재개 기록을 Driver가 작성합니다. 이 기록이 있을 때만 예비 case를 1회 허용합니다.
  - 통신, 권한, 종료 불명 실패에는 재개 기록을 만들 수 없게 합니다.
  - 시작 시 `admission-stop.json`도 함께 검사합니다.

### 5. 새 store 격리를 패킷으로 입증할 수 없음 (차단)
- **store 선택:** `call()`의 환경에는 실제 `HOME`만 있고 store 선택 값이 없으며, `matrix.sb`도 매개변수 없이 재사용합니다. 새 store가 실제로 선택되고 쓰기가 허용되는지 알 수 없습니다.
- **경로 마스킹:** 관찰자는 옛 `$COLVIA_STORE` 경로만 가립니다. 새 경로가 다르면 사설 경로 guard에 걸려 세션이 끝납니다.
- **Work 존재 확인:** `.hrn/work/first-work` 검사는 Work 기록이 외부 store에 있으면 아무것도 검출하지 못합니다.
- **고정 경로:** `HOME`, `build-14`, `continuation-1`도 함께 바꿔야 합니다. `self.release`가 없으면 `rglob`이 조용히 빈 결과를 내므로 시작 시 존재를 단언합니다.
- **최소 수정:** 4단계에 다음을 추가합니다.
  - 새 store에만 기록되는지 확인합니다.
  - 옛 store, 공개 build15, 사용자 기본 store의 해시나 트리가 그대로인지 확인합니다.
  - 마스킹이 새 경로에서 동작하는지 확인합니다.
  - 사전 Work 부재 판단을 실제 Work 위치 또는 typed 조회로 합니다.

### 6. B02의 신선도와 읽기 증거가 오염됨 (차단)
- **읽기 기록:** `read_order`는 상태 파일에 누적되어 B01의 읽기까지 포함하고, `show`는 기록하지 않습니다. B02가 아무것도 읽지 않아도 증거상 읽은 것처럼 보일 수 있습니다.
- **판정 기준:** `status='observed'`는 도구 호출이 없어도 성립합니다.
- **유도 문구:** `show`의 `result_acceptance: pending Owner decision`은 제품 기록이 아니라 bridge가 붙인 문구입니다. B02 개발자 지침의 "second turn"과 도구 설명의 "Fresh resume"도 이전 흐름을 암시합니다.
- **최소 수정:**
  - B02 판정은 그 run의 `trace.jsonl`만 사용합니다.
  - 해당 run에서 typed Work, PLAN, README를 읽은 tool_result가 없으면 FAIL로 합니다.
  - `show`의 해당 문구를 제거하고, 수락 대기 상태는 typed 필드로 확인합니다.
  - B02 지침과 도구 설명은 중립화합니다. 중립화하지 않으면 그 문구들을 평가의 한계로 명시합니다.

### 7. 수락 기록에 "approval pending"이 남을 수 있음 (중요)
- **문제:** prepare의 `reason`이 ticket에 고정되면, 승인 후 intent 기록에도 `approval pending`이 남을 수 있습니다. `owner_statement`는 상태 파일에만 있습니다.
- **영향:** 2단계에서 intent 조회를 광고하므로, B02 모델이 이미 승인된 intent를 미승인으로 오독할 수 있습니다.
- **최소 수정:** `reason`을 승인 전후 모두 참인 문구로 바꿉니다. 예: `Synthetic Owner decision on exact intent`. 4단계에서 실제 조회 결과에 모순이 없는지 확인합니다.

### 8. 사소한 입력 차이가 안전 중단으로 처리됨 (경미)
- **문제:** 읽기는 `./` 접두사를 정규화하지만 쓰기는 하지 않습니다. `./PLAN.md` 쓰기는 안전 위반으로 처리되어 세션이 끝납니다.
- **문제:** PLAN의 키워드 검사(`README`, `설치`)도 위반으로 처리되므로, 영어 "Install"만 쓴 계획이 안전 중단이 됩니다.
- **최소 수정:**
  - 쓰기 경로를 읽기와 같이 정규화합니다.
  - PLAN 키워드 거부는 안전 위반에서 제외하고 교정 가능한 응답으로 돌려줍니다.
  - 범위 밖 쓰기와 권한 위반은 계속 치명적으로 둡니다.

## 수정 없이 유지
- 과거 실패와 복구 기록, "offline 수정이며 clean model pass 아님"이라는 구분은 그대로 둡니다.
- 예산 3세션 5턴 1080초는 B01, 예비 세션, B02를 모두 실행해도 충분합니다.
- 전체 회귀를 다시 돌리지 않는 결정은 제품 소스가 그대로일 때만 유효합니다.
- 실제 설치, Git, 공개 작업 제외와 Windows 공개 범위 필수 조건은 유지합니다.
- 결과 수락 도구가 없고 Work가 Owner 수락 전까지 Active로 남는 구조는 적절합니다.

1~7번을 반영한 뒤 최종 Claude 정적 검토에 정확한 입력을 다시 제출해야 합니다. 이 판정은 실행 권한이나 Owner 수락을 뜻하지 않습니다.

~~~

Driver 처분: 1–4·6–8 반영. 사전 Work/continuation/intent 조회, 계획서 작성/정확한 ref, case별 한도/선행 조건, reserve 격리/실패 보존, 새 세션 중립 지침·run별 근거, 승인 reason, 정상 경로 표기를 관찰기에 보정한다. 제품 소스는 유지한다. 5는 고정 fixture launcher/store literal·실제 typed 위치·새 store 실행과 기존 경계로 확인한다. 사용자 기본 store 내용은 읽거나 변경하지 않으며 전체 tree 동일성을 주장하지 않는다. 모델 재실행 전 오프라인 검증을 거친다. 최종 결과 리뷰는 실제 근거와 보정된 정확한 입력을 검토한다.


### 행동 마무리 R1 결과 리뷰와 Driver 처분

Claude claude-opus-5-5, fresh session df6f0bb3-82c2-496c-bc4e-29a70fc72ab2, 기존 claude.ai Pro/firstParty 구독, 도구/시험0, 150.642초/240, exit0·group absent·input drift0. 아래는 정적 리뷰 원문이다.

~~~text
# 판정: bounded PASS (Owner 결과 수락은 별도)

코드와 제공된 증거에서 차단 결함은 찾지 못했습니다. 다만 B02 필수 기준 하나는 이 묶음만으로 확정할 수 없어 아래 조건을 붙입니다. 범위는 고정 합성 프로젝트의 첫 Work와 새 스레드 읽기 전용 재개이며, 실제 사용자 설치, 일반 채택자 품질, 자동 compaction, 공개 배포 준비 완료의 증거는 아닙니다.

## 판정 조건
**B02의 Work/continuation 조회 근거가 묶음에 없습니다.** `fresh_trace_reads` 7개에는 `view work`와 `view continuation`이 없는데, `actual_work_and_continuation_read_this_session`은 `true`입니다.
- **가능한 설명:** `project_work show`가 별도 도구 호출이라 목록에서 빠졌을 수 있습니다. 응답의 `first-2`, `review`, 빈 `evidence_refs`, 후속 미정도 이를 뒷받침하지만, `view --details`나 intent 조회만으로 나온 내용일 가능성을 배제하지 못합니다.
- **확인 방법:** `B02/trace.jsonl`에서 `project_work {action: show}` 호출과 성공 결과를 확인합니다. 모델을 다시 호출할 필요는 없습니다.
- **판정 영향:** 호출이 없으면 B02는 FAIL, 전체 판정은 CHANGES_REQUESTED입니다.

## 차단 결함
없습니다. 다음 경계는 코드상 fail-closed로 확인했습니다.
- **승인 전 차단:** 승인 전 시작과 쓰기가 막히고, 제안 후에는 PLAN을 수정할 수 없습니다.
- **쓰기 범위:** baseline 이후 README 쓰기는 Install 구역으로 제한됩니다.
- **제출 조건:** 현재 바이트에 대한 검사 통과가 필요하며, 결과 수락 경로는 없습니다.
- **중단 동작:** CLI 실패, 예상 밖 native item, 프로세스 종료 불명, 입력·설정 변경 시 재시도 없이 중단합니다.

## 증거 문구 수정 (비차단)
1. **기본 저장소 주장이 과합니다.** `sandbox-exec`는 `Bridge.call`에만 적용됩니다. `verify_workspace_product`, `snapshot`, `make_manifest`는 observer 프로세스에서 샌드박스 없이 실행되므로, 이 코드만으로는 "not read or written"을 입증할 수 없습니다. 해당 함수의 저장소 해석을 확인하기 전까지는 "샌드박스 CLI 경로 기준"으로 좁혀야 합니다.
2. **"installed" 범위가 넓습니다.** CLI는 설치본이지만 `record_ref`와 manifest 계산은 `SOURCE/src`의 `hv2ref`를 씁니다. 따라서 "설치된 CLI와 소스 helper의 조합"이 정확합니다.
3. **B02의 `read_order`는 근거로 쓰면 안 됩니다.** `live-state.json`을 이어 쓰므로 B01의 읽기까지 누적됩니다. assessment처럼 trace만 근거로 삼아야 합니다.
4. **`os_log_queries: 0`은 거부 로그가 없다는 증거가 아닙니다.** `denials=None`이 고정이라 조회 자체를 하지 않습니다.

## 한계
- **B02의 다음 행동 추천은 독립 판단이 아닙니다.** Work show의 합성 힌트는 제거됐지만, `next_action`, `observed_scope`, `unavailable_scope`는 bridge가 고정 작성한 값이고 실제 CLI를 통해 그대로 조회됩니다. PLAN이 뒤처졌다는 판단과 `evidence_refs` 부재 지적은 모델 판단의 근거가 더 강하지만, Owner 검토 추천과 미검증 범위 설명은 이 값을 따랐을 수 있습니다.
- **B02의 "새 실행 없음"은 구조적 결과입니다.** 쓰기·검사 도구를 주지 않았으므로 모델의 자제력 증거가 아닙니다. 도구 설명이 `first-work`, `first-intent`를 알려주고 프롬프트도 읽을 대상을 지정하므로, 스스로 찾아낸 재개도 아닙니다.
- **B01의 승인은 각본입니다.** 2턴 승인은 모델 응답 내용과 무관하게 진행됩니다. 필수 참조 불일치를 알린 점은 좋지만, Owner가 그 고지를 보고 판단했다는 증거는 아닙니다. intent 내용과 필수 참조도 모델이 아니라 bridge가 고정했습니다.
- **`project_check`는 약한 검사입니다.** 부분 문자열과 바깥 구역 바이트만 확인하므로 의미 품질은 수동 읽기에 의존합니다. 제공된 README에서 4단계와 Keep 구역은 확인했지만, 설치 안내와의 정확성은 안내 원문이 묶음에 없어 Driver 주장으로만 남습니다.
- **README는 설치 실행 안내로 부족합니다.** 구체적인 명령 없이 배포본 안내로 넘기고 자격 문구가 많습니다. 정직한 표현이지만 사용성은 측정되지 않았으며 UX 후속 과제입니다.
- **미제공 파일은 검증하지 못했습니다.** `authorization.json`, `ledger.json`, `inputs/identity.json`, trace, `matrix.sb`, stdio/endpoint 모듈, `official_policy`가 해당합니다. 예산은 보고값 기준 2세션, 3턴, 122.5초이며 reserve는 쓰지 않은 것으로 보입니다.

## Driver preflight 결함
- **유지할 기록:** 비교 oracle이 끝나기 전에 B01을 시작한 것은 실제 절차 결함입니다. 이후 차이가 저장소 지정 한 줄뿐임이 확인되어 결과를 무효로 볼 사유는 아니지만, "무결한 준비"나 "사전 검증 완료"로 표현하면 안 됩니다.
- **입증 범위:** `ATTEMPT-STARTED`의 해시는 `inputs/identity.json`만 묶습니다. `fixture-identity.json`의 비교 결과가 시작 전에 확정됐다는 뜻은 아닙니다.
- **권장 확인:** `B01/project-before.json`의 `colvia` 해시가 build16 payload와 같은지 대조하면, 시작 시점 launcher까지 사후 사슬로 연결됩니다.

## 잔여 코드 정리 (재사용 시만)
- `selected['project']`와 선택된 case의 프로젝트가 일치하는지 검사하지 않습니다.
- 턴 예산 확인보다 `bridge.approve()`가 먼저 실행됩니다.
- `read_key`, `guide`/`reference` 입력, `check()`의 `prefix`/`suffix`가 사용되지 않는 잔여 코드로 남아 있습니다.
- 이번 일회성 실행의 결과에는 영향이 없습니다.

## 남은 차단 조건
- **판정 유지:** B02 trace의 `project_work show` 확인이 필요합니다.
- **수락:** Owner의 결과 수락은 아직 이루어지지 않았습니다.
- **공개 배포:** Windows 전체 릴리스 범위가 아직 남아 있습니다.

정적 검토만 수행했으며, 도구나 테스트는 실행하지 않았습니다.

~~~

Driver 처분: bounded PASS의 유일한 조건인 B02 project_work show 호출과 성공 결과를 해당 trace의 연속 두 행에서 확인했다. Work와 continuation 실제 출력이 함께 있으며 추가 모델/CLI 호출 없이 조건을 충족했다. B01 시작 snapshot의 launcher도 build16과 일치했다. 제품 소스 수정은 없다. 설치 CLI와 동일 bytes의 source helper를 조합한 합성 관측으로 한정한다. 기본 사용자 store 전체 접근 감사와 OS 거부 로그 조회는 수행하지 않았으며, 새로운 쓰기 도구가 없는 B02는 모델의 자제력 증거가 아니다. 합성 Owner 승인·고정 intent/next_action·지정 조회 경로가 있는 시나리오여서 독립 추천/자율 탐색/실제 Owner 판단을 입증하지 않는다. 계획서/README의 의미 정확성은 Driver 수동 대조이며 Reviewer는 설치 안내 원문을 검토하지 않았다. 재사용 시 observer case-project 결합·턴 확인 순서·잔여 코드 정리를 다시 확인한다. 이번 결과에 영향을 주지 않는 정리를 위해 모델 재시험하지 않는다. 제품 설치 안내의 실제 명령 사용성·기술 표현·한계 문구는 실제 적용 검증의 후속으로 유지한다.

### 행동 마무리 실행 근거·한계

B01 gpt-6.1-sol 새 세션2턴97.183초, B02 별도 새 세션1턴25.305초. 실제 CLI15호출 모두 exit0·stderr 없음·group absent. 입력42개와 config bytes/auth metadata가 유지됐다. 설치 CLI와 byte-identical source helper를 함께 사용했으며 OS 거부 로그는 조회하지 않았다. B02 평가는 해당 run의 trace만 사용했고 Work/continuation·PLAN·README·승인 intent 조회 및 파일/모드 불변을 확인했다. PLAN의 비필수 참조 제안과 고정 브리지의 필수 티켓 차이는 첫 턴에서 공개됐고 정확한 두 번째 합성 Owner 승인 이후 실행됐다. README 네 단계의 내용은 Driver가 설치 안내와 대조했다. 구조·키워드 검사만으로 품질을 판정하지 않았다. 결과 수락은 실행하지 않았다.

이번 준비 과정에서 전송 전 경로 필터·관찰기 생성 구문·공백 경로 shell quoting 비교 오류를 보존했다. fixture 비교 완료 전 모델 B01을 시작한 순서상 흠이 있었다. 실행 입력은 처음부터 동일했고 정적 diff 및 보정 비교에서 단일 store assignment만 다른 것을 확인했으므로 모델 관측은 제한된 근거로 유지한다. 전체 준비 과정이 무결점이었다고 보고하지 않는다. 기존 실패를 새 PASS로 덮거나 모델을 재시도하지 않았다.

보존: 현재 worktree와 이번/이전 external artifact는 Owner 결과 수락·공개 전 자격 확인·실사용 후속 비교·실패 복구의 소비 경로다. 명시된 외부 증거 보존 조건을 유지하며 활성 경로 이동/삭제는 하지 않았다. 격리 CLI는 고정 fixture store를 대상으로 했다. 샌드박스 밖 source helper를 포함한 기본 사용자 store 전체 접근 감사는 미수행이며 전체 tree 동일성은 주장하지 않는다.

이번 계상 21.5880/90분(실측 구간+사전 읽기 보수 예약5분, 대기 포함); 기존 carry 363.6447분. 종료 문서 검사 이후 ledger의 최종값을 기록한다. 실제 설치·adopter·Git 게시·공개0.


## Owner 결과 수락과 source 완료 — 2026-11-02

Owner의 “수락한다”에 따라 이 Work를 Done으로 정리했다. 수락 대상은 앞서 보고한 macOS 배포·관리·온보딩 구현, 지정 격리 검증, B01 첫 작업 및 B02 새 세션 읽기 전용 재개, Claude 계획·결과 리뷰와 범위 내 보정이다. 제품 소스는 마지막 검증 baseline과 같으며 이전 실패·준비 순서 한계·모델/검사 소비량·원 증거를 유지한다. 실행 종료 후 계상은 이번22.7104분/90분, 추가2040분 중 누적386.3551분이며 사전 읽기 보수 예약5분을 포함한다.

이 수락은 실제 설치·clean Mac/Gatekeeper·공개 다운로드·adopter 적용·Windows 전체 기능 자격·자동 컨텍스트 압축 문제 해결·일반 사용자 품질을 뜻하지 않는다. Windows 전체 공개 범위 검증은 공개 전 필수다. 실제 설치·adopter·commit/push/PR/merge·공개는 계속 보류한다.

Adopter 영향: source에 배포·관리·안내 개선이 있으나 실제 설치 상태는 이번에 확인하지 않았다. 실제 적용은 정확한 배포본과 대상별 별도 승인·검증을 따른다. 사용성 후속과 공개 전 자격 한계는 위 현재 결과에 유지한다. 새로운 보강 제안 검토는 완료된 구현을 다시 여는 행위가 아니며 구현 승인과 구분한다.

Development index는 이 수락/완료 절을 가리키는 탐색 링크만 갱신했다. source Work·기존/이번 external 자료는 향후 정확한 Git 범위 검토, 공개 전 자격 확인, 실패 비교와 명시된 외부 증거 보존의 소비 경로로 유지한다. 활성 경로 변경/삭제는 하지 않았다.
