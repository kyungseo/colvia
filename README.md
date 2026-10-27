# Colvia

Colvia connects an agent-assisted task to your project plan, agreed scope, reviewable result and next choice. The agent prepares records; you decide material scope and acceptance. Those records and recovery evidence stay in the project-owned `.hrn/` directory. Cooperating linked workers can submit results for sequential application in one control checkout. General usability and real-project multi-worker efficiency remain unverified.

In an installed project, start with `./colvia view` and its verified manual/adapter; `./colvia status` provides machine diagnostics. Fresh setup uses an independent trusted source and the explicit `continuation-1` profile. Follow [Getting Started](docs/GETTING-STARTED.md) and project-owned rules.

The continuation-1 profile records a Work’s result and your selected follow-up independently. It also retains the optional exact grant that lets a named delegate accept one ordinary-worker Work result. [Profile and authorization](docs/README.md#continuation-1) explains the one-way update and the Owner decisions required for the source contract, exact installation and requested actions.

The runtime admits final, GIL-enabled CPython 3.14.6 or 3.14.7, with no third-party runtime dependencies. Later patches, prereleases and free-threaded builds are rejected. Passing the version check does not mean the OS or distributor build has been qualified. Primary Git checkouts and standalone non-Git projects can host control authority; linked worktrees cannot mutate it. See [Security and Support](docs/SECURITY-AND-SUPPORT.md) for trust and evidence limits.

## Read Next

- [Documentation Index](docs/README.md): current procedures and technical contracts.
- [Concepts](docs/CONCEPTS.md#the-work-cycle): the work cycle, five example requests, approval and resume.
- [Reference](docs/REFERENCE.md): source and installed commands.
- [Operations](docs/OPERATIONS.md): update, rollback, repair and detach.

For ideas before Work, use [Candidate Planning](docs/REFERENCE.md#candidate-planning). `./colvia view candidates` shows this branch's recorded choice and Work links. Selecting an idea prepares it for discussion; execution still needs its own authorization.

Generation1/2 commands, readers and migration are unsupported. Historical contracts and receipts are audit material. Public version, distribution, production support, actual adoption and host authentication require separate decisions and evidence.
