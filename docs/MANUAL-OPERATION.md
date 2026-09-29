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

Keep original requests, tokens, backups, and candidate source on durable storage. Use only the supported exact recovery paths in [Operations](OPERATIONS.md). If required bytes are unavailable, record that limitation and preserve the target for human disposition. There is no general manual rewrite procedure, Gen1/2 compatibility reader, or automatic attach operation.
