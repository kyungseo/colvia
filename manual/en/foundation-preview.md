# Installation and records in the new Preview

This guide is for the new Preview, which stores Work records in SQLite. It does not migrate `.hrn/` records from earlier trial builds automatically.

## Install and connect a project

The planned public installer uses the same command for a first installation and for updating an existing one. Colvia downloads and verifies the required files, prepares dedicated Python and selects the version. You do not need to choose a Python ZIP or adjust pyenv or PATH. The public address and command will be published with the Preview.

On Windows, open ordinary PowerShell from the Start menu as a standard user. If Colvia reports that it cannot verify the installation location from an app shell, continue in ordinary PowerShell. If it reports a lack of disk space, check the required and available space shown in the message.

After installation, open the project folder in Codex or Claude Code and ask:

> I want to apply Colvia to this folder. Show me the changes needed while preserving existing files.

Both empty folders and existing projects can be connected. For a Git project, [register the Git executable](#working-with-git) before connecting at the repository root. Before connecting, review the launcher, agent guidance and record location. Existing instructions are preserved; only the Colvia guidance is added. In a connected project, use `./colvia guide` on macOS or the project’s `colvia.cmd` on Windows (`.\colvia.cmd guide` in PowerShell). The agent then runs `ordinary list` through the same launcher to see the current Work.

Each project's records are kept separately in the operating system's user-data directory. The project folder contains connection information and entry guidance. Apps and CLIs use the same dedicated launcher. If access is blocked, first identify whether the launcher needs to run or a file or record folder needs read or write access. Allow only the necessary path when the host provides a supported way to do so. If that option is unavailable, stop the affected changes; the agent should briefly explain what is blocked and any confirmed next step. Full filesystem access and trial features are not the default remedy.

You may need to approve OS execution or notifications and sign in to your Codex or Claude subscription yourself. These steps are separate from preparing dedicated Python.

## Start with the work you want to do

> I’d like to set up a small project to track action items from our team meetings.

In a folder without project material, the agent explains what it sees and helps
turn an idea into a goal and a first task. A sentence or two is enough to start.
If you have a brief, README or existing rules, point to them and the agent
builds on what you have already decided.

For a document, ask for an outline and a way to check it. For a new app, ask for
a first version, a recommended stack and a way to run and test it. For example,
a personal to-do list that runs in one browser can start with a small web page
and browser storage. For a team list, review the proposed way to share the data
and control access as part of the first version.

If you already know what to do, ask for it directly. The agent can answer a short question or inspect files within the access already allowed. For changes you want to review and retain, the agent can propose a Work. You can discuss project goals and rules later, or
include them when you review the proposed scope. Check the file names and changes before approving that scope. Before recording the plan, review [what Colvia keeps](#retained-contents-and-backups).

## Delegate and review

> Use inquiries.csv to write a meeting report. Compare inquiry types and possible improvements to our guidance. I will decide the priorities.

The agent proposes the output files and checks. If the scope is right, tell it to proceed. When the approved work is ready, the agent records the check results and submits for review. You decide whether to accept that result or request changes. A host permission prompt controls access. The Work scope and result each need your own decision.

In a new conversation, open the same project and ask, “Show me only what I need to review in the report I assigned earlier.” The design lets another agent read the same project's records. That agent needs access to both the connected folder and its record directory. A worktree created by an app must first be matched to the original project.

Keeping several Works is different from letting several agents edit the same files concurrently. Do not assume actual concurrent execution is supported in the first release. Overlapping changes or an unresolved interruption require checking the current state before proceeding.

When applying a result from another work folder, review the exact result and destination separately. Once that application is approved and reserved, Colvia uses only the retained result, even if the source folder later disappears or its files change. Later edits are not included in that acceptance. The destination and its project connection must remain valid; removing shared Git data can still block completion. If you delete only a worktree folder and Git retains a stale registration, inspect the Git worktree state before continuing. Ordinary result acceptance continues checking the current files.

Colvia’s direct agent execution for document tasks is disabled in the first Preview. Working in the ordinary Codex or Claude Code CLI or desktop app is separate from this feature.

To revise an earlier result after working on something else, tell the agent what to change. It resumes from the recorded request, approved scope and differences since the last submission without asking you to approve the same scope again. Files added and submitted by another Work can be accounted for when its retained evidence and current content agree. Unattributed changes and outside-scope modifications or deletions are reported with the causal files. Your draft is preserved; you decide whether to accept the result after review.

Applying a revision that accounts for another Work’s added files to a different workspace is not yet available. You can review and accept it in its own workspace.

### Find a recorded next step

Ask “What did we decide to do after the meeting report?” The agent can look up
the Work using `ordinary list`, then use `ordinary view WORK_ID` for the Work
or `followup WORK_ID` for its recorded choice. Use the same project launcher
for each command. `candidate list` shows saved candidates and any Work already
linked to them. These commands only read.

The record distinguishes a choice you have never made, a decision to leave no
follow-up, and a decision deferred until later. A selected candidate or Work
appears with its name and status. If a plan or candidate has changed, the
display tells you the choice was about the earlier record. Check that follow-up Work's own approval before starting it. Reuse a recorded approval that still covers the scope.

If implementation uncovers changes to files outside the approved scope,
preserve the existing work and checks. Ask for approval of the additional files,
the reason and any new checks, and record that scope as a separate Work before
editing those files.

#### Try it · Pick up a meeting report in a new chat

If you’ve submitted a meeting report in the same connected project, open a new chat and ask:

> Find the meeting report Work and show me its latest submission status and any recorded follow-up decision. Just look it up.

If the record says “No follow-up,” you recorded a decision to leave it without a follow-up. If there’s no recorded choice or you deferred the decision, the next step is still open. If you see a candidate or a Work, check whether the work you would continue already has an approved scope.

## Retained contents and backups

When a Work plan is recorded, Colvia captures the existing contents of its listed files. It also keeps the submitted contents of changes within the approved scope. Exclude passwords, API keys and unnecessary files before recording the plan. Information used to detect changes outside that scope is kept distinct.

Captured contents are retained even if you leave the plan unapproved. Exported backups include them. The Preview provides no way to delete selected contents. Consider this when choosing what to record and where to keep backups.

A Git commit or clone does not back up Colvia records. Use Colvia export and restore to move records, retained contents, settings and acceptance history. Keep project files separately as well. A recovery copy on the same device does not protect against device failure.

Before updating, Colvia creates recovery copies of registered records and compares their required capabilities with those declared by the new runtime. This compatibility check does not run every user workflow. Returning to a compatible previous runtime does not roll work history back. If an update stops, inspect that operation instead of overwriting the installation. Resuming requires the exact prepared release, matching current state and still-valid verification. An interrupted first download can continue as an explicit new attempt while retaining the failed attempt. A prepared installation resumes the same files. If verification expires, reauthenticate the exact release or restore the interrupted update files while the previous runtime is still selected. Changed release targets and externally edited files are not overwritten. The private HTTPS checks below did not exercise interruption recovery, reauthentication or quarantine. Quarantine of a partial first installation was checked in synthetic source tests. Do not erase retained files to bypass recovery checks. If a first installation stopped after publishing some files and its original release is no longer available, inspect the installation status and quarantine preview. Files proven to belong to that attempt can be retained in quarantine before preparing a new release with the existing trust state. Resume the same quarantine if it stops. Unknown or externally changed files are not automatically cleaned up.

A backup containing unfinished external operations is not restored as immediately executable work. First establish what the original execution actually changed.

On macOS, an older connection can ask you to confirm its working folder again. Preview the listed projects and check the exact folders against your backup before applying the confirmation. This preserves the original Work scopes, retained contents and decisions. If the operation stops, inspect its status and resume the same operation for the remaining folders. If the folder was moved or replaced, check the [move conditions](#continue-after-moving-a-project-folder) before using any connection confirmation. A previous runtime that cannot read the new connection record cannot reopen it.

## Continue after moving a project folder

Finish or resolve any pending execution, delivery, Git integration or recovery
at the original location. Keep a current Colvia backup and a separate copy of
the project files. Close the project's agent sessions and launchers, then move
the folder itself on the same local volume. Reopen the project only after
Colvia has verified the new location. In case you already moved the folder,
start by asking “I moved this project. Check whether I can continue with its
existing records.”

This flow covers an ordinary folder or a single Git checkout with its own
`.git` directory, with no linked worktrees, submodules or overlapping Colvia
project. The old location must be absent and Colvia must verify the same folder
identity. A copy, another volume or a folder inside another Colvia project can
fail these checks. If folders overlap, use a non-overlapping location. Preserve
both sets of files and records, and leave the connection file and database
intact. An older macOS connection may first need the same-location confirmation
described [above](#retained-contents-and-backups).

Use the installed manager outside the project with the existing project ID and
the new absolute path. For example, on macOS, save the preview under a new name
in a private local directory:

```sh
"$HOME/Library/Application Support/Colvia/bin/colvia" manage --json move-preview PROJECT_ID "/path/to/moved-project" > move-preview.json
```

On Windows, use Command Prompt as a standard user to preserve the preview
bytes. Windows PowerShell 5.1 can re-encode output redirected to a file:

```cmd
"%LOCALAPPDATA%\Colvia\bin\colvia.exe" manage --json move-preview PROJECT_ID "C:\Work\MovedProject" > move-preview.json
```

Review the old and new paths from a successful preview. After you approve,
use the same installed manager path shown above to apply the exact file and its returned receipt with
`manage move-apply --plan move-preview.json --receipt RECEIPT_FROM_PREVIEW --statement "YOUR_APPROVAL" --operation OPERATION_ID`.
Keep the file unchanged and use a new operation ID when starting. If interrupted,
inspect `manage move-status OPERATION_ID`. Resume a pending move using
`manage move-resume OPERATION_ID` with that same ID. If there is a conflict or
the earlier location is still present, keep the records and ask for diagnosis.
Once the move completes, reopen the new folder. The move updates the connection
and keeps the Work records, decisions and retained file contents.

Source tests verified ordinary and Git folder moves on local APFS. Windows NTFS movement and the
interaction with an older launcher or recovery runtime still need final
candidate checks. Use a compatible runtime to open records after a move.

## Working with Git

Plain folders can be connected without registering Git. Before connecting a Git repository, register the executable from the Git installation you trust. In Windows PowerShell, `(Get-Command git).Source` shows the path. Use ordinary PowerShell to install Colvia, but use Command Prompt (cmd.exe) to save the registration preview. Windows PowerShell 5.1 can re-encode output written with `>` or `Out-File`.

In Command Prompt, use a local NTFS folder that does not already contain `git-registration.json`. Replace the example Git path with the absolute path you found.

```cmd
"%LOCALAPPDATA%\Colvia\bin\colvia.exe" manage git-register-preview "C:\Path\To\Git\cmd\git.exe" > git-registration.json
```

This preview does not run Git. Read the file to check the path, file hash and `receipt` value. The receipt is the confirmation value returned in the preview. Do not edit or re-save the file. If the preview reports an error, do not apply the output file. Address the reported cause and use a fresh filename for another preview. Once you approve the registration, replace `RECEIPT_FROM_PREVIEW` with that value and apply it in the same Command Prompt. Add `--replace` only if you have confirmed that you want to replace an existing registration.

```cmd
"%LOCALAPPDATA%\Colvia\bin\colvia.exe" manage git-register --plan git-registration.json --receipt "RECEIPT_FROM_PREVIEW"
```

On macOS, open a terminal in a local folder that does not already contain `git-registration.json`. Replace `/path/to/git` with the absolute path to the Git executable you use. Save the preview, review it as above, then replace `RECEIPT_FROM_PREVIEW` with the value in the approved preview and apply it.

```sh
"$HOME/Library/Application Support/Colvia/bin/colvia" manage git-register-preview "/path/to/git" > git-registration.json
"$HOME/Library/Application Support/Colvia/bin/colvia" manage git-register --plan git-registration.json --receipt "RECEIPT_FROM_PREVIEW"
```

When applying a registration, the manager verifies the selected executable’s hash and checks its version. The hash covers that executable; you still need to trust the Git installation and its dependencies.

Accepting a report and committing it to Git are separate decisions. Acceptance records that you accept the result. Git integration separately checks the entire proposed commit and the current staging state.

Changing branches, pulling or rebasing during a Work does not automatically approve a new baseline. Colvia keeps changes outside the scope visible and requires checking how to continue. Independently connecting a repository subfolder, or automatically converting a folder between Git and non-Git operation, is outside the first-release path. Symlinks and submodules can remain protected, but are not editable targets.

If hooks are present or automatic integration conditions are not met, Colvia does not disable hooks or reset the index on its own. When continuing through manual Git operations, compare the accepted result with the contents you intend to commit. During an interrupted Colvia Git integration, do not delete `index.lock` or make another commit: the index may be temporarily absent while its original is retained. Inspect the integration and use its recovery path; an unconfirmed lock owner needs diagnosis. On Windows, Git integration requires staging on the same volume, and a hook file is treated as active even without a POSIX execute bit.

If Colvia Git integration stops on Windows, ask your agent to show the interrupted integration state and lock location. Recovery can recognize a gate recorded before its move when the current file matches that evidence. A pre-commit interruption closes as not applied; after publication starts, recovery checks completion of the already-approved change. Colvia does not adopt or remove another Git program's lock, a changed file, or an older lock without prior evidence. If the blockage remains after other Git activity ends, preserve the interruption records and request diagnosis. Recovery does not accept a Work or authorize a new Git change.

## Notifications and disconnection

To use notifications, connect the current installation's receiver and allow notifications in the operating system. After a Windows receiver update, reconnect notifications with the current installation before sending another event. A notification is a shortcut to the result. Clicking it never accepts the result automatically. If delivery cannot be confirmed, Colvia does not automatically resend it; the result remains available through the project conversation.

Disconnection removes Colvia-managed connection information and guidance after checking them. It preserves your files and work records. Reconnection, or binding restored records to a new folder, also checks the folder's identity and proposed changes. Disconnecting a project is not the same as deleting all its records.

## Target platforms and verification status

The first-release targets are macOS Apple Silicon ARM64 and Windows 11 ARM64 and x64, with Codex and Claude Code in CLI and desktop form. Windows means native Windows processes; WSL belongs to follow-up Linux support. The current filesystem boundary is local APFS on macOS and local NTFS on Windows. Network shares, synchronized record stores and Windows ReFS/Dev Drive are not qualified.

First installation over private HTTPS was verified on fixed candidates. On a Windows x64 device, sequence 6 installed and updated to 7, keeping work records, settings and the previous recovery slot. On Windows ARM64 and macOS ARM64 test VMs, standard accounts installed sequences 14 and 11 respectively and confirmed that their installed launchers were ready. Offline ARM64 updates and restore were checked on other candidates. Checking a recovery slot does not establish that rollback was performed.

The private HTTPS installation and update trials used a private address and trial trust. The official address, first public trust and rerunning the same installation command to update still require final-candidate checks. Earlier Windows x64 trials also verified a Codex app custom profile with user approval and access to one additional record folder (sequence 11), and scoped writes in Codex CLI 0.167.1 using MXC (sequence 10). The profile is a specific tested setup. The ordinary approval menu, other permission modes and the final candidate have separate verification. Linux and additional agents remain follow-up candidates.

Accumulation checks covered 300 Works with 100 input files and a small report. A separate content-retention check covered three versions of a 64 MiB file. Storage and processing time vary with file count, content size and changed bytes. New contents and backups keep consuming space; records are not pruned automatically. These measurements are not a long-term capacity limit or performance guarantee.


### Check document execution availability

Colvia does not call agents directly in the first Preview. The installed launcher’s `execution readiness` inspects the configuration without opening project records or starting a model. A successful inspection does not enable execution. Retained settings and history can still be read, and the setting can be disabled. If the check reports missing or changed files, inspect the reported state. Do not change Python or retry execution to bypass it.
