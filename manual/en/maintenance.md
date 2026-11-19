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

## Remove this account’s records after a trial

This is a **temporary manual procedure** until Colvia offers automatic removal of all connections and records. Disconnect each project first, then remove the account’s records yourself.

A normal uninstall keeps your Work for reinstallation. Use these steps only when you intend to discard **the Work, approvals, submissions and recovery files for every project in this account**. To keep using other projects, [disconnect only the project you are leaving](#disconnect).

1. In the account that installed Colvia, identify **every project you connected**. [Export any records you want to keep](records.md#backup) to a separate location and verify that you can recover them. In the folder where you originally connected each project, preview and approve [disconnection](#disconnect). You can ask your agent, “Show me what Colvia added to this folder and disconnect it.” Check that your documents, code, Git history, staged changes and existing agent instructions remain. Stop if a folder is missing, disconnection is refused, or you cannot account for all connections. Deleting the records first removes the information needed to detach the remaining folders.
2. If you enabled notifications, [turn them off](#notifications). Finish active operations and complete **steps 1 and 2 only** of the [normal uninstall](#uninstall). Continue only after removal succeeds. Keep the recovery files if removal fails or stops.
3. Run the command below to **select the exact default installation folder**. Inspect its contents for personal files. Return to its parent and move only the selected `Colvia` folder to the Trash or Recycle Bin. It contains every project’s SQLite records, built-in backups, update trust data and uninstall recovery files. These commands cover the default installation location.

   macOS Terminal

   ```bash
   open -R "$HOME/Library/Application Support/Colvia"
   ```

   Windows PowerShell

   ```powershell
   $folder = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'Colvia'
   if (-not (Test-Path -LiteralPath $folder -PathType Container)) { throw 'Colvia folder not found.' }
   Start-Process explorer.exe -ArgumentList ('/select,"' + $folder + '"')
   ```

4. Installer preparation folders may remain in the same parent folder. Move each `Colvia-bootstrap-…` folder to the Trash or Recycle Bin only when its **exact path** matches a `Recovery files:` line from this account’s installer output. Keep folders of uncertain origin. Select any downloaded installer scripts and exported backups separately where you saved them.
5. Check that the default `Colvia` folder is gone and your project files remain. To delete permanently, select **only the items you just moved** in the Trash or Recycle Bin and permanently delete them. You can no longer recover those records or undo removal from that recovery copy. OS notification permissions, previously delivered notifications and copies retained by system backups or sync services are managed separately.

---

Next · [Supported environments and reference](reference.md) · [How it works · Installation and updates](architecture.md#install-update)
