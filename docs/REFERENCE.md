# Reference

Document authority and currentness: [Documentation Index](README.md).

## Single-Home Development Commands

The current development profile is `planning-1` with one `.hrn/` home. It exposes a machine interface plus a read-only human view and manual natural-language adapter. An installed project uses `./hv2`. An independent contribution source uses `./hv2 --source-checkout` explicitly.
A source path or a successful test suite is not permission to modify an adopter.

| Entry | Command | Input and effect |
| --- | --- | --- |
| Independent source | `init --profile planning-1 --target PATH --source PATH --authority-home-id ID --operation-id ID --observed-at TIME` | Preview only; save its `request` and token. Apply with the same target/source/profile plus `--apply --input FILE --confirm TOKEN`. |
| Installed or independent source | `status`, `doctor` | Read-only product and complete record-graph diagnostics. Source accepts `--target PATH`. Healthy product output derives `documentation_root` and its README entry from the verified active release. |
| Installed | `update --source PATH --operation-id ID --observed-at TIME` | Preview a candidate; `--apply --input FILE --confirm TOKEN` applies the exact request. |
| Installed | `rollback [--to RELEASE] --operation-id ID --observed-at TIME` | Preview a receipt-backed release; apply the exact request and token. |
| Installed | `detach --operation-id ID --observed-at TIME` | Preview exact managed removal; apply the exact request and token. Project truth remains. |
| Independent source | `update`, `rollback`, `detach` with `--profile planning-1 --target PATH` | Exact original request/token plus `--apply --recover` resumes a supported publication prefix. Preserve unknown/torn bytes. |
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

## Source Utilities

`classify-intent-entry --consequence consequential|non-consequential [--input FILE]` classifies provided gaps without publishing records. An input file has exactly one `gaps` field. `durability-probe --root PATH` writes disposable diagnostic files to an explicitly chosen scratch directory; it refuses a workspace root or descendant. It is not a read-only status command.

Generation commands and `--legacy-baseline` are removed. A source init/update/rollback/detach call without `--profile planning-1` fails instead of selecting an old profile. Installed commands select their bound profile. Source help and installed help deliberately expose different operations.

## Human Review

`./hv2 view` lists verified intent/Work state and current release entry paths. Use `view intent ID [--revision ID]`, `view work ID [--revision ID]`, or `view confirmation --input FILE|-`. Independent source: `hv2 --source-checkout view --target PATH ...`. These commands write GFM to stdout without publishing files, locks, caches or decisions. Imported view errors are GFM with a nonzero exit; bootstrap failures remain JSON/65. Status/doctor and machine commands retain their JSON contracts.

Confirmation consumes canonical ticket bytes, not the prepare response envelope. Observations are advisory and may be unavailable or stale; there is no aggregate permission-to-apply result. Apply checks prerequisites again. A completed record does not prove current project files match. Work comparisons list path/mode/size/digest changes, not historical text bytes; rebind discontinuities are not attributed to the Work.

Document bodies remain project Markdown. The view displays role, path, recorded digest and current observation; open those documents or have your agent explain them. Advisory reads reject links, special/unstable inputs and files over 4 MiB. A Core-readable large file can therefore be unavailable in the view. Worker-observed evidence is not reverified on control.

The planning-1 runtime rejects serial-1 and unknown windows. Independent-source reading retains valid human-1, worker-1 and umbrella-1 history; candidate creation and execution require planning-1. The installed launcher refuses old bindings before loading managed code. Old source profiles are parser errors. Transition uses the qualified independent new source; see [Transition To Planning-1](GETTING-STARTED.md#transition-to-planning-1).

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


## Candidate Planning

Candidate planning records ideas before they become execution work. Ask the agent naturally; the installed adapter prepares machine input. `./hv2 view candidates` is read-only and shows the recorded choice, reasons, conditions and actual linked Work state. The root `./hv2 view` includes the same section. A recommendation writes nothing; selection is not intent acceptance or execution approval.

Only an explicitly installed planning-1 runtime writes candidates. `./hv2 candidate ACTION --input FILE` (or `-` for stdin) accepts one canonical JSON object. Source mode has no candidate writer. Supported actions are `add`, `amend`, `select`, `defer`, `resume`, `link`, `disposition`, `reopen`. Success returns `saved` or exact-retry `unchanged`, the resulting store and digest. Before writing, tell the human any outstanding lifecycle preview will need preparation again.

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
