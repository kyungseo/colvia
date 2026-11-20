# 일반 폴더를 Git 프로젝트로 전환

## First connection candidate · 2026-11-20

The first-connection increment covers an empty or populated unconnected folder. The person may keep it plain, or approve Git initialization and connection together. A missing account registration can be included in the same receipt. A local operation journal retains the selected project and the prepared, empty repository. Native Git observation and the ordinary connection path remain in use. The installed manuals and on-demand manager guide describe cancellation before apply, release of the reservation before connection files are prepared, and resumption by operation ID. After preparation, restart checks the approved repository identity and preserves new staging. Changes to existing connected projects, Work records, first commits and remotes belong to separate decisions.

## Owner 계획 결정 · 2026-11-16

등록판 `plain-to-git-project-conversion-r1`. 첫 Preview 이후 **P1로** 등록한다. 대상은 Colvia가 이미 연결된 일반 폴더를 Git으로 관리하고, 같은 프로젝트의 Work·승인·제출본과 보존 본문을 이어 가는 흐름이다. [기존 연결 범위 검토의 ‘연결 뒤 Git 유무가 바뀜’](record-foundation/connection-edge-scope.md#첫-공개와-후속-기능)에서 이어받는다. 이번 결정의 범위는 후보 등록이다.

## 기본 사용 흐름

같은 폴더의 대화에서 “이 폴더를 Git으로 관리하고 싶어요.”라고 요청하면, 에이전트가 기존 Colvia 연결을 확인하고 그 기록을 이어 가는 것을 기본으로 제안한다. “지금까지 Colvia에서 한 작업도 그대로 이어가 주세요.”라고 덧붙여도 같은 흐름이다.

1. 기존 Colvia 프로젝트와 폴더의 정체성, Git 실행 파일·등록 상태, 저장소의 존재와 최상위 경로를 읽어 확인한다. Git이 아직 초기화되지 않았으면 필요한 초기화, Git 등록과 기존 연결 전환의 대상·바뀌는 항목을 한 미리보기에 보여 준다. 개발자가 먼저 `git init`했다면 해당 저장소와 기존 연결을 확인하고 필요한 등록과 전환만 같은 미리보기에 표시한다.
2. 사용자가 확인한 계획을 승인하면 실행 직전에 다시 대조한다. 같은 프로젝트로 전환하고 Work·승인·제출본과 기존 파일을 보존한다. 진행 중인 Work의 관측·승인 전제가 바뀐 경우에는 영향을 보여 주고 필요한 결정을 받는다. 첫 커밋과 원격 저장소 연결은 사용자가 원할 때 별도로 진행한다.
3. 독립 프로젝트와 경로가 겹치거나 같은 폴더·저장소임을 확인할 수 없으면 기존 상태를 보존하고 확인할 항목을 안내한다. 기존 연결의 신원·중복 보호와 중단 후 상태 확인을 재사용할 수 있는지 설계 때 검토한다.

## 우선 검증

- **우선 흐름.** 연결된 일반 폴더에서 Git 초기화 전에 짧은 요청만 한다. 기존 프로젝트가 자동으로 확인되고 필요한 작업이 한 미리보기에 표시되는지 확인한다. 승인 전 파일 변경이 없고, 완료 후 같은 프로젝트에서 기존 Work·승인·제출본을 열 수 있어야 한다.
- **이미 초기화한 폴더.** 개발자가 먼저 `git init`한 뒤 일부 파일을 스테이징한 같은 프로젝트에서 전환을 확인한다. 기존 파일·스테이징과 이미 설정한 Git 상태가 보존되고, 재초기화·첫 커밋·원격 연결이 자동으로 일어나지 않는지 대조한다.
- **거부 경계.** 폴더가 다르거나 다른 연결과 겹치고, 미리보기 뒤 Git 상태가 바뀌거나 전환이 중단된 경우에 기록과 파일이 보존되는지 확인한다. 합성 검사와 플랫폼별 확인 범위는 첫 Preview 이후 후보 선택 시 정한다.

## 후보 목록 반영

기준 소스 `a9d5a47d3ee8583bccf93a57f892c4c5103417d9`. 후보 목록의 변경 직전 SHA-256은 `139e0c4e2cad407b34d18d81593eeedcb92460e0afd935486958f16e52c731ed`, 등록 직후는 `4917b4a5b1e7de3c496583d48209bb1d4d82c0c0a8d2c1a07e983d15df635740`다. `New Source Candidates`에 아래 한 행을 추가했다. 기존 연결 범위 문서는 날짜를 붙인 연결만 추가했다.

> - [일반 폴더를 Git 프로젝트로 전환](plain-to-git-project-conversion-followup.md#owner-계획-결정--2026-11-16) — 첫 Preview 이후 P1. 연결된 일반 폴더를 같은 Colvia 프로젝트로 유지하면서 Git을 사용한다.

## Existing connected folders

The manager can preview and adopt Git for a connected plain folder once every Work is completed or discarded and there are no pending effects. The same project and workspace retain their Work and decisions. A required transition record fences older clients before any project file effect. An unfinished Work after external initialization still needs a separate recovery design. See the [Git guide](../../manual/en/git.md#adopt-git) and the focused transition tests.
