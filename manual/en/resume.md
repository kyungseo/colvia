# Resume From The Project Records

[Previous: first Work](first-work.md) · [Contents](README.md) · [한국어](../ko/resume.md)

Open a new conversation with access to the same project. Ask:

> Read this project's instructions and current Colvia Work. Explain what was accepted, what remains, any pending operation and the recommended next step with its reason. Check the existing authorization and limits before changing files.

The agent starts with project rules and `./colvia view --details`, reads the verified adapter, then compares the selected Work, referenced plan, continuation and current files. Human-facing `./colvia view` remains the compact overview. `./colvia help` shows query commands and prompt examples when needed.

## Recover The Current Situation

Expect a concise explanation of the accepted result, unfinished scope, current file agreement or drift, consumed time/attempts and valid remaining authority. A completed Work remains a historical acceptance even if files later change. Resolve differences between narrative and records before proposing a write.

If the previously approved task still has work remaining and its conditions hold, the agent continues it. If you asked only for a status check or recommendation, it stays read-only. A pending or unknown operation uses its recovery path; a new chat does not reset the operation or its budget. Keep the exact request and source needed for recovery.

## Choose The Next Work

For a completed task, ask for one recommendation or compare named alternatives. The agent first reads `./colvia view candidates`, then explains the proposed scope, checks and why it is useful now. An explicit request to record a candidate permits that planning change; execution and result acceptance retain their own boundaries.

If the runtime is missing after moving or cloning the project, acquire the exact pinned runtime from the trusted release. If the installed entry is damaged, use an independent trusted distribution and [Operations](../../docs/OPERATIONS.md). Preserve detached records for supported reading rather than treating them as a fresh project.

Fresh CLI-process reads and synthetic agent behavior are different observations. Record which was actually checked and retain unobserved real-project limitations.
