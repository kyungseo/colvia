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
