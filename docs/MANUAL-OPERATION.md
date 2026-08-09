# Manual Operation

The operator runs the core CLI directly. No agent/provider adapter or provider transcript is required or accepted as evidence.

For `resume` and the binding receipt emitted by it, `observed_at` inherits the sealed attempt observation. It is not the
record write time and does not claim wall-clock monotonicity. Generation 1 never uses timestamps to select authority.

Required environment:

- CPython `3.14.6`
- `PYTHONPATH=src`
- Git for the disposable target finalization boundary

The bounded sequence is:

1. Build and verify one sealed carrier.
2. Initialize one fresh disposable Git target and one authority home.
3. Apply create and observe binding-complete/Git-unfinalized.
4. Commit the disposable target.
5. Inject an in-process update abort after pointer assertion; verify the prior active selector directly and the persisted
   interruption record.
6. Resume, then commit.
7. Forward rollback to revision 1, then commit.
8. Detach logically, verify plain continuation and zero-pack/provider-null, then commit.
9. Seal `EXPECTED.json` before blind execution and use the implementation to inventory live ignored staging into
   `STAGING-AUDIT.json`; the sealed input is Git-independent, not implementation-independent.
10. Hand only the accepted contract, blind-execution-presealed expected/staging inputs and persisted target bytes to the blind auditor. Remove
    the capsule clone remote before audit.

The run receipt must contain every literal command, cwd role, exit code, runtime/tool inventory and input digest. A narrative
summary without those commands is not manual-operation evidence.
