# P7 focused result and P8 plan review disposition

A fresh Claude CLI session reviewed seven limited input excerpts and the synthetic-result summary, without tools or execution. Input identities matched before/after; the call took 337.4 seconds. This is an excerpt review, not a complete audit. The first proposed whole-file transmission was rejected by automatic approval review; it was not sent. The executed packet was reduced to the previously authorized sanitized excerpts and synthetic summary. Private verbatim findings remain in the owning Work evidence.

## P7 dispositions

| Finding | Driver disposition |
| --- | --- |
| A1 Windows create attributes | Accept. Add `FILE_READ_ATTRIBUTES` to the create handle and default metadata opener. Native round-trip remains unverified; portable source tests do not qualify Windows. |
| A2 incomplete final marker | Accept for both ports. Write and flush a fresh prepared file, then publish with a no-replace move. A failed partial write keeps only prepared bytes, never a truncated final marker. Existing targets are not replaced. Preserve post-publication uncertainty. |
| A3 Windows readers/replacement | Accept read sharing including delete, paired with opened-file and current-path identity checks. A failure after replacement gets a distinct durability-unknown classification. Prepared files remain until their recovery/retention purpose is resolved. No automatic retry. |
| A4 lock opener/cleanup | Default sharing was already read/write and disposition existing. Make it explicit, add shared read-only leases for installed transactions, and preserve an original exception if unlocking also fails. |
| A5 directory ancestors | Accept. Hold ancestor handles through directory creation, private-ACL verification and sync. |
| A6 pending existence | Accept files-port reads that treat only FileNotFoundError as absence. Permission, damaged marker and unknown I/O propagate. |
| A7 target seal | Internal project/instance identity was already checked on every store transaction. Also recheck target root, fence, pending-rebind, imported origin and pending effects in the same short write transaction that seals the target. |
| A8 readback scratch | Existing GraphAudit already uses exclusive creation and rejects symlink ancestors; it never reopens stale rows. Candidate generation names are never reused. Retain that model, use lstat consistently, and assert restored requirement/index/root-row counts before seal. A failed private audit remains evidence; it is not a reusable validation cache. |
| A9 no recovery slot | Preserve the explicit unavailable boundary when neither selected nor recorded recovery manager verifies. Do not activate arbitrary bytes or reset trust. Authenticated repair composition is still pending; the source slice is not a complete installer. Slot tokens already reject separators and leading dots. |
| A10 archive staging | Keep signed manifest plus full content verification, not the outer archive digest alone. Current extraction/inventory is POSIX source code, not Windows staging. Incomplete candidate slots remain unselected with a distinct operation name; do not overwrite/reuse them silently. |
| A11 detach | Preparation writes only reproducible private postimage staging, not routing/entry/locator files. Accept explicit manifest-to-preview equality and a recorded preview digest. Record field validation re-derives that digest; a changed transformation refuses before effect reservation. |

An installed runtime lease was independently added while the excerpt review ran. Each short managed-store transaction holds a shared runtime lock; activation holds it exclusively. Once selection changes, the old handle refuses subsequent reads/writes. Source-only stores remain labelled source-only. This change was outside the excerpt review and has its own focused transaction/race fixtures; final cumulative review must include it.

## P8 plan dispositions before implementation

- B1: Parse and validate index checksums; refuse `index.skipHash`. Only known extensions are admitted. Drop disposable `TREE`, `EOIE`, `IEOT` and `FSMN` in the newly serialized index. Initially refuse `REUC` rather than inventing merge-undo preservation. Unknown mandatory/optional representations remain unsupported. Write-tree comparison checks that dropped acceleration data cannot affect the intended tree.
- B2: Selected entry stat data is zeroed; no claim of filesystem freshness is inferred from a copied timestamp/size. Test same-size edits after integration with `diff-files`.
- B3: Refuse selected assume-unchanged, skip-worktree or intent-to-add entries. Preserve only explicitly supported unrelated flags.
- B4: Require files ref storage and known repository extensions/object format. Disable replacement objects and refuse grafts, partial-clone/promisor and alternates. Scrub inherited Git override variables. Refuse sign-required automation, then pass `--no-gpg-sign` to the admitted commit-tree operation. Disable auto-GC and hooks/filters/external diff as already scoped; hook-enabled repositories keep a manual path.
- B5: Explicit recovery for O/I0 may record not-applied and release only an exactly owned abandoned index lock after process closure is proven. It does not retry or approve a new candidate. Other states retain C6's exact ref/index rules.
- B6: Do not depend on the held P5 termination path. Bounded Git mutation records the direct child identity and waits only within its limit. Timeout keeps the effect pending without sending a signal. Hook/filter/helper-producing paths are excluded and process-group absence must still be observed before claiming closure; an empty hooks directory alone is not proof that no child exists.

These dispositions authorize no new OS action, public support claim, product commit, key generation or installation. The existing 100-hour source limit and two remaining reviewer calls still apply.
