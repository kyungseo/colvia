<a id="실행환경-계약과-다음-claude-구조-리뷰-입력" name="실행환경-계약과-다음-claude-구조-리뷰-입력"></a>

# Runtime requirements and inputs to the next Claude architecture review

상태: 2026-11-06 Owner의 기존 범위 확인을 반영한 구현 요구사항. 구현·설치·실행 검증 완료를 뜻하지 않는다. R1 입력은 그대로 보존한다. 이 저장소 문서가 실행환경·지원 목표·확장 경계의 현행 작성 위치다. 다음 집중 리뷰 패킷은 이 문서를 입력으로 참조한다. 나머지 R1 보정 명세를 대신하는 전체 패킷은 아니다.

English reference, 2026-11-19. The [original wording at the translation base](https://github.com/kyungseo/colvia/blob/eed271ad5aa665f0002c9eded69d82f224da9ce0/docs/development/record-foundation/runtime-and-extension.md) governs the dated decisions and evidence. The Owner [accepted this English reference](../document-language-result-review.md#owner-acceptance). The [R2 input table](review-r2.md) identifies the earlier review snapshot by digest.

<a id="공개-전-갖춰야-할-사용자-경험" name="공개-전-갖춰야-할-사용자-경험"></a>

## First-release user experience

People must be able to install and use Colvia without installing a particular Python version or configuring pyenv and PATH. This is a condition of the first release. Wider Python support can follow. Document source runs separately for contributors. They cannot substitute for the ordinary installation path.

Apps and CLIs use the dedicated launcher bound to the same installation. All four host forms (Codex app and CLI, Claude Code desktop and CLI) use the same Python selection rules. The launcher resolves its dedicated Python and product payload from the verified installation binding. Never silently fall back to python/python3 on PATH, a pyenv shim, shell activation or another project's virtual environment. A GUI, login shell and non-login shell must select the same product, Python and SQLite combination for a given binding. An update preserves the pinned combination of each running process. Compatible new processes use the newly verified binding.

<a id="첫-공개-설치-진입과-완료-기준" name="첫-공개-설치-진입과-완료-기준"></a>

## First-release installation entry and completion criteria

Owner 확정 요구: 플랫폼별로 문서에 안내된 명령 하나로 설치 또는 업데이트를 시작한다. OS별 shell 문법은 달라도 된다. 같은 진입이 현재 설치 상태와 호환 가능한 공개 버전을 확인해 신규 준비 또는 갱신으로 연결한다. 정확한 명령 이름과 공개 URL은 배포 설계에서 정하며, 아직 존재하지 않는 주소를 사용 가능하다고 안내하지 않는다.

The installer determines OS, architecture, channel and version compatibility. It downloads and verifies the assets, prepares the dedicated Python and activates the product/runtime binding. Show the selected version and changes in plain language. The ordinary user should not have to select or compare Python ZIPs, individual hashes, internal profiles or interpreter paths. Version pinning and offline supply are optional expert paths.

Define how the official bootstrap is trusted and how manifests and assets are verified. Refuse mismatches, failed downloads and unsupported combinations before applying anything. A hash obtained through the same compromised channel cannot authenticate the supply. Resolve outstanding supply and signing questions before qualifying the real delivery path.

One command starts the process. Explain user actions where they occur, including OS execution permission, notifications, agent installation and subscription sign-in. Distinguish Colvia readiness from agent installation or login. Do not collect credentials, initiate new charges, relax security settings automatically or delegate downloads and runtime selection back to the user.

Updates preserve records, settings, bodies, acceptance history and capability choices. After interruption, corruption or insufficient space, provide the previous verified combination or an explicit recovery path. Rollback must respect the current data format. Recovery must not require the user to assemble Python or internal files manually.

Qualify first install and update using the actual distribution address and documented command. Follow download, verification, runtime preparation and activation through the first Work in the app or CLI, result review, notification entry and resumption in a new chat. Exercise representative failure and recovery cases. Local assets, source runs and mock servers provide preliminary evidence only. They cannot qualify the actual distribution path. When real-URL testing requires publication, obtain separate approval and retain its unverified status until tested.

<a id="지원-목표와-판정-단위" name="지원-목표와-판정-단위"></a>

## Platform targets and units of verification

The first-release targets cover three platforms and both the CLI and desktop forms of two agents. Track the product target, upstream OS/architecture availability and observed Colvia results separately. The table below sets the required targets for this design. It makes no claim about upstream support or completed tests.

| 첫 공개 플랫폼 목표 | 필수 호스트 목표 | 지원 가능 여부 확인 | 새 최종 후보 검증 상태 |
| --- | --- | --- | --- |
| macOS Apple Silicon ARM64 | Codex CLI·앱, Claude Code CLI·데스크톱 | 호스트/버전별 확인 | 기존 후보 근거 재사용 가능, 새 배포 경로 최종 판정 전 |
| Windows 11 ARM64 | Codex CLI·앱, Claude Code CLI·데스크톱 | 호스트/버전별 확인 | 기존 후보 근거 재사용 가능, 새 배포 경로 최종 판정 전 |
| Windows 11 x64 | Codex CLI·앱, Claude Code CLI·데스크톱 | 호스트/버전별 확인 | 개발 후보·에뮬레이션 근거와 실제 x64 OS 설치/실행 판정 구분 |

Record the 12 platform/host combinations separately. For each, record host version, execution and permission mode, dedicated runtime, project location and observed feature. Classify upstream availability as available, constrained, unavailable upstream or unknown. Record each check as passed, failed, unrun or inapplicable, with a reason. A pass for one feature cannot establish support for the entire combination. If a host or capability is unavailable, present the evidence and options to the Owner. Retain the target and identify emulation separately. Record final acceptance separately for each platform after the Owner’s decision.

<a id="확장을-위해-지금-고정할-경계" name="확장을-위해-지금-고정할-경계"></a>

## Extension boundaries

These boundaries allow new agents and platforms to use the existing record format, acceptance semantics and history. Keep the contracts narrow. A general plugin registry, dynamic code loading, adapter generation and a future scheduler are outside this design.

| Component | Responsibility | Boundary |
| --- | --- | --- |
| Core/domain | Project, Work and result identities, approval and acceptance, references, bodies, state, concurrency and integrity | Acceptance has the same meaning across operating systems, models and products. |
| Platform implementation | Installation, runtime preparation, paths, file properties, locking, durability, permission diagnostics, OS notifications and click handling | Keep OS paths and API calls in the platform layer. |
| Agent adapter | Guidance, tool invocation, run start/status/cancellation, approvals, result and error delivery | CLI flags, app session formats and vendor output formats belong to the adapter. |
| Model/provider adapter | Model invocation and availability information required by the agent | A connected model alone establishes no capability to edit files, cancel or resume work. |
| Installation and composition | Select verified platform and agent implementations and a compatible runtime/capability combination | Select implementations outside Core. |

An agent operates on files and tools. A local model can supply inference to that agent. A local provider alone guarantees neither isolation nor cancellation, notification delivery or safe execution.

For each capability, record its name, version and verified limits. Distinguish receipt of guidance, project reads and writes, sandboxing, tool invocation, run observation, a cancellation request, confirmed termination, exact result identification and delivery, and resumption. Record product and version for adapter selection and diagnostics. Verify actual permissions and integration before granting access. Missing capabilities must not trigger a silent fallback to wider permissions.

Platforms implement OS locks. Storage and Core own the common authority's transaction, CAS and acceptance invariants. Successful execution does not accept a Work, and acknowledging cancellation does not confirm termination. The result schema must not require an agent-specific transcript or session ID as authority. An external run ID is optional provenance. The retained result and human decision must remain readable after an app chat disappears.

Register a new adapter as a capability implementation. Adding one does not require rewriting Work, bodies or acceptances or migrating a product name. At the same project authority and a valid workspace, another agent must be able to read the Work state, retained result and pending decision and continue. This makes no promise of private chat transfer or automatic synchronization across devices or clones. Stop and explain missing permissions or capabilities, uncertain earlier effects or a mismatched workspace.

If semantics must change later, follow the public compatibility and migration policy. Verify the dependency direction and neutral data contracts now so adding an OS or agent alone does not require a change of meaning.

<a id="후속-후보--현재-구현-제외" name="후속-후보--현재-구현-제외"></a>

## Follow-up candidates outside the implementation scope

| Candidate | Purpose | Condition for selection and a support claim |
| --- | --- | --- |
| EXT-PLATFORM-LINUX | Installation, paths, locking, permissions and notifications on Linux | Select the scope and target environments, then verify actual distribution and integration. |
| EXT-AGENT-LOCAL | Connect an agent that operates files and tools using a local model | Distinguish the agent from the model. Verify actual work, cancellation, results and resumption. |
| EXT-AGENT-ANTIGRAVITY | Connect Antigravity | Establish the capabilities and limits of the available version. Check Work resumption, state and permissions. |
| EXT-AGENT-PROJECT-TOOLS | Connect other AI tools that work on projects | Meet the guidance, tool and execution contracts and verify the integration. |

The development index links to this table. Keep the link when selecting a candidate. Listing a candidate neither authorizes work nor claims support or reserves a product feature ID. The current implementation covers the boundaries needed by the first-release hosts and platforms. Code and tests specific to future tools are deferred.

<a id="구현-계약" name="구현-계약"></a>

## Implementation requirements

1. Prepare the dedicated runtime for the OS and architecture without requiring a preinstalled user Python. Verify the manifest version, size, hashes and other supply requirements for online and offline assets. Detect other prerequisites such as Git separately.
2. Distinguish product version, Python version, SQLite library version, OS and architecture, and store/protocol/capability compatibility. The verified combination must work without a broader public Python support promise. Source-development prerequisites apply only to contributors.
3. Prepare and verify the new payload and runtime before activating the binding. Reuse a compatible runtime. On download, integrity, extraction, permission or interruption failure, preserve records and the previous usable combination. Never roll back automatically to a version unable to read the newer records.
4. Distinguish project identity, workspace identity and authority from runtime binding when connecting a folder or an app worktree. Ordinary folders, linked worktrees and registered app worktrees inside a project must resolve the correct authority and dedicated launcher. A copied path, another launcher on PATH or a same-name project cannot establish identity.
5. Check runtime and payload read/execute access, scoped project reads/writes, creation/replacement/recovery of authority journals and locks, and the write paths of selected delivery or notification capabilities separately. Shell access and successful source runs cannot establish app sandbox access.
6. Choose storage alongside the permission contract. R1 proposed storing under `.git`, which conflicts with default Codex sandbox protection. This design does not adopt `.git` as the default storage location. Moving the path or repeatedly escalating permissions is insufficient. Explain the exact scope, reason and revocation steps for any required setting change and respect existing approval. Do not default to disabling security controls or granting full-disk access.
7. Diagnose with the launcher and permissions that will actually be used. Read-only queries must not write files. Use only a bounded task-owned path for an explicit write probe and preserve real user records. If a diagnostic receives additional access, it cannot count as a pass in the default app mode.
8. Distinguish missing or corrupt runtimes, unsupported combinations, wrong workspaces and denied writes. Give the reason, necessary path and next action briefly. Example messages include “Colvia 실행환경이 준비되지 않았습니다. 설치 도구에서 복구를 실행해 주세요.” and “이 앱에서 작업 기록 폴더에 쓸 수 없습니다. 아래 폴더의 접근을 허용한 뒤 다시 실행해 주세요.” Keep tokens, internal instructions and long tracebacks out of routine guidance. Diagnose the cause before recommending reinstallation.

<a id="최종-검증-행렬" name="최종-검증-행렬"></a>

## Final verification matrix

Distinguish Codex CLI, the Codex app, Claude Code CLI and Claude Code desktop. Cover ordinary non-Git folders, ordinary Git checkouts, external linked worktrees and registered app worktrees nested in the project. Record which host created a worktree and which opened it. Each host need not create the worktree itself.

| Check | Verify | Evidence boundary |
| --- | --- | --- |
| First installation without personal Python settings | The installer prepares the runtime and runs the first command without pyenv, a user virtual environment or user Python. | A cleared process environment tests discovery rules only. It cannot substitute for installation by a fresh user. Record whether system Python was present and unused during a real fresh-user installation. |
| App and CLI launcher selection | Compare the binding, actual executable, Python, SQLite and product identity across the four host forms and four location types. | A process name or source version string cannot establish installed payload identity. |
| Minimum read/write paths | Query, register a synthetic Work, submit, accept, create and recover a journal, and check any selected delivery path. | Record app and CLI sandbox conditions separately. A pass with elevated permissions applies to those permissions only. |
| Another Python first on PATH | Select the dedicated launcher even with an unsupported Python or fake shim first on PATH. | Use a synthetic process environment and preserve personal settings. |
| Worktrees, moves and resumption | Query the correct authority and Work, reject mixed results across workspaces and keep valid bindings. | Identify registered nested worktrees structurally. A folder-name exclusion is insufficient. |
| Updates, interruption and recovery | Cover failed preparation, interruption immediately before/after activation, running processes and compatible/incompatible rollback. | Verify preservation of post-release records, settings, bodies and acceptance history. |
| Runtime and permission diagnostics | Report failure accurately with the reason and next action. | Distinguish product diagnostics from an explanation a model happened to give correctly. |

Use focused unit and integration checks for launcher selection, binding and failure states. Qualify actual package and app permission paths with the installed release candidate on the relevant OS and architecture. macOS or Windows ARM64 evidence alone does not establish x64 success.

For each case record reused evidence, a new pass, an observed refusal or an unrun check. Record the candidate version and hash, host and mode, workspace type, selected runtime and binding, read/write results and required human actions. Exclude credentials and personal account values. Equivalent large checks can reuse evidence. Verify launcher selection and permission differences by host and location.

## Host Approval Modes

Apply the [host approval-mode criteria](validation.md#codexclaude-권한-모드별-접근승인-경로) to actual hosts. Check that the selected approval flow can finish the task. Plan-mode write limits are expected. Host tool approvals are separate from Colvia scope approval and result acceptance. Reuse work, submission and resumption evidence where execution conditions match. Verify mode names and availability on the host version, and test differing paths without requiring full access. An unapplied setting and successful execution after a per-command approval are distinct observations.

## 기존 근거와 범위

[설치 후보와 호스트별 근거](../product-evidence-and-followups.md#record-foundation-verification)를 기준으로 재사용할 검사를 고른다. Windows x64의 Codex 앱 사용자 지정 프로필, Codex CLI의 MXC, Claude Code 앱·CLI의 Manual은 관측한 접근·승인 방식에 한해 근거가 있다. 호스트 엔진 버전과 앱 셸 버전을 각각 확인할 수 있을 때만 기록한다. 일반 CLI의 관측 버전을 제품이 관리하는 전용 실행기 버전으로 취급하지 않는다. Linux와 WSL은 첫 Preview의 네이티브 Windows 검사 범위에서 제외한다.

같은 볼륨에서 프로젝트를 옮긴 뒤의 연결은 소스에서 확인했다. 연결 이동을 기록하면 새 연결 기능을 이해하는 런타임이 필요하다. 이전 슬롯을 선택하거나 백업을 읽을 때에는 기능 호환성을 확인한다. Windows 최종 후보에서 NTFS 이동, 옛 프로젝트 실행기, 호환되지 않는 복구 슬롯·백업의 거부, Git 경로 표시·중단 복구, 네이티브 수신기, 현재 호스트 권한 중 바뀐 경계만 확인한다. 기존 후보의 갱신·Git 복구와 설치 결과는 해당 입력의 결과로 유지한다.

기존 source/PATH의 데스크톱 작성·재개·수락 결과는 에이전트 사용 흐름 근거로 재사용한다. 기존 managed 설치·갱신·알림 근거는 해당 후보와 관측한 경로에 한해 재사용한다. 새 authority 위치, runtime binding, SQLite와 권한 경계가 바뀐 부분은 새로운 설치본 검증으로 채운다. 기존 실패·측정 기록은 보존하며 성공으로 덮어쓰지 않는다.

새 Python 버전 지원 확대, 실제 개인 Python 설정 변경, 임의 OS 권한 확대는 이번 정렬에 포함하지 않는다. 실제 설치·앱/VM·모델 실행은 기존 보류와 승인 경계를 유지한다. 이번 문서화가 그러한 실행의 추가 승인이 되지는 않는다. 실행환경 구현 비용은 기존 연결·패키징·갱신 항목에 명시하고 중복 산정하지 않는다. 새 전용 과제로 확장하지 않는다.

## 다음 Claude 패킷에 넣을 검토 질문

- 플랫폼별 명령 하나에서 실제 배포 파일 검증·전용 runtime·호환 버전 선택까지 연결되는가? 수동 Python ZIP·해시·profile 조합이 일반 경로에 남아 있지 않은가?
- 세 플랫폼 × 두 에이전트 × CLI/데스크톱 목표와 실제 지원 가능성/검증 상태를 분리했는가? 실제 배포 신규 설치·업데이트/복구가 완료 기준에 있는가?
- OS adapter와 agent adapter가 Core 밖에 있으며, 능력·제약 차이가 수락 의미를 바꾸지 않는가? 로컬 모델과 파일/도구를 다루는 에이전트를 구별했는가?
- 미래 adapter가 기존 기록과 같은 Work를 읽고 이어갈 수 있는가? 그 목적을 넘어 미래 기능이나 과도한 범용 계층을 미리 만들고 있지 않은가?

- 개인 Python이 전혀 없어도 최초 준비가 가능한가? bootstrap 자체가 그 Python을 요구하는 순환 의존은 없는가?
- 앱과 CLI가 동일한 검증된 binding을 사용하며 PATH·pyenv·shell 차이에 기대지 않는가?
- runtime은 실행되지만 authority/journal 또는 전달 경로에서 쓰기가 막히는 경우를 놓치지 않았는가? 일반/linked/nested workspace에서 최소 권한으로 가능한가?
- 업데이트·중단·복구 중 runtime과 payload가 다른 세대로 섞이거나, 첫 공개 이후 기록을 읽지 못하는 rollback이 가능한가?
- source 성공, 정리된 env 성공, 실제 설치본 성공이 각각 구분되는가? 짧은 실패 안내가 실제로 필요한 조작을 알려 주는가?

위 질문은 R1 F1/F4/F7의 보정 검토에 함께 넣는다. 새 독립 실행환경 리뷰를 추가로 만드는 요청이 아니다. 기존 실행환경 방향이 구현 명세·리뷰·최종 수락 기준에서 빠지지 않게 하는 Owner의 확인이다.


## R2 설계 보정과 미결 정책

[R2 처분](review-r2-disposition.md)의 M1·M2·M8의 기록 위치·권한·백업·공급 신뢰 정책은 2026-11-06 Owner가 설계 기준으로 채택했다. 실제 설정 변경·설치·key 생성 권한은 아니다. 플랫폼별 사용자 데이터의 프로젝트별 기록 폴더를 권장하고, 호스트의 좁은 추가 쓰기 허용 가능 여부를 실제 조합별로 확인한다. 전체 authorities나 home 접근을 기본값으로 확대하지 않는다.

실행기 진입은 작업 폴더에 복사된 branch 파일에 의존하지 않는 사용자별 managed entry로 설계한다. 사용자 상대 경로의 해석도 앱별로 확인한다. Git executable/version과 필요한 config provenance를 관측 context에서 한 번 고정하며, 12개 조합 원장에 그 결과를 남긴다. 개인 Python과 Git의 존재를 혼동하지 않는다. Git 부재·CLT 준비·권한 차이는 각각 안내한다.

첫 공개부터 갱신 서명 key·서명된 channel/release metadata, freshness/expiry·관측한 순서·명시적 rollback·key 교체/회수/복구를 설계하는 안을 권장한다. 첫 취득의 HTTPS 신뢰와 OS 코드 서명/실행 허용은 별개다. 서명된 오래된 metadata도 재전송될 수 있으므로 서명 성공만으로 최신성을 판단하지 않는다. 실제 key 생성이나 유료 서명 선택은 여기서 수행하지 않는다.

runtime slot은 현재·실행 중·필요한 마지막 복구본을 보존한다. 고정된 두 개만 남기려고 실행 중인 구 slot을 삭제하지 않는다. 호환 읽기/쓰기와 필요한 capability를 별도로 판정하고, 알 수 없는 수락 의존 객체를 생략한 채 정상으로 읽지 않는다. 모델/provider는 현재 소비자가 요구하는 경계만 구현하며 미래용 범용 interface를 선행 구현하지 않는다.


## Windows/WSL qualification boundary

Qualify native Windows processes for the Windows target. WSL/Linux CLI belongs to the Linux follow-up. Writing to a shared Windows authority through a Linux mount is unverified. Block writes through that path and explain why. Qualify Windows executables invoked through WSL interop separately before counting them as native-host coverage. This restriction makes no general claim about locking on WSL filesystems.

For host access settings, first evaluate a user-level setting scoped to the project authority. Check actual support and inheritance by app worktrees in P2. Do not assume access to the entire project or user-data directory or that settings follow a branch copy. No setting change was performed in this design step. Use [C7/C8](implementation-contracts.md) for trust at first bootstrap and update.


## Supply, Candidate And VM Reuse

Before preparing a candidate, check the accepted scope of the [owning Work](../FEAT-20261106-002-record-foundation.md) and prior supply, assembly and installation evidence. Preserve original inputs and failures. Select checks according to what changed.

| Change or question | What to reuse and what to check |
| --- | --- |
| Product code or installation guidance | Reuse the pinned dedicated Python and verifier dependencies. Use the [candidate builder](../../../distribution/foundation_bundle.py) and compare the inventory and affected behavior. |
| Runtime or dependencies | Check the pinned inputs, tool versions and remote run records for the verified supply process. Regenerate and verify only affected components. Remote execution and cost require their own authorization. |
| Installation, update, recovery or host behavior | Check existing VM registration, disk, account and installation baseline first. A fresh build environment inside the VM is unnecessary. |
| An environment without personal configuration | Use a separate account or clone when needed. Build tools used to produce the supply are contributor dependencies. |

In the resumption record, include input digests, tool versions, execution order, artifact locations, verification methods, conditions for reuse, known failures and stop conditions. Set transfer timeouts using actual size and measured throughput. Compare the received bytes as well as checking the exit status. A partial transfer or a pass under different conditions cannot establish installation success.

Keep public procedures and product contracts in the repository. Keep personal paths, accounts, private execution details and original failure logs in the internal record under the [document placement rules](../document-ownership.md). Link the exact internal route from the task's existing plan and result. This procedure and prior passes grant no new execution, cost, installation or publication authority.

### Windows runtime creation checkpoint

The native runtime-directory creation correction uses the existing platform lifecycle adapter and retains the private ACL checks. The prepared candidate reuses its qualified runtime, verifier and native entry. Native directory ACLs passed; installation then stopped before runtime activation at root-metadata reauthentication because the Windows cache uses a verified two-path hardlink while that reader still requires a single link. Keep this separate from the earlier directory-creation failure. Reuse the supplied runtime and existing known-pair validation evidence when planning that correction; do not rebuild dependencies, weaken generic hardlink checks, reset trust or report installation/recovery qualification. The owning record links the private execution evidence.


### Root reauthentication and redirected-output checkpoint

The subsequent correction reuses the exact current-root pair reader while retaining strict single-link reads for historical roots and ordinary files. The Windows ARM64 fixture now passes installation, private runtime ACL checks, native status and Korean connection preview. Installed Python entry wrappers set UTF-8 output and preserve each stream's existing error handler; runtime, verifier and native executable inputs are reused.

The remaining connection attempt was refused before operation creation because the test harness wrote canonical JSON through Windows text mode. Preserve that failure, emit machine inputs as exact UTF-8/LF bytes, and validate them through the actual codec before a further approved attempt. Reuse the successful installed slot; do not reinstall to correct a test-input writer. Work retention and interrupted-update recovery remain unqualified for this fixture until the remaining sequence passes. Static root-rotation tests are not native Windows rotation qualification; the offline fixture does not qualify public-network distribution.

### Windows effect-record boundary checkpoint

The follow-up reused the same installed slot and passed native canonical-input validation. Connection then stopped at the common effect-manifest validator: Windows emits a three-part native identity list while the shared validator accepts only the Darwin identity dictionary. Keep this product-record boundary separate from installation, UTF-8 output and the earlier test-input failure. Direct port tests do not establish lifecycle-record publication compatibility; the next focused regression must connect those layers and retain malformed-identity refusals.

No Work or interrupted-update recovery ran in this follow-up. Preserve any incomplete connection journal, authority and staged originals; do not delete or silently replay them. A post-stop readback remains pending because the diagnostic used a regular-file identity API on a directory. Previous preservation checks retain their original observation time. The owning Work records the next authorization boundary.

### Windows identity publication and update checkpoint

The identity correction retains exact Windows/Darwin variants and malformed/mixed-variant refusals. Focused lifecycle-record tests passed; native Windows subsequently stored and read the connect plan/state with valid reference closure. The corrected installed slot was selected through the official update path and the former slot remains available for recovery.

Qualification is still partial. A long SQLite audit/journal path failed; a shorter fixture operation name enabled update without fixing the general path limitation. Connection then stopped before its first generated file was applied. Its persisted intent remains pending, all four targets read as pre-state, and original bytes are preserved. The generic manager error does not retain the underlying OS exception, so it is not evidence of a permission-policy failure. Diagnose that boundary before a separately approved resume. Work retention and interrupted-update recovery remain unexecuted. Preserve both failed operations and the pending authority; do not reset or reinstall to hide them. Existing-name NTFS replacement identity remains a separate qualification gap.

### Pending connection blocks corrective runtime update

The narrow rename and backup-path correction passed focused source checks and candidate verification. Native qualification stopped before selecting that candidate: the installed manager rejects updates while a project effect is pending. A prepared slot is not an activated runtime, and a validated candidate is not evidence that its native fix ran. Readback preserved the prior selected/recovery slots, pending connection closure, original data and failure records.

Before resuming this state, define an explicit recovery contract for a broken runtime with an incomplete effect. Do not clear pending records, edit selection pointers, bypass the selected-runtime entry or weaken the ordinary update guard. A separate clean test home can qualify the candidate but cannot establish recovery of the original pending connection. Reuse existing runtime/dependency supplies; no remote rebuild is justified by this source-only correction. The owning Work and private connection-correction result identify the exact preserved checkpoint and consumed execution limits.

### Draft: verified recovery of an unapplied connection

Planning status, 2026-11-09: not implemented, activated or authorized for a native run by this draft. The ordinary pending-effect update refusal remains unchanged.

Reuse the independent verified bootstrap recovery entry to finish one exact previously approved connection without first selecting the corrective runtime. This is an explicit recovery command, not an alternative ordinary launcher. Prefer this to deleting/cancelling the connection or permitting arbitrary runtime updates with pending effects. Reuse ProjectSetup/ConnectFiles ordered effects and their existing record kinds; do not add general pending-effect recovery or an automatic fallback.

Admission requirements:

- Authenticate the repair payload externally before executing it; then bind its inventory, dedicated interpreter, platform, release descriptor and digest to the existing home's signed target/trust chain. A caller-supplied manifest hash or successful payload verification alone is not the distribution trust root. Keep channel, root anchor and rollback counters unchanged; refuse stale, expired, mismatched or unavailable trust. Use existing verified transport/staging, never an unchecked source import or a new trust anchor.
- Bind the review to the home, selected/recovery pointers, exact connection operation, project instance/generation, plan and state references, topology, native entry and all effect targets. Initial admission is limited to an unapplied connection (ready/intent at index zero, every target proven pre). Reject unrelated pending effects, activation/native/app pending, incompatible schemas/capabilities, changed original bytes, ambiguous identity and unsupported partial states.
- Acquire the existing management/runtime/project effect locks in one defined order with one owner; do not recursively reacquire non-reentrant locks. Revalidate receipt, trust, identities and expected references under those locks. Recovery records never grant ordinary application writes from an unselected runtime.
- Preserve the original journal, staged originals and failure evidence. Create a verified recovery snapshot/receipt using existing preservation facilities before mutation; logical export alone must not be treated as preservation of staged native-effect bytes.
- Before each effect, revalidate the current pending reference and exact native pre/post state. Reuse the ordered effect writer and its CAS publication. Clear the pending head only through its normal final completed state, never by direct deletion or state editing. Persist repair identity and progress in the manager's existing operation area; no authority schema change.
- Keep signature expiry checks throughout recovery. If retained metadata expires after an effect, use the existing metadata-only renewal bound to the same release operation, preparation receipt and exact target; pass its explicit renewal reference when resuming. Do not skip expiry or prepare a different target to continue the admitted connection. Preserve original plan, snapshot and progress references.
- A process stop requires explicit recovery inspection. Only validated progress from the exact admitted connection state, with the same plan/native identities, expected lifecycle operation lineage and remaining pre-state targets, may be resumed under an authorized bounded run. The record proves valid progress, not which process produced it; unknown, foreign or inconsistent partial state refuses without writes.
- Prove completed connection closure and every after-file byte before returning. Preserve selected/recovery runtime pointers and unrelated authority state throughout connection repair. Then leave recovery execution and use the normal verified update/backup path; it must continue rejecting all other pending effects.

Qualification requirements: preserve refusal tests for pending ordinary updates; cover wrong receipt/operation/home/selection/target, stale signature, incompatible reader/writer capabilities, changed ancestor/original, unrelated pending and interrupted repair. Verify pre-effect refusal, crash-after-effect/before-record handling and final exact post-bytes. Native Windows qualification must exercise the corrected exact-handle rename in disposable scratch before the original connection, then prove ordinary update, Work/body/config/export and separate interrupted-update recovery. Existing source-only and native evidence retain their original limits. An isolated new home is not recovery evidence for the original home.

Out of scope: cancellation records, general effect repair, new trust anchors, key rotation, relaxed no-replace/identity checks, direct pointer or pending edits, permissions, notification registration, remote builds and publication. A safe public entry must fit the existing independently authenticated bootstrap contract; if it cannot, stop before applying to the original installation and report the missing trust boundary.


### Windows Original-Connection Recovery Qualification

The narrow verified-bootstrap recovery contract above is implemented and passed a native Windows ARM64 qualification on the original interrupted installation. The corrective payload completed the exact four-file connection and validated its record closure without changing runtime selection. Normal signed update/backup then passed, followed by synthetic ordinary Work publication/acceptance, new-process before/after body lookup, configuration, logical export, a deliberate interrupted download and a separate normal recovery update. Pending-effect guards and trust checks remained enabled. Existing installations, source files and failed operations were retained; normal pre-update export receipts could advance.

The old selected runtime's long resume operation generated an over-limit audit path and stopped before selection. A bounded fresh normal update with a short operation completed; the exact hidden OS cause is inferred from the old producer and prior native path counterexample, not newly traced. The corrected candidate uses bounded audit/export names. Preserve that first failure instead of relabelling the entire run as first-attempt success.

This evidence covers dedicated installed runtime/native entry calls with the exact generated launcher arguments, not execution of the generated command script itself, model-host usability, public network delivery, native expired-metadata renewal, arbitrary pending effects, replacement of existing user targets or Windows x64. Source/refusal evidence and actual native results remain separate. The owning Work records pending Owner acceptance and points to private inputs, unchanged suppliers, review disposition and consumed execution limits. Do not repeat completed Work/body checks or infer permission for another run from this qualification.
