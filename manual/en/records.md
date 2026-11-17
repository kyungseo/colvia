# Records, backups, and moving folders

[User guide](README.md) · [한국어](../ko/records.md) · English

What Colvia keeps, how to back up and restore records, and how to continue with existing records after moving a project folder.

[What Colvia keeps](#retained-contents) · [Back up and restore](#backup) · [Continue after moving a folder](#move) · [Check a move from the command line](#move-cli)

<a id="retained-contents" name="retained-contents"></a>

## What Colvia keeps

When a Work plan is recorded, Colvia keeps the existing contents of the listed files. It also keeps submitted contents so you can return to the version you reviewed. List only the files the work needs. Colvia keeps information about out-of-scope changes separately from retained file contents.

| When | What is kept |
| --- | --- |
| A plan is recorded | The existing contents of the files in the plan, even before you approve it |
| A result is submitted for review | The contents changed within the approved scope (the submission) and the check results |
| You decide | Scope approvals, result acceptances, revision requests, and follow-up choices |

Records live in the operating system’s user-data directory, not in the project folder. See [files and folders](reference.md#locations) for the location.

The space and processing time needed for records and backups depend on the number of files and how much changes. Records accumulate over time, so check available space in projects with large files.

<a id="backup" name="backup"></a>

## Back up and restore records

Backups include contents kept when a plan is recorded, whether or not you approved it, as well as submissions. Store the backup as you would your project data. The Preview provides no way to delete selected retained contents, so review what you want to keep before recording the plan.

A Git commit or clone does not back up Colvia records. Use Colvia export and restore to move records, retained contents, settings and acceptance history. Keep project files separately as well. A recovery copy on the same device does not protect against device failure.

To make a backup, you can ask your agent:

> Export this project’s Colvia records to a new backup file. Tell me where it was saved and whether the backup completed. I’ll back up the project files separately.

Before restoring, check what will be restored.

> Before restoring this backup, check the target project and the Works it retains, and explain the decisions needed to restore and reconnect.

1. Export the records to a new file.
2. Store the backup file as you would your project data, on another device or storage where you can.
3. When restoring, check the Works and their retained contents.
4. Check the target folder, then connect the restored records to it.

When restoring Colvia records, check both the Work and its retained contents. Review the folder identity and proposed changes when connecting restored records to a folder.

A backup containing unfinished external operations is not restored as immediately executable work. First establish what the original execution actually changed.

<a id="move" name="move"></a>

## Continue after moving a project folder

### Ask your agent to check the move

If you’ve already moved the folder, open a new chat outside the project folder and ask:

> I moved this project folder. Help me continue with its existing Colvia records.

Give the agent the new path if it asks. With the access it needs, the agent can use the installed Colvia manager to prepare a move preview. Review the old and new paths. Once Colvia verifies it is the same folder, approve updating the existing connection. The agent can apply that preview, and you can open the project at its new location and check your earlier Work.

If you haven’t moved the folder yet, ask the agent to check the move conditions first. At the original location, finish any pending execution, delivery, Git integration, or recovery, or resolve its interrupted state. Keep a current Colvia backup and a separate copy of the project files. Close any chats and launchers that have the folder open, move the folder itself on the same local volume, and make the request above.

### Move conditions

- This flow covers an ordinary folder or a single Git checkout with its own `.git` directory.
- There must be no linked worktrees, submodules or overlapping Colvia project.
- The old location must be absent and Colvia must verify the same folder identity.
- A copy, another volume or a folder inside another Colvia project can fail these checks. If folders overlap, use a non-overlapping location.
- Preserve both sets of files and records, and leave the connection file and database intact.

On macOS, if Colvia asks you to confirm the folder, follow the [connection check guide](maintenance.md#folder-confirmation).

On macOS, same-volume moves were checked for ordinary folders and single Git checkouts on local APFS. On Windows, manager commands reconnected an ordinary folder after a move within the same local NTFS volume and read its existing Work. The Windows 11 ARM64 check used the official v0.1.0 release. The x64 check used an isolated 0.1.0 test build on a physical device. Git folders on Windows need separate verification. If you’ve already moved a Git folder on Windows, preserve the connection information and records and ask for help diagnosing the move. Use a compatible launcher to open records after a move.

<a id="move-cli" name="move-cli"></a>

### Check a move from the command line

If you prefer commands or the agent can’t get the needed access, use the installed manager outside the project with the existing project ID and the new absolute path. For example, on macOS, save the preview under a new name in a private local directory:

```sh
"$HOME/Library/Application Support/Colvia/bin/colvia" manage --json move-preview PROJECT_ID "/path/to/moved-project" > move-preview.json
```

On Windows, use Command Prompt as a standard user to preserve the preview bytes. Windows PowerShell 5.1 can re-encode output redirected to a file:

```cmd
"%LOCALAPPDATA%\Colvia\bin\colvia.exe" manage --json move-preview PROJECT_ID "C:\Work\MovedProject" > move-preview.json
```

Review the old and new paths from a successful preview. After you approve, use the same installed manager path shown above to apply the exact file and its returned receipt with `manage move-apply --plan move-preview.json --receipt RECEIPT_FROM_PREVIEW --statement "YOUR_APPROVAL" --operation OPERATION_ID`. Keep the file unchanged and use a new operation ID when starting.

If interrupted, inspect `manage move-status OPERATION_ID`. Resume a pending move using `manage move-resume OPERATION_ID` with that same ID. If there is a conflict or the earlier location is still present, keep the records and ask for diagnosis. Once the move completes, reopen the new folder. The move updates the connection and keeps the Work records, decisions and retained file contents.

---

Next · [Updates, notifications, disconnecting, and removal](maintenance.md) · [How it works · Record storage](architecture.md#storage)
