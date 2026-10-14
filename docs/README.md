# Documentation Index

This index identifies current single-home development instructions. The `entry-1` development candidate profile has installed machine commands, local record writers, init/update/rollback, exact repair and receipt-bound detach. General usability and real-project multi-worker efficiency remain unverified. [Security and Support](SECURITY-AND-SUPPORT.md) distinguishes current limits from historical observations.

Verified active status exposes a derived, read-only `documentation_root`. Follow that release's index rather than guessing a newer document path. Project-authored DR, brief and Work documents remain project-owned Markdown referenced by path and digest; the product does not impose their repository layout.

| Document | Reader and responsibility | Authority and evidence boundary |
| --- | --- | --- |
| [Product Entry](../README.md) | User orientation | Current development entry; no adoption claim |
| [Agent Entry](../AGENTS.md) and [Claude Entry](../CLAUDE.md) | Agent behavior and tool projection | AGENTS is canonical; Claude is a pointer |
| [Getting Started](GETTING-STARTED.md) | Operator setup and first serial work | Current setup procedure; general usability unverified |
| [Concepts](CONCEPTS.md) | User model and ownership | Explanation; detailed contracts govern schemas |
| [Operations](OPERATIONS.md) | Operator update/recovery/exit | Current bounded lifecycle procedure |
| [Reference](REFERENCE.md) | Exact commands, paths, diagnostics and [recording/retention rules](REFERENCE.md#records-and-retention) | Source and installed interfaces are distinct; agent recording policy does not change authority |
| [Guided Intent](GUIDED-INTENT-FORMATION.md) | Intent formation and acceptance | Typed artifacts; natural-language quality unverified |
| [General Work](GENERAL-WORK.md) | Maintainer and reviewer | Work records/content and bounded worker integration contract |
| [Workspace Contract](WORKSPACE-CONTRACT.md) | Maintainer and reviewer | Root, product and recovery contract |
| [Manual Operation](MANUAL-OPERATION.md) | Operator and auditor | Plain retained evidence; no unrestricted manual writer |
| [Security and Support](SECURITY-AND-SUPPORT.md) | Trust/runtime boundary | Bounded local evidence, no native/adopter promotion |
| [Maintaining](MAINTAINING.md) | Contributor validation and inventory | Current source procedure |

## Historical Material

Source checkouts retain `docs/GENERATION-1-CONTRACT.md`, `docs/GENERATION-2-PARALLEL-SAFETY.md`, and `receipts/` for historical audit only. They are not shipped in the managed release and do not describe supported commands, readers or upgrades. Their old paths are not single-home authority. Do not follow historical operations on a current target.

If a current document and source disagree, report the difference and preserve state. Align code and docs in the same qualified change; do not promote a historical receipt to current support. Public version and distribution remain unassigned.

Human entry: run `./colvia view` in the project and read the current managed adapter it identifies. [Reference](REFERENCE.md#human-review) defines command and observation boundaries.

## Entry-1 Candidate

These working documents describe the Colvia `entry-1` successor candidate. They have not replaced the effective eleven-member M3 technical contract identified by the exact hashes in source record `docs/decisions/DR-0002-checkout-1-contract-baseline.md`, under DR-0003. The original M3 bytes remain recoverable from source revision `a17f35cf323ffde7a8642a85501fddbec858b6de` (the adapter member has moved from `adapters/harness-v2-work/SKILL.md` to `adapters/colvia-work/SKILL.md` with the same baseline bytes). The structural supplement retains its historical Draft label at that M3 hash.

DR-0004 accepts the transition design and named amendments, not this candidate's qualification or activation. Exact successor hashes, final qualification and separate Owner result/activation acceptance remain required. A copied or installed candidate still carries this limitation; document location or an installation result does not activate it. Source decision/development paths above are provenance identifiers, not links shipped in the managed payload.

## Current Candidate

The current window includes optional direct-child composition and parent acceptance checks. Qualification of the exact release candidate remains required; historical observations do not qualify these bytes. See [Direct-Child Umbrella](GENERAL-WORK.md#direct-child-umbrella) and [Transition To Entry-1](GETTING-STARTED.md#transition-to-entry-1).

Planning-1 introduced project-owned candidate notes, one recorded Owner selection, deferral and explicit resumption. Begin with [Candidate Planning](REFERENCE.md#candidate-planning).

Entry-1 retains candidate planning and the verified checkout-1 unchanged-CRLF exception, replaces the managed launcher and adapter paths, and writes paired schema 2 switch and schema 3 detach plans/receipts. See [Transition To Entry-1](GETTING-STARTED.md#transition-to-entry-1) for the one-way transition and recovery limits. This checkout is a development candidate; exact-candidate qualification and real fresh-session use are separate checks.
