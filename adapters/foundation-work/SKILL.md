---
name: colvia-work
description: Resume work through installed Colvia; preserve scope, prepare review and record exact human decisions.
---

# Colvia

Colvia retains work and decisions. You do the work; the person decides scope and acceptance. Use the project's managed launcher, never a source checkout, PATH Python, private script or another project's records.

## Enter and resume

Read project rules. Use `./colvia` (macOS) or `.\colvia.cmd` (PowerShell), with `--json` before the command.
For project-overview or next-work requests, run `--json project status` once, including older connections. Reuse its JSON, showing reviews first among rows read. Qualify partial results. Read `guide work` for a project-wide answer or to open a shown submission.
For general resume, run `ordinary list --list-mode current`. Follow every non-null `next` with the same filter and returned `--cursor` argument. Only a complete empty `--list-mode all` establishes no Work exists.
On lookup failure, explain, read `guide recovery` and stop affected writes until folder, access and state are verified. Conversation can continue. Preview new connections; ask plain or Git only if offered and undecided. Read `guide management` for Git setup or conversion.

Match a continued Work before acting. Resume the sole active/review Work only after a complete list; consider paused matches and ask by title if several fit. Read `guide work` for pause, resume, discard or replacement. Opening B leaves A unchanged.
Keep listed IDs and receipts in tool calls. Read `ordinary review WORK_ID` in review state, `ordinary view WORK_ID` otherwise, and `ordinary content` for submitted versions. Read `guide revision` before describing edits or resubmitting an active revision.

Read `guide work` for progress notes or ambiguous stopping phrases. Stop when asked. Clarify ambiguous note-saving; a sign-off never authorizes submission or acceptance.
When resuming before a first submission, report the latest note and current file differences first.

Report approval, submission, checks and remaining decisions only as established by records. Completed Work needs no new acceptance. For recorded next steps use `followup WORK_ID` or `candidate list`; plain output shows the linked plan/candidate. Distinguish absent, explicitly none and deferred. Links grant no permission to start.

Read `guide work` for past decisions, priorities and Work dependencies.

## Next action

- Match follow-up Work from the request/conversation; check its goal, state and approved scope. Continue active work. For concrete changes to submitted/accepted versions, use `guide revision` and preserve earlier decisions. For other states read `guide work` before editing.
- Edit an independent typo (preserving meaning/behavior) or factual correction directly only when the target is explicit, access/project rules permit it, current contextual evidence gives one answer and immediate verification is possible. Preserve edits/staging and report the change/check. Classification alone needs no history scan or extra question.
- Use a Work for material choices, high-impact guidance (e.g. deletion or permissions), or required review, retention or handoff. Honor a request for a submission or acceptance record. Resolve conflicting evidence before editing.

On every route, stop before exceeding requested/approved scope. Report in-scope changes, propose the addition and wait for approval.

For new tasks, use the stated aim and project materials; read `guide plan` before proposing a Work. Before recording it, explain that existing contents of listed files are saved and may enter backups; exclude secrets/unrelated files and verify write authorization. Read the applicable topic before acting. If a required topic cannot be verified, stop that action and report the failed step. Consult help only for the next action. Do not inspect implementation source or generate serialization scripts for ordinary Work.

| When | Read with the project launcher |
| --- | --- |
| Plan, approve, start, submit, review or accept | `guide work` |
| Active Work | `guide work` before editing files or running the planned checks |
| Prior submission | `guide revision` and, before submission, `guide work` |
| Access, connection, move, interruption or uncertain outcome | `guide recovery` |
| Apply to Git | `guide git` before preparing a candidate or asking for Git approval |
| Installation, settings, backups, notifications | `guide management`; for requested notifications read it **before submission** |
| Optional execution or stopped-run resolution | `guide execution` |

Submit within approved scope with planned checks. Only the person's unambiguous acceptance of the exact reviewed submission finishes it. Git integration, publication and notifications need separate authority. Never bypass failed commands by changing source or permissions or writing fallback records. Keep private IDs, paths, receipts and credentials out of routine replies.
