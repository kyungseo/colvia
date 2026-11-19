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

Read the project rules. Run `./colvia --json ordinary list --list-mode current` on macOS or
`.\colvia.cmd --json ordinary list --list-mode current` in Windows PowerShell. Use that launcher throughout.
Follow each non-null `next` with the same filter and `--cursor` plus its returned JSON argument.
An empty current list can hide archived or discarded Work. Only a complete empty `--list-mode all` establishes that this connection has no Work.
If a lookup fails, explain what is known, read `guide recovery`, and stop affected
writes until you can verify the folder, access and Work state. For a folder that
needs connection, use the manager’s connection preview first. You can still help in conversation.

Check for a matching Work first. For a general request to continue, resume the
only active or review Work when the full list establishes there is exactly one.
Consider paused matches too. If several fit, show their titles and ask which to open.
For pause, resume, discard or replacement read `guide work`. Opening B leaves A as it was. Use the ID from the
list in tool calls; the person need not supply it. Read `ordinary review WORK_ID`
for review state, otherwise `ordinary view WORK_ID`. Keep `--json` before the
command group for structured records. When needed read `ordinary content` for
the submitted version and compare it with current files. Keep IDs and approval receipts in tool calls. For an active revision
read `guide revision` before describing edits or submitting again.

For a progress note or an ambiguous stopping phrase, read `guide work`. Stop work when asked to stop. Ask before saving an ambiguous note; a sign-off never authorizes submission or acceptance.
On first-submission resume, report the latest note and current file differences before taking the next approved step.

Say what was approved, what was submitted or checked, and which decision remains,
to the extent the records establish it. A completed Work needs no new acceptance.
For a recorded next step use `followup WORK_ID` or `candidate list`; plain output
shows the linked plan or candidate. Distinguish absent, explicitly none and
deferred. A recorded link gives no permission to start its target.

## Choose the next action

An explicitly requested typo, spacing or punctuation correction may proceed
without a new Work if it preserves meaning and behavior, fits project rules and
granted access, and needs no separate review, retained result or handoff. Use a
matching Work's valid scope and revision procedure when one exists.

For changes that need review, a retained result or handoff, use a Work.
For a new task, use the stated aim and existing project materials. Read
`guide plan` before proposing a Work. Before recording a plan, explain that
listed files' existing contents are saved and may enter backups, exclude secrets
and unrelated files, and verify authorization for that write. Read the applicable
topic before acting; if a required topic cannot be verified, stop that action
and report the failed step. For example, run `./colvia guide work` on macOS or
`.\colvia.cmd guide work` in PowerShell. Use command help only for the next needed action.
Do not inspect implementation source or generate serialization scripts for ordinary Work.

| When | Read with the project launcher |
| --- | --- |
| Plan, approve, start, submit, review or accept | `guide work` |
| Resume an active Work | `guide work` before editing files or running the planned checks |
| Inspect or revise a previous submission | `guide revision` and, before submission, `guide work` |
| Access, connection, move, interruption or uncertain outcome | `guide recovery` |
| Prepare or apply to Git | `guide git` before preparing a candidate or asking for Git approval |
| Manage installation, settings, backup or notifications | `guide management`; for requested notifications read it **before submission** |
| Inspect optional execution or resolve a stopped run | `guide execution` |

Work within the approved scope. Submit the result with the planned checks. Only
the person's unambiguous acceptance of the exact reviewed submission finishes
that decision. Git integration, publication and notification have separate authority.
Do not modify source, change permissions, or write fallback records to work around
a failed command. Do not expose private IDs, paths, receipts or credential values
in routine replies.
