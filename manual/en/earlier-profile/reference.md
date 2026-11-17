# Operations reference

[User guide](README.md)

Use these notes when you need exact commands or recovery procedures.

[Project rules, updates and disconnection](rules-and-removal.md) · [Records and terminology](concepts.md) · [Operations](../../../docs/OPERATIONS.md)

<a id="notifications" name="notifications"></a>

## Turn on device notifications

Ask your agent to enable notifications on this device. On macOS, use the verified manager’s `notice-enable` command and allow notifications when prompted. On Windows, use `notice-enable` with the matching manager. After a Windows manager update, run it again with the new executable. You can always open the project inbox. [Platform commands and click support](../../../docs/REFERENCE.md#single-work-handoff-and-inbox)

<a id="resume-details" name="resume-details"></a>

## Technical details on resuming and recovery

### Recover The Current Situation

Expect a concise explanation of the accepted result, unfinished scope, current file agreement or drift, consumed time/attempts and valid remaining authority. A completed Work remains a historical acceptance even if files later change. Resolve differences between narrative and records before proposing a write.

If the previously approved task still has work remaining and its conditions hold, the agent continues it. If you asked only for a status check or recommendation, it stays read-only. A pending or unknown operation uses its recovery path; a new chat does not reset the operation or its budget. Keep the exact request and source needed for recovery.

The View puts the Work title, ID, recorded state and next check together. `view work ID` adds the recorded scope and submitted observations before technical details. The agent explains any interpretation separately from that output.

Execution records have their own cards. They describe what was recorded for that run, including document effects and process closure. A shared Work ID does not establish a link to the current Work revision. If an unresolved run has an unknown effect, first inspect the permitted records and current files; any recovery or new execution follows the existing approval rules. An already resolved run can retain an unknown historical effect while current work proceeds under its own conditions. Detailed evidence shows the limits of what was checked.

### Choose The Next Work

For a completed task, ask for one recommendation or compare named alternatives. The agent first reads `./colvia view candidates`, then explains the proposed scope, checks and why it is useful now. An explicit request to record a candidate permits that planning change; execution and result acceptance retain their own boundaries.

If the runtime is missing after moving or cloning the project, acquire the exact pinned runtime from the trusted release. If the installed entry is damaged, use an independent trusted distribution and [Operations](../../../docs/OPERATIONS.md). Preserve detached records for supported reading rather than treating them as a fresh project.

### Hand off one Work item

Ask the agent to continue an approved Work item and tell you when its result is ready. Review the title, action, scope, deadline and local inbox before confirming. A one-shot process continues after the submitting client exits while the device and user session are available. The everyday actions are summarizing one active Work and submitting an already prepared result for review. See [environments and limits](work-guide.md#limits-en) for the separate document execution path.

Ask whether the Work has a question or result, or open `./colvia view inbox` from the project. Answer a question in that Work or stop the request. Device notifications use generic text. The local inbox retains the result even if delivery fails. After an interruption, inspect the existing Work and its recorded effects before submitting anything again.

If the deadline passes and the effect remains uncertain, ask what the Work records show. Once the worker is inactive, you may explicitly close that receipt with the outcome marked unknown. Its history and consumed step stay in the inbox. You can then hand off a different action.

If you missed the alert or selecting **View** on it does not open the submission, ask about the same Work in the inbox. Check the project and revision before deciding.

<a id="review-details" name="review-details"></a>

## Review and acceptance details

### Agree On A Small Result

For a document task, ask:

> The booking policy changed. Show me which parts of the FAQ and the support reply need an update. Fees are still undecided.

The agent reads project instructions, `./colvia view --details` and the current adapter, then identifies the existing plan, affected files, expected result, checks, limits and stop conditions. It resolves material gaps and prepares the exact intent for your decision. An existing applicable approval carries forward; a changed scope or consumed approval follows its contract. See [Guided Intent](../../../docs/GUIDED-INTENT-FORMATION.md).

### Implement And Check

Once you approve a plan that covers editing, checking and submitting the drafts for review, the agent establishes the Work baseline and edits within that scope. For this example, check that both documents agree at the 24-hour boundary and leave the fee undecided. Keep temporary test data outside the Work's tracked content unless it belongs to the accepted result. Missing or unavailable checks stay visible.

The agent records the result and presents what changed, what was checked and any remaining limits. It prepares the result confirmation and reads the same revision with `./colvia view work WORK_ID --revision REVISION_ID`. The agent substitutes the actual ID and prepares canonical input; you can review the explanation and confirmation without editing JSON. [General Work](../../../docs/GENERAL-WORK.md) defines the record fields and acceptance rules.

### Decide And Continue

When the result meets the agreed criteria, accept the exact result shown. The agent applies that ticket and checks the stored state and current files. Passing tests or a reviewer recommendation support your decision; the acceptance is yours. In local work, the edited files already exist in the control checkout. Worker results have their own exact application procedure.

The completion report should say what was achieved, what remains in the project plan and the recommended next step with its reason. A recommendation can be to finish here. If there is no selected follow-up, say so and explain what decision would be useful. A recommendation does not start another task.

### Preserve The Result

Keep the accepted records, necessary source and recovery inputs. Ask for Git status and the proposed preservation set before deciding on a commit or push. Review important ignored outputs separately. Clean up only when ownership, remaining use and recoverability are established. Work acceptance, Git integration and remote publication remain separate decisions.

If application stops or current files differ from the result, preserve the inputs and inspect the supported recovery path. Continue with [a fresh conversation](resume.md) using the project records rather than reconstructing authority from chat history.

<a id="operations-reference-and-earlier-exercises"></a>

## Installed documents and related references

This page belongs to the source manual. In an installed project, `./colvia view` identifies its current manual and adapter; `./colvia status` reports the verified `documentation_root`. Use those installed documents for operations.

### Keep These References Nearby

- [Extend project rules and remove Colvia](rules-and-removal.md): local instructions, runtime updates and entry cleanup after detach.
- [Installed setup procedure](../../../docs/GETTING-STARTED.md): installation and project preparation.
- [Command reference](../../../docs/REFERENCE.md): exact commands, input contracts and diagnostics.
- [Operations](../../../docs/OPERATIONS.md): update, recovery, repair and removal.
- [Key concepts](concepts.md#when-to-stop): short guidance when the first path cannot continue.

Linked technical and operating documents under `docs/` are in English.

<a id="earlier-checkout-exercise"></a>
<a id="what-was-checked"></a>

## Earlier exercise records

The [development record](../../../docs/development/CHORE-20261105-004-user-doc-tone-and-candidate.md#historical-exercise-en) preserves the earlier exercise results and package identities.

---

[Start the tutorial](getting-started.md) · [Key concepts](concepts.md)
