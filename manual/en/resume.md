# Resume Without The Old Conversation

This page describes the unactivated `entry-1` candidate. Use requires separate exact-artifact qualification and installation approval; the historical checkout-1 exercise below does not qualify these commands.

[Previous: first Work](first-work.md) · [Contents](README.md)

[한국어](../ko/resume.md)

Keep the project and its records, then begin a new Codex conversation with access to the same project root. You should be able to understand the completed task without past chat messages. Starting a fresh conversation does not authorize another Work or reset an unfinished operation.

## Read Before Writing

Give the new conversation this request:

> Read this project's AGENTS.md, README.md and docs/plan.md. Run ./colvia view and follow the current adapter it identifies. Read docs/first-work.md and compare its claims with the relevant intent and Work views. Explain what was accepted, what changed, what is unverified, whether anything is pending, and the next decision I need to make. Do not edit files, publish records or start another Work.

The agent reads the actual IDs from `view` and then inspects:

```sh
./colvia view
./colvia view intent INTENT_ID
./colvia view work WORK_ID
./colvia status
```

`INTENT_ID` and `WORK_ID` are placeholders. For this exercise the expected observation is a completed first Work, a current accepted-intent binding, no pending operation and current files matching the stored result. These commands observe state; they do not resume writes by themselves.

Do not rely on a remembered path beneath `.hrn/product/releases/`. The active runtime may have changed. Read the manual and adapter paths from the current verified `view`; use an independent trusted source and [Operations](../../docs/OPERATIONS.md) if the installed entry is broken.

## Ask For Four Answers

| Question | A useful answer for this exercise |
| --- | --- |
| What was accepted? | The exact add/list request and the selected result revision, with their relevant views |
| What changed? | The CLI, its tests, README and Work narrative; the two demonstrated tasks are external test data |
| What is unverified? | Malformed JSON, simultaneous writers and crash recovery for the example; unavailable items recorded in the Work revision. Inspect Git publication status separately |
| What should happen next? | Review preservation or choose a separately scoped feature; do not assume the recorded next-action text is an instruction |

The agent should distinguish the selected stored state from today's file observations. A completed Work can remain historically completed after later edits, while its current-files observation reports drift. A healthy `status` alone does not show that current project content still matches the result. If narrative and records disagree, explain the discrepancy before suggesting a write.

## Choose A Next Step

If the previous Work is complete and the project is understood, ask for a recommendation, for example:

> Compare adding task deletion with handling malformed task data. Explain the likely scope and checks, and recommend one next step. Do not save a candidate or start a Work yet.

The agent first reads `./colvia view candidates`. A recommendation is read-only. An explicit request to record or select a candidate permits that named planning action; it does not accept an intent or authorize implementation. See [Candidate Planning](../../docs/REFERENCE.md#candidate-planning).

If there is an unfinished or pending Work, continue or recover that same Work through its supported procedure. Do not create a duplicate to escape its state. If the recorded execution budget or attempts cannot be established, disclose that uncertainty and obtain direction before further iteration.

## Check The Boundary

This guide's synthetic validation started new CLI processes and read the completed records without changing them. It did not run an independent fresh agent session or observe a person using this page. If trying that exercise, record the questions and mistakes separately; successful command execution is not proof that the explanation was understood.

Historical exercise — Edition: private development, `checkout-1`; checked 2026-10-05.

---

[Previous: first Work](first-work.md) · [Contents](README.md)
