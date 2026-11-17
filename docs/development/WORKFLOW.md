# Source Project Rules And Development Workflow

Use these source-project rules to select, carry out, review, resume and close work on Colvia itself. The readers are the Owner, Driver, Reviewer and an agent explicitly directed to this source entry. [Agent Collaboration](#agent-collaboration) contains invocation requirements when agents are used.

Reorganization and effective-state record: [DR-0006](../decisions/DR-0006-source-contributor-document-structure.md). Until the Owner accepts and activates its exact amendment, use the [retained accepted source procedures](../DECISION-GUIDE.md#retained-source-procedures). After that recorded activation, the identified version of this workflow owns the relocated task rules. Consult DR-0006 for the actual state; this entry does not activate them or install a runtime.

[Maintaining](../MAINTAINING.md) remains the technical-validation authority. [Decision Guide](../DECISION-GUIDE.md) owns decision identities, states and exact acceptance. One selected task keeps one progress record; the Development Index locates it rather than duplicating progress.

## Purpose, Ownership And Basis

The human Owner decides the project's rules and their accepted changes. The Driver maintains the authorized documents and evidence; the Reviewer reports findings. The responsibilities in [Roles And Authorization](#roles-and-authorization) govern those actions.

The relocated rules come from CONTRIBUTING at source revision `d86bd1fd7754144e5c8538712724ae78571941bf`, including the decision procedure accepted on 2026-10-07 and the development procedure activated by [DR-0003](../decisions/DR-0003-source-development-procedure-and-bounded-intake.md). [DR-0006](../decisions/DR-0006-source-contributor-document-structure.md) identifies the proposed destination clauses and exact acceptance boundary; [retained source procedures](../DECISION-GUIDE.md#retained-source-procedures) preserve their historical identity.

The document organization follows [Repository-Owned Rules](../REFERENCE.md#repository-owned-rules) at that same source revision. Purpose, owner, basis and reading pointers describe the existing rules; they create no new approval condition or exception. Maintaining remains the technical-verification owner. The Decision Guide owns document identity, decision states and acceptance history.

## Source And Installed Project Entry

For Colvia source development, the explicitly supplied [CONTRIBUTING entry](../../CONTRIBUTING.md) or [Development Index](README.md) leads here. Source tasks use the plain development procedure below; runtime installation and typed Work creation are not prerequisites.

In an installed project, agents start with `./colvia view --details`, read its currently verified manual/adapter and follow that project's own rules. This source-only workflow is not installed or required by that entry. The original protections for external contributors and adopter roles in this procedure remain applicable; this reorganization does not decide a licensing or public contribution policy.

At the DR-0006 source-only relocation, the unchanged AGENTS/CLAUDE entry had no verified automatic route to these source rules. The separately accepted entry amendment identified in PATCH-20261018-002 adds a conditional route through source-only CONTRIBUTING when the agent is explicitly asked to develop Colvia itself in its trusted source checkout. An installed project still starts with its own rules and the verified manual/adapter from ./colvia view; presence inside a managed manual never selects source development. This route does not require runtime installation or typed Work creation, and adds no task-selection or execution authority. DR-0006's other relocated obligations and historical identities remain unchanged.

## Find Rules For The Task

This table helps locate rules. It does not narrow their applicability, waive a required read or replace any instruction below. In particular, [Start And Select](#start-and-select) still requires reading the Development Index and the existing owning record before selection. Follow every applicable rule, including duties outside the row that first led you here.

| Situation | Relevant Rule Or Canonical Guide |
| --- | --- |
| Select or plan source work | [Roles And Authorization](#roles-and-authorization), [Start And Select](#start-and-select), existing owning record |
| Propose or amend a decision | [Decision Guide](../DECISION-GUIDE.md#document-identity-and-state), [exact acceptance](../DECISION-GUIDE.md#acceptance-records) |
| Review or execute approved work | [Review And Evidence](#review-and-evidence), [Execute Within The Approved Boundary](#execute-within-the-approved-boundary), [Maintaining](../MAINTAINING.md#validation-frequency-and-native-timeouts) |
| Invoke an agent or reviewer CLI | Common review rules and [Agent Collaboration](#agent-collaboration) |
| Resume, hand off or close work | [Resume And Handoff](#resume-and-handoff), [Close And Assess Adopter Impact](#close-and-assess-adopter-impact) |
| Prepare a GitHub release | [GitHub Release Procedure](#github-release-procedure) |
| Publish, apply to an adopter or change rules | [Publication And Adopter Authorization](#publication-and-adopter-authorization), [Rule Changes And Retirement](#rule-changes-and-retirement) |

## Roles And Authorization

The human Owner decides material scope, policy acceptance and result acceptance. The Driver proposes and performs authorized work, records evidence and limits, and dispositions review findings. A Reviewer reports findings; a review verdict or passing check does not authorize edits or replace Owner acceptance.

A decision's acceptance does not start or transfer a task. The [Decision Guide's scope boundary](../DECISION-GUIDE.md#acceptance-records) remains effective: it does not establish a task tracker. The separately accepted source-development procedure below defines task selection and its single record. That approved record fulfills Maintaining's existing Work-narrative reference; no typed runtime Work is created.

## Start And Select

Use the [Documentation Index](../README.md) for the product overview and the [Decision Guide](../DECISION-GUIDE.md#decision-catalog) for the exact current technical activation records. Read the [Development Index](README.md) and any existing record that owns the requested work. Explain the observed state and remaining authorization before selecting another task. A recommendation, candidate entry, ambiguous request to continue, or contract Draft does not authorize implementation. Do not infer an unrecorded choice from an empty list or a closed task.

Keep an unselected candidate as a title with purpose, reason for deferral and a concrete reconsideration condition when known. Do not allocate a development record ID or publish a runtime intent merely to store an idea. After the Owner selects a bounded task and approves its plan, create one source-owned record under `docs/development/<record-ID>-<topic>.md`. Use `{FEAT|PATCH|HOTFIX|CHORE}-YYYYMMDD-NNN`, with the start date and next unused three-digit sequence shared across all four prefixes for that date. FEAT denotes a new capability, PATCH a bounded correction, HOTFIX an urgent correction, and CHORE maintenance or documentation work; a decision-review task defaults to CHORE. Check current files and retained history before allocation; never reuse an ID. This check is not an atomic reservation. If a collision appears, stop allocation and confirm one unused ID and one owning record before continuing. These are plain development document IDs, not runtime Work IDs. Creating the document creates no runtime Work, intent, authority home or lifecycle state.

Here plan approval means the Owner authorizes execution of the named scope; it does not authorize Git/adopter actions or accept the resulting work. The approved development record fulfills Maintaining's reference to an existing Work narrative; the preliminary review note does not. Runtime installation is not required.

A development record states its purpose, owner, scope/exclusions, completion criteria, exact starting inputs, authorized plan, verification and time/attempt limits, current disposition, remaining work and next decision. Record proposal, execution evidence, review disposition and actual Owner acceptance distinctly. Keep detailed progress in that one record. The index locates candidates and records and holds unselected candidates' criteria; it does not mirror task progress. On selection, the task references the exact intake/criteria revision and any explicitly linked prior closeout/disposition, and owns progress only for criteria within its authorized scope. At closeout record each affected criterion's result and residual work; the next task reads those explicit links, never a timestamp-derived latest result. The index links closeouts without mirroring their progress. A decision's open points remain contract choices; the task records their review and resolution without creating a second technical decision owner.

### Candidate And Navigation Changes

Record a new unselected source-originated idea in the Development Index's New Source Candidates section, with its title, purpose, deferral/reconsideration condition when known and a link to the dated, revision-identified Owner planning authorization. Keep that authorization in the subject Draft or a source-only planning/review note as described below, not as selection/review prose in the index. A new self-contained, public-safe request, including a new anonymized adopter issue, uses this route regardless of its origin; an existing external legacy candidate still needs the handoff amendment. Record the idea entry's resulting revision and bounded diff in that authorizing record. Later edits or dropped notices use the same kind of dated Owner planning record while preserving the earlier snapshot meaning. This authorization permits adding the new idea's purpose and conditions in that designated section; it is distinct from navigation maintenance and does not require an amendment per idea. Do not copy or relabel an accepted legacy candidate there to evade its criteria or amendment boundary. A directly selected new task may go straight to its approved-plan development record and an index task link. Changing that task's agreed scope requires the relevant Owner plan decision; changing a technical contract still needs its named accepted amendment. Bringing in another legacy external candidate, changing this procedure or changing accepted intake criteria/scope requires an Owner-accepted amendment to DR-0003. Within the accepted intake, navigation means task/closeout links and candidate selected/closed/dropped notices backed by the relevant Owner record. It does not include criteria, purpose or execution boundaries. Record the changed revision and bounded diff in the authorizing task, subject Draft or source-only planning/review note described here. A navigation edit grants no wider scope. Keep dated intake observations as snapshots instead of updating them as progress. Do not create separate STATUS/backlog/receipt registries or automatically mirror progress elsewhere.

### Preliminary Review Location

Before a task record exists, use the Draft decision document that is itself the subject of the proposed review. Do not append selection or review material to an Accepted decision, a shipped or normative document, or the Development Index. If no such Draft is suitable, use one plainly named, source-only review note under `docs/development/` without a serial task ID. Follow the [Disclosure](#disclosure) rules and record the Owner's selection decision and the preliminary review in that same location. After plan approval creates the development record, link the retained review or transfer its exact contents and leave a dated historical pointer; designate one owner for subsequent progress. A preliminary review record does not itself select or start a task.

## Review And Evidence

R0 reviews a plan before execution approval; R1 reviews the resulting change before result acceptance. Their separate boundaries apply by default to all changes, including tests, runners, safety oracles and behavior-preserving refactors. The only default exception is a pure typo or navigation correction. A pure typo correction does not change executable behavior, assertions, criteria or authority. HOTFIX is not an automatic waiver. For a pure typo or navigation correction, the approved plan may state bounded document checks instead. Any waiver or combination of an otherwise applicable R0/R1 requires the Owner's explicit recorded decision identifying the scope and reason; a Driver or Reviewer cannot silently supply it.

Keep the review request, exact input identity, final reviewer response, Driver dispositions and actual Owner decisions distinct in the decision or its existing task record. Use `accept`, `revise`, `defend` or `needs-user` for each finding. Preserve the final reviewer response verbatim. Report actual model/session identity and any limits on independence. A static reading, executed check and reproduced counterexample are different evidence.

Keep the request, exact input identity, verbatim final reviewer response, Driver dispositions and actual Owner decisions distinct in the designated record (task record, subject Draft or [Preliminary Review Location](#preliminary-review-location)). For uncommitted inputs record the base and diff digest plus relevant inputs outside the diff. Detect drift before and after; an unexplained change invalidates the affected evidence. Preserve the records and exact bytes needed to support acceptance or closeout through an authorized commit or recoverable retention; a digest alone cannot restore them. Retain additional raw evidence only for a named recovery, qualification, reuse or delivery consumer, with its end condition. Never present a static inference as an executed test or a passing suite as Owner acceptance.

The Reviewer reports findings; the Driver records accept, revise, defend or needs-user and performs only authorized changes.

For agent or CLI reviews, follow [Agent Collaboration](#agent-collaboration) before invocation. A fixed packet and a fresh session limit shared context; they do not by themselves establish an independent or exhaustive review.

## Execute Within The Approved Boundary

For changed source, use Maintaining to choose checks and report actual results, inherited evidence and unverified limits separately. Preserve extra raw evidence only for an identified failure, qualification, reuse or delivery need and record its end condition. Avoid copying a whole source tree or adding a validation archive for every check.

Execute the approved scope and checks under [Maintaining](../MAINTAINING.md). Stop the affected action for a safety discrepancy, unknown state, missing recovery input, exhausted bound or required scope/contract change. Preserve the state and essential failure facts, explain the next bounded recovery proposal and obtain any authorization it needs. Do not silently add new commands or retries, delete history, weaken a test, or raise a timeout to manufacture success.

[Maintaining: Evidence Reuse And Selection](../MAINTAINING.md#evidence-reuse-and-selection) owns the cumulative-risk assessment and distinguishes new checks, inherited evidence and unavailable evidence.

## Resume And Handoff

On resume, identify the exact checkout/branch, current changes, designated progress record, accepted scope and remaining time/attempt limits. Compare current inputs with the recorded checkpoint before acting. An approval restricted to different exact bytes does not authorize a changed result. A recorded scope authorization that explicitly covers bounded corrections remains applicable within those limits; verify its conditions rather than inferring or silently expanding them. Continue the existing record when it owns the task; do not duplicate it because the conversation or checkout changed. A suspended task states why it stopped, what remains and the concrete resumption condition. These are readable dispositions in a plain document, not a new runtime lifecycle enum.

An exceptional task handoff identifies the remaining prospective scope, previous record and exact revision, new owner/record, preserved completed evidence, unmet criteria, checks and stop conditions. Activate the new owner only with the Owner's acceptance of that exact handoff and verification of both sides. Update the old location to a dated historical pointer in the same cutover; never keep two live progress owners. Sensitive provenance may remain private, but the new record must explain the remaining task without requiring private history. A candidate with no active development task needs candidate intake, not an invented task transfer.

## Close And Assess Adopter Impact

Close as completed only after the agreed completion criteria and required Owner acceptance are met. Report executed, inherited and unverified evidence separately, disposition review findings, preserve required inputs/results, and state any deferred work with its reason and reconsideration condition. A passing check, published release or merged PR alone does not close a task. Dropping work after it has started requires an explicit Owner decision: preserve the reason, unfinished criteria and required evidence, retire its ID, and do not report it as completed. Later work does not rewrite a closed result; create a separately authorized follow-up when needed. Update navigation under [Candidate And Navigation Changes](#candidate-and-navigation-changes), without a second progress ledger.

Contributors assess generic product impact from source evidence. The Owner or a designated maintainer checks known private adopters and records application decisions in private operations records; external contributors need not access that inventory. Unknown installation state remains unverified. Follow [Adopter Impact At Development Closeout](../MAINTAINING.md#adopter-impact-at-development-closeout) without treating source acceptance as permission to update an adopter.

Assess generic adopter impact using Maintaining and report update recommended, no update currently needed, or installation state unverified. Private target observations and exact application approvals remain with the Owner or designated maintainer. An adopter issue becomes a minimal anonymous or synthetic source candidate/task, followed by the qualified source change, separately approved exact application and recheck of the original case. An unsafe or unsupported application stops and preserves truth. This procedure does not authorize detach to bypass an unsupported update. Portfolio coordination (priorities and resources across separate products) is a separate action, not a prerequisite to source result acceptance unless explicitly included in that task's criteria.

At checkpoints, review closeout, handoff and task completion, follow the active working agreements for worktree preservation and cleanup. See the owning task record for any retained worktree’s purpose, consumer and condition for removal.

## Publication And Adopter Authorization

Obtain explicit Owner authorization for commit, push, PR creation, merge, public release and actual adopter application when those actions are not already authorized for the named target and scope. Review or result acceptance alone authorizes none of these actions. Do not infer execution authority from a candidate, recommendation or old task, and do not ask again for work already covered by an applicable authorization.

Commit, push, PR creation, merge, public release and actual adopter application retain the explicit authorization boundaries in this section. This procedure installs no runtime, grants no new command, changes no technical contract and launches no background scheduler or cross-repository synchronization.

### GitHub Release Procedure

When preparing a Colvia release on GitHub, load `github-release-guide`. Use `first-public` when making the private source repository public and `version-release` for new releases from a public repository. Start with read-only Assess and reuse applicable evidence from the release record. In Guided mode, show the exact target and effect, recheck the preconditions, obtain the Owner's approval for the specific action, and verify the observed result before continuing. Source visibility, repository settings, Git refs and GitHub Release objects have separate approval boundaries.

Use Colvia's existing release plan for signing, Pages deployment and installation checks. Approval for a Pages deployment covers the specified installation files at the public URL. A GitHub Release or a change to source visibility requires its own approval.

For each new public version, add the Owner’s daily-use installation to the release closeout checklist. After verifying the official distribution, the Owner applies the approved release to that installation and runs `colvia-manage status`. Record the installed version alongside the published version and close this check only when they match. If local application is pending, carry the check forward in the release record.

## Agent Collaboration

These requirements apply at least to agent review or execution invocations; they narrow no common review duty and do not prescribe an external contributor's tools or an adopter's runtime roles.

The maintainer assignment on 2026-10-07 is Codex as Driver, Claude as Reviewer and the human Owner as arbiter, unless the Owner explicitly assigns otherwise. This dated assignment does not restrict an external contributor's tools or an adopter's runtime roles. Report the actual participants and any limits on review independence.

Use a fresh reviewer session where practical and identify the actual model/session, supplied context and limits on independence. The Owner normally relays packets. An explicitly authorized CLI review may transmit and collect a fixed packet; it creates no standing orchestration or permission beyond the authorization's named scope. An explicit authorization may cover bounded follow-up rounds and payload changes; preserve input identity, disclosure checks and authentication checks for every round without asking again solely because those bytes changed. Before invocation verify the expected non-secret authentication/billing path and authorized data disclosure. A mismatch stops invocation. Use no tools for a static review. If execution is authorized, fix commands, arguments, runtime, working directory, timeout and output/write boundary; deny unneeded network and credentials. A worktree alone is not an execution sandbox.

The common [Review And Evidence](#review-and-evidence) requirements still apply: retain the exact request and input identity, verbatim final response, Driver dispositions and actual Owner decisions, and detect input drift before and after a round. This summary does not create a second evidence owner.

## Disclosure

Keep private repository/owner names, paths, revisions, branches and identifiable comparison provenance out of public-intent source documents, frontmatter and Git history. Preserve required legal attribution. A public technical rationale must stand on its own even when sensitive historical correspondence stays private.

The [Agent Collaboration](#agent-collaboration) authorization check applies to the actual data transmission. Private material may be sent only when that transmission is explicitly authorized; authorization to send it to a reviewer does not authorize public disclosure. Preserve the public-intent rule above for source, records and Git history.

## Rule Changes And Retirement

The existing amendment route applies to these rules: [Candidate And Navigation Changes](#candidate-and-navigation-changes) requires an Owner-accepted amendment to DR-0003 for a development-procedure change. A change to the decision procedure accepted on 2026-10-07 likewise requires an Owner-accepted named amendment. [Decision Guide](../DECISION-GUIDE.md#document-identity-and-state) defines named amended/replaced clauses, preserved unaffected meaning and the decision states. Retirement follows that same applicable route; a heading change, newer source version or runtime update does not retire an accepted obligation.

Compare the retained source basis, proposed change and local requirements, using the clause mapping in the named amendment. Preserve required historical bytes and identify the changed pointers, verification and unresolved policy choices in the existing task/decision record. These are pointers to the existing amendment, preservation and evidence duties, not a new rule lifecycle, acceptance mechanism or maintenance registry.
