# Install, update or disconnect

[User guide](README.md)

Prepare the tools on your device, then preview the changes for each project you want to use. Preview packages target Apple silicon Mac and Windows 11 ARM64. On Windows, use a standard account and a local NTFS project folder. See [environments and limits](work-guide.md#limits-en).

| Where | What lives there |
| --- | --- |
| Your device | The manager and private Python can serve several projects. |
| Each project | Its installed copy and launcher. Preview changes for this folder before applying them. |
| The project's `.hrn/` folder | Task history, submissions and decisions. Disconnecting preserves these records. |

### Start in a new folder

Public downloads are in preparation. If you received a preview package, use the verification value supplied separately by the distributor. If Colvia is already installed, skip to connecting your practice folder.

On an Apple silicon Mac, check the bootstrap file with `shasum -a 256 "$HOME/Downloads/bootstrap.sh"`. Compare the digest with the separately supplied value. If it matches, run `/bin/sh "$HOME/Downloads/bootstrap.sh"` to preview the installation. Check the destination and run the displayed apply command with its confirmation code.

On Windows 11 ARM64, open PowerShell as a standard user. Check the manager with `Get-FileHash "$HOME\Downloads\colvia-manage.exe" -Algorithm SHA256`. If the digest matches, use the supplied ARM64 Python ZIP to prepare the tool and private Python. Adjust the paths if your downloads are elsewhere.

```powershell
& "$HOME\Downloads\colvia-manage.exe" prepare --runtime-zip "$HOME\Downloads\python-3.14.7-embed-arm64.zip"
```

Use the ZIP filename supplied with your manager. The manager checks the ZIP size and digest before preparing Python. This command is for ARM64.

Create an empty practice folder and open Codex or Claude Code in it. Ask “Show me what connecting this folder would change.” Check the folder and proposed changes before approving.

In an empty folder, start with what you want to make. In an existing project, ask “What would Colvia add here?” If your agent hasn’t encountered Colvia yet, give it the manager location from setup. Run the manager with `start --target "PROJECT"` to see the next step before changing any files.

### Connect an existing project

1. Ask “Show me this folder’s Colvia status and any work in progress.” If it already uses Colvia, check its installed version and manager. If it was disconnected, stop here. Keep the original folder and its `.hrn/` intact. To start over, choose a different folder. The next step is for a project that has never been connected.
2. For a new connection, preview `install` and inspect the target and files it will add. Check existing `AGENTS.md`, `CLAUDE.md` and `.gitignore` entries so team instructions and tracking rules are preserved. A symlink even inside an ignored directory can stop a Work check. If a check refuses the folder, identify the path and choose a suitable workspace while leaving existing files intact.
3. Apply the saved request and confirmation only after reviewing the changes. In the same project, ask “Show me the current work and what I should do next” to check that you can open the project view.

<a id="maintenance-en"></a>

### Update, recover or disconnect

**Update.** Verify the new distribution first. On an Apple silicon Mac, run the verified new bootstrap without options and review the apply command it displays. On Windows, prepare the new manager with its matching Python ZIP. Preparing the device leaves each project on its installed version. Check the project's status, preview `update` for that folder and review the confirmation before applying. To return to a previous version, check whether `rollback` is available. If a change stopped partway, keep the request file saved during preview and check the inputs for `repair` first.

If you use device alerts on Windows 11 ARM64, verify and prepare the new manager EXE, then run `notice-enable` with that EXE to update the existing registration. Use `notice-disable` when turning alerts off.

**Disconnect.** Reconnecting a folder with its existing Work history is currently unsupported. Leave it connected if you intend to return. Otherwise, preview and apply `remove` for that project. Afterwards, check `AGENTS.md` and `CLAUDE.md` for any Colvia instructions you added yourself. Remove only those lines.

**Remove everything.** Several projects can share the manager and its private Python. Follow these steps in order.

1. Identify the affected projects. Save the project files and hidden `.hrn/` directories you want to keep, along with original requests and sources needed for recovery. Check that the saved files are readable.
2. While the manager is still available, disconnect the affected projects one at a time. Stop here if other projects still use the tool.
3. On Windows, run `notice-disable` with the manager EXE used for registration, then delete that EXE. On Mac, preview the removal with `"$HOME/Library/Application Support/Colvia/bin/colvia-manage" remove-tool`. To apply it, repeat the command with `--apply --confirm` followed by the displayed value. The private Python and recovery files remain.
4. In Finder, use Go to Folder to open `~/Library/Application Support/Colvia`. In Windows Explorer, open `%LOCALAPPDATA%\Colvia`. On Mac, `runtimes` contains private Python, `releases` and `tools` hold software copies, and `requests` holds saved requests. On Windows, look for `python-…`, `tool-…` and `requests`. Delete only dedicated files no longer needed for any project, pending recovery or access to archived records. Check downloaded assets and requests or backups saved elsewhere separately.
5. Deleting a project's `.hrn/` also deletes its local Work and acceptance history. Decide separately whether you want to erase those records. Copies may remain in Git history or backups.

If a download or first launch is blocked, keep Gatekeeper or SmartScreen enabled and stop at the warning. To report a problem, include the asset name, operating system, step and expected result. Leave private paths and project contents out.

[Back to the user guide](README.md)
