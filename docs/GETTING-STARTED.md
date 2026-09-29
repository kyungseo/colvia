# Getting Started

Use a fresh project and final, GIL-enabled CPython 3.14.6 or 3.14.7. Installation is an explicit operator action; do not infer permission to install into another repository from a successful local test.

## Prepare Project Ignore Rules

As part of an authorized Harness adoption, the agent/operator prepares a project-owned root `.gitignore` before `init` and before the first Work baseline. If it is absent, create it with the small default below. If it exists, preserve its contents, comments and intentional exceptions; review and add only missing applicable rules. Do not overwrite it or copy the Harness source checkout's development `.gitignore` into the project.

```gitignore
# Operating system files
.DS_Store
Thumbs.db

# IntelliJ IDEA: local project settings
.idea/
*.iml
*.iws
*.ipr

# Visual Studio Code: local settings and workspaces
.vscode/
*.code-workspace

# Project-root scratch space (not durable deliverables)
/temp/

# Editor temporary files
*.swp
*.swo
```

These defaults keep personal IDE files out of Git. If a project deliberately shares IDE configuration, retain its chosen exceptions. Add build, dependency, environment and generated-output rules only after confirming the project's actual tools and artifact policy; do not hide all binaries or customer deliverables by extension.

Create the root `temp/` directory for local scratch when preparing the project or when first needed. An empty ignored directory is not restored by a clone. Important ignored results need a durable copy outside that scratch directory before a pause or cleanup.

Never ignore the entire `.hrn/` tree: its records and managed runtime remain eligible for version control. Harness manages its own `.hrn/.gitignore` for `staging/` and `locks/`. Check representative IDE/temp paths with `git check-ignore`, and check that `.hrn/format.json`, `.hrn/intents/`, `.hrn/work/`, `.hrn/product/`, `hv2` and project Markdown are not hidden by the effective rules. Git ignore rules do not untrack files already committed; do not remove tracked files as part of this setup without authorization.

This is an adoption procedure performed by the agent/operator, not an extra write in the Core `init` transaction. Root `.gitignore` and `temp/` remain project-owned and are not replaced by update, rollback or detach. After a Work has started, changes to project ignore rules must follow that Work's scope and content-validation rules.

## Prepare Project Agent Entry

For a new project, keep shared project instructions in the project-owned root `AGENTS.md`. When Claude Code is used, create a thin root `CLAUDE.md` that instructs it to read and follow `AGENTS.md`; do not duplicate the full instructions. Include project purpose/context/plan pointers and the stable `./hv2 view` entry in `AGENTS.md`, not a pinned managed release path.

For an existing project, preserve its entry files and tool-specific instructions. Compare and reconcile shared instructions before replacing a duplicate body with a pointer; do not overwrite unique Claude rules or copy this source repository's development entry into the project. Keep genuinely tool-specific additions in the corresponding entry. A pointer-only file means “read and follow AGENTS.md”; it is not evidence that a particular agent session actually did so.

These are project-owned files prepared by the agent/operator within the approved adoption scope. Core init/update/rollback/detach do not generate or overwrite them. Managed payload entries describe the Harness source and are not substitutes for the project's own entry.

## Initialize A Fresh Project

From a trusted source checkout:

```sh
./hv2 --source-checkout init --profile worker-1 --target /path/to/project \
  --source /path/to/source --authority-home-id project-home \
  --operation-id init-1 --observed-at 2026-01-01T00:00:00Z
```

This previews the candidate and returns a `request` and `confirm_token`. Review the target and source; save only the `request` object as canonical JSON outside the target. Then apply that exact request:

```sh
./hv2 --source-checkout init --profile worker-1 --target /path/to/project \
  --source /path/to/source --apply --input /path/to/init-request.json --confirm TOKEN
```

Run `/path/to/project/hv2 status` after installation. A verified active product exposes its `documentation_root`. No initial intent or Work is created. A preexisting launcher, old-generation home, unsupported Git topology, or ambiguous partial install is preserved and refused.

## First Serial Work

1. An agent prepares a typed intent draft with goal, scope, expected outcome, acceptance oracle, destination, forbidden scope, and unresolved gaps. `hv2 intent draft` publishes the proposed record; it does not accept it.
2. `hv2 intent prepare` returns a ticket for the human to review. `hv2 intent apply --confirm TOKEN` consumes the exact accepted ticket. Material gaps must be resolved first.
3. The agent publishes a Work baseline referencing the accepted intent, edits within the declared scope, and submits the full result manifest for review using `hv2 work publish`.
4. `hv2 work prepare` binds the exact result and current prerequisites. The human decides acceptance; `hv2 work apply --confirm TOKEN` records that decision and selection. A selected accepted result derives completed state.

See [General Work](GENERAL-WORK.md) for exact input fields and [Guided Intent](GUIDED-INTENT-FORMATION.md) for acceptance semantics. Machine inputs are canonical JSON from `--input FILE` or stdin. The agent prepares these machine inputs; use the review flow below to review without editing JSON. Private human-1 use covered two accepted document Works and bounded fresh-session reading, not general onboarding or worker-1 adoption. For serial use, keep one editing Work at a time; the tool cannot stop arbitrary processes editing ordinary files.

Do not use a pending proposal, a successful command, a review verdict, or an agent's statement as human acceptance. Use [Operations](OPERATIONS.md) when an exact operation is interrupted.

## Review Without Editing JSON

The manual path shown by `view` belongs to Harness itself. Use it for tool operation; use the project root README and project-owned context, plan, DR, brief and Work documents for project purpose and progress. Do not interpret links inside the managed manual as links to the project root.

Start with `./hv2 view`. Ask your agent to read the current adapter and help plan or resume a task. The agent prepares validated machine input; you review project Markdown, `view intent ID`, `view work ID` and the exact confirmation screen. Decide the action before the agent applies it. A project entry may point to `./hv2 view`; do not save a release-specific adapter path there. Update/rollback changes the path shown by the verified current binding.


The default human review is your existing Work narrative and a conversation in your language. Ask the agent to explain purpose and scope, plan and progress, results and verification, then the decision needed and next action. It reads your Work, DR and brief and compares their claims with the view's selected state and reference observations. A changed or missing document and any disagreement between prose and records must be disclosed.

`hv2 view` currently prints English diagnostic Markdown. It is supporting evidence, not a replacement for the narrative or a standalone localized report. You do not need to decode its internal fields: the manual adapter guides the agent to explain them and link the original documents. Full revision identities and tokens remain available when reviewing an exact action. No automatic report file, second status registry or new record schema is introduced.

Later patches, prereleases and free-threaded builds are rejected. Other OS or distributor builds matching the accepted version conditions may execute; that is not a claim that they have been qualified. See [Security and Support](SECURITY-AND-SUPPORT.md).

## Transition From Human-1

Use a qualified independent worker-1 source's launcher with `--source-checkout update --profile worker-1 --target PROJECT --source CANDIDATE`. Review the exact preview request and token before apply. Do not run the old project's `./hv2 update --source CANDIDATE`: the old packager can incorrectly label new code as human-1. Check that the preview candidate has inventory_id worker-1. Source lifecycle requires an explicit worker-1 profile; retain the exact old source for pre-transition human-1 operations.

Preserve the old history, exact candidate bytes, confirmation request/token, and a trusted recovery tool outside the target. Update recovery uses the exact candidate supplied by --source; the trusted executing tool may be a separately verified worker-1-aware fix. After any durable worker-1 transition receipt, resume that exact transition from the independent source. A launcher/binding mismatch after interruption is not permission to delete records or reinstall.

The first worker-1 release has no supported rollback into human-1. After an update to another worker-1 release, rollback selects only the recorded previous worker-1 release. A mispackaged human-1 history containing a worker declaration is rejected even if an old tool restored the old active binding; automatic rescue of that unsupported history is not provided. New-source repair refuses human-1; use the exact old source before transition. Actual adoption requires exact-candidate qualification and human approval. Worker execution requires a committed control baseline including the installed launcher; upgrading the runtime does not require every later Work to use worker mode.
