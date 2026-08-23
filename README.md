# Harness v2 — Private Public Core Candidate

Harness v2 keeps a project’s accepted intent, current state, evidence, and recovery path readable when people and agents work
over time. The human owner still decides scope, acceptance, and finalization. Agents and runtime adapters are removable helpers.

This D1 candidate is intentionally small:

- no required server, daemon, database, registry, or network connection;
- no third-party Python package;
- project-owned state stays as plain files in the project;
- one trusted local operator can use it without an agent provider;
- same-repository parallel work has explicit scope, stale-base, conflict, and finalizer checks.

It requires Git and CPython `3.14.6`. It is not a public release and does not claim other runtime versions, real-adopter success,
untrusted multi-user authorization, or enterprise multi-project operation.

## Start With A Preview

From the contribution source checkout, preview the release and target without changing project bytes:

```sh
./hv2 init --target /path/to/project
```

Review the target and release reference (ID and SHA-256), then apply that candidate and check the installed project:

```sh
./hv2 init --target /path/to/project --apply
cd /path/to/project
./hv2 status
./hv2 doctor
```

The contribution source is the trusted checkout containing `hv2`, `src/hv2ref/`, and this documentation. An installed immutable
release cannot initialize another project. Existing collisions and managed-file drift fail before the active release switches.

## What Lives Where

```text
.harness-v2-product/   product-managed release and binding; removable
.harness-v2/           project-owned item state and evidence
.harness-v2-intents/   project-owned accepted-intent history
hv2                    small project-local launcher; removable
```

Removing the product binding does not delete project-owned state or intent history. Paths and timestamps do not decide what is
current; exact selectors and digest-bound references do.

## Next Read

- [Getting Started](docs/GETTING-STARTED.md) — initialize a project and record the first accepted intent.
- [Concepts](docs/CONCEPTS.md) — understand authority, state, identity, and collaboration.
- [Operations](docs/OPERATIONS.md) — update, recover, roll back, diagnose, and detach.
- [Security And Support](docs/SECURITY-AND-SUPPORT.md) — see the trusted-local and runtime boundary.
- [Reference](docs/REFERENCE.md) — find commands, state roots, classifications, and exit codes.
- [Maintaining](docs/MAINTAINING.md) — validate and change the product source.
- [Documentation Index](docs/README.md) — check document authority and currentness.

The deeper Generation 1, Generation 2, Guided Intent, and manual-operation contracts remain available under `docs/`. They are
technical reference, not the shortest onboarding path.
