# Getting Started

Colvia connects an agreed task, its result and the next decision. In an installed project, start with `./colvia view`; agents use `./colvia view --details` and the verified manual/adapter it names. Follow the project's own rules. For scope and qualification, see [continuation-1](README.md#continuation-1).

## Hand off one Work item

Ask your agent to submit the prepared changes for your Work for review and notify you on this device. Check the Work title, action, scope, deadline and local inbox in the preview. If they match, say “Start as shown.” Later, ask whether that Work has a question or result.

> “‘설치 안내 정리’ 작업에서 준비한 변경을 검토용으로 제출하고, 결과가 나오면 이 기기에서 알려줘.”
>
> “‘설치 안내 정리’에 질문이나 결과가 있어?”

한 프로젝트에서 진행 중인 작업 하나의 한 단계를 맡길 수 있습니다. macOS와 지정 Windows 11 ARM64 격리 환경에서 확인한 단계는 작업 현황 요약과 준비된 변경의 검토용 제출입니다. 미리보기에서 작업 제목, 맡길 단계와 범위, 기한(최대 24시간), 결과를 받을 로컬 수신함을 확인하세요. 맞으면 “그대로 맡겨”라고 답하세요.

알림을 켜면 실행 담당자가 질문이나 단계 결과를 수신함에 기록한 뒤 운영체제에 짧은 알림 표시를 요청합니다. 배너를 놓치거나 보지 못해도 질문과 결과는 수신함에서 읽을 수 있습니다. 실행 전 확인을 선택했다면 질문에 “계속해” 또는 “중단해”라고 답하세요. 기한이 지났거나 중단 후 반영 여부가 불분명하면 수신함에서 기존 작업 기록 대조를 요청하세요. 제출된 변경을 수락할지는 결과를 읽은 뒤 결정합니다.

In isolated tests on macOS and a designated Windows 11 ARM64 VM under a standard account, a one-shot worker could continue after the submitting process exited. Tests covered Work summaries, prepared-result submission, answering a question and interruption handling. Device notification calls returned successfully. Actual banner display, user reads and adopter use remain unverified. See [commands and verification limits](REFERENCE.md#single-work-handoff-and-inbox).

## macOS Managed Distribution Candidate

The macOS arm64 candidate prepares Colvia and its pinned CPython 3.14.10 in a dedicated location. The path is **prepare Colvia → connect a project → agree on a task → review its result**. A repository clone, Homebrew and shell edits are unnecessary for this path. PR #46 was privately installed on one arm64 Mac. The default project's status and View were checked. Its own official model execution remains unverified. Public distribution and Windows release qualification remain pending.

When preparing installation, follow the [bootstrap and project connection procedure](OPERATIONS.md#onboarding-macos-managed-distribution-candidate): verify the named bootstrap and its external SHA-256, preview storage and preservation, then apply the exact reviewed request with your installation decision. Installation and first-task approval are separate.

### 한국어: 설치 후 첫 작업과 재개

macOS arm64 배포 후보는 Colvia와 필요한 Python을 전용 위치에 함께 준비합니다. 저장소를 clone할 필요는 없습니다. PR #46은 arm64 Mac 한 대에서 비공개 배포 경로로 설치해 기본 프로젝트 상태와 View를 확인했습니다. PR #46 자체의 공식 실행은 미검증입니다. PR #42의 한 고정 패키지에서 확인한 정상 완료와 읽기 후 외부 취소는 [공식 실행 안내](OFFICIAL-EXECUTION.md)에 정리했습니다. 설치할 때는 [설치·연결 상세](OPERATIONS.md#onboarding-macos-managed-distribution-candidate)에 따라 배포본을 확인하고 적용 범위부터 검토합니다.

연결 후 `./colvia view`에서 현재 작업을 확인하세요. 첫 요청에는 원하는 결과와 바꿔도 되는 범위를 알려주면 됩니다. 예: “이 README의 설치 안내를 보강해줘. 나머지는 보존하고, 수정 범위와 검사 방법부터 보여줘.” 에이전트가 계획과 작업 요청을 준비하고, 유효한 승인 범위에서 진행합니다. 결과를 보고 수락할지는 사용자가 결정합니다.

새 대화에서는 “현재 Work와 계획을 읽고, 수락한 내용·남은 일·다음 추천을 정리해줘”라고 요청하세요. 에이전트가 기록과 현재 파일을 대조하고 기존 승인, 소비 시간과 시도 횟수를 이어받습니다. 진행 중인 작업은 같은 Work에서 확인합니다.

### Update, Recovery And Removal

Project update, rollback, repair and removal use preview and exact-request apply. Detach retains project Work and intent records; tool removal retains recovery material and shared Python. Shared-runtime removal and automatic store repair are unavailable. Before an operation, read [update and recovery details](OPERATIONS.md#onboarding-update-recovery-and-removal). Preserve partial state and original requests when interrupted.

갱신·복구·연결 해제는 먼저 범위를 확인하고 승인한 요청을 적용합니다. 연결 해제 뒤에도 작업 기록은 남습니다. 공유 Python 제거와 저장소 구성요소의 자동 복구는 아직 지원하지 않습니다. 해당 작업을 할 때 [상세 절차](OPERATIONS.md#onboarding-update-recovery-and-removal)를 확인하고, 중단된 요청과 파일은 보존하세요.

### Technical Details

The managed runtime requires the exact normalized tree and manifests, including modes and isolated entry. An exact relocated copy may be admitted; this checks tree identity, not publisher or interpreter authentication. Legacy CPython 3.14.6/3.14.7 admission and Windows policy remain separate. [Runtime, Git and distribution conditions](OPERATIONS.md#onboarding-technical-details) apply when preparing installation or diagnosing it.

## Prepare Project Ignore Rules

During authorized adoption, preserve existing project ignore rules and intentional exceptions. Before init and the first baseline, follow the [project ignore defaults](OPERATIONS.md#onboarding-prepare-project-ignore-rules).

## Prepare Project Agent Entry

Keep the stable `./colvia view --details` command in project instructions, following its verified manual/adapter paths. Preserve existing project rules; use the [entry preparation procedure](OPERATIONS.md#onboarding-prepare-project-agent-entry) during setup.

## Initialize A Fresh Project

For trusted source setup, use a fresh project, final GIL-enabled CPython 3.14.6 or 3.14.7, explicit `--source-checkout` and the verified profile. Preview first and obtain installation authorization before exact apply. Follow the [source commands and admission conditions](OPERATIONS.md#onboarding-initialize-a-fresh-project). Managed installation uses the bootstrap procedure above.

## First Serial Work

1. State the intended result, editable scope and what must stay unchanged. The agent prepares the plan and typed intent.
2. Decide the exact intent; the agent records the applicable approval and publishes a Work baseline. A draft or confirmation token alone grants no authority.
3. The agent edits within scope, checks the result and submits the full manifest. Keep one editing Work during serial use.
4. Review the result and limits. Your acceptance selects the completed result; Git commit and publication are separate decisions. The agent explains one useful next step and its reason.

For example: “Improve this README's installation section, preserve the rest, and propose scope and checks first.” The agent prepares machine input through the [installed adapter](../adapters/colvia-work/SKILL.md); exact fields and acceptance steps are in [General Work](GENERAL-WORK.md) and [the detailed procedure](OPERATIONS.md#onboarding-first-serial-work).

## Review Without Editing JSON

Ask in your own language about progress, results or next steps. The agent prepares exact records and explains the decision needed, including stale or missing references. Use `./colvia view --details` when technical identities or commands are needed. [Review details](OPERATIONS.md#onboarding-review-without-editing-json) cover project documents and confirmation views.

## Continuation-1 Setup And Resume

In a fresh conversation, ask: “Read the current Work and its plan; explain what was accepted, what remains and the recommended next step.” Compare records with current files, carry forward valid approval and consumed limits, and preserve pending operations. Read `./colvia view continuation WORK_ID` for the selected follow-up, including completed Work. A proposal, an existing Work, explicit none and undecided are distinct choices; selection alone authorizes no execution. See [resume details](OPERATIONS.md#onboarding-continuation-1-setup-and-resume).

## Transition To Checkout-1

Historical only: use the exact retained qualified source and original request. See [the retained procedure](OPERATIONS.md#onboarding-transition-to-checkout-1).

## Transition To Entry-1

Historical only: the current continuation-1 candidate does not perform this transition. See [the retained procedure](OPERATIONS.md#onboarding-transition-to-entry-1).

## Delegation-1 Implementation Candidate

The optional exact ordinary-worker acceptance grant requires an explicit Owner decision. Intent and parent acceptance, Git and source-development acceptance remain separate. See [grant boundaries](GUIDED-INTENT-FORMATION.md#delegation-1-implementation-candidate) and [historical details](OPERATIONS.md#onboarding-delegation-1-implementation-candidate).

## Windows-2 Entry

Use only the exact qualified native Windows tuple and explicit windows-2 profile. Current native qualification remains separate. Before setup, read [Windows entry and recovery](OPERATIONS.md#windows-2-native-entry-and-recovery) and [entry details](OPERATIONS.md#onboarding-windows-2-entry).

## Optional Official Execution Candidate

The shared source declares continuation-1. The optional macOS official-execution-2 payload needs its own preparation and installation decision; existing continuation projects have no direct switch. Follow [the exact procedure](OPERATIONS.md#onboarding-optional-official-execution-candidate) only when that profile is requested.
