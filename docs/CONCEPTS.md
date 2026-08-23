# Concepts

Harness v2 is a small planning control plane, not an agent execution engine. Its durable job is to keep human intent, authority,
state, evidence, and recovery understandable while tools and people change.

Document authority and currentness: [Documentation Index](README.md).

## The Smallest Mental Model

```text
human owner
  decides scope, acceptance, and finalization
        │
        ▼
project-owned plain truth
  intent + item state + evidence + selectors
        ▲
        │ propose, read, verify
agents and runtime adapters
  removable; never the final authority

product release ──explicit bind/update──> project-owned truth
```

The product can check declared boundaries. It cannot turn a logical actor string into authentication or prove that a human made a
good decision.

## Three Ownership Areas

| Area | Owner | Examples | Exit |
| --- | --- | --- | --- |
| Product-managed binding | product release selected by the project | `hv2`, `.harness-v2-product/` | rollback or detach |
| Project-owned truth | project and human finalizer | `.harness-v2/`, `.harness-v2-intents/` | remains readable after detach |
| Optional runtime or adapter | user-authorized integration | agent provider, Git host, CI, tracker | remove it and use the manual path |

Physical proximity does not merge authority. Product code may read project state, but an update must not silently rewrite local
intent, decisions, or evidence.

## State And Currentness

Generation 1 stores immutable item records and changes current state through an exact selector switched last. A timestamp, path,
directory order, or numerically largest filename never selects authority. Unknown schema generations are `incompatible`; unknown
additive members are `degraded` and non-writable.

Generation 2 adds repository-wide claims and one declared finalizer. Worktrees and Git commits remain caller-owned. The harness
checks exact base identity, normalized write scope, stale state, conflicts, and finalization lineage.

## Identity

An authority home qualifies local identities. The same local item or record ID in a different authority home is not the same object.
State and accepted intent use different homes:

```text
.harness-v2/           item state authority home
.harness-v2-intents/   accepted-intent authority home
```

There is no automatic cross-link between them in this D1 candidate. A future link must be explicit and digest-bound; directory
placement alone is not a relationship.

## Collaboration Boundary

Within one trusted local OS account, multiple logical actors may propose disjoint work. Each claim names the exact repository,
worktree, branch, base commit/tree, scope, actor, and finalizer. Overlap, stale base, deleted/diverged worktrees, or a competing
finalizer fails visibly.

This is same-repository coordination, not distributed locking or untrusted multi-user authorization. Enterprise multi-project
identity, delegation, policy enforcement, and portfolio control are outside Public Core.

## Manual-First Means Survivable

Manual-first does not mean automation is discouraged. It means the project remains inspectable, recoverable, and detachable without
one provider, dashboard, daemon, or chat transcript. Automation is useful when it stays inside the same authority and evidence
contract.
