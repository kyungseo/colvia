# Contributing

Current technical contract: [activated entry-1 successor set](docs/decisions/DR-0004-colvia-managed-entry-and-one-way-transition.md#entry-1-amendment-activation--2026-10-14). The exact validated document bytes retain their preparation labels; this source activation record identifies their effective status and limits.

Use this source-only guide to propose and review product decisions. Begin with the [Documentation Index](docs/README.md) for the current product, [Maintaining](docs/MAINTAINING.md) for validation and adopter impact, and the decision below for the proposed continuation contract. These source decision documents are not installed into adopter projects.

## Decisions

| Document | State | Purpose |
| --- | --- | --- |
| [DR-0001: Work Continuation Selection And Recovery](docs/decisions/DR-0001-work-continuation-selection-and-recovery.md) | Draft | Separate a Work's follow-up choice from its lifecycle and define interrupted publication recovery |

A Draft is a proposal. It does not describe supported commands or authorize implementation. The Owner must accept a contract change together with its identified contract revision and explicit effective scope. An Accepted label alone does not override the current contract documents.

The effective contract document set is normative; decisions record accepted changes and their reasons. Start with the current index above and follow its detailed contracts. If evidence or contracts conflict, preserve state and report the difference. File order, timestamps and agent statements cannot resolve it. Historical material retains its original meaning without becoming current support.

## Roles And Authorization

The human Owner decides material scope, policy acceptance and result acceptance. The Driver proposes and performs authorized work, records evidence and limits, and dispositions review findings. A Reviewer reports findings; a review verdict or passing check does not authorize edits or replace Owner acceptance.

Record what the Owner accepted, the acceptance date, the exact document or result revision, the scope, unresolved limits and when any contract change becomes effective. A Git revision or recoverably retained exact bytes can identify the accepted content. A digest detects drift but does not preserve content. Recorded Owner statements are reported evidence, not identity authentication; an agent cannot accept its own work as the human.

Obtain explicit Owner authorization for commit, push, PR creation, merge, public release and actual adopter application when those actions are not already authorized for the named target and scope. Review or result acceptance alone authorizes none of these actions. Do not infer execution authority from a candidate, recommendation or old task, and do not ask again for work already covered by an applicable authorization.

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

## Review, Evidence And Disclosure

Keep the review request, exact input identity, final reviewer response, Driver dispositions and actual Owner decisions distinct in the decision or its existing task record. Use `accept`, `revise`, `defend` or `needs-user` for each finding. Preserve the final reviewer response verbatim. Report actual model/session identity and any limits on independence. A static reading, executed check and reproduced counterexample are different evidence.

For changed source, use Maintaining to choose checks and report actual results, inherited evidence and unverified limits separately. Preserve extra raw evidence only for an identified failure, qualification, reuse or delivery need and record its end condition. Avoid copying a whole source tree or adding a validation archive for every check.

Keep private repository/owner names, paths, revisions, branches and identifiable comparison provenance out of public-intent source documents, frontmatter and Git history. Preserve required legal attribution. A public technical rationale must stand on its own even when sensitive historical correspondence stays private.

Contributors assess generic product impact from source evidence. The Owner or a designated maintainer checks known private adopters and records application decisions in private operations records; external contributors need not access that inventory. Unknown installation state remains unverified. Follow [Adopter Impact At Development Closeout](docs/MAINTAINING.md#adopter-impact-at-development-closeout) without treating source acceptance as permission to update an adopter.

## Procedure Acceptance

The human Owner accepted the procedure above on 2026-10-07 for source-authored decision documents only. Its exact UTF-8 bytes, from the first byte of this file to immediately before the Procedure Acceptance heading, have SHA-256 `6f87742bfcf0c0fd664f865628ec7210b03d37f89d5d5d87a3d888b439fc888d`. This accepts the document procedure, not DR-0001, a product contract change, a development-task transfer, runtime installation, Git publication or adopter application. DR-0001 remains a Draft until its own promotion conditions are met.


## Additional Source Decisions

This section was added after the accepted procedure above and does not alter its accepted byte range. The decision's own exact acceptance record defines its scope and effective date.

| Document | State | Purpose |
| --- | --- | --- |
| [DR-0002: Checkout-1 Contract Baseline](docs/decisions/DR-0002-checkout-1-contract-baseline.md) | Accepted (Amended); M2 and M3 effective 2026-10-07 | Own the exact eleven-document checkout-1 technical baseline; the M3 amendment identifies current revisions and preserves the original M2 table as history |

The accepted baseline includes the source-only [Checkout-1 Structural Contract](docs/development/CHECKOUT-1-STRUCTURE.md). Its preserved Draft labels identify the preparation revision; DR-0002 records activation of those exact clauses. Neither source-only document is part of the managed installation. DR-0001 remains a separate Draft, and development-task ownership, Git publication and adopter updates retain their separate authorization boundaries.


## Proposed Source Development Procedure

Preparation revision: this appendix has no effect unless [DR-0003](docs/decisions/DR-0003-source-development-procedure-and-bounded-intake.md) records Owner acceptance and verified activation of these exact bytes and their named scope. The Proposed heading is retained to identify the preparation revision; consult DR-0003 for its current acceptance and activation state. The accepted decision-guide prefix, including its statement that the decision guide establishes no task tracker, keeps its bytes and meaning. This appendix proposes a separately accepted, additional development procedure. [Development Index](docs/development/README.md) holds the proposed intake and criteria; it is not an execution queue.

| Document | State of this preparation | Purpose |
| --- | --- | --- |
| [DR-0003: Source Development Procedure And Bounded Intake](docs/decisions/DR-0003-source-development-procedure-and-bounded-intake.md) | Draft; consult its own record for any later acceptance and activation | Propose new source-development task management and the named candidate intake |

### Start And Select

Use the [Documentation Index](docs/README.md) for the product overview and DR-0002 for the normative technical contract. Read the development index and any existing record that owns the requested work. Explain the observed state and remaining authorization before selecting another task. A recommendation, candidate entry, ambiguous request to continue, or contract Draft does not authorize implementation. Do not infer an unrecorded choice from an empty list or a closed task.

Keep an unselected candidate as a title with purpose, reason for deferral and a concrete reconsideration condition when known. Do not allocate a development record ID or publish a runtime intent merely to store an idea. After the Owner selects a bounded task and approves its plan, create one source-owned record under `docs/development/<record-ID>-<topic>.md`. Use `{FEAT|PATCH|HOTFIX|CHORE}-YYYYMMDD-NNN`, with the start date and next unused three-digit sequence shared across all four prefixes for that date. FEAT denotes a new capability, PATCH a bounded correction, HOTFIX an urgent correction, and CHORE maintenance or documentation work; a decision-review task defaults to CHORE. Check current files and retained history before allocation; never reuse an ID. This check is not an atomic reservation. If a collision appears, stop allocation and confirm one unused ID and one owning record before continuing. These are plain development document IDs, not runtime Work IDs. Creating the document creates no runtime Work, intent, authority home or lifecycle state.

Here plan approval means the Owner authorizes execution of the named scope; it does not authorize Git/adopter actions or accept the resulting work. The approved development record fulfills Maintaining's reference to an existing Work narrative; the preliminary review note does not. Runtime installation is not required.

A development record states its purpose, owner, scope/exclusions, completion criteria, exact starting inputs, authorized plan, verification and time/attempt limits, current disposition, remaining work and next decision. Record proposal, execution evidence, review disposition and actual Owner acceptance distinctly. Keep detailed progress in that one record. The index locates candidates and records and holds unselected candidates' criteria; it does not mirror task progress. On selection, the task references the exact intake/criteria revision and any explicitly linked prior closeout/disposition, and owns progress only for criteria within its authorized scope. At closeout record each affected criterion's result and residual work; the next task reads those explicit links, never a timestamp-derived latest result. The index links closeouts without mirroring their progress. A decision's open points remain contract choices; the task records their review and resolution without creating a second technical decision owner.

Record a new unselected source-originated idea in the Development Index's New Source Candidates section, with its title, purpose, deferral/reconsideration condition when known and a link to the dated, revision-identified Owner planning authorization. Keep that authorization in the subject Draft or a source-only planning/review note as described below, not as selection/review prose in the index. A new self-contained, public-safe request, including a new anonymized adopter issue, uses this route regardless of its origin; an existing external legacy candidate still needs the handoff amendment. Record the idea entry's resulting revision and bounded diff in that authorizing record. Later edits or dropped notices use the same kind of dated Owner planning record while preserving the earlier snapshot meaning. This authorization permits adding the new idea's purpose and conditions in that designated section; it is distinct from navigation maintenance and does not require an amendment per idea. Do not copy or relabel an accepted legacy candidate there to evade its criteria or amendment boundary. A directly selected new task may go straight to its approved-plan development record and an index task link. Changing that task's agreed scope requires the relevant Owner plan decision; changing a technical contract still needs its named accepted amendment. Bringing in another legacy external candidate, changing this procedure or changing accepted intake criteria/scope requires an Owner-accepted amendment to DR-0003. Within the accepted intake, navigation means task/closeout links and candidate selected/closed/dropped notices backed by the relevant Owner record. It does not include criteria, purpose or execution boundaries. Record the changed revision and bounded diff in the authorizing task, subject Draft or source-only planning/review note described here. A navigation edit grants no wider scope. Keep dated intake observations as snapshots instead of updating them as progress. Do not create separate STATUS/backlog/receipt registries or automatically mirror progress elsewhere.

### Review And Execute

R0 reviews a plan before execution approval; R1 reviews the resulting change before result acceptance. Their separate boundaries apply by default to all changes, including tests, runners, safety oracles and behavior-preserving refactors. The only default exception is a pure typo or navigation correction. A pure typo correction does not change executable behavior, assertions, criteria or authority. HOTFIX is not an automatic waiver. For a pure typo or navigation correction, the approved plan may state bounded document checks instead. Any waiver or combination of an otherwise applicable R0/R1 requires the Owner's explicit recorded decision identifying the scope and reason; a Driver or Reviewer cannot silently supply it.

The maintainer assignment on 2026-10-07 is Codex as Driver, Claude as Reviewer and the human Owner as arbiter, unless the Owner explicitly assigns otherwise. This dated assignment does not restrict an external contributor's tools or an adopter's runtime roles. Report the actual participants and any limits on review independence.

Before a task record exists, use the Draft decision document that is itself the subject of the proposed review. Do not append selection or review material to an Accepted decision, a shipped or normative document, or the Development Index. If no such Draft is suitable, use one plainly named, source-only review note under `docs/development/` without a serial task ID. Follow the public-safe disclosure rules above and record the Owner's selection decision and the preliminary review in that same location. After plan approval creates the development record, link the retained review or transfer its exact contents and leave a dated historical pointer; designate one owner for subsequent progress. A preliminary review record does not itself select or start a task.

The Reviewer reports findings; the Driver records accept, revise, defend or needs-user and performs only authorized changes. Use a fresh reviewer session where practical and identify the actual model/session, supplied context and limits on independence. The Owner normally relays packets. An explicitly authorized CLI review may transmit and collect a fixed packet; it creates no standing orchestration or permission beyond the authorization's named scope. An explicit authorization may cover bounded follow-up rounds and payload changes; preserve input identity, disclosure checks and authentication checks for every round without asking again solely because those bytes changed. Before invocation verify the expected non-secret authentication/billing path and authorized data disclosure. A mismatch stops invocation. Use no tools for a static review. If execution is authorized, fix commands, arguments, runtime, working directory, timeout and output/write boundary; deny unneeded network and credentials. A worktree alone is not an execution sandbox.

Keep the request, exact input identity, verbatim final reviewer response, Driver dispositions and actual Owner decisions distinct in that designated record. For uncommitted inputs record the base and diff digest plus relevant inputs outside the diff. Detect drift before and after; an unexplained change invalidates the affected evidence. Preserve the records and exact bytes needed to support acceptance or closeout through an authorized commit or recoverable retention; a digest alone cannot restore them. Retain additional raw evidence only for a named recovery, qualification, reuse or delivery consumer, with its end condition. Never present a static inference as an executed test or a passing suite as Owner acceptance.

Execute the approved scope and checks under [Maintaining](docs/MAINTAINING.md). Stop the affected action for a safety discrepancy, unknown state, missing recovery input, exhausted bound or required scope/contract change. Preserve the state and essential failure facts, explain the next bounded recovery proposal and obtain any authorization it needs. Do not silently add new commands or retries, delete history, weaken a test, or raise a timeout to manufacture success.

### Resume, Handoff And Close

On resume, identify the exact checkout/branch, current changes, designated progress record, accepted scope and remaining time/attempt limits. Compare current inputs with the recorded checkpoint before acting. An approval restricted to different exact bytes does not authorize a changed result. A recorded scope authorization that explicitly covers bounded corrections remains applicable within those limits; verify its conditions rather than inferring or silently expanding them. Continue the existing record when it owns the task; do not duplicate it because the conversation or checkout changed. A suspended task states why it stopped, what remains and the concrete resumption condition. These are readable dispositions in a plain document, not a new runtime lifecycle enum.

An exceptional task handoff identifies the remaining prospective scope, previous record and exact revision, new owner/record, preserved completed evidence, unmet criteria, checks and stop conditions. Activate the new owner only with the Owner's acceptance of that exact handoff and verification of both sides. Update the old location to a dated historical pointer in the same cutover; never keep two live progress owners. Sensitive provenance may remain private, but the new record must explain the remaining task without requiring private history. A candidate with no active development task needs candidate intake, not an invented task transfer.

Close as completed only after the agreed completion criteria and required Owner acceptance are met. Report executed, inherited and unverified evidence separately, disposition review findings, preserve required inputs/results, and state any deferred work with its reason and reconsideration condition. A passing check, published release or merged PR alone does not close a task. Dropping work after it has started requires an explicit Owner decision: preserve the reason, unfinished criteria and required evidence, retire its ID, and do not report it as completed. Later work does not rewrite a closed result; create a separately authorized follow-up when needed. Update navigation under the authorization above, without a second progress ledger.

Assess generic adopter impact using Maintaining and report update recommended, no update currently needed, or installation state unverified. Private target observations and exact application approvals remain with the Owner or designated maintainer. An adopter issue becomes a minimal anonymous or synthetic source candidate/task, followed by the qualified source change, separately approved exact application and recheck of the original case. An unsafe or unsupported application stops and preserves truth. This procedure does not authorize detach to bypass an unsupported update. Portfolio coordination (priorities and resources across separate products) is a separate action, not a prerequisite to source result acceptance unless explicitly included in that task's criteria.

Commit, push, PR creation, merge, public release and actual adopter application retain the explicit authorization boundaries above. This procedure installs no runtime, grants no new command, changes no technical contract and launches no background scheduler or cross-repository synchronization.
