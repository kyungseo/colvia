---
id: DR-0006
status: Accepted
date: 2026-10-16
---

# DR-0006: Source Project Rules And Development Workflow

## Question

How can the Owner, Driver, Reviewer and an agent explicitly given the source entry find the applicable Colvia source-project rules, distinguish decision rules from task execution, and preserve every accepted obligation and historical identity without imposing source-development rules on installed projects?

## Decision

Accept and activate the source-only document relocation defined by Proposed Structure, Proposed Clause Mapping, Proposed Amended Records and Named Development Index Cutover, effective 2026-10-16. CONTRIBUTING is the source-rule entry; the Decision Guide owns decision rules and acceptance history; Source Project Rules And Development Workflow owns the relocated common rules and development procedure. The Development Index retains its existing criteria and task-navigation role.

This is the named location amendment to DR-0003 and to the decision procedure accepted on 2026-10-07. All unaffected obligations, exceptions and accepted historical identities remain effective. The exact accepted result and activated destinations are identified in Acceptance And Activation Record — 2026-10-16 below. No shipped entry, runtime, technical contract, public contribution policy or Git action is authorized by this decision.

## Context And Scope

The proposal wording below is retained as the reviewed preparation record. Its Draft/proposed labels and then-pending authorization statements describe that preparation. The Decision and dated acceptance/activation record govern the now-accepted scope; they do not rewrite earlier checks or approvals.

The Owner authorized drafting, bounded document checks and Claude result review on 2026-10-16. The [selected task](../development/CHORE-20261016-002-contributor-document-restructure.md) records that execution scope. This Draft is neither amendment acceptance/activation nor result acceptance. Commit, push, PR, merge, release and adopter actions remain separately authorized.

At source revision `d86bd1fd7754144e5c8538712724ae78571941bf`, CONTRIBUTING combines the accepted decision procedure and the separately accepted development appendix. The latter is effective through [DR-0003](DR-0003-source-development-procedure-and-bounded-intake.md), despite its preserved Proposed label. [DR-0004](DR-0004-colvia-managed-entry-and-one-way-transition.md) changes named technical/current-set clauses; it does not remove the remaining source-development obligations.

This proposal changes only source-document responsibility and navigation. It leaves the exact eleven technical members, managed29 inventory, runtime, tests and shipped entry surfaces unchanged. `docs/MAINTAINING.md` remains the technical verification and adopter-impact authority. AGENTS, CLAUDE, root README and docs/README are shipped entry/navigation surfaces; their unchanged bytes are protected here without incorrectly treating all of them as members of the normative eleven.

## Proposed Structure

- [CONTRIBUTING](../../CONTRIBUTING.md): short source-rule entry and historical locators; no newly authored general contribution policy or duplicated runtime/check instructions.
- [Decision Guide](../DECISION-GUIDE.md): document identities/states, exact decision acceptance/activation and retained history.
- [Source Project Rules And Development Workflow](../development/WORKFLOW.md): existing common rules, task selection and one progress record, R0/R1, execution, resume/handoff/closeout, disclosure and Agent Collaboration; purpose/ownership/basis and task-based reading provide navigation without changing applicability.
- [Development Index](../development/README.md): current procedure-location links and the selected task link; preserve dated intake criteria and unrelated task records.

The decision guide does not create a task tracker. The separately accepted development procedure still selects and owns one plain task record, fulfilling Maintaining's Work-narrative reference. A guide, DR, branch or record does not create typed runtime authority.

## Revised Direction And Clause Classification

The earlier unaccepted draft emphasized general contributor onboarding. The Owner instead approved a source-project rule reorganization and this title, retaining DR-0006's ID and path. Earlier review/check evidence remains tied to its earlier inputs; it does not accept the revised result. Licensing, external contribution and external PR policy remain outside this task and are deferred to a separately selected public-transition scope.

| Class | Treatment |
| --- | --- |
| A: accepted procedure clauses at the identified base | Preserve all duties, exceptions and authority. This includes external contributors not needing private adopter inventory and the dated agent assignment not restricting their tools or adopter roles. |
| B: additions in the earlier unaccepted contributor-oriented draft | Remove general issue/PR-preparation instructions, the added contributor-PR summary and duplicated checkout/runtime/check tables or commands. Link the existing technical owners instead; do not move duplicates into Workflow or edit shipped documents. |
| C: ambiguous policy or missing canonical information | Report the gap and stop the affected change for an explicit scope/policy decision. Do not delete an accepted clause by treating it as class B. |
| Descriptive navigation added by this reorganization | Purpose, owner, source basis, audience, reading table and rule-maintenance pointers describe existing authority and routes. The disclosure reminder that reviewer-transmission permission does not authorize public disclosure restates the existing separate transmission and public-intent duties. They grant no exception, mandatory-read waiver, new approval gate or new rule state. |

## Proposed Clause Mapping

Source references below mean CONTRIBUTING at `d86bd1fd7754144e5c8538712724ae78571941bf`, except where original accepted bytes are explicitly identified. Each normative obligation has one canonical destination; CONTRIBUTING and the Decision Guide's review pointers are summaries, not competing rules.

| Source Clause At The Pre-Reorganization Revision | Proposed Canonical Destination | Preserved Boundary |
| --- | --- | --- |
| Current-contract preamble; Decisions | Decision Guide: Decision Catalog; CONTRIBUTING points to it | Activated technical set and Draft proposals remain distinct; the entry adds the already activated First B1 supplement pointer |
| Roles And Authorization, paragraph 1 | Workflow: Roles And Authorization | Owner, Driver and Reviewer responsibilities; no reviewer self-acceptance |
| Roles And Authorization, paragraph 2 | Decision Guide: Acceptance Records | Exact content, date, scope, activation and limits; digest is not content preservation or authentication |
| Roles And Authorization, paragraph 3 | Workflow: Publication And Adopter Authorization | Named Git/adopter authority; no repeated request for an applicable authorization |
| Roles And Authorization, paragraph 4 | Decision Guide: Acceptance Records; Workflow links its task boundary | Decision acceptance does not establish/transfer a task; scope/criteria/plan/checks and one record before implementation |
| Document Identity And State, all paragraphs and state table | Decision Guide: Document Identity And State | Four-digit IDs, lineage, imports, never reuse, plain/typed identity distinction, states and amendment conditions |
| Review, Evidence And Disclosure, paragraph 1 | Workflow: Review And Evidence | Request/input/response/disposition/Owner separation; verbatim review and independence limits |
| Review, Evidence And Disclosure, paragraph 2 | Workflow: Execute Within The Approved Boundary, pointing to Maintaining | Selected checks and actual/inherited/unverified results; bounded extra evidence |
| Review, Evidence And Disclosure, paragraph 3 | Workflow: Disclosure | Public-intent provenance hygiene and legal attribution |
| Review, Evidence And Disclosure, paragraph 4 | Workflow: Close And Assess Adopter Impact | Generic contributor impact versus private maintainer observations; separate actual application |
| Procedure Acceptance; Additional Source Decisions | Decision Guide: History and Retained Source Procedures | Verbatim historical paragraphs, original coordinates and recoverable Git bytes; not new acceptance |
| Appendix preparation explanation and its DR table | Workflow effective-state entry; Decision Guide catalog/history | DR-0003's actual activation controls; preparation labels do not make it inactive |
| Start And Select, paragraph 1 | Workflow: Start And Select | Current contracts and existing task owner before selection; no inferred choice |
| Start And Select, paragraph 2 | Workflow: Start And Select | Named bounded task, date-wide shared sequence, collision stop, no typed runtime effects |
| Start And Select, paragraph 3 | Workflow: Start And Select | Plan approval authorizes its named execution only; approved record fulfills Maintaining narrative |
| Start And Select, paragraph 4 | Workflow: Start And Select | One progress owner; exact criteria/closeout links; index is navigation, no latest-wins succession |
| Start And Select, paragraph 5 | Workflow: Candidate And Navigation Changes | Dated authorization; new ideas versus legacy intake; recorded bounded diff; no extra trackers |
| Review And Execute, paragraph 1 | Workflow: Review And Evidence | R0/R1 boundaries, narrow typo/navigation exception, HOTFIX not waiver, explicit scoped waiver |
| Review And Execute, paragraph 2 | Workflow: Agent Collaboration | Original dated assignment and contributor/adopter tool freedom |
| Review And Execute, paragraph 3 | Workflow: Preliminary Review Location | Suitable Draft or unnumbered source-only review note; one owner after plan approval |
| Review And Execute, paragraph 4 | Workflow: Review And Evidence plus Agent Collaboration | Driver dispositions, explicit CLI scope, expected auth/billing, authorized transmission, tools-free static review and fixed execution sandbox |
| Review And Execute, paragraph 5 | Workflow: Review And Evidence | Verbatim records, identities/drift, recoverable inputs and bounded retention; evidence is not acceptance |
| Review And Execute, paragraph 6 | Workflow: Execute Within The Approved Boundary | Approved checks and safety/unknown/recovery/budget/scope stop conditions; no retries or weakened oracle by default |
| Resume, Handoff And Close, paragraph 1 | Workflow: Resume And Handoff | Exact checkout/inputs/remaining bounds; scoped corrections; no second task/lifecycle enum |
| Resume, Handoff And Close, paragraph 2 | Workflow: Resume And Handoff | Exact exceptional handoff, both sides, one live owner; candidate intake differs from task transfer |
| Resume, Handoff And Close, paragraph 3 | Workflow: Close And Assess Adopter Impact | Criteria plus Owner acceptance; dropping requires a decision; preserve closed history |
| Resume, Handoff And Close, paragraph 4 | Workflow: Close And Assess Adopter Impact | Generic impact, separate private application, anonymous source case, no detach workaround or portfolio prerequisite |
| Resume, Handoff And Close, paragraph 5 | Workflow: Publication And Adopter Authorization | Separate Git/adopter scope; no installed runtime, technical-contract change, scheduler or synchronization |
| Development Index procedure-location references in entry, intake notes, New Source Candidates, Task Records and Authorized Development Records | Development Index links to the workflow; this DR controls their cutover | These are named procedure-location changes, not permission to edit legacy criteria or another task's progress |


## Historical Identity And Preservation

[Decision Guide: Retained Source Procedures](../DECISION-GUIDE.md#retained-source-procedures) identifies the recoverable original `238514686078ce1564010a7b69013f48a635c57c` and the current pre-reorganization revision. The original prefix and appendix coordinates apply only to that historical CONTRIBUTING. Its 320-byte later preamble insertion is separately authorized source navigation, not corruption and not a reason to replace old acceptance hashes.

The original Procedure Acceptance paragraph and Additional Source Decisions section body are quoted verbatim in the Decision Guide's History, explicitly naming that historical scope. Existing DR-0001 through DR-0004 and closed task records retain their bytes and meaning. Retained inbound links resolve through the original CONTRIBUTING headings; relative references in relocated current procedure text point to their explicit new owner.

## Proposed Amended Records

Upon its own exact Owner acceptance and activation, DR-0006 is the named amendment to DR-0003 required by the retained development procedure, and to the source-location clauses of the decision procedure accepted on 2026-10-07. Until then, these are proposed amendments only. The affected clauses are:

- DR-0003 Decision, paragraphs 2 and 3: references to Contributing as the home of the source-development and decision procedures become references to the identified Workflow and Decision Guide respectively. Source ownership, one progress owner and all authorization boundaries remain unchanged.
- DR-0003 Proposed Decision, paragraph 1 and the navigation-authority paragraph beginning “One selected task”: the appended-procedure location and the authorizing-record rules “defined in Contributing” point to Workflow: Start And Select / Candidate And Navigation Changes. Its intake criteria, scope, snapshot and amendment duties remain unchanged.
- DR-0003 Proposed Current-Scope Authority Closure, paragraph 1, and its Bounded Dependency Disposition rows “Human/agent entry, references and closeout” and “Product planning, task/review ownership and feedback”: references to Contributing as the procedure/governance location point to the identified Decision Guide and Workflow. CONTRIBUTING remains the explicit source-rule entry; ownership, evidence limits and the authority frontier remain unchanged.
- DR-0003 Acceptance And Activation Record — 2026-10-08, the Contributing full-file and development-appendix rows: their byte coordinates and hashes remain exact historical evidence. They no longer identify the current procedure location after this amendment's recorded activation; the new exact destinations are identified here. The original accepted obligations remain effective through their mapped destinations.
- Procedure Acceptance — 2026-10-07 in the retained CONTRIBUTING: only the current home of that decision procedure changes to Decision Guide for decision rules and Workflow for its shared development/review duties, as mapped above. Its original prefix, acceptance scope, hash and historical wording remain unchanged.

DR-0003 already has effective state Accepted (Amended) through DR-0004; after this amendment activates, that state also covers these named location clauses. The future acceptance/activation record in DR-0006 will identify the exact amended clauses, destination bytes and effective date. The Decision Guide's catalog points to these records; no edit to DR-0003's preserved frontmatter, original status text, hashes or existing activation records is proposed. This amendment does not undo DR-0004's technical/current-set replacement, supersede all of DR-0003 or change the retained procedure's substantive obligations.

## Proposed Reference Cutover

The amendment's exact destination set is CONTRIBUTING, Decision Guide, Source Project Rules And Development Workflow, and the Development Index's named procedure-location changes. The future acceptance must also identify this DR's exact revision and the bounded index diff. The selected task is the record of checks, review and the eventual human decision, not an additional normative procedure document.

Before activation, the new entry and both guides point to this Draft and the retained effective source procedure; their imperative text is conditional on that activation, not newly effective policy. The entry and guides describe both states and defer to this record, so their exact accepted bytes need no pending-banner rewrite after activation. The revised Development Index likewise makes its procedure-location cutover conditional on this DR. The task link itself is authorized navigation for the selected work and grants no broader amendment authority.

No automatic source-agent discovery is claimed. Static reading paths through root CONTRIBUTING and the Development Index are checked; the existing AGENTS to Maintaining closeout path is unchanged. Changing shipped entry routing, release identity or adopter behavior would require a separately selected scope and its applicable checks.

A parallel source task already uses DR-0005 and edits the Development Index. This task allocates DR-0006 after checking current files, registered worktrees and retained history. That observation is not an atomic reservation. Recheck IDs, shared index changes and relevant catalog rows before integration; preserve the other task's record and changes rather than replacing the whole index.

## Named Development Index Cutover

The exact bounded index diff accompanies the amendment acceptance. The affected passages are the entry preamble's procedure location, the Continuation Scope And Remaining Criteria authorizing-record pointer, New Source Candidates' authorization/preliminary-review pointers, and Task Records' preliminary-review pointer. These procedure-location changes require this named amendment; ordinary task navigation does not authorize them. Reading order stays in Workflow.

The existing CHORE link and its description under Authorized Development Records are task navigation under the Owner's selected-task authorization. Updating that description for this revised scope is distinct from activation of the procedure-location changes. No criteria, dated snapshot, other task progress or new candidate is changed. The complete changed index diff is identified with the final six-file result.

## Entry Scope And Reader Checks

| Reader Scenario | Explicit Starting Point And Expected Destination | Required Boundary |
| --- | --- | --- |
| Source task start | CONTRIBUTING or Development Index to Workflow: Roles And Authorization and Start And Select, then the index and existing owning record | Selection reads remain mandatory; no runtime installation or typed Work is implied |
| Decision change | Source entry to Decision Guide: Document Identity And State / Acceptance Records and named predecessor clauses | Draft, acceptance and activation remain distinct; a decision does not start execution |
| Review and resume | Source entry to Workflow: Review And Evidence / applicable Agent Collaboration / Resume And Handoff and the existing task record | Actual review, authorization, remaining bounds and single progress owner remain visible |
| Installed-project use | Installed project entry to `./colvia view`, verified manual/adapter and that project's own rules | No requirement to load the Colvia source-only rules; this check is static, not an installation exercise |

The unchanged AGENTS/CLAUDE entry has no direct route to these source rules. Automatic discovery, actual agent compliance and human comprehension remain unverified. A request to complete that source-agent entry route would trigger a separate shipped-entry scope, inventory/consumer-path and entry/resume checks, and any applicable contract/release decisions. It is deferred work, not a newly created candidate or an upstream message. No shipped entry is changed by this amendment.

## Verification Plan

1. Match every old clause to its destination and check obligation strength, exceptions, actors, permission and execution boundaries.
2. Recover original accepted ranges from Git, compare their SHA-256 values and verify that the current pre-reorganization file differs only by the authorized preamble.
3. Collect incoming references from tracked Markdown at the identified candidate revision as well as outgoing links. Classify historical locators and current procedure descriptions; check links/anchors and GFM rendering. If an unchanged shipped current description would become false, stop the affected change and report the separately needed scope. External references remain unverified.
4. Compare all out-of-scope tracked bytes/modes with the starting revision, including normative11, managed29, runtime, tests, shipped entry surfaces and old decisions/history. Check for unexpected untracked files.
5. Trace the four explicit reader scenarios above; compare known concurrent decision/index changes read-only before integration. Do not claim automatic discovery, actual installation or coverage of every external checkout.
6. Obtain the authorized Claude R1 result review, preserve its exact response and Driver dispositions, and report static reasoning separately from executed document checks.

For this revised direction, the task allows at most three document-check rounds of 60 seconds each and three tools-free Claude rounds of 300 seconds each: one R0, one R1 and one shared follow-up. The revised-plan R0 has consumed one review; the earlier direction's checks and reviews are separately recorded history. Non-shipped prose is checked under Maintaining; no product suite, native runtime qualification or real-user comprehension exercise is claimed. An unexplained drift, scope expansion, collision or exhausted bound stops the affected action.

## Promotion Conditions

- The Owner accepts the exact identified destination bytes, this DR revision and the named Development Index cutover, including which clauses replace the old location and which historical obligations remain.
- The selected task records the final identities, coverage, executed checks, review/dispositions and remaining limits. No unfinished required correction is hidden by a passing check or reviewer verdict.
- The Owner explicitly determines when the accepted amendment takes effect. Until then the original accepted procedure remains effective at the retained source revision. Do not edit old acceptance hashes, statuses or closed records to manufacture activation.
- This proposal assumes source publication of the new guide routes occurs with or after recorded activation, under separate Git authorization. Publication before activation is not the proposed cutover; choosing it requires an explicitly revised, reviewed reader-path plan and applicable Owner authorization. Conditional state pointers remain truthful before and after activation, so no frozen-label override or unreviewed post-acceptance banner edit is needed.
- Result acceptance is separately recorded for the authorized document task. Commit, push, PR, merge, public release and actual adopter application remain separate; no task or decision document grants those actions implicitly.

## Rationale

Separate the source entry, decision rules and task procedure so the Owner, Driver, Reviewer and an explicitly directed agent can find the relevant rules. Preserve the accepted obligations and historical evidence through a named, exact relocation instead of treating a document move as permission to change policy. Keep technical validation with Maintaining and installed projects with their own verified entry and project rules.

## Consequences

The identified source guides now own the relocated rules, and the named index references take effect. Historical CONTRIBUTING anchors and original acceptance bytes remain preserved. Later substantive changes require their applicable named amendment and Owner decision.

Automatic discovery from AGENTS/CLAUDE, public contribution/licensing policy, runtime/adopter execution and actual reader comprehension remain outside this accepted outcome. Source publication may occur only with the separately required Git authorization; actual adopter application and release qualification remain separate.

## Reversal Cost

Low while this is a Draft: the old bytes remain recoverable and no runtime/adopter state changes. After source navigation is activated, a later change must preserve the accepted lineage and inbound historical locators; silently restoring old paths would not revoke a recorded decision.

## Acceptance And Activation Record — 2026-10-16

The human Owner accepted the exact final six-file result and explicitly approved acceptance and activation of this DR's proposed scope on 2026-10-16. The verbatim decision is in the selected task's Owner Result Acceptance And DR-0006 Activation record. Activation takes effect on that date in this source document lineage; it does not claim a commit, publication, installation or release.

### Exact Accepted Result

The Owner's phrase “final checked six files” identifies document round 3 (PASS, 1.671 seconds), based on source revision `d86bd1fd7754144e5c8538712724ae78571941bf`, with these exact pre-record identities:

| Accepted Result Path | UTF-8 Bytes | SHA-256 |
| --- | --- | --- |
| `CONTRIBUTING.md` | 3687 | `0ed8e25817789c077edb0195b8a47dfa7a449d8d303320d885bf7688dffa4eb4` |
| `docs/DECISION-GUIDE.md` | 11498 | `3dad40b98fe829e8c53e0d3814b1f47035c5bafd8ff1dc738535d723dd74cb0e` |
| `docs/development/WORKFLOW.md` | 22786 | `8ca8cb79aa4bd837cedc39d6b213bb1c7799a394d52fcbc7401828570e6708f2` |
| `docs/development/README.md` | 47217 | `bbeba4888fca6eb1dfa859b5cfc812d88ef0ce8976fa1d7e2033b10c712556a9` |
| `docs/decisions/DR-0006-source-contributor-document-structure.md` | 22081 | `593cb3519d465201640133cebbcfeba08f41a6cc4fa10036722ede10e65c14fd` |
| `docs/development/CHORE-20261016-002-contributor-document-restructure.md` | 120795 | `2c83613e30172f6d703840dc8f4f7fc063adb5ca922f6e4ff7d599dcedc4c7fe` |

Tracked-diff SHA-256 for that result: `9f08ec0a3016dcab11adb6c088d09f2636f2f4b9cfb986d9b93272e6ea075c6a`. The four new untracked files are identified individually above; the tracked diff alone does not include them. Exact accepted bytes that the acceptance-record update changes are retained recoverably in the task's durable preservation location; hashes alone are not their recovery source. CONTRIBUTING and WORKFLOW remain byte-identical to the accepted result.

### Activated Scope And Destinations

The accepted scope is exactly the proposal identified above, including every named predecessor clause in Proposed Amended Records and the index passages in Named Development Index Cutover. DR-0003 remains Accepted (Amended); this activation adds its named procedure-location amendment without changing its old bytes, hashes, original activation, technical/current-set successor or unaffected meaning. The 2026-10-07 decision procedure changes its current location only.

The following destination identities include only the Owner-requested acceptance bookkeeping: the Decision Guide's two catalog states and relocation-state noun, and the index's task acceptance notice. Their procedural content and accepted index criteria are unchanged. These metadata/navigation updates record the Owner decision; they introduce no new proposed policy.

| Activated Destination | SHA-256 |
| --- | --- |
| `CONTRIBUTING.md` | `0ed8e25817789c077edb0195b8a47dfa7a449d8d303320d885bf7688dffa4eb4` |
| `docs/DECISION-GUIDE.md` | `fa7be5c7447e434faf6195861b20a6702fe2be3d8efe6c3d13f55689f64b2af9` |
| `docs/development/WORKFLOW.md` | `8ca8cb79aa4bd837cedc39d6b213bb1c7799a394d52fcbc7401828570e6708f2` |
| `docs/development/README.md` | `f3d4c64f1b58e4c773ac5c82662f225abc99484f5011e84165366dfc4a3c9a5e` |

This DR's accepted proposal is the pre-record identity in the six-file table. Its post-record decision body is UTF-8 bytes `[0, 24337)`, SHA-256 `4c903dd4e9b1ec37d15e0f5d0988f565fa6f0ce3075052927e8cf23e5fb6a2e3`; that range ends immediately before this acceptance record. It contains the Accepted status, Decision, Rationale, Consequences and a historical-label explanation. The enclosing acceptance record is reported Owner evidence, not a self-authenticating approval or an acceptance of future edits.

### Exact Named Index Cutover

The reviewed and accepted index diff against the base has SHA-256 `36837b4a52438ab10ddedb18cd1667063af4d250a6ffa3fdb82da1545628d614`. The complete bounded diff follows as a JSON array of exact lines; concatenate the decoded strings to recover its original UTF-8 bytes. Its task-navigation notice was subsequently updated only to record the acceptance stated above. No other task entry or criterion was changed.

```json
[
  "diff --git a/docs/development/README.md b/docs/development/README.md\n",
  "index 77be763..6ae4809 100644\n",
  "--- a/docs/development/README.md\n",
  "+++ b/docs/development/README.md\n",
  "@@ -2,7 +2,7 @@\n",
  " \n",
  " Current technical contract: [entry-1 amendment activation](../decisions/DR-0004-colvia-managed-entry-and-one-way-transition.md#entry-1-amendment-activation--2026-10-14); retained preparation labels identify historical inputs.\n",
  " \n",
  "-Preparation revision: this label and the Proposed headings identify the prepared bytes. This index has no effect as an intake/navigation surface unless [DR-0003](../decisions/DR-0003-source-development-procedure-and-bounded-intake.md) records Owner acceptance and verified activation of the identified intake/criteria revision and named scope. Consult that record for the current acceptance and activation state. Its initial full-file identity does not freeze later authorized navigation or New Source Candidates additions/edits; neither may alter accepted legacy criteria or scope. Record the resulting revision and bounded diff in the authorizing record. Use [Contributing](../../CONTRIBUTING.md#proposed-source-development-procedure) for the proposed procedure and [DR-0002 amendment](../decisions/DR-0002-checkout-1-contract-baseline.md#entry-1-amendment-activation--2026-10-14) for the current technical contract. The [Checkout-1 Structural Contract](CHECKOUT-1-STRUCTURE.md) remains part of that accepted technical set.\n",
  "+Preparation revision: this label and the Proposed headings identify the prepared bytes. This index has no effect as an intake/navigation surface unless [DR-0003](../decisions/DR-0003-source-development-procedure-and-bounded-intake.md) records Owner acceptance and verified activation of the identified intake/criteria revision and named scope. Consult that record for the current acceptance and activation state. Its initial full-file identity does not freeze later authorized navigation or New Source Candidates additions/edits; neither may alter accepted legacy criteria or scope. Record the resulting revision and bounded diff in the authorizing record. The destination procedure location is [Source Project Rules And Development Workflow](WORKFLOW.md), with exact relocation/cutover controlled by [DR-0006](../decisions/DR-0006-source-contributor-document-structure.md). Until that amendment is accepted and activated, the [retained accepted procedure](../DECISION-GUIDE.md#retained-source-procedures) remains effective. Use [DR-0002 amendment](../decisions/DR-0002-checkout-1-contract-baseline.md#entry-1-amendment-activation--2026-10-14) for the current technical contract. The [Checkout-1 Structural Contract](CHECKOUT-1-STRUCTURE.md) remains part of that accepted technical set.\n",
  " \n",
  " ## Proposed Intake\n",
  " \n",
  "@@ -23,7 +23,7 @@ Continuation records a Work's follow-up choice independently of its lifecycle. A\n",
  " \n",
  " The minimum `(P)` scope is the exact intent-to-Work reference, a Work-local continuation selection and a single cooperating writer/finalizer (the single writer that finalizes that continuation selection), as needed for onboarding and a fresh session to find the selected next action. Later `(L)` work covers priority rationale/history, typed triage and queue-health observations. Prior public/private timing statements are retained only in the historical section below; this procedure does not adopt or change support gates.\n",
  " \n",
  "-The right-hand column is the 2026-10-07 intake snapshot, not a live progress ledger. Once a task is selected, its development record references the exact criteria revision and explicitly linked prior closeout/disposition, and owns progress only within that task's scope; do not update this column to mirror it. Closeout states criterion-level residual work for the next separately authorized task. The index adds closeout links only; there is no umbrella progress ledger or timestamp-based succession. The requirements remain criteria for selecting and planning work, not accepted runtime extensions. Changing accepted criteria or intake scope requires an Owner-accepted amendment; task/closeout links and selected/closed/dropped navigation notices may follow the authorizing planning, selection or closeout record. Record their revision and bounded diff in the authorizing record defined in Contributing. Criteria, purpose and execution boundaries are not navigation.\n",
  "+The right-hand column is the 2026-10-07 intake snapshot, not a live progress ledger. Once a task is selected, its development record references the exact criteria revision and explicitly linked prior closeout/disposition, and owns progress only within that task's scope; do not update this column to mirror it. Closeout states criterion-level residual work for the next separately authorized task. The index adds closeout links only; there is no umbrella progress ledger or timestamp-based succession. The requirements remain criteria for selecting and planning work, not accepted runtime extensions. Changing accepted criteria or intake scope requires an Owner-accepted amendment; task/closeout links and selected/closed/dropped navigation notices may follow the authorizing planning, selection or closeout record. Record their revision and bounded diff in the authorizing record defined by [Candidate And Navigation Changes](WORKFLOW.md#candidate-and-navigation-changes), subject to the relocation boundary above. Criteria, purpose and execution boundaries are not navigation.\n",
  " \n",
  " | Criterion | Required outcome | Intake snapshot — 2026-10-07; not live progress |\n",
  " | --- | --- | --- |\n",
  "@@ -191,14 +191,16 @@ The private three-arm research obligation does not grant comparative claims: abs\n",
  " \n",
  " ## New Source Candidates\n",
  " \n",
  "-None recorded in this preparation. Under the Owner planning authorization defined in Contributing, add new source-originated unselected ideas here with title, purpose, known deferral/reconsideration condition and a link to that dated, revision-identified authorization. A new self-contained public-safe request, including a new anonymized adopter issue, uses this route regardless of origin; importing an existing external legacy candidate remains an amendment. Record additions/edits and their resulting revision/bounded diff in the authorizing record. Later edits or dropped notices follow the same kind of dated Owner planning record and preserve the earlier snapshot meaning. This is the designated ordinary idea-recording surface, separate from the accepted legacy intake above. Adding an idea here is allowed under that planning authorization even though purpose/conditions are not navigation; it does not require a DR-0003 amendment per idea. It creates neither an accepted technical contract nor execution authority. Do not use this section to copy, alter or evade accepted legacy criteria, import another external legacy candidate or change this procedure; those changes still need the named amendment. On selection the approved task owns its plan, criteria and progress; this section retains the dated idea and a task link, not a second progress ledger. Keep selection/R0 material in the Draft or planning/review note required by Contributing.\n",
  "+None recorded in this preparation. Under the Owner planning authorization in [Candidate And Navigation Changes](WORKFLOW.md#candidate-and-navigation-changes), subject to the relocation boundary above, add new source-originated unselected ideas here with title, purpose, known deferral/reconsideration condition and a link to that dated, revision-identified authorization. A new self-contained public-safe request, including a new anonymized adopter issue, uses this route regardless of origin; importing an existing external legacy candidate remains an amendment. Record additions/edits and their resulting revision/bounded diff in the authorizing record. Later edits or dropped notices follow the same kind of dated Owner planning record and preserve the earlier snapshot meaning. This is the designated ordinary idea-recording surface, separate from the accepted legacy intake above. Adding an idea here is allowed under that planning authorization even though purpose/conditions are not navigation; it does not require a DR-0003 amendment per idea. It creates neither an accepted technical contract nor execution authority. Do not use this section to copy, alter or evade accepted legacy criteria, import another external legacy candidate or change this procedure; those changes still need the named amendment. On selection the approved task owns its plan, criteria and progress; this section retains the dated idea and a task link, not a second progress ledger. Keep selection/R0 material in the Draft or planning/review note required by [Preliminary Review Location](WORKFLOW.md#preliminary-review-location).\n",
  " \n",
  " ## Task Records\n",
  " \n",
  "-None created by this proposal. Allocate a plain development record ID only when a bounded task is selected and its plan approved. Before that, use the preliminary review location defined in Contributing without allocating a task ID. The selected record references the exact intake/criteria revision and owns detailed progress, reviews, result and remaining work; this index adds only navigation under the applicable Owner authorization. DR-0001 owns its contract choices. Neither editing this sentence nor accepting a contract Draft starts a development task or creates a runtime Work/intent.\n",
  "+None created by this proposal. Allocate a plain development record ID only when a bounded task is selected and its plan approved. Before that, use [Preliminary Review Location](WORKFLOW.md#preliminary-review-location), subject to the relocation boundary above, without allocating a task ID. The selected record references the exact intake/criteria revision and owns detailed progress, reviews, result and remaining work; this index adds only navigation under the applicable Owner authorization. DR-0001 owns its contract choices. Neither editing this sentence nor accepting a contract Draft starts a development task or creates a runtime Work/intent.\n",
  " \n",
  " ## Authorized Development Records\n",
  " \n",
  "+- [CHORE-20261016-002: Contributor Document Restructure](CHORE-20261016-002-contributor-document-restructure.md) — authorized source-project rule restructuring and bounded verification/review; the earlier contributor-oriented draft remains unaccepted; amendment/result acceptance and activation remain pending.\n",
  "+\n",
  " - [CHORE-20261009-001: Colvia Entry Contract](CHORE-20261009-001-colvia-entry-contract.md) — authorization, progress and review record.\n",
  " \n",
  " - [CHORE-20261009-002: Colvia Verification Controls](CHORE-20261009-002-colvia-verification-controls.md#owner-result-acceptance-and-contract-activation--2026-10-14) — accepted development result and contract activation; Git/adopter/public actions remain separate.\n"
]
```

### Evidence, Preservation And Limits

The selected task retains the exact R0/R1/R2 records and Driver dispositions; the final R2 verdict was accept. Document round 3 checked all six result files, including the final review record: 24 procedure paragraphs, historical identities, 131 local links/anchors, GFM rendering, all 192 out-of-scope tracked files/modes, normative11 and managed29. These are executed Driver checks; the Reviewer performed static reading and did not reproduce them. Shipped-description meaning remains Driver inspection. No runtime, real adopter or actual comprehension pass is asserted.

Result acceptance and amendment activation are both now recorded. The publication-with-or-after-activation condition is satisfied for a future separately authorized publication, but commit, push, PR, merge, release and actual adopter application remain unapproved. Recheck the concurrent Development Index changes before integration; this activation does not overwrite or accept another task's work.
