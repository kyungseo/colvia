# Reference

Continuation-1 profile; see [authorization and qualification](README.md#continuation-1).

Document authority and currentness: [Documentation Index](README.md).

The managed macOS arm64 distribution separately admits its exact pinned CPython 3.14.10 tree and manifests with isolated entry. `supported_versions` remains the legacy allowlist; `admission_path` reports the current gate. Windows policy is unchanged. Preserve a damaged managed runtime and follow [its recovery procedure](OPERATIONS.md#onboarding-update-recovery-and-removal). Tree identity admits an exact relocated copy and does not authenticate installation provenance.

## Single-Home Development Commands

The current development candidate profile is `continuation-1` with one `.hrn/` home. It exposes a machine interface plus a read-only human view and manual natural-language adapter. An installed project uses `./colvia`. An independent contribution source uses `./colvia --source-checkout` explicitly.
Modifying an adopter requires its own authorization, even when trusted source is available and its tests pass.

| Entry | Command | Input and effect |
| --- | --- | --- |
| Independent source | `init --profile continuation-1 --target PATH --source PATH --authority-home-id ID --operation-id ID --observed-at TIME` | Preview only; save its `request` and token. Apply with the same target/source/profile plus `--apply --input FILE --confirm TOKEN`. |
| Installed or independent source | `status`, `doctor` | Read-only product and complete record-graph diagnostics. Source accepts `--target PATH`. Healthy product output derives `documentation_root` and its README entry from the verified active release. |
| Installed | `update --source PATH --operation-id ID --observed-at TIME` | Preview a candidate; `--apply --input FILE --confirm TOKEN` applies the exact request. |
| Installed | `rollback [--to RELEASE] --operation-id ID --observed-at TIME` | Preview a receipt-backed release; apply the exact request and token. |
| Installed | `detach --operation-id ID --observed-at TIME` | Preview exact managed removal; apply the exact request and token. Project truth remains. |
| Independent source | `update`, `rollback`, `detach` with `--profile continuation-1 --target PATH` | Exact original request/token plus `--apply --recover` resumes a supported publication prefix. Preserve unknown/torn bytes. |
| Independent source | `repair --target PATH --source PATH --backup NEW_EXTERNAL_PATH --operation-id ID --observed-at TIME` | Preview restoration of the exact active product. Apply its request/token; interrupted repair uses `--recover`. Installed repair is not exposed. |
| Installed | `intent draft`, `intent prepare`, `intent apply` | Canonical JSON from `--input FILE` or stdin. Apply additionally needs `--confirm TOKEN`. |
| Installed | `work publish [--worker PATH]`, `work prepare`, `work apply` | Canonical JSON from `--input FILE` or stdin. Worker result publish requires the registered linked worker path; start/baseline rebind omit it. Apply additionally needs `--confirm TOKEN`. Worker accept records the decision before exact file application and selects completion only after whole-result checks; human baseline rebind is separate. |

See [General Work](GENERAL-WORK.md) for exact machine input fields and recovery constraints, and [Workspace Contract](WORKSPACE-CONTRACT.md)
for record and lifecycle boundaries. Apply consumes the preview's `request` or prepare's `ticket`, not the outer response envelope.
Preview/prepare does not grant permission; the human decides acceptance. Confirmation tokens bind bytes, not OS identity.

`documentation_root` is project-relative and derived, not another stored authority or document registry. It appears only after product and
record verification succeeds (possibly with pending record publication or unsupported local runtime clearly classified). Pending product,
detached, degraded, or unrecognized state does not invent an active document root. The field locates the manual; whether a user read
it or accepted project-authored documents must be established separately. Before detach, retain a trusted independent source/manual if needed.
For a pending Work publication without a decision, preserve and retry the exact original publish request after restoring its prerequisites.
For a pending Work decision or intent acceptance, preserve the original ticket and confirmation token, restore the required runtime/content/document
preconditions, then retry the same apply. Do not invent a replacement decision to bypass pending records. The narrowly supported local or all-pre worker cancellation of a pending Work acceptance follows [General Work](GENERAL-WORK.md); this advice does not remove that contract. Before mutation, use final, GIL-enabled CPython 3.14.6 or 3.14.7 for the legacy path; for managed macOS entry, preserve damaged bytes and restore its exact pinned CPython 3.14.10 tree through the recovery procedure. Single-home mutation entries, root creation, and the shared writer guard enforce implementation, explicit version membership, final release level and GIL-enabled build before writing. This is a trusted-local support check, not interpreter authentication. Status reports these actions without modifying records or manufacturing recovery input.

## Optional Local Execution Input Check

Use `./colvia doctor --runtime-input FILE` when the agent or operator already has the exact runtime input for a planned official execution. Independent source accepts the same option with `--source-checkout doctor --target PATH`; the macOS manager accepts `doctor --target PATH --runtime-input FILE`. The agent prepares this technical input; users can ask “실행 도구 구성을 확인해줘.” The ordinary doctor/status response stays unchanged when the option is omitted. Status rejects this option.

The file is the existing canonical `{paths, sha256}` runtime object, at most 64 KiB, rather than a whole execution request. The project must have a healthy verified `official-execution-2` binding on macOS before this file is read. Other profiles or incomplete project observations return an unavailable local check. A managed distribution without explicit diagnostic support uses ordinary doctor and reports that the extra check is unavailable.

Only the opt-in response adds `official_runtime_input`: `profile`, `local_check` (`passed`, `failed`, `unavailable`), fixed `reason`, `message`, `next_action`, `environment_scope`, and `account_connection`/`model_connection` (both `unobserved`). These are one-command observations, not stored records or grants. The top-level classification and exit code still describe the workspace; exit 0 alone does not indicate successful local input checks or permission to execute.

The check reads explicitly supplied pinned files, hashes their complete bytes using the existing per-file bounds, and reports the first refusal. It does not read the known default authentication/installation-ID contents, launch the CLI, connect to a model, change configuration, repair the project, or update pins. Environment checks cover this command's process; the manager retains its existing filtered child environment. A direct invocation with CODEX_HOME set refuses before opening the input. The manager filters that variable, so this check cannot identify arbitrary nondefault credential locations; supply the intended runtime object and pinned documents only. A matching local check leaves current Work, limits, execution preview and connection admission to their existing procedures. Confirm the original input and file changes before resolving drift; replacing a digest does not qualify a new CLI/helper combination.

## Single-Home Paths And Outcomes

`.hrn/format.json` identifies the format and authority. `.hrn/intents/` and `.hrn/work/` contain project-owned truth.
`.hrn/product/` and the root `colvia` are removable runtime material. `.hrn/detached.json` preserves the removal plan and receipt.
`.hrn/staging/` and `.hrn/locks/` are scratch, never selectors. Names, timestamps and path recency cannot choose authority.

| Exit | Meaning |
| ---: | --- |
| 0 | Successful command, including preview, initialized/updated/rolled-back/replayed, or completed detach. It is not admission or write authorization. |
| 10 / 11 / 12 / 13 | degraded / incompatible / conflict / stale |
| 14 / 15 / 16 | partial / uninitialized / unsupported runtime or topology classification |
| 65 | Contract failure; preserve state and inspect the named boundary. Argument-parser usage errors may instead exit 2. |
| 70 | Unexpected internal failure; preserve source, input, and state for investigation. |
| 75 | Bounded test crash injection; not a normal user operation. |

Status/doctor validates records and product identity, not fresh unsubmitted content or real-project adoption. A `detached` result is
readable retained history with mutation refused. Ordinary project edits are not prevented by these diagnostics or logical actor names.

## Single-Home Error Reference

These codes report the violated boundary. Do not repair them by deleting authority, selecting a newer filename, or changing a record hash.
If the launcher is unavailable, inspect from an independent trusted source. Runtime failures are not downgraded to successful observations.

| Codes | Meaning and next action |
| --- | --- |
| `HV2-WORKSPACE-TARGET`, `HV2-WORKSPACE-UNAVAILABLE` | Unsupported target topology, unsafe path, or unavailable observation. Confirm the intended primary/non-Git control root and preserve inaccessible bytes. |
| `HV2-WORKSPACE-RUNTIME` | Use final, GIL-enabled CPython 3.14.6/3.14.7, or the exact managed macOS 3.14.10 tree with isolated entry. Preserve damaged bytes and follow managed recovery when applicable; read-only diagnostics remain available. |
| `HV2-WORKSPACE-CONTRACT`, `HV2-WORKSPACE-VERSION`, `HV2-WORKSPACE-UNKNOWN` | Invalid root/prefix, unsupported format, or unknown authoritative member. Preserve the folder and inspect the exact format; do not initialize over it. |
| `HV2-WORKSPACE-INVENTORY`, `HV2-WORKSPACE-RELEASE`, `HV2-WORKSPACE-PRODUCT`, `HV2-WORKSPACE-LAUNCHER` | Product inventory, binding, loaded release, or launcher cannot be verified. Use matching trusted source and read-only diagnostics; exact active repair is only for its supported damage boundary. |
| `HV2-WORKSPACE-PLAN`, `HV2-WORKSPACE-RECEIPT`, `HV2-WORKSPACE-TRUTH` | Lifecycle plan, publication chain, or preserved truth contradicts the requested operation. Preserve all records and original input; recover only the exact valid pending prefix. |
| `HV2-WORKSPACE-INIT`, `HV2-WORKSPACE-INIT-INPUT`, `HV2-WORKSPACE-INIT-OPTION` | Init preconditions, exact preview request/token, or option combination is invalid. Re-preview only a fresh supported target; use exact source recovery for a known owned prefix. |
| `HV2-WORKSPACE-SWITCH-INPUT`, `HV2-WORKSPACE-SWITCH-OPTION` | Update/rollback input or target differs from its bound plan. Preserve pending publication; do not substitute another operation's input. |
| `HV2-WORKSPACE-REPAIR`, `HV2-WORKSPACE-REPAIR-INPUT` | Exact source, external backup, restoration plan, or token is unsuitable. Preserve backup and target, then use the exact supported repair/recovery procedure. |
| `HV2-WORKSPACE-DETACH`, `HV2-WORKSPACE-DETACH-INPUT` | Removal plan/token, managed membership, or remaining deletion prefix cannot be verified. Preserve remaining files and use independent-source exact recovery; no recursive cleanup. |
| `HV2-WORKSPACE-CLI-INPUT`, `HV2-WORKSPACE-COMMAND` | Machine fields or command do not match the chosen entry; source lifecycle profile and probe boundaries are also checked. Consult this release's help and exact input. |
| `HV2-WORK-CONTENT` | Content, Git evidence, scope, or ignore policy is unsafe, unavailable, or stale. Re-observe the actual control result and resolve drift before requesting acceptance. |
| `HV2-WORK-UNAVAILABLE`, `HV2-INTENT-UNAVAILABLE` | The corresponding record reader was denied filesystem read access. Preserve bytes and restore authorized read access; this does not establish malformed records or authorize repair. Other graph and I/O failures retain their existing diagnostics. |
| `HV2-WORK-RECORD`, `HV2-INTENT-RECORD` | Typed graph, exact reference, authority, expected current selection, or publication prerequisite does not match. Preserve records; do not hand-edit selectors to make them current. |
| `HV2-INTENT-FACETS`, `HV2-INTENT-FACET`, `HV2-INTENT-FACET-OWNER`, `HV2-INTENT-FACET-STATUS`, `HV2-INTENT-FACET-VALUE`, `HV2-INTENT-VACUOUS-ACCEPTANCE` | Required facet shape/owner is invalid or all facets remain unknown/deferred. Correct a draft and obtain a new exact human acceptance. Unresolved material gaps also prevent acceptance. |
| `HV2-JSON-BOM`, `HV2-JSON-CR`, `HV2-JSON-DUPLICATE-KEY`, `HV2-JSON-EMISSION`, `HV2-JSON-EOF`, `HV2-JSON-LIMIT`, `HV2-JSON-NONCANONICAL`, `HV2-JSON-NONFINITE`, `HV2-JSON-SYNTAX`, `HV2-JSON-UTF8` | Input is not permitted canonical JSON or cannot be emitted safely. Correct proposed input; preserve malformed persisted bytes for investigation. |
| `HV2-PARENT-TYPE`, `HV2-IMMUTABLE-EXISTS` | A parent is not a safe directory, or an immutable destination already exists (including a concurrent publication). Preserve bytes, stop conflicting writers, and inspect exact state before retrying the original operation. Do not delete the destination merely to make a retry succeed. |
| `HV2-INTERNAL` | Unexpected internal failure. Preserve the source version, exact non-secret input, diagnostic output, and target state for investigation. Do not treat this as successful recovery. |
| `HV2-LOCK-ANCHOR` | Writer lock anchor is linked, replaced, or wrong-type. Stop concurrent mutation and investigate the local guard; lock bytes are not authority. |

For update/rollback/detach, `HV2-JSON-LIMIT` with
`prospective-output:plan:`, `prospective-output:binding:` or
`prospective-output:receipt:` identifies output refused before lifecycle publication.
A preview with this error issues no confirmation token. Apply preserves project truth
and existing product files; normal lock-anchor creation is still possible. This is a
capacity refusal, not evidence of a newly damaged stored record. An existing oversized
record can still produce the reader's ordinary limit error: preserve it rather than
editing or deleting it. The preflight does not expand the 4 MiB limit or provide a
recovery path for previously oversized receipts.

## Source Utilities

`classify-intent-entry --consequence consequential|non-consequential [--input FILE]` classifies provided gaps without publishing records. An input file has exactly one `gaps` field. `durability-probe --root PATH` writes disposable diagnostic files to an explicitly chosen scratch directory; it refuses a workspace root or descendant. It is not a read-only status command.

Generation commands and `--legacy-baseline` are removed. A source init/update/rollback/detach call without `--profile continuation-1` fails instead of selecting an old profile. Installed commands select their bound profile. Source help and installed help deliberately expose different operations.

### Checkout Compatibility Limits

Current source updates only the exact admitted delegation-1 predecessor or a continuation-1 target. The first durable schema-5 switch receipt commits to forward recovery; rollback to delegation-1 or earlier is refused. Use the exact new source and original request/token for an admitted prefix. Existing worker results need separately authorized control Git integration, explicit same-intent worker rebind and resubmission. See [Continuation-1 operation](OPERATIONS.md#continuation-1).

All new lifecycle plans/receipts use paired schema5. Historical action/version pairs retain their meaning; old pending operations need their matching retained source. The older checkout-1 to entry-1 admission and schema2/schema3 recovery remain documented in [Workspace Contract](WORKSPACE-CONTRACT.md#entry-1-admission-and-publication) and [Transition To Entry-1](GETTING-STARTED.md#transition-to-entry-1). Retained source is not a downgrade path after a one-way receipt.

## Single Work handoff and inbox

In an installed project, the agent maps “‘설치 안내 정리’ 작업에서 준비한 변경을 검토용으로 제출하고, 결과가 나오면 이 기기에서 알려줘.” to a preview and a confirmed start. “‘설치 안내 정리’에 질문이나 결과가 있어?” opens that Work’s inbox. A project can have one outstanding handoff for an active ordinary local Work. Choose a future deadline no more than 24 hours from the request.

The commands below are arguments to the installed project launcher. On macOS run `./colvia` in the project directory. For Windows use the [Windows launcher invocation](#windows-2-command-and-failure-boundary).

| Action | Launcher arguments |
| --- | --- |
| Preview the action, scope, deadline and destination | `handoff prepare --input REQUEST` |
| Start after explicit confirmation | `handoff start TOKEN --input PLAN`. Use the preview’s `confirm_token` and its exact `plan` object. Submitting the same plan and token again returns its receipt. |
| Read questions and results | `view inbox` for the project or `view inbox WORK_ID` for one Work. Use `handoff show TOKEN` for a specific receipt. |
| Answer the current question or request a stop | `handoff answer TOKEN --question QUESTION_ID` with the receipt’s current `question_id`, or `handoff stop TOKEN`. Act on the user’s choice: continue maps to `answer` and stop to `stop`. After a stop request, check the recorded effect. |
| Reconcile an interruption | `handoff inspect TOKEN`. When the deadline has passed, the worker is inactive and the effect is still uncertain, the user may explicitly choose `handoff close-unknown TOKEN --confirm CLOSE_TOKEN` with the latest `close_token`. The spent step and receipt remain in the inbox. |

`summary` and `submit` (an already prepared result) were exercised in isolated projects on macOS and under a standard account on a designated Windows 11 ARM64 VM, including question/answer and interruption handling. With notifications enabled, the worker attempts a generic device alert after recording a question or step outcome. Check the inbox directly after expiry or an interrupted worker. OS notification calls succeeded in tests. Actual banner display and user reads remain unobserved. The optional `execute` action requires its own approved document execution on macOS `official-execution-2`; the live model path through this handoff remains unverified. User installations and adopter use remain unverified.

## Human Review

`./colvia view` shows the recorded Work overview. Use `./colvia view --details` for verified manual/adapter paths, the Intent list and raw record fields. Use `view intent ID [--revision ID]`, `view work ID [--revision ID]`, or `view confirmation --input FILE|-`. Independent source: `colvia --source-checkout view --target PATH ...`. These commands write GFM to stdout without publishing files, locks, on-disk caches or decisions. Imported view errors are GFM with a nonzero exit; bootstrap failures remain JSON/65. Status/doctor and machine commands remain JSON. The additive v2 status metadata below preserves every existing field and its meaning; consumers must not interpret extra observation fields as execution authority.

The default project view shows recorded progress, each Work's short goal label and actual ID, its state and recorded follow-up, then project-local candidates and a help entry. Known counts and unavailable counts remain distinct. Labels come from the exact intent bound to the selected Work revision, not a newer accepted goal; historical goals, scope fallbacks and unavailable labels are marked. This is a display label, not a stored Work title. Work state describes recorded progress. The project path identifies the actual worktree; no extra Git query is made for labels.

Each Work row proposes the next check or decision from its current derived state. An explicit current `view work ID` puts that summary and recorded scope/observations ahead of technical details, reusing its existing file observation. A historical `--revision` query keeps its historical meaning. The project overview compares records only and directs current-file comparison to the Work detail. Non-normal project entry takes priority over a Work decision; isolated candidate observation errors take priority over acceptance guidance. The CLI uses structured records and fixed wording; the agent explains any interpretation separately. Stored `next_action` remains historical context.

In the official v2 window, execution cards are separate historical records, sorted by grant ID rather than time. The existing verified status observation supplies an allowlisted `work_id`, `process_observation`, `effect_refs` and `closure_refs`; it does not expose grant scope, payload or recovery locations. The process observation distinguishes `closed`, `unconfirmed`, `not_started` and `not_requested` using the full reducer and start records, not a partial closure reference. Matching target/Work ID does not bind a run to the current revision or approval. Pending runs prompt evidence inspection before recovery/new execution; resolved historical unknown effects do not change existing lifecycle readiness. In particular, `operator-resolved-unknown` is a terminal state; the terminal event status `unknown` remains unresolved even when all recorded processes are closed. The View preserves this existing distinction. Detail shows journal sequence references and the missing revision linkage. v1 records retain their existing semantics without an invented v2 effect. No new OS scan or external recovery lookup is performed.

Use `./colvia help` for query commands and two natural-language patterns. The quoted alias `./colvia '?'` is also accepted; quote the question mark to prevent shell expansion. Help is static and reads no project state; installed launcher integrity checks still apply. Use `./colvia view --details` for normal raw status, Intent IDs, full Work fields and copyable per-record commands. Combine `--details` only with the default project view, never a selector, `--revision` or `--input`; invalid combinations are rejected before input is read. Existing detailed selectors and exit codes remain unchanged.

Raw details are automatically retained when the observation does not explicitly pass the normal-state checks, including unavailable runtime/planning, non-authoritative control, incomplete processing or damaged records. Human explanations appear before raw diagnostic fields. Pending decisions, unavailable or exhausted follow-up usage and changed source/target selections remain visible in Work rows. Verified manual and natural-language adapter paths appear at the start of technical details: on an explicit `--details` request or when non-normal state automatically expands diagnostics. The concise default points to technical details. Release-managed agent procedures start with `view --details`; stable project-owned entry text should start with `view` and follow its guidance, so rollback to a release without `--details` keeps its original entry command. Never retain a release-specific path as the current entry. Source-mode queries identify their independent source. The summary neither selects a task nor promotes stored next actions or follow-up choices into execution authority. Agent recommendations follow the current human request and valid project narrative. Help examples and static display checks do not prove model routing or general usability. Installed POSIX examples use `./colvia` and state the project-directory precondition. Exact commands in technical details retain full paths. Independent-source commands retain `--source-checkout` and `--target`; Windows commands retain the absolute allowed Python path and `-I -B`.

Confirmation consumes canonical ticket bytes, not the prepare response envelope. Observations are advisory and may be unavailable or stale; there is no aggregate permission-to-apply result. Apply checks prerequisites again. A completed record does not prove current project files match. Work comparisons list path/mode/size/digest changes, not historical text bytes; rebind discontinuities are not attributed to the Work.

Document bodies remain project Markdown. The view displays role, path, recorded digest and current observation; open those documents or have your agent explain them. Advisory reads reject links, special/unstable inputs and files over 4 MiB. A Core-readable large file can therefore be unavailable in the view. Worker-observed evidence is not reverified on control.

The continuation-1 runtime rejects serial-1 and unknown windows. Independent-source reading retains valid human-1, worker-1, umbrella-1, planning-1, checkout-1, entry-1 and delegation-1 history; current candidate creation and execution require continuation-1. The installed launcher refuses old bindings before loading managed code. Old source profiles are parser errors. Transition uses the qualified independent new source; see [Continuation-1 operation](OPERATIONS.md#continuation-1).

Command syntax/argument errors retain argparse stderr and exit2; the GFM error contract begins after argument parsing. The default human view omits the managed file inventory; status/doctor retain machine diagnostics.


Paths and digests use dynamically delimited GFM code spans; ordinary punctuation stays readable in raw stdout. Control characters are visible escapes and literal backslashes are distinguished. The view summarizes status before details and separates intent documents from Work revision documents. Revision progress/next_action are recorded historical fields, not the current derived Work state. Selected history follows the parent chain and includes the human action, actor and reason; the separate decision list is not chronological.

Confirmation advisory checks include required ticket references and, for Work accept/rebind, required bound intent references. The bounded reader may be stricter than Core, so an unavailable observation is not proof of a Core refusal. Worker-observed evidence is not reverified on control. Reject/revoke do not require live reference agreement. Worker accept cancellation still requires all changed paths pre and no durable result selection. There is no aggregate readiness grant. View-internal type/attribute/index failures return GFM with exit70; argument errors remain argparse/2 and pre-import launcher errors remain JSON/65.

The bounded reader requires searchable and listable physical ancestors from `/`, exact spelling, no symlink ancestor, and a regular single-link file. A macOS `/tmp` or `/var` alias can therefore be refused: use the real physical path to an authorized ticket or canonical stdin. Do not weaken the Core or remove files to bypass an unavailable observation.

Later patches, prereleases and free-threaded builds are rejected. Other OS or distributor builds can pass the version check and execute even when they have not been qualified. See [Security and Support](SECURITY-AND-SUPPORT.md).

In status, `supported_baseline` retains the historical first qualified version; it is not a minimum version. `supported_versions` is the exhaustive patch allowlist.

In status, `runtime.supported` reports the version check. Even with `classification: pass`, qualification of the OS/build and actual adopter use must be established separately.


For result acceptance, pair `./colvia view work ID --revision REVISION_ID` with `./colvia view confirmation --input FILE` (or `-`) for the same selected revision. Work details contain `observed_scope` and `unavailable_scope`; the confirmation view does not directly repeat these arrays. Explain all unavailable items against the human's declared acceptance criteria before applying the exact ticket. Nonempty observation text alone does not make a graph degraded, and an empty list does not prove verification. Required-reference and live-content refusals remain mandatory. See [General Work](GENERAL-WORK.md#observation-limits-and-human-acceptance) and the current managed adapter.

The author-declared `unavailable_scope`, an advisory reference observation labeled unavailable, and a `*-UNAVAILABLE` authority-read error are different. The last remains a degraded/write-refusal condition; neither observation prose nor an advisory display waives it.


Worker Work/confirmation views distinguish control baseline from retained candidate and partial application. Changed Work references display candidate and live-control observations separately. Human baseline refresh compares old baseline/candidate with the proposed baseline and labels content matches without attributing their cause. These read-only observations do not authorize an action or replace guarded validation. See [Worker Review Observations](GENERAL-WORK.md#worker-review-observations).

A healthy observation shares its verified graphs between status and rendering. Within its Work sweep, repeated intent references share a verified intent graph while every exact historical binding is still checked. A final independent intent collection read must match every shared graph; changes or failures discard the shared result and use the existing fresh, unshared status path. Partial, pending and unsupported graph results also use the unshared path. Work records and independently loaded intent graphs retain double reads. Before and after view observations, retries and separate commands never share this temporary state. All Works, relations and umbrella histories remain checked; writers and current/live-reference checks keep fresh reads. Changes restored between checks are not guaranteed to be detected. Stable inputs retain the same output and exit status. Concurrent changes may cause a retry and a degraded or unstable result instead of an immediate unavailable result; this is not an atomic snapshot or permission to apply.

### User-facing Communication

Colvia owns these defaults for View, help/manual text and agent explanations. Optional writing tools can refine the wording. Apply the principles to the reader's task; they are not a required response template.

- Lead with the answer, current situation or result the human needs, then the evidence and next useful action. Explain relationships in the order the reader needs them; give complex roles or sequences a short example or diagram when that helps.
- Name concrete objects and actions. Use the actual project/worktree path, Work ID and relevant revision rather than an abstract role description. Explain unfamiliar terms where needed and preserve exact identifiers, commands and links. Present a short, evidence-based task description first and its exact Work ID in parentheses. In View, goal excerpts come from the selected Work revision’s exact accepted intent binding, with older goals labelled as such; a recorded scope or an unavailable-title label is the fallback. These display labels are not stored Work titles or approval identities. Never invent a title from unreadable records or substitute a newer goal for the bound one.
- State facts, scope and requirements directly. Replace routine “does not mean/prove” disclaimers and internal review commentary with the useful explanation. Keep an explicit negative when it clearly prevents a concrete misunderstanding, unauthorized action or harm; preserve the material condition where it matters.
- Keep meaning and authority intact. Distinguish recorded results, current facts, proposals and unavailable information. Preserve conditions, uncertainty, exceptions and who decides; add no unsupported capability, actor, causal claim or extra procedure to make prose smoother.
- Match detail to the audience and request. Give one concise natural-language request pattern before technical detail, with exact commands and diagnostic fields as supporting detail. Avoid repeating the same example for every task; let the human use its displayed description or ID. Keep clear existing wording; remove repeated explanations and unnecessary scaffolding. Ask only for missing facts that change the answer or action. When a recommendation depends on missing information, ask one focused decision question rather than leaving the human to infer what to supply. Keep all material conditions, unavailable items and exact approval targets visible; limiting questions does not omit those facts. Explain the user-relevant issue and next lookup request before raw diagnostic fields.
- Name what each check actually examined and what passed; distinguish a file read from an executed check and keep untested targets explicit.
- After reporting, continue authorized remaining work. When a decision is needed, state the smallest choice, recommendation and reason. If comparison or investigation is already authorized and its inputs are available, carry it out instead of merely suggesting that the human do it. Honor report-only requests and explicit stops; finish completed requests without inventing follow-up work. Use [Continue After A Progress Report](../adapters/colvia-work/SKILL.md#continue-after-a-progress-report) for the action boundaries.

### Observation-Local Topology Reads

A healthy Git primary status observation may share only the raw topology probe within its first Work sweep. Target, ancestor,
resolved-path and effective ignore checks still run on each read. After any raw reuse, a final fresh topology probe must match
before the independent final intent read and graph comparison. Failure discards the context and uses the existing fresh fallback.
The context is not passed to writers or retained across requests or view observations, and creates no disk cache or lock.
Persistent topology changes may therefore be detected more strictly than an entry-only status label. Intermediate Git failures
or topology changes that revert between the first and final probes are not guaranteed to be observed. These reads are not an atomic
snapshot or a performance guarantee.


## Candidate Planning

Candidate planning records ideas before they become execution work. Ask the agent naturally; the installed adapter prepares machine input. `./colvia view candidates` is read-only and shows the recorded choice, reasons, conditions and actual linked Work state. The root `./colvia view` includes a reader-facing summary; `view candidates` retains full fields, digests and limits. A recommendation writes nothing; selection is not intent acceptance or execution approval.

Only an explicitly installed continuation-1 runtime writes candidates. `./colvia candidate ACTION --input FILE` (or `-` for stdin) accepts one canonical JSON object. Source mode has no candidate writer. Supported actions are `add`, `amend`, `select`, `defer`, `resume`, `link`, `disposition`, `reopen`. Success returns `saved` or exact-retry `unchanged`, the resulting store and digest. Before writing, tell the human any outstanding lifecycle preview will need preparation again.

The request has exactly these fields: `record_type: "candidate-request"`, integer `schema_version: 1`, `authority_home_id`, unique `request_id`, `candidate_id`, `action`, `expected_sha256` (null only for the first absent store), `writer`, `owner_statement`, `reason`, `observed_at`, and `payload`. IDs use the existing 1–96-character ASCII ID grammar; request IDs and candidate IDs reject case aliases. Narrative fields are nonempty strings up to 2,000 characters, except an unspecified resume condition may be empty. Writer and short Owner statement are declarations, not authentication; never save secrets or the full conversation.

| Action | Exact payload | Effect |
| --- | --- | --- |
| `add`, `amend` | `title`, `purpose`, `expected_effect`, `related_candidates` (existing distinct candidate IDs) | Add an open candidate or correct its narrative, preserving history. |
| `select` | `{}` | Select one open candidate; replace the prior choice with a recorded reason. |
| `defer` | `resume_condition` | Open → deferred; clear this choice if selected. |
| `resume` | `condition_observation` | Named deferred → open; never selects it or replaces another choice. |
| `link` | `target` | Record an exact current intent/Work revision in this home. |
| `disposition` | `disposition: "absorbed"` with `target`, or `"rejected"` with null target | Open/deferred → terminal; clear this selection. |
| `reopen` | `{}` | Rejected without a Work link → open, with a new reason. |

A target contains exactly `authority_home_id`, `kind` (`intent` or `work`), `id`, and `revision_ref: {id, sha256}`. It must resolve to the current selected/accepted revision at write time. A Work link must agree with any linked intent. Links cannot replace a different object; use a successor candidate. A Work-linked candidate cannot select/defer/resume/reopen; use the Work's own decision flow. Later historical links remain labelled rather than silently updated. A linked Work consumes the next-choice display; completion is read from Work, not copied into planning. If only the intent link was saved but a Work revision already uses that intent, the view lists those Works and reports an incomplete candidate link; verify scope/current revision and retry the link, without creating the Work again. This lookup never writes a link. `status.planning.selected` is only the recorded planning choice, not Work readiness. A deferred record linked to Work retains its historical disposition but no longer displays a candidate resume condition. Absorbed candidates cannot reopen: correct a mistaken absorption with an explicitly authorized successor candidate referencing the old candidate, preserving the original history.

The store is `.hrn/planning/candidates.json`, with `record_type: "candidate-planning"`, `schema_version: 1`, `authority_home_id`, derived `candidates`, at most one `selected` ID, and `decisions`. Each decision appends the exact request and before/after disposition/selection. Do not edit it directly. Required intent/Work inputs and results cannot point into `.hrn/`; planning is excluded by the existing content snapshot boundary. A planning-only commit is an external Git operation requiring its own authority.

The writer shares the control guard, validates the expected prior digest, then replaces the whole file atomically from `.hrn/staging/`. A crash leaves old or complete new planning; preserve the exact request, read, and retry it. Temporary `candidate-*` files can remain after interruption or a refusal before replacement; they are non-authoritative scratch, not a queue, and are not automatically cleaned. They do not prevent lifecycle preview/detach. A pending refusal means this call made no new write; an earlier interrupted call may already have published the same request. The same request ID with different bytes is refused. Ordinary editing or submitted-review allows candidate writing; pending Work/intent transactions or lifecycle recovery refuse it until the original exact operation is recovered. Candidate notes do not waive content/required-reference drift checks.

Limits are 100 candidates, 1,000 decisions and 1 MiB, whichever is reached first. At 80% the view warns; a write exceeding a limit is not saved. History is not pruned automatically. `HV2-CANDIDATE-STALE` means read before preparing a new request; `HV2-CANDIDATE-PENDING` means recover the original transaction; `HV2-CANDIDATE-WINDOW` means explicit update is needed. `HV2-CANDIDATE-RECORD`, `-UNAVAILABLE` and `-LIMIT` mean preserve bytes and inspect the stated issue. Refused requests are not saved in a hidden queue.

Candidate records are tracked branch-local planning. Commit/clone can carry them; no central ranking or cross-project graph exists. Preserve both branch refs/unique bytes before resolving a conflict. After Owner decision, restore one verified complete history and explicitly re-record needed decisions from the other branch as new requests. Restore from a known complete Git ref or preserved complete bytes; never manually stitch decision arrays or overwrite another history automatically. The reader checks transition history and the derived projection, but does not recompute every historical `expected_sha256` against its prefix. Those digests declare the writer-time CAS input, not a cryptographically verified chain: a manually stitched, internally consistent history may pass. This is not tamper authentication. Missing/unreadable/conflicted data must not be described as an empty list.

A candidate-only read error makes active `status`/`view` partial, with planning unavailable rather than empty; independently valid Work/intent graphs remain readable. Candidate writes and lifecycle operations still refuse invalid planning. The bounded no-follow reader checks exact spelling by listing each ancestor directory, like the existing view reference reader; an ancestor that permits traversal but forbids listing can make candidate observation unavailable. Preserve bytes and use a trusted readable path; do not weaken path checks.


## Project Document Assistance

Load this section when the human requests a comparison, decision record or unresolved-question note. It is an optional agent authoring procedure; Core does not generate these documents. Project rules own document locations, identifiers, indexes and lifecycle; use [Document Language](#document-language) for language selection. Read the project README and directly relevant existing narrative first, not every archive or a previous workflow's templates.

### Document Language

Before composing a saved plan, Work narrative, brief, decision or other document, establish its audience and purpose from the request and applicable project rules. Use an explicit language requested for that artifact first, then the project's language default, then the conversation language. Do not ask again when these already settle the choice. If a request conflicts with a mandatory distribution, contractual or legal language requirement, expose the conflict and obtain the human's decision before the affected write; do not silently override it.

Conversation explanations still use the human's conversation language. An English template, example, identifier or diagnostic label does not select the language of a saved artifact. Preserve exact commands, identifiers, quoted evidence, numbers and technical meaning. Follow the project's existing paired-language requirements when applicable; do not create translations or new language fields merely to use this guidance.

### Choose The Smallest Record

| Request | Response |
| --- | --- |
| Compare alternatives or explain a direction | Reuse an existing brief/plan section. State the question, meaningful alternatives, evidence and limits, tradeoffs, recommendation and open decisions. A recommendation is not the Owner's choice. |
| Record an actual human decision | Use the project's DR convention. Record the question, actual decision and authority/date, reason, consequences, reversal cost and affected scope. Cite the decision the human actually made. |
| Still undecided | Keep a Draft DR only if the project uses one; otherwise use existing Open Points. Record the question, why it matters, missing evidence/decision and condition for resolution. Do not invent Accepted status or a deadline. |
| Save a task or execution idea | Follow [Candidate Planning](#candidate-planning) and the adapter's Candidate Conversation. A document request does not implicitly authorize a candidate write. |
| “Save this” or “later” with no clear object | Ask one concise question before writing. Preserve the request in conversation while clarifying. |

Prefer a section in an existing suitable document. Create a standalone document when requested or required by the project's convention; if no convention exists, propose a descriptive filename and location. Do not impose `docs/decisions`, a global DR number, a new Work file, a STATUS document or an index that the project does not use. Update only existing relevant indexes/links within authorized scope. Respect an external canonical tracker instead of creating a local duplicate.

Keep claims proportional to the available evidence. Where the record relies on them, distinguish supplied facts as stated (including scope, units and uncertainty), measured observations, assumptions and agent recommendations; an assumption label does not make an unsupported conclusion reliable. Describe what a mechanism changes rather than claiming no risk, no delay or no required work without evidence. Add numerical estimates only when they help the requested decision, with the relevant input uncertainty, reproducible calculation and limits; otherwise state the qualitative tradeoff and the observation needed. Do not equate a proxy measure with a user benefit without evidence. Keep the record as short as the decision permits.

An explicit, sufficiently clear request to record the decision authorizes that narrative edit; do not ask the same recording permission again. It does not authorize inventing a policy choice, starting Work, accepting intent/results, Git operations or publication. Ask only about material ambiguity. The word Accepted in a human DR reports that human decision, not a typed Harness acceptance. A Draft records what evidence or choice would permit promotion; age and a reviewer verdict cannot promote it.

### Check Before Writing

1. Run the current `./colvia view --details` at control. Inspect pending operations and the intent/Work objects it lists, then `./colvia view work ID` and `./colvia view intent ID` for relevant scopes, states and references. Root view alone is not a reference-impact audit. Disclose known prepared-but-unapplied tickets: they are not all discoverable in the store and a document edit can stale them; do not claim an object-view search exhausts outstanding tickets. Include every proposed document and index path, including new files. Prioritize unfinished Work, current accepted intents and children captured by unfinished parents. Read the exact `view work ID --revision ID` for bound intent documents in related captured/historical revisions. `view intent --revision` still displays current acceptance documents, not that historical acceptance. Completed history matters for preserving what was accepted then; it is not by itself a live edit prohibition.
2. For every unfinished Work (including rejected/revoked before rework), if a path is outside its scope or the edit would disturb a submitted/rework result, worker control baseline or pending recovery, do not write. Rejection does not finish the Work or permit out-of-scope writing. After reject/revoke, even an in-scope edit before authorized rework publication would break the retained baseline. Explain the proposed content in conversation, explicitly say it is not saved to a project file, and name the operation or authorized scope/baseline change after which it can be recorded. The human can choose to finish/recover the existing operation first or separately authorize a supported intent/scope/baseline change. Never silently expand scope, absorb drift, publish a revision or lower a required flag. During review/pending, project-content handoff stays read-only. An explicitly requested candidate write during submitted-review still follows Candidate Planning; pending intent/Work/lifecycle barriers block its writers. Planning is outside content snapshots but is not an implicit fallback save channel.
3. Trace document/evidence references to each target using object views, including required intent inputs and related captured child/parent references. Explain stale/missing/unavailable observations and the cost of the lookup. Use a temporary, request-local list, not a permanent index/cache. If the affected reference set cannot be established, stop at a read-only proposal rather than claiming the edit is safe.
4. Prefer keeping a referenced predecessor DR byte-for-byte intact. Put an amendment/supersession's exact replaced and still-valid scope in the successor and any relevant existing index; check those paths too. If the human needs an in-place change, distinguish the reference owner before editing. A required intent input can require new exact intent acceptance, human Work rebind, resubmission and new exact result acceptance. For an authorized pre-submission edit to a required Work-revision document, include its new digest in the result submission; that reference alone does not require new intent acceptance or rebind. A checkpoint cannot absorb changed project content. After submission, use the supported mode-specific reject/rework or human baseline-refresh path before editing/resubmitting; local same-intent rebind is not supported. Captured child intent references can affect a parent even after the child completed. Never evade the guard with a copy or a non-required flag.
5. A non-required reference can describe a changed working draft without blocking on that reference alone. It still participates in whole-project content validation: changing it after submission can stale the result. Explain the existing mode-specific rework/baseline-refresh/resubmission path before any authorized edit. Do not rewrite a historically accepted decision as though the revised bytes were accepted then.

When the checks permit the requested write, make the smallest narrative change, preserve unrelated content and check direct links and the project's rendering requirements. Report what was recorded, what remains Draft/open, and which decision or validation is still needed. Project Markdown survives runtime replacement/removal; preserving it is not acceptance of its claims.


## Repository-Owned Rules

Use repository rules for project-specific documentation, validation or domain procedures. Core continues to own typed state, exact acceptance and integrity checks; a repository rule cannot override them. The Product supplies the application guidance below. The project owns the adopted rule, its local choices and the evidence that it was followed. Rules are instructions to agents and maintainers, not a runtime enforcement engine or a new authority record.

### Locate And Describe A Rule

Choose the entry from the task context. In an installed project, use project-owned instructions plus `./colvia view --details` and its verified manual/adapter; managed manual links stay relative to that manual. Only an explicit request to develop Colvia in a trusted source checkout uses source-only `CONTRIBUTING.md` and the workflow it names. Those source procedures are not installed-project rules.

Reuse the project's existing shared instructions or maintainer document. Keep one canonical rule and a short pointer from the relevant agent entry; retain tool-specific instructions where they are needed. No rule directory, manifest, package format, STATUS file or registry is required. Load a rule when its scope or trigger applies, not as a demand to audit every document at session start.

A short section or table should let the next maintainer find:

| Information | What to record |
| --- | --- |
| Purpose and owner | The behavior it governs and the role responsible for maintaining it |
| Origin and local authority | The source rule/section and adopted release or revision, the project canonical location, and any explicit local choice or exception |
| Scope and trigger | Which files, changes or task situations require it |
| Action and check | What the agent/maintainer does and what observation supports completion |
| Update and removal | Where to compare a later source change, which local content must survive, and who decides conflicts or retirement |

Use an existing release/revision reference or a content digest when needed to identify the adopted input. Record that identity and the source section without pinning an installed managed-directory link as the current entry or update source; obtain the current managed path from `./colvia view --details`. A current Harness installation does not prove project rules were updated with it. If origin, applicable version or ownership is unknown, report it as unknown and establish a human-reviewed comparison basis before replacing content. This comparison basis is not a typed Work baseline or a rebind. Do not invent provenance or precedence from a filename.

### Apply To A New Or Existing Project

For a new project, select only the rules needed for its actual work and put them in its chosen instruction/document structure. Explain their purpose and proposed entry pointers within the authorized adoption scope. Do not generate an empty framework of rule files.

For an existing project, inventory only the affected shared entries, tool-specific rules, hooks and related project documents. Compare the proposed rule with their current behavior. Preserve unique instructions, intentional local overrides and useful procedures; expose duplicates and contradictions before changing them. Present the exact project diff and any missing behavior. The human resolves a material policy conflict; an agent must not silently choose whichever rule is newer. Do not delete tool directories merely because their content originated with an older workflow.

Apply an authorized project edit only after [Check Before Writing](#check-before-writing) permits its content/reference impact. Include rule and pointer changes in the appropriate project scope. An adoption request is not permission to alter a pending result, rewrite immutable records, edit the managed payload or bypass a required acceptance. Core init/update/rollback/detach do not write, refresh or remove these project-owned rules.

### Update, Verify And Retire

When a relevant Product or project behavior changes, compare the adopted source, incoming guidance and local rule. Keep local changes visible. If the old basis cannot be recovered, explain the uncertain comparison and prepare an explicit replacement proposal instead of calling it a clean upgrade. After an authorized update, record the new source reference and retained exception in the existing rule/narrative, and check its pointers and the affected behavior. Source guidance is not proof that a particular agent loaded or followed it; report unexecuted tool paths and real-user observations separately.

If a rule is no longer needed, identify the exact section and pointers it owns, preserve still-valid project requirements and required historical/reference bytes, and propose its removal or replacement. An obsolete rule does not authorize deleting its containing directory. Use Git or the project's existing recovery practice to preserve unique changes; do not keep a full source copy or permanent validation archive just to prove that a check ran. A changed or removed rule cannot retrospectively change what an earlier Work accepted.

### Project-Owned Adapter Additions

A local adapter may be a short section in an existing project rule or, when useful, a project-owned document. It tells an agent which applicable rule to read and what to explain. Connect it from the relevant project entry; do not edit or duplicate the installed adapter. For example, a CLI project can ask the agent to read its documentation rule before an authorized option change and explain affected usage examples, executed checks and remaining limits in the existing Work narrative. The project selects the actual paths and checks.

Record the same purpose, owner, source basis and update/removal information as for other repository rules. Follow the current managed adapter and preserve Core authority boundaries. Show conflicts before acting; a local instruction cannot waive acceptance or integrity checks. Verify the entry pointer and report whether a fresh agent session actually read the rule. This pattern describes instructions in project-owned files. Native extension APIs and automatic discovery/installation are outside this pattern; tool-specific packaging needs its own setup and verification.

When retiring Harness, separate installed guidance from these project-owned additions. Exact detach removes the managed manual/adapter with the product, while project entries, rules and user/global tool configuration remain outside its removal surface. Plan the relevant pointer replacements, retain valid local requirements and required reference bytes, and use [Detach](OPERATIONS.md#detach) for the runtime operation and post-detach entry check. An unexpected missing launcher remains an installation problem until the documented checks establish detached state.

### First Example: Documentation Currentness

A project may adopt this rule in its existing instructions:

> When changing an API, configuration, architecture or operating procedure, identify its canonical documentation and affected pages during planning. Update the necessary pages within the authorized scope and run the checks warranted by that change. If no update is needed, state the reason. If an update must wait, name the responsible follow-up and its resume condition. Record it in the existing Work or project tracker only when authorized and [Check Before Writing](#check-before-writing) permits; otherwise report it in conversation as unsaved and state when it can be recorded. Candidate records still require an explicit planning request. Do not report the documentation as current while that gap remains.

Map actual change types to actual project documents; do not copy a technology-specific mapping into an unrelated project. For a project adopting this rule, use its canonical page and index pointers at result review, handoff and closeout to explain the affected pages, checks and remaining gaps alongside the code/configuration result. Record the accepted result and deferred document updates in the existing narrative only as the rule above permits; otherwise report them in conversation as unsaved. The common [plan and follow-up flow](CONCEPTS.md#following-a-result) still applies independently of this optional rule. Reuse applicable execution evidence and run only the missing checks. Rendering and link checks cover document structure. Meaning and reader understanding require separate assessment. Paired language versions must preserve behavior, conditions and limits; record any unresolved mismatch rather than treating the older translation as current.

This first example applies the guidance through a project rule. It provides no universal extension API. If a proposed rule needs the runtime to enforce a common invariant, identify that requirement for a separate Core change; written instructions alone cannot enforce it.

## Records And Retention

Use one project narrative for the human explanation and the existing typed stores for machine authority. These agent operating rules set the default amount of additional material; they add no record type, retention registry, automatic cleanup or permission to write. Project obligations and the exact publication, acceptance and recovery contracts still apply.

### Default Record

Reuse the current Work or a suitable section of an existing project document. Create one narrative only when none fits; do not require separate plan, review, result, handoff and closeout files. Record the purpose and scope, actual result and checks, material limits, and actual decisions or next action in the shortest useful form. These are facts to cover, not mandatory headings or a new schema. Update an authorized in-scope narrative before submission; follow [Check Before Writing](#check-before-writing) when content is already submitted, accepted, referenced or pending.

A normal verification note identifies the command or selected checks, input revision or diff identity, relevant runtime/environment, exit status and applicable counts, skips, failures and limits. Distinguish execution on this candidate, inherited evidence and unverified work. It need not duplicate successful tool output, every file hash or the full project manifest. Whole-content validation checks for unintended changes; its entry count is not the number of new files or source copies.

When an independent review is requested or required, use the same narrative. Identify the question, supplied input and any excerpts, reviewer model/session and execution boundary where known, then retain the final reviewer response verbatim, Driver disposition and actual Owner decisions separately. If the narrative cannot currently be edited under Check Before Writing, preserve the verbatim response in existing durable task storage outside the project content, identify the next authorized narrative update or Owner decision as its consumer, and report that it is not recorded in project files; do not substitute a summary or bypass the write restriction. A source revision plus reviewed diff digest identifies tracked input; identify supplied untracked or external input separately. Report unknown identity and shared-context limits. Tool-call transcripts and API envelopes are not default records. A digest detects change but does not restore input bytes; disclose when an old uncommitted input cannot be recovered instead of creating frozen copies for every round.

### Additional Material Needs A Consumer

Before retaining extra raw output or copies, name the consumer, purpose and end condition in the same narrative, usually in one sentence. The condition concerns the actual dependency, not a fixed number of days or a generic “done.” Retention and Git tracking are separate decisions.

| Material | Retain it for | End or cleanup boundary |
| --- | --- | --- |
| Authority, referenced bytes and exact Git sources | Typed history, reference validation and supported recovery | Follow their contracts. Do not edit or prune control authority, managed runtime, referenced inputs or retained refs as routine cleanup. A hash alone is not preservation. |
| Prepared caller inputs and tickets | The named publication, exact decision or recovery | Keep unapplied tickets even when the store reports no pending operation. After the decision is applied or explicitly abandoned/superseded, check remaining replay/recovery and planned use before discarding caller-side duplicates. Never discard the authoritative record. |
| Failure inputs and diagnostic output | An unresolved failure or disputed result | Keep the essential original observation and failing inputs until the investigation or explicit risk disposition resolves that dependency. A later pass alone does not resolve it. |
| Qualification or planned verification reuse | The named release, audit or future check | Preserve the exact original evidence that consumer needs, including test selection, source/artifact and runner identities where applicable. An existing narrative can hold that evidence; a separate receipt file is not automatically required. The routine summary alone is not a qualification or reuse anchor. Using a Work narrative as the original receipt requires the complete anchor information and a fixed, recoverable version under [Maintaining](MAINTAINING.md#evidence-reuse-and-selection); a summary missing those inputs cannot support that reuse. |
| Unique deliverables and recovery backups | The recipient, contractual obligation or exact recovery procedure | Preserve required outputs outside disposable checkouts. Lifecycle requests, exact source and repair originals follow [Operations](OPERATIONS.md) and [Workspace Contract](WORKSPACE-CONTRACT.md); a completed operation alone does not end their replay/recovery dependency. |
| Reproducible execution copies, renders and temporary logs | The current check or review | Once required results are recorded and no unresolved failure, delivery or reuse needs the bytes, remove disposable material within existing authority. Do not retain a full source tree just to show that a check ran. |

Unknown ownership, dependencies or unique content means retain and explain the missing check. This is not permission to delete historical material, unknown staging debris or a pending operation's prerequisites. Evidence that was required by an earlier contract keeps that meaning; a new default does not retroactively authorize its deletion.

### Approval And Closeout

Keep the user's discussion about changed files, useful results, material limits and the next actual decision. Link the existing record for details. Make the exact action, target revision and supporting confirmation available before acceptance; do not make the user reconstruct them from a JSON dump. Put aggregate tree counts and long hashes in supporting detail unless they explain a mismatch. Do not repeat an identical approval when action, target, input identity and prerequisites are unchanged. Multiple named actions may be presented together, but each exact target and its applicable approval must be clear; no future result is accepted in advance. New tickets, rebind/reject/revoke/cancel, lifecycle operations, Git publication and deletion retain their own authorization contracts.

Distinguish result acceptance, Git integration/publication and cleanup by their actual outcomes. Acceptance does not imply a merge, and a merge does not by itself authorize deletion. The agent checks cleanup at completion or abandonment under the host's policy instead of accumulating idle checkouts. [Git Integration And Candidate Reuse](GENERAL-WORK.md#git-integration-and-candidate-reuse) governs preservation of candidate commits and exact ref names independently of worker branches.

Before retiring a checkout, verify its task ownership, absence of active processes, reviews or follow-ups, and no pending publication, decision or lifecycle recovery depending on it; preserve unique commits, staged/unstaged changes, untracked files and required ignored outputs recoverably outside it. Honor required Owner acceptance. Exclude primary, pinned, shared and in-use checkouts. Use an explicit authorization or a standing project policy covering that target and operation, the host's recoverable archive or normal Git removal, and no force/bulk-prune shortcut. Before any accompanying branch deletion, check every current and historical manifest for its exact retention ref; if referenced, keep the branch even when the checkout can retire. A worker copy of authority is not the control authority: account for any unique bytes before retiring that eligible checkout. Retain a concrete near-term reuse checkout; otherwise clean up when these conditions hold. In the existing completion report, say what was retired or give the remaining use, responsible role and release condition. Do not create a second cleanup ledger, status file or background schedule.

## Session Handoff And Resume

Load this section for a pause, session summary or fresh resume. Start with `./colvia view --details`, current accepted intent, selected Work and its referenced project narrative. Resolve multiple plausible targets before acting. Read the current adapter path again; a saved release path or yesterday's next action is not current authority.

- For “stop here”, report the target and selected state, actual changes, remaining checks/limits, pending recovery if any, and the next concrete action with existing document links. Session end is not completion, rejection, revocation or a Git commit. Do not publish a typed checkpoint/revision or create a handoff file merely to save this summary.
- Reuse an existing in-scope narrative for an authorized progress update only when the [document checks](#check-before-writing) permit it. Otherwise give the summary in conversation and mark unsaved decisions/notes as not recorded in project files, with the condition for later recording. Review/pending and rejected/revoked before rework use a read-only content summary. Preserve important uncommitted/ignored deliverables through the host's existing preservation procedure; do not move/delete records or use a backup as permission to commit.
- For “continue yesterday's work”, explain pending recovery before ordinary editing. Follow the current selected revision and its references; report missing/stale/unavailable narrative instead of declaring resume complete. If prose says Done and typed state says review, show both. Revision `next_action` is a historical agent field, not the current derived state or authorization. A handoff-only read leaves selection unchanged.
- For a completed Work follow-up, preserve the accepted result/history and propose the new task or the separately authorized supported lifecycle action. Do not silently reopen, overwrite or revoke it. Candidate resume affects only the explicitly named deferred candidate; it never resumes a Work.

Read the source Work's selected continuation as well as active/completed Work, candidate choices and referenced plan. [Work Follow-Up](#work-follow-up) distinguishes proposal, existing Work, explicit none and undecided. If valid candidate and continuation choices conflict, report both and ask which action the human intends; never silently replace either or choose by timestamp. An unchanged authorized action need not be approved again. A recommendation or historical `next_action` is not a stored continuation choice.

After restoring the same task, recover the human request and its approval basis, completed and unfinished work, next concrete action and consumed limits. Compare the current prerequisites needed for that action and continue authorized remaining work after the progress report. Re-supplied system or adapter instructions and historical agent summaries do not by themselves cancel the request, select another task or grant permission. An explicit new human stop, change or approval takes effect within its stated scope. A narrative can locate an approval but does not prove it by itself: reuse requires the available human statement or a verified authority record recognized by the existing project contract for the same action, target and inputs. If that approval fact cannot be established, ask only for it before the dependent action. If several requests remain without an established priority, explain the choices and ask which to pursue before dependent changes. If evidence is unavailable, inspect permitted references for that task and ask only for the missing fact; do not create a new ledger or require the whole project to be explained again.

For the conversation branches, use the verified adapter's [Continue After A Progress Report](../adapters/colvia-work/SKILL.md#continue-after-a-progress-report) and [Resume The Same Task](../adapters/colvia-work/SKILL.md#resume-the-same-task). Once the requested stage is complete, recommend a next decision only when the larger goal needs one; a plan or review never starts implementation by itself. Report-only requests, explicit stops and genuinely completed requests retain their stopping boundaries. Context restoration depends on the evidence actually delivered by the platform and available in the project.

When evaluating the handoff experience, use actual user feedback to assess understanding. A summary and a fresh agent’s reading of it do not show that the human understood. Record the feedback separately; an ordinary pause needs no session registry or extra acceptance step.

## Project Context And Targeted Document Checks

Use existing project context. If it is missing and needed for the request, ask only for unanswered purpose, intended users and success criteria. Project context is broader than the six facets of one intent; do not ask for a technology stack for non-code work. Put an authorized context or Open Points update in an existing README/plan where suitable, after the same document checks. For an open question record the question, why it matters, resolution condition and actual conclusion when known. Closing a narrative question does not resolve a typed material intent gap; those gaps still block intent acceptance. A general project question does not automatically block unrelated Work. Do not make every context document a required intent reference.

For a requested document health check, read the named documents and directly related links/indexes. Report each broken link, stale candidate or disagreement with its evidence, effect and smallest proposed repair. Age alone does not expire a DR. State the bounded coverage and unavailable inputs; semantic consistency is judgment, not a Core proof. Keep the check read-only unless the request already authorizes specific repairs, and apply the document scope/reference checks before each repair. A request to inspect or archive is not permission to bulk move/delete typed history, rewrite referenced decisions, audit every archive or add a cache/status board. Preserve referenced bytes and explain the supported reference transition before proposing a move.

## Entry-1 Diagnostic Context

Interpret the classification together with verified target state, error code/message and derived fields; exit code alone cannot identify these cases.

| Context | Observation / operation result |
| --- | --- |
| Otherwise-valid live entry-1 plus immediate-root NFC/casefold `hv2` occupant | `status`/`doctor`/`view`: conflict/12, verified current binding retained, `lifecycle_ready: false`, `retired_entry_collision: {path: "hv2", observed_names: [...], ownership: "project", preserved: true}`. Names are unique and UTF-8 sorted. Existing partial/damaged/unsupported outcomes retain precedence. |
| Same collision on scoped lifecycle, including exact completed replay | `HV2-WORKSPACE-PRODUCT`/65 before further publication/removal; preserve current product and completed history. It is a present refusal, not retroactive pending/failure. |
| Exact schema-3 detach evidence, binding already removed, collision is the failing condition | Further removal/replay refuses 65. Independent-source diagnostics use existing degraded/10 with the product error and preservation guidance; no active binding is invented. Other detach errors can also be degraded/10. Do not call this cleanly detached. Installed observation is unavailable after launcher removal; paired schema 1/2 history is unchanged. |
| Completed entry transition with independently valid current state, plan-bound truth already changed | After applicable product/prefix/collision and synchronization checks, transient degraded/10 with `transition_content_verification: unavailable`; retain current binding and direct current Work content/ref checks. `historical_operation_result` is an observation, not a new durable record. |
| Truth drift during comparison, content mismatch, invalid product/prefix, collision or required sync failure | Preserve the applicable refusal (including 65); historical comparison unavailability does not swallow it or authorize rollback. A newer current binding is never rewound or synchronized as an older operation's B1. |

`view confirmation` can display a ticket and independent reader checks with conflict/12. Display is not confirmation, readiness or approval; current binding, required-reference, content, selection and pending rules remain mandatory. Never execute or snapshot-exclude an unowned retired occupant. For OLD pending init/repair/detach, preserve the original source/request/token and use matching OLD source; the new source's diagnostic is not a recovery executor. Exact managed O during the admitted transition is governed by its physical table, not the unowned-collision rule.

## Delegation-1 Implementation Candidate

Continuation-1 inherits the delegation-1 behavior described below. Follow [Continuation-1](README.md#continuation-1) for current lifecycle commands and authorization requirements. Historical versions retain their original meaning. Human authorization comes from the Owner’s actual decision; host authentication and general readiness require their own evidence.

The current profile is `continuation-1`. Existing Work command names and ticket fields remain unchanged. New lifecycle requests and their receipts are paired schema 5; ordinary delegated intent drafts use schema 3 as defined in Guided Intent. These two version numbers belong to different record families. `work prepare` with the exact `actor` in its canonical input may prepare an eligible ordinary accept; applying the exact returned ticket performs the existing guarded content operation and records that actor. It creates no additional command or permission.

`view work` exposes the bound `acceptance_delegation` and existing decision actor/history. View output is advisory; the full reader and each writer independently validate the selected and historical graph. Owner absence, unknown required evidence or an invalid grant is not a reason to bypass refusal. Use the normal exact-ticket recovery flow for an interrupted delegated accept, retaining its actor. Record the result and remaining limits in the existing Work narrative.

Source-development result acceptance, contract activation, commit/push/PR, release and adopter changes stay separately authorized. A delegated project Work decision grants none of those actions. A plain retained-file audit that says delegation authorization is not verified cannot be presented as full Core validation.

## Work Follow-Up

`./colvia view continuation WORK_ID` is read-only, available from installed or independent source view. `./colvia view work WORK_ID` includes its continuation. It shows the chosen meaning, selected versus current source/target references, stale or unavailable evidence, pending recovery and used/remaining normal operations out of 256. For a target Work, intent-reference or literal scope-set change means purpose changed; valid progress alone does not. It never follows the target's own continuation recursively.

Only the installed runtime exposes `continuation prepare` and `continuation apply --confirm TOKEN`, accepting canonical JSON by `--input FILE` or stdin. Prepare requires `work_id`, `action`, `actor`, `owner_statement`, `reason`, `request_id`, `observed_at`; optional `choice`, `document_refs`, `supersedes_choice_ref` default to null/empty as appropriate. The UTC time is `YYYY-MM-DDTHH:MM:SSZ`. Actions are `select`, `withdraw`, `cancel-pending`. Select choices are `{"kind":"proposal","goal":"…","scope":"…","next_step":"…","decision_needed":"…"}`, `{"kind":"work","target_work_id":"ID"}` (prepare captures exact references), or `{"kind":"none"}`. Withdrawal/cancellation use null choice; cancellation identifies the exact pending choice by `{id,sha256}` and has no document references.

Prepare returns the exact ticket, confirmation token, current usage and prospective usage. Show `view confirmation --input FILE` for that ticket together with the Work/continuation view; obtain the actual source Owner's authorization. Apply consumes only the ticket and exact token. A delegated ordinary-accept grant does not permit any continuation action. Required document references must still match for normal publication; optional drift is disclosed. The exact shapes, limits and recovery rules are in [General Work](GENERAL-WORK.md#continuation-1-successor-contract).

A durable normal select/withdraw consumes one of 256 slots, including if later cancelled. Reads, prepare, exact retry and cancellation add no normal use. Exhaustion refuses new normal choices but leaves exact recovery/cancellation available; it does not reset history or force a new Work. Damaged/unreadable state reports usage unavailable, never zero.

Valid pending continuation blocks other official writers across the project. Only its exact completion/cancellation and supported exact active repair remain possible. Unknown or malformed continuation blocks every official writer including repair/detach. Preserve original input and state; do not guess current from the newest record. `HV2-CONTINUATION` reports shape, graph, quota, stale or pending refusal; `HV2-CONTINUATION-UNAVAILABLE` reports unreadable continuation evidence. Neither authorizes hand edits or removal.

## Windows-2 Command And Failure Boundary

For windows-2 only, the explicit window/pairs in Structure's Windows Window And Record Pairs and Workspace's Windows Fresh And Same-Window Lifecycle qualify the common continuation-1 profile statement in Source Utilities, the current-source and new-write version statements in Checkout Compatibility Limits, and the candidate/execution window statements in Human Review. Windows-2 source selects windows-2 for init/update/rollback/detach, uses same-window switch6 and detach6, and admits repair6 only against the exact active windows-2 candidate without a new profile option. Current-format planning follows the applied windows-2 binding. Retained historical entry-1 source and records keep their existing contract; this clause does not backport an OS gate or admit an old-window target through the new Windows path.

The windows-2 native entry is an absolute allowed Python invocation with -I -B and the verified colvia file; it does not require a POSIX shell, executable bit or .cmd wrapper. Independent source lifecycle uses explicit windows-2 profile where that command already accepts --profile. Preserve existing command names, --input file/stdin schemas, request/token semantics and exit-code precedence. A profile or filename alone is not provenance.

Before declaring Windows PowerShell 5.1 supported, verify the real product's argv, file/stdin inputs and exit codes, including required spaces, Korean text, quotes and metacharacters. Do not narrow the existing accepted input contract for portability. If preservation fails, report that shell path as unsupported and select an exact alternative or demonstrated existing input path before making a support claim; this clause does not install or mandate PowerShell 7.

Report policy-level unsupported, classification unknown, later drift/stale and actual publication/sync/replace failure distinctly. Preserve the native error and observable phase/state without adding a new persisted diagnostic field or silently mapping unreadable to absent. The diagnostic categories are not new CLI enum values. Read-only diagnostics do not repair or reflush. A matching old request/token is not proof that prerequisites remain valid or that a previous failed invocation made no change.

An existing read-only replacement/removal target or an existing file requiring a write-capable open for mandatory flush is policy-level unsupported for the whole proposed operation before its first durable publication; an unavailable filesystem/attribute observation is unknown. The required-flush subset follows Workspace Contract's operation-specific duties, including recovery reflushes, not all unchanged files. Later attribute changes are drift; actual replace/remove/flush failures report the observed phase and preserve the prefix. Native local NTFS applies to those actual operation paths, including guard scratch and external backup; a standard-user qualification label alone does not satisfy it. Pure read/preserve exemption never waives bound repair observations. While a remaining repair replacement target is read-only, a fresh preview is non-pass with no executable request/token. Original exact retry after external attribute restoration still requires all admitted before/after observations and exact backup, candidate, binding and prefix checks. A separately admissible fresh request uses its own identity/token/backup and existing exact authorization under Structure and Operations; no new command, automatic fallback or permission-clearing action is introduced.

## Official Execution Candidate

Current source exposes bounded execution only in an explicitly verified `official-execution-2` installation. `colvia run` previews by default; `run execute --input SPEC --confirm DIGEST` consumes one grant. `run status --grant DIGEST`, `run cancel --grant DIGEST --reason CODE`, and `run resolve --grant DIGEST [--confirm DIGEST]` inspect, request cancellation, or record an operator resolution. Status and resolution accept optional `--host-control-root PATH` for explicit recovery availability checks. V2 cancellation uses fixed reason codes, with `cancelled` as the default. Read the verified release's `docs/OFFICIAL-EXECUTION.md` for exact input, effect and storage boundaries; retained v1 releases keep their own command contract.
