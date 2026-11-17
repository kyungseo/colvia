# The Records And Decisions You Need

[User guide](README.md)

For the current workflow, start with [what a Work remembers](understand.md) and [what to ask your agent](work-guide.md). The detailed record examples below describe the earlier entry-1 profile.

For the first project, keep three things distinct: the plan for the project, the exact request you accept, and the Work that carries it out. You can read explanations in Markdown while Colvia keeps the records that identify the accepted revisions.

## Plan, Intent And Work

| Term | Meaning | Task-list example |
| --- | --- | --- |
| Project plan | Project-owned narrative about goals, order and future work | Add/list first; consider deletion later |
| Intent draft | A proposed request with goal, scope, outcome, checks, destination and exclusions | The add/list proposal before acceptance |
| Accepted intent | The exact request revision selected by human acceptance | Permission for the specified four-file scope |
| Work | The unit that carries out an accepted request, including planning, progress, review and result records | Starting baseline, implementation, submitted result and decision |
| Candidate | A recorded possibility or planning choice | “Consider malformed-data handling next” |

A candidate selection does not accept an intent. An accepted intent does not accept its future result. The Work's completed state is derived from a selected accepted result.

## Who Owns What

The project has one place for the records used to determine its state, acceptance and history. This *authority home* is `.hrn/`. Project Markdown explains purpose, plans and results; it does not replace the typed acceptance records.

```text
Human owner ── decides scope and acceptance
       │
       v
Agent ── prepares proposals, implements authorized work, explains results
       │ uses verified commands
       v
.hrn/ ── project-owned intent, Work and history records
       │ read only
       v
View ── current observations for the human and agent

Project README / plan / Work narrative ── readable explanations
```

The diagram separates responsibilities; it is not an automatic orchestration system. Actor names in records declare roles within a trusted local account and are not authenticated identities. See the [source concept contract](../../../docs/CONCEPTS.md).

`View` is a read-only rendering of verified records and current observations. It neither changes state nor decides acceptance. Its output is diagnostic Markdown, primarily English with some localized content; the agent should explain it in your language. You should not need to decode internal fields to make an informed decision.

## Two Decisions Around One Work

```text
Request draft → review exact request → human accepts request
                                      ↓
                          baseline → implementation → submitted result
                                                           ↓
                                        review exact result → human accepts result
                                                           ↓
                                        selected accepted result → completed
```

The diagram shows the tutorial's successful local path. If inputs change, validation fails or an operation is interrupted, stop at that point and use the appropriate correction or recovery procedure. A review verdict, successful test or confirmation token cannot substitute for the human's decision.

For a local Work, application records the decision around files already present in the control checkout. A linked worker's result has a separate application procedure; this tutorial does not exercise it. Git commit and push are outside both acceptance steps.

## Terms You Will See

| Term | What it lets you understand |
| --- | --- |
| Revision | One exact published version of a request or Work record |
| Baseline | The project-content observation against which the Work result is compared |
| Manifest | Exact before/after content metadata and changes; not a backup of the file bytes |
| Ticket | Prepared confirmation input binding the exact action, object and prerequisites |
| Confirmation token | A value binding that ticket/request; not evidence of human consent |
| Decision | A recorded human action, such as accepting or rejecting a result |
| Selection | The exact revision/decision chosen by the verified current reference; do not infer it from the newest filename |
| Receipt | A lifecycle record used to verify installation, switching or removal |
| Control checkout | The primary project location that can write its authority records |
| Worker | A separate linked checkout used for bounded execution/submission; it cannot write control authority |
| Rebind | A supported, human-authorized change of the Work's bound baseline or intent; not a way to bypass ignore-policy checks. Local Work rebind requires a newly accepted intent; same-intent rebind is unsupported for local Work |

“Authority” can refer either to the source of truth (`.hrn/`) or to the person entitled to accept a request/result. A directory holds records; it does not grant the agent permission.

## When To Stop

| Observation | Next action |
| --- | --- |
| No installation, wrong runtime or refused topology | Check the source, interpreter and fresh primary target before installation; use [Getting Started](../../../docs/GETTING-STARTED.md) |
| Draft has a material unresolved gap | Resolve it, publish a new draft and review that revision before acceptance |
| Submitted result or required document changed | Preserve the change, explain the mismatch, and use the supported rework/new acceptance or rebind procedure; do not silently refresh the baseline |
| Intent, Work or lifecycle operation is pending | Preserve original inputs and exact source; use [Operations](../../../docs/OPERATIONS.md) before unrelated writes |
| `status` is healthy but current files differ | Inspect the Work view and actual files; historical completion and current content are separate |
| Launcher or managed files are damaged | Preserve the state and use the independent-source diagnostic/repair path in [Operations](../../../docs/OPERATIONS.md) |
| A record is unreadable, unknown or torn | Preserve it and seek diagnosis; do not hand-edit selectors or delete records to clear the error |

The [Reference](../../../docs/REFERENCE.md) explains exact error codes and the [Manual Operation](../../../docs/MANUAL-OPERATION.md) guide covers reading retained evidence without the installed product. Do not turn an unavailable observation into a successful result.

## Keep The First Work Stable

Colvia compares whole project content, not only the changed-file list. Prepare ignore rules and out-of-scope setup before the baseline; include the intended Work narrative edits in scope. Keep test data out of the result tree and finish result explanations before submission. A required document reference binds exact bytes: changing it can require a newly accepted intent and rebind, so choose required inputs deliberately.

These boundaries keep “what I approved” meaningful when an agent continues later. They do not provide an execution sandbox or prevent another process from editing the project.

Earlier exercise details are in the [operations reference](reference.md#earlier-checkout-exercise).

---

[Back to the user guide](README.md)
