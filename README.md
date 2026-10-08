# Harness v2

Harness v2 records human intent, proposed work, exact acceptance, and recovery evidence in one project-owned `.hrn/` directory. The development candidate provides local Work records and bounded linked-worker submission, human acceptance and sequential application in one control checkout. A manual natural-language adapter connects project narratives with read-only review. General usability and real-project multi-worker efficiency remain unverified. See [Security and Support](docs/SECURITY-AND-SUPPORT.md) for the limits of the available evidence.

An installed project starts human review with `./hv2 view` and machine diagnostics with `./hv2 status`. A fresh project must first be initialized from an independent trusted source with the explicit `checkout-1` development profile. See [Getting Started](docs/GETTING-STARTED.md).

The runtime version gate accepts final, GIL-enabled CPython 3.14.6 or 3.14.7, with no third-party runtime dependencies. This gate does not qualify an operating system or distributor build; see the evidence limits in [Security and Support](docs/SECURITY-AND-SUPPORT.md). Primary Git checkouts and standalone non-Git projects can host control authority. Linked worktrees cannot mutate it. Local container tests are not native-platform or real-adopter acceptance.

## Read Next

- [Documentation Index](docs/README.md): current procedures and technical contracts.
- [Concepts](docs/CONCEPTS.md): who owns intent, work, product bytes, and acceptance.
- [Reference](docs/REFERENCE.md): installed and source command surfaces.
- [Operations](docs/OPERATIONS.md): update, rollback, repair, and detach.
- [Security and Support](docs/SECURITY-AND-SUPPORT.md): trust and unresolved support limits.

Generation 1/2 commands, readers, and migration are not supported. Use fresh targets. Historical contracts and receipts are retained for audit, not as current operating instructions. Public version, release distribution, and production support are unassigned.

Later patches, prereleases and free-threaded builds are rejected. Other OS or distributor builds matching the accepted version conditions may execute; that is not a claim that they have been qualified. See [Security and Support](docs/SECURITY-AND-SUPPORT.md).

For ideas that are not ready to become Work, ask the agent to record, compare, select or defer a candidate. `./hv2 view candidates` shows this branch’s stored choice, reasons and links to actual Work state. A candidate selection does not accept an intent or authorize execution. See [Candidate Planning](docs/REFERENCE.md#candidate-planning).
