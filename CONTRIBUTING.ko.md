# Colvia에 기여하기

[한국어 README](README.ko.md) · [English contributing guide](CONTRIBUTING.md)

<a id="버그를-발견했다면" name="버그를-발견했다면"></a>

## 질문하거나 버그를 신고하려면

질문과 버그 신고는 [Colvia Issues](https://github.com/kyungseo/colvia/issues)에 남겨 주세요. 어떤 환경에서 무슨 일이 있었는지 알려 주세요. 운영체제, 사용한 버전이나 배포 파일 이름, 기대한 결과와 실제 결과를 적으면 됩니다. 빈 프로젝트에서 같은 문제를 재현하는 방법이 있다면 함께 적어 주세요. 계정 정보나 개인 경로, 실제 프로젝트 파일은 제외해 주세요.

## 변경을 제안하려면

오타나 이해하기 어려운 예제를 고쳤다면 `main`을 대상으로 풀 리퀘스트(PR)를 열어 주세요. 버그 수정도 같은 방식으로 제안할 수 있습니다. 무엇을 바꿨고 어떻게 확인했는지 짧게 적어 주세요. 큰 기능을 추가하거나 에이전트의 권한이나 작업 기록 형식을 바꾸고 싶다면 구현 전에 유지보수자와 먼저 상의해 주세요.

## 보안 문제를 발견했다면

[비공개 취약점 제보 안내](SECURITY.md)에 따라 제보해 주세요.

## 기여물의 라이선스

Colvia가 작성한 코드와 문서에는 [Apache License 2.0](LICENSE)이 적용됩니다. 프로젝트에 포함할 목적으로 제출한 기여물에는 별도로 명시하지 않는 한 라이선스 제5조가 적용됩니다. 제3자 구성요소는 각자의 라이선스를 따릅니다.

## 첫 변경과 검사

사용 흐름은 [Colvia Preview 안내](manual/ko/README.md)에서 확인하세요.

일반 Work를 바꿨다면 저장소 루트에서 [대표 검사 한 건](CONTRIBUTING.md#make-your-first-change)을 실행하세요. 이 개발 검사는 GIL을 사용하는 CPython 3.14.7과 POSIX 셸에서 실행하세요. 범위 승인, 검토용 제출, 특정 결과 수락을 확인합니다. 설치본의 Python은 Colvia가 별도로 준비합니다.

문서 변경은 링크와 안내의 적용 대상을 확인하세요. 저장소·패키징·플랫폼 변경은 [유지보수 안내](docs/MAINTAINING.md#evidence-reuse-and-selection)와 [검증 근거](docs/development/product-evidence-and-followups.md#record-foundation-verification)에서 관련 검사를 고르세요. PR에는 사용한 명령, 환경, 결과를 적어 주세요.

## 저장소 운영 원칙 초안

변경은 작업별 브랜치에서 준비하고 `main`으로 PR을 엽니다. 각 커밋에 별도로 검토한 결과가 담겨 있다면 병합할 때 그 이력을 보존합니다. 공유 브랜치의 삭제와 강제 푸시를 막고, 실제로 운영하는 검사를 병합 조건으로 두는 방향을 제안합니다. 배포한 태그는 유지하고 수정판에는 새 버전을 부여합니다. 변경을 병합할지와 새 버전을 배포할지는 따로 결정합니다.

Colvia 자체를 개발한다면 [개발 절차(영문)](docs/development/WORKFLOW.md)와 [개발 문서 목록](docs/development/README.md)에서 시작하세요. 기존 결정과 개발 규칙의 적용 시점은 [영문 기여 안내의 개발 절차](CONTRIBUTING.md#source-development-workflow)에서 확인할 수 있습니다.

[사용자 문서 작성 기준 · 영문](docs/development/user-documentation.md)

소스 체크아웃에서 설치 흐름을 검사할 때는 [설치용 소스 준비](CONTRIBUTING.md#preparing-source-for-lifecycle-checks)를 먼저 확인하세요. 공개 README와 설치본 README는 각각 원본이 있습니다. Colvia Preview 배포본을 준비할 때는 안내의 링크와 Git 등록·폴더 이동 예를 실제 ZIP과 관리자 명령에 대조하세요.

### Colvia Preview 배포본 준비

[`foundation_bundle.assemble`](distribution/foundation_bundle.py)는 플랫폼별 실행환경, 검증 라이브러리, 네이티브 실행기, 배포 채널, 신뢰 루트와 고지를 고정한 입력으로 서명 전 압축 파일을 조립합니다. 같은 파일에 있는 `guide_sources`가 진입 페이지와 한·영 안내를 설치본 경로에 배치하며, Work 어댑터도 ZIP에 들어갑니다. 배포 전에 그 ZIP에서 링크가 열리는지, Git 등록과 폴더 이동 예가 동봉한 관리자에서 맞는지 확인하세요. 자세한 절차와 확인 범위는 [조립 절차](docs/development/record-foundation/runtime-and-extension.md#supply-candidate-and-vm-reuse)와 [검증 근거](docs/development/product-evidence-and-followups.md#record-foundation-verification)에 있습니다. 저장소를 복제한 상태에서 바로 동일한 ZIP을 재현하는 경로는 확인할 항목입니다.
