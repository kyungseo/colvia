# Colvia Entry Verification Controls

Status: P1a bounded correction/review/synthetic-validation batch is Owner authorized (2026-10-10). Candidate 02 adds actual before hooks and root-fsync selection. Its runtime results remain pending; final control freeze, result acceptance, P1b and M3 remain separate.

## Historical P0 Bundle Authorization — 2026-10-09

The following dated paragraphs preserve P0 authorization history. The r01 bounded result was subsequently accepted; those run/review allowances do not transfer to this changed P1a candidate. See the current status and P1a section for the present gate.

The Owner approved preparation, necessary same-subscription Claude review, Driver dispositions, in-scope corrections and actual base verification as one bounded bundle, recorded in [CHORE-20261009-002](../../CHORE-20261009-002-colvia-verification-controls.md). Within that named bundle, earlier preparation-only and separate-per-step execution/retry statements below retain their historical meaning and are replaced by this explicit execution scope. They do not require another Owner approval at each technical gate.

The bundle permits one initial attempt plus at most three corrected attempts in four preidentified absent execution roots with the same depth, layout, policies, selection and controller budgets. Preserve every failed root/slot and required exact inputs; never reset, delete, overwrite or reuse a consumed slot. After an execution-affecting correction, freeze/review the new inputs and repeat the base sequence in the next named root; do not mix candidate evidence. Stop after three failed corrections for the same cause, total attempt/review exhaustion, a scope/security/cost change, unexplained drift, unavailable preservation or surviving processes. Verified canonical binding permits deterministic substitution of only the smoke input digest and continuation inside the approved attempt. Intermediate technical review is not Owner result acceptance.

Apart from the exact dated acquisition permission exception below, SBPL permissions, product behavior, baseline/oracle/seed selection, test assertions/discovery/timeouts, real-project application and source Git actions remain outside correction scope. Final Owner acceptance, Work Done/STATUS and publication remain separate. The existing synthetic-fixture Git operations are permitted only as part of the bounded tests. This is base qualification, not whole/future-mode or product-transition acceptance.

The Owner approved a narrower correction continuation on 2026-10-10 after both a minimal Python payload and a system no-op failed with PID-matched `file-read-data /` denials under acquire.sb. Only acquire.sb gains `(allow file-read-data (literal "/"))`, with the corresponding comment, this explanation and dependent private input hashes updated; test.sb and all six Python controls remain unchanged. This literal permission exposes root-directory entry names, without adding recursive descendant-content reads, and is not yet a demonstrated repair. Use only the next preidentified r01 root for one complete corrected base attempt, stopping at its first failure; no extra probe, second corrected root or further permission grant follows automatically. Up to three additional same-Claude-Pro static reviews (<=600 seconds each) increase the lifetime review ceiling from 8 to 11, not a reset. The existing task records exact authorization, inputs and results.


## Files And Roles

| File | Role |
| --- | --- |
| [controller.py](controller.py) | Fixed modes, parent-owned evidence, per-run child work area, tool/input checks and process-group budget |
| [common.py](common.py) | Strict invocation/path/hash checks, isolated bootstrap, exact OLD tree/blob/inventory verification |
| [acquire.py](acquire.py), [acquire.sb](acquire.sb) | Offline reconstruction through synthetic Git metadata and source objects; separate OLD write allowance |
| [canary.py](canary.py), [test.sb](test.sb) | Named boundary/runtime/Git/topology/observer probes; no whole-host isolation claim |
| [observer.py](observer.py) | Instrumented flock witness and fd/namespace observations; synthetic self-canaries precede product use |
| [runner.py](runner.py) | Occurrence-preserving discovery, object-linked execution records, explicit preservation status and authored exact-old factory interface; changed P1a behavior remains unexecuted |
| [baseline-inputs.json](baseline-inputs.json) | Unchanged 101 committed blob identities and literal 27/28/29 path sets; historical `tree` field is informational |
| [base-seed-ids.json](base-seed-ids.json), [prefix-oracle.json](prefix-oracle.json) | Unchanged 20 static seed IDs; amended 19-group oracle and late-lock ownership contract, without an executed coverage claim |

## Inputs And Execution Boundary

Private invocation schema 3 binds SOURCE, CONTROLS, ROOT, OLD, EXEC and COMMON_GIT paths, tool launcher/binary hashes, exact source/control bytes, fixed selection, the approved system Git configuration and source_root_entries. Historical schema-1/schema-2 invocation files are rejected by these corrected controls. A digest detects changes; it does not grant approval. Never execute placeholder examples.

ROOT is a named non-Git directory directly under the approved agent-worktree root and must be absent before acquisition. OLD=ROOT/old and EXEC=ROOT/exec are siblings. SOURCE is the existing implementation checkout. Acquisition alone may create OLD. Every mode/slot creates an exclusive parent evidence directory and a separate child work directory:

```text
ROOT/
  old/                         acquired predecessor bytes and exact modes
  controller.lock              parent-only lock
  exec/runs/MODE-SLOT/
    inputs.json                parent gate; child cannot write
    boundary-positive.json     parent probe observations, canary mode only
    result.json                parent gate; child cannot create or alter
    stdout.log                 untrusted child diagnostics, never a gate
    work/                      child's writable subtree
      home/  tmp/  xdg/
      ... child outputs and synthetic fixtures ...
```

The test policy grants file writes only under `work/` and `/dev/null`, plus data writes to the precreated stdout log. It permits reading the literal canary boundary-evidence file but not writing it. Acquisition additionally writes OLD and reads COMMON_GIT/objects; it does not grant reads of the original repository config, HEAD, refs or hooks. Parent result records bind the input-record digest and mode/slot; prerequisite checks compare controls, runtime, Git and system-config identities. A missing/invalid parent result cannot become a completed prerequisite. Earlier child outputs are not mutable by the next slot.

Policies still permit global file metadata and reads of the listed trusted OS/developer/runtime prefixes. This is not whole-host confidentiality or a hermetic runtime. The test policy additionally permits directory-name enumeration at exactly nine literal ancestors of the writable work directory: the run evidence directory, runs, exec, ROOT, agent-worktrees, dev-home, the account home, /Users and /. The controller derives ANCESTOR_0 through ANCESTOR_8 from the fixed invocation/run layout and checks the nine-entry layout before creating the run slot. This exposes the entry names in those directories, including home and root; the literals add no recursive file-content read allowance. Product classify_target requires this enumeration. Acquisition receives no ancestor parameters. The 2026-10-10 correction permits file-read-data on literal / only; no other ancestor-listing grant is added. Network and keychain/mach lookup have no allowance. No real credential query or helper invocation is part of the probes. Policy syntax, service requirements and effective denial remain unverified until separately approved execution; do not widen permissions to make a run pass.

## Isolated Python And Known Git Configuration

The controller and control children use a fixed isolated no-site bootstrap:

```text
PYTHON -I -S -B -c 'import runpy,sys; p=sys.argv.pop(1); f=sys.argv.pop(1); sys.path.append(p); runpy.run_path(p+"/"+f,run_name="__main__")' CONTROLS controller.py INPUT INPUT_SHA256 MODE SLOT
```

The controls directory is appended after the isolated interpreter's standard paths, so it does not take priority over stdlib modules. Only the five named control script basenames are accepted by the child command builder. Complete-parent-O adds `-O` to its runner child. The controller/acquisition/canary/observer check isolation flags; script/module import during P0a authoring remains prohibited. The approved CPython 3.14.7 executable hash identifies that launcher, not every framework dylib or stdlib file. The host's runtime installation is trusted and unsealed; this work does not introduce a toolchain packaging project.

The controller builds PATH, HOME, XDG_CONFIG_HOME, TMPDIR, locale, TZ and bytecode settings from an allowlist and uses DEVNULL stdin. Product/test isolation does not depend on `GIT_*` variables because product `git_environment` removes them. The canary checks PATH-resolved bare `git` against the fixed CLT binary and version, as well as the Python shebang resolution.

The Owner approved retaining the current CLT Git and permitting only the observed system configuration when it is an actual origin: the fixed CLT `usr/share/git-core/gitconfig`, SHA-256 `d9edd909b86735d18b57095355e8f16a67f2a557d02431bb223854291eb6e653`, with `credential.helper=osxkeychain` and `init.defaultBranch=main`. Its exact bytes are checked before mutation. The canary allows either no system origin or exactly both expected system entries; other origins, keys, values or duplicates fail. Its only other permitted origin is its newly generated synthetic repository config, with an explicit safe-key/value set. Reading this helper setting does not authorize a keychain request. Host/global config is never changed.



Before test imports, config verifies the exact immediate SOURCE-root name/type map in source_root_entries, rejecting extra/missing entries, changed file/directory types, symlinks and special entries. This reads names and metadata, not the contents of the .git pointer. Existing src/tests membership and identified-file byte/mode checks remain unchanged. Runner keeps src/tests in their original order and appends SOURCE at the end so tests.test_productization can resolve through its namespace parent. No tests/__init__.py or discovery change is introduced. Collection payload includes the root map, so its hash binds that map as well as source and control identities.

The root guard is not a recursive import seal: existing non-src/tests directories remain importable namespace candidates and their unlisted descendants are not covered. The host runtime remains trusted/unsealed, and other installed or control-directory namespace resolution is not qualified by this static correction. A new root entry needs a newly reviewed exact inventory; do not automatically refresh it to suppress drift. All config callers, including acquisition/canary children and the controller post-check, receive this schema-3 requirement without changing their policies or command budgets.

## Read-Only Preflight And Failure Limits

Immediately before a separately approved first controller call, recheck the fixed runtime/Git/system-config bytes and one-link regular-file status, sandbox-exec presence, PATH python3 resolution, source/controls bytecode absence, object-store alternate/promisor absence and /etc/gitconfig absence. The prior read-only host observations are time-specific, not a substitute for that check. Do not create fixtures, run Git init/config probes, import controls or change host settings as part of this read-only preflight.

Inspect the existing SOURCE/hv2, controls/common.py and invocation file ownership/modes before acquisition. Before canary, also inspect the existing successful acquisition result. These metadata checks identify obvious DAC mismatches but do not prove write-open success under ACLs. Current-run parent files are created within their exclusive slot and receive positive probes only after they exist. A positive probe or setup failure can therefore consume a slot without result.json. Preserve that incomplete result and request an exact recovery decision; do not reuse/delete the slot or select a new ROOT as an automatic retry.

During each future run, preserve the identified immediate SOURCE-root entries. Avoid Finder/IDE/agent actions that create .DS_Store, tool directories or other new root occupants. Read-only inspection is not inherently prohibited. A new or changed entry during execution fails the controller post-check and consumes that exclusive slot; do not refresh the inventory, delete the evidence or reset ROOT to retry.

The synthetic Git origin allowlist remains exact. Extra init keys or an unexpected system origin cause failure, not an inferred expansion of permitted settings. Only the synthetic commit uses `-c maintenance.auto=false -c gc.auto=0`; the preceding config-origin inspection and all host/product configuration remain unchanged. These switches request disabling automatic maintenance for that command. Actual Apple Git subprocess behavior and other process escape assumptions remain unverified.

## Fixed Modes And Bounds

Use exact resolved paths and the identified private invocation after a separate execution approval. cwd is SOURCE. Input preparation and parent probe work count toward the mode budget. Each output slot is exclusive, including failure/interruption; changing roots or slots to reset a bound is not a retry permission.

| Mode and slot | Maximum seconds including cleanup | Required evidence |
| --- | ---: | --- |
| acquire base | 300 | ROOT absent; fixed commit/tree entries/blobs; exact acquired OLD |
| canary base | 300 | Successful parent acquisition record; named positive/refusal controls and bootstrap observations |
| collect base | 300 | Matching passed canaries; real baseline discovery, not AST-inferred counts |
| smoke base | 1200 | Explicitly bound collection hash; every discovered occurrence of the 20 seeds, no skips/expected failures |
| collect p1-controls, p1, p1-correction, p2, p2-correction, p3, p3-correction, final | 300 each | Eight entry slots; no repeated source/control/phase tuple; exact-old factory |
| focused p1-controls, p1, p2, p3, correction | 1200 each | Five entry slots; shared product correction slot; exact selected occurrences |
| complete-normal final | 5400 | One frozen candidate; whole default collection plus exact factory |
| complete-parent-O final | 5400 | Same candidate/collection; parent runner optimized, child flags reported separately |
| artifact final | 1800 | Same candidate and exact fixed artifact IDs |

These are proposed ceilings, not approved runs or promised durations. The controller stops the process group on budget exhaustion and treats surviving children, incomplete cleanup, input drift and oversized stdout as non-pass. Stdout has a 16 MiB detection threshold checked while running and at completion; a write burst can overshoot before termination, so this is not a filesystem quota. The child can truncate or rewrite its diagnostic log; observed size therefore does not bound cumulative output or guarantee a complete transcript. Parent inputs/results, rather than stdout content, remain the prerequisite gate. Input/post-check time is included in recorded total duration, and exceeding the total bound is non-pass. Filesystem calls themselves are not an independently preemptible host sandbox.

The bounded A2 runner corrections have an accepted static checkpoint; actual collection/test behavior, integration with the `work/` layout and broader runner/factory qualification remain open. The initial schema-3 input has `collection_sha256=null`; it grants no smoke/test identity. A future execution approval must expressly cover the binding procedure below. No current authoring approval covers collection, binding or smoke execution.

## Acquisition And OLD Identity

Acquisition writes a small synthetic bare metadata directory under its own `work/`: fixed safe config, HEAD, empty refs/objects directories. This is a synthetic fixture, not a managed source worktree. Its Git processes use `GIT_OBJECT_DIRECTORY=COMMON_GIT/objects`, `GIT_NO_LAZY_FETCH=1`, `GIT_OPTIONAL_LOCKS=0`, the exact approved system-config path and `GIT_CONFIG_GLOBAL=/dev/null`. These variables are restricted to acquisition subprocesses; they are not a product/test isolation strategy.

Reject alternate-object-store and promisor markers before invoking Git. The fixed Git binary receives only these acquisition command forms, each with a 30-second subprocess limit inside the total 300 seconds:

```text
git --git-dir=WORK/git-metadata ls-tree -rz --full-tree 238514686078ce1564010a7b69013f48a635c57c
git --git-dir=WORK/git-metadata cat-file blob OID
```

OID must be in the unchanged baseline manifest. No fetch, checkout, hook, filter or source-repository configuration is needed. The manifest's file names/types/modes must match the tree listing. Blob content is checked by size, SHA-256 and independent SHA-1 Git blob-object calculation. Files become 0444/0555 according to executable intent; all directories, including OLD, become 0555. Verification rejects extra empty directories, symlinks and special members, checks exact file/directory membership and modes, and independently reconstructs the 29-file checkout inventory digest from acquired content. The manifest's `tree` value is historical metadata, not a separately attested tree seal.

Partial acquisition is retained as non-pass, without cleanup or retry. These bytes qualify only the fixed checkout-1 predecessor input; literal earlier path lists are structural oracles. Historical schema1 and actual schema2 detach qualification still need their separately reviewed fixture/factory work.

## Named Boundary And Observer Probes

Before the canary child starts, the parent records positive controls for the same OS user: open existing SOURCE/CONTROLS/INPUT/current-parent-inputs/prior-result files for writing without truncation or writes; read the known non-secret COMMON_GIT HEAD and synthetic sentinel; perform an idempotent same-mode chmod on OLD's `.gitignore`. It checks retained bytes/modes after the positive operations. The chmod may update filesystem ctime; it is not a claim that every stat field is immutable. These positive operations are future execution steps, not performed during authoring.

The sandboxed canary attempts those exact operations and requires EACCES/EPERM. The successful parent counterpart distinguishes ordinary permissions from the sandboxed refusal. OLD's chmod result supports only metadata-write denial for that operation; exact read-only mode custody is checked separately, and this does not prove every possible data-write operation. An unexpected permission is a failure even if no bytes changed. Network probes are named loopback bind/connect denials. The child-inheritance canary repeats the named boundary/runtime probes; it is not a whole-OS isolation proof.

Synthetic observer cases cover file-object and integer-fd flock inputs, parent-held attempt/acquired ordering, fd writes/fsync/mode changes, unlink/replace and mkdir/rename/rmdir/chmod plus audit-before events. `observed_flock` normalizes the descriptor for observation while delegating the original argument and operation. A one-byte interrupted fake write verifies its physical result and SIGKILL status. No self-canary is product-prefix or real old-writer qualification.

The observer uses the same isolated bootstrap, with `observer.py INPUT SHA SCENARIO SCENARIO_SHA256` after CONTROLS. Scenarios are synthetic files inside the current writable work area, with exact `entry,target,argv,events,fault` keys and optional entry-only `pause`. Product selectors remain old-source/new-source/installed-old/installed-new; additional primitive/lock/lock-fd canaries use fixed fake bytes and empty argv. Old product paths receive only flock delegation/observation. New-prefix fault observation remains instrumented, not an uninstrumented CLI or power-loss claim. Descriptor-relative namespace operations remain unavailable and must stop, not silently pass.

## Later Runner And Factory Boundary

The runner preserves default discovery duplicates and labels each occurrence `{id, occurrence}`. Entry phase still requires `test_entry_window_transition.build_entry_suite(old_source, candidate_source, expected_predecessor, prefix_oracle, *, execution_context)` and rejects a missing/empty factory. The explicit factory now exists in `tests/test_entry_window_transition.py`; its local classes remain outside default discovery. Historical planning-1 factories are not retargeted. Adding SOURCE/colvia in a future entry phase changes root membership and requires a newly identified and reviewed root map before that phase runs. Static intended IDs, independent schema1 construction, actual OLD schema2 construction and initial future-product assertions are now authored; their actual collection and behavior require separate review and execution approval.

Selected test objects retain their identity queues independently. startTest checks the actual object and its id rather than consuming a global positional queue; class/module setup failures cannot shift another object's label. Non-start callbacks are recorded in suite-events.jsonl with identity=null. A skipped subtest is associated with its active parent. If the same object occurs more than once after a non-start fixture event, the runner conservatively writes identity-stop.json and refuses to guess which occurrence ran. This can stop an otherwise disambiguatable run; it is not a false-success workaround or permission to deduplicate. When TextTestRunner.run() returns normally, including runs with test failures, the runner records unstarted.json and unfinished.json; a missing final summary after an exception/termination remains incomplete evidence.

Each executed row includes all observed outcome categories and a non-pass-first summary, so a later skipped subtest does not replace an earlier failure label. Existing unittest failure/error/skip/expected/unexpected counts and the all-selected-occurrences requirement remain the exit gate. No assertion, selected ID or discovery algorithm is substituted. Non-start events are not claimed as executed test rows.

Child collection.json, selected/executed/count and diagnostic records belong under MODE-SLOT/work/; parent inputs.json and result.json remain above that subtree. Child output is diagnostic evidence, not authority to accept work. Each addError/addFailure/failing-addSubTest preservation attempt writes preservation.jsonl with copied, unavailable or stopped status and its reason. Root candidates remain exactly base/root/f.base/h.f.base; no temp.name/target.parent search or fixture edit is added. Missing reachable roots and roots containing the output are explicit unavailable results. Local fixtures and with-block cleanup can still destroy bytes before a callback; retaining EXEC does not preserve those lost bytes.

Existing copy caps remain 64 MiB per attempt and 256 MiB per run; repeated subtest attempts still accumulate. Root/scan/copy errors and cap exhaustion try to write preservation-stop.json and end with exit 87 without Python fixture finalizers. If the diagnostic filesystem itself fails, a marker may be absent; the exit/partial run remains non-pass. File-size accounting is not a quota or a concurrent-tree snapshot, and copied status describes a completed copy call, not an independent byte-for-byte attestation. Process-test sibling evidence and its own archive remain outside these caps. Diagnostic JSONL files are not fsynced or separately bound into parent result.json. These limitations remain open; no broader preservation or crash-durability claim is made.

## Collection Binding Before Smoke — Proposed Procedure

This is a concrete prerequisite procedure for a future separately approved run. The controller currently does not enforce successful collect-base provenance or exact equality with the seed file. Do not treat the following steps as already executed or as a new automatic controller feature.

1. Verify the approved schema-3 invocation and all fixed inputs before consuming any slot. Require phase=base, factory=false, selection equal to the ordered twenty-ID seed file and collection_sha256=null. Stop for any mismatch; do not use a failed run to discover an obviously incomplete input.
2. After a separately approved collect-base finishes, read its exact parent result.json and inputs.json. Require execution_pass=true, mode=collect, slot=base, the expected invocation_sha256 and the result's inputs_sha256 equal to the actual input-record file digest. Verify source/control/tool/config identities against the approved invocation and retain all existing parent success/cleanup limits. No failed, partial or differently identified collect run is eligible.
3. Read that same run's work/collection.json directly with duplicate JSON keys rejected. Require exactly seven keys: source_digest, source_root_entries, controls, default_ids, factory_ids, ordered and duplicates. Require the raw file bytes to equal canonical reserialization as defined by common.canonical (sorted keys, two-space indentation, ensure_ascii=false, one trailing newline, UTF-8). Verify source_digest, controls and source_root_entries against the invocation; require empty factory_ids in base mode and independently derive ordered per-ID occurrences and duplicates from default_ids. Require exact agreement with ordered/duplicates and presence of all twenty selected IDs. Record actual occurrence counts and every unittest.loader. synthetic ID, including import-time ModuleSkipped entries, and their effect on the selected IDs. Do not filter or deduplicate discovery to hide those entries; non-seed synthetic IDs remain explicit collection limitations, not full-suite qualification. Hash the exact canonical file bytes; compare the emitted stdout hash only as a diagnostic cross-check. A missing/mismatched record stops binding. Parent success does not itself cryptographically bind the child's collection file, and these checks cannot prevent nondeterministic later rediscovery.
4. Prepare a new identified invocation whose only difference from the approved collection invocation is collection_sha256 set to that verified file digest. Confirm every other field/selection/path is identical and recheck the input identities. Preserve both exact inputs and the parent-result/collection references. The new digest identifies bytes but does not authorize smoke; invocation/binding execution must be within the future Owner approval. Smoke independently recollects and requires the same payload digest before running every occurrence of the selected IDs.

Do not overwrite the initial invocation, reset ROOT/slots or silently change root membership, controls, budgets or selection to make this procedure pass. Changed controls before the first acquisition require their own corrected-input review; later changes make earlier prerequisite evidence inapplicable to that new candidate while preserving its historical meaning.

## Static Checks And Remaining Gate

This revision may be AST-parsed without import, checked for JSON/hash/path consistency, reviewed against the named counterexamples and rendered for document/link/disclosure/whitespace checks. The prior P0 base controls executed with 20/20 selected occurrences and were accepted only for that identified input. This changed P1a candidate has not been imported, compiled by SBPL, acquired, collected or executed. The bounded execution-documentation result review, base-plan review and actual base execution retain their separate approval boundaries. Runtime service/permission behavior, process timings, observer effects and downstream test integration remain unverified. Preserve exact corrected inputs and the recorded limits for the next review; do not promote static checks to executable success.

## P1a Candidate 01 — Actual Authoring Boundary

The runner builds the exact ten-field immutable `execution_context` from the verified invocation, controls, runtime and current WORK. The factory verifies it again and constructs suites without fixtures or children. `controller.ENTRY_MODE_SLOTS` is the sole entry slot table; `ENTRY_RUN_NAMES` is derived from it. Both runner and observer validate the imported controller module path before use. Collection attempts are distinct by `(source_digest, controls, phase)`; missing phase is rejected. Default discovery multiplicity remains unchanged by the collection algorithm.

Entry scenarios live at `WORK/entry-scenarios/ID.json`. Targets, event logs and exclusive ready/release files are confined to that WORK. Pause is allowed only at the first actual writer-lock acquisition, with timeout exactly 15 or 60 seconds. The child owns the lock; ready carries PID/PGID, target/lock inode identity and scenario/sequence identity. Original I/O performs the handshake outside product fault logging. File-object and integer-fd flock delegation remain separate checks. The fixed entry-only `lock-prefix-canary` writes `synthetic-prefix-only\n` after matching release. Wrong token, links, reused paths, timeout, missing requested pause/fault, full write kill and one-byte short write do not become success.

Current static AST enumeration finds 25 intended P1a control/fixture IDs and 13 intended future-product IDs. This is an authoring inventory, not executed discovery. `focused-p1-controls` may select only factory objects labelled `verification_stage="p1-controls"`. Product cases require entry-1 at execution and are never skipped to manufacture a pass.

The OLD child programs are fixed module strings. They use a non-Git target, fixed authority/operation identifiers and `2026-01-01T00:00:00Z`; import only OLD/src; verify the exact checkout-1 release; and report PID/PGID. The schema2 child performs init, verified snapshot, detach preview and the exact `after-receipt` exception, then checks paired schema2 and preservation. Schema1 is an independently authored literal 29-member planning-1 fixture with exact removal order and binding/receipt relations. Neither is a renamed schema3 fixture.

Synthetic child/coordinator bounds are 60/90 seconds; OLD fixture bounds are 90/120; product child/coordinator bounds are 150/180. Cleanup terminates then kills boundedly, attempts every direct child before reporting errors, and reaps direct children. Reaping does not prove grandchild absence or absence of PID reuse. The outer controller checks process-group absence after the runner ends. A live coordinator cannot claim its own group is absent. Time bounds are proposed executable contracts, not measured sufficient durations.

The 19 oracle groups remain qualification obligations. Initial product cases cover selected N/B/O kill points, synthetic receipt/staging tears, late collision/operator relocation, unsupported umask, schema1/2 readers, schema3 detach and one late OLD detach sequence. They do not provide complete before/after coverage for all 19 groups, every member or every old operation. Buffered file writes are not os.write hooks; synthetic truncation is not a killed write or power-loss evidence. Remaining P2/P3 test matrix work must use the reviewed controls or trigger the accepted E control-change route. No unsupported observation counts as PASS.

The eleven control files are a proposed freeze candidate, identified in the private actual-byte packet. Review and Owner acceptance must precede any freeze claim. The current Owner batch authorizes six separately identified calls (base acquire/canary/collect/smoke, entry collect/focused p1-controls), at most 3,600 seconds total, one each and no automatic retries, after review removes execution blockers. The Driver must fix the new ROOT and exact invocation/selection/commands and a cumulative cross-root ledger before execution. This authorization replaces the earlier separate per-step approval waits within the batch only. Prior P0 receipts cannot qualify changed controls. Product/default tests, common/acquire/canary, baseline/seeds and policies are unchanged.

## P1a Candidate 02 — Bounded Correction

Each existing os wrapper now emits a selectable operation-before event immediately before delegation and operation-after only after successful return: open/write/fsync/fchmod/unlink/replace/mkdir/rename/rmdir/chmod. The before event is not a previous operation's after event. Exact root path `.` is allowed only for fsync-before/after; common relative-path validation is unchanged. The fixed lock-prefix canary also opens/fsyncs the target directory after its file write under the child's own lock. No arbitrary program/selector was added, and OLD writer delegation is unchanged.

Six additional control tests specify all ten primitive before/after fault pairs, both root-fsync edges after a matching pause release, invalid root/path selectors, overlapping/target-internal handshakes and an unobserved requested fault. Link negatives require the specific linked-path or handshake-file-kind failure, excluding timeout. The factory-construction snapshot permits recording regular hardlink counts so the check is independent of a preceding link fixture; product/OLD fixture snapshots still reject hardlinks. Import audit coverage adds link/symlink/truncate/exec/forkpty events; os.replace is covered by os.rename. This is a partial side-effect probe, not a security boundary.

Timeout values remain closed duplicated constants: the oracle test compares the oracle to literals, not a mechanical binding to every observer/coordinator call site. No bound is increased or derived from arbitrary input. Requested-pause-not-observed and fault-before-matching-release branches have no reachable fixed synthetic selector under the existing first-lock and path guards; product paths remain future qualification. Base-phase pause rejection remains statically guarded and is not claimed as an executed negative by these new entry tests. Buffered I/O, power-loss durability and the complete nineteen-group product matrix remain unqualified.

The six-call order is acquire-base → canary-base → collect-base → smoke-base → collect-p1-controls → focused-p1-controls. The smoke-base and focused-p1-controls runs require the exact successful collection identity, source/control/phase matching and independently checked selection; entry focused additionally needs the prior collect WORK for its cross-WORK refusal case. Runtime failures stop the batch without retries or policy widening. The existing runner preservation callback can fail while a child is still live; exit 87 or incomplete preservation remains non-pass, not a repair of that limitation.

The primitive fsync edge assertions establish event/call order, not persisted state; chmod-before likewise has no umask-independent physical mode assertion. Other operations (including os.link/symlink/truncate/pwrite and native-copy paths) have no selectable before/after hooks. Such observations remain unavailable for future product qualification. The first candidate-02 static review found no confirmed execution blocker; source metadata and actual execution identities remain distinct from executed evidence.
