# Guided Intent Formation

Current surface: typed single-home intent records, machine commands and a read-only human view. The manual natural-language adapter guides the human through existing commands; it does not decide acceptance.

## Draft And Acceptance

An intent draft describes six facets: goal, scope, expected_outcome, acceptance_oracle, destination, and forbidden_scope. A facet is known with a value, or unknown/deferred with an owner. Statements distinguish fact, assumption, unknown, and human-decision. Material unresolved gaps prevent acceptance; an entirely unknown/deferred draft cannot grant Work authority.

Drafts form a single predecessor chain within one intent and retain one acceptance authority. New drafts do not automatically replace current intent. `hv2 intent draft` publishes a proposal. `hv2 intent prepare` creates an exact ticket binding the proposed revision and prerequisites. The human decides; `hv2 intent apply --confirm TOKEN` publishes acceptance and selection. Only the selected accepted draft is current.

All machine input uses canonical JSON from `--input FILE` or stdin. Prepare requires `intent_id`, `revision_ref`, `actor`, `reason`, `request_id`, and `observed_at`, with optional `document_refs` (omission means an empty list). Apply consumes the returned ticket, not its response envelope. See [General Work](GENERAL-WORK.md) for integration and [Reference](REFERENCE.md) for diagnostics.

## Work And Recovery

A Work references an accepted intent revision and shares its acceptance authority. A newer current intent makes acceptance of an old-bound result stale; human rebind or rejection is required. Draft/acceptance identifiers cannot be reused with different bytes. Historical exact replay does not move current backward.

Pending Work decision/selection blocks new intent mutation; pending intent acceptance/selection blocks other intent and Work mutation. Restore exact prerequisites and replay the original request after a supported interruption. Preserve torn records for investigation rather than deleting or rewriting them.

The independent source utility `classify-intent-entry --consequence consequential|non-consequential [--input FILE]` classifies supplied gaps without publishing authority. It is not a natural-language entry adapter or a measure of question quality.

## Human Review And Documents

Use `view intent ID` for the selected accepted intent and drafts; acceptance-ticket documents appear in `view confirmation`. Required intent document changes block all related start/checkpoint/submit-result/rework publication, acceptance and rebind until the human accepts a new intent. Then rebind the Work, submit a new result and obtain new human acceptance. Reject/revoke/cancel do not grant new authority and have different prerequisites. Explain this cost when proposing required references.
