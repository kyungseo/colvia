# Operations

Product lifecycle commands separate contribution source, immutable release bytes, and the project’s active binding. Mutating commands
preview by default and require `--apply`.

Document authority and currentness: [Documentation Index](README.md).

## Initialize

Run initialization from a trusted contribution source checkout containing `hv2`, `src/hv2ref/`, and the repository docs. An
installed immutable release is not a contribution source and fails with `HV2-PRODUCT-INSTALLED-SOURCE` before target mutation.

```sh
./hv2 init --target /path/to/project
./hv2 init --target /path/to/project --apply
```

The source tree is inventoried by exact path, byte length, and SHA-256. The release ID has the form
`product-release-<24-hex>` and is derived from the canonical inventory; the complete inventory SHA-256 remains 64 hexadecimal
characters.
Initialization stages and verifies that release, creates separate state and intent authority homes, writes the launcher, and switches
the active release last. Repeating the exact command is idempotent.

## Status And Doctor

From the initialized project:

```sh
./hv2 status
./hv2 doctor
```

`status` checks the active release, operation receipt, launcher, project state, intent authority, and active release capability
declaration. `doctor` runs that same status check and adds the local Git and CPython tuple. Neither command reads arbitrary project
content or mutates project bytes.

| Classification | Meaning | Next action |
| --- | --- | --- |
| `pass` | exact binding verified; `doctor` also verifies the required local tuple | continue |
| `uninitialized` | no product binding | preview `init` |
| `partial` | an initialization stage exists without an active switch | repeat the exact `init --apply` from source |
| `degraded` | known schema but a digest/tree/binding contradiction exists | stop mutation; inspect the stable error code |
| `incompatible` | schema generation cannot be interpreted safely | use a compatible release or manual path |
| `unsupported` | runtime/tool tuple is not certified | use the documented tuple or manual fallback |
| `detached` | product-managed bytes are gone; project truth remains | continue manually or explicitly initialize a new binding |

## Update

Point the installed project at another trusted source checkout:

```sh
./hv2 update --source /path/to/new/source
./hv2 update --source /path/to/new/source --apply
```

Preview lists changed managed paths and performs no target mutation. Apply creates and verifies a new immutable release, writes an
operation receipt, then switches the active selector. Project-owned state and intent are not included in the managed inventory.

D1 keeps the root launcher byte-stable across releases. A launcher change fails with `HV2-PRODUCT-LAUNCHER-CHANGE` and needs a
separate migration gate. A changed or unexpected managed byte also fails before switch; it is never overwritten as accepted drift.

## Roll Back

Preview the prior release, then apply:

```sh
./hv2 rollback
./hv2 rollback --apply
```

Use `--to product-release-<digest>` only for an exact release already present in the binding. Rollback is a forward operation that
changes the active selector and preserves both releases and its receipt.

## Recover From Interruption

- Before the active selector switches, the prior release remains current.
- An exact retry reuses immutable release and receipt bytes.
- A contradictory retry fails; it does not repair by recency.
- `partial` initialization is resumed from the contribution source because the target launcher may not yet be active.
- Unexpected files under `.harness-v2-product/` block detach rather than being deleted.

If only the root `hv2` launcher drifted, read the exact active release ID from `.harness-v2-product/active-release.json`. Confirm
that the named directory is the intended retained release, then restore its launcher bytes and executable mode:

```sh
cp .harness-v2-product/releases/product-release-<24-hex>/hv2 ./hv2
chmod 755 ./hv2
./hv2 status
```

Do not select a release by recency. If the retained release itself fails verification, stop and recover from a trusted contribution
source or retained release archive; this D1 candidate has no automatic repair command.

## Detach

Preview what will be removed and preserved:

```sh
./hv2 detach
./hv2 detach --apply
```

Detach writes `.harness-v2-detached.json`, verifies the complete managed tree, then removes only `hv2` and
`.harness-v2-product/`. It preserves `.harness-v2/` and `.harness-v2-intents/`. If the launcher disappears during an interrupted
detach, repeat the command from a trusted source checkout with `--target /path/to/project`.

Detach also removes the release-local documentation. Before applying detach, preserve `README.md`, `AGENTS.md`,
`docs/GETTING-STARTED.md`, `docs/OPERATIONS.md`, and `docs/MANUAL-OPERATION.md` outside product-managed paths if offline guidance
is required. The plain receipt records the exact documentation release reference and required relative paths, but retrieval after
detach is `not-guaranteed`.

Continue from project-owned JSON using [Manual Operation](MANUAL-OPERATION.md). Back up the project under its own policy before any
broader deletion.
