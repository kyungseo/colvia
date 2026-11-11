# Pre-R3 direction advice — Driver disposition

2026-11-06. Owner pasted a Claude direction opinion based on documents around 21:11 KST, while the Driver was still editing. No fixed input digests, model/session identity or executed tests were supplied. Treat it as supplementary design advice, not the pending R3 verdict. Its original wording remains in the Owner's chat message; this file contains Driver dispositions, not a purported verbatim reviewer file. Current source and the original desktop handoff were read; no product test or model was run.

## Conclusion and corrections to claims

Accept the architectural direction and the D7 mismatch. The real recorded pattern is `.claude/worktrees/`, which addresses a parent container. Merely allowing an individual registered root would not handle that case. Pattern semantics matter too: an internal slash can make the pattern root-relative without a leading slash. The earlier blanket “all detailed choices closed” wording did not prove this observed case was covered.

Do not adopt two broader assurances. Storage grows with new unique chunks plus metadata/index/staging/backups, not exactly with changed source bytes; shifted/recompressed documents can defeat most deduplication. “Normal scale is sufficient” is not measured new-implementation performance. Existing observations identify bottlenecks, not a successful new latency benchmark.

## Item dispositions

| Advice | Disposition | Treatment |
| --- | --- | --- |
| Required D7 | revise/accept | C5 covers exact root or verified parent, every immediate entry including hidden entries, empty/absent former parent, baseline protection and per-observation recheck. Never permanently whitelist a container name. |
| 1 body removal | needs-user | A material exception to retained-body policy, not just a new enum. Concrete recommended policy below; include in R3 as an open decision. |
| 2 WSL | accept with narrower rationale | Native Windows is the first Windows qualification target. WSL/Linux and cross-OS authority writes are unqualified; do not claim all WSL locking is inherently invalid. |
| 3 bootstrap/signing operations | revise/accept | Thin authenticated first-install bundle may supply Python and verifier; existing trusted manager must verify updates before running new code. A fixed hash from the same compromised origin adds no independent initial trust. Add freshness automation/outage cost; do not extend expiry arbitrarily. |
| 4 host settings | accept, already early gate | Compare narrow user-level per-project grants and actual inheritance in P2; no assumption that each host supports the same setting or that worktree copies contain it. |
| 5 large observation | accept with caveat | Publish measured scale and separate bytes/history/workload. A future stat cache cannot certify unchanged content for decisions by size/mtime alone; false-negative tests required. |
| 6 batch chunks | accept | C3 now permits up to 4 MiB/64 chunks per staging transaction with 1 MiB chunk maximum. This is an engineering bound, not a latency guarantee. Measure actual reader delay. |
| 7 hooks | accept | Manual Git handoff is normal, but exact commands depend on current staging. Preserve partial staging and inspect post-hook commit contents before linking to acceptance. |
| 8 backup hint | accept | On-demand last successful export/root status, no claim that backup still exists or is off-device. No automatic deletion/export/reminder. |
| Time estimate | revise | The P4/P5/P7 ranges were optimistic. Show a risk-adjusted forecast separately from the previous reuse case and unchanged proposed stop budget; do not make the Reviewer total an observed fact. |

Additional official-document check: SQLite DELETE journal durability differentiates FULL from EXTRA at journal unlink. C3 now asks for EXTRA plus the separately qualified macOS fullfsync behavior; this is not a power-loss guarantee independent of the OS/storage. [SQLite pragma reference](https://www.sqlite.org/pragma.html#pragma_synchronous)

## Owner decision proposal — explicit removal of retained body content

Recommendation: permit an explicit owner-authorized exception before v1 is fixed, and include a minimal operator command before public release; a polished UI may follow. This is stronger than reserving an enum while leaving users unable to act. No actual removal or policy adoption has occurred.

Proposed scope:

1. Keep the historical fact of submission/acceptance, identifiers and a removal decision. Make body availability explicit: retained / intentionally removed under a referenced decision / unavailable-corrupt. Acceptance is not rewritten to say another body was reviewed. A removed result cannot be used as available input for replay/integration or a fresh acceptance requiring its bytes.
2. Preview exact affected bodies and every shared consumer before approval. Deduplicated chunks may be used by other Works. Removing bytes globally must identify and authorize all affected consumers; otherwise refuse, never silently damage other results. A logical hide that leaves reconstructible chunks must not be reported as physical removal.
3. Preserve an explicit decision/refusal path and redact sensitive text from reasons, diagnostics, caches and display projections too. Do not quote the secret in the removal log. A digest or filename may itself reveal information; retaining it is not an anonymization guarantee.
4. Treat the operation as a separate recoverable transaction: record authorization, block new references/reintroduction during application, classify interrupted states and verify the live store's reachable content afterward. Unknown removal record kinds must fail closed in older readers, not be mistaken for corruption that can be “repaired” by restoring deleted bytes.
5. Updated export/import must represent authorized absent bodies without fabricating complete content or silently restoring it from an older local copy. Existing exported backups, Git history, original project files, OS snapshots, filesystem remnants and external copies do not disappear automatically. List these as separate cleanup/recovery obligations. Restoring an old backup can restore old content; do not promise universal irreversible erasure.
6. Document during connection that approved files' before/after content is retained. This is a retention-policy exception, not a PII scanner, model isolation feature or encryption system.

The exact missing-body/export semantics and shared-chunk protocol need R3 review and Owner policy choice before P1 format freeze. Implementation cost is not yet included in the revised forecast. SQLite row deletion alone is not a secure-erasure proof; the official secure-delete behavior has specific limits. [SQLite secure-delete reference](https://www.sqlite.org/pragma.html#pragma_secure_delete)

Until that choice, preserve the currently accepted rule: no automatic deletion of published bodies. A schema can evolve under the already planned compatibility protocol; reserving an undefined enum does not make future semantics automatically backward compatible.

## Estimate disposition

The former implementation estimate was 50–75 activity hours. Substituting the identified risk ranges P4 8–12, P5 12–20 and P7 20–35 gives 75–120 activity hours for the same retained scope. This is a scenario calculation using unmeasured judgment inputs, not new development evidence. With the separately estimated actual qualification 12–20, the combined activity forecast becomes 87–140 hours, excluding environment/authentication/external waits. Do not compare that directly with another estimate unless its included activities match.

The proposed 100-hour implementation stop budget remains a stop, not a guarantee of completion within 100 hours. No new or enlarged implementation authorization is inferred. P0–P3 early checkpoints and post-P1/P2/P3 re-estimation remain. A full-body-removal implementation or unexpected platform redesign requires an explicit cost amendment before execution. The goal is honest staged investment, not increasing a cap until every uncertainty fits.

## Evidence and next review

Observed D7 wording comes from the existing desktop handoff; new C5 behavior is designed, not reproduced. Git pattern interpretation was checked against [official documentation](https://git-scm.com/docs/gitignore#_pattern_format). Initial trust and update verification are separated consistently with [TUF's scope](https://theupdateframework.github.io/specification/latest/#14-non-goals). No existing failure is converted into a pass.

The earlier R3 packet was prepared but the Owner says it has not been sent. Retain it as superseded input identity; prepare a new R3a packet with this disposition and the open retention choice. There is no R3 reviewer response yet. Do not silently claim the 21:11 advice reviewed later changes.
