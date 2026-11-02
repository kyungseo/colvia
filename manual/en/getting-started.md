# Prepare Colvia And Your Project

[Contents](README.md) · [한국어](../ko/getting-started.md) · [Next: first Work](first-work.md)

Start with the result you want from the project. The macOS arm64 distribution candidate prepares Colvia and its own pinned Python, then connects the project through a separate preview and decision. Public distribution and final qualification are pending; use an authorized, qualified release for a real project. Windows is a required pre-publication check.

## Private Windows 11 ARM64 candidate

The isolated qualification used a standard account and local NTFS. Keep the supplied management executable and check its SHA-256 against the separately provided value with PowerShell `Get-FileHash -Algorithm SHA256`. Invoke it by its full path. The standard build uses the user's local application data directory. Test builds use a directory fixed at build time.

```powershell
$Manage = 'C:\Tools\Colvia\colvia-manage.exe'  # Use the actual verified executable path
& $Manage prepare --runtime-zip 'C:\Downloads\python-3.14.7-embed-arm64.zip'
& $Manage install --target (Get-Location).Path --json
```

The first command checks the original upstream archive and prepares a private Python runtime. The online download path still needs separate qualification. The second command previews the project connection. Review the scope, then ask the agent to apply the saved request with its confirmation. Once connected, use the same manager with `start`, `view` or `resume`. Each update, rollback, repair or removal has its own preview. Project removal preserves Work and approval records and the dedicated Python.

## Prepare the macOS tool

Use the named version and bootstrap digest supplied with the release. Download the bootstrap to a durable location, compare its SHA-256 with the separately provided value, then run it without arguments. Review its target storage and preservation plan before applying the displayed exact confirmation. The tool and Python live under `~/Library/Application Support/Colvia`; this path does not require a source clone, Homebrew setup or shell configuration edits.

## Connect A Project

Ask your agent:

> Preview connecting Colvia to this project with the verified release. Show the target, files that will change and what will be preserved. Keep the first task separate and wait for my installation decision.

Use a fresh non-Git folder or a primary Git checkout. An existing installation, retained detached records, unknown state or a linked worktree needs its own supported procedure. Keep exact requests outside the project. The agent uses the management command's `install --target PROJECT --json --save REQUEST_FILE`, explains the request, and applies that same request with its confirmation after your decision. Commands, supported transitions and recovery details are in [Getting Started](../../docs/GETTING-STARTED.md#macos-managed-distribution-candidate).

Before the first Work, agree on the project's purpose and plan, preserve existing instructions, and review the [project ignore rules](../../docs/GETTING-STARTED.md#prepare-project-ignore-rules). Keep shared instructions in project-owned `AGENTS.md`; Claude's entry can point to it while retaining unique tool instructions. A runtime update leaves these project-owned files in place. In managed distribution mode, effective Git policy comes from project configuration and ignore rules; review intended shared ignores before establishing the baseline.

## Check Where You Are

From the project folder, `./colvia view` shows current work and next steps. The agent reads `./colvia view --details` for the verified manual and adapter. A fresh connection has no accepted task or Work yet. Keep the stable view command in project instructions, not a remembered release directory.

If setup stops, preserve its request, exact distribution and partial state. Ask for the current state and supported recovery before another attempt. Completed detach preserves records for reading and does not create a fresh install target.

Next, [agree on the first Work](first-work.md). Historical checkout-1 observations from 2026-10-05 describe that older exercise; qualification of this distribution and its first-use flow is tracked separately.
