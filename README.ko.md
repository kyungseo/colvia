<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/brand/logo-hero-dark.svg">
    <img src="assets/brand/logo-hero-light.svg" width="320" alt="Colvia — AI Work Harness">
  </picture>

**AI가 일하고, 내가 결정하고, 프로젝트가 기억합니다.**

한국어 · [English](README.md)

[SQLite Preview 안내](manual/ko/foundation-preview.md) · [이전 프로필 설명서](manual/ko/README.md) · [기여와 첫 검사](CONTRIBUTING.ko.md#첫-변경과-검사) · [SQLite 후보 검증 근거](docs/development/product-evidence-and-followups.md#record-foundation-verification)

</div>


Colvia는 AI에게 맡긴 범위, 에이전트가 Colvia에 검토용으로 등록한 수정본, 내가 받아들인 결과를 프로젝트별로 기록하는 로컬 도구입니다. 어제 Codex와 하던 일을 오늘 Claude Code에서 이어갈 때, 기록과 지금 파일을 대조해 어디서부터 시작할지 정할 수 있습니다.

대화나 파일 내용을 에이전트에 전달할 때는 사용하는 서비스의 설정이 적용됩니다.

## 무엇을 해 주나요?

<table>
<tr>
<td width="33%" align="center" valign="top">
<picture><source media="(prefers-color-scheme: dark)" srcset="manual/assets/gallery/scope-dark.png"><img src="manual/assets/gallery/scope-light.png" width="100%" alt="사람이 범위를 정해 맡기고, 에이전트가 낸 결과를 검토합니다. Colvia가 그 합의와 결정을 기록합니다."></picture><br>
<strong>범위를 정하고 맡기기</strong><br>
고칠 파일과 확인할 기준을 에이전트와 합의합니다. 결과가 나오면 다시 고칠지, 받아들일지 내가 결정합니다.
</td>
<td width="33%" align="center" valign="top">
<picture><source media="(prefers-color-scheme: dark)" srcset="manual/assets/gallery/switch-dark.png"><img src="manual/assets/gallery/switch-light.png" width="100%" alt="다른 대화 도구에서도 같은 프로젝트의 Colvia 기록을 찾아 이어갑니다."></picture><br>
<strong>도구를 바꿔도 이어가기</strong><br>
같은 프로젝트에서 새 에이전트에게 “어디까지 검토했지?”라고 물어보세요. 에이전트가 Colvia 기록을 찾아 이전 결정과 남은 일을 알려 줍니다.
</td>
<td width="33%" align="center" valign="top">
<picture><source media="(prefers-color-scheme: dark)" srcset="manual/assets/gallery/drift-dark.png"><img src="manual/assets/gallery/drift-light.png" width="100%" alt="수락한 수정본과 현재 파일을 나란히 비교해 달라진 부분을 확인합니다."></picture><br>
<strong>달라진 파일 확인하기</strong><br>
“내가 검토한 뒤 무엇이 바뀌었어?” 에이전트에게 기록한 판본과 지금 파일을 비교해 달라고 하세요.
</td>
</tr>
</table>

### 사람, 에이전트, Colvia의 역할

사람이 작업 범위를 승인하면 에이전트가 수정과 검사를 수행하고, 사람이 검토할 수정본의 등록을 Colvia에 요청합니다. 사람은 그 수정본을 받아들일지, 에이전트에게 수정을 요청할지 결정합니다. Colvia는 합의한 범위, 등록된 수정본, 사람의 결정을 해당 프로젝트의 기록에 남깁니다. 검사 통과, 결과 수락, Git 커밋은 서로 다른 단계입니다. [구조와 역할](manual/ko/architecture.md)

## 설치와 첫 작업

SQLite Preview에는 작업 범위 승인부터 제출과 수락까지 Work 한 건의 기록이 남습니다. 예를 들어 에이전트에게 `문의.csv`의 문의 유형을 비교해 달라고 요청하세요. 보고서 파일과 검사 범위를 승인하고, 제출한 판본을 검토해 수락할지 정합니다. 이어 할 일을 남겨 두거나 이번 작업에서 마무리할 수 있습니다. 새 대화에서는 무엇을 수락했고 다음에 무엇을 하기로 했는지 물어보세요. [Preview의 Work와 후속 결정](manual/ko/foundation-preview.md#기록한-후속-작업-찾기)

[SQLite Preview 안내](manual/ko/foundation-preview.md)에서 설치, 프로젝트 연결, 첫 작업을 확인하세요. 운영체제별 공개 설치 명령은 Preview 배포와 함께 안내합니다. Windows x64 실기기와 Windows·macOS ARM64 시험 VM에서 비공개 HTTPS 설치를 확인했습니다. 어떤 후보를 어디까지 확인했는지는 [검증 근거](docs/development/product-evidence-and-followups.md#record-foundation-verification)에 정리했습니다.

### 이전 프로필의 설치 예

<p align="center">
<picture><source media="(prefers-color-scheme: dark)" srcset="manual/assets/gallery/overview-dark.png"><img src="manual/assets/gallery/overview-light.png" width="900" alt="이전 프로필의 연결, 후보 선택, 범위 승인과 결과 검토 흐름"></picture>
</p>

[이전 프로필의 설치·갱신 안내](manual/ko/project-setup.md)와 [고객 문의 12건 예제](manual/ko/getting-started.md)는 이전 `.hrn/` 배포본용입니다. SQLite Preview에는 위의 안내를 따르세요.

## 자리를 비울 때는 결과를 수신함으로

아래는 이전 `.hrn/` 프로필의 예입니다. SQLite Preview에서 알림을 쓰려면 [현재 설치본의 안내](manual/ko/foundation-preview.md#알림과-연결-해제)를 확인하세요.

<table>
<tr>
<td width="42%" align="center" valign="middle">
<picture><source media="(prefers-color-scheme: dark)" srcset="manual/assets/gallery/notify-dark.png"><img src="manual/assets/gallery/notify-light.png" width="360" alt="Colvia가 준비된 수정본을 프로젝트 수신함에 제출하고 사용자에게 기기 알림을 보냅니다. 사용자가 돌아와 결과를 검토합니다."></picture>
</td>
<td width="58%" valign="middle">
<blockquote><p>초안은 준비됐어. 검토용으로 제출하고 이 기기에서 알려줘.</p></blockquote>
<p>내가 맡길 단계와 기한을 확인하면, Colvia가 준비된 수정본을 내가 검토할 수 있도록 프로젝트 수신함에 제출합니다. 이 제출 단계에는 AI 모델을 쓰지 않습니다.</p>
<p>기기를 깨어 있게 두고 로그인 상태를 유지하세요. 돌아와서 에이전트에게 “검토할 게 있어?”라고 물으면 알림을 놓쳤거나 알림에서 결과가 열리지 않아도 수신함에서 찾을 수 있습니다.</p>
<p>결과를 받아들일지는 내가 결정합니다. <a href="manual/ko/resume.md#handoff">수신함과 알림</a></p>
</td>
</tr>
</table>

## 여러 파일을 고치는 코딩 작업에도

- **이전 검토에서 이어가기** · “내가 받아들인 결제 변경 이후에 달라진 파일과 내가 다시 볼 부분을 보여줘.”
- **남은 검사 찾기** · “같은 파일을 두 번 올려도 주문이 하나만 생기는 건 확인했지? 업로드가 끊겼다가 재개되는 경우도 검사했어?”

에이전트는 내가 검토할 수정본의 등록을 Colvia에 요청합니다. 합의한 범위를 벗어난 파일 변경이 포함되어 있으면 Colvia가 그 등록 요청을 거부할 수 있습니다. Colvia는 다른 프로그램의 파일 편집을 막지 않으며, 등록 요청을 거부해도 이미 편집된 파일을 되돌리지는 않습니다. 범위와 작업 폴더가 그대로라면 새 대화에서도 같은 Work와 기록된 승인을 이어서 사용할 수 있습니다. [SQLite Preview에서 작업하고 검토하기](manual/ko/foundation-preview.md#맡기고-검토하기)

## 고급 참고 기능 · 여러 작업과 작업 공간

다음 그림과 예는 이전 `.hrn/` 프로필의 고급 흐름을 보여 줍니다. SQLite Preview의 기능과 조건은 [현재 안내](manual/ko/foundation-preview.md)를 확인하세요.

<table>
<tr>
<td width="50%" align="center" valign="top">
<picture><source media="(prefers-color-scheme: dark)" srcset="manual/assets/gallery/split-dark.png"><img src="manual/assets/gallery/split-light.png" width="100%" alt="하위 작업의 결과를 각각 수락한 뒤 모은 결과를 따로 검토합니다."></picture><br>
<strong>관련 작업 묶어 검토하기</strong><br>
내가 각 작업의 결과를 수락했더라도, 여러 결과를 합친 통합 결과는 별도로 검토합니다.
</td>
<td width="50%" align="center" valign="top">
<picture><source media="(prefers-color-scheme: dark)" srcset="manual/assets/gallery/parallel-dark.png"><img src="manual/assets/gallery/parallel-light.png" width="100%" alt="분리한 작업 공간에서 수정본을 준비하고 기준 작업 공간에 하나씩 통합합니다."></picture><br>
<strong>작업 공간 나눠 준비하기</strong><br>
작업자들이 각자의 작업 공간에서 수정본을 준비하면 내가 결과를 따로 검토합니다. 기준 작업 공간에는 한 건씩 통합합니다.
</td>
</tr>
</table>

내가 지정한 대리인에게 특정 결과 한 건의 수락을 맡기는 방법도 있습니다. 이전 macOS 프로필에는 별도 준비와 승인이 필요한 문서 실행기도 있습니다. [이전 프로필의 기능별 조건](manual/ko/work-guide.md)

## 내 프로젝트와 기록

SQLite Preview는 작업 기록을 운영체제의 사용자 데이터 폴더에 프로젝트별로 보관합니다. 기록·본문·설정·수락 이력은 [Colvia에서 내보내고 복원](manual/ko/foundation-preview.md#본문과-백업)할 수 있습니다. Git commit이나 clone으로는 이 기록을 백업할 수 없습니다. [연결을 해제](manual/ko/foundation-preview.md#알림과-연결-해제)해도 사용자 파일과 작업 기록은 남습니다. 연결한 폴더를 옮겼다면 [새 위치를 확인하는 방법](manual/ko/foundation-preview.md#프로젝트-폴더를-옮긴-뒤-이어가기)을 살펴보세요.

[이전 프로필 설명서](manual/ko/README.md) · [SQLite Preview의 사용 환경](manual/ko/foundation-preview.md#지원-목표와-확인-상태) · [한국어 기여 안내](CONTRIBUTING.ko.md) · [Apache License 2.0](LICENSE)
