# Manual Operation

Project truth remains readable without a running product or agent provider. Reading bytes is not permission to rewrite authority.

## Retained Evidence

Preserve `.hrn/format.json`, intent and Work records, referenced project documents, and `.hrn/detached.json` when present. Follow exact typed references and validate their digests; never choose the newest file. Do not hand-edit current pointers or recompute hashes to make damaged history appear valid.

An independent trusted source can run `--source-checkout status --target PATH` or `doctor` after detach to validate complete intent/Work graphs. For a product-free byte audit, obtain `tests/fixtures/product_plain_auditor.py` from a trusted source and run:

```sh
python3 -I -B product_plain_auditor.py /path/to/project
```

This stdlib-only fixture checks receipt inventory, deletion prefix, and selected references. It does not implement the full Work state machine or authorize mutation. A read-only clone audit is distinct from recovery, which remains bound to the original target fingerprint.

## Recovery Boundary

Keep original requests, tokens, backups and candidate source on durable storage while their exact operation, replay or recovery depends on them. A completed repair still has contract-bound original bytes; do not treat its backup as disposable. Use [Records And Retention](REFERENCE.md#records-and-retention) to distinguish caller-side duplicates and temporary checks from authority and required recovery material; a healthy view or empty pending list alone is not permission to remove them. Use only the supported exact recovery paths in [Operations](OPERATIONS.md). If required bytes are unavailable, record that limitation and preserve the target for human disposition. There is no general manual rewrite procedure, Gen1/2 compatibility reader, or automatic attach operation.

## Retained Candidate Planning

After detach, keep `.hrn/planning/candidates.json` with the format, intent and Work records. The detach receipt binds its preserved digest and size. The independent stdlib product auditor checks those bytes and receipt inventory; it does not reimplement candidate transitions or authenticate Owner declarations. Use an independent trusted checkout-1 source for `--source-checkout view candidates --target PATH`. Preserve damaged/conflicted planning and follow the explicit branch recovery in [Candidate Planning](REFERENCE.md#candidate-planning); do not delete it to make another command succeed.
