# Resume From The Project Records

[Previous: first Work](first-work.md) · [Contents](README.md) · [한국어](../ko/resume.md)

Open a new conversation with access to the same project. Ask:

> Read this project's instructions and current Colvia Work. Explain what was accepted, what remains, any pending operation and the recommended next step with its reason. Check the existing authorization and limits before changing files.

The agent starts with project rules and `./colvia view --details`, reads the verified adapter, then compares the selected Work, referenced plan, continuation and current files. Human-facing `./colvia view` remains the compact overview. `./colvia help` shows query commands and prompt examples when needed.

## Recover The Current Situation

Expect a concise explanation of the accepted result, unfinished scope, current file agreement or drift, consumed time/attempts and valid remaining authority. A completed Work remains a historical acceptance even if files later change. Resolve differences between narrative and records before proposing a write.

If the previously approved task still has work remaining and its conditions hold, the agent continues it. If you asked only for a status check or recommendation, it stays read-only. A pending or unknown operation uses its recovery path; a new chat does not reset the operation or its budget. Keep the exact request and source needed for recovery.


The View puts the Work title, ID, recorded state and next check together. `view work ID` adds the recorded scope and submitted observations before technical details. The agent explains any interpretation separately from that output.

Execution records have their own cards. They describe what was recorded for that run, including document effects and process closure. A shared Work ID does not establish a link to the current Work revision. If an unresolved run has an unknown effect, first inspect the permitted records and current files; any recovery or new execution follows the existing approval rules. An already resolved run can retain an unknown historical effect while current work proceeds under its own conditions. Detailed evidence shows the limits of what was checked.

## Choose The Next Work

For a completed task, ask for one recommendation or compare named alternatives. The agent first reads `./colvia view candidates`, then explains the proposed scope, checks and why it is useful now. An explicit request to record a candidate permits that planning change; execution and result acceptance retain their own boundaries.

If the runtime is missing after moving or cloning the project, acquire the exact pinned runtime from the trusted release. If the installed entry is damaged, use an independent trusted distribution and [Operations](../../docs/OPERATIONS.md). Preserve detached records for supported reading rather than treating them as a fresh project.

Fresh CLI-process reads and synthetic agent behavior are different observations. Record which was actually checked and retain unobserved real-project limitations.

## Hand off one Work item

Ask the agent to continue an approved Work item and tell you when its result is ready. Review the title, action, scope, deadline and local inbox before confirming. A one-shot process continues after the submitting client exits while the device and user session are available. The supported actions are summarizing one active Work, submitting an already prepared result for review, and running a previously prepared document execution on the official macOS profile.

Ask whether the Work has a question or result, or open `colvia view inbox` from the project. Answer a question in that Work or stop the request. Device notifications use generic text. The local inbox retains the result even if delivery fails. After an interruption, inspect the existing Work and its recorded effects before submitting anything again.

If the deadline passes and the effect remains uncertain, ask what the Work records show. Once the worker is inactive, you may explicitly close that receipt with the outcome marked unknown. Its history and consumed step stay in the inbox. You can then hand off a different action.
