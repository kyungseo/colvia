# Harness v2 Generation 2 Parallel Safety Contract

Generation 2 adds repository-wide work claims and single-finalizer integration while preserving Generation 1 bytes and reader
semantics. It is a private, same-filesystem, local-trust reference contract. It does not claim public, distributed, NFS,
cross-filesystem, cryptographic authentication, runtime-provider or automatic worktree support.

## Compatibility

| Reader | State | Result |
| --- | --- | --- |
| Generation 1 | Generation 1 | Existing one-item behavior |
| Generation 1 | Active Generation 2 | `incompatible` |
| Generation 2 | Generation 1 | Delegate to the Generation 1 reader |
| Generation 2 | Generation 2 | Validate registry, claims, conflicts, reassignments and integration epochs |
| Any | Unknown future generation | `incompatible` or fail-closed |

Activation first verifies the Generation 1 item and inventories every immutable Generation 1 state file. It writes the Generation
2 immutable tree, binds the prior item selector digest, switches the item selector, and creates the repository Generation 2 selector
last. A partial activation is non-writable and non-finalizable. Existing authority, item identity, generation assertions and
`generations/1/**` bytes remain exact; the mutable predecessor selector digest is retained by the item registration.

## Persisted Tree

```text
.harness-v2/parallel/
  generation-assertions/generation-assertion-0002.json
  generations/2/
    repository.json
    item-registrations/<item-id>.json
    claims/<claim-id>.json
    conflicts/<conflict-id>.json
    reassignments/<reassignment-id>.json
    integration-epochs/<epoch-id>/
      intent.json
      finalize-marker.json
      finalization.json
  active-generation.json
  active-integration.json
```

Immutable records use canonical UTF-8 JSON and same-filesystem `O_EXCL` creation. References bind stored bytes with exact
`{id, sha256}`. The active generation and integration selectors are the only replaceable Generation 2 current-state files and are
switched last.

## Claim

A claim binds `claim_id`, `item_id`, logical actor/finalizer, repository/worktree IDs, branch, exact Git base commit/tree,
observation, predecessor and normalized `write_scope[]`. Claim creation is append-only. The writer creates the record, then reloads
the active integration selector and closed claim set before returning success.

Scope is NFC repository-relative POSIX identity. Empty, absolute, dot/dotdot, root escape, backslash/control bytes, `.git`,
`.harness-v2` and symlink components are rejected. Comparison uses NFC+casefold and bidirectional directory-prefix overlap. Same-item
claims always conflict; different items conflict when scope or control metadata overlaps. Disjoint claims do not conflict merely
because both claim records exist.

A rejected overlap or stale-base attempt may leave its immutable claim and conflict receipt. It must not change project bytes,
active selectors, staging or Git index/worktree state.

## Finalization And Recovery

One declared finalizer owns an integration epoch. `finalize-work` verifies the exact claim set and caller-provided worktrees, acquires
the epoch marker with `O_EXCL`, then revalidates the current base, scopes, Git ancestry and integrated result commit/tree. It writes
the finalization record and switches `active-integration.json` last. Git work and integration commits are caller-owned and occur
outside the harness.

A different duplicate marker is a visible conflict. The same finalizer may resume only with byte-identical intent/marker input.
Abandoned work does not expire; an explicit reassignment or successor epoch preserves the predecessor digest and reason. Actor and
finalizer equality is logical declaration enforcement, not authentication.
