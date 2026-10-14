# Complete Your First Work

This page describes the unactivated `entry-1` candidate. Use requires separate exact-artifact qualification and installation approval; the historical checkout-1 exercise below does not qualify these commands.

[Previous: preparation](getting-started.md) · [Contents](README.md) · [Next: resume](resume.md)

[한국어](../ko/first-work.md)

Your prepared project now has a plan. This page turns one part of it into an accepted request, runs the agreed work, and records your decision about the result. Keep one editing Work at a time and preserve the project and external request files throughout the exercise.

## 1. Publish A Request Draft

Before the first draft is published, ask the agent to show you its declared acceptance authority and confirm that it is correct. All later drafts within that intent and its Work retain the same authority. This is a role declaration, not an authenticated identity. If a published draft has the wrong authority, do not accept it or edit the record; ask the agent to check the supported correction procedure.

Ask Codex:

> Use docs/plan.md and docs/first-work.md to prepare an intent draft for todo-lab's add/list feature. Carry the agreed CLI contract, four behavior criteria and material verification conditions into the typed request. Show me the goal, exact file scope, expected result, acceptance checks, result destination, exclusions and unresolved questions. Explain what I am being asked to accept. Before publishing, show me the acceptance authority you will declare and wait for my confirmation. After I confirm, publish the draft. Do not accept the draft or start implementation yet.

The agent uses the installed `colvia intent draft` interface and shows the draft with `./colvia view intent INTENT_ID`, substituting its actual ID. You should see an unaccepted draft. A published proposal is not your acceptance.

Check all six parts:

| Part | This exercise |
| --- | --- |
| Goal | Keep a small local task list |
| Scope | `todo.py`, `tests/test_todo.py`, `README.md`, `docs/first-work.md` |
| Expected outcome | `python3 todo.py --file PATH add TEXT` prints `Added: TEXT`; `python3 todo.py --file PATH list` prints tasks in insertion order as `1. TEXT`, `2. TEXT`, one per line |
| Acceptance checks | Empty list: no output or file creation; ordered add/list; empty or whitespace-only task: exit 2 without writing; listing: data unchanged. Use the agreed verification conditions |
| Destination | The current project; disposable test data stays outside the project or in already-ignored scratch |
| Forbidden scope | Edit/delete, new dependencies, network, deployment, Git commit and push |

For this exercise, put the material scope and checks in the typed request. The plan and editable Work narrative are explanatory documents, not required digest-bound inputs. If you choose to make another document required, review the resulting edit/reacceptance cost before accepting.

Resolve material unknowns before acceptance. The agent can publish a new draft; it must not edit an immutable published draft. The project plan and Markdown Work narrative help you understand the proposal; the accepted typed request identifies the exact authorized revision.

## 2. Accept The Exact Request

Ask the agent to prepare acceptance and show its confirmation in readable form. The agent saves only the returned `ticket` outside the project and runs:

```sh
./colvia view confirmation --input /absolute/path/todo-lab-inputs/intent-ticket.json
```

The path is illustrative; use the actual saved ticket. Confirm the project, intent revision, acceptance authority, scope, exclusions and any required document references. Do not copy this guide's IDs, hashes or tokens into a real decision.

Before accepting, confirm that the draft carries the agreed CLI contract, behavior criteria and material verification conditions from `docs/first-work.md`. Resolve gaps before preparing the exact acceptance ticket again. The agent must carry consumed limits forward when resuming, and must not retry a failed authority apply automatically.

When correct, tell the agent:

> I accept the intent revision shown in this confirmation for the add/list feature. Apply this exact intent ticket. Then start and implement the Work within the four-file scope and run the agreed checks. Stop if scope or required inputs change, verification fails without an in-scope correction, or an authority operation fails. Do not commit or push.

Only after that decision does the agent use `colvia intent apply` with the exact ticket/token. It verifies the selected accepted request, then publishes the Work's starting baseline. The [machine input contracts](../../docs/GENERAL-WORK.md#installed-machine-commands-development) are for the agent; you review the proposal and confirmation rather than composing JSON.

## 3. Implement And Check The Result

The agent implements the feature in the project and runs the fixed checks. It can make authorized corrections within the accepted scope. A wider feature, changed acceptance criterion or changed ignore policy needs a separate decision. Colvia does not run an autonomous iteration loop or stop unrelated editors from changing files.

For this example, from the project root:

```sh
python3 -B -m unittest discover -s tests -v
```

Expected: all four behavior criteria above pass. The synthetic exercise used four test functions; your test count may differ. This is the example application's verification, not the Colvia regression suite.

Ask the agent to demonstrate the CLI using a fresh data file in the external practice-input directory. Its parent directory must already exist. Replace the illustrative path before running:

```sh
python3 todo.py --file /absolute/path/todo-lab-inputs/tasks.json add "Read manual"
python3 todo.py --file /absolute/path/todo-lab-inputs/tasks.json add "Review result"
python3 todo.py --file /absolute/path/todo-lab-inputs/tasks.json list
```

The two add commands print `Added: Read manual` and `Added: Review result`. The final command prints:

```text
1. Read manual
2. Review result
```

These operations write only the chosen data file. The exercise does not test malformed JSON, simultaneous writers or crash recovery for this example application.

Before submission, the agent updates the in-scope README and Work narrative with the implementation, tests, limits and proposed next step. It then publishes the full result manifest and a revision for review. Once submitted, keep project content unchanged while reviewing. Editing even an explanatory file can invalidate the exact result; ask for the supported rework path when a correction is needed. [Check Before Writing](../../docs/REFERENCE.md#check-before-writing) explains the wider content boundary.

## 4. Review And Accept The Result

Ask Codex:

> Explain what changed in this Work, show the relevant code and test results, compare them with the accepted request, and identify anything untested. Show the selected Work revision and its exact result confirmation together. Explain every recorded unavailable item against my acceptance criteria. Wait for my decision.

The agent saves only the returned Work `ticket` outside the project and shows these views for the same selected revision: the submitted revision currently under review, not yet accepted.

```sh
./colvia view work WORK_ID --revision REVISION_ID
./colvia view confirmation --input /absolute/path/todo-lab-inputs/work-ticket.json
```

Use the actual IDs and saved ticket path. The Work view contains the author-declared `observed_scope` and `unavailable_scope`; the confirmation view does not repeat them. The agent explains every unavailable item against your acceptance criteria. You decide whether it is outside scope, needs more evidence or needs a new scope/request acceptance. An empty unavailable list does not prove that the criteria passed. If the revision or selection changes, prepare both views and the ticket again before deciding.

Check the actual files too: the manifest displays metadata and does not reconstruct historical file contents. A passing test or a review recommendation does not accept the result.

If it meets the agreed checks, tell the agent:

> I accept the result revision shown in this confirmation. Apply this exact Work acceptance ticket and verify the resulting state and current files. Do not create a Git commit or push.

The agent applies the ticket, then checks the Work view and status. For this local Work, the implementation is already in the control checkout; acceptance records the decision and selects the accepted result. It does not copy a worker's files or rerun implementation.

Expected result:

- The Work's stored state is `completed`, with no pending operation.
- The accepted request binding is current.
- The current-files observation says `matches stored result`.
- Git publication remains a separate decision.

An older revision field may still say `progress: review` or “Owner result review.” That field records what the agent wrote at submission time. The selected acceptance determines the stored completed state. Do not edit records or project files just to make an older description say “complete.”

If apply fails or content no longer matches, preserve the request and files, stop and ask the agent to explain the exact state and supported recovery. Do not fabricate a new approval or delete records to make the screen look complete.

## 5. Decide How To Preserve The Work

Colvia records completion under `.hrn/`; it does not commit or push. Ask the agent to show the Git diff and status, the intended preservation set and any important ignored outputs. Installation files, authority records, source and project documents must be accounted for under the project's policy.

Approve commit and remote publication separately if wanted. This tutorial stops before either operation. Keep the durable project and exact source/request files available, then move to [a new session](resume.md).

Follow [Records And Retention](../../docs/REFERENCE.md#records-and-retention): reuse one suitable narrative for checks, material limits, review and decisions, and retain extra raw output or copies only for a named investigation, recovery, reuse or delivery. This local exercise creates no worker checkout; for worker projects, the agent separately verifies cleanup authority and preservation, then retires an eligible unused checkout or reports its remaining use and release condition.

Historical exercise — Edition: private development, `checkout-1`; checked 2026-10-05.

---

[Previous: preparation](getting-started.md) · [Contents](README.md) · [Next: resume](resume.md)
