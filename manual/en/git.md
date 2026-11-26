# Working with Git

[User guide](README.md) · [한국어](../ko/git.md) · English

For a Git repository, start by [asking to connect the folder](install.md#connect). If Git is not registered yet, the connection preview stops and asks you to register it first. Review and approve the registration as described below, then ask for the connection preview. Other projects in the same account can use the registered Git executable. Accepting a result and putting that result into Git are separate decisions.

[Register Git](#git-register) · [Register from the command line](#git-register-cli) · [Put an accepted result into Git](#git-integration) · [Recover an interrupted Git integration](#git-recovery)

When first connecting a folder that does not yet use Git, you can ask “Set up Git when you connect this folder.” See [the conditions and connection preview](install.md#first-git).

<a id="git-and-colvia-records"></a>

## Git keeps a file history. Why does Colvia keep records too?

You can approve a scope or ask for revisions before you have anything to commit. Colvia keeps the version you accept. For example, if you accept a report and then switch branches in the same working folder, you can reopen the accepted report and compare it with the one on your current branch.

If you later commit the accepted file, Git keeps its contents too. A colleague who pulls the branch won’t receive your approvals or requests for changes. [Where Colvia keeps these records and why](architecture.md#why-local-records) · [Recover an interrupted Git integration](#git-recovery)

A design note committed to a shared repository lets colleagues read the reasoning behind a decision. On the device that recorded the Work, Colvia can also show which revision the reviewer read and what changes they requested. A colleague cloning the repository receives the committed document. The local Work records stay on the recording device.

<a id="adopt-git"></a>

## Start using Git in a connected folder

In the same folder, ask “I'd like to manage this folder with Git.” Once you have [registered Git](#git-register), the agent checks the folder and its existing Work. The preview offers to create an empty `main` branch or use the repository you already created with `git init`. Approving it keeps your working files, staged changes, Work history and accepted results. Ask for a first commit or a remote separately when you need one.

Use a single project root on the same volume as the Colvia records. All Work must be finished or discarded, including any Work under review or paused. If you have yet to initialize Git, you can finish the Work first. Submodules, linked worktrees, ongoing Git operations and a Git-tracked Colvia locator also require attention before conversion.

If you ran `git init` while a Work was open, ask the agent in the original folder: “Back up my Work and help me finish it before switching to Git.” Colvia checks the original connection and repository. You can review the saved plan or submission, resume paused Work, and submit changes within the approved scope. Git-ignored files still count when Colvia checks for changes outside that scope. To stop a Work, review the discard preview and confirm that decision separately. Past approvals and submissions remain available.

To see your Work, run `./colvia --finish-plain-work ordinary list` on macOS or `.\colvia.cmd --finish-plain-work ordinary list` in PowerShell. Use the same option before `backup export` when following the [backup instructions](records.md). Choose a backup file and a scratch directory outside the project. A Work awaiting its first approval can be inspected or explicitly discarded in this mode. Once every Work is finished or discarded, review and approve the Git conversion; your staging is preserved.

After an interruption, ask the agent to resume the Git conversion. It uses the same operation ID. If your working files or staging have changed, review their current state and approve it again. The preview shows which Git settings or references changed and examples of working and staged paths. An index refresh by another Git client can also require confirmation. If another program initialized Git before Colvia applied its first project change, ask the agent to cancel the reservation and preview the existing repository. You can still read results accepted before the conversion. To revise those results or put them into Git, agree on the scope in a new Work.

<a id="git-register" name="git-register"></a>

## Register Git

Git registration applies to the account’s Colvia installation, so you do not need to repeat it for each project. If Git is already registered, ask to [connect the repository root](install.md#connect). A folder that stays without Git does not need registration.

If the connection preview asks you to register Git, or you want to register it in advance, ask:

> Register the Git executable I use for this project with Colvia.

The agent can find the executable in its current environment and prepare a registration preview. If it finds several paths, choose the Git installation you use. Check the path in the preview and approve the registration. The agent then applies the original preview. To change an existing registration, review the replacement path and approve the replacement separately. The replacement applies to every project using the registered Git executable in this account. Once registration is confirmed, ask to [connect the repository root](install.md#connect).

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

<a id="git-worktree-registration" name="git-worktree-registration"></a>

## If a registered Git worktree blocks a command

A missing worktree or an entry marked `bare` can stop Colvia when it checks the repository layout. This can happen during a connection preview or while running a command in a connected project. Ask the agent to show you the entry that blocked the command. To inspect the registrations yourself, run this in the repository.

```sh
git worktree list --porcelain
```

- For a path marked `prunable`, first check whether it is still accessible. If the folder moved or its drive is unavailable, restore access at the original path. If it is gone, ask the repository maintainer to inspect the branch, working files, and staged changes, preserve anything needed, and clear that registration.
- An entry marked `bare` is a repository with Git data and no working folder. Ask the maintainer to identify an eligible Git checkout.

Git’s bulk cleanup can affect several registrations. Preserve the contents of `.git` and other worktree registrations, and check the blocked command again after the maintainer’s action. If you were connecting the project, check the [connection preview](install.md#connect) again.

<a id="git-integration" name="git-integration"></a>

## Put an accepted result into Git

To put [the version you accepted](#git-and-colvia-records) into Git, review the selected files, the change preview and your current staging area, then approve the integration separately.

<a id="git-credential-check" name="git-credential-check"></a>

### If the credential check stops a commit · v0.2.0

Before creating Git objects, Colvia checks the selected files and their paths, the commit message, the branch name, the author’s name and email, and the operation ID on your device. It looks for recognizable keys and tokens, private keys, passwords embedded in URLs, and secrets written directly into settings. The check stops at the first finding. It shows the location and, when available, the type and line number. The value stays hidden. Before submitting a revision, you can ask your agent to check the other selected files for the same kind of value and report only the locations. For example, replace a key written directly into Python code with a reference such as `api_key = os.getenv("OPENAI_API_KEY")`, then submit and accept the revision. For a finding in the message, edit the message. This check covers Git changes prepared through Colvia. Previously stored Work and Git history keep their original contents.

Colvia blocks additions and edits to `.env`, `.env.local`, `.env.production`, and any file inside a `secrets/` directory. These names are matched case-insensitively at every level of the project. To share settings, keep `.env.example` or `.env.template` outside `secrets/` and use environment references for real values. Templates still go through the content check. The same protection covers `.netrc` (including `_netrc` on Windows), Terraform state files (`*.tfstate`), and backups (`*.tfstate.backup` or `*.tfstate.<digits>.backup`). Keystores (`.p12`, `.pfx`, `.jks`, `.keystore`) are also protected by path. When you delete a tracked file at a protected path, the preview shows the deletion and withholds its contents.

You can share a project `.npmrc`. Colvia blocks literal credentials in settings such as `_authToken`, `_auth`, and `_password`. Keep the registry settings and reference an environment variable such as `${NPM_TOKEN}` for the credential. When you replace a stored token with a reference, the preview shows the new configuration and withholds the old contents.

If you delete a protected file and include an exact copy of its contents at another path in the same commit candidate, Colvia stops even if you renamed the file. The same rule applies if you delete or edit a `.npmrc` that contained credentials and include an unchanged copy of its old contents elsewhere in the candidate. Remove the credential from the file you intend to share, then submit the revision.

**Including images and fonts.** Colvia accepts PNG, JPEG (`.jpg` or `.jpeg`), GIF, WebP and ICO images, and WOFF, WOFF2, TTF and OTF fonts, when the extension matches the file signature. It skips credential checks inside these files. Before approving the commit, review each path and format in the preview or in the JSON field `unchecked_assets` (for example, `{"logo.png": "PNG"}`). Protected paths and exact-copy checks still apply. SVG files go through the text check.

**When another file stops the candidate.** An image or font with a mismatched signature, a PDF, an archive, a database, an executable or another unsupported binary stops preparation. You can first integrate Works that exclude that file. If the file needs a separate commit, review its contents yourself before committing it with Git. Keep private keys and actual passwords out of the commit. Text must be UTF-8. Any line longer than 256 KiB stops the candidate, including in minified JavaScript or CSS.

When the previous contents of the same file contain a recognized credential or cannot be inspected, the preview identifies the deletion or shows the new content with the old side withheld. If Colvia says the previous preview contains material it cannot display, prepare a new preview. Preparing a candidate creates Git objects. Applying it to your current branch and staging area is approved separately, after you review the candidate.

### Check staging and repository state

Colvia preserves changes staged for other files. To protect your staged changes, Colvia stops if the staged content for a selected file matches neither the current commit nor the accepted result.

Changing branches, pulling or rebasing during a Work does not automatically approve a new baseline. Colvia keeps changes outside the scope visible and requires checking how to continue. Independently connecting a repository subfolder, or automatically converting a folder between Git and non-Git operation, is outside the current Preview’s supported workflow. Symlinks and submodules can remain protected, but are not editable targets.

If hooks are present or automatic integration conditions are not met, Colvia does not disable hooks or reset the index on its own. When continuing through manual Git operations, compare the accepted result with the contents you intend to commit.

<a id="git-recovery" name="git-recovery"></a>

## Recover an interrupted Git integration

During an interrupted Colvia Git integration, do not delete `index.lock` or make another commit: the index may be temporarily absent while its original is retained. Inspect the integration and use its recovery path; an unconfirmed lock owner needs diagnosis. On Windows, Git integration requires staging on the same volume, and a hook file is treated as active even without a POSIX execute bit.

If Colvia Git integration stops on Windows, ask your agent to show the interrupted integration state and lock location. Recovery can continue if the current lock file matches the record Colvia made before moving it. A pre-commit interruption closes as not applied; after publication starts, recovery checks completion of the already-approved change. Colvia does not adopt or remove another Git program's lock, a changed file, or a lock whose ownership cannot be verified. If the blockage remains after other Git activity ends, preserve the interruption records and request diagnosis. Recovery does not accept a Work or authorize a new Git change.

---

Next · [Records, backups, and moving folders](records.md) · [How it works · The Git boundary](architecture.md#git-boundary)
