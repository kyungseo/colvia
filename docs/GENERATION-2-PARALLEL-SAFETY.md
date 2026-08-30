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
    finalize-arbitrations/<prior-selector-sha256>.json
    finalize-successors/<predecessor-authority-sha256>.json
    integration-epochs/<epoch-id>/
      intent.json
      finalize-marker.json
      finalization.json
  active-generation.json
  active-integration.json
.harness-v2/staging/locks/
  active-integration.switch.lock
```

Immutable records use canonical UTF-8 JSON and same-filesystem `O_EXCL` creation. References bind stored bytes with exact
`{id, sha256}`. The active generation and integration selectors are the only replaceable Generation 2 current-state files and are
switched last. The empty lock file is a stable, non-authority advisory-lock anchor; its content, timestamp, and presence in ignored
runtime staging never select current authority.

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

One declared finalizer owns an integration epoch. On supported macOS hosts, `finalize-work` takes an exclusive kernel advisory lock
on `.harness-v2/staging/locks/active-integration.switch.lock` before reading the selector and holds it through claim, authority-leaf,
Git-result and selector revalidation, immutable finalization, and the last selector switch. It then verifies the exact claim set and
caller-provided worktrees, acquires the epoch marker, and acquires an append-only arbitration record keyed by the SHA-256 of the prior
active selector. Different epochs are therefore serialized against fresh selector state; only the exact winner can write a
finalization and reach the selector switch. Git work and integration commits are caller-owned and occur outside the harness.

A different duplicate marker or prior-selector arbitration record is a visible conflict. Process exit or crash releases the kernel
lock, but it does not release, expire, or implicitly transfer an append-only arbitration record. The same epoch may resume only with
byte-identical intent, marker and arbitration input.
If exact resume is unavailable while the prior selector remains unchanged, the declared finalizer may explicitly name the current
authority-chain leaf and a non-empty reason when creating a successor epoch. The append-only successor record is keyed by the stored
byte digest of that predecessor authority, binds the successor intent, and becomes the only valid leaf; concurrent branching and a
late predecessor resume fail closed. Every predecessor arbitration, successor, marker and finalization remains immutable. Replaceable
selectors use operation-owned exclusive temp files so concurrent byte-identical resumes do not delete a peer temp or leak raw
filesystem races. Actor and finalizer equality is logical declaration enforcement, not authentication.

If a successor is incorrectly declared while the unchanged selector has no predecessor arbitration, its new epoch arbitration may be
recorded before finalization fails closed with `HV2-SUCCESSOR-PREDECESSOR`. That arbitration is not implicitly reusable; the
in-contract forward path is a later explicit successor naming the rejected epoch. This is not automatic recovery or a general
liveness guarantee.
