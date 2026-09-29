# Agent Entry

This is the canonical agent entry for the Harness v2 single-home development candidate.
Read [docs/README.md](docs/README.md) for document authority and currentness.

## Authority Floor

- The human owner decides material scope and acceptance. Agent output and confirmation tokens do not prove human authorization.
- `.hrn/format.json`, `.hrn/intents/`, and `.hrn/work/` are project-owned authority. Select current state only through verified typed references; never by timestamp or filename.
- `.hrn/product/` and the root `hv2` are managed runtime. Do not customize them. `.hrn/staging/` and `.hrn/locks/` are scratch, not authority.
- Actor strings declare roles inside one trusted local OS account; they are not authentication.
- Never put secrets in records, inputs, evidence, examples, or review packets.
- Preserve unknown, damaged, stale, partial, or unsupported state. Never turn unavailable evidence into success or delete records to unblock a command.

## Start

1. In an installed project run `./hv2 view`. Read the current verified manual and adapter paths it displays; never pin a release directory in the project entry.
2. For setup or broken-launcher diagnosis, use an independent trusted source with explicit `--source-checkout`; see [Getting Started](docs/GETTING-STARTED.md) and [Operations](docs/OPERATIONS.md).
3. Propose scope and evidence. Obtain human acceptance of the exact intent and result. Keep one editing Work at a time during serial use.

Lifecycle commands preview by default. Intent/Work publication writes machine records; prepare is read-only and apply requires the exact ticket/token. Obtain the relevant authorization before invoking a writer. Worker worktrees cannot write control authority.

## Typed Pointers

- Mental model: [Concepts](docs/CONCEPTS.md)
- Machine commands and failures: [Reference](docs/REFERENCE.md)
- Work records and content: [General Work](docs/GENERAL-WORK.md)
- Root and lifecycle: [Workspace Contract](docs/WORKSPACE-CONTRACT.md)
- Intent acceptance: [Guided Intent](docs/GUIDED-INTENT-FORMATION.md)
- Recovery and exit: [Operations](docs/OPERATIONS.md), [Manual Operation](docs/MANUAL-OPERATION.md)
- Trust and support: [Security and Support](docs/SECURITY-AND-SUPPORT.md)

Bounded worker execution and recovery have recorded synthetic qualification. Two private document Works were accepted on the earlier human-1 runtime; actual worker-1 adoption, same-file real-use continuation and general usability remain unverified. A local passing suite does not establish production readiness.
