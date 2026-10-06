# Operations

Use [Reference](REFERENCE.md) for command options and [Workspace Contract](WORKSPACE-CONTRACT.md) for exact lifecycle rules. Installed commands use the bound product. Independent source commands require `--source-checkout`; init/update/rollback/detach additionally require `--profile checkout-1`.

## Observe Before Acting

`hv2 view`, `hv2 status` and `hv2 doctor` are read-only. They validate product and typed record graphs, classify pending or unsupported state, and expose verified documentation when available. They do not attest a later unsubmitted edit or grant write authority. If the launcher fails, use an independent trusted source's view/status/doctor with `--target PATH`.

## Update And Rollback

`hv2 update --source PATH --operation-id ID --observed-at TIME` previews a new release. `hv2 rollback [--to RELEASE] --operation-id ID --observed-at TIME` previews a receipt-backed prior release. Save the exact preview `request` outside the target and apply it with `--apply --input FILE --confirm TOKEN`. Pending Work/intent publication blocks a new switch.

For an older-window transition, use the qualified independent checkout-1 source and explicit profile. See [Transition To Checkout-1](GETTING-STARTED.md#transition-to-checkout-1). After the first durable checkout-1 receipt, only exact forward recovery and same-window rollback are supported. Use retained old sources for old-window repair; never package new code with an old installed launcher.

A switch preserves project truth and results but changes the product binding and may replace the launcher. Existing confirmation tickets become stale. Re-prepare them against the new binding. Release digest verification does not establish arbitrary candidate compatibility; qualify the new release before use.

## Interrupted Operations

Preserve original input, token, source, and observed bytes. Supported complete-file prefixes can resume from independent source using the same operation, target, profile, `--apply --recover --input FILE --confirm TOKEN`. Do not invent a replacement request or delete a receipt to clear a pending operation. Torn bytes, unknown members, wrong file kinds, and missing prerequisites require preservation and investigation.

For pending intent/Work records, preserve the exact prerequisites and original publish request or accepted ticket. A pending worker acceptance can resume with the original `work apply --input FILE --confirm TOKEN`; product lifecycle `--recover` is not a Work option. After the decision is durable, retained control Git objects can supply the remaining pre-images even when the worker folder is unavailable. A mixed pre/post result is not eligible for cancellation. Recover only within the authorized action and verified prerequisites; do not prepare a replacement acceptance merely to finish the same pending decision. See [General Work](GENERAL-WORK.md#worker-publication-development-checkpoint) for the full recovery and cancellation contract.

Git integration failure after completed acceptance is a separate condition. Preserve the accepted history and candidate, report integration as incomplete, and use the project's authorized Git recovery path. Completed decision replay does not restore project content. See [Git Integration And Candidate Reuse](GENERAL-WORK.md#git-integration-and-candidate-reuse) before changing the baseline or submitting a changed result.

## Broken Launcher Or Payload

Use independent exact source `repair` with `--target PATH --source PATH --backup NEW_EXTERNAL_PATH --operation-id ID --observed-at TIME`. Review its preview, then apply the exact request/token. Source must match the active release; the backup must be new and outside source and target, on durable storage. Original bytes are retained before replacement. Repair does not recreate missing metadata or directories, change authority, or upgrade the product. Interrupted repair uses the same request plus `--recover`.

## Detach

Before preparing the detach request, resolve pending Work, intent and lifecycle operations through supported paths. Decide how unfinished Work and results awaiting a decision will be handled before approval; not every unfinished Work state blocks detach. Identify the affected project-entry pointers, local rules, tool-specific instructions and hooks that invoke Harness, and propose their exact edits and the supported future operating method. Complete authorized pre-detach edits under [Check Before Writing](REFERENCE.md#check-before-writing) before preview; keep `./hv2 view` pointers until verified completion. Secure compatible independent source and useful manuals outside the target, then preserve the prepared request/token there before applying it. Defer further project edits until the operation resolves: publishing their Work records can change the bound truth. Project-instruction edits and exact detach require their respective authorization.

`hv2 detach --operation-id ID --observed-at TIME` previews removal. Apply its exact request/token only after reviewing the removal list. The durable `.hrn/detached.json` receipt is written first; verified product files and launcher are removed individually. Format, candidate planning, intent, Work, results, authored documents, and ignored scratch remain. Unknown or changed bytes block removal rather than being recursively deleted.

If the launcher has already been removed, use independent-source detach with the explicit profile and exact request/token plus `--recover`. Preserve useful product manuals before detach. Read retained history as described in [Manual Operation](MANUAL-OPERATION.md). Reinitializing or attaching a detached authority is not supported by this candidate.

After verified completed detach, finish the authorized project-entry edits: remove or replace obsolete `./hv2 view` and managed-adapter instructions, retain useful local requirements and required historical/reference bytes, and verify the new entry and a fresh session when available. If a referenced instruction must remain fixed, preserve it and propose a separate current instruction. Runtime removal does not perform this project edit, remove global agent rules or authorize deleting a tool directory. Report remaining edits or unavailable session checks separately from completed detach. See [Repository-Owned Rules](REFERENCE.md#repository-owned-rules).
