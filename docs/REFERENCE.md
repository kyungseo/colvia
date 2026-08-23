# Reference

Document authority and currentness: [Documentation Index](README.md).

## Product Commands

| Command | Default | Mutation |
| --- | --- | --- |
| `hv2 init --target PATH [--source PATH]` | preview | `--apply` creates binding and authority homes |
| `hv2 status [--target PATH]` | read-only | none |
| `hv2 doctor [--target PATH]` | read-only | none |
| `hv2 update --source PATH [--target PATH]` | preview | `--apply` stages and switches release |
| `hv2 rollback [--to RELEASE] [--target PATH]` | preview | `--apply` switches release |
| `hv2 detach [--target PATH]` | preview | `--apply` removes only product-managed binding bytes |

The source entry is `./hv2`. An installed project also uses `./hv2`. Low-level commands remain available through the same launcher.
Here, `--source` means a contribution source checkout. An installed immutable release is runtime material, not a source for
initializing or updating another project; that attempt fails before target mutation with `HV2-PRODUCT-INSTALLED-SOURCE`.

## Low-Level Command Groups

- Carrier and Generation 1: `build-release`, `verify-release`, `init-target`, `transition`, `resume`, `verify-state`.
- Generation 2: `activate-parallel`, `register-item`, `claim-work`, `reassign-claim`, `finalize-work`, `verify-repository`.
- Guided Intent: `classify-intent-entry`, `init-intent-home`, `create-intent-draft`, `show-intent`, `accept-intent`, `verify-intent`.
- Durability: `durability-probe`.

Use `./hv2 <command> --help` for exact arguments. Technical semantics remain in the Generation 1, Generation 2, Guided Intent, and
manual-operation contracts.

## State Roots

| Path | Ownership | Currentness |
| --- | --- | --- |
| `.harness-v2-product/active-release.json` | product-managed binding | exact release and receipt references |
| `.harness-v2-product/releases/<release-id>/` | immutable product release | directory ID derives from canonical inventory |
| `.harness-v2-product/receipts/` | immutable product operations | selected active receipt is digest-bound |
| `.harness-v2/` | project-owned item state | generation and active pointer selectors |
| `.harness-v2-intents/` | project-owned intent history | exact current selection reference |
| `.harness-v2-detached.json` | project-owned plain exit receipt | present only after detach begins |

## Exit Codes

| Code | Meaning |
| ---: | --- |
| `0` | pass, preview, no-change, or completed detach (`classification: detached`) |
| `10` | degraded |
| `11` | incompatible |
| `12` | conflict |
| `13` | stale |
| `14` | partial |
| `15` | uninitialized |
| `16` | unsupported local tuple |
| `65` | contract or usage failure returned by the product layer |
| `70` | unexpected internal error; exception type only |
| `75` | intentional bounded interruption fixture |

Stable error codes identify the violated contract. Error output must not contain secret values or raw internal exception messages.

## Product Error Codes

The product stops rather than guessing. Find the code in the first column, correct the named boundary, and rerun the preview or
read-only diagnostic before applying a mutation.

| Codes | Meaning | Safe next action |
| --- | --- | --- |
| `HV2-PRODUCT-LAUNCHER-ACTIVE`, `HV2-PRODUCT-LAUNCHER-RELEASE`, `HV2-PRODUCT-LAUNCHER-SOURCE` | The installed launcher cannot resolve its active selector, release, or entry module. | Use the exact active selector to restore `./hv2`; do not select a release by recency. See [Operations](OPERATIONS.md). |
| `HV2-PRODUCT-TARGET`, `HV2-PRODUCT-GIT-ROOT`, `HV2-PRODUCT-ROOT`, `HV2-PRODUCT-DIRECTORY` | The requested target or managed root is absent, outside the Git worktree, or has the wrong type. | Confirm the exact target path and Git root. Do not create or move authority homes by hand. |
| `HV2-PRODUCT-SOURCE`, `HV2-PRODUCT-SOURCE-TARGET`, `HV2-PRODUCT-SOURCE-DIRECTORY`, `HV2-PRODUCT-SOURCE-FILE` | The contribution source is missing, overlaps the target, or does not match its inventory. | Use a clean contribution checkout and rerun preview. |
| `HV2-PRODUCT-INSTALLED-SOURCE` | An installed immutable release was supplied as a contribution source. | Use the matching contribution source checkout; do not copy or mutate the installed release. |
| `HV2-PRODUCT-INVENTORY`, `HV2-PRODUCT-INVENTORY-DIGEST`, `HV2-PRODUCT-INVENTORY-ENTRY`, `HV2-PRODUCT-INVENTORY-ORDER`, `HV2-PRODUCT-INVENTORY-PATH`, `HV2-PRODUCT-INVENTORY-SIZE` | The canonical inventory is missing, malformed, unordered, unsafe, or inconsistent. | Stop and rebuild the candidate from a clean contribution checkout. |
| `HV2-PRODUCT-RELEASE-ID`, `HV2-PRODUCT-RELEASE-REF`, `HV2-PRODUCT-RELEASE-PATH`, `HV2-PRODUCT-RELEASE-FILE`, `HV2-PRODUCT-RELEASE-DIGEST`, `HV2-PRODUCT-RELEASE-COVERAGE`, `HV2-PRODUCT-RELEASE-TREE`, `HV2-PRODUCT-RELEASE-SYMLINK`, `HV2-PRODUCT-RELEASE-CONTRADICTION`, `HV2-PRODUCT-IMMUTABLE-CONTRADICTION` | An immutable release identity, file, digest, coverage, tree, or selector contradicts its receipt. | Preserve evidence, stop using the release, and install a verified candidate. Do not repair immutable bytes in place. |
| `HV2-PRODUCT-ACTIVE`, `HV2-PRODUCT-STATE-BINDING`, `HV2-PRODUCT-INTENT-BINDING`, `HV2-PRODUCT-ATTACH-REQUIRED`, `HV2-PRODUCT-ALREADY-INITIALIZED` | Active product binding, project-owned state binding, or lifecycle state is absent or incompatible with the requested operation. | Run `status` and `doctor`. D1 has no attach flow: initialize only when no authority home exists; otherwise handle the existing home under project policy. |
| `HV2-PRODUCT-INIT-PLAN`, `HV2-PRODUCT-COLLISION`, `HV2-PRODUCT-LAUNCHER-CHANGE`, `HV2-PRODUCT-LAUNCHER-DRIFT`, `HV2-PRODUCT-LAUNCHER-MISSING`, `HV2-PRODUCT-LAUNCHER-MODE`, `HV2-PRODUCT-STAGING` | The preview plan, target collision, launcher, or staging area is unsafe or differs from recorded product bytes. | Inspect the preview and diagnostics. Preserve project-owned collisions; restore only exact product-managed bytes. |
| `HV2-PRODUCT-RECEIPT`, `HV2-PRODUCT-RECEIPT-REF`, `HV2-PRODUCT-RECEIPT-CONTRADICTION` | A lifecycle receipt is missing, misreferenced, or contradicts the selected state. | Preserve the receipt set and stop mutation until the exact referenced receipt is recovered. |
| `HV2-PRODUCT-DETACH-RECEIPT`, `HV2-PRODUCT-DETACH-STAGING`, `HV2-PRODUCT-DETACH-TREE`, `HV2-PRODUCT-ROOT-TREE` | Detach cannot prove its receipt, staging, or product-managed removal boundary. | Rerun detach to resume its bounded recovery; do not delete project-owned authority homes. |
| `HV2-PRODUCT-NO-ROLLBACK`, `HV2-PRODUCT-ROLLBACK-ID` | No prior release is available, or the requested rollback release is invalid. | List the receipt-backed release history and choose an exact valid release ID. |
| `HV2-PRODUCT-CAPABILITIES` | The product capability declaration is absent or inconsistent. | Verify the candidate source and capability manifest before install or update. |
