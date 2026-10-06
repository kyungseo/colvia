# Reference

Document authority and currentness: [Documentation Index](README.md).

## Single-Home Development Commands

The current development profile is `checkout-1` with one `.hrn/` home. It exposes a machine interface plus a read-only human view and manual natural-language adapter. An installed project uses `./hv2`. An independent contribution source uses `./hv2 --source-checkout` explicitly.
A source path or a successful test suite is not permission to modify an adopter.

| Entry | Command | Input and effect |
| --- | --- | --- |
| Independent source | `init --profile checkout-1 --target PATH --source PATH --authority-home-id ID --operation-id ID --observed-at TIME` | Preview only; save its `request` and token. Apply with the same target/source/profile plus `--apply --input FILE --confirm TOKEN`. |
| Installed or independent source | `status`, `doctor` | Read-only product and complete record-graph diagnostics. Source accepts `--target PATH`. Healthy product output derives `documentation_root` and its README entry from the verified active release. |
| Installed | `update --source PATH --operation-id ID --observed-at TIME` | Preview a candidate; `--apply --input FILE --confirm TOKEN` applies the exact request. |
| Installed | `rollback [--to RELEASE] --operation-id ID --observed-at TIME` | Preview a receipt-backed release; apply the exact request and token. |
| Installed | `detach --operation-id ID --observed-at TIME` | Preview exact managed removal; apply the exact request and token. Project truth remains. |
| Independent source | `update`, `rollback`, `detach` with `--profile checkout-1 --target PATH` | Exact original request/token plus `--apply --recover` resumes a supported publication prefix. Preserve unknown/torn bytes. |
| Independent source | `repair --target PATH --source PATH --backup NEW_EXTERNAL_PATH --operation-id ID --observed-at TIME` | Preview restoration of the exact active product. Apply its request/token; interrupted repair uses `--recover`. Installed repair is not exposed. |
| Installed | `intent draft`, `intent prepare`, `intent apply` | Canonical JSON from `--input FILE` or stdin. Apply additionally needs `--confirm TOKEN`. |
| Installed | `work publish [--worker PATH]`, `work prepare`, `work apply` | Canonical JSON from `--input FILE` or stdin. Worker result publish requires the registered linked worker path; start/baseline rebind omit it. Apply additionally needs `--confirm TOKEN`. Worker accept records the decision before exact file application and selects completion only after whole-result checks; human baseline rebind is separate. |

See [General Work](GENERAL-WORK.md) for exact machine input fields and recovery constraints, and [Workspace Contract](WORKSPACE-CONTRACT.md)
for record and lifecycle boundaries. Apply consumes the preview's `request` or prepare's `ticket`, not the outer response envelope.
Preview/prepare does not grant permission; the human decides acceptance. Confirmation tokens bind bytes, not OS identity.

`documentation_root` is project-relative and derived, not another stored authority or document registry. It appears only after product and
record verification succeeds (possibly with pending record publication or unsupported local runtime clearly classified). Pending product,
detached, degraded, or unrecognized state does not invent an active document root. Documentation availability is not a claim that a user read
it or that project-authored documents were accepted. Before detach, retain a trusted independent source/manual if needed.
For a pending Work publication without a decision, preserve and retry the exact original publish request after restoring its prerequisites.
For a pending Work decision or intent acceptance, preserve the original ticket and confirmation token, restore the required runtime/content/document
preconditions, then retry the same apply. Do not invent a replacement decision to bypass pending records. The narrowly supported local or all-pre worker cancellation of a pending Work acceptance follows [General Work](GENERAL-WORK.md); this advice does not remove that contract. An unsupported runtime must be
replaced with final, GIL-enabled CPython 3.14.6 or 3.14.7 before mutation. Single-home mutation entries, root creation, and the shared writer guard enforce implementation, explicit version membership, final release level and GIL-enabled build before writing. This is a trusted-local support check, not interpreter authentication. Status reports these actions without modifying records or manufacturing recovery input.

## Single-Home Paths And Outcomes

`.hrn/format.json` identifies the format and authority. `.hrn/intents/` and `.hrn/work/` contain project-owned truth.
`.hrn/product/` and the root `hv2` are removable runtime material. `.hrn/detached.json` preserves the removal plan and receipt.
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
| `HV2-WORKSPACE-RUNTIME` | Mutation requires final, GIL-enabled CPython 3.14.6 or 3.14.7. Preserve the target and use that runtime; read-only diagnostics remain available. |
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

Generation commands and `--legacy-baseline` are removed. A source init/update/rollback/detach call without `--profile checkout-1` fails instead of selecting an old profile. Installed commands select their bound profile. Source help and installed help deliberately expose different operations.

### Checkout Compatibility Limits

Only planning-1 and checkout-1 targets admit the new source's update. A durable checkout-1 receipt prevents older-window downgrade; recovery requires the exact new source and original request. Old worker manifests need an explicitly approved new control baseline, same-intent rebind and resubmission. New detach uses paired plan/receipt schema 2; legacy schema 1 reading is retained, but its recovery belongs to the retained old source. See [transition instructions](GETTING-STARTED.md#transition-to-checkout-1).

Retained older source applies only while that older window is active or for its recorded legacy recovery. It is not a rollback path after a checkout-1 receipt.

## Human Review

A healthy observation shares its verified graphs between status and rendering. Within its Work sweep, repeated intent references share a verified intent graph while every exact historical binding is still checked. A final independent intent collection read must match every shared graph; changes or failures discard the shared result and use the existing fresh, unshared status path. Partial, pending and unsupported graph results also use the unshared path. Work records and independently loaded intent graphs retain double reads. Before and after view observations, retries and separate commands never share this temporary state. All Works, relations and umbrella histories remain checked; writers and current/live-reference checks keep fresh reads. Changes restored between checks are not guaranteed to be detected. Stable inputs retain the same output and exit status. Concurrent changes may cause a retry and a degraded or unstable result instead of an immediate unavailable result; this is not an atomic snapshot or permission to apply.

`./hv2 view` lists verified intent/Work state and current release entry paths. Use `view intent ID [--revision ID]`, `view work ID [--revision ID]`, or `view confirmation --input FILE|-`. Independent source: `hv2 --source-checkout view --target PATH ...`. These commands write GFM to stdout without publishing files, locks, on-disk caches or decisions. Imported view errors are GFM with a nonzero exit; bootstrap failures remain JSON/65. Status/doctor and machine commands retain their JSON contracts.

Confirmation consumes canonical ticket bytes, not the prepare response envelope. Observations are advisory and may be unavailable or stale; there is no aggregate permission-to-apply result. Apply checks prerequisites again. A completed record does not prove current project files match. Work comparisons list path/mode/size/digest changes, not historical text bytes; rebind discontinuities are not attributed to the Work.

Document bodies remain project Markdown. The view displays role, path, recorded digest and current observation; open those documents or have your agent explain them. Advisory reads reject links, special/unstable inputs and files over 4 MiB. A Core-readable large file can therefore be unavailable in the view. Worker-observed evidence is not reverified on control.

The checkout-1 runtime rejects serial-1 and unknown windows. Independent-source reading retains valid human-1, worker-1, umbrella-1 and planning-1 history; candidate creation and execution require checkout-1. The installed launcher refuses old bindings before loading managed code. Old source profiles are parser errors. Transition uses the qualified independent new source; see [Transition To Checkout-1](GETTING-STARTED.md#transition-to-checkout-1).

Command syntax/argument errors retain argparse stderr and exit2; the GFM error contract begins after argument parsing. The default human view omits the managed file inventory; status/doctor retain machine diagnostics.


Paths and digests use dynamically delimited GFM code spans; ordinary punctuation stays readable in raw stdout. Control characters are visible escapes and literal backslashes are distinguished. The view summarizes status before details and separates intent documents from Work revision documents. Revision progress/next_action are recorded historical fields, not the current derived Work state. Selected history follows the parent chain and includes the human action, actor and reason; the separate decision list is not chronological.

Confirmation advisory checks include required ticket references and, for Work accept/rebind, required bound intent references. The bounded reader may be stricter than Core, so an unavailable observation is not proof of a Core refusal. Worker-observed evidence is not reverified on control. Reject/revoke do not require live reference agreement. Worker accept cancellation still requires all changed paths pre and no durable result selection. There is no aggregate readiness grant. View-internal type/attribute/index failures return GFM with exit70; argument errors remain argparse/2 and pre-import launcher errors remain JSON/65.

The bounded reader requires searchable and listable physical ancestors from `/`, exact spelling, no symlink ancestor, and a regular single-link file. A macOS `/tmp` or `/var` alias can therefore be refused: use the real physical path to an authorized ticket or canonical stdin. Do not weaken the Core or remove files to bypass an unavailable observation.

Later patches, prereleases and free-threaded builds are rejected. Other OS or distributor builds matching the accepted version conditions may execute; that is not a claim that they have been qualified. See [Security and Support](SECURITY-AND-SUPPORT.md).

In status, `supported_baseline` retains the historical first qualified version; it is not a minimum version. `supported_versions` is the exhaustive patch allowlist.

In status, `runtime.supported` reports the version gate, not OS/build qualification. A `classification: pass` result does not establish that this OS/build or an actual adopter has been qualified.


For result acceptance, pair `./hv2 view work ID --revision REVISION_ID` with `./hv2 view confirmation --input FILE` (or `-`) for the same selected revision. Work details contain `observed_scope` and `unavailable_scope`; the confirmation view does not directly repeat these arrays. Explain all unavailable items against the human's declared acceptance criteria before applying the exact ticket. Nonempty observation text alone does not make a graph degraded, and an empty list does not prove verification. Required-reference and live-content refusals remain mandatory. See [General Work](GENERAL-WORK.md#observation-limits-and-human-acceptance) and the current managed adapter.

The author-declared `unavailable_scope`, an advisory reference observation labeled unavailable, and a `*-UNAVAILABLE` authority-read error are different. The last remains a degraded/write-refusal condition; neither observation prose nor an advisory display waives it.


Worker Work/confirmation views distinguish control baseline from retained candidate and partial application. Changed Work references display candidate and live-control observations separately. Human baseline refresh compares old baseline/candidate with the proposed baseline and labels content matches without attributing their cause. These read-only observations do not authorize an action or replace guarded validation. See [Worker Review Observations](GENERAL-WORK.md#worker-review-observations).

### Observation-Local Topology Reads

A healthy Git primary status observation may share only the raw topology probe within its first Work sweep. Target, ancestor,
resolved-path and effective ignore checks still run on each read. After any raw reuse, a final fresh topology probe must match
before the independent final intent read and graph comparison. Failure discards the context and uses the existing fresh fallback.
The context is not passed to writers or retained across requests or view observations, and creates no disk cache or lock.
Persistent topology changes may therefore be detected more strictly than an entry-only status label. Intermediate Git failures
or topology changes that revert between the first and final probes are not guaranteed to be observed. These reads are not an atomic
snapshot or a performance guarantee.


## Candidate Planning

Candidate planning records ideas before they become execution work. Ask the agent naturally; the installed adapter prepares machine input. `./hv2 view candidates` is read-only and shows the recorded choice, reasons, conditions and actual linked Work state. The root `./hv2 view` includes the same section. A recommendation writes nothing; selection is not intent acceptance or execution approval.

Only an explicitly installed checkout-1 runtime writes candidates. `./hv2 candidate ACTION --input FILE` (or `-` for stdin) accepts one canonical JSON object. Source mode has no candidate writer. Supported actions are `add`, `amend`, `select`, `defer`, `resume`, `link`, `disposition`, `reopen`. Success returns `saved` or exact-retry `unchanged`, the resulting store and digest. Before writing, tell the human any outstanding lifecycle preview will need preparation again.

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

Load this section when the human requests a comparison, decision record or unresolved-question note. It is an optional agent authoring procedure; Core does not generate these documents. Project rules own their language, location, identifiers, index and lifecycle. Read the project README and directly relevant existing narrative first, not every archive or a previous workflow's templates.

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

1. Run the current `./hv2 view` at control. Inspect pending operations and the intent/Work objects it lists, then `./hv2 view work ID` and `./hv2 view intent ID` for relevant scopes, states and references. Root view alone is not a reference-impact audit. Disclose known prepared-but-unapplied tickets: they are not all discoverable in the store and a document edit can stale them; do not claim an object-view search exhausts outstanding tickets. Include every proposed document and index path, including new files. Prioritize unfinished Work, current accepted intents and children captured by unfinished parents. Read the exact `view work ID --revision ID` for bound intent documents in related captured/historical revisions. `view intent --revision` still displays current acceptance documents, not that historical acceptance. Completed history matters for preserving what was accepted then; it is not by itself a live edit prohibition.
2. For every unfinished Work (including rejected/revoked before rework), if a path is outside its scope or the edit would disturb a submitted/rework result, worker control baseline or pending recovery, do not write. Rejection does not finish the Work or permit out-of-scope writing. After reject/revoke, even an in-scope edit before authorized rework publication would break the retained baseline. Explain the proposed content in conversation, explicitly say it is not saved to a project file, and name the operation or authorized scope/baseline change after which it can be recorded. The human can choose to finish/recover the existing operation first or separately authorize a supported intent/scope/baseline change. Never silently expand scope, absorb drift, publish a revision or lower a required flag. During review/pending, project-content handoff stays read-only. An explicitly requested candidate write during submitted-review still follows Candidate Planning; pending intent/Work/lifecycle barriers block its writers. Planning is outside content snapshots but is not an implicit fallback save channel.
3. Trace document/evidence references to each target using object views, including required intent inputs and related captured child/parent references. Explain stale/missing/unavailable observations and the cost of the lookup. Use a temporary, request-local list, not a permanent index/cache. If the affected reference set cannot be established, stop at a read-only proposal rather than claiming the edit is safe.
4. Prefer keeping a referenced predecessor DR byte-for-byte intact. Put an amendment/supersession's exact replaced and still-valid scope in the successor and any relevant existing index; check those paths too. If the human needs an in-place change, distinguish the reference owner before editing. A required intent input can require new exact intent acceptance, human Work rebind, resubmission and new exact result acceptance. For an authorized pre-submission edit to a required Work-revision document, include its new digest in the result submission; that reference alone does not require new intent acceptance or rebind. A checkpoint cannot absorb changed project content. After submission, use the supported mode-specific reject/rework or human baseline-refresh path before editing/resubmitting; local same-intent rebind is not supported. Captured child intent references can affect a parent even after the child completed. Never evade the guard with a copy or a non-required flag.
5. A non-required reference can describe a changed working draft without blocking on that reference alone. It still participates in whole-project content validation: changing it after submission can stale the result. Explain the existing mode-specific rework/baseline-refresh/resubmission path before any authorized edit. Do not rewrite a historically accepted decision as though the revised bytes were accepted then.

When the checks permit the requested write, make the smallest narrative change, preserve unrelated content and check direct links and the project's rendering requirements. Report what was recorded, what remains Draft/open, and which decision or validation is still needed. Project Markdown survives runtime replacement/removal; preserving it is not acceptance of its claims.


## Repository-Owned Rules

Use repository rules for project-specific documentation, validation or domain procedures. Core continues to own typed state, exact acceptance and integrity checks; a repository rule cannot override them. The Product supplies the application guidance below. The project owns the adopted rule, its local choices and the evidence that it was followed. Rules are instructions to agents and maintainers, not a runtime enforcement engine or a new authority record.

### Locate And Describe A Rule

Reuse the project's existing shared instructions or maintainer document. Keep one canonical rule and a short pointer from the relevant agent entry; retain tool-specific instructions where they are needed. No rule directory, manifest, package format, STATUS file or registry is required. Load a rule when its scope or trigger applies, not as a demand to audit every document at session start.

A short section or table should let the next maintainer find:

| Information | What to record |
| --- | --- |
| Purpose and owner | The behavior it governs and the role responsible for maintaining it |
| Origin and local authority | The source rule/section and adopted release or revision, the project canonical location, and any explicit local choice or exception |
| Scope and trigger | Which files, changes or task situations require it |
| Action and check | What the agent/maintainer does and what observation supports completion |
| Update and removal | Where to compare a later source change, which local content must survive, and who decides conflicts or retirement |

Use an existing release/revision reference or a content digest when needed to identify the adopted input. Record that identity and the source section without pinning an installed managed-directory link as the current entry or update source; obtain the current managed path from `./hv2 view`. A current Harness installation does not prove project rules were updated with it. If origin, applicable version or ownership is unknown, report it as unknown and establish a human-reviewed comparison basis before replacing content. This comparison basis is not a typed Work baseline or a rebind. Do not invent provenance or precedence from a filename.

### Apply To A New Or Existing Project

For a new project, select only the rules needed for its actual work and put them in its chosen instruction/document structure. Explain their purpose and proposed entry pointers within the authorized adoption scope. Do not generate an empty framework of rule files.

For an existing project, inventory only the affected shared entries, tool-specific rules, hooks and related project documents. Compare the proposed rule with their current behavior. Preserve unique instructions, intentional local overrides and useful procedures; expose duplicates and contradictions before changing them. Present the exact project diff and any missing behavior. The human resolves a material policy conflict; an agent must not silently choose whichever rule is newer. Do not delete tool directories merely because their content originated with an older workflow.

Apply an authorized project edit only after [Check Before Writing](#check-before-writing) permits its content/reference impact. Include rule and pointer changes in the appropriate project scope. An adoption request is not permission to alter a pending result, rewrite immutable records, edit the managed payload or bypass a required acceptance. Core init/update/rollback/detach do not write, refresh or remove these project-owned rules.

### Update, Verify And Retire

When a relevant Product or project behavior changes, compare the adopted source, incoming guidance and local rule. Keep local changes visible. If the old basis cannot be recovered, explain the uncertain comparison and prepare an explicit replacement proposal instead of calling it a clean upgrade. After an authorized update, record the new source reference and retained exception in the existing rule/narrative, and check its pointers and the affected behavior. Source guidance is not proof that a particular agent loaded or followed it; report unexecuted tool paths and real-user observations separately.

If a rule is no longer needed, identify the exact section and pointers it owns, preserve still-valid project requirements and required historical/reference bytes, and propose its removal or replacement. An obsolete rule does not authorize deleting its containing directory. Use Git or the project's existing recovery practice to preserve unique changes; do not keep a full source copy or permanent validation archive just to prove that a check ran. A changed or removed rule cannot retrospectively change what an earlier Work accepted.

### Project-Owned Adapter Additions

A local adapter may be a short section in an existing project rule or, when useful, a project-owned document. It tells an agent which applicable rule to read and what to explain. Connect it from the relevant project entry; do not edit or duplicate the installed adapter. For example, a CLI project can ask the agent to read its documentation rule before an authorized option change and explain affected usage examples, executed checks and remaining limits in the existing Work narrative. The project selects the actual paths and checks.

Record the same purpose, owner, source basis and update/removal information as for other repository rules. Follow the current managed adapter and preserve Core authority boundaries. Show conflicts before acting; a local instruction cannot waive acceptance or integrity checks. Verify the entry pointer and report whether a fresh agent session actually read the rule. This is an instruction pattern, not a native extension API or automatic discovery/installation guarantee; tool-specific packaging needs its own setup and verification.

When retiring Harness, separate installed guidance from these project-owned additions. Exact detach removes the managed manual/adapter with the product, while project entries, rules and user/global tool configuration remain outside its removal surface. Plan the relevant pointer replacements, retain valid local requirements and required reference bytes, and use [Detach](OPERATIONS.md#detach) for the runtime operation and post-detach entry check. An unexpected missing launcher remains an installation problem until the documented checks establish detached state.

### First Example: Documentation Currentness

A project may adopt this rule in its existing instructions:

> When changing an API, configuration, architecture or operating procedure, identify its canonical documentation and affected pages during planning. Update the necessary pages within the authorized scope and run the checks warranted by that change. If no update is needed, state the reason. If an update must wait, name the responsible follow-up and its resume condition. Record it in the existing Work or project tracker only when authorized and [Check Before Writing](#check-before-writing) permits; otherwise report it in conversation as unsaved and state when it can be recorded. Candidate records still require an explicit planning request. Do not report the documentation as current while that gap remains.

Map actual change types to actual project documents; do not copy a technology-specific mapping into an unrelated project. At result review, report the affected pages, checks and remaining gaps alongside the code/configuration result. Reuse applicable execution evidence and run only the missing checks. Rendering and link success establish structural properties, not semantic correctness or reader understanding. Paired language versions must preserve behavior, conditions and limits; record any unresolved mismatch rather than treating the older translation as current.

This example is the first application of the rule guidance, not a universal extension API. If a proposed rule needs a common invariant enforced by runtime, identify that requirement for a separate Core change instead of pretending prose enforces it.

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

Load this section for a pause, session summary or fresh resume. Start with `./hv2 view`, current accepted intent, selected Work and its referenced project narrative. Resolve multiple plausible targets before acting. Read the current adapter path again; a saved release path or yesterday's next action is not current authority.

- For “stop here”, report the target and selected state, actual changes, remaining checks/limits, pending recovery if any, and the next concrete action with existing document links. Session end is not completion, rejection, revocation or a Git commit. Do not publish a typed checkpoint/revision or create a handoff file merely to save this summary.
- Reuse an existing in-scope narrative for an authorized progress update only when the [document checks](#check-before-writing) permit it. Otherwise give the summary in conversation and mark unsaved decisions/notes as not recorded in project files, with the condition for later recording. Review/pending and rejected/revoked before rework use a read-only content summary. Preserve important uncommitted/ignored deliverables through the host's existing preservation procedure; do not move/delete records or use a backup as permission to commit.
- For “continue yesterday's work”, explain pending recovery before ordinary editing. Follow the current selected revision and its references; report missing/stale/unavailable narrative instead of declaring resume complete. If prose says Done and typed state says review, show both. Revision `next_action` is a historical agent field, not the current derived state or authorization. A handoff-only read leaves selection unchanged.
- For a completed Work follow-up, preserve the accepted result/history and propose the new task or the separately authorized supported lifecycle action. Do not silently reopen, overwrite or revoke it. Candidate resume affects only the explicitly named deferred candidate; it never resumes a Work.

A conversational summary and a fresh agent reading it are not proof of human understanding. Record actual user feedback separately when evaluating the experience; do not require a session registry or extra acceptance step for an ordinary pause.

## Project Context And Targeted Document Checks

Use existing project context. If it is missing and needed for the request, ask only for unanswered purpose, intended users and success criteria. Project context is broader than the six facets of one intent; do not ask for a technology stack for non-code work. Put an authorized context or Open Points update in an existing README/plan where suitable, after the same document checks. For an open question record the question, why it matters, resolution condition and actual conclusion when known. Closing a narrative question does not resolve a typed material intent gap; those gaps still block intent acceptance. A general project question does not automatically block unrelated Work. Do not make every context document a required intent reference.

For a requested document health check, read the named documents and directly related links/indexes. Report each broken link, stale candidate or disagreement with its evidence, effect and smallest proposed repair. Age alone does not expire a DR. State the bounded coverage and unavailable inputs; semantic consistency is judgment, not a Core proof. Keep the check read-only unless the request already authorizes specific repairs, and apply the document scope/reference checks before each repair. A request to inspect or archive is not permission to bulk move/delete typed history, rewrite referenced decisions, audit every archive or add a cache/status board. Preserve referenced bytes and explain the supported reference transition before proposing a move.
