# Getting Started

## Agent setup and diagnosis

For an installed project, use the verified platform launcher to run `view --details` and follow the manual and adapter identified there. For a new project or a launcher that will not start, first identify the platform, the target folder and the trusted setup source. Follow the [macOS managed setup](OPERATIONS.md#onboarding-macos-managed-distribution-candidate) or [native Windows procedure](OPERATIONS.md#onboarding-windows-2-entry). Show the proposed changes before applying them with the user's approval.

For a guided first Work, open the [English exercise](README.md#guide-en) or [한국어 실습](README.md#guide-ko).

## Hand off one Work item

Hand off one supported step with a deadline of up to 24 hours. Ask for the result in your project inbox. [Handoff and inbox](REFERENCE.md#single-work-handoff-and-inbox)

## macOS Managed Distribution Candidate

[Prepare the tool and connect a project](OPERATIONS.md#onboarding-macos-managed-distribution-candidate).

### Technical Details

The managed runtime requires the exact normalized tree and manifests, including modes and isolated entry. An exact relocated copy may be admitted; this checks tree identity, not publisher or interpreter authentication. Legacy CPython 3.14.6/3.14.7 admission and Windows policy remain separate. [Runtime, Git and distribution conditions](OPERATIONS.md#onboarding-technical-details) apply when preparing installation or diagnosing it.

## Prepare Project Ignore Rules

During authorized adoption, preserve existing project ignore rules and intentional exceptions. Before init and the first baseline, follow the [project ignore defaults](OPERATIONS.md#onboarding-prepare-project-ignore-rules).

## Prepare Project Agent Entry

Keep the stable `./colvia view --details` command in project instructions, following its verified manual/adapter paths. Preserve existing project rules; use the [entry preparation procedure](OPERATIONS.md#onboarding-prepare-project-agent-entry) during setup.

## Initialize A Fresh Project

For trusted source setup, use a fresh project, final GIL-enabled CPython 3.14.6 or 3.14.7, explicit `--source-checkout` and the verified profile. Preview first and obtain installation authorization before exact apply. Follow the [source commands and admission conditions](OPERATIONS.md#onboarding-initialize-a-fresh-project). Managed installation uses the bootstrap procedure above.

## First Serial Work

1. State the intended result, editable scope and what must stay unchanged. The agent prepares the plan and typed intent.
2. Decide the exact intent; the agent records the applicable approval and publishes a Work baseline. A draft or confirmation token alone grants no authority.
3. The agent edits within scope, checks the result and submits the full manifest. Keep one editing Work during serial use.
4. Review the result and limits. Your acceptance selects the completed result; Git commit and publication are separate decisions. The agent explains one useful next step and its reason.

For example: “Which figures change if we exclude shipping from the inquiry report I reviewed yesterday?” The agent prepares machine input through the [installed adapter](../adapters/colvia-work/SKILL.md); exact fields and acceptance steps are in [General Work](GENERAL-WORK.md) and [the detailed procedure](OPERATIONS.md#onboarding-first-serial-work).

## Review Without Editing JSON

Ask in your own language about progress, results or next steps. The agent prepares exact records and explains the decision needed, including stale or missing references. Use `./colvia view --details` when technical identities or commands are needed. [Review details](OPERATIONS.md#onboarding-review-without-editing-json) cover project documents and confirmation views.

## Continuation-1 Setup And Resume

In a fresh conversation, ask: “Read the current Work and its plan; explain what was accepted, what remains and the recommended next step.” Compare records with current files, carry forward valid approval and consumed limits, and preserve pending operations. Read `./colvia view continuation WORK_ID` for the selected follow-up, including completed Work. A proposal, an existing Work, explicit none and undecided are distinct choices; selection alone authorizes no execution. See [resume details](OPERATIONS.md#onboarding-continuation-1-setup-and-resume).

## Transition To Checkout-1

Historical only: use the exact retained qualified source and original request. See [the retained procedure](OPERATIONS.md#onboarding-transition-to-checkout-1).

## Transition To Entry-1

Historical only: the current continuation-1 candidate does not perform this transition. See [the retained procedure](OPERATIONS.md#onboarding-transition-to-entry-1).

## Delegation-1 Implementation Candidate

The optional exact ordinary-worker acceptance grant requires an explicit Owner decision. Intent and parent acceptance, Git and source-development acceptance remain separate. See [grant boundaries](GUIDED-INTENT-FORMATION.md#delegation-1-implementation-candidate) and [historical details](OPERATIONS.md#onboarding-delegation-1-implementation-candidate).

## Windows-2 Entry

Use only the exact qualified native Windows tuple and explicit windows-2 profile. Current native qualification remains separate. Before setup, read [Windows entry and recovery](OPERATIONS.md#windows-2-native-entry-and-recovery) and [entry details](OPERATIONS.md#onboarding-windows-2-entry).

## Optional Official Execution Candidate

The shared source declares continuation-1. The optional macOS official-execution-2 payload needs its own preparation and installation decision; existing continuation projects have no direct switch. Follow [the exact procedure](OPERATIONS.md#onboarding-optional-official-execution-candidate) only when that profile is requested.

## Try your first Work

[Open this step in the user guide](README.md#guide-en).

## Before you begin

[Open this step in the user guide](README.md#guide-en-setup).

## Yesterday · agree on the change

[Open this step in the user guide](README.md#guide-en-plan).

## Today · make the decision

[Open this step in the user guide](README.md#guide-en-review).

## Update, Recovery And Removal

[Open this step in the user guide](README.md#guide-en-recovery).
