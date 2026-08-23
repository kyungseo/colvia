# Documentation Index

This index is the self-description authority for repository documents. It states each document’s job, audience, authority,
applicable surface, and verification state without requiring per-file frontmatter.

Applies to: private D1 source-derived Public Core candidate. Public name and SemVer are unassigned.

Verified on: local product lifecycle and command regression passed on 2026-08-23. A prior fresh-context agent reader was `partial`,
and the prior bounded focused review is closed. Human fresh-reader evidence remains unavailable. Existing Generation 1, Generation 2,
and Guided Intent evidence is not a productization result.

| Document | Type / Reader | Jobs | Authority | Currentness |
| --- | --- | --- | --- | --- |
| `../README.md` | orientation / user | identity, prerequisites, first command, map, boundary | current D1 entry | local lifecycle regression verified 2026-08-23 |
| `GETTING-STARTED.md` | onboarding / user | first work and human gate | current D1 procedure | local lifecycle regression verified 2026-08-23 |
| `CONCEPTS.md` | concept guide / user and operator | mental model, state, identity, collaboration | current D1 explanation; deep contracts win on schema detail | local lifecycle regression verified 2026-08-23 |
| `OPERATIONS.md` | manual / operator | delivery, update, recovery, exit, diagnostics | current D1 product lifecycle | local lifecycle regression verified 2026-08-23 |
| `SECURITY-AND-SUPPORT.md` | boundary / user and operator | trust, runtime, support, integration | current D1 claim boundary | local lifecycle regression verified 2026-08-23 |
| `REFERENCE.md` | reference / user and operator | command, state, lifecycle, classification | current D1 reference | local lifecycle regression verified 2026-08-23 |
| `MAINTAINING.md` | maintainer guide | source, validation, release inventory, change boundary | current D1 maintainer procedure | local lifecycle regression verified 2026-08-23 |
| `MANUAL-OPERATION.md` | deep manual / operator and auditor | provider-null Generation 1/2 procedure | accepted bounded private contract | historical + current source projection |
| `GENERATION-1-CONTRACT.md` | technical contract / maintainer and auditor | item state and release payload | Generation 1 contract | accepted bounded private evidence |
| `GENERATION-2-PARALLEL-SAFETY.md` | technical contract / maintainer and auditor | same-repository parallel safety | Generation 2 contract | accepted bounded private evidence |
| `GUIDED-INTENT-FORMATION.md` | technical contract / maintainer and auditor | exact-revision accepted intent | Guided Intent contract | accepted bounded private evidence |
| `../AGENTS.md` | agent entry / agent runtime | authority floor and typed routing | canonical agent entry | local lifecycle regression verified 2026-08-23 |
| `../CLAUDE.md` | tool projection / supported agent runtime | pointer to canonical agent entry | derived; never independent authority | local lifecycle regression verified 2026-08-23 |

## Document Job Coverage

One document may serve several jobs. A job marked technical still has a shorter user path; the technical contract remains schema
authority. The three retained deep contracts predate this index and are the explicit standalone-pointer exception.

| Job | Shortest D1 Landing | Deeper Authority |
| --- | --- | --- |
| Orientation | `../README.md` | this index |
| Mental Model | `CONCEPTS.md` | Generation contracts |
| First Work | `GETTING-STARTED.md` | `GUIDED-INTENT-FORMATION.md` |
| State And Authority | `CONCEPTS.md` | `GENERATION-1-CONTRACT.md` |
| Identity | `CONCEPTS.md` | Generation 1 and Guided Intent contracts |
| Collaboration | `CONCEPTS.md` | `GENERATION-2-PARALLEL-SAFETY.md` |
| Delivery | `OPERATIONS.md` | `GENERATION-1-CONTRACT.md` |
| Update And Recovery | `OPERATIONS.md` | Generation contracts and `MANUAL-OPERATION.md` |
| Exit | `OPERATIONS.md` | product detach receipt and Generation 1 contract |
| Diagnostics | `OPERATIONS.md`, `REFERENCE.md` | CLI classifications |
| Runtime And Support | `SECURITY-AND-SUPPORT.md` | `PRODUCT-CAPABILITIES.json` |
| Security And Trust | `SECURITY-AND-SUPPORT.md` | implementation fail-closed checks |
| Integration | `SECURITY-AND-SUPPORT.md` | provider-null manual contract |
| Reference | `REFERENCE.md` | CLI help and deep contracts |
| Maintainer Entry | `MAINTAINING.md` | source and test suite |
| Agent Entry / Kernel | `../AGENTS.md`, `../CLAUDE.md` | `../AGENTS.md` |

History rule: a dated receipt or prior contract remains historical evidence. It does not become current product support merely
because the file still exists. If this index and a deep schema contract disagree on schema detail, stop and use the deep contract.
If this index and the implementation disagree on a command, treat the implementation as observed truth, mark the document stale,
and repair both in the same product revision.
