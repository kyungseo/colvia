# Harness v2 Generation 1 Contract

This is the project-owned payload for the first private production reference. It is not filler and does not claim public,
default, adopter, runtime-support, or population validity.

## Release Carrier

```text
hv2-reference-release/
  release.json
  inventory.json
  payload/generation-1-contract.md
```

`release.json` keys are `authority_home_id`, `created_at`, `inventory_ref`, `record_type`, `release_id`, and
`schema_generation`. `inventory.json` keys are `entries`, `inventory_id`, `record_type`, and `schema_generation`.
Inventory entry keys are `path`, `sha256`, and `size_bytes`.

JSON uses UTF-8 without BOM, LF newlines, exactly one EOF LF, duplicate-key rejection, two-space indentation, and
lexicographically sorted object keys. Digests apply to stored bytes. Consumers verify every payload entry before hashing the
inventory bytes, then verify `release.json.inventory_ref`, then hash `release.json` as the carrier identity.

## State

The canonical root is `.harness-v2/`. Generation 1 uses one authority home, immutable item-local B2 records, explicit active
generation and pointer selectors, and forward-only rollback. Path, recency, and timestamps do not select current authority.

Assertion-bearing records contain `record_type`, `schema_generation`, `record_id`, `item_id`, `observed_at`, `observed_scope`,
and `unavailable_scope`. Same-home immutable references use exact `{id, sha256}` objects. Unknown additive members make the
item degraded, non-writable, and non-finalizing. Unknown schema generations are incompatible.

Each completed revision is digest-bound to its attempt result and acceptance. The verifier requires `accepted: true`,
`outcome: validated`, exact proposal inventory equality, item/path identity, a single pointer-chain tip, and active pointer equal
to that tip. Evidence facets bind the landed payload digest. Create records also carry a self-contained release binding.
Forward rollback names a previously selected completed revision by `{id, sha256}`.

## Ordered Stage-Then-Switch

1. Persist immutable attempt intent.
2. Stage candidate project bytes and sealed proposal inventory.
3. Persist human acceptance for the exact proposal.
4. Validate staged bytes, ownership, references, and digests; persist attempt result and self-contained release binding.
5. Persist facet assertions and a completed revision.
6. Append a pointer assertion.
7. Switch `active-pointer.json` last.
8. Land project payload bytes idempotently and persist a binding receipt with `git_state: unfinalized`, separately from Git
   finalization. An interrupted step can only continue from the exact sealed attempt and current pointer tip.

An in-process abort at a named semantic point persists an interruption record. An abort before step 7 preserves the prior active
pointer; retry/resume must either finish the same exact attempt or fail. No latest-wins or heuristic repair is allowed.

## Git, Retention, And Privacy

Authority, canonical item records, and selectors are tracked. Root `staging/` is ignored but independently inventoried; its
absence is not binding or cleanup proof. Immutable success, failure, inconclusive, assertion, acceptance, attempt, revision,
pointer, generation, and tombstone history is retained. Deletion is logical; stable ID reuse and physical-deletion success
claims are forbidden. Secret and credential input is forbidden.

## Durability And Acceptance

Writes are limited to one filesystem and use flush, file sync, classified Darwin full sync, atomic replace, and directory sync.
Process-crash injection proves ordering only; it does not prove kernel, firmware, or hardware power-loss durability.

Manual operation may use the core CLI without an agent/provider adapter. A plain auditor receives only persisted target bytes,
this contract, a presealed `EXPECTED.json`, and a live-target staging audit seal. It uses general-purpose tools and receives no
project CLI, implementation source/tests, or runtime transcript. Bare `assert` and optimized Python mode are forbidden.
