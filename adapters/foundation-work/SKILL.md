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

Read project rules. Use `./colvia` (macOS) or `.\colvia.cmd` (PowerShell), with `--json` before the command.
For “오늘 뭐부터 보면 돼?” or “다음 진행할 작업은?”, run `--json project status` once, even in older connections. Reuse its JSON for the overview. Show reviews first among the rows read. Qualify partial results. For a project-wide answer or a request to open a shown submission, read `guide work`.
For general resume, run `ordinary list --list-mode current`. Follow every non-null `next` with the same filter and returned `--cursor` argument. Only a complete empty `--list-mode all` establishes no Work exists.
If lookup fails, explain, read `guide recovery` and stop affected writes until folder, access and state are verified. Preview new connections. Ask plain or Git only if offered and undecided. For Git setup or conversion read `guide management`. You can still help in conversation.

For a request to continue a Work, match it before acting. Resume the only active or review Work when the full list establishes it. Consider paused matches; if several fit, ask by title. For pause, resume, discard or replacement read `guide work`. Opening B leaves A as it was.
Use the listed ID internally. Read `ordinary review WORK_ID` for review state or `ordinary view WORK_ID` otherwise. Use `ordinary content` for a submitted version. Keep IDs and approval receipts in tool calls. For an active revision read `guide revision` before describing edits or submitting again.

For a progress note or an ambiguous stopping phrase, read `guide work`. Stop work when asked to stop. Ask before saving an ambiguous note; a sign-off never authorizes submission or acceptance.
On first-submission resume, report the latest note and current file differences before taking the next approved step.

Say what was approved, what was submitted or checked, and which decision remains,
to the extent the records establish it. A completed Work needs no new acceptance.
For a recorded next step use `followup WORK_ID` or `candidate list`; plain output
shows the linked plan or candidate. Distinguish absent, explicitly none and
deferred. A recorded link gives no permission to start its target.

For decisions made earlier, candidate priorities or Work dependencies, read `guide work`.

## Choose the next action

- For a follow-up, identify the Work from the request or conversation. Check its goal, state and approved scope. Continue active work; use `guide revision` for a concrete change to a submitted or accepted version. Preserve earlier decisions. For other states use `guide work` before editing.
- For an independent correction (a typo that preserves meaning and behavior, or a factual update), edit directly if the target is explicit, access and project rules permit it, current evidence gives one answer in context (e.g. command help), and you can verify it immediately. Preserve existing edits and staging; report the change and check. No history scan or extra question is needed solely to classify it.
- Use a Work for material choices, high-impact guidance (e.g. deletion or permissions), or required review, retention or handoff. Honor a request for a submission or acceptance record. Resolve conflicting evidence before editing.

On any route, if the edit needs more scope, stop before editing outside the request or approval. Report what changed within scope and propose the addition; wait for approval.

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
