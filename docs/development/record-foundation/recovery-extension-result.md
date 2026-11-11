# Recovery extension result and remaining initial-install boundary

Status: source correction and two static reviews performed; Owner acceptance and
installed-release qualification remain separate. One first-install recovery case
is still a public-release blocker. No actual install, OS grant, key generation,
notification, product commit or publication occurred.

## Implemented behavior

- Initialize trust/configuration/attempt identity privately, then publish the whole
  home with a no-replace directory move. Interrupted stages and failed attempts stay.
- Retry an initial preparation explicitly without resetting trust floors. A
  prepared attempt may be superseded only while all live installation paths remain
  absent; a superseded attempt cannot publish, refresh or resume.
- Renew metadata for the exact original target only. Renewal binds operation,
  preparation receipt and full target descriptor; it never downloads target bytes.
- Restore authenticated prior alias/app bytes only while the old runtime remains
  selected. Check originals again before creating the one-way rollback intent.
  Keep displaced update bytes and pending barriers through exact completion.
- Once runtime selection has completed, verify exact current files and finish
  receipts/barriers without requiring a new target authentication. This path does
  not recreate or overwrite missing/changed executable files.
- Inspect initial installation through the verified bootstrap (`--install-status`
  or PowerShell `-InstallStatus`). It returns the latest attempt, prepared receipt,
  selection and whether live files already exist. No hand-written hash script is
  needed. This inspection still requires the verified bootstrap runtime.

## Result-review disposition

Both reviews were fresh, static CLI calls with no tools. Plan review took 233.620
seconds; result review 381.285 seconds; inputs stayed unchanged during each call.
The result packet deliberately omitted unchanged dependencies. Conditional claims
below are checked against those dependencies, not treated as reproduced failures.

| Finding | Driver disposition |
| --- | --- |
| H1: retired target blocks prepared first install | Corrected for prepared but unpublished attempts through explicit supersession and a permanent old-attempt guard. The partially published case below remains open. |
| M1: omitted pending component | Fixed by checking both fixed pending paths independently of computed components. The illustrative old-entry-absent path is already constrained by native-entry preparation, but the stronger invariant is retained. |
| M2: rollback intent before original recheck | Fixed: inspect every forward item again under management/runtime/effect exclusion before writing the irreversible intent. |
| M3: missing POSIX directory flush | Not adopted: exclusive.rename already fsyncs the destination directory handle (and distinct source handle). The caller also rechecks parent and published identity. No duplicate flush is needed. |
| M4: Windows open handles / transient retry | Source objects hold no persistent stage handles; API-double publication checks zero open stage handles. Native scanner/sharing behavior remains unqualified. No automatic permission/sharing retry was added. |
| M5: verified_ns might refresh a withdrawn target | Not adopted: this is a clock floor plus exact preparation binding, not a substitute for target verification. activation_check reauthenticates cached signatures and the exact target; old metadata/version/time mismatches refuse. Splitting the clock update would weaken failed-refresh clock preservation. |
| M6: expiry blocks selected-runtime finish | Fixed for update and first install: exact selected files/slot/receipts only, no fresh executable effect or metadata fetch. |
| L1/L6: latest attempt and receipt unavailable | Added verified-bootstrap initial status. The bootstrap's terse interruption message directs to status; its original attempt identifier remains historical, not permission to retry it. |
| L2: replace identity with nonce for moved homes | Not adopted. Initial-attempt recovery does not implicitly adopt copied/moved homes. Identity/path refusal protects the publication claim; relocation needs a separate explicit contract. |
| L3: claimed old attempt can run after retry | Fixed: supersession guard is checked under the management lock at start and resume/refresh/publication. |
| L4/L5: metadata port / rollback Trust / operation argument | Renewal uses a metadata-role-name allowlist in both entry paths. Rollback dispatch creates neither fetcher nor Trust. Recovery operation is already a required positional parser argument; only ordinary update generates one. |
| L7: later update changes past rollback status | Fixed: status compares pending tokens with this rollback's own bindings, rather than global existence alone. |

Additional information dispositions: completed cleanup uses a receipt-bound area
basename and this is now stated accurately; payload digest records the initial
bootstrap provenance and is not imported as a replacement root on retry; private
file/ACL methods validate rather than set permissions; alias names are fixed by
the v1 protocol; effect manifests always contain the evacuated-name field,
including create-from-absence entries. Windows retained-original checks include a
portable protocol test and do not imply native Windows qualification.

Windows directory publication uses the documented same-drive, absent-destination
MoveFileEx path with no copy/replace flag. See the [Microsoft directory move
contract](https://learn.microsoft.com/en-us/windows/win32/fileio/moving-directories).
This source alignment does not establish native durability or scanner behavior.

## Executed checks and limits

The consolidated recovery checkpoint passed 128 tests across 14 suites. After
result-review corrections, 112 relevant tests passed across 10 suites. Counts
overlap and must not be summed. The earlier 822-test cumulative source checkpoint
is reused for unaffected behavior, not presented as a fresh full-suite result.

The routing pass first failed two optional-empty-argument expectations; the
corrected route passed. The result-correction pass first failed a test expecting a
RecordError directly: pinned TUF wraps it in DownloadError. The corrected assertion
checks the original refusal cause and no upstream target fetch. All failed outputs
remain preserved. Input identity stayed stable in each executed run.

Fixed signed fixtures cover authentication/counter behavior without creating keys.
Native macOS file effects use inert synthetic bytes; Windows tests use API/protocol
doubles. Real release-service expiry rollover, installation and host behavior are
not qualified by these checks.

## Remaining public blocker: retired first target after partial publication

Executed synthetic counterexample: initial preparation is complete and aliases
exist; runtime selection has not occurred; metadata has expired; the configured
signed target now describes different bytes. Exact resume refuses expiry; renewal
refuses target mismatch; retry refuses existing live files. All prior files stay
unchanged. A passing refusal test proves preservation, not successful recovery.

No old runtime exists, so the approved old-runtime rollback cannot resolve this
case. Do not reset trust, erase the home, silently activate expired bytes or label
it supported. A possible next source contract is explicit quarantine/supersession
of only this attempt's authenticated generated files, with no selected runtime,
project authority or OS registration, followed by fresh signed preparation using
the existing trust floors. Its interrupted-quarantine ownership and exact file
inventory need a separately reviewed contract before implementation.

Existing worker-source lifetime, native execution closure, unfinished imported
effects and Codex writer-host holds remain unchanged. This result does not reopen
those lanes or authorize product acceptance or release.
