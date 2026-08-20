# Guided Intent Formation Contract

This contract defines the bounded private `A-minimal` vertical for turning a consequential request into an exact-revision,
human-accepted intent record. It implements artifact semantics only. It does not implement an interactive question engine,
judge clarification quality, link an intent to a managed item, or make adopter, public, default, or runtime-support claims.

## Entry Boundary

The caller or human declares consequence. The product does not infer it.

| Entry | Artifact | Route |
| --- | --- | --- |
| Non-consequential | none | `non-consequential` |
| Consequential, no unresolved material gap | one draft | `direct-entry` |
| Consequential, independent unresolved material gaps | one draft | `bounded-clarification` |
| Consequential, unresolved material dependency edges | one draft | `dependency-ordered-clarification` |

For a well-formed consequential request, the request payload is revision 1. Guided Intent Formation adds one whole-revision
acceptance; it does not add a draft-approval-start triple ceremony. Questions remain in the human or agent layer. The durable
route is derived only from the declared gap graph included in the accepted revision.

## Authority Home And Tree

`.harness-v2-intents/` is separate from the existing `.harness-v2/` exact-tree authority home.

```text
.harness-v2-intents/
  authority.json
  <intent-id>/
    identity.json
    drafts/revision-0001.json
    acceptances/acceptance-0001.json
    selection-assertions/selection-0001.json
    current-selection.json
```

The stable identity is `(authority_home_id, intent_id)`. Paths, timestamps, directory order, and the numerically largest file do
not select current authority. Drafts, acceptances, and selection assertions are immutable canonical JSON. The current selector
is switched last and points to an exact `{id, sha256}` selection reference.

The separate root is required because Generation 1 treats extra `.harness-v2/` entries as degraded and Generation 2 requires
an exact state tree. Guided intent files never enter `.harness-v2/items`, `attempts`, or existing receipts.

## REQ-002 Field Contract

Every draft preserves `actor`, `acceptance_authority`, and these exact facets:

| REQ-002 field | Stored key |
| --- | --- |
| actor | `actor` plus `acceptance_authority` |
| goal | `facets.goal` |
| scope | `facets.scope` |
| forbidden scope | `facets.forbidden_scope` |
| expected outcome | `facets.expected_outcome` |
| acceptance oracle | `facets.acceptance_oracle` |

`facets.destination` is additional framing. Each facet is either `{"status":"known","value":...}` or an explicit
`unknown`/`deferred` value with an owner. Statements use one of `fact`, `human-decision`, `assumption`, or `unknown`, and always
carry text and owner. The implementation sorts statements and gap identifiers before emission; prompt, model, language, and
question order are not stored authority inputs.

A draft may remain incomplete and readable. Acceptance fails when every facet is unknown/deferred, when an unresolved material
gap remains, or when the acceptance actor differs from `acceptance_authority`.

## Gap Graph

Each gap has `gap_id`, `material`, `status`, `owner`, and `depends_on`. Dependencies must reference existing gap IDs and the graph
must be acyclic. The graph is a human-authored assertion inside the revision; deterministic routing does not claim that the
graph is substantively correct.

## Acceptance And Supersede

- Acceptance covers the whole exact revision; partial facet acceptance is invalid.
- The supplied revision SHA-256 must match the canonical stored bytes.
- Acceptance of revision N never accepts revision N+1, even when N+1 already exists.
- At most one accepted revision is current.
- A second current selection requires the exact current selection reference as `supersedes`.
- Changing accepted intent requires a new immutable draft and a new acceptance.
- An abandoned or newer unaccepted draft never becomes current by recency.

## Non-Interactive CLI

```sh
PYTHONPATH=src python3 -m hv2ref.cli classify-intent-entry \
  --consequence non-consequential

PYTHONPATH=src python3 -m hv2ref.cli init-intent-home \
  --target /path/to/target \
  --authority-home-id AUTH-HOME-INTENT-001 \
  --observed-at 2026-08-19T10:00:00+09:00

PYTHONPATH=src python3 -m hv2ref.cli create-intent-draft \
  --target /path/to/target \
  --intent-id INTENT-001 \
  --sequence 1 \
  --observed-at 2026-08-19T10:01:00+09:00 \
  --input /path/to/canonical-input.json

PYTHONPATH=src python3 -m hv2ref.cli show-intent \
  --target /path/to/target \
  --intent-id INTENT-001 \
  --revision-id revision-0001

PYTHONPATH=src python3 -m hv2ref.cli accept-intent \
  --target /path/to/target \
  --intent-id INTENT-001 \
  --revision-id revision-0001 \
  --revision-sha256 <sha256 from create output> \
  --acceptance-id acceptance-0001 \
  --actor OWNER-LOCAL-001 \
  --observed-at 2026-08-19T10:02:00+09:00

PYTHONPATH=src python3 -m hv2ref.cli verify-intent \
  --target /path/to/target \
  --intent-id INTENT-001
```

For supersede, `accept-intent` additionally requires both `--supersedes-selection-id` and
`--supersedes-selection-sha256`. Omitting either fails closed.

## Plain Manual Read And Recovery

A reader without the project CLI can:

1. Read `authority.json` and `<intent-id>/identity.json` to establish qualified identity.
2. Hash the named draft's stored bytes and compare the acceptance `revision_ref`.
3. Compare the acceptance actor with the draft `acceptance_authority`.
4. Follow `current-selection.json` to its selection assertion, acceptance, and draft exact references.
5. Read the draft facets, typed statements, route, and unresolved gap list directly.

An interruption after draft persistence leaves a canonical `draft-unaccepted` artifact and no current selector. Repeating the
same create operation is byte-idempotent; different bytes for the same revision fail as a contradiction. No chat transcript,
provider session, latest-file heuristic, or automatic repair is needed to continue.

An interruption after acceptance or selection persistence is reported as `partial`. The prior current selection remains
actionable until the new selector switches. Repeating the same exact acceptance resumes idempotently; a changed revision,
actor, digest, acceptance, or supersede reference fails as a contradiction.

## Verification Boundary

The focused suite covers direct/bounded/dependency routing, zero-artifact non-consequential entry, exact byte determinism,
missing fields, ownerless unknowns, graph cycles, interruption retry, revision race, wrong actor/digest, material gaps,
vacuous/partial acceptance, acceptance/selection crash recovery, explicit supersede, abandoned drafts, extra tree entries,
symlinks, and existing state no-touch.

These tests verify artifact meaning and process ordering on the current local filesystem. They do not verify question quality,
multi-user authentication, hardware power-loss durability, adopter outcomes, record-to-item integration, or public/runtime support.
