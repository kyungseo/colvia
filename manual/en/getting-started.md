# Prepare A Project And Its First Plan

[Previous: introduction](README.md) · [Contents](README.md) · [Next: first Work](first-work.md)

[한국어](../ko/getting-started.md)

Start with a new practice project named `todo-lab`. By the end of this page, Harness will be installed and the project will have a purpose, a first plan and an agent entry. Installation will not have created or accepted any task.

## 1. Agree On The Project And The Working Directories

Use a fresh primary Git checkout in a durable location outside the Harness source. Keep request and ticket files in a separate durable directory outside the project. Use its physical path without symlink ancestors. If the confirmation view cannot read the path, use the actual physical path; do not delete the input or weaken checks. Do not reuse a customer project for this exercise. Read the [runtime and source prerequisites](README.md#before-you-start) first.

Ask Codex:

> Prepare a new practice project named todo-lab at the durable path I choose. Its purpose is a Python standard-library CLI that adds tasks to a JSON file and lists them in order. Propose the project path, a separate location for Harness request/ticket files, the trusted source path and preparation steps. Check Python and Git. Wait for my approval before creating files or installing Harness.

Review the paths and source. Approve the bounded preparation when they are correct. If the target already contains project files or an installation, stop; this fresh-project exercise does not cover that case. The [project ignore preparation guidance](../../docs/GETTING-STARTED.md#prepare-project-ignore-rules) explains preservation rules for existing project files, not how to update an existing installation.

The agent checks `python3 --version`, the interpreter's final/GIL-enabled build, `git --version` and target topology. A linked Git worktree cannot host control writes; this exercise uses the primary checkout. A successful version check alone does not qualify the source or operating system.

## 2. Prepare Project-Owned Files Before The First Work

The agent initializes Git and prepares:

| File | Purpose |
| --- | --- |
| `README.md` | What the task-list project is for and where its plan lives |
| `docs/plan.md` | The project goal, the first feature and deferred features |
| `AGENTS.md` | Shared project instructions, purpose/plan pointers and the stable `./hv2 view` entry |
| `.gitignore` | Applicable personal IDE, OS, scratch and Python-generated files |
| `docs/first-work.md` | The proposed scope and checks for the first Work |

These names are choices for this exercise; Harness does not impose a project-document directory layout or generate these files. If Claude Code will also be used, the agent can prepare a thin `CLAUDE.md` pointing to the project's `AGENTS.md`, while preserving any tool-specific instructions.

Use the [small ignore defaults](../../docs/GETTING-STARTED.md#prepare-project-ignore-rules) and add `__pycache__/` and `*.pyc` for this Python example. Create root `temp/` when needed for disposable scratch. Never ignore all of `.hrn/`; its records and runtime must remain eligible for Git tracking. Verify representative ignored paths and confirm that `.hrn/format.json`, intents, Work, planning, product files, `hv2` and project Markdown are not hidden by effective ignore rules. Ignore rules do not untrack existing commits.

Do this before recording a Work baseline. Ignore-policy changes, including global Git ignore rules, cannot be included in this first Work. Important ignored outputs need a durable copy before a pause or cleanup; an empty `temp/` directory will not return after a clone.

For repository-owned documentation or validation rules, select only the relevant rules and point to their canonical location from the project entry. Installation and later runtime updates do not install or update these project-owned rules automatically. See [Repository-Owned Rules](../../docs/REFERENCE.md#repository-owned-rules).

## 3. Review And Apply The Installation

Ask the agent to preview installation into the agreed target using the agreed qualified source. The preview is read-only. Review the target, source, runtime profile, proposed files and preservation/recovery requirements before approving that exact request. Have the agent compare `request.plan.candidate_release.sha256` in the preview with the README release digest and the qualification receipt for that artifact, then show you the comparison. Stop before approval if they do not match.

The agent saves the preview's `request` object outside the target and keeps its matching confirmation token. The response wrapper is not the apply input. After your explicit installation approval, it applies the saved request and checks the result. A token identifies the request; possession of it does not replace your decision.

<details>
<summary>Commands the agent uses for installation</summary>

These are templates. The agent replaces every `/absolute/path/...`, `UTC_TIME` and `TOKEN` from the reviewed paths and actual preview; do not paste them unchanged. Run from the trusted source checkout.

```sh
./hv2 --source-checkout init --profile checkout-1 \
  --target /absolute/path/todo-lab --source /absolute/path/trusted-source \
  --authority-home-id todo-home --operation-id init-todo --observed-at UTC_TIME
```

After exact approval, using the saved canonical request JSON:

```sh
./hv2 --source-checkout init --profile checkout-1 \
  --target /absolute/path/todo-lab --source /absolute/path/trusted-source \
  --apply --input /absolute/path/todo-lab-inputs/init-request.json --confirm TOKEN
```

Retain the exact source and original request for supported recovery. If apply fails, preserve the target and input and consult [Operations](../../docs/OPERATIONS.md); do not automatically repeat installation or delete `.hrn/`.

</details>

From the project root, the agent then runs:

```sh
./hv2 status
./hv2 view
```

Expected result: healthy installation, no pending operation, and no accepted intent or Work. `view` gives the current installed manual and natural-language adapter paths. Ask the agent to read those paths. Keep `./hv2 view` in `AGENTS.md`; do not copy a release-specific path there.

## 4. Turn The Goal Into A Small Plan

Ask Codex:

> Read the project README, AGENTS.md, current Harness adapter and docs/plan.md. Plan the first todo-lab feature: add a nonblank task to an explicitly chosen JSON file and list tasks in insertion order. Use only Python's standard library. Keep edit/delete, network access, extra dependencies and deployment outside this Work. Use the CLI contract and four behavior checks below. Record them, the proposed file scope, verification commands, execution environment, time/attempt limits and stop conditions in docs/first-work.md. Do not yet publish an intent or start implementation.

The first implementation will change only `todo.py`, `tests/test_todo.py`, `README.md` and `docs/first-work.md`. Use `python3 todo.py --file PATH add TEXT` and `python3 todo.py --file PATH list`, substituting the chosen JSON path and quoting task text. Adding a task prints `Added: TEXT`; listing prints one task per line as `1. TEXT`, `2. TEXT`, and so on. The initial plan must cover four behaviors: an empty list prints nothing and creates no file; adding two tasks preserves order; an empty or whitespace-only task exits with code 2 without writing; listing leaves data unchanged. These are behavior criteria, not a required number of test functions. Keep test data outside the project or in its already-ignored scratch directory so that a demonstration does not become an unexplained result change.

Before moving on, confirm that you and the agent agree on the goal, these four files, the exclusions, the CLI contract, the checks, the execution limits and where the result will remain. This project plan is a proposal. The next page turns it into an exact accepted request.

Edition: private development, `checkout-1`; checked 2026-10-05.

---

[Previous: introduction](README.md) · [Contents](README.md) · [Next: first Work](first-work.md)
