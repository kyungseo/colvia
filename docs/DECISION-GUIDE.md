# Decision Guide

Use this source-only guide to author, review and maintain plain decision documents. It is separate from runtime Work/intent authority and from task execution.

Reorganization and effective-state record: [DR-0006](decisions/DR-0006-source-contributor-document-structure.md). Until its exact amendment is accepted and activated, the [retained source procedures](#retained-source-procedures) remain effective. After that recorded activation, the identified version of this guide owns the relocated decision rules. Consult DR-0006 for the actual state; this entry does not activate them.

## Decision Catalog

| Document | Effective State And Scope |
| --- | --- |
| [DR-0001: Work Continuation Selection And Recovery](decisions/DR-0001-work-continuation-selection-and-recovery.md) | Draft; continuation support and implementation remain unapproved |
| [DR-0002: Checkout-1 Contract Baseline](decisions/DR-0002-checkout-1-contract-baseline.md) | Accepted (Amended); retained M2/M3 history and the named entry-1 successor amendment |
| [DR-0003: Source Development Procedure And Bounded Intake](decisions/DR-0003-source-development-procedure-and-bounded-intake.md) | Accepted (Amended); effective 2026-10-08, with the unchanged-M3 current-set reference and Public Preview managed-launcher preservation clause amended by DR-0004 on 2026-10-14; the named procedure-location amendment is accepted and effective through DR-0006 on 2026-10-16 |
| [DR-0004: Colvia Managed Entry And One-Way Transition](decisions/DR-0004-colvia-managed-entry-and-one-way-transition.md) | Accepted (Amended); exact entry-1 activation on 2026-10-14 and the named First B1 supplement on 2026-10-15 |
| [DR-0005: Delegated Ordinary Work Acceptance](decisions/DR-0005-delegated-ordinary-work-acceptance.md) | Accepted and activated only for the exact delegation-1 successor and named scope in its [activation record](decisions/DR-0005-delegated-ordinary-work-acceptance.md#delegation-1-activation); earlier guarantees remain except its explicit replacements |
| [DR-0006: Source Project Rules And Development Workflow](decisions/DR-0006-source-contributor-document-structure.md) | Accepted; source-only relocation and the named navigation cutover effective 2026-10-16; see its acceptance and activation record for exact scope and identities |

This catalog identifies the records relevant to these entry, procedure and technical-contract boundaries. It is not a complete inventory of concurrent work; consult the Development Index and recheck catalog rows before integration.

A Draft is a proposal. It does not describe supported commands or authorize implementation. The Owner must accept a contract change together with its identified contract revision and explicit effective scope. An Accepted label alone does not override the current contract documents.

The effective contract document set is normative; decisions record accepted changes and their reasons. Start with the [Documentation Index](README.md) and follow its detailed contracts. If evidence or contracts conflict, preserve state and report the difference. File order, timestamps and agent statements cannot resolve it. Historical material retains its original meaning without becoming current support.

For the current technical set, follow the exact [delegation-1 activation](decisions/DR-0005-delegated-ordinary-work-acceptance.md#delegation-1-activation) and its named successor clauses. Retain the [entry-1 activation](decisions/DR-0004-colvia-managed-entry-and-one-way-transition.md#entry-1-amendment-activation--2026-10-14) and [First B1 supplement](decisions/DR-0004-colvia-managed-entry-and-one-way-transition.md#first-b1-permission-observation-activation--2026-10-15) guarantees except where the delegation-1 activation explicitly replaces them. Historical preparation labels do not independently determine current activation or support.

## Acceptance Records

Record what the Owner accepted, the acceptance date, the exact document or result revision, the scope, unresolved limits and when any contract change becomes effective. A Git revision or recoverably retained exact bytes can identify the accepted content. A digest detects drift but does not preserve content. Recorded Owner statements are reported evidence, not identity authentication; an agent cannot accept its own work as the human.

The [Source Project Rules And Development Workflow](development/WORKFLOW.md#roles-and-authorization) owns Driver/Reviewer/Owner responsibilities and [publication authorization](development/WORKFLOW.md#publication-and-adopter-authorization). This guide records exact decision identity, accepted scope and activation; its summaries do not establish a second owner for the task procedure.

This decision guide does not establish a development-task tracker or transfer an existing task. Before implementation, agree on the task's scope, completion criteria, plan, checks and authorization, and designate its single progress record. A decision's acceptance and that task's execution are separate.

## Document Identity And State

Use `docs/decisions/DR-NNNN-<topic>.md`, with a four-digit local ID allocated when the Draft is created. Check current files and recorded history first. Do not reuse an ID after a proposal is abandoned or superseded. Guides and ordinary notes do not need serial IDs.

The Product Owner owns this document lineage and its local IDs. A move or rename that preserves the logical document keeps its ID. An independent import or fork receives a new local identity and a preserved provenance relation. Required provenance may remain in private records when disclosure is inappropriate, but understanding or operating this source must not require access to it. Human cross-repository pointers identify the repository or document lineage, local ID and exact revision; a bare local ID is ambiguous.

A plain authored document is not a runtime record. Its ID, path, repository URL or digest does not create an authority home or a typed reference. These rules do not change runtime Work/intent identities, release/binding identities or machine imports. A future plain Work ID must not be treated as a typed Work `Id` without an explicit supported transition.

| State | Meaning |
| --- | --- |
| Draft | Open proposal; identify alternatives, limits and promotion conditions |
| Accepted | Exact content and scope accepted by the Owner; identify activation separately when needed |
| Accepted (Amended) | An accepted decision with a later Owner-accepted change to named clauses |
| Superseded / Partially Superseded | Identify the replacing accepted decision, affected clauses and effective revision; preserve unaffected meaning |
| Dropped | The proposal was not adopted; retain the reason and retire its ID |

Keep the title, ID, status and date visible. A small frontmatter block may hold those fields and public-safe replacement links. Drafts leave final Decision, Rationale and Consequences empty; explain the proposal and its reasons in the body. On acceptance, fill those sections and record the Owner's exact scope. Later changes name the clauses they amend or replace. Adding evidence that already accepted activation conditions were met is distinct from changing those conditions; the latter requires an amendment and Owner acceptance.

## Review And Evidence

Follow [Review And Evidence](development/WORKFLOW.md#review-and-evidence) for the request, input identity, verbatim response, Driver disposition and actual Owner decision. Use [Disclosure](development/WORKFLOW.md#disclosure) for public-intent content and separately authorized private review transmission. These are pointers to the common source procedure, not an additional review gate.

## Retained Source Procedures

The previously accepted decision procedure and development appendix remain recoverable in Git. Their historical coordinates refer to `CONTRIBUTING.md` at `238514686078ce1564010a7b69013f48a635c57c`, never to the first bytes of this new guide or to current file offsets.

| Historical Input | Exact Identity |
| --- | --- |
| Original full CONTRIBUTING at `238514686078ce1564010a7b69013f48a635c57c` | 21,849 bytes; SHA-256 `ca0a2c291716159f4fc7accc461a93992c11182242ebdfdb5c43fa4b54d0448d` |
| Decision procedure prefix in that file | bytes `[0, 6746)`; SHA-256 `6f87742bfcf0c0fd664f865628ec7210b03d37f89d5d5d87a3d888b439fc888d` |
| Source-development appendix in that file | bytes `[8337, 21849)`; length 13,512; SHA-256 `b25ad8a06e0d1998ce3d869ec0ac8fd08caf9c4631a0a06dd4d31a5962d0b1fa` |
| Current pre-reorganization source at `d86bd1fd7754144e5c8538712724ae78571941bf` | 22,169 bytes; SHA-256 `f68e09e3415ac6955443f22b5d880c2784e49158716ec16087a6745a535a60c6` |

The current pre-reorganization version adds only the authorized 320-byte current-contract preamble after `# Contributing`. The [activation closeout](development/CHORE-20261009-002-colvia-verification-controls.md#owner-result-acceptance-and-contract-activation--2026-10-14) and [DR-0004's frozen-label explanation](decisions/DR-0004-colvia-managed-entry-and-one-way-transition.md#frozen-preparation-labels) identify that source-navigation change. It does not change the historical prefix hash or move the historical coordinate system to the current file.

Use the retained source revision when the relocation has not been activated:

```sh
git show d86bd1fd7754144e5c8538712724ae78571941bf:CONTRIBUTING.md
```

[DR-0003](decisions/DR-0003-source-development-procedure-and-bounded-intake.md) records the appendix's actual acceptance and activation on 2026-10-08. [DR-0004](decisions/DR-0004-colvia-managed-entry-and-one-way-transition.md) changes named technical/current-set clauses; it does not replace the unrelated source-development procedure. Original accepted decisions and closed development records remain unchanged by this relocation amendment.

## History

### Procedure Acceptance — 2026-10-07

The following is the original paragraph, quoted verbatim from the retained CONTRIBUTING revision `238514686078ce1564010a7b69013f48a635c57c`. “This file” and “the procedure above” refer to that historical file and byte range, not this guide. Its acceptance does not accept DR-0006 or the new document layout.

```text
The human Owner accepted the procedure above on 2026-10-07 for source-authored decision documents only. Its exact UTF-8 bytes, from the first byte of this file to immediately before the Procedure Acceptance heading, have SHA-256 `6f87742bfcf0c0fd664f865628ec7210b03d37f89d5d5d87a3d888b439fc888d`. This accepts the document procedure, not DR-0001, a product contract change, a development-task transfer, runtime installation, Git publication or adopter application. DR-0001 remains a Draft until its own promotion conditions are met.
```

### Additional Source Decisions History

The following original section body is preserved verbatim in its historical context. Relative Markdown links inside this quotation belong to the original root CONTRIBUTING file; use the live decision catalog above for navigation.

```text
This section was added after the accepted procedure above and does not alter its accepted byte range. The decision's own exact acceptance record defines its scope and effective date.

| Document | State | Purpose |
| --- | --- | --- |
| [DR-0002: Checkout-1 Contract Baseline](docs/decisions/DR-0002-checkout-1-contract-baseline.md) | Accepted (Amended); M2 and M3 effective 2026-10-07 | Own the exact eleven-document checkout-1 technical baseline; the M3 amendment identifies current revisions and preserves the original M2 table as history |

The accepted baseline includes the source-only [Checkout-1 Structural Contract](docs/development/CHECKOUT-1-STRUCTURE.md). Its preserved Draft labels identify the preparation revision; DR-0002 records activation of those exact clauses. Neither source-only document is part of the managed installation. DR-0001 remains a separate Draft, and development-task ownership, Git publication and adopter updates retain their separate authorization boundaries.
```
