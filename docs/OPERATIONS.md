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

## Track A Durable D2-A Binding

For an adopter repository that requires the same binding to survive a fresh clone or Git worktree, track the root `hv2` launcher,
project-owned `.harness-v2/` and `.harness-v2-intents/` truth, and every durable binding entry:

- `.harness-v2-product/active-release.json`
- `.harness-v2-product/init-plan.json`
- `.harness-v2-product/receipts/`
- `.harness-v2-product/releases/`, including both exact update and rollback releases required by the adopter acceptance plan

Ignore only the runtime scratch path by adding this exact target-root rule:

```gitignore
.harness-v2-product/staging/
```

Do not ignore `.harness-v2-product/` as a whole. Before committing the binding, run `status`, verify the managed release payload under
the repository's disclosure policy, and confirm that the root launcher is a regular executable file whose bytes equal the launcher in
the active release. Then create both a fresh clone and a `git worktree add` checkout from the committed binding. In each checkout, run
`./hv2 status` before any mutating command. Success is `classification: pass`; the absent ignored staging directory is expected and the
next init or update recreates it. A missing durable entry, private payload hit, launcher mismatch, or non-`pass` first status blocks
adopter acceptance.

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
| `partial` | an initialization stage lacks an active switch, an exact sealed item interruption can resume, or an exact detach receipt exists beside a remaining managed root | run only the exact reported `init --apply`, `resume --target <project> ...`, or `detach --target <project> --apply` action; do not run another mutator |
| `degraded` | known schema but a digest/tree/binding contradiction exists | stop mutation; inspect the stable error code |
| `incompatible` | schema generation cannot be interpreted safely | use a compatible release or manual path |
| `unsupported` | runtime/tool tuple is not certified | use the documented tuple or manual fallback |
| `detached` | product-managed bytes are gone; project truth remains | continue manually; D1-A detach is terminal |

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

An installed `./hv2 update` transaction is governed by the currently active release. After a successful switch, the next launcher
invocation is governed by the newly selected release. If the active release cannot admit the current binding, run the update from the
trusted new contribution source instead:

```sh
/path/to/new/source/hv2 update --target /path/to/project --source /path/to/new/source --apply
```

This source-mode bootstrap does not add a new command or infer a release by recency. It uses the candidate code to verify and commit
the same receipt-backed update contract.

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
- A sealed Generation 1 interruption after pointer assertion or selector switch makes product `status` return `partial` with
  `HV2-PRODUCT-STATE-INTERRUPTED` and the exact item `resume --target <project> ...` action. Substitute the initialized project path
  for `<project>` and run only that action before product update or rollback.
- If the item staging inventory or any sealed staged byte is absent, linked, damaged, or mismatched, status does not advertise the
  interruption as resumable. Preserve the checkout and use the checkout that still holds the original sealed staging evidence. Do
  not recreate staging or copy it from an unverified source.
- `HV2-RESUME-EVIDENCE` means required sealed evidence became unavailable after admission; `HV2-NONWRITABLE` means current state is
  not the exact admissible interruption. `HV2-RESUME-NOT-TIP` and `HV2-RESUME-ALREADY-CURRENT` are bounded pointer diagnostics. Stop
  on any of these codes and rerun read-only status; do not repair selectors or immutable records by hand.
- Unexpected files under `.harness-v2-product/` block detach rather than being deleted.

The `staging/` directory is runtime-only scratch. A fresh clone or worktree may omit an empty
`.harness-v2-product/staging/`; read-only status treats absence as empty. The next mutating init or update recreates it before writing.
A symlink, non-directory, or non-empty staging area still fails closed.

For `HV2-PRODUCT-STAGING`, or an `HV2-PRODUCT-IMMUTABLE-CONTRADICTION` whose reported path is below product staging:

1. Stop the mutation and establish that no product writer is active for that target.
2. Preserve the error output and inspect the exact reported child below `.harness-v2-product/staging/`.
3. Remove only that reported product-managed scratch child after confirming it is not a durable release, receipt, selector, or
   project-owned path.
4. Retry the exact source command; the mutator recreates missing scratch directories.

Do not delete the staging root blindly and do not remove an unreported child. If `.harness-v2-detached.json` differs from the expected
receipt, do not delete or replace it: stop and report the contradiction. Existing immutable release or receipt contradictions are
evidence and are never repaired in place.

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

If the exact detach receipt and live managed root coexist, `status` and `doctor` return `partial` with
`HV2-PRODUCT-DETACH-INCOMPLETE`; `init`, `update`, and `rollback` stop before their first write. Detach preview remains read-only and
the exact apply retry may finish even when a preserved authority home is unavailable or degraded. Retry proves only that the receipt
matches the active selector and init plan. Receipt statements that project-owned roots remain mean the product did not delete those
roots; they are not a health, integrity, or authority attestation. A malformed, linked, wrong-type, or differing receipt is not this
recovery state: preserve it and stop.

If removal was interrupted after the receipt was committed and `active-release.json` is already absent, the same exact detach retry
validates the regular canonical receipt and requires every remaining product-root entry to stay within the fixed managed-root
allowlist before completing removal. It also binds the receipt to both regular local authority homes and any surviving init plan or
named release. An unexpected entry or differing/linked authority home blocks mutation and is preserved. If root `hv2` exists in this
interrupted state, treat it as a user/external recreation regardless of byte equality: move it aside and repeat the exact retry; the
product will not delete it automatically. The receipt is lifecycle commitment, not permission to delete anything outside root `hv2`
and `.harness-v2-product/`.

Detach also removes the release-local documentation. Before applying detach, preserve `README.md`, `AGENTS.md`,
`docs/GETTING-STARTED.md`, `docs/OPERATIONS.md`, and `docs/MANUAL-OPERATION.md` outside product-managed paths if offline guidance
is required. The plain receipt records the exact documentation release reference and required relative paths, but retrieval after
detach is `not-guaranteed`.

Continue from project-owned JSON using [Manual Operation](MANUAL-OPERATION.md). Back up the project under its own policy before any
broader deletion. D1-A detach is terminal: neither status nor the receipt promises reinitialization or attachment of the retained
authority homes.

## Persisted Identity Vocabulary

New Generation 1 records use neutral project-local evidence, finalizer, and writer identifiers. Existing records with earlier logical
identity strings remain immutable history and can coexist with new records; this release does not rewrite them. These identifiers are
declarations inside a trusted local OS account boundary, not authentication.
