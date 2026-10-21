---
id: DR-0001
status: Accepted
date: 2026-10-07
revised: 2026-10-21
---

# DR-0001: Work Continuation Selection And Recovery

## Question

How can a Work retain its selected follow-up, an explicit decision to have no follow-up, and withdrawal without changing its accepted result or lifecycle, while allowing interrupted publication to be recovered or cancelled and read accurately in a new session?

## Decision

The human Owner accepted the corrected continuation contract on 2026-10-21 and explicitly authorized its bounded U1 implementation, including visible normal-operation usage and remaining quota. Adopt immutable choices/selections with a separate authoritative current; Owner-only select/withdraw/cancel; project-wide refusal while continuation is pending or its integrity is unavailable; and 256 normal operations per source Work with separate cancellation capacity. The exact meanings, schema, references, publication/recovery and limits in the contract below apply.

This is the accepted source contract for the continuation-1 successor. It activates only the named continuation deltas for development; existing delegation-1 installations retain their installed contract until an exact qualified update is separately authorized. Implementation, test results, result acceptance, Git publication and real installation are distinct. The Owner authorized implementation under the previously revised 9.25~13.75-hour estimate and 16-hour cumulative stop; no runtime or adopter is qualified by this decision.

## Context And Scope

This is an accepted source contract; implementation and qualification remain pending. The Owner separately authorized bounded implementation on 2026-10-21. The contract does not itself authorize a live project writer or installation. The current product uses `delegation-1` under [DR-0005 activation](DR-0005-delegated-ordinary-work-acceptance.md#delegation-1-activation) and the contracts indexed in [Documentation Index](../README.md). The source successor below preserves existing authority except its explicitly named continuation deltas. Follow [Contributing](../../CONTRIBUTING.md) for decision acceptance.

[General Work](../GENERAL-WORK.md) defines Work and intent records, [Reference](../REFERENCE.md) describes candidate planning and project document references, and [Workspace Contract](../WORKSPACE-CONTRACT.md), [Operations](../OPERATIONS.md) and [Maintaining](../MAINTAINING.md) govern runtime and lifecycle changes. A current Work selection identifies its lifecycle revision; a candidate selection identifies a project planning choice. Neither is a dedicated follow-up choice for one Work.

A static source comparison found that the Work reader admits known record directories, pending guards enumerate existing Work/intent operations, and lifecycle truth collection first validates the Work graph. Therefore adding a continuation directory requires coordinated reader, guard and lifecycle changes. This is a design dependency, not a reproduced product defect. The proposed records, limits and recovery rules have no implementation or execution evidence.

## Named Successor Scope

The source comparison basis is `aa1e66059083996a3dda08cd78bca7d0d93fddfa`. This is the source basis of the Owner-accepted corrected Draft reviewed in R0; [the selected contract-review record](../development/CHORE-20261021-001-continuation-contract-review.md) owns scope, review and remaining decisions. The R0 verdict remains CONDITIONAL on its original input; the Owner subsequently selected the corrected design and quota display on 2026-10-21.

The accepted successor keeps immutable choices/selections, a separate current, Owner-only choice/cancellation and project-wide pending protection. It replaces only the named clauses below for continuation-1; unrelated obligations and historical accepted bytes retain their meaning.

| Effective Owner / Clauses | Accepted Replacement Or Extension | Preserved Meaning |
| --- | --- | --- |
| DR-0002's retained record-shape/pending guarantees, carried by [Structural Contract](../development/CHECKOUT-1-STRUCTURE.md) Root Format And Record Locations, Work Shapes And State, Reader/Publication/Change Boundaries and Delegation-1 Successor Delta | Admit exactly the new Work-local continuation subtree and schema-1 records; validate base Work/intent before continuation; extend every official writer's pending guard | Strict known-shape/typed-ref/alias rules, Work schemas 1/2, intent schemas 1/2/3, exact history/current and unchanged source result bytes |
| DR-0004 entry-1 and First B1 guarantees, with DR-0005's current [Workspace Contract](../WORKSPACE-CONTRACT.md) lifecycle/window clauses and Structural Contract Window And Lifecycle Pairing | continuation-1 after delegation-1, paired lifecycle plan/receipt schema 5 for all new lifecycle actions, exact predecessor admission and downgrade barrier | Existing entry transition, captured-child protection, permission observation, truth preservation and exact old-source recovery; schema/action pairs 1~4 are not reinterpreted |
| DR-0005 authority and [General Work](../GENERAL-WORK.md) Delegation-1 Implementation Candidate | Extend window admission for the unchanged ordinary isolated-worker accept grant; add a distinct Owner-only CONT writer | Grant binding/consumption/revocation/ancestry and parent-human acceptance; a Work accept grant never grants CONT select/withdraw/cancel |
| Current Reference/Operations/Maintaining, view, entry and adapter clauses carrying those contracts | Exact commands, separate lifecycle/follow-up projection, pending/recovery, package membership and entry/plan alignment | Project narrative ownership, source/installed distinction, evidence reuse, exact acceptance and separate installation/publication authority |

The owning record identifies the accepted decision and the initial normative successor additions by exact bytes. Implementation documentation may explain those accepted clauses within the approved scope; a material contract change needs its own Owner decision. DR-0003 intake/criteria and DR-0006 development procedure are unchanged. New runtime/platform support, general attach/pending clone recovery, priority history and an automatic planner remain outside this proposal.

## Options Considered

| Option | Benefit | Cost Or Limit | Proposed Disposition |
| --- | --- | --- | --- |
| Put the follow-up in a Work revision/current | Reuse existing paths | Couples follow-up changes to source lifecycle and acceptance records | Do not select |
| Reuse project candidate selection | No new store | Project planning and a Work-specific follow-up have different lifetimes and authority | Do not select |
| One mutable history/current file per Work | Simplifies the atomic publication boundary | Adds a separate bounded storage pattern and rewrites a potentially large file | Retain as an alternative |
| Immutable choices/selections and a separate current per Work | Matches existing immutable publication, exact references and explicit current | Requires cancellation branches, pending rules and a new reader window | Selected |

## Accepted Contract

### Responsibility And Meaning

```text
Work A current              A's lifecycle and accepted result
Work A continuation current The follow-up chosen after A
                              proposal: no target Work yet
                              work: an existing Work B
                              none: an explicit no-follow-up decision
No selection or withdrawal  Undecided
cancel-pending              Resolves incomplete publication; keeps prior meaning
```

Continuation is authoritative for the follow-up choice, not for creating or executing the target or accepting its result. Existing Work/intent approvals still apply. Before approval, the agent keeps a proposal in the current project narrative or preview. Only explicitly approved exact input is published from control. Actor strings, Owner statements and tokens are operating evidence within a trusted local account, not authentication.

One source Work has at most one current follow-up. Multiple alternatives belong to planning; decomposition, parent-child and dependency semantics belong to their respective contracts; projection presents the result for readers. Targets are same-home Works only. This proposal adds no cross-project graph, scheduler, automatic Work creation, automatic reselection or priority change. A→B→A references are neither recursively executed nor interpreted as dependency cycles.

### Layout And Initialization

```text
.hrn/work/<source-work-id>/
  identity.json
  current.json
  continuation/
    choices/<choice-id>.json
    selections/<selection-id>.json
    current.json
```

The operation does not write the source Work's existing lifecycle files or result manifests. Readers allow only known subtrees and regular files. Unknown keys/members, symlinks, special files, casefold/NFC aliases and invalid kinds, IDs or digests are preserved and make the state non-writable. Timestamps, filenames and directory enumeration do not order records.

The first approved apply prepares known empty directories and durably publishes an initial continuation current with `selection_ref:null` before writing a choice. Initialization is part of that same approved apply. Read and prepare create no directory or current. An absent continuation or known empty directories with no records mean undecided. If any choice or selection record exists but current is missing, the state is `unavailable-current`; do not infer a normal first pending operation or select the latest selection. Initial null current and a missing current file are different states.

Null is allowed only for initialization. After the first selection or cancellation selection, current never returns to null; a new selection expresses withdrawal. An interruption leaving known empty directories before initial current may be resumed by the next explicit apply without deleting records. Initialization retry cannot overwrite an invalid current or unknown file.

### Primitive Types And Limits

Every object has exactly its listed keys. Nullable fields are explicit nulls, not omitted fields. Use canonical JSON: UTF-8, no BOM or CR, sorted keys, indent 2 and one EOF LF; hash the raw canonical bytes with SHA-256. Reject duplicate keys, non-finite numbers, bool-as-int and unknown versions. Continuation-specific limits apply before the existing `jsonio` absolute limits of 4 MiB, depth 128 and 1024 integer digits.

| Type | Exact Shape And Constraint |
| --- | --- |
| `Id` | ASCII `[A-Za-z0-9][A-Za-z0-9_-]{0,95}`; reject casefold collisions within one namespace |
| `Sha` | 64 lowercase hexadecimal characters |
| `Ref` | `{id: Id, sha256: Sha}`; the containing field fixes record kind and source Work namespace |
| `QualifiedWork` | `{authority_home_id: Id, kind: "work", id: Id}`; same home as the source |
| `IntentRef` | `{authority_home_id: Id, kind: "intent", id: Id, revision_ref: Ref, acceptance_ref: Ref, selection_ref: Ref}`; exactly matches the Work revision's accepted intent |
| `WorkSnapshot` | `{object: QualifiedWork, revision_ref: Ref, selection_ref: Ref, intent_ref: IntentRef}`; the selection selects that revision, which refers to that intent_ref |
| `Text` | Nonempty string, 1–2048 UTF-8 bytes, no NUL; do not normalize or trim it |
| `LongText` | Same rules as Text, with a 4096-byte upper limit |
| `DocumentRef` | `{path: string, sha256: Sha, role: Text, required: boolean}`; current `project_path` and safe regular-file observation rules; path at most 1024 UTF-8 bytes; no `.hrn`, `.git` or managed launcher as document evidence |
| `observed_at` | Valid UTC `YYYY-MM-DDTHH:MM:SSZ`; provenance, not order or authority |

Canonical-byte limits are 24 KiB per ticket, 32 KiB per choice, 4 KiB each per selection/current and depth 16. There are at most 16 document refs; reject duplicate or aliased paths. Refuse an operation before its first write if the total-byte limit is exceeded, even when individual fields fit.

Each Work allows at most 256 normal operations (`select` plus `withdraw`) and at most one cancellation per normal operation. Choices and selections therefore each have at most 512 records, and all canonical continuation files total at most 20 MiB. Even 512 × (32 KiB + 4 KiB) + 4 KiB current fits within 20 MiB. These are accepted bounds for the first implementation, not measured performance guarantees. At 256 normal operations, refuse a new normal operation but allow the existing exact publication, its one cancellation and that cancellation's publication. A separate normal quota must not block cancellation. Check prospective record sizes/counts before durable writes; do not delete history to recover capacity.

Usage is derived from the fully validated continuation graph: expose `normal_limit: 256`, `normal_used` (durable select/withdraw choices, including later cancelled choices), and `normal_remaining: 256 - normal_used`. Preview/read, exact retry and cancellation do not consume another normal slot. Show current and prospective usage in a new-operation preview and current usage in Work/continuation views. At the limit, explain that new select/withdraw is refused while existing exact publication/cancellation remains permitted. No automatic reset, history deletion, Work splitting or unbounded extension is introduced. Invalid/unavailable graph means usage unavailable, never a guessed zero or remaining count.

### Ticket And Choice Variants

The exact `Ticket` keys are:

```text
record_type = "continuation-confirmation-ticket"
schema_version = 1
source: WorkSnapshot
expected_continuation_selection_ref: Ref | null
action: "select" | "withdraw" | "cancel-pending"
choice: ChoiceValue | null
supersedes_choice_ref: Ref | null
actor: Text
owner_statement: LongText
reason: LongText
request_id: Id
observed_at: UTC timestamp
product_binding_ref: Ref
target_fingerprint: Sha
document_refs: DocumentRef[]
```

`target_fingerprint` hashes the resolved path bytes of the actual control target, without storing the path itself. Actor matches the source Work identity's human acceptance authority. An ordinary isolated-worker acceptance grant does not authorize any continuation action; preserve its separate actor/consumption/revocation semantics. `owner_statement` describes the human request for that choice or cancellation. Preview shows the full ticket SHA, a confirmation token of its first 16 hex characters, source, prior, choice and limits. Apply receives the full ticket and a separate token and validates the full canonical bytes and bound conditions. A token alone is not human authorization. Keep the full ticket in the choice so staging is not the only copy of approval evidence.

| `ChoiceValue` | Exact Keys | Meaning |
| --- | --- | --- |
| proposal | `{kind:"proposal", goal:LongText, scope:LongText, next_step:LongText, decision_needed:LongText}` | Goal, scope, next action and next human decision for a follow-up not yet started; neither a new intent/Work nor an executable command |
| work | `{kind:"work", target:WorkSnapshot}` | An existing Work with exact evidence captured when selected |
| none | `{kind:"none"}` | No follow-up for this source selection; reason is in ticket.reason |

Only `select` has a non-null choice; its supersedes field is null. For `withdraw`, both fields are null and a prior effective choice must exist. If already undecided, return non-pass `already-undecided` without a new record. For `cancel-pending`, choice is null, supersedes points to the exact unresolved normal choice, and document_refs is `[]`. Its source exactly equals the original ticket.source and its prior equals the original expected continuation selection. Cancellation must not depend on the new target's or proposal's latest documents.

Request IDs are casefold-unique across this Work's continuation tickets. The same ID with the same ticket bytes is an exact retry; different bytes are refused. Replaying a historically resolved ticket does not change current. Replaying a cancelled original ticket returns cancelled and does not republish its choice. A shared request ID cannot implicitly approve changed source, binding or documents.

### Persisted Record Schemas

All three records require `record_type`, `schema_version:1`, `authority_home_id:Id` and `work_id:Id`. Home/Work match ticket.source.object and directory identity.

| Record Type | Exact Additional Keys | ID And Reference Binding |
| --- | --- | --- |
| `continuation-choice` | `record_id:Id`, `confirmation:Ticket` | `record_id = "choice-" + SHA256(ticket canonical bytes)` |
| `continuation-selection` | `record_id:Id`, `parent_selection_ref:Ref or null`, `choice_ref:Ref` | `record_id = "selection-" + SHA256(ticket canonical bytes)`; choice_ref hashes the whole choice; parent equals the ticket's expected continuation ref |
| `continuation-current` | `selection_ref:Ref or null` | Null only for initialization; otherwise references exact selection bytes |

The choice ID derives from the ticket digest; the choice reference digest covers the full choice envelope. Do not confuse them. Selection/current references likewise hash the referenced record's entire raw canonical bytes. Do not duplicate actor, time, reason, request ID or source in the selection. Derive effective choice, validity/staleness/pending and next action from the graph and live observations rather than persisting them.

### Graph Validation And Effective Choice

Observe and validate base source/target Work and accepted intent records before continuation; do not re-enter continuation validation through a target Work reader. Retain change detection across both observations. Then validate current and every choice/selection for exact kind, ID, hash, same home/Work and parent relation. Build an acyclic selection chain from one root with null parent. Current's ancestors are selected history. Never reconstruct current from directory order or timestamps.

A normal choice binds one expected continuation prior. Two competing normal choices at that prior conflict. One cancellation choice that exactly supersedes the original normal choice is the explicit exception below. Each choice has only the selection with its exact deterministic ID. Choices/selections outside current and its ancestors must belong to one pending operation or a validated cancellation relation. Preserve unexplained orphans/forks and report conflict.

A cancellation choice may supersede only a normal choice. Its source and prior match the original ticket, and current must still be that prior when cancellation is first published. The original selection may be durable but must not yet be selected history. Once cancellation is durable, classify the original selection as unselected retained evidence and exclude it from competing active children. Refuse a graph that uses that original selection as current or another selection's parent. Refuse cancellation of a cancellation, two different cancellations, or pending cancellation of a normal choice already among current's ancestors.

Derive effective choice from current's selection: `select` yields ticket.choice, `withdraw` yields undecided, and `cancel-pending` yields the parent's effective choice, or undecided for a null parent. Cancellation current advances while preserving the prior choice's source/target evidence and meaning. The cancellation ticket's source does not renew the prior choice's validity. Walk the bounded chain iteratively; do not recursively read the target Work's continuation.

### Publication, Retry And Pending Cancellation

Under the same project writer guard, validate runtime, authority, current source/continuation, live required refs, pending state and limits. Then prepare initial current if needed → durably write choice → revalidate → durably write selection → final revalidation → atomic current replacement and directory sync. Keep existing exact immutable writes and fsync/F_FULLFSYNC conditions; scratch belongs in `.hrn/staging`. Do not overwrite different bytes at an immutable path. Release the guard and handle scratch failures on every path; deleting records is not recovery.

| Observed State | Allowed Action | Invalid Interpretation |
| --- | --- | --- |
| No records / known empty initialization prefix | New preview and approved apply | Empty planning means explicit none |
| Initial current=null, no choice/selection records | Undecided; a new approved apply reuses the verified null current without overwriting it | Initialization alone is a pending chosen follow-up |
| Initial current=null, normal choice durable | Original exact publication or explicit pending cancellation | Choice alone confirms selection |
| Prior B current, C choice durable | Recover C or cancel that exact operation | Delete B or automatically make C current |
| C selection durable, prior B still current | Reuse the exact selection and publish current, or explicitly cancel | A selection file proves completion |
| Cancellation choice durable, cancellation current not yet published | Exact publication of that same cancellation only | Resume C, introduce a competing choice or cancel the cancellation |
| Cancellation current published | Keep B's effective meaning; allow a new normal preview | Reset B's stale conditions or delete C bytes |
| Normal current published | Same ticket is historical/current replay; new request binds current prior | Late retry promotes a past choice to current |
| Records exist but current is missing/damaged | Read as unavailable; separately assess recovery using a trusted exact retained copy | Guess latest selection or ignore damage through ordinary cancel |
| Torn immutable file, unknown member or invalid refs | Preserve, non-writable | Exact retry overwrites invalid bytes |

Normal recovery requires the original source/current continuation/binding, required documents and the target's exact selection-time observations to match again. If the target progresses before the original choice is published, the pending operation is stale; do not create a new ticket automatically. Explicitly cancel it before preparing a new choice. Normal progress after a completed selection follows the next section instead.

Prepare cancellation only while the original choice is unresolved, current prior is unchanged and original records validate. A changed live source/target selection or proposal document alone must not block cancellation. Verify the original source refs' historical integrity, source identity authority, continuation prior, safe control paths and active product binding. Official lifecycle changes are forbidden during pending, so binding must equal the original ticket. Pending recovery/cancellation after a move or clone changes the live fingerprint and is outside initial support; do not rebind it arbitrarily. This can leave the moved/cloned home read-only while pending. An Owner-directed restoration to the original verified control location may allow the original exact recovery/cancellation only after identity, original bytes, binding, fingerprint and all other applicable conditions match again; moving a directory back alone is not proof. If those inputs cannot be restored, retain the non-writable state and obtain a separate recovery decision. This proposal implements no general relocation or damaged-current repair.

### Shared Writer And Freshness Rules

- Begin a new continuation operation only when no existing Work, intent, lifecycle or continuation operation is pending. Exact recovery/cancellation of that same operation is an explicit exception.
- Continuation pending blocks all official mutations except its exact recovery/cancellation and existing exact active-release repair that changes neither binding nor truth. Reads remain allowed. Do not automatically undo user edits to project files.
- If any Work's continuation cannot be classified because its graph/current or member shape is invalid, treat project mutation admission as unavailable, not as no pending operation. All official Work/intent/candidate/lifecycle writers, including repair and detach, refuse until that integrity problem is resolved under a separately assessed exact recovery. The repair exception above applies only to a valid, classifiable pending graph with exact preserved truth. Read-only inspection remains allowed and reports the affected state as unavailable; never reconstruct current, delete unknown records or silently cancel to unblock writers.
- The writer guard serializes cooperating control writers. Workers can submit proposals but cannot write official continuation. It does not make Git merges, external file edits or concurrent independent-clone control atomic.
- With no pending operation, allow source lifecycle changes. A continuation choice must not permanently block completion or revocation. If the recorded source selection differs from the current one, the choice is historical/stale.
- Fresh select/withdraw requires a source snapshot exactly matching current Work selection/revision and valid historical accepted intent refs. Show any difference between those historical intent refs and current intent separately; it grants no new execution authority.
- On first selection, a Work target snapshot must match current selection/revision, and its bound accepted intent must currently be valid. After graph validation, compare the selected and current target revisions by the exact `intent_ref`, the set of literal validated `scope` paths (order alone does not change purpose; no path normalization), and `execution_context.mode`. A changed intent ref or scope set yields `target-purpose-changed`. Current Work history already forbids a mode change; a violated history is unavailable rather than valid normal progress. Changes only to revision/selection refs, valid operation/progress/result, timestamps or attempt_id do not by themselves change target purpose when that tuple is unchanged. Show target rejection, revocation or pending as separate execution limits; do not automatically reselect.
- Show required document drift as changed selection evidence and do not use it to justify execution. Show unobserved/changed optional refs too, without deleting the choice for that reason alone. Distinguish integrity failure from ordinary live drift.

This read model does not compute execution authority as a scheduler. Check the current human request and the target Work/intent's existing authorization. Do not add a separate continuation approval merely to repeat approval of the same already authorized action.

### Reader Window And Lifecycle Boundary

The proposed new `inventory_id` is `continuation-1`, after delegation-1 (proposed rank 7). Keep root format 1, existing Work revision schemas 1/2, intent schemas 1/2/3 and their authority meanings; add continuation record schema 1. Do not silently extend delegation-1, which does not support continuation records. Reserve paired lifecycle plan/receipt schema 5 for all new init/update/rollback/repair/detach actions; retain exact historical schema/action pairs 1~4 and reject mixed/unknown pairs.

| Boundary | Proposal |
| --- | --- |
| New init | Install continuation-1 with explicit approval; do not overwrite an existing root with a new init because its reader is missing |
| Existing installation | Initially support an explicit, exactly qualified delegation-1 → continuation-1 update only. Fix the predecessor artifact identity before transition tests/adoption; a shared window name does not admit every release. Older active windows need their own supported transition |
| Downgrade barrier | From the first durable continuation-1 lifecycle receipt, refuse downgrade to delegation-1 or older, even with no continuation records |
| Rollback within the new window | Only between releases with P→Q→P evidence that P reads and preserves Q-created continuation |
| History reader | Retain human-1/worker-1/umbrella-1/planning-1/checkout-1/entry-1/delegation-1 history with its original action/schema meanings; add no unknown/serial-1 support |
| Old source/writer | Preserve and remain non-writable when the new inventory/receipt or continuation subtree is not understood; never bypass the new window through an old writer |
| Detach | Write both new-window plan and receipt as schema 5; preserve old paired schema 1/2/3/4 meaning, but new-source writes/recovery use schema 5 only; recover old detach prefixes with the exact retained old source |
| Clone / detached plain read | Track and preserve choices, selections and current as project truth; do not compare historical ticket fingerprints to the clone's path, but require a live fingerprint match for pending apply |

A preview/request plan, including a saved input file, does not itself create a canonical pending transition. Preserve the existing publication order: the first durable authoritative transition item is the receipt containing that exact plan, before candidate payload, launcher or binding publication. From that receipt, only the exact new-source forward recovery is permitted and older source/writers refuse, including a late-lock caller. An incomplete/torn receipt is unavailable and cannot be treated as no transition. Before any receipt exists, unchanged old authority remains subject to the ordinary checks; a subsequent apply revalidates all preview conditions. Do not invent a separate authoritative plan-only phase.

Detach schema 5 closes the reader window by version; it does not authorize different removal targets, order or preservation obligations. Bind continuation in the new plan's truth_refs/preserve set. Even after new detach has removed product receipts, old delegation-1 source must not continue that prefix as schema 4. Do not delete unknown/legacy receipts or edit versions to recover.

Change and verify all consumers together: Work tree reader/truth visibility; Work/intent/candidate pending guards; current bound-runtime admission; source/installed CLI; status/doctor/projection; update/rollback/repair/detach; launcher allowlist/managed inventory; and the plain auditor. The implementation plan proposes `src/hv2ref/continuation.py` as the only new runtime module, taking the new managed set from 29 to 30 files and the launcher module allowlist from 11 to 12. Fix exact new membership and preserve every old literal membership, including the distinct 29-file planning/checkout, entry and delegation sets; never recompute historical membership from the new set. A window name or matching digest alone does not prove compatibility.

Static predecessor admission evidence at the source basis: `WorkStore.__init__` uses `product.require_workspace_runtime`; that gate requires inventory_id exactly delegation-1, and `WorkStore._runtime` independently rejects unknown windows. Intent publication and apply call that same gate under writer_guard and recheck it before publication. Thus current source admission does not depend on a continuation subtree being present. Fixture-injected runtime doubles are not production writer admission. This is a static source check, not executed qualification of an installed predecessor; C13 must still exercise the exact retained predecessor, the new receipt without CONT records and late-lock/prefix cases.

### Projection Contract

Present Work lifecycle and continuation separately. At minimum show source Work identity/current lifecycle, recorded continuation selection/ref, effective kind/content, selection-time source/target evidence, live source/target state, pending/cancellation state and the next human decision. Damage is unavailable; source drift is historical/stale; changed documents or target purpose have specific reasons. Do not collapse undecided, none and damage into one label.

Examples: “A completed / follow-up B selected / B in review / B result acceptance needed”; “A completed / prepare a follow-up intent proposal selected / no target Work”; “A completed / no follow-up decided”; “A completed / C selection publication interrupted / prior B retained / exact C recovery or cancellation needed”. Distinguish already authorized follow-up execution from a new approval requirement.

Projection is derived stdout, with no new authoritative cache. Deleting or regenerating it does not change canonical records. Deleting continuation current damages authority; it is not projection cleanup. Reuse the bounded current graph without recursively expanding target continuations. Exceeded data limits, unstable observation or integrity failure end with explicit unavailable.

### Adapter Plan Alignment And Entry

Core owns exact continuation truth; existing project narrative owns plans, results and remaining work. The adapter reads the verified installed entry and documents designated at task start, connects plan items to candidate/Work, and reports reflected / no change needed / not yet reflected. Resume checks relevant linked closeout/follow-up records for unreflected outcomes; a missing link or unreadable evidence is unavailable, not proof that nothing remains. Do not add an authoritative plan store or automatic ranking/synchronization.

Plan edits stay within the approved scope and required-document/whole-content rules. Preserve pending refusal and consider effects on other Work baselines before edits. Result acceptance and plan reflection are distinct. Candidate choice does not overwrite Work CONT; show conflicting valid Owner choices without deciding by timestamp. Root view already lists readable completed Works; verify root → Work → continuation/narrative and Work-detail entry rather than assuming completed Works are hidden.

U1 covers entry/selection/alignment guidance and CONT P-1~P-6. U2 owns actual continuous execution of the same Work, umbrella/delegation usage scenarios and host recovery/Owner-effort observations; it does not own every form of actual use. Existing umbrella/delegation safety regression and correct mode selection/refusal stay within U1. U1 requires one newly observed end-to-end continuation/plan-alignment use in an already existing non-sensitive real task, after exact adopter authorization, plus synthetic unreflected/conflicting-choice cases and a bounded fresh-session exercise. Existing refers to the task, not inherited evidence of the new behavior. No customer originals or private business payloads are required. Source-only success does not complete this actual-use criterion or full onboarding intake.

### Verification Oracles

These are accepted expected outcomes for implementation, not passing results.

| ID | Input Or Interruption | Expected Outcome |
| --- | --- | --- |
| C01 | Follow-up select/withdraw while A is active/review/completed | A lifecycle/result bytes unchanged; only continuation changes |
| C02 | proposal/work/none/no selection/withdraw/damage | Distinct states; no new Work/intent |
| C03 | Crash before/after first current and before/after choice | No-record/verified null-current-without-choice is undecided; a durable choice creates pending; choices/selections with missing current are unavailable |
| C04 | Prior B, cancel after C choice is durable | Keep B meaning and C records; source result bytes unchanged |
| C05 | Cancel after C selection is durable, before current | Only the explicit cancellation sibling is valid; refuse C as current/parent |
| C06 | Crash after cancellation choice/selection is durable | Refuse original C resume; publish only the exact cancellation; refuse a second cancellation |
| C07 | Late cancellation after C current / past replay after B | Refuse pending cancellation; replay never rolls current back |
| C08 | Two actual processes requesting the same prior | Only one operation selected/pending; the later request is stale/non-pass and writes no new bytes |
| C09 | Source selection changes / valid B progress with equal purpose tuple / B intent ref or scope-set change / invalid mode-changing history | Source stale, normal B progress, target-purpose-changed and unavailable history remain distinct |
| C10 | Wrong home/kind/ref/alias/unknown/torn records or ambiguous orphan | Preserve and report unavailable/conflict; unclassifiable CONT blocks every official project writer including repair/detach; no automatic recovery or latest-wins |
| C11 | Continuation pending at any stage plus another official writer | Refuse new mutation except exact recovery/cancel/exact active-release repair; permit reads |
| C12 | Normal quota 256, last operation pending | Show exact used/remaining or unavailable; refuse new normal operation; permit that operation's publication and one cancellation |
| C13 | New-window receipt durable with no records / paired schema 5 detach prefix | Refuse old downgrade/writer/schema 4 or older recovery; preserve existing bytes and historical pairing |
| C14 | Same-window P→Q→P with Q-created records, repair/detach/clone/plain read | Preserve exact truth and meaning; pending states have separate refusal/exact recovery rules |
| C15 | A→B→A, long target chain, regenerated view, unstable reads | Bounded nonrecursive reading; canonical bytes unchanged; unstable means unavailable |
| C16 | New reader without hidden conversation | Accurately distinguish current follow-up, undecided, none, pending and next human decision |

The implementation plan distinguishes complete normal/parent-optimized regression, actual process/crash checks, exact-artifact lifecycle and a bounded fresh-reader exercise. Before a complete run, apply Maintaining's cumulative-risk/evidence-reuse assessment to establish necessity and the smallest sufficient checks. The proposed record/writer/lifecycle/recovery changes require a final complete run in each mode; use focused checks during iteration and do not repeat full runs solely for digests, candidate names or bounded prose edits. Retained predecessors need selected transition/refusal/recovery cases, not automatic full-suite runs. Share an execution only when inputs, commands, controls, modes and oracles are equivalent. Fix source/runtime/runner, ordered test collection and expected duration separately from stop/attempt limits before execution. Interruption, skip or unexplained results are not passes. Earlier regression evidence does not validate this new contract. A fresh agent's reading does not establish actual Owner comprehension or productivity.

## Acceptance And Remaining Qualification

On 2026-10-21 the Owner explicitly selected all three Driver recommendations: immutable history plus current, project-wide pending/integrity refusal, and 256 normal operations with visible used/remaining counts. The accepted input is the corrected post-R0 Draft (SHA-256 `189f9dfaced33f7fe6f712796fb09e7efd6ca712375a3126c4d4172803863a7b`) plus that quota-display amendment and this acceptance record. Exact recoverable decision/initial successor bytes and their hashes are identified in the single owning development record; the decision's own digest is stored outside its bytes.

This activates the named continuation-1 source successor deltas for the authorized implementation, preserving DR-0002/0004/0005 unaffected guarantees and the DR-0003/0006 procedures. The current installed delegation-1 profile remains unchanged until separately approved exact application. C03–C07, C09/C13 and all other acceptance oracles are implementation requirements, not already-passing evidence. Missing/damaged current has no general repair; preserve it for separately assessed exact recovery.

Before qualification, fix the exact retained delegation-1 predecessor and distinct continuation-1 P/Q artifacts. Before a live update, obtain target-specific exact application authorization and verify required preservation/recovery inputs. Result acceptance, Git publication and actual-use completion remain pending. The Owner-authorized record carries the approved scope, checks and cumulative time/attempt limits; its R1 and final evidence do not self-accept the result.

## Rationale

Reuse existing immutable publication and typed current selection instead of a second mutable-history storage pattern. Separate follow-up choice from accepted source results and target execution authority. A single project-wide pending/integrity boundary keeps initial recovery conditions auditable; its availability cost is explicit. A bounded 256-operation history and separate cancellation allowance bound per-Work verification/storage while keeping recovery possible. Display usage so the bound is visible before exhaustion. These choices favor the existing implementation primitives and bounded validation; they are not measured performance or usability claims.

## Consequences

The new continuation-1 window, paired lifecycle schema 5 and managed module require coordinated reader/writer/lifecycle/launcher and plain-auditor changes. New-window receipts establish a downgrade barrier; old historical record/schema meanings remain unchanged. One unresolved or damaged continuation can stop all official project mutations while reads remain available. Cancellation retains evidence and does not return normal-operation capacity. There is no automatic compaction/reset, relocation recovery, scheduler, new execution grant or general repair. Exact implementation and actual-use evidence, Owner result acceptance and adopter approval remain necessary.

## Reversal Cost

Before publication of new-window runtime/truth, a named Owner amendment can revise this accepted source design. Medium or higher after new-window receipts and continuation bytes are published, because old-reader, downgrade, preservation and recovery constraints apply. Do not hide migration cost by deleting records or silently changing their meaning.
