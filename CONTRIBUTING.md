# Contributing to Colvia

[English README](README.md)

Small changes are welcome for review. If you found a bug, describe what you expected, what happened, the operating system and the asset name or version you received. A short example in a clean project helps. Leave out account details, private paths and project files.

For a typo, a clearer example or a reproducible bug, open a focused pull request against `main`. Explain what changed and how you checked it. Discuss larger features, changes to what agents can do, or changes to stored Work records with a maintainer before implementing them.

Please keep security reports out of public issues and pull requests. During the private preview, contact the person who supplied your build privately. Before public release, we’ll list a private reporting contact here.

Colvia’s own code and documentation in this revision use Apache-2.0. Contributions intentionally submitted for inclusion are handled under section 5 of the license unless explicitly stated otherwise. Third-party components keep their own licenses. [License](LICENSE)

## Make your first change

Use the [next Preview guide](manual/en/foundation-preview.md) to see the SQLite candidate’s user flow. The earlier `.hrn/` profile has its own [user guide](manual/en/README.md).

For the source check below, use a standard GIL-enabled CPython 3.14.7 in a POSIX shell. The check ran in the development worktree on macOS 27.2 ARM64 with SQLite 3.54.0. Colvia’s installed runtime uses its own dedicated Python.

From the repository root, run this command before opening a PR for a change to the ordinary Work flow.

```sh
PYTHONPATH=src:tests python3.14 -B -m unittest test_foundation_work.WorkTests.test_one_approval_submission_prepares_review_and_one_acceptance
```

The test should report `OK`. It uses a synthetic project to check scope approval, submission for review, and acceptance of a specific result. Installed behavior, native execution, and a Windows contributor command need their own verification.

For a documentation change, check links and applicable instructions. For storage, packaging, or platform changes, choose the relevant checks from [Maintaining](docs/MAINTAINING.md#evidence-reuse-and-selection) and the [verification map](docs/development/product-evidence-and-followups.md#record-foundation-verification). Run the checks locally and include the command, environment and result in your PR to `main`.

## Maintainer Git policy (proposal)

Use a topic branch and a PR to main. Keep related changes reviewable and prefer a merge commit when individual accepted commits carry distinct evidence. Protect shared branches against deletion and force pushes. Require checks once the project actually runs them. Merging and publishing are separate owner decisions. Leave a distributed release tag in place; issue a new version for a correction. These are proposed practices, not a statement that branch or tag rules are enabled.

## Source development workflow

This file locates the rules for developing Colvia itself. Start with [Source Project Rules And Development Workflow](docs/development/WORKFLOW.md) and the [Development Index](docs/development/README.md). Use [Document and artifact placement](docs/development/document-ownership.md) to keep product specifications and reusable material in source while preserving private evidence separately. Decision-document rules are in the [Decision Guide](docs/DECISION-GUIDE.md); technical verification remains in [Maintaining](docs/MAINTAINING.md).

Reorganization and effective-state record: [DR-0006](docs/decisions/DR-0006-source-contributor-document-structure.md). Until the Owner accepts and activates its exact amendment, the [retained source procedures](docs/DECISION-GUIDE.md#retained-source-procedures) remain effective. After that recorded activation, the identified guides own the relocated rules. This entry does not activate them.

An installed-project agent starts with `./colvia view --details`, its verified manual/adapter and that project's own rules. The human overview remains `./colvia view`. Developing Colvia from its trusted source checkout does not require installing the runtime or creating a typed Work. The source rules here do not define a public contribution or licensing policy.

The headings below retain historical links. Their destinations follow the effective-state boundary above.

## Decisions

Decision identities, states, amendments and exact acceptance belong to the [Decision Guide](docs/DECISION-GUIDE.md). Its [decision catalog](docs/DECISION-GUIDE.md#decision-catalog) distinguishes current accepted records from Draft proposals.

## Roles And Authorization

Historical anchor retained. Read the workflow's [Roles And Authorization](docs/development/WORKFLOW.md#roles-and-authorization); use [Acceptance Records](docs/DECISION-GUIDE.md#acceptance-records) for exact decision identity and activation.

## Document Identity And State

Historical anchor retained. The [Decision Guide](docs/DECISION-GUIDE.md#document-identity-and-state) owns the relocated document rules.

## Review, Evidence And Disclosure

Historical anchor retained. Read [Review And Evidence](docs/development/WORKFLOW.md#review-and-evidence), [Disclosure](docs/development/WORKFLOW.md#disclosure), and the technical rules in [Maintaining](docs/MAINTAINING.md).

## Procedure Acceptance

Historical locator only. The original acceptance paragraph and its exact Git scope are preserved in [Decision Guide: History](docs/DECISION-GUIDE.md#history). It does not accept the reorganized files in this checkout.

## Additional Source Decisions

Historical locator only. Use the [decision catalog](docs/DECISION-GUIDE.md#decision-catalog) and the original [additional-source-decisions text](docs/DECISION-GUIDE.md#additional-source-decisions-history). Existing accepted records retain their meaning.

## Proposed Source Development Procedure

Historical anchor retained for links to the original appendix. [DR-0003](docs/decisions/DR-0003-source-development-procedure-and-bounded-intake.md) records its acceptance and activation. The relocation destination is [Source Project Rules And Development Workflow](docs/development/WORKFLOW.md); [DR-0006](docs/decisions/DR-0006-source-contributor-document-structure.md) controls whether that new location becomes effective.

### Start And Select

Read [Start And Select](docs/development/WORKFLOW.md#start-and-select) under the effective-state boundary above.

### Review And Execute

Read [Review And Evidence](docs/development/WORKFLOW.md#review-and-evidence) and [Execute Within The Approved Boundary](docs/development/WORKFLOW.md#execute-within-the-approved-boundary).

### Resume, Handoff And Close

Read [Resume And Handoff](docs/development/WORKFLOW.md#resume-and-handoff) and [Close And Assess Adopter Impact](docs/development/WORKFLOW.md#close-and-assess-adopter-impact).

[Writing and navigating the user guides](docs/development/user-documentation.md)


## Preparing source for lifecycle checks

The repository README introduces the product. The installed bilingual entry is maintained in `distribution/README-installed.md`; its links are relative to its destination, `README.md` in the prepared tree. Do not pass the raw developer checkout as a lifecycle candidate.

Prepare an ordinary managed source tree in a new directory outside the checkout:

```sh
python3 scripts/prepare-source.py --output /path/to/new-prepared-source
```

Then use that prepared directory as the explicit `--source` for a source lifecycle preview. Source `init` requires this argument; the user-facing management tools already supply it. Preview and apply remain separate. Windows and macOS packaging scripts apply the same README mapping and retain the installed file names and inventory. Preparation alone installs nothing.

### Record-foundation candidate preparation

For the SQLite candidate, [`foundation_bundle.assemble`](distribution/foundation_bundle.py) builds an unsigned archive from prepared inputs. Reproducing an identical release archive from a clone alone remains unverified. Assembly requires the pinned platform runtime, verifier dependencies and native launcher, plus the channel configuration, trust root and notices for that candidate. See [the supply and candidate procedure](docs/development/record-foundation/runtime-and-extension.md#supply-candidate-and-vm-reuse) and [verified results](docs/development/product-evidence-and-followups.md#record-foundation-verification).
