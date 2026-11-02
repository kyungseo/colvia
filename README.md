# Colvia

Windows-2: see [entry and limits](docs/README.md#windows-2-integration-candidate).

Colvia connects agent-assisted work to a project plan, agreed scope, reviewable result and next choice. You decide material scope and acceptance; the agent prepares records in the project-owned `.hrn/` directory alongside recovery evidence. Linked workers submit results for sequential application in one control checkout. General usability and real-project multi-worker efficiency remain unverified.

In an installed project, start with `./colvia view`; agents read the verified manual/adapter in `./colvia view --details`; `./colvia status` provides machine diagnostics. Source-based fresh setup uses an independent trusted source and the explicit `continuation-1` profile; the macOS managed candidate uses the bootstrap procedure in Getting Started. Follow [Getting Started](docs/GETTING-STARTED.md) and project-owned rules.

The continuation-1 profile keeps Work results and selected follow-ups independent, retaining the optional exact grant for a named delegate to accept one ordinary-worker Work result. [Profile and authorization](docs/README.md#continuation-1) covers the one-way update and required Owner decisions for the source contract, exact installation and requested actions.

The runtime admits final, GIL-enabled CPython 3.14.6 or 3.14.7 without third-party runtime dependencies. The managed macOS arm64 candidate separately admits its exact pinned CPython 3.14.10 tree with isolated entry; this leaves the legacy version allowlist and Windows policy unchanged. Other unqualified builds, prereleases and free-threaded builds are rejected. Version admission does not qualify the OS or distributor build. Primary Git checkouts and standalone non-Git projects can host control authority; linked worktrees cannot mutate it. [Security and Support](docs/SECURITY-AND-SUPPORT.md) explains trust and evidence limits.

## Read Next

- [Documentation Index](docs/README.md): current procedures and technical contracts.
- [Concepts](docs/CONCEPTS.md#the-work-cycle): the work cycle, five example requests, approval and resume.
- [Reference](docs/REFERENCE.md): source and installed commands.
- [Operations](docs/OPERATIONS.md): update, rollback, repair and detach.

For ideas before Work, use [Candidate Planning](docs/REFERENCE.md#candidate-planning). `./colvia view candidates` shows this branch's recorded choice and Work links. Selecting an idea prepares it for discussion; execution still needs its own authorization.

Generation1/2 commands, readers and migration are unsupported. Historical contracts and receipts are audit material. Public version, distribution, production support, actual adoption and host authentication require separate decisions and evidence.
