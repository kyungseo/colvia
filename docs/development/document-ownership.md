# Where Colvia documents and artifacts belong

Use this map when developing Colvia itself. It locates existing rules and describes how to apply the documentation language conventions; it does not create a new approval process or make source-development documents part of an installed project. Revisit it when planning, resuming or closing source work, including after the first public release.

## Existing rules to apply

- [Source workflow](WORKFLOW.md#start-and-select): one owning task record and a navigation index; keep proposal, implementation, verification and acceptance distinct.
- [Disclosure](WORKFLOW.md#disclosure): remove private identities and identifiable external comparison provenance before content enters a public-intent repository.
- [Decision guide](../DECISION-GUIDE.md#document-identity-and-state): decisions have their own identity, state and explicit activation; copying a draft into source does not accept it.
- [Document language and placement](preview-release-order-and-user-journey.md#문서-언어와-배치-제안--11월-4일): the accepted reader/language split remains applicable. Historical records keep their authored language; new technical contracts use the existing English reference convention. User guides remain paired English/Korean.
- [User guide navigation](user-documentation.md): source manuals own generated installed content; verify links in the installed destination.
- [Records and retention](../REFERENCE.md#records-and-retention): retain raw material only for a named evidence, recovery or follow-up need; do not duplicate plan/review/result trackers.

## Document language

Choose the language by the page’s reader and purpose. These conventions apply to the Colvia repository. A project connected to Colvia keeps its own writing conventions.

| Where you are writing | What to write |
| --- | --- |
| Root README and CONTRIBUTING; current pages under `manual/en/` and `manual/ko/` | Maintain an English and a Korean page. Update both when instructions, support conditions or examples change. Link to the same page in the other language. An installation link in a single-language page should open that language on the downloads site. |
| Shared entry pages | `docs/README.md`, `SECURITY.md` and the installed welcome page serve both languages on one page. Give each reader the same actions and destinations. The installable language indexes under `distribution/foundation-guides/` follow their respective locales. |
| Source and agent references | Write current technical references under `docs/`, new decision text under `docs/decisions/`, agent entry points, adapter instructions and maintainer notes for builds, runtime and assets in English. Localized diagrams, example prompts and exact interface messages may use their intended language. |
| Development index and ongoing development | Use English for index headings, link labels and summaries, and for new task plans, technical designs, follow-ups and result summaries under `docs/development/`, including `record-foundation/`. A dated update to an older file can use English under its own heading. If a plan is expressly requested in Korean for its reviewer, write it in Korean and identify its purpose in the English index entry. |
| Maintained explanations in pages that also contain historical records | Apply the language convention by section. Write maintained technical explanations in English. When translating earlier wording in place, date the translation and link to the exact original revision. Historical decisions and evidence retain their original authority. Translating or maintaining a reference does not adopt a decision. |
| Decisions, reviews and evidence already on record | Preserve the original language of accepted decisions, dated plans, reviewer responses, observations, receipts and earlier-profile material. Keep quoted wording, fixture bytes, identifiers and existing link targets intact. Describe a decision or finding in English in the current index or record when readers need it. A translation is a summary unless it has itself been adopted. |

When reviewing a documentation change, check the headings **and the body** of the maintained text. For paired pages, follow the language switch and the links for the action that changed. For packaged pages, check the destination produced by the [guide mapping](../../distribution/foundation_bundle.py). For links into historical records, translate the visible label where needed and retain the original fragment.

## Placement by purpose

| Content | Maintained location | Boundary |
| --- | --- | --- |
| Product implementation specification, architecture, invariants and validation criteria | Source-owned technical/design documents under docs; drafts supporting active work under docs/development | Keep actionable requirements and rationale in the repository, not only in a personal artifact directory. Mark draft/open/implemented/verified states accurately. |
| Technical decision and activation | docs/decisions under the Decision Guide | An Owner requirement, draft design, implementation approval and exact contract activation are distinct. |
| Task progress, public-safe review findings, results, remaining work and follow-up candidates | One owning development record, with navigation/candidate links in docs/development/README.md | Do not maintain a competing private progress record. Preserve useful technical findings even when original correspondence stays private. |
| End-user instructions | README pairs and manual/en, manual/ko; installed guides from their defined sources | Do not put development instructions or private evidence paths into installed-project requirements. |
| Agent/runtime contracts and reusable checks | Their existing source entry, adapter, technical reference and test locations | Source-development entry is conditional on explicitly developing Colvia; installed agents follow their verified project launcher and adapter. |
| Reusable build/verification code, selected assets and required notices | Repository-owned scripts/tests/assets and legal notices | Reusability and product ownership, not whether an agent authored the file, determine placement. |
| Personal/account/customer material, identifiable external comparison evidence, raw runs, failed fixtures, large candidate binaries and recovery copies | Task-owned durable artifacts outside Git when appropriate | Keep exact provenance and failure/recovery evidence privately. Publish sanitized technical conclusions and reusable fixtures where needed. Raw output is not required merely because it exists. |
| Separate learning/tutorial content | Its own learning publication, linked to a real product version when available | Product behavior, commands and support contracts remain owned here. Do not duplicate their authority in teaching materials. |

## Disclosure check

Check source, tests, fixtures, generated documents and proposed Git messages for personal paths, account/contact data, credentials, customer data and identifiable external comparisons. Repository/owner names, URLs, local paths, revisions, branches and benchmark provenance can identify an external reference even when no secret is present. Use neutral reference labels and the minimum technical fact needed. This follows the existing Disclosure rule; it is not a reason to omit a design finding or move an entire otherwise useful specification out of the repository.

Keep required dependency/license/SBOM attribution. Explicitly supported host/product names are necessary product information, not anonymized comparison labels. The private provenance map may point into the repository; repository documents must remain understandable without links to private local files.

## At each source-work checkpoint

Identify the canonical documents and the material remaining in task artifacts. Update the repository-owned requirements and record the private remainder's purpose/end condition in the existing task evidence. Preserve original reviewed inputs and failures; do not rewrite them as current instructions. Link a relocated current document from the existing source entry/index, and make future edits in that one location. Run bounded link, disclosure and source-versus-installed routing checks. A successful copy does not authorize deleting originals, committing or publishing.

Current application: [record foundation](FEAT-20261106-002-record-foundation.md).
