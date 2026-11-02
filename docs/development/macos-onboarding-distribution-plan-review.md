# macOS Onboarding Distribution Plan Review

계획 리뷰 정본. Owner가 공급 조건 구체화와 Claude R0를 승인했다. 제품 구현·통합·설치·Git·게시·adopter 적용은 보류한다. 계획 초안과 Reviewer 원문, Driver 처분을 이 문서에 구분해 기록한다. 비공개 자료의 원문/경로는 전송하거나 이 문서에 기록하지 않는다.

# Colvia macOS 배포·관리·첫 사용 통합 계획

2026-11-01 KST · 계획 초안 r3 · 공급 조건/R0 검토 · 실행 승인 전

이 문서는 현재 채팅에서 요청한 계획 산출물이다. 구현·통합·제품 시험·Claude 전송·설치·게시·실제 adopter 적용을 승인하거나 시작하지 않는다. formal R0를 진행할 때는 source Workflow의 Preliminary Review Location을 따르고, 실행 승인 후 하나의 새 source Work가 진행을 소유한다. 완료한 View Work나 가드레일 원장에 새 작업의 진행을 섞지 않는다.

## 1. 판단과 확인한 입력

추천은 로그인/clone 없는 공개 설치 경로를 목표로 설계하되, 실제 게시와 저장소 공개는 별도 결정하는 것이다. private 전용 인증 installer를 먼저 만들지 않는다. 이번 사용자 선택에 따라 필요한 Python을 전용 위치에 자동 준비한다. 사용자의 시스템 Python·전역 설정을 변경하는 방식은 기본안이 아니다.

- View: 수락 da3e20d329e88b998d141c76ff3b3ff66d6f707d, merge e411c4af9df0402b4542600d3e9cdc8624c9a15e. 로컬 main/origin-main이 이 객체이며 실제 원격을 이번에 갱신하지 않았다. source 작업 트리는 깨끗하고 수락 커밋에 있다.
- Guardrails 정본: [private evidence location retained by Driver] 마지막 Owner Acceptance And Main Continuation 절이 현재 상태다. 앞의 수락 미확인 문구는 역사다.
- S1b는 trusted-local 전제의 제한된 payload 전달/쓰기 검사·합성 검증·지정 native worker/probe·취소/부분 전송 E2E·정적 리뷰와 Low7 한정으로 수락됐다. 일반 desktop/독립 승인/provider 전체 보호·실자료·새 설치 자격의 수락은 아니다.
- Guardrails 기준은 ff299095ba450ef199392ce2f6d92ee5e8f3918b. 47개 변경 patch/mode manifest와 수락 문서 추가문을 합쳐 사용한다. 현재 46개는 원 manifest와 같고 1개는 owner-acceptance.json의 source_after와 같다. patch와 최종 handoff digest도 일치했다. 이 확인은 읽기 전용 identity 대조이며 복원/통합/제품 시험이 아니다.
- 공통 7개 파일: AGENTS.md, adapters/colvia-work/SKILL.md, colvia, docs/GETTING-STARTED.md, docs/REFERENCE.md, src/hv2ref/cli.py, src/hv2ref/view.py. 핸드오프의 기준 줄 구간 교집합은 없지만 의미 결합과 실제 merge 성공은 미검증이다.
- 과거 candidate-handoff는 S1a 후보이며 최신 S1b+View 배포본이 아니다. 새 통합 후보를 준비해야 한다.
- 현재 관측 가능한 host는 macOS arm64다. 첫 qualification은 고정된 macOS/arm64/runtime 조합에 한정하고 Intel/Windows 지원을 자동 주장하지 않는다.

## 2. 사용자 경험과 범위

사용자는 저장소 clone이나 GitHub 계정 없이 공개 배포본을 받는 명령으로 시작한다. Git은 Git 기반 첫 작업의 보존 도구로 설명하며 배포본 획득 조건으로 삼지 않는다. 정확한 다운로드 주소·도메인·버전 정책은 R0 입력으로 고정하고 지금은 실제 URL을 만들거나 공개하지 않는다.

흐름: 배포본 획득/검증 → 전용 Python/관리 도구 준비 → 프로젝트 확인 → 설치 미리보기/승인/적용 → 목표/계획 → 첫 작업 요청서 승인 → 실행/검증/결과 수락 → 새 세션 재개. 별도로 같은 관리 진입점에서 업데이트/복귀/복구/제거를 제공한다.

배포 및 bootstrap:
- 검증 가능한 macOS 배포 artifact를 구성한다. 필요한 제품 payload, 관리 진입점, 설명/라이선스, release/호환 manifest, runtime 출처·identity를 포함하고 내부 Work·private 증거·테스트 자료는 제품 배포물에서 제외한다.
- 배포 대상은 버전별 고정 artifact다. 사람이 이해하는 버전과 source revision, product inventory/window, runtime identity를 연결한다. latest 표시는 탐색 편의이며 실행은 확정된 버전에 결속한다.
- 다운로드 완료·크기/해시·manifest·실행 권한과 출처 신뢰를 각각 확인한다. 같은 서버에서 받은 checksum만으로 제작자 신뢰까지 증명했다고 표현하지 않는다. bootstrap 신뢰 기준과 배포본 검증 방식을 R0에서 고정한다.
- 안전한 압축 해제, 경로 이탈/링크 탈출 거절, 중단된 다운로드·잘못된 arch·손상 artifact·공간/권한 오류를 다룬다. 설치 전 실패는 기존 설치본/프로젝트를 바꾸지 않아야 한다.
- Python이 아직 없는 환경에서도 bootstrap이 시작돼야 한다. CPython 공급 빌드의 출처·재배포 조건·전용 경로 실행 가능성을 먼저 확인한다. 현 source 허용값(final GIL CPython 3.14.6/3.14.7)을 임의 확대하지 않는다. 확보가 안 되면 새 빌드 제작이나 허용 버전 변경을 자동 수행하지 않고 계획 변경 지점을 보고한다.
- 사용자 전용 설치 위치와 버전별 runtime을 사용한다. launcher, verifier, 복구 명령도 같은 검증 interpreter를 사용하도록 연결한다. 기존 env python3에 기대고 끝내지 않으며 사용자 시스템 Python/PATH 설정을 몰래 바꾸지 않는다. PATH 연결은 효과를 설명하는 명시적 설정 단계로 다룬다.

관리 명령:
- install/update/remove 등 사용자 이름은 R0에서 확정한다. bootstrap/관리 도구와 프로젝트 ./colvia의 역할·버전 선택을 명확히 하며 기존 init/update/rollback/repair/detach 계약을 재사용한다.
- 설치·업데이트·제거는 대상, 현재/새 버전, 변경/보존 목록, 복구 가능 범위를 먼저 보여준다. exact request/token 저장은 관리 도구가 돕되 실제 Owner 승인을 대신하지 않는다.
- 사용자용 관리 도구 설치, 프로젝트 runtime 설치, optional official 실행 활성화를 각각 구분한다. 기본 continuation 경로는 official2 보호를 주장하지 않는다. official2는 명시적 선택 경로다.
- 프로젝트 제거는 product와 launcher만 계약대로 제거하고 프로젝트 파일, intent/Work/결과, capsule, 외부 recovery를 보존한다. 사용자 관리 도구/공유 Python 제거는 별도 대상이며 다른 설치가 필요로 하는 runtime을 자동 삭제하지 않는다.
- unsupported update를 detach+init으로 우회하거나 retained .hrn 위에 fresh init을 하지 않는다. 제거 후 기존 기록 재부착/재설치를 지원한다고 안내하지 않는다.

온보딩:
- manual/en·ko getting-started/first-work/resume/rules-and-removal과 직접 연결된 README/개념/help를 최신 실제 경로로 맞춘다. 과거 entry-1 실습은 현재 PASS로 바꾸지 않는다.
- 첫 경로는 domain-neutral 합성 프로젝트에서 목표/계획/범위/검증을 정하고 한 결과를 수락한 뒤, 새 세션에서 같은 파일의 후속 작업으로 이어진다. 기존 파일이 있는 합성 프로젝트도 설치 보존 경계를 확인한다.
- 사람에게 JSON 작성을 요구하지 않고 agent가 준비한 정확한 요청을 이해하고 결정하도록 돕는다. 프로젝트 규칙·개인 tool 설정을 자동 덮어쓰지 않는다.
- Git 보존과 작업 결과 수락은 구분하고 remote push는 선택 사항이다. 설치 자체가 Work 생성·실행·수락이 되지 않는다.

## 3. 통합 및 실행 순서

A. 계획 결정/R0: 공개 설치 목표, bootstrap/runtime 공급, profile/전환표, 제거 보존, 배포물 구성, 검증 행렬을 묶어 검토한다. 아직 새 모델 호출은 없다.
B. 승인 후 별도 소유 integration worktree를 e411c4a에서 준비한다. 등록 경로와 소유권을 확인하고 guardrails 원 작업 트리를 수정하지 않는다. 47개 delta+수락 추가문을 결합하며 7개 공통 파일의 양측 의미를 보존한다.
C. 통합의 최소 교차 확인: v1/v2·상태/효과·View/CLI/entry·inventory/old writer를 먼저 확인한다. Guardrails 후속 후보 7개의 인덱스 문안을 이때 적용하고 기존 source 기록에 resulting revision과 bounded diff를 연결한다.
D. 그 기준 위에서 clone 없는 bootstrap·전용 runtime·관리 명령과 EN/KO 온보딩을 구현한다. 변하는 후보마다 전체 설치 행렬을 반복하지 않고 집중 검사로 수정한다.
E. 최종 배포 bytes를 고정하고 실제 사용할 interpreter 및 압축 배포본을 격리 fixture에 다운로드/설치하여 전체 경로와 lifecycle을 검증한다. source checkout을 실행한 결과만으로 배포본 PASS라 하지 않는다.
F. Claude 결과 리뷰와 범위 내 보정·영향 검사, Owner 수락용 결과/한계/공개 및 adopter 적용안을 정리한다. 실제 Git 통합·게시·adopter 적용은 별도 권한이다. 이번 계획으로 기존 main을 수정하지 않는다.

## 4. 반드시 유지할 호환 경계

- official1→2는 핸드오프에 지정된 정확한 v1 predecessor에서만 허용된다. View만 담은 임의 v1을 중간 설치하지 않는다. continuation/더 오래된 설치의 official2 직행도 자동 제공하지 않는다.
- 새 window의 첫 durable schema8 receipt 이후 구 window로 rollback할 수 없다. 같은 window P/Q 및 Q-created 이력은 정확한 양방향 reader/receipt 근거를 확인한다.
- lifecycle schema8과 execution schema2를 구분한다. product inventory와 bootstrap 배포 포맷/버전도 혼동하지 않는다.
- unknown, 미종결, partial, process 불명은 기존 guard를 유지한다. operator-resolved-unknown에서 ready=true여도 효과 unknown을 상세에서 보존한다. 기본 View 표시 변경은 별도 설계 판단으로 다루며 조회가 외부 recovery를 자동 탐색/복원하지 않는다.
- 일반 desktop/독립 승인/실제 provider 전체 보호의 미완료는 명시한다. 그 강한 보호가 필요한 사용을 지원한다고 약속하지 않으며 해당 잔여 전체를 기본 조회 온보딩의 선행조건으로 만들지 않는다.

## 5. 검증과 재사용

정상 작업의 품질·완료율·사용 마찰은 9절의 추가 기준을 함께 적용한다. 차단 검증만으로 통합 결과를 수락하지 않는다.

재사용: 수락한 View 집중 검사/문서/진입·합성 lifecycle/after B·C, Guardrails 전체 실행의 원래 결과와 후속 보정·E2E/native·리뷰. 원문/실패/skip/소비량과 정확한 identity를 유지한다. 구 전체 실행의 문서1fail과 Windows100skip을 전체 PASS로 바꾸지 않는다.

새 검사:
1. 통합 상태→View: ready/available/unknown/none/applied, v1/v2·잘못된 입력, summary/details/exit, read-only 전후와 공유 관찰, old writer 거절.
2. 배포/관리: source/Git checkout이 없는 fixture, 시스템에 지원 Python이 없는 경우, 정확한 runtime 자동 준비, arch·출처·해시·압축 경계·중단/권한/손상, 기존 설치 보존, 여러 프로젝트의 runtime 사용과 제거 경계.
3. 최종 artifact lifecycle: fresh Git/non-Git, 지원 update·거절되는 predecessor, P/Q·금지된 rollback·repair/detach·정확한 중단 복구와 plain retained reader. 실제 공개 endpoint나 실제 adopter를 사용하지 않는다.
4. 첫 작업/재개: 사용자 요청→계획→승인→결과→검증→수락→fresh session의 완료/잔여/권한 회복. 합성 Owner 결정을 실제 사람 이해도 관측으로 확대하지 않는다. 실제 compaction 해결을 주장하지 않는다.
5. 문서: EN/KO 의미, help/기술상세, 실제 명령/예상 결과, 링크/GFM, 출시 artifact에 포함되는 문서/라이선스와 제외 파일.

전체 회귀 선택: 단순 digest 변경으로 반복하지 않는다. 그러나 자동 provision한 Python 빌드는 새 실행 조합이고 launcher/배포 경로도 바뀌므로 최종 후보에 normal/parent-O 전체 회귀 1쌍을 예산에 포함한다. 고정 빌드가 기존 qualified 조합과 실제로 동일하고 영향이 충분히 한정되면 재사용 근거로 축소할 수 있다. legacy 1회 약71분은 참고이며 새 빌드 속도는 미측정이다. 집중 수정 뒤 보정 영향만 재검사하고 새로운 우려가 없으면 전체를 다시 돌리지 않는다.

격리 로컬 배포 서버/fixture 결과와 실제 공개 다운로드는 별개다. 공개 게시 승인 후 고정 URL에서 같은 bytes가 내려오는지 확인하는 마지막 확인이 필요하다. GitHub Releases 등 versioned asset 제공이 가능한 호스팅을 후보로 두되 실제 주소·공개 범위는 지금 확정하지 않는다. https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases

## 6. Claude 리뷰와 중단 조건

계획 리뷰 R0를 실행 승인 전에 진행한다. R1은 통합·관리 명령·배포/검증·온보딩 결과를 함께 검토한다. 주요 보정은 영향과 미해결 finding만 묶어 후속 리뷰한다. R0/R1은 도구/제품 시험을 Reviewer가 직접 실행한 것으로 표현하지 않는다.

제안 한도: Claude 최대6회(회당240초; 원칙적으로 R0 1회, 결과 1~2회, 나머지 보정용), 합성 새 세션 행동 최대2세션/4턴·모델 실행 합계12분. reviewer는 기존 구독 경로를 확인하고 필요한 source diff/계약/합성 결과만 전송한다. 로컬 경로·계정·실제 adopter 원문·비밀·전체 과거 로그는 제외한다. 전송 범위의 명시적 승인은 실행 패키지에 포함해야 하며 이 계획은 전송하지 않았다.

범위 내 코드·문서 보정과 영향 검사에는 매번 새 승인을 요구하지 않는 실행안을 제안한다. 예상된 거절/장애 주입은 검증 결과로 다룬다. 예상 밖 통신·권한·종료 불명 실패는 자동 retry 없이 보존/중단한다. 출처/identity/복구 근거가 불명확하거나 새 권한·지원 profile·업그레이드 경로·예산 확대가 필요하면 의존 작업을 중단하고 결정 사항을 정리한다. 제3자 runtime 신규 빌드/서명 인프라 구축, 공개 게시, 전역 환경 변경, 실제 provider/실자료 시험은 자동 포함하지 않는다.

## 7. 예상 시간과 제안 상한

단위는 능동 wall-clock 시간이다. 도구·검사·리뷰 대기와 기록/보정을 포함하고 Owner 응답·접근 제공·게시 결정 대기는 제외한다. 독립 작업과 실행이 겹치면 실제 경과를 한 번만 계산한다. Guardrails 잔여 예산을 이전하지 않는다.

- 계획/R0·배포/runtime 공급 확정: 1.5~2.5시간
- View+Guardrails 결합·교차 확인·후속 index: 2.5~4시간
- bootstrap/전용 Python/관리 명령: 4~6시간
- EN/KO 첫 작업·재개·제거 안내: 2~3시간
- 최종 artifact/lifecycle/새 runtime 회귀·행동 관측: 3~4.5시간
- 결과 리뷰·보정·수락 정리: 1~2시간
- 합계 예상: 14~22능동시간. 새 묶음 누적 중단 상한 제안: 28시간(1,680분).

위 시간은 과거 전체 회귀 약71분/모드, Guardrails 인계 통합 추정150~240분을 참고한 판단 추정이다. installer 구현 자체의 실측은 없으며 공급 가능한 전용 Python artifact·통합 영향·리뷰 finding이 주요 불확실성이다. 별도 CPython 빌드나 새로운 macOS 서명/배포 시스템 개발이 필요하면 이 추정으로 약속하지 않는다. runtime 공급 경로와 통합 기준을 확정한 checkpoint에서 남은 비용을 다시 평가하되 진행 중 소소한 보정마다 재승인을 요청하지 않는다.

기존 원장은 그대로 보존한다. Guardrails412.77/1080분·잔여667.23분은 기존 작업 계정이며 신규28시간에 숨겨서 합치거나 초기화하지 않는다. 기존 View 행동 실패/소비량도 재시험 권한으로 전환하지 않는다. 현재 계획 정리는 위 신규 실행 한도의 소비 시작이나 승인이 아니다.

## 8. 후속 후보와 완료 기준

통합 시 공통 index에 7개 후속 후보를 원 계획 링크와 함께 연결한다. 설치 전 P0는 통합 후보·설치 호환 확인으로 본 실행 범위에 연결한다. P1 원천/native·provider/독립 승인·기존 기록/사고 대응, P2 종료/취소/crash·탐지/정상 입력·일반 개발/민감자료는 각 재개 조건과 완료 근거를 보존한다. 결함이 현재 설치 경로에 영향을 주면 우선순위를 다시 판단한다. 후보 등록은 그 구현의 승인이 아니다.

완료는 고정 macOS arm64 조합에서 clone 없이 배포 artifact와 전용 Python을 준비하고, 설치·첫 결과·재개·지원 update/복귀/제거가 기존 데이터와 승인 경계를 지키며 작동하는 것을 기록된 근거로 보이는 것이다. 실제 사용자 이해도, Intel/Windows, 실제 공개 endpoint, 전체 desktop/provider 보호, 기존 adopter 적용은 실행하지 않았으면 미검증으로 남긴다.

최종 산출물: 설치/관리 명령, 재현 가능한 배포 recipe와 후보/manifest·runtime 근거, EN/KO 온보딩, 재사용/실행/미검증이 분리된 검증·리뷰 결과, 후속 index, 정확한 공개 및 adopter 적용 제안. 실제 repository 공개·release 게시·Git commit/push/merge·adopter 적용은 별도 결정이다.

## 9. 정상 작업 품질·완료율·사용 마찰 — 추가 전달 반영 r2

2026-11-01 KST Owner가 전달한 추가 검증 기준을 반영했다. 계획 r1의 입력·수락·호환·증거와 한도 경계는 유지한다. 이 추가는 새 시험·모델 호출·구현·설치 실행이나 한도 확대 승인이 아니다.

### 비교 대상과 기대 결과

대표적인 정상 문서 조회·편집·검증 작업을 고정된 합성 사례로 선정한다. 각 사례는 입력 bytes, 요청 내용과 형식, 허용 편집 구간, 보존 구간, 기존 승인 범위, 기대 결과와 정상 종료 기준을 실행 전에 명시한다. 기존 검증에서 동일하게 쓸 수 있는 사례를 우선 활용하며 검사 편의를 위해 정상 입력을 줄이거나 비밀 아닌 예시·인용·링크를 제거하지 않는다.

일반 문서 조회가 요청한 내용을 제공하는지, 편집이 요구 내용·형식을 만족하고 허용 구간 밖 bytes를 보존하는지, 검증이 결과와 실제 검사 범위·남은 한계를 정확히 보고하는지를 각각 확인한다. 성공 exit만으로 작업 품질을 통과시키지 않는다. 기본 경로와 선택적 공식 실행 경로는 조건과 결과를 구분한다.

정상 예시, 정상 인용·링크, 편집 구간 밖 보존 내용에 대한 양성 사례와 의도된 차단 사례를 짝지어 둔다. 비밀이 아닌 예시가 탐지될 수 있다는 기존 제한을 숨기지 않되, 제한을 기록했다는 이유만으로 불필요한 정상 작업 실패를 성공으로 세지 않는다.

### 완료율과 마찰 기록

- 각 사례를 완료/부분 완료/거절/실패/미실행으로 기록한다. 요청 내용·형식·편집 범위·검증·종료 조건을 모두 충족한 경우만 완료로 센다.
- 실행 전에 고정한 정상 사례 전체 N과 실행한 사례 수, 조건 충족 완료 수를 함께 보고한다. 완료율은 완료/N으로 제시하며 미실행·환경 차단을 조용히 분모에서 빼지 않는다. 미실행이 남으면 그 값은 현재 검증 진행 결과이며 제품의 일반 성공률이 아니다.
- 합성 사례 수와 실행 시도 수를 분리하고 실패 뒤 보정 결과가 원 실패를 덮어쓰지 않게 기록한다. 서로 다른 조건의 결과를 합쳐 성공률을 높이지 않는다.
- 유효한 동일 action/target/inputs의 승인으로 이어갈 수 있는 구간에서 재승인 요청 횟수, 불필요한 중단, 수동 우회 필요 여부와 이유를 기록한다. 변경된 입력·새 전송·소비된 grant/attempt·새 적용에 실제로 필요한 승인은 불필요한 재승인으로 세지 않는다.
- 고정한 필수 정상 사례의 설명되지 않은 품질 저하·미완료·재승인 회귀는 차단 사항이다. 이미 알고 있는 제한도 영향과 우회 가능성·후속 보강을 명시해 Owner 판단 대상으로 남기며 Driver가 자동 면제하지 않는다.

### 기존 근거와 비교 및 원인 분류

같은 합성 입력과 기대 결과를 사용하는 보존된 결과와 대조한다. 입력·runtime·profile·승인 조건·판정 기준이 다르면 차이를 밝히고 비교 불가/부분 비교로 남긴다. 비교표를 채우기 위해 기존 후보를 자동 재실행하지 않는다. 새 baseline 실행이 꼭 필요한 경우 승인된 시험·모델·시간 한도 안에 포함할 수 있는지 먼저 판단한다. 과거 원문이나 실제 업무 자료를 비교 입력으로 전송하지 않는다.

거절·중단은 의도된 차단, 탐지 오탐, 제품 오류, 환경 제약으로 구분한다. 증거가 부족하면 원인 미확정으로 두며 하나로 억지 분류하지 않는다. 품질 미달과 과도한 재승인도 별도로 보이게 기록한다. 각 항목에는 관측 사실, 기대 결과, 원인 근거, 사용자 영향과 후속 조치를 연결한다. 합성 결과만으로 실제 업무 품질·일반 완료율·사용자 이해도를 보장하지 않는다.

### 보정·리뷰·완료 기준 연결

문제가 발견되면 원천 접근이나 승인 경계를 일괄 완화하지 않는다. 탐지 규칙, 입력 계약, 보존 구간 처리, 오류 안내 등 근거로 확인한 원인에 대한 최소 보정안을 제시한다. 정상 양성 사례와 의도된 차단 사례를 함께 보존하며, 실행이 나중에 승인된 경우에도 그 승인 범위 안에서만 수정·영향 검사를 수행한다. 지원·권한·전송 계약이 바뀌면 범위 변경으로 다룬다.

R0에는 사례/기대 결과·분모·마찰 정의와 증거 재사용표를 포함한다. R1에는 정상 작업 결과, 실패/거절 분류, 비교 한계와 최소 보정의 효과를 포함한다. 별도 정상 품질 리뷰 프로젝트나 매 사례별 승인 절차를 만들지 않고 기존 통합 검증·Claude 리뷰에 묶는다.

8절의 완료 기준에는 위 필수 정상 사례의 결과 품질·완료·승인 연속성 판정을 추가한다. 안전한 거절의 성공과 정상 사용의 성공을 함께 확인해야 한다.

### 시간·권한 유지

기존 Guardrails 승인 누적 상한은18시간이며 마지막 인계412.77/1080분·잔여667.23분을 이 추가로 초기화하거나 확대하지 않는다. 7절의14~22시간 예상과 신규28시간 상한은 여전히 미승인 제안이고 이번 전달로 발효되지 않는다. 모델·리뷰 호출 횟수도 늘리지 않는다.

추가 기준은 예정된 정상 경로·회귀 사례에 우선 결합하고 같은 실행을 품질/마찰 평가에도 재사용한다. 현재는 사례를 실행하지 않았으므로 추가 소요를 실측했다고 주장하지 않는다. 기존 근거로 비교할 수 없는 필수 사례가 드러나 실제 예상이 달라지면, 실행 계획을 확정할 때 해당 차이만 설명하고 필요한 시간을 재산정한다.

## 10. 배포·Python 공급 구체안 — R0 입력, 2026-11-01

Owner는 r2 기반 공급 조건 구체화와 Claude 계획 리뷰를 승인했다. 제품 구현·통합·시험·설치·실제 adopter 적용은 제외한다. 이번에는 fresh session 정적 계획 리뷰1회, 회당240초, tools/MCP/시험0을 사용한다. 과거 실패/소비량은 보존하고28시간 실행안은 미승인이다. 이번 조사 전반의 시간을15분으로 보수 예약한 뒤 고정 시작부터 실제 경과를 더해 기존412.77분과 합산해1080분 상한을 지킨다.15분은 실측치가 아닌 사전 조사 비용의 보수 예약이다. 기존 Guardrails 원장을 수정하거나 남은 시간을 초기화하지 않는다.

### 배포 구조와 신뢰

제안 채널은 공개 GitHub Releases의 버전별 고정 자산이다. 현재 private 저장소를 공개하거나 새 배포 저장소를 만드는 것은 이번에 실행하지 않는다. 게시 위치는 공개 시점의 Owner 결정이며, 구현은 하나의 고정 origin/tag/asset 조합으로 구성 가능하게 하고 임의 URL 실행 기능을 일반화하지 않는다. 초기에는 private 전용 로그인/토큰 설치 경로를 만들지 않는다.

제안 asset: bootstrap shell, Colvia 관리/제품 payload archive, upstream runtime archive의 byte-identical mirror(최종 runtime license/재배포 조건 확인 후), runtime/license metadata와 release manifest, SHA-256 목록. Core product inventory digest, 배포 archive digest, runtime digest, 실제 source identity와 준비 변환은 각각 명시한다. 원 repository 자동 생성 source zip은 사용자 설치물이 아니다. 공개용 자료에는 내부 Work/리뷰/경로·계정/원 실패 원문을 포함하지 않는다. 필수 dependency attribution/license는 유지한다.

최초 명령의 개념은 버전 고정 HTTPS에서 bootstrap을 파일로 받고 공개된 고정 SHA-256과 대조한 뒤 실행하는 것이다. `curl | sh`를 기본 예제로 삼지 않는다. bootstrap 안에 해당 버전 manifest digest를 고정하여 후속 payload/runtime을 검사한다. 공개 페이지/도메인 및 GitHub 계정·TLS가 첫 신뢰 기준이며, 동일 제공처의 checksum을 독립 서명 인증이라고 주장하지 않는다. 사용자는 repo clone/GitHub 로그인/gh/uv/Homebrew를 설치 전제조건으로 갖지 않는다. macOS 기본 도구만으로 bootstrap을 시작하고 추가 도구가 없으면 변경 전에 명확히 거절한다.

Maintainer는 게시 전에 release asset identity와 upstream 근거를 검토하고, 공개 시 immutable releases/attestation을 사용할 계획이다. 사용자 bootstrap이 gh attestation 검증을 수행한다고 주장하지 않는다. 최신 표시를 바꿔도 기존 프로젝트/runtime을 자동 갱신하지 않는다. versioned source/준비 근거는 복구용으로 유지한다. 게시 이후 URL/자산 bytes의 실제 다운로드 확인은 별도 게시 승인 뒤 수행한다.

### Python 공급 후보와 현재 확인 수준

공급 후보: Astral Python Build Standalone의 GIL CPython 3.14.7, aarch64-apple-darwin, install_only gzip archive. 공급 빌드20260929를 첫 검토 후보로 고정한다. release metadata에서 아래를 확인했다.

- 파일: cpython-3.14.7+20260929-aarch64-apple-darwin-install_only.tar.gz
- 크기: 26775255bytes
- SHA-256(metadata): 0211ccf04c5e0a0feb0b9bf1148030e1f6a31b8eae624f13919a7752a4e3dc79
- 원본 URL: https://github.com/astral-sh/python-build-standalone/releases/download/20260929/cpython-3.14.7%2B20260929-aarch64-apple-darwin-install_only.tar.gz
- 공개 release metadata 조회: https://api.github.com/repos/astral-sh/python-build-standalone/releases?per_page=30

이것은 공개 metadata 관측이며 archive bytes 독립 hash·압축 내부·코드서명/격리 속성·실행·TLS·stdlib·Seatbelt 호환성 확인은 아니다. 공급자 문서는 portable/install_only·GIL 구분을 설명하지만 정확한 macOS 최소 버전과 Colvia qualification은 별도다. 현 제품의 허용 Python gate는3.14.6/3.14.7이며, upstream3.14.7은 더 최신 patch로 대체됐다는 표기가 있다. 이 사실 때문에 gate를 자동 확대하지 않는다. 실제 공개 직전 지원/보안 적합성을 다시 판단하고 필요하면 runtime gate 변경을 별도 승인 대상으로 한다.

재배포 조건은 build tool LICENSE만으로 결론내리지 않는다. 승인된 준비 단계에서 정확한 runtime archive의 license 본문과 그 빌드의 full metadata를 대조하고 의존 라이선스/고지·원본 참조를 보존한다. install_only에는 full의 PYTHON.json이 없으므로 별도 공급 metadata를 정확히 결속해야 한다. 필요한 자료가 없거나 조건을 충족할 수 없으면 공개 후보로 확정하지 않는다. archive 다운로드/풀기/실행은 이번 계획 리뷰에서 하지 않는다.

### 전용 runtime·관리 명령·프로젝트 연결

제안 사용자 저장소는 사용자 전용 Library/Application Support/Colvia 아래의 runtime/<runtime-id>, manager/<version>, distributions/<release-id>, requests/<operation-id>, staging/<operation-id>다. 제품 프로젝트 authority는 기존 .hrn에 남는다. 사용자 저장소의 목록은 배포/관리 소유 기록이고 작업 승인이나 결과 수락의 새 authority가 아니다. root/sudo·시스템 Python 변경·전역 pip·사용자 shell rc 자동 변경은 하지 않는다.

관리 명령은 전용 Python의 검증된 절대 executable을 -I/-B로 호출한다. 프로젝트 ./colvia는 현재 env python3 방식이므로 관리 명령만 고쳐서는 충분하지 않다. managed 프로젝트 launcher도 같은 검증된 runtime으로 연결할 수 있도록 설계하고 기존 inventory·same-window launcher 동등성·old writer 거절·Git 내용 검증을 함께 평가한다. 단순 post-install 치환으로 immutable payload를 바꾸지 않는다. 경로가 root/선택된 runtime 밖으로 빠지는 symlink를 허용하지 않되 공급 archive의 필요한 내부 링크는 정확한 manifest와 경계 검사를 통해 평가한다. launcher binding 표현은 R0에서 명시적으로 검토할 핵심 설계 위험이다. 기존 계약으로 표현할 수 없으면 구현 전에 최소 계약 개정안을 Owner에게 제시한다.

초기 명령 이름 후보: 관리 도구의 install/update/remove/status/doctor와 명시적 rollback/repair. 명령 실행은 먼저 대상과 변경/보존/전환 한계를 제시하고 정확한 preview/request에 결속해 승인 뒤 적용한다. source/init 등의 내부 용어는 상세에 남긴다. 도구 자체 update와 프로젝트 update를 구분한다. installer 실행 승인은 프로젝트 작업·모델 전송 승인으로 확장되지 않는다. 프로젝트 제거 뒤에도 독립 관리 명령·원 request·필요한 runtime이 남아 복구/조회가 가능해야 한다. 공유 runtime은 사용자를 모두 확인할 수 없으면 유지하고 프로젝트 제거가 함께 지우지 않는다.

### 정상 품질·완료율·마찰의 고정 사례 제안

검증 사례는 최소8개 정상 사례를 같은 합성 입력과 기대 결과로 고정한다. Q1문서 조회와 요구 항목/근거, Q2정확한 구간 편집과 나머지 bytes 보존, Q3구조/목록/줄바꿈 형식, Q4비밀 아닌 예시·정상 인용/링크, Q5편집 구간 밖 정상 보존 내용, Q6지원하는 문서 검증과 정확한 결과 설명, Q7유효한 같은 승인 아래 진행 지속, Q8새 세션의 완료/잔여/권한 회복이다. 경계 간 겹침을 정리해 독립 판정 행을 만들고 단순 test method 수와 혼동하지 않는다. 이8개는 아직 실행되지 않았다.

각 사례의 요청·입력·편집구간·승인조건·정상 종료·기대 출력/검사 predicate와 의도된 차단의 paired control을 R0 처분 때 확정한다. 사례를 사후 삭제해 N을 줄이지 않는다. 기본/official 경로의 applicability를 실행 전에 기록하고 다른 조건의 결과를 하나의 성공률로 합치지 않는다. 완료/N, 실행수, 미실행/부분/거절/오류와 재승인/중단/수동 우회를 별도로 보고한다. 보존된 결과의 exact input/기준이 맞으면 재사용하고 맞지 않으면 비교 불가/부분 비교로 명시한다. 모델2세션/4턴·12분은 미승인 제안이며, 결정적 fixture로 확인한 품질을 실제 agent/사람 품질로 바꾸지 않는다.

불필요한 차단은 의도된 거절·오탐·제품 오류·환경 제약·원인 미확정으로 분류하고 품질/마찰 회귀를 숨기지 않는다. 실제 입력이 비밀이거나 새로운 권한을 요구하면 필수 차단/승인으로 분류한다. 원천·승인 경계를 느슨하게 만들어 통과시키지 않고 detector/입력계약/오류 안내 등 원인별 최소안을 제안한다.

### 공급 근거

- https://docs.astral.sh/python-build-standalone/ : portable/self-contained 배포 방향
- https://docs.astral.sh/python-build-standalone/distributions/ : install_only 형태, GIL/free-threaded 구분, full metadata와 차이
- https://docs.astral.sh/python-build-standalone/running/#licensing : runtime와 의존성별 license·고지 확인 필요
- https://docs.astral.sh/python-build-standalone/quirks/ : sysconfig build-time path 등 주의사항. C extension/사용자 pip 환경은 초기 installer 범위가 아님
- https://www.python.org/downloads/release/python-3147/ :3.14.7 release 및 superseded 표시
- https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases : versioned asset/tag 고정과 release attestation. 사용자 검증 구현/현재 repo 설정을 확인한 근거는 아님

현재 공급 후보는 선택 가능한 것으로 관측됐으나 설치·제품 적합성은 미검증이다. 예상14~22시간/제안28시간은 여전히 미승인이고 실제 독립 runtime/launcher 변경 비용을 R0에서 재판단한다.


## Formal R0 record

Reviewer: Claude CLI, reported model `claude-opus-5-5`; existing claude.ai first-party Pro subscription. Fresh session `86da98a6-bed6-4aed-bf73-36fc95c308d6`. Tools/MCP/tests disabled. One call, no retry. Started 2026-11-01T11:44:31.837636Z; completed 11:48:26.827098Z, elapsed234.988s/240s, exit0, process group absent, no permission denial/input drift. This is a static review, not product execution evidence.

Base: `da3e20d329e88b998d141c76ff3b3ff66d6f707d`.
Packet SHA-256: `4386e56996a3afbc5825d3d1b9cd238a79e395b5d685db7ebf0cdbbabb734bbc` (34,605bytes).
Pre-review note SHA-256: `5bcc34a8cfe5920f21de50cef2248c33a0df5974d59acdf373e4d959abe390f0`.
Pre-review new-note unified diff SHA-256: `983eb99d1849a4a1d8edf24512172345c0eb219bdcbb5d86d0f1609587d26950`.
Verdict SHA-256: `8447d2024e4f40ffec0302bac836d0c4ad838c69141f3390cf2e277089cb1093`.
Fixed packet, runner, execution metadata and response are retained in Driver-owned private evidence for the Owner plan decision and later delta review. The following is the verbatim reviewer response. r4 is appended after the response and was not reviewed in R0.

<!-- BEGIN VERBATIM R0 -->
# R0 계획 리뷰: Colvia macOS 배포·관리·첫 사용 통합 계획 r3

## Verdict: CHANGES_REQUESTED

방향은 타당하다. 공개 설치 목표, 전용 Python, 정직한 신뢰 표현, 증거 재사용 원칙은 유지할 만하다. 다만 r3는 구현 착수 전에 정할 내용이 비어 있어 실행 승인 입력으로는 부족하다.

- **핵심 공백:** launcher 결속 방식, profile/전환표, 공급 실현성 확인 순서, 정상 사례 분모가 정해지지 않았다.
- **BLOCKED가 아닌 이유:** 대부분 계획 보정과 Owner 결정으로 해소할 수 있다.
- **검토 한계:** 정적 설계 검토이며, source observation은 Driver 관측으로만 취급했다. URL, digest, 라이선스, 호환성은 직접 검증하지 않았다. macOS·Python 동작에 관한 언급은 일반 지식에 근거한 확인 대상이다.
- **권한:** 이 리뷰는 구현, 다운로드, 설치, 시험, 게시 권한을 부여하지 않는다.

## Findings

### F1. High: launcher 결속안이 없어 "전용 Python 자동 공급"이 아직 구체안이 아니다

**근거**

10절은 launcher 표현을 핵심 위험으로 지목하지만 후보를 선택하지 않았다. 요구사항은 서로 충돌한다.

- 프로젝트 launcher는 inventory와 Git 내용 검증, same-window 동등성의 대상이다.
- 사용자별 절대 경로를 넣으면 byte 동등성이 깨지고, 커밋되는 파일에 사용자 경로가 들어간다.
- `Library/Application Support`에는 공백이 있어 shebang 직접 지정이 부적합하다.
- `env python3`에 머물면 PATH 순서에 따라 다른 허용 interpreter가 선택될 수 있다. 전용 runtime에 결속되지 않는다.
- 지원 Python이 없는 Mac에서는 `/usr/bin/python3` stub이 Command Line Tools 설치 안내를 띄울 수 있다.
- 제품이 띄우는 worker와 probe, Seatbelt 허용 경로가 새 runtime 위치와 맞는지 계획에 나타나 있지 않다.

**최소 보정**: 계획에 다음 두 안을 명시하고 첫 후보를 하나 고른다.

| 안 | 방식 | 영향 |
|---|---|---|
| A (권고) | launcher bytes를 유지한다. 관리 명령이 runtime을 검증한 뒤 자식 프로세스의 PATH에만 전용 `bin`을 앞세워 `./colvia`를 실행한다. | inventory·schema 변경을 피할 가능성이 크다. 단, 직접 실행한 `./colvia`는 전용 runtime 보장 밖이다. 지원 Python이 없으면 명확히 실패시키고, 이 한계를 완료 기준과 agent 안내에 적는다. |
| B | launcher가 runtime-id를 해석해 전용 runtime을 직접 실행한다. | 직접 실행까지 결속된다. 대신 inventory·window·전환 계약이 바뀌므로 별도 승인 대상이며, 비용을 재산정해야 한다. |

두 안 모두 실행 체인 점검을 범위에 넣는다. 대상은 `sys.executable`, 자식 프로세스 호출 방식, `-I/-B` 전파, Seatbelt 경로다. 점검에서 gate나 schema 변경이 필요해지면 작은 보정으로 처리하지 않고 중단해 결정을 요청한다.

### F2. High: R0에 포함하기로 한 전환표·사례표·재사용표가 입력에 없다

**근거**

- 3절 A는 profile/전환표와 검증 행렬을, 9절은 사례·분모·마찰 정의와 증거 재사용표를 R0에 포함한다고 했다.
- 10절은 사례 세부를 "R0 처분 때" 확정한다고 미룬다. 전환표 자체는 제공되지 않았다.
- 2절도 URL·도메인·버전 정책과 명령 이름을 R0에서 고정한다고 했지만, 10절은 게시 위치를 공개 시점 결정으로 넘긴다.
- View+Guardrails 결합본은 핸드오프의 원래 target과 identity가 다르다. 핸드오프의 정확한 predecessor 근거가 결합 target에도 유효한지는 다시 지정해야 한다.
- 공개 기본 설치가 continuation일 때 official2로 갈 경로가 불명확하다. 2절은 "optional official 실행 활성화"를 말하고, 4절은 continuation의 official2 직행을 제공하지 않는다고 한다. 설치 후 활성화가 금지된 전환인지 답이 없다.

**최소 보정**: 다음 축을 가진 전환표를 실행 패키지 전제로 추가한다.

- **행:** fresh, exact v1 predecessor, e411c4a(View only), 구 continuation, 더 오래된 설치, retained `.hrn`, 결합본 P/Q
- **열:** 허용/거절, 근거 receipt, rollback 가능 시점, runtime 요구, 사용자 안내

표에 없는 전환은 거절로 고정한다. 이미 설치한 사용자의 official2 활성화가 어느 칸인지 반드시 답한다.

### F3. High: 공급 실현성 확인이 통합 뒤로 밀려 있어 비용 낭비 위험이 있다

**근거**

- 3절은 B·C 통합(2.5~4시간)을 먼저 하고 D에서 runtime을 다룬다.
- 그런데 archive의 실제 hash, 내부 구조, 서명, 실행, TLS, stdlib, Seatbelt, 라이선스는 모두 미확인이다.
- 1.5~2.5시간의 "공급 확정" 항목은 있으나 무엇을 해도 되는지 권한이 정의되지 않았다. A는 계획·R0 단계로만 서술되어 있다.

**최소 보정**: A와 B 사이에 S0 게이트를 둔다.

- **허용 범위:** 고정 URL 1건 다운로드, 격리 디렉터리 내 전개, 독립 SHA-256 비교, 라이선스·full metadata 대조, 서명 상태 확인, 격리 위치에서의 최소 실행 smoke
- **제외 범위:** 제품 통합, gate 변경
- **상한:** 2.5시간 이내
- **판정:** 공급 불가, 라이선스 불충족, gate 변경 필요 중 하나면 통합에 들어가지 않고 Owner 결정으로 돌린다.

다운로드와 실행은 네트워크 허용 목록과 함께 명시적으로 승인받아야 한다.

### F4. High: 고정 origin과 "최종 bytes 격리 검증"이 충돌한다

**근거**

- bootstrap에 origin/tag/asset과 manifest digest를 고정하고, 임의 URL 기능은 두지 않는다.
- 3절 E와 5절은 같은 최종 bytes를 격리 서버에서 시험하라고 한다.
- 게시 위치는 공개 시점에 결정된다.

이 조합에서는 고정 origin을 넣은 bytes를 격리 서버로 시험할 방법이 없다. 시험 후 origin을 넣으면 bootstrap bytes와 digest가 바뀌어 시험 결과가 해당 bytes의 증거가 되지 못한다. 또한 manifest가 bootstrap digest를 담으면서 bootstrap이 manifest digest를 고정하면 digest 순환이 생긴다.

**최소 보정**

- 빌드 순서를 고정한다: payload·runtime → manifest → bootstrap → 외부 `SHA256SUMS`. manifest는 bootstrap digest를 담지 않는다.
- bootstrap을 "origin 없는 검증 코어"와 "origin·release 값 렌더링"으로 나눈다.
- 시험 경로는 로컬 asset 디렉터리 입력 등 좁은 수단으로 두고, manifest digest 검증은 우회하지 못하게 한다.
- 게시 위치가 확정되면 렌더링 차이가 허용 값뿐임을 확인하고, 그 bytes로 제한된 재확인을 수행한다.
- 이렇게 얻은 PASS는 "동일 코어+제한된 렌더링 차이"로 기록한다.

### F5. High: Python 이전 단계의 압축 해제 경계와 결속 사슬에 공백이 있다

**근거**

경로 이탈과 링크 탈출을 거절한다고 했지만, 신뢰할 Python이 없는 시점에 runtime archive를 무엇으로 검사할지 정하지 않았다. shell에서 `tar -t` 출력을 파싱하는 방식은 취약하다. 또한 `install_only`에는 `PYTHON.json`이 없어 전개 후 트리를 대조할 기준이 필요하다.

**최소 보정**: 다음 사슬을 계획에 고정한다.

1. 외부 SHA-256으로 bootstrap을 대조한다.
2. bootstrap의 고정값으로 manifest를 대조한다.
3. 크기와 digest가 맞는 runtime archive만 staging에 전개한다. 이 archive의 내용은 maintainer가 게시 전에 검사해 둔 것이다.
4. 전개 트리를 manifest의 파일·mode·링크 목록과 대조한다.
5. 대조를 통과한 뒤 해당 interpreter를 `-I`로 실행하고, payload는 Python의 안전 추출기로 처리한다.
6. 원자적 rename으로 활성화한다.

추가로 다음을 명시한다.

- **식별:** runtime-id는 버전이 아니라 digest에 결속한다.
- **공급 메타데이터:** full metadata와의 대응을 manifest에 기록한다.
- **bootstrap 실행 환경:** `/usr/bin` 절대 경로, `curl -q`, https 전용 redirect, `sysctl hw.optional.arm64` 기반 arch 판정(Rosetta 대비)을 사용한다.
- **단계 승인:** runtime 다운로드 전에 shell 단계의 미리보기와 승인을 둔다. 현재 흐름은 미리보기가 runtime 준비보다 뒤에 있어, 사용자 저장소 변경이 먼저 일어난다.

### F6. Medium-High: 관리 도구 update의 신뢰와 프로젝트-runtime 연결 기록이 미정의다

**근거**

서명이 없으면 관리 도구가 N+1 manifest를 신뢰할 근거는 TLS와 제공처뿐이다. "latest"로 자동 해석하면 초기 신뢰 설명이 약해지고 downgrade 판정도 불가능하다. 프로젝트가 어떤 runtime을 쓰는지 기록할 위치도 없다. `.hrn`에 넣으면 schema 변경이 될 수 있고, 사용자 저장소에 두면 저장소 삭제나 다른 기기 clone 시의 동작이 미정의다.

**최소 보정**

- 첫 공개판 update는 명시 버전과 사용자가 대조한 새 bootstrap 또는 manifest digest로만 시작한다.
- 자동 latest 추적과 자동 업데이트는 제외한다. downgrade는 전환표로만 허용한다.
- 안 A에서는 연결 기록을 authority가 아닌 사용자 저장소 캐시로 둔다. 누락 시 추정하지 않고 명확히 거절하거나 재지정을 요구한다.
- 시험 행렬에 다음을 추가한다: 2개 fixture release, runtime 저장소 삭제, 다른 기기 clone 모사, 동시 설치 경합, staging 중단 후 재시작.

### F7. Medium-High: 제거 후 복구의 약속 범위가 모호하다

**근거**

10절은 프로젝트 제거 뒤 "복구/조회가 가능"해야 한다고 하고, 2절은 제거 후 재부착이나 재설치를 지원한다고 안내하지 않는다고 한다. 관리 도구 제거 시 `requests/`, `distributions/`의 처리와 retained 기록을 어느 interpreter로 읽는지도 불명확하다. 또한 프로젝트 사용처를 모두 확인할 수 없으면 runtime을 유지한다는 규칙은 프로젝트 이동 가능성을 고려하면 사실상 영구 유지가 된다.

**최소 보정**: 대상별 보존 표를 만든다.

| 대상 | 기본 처리 | 보정 내용 |
|---|---|---|
| 프로젝트 제거 | product·launcher만 제거 | 제거 후 가능한 일은 plain retained reader와 조회로 한정한다. 재부착은 미지원으로 명시한다. |
| 관리 도구 제거 | request·복구 근거 보존이 기본 | 삭제 시 잃는 복구 범위를 미리보기에 표시한다. |
| runtime 삭제 | 자동 삭제 금지 | 명시적 대상 지정 후, 알려진 사용처와 "알 수 없는 사용처 가능성"을 표시한다. 같은 digest로 재획득 가능한지도 안내한다. |
| `.hrn`, Work, capsule, 외부 recovery | 항상 보존 | 어떤 관리 명령도 삭제하지 않는다. |

`rollback`이 관리 도구, runtime, 프로젝트 중 어느 것의 복귀인지 명령 이름과 미리보기에서 구분한다.

### F8. Medium-High: 3.14.7이 superseded인데 판단 시점이 공개 직전이다

**근거**

공개 직전에 새 patch가 필요하다고 판단하면 gate 변경, 새 공급 빌드, 전체 회귀가 다시 발생한다. 그때까지의 qualification 상당 부분이 무효가 된다. gate 변경은 별도 승인 사항이므로 작은 보정으로 처리할 수 없다.

**최소 보정**

- S0 종료 시 3.14.7 이후 patch의 보안 수정 내용을 근거로 Owner가 먼저 결정한다.
- 공개 직전 재검토는 유지하되, 재qualification을 일으키는 조건과 예상 비용을 미리 적는다.
- gate 변경 시 runtime과 launcher 관련 회귀 1쌍을 다시 쓸 수 있음을 비용표에 밝힌다.

### F9. Medium-High: 정상 작업 지표의 분모와 측정 방법이 아직 판정 가능하지 않다

**근거**

- "최소 8개"와 "겹침을 정리해 독립 판정 행을 만든다"는 표현으로는 N이 고정되지 않는다.
- Q3, Q4는 여러 성질을 한 행에 묶어 부분 실패를 가릴 수 있다.
- 기본 경로와 official 경로의 칸별 분모가 없다.
- 모델 2세션/4턴으로 8개 이상의 agent 품질을 모두 볼 수 없다. 어떤 행이 결정적 fixture이고 어떤 행이 agent 실행인지 정해져 있지 않다.
- 기존 근거와 비교할 수 없는 행은 "회귀 없음"을 판단할 수 없다.
- 설치와 첫 사용의 마찰이 사례에 없다. Q7은 작업 중 승인 연속성만 다룬다.

**최소 보정**: 실행 패키지 전에 사례 표를 동결한다.

- **행 분해:** 판정 predicate 하나당 한 행으로 나눈다.
- **분모:** `사례×경로` 칸마다 applicable 또는 N/A(사전 사유)를 기록한다.
- **행 필드:** 측정 종류, 기대 승인 수, 정상 종료 predicate, paired control, baseline 식별자 또는 비교 불가
- **보고:** 최초 시도 완료/N과 보정 후 완료/N을 분리한다. 측정 종류별 수치를 합치지 않는다. 사후 추가 사례는 별도 cohort로 둔다. control은 N에 넣지 않는다.
- **판정:** 필수 행이 미완료이면 차단하고 Owner만 예외 처리할 수 있다. 비교 불가 행은 절대 predicate로 판정하되 "회귀 없음"이라 쓰지 않는다.
- **추가 행:** Q9 "첫 설치→첫 결과"를 둔다. 기록 항목은 필요한 수동 단계 수, 승인 수, 중단 수, 소요 시간이다. 이는 합성 관측이며 실제 사람 이해도 근거가 아니다.

행 수와 agent 실행 여부는 12분 한도 안에서 정한다. 한도를 넘어야 한다면 사례를 지우지 말고 미실행으로 남긴다.

### F10. Medium: 회귀 축소 조건과 재실행 기준이 느슨하다

**근거**

5절은 고정 빌드가 기존 qualified 조합과 같으면 전체 회귀를 축소할 수 있다고 했으나, 비교 대상 빌드 identity가 제시되지 않았다. 또한 결합본은 7개 공통 파일의 의미 결합이 미검증이므로 Python이 같아도 기존 전체 실행을 그대로 대체할 수 없다.

**최소 보정**

- 첫 공개 후보의 normal/parent-O 1쌍은 필수로 하되, 최종 bytes 고정 후 1회만 수행한다.
- 축소는 Driver가 정하지 않고 근거와 함께 Owner 결정으로 둔다.
- 재실행 기준을 표로 고정한다.

| 변경 유형 | 재검사 |
|---|---|
| 문서·문구만 변경 | 문서 검사 |
| bootstrap·manifest만 변경 | artifact lifecycle smoke |
| 관리 명령만 변경 | 해당 lifecycle 행 |
| runtime, launcher, inventory, lifecycle writer, gate 변경 | 영향 모드 전체 회귀 |

- 구 전체 실행의 문서 1 fail과 Windows 100 skip은 원문 그대로 인용하고, 결합본에서의 처리 결과를 별도 행으로 둔다.
- 기존 View·Guardrails 증거는 각 원래 identity의 증거로만 쓰고, 결합본에는 교차 확인 결과만 새로 붙인다.

### F11. Medium: 240초 리뷰 한도에 맞는 패킷 설계가 없다

**근거**

R1은 통합, 관리 명령, 배포, 온보딩, 품질 결과를 함께 검토한다. 큰 패킷을 240초에 넣으면 시간 초과나 표면적 검토가 될 수 있다. 시간 초과가 1회 소비인지, 부분 결과를 어떻게 다룰지도 없다. 이번 R0가 6회에 포함되는지도 불명확하고, r4 재리뷰 권한도 없다. 10절의 승인은 1회뿐이다.

**최소 보정**

- 회당 240초와 총 6회는 유지하되 이번 R0를 1회로 센다.
- R0 델타 1회로 High 보정만 확인한다. 이 회차는 새 승인을 받아야 한다. 남은 4회를 결과와 보정에 쓴다.
- R1은 패킷 2개로 나눈다: ① 통합·전환·lifecycle, ② bootstrap·runtime·온보딩·품질. 패킷마다 크기 상한을 둔다.
- 시간 초과는 소비로 기록하고 자동 재시도하지 않는다. 부분 응답은 부분 결과로만 처리한다.

### F12. Medium: 시간 원장의 귀속이 일관되지 않다

**근거**

- 10절은 이번 조사 시간을 기존 412.77분과 합산해 1080분 상한을 지키되 원장은 수정하지 않는다고 한다.
- 7절은 Guardrails 잔여를 이전하지 않는다고 하면서 "계획/R0"를 신규 예상에도 넣는다.
- 15분은 실측이 아니므로 "보수"임을 증명할 수 없다.
- 통합 추정 150~240분이 신규 예산으로 옮겨졌는데, Guardrails 잔여 667.23분이 살아 있으면 같은 작업에 계정이 둘 존재한다.

**최소 보정**

- 이번 조사와 R0는 별도 계획 기록에 `15분 예약 + 실측 경과`로 남기고, 18시간 상한 판정에 합산만 한다.
- 합산 예시: `412.77 + 15 + 실측 경과 ≤ 1080`. 한도까지 여유가 커서 이번 리뷰만으로 상한 위험은 없다.
- 신규 28시간이 승인되면 "시작 이후 계획·R0 잔여"만 신규로 계상한다.
- Guardrails 잔여를 신규 통합에 쓰지 않음을 명시하고, 잔여의 동결 여부를 Owner가 결정한다.

### F13. Medium: 실행 패키지에 필요한 권한이 일부 빠져 있다

**근거**

8절은 Git commit을 별도 결정으로 두지만, manifest와 3절 C는 source revision과 resulting revision을 요구한다. 커밋 없이는 배포 identity가 성립하지 않는다. 또한 E의 실제 interpreter 획득은 upstream 네트워크 접근이지만, "실제 공개 endpoint 미사용" 문구와 구분되어 있지 않다.

**최소 보정**: 실행 패키지에 다음을 명시한다.

- 소유 integration worktree 내 로컬 커밋 허용, main·push·merge 제외
- 네트워크 허용 목록: 고정 upstream URL 1건과 필요한 metadata 조회
- e411c4a가 실행 시점에도 수락 기준인지 재확인. 원격을 갱신하지 않았다는 관측이 남아 있다.

### F14. Medium: 공개 범위와 대상자 표현이 보호 수준에 맞게 고정되지 않았다

**근거**

S1b 수락은 trusted-local 전제이고 전체 desktop/provider 보호는 미완료다. 공개 설치는 이 전제를 공유하지 않는 사용자까지 넓힌다. 또한 현재 저장소는 private이다. 일반적으로 private 저장소의 release asset은 인증 없이 받을 수 없으므로, 로그인 없는 설치의 전제는 공개 저장소 또는 다른 공개 호스팅이다. 저장소 전체 공개는 내부 Work와 리뷰, 이력을 노출할 위험이 있다.

**최소 보정**

- 보호 한계와 trusted-local 전제를 공개 README, 설치 미리보기, 첫 작업 안내에 넣어 EN/KO 문서 검사에 포함한다.
- 배포 전용 공개 저장소를 권고 기본안으로 둔다. public asset만 싣고 source 대응 근거와 라이선스를 포함한다.
- immutable 설정은 첫 게시 전에 켜야 하는지 확인한다.
- 완료 보고에서 "공개 설치 가능"을 주장하지 않는다. 게시 후 확인 전까지는 "게시 준비된 후보"로 표현한다.

### F15. Low: 작은 정리 사항

- **fixture 한계:** PATH를 비운 fixture는 깨끗한 macOS가 아니다. `/usr/bin/python3` stub, CLT 유무, Gatekeeper 동작은 제한 사항으로 기록한다.
- **미러 경로:** 기본 다운로드 위치를 하나로 정한다. upstream 대체 경로를 둘 경우 같은 digest를 강제하고 조용한 fallback을 두지 않는다. 라이선스 때문에 미러가 불가능하면 upstream 직접 다운로드가 대안이다.
- **테스트 환경:** 지원 macOS 최소 버전을 실제 시험 버전으로만 표기한다.
- **기록 경계:** 3절 C의 "기존 source 기록 연결"은 완료 Work에 진행을 섞지 않는다는 서문과 충돌하지 않도록, 새 Work가 소유하는 index 항목으로 표현한다.

## 잘 설계되어 유지할 부분

- `curl | sh`를 기본으로 쓰지 않고, 같은 제공처의 checksum을 제작자 인증으로 표현하지 않으며, gh attestation을 사용자 검증처럼 말하지 않는다.
- sudo, 전역 pip, shell rc 자동 변경을 제외한다.
- source checkout 결과를 배포본 PASS로 간주하지 않는다.
- 금지된 우회(detach+init, retained `.hrn` 위 fresh init)를 차단한다.
- 미실행을 분모에서 빼지 않고, 실패 기록을 보정 결과로 덮지 않는다.
- 불필요한 재승인과 정당한 재승인을 구분한다.
- 사례별 승인을 만들지 않고, 범위 내 보정마다 재승인하지 않는다.
- 3.14.6/3.14.7 gate를 임의로 확대하지 않는다.

## 미확정 Owner 결정

괄호 안은 리뷰어 권고이며 결정이 아니다.

1. **launcher 결속:** 안 A(첫 후보로 권고)와 안 B 중 선택. 직접 실행한 `./colvia`의 runtime 비보장을 받아들일지 포함한다.
2. **Python 패치:** 3.14.7 유지 또는 gate 변경 별도 승인. (S0 종료 시 결정)
3. **첫 신뢰 기준:** 서명 없는 TLS+제공처+공개 SHA-256 수준을 첫 공개에 수용할지. (명확한 고지 전제로 수용 가능)
4. **게시 위치:** 공개 전환 또는 배포 전용 공개 저장소. (배포 전용 권고)
5. **Runtime 배포:** 미러 또는 upstream 직접 다운로드. (라이선스 확인 뒤 미러, 불가 시 upstream)
6. **전환표:** 기존 설치의 official2 활성화와 e411c4a 설치본의 처리. (표에 없으면 거절)
7. **공개 대상자:** trusted-local 한계를 전제로 한 일반 공개 여부.
8. **예산:** 신규 예산과 단계 해제 방식, Guardrails 잔여 동결 여부.
9. **필수 사례:** 필수 행과 모델 관측 대상 행의 확정, 미달 시 예외 권한.

## 범위와 예산 판단

**범위:** 합리적이지만 한 번의 실행에 묶을 수 있는 조건은 안 A다. 안 B나 gate 변경, 서명 인프라가 들어가면 별도 범위로 분리해야 한다. 자동 업데이트, Intel/Windows, 자체 CPython 빌드, 실제 adopter 시험 제외는 유지한다.

**시간:** 14~22시간은 안 A 기준으로 가능하나 낙관적이다.

- 회귀 1쌍은 이전 실측 기준으로 약 142분이고 새 빌드 속도는 미측정이다. 3~4.5시간 구간은 artifact lifecycle과 품질 사례까지 담기에 빠듯하다.
- 해당 구간을 4~6시간으로 올리면 합계는 15~23.5시간이다. 이 수치도 설치 도구 실측이 없는 판단 추정이다.
- 28시간 상한은 안 A 기준으로 전체 중단선으로 적정하다. 안 B의 비용은 현재 근거로 추정할 수 없어 28시간 약속에 포함하면 안 된다.

**단계 해제 권고:**

| 단계 | 상한 | 다음 단계 진입 조건 |
|---|---|---|
| S0 공급 실현성 | 2.5시간 | 공급 후보·라이선스·실행 smoke 확인, 패치 결정 |
| 통합·교차 확인 | 누적 7시간 | 전환표 유효, 의미 결합 확인 |
| 구현·온보딩 | 누적 16시간 | 집중 검사 통과, 비용 재평가 |
| 최종 qualification·리뷰 | 누적 28시간 | 종료 |

단계 진입 조건은 실질 판단 지점에만 두고, 범위 내 소규모 보정에는 재승인을 요구하지 않는다. 기존 18시간 상한과 412.77분 기록은 그대로 두며 신규 예산과 섞지 않는다.

**다음 게이트:** F1~F5를 반영한 r4와 F9의 사례표가 갖춰지고, Owner 결정 1·6·8이 내려진 뒤에 S0 실행 승인을 판단할 수 있다. 결정 2는 S0 결과로 내린다.

<!-- END VERBATIM R0 -->

## Driver dispositions — no Owner acceptance inferred

| Finding | Disposition | Reason/result |
|---|---|---|
| F1 High | Gap accepted, Reviewer A recommendation not adopted | Direct ./colvia experience retained; binding contract unresolved; B scope/cost not yet established. |
| F2 High | Plan corrected; target qualification open | Explicit transition matrix, exact predecessor and cohort/reuse table in r4. |
| F3 High | Plan corrected | S0 before integration; downloads/execution remain unapproved. |
| F4 High | Plan corrected | Acyclic digest chain; local core vs rendered production evidence separated. |
| F5 High | Partially corrected, implementation design open | Trust sequence fixed; exact pre-Python tree verifier still requires design. |
| F6 Medium-High | Plan corrected; binding storage open with F1 | Explicit version/digest update; cache has no authority; lifecycle additions. |
| F7 Medium-High | Plan corrected | Removal preservation table; interrupted recovery distinct from completed detach reattachment. |
| F8 Medium-High | Plan corrected; patch decision open | Patch/security assessment before qualification; no runtime gate change. |
| F9 Medium-High | Plan corrected, fixture binding pending execution preparation | D9 per path, A2, L1 separate cohorts; exact expectations and no invented baseline. |
| F10 Medium | Partially accepted | First new combination full pair retained; routine evidence selection stays within Driver authorization, no repeated approval gate added. |
| F11 Medium | Plan corrected | 1/1 call consumed; proposed six total not activated, smaller delta/result packets. |
| F12 Medium | Plan corrected | Reservation separated from measured interval; original ledger preserved; no double charging or transferred budget. |
| F13 Medium | Partially defended | Commit not prerequisite for recoverable prototype identity; upstream network and publication permissions separated. No Git mutation authorized. |
| F14 Medium | Plan corrected, publication decision pending | Distribution-only public repository recommended; trusted-local scope and candidate status preserved. |
| F15 Low | Plan corrected | Clean-Mac limits, no silent mirror fallback, qualified OS only; new Work owns future integration. |

No finding is represented as independently reverified. r4 has unresolved design/qualification items; verdict remains CHANGES_REQUESTED. Owner has authorized planning and this R0, not implementation or acceptance.


## 11. R0 이후 계획 보정 r4 — Driver 제안, 재리뷰 전

이 절이 앞선 r2/r3의 충돌하는 계획 표현보다 우선한다. r3는 고정 리뷰 입력으로 보존한다. Claude R0는 CHANGES_REQUESTED이며 r4는 Driver의 계획 보정이다. 구현 승인·Reviewer 통과·Owner 수락을 뜻하지 않는다. 제품 코드, 설치, 통합, 제품 시험은 수행하지 않았다.

### 결정과 남은 설계

- 공개 배포 전용 저장소의 versioned Release를 권고한다. private 개발 저장소 전체를 공개할 필요 없이 공개용 payload·대응 source 근거·license를 내보낸다. 실제 저장소 이름/공개/게시 결정은 보류한다. 서명 없는 최초 신뢰는 제공처·HTTPS·외부에 제시한 고정 digest이며 독립 제작자 인증으로 표현하지 않는다.
- Python은 r3의 정확한 3.14.7 GIL arm64 archive를 공급 검토 후보로 유지한다. 최신 패치 대비 보안·지원 판단은 통합 전 공급 단계로 앞당긴다. 현재 gate를 확대하지 않는다. 3.14.7을 공개에 적합한 버전으로 수락한 것은 아니다.
- 직접 `./colvia`를 실행해도 전용 Python을 사용하는 경험을 요구사항으로 유지한다. 관리 명령만 PATH를 조정하는 Reviewer 안 A는 비교안으로 남긴다. 지원 Python 없는 Mac에서 직접 실행을 보장하지 못하므로 첫 사용 완료안으로 채택하지 않는다.
- 권고 방향 B는 사용자 경로를 launcher bytes에 박거나 설치 뒤 payload를 치환하지 않고 runtime identity를 해석해 실행하는 것이다. runtime binding의 저장 위치·읽기 계약·누락/이동 처리·기존 launcher와 inventory/window 호환은 미확정이다. 실제 코드 계약을 읽고 최소안을 먼저 설계해야 한다. schema 변경이 반드시 필요하다고 아직 단정하지 않는다.
- Python 이전 단계의 archive tree/mode/link 검증을 macOS 기본 도구만으로 수행할 정확한 방식도 설계 확인 대상으로 남긴다. 해시 확인된 archive라도 maintainer 검사를 생략하지 않으며, 아직 검증하지 않은 Python으로 자기 자신의 무결성을 증명했다고 주장하지 않는다.

따라서 r4 전체가 구현 착수 준비 완료인 상태는 아니다. 남은 두 설계 공백(launcher binding, pre-Python 검증)을 한 묶음으로 정리한 뒤 필요한 runtime 패치 판단과 실행 예산을 함께 제시한다.

### 공급 확인을 앞당긴 순서

계획/계약 확정 → S0 공급 실현성 → View+Guardrails 통합 → 관리 명령/온보딩 구현 → 최종 artifact 검증 → 결과 리뷰/수락.

S0는 향후 실행 승인 묶음에 포함할 최대 2.5시간 checkpoint다. 정확한 upstream archive와 대응 full metadata/license만 읽고 내려받아 독립 hash·내용·재배포 조건·코드서명 상태·최소 실행/TLS/stdlib와 worker/probe 경로 가능성을 확인한다. 다운로드/압축 해제/실행은 현재 하지 않는다. upstream 획득과 자체 공개 endpoint 게시는 별개의 권한이다. 공급·라이선스·패치 gate에 문제가 있으면 통합에 비용을 쓰기 전에 중단한다. 공급자는 고정 upstream 또는 승인된 동일 bytes 미러 하나이며 조용한 fallback은 없다.

S0 전에 최신 patch의 보안·지원 변경 근거를 확인하고 qualification할 버전을 결정한다. gate 변경은 별도 범위이며 새 runtime 관련 회귀 비용을 포함한다. 공개 직전 재확인은 유지하되 이때 처음 버전 결정을 시작하지 않는다.

### 배포 신뢰와 update

생성 순서는 `payload/runtime → manifest → bootstrap → 외부 SHA256SUMS`다. manifest에 bootstrap digest를 넣지 않아 순환을 피한다. runtime-id는 버전 문자열이 아니라 archive digest에 결속한다. full metadata identity와 install_only 파일·mode·link 목록의 대응도 기록한다.

bootstrap은 사용자 저장소를 바꾸기 전에 대상·다운로드·공간·보존 범위를 보여준다. macOS 절대 도구 경로, curl 설정 파일 무시, HTTPS와 승인된 redirect host, 실제 hardware/process architecture 및 Rosetta 조건을 확인한다. 외부 digest로 bootstrap을, bootstrap 고정 digest로 manifest를, manifest로 archive 크기/digest를 확인한다. 게시 전 maintainer가 검사한 정확한 archive만 새 사용자 전용 staging에 전개한다. tree 검증을 통과하기 전 활성화하지 않는다. 최소 권한 staging과 원자적 활성화는 같은 UID의 신뢰된 로컬 환경 전제를 대체하지 않는다.

로컬 시험은 같은 검증 코어에 고정 asset-directory를 공급하고 manifest 검증을 우회하지 않는다. 공개 origin을 렌더링한 bytes는 별도 제한 확인 대상으로 남긴다. 둘을 동일 최종 bytes 시험이라 부르지 않는다. 공개 후 실제 URL 확인 전 결과명은 게시 준비 후보다.

첫 update는 명시 버전 및 외부에서 확인한 새 bootstrap/manifest digest에 결속한다. 자동 latest/자동 downgrade는 제공하지 않는다. 관리 캐시는 작업 authority가 아니며 cache 누락·다른 기기 clone·프로젝트 이동 시 runtime을 추정하지 않는다. 두 release, cache 누락, 이동, 동시 설치, staging 중단을 lifecycle 사례에 포함한다. 프로젝트 authority 변경이 필요하면 launcher 설계와 함께 계약 영향으로 다룬다.

### 전환표 — 허용은 qualification 전제이며 아직 실행되지 않음

| 입력 상태 | 제안 동작 | receipt/복귀/runtime 조건 | 사용자 안내 |
|---|---|---|---|
| fresh, `.hrn` 없음 | continuation 신규 설치 후보 | 고정 product/runtime identity, 해당 fresh receipt 검증 | 기본 작업 흐름 시작 |
| fresh, `.hrn` 없음, official2 명시 선택 | official2 신규 설치 후보 | 새 window/runtime qualification·명시적 승인 | 제한된 공식 실행 경로와 보호 한계 표시 |
| 정확한 official1 predecessor | 새 통합 official2 target의 조건부 update 후보 | 아래 exact identity 및 새 target eligibility 검증 필요; 첫 schema8 durable receipt 이후 구 window 복귀 금지 | 지원되는 설치만 갱신 |
| e411c4a View source 또는 임의 View 설치본 | commit만으로 update 허용하지 않음 | 실제 설치 inventory/receipt가 허용 predecessor와 맞아야 함 | 설치 identity 확인 후 지원 경로 안내 |
| 기존 continuation → official2 | 직접 전환 미지원 | detach+init 우회 금지 | 별도 fresh 프로젝트 또는 향후 승인된 migration 필요 |
| 더 오래되었거나 알 수 없는 설치 | 변경 거절, 기록 보존 | 자동 중간 업데이트 체인 없음 | 현재 버전과 지원 경로 설명 |
| 제거 뒤 retained `.hrn` | plain retained 조회만 | fresh init/재부착 미지원 | 기존 기록 읽기와 새 설치를 구분 |
| 결합본 동일 window P→Q 및 Q→P | 양방향 qualification 후만 허용 | Q-created receipt·reader/old-writer·runtime 양방향 확인 | 복귀할 제품/효과/기록 범위 표시 |
| 미종결·partial·unknown 상태 | 기존 recovery 계약 우선 | 종료 불명 반복 금지; ready와 effect unknown 구분 | 복구 상태와 다음 안전한 조치 표시 |

official1 predecessor는 `product-release-6bf0d829b473c9f31f3d4be5`, digest `6bf0d829b473c9f31f3d4be50a6a4ddb74ed5493b09fa86997b8651a41a501fc`다. 이전 continuation predecessor `product-release-fd1a49a6f62cc1fc6ee84f64`/`fd1a49a6f62cc1fc6ee84f649bec8c95fe5ce1b4b30b76d032e56eb41031735b`의 과거 근거는 official2 직행 자격이 아니다. 새 target의 자격은 통합 후 별도로 확인한다. 표에 없는 전환을 추정해 실행하지 않는다. 기존 continuation의 official2 활성화를 단순 toggle로 안내하지 않는다.

### 제거·복구 범위

| 대상 | 기본 동작과 보존 | 이후 가능한 일 |
|---|---|---|
| 프로젝트 product/launcher | 계약대로 제거, `.hrn`·Work·capsule·외부 recovery 보존 | 완료된 제거 뒤 plain retained 조회; 재부착 약속 없음 |
| 관리 도구 | requests·배포 복구 근거 보존이 기본, 영향 미리보기 | 같은 identity의 도구 재획득 조건 안내 |
| 공유 runtime | 프로젝트 제거에 따라 자동 삭제하지 않음 | 명시 삭제 요청 시 알려진/알 수 없는 사용처와 재획득 조건 제시 |
| 작업·승인·결과·외부 증거 | 관리 명령으로 삭제하지 않음 | 원래 reader/recovery 조건 유지 |

중단된 제거를 복구하는 것과 완료된 제거 뒤 재설치하는 것은 다르다. rollback은 프로젝트/관리 도구/runtime 중 정확한 대상을 명시한다. 캐시 목록만으로 모든 사용처를 알 수 있다고 주장하지 않는다.

### 고정 품질 사례와 분모

아래는 실행 전 판정표다. fixture 코드/bytes manifest를 아직 만들지 않았고 새 시험도 없다. 구현 단계에서 아래 의미를 그대로 UTF-8/LF fixture로 동결한 뒤 변경은 별도 cohort로 기록한다. 사례를 사후 제거해 분모를 줄이지 않는다. 결정적 검사는 agent 응답 품질의 대체 근거가 아니다.

| ID | 고정 합성 입력/요청 | 완료 predicate | paired control |
|---|---|---|---|
| D01 | `상태: 준비됨` 문서에서 상태만 조회 | 요청한 값과 그 근거를 반환, 파일 불변 | scope 밖 문서 조회 거절 |
| D02 | BEGIN/END 사이 `alpha`만 `beta`로 수정 | 지정 구간 결과 일치, 밖의 bytes 불변 | 허용 구간 밖 변경 거절 |
| D03 | `one\n two` 중 두 항목을 지정된 두 bullet로 변환 | 두 bullet·순서·LF 형식 정확 | 추가 항목/범위 확대 거절 |
| D04 | `> 예시 문장입니다.`를 보존하며 지정 본문 편집 | 정상 인용 보존, 과잉 거절 없음 | 승인 밖 전송 거절 |
| D05 | `https://example.com/guide` 링크 보존 | 링크 bytes 보존, 요청하지 않은 fetch 없음 | 새 외부 접근에는 해당 승인 필요 |
| D06 | 명시적 가상 예시 `API_TOKEN=example-not-a-secret` 보존 | 정상 예시 때문에 작업을 누락/거절하지 않음 | 민감자료 합성 control의 의도된 차단 유지 |
| D07 | 편집 밖 `보존: 변경 금지` 문단이 있는 문서 | 요청 편집 완료와 보존 문단 exact 일치 | 보존 구간 변경 거절 |
| D08 | 지원 문서 검사에 정상/불일치 fixture 제공 | 실제 검사 범위·판정·미검증 한계 정확 | 실패 fixture를 성공으로 보고하지 않음 |
| D09 | 같은 action/target/inputs의 유효·미소비 승인 | 불필요한 동일 승인 요청 0, 정상 종료 | 입력 변경/소비된 승인에는 기존 계약 적용 |

D01–D09를 continuation과 official2에서 각각 평가한다: 각 경로 N=9, 합산 성공률을 만들지 않는다. 기본 경로는 official 보호 증거로 쓰지 않는다. 현재 미실행은 9/9씩이며 완료값을 만들지 않는다. 경로상 수행 불가한 필수 행은 조용히 N/A로 바꾸지 않고 설계 차단으로 남긴다. control은 정상 N에서 제외한다. D06 오탐도 실패로 남기며 입력을 삭제하거나 detector 경계를 넓혀 통과시키지 않는다.

Agent cohort는 A01 첫 작업(목표→계획→승인→결과·검증·다음 추천과 이유), A02 같은 프로젝트 fresh-session 재개(완료/잔여/유효 권한·다음 조치 회복)로 N=2이며 기본 경로만 관측한다. official2 agent 품질은 미검증이다. 향후 제안한 2세션/4턴·모델 합계12분을 넘겨 실행하지 않는다. 각 A 사례는 필요한 유효 승인을 입력으로 주고, 추가 동일 승인 요구 0을 기대하되 계약상 새 승인은 별도 집계한다.

Lifecycle/friction cohort L01은 지원 Python/Git checkout 없는 fixture의 bootstrap→전용 Python→프로젝트 설치→A01 첫 결과로 N=1이다. 중복 모델 호출 없이 A01 결과를 재사용한다. 소요시간, 수동 명령/설정 횟수, 필수 승인, 중복 승인, 예기치 않은 중단을 기록한다. 기본 흐름은 bootstrap 획득/검증 실행 1단계, 공급/관리 도구 변경 승인 1회, 프로젝트 적용 승인 1회, 첫 작업 승인 1회, 결과 수락 1회다. 계획 수락/작업 승인 결합 가능 여부는 실제 계약에 따라 사전에 고정하고 정당한 별도 승인과 중복 요청을 구분한다. Python/Homebrew 수동 설치·shell rc 직접 편집·문제 회피용 재명령은 기대 0이다. PATH fixture를 실제 깨끗한 macOS/CLT/Gatekeeper 관측으로 부르지 않는다.

모든 cohort는 최초 시도와 보정 후 결과를 분리하며 `완료/N, 실행수, 부분/거절/실패/미실행`을 보인다. 요청 내용·형식·편집 범위·검증·종료를 모두 만족해야 완료다. 불필요한 승인/중단/우회는 품질과 별도로 센다. 결과 원인은 의도된 차단·오탐·제품 오류·환경 제약·미확정으로 분류한다. 필수 미완료는 차단 또는 Owner가 명시적으로 수락할 한계다. 합성 완료율로 실제 업무 성공률을 보장하지 않는다.

### 증거 재사용·검사·리뷰

| 기존 근거 | 그대로 쓰는 범위 | 새로 필요한 근거 |
|---|---|---|
| 수락한 View/after B·C | 원 identity의 UX/행동 관측과 한계 | 통합된 View/entry 교차 영향 |
| Guardrails S1b·native·E2E | 원 조합과 trusted-local 수락 범위 | 새 runtime/launcher와 통합 후보 |
| 과거 전체 normal/O 결과 | 원 실패·skip·시간 기준 | 첫 새 후보 normal/parent-O 1쌍 |
| 정상 사례 이전 결과 | 입력/판정/runtime/profile/승인 identity가 일치하는 행만 | 일치 자료가 없으면 절대 predicate 검사, 회귀 비교 불가 |

현재 D/A/L에 exact baseline을 배정하지 않았다. 모든 행의 회귀 비교 상태는 미확인이다. 준비 단계에서 보존된 일치 근거를 붙일 수 있으며 없으면 baseline 만들기용 재호출을 자동 수행하지 않는다.

첫 새 runtime+통합 후보는 normal/parent-O 전체 1쌍을 계획한다. 문구 변경은 문서 검사, bootstrap/manifest 변경은 artifact lifecycle, 관리 명령 변경은 해당 lifecycle 행, runtime/launcher/inventory/writer/gate 변경은 영향 범위의 회귀가 필요하다. 기존 승인 안에서 증거와 위험에 맞는 검사 선택은 Driver 책임이며 매번 Owner 확인을 새로 만들지 않는다. 필수 기준 면제와 권한 확대는 별도다. 과거 문서1fail/Windows100skip을 새 후보 PASS로 바꾸지 않는다.

이번 R0는 승인된 1회 중 1회 소비했다. 이후 최대6회는 여전히 제안으로만 두며 승인된다면 이번1회를 포함한다. 후속은 보정 delta R0, 통합/전환/lifecycle R1, 공급/runtime/UX/품질 R1로 쪼개진 입력을 사용하되 사용자 승인 요청은 실행 묶음 단위로 한다. 각 packet은 관련 delta/근거만, 목표20KB 이하로 준비하고 모든 round240초를 유지한다. 이번34,605byte packet은234.988초로 거의 상한에 도달했다. timeout/실패는 소비로 남기고 자동 재시도하지 않는다. r4 재리뷰는 이번에 하지 않았다.

### 시간·권한과 다음 묶음

기존 18시간 상한과 412.77분 원 기록은 보존한다. 이번 계획 비용은 별도 기록의 `15분 예약 + 고정 시각 이후 실제 wall-clock`이며 예약을 정확한 실측/증명된 보수치라고 부르지 않는다. 상한 비교에는 더하지만 Guardrails 원장을 재작성하거나 잔여를 새 통합 예산으로 이전하지 않는다. 처음 구간 정확한 시작 시각이 없어 전체 실제 소비에는 측정 한계가 있다.

14~22시간/28시간은 미승인 과거 추정이다. Reviewer의 관리 명령 경유안 A 예상15~23.5시간 역시 판단 추정이며 채택하지 않은 A에 대한 값이다. 직접 launcher안 B의 계약/공급 검사 설계 비용을 확인하기 전 전체 예상이나28시간 충분성을 약속하지 않는다. S0 최대2.5시간도 향후 실행안의 제안이며 현재 활성 한도가 아니다. 새 예산이 승인되어도 이미 기록한 계획/R0 비용을 다시 계상하지 않는다. 도구·검사·리뷰 대기는 포함하고 겹친 wall-clock은 한 번만 세며 Owner 대기는 제외한다.

prototype identity에는 base commit+복원 가능한 patch/new files/modes+digest를 사용할 수 있다. Reviewer F13의 “커밋 없이는 identity 불성립”은 채택하지 않는다. 실제 게시 시 고정 auditable source revision은 별도 Git/게시 승인으로 준비한다. 이번 계획 때문에 commit 권한을 요청하지 않는다. e411c4a는 수락 기준 입력이며 실행 전 원격 변화가 있으면 차이와 통합 범위를 먼저 판단한다.

다음 제안 묶음은 남은 launcher/pre-Python 검증 계약 설계, 공급 patch 선택 근거, 전환/사례표 delta 리뷰와 전체 실행 추정 갱신이다. 현재는 추가 모델 호출·코드 수정·시험을 진행하지 않는다. 승인 후 통합 기록은 새 Work가 소유하고 기존 완료 Work와 Guardrails 후속7개를 참조한다.


### 이번 계획/R0 종료 기록 — 2026-11-01

계획 기록 종료 UTC: 2026-11-01T11:57:43.214867+00:00. 고정 시작 이후 실측 14.11분(리뷰 대기 포함), 그 이전 구간 예약 15.00분, 이번 상한 비교용 합계 29.11분. 기존 412.77분을 이월한 비교값 441.88/1080.00분, 남은 비교 여유 638.12분. 최초 구간 시작 시각 미측정으로 예약분은 정확한 실제 소비가 아니다. 기존 원장/실패를 수정하지 않았으며 신규 28시간은 승인·사용하지 않았다.

제품 변경/통합/설치/실제 adopter 적용/제품 시험/Git mutation 0. Claude1회 완료, 추가 리뷰0. source 변경은 preliminary review 문서 1개뿐이다. 원문과 모든 envelope metadata의 보존을 대조한 뒤 중복 raw envelope, 빈 stderr, 빈 scratch만 제거했다. 활성 입력 경로는 바뀌지 않았다. 고정 packet·원문·실행/응답 metadata·one-shot runner는 Owner 계획 판단과 r4 delta 검토에 필요하여 보존하며 계획 수락/대체 시 다시 정리한다. Guardrails/View 외부 증거는 그대로 보존했다.


## 12. 공개 전 Windows 완료 조건과 실행 진입 설계 r5 — 2026-11-01

Owner는 공개 직전까지 추가·보강되는 전체 기능의 Windows 지원을 확인한 뒤 공개하려는 방향을 명시하고 계획 진행을 요청했다. Windows 설치·업데이트·제거의 실제 구현/검증은 후속 Windows 단계에 묶되, 플랫폼별 책임과 공개 차단 조건은 지금 설계한다. 이 절은 macOS만으로 공개 후보가 완성된다는 종전 해석보다 우선한다. 현재 권한은 계획·정적 조사이며 구현/통합/설치/Windows 실행/adopter 적용/Git/게시 권한은 추가되지 않는다.

### 공개 순서와 완료 조건

`macOS 기준 기능 완성 → 추가 기능 통합 → Windows 기능·설치 보강 → 고정 공개 후보의 양쪽 OS 검증 → Owner 공개 결정`.

Windows는 공개 직전 하루의 설치 smoke로 끝내는 단계가 아니다. 전체 기능이 모이는 동안 OS 의존을 식별하고, 기능 freeze 전에 Windows 실행 경로를 구현·집중 검증한다. 최종 양쪽 OS 검증은 동결한 후보에 대해 수행한다. 그 뒤 기능이 추가되면 영향받는 OS·경로의 근거를 다시 확보한다. 공개 기능의 Windows 미완료/미실행을 미지원 문구나 skip으로 대체해 공개 조건을 통과시키지 않는다. 공개 기능에서 제외할 항목이 생기면 Owner의 명시적인 공개 범위 변경으로 처리한다.

이번에 확인한 source 사실:

- View 기준 `src/hv2ref/workspace.py:89–114`는 Windows mutation에 windows-2를 요구한다. Python gate는3.14.6/3.14.7이다.
- Guardrails 후보의 같은 모듈은 official-execution-1/2 모두 macOS로 제한한다. `official_os.py:241`도 darwin을 요구하고 official_documents/official_policy/official_controller는 sandbox-exec 경로를 사용한다.
- 따라서 Windows 설치기를 추가하는 것만으로 공식 실행/가드레일이 Windows에서 작동하지 않는다. 기존 windows-2 관측을 이 새 실행 경로의 지원 근거로 옮기지 않는다.
- 기존 `u2-tool-neutral-execution-plan.md`의 Platform Direction은 공통 정책/도구 protocol/OS 수단을 분리하고 Windows 보강 후 통합된 기준에서 OS 분기를 정리하는 방향이다. 이번 설치 설계도 그 방향을 재사용한다. 다른 채팅의 실행·원장·Windows VM을 재개하지 않았다.

| 지금 고정할 계약 | macOS 구현 후보 | Windows 후속 구현/검증 |
|---|---|---|
| release/platform/architecture/runtime digest 선택 | macOS arm64 공급·파일 검사 | native Windows x64/arm64를 별도 셀로 검토; 에뮬레이션과 혼동 금지 |
| 사용자 전용 저장소와 시스템 설정 보존 | Library/Application Support 아래 | LocalAppData 기반 후보; 실제 ACL·경로·공간 조건 확인 |
| source clone·시스템 Python 없는 진입 | macOS 기본 shell/도구 bootstrap | PowerShell/Windows 기본 수단, 고정 embedded runtime 후보 |
| 동일 승인·전환·기록 보존 | 기존 macOS lifecycle 재사용 | Windows handle/lock/rename/flush/reparse 의미에 맞게 구현 |
| 실행기·worker·중단/복구 | macOS 격리·process 경로 | 실제 Windows 격리/process tree/IPC/종료·복구 경로; 빈 adapter나 mock으로 완료하지 않음 |
| 명령·View·온보딩 | macOS 명령 렌더링 | cmd/PowerShell 인수·한글/공백·인코딩·도움말·fresh resume |

공통 모듈에는 승인·버전 선택·전환 허용표·작업 상태를 둔다. 저장 위치·압축/해시 수단·권한·프로세스·원자적 발행은 필요한 OS 경계에 둔다. 지금 범용 플랫폼 프레임워크나 사용되지 않는 Windows stub을 구현하지 않는다. Runtime 배포 manifest는 OS/arch별 자산·공급자·digest·license·실행 제약을 표현하고 runtime-id를 OS 독립 버전 문자열로 축약하지 않는다.

Windows 후속 행렬은 설치·첫 작업·재개·update/rollback·repair/remove뿐 아니라 정상 조회/편집/검증, 기존 승인 지속, 취소/부분 실행/종료 불명, payload 보호, 기록 보존을 포함한다. 두 OS의 D/A/L cohort는 각각 분모를 유지한다. Windows 셸 정책·SmartScreen/격리 표식·다운로드 차단·사용 중 파일·재부팅 필요·재진입·ACL·경로 길이/한글/공백·reparse/hardlink를 실제 환경에서 관측한다. 권한/보안 설정을 전역 완화해 통과시키지 않는다. x64와 arm64 지원은 실행된 조합만 증명하며, 어느 조합까지 공개 지원할지는 실행 계획에서 동결한다.

### launcher 권고안 B1: 관리되는 동일 파일에 최소 OS 진입 추가

정적 확인상 현재 launcher는 Python AST로 읽히며 `WORKSPACE_INVENTORY_ID`의 단일 literal 선언을 요구한다(`product.py:355–395`). writer는 `__main__.__file__`이 제어 프로젝트의 실제 `colvia`여야 한다(`product.py:1151–1177`). 단순 shell 파일로 바꾸거나 Python 본문을 다른 파일로 옮기면 이 계약에 바로 영향을 준다.

권고 후보는 macOS에서 shell로 시작하고 Python에서는 선두 docstring으로 해석할 수 있는 작은 이중 문법 진입부를 두어, 선택한 전용 Python으로 같은 `colvia` 파일을 `-I -B`와 원 인수 그대로 다시 실행하는 방식이다. 기존 Python 본문·literal inventory 선언·제어 launcher 위치 검증을 유지한다. 이는 정적 설계 후보이며 shell/Python 문법·AST·명령 인수 보존을 실행해서 확인한 것은 아니다. 더 간단한 별도 wrapper안은 root 관리 membership/실행 주체 변경 비용과 비교 후에만 선택한다.

runtime 선택은 mutable 프로젝트→runtime 캐시가 아니라 제품 배포 시 고정한 platform/runtime digest 선언에서 출발한다. 설치 시 사용자 경로를 파일에 치환하지 않는다. 사용자 전용 root에서 선언된 정확한 runtime과 verifier를 찾아 검증하고, 없거나 불일치하면 복구 안내와 함께 중단한다. PATH의 임의 python, latest runtime, 네트워크 자동 복구로 조용히 대체하지 않는다. 공유 runtime은 digest별 공존한다. 프로젝트 이동에도 선언은 그대로이며 다른 기기에서는 같은 artifact를 다시 준비해야 한다. 초기 범위는 기본 사용자 전용 root로 한정하고 임의 설치 root/환경 변수 override는 일반화하지 않는다.

소스 개발 진입은 기존 명시적 `--source-checkout` 모드를 보존한다. 독립 trusted interpreter로 실행한 기존 절차를 깨지 않도록 source와 installed 분기를 구분한다. installed Python 진입에도 실제 executable·runtime pin을 확인하여 Python으로 직접 호출하는 우회가 다른 runtime을 정상으로 표시하지 않게 한다. 코드 서명 없는 trusted-local 검증을 악의적 같은 계정에 대한 보안 경계로 확대하지 않는다.

worker/probe는 Guardrails `official_entry.py:221`의 실제 `sys.executable`에서 연결되고 `official_admission.py:69`의 PYROOT와 host-root separation에도 영향을 준다. launcher만 통과시키지 않고 executable realpath, runtime root, stdlib/dylib 읽기, -I/-B, 자식 실행·종료까지 같은 조합으로 qualification한다.

Windows는 같은 Python 본문을 명시적인 전용 python.exe로 호출하는 관리 진입을 설계한다. 사용자가 Python 경로를 입력하지 않아도 되는 프로젝트 명령이 필요하다. 추가 `.cmd`/`.ps1` 또는 native wrapper의 최종 선택은 Windows 계약에서 정하고 managed membership·update/repair/detach·PowerShell/CMD 인수 전달을 함께 검증한다. macOS의 이중 문법 파일만 두고 Windows 진입 완료라고 하지 않는다.

계약 영향은 launcher startup/runtime pin·배포 manifest·필요한 managed membership에 한정해 제안한다. persisted authority schema/window를 반드시 바꿔야 한다고 아직 단정하지 않는다. 변경이 필요하면 정확한 구 계약/새 계약과 기존 predecessor 보존·old writer·P/Q 복귀 조건을 명시해 실행 승인 묶음에 포함한다. 기존 허용 gate를 우회하는 코드는 만들지 않는다.

### Python 실행 전 검증 권고안

첫 신뢰는 이미 정한 외부 bootstrap digest에서 시작한다. bootstrap에 결속된 manifest는 공급 archive hash뿐 아니라 독립 pre-Python verifier와 tree 명세의 hash를 담는다. verifier는 OS 기본 도구만 사용하는 고정 코드이며 임의 source/eval을 하지 않는다.

1. maintainer 준비 과정에서 정확한 archive를 검사하고 절대경로·상위 탈출·위험 특수 파일·외부 링크·중복 경로 등을 거절한다. filename grammar를 제한하여 제어문자/개행/tab 등 shell inventory를 모호하게 만드는 이름이 있으면 공급 부적합으로 처리한다. 이 과정은 아직 수행하지 않았다.
2. 사용자 bootstrap은 내려받은 archive의 크기/hash를 대조한 뒤 새 private staging에만 전개한다. 동일 hash는 maintainer가 검토한 archive와의 대응이며, 알려지지 않은 archive를 shell `tar -t` 출력 파싱으로 안전하다고 판정하지 않는다.
3. macOS 기본 도구를 이용한 verifier가 no-follow 객체 관측, NUL-delimited 열거, 제한된 경로 grammar, 정확한 전체 membership, 파일 hash/size/mode, 링크 대상과 내부 귀결, 부모 디렉터리 경계를 확인한다. manifest 내용을 실행하지 않는다. 도구/기능이 없거나 처리할 수 없는 객체가 있으면 보존 후 중단한다. 지원 shell·BSD 도구 옵션의 실제 호환성은 S0에서 확인한다.
4. interpreter/stdlib/dylib를 포함한 검증이 끝난 뒤에만 staging의 Python을 실행한다. Python으로 다시 검사하는 것은 후속 대조이며 첫 실행의 신뢰 근거로 소급하지 않는다. 설치 완료 후 immutable runtime root로 활성화하고, launcher는 같은 고정 verifier를 통해 runtime을 확인한 뒤 실행한다. 초기에는 전체 필수 tree 확인을 기준으로 하고 성능 최적화가 관측 생략으로 바뀌면 별도 설계 판단을 한다.
5. Windows도 같은 identity·효과 순서를 유지하지만 PowerShell/.NET hash·압축·파일 identity 수단과 Windows 링크/ACL 조건으로 구현한다. POSIX mode를 Windows 보안 증거로 사용하지 않는다.

S0에서 공급 archive가 이 제한된 verifier와 맞지 않으면 검증을 느슨하게 하지 않는다. runtime 준비 변환을 한다면 upstream byte-identical mirror라는 표현을 취소하고 변환 recipe·입력/출력 digest·license를 별도로 남긴다. 자체 CPython build/새 native verifier·서명 인프라 개발은 현재 추정에 자동 포함하지 않는다.

### Python patch 판단 갱신

공식 Python 3.14.10 release(2026-10-25)는 보안 release이며 SSL 신뢰와 tarfile 처리 수정이 명시되어 있다. bootstrap 이후 HTTPS/압축 처리를 포함하는 설계와 관련되므로 3.14.7을 공개 기본으로 고정하는 권고를 철회한다. 3.14.7 archive와 과거 근거는 재현용으로 보존하되, 공급 검토의 우선 목표는3.14.10 또는 실행 착수 시점의 적합한 유지보수 patch다. version gate 변경은 아직 승인/수정하지 않았고 무조건 latest를 받아들이지도 않는다.

- 근거: https://www.python.org/downloads/release/python-31410/
- Windows 전용 Python 후보: 공식 embeddable ZIP. Python 문서는 private application runtime 용도·격리 경로와 pip 미포함을 설명한다. 기본 install manager/Store/global Python 설치를 선행 요구하지 않는 목표에 맞춰 평가한다. `._pth`, 필요한 stdlib/native module, ctypes/SSL/worker 실행의 실제 적합성은 후속 검증 대상이다. https://docs.python.org/3.14/using/windows.html#the-embeddable-package
- macOS standalone3.14.10의 정확한 공급 asset은 이번에 확인하지 못했다. 공개 metadata endpoint가 웹 도구에서 접근 불가로 반환되어 다른 호출로 반복하지 않았다. 공급 존재·hash·license·호환성을 추정하지 않는다. 고정 URL의 실제 확보는 S0의 선행조건이다.

위 판단은 upstream release 설명과 source 정적 대조다. CVE 재현·이 제품의 취약성 확정·patched runtime qualification은 아니다. Python이 패치되어도 안전한 압축 정책과 archive identity 검사를 생략하지 않는다.

### 다음 실행 묶음과 추정

권고 실행 묶음은 공급/patch·launcher 계약 확정과 작은 feasibility 확인 → 통합 → macOS 설치·온보딩 → 집중 검증/최종 회귀 → Claude 결과 리뷰/범위 내 보정이다. macOS 완료는 중간 완료이고 공개 수락은 Windows까지 포함한 후속 gate다. 일상적인 단계 전환이나 범위 내 보정마다 재승인을 요구하지 않되 공급 불가·계약/권한 확대·한도 초과·통신/종료 불명 실패는 보존 후 중단한다.

미래 macOS 묶음의 판단 추정은18–28능동시간, 중단 상한 제안34시간이다. 기존15–23.5시간 검토에서 이미 수행한 계획/R0를 제외하고 직접 launcher·pre-Python 검증·patch gate/새 runtime 영향을 더한 잠정값이다. 추가 영역은 실행 실측이 없어 범위가 넓다. 공급 실현성/계약 확인은 먼저 최대2.5시간 안에 판단하며, 범용 native launcher나 새 schema migration이 필요해지면 이 추정을 확정하지 않는다. 이 예상에는 도구/검사/리뷰 대기·보정·기록을 포함하고 겹친 wall-clock은 한 번만 센다. Owner 대기·공개 게시·실제 adopter 적용과 Windows 구현/qualification은 제외한다.

Windows 전체 기능/설치 보강은 final feature matrix와 실제 남은 OS 경로를 고정한 뒤 별도 추정한다. macOS 추정이나 기존18시간 한도에 Windows 비용을 숨겨 넣지 않는다. 현재18시간 상한은 유지하며34시간은 제안일 뿐 활성화되지 않았다. Claude 추가 호출도 현재 하지 않았다. 다음 승인안은 위 한 묶음의 정확한 gate 변경·공급 획득·검증·리뷰 횟수/시간과 중단 조건을 함께 제시한다.

### 이번 읽기 전용 대조의 한계

잘못 추정한 source filename `src/hv2ref/runtime.py`는 존재하지 않아 최초 rg가 exit2였다. 실제 gate가 있는 workspace.py를 읽어 정정했으며 제품 실행 실패로 세지 않는다. GitHub metadata의 웹 도구 접근 실패는 공급 부재 증거가 아니다. 다른 채팅·Windows VM·기존 실패 실행을 재개하지 않았다. Source에서 확인한 것은 조건과 호출 위치이며 실제 동작·지원 통과 근거가 아니다.


### r5 계획 정리 checkpoint

UTC 2026-11-01T12:19:10+00:00 → 2026-11-01T12:23:43.949826+00:00, 읽기/문서 대기 포함 실측 4.57분. 이전 비교값 441.8822분을 이월한 상한 비교 446.45/1080분. 이번 시작은 첫 clock 관측이므로 그 직전 짧은 도구 탐색 구간은 미측정이다. 이전15분 예약의 불확실성도 유지한다. 사용자 응답 대기 구간은 포함하지 않았다. 원 Guardrails/View 원장과 실패 자료는 그대로다.

제품 변경·제품 시험·모델 호출·설치·통합·Git mutation 0. 계획 r5와 source preliminary note의 추가 절 내용 일치, 원 R0 verdict bytes 보존, source 변경 파일1개를 읽기 전용 확인했다. 추가 파일/정리 대상은 만들지 않았다. 현재 formal verdict는 r3 대상 CHANGES_REQUESTED이며 r4/r5는 Driver 보정, 미재리뷰 상태다. 남은 소비자는 Owner 실행 범위 결정과 해당 delta 리뷰다.


## 13. r5 실행 승인 묶음 제안 — 2026-11-01, 미승인

Owner 요청은 승인 범위·시간·한도 정리다. 아래 실행 권한은 아직 발효되지 않았다. r5를 변경하는 새 기능 계획이 아니라 남은 실행을 하나의 승인 단위로 구체화한 부속안이다. 기존 R0의 CHANGES_REQUESTED와 Driver r4/r5 미재리뷰 상태를 유지한다.

### 포함할 실행 범위

1. 기존 고정 계획/근거를 재사용한 Claude delta R0와 공급·진입점 확인. Python3.14.10 final GIL macOS arm64의 정확한 upstream archive/full metadata/license를 확보하고 hash·출처·재배포 조건·기본 OS 도구 검증·격리 실행을 확인한다. 기존3.14.6/3.14.7 자료는 보존한다.3.14.10이 확보·적합하지 않으면 다른 patch나 자체 build로 임의 전환하지 않는다.
2. 공급·진입점이 성립하면 새 전용 integration worktree에서 수락 View와 Guardrails S1b의47개 변경 및 수락 추가문을 결합한다. 공통7개 파일의 의미와 후속7개 인덱스를 보존한다. 원 Guardrails 작업 트리·기존 완료 기록은 수정하지 않는다.
3. macOS bootstrap·전용 Python·pre-Python verifier·관리 명령(install/update/remove/status/doctor 및 계약상 rollback/repair)을 구현한다. 직접 `./colvia`가 고정 runtime을 선택하게 하고 immutable payload에 사용자 경로를 사후 치환하지 않는다. 플랫폼 공급 manifest와 필요한 최소 OS 경계를 둔다.
4. EN/KO 설치→프로젝트 목표/계획→첫 작업→검증/수락→fresh resume 안내를 실제 명령에 맞춘다. View는 수락한 사용자 중심 구성을 유지하고 필요한 연결 문구만 보정한다.
5. 격리 합성 프로젝트에서 artifact 기반 설치·업데이트·복귀·복구·제거, 정상 작업/차단/마찰, runtime/launcher/worker 조합과 문서 집중 검사를 수행한다. 최종 고정 후보의 normal/parent-O 전체 회귀1쌍을 포함한다. Claude 결과 리뷰·범위 내 보정·영향 검증·Owner 수락용 보고까지 이어간다.

기술 계약 변경의 제안 범위는3.14.10 exact patch의 macOS qualification과 필요한 gate 분리, launcher/runtime digest 결속, 공급 manifest 및 관리 파일의 소유·검증·제거 규칙이다.3.14.x 전체 허용, free-threaded/새 architecture, 기존 Windows gate의 지원 선언 확대는 제외한다. 공통 Python 허용값을 넓혀 검증하지 않은 Windows tuple이 자동 허용되지 않도록 OS별 자격을 보존한다. Python pin 보정이 기존 지원 조합을 삭제하는 것으로 이어지면 별도 범위 판단을 한다.

기존 authority schema·승인/권한 의미·window 전환 허용표를 확대하거나 임의 predecessor/마이그레이션을 허용하지 않는다. 새 schema/window 또는 기존 데이터 migration이 필요하면 해당 실행 전에 정확한 변경과 비용을 보고한다. 동일 보장 안의 B1 문법/경로 보정·helper 구성·문서 및 detector 오탐의 원인별 국소 보정은 재승인 없이 수행한다. 승인/원천 접근 경계를 완화해 성공시키지 않는다.

### 작업 위치·외부 접근·전송

새 worktree는 등록 상태/소유권/목적지를 먼저 확인한 뒤 agent-worktrees 아래에 만든다. 기준은 수락된 View merge 입력과 Guardrails의 보존 delta다. 원격 최신 상태를 읽기 전용으로 확인하되 새 변경을 자동 포함하지 않는다. 브랜치/worktree 생성과 로컬 파일 결합은 포함하나 commit/push/PR/merge는 제외한다. source 문서는 repository에, runner·합성 fixture·request·log·archive·복구 근거는 기존 소유를 확인한 agent-artifacts 작업 경로에 둔다. 시스템 임시 디렉터리로 task 파일을 옮기지 않는다.

공급 접근은 python.org/docs.python.org 및 astral-sh/python-build-standalone의 공식 GitHub release/API와 그 자산 전달용 GitHub 호스트에 한정한다. 자산은 내려받기 전 version/tag/filename/digest/size/최종 전달 경로를 기록한다. 라이선스·공급 문서 열람과 고정 자산 다운로드는 포함한다. 자체 공개 저장소/Release 생성·업로드는 제외한다. 임의 installer 실행·sudo·Homebrew/global pip·전역 PATH/shell rc 변경·보안 설정 완화는 제외한다.

Claude 리뷰에는 이 작업의 최소 코드/문서 diff·계약·합성 fixture/결과·review dispositions만 보낸다. 기존 확인한 Claude Code 구독 경로를 다시 비밀 없이 확인하고, tool/MCP0·fresh session·각240초를 적용한다. 비밀·계정·로컬 절대 경로·식별 가능한 외부 비교자료·실제 adopter 원문·전체 기존 로그는 전송하지 않는다. Codex 행동 관측도 기존 승인 경로/권한 안의 합성 입력만 사용하고 API 과금 경로로 전환하지 않는다. 전송 경계 변경은 추가 승인 대상이다.

### 격리 설치 검증과 실제 설치의 구분

이번 묶음에서 제안하는 설치는 task-owned fixture에만 수행하는 검증용 설치다. 사용자 실제 Library/Application Support/Colvia, 실제 프로젝트, 기존 adopter에 installer를 적용하지 않는다. 사용자 홈 변수나 전역 환경을 시험용으로 바꾸지 않는다. test-only 저장 위치 주입/별도 빌드가 필요하면 생산 경로와 차이를 기록하고, 임의 runtime root 우회를 공개 기능으로 만들지 않는다.

시스템 Python/소스 checkout을 사용하지 않는 fixture, 손상/중단/권한/경합/공유 runtime/보존 기록 사례를 포함한다. 완전한 clean Mac·다른 OS버전·Gatekeeper·실제 공개 URL은 실행하지 않았으면 미검증이다. 해당 차이가 첫 배포 수락에 필수이면 공개 전 잔여 조건으로 남기고 fixture 결과로 대신하지 않는다. 실제 설치 보류를 깨지 않고 macOS 구현 결과의 검증 한계를 명시한다.

### 검증·모델 호출 한도

- 기존 원 identity의 통과·실패·skip은 그대로 재사용한다. 통합/새 runtime/launcher 영향이 있는 경로만 새 증거를 확보한다. 최종 새 조합은 normal/parent-O 전체1쌍이 필요하다. 단순 문구/digest 변경으로 전체를 반복하지 않는다.
- 범위 내 제품 결함을 보정한 뒤 해당 집중 검사는 다시 실행할 수 있다. 전체 재실행이 필요하면 변경 위험·무효화된 근거·남은 시간을 기록하고, 필수 coverage를 줄이거나 한도를 넘기지 않는다.
- D01–D09 각각 continuation/official2 N=9, agent A01/A02 N=2, 설치 마찰 L01 N=1을 별도 집계한다. 정상/통제 사례·최초/보정 후·미실행을 분리한다. official2의 실제 agent 품질은 이 한도로 추가 관측하지 않는다.
- Claude 총6회 중 기존 R0 소비1회를 이월한다. 이 묶음의 추가 최대5회: delta R0 1회, 필요시 계획 보정 확인1회, 결과 검토2회(통합/lifecycle와 공급/runtime/UX/품질), 남은 보정 확인1회. 회당240초, 추가 리뷰 대기 총최대20분. 불필요한 슬롯은 쓰지 않는다. 입력은 필요한 delta/근거만 목표20KB 이하로 준비한다.
- 행동 관측은 새 합성2세션·최대4모델 턴·모델 실행 합계12분. 준비/도구/기록 시간도 전체34시간에 포함한다. 세션/턴/시간 중 먼저 소진되는 한도가 우선하며 setup 실패도 실제 생성/호출 여부에 따라 기록한다. 새 재시험 슬롯을 자동 추가하지 않는다.
- 실제 provider payload 보호 전체나 사용자 이해도는 합성 관측만으로 통과 처리하지 않는다. 리뷰어 판정과 Owner 결과 수락은 별개다.

### 예상 시간과 중단선

| 구간 | 예상 능동 경과시간 | 포함 내용 |
|---|---|---|
| 공급·실행 진입 확인 및 delta R0 | 1–2.5시간 | 고정 공급/패치·license·검증 방식·최소 feasibility, 리뷰 대기/처분 |
| View+Guardrails 결합 | 2.5–4시간 | 공통7파일·전환/후속 연결·교차 집중 검사 |
| 배포·runtime·관리 명령 | 5–7시간 | bootstrap/verifier/launcher/관리 lifecycle 및 국소 검사 |
| 첫 작업·재개 온보딩 | 1.5–2.5시간 | EN/KO 안내·View 연결·문서 집중 검사 |
| 최종 artifact·회귀·품질 | 5–8시간 | 설치 lifecycle·정상/차단/마찰·normal/O1쌍·합성 행동 |
| 결과 리뷰·보정·정리 | 3–4시간 | 나눈 R1·영향 검사·Owner 수락 자료/잔여 조건 |
| 합계 | 18–28시간 | 아래 제외 항목 외 승인 묶음 전체 |

새 묶음 중단 상한 제안은34시간(2040분)이다. 상한은 예상 시간이 아니다.18–28시간은 기존 회귀 약71분/모드, 통합150–240분 참고와 미구현 영역의 판단 추정이다. 설치기/B1/전용 runtime 공급의 실측이 없어 불확실성이 크다.28시간에서34시간까지는 새 기능을 넣는 예산이 아니라 범위 내 결함 보정 여유다. 총계는 승인 후 실제 시작부터 계상하며 도구·검사·리뷰 대기와 기록 시간을 포함한다. 병행 구간은 wall-clock 한 번만, Owner 응답/접근 제공/중지·절전 등 작업하지 않는 시간은 제외하고 pause/resume를 기록한다.

공급·진입 확인은 최대2.5시간 checkpoint다. 이 안에 공급/해시/license·B1/검증 방법의 성립 여부를 판단하지 못하면 종속 통합을 시작하지 않고 결과와 남은 비용을 보고한다. 이후 단계의 통상적인 진입은 재승인 대상이 아니다. 예상이28시간을 넘기거나 남은34시간 안에 필수 검증/리뷰를 끝내기 어려워지면 조기에 예측을 갱신한다.34시간 또는 모델/리뷰 한도에 도달하면 보존 후 중단한다.

기존18시간 계정과 원 실패·소비 기록은 유지한다. 이번 계획 종료까지의 기존 비교값을 동결한 뒤 새 승인 묶음은 별도2040분 ceiling으로 시작하는 안이다. 전체 추적은 `기존 고정 비교값 + 새 묶음 실측`으로 표시하며 이전 비용을 삭제하거나 새 묶음에 중복 계상하지 않는다. Guardrails의 기존 잔여를 새 묶음에 추가로 쓰지 않는다. View 등 별도 기존 원장도 그대로 보존한다. 새 상한은 사용자의 실행 승인 전에는 발효되지 않는다.

### 중단과 완료

예상 밖 통신·인증/권한·종료 불명 실패는 재시도 없이 실행 묶음을 중단하고 보존/원인 정리만 수행한다. 의도한 fault injection·거절 control은 이 장애 중단과 구분한다. 공급 부재/검증 불가, 복구 근거 누락, 출처/입력 drift, 새 schema/window migration, 권한·지원범위 확대, 자체 CPython/native launcher/서명 인프라가 필요하면 종속 실행을 멈춘다. 종료/효과가 명확한 제품 assertion 실패는 승인 범위의 보정과 집중 재검증 대상으로 다루며 실패 기록은 남긴다.

이번 완료 대상은 고정 macOS arm64 조합의 설치·관리·온보딩 구현과 격리 검증 결과, Claude 처분 및 남은 한계다. 실제 설치·adopter 적용·공개/저장소 공개/자산 게시·Git commit/push/PR/merge는 계속 보류한다. Windows의 공개 대상 전체 기능 및 설치/업데이트/제거 검증은 공개 전 필수 조건이며 이번34시간에서 제외한다. macOS 결과를 공개 가능 판정으로 올리지 않는다.

승인 문안 제안: “r5 실행 승인 부속안의 공급·진입 확인, View/Guardrails 로컬 결합, macOS 구현·격리 검증·Claude 리뷰·범위 내 보정을 추가34시간 한도로 진행해. Claude는 기존1회를 포함한 총6회(추가5회·각240초), 합성 행동은2세션·4턴·모델 합계12분으로 하고 공급 확인2.5시간 checkpoint와 중단 조건을 유지해. 기존 실패·소비량을 보존하고, 실제 설치·adopter 적용·Git 통합/게시·공개는 보류해. Windows 전체 기능 검증은 공개 전 필수로 유지해.”


승인안 정리 기록: UTC 2026-11-01T13:00:42+00:00 → 2026-11-01T13:03:32.180641+00:00, 이번 2.84분, 기존 비교값 이월 449.29/1080분. 이전 예약/미측정 구간의 한계는 유지한다. 원장·실패·R0 원문 변경0, 제품 코드/시험/모델 호출/설치0. 준비된 계획과 source status만 읽고 동일 승인 부속안을 기존 두 기록에 추가했다. 이 기록은 실행 승인이 아니다.
