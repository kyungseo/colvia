# Installation and Work records in Colvia Preview

Install Colvia, connect a project folder, and start your first task. This guide also covers keeping the results you review and picking up the work in a new chat.

[First task](#start-with-the-work-you-want-to-do) · [Review and revise](#delegate-and-review) · [Updates and recovery](#updating-and-recovering-an-interrupted-update) · [Supported environments](#supported-environments)

[Register Git](#register-git) · [Put a result into Git](#put-an-accepted-result-into-git) · [Set up notifications](#set-up-notifications) · [Disconnect a project](#disconnect-a-project)

## Install and connect a project

Install Codex or Claude Code and sign in first. Run the installation command for your operating system. Colvia downloads and verifies the release files and prepares its own Python runtime. When setup completes, [check the installed version](#check-installed-version). See [updates and recovery](#updating-and-recovering-an-interrupted-update) for what to do after installation.

On Windows, open ordinary PowerShell from the Start menu as a standard user. If Colvia reports that it cannot verify the installation location from an app shell, continue in ordinary PowerShell. If it reports a lack of disk space, check the required and available space shown in the message.

After installation, open the project folder in Codex or Claude Code and ask:

> Connect this folder to Colvia.

Connect an empty folder to start something new, such as writing a report or building a web app. You can also connect a project you already work in. If the project uses Git, [ask the agent to register Git](#register-git) before connecting the repository root. In the connection preview, check the folder, the launcher and guidance Colvia will add, and where it will store records. Then approve the connection. Colvia uses your existing project rules and appends its guidance to the agent instructions where applicable. In a connected project, use `./colvia guide` on macOS or the project’s `colvia.cmd` on Windows (`.\colvia.cmd guide` in PowerShell). The agent then runs `ordinary list` through the same launcher to see the current Work.

Colvia keeps Work records for each project in a local SQLite database in the operating system’s user-data directory. The project folder contains connection information and entry guidance. Apps and CLIs use the same dedicated launcher.

If work stops, ask the agent where it got blocked. A launcher that won’t start, a folder the agent can’t read or write, and a change Colvia refuses because it’s outside the approved scope each need a different next step. If the app or CLI lets you grant access to just the path you need, use that option. If you can’t verify a way to grant access to that path alone, pause the affected changes and check what is blocked and what you can do next. Keep filesystem access limited to the necessary paths and leave trial features disabled while you check.

You may need to approve OS execution or notifications and sign in to your Codex or Claude subscription yourself. These steps are separate from preparing dedicated Python.

<a id="check-installed-version" name="check-installed-version"></a>

### Check the installed version

Once setup completes, run the following command to see the version next to `Colvia`.

macOS Terminal

```sh
"$HOME/Library/Application Support/Colvia/bin/colvia-manage" status
```

Regular PowerShell on Windows

```powershell
& (Join-Path ([Environment]::GetFolderPath("LocalApplicationData")) "Colvia\bin\colvia-manage.exe") status
```

## Start with the work you want to do

Once the folder is connected, tell the agent what you want to do here in the current chat. A sentence or two is enough. The agent may ask:

> The folder is connected. Tell me briefly what you’d like to work on here.

> I’d like to set up a small project to track action items from our team meetings.

In a folder without project material, the agent can explain what it sees and help turn an idea into a goal and a first task. You might say, “I’d like to summarize the meeting in one page.” If you have already shared a goal or task, the agent can use that request and any existing brief, README, or project rules to propose a plan.

For a document, ask for an outline and a way to check it. For a new app, ask for
a first version, a recommended stack and a way to run and test it. For example,
a personal to-do list that runs in one browser can start with a small web page
and browser storage. For a team list, review the proposed way to share the data
and control access as part of the first version.

If you already know what to do, ask for it directly. The agent can answer a short question or inspect files within the access already allowed.

You can skip creating a Work for a typo, spacing, or punctuation correction you explicitly request. The edit must follow your project rules and granted access, preserve meaning and behavior, and need no separate result review, retention, or handoff. If the edit belongs to an existing Work, check that Work’s approved scope and continue with its records.

You can discuss project goals and rules later, or
include them when you review the proposed scope. Check the file names and changes before approving that scope. Before recording the plan, review [what Colvia keeps](#retained-contents-and-backups).

## Delegate and review

> Summarize the types of customer inquiries and the complaints that come up most often in a report for our meeting. I’ll decide which improvements to prioritize.

The agent proposes files to work on and how to check the result. If you agree with the scope, tell it to proceed. When the work is ready, the agent records the check results and submits it for review. Read the submission and decide whether to accept it or ask for changes. Colvia records which plan you approved and which submission you accepted.

The app or CLI’s permission prompts control which files the agent can read or write and which tools it can run. Review the Work scope and its submission separately.

In a new conversation, open the same project and ask, “Show me only what I need to review in the report I assigned earlier.” If you use both Codex and Claude Code, you can switch between them in the same project. The new agent can find the records when it can read both the connected folder and the Colvia record folder. If the app created a Git worktree, first confirm which project it belongs to.

Keeping several Works is different from letting several agents edit the same files concurrently. Do not assume actual concurrent execution is supported in the first release. Overlapping changes or an unresolved interruption require checking the current state before proceeding.

Colvia’s direct agent execution for document tasks is disabled in the first Preview. Working in the ordinary Codex or Claude Code CLI or desktop app is separate from this feature.

To revise an earlier result after working on something else, tell the agent what to change. The agent checks the recorded request, approved scope, and changes since the last submission. If the approval is still valid and the requested changes fit the scope, continue in the same Work. Files added and submitted by another Work can be accounted for when its retained evidence and current content agree. Unattributed changes and outside-scope modifications or deletions are reported with the causal files. Your draft is preserved; you decide whether to accept the result after review.

Applying a revision that accounts for another Work’s added files to a different workspace is not yet available. You can review and accept it in its own workspace.

### Child Works and results from isolated folders

If you split a larger goal into direct child Works in the same folder, review and accept each submission. For an isolated folder (a registered Git worktree of the same repository), check the exact submission and destination. If the submission is still under review, use the preview to approve both applying and accepting it. Colvia records acceptance after applying the files and checking the destination. If you already accepted the submission, approve the application alone. Check the destination before applying. Colvia blocks the application if any other Work in that folder is approved, in progress, or under review. Apply one submission at a time, then review the combined result and checks before accepting the parent Work separately.

If applying an approved submission is interrupted, check whether Colvia recorded its preparation. When that record is available, resume the application with the approved submission. The destination connection and shared Git data must remain valid. If you can’t verify the preparation record or the destination connection, pause and ask for help diagnosing the issue.

To delegate applying and accepting a specific isolated Work, check the source, destination, file scope, named delegate, and a valid grant. The grant applies to the specified isolated Work. You decide whether to accept other Work and the final parent result.

If Git still lists a worktree whose folder has been removed, inspect its registration before continuing. For ordinary Work acceptance, Colvia still checks the current files in that Work’s own folder.

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

When a Work plan is recorded, Colvia keeps the existing contents of the listed files. It also keeps submitted contents so you can return to the version you reviewed. List only the files the work needs. Colvia keeps information about out-of-scope changes separately from retained file contents.

### Back up and restore records

Backups include contents kept when a plan is recorded, whether or not you approved it, as well as submissions. Store the backup as you would your project data. The Preview provides no way to delete selected retained contents, so review what you want to keep before recording the plan.

A Git commit or clone does not back up Colvia records. Use Colvia export and restore to move records, retained contents, settings and acceptance history. Keep project files separately as well. A recovery copy on the same device does not protect against device failure.

### Updating and recovering an interrupted update

Ask your agent, “Update Colvia.” Use the same account that installed Colvia. The agent can run the installed manager if it has access to the installation and can reach the official download site. If the app asks for permission, review the command and approve it there. If the agent cannot run the update in that account, use your terminal.

To update it yourself, rerun the command you originally used from the [official installation page](https://colvia.github.io/downloads/). If `colvia-manage` is on your `PATH`, you can also run `colvia-manage update`. For a default installation, use the full path below without changing your `PATH`.

macOS Terminal

```bash
"$HOME/Library/Application Support/Colvia/bin/colvia-manage" update
```

Windows PowerShell

```powershell
& (Join-Path ([Environment]::GetFolderPath("LocalApplicationData")) "Colviain\colvia-manage.exe") update
```

Colvia checks for a newer version at the address verified during installation. If you are already on the current release, Colvia keeps using that runtime.

Before updating, Colvia creates recovery copies of registered records and compares their required capabilities with those declared by the new runtime. This compatibility check does not run every user workflow. Returning to a compatible previous runtime does not roll work history back.

If an update stops, check where it stopped before changing any installed files. Resuming requires the exact prepared release, matching current state and still-valid verification.

If the first download was interrupted, keep the failed attempt’s record and start a new download explicitly. A prepared installation resumes the same files. If verification expires, reauthenticate the exact release or restore the interrupted update files while the previous runtime is still selected. Changed release targets and externally edited files are not overwritten. Do not erase retained files to bypass recovery checks.

If a first installation stopped after putting some files in place and the original release is no longer available, check the installation status and the quarantine preview. Files proven to belong to that attempt can be retained in quarantine before preparing a new release with the existing trust state. Resume the same quarantine if it stops. Unknown or externally changed files are not automatically cleaned up.

A backup containing unfinished external operations is not restored as immediately executable work. First establish what the original execution actually changed.

On macOS, if Colvia asks you to confirm a working folder, first identify the project and the folder it uses. Preview the listed projects and check the exact folders against your backup before applying the confirmation. This preserves the original Work scopes, retained contents and decisions. If the operation stops, inspect its status and resume the same operation for the remaining folders. If the folder was moved or replaced, check the [move conditions](#continue-after-moving-a-project-folder) before using any connection confirmation. Use a runtime that can read the project’s connection records when resuming.

### Remove Colvia and keep your records

Ask your agent, “Show me what would be removed if I uninstall Colvia and keep my records.” The agent can run the removal preview with the official installer script if it has the required access in the account that installed Colvia. Check the files it would remove and what it would keep. Ask the agent to apply the removal after you approve that preview. Project files, Work records, approvals, submissions, project connections, settings and update trust remain. Use the commands below if you want to do it yourself or the app cannot run them.

Use the standard account and default management folder you used to install Colvia. Finish any active Work, Git integration or update and close Colvia work and notification windows. Save the official installer script for [macOS ARM64](https://colvia.github.io/downloads/preview/macos-arm64/install.sh), [Windows x64](https://colvia.github.io/downloads/preview/windows-x64/install.ps1), or [Windows ARM64](https://colvia.github.io/downloads/preview/windows-arm64/install.ps1). Open Terminal or ordinary Windows PowerShell in the folder where you saved it.

**Preview the removal.** Choose an unused operation ID. This example uses `remove-colvia`.

macOS Terminal

```bash
/bin/sh ./install.sh --uninstall-preview remove-colvia
```

Windows PowerShell

```powershell
$path = (Resolve-Path -LiteralPath .\install.ps1).Path
$installer = [ScriptBlock]::Create([IO.File]::ReadAllText($path))
& $installer -UninstallPreview remove-colvia
```

**Apply after checking the preview.** Replace `RECEIPT_FROM_PREVIEW` with the receipt displayed in the preview. In PowerShell, continue in the same window.

macOS Terminal

```bash
/bin/sh ./install.sh --uninstall remove-colvia RECEIPT_FROM_PREVIEW
```

Windows PowerShell

```powershell
& $installer -Uninstall remove-colvia -Receipt RECEIPT_FROM_PREVIEW
```

The receipt is shown by the preview. If interrupted, use `--resume-uninstall` on macOS or `-ResumeUninstall` on Windows with the same operation ID and receipt.

**Reinstall when needed.** Run the usual install command in the same account. Open the same project to review its existing Work and submissions. If the installer reports that a reinstall is pending, use `--resume-reinstall` on macOS or `-ResumeReinstall` on Windows with the saved script. Keep the management folder and its records.

To undo an interrupted removal before starting a reinstall, use `-RestoreUninstall <operation ID> -Receipt <receipt>` on Windows or `--restore-uninstall <operation ID> <receipt>` on macOS. If you used Windows notifications before removing Colvia, enable them again after restoring or reinstalling.

## Continue after moving a project folder

### Ask your agent to check the move

If you’ve already moved the folder, open a new chat outside the project folder and ask:

> I moved this project folder. Help me continue with its existing Colvia records.

Give the agent the new path if it asks. With the access it needs, the agent can use the installed Colvia manager to prepare a move preview. Review the old and new paths. Once Colvia verifies it is the same folder, approve updating the existing connection. The agent can apply that preview, and you can open the project at its new location and check your earlier Work.

If you haven’t moved the folder yet, ask the agent to check the move conditions first. At the original location, finish any pending execution, delivery, Git integration, or recovery, or resolve its interrupted state. Keep a current Colvia backup and a separate copy of the project files. Close any chats and launchers that have the folder open, move the folder itself on the same local volume, and make the request above.

This flow covers an ordinary folder or a single Git checkout with its own
`.git` directory, with no linked worktrees, submodules or overlapping Colvia
project. The old location must be absent and Colvia must verify the same folder
identity. A copy, another volume or a folder inside another Colvia project can
fail these checks. If folders overlap, use a non-overlapping location. Preserve
both sets of files and records, and leave the connection file and database
intact. On macOS, if Colvia asks you to confirm the folder, follow the
[connection check and recovery guide](#updating-and-recovering-an-interrupted-update).

### Check a move from the command line

If you prefer commands or the agent can’t get the needed access, use the installed manager outside the project with the existing project ID and
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

The verified scope for moves covers ordinary and Git folders on local APFS on macOS.
If you’ve already moved a folder on Windows NTFS, keep the connection information and records and ask for help diagnosing the issue.
Use a compatible launcher to open records after a move.

## Working with Git

### Register Git

You can connect a plain folder right away. If your project uses Git, ask in your usual chat before connecting the repository:

> Register the Git executable I use for this project with Colvia.

The agent can find the executable in its current environment and prepare a registration preview. If it finds several paths, choose the Git installation you use. Check the path in the preview and approve the registration. The agent then applies the original preview. To change an existing registration, review the replacement path and approve the replacement separately. Once registration is confirmed, ask to connect the repository root. You can reuse the registered Git executable when connecting other projects in the same Colvia installation.

If the app or CLI blocks the command or a required path, ask the agent what access it needs. If the host lets you grant only that access, use that option. To register Git yourself, follow the [commands below](#register-git-from-the-command-line).

#### Register Git from the command line

Use the executable from a Git installation you trust. In Windows PowerShell, `(Get-Command git).Source` shows the path. Use ordinary PowerShell to install Colvia, but use Command Prompt (cmd.exe) to save the registration preview. Windows PowerShell 5.1 can re-encode output written with `>` or `Out-File`.

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

### Put an accepted result into Git

Accepting a submission keeps a version you can compare with your current files later. You can make that comparison without a work-in-progress (WIP) commit. To put the accepted submission into Git, review the full proposed commit and current staging state, then approve the integration separately.

Changing branches, pulling or rebasing during a Work does not automatically approve a new baseline. Colvia keeps changes outside the scope visible and requires checking how to continue. Independently connecting a repository subfolder, or automatically converting a folder between Git and non-Git operation, is outside the first-release path. Symlinks and submodules can remain protected, but are not editable targets.

If hooks are present or automatic integration conditions are not met, Colvia does not disable hooks or reset the index on its own. When continuing through manual Git operations, compare the accepted result with the contents you intend to commit. During an interrupted Colvia Git integration, do not delete `index.lock` or make another commit: the index may be temporarily absent while its original is retained. Inspect the integration and use its recovery path; an unconfirmed lock owner needs diagnosis. On Windows, Git integration requires staging on the same volume, and a hook file is treated as active even without a POSIX execute bit.

If Colvia Git integration stops on Windows, ask your agent to show the interrupted integration state and lock location. Recovery can continue if the current lock file matches the record Colvia made before moving it. A pre-commit interruption closes as not applied; after publication starts, recovery checks completion of the already-approved change. Colvia does not adopt or remove another Git program's lock, a changed file, or a lock whose ownership cannot be verified. If the blockage remains after other Git activity ends, preserve the interruption records and request diagnosis. Recovery does not accept a Work or authorize a new Git change.

## Notifications and disconnection

### Set up notifications

Connect the current installation’s receiver and allow notifications in the operating system. Where notifications are supported, click one to open the Work. Read the submission and decide whether to accept it.

After a Windows receiver update, reconnect notifications with the current installation before sending another event. If delivery is uncertain, Colvia keeps that event’s record and leaves any resend to a separate decision. In the project chat, ask, “Is anything waiting for my review?”

To stop new notifications, ask your agent, “Turn off Colvia notifications for this account.” The installed manager uses `notice-disable`. Existing Work records remain available.

### Disconnect a project

Ask the agent in that project, “Show me how Colvia would disconnect this folder while keeping my files and records.” Review the managed connection and guidance changes before approving them. Your files and Work records remain. If you plan to resume the Work later, [back up the records](#back-up-and-restore-records) before disconnecting. Review the folder identity and proposed changes when connecting restored records to a folder. To remove the installation, use [the record-preserving removal procedure](#remove-colvia-and-keep-your-records).

<a id="target-platforms-and-verification-status"></a>

## Supported environments

Colvia Preview targets macOS on Apple Silicon and Windows 11 on x64 and ARM64, with the Codex and Claude Code CLI and desktop apps. On Windows, this covers native Windows apps and CLIs. We’ll consider WSL as part of Linux support. The current filesystem boundary is local APFS on macOS and local NTFS on Windows. Network shares, synchronized record stores and Windows ReFS/Dev Drive are not qualified.

Use the official command for your operating system to start installation or an update. If setup or an update stops, see [updates and recovery](#updating-and-recovering-an-interrupted-update) for the procedure that matches its state. To resume applying a submission from an isolated folder, first check the preparation record and the destination connection.

Depending on the agent, you may need to grant access to the Colvia record folder in addition to the project folder. Tested Windows x64 setups include the Codex app with user approval and write access to one designated record folder, and Codex CLI 0.167.1 in MXC. Verification varies by app version and approval mode. Linux and additional agents are follow-up candidates.

The space and processing time needed for records and backups depend on the number of files and how much changes. Records accumulate over time, so check available space in projects with large files.

### Check document execution availability

Direct agent invocation is disabled in the first Preview. Run the installed launcher’s `execution readiness` to inspect its current configuration. The check leaves project records closed and does not start a model. If the check reports missing or changed files, inspect the reported state.
