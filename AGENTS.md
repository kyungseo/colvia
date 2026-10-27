# Agent Entry

This is the canonical agent entry for Colvia’s single-home `continuation-1` profile.
Read [docs/README.md](docs/README.md) for document authority and currentness.

These instructions describe the `continuation-1` profile; in an installed project, use the verified installed release; see [Profile and authorization](docs/README.md#continuation-1). Owner authorization and source-contract activation come from their actual decisions. Do not infer either from document presence or a verified binding. Editing these files does not activate the contract.

## Authority Floor

- The human owner decides material scope and acceptance. An activated exact intent-bound grant may permit only the named ordinary isolated-worker accept described in General Work. All other decisions and source-development result acceptance remain human. Agent output and confirmation tokens do not prove human authorization.
- `.hrn/format.json`, `.hrn/intents/`, and `.hrn/work/` are project-owned authority. Select current state only through verified typed references; never by timestamp or filename.
- `.hrn/product/` and the root `colvia` are managed runtime. Do not customize them. `.hrn/staging/` and `.hrn/locks/` are scratch, not authority.
- Actor strings declare roles inside one trusted local OS account; they are not authentication.
- Never put secrets in records, inputs, evidence, examples, or review packets.
- Preserve unknown, damaged, stale, partial, or unsupported state. Never turn unavailable evidence into success or delete records to unblock a command.

## Start

1. When explicitly asked to develop Colvia itself in its trusted source checkout, read source-only `CONTRIBUTING.md`, then its Development Workflow and existing task record. The Workflow's unchanged-entry statement describes the earlier source-only relocation; this candidate adds the conditional route. Do not install a runtime or create typed Work to begin source development.
2. In an installed project run `./colvia view`, follow project-owned rules and read the verified manual/adapter paths it displays. Being inside this managed manual does not make the task source development. Source-only files are absent here; never require them or pin a release directory in the project entry.
3. For setup or broken-launcher diagnosis, use an independent trusted source with explicit `--source-checkout`; see [Getting Started](docs/GETTING-STARTED.md) and [Operations](docs/OPERATIONS.md).
4. Propose scope and evidence. Obtain human acceptance of the exact intent and result. Keep one editing Work at a time during serial use.

Lifecycle commands preview by default. Intent/Work publication writes machine records; prepare is read-only and apply requires the exact ticket/token. Obtain the relevant authorization before invoking a writer. Worker worktrees cannot write control authority.

## Candidate Entry

Read `./colvia view candidates` before recording an idea or answering what to do next. Planning is project-owned but grants no execution authority. Follow the installed adapter's Candidate Conversation section. Recommendations and ambiguous resume requests are read-only; an explicit planning request authorizes only that named planning change. Never upgrade the runtime merely to save an idea.

## Follow-Up And Plan Alignment

On resume, read the selected Work, its referenced plan and `./colvia view continuation WORK_ID`, including completed Work. Explain accepted result, remaining plan items and the recorded follow-up separately. Proposal, existing Work, explicit none and undecided have different meanings. Selection grants no execution or acceptance authority. Reconcile conflicting valid choices with the human; never choose by timestamp. Preserve pending/unknown state and explain usage out of 256, remaining count or unavailable usage. Follow the installed adapter’s Follow-Up And Plan Alignment section.

## Typed Pointers

- Mental model: [Concepts](docs/CONCEPTS.md)
- Machine commands and failures: [Reference](docs/REFERENCE.md)
- Work records and content: [General Work](docs/GENERAL-WORK.md)
- Root and lifecycle: [Workspace Contract](docs/WORKSPACE-CONTRACT.md)
- Intent acceptance: [Guided Intent](docs/GUIDED-INTENT-FORMATION.md)
- Recovery and exit: [Operations](docs/OPERATIONS.md), [Manual Operation](docs/MANUAL-OPERATION.md)
- Trust and support: [Security and Support](docs/SECURITY-AND-SUPPORT.md)

Use evidence for the exact current source or installed release when assessing general usability, real-project multi-worker efficiency or production readiness. Keep the historical observations in [Security and Support](docs/SECURITY-AND-SUPPORT.md) within their recorded scope; do not use them as qualification of the current source or installed release.

The optional direct-child parent gate requires human acceptance of the integrated result. Follow the current index and the exact installed release; development acceptance does not qualify a release candidate.

## Source Development Closeout

When closing a Harness source change, follow [Adopter Impact At Development Closeout](docs/MAINTAINING.md#adopter-impact-at-development-closeout) and report the update recommendation in the existing completion report. This applies to Harness development, not ordinary work inside an installed project.
