# Getting Started

Continuation-1 profile; see [authorization and qualification](README.md#continuation-1). Start with [the work cycle and example requests](CONCEPTS.md#the-work-cycle), then use the setup and first-Work steps below.

Use a fresh project and final, GIL-enabled CPython 3.14.6 or 3.14.7. Installation needs explicit operator authorization; a successful local test does not authorize installing into another repository.

## Prepare Project Ignore Rules

During authorized adoption, the agent/operator prepares project-owned root `.gitignore` before `init` and the first Work baseline. If absent, use the defaults below; otherwise preserve contents, comments and intentional exceptions, adding only missing applicable rules after review. Never overwrite it or copy the Harness source’s development `.gitignore`.

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

These defaults exclude personal IDE files; retain deliberate shared-configuration exceptions. Add build, dependency, environment and generated-output rules only after confirming actual project tools and artifact policy. Never blanket-ignore binaries or customer deliverables by extension.

Create root `temp/` for scratch during setup or when needed; clones do not restore empty ignored directories. Before pausing or cleaning up, preserve important ignored results durably outside scratch.

Never ignore the entire `.hrn/` tree: its records and managed runtime remain eligible for version control. Harness manages its own `.hrn/.gitignore` for `staging/` and `locks/`. Check representative IDE/temp paths with `git check-ignore`, and check that `.hrn/format.json`, `.hrn/intents/`, `.hrn/work/`, `.hrn/planning/`, `.hrn/product/`, `colvia` and project Markdown are not hidden by the effective rules. Git ignore rules do not untrack files already committed; do not remove tracked files as part of this setup without authorization.

The agent/operator performs this adoption procedure outside Core `init`. Root `.gitignore` and `temp/` stay project-owned; update, rollback and detach do not replace them. Once Work starts, ignore-rule changes must follow its scope and content-validation rules.

## Prepare Project Agent Entry

For new projects, put shared instructions, purpose/context/plan pointers and stable `./colvia view` entry in project-owned root `AGENTS.md`; never pin a managed release path. With Claude Code, add a thin root `CLAUDE.md` directing it to read and follow `AGENTS.md`, without duplicating instructions.

For existing projects, preserve entry files and tool-specific instructions. Reconcile shared instructions before replacing duplicates with pointers; preserve unique Claude rules and keep tool-specific additions in their entries. Do not copy this repository’s development entry. A pointer directs agents to read and follow `AGENTS.md`; it does not prove they did.

For project-specific adapter additions and their maintenance boundaries, use [Project-Owned Adapter Additions](REFERENCE.md#project-owned-adapter-additions). Runtime updates leave these additions unchanged; a later detach needs a separate review of obsolete project-entry instructions.

The agent/operator prepares these project-owned files within approved adoption scope. Core init/update/rollback/detach neither generate nor overwrite them. Managed payload entries describe Harness source, not the project.

Use [Repository-Owned Rules](REFERENCE.md#repository-owned-rules) to connect applicable documentation, validation and domain procedures. Include the project language default when one exists; [Document Language](REFERENCE.md#document-language) distinguishes it from an explicit artifact request and conversation explanations. For a new project, select a small set and connect its canonical location. For an existing project, compare affected rules and preserve local instructions before applying an authorized diff. Record the adopted source and any local choice in the existing rule or maintainer document. A runtime update does not update these rules automatically; compare relevant changes explicitly, including their verification and removal impact.

## Initialize A Fresh Project

From a trusted source, use [PowerShell for Windows-2](OPERATIONS.md#windows-init) or entry-1 below:

```sh
./colvia --source-checkout init --profile continuation-1 --target /path/to/project \
  --source /path/to/source --authority-home-id project-home \
  --operation-id init-1 --observed-at 2026-01-01T00:00:00Z
```

This previews the candidate and returns a `request` and `confirm_token`. Review the target and source; save only the `request` object as canonical JSON outside the target. Then apply that exact request:

```sh
./colvia --source-checkout init --profile continuation-1 --target /path/to/project \
  --source /path/to/source --apply --input /path/to/init-request.json --confirm TOKEN
```

Run `/path/to/project/colvia status` after installation. A verified active product exposes its `documentation_root`. No initial intent or Work is created. A preexisting launcher, old-generation home, unsupported Git topology, or ambiguous partial install is preserved and refused. Any immediate-root `hv2` occupant (NFC/casefold, file/directory/symlink) found at first admission is refused before the first target write; a late collision preserves earlier permitted writes and stops further publication. See [Entry-1 admission](WORKSPACE-CONTRACT.md#entry-1-admission-and-publication) for the tracked-but-absent distinction and exact limits.

## First Serial Work

1. An agent prepares a typed intent draft with goal, scope, expected outcome, acceptance oracle, destination, forbidden scope, and unresolved gaps. `colvia intent draft` publishes the proposed record; it does not accept it.
2. `colvia intent prepare` returns a ticket for the human to review. `colvia intent apply --confirm TOKEN` consumes the exact accepted ticket. Material gaps must be resolved first.
3. The agent publishes a Work baseline referencing the accepted intent, edits within the declared scope, and submits the full result manifest for review using `colvia work publish`.
4. `colvia work prepare` binds the exact result and current prerequisites. The human decides acceptance; `colvia work apply --confirm TOKEN` records that decision and selection. A selected accepted result derives completed state. The optional exact ordinary-worker grant is described in [Delegation-1](#delegation-1-implementation-candidate); it does not authorize intent or parent acceptance.

Use [General Work](GENERAL-WORK.md) for input fields and [Guided Intent](GUIDED-INTENT-FORMATION.md) for acceptance. The agent prepares canonical JSON via `--input FILE` or stdin; review without editing JSON below. General onboarding and installed use need [separate evidence](SECURITY-AND-SUPPORT.md). Keep one editing Work during serial use; the tool cannot stop arbitrary ordinary-file editors.

Do not use a pending proposal, a successful command, a review verdict, or an agent's statement as human acceptance. Use [Operations](OPERATIONS.md) when an exact operation is interrupted.

Accepting a worker result applies exact changes on control, leaving Git HEAD, index and refs unchanged. Before the next worker, follow project Git policy and [Git Integration And Candidate Reuse](GENERAL-WORK.md#git-integration-and-candidate-reuse). Its baseline needs a control commit matching the observed product and verified launcher; an existing candidate may suffice. Report Work acceptance and Git integration separately. The linked example covers reuse and stop conditions.

## Review Without Editing JSON

Start with `./colvia view` and follow its guidance to the current adapter; this release exposes verified manual/adapter paths in `./colvia view --details`. The managed manual explains Harness operation; project README/context/plan/DR/brief/Work documents explain project purpose and progress. Keep the stable view command in project entry, not a release-specific adapter path.

The agent prepares machine input and explains the existing Work narrative in your language: scope, progress, results, checks, limits and the decision needed. Review intent/Work and confirmation views; full revision identities and tokens support them. Decide the exact action before apply. Disclose changed/missing references and narrative/selected-record disagreement. English diagnostic labels do not set the conversation language. Views support the existing explanation; no automatic report, second status registry or extra record is needed.

For briefs, decision records or unresolved questions, use [Project Document Assistance](REFERENCE.md#project-document-assistance) with existing project documents.


## Transition To Checkout-1

Historical procedure for a retained qualified checkout-1 source only. The current candidate cannot perform this earlier transition. Use its exact retained manual and source; do not substitute a new profile. The first durable checkout-1 switch receipt is one-way even before new records, and loss of the original source/request can leave no supported recovery. Preserve restoration-verified recovery material before an authorized transition.

## Transition To Entry-1

Historical procedure for a retained qualified entry-1 source only. Read [Entry-1 transition](OPERATIONS.md#entry-1-transition) for its exact checkout-1 predecessor, one-way schema-2 boundary, original-request recovery, unsupported prefixes and separate worker rebind. These instructions do not authorize applying the current continuation-1 candidate with an old profile.

## Delegation-1 Implementation Candidate

Continuation-1 inherits the [optional schema-3 ordinary-worker grant](GUIDED-INTENT-FORMATION.md#delegation-1-implementation-candidate). Only an explicit Owner decision grants that exact scope; an agent role or broad instruction to continue does not. No-grant use keeps human acceptance. Intent and parent acceptance, Git integration and source-development acceptance remain separate. Host caller enforcement and general first-session usability are unverified.

Historical locator: entry-1→delegation-1 used the exact entry-1 inventory `2216a2634eb3fa5d6a8bfa7c7d4847b29fb2443ba7b367156c15b15ddb5a17e0`, matching retained source and original input. Old pending operations still need their own source/request. This is not the current transition path.

## Continuation-1 Setup And Resume

Fresh setup uses the continuation-1 command above. The exact release needs qualification, accepted source-contract scope and separate Owner installation authorization; source-only decision files are not installed prerequisites. For an existing installation, [Operations](OPERATIONS.md#continuation-1) admits only the exact delegation-1 predecessor or a compatible continuation-1 release. Do not apply the historical entry-1 transition instructions with current source.

Before starting work, name the existing project plan and the item it covers. After a result is actually accepted, report what that item achieved, what remains and whether the human selected a follow-up. Read `./colvia view continuation WORK_ID` in a new session. A proposal still needs intent approval; an existing Work follows its own current state; explicit none ends this follow-up path; undecided requires a choice only when the next action depends on it. The adapter explains plan updates and reference/content checks without adding another tracker.

## Windows-2 Entry

For a qualified windows-2 target, invoke the verified colvia file with an absolute allowed Python path and -I -B from native Windows PowerShell. This replaces only the generic ./colvia prefix; preserve arguments, human authorization and verified view/manual routing. Independent source lifecycle requires the explicit windows-2 profile, matching candidate and admitted native runtime. A POSIX shell, executable bit, entry-1 fallback or unverified interpreter alias is not a substitute. Fresh and same-window operations only; no old-window/cross-OS migration or detached-authority reinitialization. Report the exact qualified tuple and unavailable observations. These instructions grant no intent/result acceptance, writer authorization or environment qualification.

## Optional Official Execution Candidate

The shared source still declares `continuation-1`. Preparing `scripts/prepare-official.py --output NEW_DIRECTORY` creates the explicit macOS `official-execution-1` payload without installation or execution. Install only with separate authorization and the existing lifecycle preview/apply procedure. The verified release includes `docs/OFFICIAL-EXECUTION.md`. The candidate does not authorize updating an existing adopter or qualify Windows.
