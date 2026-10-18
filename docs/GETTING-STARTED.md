# Getting Started

Delegation-1 profile; see [authorization and qualification](README.md#delegation-1-implementation-candidate).

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

Never ignore the entire `.hrn/` tree: its records and managed runtime remain eligible for version control. Harness manages its own `.hrn/.gitignore` for `staging/` and `locks/`. Check representative IDE/temp paths with `git check-ignore`, and check that `.hrn/format.json`, `.hrn/intents/`, `.hrn/work/`, `.hrn/planning/`, `.hrn/product/`, `colvia` and project Markdown are not hidden by the effective rules. Git ignore rules do not untrack files already committed; do not remove tracked files as part of this setup without authorization.

This is an adoption procedure performed by the agent/operator, not an extra write in the Core `init` transaction. Root `.gitignore` and `temp/` remain project-owned and are not replaced by update, rollback or detach. After a Work has started, changes to project ignore rules must follow that Work's scope and content-validation rules.

## Prepare Project Agent Entry

For a new project, keep shared project instructions in the project-owned root `AGENTS.md`. When Claude Code is used, create a thin root `CLAUDE.md` that instructs it to read and follow `AGENTS.md`; do not duplicate the full instructions. Include project purpose/context/plan pointers and the stable `./colvia view` entry in `AGENTS.md`, not a pinned managed release path.

For an existing project, preserve its entry files and tool-specific instructions. Compare and reconcile shared instructions before replacing a duplicate body with a pointer; do not overwrite unique Claude rules or copy this source repository's development entry into the project. Keep genuinely tool-specific additions in the corresponding entry. A pointer-only file means “read and follow AGENTS.md”; it is not evidence that a particular agent session actually did so.

For project-specific adapter additions and their maintenance boundaries, use [Project-Owned Adapter Additions](REFERENCE.md#project-owned-adapter-additions). Runtime updates leave these additions unchanged; a later detach needs a separate review of obsolete project-entry instructions.

These are project-owned files prepared by the agent/operator within the approved adoption scope. Core init/update/rollback/detach do not generate or overwrite them. Managed payload entries describe the Harness source and are not substitutes for the project's own entry.

Use [Repository-Owned Rules](REFERENCE.md#repository-owned-rules) to connect applicable documentation, validation and domain procedures. Include the project language default when one exists; [Document Language](REFERENCE.md#document-language) distinguishes it from an explicit artifact request and conversation explanations. For a new project, select a small set and connect its canonical location. For an existing project, compare affected rules and preserve local instructions before applying an authorized diff. Record the adopted source and any local choice in the existing rule or maintainer document. A runtime update does not update these rules automatically; compare relevant changes explicitly, including their verification and removal impact.

## Initialize A Fresh Project

From a trusted source checkout:

```sh
./colvia --source-checkout init --profile delegation-1 --target /path/to/project \
  --source /path/to/source --authority-home-id project-home \
  --operation-id init-1 --observed-at 2026-01-01T00:00:00Z
```

This previews the candidate and returns a `request` and `confirm_token`. Review the target and source; save only the `request` object as canonical JSON outside the target. Then apply that exact request:

```sh
./colvia --source-checkout init --profile delegation-1 --target /path/to/project \
  --source /path/to/source --apply --input /path/to/init-request.json --confirm TOKEN
```

Run `/path/to/project/colvia status` after installation. A verified active product exposes its `documentation_root`. No initial intent or Work is created. A preexisting launcher, old-generation home, unsupported Git topology, or ambiguous partial install is preserved and refused. Any immediate-root `hv2` occupant (NFC/casefold, file/directory/symlink) found at first admission is refused before the first target write; a late collision preserves earlier permitted writes and stops further publication. See [Entry-1 admission](WORKSPACE-CONTRACT.md#entry-1-admission-and-publication) for the tracked-but-absent distinction and exact limits.

## First Serial Work

1. An agent prepares a typed intent draft with goal, scope, expected outcome, acceptance oracle, destination, forbidden scope, and unresolved gaps. `colvia intent draft` publishes the proposed record; it does not accept it.
2. `colvia intent prepare` returns a ticket for the human to review. `colvia intent apply --confirm TOKEN` consumes the exact accepted ticket. Material gaps must be resolved first.
3. The agent publishes a Work baseline referencing the accepted intent, edits within the declared scope, and submits the full result manifest for review using `colvia work publish`.
4. `colvia work prepare` binds the exact result and current prerequisites. The human decides acceptance; `colvia work apply --confirm TOKEN` records that decision and selection. A selected accepted result derives completed state. The optional exact ordinary-worker grant is described in [Delegation-1](#delegation-1-implementation-candidate); it does not authorize intent or parent acceptance.

See [General Work](GENERAL-WORK.md) for exact input fields and [Guided Intent](GUIDED-INTENT-FORMATION.md) for acceptance semantics. Machine inputs are canonical JSON from `--input FILE` or stdin. The agent prepares these machine inputs; use the review flow below to review without editing JSON. General onboarding and actual use of the installed candidate require separate evidence; see [Security and Support](SECURITY-AND-SUPPORT.md). For serial use, keep one editing Work at a time; the tool cannot stop arbitrary processes editing ordinary files.

Do not use a pending proposal, a successful command, a review verdict, or an agent's statement as human acceptance. Use [Operations](OPERATIONS.md) when an exact operation is interrupted.

Accepting a worker result applies its exact changes on control but leaves Git HEAD, index and refs unchanged. Before starting the next worker, follow your project's Git policy and [Git Integration And Candidate Reuse](GENERAL-WORK.md#git-integration-and-candidate-reuse). The next baseline needs a control commit matching the observed product and verified launcher; an existing candidate may satisfy that requirement. Report Work acceptance and Git integration separately. The detailed example states when candidate reuse is possible and when to stop.

## Review Without Editing JSON

The manual path shown by `view` belongs to Harness itself. Use it for tool operation; use the project root README and project-owned context, plan, DR, brief and Work documents for project purpose and progress. Do not interpret links inside the managed manual as links to the project root.

Start with `./colvia view`. Ask your agent to read the current adapter and help plan or resume a task. The agent prepares validated machine input; you review project Markdown, `view intent ID`, `view work ID` and the exact confirmation screen. Decide the action before the agent applies it. A project entry may point to `./colvia view`; do not save a release-specific adapter path there. Update/rollback changes the path shown by the verified current binding.


The default human review is your existing Work narrative and a conversation in your language. Ask the agent to explain purpose and scope, plan and progress, results and verification, then the decision needed and next action. It reads your Work, DR and brief and compares their claims with the view's selected state and reference observations. A changed or missing document and any disagreement between prose and records must be disclosed.

`colvia view` currently prints English diagnostic Markdown. It is supporting evidence, not a replacement for the narrative or a standalone localized report. You do not need to decode its internal fields: the manual adapter guides the agent to explain them and link the original documents. Full revision identities and tokens remain available when reviewing an exact action. No automatic report file, second status registry or new record schema is introduced.

Later patches, prereleases and free-threaded builds are rejected. Other OS or distributor builds matching the accepted version conditions may execute; that is not a claim that they have been qualified. See [Security and Support](SECURITY-AND-SUPPORT.md).

For a requested brief, decision record or unresolved question, ask the agent to use [Project Document Assistance](REFERENCE.md#project-document-assistance) with your existing project documents.


## Transition To Checkout-1

Historical procedure for a retained qualified checkout-1 source only. The current candidate cannot perform this earlier transition. Use its exact retained manual and source; do not substitute a new profile. The first durable checkout-1 switch receipt is one-way even before new records, and loss of the original source/request can leave no supported recovery. Preserve restoration-verified recovery material before an authorized transition.

## Transition To Entry-1

Historical procedure for a retained qualified entry-1 source only. Read [Entry-1 transition](OPERATIONS.md#entry-1-transition) for its exact checkout-1 predecessor, one-way schema-2 boundary, original-request recovery, unsupported prefixes and separate worker rebind. These instructions do not authorize applying the current delegation-1 candidate with an old profile.

## Delegation-1 Implementation Candidate

This section describes the `delegation-1` profile; its heading is retained for existing links. Before actual installation or update, obtain the responsible Owner's authorization for source-contract activation and the exact qualified release. Development acceptance, exact-artifact checks and real adoption remain distinct. Installed readers use their verified release and project authorization; source-only decision files are not installed prerequisites.

Fresh installation uses `--profile delegation-1`; the exact release requires qualification, source-contract activation and Owner installation authorization before actual adoption. Synthetic verification does not establish those approvals. Continue to use `./colvia view` and its verified manual/adapter paths. Begin ordinary work with an Owner-accepted intent and keep acceptance separate from Git integration.

Before an authorized transition, verify the active entry-1 inventory SHA-256 is `2216a2634eb3fa5d6a8bfa7c7d4847b29fb2443ba7b367156c15b15ddb5a17e0`. Other older releases require their own supported sequence, not a forced direct transition. Resolve old pending operations with their exact old source and original requests first. Preserve the exact candidate source and transition request for forward recovery.

An Owner may explicitly include the schema-3 grant described in [Guided Intent](GUIDED-INTENT-FORMATION.md#delegation-1-implementation-candidate). The adapter must explain its exact scope and cannot infer it from an agent's role or a broad instruction to continue. Ordinary no-grant use remains supported. First-session usability and host caller enforcement are unverified.
