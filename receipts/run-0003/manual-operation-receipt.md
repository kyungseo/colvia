# Run-0003 Manual Operation Receipt

## Identity And Claim Boundary

- Run: `run-0003`; Owner accepted the bounded private minimum production vertical result on `2026-08-09`.
- Implementation: `HV2-REPO-IMPL-001`, `main` unborn, commit `0`, remote `0`.
- Target: `HV2-REPO-TARGET-run-0003`, fresh disposable private Git root.
- Authority home: `7d854f54-6538-4cd4-8961-2e2f50ef9653`.
- Payload SHA-256: `86224066abe04e28a49a2d33f32d9b343ca8ad0552d2d540f39a43270b331717`.
- Public/default/adopter/runtime support/TD-ACC/three-arm/population/power-loss claims: `0`.
- Physical session locators are normalized below to logical repository roles and are not durable identity.

## Tool Inventory

- `CPython 3.14.6`, stdlib only; `PYTHONPATH=src`.
- Local Git; target commits only, implementation commit/remote `0`.
- Provider adapter/transcript: not used as evidence.
- Auditor: `python3 -I`, general-purpose stdlib + Git only; project source/CLI/tests/transcript not provided.

## Literal Command Ledger

`cwd=HV2-REPO-IMPL-001`; `<TARGET>`=`HV2-REPO-TARGET-run-0003`, `<RELEASE>`=`release-0002`,
`<CAPSULE>`=`HV2-MPV-AUDIT-CAPSULE-run-0003`, `<DURABILITY-SCRATCH>`=`HV2-DURABILITY-SCRATCH-run-0003`.

The ledger begins at the admitted implementation and target boundaries. Before row 3, `<TARGET>` existed as an empty directory except
for `README.md`; its historical construction command was not captured and is not claimed as a literal ledger row. The admitted README is
151 bytes, SHA-256 `d168fa650c3881e59724e135fceae2b89cca051ec47a7237192ac9d870f43d53`, and remains recoverable from
root commit `472354edaf98fd7b6c98dc8d181adf30ad0f7c0c`. Rows 3~29 are the literal commands actually recorded.

| # | Cwd role | Literal command after locator normalization | Exit | Result |
| --- | --- | --- | --- | --- |
| 1 | implementation | `PYTHONPATH=src python3 -m unittest discover -s tests -v` | 0 | historical run `43/43`; R2 bounded-remediation suite `48/48` pass |
| 2 | implementation | `PYTHONPATH=src python3 -m hv2ref.cli build-release --source docs/GENERATION-1-CONTRACT.md --output <RELEASE> --seal receipts/run-0003/run-seal.json` | 0 | carrier `9789321ee695609cb179c4bbf16dab7e9afb2b1c7de12ae9fb6d322c53045b7c`, payload `86224066abe04e28a49a2d33f32d9b343ca8ad0552d2d540f39a43270b331717` |
| 3 | target | `git init -b main` | 0 | fresh private Git root |
| 4 | target | `git config user.name 'Harness v2 Local Fixture'` | 0 | local fixture identity |
| 5 | target | `git config user.email 'harness-v2-fixture@example.invalid'` | 0 | non-routable address |
| 6 | target | `git add README.md` | 0 | initial boundary staged |
| 7 | target | `git commit -m 'fixture: run-0003 disposable target을 초기화한다' -m 'Fresh B1 rerun의 target repository boundary를 구현 저장소와 분리한다.' -m 'Co-authored-by: Codex <noreply@openai.com>'` | 0 | root commit with Codex trailer |
| 8 | implementation | `PYTHONPATH=src python3 -m hv2ref.cli init-target --target <TARGET> --authority-home-id 7d854f54-6538-4cd4-8961-2e2f50ef9653 --item-id item-0001 --observed-at 2026-08-09T09:01:00Z` | 0 | generation 1 initialized |
| 9 | implementation | `PYTHONPATH=src python3 -m hv2ref.cli transition --target <TARGET> --item-id item-0001 --operation create --sequence 1 --observed-at 2026-08-09T09:02:00Z --actor OWNER-LOCAL-001 --release <RELEASE>` | 0 | revision-0001, binding complete |
| 10 | target | `git status --short` | 0 | `.harness-v2/`, `docs/` unfinalized |
| 11 | target | `git check-ignore -v .harness-v2/staging/attempt-create-0001/inventory.json` | 0 | ignored by project `.gitignore` |
| 12 | target | `git add .harness-v2 docs/GENERATION-1-CONTRACT.md` | 0 | canonical binding staged, staging excluded |
| 13 | target | `git commit -m 'fixture: run-0003 create binding을 finalize한다' -m 'Payload digest와 release/result/acceptance/binding receipt를 함께 보존한다.' -m 'Co-authored-by: Codex <noreply@openai.com>'` | 0 | create finalized |
| 14 | implementation | `PYTHONPATH=src python3 -m hv2ref.cli transition --target <TARGET> --item-id item-0001 --operation update --sequence 2 --observed-at 2026-08-09T09:03:00Z --actor OWNER-LOCAL-001 --inject-at after_pointer_assertion` | 75 | persisted in-process abort; active remained revision-0001 |
| 15 | implementation | `PYTHONPATH=src python3 -m hv2ref.cli resume --target <TARGET> --item-id item-0001 --operation update --sequence 2` | 0 | exact tip resume to revision-0002 |
| 16 | target | `git add .harness-v2` | 0 | interruption/resume/binding bytes staged |
| 17 | target | `git commit -m 'fixture: run-0003 interrupted update를 resume한다' -m 'Persisted interruption과 resume record로 prior pointer 보존과 exact tip continuation을 증명한다.' -m 'Co-authored-by: Codex <noreply@openai.com>'` | 0 | resumed update finalized |
| 18 | implementation | `PYTHONPATH=src python3 -m hv2ref.cli transition --target <TARGET> --item-id item-0001 --operation rollback --sequence 3 --observed-at 2026-08-09T09:04:00Z --actor OWNER-LOCAL-001 --rollback-revision revision-0001` | 0 | digest-bound forward rollback revision-0003 |
| 19 | target | `git add .harness-v2` | 0 | rollback bytes staged |
| 20 | target | `git commit -m 'fixture: run-0003 forward rollback을 finalize한다' -m 'Previously selected completed revision을 digest-qualified source로 결속한다.' -m 'Co-authored-by: Codex <noreply@openai.com>'` | 0 | rollback finalized |
| 21 | implementation | `PYTHONPATH=src python3 -m hv2ref.cli transition --target <TARGET> --item-id item-0001 --operation detach --sequence 4 --observed-at 2026-08-09T09:05:00Z --actor OWNER-LOCAL-001` | 0 | logical detach revision-0004 |
| 22 | target | `git add .harness-v2` | 0 | detach bytes staged |
| 23 | target | `git commit -m 'fixture: run-0003 logical detach를 finalize한다' -m 'History와 payload를 보존하며 plain continuation으로 전환한다.' -m 'Co-authored-by: Codex <noreply@openai.com>'` | 0 | detach finalized |
| 24 | implementation | `PYTHONPATH=src python3 -m hv2ref.cli verify-state --target <TARGET> --item-id item-0001` | 0 | pass, detached, record 57, staging 4/4 sealed |
| 25 | implementation | `PYTHONPATH=src python3 -m hv2ref.cli durability-probe --root <DURABILITY-SCRATCH>` | 0 | Darwin fsync/fullfsync/directory cleanup pass |
| 26 | capsule | `git clone --no-local <TARGET> target` | 0 | fresh tracked projection |
| 27 | capsule target | `git remote remove origin` | 0 | host locator removed before audit |
| 28 | capsule | `python3 -I auditor-procedure.py` | 0 | blind audit pass |
| 29 | capsule | `python3 -O -I auditor-procedure.py` | 1 | optimized mode fail-closed |

All five target commit messages contain `Co-authored-by: Codex <noreply@openai.com>`. Final target is clean, commit count `5`,
HEAD `d6d354a45786b451ee7c61859baff154213a8681`, tree `27f9883aec817575bf29aecd1c994131f415564a`.

## Pre-Run Correction

The first build-release admission rejected the full run seal with `HV2-CARRIER-SEAL` before creating `<RELEASE>`. The seal
validator was corrected to require the four carrier keys, accept only the three known run-allocation keys, and reject all
unknown keys. The suite returned `43/43` before the successful command in ledger row 2. No target or release bytes existed at
the failed admission point.
