# Checkout-1 Structural Contract

Current reading boundary: [DR-0004](../decisions/DR-0004-colvia-managed-entry-and-one-way-transition.md#entry-1-amendment-activation--2026-10-14) activated the exact entry-1 supplement and its named later First B1 permission clauses. The preparation labels below retain their historical meaning. The [Delegation-1 Successor Delta](#delegation-1-successor-delta) is the proposed replacement for the named clauses only; [DR-0005](../decisions/DR-0005-delegated-ordinary-work-acceptance.md) and its exact Owner activation record must make it effective. This source-only file is outside managed29.

Status: unactivated entry-1 successor candidate. The M3 version of this supplement retains its historical "Draft" label and SHA-256 `5797a6c2052c17f911551bdfd0205dcffb5e7c0dd2600dad5b64ae130a417944`; prepared 2026-10-07. [DR-0002](../decisions/DR-0002-checkout-1-contract-baseline.md) remains effective until separate successor qualification and activation. Source development only; this file is not part of the managed installation.

This supplement specifies the exact objects, references and graph constraints needed to interpret entry-1 and retained supported records without a private schema document. Read it when changing a record reader, writer or compatibility rule. The lifecycle and authority procedures remain in the contract set named by DR-0002. A structurally valid object alone never authorizes publication, acceptance, content application or recovery.

These clauses become normative only when the Owner activates their exact revision with the baseline. Until then they are a proposal checked against the current validators. The implementation is a comparison target, not an alternative source of authority. A disagreement must be reported and resolved explicitly; copying observed code into this document does not settle a policy change.

## Reading The Specification

Each `Name = {fields}` declaration below denotes the exact set of required object keys. `A + B` means the union of those sets, not nested objects. No unlisted key is allowed. A nullable key remains present with JSON `null`. A field described as an array is a JSON array; an object is a JSON object. Empty arrays are allowed unless a rule says otherwise. The declarations are notation for this document, not another runtime file format.

The field/type clauses, identity equalities and graph rules apply together. For example, a `Ref` may have a valid ID and digest but fail because the named record is missing, has different bytes or belongs to the wrong object. The tables distinguish constraints on saved history from checks that require the current project at publication time.

CLI convenience inputs and diagnostic output are not persisted records. Documented input defaults remain valid; they do not permit missing keys in the saved result. Scratch files, in-memory observations and an older standalone intent-entry classifier are not new authority families.

## Common Types And Exact Bytes

| Name | Definition |
| --- | --- |
| `Id` | ASCII full match `[a-zA-Z0-9][a-zA-Z0-9_-]{0,95}`; 1–96 characters |
| `Sha` | Exactly 64 lowercase hexadecimal characters |
| `Text` | A JSON string containing at least one non-whitespace character |
| `Bool` | JSON `true` or `false`; never integer 0/1 |
| `Int` | A JSON integer; a boolean is not an integer |
| `TextArray` | Array of `Text`; no implicit sorting or deduplication |
| `Path` | Literal nonempty relative NFC path with `/` separators; no empty, `.` or `..` components, backslash or NUL; no component whose casefold is `.git` or `.hrn` |
| `Window` | Candidate writer `entry-1`; readable earlier inventory history may name `human-1`, `worker-1`, `umbrella-1`, `planning-1` or `checkout-1`. `serial-1` and generation formats are not supported aliases |
| `Oid` | 40 or 64 lowercase hexadecimal characters |
| `ShortText` | String of at most 2,000 characters, normally non-whitespace; only fields expressly permitting empty text may be empty |

Persisted authority/planning JSON is UTF-8 without BOM or raw CR bytes, with sorted object keys, two-space indentation, unescaped Unicode and exactly one final LF. Nonfinite numbers, duplicate keys and malformed UTF-8 are refused. Canonical emission is the current Python JSON representation with `allow_nan=False`, `ensure_ascii=False`, `indent=2` and `sort_keys=True`, followed by LF. Readers of saved records compare the complete bytes with this emission; they do not normalize damaged history. The common input decoder also rejects a missing or repeated final LF, even when a convenience input does not require canonical key order/spacing.

The common JSON limits are 4 MiB, depth 128 and 1,024 integer digits. Root depth is 1; each contained value adds one. These are parsing ceilings, not a guarantee that a record of that size will satisfy its family or publication constraints. Candidate planning has the lower limits specified below. The advisory document reader's independent observation limit is not a record schema rule.

Let `C(x)` be the canonical bytes of `x`, `H(b)` lowercase SHA-256 of bytes `b`, and `D(x) = H(C(x))`. Digests of saved canonical records equal their raw-byte digests. An array's order is part of its digest. A digest detects different bytes; it does not preserve or authenticate them.

A `Path` set rejects duplicate paths, NFC/casefold aliases at every prefix, and a path that is also an ancestor of another file. Required sort orders below use UTF-8 byte order. Metadata inventory and lifecycle truth paths have their own namespaces; they are not project-content `Path` values.

Created/observed times are provenance strings, not current selectors or authority. Their structural type is `Text`; this specification introduces no clock-order or timestamp-format gate. Actor, owner, writer and acceptance-authority strings describe roles within the trusted local account; they are not authentication.

### Reference Shapes

```text
Ref = {id, sha256}
Object = {authority_home_id, kind, id}
IntentRef = {authority_home_id, kind, id, revision_ref, acceptance_ref, selection_ref}
DocumentRef = {path, sha256, role, required}
EvidenceRef = {path, sha256, required, verification}
```

- `Ref.id` is `Id`, `sha256` is `Sha`. The containing field determines the record family; IDs do not supply an alternative kind. Resolve both ID and complete digest.
- `Object.authority_home_id` and `id` are `Id`; `kind` is `intent` or `work`. A rule requiring a Work or intent narrows this enum.
- `IntentRef` is an intent `Object` plus three non-null `Ref` values. Its selection must publish exactly its revision and acceptance; the acceptance ticket targets that revision. The selection must already be in published intent history. New Work authority additionally requires the current accepted intent.
- `DocumentRef.path` and `EvidenceRef.path` are `Path`; `sha256` is `Sha`; `required` is `Bool`. Document roles are `decision`, `brief`, `plan`, `narrative`, `result`. Evidence verification is `worker-observed` or `control-required`; required evidence must be `control-required`.
- Each document-reference list and each evidence-reference list obeys the `Path`-set rule. Neither kind's list is silently reordered. Presence, live bytes and authority significance remain separate checks.

## Root Format And Record Locations

```text
Format = {record_type, format_version, authority_home_id, created_at, lineage}
FormatLineage = {parent, reason}
```

`Format` is `workspace-format`, `format_version` is integer 1, `authority_home_id` is `Id`, and `created_at` is `Text`. `lineage` is null or `FormatLineage`, whose parent is an `Object` and reason is `Text`. This lineage does not import another home or grant authority there.

| Location under `.hrn/` | Structural meaning |
| --- | --- |
| `format.json` | Immutable `Format` |
| `.gitignore` | Exact bytes `staging/` + LF + `locks/` + LF |
| `intents/<intent_id>/identity.json` | `IntentIdentity` matching the directory and root authority |
| `intents/<intent_id>/drafts/<revision_id>.json` | `IntentDraft1` or `IntentDraft2` |
| `intents/<intent_id>/acceptances/<acceptance_id>.json` | `IntentAcceptance` |
| `intents/<intent_id>/selections/<selection_id>.json` | `IntentSelection` |
| `intents/<intent_id>/current.json` | `IntentCurrent`, when published |
| `work/<work_id>/identity.json` | `WorkIdentity` matching the directory and root authority |
| `work/<work_id>/revisions/<record_id>.json` | `WorkRevision1` or `WorkRevision2` |
| `work/<work_id>/decisions/<record_id>.json` | `WorkDecision` |
| `work/<work_id>/selections/<record_id>.json` | `WorkSelection` |
| `work/<work_id>/results/<digest>.json` | `Manifest`, named by `D(manifest)` |
| `work/<work_id>/current.json` | `WorkCurrent`, when published |
| `planning/candidates.json` | `CandidateStore`, when a decision has been saved |
| `product/init-plan.json` | Original init `LifecyclePlan` |
| `product/binding.json` | Applied `Binding` |
| `product/receipts/<operation_id>.json` | Init/update/rollback `LifecycleReceipt` |
| `product/releases/<release_id>/inventory.json` | `Inventory` |
| `product/releases/<release_id>/payload/…` | Exact managed members for that inventory window |
| `detached.json` | Detach `LifecycleReceipt`, including its exact plan |
| `staging/`, `locks/` | Scratch; neither current authority nor recovery proof |

Root members are exactly the named top-level files/directories above when present. Unknown members, wrong file types and unsupported versions are preserved and non-writable under the existing diagnostic rules. Missing empty intent/Work directories after Git transport mean no records, not invented identities. A partial object is not a completed empty object. Object and record filename spellings must match their IDs; case aliases are rejected within their collection. A file's order in the directory does not select current.

## Content Trees And Manifests

```text
TreeEntry = {path, mode, sha256, size_bytes}
Tree = {policy_version, ignore_fingerprint, entries, sha256}
Change = {path, pre, post}
Manifest = {record_type, schema_version, base, result, changes, base_commit, candidate_commit, base_retention_ref, candidate_retention_ref}
```

| Shape | Fields and constraints |
| --- | --- |
| `TreeEntry` | `path: Path`, `mode: "100644"` or `"100755"`, `sha256: Sha`, `size_bytes: Int >= 0` |
| `Tree` | `policy_version: Int = 1`, `ignore_fingerprint: Sha`, `entries: TreeEntry[]` in canonical path order; `sha256 = D(the Tree without its sha256 key)` |
| `Change` | `path: Path`; `pre` and `post` are a `TreeEntry` or null. Their paths equal the change path. Both sides cannot be null in an actual change |
| `Manifest` | `record_type: "result-manifest"`, `schema_version: Int = 1`; `base` and `result` are `Tree`; `changes: Change[]` is their exact sorted difference |

Tree entries obey the `Path`-set rule. The two trees have the same ignore fingerprint. Every changed path is in the revision's exact file scope; scope does not reduce snapshot membership. In Git mode the snapshot includes tracked files even if ignored and non-ignored untracked files, excluding authority/runtime metadata as documented. Non-Git uses the documented regular-file observation. Whole-content and ignore-policy rules are in [General Work](../GENERAL-WORK.md).

All four manifest provenance fields are null for local execution. For isolated-worker execution, both commits are `Oid` and both retention refs are named full `refs/heads/…` or `refs/tags/…` refs. Their spelling disallows whitespace/control characters, `~ ^ : ? * [ \\`, `..`, `@{`, empty components, components beginning with `.`, and components ending with `.` or `.lock`. Publication additionally verifies that the retained refs/objects actually provide the stated exact commits; spelling alone is insufficient.

`changes` is derived from the union of base/result paths, retaining only unequal entries in UTF-8 path order. Additions have null pre; deletions have null post; edits retain both. The manifest has no separate ID field. Its `Ref` has `id == sha256 == D(manifest)`.

## Work Shapes And State

```text
WorkBase = {record_type, schema_version, authority_home_id, work_id}
WorkProvenance = {record_id, observed_at, observed_scope, unavailable_scope}
WorkIdentity = WorkBase + {work_type, created_at, acceptance_authority, lineage}
WorkRevision1 = WorkBase + WorkProvenance + {author, operation, expected_prior_selection, intent_ref, scope, document_refs, evidence_refs, result_refs, progress, next_action, relations, rebind_from, execution_context}
WorkRevision2 = WorkRevision1 + {umbrella_evidence}
WorkDecision = WorkBase + {record_id, confirmation}
WorkSelection = WorkBase + WorkProvenance + {parent_selection_ref, revision_ref, decision_ref, operation_id}
WorkCurrent = WorkBase + {selection_ref}
ResultRefs = {manifest}
Execution = {mode, attempt_id}
Relation = {relation, target}
```

All Work records carry `authority_home_id: Id` and `work_id: Id`. `record_type` identifies the named family: `work-identity`, `work-revision`, `work-decision`, `work-selection` or `work-current`. `schema_version` is integer 1 except `WorkRevision2`, which uses integer 2. The revision version does not change identity, selection, decision or current versions.

| Shape or field group | Types and constraints |
| --- | --- |
| Work identity | `work_type`, `created_at`, `acceptance_authority`: `Text`; `lineage`: null or `Object`. Identity is immutable |
| Work provenance | `record_id: Id`, `observed_at: Text`, `observed_scope` and `unavailable_scope`: `TextArray`. Observation lists are not approval or automatic pass/fail predicates |
| Revision description | `author`, `next_action`: `Text`; `scope: Path[]`; `document_refs: DocumentRef[]`; `evidence_refs: EvidenceRef[]` |
| Revision operation | `start`, `checkpoint`, `submit-result`, `rework`, `rebind` |
| Revision progress | `planned`, `active`, `review`, `rework`; `review` if and only if operation is `submit-result`. An agent revision never declares completed |
| Revision binding | `expected_prior_selection: Ref or null`; `intent_ref: IntentRef` in the same home; `result_refs: ResultRefs` containing non-null manifest `Ref` |
| Revision execution | `execution_context: Execution`; `mode` is `local` or `isolated-worktree`; `attempt_id: Id` |
| Revision relations | `relations: Relation[]`; kind is `parent`, `depends_on` or `continues`; target is a same-home Work `Object` other than self. No duplicate `(relation, target.id)` pair |
| Revision rebind | `rebind_from: IntentRef or null`; non-null if and only if operation is `rebind` |
| Work decision | `record_id: Id` derived below; `confirmation: Ticket` naming exactly this Work |
| Work selection | `parent_selection_ref: Ref or null`, `revision_ref: Ref`, `decision_ref: Ref or null`, `operation_id: Id` |
| Work current | `selection_ref: Ref` naming an existing exact selection |

### Work History Constraints

All records in an object graph match its immutable home/Work identity. Every ref resolves against the indicated family, including records not selected as current. Manifests have their digest as filename. A revision's execution mode is local if and only if its manifest commit provenance is null.

A start revision has null prior selection; every other revision has a resolvable prior. A revision other than `submit-result` has equal base/result trees and no changes. Worker start/rebind uses one commit for both manifest commits. Worker `rework` is unsupported; its recovery path is human baseline refresh.

When a prior selection exists:

- Execution mode is unchanged. A selected schema-2 parent cannot downgrade to schema 1. Except for a rebind, a schema-2 revision retains the exact selected parent child evidence.
- The new base ignore fingerprint equals the prior result's. Checkpoint/rework keeps the prior result tree; it cannot absorb unreviewed content. A worker checkpoint cannot follow a submitted result to absorb it.
- A completed Work requires human revoke before another revision. A rejected/revoked result requires rework or rebind; a local rework requires one of those outcomes.
- Rebind's `rebind_from` equals the previous intent ref. An unchanged-intent rebind is allowed only in worker mode, preserves exact scope and remains active. Other operations preserve the intent ref.
- Submission follows a selected non-submitted baseline whose outcome is not review/rejected/revoked, and its manifest base equals that baseline's result.

Every relation from every retained proposal resolves to an existing Work. The union of all relation kinds over all revisions must be acyclic; checking only current selections is insufficient. Ordinary relations do not create scheduling, prerequisite completion or automatic parent acceptance. The stricter optional parent rules below are separate.

### Work Decisions And Selections

A Work ticket's actor equals the immutable acceptance authority. Its intent/document/evidence refs and execution mode equal the target revision. Reusing a request ID with different ticket bytes is invalid. The expected selection is non-null for a Work decision even though the shared Ticket shape permits null for the first intent acceptance.

| Action | Required relation to selected history |
| --- | --- |
| `accept` / ordinary `reject` | Target is the undecided selected `submit-result` revision in review; `supersedes_decision_ref` is null |
| Cancellation `reject` | Supersedes one open `accept` with null supersedes, targeting the same prior selection and revision. One cancellation successor only; the original accept must have no durable selection |
| `rebind` | Targets a proposed rebind whose expected prior equals the ticket's expected selection; supersedes is null |
| `revoke` | Prior outcome is completed; supersedes equals that selection's accepted decision |

A decision's ID is derived from its entire ticket, including actor, reason, request ID and observations. A selection with a decision publishes exactly that decision's expected selection, target revision and request ID. One decision cannot be selected twice. An agent selection has null decision ref, cannot select a rebind, matches the revision's expected prior, and has an operation ID that does not collide with human request IDs in that Work. Selection operation IDs are unique within the Work.

Selections form one connected chain from a null parent, with no fork or cycle. Current points into that chain. At most one selection may be durable beyond current. Otherwise pending decisions target the current selection and consist of one decision or an accept plus its sole cancellation successor; incomparable pending decisions are invalid. A pending selection and unresolved decision cannot coexist. A durable selection for a cancelled decision is invalid.

The selected decision maps `accept` to completed, `reject` to rejected and `revoke` to revoked; rebind uses its target revision's progress. Without a decision, the outcome is the revision's progress. Without current, the Work is empty even when proposals exist. Orphan revisions are preserved and do not select themselves.

## Confirmation Ticket

```text
Ticket = {record_type, schema_version, authority_home_id, action, actor, object, target_revision_ref, expected_selection_ref, intent_ref, product_binding_ref, document_refs, evidence_refs, execution_mode, supersedes_decision_ref, reason, request_id, observed_at, target_fingerprint}
```

The type is `confirmation-ticket`, schema integer 1. `authority_home_id` and `request_id` are `Id`; `actor`, `reason` and `observed_at` are `Text`; `target_fingerprint` is `Sha`. `object` is an `Object` in the ticket's home. `target_revision_ref` and `product_binding_ref` are non-null `Ref`; `expected_selection_ref` and `supersedes_decision_ref` are `Ref` or null. Reference arrays use the common shapes.

For an intent, `action` is only `accept`, and `intent_ref`, `execution_mode` and `supersedes_decision_ref` are null. For a Work, `action` is `accept`, `reject`, `rebind` or `revoke`, `intent_ref` is `IntentRef`, and `execution_mode` is `local` or `isolated-worktree`. Graph and mutation checks narrow these choices further; the common shape alone does not permit every combination.

A prepared ticket is an external exact input, not a saved decision. It has no independent accepted flag. Confirmation tokens detect exact input changes; they do not prove the human's identity or consent.

## Intent Shapes And Selection

```text
IntentBase = {record_type, schema_version, authority_home_id, intent_id}
IntentIdentity = IntentBase
IntentDraft1 = IntentBase + {acceptance_authority, actor, facets, gaps, statements, observed_at, prior_revision_ref, revision_id, route, sequence}
IntentDraft2 = IntentDraft1 + {composition}
IntentAcceptance = IntentBase + {acceptance_id, confirmation}
IntentSelection = IntentBase + {acceptance_ref, prior_selection_ref, revision_ref, selection_id}
IntentCurrent = IntentBase + {selection_ref}
Facets = {acceptance_oracle, destination, expected_outcome, forbidden_scope, goal, scope}
KnownFacet = {status, value}
UnresolvedFacet = {owner, status}
Gap = {depends_on, gap_id, material, owner, status}
Statement = {kind, owner, text}
```

All intent records match the root home and intent directory, with `authority_home_id` and `intent_id` as `Id`. Types are `intent-identity`, `intent-draft`, `intent-acceptance`, `intent-selection`, `intent-current`. Schema is integer 1 except `IntentDraft2`, which is integer 2; only it adds non-null `composition`.

| Field group | Types and constraints |
| --- | --- |
| Draft identity/history | `revision_id: Id`, `sequence: Int > 0`, `prior_revision_ref: Ref or null` |
| Draft declarations | `acceptance_authority`, `actor`, `observed_at`: `Text`; `facets: Facets`; `gaps: Gap[]`; `statements: Statement[]` |
| Known facet | `status: "known"`; value is a JSON value other than null, empty string or empty object. Empty array is allowed only for `forbidden_scope`; other values are not implicitly restricted to prose strings |
| Unresolved facet | `status: "unknown"` or `"deferred"`; `owner: Text`. No `value` key |
| Gap | `gap_id: Id`, `material: Bool`, `owner: Text`, `status: "resolved"` or `"unresolved"`, `depends_on: Id[]` |
| Statement | `kind`: `assumption`, `fact`, `human-decision` or `unknown`; `owner`, `text`: `Text` |
| Acceptance | `acceptance_id: Id` derived below; `confirmation: Ticket` naming this intent |
| Selection | `selection_id: Id`; `acceptance_ref`, `revision_ref`: non-null `Ref`; `prior_selection_ref: Ref or null` |
| Current | `selection_ref: Ref` naming an exact intent selection |

The draft history has unique positive sequences, one root at 1, and each draft's sequence is its exact prior's plus 1. Acceptance authority remains constant across drafts. Gaps have unique IDs; dependency arrays have no duplicates, resolve to known gaps and form an acyclic graph. The route is derived: unresolved material gaps depending directly on another unresolved material gap select `dependency-ordered-clarification`; other unresolved material gaps select `bounded-clarification`; no unresolved material gaps select `direct-entry`.

Acceptance requires at least one known facet, no unresolved material gap, and a ticket actor equal to the draft's acceptance authority. It does not require all six facets to be known. The draft's role must satisfy the parent-role constraints below. Intent request IDs are unique in the acceptance history.

Selections form one connected nonforking acyclic chain. Each publishes one unique acceptance and exactly its ticket's revision/prior-selection refs. Current names a selection in that chain. At most one unselected acceptance or one selection beyond current may be pending, not both. A pending acceptance's expected selection equals current, or null if no current exists. A later draft does not automatically replace the accepted selection; sequence is draft ancestry, not accepted-current authority.

## Optional Direct-Child Parent

```text
Composition = {parent, required_children}
RequiredChild = {work, intent}
UmbrellaEvidence = {children, integration_document}
ChildEvidence = {work, intent_ref, selection_ref, revision_ref, decision_ref, manifest_ref}
```

Composition's parent is a same-home Work `Object`; each required child has a Work `Object` and an intent `Object` in that home. The required-child array is nonempty, sorted by Work ID in UTF-8 order, has no duplicate/case-alias Work ID and excludes the parent itself under casefold comparison. A schema-2 Work must be the parent named by its exact accepted intent composition.

Each evidence child has a same-home Work `Object`, `IntentRef` and four non-null `Ref` values. `manifest_ref.id == manifest_ref.sha256`. Evidence rows are sorted and unique by Work ID under the same rule. `integration_document` is null for a baseline and a `Path` for a submitted result. Baseline child evidence may be a subset of declared children; submitted evidence contains exactly all required children.

Each captured chain must already be published: Work selection → accept decision → submitted revision → manifest and exact accepted intent. All equalities between these refs are checked, not inferred from IDs. The child revision declares exactly this one parent, has schema 1, and its bound draft has no composition. Cross-home and nested parents are unsupported.

Historical validation checks the sealed chain and its publication position. Current readiness additionally requires the captured child Work to remain current/completed with no pending publication, and its exact intent to remain current without pending acceptance/selection. Later child drift does not erase a historical parent completion.

Start/rebind captures the currently eligible children, including a partial set when others are unavailable. Non-rebind successors retain that exact baseline capture. Parent result readiness requires all declared children still matching, a required result-role document ref at `integration_document`, and at least one required control-required evidence ref. Runtime/live bytes, the parent's own content result and human integration judgment are additional conditions; the reference predicate does not accept the parent.

After an accepted intent becomes a parent, later acceptance cannot remove composition or change parent identity. After a selected Work becomes schema 2, it cannot become ordinary. These checks follow accepted/selected ancestry, not orphan drafts. Changed child evidence requires explicit human rebind and subsequent verification under the existing procedure.

## Candidate Planning Store

```text
CandidateRequest = {record_type, schema_version, authority_home_id, request_id, candidate_id, action, expected_sha256, writer, owner_statement, reason, observed_at, payload}
CandidateStore = {record_type, schema_version, authority_home_id, candidates, selected, decisions}
CandidateEvent = {request, before, after}
CandidateState = {disposition, selected}
CandidateRow = {title, purpose, expected_effect, related_candidates, disposition, reason, resume_condition, links}
CandidateLink = {authority_home_id, kind, id, revision_ref}
CandidateTextPayload = {title, purpose, expected_effect, related_candidates}
CandidateDeferPayload = {resume_condition}
CandidateResumePayload = {condition_observation}
CandidateLinkPayload = {target}
CandidateDispositionPayload = {disposition, target}
EmptyPayload = {}
```

The request type is `candidate-request`, store type is `candidate-planning`, and each schema version is integer 1. The store's home equals the root. Request home, request ID and candidate ID are `Id`; `expected_sha256` is `Sha` or null; writer, Owner statement, reason and observed time are `ShortText`. They are recorded declarations, not authenticated identity.

Actions are `add`, `amend`, `select`, `defer`, `resume`, `link`, `disposition`, `reopen`. Add/amend use `CandidateTextPayload`: title/purpose/expected effect are `ShortText`, related candidates are at most 100 unique IDs. Defer uses `CandidateDeferPayload`, whose short string may be empty to mean unspecified. Resume uses `CandidateResumePayload` with nonempty `ShortText`. Link uses `CandidateLinkPayload`. Disposition uses `CandidateDispositionPayload`, with disposition `absorbed` and a link target, or `rejected` and null target. Select/reopen use `EmptyPayload`.

A `CandidateLink` is a same-home intent or Work `Object` plus a non-null revision `Ref`. It is an observation of an existing object; it is not the full accepted `IntentRef` and grants no Work authority. At mutation, the revision must be the object's current selected/accepted revision. If both kinds are linked, their intent identity/revision must agree with the linked Work's current intent binding. Old stored links can become historical or unavailable without fabricating a new live relation.

### Planning Fold And Limits

`candidates` is an object keyed by candidate ID; its values have exactly `CandidateRow` fields. Rows and `selected` are derived by replaying `decisions` from an empty map and null selection. A row has the narrative payload, disposition `open`/`deferred`/`absorbed`/`rejected`, latest request reason, a short resume-condition string (initially empty), and a link array. Links have at most one entry per kind and are ordered by kind; updating a link may change its revision but cannot silently replace a different object's ID.

Each event contains a complete request and exact before/after states. A state's disposition is null only before an add; selected is null or a candidate ID. Request IDs are case-insensitively unique. The first request has null expected digest; all later requests have a digest. The history fold checks that presence rule and exact transition/projection equality, not a reconstructed cryptographic digest chain. A new mutation separately compares expected digest with the actual whole stored bytes.

| Action | Fold rule |
| --- | --- |
| Add | New ID without a case alias; related IDs already exist and are not self. Starts open with empty condition/links |
| Amend | Existing candidate; related IDs exist and are not self. Updates narrative fields without changing disposition or selection |
| Select | Open, not already selected and no Work link; replaces the single recorded selection |
| Defer | Open and no Work link; sets deferred/condition and clears selection if this candidate was selected |
| Resume | Deferred and no Work link; sets open without replacing another selection |
| Reopen | Rejected and no Work link; sets open. Absorbed candidates cannot reopen |
| Link / disposition | Candidate is open or deferred. Disposition clears its selection; a non-null target obeys same-home and same-object-per-kind rules |

Every successful action records its reason. Resume/reopen do not implicitly select or erase the stored condition. Amend does not revive a terminal candidate. Related-candidate edges are references, not a dependency DAG or a scheduler.

Limits are 100 candidates, 1,000 decisions and 1 MiB canonical stored bytes. Counts do not grant deletion/compaction authority. Absent store means empty planning; a present store must contain at least one decision. The planning directory admits only `candidates.json`. Publication replaces the whole file atomically, so interruption yields old or new complete bytes; a prior request may already be saved. Installed-runtime and pending-graph admission are checked before exact retry. Unknown/conflicted/damaged input is preserved, not reset to empty.

## Product Inventory And Lifecycle

```text
ReleaseRef = {id, sha256, inventory_id}
InventoryEntry = {path, sha256, size_bytes}
Inventory = {record_type, schema_version, inventory_id, entries}
Binding = {record_type, schema_version, authority_home_id, active_release, prior_release, operation_id}
TruthRef = {path, sha256}
LifecyclePlan = {record_type, schema_version, operation_id, action, target_fingerprint, authority_home_id, expected_binding_ref, candidate_release, format_sha256, truth_refs, remove, preserve, created_at}
LifecycleReceipt = {record_type, schema_version, operation_id, plan, prior_binding_ref, result_binding_ref}
InitRequest = {format, plan}
RepairRequest = {plan, files, backup, product_observation}
RepairFile = {path, before, after}
FileObservation = {sha256, size_bytes, mode}
```

A release ref has `sha256: Sha`, `inventory_id: Window` and `id = "product-release-" + sha256[0:24]`, with the full digest retained. `Inventory` is `release-inventory`, schema integer 1, with a window and an array of inventory entries. Each entry has a managed relative path, `Sha` and nonnegative integer size. Entry coverage and order equal the exact managed set; the release digest is `D(inventory)`. Prefix collisions never replace the full-digest check.

### Exact Managed Membership

Historical planning-1/checkout-1 membership is the following literal 29 paths, sorted by UTF-8 bytes in an inventory. Umbrella-1 uses this set without `src/hv2ref/candidates.py` (28). Human-1/worker-1 use that set without `src/hv2ref/umbrella.py` (27). Earlier receipts retain their own window's exact set; no new source-only development document is added implicitly.

```text
.gitignore
AGENTS.md
CLAUDE.md
PRODUCT-CAPABILITIES.json
README.md
adapters/harness-v2-work/SKILL.md
docs/CONCEPTS.md
docs/GENERAL-WORK.md
docs/GETTING-STARTED.md
docs/GUIDED-INTENT-FORMATION.md
docs/MAINTAINING.md
docs/MANUAL-OPERATION.md
docs/OPERATIONS.md
docs/README.md
docs/REFERENCE.md
docs/SECURITY-AND-SUPPORT.md
docs/WORKSPACE-CONTRACT.md
hv2
src/hv2ref/__init__.py
src/hv2ref/candidates.py
src/hv2ref/cli.py
src/hv2ref/errors.py
src/hv2ref/intent.py
src/hv2ref/jsonio.py
src/hv2ref/product.py
src/hv2ref/umbrella.py
src/hv2ref/view.py
src/hv2ref/work.py
src/hv2ref/workspace.py
```

Current entry-1 membership replaces only `hv2` with `colvia` and `adapters/harness-v2-work/SKILL.md` with `adapters/colvia-work/SKILL.md` in membership; its actual ordered inventory is UTF-8 sorted and still has 29 paths. Retain the old lists literally in readers, independently of the new set. A retained release directory contains exactly `inventory.json` plus its window's payload paths and their required ancestor directories. Every payload size/digest and the launcher's declared window must agree with its inventory. Files not in this set cannot silently enter the release.

### Plans, Bindings And Receipts

A binding is `product-binding`, schema integer 1, with `authority_home_id: Id`, `operation_id: Id`, an active `ReleaseRef` and a prior `ReleaseRef` or null. Its reference ID is operation ID; its digest covers the complete binding.

A plan is `lifecycle-plan`. Its operation/home IDs are `Id`, created time is `Text`, and target/format digests are `Sha`. The format digest binds the exact format; target fingerprint is `H(os.fsencode(the validated absolute target path))`. `truth_refs` is a sorted unique array of `TruthRef`; remove/preserve are arrays of `InventoryEntry`. Their action-specific values are mandatory:

| Action | Version | Binding / candidate | Truth and file lists |
| --- | --- | --- | --- |
| Init | 1 | Expected binding null; candidate release non-null | `truth_refs`, `remove`, `preserve` all empty. `InitRequest.format` and plan format/home/target agree |
| Update / rollback | Paired 2 for entry-1; paired 1 historical | Expected binding non-null; candidate entry-1 for new writes | Exact observed truth; preserve empty. Same-entry remove empty; admitted checkout-1→entry-1 update removes exactly verified old `hv2` |
| Repair | 1 | Expected binding non-null; candidate equals exact active release | Exact observed truth, allowing valid Work/intent pending; remove and preserve are the same list of original damaged files that exist |
| Detach | 3 for new writes; paired 1/2 readable as history | Expected binding non-null; candidate null | Exact truth and exact managed removal / authority preservation inventories described below |

A `TruthRef` has a path relative to `.hrn/` and `Sha`. Paths are `planning/candidates.json` or paths under `intents/` / `work/` with at least three components, no empty/dot/parent components or backslash. The actual list binds every saved truth file, not merely current pointers. Names are unique and sorted by UTF-8 bytes. A valid-looking path alone does not prove the file belongs to a valid object graph.

A receipt is `lifecycle-receipt` with operation ID, complete plan and two `Ref`-or-null binding refs. Its version is 1 for init/repair and historical switches, 2 for entry-1 switches, and exactly the embedded detach plan's version (paired 1/2/3) for detach. Mixed pairs and bool/non-integer versions are refused. Outer and plan operation IDs agree. The whole receipt must equal the canonical expected record:

- Init result binding has candidate active, null prior and this operation ID; receipt prior is null and result names that binding.
- Switch result binding has candidate active, previous active as prior and this operation ID; receipt prior names the exact previous binding and result names the new binding.
- Repair receipt prior and result both equal the unchanged expected binding. It is external backup evidence, not a product-history authority node.
- Detach receipt prior equals expected binding; result is null. The embedded plan remains interpretable after product files are removed.

Product receipts form a complete nonforking chain from the init receipt; orphan/cyclic receipts, case aliases and a receipt inconsistent with its reconstructed binding are refused. Applied binding bytes match exactly either the chain tip or its single pending predecessor. A receipt alone is not applied completion. Every retained release is verified against its named window; launcher bytes must be among the permitted active/pending bytes under the lifecycle procedure.

Window rank is human-1 < worker-1 < umbrella-1 < planning-1 < checkout-1 < entry-1; history cannot downgrade. Rollback names exactly the prior release recorded by the applied binding, still subject to that rank rule. Current writers switch only to entry-1 from the exact allowlisted checkout-1 predecessor or entry-1. The full old release reference and entry-specific receipt/retirement rules are in [Workspace Contract](../WORKSPACE-CONTRACT.md#entry-1-admission-and-publication); a matching window alone does not admit a predecessor. Earlier readable windows do not gain current write support. Planning records require an applied planning-capable binding. Runtime provenance and the first durable receipt barrier remain as specified in [Workspace Contract](../WORKSPACE-CONTRACT.md).

### Exact Repair Request

`RepairRequest.plan` is the repair plan above. `files` is a nonempty, unique sorted array of `RepairFile`; `backup` is the canonical absolute path of a new external directory; `product_observation` maps observed product-relative file names to raw digests. The destination must be physically outside source and target, including alias/containment checks. Recovery requires that exact previously created backup instead of a new destination.

A repair file is only the launcher or a file in the exact active managed release. `before` is null if missing, otherwise `FileObservation`; `after` is non-null `FileObservation`. The observation has `sha256: Sha`, `size_bytes: Int >= 0`, `mode: Int` in `0..4095` (octal `07777`). After bytes are exactly the candidate bytes. Launcher after mode is octal `0755`; another file uses the previous mode masked with `0777`, or `0644` if missing. Before and after differ. An unlisted active file must already be correct.

The plan's preservation lists include each non-null before image as path/digest/size, in repair-file order. Product observations outside repair paths remain exact; an included path's original digest also agrees. The backup contains exact `request.json`, every required original byte file, then `receipt.json` after successful repair. Missing originals cannot be reconstructed from repaired bytes. No binding/authority change, pending product lifecycle or inactive-release damage is repaired by this operation.

### Detach Plan And Receipt

Removal entries are sorted, unique under casefold, relative metadata paths with exact raw digests/sizes. They comprise the launcher, product init plan, binding, every lifecycle receipt, and each retained release's exact inventory/payload membership. At least one release and receipt exist. The detach operation ID does not alias a removed receipt ID. Each release ID matches its removed inventory digest prefix; the removed binding digest equals the expected binding ref. The launcher digest/size matches a removed release's payload launcher: `colvia` for schema 3, historical `hv2` for paired 1/2. Schema 3 checks the retired-entry collision after exact prefix validation, including when no active binding remains; do not add that occupant to removal or infer an active product. See [diagnostic context](../REFERENCE.md#entry-1-diagnostic-context).

Preserve entries are exactly `.hrn/format.json`, `.hrn/.gitignore` and `.hrn/` plus every truth-ref path. Format and ignore entries match their exact canonical bytes, and truth digests agree. Entries do not authorize arbitrary project-file deletion.

The durable detach receipt equals the expected paired-version receipt before removal. Remaining files must match an exact suffix of the removal order: launcher first, then remaining paths in canonical order. Directories are removed only after files, deepest first and then UTF-8 order. Unknown, changed or out-of-order remnants remain unavailable and preserved. New writes require schema 3 and exact original request/target; paired schema 1/2 history is read-only here and requires its retained old source for recovery.

## Derived Identities And Tokens

| Item | Exact derivation |
| --- | --- |
| Saved record ref | `{id: its family ID, sha256: D(record)}`; no digest field is removed unless specifically stated |
| Tree digest | `D(tree without the sha256 key)` |
| Manifest filename/ref | `D(manifest)` for filename stem and both ref ID/digest |
| Work decision ID | `"decision-" + D(ticket)` |
| Human Work selection ID emitted by the writer | `"selection-" + D(ticket)`; operation ID is ticket request ID |
| Intent acceptance ID | `"acceptance-" + D(ticket)` |
| Intent selection ID emitted by the writer | `"selection-" + D(ticket)` |
| Agent Work revision/selection/operation IDs | Explicit caller-supplied `Id` values with immutable-retry/collision rules; no timestamp-derived selection |
| Intent draft revision ID | Caller-supplied `Id`; sequence/prior constraints do not derive the ID |
| Product release ID | `"product-release-" + D(inventory)[0:24]`; full digest remains in `ReleaseRef` |
| Binding ref ID / receipt filename | Plan operation ID; binding and receipt bytes still have distinct complete digests |
| Work / intent confirmation token | First 16 hex characters of `D(ticket)` |
| Init confirmation token | First 16 hex characters of `D({format, plan})` |
| Update / rollback / detach token | First 16 hex characters of `D(plan)` |
| Repair token | First 16 hex characters of `D(complete RepairRequest)` |
| Candidate CAS digest | `H(saved candidates.json bytes)`; null only when no store exists |

The writers emit deterministic human selection IDs above. The graph readers validate selection IDs as `Id`, exact references and chain membership; they do not impose that derivation as an additional reader rejection. Decision/intent-acceptance IDs do have the explicit ticket-digest equality check. This distinction preserves current reading behavior without authorizing manual record edits or alternative writers.

## Reader, Publication And Change Boundaries

The structure/graph clauses do not replace the mutation checks: verified current bound runtime, physical target topology, shared cooperating-writer guard, pending matrix, current acceptance authority/intent, required references, exact content/retained Git objects and publication-time revalidation. Reads may validate historical refs while new writes require current ones. A historical exact replay never rolls current backward.

An inventory window, root format version and individual record schema version are independent. A changed accepted shape or reference/state meaning is a contract change even when a test still passes. Assess reader/writer compatibility under [Maintaining](../MAINTAINING.md#inventory-window-compatibility); do not silently reinterpret old bytes, update a managed path set or turn an implementation rename into a semantic change.

For changes to these structures, update the relevant declaration and its graph/identity clauses together, compare them with the corresponding validator and writer, and retain the exact accepted revision through the baseline decision. Unknown obligations or disagreement block the affected adoption scope. This Draft does not enable continuation records proposed separately in DR-0001.

## Correspondence And Verification Scope

| Clauses | Source comparison locations |
| --- | --- |
| Common encoding | `src/hv2ref/jsonio.py`: canonical emission and bounded decoder |
| Format/init | `src/hv2ref/workspace.py`: format, plan and root validation |
| Trees, manifests, Work, tickets and cross-Work relations | `src/hv2ref/work.py`: content/record validators, Work graph, collection guard and writer construction |
| Intent shapes and ancestry | `src/hv2ref/intent.py`: persisted intent graph and acceptance/selection construction, not the standalone classifier |
| Parent composition/evidence | `src/hv2ref/umbrella.py`: structural validation, history/current predicates and baseline binding |
| Candidate shapes/fold | `src/hv2ref/candidates.py`: request, transition, store, live-link and mutation checks |
| Product inventory/lifecycle | `src/hv2ref/product.py`: membership, plan/receipt construction, chain verification, repair and detach |

These locators support maintenance; their names do not delegate normative authority to code. The baseline record identifies this supplement's exact proposed bytes and records the actual checks and remaining limits. Document/validator correspondence is not a new full runtime qualification, proof of every historical assertion, or evidence of real adopter use.


## Delegation-1 Successor Delta

This proposed delta changes Common Types (`Window`), Intent Shapes And Selection, the ordinary Work Decisions And Selections actor predicate, and Product Inventory And Lifecycle's window/version/current-writer clauses. It adds the following exact rules; all other identity, content, graph, reference, encoding, concurrency and recovery guarantees remain as specified above and in the effective contract. This is a proposal for exact activation, not a new source of runtime authority.

### Intent Draft And Grant Shape

```text
IntentDraft3 = IntentDraft1 + {acceptance_delegation}
AcceptanceDelegation = {action, delegate_actor, execution_mode, scope, work}
```

`IntentDraft3.schema_version` is integer 3; `acceptance_delegation` is a required non-null `AcceptanceDelegation`. It has no `composition`. Saved schema-1 and schema-2 drafts retain their exact old keys and Owner-only acceptance behavior; their absent grant is interpreted as no grant, not rewritten into their saved bytes. Intent identity, acceptance, selection and current records stay schema 1. Draft history/authority, required inputs and exact Owner acceptance gates remain unchanged.

| Grant field | Exact constraint |
| --- | --- |
| `action` | Literal `accept` |
| `delegate_actor` | `Id` (the 1–96-character ASCII grammar above), distinct from the Owner string; if the Owner string is ASCII, case-insensitive equality is also forbidden. Existing Owner/legacy actor fields retain `Text`; this does not globally narrow them |
| `execution_mode` | Literal `isolated-worktree` |
| `work` | Exact `Object` with `kind: work` and the same authority home |
| `scope` | Nonempty array of `Path` satisfying the existing path-set constraints; Work scope equality compares sets, without changing the saved array's digest/order |

A grant binds the accepted draft's exact revision ID and digest, not an independent registry. Re-acceptance or reselection of the same draft does not create a fresh grant identity. Presence of any saved or prospective schema-3 draft requires a verified delegation-1 writer, including Owner writes, replay and a later no-grant draft. Historical graph reading and live writer admission are separate checks; repeat writer admission under the existing guard.

### Ordinary Work Actor And Consumption

The only non-Owner action allowed by this delta is one exact ordinary isolated-worker `accept`. Resolve the Work revision's complete intent reference through its verified intent graph. Work and intent Owner identities agree; the grant's qualified Work, scope set, mode and delegate match the exact ticket and revision. The accepted Work revision is schema 1 without composition; the delegated ticket has no supersedes decision. Every revision in its selected ancestry is schema 1. An ordinary child may qualify; a parent/composition revision or mixed composition ancestry cannot.

Consumption key: `(authority_home_id, work_id, intent_id, draft_revision_id, draft_sha256)`. Every lawful durable delegated accept decision consumes that key, including an orphan decision, a pending accept later cancelled, or a completed result later revoked. One key cannot support another delegated decision. A selected revoke of an accept for the same key bars later delegated acceptance even when that revoked accept was Owner-issued. Traverse the validated selection ancestry; a new request, reselection or baseline-refresh rebind cannot erase it. Earlier lawful history does not become invalid merely because a later revoke exists. A new draft changes the key only through existing lawful acceptance/rebind rules; completed Work does not reopen.

The existing ticket/decision stores the actual actor, and exact recovery retains it. Owner acceptance remains available under existing gates. Intent acceptance, rebind, reject, revoke, cancellation, lifecycle, Git and parent acceptance remain human-authorized; this delta grants none of them to the delegate. A valid delegated ordinary child may satisfy the existing parent's readiness, without transferring parent authority or creating a transitive grant. Serial control writes and the prohibition on concurrent same-Work content editing remain. Actor strings provide no caller authentication or immutable-payload enforcement.

### Window And Lifecycle Pairing

Append `delegation-1` at rank 6 after `entry-1`. Root format, inventory and binding remain schema 1; launcher remains `colvia`; exact managed membership equals the existing entry-1 29 paths. Source-only documents, including this supplement, do not join that inventory.

| Action | New plan / receipt pair | Unchanged action-specific boundary |
| --- | --- | --- |
| Init | 4 / 4; candidate delegation-1 | Null binding, exact format and empty truth/remove/preserve |
| Update / rollback | 4 / 4; candidate delegation-1 | Existing binding/truth checks, empty remove/preserve, same-window prior-release rollback only |
| Repair | 4 / 4; exact active delegation-1 | Existing request fields, exact damaged-file before/after evidence and external backup, unchanged binding |
| Detach | 4 / 4 | Existing exact removal/preservation order, prefix checks, receipt and `colvia` collision protection |

The only admitted cross-window update begins at the exact entry-1 predecessor inventory SHA-256 `2216a2634eb3fa5d6a8bfa7c7d4847b29fb2443ba7b367156c15b15ddb5a17e0`, not any entry-1 release. Preserve old source and original input for old pending recovery. The first durable schema-4 switch receipt establishes the one-way boundary before schema-3 intent publication; old writers must refuse even in the late-lock case. Return to entry-1 after that boundary is unsupported. Same-window rollback is permitted only when the exact retained prior release and all current history satisfy the existing checks.

Retained init/repair schema 1, switch pairs 1/1 and 2/2, and detach pairs 1/1, 2/2 and 3/3 retain their historical meaning. Current mutation uses 4/4; a version is an integer, never boolean, and mixed/unknown/action-incompatible pairs are refused. Schema 4 is not admission for a future window. Saved detach history validates its exact pair and removed membership. Once all payloads are removed, identical entry-1/delegation-1 membership cannot independently prove old active-window provenance; writer admission enforces that boundary before deletion. Do not infer a reconstructible release identity from that history.

The current [Workspace Contract](../WORKSPACE-CONTRACT.md#delegation-1-implementation-candidate) and [General Work](../GENERAL-WORK.md#delegation-1-implementation-candidate) carry the corresponding candidate lifecycle and authority clauses. Static comparison with unchanged validators/writers supports correspondence only; the owning A record distinguishes inherited runtime assertions, newly executed artifact/consumer checks and unavailable coverage. No runtime, real-adopter or authentication qualification arises from this document edit.
