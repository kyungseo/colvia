# R2 review disposition and remaining decisions

Status: Driver disposition, 2026-11-06. [Reviewer response](review-r2.md) is preserved verbatim. All eleven reported document hash prefixes and the entry-document diff prefix matched before correction. The reviewer used a fresh conversation but the same model family as R1; its external-behavior claims were not executed tests. The Driver checked the official documentation cited below. No product, installed setting, VM, model session or Git state was changed by this disposition.

## Practical conclusion

Keep the shared authority, workspace-specific results, preserved bodies and separate Git integration. Do not start implementing an unresolved public format. R2 identifies real gaps, but its suggested algorithms are not automatically safe or fully specified. The initial intake corrected contradictory text. The closure below now supplies detailed contracts, semantic refusal inventory and costs; implementation and qualification remain separate from design closure.

## Mandatory findings

| ID | Disposition | Concrete treatment and remaining gate |
| --- | --- | --- |
| M1 location and permissions | revise / Owner policy adopted | Recommend an OS user-data authority per project, with explicit host-scoped access to that project directory. Do not grant the entire authorities root by default. Common-dir/non-Git locators are connection-time metadata, not permission grants. Realpath/file-system identity and nonce mismatch must stop writes. A copied nonce or an absent old path does not prove a move; explicit relocation must retire the old binding and address simultaneous copies. Exact CLI/app settings and their inheritance remain to be qualified before choosing the locator. |
| M2 backup promise | revise / Owner policy adopted | Recommend versioned logical export/import of a pinned complete root set, including settings, workspace registrations, capability state, archived Work and acceptance bodies. Work heads alone are insufficient. A local update recovery checkpoint and an off-device user backup serve different failures. Import into a new empty authority validates all references and requires explicit local rebinding; it does not revive copied host permissions. Git clone alone is not backup. |
| M3 large-body lock | accept, qualification pending | Remove the single large body-import transaction. Stage immutable chunks in bounded transactions, then atomically publish the small body descriptor and referencing heads after revalidation. Incomplete imports remain unreferenced. Short transactions still take locks; require bounded reader latency/busy handling rather than promising zero contention. Chunk size and timeout need measurement. Chunk rows do not inherently require Python blobopen. |
| M4 paths and trie | detailed contract C2 written; tests pending | Specify canonical logical path, actual filesystem spelling and alias detection separately. NFC/UTF-8/slash-separated paths are the proposed logical key, never a silent filesystem rename. Git case settings and Python casefold are not proof of the filesystem's equivalence rules. Preserve mode/symlink meaning rather than treating every non-Git Windows entry as regular. Define Node(S,d) from sorted complete sets and test order independence and overflow with a test-only hash seam; production hashes remain fixed. C2/C3 now set encoding, limits and portability refusal; property tests remain pending. |
| M5 observation policy | detailed contract C5 written; tests pending | Freeze the effective policy inputs needed to replay admission, including interpreted origin and rule order; retain only relevant config, never dump full Git config/credentials. Pattern text alone is insufficient rule identity when lines repeat. Previously admitted files cannot disappear from protection merely because bytes stayed unchanged once. New exclusions may be equivalent only when their effects are proven confined to verified structural boundaries. A human statement that no hidden edits exist cannot substitute for coverage; a changed scope starts a separately observed baseline without blessing old hidden changes. Test negation removal, new hidden paths, policy-file edits, CLI/app environment differences and orphan worktrees. |
| M6 Git integration | detailed contract C6 written; tests pending | Reference and index updates can invoke hooks; ordinary Work acceptance must not need Git write authority. Separate content application from committing the destination workspace. Bind the complete candidate and preserve unrelated/partial staging. Refuse unsupported hooks/topology rather than silently bypass project policy. Journal expected old/new ref, candidate tree, index and working-tree preimages and postconditions; recover from actual states at every interruption. Commit ancestry alone is not completion and never authorizes rewriting a changed index. Other checked-out worktrees and cross-workspace content need explicit handling. C6 now defines the exact phase protocol and interruption matrix; executing its fault tests remains prerequisite to activation. |
| M7 launcher and Git discovery | accept, qualification pending | Use one managed per-user entry, independent of copied branch launchers, with a verified installation binding. Resolve Git once per observation context, record executable/version and relevant config provenance, and treat missing Git as a specific prerequisite failure. Avoid accidental CLT prompts during read-only diagnosis. Verify relative user-path resolution in each host rather than assuming shell expansion works everywhere. |
| M8 distribution trust | revise / Owner policy adopted | Recommend first-install trust explicitly limited to the authenticated official distribution entry, with update verification keys present in the first public installer. Sign versioned release/channel metadata and define expiry/freshness, last-seen sequence, authorized rollback, key rotation and recovery. A signed old index can still be replayed; signature plus version comparison is not complete freeze protection. OS signing/notarization is a separate trust and cost decision. No key generation, purchase or publication is authorized here. |
| M9 costs and refusals | design inventory and phase costs written | The prior test-name inventory and estimate were insufficient. The current RF map supplies 36 semantic families, source conditions/functions, retain/replace rationale and planned negative oracles across Python/distribution/native layers. The expanded scan has 2,289 syntactic sites, not independent rules; exact extraction/routing and its limits are preserved. The phase plan includes all capabilities: 50–75 activity hours, proposed stop limit 100. Per-port semantic verification remains implementation work. Freeze the accepted semantic oracle independently from the currently unaccepted usability changes. |
| M10 self-contained specifications | accept, document correction | Define desktop cases and structural topics in source, link the earlier product evidence supplement, and replace private verification-path shorthand with explicit private-evidence descriptions. Keep method/outcome/limits public; raw operations and provenance remain private. No need to import entire internal dossiers. |

## Recommended findings

| R2 recommendation | Driver treatment |
| --- | --- |
| R1 separate read/write compatibility | Accept the distinction. Unknown optional display data may be unavailable; unknown fields/kinds in an acceptance dependency cannot be skipped. Version minima alone do not prove compatible rollback. |
| R2 retain two runtime slots | Revise. Keep active, in-use and required last-recovery slots; two is not a hard maximum while older processes still use a slot. Cleanup failure is reported separately from activation success. |
| R3 Windows sync/antivirus | Include in platform qualification. Do not assert default backup coverage or diagnose antivirus from an unexplained lock error. |
| R4 provider interface | Accept as a design boundary only; do not build a speculative provider framework without a current consumer. Preserve required existing optional-execution ports. |
| R5 leaf size | Set explicit path/entry encoded limits; test every effective bound. Do not infer byte bounds are unreachable before the actual schema is fixed. |
| R6 authority inventory/delete | Keep discoverability and explicit data removal distinct from detach. Verify active bindings, references and recovery needs before deletion; no current deletion authorization. |
| R7 launcher cost | Include measured managed-launcher startup separately from model wait, content work and record operations. |
| R8 entry duplication | Reuse the observed payload auto-load issue; correct actual installed routing rather than removing a warning solely because a new path has not been observed. |
| R9 non-Git copies | Apply M1 identity/move/copy protections equally to non-Git roots. |

## Owner policies adopted together

Owner accepted all three policies on 2026-11-06: “세 정책을 설계 기준으로 채택”. This is design-policy acceptance, not permission to change this Mac, install a candidate or generate keys. Detailed format activation and implementation results remain separate.

1. Data location and permissions: keep each project's records under the OS user-data area, independent of Git worktrees. Ask once per relevant host/project for the narrow necessary access when the host supports it. Show the paths, purpose and removal method; honor managed restrictions. If the host cannot express it, report that combination as constrained instead of broadening access. Detach revokes only Colvia-owned grants no longer required by another binding.
2. Data preservation: explain that Git push/clone does not carry Colvia's records. Provide verified versioned export/import of records, bodies, settings and acceptance history, plus local pre-update recovery. Off-device backup remains a separate user destination. Preserve first-public data across supported updates.
3. Distribution trust: include update-signature verification from the first public release, with a defined signing-key lifecycle and freshness/rollback policy. Treat initial HTTPS acquisition and platform execution warnings honestly. Defer any paid OS-signing choice to a concrete cost/benefit decision.

With these policy decisions recorded, the detailed M4/M5/M6 contracts and M9 refusal/capability accounting have now been written in the closure below. Review the resulting specification and confirm the applicable implementation budget before scheduling product implementation. Existing implementation authorization is retained; it does not replace detailed contract closure or execution-limit decisions. Do not restart measured scale tests, current apps or installations merely to process the review. Host permission probes remain separately authorized real-environment work.

## Checked official references

Checked 2026-11-06; documentation evidence, not product reproduction:

- [Codex protected paths](https://learn.chatgpt.com/docs/agent-approvals-security#protected-paths-in-writable-roots): default workspace-write protects Git directories, pointer files and resolved gitdir recursively. This supports withdrawing an unconditional writable common-dir store, not a universal claim about every custom permission mode.
- [Claude Code sandbox configuration](https://code.claude.com/docs/en/sandboxing#configure-sandboxing): documents specific additional writable paths and managed-policy limits. Desktop propagation and each target OS remain untested here.
- [SQLite cache spill](https://www.sqlite.org/pragma.html#pragma_cache_spill): spilling dirty pages can acquire an exclusive lock. Staging limits transaction size but does not eliminate all reader/writer contention.
- [SQLite online backup](https://www.sqlite.org/backup.html): external writes can restart incremental backup and prevent completion if repeated; this is not a claim that the backup API always fails.
- [Git hooks](https://git-scm.com/docs/githooks): reference transactions and index writes have hooks. Low-level Git commands are not inherently hook-free.
- [Git configuration](https://git-scm.com/docs/git-config): Unicode precomposition, case and filemode behavior depend on configuration/platform; a default must not replace observed filesystem identity.


## Detailed-contract closure · 2026-11-06

The Owner requested the remaining contract, refusal inventory and capability costs together. [C1–C8](implementation-contracts.md), [RF map](refusal-map.md) and [phase plan](implementation-plan.md) are the resulting source-owned specification. They replace the intake's open algorithm/estimate placeholders, not the verbatim reviewer response or historical evidence.

| Finding | Written decision | Still not proved |
| --- | --- | --- |
| M1 | C1 OS-data authority, verified binding/copy/move/restore, narrow host access | Actual four host forms and three OS/architectures |
| M2 | C3 complete pinned root + C4 versioned framed export/restore | Fault tests, off-device recovery procedure |
| M3 | C3 1 MiB staging + short final publication, bounded busy failure | Real latency/durability/platform behavior |
| M4 | C2 canonical paths/objects/Node(S,d), C3 numeric guards | Properties, alias/race/platform tests |
| M5 | C5 conservative D7 proof and explicit policy-edit union | Real app patterns and hidden-path counterexamples |
| M6 | C6 full candidate, preserved staging, ref/index recovery matrix | Git fault/concurrency/native execution |
| M7 | C7 managed entry and verified runtime/Git selection | Actual installed CLI/app permissions |
| M8 | C8 standard update metadata and Colvia activation policy | Pinned verifier dependency, production key custody/domain and channel qualification |
| M9 | RF semantic map + all-phase cost estimate | Each changed guard's ported oracle and measured implementation cost |
| M10 | Source-owned cases/contracts/maps and relative links | Final packaged documentation qualification |

No claim that R2's mandatory findings are all executed and passed. The design output is reviewable; changing actual settings, installation, key generation, committing and publishing remain withheld. Production operations inputs cannot be fabricated merely to close a document checkbox.
