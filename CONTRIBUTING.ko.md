# Colvia에 기여하기

[한국어 README](README.ko.md) · [English contributing guide](CONTRIBUTING.md)

## 버그를 발견했다면

어떤 환경에서 무슨 일이 있었는지 알려 주세요. 운영체제, 사용한 버전이나 배포 파일 이름, 기대한 결과와 실제 결과를 적으면 됩니다. 빈 프로젝트에서 같은 문제를 재현하는 방법이 있다면 함께 적어 주세요. 계정 정보나 개인 경로, 실제 프로젝트 파일은 제외해 주세요.

## 변경을 제안하려면

오타나 이해하기 어려운 예제를 고쳤다면 `main`을 대상으로 풀 리퀘스트(PR)를 열어 주세요. 버그 수정도 같은 방식으로 제안할 수 있습니다. 무엇을 바꿨고 어떻게 확인했는지 짧게 적어 주세요. 큰 기능을 추가하거나 에이전트의 권한이나 작업 기록 형식을 바꾸고 싶다면 구현 전에 유지보수자와 먼저 상의해 주세요.

## 보안 문제를 발견했다면

비공개 배포본의 보안 문제는 그 파일을 제공한 담당자에게 개별적으로 알려 주세요. 공개 이슈나 PR에는 재현 정보가 노출될 수 있습니다. 공개 배포를 시작하기 전에 이곳에 비공개 제보 창구를 안내하겠습니다.

## 기여물의 라이선스

Colvia가 작성한 코드와 문서에는 [Apache License 2.0](LICENSE)이 적용됩니다. 프로젝트에 포함할 목적으로 제출한 기여물에는 별도로 명시하지 않는 한 라이선스 제5조가 적용됩니다. 제3자 구성요소는 각자의 라이선스를 따릅니다.

## 첫 변경과 검사

SQLite 후보의 사용 흐름은 [Preview 안내](manual/ko/foundation-preview.md)에서, 이전 `.hrn/` 배포본은 [이전 프로필 설명서](manual/ko/README.md)에서 확인하세요.

일반 Work를 바꿨다면 저장소 루트에서 [대표 검사 한 건](CONTRIBUTING.md#make-your-first-change)을 실행하세요. 확인한 개발 환경을 재현하려면 GIL을 사용하는 CPython 3.14.7과 POSIX 셸을 사용하세요. `448b581`의 깨끗한 로컬 clone에서 macOS ARM64와 SQLite 3.54.0으로 통과했습니다. 범위 승인, 검토용 제출, 특정 결과 수락을 확인합니다. 설치본의 Python은 Colvia가 별도로 준비합니다.

문서 변경은 링크와 안내의 적용 대상을 확인하세요. 저장소·패키징·플랫폼 변경은 [유지보수 안내](docs/MAINTAINING.md#evidence-reuse-and-selection)와 [검증 근거](docs/development/product-evidence-and-followups.md#record-foundation-verification)에서 관련 검사를 고르세요. PR에는 사용한 명령, 환경, 결과를 적어 주세요.

## 저장소 운영 원칙 초안

변경은 작업별 브랜치에서 준비하고 `main`으로 PR을 엽니다. 각 커밋에 별도로 검토한 결과가 담겨 있다면 병합할 때 그 이력을 보존합니다. 공유 브랜치의 삭제와 강제 푸시를 막고, 실제로 운영하는 검사를 병합 조건으로 두는 방향을 제안합니다. 배포한 태그는 유지하고 수정판에는 새 버전을 부여합니다. 변경을 병합할지와 새 버전을 배포할지는 따로 결정합니다.

Colvia 자체를 개발한다면 [개발 절차(영문)](docs/development/WORKFLOW.md)와 [개발 문서 목록](docs/development/README.md)에서 시작하세요. 기존 결정과 개발 규칙의 적용 시점은 [영문 기여 안내의 개발 절차](CONTRIBUTING.md#source-development-workflow)에서 확인할 수 있습니다.

[사용자 문서 작성 기준 · 영문](docs/development/user-documentation.md)

소스 체크아웃에서 설치 흐름을 검사할 때는 [설치용 소스 준비](CONTRIBUTING.md#preparing-source-for-lifecycle-checks)를 먼저 확인하세요. 공개 README와 설치본에 들어가는 README는 서로 다른 원본으로 관리합니다.

### 새 기록 구조의 후보 준비

앞의 `scripts/prepare-source.py`는 기존 프로필용 소스 트리를 준비합니다. 새 기록 구조의 배포 후보는 `distribution/foundation_bundle.py`에 정규화한 실행환경, 검증 라이브러리, 네이티브 실행기와 신뢰 입력을 명시해 준비합니다. `guide_sources(source)`는 후보 전용 진입 페이지와 한영 안내를 설치본 경로에 연결하며, 예전 기술 색인을 복사하지 않습니다. 현재 Git 등록 예는 고정한 시험본의 관리자와 대조했습니다. 새 배포본을 배포하기 전에는 그 배포본에 들어간 관리자와 예제를 다시 대조하세요. 보정 전 `448b581`에는 시험본의 Git·설치기 수정이 없습니다. 생성 결과는 서명하지 않은 준비용 압축 파일입니다. 설치나 플랫폼 검증을 완료한 것은 아닙니다. 근거와 다음 작업은 [현재 작업 기록](docs/development/FEAT-20261106-002-record-foundation.md)을 확인하세요.
