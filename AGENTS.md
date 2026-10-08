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

## Candidate Entry

Read `./hv2 view candidates` before recording an idea or answering what to do next. Planning is project-owned but grants no execution authority. Follow the installed adapter's Candidate Conversation section. Recommendations and ambiguous resume requests are read-only; an explicit planning request authorizes only that named planning change. Never upgrade the runtime merely to save an idea.

## Typed Pointers

- Mental model: [Concepts](docs/CONCEPTS.md)
- Machine commands and failures: [Reference](docs/REFERENCE.md)
- Work records and content: [General Work](docs/GENERAL-WORK.md)
- Root and lifecycle: [Workspace Contract](docs/WORKSPACE-CONTRACT.md)
- Intent acceptance: [Guided Intent](docs/GUIDED-INTENT-FORMATION.md)
- Recovery and exit: [Operations](docs/OPERATIONS.md), [Manual Operation](docs/MANUAL-OPERATION.md)
- Trust and support: [Security and Support](docs/SECURITY-AND-SUPPORT.md)

General usability, real-project multi-worker efficiency and production readiness require their own evidence. Historical observations in [Security and Support](docs/SECURITY-AND-SUPPORT.md) do not qualify the current source or installed release.

The optional direct-child parent gate requires human acceptance of the integrated result. Follow the current index and the exact installed release; development acceptance does not qualify a release candidate.

## Source Development Closeout

When closing a Harness source change, follow [Adopter Impact At Development Closeout](docs/MAINTAINING.md#adopter-impact-at-development-closeout) and report the update recommendation in the existing completion report. This applies to Harness development, not ordinary work inside an installed project.
