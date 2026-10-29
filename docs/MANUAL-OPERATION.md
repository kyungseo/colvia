# Manual Operation

Continuation-1 profile; see [authorization and qualification](README.md#continuation-1).

You can read the retained project records without a running product or agent provider. Preserve authority records while inspecting them; read access does not authorize rewriting them.

## Retained Evidence

Preserve `.hrn/format.json`, intent and Work records, referenced project documents, and `.hrn/detached.json` when present. Follow exact typed references and validate their digests; never choose the newest file. Do not hand-edit current pointers or recompute hashes to make damaged history appear valid.

An independent trusted source can run `--source-checkout status --target PATH` or `doctor` after detach to validate complete intent/Work graphs. For a product-free byte audit, obtain `tests/fixtures/product_plain_auditor.py` from a trusted source and run:

```sh
python3 -I -B product_plain_auditor.py /path/to/project
```

This stdlib-only fixture reads paired detach schemas1/2/3/4/5 and checks receipt inventory, deletion prefix and selected references. Schemas3/4 use the historical colvia membership; schema5 additionally admits the literal 30-file continuation set while retained releases keep their literal old inventories; membership alone does not identify which old inventory window produced a completed detach. A scoped retired-entry collision with otherwise-valid schema3/4/5 evidence is preserved as degraded/10 by independent-source diagnostics, distinguished by the product error/message; it is not cleanly detached and does not invent an active binding. Further removal or exact completed replay refuses 65. Once the launcher is removed, installed observation is unavailable. Historical schema1/2/3/4 mutation/recovery requires its matching retained source; current schema5 recovery requires the exact continuation-1 source. It does not implement the full Work state machine or authorize mutation. A read-only clone audit is distinct from recovery, which remains bound to the original target fingerprint.

For windows-2, read original modes and canonical records without translating them from current host permissions. While the product is present, verify policy through the binding/release/inventory chain. After complete product removal, only a paired detach6 receipt validated under Workspace's Windows Fresh And Same-Window Lifecycle (complete remove/preserve path/digest/size lists, internal links, actual absence/prefix and preserved bytes) identifies windows-2 policy; the removed inventory's digest cannot reconstruct its contents. The receipt embeds the complete canonical plan. Read-only validation uses that plan and actual preserved/remnant state without requiring a separate external original-plan file/token; mutation recovery retains the original exact request/token and target requirement. Historical detach1/2/3 retain their original meanings, and unavailable policy provenance remains unknown rather than guessed. Reading retained evidence grants no new mutation, attachment or reinitialization. Use a compatible qualified reader to validate the receipt, preserved truth and admitted removal prefix. This contract cannot change older audit code: a reader that does not understand detach6 supplies no detach6 validation evidence, even if it prints PASS. If that output is required for qualification, the proof remains non-pass until compatible evidence is available; it is not an old-writer publication event.

## Recovery Boundary

Keep original requests, tokens, backups and candidate source on durable storage while their exact operation, replay or recovery depends on them. A completed repair still has contract-bound original bytes; do not treat its backup as disposable. Use [Records And Retention](REFERENCE.md#records-and-retention) to distinguish caller-side duplicates and temporary checks from authority and required recovery material; a healthy view or empty pending list alone is not permission to remove them. Use only the supported exact recovery paths in [Operations](OPERATIONS.md). If required bytes are unavailable, record that limitation and preserve the target for human disposition. There is no general manual rewrite procedure, Gen1/2 compatibility reader, or automatic attach operation.

## Retained Candidate Planning

After detach, keep `.hrn/planning/candidates.json` with the format, intent and Work records. The detach receipt binds its preserved digest and size. The independent stdlib product auditor checks those bytes and receipt inventory; it does not reimplement candidate transitions or authenticate Owner declarations. Use an independent trusted continuation-1 source for `--source-checkout view candidates --target PATH`. Preserve damaged/conflicted planning and follow the explicit branch recovery in [Candidate Planning](REFERENCE.md#candidate-planning); do not delete it to make another command succeed.

## Delegation-1 Implementation Candidate

Continuation-1 inherits the delegation-1 behavior described below. Follow [Continuation-1](README.md#continuation-1) for current lifecycle commands and authorization requirements. Historical versions retain their original meaning. Human authorization comes from the Owner’s actual decision; host authentication and general readiness require their own evidence.

A schema-3 ordinary intent draft contains a non-null exact acceptance grant. Retained records alone do not authenticate its Owner or delegate. A plain audit may check hashes and selected references and display the grant, but it must explicitly report delegation authorization as unverified unless it implements the full Work/intent historical constraints, one-use key and selected-revoke rule. Do not downgrade unknown schema-3 content to an ordinary no-grant record.

Core readers perform the full checks with the verified accepted-intent context. The supplied plain intent auditor reports `delegation_authorization: not-verified`; the product auditor reports `full_record_semantics: not-reimplemented`. These tools check their declared subsets. Lifecycle pairing alone leaves host enforcement and the pre-detach inventory window unverified. Preserve unknown or damaged records and original recovery inputs. Manual editing, deletion or token substitution is not a supported recovery path.

## Retained Continuation

Detach preserves each continuation choice, selection and current. The independent stdlib product auditor checks their retained bytes and selected references and reports `verification: selected-refs-only`; it does not reimplement the complete continuation graph, freshness or authorization. Use a trusted independent continuation-1 source for full read-only view. Null current with no choices is undecided; unknown/missing current with durable choices must be preserved as invalid, never replaced from a filename guess. A copied/clone audit does not authorize pending recovery at a different fingerprint.
