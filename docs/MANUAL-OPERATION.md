# Manual Operation

The operator runs the core CLI directly. No agent/provider adapter or provider transcript is required or accepted as evidence.

Document authority and currentness: [Documentation Index](README.md).

## Product Lifecycle Entry

The D1 project-local entry is `./hv2`. From a trusted contribution checkout, `init` inventories an exact source-derived release and
binds it to one fresh Git project. In the project, `status` and `doctor` are read-only; `update`, `rollback`, and `detach` preview by
default and mutate only with `--apply`. See `OPERATIONS.md` for commands and recovery.

The product lifecycle does not replace the Generation 1 item transition below. Product update changes managed release bytes;
Generation 1 `transition --operation update` changes one project-owned item revision. The two authorities must not be conflated.

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

## Generation 2 Parallel Safety

Generation 2 does not allocate worktrees or branches. The caller creates them and supplies a logical repository ID, worktree ID,
branch, exact base commit/tree and repository-relative write scope. The bounded manual sequence is:

1. Verify Generation 1 and activate Generation 2 from a clean integration worktree at the exact Git base.
2. Register each additional item add-only.
3. Create claims from caller-provided clean worktrees at the same exact base.
4. Treat same-item, normalized path/prefix, stale-base and control-metadata collisions as visible conflict evidence.
5. Perform work and Git commits outside the harness, integrate them through the declared finalizer, then call `finalize-work` with
   the exact integrated result commit/tree.
6. Verify the repository. Shared current state changes only after the integration-epoch marker and final revalidation.

The same actor may run the whole sequence as the one-agent fallback. Actor/finalizer strings are declarations inside a trusted
local OS-account/operator boundary; they are not credentials. A claim or finalize attempt never expires by wall clock. Recovery is
an exact same-finalizer resume or an explicit reassignment/successor epoch.
