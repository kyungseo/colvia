# Guided Intent Formation

Delegation-1 profile; see [authorization and qualification](README.md#delegation-1-implementation-candidate).

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

This section describes the `delegation-1` profile in the verified installed release. Its heading is retained for existing links and does not indicate activation status. Where this document elsewhere describes `entry-1` as current, this section governs new operations. Preserve the stated limits for historical records. Installing or reading these files does not prove Owner authorization, human authentication, source-contract activation, runtime qualification or adopter readiness.

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

The delegate uses the ASCII record-ID grammar and must differ from the Owner exactly and after ASCII case-folding. The Work is in the same authority home. Scope is a nonempty duplicate-free set of valid paths; order does not grant a different scope. The Owner accepts the exact draft bytes through the existing intent acceptance operation. Draft publication alone grants nothing, but its presence requires a delegation-1 writer for later mutations of that history.

Before acceptance, explain the exact delegate, Work, scope and one-use boundary. The grant does not accept an intent, authorize execution beyond scope, authenticate a caller, or grant reject/revoke/rebind, lifecycle, Git, parent or continuation authority. Preserve required document and currentness rules. Every writer and recovery still validates the full history under the existing control guard.
