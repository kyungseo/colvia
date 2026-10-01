# Operations

Use [Reference](REFERENCE.md) for command options and [Workspace Contract](WORKSPACE-CONTRACT.md) for exact lifecycle rules. Installed commands use the bound product. Independent source commands require `--source-checkout`; init/update/rollback/detach additionally require `--profile umbrella-1`.

## Observe Before Acting

`hv2 view`, `hv2 status` and `hv2 doctor` are read-only. They validate product and typed record graphs, classify pending or unsupported state, and expose verified documentation when available. They do not attest a later unsubmitted edit or grant write authority. If the launcher fails, use an independent trusted source's view/status/doctor with `--target PATH`.

## Update And Rollback

`hv2 update --source PATH --operation-id ID --observed-at TIME` previews a new release. `hv2 rollback [--to RELEASE] --operation-id ID --observed-at TIME` previews a receipt-backed prior release. Save the exact preview `request` outside the target and apply it with `--apply --input FILE --confirm TOKEN`. Pending Work/intent publication blocks a new switch.

For an older-window transition, use the qualified independent umbrella-1 source and explicit profile. See [Transition To Umbrella-1](GETTING-STARTED.md#transition-to-umbrella-1). After the first durable umbrella-1 receipt, only exact forward recovery and same-window rollback are supported. Use retained old sources for old-window repair; never package new code with an old installed launcher.

A switch preserves project truth and results but changes the product binding and may replace the launcher. Existing confirmation tickets become stale. Re-prepare them against the new binding. Release digest verification does not establish arbitrary candidate compatibility; qualify the new release before use.

## Interrupted Operations

Preserve original input, token, source, and observed bytes. Supported complete-file prefixes can resume from independent source using the same operation, target, profile, `--apply --recover --input FILE --confirm TOKEN`. Do not invent a replacement request or delete a receipt to clear a pending operation. Torn bytes, unknown members, wrong file kinds, and missing prerequisites require preservation and investigation.

For pending intent/Work records, restore the exact prerequisites and replay the original publish request or accepted ticket. The limited Work cancellation contract is described in [General Work](GENERAL-WORK.md); there is no generic reset command.

## Broken Launcher Or Payload

Use independent exact source `repair` with `--target PATH --source PATH --backup NEW_EXTERNAL_PATH --operation-id ID --observed-at TIME`. Review its preview, then apply the exact request/token. Source must match the active release; the backup must be new and outside source and target, on durable storage. Original bytes are retained before replacement. Repair does not recreate missing metadata or directories, change authority, or upgrade the product. Interrupted repair uses the same request plus `--recover`.

## Detach

`hv2 detach --operation-id ID --observed-at TIME` previews removal. Apply its exact request/token only after reviewing the removal list. The durable `.hrn/detached.json` receipt is written first; verified product files and launcher are removed individually. Format, intent, Work, results, authored documents, and ignored scratch remain. Unknown or changed bytes block removal rather than being recursively deleted.

If the launcher has already been removed, use independent-source detach with the explicit profile and exact request/token plus `--recover`. Preserve useful product manuals before detach. Read retained history as described in [Manual Operation](MANUAL-OPERATION.md). Reinitializing or attaching a detached authority is not supported by this candidate.
