# Agent Entry

This file is the canonical minimal entry for an agent working in a project with the Harness v2 private D1 candidate.
Document authority and currentness are indexed in [docs/README.md](docs/README.md).

## Authority Floor

- The human owner decides material scope, acceptance, and shared-state finalization.
- `.harness-v2/` and `.harness-v2-intents/` are project-owned truth. Do not select authority by path, timestamp, recency, or filename.
- `.harness-v2-product/` and `hv2` are product-managed and removable. Do not edit them as project customization.
- Actor and finalizer strings are logical declarations inside one trusted local OS account, not authentication.
- Do not read, copy, print, or place secrets in state, intent, evidence, examples, commands, or review packets.
- Never turn `degraded`, `partial`, `incompatible`, `conflict`, `stale`, `unsupported`, or unavailable evidence into success.

## Start

1. Run `./hv2 status`.
2. Read `docs/GETTING-STARTED.md` for the first work or `docs/OPERATIONS.md` for recovery.
3. Propose the exact scope and evidence. A human accepts consequential intent and finalizes shared truth.

Mutating product commands preview by default and require explicit `--apply`. Do not add it without the user’s authorization.

## Typed Pointers

- Mental model and identity: `docs/CONCEPTS.md`
- Product lifecycle and recovery: `docs/OPERATIONS.md`
- Provider-null and plain-file procedure: `docs/MANUAL-OPERATION.md`
- Trust and support boundary: `docs/SECURITY-AND-SUPPORT.md`
- Exact commands and classifications: `docs/REFERENCE.md`
- Generation 1 state: `docs/GENERATION-1-CONTRACT.md`
- Generation 2 parallel safety: `docs/GENERATION-2-PARALLEL-SAFETY.md`
- Guided intent: `docs/GUIDED-INTENT-FORMATION.md`

If a pointer is unavailable or contradicts persisted bytes, stop, report the contradiction, and preserve the last useful state.
