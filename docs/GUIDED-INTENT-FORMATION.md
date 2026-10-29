# Guided Intent Formation

Continuation-1 profile; see [authorization and qualification](README.md#continuation-1).

An intent is stored as a typed record in the single project home. Machine commands create these records and record acceptance; a read-only view presents them for human review. The natural-language adapter guides the human through those commands, while acceptance remains the human’s decision.

## Draft And Acceptance

An intent draft describes six facets: goal, scope, expected_outcome, acceptance_oracle, destination, and forbidden_scope. A facet is known with a value, or unknown/deferred with an owner. Statements distinguish fact, assumption, unknown, and human-decision. Material unresolved gaps prevent acceptance; an entirely unknown/deferred draft cannot grant Work authority.

Drafts form a single predecessor chain within one intent and retain one acceptance authority. New drafts do not automatically replace current intent. `colvia intent draft` publishes a proposal. `colvia intent prepare` creates an exact ticket binding the proposed revision and prerequisites. The human decides; `colvia intent apply --confirm TOKEN` publishes acceptance and selection. Only the selected accepted draft is current.

All machine input uses canonical JSON from `--input FILE` or stdin. Prepare requires `intent_id`, `revision_ref`, `actor`, `reason`, `request_id`, and `observed_at`, with optional `document_refs` (omission means an empty list). Apply consumes the returned ticket, not its response envelope. See [General Work](GENERAL-WORK.md) for integration and [Reference](REFERENCE.md) for diagnostics.

## Ordinary Draft Input

Use this schema-1 input for one ordinary Work without parent composition or delegated acceptance. The agent prepares the JSON from the human's goal and actual observations; the human decides acceptance. Schema 2 and 3 add the separate fields described below and are not defaults for this example.

Every field shown here is required. This synthetic example proposes changing one file; its names, time, actors and text are examples, not facts about your project or authorization to run it.

```json
{
  "record_type": "intent-draft",
  "schema_version": 1,
  "authority_home_id": "example-home",
  "intent_id": "example-intent",
  "revision_id": "draft-1",
  "sequence": 1,
  "prior_revision_ref": null,
  "actor": "agent",
  "acceptance_authority": "owner",
  "observed_at": "2026-01-01T00:00:00Z",
  "facets": {
    "goal": {"status": "known", "value": "Change the agreed sample line."},
    "scope": {"status": "known", "value": ["sample.txt"]},
    "expected_outcome": {"status": "known", "value": "sample.txt contains after followed by one LF."},
    "acceptance_oracle": {"status": "known", "value": "Observe UTF-8 bytes after plus LF and no other content changes against the whole-project baseline."},
    "destination": {"status": "known", "value": "This installed synthetic project."},
    "forbidden_scope": {"status": "known", "value": "Other project files, runtime files and authority records outside official commands."}
  },
  "gaps": [],
  "statements": [],
  "route": "direct-entry"
}
```

Use the installed home's actual `authority_home_id`. Persisted IDs use ASCII `[A-Za-z0-9][A-Za-z0-9_-]{0,95}`; case aliases and reusing an ID for changed bytes are refused. Keep one acceptance authority throughout an intent. The first draft has `sequence: 1` and `prior_revision_ref: null`; a later draft references the preceding draft as `{id, sha256}` and increments its sequence by one.

`facets` has exactly the six keys in the example. A known facet has exactly `status` and `value`; its value cannot be null, an empty string or object, or an empty list except for `forbidden_scope`. An unknown or deferred facet instead has exactly `status` and a nonempty `owner`, without `value`. Describe uncertainty rather than filling it with an invented decision.

Each gap has exactly `gap_id`, `depends_on` (an array of gap IDs), `material` (boolean), `owner`, and `status` (`resolved` or `unresolved`). IDs and dependencies are unique, all dependencies exist, and the graph has no cycles. Each statement has exactly `kind` (`fact`, `assumption`, `unknown` or `human-decision`), `owner`, and `text`. Use `route: "direct-entry"` when no material gap is unresolved; otherwise use `dependency-ordered-clarification` when an unresolved material gap depends on another unresolved material gap, or `bounded-clarification` when none does. Unresolved material gaps still block acceptance.

### From Draft To Accepted Intent

Serialize input as canonical JSON: UTF-8 without BOM, sorted object keys, two-space indentation, unescaped Unicode, no non-finite numbers, and one final LF. Do not send a PowerShell text pipeline that changes these bytes. Keep input and returned output in the authorized durable location outside project content.

After authorized `intent draft --input FILE`, the JSON response is a graph. Its `drafts` map holds the exact published draft under its `revision_id`. Define `H(value)` as the lowercase SHA-256 of the canonical JSON bytes above. Prepare with this complete object, substituting actual values:

```python
prepare_input = {
    "intent_id": draft["intent_id"],
    "revision_ref": {"id": draft["revision_id"], "sha256": H(draft)},
    "actor": draft["acceptance_authority"],
    "reason": owner_reason,
    "request_id": new_request_id,
    "observed_at": observed_at,
    "document_refs": document_refs,
}
```

Here `draft` is the exact record returned by publication, not a reconstructed summary. `document_refs` is an explicitly chosen list (possibly empty) of `{path, sha256, role, required}` with actual file-byte digests. Supported roles are `decision`, `brief`, `plan`, `narrative`, and `result`. Explain the existing required-reference cost before choosing `required: true`; it is not a harmless documentation toggle.

Run `intent prepare --input FILE`, review its ticket, and obtain the human decision. Save only the returned `ticket` object as canonical JSON; `intent apply --input TICKET_FILE --confirm TOKEN` consumes that object and the same response's `confirm_token`. Neither the actor string nor the token supplies authorization. An apply failure requires preserving the original inputs and inspecting pending state, not automatically preparing a replacement.

A successful apply returns an intent graph `G`. For a later Work, take `selection_ref = G["current"]["selection_ref"]` and `S = G["selections"][selection_ref["id"]]`. The accepted `intent_ref` has exactly `authority_home_id`, `kind: "intent"`, `id` (the intent ID), `revision_ref: S["revision_ref"]`, `acceptance_ref: S["acceptance_ref"]`, and `selection_ref`. Preserve those returned digests. This is selected acceptance, not the newest draft by filename or timestamp. Continue with [Ordinary Local Work Input](GENERAL-WORK.md#ordinary-local-work-input).

## Work And Recovery

A Work references an accepted intent revision and shares its acceptance authority. A newer current intent makes acceptance of an old-bound result stale; human rebind or rejection is required. Draft/acceptance identifiers cannot be reused with different bytes. Historical exact replay does not move current backward.

Pending Work decision/selection blocks new intent mutation; pending intent acceptance/selection blocks other intent and Work mutation. Restore exact prerequisites and replay the original request after a supported interruption. Preserve torn records for investigation rather than deleting or rewriting them.

The independent source utility `classify-intent-entry --consequence consequential|non-consequential [--input FILE]` classifies gaps supplied as input and publishes no authority records. It accepts structured input rather than a natural-language request, and does not evaluate question quality.

## Human Review And Documents

Use `view intent ID` for the selected accepted intent and drafts; acceptance-ticket documents appear in `view confirmation`. Required intent document changes block all related start/checkpoint/submit-result/rework publication, acceptance and rebind until the human accepts a new intent. Then rebind the Work, submit a new result and obtain new human acceptance. Reject/revoke/cancel do not grant new authority and have different prerequisites. Explain this cost when proposing required references.

## Optional Parent Composition

A parent intent draft uses schema_version2 and adds exactly `composition={parent, required_children}`. Each child row declares a qualified Work and intent identity in the same home; exact accepted revisions are captured later by the parent Work. The original six facets still hold purpose, scope, constraints and integration criteria. An ordinary request stays schema1.

Once a composition draft is accepted, later acceptance for that intent must preserve composition and its parent identity. Unaccepted drafts do not lock the role. Changing the required set uses a new accepted draft and human parent rebind, not editing accepted bytes. IDs can be declared before publication but are not reserved. Nested/cross-home umbrella is unsupported; see [General Work](GENERAL-WORK.md#direct-child-umbrella).

## Delegation-1 Implementation Candidate

Continuation-1 inherits the delegation-1 behavior described below. Follow [Continuation-1](README.md#continuation-1) for current lifecycle commands and authorization requirements. Historical versions retain their original meaning. Human authorization comes from the Owner’s actual decision; host authentication and general readiness require their own evidence.

An ordinary draft may use schema 3 with exactly the schema-1 ordinary fields plus a non-null `acceptance_delegation`. Schema 1 remains the no-grant ordinary format; schema 2 remains composition. A schema-3 draft cannot also contain composition, and null does not mean no grant.

The grant has exactly these fields:

```json
{
  "delegate_actor": "agent-acceptor",
  "action": "accept",
  "work": {"authority_home_id": "home-example", "kind": "work", "id": "work-example"},
  "execution_mode": "isolated-worktree",
  "scope": ["src/example.py"]
}
```

The delegate uses the ASCII record-ID grammar and must differ from the Owner exactly and after ASCII case-folding. The Work is in the same authority home. Scope is a nonempty duplicate-free set of valid paths; order does not grant a different scope. The Owner accepts the exact draft bytes through the existing intent acceptance operation. Draft publication alone grants nothing, but its presence requires a verified current continuation-1 writer for later mutations; the historical delegation-1 gate remains part of retained-source behavior.

Before acceptance, explain the exact delegate, Work, scope and one-use boundary. The grant does not accept an intent, authorize execution beyond scope, authenticate a caller, or grant reject/revoke/rebind, lifecycle, Git, parent or continuation authority. Preserve required document and currentness rules. Every writer and recovery still validates the full history under the existing control guard.

A continuation proposal is input to the next intent discussion, not an accepted intent. A reference to an existing Work preserves its selected intent snapshot; that Work's current authorization and prerequisites still govern execution. No ordinary-accept grant authorizes selecting, withdrawing or cancelling a continuation.
