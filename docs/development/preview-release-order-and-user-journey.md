# 첫 Preview의 지원 결정과 사용자 여정

2026-11-03 · Owner가 선택한 방향은 macOS와 Windows 동시 Preview 준비, 플랫폼별 수락이다. 아래 문안은 DR-0007의 공개 시점 개정 제안이다. 정확한 문안의 Owner 수락은 대기 중이다.

## 공개 시점 개정안

[DR-0007의 공개 순서](../decisions/DR-0007-windows-native-runtime-contract.md)와 [Windows 정식 지원 판정](windows-native-implementation-plan.md#completion-stop-and-retention) 중 ‘live macOS Preview 이후’라는 선행 시점만 다음으로 대체할 것을 제안한다. macOS arm64, Windows 11 ARM64, Windows 11 x64를 함께 준비하고, 각 환경에서 고정 배포본과 관측 근거를 기준으로 Owner가 Preview 지원 여부를 별도로 결정한다. 한 대상의 결과로 다른 대상을 수락하지 않는다. 동시 공개 목표일에 근거가 부족한 대상은 미결로 남기고 Owner가 시점과 표기를 선택한다.

Windows의 기존 10개 지원 판정 기준, 기술 activation, 배포본 재취득·동일성, 인증된 배포와 익명 배포의 구분, 실제 알림 클릭 조건을 유지한다. 공개 접근을 요구하는 항목은 해당 대상의 실제 배포 채널에서 판정하고, 선행 플랫폼 증거를 명시한 세부 기준과 충돌하면 해당 지원 결정을 열어 둔다. 플랫폼별 기록에 대상·버전·파일 식별값·실행 환경·관측 범위·잔여 조건·Owner 결정을 남긴다. 이번 선택은 실행·공개 승인을 부여하지 않는다.

정확한 개정 문안의 수락 기록: 대기. 수락 시 문안 식별값, Owner 응답과 날짜를 기록한다.

## 공개 전 문서와 사용자 흐름

1. 제품 문서는 설치·환경 확인·첫 Work·결과·재개, 업데이트·복구·연결 해제·지원 조건·문제 신고의 정본이다. 저장소 README에서 설치본에도 들어가는 [한국어 SQLite Preview 안내](../../manual/ko/foundation-preview.md)와 [영문 안내](../../manual/en/foundation-preview.md)로 연결한다. 운영 명령과 지원 한계는 제품이 소유한다. EN/KO 설명이 다르면 플랫폼별 수락 근거와 명령 계약에 맞춰 두 언어를 함께 수정한다.
2. 별도 학습 자료는 의도·작업·수락 개념, 작은 실습, 기대 결과와 회고를 다룬다. 공개 전 담당·초안·대상 제품 버전을 연결하고, 공개 가능한 제품 링크가 생기면 그 버전의 안내를 참조한다. 내부 사례·계정·채팅을 공개 예제로 가져오지 않는다.
3. 공개 표시명과 설명, 선택한 Apache-2.0의 배포물 적용 범위·문의 채널·버전별 다운로드/서명 안내를 결정한다. 제품명과 명령 변경은 별도 결정이다. 외부 배포 주소와 지원 표시는 확인 후 제공한다.
4. 새 안내를 포함한 소스와 최종 서명 바이트로 후보를 식별한다. [기존 후보 근거](product-evidence-and-followups.md#record-foundation-verification)로 달라지지 않은 설치·Work·호스트 경로를 확인한다. 각 최종 후보는 공식 주소 최초 설치와 같은 명령으로 갱신할 때의 관리자 선택, 바뀐 네이티브 연결·Git·권한·수신기 경계를 우선 확인한다. A 알림 열기와 B 전환, 새 대화 재개는 기존 근거가 현재 경로를 뒷받침하지 않을 때만 선택한다. 다운로드 차단과 미실행은 지원 판정에서 따로 기록한다.

### 최종 문서 정합성 · 공개 완료 조건

2026-11-11 Owner 결정. Windows x64 실기기를 포함한 플랫폼·호스트 검증과 남은 설치·지원·배포 판정을 마친 뒤, 공개 전에 최종 후보 기준으로 사람용 안내와 에이전트용 지침을 함께 검토하고 보강한다. 저장소 README와 기여 안내, 개발·기술 문서, 에이전트 진입 지침과 어댑터, 사용자 매뉴얼, 설치본에 포함된 안내를 대조한다.

같은 후보의 버전·실행 명령·기록 위치·권한과 수락 경계·지원 상태·복구 절차를 설명해야 한다. 기존 프로필과 새 기록 기반의 적용 대상을 표시하고, 한영 의미와 실제 저장소·설치본에서 열리는 링크를 확인한다. 검증 결과의 범위를 넘는 지원 문구, 잘못된 예제, 공개 식별정보를 수정한다. 설치본 바이트나 지침이 바뀌면 해당 후보의 변경분만 다시 검사하고, 영향이 없는 기존 근거는 재사용한다. 검토한 소스와 설치 후보를 식별하고 남은 예외를 기록한 뒤 최종 문서 완료를 판정한다. 이 조건은 플랫폼별 지원이나 공개 승인을 대신하지 않는다.

## 버전과 첫 배포 입력

제품은 0.x Preview에서 1.0 정식으로 진행한다. 지원 범위는 플랫폼과 사용한 호스트별 검증 근거에서 확인한다. 첫 Releases 제품 버전 0.1.0과 태그 `v0.1.0`, 먼저 공식 주소에서 검증할 Pages 기준판 `v0.1.0-preview.1`은 제안이다. 기준판도 접근 가능한 배포본이므로 필수 안전 안내와 지원 조건을 모두 갖춘다. 후속판은 안내의 실제 변경을 포함해 ZIP과 매니페스트를 분리하고 제품 순번을 올린다. 운영 신뢰·배포 주소·조립 입력과 태그는 해당 실행 단계의 승인을 거쳐 고정한다.

## 근거와 상태

개발 문서 작업 중. 격리 후보의 [알림 검증](FEAT-20261103-007-notification-work-detail.md#owner-수락과-완료)은 재사용한다. 보정 뒤 독립 재리뷰와 공개 후보의 도구별 네이티브 클릭은 그 기록에 남긴 범위대로다. 이 문서 변경으로 새 설치·실행·지원·배포를 검증하지 않았다.

계획·결과 정적 리뷰를 별도 세션에서 각 1회 진행했다. 결과 리뷰 의견을 반영해 Windows 도구 준비와 프로젝트 연결 미리보기의 차이, ZIP 검증, 알림 선택과 결과 제출의 구분, 갱신 후 새 EXE 확인, 연결 해제 후 한계를 명확히 했다. 최종 안내는 문서 집중 검사 대상으로 확인한다. 실제 설치본·도구별 클릭은 후보 고정 뒤 별도 검증한다.

## 이전 README·라이선스·기여 안내 제안

앞선 원고의 영문과 한국어 첫 화면은 어제 맡긴 인증 API 문서의 만료 응답 한 줄을 오늘 다시 검토하는 예제를 쓴다. 독립 한국어 README는 저장소에 두고, 영문 첫 화면의 한국어 링크는 기존 설치본 파일 목록에 들어가는 한국어 시작 화면을 연다. 이 경로는 공개 저장소 주소나 네트워크 연결에 의존하지 않는다. 이 버전의 자체 소스·문서 라이선스는 Owner가 선택한 Apache-2.0이다. 현재 배포물용 원문과 제3자 고지를 구분하고 과거 배포물은 유지한다. 공개 기여·Git 정책과 플랫폼별 안내는 수락 대기다. 외부에 공개할 저장소와 기록의 처분은 별도 비공개 점검을 따른다.

README·기여 정책의 계획·결과 리뷰를 각각 한 번 받았다. 결과 리뷰의 중간 우선순위 의견 8건을 반영했다. 보정 후 별도 독립 재리뷰는 진행하지 않았다. 개발용 macOS 두 구성과 Windows ARM64·x64 패키지를 열어 첫 화면과 시작 안내의 내부 링크와 문서 내 이동 위치 41곳씩, 한영 전환과 라이선스 원문 포함 여부를 확인했다. 기본 구성에 없는 문서를 가리키던 시작 안내 링크는 두 구성에 공통인 설명으로 연결했다. 실제 설치·알림 클릭·최종 배포 파일 확인은 플랫폼별 공개 준비에 남긴다.

## 사용자 개편 요청 반영 · 현재 원고

첫 화면은 출시 안내 세 건 가운데 근거가 있는 문구와 남은 결정을 보여 주고, 빠른 시작을 신규 사용자와 기존 사용자로 나눈다. 실습의 기준 자료는 예약 정책 메모이며 FAQ와 상담 답변을 함께 수정한다. 수수료 결정은 후속으로 남긴다. 공개 다운로드 주소·명령과 실제 소요 시간은 확인 뒤 반영한다.

[한국어 시작하기](../../manual/ko/getting-started.md)와 [English](../../manual/en/getting-started.md)는 언어별 독립 페이지다. 배포본에서는 영어 시작 안내와 문서 색인의 한국어 사용자 장을 서로 연결해 기존 파일 목록을 유지한다. 소스 매뉴얼과 설치본의 반복 구간은 릴리스 전에 대조한다. 일반 설명, 초급 엔지니어 구조 설명과 실습은 서로 연결한다. 별도 학습 자료는 실제 페이지와 적용 버전이 정해질 때 양쪽에서 연결한다.

개편 계획·결과의 정적 리뷰 2회를 수행했다. 첫 사용 조건과 수락·수신함·플랫폼 표현을 보정했다. x64 실행, 공개 다운로드, 최종 후보별 알림 클릭과 실사용 소요 시간은 별도 확인 대상이다.

## 공개 직전 문서 정리 기준

`docs/GETTING-STARTED.md`의 주 독자는 설치와 진단을 수행하는 에이전트다. 프로젝트 지침에서 이 문서로 진입해 설치 상태, 대상 경로, 적용 전 확인 사항과 다음 절차를 찾도록 한다. 사람이 읽는 첫 작업 실습은 [한국어 매뉴얼](../../manual/ko/getting-started.md)과 [English manual](../../manual/en/getting-started.md)에서 관리한다. 공개 직전 README의 시작 링크를 해당 언어의 사용자 안내로 연결하고, 저장소와 설치본 양쪽에서 링크가 열리는지 확인한다. 11월 4일 문서 후보에서는 두 언어의 실습을 설치본 색인 안에 각각 담고, 영문 README에서 실습으로 바로 연결했다. 설치·진단 절차에는 기존 책갈피를 위한 짧은 안내만 남겼다.

## 문서 언어와 배치 제안 · 11월 4일

2026-11-04에 Owner가 아래 배치안을 수락했다. 다음 문서 정비에서는 영문 README에서도 사람용 시작 안내로 들어갈 수 있게 하고, 설치본의 한영 안내 경로를 확보한 뒤 에이전트용 설치·진단 문서에서 중복 실습을 정리한다.

| 독자와 목적 | 위치와 언어 | 바뀔 때 맞춰 볼 곳 |
| --- | --- | --- |
| 처음 방문한 사용자와 기여자 | 루트 README와 CONTRIBUTING은 영문과 한국어 파일을 나란히 둔다. | 양쪽에서 대상 사용자, 사례와 정책이 같은지 확인한다. 공개 시 각 언어의 시작 안내로 연결한다. |
| 설치하고 프로젝트를 쓰는 사람 | 저장소 안내는 `manual/en/`과 `manual/ko/`에 전체 여정을 각각 쓴다. | 첫 Work와 수락, 재개, 알림, 갱신·해제 안내를 짝지어 수정한다. 설치본 안의 영문 실습과 한국어 사용자 장도 같은 행동을 안내해야 한다. |
| 명령·제약을 확인하는 사람 | 명령과 기술 계약은 기존 영문 레퍼런스를 기준으로 삼는다. 한국어 매뉴얼은 필요한 절차와 사례를 설명한다. | 명령·지원 범위 변경 시 두 매뉴얼과 설치본의 링크를 확인한다. |
| 프로젝트에서 작업하는 에이전트 | 공통 영문 진입점과 검증된 어댑터를 사용한다. Claude 진입점은 공통 지침을 참조한다. | 프로젝트 규칙, 플랫폼별 실행 방법, 어댑터가 가리키는 절차를 함께 대조한다. |
| 유지보수자와 학습자 | 과거 결정·검증 기록은 작성 언어로 보존한다. 별도 학습 자료는 개념과 연습을 맡는다. | 학습 자료를 공개할 때 제품 버전과 사용자 가이드를 양방향으로 연결한다. |

설치본의 영문·한국어 실습은 소스 매뉴얼을 기준으로 갱신한다. 원고를 바꾸면 저장소 루트에서 `python3 scripts/sync-first-work-guides.py --write`로 두 실습을 반영하고, 옵션 없이 실행해 일치 여부를 확인한다. 언어 전환과 도움말 링크는 배포 파일 안에서도 확인한다.

## 첫 작업 실습 진입 경로 · 11월 4일 · Owner 수락·완료

Owner가 사용자용 한영 실습과 에이전트용 설치·진단 안내의 분리를 수락했다. 깨끗한 VM에서의 사용성 확인은 공개 후보 단계에 남긴다.

영문 README의 첫 작업 링크와 한국어 전환은 설치본에도 들어가는 각 언어의 실습을 연다. 저장소 한국어 README에서는 한국어 매뉴얼을 바로 연다. 에이전트의 설치·진단 절차와 예전 실습의 책갈피는 같은 경로를 유지한다.

소스에서는 두 README의 진입점, 실습 사이 언어 전환과 실제 렌더링된 앵커를 확인했다. macOS 두 프로필, Windows ARM64·x64 시험 배포 파일에서 각각 링크와 책갈피 44개를 대조했다. 원고 불일치 감지와 갱신도 두 언어 모두 확인했다. 독립 계획·결과 리뷰를 마쳤고, 결과 리뷰의 두 확인 요청은 소스 링크와 앵커 태그를 직접 검사해 해소했다. 공개 주소에서의 다운로드, 화면 읽기 프로그램의 발음과 깨끗한 VM에서의 사용성은 이 검사에 포함되지 않는다.

## 후속 후보 · 민감정보가 있는 작업

- 평소에는 일반 작업으로 진행한다. 고객 자료를 다뤄야 할 때는 원본을 읽기 전에 사용자가 보호 경로를 선택할 수 있게 한다. 사람 이름·연락처와 함께 고객사명, 내부 프로젝트명, 문맥으로 고객을 알아볼 수 있는 표현을 다룬다.
- 보호 경로에서는 로컬에서 가명을 붙인다. 고객 간 구분과 조사, 누가 무엇을 언제까지 하기로 했는지 보존한다. 사용자가 사본과 요청문을 함께 확인하고, 작업·내용·받는 곳이 바뀌면 다시 확인한다. 원본·대응표 직접 읽기와 우회 전송을 막을 수 있는지 검증한 경로에서만 지원 범위를 정한다. 일반 채팅에 직접 붙여 넣은 내용은 별도 경로다.
- 재검토 조건은 같은 합성 입력에서 누락·오탐, 고객이나 약속의 뒤바뀜, 실제 검토 수고, 승인 사본 외 입력 차단을 함께 비교할 수 있을 때다. 규칙·고객 사전을 기준으로 보조 모델이 더하는 효과와 비용을 판단한다. 실제 고객 자료 사용과 제품 적용은 별도 결정이다.
- 가명 사본 요약과 근거 문장 바로가기는 선택형 후속 후보다. 긴 기록에서 고객별 약속 확인이 실제로 어렵다는 사례가 생기면 다시 검토한다. 공개의 선행 조건으로 두지 않는다.


## 첫 Preview 기능과 매뉴얼 제안 · 11월 4일

사용자 검토 대기. 사람용 안내는 [한국어](../../manual/ko/work-guide.md)와 [영문](../../manual/en/work-guide.md)에서 같은 열두 가지 일을 같은 순서로 다룬다. 다음 표는 공개 지원을 판단할 때 다시 확인할 근거다. 기능 식별자는 PRODUCT-CAPABILITIES.json의 항목과 대응한다. 소스의 기능 상태와 이미 수락한 개별 사례, 공개 후보의 플랫폼 판정은 각각 유지한다.

| 순서 · 기능 식별자 | 제안과 근거 |
| --- | --- |
| 1 · guided-intent-formation | 기본 흐름. [목표와 범위 합의](../GUIDED-INTENT-FORMATION.md)와 [작업 제출 검증](FEAT-20261104-001-approved-work-review.md). |
| 2 · single-home-serial-work | 기본 흐름. [범위 내 반복 수정](../GENERAL-WORK.md#supervised-work-iteration)과 [범위·판본 변경 검사](FEAT-20261104-001-approved-work-review.md). |
| 3 · human-readable-view-and-entry | 기본 흐름. [판단할 Work 표시](PATCH-20261102-005-view-decision-summary.md). |
| 4 · work-continuation | 기본 흐름. [재개·중단 후 View](FEAT-20261102-001-resume-interruption-view.md)와 [후속 선택 계약](../GENERAL-WORK.md#continuation-1-successor-contract). |
| 5 · candidate-planning | 기본 흐름에서 후보 기록·비교. [후보 계획과 실행 승인 구분](../REFERENCE.md#candidate-planning). |
| 6 · single-work-local-delivery | 조건부 한 단계. [기기 수신함](FEAT-20261103-001-single-work-local-delivery.md), [격리 후보 클릭](FEAT-20261103-007-notification-work-detail.md). |
| 7 · same-home-direct-child-umbrella | 고급 참고. [직접 하위 작업의 판본과 상위 수락](../GENERAL-WORK.md#direct-child-umbrella). |
| 8 · same-repository-parallel-integration | 고급 참고. [격리 작업자의 제출·확인](../GENERAL-WORK.md#worker-review-observations). 실사용 팀의 병렬 효율은 미측정. |
| 9 · delegated-ordinary-acceptance | 고급 참고. [한정된 위임 수락 기록](FEAT-20261016-001-delegated-ordinary-acceptance.md). |
| 10 · project-local-product-lifecycle | 플랫폼별 운영. [macOS 설치·온보딩 변경](FEAT-20261101-003-macos-distribution-onboarding.md), [설치 및 실행의 구분](CHORE-20261103-003-qualification-alignment.md). |
| 11 · windows-native-runtime | 지정 ARM64 관측과 [x64 개발 빌드](FEAT-20261103-006-windows-x64-development-candidate.md)를 구분. [ARM64 기본 운영](FEAT-20261102-006-windows-basic-distribution.md). |
| 12 · official-document-execution | macOS 선택 프로필 한정. [고정 패키지별 실행 근거](CHORE-20261103-003-qualification-alignment.md)와 [공식 실행 계약](../REFERENCE.md#official-execution-candidate). |

상위 작업·병렬 통합·수락 위임은 첫 공개에서 기능을 삭제하는 안이 아니다. 조건과 한계를 참고 문서로 제공하고, 초기 지원 약속에서는 제외하는 제안이다. 설치·알림·공식 실행의 최종 공개 지원 결정은 각 환경의 후보 확인 뒤 Owner가 내린다.

계획과 초안에 대해 Claude 정적 리뷰를 각각 받았다. 결과 리뷰 후 양쪽 README의 공개 다운로드 상태, 고급 기능과 수락 위임의 범위, 기기 알림의 실행 조건을 맞추고 프로젝트 지침과 Core가 검사하는 조건을 구분했다. 보정 후 macOS 두 프로필과 Windows ARM64·x64 패키지를 오프라인으로 생성했다. 네 패키지 각각에서 한영 12개 안내, 원본과 같은 안내 파일 8개, 사용자 경로 링크·절 52개와 라이선스가 확인됐다. Mermaid 9개를 렌더링하고 한영 SVG도 화면으로 확인했다. 최종 문구의 독립 재리뷰와 네이티브 설치·에이전트 행동 시험은 이 문서 점검 범위 밖에 남아 있다.

## 저장소와 설치본에서 안내 열기 · 11월 4일

Owner 검토 대기. 저장소의 [영문 README](../../.github/README.md)와 [한국어 README](../../README.ko.md)는 서로를 열며 보고서 타임라인과 코드 작업 두 예를 소개한다. 저장소 첫 화면에는 GitHub가 우선 선택하는 영문 파일을 사용한다. 루트 README는 설치 후보에 그대로 포함되는 한영 안내로, 같은 트리를 직접 읽거나 소스에서 설치본을 만드는 경로에서도 상대 링크가 유효하다. 전체 영문 소개는 한 곳에서 관리하며 관리 파일 목록과 제품 실행 코드는 바꾸지 않았다.

[한국어 사용 설명서](../../manual/ko/README.md)와 [영문 사용 설명서](../../manual/en/README.md)의 순서는 예약 안내 실습, 두 초안 검토, 새 대화에서 재개, 수신함, 갱신·복구다. 기술 절차와 과거 실습 근거는 별도 참고 페이지에서 찾는다. 계획·결과 독립 리뷰 후 갱신·기여 링크, 직접 알림을 켜는 방법, 기기 실행 조건과 수락·수정 선택을 맞췄다.

최종 오프라인 검사에서 저장소의 입구·매뉴얼 23쪽과 상대 링크·이미지·문서 내 목적지 200곳, 배포물 네 종류에서 사용자 안내 경로 각 54곳을 확인했다. macOS 두 구성과 Windows ARM64·x64 패키지의 해당 안내 파일 8개는 소스와 일치했다. 한영 README의 기록 구조도는 로컬에서 각각 렌더링했다. 공개된 GitHub 화면이나 실제 기기에 설치해 클릭한 결과, 보정 후 독립 재리뷰와 구분한다.

## 고객 문의 보고서로 첫 작업 이어가기 · 11월 4일

앞 절의 예약 예제는 추가 실습으로 보존했다. 현재 저장소 첫 화면과 설치본의 시작 가이드는 고객 문의 12건을 바탕으로 초안을 검토하고, 새 대화에서 범위가 바뀐 보고서를 이어 쓰는 과정을 따른다. 연결 해제와 기기 도구 제거는 서로 다른 결정으로 안내한다.

독립 문서 리뷰 뒤 완전 삭제 순서, 재연결 제한, 로컬 기록과 에이전트 대화의 구분, 결과 수락과 알림 안내를 보정했다. 한영 기여 안내까지 포함한 저장소 문서 25개에서 링크·앵커·그림 231곳, 격리 생성한 macOS 두 구성과 Windows ARM64·x64 패키지에서 첫 사용 경로 각 54곳을 확인했다. Mermaid 6개와 두 언어 SVG의 밝은·어두운 화면도 렌더링했다. 이는 문서와 패키지 내용 검사이며, 공개 후보의 플랫폼별 설치·알림 클릭 자격은 별도로 판단한다. 사용자 검토 대기.

## 한영 README와 매뉴얼 탐색 · C안 검토본

README는 보고서 타임라인과 사용자·에이전트·Colvia·프로젝트의 기본 관계를 보여 준다. 준비된 결과의 제출은 그림 아래에서 따로 설명한다. 저장소 매뉴얼의 언어 전환은 입구에 두며 설치본의 한영 색인은 같은 파일 안에서 해당 언어의 안내로 연결한다. [작성 기준](user-documentation.md)과 [프로젝트 설치·운영 안내](../../manual/ko/project-setup.md)를 사용한다.

독립 결과 리뷰에서 제시한 여섯 항목을 보정했다. 최종 원고의 저장소 문서 28개에서 링크·앵커·그림 218곳, macOS 두 구성과 Windows ARM64·x64 격리 패키지에서 첫 사용 경로 각각 68곳을 확인했다. 한영 관계도와 구조도 총 6개, 두 언어 타임라인의 밝은·어두운 표시도 확인했다. 무시되는 디렉터리 안의 링크가 작업 스냅샷 검사에서 거부되는 기존 합성 검사 1건을 실행했다. 설치·연결 단계의 거부로 일반화하지 않는다. 보정 뒤 별도 독립 재리뷰는 없었으며 Owner 검토 대기다.

공개 후보에서는 운영체제와 대화 에이전트별 실제 클릭 및 새 대화에서의 재개를 확인한다. 지원 표와 기능 목록의 자동 대조를 CI에 연결하는 일은 공개 전 과제로 남긴다. 비교 시안은 Owner의 원고 비교가 끝날 때까지 추적하지 않는다.

## 비공개 후보 고정 전 대조 · 11월 4일

에이전트 진입과 설치본 안내에 대한 집중 검증을 마쳤다. Claude Code는 공통 진입 문서를 따른다. 두 도구 모두 설치된 프로젝트의 실행기로 현재 어댑터를 찾도록 안내한다. 어댑터 메타데이터 안에 있던 Windows 안내를 본문 첫 명령 앞으로 옮겼다. 한영 기능 안내는 준비된 결과를 제출하는 동작과 선택형 문서 실행을 구분한다. 정상 완료와 읽기 후 취소의 직접 실행 근거는 고정 macOS 패키지에 한하며, 수신함으로 맡긴 공식 문서 실행은 미검증이다.

비공개 기록을 뺀 작업용 소스 사본에서 보존한 공급 파일로 macOS 두 구성과 Windows ARM64·x64 시험 배포물을 만들었다. 선별 사본 45개 문서의 로컬 참조 472곳과 네 배포물의 로컬 참조 289·291·289·289곳에서 누락을 찾지 못했다. 선택형 구성에만 포함된 실행 안내에서 수신함과 입력 검사를 가리키는 두 링크가 차이를 만든다. 선별 소스의 문서·시험 도우미 집중 검사 43건, 격리 프로젝트의 갱신·롤백·해제 후 진입 검사 1건이 통과했다. 실제 대화나 Windows 기기를 실행한 결과와는 구분한다.

2026-11-04 Owner가 위 정합성 보정과 비공개 후보 준비 결과를 수락해 이 점검을 완료했다. 공개용 기여 안내와 파일 선별안은 초안이다. 공개할 소스 정본과 버전, 신고 창구와 배포·서명 방식, 최종 파일의 공개 적합성과 제3자 고지를 확정해야 한다. 깨끗한 macOS·Windows ARM64에서 Codex와 Claude Code로 첫 Work·검토 대기·알림 클릭·새 대화 재개를 확인하고, x64는 최종본을 한 번에 확인한다. 외부에서 실제로 내려받고 확인한 환경별로 지원 여부를 결정한다.

## Candidate freeze prerequisite — accumulated history (2026-11-06)

Owner requires accumulated-history assessment before freezing the public candidate. This is separate from desktop usability: the Owner may test a fixed usability candidate while capacity assessment remains open. No record-format change or automatic pruning is authorized.

Reuse the earlier Work-count/revision/intent-count diagnostics and the accepted [large-file checks and isolated prototype](PATCH-20261104-005-large-ordinary-work.md). The 3,000-file submission checks and 12,000-file early refusal do not establish long-running history performance. Raw record bytes, allocated storage and Git object storage are different measurements.

Proposed focused assessment: keep file count fixed while increasing completed Work history (30, 100, then 300 only if the earlier stages remain bounded); separately keep history fixed while increasing project files (100, 1,000, 3,000). Use a few selected cells rather than the full cross product. Include one deeper revision chain, candidate usage near its warning/refusal thresholds and one small edit after history has accumulated. Generate valid history through supported writers, never by fabricating authoritative JSON. Measure generation cost, record count/bytes, largest record, total/individual View latency, peak process memory and output size. Run one initial observation and three warm observations per selected query; do not call the first observation a cold-cache test. Git storage comparison, if performed, uses only a separately authorized synthetic repository; no real project commits.

Proposed budget, not execution approval: 2–3 hours expected including fixture preparation, measurements and reporting; cumulative cap 4 hours, no model calls, VM or installation. Use at most 2 GiB of new synthetic data, 120 seconds per query and 30 minutes per generation stage; stop a cell on limit, error or inconsistent state and retain it as incomplete. Do not retry to obtain a pass or silently lower coverage. The estimate is judgment informed by earlier small-history measurements, not measured duration for 300 Works.

Decision criteria: records and source files remain unchanged by reads; newest and historical decisions resolve correctly; crossing a record/candidate limit refuses without losing prior state. Report latency and growth by scale, with a provisional usability target of median ≤5 seconds and every measured query ≤10 seconds in the named local environment. These are assessment thresholds, not advertised platform guarantees. If ordinary target usage exceeds the agreed threshold or cannot save a small edit, hold candidate freeze and propose the smallest storage/reader change. A passing bounded test does not qualify unlimited history. Preserve old evidence and separately report unresolved larger-scale, OS and long-term conditions.
