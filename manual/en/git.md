# Working with Git

[User guide](README.md) · [한국어](../ko/git.md) · English

In a project that uses Git, register Git with Colvia before connecting. Accepting a result and putting that result into Git are separate decisions.

[Register Git](#git-register) · [Register from the command line](#git-register-cli) · [Put an accepted result into Git](#git-integration) · [Recover an interrupted Git integration](#git-recovery)

<a id="git-register" name="git-register"></a>

## Register Git

You can connect a plain folder right away. If your project uses Git, ask in your usual chat before connecting the repository:

> Register the Git executable I use for this project with Colvia.

The agent can find the executable in its current environment and prepare a registration preview. If it finds several paths, choose the Git installation you use. Check the path in the preview and approve the registration. The agent then applies the original preview. To change an existing registration, review the replacement path and approve the replacement separately. Once registration is confirmed, ask to [connect the repository root](install.md#connect). You can reuse the registered Git executable when connecting other projects in the same Colvia installation.

If the app or CLI blocks the command or a required path, ask the agent what access it needs. If the host lets you grant only that access, use that option. To register Git yourself, follow the [commands below](#git-register-cli).

<a id="git-register-cli" name="git-register-cli"></a>

### Register Git from the command line

Use the executable from a Git installation you trust. In Windows PowerShell, `(Get-Command git).Source` shows the path. Use ordinary PowerShell to install Colvia, but use Command Prompt (cmd.exe) to save the registration preview. Windows PowerShell 5.1 can re-encode output written with `>` or `Out-File`.

**Windows.** In Command Prompt, use a local NTFS folder that does not already contain `git-registration.json`. Replace the example Git path with the absolute path you found.

```cmd
"%LOCALAPPDATA%\Colvia\bin\colvia.exe" manage git-register-preview "C:\Path\To\Git\cmd\git.exe" > git-registration.json
```

This preview does not run Git. Read the file to check the path, file hash and `receipt` value. The receipt is the confirmation value returned in the preview. Do not edit or re-save the file. If the preview reports an error, do not apply the output file. Address the reported cause and use a fresh filename for another preview. Once you approve the registration, replace `RECEIPT_FROM_PREVIEW` with that value and apply it in the same Command Prompt. Add `--replace` only if you have confirmed that you want to replace an existing registration.

```cmd
"%LOCALAPPDATA%\Colvia\bin\colvia.exe" manage git-register --plan git-registration.json --receipt "RECEIPT_FROM_PREVIEW"
```

**macOS.** Open a terminal in a local folder that does not already contain `git-registration.json`. Replace `/path/to/git` with the absolute path to the Git executable you use. Save the preview, review it as above, then replace `RECEIPT_FROM_PREVIEW` with the value in the approved preview and apply it.

```sh
"$HOME/Library/Application Support/Colvia/bin/colvia" manage git-register-preview "/path/to/git" > git-registration.json
"$HOME/Library/Application Support/Colvia/bin/colvia" manage git-register --plan git-registration.json --receipt "RECEIPT_FROM_PREVIEW"
```

When applying a registration, the manager verifies the selected executable’s hash and checks its version. The hash covers that executable; you still need to trust the Git installation and its dependencies.

<a id="git-integration" name="git-integration"></a>

## Put an accepted result into Git

Accepting a submission keeps a version you can compare with your current files later. You can make that comparison without a work-in-progress (WIP) commit. To put the accepted submission into Git, review the full proposed commit and current staging state, then approve the integration separately. Preparing a candidate creates Git objects. Applying it to your current branch and staging area is approved separately, after you review the candidate.

Colvia preserves changes staged for other files. To protect your staged changes, Colvia stops if the staged content for a selected file matches neither the current commit nor the accepted result.

Changing branches, pulling or rebasing during a Work does not automatically approve a new baseline. Colvia keeps changes outside the scope visible and requires checking how to continue. Independently connecting a repository subfolder, or automatically converting a folder between Git and non-Git operation, is outside the first-release path. Symlinks and submodules can remain protected, but are not editable targets.

If hooks are present or automatic integration conditions are not met, Colvia does not disable hooks or reset the index on its own. When continuing through manual Git operations, compare the accepted result with the contents you intend to commit.

<a id="git-recovery" name="git-recovery"></a>

## Recover an interrupted Git integration

During an interrupted Colvia Git integration, do not delete `index.lock` or make another commit: the index may be temporarily absent while its original is retained. Inspect the integration and use its recovery path; an unconfirmed lock owner needs diagnosis. On Windows, Git integration requires staging on the same volume, and a hook file is treated as active even without a POSIX execute bit.

If Colvia Git integration stops on Windows, ask your agent to show the interrupted integration state and lock location. Recovery can continue if the current lock file matches the record Colvia made before moving it. A pre-commit interruption closes as not applied; after publication starts, recovery checks completion of the already-approved change. Colvia does not adopt or remove another Git program's lock, a changed file, or a lock whose ownership cannot be verified. If the blockage remains after other Git activity ends, preserve the interruption records and request diagnosis. Recovery does not accept a Work or authorize a new Git change.

---

Next · [Records, backups, and moving folders](records.md) · [How it works · The Git boundary](architecture.md#git-boundary)
