# P0–P3 source checkpoint

Status: source implementation and focused verification; P3 result review completed with bounded Driver corrections. The new format is not active in an installed product. Existing installation, runtime and project records have not been replaced.

## Implemented slice

The new `src/colvia` package owns immutable storage, connection identity, POSIX/Git observation and ordinary Work services. `src/hv2ref` remains the old installed composition until the later feature/lifecycle integration steps. This is a staged replacement, not two authoritative stores or dual writes.

- One plan approval covers the named edit and checks through review submission. Result acceptance is a separate single decision bound to the shown result. Receipts are internal identifiers, not proof that a person agreed.
- Submission retains original and submitted bodies. Rework keeps old results, archive changes visibility without deleting bodies or decisions, and historical content can be read without relying on the present file or a Git commit.
- Different Work heads retain separate decisions. Candidates and follow-up choices neither start work nor accept a result. Paged lists refuse a stale cursor rather than silently mixing versions.
- Verified Git workspaces share one project authority and have distinct workspace identity. Nested app workspaces require actual Git registration and Colvia identity; their directory names alone confer no exemption. Both a proved parent exclude and an exact child exclude are covered. Previously protected paths remain in the comparison after a policy edit.
- Unchanged symlinks and supported submodule entries coexist with ordinary files as opaque protected entries. Editing them, traversing them as ancestors, or hiding dirty submodule content remains unsupported/refused.
- The source-only command entry is explicit. It does not install itself, select a Python from PATH on behalf of a public user, or qualify a future managed runtime. CLI serializers handle repeated criteria and canonical records without an agent-written JSON script.

## Executed coverage and remaining boundaries

The tests below are repository-owned synthetic checks. They do not replace the existing RF family requirements or mark future platform rows passed.

| Boundary | Source checks | Limits / later owner |
| --- | --- | --- |
| RF-01/06/07: typed bytes, fixed roles, canonical maps/trees, selected/full graph validation | `test_foundation_codec`, `tree`, `maps`, `graph`, `schemas`, `backup` | Whole public lifecycle import/restore integration remains P7 |
| RF-02/03/04/05/13: no-follow identity, registered topology, policy and opaque observations | `test_foundation_binding`, `connection`, `observation`, `observe`, `policy`, `git`, `opaque`, `entry` | POSIX implementation; Windows native handles/reparse behavior and actual managed entry are not qualified here |
| RF-08/09/10: plan approval, exact submitted result, rework and old bodies | `test_foundation_work`, `work_git`, `cli` | Ordinary Work only; delegated worker acceptance/application is P4 |
| RF-11/36: atomic publication, read-set CAS, process crash, journal recovery, generation fencing | `test_foundation_store`, `store_faults`, `processes`, `generation`, `review` | Synthetic failures do not prove every filesystem or power-loss behavior |
| Candidate/follow-up and RF-35 human/agent command boundary | `test_foundation_planning`, `cli` | Human output is short; model compliance and installed adapters need later behavior qualification |
| Worker/umbrella, formal execution, delivery, updater/signing/Git integration | Existing RF requirements and prior evidence retained | P4–P9, not implemented or waived by this checkpoint |

Before P3 review, all 146 foundation tests passed in normal and optimized source runs. The final reviewer corrections and cumulative counts are recorded in the owning Work and [Driver disposition](review-p3-work-disposition.md). The checks are one cumulative run of the changed common layer, not a repeat of unrelated existing notification/packaging suites.

## Source scale observations

This synthetic Mac source run uses plain folders, one small changing report, stable input files, and the same retained authority through all Work steps. It includes no model calls. Times are service execution, not installed process startup or user dialogue. Earlier Git-based measurements used another path and must not be represented as an exact speedup ratio.

| Files / completed Work | First → last six Work steps | First → last selected query | Selected object loads | DB bytes at end |
| --- | ---: | ---: | ---: | ---: |
| 100 / 69 | 0.286 → 0.419 s | 9.4 → 12.7 ms | 17 → 17 | 8,577,024 |
| 1,000 / 1 | 1.926 s | 13.9 ms | 18 | 561,152 |
| 3,000 / 30 | 4.202 → 4.278 s | 18.6 → 20.8 ms | 18 → 18 | 5,758,976 |

The six steps are plan, approve, start, submit, review and accept; submit also prepares the review result. Query counts are calls through the immutable object loader, not disk-I/O counts. Each run is a single diagnostic sample, not a latency percentile or public capacity/SLA. The 1,000-file row contains one Work, not 30.

The first new-source measurement exposed repeated wide map nodes. Changing the unactivated persistent key maps to canonical radix-16/leaf-16 reduced the same 100/69 DB from 17,981,440 to 8,577,024 bytes and 3,000/30 from 7,847,936 to 5,758,976 bytes. File-tree structure and body retention did not change. The original results remain in private evidence. Some source checks overlapped the first timing run; space comparison is exact for these fixtures, timing is diagnostic only.

The authority still grows with retained decisions, metadata and unique bodies. Archive does not reduce storage. These figures are not compressed Git history size, unique APFS physical allocation, or a long-term storage guarantee. Large unique binary content, storage pressure and installed Git-based workloads remain explicit P7/P9 verification items.

## Host evidence transfer

Earlier narrow source probes passed CLI primary/sibling and Claude desktop primary/sibling/nested cases. Codex desktop now has bounded source-helper passes in primary, sibling and nested workspaces: the primary result was reused, and the latter two passed after the synthetic instructions were aligned with the exact Owner authorization. Each actual permission response granted write access to one synthetic authority directory for one turn, with no network grant. The base workspace permission profile and automatic approval review remained active; the fixed helper ran with default sandbox permissions. The project-local permission-request feature flag and temporary instructions were restored after the probes. Earlier denied requests and a Driver preparation failure remain preserved. This is not installed managed-launcher, clean-user, permanent-access or negative-isolation qualification. No target host is silently removed from the matrix.

The next integration steps consume this package through ports; they must not bypass connection identity, fixed reference roles, exact result acceptance or whole-tree scope protection to simplify adapters. Raw logs, first failures and diagnostic fixtures remain private for review and installed qualification; product contracts and sanitized findings stay in the owning repository.
