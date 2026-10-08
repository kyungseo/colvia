---
id: DR-0001
status: Draft
date: 2026-10-07
---

# DR-0001: Work Continuation Selection And Recovery

## Question

How can a Work retain its selected follow-up, an explicit decision to have no follow-up, and withdrawal without changing its accepted result or lifecycle, while allowing interrupted publication to be recovered or cancelled and read accurately in a new session?

## Decision

## Context And Scope

This is a proposed contract, not implemented support. Obligations below constrain the proposal; they do not authorize a writer or an implementation. The current product uses `checkout-1` and the contracts indexed in [Documentation Index](../README.md). This Draft neither activates `continuation-1` nor changes existing authority. Follow [Contributing](../../CONTRIBUTING.md) for decision acceptance.

[General Work](../GENERAL-WORK.md) defines Work and intent records, [Reference](../REFERENCE.md) describes candidate planning and project document references, and [Workspace Contract](../WORKSPACE-CONTRACT.md), [Operations](../OPERATIONS.md) and [Maintaining](../MAINTAINING.md) govern runtime and lifecycle changes. A current Work selection identifies its lifecycle revision; a candidate selection identifies a project planning choice. Neither is a dedicated follow-up choice for one Work.

A static source comparison found that the Work reader admits known record directories, pending guards enumerate existing Work/intent operations, and lifecycle truth collection first validates the Work graph. Therefore adding a continuation directory requires coordinated reader, guard and lifecycle changes. This is a design dependency, not a reproduced product defect. The proposed records, limits and recovery rules have no implementation or execution evidence.

## Options Considered

| Option | Benefit | Cost Or Limit | Proposed Disposition |
| --- | --- | --- | --- |
| Put the follow-up in a Work revision/current | Reuse existing paths | Couples follow-up changes to source lifecycle and acceptance records | Do not select |
| Reuse project candidate selection | No new store | Project planning and a Work-specific follow-up have different lifetimes and authority | Do not select |
| One mutable history/current file per Work | Simplifies the atomic publication boundary | Adds a separate bounded storage pattern and rewrites a potentially large file | Retain as an alternative |
| Immutable choices/selections and a separate current per Work | Matches existing immutable publication, exact references and explicit current | Requires cancellation branches, pending rules and a new reader window | Preferred proposal |

## Proposed Contract

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

The first approved apply prepares known empty directories and durably publishes an initial continuation current with `selection_ref:null` before writing a choice. Initialization is part of that same approved apply. Read and prepare create no directory or current. An absent continuation or known empty directories with no records mean undecided. If any record exists but current is missing, the state is `unavailable-current`; do not infer a normal first pending operation or select the latest selection. Initial null current and a missing current file are different states.

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

Proposed canonical-byte limits are 24 KiB per ticket, 32 KiB per choice, 4 KiB each per selection/current and depth 16. There are at most 16 document refs; reject duplicate or aliased paths. Refuse an operation before its first write if the total-byte limit is exceeded, even when individual fields fit.

Each Work allows at most 256 normal operations (`select` plus `withdraw`) and at most one cancellation per normal operation. Choices and selections therefore each have at most 512 records, and all canonical continuation files total at most 20 MiB. Even 512 × (32 KiB + 4 KiB) + 4 KiB current fits within 20 MiB. These are proposed bounds for the first implementation, not measured performance guarantees. At 256 normal operations, refuse a new normal operation but allow the existing exact publication, its one cancellation and that cancellation's publication. A separate normal quota must not block cancellation. Check prospective record sizes/counts before durable writes; do not delete history to recover capacity.

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

`target_fingerprint` hashes the resolved path bytes of the actual control target, without storing the path itself. Actor matches the source Work identity's acceptance authority. `owner_statement` describes the human request for that choice or cancellation. Preview shows the full ticket SHA, a confirmation token of its first 16 hex characters, source, prior, choice and limits. Apply receives the full ticket and a separate token and validates the full canonical bytes and bound conditions. A token alone is not human authorization. Keep the full ticket in the choice so staging is not the only copy of approval evidence.

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

First validate current and every choice/selection for exact kind, ID, hash, same home/Work and parent relation. Build an acyclic selection chain from one root with null parent. Current's ancestors are selected history. Never reconstruct current from directory order or timestamps.

A normal choice binds one expected continuation prior. Two competing normal choices at that prior conflict. One cancellation choice that exactly supersedes the original normal choice is the explicit exception below. Each choice has only the selection with its exact deterministic ID. Choices/selections outside current and its ancestors must belong to one pending operation or a validated cancellation relation. Preserve unexplained orphans/forks and report conflict.

A cancellation choice may supersede only a normal choice. Its source and prior match the original ticket, and current must still be that prior when cancellation is first published. The original selection may be durable but must not yet be selected history. Once cancellation is durable, classify the original selection as unselected retained evidence and exclude it from competing active children. Refuse a graph that uses that original selection as current or another selection's parent. Refuse cancellation of a cancellation, two different cancellations, or pending cancellation of a normal choice already among current's ancestors.

Derive effective choice from current's selection: `select` yields ticket.choice, `withdraw` yields undecided, and `cancel-pending` yields the parent's effective choice, or undecided for a null parent. Cancellation current advances while preserving the prior choice's source/target evidence and meaning. The cancellation ticket's source does not renew the prior choice's validity. Walk the bounded chain iteratively; do not recursively read the target Work's continuation.

### Publication, Retry And Pending Cancellation

Under the same project writer guard, validate runtime, authority, current source/continuation, live required refs, pending state and limits. Then prepare initial current if needed → durably write choice → revalidate → durably write selection → final revalidation → atomic current replacement and directory sync. Keep existing exact immutable writes and fsync/F_FULLFSYNC conditions; scratch belongs in `.hrn/staging`. Do not overwrite different bytes at an immutable path. Release the guard and handle scratch failures on every path; deleting records is not recovery.

| Observed State | Allowed Action | Invalid Interpretation |
| --- | --- | --- |
| No records / known empty initialization prefix | New preview and approved apply | Empty planning means explicit none |
| Initial current=null, normal choice durable | Original exact publication or explicit pending cancellation | Choice alone confirms selection |
| Prior B current, C choice durable | Recover C or cancel that exact operation | Delete B or automatically make C current |
| C selection durable, prior B still current | Reuse the exact selection and publish current, or explicitly cancel | A selection file proves completion |
| Cancellation choice durable, cancellation current not yet published | Exact publication of that same cancellation only | Resume C, introduce a competing choice or cancel the cancellation |
| Cancellation current published | Keep B's effective meaning; allow a new normal preview | Reset B's stale conditions or delete C bytes |
| Normal current published | Same ticket is historical/current replay; new request binds current prior | Late retry promotes a past choice to current |
| Records exist but current is missing/damaged | Read as unavailable; separately assess recovery using a trusted exact retained copy | Guess latest selection or ignore damage through ordinary cancel |
| Torn immutable file, unknown member or invalid refs | Preserve, non-writable | Exact retry overwrites invalid bytes |

Normal recovery requires the original source/current continuation/binding, required documents and the target's exact selection-time observations to match again. If the target progresses before the original choice is published, the pending operation is stale; do not create a new ticket automatically. Explicitly cancel it before preparing a new choice. Normal progress after a completed selection follows the next section instead.

Prepare cancellation only while the original choice is unresolved, current prior is unchanged and original records validate. A changed live source/target selection or proposal document alone must not block cancellation. Verify the original source refs' historical integrity, source identity authority, continuation prior, safe control paths and active product binding. Official lifecycle changes are forbidden during pending, so binding must equal the original ticket. Pending recovery/cancellation after a move or clone changes the live fingerprint and is outside initial support; do not rebind it arbitrarily.

### Shared Writer And Freshness Rules

- Begin a new continuation operation only when no existing Work, intent, lifecycle or continuation operation is pending. Exact recovery/cancellation of that same operation is an explicit exception.
- Continuation pending blocks all official mutations except its exact recovery/cancellation and existing exact active-release repair that changes neither binding nor truth. Reads remain allowed. Do not automatically undo user edits to project files.
- The writer guard serializes cooperating control writers. Workers can submit proposals but cannot write official continuation. It does not make Git merges, external file edits or concurrent independent-clone control atomic.
- With no pending operation, allow source lifecycle changes. A continuation choice must not permanently block completion or revocation. If the recorded source selection differs from the current one, the choice is historical/stale.
- Fresh select/withdraw requires a source snapshot exactly matching current Work selection/revision and valid historical accepted intent refs. Show any difference between those historical intent refs and current intent separately; it grants no new execution authority.
- On first selection, a Work target snapshot must match current selection/revision, and its bound accepted intent must currently be valid. Later checkpoint/review/completed progress within the same intent refs and scope does not automatically invalidate the choice. Changed intent refs or scope yield `target-purpose-changed`. Show target rejection, revocation or pending as limits on execution; do not automatically reselect.
- Show required document drift as changed selection evidence and do not use it to justify execution. Show unobserved/changed optional refs too, without deleting the choice for that reason alone. Distinguish integrity failure from ordinary live drift.

This read model does not compute execution authority as a scheduler. Check the current human request and the target Work/intent's existing authorization. Do not add a separate continuation approval merely to repeat approval of the same already authorized action.

### Reader Window And Lifecycle Boundary

The proposed new `inventory_id` is `continuation-1`. Keep root format 1, existing Work revision schemas 1/2 and intent/Work authority meanings; add continuation record schema 1. Do not silently extend checkout-1, which does not support continuation records.

| Boundary | Proposal |
| --- | --- |
| New init | Install continuation-1 with explicit approval; do not overwrite an existing root with a new init because its reader is missing |
| Existing installation | Initially support an explicit checkout-1 → continuation-1 update only; older active windows first take their existing supported transition |
| Downgrade barrier | From the first durable continuation-1 lifecycle receipt, refuse downgrade to checkout-1 or older, even with no continuation records |
| Rollback within the new window | Only between releases with P→Q→P evidence that P reads and preserves Q-created continuation |
| History reader | Retain existing human-1/worker-1/umbrella-1/planning-1/checkout-1 history; add no unknown/serial-1 support |
| Old source/writer | Preserve and remain non-writable when the new inventory/receipt or continuation subtree is not understood; never bypass the new window through an old writer |
| Detach | Write both new-window plan and receipt as schema 3; new readers preserve old schema 1/2 meaning, but new-source writes/recovery use schema 3 only; recover old detach prefixes with the exact retained old source |
| Clone / detached plain read | Track and preserve choices, selections and current as project truth; do not compare historical ticket fingerprints to the clone's path, but require a live fingerprint match for pending apply |

Detach schema 3 closes the reader window by version; it does not authorize different removal targets, order or preservation obligations. Bind continuation in the new plan's truth_refs/preserve set. Even after new detach has removed product receipts, old checkout-1 source must not continue that prefix as schema 2. Do not delete unknown/legacy receipts or edit versions to recover.

Change and verify all consumers together: Work tree reader/truth visibility; Work/intent/candidate pending guards; current bound-runtime admission; source/installed CLI; status/doctor/projection; update/rollback/repair/detach; launcher allowlist/managed inventory; and the plain auditor. The implementation plan must name new modules and exact managed paths, preserving the old window's 29-file membership as historical membership. A window name or matching digest alone does not prove compatibility.

### Projection Contract

Present Work lifecycle and continuation separately. At minimum show source Work identity/current lifecycle, recorded continuation selection/ref, effective kind/content, selection-time source/target evidence, live source/target state, pending/cancellation state and the next human decision. Damage is unavailable; source drift is historical/stale; changed documents or target purpose have specific reasons. Do not collapse undecided, none and damage into one label.

Examples: “A completed / follow-up B selected / B in review / B result acceptance needed”; “A completed / prepare a follow-up intent proposal selected / no target Work”; “A completed / no follow-up decided”; “A completed / C selection publication interrupted / prior B retained / exact C recovery or cancellation needed”. Distinguish already authorized follow-up execution from a new approval requirement.

Projection is derived stdout, with no new authoritative cache. Deleting or regenerating it does not change canonical records. Deleting continuation current damages authority; it is not projection cleanup. Reuse the bounded current graph without recursively expanding target continuations. Exceeded data limits, unstable observation or integrity failure end with explicit unavailable.

### Verification Oracles

These are expected outcomes to fix before implementation, not passing results.

| ID | Input Or Interruption | Expected Outcome |
| --- | --- | --- |
| C01 | Follow-up select/withdraw while A is active/review/completed | A lifecycle/result bytes unchanged; only continuation changes |
| C02 | proposal/work/none/no selection/withdraw/damage | Distinct states; no new Work/intent |
| C03 | Crash before/after first current and before/after choice | Distinguish no-record prefix from null-current pending; records plus missing current is unavailable |
| C04 | Prior B, cancel after C choice is durable | Keep B meaning and C records; source result bytes unchanged |
| C05 | Cancel after C selection is durable, before current | Only the explicit cancellation sibling is valid; refuse C as current/parent |
| C06 | Crash after cancellation choice/selection is durable | Refuse original C resume; publish only the exact cancellation; refuse a second cancellation |
| C07 | Late cancellation after C current / past replay after B | Refuse pending cancellation; replay never rolls current back |
| C08 | Two actual processes requesting the same prior | Only one operation selected/pending; the later request is stale/non-pass and writes no new bytes |
| C09 | Source selection changes / B progresses normally / B intent or scope changes | Source stale, normal B progress and purpose-change review remain distinct |
| C10 | Wrong home/kind/ref/alias/unknown/torn records or ambiguous orphan | Preserve and report unavailable/conflict; no automatic recovery or latest-wins |
| C11 | Continuation pending at any stage plus another official writer | Refuse new mutation except exact recovery/cancel/exact active-release repair; permit reads |
| C12 | Normal quota 256, last operation pending | Refuse new normal operation; permit that operation's publication and one cancellation |
| C13 | New-window receipt durable with no records / schema 3 detach prefix | Refuse old downgrade/writer/schema 2 recovery; preserve existing bytes |
| C14 | Same-window P→Q→P with Q-created records, repair/detach/clone/plain read | Preserve exact truth and meaning; pending states have separate refusal/exact recovery rules |
| C15 | A→B→A, long target chain, regenerated view, unstable reads | Bounded nonrecursive reading; canonical bytes unchanged; unstable means unavailable |
| C16 | New reader without hidden conversation | Accurately distinguish current follow-up, undecided, none, pending and next human decision |

The implementation plan distinguishes complete normal/parent-optimized regression, actual process/crash checks, exact-artifact lifecycle and a bounded fresh-reader exercise. Fix source/runtime/runner, ordered test collection and time/attempt budgets before execution. Interruption, skip or unexplained results are not passes. Earlier regression evidence does not validate this new contract. A fresh agent's reading does not establish actual Owner comprehension or productivity.

## Open Points

1. The Owner must choose whether to adopt the immutable structure, proposal/work/none/withdraw meanings, cancellation that preserves prior meaning and the cost of project-wide pending blocking. The mutable single-file alternative remains open.
2. Contract review must resolve initial null current, cancellation graph branches and separate exact recovery of missing/damaged current. Adding a general repair mechanism is not currently recommended.
3. `continuation-1`, detach schema 3, source/target freshness and the 256-operation/byte/depth limits are concrete Draft values. Owner review or counterexamples may change them; they are not measured support limits.
4. Module/CLI layout, managed membership and budgets belong to the implementation plan. Revise the contract first if a counterexample shows a consumer cannot meet it. Decision acceptance does not authorize code changes.
5. Before this Draft can become effective, identify and accept the affected source contract set, its exact revisions and replacement scope. Current Work, intent, candidate, lifecycle and reader contracts remain effective meanwhile. This proposal has not completed that contract adoption or established implementation authority.

## Promotion Conditions

- The Owner explicitly selects the proposed meaning, authority, pending, window and limits, and resolves the remaining contract questions.
- Review at least C03–C07 interruption/cancellation/loss states and C09/C13 freshness/old-reader boundaries for one unambiguous expected outcome. An independent reviewer or reviewer CLI needs a defined and authorized scope.
- Fix the Draft values and corrections, fill Decision/Rationale/Consequences, and obtain Owner acceptance of the exact revision and scope. Accept the affected source contract revisions and their explicit activation with this contract-changing decision. Do not promote it while a required prerequisite remains missing.
- Implementation requires its own authorized scope, checks and time/attempt bounds. Contract acceptance, implementation results, Git publication and actual adopter application remain separate decisions.

## Rationale

## Consequences

## Reversal Cost

Low while this is only a Draft: revise it or mark it Dropped with a reason. Medium or higher after new-window receipts and continuation bytes are published, because old-reader, downgrade, preservation and recovery constraints apply. Do not hide migration cost by deleting records or silently changing their meaning.
