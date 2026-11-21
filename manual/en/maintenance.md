# Updates, notifications, disconnecting, and removal

[User guide](README.md) · [한국어](../ko/maintenance.md) · English

Procedures you need after installation. Each one has a different reach, so check which one you want first.

| What you want to do | What it affects | What remains |
| --- | --- | --- |
| [Update](#update) | The Colvia installation for this account | Records and connections for projects using this installation |
| [Turn notifications on or off](#notifications) | Notification delivery for this account | Existing Work records |
| [Disconnect a project](#disconnect) | One project | Your files and Work records |
| [Remove Colvia](#uninstall) | The installation for this account | Project files, Work records, approvals, submissions, project connections, settings and update trust |
| [Remove all records](#remove-all) | Every project connected in this account | Your project files and separately stored copies |

<a id="update" name="update"></a>

## Update

Updating keeps your Work. When you stop using Colvia, choose whether to [keep your records](#uninstall) or [remove them permanently](#remove-all).

Ask your agent, “Update Colvia.” Use the same account that installed Colvia. The agent can run the installed manager if it has access to the installation and can reach the official download site. If the app asks for permission, review the command and approve it there. If the agent cannot run the update in that account, use your terminal.

To update it yourself, rerun the command you originally used from the [official installation page](https://colvia.github.io/downloads/#en). If `colvia-manage` is on your `PATH`, you can also run `colvia-manage update`. For a default installation, use the full path below without changing your `PATH`.

macOS Terminal

```bash
"$HOME/Library/Application Support/Colvia/bin/colvia-manage" update
```

Windows PowerShell

```powershell
& (Join-Path ([Environment]::GetFolderPath("LocalApplicationData")) "Colvia\bin\colvia-manage.exe") update
```

Colvia checks for a newer version at the address verified during installation. If you are already on the current release, Colvia keeps using that runtime.

Before updating, Colvia creates recovery copies of registered records and compares their required capabilities with those declared by the new runtime. This compatibility check does not run every user workflow. Returning to a compatible previous runtime does not roll work history back.

<a id="update-recovery" name="update-recovery"></a>

### If setup or an update stops

If an update stops, check where it stopped before changing any installed files. Resuming requires the exact prepared release, matching current state and still-valid verification.

| Situation | How to continue |
| --- | --- |
| The first download was interrupted | Keep the failed attempt’s record and start a new download explicitly. |
| A prepared installation was interrupted | It resumes the same files. |
| Verification expired | Reauthenticate the exact release, or restore the interrupted update files while the previous runtime is still selected. |
| A first installation stopped after putting some files in place and the original release is no longer available | Check the installation status and the quarantine preview. Files proven to belong to that attempt can be retained in quarantine before preparing a new release with the existing trust state. Resume the same quarantine if it stops. |

Changed release targets and externally edited files are not overwritten. Unknown or externally changed files are not automatically cleaned up. Do not erase retained files to bypass recovery checks.

<a id="folder-confirmation" name="folder-confirmation"></a>

### If macOS asks you to confirm a working folder

First identify the project and the folder it uses. Preview the listed projects and check the exact folders against your backup before applying the confirmation. This preserves the original Work scopes, retained contents and decisions. If the operation stops, inspect its status and resume the same operation for the remaining folders. If the folder was moved or replaced, check the [move conditions](records.md#move) before using any connection confirmation. Use a runtime that can read the project’s connection records when resuming.

<a id="notifications" name="notifications"></a>

## Set up notifications

Connect the current installation’s receiver and allow notifications in the operating system. Where notifications are supported, click one to open the Work. Read the submission and decide whether to accept it. Clicking a notification does not accept the result.

After a Windows receiver update, reconnect notifications with the current installation before sending another event. If delivery is uncertain, Colvia keeps that event’s record and leaves any resend to a separate decision. If you miss a notification or it doesn’t open the result, ask in the project chat, “Is anything waiting for my review?”

To stop new notifications, ask your agent, “Turn off Colvia notifications for this account.” The installed manager uses `notice-disable`. Existing Work records remain available, and you can still check for results to review in the project chat.

<a id="disconnect" name="disconnect"></a>

## Disconnect a project

Ask the agent in that project, “Show me how Colvia would disconnect this folder while keeping my files and records.” Review the managed connection and guidance changes before approving them. Your files and Work records remain.

If you plan to resume the Work later, [back up the records](records.md#backup) before disconnecting. Review the folder identity and proposed changes when connecting restored records to a folder. To remove the installation, use [the record-preserving removal procedure](#uninstall) below.

<a id="uninstall" name="uninstall"></a>

## Remove Colvia and keep your records

Ask your agent, “Show me what would be removed if I uninstall Colvia and keep my records.” The agent can run the removal preview with the official installer script if it has the required access in the account that installed Colvia. Check the files it would remove and what it would keep. Ask the agent to apply the removal after you approve that preview. Project files, Work records, approvals, submissions, project connections, settings and update trust remain. Use the commands below if you want to do it yourself or the app cannot run them.

### Remove from the command line

Use the standard account and default management folder you used to install Colvia. Finish any active Work, Git integration or update and close Colvia work and notification windows. Save the official installer script for [macOS ARM64](https://colvia.github.io/downloads/preview/macos-arm64/install.sh), [Windows x64](https://colvia.github.io/downloads/preview/windows-x64/install.ps1), or [Windows ARM64](https://colvia.github.io/downloads/preview/windows-arm64/install.ps1). Open Terminal or ordinary Windows PowerShell in the folder where you saved it.

**1. Preview the removal.** Choose an unused operation ID. This example uses `remove-colvia`.

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

**2. Apply after checking the preview.** Replace `RECEIPT_FROM_PREVIEW` with the receipt displayed in the preview. In PowerShell, continue in the same window.

macOS Terminal

```bash
/bin/sh ./install.sh --uninstall remove-colvia RECEIPT_FROM_PREVIEW
```

Windows PowerShell

```powershell
& $installer -Uninstall remove-colvia -Receipt RECEIPT_FROM_PREVIEW
```

The receipt is shown by the preview. If interrupted, use `--resume-uninstall` on macOS or `-ResumeUninstall` on Windows with the same operation ID and receipt.

Colvia moves the removed installation files to `operations/<operation ID>/retired/` in the [management folder](reference.md#locations). It uses these files to undo an interrupted removal. They continue to occupy disk space while they are retained.

**3. Reinstall when needed.** Run the usual install command in the same account. Open the same project to review its existing Work and submissions. If the installer reports that a reinstall is pending, use `--resume-reinstall` on macOS or `-ResumeReinstall` on Windows with the saved script. Keep your records and the entire management folder for recovery.

To undo an interrupted removal before starting a reinstall, use `-RestoreUninstall <operation ID> -Receipt <receipt>` on Windows or `--restore-uninstall <operation ID> <receipt>` on macOS. If you used Windows notifications before removing Colvia, enable them again after restoring or reinstalling.

<a id="remove-all" name="remove-all"></a>

## Permanently remove Colvia and this account’s Work records

Ask your agent, “Remove Colvia completely. Show me what will be deleted first.” [Export any Work you want to keep](records.md#backup) outside the management folder. The preview lists managed project files, Work counts by state, built-in backups and installation files. If a folder has moved or cannot be verified, you can make it available again or exclude it. Connection files may remain in excluded folders and shared Git directories.

Save the official installer as described above. Run the preview from the account that installed Colvia. In Windows PowerShell, load the script into `$installer` as shown above.

| Step | macOS Terminal | Windows PowerShell |
| --- | --- | --- |
| Preview | `/bin/sh ./install.sh --purge-preview remove-all` | `& $installer -PurgePreview remove-all` |
| Apply after approving the list | `/bin/sh ./install.sh --purge remove-all RECEIPT` | `& $installer -Purge remove-all -Receipt RECEIPT` |
| Resume an interrupted removal | `/bin/sh ./install.sh --resume-purge remove-all RECEIPT` | `& $installer -ResumePurge remove-all -Receipt RECEIPT` |

To exclude all unverified folders, append `--exclude-unavailable` on macOS or `-ExcludeUnavailable` on Windows to both the preview and apply commands. Review the exclusions and files first. Once you approve this list, replace `RECEIPT` with its preview receipt. Colvia disconnects the verified projects first, preserves your files and Git staging, and deletes account databases and built-in backups last.

If another operation is writing, let it finish. If removal stops, keep the operation ID and receipt and resume the same operation. If ownership or file contents have changed, check the error and remaining paths. After removal, check any exclusions and the preparation folder printed by the installer. The last manual step below covers preparation folders from earlier installers.

Excluded folders keep their files. Their Work records in this account are erased with the other records. If the writer lock persists, close apps using Colvia. `remove-all` is an example operation ID. If that name was already used before approval, preview with a new ID. Once removal starts, resume using the original ID and receipt. If a managed file changed during removal, keep a copy of your edit and restore the approved contents and location before resuming. If you cannot restore them, stop and retain the remaining files and removal journal.

If you already uninstalled while keeping records, the preview reports `records-retained-after-uninstall`. Use the manual procedure below to check the steps you have completed and clean up the remaining files. Its final step also covers old installer folders listed under `retained_preparation_paths`.

### Manual cleanup with an older installer

A normal uninstall keeps your Work for reinstallation. Use these steps only when you intend to discard **the Work, approvals, submissions and recovery files for every project in this account**. To keep using other projects, [disconnect only the project you are leaving](#disconnect).

1. **Account for the projects you connected.** This Preview has no command that lists every connected folder. The manager’s `status` count can include records kept after disconnection. In a plain folder, look for the hidden file `.colvia-link.json`. In a Git project, run `git rev-parse --path-format=absolute --git-common-dir` and look for `colvia/connection.json` inside the reported directory. Use these files for identification only. If you cannot account for all connections or the originally connected worktree is gone, stop after the record-preserving uninstall.
2. [Export any Work you want to keep](records.md#backup) **outside the folders you will remove**. Confirm that export completed and locate the saved file. Keep your project files separately. In each project’s originally connected folder, ask your agent, “Show me what Colvia added. After I approve, disconnect the project and confirm it finished.” For multiple Git worktrees, use the originally connected worktree. Confirm that [disconnection](#disconnect) reached `detached` for each project. The agent can read `state` from the manager’s `--json` output. Stop on `pending` or an error. Project files, your own instructions, Git history and staged changes stay in place.
3. [Turn off notifications](#notifications) if enabled. Finish active work, close windows and processes using Colvia, then complete **steps 1 and 2 only** of the [normal uninstall](#uninstall). Check the output for your operation ID, `"state": "removed"` and `"records_preserved": true`. Keep the management folder if removal stopped, failed, is in recovery, or you used a custom installation path.
4. Run the command below to **select the default management folder**. It holds every project’s SQLite records, built-in backups, update trust data and uninstall recovery files. Inspect it for personal files, then **run the same command again** to reselect it. Move the selected item to the Trash or Recycle Bin only if its name is `Colvia` and its full path matches [this account’s default management folder](reference.md#locations). Cancel if nothing is selected, the item is a link or junction, or the system offers immediate permanent deletion. On Windows, use ordinary Delete, never Shift+Delete.

   macOS Terminal

   ```bash
   folder="$HOME/Library/Application Support/Colvia"
   if [ -d "$folder" ] && [ ! -L "$folder" ]; then open -R "$folder"; else echo "Cannot verify the default Colvia folder."; fi
   ```

   Windows PowerShell

   ```powershell
   $folder = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'Colvia'
   $item = Get-Item -LiteralPath $folder -Force -ErrorAction SilentlyContinue
   if ($item -and $item.PSIsContainer -and -not ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { Start-Process explorer.exe -ArgumentList ('/select,"' + $folder + '"') } else { Write-Warning 'Colvia folder not found.' }
   ```

5. Move a `Colvia-bootstrap-…` preparation folder to the Trash or Recycle Bin only if its **exact path** matches a `Recovery files:` line in your installer output. Keep it if you no longer have the log or cannot verify its origin. Leave the exports and personal backups you kept in step 2 outside this cleanup.
6. Confirm that the default `Colvia` folder is gone and that your project files and chosen backups remain. If you want permanent deletion, use the deletion date to select only the items you just moved. On Windows, check the original location too. Once permanently deleted, those records and recovery files cannot be restored from the Trash or Recycle Bin. OS notifications and permissions, manually configured app access or PATH entries, Git history, and system backups such as Time Machine or synced copies can remain.

---

Next · [Supported environments and reference](reference.md) · [How it works · Installation and updates](architecture.md#install-update)
