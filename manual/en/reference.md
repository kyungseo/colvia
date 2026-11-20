# Supported environments and reference

[User guide](README.md) · [한국어](../ko/reference.md) · English

Look up supported environments, storage locations, commands, and terms here. The procedures themselves are in each guide.

[Supported environments](#environments) · [Files and folders](#locations) · [Command summary](#commands) · [Glossary](#glossary) · [When something goes wrong](#problems)

<a id="environments" name="environments"></a>

## Supported environments

Colvia Preview targets macOS on Apple Silicon and Windows 11 on x64 and ARM64, with the Codex and Claude Code CLI and desktop apps.

| Item | Preview scope |
| --- | --- |
| Operating systems | macOS on Apple Silicon, Windows 11 on x64 and ARM64 |
| Agents | The Codex and Claude Code CLI and desktop apps. On Windows, this covers native Windows apps and CLIs |
| Filesystems | Local APFS on macOS, local NTFS on Windows |
| Not qualified | Network shares, synchronized record stores, and Windows ReFS/Dev Drive |
| Follow-up candidates | Linux and additional agents. We’ll consider WSL as part of Linux support. |

Use the official command for your operating system to start installation or an update. If setup or an update stops, see [updates and recovery](maintenance.md#update-recovery) for the procedure that matches its state. To resume applying a submission from an isolated folder, first check the preparation record and the destination connection.

Depending on the agent, you may need to grant access to the Colvia record folder in addition to the project folder. Tested Windows x64 setups include the Codex app with user approval and write access to one designated record folder, and Codex CLI 0.167.1 with the Windows sandbox backend set to `mxc`. Verification varies by app version and approval mode.

The space and processing time needed for records and backups depend on the number of files and how much changes. Records accumulate over time, so check available space in projects with large files.

<a id="execution-readiness" name="execution-readiness"></a>

### Check document execution availability

Direct agent invocation is disabled in the first Preview. Run the installed launcher’s `execution readiness` to inspect its current configuration. The check leaves project records closed and does not start a model. If the check reports missing or changed files, inspect the reported state.

<a id="locations" name="locations"></a>

## Files and folders

<a id="device--the-colvia-management-folder" name="device--the-colvia-management-folder"></a>

### The account’s Colvia management folder

| Operating system | Location |
| --- | --- |
| macOS | `~/Library/Application Support/Colvia` |
| Windows | `%LOCALAPPDATA%\Colvia` |

| Entry | Contents |
| --- | --- |
| `bin/` | The launcher `colvia` and the manager `colvia-manage` (`.exe` on Windows), and the notification receiver on macOS |
| `notification-tools/` | The notification receiver on Windows |
| `runtime/` | Runtime slots holding dedicated Python and the Colvia code, and the current selection |
| `authorities/<project ID>/` | Records for each project. The SQLite database is here. |
| `backups/` | Recovery copies of records made before an update |
| `operations/` | Progress records for management operations and installation files retained during removal |
| `trust/` | Trust state used to verify updates |

Do not edit or delete files in this folder yourself. If you need to recover, use the procedures under [updates and recovery](maintenance.md#update-recovery). For an agent to read and write records, you may need to grant access to this folder in the app or CLI. After a completed uninstall, follow the [temporary manual cleanup procedure](maintenance.md#remove-all) if you also want to discard the account’s records.

### The project folder

Connecting adds the following to the project folder. The connection preview shows the same list.

| Entry | Contents |
| --- | --- |
| `colvia` (macOS), `colvia.cmd` (Windows) | The project launcher. It calls the installed launcher for this project path. |
| `AGENTS.md`, `CLAUDE.md` | Colvia appends a guidance block to the end of each file and creates the file if it is absent. Existing contents stay as they are. |
| Connection information | `.colvia-link.json` in a plain folder, or `colvia/connection.json` in the common Git directory of a repository. Worktrees of the same repository are each registered under this project connection. |

Connection information is a marker that identifies the project; it is not the record. Copying this file to another folder does not make that folder share the records.

<a id="commands" name="commands"></a>

## Command summary

Your agent normally runs these commands for you. To run one yourself, use `./colvia` on macOS or `.\colvia.cmd` in Windows PowerShell from the project folder. Check exact arguments with `./colvia <command> --help`.

### The project launcher

| Command | What it does |
| --- | --- |
| `guide` | Shows the short startup guide. For a specific step, append a topic such as `guide work` (submission and acceptance) or `guide recovery` (interrupted work). Both forms read verified instructions without opening project records. |
| `ordinary list` | The current list hides archived and discarded Work. Choose `--list-mode current`, `archived` or `all`. Unfiltered JSON keeps the full list. |
| `ordinary lifecycle-preview` · `ordinary lifecycle-apply` | [Pause, resume, discard or replace a Work](work.md#work-lifecycle) |
| `ordinary view`, `ordinary review`, `ordinary content` | Shows a Work’s state, a submission awaiting review, and retained contents. |
| `ordinary progress` | Save a note before the first submission. |
| `ordinary scope-preview` · `ordinary scope-apply` | [Add files before the first submission](work.md#scope-change) |
| `ordinary plan`, `plan-review`, `approve`, `start`, `submit`, `accept`, `revise`, `archive` | Moves a Work from a recorded plan through scope approval, submission, acceptance, revision requests and archiving. |
| `candidate list`, `candidate save`, `followup` | Shows and records candidates for later work and a Work’s follow-up choice. |
| `composition` | Names direct child Works under a parent Work. |
| `worker` | Applies a submission from an isolated folder to a destination folder. |
| `delivery` | Hands off submission of a prepared result and sends a notification. |
| `git-integration` | Puts an accepted result into Git under a separate approval, and recovers an interrupted integration. |
| `backup status`, `backup export` | Shows backup status and exports records. |
| `execution readiness` | Inspects the document execution configuration. Document execution is disabled in this Preview. |
| `manage` | Calls the manager of the same installation. |

Use the same paths, reason and checks for preview and apply. Supply the receipt and the user’s approval statement only on apply.

```text
ordinary scope-preview WORK_ID --edit table.md --create appendix.md --reason "Appendix" --check "Sources"
ordinary scope-apply WORK_ID --edit table.md --create appendix.md --reason "Appendix" --check "Sources" --receipt RECEIPT --statement "Approved"
```

Before the first submission, use the `progress_receipt` from `--json ordinary view WORK_ID`. If `first_project_note` is true, explain the older-version limit before saving. Each field is one line of up to 2,048 characters. Up to the first 128 approved paths are compared. Excess paths and unreadable files are reported as unavailable.

```text
ordinary progress WORK_ID --receipt RECEIPT --done "…" --checked "…" --remaining "…" --next-action "…"
```

Output is a human-readable summary by default. Put `--json` before the command group for machine output. Identifiers needed for a related Work or a diagnosis can appear in human output too.

### The manager

Call it as `colvia-manage` or through the project launcher’s `manage`. Some commands print JSON, such as a preview you save to a file and apply.

| Command | What it does |
| --- | --- |
| `status` | Shows the installed version and state. |
| `update`, `update-status`, `update-resume` | Updates, and inspects and resumes an interrupted update. |
| `update-rollback-preview`, `update-rollback` | Reverses the installation files changed by an update that stopped before the new runtime was selected. This is not a downgrade command. |
| `connect-preview`, `connect`, `connect-resume`, `connect-cancel` | Connects a folder. For a new local repository, preview with `connect-preview ROOT --init-git`. If Git is unregistered, add `--git-executable ABSOLUTE_PATH` to include account registration in the preview. After approval, use `connect` with the saved plan, receipt, statement and operation ID. Resume with `connect-resume OPERATION`. Before connection files are prepared, use `connect-cancel OPERATION` to release the reservation. |
| `detach-preview`, `detach` | Disconnects a project. |
| `move-preview`, `move-apply`, `move-status`, `move-resume` | Carries an existing connection over to a moved folder. |
| `git-register-preview`, `git-register` | Registers the Git executable to use. |
| `notice-enable`, `notice-disable`, `notice-check` | Turns notifications on and off and checks them. |
| `restore-prepare`, `restore-apply`, `rebind-preview`, `rebind` | Restores a backup and connects the restored records to a folder. |
| `repair-preview`, `repair-apply` | Recovers to a compatible previous runtime. Available only in the recovery mode started with the `--repair` option (for example `colvia-manage --repair repair-preview`). A recovery target compatible with the current records must exist. |

Removal and reinstallation use the official installer script, not the manager. See [Remove Colvia and keep your records](maintenance.md#uninstall).

<a id="glossary" name="glossary"></a>

## Glossary

| Term | Meaning |
| --- | --- |
| Work | A single task you scope and review. It keeps the goal, file scope, checks, submission, and decisions together. |
| Plan | The goal, file scope, checks and exclusions the agent proposes. Recording it keeps the existing contents of the files in scope. |
| Scope approval | Your decision to entrust the work under that plan |
| Submission | The result the agent submits for review. It holds the changed contents and the check results. |
| Acceptance | Your decision to accept the submission you read. It does not mean a Git commit or a deployment. |
| Revision request | A decision to have a submission changed. The work continues in the same Work. |
| Candidate | An item saved as something you might do later. Saving it grants no permission to start. |
| Follow-up choice | The record of what comes after a Work. It distinguishes a candidate, another Work, no follow-up, and undecided. |
| Child Work | A Work directly under a larger goal. You accept each result and the parent result separately. |
| Isolated folder | A registered Git worktree of the same repository |
| Preview and receipt | The changes shown before a state change, and the value bound to them. The change applies only when the receipt matches. |
| Project launcher | `colvia` or `colvia.cmd` in the project folder |
| Manager | `colvia-manage`, which manages the installation |
| Connection | The link between a project folder and its Colvia records. Disconnecting keeps your files and records. |

<a id="problems" name="problems"></a>

## When something goes wrong

Start by asking the agent where it stopped. Then use the guide that matches the situation.

| Situation | Where to look |
| --- | --- |
| The launcher won’t start, or a folder or record store can’t be accessed | [If access is blocked](install.md#access) |
| A submission was refused for changes outside the scope | [Delegate and review](work.md#review) · [When files outside the approved scope are needed](work.md#scope-change) |
| A new chat can’t find the earlier work | [Pick up in a new chat or with another agent](work.md#resume) |
| Setup or an update was interrupted | [If setup or an update stops](maintenance.md#update-recovery) |
| macOS asks you to confirm a working folder | [Confirm a working folder](maintenance.md#folder-confirmation) |
| You moved the project folder | [Continue after moving a project folder](records.md#move) |
| A registered Git worktree blocks a command | [Check Git worktree registrations](git.md#git-worktree-registration) |
| A Git integration was interrupted | [Recover an interrupted Git integration](git.md#git-recovery) |
| A notification doesn’t arrive or doesn’t open the result | [Set up notifications](maintenance.md#notifications) |
| Applying a result from an isolated folder was interrupted | [Child Works and results from isolated folders](work.md#child-works) |

Do not delete retained files or records to make an error go away. When a state can’t be established, stopping and asking for diagnosis is the safe choice.

## If you came from the earlier reference

<a id="notifications" name="notifications"></a>

- [Set up notifications and open the result](maintenance.md#notifications)

<a id="resume-details" name="resume-details"></a>

- [Pick up in a new chat](work.md#resume)

<a id="review-details" name="review-details"></a>

- [Review and accept a submission](work.md#review)

---

[Back to the user guide](README.md) · [Architecture](architecture.md)
