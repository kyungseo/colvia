# Operations

Continuation-1 profile; see [authorization and qualification](README.md#continuation-1).

Use [Reference](REFERENCE.md) for command options and [Workspace Contract](WORKSPACE-CONTRACT.md) for exact lifecycle rules. Installed commands use the bound product. Independent source commands require `--source-checkout`; init/update/rollback/detach additionally require `--profile continuation-1`.

## Observe Before Acting

`colvia view`, `colvia status` and `colvia doctor` are read-only. They validate product and typed record graphs, classify pending or unsupported state, and expose verified documentation when available. Their results cover the verified records and product, not later unsubmitted edits, and they grant no write authority. If the launcher fails, use an independent trusted source's view/status/doctor with `--target PATH`.

## Update And Rollback

`colvia update --source PATH --operation-id ID --observed-at TIME` previews a new release. `colvia rollback [--to RELEASE] --operation-id ID --observed-at TIME` previews a receipt-backed prior release. Save the exact preview `request` outside the target and apply it with `--apply --input FILE --confirm TOKEN`. Pending Work/intent publication blocks a new switch.

For the exact admitted delegation-1 predecessor, use a qualified independent continuation-1 source and explicit profile. See [Continuation-1 transition](#continuation-1). Its first durable schema-5 receipt permits exact forward recovery and later compatible same-window rollback; the prior delegation-1 release is not a rollback target. Use matching retained source for old pending operations and old-window repair; never package new code with an old launcher.

A switch preserves project truth and results but changes the product binding and may replace the launcher. Existing confirmation tickets become stale. Re-prepare them against the new binding. Qualify the new release before use: digest verification checks its bytes, while compatibility depends on the release’s qualification evidence.

## Interrupted Operations

Preserve original input, token, source, and observed bytes. Supported complete-file prefixes can resume from independent source using the same operation, target, profile, `--apply --recover --input FILE --confirm TOKEN`. Do not invent a replacement request or delete a receipt to clear a pending operation. Torn bytes, unknown members, wrong file kinds, and missing prerequisites require preservation and investigation.

For pending intent/Work records, preserve the exact prerequisites and original publish request or accepted ticket. A pending worker acceptance can resume with the original `work apply --input FILE --confirm TOKEN`; product lifecycle `--recover` is not a Work option. After the decision is durable, retained control Git objects can supply the remaining pre-images even when the worker folder is unavailable. A mixed pre/post result is not eligible for cancellation. Recover only within the authorized action and verified prerequisites; do not prepare a replacement acceptance merely to finish the same pending decision. See [General Work](GENERAL-WORK.md#worker-publication-development-checkpoint) for the full recovery and cancellation contract.

Git integration failure after completed acceptance is a separate condition. Preserve the accepted history and candidate, report integration as incomplete, and use the project's authorized Git recovery path. Completed decision replay does not restore project content. See [Git Integration And Candidate Reuse](GENERAL-WORK.md#git-integration-and-candidate-reuse) before changing the baseline or submitting a changed result.

## Broken Launcher Or Payload

Use independent exact source `repair` with `--target PATH --source PATH --backup NEW_EXTERNAL_PATH --operation-id ID --observed-at TIME`. Review its preview, then apply the exact request/token. Source must match the active release; the backup must be new and outside source and target, on durable storage. Original bytes are retained before replacement. Repair does not recreate missing metadata or directories, change authority, or upgrade the product. Interrupted repair uses the same request plus `--recover`.

## Detach

Before preparing the detach request, resolve pending Work, intent and lifecycle operations through supported paths. Decide how unfinished Work and results awaiting a decision will be handled before approval; not every unfinished Work state blocks detach. Identify the affected project-entry pointers, local rules, tool-specific instructions and hooks that invoke Harness, and propose their exact edits and the supported future operating method. Complete authorized pre-detach edits under [Check Before Writing](REFERENCE.md#check-before-writing) before preview; keep `./colvia view` pointers until verified completion. Secure compatible independent source and useful manuals outside the target, then preserve the prepared request/token there before applying it. Defer further project edits until the operation resolves: publishing their Work records can change the bound truth. Project-instruction edits and exact detach require their respective authorization.

`colvia detach --operation-id ID --observed-at TIME` previews removal. Apply its exact request/token only after reviewing the removal list. The durable `.hrn/detached.json` receipt is written first; verified product files and launcher are removed individually. Format, candidate planning, intent, Work, results, authored documents, and ignored scratch remain. Unknown or changed bytes block removal rather than being recursively deleted.

Current detach uses paired schema5. If the launcher has already been removed, use the exact independent continuation-1 source with its explicit profile and original request/token plus `--recover`. Historical paired schemas1/2/3/4 remain readable, but their recovery requires matching retained source. A retired `hv2` collision in otherwise-valid detach evidence refuses further removal or completed replay with 65; source diagnostics report degraded/10 with the product error, not clean completion or a new active binding. Preserve the occupant and remaining bytes. Installed observation is unavailable after launcher removal. Preserve useful product manuals before detach. Read retained history as described in [Manual Operation](MANUAL-OPERATION.md). Reinitializing or attaching a detached authority is not supported by this candidate.

After verified completed detach, finish the authorized project-entry edits: remove or replace obsolete `./colvia view` and managed-adapter instructions, retain useful local requirements and required historical/reference bytes, and verify the new entry and a fresh session when available. If a referenced instruction must remain fixed, preserve it and propose a separate current instruction. Runtime removal does not perform this project edit, remove global agent rules or authorize deleting a tool directory. Report remaining edits or unavailable session checks separately from completed detach. See [Repository-Owned Rules](REFERENCE.md#repository-owned-rules).

## Entry-1 Transition

Retained checkout-1 to entry-1 procedure; execute it only with its qualified exact entry-1 source. These historical schema2/schema3 commands do not operate the current continuation-1 candidate.

The unactivated permission amendment candidate accepts an exact completed first-transition B1 at 0600 or 0644 without chmod. Git may restore its unchanged bytes as 0644. Older retained entry-1 installations still report degraded status/doctor/view and refuse their installed update writer at that mode. After separate qualification and authorization, use the trusted independent new source for update; do not treat the old installed refusal as evidence that records changed. New B1 publication and incomplete binding staging remain 0600, and the launcher remains 0755. Current-B1 replay still performs required sync; historical replay must not sync or rewind a newer binding. This description does not activate the amendment or authorize changing a real target.

Before preview, verify the complete allowlisted predecessor identity in [Workspace Contract](WORKSPACE-CONTRACT.md#entry-1-admission-and-publication), obtain qualification for the exact old/new artifacts, and stop cooperating writers. Retire outstanding prepared tickets operationally. Preserve exact old/new sources, original request/token and restoration-verified external target recovery material. Local/parent selected manifests must still match actual content and have no forbidden renamed-entry dependencies, including required sealed direct captured-child references. Unfinished worker/orphan records alone do not block; their bytes and refs remain preserved.

From the qualified new independent source, preview with `./colvia --source-checkout update --profile entry-1 --target PROJECT --source CANDIDATE --operation-id ID --observed-at TIME`. Review and separately authorize its exact request; apply with the same target/source/profile and `--apply --input FILE --confirm TOKEN`. Preserve that input outside the target. Project-owned `./hv2 view` instructions require their own authorized edits to `./colvia view` after verified cutover; runtime changes do not edit them automatically.

S1, the first durable paired schema-2 receipt, is one-way even before new records exist. S1–S5 recovery uses the same request/token, exact new source and admitted physical prefix. Never delete the receipt, run OLD writers or invoke rollback to escape it. Exact executable N must exist before exact O is retired, and O must be absent before B1. Only specified N/binding-staging byte prefixes can be completed. Torn first receipt or S2 file, wrong types/modes, unknown members, O plus *any* `binding.next` (even zero bytes), or B1 plus remaining `binding.next` are preserved non-pass. They can leave both old/new ordinary writers blocked and require separately authorized external restoration/disposition. Do not change files to manufacture an admitted prefix. [Workspace Contract](WORKSPACE-CONTRACT.md#entry-1-admission-and-publication) defines the exact table and same-account substitution limit.

Under the guard, a bounded pre-S1 directory-sync admission check refuses observable unsupported environments with 65 before the first receipt; it may already have created the normal lock anchor. Successful preflight does not excuse later sync failures. Required syncs recur at publication/retirement, prefix retry and exact-current B1 replay. Failure preserves the observed prefix or independently verified current binding and stops before success or degraded content-comparison reporting. Do not roll back B1. Later healthy diagnostics or successful retry do not certify an earlier sync outcome, power-loss persistence or device flush behavior. Older historical replay does not synchronize a newer binding as if it were its own.

For exact completed transition replay, already-changed plan-bound truth produces transient degraded/10 plus `transition_content_verification: unavailable` only after required current-state checks; retain current binding and inspect current Work content/ref state. Comparison-time drift or mismatch still refuses 65. Product/prefix/collision/sync refusals retain precedence. See [diagnostic context](REFERENCE.md#entry-1-diagnostic-context); exit10 alone is insufficient. Historical completion is not rewritten.

A scoped retired `hv2` occupant is never automatically removed or renamed. Otherwise-valid live entry-1 diagnostics return conflict/12 and `lifecycle_ready: false`; lifecycle/replay refuses 65. OLD pending operations need their matching OLD source and original input, not the entry-1 profile. Existing worker results require separately authorized new control Git integration, explicit same-intent worker baseline rebind and resubmission; Core performs none automatically.

## Delegation-1 Implementation Candidate

Continuation-1 inherits the delegation-1 behavior described below. Follow [Continuation-1](README.md#continuation-1) for current lifecycle commands and authorization requirements. Historical versions retain their original meaning. Human authorization comes from the Owner’s actual decision; host authentication and general readiness require their own evidence.

Retained delegation-1 lifecycle writers require that exact historical source and pair plan/receipt schema 4. The initial update admits only the exact audited entry-1 predecessor in Getting Started. The first durable schema-4 switch receipt is the one-way boundary: every older writer must refuse, even before any schema-3 intent exists. Do not roll back to an old window at any later prefix. Recover forward with the exact new source and original request. The launcher path remains `colvia`; no retired `hv2` path is removed by this switch.

Observable old pending init/switch/detach/intent/Work and damaged old target state block admission. Complete them with their matching old source first. Repair's completion receipt lives only in its external backup: after the last target replacement but before that external receipt, the target cannot reveal that repair is unfinished. Finish or explicitly abandon that completion before transitioning, and preserve the backup. If transition has occurred, old repair recovery must refuse without changing either target or backup. A successful transition does not complete the earlier repair; no new marker or automatic backup deletion exists.

During entry-1 to delegation-1 transition, local and parent snapshots continue to exclude the verified same-path launcher. Existing worker commit trees still contain old launcher bytes, so their results remain readable but cannot be accepted directly against the new runtime. Preserve the old worker result and retained refs; integrate the exact new launcher into the control Git baseline under separate Git authorization, then explicitly rebind and resubmit before requesting acceptance. Runtime update does not perform those steps.

Same-window update and rollback preserve all accepted/unaccepted intent history, Work, composition, planning, delegated/cancelled/revoked decisions and references. A recorded historical replay validates current graphs and reports changed truth as unavailable for its old observation; it never overwrites a newer active release. Retained delegation-1 repair restores exact active candidate bytes only; its detach preserves project truth and its schema-4 receipt. Current source uses the next section. Historical receipts remain auditable; incompatible pending operations require their exact retained source, not a rewritten request.

Interrupted namespace/durability states are supported only where exact candidate tests establish a recoverable prefix. Torn, unknown or neither-pre-nor-post bytes are preserved and refused. An unavailable synchronization operation is not success. No lifecycle action grants Git or actual-adopter authorization.

## Continuation-1

Current init/update/rollback/repair/detach use paired schema 5. Initial update admits only delegation-1 release `product-release-d71214aa37687189ebf12c51`, inventory SHA-256 `d71214aa37687189ebf12c517874016e2d50622b0fbd21d3e5b971df9ec59262`. Verify the actual target, candidate qualification and exact Owner application authorization first. Arbitrary earlier windows and old pending operations are refused; preserve their matching retained source and original request.

Preview from trusted source with `./colvia --source-checkout update --profile continuation-1 --target PROJECT --source CANDIDATE --operation-id ID --observed-at TIME`; review and apply its exact saved request/token. The first durable schema-5 receipt commits to forward recovery even before any continuation exists. A saved preview alone is not pending authority. After that receipt, use only the exact new source and original request with `--apply --recover`; never downgrade to delegation-1 or older. Torn/unknown prefixes are preserved. Existing worker results remain historical and need separately authorized control Git integration, explicit same-intent rebind and resubmission before acceptance against the changed launcher.

Compatible same-window update/rollback must preserve all continuation and existing project truth in both directions. Qualification covers the exact tested P/Q pair, not arbitrary future releases. Normal update/rollback/detach refuse pending continuation. Exact active-release repair may proceed only with a valid classifiable pending graph, unchanged binding and preserved truth, under the existing external-backup limits. Unknown/damaged continuation also blocks repair. There is no general current repair or automatic history reset.

Continuation pending recovery/cancellation is bound to the original home/location, exact binding and references. Moving or cloning pending authority does not rebind it. Read the preserved history; recovery is possible only after separately authorized restoration to the original conditions passes every original check. A read-only clone audit is not recovery.

Detach preserves continuation choices, selections and current with intent, Work and planning truth. Its new paired schema-5 receipt is auditable independently; old schema-4 and earlier pending detach require their retained source. The project-entry cleanup after verified detach remains a separate authorized change.

## Windows-2 Native Entry And Recovery

For a qualified windows-2 project, invoke the verified managed colvia file through an absolute allowed Python path with -I -B from native Windows PowerShell. Replace the illustrative paths with the exact qualified paths; do not copy them as installed locations:

```powershell
& 'C:\Runtime\python.exe' -I -B 'C:\Project\colvia' view
```

For independent source init/update/rollback/detach, retain --source-checkout and explicitly select --profile windows-2 together with the existing target, candidate and operation arguments. Source repair retains its existing interface and exact-active-source checks; do not invent a new repair profile argument. The profile selects a requested policy, while verified candidate/active release and actual runtime checks establish whether that request is admissible. Do not fall back to entry-1 or select a window from host OS alone.

Use only fresh or same-window operations. Retain original preview requests/tokens and compatible recovery source outside the target on durable storage before applying. Interrupted lifecycle uses its existing --apply --recover --input FILE --confirm TOKEN path where supported; worker acceptance uses the original work apply ticket and does not gain a lifecycle --recover option. Re-observe state and preserve unknown/torn bytes; automatic replace retry is zero. Existing exact authorization can cover the original retry without a new generic approval step.

Before mutation, apply Workspace Contract's actual native local NTFS path checks and whole-operation read-only preflight for existing files to replace/remove and existing files requiring write-capable flushes. New files are read-only clear; preserved/read-only source files are not normalized. For detach the complete remove set and any required-flush files must pass before publishing the detach receipt. Recovery includes required reflushes of the admitted existing prefix. Pure read/preserve exemption does not waive exact bound observations, and completed read-only replay gains no mutation or reflush. Later drift or failure still requires exact prefix preservation.

For repair, distinguish retrying the original exact request from preparing a separate request. If an attribute or other bound observation differs from admitted before/after, refuse the old retry without changing its token/backup or claiming success. External restoration of the original attribute permits reconsideration only if every exact byte/observation, backup, candidate, binding and prefix condition holds; it is not a product action, a restoration instruction or a success guarantee. External repair evidence alone is not a product pending barrier. While a remaining replacement target is read-only, a fresh preview is also non-pass with no executable request/token. Only when no such target remains and all current active-product/candidate/truth and existing pending guards permit it may a separate preview describe an executable repair. Its apply must satisfy the full Workspace preflight, including required flushes. Use a new operation identity/request/token and new backup destination, preserve prior originals/evidence and obtain the authorization required for that exact apply. Do not bypass actual pending lifecycle/detach, automatically re-preview, clear attributes, or treat the new result as completion of the old request.

Detach6 publishes the receipt first and preserves project truth and instructions as the existing detach procedure requires. After launcher removal, mutation recovery uses compatible independent windows-2 source and the same plan/token. Read-only validation uses the complete plan embedded in the receipt and does not require a separate external original-plan file or token. A validated complete detach6 identifies the windows-2 policy but does not certify runtime, prior flush outcomes or permit reinitialization. Keep useful manuals and any required exact recovery inputs outside the removal set. Historical detach1/2/3 retain their own reader/recovery scope; never reinterpret them from the current Windows host.

## Windows Init

The agent prepares machine input; the human reviews the target, proposed action and exact confirmation. Prefer `--input FILE` in Windows PowerShell 5.1. A request or ticket must be UTF-8 without a BOM, use LF only and end with exactly one LF. Canonical JSON also requires sorted keys, two-space indentation and unescaped Unicode. The agent can emit it with Python's `json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True) + "\n"`, encoded as UTF-8 and written in binary mode. Save only the returned `request` for lifecycle apply or `ticket` for intent/Work apply, not the enclosing preview/prepare response. Keep the exact file and confirmation token on durable storage outside the target before applying.

Do not pass JSON through PowerShell text pipelines, default output redirection or a JSON reserialization step and assume its bytes survive. Stdin is supported only when its transport preserves the canonical bytes; use a file when that cannot be verified. Preserve quoting and Unicode in paths and values. Single-quoted PowerShell literals keep `$` and `&` literal; represent a literal apostrophe by doubling it. Check the native command's `$LASTEXITCODE` before continuing.

For a separately qualified fresh windows-2 installation, substitute the actual allowed Python, prepared source and target paths below. This example uses one PowerShell line per command and creates no permission to install. The common continuation-1 source cannot stand in for explicitly prepared windows-2 source.

```powershell
$Python = 'C:\Runtime\python.exe'
$Source = 'C:\Source'
$Project = 'C:\Project'
$Launcher = Join-Path $Source 'colvia'
& $Python -I -B $Launcher --source-checkout init --profile windows-2 --target $Project --source $Source --authority-home-id project-home --operation-id init-1 --observed-at 2026-01-01T00:00:00Z
if ($LASTEXITCODE -ne 0) { throw 'Init preview failed; preserve and inspect the output.' }
```

Use the actual unique operation ID and observation time. After the agent saves the canonical request and the human authorizes that exact action, apply using the saved file and its matching token. Replace the illustrative input path and token; preserve the source and request for recovery.

```powershell
$RequestFile = 'C:\Recovery\init-request.json'
$ConfirmToken = 'TOKEN_FROM_THIS_PREVIEW'
& $Python -I -B $Launcher --source-checkout init --profile windows-2 --target $Project --source $Source --apply --input $RequestFile --confirm $ConfirmToken
if ($LASTEXITCODE -ne 0) { throw 'Init did not report success; preserve the request and inspect current state.' }
& $Python -I -B (Join-Path $Project 'colvia') status
if ($LASTEXITCODE -ne 0) { throw 'Installed status is non-pass; inspect the reported state.' }
```

Do not infer from a failed apply that no bytes were published. Use the original request/token and the supported recovery path only after checking the observed prefix. Unknown state, read-only targets and unverified runtime or filesystem conditions remain non-pass; these examples do not establish native qualification or a successful fresh-reader exercise.

## Official Execution Records

The optional macOS official-execution windows preserve project-owned execution capsules under `.hrn/executions/`. V2 stores allowlisted metadata there and keeps original document recovery copies and worker transient material in an explicit private host control root outside Git. Existing v1 payload records are preserved without automatic migration or deletion. Cancellation receipt is not effect cessation. Unresolved effects block new runs and lifecycle mutation; explicit resolution records current document/process observations without deleting evidence or restoring documents. Detach preserves capsules and original outputs. Use the verified release's `docs/OFFICIAL-EXECUTION.md`; no automatic retry or Core acceptance is added.

## Setup And Onboarding Details

Read the relevant section when preparing setup, a lifecycle change or recovery. For ordinary work, use [Getting Started](GETTING-STARTED.md) and the current installed adapter.

Continuation-1 profile; see [authorization and qualification](README.md#continuation-1). Start with [the work cycle and example requests](CONCEPTS.md#the-work-cycle), then use the setup and first-Work steps below.

For trusted source setup, use a fresh project and final, GIL-enabled CPython 3.14.6 or 3.14.7. The managed macOS candidate below supplies its separately pinned runtime. Installation needs explicit operator authorization; a successful local test does not authorize installing into another repository.

### Onboarding: macOS Managed Distribution Candidate

The macOS arm64 distribution candidate prepares its own pinned CPython 3.14.10. It uses a versioned bootstrap and external SHA-256 digest supplied with that release; a source clone, Homebrew setup and shell configuration edits are not part of this path. Public URLs and final qualification are pending. Use an authorized, qualified release before applying it to a real project. Windows qualification remains required before public release.

The sequence is **prepare Colvia → connect a project → agree on the first task → review the result**. Download the named bootstrap to a durable directory, compare its SHA-256 with the separately supplied release value, then run it without arguments to see its storage and preservation plan. Apply only that reviewed plan with the exact confirmation value it displays. The bootstrap prepares the tool and Python under `~/Library/Application Support/Colvia`; it leaves project files and shell settings in place.

From the chosen fresh project, ask your agent:

> Prepare Colvia for this project using the verified release. Show the target, proposed changes and what will be preserved. Keep project setup separate from the first task; wait for my installation decision.

The management command lives at `"$HOME/Library/Application Support/Colvia/bin/colvia-manage"`. Its `install --target PROJECT` command previews project connection. A successful preview saves its exact request under the tool’s `requests` directory and displays its path and confirmation value. The agent can choose an external path with `--json --save REQUEST_FILE`, explains that same request and applies it after your decision using `--apply --input REQUEST_FILE --confirm TOKEN`. Keep the request outside the project. `official-execution-2` is a separate explicit profile with its [execution limits](OFFICIAL-EXECUTION.md); existing continuation projects have no direct switch to that profile.

After connection, `./colvia view` shows the current project and work. The agent uses `./colvia view --details` to find its verified instructions. For the first task, give the intended result and the files or scope that may change. For example: “Improve the installation section in this README. Keep the rest of the document, show the proposed scope and checks, then wait for my decision.” The agent prepares the plan and exact intent, uses an existing applicable approval, and explains results, remaining limits and one useful next step with its reason. You decide acceptance. Git commits and publication remain separate choices.

For a fresh conversation, ask: “Read this project's instructions and current Colvia Work. Explain what was accepted, what remains and the recommended next step before changing files.” The agent compares current records, referenced plans and current files, carries forward consumed time and attempts, and continues the same authorized scope when its conditions still hold. A new conversation does not reset pending operations or create a new Work.

#### Onboarding: 한국어: 설치 후 첫 작업과 재개

macOS arm64 배포 후보는 필요한 Python을 전용 위치에 함께 준비합니다. 공개 배포 주소와 최종 검증 결과는 공개 단계에서 제공됩니다. 실제 프로젝트에는 승인한 검증 배포본을 사용하세요. Windows 전체 기능·설치 검증도 공개 전에 완료해야 합니다.

먼저 배포본에 명시된 bootstrap 파일을 지속 보관할 위치에 내려받고, 별도로 제공된 SHA-256과 대조합니다. 인수 없이 실행하면 저장 위치와 보존 범위가 나옵니다. 내용을 확인한 뒤 표시된 확인값으로 적용하면 Colvia 도구와 Python이 준비됩니다. 저장소 clone, Homebrew 설치, shell 설정 편집은 이 설치 경로의 준비 사항이 아닙니다.

다음으로 에이전트에게 “검증된 배포본으로 이 프로젝트에 Colvia를 연결할 범위와 보존할 내용을 보여줘. 실제 적용은 내 결정을 기다려줘”라고 요청하세요. 성공한 미리보기는 정확한 요청을 관리 도구의 requests 폴더에 저장하고 경로·확인값을 보여줍니다. 에이전트가 그 요청을 설명하고 승인한 내용 그대로 적용합니다. 연결이 끝나면 프로젝트의 `./colvia view`에서 현재 상태를 볼 수 있습니다.

첫 작업은 원하는 결과와 바꿔도 되는 범위를 알려주는 것으로 시작합니다. 예를 들어 “이 README의 설치 안내를 보강하고 싶어. 나머지 내용은 보존하고, 수정 범위와 검사 방법부터 보여줘”라고 요청할 수 있습니다. 에이전트가 계획·작업 요청을 준비하고, 유효한 승인이 있으면 그 범위에서 진행합니다. 결과를 검토할 때는 완료한 내용, 남은 한계, 다음 추천과 이유를 함께 보여줍니다. 결과 수락과 Git commit·게시는 각각 결정합니다.

새 대화에서는 “이 프로젝트의 지침과 현재 Work를 읽고, 수락한 내용과 남은 일, 다음 추천을 정리해줘”라고 요청하세요. 에이전트가 현재 기록·참조 계획·파일을 대조하고 기존 승인, 소비 시간과 시도 횟수를 이어받습니다. 미완료 동작은 같은 Work에서 확인·복구합니다.

#### Onboarding: Update, Recovery And Removal

Use a named new version and its external bootstrap digest to prepare an update. Project `update`, `rollback`, `repair` and `remove` preview first and use the same exact-request apply flow. `rollback` targets the project's recorded prior release, not a Python downgrade. `repair` requires a new external backup location. Keep the exact release and request for interrupted operations and use the supported `--recover` flow; inspect unknown effects before another attempt.

Project `remove` detaches managed product files while retaining Work, intent, result and recovery records. Completed detach supports retained-record reading; it is not a fresh installation target. `remove-tool` separately removes the management entry and keeps its recovery copy, requests, shared Python and projects. This version does not support shared Python removal through `remove-runtime`; it retains Python, releases and recovery material. Moving a project or cloning its records does not copy the user-level Python store; acquire the exact pinned runtime on the destination machine before using its launcher.

갱신할 때는 명시한 새 버전과 외부에서 확인한 bootstrap 해시를 사용합니다. 프로젝트 `update`, `rollback`, `repair`, `remove`는 먼저 범위를 보여주고 승인한 요청을 적용합니다. `rollback`은 기록된 이전 프로젝트 배포본으로 돌아가며, `repair`는 새 외부 백업 위치를 요구합니다. 중단되면 정확한 배포본·요청·부분 상태를 보존하고 지원되는 복구 경로를 확인하세요.

프로젝트 `remove`는 Colvia 연결을 해제하고 작업·승인·결과 기록을 남깁니다. 연결 해제 뒤에는 보존한 기록을 조회할 수 있으며, 새 설치 대상으로 다시 연결하는 흐름은 지원하지 않습니다. `remove-tool`은 관리 명령만 제거하고 복구 사본·요청·공유 Python·프로젝트를 보존합니다. 현재 버전의 remove-runtime은 공유 Python 제거를 지원하지 않으며 Python·배포본·복구 자료를 보존합니다. 다른 기기로 프로젝트를 옮길 때는 그곳에도 정확한 전용 Python을 준비해야 합니다.

To restore a removed management command, verify and apply the same named bootstrap again. This restores the management entry; it does not reconnect a detached project. If a runtime is damaged or an activation lock remains, preserve that state and ask the agent to inspect it before recovery. The current bootstrap preserves an existing mismatched runtime, release or management entry. Automatic repair of these stored components is unavailable. Keep the damaged bytes and required old versions; before any manual relocation, check active consumers and agree on the exact preserved path and version to restore. Project `repair` is a separate, supported operation. The retained matching manager under `tools/<digest>/colvia-manage` can recover its own exact interrupted project request with `--recover`; a newer manager does not replace that identity.

제거한 관리 명령은 같은 버전의 bootstrap을 다시 검증·적용해 복구합니다. 프로젝트 연결 해제와 관리 도구 복구는 별개입니다. 전용 Python이 손상됐거나 설치 잠금이 남았다면 원본을 보존하고 에이전트에게 현재 상태와 복구 경로 확인을 요청하세요. 현재 bootstrap은 손상된 전용 Python·배포본·관리 명령을 보존합니다. 이 저장 구성요소의 자동 복구는 아직 지원하지 않습니다. 손상 원본과 필요한 구 버전을 남기고, 수동 이동 전 사용 중인 프로세스·프로젝트와 보존 위치·복원할 정확한 버전을 확인해야 합니다. 프로젝트 파일의 repair는 별도 지원 흐름입니다. 중단된 프로젝트 요청은 tools/<digest>/colvia-manage의 해당 버전 도구로 정확한 요청에 --recover를 적용합니다. 새 관리 도구로 원 요청의 배포본 identity를 대체하지 않습니다.

Existing projects retain their recorded profile; the exact supported official-execution-1 predecessor selects official-execution-2 for its one-way transition. Only a fresh `install` defaults to continuation-1. Use an explicit profile after inspecting damaged or incomplete binding information. Run `status --details` with the same manager and target to inspect partial states before recovery. Preview writes only its saved request outside the project.

기존 프로젝트는 연결 기록의 프로필을 이어받습니다. 정확히 지원하는 official-execution-1 이전 배포본은 단방향 전환을 위해 official-execution-2를 선택합니다. 새 install만 continuation-1을 기본값으로 사용합니다. 연결 기록이 손상됐거나 불완전하면 상태를 확인한 뒤 정확한 프로필을 지정하세요. 중단 상태는 같은 관리 도구의 status --details와 대상 경로로 확인합니다. 미리보기는 프로젝트 밖에 요청 파일만 저장합니다.

A forced SIGKILL or power loss can leave an operation or child process unconfirmed. Preserve the exact request and files; verify process termination and project status before recovery. Atomic publication covers ordinary process interruption, not a guarantee against power or storage failure.

강제 SIGKILL이나 전원 손실 뒤에는 적용 결과와 자식 프로세스 종료 여부가 미확인일 수 있습니다. 정확한 요청과 파일을 보존하고, 프로세스 종료 및 프로젝트 상태를 확인한 뒤 복구하세요. 원자적 게시는 일반적인 프로세스 중단을 다루며 전원·저장 장치 장애까지 보장하지 않습니다.

#### Onboarding: Technical Details

- The release pins the runtime archive, normalized file tree, verifier and product payload. Hashes identify the supplied bytes; the current unsigned distribution does not independently authenticate its publisher.
- Launch checks cover interpreter, stdlib, native libraries, modes, links and exact tree membership before executing Python. Source operators keep the explicit `<trusted-python> -I -B colvia --source-checkout ...` entry. There is no system-Python fallback for a prepared managed launcher.
- Managed entry uses project Git configuration and ignore rules with user/system Git configuration disabled. Before the first Work, review the effective project rules and any intended shared ignores. It selects an available actual Git binary on macOS without triggering developer-tools installation. A primary Git repository needs Git; the basic non-Git flow can operate without it.
- Managed entry uses fixed executable paths and a closed environment; inherited API credentials, custom PATH, SSH agent and proxy settings are not forwarded. The official path separately checks its pinned CLI and subscription inputs. Proxy-dependent download and user-level Git filters/attributes require separate qualification. Each download keeps a 120-second limit and does not retry automatically.
- The initial source remains `continuation-1`; optional `official-execution-2`, unknown/partial state, exact predecessors and retained detach follow their existing contracts. View success does not establish native execution eligibility.
- The local fixture changes only fixed storage/asset locations. Public-origin download, clean-Mac user experience, Gatekeeper/notarization and Windows remain separately qualified conditions. Preserve first-attempt failures when comparing later corrections.

### Onboarding: Prepare Project Ignore Rules

During authorized adoption, the agent/operator prepares project-owned root `.gitignore` before `init` and the first Work baseline. If absent, use the defaults below; otherwise preserve contents, comments and intentional exceptions, adding only missing applicable rules after review. Never overwrite it or copy the Harness source’s development `.gitignore`.

```gitignore
# Operating system files
.DS_Store
Thumbs.db

# IntelliJ IDEA: local project settings
.idea/
*.iml
*.iws
*.ipr

# Visual Studio Code: local settings and workspaces
.vscode/
*.code-workspace

# Project-root scratch space (not durable deliverables)
/temp/

# Editor temporary files
*.swp
*.swo
```

These defaults exclude personal IDE files; retain deliberate shared-configuration exceptions. Add build, dependency, environment and generated-output rules only after confirming actual project tools and artifact policy. Never blanket-ignore binaries or customer deliverables by extension.

Create root `temp/` for scratch during setup or when needed; clones do not restore empty ignored directories. Before pausing or cleaning up, preserve important ignored results durably outside scratch.

Never ignore the entire `.hrn/` tree: its records and managed runtime remain eligible for version control. Harness manages its own `.hrn/.gitignore` for `staging/` and `locks/`. Check representative IDE/temp paths with `git check-ignore`, and check that `.hrn/format.json`, `.hrn/intents/`, `.hrn/work/`, `.hrn/planning/`, `.hrn/product/`, `colvia` and project Markdown are not hidden by the effective rules. Git ignore rules do not untrack files already committed; do not remove tracked files as part of this setup without authorization.

The agent/operator performs this adoption procedure outside Core `init`. Root `.gitignore` and `temp/` stay project-owned; update, rollback and detach do not replace them. Once Work starts, ignore-rule changes must follow its scope and content-validation rules.

### Onboarding: Prepare Project Agent Entry

For new projects, put shared instructions, purpose/context/plan pointers and stable `./colvia view` entry in project-owned root `AGENTS.md`; never pin a managed release path. With Claude Code, add a thin root `CLAUDE.md` directing it to read and follow `AGENTS.md`, without duplicating instructions.

For existing projects, preserve entry files and tool-specific instructions. Reconcile shared instructions before replacing duplicates with pointers; preserve unique Claude rules and keep tool-specific additions in their entries. Do not copy this repository’s development entry. A pointer directs agents to read and follow `AGENTS.md`; it does not prove they did.

For project-specific adapter additions and their maintenance boundaries, use [Project-Owned Adapter Additions](REFERENCE.md#project-owned-adapter-additions). Runtime updates leave these additions unchanged; a later detach needs a separate review of obsolete project-entry instructions.

The agent/operator prepares these project-owned files within approved adoption scope. Core init/update/rollback/detach neither generate nor overwrite them. Managed payload entries describe Harness source, not the project.

Use [Repository-Owned Rules](REFERENCE.md#repository-owned-rules) to connect applicable documentation, validation and domain procedures. Include the project language default when one exists; [Document Language](REFERENCE.md#document-language) distinguishes it from an explicit artifact request and conversation explanations. For a new project, select a small set and connect its canonical location. For an existing project, compare affected rules and preserve local instructions before applying an authorized diff. Record the adopted source and any local choice in the existing rule or maintainer document. A runtime update does not update these rules automatically; compare relevant changes explicitly, including their verification and removal impact.

### Onboarding: Initialize A Fresh Project

From a trusted source, use [PowerShell for Windows-2](OPERATIONS.md#windows-init) or entry-1 below:

```sh
./colvia --source-checkout init --profile continuation-1 --target /path/to/project \
  --source /path/to/source --authority-home-id project-home \
  --operation-id init-1 --observed-at 2026-01-01T00:00:00Z
```

This previews the candidate and returns a `request` and `confirm_token`. Review the target and source; save only the `request` object as canonical JSON outside the target. Then apply that exact request:

```sh
./colvia --source-checkout init --profile continuation-1 --target /path/to/project \
  --source /path/to/source --apply --input /path/to/init-request.json --confirm TOKEN
```

Run `/path/to/project/colvia status` after installation. A verified active product exposes its `documentation_root`. No initial intent or Work is created. A preexisting launcher, old-generation home, unsupported Git topology, or ambiguous partial install is preserved and refused. Any immediate-root `hv2` occupant (NFC/casefold, file/directory/symlink) found at first admission is refused before the first target write; a late collision preserves earlier permitted writes and stops further publication. See [Entry-1 admission](WORKSPACE-CONTRACT.md#entry-1-admission-and-publication) for the tracked-but-absent distinction and exact limits.

### Onboarding: First Serial Work

1. An agent prepares a typed intent draft with goal, scope, expected outcome, acceptance oracle, destination, forbidden scope, and unresolved gaps. `colvia intent draft` publishes the proposed record; it does not accept it.
2. `colvia intent prepare` returns a ticket for the human to review. `colvia intent apply --confirm TOKEN` consumes the exact accepted ticket. Material gaps must be resolved first.
3. The agent publishes a Work baseline referencing the accepted intent, edits within the declared scope, and submits the full result manifest for review using `colvia work publish`.
4. `colvia work prepare` binds the exact result and current prerequisites. The human decides acceptance; `colvia work apply --confirm TOKEN` records that decision and selection. A selected accepted result derives completed state. The optional exact ordinary-worker grant is described in [Delegation-1](GETTING-STARTED.md#delegation-1-implementation-candidate); it does not authorize intent or parent acceptance.

Use [General Work](GENERAL-WORK.md) for input fields and [Guided Intent](GUIDED-INTENT-FORMATION.md) for acceptance. The agent prepares canonical JSON via `--input FILE` or stdin; review without editing JSON below. General onboarding and installed use need [separate evidence](SECURITY-AND-SUPPORT.md). Keep one editing Work during serial use; the tool cannot stop arbitrary ordinary-file editors.

Do not use a pending proposal, a successful command, a review verdict, or an agent's statement as human acceptance. Use [Operations](OPERATIONS.md) when an exact operation is interrupted.

Accepting a worker result applies exact changes on control, leaving Git HEAD, index and refs unchanged. Before the next worker, follow project Git policy and [Git Integration And Candidate Reuse](GENERAL-WORK.md#git-integration-and-candidate-reuse). Its baseline needs a control commit matching the observed product and verified launcher; an existing candidate may suffice. Report Work acceptance and Git integration separately. The linked example covers reuse and stop conditions.

### Onboarding: Review Without Editing JSON

Start with `./colvia view` and follow its guidance to the current adapter; this release exposes verified manual/adapter paths in `./colvia view --details`. The managed manual explains Harness operation; project README/context/plan/DR/brief/Work documents explain project purpose and progress. Keep the stable view command in project entry, not a release-specific adapter path.

The agent prepares machine input and explains the existing Work narrative in your language: scope, progress, results, checks, limits and the decision needed. Review intent/Work and confirmation views; full revision identities and tokens support them. Decide the exact action before apply. Disclose changed/missing references and narrative/selected-record disagreement. English diagnostic labels do not set the conversation language. Views support the existing explanation; no automatic report, second status registry or extra record is needed.

For briefs, decision records or unresolved questions, use [Project Document Assistance](REFERENCE.md#project-document-assistance) with existing project documents.


### Onboarding: Transition To Checkout-1

Historical procedure for a retained qualified checkout-1 source only. The current candidate cannot perform this earlier transition. Use its exact retained manual and source; do not substitute a new profile. The first durable checkout-1 switch receipt is one-way even before new records, and loss of the original source/request can leave no supported recovery. Preserve restoration-verified recovery material before an authorized transition.

### Onboarding: Transition To Entry-1

Historical procedure for a retained qualified entry-1 source only. Read [Entry-1 transition](OPERATIONS.md#entry-1-transition) for its exact checkout-1 predecessor, one-way schema-2 boundary, original-request recovery, unsupported prefixes and separate worker rebind. These instructions do not authorize applying the current continuation-1 candidate with an old profile.

### Onboarding: Delegation-1 Implementation Candidate

Continuation-1 inherits the [optional schema-3 ordinary-worker grant](GUIDED-INTENT-FORMATION.md#delegation-1-implementation-candidate). Only an explicit Owner decision grants that exact scope; an agent role or broad instruction to continue does not. No-grant use keeps human acceptance. Intent and parent acceptance, Git integration and source-development acceptance remain separate. Host caller enforcement and general first-session usability are unverified.

Historical locator: entry-1→delegation-1 used the exact entry-1 inventory `2216a2634eb3fa5d6a8bfa7c7d4847b29fb2443ba7b367156c15b15ddb5a17e0`, matching retained source and original input. Old pending operations still need their own source/request. This is not the current transition path.

### Onboarding: Continuation-1 Setup And Resume

Fresh setup uses the continuation-1 command above. The exact release needs qualification, accepted source-contract scope and separate Owner installation authorization; source-only decision files are not installed prerequisites. For an existing installation, [Operations](OPERATIONS.md#continuation-1) admits only the exact delegation-1 predecessor or a compatible continuation-1 release. Do not apply the historical entry-1 transition instructions with current source.

Before starting work, name the existing project plan and the item it covers. After a result is actually accepted, report what that item achieved, what remains and whether the human selected a follow-up. Read `./colvia view continuation WORK_ID` in a new session. A proposal still needs intent approval; an existing Work follows its own current state; explicit none ends this follow-up path; undecided requires a choice only when the next action depends on it. The adapter explains plan updates and reference/content checks without adding another tracker.

### Onboarding: Windows-2 Entry

For a qualified windows-2 target, invoke the verified colvia file with an absolute allowed Python path and -I -B from native Windows PowerShell. This replaces only the generic ./colvia prefix; preserve arguments, human authorization and verified view/manual routing. Independent source lifecycle requires the explicit windows-2 profile, matching candidate and admitted native runtime. A POSIX shell, executable bit, entry-1 fallback or unverified interpreter alias is not a substitute. Fresh and same-window operations only; no old-window/cross-OS migration or detached-authority reinitialization. Report the exact qualified tuple and unavailable observations. These instructions grant no intent/result acceptance, writer authorization or environment qualification.

### Onboarding: Optional Official Execution Candidate

The shared source still declares `continuation-1`. Preparing `scripts/prepare-official.py --output NEW_DIRECTORY` creates the explicit macOS `official-execution-2` payload without installation or execution. Install only with separate authorization and the existing lifecycle preview/apply procedure. The verified release includes `docs/OFFICIAL-EXECUTION.md`. The candidate does not authorize updating an existing adopter or qualify Windows.
