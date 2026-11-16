---
name: colvia-work
description: Continue project work through the installed Colvia entry, preserve agreed scope, prepare the result for review, and record the person's exact decision.
---

# Working with Colvia

Colvia retains project work and human decisions. You perform the requested work;
the person decides what to entrust and which result to accept. Use the project's
managed launcher. Do not substitute a source checkout, PATH Python, private script
or another project's record directory.

## Enter and resume

Read the project rules and use the connected project’s launcher: `./colvia` in a
macOS shell or `colvia.cmd` at the Windows project root (`.\colvia.cmd` in
PowerShell). Read its `guide` on first
entry. Run `./colvia --json ordinary list` on macOS or
`.\colvia.cmd --json ordinary list` in Windows PowerShell to establish the
Work context. In examples below, use the same platform launcher. A successful empty list with no next page means the connected
project has no Work. Follow [Access failures](#access-failures) when a lookup is
unavailable or the folder needs a connection preview. Give whatever help you
can in conversation. Establish the connection and relevant Work state before
creating or changing Work records.

Check the request against existing Work first. Resume a clear match within its
recorded scope and approval while its prerequisites still hold. Present a
pending decision if there is one. For a general request to continue, pick up the
only active or review Work if the list establishes there is exactly one. When
the target is unclear, show the relevant titles and ask which one to continue.

For a new request, an explicitly requested typo, spacing, or punctuation
correction can proceed without a new Work if it preserves meaning and behavior,
fits the requested change, project rules and granted access, and needs no
separate review, retained result, or handoff. Check for a matching Work first.
For a correction in an existing Work, follow that Work’s recorded approval,
state and revision procedure. Edit only after confirming the applicable rules,
access and Work context. If any cannot be confirmed, follow [Access failures](#access-failures).
For other changes, use [Ordinary work](#ordinary-work).

For a new request that needs a Work, use what the person has already said and what you can verify
in the folder. Read relevant rules, README files, briefs or plans. Say what
those documents describe and which files you actually found. If code, data or
configuration needed for the work is missing, name it and keep the affected
part of the proposal provisional. Distinguish project material from the launcher,
connection files, repository metadata and OS files. Read project and repository
instructions even if there are no working files yet. If all you find is a set of project rules, acknowledge it and use it.

- **A broad request in a project with no material yet.** Tell the person what
  you found. Give one or two examples that show what they could say, such as a
  one-page proposal for a customer meeting or the first version of a personal
  budget app. Invite them to describe their aim in a sentence or two. Use that
  aim to fill in a short project outline and propose a first task with a way to
  tell when it is done.
- **A broad request with existing material.** Build on the relevant purpose,
  decisions and current state. Suggest a first or next task that follows from
  them. Ask only about a gap that would change the proposal.
- **A concrete new request.** Lead with a filled-in work proposal. Show the
  intended output or a small sketch and how you would check it. If a project
  outline or shared rules would help future work, offer to discuss them in one
  optional line at the end. The person can review the work proposal without
  answering that offer. If they defer it, let it rest in this conversation.

Tailor the proposal to the request:

- For a document, use the intended readers and the decision it should support.
  Suggest a specific outline, the source material and the checks that make the
  result useful. Preserve originals and distinguish source facts from proposals.
- For software, start with who uses it, their first useful action and what
  belongs in the first version. Recommend a stack and a simple structure when
  useful, with a reason tied to the project's needs. Follow the project's working
  rules and reuse the stack and commands you can verify in the repository. For a new project, propose one usable flow, a run method,
  and checks that use that same method. When using Git, treat result acceptance
  and commit as separate decisions.
- For research, operations or mixed work, identify the decision or routine the
  person wants to improve. Suggest the inputs, first deliverable and how to
  review it. Add a recurring schedule or working rules when they serve the goal.

Fill in low-impact defaults such as an output format or file name when useful.
State assumptions that matter. For example, a personal task list for one
browser can start with HTML, CSS and JavaScript, separating the screen, task
logic and browser storage. A shared list needs a storage and access proposal
that fits its users. Use conditions the person already stated. Present choices
about access, deployment, cost or data handling as proposals for the person to
confirm. If a missing answer would change the work scope, keep the proposal in
conversation and ask before requesting approval. In a simple first reply, ask
only one question that requires an answer. Group related questions when they
need a joint decision. When the scope is clear, show it and ask for approval in
the same reply if needed. Use existing exact authorization when it applies.
`ordinary plan` writes a plan record, so run it only with authorization for that
write and follow [Ordinary work](#ordinary-work).

When outlining a project, draft its purpose, first result and a few reusable
working rules based on the person's aim. For a recurring report, suggest how to
keep source data and check the numbers. For software, suggest how to keep the
first version small and what to run before each result is reviewed. Offer to
save the outline in an existing document, or suggest one short project document
when needed. Show the intended changes. Include them in the proposed scope or
use the existing scope-change procedure for an already approved Work. Discuss drafts and recommended defaults
in conversation, and follow [Ordinary work](#ordinary-work) for recording and
approval. File creation, dependency installation, Git setup and execution checks
belong to the applicable approved scope.

For existing Work:

1. Use the machine Work ID from `list`. Human display text is not a command ID.
   If two Works fit the request, show their titles and ask which one.
   Do not ask the person to paste internal IDs.
2. Select by the state returned by `list`: use `ordinary review` only when it
   says `review`. Use `ordinary view` for active or completed work. A completed
   work needs no new acceptance question. Read preserved historical text with
   `ordinary content` when needed; keep it distinct from current files.
3. For internal IDs or approval receipts, put `--json` before the command group:
   `./colvia --json ordinary review WORK_ID`. Keep these fields in tool calls;
   do not paste them in the human response. Use the ID from `list`, not a guessed
   slug or the visible title. A normal resume needs list, the selected view/review,
   and the relevant content. When the request is about the next decision, use
   `followup WORK_ID` to read the selected Work’s saved choice, or `candidate list`
   for saved candidates. Distinguish no record, explicitly none, and deferred.
   Use these commands without `--json` when explaining whether a choice or
   link refers to an earlier plan or candidate. The structured follow-up read
   gives the saved choice and target ID without the current display details. A saved
   relationship carries no permission to start the target Work.
4. Read `./colvia <group> --help` only for the next needed action. Do not inspect
   implementation source or generate serialization scripts to perform ordinary
   planning, submission or acceptance.

## Access failures

Use the actual command result, not an assumed permission setting:

| Observation | Meaning and next step |
| --- | --- |
| No narrow-access request tool in this session | No request was made. Do not report an OS denial or invent a settings control. |
| Host explicitly reports the command was not started | Report that start refusal. This observation establishes no current record state. |
| A started command times out, is interrupted or returns missing/damaged output | Its outcome is unknown. Inspect the Work or known operation read-only before considering another mutation; missing JSON alone is not a host denial. |
| The person declines a tool request | Stop that action. Do not seek a bypass. |
| Colvia reports a file or storage access failure | It may concern an input, output, runtime or record store. Identify only what the actual diagnostic establishes. |
| `ordinary list` exits 0 with `items: []` and `next: null` | This verified connection has no Work. A failed query never establishes that. |

`workspace-registration-required` needs the manager's connection preview; it is
not an empty Work list. A non-null `next` means there are more pages. A new folder
without a verified connection must use that preview before any record writes.
For `connection-move-review-required`, use the installed manager's
`move-preview` with the existing project ID and new absolute root. Review the
verified old and new locations. Use the exact canonical preview and receipt
only after the person approves the move. Inspect `move-status` before resuming
an interrupted operation with the same ID. Keep the connection file and
record store intact. A copy, overlap or unverified identity requires diagnosis.

Use the host's actual denial details and verified connection information to locate
the required path and read/write/execute access. Colvia's generic error does not
identify the denied path. If the path or cause is unavailable, say so instead of
assuming the record directory. Explain the smallest known action briefly; show an
exact private path only when the person needs it to authorize or perform that action.

Only use a narrow-access mechanism actually available in the current host and
covered by authorization. Verify the returned path, access mode and duration;
a partial grant is not the full requested grant. Do not add network access or
assume a turn grant survives the turn or a new conversation. Do not enable trial
features, change host settings, install tools, switch to full access, or substitute
a source launcher to work around missing access. If no supported narrow path is
available, stop the affected writes and name the missing capability.

A grant alone does not authorize retrying a stopped command. Before reconsidering
a mutation, inspect its current Work, or its operation if the ID is known, using the
applicable read-only command; some changes may already have happened. Keep unknown effects unknown and
follow existing recovery and retry authorization. Do not create an untracked
fallback result or claim that chat text was recorded or submitted. Successful
reads alone do not establish write access. Another host's successful run does not
establish this host's permissions.

## Ordinary work

- Before `ordinary plan`, agree on the goal, exact files, checks and exclusions.
  Recording the plan saves the existing contents of its listed files, even
  before the user approves the plan. Submitting keeps the result contents.
  Both can enter backups, and the Preview has no selective content deletion.
  Exclude secrets and unrelated files before the capture. Reuse existing
  authorization for this exact action when it covers those facts. Ask once
  when a decision is needed.
- Keep the receipt and machine identifiers in tool calls. Explain the practical
  reason for any new decision. Follow a host-required disclosure when applicable,
  but do not repeat internal rules and paths in routine status or completion text.
- After approval, record it and start the work. Edit within scope and perform the
  checks that establish the requested result. Preserve source materials and leave
  business choices such as prioritization to the person unless explicitly delegated.
  If a new file is needed outside the approved Work, preserve its existing edits and
  checks. Show the additional files, why they are needed and any check changes.
  Record an approved separate Work for that scope before editing those files.
- In reports, distinguish source-supported facts, interpretations and proposed
  actions. Counts or categories in supplied data alone do not establish gaps in
  the project's existing documents (such as customer guides or help documents),
  implementation effort, or measured effects.
  Keep useful proposals conditional on the evidence needed to assess them; do not
  turn missing evidence into a claim or bury the findings in repeated caveats.
- Submit the reviewable result automatically when the approved work is ready.
  A separate request to submit is unnecessary. Unavailable checks stay unavailable;
  they must not be reported as passed. Report each planned check exactly once by
  its planned name, with its truthful passed, failed or unavailable status. Put
  additional checks and their results in the summary, stating any failure or
  finding that affects the result. If an unplanned check changes the
  agreed scope or acceptance conditions, propose a revised plan through the
  existing approval path instead of silently adding it to the submission.
- After an explicit `check-report-mismatch` refusal during submission, compare
  the report with `ordinary view` and correct the reported checks. Use the
  stored `checks` names (or `rework.checks` for an active revision); `plan-review`
  is only for a plan awaiting approval. Send
  the correction as a new command, letting the CLI choose a new operation ID;
  do not reuse the refused operation ID or remove its preparation records.
  This applies only to a confirmed refusal. For an unknown outcome, inspect the
  existing operation before deciding any recovery; do not start another attempt.
- Show the result link, relevant changes and the decision needed. Ask whether to
  finish with this result or revise it. After an unambiguous answer to the exact
  reviewed result, record acceptance once and finish briefly. Do not ask again
  merely because an internal receipt was prepared.
- On successful acceptance, one sentence is normally enough: identify the file
  and say it is finished with the reviewed result. Do not repeat the review,
  hashes, limits already disclosed, or a list of actions not taken. Add another
  sentence only for an unresolved issue that changes the person's next action.
- A stale result, ambiguous target, changed scope or unresolved external effect
  requires the specific missing decision or recovery step. Do not reuse an old
  receipt to accept changed bytes, silently broaden scope or rerun an unknown effect.

## Revising an already submitted result

Use `ordinary revise` once after the person requests a concrete modification to
the reviewed result. That records the request and keeps the original approved
file scope, checks and previous submitted content. A new conversation reads
`ordinary view`: `rework.approved_request`, `approved_scope`, `checks`, scoped
`differences`, and `submission_check`. Do not re-approve a recorded request or
call `plan-review` for an active Work. Ask only about a genuinely changed scope,
ambiguous result or unresolved effect; final acceptance remains a separate decision.

While the Work is active, its last submitted body is retained history, not a
currently pending review. This read does not establish whether checks were run
in another conversation; say that current check evidence needs confirmation,
not that nobody has run them. An unattributed addition means the submitted proof
was not established, not that the file has no possible owner.

The scope diagnosis is a current read, not a replay of an old failure or proof
that all checks passed. When the person asks what changed or where a revision
stands, do not stop at `rework.differences`: it lists changed paths, not text edits.
Read the relevant file in the approved scope in the workspace and its preserved last submitted
body with `ordinary content WORK_ID PATH --revision LAST_SUBMITTED_REVISION`,
using `rework.last_submitted_revision` from that view. Compare the two before describing
the current edit, even when outside-scope changes block submission. For large text,
compare the relevant sections and state the comparison limit. If either body is
unavailable or not readable as text, name that limitation and the observed reason;
do not infer a missing edit or ask for the same scope approval again. Show the
concrete content change briefly, separately from the file-specific submission
blockers and any remaining human decision. This comparison does not prove checks
passed or authorize editing, restoring, submitting or accepting during a read-only
status request.

For an already authorized modification task, execute the remaining planned checks
and submit the modification without a separate submission request.

If the diagnosis is unavailable, do not
invent the cause. If blocked, name the causal files and additions/modifications/
deletions, retain the modified draft and last submission, and explain the next
needed action briefly. Never reset a baseline, ignore outside changes, remove
another Work's files, or ask the person to edit internal record IDs.

A rework may account for regular files added by another approved and submitted
Work in the same workspace when its immutable submission and current content
agree. This does not accept or edit the other Work, and cannot cover unsubmitted
files, overlapping scope, policy changes, or existing outside modifications or
deletions. Such a submission requires all planned checks to have passed. Do not
claim attribution proves who authored the bytes. First submissions and general
external-change recovery are outside this exception. An attributed revision can
be reviewed, accepted, backed up and selected for scope-only Git integration;
applying it to another workspace through worker is not yet supported. Do not
bypass that refusal with a private file-copy script.

## Additional capabilities

Use the installed command's own help for candidates/follow-ups, composition,
worker application, delivery, optional execution, backup and separate Git
integration. Capability presence is not evidence that a host or OS path has been
qualified. Direct agent execution is disabled in the first Colvia Preview; enabling it is
refused. Ordinary work in an agent’s own CLI or desktop app is separate.
Retained execution settings and history remain
readable, and disabling the setting remains possible. Preparing or inspecting an action does not execute it.

A Work acceptance records the person's decision about the exact result. It does
not commit, merge, publish, deploy, send a notification or accept another Work.
An explicit request can authorize notification as part of the same scope; do not
add a duplicate confirmation when the concrete receiver and action are already
covered. Use the managed Colvia receiver only, never a terminal notification as
substitute evidence. A displayed event is not a successful click or result acceptance.

Use bounded result summaries by default. Put hashes, receipts, raw checks and
recovery internals in machine output or requested technical details. Keep failure
records, and do not remove history or evidence simply because a task completed.

## Managed setup and notifications

Use `./colvia manage --help` for the manager bound to this same installation;
`./colvia --json manage status` does not open a Work or change settings. Never
supply a different management root to bypass a refusal. On Windows use the
project's `colvia.cmd` launcher with the same arguments. Installation, OS consent
and subscription login are separate from approving a Work.

For an explicitly requested result notification, first inspect
`./colvia --json manage notice-check`. If registration is needed, use the same
manager's `notice-enable` only within authorization; OS consent may require the
person. Use the returned receiver identity in `delivery prepare --step submit`
with the exact Work, prepared summary and check results. Record the already-given
scope approval with `delivery start`, then `delivery run`. This replaces the
ordinary submit for that result; do not submit twice. After the delivery finishes,
`delivery notify DELIVERY_ID` resolves this project's record location and calls
the managed receiver once. An unknown emission is not permission to repeat it.
Use `delivery view` or `delivery details` to find the retained result. Neither
notification nor clicking it accepts the Work. No desktop or OS qualification
may be inferred from these commands being present.

For a stopped update, use `manage --json update-status OPERATION_ID` to inspect
the prepared release and receipt before an explicitly authorized resume. A
missing preparation or expired verification needs diagnosis, not a new download
loop. Preserve interrupted Git integration locks; do not remove `index.lock` or
make another commit while recovery is pending.


When asked whether optional document execution is available, use the managed
launcher's `execution readiness`. It opens no project store and launches no
model. Exit 0 means the inspection completed, not that execution is enabled.
Both `absent` and `prepared-dispatch-unavailable` have `dispatch_available:false`.
Keep ordinary Work and review available; do not enable execution from asset or
feature-token presence. Corruption is an error, not an invitation to alter Python,
permissions, runtime files, or retry the execution.


## Optional document execution

`execution prepare` and `execution start` use the installed composition only.
This candidate has no qualified runtime combination and refuses before opening
project records for those actions. Do not supply custom ports, change the runtime
configuration, use a source command or relax permissions to bypass that refusal.
Use ordinary Work when the requested result can be prepared in the current chat.
`execution view` remains readonly; `execution cancel` records a separate request
without taking the running worker's effect lock. A lost start response is not
permission to repeat it. Inspect the run. An active execute delivery with no child,
or with a closed matching child, can finish through `delivery finish-execution`;
this never launches a process or accepts a Work. Never finish an unclosed child.
For an unresolved run, use `execution resolve-preview` to show the existing exact
observation and obtain human approval before `execution resolve --receipt ...
--statement ...`. This records an operator resolution only: it neither restarts
execution, restores bytes nor accepts the Work. Missing process identity, changed
observations or unconfirmed absence retain the barrier. The resolution path uses
the existing qualified macOS observer; it is not a user-supplied assertion.

A qualified runtime is only availability. Project feature opt-in and approval of
each exact grant are also required. Preserved feature settings alone do not
approve a run; a changed runtime binding changes the grant capability. Never
populate qualification keys or edit runtime configuration as an agent workaround.
