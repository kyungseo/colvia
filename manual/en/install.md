# Install Colvia and connect a project

[User guide](README.md) · [한국어](../ko/install.md) · English

Install Colvia once for the operating-system account that will use it. Connect each project folder you want to use with that installation.

[Install](#install) · [Check the installed version](#check-installed-version) · [Connect a project folder](#connect) · [If access is blocked](#access)

## Before you begin

- Install Codex or Claude Code and sign in.
- Check that your operating system and agent are among the [supported environments](reference.md#environments).
- You may need to approve OS execution or notifications and sign in to your Codex or Claude subscription yourself. These steps are separate from preparing dedicated Python.

<a id="install" name="install"></a>

## Install

Copy and run the installation command for your operating system from the [official installation page](https://colvia.github.io/downloads/). Colvia downloads and verifies the release files and prepares its own Python runtime. When setup completes, [check the installed version](#check-installed-version). See [updates and recovery](maintenance.md#update) for what to do after installation.

On Windows, open ordinary PowerShell from the Start menu as a standard user. If Colvia reports that it cannot verify the installation location from an app shell, continue in ordinary PowerShell. If it reports a lack of disk space, check the required and available space shown in the message.

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

<a id="connect" name="connect"></a>

## Connect a project folder

After installation, open the project folder in Codex or Claude Code and ask:

> Connect this folder to Colvia.

Connect an empty folder to start something new, such as writing a report or building a web app. You can also connect a project you already work in. If the project uses Git, [ask the agent to register Git](git.md#git-register) before connecting the repository root.

In the connection preview, check the folder, the launcher and guidance Colvia will add, and where it will store records. Then approve the connection. Colvia uses your existing project rules and appends its guidance to the agent instructions where applicable.

### What a connection changes

| Location | What it holds |
| --- | --- |
| The project folder | The project launcher (`colvia` on macOS, `colvia.cmd` on Windows), connection information, and entry guidance for agents |
| The operating system’s user-data directory | A SQLite database with each project’s Work records, plus the dedicated launcher and manager |

Colvia keeps Work records for each project in a local SQLite database in the operating system’s user-data directory. The project folder contains connection information and entry guidance. Apps and CLIs use the same dedicated launcher. The exact paths are listed under [files and folders](reference.md#locations).

In a connected project, use `./colvia guide` on macOS or the project’s `colvia.cmd` on Windows (`.\colvia.cmd guide` in PowerShell). The agent then runs `ordinary list` through the same launcher to see the current Work.

Once the folder is connected, [start with the work you want to do](work.md#start).

<a id="access" name="access"></a>

## If access is blocked

If work stops, ask the agent where it got blocked. These three cases each need a different next step:

- A launcher that won’t start
- A folder or record store the agent can’t read or write
- A change Colvia refuses because it’s outside the approved scope

If the app or CLI lets you grant access to just the path you need, use that option. If you can’t verify a way to grant access to that path alone, pause the affected changes and check what is blocked and what you can do next. Keep filesystem access limited to the necessary paths and leave trial features disabled while you check.

Depending on the agent, you may need to grant access to the Colvia record folder in addition to the project folder. Tested setups are listed under [supported environments](reference.md#environments).

---

Next · [Follow along](tutorial.md) · [Assign and review work](work.md)
