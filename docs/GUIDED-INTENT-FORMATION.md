# Guided Intent Formation

Continuation-1 profile; see [authorization and qualification](README.md#continuation-1).

Current surface: typed single-home intent records, machine commands and a read-only human view. The manual natural-language adapter guides the human through existing commands; it does not decide acceptance.

## Draft And Acceptance

An intent draft describes six facets: goal, scope, expected_outcome, acceptance_oracle, destination, and forbidden_scope. A facet is known with a value, or unknown/deferred with an owner. Statements distinguish fact, assumption, unknown, and human-decision. Material unresolved gaps prevent acceptance; an entirely unknown/deferred draft cannot grant Work authority.

Drafts form a single predecessor chain within one intent and retain one acceptance authority. New drafts do not automatically replace current intent. `colvia intent draft` publishes a proposal. `colvia intent prepare` creates an exact ticket binding the proposed revision and prerequisites. The human decides; `colvia intent apply --confirm TOKEN` publishes acceptance and selection. Only the selected accepted draft is current.

All machine input uses canonical JSON from `--input FILE` or stdin. Prepare requires `intent_id`, `revision_ref`, `actor`, `reason`, `request_id`, and `observed_at`, with optional `document_refs` (omission means an empty list). Apply consumes the returned ticket, not its response envelope. See [General Work](GENERAL-WORK.md) for integration and [Reference](REFERENCE.md) for diagnostics.

## Work And Recovery

A Work references an accepted intent revision and shares its acceptance authority. A newer current intent makes acceptance of an old-bound result stale; human rebind or rejection is required. Draft/acceptance identifiers cannot be reused with different bytes. Historical exact replay does not move current backward.

Pending Work decision/selection blocks new intent mutation; pending intent acceptance/selection blocks other intent and Work mutation. Restore exact prerequisites and replay the original request after a supported interruption. Preserve torn records for investigation rather than deleting or rewriting them.

The independent source utility `classify-intent-entry --consequence consequential|non-consequential [--input FILE]` classifies supplied gaps without publishing authority. It is not a natural-language entry adapter or a measure of question quality.

## Human Review And Documents

Use `view intent ID` for the selected accepted intent and drafts; acceptance-ticket documents appear in `view confirmation`. Required intent document changes block all related start/checkpoint/submit-result/rework publication, acceptance and rebind until the human accepts a new intent. Then rebind the Work, submit a new result and obtain new human acceptance. Reject/revoke/cancel do not grant new authority and have different prerequisites. Explain this cost when proposing required references.

## Optional Parent Composition

A parent intent draft uses schema_version2 and adds exactly `composition={parent, required_children}`. Each child row declares a qualified Work and intent identity in the same home; exact accepted revisions are captured later by the parent Work. The original six facets still hold purpose, scope, constraints and integration criteria. An ordinary request stays schema1.

Once a composition draft is accepted, later acceptance for that intent must preserve composition and its parent identity. Unaccepted drafts do not lock the role. Changing the required set uses a new accepted draft and human parent rebind, not editing accepted bytes. IDs can be declared before publication but are not reserved. Nested/cross-home umbrella is unsupported; see [General Work](GENERAL-WORK.md#direct-child-umbrella).

## Delegation-1 Implementation Candidate

This retained heading explains the delegation-1 behavior inherited by continuation-1. For current lifecycle commands and authorization boundaries, follow [Continuation-1](README.md#continuation-1). Historical versions keep their original meaning. A verified installation, document or passing check does not prove human authorization, host authentication or general readiness.

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
