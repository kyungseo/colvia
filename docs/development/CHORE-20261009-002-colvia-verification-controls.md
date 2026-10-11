# CHORE-20261009-002: Colvia Verification Controls

Date: 2026-10-09
Disposition: Owner accepted bounded P1a result; actual-result R1 found no blocker and controls11 are frozen. Authorized C1 P1b/P2 implementation is active; no product result acceptance, activation or Git actions.
Owner: Human Owner
Driver: Codex
Reviewer: Claude only through separately authorized review

## Scope And Authorization

The Owner replied “승인” to P0a: write inspectable runner, isolation policy and verification procedures without executing them, and prepare the two remaining policy choices. This authorizes controls authoring and static document/syntax/input checks only. It does not authorize test imports/discovery, acquisition, canaries, runner execution, product/runtime/test-source edits, a new reviewer invocation, result acceptance, contract activation, source Git operations or adopter application.

This is the one source-owned progress record for this bounded task. IDs in the current tree and retained Git history across refs were checked before allocating the next shared date sequence 002. This is a plain development document, not a runtime Work. [Implementation-plan R0](colvia-entry-implementation-plan.md#implementation-plan-r0-record) remains the exact historical review input; its SHA-256 at handoff is `862a57d47c42e20f1e1a56ff6ec426dce8f5e7c74610fccba73fdbf200207f02`. [DR-0004](../decisions/DR-0004-colvia-managed-entry-and-one-way-transition.md) remains Accepted with activation pending. C0 stays closed.

Base: `238514686078ce1564010a7b69013f48a635c57c`; existing Development Index before navigation SHA-256 `ae698d1b83ce710a67bf727668c0eceed77ba356fd67cf61358369fbed6045d6`. The selected scope is a direct bounded source request; it does not select the broader Public Preview intake. The index receives only a link to this record.

## Authorized Plan And Completion Criteria

1. Author controls outside the managed inventory and default unittest discovery, under [verification/colvia-entry](verification/colvia-entry/README.md). Freeze baseline source/blob/path identities without extracting or executing it.
2. Make execution modes, inputs, environment, working directory, runtime/Git identities, output boundaries and budgets concrete. Keep OLD, SOURCE and controls read-only to child tests; acquisition has a separate narrow policy and fixed offline commands.
3. Specify real collection versus factory IDs, base smoke, refusal controls, numbered physical-prefix and late-lock evidence requirements. Do not invent new implemented tests or claim unsupported sandbox rules work.
4. Propose exact retired-entry diagnostic and fresh-init collision choices for Owner decision. No DR amendment or choice is accepted by this task.
5. Statically check Python syntax without imports/execution, JSON consistency, local references, GFM rendering, disclosure, whitespace, input preservation and controlled write scope. Preserve review-ready exact files outside the checkout and prepare P0b fixed input.

Risk: L3 controls for later mutating validation. P0a is reversible source-only authoring. A syntactically valid policy is not proven isolation; no runtime result can be claimed. Stop on contract/scope expansion, source drift, unsafe destination or unavailable exact input. P0c budgets remain proposed in the reviewed plan and must be fixed against actual controls before execution approval. Do not create an execution directory during P0a.

## Progress And Remaining Gates

Authoring started under the explicit P0a approval. The actual control files and remaining policy options below will be recorded here. P0b must review exact controls; P0c needs separate authorization, canaries and base checks, runner result review and Owner acceptance before product implementation.

## Prepared Controls And Proposed Decisions

Controls are now authored under [verification/colvia-entry](verification/colvia-entry/README.md), outside the 29-file managed set and `tests/` discovery. They cover fixed-mode dispatch, per-run write isolation, offline fixed-blob acquisition, occurrence-preserving real collection, 20 baseline seed IDs, result/failure retention, instrumented old-lock/new-prefix observations and 19 numbered expected operation groups. The future entry-1 test factory and actual runtime implementation are not authored in P0a. Missing future inputs produce an error, not a skip.

Observed read-only host identities: macOS 27.0.1 arm64; final GIL-enabled CPython 3.14.7 SHA-256 `87d4df53fd91304be5bac391fb204643c36b7df2023c04a0953bcbc7d4fdf634`; Git 2.54.0 (Apple Git-157) real-binary SHA-256 `a73bf622a2e470d5d57a4b1d5aef1e8680e67278018d4858a2f93825b7d595c7`. These identify proposed tools and do not qualify controls, the OS or a new release.

### D1 — Retired Entry Diagnostics

The choice applies only when the entry-1 binding/product and ordinary record observations would otherwise be valid. Unknown/damaged/unsupported/pending state retains its existing non-pass classification and precedence; collision information must not mask it. In every option, lifecycle update/rollback/init replay/repair/detach refuse with existing `HV2-WORKSPACE-PRODUCT` and exit 65 before mutation, preserve the hv2 occupant, and never execute or exclude it. Ordinary Work/intent/candidate paths retain normal live-content proof and remain independent of this diagnostic classification.

| Option | Exact proposed observation | View/consumer consequence |
| --- | --- | --- |
| D1-A — recommended | status/doctor and ordinary view use existing `classification: conflict`, exit 12; retain verified product/binding, add `lifecycle_ready: false`, `retired_entry_collision: {path: hv2, ownership: project, preserved: true}`, precise next_action | View keeps readable Work/intent/candidate content after fresh graph checks, plus visible lifecycle conflict. Machine callers receive nonzero instead of mistaking the installation for clean |
| D1-B | Same fields/binding with existing `classification: degraded`, exit 10 | Current view excludes detailed Work/intent rendering for degraded state; ordinary record writers still keep the H-A rules. Less useful read-only diagnosis, but smaller classification routing change |

Recommend D1-A. Existing `cli.main` maps conflict→12; view's EXITS agrees and its read path does not suppress conflict as it does degraded. Add the collision/readiness fields to displayed status rather than leaving them only in JSON. The default runtime verifier must stay separate from lifecycle collision admission, preserving accepted H-A behavior. This is a proposed C2 diagnostic choice, not a new persistent lifecycle state or accepted contract change. Owner has not selected it.

### D2 — Fresh Init With Existing hv2

This is a previously unspecified admission case, distinct from hv2 reappearing after migration. Neither the private source rename nor P0a decides it. Existing colvia collision rules remain unchanged. For each option inspect all root occupants and aliases under the same path/topology rules; never delete or rename user content automatically.

| Option | Exact proposed behavior | Cost |
| --- | --- | --- |
| D2-A — recommended | Refuse fresh entry-1 init when any root hv2 occupant or NFC/casefold alias exists, before the first init receipt or root mutation; `HV2-WORKSPACE-PRODUCT`, exit 65, preserve bytes and explain separate operator disposition | Adds a narrow first-init admission restriction; requires a named DR-0004 amendment/Owner acceptance before code, not an inferred interpretation of reappearance |
| D2-B | Permit fresh init while preserving hv2 as ordinary project content; only colvia is managed. Successful init must immediately disclose lifecycle-blocked collision using selected D1 classification/exit and verify product/truth preservation | Installation immediately needs file disposition before later lifecycle operations; exact init-result success/replay meaning and additional normative clauses must be settled before implementation |

Recommend D2-A for a consistent first-slice entry path. Root file/dir/symlink/alias and Git-index edge cases need named positive/refusal tests under the chosen policy. No option changes .hrn, HV2-, record identities, completed history or automatic Work/Git behavior. Present the exact amendment text only after Owner selection; do not rewrite the accepted A record during this authoring task.

### Remaining Execution Gates

P0a authoring does not accept D1/D2, activate DR-0004 or authorize P0b/P0c. Next concrete review is a fixed no-tool P0b packet covering actual controls and their invocation/input identity. P0c would then require separately approved acquisition/canary/collection/base smoke, with the deterministic collection-hash binding step explicitly included. Actual policy validity, system service allowances, fd observation feasibility, test multiplicity and runtime duration remain unverified. If any fails, preserve the precise observation and propose one bounded correction; no broad permission switch or automatic retry.

## Authoring Result And Static Checks — 2026-10-09

The 12 control/data/guide files below are authored. Six Python files passed AST syntax parsing without import or execution; three JSON files parsed and their identities/relationships were checked. Two policies passed balanced-form inspection only; no SBPL compilation or effective sandbox validation was performed. Twenty existing seed IDs were located statically, not collected. The 19 numbered prefix groups are a proposed independent oracle, not executed cases. Observer self-canaries were also authored for fd events, a one-byte interrupted write and parent-held lock witnesses on fixed non-product bytes; they have not run.

The 101 fixed Git blob identities were read and matched without reconstructing OLD. Literal 27/28/29 path hashes match C0; independent canonical-inventory computation matches the single checkout-1 predecessor release hash. All 29 managed source files remain byte-identical to the base. DR-0004 acceptance bytes are unchanged. No product/runtime/test source, accepted contract or real installation changed.

GFM rendering, local links, disclosure and whitespace checks passed. The Development Index changed only by one task link after its existing protected/navigation content, from `ae698d1b83ce710a67bf727668c0eceed77ba356fd67cf61358369fbed6045d6` to `d24e74882a6d79813379a70c0161e83f49b8cacbd71e0cb00793a34f3b4120ab`. The prior implementation note gained only the dated handoff pointer; its pre-handoff exact bytes remain in the preserved R0 record. No central status or duplicate progress ledger was edited.

| File | SHA-256 |
| --- | --- |
| [README.md](verification/colvia-entry/README.md) | `32b92e12721b09b6f1f1c2fe375816c0378c7f64fe7800fe1abd5455fe472948` |
| [acquire.py](verification/colvia-entry/acquire.py) | `e42d9955fa071e676219d083a2c95f4319715a17045b1d8c740e407adbd38dfb` |
| [acquire.sb](verification/colvia-entry/acquire.sb) | `2d35bb94c4e42078b5f8c47d9f4009ad690112fc3217bea3401d8ba29563521e` |
| [base-seed-ids.json](verification/colvia-entry/base-seed-ids.json) | `4e20e8cfc3e7ace2580067a7218ea0705a6c6398d2feba158e93036b6695ca06` |
| [baseline-inputs.json](verification/colvia-entry/baseline-inputs.json) | `f1ee1072b0e1cfe8cef92a44a84ab2c7c107eae05998ce0b191d7826c3f4c199` |
| [canary.py](verification/colvia-entry/canary.py) | `11007ce3c4f31f063579a0165d1e58e95163f28891c4116b39c279290225652f` |
| [common.py](verification/colvia-entry/common.py) | `862884854c80f5d79da45d651ec67e8eb53e9c165c3f8458fe8158a52f3c1c8a` |
| [controller.py](verification/colvia-entry/controller.py) | `536bc4736d0a92b5f29e2eb7d534605ada427226056ff5b3c76ab27fd1113365` |
| [observer.py](verification/colvia-entry/observer.py) | `2fb8a12bca7fd8e7e2db9d5a03cd81e88b9b5970d3788dae1ba58dfc845e4f39` |
| [prefix-oracle.json](verification/colvia-entry/prefix-oracle.json) | `b970150691d7986607239aff7bd56a84546382d31ef3c9dc44cc29a52b546b9b` |
| [runner.py](verification/colvia-entry/runner.py) | `e690b5364492255d74ecc31f21413525642fb0c36c88d4d1fffa75f8b2aa8483` |
| [test.sb](verification/colvia-entry/test.sb) | `785dbfa0631996e84a32d08b57113b78f0d3bb2ac79ae54a749c39eeabea1aad` |

### Completion Criteria Disposition

| Criterion | Observation and limit |
| --- | --- |
| Inspectable controls outside shipping/discovery | Authored 12 files; no packaging or public support change |
| Fixed commands, inputs and boundaries | Authored fixed mode/slot dispatcher, private resolved base invocation and read-only OLD versus per-run output policies; policy execution unavailable |
| Test/oracle specification | 20 static base IDs, mandatory future factory interface, 19 prefix groups and instrumented witnesses specified; actual collection/factory/schema1 fixture/production proof remain later gates |
| Policy choices | D1-A and D2-A recommended; neither selected or applied |
| Static checks and preservation | Passed the bounded checks above; review-ready exact files and input retained outside the active checkout with readback |

P0a authored output is ready for review, not accepted as completed execution work. The next proposed P0b is one fresh no-tool review of actual controls and the bounded base execution proposal. To avoid pretending one review label silently fulfills another, request explicit Owner authorization to combine P0a authored-result R1 with P0c execution-plan R0, with separate conclusions. This does not combine or waive the later post-execution runner-result R1. The authoring approval itself covers no new review transmission or execution.

Custody consumer: P0b reviewer/Owner and subsequent exact-controls/base-verification handoff. Keep the original fixed review inputs and final authored files until their identities are referenced by the approved next phase and Git or equivalent custody preserves the necessary bytes. Static render/check outputs and one-off authoring scripts are reproducible, not permanent deliverables. The proposed non-Git execution root is absent; no worktree or fixture was created. Keep the current source worktree for this concrete near-term review/implementation use; no checkout is eligible for retirement now.

## P0b Combined Review Attempt — 2026-10-09

### Actual Owner Authorization And Request

The Owner replied “승인” to one fresh no-tool Claude subscription review, bounded to 600 seconds, explicitly combining the P0a authored-controls result R1 and the P0c base-execution plan R0 with separate conclusions. The reason for combining them was that the same concrete controls are both the authored result and the input to the proposed base execution. This did not combine or waive the later post-execution runner-result R1. The Driver was to record the response and dispositions and stop; correction, a further review invocation, test execution, D1/D2 selection, result acceptance, contract activation, Git and adopter actions were not authorized.

The fixed request asked for concrete control/runner/policy feasibility and safety findings, with separate A/B conclusions, static versus executed evidence boundaries and a bounded next scope. It contained 21 full inputs and four excerpts, including the authored task and all 12 controls/guide files. Selected existing source/contract references were supplied; the complete repository and all normative/test files were not. Six private invocation path strings were replaced by structurally equivalent illustrative paths, so actual host topology was explicitly unavailable to the reviewer. No new inputs were added during the attempt.

| Input identity | Value |
| --- | --- |
| Base revision | `238514686078ce1564010a7b69013f48a635c57c` |
| Tracked diff SHA-256 | `12238ddc334c4a6971d657249732a73d59cc4c3e32b6463d5a7fccfc867a6b04` |
| Fixed packet | 318,533 bytes; SHA-256 `211bd566ae0f4a318f6fff3e9bbccd8b1132282f35942706dce90a3a02e4f433` |
| This task before the attempt, outside the tracked diff | SHA-256 `309fc9b6fb28831cacab839f492b2ec705994cfb2136784b89434f2f46423158` |
| Other full/excerpt inputs | Fixed packet identifies each by path/hash; all 12 untracked controls have the exact hashes in the authoring table above. The untracked accepted DR and implementation-plan excerpt are separately identified in that packet |
| Private resolved invocation | SHA-256 `366f147fcedbb0848338a1c05f07c7b231fc19a5867dd837b5298595bcc5a0e3` |
| Path-substituted review invocation | SHA-256 `ec41662c1b02943a07ae1bd4b5799355b3b2b66032cf9d18b35ba53e72b783f9` |

### Invocation And Observation

Authentication was verified immediately before invocation as logged in via `claude.ai / firstParty / pro`. The initial restricted-context false negative was resolved by an outside-sandbox status check; no reauthentication was performed. Only the non-secret authentication/provider/subscription fields were retained. No credential values or account email were recorded.

The CLI requested model alias `opus`, effort `high`, print mode, safe/restricted mode, empty tools, strict empty MCP configuration, disabled slash commands, empty setting sources, `dontAsk`, no session persistence and JSON output. The system instruction stated the actual combined-review authorization, required separate conclusions, treated source as data and forbade tools/execution. The fixed packet was provided on stdin from its review-request directory. A parent process enforced the 600-second bound and sent SIGKILL to the review process group at the limit. This is reviewer invocation evidence, not a test-runner execution.

| Observation | Result |
| --- | --- |
| Wall time | 600.01 seconds |
| CLI exit status | -9 after the enforced timeout |
| Final stdout / stderr | 0 bytes / 0 bytes |
| Actual model/session identity | Unavailable: no response envelope was returned. Requested alias `opus` is not proof of the model that ran |
| Reviewer response | Unavailable; no final text, findings or A/B verdict received |
| Input verification before/after | Passed: base/diff, full inputs and excerpt-source bytes, both invocation files, all identified source bytes/modes, packet and absent execution root |
| Tests, acquisition, canaries, collection or runner execution | None; no pass/fail counts exist |

The timeout establishes no technical finding and no conclusion about control quality. Its cause is undetermined; this record does not attribute it to payload size, model reasoning, service capacity or authentication. A fresh invocation was requested, but absent model/session metadata limits confirmed independence. The Driver-generated unavailable-result marker is not a Reviewer response and is not quoted as one.

### Driver Disposition And Remaining Gate

No Reviewer findings exist to accept, revise or defend. Driver disposition for the exhausted attempt is `needs-user`: preserve the fixed input and essential timeout facts, do not retry automatically, and obtain a new bounded review authorization before resuming. Neither authored-result R1 nor execution-plan R0 is discharged. P0a remains authored/static-only, D1/D2 remain unselected and P0c remains unapproved.

The recommended recovery proposal is one further fresh no-tool subscription review of the same 318,533-byte packet, at most 600 seconds, using the same A/B scope and invocation restrictions. Keep the original packet byte-identical; identify this post-attempt record as intentionally absent from that historical review input. A successful response would be recorded verbatim with separate Driver dispositions before stopping. A second timeout, auth-path mismatch, input drift or required scope expansion ends the attempt without further retries or execution. This is a proposal, not an authorization. The initial P0b allowance is consumed.

Custody consumer: Owner review-recovery decision and the next explicitly authorized controls review. The previously retained authored/input copy preserves the pre-attempt bytes. Preserve this updated task and compact authorization/timeout metadata outside the source checkout with readback; these identify the new checkpoint without creating a new source-tree snapshot. Retain the fixed packet/invocation inputs for that next consumer. Empty stdout/stderr files and the Driver-generated unavailable marker have no unique Reviewer content and need not become permanent review artifacts. Keep the source worktree for this concrete near-term review recovery; no worktree cleanup is eligible. Product/runtime/controls, accepted decisions, navigation and central status remain unchanged by this record update.

## P0b Reauthorized Attempt And Narrower Recovery — 2026-10-09

### Owner Authorization, Fixed Input And Invocation

After the first timeout report and the explicit proposal for one further same-input review bounded to 600 seconds, the Owner replied “승인”. This authorized exactly one additional fresh no-tool subscription review of the same combined P0a R1/P0c plan R0 packet, followed by recording and stopping. It did not authorize a third invocation, input/scope expansion, corrections or execution.

The second invocation sent exactly the original 318,533-byte packet with SHA-256 `211bd566ae0f4a318f6fff3e9bbccd8b1132282f35942706dce90a3a02e4f433`. It deliberately retained this task's historical pre-attempt bytes. The known timeout checkpoint, SHA-256 `74c4df1a4b991f1eaa66092dc3b206cf7bb6ba31e7e38b6854594c6c8a16fb87`, was verified locally and was not added to that fixed input. All other reviewed full inputs, excerpt-source bytes and resolved/substituted invocation identities were unchanged. This is an explained record-only difference, not evidence that changed controls were reviewed.

Immediately before invocation, non-secret authentication again confirmed logged-in `claude.ai / firstParty / pro`. Requested alias `opus`, effort `high`, tool/MCP/settings/slash-command/session-persistence restrictions, fixed stdin and the 600-second process-group timeout matched the first attempt. The new invocation used its own request/output directory. No account email or credential values were retained.

### Observed Result And Driver Disposition

The second attempt also reached 600.01 seconds and exited -9 after the enforced process-group SIGKILL. Stdout and stderr were both empty. No final Reviewer response, findings, A/B verdict, actual model or session identity was available. This is a second unavailable review, not a repeated technical finding or a failed product test. The cause remains undetermined. The before/after input check passed; the proposed execution root remained absent and no controls, acquisition, canaries, collection or tests ran.

There are still no Reviewer findings to disposition. Driver response to the exhausted attempt is `needs-user`: stop identical retries and propose a smaller review boundary. Both authorized attempts are consumed. The authored result R1 and base-execution plan R0 remain undischarged; D1/D2 remain unselected. No new policy, product contract, result acceptance or execution authority follows from this record.

### Concrete Next Proposal: A1 Bootstrap-Only Static Review

A new unsent fixed packet narrows the next proposed review to acquisition and canary bootstrap controls: input/path checks, offline OLD reconstruction, read/write/network/credential isolation, runtime/Git identity, child inheritance, synthetic topology/lock/sync checks and observer self-canaries. It contains ten full files: the controls README, common, controller, acquire, canary, observer, both sandbox policies, baseline-inputs and the existing workspace module; it also contains the same path-substituted invocation. All supplied source/control bytes are unchanged. Full files may mention later stages, but those stages are explicitly outside this review's conclusion.

The proposal excludes unittest collection/smoke/full suites, the runner/future entry factory, product-prefix coverage, D1/D2, contract activation and actual execution. It asks for a concise bootstrap-only judgment, concrete blockers with minimal corrections, unavailable evidence and the remaining broader review gates. Missing product/normative/test bodies are explicit limitations. This partial review cannot be recorded as completion of the original whole P0a R1 or P0c R0. It reduces the review scope and input volume; it does not establish why either previous invocation timed out or guarantee a shorter response time.

New packet: 130,060 bytes; SHA-256 `7ae54ca435ff78f71cdf076d5885a11ac18cca5728c7f52b253f5a5924c78e62`. Proposal: one fresh `opus`/`high` no-tool subscription review, the same CLI restrictions and maximum 600 seconds, then Driver recording/disposition and stop. Authentication mismatch, input drift, timeout or material scope expansion stops the attempt. No automatic retry or controls execution is included. Owner authorization for this narrower transmission is pending; the packet has not been sent. Any later runner/factory/oracle review remains a separate proposed continuation within this owning task, not silently granted by A1.

Custody consumer: Owner's decision on narrower recovery and an explicitly authorized A1 reviewer. Preserve this updated task, the compact second-attempt authorization/timeout metadata and the unsent A1 packet/identity outside the active source checkout with readback. Earlier authored and first-timeout copies retain their historical input meaning. Empty output files and the Driver-only unavailable marker carry no Reviewer content and are not permanent evidence. Keep the existing worktree for this concrete near-term review recovery. Controls, product/runtime, accepted decisions, index and central status remain unchanged.

## A1 Bootstrap-Only Review Result — 2026-10-09

### Actual Authorization And Input

The Owner replied “승인” to the narrower proposal: one fresh no-tool subscription review, maximum 600 seconds, limited to baseline acquisition and isolation/canary bootstrap. This authorized sending the prepared 130,060-byte packet and recording/dispositioning the response, then stopping. It did not authorize control corrections, another invocation, actual canaries/tests, D1/D2 selection, contract activation or result acceptance. The explicitly reduced scope does not discharge the original full P0a authored-result R1 or P0c execution-plan R0.

Packet SHA-256: `7ae54ca435ff78f71cdf076d5885a11ac18cca5728c7f52b253f5a5924c78e62`; ten full source/control inputs plus the path-substituted base invocation described in the preceding proposal. Base/diff remain `238514686078ce1564010a7b69013f48a635c57c` / `12238ddc334c4a6971d657249732a73d59cc4c3e32b6463d5a7fccfc867a6b04`. The invocation identities remain private `366f147fcedbb0848338a1c05f07c7b231fc19a5867dd837b5298595bcc5a0e3` and review copy `ec41662c1b02943a07ae1bd4b5799355b3b2b66032cf9d18b35ba53e72b783f9`. All untracked reviewed controls retain their authoring-table hashes. The supplied workspace module has SHA-256 `ca08550f64bb7331bdd5ceba720b36f67e1603f90cffe7286c80565ee84762f3`. The local task checkpoint `d637cc1ab71dff21a775d59c8462ebea9a29d2b7f4c88e4c5be90db8d59db287` was checked before/after but was not included in this narrower packet. Exact included paths and hashes remain embedded in the retained packet.

### Invocation And Evidence Limits

Immediately before invocation, authentication confirmed logged-in `claude.ai / firstParty / pro`. Actual model: Claude Opus 5.5 (`claude-opus-5-5`); fresh session `a88e9e65-0d7e-4277-b5f4-7d7f88b7ce43`. The CLI used requested alias `opus`, effort `high`, safe/restricted mode, empty tools, strict empty MCP, disabled slash commands, empty setting sources, `dontAsk` and no session persistence. Startup independently reported empty tool and MCP lists. Output transport changed to verbose `stream-json` to distinguish startup from a final result; no partial-message flag or additional Reviewer capability was enabled. The system prompt stated the actual A1 authorization, partial scope and no-execution/Owner boundaries.

Elapsed 406.40 seconds, exit 0, no reported error, zero stderr bytes, final result received. The stream contained 308 valid events and no invalid lines. The before/after packet, included files, full identified source bytes/modes, control hashes, invocation files, base/diff and task-checkpoint checks passed. The proposed execution root stayed absent. No acquisition, canary, unittest discovery, runtime test or product command was executed by the Reviewer. This is a fresh model/session reviewing Driver-selected inputs; supplied omissions and substituted host paths limit independence and completeness. Reviewer statements of deterministic behavior are static inferences, not reproduced executions.

### Reviewer Response Verbatim

````text
# A1 부분 정적 검토: acquire base → canary base 부트스트랩

## 1. 판정

**현재 바이트 그대로는 신뢰할 수 있는 시도가 불가합니다.** `canary base`는 결정적으로 실패하며, 슬롯이 1회용이고 ROOT 재사용이 금지되어 있어 그대로 실행하면 ROOT·acquire·canary 슬롯만 소모됩니다.

- **acquire 경로**(`controller.main/run` → `acquire.sb` → `acquire.py` → 사후 `verify_old`): 정적으로 차단 결함을 찾지 못했습니다. tree 동일성, 모드·종류 제한, 배타 생성, sha256/size 검증, 샌드박스 밖 재검증이 모두 fail-closed입니다.
- **canary 경로**: 아래 B1~B3 때문에 통과 불가이거나, 통과하더라도 증거가 약합니다.

실행한 것은 없으며, SBPL 컴파일·집행 여부는 판단하지 않았습니다. 이 판정은 실행 허가나 P0 전체 수락이 아닙니다.

## 2. 차단 결함

**B1. lock-canary 증인이 기록되지 않음** — `observer.py` `observed_flock`/`path_of` (직접 관찰, 결정적)
- lock-canary 분기는 `fcntl.flock(f, LOCK_EX)`에 파일 객체를 넘깁니다. `path_of`는 `int`/`bytes`/`str`/`PathLike`만 처리하므로 `None`을 반환하고 `emit`이 아무것도 쓰지 않습니다.
- 결과: `lock-attempt`/`lock-acquired`가 없어 `canary.py`가 15초 뒤 "no observed lock wait"로 실패합니다.
- 교정: `observed_flock`에서 `fileno()`가 있으면 정수 fd로 정규화한 뒤 `emit`합니다. 제품 락 코드가 파일 객체를 넘길 때도 같은 유실이 생기므로 canary 쪽이 아니라 observer 쪽을 고쳐야 합니다.

**B2. Git 설정 origin 검사가 Apple Git 시스템 설정과 충돌** — `canary.py` `config --show-origin --list` 루프 (정적 추론, 호스트 미확인)
- Apple CLT Git은 보통 `/Library/Developer/CommandLineTools/usr/share/git-core/gitconfig`(`credential.helper=osxkeychain`)를 시스템 설정으로 갖습니다. 두 정책 모두 이 경로의 읽기를 허용합니다.
- 결과: 파일이 존재하면 "unexpected Git configuration origin"으로 실패합니다. 제품이 `GIT_*`를 제거하므로 환경변수로 우회할 수도 없습니다.
- 교정: Owner 결정이 필요합니다. 그 literal origin과 정확한 키/값을 고정 허용하고 keychain 거부를 별도로 증언하거나, 시스템 설정이 없는 Git 바이너리로 바꿉니다. 그 전에 호스트에서 파일 존재 여부를 확인해야 합니다.

**B3. OLD 쓰기 거부 canary가 샌드박스를 증언하지 못함** — `canary.py` `denied()` (직접 관찰)
- `denied()`는 EACCES와 EPERM을 모두 받아들이는데, OLD는 acquire 후 0555입니다. 샌드박스가 없어도 모드 비트만으로 통과합니다.
- 결과: README의 "모드와 독립적으로 OLD 쓰기 거부"가 증언되지 않습니다.
- 교정: 샌드박스 거부 probe는 EPERM만 인정하거나, 모드 비트로는 막히지 않는 연산으로 probe합니다. 어느 errno가 나오는지는 런타임 확인이 필요합니다.

## 실행 전 교정 권고 (비차단)

- **N1. 증거 앵커가 자식 쓰기 영역 안에 있음** (`controller.run`, 직접 관찰): `inputs.json`/`result.json`/`stdout.log`가 자식의 `file-write*` 범위인 `out`에 있습니다. 자식이 `result.json`을 먼저 만들면 controller의 배타 생성은 실패하고 자식이 쓴 파일이 이후 게이트에 읽힙니다. 자식 쓰기 범위를 `out/work`로 좁히십시오. 신뢰된 canary에서는 실해가 낮지만 collect 이후에는 차단급입니다.
- **N2. stdin 상속** (`controller.run` `Popen`, 직접 관찰): stdin을 지정하지 않아 controller의 TTY가 자식에 상속됩니다. `stdin=subprocess.DEVNULL`을 지정하십시오.
- **N3. canary 누락 범위** (직접 관찰): 다음 항목의 증인이 없습니다.
  - SOURCE/CONTROLS/INPUT 쓰기 거부
  - 이전 슬롯(`runs/acquire-base`) 쓰기 거부
  - `test.sb`에서 COMMON_GIT 읽기 거부
  - PATH로 해석된 `git`이 고정 바이너리와 같은지 (제품 `_topology_probe`는 bare `git`을 씀)
  - observer의 mkdir/rename/rmdir/chmod 훅과 `audit-before` 이벤트
- **N4. `verify_old`/`acquire.py`의 검증 공백** (직접 관찰): 디렉터리 모드, 빈 디렉터리, 비정규 멤버를 검사하지 않습니다. README가 말한 "Git blob identity" 재계산이 없고, manifest의 `tree`는 쓰이지 않으며, `release_sha256`은 상수 비교뿐입니다.
- **N5. 런타임 해시 범위** (정적 추론): Homebrew framework 구조라면 `sys.executable` 해시는 런처 스텁만 묶고, 실제 인터프리터·dylib·stdlib은 묶지 않습니다. controller는 `-I`/`-E` 없이 실행되어 호출 셸의 `PYTHONPATH`와 site-packages `.pth`의 영향을 받습니다.
- **N6. 읽기 범위가 설명보다 넓음** (직접 관찰): `acquire.sb`는 COMMON_GIT 전체(config 포함)를 읽게 하고, 두 정책 모두 전역 `file-read-metadata`와 USERDIR 목록 읽기를 허용합니다.

## 3. 미확보 증거와 남은 게이트

**런타임·호스트 미확인**
- SBPL 문법과 의미: `param`, `process-info*`, `same-sandbox`, OLD 자체 생성에 대한 `subpath` 매칭, literal 디렉터리의 readdir.
- `deny default`에서 `flock`/`F_FULLFSYNC`/`F_GETPATH`/자기 SIGKILL이 허용되는지. 명시 규칙이 없습니다.
- mach-lookup 전면 거부 상태에서 Python·Git이 기동하는지.
- `/opt/homebrew/etc`(openssl.cnf)와 `/opt/homebrew/lib`(site-packages) 읽기 거부의 영향.
- 호스트 사실: git/python 바이너리의 `st_nlink == 1`, 런타임 bin의 `python3` 존재, 실제 버전 문자열, SOURCE `src`/`tests`의 `__pycache__` 부재, 파일 모드, 경로 깊이(`/Users/<user>/dev-home/agent-worktrees/ROOT`), BASE 객체 존재, COMMON_GIT의 config/alternates/promisor.

**미제공 입력**
- `hv2ref/jsonio.py`, `errors.py`: canary가 import하므로 import 시 부작용과 flock 호출 형태를 확인할 수 없습니다.
- private 정확 invocation과 `release_sha256` 산출 근거.
- `source_files`와 baseline은 101개 이름과 일부 해시만 대조했습니다(차이는 `docs/development/README.md` 1건). 전수 대조는 하지 않았습니다.

**남은 게이트**
- B1~B3를 고치면 control 해시와 invocation 해시가 바뀌므로 델타 재검토와 Owner 승인이 다시 필요합니다.
- 이번 범위 밖: runner/factory, collect/smoke/complete, 테스트 부하에서의 `test.sb`, `prefix-oracle`/`base-seed-ids`, observer의 제품 경로, P0a R1 전체, P0c R0.
````

### Driver Follow-Up Observations

These checks occurred after the Reviewer response and were not supplied to that review. They do not retroactively expand its coverage.

- B1 follows directly from the supplied code: the synthetic lock-canary passes a file object, while `path_of` does not handle that type. Current product `jsonio.exclusive_file_lock` passes an integer fd; do not turn the synthetic observer bug into a claim that the current product lock fails. No observer or product module was imported/executed to establish this distinction.
- The named CLT system configuration file exists: 64 bytes, SHA-256 `d9edd909b86735d18b57095355e8f16a67f2a557d02431bb223854291eb6e653`. Direct read-only inspection found exactly the `credential.helper` and `init.defaultBranch` entries, with non-secret values `osxkeychain` and `main`. This establishes file contents, not that the future isolated child actually consumes this origin. A separate read-only `git config --system --no-includes --show-origin --name-only --list` inspection, using the named CLT binary with cwd in a disposable directory, returned exit 128; its stderr was not retained by that inspection wrapper, so the cause and effective automatic origin remain unavailable. This command was not a control/canary test and has no pass counts. It was not retried to manufacture a pass.
- Read-only source inspection of the previously omitted `jsonio.py` (`6432f0d2b2a09dcbdc1c473ab0596def1751d2733b691684349fb62a536e69fe`) and `errors.py` (`63cae866bc847606e097d3acd62e6a460d994436873d21a95da39caf384decd9`) found ordinary import/constants/function/class definitions and the integer-fd flock call. AST inspection is not import-time execution proof. Include these exact module bodies in the next relevant review.

### Driver Dispositions

All corrections below are proposed, not implemented. Accept/revise records the Driver's judgment; it does not supply Owner execution approval.

| Finding | Disposition | Bounded response and evidence boundary |
| --- | --- | --- |
| B1 — file-object lock witness | accept | Normalize objects exposing `fileno()` to integer descriptors for observation while preserving the original flock call/delegation. Cover both file-object and integer-fd self-canary paths. The counterexample is statically established, not executed |
| B2 — system Git origin | needs-user | Recommend retaining the already identified CLT Git and permitting only the exact observed system origin/digest and its two known non-secret key/value pairs when actually present. Refuse other origins/values; keep network and keychain access denied. Do not alter host/global config or invoke credential helpers. Actual child origin and effective denials remain runtime evidence. Changing the Git binary is a separate alternative, not selected |
| B3 — DAC versus sandbox proof | revise | Accept the missing proof, but do not make EPERM alone a universal isolation oracle. Separate mode-bit protection from sandbox evidence and author a non-destructive probe/positive-control design whose outcome is not caused merely by OLD's 0555/0444 modes. State exactly which operation the observation supports; retain unavailable cases instead of relabelling them pass |
| N1 — child-writable evidence anchors | accept | Promote this to a prerequisite before any base execution: keep controller inputs/results outside the child's writable subtree, and give the child only a dedicated work subdirectory. Inherited stdout is untrusted diagnostic output, never the parent gate. Bind subsequent prerequisites to parent-owned evidence |
| N2 — inherited stdin | accept | Set child stdin to DEVNULL; no interaction or terminal input is needed |
| N3 — missing boundary and machinery canaries | revise | Add non-destructive SOURCE/CONTROLS/INPUT/prior-anchor refusal probes, bounded COMMON_GIT read refusal, PATH-resolved Git identity and non-product observer self-canaries. Keep later product-prefix/factory coverage outside this correction's acceptance; do not claim those scenarios were reviewed |
| N4 — OLD identity/shape gaps | revise | Check exact directory/file membership, modes and unsupported members; independently recompute stated blob/inventory identities where claimed. Label any merely informational tree field as such. Preserve the fixed predecessor bytes and release identity; no new historical-compatibility claim |
| N5 — Python environment and identity | revise | Propose an isolated no-site bootstrap (`-I -S -B` with fixed controls path) for the controller/appropriate children, plus matching checks. Describe the existing binary digest as a launcher identity, not a seal over dylibs/stdlib. The trusted host runtime remains an explicit assumption; do not introduce a new full toolchain packaging project |
| N6 — broader reads than prose | revise | Make metadata/directory enumeration and acquisition Git reads explicit; narrow unnecessary ancestor listing and repository read allowances. Fix the required object/config read set during bounded authoring and stop if it needs unapproved credential-bearing data or broader access. Do not widen access to cure a denial, or claim all host metadata is private |

The Driver agrees that the present controls should not be executed. The acquired-path static observation is limited to “no blocker found in supplied text”; it is not successful acquisition or a complete safety assessment. SBPL effects, platform services and actual runtime behavior remain unavailable. No finding has been reproduced by running the controls, and no fix or test pass is claimed.

### Proposed Next Bounded Scope

Propose one authoring-only correction slice for the A1 controls, incorporating B1/B3 and the accepted/revised bootstrap issues above, with B2's exact-known-system-config option explicitly selected by the Owner if approved. Editable source scope: `common.py`, `controller.py`, `acquire.py`, `canary.py`, `observer.py`, `test.sb`, `acquire.sb`, `baseline-inputs.json` only as necessary for exact verification metadata, the controls README and this owning task. Update the private invocation's deterministic hashes/fields and prepare a fixed correction-review packet. Read-only context may include the omitted jsonio/errors modules. Do not edit product/runtime/test sources, runner/factory/product-prefix criteria, D1/D2, accepted decisions, index or central status.

Completion criteria: the static B1 counterexample is addressed; authority evidence is outside child write access; bootstrap boundary/identity claims match the proposed code and tests; the B2 choice is explicit; original predecessor/managed bytes are preserved; exact new inputs and the remaining runtime limits are identified. Verify with AST parsing without imports, JSON/hash/path consistency, focused read-through of the named counterexamples, GFM/link/disclosure/whitespace checks and preservation checks. These are authoring checks, not canary execution or SBPL qualification.

Execution mode: local source-only authoring, one bounded slice; no acquisition, canary, discovery, test execution, new Reviewer invocation, Git or adopter action. Reversal cost is limited to uncommitted control/document bytes. Stop if an effective isolation claim needs execution, a new host/runtime/dependency is required, baseline/contract scope changes, permissions must broaden beyond the approved choice, or the correction expands into product behavior. Report the narrower unresolved point instead of silently adding scope. This approval is pending. Subsequent delta review and any actual base execution retain separate authorization; A1 does not close the broader R1/R0 gates.

Custody consumer: Owner correction decision and the next expressly authorized correction Reviewer. Retain the fixed A1 input, this verbatim result/dispositions and exact uncommitted authored controls through existing recoverable custody until referenced by the next phase. Preserve this updated record plus compact authorization/result metadata outside the active checkout with readback. The verbose API event stream is not a permanent deliverable once the final response and necessary model/session/command facts are verified in this record. Keep the source worktree for the concrete correction/review continuation; no checkout is eligible for retirement. Controls and all 29 managed files remain unchanged in this review-only turn.

## A1 Correction Authoring — 2026-10-09

### Actual Owner Authorization

The Owner replied “승인” to the proposed authoring-only correction slice and the recommendation to retain the current Apple CLT Git with only the two identified system settings permitted by the checks. This selects B2's known-system-configuration option for these proposed verification controls: exact origin/file digest, `credential.helper=osxkeychain` and `init.defaultBranch=main`; it does not authorize a keychain request or modification of host settings. Correction authoring, static verification, private input/hash updates and preparation of a fixed correction-review packet are authorized. Actual control execution, a new Reviewer invocation, Git/adopter actions, D1/D2 selection and product/contract changes remain excluded.

The A1 response and its original input retain their prior meaning. These corrected bytes have not yet been reviewed by Claude. This remains the single owning task; no new task, runtime Work or duplicate tracker was created.

### Authored Corrections And Limits

| Finding | Authored change | Remaining evidence boundary |
| --- | --- | --- |
| B1 | Observer converts a file object's `fileno()` for attempt/acquired events, delegates the original flock operand unchanged, and defines file-object and integer-fd self-canaries | Static data-flow inspection only; no witness was executed |
| B2 | Invocation schema 2 and common checks pin the approved configuration's exact bytes; canary accepts only the known system origin/entries when present and an explicit safe synthetic-local config set | No effective child-origin or keychain behavior observed. Host/global configuration stays unchanged |
| B3 | Parent positive counterparts perform non-truncating write opens, bounded reads and same-mode OLD chmod; child probes require matching named denials. Bytes/modes are rechecked | OLD probe proves only a metadata-write refusal, not all data writes; same-mode chmod can change ctime. These positive operations themselves require later execution approval |
| N1 | Per-run inputs/result/boundary evidence remain above a separate child `work/` subtree. Parent prerequisites bind inputs digest, mode/slot and control/tool/config identities | Policy compilation/effect unverified; stdout is explicitly untrusted diagnostics with only a literal data-write allowance |
| N2 | Controller and authored canary/acquisition subprocesses use DEVNULL stdin | No interactive runtime observation |
| N3 | Named SOURCE/CONTROLS/INPUT/current/prior-anchor probes, COMMON_GIT read refusal, PATH Git identity and non-product namespace/audit/lock self-canaries added | Product-prefix and future factory coverage remain outside A1 |
| N4 | OLD verifier checks exact directories/files/modes and rejects special members; blob Git OIDs and checkout inventory digest are recomputed from content | Historical tree field remains informational; no broader historical compatibility claim |
| N5 | Fixed `-I -S -B` runpy bootstrap and isolation/no-site checks; source/import roots remain explicitly supplied | Runtime launcher digest does not seal dylibs/stdlib. Trusted host runtime remains a stated assumption |
| N6 | Ancestor listing permissions removed; acquisition reads source objects through its own synthetic safe bare metadata, with fixed config/environment and no original repository config/refs/HEAD/hooks read allowance | OS/runtime prefix reads and global metadata remain explicit; effective SBPL behavior is not proven |

The acquisition adjustment uses only the existing fixed `ls-tree` and `cat-file blob` operations, with `--git-dir` pointing at synthetic metadata under its own writable work directory. Its subprocess-only environment selects the original objects directory, disables lazy fetching, pins the approved system config and points global config at `/dev/null`. It does not depend on the product retaining `GIT_*` variables. Read-only authoring inspection found the current object directory unlinked, no `objects/info/alternates` and no pack promisor markers. The authored runtime rejects those cases rather than broadening reads. No synthetic metadata directory or OLD tree was created during authoring.

Parent setup time now counts toward the existing budgets; no timeout ceiling increased. Stdout size is checked during and after the child. Its 16 MiB threshold can be overshot by a burst before detection and is documented as detection/stop behavior, not a storage quota. The child layout changes future runner output paths to `MODE-SLOT/work/`; the unchanged runner and downstream integration still require broader review. This correction does not silently qualify those modes.

### Static Verification And Controlled Write Scope

Six Python files passed AST parsing without imports or execution; three JSON files parsed; both SBPL files passed balanced-form checks only. Focused static reading checked the B1 operand flow, parent/child path separation, DEVNULL, known config binding, OLD metadata/data proof distinction and isolated command construction. These are static checks, not reproduced canary results.

An independent read-only computation checked all 101 fixed committed blobs by size/SHA-256/Git blob OID and reconstructed the unchanged checkout-1 release digest. All 29 managed file bytes remain equal to the baseline. Exactly eight control/guide files changed. `runner.py`, the baseline JSON, seed IDs and prefix oracle are unchanged; product/test sources, accepted DR, index, central status and tracked diff are unchanged. The proposed execution root remains absent; no new control bytecode or import cache exists. Link/disclosure/whitespace checks passed. GFM rendering is checked again with the completed record and packet before handoff.

| Corrected file | SHA-256 |
| --- | --- |
| [README.md](verification/colvia-entry/README.md) | `6c621fb17558f97161eae50a615f92c7aec239fb9545a4130fc7a8f8e620b121` |
| [common.py](verification/colvia-entry/common.py) | `5bf311c8877419f58c9936325df8074c4235f6e7596810a7a7f1537373ce1173` |
| [controller.py](verification/colvia-entry/controller.py) | `c188f26921bc1fc738865507402a08b0cfbee2cbf23eab5ee6d68ce67f23a060` |
| [acquire.py](verification/colvia-entry/acquire.py) | `4ac63bc1a3c5b711a954c15ab3a18e3ada8e6af549f10bf787d706ac9209a045` |
| [canary.py](verification/colvia-entry/canary.py) | `88271219e6fcd16a5b0d0bc3436d31e2d5fa633080c7946c669c82a52f449cec` |
| [observer.py](verification/colvia-entry/observer.py) | `58b045cf08ae3e7c42be06930ea1a6947ef2b8458a58fce082a7208b4e78fafd` |
| [test.sb](verification/colvia-entry/test.sb) | `137172701875e8cdca126f37adf3919051377088504d86ee5d1125c6c6898d81` |
| [acquire.sb](verification/colvia-entry/acquire.sb) | `638bf3ee10ab06a423b38b55d9e911a0dd1e19ff7df9798e7862fe6a3d4a7780` |

### Next Review And Preservation

Prepare a fixed bootstrap-correction packet with the corrected controls, unchanged baseline metadata, exact schema-2 invocation review copy, the prior A1 response/dispositions and the previously omitted jsonio/errors context. Private actual paths remain local; substitutions must be explicit. The proposed next action is one fresh no-tool Claude subscription delta review, maximum 600 seconds, scoped to these A1 corrections and their acquisition/canary integration, then record/disposition and stop. It is not whole P0a R1/P0c R0 completion and does not authorize collection, tests or execution. This transmission requires a new Owner approval; it has not occurred.

Custody consumer: Owner review decision and the next explicitly authorized correction Reviewer. Preserve exact corrected files, invocation/packet identities and the updated owning record outside the active checkout with readback. Earlier authored/review copies preserve prior input meaning. Reproducible render/static-check output and authoring scripts are not permanent deliverables. Retain the source worktree for the concrete next review; no checkout is eligible for retirement.

## A1 Correction Delta Review Result — 2026-10-09

### Actual Authorization And Fixed Input

The Owner approved one fresh tool-free A1 correction delta review, maximum 600 seconds, with response/disposition recording only. An initial external-transmission approval check rejected the launch before the reviewer process started; no packet was sent by that rejected action. The Owner then expressly approved transmitting the approximately 171 KB internal packet, including 12 complete source/control/context files and the previous review, to Anthropic Claude through the existing subscription account. One reviewer invocation was subsequently performed. Correction authoring, control/test execution, another invocation, Owner result acceptance, D1/D2 selection, contract activation, Git and adopter actions remain excluded.

The fixed packet is 170,952 bytes, SHA-256 `4eefbdf14819575131dba7ff350ccfdb2b7a17aab6a880550cb602b3ed404f7f`. Base revision `238514686078ce1564010a7b69013f48a635c57c` and tracked diff SHA-256 `12238ddc334c4a6971d657249732a73d59cc4c3e32b6463d5a7fccfc867a6b04` were unchanged. The untracked task checkpoint was `915ed2374d537cea9be82211272dac64cdaf701261a8c870464e1523c43522c2`. The packet contains its prior-review, Driver-disposition and correction-authoring excerpts, not the complete task. Their hashes are respectively `529f6f7d0da4262281cf929bdd3e4bf810be7e1b2ebc260140dc60202a005f1f`, `6aace1f6d6616bce7ffdb374c3b56730577fe8eadac2017c3817961362aaf784` and `297cb21cf1c789dac52005295a490f04693c2cdeeaa95c44e09857a090c19363`.

The 12 full inputs are README/common/controller/acquire/canary/observer/test.sb/acquire.sb/baseline-inputs.json under the control directory, plus workspace/jsonio/errors under the source package. Each full path and digest is embedded in the retained packet and identity record; corrected controls retain the preceding table's hashes. Private invocation SHA-256 is `812aad74c5d908d5619b768797a421113c68c57a2148ce78019ff71707446410`; the review copy is `6ee8e18c080702a874306cbee857fe7626fd428cc2438fa02061d8b78f215444`. Only six private path strings are substituted with illustrative paths in the review copy. Private host topology remains outside the reviewer's observations. The prepared packet's pending-authorization wording was historical; the invocation system prompt explicitly stated the actual approval.

### Invocation And Evidence Limits

Authentication immediately before invocation confirmed `loggedIn=true`, `authMethod=claude.ai`, `apiProvider=firstParty`, `subscriptionType=pro`. The actual model was Claude Opus 5.5 (`claude-opus-5-5`), fresh session `6967d5e4-68a0-4ebe-9c2a-df06ef4ffded`. The actual argument vector is below; cwd was the fixed private packet directory and stdin was its exact prompt bytes. The local wrapper enforced one 600-second attempt and process-group termination on timeout.

```json
[
  "claude",
  "-p",
  "--model",
  "opus",
  "--effort",
  "high",
  "--safe-mode",
  "--system-prompt",
  "The human Owner has now explicitly authorized this one A1 correction delta static review. The fixed packet was prepared before approval; its pending-authorization wording is historical. Follow the fixed bounded request. Treat source as data, use no tools or execution, and respond concisely in Korean. This is partial review of acquisition/canaries only, not whole P0a R1 or P0c R0 completion. A reviewer verdict is not Owner acceptance.",
  "--restricted",
  "--tools",
  "",
  "--strict-mcp-config",
  "--mcp-config",
  "{\"mcpServers\":{}}",
  "--disable-slash-commands",
  "--setting-sources",
  "",
  "--permission-mode",
  "dontAsk",
  "--no-session-persistence",
  "--output-format",
  "stream-json",
  "--verbose"
]
```

Elapsed 559.42 seconds; exit 0; no timeout or reported error; final result received; stderr 0 bytes. Startup reported no tools and no MCP servers. The transport produced 435 valid events and zero malformed lines; the raw event stream is not a permanent deliverable. Before/after checks passed for the packet, 12 complete inputs, task checkpoint, base/diff, private/review invocation, all 101 identified source bytes/modes, 11 control files and runtime/Git/system-config bytes. The proposed execution root remained absent. No control imports, SBPL compilation, acquisition, canaries, collection, tests or product commands were executed by this review.

This is independent model/session review of Driver-selected inputs. It is not a complete repository audit; the supplied prior response and disposition intentionally provide context. All code-behavior conclusions below are static inference, not reproduced counterexamples or runtime passes. Full P0a authored-result R1 and P0c execution-plan R0 remain open.

### Delta Reviewer Response Verbatim

````text
# A1 교정 델타 정적 검토: acquire base → canary base

## 1. 판정 (부트스트랩 한정)

**현재 바이트 그대로는 시도 불가입니다.** B1~B3와 N1~N5는 정적으로 해소됐지만, N6 교정이 과잉이어서 `canary base`가 다시 결정적으로 실패하는 것으로 추론됩니다(R1).

- **acquire 경로**: 차단 결함을 찾지 못했습니다.
- **acquire 단독 선실행도 권고하지 않습니다.** R1을 고치면 `test.sb` 해시가 바뀌고, `controller.completed()`의 `inputs["controls"] == c["controls"]` 검사가 기존 acquire-base 결과를 무효로 만듭니다. ROOT만 소모됩니다.

실행한 것은 없으며 전부 정적 판독입니다. SBPL 컴파일과 실효는 판단하지 않았고, 이 판정은 Owner 수락이나 실행 허가가 아닙니다.

## 2. 회귀 (차단)

**R1. `test.sb`의 조상 디렉터리 목록 읽기 제거로 topology canary가 실패함** (정적 추론, 확신 높음)

- 위치: `test.sb`(조상 readdir 허용 없음, 마지막 주석) ↔ `canary.py`의 `classify_target(plain, mutation=True)` ↔ `workspace.py` `_classify_target`의 `parent.iterdir() for parent in target.parents`.
- 제품 코드는 target의 모든 조상을 `/`까지 열거합니다. target이 `…/canary-base/work/non-git`이면 읽기가 허용된 조상은 `work`뿐입니다.
- `runs/canary-base`, `runs`, `exec`, ROOT, `agent-worktrees`, `dev-home`, `/Users/<user>`, `/Users`, `/`의 9개는 전역 `file-read-metadata`만 있습니다. opendir가 EPERM이 되고, `OSError`가 `ContractError(HV2-WORKSPACE-TARGET)`로 바뀌어 canary가 비정상 종료합니다.
- 같은 정책이 `/dev/fd` 목록에 `file-read-data` literal을 따로 두는 것과 같은 모델입니다.
- 교정 방향: `test.sb`에만 위 9개에 대한 `file-read-data` **literal**(subpath 아님)을 명시합니다. `acquire.sb`에는 필요 없습니다.
- 이 교정은 `$HOME`, `dev-home`, `/`의 이름 열거를 다시 허용하므로 Owner 결정이 필요합니다. 제품의 조상 열거는 이 범위의 변경 대상이 아닙니다.

## 3. 기존 지적 상태

| 항목 | 상태 | 위치와 근거 (모두 정적) |
| --- | --- | --- |
| B1 | 해소 | `observer.observed_flock`이 `fileno()`를 정규화해 `emit`하고 원 operand를 그대로 위임. `canary.py`의 `lock-object`/`lock-fd` 두 경로. `jsonio.exclusive_file_lock`의 int fd 호출과도 일치 |
| B2 | 해소 | `common.SYSTEM_GIT_CONFIG`와 `config()`의 정확 바이트 고정. `canary.py` origin 루프가 키·값·중복·부분 집합을 거부. acquire는 서브프로세스 한정 env |
| B3 | 해소 (제한 주장) | `controller.positive_boundary_controls` ↔ `canary.boundary_probes`. 부모 성공과 자식 거부의 쌍으로 DAC와 구분됨. OLD는 chmod 메타데이터 거부만 증언하고, 데이터 쓰기 거부는 정책 문면 추론. README 한계 문구와 일치 |
| N1 | 해소 | `controller.run`의 `work/` 분리, `test.sb` 쓰기 범위, `completed()`의 inputs 해시·mode·slot·식별자 결속 |
| N2 | 해소 | controller `Popen`과 canary·acquire·observer 호출 전부 `DEVNULL` |
| N3 | 문면 해소, 일부 도달 불가 | 쓰기·읽기 거부 probe, PATH git, observer 네임스페이스·audit 이벤트는 요구 집합과 일치. topology 단계 이후는 R1 때문에 도달하지 못함 |
| N4 | 해소 | `common.verify_old`: 디렉터리·파일 멤버십과 모드, 특수 멤버 거부, blob OID와 29개 inventory 재계산. `tree`는 정보용. BASE→tree 결속은 샌드박스 안 `ls-tree` 대조에만 의존 |
| N5 | 해소 | `BOOTSTRAP`, `require_isolated`, `python_command`. 런처 해시 한계가 명시됨 |
| N6 | acquire 해소, test 회귀 | `acquire.sb`는 OBJECTS만 추가 읽기. `test.sb`는 R1 |

## 4. 신규 비차단 지적

- **M1. 양성 probe가 슬롯 생성 뒤에 실행됨** (`controller.run`, 직접 관찰): INPUT이나 `common.py`가 소유자 쓰기 불가(예: 0444)이면 `os.open`이 `PermissionError`를 내고, `result.json` 없이 canary 슬롯이 소모됩니다. DAC 사전검사를 `out.mkdir` 앞으로 옮기거나 호스트 모드를 미리 확인하십시오.
- **M2. `git commit`의 자동 maintenance가 프로세스 그룹을 벗어남** (`canary.py`, upstream 2.47+ 동작 기준 추론, Apple 빌드 미확인): `--detach`가 setsid를 하므로 controller의 group 검사 밖입니다. canary commit에 `-c maintenance.auto=false`를 주거나 한계로 기록하십시오.
- **M3. `/etc/gitconfig`가 호스트에 있으면 모든 git 호출이 실패할 수 있음** (추론, 불확실): Git은 설정 파일 접근의 EPERM을 fatal로 처리합니다. Apple Git이 이 경로를 별도 system 경로로 탐색하는지는 확인하지 못했습니다. 부재를 읽기 전용으로 확인하면 됩니다.
- **M4. `git init`이 허용 집합 밖 키를 쓸 수 있음** (런타임 미확인): 2.54가 `core.symlinks`나 `extensions.*`를 쓰면 fail-closed로 슬롯이 소모됩니다.
- **M5. `sys.path.insert(0, CONTROLS)`** (`common.BOOTSTRAP`, 직접 관찰): 멤버십 검사 전에 stdlib 이름의 `.py`가 우선합니다. `append`로 충분합니다.
- **M6. 자식이 `stdout.log`를 truncate할 수 있음** (`test.sb` LOG 허용, 직접 관찰): 16MiB 탐지를 우회할 수 있습니다. 게이트가 아니므로 수용 가능하지만 README 한계에 추가하십시오.

## 5. 불필요한 확장

제품·factory 쪽으로의 확장은 없습니다. 좁힐 수 있는 것은 세 가지입니다.

- `acquire.sb`의 `literal BOUNDARY` 읽기: 그 모드에는 파일이 없습니다.
- `test.sb`에 전달되는 `OBJECTS` 파라미터: 쓰이지 않으며 무해합니다.
- acquire의 system config 읽기: `ls-tree`/`cat-file`에 필요 없으므로 `GIT_CONFIG_NOSYSTEM=1`이 더 좁습니다. Owner 승인 범위 안의 선택 사항입니다.

## 6. 정적 한계와 미제공 입력

**런타임 미확인**
- SBPL 컴파일과 `param`, OLD 자체 생성에 대한 `subpath` 매칭.
- deny-default에서 `flock`, `F_FULLFSYNC`, `F_GETPATH`, 자기 SIGKILL이 허용되는지.
- mach-lookup 전면 거부 상태의 Python·Git 기동, `/opt/homebrew/etc` 읽기 거부의 영향.
- `-I`에서 framework 런처의 `sys.executable`이 고정 해시 경로로 해석되는지. controller에서는 ROOT 생성 전에 fail-closed입니다.
- 소켓 거부가 bind/connect 단계인지 생성 단계인지.

**호스트 미확인**
- git·python·system config의 `st_nlink == 1`, 런타임 bin의 `python3`, `sandbox-exec` 존재.
- SOURCE `src`/`tests`의 `__pycache__` 부재.
- alternates/promisor 부재는 저작 기록의 주장일 뿐입니다.

**미제공 입력**
- `src/hv2ref/__init__.py`(98B): canary import 경로에 있습니다.
- 이전 `test.sb`/`acquire.sb` 바이트: "제거"는 기록과 주석으로만 확인했습니다.
- private invocation, `runner.py`, `prefix-oracle.json`, `base-seed-ids.json`.

해시와 release digest는 재계산하지 못했습니다. `source_files`와 baseline은 표본만 대조했고, 차이는 `docs/development/README.md` 1건입니다.

## 7. 남은 게이트 (실행 권한 아님)

1. R1 교정과 조상 이름 열거 범위에 대한 Owner 결정. M1~M6 반영 여부도 함께 정합니다.
2. control·invocation 해시 갱신 후 한정 델타 재검토와 Owner 승인.
3. 실행 전 읽기 전용 호스트 사실 확인(6절 항목, `/etc/gitconfig`, INPUT·CONTROLS 모드). 별도 승인이 필요합니다.
4. acquire와 canary의 실제 실행은 별도 Owner 승인 사항입니다. 1회용 ROOT·슬롯이 SBPL 미확인 항목에서 소모될 때의 처리를 미리 정해 두십시오.
5. 범위 밖으로 남는 것: runner와 `work/` 통합, collect/smoke/complete, factory, product-prefix, D1/D2, P0a R1 전체, P0c R0.
````

### Driver Follow-Up Observations

The following read-only checks occurred after the review and do not retroactively expand its evidence:

- The supplied `workspace.py` really calls `parent.iterdir()` across `target.parents` in `_classify_target`; `classify_target` converts an `OSError` to `HV2-WORKSPACE-TARGET`. The current `test.sb` has no ancestor listing allowance. This confirms the code/policy mismatch underlying R1; the actual SBPL denial/errno remains unexecuted.
- Runtime, Git and pinned system-config files each currently have link count 1; their modes are respectively 0755, 0755 and 0644. The fixed input and controls `common.py` are currently 0644 and owned by the same local account. This is a metadata observation, not an actual positive write-open probe or future ACL guarantee.
- `sandbox-exec` exists; `python3` beside the fixed runtime resolves to the fixed launcher. `/etc/gitconfig` is absent including a dangling symlink check. SOURCE src/tests have no `__pycache__`; the source object store has no alternates entry or promisor markers. These are current facts to recheck before future execution, not proof of sandboxed Git behavior.
- The omitted `src/hv2ref/__init__.py` contains only a module docstring and `__version__ = "d1-source-derived"`. Its bytes will be included as import context in the next relevant packet. It was read, not imported; SHA-256 `9f56d182be547f3fae080f1ad18dd07e91fb7a9b3e6a483069b150fb3cb3e43a`. The reviewer did not see it in this round.

The follow-up metadata inspection used Python standard-library Path stat/exists/is_symlink/resolve/rglob operations only and exited 0. Source read-through and `git diff --check` also exited 0. No test suite or pass count applies. These commands did not exercise the proposed controls.

### Driver Dispositions

The Driver accepts the execution hold. No correction below has been applied; accept/revise/needs-user describe proposed dispositions, not Owner decisions or permission to execute.

| Finding | Disposition | Response and boundary |
| --- | --- | --- |
| R1 — required ancestor enumeration absent | needs-user | Accept the static mismatch. Recommend authoring exact `file-read-data` literal allowances in test.sb for the nine missing ancestor directories, supplied by the controller from the fixed run layout. No subpath/recursive-content grant. Keep acquire.sb unchanged. This exposes directory entry names along the approved path, including the home directory and filesystem root, and needs an explicit Owner scope decision before changing the policy |
| B1-B3, N1-N5 | accept | Their fixes have static support within the stated limits; N3's later observer probes remain blocked by R1. This is not executed qualification or closure of the broader review |
| N6 | revise | Acquire narrowing has no identified static blocker; test-policy narrowing removed an existing product prerequisite. Restore only the named directory enumerations if approved rather than editing product topology behavior |
| M1 — slot consumption on positive-probe failure | revise | Current 0644 metadata does not show the proposed counterexample on this host. Add an explicit pre-execution check of existing probe targets and retain the exclusive-slot failure limitation. Do not claim mode inspection proves ACL/write-open success, move synthetic parent-file probes before those files exist, or permit slot/root recycling. No new controller recovery mechanism is proposed |
| M2 — possible detached automatic maintenance | revise | Upstream/Apple process behavior is not independently verified here. Propose `-c maintenance.auto=false -c gc.auto=0` on the synthetic commit invocation only, without persistent Git config or product changes. Applying these switches to every config inspection would itself introduce command-line origins and is not proposed. Other escape/process assumptions remain explicit |
| M3 — possible extra system-config origin | revise | Read-only follow-up found /etc/gitconfig absent now. Keep actual Apple Git origin behavior unavailable and recheck absence before execution; do not widen config read paths or change host settings |
| M4 — possible additional init keys | defend | Keep the explicit allowed key/value set and fail-closed behavior. No runtime result supports speculative allowlist expansion. If the fixed Git emits another key during later approved execution, preserve the precise observation and request a bounded decision |
| M5 — control path precedes stdlib | accept | Propose appending the controls path after the isolated interpreter's standard paths in common.BOOTSTRAP and the matching README command. No module execution or package redesign is needed for authoring |
| M6 — rewritable stdout diagnostics | accept | Document that the child can truncate/rewrite its diagnostic log, so the observed 16 MiB size threshold does not bound cumulative output or guarantee a complete transcript. Parent input/result files remain the gate. Do not add a log-capture subsystem in this slice |
| Optional cleanup / acquire system config | defend | Leave unused parameters/absent BOUNDARY allowance and the already approved exact-known-system-config acquisition choice unchanged in this correction. These are optional simplifications, not blockers. Avoid reopening the B2 choice without a demonstrated need |
| Reviewer request for separate read-only-host approval | defend | Non-mutating source/metadata inspection is already allowed by the current review task. The checks above were performed without launching controls or widening execution scope. Actual positive probes, synthetic Git work and sandbox execution still require separate authorization |

Do not run acquisition ahead of R1 correction: changing any bound control invalidates the current prerequisite identity, and an exclusive root is not a disposable retry token. No finding is labelled reproduced, and no test pass count is claimed.

### Proposed Next Bounded Authoring Slice

Recommend one authoring-only correction for R1, M2 and M5, plus README/preflight limitations for M1/M3/M4/M6. Exact editable source scope: test.sb, controller.py only to supply/validate the fixed literal ancestor parameters, common.py only for bootstrap import ordering, canary.py only for the synthetic commit switches, controls README and this task. Update corresponding private invocation hashes and prepare one fixed delta packet including the previously omitted package initializer. Other controls, product/runtime/test sources, runner/factory/oracles, D1/D2, accepted DR, index and central STATUS remain unchanged.

For the current canary target, WORK is already readable. The nine additional literal directories are: the run evidence directory (canary-base), runs, exec, ROOT, the agent-worktree storage directory, dev-home, the local account home directory, /Users and /. The permission is directory enumeration at those exact paths; it must not become a recursive read of files under home or the storage root. Actual private paths stay in the private invocation, with generic parameters in source. Acquisition receives no new ancestor read allowance. Keep the existing parent evidence write denial and all named refusal probes.

Completion criteria: the source enumeration path and explicit test-policy literals agree; existing parent-evidence and write boundaries remain intact; import ordering no longer prioritizes controls over stdlib; synthetic commit disables automatic maintenance without affecting the origin probe; docs state the remaining slot/log/runtime limitations; managed/source/baseline identities are preserved; new inputs are fixed and reviewable. Check by AST parsing without imports, balanced SBPL forms only, exact literal/path derivation inspection, hashes/JSON, links/GFM/disclosure/whitespace and preservation. No control execution or SBPL effect is implied.

Execution mode: source-only authoring; no acquisition/canary/collection/test/product execution, new Reviewer invocation, Git or adopter action. The next delta review remains separate, with at most one explicitly approved invocation. Stop if more read permissions, a different host/runtime, product changes, retry/recovery semantics or broader runner scope are needed. Reversal cost is limited to uncommitted control/document bytes. Owner approval must explicitly include the nine-directory name-enumeration scope. This proposal is pending.

### Custody And Remaining State

Only this owning task record changed in the review turn. Controls, the 101 identified source files, all 29 managed baseline bytes, accepted DR, index and tracked diff remain unchanged. The proposed execution root is still absent. No central state update is needed because this is a checkpoint on the existing development task, not acceptance or execution completion.

Retain the exact fixed packet and the existing authored-input backup for the named Owner/correction-review consumer until a subsequent accepted handoff or durable Git custody replaces that dependency. Preserve this updated task and compact authorization/result metadata outside the checkout with readback. After the verbatim final response and these essential facts are verified in that durable copy, remove the transient duplicate response and raw API event stream; no reasoning/tool transcript is a permanent review deliverable. Retain the source worktree for the concrete pending correction/review continuation; no checkout is eligible for retirement.

## A1 Ancestor Correction Authoring — 2026-10-09

### Actual Owner Authorization

The Owner replied “승인” to the bounded authoring proposal following the A1 delta review. This expressly includes directory-name enumeration at the nine fixed ancestor directories, including the local account home and /. It also covers the proposed import-order and synthetic-commit corrections, limitation/preflight documentation, static checks, refreshed private invocation hashes and a prepared delta-review packet. It does not authorize a new external review transmission/invocation, control/SBPL/test execution, acquisition, result acceptance, product/contract changes, Git or adopter actions. The earlier external-transmission approval was for the already completed single review, not a recurring delegation.

### Authored Changes

| Finding | Current authored change | Remaining limit |
| --- | --- | --- |
| R1 — ancestor enumeration | test.sb has exactly nine file-read-data literal parameters ANCESTOR_0 through ANCESTOR_8. Controller derives `(out, *out.parents)`, checks nine entries and the runs/exec/ROOT ancestry, and supplies them only to test-policy modes. This check precedes run-slot creation | These are directory entry-name grants at the fixed approved paths, not descendant content grants. SBPL compilation/effect remains unexecuted |
| M2 — possible detached maintenance | Only the synthetic commit receives `-c maintenance.auto=false -c gc.auto=0` | No persistent config, host setting or product behavior changes. Actual Apple Git process behavior is still unobserved |
| M5 — import precedence | common.BOOTSTRAP and its README example now append CONTROLS after the isolated interpreter's standard paths | No module was imported; host stdlib/dylib trust remains explicit |
| M1/M3/M4/M6 | README specifies read-only metadata/config preflight, exclusive-slot/setup failure limits, unchanged fail-closed origin/key handling and rewritable stdout limitations | Mode inspection is not ACL/write-open proof; stdout size is not cumulative output or transcript integrity. No retry/recovery or logging subsystem was added |

For the current canary target, the nine additional directories are the canary-base run directory, runs, exec, ROOT, agent-worktrees, dev-home, the account home, /Users and /. WORK already has its existing read allowance. The fixed invocation determines actual host paths; source uses generic parameters. Acquisition does not receive these parameters, and acquire.sb is byte-identical to the reviewed input. Parent evidence write denial, named refusal probes, network/keychain restrictions and existing OS/runtime read assumptions remain as before. The helper also derives the corresponding fixed-depth path list for other test modes, but their runner/integration behavior is not qualified by this A1 authoring.

### Static Verification And Scope Preservation

Six Python files passed AST parsing without imports; three JSON files parsed; both SBPL policies passed balanced-form inspection only. Independent path arithmetic on the private fixed layout matched the nine literals and the actual source parent-enumeration path. The controller shape check occurs before slot creation, and acquire selects an empty ancestor-parameter set. AST/source inspection found the maintenance switches on exactly one synthetic commit invocation, leaving the config-origin inspection unchanged. The bootstrap/example both use append.

Exactly five control/guide files changed. All seven other control/data files remain unchanged, including acquisition, observer, runner, baseline, seed IDs and prefix oracle. All 101 identified source bytes/modes, including the 29 managed files, remain unchanged. Base revision and tracked diff are unchanged; accepted DR, development index and central STATUS are unchanged. The execution root remains absent, with no new control import cache. This is authored-code/static consistency evidence, not a runtime fix demonstration. GFM/link/disclosure/whitespace checks and backup readback are completed as the final packaging step.

| Current corrected file | SHA-256 |
| --- | --- |
| [common.py](verification/colvia-entry/common.py) | `c9bc7f6ded6348960d2daeb1cad093ea9262c0c1a0d7aa8d7357e63de7f8e80f` |
| [controller.py](verification/colvia-entry/controller.py) | `aa58da53f5b522e5557b1d650436c122aa09c07ddb2a3f9a552a0f31e4c268aa` |
| [canary.py](verification/colvia-entry/canary.py) | `33a6ae014e979c57d7aacfb9161f031b8f1c637bf24f82105d14c0a10d7e2726` |
| [test.sb](verification/colvia-entry/test.sb) | `27de945d5a98549062ed1620351ed0578d4e97251f7693da15471cd9b71857f4` |
| [README.md](verification/colvia-entry/README.md) | `14b55aeeb0259c78e0b0adccb5541e661c34e9446add89c83b38b3c88c3a879b` |

### Next Review And Custody

Prepare one fixed A1 ancestor-correction delta packet with the 13 complete control/context inputs: the prior 12-file set plus the previously omitted package initializer, current schema-2 invocation with the same six private-path substitutions, the latest delta-review response, Driver dispositions and this authoring excerpt. Include a short change summary and distinguish unchanged read context from corrected files. The proposal is one fresh tool-free Anthropic Claude subscription review, maximum 600 seconds, after explicit Owner approval of that packet's external transmission. No review has been called for these new bytes.

Review completion means receiving one bounded response about R1/M2/M5 and the stated limitations, recording it verbatim with Driver dispositions and stopping. It does not complete full P0a R1/P0c R0, qualify runner/factory/product-prefix behavior, select D1/D2 or permit control execution. Preserve an unavailable/timeout result and request a bounded decision rather than retrying.

Custody consumer: the Owner and next separately authorized delta Reviewer, followed by the exact-control execution handoff if approved. Keep the fixed new packet, refreshed invocation and exact authored controls/task outside the checkout with verified readback until that consumer's accepted handoff or durable Git custody replaces them. Earlier inputs/verbatim responses preserve historical meaning. Reproducible static/render scripts are not permanent deliverables. Retain the source worktree for this concrete pending review and possible correction/implementation; no checkout is eligible for retirement.

## A1 Ancestor Correction Review Result — 2026-10-09

### Actual Authorization And Input Identity

The Owner replied “승인” to the explicit proposal to send the approximately 176 KB internal packet, including 13 complete files, to Anthropic Claude through the subscription service for one fresh tool-free static re-review, maximum 600 seconds. This authorized that one transmission/invocation and recording/Driver disposition. It did not authorize corrections, further invocations, control/SBPL/test execution, result acceptance, source Git operations or adopter actions.

The fixed packet was 175,512 bytes, SHA-256 `a279c9364b09c806cf5dabd5a07b673b9f0e8bfe309f4180485709350107abe6`. Base `238514686078ce1564010a7b69013f48a635c57c` and tracked diff SHA-256 `12238ddc334c4a6971d657249732a73d59cc4c3e32b6463d5a7fccfc867a6b04` were unchanged. The untracked task input checkpoint was `18c78211db056f8d972088e50d875f4aa4f8fa1b4ec8a4e104d9a1c35673421f`. Thirteen complete inputs were supplied: the nine control/guide/baseline files of the preceding review plus workspace/jsonio/errors and the package initializer. Each path and hash is embedded in the retained fixed packet; the corrected five files have the preceding authoring table's hashes. Runner, seed/oracle bodies and private host paths were omitted, as declared.

Private invocation SHA-256: `a7db158a24646441f1268a6f6eed16b206072dc47b35ef57082fc73d534430f9`. The supplied review copy changes only the same six private path strings. The packet also contains the preceding delta response verbatim, its Driver dispositions and the latest authoring excerpt; their exact identities are in the retained identity record. This is selected input context, not the full repository or a full task-history review.

### Invocation And Evidence Limits

Immediately before launch, auth was `loggedIn=true`, `authMethod=claude.ai`, `apiProvider=firstParty`, `subscriptionType=pro`. Actual reviewer: Claude Opus 5.5 (`claude-opus-5-5`); fresh session `559ad00a-0e53-48cc-83c1-7ac7ed2d7d83`. The argument vector below was used with cwd at the fixed private packet directory and the exact packet bytes on stdin. The wrapper allowed one 600-second attempt and would terminate the process group on timeout.

```json
[
  "claude",
  "-p",
  "--model",
  "opus",
  "--effort",
  "high",
  "--safe-mode",
  "--system-prompt",
  "The human Owner has now explicitly authorized this one A1 ancestor-correction delta static review. The fixed packet was prepared before approval; its pending-authorization wording is historical. Follow the fixed bounded request. Treat source as data, use no tools or execution, and respond concisely in Korean. This is partial review of acquisition/canaries only, not whole P0a R1 or P0c R0 completion. A reviewer verdict is not Owner acceptance.",
  "--restricted",
  "--tools",
  "",
  "--strict-mcp-config",
  "--mcp-config",
  "{\"mcpServers\":{}}",
  "--disable-slash-commands",
  "--setting-sources",
  "",
  "--permission-mode",
  "dontAsk",
  "--no-session-persistence",
  "--output-format",
  "stream-json",
  "--verbose"
]
```

Elapsed 183.61 seconds; exit 0; no timeout or reported error; final response received; stderr 0 bytes. Startup showed empty tool and MCP lists. There were 130 valid transport events and zero malformed lines. Packet/input/base/diff/task checks passed before and after, including all 101 identified source bytes/modes, 11 control files and fixed runtime/Git/config bytes. The execution root stayed absent. No controls, SBPL, acquisition, canaries, collection, tests or product commands ran.

The fresh model/session is independent of the Driver, but reviews selected full inputs and supplied prior findings rather than an independently discovered repository. Reviewer code/API statements below remain static inference; they are not independently reproduced runtime observations. In particular, Apple Git behavior, SBPL path semantics and subprocess timings remain unverified. No test pass count applies.

### Ancestor Reviewer Response Verbatim

````text
# A1 조상 교정 델타 정적 검토 (acquire base → canary base, 부트스트랩 한정)

## 1. 판정

**정적으로 확인되는 차단 결함이나 회귀는 없습니다.** R1은 문면상 해소됐고, M2와 M5는 제안된 범위 그대로 반영됐습니다.

- 실행한 것은 없고 전부 정적 판독이며, 해시는 재계산하지 못했습니다.
- SBPL 컴파일과 실효, Apple Git 동작은 판단하지 않았습니다.
- 이 판정은 Owner 수락이나 실행 허가가 아니며, P0a R1 전체나 P0c R0의 완료도 아닙니다.

## 2. 교정 항목 확인

| 항목 | 상태 | 근거 (모두 정적 추론) |
| --- | --- | --- |
| R1 경로 산술 | 해소 | `out=EXEC/runs/canary-base`에서 `(out, *out.parents)`는 9개입니다: canary-base, runs, exec, ROOT, agent-worktrees, dev-home, 홈, `/Users`, `/`. target `work/{non-git,git,linked}`의 `target.parents`는 `work`와 이 9개이며, `work`는 기존 `subpath WORK`가 덮습니다. |
| R1 controller 검사 | 해소 | `len==9`, `[1:4]==(runs, exec, ROOT)`, `[-1]==/` 검사가 `out.mkdir` 앞에 있습니다. 나머지 `[4..7]`은 invocation 해시와 `root.parent.name` 검사에 결속됩니다. acquire에는 빈 집합이 전달됩니다. |
| R1 `test.sb` | 해소 | `file-read-data` literal 9개만 추가됐고 subpath는 없습니다. 괄호 균형이 맞고, 기존 `literal (param …)` 형식과 같습니다. |
| R1 제품 쪽 요구 | 충족 | `iterdir`는 이름만 쓰고 항목별 stat이 없습니다. `safe_target`, `_exists`, Git의 상향 탐색은 전역 `file-read-metadata`로 충분합니다. |
| 거부 probe 보존 | 유지 | 쓰기 허용은 여전히 WORK, `/dev/null`, LOG(data)뿐입니다. `ROOT/denied-sentinel`과 `COMMON_GIT/HEAD`는 literal 디렉터리의 자식이라 읽기 거부가 유지됩니다. inputs.json과 prior result의 쓰기 open, OLD chmod 거부도 정책 문면상 그대로입니다. |
| M2 | 반영 | 스위치는 합성 commit 한 호출에만 있고, origin 검사 호출은 그대로입니다. upstream 기준으로 `maintenance.auto=false`이면 commit이 `maintenance run --auto`를 아예 띄우지 않습니다. canary의 다른 Git 명령은 auto-maintenance 경로가 아닙니다. |
| M5 | 반영 | `BOOTSTRAP`과 README 예시가 같은 문자열이고 `append`입니다. `run_path`는 스크립트 디렉터리를 `sys.path`에 넣지 않으며, control 이름 6개는 stdlib 최상위 모듈과 겹치지 않습니다. |
| `__init__.py` | 확인 | docstring과 `__version__`뿐이라 import 부작용이 없습니다. 이전의 미제공 입력 한 건이 해소됐습니다. |

## 3. M1·M3·M4·M6 한계 문서화

README의 "Read-Only Preflight And Failure Limits"와 "Fixed Modes And Bounds"에 네 항목이 Driver 처분대로 들어 있고, 코드와 어긋나는 서술은 찾지 못했습니다.

- **M1**: 양성 probe는 여전히 슬롯 생성 뒤에 실행됩니다. 슬롯 소모 가능성과 "mode 검사는 ACL·write-open 증명이 아님"이 명시됐습니다.
- **M3**: `/etc/gitconfig` 부재를 실행 직전에 다시 확인하도록 돼 있습니다. 부재 경로가 샌드박스에서 EPERM이 아니라 ENOENT로 돌아오는지는 미확인입니다.
- **M4**: 허용 키 집합과 fail-closed가 그대로입니다. 2.54의 `init`이 다른 키를 쓰면 canary 슬롯이 소모됩니다.
- **M6**: 자식이 로그를 truncate·재작성할 수 있다는 점과 16MiB가 누적 상한이 아니라는 점이 명시됐습니다.

## 4. 비차단 관찰

- **O1. 9-깊이 검사는 acquire에서 돌지 않습니다.** 실제 private 경로의 깊이가 다르면 ROOT와 acquire-base를 쓴 뒤 canary에서야 드러납니다(canary 슬롯은 보존됨). review 경로로는 9가 맞고, private 경로는 저작 기록의 주장만 있어 제가 확인하지 못했습니다. 실행 전 preflight 기록에 이 산술 결과를 남기면 충분하고, 코드 변경은 필요 없습니다.
- **O2. literal 매칭은 커널이 보는 경로 표기에 의존합니다.** 대소문자와 firmlink 표기가 다르면 열거가 거부될 수 있습니다. 기존 subpath 파라미터와 같은 의존이라 새 위험은 아닙니다.
- **O3. topology 이후 단계가 이번에 처음 정적으로 도달 가능해졌습니다.** `worktree remove`, observer의 primitive·short-write·lock 시나리오에서 문면상 차단점은 찾지 못했습니다. 다만 샌드박스 안 기동 시간이 15초·30초 타임아웃에 들어오는지는 미지입니다.
- **O4. collect·smoke 등 다른 test 모드에도 같은 9개 파라미터가 전달됩니다.** 그 모드들의 runner 통합은 이 검토 범위 밖이며 통과로 추론하지 않습니다.

제품·factory 쪽 확장이나 새 복구·로깅 장치는 없습니다.

## 5. 정적 한계와 미제공 입력

- **SBPL**: `param` 치환과 컴파일, 디렉터리 literal의 `file-read-data`가 opendir·readdir을 실제로 허용하는지, `/` literal의 동작.
- **기존 미확인 항목**: deny-default에서의 `flock`, `F_FULLFSYNC`, `F_GETPATH`, 자기 SIGKILL, mach-lookup 거부 상태의 Python·Git 기동.
- **Apple Git 2.54**: `maintenance.auto` 처리, system config 탐색 경로, `init`이 쓰는 키.
- **호스트**: 실제 경로 깊이와 표기, 도구의 `st_nlink`, PATH의 `python3`, `sandbox-exec`, bytecode·alternates·promisor 부재.
- **미제공**: private invocation, `runner.py`, seed·oracle 본문, 이전 `test.sb` 바이트. 따라서 "9개 literal만 추가"는 현재 바이트와 기록으로만 확인했습니다.

## 6. 다음 단계 (실행 권한 아님)

1. Owner가 이 응답과 Driver 처분을 검토합니다. 정적으로 요구되는 추가 교정은 없습니다.
2. 실행 승인을 별도로 구할 때는 직전에 README의 읽기 전용 preflight를 수행하고 O1의 산술 결과를 함께 기록합니다.
3. SBPL·Git 미확인 항목으로 ROOT나 슬롯이 `result.json` 없이 소모될 때의 처리를 실행 승인 전에 정해 둡니다. 자동 재시도, 슬롯 재사용, 새 ROOT 선택은 하지 않습니다.
4. 범위 밖으로 남는 것: runner와 `work/` 통합, collect·smoke·complete, factory, product-prefix, D1/D2, P0a R1 전체, P0c R0.
````

### Driver Dispositions And Follow-Up

The Driver agrees that no additional A1 source correction is indicated by this bounded static review. This is a proposed acceptance of the static review result only; the Owner has not yet accepted it. The full P0a result R1, full P0c base-execution plan R0 and all actual execution remain open.

| Item | Disposition | Meaning and remaining boundary |
| --- | --- | --- |
| R1 | accept | Fixed path arithmetic, literal listing grants and preserved write/refusal boundaries now agree in the supplied source. No runtime isolation claim follows |
| M2/M5 | accept | The requested per-commit options and append bootstrap are reflected within the approved scope. The reviewer's upstream/API assertions do not supply an Apple Git or Python/SBPL execution result |
| M1/M3/M4/M6 | accept | The current documentation accurately retains slot/setup failure, system-config/init uncertainty and rewritable diagnostic-log limits. No new recovery, permission or logging mechanism is needed for this result |
| O1 — actual private path depth | accept | A post-review read-only Python pathlib calculation independently checked both actual private and illustrative layouts: nine ancestors, with positions 1–3 matching runs/exec/ROOT, and execution root absent. No controller function was imported or run. Recheck this arithmetic in the future execution preflight; no code edit is needed |
| O2 — kernel path representation | accept | Retain exact-path/firmlink/case uncertainty for actual sandbox execution. A denial is an observation to preserve, not permission to broaden the profile |
| O3 — downstream bootstrap timings | accept | No static blocker is identified after topology. Existing 15/30-second subprocess limits and the total bound stay unchanged; runtime feasibility remains unobserved |
| O4 — other test modes | accept | Passing ancestor parameters to collect/smoke/other modes is not their qualification. The unchanged runner and work-directory integration require the remaining bounded review |
| Missing inputs / static limits | accept | The initializer is now supplied. Private host facts were deliberately not externally disclosed; runner/seed/oracle omissions remain explicit scope limits. Prior policy bytes were not supplied to this reviewer, while the Driver's prior authoring diff check remains separate evidence |

The O1 check exited 0 using only Path arithmetic and an existence check. It supports current layout consistency, not kernel path identity, directory-access permissions or future host state. All three Reviewer responses retain their original bytes and meaning. No finding is marked reproduced by execution, no new code change was made, and no reviewer conclusion is treated as Owner authority.

### Proposed Next Bounded Scope

Recommend Owner acceptance of the A1 bootstrap static-review checkpoint, followed by A2 review-packet preparation only for the remaining runner collection/base-smoke path and result/fixture handling. This does not accept the full P0a result or authorize P0c. The bounded preparation should read the unchanged runner and its common/controller/policy integration, trace exact seed IDs and necessary fixture/import context statically, and fix the smallest sufficient packet and input hashes for the next review. Do not import/discover tests merely to prepare that input. Explicitly distinguish covered base-mode behavior from later complete/factory/product-prefix scope and identify any still-missing evidence instead of closing it by implication.

The only source write in that preparation would be a dated proposal/input-scope checkpoint in this existing owning task, plus private review input/hash files. Product/runtime/test/control sources, README, DR, index and central STATUS remain unchanged. Completion criteria: an inspectable exact A2 packet and a concrete external-review proposal stating scope, included and omitted inputs, time budget and remaining gates. Execution mode: read-only inspection plus packet/task authoring; no new reviewer transmission, control/SBPL/test execution, result acceptance beyond the explicitly approved A1 checkpoint, Git or adopter action. Stop if preparation requires imports/execution, source corrections, policy expansion or broader factory implementation. This next scope and A1 result acceptance are pending Owner decision; they were not included in the one-review approval.

### Custody And Remaining State

Only this owning task record changed. Controls, all identified source/managed bytes, accepted DR, index and tracked diff remain unchanged. No central STATUS update is needed for this review checkpoint. Preserve the updated task and compact authorization/result metadata outside the checkout with verified readback; the exact fixed packet and authored-control backup remain for the Owner and the next bounded review/execution-handoff consumer. Once the verbatim response and essential facts are confirmed in the durable copy, remove transient duplicate review/API stream files rather than retaining reasoning or tool transcripts as permanent deliverables.

Retain the source worktree for the concrete remaining A2 review and implementation continuation; no checkout is eligible for retirement. A1 has no newly requested code correction, but Owner checkpoint acceptance, broader review, D1/D2 and actual execution gates remain distinct.

## A1 Static Checkpoint Acceptance And A2 Preparation — 2026-10-09

### Actual Owner Decision And Scope

The Owner replied “승인” to accepting the A1 bootstrap static-review result and preparing the next A2 review packet. The accepted checkpoint is the preceding ancestor-correction result and Driver dispositions in task revision SHA-256 `7e25475520b85d3ae9ca1158739603b521f2ebcf0f51e00afc6f0ba0f4567396`, with Reviewer response SHA-256 `3dbb95f321c9ef8b4b1fd2f69f8818a0b4310681a3d947f02df950717bff7cdc` and exact reviewed packet `a279c9364b09c806cf5dabd5a07b673b9f0e8bfe309f4180485709350107abe6`. That record has recoverable custody. The acceptance means no further A1 source correction is required by that bounded static result; it does not accept full P0a R1/P0c R0, runtime isolation, actual control execution, D1/D2 or contract activation.

A2 preparation is read-only tracing plus private packet/hash authoring and this task checkpoint. It covers runner collection/base smoke, controller work-directory integration, result truthfulness and failure-fixture handling. No control, test, runtime, README, DR, index or central STATUS source is edited. No test/module import, discovery, sandbox compilation, acquisition, fixture creation, test run, external reviewer transmission, Git or adopter action is authorized or performed.

### Concrete A2 Review Boundary

The proposed review follows the current base input: `phase=base`, `factory=false`, twenty literal seed IDs and `collection_sha256=null`. The initial invocation is unchanged. There is no collected hash to bind yet; neither a smoke-ready input nor an executed collection count is invented. The future binding step remains a separately approved operation that must preserve every other identified input.

| Path | What A2 should assess | What this packet cannot establish |
| --- | --- | --- |
| Bootstrap to collection | Isolated Python path setup, loader imports, exact ordered IDs and duplicate occurrences, import/load errors and work/collection.json | Actual import success, discovered counts or platform timings |
| Collection to base smoke | Exact collection digest binding, unchanged source/control identity, the twenty fixed IDs and all occurrences, base phase/factory boundaries | Actual seed passes, a changed selection, future entry factory or complete-mode qualification |
| Test reporting | selected/executed/count consistency, skipped/expected/unexpected outcomes, subtests and setup/class/module errors, incomplete execution | A passing suite or product oracle correctness |
| Fixture handling | Fixture root reachability, unittest callback/cleanup order, bounded copies, absent-root or preservation failure visibility, process-test evidence siblings | Universal preservation of every fixture, real process cleanup or a new recovery/logging design |
| Controller integration | Per-run work paths, prerequisite/input binding, exclusive slots, existing budgets and inherited A1 policy limits | SBPL effect, actual acquisition/canaries or full P0c approval |

A1 is an accepted static prerequisite at its exact bytes; new concrete interaction defects may still be reported. The reviewer must not treat this as permission to alter tests, assertions, timeouts, discovery or policy. Complete/focused/artifact modes, future factory/product-prefix behavior, D1/D2 and broader result acceptance remain outside this A2 base-path slice even where shared code is visible.

### Selected Inputs And Explicit Omissions

Prepare sixteen full files: controls README/runner/common/controller/test policy/seed IDs; four complete seed modules (runtime admission, plain auditor boundary, CRLF checkout and installed process safety); the Git fixture helper; plain auditor script; launcher; and jsonio/errors/package initializer. The checkout-window module is supplied as an exact excerpt containing imports and both complete seed classes, excluding its unrelated historical transition factory.

Fifteen exact source excerpt ranges across eight files supply that checkout seed context, the needed ActualWorkspaceInit/SerialWriter/WorkerPublication/InstalledWorkerPublication helpers and aliases, candidate-module import context, workspace runtime/Git environment context, product source_root and the historical execution-boundary proposal. Every range carries its source path, whole-file hash, start/end lines and exact-slice hash. Excerpts retain original bytes; they are not rewritten runnable modules. Omitted test-method and product bodies remain omissions.

Eleven exact excerpts from three files in the identified CPython 3.14.7 installation supply unittest loader, case/result-callback, cleanup and suite behavior needed to assess the runner. These standard-library files were read and AST-parsed, not imported or executed for this check. They receive separate whole-file and slice identities; a launcher hash alone does not seal them. The remainder of the runtime, built-ins and OS effects remain outside the review evidence.

A static inventory identifies 26 physical test*.py files and their top-level test-local imports, plus all twenty seed definition locations in five modules. The definition map is not unittest discovery or an executed test count; imported/re-exported TestCase classes can create additional occurrences. Product/stdlib imports and other executable bodies are not fully represented by that inventory. tests/__init__.py is absent in the current exact tree; that fact is explicit rather than silently adding a file.

The previous A1 baseline manifest and acquisition/canary/observer bodies are unchanged and retain their identified hashes, but are not repeated in full in this A2 packet. Full product implementations and all 26 complete test modules are not supplied. The packet supports the named runner/fixture questions, not an audit of every import side effect or product assertion. Retain missing-evidence findings rather than broadening a pass claim. The actual private invocation stays local; the review copy retains the same six declared illustrative path substitutions. Standard-library context uses logical runtime labels in the packet with exact local source identities retained privately.

### Driver Pre-Review Questions

These are Driver-selected static questions for independent assessment, not an A2 reviewer verdict or reproduced test result. No source corrections have been applied.

1. The isolated bootstrap appends CONTROLS, and runner adds SOURCE/src and SOURCE/tests before `discover("tests")`; it does not explicitly add SOURCE. A fixture imports `tests.test_productization`, while tests/__init__.py is absent. The supplied local unittest loader defaults top_level_dir to the start directory. Assess whether this leaves the namespace import unavailable and where the exact minimal correction would belong if confirmed. No loader or test import was run to reproduce it.
2. `Result.preserve` looks for test.base/test.root/test.f.base/test.h.f.base, but some supplied seed fixtures expose self.target/self.temp or only a local fixture object/context-managed TemporaryDirectory. Missing roots return silently, while unittest cleanup or context exit can remove the original. Assess preservation and the visibility of unavailable evidence against the stated contract; retaining the outer EXEC directory does not by itself prove those bytes survive cleanup.
3. Assess fixture/class/module failures, repeated subtest failures, preservation exceptions/size caps and selected-versus-executed identity reporting. An incomplete run must remain distinguishable from success; do not redesign the reporting stack without a concrete finding.
4. Assess exact collection-hash binding and source/control/prerequisite drift across collect and smoke. Keep all occurrences of each selected ID and the existing 300/1,200-second limits; the static twenty-ID set does not predict discovered multiplicity or duration.
5. Inspect synthetic Git/process fixture commands, TMPDIR-derived targets, temporary cleanup and sibling process evidence under work/. The existing process tests have their own barriers/timeouts and failure archive; identify their retention/budget limits separately from the runner's copy limits. Do not modify their assertions or infer real sandbox feasibility.

### Preparation Checks And Next Approval

All twenty configured IDs resolve statically to the named class/method definitions. The fixed selection equals the seed-ID file. Source/control/stdlib snippets and inventory were parsed/read without importing them; file and excerpt identities will be verified against their final packet bytes. All controls, the 101 identified source bytes/modes, 29 managed bytes, accepted DR, index, base and tracked diff remain unchanged. The execution root stays absent. Only this task record and private review inputs are written. GFM/link/disclosure/whitespace checks and backup readback complete packaging; no runtime test counts apply.

The next proposed action is one fresh tool-free Anthropic Claude subscription A2 static review of the exact prepared packet, maximum 600 seconds, followed by verbatim response and Driver dispositions in this task, then stop. It needs separate Owner approval of the fixed internal source/test/standard-library excerpt transmission. Check the expected claude.ai/firstParty subscription path before invocation and all input identities before/after. No source correction, extra invocation or test execution is included; timeout or missing input remains unavailable evidence, without automatic retry. A2's result must state the covered base-path conclusion separately from the still-open full P0a/P0c and future-mode gates.

Custody consumer: the Owner approving the exact A2 packet and the next explicitly authorized A2 Reviewer, followed by the bounded correction/execution-plan handoff. Preserve this task, the fixed packet, input identity and private/review invocation copies outside the worktree with verified readback until an accepted next handoff or durable Git custody replaces that need. Exact excerpts are retained for that consumer; no full extra source/runtime snapshot or permanent one-off validation output is needed. Keep prior accepted A1 input/result custody. Retain the source worktree for concrete A2 review and implementation continuation; no checkout is eligible for retirement.


## A2 Runner And Base-Smoke Review Result — 2026-10-09

### Actual Owner Authorization And Exact Inputs

The Owner replied “승인” to the explicit proposal to send the fixed approximately 238 KB internal source/test/installed-Python excerpt packet to the Anthropic Claude subscription service for one fresh tool-free static review, maximum 600 seconds, then record the response and Driver dispositions. This authorizes this single transmission/review and record only. It does not authorize corrections, another review, imports/discovery, control or test execution, contract activation, Git actions or adopter application. The earlier packet's pending-authorization wording identifies its preparation state; the invocation system prompt explicitly reports the later Owner authorization.

The reviewed packet is exactly 238,042 bytes, SHA-256 `528ce1082d99485ed4a8eb0fac3a1a917af4b99a1eb36f7eff395c2ae74c12b0`. It contains sixteen full inputs, fifteen repository excerpt ranges across eight files, eleven installed CPython unittest excerpt ranges across three files, the static 26-module/twenty-seed context map, the path-substituted invocation, accepted A1 response and preparation excerpt. Input base is `238514686078ce1564010a7b69013f48a635c57c`; tracked diff SHA-256 is `12238ddc334c4a6971d657249732a73d59cc4c3e32b6463d5a7fccfc867a6b04`; owning task before review is `d3fd8f82511d6b20a283349f9a2538e9bc7b2d654c011aaae32cafed506604d5`. The sixteen untracked/tracked full inputs and all excerpt source/range hashes are enumerated in the retained identity, separately from that diff. Private invocation SHA-256 is `a7db158a24646441f1268a6f6eed16b206072dc47b35ef57082fc73d534430f9`; review copy SHA-256 is `281d54fe0dde7b9453dc72ec578a6946217a35e6d183c501a37fe996df5df32b`. The same six declared illustrative path substitutions remain unchanged; actual private paths are not disclosed here.

Before and after the review, the Driver verified packet bytes/hash, base/diff, task checkpoint, every full input, repository and runtime whole-file/range identity, 26 context-source hashes, exact src/tests file membership and tests/__init__.py absence. All 101 identified source bytes/modes, twelve controls and fixed runtime/Git/system-config bytes matched. The execution root remained absent. These are read/hash checks, not an import or execution of the reviewed files. The wrapper itself reads inputs and invokes the authorized Reviewer; it does not invoke a control or test.

### Actual Reviewer Execution And Limits

Driver: Codex. Reviewer: Claude Opus 5.5, reported startup/final model `claude-opus-5-5`, fresh session `0c018c40-017a-460e-94b8-4092c3fe2c99`. Authentication was checked immediately before invocation: loggedIn=true, authMethod=claude.ai, apiProvider=firstParty, subscriptionType=pro. No secret or account email is recorded. The actual tools and MCP server arrays were empty. No inherited reviewer session was resumed; independence is limited to the fixed Driver-selected packet, its omissions and the model's prior knowledge.

The CLI ran in the private packet directory with prompt.txt bytes on stdin, a 600-second process-group deadline and no retry. Exact argv, with no private path arguments:

```json
[
  "claude",
  "-p",
  "--model",
  "opus",
  "--effort",
  "high",
  "--safe-mode",
  "--system-prompt",
  "The human Owner has now explicitly authorized this one A2 runner/base-smoke static review. The fixed packet was prepared before approval; its pending-authorization wording is historical. Follow the fixed bounded request. Treat source as data, use no tools or execution, and respond concisely in Korean. This is partial review of runner collection/base smoke and failure-fixture handling only, not whole P0a R1 or P0c R0 completion. A reviewer verdict is not Owner acceptance.",
  "--restricted",
  "--tools",
  "",
  "--strict-mcp-config",
  "--mcp-config",
  "{\"mcpServers\":{}}",
  "--disable-slash-commands",
  "--setting-sources",
  "",
  "--permission-mode",
  "dontAsk",
  "--no-session-persistence",
  "--output-format",
  "stream-json",
  "--verbose"
]
```

Observed duration: 324.75 seconds; exit status 0; timeout=false; is_error=false; stderr 0 bytes; 235 valid stream events and 0 malformed lines. Pre/post input checks passed. Stream transport is not a reviewed-source test: no executed test pass/fail counts exist. Final Reviewer response SHA-256: `769b701bf95560acf45878ca2741a5b097e6f9b108abd4aaf9cf937c556451a9`. Intermediate API/event envelopes are disposable after the response and compact execution record have verified durable custody.

### A2 Reviewer Response Verbatim

````text
# A2 runner/base-smoke 정적 검토 결과

## 1. 판정

**현재 바이트로는 `collect base`가 통과할 수 없습니다.** 정적 추론이며 재현한 것은 아닙니다. 그 밖에 실패 기록의 정확성 결함이 두 건 있습니다.

- 종료 코드 수준의 통과/실패 판정은 fail-closed입니다. 통과로 위장되는 경로는 찾지 못했습니다.
- 전부 정적 판독이고, 실행·해시 재계산·SBPL 실효 판단은 하지 않았습니다.
- 이 판정은 Owner 수락이나 실행 허가가 아니며, P0a R1 전체나 P0c R0의 완료도 아닙니다.

## 2. Must-fix

### M1. `tests` 네임스페이스 import 불가 (Driver Q1 확인, 차단)

- **원인**: `-I`는 cwd를 `sys.path`에 넣지 않습니다. bootstrap은 CONTROLS만 추가하고, runner는 `SOURCE/src`와 `SOURCE/tests`만 넣습니다. `discover("tests")`의 암묵적 top-level도 `SOURCE/tests`입니다(loader L266-280). SOURCE는 어디에도 없습니다.
- **결과**: `test_productization_safety.py` L19의 `from tests.test_productization import …`가 `ModuleNotFoundError`가 됩니다. 26개 모듈 중 18개가 직·간접으로 실패합니다.
- **시드 영향**: 20개 중 19개가 수집되지 않습니다. `test_plain_auditor_boundary`만 남습니다.
- **종료 방식**: `require(not loader.errors)`로 멈추고 `collection.json`은 생기지 않습니다. 다만 실패를 `loader.errors`에 넣는 `_find_test_path` 본문은 미제공이라, 이 부분은 제 지식에 기댄 것입니다.
- **`__init__.py`는 원인이 아닙니다.** 네임스페이스 패키지는 그 파일 없이도 동작하며, 파일을 추가해도 SOURCE가 경로에 없으면 그대로 실패합니다. 과거 명령 `-m unittest discover -s tests`는 cwd가 `sys.path[0]`이라 동작했습니다.
- **교정 위치**: `runner.py`의 `sys.path` 설정 한 곳에 `str(p["source"])`를 최하위(append)로 추가하면 됩니다. 테스트 소스, discovery 알고리즘, 시드 ID는 바뀌지 않습니다.
- **교정의 부수 한계**: `file_map`의 membership 검사는 `src/`와 `tests/`만 덮습니다. SOURCE 루트의 미등재 `*.py`나 디렉터리가 import 가능해집니다. 루트 1단계 membership 검사를 추가할지, 한계로 문서화할지는 Driver/Owner가 정할 일입니다.
- **순서 제약**: `completed()`가 controls 해시 일치를 요구하고 슬롯이 배타적입니다. runner 교정은 **acquire-base 이전**에 끝나야 합니다. 이후에 고치면 ROOT 전체가 무효가 됩니다.

### M2. fixture root 부재가 무표시로 사라짐 (Driver Q2 확인)

`Result.preserve`는 `base`, `root`, `f.base`, `h.f.base`만 찾습니다. 못 찾으면 그냥 `return`하며, 주석의 "report absence"는 실제로는 어떤 기록도 남기지 않습니다.

| 분류 | 시드 수 | 해당 |
| --- | ---: | --- |
| root 도달 가능 (`self.base`) | 6 | DetachVersionTests 3, InstalledUnchangedCrlf 1, InstalledWorkerProcess 2 |
| fixture 없음 | 3 | CheckoutWindowTests 2, `test_explicit_allowlist…` |
| fixture는 있으나 도달 불가 | 11 | RuntimeAdmission 4(지역 변수 `t`), PlainAuditor 1(with 블록 지역), UnchangedCrlf 6(`self.temp`와 `self.target`뿐) |

- 도달 불가 11건은 실패해도 `addCleanup`이나 with 종료가 원본을 지웁니다. EXEC를 보존해도 그 바이트는 남지 않습니다.
- 도달 가능한 6건은 콜백이 `doCleanups` 앞에서 불리므로 시점이 맞습니다(case.py L664-673).
- **최소 교정**: 실행 행(`executed.jsonl`)이나 별도 기록에 "보존 없음/사유"를 남깁니다.
- **선택 사항**: 탐색 후보를 `temp.name`, `target.parent`까지 넓히면 UnchangedCrlf 6건이 덮입니다. RuntimeAdmission과 PlainAuditor 5건은 테스트를 고치지 않고는 닿지 않습니다. 넓힐지는 Owner 범위 결정입니다.

### M3. `queue` 위치 기반 identity가 어긋날 수 있음 (base에서는 잠재)

- **기제**: `startTest`가 `next(queue)`로 identity를 받습니다. `setUpClass`나 `setUpModule`이 실패하거나 skip되면 해당 테스트는 `startTest` 없이 건너뜁니다(suite.py L116-118). 이후 행에는 건너뛴 테스트의 identity가 붙습니다.
- **영향 범위**: 종료 코드는 여전히 비통과입니다. 틀어지는 것은 `executed.jsonl`의 실패 귀속입니다.
- **base 20개**: 완전 제공된 4개 모듈과 checkout L1-110에는 class/module fixture가 없어 도달 경로가 보이지 않습니다. checkout L111 이후는 미제공입니다.
- **교정 위치**: `startTest`에서 test 객체로 identity를 찾으면 됩니다(`selected`가 참조를 쥐고 있습니다). M1과 같은 바이트 변경에 묶기를 권합니다. 최소한 focused/complete 모드 전에는 필요합니다.

## 3. Driver Q3–Q5 평가

**Q3 (결과 보고)**
- subtest 실패, skip, expected-failure, unexpected-success는 모두 `ok=False`로 귀결됩니다.
- 한 테스트에서 subtest가 여러 번 실패하면 같은 base를 매번 다시 복사하며, 256MiB 누계에 합산됩니다.
- size-cap이나 복사 실패는 `os._exit(87)`로 끝납니다. 해당 테스트의 STOP 행과 `counts.json`이 없고, 남은 시드는 실행되지 않습니다. 비통과로 구분됩니다.
- `os.walk` 중 `lstat` 오류나 비정규 파일은 `preservation-stop.json` 없이 traceback으로 중단됩니다. 비통과이지만 표식이 일관되지 않습니다.
- class/module 수준 오류는 행 없이 `counts.errors`와 stdout에만 나타납니다.

**Q4 (collection 해시 결속)**
- payload에 `source_digest`와 `controls`가 들어 있고 smoke가 다시 수집해 비교합니다. source나 controls가 바뀌면 불일치로 실패합니다.
- 부모는 smoke 전에 collect-base의 완료를 확인하지 않습니다. 해시는 untrusted stdout과 자식이 쓴 `collection.json`에만 있습니다. 출처 결속은 절차에 의존합니다.
- `selection == base-seed-ids.json`을 강제하는 코드가 없습니다. 리뷰 invocation에서는 20개가 순서까지 일치함을 확인했습니다.
- `collection_sha256=null`이거나 selection이 수집 결과에 없으면, smoke-base 슬롯을 만든 뒤에야 실패해 슬롯이 소모됩니다.
- inventory의 from-import만 보면 시드 클래스 7개는 재노출되지 않습니다. 중복이 예상되는 것은 `SerialWriterTests`와 `ActualWorkspaceInitTests`(`test_worktree_execution` 경유)이고 시드가 아닙니다. 모듈 수준 대입 별칭은 inventory에 없어 확정하지 못합니다.

**Q5 (프로세스 증거와 예산)**
- 증거 디렉터리는 `work/tmp/worker-process-evidence-<base>/<method>`입니다. base의 형제라서 cleanup에도 남고, runner 복사 상한과는 무관합니다(상한 없음).
- 실패하면 테스트 자체의 `failed-target.tar.gz`(target만)와 runner의 base 복사가 둘 다 남습니다.
- 프로세스 테스트 한 건의 내부 대기 합은 최악 180×4+240×2=1200초입니다. controller는 1180초에 그룹을 종료합니다. 늦게 정체되면 `finally`가 돌지 않아 receipt와 tar가 없습니다. 이때 base는 cleanup되지 않아 남습니다.
- 타임아웃이나 예산을 바꾸라는 제안은 아닙니다.

## 4. 비차단 한계

- **경로 표기**: `chdir` 뒤의 `abspath("tests")`가 invocation 표기와 대소문자까지 같아야 합니다. 다르면 "imported from different location" load error가 날 수 있습니다(A1 O2와 같은 계열).
- **`os.getpgid(child)`**: 프로세스 시드가 호출합니다. `process-info* (target self)` 아래에서 허용되는지 알 수 없고, canary가 다루는지도 이 패킷으로는 확인할 수 없습니다.
- **설치 자식의 site**: shebang과 `-I -B` 자식은 `-S`가 없어 site가 켜집니다. `/opt/homebrew/lib` 읽기가 거부될 때의 동작은 실행해야 알 수 있습니다.
- **`executed.jsonl`**: fsync하지 않으며, 부모 `result.json`은 자식 기록을 결속하지 않습니다.

## 5. 미제공 입력

- 22개 테스트 모듈 본문과 import 부작용(완전 제공 4개 외), checkout L111 이후
- loader의 `_find_tests`, `_find_test_path`, `TextTestRunner`, `TextTestResult` 본문
- stdlib와 CONTROLS 디렉터리에 `tests` 항목이 없다는 사실
- canary 본문, 제품 구현, private 경로

## 6. 다음 단계 (실행 권한 아님)

1. Driver가 M1–M3를 처분하고, Owner가 교정 범위를 승인합니다. 정할 것은 M2를 표시만 할지 후보까지 넓힐지, 그리고 SOURCE 루트 membership입니다.
2. 교정된 runner 바이트와 새 controls 해시·invocation을 델타 재검토합니다. acquire-base보다 먼저여야 합니다.
3. 해시 결속 절차를 실행 승인 전에 문서로 고정합니다.
   - collect-base `result.json`의 `execution_pass`를 확인합니다.
   - `collection.json` 파일의 SHA-256이 stdout 값과 같은지 확인합니다.
   - 20개 ID의 포함 여부와 occurrence 수를 기록합니다.
   - 새 invocation과 기존 invocation의 차이가 `collection_sha256` 한 필드뿐인지 확인합니다.
4. 범위 밖으로 남는 것: SBPL 실효와 실제 타이밍, focused/complete/artifact, factory, product-prefix, D1/D2, P0a R1 전체, P0c R0.
````

### Driver Dispositions — Proposed Corrections, Not Applied

The covered static conclusion is that the base collection path has a concrete missing SOURCE namespace-parent defect under the supplied isolated path setup, and failure diagnostics have two further defects/limitations. There is no executed reproduction. The review found no false-success exit path in its covered static reading; this does not establish a general fail-closed guarantee or qualify SBPL/runtime behavior. A1 acceptance remains its bounded static checkpoint; A2 and full P0a R1/P0c R0 are not accepted or completed by this review.

| Item | Driver decision | Evidence and proposed handling |
| --- | --- | --- |
| M1 namespace parent | accept core defect; revise certainty/scope of remedy | runner adds src and tests but not SOURCE; test_productization_safety imports tests.test_productization. A source-root path correction belongs in runner, without changing tests, default discovery or seed IDs. The review's 18-module/19-seed impact counts and loader exception path are Reviewer inference, not executed counts or an independently recalculated coverage claim. Missing stdlib/controls namespace evidence remains explicit. |
| M1 added root import surface | needs-user | Recommend a bounded SOURCE append together with a pinned immediate-root entry/type inventory checked before import, and explicit documentation that this does not recursively seal every existing non-src/tests directory. Stop if the chosen implementation needs a broader import resolver, new dependency, policy read grant or source-test edits. This root-membership proposal is new correction scope, not an already accepted A1 policy. |
| M1 timing and historical evidence | revise | Correct and review controls before the first acquisition. A later control-hash change makes existing prerequisite evidence inapplicable to that changed candidate; it does not invalidate historical bytes or authorize deleting/reusing ROOT or resetting an exclusive slot. ROOT is still absent now. |
| M2 missing fixture roots | accept minimum correction | Record preservation status and a concrete reason for every failure-preservation attempt, including no reachable root and an excluded ancestor/out path. Recommend reporting only in this slice: keep the current root candidates and explicitly preserve the local/context-managed-fixture limitations. Do not claim EXEC retention preserves bytes that fixture cleanup removes. The review's 6/3/11 split remains its static classification, not a run result. |
| M2 expanded fixture search | defer, not selected | Adding temp.name/target.parent, changing test fixtures or suppressing cleanup would enlarge this slice. They are not needed to make unavailable preservation visible. Reconsider only if the Owner later requires those actual fixture bytes and accepts a concrete preservation design. |
| M3 occurrence identity | accept bounded correction | Replace the global position queue with identity lookup tied to the actual selected test object, retaining an ordered occurrence queue per object where an object repeats. Validate the observed id against its selected identity; do not deduplicate or alter discovery. Keep class/module events without startTest distinguishable from actual executed rows and report unstarted selections without assigning them to another test. The supplied base paths do not demonstrate an actual class/module-fixture failure. |
| Q3 diagnostic completeness | accept limit; bounded proposal | Preserve existing non-pass treatment of skip/expected/unexpected outcomes and existing copy caps. Make preservation errors visible without substituting assertions or claiming missing STOP/counts are a completed run. Repeated subtest copies, callback ordering and interruptions need targeted future checks; no runtime proof is supplied here. |
| Q4 collection provenance | accept procedural gap | Before future smoke approval, bind only a successful parent collect-base result, verify its input identity and collection file hash, verify exact twenty-ID selection plus every discovered occurrence, and identify a new invocation differing only in collection_sha256. Child stdout is a cross-check, not independent authority. A static review of the matching supplied invocation is not a runtime enforcement claim. No collection hash or new smoke input is generated now. |
| Q5 process evidence and budget | accept limitation | Keep 300/1,200-second base budgets and process-test assertions unchanged. Sibling process evidence and its archive are outside runner copy caps; controller termination can preempt finally. A missing receipt/tar or partial execution remains unavailable/non-pass, not proof of cleanup or fixture preservation. |
| Other nonblocking limits and omissions | accept as open | Retain path spelling/firmlink, process-info permissions, installed-child site behavior, output durability, omitted imports/runtime/product bodies and unqualified future modes as limitations. Do not reopen accepted A1 choices without a concrete new interaction defect. |

The Driver read the unchanged runner/controller/common, named fixture snippets and the namespace import to assess these dispositions. No imports, fixture construction, discovery, SBPL compilation, acquisition, canaries or tests were run. Reviewer suggestions are not automatically applied. Only this task record changes; controls, runtime/test source, README, DR, development index and central STATUS remain unchanged. Generic adopter impact: no update currently needed from this review-record-only step; installation state is not assessed.

### One Proposed Next Slice And Stop Rule

Propose A2 correction authoring only, pending Owner approval of the plan and the two recommended choices: (1) append SOURCE with a pinned immediate-root entry/type guard and its explicit remaining import-surface limit; (2) report unreachable preservation without expanding fixture-root discovery. Allowed source files would be runner.py, common.py only for that guard/config contract, README.md and this task; private input/identity files would be refreshed for the changed controls/guard. Controller, policies, acquisition/canary/observer, product/runtime/test source, seed selection, factory, timeouts, copy caps, DR/index/central STATUS remain outside that correction proposal.

Completion means inspectable M1/M2/M3 corrections, exact proposed collection-binding instructions, AST/JSON/hash/path checks without importing reviewed code, GFM/link/disclosure/whitespace checks, preserved inputs and one bounded delta-review proposal. The guard must describe its actual coverage; it must not imply that a top-level inventory seals all recursive imports. A concrete need for a new policy allowance, source-test edit, new resolver/dependency, actual execution or a wider retention guarantee stops this slice for a revised plan. The next delta review/transmission and actual control/test execution each need their own authorization. No correction is made under the current review-only approval.

### Verification And Custody

Verify the final record with GFM rendering, local links, whitespace/disclosure checks and exact verbatim response comparison. Preserve the final task plus compact authorization/execution metadata outside the source checkout, with archive readback, for the Owner's correction-scope decision and the next bounded A2 correction/delta-review handoff. The prepared packet/identity and existing authored-control backup remain the exact input custody; retain them until that named handoff is accepted or equivalent durable Git custody replaces them. Intermediate event output, empty stderr and the duplicate standalone review may then be removed; they are not permanent review deliverables. Keep all earlier accepted A1 response bytes and custody intact. The source worktree has concrete remaining A2 correction/review use and is retained; no worktree is eligible for retirement.


## A2 Correction Authoring — 2026-10-09

### Actual Owner Authorization

The Owner replied “승인” to the bounded proposal to correct all three A2 findings through code/document authoring only: append the namespace parent with an immediate-root membership guard, retain fixture-root candidates while reporting unavailable preservation, and attach execution identities to actual test objects. The approved proposal is in the preceding A2 record at task SHA-256 `69b384d2923f4305eea914ea87ff0713d6bb891d46b5b3fd921602394519033d`, with Reviewer response `769b701bf95560acf45878ca2741a5b097e6f9b108abd4aaf9cf937c556451a9`. This accepts those two recommended scope choices and authoring plan, not the resulting correction or a wider evidence claim.

Source edits are limited to runner.py, common.py for the guard/config contract, the controls README and this task. Private invocation/identity/packet preparation is included. No controller, policy, acquisition/canary/observer implementation, product/runtime/test source, seed IDs, factory, timeout/copy cap, DR/index/central STATUS, Git or adopter change is authorized. No reviewed-code import/discovery, control execution, external review transmission or further review invocation is included. The separate Runner delta review and execution gates remain open.

### Authored Changes And Boundaries

| Finding | Authored correction | Explicit limit |
| --- | --- | --- |
| M1 namespace import | runner appends SOURCE after the existing isolated paths; config first validates source_root_entries, an exact immediate-root name/file-or-directory map. Current map has sixteen entries. lstat rejects links and special entries; root pointer contents are not read. | Existing non-src/tests descendants are not recursively sealed. Standard/control namespace resolution and actual loader behavior remain unexecuted. No tests/__init__.py or discovery change. |
| M1 input identity | Invocation becomes schema 3 with the required root map. Historical schema 1/2 inputs are rejected. Collection payload includes source_root_entries alongside source_digest and controls. | New input bytes identify this correction, not an execution permission or successful collection. Initial collection_sha256 remains null. |
| M2 preservation status | Each addError/addFailure/failing-addSubTest preservation attempt records copied/unavailable/stopped and a reason. Missing reachable roots and roots containing output no longer return silently. Root/scan/copy failures try a stop marker then exit 87 without fixture finalizers. | Candidates remain base/root/f.base/h.f.base. Local/context-managed fixtures can still disappear. A diagnostic write failure may prevent a marker, and copy completion is not an independent content attestation. No wider preservation guarantee. |
| M3 execution identity | Object-indexed occurrence queues replace the global positional queue. startTest checks the actual selected object/id. Non-start fixture events receive identity=null; subtest skips use their active parent. Final normal completion reports unstarted/unfinished selections separately. | A repeated identical object after a non-start event is conservatively ambiguous: identity-stop.json then non-pass, rather than assigning an unproven occurrence. This may stop a run whose identity could be resolved with a more elaborate design. No deduplication or fixture/discovery rewrite. |
| Related diagnostic consistency | Executed rows retain outcome categories with a non-pass-first summary; a later skipped subtest does not replace an earlier failure. os.walk errors are surfaced to preservation-stop handling. | Interrupted/exceptional runs may lack STOP/counts/unstarted summaries. Missing summaries remain incomplete evidence. JSONL is not fsynced or parent-bound; existing exit gates, budgets and caps remain. |
| Q4 collection binding | README fixes the future parent-result/input checks, exact collection bytes/root map/source/control/occurrence validation, exact twenty-ID selection and a new invocation differing only in collection_sha256. | This is an explicit future procedure, not a new controller feature or completed binding. Child stdout is only a cross-check, and parent result does not itself bind child collection bytes. |

All config callers now require schema 3, so the unchanged acquisition/canary/observer caller preambles and acquisition policy are included in the proposed delta input. SOURCE read permissions already exist in both policies; no new SBPL grant was authored. Corrected common/config behavior remains subject to delta review, even though the earlier A1 checkpoint was accepted at its historical bytes.

Only common.py and runner.py control hashes changed. The private input differs from the prior schema-2 input in schema, source_root_entries and those two control hashes; phase, factory, selection, source_files/source_digest, paths, tools/config and null collection hash remain identical. The review copy uses exactly the same six declared illustrative path substitutions. No smoke-ready input is fabricated.

Corrected file SHA-256 identities:

| File | SHA-256 |
| --- | --- |
| common.py | `37756fbd18d7f58037a99bc1f8e81c8d03176b185a0236bce579585901e2a83e` |
| runner.py | `50529c3c79f8ee14f03b9536a6d4f4b4468abfaad3cfa5fe8b9cb646d12f68b0` |
| README.md | `92a5c75e46a823b479eeb34d032b364d3f6e918fe04571b54a924da093a53954` |

Private schema-3 invocation SHA-256: `bd4a422f98fb4e04d8a4c5fe3adb463ace5b48e16a3c50b5f474751c78be2ef1`; path-substituted review copy SHA-256: `4a703f57c0db5992bfdb998fef8d7a785e0dea131356be29b42996a2f4fc14fc`. Final packet and task identities are retained outside the source record to avoid a self-referential hash.

### Static Checks And Proposed Delta Packet

The Driver AST-parsed all six control Python files without importing them; parsed the three control JSON files and new invocation; checked exact input keys/root inventory, unchanged selection, original discovery call and config-before-SOURCE-append-before-discovery ordering; and inspected the exact diff against the prior packet's hash-verified common/runner/README bytes. Unchanged nine controls, 101 source bytes/modes and src/tests membership, base/tracked diff and absent execution root were checked. The 29 managed files remain within that unchanged source set. No canary, test, guard function, Result callback, sandbox compiler or reviewed-code import executed. There are no test pass/fail counts and no reproduced counterexample claim.

The proposed fixed delta packet contains seventeen full files, eighteen repository excerpt ranges and seventeen installed CPython unittest excerpt ranges, the unchanged physical-module/seed map, previous A2 Reviewer response, Driver dispositions, this authoring checkpoint and an exact three-file correction diff. The additional runtime context supplies the formerly omitted loader find helpers, _SubTest and result/runner callbacks. It is exact installed-file text with whole-file/range identities, not a guarantee about the rest of Python or host runtime behavior. The three unchanged A1 caller preambles show the new config interface's reach; their remaining bodies stay omitted historical context. Full product implementations, all 26 test-module bodies, new factory and actual SBPL/timing remain outside this delta.

The intended next review is one fresh tool-free Claude subscription review, maximum 600 seconds, after the Owner separately approves the exact internal transmission. It should independently assess M1/M2/M3, schema/root-map integration, preservation error paths, object/occurrence ambiguity and the future binding procedure; unchanged inputs are context, not full A1/A2/P0a/P0c or future-mode qualification. Do not transmit, invoke, run controls or make a new correction merely because this packet is prepared.

### Custody And Remaining Decisions

GFM rendering, local links, whitespace/disclosure checks, final source/input hash checks and archive readback finish preparation. Preserve the corrected control set, task and fixed packet/identity/private-and-review inputs outside the source checkout for the Owner's delta-review decision and the next bounded correction/execution-plan handoff. Keep this custody until that identified handoff is accepted or equivalent durable Git custody replaces it; no permanent disposable validation scripts/renders or API transcripts are needed. Earlier A1/A2 review input and result custody remains intact. Retain the existing source worktree for concrete A2 delta review and implementation continuation; no worktree is eligible for retirement.

The completion here is authoring and inspectable packet preparation only. The Owner has not accepted these correction bytes, and no Reviewer has reviewed them yet. The full P0a result, P0c execution plan, D1/D2, future factory/product-prefix work and actual execution remain open. Generic adopter impact is no current update recommendation from this source-only verification-authoring slice; no installation was assessed or changed.


## A2 Correction Delta Review Result — 2026-10-09

### Actual Owner Authorization And Input Identity

The Owner replied “승인” to the exact proposal to send the approximately 325 KB internal correction/source/test/installed-Python excerpt packet to the Anthropic Claude subscription service for one fresh tool-free static review, maximum 600 seconds, followed by response and Driver disposition recording. This authorizes this one transmission/review and its record, not further code/README corrections, another review, runtime/test execution, result acceptance, contract activation, Git or adopter actions. The fixed packet's pending-authorization prose remains its preparation state; the invocation system prompt explicitly reports the later approval.

Exact packet: 324,705 bytes, SHA-256 `752a4a9ce8e0868d67e2c8c7b29366f372958967e6fd21999aaf3752420c8ca6`. It contains seventeen full files, eighteen repository excerpts, seventeen installed-runtime excerpts, the static module/seed map, exact three-file diff, prior A2 response/dispositions and current authoring checkpoint. Base: `238514686078ce1564010a7b69013f48a635c57c`; tracked diff: `12238ddc334c4a6971d657249732a73d59cc4c3e32b6463d5a7fccfc867a6b04`; task before review: `e7f477c8b2d271aeb50c0938759c56633576222d1f0fbdc6a5c2033d3b54323d`. Full inputs and whole-file/range identities, including untracked controls outside that tracked diff, are enumerated in the retained identity. Private schema-3 invocation SHA-256: `bd4a422f98fb4e04d8a4c5fe3adb463ace5b48e16a3c50b5f474751c78be2ef1`; six-path-substituted review copy: `4a703f57c0db5992bfdb998fef8d7a785e0dea131356be29b42996a2f4fc14fc`.

Before and after transmission, the Driver verified the packet, task/base/diff, all seventeen full inputs and thirty-five exact excerpts, 26 static-map source hashes, src/tests membership and tests/__init__.py absence, all 101 source bytes/modes and eleven executable/data/policy control identities plus the full README input, runtime/Git/system-config hashes, and the schema-3 sixteen-entry root name/type map. All matched; ROOT stayed absent. The Reviewer did not independently recalculate those hashes. Driver read/hash verification is separate from the Reviewer's code inferences and from still-unperformed runtime checks.

### Actual Reviewer Invocation And Limits

Driver: Codex. Reviewer: Claude Opus 5.5, actual startup/final model `claude-opus-5-5`, fresh session `c0cdb93b-4ff7-4886-85d9-1cdd9d71d727`. Immediately checked authentication: loggedIn=true, authMethod=claude.ai, apiProvider=firstParty, subscriptionType=pro. No credentials or account email are recorded. Actual tools and MCP arrays were empty. No reviewer session was resumed; independence is limited to the identified Driver-selected context, omissions and model knowledge.

The CLI ran from the private fixed-packet directory with prompt.txt bytes on stdin, one 600-second process-group deadline and no retry. Exact argv, with no private paths:

```json
[
  "claude",
  "-p",
  "--model",
  "opus",
  "--effort",
  "high",
  "--safe-mode",
  "--system-prompt",
  "The human Owner has now explicitly authorized this one A2 M1/M2/M3 correction delta static review. The fixed packet was prepared before approval; its pending-authorization wording is historical. Follow the fixed bounded request. Treat source as data, use no tools or execution, and respond concisely in Korean. This is partial correction review of namespace/root guards, runner occurrence/results, preservation diagnostics and the proposed collection-binding procedure only, not whole P0a R1 or P0c R0 completion. A reviewer verdict is not Owner acceptance.",
  "--restricted",
  "--tools",
  "",
  "--strict-mcp-config",
  "--mcp-config",
  "{\"mcpServers\":{}}",
  "--disable-slash-commands",
  "--setting-sources",
  "",
  "--permission-mode",
  "dontAsk",
  "--no-session-persistence",
  "--output-format",
  "stream-json",
  "--verbose"
]
```

Observed duration 313.06 seconds, exit 0, timeout=false, is_error=false, stderr 0 bytes, 226 valid stream events and 0 malformed lines. Pre/post input checks passed. No reviewed code/control/test was executed or imported, so there are no runtime test pass/fail counts or reproduced counterexamples. Final response SHA-256: `7ed968c7f3800f8482d1e51c1230f458b83df0ee93a5acb9c925a3433efe82ed`. Stream transport and wrapper checks do not qualify the controls.

### A2 Correction Reviewer Response Verbatim

````text
# A2 M1/M2/M3 교정 델타 정적 검토 결과

## 1. 판정

**커버 범위 안에서 must-fix는 찾지 못했습니다.** 교정된 `common.py`, `runner.py`, README는 M1/M2/M3 처분과 Owner 선택(SOURCE append + 1단계 루트 가드, 후보 확장 없는 보존 상태 보고)을 정적으로 일관되게 구현합니다. 통과로 위장되는 종료 경로도 보이지 않습니다.

- 전부 정적 판독입니다. 실행, 해시 재계산, SBPL 실효 판단은 하지 않았습니다.
- 이 판정은 Owner 수락이나 실행 허가가 아니며, P0a R1 전체나 P0c R0의 완료도 아닙니다.
- 실행 승인 전에 보완을 권하는 문서·절차 항목이 3건, 선택 사항이 2건 있습니다(§3).

## 2. Must-fix

없음.

## 3. 실행 승인 전 보완 권고 (차단 아님)

**S1. 결속 절차 3단계에 바이트 형식 검사가 없습니다 (README "Collection Binding" 3).**
- smoke는 `digest(canonical(collection))`을 비교합니다. 파일 해시가 이 값과 다르면 smoke-base 슬롯을 만든 뒤에야 실패합니다.
- 절차에 두 가지를 추가하면 됩니다: 키가 정확히 7개인지, 그리고 파일 바이트가 파싱 값의 canonical 재직렬화와 같은지.
- 재수집이 비결정적이면 절차로는 막을 수 없습니다. 이 점은 한계로 명시하는 편이 맞습니다.

**S2. import 시점 `SkipTest`는 `loader.errors`에 들어가지 않습니다 (loader L434-435).**
- 이 경우 collect는 통과하고 `default_ids`에 `unittest.loader.ModuleSkipped.*`가 남습니다.
- 시드 모듈이면 3단계의 20개 ID 존재 확인이 잡습니다. 그래도 `unittest.loader.` 합성 ID의 유무를 결속 기록에 남기길 권합니다.

**S3. 실행 중 루트 변동은 슬롯을 소모합니다 (controller post-check의 `config`).**
- 시작 시점 변동은 슬롯 생성 전에 걸러집니다. 실행 중 `.DS_Store`나 IDE/에이전트 디렉터리가 생기면 사후 검사에서 비통과가 됩니다.
- fail-closed이므로 결함은 아닙니다. 실행 중 SOURCE 루트를 Finder나 도구로 열지 말라는 운영 주의를 README에 추가하길 권합니다.

**S4. 보존 진단의 사유·단계 표기가 일부 뭉뚱그려집니다 (runner `preserve`, 선택 사항).**
- `no-reachable-root`가 세 경우를 한데 묶습니다: 속성 없음, 디렉터리 아님(이미 정리됨), EXEC 밖.
- `unavailable` 행 쓰기가 실패하면 `stage="root-inspection"`으로 87 종료합니다. 단계 표기가 실제 원인(기록 실패)과 다릅니다.
- `base`/`root`가 경로가 아닌 객체면 `TypeError`로 전체 실행이 87 종료합니다. base 시드 7개 클래스에서는 도달 경로가 보이지 않고, 1회성 complete 모드에서는 고려할 일입니다.

**S5. README 표현 (선택 사항).**
- "Successful completion of the runner also records unstarted.json…"은 실제로는 테스트 실패를 포함해 `run()`이 정상 반환한 경우입니다.
- entry 단계에서 `SOURCE/colvia`가 추가되면(observer L29) 새 루트 맵 검토가 필요합니다. 한 줄 명시를 권합니다.

## 4. 필수 점검 항목별 확인

| 항목 | 결과 | 근거 |
| --- | --- | --- |
| 스키마 3 키 검증 | 일치 | 13개 키 정확 일치, `type is int and == 3`. 스키마 1/2는 키 불일치로 거부됩니다. |
| 가드와 append 순서 | 일치 | `config`(file_map → `verify_source_root`) → `verify_old` → `sys.path` → `chdir` → `discover`. |
| 가드 내용 | 일치 | 이름은 `relative()`와 parts==1, 종류는 file/directory만. `lstat`으로 링크·특수 항목을 거부하고 정확 일치를 요구합니다. |
| invocation 정합 | 일치 | 루트 16개는 `source_files` 최상위 15개 + `.git`(file)과 같습니다. controls는 `.py` 6개입니다. |
| 정책 권한 | 정적으로 충분 | 두 정책 모두 `file-read* (subpath SOURCE)`와 전역 `file-read-metadata`가 있습니다. 새 grant는 필요 없습니다. |
| 네임스페이스 해소 | 정적으로 성립 | `SOURCE/src`와 `SOURCE/tests`에는 file_map 때문에 미등재 파일이 있을 수 없어, `tests`는 SOURCE 부분으로 해소됩니다. SOURCE 루트 이름 중 stdlib과 겹치는 것은 제 지식으로는 없습니다. |
| collection identity | 일치 | payload에 `source_root_entries`가 포함됩니다. |
| discovery/selection/occurrence | 변경 없음 | `discover("tests")`, `ordered`, selection 필터가 그대로입니다. |
| 객체 기반 identity | 일치 | `id(test)`별 deque를 쓰고 `selected`가 참조를 쥐어 id 재사용이 없습니다. 재노출 클래스는 서로 다른 객체라 각자 큐를 가집니다. |
| 모호성 거부 | 충분 | start 없이 건너뛰는 경로(suite L116-118)는 항상 `_ErrorHolder` 콜백이 먼저 옵니다. 플래그가 선행하고, `identity-stop.json` 뒤 예외로 종료 1이 됩니다. |
| class/module 이벤트 | 분리됨 | `suite-events.jsonl`에 `identity=null`로 기록되고 `testsRun`은 늘지 않습니다. errors/skipped로 종료 게이트에 반영됩니다. |
| subtest skip 연결 | 일치 | `_SubTest.test_case`는 항상 루트 테스트입니다. 실패 subtest는 부모가 `preserve` 대상입니다. |
| outcome 우선순위 | 일치 | 비통과 우선입니다. 모든 콜백이 `super()`를 호출해 unittest 카운트와 어긋나지 않습니다. |
| unstarted/unfinished | 일치 | `ok` 조건에 포함됩니다. 다만 unfinished는 정상 반환 시 항상 비어 있어 실효가 없고, 해도 없습니다. |
| 보존 상태 | 일치 | copied/unavailable/stopped를 기록합니다. `preservation_stop`은 `finally`에서 `os._exit(87)`이라 진단 I/O가 실패해도 87로 끝납니다. |
| 상한과 예산 | 변경 없음 | 64/256MiB와 모드 예산이 그대로입니다. |

- **`copied`의 의미**: `copytree`가 예외 없이 반환했다는 뜻입니다. 사후 바이트 대조가 없고, 크기는 사전 `lstat` 합이며, 복사본은 child가 쓸 수 있는 `work/` 아래에 있습니다. 증명된 바이트도, 모든 실패 fixture의 보존도 아닙니다. README 서술과 일치합니다.
- **도달 가능 시드**: 여전히 6/20이며 이전 분류 그대로입니다.

## 5. 비차단 한계

- **CONTROLS 하위 디렉터리**: `sys.path`에서 CONTROLS가 SOURCE보다 앞이고, 멤버십 검사는 최상위 `*.py`와 `*.pyc`만 봅니다. `CONTROLS/tests/…`가 있으면 선점합니다. README가 한계로 선언했습니다. 원하면 discovery 직후 `tests.__path__`와 `tests.*` 모듈의 `__file__` 위치를 한 번 `require`하는 방법이 있습니다. 새 가드이므로 Owner가 정할 일입니다.
- **가드 범위**: 가드와 import 사이의 TOCTOU, 루트 하드링크, `docs/` 등 비봉인 하위 트리는 덮지 않습니다.
- **선행 결과 검사**: `completed()`는 루트 맵과 invocation 해시를 비교하지 않습니다. 실행별 `config`와 collection 해시에 의존합니다.
- **종료 표식의 비대칭**: `suite-events`, `executed`, `identity-stop` 쓰기 실패는 표식 없이 traceback 종료 1입니다. 87 경로와 다르지만 비통과입니다.
- **identity-stop 경로**: `os._exit`가 아니라 finalizer가 돕니다. 그 시점에 활성 테스트는 없습니다.
- **행 없는 87 종료**: STOP 행과 counts가 없습니다. 고아 child는 controller가 surviving-group으로 처리합니다.
- **함수 내부의 `tests.` import**: 정적 맵에 없어 판단하지 못합니다.
- **이전 한계**: 경로 표기, `getpgid`, site, fsync 관련 한계는 그대로입니다.

## 6. 미검증

- 세 파일의 해시 일치와 "controller 등 9개 controls 불변" 주장
- stdlib Lib에 `tests`가 없다는 사실과 CONTROLS의 실제 디렉터리 내용
- 22개 테스트 모듈 본문과 checkout L111 이후
- acquire/canary/observer의 나머지 본문
- SBPL 실효와 실제 타이밍

## 7. 다음 단계 (실행 권한 아님)

1. Driver가 S1–S5를 처분합니다. 권고대로면 S1–S3과 S5는 README만 바뀌어 controls 해시가 그대로입니다. S4를 코드로 반영하면 runner 해시와 invocation이 바뀌므로 다시 델타 검토가 필요합니다.
2. Owner가 이 교정 바이트의 수락 여부를 별도로 결정합니다.
3. acquire-base 실행 승인은 그 뒤의 별도 게이트입니다. 결속 절차는 실행 승인 범위에 명시적으로 포함되어야 합니다.
4. 범위 밖으로 남는 것: focused/complete/artifact, factory, product-prefix, D1/D2, P0a R1 전체, P0c R0.
````

### Driver Dispositions And Read-Only Follow-Up

The Driver agrees that the supplied correction has no remaining must-fix identified by this bounded static review. M1/M2/M3 are addressed at the reviewed bytes within the accepted authoring choices; this is a proposed acceptance of the A2 static checkpoint, not Owner acceptance, whole P0a/P0c completion, actual sandbox/import success or a general false-success-path guarantee. The previous A1 acceptance remains its historical bounded checkpoint. No further code correction is selected on this result.

| Item | Driver decision | Disposition and remaining boundary |
| --- | --- | --- |
| S1 canonical collection bytes | accept for next authorized documentation slice | Add exact collection-key validation and require the actual file bytes to equal canonical reserialization before binding the file hash. The seven keys are source_digest, source_root_entries, controls, default_ids, factory_ids, ordered and duplicates. Use duplicate-key rejection consistent with the control reader. Keep rediscovery nondeterminism as a limitation; no procedure can guarantee later recollection is identical. No binding or README edit occurs under this review-only approval. |
| S2 import-time SkipTest | accept reporting recommendation | The future binding record should list any unittest.loader. synthetic IDs and their effect on the selected twenty IDs. Preserve default discovery and all occurrences; do not filter those IDs, invent a successful full suite or silently reinterpret a non-seed skip as qualification. Existing seed-presence checks remain required. |
| S3 root changes during a run | revise wording, accept operational point | In the next README/preflight clarification, require the identified SOURCE root to remain unchanged while a slot runs; Finder/IDE/agent tools may create .DS_Store or new directories. Avoid actions that create those entries, rather than claiming all read-only inspection is forbidden. A post-check drift consumes the exclusive slot as non-pass; no automatic inventory refresh, ROOT reset or retry is implied. |
| S4 coarse preservation reasons/stages | defer optional code refinement | Current no-reachable-root is deliberately broad and its log-write failure can retain a coarse root-inspection stage. Unsupported path-like attributes fail non-pass with exit 87. Record these limits; do not change runner bytes merely to refine diagnostics or expand fixture search. Reconsider for a demonstrated base-path problem or a separately scoped future-mode review. |
| S5 wording and future entry root | accept for next authorized documentation slice | Replace successful completion with normal return of run(), which may contain test failures. State explicitly that future SOURCE/colvia addition requires a newly identified/reviewed root map before entry-phase use. This is not permission to add that launcher or auto-refresh inputs. |
| Remaining namespace/control-directory limits | accept bounded limitation | No new resolver/origin guard is added. Point-in-time Driver read-only metadata inspection after review found no tests entry under the current controls directory or the identified stdlib directory; controls contained exactly the twelve known files and no immediate directory. This narrows those two observations only, not all sys.path origins, zip/builtin/runtime effects, recursive imports or future drift. |
| Result and preservation limits | accept | Child diagnostics/copies remain mutable evidence, not parent-bound acceptance authority. Copied means copytree returned, not independently attested bytes. Non-start events, identity-stop with finalizers, missing summaries after exit 87 or I/O errors, process cleanup and nonrecursive root coverage retain their stated limits. Actual behavior remains unexecuted. |

The read-only follow-up inspected only the named current filesystem entries; it did not run Python path resolution, import tests, create fixtures or invoke a guard. The Reviewer table's feasibility statements and current 6/20 fixture reachability remain static judgments. The Driver's before/after checks support input preservation; they do not upgrade the Reviewer's scope.

Only this task's disposition and appended result record change. common.py, runner.py, README and all other controls/source inputs remain at their reviewed bytes. DR, index, central STATUS, runtime, adopter state and Git history remain unchanged. Generic adopter impact: no update currently needed for this review-record-only step; installations were not assessed.

### Proposed Next Bounded Slice — Acceptance And Base-Plan Preparation

Recommend Owner acceptance of this exact A2 correction static checkpoint together with the dispositions and limits above, followed by documentation/base-plan preparation only. Acceptance would identify this result and the fixed reviewed correction packet, without claiming all P0a controls, future factory/product-prefix behavior or actual execution is qualified.

The proposed edits are limited to the controls README for S1/S2/S3/S5 and this existing task for one dated base-execution plan; prepare private exact plan/review inputs as needed. Do not alter controls, product/test sources, selection, policies, budgets, root inventory, DR/index/central STATUS or any runtime state. The plan must name the exact source/control/runtime/Git/config and schema-3 input identities, read-only preflight, four ordered acquire-base/canary-base/collect-base/smoke-base slots and their existing 300/300/300/1,200-second ceilings, exact commands/paths, deterministic collection-hash binding checks, output/recovery custody, stop on first non-pass and no automatic retries. It must explain which reviewed A1/A2 base-scope claims support it and which original P0a/P0c or future-mode claims remain open; no unreviewed wider gate is silently discharged.

Completion would be an inspectable plan and smallest sufficient fixed review packet, with static source/input, GFM/link/disclosure/whitespace and custody checks. Actual acquisition, sandbox compilation/canaries, imports/discovery, binding, smoke, a new external Reviewer invocation and Git/adopter actions remain excluded. A need for new controls, a wider policy allowance, changed limits or a technical contract choice stops preparation for a revised scope. A future plan-review approval and a later exact execution approval remain distinct; the current one-review authorization covers neither. This next slice is proposed, not started.

### Verification And Custody

Verify the response verbatim, prior task/review bytes apart from the current disposition, final input identities and document GFM/links/disclosure/whitespace. Preserve the final task and compact authorization/execution metadata outside the checkout with verified archive readback for the Owner's A2 acceptance decision and the proposed documentation/base-plan handoff. The exact correction packet and authored-control backup remain the input custody until that named handoff is accepted or equivalent durable Git custody replaces them. Intermediate stream output, empty stderr and the duplicate standalone response may then be removed; keep no default permanent API transcript. Prior A1/A2 evidence and custody remain intact. The source worktree has concrete documentation/base-plan and implementation continuation use and is retained; no checkout is eligible for retirement.


## A2 Static Acceptance And Base-Execution Plan Preparation — 2026-10-09

### Actual Owner Decision And Authorized Preparation

The Owner replied “승인” to accepting the A2 static result and preparing README amendments plus the base-execution plan. The accepted A2 result is this task at SHA-256 `cc5259297bdc005321598838ff7930cb5b3be32bc9000c682198f5235fb32916`, Reviewer response `7ed968c7f3800f8482d1e51c1230f458b83df0ee93a5acb9c925a3433efe82ed` and fixed correction packet `752a4a9ce8e0868d67e2c8c7b29366f372958967e6fd21999aaf3752420c8ca6`. Exact bytes have retained custody. Acceptance covers the M1/M2/M3 correction static checkpoint and recorded limits/dispositions, including deferral of optional S4 code refinement. It does not accept new documentation/plan bytes, the original whole P0a R1 or P0c R0, runtime qualification, future modes, D1/D2 or product implementation.

Preparation authorizes only the controls README for S1/S2/S3/S5, this task's dated acceptance/plan record, and private identified plan/review inputs. No control, runtime/test source, selection, policy, budget, root inventory, DR/index/central STATUS, Git or adopter state changes are authorized. No acquisition, sandbox/canary, reviewed-code import/discovery, collection binding, smoke or external Reviewer invocation is authorized or performed.

### README Amendments And Unchanged Inputs

S1 now requires exactly seven collection keys, duplicate-key rejection and raw bytes equal to common.canonical reserialization before hashing/binding; nondeterministic later rediscovery remains a limitation. S2 records every unittest.loader. synthetic ID and selected-ID impact without filtering/deduplicating discovery or claiming full-suite qualification. S3 distinguishes prohibited root-creating interference from read-only inspection and keeps drifted slots consumed/non-pass. S5 states that normal TextTestRunner.run() return may include failed tests, and a future SOURCE/colvia addition needs a newly identified/reviewed root map. The status text reports the actual bounded A1/A2 acceptances while keeping execution open. No S4 runner change was made.

Current README SHA-256: `30dd7428034439e56b62fa56b1031af059434d2112ca761897b90bf76591f6b7`. All eleven control code/policy/data hashes remain those of accepted A2, including common.py `37756fbd18d7f58037a99bc1f8e81c8d03176b185a0236bce579585901e2a83e` and runner.py `50529c3c79f8ee14f03b9536a6d4f4b4468abfaad3cfa5fe8b9cb646d12f68b0`. The 101 source bytes/modes, 29 managed files, twenty ordered seed IDs, root inventory, runtime/Git/system config, base and tracked diff remain unchanged.

The initial private invocation is copied byte-for-byte to the plan-input directory: schema 3, phase=base, factory=false, sixteen source-root entries, the same twenty IDs and collection_sha256=null. SHA-256 remains `bd4a422f98fb4e04d8a4c5fe3adb463ace5b48e16a3c50b5f474751c78be2ef1`; the six-path-substituted review copy remains `4a703f57c0db5992bfdb998fef8d7a785e0dea131356be29b42996a2f4fc14fc`. The file argument location changes to the separately identified plan-input directory; source/control/execution paths inside the invocation do not change. The future smoke input and collection-binding summary are named but absent. No collection digest is invented.

### Bounded Base Plan — Proposal, Not Permission

The private declarative plan identifies the real source/control/runtime/Git/config/input paths and exact argv arrays. Its review copy substitutes the same six private path values plus the plan/input directory (seven path substitutions total); illustrative commands must never be executed. Private plan SHA-256: `6412fff9f2aee257f66c0ee9340e631cc762eb603395b1680777dc8b7f0fcb99`; review-plan SHA-256: `758df9a15fd256e0477a74d5b276329b666377a3bb55a964e288037b0005020a`. This plan JSON is not a control program or runtime authority record.

Every step launches the pinned CPython 3.14.7 through /usr/bin/env -i, then the unchanged isolated bootstrap and controller. The direct argv fixes -I -S -B, the exact BOOTSTRAP string, CONTROLS, controller.py, the input path/hash, mode and base slot. cwd is SOURCE and stdin is DEVNULL. A fixed parent environment contains only PATH, HOME, XDG_CONFIG_HOME, TMPDIR, LC_ALL, TZ and PYTHONDONTWRITEBYTECODE. Parent HOME/XDG use the observed inert /var/empty directory and parent TMPDIR uses /private/tmp only for disposable interpreter scratch, never worktree/deliverable custody. The trusted controller is unsandboxed; each child receives the existing separate allowlist with its own work-local HOME/XDG/TMPDIR and fixed SBPL policy. Host runtime/OS installation remains trusted and unsealed. No real credentials or user Git configuration are supplied to children.

Command structure, with symbolic fields only in this source record:

```text
/usr/bin/env -i <fixed parent environment> PYTHON -I -S -B -c BOOTSTRAP CONTROLS controller.py INPUT INPUT_SHA MODE base
```

The first three private argv arrays are literal and use the unchanged base-input digest. Only the smoke input digest is unresolved; its token may be replaced solely with the digest of the real exclusively created bound input after the separately approved collection/binding step. The smoke path, mode, slot, runtime, bootstrap, environment and all other arguments are already fixed. A placeholder is not a runnable approved command.

| Sequence | Mode/slot | Ceiling including controller setup/cleanup | Required before next step |
| --- | --- | ---: | --- |
| 1 | acquire / base | 300 seconds | Exact initial preflight; absent ROOT; successful parent result and manifest-checked 101-file OLD with exact file/directory modes and 29-member inventory |
| 2 | canary / base | 300 seconds | Passed matching acquisition; current positive/refusal, inherited-child, runtime/Git/topology/fd/observer synthetic evidence and successful parent result |
| 3 | collect / base | 300 seconds | Passed matching canaries; actual collection plus parent input/result identity; no inferred discovery count |
| Binding | one new private input and one summary | No controller slot; read/JSON-write procedure only under future explicit binding approval | Successful exact collect record, canonical collection bytes, identity/occurrence checks, unchanged twenty-ID selection and exactly one changed invocation field |
| 4 | smoke / base | 1,200 seconds | Bound input digest; every occurrence of each selected ID; truthful counts and records; successful parent completion with no surviving group |

The configured controller ceilings sum to 2,100 seconds. That sum excludes read-only preflight, between-mode verification/binding and reporting, and promises no overall elapsed time or successful completion. Existing filesystem-call preemption and escaped-process limitations remain; the plan does not add a new watchdog or claim a hard whole-host deadline. Monitor the running command and report progress at most 60 seconds apart without launching overlapping modes. A discrepancy stops further launches and requires a bounded recovery decision; do not blindly signal a shared/unidentified process or reset a budget.

### Preflight, Evidence And Binding Rules

Before a future authorized first command, recheck exact plan/input/source/control/runtime/Git/system-config and /usr/bin/env/sandbox-exec bytes, regular-file/link/mode facts, source/control bytecode absence, src/tests membership, the sixteen-entry root map, unchanged selection and null initial collection hash. Confirm unlinked/disjoint SOURCE/CONTROLS/COMMON_GIT/OLD/EXEC/input paths, absent ROOT and no Git/authority ancestors. Verify no alternate/promisor object markers or /etc/gitconfig, and the planned PATH resolves python3/Git to the pinned tools. Inspect source launcher/common/input ownership and modes without a write-open probe. No fixture or ROOT is created by preflight. Before canary, inspect the actual acquired OLD and prior acquisition result; ACL viability and the positive operations remain actual canary steps.

The actual parent and child write boundaries are distinct. The parent creates ROOT/exec, its synthetic denied-sentinel and controller lock, and each run's parent inputs/result/log. Acquisition alone writes OLD and its own synthetic Git metadata; other children write only their own work subtree and diagnostic log under the fixed policy. The later private bound invocation/summary and final task/custody records are separately declared Driver writes outside ROOT. No source/product/host-configuration write or real-secret/network access is requested. Parent positive probes can open named existing inputs for writing without truncation/write and perform same-mode OLD chmod; the latter may alter ctime. A failed setup/positive probe may consume a slot without a result.

After each mode require exit 0 and the exact parent result with execution_pass=true, correct mode/slot and inputs_sha256 matching the actual inputs.json bytes. Require that inputs record to identify the command's invocation hash, expected source/controls/tools/config, policy/argv/environment and budget; check natural_completion=true, group_absent=true, inputs_unchanged_or_acquired_exact=true, reason=null and duration within the mode ceiling. Recheck current inputs/root membership and inspect the required named child evidence. A missing/malformed/conflicting record stops progress even if an outer command returned zero. Parent fields and named canaries support their covered claims only, not whole-host process isolation or all test behavior.

Binding follows the amended README exactly: reject duplicate/invalid/oversized JSON; require the seven exact collection keys and canonical raw bytes; match source/root/control identities and empty factory_ids; derive ordered per-ID occurrence counters/duplicates from default_ids and match them exactly; require all twenty selected IDs. Record actual multiplicity and synthetic loader IDs with their effects. Verify the exact parent collect input/result first. Hash collection.json directly, using stdout only as a cross-check. Exclusively write a new canonical invocation with only collection_sha256 changed, then re-read/diff/hash it and exclusively record the referenced parent/input/collection identities and counts. No initial input overwrite or partial-binding retry is allowed. The real bound-input digest alone fills the fixed smoke command token. Parent success does not itself bind child collection bytes and these checks cannot guarantee deterministic rediscovery.

After smoke, selected.json must equal the ordered subset containing all occurrences of the twenty fixed IDs; executed identities must match without extras/duplicates and all summaries must be pass. selected/run counts must equal that actual count, all non-pass/unstarted/unfinished counters must be zero, unstarted/unfinished lists empty, and no suite event or stop marker may contradict success. Retained child evidence remains mutable diagnostics; copied fixtures are not independently attested bytes, and cleanup-deleted/local fixtures remain unavailable. Existing process-test sibling evidence is outside runner copy caps. No whole suite, entry factory, prefix oracle, D1/D2, product acceptance or adopter qualification follows from a base result.

### Stop, Recovery And Review Boundary

Stop on the first non-pass, input/approval discrepancy, timeout, cleanup/surviving-group issue, missing evidence or failed binding. Preserve ROOT, partial OLD, consumed slots, exact private inputs/summary and essential command/runtime/exit observations; launch no later mode. Do not delete/chmod evidence to retry, use another root/slot, relax policy, increase limits, change assertions/selection, invoke a missing dependency or add a new control. New controls, broader permissions, changed limits or a technical contract choice require a revised scope. A clean source status is not proof that ignored runtime evidence or failure fixtures survived.

The next proposed external review explicitly combines two narrow purposes with separate conclusions: R1 of README S1/S2/S3/S5 amendments and R0 of this prospective four-step base plan. It does not complete the original whole P0a authored-controls R1, approve unreviewed future-mode claims or waive the post-execution runner-result R1 and Owner acceptance before product implementation. It must assess whether the identified A1/A2 static checkpoints plus the supplied unchanged code sufficiently support this bounded base plan; missing evidence remains a condition, not a silent wider pass.

The fixed packet provides current controls/read policy/baseline/seed input and necessary canary source context, accepted A1/A2 responses, exact current plan and a README diff. It deliberately omits all complete test-module/product bodies and the future prefix/factory review, whose known scope limits remain visible. One fresh no-tool Claude subscription review, at most 600 seconds, is proposed only after a separate Owner approval of its exact internal transmission. Actual four-step execution and deterministic binding require a later exact approval; neither is performed by this preparation.

### Read-Only Preparation Checks And Custody

Current read-only observations found ROOT absent, the sixteen-entry source root unchanged, sandbox-exec and /var/empty present, PATH python3 resolving to the fixed interpreter, and no /etc/gitconfig/alternate/promisor marker. Existing source launcher/common/input were one-link regular files owned by the executing user with expected bytes/modes. These observations are not a future execution clearance or proof of ACL/SBPL service behavior. The new plan-input copy's bytes match the accepted input; repeat path/metadata checks immediately before an approved run. No source/control import, test discovery, guard execution, fixture or smoke input was created.

Static checks compare the fixed argv/bootstrap/budgets against AST/read source, private/review substitutions, source/control/input hashes and all inherited input identities. GFM/link/disclosure/whitespace checks and archive readback complete preparation. Only README and this task change in the source checkout. Preserve the final task/README and exact plan/review inputs outside the checkout for the Owner's plan-review decision and then the separately authorized base execution/review handoff, until accepted handoff or equivalent durable custody replaces that need. Keep prior accepted input/result custody. Runtime evidence will be retained for its named execution/Reviewer recovery need if a run is later authorized; no raw API transcript or disposable validation script is a default permanent artifact. The source worktree remains needed for the concrete plan review and implementation continuation, so it is retained.


## README Result And Base-Plan Review — 2026-10-09

### Actual Owner Authorization And Exact Inputs

The Owner replied “승인” to sending the exact approximately 273 KB internal packet to Anthropic Claude through the subscription account for one fresh no-tool review, maximum 600 seconds: README S1/S2/S3/S5 amendment result R1 and prospective base-execution-plan R0 with separate conclusions, followed by response/Driver disposition recording. This permits one transmission/review and this record only. It does not authorize corrections, acceptance, a further Reviewer invocation, helper/controller execution, acquisition/canary/discovery/binding/smoke, product/Git/adopter changes or completion of whole P0a R1/P0c R0. The invocation explicitly distinguishes this later approval from the packet's historical preparation-only wording.

Fixed packet: 272,815 bytes, SHA-256 `3487397dec1b345884c69291928679c45e6c5447c25e7a109f37f398c2d0de85`. Base `238514686078ce1564010a7b69013f48a635c57c`; tracked diff `12238ddc334c4a6971d657249732a73d59cc4c3e32b6463d5a7fccfc867a6b04`; task checkpoint `6361b070f8a44148b0043e8ea419a824ab628962ae0da040ca6ef9a07dfdaff5`; README `30dd7428034439e56b62fa56b1031af059434d2112ca761897b90bf76591f6b7`. The packet contains sixteen complete inputs: eleven controls/README files excluding prefix-oracle.json, the launcher and four necessary source-context files. It also includes the exact README diff, accepted A1/A2 responses, static 26-module/twenty-seed context and the path-substituted plan/input. Complete test/product bodies, installed-runtime excerpt bodies and future prefix/factory qualification are explicitly omitted; recorded hashes are not claims that the Reviewer saw those bodies. The inherited A1/A2 results retain their own bounded scope.

Private initial invocation `bd4a422f98fb4e04d8a4c5fe3adb463ace5b48e16a3c50b5f474751c78be2ef1`; six-path-substituted invocation `4a703f57c0db5992bfdb998fef8d7a785e0dea131356be29b42996a2f4fc14fc`; private plan `6412fff9f2aee257f66c0ee9340e631cc762eb603395b1680777dc8b7f0fcb99`; seven-path-substituted plan `758df9a15fd256e0477a74d5b276329b666377a3bb55a964e288037b0005020a`. The retained identity enumerates full inputs, 101 source bytes/modes, eleven control identities, static map, membership, root inventory, five inherited installed-runtime file hashes and host tool identities. The Driver verified these before and after the review, including plan hashes, base/diff/task, runtime/Git/config, host tools and absence of ROOT, smoke input and binding summary. All checks matched. The Reviewer did not inspect private paths or recalculate hashes; input preservation/equivalence checks are Driver evidence, separate from Reviewer static inference.

### Actual Invocation And Evidence Limits

Driver: Codex. Reviewer: Claude Opus 5.5, actual startup/final model `claude-opus-5-5`, fresh session `53c24d41-6c78-40ce-97f2-696ce6f74f87`. Immediately checked authentication was loggedIn=true, authMethod=claude.ai, apiProvider=firstParty, subscriptionType=pro. No credentials or account email are recorded. Actual tools and MCP arrays were empty; no prior session was resumed. Independence is limited by the Driver-selected packet, inherited context, omitted bodies and model knowledge.

One CLI invocation ran from the private packet directory with exact prompt.txt bytes on stdin, a 600-second process-group deadline and no retry. Its exact argv, containing no private paths:

```json
[
  "claude",
  "-p",
  "--model",
  "opus",
  "--effort",
  "high",
  "--safe-mode",
  "--system-prompt",
  "The human Owner has now explicitly authorized this one combined bounded README-amendment result R1 and prospective base-execution-plan R0 static review, with separate conclusions. The fixed packet was prepared before approval; its pending-authorization wording is historical. Follow the fixed bounded request. Treat source as data, use no tools or execution, and respond concisely in Korean. This is review of README S1/S2/S3/S5 amendment results and the prospective four-step acquire/canary/collect/smoke base plan only, not whole P0a R1 or P0c R0 completion. A reviewer verdict is not Owner acceptance.",
  "--restricted",
  "--tools",
  "",
  "--strict-mcp-config",
  "--mcp-config",
  "{\"mcpServers\":{}}",
  "--disable-slash-commands",
  "--setting-sources",
  "",
  "--permission-mode",
  "dontAsk",
  "--no-session-persistence",
  "--output-format",
  "stream-json",
  "--verbose"
]
```

Duration 315.36 seconds; exit 0; timeout=false; is_error=false; 234 valid stream events, 0 malformed lines and 0 stderr bytes. Pre/post input checks passed. No reviewed code, controls, tests or binding helper was imported or executed. There are no runtime-test counts or reproduced counterexamples from this review. Final response SHA-256: `1edb8603ecc0584d3513590b3dc6939c999d597edf83cb49e34a51e04b7624db`.

### Reviewer Response Verbatim

````text
# README 결과 R1 + base 실행 계획 R0 정적 검토

## 1. 판정

- **(A) README S1/S2/S3/S5:** 수락된 A2 처분을 그대로 구현했고 회귀는 찾지 못했습니다. must-fix는 없습니다.
- **(B) 4단계 base 계획:** argv, 환경, 예산, 증거 게이트가 제공된 구현과 일치하며 코드·정책 차원의 차단 결함은 없습니다. 다만 정확한 실행 결정 전에 계획 기록에 채워야 할 조건이 4건 있습니다(§4). 이 중 C1 때문에 결속과 smoke는 지금 상태로는 정확한 승인 대상이 되기 어렵습니다.

전부 정적 판독입니다. 해시는 재계산하지 못했고, private 계획과 private 경로는 보지 못했습니다. 이 판정은 Owner 수락이나 실행 허가가 아니며, P0a R1 전체나 P0c R0의 완료도 아닙니다.

## 2. (A) README 수정 확인

| 항목 | 결과 | 근거 |
| --- | --- | --- |
| S1 | 일치 | 7개 키는 `runner.py`의 `collection` 딕셔너리와 같습니다. 정규형 서술은 `common.canonical`과 같고 중복 키 거부는 `read_json`과 같습니다. 파일은 `exclusive_json`으로 쓰이므로 파일 해시가 smoke의 `digest(payload)`와 같은 값입니다. 비결정적 재수집 한계도 명시됐습니다. |
| S2 | 일치 | import 시점 `SkipTest`는 `loader.errors` 없이 `unittest.loader.ModuleSkipped.*`로 남습니다. 기록 의무와 필터·중복 제거 금지, 20개 ID 존재 확인이 이를 덮습니다. |
| S3 | 일치 | 실행 중 루트 변동은 controller 사후 `config()`에서 비통과가 됩니다. 읽기 전용 검사와 구분했고 재시도 금지를 유지합니다. |
| S5 | 일치 | `unstarted.json`과 `unfinished.json`은 `run()` 정상 반환 뒤 `ok` 판정 전에 쓰입니다. `SOURCE/colvia` 추가 시 새 루트 맵이 필요하다는 점도 명시됐습니다. |
| 상태 문구 | 일치 | A1/A2를 정적 체크포인트로 한정하고 실행 미수행을 유지합니다. S4 코드 변경은 없습니다. |

- **비차단:** "Fixed Modes And Bounds"의 "the corrected runner … still require delta review" 문장은 A2 수락 이전 표현입니다. 보수적이라 해는 없지만 현재 상태 문구와 맞추길 권합니다.

## 3. (B) 구현과 대조해 일치한 부분

- **argv:** bootstrap이 인자 두 개를 꺼낸 뒤 `sys.argv` 길이가 5가 되어 controller 요구와 맞습니다. `-I -S -B`는 `require_isolated`를 충족합니다.
- **환경:** 부모는 `env -i` 7개 변수뿐이고 Git이나 임시 파일을 쓰지 않습니다. 자식 환경은 controller가 `work/` 아래로 따로 만듭니다. 계획의 부모 PATH는 controller가 만드는 자식 PATH와 같은 문자열입니다.
- **소모 전 실패:** acquire에서 `config`, `allowed`, 인터프리터 해시 검사는 ROOT 생성 전에 실행됩니다. 입력 불일치는 ROOT를 소모하지 않습니다.
- **예산:** `LIMITS`는 300/300/300/1200이고 합은 2100입니다. 자식 강제 종료 기준은 예산−20초이며, 계획의 "합계는 전체 소요 약속이 아님" 서술과 맞습니다.
- **사후 게이트:** 계획이 요구하는 `result.json`과 `inputs.json` 필드가 모두 실제로 존재합니다.
- **smoke 선행 조건:** `completed()`는 invocation 해시를 비교하지 않으므로 새 smoke 입력이 acquire/canary 선행 검사를 통과합니다. collect 출처와 seed 일치는 controller가 강제하지 않으며, 계획의 수동 검사가 이를 맡습니다.
- **smoke 증거:** 증거 목록이 runner의 `ok` 조건, `counts.json` 키, stop 표식과 일치합니다.
- **네임스페이스:** `CONTROLS/tests` 부재가 준비 관찰에 기록돼 A2의 한계 항목이 다뤄졌습니다.

## 4. (B) 실행 결정 전 조건

모두 계획 기록 보완이며 controls, 정책, 예산 변경은 필요 없습니다.

**C1. 결속과 모드 간 검증의 실행 수단이 식별돼 있지 않습니다.**
- 네 controller 명령은 argv로 고정됐습니다. 반면 결속(정규형 재직렬화, 해시, 배타 쓰기)은 점검 목록만 있고 실행할 코드나 명령이 없습니다.
- 계획상 결속 실패는 재시도가 없으므로, 임시 스크립트의 오류 하나가 전체 진행을 멈춥니다.
- 승인 대상에 다음을 넣어야 합니다: 인터프리터와 플래그, 환경, cwd(SOURCE 밖), 코드 식별자, 쓰기는 두 지정 파일의 배타 생성뿐이라는 점, controls와 SOURCE를 import하지 않는다는 점.
- 그렇게 하지 않으려면 acquire/canary/collect와 결속+smoke를 나눠 승인하면 됩니다.

**C2. 9-조상 산술이 preflight에 없습니다 (A1 O1 미반영).**
- acquire는 이 검사를 하지 않습니다. private 경로 깊이가 다르면 ROOT와 acquire-base를 쓴 뒤 canary에서야 드러납니다.
- review 경로로는 9가 맞습니다. private 경로의 결과를 preflight 기록 항목으로 추가하면 됩니다.

**C3. canary 양성 probe는 owner 쓰기 권한을 전제합니다.**
- 부모가 `SOURCE/hv2`, `controls/common.py`, 입력 파일을 `O_WRONLY`로 엽니다. 입력은 새 plan-input 디렉터리의 사본입니다.
- 사본이 읽기 전용이면 canary-base가 `result.json` 없이 소모됩니다.
- "expected modes"를 수치 기준(u+w, 1-link, 소유자)으로 preflight에 명시해야 합니다.

**C4. supervisor 자신의 대기 한도가 없습니다.**
- 실행 수단의 타임아웃이 300초나 1200초보다 짧아 controller를 종료시키면 정리 코드가 돌지 않습니다. 자식은 새 세션이라 살아남고, 슬롯은 결과 없이 소모됩니다.
- 실행 수단, 대기 한도(상한 초과), 한도 도달 시 controller에 신호를 보내지 않는다는 점을 승인 기록에 고정해야 합니다.

**C5. smoke 토큰의 승인 형식은 Owner가 정할 일입니다.**
- Driver의 결속 검증만으로 smoke를 시작할지, 해석된 digest를 Owner가 확인한 뒤 시작할지 승인 문면에 명시해야 합니다.

## 5. 비차단 한계

- **미검증 항목:** SBPL 컴파일과 실효, Apple Git 동작, 샌드박스 안 타이밍, 테스트 본문의 import 부작용. 첫 실패는 ROOT나 슬롯을 소모하고 Owner 복구 결정을 요구합니다.
- **canary INPUT 거부 증거:** base 입력 경로에만 해당합니다. smoke 입력은 같은 정책 형식을 쓰지만 별도 probe는 없습니다.
- **argv와 `shell_command` 병기:** 권위는 argv 배열이라고 명시하길 권합니다. shell 문자열에는 cwd와 stdin이 없습니다.
- **smoke 증거 보강(선택):** `preservation.jsonl`과 `failures/` 부재 확인, smoke의 `work/collection.json` 해시와 결속 digest의 교차 확인.
- **preflight 목록:** `CONTROLS/tests` 부재 재확인을 명시적으로 넣길 권합니다.
- **과업 기록 갱신:** SOURCE 안의 쓰기이므로 네 단계가 끝나거나 중단된 뒤로 미루는 편이 안전합니다.
- **private 계획:** 세 argv가 literal이라는 점과 7개 치환의 동등성은 Driver 기록으로만 확인했습니다.

## 6. 다음 단계 (실행 권한 아님)

1. Driver가 C1–C5를 계획 기록에 반영하고 새 해시로 식별합니다. 범위를 좁히는 기록 보완이므로 좁은 델타 확인으로 충분해 보이며, 재검토 필요 여부는 Owner가 정합니다.
2. Owner가 (A) README 바이트와 (B) 보완된 계획의 수락 여부를 각각 결정합니다.
3. 실행 승인은 그 뒤의 별도 게이트입니다. 네 명령, 결속 수단, smoke 토큰 규칙을 문면에 명시하고 직전에 preflight를 수행합니다.
4. 범위 밖으로 남는 것: 실행 후 runner-result R1과 Owner 수락, focused/complete/artifact, factory, product-prefix, D1/D2, P0a R1 전체, P0c R0.
````

### Driver Dispositions

The Driver proposes accepting the reviewed README S1/S2/S3/S5 result at the exact README hash above, with the nonblocking stale status sentence recorded below. The Owner has not yet accepted this result. The base plan is not ready for exact execution approval: C1-C4 must be resolved in a newly identified plan and C5 must state the intended Owner authorization. No source control/policy defect was identified in this bounded static review, but that does not prove runtime correctness or complete the original whole P0a/P0c gates. Four conditions plus one Owner choice explain the Reviewer's C1-C5 numbering; do not misreport five code defects.

| Item | Driver decision | Proposed disposition, not implemented by this review |
| --- | --- | --- |
| README result R1 | accept, pending Owner | S1/S2/S3/S5 match the accepted A2 dispositions; preserve the exact reviewed README as the result checkpoint. No must-fix was identified. |
| C1 identified verification/binding execution | accept | Prepare a small identified private helper and exact commands for read-only preflight, between-mode evidence checks and the existing canonical one-field binding procedure. Pin interpreter/flags/environment/cwd outside SOURCE, helper hash and argument allowlist. No SOURCE/CONTROLS imports, subprocess launches, network or fixture creation; only the two already named private binding files may be exclusively created by its binding mode. Verification modes are read-only. Any broader need stops preparation. Do not execute the helper against real evidence during preparation or modify runtime controls. The helper is a future execution input, not default permanent review output. |
| C2 nine-ancestor arithmetic | accept | Put the exact private path computation into preflight before acquisition, requiring the same nine entries and intermediate exec/runs/ROOT relationships as controller.test_ancestor_parameters. Point-in-time read-only Driver calculation found nine entries for each of the four planned run directories; this observation does not replace the future preflight. |
| C3 positive-probe DAC prerequisites | revise, accept explicit preflight | Require regular one-link files, executing-user ownership, exact expected modes and owner-write bit for SOURCE/hv2, controls/common.py and the actual copied input. Current read-only observations were 0755/0644/0644, all one-link and user-owned with owner-write. Unix ACL/group access can differ, so owner-write is a deliberately conservative plan precondition, not a universal necessary-and-sufficient OS rule. Recheck acquired OLD ownership/modes and prior result before canary; no positive write-open/chmod is performed now. |
| C4 outer supervision | accept | Identify the actual asynchronous execution facility, its yield/poll behavior and monitoring ceiling exceeding each controller ceiling. A yield is not a kill timeout. Do not wrap controllers in a shorter destructive deadline or send a signal to the controller when a monitoring deadline is reached; preserve the live session and stop later launches for a bounded recovery decision. Controller-owned child-group termination and existing budgets remain unchanged. Verify the chosen facility contract before claiming this condition closed; no hard whole-host deadline is promised. |
| C5 smoke-token authorization | needs-user; propose deterministic substitution | Recommend that a later exact execution approval expressly authorize starting smoke only after all identified helper/Driver checks pass and only replacing the digest token with the hash of the exclusively written one-field-bound invocation. Preserve the derived digest in the binding record. No arbitrary argument change or new selection follows from that approval. This is a proposed approval form, not a current decision; the Owner can instead require a pause after collection/binding to inspect the resolved digest. |
| Stale README delta-review sentence | accept as next narrow documentation correction | Align the Fixed Modes And Bounds sentence with accepted A2 static status while keeping runtime integration and wider reviews open. The current sentence is conservative and nonblocking; it is not changed under this review-only approval. |
| argv authority and preflight namespace | accept | State that argv arrays are authoritative; shell strings are display-only and omit cwd/stdin. Explicitly recheck CONTROLS/tests absence during preflight. This point-in-time absence was independently rechecked after review without importing anything. |
| Optional smoke diagnostics | accept as bounded evidence checks | In the next plan/helper, cross-check smoke work/collection.json against the bound digest and inspect absence of preservation.jsonl/failures alongside existing stop/failure gates. Such checks strengthen diagnostics only; no parent attestation or broader fixture custody is invented. |
| SOURCE record timing | accept | During future execution, delay task/README writes until all four modes finish or the sequence stops. Progress messages may continue. No source-record write is a hidden between-mode action. |
| Remaining limits | accept | SBPL/service behavior, Git behavior, timings and actual test imports remain unexecuted. The canary's input-path denial observation covers the initial input only, not a separate probe of the later smoke input. Private-path equivalence remains Driver evidence. Whole/future-mode/product/adopter qualification stays open. |

Only read-only arithmetic and lstat-style metadata checks supported the C2/C3/namespace observations. They neither tested ACL access nor executed controller functions or test discovery. The Reviewer statement about matching code does not authorize a helper, broaden a policy or accept a result.

### Proposed Next Bounded Slice — Plan Conditions Only

Recommend Owner acceptance of the exact README result above and authorization to prepare the C1-C5 plan refinements: the one stale README sentence, this task's dated correction record, revised private/review plans and one minimal identified verification/binding helper outside SOURCE. Keep the existing reviewed plan/packet immutable as historical input; identify any revised artifacts separately. Existing base input/control/source/runtime/root-map/selection/budget bytes stay unchanged. No DR/index/central STATUS, controller/product/test-source, policy, Git or adopter change is included.

Prepare exact helper commands and identity, static AST/allowlist checks without executing its body, private nine-ancestor proof, explicit modes/ownership criteria, actual supervision/yield/recovery behavior, argv authority, evidence checks and the proposed deterministic smoke-token approval wording. Record completion as an inspectable bounded delta with input/hash, GFM/link/disclosure/whitespace and durable-custody checks. Stop if this requires a broader helper, new dependency/control, permission, root, budget, source edit or technical contract choice. Keep actual binding outputs absent and ROOT uncreated.

This proposal includes neither another external review nor actual execution. The new helper and amended plan still need the applicable bounded review/Owner gate before use; a full packet retransmission is not automatically required or authorized. Decide the smallest sufficient delta review after inspecting the prepared change. The Owner's acceptance of the README is separate from acceptance of a corrected plan, helper or future execution. No approved preparation is represented here as already started.

### Verification And Custody

This turn changes only the task disposition and this appended result/Driver record. README, code, policies, initial invocation, plans and all reviewed inputs remain unchanged. Verify response bytes and all previous review records, final input identities, GFM rendering, links, disclosure and whitespace. Preserve the final task plus compact authorization/execution metadata outside the checkout with exact archive readback for the Owner's README decision and proposed plan-condition handoff. Retain the exact reviewed packet, plans and accepted control-input custody for that consumer until accepted handoff or equivalent durable custody replaces the need. After response text is verified in both task and archive, remove only the transient JSONL transport, empty stderr and duplicate standalone response; no raw API transcript becomes a default deliverable. The source worktree remains in active use for this concrete correction/implementation continuation and is retained. No checkout cleanup, commit or publication occurs.


## README Acceptance And Base-Plan Conditions Preparation — 2026-10-09

### Actual Owner Decision And Scope

The Owner replied “승인” to accepting the README result and preparing only the identified plan refinements and minimum verification/binding helper. Accepted README bytes: `30dd7428034439e56b62fa56b1031af059434d2112ca761897b90bf76591f6b7`; preceding review response `1edb8603ecc0584d3513590b3dc6939c999d597edf83cb49e34a51e04b7624db`, recorded task `e4c556a3b0948bb3f7fc9c70061bbd9c60206eb595c423cae21100ba9afb40ca` and packet `3487397dec1b345884c69291928679c45e6c5447c25e7a109f37f398c2d0de85`. Exact bytes remain recoverable. This accepts only the S1/S2/S3/S5 README result, with its recorded nonblocking stale sentence and limits. Prior bounded A1/A2 acceptances retain their historical scope.

The authorized new work is the stale README sentence, this existing progress record, separately identified private/review plans and exact command specifications, and one private helper outside SOURCE. No additional Reviewer transmission, helper body execution, controller/test execution, binding, acquisition, canary, discovery or smoke is included. No acceptance of the resulting new helper/plan, original whole P0a/P0c gate closure, D1/D2 choice, product/test/control/policy/budget/root-map/selection change, DR/index/central STATUS edit, Git action or adopter application follows.

### Prepared Result And Exact Identity

README changes only the conservative pre-A2 sentence: the bounded A2 runner corrections now have an accepted static checkpoint while actual collection/test behavior, work-layout integration and broader runner/factory qualification remain open. Current README SHA-256 `5747c9a3cf9cf277cfdf8d9af3a847f1356eebeba98703df79e04289b27de612` identifies this one-sentence preparation, separately from the accepted prior README.

| Prepared artifact | Exact SHA-256 | Role |
| --- | --- | --- |
| verify-base-plan.py | `0b11832758731b54d8df5463e167bebad3f5b2328d40b9b352e8e2133004c81c` | New 402-line, 22,924-byte private base-only verification/binding helper; not imported or executed |
| private-plan.json | `7147e80e70fc111d8767dba906da1d910fbd8b190646eee79fbd987ec80a33fb` | Corrected actual-path plan and expected parent input records |
| review-plan.json | `78a3f9f3efcb3f49664a29f4a0d2e6a1dd720d6c96a6f0b4c6859c3357753e0a` | Same non-path values with eleven identified private path/ancestor substitutions |
| private-commands.json | `2597703e8ea52337c6bc8b7719f2df4566b9ff28ecf1d884b4f0d459e42e295e` | Fixed tool specifications with literal plan digest, helper modes and four controller commands |
| review-commands.json | `daf49053eef1b75fca29f66b678e13cf72a3bec8e3c68d9f2ee9d57ff33f6386` | Corresponding illustrative command specifications; never executable review examples |

These new artifacts are separate from the preceding reviewed packet/plan; that historical input remains unchanged. The original schema-3 base invocation is still `bd4a422f98fb4e04d8a4c5fe3adb463ace5b48e16a3c50b5f474751c78be2ef1` at the same planned location. Its future smoke-input and binding-summary paths also remain unchanged and absent. All eleven control code/policy/data hashes, 101 source bytes/modes, sixteen-entry root map, twenty selected IDs, four controller argv arrays and 300/300/300/1,200-second controller budgets are unchanged. ROOT remains absent.

### C1 — Fixed Helper And Command Sequence

The helper directly runs under the pinned interpreter with -I -S -B, from its private preparation directory outside SOURCE and under the same seven-variable env -i allowlist. It accepts only PLAN, 7147e80e70fc111d8767dba906da1d910fbd8b190646eee79fbd987ec80a33fb and one of seven named modes. It verifies the plan bytes, its own file hash, interpreter path, cwd and environment before interpreting the pinned plan. It imports only errno/hashlib/json/math/os/pathlib/stat/sys; it never imports SOURCE/CONTROLS, launches a subprocess, invokes a controller/test, creates a fixture, accesses a credential or requests network access.

```text
preflight + two fixed read-only Git identity queries
  → acquire → after-acquire
  → canary  → after-canary
  → collect → after-collect → bind → before-smoke
  → smoke   → after-smoke
```

Controller commands retain their original input path/hash and base slots. The seven helper commands contain the exact new plan digest. The two separately identified read-only Git queries return HEAD and the tracked binary diff; the Driver compares exact stdout and exit status with the prepared literals. They are outside the helper and do not create a Git writer or grant arbitrary shell access. All outer tool exits must be zero before the matching artifact checks; helper success cannot replace an unavailable/nonzero controller tool result.

Read-only modes verify identified source/control/tool/root/seed inputs, OLD bytes/modes/inventory, exact parent inputs and success/cleanup fields, named canary evidence, collection occurrence accounting and smoke identities/counts. Parent inputs are matched against the complete planned command/environment/policy/budget record, including all fixed sandbox parameters. Canary child summaries/events remain diagnostic observations; no copied report becomes independent host attestation. The helper checks old release identity using the already identified baseline, without importing acquired code.

Only bind calls the write function, exactly twice: exclusive creation of the already designated smoke invocation and binding summary. It requires canonical seven-key collection JSON, duplicate-key rejection, exact source/root/control identities, empty factory IDs, every selected ID and occurrence, and a matching collect parent/input record. The bound invocation changes only collection_sha256. The summary identifies the plan/helper/input/parent/collection bytes, actual selected multiplicities and every synthetic unittest.loader. ID. It flushes/fsyncs/re-reads each file; it neither overwrites nor deletes either file. A partial two-file write remains a stop state with no retry. before-smoke rechecks the same deterministic bytes and evidence without writing.

The helper has 4 MiB JSON/source-read, 16 MiB diagnostic-log-read and 128 MiB tool-binary-read ceilings. These reject oversized evidence; they are not filesystem quotas, new test budgets or permission to discard artifacts. Its schema/type/canonical checks are stricter diagnostic checks on this exact base plan. No dynamic test selection, default-discovery filtering, factory implementation or product-prefix behavior is introduced. Source/runtime trust, file-read races, mutable child evidence, filesystem blocking and nondeterministic rediscovery retain their stated limits.

### C2/C3 — Preflight Before Consuming A Slot

The plan and helper explicitly compute each planned run directory plus its parents before acquisition: exactly nine entries, the expected runs/exec/ROOT intermediate entries and final /. The private paths currently satisfy all four calculations. CONTROLS/tests absence is an explicit repeated check.

SOURCE/hv2, controls/common.py and the actual copied initial input must be regular one-link files owned by the executing user, with modes 0755/0644/0644 respectively and owner-write bit 0200. Current read-only observations matched. Before canary, the acquired OLD .gitignore ownership/mode and prior result's one-link/euid/0200 properties are checked. The newly generated result mode is observed rather than assumed to be 0644 because process umask can vary. These are conservative metadata preconditions, not ACL/write-open proof; actual positive probes remain unexecuted.

The helper accounts for the existing trusted macOS aliases: /etc/gitconfig and /private/etc/gitconfig must both be absent, and /var/empty must resolve to /private/var/empty. This does not loosen unlinked-path rules for SOURCE, CONTROLS, inputs, ROOT or evidence. The pinned system shell is additionally identified as a host tool; no dependency installation or host configuration change occurred.

### C4 — Asynchronous Supervision Without Premature Termination

The concrete execution facility is tools.exec_command with shell=/bin/sh, login=false, tty=false, env -i, exec and DEVNULL redirection. The trusted parent/helper runs outside the app sandbox under separately approved execution; each controller child retains the unchanged SBPL policy. The helper's permitted reads/writes are an authorized behavioral boundary, not an additional OS sandbox.

Launch yields after 1,000 ms and returns a session ID while running. tools.write_stdin with empty chars polls for at most 30,000 ms per call. These settings bound output waiting, not process lifetime; the available tool schema exposes no hard-timeout parameter. Controller monitoring ceilings are 360/360/360/1,260 seconds, above the existing controller ceilings; helper/read-only-Git monitoring ceilings are 60 seconds. Record dispatch/elapsed time and report progress at most 60 seconds apart. No mode overlaps another.

At a monitoring ceiling, stop later launches and preserve the live session/evidence for a bounded recovery decision. Do not send Ctrl-C, terminate/close the session or signal the controller. Do not add timeout/gtimeout, shell alarms or a wrapper subprocess deadline. The controller still owns its existing child-group cleanup. A tool/session loss is unavailable supervision, not proof of group absence. These are monitoring escalation points, not a controller budget increase or a hard guarantee against app/transport/host failure or blocking filesystem calls.

### C5 And Remaining Approval Form

The prepared future approval form proposes deterministic continuation: after every fixed helper/Driver check succeeds, verify the exact bound invocation bytes/digest and replace only the smoke command's digest token, then start that fixed smoke command. This would avoid a separate digest-only pause. The current preparation approval does not adopt or exercise that execution authority; the Owner may instead require a pause to inspect the resolved digest in the later exact execution decision. No arbitrary path, argv, selection, policy or budget adjustment follows from either form.

The plan also makes argv arrays plus cwd/stdin authoritative and shell strings display-only. After smoke, collection bytes must match the bound digest and no preservation.jsonl/failures, suite event or stop marker may contradict success. SOURCE/task/README writes are deferred until the whole sequence completes or stops. Child evidence remains mutable; the canary only probes the initial input path, not the later separate smoke-input path. All wider execution/result/Owner gates remain open.

### Static Checks, Review Need And Custody

The Driver AST-parsed the new helper without importing or executing its body. Static checks confirmed the eight stdlib imports, seven-mode allowlist, absence of assertions used as runtime guards, absence of subprocess/network/dynamic-code/signal or filesystem-mutation APIs outside the named binding writer, one read-only open site and one exclusive-write open site, and exactly two write-function calls inside bind. The fixed tool argv/environment/cwd/stdin/shell round-trips, per-mode expected parent records, unchanged source/control/input identities and controller budgets were checked against the existing control source. These checks are not behavioral tests or a runtime pass.

An initial disclosure check rejected residual account-ancestor labels newly present in the expected-parent command records. Three ancestor mappings were added to the existing eight substitutions, for eleven total. The final review-plan and review-command copies preserve all non-path data and contain no identified private repository/account labels. No external transmission occurred. This was a preparation validation correction; no runtime slot or binding output was created.

Document checks cover the exact one-sentence README diff, preservation of the prior task except its current disposition, GFM rendering/links/disclosure/whitespace and exact archive readback. The new helper/result and corrected plan need their applicable bounded R1/R0 review and Owner decisions before use; AST checks do not waive them. Prepare a fixed delta-review request for these changed artifacts and necessary unchanged control context, retaining explicit inherited/omitted scope. It is not an automatic whole P0a/P0c rerun, a new model invocation or an approval to execute.

Retain the new helper/plans/commands, exact previous inputs and final task/README outside the source checkout for the Owner's bounded-delta review and subsequent separately authorized execution/recovery handoff, until accepted handoff or equivalent durable custody replaces that need. Disposable static-check scripts/rendered output are not default permanent deliverables. The source worktree remains needed for this concrete next review and implementation continuation and is retained. Generic adopter impact: no update currently needed for this preparation-only change; actual installations remain unassessed.


## Integrated Base Verification Bundle Authorization — 2026-10-09

The Owner requested one integrated plan covering preparation, implementation within scope, necessary reviews and Driver dispositions/corrections, isolated actual verification, failure fixes and revalidation, without per-step approval waits. After the Driver presented the file/command/completion/stop boundaries, the Owner replied “진행하자”. This is actual authorization of that bounded plan, not final result acceptance.

Scope is P0/base verification of all actually discovered occurrences of the fixed twenty seed IDs. Editable source controls are common.py, controller.py, acquire.py, canary.py, observer.py and runner.py, plus their README and this existing task. The five existing seed-test modules may receive only path/environment/fixture-setup corrections, preserving assertions and test meaning. Private helper/invocation/plan/command/review/evidence revisions are within the named bundle. Product src/launchers, SBPL permissions, baseline/oracle/selection, assertions/discovery/timeouts, DR/index/central STATUS and real-project state remain unchanged. Any required expansion stops for the Owner. P1-P4 implementation and future-mode/factory qualification are excluded.

The Owner authorizes at most eight fresh no-tool Claude reviews, each at most 600 seconds, through the existing claude.ai/firstParty/pro subscription path. Check the path on every call; no paid API or other cost path fallback. Necessary changed code/diffs, bounded source/test context and sanitized verification evidence may be sent after fixing their bytes/hashes without another per-packet approval. Preserve the response verbatim and Driver accept/revise/defend/needs-user separately. Initial plan/result review, execution-affecting correction review and final actual-result review remain technical gates, not Owner acceptance.

Execution permits the preidentified base root and r01/r02/r03 siblings under the approved agent-worktree root: one initial attempt and at most three corrected attempts, all with the same nine-ancestor layout and original policies and ceilings. Roots were absent at authorization. This explicit bounded recovery scope replaces the earlier per-step Owner execution/retry prohibition only here. Preserve failed roots/slots and required exact input/evidence; never reset, reuse, overwrite or delete consumed slots. Freeze and review corrected inputs as applicable, then repeat acquire/canary/collect/bind/smoke in the next named root. Do not combine different candidate evidence into one pass.

After initial detection, three failed corrections/revalidations for the same cause stop the bundle; renaming or new roots/sessions do not reset that count. Four total execution attempts and eight review calls are independent ceilings. Also stop for scope/design/security/cost changes, permission expansion, real-project application, unapproved dependency/budget/assertion/selection changes, unexpected outside access/write/credential exposure, surviving processes or unavailable supervision, unexplained drift or missing preservation. Capture the cause, consumed bounds, preserved state and options. This authorization covers safe bounded corrections, not weakening a criterion to pass.

The fixed command family remains isolated pinned Python plus unchanged controller modes acquire-base/canary-base/collect-base/smoke-base, with 300/300/300/1,200-second ceilings, seven helper modes and two read-only Git identity queries. Same-subscription review and this exact controlled command family are authorized without further stage approval. Freeze actual input/plan/helper hashes for every dispatch. After canonical binding and before-smoke checks pass, substitute only the verified digest and continue without a digest-only Owner pause. Parent positive probes retain their known write-open-without-write and same-mode OLD chmod/ctime behavior. Existing synthetic-fixture Git operations are allowed only inside the tests; no source or real-project Git mutation is included.

Use the existing asynchronous supervision plan: fixed non-login /bin/sh and env -i, DEVNULL stdin, outside-app-sandbox trusted parent/helper, unchanged sandboxed children. Poll output without killing the controller at a monitoring ceiling; retain live sessions and stop later launches for recovery. Do not edit SOURCE while any execution process is active. After a sequence ends/stops, this task records observations and counts; no second progress ledger or runtime Work is created.

Completion is one exact candidate with all base parent/evidence gates passing, every selected occurrence executed with no failure/error/skip/expected/unexpected success or unstarted/unfinished result, no drift/surviving group, required custody and resolved final technical review findings. Report base PASS with limits. Final Owner acceptance, Work Done/STATUS, commit/push/PR/merge/deployment and actual adopter application are excluded and will be proposed together at the end.

Starting source task was `89a9b27d2606ae9505b3d0cc85423888a6124b9fe620172d22e1c23087025660`; all prepared inputs matched. The preceding preparation and review packets remain historical unchanged inputs. Current bundle/private plan/commands and their path-substituted review equivalents are separately identified. The unchanged helper is relocated to attempt-00 with no code edits; only bounded authorization, input/output locations and review/custody context change. ROOT remains absent and no helper/controller/test execution has occurred at this checkpoint.


### Integrated Bundle Review Call 1 — Incomplete

Initial combined base-controls/helper R1 and execution-plan R0 review used fresh Claude Opus 5.5 (`claude-opus-5-5`), session `d77ea265-5223-4dae-9353-f1d54966a8fe`, no tools/MCP, through the confirmed claude.ai/firstParty/pro subscription. The 329,949-byte packet was `90b9c0418fd68fdcc063ac34b8101a7dcb6e5d652fdbdb5ecd57e8854a583522`, base `238514686078ce1564010a7b69013f48a635c57c`, with tracked-diff identity and additional untracked reviewed inputs listed in the private snapshot. The review-only process reached 600.02 seconds and was terminated by its predeclared 600-second wrapper limit: child exit -9, no final result and no completed reviewer text. There is no reviewer response to quote and no verdict to accept. Input checks passed before/after, tools/MCP were empty and stderr was empty. This reviewer-process deadline is not a controller termination policy.

Driver disposition: incomplete/unavailable; do not promote to R1/R0 PASS. One of eight review calls is consumed; zero execution roots are consumed and no helper/controller/test was launched. Prepare a smaller packet retaining the complete base-control/helper implementations and exact execution specification while excluding repeated historical narrative and identifying omitted inventories/context. Use the same subscription and no-tool fresh-session boundary; medium review effort reduces the risk of another timeout without changing authorization, runtime policies or test criteria. The initial timeout is cause `review-response-timeout`, detection 1, failed correction cycles 0. No source/control/test or invocation bytes changed.


### Integrated Bundle External-Review Dispatch Block — 2026-10-09

The second review packet is prepared at 192,172 bytes, SHA-256 `d73659c8274781ab6a6b6a12643ac719e2d297aa0fdc61a72bab05d4e2e1a3da`. It supplies complete helper/six-control/two-policy/seed code and compact equivalent plan/command data, with omitted original-test/product/baseline inventory bodies explicitly identified. Its fourteen full implementation/specification inputs are byte-identical inputs already included in review call 1. No new implementation source or external destination was added.

Automatic approval review rejected dispatch before process creation, stating that the private implementation payload lacked specific user authorization for transmission to the external Claude service. The Driver rechecked the preceding Owner-approved plan, which expressly included the named control/helper inputs, necessary Claude reviews and changed review-input transmissions without per-step approval. A read-only comparison confirmed the exact repeated-input subset. One same-command resubmission with that evidence was also rejected: the approval service did not accept the earlier plan approval as payload-specific authorization. No alternate route or indirect invocation was attempted.

The Driver requested explicit Owner approval for this exact packet to the external Claude service using the existing subscription, with no tools and a 600-second limit. Pending that response, the external-review prerequisite and dependent actual verification remain stopped. The two rejected dispatches created no process or review authorization/output artifacts and consume no model call or execution root. Totals remain one actual review call (timeout), zero actual verification attempts, and zero failed correction cycles for a runtime defect. No second-review verdict, execution PASS or Owner acceptance exists.

Required inputs, timeout metadata and this record are retained outside the source checkout for the Owner's pending transmission decision and bounded execution/recovery continuation. The source worktree has concrete near-term use for that continuation and is retained. Product/source/test/policy bytes, baseline, selection, central STATUS and Git lifecycle remain unchanged. Final acceptance, Work Done/STATUS and Git/publication remain outside this bundle. This is a dispatch-policy block, not an observed product failure.


### Exact Second-Packet Transmission Authorization

After the Driver identified the prepared 192,172-byte packet and explicitly requested permission to transmit its private verification implementation and execution specifications to the external Claude service through the existing subscription, the Owner replied “진행하자”. This authorizes the exact second packet `d73659c8274781ab6a6b6a12643ac719e2d297aa0fdc61a72bab05d4e2e1a3da`, one fresh no-tool review up to 600 seconds, and continuation under the earlier integrated bundle boundaries. It does not change scope, billing path, security policy or final acceptance authority. The packet bytes remain unchanged; only the local task-input guard is refreshed for this explicit authorization record.


### Integrated Bundle Review Call 2 — Conditional Static Result

Fresh Claude Opus 5.5 (`claude-opus-5-5`), session `08a7b7f1-1b48-4c24-a9d2-27fb0ce7e1d7`, completed in 257.91 seconds, exit 0, no timeout/API error, tools/MCP empty, subscription claude.ai/firstParty/pro. The exact explicitly approved packet was 192,172 bytes, SHA-256 `d73659c8274781ab6a6b6a12643ac719e2d297aa0fdc61a72bab05d4e2e1a3da`. Private snapshot records base, tracked diff and reviewed untracked inputs. Pre/post input checks passed. No actual helper/controller/test was executed during the review.

#### Reviewer Response Verbatim

````text
# 리뷰 2/8 — base controls/helper R1, 실행계획 R0 (정적 검토, 실행 없음)

## (A) base 저작 controls/helper R1 — 조건부 통과 (차단 1건, helper만 교정 필요)

**A-1 [차단] `verify-base-plan.py::main` — 환경 완전일치 검사**

- **문제:** `need(same(dict(os.environ), plan["parent_environment"]), "helper environment")`가 preflight에서 실패할 개연성이 높습니다.
- **근거:** macOS framework Python은 `env -i`로 띄워도 CoreFoundation 초기화가 `__CF_USER_TEXT_ENCODING`을 환경에 넣습니다. CPython `test_subprocess`도 같은 이유로 `__CF*` 키를 무시합니다. 그러면 `os.environ`이 7키가 아니라 8키가 됩니다.
- **확신도:** 실행하지 않은 추정입니다. helper 본문은 아직 한 번도 실행되지 않았습니다(`helper.status`).
- **영향:** fail-closed이고 ROOT/slot을 소비하지 않습니다. 다만 교정하면 helper SHA → plan SHA → commands가 연쇄 변경되므로 첫 dispatch 전에 고치는 편이 낫습니다.
- **최소 교정:**
  ```python
  env = dict(os.environ); cf = env.pop("__CF_USER_TEXT_ENCODING", None)
  need(same(env, plan["parent_environment"]) and (cf is None or (type(cf) is str
       and cf.startswith("0x") and set(cf) <= set("0123456789abcdefABCDEFx:"))), "helper environment")
  ```
  plan의 `helper.execution_limit`에 이 단일 OS 주입 키 허용을 한 줄 명시하면 됩니다.
- **범위:** helper/plan은 private edit scope 안이고, 정책·권한·선택·assertion 변경이 아닙니다. controller와 child는 env를 완전일치로 검사하지 않고, `canary.py`의 forbidden 패턴에도 이 키는 걸리지 않으므로 controls 수정은 필요 없습니다.

**이 순서에서 정합성을 확인한 것 (차단 없음)**

- **parent inputs:** `controller.run`이 쓰는 `inputs.json` 13키, `-D` 순서(SOURCE…LOG, ANCESTOR_0..8), `-f` 정책, `python_command` argv, env PATH 조립, cwd, budget이 4개 step의 `expected_parent_inputs`와 일치합니다. smoke의 토큰과 `collection_sha256` 치환 경로(`parent_result`)도 맞습니다.
- **result와 수집:** result 11키, `COLLECTED n sha256 h` 교차검사, collection 7키와 canonical 바이트가 runner와 helper 사이에 일치합니다.
- **bind:** `dict(c)`에서 `collection_sha256`만 바뀌고, `common.config`의 키 집합과 `factory is (phase=="entry")`를 통과합니다. 두 파일 모두 exclusive `xb`로 쓰고, before-smoke 재계산은 결정적입니다.
- **canary 증거:** `boundary-positive.json`, `canaries.json`, `child-canary.json`, 4개 events 파일의 이름·필드가 `canary.py`/`observer.py` 산출과 일치합니다. short-write는 `b"s"`, 0600, hv2 보존, -9로 맞습니다.
- **smoke 증거:** `executed.jsonl` 행 5키, counts 10키, 부재해야 할 파일 목록이 `runner.py`와 일치합니다.
- **9-ancestor:** 치환 경로 기준 9개입니다. 실제 경로와 r01–r03은 Driver가 확인한 동등성에 의존합니다.

**비차단 메모**

- `controller.group_exists`는 `ProcessLookupError`만 잡습니다. `killpg`가 EPERM을 내면 `result.json` 없이 종료하지만 fail-closed이므로 base에서는 수정이 필요 없습니다.
- `regular()`/`raw_file()`의 `st_nlink == 1` 요건은 runtime launcher와 CLT `git`에도 적용됩니다. 준비 관측에는 `host_tools`와 probe 3개의 nlink만 있으므로, Driver가 두 바이너리의 nlink=1을 stat으로 사전 확인하기 바랍니다(쓰기 없음).
- SBPL 아래에서 flock, `F_FULLFSYNC`, `F_GETPATH`, CF 초기화, git 동작이 실제로 되는지는 정적으로 확정할 수 없습니다. canary가 판정하며, 실패하면 정책 변경이 필요하므로 계획대로 Owner STOP입니다.

## (B) 정확 실행계획 R0 — 조건부 통과 (교정 1건, 확인 1건)

**B-1 [실행 전 교정] `read_only_git_checks.tracked_diff` — 읽기 전용이 아닐 수 있음**

- **문제:** `git diff HEAD --binary`는 stat 정보가 바뀌었으면 index를 기회적으로 refresh하여 `common_git/worktrees/<name>/index`(와 `index.lock`)를 쓸 수 있습니다.
- **충돌:** 계획의 "read-only Git query", "no Git writer", write_boundaries와 어긋나고, stop 조건인 "unexpected outside write"에 해당할 수 있습니다. SOURCE 해시에는 영향이 없습니다.
- **최소 교정:** 두 git check의 argv/cmd env에 `GIT_OPTIONAL_LOCKS=0`을 추가합니다(또는 `git --no-optional-locks`). plan과 commands 양쪽에 동일하게 반영하고 SHA를 재동결합니다. expected stdout은 그대로입니다.

**B-2 [Driver 확인, 차단 아님] 식별자 표기**

- 리뷰본의 "original SHA256"(bundle `0f7de2…`, plan `944534…`, invocation 발췌 `4a703f…`)이 plan 내부 참조(`bundle_plan_sha256` `0b9bcc…`, commands의 `private_plan_sha256` `d4fde2…`, `initial_input` `bd4a42…`)와 다릅니다.
- 경로 치환·발췌 때문으로 보이나, 여기서는 검증할 수 없습니다. 실제 private 파일 바이트가 내부 참조와 일치하는지 Driver 기록에 명시하기 바랍니다.

**그 외 계획 요소 (문제 없음)**

- 순서(preflight → git 2건 → acquire → after-acquire → canary → after-canary → collect → after-collect → bind → before-smoke → smoke → after-smoke)가 helper의 `count`/`expected_runs`와 일치합니다.
- 모니터링 ceiling(360/360/360/1260, helper·git 60)과 "kill 금지·세션 보존" 규칙, `/bin/sh` `exec … < /dev/null` 형식, BOOTSTRAP 인용, smoke 토큰 단일 치환 규칙에 문제가 없습니다.
- A-1/B-1을 고치면 helper/plan/commands SHA가 바뀝니다. 아직 아무것도 실행되지 않았으므로 attempt-00/ROOT는 소비되지 않았고, 재동결 후 변경분(delta) 확인으로 충분합니다.

## 한계

- 리뷰하지 않은 것: `source_files` 표, `baseline-inputs.json` 내용, 테스트 본문, 제품 import(`hv2ref.workspace.classify_target` 포함), README 본문, 실제 실행.
- A-1은 실행 없이 내린 고개연성 판단입니다.
- 이 결론은 최종 Owner 수용, Work Done/STATUS, Git, 채택을 포함하지 않습니다.
````

#### Driver Dispositions

- A-1: accept the bounded helper correction, with the finding explicitly static and not reproduced. Permit only the named runtime-injected `__CF_USER_TEXT_ENCODING` value if it matches the review's restricted hexadecimal/colon format, while all other environment entries must exactly match the seven declared values. Record this private-helper diagnostic allowance; shell dispatch environment, child SBPL permissions and credential-key rules remain unchanged. This does not assert that the host actually injected the key.
- B-1: accept. Add Git's `--no-optional-locks` option to the two identity queries and the review wrapper's corresponding read-only identity checks. This narrows optional writes and preserves expected stdout, helper/controller environment and test behavior. Opportunistic index refresh was a static risk; no actual unintended write was observed or established.
- B-2: accept verification request. Distinguish original private-file hashes from path-substituted review-file hashes; verify every internal private reference and the path-equivalent reviewed data after refreezing. A review copy's different hash is not input drift.
- Runtime/Git nlink note: accept the read-only stat check before dispatch; require regular one-link files as the existing helper/control already require.
- Remaining limitations: accept. A canary failure requires diagnosis; stop if its fix needs SBPL permissions or another excluded boundary change. Not every canary failure necessarily requires a policy change. No omitted source body or actual runtime behavior was reviewed by this packet.

The conditional review is not an execution PASS or Owner acceptance. Preserve attempt-00 inputs unchanged and prepare a separately identified correction input directory for the same still-absent initial execution root. Freeze the helper/plan/command deltas, perform bounded technical delta review, then execute the approved sequence if ready. Two of eight review calls are consumed; zero actual verification roots are consumed. No repeated runtime-cause correction failure has occurred.


### Review-2 Corrections Prepared; Delta Dispatch Blocked

Both accepted corrections are prepared in a new private correction-input directory while preserving attempt-00 unchanged. Helper SHA-256 is `dcc35fa2d22fb9bd485c56f3e2181ea322674b968cd92d1bd2da8250e204e4cd`; private plan is `9c37ff9a9e32ea2f6b030478b41250b0bca6ddf76df8f82c44744fa646e217ad`. The base invocation bytes and execution root are unchanged. The helper body diff replaces only the environment equality line with the named optional CoreFoundation key check; the Git queries add only `--no-optional-locks`. Dependent private paths/hash references and shell command strings are updated consistently. The reviewer wrapper uses the same no-optional-locks option for its identity queries.

Static checks passed: AST syntax without running the helper; literal shell/argv equality for all commands; identical plan/command Git queries and expected stdout; internal helper, plan, invocation and bundle hashes; unchanged source/control/runtime identities; runtime and Git are regular files with nlink=1. These are authored-correction checks, not actual reproduction or runtime success. No policy, assertion, test selection, timeout or source product/control code changed.

The delta-review packet is 20,321 bytes, SHA-256 `7f543c900e21cf0f63e423a63a9884e3f04ecdb95cd9384e66e1ff750ccb98bf`: previous review verbatim, exact helper diff and complete corrected main/entry function, and corrected relevant plan/Git dispatch data with private paths substituted. Automatic approval review rejected dispatch before process creation because it considered the prior specific approval limited to the previous packet. No workaround was attempted. A request now asks the Owner to explicitly authorize this packet and bounded necessary subsequent private verification code/specifications/sanitized results to the same external Claude subscription, within the six remaining calls and original limits; the Owner may instead choose this packet only or stop. No such new response has been recorded yet.

Counts remain two actual review calls, one timed out and one conditional static result; zero actual helper/controller/test executions and zero consumed roots. The third call did not start. Neither static correction has failed revalidation; no cause counter or limit is reset. Preserve the exact correction inputs and pending packet for the Owner decision and actual verification. The source worktree remains in use for this concrete continuation; no cleanup or Git lifecycle action is eligible.


### Explicit Bounded Follow-Up Transmission Authorization

The Driver explicitly requested permission to send this correction packet and subsequent necessary private verification code, execution specifications and de-identified result/failure logs within this same Colvia base-verification bundle to the external Claude service. The Owner replied “승인”. This authorizes the prepared 20,321-byte packet `7f543c900e21cf0f63e423a63a9884e3f04ecdb95cd9384e66e1ff750ccb98bf` and the stated bounded follow-up payload changes through the existing Claude Pro subscription, no-tool fresh sessions, at most six remaining calls and 600 seconds each. Product implementation, real-project data, credentials, different destinations and API billing remain excluded. Keep per-round input identities and disclosure/authentication checks; do not request approval solely because in-scope review bytes changed. This data-transmission authorization does not expand implementation scope or final acceptance authority.


### Review Call 3 — Subscription Limit, No Technical Verdict

The explicitly authorized correction-packet call started through the verified existing claude.ai/firstParty/pro path. It returned in 2.10 seconds with CLI exit 1, is_error=true, no timeout, startup model `claude-opus-5-5`, session `38ef664c-ef66-4619-9d33-fceeb4327a0f`, empty tools/MCP, and no model-usage result. Input checks passed before/after. The packet remained `7f543c900e21cf0f63e423a63a9884e3f04ecdb95cd9384e66e1ff750ccb98bf`. The service response is preserved verbatim below; it is an availability error, not a review finding or verdict.

````text
You've hit your session limit · resets 11:30pm (Asia/Seoul)
````

Driver disposition: unavailable. The account's indicated reset is 2026-10-09 23:30 Asia/Seoul; this is the service's reported reset, not guaranteed restored availability. At the observed time 23:06 KST the required correction review was unavailable. Do not substitute an API key, change billing/provider/model to evade the limit, repeatedly retry before reset, waive the technical gate or claim base PASS. The prepared helper/command corrections remain statically checked but not yet reviewer-confirmed or executed. No runtime defect or failed runtime correction was observed.

Three review dispatch slots of eight are conservatively consumed (one timeout, one completed conditional technical review, one subscription-limit error); five remain. Actual verification attempts remain 0/4 and helper/controller/test executions remain zero. The initial and all three correction execution roots are absent. The Owner's explicit bounded payload-change authorization remains valid; another approval is not required solely because the service limit clears or necessary in-scope review bytes change.

Resume at the pending correction review once the same subscription becomes available: retain r03 as failed evidence, prepare the next fresh-session review slot with the exact same correction packet and current input guards, recheck authentication and source/input preservation, and consume one of the five remaining slots. If technical findings are resolved, run the identified attempt-00-c01 preflight and the full approved base sequence with its fixed commands. Preserve the initial root until actual acquisition; do not allocate a new execution attempt just because this review call failed. No background retry or scheduler was created. Final Owner acceptance, Work Done/STATUS and Git/publication/adopter actions remain excluded.


### Review Call 4 — Correction Delta Ready For Execution

After the service's reported reset, the Owner requested continuation. Fresh same-subscription Claude Opus 5.5 (`claude-opus-5-5`), session `9ee8de76-06c7-4dd2-86a2-3e514825375b`, reviewed the unchanged 20,321-byte correction packet `7f543c900e21cf0f63e423a63a9884e3f04ecdb95cd9384e66e1ff750ccb98bf`. It completed in 51.20 seconds, exit 0, no timeout/error, tools/MCP empty and input checks passing before/after. This is actual dispatch 4/8; the response's inherited heading says 3/8 because the exact retained prompt preceded the subscription-limit attempt. Preserve that heading verbatim without using it to reset the count. Four review slots remain.

#### Reviewer Response Verbatim

````text
# 리뷰 3/8 — A-1/B-1 교정 delta (정적 검토, 실행 없음)

두 교정 모두 이전 지적을 충족하며 새 차단 사항은 없습니다. 상속된 조건부 base R1/R0는 preflight → git 2건 → acquire → canary → collect → bind → smoke로 진행해도 됩니다. 다만 B-1에는 제가 정적으로 확정하지 못한 잔여 불확실성이 하나 있어, Driver의 쓰기 없는 전후 관측을 권고합니다.

## (A) helper R1 delta — 충족, 차단 없음

- **교정 일치:** A-1 제안과 본문이 같습니다. `pop` 후 나머지 7키는 여전히 `same()`으로 완전일치 검사하므로, 다른 키가 추가·누락·변조되면 그대로 NON-PASS입니다.
- **허용 범위:** 완화된 것은 `__CF_USER_TEXT_ENCODING` 한 키뿐이고, 값은 `0x` 접두와 16진/`x`/`:` 문자로 제한됩니다. 통상 형태(`0x1F5:0x0:0x0`, 비영어 로캘의 `0x1F5:0x3:0x33`)는 통과하고, 경로·공백·자격증명 형태는 통과하지 못합니다.
- **양쪽 경우 처리:** 키가 주입되지 않으면 `cf is None`으로 통과합니다. 실제 주입 여부는 미관측이며, `helper.status`도 그렇게 적고 있습니다.
- **회귀 없음:** 괄호와 우선순위가 맞고, 예외 경로와 `fixed_inputs` 이후 흐름, mode별 분기는 그대로입니다. dispatch env는 7키로 유지됩니다.
- **plan 정합:** `execution_limit` 명시 문구가 helper 동작과 일치합니다. `helper.path`, `cwd`, `write_boundary`가 모두 `attempt-00-c01`로 함께 옮겨졌고, `helper.sha256`과 `private_helper_sha256`이 같습니다(`dcc35f…`).

## (B) 실행계획 R0 delta — 충족, 차단 없음 (확인 1건)

- **교정 일치:** `--no-optional-locks`가 서브커맨드 앞 전역 옵션 위치에 올바르게 들어갔습니다. 두 check의 argv와 `/bin/sh` cmd 문자열이 토큰 단위로 일치하고, env 7키·cwd·expected stdout/SHA·ceiling은 그대로입니다.
- **B-2 해소:** private input/plan/bundle 해시가 내부 참조와 일치한다는 Driver 확인으로 해소된 것으로 봅니다. 저는 그 바이트를 직접 검증하지 않았습니다.
- **nlink 메모 해소:** runtime과 git 바이너리가 regular one-link라는 Driver 확인으로 해소됐습니다.

**B-1 잔여 [비차단, Driver 확인 권고]**

- **불확실성:** `git diff`의 기회적 index refresh가 이 CLT git 버전에서 optional-locks 설정을 실제로 따르는지 저는 기억만으로 확정하지 못합니다. 이전 리뷰에서 제가 제안한 교정이 완전한 보장이 아닐 수 있습니다.
- **발생 조건:** stat만 바뀌고 내용이 같은 tracked 파일이 있을 때만 refresh가 일어납니다.
- **영향:** 쓰기가 일어나도 worktree gitdir의 `index`에 한정되고, SOURCE 해시와 expected stdout에는 영향이 없습니다.
- **권고:** `tracked_diff` 전후로 해당 `index`의 size/mtime(또는 SHA)을 쓰기 없이 관측해 기록합니다. 변하면 계획의 "unexpected outside write" 규칙대로 STOP입니다. plan/commands 변경이나 재동결은 필요 없습니다.

## 진행 판단

- **진행 가능:** 초기 ROOT는 미실행·미변경이고 attempt-00 파일은 보존돼 있어, 소비된 slot은 없습니다.
- **상속 조건 유지:** SBPL 아래의 flock, `F_FULLFSYNC`, `F_GETPATH`, CF 초기화, git 동작은 canary가 판정합니다. 실패하면 정책 변경이 필요하므로 Owner STOP이고, kill 금지·세션 보존 규칙도 그대로입니다.
- **preflight 실패 시:** `helper environment` NON-PASS가 나오면 stderr 사실만 기록하고 중단합니다. ROOT는 소비되지 않습니다.

## 한계

- 이번 검토는 delta, `main` 본문, 제시된 plan 발췌에 한정됩니다. 나머지 helper 함수, controls, source, tests, SBPL은 리뷰 2의 상속 판단이며 새로 전체 검토하지 않았습니다.
- 해시 일치, argv round-trip, nlink는 Driver 진술에 의존합니다.
- 런타임 주입과 preflight 성공은 미관측입니다.
- 이 결론은 최종 Owner 수용, Work Done/STATUS, Git, 채택을 포함하지 않습니다.
````

#### Driver Dispositions And Execution Boundary

- A-1/B-1: accept the bounded correction result. No open must-fix remains in this delta; proceed under the already authorized exact attempt-00-c01 commands and inherited base R1/R0 limits. This is a technical readiness disposition, not actual execution success or Owner result acceptance.
- B-1 residual observation: accept the nonblocking recommendation. Read the actual worktree gitdir index bytes and stat fields before/after the two fixed identity queries without touching it. Unexpected change stops later launches under the existing rule; no forced dirty-stat fixture or new Git command is added.
- B-2/nlink: resolved by recorded Driver byte-reference and stat checks, not independently executed Reviewer evidence.
- Canary/preflight failures: retain the existing bounded recovery rules. Diagnose the concrete cause; a failure is not automatically proof that a policy change is necessary. Stop for actual excluded permission/security/design changes or unavailable supervision; perform only authorized corrections otherwise.
- Inherited/omitted scope: accept the stated static limitations; do not claim full-source re-review, runtime environment observation or final qualification.

The current helper and plan are `dcc35fa2d22fb9bd485c56f3e2181ea322674b968cd92d1bd2da8250e204e4cd` and `9c37ff9a9e32ea2f6b030478b41250b0bca6ddf76df8f82c44744fa646e217ad`. Source, controls and initial invocation remain unchanged; the corrected directory holds identified dispatch inputs and old attempt-00 remains preserved. All four execution roots are still absent before dispatch. This task will not be edited while the actual sequence has an active process; progress can be reported in conversation.


### Actual Attempt 00 — Preflight Passed; Acquisition Failed Before Python Code

The exact attempt-00-c01 command specification SHA-256 is `d97b76ad3c7287e025c2fd2d319eb63caf33d91ac05c16bd77c71aec8361cad3`, helper `dcc35fa2d22fb9bd485c56f3e2181ea322674b968cd92d1bd2da8250e204e4cd`, private plan `9c37ff9a9e32ea2f6b030478b41250b0bca6ddf76df8f82c44744fa646e217ad`, initial invocation `bd4a422f98fb4e04d8a4c5fe3adb463ace5b48e16a3c50b5f474751c78be2ef1`. Dispatch used the approved pinned CPython 3.14.7 `-I -S -B`, fixed non-login /bin/sh/env-i/DEVNULL commands, then the unchanged acquire controller and SBPL policy. The private command manifest preserves full literal argv/cwd/stdin/environment; the table below is a readable command-family summary, not an alternative invocation.

| Command | Outer result | Observation |
| --- | --- | --- |
| helper PLAN PLAN_SHA preflight | exit 0 | check_pass=true for the exact corrected plan; no runtime-injected-key value was reported or inferred |
| pinned Git --no-optional-locks -c core.fsmonitor=false rev-parse HEAD | exit 0 | stdout exactly matches base `238514686078ce1564010a7b69013f48a635c57c` |
| pinned Git --no-optional-locks -c core.fsmonitor=false diff HEAD --binary | exit 0 | stdout exactly matches prepared tracked diff SHA-256 `12238ddc334c4a6971d657249732a73d59cc4c3e32b6463d5a7fccfc867a6b04` |
| controller INPUT INPUT_SHA acquire base | exit 2 | child exit -6 (SIGABRT), controller elapsed 0.236 seconds; acquisition non-pass |

Index bytes, size, mtime_ns, ctime_ns, inode and mode were equal before/after the two Git queries, and index.lock was absent at both observations. Index SHA-256 was `6e14ab18b7e159e137b8ea5d14882180ac2e50756f9e7ceb28eef2de90799533`. This supports preservation for these actual queries; it is not a proof of every CLT Git stat-refresh scenario.

The controller recorded execution_pass=false, natural_completion=false, group_absent=true and inputs_unchanged_or_acquired_exact=false. Its reason identifies absent OLD during the post-check (`input-drift-or-incomplete-acquisition`); this is incomplete acquisition, not evidence that SOURCE changed. Parent inputs/result SHA-256 are `609da1e0f9fde352bb0db722707b9fb430baad0d663bf43a6abe91a48f49e897` / `2a89db34f80098bede84037a9ca19a7e138b0bc580fd734e8b0c6dc5067e062b`. Child stdout.log is zero bytes. OLD and even acquisition's git-metadata directory were never created. Only the controller lock/sentinel, parent inputs/result, empty stdout and initial work/home/tmp/xdg directories exist. No after-acquire helper, canary, collection, binding or smoke was launched after this failure.

A PID-matched OS crash report for child 48946 (parent 48945), captured at 2026-10-09 23:35:49 KST, reports EXC_CRASH/SIGABRT with termination namespace `<0x23>`, code 2. The triggered stack is in dyld: `__abort_with_payload`, `abort_with_reason`, `ignition_halt`, `boot_boot`, `ignite`, `dyld4::CacheFinder`, then startup. Only the Python launcher and dyld are listed as loaded named images. This is direct evidence of a loader-stage failure before the reviewed Python acquisition body, not a reproduced product or test failure. A narrowly timed PID query confirmed policy compilation/application immediately before the crash; it did not identify a specific denied operation. A provenance-sandbox log is context, not proof of its causal role. Absence of a denial line is not proof of policy sufficiency. The precise host/policy mechanism is unresolved.

Read-only post-failure checks independently confirmed all 101 source files' bytes/modes, all 11 pinned control inputs and runtime/Git/config identities unchanged. The child process group was absent again at inspection. The failure was natural neither at the child nor successful at the controller; no evidence is promoted to PASS. One of four execution roots is consumed and preserved; three preauthorized correction roots remain absent. Zero runtime correction/revalidation cycles have occurred, so the same-cause three-failure limit is not reached or reset.

Retain the failed root and exact execution inputs. A separate durable private failure copy holds parent inputs/result, empty log and the PID-matched original OS crash report plus a de-identified diagnostic extract. The named consumer is resolution/review of this unresolved loader failure and the Owner's next bounded diagnostic decision; retain until that consumer accepts equivalent custody. Only the sanitized extract may enter review packets or source records; personal OS report metadata is not public evidence. Source and private task-record copies remain preserved for continuation.

Do not change SBPL permissions, runtime identity, execution topology, child environment or attempt slots speculatively. First review the actual failure evidence and distinguish an in-scope concrete correction from a new diagnostic/permission boundary. A new minimal sandbox reproduction command or policy grant is not in the fixed four-controller command family and needs an explicit bounded extension if required. No uncorrected repeat, whole-suite test, product edit, Owner acceptance or lifecycle/Git action is performed.


### Review Call 5 — Actual Failure And Scope Stop Confirmed

Fresh Claude Opus 5.5 (`claude-opus-5-5`), session `f51c6035-1a81-4e64-a4cd-b3b87b74e65e`, completed this static failure-evidence review in 73.36 seconds, exit 0, no timeout/error, empty tools/MCP and the existing claude.ai/firstParty/pro path. Packet identity: 50,913 bytes, SHA-256 `ac9fe984835be3adcabc3ca47c46dcac9a38c574b2f702bbe1b760acef3b3cf9`. Inputs were unchanged before/after. Complete relevant controller/common/acquire and two-policy source, parent evidence and sanitized crash fields were supplied; original private OS metadata and product/test bodies were not transmitted.

#### Reviewer Response Verbatim

````text
# 리뷰 5/8 — 실제 acquire 실패 증거와 다음 경계 (정적 검토, 실행 없음)

**결론: 증거는 acquisition NON-PASS와 loader 단계 실패까지만 지지하며, 기존 경계 안에서 근거 있는 교정은 없습니다. 따라서 다음 root 실행은 차단이고, Owner의 bounded 진단 범위 결정이 필요합니다.**

## (1) 증거가 지지하는 범위

**확립된 것**
- **acquisition NON-PASS:** child가 -6으로 끝났고 OLD와 git-metadata가 없으며 stdout이 0바이트입니다.
- **loader 단계 중단:** 로드된 이미지가 python3.14와 dyld뿐이고, 스택이 `start → ProcessConfig → DyldCache → CacheFinder → ignition_halt`입니다. `acquire.py` 본문과 git 호출은 실행되지 않았습니다.
- **SBPL 적용 후 exec:** `sandbox-exec` 자체는 기동해 프로필을 적용한 뒤 runtime으로 exec했습니다. 충돌 보고서가 그 PID를 python3.14로 식별합니다.
- **보존의 내부 방증:** controller 사후 검사에서 `config()`가 `verify_old()`보다 먼저 호출됩니다. reason이 `verify_old`의 `lstat` ENOENT이므로, controller 자신의 재검증(controls, 도구, SOURCE 101개)이 통과한 뒤 OLD 부재에서 멈춘 것입니다. Driver의 독립 확인과 일치합니다.
- **같은 바이너리의 샌드박스 밖 기동:** controller가 같은 runtime(SHA 검증)으로 직전에 정상 기동했습니다. 차이는 SBPL, child env, 세션에 있지만, 그중 무엇이 원인인지는 확립되지 않습니다.

**과장 또는 정정할 점 (모두 비차단, 기록 수정)**
- **"child -6 in 0.236s":** 0.236초는 controller 전체 경과이며 child 수명이 아닙니다. Driver 본문 표기가 맞고, dispatch 요약만 부정확합니다.
- **`tool_wall_seconds`:** helper가 약 11µs이고, controller 외부값 0.137초가 내부값 0.236초보다 작습니다. 이 필드는 신뢰할 수 없으니 증거로 인용하지 말고 그렇게 표기해야 합니다.
- **`capture_time`:** 23:35:49는 보고서 작성 시각으로 보는 것이 안전합니다. 귀속 근거는 PID/PPID 일치입니다.
- **result의 `reason`:** 사후 검사의 부산물입니다. 1차 사실은 `exit=-6`이며, Driver 기록이 이미 그렇게 구분했습니다.
- **해시·불변 확인:** Driver 진술에 의존하며 제가 검증하지 않았습니다.

STOP 판단, 승격 금지, root 1개 소비와 3개 잔여, 교정 주기 0회는 과장이 아닙니다.

## (2) 경계 내 교정 여부

**교정 없음 → 계속 진행 중단.**
- **Python 오류 없음:** helper, controller, controls의 Python 코드에서 오류가 관측되지 않았습니다. 명령 구성과 env도 설계대로입니다.
- **가능한 교정은 모두 제외 경계:** dyld 단계 실패를 바꿀 수단은 SBPL 권한, runtime, child env/토폴로지뿐입니다. 어느 것도 제공된 증거로 특정되지 않습니다.
- **재실행 금지:** 식별된 교정이 없으므로 root 2 실행은 "무교정 반복"에 해당합니다.

**가설 (미확립, 모두 제외 경계의 승인 필요)**
- **H1:** deny-default 프로필에 이 OS의 dyld 캐시 탐색이 요구하는 동작이 빠져 있을 수 있습니다. 후보는 허용 subpath 밖의 캐시/cryptex 경로 읽기, `file-map-executable`, 특정 syscall/fsctl 계열, mach/iokit 조회입니다. 어느 것인지 가릴 근거가 없습니다.
- **H2:** 기존 provenance sandbox와의 상호작용입니다.
- **H3:** child env 또는 세션 요인입니다. 가능성은 낮아 보이나 배제할 증거가 없습니다.
- **파급:** `test.sb`가 같은 기본 절을 공유하므로 canary/smoke도 같은 영향을 받을 수 있습니다.

**없는 증거**
- PID에 매칭되는 거부(deny) 로그 라인이 없습니다.
- dyld abort payload/reason 문자열이 sanitized 추출에 없습니다.
- namespace `<0x23>`/code 2의 의미가 식별되지 않았고, 저도 확정하지 못합니다.
- 같은 정책 아래에서 다른 바이너리가 기동하는지에 대한 대조가 없습니다.

## (3) 최소 진단 slice

**Slice A — 새 실행 없음**
- **내용:** 이미 보관된 private 충돌 보고서에서 dyld abort 메시지, termination indicator/details/reasons 필드만 비식별화해 추가 추출합니다.
- **경계:** 보관 증거를 읽기만 하므로 기존 범위로 보이지만, 판단은 Driver/Owner 몫입니다.
- **완료:** 해당 필드의 유무와 내용을 기록합니다. 구체 동작이 식별되면 Slice B는 생략할 수 있습니다.

**Slice B — Owner의 bounded 확장 필요 (새 명령)**
- **위치:** 4개 root 밖의 전용 진단 scratch에서, 변경하지 않은 `acquire.sb`와 같은 고정 env로 실행합니다.
- **B1 (1회):** 같은 runtime으로 `-I -S -B -c pass`를 실행합니다. SOURCE, OBJECTS, git 접근은 없고, 해당 PID의 sandbox deny 로그를 동시에 수집합니다.
- **B2 (1회):** 같은 정책으로 시스템 바이너리(예: `/usr/bin/true`)를 실행해, 실패가 runtime 특이인지 정책 일반인지 가릅니다.
- **한도:** 총 2회이며 반복과 정책 변형은 없습니다.

**완료 기준**
- PID 매칭 deny 라인 또는 dyld 메시지로 구체 동작이 식별되면, `acquire.sb`와 `test.sb`에 대한 bounded 권한 제안서를 작성합니다. 진단은 여기서 끝나며 정책 적용은 아닙니다.
- 정책 적용은 별도 Owner 승인, control 해시 재동결, 리뷰를 거친 뒤 root 2에서 합니다.

**STOP 기준**
- 2회 뒤에도 미식별이면 미해결로 보고하고, 추가 탐색은 새 제안으로 올립니다.
- scratch 밖 쓰기, 잔존 프로세스, source/control/도구 drift가 생기면 중단합니다.
- 진단 결과는 PASS 증거가 아니며 root나 실패 한도를 소비·초기화하지 않습니다.

## 한계

source/test 본문, 전체 충돌 보고서, OS 로그 원문은 보지 않았습니다. 이 응답은 정책 변경, 권한 확장, Owner 수용을 승인하지 않습니다.
````

#### Driver Dispositions

- Actual-result conclusion: accept acquisition NON-PASS and loader-stage SIGABRT only. No product/test failure or full verification PASS is established. The controller post-check and independent source checks support preservation; missing OLD does not contradict unchanged SOURCE.
- Timing precision: accept. The 0.236-second value is controller total monotonic elapsed, not child lifetime. Private dispatch metadata's tool_wall_seconds is a transport-reported field with inconsistent precision/semantics and is not timing evidence. Only command completion/outer exit and controller-recorded duration are used here. The crash report captureTime is report metadata; PID/PPID matching and the targeted launch/crash logs establish attribution.
- Scope stop: accept. No concrete justified correction is identified within the currently fixed sequence. Do not spend another execution root on an unchanged repeat or speculate by changing permissions/runtime/environment. The relevant stop is need for a new bounded diagnostic command/scope, not exhaustion of the three-correction limit.
- H1/H2/H3: retain as unproven hypotheses only. Neither a specific SBPL permission nor provenance interaction has been reproduced as the cause. No global permission grant or runtime replacement follows from this review.
- Slice A: completed read-only after review. The retained PID-matched raw crash report has only termination namespace/flags/code; termination indicator/details/reasons are absent. Top-level asi, asiBacktraces, applicationSpecificInformation, dyldError, errorMessage and abortReason are absent, and the header has no error/reason/abort/dyld detail key. No additional causal string is available in that report. This requires no new process or policy change.
- Slice B: propose a separately authorized diagnostic extension below. The Reviewer suggestion does not execute it or authorize a policy change. The exact same policy reduces one variable but cannot itself distinguish every host/environment cause.

### Bounded Loader Diagnostic Extension — Proposal Only

Purpose: determine whether minimal runtime startup fails under the unchanged acquisition policy, and whether the same policy also prevents a pinned system no-op binary from starting. Keep it separate from acquisition/base qualification. This proposal is not execution authority.

Scope and location: use one new, initially absent non-Git diagnostic directory under the approved agent-worktree root, named `colvia-entry-loader-diagnostic-20261009`, with distinct python-start and system-start output slots. Recheck absence/ownership/active use before creation. Keep the failed acquisition root and its evidence immutable. Temporary scripts may be disposable; the diagnostic inputs/output needed for the unresolved cause must have durable custody under this bundle. No real project or source checkout is copied.

Prepare one private fixed diagnostic supervisor/manifest inside this existing bundle, plus this task record; do not edit the six source controls, acquire.sb/test.sb, product, tests, STATUS or Git. Before execution identify exact script/policy/runtime/system-binary hashes, literal argv, sandbox parameters, seven-key environment, cwd/stdin, outputs and bounded process-group supervision. The initial policy bytes are unchanged. Bind source/object/input placeholders to explicit inert diagnostic inputs where they are unnecessary to the no-op payload; record those path differences instead of claiming an identical acquisition command. The payload must not import source controls/product/tests, read source objects, create Git metadata, discover tests or access credentials/network.

Two child invocations maximum, one each: (1) pinned CPython 3.14.7 with `-I -S -B -c pass`; (2) preidentified `/usr/bin/true`. Each runs under the unchanged acquisition SBPL with predeclared parameter paths, isolated diagnostic HOME/XDG/TMP and DEVNULL input. Use the existing non-login shell/env-i launch pattern. Each child gets at most 30 seconds plus up to 10 seconds controller-owned cleanup within a 45-second supervisor ceiling; observe through the persistent tool session without killing the supervisor. Correlate only the named PID/PPID and narrow launch window in OS crash/deny logs. One no-op comparison is permitted after an ordinary crash/refusal with verified group cleanup; stop immediately instead for surviving/unknown processes, unexpected outside access/write or source/tool drift. No retry, policy variant or runtime/billing/dependency change is included.

Completion is an evidence table of both actual exits, startup/crash observations, named denial if present, cleanup and preserved inputs. A concrete denied operation or causal message may justify a minimal permission-change proposal; it never authorizes applying it. If two probes leave the cause unknown, report unresolved and stop. The two new diagnostics are separately bounded work, not acquisition corrections or extra hidden base attempts; they do not reset existing review/execution counts. The existing three remaining review slots and three unused base correction roots retain their original limits. Any later SBPL permission change needs its own exact Owner scope decision, reviewed input freeze and a full corrected base attempt.

### Bundle Stop State And Preservation

The approved execution bundle reached its scope boundary after one failed acquisition attempt. Helper preflight and two identity checks passed; acquisition failed before its Python body. Canary, collection, binding and smoke remain unexecuted, and no seed-test count or pass rate exists. Both earlier private-helper/Git-query corrections passed bounded static review. Total review dispatches are 5/8 (three completed technical responses, one timeout and one subscription-limit error); actual base attempts are 1/4; runtime correction cycles are zero.

The failed execution root, exact attempt inputs, essential controller/crash evidence and current task copy remain durably retained for this named unresolved-failure/diagnostic consumer. No agent/process remains in the failed child group. The source worktree is retained for the concrete diagnostic/verification continuation and pending Owner disposition; it is not disposable. No Work Done, STATUS, commit, push, PR, merge, deployment or adopter application occurred. No adopter update is currently needed for private verification-helper/command changes; installed project behavior was not evaluated.

At this stop, propose only the bounded loader diagnostic extension. Final Owner result acceptance, Work Done/STATUS and Git/publication decisions should wait for a qualified result or an explicit rescope/abandonment decision; no completion acceptance is requested for the failed base run.


## Bounded Loader Diagnostic Extension Authorization — 2026-10-10

After the Driver reported the actual acquisition failure and proposed two minimal startup diagnostics under the unchanged isolation policy, the Owner replied “승인”. This authorizes the preceding Bounded Loader Diagnostic Extension: private fixed supervisor/manifest preparation and review, then at most one pinned Python `-I -S -B -c pass` and one pinned system no-op command, followed by evidence review and Driver dispositions. The historically named diagnostic directory remains `colvia-entry-loader-diagnostic-20261009`; its suffix is an identifier, not a claim about today's execution date. It is absent and not a registered Git worktree at this checkpoint.

Keep the acquisition/test policy bytes and all source controls/product/tests unchanged. Use only the named diagnostic directory and bundle inputs/records, inert parameter targets, fixed environment and supervisor bounds proposed above. An ordinary child crash/refusal with verified cleanup may be followed by the one comparison probe; unsafe or unavailable supervision/preservation stops it. No third payload, repeat, policy variant, new dependency, billing/provider path, permission change or base retry is authorized. Three remaining existing review slots and three unused base correction roots are preserved as separate limits. A diagnostic result is not base qualification, Owner acceptance, Work Done/STATUS, Git or adopter permission.

The existing explicit authorization for bounded private verification code/specifications/de-identified evidence transmission to the external Claude Pro service applies to this named diagnostic continuation. Check identities/disclosure/authentication per review. Record actual results and conclude the two-probe slice or its stop state without another per-step approval inside this scope.


### Diagnostic Inputs Prepared For Review

Prepared one private standard-library-only supervisor and a fixed two-command manifest. No diagnostic child has launched and the diagnostic root remains absent. The supervisor uses exclusive creation, one consumed slot per command, the original seven-key parent environment, DEVNULL, isolated child HOME/XDG/TMP, and the unchanged acquisition policy with inert parameter targets. Negative child exits are observations, not qualification. A comparison is permitted only after normal controller completion with verified group absence, unchanged protected inputs and no unexpected diagnostic writes. Timeouts, cleanup uncertainty or preservation failures stop continuation.

Static AST parsing succeeded; the supervisor has one Popen call site and exactly two allowlisted modes. This is not executed-test evidence. The manifest pins 125 files, including the existing 101 source files and 11 controls, plus the failed acquisition tree and three unused base roots. Parent preservation checks do not claim whole-host monitoring. OS/runtime files outside the pinned inputs remain trusted; filesystem calls are not independently preemptible.

- diagnose-loader.py: SHA-256 `a10885e93959de2b2deb265508f76bdef75eef254e4deabe55424eeb01e58756`.
- manifest.json: SHA-256 `4cc65133ebe38ba7b0c8af107fbec3e3e67880dc90de0cb5dab43204589d56f5`.
- commands.json: SHA-256 `93d9882b90e8125f911fe01001898b7bc2239662db1a04d817867ed415bc8ec7`.

Exact private inputs and essential diagnostic failure outputs are retained for the unresolved loader investigation and Owner disposition, until resolved or explicitly abandoned. Task records preserve scope, minimal evidence and verbatim reviews; duplicate raw review envelopes are not permanent deliverables.


### Review Call 6 — Diagnostic Preparation

Fresh Claude Opus 5.5 (`claude-opus-5-5`), session `c1d0cc13-d878-4aa1-8b4b-8e361f5f8073`, static/no-tools review, 100.16 seconds, exit 0, no timeout/error, existing claude.ai/firstParty/pro authentication. Packet: 61,896 bytes, SHA-256 `dcef1c9dc9548da1dd8dcf9dec5e9eab5386da379f5604812aa921c75019911a`. Inputs unchanged before/after. Source/product bodies and raw OS metadata were not sent.

#### Reviewer Response Verbatim

````text
**판정: 조건부 PASS** — 제공된 텍스트 기준으로 로직상 차단 결함은 없으나, 아래 경로명 불일치 1건은 실행 전 Driver 확인이 필요하며 원본에서도 사실이면 차단 사유입니다.

정적 검토만 했고, 실행·도구 사용은 없습니다. 제공본은 비식별화된 텍스트라 원본 SHA-256과의 일치는 제가 확인할 수 없습니다.

## 확인 필요 (원본에서도 사실이면 차단)

- **관찰:** 승인 범위의 진단 디렉터리명은 `colvia-entry-loader-diagnostic-20261009`입니다. 그런데 제공된 manifest의 `root`, 모든 `-D` 파라미터, 자식 cwd/HOME/TMP/XDG는 접미사 없는 `.../colvia-entry-loader-diagnostic`입니다.
- **추론:** 비식별화 과정에서 접미사가 빠졌을 수 있으나, 제공본만으로는 판별할 수 없습니다.
- **최소 조치:** Driver가 원본 manifest(sha `4cc65133…`)의 `root` basename을 승인된 이름과 대조합니다.
  - 일치하면 비식별화 차이로 기록하고 진행합니다.
  - 불일치하면 실행하지 않습니다. manifest 경로 문자열만 정정하고, manifest 해시와 commands.json의 해시 인자를 재동결한 뒤 Owner/Driver 절차를 따릅니다. supervisor와 정책 변경은 필요 없습니다.

## 관찰된 근거 (코드/manifest에서 직접 확인)

- **자식 수와 재실행 방지:** `Popen` 호출 지점은 1곳이고 모드는 2개 allowlist입니다. `root.mkdir`, 슬롯 `mkdir`, `open('xb')`가 모두 배타 생성이라 같은 슬롯 재실행은 `FileExistsError`로 멈춥니다. 세 번째 페이로드 경로는 없습니다.
- **mkdir 이전 실패는 슬롯 미소모:** 인자, manifest 해시, cwd, 런타임 플래그, 환경, `verify()` 실패는 모두 디렉터리 생성 전에 종료(exit 2)합니다.
- **정책 불변과 파라미터:** acquire.sb(`638bf3ee…`)가 `protected_files`에 고정되어 실행 전후로 검증됩니다. 정책이 참조하는 8개 파라미터가 모두 `-D`로 제공되고, `LOG`는 부모가 미리 연 `stdout.log`와 일치합니다.
- **페이로드:** argv는 `-I -S -B -c pass`와 `/usr/bin/true`뿐입니다. 소스 import나 객체 읽기, Git, 네트워크 경로는 없고 SOURCE/OLD/CONTROLS/OBJECTS는 빈 inert 디렉터리입니다.
- **음수 종료 처리:** SIGABRT(-6) 같은 종료도 `natural=True`로 기록되며, 그룹 부재와 보존 검증이 통과해야만 `diagnostic_observation_complete=True`가 됩니다.
- **비교 프로브 게이트:** system-start는 다음을 모두 요구합니다.
  - 선행 `result.json`의 완료 플래그와 manifest 해시 일치
  - 선행 입력·stdout 해시, work/inert 트리 불변
  - 선행 자식 그룹 부재
  - root 구성원이 정확히 `inert`, `python-start`
- **정리와 시간 한도:** 타임아웃이나 예외 시 `killpg(SIGKILL)` 후 최대 10초(전체 44초 이내) 대기합니다. 그룹 부재가 확인되지 않거나 `PermissionError`가 나면 미완료로 기록되어 비교가 막힙니다. 설정 5초 + 자식 30초 + 정리 10초가 45초 한도 안에 들어갑니다.
- **보존 검증:** 실행 후 `verify(m)`을 다시 돌려 다음을 확인하고, 하나라도 어긋나면 미완료 처리합니다.
  - 고정 파일 전체(소스 101개·컨트롤 11개 포함), 실패 루트 트리, 미사용 루트 3개 부재
  - inert/work 트리 불변, 슬롯 구성원이 정확히 `work`, `inputs.json`, `stdout.log`
- **상관 정보:** `child_pid`, `parent_pid`, `launch_epoch`, `observation_end_epoch`가 stdout과 `result.json`에 남습니다.

## 추론 (실행으로 검증되지 않음)

- `sandbox-exec`와 프레임워크 Python 스텁이 같은 PID로 exec한다고 가정하면, 기록된 `child_pid`가 크래시/거부 로그의 PID와 같습니다.
- 다음 항목은 실제 호스트 상태에 달려 있습니다. 어긋나면 mkdir 이전에 fail-closed로 멈추므로 안전성 문제는 아닙니다.
  - `sys.executable`이 manifest의 Cellar 경로와 일치하는지
  - 부모 환경에 `__CF_USER_TEXT_ENCODING` 외 주입(예: 런처 변수)이 없는지
  - `/usr/bin/true` 등의 `st_nlink == 1`과 상위 경로에 심볼릭 링크가 없는지
- 두 no-op 페이로드가 work/home/tmp/xdg에 쓰지 않을 것으로 예상합니다. 쓰기가 생기면 "unexpected diagnostic write"로 중단되며, 이는 승인된 중단 조건과 같습니다.

## 비차단 메모 (Driver 판단 사항)

- supervisor는 python-start가 exit 0으로 끝나도 system-start를 허용합니다. 승인 문구의 "ordinary crash/refusal 후 비교"에 이 경우가 포함되는지는 Driver/Owner가 판단할 사항입니다. 코드 변경은 필요 없습니다.
- commands.json 해시는 supervisor가 검증하지 않습니다. Driver가 실행 직전 `tool_cmd`를 동결본과 대조하면 충분합니다.

이 검토는 Owner 결정이나 실행 권한을 대체하지 않습니다.
````

#### Driver Dispositions And Bounded Correction

- Directory condition: accept the required check and discharge it. The original manifest root is exactly `colvia-entry-loader-diagnostic-20261009`, as approved; only the review path substitution removed the date suffix. No actual root/parameter correction is needed. Preserve this basename in subsequent redaction to prevent ambiguity.
- Static safety findings: accept only as static inference. Negative child status remains visible and never means base qualification; actual results are still required.
- Success-case comparison: clarify that the two-command diagnostic explicitly compares Python and system startup; either a success or ordinary crash/refusal allows the second command only after the same cleanup/preservation gates. This does not add a child or repeat.
- Dispatch binding: accept. The Driver must verify commands.json and the manifest argument against the reviewed hashes immediately before each dispatch; supervisor self-hash and manifest SHA guard its own inputs.
- Driver-found environment defect: revise before execution. The original regex rejected the `x` in later `0x` components of a standard OS-injected CF value. The corrected restricted character set matches the already reviewed base helper behavior (starts with 0x; hex/x/colon only). An in-process expression check accepts `0x1F5:0x0:0x0` and rejects a slash-containing value. This did not execute the supervisor or a diagnostic payload and is not host startup evidence. The seven dispatched environment entries are unchanged.
- Driver-found timing edge: revise before execution. Add an explicit child observation <=30-second check after poll completion, so delayed observation cannot report a complete result beyond that bound. No timeout budget increases.

Only these two supervisor checks and dependent hashes changed. Manifest root, child argv/environment, policy and protected source/control bytes are unchanged. No diagnostic root or child exists yet; request the bounded delta review within the remaining two calls.

- Current diagnose-loader.py: SHA-256 `0d4bdd2356215d48f9b20bb1d568344e966ab498dad79091b85ac917b70b2e77`.
- Current manifest.json: SHA-256 `4833218b3a38dceee9d9bd857b901e28ca0d8e8ddfe13832b690114eed5ed44e`.
- Current commands.json: SHA-256 `df2e6b38d67c28e24cf15e134fc8ea23dc4709afb88ae3db7559987e49d0b023`.


### Review Call 7 — Diagnostic Delta PASS (Static)

Fresh Claude Opus 5.5 (`claude-opus-5-5`), session `e4151df1-b54c-46a8-b660-d3d752527220`, 65.36 seconds, exit 0, no timeout/error, empty tools/MCP, unchanged claude.ai/firstParty/pro path. Packet 70,684 bytes, SHA-256 `b564f1d60ea11eee599414a878b6f66db5567788796810659e727c5ee9b7da74`; inputs unchanged before/after.

#### Reviewer Response Verbatim

````text
**판정: PASS** — 이번 델타 두 건과 현재 전체 소스에서 실행을 막을 차단 결함은 찾지 못했습니다.

정적 검토만 했고 실행·도구 사용은 없습니다. 제공본이 원본 SHA-256과 일치하는지는 제가 확인할 수 없으며, 아래 "관찰"은 모두 제공된 텍스트에서 읽은 것입니다.

## 델타 2건 (관찰)

- **CF 정규식 `0x[0-9A-Fa-fx:]+`:** `0x1F5:0x0:0x0` 형태를 허용하고 슬래시·공백 등은 거부합니다. `0xx::` 같은 값도 통과할 만큼 느슨하지만, 이 값은 pop된 뒤 `parent_cf_injected` 불리언으로만 기록됩니다. 자식 환경은 manifest의 고정 7키라서 자식에게 전달되지 않습니다.
- **`child_elapsed <= 30` 검사:** poll 완료 직후 `natural = True` 이전에 평가됩니다. 초과하면 `reason`이 설정되어 미완료(exit 2)가 되고, system-start 게이트가 막힙니다. 이 경로에서도 `finally`의 그룹 부재 확인은 정상 동작하며, 시간 예산은 늘지 않았습니다.

## 해시 결속과 범위 (관찰)

- **해시 결속:** commands.json의 두 모드 인자 `4833218b…`가 manifest 해시와 같고, manifest의 `protected_files`에 있는 supervisor 해시 `0d4bdd23…`가 현재 supervisor 해시와 같습니다.
- **승인 범위 일치:** `root`와 모든 `-D`·cwd·HOME·TMP·XDG 경로가 `colvia-entry-loader-diagnostic-20261009`입니다. acquire.sb는 `638bf3ee…`로 고정되어 있고, 정책의 8개 파라미터가 모두 제공됩니다.
- **변경 없는 부분:** 자식 argv와 7키 환경, Popen 1곳, 배타 생성(`mkdir`, `open('xb')`), 비교 게이트, 정리·보존 검증은 R06에서 본 로직과 같습니다. 세 번째 페이로드나 재실행 경로는 없습니다.

## 추론 (실행으로 검증되지 않음)

- **dyld 단계 SIGABRT 재현 시:** `returncode = -6`으로 poll에 잡히고, 회수된 뒤 `killpg(pid, 0)`이 ESRCH를 내어 완료로 기록될 것으로 봅니다. 이는 sandbox-exec와 프레임워크 스텁이 같은 PID로 exec한다는 가정에 달려 있습니다.
- **호스트 상태 의존 항목:** `sys.executable` 일치, 추가 환경 주입 없음, `st_nlink == 1`, `.DS_Store`나 `__pycache__` 부재가 어긋나면 중단됩니다. 대부분 `root.mkdir` 이전이라 슬롯이 소모되지 않습니다.

## 비차단 메모 (코드 변경 불필요)

- **macOS EPERM:** 미회수 좀비만 남은 그룹에 `killpg(…, 0)`을 하면 EPERM이 날 수 있습니다. 정상 경로는 poll 회수 뒤에 호출하므로 해당하지 않고, 예외 경로에서 나더라도 `cleanup error`로 미완료 처리됩니다.
- **PID 재사용:** system-start가 `absent_group(prior['child_pid'])`에서 우연한 PID 재사용으로 멈출 수 있습니다. 슬롯 생성 전이라 소모는 없으며, 이후 처리는 Driver/Owner 판단입니다.
- **mkdir 이후 설정 실패:** 예를 들어 5초 설정 한도를 넘기면 `result.json` 없이 슬롯이 소모되고 system-start도 막힙니다. 승인된 중단 조건과 같은 동작입니다.
- **실행 직전 대조:** R06 처분대로 Driver가 `tool_cmd`와 manifest 인자를 동결 해시와 대조해야 합니다.

이 검토는 실행 권한이나 Owner 결정을 대체하지 않습니다.
````

#### Driver Disposition

Accept static PASS for the two corrected checks and the currently bound two-command specification. Actual diagnostic execution remains separate evidence. The original exact basename and all pinned files were independently checked; the Driver will use only the current commands.json after rechecking its reviewed digest. Host-state drift, partial setup, PID ambiguity or cleanup failure stops the sequence with no retry. Proceed with the two commands under the Owner's existing diagnostic authorization; one review call remains for actual results. This is neither base qualification nor Owner result acceptance.


### Actual Two-Probe Diagnostic Result — 2026-10-10

Both approved children were executed exactly once using the reviewed commands.json (`df2e6b38…`), manifest (`4833218b…`) and supervisor (`0d4bdd23…`). Immediately before dispatch the Driver rechecked complete reviewed input digests, command serialization and the manifest argument. The initially absent diagnostic directory was not a registered worktree. Both supervisors returned exit 0 with diagnostic_observation_complete=true, which means observation/cleanup/preservation completed; both children failed, and neither result is base qualification. No further diagnostic payload was launched.

| Probe under unchanged acquire.sb | Child / parent PID | Child exit | Child observed duration | Supervisor before result write | Cleanup / preservation |
| --- | --- | --- | --- | --- | --- |
| Pinned Python 3.14.7 -I -S -B -c pass | 24649 / 24648 | -6 (SIGABRT) | 0.02456 s | 0.05030 s | group absent; protected inputs unchanged |
| Pinned /usr/bin/true | 24701 / 24700 | -6 (SIGABRT) | 0.02505 s | 0.04662 s | group absent; protected inputs unchanged |

Durations are supervisor monotonic observations, not precise OS process lifetimes; tool transport wall-time fields are not used. Cleanup checks completed in under 0.00001 seconds each; neither needed a kill. Each stdout.log is zero bytes and work/inert trees are unchanged. The first result, command, hashes and group absence were independently checked before the second launch; after both, all 125 pinned files (101 source, 11 controls and other inputs/tools) remained unchanged and both groups were independently absent. The supervisor also verified the complete failed-acquisition tree before/after each command and that all three unused base roots remain absent. No successful unexpected outside access/write is established; whole-host monitoring is not claimed.

Both PID/PPID-matched crash reports show EXC_CRASH/SIGABRT, termination namespace <0x23>, code 2, and the same dyld CacheFinder/ignition_halt startup stack. Named loaded images are only the respective launcher and dyld. Additional causal text fields are absent. This reproduces loader-stage failure without acquisition code and also with a system binary; it does not prove every runtime fails or identify the underlying OS mechanism.

A read-only OS-log query (exit 0, timeout 30 seconds) covered 2026-10-10 07:44:56 through 07:45:18 KST and only the two process identifiers/message PID strings. The exact argv is retained privately. It returned 27 rows; six policy compile/apply/deny rows were retained in the sanitized extract, excluding unrelated crash-service/account/provenance metadata. New direct evidence is:

```text
2026-10-10 07:44:58.907826+0900 Sandbox: python3.14(24649) deny(1) file-read-data /
2026-10-10 07:45:13.489302+0900 Sandbox: true(24701) deny(1) file-read-data /
```

These named root-directory read denials are correlated with both crashes. They identify an exact denied operation and a bounded candidate correction, not a demonstrated causal repair. The first acquisition's earlier log query still did not identify a denial; do not retroactively claim it did.

Exact parent inputs/results and original PID-matched crash reports have a durable private failure copy; only sanitized crash fields and the six selected log rows are eligible for external review. Retention consumer: unresolved loader diagnosis and Owner disposition, until resolved or explicitly abandoned. Source worktree and consumed diagnostic/base roots remain retained for that concrete continuation; no checkout is currently disposable.

### Exact Permission-Change Candidate — Proposal Only, Not Applied

A minimal candidate is one literal root-directory read grant in acquire.sb:

```scheme
(allow file-read-data (literal "/"))
```

This expands acquisition from no ancestor listing to permission to read/list the root directory itself. It exposes root entry names; it does not add a recursive subpath allowance for descendant file contents. Existing trusted OS/runtime reads remain separately allowed. The actual syscall that triggered the logged operation and sufficiency of this grant are unproven; do not claim a guaranteed fix or use a broad file-read*/subpath-root allowance. The acquisition policy's no-ancestor-listing comment and README acquisition paragraph would need the exact corresponding qualification if approved.

Inspection also corrects the earlier hypothesis that test.sb necessarily needs the same change: test.sb already grants file-read-data on nine literal ancestors, and controller.test_ancestor_parameters binds ANCESTOR_8 to /. Therefore no new test-policy permission is presently justified; test startup has not been executed and is not a pass. The proposed policy change is limited to acquire.sb. Keep all six Python control files (acquire.py, canary.py, common.py, controller.py, observer.py and runner.py), test.sb, product and tests unchanged. Re-freeze the changed acquire.sb digest in the private invocation controls map and every dependent private plan/helper binding/command/input snapshot for the new root; update only the corresponding acquisition comment and README explanation. Baseline source fixtures, selection and runtime identities remain unchanged.

Proposed next bounded slice (requires a new Owner decision): apply only the one acquisition grant and matching explanatory text, update dependent frozen hashes/private invocation/plan/commands for the next absent `colvia-entry-verification-20261009-r01` root, obtain technical delta review, then run one full corrected base sequence (acquire, canary, collect, bind, smoke) using existing selection and budgets. Preserve both consumed roots and exact earlier inputs. Stop on the first failure/unavailable/drift/cleanup problem; no second corrected root, extra no-op or further permission grant follows automatically. A failure after this change does not itself justify broadening access.

The current final-result review is call 8/8. A resumption proposal therefore also needs an explicit addition of at most three same-Claude-Pro static review calls, each <=600 seconds (delta review, at most one in-scope revision review, actual-result review), making the lifetime ceiling 11 instead of resetting 8. Existing source-data disclosure authorization and no-tools/provider-fallback limits carry forward only if that extension is approved. This proposal does not consume another base root now. Final Owner acceptance, Work Done/STATUS, Git/publication and adopter actions remain excluded.

- python-start result SHA-256 `f53772b3e42cb223eed6eaa83c18ff72ee4de6b70e3de09b4fc32f6f51ebfbfb`; sanitized crash SHA-256 `66f57d55a01b23bd9a94b805a4df10f8e1c0fabe5b0f9488ea9166fe25a4db61`.
- system-start result SHA-256 `5d970db961f770a85f86c0bd180538090c7af0d9bd801a566fa761e1762351cc`; sanitized crash SHA-256 `d02045567813fa5b866024d029488eca1e7cb14291da5205b2acca5747721f59`.
- Sanitized six-row OS log extract SHA-256 `4878aa0f242f4c4e8e7a1520ed61c1cb6907c643a2b4c52e59df4d5454da50dc`.


### Review Call 8 — Actual Diagnostic Evidence And Unapplied Proposal

Fresh Claude Opus 5.5 (`claude-opus-5-5`), session `535e3deb-601d-4de5-bd54-7d8d406d070f`, static/no-tools review, 64.03 seconds, exit 0, no timeout/error, unchanged claude.ai/firstParty/pro path. Packet 66,255 bytes, SHA-256 `85fb71cd9240a00dc6d44680c448a5d0e32b56fe957508cb0da08c5fe0b9e9dd`. All reviewed inputs remained unchanged before/after. Current overall review allowance is now 8/8 consumed.

#### Reviewer Response Verbatim

````text
**판정: PASS (현재 범위의 증거·제안 검토 한정) — 차단 사항 없음, 기록 정정 3건 필요**

이 판정은 정책 변경, 실행, base 자격, Owner 결정을 승인하거나 대체하지 않습니다. 모든 해시·보존·종료코드 확인은 Driver 주장이며, 저는 패킷 내 정적 일관성만 대조했습니다.

**기록 정정 필요**
1. **루트 이름 불일치 (Owner 패킷 전에 반드시 정정).** 제안서의 다음 루트는 `colvia-entry-verification-20261009-r01`인데, manifest `unused_base_roots`는 `colvia-entry-verification-r01/r02/r03`입니다. supervisor가 부재를 확인한 것은 후자뿐이므로, 제안된 이름의 부재는 이 패킷에서 근거가 없습니다. 오기인지 별도 네 번째 루트인지 밝혀야 합니다.
2. **"six source controls unchanged" 표현.** acquire.sb 자체가 컨트롤이고 해시가 `c["controls"]`에 묶여 있습니다. "acquire.sb 외 나머지 불변"으로 쓰고, 재동결 대상을 열거해야 합니다.
3. **단일 deny 행의 한계 명시.** dyld는 첫 실패에서 abort했으므로 그 뒤의 거부는 가려졌을 수 있습니다. 제외된 21행에 다른 deny가 없다는 것도 Driver 주장입니다. "유일한 거부"로 읽히지 않게 적어야 합니다.

**관찰 (패킷에서 직접 대조됨)**
- PID/PPID(24649/24648, 24701/24700)가 summary, result, inputs, crash, OS log에서 일치합니다.
- `launch_epoch`는 07:44:58.898 및 07:45:13.481 KST로 환산됩니다. 각각 약 10ms, 9ms 뒤에 sandbox apply와 deny 행이 이어지고, 순서가 맞습니다.
- result의 `inputs_sha256`은 두 inputs.json 헤더와 일치하고, stdout 해시는 빈 파일 해시이며, inert 파일 크기 20바이트도 코드와 맞습니다.
- 두 crash 모두 EXC_CRASH/SIGABRT이고 같은 dyld `CacheFinder`→`ignition_halt` 스택이며, 이미지는 런처와 dyld뿐입니다.
- `reason=null`이고 `natural_completion=true`이므로 코드 경로상 kill 분기에 들어가지 않았습니다. "kill 불필요"는 이로써 지지됩니다.
- supervisor exit 0은 관찰·정리·보존 완료만 뜻하며, 결과에 `base_qualification=false`가 고정되어 있습니다.
- `test_ancestor_parameters`는 조상 9개와 마지막이 `/`임을 강제하므로 `ANCESTOR_8=/`는 코드로 확인됩니다.

**추론 (타당하나 미입증)**
- 루트 읽기 거부가 abort의 원인이라는 것은 시간·PID·스택의 강한 상관일 뿐입니다. Driver의 "상관이지 입증된 수정 아님" 표현이 적정합니다.
- 최초 acquisition 실패가 같은 원인이라는 것도 추론입니다. 소급 주장을 금지한 Driver 기록이 맞습니다.
- `(allow file-read-data (literal "/"))`가 루트 항목 이름 나열만 허용하고 하위 내용은 열지 않는다는 것은 SBPL 의미상 타당합니다. 이름 열거가 새 노출입니다.

**미지**
- 실제로 거부된 syscall과 `<0x23>` code 2의 의미.
- 이 grant로 충분한지, 그리고 그 뒤에 다른 거부가 나오는지.
- test.sb 아래에서 실제로 기동되는지(미실행).
- 생략된 product/test/README/canary가 acquire.sb의 "no ancestor" 문구나 해시에 의존하는지. 승인된다면 delta 리뷰에서 확인할 항목입니다.
- 제안 순서의 "bind"는 controller 모드가 아니어서 Driver 측 절차로 보이나, 본문이 생략되어 확인하지 못했습니다.
- 전체 호스트 차원의 외부 영향.

**제안의 경계성**
제안 범위는 충분히 한정되어 있습니다: literal 1줄과 대응 문구, test.sb 불변, 1회 r01 시도, 첫 실패 시 중단, 자동 확대 없음, 리뷰 +3으로 상한 11(리셋 아님). 과대 주장은 발견하지 못했습니다. 위 정정을 기록에 반영한 뒤 현 범위를 종료하는 것이 맞습니다.
````

#### Driver Dispositions

1. Root identity: accept the required clarification; the perceived mismatch is again only review path redaction. In the actual reviewed manifest, unused_base_roots are exactly `colvia-entry-verification-20261009-r01`, `colvia-entry-verification-20261009-r02`, `colvia-entry-verification-20261009-r03`. All three were independently absent immediately before this record. No fourth/new base root is proposed. The original verification-root substitution removed its date substring within the suffixed names; subsequent packets must preserve all named basenames or explicitly map each label. The actual supervisor checked the approved original paths, not the de-identified strings.
2. Control terminology: accept and revise the proposal above to name the six Python files explicitly and distinguish the proposed acquire.sb change. A new candidate must update the acquire.sb hash in the controls map and dependent private invocation/plan/helper binding/commands/review snapshot, plus the narrow README/comment explanation. No product, test.sb or other source-control change is presently proposed. Inspect consumers during approved preparation rather than silently broadening source edits.
3. Denial limits: accept. The two retained root-directory denial rows are the observed named denials, not proof that they are the only possible denials. The Driver inspected all 27 query rows and selected all six sandbox compilation/application/denial rows. The omitted rows covered crash-service, provenance and AMFI core-dump/exception-handler context; they are not independent proof that no later denial exists. An early loader abort can mask subsequent access failures, and only a separately authorized changed-policy run could test whether this grant is sufficient.
4. Evidence conclusion: accept only within the stated scope. The two failed startup probes, PID-correlated denials, normal supervisor cleanup and preserved inputs are supported; a successful base/test result and a proven causal repair are not. The Reviewer independently assessed supplied text but did not execute checks.
5. Binding terminology: clarify. `bind` is the existing fixed private helper mode that validates actual collection evidence and exclusively creates the bound smoke invocation/summary; it is not a controller or test mode. Any proposed corrected full sequence retains that distinction and existing gate.
6. Review budget/scope: accept the current stop. No policy change, third probe, base retry or ninth review is authorized by this result. The exact acquire-only proposal and maximum three additional review calls remain pending the Owner decision described above.

### Diagnostic Slice Complete; Base Qualification Still Blocked

The approved two-probe slice is complete with actual failed-startup observations and a specific, PID-matched denied operation. Policy correction remains a proposal, not an applied or proven fix. Current counts: two of two diagnostics used; one of four base roots consumed; zero runtime correction cycles; eight of eight review dispatches consumed. Product tests, canary, collection, binding and smoke still have no executed result.

Independent final inspection reconfirmed the failed acquisition tree exactly unchanged, only the two approved diagnostic slots plus inert inputs present, unchanged diagnostic work/inert trees, absent child process groups and byte-identical durable copies of both parent inputs/results/logs. Required original crash reports and sanitized extracts remain privately retained for unresolved-failure investigation and Owner disposition. The source worktree and both consumed execution directories are retained because that concrete near-term continuation is unresolved; no eligible checkout is retired here.

Preserve this task and its durable private copy. After confirming the verbatim reviews are in both, remove only duplicated r06-r08 API envelopes, stderr and separate review.md copies; retain their authorization/metadata and identified packets/snapshots while the unresolved review/permission decision needs them. No source/adopter policy change, Work Done, STATUS, commit, push, PR, merge or deployment occurred.


## Acquisition Root-Read Correction Authorization — 2026-10-10

The Owner directly replied “승인” to the final two-diagnostic report and its concrete next-slice request: add only `(allow file-read-data (literal "/"))` to acquire.sb with matching explanation/dependent hashes; run one corrected full base sequence in `colvia-entry-verification-20261009-r01`; stop on the first failure; and add at most three same-Claude-Pro reviews, increasing the lifetime review ceiling from 8 to 11 without a reset. This is actual execution/preparation/review authority for that bounded correction, not Owner result acceptance. No per-stage approval is required inside it.

The new grant exposes root-directory entry names and has not yet been shown sufficient to repair startup. test.sb already has the root literal through ANCESTOR_8 and remains unchanged. All six Python controls, product/tests, runtime/environment/topology, selection/assertions and budgets remain unchanged. Only the narrow policy/comment/README changes, private attempt inputs/bindings and this existing record are editable. Stop before any second corrected attempt, extra probe or permission grant; this narrower scope controls over historical broader correction permissions.

The existing explicit code/specification/de-identified evidence disclosure authorization applies to these at most three fresh no-tools Claude reviews, each <=600 seconds, using only the verified claude.ai/firstParty/pro route. Review roles are delta, at most one in-scope revision review, then actual result; no unused call authorizes unrelated work. Authentication/billing change, unexplained input drift or review timeout/error remains a stop.

Before mutation, all 125 diagnostic-pinned inputs were verified unchanged and r01 was absent and not a registered worktree. Preserve the exact executed pre-correction acquire.sb once in the private failed-attempt evidence for the named old/new loader-correction assessment and Owner disposition; both failed roots and the two-probe evidence stay intact. Policy and README will be frozen as new candidate inputs; earlier hashes remain historical and must not be reused as current identities. Work Done/STATUS, commits/push/PR/merge and adopter actions remain excluded.

- New immutable extension SHA-256: `7213dd2872e201ec4a5e46d4f5d4362c4375b3ea7021237e493ed34c8742e9a4`.
- Preserved executed acquire.sb SHA-256: `638bf3ee10ab06a423b38b55d9e911a0dd1e19ff7df9798e7862fe6a3d4a7780`.


### r01 Candidate Prepared; Execution Pending Delta Review

The acquisition policy now differs from the executed original by exactly one non-comment form: `(allow file-read-data (literal "/"))`. Corresponding acquisition comments and README text describe root-entry-name exposure and the narrower one-attempt authorization. Source 101-file identities, the other ten pinned controls (including test.sb and all six Python controls), runtime, selected IDs, environment construction and budgets are unchanged. A source/controls search found the relevant no-ancestor statement only in the policy/README and the controller's existing acquire-versus-test ancestor routing; no product/test edit is needed for this preparation.

New private inputs are isolated in attempt-01; previous attempt/diagnostic inputs and consumed execution roots are preserved. The unchanged helper body is copied with the same digest. Every active invocation/plan/parent expectation/dispatch now binds the new root and acquire.sb digest; shell commands round-trip to their literal argv plus DEVNULL redirection. Full source maps and the 20-ID selection remain unchanged. Preparation hit and corrected a local metadata-builder TypeError (scope is a list); no controller/helper/diagnostic child ran, and only the two newly created private input files existed at that point. Their bytes were verified before completing the builder. This is not a runtime attempt or a changed test result.

Current r01 root is still absent. The policy has not yet been compiled/applied as this candidate, and no success is inferred from static parsing or hash consistency. The exact new extension overrides old broad retry text; only this one corrected attempt and at most three additional reviews are authorized.

- private-invocation-base.json: SHA-256 `950c50c7b6d4afbe4d604413e711e99bbab497ad5ac67a33838d00a4e8f81a9e`.
- private-plan.json: SHA-256 `dc98e981fbc2e71196157e786dc9e6486243bf8479c4db40d452529015918ae4`.
- private-commands.json: SHA-256 `13a204908cea144fdaa24403859046c8dde6fbd6ce77bb600922c0de033ff094`.
- verify-base-plan.py: SHA-256 `dcc35fa2d22fb9bd485c56f3e2181ea322674b968cd92d1bd2da8250e204e4cd`.
- acquire.sb: SHA-256 `b380794c937a944c52d69910176a48e0da8f9d90bb00b781a94df77ede70e59c`.
- README.md: SHA-256 `7c4060f1abd24aa264d6f1bca983c12681e56d4716545715a594769145dbfae2`.


### Review Call 9 — r01 Permission/Input Delta PASS (Static)

Fresh Claude Opus 5.5 (`claude-opus-5-5`), session `0abdb0d0-f982-467a-ba2a-535e282c5946`, 43.85 seconds, exit 0, no timeout/error, empty tools/MCP and verified claude.ai/firstParty/pro path. Packet 163,839 bytes, SHA-256 `35c63cfa64395a930f5f66e15b81c9921a4594dfe017c3fd64bb677635132c18`. Inputs and preserved failed/diagnostic evidence were unchanged before/after. Lifetime review usage is 9/11.

#### Reviewer Response Verbatim

````text
**판정: PASS** (정적 delta 검토, 호출 9/11). 차단 사유는 없습니다. 이 판정은 추가 권한, 재시도, 소스 변경, Owner 수락을 부여하지 않습니다.

**확인한 내용**
- **정책 delta**: acquire.sb의 비주석 변경은 `(allow file-read-data (literal "/"))` 한 form뿐이고, Owner 확장 문구와 일치합니다. 나머지는 주석 2줄 추가와 "No other ancestor readdir" 수정입니다. `literal`이라 하위 경로 재귀 읽기는 추가되지 않습니다. 제공된 test.sb 본문에는 변경이 없습니다.
- **README 범위**: 날짜가 명시된 예외 문단과 경계 문단이 승인 범위(acquire 전용, 루트 항목명 노출, 수리 미입증, r01 1회, 리뷰 +3, 상한 11)와 일치합니다. 상단의 "최대 3회 수정 시도" 일반 문구는 남아 있지만, 뒤 문단과 extension이 명시적으로 좁히므로 차단 사유는 아닙니다.
- **해시 전파**: 제공된 텍스트 안에서 아래 값이 모두 일관됩니다.
  - acquire.sb `b380794c…`: invocation controls, plan controls, 네 단계 expected_parent_inputs.
  - invocation `950c50c7…`: plan initial_input, acquire/canary/collect argv, 샌드박스 child argv.
  - plan `dc98e981…`: 모든 helper dispatch.
  - helper `dcc35fa2…`: plan과 dispatch.
  - README `7c4060f1…`: plan.
- **루트와 경로**: root, old, exec, WORK, LOG, BOUNDARY, ANCESTOR_0~8, 바인딩 경로가 모두 r01과 attempt-01을 가리킵니다. 9단계 조상 체인과 `agent-worktrees` 부모 조건을 충족합니다. helper의 cwd, 경로, 7개 환경값도 dispatch와 맞습니다.
- **수집 바인딩**: 변경 없는 helper가 r01의 collect-base 증거, canonical 바이트, stdout 교차확인, `collection_sha256` 단일 필드 차이, 배타적 쓰기 2건을 그대로 강제합니다. `runs/` 구성원 일치 검사와 preflight의 r01·smoke 입력·summary 부재 검사가 있어, 이전 후보의 증거가 현재 통과로 계산될 경로는 없습니다.
- **첫 실패 중단**: controller와 helper는 비통과 시 exit 2를 내고, 각 dispatch는 `expected_exit` 0을 요구합니다. 슬롯은 배타적 `mkdir`이며 stop_rule도 extension과 일치합니다.

**증거 한계**
- 해시, 소스 101개 불변, diff의 정확성은 Driver 주장이며 제가 독립 검증하지 않았습니다.
- 경로는 비식별화된 것이라, 실제 경로의 깊이가 같다는 전제에 의존합니다.
- canary.py, observer.py, runner.py 본문과 README의 나머지 부분은 이번에 보지 못했습니다.
- plan의 `host_tools`, `inherited_runtime_files`, `positive_probe_preflight`는 발췌에 없어 검토하지 못했습니다.
- 이 grant가 충분한지, 원인이 맞는지는 미입증입니다. 첫 거부가 이후 거부를 가렸을 수 있습니다. test.sb도 아직 실행된 적이 없어, ANCESTOR_8 경로가 실제로 동작한다는 증거도 없습니다.

**실행 전 권고 (비차단, 읽기 전용 확인)**
- `positive_probe_preflight`의 INPUT 항목이 attempt-01의 `private-invocation-base.json`을 가리키는지 Driver가 확인하길 권합니다. 이전 attempt 경로가 남아 있으면 preflight는 보존된 옛 파일로 통과합니다. 그러면 새 입력의 소유자/모드 결함이 canary 단계에서야 드러나 단 한 번의 시도를 소모할 수 있습니다.
- 불일치가 발견되면 실행하지 말고, 범위 내 revision 리뷰(호출 10)로 다루어야 합니다.

실행 후에는 actual-result 리뷰가 필요합니다.
````

#### Driver Dispositions

Accept static PASS for the exact acquisition-policy and r01 input-binding delta, with all stated evidence limits. No execution result or causal repair is inferred. The nonblocking INPUT positive-probe recommendation was independently checked: the current path is attempt-01/private-invocation-base.json, a regular one-link file owned by the effective user, mode 0644 with owner-write bit. No old attempt path remains in active plan or dispatch JSON. No correction/revision review is needed.

Use only the frozen commands after rechecking their digests. Run the existing read-only helper preflight and both exact read-only Git identity queries before first acquisition; keep optional locks disabled and verify index preservation. Then continue each reviewed step only on its actual parent/helper PASS. A first failure ends this r01 attempt with preservation and actual-result review. The Owner's scope already authorizes this sequence; no new stage permission is requested.


### Actual r01 Base Sequence — All Execution Gates PASS

Executed exactly one corrected r01 candidate, using private-commands SHA-256 `13a204908cea144fdaa24403859046c8dde6fbd6ce77bb600922c0de033ff094`, plan `dc98e981fbc2e71196157e786dc9e6486243bf8479c4db40d452529015918ae4`, initial invocation `950c50c7b6d4afbe4d604413e711e99bbab497ad5ac67a33838d00a4e8f81a9e`, unchanged helper `dcc35fa2d22fb9bd485c56f3e2181ea322674b968cd92d1bd2da8250e204e4cd` and the reviewed acquisition policy `b380794c937a944c52d69910176a48e0da8f9d90bb00b781a94df77ede70e59c`. All dispatches used the fixed non-login /bin/sh, env -i, DEVNULL and pinned CPython 3.14.7 -I -S -B family. No extra no-op, second corrected root or policy edit occurred.

The read-only helper preflight passed. Both exact Git identity commands returned exit 0 and expected stdout: base HEAD and tracked diff matched the prepared identities. Optional locks stayed disabled. Index bytes/hash, size, mtime_ns, ctime_ns, inode and mode were identical before/after; index.lock was absent. The index SHA-256 remained `6e14ab18b7e159e137b8ea5d14882180ac2e50756f9e7ceb28eef2de90799533`.

| Controller stage | Outer / child exit | Controller monotonic elapsed | Group absent / inputs preserved |
| --- | --- | --- | --- |
| acquire-base | 0 / 0 | 0.653 s | true / true |
| canary-base | 0 / 0 | 0.676 s | true / true |
| collect-base | 0 / 0 | 0.459 s | true / true |
| smoke-base | 0 / 0 | 61.739 s | true / true |

Every parent execution_pass and natural_completion field is true and reason is null. All seven helper modes passed: preflight, after-acquire, after-canary, after-collect, bind, before-smoke and after-smoke. The acquisition post-check verified the acquired baseline membership/bytes/modes; canary evidence checks verified the named positive/negative probes. The corrected candidate no longer exhibits the previous startup block on this host. This is a successful bounded correction outcome, not a claim to have identified every dyld syscall or proved general policy sufficiency. The original failed attempt/diagnostics remain historical failures.

Canary named denials cover SOURCE, CONTROLS, OLD_MODE, INPUT, COMMON_GIT, SENTINEL, PARENT_INPUTS, PRIOR_RESULT, LOOPBACK_BIND and LOOPBACK_CONNECT, each with the expected refusal. Child inheritance probes passed. fullfsync executed, the pinned Git/runtime identities matched, and non-Git/primary/linked-worktree topologies and existing observer scenarios passed their helper checks. OLD_MODE proves only the named metadata-write refusal, and the policy still exposes the documented metadata/trusted prefixes and literal ancestor names. No whole-host confidentiality or real credential query is claimed.

The Driver computed 776 ordered occurrences and 599 unique IDs from the full collection file; 177 IDs appear twice. The Reviewer received the derived summary and selected rows, not that full list. The unchanged 20 selected IDs each occur once, for 20 selected occurrences. No unittest.loader synthetic IDs were present. No deduplication, discovery edit or assertion/selection change occurred; the non-selected 756 occurrences were not executed and are not qualified.

The existing helper exclusively created the smoke invocation and binding summary from the canonical collection bytes. Only collection_sha256 differs from the initial invocation. The subsequent before-smoke gate passed, then only the preauthorized digest token was substituted in the frozen smoke command. The smoke runtime's rediscovered canonical collection digest exactly matched the bound digest.

- Collection SHA-256: `a407f2fd7e3f6da93b084f5f8f5043f1c2497bc1b44d95eeed4be18ebdf6c24f`.
- Bound smoke invocation SHA-256: `38889202c19c0a92fb38f1a61c7d04889723545495589f607ff3746b363795c2`.
- Selected rows SHA-256: `67cb50aed558c9635c8a807d2487fad320fd2f04fbdf80850a62e8a56f9b7835`.
- Executed rows SHA-256: `2a8c63a340c910d1de3d2194be38e3c031e9bd75cbff5a7eb74b657137afbd77`.
- Counts SHA-256: `72755819d7475a8c593bd0d48650dcc2d7a05359647ab00b79d3ada5bf91db0d`.

Smoke ran 20/20 selected occurrences: 20 pass; failures, errors, skips, expected failures, unexpected successes, unstarted and unfinished all zero. Actual ordered executed identities match selected identities, each outcome is exactly pass, and unstarted/unfinished arrays are empty. No suite-event/identity-stop/preservation-stop/preservation-event/failure directory exists. The two process-safety cases also completed with their asserted expected child exits; no child exit is reinterpreted as a failed test merely because a case intentionally checks a nonzero refusal. Runner reports 61.429 seconds for the tests; controller reports 61.739 seconds including its overhead. Tool transport wall-time is not used as timing evidence.

The Driver performed read-only checks independently of the helper and confirmed all 101 source files and 11 candidate controls match their pinned bytes/modes as applicable, the previous failed root and diagnostic root files/members are unchanged, and all four controller child groups (33538, 33717, 33806, 33966) are absent. r02/r03 remain absent. The after-smoke helper additionally verified acquired baseline custody, all parent/input gates and exact bound collection/run accounting. No extra suite was run for reporting.

Retain r01's acquired baseline and essential parent/canary/collection/smoke evidence in its durable execution directory for the named final-result review, pending Owner acceptance and next implementation handoff. Exact candidate inputs and concise execution/evidence summaries remain in this existing private bundle; original failed/diagnostic evidence remains preserved for correction assessment. No additional source tree or blanket output archive is needed. Source worktree and consumed roots are not yet disposable while Owner disposition and that handoff remain pending.

The remaining required authorized step is actual-result technical review. This execution result is bounded P0/base PASS pending that review, not full-suite qualification, P1-P4 Colvia implementation, Owner acceptance, Work Done/STATUS or Git/adopter permission.


### Review Call 10 — Bounded P0/Base Actual-Result PASS

Fresh Claude Opus 5.5 (`claude-opus-5-5`), session `f9321be8-3282-43e1-91c9-ed3df79cb3bc`, 50.6 seconds, exit 0, no timeout/error, empty tools/MCP and verified claude.ai/firstParty/pro path. Packet 163,969 bytes, SHA-256 `1662c0b9ee19cdbdc02575b82486a1914200ff855d7fe7da626778d4c4dc0374`. All 262 protected files plus recorded root memberships stayed unchanged before/after review. Lifetime reviews: 10/11; this extension used 2/3, with no revision review needed.

#### Reviewer Response Verbatim

````text
**판정: PASS (bounded P0/base 실제 결과 기술 검토, blocker 없음)**

이 판정은 전달된 바이트의 정적 대조에만 근거합니다. 해시 재계산이나 실행은 하지 않았고, 추가 권한·재시도·소스 변경·Owner acceptance는 부여하지 않습니다.

**대조해 일치를 확인한 항목**
- **부모 증거 체인**: 네 단계 `result.json`의 `inputs_sha256`이 각 `inputs.json` 표기 해시와 일치합니다. `boundary-positive.json`의 PRIOR_RESULT, PARENT_INPUTS, INPUT, CONTROLS 해시도 해당 파일 표기 해시와 일치합니다.
- **통제 파일 동일성**: 네 단계와 binding summary의 controls 11개 해시가 모두 같습니다. `acquire.sb`는 b380…이고, 승인된 한 줄 `(allow file-read-data (literal "/"))`과 주석만 들어 있습니다. `test.sb`는 27de…로 그대로입니다.
- **정책 적용**: acquire 단계만 `acquire.sb`를 쓰고 ANCESTOR 파라미터가 없습니다. 나머지 세 단계는 `test.sb`와 9개 ancestor(마지막이 `/`)를 씁니다.
- **바인딩**: summary의 collect inputs/result 해시(b963…/79b2…)가 실제 파일과 일치합니다. smoke 명령의 INPUT 경로, 토큰 치환값 3888…, `collection_sha256` a407…이 summary와 일치합니다.
- **스모크 결과**: selected 20행과 executed 20행의 순서·ID·occurrence=1이 일치하고, 모두 `outcome=pass`, `outcomes=["pass"]`입니다. counts는 776/20/20에 나머지 0이고, unstarted/unfinished는 `[]`입니다. stdout의 START/STOP 20쌍과 "Ran 20 … OK"도 같습니다.
- **시간**: 행별 초 합계가 약 61.427초로 러너의 61.429초와 맞고, 컨트롤러 61.739초는 1200초 예산 안입니다.
- **카나리**: 부모와 child 모두 10개 named denial이 EPERM(1)입니다. primitive 이벤트는 필수 집합을 모두 포함하고, short-write는 `written:1` 뒤 종료, lock 두 종은 attempt→acquired 순서입니다. 관측 프로세스의 pgid는 33717입니다.
- **수치**: 776−599=177이 duplicate_ids 177, extra 177과 맞습니다. 선택 20개는 각 1회, synthetic loader ID는 없습니다.
- **범위 준수**: 기록상 수정 r01 1회 실행이며 r02/r03 부재, 추가 no-op·정책 편집 없음으로 Owner extension과 충돌하는 내용이 없습니다.

**증거 한계 (Reviewer가 검증하지 못한 것)**
- 다음은 Driver/helper의 주장으로만 남습니다:
  - `collection.json` 전체(776행)
  - acquire/collect/canary `stdout.log`
  - plan, private-commands, invocation 본문
  - README와 task record
  - source 101개와 controls 11개의 실바이트
  - Git index 불변
  - 그룹 부재
  - 이전 실패 root 보존
- 스모크 stdout은 전달된 사본이며, 원본 로그 해시는 제시되지 않았습니다.

**보고 정정 권고 (non-blocking)**
1. **카나리 범위 명시**: named denial은 모두 `test.sb` 아래에서 관측된 것입니다. 수정된 `acquire.sb` 아래의 런타임 거부 프로브는 없습니다. literal `/`가 "이름만 노출하고 하위 내용은 읽지 못한다"는 것은 정적 정책 해석이며 실행으로 입증된 것이 아니라고 적어야 합니다.
2. **인과 표현**: `test.sb`는 원래 `ANCESTOR_8=/`를 허용했고 acquire만 막혔다는 점은 가설과 정합합니다. 다만 근거는 단일 호스트 1회 성공뿐이므로 "이 호스트에서 시작 차단이 재현되지 않음"까지만 쓰는 현재 문구를 유지해야 합니다.
3. **`session_observed` 필드**: acquire/canary/collect는 false, smoke는 true인데 정의가 없습니다. 의미(예: 진행 폴링 관측 여부)를 적거나 판정 근거가 아님을 밝혀야 합니다.
4. **"177 IDs appear twice"**: 수치상 정합하지만 전체 목록이 전달되지 않았으므로 helper/Driver 산출임을 표기해야 합니다.
5. **"Independent read-only post-execution checks"**: helper와는 독립이지만 Driver가 수행한 것이며 Reviewer 검증이 아님을 명시해야 합니다.
6. **`credential.helper=osxkeychain`**: 시스템 Git 설정값을 관측한 것일 뿐 keychain 접근 여부를 시험한 것이 아님을 유지해야 합니다.

**자격 경계**
- 이 PASS는 selected 20건의 base 스모크와 named canary에만 해당합니다.
- 실행하지 않은 756 occurrence, full-suite, factory, P1–P4, product transition, whole-host 격리는 자격 대상이 아닙니다.
- 이전 실패 시도는 실패 이력으로 남습니다.
- Owner acceptance, Work Done/STATUS, Git/adopter 조치는 별도 Owner 결정 사항입니다.
````

#### Driver Dispositions

- Verdict: accept bounded P0/base technical PASS with no blocker. Reviewer assessment is static consistency checking of supplied evidence, distinct from the Driver's actual commands and read-only verification. Owner result acceptance remains pending.
- Canary scope: accept the qualification. All named denial probes ran under unchanged test.sb, not the corrected acquisition policy. No additional negative-access probe under acquire.sb was executed. The statement about literal / versus recursive descendant contents is a static policy interpretation, not a new runtime proof of the grant's full extent. Acquisition's runtime evidence establishes successful baseline acquisition and preservation for this candidate.
- Causality: accept and retain the narrow wording: this one corrected candidate on this host no longer reproduced the startup block. No exact dyld syscall, universal repair or hidden later permission requirement is inferred.
- session_observed: define it as whether the tool returned a persistent session_id for asynchronous polling. acquire/canary/collect completed in the initial response, while smoke returned a session and was polled. It is transport bookkeeping, not a success, timing or security criterion.
- Discovery counts: accept and explicitly attribute full-list occurrence/duplicate calculations to the Driver. The Reviewer could check supplied summary arithmetic and selected rows but not independently recompute the omitted 776-entry list.
- Independent checks: accept and clarify that these are Driver checks independent of the helper, not Reviewer executions. No additional test run follows these wording corrections.
- Git credential setting: accept the limit. credential.helper=osxkeychain is the observed system configuration string only; no keychain credential query or helper invocation was performed or qualified.
- Log identity: the actual smoke stdout SHA-256 is `6738f06e61a351359ae5ef0aaf5230615d896ae58c65288ac13144872f64f7d5`. The R10 snapshot already protected its original bytes, but its explicit hash header was omitted from the transmitted stdout section. This records the Driver's verified original identity without claiming the Reviewer recomputed it.

### Current Technical Result And Owner Boundary — 2026-10-10

The authorized acquisition-permission correction and one r01 base attempt are complete: acquire, canary, collect, helper binding and smoke passed; all seven helper gates passed; selected tests are 20/20 pass with every non-pass/incomplete counter zero; final technical review is PASS with the reporting qualifications above resolved. Only acquire.sb's one literal root-read form, matching comments/README and private input bindings changed. The six Python controls, test.sb, product/test bodies, selection and budgets are unchanged.

Overall accounting: base attempts 2/4 consumed (original acquisition failure, then r01 success); one successful runtime correction/revalidation cycle and zero failed correction cycles; diagnostics 2/2 consumed; reviews 10/11 consumed. r02/r03 remain absent and unused. The unused review allowance is not authority for unrelated work or another base attempt. Original failed/diagnostic evidence remains a failure history and is not promoted to PASS.

Qualification is limited to this exact candidate's selected 20 base test occurrences and named test-policy canaries. The 756 non-selected occurrences, full suite, entry factory, P1-P4 product transition and whole-host isolation remain unqualified. Final Owner result acceptance, Work Done/STATUS, next implementation start, source Git/publication and adopter application remain separate decisions. No such action occurred.

The source worktree, original failed root, diagnostic root and successful r01 root are retained for the concrete pending Owner result decision and next implementation handoff, including acquired baseline and required exact candidate evidence. Durable private copies preserve this task record and the unique prior-failure crash evidence; identified inputs and runtime outputs remain under the approved non-temporary roots. No eligible checkout is retired while that work is pending. After checking verbatim review preservation in this task and its durable copy, only duplicated r09/r10 API envelopes, stderr and standalone review.md copies are removed. Authorization/metadata and identified packets/snapshots remain for pending Owner disposition.


## P1 Preparation And Selected Draft Direction — 2026-10-10

### 이번 준비의 결과와 승인 범위

다음 작업은 entry-1 구현에 필요한 호출부와 검증 설계를 고정하는 것이다. r01의 base 20/20 PASS와 실제 결과 리뷰 PASS는 기존 범위의 증거로 유지한다. 아직 실행하지 않은 entry factory, 구형 writer의 실제 전환 중 거부, 전체 회귀 검증을 이 결과에 포함하지 않는다.

Owner는 D1-A/D2-A를 추천한 뒤 정책 수정 문안·호출부 목록·P1 실행 계획을 준비하겠다는 제안에 “계속하자”라고 답했다. 이를 두 추천안을 기준으로 한 이번 문서 준비 승인으로 기록한다. 아래 문안 자체의 계약 수락, base 결과의 최종 Owner 수락, 제품 구현, reviewer 호출 또는 계약 활성화로 확대하지 않는다. 앞의 D1/D2 표는 선택 전의 역사적 제안이며, 이후 준비 기준은 이 절이다. 기존 Accepted DR-0004의 바이트는 변경하지 않았다.

진행 기록은 계속 이 문서 하나가 소유한다. 이번 수정은 이 절의 추가와 상단 현재 설명만으로 제한한다. 외부 조정 문서의 STATUS, Development Index, 기존 구현 계획·리뷰, runtime/test/control 파일은 수정하지 않는다. 아래 P1a/P1b는 기존 P1의 제안된 세부 순서이며 새 Work나 독립 상태표가 아니다.

### DR-0004에 추가할 정확한 문안 후보

제목 후보: `Named Amendment: Entry Diagnostics And Fresh-Init Admission (D1-A/D2-A)`.

대상은 DR-0004의 `Rollback, Proof And Retained Meaning` 중 C0-H-A 진단 미결 부분과 `Inventory And Version Table` 및 `Source By Target By Operation`의 fresh-init 허용 조건이다. 기존 S1 경계, T-A 손상 한계, predecessor allowlist, local/worker 정책, schema 및 authority 의미는 바꾸지 않는다. 다음 인용문이 제안하는 추가 계약 문안이다. 실제 적용 시에는 원문을 지우지 않고 명시적인 amendment와 Owner 수락 범위를 기록한다.

> **D1-A — Retired-entry diagnostics.** Otherwise valid entry-1 product/binding and record observations에서 root `hv2`가 다시 나타나면 `status`, `doctor`, ordinary `view`는 기존 `classification: conflict`, exit 12를 사용한다. 검증된 binding/product를 유지하면서 `lifecycle_ready: false`와 `retired_entry_collision: {path: hv2, ownership: project, preserved: true}`를 표시하고, 해당 항목의 처리를 운영자가 별도로 결정해야 한다는 next action을 제공한다. JSON과 사람이 읽는 출력 모두 lifecycle 준비가 끝나지 않았음을 드러낸다. `view`는 새로 검증한 Work/intent/candidate 내용을 계속 보여 준다. Unknown, damaged, unsupported, pending 관측은 기존 분류·우선순위를 유지하며, collision 정보로 그 오류를 가리지 않는다.
>
> C0-H-A에 따라 lifecycle update/rollback/init replay/repair/detach는 mutation 전에 `HV2-WORKSPACE-PRODUCT`, exit 65로 거부하고 root `hv2`를 보존한다. Ordinary Work/intent/candidate 경로에는 이 lifecycle 거부를 전역 적용하지 않는다. 이 경로들은 기존 fresh proof, content, pending 및 exact-ticket 규칙을 지키며, `hv2`를 실행하거나 snapshot에서 제외하지 않는다. 검증된 `colvia`만 managed-entry 제외·보호 대상이다. 진단 필드는 관측 결과이며 영속 상태나 새 writer 권한이 아니다.
>
> **D2-A — Fresh-init admission.** Fresh entry-1 init의 대상 root에 `hv2` 파일·디렉터리·symlink 또는 그 NFC/casefold 이름 별칭이 있으면, 첫 init receipt 또는 첫 target mutation 전에 `HV2-WORKSPACE-PRODUCT`, exit 65로 거부한다. 기존 path/topology 검사와 `colvia` collision 규칙도 계속 적용한다. 해당 항목의 bytes와 종류를 보존하고, 삭제·이동·이름 변경 없이 별도의 운영자 판단이 필요함을 설명한다. 이 조건은 전환 후 재등장 정책의 소급 해석이 아닌, 첫 설치에 추가하는 명시적 admission 제한이다. 파일이 없더라도 Git index, ignore 및 topology의 기존 검사 결과를 우회하지 않는다.
>
> **Effect and limits.** 이 amendment를 Owner가 수락하더라도 entry-1 runtime 계약은 즉시 활성화되지 않는다. M3는 정확한 C2 successor 문안·hash, qualification 및 별도 Owner activation 전까지 현행 계약이다. `.hrn/`, `HV2-`, `hv2ref`, record IDs, 완료 이력, 자동 Work/Git 행동 및 기존 D1/D2 밖의 정책은 그대로 유지한다.

C2 반영 대상은 `WORKSPACE-CONTRACT`, `REFERENCE`, `GETTING-STARTED`, `OPERATIONS`, managed adapter와 관련 current CLI/view 설명이다. 이는 기존 eleven-member successor 준비 안의 세부 문안이며 지금 해당 파일을 변경하거나 successor를 활성화하지 않는다. D1의 보조 필드를 모든 무충돌 응답에 새 필수 필드로 추가하는 것은 이 문안의 요구가 아니다.

### 호출부와 테스트 대역의 처분

기준은 source base `238514686078ce1564010a7b69013f48a635c57c`이다. 아래 위치는 그 바이트를 가리킨다. AST/문자열 검사는 static inspection이며 test discovery 또는 실행 결과가 아니다. 함께 준비한 review packet에 전체 검사 대상 목록, 관련 AST 호출 위치와 원문 발췌를 넣는다. Dynamic Python 전반의 완전성을 증명하는 목록은 아니며, candidate 작성 뒤 동일한 검사를 반복하고 실제 collection과 비교해야 한다.

| 경로와 전달 경계 | P1에서 필요한 변경 / 유지 |
| --- | --- |
| `product.py:require_workspace_runtime` → WorkStore/CandidateStore | 실제 production 결과에 검증된 `inventory_id` 필수. entry-1 installed launcher/module provenance를 검사하고 현재 writer window를 entry-1로 제한. test double의 None 예외가 production fallback이 되지 않음 |
| `work.py:_snapshot_once/snapshot`, `_preflight_changed_paths/preflight_changed_paths`, `_verify_worker_sources/verify_worker_sources` | SHA와 window를 함께 전달하고 literal window→launcher map으로 제외·보호 경로 결정. 내부 wrapper까지 전달. caller가 임의 제외 경로를 넘기지 않음 |
| `work.py:_live_external_refs`, `_worker_required_refs`, `_worker_record_preflight`, `_worker_content_state`, `_apply_worker_path` | 간접 전달까지 같은 verified identity 유지. WorkStore publish/prepare/apply/recovery 및 worker 경로 전체를 확인. `.get()` 결과가 non-null SHA의 누락 window를 정상화하지 않음 |
| `intent.py:258,369,397,403` | 369/397/403의 live 호출은 verified identity 전달. 258의 bound-intent 역사 참조 검사는 명시적 SHA None/no live exclusion 유지. `WorkspaceIntentStore`가 넘기는 WorkStore runtime seam도 함께 확인 |
| `view.py:144,149,151,232` | worker proof, snapshot 두 곳과 changed-path 검사에 product의 검증된 nested inventory 전달. collision 표시와 fresh graph 검사 연결. read 경로가 writer 권한을 만들지 않음 |
| `candidates.py:240` | current writer gate는 entry-1. 실제 구형 설치로 새 candidate write가 성공하는 fallback을 추가하지 않음 |

테스트 대역은 다음과 같이 처분한다. `keep`은 해당 과거 의미를 유지한다는 뜻이며 새 production writer가 old window를 허용한다는 뜻이 아니다. `migrate`는 current fixture의 전달을 고친다. `duplicate`는 기존 assertion을 지우지 않고 entry-1/거부 사례를 추가한다.

| 위치 | 현재 window / SHA | 처분과 근거 |
| --- | --- | --- |
| `test_general_work_recovery.py:39` | 없음 / None | keep: runtime launcher proof 없는 record/recovery seam |
| `test_general_work_invariants.py:36,250,422` | 없음 / None | keep: 공유 seam·binding-change double·별도 intent seam. 250의 결과는 255/263에서 주입되므로 두 소비자 모두 목록에 포함 |
| `test_umbrella_recovery.py:142` | 없음 / None | keep: old/non-umbrella 의도적 대역. 성공 경로로 바꾸지 않음 |
| `test_candidates.py:496` | 없음 / None | keep: WorkspaceIntentStore의 record-only seam. CandidateStore writer 승인으로 해석하지 않음 |
| `test_umbrella_recovery.py:26` | umbrella-1 / None | keep + duplicate: 기존 umbrella seam assertion과 entry-1 capability 사례를 구분 |
| `test_worktree_checkout_bytes.py:18` | checkout-1 / None | keep + duplicate: checkout-1 CRLF 의미와 entry-1 상속을 각각 검증. 생산 gate를 대체하지 않음 |
| `test_candidates.py:49` | checkout-1 / None | migrate current fixture to entry-1; old checkout-1 writer 거부를 별도로 추가. 과거 실제 성공 증거는 OLD에 보존 |
| `test_worktree_execution.py:486` | 실제 product SHA non-null / window를 버리는 dict comprehension | migrate: 실제 관측의 nested inventory에서 검증된 ID를 함께 전달. 현재 두 필드 필터는 새 proof 계약에 불충분. 통제된 pending prefix 생성과 이후 installed CLI assertion은 유지 |
| `test_worktree_execution.py:164` | 상위 `self.store.runtime_check` 위임 | keep forwarding; 부모 fixture 처분을 상속. 독립적인 production 검증으로 계산하지 않음 |
| `test_human_view.py:261` | nested inventory None / None | keep: `_worker_inspection`용 synthetic 관측. WorkStore runtime double과 혼동하지 않음 |
| `test_worktree_checkout_bytes.py:207,210` | nested window / None | keep + duplicate: inspection capability 경계. entry-1 허용 및 unknown/누락 값의 예상 결과를 구분 |
| `test_productization_safety.py:117–148` | embedded child program의 실제 runtime 관측 | migrate: 문자열 안에 든 snapshot 호출에도 inventory 전달. AST의 일반 call 탐색만으로 누락시키지 않음 |

추가 규칙: non-null launcher SHA를 쓰는 seam은 지원되는 명시적 inventory ID가 있어야 한다. 기존 두 필드 결과는 SHA None이며 managed-entry proof를 하지 않는 record-only seam에서만 허용한다. `callable` identity, 함수 이름 또는 default verifier와의 객체 동일성으로 production/test를 추정하지 않는다. 필요한 invalid/missing/unknown window refusal tests와 valid matching-window positive tests를 함께 추가한다.

직접 proof API 테스트도 변경 대상이다. `test_general_work.py:159,161,340,559,562,565`는 SHA를 직접 넘기므로 current valid window를 명시하고 missing/unknown/mismatch 사례를 별도로 남긴다. 설치 fixture의 SHA-only snapshot 전달은 `test_productization_safety`, `test_umbrella_lifecycle`, `test_worktree_integration`, `test_human_view`, `test_worktree_history`, `test_git_candidate_reuse`, `test_worktree_execution`, `test_candidates`에서 함께 migrate한다. 이미 window를 넘기는 worker-proof 사례도 entry-1을 실제로 검증하는지 확인한다. 단순 인자 추가만으로 새 window coverage를 주장하지 않는다.

`test_checkout_window_transition.make_exact_suite`의 역사적 planning-1 factory 20건은 현재 코드용 entry-1 factory로 바꾸지 않는다. 이 파일의 default-discovered current-window 검사와 명시적 old factory를 구분한다. old factory는 정확한 구형 source에 속한 채 보존하고, 새 module의 factory를 별도로 추가한다. `test_productization.py`의 imported/re-exported 사례 등 discovery 중복은 임의 제거하지 않는다. 원래 26개 module의 의미를 유지하며 추가 helper는 아래 한 파일 범위 안에서 우선 해결한다.

### P1 세부 순서와 검증 기준

P1a는 전환 검증 기반 작성, P1b는 reader/identity 구현으로 제안한다. 현재 승인된 것은 이 계획의 준비이다. P1a의 실제 파일 작성도 이 계획의 R0와 Owner 실행 승인 뒤 시작한다. 기존 P0 base만으로 entry 검증 경계가 완성됐다고 판단하지 않는다.

| 순서 | 제안 범위 | 완료 기준 / 다음 단계 조건 |
| --- | --- | --- |
| P1a: entry 검증 기반 작성 | 새 `tests/test_entry_window_transition.py` 안에 mandatory `build_entry_suite(old_source, candidate_source, expected_predecessor, prefix_oracle)`와 test-local fixture/oracle를 작성. 기존 controls가 부족할 때는 변경 필요를 먼저 보고하고 범위를 다시 고정 | exact OLD input, independent schema1 literal fixture, schema2 실제 OLD 생성 경로, operation matrix, numbered prefix·late-lock witness와 collection 분리가 검토 가능. 제품 코드 수정 없이 actual factory/fixture bytes의 review input을 준비 |
| P1a validation gate | actual factory/fixture와 source-root map/selection/command input을 고정하고 해당 검증 계획을 검토 | missing/empty factory가 error, historical factory 미대체, 각 관측의 positive/negative control 및 observer 한계가 명확. 필요한 synthetic runner/oracle 검증은 별도 고정된 입력으로 실행·리뷰·Owner 수락 후 P1b에 진입. 미래 entry 성공 테스트를 base 위에서 통과했다고 표시하지 않음 |
| P1b: reader/identity | root launcher, `product.py`, `work.py`, `intent.py`, `workspace.py`, `candidates.py`, `view.py`, `cli.py`, plain auditor 및 기존 26개 test module 중 영향 사례 | literal old inventories 보존, entry-1 map/paired schema/bootstrap, 모든 live proof 전달, non-null SHA의 missing-window 거부, old/current test 의미 분리. P2 lifecycle 구현과 P3 C2 문안까지 끝나기 전 중간 artifact를 설치·배포하지 않음 |

P1b 파일 목록은 edit 상한이며 전부 수정하라는 지시가 아니다. `__init__.py`, `errors.py`, `jsonio.py`, `umbrella.py`는 read-only 기본값을 유지한다. 새 dependency, package rename, shared immutable-writer 일반화, 자동 record rebind, adopter/project entry 수정은 포함하지 않는다. D1의 진단 routing과 D2의 fresh-init admission은 P1a에서 테스트 계약을 고정하고, 실제 behavior 변경은 해당 lifecycle/C2 범위와 함께 승인한다.

P1a authoring의 제안 상한은 60분, fixed candidate 한 번의 작성·정적 확인이다. 실행 budget은 포함하지 않는다. 아직 없는 entry-1 API를 module import 시 호출하지 않고 테스트 실행 시점에 검증하여, 작성된 factory의 수집과 미래 runtime assertion을 구분한다. P1b 전 synthetic validation의 대상은 loader 계약과 observer/oracle 자체의 관측 가능성이다. 실제 entry-1 성공이나 product별 late-writer 안전성은 P1b/P2 구현 후 증거이며, 이를 선행 PASS로 요구하거나 꾸며 내지 않는다. 필요한 synthetic 검사 인터페이스가 기존 named mode로 표현되지 않으면 해당 control 변경 계획부터 검토한다.

필수 test/oracle 계약:

1. **역사 입력.** 획득한 exact OLD의 schema2 detach prefix는 실제 old code로 만들고 해당 입력의 hash를 확인한다. schema1은 production verifier를 가져다 생성한 fixture 하나로 대체하지 않는다. literal membership·schema pairing·release digest·deletion suffix를 독립적으로 구성/검증한 fixture가 필요하다. 이를 실제 구형 writer 실행이라고 보고하지 않는다.
2. **진입점과 proof.** 올바른 entry-1 live bytes/window positive; SHA non-null + missing/unknown/wrong window refusal; old window literal reader; changed mapped launcher 보호; unowned hv2 포함; CRLF unchanged capability; ordinary Work/intent/candidate의 pending/content/ref 검사 보존.
3. **D1/D2.** 정상 entry-1에서 hv2 재등장 → readable content + conflict/12 + lifecycle_ready false; damaged/unsupported/pending 결과 우선; lifecycle 동작별 refusal/65와 bytes 보존; fresh Git/non-Git init의 empty-target positive와 file/dir/symlink/NFC/casefold alias refusal. 최초 receipt나 `.hrn` 등 target 변경 전 거부를 before/after로 확인하고, tracked/absent-index 및 ignore cases의 기존 판단을 보존한다.
4. **operation matrix.** New source로 checkout-1 init/rollback/repair/detach 거부, old source로 fresh entry-1 writer 거부, new source의 `--profile checkout-1` 거부를 각각 positive control과 함께 고정한다. old artifact 자체를 수정해서 refusal을 만들지 않는다.
5. **physical prefixes.** 기존 oracle의 19개 operation group을 실제 syscall의 before/after에 연결한다. S1/S2 byte tears는 T-A의 preserved refusal, N의 exclusive create/short write/mode/flush, old unlink/root sync, binding.next partial/replace/directory sync와 unexpected aliases를 각각 관측한다. 지원하지 않는 syscall/관측은 unavailable/error이며 생략 성공이 아니다.
6. **late old writers.** 동일 writer lock을 부모가 보유한 상태에서 exact old child의 `lock-attempt`를 확인하고, 새 prefix를 올바른 lock ownership 아래 만든 뒤 release한다. `lock-acquired` 이후 old writer의 거부와 무변경을 확인한다. instrumented flock forwarding과 uninstrumented old CLI 결과를 별도 증거로 기록한다. primitive canary 성공만으로 실제 old writer 관측을 대체하지 않는다.

실행 명세의 고정 방식도 유지한다. 기존 controller/runner의 named mode만 사용하고 arbitrary shell command를 추가하지 않는다. entry phase는 `factory=true`가 필수이며 `collect`가 생성한 ordered IDs와 모든 occurrence를 보존한다. P1 focused selection은 위 요구 사례를 actual collection에서 고른 고정 파일로 식별한다. 테스트가 아직 없으므로 이 단계에서 실행 가능한 exact ID나 candidate/collection digest를 꾸며 넣지 않는다. SOURCE에 `colvia`가 추가되거나 `hv2`가 사라지는 root map은 그 실제 candidate를 다시 식별·검토한 뒤 사용한다. 이번에는 run directory를 만들거나 기존 consumed root를 재사용하지 않는다.

기존 전체 구현 계획의 제안 budget은 그대로 입력으로 유지한다: baseline/final을 포함한 collection 최대 8회(각 300초, 다음 실행 승인에서 실제 소비 기록과 대조), P1/P2/P3 focused 각 1회와 공유 correction 1회로 최대 4회×1,200초, converged candidate의 complete normal/parent-O 각 5,400초 1회, artifact 1,800초 1회. 이 숫자는 새 실행 승인이 아니며 consumed base/review/diagnostic budget을 초기화하지 않는다. P1a의 별도 synthetic 검증은 정확한 명령과 필요한 budget을 actual bytes 검토 때 명시해야 하며 여기에 몰래 추가하지 않는다.

중단 조건은 unknown/drifted input, 불명확한 write ownership, 지원하지 않는 observer 경로, 실패한 isolation, 예산 초과, 새로운 계약·파일·명령 필요이다. 실패 결과와 복구에 필요한 최소 입력을 보존하고 한정된 보정안을 제안한다. assertion 완화, retry 추가, timeout 증대 또는 full suite 반복으로 통과를 만들지 않는다.

### 준비 결과 검토용 입력과 다음 승인 지점

현재 준비의 완료 기준은 (a) D1/D2 exact amendment 후보, (b) live caller 및 test seam 처분, (c) P1a/P1b 파일·검증·중단 범위, (d) 고정된 읽기 전용 R0 packet이다. 이 절과 관련 실제 source 발췌, DR-0004, 기존 implementation plan/R0, Contributing/Maintaining, runner/observer/prefix oracle를 포함한 packet을 별도 private 보관 위치에 준비한다. base와 tracked diff digest, untracked 문서별 hash 및 발췌 범위를 기록한다. Reviewer에게 전달되지 않은 full source는 hash만으로 검토됐다고 주장하지 않는다.

다음 제안은 그 packet에 대한 fresh Claude subscription static review 1회, 최대 600초다. tools/MCP/test 실행·파일 변경 없이 정책 문안의 계약 범위, caller/test 처분 누락, P1a 검증 설계의 실행 가능성과 P1b 진입 조건을 검토한다. 호출 전 `claude auth status`의 claude.ai/firstParty/pro 경로를 확인하고 불일치·unknown이면 중단한다. 실제 model/session과 독립성 한계를 결과에 기록한다. 이번에는 호출하지 않았으며, 기존 r01에서 남은 1회 allowance도 소비하지 않는다. 추가 round나 결과를 고친 뒤 재호출은 이 1회 제안에 포함하지 않는다.

R0 응답은 이 문서에 원문과 Driver disposition으로 남긴다. 다음 Owner 결정에서 base의 한정된 결과 수락, 이 amendment 후보의 정확한 설계 수락 여부, P1a의 구체적 authoring scope 승인을 구분한다. P1b code/execution 및 P4의 normative activation은 그 조건을 충족한 뒤의 결정이다. Git, Work Done/STATUS와 실제 adopter 적용은 포함되지 않는다.

보존 목적은 다음 Reviewer/Owner의 이 준비안 검토와 이어질 P1 입력 재사용이다. 이 절의 byte-exact 문서 사본과 고정 review packet만 기존 durable private bundle에 보관한다. 재현 가능한 scan/render 출력은 영구 deliverable로 만들지 않는다. 기존 source worktree와 획득 OLD/실패·진단·r01 결과는 pending Owner 수락 및 다음 검증의 구체적인 입력이므로 유지한다. 해당 소비가 끝나면 보존·사용 여부를 확인하여 기존 cleanup 규칙을 적용한다.

### P1 준비 정적 확인 결과

Python 파일 39개를 import 없이 AST로 읽어 관련 call 283개, import 89개, SHA를 포함한 test dict/dict-comprehension 13개를 검토용 목록에 기록했다. 이 수치는 test 수나 실제 실행 수가 아니며, 13개 모두가 runtime verifier double인 것도 아니다. Embedded child program과 runtime_check 재주입은 별도 원문 발췌로 보완했다.

GFM 렌더링에서 code 밖 literal `**` 0건, 기존 로컬 링크 대상 29개 확인, trailing whitespace 및 `git diff --check` 통과. 이번 작업 기록을 제외한 source 파일 117개의 내용과 mode가 준비 전과 같고, DR-0004 SHA-256은 `799d45740ba00fe7722df3c6caec1c9de8898f2e1b442cca5ab8a08183726ea7`로 유지됐다. Byte-exact 문서 사본과 fixed review packet을 durable private bundle에 보존했다. 원문별 hash·발췌 범위·packet hash는 그 묶음의 input identity에 기록했다.

준비는 완료했고 새 reviewer 호출은 0회다. 제품 import, test collection/execution, controls 변경, run-directory 생성, Git publication 및 계약 활성화는 수행하지 않았다. 위 확인은 문서 준비의 결과이며 P1 구현이나 전환 검증 PASS가 아니다.

## P1 Preparation R0 Review — 2026-10-10

### Authorization, Exact Input And Execution

Owner는 고정 P1 준비 packet에 대한 fresh Claude subscription 정적 검토 1회, 최대 600초 제안에 “진행해”라고 답했다. 이 승인은 해당 전송·응답 수집 및 이 문서의 원문/Driver disposition 기록만을 대상으로 한다. 제품·test·control 수정, 계약 또는 base 결과 수락, 후속 호출, Git/adopter 조치는 포함하지 않는다.

- Review input: `e0960063b2541d2594b82c058f259b29ad8491a5ae756e1b70e80155e7780461`, 350,407 bytes. Source base: `238514686078ce1564010a7b69013f48a635c57c`. Tracked diff SHA-256: `12238ddc334c4a6971d657249732a73d59cc4c3e32b6463d5a7fccfc867a6b04`. Reviewed record SHA-256: `78f9d144d53b52a16ab30d0558c193a09e5b874068d324f16e84facc4592ff26`. 발췌·untracked 입력은 private input identity에 개별 hash로 식별했고 review 전후 전체 입력 일치를 확인했다.
- Observed authentication before invocation: loggedIn true, authMethod `claude.ai`, apiProvider `firstParty`, subscriptionType `pro`. 계정 email이나 credential 값은 기록하지 않았다.
- Actual Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), fresh session `7c32fd61-9c44-495d-8030-8ca1d9f6ea81`. Driver는 Codex. 이전 plan/R0 내용이 packet에 포함돼 prior-review context의 영향은 배제하지 못하며, 이전 Claude rounds와 model-family 독립성도 주장하지 않는다. 새 session이며 이전 CLI session을 resume하지 않았다.
- 고정 호출: `claude -p --model opus --effort medium --safe-mode --restricted --tools "" --strict-mcp-config --mcp-config '{"mcpServers":{}}' --disable-slash-commands --setting-sources "" --permission-mode dontAsk --no-session-persistence --output-format stream-json --verbose`; 별도 system prompt는 승인된 정적 scope·도구 금지·Owner 권한을 명시했다. 정확한 argv는 private authorization에 보존했다. stdin은 위 packet, cwd는 별도 private review directory이며 product test runtime이 아니다.
- Runtime 261.12 seconds, exit 0, timeout false, final result present, API error false. Startup tools `[]`, MCP servers `[]`, tool-use count 0. Reviewer가 실행한 test는 0건이다. 종료 후 process group absent, 입력 before/after PASS. 한도 1/1회 소비; 기존 base bundle의 리뷰 횟수는 사용하거나 초기화하지 않았다.
- Reviewer response SHA-256: `31fbf986af78faf4fa99226b7d3ea95bb4c7badeabef6172729803fee7584923`. 아래 원문은 final response와 byte-for-byte 일치하는 문자열이다. 원문과 이 결과의 durable 사본을 확인한 뒤 중복 API envelope·빈 stderr·별도 response 사본은 남기지 않는다. 입력 packet/identity와 authorization/meta는 미결 correction/Owner 검토의 입력으로 유지한다.

### P1-R0 Reviewer Response — Verbatim

# P1 준비 R0 정적 검토 보고

## 판정

**이 준비안은 아직 P1a 작성 승인이나 D1-A/D2-A 수락의 근거로 쓰기 어렵습니다.** 계약 차단 2건, P1a 설계 차단 2건, P1b 진입 차단 1건이 있습니다.

- DR-0004 A안을 다시 열어야 할 새 모순은 찾지 못했습니다.
- 차단 항목은 모두 문서 수준의 좁은 교정으로 닫을 수 있습니다.
- 이 보고는 Reviewer 소견입니다. Owner의 정책 수락, 실행 승인, 활성화를 대신하지 않습니다.

## 증거 한계

모든 판단은 제공된 바이트의 정적 판독이며, 실행 증거는 없습니다.

**직접 읽지 못한 것** (해시만으로 검토했다고 보지 않습니다):
- `cli.py`, `workspace.py`(`writer_guard` 475–501 포함), `jsonio.py`, root `hv2`
- `common.py`, controller, `test.sb`, `baseline-inputs.json`
- `product.py`의 발췌 밖 구간(switch, repair, detach, `verify_workspace_product`)
- `test_checkout_window_transition.py` 111행 이후
- `.gitignore`, C0 baseline appendix, DR-0002/0003

**정적으로 일치를 확인한 것**:
- SHA 포함 test 구성 13개가 처분 표에 모두 대응합니다(`runtime_check` 재주입 164행, embedded program 포함).
- scan 대상은 39개 파일입니다.
- `candidates.py:240`의 checkout-1 gate, `work.py:_runtime`의 선택적 `inventory_id`, `test_worktree_execution.py:486`의 window 탈락 필터는 처분 표의 설명과 같습니다.
- call 283개, import 89개라는 수치는 다시 세지 않았습니다.

## 차단 항목

### B1. D2-A는 P1b에서 미룰 수 없습니다 (계약 차단, P1b 진입)

- **근거**: `product.py:_workspace_init_preflight`의 fresh 경로에 `not _exists(target / "hv2")`("preexisting launcher is not owned")가 있습니다. 같은 함수의 recovery 경로는 `target / "hv2"`의 receipt와 bytes를 검사합니다.
- **문제**: P1b가 launcher mapping을 `colvia`로 바꾸면 이 줄을 반드시 건드립니다. 줄을 옮기면 hv2 거부가 조용히 사라지고, 남기면 별칭 없는 D2-A 일부를 수락 없이 구현하게 됩니다. 준비안의 "실제 behavior 변경은 lifecycle/C2 범위와 함께 승인"과 양립하지 않습니다.
- **추가 공백**: D2-A는 fresh만, D1-A는 완료된 init replay만 다룹니다. 미완료 entry-1 init 복구 중에 `hv2`가 나타난 경우는 정의되지 않았습니다.
- **최소 교정**:
  - P1b 진입 조건에 "D2-A의 Owner 설계 수락"을 명시합니다.
  - D2-A에 "exact init recovery의 매 재관측에서도 같은 거부, prefix 보존" 한 문장을 추가합니다.

### B2. D1-A의 분류·exit 문안이 제공 증거로 닫히지 않습니다 (계약 문안 차단, 일부는 증거 누락)

- **exit 근거 부족**: `conflict: 12`는 `view.py`의 `EXITS` 표에서만 확인됩니다. `status`/`doctor`가 `conflict`를 쓰는지와 `HV2-WORKSPACE-PRODUCT`→65 mapping은 `cli.py`가 없어 확인하지 못했습니다. 65는 test의 Work 오류 사례에서만 보입니다.
- **경로별 차이 무시**: DR은 진단 단언이 명령 경로별이어야 한다고 합니다. D1-A는 installed와 independent-source lifecycle 모두에 65를 일괄 선언합니다.
- **view와 충돌**: `_workspace_status_observation`은 `classification == "pass"`일 때만 `(works, intents)`를 돌려주고, 비-pass면 `_share_intents=False`로 다시 관측합니다. "conflict인데 view는 내용을 계속 보여 준다"는 이 반환 계약의 변경을 전제합니다.
- **우선순위 누락**: "unknown, damaged, unsupported, pending"만 열거되어 `stale`(13), `incompatible`(11), planning-unavailable `partial`이 빠졌습니다.
- **소비자 영향 누락**: 앞선 미결 표는 "consumer effects"를 요구했습니다. 충돌 중에는 `view confirmation`과 adapter의 status 확인이 모두 12를 반환합니다. C0-H-A는 ordinary Work를 허용하는데, 이 exit가 일반 절차를 막지 않는다는 서술이 없습니다.
- **최소 교정**:
  - `cli.py` exit mapping과 `doctor` 경로를 packet에 넣거나, exit 숫자를 "기존 명령별 mapping에 따름"으로 낮춥니다.
  - 우선순위를 "다른 모든 기존 비-pass 분류가 우선, collision은 그 외에는 pass였을 관측에만 적용"으로 한 문장화합니다.
  - 명령별 소비자 영향 표를 추가합니다.

### B3. late-lock 증인 절차가 적힌 대로는 성립하지 않을 가능성이 큽니다 (P1a 설계 차단)

- **근거**: `prefix-oracle.json`의 `late_lock.required` 2–4항과 준비안 6항은 "부모가 writer.lock을 보유한 채 새 prefix를 올바른 lock ownership 아래 만든다"고 합니다.
- **문제**: guard가 lock 파일을 새로 열어 `flock`하는 구조라면, 부모가 쥔 lock과 새 source 전환의 lock은 서로 다른 open file description이라 충돌합니다. 부모가 쥐고 있는 동안 전환은 진행되지 않습니다. 이 전제는 `workspace.py:475-501`을 보지 못해 확정하지 못했습니다.
- **통제물 한계**: 필요한 순서는 "새 실행자가 lock 획득 → receipt 쓰기 전 정지 → old child가 S0 검사를 통과하고 `lock-attempt` → 새 실행자가 S1 이후 진행 후 해제"입니다. `observer.py`의 fault는 SIGKILL뿐이고 정지·재개 수단이 없습니다.
- **증인 누락 가능성**: `observed_flock`은 `operation == fcntl.LOCK_EX`만 기록합니다. old guard가 `LOCK_EX|LOCK_NB` polling이거나 `from fcntl import flock`이면 이벤트가 나오지 않습니다. launcher가 re-exec하면 hook 자체가 사라집니다.
- **최소 교정** (P1a 승인 전 문서로 고정):
  - lock 보유 주체를 "새 전환 실행자"로 정정합니다.
  - 정지 수단을 하나 고릅니다: observer에 pause 동작 추가(control 변경이므로 별도 검토) 또는 대기 중인 old child에 대한 SIGSTOP/SIGCONT 순서화.
  - S0 양성 대조에서 old child의 `lock-attempt`와 `lock-acquired`가 실제로 관측되지 않으면 해당 증거를 unavailable로 처리한다고 명시합니다.

### B4. factory에서 observer와 scenario로 가는 입력 채널이 없습니다 (P1a 설계 차단)

- **근거**: `runner.py`는 `build_entry_suite`에 `old_source`, `candidate_source`, `expected_predecessor`, `prefix_oracle` 네 개만 넘깁니다. `observer.py`는 `INPUT SHA SCENARIO SHA`가 필요하고 `config()`로 검증합니다.
- **문제**: factory는 controls 위치와 input 파일·해시를 검토된 경로로 받을 수 없습니다. `sys.argv`나 환경에서 추정하면 앞선 R0가 금지한 ambient 입력입니다.
- **관련 공백**: observer는 old code에 fault를 허용하지 않습니다("no old-code fault substitution"). 그런데 "실제 OLD로 schema2 detach prefix 생성"의 중단 수단이 정해지지 않았습니다.
- **최소 교정**:
  - `build_entry_suite` 인자 확장(control 변경 검토 필요)과 고정 input에서의 명시적 파생 규칙 중 하나를 P1a 범위에 적습니다.
  - OLD prefix 생성 수단을 지정합니다: OLD 자체의 injection 기능, 또는 OLD API를 부르는 별도 subprocess. 후자는 "test seam" 라벨을 붙입니다.

### B5. `test_checkout_window_transition.py` 처분과 P1b/P2 경계가 비어 있습니다 (P1b 진입 차단)

- **기본 발견 test 5건의 처분이 없습니다** (4건은 P0 seed ID입니다):
  - `test_current_source_declares_checkout_window_with_same_membership`는 `'checkout-1'`과 `SERIAL_MANAGED_PATHS` 일치를 단언하므로 P1b에서 반드시 깨집니다.
  - `test_old_and_unknown_source_declarations_are_not_current_candidates`의 window 목록에 checkout-1이 없습니다.
  - `DetachVersionTests`는 schema 2와 `(3,3)` 음성을 단언하는데, 이는 P2에서 바뀝니다.
- **단계 경계가 모호합니다**: P1b 행의 "paired schema"가 switch 2/detach 3 writer를 포함하는지 불명확합니다. P1b 뒤 P2 전에는 entry-1 fresh init은 되지만 detach는 schema 2인 중간 상태가 됩니다. P1 focused 실행에서 어떤 단언이 통과하고 어떤 단언이 실패해야 하는지 정해지지 않았습니다.
- **migrate 목록 누락**: inventory에는 이 파일의 SHA-only `snapshot` 호출(182, 185, 370, 382, 395, 402행)이 있는데 migrate 목록에 없습니다. 발췌 밖이라 factory 내부인지는 확인하지 못했습니다.
- **factory 보존의 의미**: "non-null SHA는 window 필수" 규칙이 들어가면, 현재 `hv2ref`를 import하는 이 factory는 호출 시 깨집니다. runner는 새 factory만 부릅니다.
- **`SERIAL_MANAGED_PATHS` 기호**: `UMBRELLA_`/`LEGACY_MANAGED_PATHS`가 `SERIAL_`에서 파생됩니다. 이 기호가 old literal로 남는지 새 집합이 되는지에 따라 test 20, 38, 86행 소비자가 달라집니다.
- **최소 교정**:
  - 5건 각각에 keep/migrate/duplicate와 귀속 단계(P1b 또는 P2)를 적습니다.
  - P1 focused의 기대 실패·통과 목록 규칙을 명시합니다.
  - factory는 "후보에서 실행 불가한 역사 코드"로 라벨링하거나 호출부를 migrate합니다.
  - `SERIAL_MANAGED_PATHS` 기호 계획을 한 줄 추가합니다.

## 비차단 교정 (P1a 실제 바이트 검토 전 반영 권장)

| # | 항목 | 근거 | 교정 |
| --- | --- | --- | --- |
| N1 | caller 표 누락 | `work.py:_runtime`(1164–1171)의 window allowlist, `_umbrella_runtime`(1174), `_allows_unchanged_crlf`; `product.py` 713/792/803/1146/1228/1243과 `cli.py:223`의 `require_workspace_runtime` 호출 | 각각 처분(P1b 변경, P2 소유, 불변)을 추가합니다 |
| N2 | embedded launcher | `test_productization_safety.py:107`의 `WORKSPACE_INVENTORY_ID = "checkout-1"`; `require_workspace_runtime`의 `target / "hv2"` 일치 요구 | "snapshot 인자"뿐 아니라 선언과 설치 경로도 migrate 대상으로 적습니다 |
| N3 | root launcher 경로 literal | AST call 목록은 `installed()`류 helper의 `target/"hv2"`, `payload/hv2` 구성을 잡지 못합니다 | 문자열 literal scan 목록을 packet에 추가합니다 |
| N4 | D1/D2 별칭 비대칭 | D2-A는 NFC/casefold 별칭과 파일·디렉터리·symlink를 거부하고, D1-A는 "root `hv2`"만 말합니다 | D1-A에 대상 종류와 별칭 포함 여부를 명시합니다 |
| N5 | 완료된 update replay | D1-A는 "update" 거부, DR은 S6 replay를 "observes current"로 둡니다 | collision 중 완료 replay의 결과를 한 문장으로 정합니다 |
| N6 | amendment 문안 언어 | 규범 인용문에 한·영이 섞여 "otherwise valid"의 범위가 모호합니다 | DR 본문 언어로 exact text를 다시 씁니다. CONTRIBUTING에 따라 대상 clause와 `Accepted (Amended)` 기록 계획도 명시합니다 |
| N7 | test 계약 3항의 권위 | amendment가 수락되지 않은 채 P1a가 승인되면 D1/D2 test의 근거가 없습니다 | 3항 작성 조건을 amendment 설계 수락으로 두거나 "pending-contract"로 라벨링합니다 |
| N8 | 새 module의 중복 수집 | `loader.discover("tests")`가 새 module을 기본 수집하고 runner가 factory를 다시 부릅니다 | factory 전용 class는 module 수준에서 발견되지 않게 한다고 명시합니다. 기대 `duplicates`는 빈 값으로 적습니다 |
| N9 | schema1 literal fixture | 취득한 OLD는 schema 2만 쓰고, 이전 window의 실제 release 바이트는 없습니다 | fixture의 window와 합성 release 구성을 지정하고 "structural/synthetic" 라벨을 붙입니다 |
| N10 | P1a 검증의 예산과 리뷰 | 기존 budget에 P1a synthetic 실행이 없습니다. test와 oracle은 CONTRIBUTING상 R0/R1 기본 대상입니다 | 실제 바이트 검토 때 명령·budget·리뷰 승인을 따로 요청한다고 다음 결정 목록에 넣습니다 |
| N11 | view 행의 범위 충돌 | caller 표의 `view.py` 행은 P1 변경에 "collision 표시"를 넣었고, 본문은 D1 behavior를 뒤로 미룹니다 | 둘 중 하나로 통일합니다 |
| N12 | D2-A의 "target 변경 전" | fresh target에서 guard가 `.hrn/locks`를 만드는지 `workspace.py`가 없어 확인하지 못했습니다 | 허용되는 차이(빈 writer.lock 여부)를 기존 B3 규칙과 맞춰 적습니다 |

## 영역별 결론

- **D1-A/D2-A**: 방향은 C0-H-A 및 현 fresh-init 코드와 일치합니다. B1·B2와 N4–N6을 반영한 exact text가 있어야 Owner가 판단할 수 있습니다.
- **caller/test 처분**: SHA 구성 13개와 간접 전달은 닫혔습니다. B5와 N1–N3이 남습니다.
- **P1a 작성 가능성**: loader, 역사 입력, operation matrix, D1/D2 계약 초안은 작성할 수 있습니다. late-lock(B3)과 observer 구동(B4)은 현 controls로는 설계가 고정되지 않았습니다.
- **P1b 진입 조건**: 준비안의 조건에 다음을 더해야 합니다.
  - D2-A 수락
  - B5의 단계별 기대 실패·통과 규칙
  - N1의 gate 목록
  - P1a 결과의 검토와 Owner 수락

### P1-R0 Driver Dispositions

아래 처분은 Reviewer 제안을 실제 source와 대조한 Driver 판단이다. 코드·controls 또는 위 exact amendment 후보를 수정한 결과가 아니다. Reviewer가 못 본 추가 source는 이번 호출 뒤 Driver만 읽었으므로, 그 사실로 Reviewer의 증거 범위를 소급 확장하지 않는다. P1a/P1b는 아직 착수하지 않는다.

| ID | 처분 | 확인 내용과 후속 조치 |
| --- | --- | --- |
| B1 | revise / needs-user | `_workspace_init_preflight:452–496`의 fresh·complete·recover 경로와 `workspace_init_apply:509–533`의 guard 전/후 재관측을 확인했다. P1b에서 launcher mapping과 init 경로를 분리해 생각한 계획은 불충분하다. D2-A exact 설계 수락을 첫 관련 P1b edit 전 조건으로 명시해야 한다. 미완료 entry-1 init의 매 exact recovery 관측에서 retired hv2 충돌을 거부하고 prefix를 보존한다는 문안은 추가 Owner 판단이 필요한 amendment 후보로 준비한다. 이번 리뷰로 수락된 정책이 아니다 |
| B2 | revise; 일부 defend | `cli.py:106–108,140–166,218–221`을 Driver가 읽어 status/doctor가 공통 workspace_status를 사용하고 conflict→12, ContractError→65로 매핑됨을 확인했다. 그러나 installed CLI에는 init/repair subcommand가 없으므로 명령 경로별 표가 필요하며 unsupported invocation까지 65로 일반화하지 않는다. 다른 모든 기존 non-pass 관측 우선과 confirmation/adapter 소비자 영향을 보완한다. `_workspace_status_observation:653–659`의 non-pass graphs=None은 사실이나 `view.py:214–221`이 conflict에서 Work/intent를 새로 읽는다. 따라서 readable conflict를 위해 공유 graph 반환 계약을 반드시 바꿔야 한다는 전제는 수용하지 않는다. 이 fallback을 유지하고 fresh graph/안정성 검사를 검증하는 방향이 최소 변경이다 |
| B3 | revise | `writer_guard:475–501`과 `jsonio.exclusive_file_lock:153–181`은 guard 재진입을 금지하고 blocking `fcntl.flock(fd, LOCK_EX)`를 사용한다. 부모가 lock을 보유한 채 별도 새 실행자가 lock을 요구하는 현재 설명은 실행 절차로 충분하지 않다. 새 전환 실행자가 lock을 획득하고 첫 receipt 전 검증된 지점에서 pause → exact old child의 S0 통과/lock-attempt 관측 → 새 실행자 resume/prefix/lock 해제 → old acquired/refusal 관측으로 계획을 고친다. bounded pause/resume는 observer control 변경안으로 먼저 정의·검토한다. 이 audit에서 LOCK_NB 사용은 없고 launcher에 re-exec도 보이지 않았지만, 실제 observer S0 positive witness가 필요하다는 조건은 유지한다. 실제 deadlock 재현 결과로 보고하지 않는다 |
| B4 | accept | runner의 네 인자와 observer의 INPUT/SHA/SCENARIO/SHA 사이에 명시적 전달 계약이 없다. 이미 검증된 invocation의 값에서 runner가 만드는 명시적 `execution_context` 인자 확장을 설계하는 방향을 추천한다. factory의 환경·sys.argv 추정은 사용하지 않는다. 이 방향은 runner와 factory interface의 변경 범위이므로 P1a 한 파일 authoring 제안을 수정해야 한다. schema2 OLD prefix는 exact OLD API의 기존 `inject_at="after-receipt"`를 격리된 synthetic child에서 호출하는 test seam으로 명시하는 방향을 추천한다. 이를 uninstrumented old CLI 증거로 계산하지 않는다. 구체적 child/command/context schema는 후속 문서 보정에서 고정하며 아직 실행하지 않는다 |
| B5 | accept | default test 5건과 historical `make_exact_suite` 본문을 구분하고 각 default test의 P1b/P2 귀속을 명시해야 한다. 182/185/370/382/395/402행은 `make_exact_suite` 내부다. candidate의 현재 API로 이 historical factory를 호출하는 것은 지원하지 않으며, 실제 old factory 사용은 고정 OLD source의 원래 환경에 속한다고 명확히 해야 한다. 기존 source의 역사 코드를 entry-1용으로 retarget하지 않는다. literal old inventory 상수와 current member 상수를 분리하는 symbol 계획 및 P1 focused 선택 규칙을 추가한다. P2 미구현 사례를 expectedFailure/skip으로 바꿔 PASS를 만들지 않는다 |

| ID | 처분 | 후속 문서 보완 범위 |
| --- | --- | --- |
| N1 | accept | `_runtime`, `_umbrella_runtime`, `_allows_unchanged_crlf`와 product/cli runtime gate 호출을 P1b 변경·P2 소비·불변으로 명시 |
| N2 | accept | embedded launcher의 `WORKSPACE_INVENTORY_ID`와 installed root 경로까지 migrate 대상으로 명시; snapshot 인자만으로 축소하지 않음 |
| N3 | accept | root/payload launcher literal 및 installed helper 문자열 scan을 추가 packet에 포함. AST 호출 목록과 별도이며 zero-hv2 목표로 바꾸지 않음 |
| N4 | revise / needs-user | D1의 occupant 종류·별칭 범위를 exact text로 정리. D2 별칭 규칙을 D1에 자동 복사해 기존 accepted H-A 범위를 넓히지 않음 |
| N5 | accept / needs-user | 완료 update replay의 관측과 collision 중 lifecycle 재호출 거부를 구분하는 문안 후보 준비. S6의 이미 완료된 binding을 pending/B0로 되돌리거나 재실행하지 않음 |
| N6 | accept | DR 본문의 English로 exact amendment 후보를 다시 작성하고 named clauses, Accepted (Amended) append 계획과 별도 활성화를 표시. 기존 Accepted bytes는 유지 |
| N7 | accept | D1/D2 behavior test 작성의 근거는 exact amendment 설계 수락 또는 명시적인 pending-contract draft. test 작성만으로 정책 수락을 만들지 않음 |
| N8 | revise | factory 전용 class가 default discovery에 다시 잡히지 않도록 하는 요구는 수용. `duplicates` 전체를 empty로 기대하라는 처방은 수용하지 않음: base에서 기존 177개 ID가 두 번 수집됐다. 새 factory ID는 default ID와 겹치지 않고 factory 안에서 유일해야 하며, 기존 default multiplicity는 유지 |
| N9 | accept | schema1 fixture의 정확한 old window, 독립 literal member set·synthetic release 구성과 structural/synthetic 한계를 명시. 없는 historical release 바이트를 actual-old 실행이라고 부르지 않음 |
| N10 | accept | P1a actual-byte review와 synthetic 실행의 명령·budget·R0/R1 및 Owner 승인 조건은 별도로 고정. 기존 base 또는 남은 리뷰 횟수에 포함시키지 않음 |
| N11 | accept | view caller 표에서는 identity 전달과 collision behavior의 귀속을 분리하고 본문의 P1b/P2/P3 범위와 일치시킴 |
| N12 | revise | fresh init은 guard 전에 preflight하므로 시작 시 충돌이면 target mutation 없이 거부해야 한다. 이미 시작한 exact recovery의 재관측은 stable lock 생성 가능성과 기존 허용 범위를 구분한다. 빈 writer.lock 예외를 모든 경로에 새로 허용하지 않으며, 기존 lock/prefix 규칙을 확인한 command별 before/after 기준으로 문안을 작성 |

### P1-R0 Result And Next Bounded Proposal

승인된 static review 1회와 그 결과 기록을 완료했다. Reviewer 판정은 차단 5건이며, Driver는 주요 누락을 수용하되 B2의 필수 graph-return 변경 전제와 N8의 전체 duplicates=empty 처방을 위와 같이 수정했다. 이 처분은 reviewer 재확인이나 차단 해소 PASS가 아니다. D1/D2는 준비 방향만 선택된 상태이고, 기존 exact amendment 후보는 수락 또는 구현에 바로 사용할 수 없다. P0 base 20/20 PASS는 그 한정된 범위로 유지한다.

다음 한정 작업으로 이 문서의 새 correction 절과 새 private packet만 작성하는 것을 제안한다. 기존 검토 입력과 Reviewer 원문은 보존한다. 승인 전 제품·test·control 파일이나 Accepted DR를 바꾸지 않는다. 제안 작성 상한은 45분, correction 후보 한 번이며 test/runner 실행과 추가 reviewer 호출은 포함하지 않는다.

작성할 결과는 다음과 같다.

1. D1/D2의 English exact amendment 후보: init recovery, 모든 기존 non-pass 우선, 명령별 status/doctor/view/confirmation/지원되는 lifecycle 경로, occupant·alias·완료 replay와 소비자 영향.
2. P1a의 수정된 파일·interface 설계: `runner.py`의 explicit execution_context 전달, `observer.py`의 bounded pause/resume, `prefix-oracle.json`의 새 실행자 lock ownership, controls README와 새 test module의 연결. 이 파일들을 실제 수정하는 승인은 아니다. `common.py`, controller, Seatbelt policy 또는 새 dependency가 추가로 필요하면 확대를 숨기지 말고 보정안의 미결로 표시한다.
3. 다섯 default test 각각의 단계·keep/migrate/duplicate, historical factory의 실행 경계, literal old/current inventory symbol, P1/P2의 focused 범위. P1 focused는 구현된 P1 assertions만 exact IDs로 골라 모두 pass해야 하며, 미구현 P2는 미검증으로 남긴다. P4 complete에서 누락·skip·expectedFailure로 대체하지 않는다.
4. 이번 Reviewer에게 없었던 CLI mapping, workspace/jsonio lock, launcher, 필요한 common/controller/policy/old-input 설명과 정확한 test 문맥을 제공하는 packet. 추가 정보는 각 지적을 판정하는 데 필요한 범위로 제한하고, 새 packet의 identity와 누락 입력을 명시한다.

완료 기준은 위 문안·표·control interface가 읽어서 검토 가능한 하나의 수정안과 고정 packet으로 존재하는 것이다. 작성 중 실행·source/control 변경이나 새 계약 선택이 필요해지면 그 부분을 미결로 남기고 중단한다. 그 결과를 본 뒤 Owner가 새 review나 실제 P1a authoring 범위를 결정한다. 이번 1회 리뷰 권한은 소진됐으며 후속 호출 권한은 없다.

## P1 Preparation Correction Candidate — 2026-10-10

### 승인 범위와 이번 수정안의 위치

Owner는 P1-R0의 지적을 반영해 계획 문서와 검토 packet만 보정하는 45분·후보 1회 제안에 “진행해”라고 답했다. 이 절과 새 private packet이 그 결과다. 기존 P1 준비안·R0 원문·Driver 처분은 검토 당시 의미로 보존한다. 다음 검토는 이 절을 현재 제안으로 읽으며, 앞의 문안과 충돌하는 부분은 이 절의 수정안을 따른다. 이는 제안 사이의 우선순위이며 Accepted DR나 현행 M3의 우선순위를 바꾸지 않는다.

이번 변경은 기존 작업 기록의 추가 절과 현재 disposition, private 검토 입력뿐이다. runtime, tests, controls, Accepted DR-0004, Development Index와 STATUS는 그대로다. 추가 reviewer 호출, test import/collection/execution, 새 실행 root 생성도 하지 않는다. 보정안 작성 완료와 기술적 차단 해소를 구분한다. 후속 reviewer가 이 바이트를 확인하기 전에는 R0 PASS라고 쓰지 않는다.

### C1. Exact English Amendment Candidate

아래는 앞의 한·영 혼합 인용문을 대체할 English 문안 후보다. 추가로 구체화한 항목은 incomplete-init recovery, D1의 occupant/alias 범위와 `observed_names`, 완료된 lifecycle replay의 현재 충돌 거부이다. 이들은 named amendment의 Owner 판단 대상이며, D1-A/D2-A라는 준비 방향 선택만으로 이미 수락됐다고 보지 않는다.

> **Named Amendment: Entry Diagnostics And Fresh-Init Admission (D1-A/D2-A).** This amendment supplements the retired-entry paragraph of **Rollback, Proof And Retained Meaning**, the fresh-init row of **Inventory And Version Table**, and the fresh-init and completed-replay cases of **Source By Target By Operation**. It does not change the S1 one-way boundary, T-A torn-write limit, admitted predecessor, local/worker policies, persistent record schemas, or authority identities.
>
> **Collision observation.** A retired-entry collision is the presence of an immediate target-root entry whose name, after Unicode NFC normalization and case folding, equals `hv2`. Enumerate the root names without following the occupant. Files, directories and symbolic links, including dangling symbolic links, are occupants; do not open, execute, rename or delete them to resolve the collision. Alias inclusion is an explicit addition to this amendment, not a retrospective claim about the earlier C0-H-A text. Existing unsafe-path, topology, unsupported, damaged, pending, stale, incompatible, partial and other non-pass outcomes retain their original meaning and precedence. Collision changes the diagnostic classification only when the complete ordinary observation would otherwise be `pass`. It never hides or improves another non-pass result.
>
> **D1-A diagnostics.** For an otherwise valid entry-1 product/binding and record observation with a retired-entry collision, supported `status`, `doctor` and `view` paths report `classification: conflict`, exit 12. Retain the verified current product/binding; report `lifecycle_ready: false` and `retired_entry_collision: {path: "hv2", observed_names: [...], ownership: "project", preserved: true}`. `path` denotes the canonical retired name; `observed_names` contains every colliding immediate-root name, once each, sorted by UTF-8 bytes. The human-readable view and next action identify the actual names and require a separate operator decision. These are derived diagnostic fields, not persistent state. They are not required additions to every collision-free response.
>
> Readable Work, intent and candidate content remains available only after fresh graph and stability checks. In particular, `view confirmation` may return 12 while displaying a valid current ticket and its independent checks; this is not confirmation, readiness, or authorization. Ordinary Work/intent/candidate commands retain their exact-content, pending, reference, binding and ticket rules. They neither execute a retired occupant nor exclude it from snapshots. Only the verified mapped `colvia` entry is excluded and protected as managed runtime. A collision diagnostic does not bypass a stale result, an unavailable required reference or any existing acceptance gate.
>
> **Lifecycle refusal and replay.** On supported new-runtime lifecycle paths, a detected retired-entry collision refuses init replay/recovery, update, rollback, repair and detach with `HV2-WORKSPACE-PRODUCT`, exit 65, before any further product or authority publication. This includes an invocation of an exact already-completed operation: observe and preserve the current binding/history, then report the present collision without performing the operation again. The message must distinguish this current refusal from the historical operation's completion. Do not relabel a completed operation as pending or failed, rewind its binding, or repeat its old truth comparison as a new completion claim. Use status/doctor/view to inspect the current verified binding. Unsupported commands, bootstrap failures and invalid command syntax retain their own existing diagnostics; this amendment does not promise code 65 for every unsuccessful invocation.
>
> **D2-A fresh init and exact recovery.** Fresh entry-1 init refuses every retired-entry occupant described above. When the occupant is present at the initial admission check, refuse before creating any target directory, init plan, receipt, lock or other target file, with `HV2-WORKSPACE-PRODUCT`, exit 65. Existing `colvia` collision, path/topology, Git-index and ignore-policy checks still apply. An absent worktree file is not evidence that an index or topology check is unnecessary.
>
> An exact incomplete-init recovery performs the same collision check before resuming and at each existing under-guard re-observation. On detection, preserve the already durable prefix and perform no further product/authority publication. If the collision appears only after the initial check, do not claim the invocation made no earlier write. The only new scratch differences permitted by an existing guard contract are its exact `.hrn/locks` directory and empty regular `writer.lock` anchor where that contract permits their creation; no other path, replacement or content change is exempted. A preexisting malformed lock remains an error. This is not an atomic protection claim against a non-cooperating process changing paths between observations. Do not delete or rename the occupant or any prefix to obtain a successful retry.
>
> **Acceptance and effect.** Owner acceptance must identify the exact amendment revision and these named clauses. On that acceptance, append an explicitly named `Accepted (Amended)` decision record without rewriting the earlier accepted bytes. Technical activation remains separate: DR-0002 M3 stays effective until the exact eleven-member C2 successor, qualification and separate Owner result/activation acceptance. `.hrn/`, `HV2-`, `hv2ref`, authority/record IDs, completed history and the absence of automatic Work/Git actions are unchanged.

### C2. 명령별 결과와 소비자 영향

현재 `cli.main:140–166`은 두 정상 CLI route에 공통으로 conflict→12, ContractError→65를 적용한다. source와 installed `status`/`doctor`는 모두 workspace_status를 호출한다. Installed parser에는 init/repair가 없으며, independent source의 lifecycle은 명시적 source profile을 요구한다. 아래 표는 올바른 entry-1 bootstrap/지원되는 route/정확한 인자를 전제로 한 목표 동작이다. 파서·bootstrap·잘못된 source profile의 기존 거부를 이 표로 덮지 않는다.

| 호출 경로 | collision만 있을 때의 목표 결과 | 소비자와 검증 기준 |
| --- | --- | --- |
| Installed `colvia status/doctor`; independent `colvia --source-checkout status/doctor` | verified product/binding + conflict/12 + collision/readiness fields | adapter와 automation은 exit 12를 clean 또는 product-unavailable로 단정하지 않는다. 구체적 collision과 다른 관측을 설명하고 별도 명령의 실제 gate를 확인한다 |
| Installed/independent ordinary `view`, `view work`, `view intent`, `view candidates` | fresh readable content + conflict/12 | `_workspace_status_observation`의 non-pass graphs=None을 유지해도 `view._observe:214–221`이 새 graph를 읽는다. 공유 graph 반환 계약을 넓히지 않는다. 기존 안정성 재관측/참조 실패는 그대로 유지한다 |
| Installed/independent `view confirmation --input …` | 정확한 ticket의 reader checks와 collision 설명 + 12 | exit 12만으로 일반 Work가 금지됐다고 결론내리지 않는다. 실제 content/ref/ticket 검사가 충족됐는지와 human approval을 따로 확인한다. stale/unavailable/pending 문제는 collision 명목으로 무시하지 않는다 |
| Installed ordinary Work/intent/candidate | collision 자체로 전역 거부하지 않음 | 실행 중 검증한 inventory, current content, pending과 binding gate를 통과해야 한다. 성공·거부 exit와 오류 코드는 해당 명령 계약대로다. hv2 재등장으로 snapshot이 바뀌었으면 정상적인 content-stale 거부가 가능하다 |
| Installed update/rollback/detach; independent supported init/update/rollback/repair/detach | 현재 collision이면 PRODUCT/65; exact completed replay도 같은 현재 거부 | 수행 완료된 receipt/history는 보존하고 메시지는 현재 장애를 설명한다. 새 publication·history rewind 없음. init/repair를 installed 명령으로 새로 추가하지 않는다 |
| Independent fresh init의 첫 관측 | D2 occupant면 PRODUCT/65, target 변경 0 | 빈 Git/non-Git positive와 file/dir/symlink/alias refusal을 대조. target before/after에 lock 예외를 적용하지 않는다 |
| Independent incomplete-init recovery | initial 및 기존 under-guard check에서 D2 검사; 감지 뒤 추가 publication 없음 | 이미 존재한 prefix를 보존. 초기 검사를 통과한 뒤 등장한 collision은 앞선 허용 쓰기와 기존 guard scratch 차이를 구분해 기록 |
| 기존 다른 non-pass / unsupported command / old executor | 원래 분류·exit·오류 우선 | 특히 partial(planning unavailable 포함), stale, incompatible, unsupported, degraded/unstable 등은 conflict로 치환하지 않음. old executor마다 기존 bootstrap/receipt/profile 결과를 따로 단언 |

P3의 adapter·current manual에는 이 구분을 명시한다. D1은 blanket write refusal도 blanket acceptance permission도 아니다. 대상·ticket·input identity가 바뀌면 기존 exact approval 재사용 규칙을 따르며, collision 처리를 이유로 사용자의 파일을 자동 이동하지 않는다.

### C3. P1a의 명시적 factory 입력과 수집 계약

수정된 interface 제안은 `build_entry_suite(old_source, candidate_source, expected_predecessor, prefix_oracle, *, execution_context)`이다. `runner.py`가 기존 `config(INPUT, SHA)` 검증 직후 아래 context를 구성해 전달한다. 이 추가 인자는 승인된 test interface 변경 대상이며, ambient 환경·factory의 `sys.argv` 조회 또는 source-relative 경로 추측으로 대체하지 않는다.

| context field | 유일한 출처 / 사용 제한 |
| --- | --- |
| `schema: 1`, `phase: "entry"` | 고정 interface version과 이미 검증한 invocation phase. base mode는 factory를 호출하지 않음 |
| `invocation_path`, `invocation_sha256` | runner가 실제로 검증한 readonly INPUT과 SHA. factory가 다른 input을 선택할 수 없음 |
| `controls_dir`, `observer_sha256` | 검증된 `paths.controls`와 `controls["observer.py"]`. observer 경로는 그 디렉터리의 고정 `observer.py` |
| `work_root` | controller가 이번 run에 만든 WORK를 runner가 받은 `out` 값. parent `inputs.json`, `result.json`, 이전 run, OLD/SOURCE와는 다른 쓰기 경계 |
| `runtime_path`, `runtime_sha256` | 검증된 runtime의 실제 executable·digest. 임의 Python이나 shell을 선택하지 않음 |
| `observer_command_prefix` | 기존 `common.python_command(c, p, "observer.py")`가 반환한 고정 bootstrap argv의 immutable tuple. 위 runtime/controls와 완전히 일치해야 하며 임의 command 입력이 아님 |

runner는 exact field set, 값의 타입·일치, resolved regular-file/no-link 및 WORK 경계를 확인한다. Context의 파생 필드는 원래 c/p/input/out과 다시 대조한다. factory에는 복사된 읽기 전용 mapping으로 전달하며, nested mutable config 전체나 임의 command/environment를 전달하지 않는다. Observer는 child 시작마다 원래 INPUT/SHA와 자기 scenario SHA를 다시 검증한다. Context는 권한 token이나 새로운 persistent record가 아니다.

Factory 생성 시에는 디렉터리·scenario·subprocess를 만들지 않는다. 입력 식별과 순수 suite 구성만 하고, fixture 및 observer 호출은 선택된 test의 setUp/test 실행 안에서 수행한다. Factory-only TestCase는 factory 안의 local class로 만들어 module-level 발견 대상에 노출하지 않는다. Test ID는 root 경로나 run 이름에 의존하지 않는 고정 module/class/method 이름이다. runner는 factory가 nonempty TestSuite인지, factory ID가 내부에서 유일한지, default IDs와 교집합이 없는지를 검사한다. 기존 default discovery의 177개 중복 ID를 제거하거나 전체 duplicates를 empty로 요구하지 않는다. 모듈 import에 아직 없는 entry API를 요구하지 않으며, 실제 미구현 behavior test는 실행하면 fail해야 한다. skip/expectedFailure로 준비 완료를 만들지 않는다.

Observer 호출은 검증된 `observer_command_prefix`에 `INPUT INPUT_SHA SCENARIO SCENARIO_SHA`만 붙인다. 실제 prefix는 `RUNTIME -I -S -B -c BOOTSTRAP CONTROLS observer.py`이며 BOOTSTRAP은 기존 `common.py`의 고정 값이다. `-I -S`에서 `common` import가 사라지는 direct-file 실행 형태로 되돌리지 않는다. Cwd와 child 환경은 승인된 run의 제한된 값을 그대로 사용하고 shell 또는 `start_new_session`을 사용하지 않는다. Scenario, target, events, pause 파일은 모두 이 run의 WORK 아래에 두며, events/handshake는 product target 밖에 둔다. 다른 run의 EXEC 경로는 context가 가리킨 WORK가 아니므로 factory가 쓰지 않는다. 기존 observer의 EXEC-level 검사보다 좁은 WORK 검사는 factory에서 수행하고, 그 우회를 방지하는 negative case도 작성한다.

Entry scenario의 위치는 `WORK/entry-scenarios/ID.json`으로 고정한다. Observer는 검증된 SCENARIO 경로에서 `WORK = SCENARIO.parent.parent`를 명시적으로 유도하고, 그 구조가 `EXEC/runs/<고정 mode-slot>/work`인지 확인한다. Entry phase의 target/events/ready/release 모두 이 WORK 경계를 다시 검사한다. Mode-slot은 승인된 controller allowlist에 있는 이름만 허용하고 parent evidence를 읽어 추정하지 않는다. Base phase의 기존 scenario 경로는 이 신규 entry 규칙으로 소급 변경하지 않는다. 이 규칙은 observer가 환경이나 현재 디렉터리로 WORK를 추정하는 입력 공백을 막는다.

### C4. 새 실행자가 소유하는 lock과 pause/resume

수정안에서는 test coordinator가 writer.lock을 보유하지 않는다. 새 전환 실행자가 정상 `writer_guard`로 lock을 획득한다. Observer가 `lock-acquired`를 기록한 직후, guard 내부의 전환 preflight와 첫 receipt 전에 멈춘다. 이 시점의 목표 상태는 S0다. 원래 guard 순서를 옮기거나 old source에 별도 lock 함수를 주입하지 않는다.

`observer.py`의 entry-phase scenario에 선택적 `pause` 필드를 제안한다. 기존 base scenario의 다섯 필드는 그대로 허용하며 pause가 없으면 기존 동작을 유지한다. 새로운 pause shape는 `{event: "lock-acquired", path: ".hrn/locks/writer.lock", occurrence: 1, ready: RELATIVE_WORK_PATH, release: RELATIVE_WORK_PATH, timeout_seconds: 15}`로 닫는다. New-source/installed-new와 synthetic lock-canary 두 selector에서만 허용하고 old-source/installed-old에는 금지한다. 기존 kill/short-write `fault`와 pause를 구분하며 old bytes/byte writers를 변경하지 않는다.

Pause 상태의 ready JSON은 scenario SHA, event sequence, observed target/lock identity와 child PID를 담는다. Child가 WORK의 신규 regular file로 exclusive publish하며, parent는 그 exact 내용을 확인한 후 matching scenario SHA/sequence와 `action: "continue"`만 담은 release JSON을 exclusive publish한다. 경로는 입력에 고정되고 symlink/hardlink/기존 파일/다른 scenario token은 거부한다. Child는 최대 15초 동안 제한된 polling으로 matching release를 기다린다. timeout·잘못된 release는 error이며 자동 계속하지 않는다. 이 handshake는 test 동기화만 하며 product 상태나 Owner 권한을 나타내지 않는다.

Late-writer 한 사례의 순서는 다음과 같다.

1. 같은 old executor·request·runtime·topology의 별도 S0 positive control에서 lock-attempt/acquired와 예상 성공을 관측한다. exact old source를 수정하지 않는다. bootstrap 재실행이나 관측되지 않는 lock 방식 때문에 witness가 없으면 unavailable/error다.
2. 새 실행자가 lock을 얻고 S0 pause-ready를 보낸다. Coordinator는 S0와 inode/path identity를 확인한다.
3. Exact old child를 시작한다. 그 child가 실제 guard 진입 경로를 지나 같은 lock의 attempt를 기록하고, 새 실행자가 보유하는 동안 acquired가 없음을 확인한다. 단지 프로세스가 있다는 사실이나 arbitrary sleep은 증거가 아니다.
4. Matching release를 보내 새 실행자가 지정 prefix까지 진행하게 한다. prefix에 따른 정상 종료 또는 사전 검토된 kill fault 뒤 lock이 해제된다. S1/S2 torn-write 관측은 별도 byte-tear 사례로 구분한다.
5. Old acquired 뒤 receipt/schema/window에 의한 예상 refusal과 product/truth 보존을 확인한다. 단순 nonzero, missing input, runtime/topology/permission 오류는 negative control 성공이 아니다.

P1a에서는 synthetic lock-canary pair로 handshake/timeout/잘못된 token/정리와 fd 관측 자체를 검증한다. 위 product late-writer sequence의 실제 새 entry prefix와 OLD writer 결과는 P2 증거다. 각 synthetic child 60초, coordinator case 90초와 15초 pause는 후속 실행안의 제안 상한이며 아직 실행 승인이 아니다. 모든 test/observer 자식은 controller가 감독하는 sandbox child process group 안에 남기고, 실패·timeout 시 child 종료와 group absence를 확인한다. 현 Seatbelt의 same-sandbox signal 및 WORK 쓰기 범위를 넓히지 않는다. 그 안에서 구현·관측할 수 없으면 정책을 자동 확대하지 않고 중단한다.

### C5. OLD detach 입력과 독립 schema1 fixture

Schema2 detach prefix는 획득한 exact checkout-1 OLD로만 생성한다. 고정된 stdlib-only child entry가 OLD/src만 import 경로에 추가하고 OLD product API의 preview/apply를 호출한다. Detach apply는 기존 `inject_at="after-receipt"`로 중단하며 `InjectedCrash`의 exact point와 receipt/plan schema 2, root/payload/authority 보존을 확인한다. 이 child program은 새 test module 안의 고정 문자열로 식별한다. 경로·target·canonical request 외 임의 code/command 입력은 받지 않는다. OLD 기존 test seam 실행이며 uninstrumented CLI/power-loss 증거가 아니다. 실제 bytes와 command digest는 P1a authoring 결과 리뷰에서 고정한다. 다른 old-source prefix나 arbitrary old artifact를 대체하지 않는다.

Schema1 구조 fixture는 `planning-1`, exact literal old 29-member set으로 고정한다. Production builder/verifier를 fixture 생성 oracle로 import하지 않는다. 각 payload는 stdlib로 결정적으로 만드는 `synthetic planning-1 fixture: <path>\n` bytes이며, launcher만 유효한 Python 선언 `WORKSPACE_INVENTORY_ID = "planning-1"\n`으로 만든다. root hv2와 payload/hv2 bytes를 같게 하고 launcher 0755/기타 regular 0644로 고정한다. Synthetic inventory의 canonical JSON bytes에서 digest와 `product-release-<first24>`를 계산한다. 이 fixture는 실행 가능한 역사 제품이 아니며 historical release/source 확보의 증거가 아니다.

독립 literal schema1 init/binding/receipt와 detach plan/receipt를 원래 schema field contract에 맞춰 구성한다. 서로를 가리키는 canonical digest, format/authority/target identity, exact remove/preserve membership, root-hv2-first 후 UTF-8 삭제 suffix를 독립 계산한다. None/boolean/mixed schema, 잘못된 digest/member/suffix 및 colvia 혼합은 거부 사례다. 새 reader와 plain auditor는 이 fixture의 검증 대상이며 생성의 정답을 공급하지 않는다. Schema1 positive/negative와 actual OLD schema2 결과는 별도로 보고한다. 현 complete old source의 schema1 writer를 실행한 것으로 계산하지 않는다.

### C6. 기본 발견 5개 테스트와 P1b/P2 경계

P1b의 paired schema는 reader/shape/identity 판정과 fresh init의 기존 schema1 entry-1 결합을 뜻한다. Schema2 switch와 schema3 detach의 새 publication·복구 writer는 P2다. P1b tree는 검증 중인 부분 구현이며 lifecycle-complete release가 아니다. P1 focused에서는 P2 미구현 동작을 호출하지 않고 미검증으로 남긴다. 실제 실행한 P1 assertions는 전부 PASS해야 하며 예상 실패·skip으로 통과시킬 수 없다. P4 complete는 P1/P2/P3 전체를 포함한다.

| `test_checkout_window_transition`의 default test | 처분 / 귀속 | 완료 시 기대 assertion |
| --- | --- | --- |
| `CheckoutWindowTests.test_current_source_declares_checkout_window_with_same_membership` | migrate / P1b | entry-1 + new literal ENTRY_MANAGED_PATHS 29개 + 실제 source의 새 launcher/adapter 경로 일치. old literal 집합 자체도 별도 보존 확인 |
| `CheckoutWindowTests.test_old_and_unknown_source_declarations_are_not_current_candidates` | migrate + duplicate reader positive / P1b | current candidate parsing은 checkout-1을 포함한 old/unknown 선언 거부; explicit historical reader의 지원 old 선언은 그대로 판독 |
| `DetachVersionTests.test_paired_version_reader_and_independent_auditor_reject_invalid_versions` | migrate + duplicate old-reader / P2 | new plan/receipt 3/3 positive, 1/3·2/3·3/1·3/2·4/4·boolean 거부. 3/3을 기존 음성 목록에 남기지 않음. old 1/1·2/2 reader 및 new-source write refusal는 독립 fixture에서 검증 |
| `DetachVersionTests.test_older_synthetic_predecessors_refuse_preview_and_apply_before_writes` | migrate / P2 | 실제 허용된 exact checkout-1→entry-1과 same-entry-1 control 이외 predecessor/window/digest 거부. synthetic observation seam과 actual OLD 검증을 분리하고 무변경 단언 유지 |
| `DetachVersionTests.test_legacy_version_is_read_only_for_new_source` | migrate + duplicate / P2 | independently constructed schema1 + actual OLD schema2 prefix를 새 reader가 읽고 새 writer가 거부. new schema3 receipt의 version 숫자만 바꿔 old fixture라고 하지 않음 |

Historically generated `make_exact_suite` 20건과 그 내부 SHA-only calls(182/185/370/382/395/402행)는 entry-1 candidate API 대상으로 실행하지 않는다. 후보에 남긴 함수는 historical code이며 current executor가 아니다. 실제 구 factory 사용이 필요하면 고정 OLD source의 원래 code/환경/승인 범위에서 수행한다. 새 runner는 새 entry factory만 호출한다. Default 5건 변경이 그 20건의 통과나 교체를 뜻하지 않는다.

`SERIAL_MANAGED_PATHS`는 frozen old 29 paths로 남긴다. `UMBRELLA_MANAGED_PATHS`(28)와 `LEGACY_MANAGED_PATHS`(27)도 새 집합에서 빼서 만들지 않고 독립 literal old tuples로 고정한다. 새 `ENTRY_MANAGED_PATHS`는 colvia와 새 adapter를 가진 literal 29개다. window→paths/launcher/adapter는 이 집합을 명시적으로 선택한다. Current source/candidate fixture의 `SERIAL_MANAGED_PATHS` 소비는 ENTRY로 migrate하되, old fixture/reader/factory 소비는 old 의미를 유지한다. Plain auditor는 production 상수를 import하지 않고 자기 literal 집합을 보유한다.

P1b의 실제 candidate membership 검사를 위해 root launcher rename뿐 아니라 adapter의 물리적 경로도 `adapters/colvia-work/SKILL.md`로 옮겨야 한다. 이는 전체 C1/C2 범위 안의 포장 선행 조건을 P1b에 명시한 제안이다. Current instruction 내용의 일관성은 P3가 완성하며, 그 전의 managed candidate를 사용자에게 설치하거나 배포하지 않는다. 이 경로 이동 역시 이번 문서 보정에서는 수행하지 않았다.

### C7. 추가 caller·literal 처분

| source 경계 | 귀속 / 처분 |
| --- | --- |
| `work._runtime`, `_umbrella_runtime`, `_allows_unchanged_crlf` | P1b: current entry-1 identity/capability 추가, SHA non-null missing-window refusal. 두 필드 SHA None record-only seam 외에 production fallback 없음 |
| `product.require_workspace_runtime`와 `cli.workspace_run:223` | P1b: 실제 bound launcher/module proof가 entry-1을 사용하도록 정렬. `cli`의 ordinary writer pre-gate는 유지 |
| `product` runtime gate call sites 713/792/803/1146/1228/1243 | P2 lifecycle preview/apply/recovery의 소비 지점으로 표기. 호출 제거·source 우회는 하지 않음. P1b verifier 변경만으로 해당 lifecycle의 qualification을 주장하지 않음 |
| `view`의 proof 전달과 collision rendering | identity 전달은 P1b, collision observation/rendering·consumer 문안은 P2/P3. fresh fallback 경로 유지, render field allowlist와 안정성 재관측에 새 derived fields 반영 |
| `test_productization_safety` embedded launcher 107–159 및 installed helper | P1b: `WORKSPACE_INVENTORY_ID`, root/payload 경로와 snapshot identity를 함께 migrate. historical fixture는 old 의미 유지 |
| `installed()`류 helper, root/payload 문자열, managed-path 상수 | 추가 literal scan의 file/line/enclosing function으로 분류. current fixture→migrate, explicit old fixture/retired-entry negative→keep, new/old 대비→duplicate. internal hv2ref/HV2-/historical prose는 rename 대상 아님 |

새 packet은 39개 Python 입력과 root launcher를 대상으로 standalone hv2, payload/hv2, inventory declaration, managed-path 상수의 문자 위치를 첨부한다. 이는 0건 검색을 완료 조건으로 삼는 작업이 아니며 code 생성 문자열·동적 호출 전체의 완전성을 증명하지 않는다. 기존 AST import/call 목록과 actual candidate의 후속 collection/검증을 함께 사용한다.

### C8. controls 변경과 재검증의 실행 경계

`controller.completed()`는 기존 acquire/canary/smoke의 controls/runtime/Git/config identity가 현재 invocation과 같아야 한다. Runner·observer가 바뀌면 r01의 base PASS를 새 controls의 선행 증거로 재사용할 수 없다. 이 검사를 완화하거나 기존 receipt를 고쳐 맞추지 않는다.

P1a authoring 제안 파일은 새 test module, `runner.py`, `observer.py`, `prefix-oracle.json`, controls README 및 이 작업 기록이다. 추가로 controller의 collection/focused slot을 구분할 필요가 발견됐다. 제안은 `collect-p1-controls`와 `focused-p1-controls` 두 이름만 enum/allowlist에 추가해 P1a synthetic 검증이 기존 `p1`(P1b) 슬롯을 소비하지 않게 하는 것이다. 또 현재 collection 중복 방지는 `(source_digest, controls)`만 비교하므로 동일 P1a source의 base collection 뒤 entry collection을 거부한다. 새 root의 parent `inputs.json`에 이미 검증한 `phase`를 명시하고 중복 key를 `(source_digest, controls, phase)`로 한정하는 변경도 함께 제안한다. 같은 source/controls/phase의 재시도 금지는 유지하며, phase가 없는 old receipt를 추정하거나 수정해 재사용하지 않는다. Mode와 per-run timeout은 그대로다. 이 두 slot과 phase별 collection 구분을 위한 controller 변경은 앞선 한 파일 authoring 계획에 없던 명시적 승인 대상이며, 이번에 실제 적용하지 않는다. `common.py`, `canary.py`, `acquire.py`, baseline/seeds, 두 Seatbelt policy는 변경하지 않는 것을 기본으로 둔다. 구현 중 그 범위로 확대해야 하면 중단하고 정확한 이유와 변경안을 제시한다.

새 controls를 검증할 때의 제안 순서는 다음과 같다. Exact inputs와 root 이름은 실제 bytes가 생긴 뒤 승인할 execution supplement에 고정한다.

1. 별도 새 non-Git verification root에서 corrected controls로 base acquire/canary/collect/smoke를 각각 한 번 수행한다. P1a 단계의 product source는 아직 checkout-1이고 새 module의 factory-only class는 default discovery에 나오지 않는다. 기존 fixed 20 seed의 실제 occurrence를 그대로 검증한다. Old r01 root/receipt는 수정·재사용하지 않는다.
2. 같은 controls identity와 exact P1a source로 entry `collect p1-controls`를 한 번 수행한다. Factory ID set과 default overlap, missing/empty rejection, deterministic collection을 확인하고 digest를 고정한다. 별도 selection에는 context/loader contract, pause handshake·timeout·wrong-token·fd witness·cleanup, independent fixture construction 등 synthetic control assertions만 넣는다. 미구현 entry product assertion은 선택하지 않는다.
3. `focused p1-controls` 한 번을 실행한다. Actual child commands, runtime, environment, WORK 경계 및 exact IDs/selection digest는 그 전에 실제 바이트로 검토한다. 결과 R1과 Driver disposition 및 Owner 수락 후에야 P1b에 진입한다. Product S1–S6/late-writer 결과는 이 synthetic PASS에 포함하지 않는다.

이 control-revalidation 제안의 상한은 acquire/canary/base collect 각 300초, base smoke 1,200초, entry-control collect 300초, entry-control focused 1,200초로 합계 최대 3,600초이며 각각 1회, 자동 correction/retry는 0회다. 아직 실행 승인이 아니고 기존 base 2/4·diagnostic 2/2·review 소비량을 초기화하지 않는다. 기존 product collection 최대 8회와 P1/P2/P3 focused 예산에 이 두 새 control collection을 숨겨 넣지 않는다. 별도 명명된 2회 control collection을 추가하는 제안이므로 실행 승인 때 총 ledger와 기존 baseline 포함 관계를 함께 고정한다. P1b 이후 같은 controls가 유지되는 경우에만 기존 completed checks를 통과할 수 있으며, SOURCE bytes/root map/selection은 매번 별도 식별한다.

새 controls 작성 전 R0, 실제 bytes의 결과 검토와 실행계획 R0, 실행 뒤 R1 및 Owner 수락을 구분한다. 이들의 결합이나 면제는 Driver가 결정하지 않는다. 이번 문서 보정은 어떤 리뷰·실행 budget도 사용하지 않는다. Runnable exact hash/ID가 아직 없는 상태를 execution-ready라고 표시하지 않는다.

### C9. P1b 진입 조건과 보정 추적

P1b 전에 필요한 조건은 (1) 한정된 P0 base 결과의 Owner 수락, (2) C1 exact amendment의 Owner 설계 수락, 특히 init mapping을 처음 건드리기 전 D2-A 수락, (3) 수정된 P1a scope와 control interface 검토·실행 승인, actual-byte/실행 결과 검토와 Owner 수락, (4) 위 default-test 단계·symbol/caller 목록과 exact P1 focused 입력 고정이다. D1/D2 draft tests는 설계가 수락되기 전까지 pending-contract draft이며, 테스트 작성이나 실행 결과로 정책을 승인하지 않는다. P1b source 작성과 P4 normative activation도 별도 승인 범위로 유지한다.

P1a authoring 승인안에도 기존 한정 base 결과의 Owner 수락 여부를 명시한다. 준비·리뷰를 계속하라는 말만으로 P0c의 Owner gate를 넘겼다고 기록하지 않는다. 실제 P1a authoring의 제안 상한은 기존 60분·후보 1회이며, 늘어난 명시적 파일 범위를 그 안에서 완성할 수 없으면 현 상태와 남은 범위를 보존하고 중단한다. 이번 문서 보정의 45분 한도와 후속 authoring/실행 한도는 별개다.

| R0 finding | 현재 보정 위치 | 남은 증거/결정 |
| --- | --- | --- |
| B1 | C1/C2/C9 | exact recovery 문안과 D2-A 설계 Owner 수락 |
| B2 | C1/C2/C7; 새 packet의 CLI/view 원문 | command별 검토 및 actual consumer tests. 기존 fresh-read fallback을 유지한다는 defend 근거 재검토 |
| B3 | C4/C8; guard/jsonio/launcher 원문 | pause 실제 bytes와 synthetic witness, 이후 P2 old-writer 관측 |
| B4 | C3/C5/C8; runner/common/observer 원문 | context와 OLD child 실제 bytes의 검토·고정 실행 |
| B5 | C6/C7 | 다섯 test의 actual migration과 P1/P2 complete assertion |
| N1/N2/N3/N11 | C6/C7 및 literal scan | candidate의 변경 후 closure와 collection 대조 |
| N4/N5/N6/N7/N12 | C1/C2/C9 | 명시한 추가 정책과 정확한 English 문안 수락 |
| N8/N9/N10 | C3/C5/C8 | factory multiplicity·fixture·budget과 리뷰의 actual 검증 |

이번 준비의 완료 기준은 exact English amendment, 명령·소비자 표, control context/pause 계약, old fixture와 다섯 test의 단계 처분, control 재검증/추가 slot 범위를 한 문서와 식별된 packet으로 검토할 수 있는 것이다. 새 packet은 기존 Reviewer 원문과 Driver 처분, accepted DR, 필요한 source/controls/contract 원문과 발췌·literal scan을 포함한다. 보정된 주장의 직접 근거를 우선하고, omitted source는 hash만으로 검토됐다고 하지 않는다.

다음 제안은 이 보정 packet에 대한 fresh Claude subscription static review 1회, 최대 600초다. 도구·MCP·test 실행·파일 편집 없이 B1–B5/N1–N12의 처분, 추가 controller slot/phase별 collection 구분/base 재검증 범위와 남은 승인 조건을 확인한다. 현재 호출은 하지 않았다. 이전 P1-R0 1/1회 권한과 old base bundle의 잔여 allowance를 재사용하지 않는다. Owner가 새 packet의 전송을 승인하면 실제 auth/model/session, 응답 원문과 Driver 처분을 이 기록에 이어 남긴다.

### 보정 결과와 보존 확인

허용된 문서 보정 후보 1회를 작성했다. C1–C9는 현재 검토 제안이며 R0 차단 해소 판정, exact amendment 수락, P1a authoring 승인 또는 실행 준비 완료가 아니다. 기존 P1-R0 응답 원문과 처분 및 검토 당시 준비안은 그대로 보존했다. 현재 제안의 우선순위는 이 correction 절에 한정한다.

정적 확인은 GFM 렌더링의 코드 밖 literal emphasis, 기존 local link 목적지, 문서 whitespace, base revision과 source 118개 파일의 bytes/mode 대조 및 readback으로 한정했다. 변경 파일은 이 작업 기록 1개이고 다른 117개 source 입력, Accepted DR-0004, 제품·tests·controls·Development Index는 동일하다. Test import/collection/execution, reviewer 호출, Git 상태 변경 명령, 새 execution root 생성은 하지 않았다. Static literal/AST 검사는 Python 구문을 데이터로 읽은 결과이며 테스트 실행 증거가 아니다.

현재 packet과 전체 기록 사본 및 input identity는 기존 private bundle의 `p1-preparation/correction-01/`에 둔다. Identity에는 base/tracked diff digest, source bytes/modes, packet에 실제 포함한 file/line 범위, 추가 scan 범위와 packet SHA-256을 기록한다. 원래 `p1-preparation`과 `review-01` 입력은 변경하지 않았다. Packet에서 빠진 입력은 검토한 것으로 주장하지 않는다.

보존 대상의 소비자는 후속 R0 Reviewer와 Owner 및 그 수락 뒤 P1a의 exact-input handoff다. 새 packet을 대체하거나 이 입력을 명시한 다음 단계가 필요한 bytes를 다른 durable custody로 확보할 때까지 보존한다. 한 번 사용한 render/check 출력과 작성 script는 재생성 가능하므로 영구 산출물에 넣지 않는다. Source worktree와 이전 verification/diagnostic root는 base Owner 수락 및 실제 후속 사용 판단이 남아 있어 유지한다. 이번 준비 완료만으로 삭제 가능한 checkout은 없다.

## P1 Correction R0 Review — 2026-10-10

### Authorization, Input And Execution

Owner는 correction-01 packet에 대한 fresh Claude 정적 재검토 1회·최대 600초 제안에 “진행해”라고 답했다. 이 승인은 해당 전송·응답 확인·기존 기록의 Reviewer 원문과 Driver 처분 기록에 한정된다. Correction-01 문안의 추가 수정, P0 base 결과/정책 수락, product/test/control 작성, 실행·활성화 또는 Git 작업 승인이 아니다.

실행 직전 인증은 `loggedIn=true`, `authMethod=claude.ai`, `apiProvider=firstParty`, `subscriptionType=pro`였다. 실제 Reviewer는 Claude Opus 5.5 (`claude-opus-5-5`), fresh session `efd2fbfc-c50d-4861-af2f-49e38380a10a`이다. 이전 리뷰와 다른 session이지만 같은 model 계열이며 이전 응답·Driver 처분을 packet으로 읽었으므로 맥락 독립성이 완전하다고 하지 않는다. 모델 fallback이나 추가 호출은 없었다.

- Base revision: `238514686078ce1564010a7b69013f48a635c57c`; tracked binary diff SHA-256: `12238ddc334c4a6971d657249732a73d59cc4c3e32b6463d5a7fccfc867a6b04`.
- Exact packet: 648,088 bytes, SHA-256 `0327ed6c1f30c340026b1f78b7f386dac1fa963f0beb0a709fdadbdb497c26ea`.
- Reviewed current task SHA-256: `3ddefc39f0e7b5f6e76c8a4bacc704b29e4169894a8ab501d5798f818a73e6fc`; input identity SHA-256: `5e4682f756669a354a711e53a5a54e1da17dccd39e65edda99acd038eb0af63c`. 이 결과 절은 리뷰 입력에 없었다. Untracked task/DR/controls 등 diff 밖 입력은 해당 identity의 `untracked_inputs`와 bytes/mode map에 별도로 식별됐다.
- 명령은 보존한 `authorization.json`의 argv 그대로이며 `claude -p --model opus --effort medium`, no-tool/MCP/restricted 설정, `--setting-sources ""`, `--permission-mode dontAsk`, no-session-persistence와 stream-json을 사용했다. Exact packet을 stdin으로 전달했고 cwd는 새 private `correction-01/review-01`이었다. Reviewed code/test command는 하나도 실행하지 않았다.
- 소요 287.71초, exit 0, timeout/error 없음, final response 수신. Startup tools/MCP는 모두 빈 배열, tool use 0건, stderr 0 bytes. 종료 후 process group 부재를 확인했다.
- 전후 입력 검사 PASS: source 118개 bytes/modes·membership, base/tracked diff, packet/record-copy/identity가 동일했다. 이 호출의 1/1회 권한은 소진됐으며 자동 재호출하지 않는다.

Reviewer의 “조건부 통과”에는 새 차단 2건이 포함된다. 따라서 Driver의 운영 결론은 R0 closure 보류다. 기존 B3/B4/B5 및 대부분 N 항목은 계획 수준에서 해소됐지만 C1 exact 수락이나 P1a 작성에 바로 들어갈 수는 없다. 아래 판정은 정적 추론이며 테스트 재현 결과가 아니다.

### P1 Correction Reviewer Response — Verbatim

````text
# P1 준비 보정안(correction-01) R0 정적 검토

## 판정

**조건부 통과입니다. 새 차단 2건을 문서에서 고치기 전에는 C1 수락 요청이나 P1a 작성 승인의 근거로 쓰기 어렵습니다.**

- B3, B4, B5와 N1–N12는 계획 수준에서 해소됐거나 비차단 잔여만 남았습니다.
- B1, B2는 방향과 근거가 해소됐지만, C1 English 문안에 새 결함(NB-1)이 있어 그 문안 그대로는 수락 대상이 될 수 없습니다.
- C8의 재검증 계획은 P1a 단계까지만 성립하고, 그 뒤 controls가 바뀌는 경우의 경로가 없습니다(NB-2).
- B2의 공유 graph 반환 계약과 N8의 duplicates 처방에 대한 Driver의 defend/revise는 제공된 source로 확인되어 받아들입니다.

이 보고는 Reviewer 소견입니다. Owner의 정책 수락, 실행 승인, 활성화를 대신하지 않습니다.

## 증거 한계

모든 판단은 제공된 바이트의 정적 판독이며, 실행·재현 증거는 없습니다.

- **읽지 못한 것**(해시만으로 검토했다고 보지 않습니다):
  - `workspace.py` 113–474행(`inspect_root`, `classify_target`, `bootstrap_root`, `_root_aliases`, `_durable_directory`)
  - `work.py`의 대부분(`_visible_truth`, `_regular_files` 포함)
  - `view.py`의 `_product`, `_work`, `_worker_inspection`
  - `intent.py`, `candidates.py`, 대부분의 test 본문
  - private invocation과 `c["controls"]`의 실제 구성원, DR-0002/0003, C0 appendix
- **확인하지 못한 수치**: 기존 중복 ID 177개, literal 205건, call 283개는 다시 세지 않았습니다.
- **독립성 한계**: 이전 Reviewer와 같은 model 계열이고, packet에 이전 응답과 Driver 처분이 들어 있습니다.

## 차단 항목

### NB-1. C1의 collision 정의에 적용 범위가 없어 전환 자체를 거부하게 읽힙니다

- **근거**:
  - C1 Collision observation은 "the presence of an immediate target-root entry whose name … equals `hv2`"로만 정의합니다.
  - Lifecycle refusal은 "On supported new-runtime lifecycle paths, a detected retired-entry collision refuses init replay/recovery, **update**, rollback, repair and detach"입니다.
  - entry-1 한정어("otherwise valid entry-1 product/binding")는 D1-A diagnostics 문단에만 있습니다.
- **문제**:
  - DR-0004 Durable Switch Sequence에서 S0–S4의 root `hv2`는 관리 대상 O입니다.
  - S5에서는 "If interruption leaves O visible again, re-observe S4 and repeat the same exact retirement"가 허용됩니다.
  - 문자 그대로면 checkout-1→entry-1 update와 S1–S5 exact recovery가 모두 65로 거부됩니다. 서두의 "does not change the S1 one-way boundary … admitted predecessor"와 모순됩니다.
- **최소 교정**: Collision observation에 한 문장을 추가합니다.
  - 적용 대상: 검증된 현재 binding이 entry-1(B1)인 target, fresh entry-1 init, incomplete entry-1 init.
  - 제외 대상: checkout-1 binding의 exact O와 DR-0004 physical-prefix 표의 S1–S5 `hv2`. 이들은 그 표가 계속 규율합니다.
- **함께 고칠 것**: 완료된 update replay의 거부는 Durable Switch Sequence S6 행("idempotent replay observes current")과 Admission의 "For completed execution or historical replay" 문단에도 닿습니다. named clause 목록에 추가하거나 "collision 중에만 보충"이라고 명시해야 합니다(CONTRIBUTING: "Later changes name the clauses they amend").

### NB-2. P1b 이후 controls가 바뀌면 base 재검증을 할 방법이 없습니다

- **근거**:
  - `controller.completed()`는 `inputs[key] == c[key]`(controls 포함)를 요구합니다.
  - `positive_boundary_controls`와 `canary.boundary_probes`는 `p["source"] / "hv2"`를 고정 probe로 씁니다.
  - `base-seed-ids.json`의 seed는 checkout-1을 단언합니다(예: `test_current_source_declares_checkout_window_with_same_membership`).
- **문제**:
  - base acquire/canary/collect/smoke는 SOURCE가 checkout-1인 P1a 시점에만 통과할 수 있습니다.
  - C8은 "P1b 이후 같은 controls가 유지되는 경우에만"이라고만 하고, 유지되지 않을 때의 경로를 정하지 않았습니다.
  - C4는 pause shape를 `timeout_seconds: 15`로 닫았습니다. 실제 old writer는 bootstrap 검증, `require_workspace_runtime`의 이중 관측, Git snapshot을 거쳐야 flock에 도달합니다. 기존 test의 subprocess 상한은 45초입니다.
  - P2에서 15초가 부족하면 `observer.py`를 고쳐야 하고, 그러면 controls 변경 → base 재실행 필요 → 현 canary/seed로는 불가능한 막힌 경로가 됩니다.
  - `prefix-oracle.json`이 controls map의 구성원이면 P2의 oracle 수정도 같은 결과를 냅니다. invocation이 없어 구성원 여부는 확인하지 못했습니다.
- **최소 교정**: C8에 문단 하나를 추가합니다.
  - P1a controls는 P2/P3까지 쓸 최종 형태로 동결한다고 선언합니다.
  - pause timeout은 P2 product 경로를 감안한 고정값이나 닫힌 상한 범위로 지금 정합니다.
  - 동결 뒤 controls 변경이 불가피할 때의 유일한 경로를 미리 적습니다. 예: 보존한 checkout-1 SOURCE snapshot에 대한 base 재검증(`completed()`는 `same_source=False`), 또는 Owner 재승인 대상인 canary/seed 변경.
  - pause와 `fault`를 한 scenario에서 함께 쓸 수 있는지도 같이 닫습니다. late-writer 4단계가 "사전 검토된 kill fault"를 전제합니다.

## B1–B5 해소 여부

| ID | 판정 | 확인 근거와 잔여 |
| --- | --- | --- |
| B1 | 해소 (NB-1 조건) | C9가 init mapping 전 D2-A 수락을 조건으로 둡니다. `workspace_init_apply`가 preflight를 `bootstrap_root`와 `writer_guard`보다 먼저 호출하므로 "initial check 시 target 변경 0"은 구조적으로 가능합니다. |
| B2 | 해소 (NB-1 조건) | `cli.main:140–166`의 conflict→12, ContractError→65를 확인했습니다. `view._observe:214–221`은 conflict에서 `WorkStore(target)._all()`을 새로 읽으므로 Driver의 defend가 맞습니다. installed parser에 init/repair가 없는 것도 확인했습니다. |
| B3 | 해소 | `jsonio.exclusive_file_lock`은 `fcntl.flock(fd, fcntl.LOCK_EX)` 속성 호출이라 observer의 module-level patch가 잡습니다. launcher는 re-exec하지 않습니다. 새 실행자 소유와 `lock-acquired` 직후 pause는 guard 순서를 바꾸지 않습니다. 실제 witness는 P1a(synthetic)와 P2(product) 증거로 남습니다. |
| B4 | 해소 | `common.python_command`가 고정 prefix를 반환합니다. runner의 `out`은 controller가 넘긴 `work`입니다. OLD의 `inject_at="after-receipt"` seam은 base에 실재합니다. |
| B5 | 해소 | 5건의 단계·처분, `make_exact_suite`의 역사 코드 라벨, 독립 literal symbol 계획이 있습니다. 잔여는 아래 R5, R6입니다. |

## N1–N12 해소 여부

- **해소**: N1, N2, N4, N5, N6, N7, N9, N10, N11.
- **N3 부분 해소**: hv2 literal scan은 있지만 adapter 경로 literal은 scan 대상이 아닙니다(R5).
- **N8 해소**: Driver의 revise를 받아들입니다. runner는 `duplicates`를 기록만 하고, 기존 default 중복을 없애라는 요구는 discovery 변경이 됩니다.
- **N12 대체로 해소**: 문장 간 긴장이 남습니다(R2).

## 비차단 잔여 (P1a 실제 바이트 검토 전 반영 권장)

| # | 항목 | 근거 | 최소 교정 |
| --- | --- | --- | --- |
| R1 | repair에는 profile이 없음 | C2는 "independent source의 lifecycle은 명시적 source profile을 요구"라고 하지만 `cli.run`은 repair를 profile 검사 전에 분기하고 parser에 `--profile`이 없습니다 | C2 표에 repair 예외를 적습니다 |
| R2 | recovery의 scratch 문장 | 재개 흐름은 initial preflight → (partial-candidate면) `bootstrap_root` → guard → 재관측입니다. "The only new scratch differences …" 문장이 guard 전 bootstrap 쓰기와 충돌하게 읽힙니다 | 두 경우로 나눕니다. 초기 감지는 lock 포함 변경 0, 사후 감지는 감지 전 완료된 exact-recovery 단계와 lock anchor만 |
| R3 | 완료된 detach replay | detach 완료 뒤에는 binding이 없어 "observe and preserve the current binding/history", "Use status/doctor/view"가 맞지 않습니다 | detached 상태의 결과를 한 문장으로 정합니다 |
| R4 | `conflict` 분류의 기존 의미 | `workspace_status`는 `root["classification"]`을 그대로 통과시킵니다. `inspect_root`가 이미 `conflict`를 내는지는 미제공 구간입니다 | 기존 의미가 있으면 소비자가 `retired_entry_collision` 필드로 구분한다고 C2에 적습니다 |
| R5 | adapter 경로 literal | C6가 물리 rename을 P1b로 당겼습니다. `view.render_view`의 `"/adapters/harness-v2-work/SKILL.md"`, `product.py`의 managed tuple, auditor `SERIAL_PATHS`가 같은 literal을 씁니다 | `harness-v2-work` literal scan을 추가하고 view의 해당 줄을 P1b 귀속으로 적습니다 |
| R6 | init replay 거부의 단계 | Lifecycle refusal의 init replay는 P1b가 건드리는 `_workspace_init_preflight`의 "complete" 경로이지만, C7은 collision behavior를 P2/P3로 둡니다 | init replay와 recovery의 collision 거부를 P1b로 귀속하거나 명시적으로 미룹니다 |
| R7 | mode-slot allowlist의 출처 | observer가 WORK 구조를 allowlist로 확인하는데 목록은 `controller.py`에만 있고 `common.py`는 불변 기본값입니다 | 단일 출처(예: `controller`에서 import)나 교차 검증 test를 지정합니다 |
| R8 | OLD schema2 prefix의 실행 단계 | C5는 생성 수단만 정했습니다. C8 2단계 선택 목록에는 없고, 선행 OLD init 호출도 적혀 있지 않습니다 | `focused p1-controls`에 포함하는지와 init→preview→apply 순서를 적습니다. OLD CLI의 숨은 `--inject-at after-receipt`(exit 75)가 고정 code 문자열보다 CLI에 가까운 대안입니다 |
| R9 | P1b 중간 tree의 범위 | 5건 외에도 switch/repair/detach를 쓰는 default test 다수가 P2 전까지 깨집니다(예: `_detach_preview_plan`의 checkout-1 요구) | "P1 focused는 exact ID만, 나머지는 미검증"이 이 파일 5건만의 규칙이 아님을 한 줄로 적습니다 |
| R10 | DR-0004 status 표시 | `Accepted (Amended)` 기록을 append할 때 frontmatter `status`와 CONTRIBUTING 표의 갱신 여부가 없습니다 | 표시 계획을 한 문장으로 추가합니다 |

## 영역별 확인

- **execution_context와 bootstrap**: 필드 6개의 출처가 모두 검증된 `c`, `p`, `INPUT`, `out`에서 나옵니다. `-I -S -B -c BOOTSTRAP CONTROLS observer.py` 형태가 유지되어 `require_isolated()`와 맞습니다. 다른 run의 WORK 차단은 `test.sb`의 `subpath WORK` 읽기 제한에 기대는데, 이 정책의 실효는 실행 증거 영역입니다.
- **old fixture 독립성**: planning-1 + schema1 조합은 MAINTAINING의 "Readers retain schema 1"과 맞습니다. launcher 선언은 `_launcher_inventory_window(allow_legacy=True)`가 받는 형태입니다. production builder를 oracle로 쓰지 않는다는 계획과 "synthetic" 라벨이 일관됩니다.
- **controller slot과 phase key**: 현 중복 검사가 `(source_digest, controls)`만 비교해 base 뒤 entry collection을 거부한다는 진단은 `controller.run`과 일치합니다. `allowed()`에 `p1-controls`를 더하는 변경과 예산 합계 3,600초(300×3 + 1,200 + 300 + 1,200)도 맞습니다. P1a 범위에서는 계획이 성립합니다.

## Owner 결정 사항 (Reviewer가 대신할 수 없음)

1. 한정된 P0 base 결과의 수락 여부.
2. NB-1 교정 뒤 C1 exact revision의 수락. 기존 C0-H-A에 없던 추가 정책은 다음과 같습니다.
   - D1의 alias 포함과 `observed_names`
   - `conflict`/12 선택
   - incomplete-init recovery의 거부
   - 완료된 lifecycle replay의 현재 거부
   - lock scratch 예외
3. 확대된 P1a 범위: `controller.py` 변경(slot 2개, phase key, `inputs.json`의 phase), runner interface 인자, observer pause. 60분·후보 1회 상한이 이 범위에 현실적인지도 포함합니다.
4. adapter 물리 경로를 P1b에서 옮기는 것. M3는 활성화 전까지 옛 경로를 규범 구성원으로 둡니다.
5. controls 재검증 실행: 새 root, 최대 3,600초, collection ledger, 미사용 r02/r03의 처분.
6. NB-2의 controls 동결 정책과 pause timeout 값.
7. 실제 바이트 R0, 실행 계획 R0, R1의 결합이나 면제 여부.
````

### P1 Correction Driver Dispositions

Reviewer 응답 뒤의 추가 source 확인은 Driver만 수행했다. 그 source를 Reviewer가 읽은 것으로 소급하지 않는다. Correction-01 본문/packet과 Accepted DR-0004는 그대로 두고 후속 보정 범위만 아래에 기록한다.

| ID | 처분 | 근거와 다음 보정 범위 |
| --- | --- | --- |
| NB-1 | accept / needs-user | C1의 collision 정의가 binding/window/prefix와 연결되지 않은 것은 실제 문안 결함이다. DR-0004의 S0–S5 exact O와 forward recovery를 retired unowned occupant로 분류하면 안 된다. Entry-1의 verified current binding, fresh/incomplete entry-1 init과 그 전의 checkout-1→entry-1 prefix를 명시적으로 구분하는 다음 문안을 준비한다. 완료 update replay의 collision 보충은 Admission의 completed/historical replay 문단과 Durable Switch Sequence S6 행도 named amendment 대상으로 추가해야 한다. 이번 검토로 정책을 수락하거나 수정하지 않았다 |
| NB-2 | accept; timeout 인과는 revise | Controls identity가 달라지면 기존 base 증거를 재사용할 수 없고 현 canary의 SOURCE/hv2·checkout-1 seed로 entry-1 source에서 같은 base를 실행할 수 없다는 경로 공백을 수용한다. Driver가 기존 `attempt-01/private-invocation-base.json`과 smoke invocation의 controls map을 확인했으며 `prefix-oracle.json`도 포함된다. 다만 45초 subprocess 상한은 실제 flock 도달 시간이 15초를 넘는다는 실행 증거가 아니다. 후속 보정에서는 P1a controls의 동결 범위, pause/fault 병용과 닫힌 시간 예산, 불가피한 변경 시 별도 승인·검토 후 보존된 checkout-1 입력으로 새 root에서 base를 다시 검증하는 경로를 구체화한다. 아직 source snapshot을 새로 만들거나 canary/seed를 바꾸지 않는다 |
| R1 | accept | `cli.run:109–113`은 repair를 source-profile 검사 전에 분기한다. C2의 일반화에서 repair 예외를 명시해야 한다. Installed에 repair를 새로 추가하지 않는다 |
| R2 | accept | `workspace_init_apply:521–528`은 initial preflight 뒤 partial-candidate bootstrap을 수행하고 guard 안에서 다시 검사한다. Driver가 `workspace.bootstrap_root:405–468`을 추가로 읽어 root primitives 쓰기를 확인했다. 초기 충돌의 변경 0과, 뒤늦은 충돌 감지 전 정상적으로 수행한 exact bootstrap/prefix 및 기존 lock scratch를 분리하는 문안이 필요하다. 감지 후 publication 금지와 기존 bytes 보존은 유지한다 |
| R3 | accept / needs-user | `workspace_detach_apply:1230–1240`의 완료 detached replay는 `.hrn/detached.json`에서 관측하며 active binding이 없는 상태다. C1의 current-binding 일반화를 제거하고 completed detach의 현재 관측/거부 조건을 별도 명시해야 한다. 다른 정책을 리뷰 결과만으로 결정하지 않는다 |
| R4 | revise | Driver가 추가로 읽은 `inspect_root:286–340`에는 conflict 반환이 없다. 따라서 현재 root conflict와 이미 충돌한다고 단정하지 않는다. 그래도 consumer가 exit/classification 하나만으로 retired-entry라고 판단하지 않고 `retired_entry_collision` 필드와 verified binding을 함께 확인하도록 명시하는 보완은 수용한다. 모든 non-pass 우선은 유지한다 |
| R5 | accept | `view.render_view:570`, product managed tuple과 plain auditor literal에 old adapter 경로가 남는다. 다음 packet에 `harness-v2-work`/`colvia-work` literal scan을 추가하고 현재 adapter 표시 경로를 P1b로 귀속한다. Historical old tuple/fixture는 보존한다. Current source의 전체 문안 coherence(P3)와 물리 membership(P1b)을 구분한다 |
| R6 | accept | Init complete/recovery preflight와 현재의 P2/P3 collision 표현 사이 단계 공백이 있다. P1b에서 fresh init을 다루는 한 exact init replay/recovery의 충돌 admission도 함께 다루거나, 미구현 범위를 명시적으로 분리해야 한다. 후속 계획은 전자를 우선 후보로 구체화하되 D2 exact 수락 전 코드를 바꾸지 않는다 |
| R7 | accept | Observer WORK 검사에서 허용할 run-name 목록과 controller allowed mode/slot 사이의 일치 증거가 필요하다. 다음 보정안에서 한 출처 또는 exact 교차 검증 test를 선택해 닫는다. 이 이유로 `common.py`를 자동으로 변경 범위에 넣지 않는다 |
| R8 | accept; 대안 채택은 보류 | OLD schema2 prefix의 선행 exact OLD init preview/apply → detach preview → after-receipt apply 순서와 `focused p1-controls` 포함 여부를 명시해야 한다. Hidden CLI inject/exit 75 경로는 실제 source에 있으나, 이미 제안한 API seam을 자동 교체할 근거는 아니다. 최소 범위의 고정 API child 유지안을 우선하고 실행 선택/명령은 actual-byte 승인 때 고정한다 |
| R9 | accept | P1 focused의 exact ID selection과 나머지 미검증 원칙은 default 5건만이 아니라 전체 suite에 적용한다. P1b를 full-suite green 또는 lifecycle-complete candidate로 주장하지 않는다는 문장을 추가해야 한다 |
| R10 | revise / 일부 defend | 상태 표시 계획의 명시성은 보완한다. 그러나 protected Accepted bytes와 기존 frontmatter를 덮어쓰는 처방은 채택하지 않는다. Named `Accepted (Amended)` append에 exact scope와 이전 header의 역사 의미를 드러내고, 현재 source navigation의 갱신 여부/범위를 별도 승인 대상으로 명시하는 방향이다. 현재 CONTRIBUTING에는 DR-0004 row가 없고 managed 파일이므로 리뷰 명목으로 새 row나 runtime payload 변경을 자동 추가하지 않는다 |

B2의 fresh graph fallback 및 N8의 default multiplicity 처분은 이번 Reviewer가 source를 읽고 수용했다. 이것은 해당 계획 근거의 해소이며 실제 entry-1 view/test 결과는 아니다. B3/B4/B5의 계획상 해소 역시 P1a synthetic 및 P2 product 검증을 면제하지 않는다. 새 controls slot/phase key와 합계 3,600초 제안은 P1a까지만 검토됐고 NB-2의 후속 변경 경로는 아직 닫히지 않았다.

### Result, Next Bounded Proposal And Preservation

이번에 승인된 재검토와 결과 기록을 완료했다. 현 상태는 “기존 핵심 지적 대부분 해소, 새 차단 NB-1/NB-2 미해소”다. C1 exact amendment, P0 base Owner 수락, 확대 P1a authoring/실행, adapter 이동, controls 동결/재검증과 활성화는 여전히 Owner 판단 대상이다. Reviewer가 나열한 Owner 항목은 선택해야 할 의제이며 이번 “진행해”로 수락된 항목이 아니다.

다음 한정 제안은 기존 기록의 correction-02 절과 새 private packet을 작성하는 문서 보정 1회, 최대 45분이다. NB-1의 상태별 충돌 범위와 named clause, NB-2의 controls 동결·pause/fault·변경 후 재검증 경로를 먼저 닫고 R1–R10의 문장/단계/입력 누락을 함께 반영한다. 소비자가 필요한 정확한 checkout-1 입력 보존 방안을 문서로 특정하되, 새 snapshot/root 생성이나 product/test/control 수정은 포함하지 않는다. Accepted bytes, 기존 packet/Reviewer 원문은 보존한다. 추가 reviewer·test 실행은 포함하지 않으며 실행 또는 계약 선택이 필요한 부분은 pending으로 남기고 중단한다. 완료 기준은 이 두 차단과 잔여 처분을 하나의 문안·검토 입력으로 판단할 수 있는 상태다.

이 기록의 GFM 렌더링에서 코드 밖 literal emphasis, 기존 링크 29개, whitespace, source 입력 118개 bytes/modes와 durable copy readback을 확인했다. Source 변경은 이 작업 기록 하나이며 나머지 117개 입력과 Accepted DR/controls/product/tests/index를 보존한다. Current record 사본, authorization과 compact metadata는 private `correction-01/review-01`에 유지한다. 응답 원문은 이 기록에 정확히 옮기고 digest를 확인한 뒤 중복 response transport/빈 stderr/중복 review 파일은 보존하지 않는다. 소비자는 Owner의 correction-02 결정과 다음 exact-input handoff이며, 필요한 고유 bytes가 durable custody에 남을 때까지 current record 사본을 유지한다. 기존 source/verification/diagnostic checkout은 Owner base 수락과 후속 사용이 남아 있어 유지한다.

## P1 Preparation Correction-02 Candidate — 2026-10-10

### 범위와 읽는 순서

Owner는 correction-01 재검토 결과 뒤 문서·packet 보정 1회·최대 45분 제안에 “계속하자”라고 답했다. 이 절과 새 private packet이 그 한정 결과다. 새 Reviewer 호출, test import/collection/execution, product/test/control 수정, Accepted DR 수정, 실행용 SOURCE 복사·snapshot/root 생성은 포함하지 않는다.

현재 제안은 이 correction-02 절을 먼저 읽는다. 아래 English 문안은 correction-01 C1 전체를 교체하는 후보이며, 이후 표는 C2/C4/C6/C7/C8/C9의 지정 부분을 보정한다. 명시적으로 바꾸지 않은 C3의 execution_context·고정 isolated bootstrap·순수 factory/ID 계약과 나머지 fixture·기존 gate는 유지한다. 앞의 준비안, 두 Reviewer 원문과 처분은 역사 입력으로 보존한다. 이 우선순위는 제안 사이에만 적용되며 Accepted DR나 M3를 바꾸지 않는다.

### A. Exact English Amendment Candidate v2

> **Named Amendment: Entry Diagnostics And Fresh-Init Admission (D1-A/D2-A), revision 2.** This amendment supplements the retired-entry paragraph of **Rollback, Proof And Retained Meaning**; the fresh-init row of **Inventory And Version Table**; the applicable new-source/live-entry-1, fresh-init and completed-replay cases of **Source By Target By Operation**; the completed-execution/historical-replay paragraph of **Admission And Quiescence**; the S6 replay cell of **Durable Switch Sequence**; and the retired-entry refusal and observation cases of **Proposed Detach Schema 3 Closure**. The replay supplements apply only when the scoped retired-entry collision below is present. Other replay rules remain in force. This amendment does not change the S1 one-way boundary, the exact S1–S5 forward-recovery rules, T-A torn-write limit, admitted predecessor, local/worker policies, persistent record schemas or authority identities.
>
> **Target-state scope comes before the name check.** This amendment's retired-entry rule applies to (a) a target whose current binding is independently verified to identify entry-1, including supported repair/recovery when live runtime bytes are incomplete; (b) fresh entry-1 init and exact incomplete entry-1 init identified by the entry-1 candidate and exact init request/prefix; and (c) an entry-1 detach operation identified by its verified exact schema-3 plan/receipt and removal/preservation sets, including partial and completed detach with no remaining active binding. Do not infer any of these states from a filename alone. Unsupported, malformed, ambiguous or otherwise invalid identity/prefix evidence retains its existing refusal or unavailable result.
>
> **Managed O during the admitted transition is not a retired-entry collision.** The exact managed `hv2` of the admitted checkout-1 predecessor at S0, and the exact O allowed by DR-0004's S1–S5 physical-prefix table, remain governed by that table. In particular, its S5 re-observation of S4 and exact O retirement remains possible. Do not apply this amendment's unowned-entry refusal to those exact transition paths. This exclusion does not admit a case alias, altered O, unsupported predecessor, unexpected O/N combination, torn bytes or any other unsupported prefix. The original validation and preservation rules still decide those cases.
>
> **Scoped collision observation.** Within an applicable target state, a retired-entry collision is an immediate target-root entry whose name, after Unicode NFC normalization and case folding, equals `hv2`. Enumerate names without following the occupant. Files, directories and symbolic links, including dangling links, are occupants; do not open, execute, rename or delete them to resolve the collision. Alias inclusion and the diagnostic list of observed names are explicit additions, not retrospective claims about C0-H-A. Existing unsafe-path, topology, unsupported, damaged, pending, stale, incompatible, partial and other non-pass outcomes retain their meaning and precedence. Only a complete ordinary live entry-1 observation that would otherwise be `pass` is reclassified by D1-A below.
>
> **D1-A live-entry diagnostics.** For an otherwise valid live entry-1 product/binding and record observation with a scoped collision, supported `status`, `doctor` and `view` paths report `classification: conflict`, exit 12. Retain the verified current product/binding; report `lifecycle_ready: false` and `retired_entry_collision: {path: "hv2", observed_names: [...], ownership: "project", preserved: true}`. `path` is the canonical retired name. `observed_names` contains each colliding immediate-root name once, sorted by UTF-8 bytes. These are derived fields, not persistent state, and are not mandatory on collision-free responses. Human output identifies the actual names and requires a separate operator decision. Consumers distinguish this condition by its derived collision fields and verified entry-1 context, not by exit 12 alone.
>
> Readable Work, intent and candidate content remains available only after fresh graph and stability checks. `view confirmation` may return 12 while displaying the current ticket and independent reader checks; this is not confirmation, readiness or authorization. Ordinary record commands retain their exact-content, pending, reference, binding and ticket rules. They never execute or snapshot-exclude a retired occupant. Only the verified mapped `colvia` entry is managed runtime. A stale result, missing reference or existing acceptance gate is not bypassed.
>
> **Lifecycle refusal and completed live-entry replay.** On supported new-runtime lifecycle paths within the scoped target states, a detected collision refuses init replay/recovery, update, rollback, repair and detach with `HV2-WORKSPACE-PRODUCT`, exit 65, before any further product or authority publication. This includes an exact already-completed live-entry operation: observe and preserve the current product/binding/history, then report the present collision without performing the operation again. The message distinguishes current refusal from historical completion. Never relabel completed history as pending/failed, rewind the binding or repeat its old truth comparison as a new completion claim. The Admission/S6 replay supplement changes only this collision result; all other current-product and historical-comparison limits remain. Unsupported commands, bootstrap failures, invalid profiles/arguments and other preexisting validation failures keep their own diagnostics.
>
> **Entry-1 detach without an active binding.** An exact schema-3 detach prefix remains identified through its verified receipt/plan and exact remaining suffix/preserve set even after binding removal. On a collision, refuse further removal or exact completed-detach replay with `HV2-WORKSPACE-PRODUCT`, exit 65, and preserve the receipt, history, occupant and remaining bytes. Do not invent a current product/binding or reinstall a launcher. Independent-source `status`/`doctor` retain the existing detach diagnostic flow: when the detach evidence otherwise verifies and the scoped collision is the failing condition, report `degraded`, exit 10, with that product error and preservation guidance. Source `view` uses the corresponding existing degraded rendering. Do not call the current target cleanly detached or rewrite its retained receipt/history. For an operation previously established as complete, this is a current refusal, not a rewrite of that historical result; receipt presence alone does not establish completion. Installed observation is unavailable once its managed launcher is removed. Schema-1/2 historical detach readers and their retained-old-source write rules are unchanged, and a historical managed `hv2` is not reclassified under this schema-3 rule.
>
> **D2-A first admission.** Fresh entry-1 init refuses every scoped occupant above. If present at the first admission observation, refuse before any target directory, bootstrap primitive, init plan, receipt, lock or other target write, with `HV2-WORKSPACE-PRODUCT`, exit 65. Existing `colvia` collision, path/topology, Git-index and ignore-policy checks still apply. A missing worktree file does not exempt its index or topology from checks.
>
> **Exact init recovery and late collision.** Exact incomplete entry-1 init checks for the collision before resuming and at each existing under-guard re-observation. Detection at the initial preflight permits no target change. If the initial preflight passed and the occupant appears later, the invocation may already have completed the exact bootstrap/recovery steps allowed by that request; preserve that durable prefix and perform no further product/authority publication after detection. Report those earlier writes as earlier writes, not as a zero-change result or a new scratch exemption. Account separately for the exact `.hrn/locks` directory and empty regular `writer.lock` anchor only where the existing guard contract permits their creation. Do not exempt any other path, replacement or content change, and do not repair a preexisting malformed lock. This is not atomic protection against a non-cooperating path change between observations. Never delete or rename the occupant or prefix to obtain success.
>
> **Acceptance and effect.** Owner design acceptance must identify this exact revision and its named clauses, including the alias/diagnostic, init-recovery and completed/detached-replay supplements. On acceptance, append a named `Accepted (Amended)` record with the exact accepted input and scope; preserve earlier accepted bytes and their original header/frontmatter. Explain there that the old header identifies the historical acceptance. Technical activation remains separate: DR-0002 M3 remains effective until the exact eleven-member C2 successor, qualification and separate Owner result/activation acceptance. `.hrn/`, `HV2-`, `hv2ref`, authority/record IDs, completed history and the absence of automatic Work/Git actions are unchanged.

### B. 상태·명령·구현 단계의 고정

| 대상 상태 / 경로 | `hv2`의 의미와 보정된 결과 | 작성·검증 귀속 |
| --- | --- | --- |
| 허용된 checkout-1의 S0, exact S1–S5 | 검증된 O와 허용 prefix는 기존 전환 표로 판정. 새 retired collision 규칙으로 차단하지 않음 | P2 전환·복구와 positive/negative prefix tests |
| fresh entry-1 init; incomplete exact init | D2 admission과 재관측. 최초 감지 시 target 변경 0, 늦은 감지 시 그 전의 exact prefix와 기존 guard scratch를 별도 기록 | P1b. 첫 init mapping edit 전에 exact D2 설계 수락 필요 |
| 완료 entry-1 init의 exact replay | live entry-1 collision이면 현재 PRODUCT/65, 완료 history 보존 | P1b의 complete preflight까지 포함. P2로 암묵적으로 미루지 않음 |
| live entry-1의 status/doctor/view/confirmation | 다른 non-pass가 없을 때만 conflict/12; fresh content와 collision fields로 설명 | P2의 진단 behavior, P3 consumer 문안. P1b의 inventory/adapter 표시 mapping과 구분 |
| live entry-1 update/rollback/repair/detach | scope에 해당하는 collision이면 현재 PRODUCT/65; prefix/history 보존 | P2. Ordinary Work/intent/candidate의 정확한 content/proof gate는 유지 |
| partial/completed schema-3 detach, binding 없음 | receipt/plan/suffix로 상태 확인. collision이면 더 지우거나 replay하지 않고 PRODUCT/65. 독립 source 진단은 해당 기존 detach flow의 degraded/10 | P2 detach reader/writer/replay와 P3 설명. live-binding conflict/12를 복사하지 않음 |
| historical schema-1/2 detach | old managed `hv2` 의미 보존; new-source 읽기와 old-source 쓰기 경계 유지 | P1 reader 범위와 P2 실제 detach/old-prefix 검증을 구분 |

Independent source의 `init/update/rollback/detach`는 현재 parser의 명시적 profile 계약을 따르고, `repair`는 profile 검사 전 분기하며 `--profile`을 받지 않는다. Installed에 init/repair를 추가하지 않는다. Unsupported syntax/profile/bootstrap을 일괄 PRODUCT/65로 바꾸지 않는다.

현재 `inspect_root:286–340`에는 conflict 반환이 없다. 그래도 consumer는 `conflict`만 보고 이 collision이라고 단정하지 않고 derived field와 검증된 window를 함께 본다. Current `view.render_view:570`의 adapter 표시 경로는 물리 rename과 함께 P1b에서 새 mapping으로 바꾼다. Historical old release의 경로는 old mapping으로 유지한다. 전체 current manual/adapter prose coherence는 P3이며 부분 candidate의 설치·배포는 허용하지 않는다.

P1 focused는 전체 suite 중 실제 구현된 exact IDs만 실행한다. 이 원칙은 기존 default 5건뿐 아니라 switch/repair/detach를 쓰는 다른 default tests에도 적용한다. 미선택 P2/P3 동작은 미검증이며, P1b를 full-suite green 또는 lifecycle-complete release로 부르지 않는다. 실제 선택된 assertion은 모두 PASS해야 하고 skip/expectedFailure로 대체하지 않는다. P4 complete가 전체 결합을 검증한다.

### C. P1a에서 동결할 control interface

Correction-01 C3의 readonly execution_context와 `common.python_command` 기반 `-I -S -B -c BOOTSTRAP` 호출을 유지한다. Factory는 module-level 발견 class나 collection 중 fixture/subprocess를 만들지 않는다. 이 절은 아직 실제 code/IDs/hashes가 없는 설계 제안이다.

Run-name allowlist는 controller의 순수 상수 `ENTRY_MODE_SLOTS` 한 곳에서 정의한다. `allowed()`와 그 값에서 파생한 `ENTRY_RUN_NAMES`가 같은 표를 사용하며 runner/observer는 test/product import 전에 controls의 controller module에서 그 상수만 가져오고, config 검증 뒤 실제 module 경로가 검증된 controls의 `controller.py`인지 확인한다. Controller import는 product import, config 실행, 디렉터리·process 생성 또는 main 호출을 하지 않아야 한다. `if __name__ == "__main__"` 경계를 유지한다. 이 조건은 P1a import/collection side-effect negative check 대상이다. `common.py`에는 별도 allowlist를 복제하지 않는다.

Entry collect slots는 `p1-controls`, `p1`, `p1-correction`, `p2`, `p2-correction`, `p3`, `p3-correction`, `final`; focused slots는 `p1-controls`, `p1`, `p2`, `p3`, `correction`; complete-normal/complete-parent-O/artifact는 각각 `final`이다. 새로 추가되는 run 이름은 `collect-p1-controls`, `focused-p1-controls` 두 개뿐이다. Base allowlist와 기존 per-run timeout은 그대로다. Parent inputs의 validated `phase`와 `(source_digest, controls, phase)` collection 중복 key 제안도 유지하며, 같은 세 값의 재시도는 금지한다. Old phase-less evidence를 수정·추정해서 사용하지 않는다.

Pause는 entry phase에서만 허용한다. `event: "lock-acquired"`, `path: ".hrn/locks/writer.lock"`, `occurrence: 1`, WORK-relative exclusive ready/release와 exact token 조건은 유지한다. `timeout_seconds`는 닫힌 집합 `{15, 60}` 중 하나이며 입력 임의 숫자나 자동 증가는 거부한다. Synthetic timeout/cleanup case는 15초, P2 product late-writer case는 60초를 선택하는 제안이다. 45초짜리 기존 subprocess 상한은 실제 flock 도달 시간의 측정치가 아니며, 60초가 충분하다고 검증된 것은 아니다. 늦으면 해당 case가 실패/불가로 끝나고 자동 연장·재시도하지 않는다.

- Synthetic child/coordinator 상한은 각각 60/90초로 유지한다. Product late-writer child/coordinator는 각각 150/180초를 제안한다. 이는 새로 명시한 내부 상한이며 실행 승인이 아니다. 상위 focused 1,200초와 cleanup 예산은 늘리지 않는다.
- `pause`와 기존 `fault`는 한 scenario에서 병용할 수 있다. 실제 LOCK_EX 취득 → lock-acquired 로그/ready → matching release → guard 안의 정상 전환 → 지정된 후속 fd fault 순서다. `fault`는 pause 이벤트가 아니라 기존 allowlist의 후속 파일 이벤트만 지정하며, old-source/installed-old에는 둘 다 금지한다.
- P1a 병용 검증을 위해 observer에 고정 `lock-prefix-canary` selector를 제안한다. Entry phase, 빈 argv만 허용하며 실제 lock을 소유한 synthetic child가 resume 뒤 target의 고정 `prefix-probe.bin`에 고정 비제품 bytes를 쓰고 lock을 해제한다. Pause/normal, pause/after-write kill과 한 바이트 short-write, timeout/잘못된 token 뒤 lock release·process cleanup을 검증한다. 이 selector에 임의 code/path/command를 받지 않는다. 기존 base primitive/lock canary 동작은 그대로다.
- Pause 허용 selector는 new-source, installed-new, lock-canary, lock-fd-canary 및 새 lock-prefix-canary다. Pause+fault 병용은 new-source/installed-new/lock-prefix-canary로 한정한다. 새 synthetic selector의 fd hooks는 기존 new/primitive 관측과 같은 경계에서만 활성화한다. Old observer는 byte-writer hooks를 받지 않는다.

Ready/release의 파일·token·inode/PID 검증과 WORK 경계, 같은 sandbox child process group, timeout 시 cleanup과 absence 확인은 correction-01 C4를 따른다. Parent는 lock을 소유하지 않는다. P1a의 synthetic PASS는 P2의 실제 old S0 positive → old attempt → new resume/prefix → old acquired/refusal 관측을 대신하지 않는다.

Controls map은 현재 실행 입력의 11개 이름을 명시적으로 동결한다: `acquire.py`, `acquire.sb`, `base-seed-ids.json`, `baseline-inputs.json`, `canary.py`, `common.py`, `controller.py`, `observer.py`, `prefix-oracle.json`, `runner.py`, `test.sb`. 특히 oracle도 controls identity에 포함된다. P1a에서 P2/P3에 필요한 interface·pause/fault·oracle 구조까지 작성/검토하여 이 11개 이름과 실제 digest를 동결한다. 이후 tests/factory 구현과 selection은 source/collection identity로 따로 고정한다. 고정됐다는 말로 아직 실행하지 않은 future behavior를 PASS로 만들지 않는다.

### D. OLD schema2 fixture의 실행 순서와 P1a 선택

이 fixture는 `focused p1-controls`에 포함할 별도 control case다. Schema1 synthetic construction case와 분리한다. Exact OLD source만 import하는 고정 stdlib child program으로 다음 순서를 수행한다.

1. 이번 WORK 안에 새 synthetic target을 만들고 exact OLD의 init preview와 apply를 수행한다. 새 current source의 init을 대신 호출하지 않는다.
2. OLD verifier로 초기 binding/release를 확인하고 root/product/truth snapshot을 잡는다.
3. 같은 OLD의 detach preview를 만들고 exact plan/token으로 apply한다. 기존 `inject_at="after-receipt"`의 정확한 `InjectedCrash`만 기대한다.
4. Plan/receipt schema 2와 canonical binding 관계, exact crash point, 추가된 detach receipt 이외 root/product/truth bytes 보존을 확인한다. Fake version flip, 다른 exception 또는 일반 nonzero를 성공으로 세지 않는다.

Child는 검증된 runtime의 `-I -S -B -c FIXED_PROGRAM OLD_SRC TARGET` 형태이며, 프로그램 bytes/command digest와 실제 test ID는 authoring 뒤 검토 입력에 고정한다. Shell이나 임의 code/command 인자를 받지 않는다. Context의 WORK/OLD와 대조하고 기존 SBPL·process group 경계를 상속한다. 이 case의 child/coordinator 상한은 90/120초 제안이며 상위 1,200초 안에 포함한다. Existing hidden CLI `--inject-at`/exit 75 대안으로 이번 계획을 교체하지 않는다.

이는 실제 OLD API를 synthetic target에서 실행하는 fixture 생성 test seam이다. Uninstrumented CLI, power-loss 또는 entry-1 writer qualification이 아니다. P1a에서 fixture construction과 controls를 확인한 뒤, P2에서 new reader의 schema2 read-only/쓰기 거부를 검증한다. Test 구현·실행 명령·exact ID와 결과는 아직 없다.

### E. controls 동결 뒤 변경이 필요할 때의 유일한 재검증 경로

`completed()`의 controls/runtime/Git/config 일치 조건과 `same_source=False`를 그대로 사용한다. Canary의 고정 SOURCE/hv2 probe와 checkout-1 seed를 entry-1 SOURCE로 실행하거나, 이전 r01 receipt를 바꿔 새 controls에 맞추지 않는다. Oracle 수정도 controls 변경으로 취급한다.

재검증에 필요한 checkout-1 입력은 이미 보존된 r01 OLD의 exact 101-file baseline이다. 이번 준비에서 manifest의 bytes/size/Git blob identity, readonly mode와 전체 file/directory membership을 읽어서 확인했다. 테스트 실행은 아니다. 소비자는 향후 불가피한 control 변경의 checkout-1 base 재검증이며, C2 결과 Owner 수락과 잔여 control 변경 가능성 해소 또는 동등한 exact bytes의 durable 보존 확인 전까지 이 입력을 유지한다. 이 목적을 위해 새 전체 source snapshot을 지금 만들지 않는다.

변경이 실제로 필요해지면 실행을 중단하고 다음 절차를 별도 Owner 승인 대상으로 제시한다.

1. 바뀔 controls의 파일·이유·exact diff와 유지할 baseline/seeds/policies/runtime를 고정하고 actual-byte 검토를 받는다. P1a 때의 잔여 횟수나 과거 r02/r03 root를 재사용할 권한으로 해석하지 않는다.
2. 승인된 worktree root 아래 새 `BASE-SOURCE` 실행 입력 디렉터리를 만든다. 기존 Git checkout을 덮어쓰거나 이동하지 않는다. Read-only r01 OLD를 다시 검증한 뒤 manifest의 101개 regular file bytes만 복사하고, BASE-SOURCE 쪽 mode만 manifest의 0644/0755 및 필요한 directory mode로 구성한다. OLD의 0444/0555 mode는 바꾸지 않는다. `.git` pointer/metadata, `.hrn`, 비목록 파일, symlink/hardlink는 복사하지 않는다.
3. 새 BASE-SOURCE의 `docs/development/verification/colvia-entry` 안에 검토된 새 controls 11개와 그 README를 둔다. Runtime/test/managed 29개 baseline bytes는 그대로다. 실제 파일 map과 root names/types를 이 구성에서 새로 계산한다. `.git`가 없으므로 원래 source의 `source_root_entries`를 복사하지 않는다. `paths.controls`가 `paths.source` 안에 있어야 한다는 현 common 계약을 만족시키며, 다른 source의 controls 경로를 억지로 연결하거나 common/SBPL을 완화하지 않는다.
4. 별도 새 verification root에서 이 BASE-SOURCE와 그 내부 controls로 base acquire → canary → collect → bound smoke를 한 번씩 수행한다. Runtime/Git/system-config 및 common Git input은 승인된 동일 입력을 사용한다. 101-file OLD acquisition과 20 seed/multiplicity 검증도 유지한다. 새 base source map과 실제 collection hash는 해당 invocation에 고정한다.
5. 같은 verification root/OLD와 byte-identical controls 11개를 사용하는 current entry candidate로 전환한다. Entry SOURCE는 원래 candidate이며 controls도 그 안에 있는 동일 bytes의 사본이다. Base와 entry의 SOURCE/CONTROLS 절대 경로는 달라도 `c["controls"]` 이름→digest map과 tool/config identity가 같아야 한다. `completed(..., same_source=False)`만 이 차이를 허용한다. Source map, root entries, factory/collection/selection은 각각 실제 current candidate로 검증한다. Base PASS를 entry product PASS로 확대하지 않는다.
6. Control delta의 영향을 검증하는 entry collect/focused를 한 번씩 수행하고, 결과 리뷰와 Owner 수락 뒤 중단 지점의 product phase를 재개한다. 해당 phase가 요구하는 나머지 product 검증은 별도 남는다. 이 새 root에서 product 실행 횟수를 몰래 초기화하지 않는다.

이 경로의 실행을 지금 승인하지 않는다. 나중의 실행안은 새 root/input-copy 이름, copy allowlist와 source/control hashes, 정확한 child commands/IDs 및 총 ledger를 다시 고정해야 한다. 제안 기본 상한은 base acquire/canary/collect 각 300초, smoke 1,200초와 delta entry collect 300초/focused 1,200초의 6회·합계 3,600초다. 각 1회, 자동 retry 0회이며 기존 bundle 예산과 별도 승인이다. Initial P1a의 3,600초 제안도 그대로 별도다. Runtime/policy/seed/baseline 또는 collector 의미가 달라지는 변경은 이 경로의 자동 허용 대상이 아니다. OLD custody가 없거나 새 controls가 고정 checkout-1 baseline을 처리하지 못하면 stop하고 다른 bounded 계획을 다시 승인받는다.

BASE-SOURCE는 Git worktree가 아닌 명시된 실행 입력 사본이며 임시 디렉터리에 두지 않는다. 소비자는 그 controls delta의 base/entry 검증과 결과 리뷰다. Owner 결과 수락과 후속 사용 종료 뒤 101 baseline 및 해당 controls의 고유 bytes가 다른 durable custody에 남고 사용 중인 process/review가 없음을 확인하면 기존 cleanup 규칙으로 정리한다. 이 문구는 현재 checkout 삭제나 새로운 백업·복사 작업의 승인이 아니다.

### F. 작성 범위·상태 표시와 남은 gate

P1a authoring 제안은 새 test module, runner, observer, controller, prefix-oracle, controls README와 이 기록이다. Controller의 상수 공유/slot/phase key, observer의 새 synthetic selector와 닫힌 pause/fault 계약을 포함한다. `common.py`, acquire/canary, baseline/seeds와 두 SBPL policy는 변경하지 않는다. 상한은 여전히 60분·후보 1회 제안이다. 실제 범위를 그 안에 완성할 수 없으면 보존하고 중단하며, 승인되지 않은 파일이나 시간으로 확대하지 않는다.

P1b 전에 한정된 P0 base Owner 수락, 위 exact amendment의 설계 수락, 실제 P1a controls/fixture 입력 검토·실행 승인·결과 리뷰와 Owner 수락, exact P1 selection 고정이 필요하다. P1a 설계 작성은 pending-contract draft이고 정책 수락이 아니다. P2/P3에 쓸 controls를 동결한다는 정책도 아직 Owner 수락 대상이다.

Amendment 수락 시 DR-0004의 원래 `status: Accepted` frontmatter와 기존 accepted body는 보존한다. 새 `Accepted (Amended)` 절에 exact revision/scope/Owner 기록과 이전 header의 역사 의미를 표시하고, 이 작업 기록의 current disposition에서 그 named anchor를 연결하는 계획이다. 현재 CONTRIBUTING에 DR-0004 row가 없으므로 새 row를 추가하지 않는다. Development Index의 기존 이 작업 기록 링크도 유지한다. Managed CONTRIBUTING/docs README 또는 M3의 current normative 표시는 C2 활성화 범위에서 별도로 처리하며 이번 수락 표시로 앞당기지 않는다.

| correction-01 R0 항목 | correction-02 위치 | 남는 증거/판단 |
| --- | --- | --- |
| NB-1 | A의 target-state/managed O 예외 및 named Admission/S6/Detach clauses; B | exact v2 문안의 Reviewer 확인과 Owner 설계 수락 |
| NB-2 | C의 controls 동결·pause/fault; E의 nested controls를 가진 BASE-SOURCE 경로 | 실제 authoring/실행 입력·runtime 관측·Owner 수락. 60초 sufficiency 미검증 |
| R1/R2/R3/R4 | A/B의 repair, 초기·늦은 collision, detached observation, consumer 판별 | 실제 source/installed/init/detach tests |
| R5/R6/R9 | B와 추가 adapter literal scan | P1b current mapping·init replay/recovery와 전체 focused 범위 |
| R7/R8 | C의 controller 단일 표, D의 OLD fixture 순서·선택 | actual-byte import side-effect/fixture/control 실행 |
| R10 | A/F의 append·원래 status·navigation 계획 | exact acceptance를 받은 뒤에만 기록 |

새 packet에는 이 제안, correction-01의 유지되는 interface 문맥과 최신 Reviewer/Driver 기록, 필요한 source/controls/contract 원문, 추가 `harness-v2-work`/`colvia-work` scan과 실제 11-member controls map을 포함한다. 이 사본의 작성 완료는 NB-1/NB-2 해소 PASS가 아니다. 다음 제안은 고정된 correction-02 packet에 대한 fresh Claude 구독 static R0 1회·최대 600초이며, 현재 호출하지 않는다.

### Correction-02 준비 확인과 보존

이번 문서 후보 1회를 작성했다. 이 기록 한 파일에 correction-02와 current disposition을 반영하고, 다른 117개 source 입력의 bytes/modes 및 Accepted DR-0004·제품·tests·controls·index는 보존했다. Base revision과 tracked diff도 동일하다. 이전 두 Reviewer 원문과 correction-01 packet/identity/record 사본을 변경하지 않았다.

GFM 렌더링에서 코드 밖 literal emphasis, 기존 local link 목적지, 문서 whitespace와 durable 사본 readback을 확인했다. 추가 adapter literal scan은 39개 src/tests Python 입력과 root launcher에서 3개 일치를 찾았다: product의 old tuple은 keep + 별도 ENTRY tuple 추가, plain auditor의 old tuple도 keep + 독립 ENTRY tuple 추가, view의 표시 경로는 verified-window mapping으로 P1b migrate다. 새 이름 일치 0건은 아직 구현하지 않았다는 관측이며 전체 동적 경로 closure를 증명하지 않는다. Test import/collection/execution이나 새 Reviewer 호출은 하지 않았다.

현재 기록 사본·검토 packet·identity는 기존 private bundle의 `p1-preparation/correction-02/`에 보존한다. Identity는 전체 before/after input map, actual excerpt coverage와 supplemental scan, 기존 OLD의 읽기 전용 custody check 및 packet SHA-256을 포함한다. Source 전체를 새로 복제하지 않았다. 소비자는 후속 R0 Reviewer/Owner와 수락된 다음 단계의 exact-input handoff이며, 대체 입력이나 동등한 durable custody가 확보될 때까지 필요한 bytes를 유지한다. Reproducible 작성·render·check output은 영구 산출물에 포함하지 않는다. Source와 기존 verification/diagnostic checkout은 Owner base 수락 및 위 OLD 재검증 소비자가 남아 있어 유지한다.

## P1 Correction-02 R0 Review — 2026-10-10

### Authorization, Input And Execution

Owner는 고정 correction-02 packet의 fresh Claude 정적 재검토 1회·최대 600초 제안에 “진행해”라고 답했다. 승인 범위는 이 호출과 입력 확인, 응답 원문·Driver 처분을 기존 기록에 남기는 일이다. Amendment 보정/수락, P0 base 수락, product/test/control 작성·실행이나 활성화 승인이 아니다.

직전 인증은 `loggedIn=true`, `authMethod=claude.ai`, `apiProvider=firstParty`, `subscriptionType=pro`였다. 실제 Reviewer는 Claude Opus 5.5 (`claude-opus-5-5`), fresh session `8944424b-d658-4ce1-8fe5-cc8e08856b59`다. 이전 session과 다르지만 같은 model 계열이고 이전 응답/Driver 처분을 읽었으므로 맥락 독립성에는 한계가 있다. 모델 fallback·추가 호출은 없었다.

- Base revision: `238514686078ce1564010a7b69013f48a635c57c`; tracked binary diff SHA-256: `12238ddc334c4a6971d657249732a73d59cc4c3e32b6463d5a7fccfc867a6b04`.
- Exact packet: 594,018 bytes, SHA-256 `1098874659aa24b10e96d2cfddd6f160eb9faed670916047613a7a490487b47a`.
- Reviewed task SHA-256: `7a45b5ed6c4c1fea1aaf10bdb45246e5919238013eebb769f81e04199b3b72b9`; input identity SHA-256: `593d40ec17a4831ec2640452f228a1d8160509c9db5d021a8f626c08bbd1a8b2`. 이 결과 절은 검토 입력에 없다. Diff 밖의 untracked task/DR/controls는 identity의 별도 목록과 전체 bytes/mode map으로 식별했다.
- 실제 명령은 private `authorization.json`의 exact argv다. `claude -p --model opus --effort medium`, safe/restricted, tools 빈 문자열, strict empty MCP, slash commands/settings 비활성화, `--permission-mode dontAsk`, no-session-persistence, verbose stream-json으로 실행했다. Packet을 stdin으로 넘겼고 cwd는 새 private `correction-02/review-01`이었다. Product/test command는 실행하지 않았다.
- 275.85초, exit 0, timeout/error 없음, final response 수신. Tools/MCP 빈 배열, tool use 0건, stderr 0 bytes, malformed stream 0건, 종료 뒤 process group 부재 확인.
- 전후 source 118개 bytes/modes·membership, base/tracked diff, packet/identity/record-copy 동일성 PASS. 허용된 호출 1/1회를 소진했으며 자동 재호출하지 않는다.

Reviewer 판정은 조건부 통과다. NB-1/NB-2와 R1–R10은 계획 수준에서 해소됐고, exact amendment 서두의 named row 누락 B-1 한 건을 Owner 수락 요청 전에 보정해야 한다. 따라서 현재 exact bytes의 무조건 R0 closure나 정책 수락으로 기록하지 않는다. 아래는 정적 판단이며 실행·재현 결과가 아니다.

### Correction-02 Reviewer Response — Verbatim

````text
# P1 준비 보정안(correction-02) R0 정적 검토

## 판정

**조건부 통과입니다.** NB-1, NB-2와 R1–R10은 계획 수준에서 해소됐고, 제공된 코드와 모순되는 설계는 찾지 못했습니다. 다만 Amendment v2 문안에는 Owner 수락 요청 전에 고쳐야 할 한 구절이 있습니다(B-1).

이 보고는 Reviewer 소견입니다. Owner의 amendment 수락, 구현·실행 승인, base 결과 수락, 활성화를 대신하지 않습니다.

## 증거 한계

모든 판단은 제공된 바이트의 정적 판독이며 실행 증거는 없습니다.

- **읽지 못한 것**:
  - `work.py`의 대부분(`_visible_truth`, `_regular_files`, `_stable_file`)
  - `intent.py`, `candidates.py`, DR-0002/0003, private invocation
  - 이전 AST/literal 목록
- **다시 세지 않은 수치**: 118개 입력, 39개 scan 대상, 중복 ID 177개.
- **독립성 한계**: 이전 Reviewer와 같은 model 계열이고, packet에 이전 응답과 Driver 처분이 들어 있습니다.

## 차단 항목 (문안 한 구절)

### B-1. named clause 목록이 실제로 바뀌는 Source×Target 행을 다 가리키지 않습니다

- **근거**: v2 서두는 Source By Target By Operation에서 "new-source/live-entry-1, fresh-init and completed-replay cases"만 지명합니다.
- **문제**: 본문은 아래 세 행의 결과도 바꾸는데, 이 행들은 지명되지 않았습니다.
  - `New / incomplete entry-1 init`: collision이면 exact recovery를 65로 거부합니다.
  - `New / incomplete entry-1 repair`: scope (a)와 Lifecycle refusal의 repair가 적용됩니다.
  - `New / schema 3 detach prefix`: Detach는 65로 거부하고, Read는 degraded/10이 됩니다.
- **왜 차단인가**: CONTRIBUTING은 "Later changes name the clauses they amend"를 요구합니다. NB-1의 "함께 고칠 것"과 같은 유형이고, 수락 뒤에 고치면 또 한 번의 amendment가 됩니다.
- **최소 교정**: 서두의 해당 구절에 "incomplete-entry-1-init, incomplete-entry-1-repair and schema-3-detach-prefix rows"를 추가합니다. 설계 변경은 없습니다.

## NB-1, NB-2 해소 여부

**NB-1은 해소됐습니다(B-1 조건).**

- **범위 선행**: target-state scope (a)/(b)/(c)가 이름 검사보다 먼저 옵니다.
- **S0–S5 제외**: S0–S5의 binding은 B0(checkout-1)이라 scope (a) 밖입니다. managed-O 제외 문단이 exact O와 S5의 S4 재관측을 명시적으로 보존합니다.
- **S6**: binding이 B1이 되어야 scope에 들어오므로 "collision 중에만 보충"과 맞습니다.
- **alias·altered O**: 제외 대상이 아니며 원래 규칙으로 돌아갑니다.
- **named clause**: Admission 문단, S6 cell, Detach Closure가 추가됐습니다.

**NB-2는 해소됐습니다.** E 경로를 현 controls 코드와 대조했습니다.

- **controls 위치**: `common.config`의 `controls.is_relative_to(source)`는 BASE-SOURCE 안에 controls를 두는 구성으로 충족됩니다.
- **canary probe**: `SOURCE/hv2`는 baseline 101개에 있습니다. 0755로 복사하므로 parent의 write-open positive control이 성립합니다.
- **source 차이 허용**: `completed()`는 controls, runtime, git, git_system_config만 비교합니다. 경로와 source digest는 `same_source=False`에서 비교하지 않습니다. 따라서 base(BASE-SOURCE)와 entry(candidate)의 SOURCE가 달라도 통과합니다.
- **root 구성**: `.git`이 없는 `source_root_entries`를 새로 계산한다는 문장이 `verify_source_root`와 맞습니다.
- **예산**: 300×3 + 1,200 + 300 + 1,200 = 3,600초, 6회로 산술이 맞습니다.
- **미확인**: seed 20개가 non-Git SOURCE에서 같은 multiplicity로 수집되는지는 실행 증거 영역입니다.

## R1–R10 해소 여부

| ID | 판정 | 확인 근거와 잔여 |
| --- | --- | --- |
| R1 | 해소 | B가 repair의 profile 전 분기를 명시합니다. `cli.run:109–113`과 일치합니다. |
| R2 | 해소 | 초기 감지는 변경 0, 늦은 감지는 exact prefix와 lock anchor를 분리 기록합니다. `workspace_init_apply`의 preflight → `bootstrap_root` → `writer_guard` → 재관측 순서와 맞습니다. |
| R3 | 해소 | binding 없는 detach를 receipt/plan/suffix로 식별합니다. degraded/10은 `_workspace_status_observation`의 detach-candidate 분기(ContractError → degraded)와 일치합니다. |
| R4 | 해소 | `inspect_root`와 `product.py`에 `conflict` 반환이 없음을 확인했습니다. 소비자는 derived field로 구분합니다. |
| R5 | 해소 | literal 3건의 처분이 있습니다. `_product()`가 inventory를 반환하므로 `view:570`의 window mapping은 구현 가능합니다. |
| R6 | 해소 | init complete replay와 recovery의 collision 거부가 P1b로 귀속됐습니다. |
| R7 | 해소 | `controller.py`는 import 시 부작용이 없습니다(상수, 함수, `__main__` guard). BOOTSTRAP이 CONTROLS를 `sys.path`에 추가하므로 observer와 runner에서 import할 수 있습니다. |
| R8 | 해소 | init → detach preview → `after-receipt` 순서가 기존 `DetachVersionTests.seed`와 20건 suite의 `-I -B -c` 패턴으로 뒷받침됩니다. `focused p1-controls` 포함도 명시됐습니다. |
| R9 | 해소 | exact ID 원칙을 전체 suite로 확장했습니다. |
| R10 | 해소 | 원래 frontmatter 보존 + named append 계획이 DR-0004가 DR-0003에 정한 방식과 같습니다. |

## 비차단 교정 (P1a authoring 전 반영 권장)

| # | 항목 | 근거 | 최소 교정 |
| --- | --- | --- | --- |
| N1 | same-window pending 복구의 결과 | entry-1→entry-1 update/rollback이 pending일 때 collision이 있으면 문안상 복구가 65로 거부됩니다. 진단은 partial/14가 우선해 collision field가 안 나옵니다. 의도로 읽히지만 서두의 "S1–S5 forward-recovery 불변" 문장과 혼동될 수 있습니다. | "same-window pending recovery도 collision 해소 전까지 거부"를 한 문장으로 적습니다. |
| N2 | "each existing under-guard re-observation" | init의 guard 안 재관측은 현재 한 번입니다. 그 뒤 나타난 occupant는 완료까지 감지되지 않을 수 있습니다. | 재관측 지점을 늘리지 않는다는 것을 B 표에 적습니다. |
| N3 | D2-A의 Git-index 문장 | DR의 index 규칙은 `colvia` 대상입니다. v2의 collision은 파일시스템 entry로 정의됩니다. tracked-but-deleted `hv2`가 거부 대상인지 모호합니다. | "index 검사는 `colvia` 한정"이라고 적거나, `hv2`까지 넣으려면 Owner 결정으로 올립니다. |
| N4 | "C2 must fix" 문장과의 관계 | DR-0004 원문은 분류와 exit를 C2가 정한다고 했습니다. | "이 amendment가 그 결정을 대신하고 C2 문서는 이를 반영"이라고 Acceptance 문단에 적습니다. |
| N5 | E 6단계의 slot과 ledger | controls가 바뀌면 옛 root의 base 증거는 `completed()`를 통과하지 못합니다. 이후 product phase는 모두 새 root에서 돌게 되고, 새 root의 slot은 전부 비어 있습니다. slot 배타성만으로는 누적 한도가 지켜지지 않습니다. | delta 검증에 쓸 slot 이름을 지정하고, root를 넘는 누적 ledger를 Driver가 기록한다고 적습니다. |
| N6 | `prefix-oracle.json`의 `late_lock` | 현 oracle은 "parent demonstrably holds common writer.lock"입니다. C4 이후 모델은 새 실행자가 소유합니다. | P1a 동결 때 고칠 항목으로 명시합니다. |
| N7 | pause handshake의 I/O | new-source selector에서는 `os.open`/`os.write`가 hook됩니다. ready/release는 target 밖이라 기록되지 않지만 원본 함수 사용이 안전합니다. | observer 설계에 "handshake는 `original[...]` 사용"을 적습니다. |
| N8 | profile gate의 단계 | `cli.run`의 `args.profile != "checkout-1"` 검사는 init/update/rollback/detach가 공유합니다. P1b에서 init만 바꿀 수 없습니다. | "gate는 P1b에서 네 명령 모두 전환, update/rollback/detach 동작은 P2까지 미검증"이라고 적습니다. |
| N9 | P1b window literal 목록 | 아래 literal이 P1b 대상인지 이 packet만으로는 확인되지 않습니다. `workspace._validate_plan_shape`, `_validate_init_plan`, `product._managed_paths`, `_serial_inventory`, `_launcher_inventory_window`, `_workspace_product_once`의 planning 조건과 `target/"hv2"`. | 이전 AST 목록에 있는지 대조하고 없으면 추가합니다. |
| N10 | OLD fixture의 고정 입력 | target이 Git인지 non-Git인지, operation ID와 시각 상수가 D에 없습니다. | authoring 때 프로그램 안 고정값으로 정한다고 적습니다. |

## 영역별 확인

- **D1-A와 view**: conflict는 `pass`가 아니므로 graphs가 None이 되고, `view._observe`가 새 graph를 읽습니다. `EXITS`에 `conflict: 12`가 이미 있습니다. `render_view`의 status field allowlist에는 `retired_entry_collision` 추가가 필요하며 P2 귀속과 맞습니다.
- **pause와 fault**: 현 observer는 fault를 `primitive-canary`와 entry phase의 new-source/installed-new로 제한합니다. `lock-prefix-canary` 추가와 old selector 금지는 이 구조와 일관됩니다. canary가 쓰는 5-key scenario는 `pause`가 선택 필드라 그대로 통과합니다.
- **60초의 충분성**: coordinator는 ready 확인, old child 기동, old의 lock-attempt 관측을 60초 안에 끝내야 합니다. 부족하면 case 실패 후 E 경로로 가므로 막힌 경로는 아닙니다.
- **controls 동결**: 11개 이름은 custody 관측과 일치합니다. `prefix-oracle.json`을 P2 구현 전에 syscall 단위로 동결하면 P2에서 E 경로(3,600초 + 리뷰)를 탈 가능성이 실질적입니다.

## Owner 결정 사항

1. 한정된 P0 base 결과의 수락 여부.
2. B-1 교정 뒤 v2 exact revision의 수락. C0-H-A에 없던 추가 정책은 다음과 같습니다.
   - alias 포함과 `observed_names`
   - `conflict`/12
   - incomplete-init recovery와 same-window pending recovery의 거부
   - 완료된 replay의 현재 거부
   - 완료된 detach 뒤 `hv2`가 있으면 degraded/10이고 "cleanly detached"로 부르지 않음
   - lock scratch의 별도 기록
3. B-1로 바이트가 바뀐 revision을 다시 검토할지, 이번 검토로 갈음할지.
4. controls 동결 정책: oracle을 P2 전에 동결하는 것, pause `{15, 60}`, child/coordinator 150/180초.
5. 확대된 P1a 범위가 60분·후보 1회에 현실적인지.
6. adapter 물리 경로를 P1b에서 옮기는 것.
7. E 경로를 유일한 재검증 경로로 두는 것과 r01 OLD의 유지 기간, root를 넘는 실행 ledger.
8. tracked-but-deleted `hv2`를 fresh init에서 거부할지(N3).
9. 실제 바이트 R0, 실행 계획 R0, R1의 결합이나 면제 여부.
````

### Correction-02 Driver Dispositions

수정 전의 correction-02와 검토 packet은 그대로 보존한다. 다음 표는 Reviewer 응답 처분이며 실제 amendment 변경이나 Owner 선택이 아니다. 응답 뒤 추가 확인은 Driver만 수행했고 Reviewer가 읽은 입력으로 소급하지 않는다.

| ID | 처분 | 근거와 최소 후속 범위 |
| --- | --- | --- |
| B-1 | accept | Source By Target By Operation의 incomplete entry-1 init, incomplete entry-1 repair, schema-3 detach-prefix 행도 본문에 의해 달라진다. Named clause 첫 문장에 세 행을 추가하는 것이 맞다. 기존 본문의 결과/정책은 유지하고 exact v2 correction identity를 따로 고정하는 후속 문안 보정을 제안한다 |
| N1 | accept clarification | Same-window entry-1 pending recovery도 collision이면 writer 거부 대상이다. 진단의 partial/14 등 기존 non-pass 우선과 구분한다. checkout-1→entry-1의 exact S1–S5 예외를 same-window에 확대하지 않는 설명을 다음 문안에 추가한다 |
| N2 | accept clarification | 현재 init의 guard 안 재관측은 한 번이며 이 제안이 관측 지점을 늘리지는 않는다. 늦은 비협조적 변경의 원자성 보장 없음은 이미 A에 있다. 표에도 이 한계를 짧게 연결한다 |
| N3 | accept ambiguity / no new policy | Driver가 DR-0004:100의 index 거부 대상이 colvia/alias/descendant임을 확인했다. 새 retired collision은 실제 immediate-root occupant 정의다. 다음 후보는 기존 colvia index 규칙과 hv2 filesystem 관측을 구분하는 명료화를 제안한다. Tracked-but-deleted hv2까지 새 거부 대상으로 늘리는 정책은 현재 제안에 몰래 포함하지 않으며 별도 Owner 결정 없이는 추가하지 않는다 |
| N4 | accept clarification | Driver가 DR-0004:194의 C2 diagnostic mapping 위임을 확인했다. 이미 named 대상인 retired-entry 문단에 이 amendment의 exact mapping을 설계 선택으로 보충하고, 실제 C2 구현/qualification/활성화는 별도라는 문장을 명확히 한다 |
| N5 | accept | E에 예산 재설정 금지는 이미 있지만 새 root의 empty slot이 누적 한도를 보장하지 않는다. 후속 문안은 delta collect/focused용 exact slot과 이전 root→새 root의 승인·실행 횟수를 같은 task에 연결하는 누적 ledger를 특정해야 한다. 실제 이름/입력/명령/총량은 해당 실행 승인 때 고정하고 old receipt 수정이나 자동 retry는 허용하지 않는다 |
| N6 | accept | Driver가 prefix-oracle.json:158–165의 parent lock/transition/release 문구를 확인했다. P1a 작성 범위에 oracle은 이미 있으나 새 executor 소유와 coordinator 관측/해제 요청의 차이를 수정 항목으로 명시해야 한다. Oracle bytes는 이번에 바꾸지 않았다 |
| N7 | accept implementation requirement | Observer handshake는 보존된 original I/O로 수행하는 bounded 구현 요구를 다음 문안에 넣는다. 실제 pause/fault 및 cleanup correctness는 P1a actual-byte/실행 검증 대상이며 현재 정적 검토로 PASS를 주지 않는다 |
| N8 | revise / accept shared gate concern | cli.run:111–118의 profile gate는 네 명령이 공유한다. 다만 명령별 분기가 논리적으로 불가능하다는 뜻은 아니다. 현재 계획의 P1b 공통 entry-1 profile mapping과 P2 update/rollback/detach behavior 미검증 경계를 명시하는 방향을 제안한다. Partial source를 설치·배포할 수 있다는 권한은 생기지 않는다 |
| N9 | accept bounded reconciliation | 첫 준비 packet의 단순 name lookup에서 _validate_plan_shape, _validate_init_plan, _managed_paths, _launcher_inventory_window, _workspace_product_once는 발견됐고 _serial_inventory는 없었다. 이름 존재만으로 AST coverage나 phase 귀속을 증명하지 않는다. 다음 문서 보정에서 여섯 함수 및 planning/target-hv2 literal의 기존 목록을 현재 source와 대조하고 P1b reader/mapping과 P2 writer로 귀속한다. Test import/execution은 필요하지 않다 |
| N10 | accept authoring pin | OLD fixture의 Git/non-Git 선택과 operation ID/시각은 고정 child program의 literal로 actual-byte 검토 입력에 포함해야 한다. 임의 입력 경로를 추가하지 않는다. 지금 새 fixture/code를 작성하지 않았다 |

Reviewer의 NB-1/NB-2와 R1–R10 해소는 계획 수준의 결과로 수용한다. Non-Git BASE-SOURCE에서의 seed multiplicity, 실제 controller import/OLD fixture/pause/fault, 60초 sufficiency와 P2 lifecycle 결과는 미실행이다. Timeout 발생은 해당 case 실패/불가다. E 재검증이 자동 진행되거나 고정 pause 집합을 임의로 늘릴 수 있다는 뜻이 아니다. 실제 delta가 필요하면 그때의 exact input과 새 승인 범위를 확인해야 한다.

### Next Bounded Proposal And Remaining Owner Decisions

이번 검토와 결과 기록은 완료했다. 현재 exact amendment에는 named row 보정 B-1이 남아 있으며, 코드·Accepted DR·controls·기존 proposal bytes는 수정하지 않았다.

다음 제안은 문서 보정 1회·최대 20분이다. 기존 작업 기록에 세 행을 명시한 exact amendment candidate와 N1–N10의 좁은 설명/귀속을 추가하고, 기존 검토 입력을 참조하는 private delta packet을 만든다. 새 전체 source snapshot이나 전체 packet 복제는 필요하지 않다. N9는 여섯 함수와 해당 literal을 읽기 전용으로 대조한다. 완료 기준은 B-1의 정확한 교정과 비차단 처분을 Owner가 한 번에 판단할 수 있는 문안/identity다. 정책 확대, source/control/test 구현, 추가 Reviewer/test 실행은 포함하지 않는다. 기존 의미를 넘는 선택이나 20분을 넘는 추가 조사가 필요하면 해당 항목을 pending으로 남기고 중단한다.

보정 bytes에 추가 Reviewer 호출이 필요한지는 별도 Owner 판단이다. 같은 전체 packet의 자동 재검토를 제안하지 않는다. 이번 리뷰가 정한 최소 교정 및 Driver static delta 검증으로 보정안을 판단하는 경로를 우선 제안하되, 미검토 bytes를 Reviewer가 승인했다고 쓰지 않는다. 그 뒤 exact amendment/controls freeze/P1a 범위 수락과 한정 P0 base 결과 수락을 각각 구분해 요청한다. Actual-byte R0·실행 계획·R1을 이번 설계 검토가 면제하지 않는다. 확대 P1a authoring의 60분·1후보, adapter mapping P1b, OLD custody 기간과 E 변경 경로 역시 아직 Owner 결정 전이다.

### Validation And Preservation

이 결과 기록은 GFM으로 렌더링해 코드 밖 literal emphasis, 기존 local link 29개와 whitespace를 확인했다. Source 변경은 기존 작업 기록 하나다. 다른 117개 입력의 bytes/modes, base/tracked diff와 Accepted DR/product/tests/controls/index를 보존했고 central STATUS 변경은 필요하지 않다. 응답 원문은 이 기록에 정확히 옮긴 뒤 SHA-256과 durable 사본 readback으로 확인한다.

Private correction-02/review-01에는 authorization, compact metadata, current record 사본을 유지한다. 원문이 source와 durable 사본에 보존된 뒤 중복 stream transport·빈 stderr·중복 응답 파일은 제거한다. 기존 packet/identity/record-copy와 이전 review 기록은 그대로다. 소비자는 Owner의 보정안 판단과 다음 exact-input handoff다. Source checkout과 r01 OLD/검증 환경은 base 수락과 P1 재사용·controls 변경 소비자가 남아 있어 유지한다. 검토 환경 자체를 영구 증거로 요구하는 것은 아니며 필요한 고유 입력의 보존과 사용 종료를 확인한 뒤 기존 cleanup 규칙으로 정리한다.

## P1 Preparation Correction-03 Delta — 2026-10-10

### Scope And Current Proposal

Owner는 correction-02 정적 검토 뒤 문안 보정과 delta packet 작성만 1회·최대 20분 진행하자는 제안에 “진행해”라고 답했다. 이번 결과는 남은 B-1의 named row 누락과 N1–N10의 설명·작성 단계만 보정한다. 제품·tests·controls·Accepted DR, 기존 proposal와 Reviewer 원문은 보존한다. 추가 Reviewer나 test/import/collection 실행은 포함하지 않는다.

현재 exact amendment 후보는 아래 revision 2.1이다. Correction-02 A의 문안을 국소 보정한 것으로, 이전 A를 현재 후보로 읽지 않는다. Correction-02 B–F와 correction-01에서 유지한 interface는 아래 지정 보충 외에 그대로다. 이 우선순위는 제안 사이에만 적용되며 현재 M3나 Accepted 상태를 바꾸지 않는다. 이전 Reviewer는 revision 2를 조건부 통과로 판정했다. Revision 2.1과 이번 delta는 Driver가 대조했으며 추가 Reviewer에게 보내지 않았다.

### Exact English Amendment Candidate v2.1

> **Named Amendment: Entry Diagnostics And Fresh-Init Admission (D1-A/D2-A), revision 2.1.** This amendment supplements the retired-entry paragraph of **Rollback, Proof And Retained Meaning**; the fresh-init row of **Inventory And Version Table**; the applicable new-source/live-entry-1, fresh-init and completed-replay cases, and the incomplete-entry-1-init, incomplete-entry-1-repair and schema-3-detach-prefix rows, of **Source By Target By Operation**; the completed-execution/historical-replay paragraph of **Admission And Quiescence**; the S6 replay cell of **Durable Switch Sequence**; and the retired-entry refusal and observation cases of **Proposed Detach Schema 3 Closure**. The replay supplements apply only when the scoped retired-entry collision below is present. Other replay rules remain in force. This amendment does not change the S1 one-way boundary, the exact S1–S5 forward-recovery rules, T-A torn-write limit, admitted predecessor, local/worker policies, persistent record schemas or authority identities.
>
> **Target-state scope comes before the name check.** This amendment's retired-entry rule applies to (a) a target whose current binding is independently verified to identify entry-1, including supported repair/recovery when live runtime bytes are incomplete; (b) fresh entry-1 init and exact incomplete entry-1 init identified by the entry-1 candidate and exact init request/prefix; and (c) an entry-1 detach operation identified by its verified exact schema-3 plan/receipt and removal/preservation sets, including partial and completed detach with no remaining active binding. Do not infer any of these states from a filename alone. Unsupported, malformed, ambiguous or otherwise invalid identity/prefix evidence retains its existing refusal or unavailable result.
>
> **Managed O during the admitted transition is not a retired-entry collision.** The exact managed `hv2` of the admitted checkout-1 predecessor at S0, and the exact O allowed by DR-0004's S1–S5 physical-prefix table, remain governed by that table. In particular, its S5 re-observation of S4 and exact O retirement remains possible. Do not apply this amendment's unowned-entry refusal to those exact transition paths. This exclusion does not admit a case alias, altered O, unsupported predecessor, unexpected O/N combination, torn bytes or any other unsupported prefix. The original validation and preservation rules still decide those cases.
>
> **Scoped collision observation.** Within an applicable target state, a retired-entry collision is an immediate target-root entry whose name, after Unicode NFC normalization and case folding, equals `hv2`. Enumerate names without following the occupant. Files, directories and symbolic links, including dangling links, are occupants; do not open, execute, rename or delete them to resolve the collision. Alias inclusion and the diagnostic list of observed names are explicit additions, not retrospective claims about C0-H-A. Existing unsafe-path, topology, unsupported, damaged, pending, stale, incompatible, partial and other non-pass outcomes retain their meaning and precedence. Only a complete ordinary live entry-1 observation that would otherwise be `pass` is reclassified by D1-A below.
>
> **D1-A live-entry diagnostics.** For an otherwise valid live entry-1 product/binding and record observation with a scoped collision, supported `status`, `doctor` and `view` paths report `classification: conflict`, exit 12. Retain the verified current product/binding; report `lifecycle_ready: false` and `retired_entry_collision: {path: "hv2", observed_names: [...], ownership: "project", preserved: true}`. `path` is the canonical retired name. `observed_names` contains each colliding immediate-root name once, sorted by UTF-8 bytes. These are derived fields, not persistent state, and are not mandatory on collision-free responses. Human output identifies the actual names and requires a separate operator decision. Consumers distinguish this condition by its derived collision fields and verified entry-1 context, not by exit 12 alone.
>
> Readable Work, intent and candidate content remains available only after fresh graph and stability checks. `view confirmation` may return 12 while displaying the current ticket and independent reader checks; this is not confirmation, readiness or authorization. Ordinary record commands retain their exact-content, pending, reference, binding and ticket rules. They never execute or snapshot-exclude a retired occupant. Only the verified mapped `colvia` entry is managed runtime. A stale result, missing reference or existing acceptance gate is not bypassed.
>
> **Lifecycle refusal and completed live-entry replay.** On supported new-runtime lifecycle paths within the scoped target states, a detected collision refuses init replay/recovery, update, rollback, repair and detach with `HV2-WORKSPACE-PRODUCT`, exit 65, before any further product or authority publication. This includes an exact already-completed live-entry operation: observe and preserve the current product/binding/history, then report the present collision without performing the operation again. The message distinguishes current refusal from historical completion. Never relabel completed history as pending/failed, rewind the binding or repeat its old truth comparison as a new completion claim. The Admission/S6 replay supplement changes only this collision result; all other current-product and historical-comparison limits remain. Unsupported commands, bootstrap failures, invalid profiles/arguments and other preexisting validation failures keep their own diagnostics. Same-window entry-1 pending update/rollback recovery is also refused while a scoped collision remains; this does not extend the checkout-1-to-entry-1 S1–S5 exception. Diagnostic partial/14 and other preexisting non-pass outcomes retain precedence.
>
> **Entry-1 detach without an active binding.** An exact schema-3 detach prefix remains identified through its verified receipt/plan and exact remaining suffix/preserve set even after binding removal. On a collision, refuse further removal or exact completed-detach replay with `HV2-WORKSPACE-PRODUCT`, exit 65, and preserve the receipt, history, occupant and remaining bytes. Do not invent a current product/binding or reinstall a launcher. Independent-source `status`/`doctor` retain the existing detach diagnostic flow: when the detach evidence otherwise verifies and the scoped collision is the failing condition, report `degraded`, exit 10, with that product error and preservation guidance. Source `view` uses the corresponding existing degraded rendering. Do not call the current target cleanly detached or rewrite its retained receipt/history. For an operation previously established as complete, this is a current refusal, not a rewrite of that historical result; receipt presence alone does not establish completion. Installed observation is unavailable once its managed launcher is removed. Schema-1/2 historical detach readers and their retained-old-source write rules are unchanged, and a historical managed `hv2` is not reclassified under this schema-3 rule.
>
> **D2-A first admission.** Fresh entry-1 init refuses every scoped occupant above. If present at the first admission observation, refuse before any target directory, bootstrap primitive, init plan, receipt, lock or other target write, with `HV2-WORKSPACE-PRODUCT`, exit 65. Existing `colvia` collision, path/topology, Git-index and ignore-policy checks still apply. The retained launcher-index check covers `colvia`, its NFC/casefold aliases and descendants, even when the worktree path is absent. The retired-`hv2` collision rule observes immediate filesystem occupants; this amendment adds no refusal solely because `hv2` is tracked but absent. Other existing validation failures retain their effect.
>
> **Exact init recovery and late collision.** Exact incomplete entry-1 init checks for the collision before resuming and at each existing under-guard re-observation. Detection at the initial preflight permits no target change. If the initial preflight passed and the occupant appears later, the invocation may already have completed the exact bootstrap/recovery steps allowed by that request; preserve that durable prefix and perform no further product/authority publication after detection. Report those earlier writes as earlier writes, not as a zero-change result or a new scratch exemption. Account separately for the exact `.hrn/locks` directory and empty regular `writer.lock` anchor only where the existing guard contract permits their creation. Do not exempt any other path, replacement or content change, and do not repair a preexisting malformed lock. This is not atomic protection against a non-cooperating path change between observations. Never delete or rename the occupant or prefix to obtain success.
>
> **Acceptance and effect.** Owner design acceptance must identify this exact revision and its named clauses, including the alias/diagnostic, init-recovery and completed/detached-replay supplements. On acceptance, append a named `Accepted (Amended)` record with the exact accepted input and scope; preserve earlier accepted bytes and their original header/frontmatter. Explain there that the old header identifies the historical acceptance. On design acceptance, this exact diagnostic mapping supplies the decision delegated to C2 by the named retired-entry paragraph; the C2 successor documents must reflect it. Technical activation remains separate: DR-0002 M3 remains effective until the exact eleven-member C2 successor, qualification and separate Owner result/activation acceptance. `.hrn/`, `HV2-`, `hv2ref`, authority/record IDs, completed history and the absence of automatic Work/Git actions are unchanged.

### Change Map And Preservation

| 근거 | 수정한 위치 | 보존한 의미 |
| --- | --- | --- |
| B-1 | 서두에 incomplete entry-1 init, incomplete entry-1 repair, schema-3 detach-prefix 세 행 추가 | 이미 본문에 있던 적용 상태와 결과. 새 command/state를 추가하지 않음 |
| N1 | Lifecycle refusal 마지막에 same-window pending recovery와 진단 우선순위 명시 | Checkout-1 전환의 exact S1–S5 예외, partial/14 우선, scoped writer PRODUCT/65 |
| N3 | D2-A의 index/absent-path 두 문장을 구체화 | 기존 colvia index/alias/descendant 검사와 실제 hv2 occupant 정의. Tracked-but-deleted hv2를 이유로 한 새 거부는 추가하지 않음 |
| N4 | Acceptance에 C2 위임과 successor 문서 반영 관계 명시 | 설계 수락과 technical activation 분리, unchanged M3와 exact eleven-member C2/qualification/Owner gate |

그 밖의 amendment 문단·순서·수치·식별자·예외는 revision 2와 byte 단위로 같다. Title의 revision 번호 외 변경은 위 네 곳뿐이다. D1 conflict/12, schema-3 detached degraded/10, lifecycle PRODUCT/65, alias/observed_names, initial-zero/late-prefix 보존과 lock scratch 경계는 바꾸지 않았다.

### Implementation Notes For N2 And N5–N10

**N2 — Init observation.** 현재 init의 guard 안 재관측은 한 번이며 이번 설계가 재관측 지점을 늘리지는 않는다. 그 관측 뒤 생긴 비협조적 occupant까지 원자적으로 막는다는 보장은 없다. P1b의 init/recovery 검증은 이미 지정한 관측 지점의 초기 거부·늦은 거부·prefix 보존을 확인한다.

**N5 — Delta slots and cumulative ledger.** Correction-02 E의 새 controls 검증은 아래 여섯 mode/slot을 각각 한 번 사용한다. Entry 두 단계는 P1a에서 제안한 p1-controls slot을 그대로 쓰며 새로운 slot 이름을 추가하지 않는다.

| phase | mode | slot / run name | 상한 |
| --- | --- | --- | --- |
| base | acquire | base / acquire-base | 300초 |
| base | canary | base / canary-base | 300초 |
| base | collect | base / collect-base | 300초 |
| base | smoke | base / smoke-base | 1,200초 |
| entry | collect | p1-controls / collect-p1-controls | 300초 |
| entry | focused | p1-controls / focused-p1-controls | 1,200초 |

합계 6회·3,600초, 자동 retry 0회라는 제안은 그대로다. 실제 root 이름·source/control/selection hashes·child 명령은 해당 실행안에서 고정한다. Driver는 새 root 승인/실행 전 이 작업 기록에 이전 root, 새 root, 승인 근거, 단계·mode/slot, exact input digest, 허용 횟수, 기존 소비량, 이번 실행 결과와 잔여량을 연결해 기록한다. 새 root의 빈 slot은 누적 허용 횟수를 늘리지 않는다. P1a 최초 controls 검증과 이후 controls delta 검증은 서로 다른 승인/예산 항목이며, 기존 base/diagnostic/product 횟수는 이전 기록의 실제 값으로 이어받는다. 이 표는 그 실행을 승인하거나 실제 소비량을 0으로 선언하지 않는다. 한도/이전 소비량을 확인할 수 없으면 실행 전에 멈춘다. Delta control 결과 수락 뒤 product phase 재개는 실제 동일 입력에 필요한 검증과 남은 승인 횟수를 확인하고 별도로 고정하며, 옛 root의 product PASS를 새 controls의 PASS로 복사하지 않는다.

**N6 — Prefix oracle.** P1a에서 `prefix-oracle.json`의 `late_lock.required` 2–5항을 새 실행자의 실제 lock 소유, old child의 같은 lock attempt, 새 실행자의 지정 prefix 진행, lock 해제 뒤 old acquired/refusal 순서로 바꾼다. Coordinator는 ready/attempt 확인과 matching release 요청을 하며 lock을 소유하지 않는다. 기존 parent 소유 문구를 남긴 채 observer만 바꾸지 않는다. Oracle은 동결하는 11-member controls에 포함되며 실제 bytes는 P1a 검토 입력이다.

**N7 — Handshake I/O.** Observer의 ready/release open/read/write/close는 hook 설치 전에 보존한 original I/O를 사용한다. Handshake를 product fd event나 fault 횟수로 세지 않는다. 기존 exclusive regular-file·token·inode/PID·WORK 경계 검사와 timeout/cleanup을 유지하고, 실제 병용 negative cases로 확인한다. 새 임의 path/code/command 인자를 허용하지 않는다.

**N8 — Shared profile gate.** P1b는 `cli.run`의 init/update/rollback/detach 공통 profile gate를 current entry-1 source 계약에 맞게 함께 정렬한다. 네 명령이 같은 profile을 받는 것과 네 동작을 검증한 것은 별개다. P1b의 실행 선택에는 구현된 init/reader assertions만 들어가며 update/rollback/detach behavior는 P2 전까지 미검증이다. Repair의 별도 분기와 installed command 집합은 유지한다. 부분 candidate의 설치·배포는 허용하지 않는다. 명령별 분기가 불가능해서 이렇게 정한 것이 아니라, 기존 공통 gate의 귀속을 명확히 한 것이다.

**N9 — Current source reconciliation.** 다음 표는 Driver가 현재 source의 여섯 함수 본문을 읽고 기존 P1b reader/mapping과 P2 writer 구분에 연결한 결과다. 첫 준비 packet의 이름 검색에서 `_serial_inventory`만 없었으며, 다른 이름이 있었던 사실만으로 종전 AST/phase coverage를 주장하지 않는다. 이번 delta packet에 해당 함수 원문과 source/excerpt hashes를 넣는다. 이 표는 전체 동적 caller를 전수 검증한 결과가 아니다.

| 현재 source 위치 | P1b reader/mapping 귀속 | P2 writer/결합 귀속 |
| --- | --- | --- |
| workspace._validate_plan_shape:343–353 | Entry-1 init release/window의 shape reader를 추가하고 literal old windows를 유지 | Switch/detach writer 검증을 대신하지 않음 |
| workspace._validate_init_plan:387–402 | Entry-1 fresh/exact init schema1 validation과 request identity. 기존 old history 의미 보존 | 새 switch/detach publication은 별도 |
| product._managed_paths:65–67 | Entry-1의 독립 29-member tuple을 선택. 기존 old tuples/지원 window 유지 | 전환 때 O/N 조합·retirement 판단은 P2 |
| product._serial_inventory:155–172 | Entry-1 window와 exact mapped membership/order/duplicate 판정 | 새 writer가 만든 실제 inventory의 lifecycle 결합 검증은 P2 |
| product._launcher_inventory_window:75–116 | Current entry-1 선언과 allow_legacy old 선언을 구분. AST 단일 literal/재바인딩 검사는 유지 | 각 executor의 실제 bootstrap·전환 거부 관측은 P2 |
| product._workspace_product_once:263–354 | Init/history reader·paired schema reader의 P1b 범위, line 307 planning-capable entry-1, verified window에 따른 live launcher/payload/truth mapping(337/345/350) | Repair candidate gate(310), mixed/pending O/N·새 schema receipt의 쓰기/복구, repair observations(340), pending candidate launcher(346–347)의 전환 허용 조건은 P2에서 완성·실행 검증 |

공유 함수 안에서는 P1b의 collision-free entry-1 init 관측과 historical reader가 필요한 mapping을 먼저 만들되, P2의 transition/pending/repair 동작을 미리 PASS로 간주하지 않는다. 특히 repair/pending branch의 `hv2` literal을 무조건 colvia로 바꾸지 않는다. Verified active/candidate window, exact allowed prefix, snapshot exclusion과 보존 규칙을 함께 판정한다. Actual P1b byte/selection 검토에서 아직 필요한 P2 경로가 호출되면 실행 범위를 숨겨 늘리지 말고 해당 결합을 미결로 남긴다.

**N10 — Fixed OLD fixture inputs.** P1a authoring 시 fixed child program 안에 Git/non-Git target 선택, init/detach operation IDs와 timestamp literals를 명시한다. 선택한 topology와 상수를 실제 program/command digest와 함께 검토 입력에 고정하고 환경·현재 시각·난수나 CLI 자유 인자로 정하지 않는다. 이번 문서에는 아직 존재하지 않는 실제 program digest나 test ID를 만들지 않는다. OLD init → verifier/snapshot → detach preview → exact after-receipt exception → 보존 검사 순서와 `focused p1-controls` 포함은 유지한다.

### Owner Decision Packet

이 보정안은 Reviewer가 요구한 B-1 교정과 Driver의 static delta 검사를 마쳤다는 판단을 위한 입력이다. Reviewer가 revision 2.1을 확인했다고 기록하지 않는다. 추가 전체 packet 재검토는 자동 진행하지 않는다. Owner가 이 delta와 기존 조건부 검토로 설계 판단을 할지, 별도 검토를 요청할지 결정한다.

다음 결정은 분리한다: (1) P0 base의 한정 결과 수락, (2) exact revision 2.1의 설계 수락과 append 기록, (3) controls 동결·E 재검증 경로·보존 기간과 P1a authoring 범위의 수락. P1a는 새 test module, runner, observer, controller, prefix-oracle, controls README와 이 기록에 한정한 60분·후보 1회 제안이다. 실제 바이트 검토와 실행 승인·R1/Owner 결과 수락은 이후 별도다. 이 문서 작성 승인을 어느 항목의 수락으로도 바꾸지 않는다. Runtime/tests/controls와 Accepted DR는 그대로다.

### Validation And Custody

Correction-02와 최신 Reviewer 원문을 보존한 채 이 절과 current disposition만 추가했다. Exact amendment의 다섯 국소 변경(번호 하나와 위 네 곳)을 비교하고, 여섯 함수·CLI·oracle·관련 DR/controls 원문의 line/hash를 고정했다. GFM에서 코드 밖 literal emphasis가 없고 기존 local link 29개와 whitespace가 유효함을 확인했다. 다른 117개 source 입력의 bytes/modes, base/tracked diff, 기존 private custody와 durable 사본 readback 결과는 보존된 input identity의 static_checks에 기록한다. 이 검사는 문서·입력 보존 검사이며 product/test 실행 결과가 아니다.

Private `p1-preparation/correction-03`에는 current record 사본, delta packet, input identity만 둔다. Delta는 correction-02의 기존 exact packet과 review record를 경로/해시로 참조하며 전체 source나 이전 packet을 새로 복제하지 않는다. 소비자는 Owner의 다음 설계/작성 판단과 exact-input handoff다. 그 판단과 후속 입력 사용이 끝나고 고유 bytes가 동등하게 보존될 때까지 필요한 사본을 유지한다. 재생성 가능한 scratch/render/check output은 영구 산출물로 삼지 않는다. Source/OLD checkout은 기존 P1 재사용 및 controls 재검증 소비자가 남아 있어 유지한다.

## P1 Owner Acceptance And Authoring Start — 2026-10-10

Owner는 correction-03 완료 보고 뒤 다음 세 항목을 명시적으로 묶어 요청한 승인에 “진행해”라고 답했다. 아래 수락을 각각 기록한다.

1. P0 base r01의 선택된 20/20 PASS 결과를 그 한정 범위로 수락했다. 기록된 네 controller 단계와 실제 선택 20건의 결과만 해당한다. 미선택 756 occurrences, entry-1 기능, 일반 host confinement 또는 실제 adopter 검증은 수락 결과에 포함되지 않는다. 이번에 base를 다시 실행하지 않았다.
2. Exact amendment v2.1과 correction-03까지의 보완 계획을 설계로 수락했다. Amendment SHA-256 `2cf4f0b07fad00b137328d6aa416652af772011d1583e929c0f86ef2ecbb12f0`, accepted task SHA-256 `0fe55811e16c36ac1c537051881429772b40a8ac2f4a4834ac8ceb89deb90e4b`, delta packet SHA-256 `464769a35a1f6f537a247be26b8041e46e19fa473a48f19a68c50fd4abd5c7c0`다. 기존 correction-02 조건부 R0와 Driver의 국소 delta 검사를 근거로 이 보정에 추가 전체 packet 재검토를 요구하지 않는 경로를 승인했다. 이는 actual-byte R0/실행 계획/R1의 면제가 아니다. Alias/진단·init/replay/detach 의미, P1b/P2 단계, 11-member controls 동결, pause 및 내부 시간 상한, E 재검증 경로·OLD 보존 목적과 root 간 누적 ledger가 그 설계 범위다. DR-0004에는 [named acceptance append](../decisions/DR-0004-colvia-managed-entry-and-one-way-transition.md#accepted-amended-entry-diagnostics-and-fresh-init-admission-v21--2026-10-10)를 추가하고 이전 accepted bytes/frontmatter를 보존했다. M3/제품 활성화는 별도다.
3. P1a 검증도구·fixture 작성 1회·최대 60분을 승인했다. Editable code는 `tests/test_entry_window_transition.py`, controls의 `runner.py`, `observer.py`, `controller.py`, `prefix-oracle.json`이며 설명은 controls README와 이 기록이다. 위 DR append는 설계 수락 기록이며 runtime 작성 범위가 아니다. Common/acquire/canary/baseline/seeds/SBPL, product/runtime/default tests, index/STATUS는 바꾸지 않는다.

작성 시작은 2026-10-10 03:13:04 UTC, 종료 상한은 04:13:04 UTC다. 후보 하나를 작성하고 import 없는 syntax/AST·JSON·문서·범위 보존 검사를 수행한다. Test import/collection/execution, 새 검증 root, Reviewer CLI는 실행하지 않는다. 완료 기준은 factory/context/fixture와 pause·slot·oracle의 실제 bytes, 고정된 case/command 식별 정보 및 다음 actual-byte review 입력이다. 범위 밖 변경, 새로운 계약 선택, 지원하지 않는 경로 또는 시간 한도에 도달하면 현재 bytes와 미완료 항목을 보존하고 중단한다. 작성 완료를 test PASS나 P1b 진입 승인으로 표시하지 않는다.

보존 소비자는 actual-byte Reviewer/Owner와 후속 승인된 synthetic 검증이다. Authoring bundle에는 before identity와 승인 범위, 필요한 변경 파일의 exact bytes/최종 기록 및 bounded review packet만 유지한다. 전체 source/실행 환경을 새로 복제하지 않는다. 이 소비와 필요한 recovery가 끝나고 고유 bytes의 동등한 보존을 확인하면 추가 사본은 기존 규칙에 따라 정리한다.


## P1a Authoring Candidate 01 — 2026-10-10

### 완료 범위와 현재 판정

Owner가 승인한 60분·후보 1회 안에서 controls/factory 후보를 작성했다. 현재 상태는 **실제 바이트 검토 대기**다. P0 base의 한정 결과와 v2.1 설계 수락은 위 기록대로 유지한다. 이번 후보의 동작 PASS, controls 동결 수락, P1b 착수 또는 M3 활성화는 주장하지 않는다. 추가 reviewer 호출, import/collection/test 실행, 새 verification root, Git commit/push는 수행하지 않았다.

| 작성 영역 | 실제 내용 | 남은 증거 |
| --- | --- | --- |
| runner / factory | 검증된 invocation으로 만든 10-field readonly context, local TestCase factory, empty/duplicate/default-overlap 거부, p1-controls selection 제한 | 실제 import 순수성·collection ID/digest·실행 결과 |
| controller | 단일 entry slot 상수와 파생 run names, p1-controls 두 slot, validated phase 기록과 source/controls/phase 재시도 거부 | changed-controls base 및 entry 검증 |
| observer | 현재 WORK 경계, 실제 lock-acquired pause, 원래 I/O handshake, fd/inode/PID/PGID, 15/60초 닫힌 상한, fixed prefix canary와 pause/fault 병용 | timeout/link/token/cleanup 및 OS 동작 |
| 역사 fixture | literal planning-1 schema1; exact OLD init→verify/snapshot→detach after-receipt schema2 child | synthetic construction/OLD 실행 및 P2 reader 판정 |
| 향후 product tests | entry membership·충돌/operation matrix·old reader/write refusal·선택된 prefix와 T-A tears·schema3 detach·late OLD detach | P2/P3 제품 작성 및 검증; 전체 매트릭스는 아직 없음 |

AST에서 정적으로 열거한 intended test ID는 control/fixture 19개, future-product 13개다. 실제 discovery 수나 PASS 수가 아니다. OLD INIT/DETACH와 import probe의 고정 program bytes/hash, 정확한 intended IDs, 변경 파일·전체 입력 식별 및 scoped diff는 private `p1a-authoring-01/review-packet.md`와 `input-identity.json`에 고정한다. Program AST/compile 검사는 실행하지 않고 구문만 확인했다.

### 검증 범위와 미완료 항목

허용된 static check는 Python AST/메모리 compile(모듈 import·코드 실행 없음), embedded fixed-program 구문, JSON 형식, intended ID 중복/노출 구조, 문서 GFM/link, disclosure/whitespace, 승인 파일 밖 bytes/mode 보존, durable readback이다. 이 목록의 실제 결과는 input identity의 `static_checks`에 기록한다. 별도 실행 환경이나 재현 script는 permanent review deliverable로 만들지 않는다.

19개 prefix 번호를 모두 oracle에 유지했지만 번호 존재만으로 coverage를 주장하지 않는다. 현재 selected fd kill 사례는 일부 N/O/B 지점이며, 각 syscall의 전후·각 staging member·모든 OLD operation을 포괄하는 P2/P3 매트릭스는 후속 source-test 작성 범위다. Buffered write는 os.write hook에서 관측되지 않으므로 receipt/staging length 0/1/mid/L-1은 명시적 synthetic tear로만 작성했다. 현재 observer가 제공하지 않는 before/post 증거는 unavailable이며, 추론으로 보충해 PASS 처리하지 않는다. 최종 검토에서 controls interface 부족이 발견되면 동결했다고 선언하지 않고 E 재검증 경로와 그 별도 승인을 따른다.

내부 시간 상한은 synthetic 60/90초, OLD fixture 90/120초, product 150/180초이고 상위 focused 1,200초는 그대로다. 여러 subcase의 실제 소요 시간은 미측정이며 초과하면 자동 연장·retry 없이 실패로 남긴다. Child PID 정리는 test coordinator의 의무, runner 종료 뒤 process-group absence는 controller의 의무다. 구현된 cleanup이 실제 OS에서 성립한다는 판정은 아직 없다.

### 보존과 다음 gate

현재 worktree는 P1 actual-byte review 및 후속 구현에 사용하므로 유지한다. 승인된 OLD와 기존 verification/diagnostic root도 기존 E 재검증·해결되지 않은 failure 소비자가 있어 유지하며 이번에 이동/삭제하지 않는다. 이번 후보의 변경 파일과 작업 기록은 private `p1a-authoring-01/candidate/`에 exact bytes로 보존한다. 소비자는 actual-byte Reviewer, Owner와 수락 뒤 승인된 synthetic validation이며, 그 사용이 끝나고 필요한 유일 bytes가 동등하게 보존되기 전까지 유지한다. 중간 in-progress 사본은 완성 후보의 readback 확인 뒤 대체한다.

다음 한 단계는 이 exact 후보에 대한 fresh read-only R0 1회다. 제안 범위는 본 packet과 기존 수락 계약의 정합성, control/factory 격리, OLD fixture와 실행안의 누락이며 코드 변경·test 실행 권한을 Reviewer에게 주지 않는다. 실제 호출 전에 subscription/auth path, model/session, input drift와 명령·시간 한도를 고정하고 별도 Owner 승인을 받는다. Finding은 원문과 Driver 처분으로 이 기록에 붙이며 자동 수정하지 않는다. R0만으로 실행/동결/P1b를 승인하지 않는다. 후속 synthetic 실행안은 exact 새 root/11 controls/source/selection/명령·누적 ledger를 따로 고정한 뒤 승인 대상이다.


## P1a Actual-byte R0 Attempt 01 — Authentication Failure, 2026-10-10

### Authorization And Exact Input

Owner는 고정 P1a 후보의 fresh Claude R0 1회·최대 600초, 읽기 전용 검토와 응답 원문·Driver 처분 기록 제안에 “진행해”라고 답했다. 자동 수정, test/import/collection 실행, 새 검증 root, Git 작업이나 활성화는 포함하지 않는다. 이 호출은 그 1회 한도를 소비했으며 후속 호출 권한으로 자동 전환하지 않는다.

- Base revision: `238514686078ce1564010a7b69013f48a635c57c`; tracked diff SHA-256: `12238ddc334c4a6971d657249732a73d59cc4c3e32b6463d5a7fccfc867a6b04`.
- Exact packet: 288,712 bytes, SHA-256 `3d721be52afc1483fbed11bed7a25d1c3f93bc1bff8d84838ca77900a18bd8d0`. Authoring input identity SHA-256: `3eeb8596b7ca6c0d5fa736c2a58a845cb5b3a9531bb5cd1c5afe3476694992b3`.
- Reviewed input task SHA-256: `7351e9f062ba6450b934f3be98c02ab2c0b02ea331bfcd7e59baa831450f5dbf`. 이 실패 결과 절은 입력 packet에 없으며, code/control 후보는 unchanged다. Diff 밖의 untracked task/DR/controls/new test module을 포함한 전체 119개 입력은 기존 identity의 bytes/mode map으로 식별했다.
- CLI `2.1.296 (Claude Code)`; fresh session `d47e0da3-8a4f-4458-ad17-354e8fbc2405`. Startup은 `claude-opus-5-5`(Claude Opus 5.5)를 보고했지만 actual model usage가 비어 있고 인증에 실패했다. 모델의 검토 수행이나 판단이 있었다고 확인하지 않는다. Driver가 선정한 packet을 보낸 호출이며 전체 저장소 감사가 아니다.

### Observed Authentication And Failure

직전 `claude auth status`는 `loggedIn=true`, `authMethod=claude.ai`, `apiProvider=firstParty`, `subscriptionType=pro`였다. API-key/provider override 환경 변수는 없었다. 이 값은 당시 CLI 상태 조회 결과이고 유효한 서버 토큰을 입증하지 못했다. 실제 호출은 아래 401 OAuth 만료 오류로 종료했다. 계정 이메일·토큰·키는 기록하지 않았다.

명령은 private `review-01/authorization.json`의 exact argv로 식별한다. `claude -p --model opus --effort medium`, safe/restricted, tools 없음, strict empty MCP, slash commands/settings 비활성화, `--permission-mode dontAsk`, no-session-persistence, verbose stream-json을 사용했다. Cwd는 이 private review 디렉터리이고 fixed packet을 stdin으로 전달했다. 최대 600초였으며 실제 123.17초, exit 1, timeout 없음, `is_error=true`다. Transport result의 `subtype=success`는 오류 판정을 바꾸지 않는다. Tool/MCP 빈 배열, tool use 0건, stderr 0 bytes, malformed stream 0건이며 종료 뒤 process group 부재를 확인했다.

### CLI Final Response — Verbatim Error, Not A Review Verdict

````text
Failed to authenticate. API Error: 401 OAuth access token has expired. Re-authenticate to continue.
````

### Driver Disposition And Resume Condition

| ID | 처분 | 의미와 후속 경계 |
| --- | --- | --- |
| F1 | accept failure / stop | 서비스가 OAuth access token 만료를 반환했다. 직전 상태 조회의 로그인 표시를 근거로 오류를 무시하지 않는다. Code finding이나 Reviewer verdict는 없으므로 P1a R0 미완료 상태를 유지한다 |
| F2 | preserve / no retry | 입력 119개와 base/tracked diff, packet/identity/후보 사본은 호출 전후 동일했다. Test 실행, source/control 수정, API billing 전환, 모델 fallback, 두 번째 호출 또는 로그인 변경을 하지 않았다 |

다음 조건은 Owner가 기존 Claude 구독으로 재인증하고 fresh 재검토 1회·최대 600초를 다시 승인하는 것이다. 로컬 CLI help에서 구독용 명령 `claude auth login --claudeai`를 확인했으며, 여기서는 실행하지 않았다. 재개 시 non-secret auth/billing 경로와 코드·controls·packet 동일성을 다시 확인하고, 이 실패 기록만 추가된 current task identity를 명시적으로 반영해야 한다. 기존 실패 호출을 삭제하거나 횟수를 0으로 바꾸지 않는다. 같은 packet의 새 호출은 별도 attempt로 기록한다.

후속 검토가 완료되더라도 synthetic 실행, control freeze/Owner 결과 수락, P1b 및 M3는 각 gate를 유지한다. 현재 source 후보는 여전히 미실행이며 P0의 과거 한정 PASS와 v2.1 설계 수락은 변경하지 않는다.

### Validation And Preservation

이 기록 외 나머지 118개 source 입력의 bytes/modes와 source membership, base/tracked diff를 보존한다. GFM/link/whitespace와 원문 error SHA-256, durable current-record 사본 readback을 확인한다. 기록 결과와 검사는 compact metadata에 식별한다. Original authoring packet/identity와 8-file candidate 사본은 그대로 유지하므로 이번 실패 절이 과거 검토 입력을 덮어쓰지 않는다.

Private `review-01`에는 authorization, compact metadata와 current record 사본을 남긴다. 원문 오류와 essential transport 상태가 이 기록 및 durable 사본에 보존된 뒤 중복 response stream·빈 stderr·중복 error 파일은 제거한다. 소비자는 인증 복구 뒤 재검토 승인과 exact-input handoff이며, 그 사용이 끝나고 필요한 고유 bytes가 동등하게 보존될 때까지 유지한다. Source/OLD와 기존 verification/diagnostic checkout은 기존 후속 사용·복구 목적이 있어 유지한다. 이번 인증 실패 때문에 작업 환경을 삭제하거나 새 root를 만들지 않는다.


## P1a Actual-byte R0 Attempt 02 — Completed, 2026-10-10

### Authorization, Identity And Actual Execution

Owner는 attempt 01의 OAuth 실패와 재인증 안내 뒤 “재검토 진행”이라고 답했다. 이는 같은 고정 packet의 fresh read-only R0 한 번·최대 600초와 응답 원문/Driver 처분 기록에 대한 새 승인이다. 이전 호출 1회와 실패 기록을 보존했으며 한도를 초기화하거나 자동 재시도하지 않았다. 이번 승인 1/1회, 누적 호출 2회(인증 실패 1회 + 완료 1회)다. 코드 자동 수정, test 실행, 검증 root 생성, Git/활성화는 승인 범위가 아니다.

- Base `238514686078ce1564010a7b69013f48a635c57c`; tracked diff SHA-256 `12238ddc334c4a6971d657249732a73d59cc4c3e32b6463d5a7fccfc867a6b04`.
- Exact packet 288,712 bytes, SHA-256 `3d721be52afc1483fbed11bed7a25d1c3f93bc1bff8d84838ca77900a18bd8d0`. Authoring input identity SHA-256 `3eeb8596b7ca6c0d5fa736c2a58a845cb5b3a9531bb5cd1c5afe3476694992b3`.
- Packet에 들어간 authoring task SHA-256 `7351e9f062ba6450b934f3be98c02ab2c0b02ea331bfcd7e59baa831450f5dbf`; 호출 직전 current task SHA-256 `3d71c05da3fb7b55d8ee201fdeb3ee0909fa14a7447204a06133b492ab7113fc`. 차이는 이전 인증 실패 기록과 current disposition뿐이다. Candidate 코드/controls와 packet은 동일하다. 이번 결과 절은 검토 입력에 없다. Tracked diff 밖 untracked 입력도 전체 119개 map으로 식별했다.
- Auth 조회는 `claude.ai / firstParty / pro`, loggedIn=true였고 API-key/provider override 환경 변수는 없었다. 이번에는 실제 요청도 완료됐다. CLI `2.1.296 (Claude Code)`, 실제 모델 Claude Opus 5.5 (`claude-opus-5-5`), fresh session `2ce19a6f-e00e-4d01-a819-eb357df95eb8`이며 modelUsage도 같은 모델을 식별했다.
- `claude -p --model opus --effort medium`, safe/restricted, tools 없음, strict empty MCP, slash commands/settings 비활성화, dontAsk, no-session-persistence, verbose stream-json으로 호출했다. Exact argv는 private authorization에, cwd는 private `p1a-authoring-01/review-02`, stdin은 fixed packet이다.
- 358.22초, exit 0, timeout/error 없음, tools/MCP 빈 배열·tool use 0·stderr 0 bytes·malformed stream 0건, process group 부재 확인. Source 119개 bytes/modes/membership, packet/identity, 이전 review-01 custody, base/tracked diff 전후 일치 PASS. Runtime/test 실행과 재현 counterexample는 없으며 test PASS 수는 해당 없음이다.

새 session이지만 Driver가 고른 packet과 수락 기록/발췌에 한정된 검토다. 전체 저장소를 읽거나 OLD API를 실행하지 않았다. 이전과 같은 Claude 계열의 Reviewer이며 독립된 모델/session 판단을 실제 실행 증거로 확대하지 않는다.

### Reviewer Response — Verbatim

````text
# P1a Candidate 01 — Actual-byte R0 (정적, 읽기 전용)

packet 바이트만 읽고 추적했다. 실행·import·해시 재계산은 하지 않았고, 아래 내용은 PASS·동결·실행 승인이 아니다.

## 1. 요약

- **P1a 실행 blocker**: 정적 추적으로 확정되는 것은 없다. p1-controls 19개 중 `OldFixtureTests.test_actual_old_schema2_prefix`를 제외한 18개는 control 4개와 factory 코드 경로상 의도대로 도달한다. 제외한 1개는 OLD API가 packet에 없어 확인하지 못했다(L1).
- **동결 적합성**: Driver/Owner 결정이 필요한 항목이 2건 있다(F1, F2). 지금 고치지 않으면 P2에서 E 재검증 경로가 필요해질 수 있다.
- **nonblocker**: 9건. 대부분 테스트 모듈이나 README 쪽이라 controls digest에 영향이 없다.
- **다음 제안**: 공급된 바이트는 6회 bounded validation 제안의 입력으로 쓸 수 있다. 다만 F1/F2 처분이 먼저 필요하다.

## 2. Blocker

확정 blocker는 없다. 추적 결과는 다음과 같다.

- **import 체인**: BOOTSTRAP → `runner.py` → `import controller` → `common` 순서로 로드된다. `controller.py` 최상위는 상수와 함수 정의뿐이고 `__main__` 가드가 유지된다.
- **base 호환**: `observer.py`는 base phase에서 `work=None`이고 pause가 없는 5-key scenario를 그대로 받는다. `canary.py`의 primitive, short-write, lock-object, lock-fd 경로와 호환된다. `observed_flock`의 `detail` 추가는 canary가 `event`만 읽으므로 영향이 없다.
- **controller**:
  - `allowed()`는 base 4개 모드와 기존 entry slot에 대해 이전과 같은 결과를 내고, `p1-controls` 두 이름만 추가된다.
  - `require_new_collection`은 base→entry의 동일 source/controls를 phase로 구분한다.
  - `inputs.json`에 `phase`가 기록된다.
- **context 검증**: `build_execution_context`와 `_validated_context`는 10필드, 타입, 파생값을 양쪽에서 다시 대조한다. `test_readonly_context_and_command_identity`의 변조 5건은 모두 `RuntimeError`에 도달한다.
- **pause 경로**:
  - `emit` 안에서 `active=True`인 상태로 `pause_after_lock`이 실행된다. 그래서 handshake의 `original["open"]` audit 이벤트는 기록되지 않고 fault 횟수에도 들어가지 않는다.
  - `lock-prefix-canary`의 이벤트 순서는 lock 파일 audit-open → attempt → acquired(pause) → probe open/write/fsync이다.
  - `_pause_fault`는 `write-after`를 로그에 fsync한 뒤 SIGKILL하므로 `rows[-1]` 단정이 실제 kill을 가리킨다. 1바이트 short-write는 `b's'`가 남는다.
- **부정 사례**: wrong token, timeout, symlink, hardlink, existing은 각각 `require` 또는 `unlinked_path` 예외로 끝나고, `with` 종료와 프로세스 종료로 lock이 풀린다.
- **선택 제한**: `focused-p1-controls`는 `verification_stage == "p1-controls"`인 factory 객체만 고를 수 있다. `EntryProductTests`는 `"p2"`라 선택되지 않는다.
- **ID 수**: 본문에서 세면 control 18 + OLD fixture 1 + product 13이고 packet 목록과 일치한다. `PREFIX_IDS`도 oracle의 19개 step 순서와 일치한다.

## 3. 동결 적합성 — 결정 필요

**F1. root 디렉터리 fsync 지점을 fault로 지정할 수 없다** (`observer.py` `main`의 fault 검증, `path_of`)

- `path_of`는 target 자신의 fd에 대해 `"."`를 돌려준다. 그런데 `relative(fault["path"])`는 `"."` 성분을 거부한다("unsafe input member").
- 그래서 oracle N-05("N file and root directory fsync")와 O-02("root directory sync after O unlink")의 root-dir `fsync-after`는 관측은 되지만 kill 지점으로 선택할 수 없다.
- oracle 문구상 "unavailable"로 처리할 수는 있다. 다만 P2가 이 지점을 요구하면 observer 변경이 필요하고, 그것은 E 경로다.
- 최소 보정안: fault path에 정확히 `"."`를 `fsync-after`에 한해 허용한다. 또는 N-05/O-02의 root-dir kill을 unavailable로 명시 수락한다. 선택은 Driver/Owner 몫이다.

**F2. "before" kill 지점은 `write-before`뿐이다** (`observer.py` fault event allowlist)

- `audit-before:*`는 로그에만 남고 fault 대상이 아니다.
- oracle의 "before/after each actual matching operation" 중 open, fsync, fchmod, unlink, replace, mkdir의 before는 "직전 연산의 after"로만 근사할 수 있다.
- 이 근사를 동결 해석으로 수락할지, 아니면 unavailable로 둘지를 기록해야 한다. 코드 변경이 필수는 아니다.

## 4. Nonblocker

| # | 위치 | 내용 | 최소 보정 |
|---|---|---|---|
| N1 | `test_release_links_and_reused_paths_refuse` | symlink/hardlink 사례가 `b'RuntimeError'`만 단정한다. `pause release timeout`도 통과하므로 거부 원인을 구분하지 못한다. | `b'linked path'`와 `b'handshake file kind/size'`를 각각 단정 |
| N2 | `test_factory_construction_has_no_writes_or_processes`, `snapshot` | `snapshot(work_root)`는 nlink≠1에서 예외를 낸다. 지금은 알파벳 순서상 hardlink 사례보다 먼저 돌아 문제가 없지만 순서 의존이 숨어 있다. 실패는 error로 드러나고 false PASS는 아니다. | hardlink를 한 디렉터리로 격리하거나 순서 의존을 주석으로 명시 |
| N3 | `test_observer_rejects_cross_work_target` | 같은 root의 `collect-p1-controls/work`가 있어야 한다. controller는 focused 전에 해당 collect의 성공을 강제하지 않는다. | 실행안에 순서와 전제를 명시 |
| N4 | `FixtureBase.cleanup_children` | `wait()` 뒤의 `os.kill(pid,0)` 단정은 사실상 항상 참이고 손자 프로세스를 보지 못한다. 한 child에서 단정이 실패하면 나머지를 정리하지 않는다. | 문서대로 controller의 group 검사에 의존함을 유지하고, 루프는 모두 정리한 뒤 단정 |
| N5 | `runner.Result.preserve` (기존 동작) | 실패 콜백이 cleanup보다 먼저 실행된다. paused child가 살아 있는 `base`를 복사하다 오류가 나면 `os._exit(87)`로 focused 전체가 중단될 수 있다. P1a synthetic에서는 가능성이 낮다. | 한계로 기록 |
| N6 | README "Fixed Modes And Bounds" 표 | collect 7개 slot, focused 4개 slot으로 남아 있다. `ENTRY_MODE_SLOTS`는 8개와 5개다. 관측자 절의 "exact 5 keys" 문구도 옛 내용이다. | README만 갱신 (controls digest와 무관) |
| N7 | `prefix-oracle.json` `control_contract` | observer의 `{15, 60}`과 factory의 60/90/120/180 상수와 기계적으로 묶여 있지 않다. 테스트는 oracle을 리터럴과만 비교한다. | factory가 oracle 값에서 상한을 읽거나, 중복 상수임을 명시 |
| N8 | 미검증 negative | 다음 경로에 synthetic 사례가 없다: "fault occurred before matching pause release", "requested pause/fault was not observed", ready==release 또는 target 내부 경로, base phase의 pause 거부. | P1a 범위로 넣을지 결정. 테스트 쪽 추가라 controls는 불변 |
| N9 | `IMPORT_PROBE_PROGRAM` | audit 목록에 `os.replace`, `os.symlink`, `os.link`, `os.truncate`, exec류가 없다. 이 테스트는 부분적 순수성 증거다. | 한계로 기록하거나 목록 확장 (테스트 쪽) |

observer의 entry WORK 검사는 호출한 run이 아니라 scenario가 놓인 WORK를 기준으로 한다. 다른 run의 scenario에 대한 쓰기는 `test.sb`의 WORK 한정에 의존하며, 설계 문구와 일치하므로 지적 대상은 아니다.

## 5. 증거 한계

- **L1. OLD API**: `_OLD_PROGRAM_BASE`와 `OLD_DETACH_PROGRAM`이 가정하는 다음 항목을 확인할 수 없다. OLD `product.py`가 packet에 없다. 불일치하면 error로 드러나고 false PASS는 아니다.
  - `workspace_*_preview/apply` 시그니처와 `state['inventory']`, `state['binding_ref']`의 형태
  - `.hrn/detached.json` 경로
  - `inject_at='after-receipt'` 시점에 receipt 외 새 멤버가 없다는 점
  - `InjectedCrash.point`와 `.code`
- **L2. schema1 리터럴**: `schema1_fixture`의 레코드 필드가 실제 planning-1 형식과 맞는지는 P2 reader가 판정한다. `test_schema1_independent_inventory_binding_and_suffix`는 자기 구성물의 자기 일관성만 본다.
- **L3. OS/sandbox**: 다음은 모두 미실행이다. 특히 `test.sb`에서 `os.link`가 거부되면 hardlink 사례는 error가 되며, 그때 정책을 넓히면 안 된다.
  - WORK 내 `link(2)`와 `symlink`
  - `F_GETPATH`, flock, 자기 SIGKILL
  - 15초 안에 ready에 도달하는지
  - 90/120초 coordinator 상한이 충분한지
- **L4. 해시와 정적 검사**: packet의 SHA-256(controls 11개, 프로그램 4개, 발췌)은 재계산하지 않았다. `input-identity.json`의 `static_checks`와 기존 tracked diff는 packet에 없다.
- **L5. 프로그램 고정**: 고정 프로그램 해시는 런타임에 강제되지 않는다. 테스트 모듈의 `source_files` digest로만 간접 고정된다.
- **L6. product 테스트**: `EntryProductTests` 13개는 P2/P3 대상이다. 정합성, 19-group 매트릭스 완전성, 제품 정확성은 이번 판정 범위 밖이다.

## 6. 다음 bounded validation 제안 지원 여부

공급 바이트는 base 4회 + entry collect/focused p1-controls 2회 제안의 입력으로 쓸 수 있다. 제안 전에 고정해야 할 것은 다음과 같다.

1. F1/F2 처분. 수정하면 `observer.py` digest가 바뀌므로 변경분 재검토가 필요하다.
2. 새 ROOT, invocation 2개(base/entry), `source_files`와 `source_root_entries`. 새 테스트 모듈과 기존 tracked diff가 여기에 들어가야 한다.
3. p1-controls 19개 exact selection과 collection hash 바인딩 절차.
4. collect → focused 순서(N3)와 누적 ledger.

N1~N9는 실행 전에 고치지 않아도 false PASS를 만들지 않는다. N1만은 link 거부 증거의 해석력에 직접 영향을 주므로 실행 전 보정을 권한다.
````

### Driver Dispositions

Reviewer는 확정된 P1a 실행 blocker가 없다고 보고했다. Driver의 결론은 **정적 검토 완료, controls 동결·실행 보류**다. F1/F2의 실제 공백을 먼저 보정하는 경로를 추천한다. 이는 새로운 제품 정책 선택이나 이미 완료한 코드 수정이 아니다. 아래 추가 source/문서 확인은 Driver만 수행했으며 Reviewer의 검토 범위를 소급 확장하지 않는다.

| ID | 처분 | 근거와 최소 후속 범위 |
| --- | --- | --- |
| F1 | accept gap; needs-user correction | observer의 fault path는 common.relative로 검사해 `.`를 거부하지만 target 자체 fd는 `.`로 관측된다. N-05/O-02의 root fsync kill 선택이 불가능하다. Root 상대 표기를 fsync-before/after에만 명시 허용하고 다른 event/path에는 기존 거부를 유지하는 한정 보정을 제안한다. common의 일반 path 규칙은 바꾸지 않는다 |
| F2 | accept gap; revise approximation | 실제 before hook이 없는 지점을 이전 연산의 after로 대체해 before coverage로 계산하지 않는다. 기존 os wrapper 대상에 닫힌 before event를 추가하고 post event와 구분하는 보정을 제안한다. Python buffered I/O에 여전히 없는 관측은 unavailable로 남기며 synthetic tear와 구별한다. 모든 19-group의 완전성을 이번 변경만으로 주장하지 않는다 |
| N1 | accept; before-execution correction | 모듈 505–524행의 RuntimeError만으로는 링크 검사 거부와 pause timeout을 구분하지 못한다. symlink는 linked path, hardlink는 handshake file kind/size 원인을 각각 단정한다. Reviewer의 마지막 “N1–N9는 false PASS를 만들지 않는다”는 일반화는 이 link-refusal 주장에는 적용하지 않는다. Intended negative를 다른 실패가 통과시킬 수 있다 |
| N2 | accept bounded test correction | snapshot의 nlink==1 요구와 남은 hardlink fixture 때문에 factory purity 검사가 순서에 의존한다. 제품 fixture의 엄격한 snapshot 의미는 유지하면서 control purity 관측/fixture 정리를 분리해 순서 의존을 없애는 보정을 제안한다 |
| N3 | accept execution prerequisite | collect-p1-controls 성공과 exact collection binding 뒤 focused-p1-controls를 실행해야 한다. Controller 기능 확대 대신 실제 실행안의 순서·parent receipts·selection/ledger gate로 명시한다 |
| N4 | accept cleanup correction; revise evidence | 한 child에서 실패해도 나머지 정리를 시도한 뒤 오류를 모아 보고하도록 제안한다. wait 뒤 PID 부재는 손자/escape 부재 증거가 아니고 PID 재사용도 가능하다. Process-group 검사는 계속 outer controller 책임이며 추가 session/group를 만들지 않는다 |
| N5 | accept limitation | runner의 addError/addFailure/addSubTest가 보존을 먼저 수행하고 보존 오류는 exit 87로 끝낼 수 있다. 살아 있는 child와의 보존 race는 unavailable/non-pass이며 snapshot 일관성을 보장하지 않는다. 이번 보정에서 runner나 정책을 확대하지 않는다 |
| N6 | accept documentation correction | README 95–96행의 7/4 slot 표와 128행의 5-key-only 문구가 실제 8/5 및 optional pause와 어긋난다. 현재 shape/phase와 entry p1-controls를 반영하도록 제안한다 |
| N7 | accept limitation | Oracle timeout과 코드의 닫힌 상수는 중복이며 현재 검사는 oracle과 literal만 비교한다. 다음 후보는 코드/테스트의 시간 계약 일치를 명시적으로 검사하거나 중복 한계를 정확히 적는다. 승인된 상한을 늘리거나 임의 oracle 값으로 자동 확장하지 않는다 |
| N8 | accept bounded negative expansion | Root fsync/before hook 보정의 양성·음성 사례와 함께 unobserved pause/fault, handshake 경로 충돌/target 내부, base pause 거부 등 실제 구성 가능한 누락 negative를 고정한다. 도달 불가능한 분기를 억지로 재현하거나 정책을 넓히지 않고 그 이유를 기록한다 |
| N9 | revise / partial defend | 부분적 import-purity 증거라는 한계는 수용한다. 다만 os.replace는 별도 os.replace audit event가 아니라 기존 차단 목록의 os.rename을 발생시키므로 그 항목은 이미 포함된다. os.link/os.symlink/os.truncate/os.exec 등 누락된 실제 audit event는 bounded probe 보정 대상으로 검토한다. 모든 OS 쓰기/실행을 막는 보안 경계라고 주장하지 않는다 |

N9의 os.replace 판단은 [Python 3.14 공식 os.replace 문서](https://docs.python.org/3.14/library/os.html#os.replace)의 audit event 설명과 현재 IMPORT_PROBE_PROGRAM을 대조한 정적 판단이다. 해당 문서는 현재 3.14.8로 표시되며 pinned 3.14.7 runtime을 새로 실행해 확인한 결과는 아니다.

| 한계 | Driver 처분 |
| --- | --- |
| L1 OLD API 부재 | accept reviewer limit. Driver는 현재 product.py/workspace.py/errors.py bytes가 OLD baseline manifest의 세 hash와 동일함을 다시 확인했다. product.py:357–360 반환 키, 405–418/501–518 init 인자, 1143–1150/1213–1250 detach 인자·receipt 뒤 crash, errors.py:10–15 point/code, workspace.py:475–501 guard를 읽었다. 고정 child의 해당 API 가정은 source와 일치하지만 실행 PASS는 아니다. 다음 delta packet에 이 좁은 OLD API 발췌와 hashes를 넣는다 |
| L2 schema1 | accept. 현재 P1a case는 독립 literal fixture의 자기 일관성만 검증하도록 작성됐다. 실제 reader 형식 판정은 P2에 남는다 |
| L3 OS/sandbox/time | accept. Link/F_GETPATH/flock/SIGKILL 및 내부 시간 충분성은 전부 미실행이다. 실패하면 멈추며 정책·상한을 자동 확대하지 않는다 |
| L4 해시/static metadata | accept reviewer limit. Driver의 before/after check는 별도 증거다. 다음 delta packet에 compact static-check 결과와 scoped diff identity를 함께 제공한다 |
| L5 program pin | accept. Program bytes는 source_files의 test-module digest로 고정되고 별도 runtime self-hash를 강제하지 않는다. 독립된 두 번째 seal이라고 쓰지 않는다 |
| L6 product assertions | accept. 13개 future-product case와 19-group 완전성·제품 정확성은 이번 결과로 검증하지 않는다 |

### Next Bounded Correction Proposal — Not Executed

추천하는 다음 한정 묶음은 **보정 후보 1회·작성 최대 45분 + 변경분 fresh R0 1회·최대 600초**다. Editable source는 observer.py, tests/test_entry_window_transition.py, controls README와 이 기존 작업 기록 네 파일이다. F1/F2와 위 N1/N2/N4/N6/N7/N8/N9 중 그 파일 안에서 해결 가능한 범위만 다룬다. F1/F2는 코드 보정을 추천하며, coverage 요구를 낮추거나 “직전 after=현재 before”로 인정하는 선택은 제안하지 않는다.

구체적으로 before event는 현재 os wrapper의 open/write/fsync/fchmod/unlink/replace/mkdir/rename/rmdir/chmod에 한정해 operation 직전/직후를 분리한다. Root `.`는 fsync-before/after에만 허용한다. Fixed synthetic selector를 필요한 file/root fsync와 before/post 관측에 한정해 보완하며 임의 code/path/command selector를 추가하지 않는다. Old-source byte writers, 원래 base scenarios 및 readonly WORK/handshake 경계는 유지한다. 두 hook 보정에 필요한 positive/negative tests와 위 좁은 test 품질 보정을 작성하되, 새 fixed program/ID/hash는 실제 결과로 식별한다.

Common/controller/runner/acquire/canary/oracle/baseline/seeds/SBPL, product/default tests, index/STATUS는 바꾸지 않는다. 이 범위를 넘어야 한다면 이유와 미완료 bytes를 보존하고 중단한다. 기존 60분 authoring을 연장하는 것이 아니라 이 결과에 근거한 별도 후보 승인 대상이다. Import 없는 AST/compile·JSON·GFM/link·범위/hash 보존 검사를 수행하고, 이전 packet을 변경하지 않은 delta 입력으로 actual-byte R0 한 번을 요청한다. 새 인증 경로, identity, no-tools, finite timeout 및 before/after 검사를 동일하게 적용한다. Delta Reviewer의 지적은 원문·Driver 처분으로 남기며 그 호출 뒤 자동 추가 수정/호출은 하지 않는다.

완료 기준은 두 fault-selection 공백과 식별한 test/document 보정의 실제 bytes, 변경 전후 identity와 static checks, 좁은 OLD API 보충 발췌, delta R0 응답과 처분이 검토 가능하게 남는 것이다. 범위·시간·인증/비용 경계 실패는 해당 단계에서 중단한다. 현재 이 묶음을 실행하지 않았고 Owner 승인을 기다린다. Synthetic 6회 실행·새 ROOT·invocation/selection/누적 ledger, controls 동결/결과 수락, P1b와 M3는 이후 별도 gate다.

### Validation And Custody

이번 변경은 기존 task 한 파일의 current disposition과 이 review 절뿐이다. 나머지 118개 source 입력, 기존 authoring 8-file candidate/packet/identity, attempt 01의 세 보존 파일은 변경하지 않았다. 응답 원문 SHA-256, GFM/link/whitespace, 역사 본문 보존 및 durable 사본 readback 결과는 private review-02 metadata에 기록한다. 원문을 source와 current-record-copy에 정확히 보존한 뒤 중복 transport·빈 stderr·review.md는 제거한다. Exact argv, actual model/session, essential limits와 결과는 compact metadata/authorization에 남긴다.

소비자는 Owner의 보정 묶음 판단과 후속 exact-input review handoff이며 필요한 고유 bytes가 동등하게 보존되고 사용이 끝날 때까지 유지한다. Source/OLD와 기존 verification/diagnostic 환경은 실제 후속 사용·복구 목적이 있어 유지한다. 인증 실패가 해결됐다는 사실은 그 과거 실패를 지우거나 당시 호출을 성공으로 바꾸지 않는다.


## P1a Bounded Batch 01 — Owner Authorization And Candidate 02, 2026-10-10

Owner는 P1a를 최종 판단 가능한 상태까지 일괄 진행하라고 명시했다. Observer·test module·controls README·이 작업 기록 네 파일의 보정/정적 검사, Claude 독립 검토와 범위 내 후속 보정/재검토, 차단 문제 해소 뒤 합성 검증 여섯 단계, exact root/input/selection/command 고정, 누적 실행량 기록과 보존을 포함한다. 이 범위의 종전 단계별 승인 대기는 이번 승인으로 대체하며 과거 승인·실패·실행량은 그대로 보존한다. Reviewer에게 source edit나 test 실행 권한을 주지 않는다.

시작은 2026-10-10 04:21:17 UTC, 전체 종료 상한은 07:21:17 UTC다. 새 Claude 호출은 최대 2회·각 600초, 합성 검증은 acquire/canary/collect/smoke base와 collect/focused p1-controls의 여섯 slot 각각 한 번·합계 3,600초다. 이번 묶음 시작 시 새 호출/실행 소비는 각각 0이며 이전 P0와 P1a review 호출을 초기화하지 않는다. 실행 전 이전 root/소비량과 새 root를 연결한 ledger를 고정한다. 실제 검증 실패·설명되지 않은 입력 drift·보존 실패는 중단 조건이며 자동 retry 0회다.

허용 범위/설계 확대, 격리 정책·검증 기준 완화, 인증·과금 경로 변경, 예산 초과가 필요하면 중단한다. Controls 최종 동결·Owner 결과 수락, P1b 이후, 실제 프로젝트 적용, Git commit/push/PR/merge는 포함하지 않는다. 정상 경로에서 내부 단계 전환은 Driver가 진행하고, 결과 수락과 다음 긴 묶음의 지시문을 최종 보고에서 함께 제안한다.

### Candidate 02 Changes And Driver Reasoning

- F1/F2: 기존 열 가지 os wrapper에 실제 operation-before hook을 추가했다. Root `.`는 fsync-before/after에만 허용하며 common path 규칙은 불변이다. 기존 lock-prefix canary는 쓰기 뒤 같은 lock 아래 target root를 fsync한다. 임의 코드/명령/경로 selector는 추가하지 않았다.
- N1: symlink와 hardlink negative는 linked path/handshake file kind/size 각각의 원인을 요구하고 timeout을 명시적으로 배제한다.
- N2: factory purity의 WORK snapshot만 regular hardlink 수를 기록하도록 허용한다. 다른 fixture의 single-link 요구는 유지한다. 따라서 앞선 hardlink fixture 때문에 순서 의존으로 실패하지 않으며 링크 자체가 지워졌다고 주장하지 않는다.
- N4: direct child 모두의 정리를 시도한 뒤 오류를 모아 실패한다. wait 이후 PID 부재 단정을 삭제하고 reaping과 outer process-group 증거를 구분한다.
- N6: entry collect/focused slot을 8/5로, scenario optional pause와 현재 control ID 수를 실제 source에 맞췄다.
- N7: oracle와 코드의 closed timeout 상수 중복은 그대로다. 현재 literal 비교가 모든 call site와 기계적으로 묶인다는 주장을 명시적으로 배제했으며 상한을 늘리지 않았다.
- N8: primitive 열 가지 연산의 before/after, pause 뒤 root fsync 두 edge, 잘못된 root/path 선택, handshake 중복/target 내부, 요청 fault 미관측 등 여섯 test ID를 추가했다. 현 고정 selector와 first-lock/path guard 때문에 pause 미관측·release 전 fault가 구성 불가능한 경로는 억지로 새 selector를 만들어 실행하지 않는다. Base pause 거부는 static guard 한계로 남긴다.
- N9: import audit 목록의 link/symlink/truncate/exec/forkpty를 보완했다. os.replace는 기존 os.rename event로 포함된다. 이 probe는 부분적 side-effect 확인이며 OS 보안 경계가 아니다.
- N3/N5: collect 성공·exact identity binding 뒤 focused를 실행하는 전제를 실행안에 묶는다. Runner의 live-child preservation race/exit87 한계는 그대로이며 runner를 수정하지 않는다.

현재 intended control/fixture IDs는 정적 열거 25개, future-product IDs는 13개다. 실제 discovery나 실행 PASS가 아니다. OLD 고정 프로그램, future-product assertions, common/controller/runner/acquire/canary/oracle/baseline/seeds/SBPL, product source, index/STATUS는 변경하지 않았다. No-import AST/compile·embedded program syntax·GFM/link/whitespace·scope/hash preservation은 실제 결과를 private batch identity에 기록한다. 검토에는 변경 bytes/diff, 기존 계약, 좁은 OLD API 발췌와 source hashes, unchanged control 문맥을 제공한다.

### Current Custody And Remaining Execution

Private `p1a-batch-01/authorization.json`이 시작 시 119개 source 입력 identity, 네 파일 범위와 예산을 식별한다. 새 후보와 packet은 이번 Reviewer와 승인된 synthetic 실행/Owner 결과 판단의 exact-input 소비를 위해 보존한다. 이전 authoring/review 기록은 수정하지 않는다. 후속 실행안은 Driver가 같은 범위 안에서 구체화해 기록하고 검토한 뒤 진행한다. 이 절 작성 시 test import/실행, 새 root 생성, 새 Reviewer 호출은 아직 없었다.


### Batch Review 1/2 — Candidate 02 Static Result And Candidate 03 Refinement

Claude Opus 5.5 (`claude-opus-5-5`), fresh session `3ddcfdfb-e38b-4fbf-be9e-b54234e07726`, CLI 2.1.296, claude.ai/firstParty/pro로 호출했다. 252.36초, exit 0, timeout/error 없음, tools/MCP 빈 배열·tool use 0·stderr 0 bytes·malformed stream 0건, 종료 group 부재, 119개 source 입력 및 candidate before/after 일치 PASS다. Packet 296,930 bytes SHA-256 `2cd595314d78f681965b4142dfffa46477d26d88815ebefd103b39b160039790`, scoped diff `2690df654c051e92b125de422729353a67dc7ed70de166e81faf3baeb6c054ca`를 검토했다. 이번 묶음 호출 1/2회이며 기존 P1a 두 호출(인증 실패 1회 포함)은 별도로 유지한다. Test 실행과 재현 결과는 없다. Driver가 구성한 packet에 한정된 정적 검토이고 해시 재계산은 Reviewer가 하지 않았다.

#### Reviewer Response — Verbatim

````text
# P1a Candidate 02 — Delta 정적 검토 (호출 1/2)

packet 바이트만 읽고 추적했습니다. 실행·import·해시 재계산은 하지 않았고, 아래는 PASS·동결·Owner 수락이 아닙니다.

## 1. 결론

- **정적으로 확정되는 P1a 실행 blocker는 없습니다.** 새 6개 test ID는 `test.sb` 변경 없이 의도한 primitive와 거부 분기에 도달합니다.
- **공급된 코드는 6회 bounded validation 입력으로 쓸 수 있습니다.** 코드 blocker는 아니지만 실행 전에 지켜야 할 운영 전제가 하나 있습니다(P1).
- nonblocker 5건은 모두 false PASS를 만들지 않습니다. 고친다면 test module이나 README만 바뀌고 controls 11개 digest는 그대로입니다.

## 2. 실행 전제 (코드 blocker 아님)

**P1. 기록 문서가 source identity 안에 있습니다.**
- 119개 source map에 작업 기록 `CHORE-20261009-002…md`와 controls `README.md`가 들어 있습니다.
- `common.file_map`은 controller 시작 시와 종료 후 `config()` 재검사에서 이 바이트를 대조합니다.
- 이번 검토 원문과 처분을 CHORE에 적으면 packet의 해시 `7c1be49f…`는 낡은 값이 됩니다.
- 따라서 처분·실행안 기록을 먼저 끝낸 뒤 `source_files`와 `source_digest`를 고정해야 합니다.
- acquire-base부터 focused-p1-controls 종료까지 두 문서를 고치면 `input bytes/mode drift`로 non-pass가 되고 slot이 소모됩니다. 중간 기록은 private 쪽에 두어야 합니다.
- invocation의 `source_files`가 실제로 119개 전체인지는 별도 준비 중이라 확인하지 못했습니다.

**P2. invocation 구성(정적 추론).**
- `runner`는 collect 외 모드에서 `collection_sha256` 일치를 요구하므로, invocation은 base/entry 각각 null과 bound로 4개가 필요합니다.
- `completed()`는 controls·runtime·git 일치만 보므로 네 파일의 `controls`가 같아야 합니다.
- entry focused의 `selection`은 `verification_stage=="p1-controls"`인 25개 ID의 부분집합이어야 합니다.
- `LIMITS` 합계는 300+300+300+1200+300+1200 = 3,600초로 승인 상한과 같습니다.

## 3. F1/F2 보정 확인 (`observer.py`)

- **fault event 집합**: 10개 연산 × before/after = 20개입니다. `write_bytes`는 여전히 `write-after` 전용입니다.
- **root `.`**: `fsync-before/after`일 때만 `relative()`를 우회하고, 그 외 경로는 종전 거부가 유지됩니다. `lock-prefix-canary` 가드의 연산자 우선순위는 `A or (B and C)`로 의도와 같습니다.
- **before hook**: 10개 wrapper 모두 `original[...]` 호출 직전에 `emit`합니다. after는 정상 반환 뒤에만 나옵니다. 재진입은 `active`로 막히고, `os.kill`의 audit event도 `active`로 무시됩니다.
- **canary의 root fsync**: `os.open(target)`에서 `path_of`가 `"."`를 돌려주고, 이어지는 `os.fsync(root_fd)`가 `fsync-before/after "."`를 냅니다. pause release 이후이므로 `fault occurred before matching pause release` 단정은 참입니다.
- **base 호환**: `canary.py`는 `required <= events`, short-write, `lock-attempt/acquired`만 봅니다. 이벤트가 늘어도 영향이 없고, lock/lock-fd canary에는 os wrapper가 설치되지 않습니다.
- **기존 test**: `test_pause_resume_holds_real_lock`의 `'ready'/'release' in path` 부정 단정은 새 `"."` 경로와 충돌하지 않습니다. `test_file_and_fd_pause_selectors`의 정확한 2-event 단정도 유지됩니다.

## 4. 새 test 추적

| test | 추적 결과 |
|---|---|
| `test_primitive_file_fault_before_after`, `test_primitive_namespace_fault_before_after` | 20개 edge 모두 `rows[-1]`이 kill 지점과 같습니다. `matched` 필터는 경로·연산당 정확히 1~2건입니다. open/write/fchmod/unlink/replace/mkdir/rename/rmdir의 상태 단정은 before/after를 실제로 구분합니다. |
| `test_root_fsync_pause_and_fault_edges` | ready → release → probe 전체 쓰기 → root fsync edge에서 SIGKILL 순서입니다. `matched`는 `"."`의 fsync 이벤트만 잡습니다. |
| `test_root_fault_rejects_other_events_and_unsafe_paths` | 세 경우 모두 `events.open("x")` 이전에 의도한 `require`에서 끝납니다. |
| `test_pause_rejects_overlapping_or_target_handshakes` | 두 경우 모두 `"pause paths"` require에 도달합니다 (NB1 참조). |
| `test_unobserved_fault_is_not_success` | `fchmod`가 1회뿐이라 canary가 끝까지 돌고 마지막 `require(fault is None)`에서 실패합니다. |
| `test_release_links_and_reused_paths_refuse` (N1) | symlink는 `unlinked_path`의 `linked path:`, hardlink는 `read_handshake`의 nlink 검사에 걸립니다. traceback이 실패한 소스 줄을 되비추지만 timeout `raise` 줄은 나오지 않아 부정 단정이 유효합니다. |

## 5. 이전 처분과 실제 코드 대조

| ID | 판정 |
|---|---|
| F1, F2 | 반영됐습니다 (§3). "직전 after = before" 근사는 없습니다. |
| N1 | 반영됐습니다. 원인별 단정과 timeout 배제가 들어갔습니다. |
| N2 | 반영됐습니다. `allow_hardlinks`는 factory purity snapshot에서만 쓰이고 기본값은 종전과 같습니다. symlink는 종전처럼 기록됩니다. |
| N3 | README의 6-call 순서로 명시됐고 controller 강제는 없습니다. 실행안에 묶어야 합니다. |
| N4 | 반영됐습니다. 전부 정리한 뒤 오류를 모아 단정하고, PID 부재 단정은 삭제됐습니다. |
| N5 | 한계로 유지됩니다. `runner.py`는 바뀌지 않았습니다. |
| N6 | README 표가 8/5 slot, optional pause, 25개 ID로 맞습니다. "Six additional control tests"도 실제 6개와 일치합니다. |
| N7 | 중복 상수 한계가 README에 명시됐고 코드는 그대로입니다. |
| N8 | 6개 ID가 추가됐습니다. pause 미관측과 release 전 fault가 고정 selector로 도달 불가능하다는 Driver 설명은 가드와 일치합니다. base pause 거부는 실행되지 않습니다. |
| N9 | audit 이름 `os.link/os.symlink/os.truncate/os.exec/os.forkpty`가 추가됐습니다. import 경로에서 이 event는 나오지 않아 오탐은 없습니다. |
| L1 (OLD API) | 발췌 범위에서는 고정 프로그램과 일치합니다(아래). |

**L1 대조 내용**
- 일치: `workspace_init_preview/apply`의 keyword 인자, `verify_workspace_product` 반환 키, `workspace_detach_preview`의 `request`/`confirm_token`, `schema_version == 2` 요구.
- 일치: `_write_exact(receipt)` 직후의 `InjectedCrash('after-receipt')`, 그 `.point`와 `.code`, `.hrn/detached.json` 경로.
- 미확인: `jsonio.canonical_json_bytes`의 형식, `_detach_receipt`의 필드, `_visible_truth`와 `classify_target`의 부작용은 packet에 없습니다. 어긋나면 error로 드러나고 false PASS는 아닙니다.

## 6. Nonblocker

- **NB1** `test_pause_rejects_overlapping_or_target_handshakes`: `b'pause paths'`는 `"pause paths must be exclusive"`의 부분 문자열이라 두 거부를 구분하지 못합니다. 현재 두 경우는 정적으로 앞쪽 require에서 끝납니다. 보정하려면 `assertNotIn(b'must be exclusive', data)`를 추가하면 됩니다.
- **NB2** `_primitive_fault_edges`: `fsync` 양 edge와 `chmod-before`는 이벤트 순서만 증거이고 상태 단정이 없습니다. umask 의존 때문에 타당한 생략으로 보입니다. 한계로 기록하면 됩니다.
- **NB3** README 마지막 문단의 "Both focused executions"는 smoke-base와 focused-p1-controls를 가리킵니다. 모드 이름과 어긋나는 표현입니다.
- **NB4** before/after 선택은 `os` 모듈의 10개 속성 호출에만 적용됩니다. `os.link/symlink/truncate/pwrite`, `shutil`의 native copy, buffered I/O는 여전히 선택할 수 없습니다. P2에서 unavailable로 처리해야 하며 P1a 완료 조건은 아닙니다.
- **NB5** `prefix-oracle.json`은 범위 밖이라 그대로입니다. before hook은 oracle이 아니라 README에만 적혀 있습니다. 기존 limitations 문구와 모순되지는 않습니다.

## 7. 증거 한계 (미실행 OS/runtime 사실)

- 디렉터리 fd의 `F_GETPATH`가 target의 literal 경로를 돌려주는지. P0에서는 파일 fd만 확인됐습니다.
- `test.sb` 아래 WORK 내 `os.link`와 `symlink`가 허용되는지. 거부되면 error이고 정책을 넓히면 안 됩니다.
- 자기 SIGKILL과 디렉터리 fsync는 P0의 base canary에서 유사 경로만 실행됐습니다.
- primitive test 하나가 observer child 10개를 90초 coordinator 상한 안에 끝내는지. emit마다 log fsync가 있고 이벤트 수가 약 2배가 됐습니다. 15초 ready, OLD fixture 90/120초도 측정되지 않았습니다.
- Python 3.14.7의 traceback 출력 형태와 OLD init/detach의 실제 동작.
- 새 ROOT, invocation, selection, command, ledger는 packet에 없어 검토하지 않았습니다.
- packet의 SHA-256과 Driver가 보고한 static check 결과는 재계산하지 않았습니다.
- `EntryProductTests` 13개와 19-group 완전성은 P2/P3 범위라 판정하지 않았습니다.
````

#### Driver Dispositions And Authorized Refinement

- F1/F2와 기존 처분 대조: accept. 실제 before/root hook 보정의 정적 정합성만 수용하며 동작 PASS나 controls 동결로 승격하지 않는다.
- P1: revise premise, accept custody precaution. Reviewer가 본 119개는 전체 검토/보존 input map이다. 실제 준비 중인 invocation source_files는 기존 101개와 새 test module의 102개이며 CHORE와 controls README는 포함하지 않는다. README는 별도 helper hash, controls는 11개 map으로 고정한다. Scope 변경을 숨기지 않고 다음 packet에 actual invocation을 제공한다. 전체 실행 중 source 기록을 수정하지 않고 private ledger만 갱신한다.
- P2: accept. Base null/bound와 entry null/bound의 네 invocation 경로를 고정한다. 현재 파일은 null 두 개이며 bound 두 개는 실제 successful collection으로만 배타적으로 생성한다. Controls는 전부 같은 11개 map이고 entry selection은 부분집합으로 줄이지 않고 P1a 25개 전체를 선택한다.
- NB1: accept and correct. `pause paths`와 `pause paths must be exclusive`가 섞이지 않도록 `assertNotIn(b'must be exclusive', data)` 한 줄을 추가했다. Test 의미와 control code는 유지한다.
- NB2: accept limitation. fsync 두 edge와 chmod-before는 event/call 순서 증거이며 물리적 persistence 또는 umask 독립 mode 증거가 아니라고 README에 명시했다.
- NB3: accept and correct. README의 Both focused executions를 smoke-base and focused-p1-controls runs로 바꿨다.
- NB4/NB5: accept limits. 다른 os API/native copy/buffered I/O에는 선택 hook이 없고 oracle 변경이나 제품 완전성을 이번 범위에 넣지 않는다.
- L1 및 OS/runtime limits: accept. OLD API 발췌의 일치와 아직 실행하지 않은 directory F_GETPATH, link, child/coordinator 시간·traceback·OLD 부작용을 구분한다. 이 사유로 정책/timeout을 늘리거나 실패를 무시하지 않는다.

이 후속 보정은 Owner의 같은 네 파일 범위 안이며 추가 승인을 요구하지 않았다. Observer와 controls 11개의 candidate-02 bytes는 그대로다. 다음 검토는 위 test/document delta와 정확한 실행 입력·고정 helper·명령·누적 ledger를 함께 보는 이번 묶음의 마지막 호출이다. 남은 호출은 1회, 합성 controller 실행은 아직 0/6회다.


### Fixed Six-call Execution Input — Prepared, Not Run

새 root는 `/Users/kyungseo/dev-home/agent-worktrees/hv2-reference-private-colvia-p1a-verification-20261010-b01`다. 지정된 agent-worktrees 바로 아래 non-Git synthetic 실행 경로이며 부재와 등록 worktree 충돌 없음, ancestor의 .git/.hrn 부재를 확인했다. 기존 source/OLD/검증 root를 이동·덮어쓰지 않는다. 생성은 첫 acquire controller가 담당한다.

| 단계 | phase / mode / slot | 상한 | 전제/선택 |
| --- | --- | ---: | --- |
| 1 | base / acquire / base | 300초 | Root 부재, exact baseline 101개 blob의 offline acquisition |
| 2 | base / canary / base | 300초 | 성공한 acquire parent receipt, 기존 named positive/refusal probes |
| 3 | base / collect / base | 300초 | 성공한 canary; 기본 discovery의 원래 multiplicity 보존 |
| 4 | base / smoke / base | 1,200초 | 실제 collection hash로 새 invocation을 배타적으로 bind; 기존 seed 20개 모든 occurrence |
| 5 | entry / collect / p1-controls | 300초 | 위 base 네 단계 성공, 동일 source/controls, factory=True |
| 6 | entry / focused / p1-controls | 1,200초 | 성공한 entry collect와 exact binding; control/fixture 25개 전체, product 13개 제외 |

합계 상한 3,600초에는 dispatcher가 측정하는 helper 포함 실행 sequence 경과도 적용한다. Slot 각각 한 번, 재시도 0회다. 남은 전체/sequence 시간으로 한 단계의 원래 상한을 확보할 수 없으면 시작하지 않는다. Child의 네트워크는 기존 test/acquire 정책대로 차단되고 실제 adopter나 credentials는 주입하지 않는다. Parent 환경은 기존 일곱 키의 clean environment, runtime은 동일 GIL CPython 3.14.7 `-I -S -B`다. Controller cwd는 SOURCE, evidence helper/dispatcher cwd는 private execution 입력 디렉터리다. Controller가 own sandbox child group/timeout/cleanup을 관리하며 외부 monitoring timeout은 controller를 강제 종료하거나 재시도하지 않고 unavailable로 중단한다. Filesystem syscall 선점 불가와 stdout 진단의 가변성 한계는 기존대로다.

Private 실행 입력 식별:

- Base null invocation SHA-256 `5009cbffc3a2c9357e1149bdbfe0fb8f128a207137c37a5193ef05f111eb4b04`, entry null invocation `7fe11771da2d8225d6fdaf5e50cb2cc3d8465d09f3c17b469d9bd77d6cf4910d`.
- Runtime source_files 102개 SHA-256 `91ec8d6334a92617acb16d8b33425a4f185f582f4fed4099b2c3c3c0e0886c5b`; source root names/types, 11 controls와 tool/config identity를 고정했다. CHORE는 runtime source map 밖이며 helper는 README hash를 별도로 확인한다. Dispatcher는 CHORE를 뺀 118개 source 입력을 추가로 보존 검사한다.
- Base evidence plan `df71ea11dda14348a2000c5802675b221f9eb95ec48821095c1cd2d1b285938c`, entry evidence plan `ea95937d0da518af86f55600dcf3bb36b7aaabdfb2628212333a6af6a1320ff3`, 고정 dispatcher manifest `68a8da6d36b445d76df881a740b0abd363c652f653a345ea9d1fd4d611a614b5`.
- Manifest에 여섯 controller argv와 helper 12개 mode의 exact argv/cwd/env, 각 output, runtime/입력 식별과 기존 root parent-evidence hashes가 있다. Base helper는 이전 검토/실행된 bytes 그대로다. 새 entry helper는 그것을 hash 검증 뒤 stdlib-only 정의로 로드하며 SOURCE/test를 import하거나 process를 만들지 않는다. 새 dispatcher는 위 여섯 controller만 순서대로 호출하고 각 helper gate 실패 시 멈춘다. 이번 actual-byte review가 이 새 private helper/dispatcher도 검토한다.
- Bound smoke/focused invocation과 두 binding summary는 아직 없다. 각각 successful canonical collection의 source/control/default/factory/ordered/duplicate/selection을 검증한 뒤 그 collection hash 하나만 달라지는 exact bytes로 xb 생성·fsync/readback한다. 다른 값이나 selection을 통과를 위해 바꾸지 않는다. 두 번째 기록에 실패하면 partial evidence를 보존하고 중단한다.
- 여섯 parent command/env/budget/phase shape를 Driver가 controller source와 독립적으로 구성·대조했다. Python/helper compile은 메모리 syntax 검사만 했고 preflight/helper/controller는 실행하지 않았다.

누적 ledger의 이전 P0는 base attempt 2/4(원 acquisition 실패 1회, r01 네 단계 성공 1회), 실제 controller 호출 5회, diagnostic 2/2, review 10/11이다. 원 `colvia-entry-verification-20261009`, 성공 `colvia-entry-verification-20261009-r01`, diagnostic `colvia-entry-loader-diagnostic-20261009` root와 parent evidence를 보존한다. r02/r03 미사용 allowance를 새 묶음으로 가져오지 않는다. 이전 P1a actual-byte 호출은 2회(인증 실패1/완료1)이고 이번 묶음 준비 시 호출 1/2, controller 0/6이다. P1 preparation 검토 이력은 앞 절에 남으며 이 ledger로 초기화하지 않는다. `accounting-before.json`은 준비 시점이고 이후 소비는 exclusive start marker와 append-only execution ledger 및 이 기록의 후속 결과로 이어진다.

새 helper/dispatcher/input은 이번 실제 실행과 Owner 판단·필요한 후속 재사용 소비를 위한 고정 입력이다. 완료해 재사용/복구 소비가 끝나면 재현 가능한 추가 자료를 기본 영구 산출물로 누적하지 않는다. 현재 source worktree와 이전 root에는 후속 구현/OLD 재사용 또는 실패 이력 소비자가 있어 유지한다. 이 준비는 최종 controls 동결이나 실행 결과 수락이 아니다.


### Batch Review 2/2 — Exact Pre-execution Input Ready

Claude Opus 5.5 (`claude-opus-5-5`), fresh session `eaa11d3a-8362-490c-8d3b-3932972390f3`, CLI 2.1.296, claude.ai/firstParty/pro로 마지막 승인 호출을 수행했다. 303.09초, exit 0, timeout/error 없음, tools/MCP 빈 배열·tool use 0·stderr 0 bytes·malformed stream 0건·종료 group 부재다. Source 119개와 private input 12개, candidate copies가 호출 전후 그대로였다. Packet 449,111 bytes SHA-256 `d12df9b4f4f6e235b9e025e7e63a46cb954bd7d6256670ef300ecceafb58fce1`이다. 이번 묶음 검토 2/2회가 소모됐으며 추가 호출은 하지 않는다. 이는 실행 전 검토이고 실제 결과를 Reviewer가 검토한 것은 아니다.

#### Reviewer Response — Verbatim

````text
# P1a Candidate 03 실행 전 최종 정적 검토 (호출 2/2)

**확정된 실행 blocker는 없으며, 고정된 6-call sequence는 dispatch 가능한 상태로 판단합니다.** packet 바이트만 읽고 추적했습니다. 실행·import·해시 재계산은 하지 않았고, 이 판단은 실행 성공 예측이나 동결·Owner 수락이 아닙니다.

## 1. Blocker

없습니다. 아래 항목을 추적했고 어긋난 곳을 찾지 못했습니다.

- **Parent/child command·env 형상**: 여섯 단계의 `expected_parent_inputs`가 `controller.run()`이 쓰는 `inputs.json`과 일치합니다.
  - 키는 14개로 같습니다.
  - `-D` 순서는 SOURCE, OLD, CONTROLS, WORK, INPUT, OBJECTS, BOUNDARY, LOG, 이어서 ANCESTOR_0~8이며 acquire에는 ANCESTOR가 없습니다.
  - policy는 acquire만 `acquire.sb`이고 나머지는 `test.sb`입니다.
  - 인자 끝의 mode는 runner를 쓰는 단계에만 붙습니다.
  - BOOTSTRAP 문자열, PATH 조립, HOME/TMPDIR/XDG, budget 300/300/300/1200/300/1200이 모두 맞습니다.
  - ROOT 깊이는 ancestor 9개 조건을 만족합니다.
- **네 invocation**: entry null은 base null과 `phase`, `factory`, `selection`만 다릅니다. `controls`·`paths`·`runtime`·`git`·`source_digest`·`source_root_entries`는 같고, `source_files`는 Driver가 고정한 `source_digest`의 동일성에 의존합니다(개별 대조는 §3). bound 두 개는 helper가 `collection_sha256`만 바꾼 canonical bytes로 `xb` 생성하고 다시 읽어 비교합니다.
- **Selection과 factory 순서**: `expected_factory_ids` 38개의 순서가 `loadTestsFromTestCase`의 정렬 결과와 같습니다(EntryControl 24, OldFixture 1, EntryProduct 13). selection 25개는 모두 `verification_stage="p1-controls"`이고 product 13개는 들어 있지 않습니다. `test` 접두 helper 메서드가 없어 의도하지 않은 ID가 생기지 않습니다.
- **base discovery**: 새 test module은 모듈 수준 TestCase가 없어 base `default_ids`에 0건을 더합니다. base helper의 `factory_ids == []` 조건과 entry helper의 default-ID 동일성 조건이 함께 성립합니다.
- **phase 연결**: entry collect에서 `require_new_collection`은 phase가 달라 통과합니다. `completed(smoke, base)`는 controls·runtime·git·config만 비교합니다. focused는 `collect-p1-controls/work`가 있어야 하고 순서상 존재합니다.
- **entry helper**: `runpy.run_path`로 받은 base helper 함수는 자신의 globals dict를 유지하므로 호출할 수 있습니다. `__name__`이 `__main__`이 아니어서 base `main()`은 실행되지 않습니다. 쓰기는 bind의 두 파일뿐이고 subprocess와 SOURCE import가 없습니다.
- **dispatcher**: 고정된 6개 `(mode, slot)`만 실행합니다. token은 정확히 1회 치환합니다. exclusive marker로 재실행을 막고 retry 경로가 없습니다. 감독 timeout에서는 controller에 signal을 보내지 않습니다. 각 gate 실패는 STOP NON-PASS로 끝납니다.
- **False PASS 경로**: after-smoke와 after-focused는 parent result, 재수집 digest, selected 순서, executed row 전부 `["pass"]`, counts 10개 키, unstarted/unfinished 빈 목록, preservation·suite-events·failures 부재를 모두 요구합니다. 실패 하나가 PASS로 집계될 경로를 찾지 못했습니다.
- **NB1 보정**: `"pause paths"` require가 실패할 때 traceback에 나오는 것은 그 호출식의 두 줄뿐입니다. 다음 문장의 `must be exclusive` 줄은 나오지 않으므로 `assertNotIn`이 오탐하지 않습니다. 실제 출력 형태는 미실행입니다.
- **NB3·NB2/NB4 문서 변경**: 코드나 gate에 영향이 없고, helper와 manifest의 README hash `d58d4724…`가 일치합니다.
- **CHORE 분리**: runtime `source_files`에는 CHORE, DR-0004, controls 디렉터리 문서가 없습니다. dispatch 전에 CHORE에 기록해도 `file_map`과 root map은 변하지 않습니다.

## 2. Nonblocker (실행 전 운영 확인)

| ID | 내용 | 권고 |
|---|---|---|
| O1 | dispatcher는 시작 시 전체 잔여 시간을 보지 않고 단계별로만 `deadline − now > budget + 60`을 검사합니다. 늦게 시작하면 중간(특히 focused 직전 1,260초 요구)에서 멈추고 ROOT와 slot이 재시도 없이 소모됩니다. `entry-after-focused`도 deadline 이후면 non-pass입니다. | 최악 경우까지 보장하려면 약 06:19 UTC 이전에 시작합니다. 그 뒤에 시작하면 중간 정지 위험을 명시적으로 받아들이는 것입니다. P0 실측은 총 약 64초였지만 이번 소요의 보증은 아닙니다. |
| O2 | dispatcher 자신의 기동 명령·env·umask가 packet과 manifest에 없고, dispatcher는 `-I -S -B`를 자체 검사하지 않습니다. 자식에는 명시 env를 주므로 false PASS는 아닙니다. | 고정 python `-I -S -B`, 절대경로, cwd는 execution 디렉터리로 기동하고 그 명령을 ledger에 남깁니다. |
| O3 | umask는 dispatcher에서 controller, sandbox, test, OLD fixture로 상속됩니다. OLD product의 umask 민감도는 packet에 없습니다. | P0 r01과 같은 umask(통상 022)로 기동하고 기록합니다. |
| O4 | `execution-started.json`이 `base-preflight`보다 먼저 생깁니다. preflight가 실패하면(예: invocation 파일 mode가 0644가 아님, tool drift) controller 0회, ROOT 미생성인데도 dispatcher는 재실행할 수 없습니다. | 이 상태는 "controller 0/6, dispatcher 소모"로 구분해 기록합니다. marker 삭제는 금지이고 재개에는 새 manifest나 Owner 판단이 필요합니다. |
| O5 | helper는 60초 timeout에서 `subprocess.run`이 강제 종료합니다(controller는 아님). bind 도중이면 파일 하나만 남는 정지 상태가 될 수 있습니다. | 문서화된 partial-binding 정지 규칙대로 처리합니다. |
| O6 | focused용 token 이름도 `<verified-smoke-input-sha256>`을 재사용합니다. | 동작에 영향이 없는 표기 문제입니다. |
| O7 | helper가 읽는 child 증거(collection, executed, counts, stdout)는 child가 쓸 수 있는 WORK와 LOG에 있습니다. | 이미 명시된 한계이므로 결과 보고에서 유지합니다. |

## 3. 미실행·미확인 한계

- **OS/runtime 사실**: 디렉터리 fd의 `F_GETPATH`가 `"."`를 주는지, `test.sb` 아래 WORK 내 `os.link`·`symlink`, 디렉터리 fsync, 자기 SIGKILL, Python 3.14.7 traceback 형태, OLD init/detach의 실제 동작과 출력이 한 줄 JSON인지는 실행해야 드러납니다. 어긋나면 error나 fail이고 PASS로 바뀌지 않습니다.
- **시간**: primitive test의 child 10개와 90초 coordinator 상한, 15초 ready, OLD fixture 90/120초는 측정되지 않았습니다.
- **packet에 없는 것**: `canary.py`, `acquire.py`, `prefix-oracle.json`, `baseline-inputs.json`, `base-seed-ids.json` 본문과 OLD product 소스는 대조하지 않았습니다. 새 observer의 추가 이벤트가 base canary를 깨지 않는다는 판단은 helper의 superset 조건과 1차 검토 결과에 근거합니다.
- **개수와 해시**: `source_files` 102개와 118개의 정확한 개수, 모든 SHA-256, Driver의 static check 결과는 재계산하지 않았습니다. 두 invocation의 `source_files`도 항목별로 대조하지 않았습니다.
- **기존 한계**: runner의 live-child preservation race와 exit 87, 재수집 비결정성은 그대로이며 발생하면 non-pass입니다.
- **범위 밖**: `EntryProductTests` 13개, 19-group 완전성, P1b 이후는 판정하지 않았습니다.

## 4. 준비 상태

- **가능**: 공급된 candidate 03 bytes, 네 invocation 경로, 두 plan, 두 helper, dispatcher, manifest는 서로 정합합니다. O1~O3을 기동 직전에 확인하면 1회 dispatch 입력으로 쓸 수 있습니다.
- **유지할 조건**: sequence가 도는 동안 SOURCE를 수정하지 않습니다. SOURCE 루트에 `.DS_Store` 같은 새 항목이 생기면 non-pass입니다. 첫 실패에서 멈추고 정책·timeout·selection을 바꾸지 않습니다.
- **Reviewer 판정의 범위**: 이 결과는 "실행 전 정적 blocker 없음"까지입니다. 실행 PASS, controls 동결, Owner 결과 수락은 포함하지 않습니다.
````

#### Driver Dispositions And Dispatch Record

- Blocker 없음: accept as static readiness only. 여섯 command/env/phase/selection/parent-result 연결과 candidate03 delta의 정적 정합성을 수용한다. 이 판단을 runtime PASS나 Owner 수락으로 바꾸지 않는다.
- O1: accept operational check. Dispatch 준비 시 전체 deadline까지 남은 시간이 4,680초보다 큰 것을 확인했다(launch record 실제 값 9326초). Dispatcher는 매 단계 남은 시간과 sequence 3,600초 상한을 다시 검사한다. P0 실측으로 이번 충분성을 보증하지 않는다.
- O2/O3: accept and fix launch specification without source changes. Non-login `/bin/sh`의 현재 umask를 `0022`로 관측했다. 같은 child umask를 명시적으로 고정하고 pinned Python `-I -S -B`, absolute dispatcher/manifest, execution cwd, DEVNULL, 기존 clean 일곱-key 환경으로 기동한다. P0 r01의 당시 umask는 별도로 기록되지 않았으므로 과거와 같다고 소급 주장하지 않는다. Exact argv와 shell/umask는 private `dispatcher-launch.json`(SHA-256 `8f7d109290f4570c3d893dc6d244213aaeb27c8d41f8a2046f13f9370dc6550e`)에 기록했다.
- O4: accept. Preflight 전에 생기는 marker도 소비된 dispatcher로 취급한다. 그때 controller 0/6·ROOT 미생성일 수 있으며 marker 삭제나 자동 새 manifest/root는 하지 않는다.
- O5: accept. Helper 60초 timeout은 helper를 종료할 수 있고 bind가 partial이면 그대로 중단·보존한다. Controller나 test child를 독자적으로 재실행하지 않는다.
- O6: accept no-change. Focused도 기존 token 이름을 쓰지만 실제 지정 bound input hash만 한 번 치환한다. 표기만 고치려고 검토된 plan/dispatcher를 변경하지 않는다.
- O7 및 미실행 한계: accept. Child WORK/log evidence는 가변 진단 자료이며 parent 입력/성공/보존 gate와 실제 record 검사 범위만 주장한다. F_GETPATH/link/시간/OLD 동작과 누락 transitive source, future-product13/19-group 전체는 실행/후속 범위로 구분한다.

이 절 뒤 실제 실행은 기존 일괄 승인 안에서 진행한다. Runtime 입력과 controls, README, helper/plan/manifest는 검토한 bytes 그대로이며 이 CHORE 기록만 갱신했다. Sequence가 활성화된 동안 SOURCE를 수정하지 않는다. 이번 여섯 호출의 실제 결과와 각 helper/보존 판정은 종료 또는 첫 중단 뒤 아래에 기록한다. 현재 root는 아직 없고 controller 소비는 0/6이다.


## P1a Batch 01 Actual Result — Bounded PASS, Owner Decision Pending

승인한 네 파일 보정과 두 static Claude 검토, 여섯 controller 실행과 열두 helper gate를 완료했다. 실행 sequence는 77.942초(helper 포함), controller outer 합계 77.116초이며 재시도 0회다. 전체 시작 04:21:17 UTC부터 2026-10-10T04:49:08.999481+00:00까지 3시간 한도 안에 완료했다. 시간은 실제 dispatcher/controller monotonic 관측이며 tool transport wall time을 증거로 쓰지 않는다.

| 실제 단계 | controller seconds | outer/child exit | 결과 |
| --- | ---: | --- | --- |
| acquire-base | 0.661 | 0 / 0 | execution_pass=true, group_absent=true |
| canary-base | 0.678 | 0 / 0 | execution_pass=true, group_absent=true |
| collect-base | 0.47 | 0 / 0 | execution_pass=true, group_absent=true |
| smoke-base | 55.51 | 0 / 0 | execution_pass=true, group_absent=true |
| collect-p1-controls | 0.471 | 0 / 0 | execution_pass=true, group_absent=true |
| focused-p1-controls | 19.134 | 0 / 0 | execution_pass=true, group_absent=true |

Base smoke는 선택한 20/20 occurrence, entry focused는 P1a control/fixture 25/25 occurrence가 모두 PASS다. 두 결과에서 failures/errors/skips/expected failures/unexpected successes/unstarted/unfinished는 모두 0이다. Entry factory는 control24 + OLD fixture1 + future-product13 = 38개를 실제 수집했으며 product13은 선택·실행하지 않았다. Default discovery와 duplicate multiplicity는 보존했다.

- smoke: default 776, factory 0, 전체 발견 776, unique 599, duplicate IDs 177; selected/executed/count SHA-256 `67cb50aed558c9635c8a807d2487fad320fd2f04fbdf80850a62e8a56f9b7835` / `3d0c27deb654a196e7f6e228482cfa1ea59f471846a61aa0d56140792f93cba0` / `72755819d7475a8c593bd0d48650dcc2d7a05359647ab00b79d3ada5bf91db0d`.
- focused: default 776, factory 38, 전체 발견 814, unique 637, duplicate IDs 177; selected/executed/count SHA-256 `2428055f8f23e95773cb0a837f59342ee166a8d873495f7cf5f0ffb5a1d62db6` / `d8708ee4aa4a97c52e2ea7910773605c8190cfc66f228a855bf9d94ad0c43cb1` / `39d3e4cee3763262316ef6895773327e9959845a8921f73571a7af92e93b39c7`.

실제 실행된 증거는 열 가지 primitive의 before/after kill 경계와 해당 physical state 단정, lock 소유·matching pause release 뒤 root fsync 양 edge, 잘못된 root/path·handshake/link/token 거부, timeout 뒤 lock 해제, unobserved fault 실패, 한 바이트 short write, 순수 factory/명령 identity, literal schema1 구성과 exact OLD init→detach after-receipt schema2 보존이다. fsync는 call/event 경계만 확인하며 power-loss durability를 증명하지 않는다. import audit와 snapshot은 부분적 side-effect 증거이고 모든 OS 쓰기나 동시 변경을 막는 경계가 아니다. 실제 source/installed entry-1 전환, 제품 13개, 19-group 완전성, 실제 adopter와 전체 suite는 미검증이다.

Base/entry collection은 각각 successful parent receipt와 source/control identity를 확인하고 canonical ordered/duplicate/selection을 검사했다. Bound invocation은 collection hash만 바꾼 별도 bytes로 배타적으로 생성했고 실제 smoke/focused 재수집 digest가 일치했다. Parent result 자체가 모든 mutable child output을 cryptographically 봉인한다는 주장은 하지 않는다. Source/old metadata·policy qualification은 named probes의 범위에 한정한다.

Driver는 helper와 별도로 실제 parent/input hashes, selected/executed 순서와 pass rows/counts, source118개와 실행 중 CHORE 불변, source membership/base/tracked diff, controls/private fixed artifacts와 이전 증거 불변을 재확인했다. 여섯 child process group 부재도 종료 후 다시 확인했다. 이는 Driver의 실제 read-only 검사이며 Claude가 실행하거나 재계산한 결과가 아니다. Claude 두 호출은 모두 실행 전 static review였고, 실제 결과의 독립 R1은 아직 수행하지 않았다. 이번 호출 예산이 끝났으므로 세 번째 호출을 하지 않는다.

누적 소비는 이번 묶음 review2/2·controller6/6·helper12·retry0이다. P0의 과거 controller5회와 diagnostic/실패, 이전 P1a 두 review는 그대로 남는다. 새 root로 한도를 초기화하지 않았다. Product/default tests, accepted DR, index/STATUS, 실제 project state, Git commit/push/PR/merge와 M3 활성화는 변경하지 않았다.

결과 판정용 private actual-result-summary에는 명령 ledger/parent/count/선택 식별과 핵심 관측만 남긴다. 현 root의 acquired OLD와 결과, source worktree 및 candidate03 exact bytes는 Owner 수락·실제 결과 독립 검토·P1b/P2 후속 사용을 위해 유지한다. 필요한 ignored deliverable은 source 밖 durable bundle에 보존됐으며 새 Git worktree를 만들거나 기존 checkout을 삭제하지 않았다. 최종 controls11 고정과 Owner 결과 수락은 아직 하지 않았다.

### Recommended Next Batch — Proposal Only

다음은 P1a의 한정 결과를 Owner가 판단한 뒤 실제 결과 Claude R1과 P1b/P2 구현·focused 검증을 한 묶음으로 승인하는 경로를 추천한다. P1b는 reader/identity·fresh init와 exact recovery/replay, P2는 S1–S6 전환·복구·충돌 진단·schema3 detach와 OLD writer/prefix 검증이다. Accepted v2.1과 구현 계획의 closed C1 file inventory 안에서만 진행하며 controls11은 고정한다. R1에서 새 차단 문제가 나오면 P1b를 시작하지 않는다.

권장 예산 후보는 전체6시간, 새 Claude 최대4회·각10분, P1b/P2 collect·focused 각1쌍과 필요 시 기존 shared correction1쌍(최대6 controller calls·합계4,500초)이다. Correction은 P1/P2/P3 전체의 기존 shared slot을 소비하며 새 root로 되살리지 않는다. 일반 제품 assertion 실패에 대한 그 한 번의 보정·재검토·재실행을 다음 승인이 명시적으로 포함할 때만 수행한다. 격리/입력보존/인증·과금/범위·계약/예산 문제는 즉시 중단한다. P3 문서 전체 정렬, P4 complete qualification, normative 활성화, 실제 적용과 Git은 다음 경계다. 이 제안은 아직 실행 승인이나 결과 수락이 아니다.


## P1b And P2 Bounded Batch 01 — Owner Authorization

2026-10-10 Owner는 “P1a의 보고된 결과와 한계를 수락한다”라고 명시하고 실제 결과 Claude 독립 검토부터 P1b·P2 구현과 focused 검증까지 일괄 승인했다. 수락 대상은 바로 앞 P1a Batch 01 결과와 명시된 한계이며 task 당시 SHA-256은 `bd656517f77b6081176f8f3cb87026feca0241cf163515114f463dce1e75b33b`다. 과거 미수락 표기는 당시 checkpoint로 보존한다. 이 결과 수락은 제품·전체 suite·실제 adopter 수락이 아니다.

먼저 Claude가 실제 실행 결과와 증거를 R1으로 검토한다. 차단 문제가 없을 때만 검증된 controls11을 최종 고정한 뒤 accepted v2.1과 기존 구현 계획 C1 목록 안에서 P1b(reader·identity·fresh init·recovery/replay), P2(S1–S6 전환·복구·충돌 진단·schema3 detach)를 구현한다. 검토 지적의 근거 확인·처분, 범위 내 보정, 정적 검사와 필요한 검토·focused 실행, 기존 기록과 필요한 증거 보존을 포함한다. 범위 내 단계 전환에는 추가 승인을 요청하지 않는다.

전체 시작은 05:00:28 UTC, 종료 한도는 11:00:28 UTC(6시간)다. 새 Claude 최대4회·각600초다. P1b/P2 collect·focused 각1쌍, 일반 제품 assertion 실패에만 기존 shared correction1쌍을 허용한다. 최대6 controller 호출·합계4,500초이며 correction은 P1/P2/P3 전체에서 한 번이다. 과거 검토·실패·controller 실행량을 유지하며 root/slot 교체로 초기화하지 않는다. 새 인증 확인과 source/input pre/post 검사를 각 reviewer 호출에 적용한다.

R1 차단 문제는 P1b 미착수 중단이다. Controls 변경, 파일·설계 범위 확대, 격리·검증 기준 완화, 인증·과금 경로 변경, 입력·보존 문제 또는 예산 초과도 중단한다. 위 ordinary assertion correction 외 실행 실패를 자동 재시도하지 않는다. P3 전체 문서 정렬, P4 complete qualification, normative 활성화, 실제 적용, commit/push/PR/merge는 제외한다. 작업 기록은 계속 이 문서 하나가 소유하며 final result acceptance는 별도 Owner 결정이다.

현재 호출 소비는 새 review0/4·controller0/6·shared correction0/1이다. P1a의 review2/2·controller6/6·helper12·retry0 및 이전 누적 이력은 유지한다. Source checkout, P1a OLD와 controls/result는 실제 R1 및 승인된 P1b/P2 재사용을 위해 유지한다. 필요한 변경 사본은 source 밖 durable private bundle에 보존한다.


### Actual-result R1 — No Blocker And Controls Freeze

Claude Opus 5.5 (`claude-opus-5-5`), fresh session `0a764b1b-e523-458e-afdd-1f0349e63b98`, CLI 2.1.296, claude.ai/firstParty/pro 경로로 actual-result R1을 수행했다. 169.18초·exit0·timeout/error 없음·tools/MCP 빈 배열·tool use0·stderr0·malformed stream0·group 부재다. 이번 묶음 review1/4, controller0/6이다. 원래 426,332-byte private 패킷 전송은 자동 승인 심사에서 payload/목적지 승인의 구체성 문제로 실행 전에 차단됐으며 호출은 소모하지 않았다. 요청한 검증 코드·합성 증거만 유지하고 source identity map과 실제 사용자/private root 경로를 제거한 패킷으로 재심사한 뒤 허용됐다. 우회 채널이나 과금 경로 변경은 없었다.

실제 전달 패킷은 384,258 bytes, SHA-256 `f4c7365c769d6dbfa0c602a3db4666852859b508549d241dfe777db0e9ceb19d`다. 경로는 일관된 symbolic root로 대체했다. File hash는 대체 전 bytes, packet hash는 전달된 bytes를 식별한다. Reviewer는 실행·import·hash 재계산 없이 고정 증거를 읽었다. Source119개와 기존 evidence, synthetic link의 literal target은 호출 전후 같았다. Driver가 선택한 패킷과 미열람 input의 한계는 아래 응답대로 남는다.

#### Reviewer Response — Verbatim

````text
# P1a 실제 결과 R1 — 판정: 차단 문제 없음 (한정)

패킷 안의 실제 증거와 코드에서 P1a 한정 PASS를 뒤집는 false-pass나 자격 결함은 찾지 못했습니다. 저는 실행·import·해시 재계산을 하지 않았고, 아래 "일치"는 패킷에 적힌 값끼리의 정합성만 뜻합니다.

## 근거

**Parent receipt 체인 (6/6 정합)**
- 각 `result.json`의 `inputs_sha256`이 해당 `inputs.json` 라벨과 모두 일치합니다(6d9cf…, 554e1…, db569…, baf13…, a16db…, 1c667…).
- 여섯 건 모두 `exit=0`, `reason=null`, `natural_completion`·`group_absent`·`inputs_unchanged…`가 true입니다.
- 여섯 건의 `controls` 11개 해시와 `source_digest`(91ec8d…)가 동일합니다.
- `boundary-positive.json`의 PRIOR_RESULT(9cf3f5…)와 PARENT_INPUTS(554e10…)가 acquire result와 canary inputs 라벨과 일치합니다.
- 바인딩 요약의 collection 해시(110d33…, d3bb10…)가 smoke·focused `inputs.json`의 `collection_sha256`과 일치합니다.
- bound invocation 해시(695d7f…, 93deb3…)가 ledger argv와 parent `invocation_sha256`에 일치합니다.

**실행·횟수**
- ledger는 controller 6회, helper 12회, 재시도 0회이고 순서가 manifest 고정 목록과 같습니다.
- outer 초 합계는 77.116으로 보고값과 같습니다.
- ledger의 child PID 6개가 Driver 재확인 목록(8944, 9063, 9106, 9122, 18166, 18171)과 같습니다.

**테스트 선택·실행**
- `selected.json`과 `executed.jsonl`은 25행으로 순서가 같고 모두 `outcomes=["pass"]`입니다. 구성은 EntryControlTests 24개와 OldFixtureTests 1개입니다.
- 테스트 소스의 메서드 수는 control 24, OLD 1, product 13으로 합계 38이며, 814 = 776 + 38과 맞습니다.
- `EntryProductTests`는 실행 행에 없습니다. runner의 `focused-p1-controls` 분기가 `verification_stage=="p1-controls"`만 허용합니다.
- smoke는 20행 모두 pass입니다.
- 행별 초 합계가 unittest 보고와 맞습니다(focused 약 18.776 대 18.780, smoke 약 55.17 대 55.174). `test_pause_timeout_releases_lock`의 15.11초는 닫힌 15초 timeout과 부합합니다.

**Canary 원시 증거의 코드 정합**
- primitive 52행의 순서가 `observer.py`의 primitive-canary 경로와 일치합니다.
- flags 2817은 WRONLY|CREAT|EXCL|NOFOLLOW이고, audit 값 16780033은 여기에 CLOEXEC가 더해진 값입니다.
- lock 두 건은 attempt에서 acquired까지 약 8~10ms로, 부모의 10ms 폴링 뒤 해제와 부합합니다.
- short-write는 `written:1`에서 종료했습니다.
- 명명된 거부 10개는 parent와 child 모두 EPERM(1)입니다.

**Oracle 점검 (정적)**
- 10개 primitive × before/after subTest는 마지막 이벤트, PID, 해당 연산의 before/after 열, 물리 상태를 단정합니다.
- 음성 케이스는 지정 메시지 포함과 `events`/`ready` 부재를 함께 요구합니다. 링크 케이스는 timeout 메시지를 배제합니다.
- subTest 실패는 runner에서 `subtest-failure`로 기록되고 `wasSuccessful`에도 반영됩니다.
- `test_pause_resume_holds_real_lock`은 부모의 `LOCK_NB` 시도가 `BlockingIOError`임을 단정하므로 실제 소유를 확인합니다.

## 비차단 지적

1. **미열람 입력.** controls11 중 `acquire.py`, `baseline-inputs.json`, `base-seed-ids.json`, `prefix-oracle.json` 본문이 패킷에 없습니다. `base-plan.json`, `entry-plan.json`, private invocation 4종, 두 `collection.json`도 없습니다. 38개 factory ID의 정확한 동일성과 599/637 unique는 helper PASS와 Driver 관측에만 의존합니다.

2. **schema1 테스트는 자기정합 검사입니다.** `remove_order` 비교와 마지막 unlink 단정은 fixture 자신의 구성에 대한 동어반복에 가깝습니다. 실제 과거 planning-1 형식과의 일치는 실행 증거가 없으므로, P2 reader 구현의 독립 oracle로 인용하면 안 됩니다.

3. **"timeout 뒤 lock 해제"의 범위.** 증명된 것은 프로세스가 timeout 메시지로 비정상 종료했고 그 뒤 lock이 비어 있다는 것입니다. 생존 프로세스의 명시적 해제는 아닙니다.

4. **결과 문단의 누락.** fsync 한계만 적혀 있고, chmod-before에 물리 단정이 없다는 점(README에는 기재)이 빠져 있습니다.

5. **"duplicate IDs 177"의 의미.** 776 − 599 = 177이므로 잉여 occurrence 수와 같습니다. 중복된 ID의 개수인지는 패킷만으로 확정할 수 없습니다.

6. **README가 실제 결과와 어긋납니다.** "runtime results remain pending", "has not been … executed" 문구가 남아 있고, 결과 본문의 "candidate03"은 README(Candidate 01/02)에 설명이 없습니다. README는 controls11 밖이지만 `source_files`에 포함됩니다.

7. **동결 전 읽기 전용 확인 권고.** 동결될 observer는 다음 제약을 가지며, 모두 fail-closed입니다.
   - `operation == LOCK_EX`와 정확히 같을 때만 lock 이벤트를 냅니다(`LOCK_EX|LOCK_NB`는 관측되지 않음).
   - pause는 lock 파일 크기가 0이어야 합니다.
   - `dir_fd` 사용은 즉시 중단됩니다.
   - buffered write, `os.link`/`symlink`/`truncate`에는 hook이 없습니다.

   P1a는 합성 lock만 실행했고, OLD/NEW `writer_guard`가 이 조건을 만족하는지는 실행 증거가 없습니다. 맞지 않으면 동결 후 controls 변경(Owner 범위)이 필요해지므로, 동결 전에 기존 `product.py`의 `writer_guard`를 정적으로 대조하길 권합니다.

8. **P1b/P2 운용 주의.**
   - `require_new_collection`은 같은 (source_digest, controls, phase)의 두 번째 collect를 거부합니다. P1b와 P2 collect는 source가 달라야 합니다.
   - `SOURCE/colvia`를 추가하면 새 `source_root_entries`가 필요합니다.
   - entry 단계의 선행 확인은 `same_source=False`입니다. base smoke 20/20은 controls 자격이며, 변경될 제품 source의 증거가 아닙니다.

9. **이미 선언된 한계 유지.** child 출력은 가변이고, process-group 부재는 세션을 벗어난 손자 프로세스를 보증하지 않으며, PID 재사용 가능성도 남습니다. 과대 주장은 보지 못했습니다.

## 향후 범위 (P1a 결함 아님)

product 13개, 19-group 전수, entry-1 실제 전환, installed 경로, 전체 suite, power-loss, P3/P4는 P1a 범위 밖입니다.

## 결론과 한계

- **R1 차단 문제: 없음.** 제공된 증거 범위에서 P1a 한정 PASS와, 동일 해시의 controls11을 후속 focused 실행용으로 동결하는 것에 반대할 구체적 근거가 없습니다.
- 이 의견은 본문을 읽은 controls 7개(common, controller, runner, observer, canary, acquire.sb, test.sb)와 테스트 팩토리에 대한 것입니다. 나머지 4개는 해시 라벨 정합만 확인했습니다.
- 이 응답은 Owner 수락, 범위 부여, 제품·전체 자격 판정이 아닙니다.
````

#### Driver Dispositions And Remaining Limits

| Finding | Disposition | 판단과 조치 |
| --- | --- | --- |
| No blocker | accept | P1a base20·control25의 한정 결과 정합성과 동일 controls의 후속 사용만 수용한다. 제품/full qualification은 포함하지 않는다 |
| N1 | accept limitation | 미열람 controls4·전체 collection·OLD 본문은 이전 exact-byte 검토와 Driver custody에 의존한다. 이번 Reviewer가 독립 검증했다고 쓰지 않는다 |
| N2 | accept | Schema1은 synthetic 자기구성 검사다. P1b/P2에서는 literal 역사 계약과 reader/auditor 양성·음성 검사를 함께 확인하며 실제 old schema1 writer 증거로 승격하지 않는다 |
| N3/N4 | accept clarification | timeout 오류로 child가 종료한 뒤 lock 부재만 확인했다. chmod-before는 mode 변화 단정 없이 event/call 순서이며 fsync도 물리 persistence를 증명하지 않는다 |
| N5 | defend | Driver가 실제 duplicates dict177개와 각 값2를 확인했다. 이 실행에서는 중복 ID 수와 잉여 occurrence가 모두177이다. Reviewer의 패킷 한계는 유지한다 |
| N6 | revise premise / preserve historical input | README는 runtime source_files102와 controls11 밖이며 helper가 별도 hash로 식별했다. Candidate01/02 pending 문구는 당시 checkpoint다. 실제 결과·candidate03의 한 assertion/문구 보정·Owner 수락은 이 task가 기록한다. README를 실행 증거로 쓰지 않는다 |
| N7 | accept / statically reconcile | 현재와 OLD workspace.py bytes는 같다. writer_guard→jsonio.exclusive_file_lock은 fd 기반 exact LOCK_EX/LOCK_UN을 사용하고 정상 새 lock은 빈 regular file이다. dir_fd는 쓰지 않는다. Nonempty lock·LOCK_NB·buffered/native I/O의 일반 관측은 보증하지 않고 P2 실제 경로의 관측 여부를 따로 확인한다 |
| N8 | accept | 기존 qualified root의 p1/p2 slots를 사용하고 source/root membership/selection을 각 단계에 고정한다. 새 제품에 base smoke PASS를 복사하지 않는다 |
| N9 | accept | child mutable output, process-group 밖 descendant 및 PID 재사용 한계를 유지한다 |

Owner가 지정한 no-blocker 조건이 충족돼 P1a에서 실행한 동일 controls11을 최종 고정했다. 정렬 canonical map SHA-256은 `7ccaa529b60de4869ab7398540f3d50b91db1e32fc7992b5c6bcad040f4aa55f`다. Source와 durable exact copy의 각 file hash/mode가 같다. Control/runtime/policy bytes는 바꾸지 않았다. Copy 소비자는 승인된 P1b/P2 실행·복구이며 해당 사용과 필요한 유일 bytes 보존이 끝날 때까지 유지한다.

중복 raw response/stderr/review 사본 정리는 자동 승인 심사에서 증거 손실 가능성을 이유로 차단됐다. 이 기록·동결 작업에서는 삭제를 완전히 제외하고 원본을 그대로 유지했다. 이는 제품 검증 실패나 추가 Reviewer 호출이 아니다.

P1b는 C1 reader/window mapping, proof caller 전달, launcher/adapter mapping, paired reader와 fresh/exact init·replay를 구현한다. M3 문서와 P3 정렬은 별도이며 중간 제품은 설치·배포하지 않는다. 구현된 P1b selection만 collect/focused로 확인한 뒤 P2로 넘어가며 controls 변경 필요 시 중단한다.


### P1b Candidate And Focused Pair — Prepared, Not Executed

고정 controls11을 유지하면서 C1의 product/work/intent/workspace/candidates/view/cli와 root `colvia`, 동일 bytes의 renamed adapter를 반영했다. P1b는 독립 old27/28/29 및 entry29 literal membership, window→launcher/adapter 매핑, init schema1과 switch1/2·detach1/2/3 paired readers, non-null launcher proof의 verified window 전달, entry-1 fresh init와 exact init recovery/replay를 맡는다. 기존 record schema와 `.hrn/`/HV2-/hv2ref는 유지한다. P2 전환·repair·detach writer와 collision diagnostic은 아직 구현/검증 완료가 아니다. 중간 source를 실제 프로젝트에 설치하지 않는다.

EntryFoundationTests 11개를 explicit factory에 추가했다. Git/non-Git init와 installed status, 첫 retired collision의 무쓰기 거부, colvia Git index/alias/descendant·ignore admission, 9개 exact init crash point의 recovery/replay, partial/completed init의 collision 보존, bootstrap 뒤 late collision의 정확한 prefix/lock anchor 보존, mapped snapshot·required refs·runtime double 경계, synthetic schema1/actual OLD schema2 reader 및 독립 auditor 양성·음성을 선택한다. Schema1은 실제 historical writer 실행이 아니라 literal synthetic 구성이라는 한계를 유지한다.

기존 checkout-window current candidate 두 assertion은 entry mapping/checkout refusal로 전환했고, general-work의 6개 직접 proof caller는 명시적 checkout-1 fixture window를 전달한다. Historical make_exact_suite 본문과 기존 control24·OLD1·P2 product13의 AST/상수 bytes는 유지했다. 기존 source-based default fixture의 나머지 entry 전환은 P2 안에서 이어간다. P1b pair는 새 foundation11 + current-window2 + direct proof3 = 16개 ID/16 occurrence로 준비했다. Default discovery776과 명시 factory49의 실제 일치는 collect 뒤 판정하며 아직 실행 결과가 아니다.

기존 qualified root의 `collect-p1`/`focused-p1` 미소비 slot을 사용한다. Source map102개와 추가 source/문서118개 보존을 고정하고 `hv2`→`colvia` root membership 변경을 반영한다. 300초 collect 후 실제 collection hash만 bind한 1,200초 focused, 최대1,500초의 한 쌍이다. 새 private pair dispatcher는 읽기 전용 source/OLD/controls 및 기존6개 controller 결과, exact environment/argv/parent receipt/collection·duplicate multiplicity/selected·executed·counts를 검사한다. Controls11이나 sandbox 정책을 수정하지 않는다. Base smoke는 controls 선행 자격이며 새 source 증거로 재사용하지 않는다.

실행 전 Claude call2/4가 P1b 코드·fixture·fixed pair를 정적으로 검토한다. Ordinary assertion failure만 기존 shared correction1쌍 조건에 따라 처분할 수 있으며 그 외 실패는 중단한다. 이번 prepared checkpoint에서 controller 소비는0/6이고 결과 claim은 없다.


### P1b/P2 Batch Stop — Claude Call 2 Timeout, No Result Acceptance

2026-10-10 05:38:50 UTC에 P1b 정적 검토가 600초 상한에 도달하여 중단됐다. 실제 startup model은 Claude Opus 5.5 (`claude-opus-5-5`), session `74d001a6-7f3a-41f8-a26d-e217c0b04c35`, CLI 2.1.296였다. claude.ai/firstParty/pro 경로가 일치했고 tools/MCP 빈 배열·tool use0이었다. Wrapper는 상한에 따라 process group을 종료했다. Reviewer process exit는 -9, 실제600.02초, timeout=true, stderr0, malformed stream0, 종료 후 group_absent=true였다. Wrapper의 outer exit0은 metadata 기록 완료만 뜻하며 Reviewer 완료나 PASS가 아니다.

Result event0·assistant text block0으로 최종 Reviewer 응답과 판정은 없다. Verbatim final response는 unavailable이며, 이를 no-blocker/approval 또는 지적 없음으로 해석하지 않는다. 515,474-byte 전송 패킷 SHA-256은 `45933da1a5c2b1dca0c41b3facfc02b50391aabef4f53a5631f2962ad2f1c71a`이다. 큰 입력이 timeout의 원인인지는 확인하지 못했다. 인증·과금 변경이나 도구 실행, source/input drift는 관측하지 않았다. Source119개, 삭제 예정 tracked2개의 부재, tracked diff와 보호 입력118개의 호출 전후 검사는 PASS였다.

Owner의 “명시한 correction 외의 실패는 자동 재시도하지 않는다”는 중단 조건을 적용했다. 일반 제품 assertion 실패가 아니므로 shared correction을 사용하거나 Reviewer를 다시 호출하지 않는다. P1b controller pair를 시작하지 않았고 P2 구현에도 착수하지 않았다. 이 문서는 완료 checkpoint나 결과 수락이 아니라 중단·복구 준비 기록이다.

| 항목 | 실제 상태 |
| --- | --- |
| P1a actual-result R1 / controls11 | Call1 완료·차단0, 동일 controls 최종 고정 |
| P1b 구현 | C1 reader/proof/init 후보 반영; 최종 독립 판정·동작 검증 미완료 |
| P1b 정적 검사 | Python compile, diff whitespace, GFM 강조 렌더링 PASS; runtime/test PASS를 뜻하지 않음 |
| P1b collect/focused | 16개 선택 준비, 실행0회 |
| P2 | 계약·코드 읽기만 수행, 구현/실행 미착수 |
| 이번 묶음 예산 | Reviewer2/4 소비(완료1·timeout1), controller0/6·0/4,500초, shared correction0/1 |
| 과거 실행량 | P1a controller6·helper12 및 앞선 P0/검토/실패 이력 그대로 유지 |
| 제외 범위 | P3/P4·normative 활성화·실제 적용·commit/push/PR/merge 미수행 |

필요한 미커밋 변경은 durable private bundle에 base revision+tracked binary diff+신규 colvia/adapter/test bytes로 보존했다. Patch의 현재 checkout에 대한 reverse-check는 PASS였고 신규 파일의 bytes/mode는 일치했다. 기존 C0/controls exact copies와 current task copy도 유지한다. Raw 검토 stream·metadata를 삭제하지 않았다. 소비자는 Owner 중단 판정, exact P1b 재검토와 후속 P2/P4이며 해당 복구 의존성이 해소될 때까지 보존한다. Source 작업트리와 기존 qualified execution root는 구체적 후속 재사용 대상이므로 유지한다. 다른 checkout의 이동·삭제 또는 새 root/slot으로 예산 초기화는 하지 않았다.

### Bounded Recovery Proposal — Approval Required

P1b 재검토 후보 패킷을 177,690 bytes로 준비했다. SHA-256은 `2324abd287182d75f546314d106a701ed7e61cfa3d89d20d05690bca93609f6c`다. 미선택 P2 본문과 이미 검증한 control 본문 반복을 제외하고 모든 tracked runtime/test diff, 핵심 reader/init 본문, 새 launcher/auditor, foundation11과 필요한 fixture/helper, 고정 pair를 포함한다. 생략한 변경 없는 본문과 이전 OLD/control 증거의 상속 한계를 명시한다. 이는 제안 패킷 작성이며 전송·검토 재시도가 아니다. Tests/controls/격리 조건을 줄이거나 고치지 않았다. 새 fixture의 Git 호출을 pinned Git 경로로 맞추는 실행 전 후보는 별도로 명시했으며 중단 뒤 source에 적용하지 않았다.

권장 재개는 이번 review timeout 뒤 축소 패킷으로 fresh no-tool Claude 검토1회를 명시적으로 재승인하고, 차단 지적의 범위 내 보정 후 P1b pair→P2 구현·남은 Claude1회·P2 pair를 이어가는 것이다. 기존 Reviewer 총4회 한도에서 다음은 call3이며 모델·인증 경로·각600초·controller6회/4,500초·shared correction1쌍·기존 deadline11:00:28 UTC를 그대로 유지한다. 남은 시간으로 고정 상한을 충족하지 못하면 실행하지 않는다. Timeout 등 비-assertion 실패가 다시 발생하면 또 중단하며 자동 재시도나 범위 확대를 하지 않는다. P1b/P2 최종 결과 수락은 두 단계가 실제 완료된 뒤 요청한다.


### Owner Resumption And Increased Review Limit — 2026-10-10

Owner는 “상한을 좀 늘려야 하는 것 아닌지? 괜히 두 번 작업하지 않게. 진행해”라고 요청했다. Driver는 중단된 P1b/P2 묶음 재개와 남은 Claude call3/4의 각각 최대30분(1,800초)으로 상한 증가를 해석·고지했다. 기존 전체6시간 마감 2026-10-10 11:00:28 UTC, 총검토4회, controller6회/4,500초, 일반 제품 assertion shared correction1쌍과 나머지 중단·제외 조건은 유지한다. 과거 call2 timeout을 지우거나 예산을 초기화하지 않는다.

먼저 fresh no-tool Claude call3로 P1b 후보와 fixed pair를 검토한다. 축소 패킷은 모든 변경 diff·관련 reader/init·foundation/helper·실행 pair를 담고, 승인된 DR-0004 원문을 추가해 계약 판정 입력을 제공한다. 생략한 변경 없는 코드와 상속 controls/OLD 증거의 한계를 명시한다. 제품 입력과 실행 controls는 중단 시점 그대로이며, 검토 후 Driver 처분에 따른 승인 범위 내 보정과 exact source-map 갱신을 수행한다. 최종 결과 수락은 구현·focused 검증 뒤 별도로 요청한다.


### Resumed P1b Review 3 And Driver Dispositions

Claude Opus 5.5 (`claude-opus-5-5`)가 call3을 330.09초에 정상 완료했다. Session `1b73ae85-d96e-47bb-82f5-d2132a637985`, CLI2.1.296, claude.ai/firstParty/pro 경로, fresh/no tools/MCP, tool use0, exit0, is_error=false, timeout=false였다. 종료 후 group 부재와 exact source119개·보호 입력의 전후 불변을 확인했다. 이번 상한은 Owner 재개에 따라1,800초이며 총검토3/4를 소비했다. 최종 응답은 아래에 원문으로 보존한다. 정적 검토이며 실행·import·해시 재계산 증거가 아니다.

#### Reviewer Response Verbatim

````markdown
# P1b 정적 검토 결과 (call 3/4)

**판정: 조건부 준비.** 제공된 바이트 범위에서 P1b 런타임 코드(reader, 증명 매핑, fresh init, 복구)를 막는 구체적 정확성 결함은 찾지 못했습니다. 다만 고정 16개 pair 실행 전에 아래 차단 2건을 닫아야 합니다. 도구 실행, 테스트, 해시 재계산은 하지 않았고, 모든 해시는 제시된 값의 문자열 대조입니다.

## 1. 차단 사항 (pair 실행 전 해소 필요)

**B1. 고정되지 않은 git 실행 파일 (실행 경계)**
- `test_fresh_git_and_non_git_init_installed_reader`와 `test_init_index_and_ignore_admission`이 `/usr/bin/git`을 직접 spawn합니다.
- dispatcher가 drift를 검사하는 대상은 `c['git']['path']`와 그 sha256뿐입니다. `/usr/bin/git`은 macOS shim이라 검증된 바이너리와 다른 경로를 타고, `test.sb`가 이를 허용하는지는 제공되지 않았습니다.
- pair는 1회용입니다(`start.json` 배타 생성, 재시도 없음). sandbox 거부가 나면 슬롯만 소모됩니다.
- Driver 후속안(`config[git][path]` 사용)을 수집 전에 적용하고 invocation/source map을 갱신하는 것이 맞습니다.
- 대안으로, P1a 통제 실행이 동일 sandbox에서 `/usr/bin/git`을 통과했다는 증거가 있으면 "차단"에서 "식별성 약점"으로 내릴 수 있습니다. 그 증거는 이번 입력에 없습니다.

**B2. diff 식별값 불일치 미해명**
- 제시된 "All tracked runtime and test changes" 원본 SHA256은 `de3f6ca8…`입니다.
- plan projection의 `tracked_diff_sha256`은 `4d7a50e0…`입니다.
- 표현 차이(범위나 인코딩)일 수 있으나 저는 판별할 수 없습니다. 제가 검토한 바이트가 plan이 묶은 바이트와 같은지 Driver가 실행 전에 명시해야 합니다. 다르면 이 검토는 해당 후보에 적용되지 않습니다.
- `dispatch.json`의 dispatcher/plan 해시는 제시값과 문자열상 일치합니다.

## 2. 비차단 우려

### 테스트 oracle
- **N1. index 승인 테스트가 거부 사유를 고정하지 않습니다.** `test_init_index_and_ignore_admission`의 네 경우 모두 `assertRaises(ContractError)`만 봅니다. "index에 항목이 있고 worktree 파일이 삭제된" 상태의 양성 대조가 없어서, `classify_target` 등 다른 경로의 거부로도 통과합니다. code와 메시지("tracked", "not owned", 가시성) 단언을 권고합니다. B1 때문에 본문을 고친다면 같이 넣을 수 있습니다.
- **N2. `assertIn(name, message)`가 'HV2' 경우에 공허할 수 있습니다.** `ContractError.message`가 코드 문자열(`HV2-WORKSPACE-PRODUCT`)을 포함하면 항상 참입니다. `repr([name])` 포함 여부로 단언하는 편이 낫습니다.
- **N3. schema1 변형 테스트는 "어떤 이유든 거부"만 확인합니다.** `ContractError` 또는 auditor `degraded/10`이면 통과합니다. 무변형 양성 대조(partial/14)가 있어 완전히 공허하지는 않습니다. 사유는 고정되지 않습니다.
- **N4. `.git` 내부까지 before/after 비교에 들어갑니다.** fixture `snapshot`은 `rglob('*')`입니다. `_visible_truth`나 `classify_target`이 index를 갱신하는 git 명령을 쓰면 거짓 실패가 납니다. fail-closed이지만 슬롯을 소모합니다. 해당 본문은 제공되지 않았습니다.

### 런타임 코드
- **N5. guard 아래 재관측에 alias/index 재검사가 없습니다.** `_entry_absence_admission`은 `fresh` 분기에서만 실행됩니다. guard 아래 재관측과 `recover=True` 경로는 정확한 이름 `colvia` 존재와 `_visible_truth(planned)`만 봅니다. 대소문자 구분 FS의 `COLVIA` 등 alias 지연 출현과 index-only 추적은 재검사되지 않습니다. 협조 writer 모델에서는 위험이 낮습니다.
- **N6. 비UTF-8 추적 경로에서 진단 코드가 불안정합니다.** `_entry_absence_admission`의 `decode("utf-8","strict")`가 `ContractError`가 아닌 `UnicodeDecodeError`를 냅니다. 쓰기 전 거부라는 점은 유지됩니다.
- **N7. window→launcher 매핑이 두 곳에 있습니다.** `product.WINDOW_LAUNCHERS`와 `work._verified_launcher_path`입니다. 둘의 동등성 단언이 없습니다.

### dispatcher (`run-pair.py`)
- **N8. 선택 집합의 완전성을 자체 단언하지 않습니다.** `c['selection']==plan['selection']`, 선택 ID 집합 일치, 16건, occurrence 1을 확인하지 않습니다. 고정된 `default_ids`/`factory_ids` 멤버십과 미검토 runner에 의존합니다. foundation 11개는 `factory_ids`에 모두 있음을 확인했습니다. default 5개는 projection에 `default_ids`가 없어 확인할 수 없습니다.
- **N9. 외곽 감시가 없습니다.** `child.wait()`에 timeout이 없어(의도된 설계) controller가 멈추면 dispatcher도 무기한 대기합니다. 운영자 상한이 필요합니다.
- **N10. 경계 시간에서 슬롯이 소모될 수 있습니다.** collect의 외곽 경과가 300초를 조금 넘으면 `elapsed+1200<=1500`에서 STOP합니다.

## 3. 정적으로 추적해 문제를 찾지 못한 부분

- **경로 리터럴.** SERIAL 29, UMBRELLA 28, LEGACY 27이 `OLD_PATHS` 및 그 파생과 순서까지 일치합니다. ENTRY 29는 UTF-8 바이트 정렬이고 테스트 기대식과 일치합니다.
- **fresh init.** 첫 preflight는 `bootstrap_root`와 `writer_guard`보다 앞에 있습니다. 은퇴 점유자 검사는 이름만 열거하고(NFC+casefold, 대상을 열지 않음) D2-A 순서와 맞습니다.
- **지연 충돌.** 함수 내부 import라 `patch.object(workspace,'bootstrap_root')`가 유효합니다. guard 아래 preflight의 마지막 단계에서 거부하므로 release, receipt, launcher, binding은 게시되지 않습니다. 테스트의 lock anchor 허용 범위와 일치합니다.
- **완료 replay와 복구 충돌.** `verify_workspace_product` 후 entry-1 확인, 그다음 충돌 거부 순서입니다. guard 밖 첫 preflight에서 멈추므로 before==after 기대가 성립합니다.
- **증명 매핑.** sha가 non-null이면 지원 window가 필수입니다(fail-closed). `colvia`만 제외/보호되고 재등장한 `hv2`는 프로젝트 내용으로 남습니다(C0-H-A 부합). `None`/`unknown`/`checkout-1` 거부 경로도 테스트 기대와 일치합니다.
- **switch reader.** schema와 window의 쌍 제약이 있고, receipt schema는 plan schema를 따르며 canonical 대조로 혼합쌍을 거부합니다. 첫 entry-1에서 checkout-1로의 rollback은 rank로 거부됩니다.
- **detach reader와 auditor.** schema 1/2는 `hv2`, schema 3은 `colvia`입니다. `payload/colvia`는 schema 3에서만 허용됩니다. schema-3 충돌 거부는 reader와 auditor가 대칭입니다. `any()` 필터로 KeyError를 피합니다.
- **`colvia` launcher.** binding ref가 `entry-1`과 정확히 일치해야 하므로 B0에서 bootstrap을 거부합니다.

## 4. P2 대기 의존성 (현재 P1b 실패 아님)

- **D1. `remove` 항목의 선행 release 대조.** schema-2의 `{path:"hv2",sha256,size}`를 선행 release의 `payload/hv2` 항목과 대조하는 코드가 reader에 없습니다(형태 검사만). 계약의 "verified against the predecessor release"는 P2 writer/preview나 reader에서 닫아야 합니다.
- **D2. 교차 window pending 관측.** `_workspace_product_once`는 활성 binding의 launcher(`hv2`) 존재를 요구하므로 S5(O 부재, B0)는 `allow_pending`으로도 읽지 못합니다. `permitted`에는 N 바이트가 `hv2` 경로 허용값으로 들어갑니다. S1–S5 전용 관측과 물리 prefix 표가 필요합니다.
- **D3. repair 경로.** 아직 `checkout-1` 요구가 남아 있어 새 소스의 repair는 전부 거부됩니다. 안전한 거부이며 entry-1 exact repair가 미구현입니다.
- **D4. switch/detach writer.** schema 2/3 생성, 배타적 N 생성, 0600 B1 staging, umask 거부가 없습니다.
- **D5. D1-A 진단.** status/doctor/view의 `conflict`/12와 `retired_entry_collision` 필드, CLI exit 65 매핑이 없습니다.
- **D6. 중간 후보의 노출면.** CLI가 `--profile entry-1`로 update/rollback/detach를 노출하지만 writer는 미완입니다. 이 후보는 fixture 밖에서 설치하거나 사용하면 안 됩니다.

## 5. 확인 불가 증거

- **U1. 변경되지 않은 코드 본문.** `classify_target`, `target_fingerprint`, `_visible_truth`, `bootstrap_root`, `inspect_root`, `_workspace_observe`, `_write_exact`, `_serial_inventory` 후반부, `_detach_receipt`, `_detach_observe_records` 전반부, `workspace_detached_status`, `view._product`, cli status 경로. 특히 `umbrella.py`·`cli.py` 등에 남은 `"hv2"` 리터럴이나, inventory id 없이 sha만 넘기는 `snapshot`/`_live_external_refs` 호출부가 있는지 확인할 수 없습니다(있으면 fail-closed 기능 회귀).
- **U2. 통제 파일.** `controller.py`, `runner.py`, `common.py`, `test.sb`, observer. `installed-new` entry의 의미, subTest 실패 집계, `p1` 슬롯 허용 여부, `c['collection_sha256']` 키 존재도 여기에 포함됩니다.
- **U3. helper의 실제 출처.** `EntryFoundationTests`는 `product`/`call`/`new_init`을 `EntryProductTests`에서 가져옵니다. 제시된 base helper 본문이 실제로 바인딩되는 본문이라고 가정했습니다.
- **U4. 후보 소스의 신규 파일.** `adapters/colvia-work/SKILL.md` 등 ENTRY 29개 경로의 존재와 바이트. 모든 init 테스트의 전제입니다.
- **U5. 고정 입력 원문.** plan의 `default_ids`, `source_all`, `prior_results`, invocation 본문.
- **U6. 선택되지 않은 테스트.** inventory id 없는 non-null launcher 증명을 쓰는 fixture double이 전체 스위트에서 깨질 가능성은 P1b 범위 밖입니다.

## 6. 준비도와 한계

- **코드(P1b 범위):** 정적 차단 결함 없음. N5–N7은 권고입니다.
- **고정 16개 pair 실행:** B1과 B2 해소가 조건입니다. N1과 N2는 B1 수정 때 함께 반영하길 권고합니다.
- **통과해도 뒷받침되지 않는 것:** 설치된 entry-1 writer 경로(`require_workspace_runtime`, candidates/intent gate), entry-1 worker 증명과 CRLF, schema-2 switch 이력 reader, schema-3 detach, CLI exit 매핑. 16개 중 어느 것도 이들을 실행하지 않습니다.
- **Driver 후속안 2번**(완료 init 재관측에 verifier inventory 필드 사용): 현재 본문도 `observed["inventory"]["inventory_id"]`를 쓰고 있어 결함으로 보지 않았습니다. 정확한 변경안은 제시되지 않아 평가하지 않았습니다.
- 이 검토는 Owner 수락, 범위 부여, 활성화 판단이 아닙니다.
````

#### Driver Dispositions

| ID | Disposition | 근거와 범위 내 조치 |
| --- | --- | --- |
| B1 | accept / corrected | foundation의 Git 호출4곳을 invocation에서 해시 고정한 config Git 경로로 맞췄다. 정책/controls는 바꾸지 않았다 |
| B2 | revise / resolved | de3f6ca8…은 `git diff HEAD -- src tests`의 원본 digest, 4d7a50e0…은 `git diff HEAD --binary` 전체 tracked digest다. 전체에는 root/adapter 삭제·index 문서가 추가된다. 두 명령을 동일 검토 입력에서 재계산해 일치했고119개 file map으로 동일 후보를 확인했다. 필터 차이며 unexplained drift가 아니다 |
| N1 | accept / corrected | tracked 원인과 Product code를 단정하고 ignore 원인 문구를 단정했다. 무관한 index-only 파일은 허용하는 preview 양성 대조를 같은 method에 추가했다 |
| N2 | revise / strengthen | ContractError.message는 코드 문자열을 포함하지 않아 기존 HV2 단정이 공허하지 않다. 그래도 실제 observed_names 배열 표현을 단정하도록 강화했다 |
| N3 | accept limitation | malformed schema1의 code별 원인 완전성은 미검증이다. unchanged 양성 및 정확한 bytes 보존 대조를 유지한다 |
| N4 | defend / retain strict comparison | git_environment는 GIT_OPTIONAL_LOCKS=0을 설정하고 observation은 읽기 명령이다. Git 전체 bytes 비교를 약화하지 않았다. 실제 filesystem 결과는 focused가 판정한다 |
| N5 | accept / corrected | exact incomplete-init prefix의 identity/state 검증 후 매 preflight에서 alias/index/visibility를 재검사한다. 기존 정확한 colvia prefix는 별도 receipt/bytes 검사로 계속 제한한다. 완료 후 정상 Git 추적을 새 fresh-init 거부로 바꾸지 않는다. 기존 late-init method에 alias/index 거부·무변경 사례를 추가했다 |
| N6 | accept / corrected | 비UTF-8 index path를 보존하며 HV2-WORKSPACE-PRODUCT로 명시 거부한다. 공통 Git/path 계약은 변경하지 않는다 |
| N7 | accept / corrected | foundation의 literal-window method에서 두 mapping의 동등성을 직접 단정한다 |
| N8 | accept / corrected | task-local dispatcher에서 invocation/plan selection 일치,16 IDs와 각1 occurrence를 강제한다. controls runner는 그대로다 |
| N9 | accept limitation | controller가 timeout/cleanup을 소유하며 Driver가 전체 상한과 진척을 관측한다. dispatcher는 controller를 조기 kill해 cleanup을 방해하지 않는다. hang/상한 문제는 중단 사유이며 새 실행을 자동 시작하지 않는다 |
| N10 | accept conservative stop | 기존300+1,200초 및 총1,500초를 늘리지 않는다. 남은 고정 예산이 부족하면 focused를 시작하지 않는다 |
| D1–D6 | accept pending P2 | retirement 대조, S1–S6 reader/physical prefix, repair, schema2/3 writer, conflict 진단을 P2에서 닫는다. 중간 candidate의 실제 설치/사용은 승인 범위가 아니다 |
| U1–U6 | accept bounded limits | 생략한 unchanged source/controls/OLD 본문은 이전 검토·Driver identity 확인에 의존한다. 이번 Reviewer가 전체 source/실행을 독립 검증했다고 주장하지 않는다 |
| 완료 init 후속 후보 | defend current code | 현재 source는 이미 observed.inventory.inventory_id를 쓴다. stale 제안 문구였으며 추가 source 보정은 필요하지 않다 |

보정은 product.py·entry test 두 source 파일과 task-local pair helper에 한정했다. 이전 control24·OLD1·P2 product13 및 공유 fixture/helper AST와 bytes는 그대로다. 새 focused method를 늘리지 않아 선택은16 IDs/16 occurrences이며 default776+factory49=825는 아직 수집 예상이다. Source102 map과 보존118 map·invocation/plan/helper digest를 새 바이트에 맞춰 갱신했다. Python 전체 source/tests 정적 compile, git diff --check, controls11 불변을 확인했다. 이는 실제 제품 테스트 PASS가 아니다. GFM 렌더링은 기록 저장 후 확인한다.

다음은 기존 qualified root의 미소비 collect-p1→focused-p1 한 쌍이다. Controller300/1,200초, 현재 source identity와 collection hash를 순서대로 결속한다. 이번 correction은 실행 전 정적 보정으로 shared assertion correction pair를 소비하지 않았다. 실행 실패는 원래 중단/한정 correction 조건으로 판정한다.


### P1b Actual Pair — 15 Pass, 1 Failure; Stopped Before P2

2026-10-10 실행은 pinned CPython3.14.7, 기존 test.sb sandbox와 고정 controls11, source102 digest `557328fbb35d23b5502c9e19d7efa2462ba5d3607ad9cd739f68e8c14bd6c7ef`를 사용했다. 정확한 controller argv·cwd·환경은 private pair plan 및 각 parent inputs에 보존했다. collect-p1은 exit0·0.458초, 실제825 occurrences(default776+factory49), collection SHA-256 `5e033d4bfa6e01b4d272af8a229d858b11106e41e9d6f8c6faba917c23ec89d1`였다. 이 digest를 focused invocation에만 결속했다.

focused-p1은 자연 종료 exit1·9.435초였고16개 모두 실행했다. Pass15, failure1, errors0, skips0, expected failures0, unexpected successes0, unstarted0, unfinished0이다. 양쪽 process group 부재와 input 불변을 확인했다. Dispatcher는 controller의 non-pass를 받아 outer exit2로 중단했고 pair-result PASS를 만들지 않았다. Controller 누적2/6회·9.893/4,500초, outer 경과9.956초다. 이전 P1a6회와 모든 과거 실패/검토 소비량은 그대로 유지한다.

실패 ID: `test_entry_window_transition.EntryFoundationTests.test_fresh_git_and_non_git_init_installed_reader`, occurrence1. Git fixture의 설치 자체는 완료했고 installed-new observer를 통한 status 기대값에서 실패했다. 루프의 첫 Git 사례에서 멈췄으므로 뒤 non-Git installed status는 이 method에서 미실행이다. 다른 fresh/non-Git init 검사는 각 실제 선택 결과 범위로만 보고한다. 핵심 출력은 다음과 같다.

```text
AssertionError: 0 != 65
{"classification":"fail","code":"HV2-WORKSPACE-TARGET","message":"target classification unavailable"}
Ran 16 tests
FAILED (failures=1)
```

Runner가 실패 fixture612,036 bytes를 기존 qualified root의 실패 보존 경로로 복사했고 preservation-stop은 없었다. 이벤트36개·stdout·stdin·Git fixture·정확한 설치 payload·collection/선택/실행/counts·parent inputs/result를 보존했다. Source의 현재 binary diff+신규 launcher/adapter/test bytes를 private bundle의 별도 실패 후보로 보존하고 reverse-apply check 및 bytes/mode readback을 확인했다. 중단 이전 후보와 원문 검토 이력도 지우지 않았다. 소비자는 Owner 실패 처분 및 exact observer 호환성 조사이며 이 복구 의존성이 끝날 때까지 필요한 입력·fixture를 유지한다. Source와 기존 실행 checkout은 근접 재사용 대상이므로 유지한다.

#### Failure Classification And Static Diagnosis

제품 assertion 예외로 자동 보정하기 전에 원인 분류가 필요하다. 정적 경로는 installed status → classify_target → subprocess.run(capture_output=True) → CPython subprocess.Popen의 io.open(pipe fd) → observer audit(open) → path_of(int) → fcntl(F_GETPATH)다. 고정 observer는 모든 int fd에 F_GETPATH를 호출하고 pipe/non-path fd를 분리하거나 해당 조회 실패를 처리하지 않는다. 외곽 classify_target은 OSError를 위 HV2-WORKSPACE-TARGET으로 바꾼다. 실제 event trace는 product/workspace/work 모듈 로딩 뒤 끝났고 검증된 Git 설치/API 경로의 앞선 호출들은 통과했다.

이는 observer의 비파일 fd 호환성 문제를 지목하는 **정적 유력 가설**이다. 정확한 예외 chain을 별도로 포착하거나 pipe counterexample을 실행한 것은 아니므로 “재현된 원인”이라고 쓰지 않는다. 현재 증거만으로 일반 제품 assertion 실패라고 확정하거나 shared correction 예외를 적용하지 않는다. controls 변경이 필요한 경우 명시적 중단 조건에 해당하므로 P2 구현, 제품 재실행과 추가 Claude 호출을 멈췄다. controls/policy/격리 기준은 그대로이며 shared correction0/1이다. Reviewer 총3/4(완료2·timeout1), 마지막 남은 검토 상한1,800초와 원래 전체 마감11:00:28 UTC를 보존한다.

#### Concrete Diagnostic Proposal — Not Executed

고정 observer 원문의 path_of 함수 AST만 그대로 추출해 pipe read/write fd와 regular file/directory fd4개를 비교하는1회 진단 스크립트를 준비했다(1,642 bytes, SHA-256 `0e6c80f887517c6672f21f177d17827108e704ce2d256a8be787986375f94424`). 원본 observer hash를 먼저 검사하고 AST를 변경하지 않는다. 결과에는 파일 종류, 반환 path 또는 예외 type/errno와 해당 AST digest를 남긴다. Product import·Git 실행·source/controls 수정·기존 실패 fixture 변경·기존 테스트 재실행은 포함하지 않는다.

제안 경계는 기존 qualified root 아래 새 diagnostic WORK 하나, 기존 test.sb 그대로, pinned Python -I -S -B와 지정 argv/환경, 최대1회·300초(종료/정리 포함)다. 파일 생성은 그 WORK의 regular test file과 parent output으로 한정하고 network/credential 접근은 허용하지 않는다. 이것은 새 qualification root나 controller/shared-correction 예산 초기화가 아니라 별도 명시 승인될 원인 확인1회다. 아직 실행하지 않았다.

이 진단이 control 결함을 확인하면 non-filesystem fd만 관측 대상에서 제외하되 실제 파일·디렉터리의 조회 오류/identity/fault 요구는 유지하는 최소 보정을 검토한다. 실제 control 변경, 독립 delta review, 필요한 재자격 검증과 P1b 재실행은 정확한 영향/추가 실행량을 산정해 별도 승인된 복구 범위로 묶어야 한다. 이 문서는 그 실행을 승인하지 않는다. 진단이 가설을 지지하지 않으면 관측 결과를 보존하고 다른 원인을 보고한다. P1b/P2 결과 수락·Done·P3/P4·활성화·실제 적용·Git publication은 모두 미수행이다.


### Pipe FD Diagnostic — Reproduced Observer Defect; No Product Rerun

Owner의 후속 `진행해`는 직전 제안의 최대1회·300초 진단을 승인한 것으로 적용했다. 2026-10-10 06:07:12 UTC에 기존 test.sb와 pinned CPython3.14.7 `-I -S -B -c <exact diagnose.py>`로 실행했다. argv의 나머지는 검증 control directory, observer SHA-256, 신규 diagnostic WORK다. cwd와 HOME/TMPDIR/XDG_CONFIG_HOME은 그 WORK 안이며 나머지 환경은 기존 pair의 명시 allowlist다. 정확한 argv·환경·cwd·정책 hash는 private execution receipt에 있다. 제품 import, Git 실행, 제품 테스트 재실행, source/controls 변경은 하지 않았다.

자연 종료 exit0, child 경과0.038449초, timeout 없음, process group 부재였다. 진단 script SHA-256은 `0e6c80f887517c6672f21f177d17827108e704ce2d256a8be787986375f94424`, observer SHA-256은 `c7928dba5358a702896461d5edec08baad8ec7d711e96151aa24d55861a5225c`다. 원문에서 수정 없이 추출한 함수 AST digest는 `7258771fea53da90d1e1a00a082770dc2b4594400e6f0c37030779a7f0b0cc31`, stdout digest는 `023bda76f5f08cf7ac916f7d42c4ffd93db97ac7cc4edc8d4674e40175a18507`다.

| 입력 fd | 실제 관측 |
| --- | --- |
| pipe read | fstat kind4096 확인 후 path_of에서 OSError, errno9, `[Errno 9] Bad file descriptor` |
| pipe write | fstat kind4096 확인 후 path_of에서 같은 OSError·errno9 |
| regular file | kind32768, path `regular` |
| directory | kind16384, path `.` |

유효한 pipe fd에 대한 기존 F_GETPATH 호출 실패는 실제 재현됐다. 일반 파일·디렉터리 대조는 정상이다. 앞선 정적 경로와 함께 observer의 pipe 처리 결함을 지지한다. 다만 이번 실행은 추출한 path_of의 반례이며, 원래 installed status 전체 예외 chain을 다시 실행해 포착한 결과는 아니다. P1b 결과는 여전히15 pass·1 failure이고 제품 PASS로 승격하지 않는다. P2는 미착수다.

실행 전후 source 보존 map의 bytes/mode, controls11, 기존 실패 evidence map과 task record hash가 동일했다. 원래 실패 fixture/후보 보존본과 과거 검토·실행 기록은 유지한다. 이번 diagnostic receipt와 작은 stdout은 실패 처분 및 보정 대조를 위한 소비자에게 필요하므로 private bundle에 보존한다. 이전 qualification 및 구현 checkout은 해당 후속 작업의 근접 재사용 대상으로 유지한다. 재현 가능한 regular diagnostic 파일 자체는 별도 영구 납품물이 아니다.

#### Bounded Recovery Preparation Proposal — Not Applied

검토 가능한 최소 patch 후보를 private bundle에 준비했다. observer.path_of에서 int fd를 os.fstat으로 확인해 FIFO인 경우만 None을 반환하는2행 추가다. 기존 stat import를 사용하고 일반 파일·디렉터리의 F_GETPATH 오류 및 유효하지 않은 fd의 fstat 오류는 계속 전파한다. 이 후보는 anonymous pipe뿐 아니라 named FIFO fd에도 적용되므로, fault 대상의 regular file/directory 계약 및 미관측 fault 실패 판정을 약화하지 않는지 독립 검토와 반례가 필요하다. socket·기타 특수 fd 처리까지 확장하지 않는다. 실제 observer나 다른 controls에는 적용하지 않았다.

재개는 이2행 적용 후 기존 pair를 바로 반복하는 것으로 끝나지 않는다. controller.completed는 acquire/canary/smoke의 controls map 완전 일치를 요구한다. observer hash가 달라지면 기존 qualification을 그대로 재사용할 수 없다. 기존 슬롯을 덮어쓰거나 identity check를 완화하면 안 된다. 또한 현재 source는 root colvia로 전환됐지만 controller.positive_boundary_controls와 canary의 SOURCE 대조는 hv2를 고정하고 있어 재자격 실행 설계에서 이 차이를 명시적으로 해결해야 한다.

다음 승인 대상은 **통제 보정과 재검증 준비** 한 묶음이다. 허용 후보는 observer의 fd 분류, 그 회귀 검증, 필요한 재자격 입력/출처와 고정 실행계획이다. 완료 기준은 파이프·regular·directory·닫힌 fd·실제 file path 조회 실패·미관측 fault를 구분한 기대값, 변경 control 목록과 digest, 기존 qualification 보존 방식, exact commands/slots/시간·호출 예산, 독립 delta review 입력을 검토 가능하게 제시하는 것이다. 제품 코드/P2를 수정하거나 CLI Reviewer·canary·제품 테스트를 실행하는 승인은 여기에 포함하지 않는다. authoring만 하며 범위 밖 계약 변경이 필요하면 멈춘다. 실행 승인은 이 고정 계획이 준비된 뒤 최종 단계에서 받는다.

이번 별도 진단은1/1회 소비했다. 원래 batch의 Reviewer3/4, controller2/6·9.893/4,500초, shared ordinary-assertion correction0/1 및 마감11:00:28 UTC는 초기화하지 않는다. 통제 보정과 재자격 실행을 기존 ordinary-assertion correction으로 취급하지 않는다. 실제 통제 수정·추가 검토·재실행·Owner 결과 수락·Done·P3/P4·활성화·Git publication은 미수행이다.


### Owner-Approved Control Correction And Recovery Preparation — Execution Pending

Owner의 `승인`은 직전 제안인 통제 보정과 정확한 재검증 실행계획 작성을 승인했다. 이 범위에서 observer.path_of에2행을 추가했다. int fd의 os.fstat 결과가 FIFO이면 경로 관측 대상에서 제외한다. 일반 파일·디렉터리의 F_GETPATH 처리와 오류 전파, closed fd의 오류, fault 미관측 실패 계약은 유지한다. named FIFO fd도 제외되며 이 범위가 fault 보장을 약화하는지는 다음 독립 delta review의 명시 검토 대상이다. Product 코드와 기존825개 수집 후보는 변경하지 않았다. 기존11개 통제 중 observer.py1개만 변경했으며 정책·controller·runner·canary·seed 목록은 그대로다.

기존 observer SHA-256은 `c7928dba5358a702896461d5edec08baad8ec7d711e96151aa24d55861a5225c`, 보정 후보는 `fe89e2eb4a2ddecb6231b606962e876c9ce22e1b2700f3a362cf98c266e1ef8d`다. 기존 freeze는 그 당시 실행의 역사적 입력으로 보존한다. 새 후보를 기존 qualification에 끼워 넣거나 옛 입력을 갱신하지 않았다.

#### Qualification Path And Provenance

기존 controller의 controls 완전 일치 검사를 유지하므로 fresh qualification이 필요하다. 등록된 worktree와 목적지 부재를 확인하고, 지정 agent-worktrees 루트에 **검증용 기준 소스 복사본** 하나를 준비했다. 새 Git worktree가 아니며 `.git`·runtime authority는 없다. BASE revision `238514686078ce1564010a7b69013f48a635c57c`의101개 파일을 기존 OLD 및 baseline manifest의 bytes/size와 대조한 뒤 원래 Git mode로 복사하고 새 controls11개만 추가했다. 총112개 파일의 목록·bytes·mode를 고정했다. 원래 Product 기준 소스는 바꾸지 않았고 런타임 검증을 실행하지 않았다.

이 복사본의 소비자는 기준 소스에서 fresh acquire/canary/base collection/기존20 smoke를 수행하는 절차와 그 delta review다. 재현 가능한 실행 입력이며 제품 납품물이나 새 진척 원장이 아니다. 복구 처분과 후속 검증·리뷰 의존성이 끝나면 기존 보존·정리 규칙으로 정리한다. 구·신 observer 원문2개는 이번 정확한 before/after fd 대조의 입력으로 필요하다. 원래 실패 fixture와 검토 기록은 별도로 보존한다.

```text
기준 revision + 새 controls ── acquire → canary → collect → smoke20
                                                 │ 같은 controls/runtime/Git
현재 P1b 후보 + 새 controls ── collect → controls25 → P1b16 → 결과 보고
```

기준 소스의 hv2를 사용하므로 SOURCE boundary probe를 colvia로 바꾸거나 canary 검사를 약화할 필요가 없다. 새 execution root의 acquire/canary/smoke를 동일 controls/runtime/Git/config로 새로 만들고, 현재 후보의 entry 실행으로 전환한다. controller.completed가 source equality를 요구하지 않는 bootstrap 경계는 기존 동작 그대로이며 각 단계의 실제 source path/digest는 별도로 기록한다. smoke20은 **기준 revision의 결과**이고 현재 entry 제품의20개 검증으로 보고하지 않는다. 현재 후보의 통제25개와 P1b16개는 현재 source digest에 묶는다.

#### Fixed Prospective Execution

아래는 작성된 실행안이며 아직 승인·실행하지 않았다. pinned CPython3.14.7 `-I -S -B`, 기존 명시 환경, acquire.sb/test.sb를 유지한다. parent helper는 정확한 source/control map·기존 증거·명령·환경·선택/실행 occurrence·종료/그룹 부재를 확인하며 임의 명령이나 retry 입력을 받지 않는다. 정확한 argv·절대 경로·input template·digest는 private execution-plan/dispatch 및 고정 helper에 있다. 실제 collection hash만 전용 bound input에 배타적으로 넣으며 다른 template 필드는 바꾸지 않는다.

| 순서 | 범위·명령 | 실행 상한 | 성공 뒤 진행 조건 |
| --- | --- | --- | --- |
| 0 | fresh Claude `opus`, medium, tools/MCP 없음, 정적 delta review1회 | 종료·정리 포함1,800초 | 실제 model/session·인증 경로·입력 불변 확인, 원문 기록과 Driver disposition, blocker 없음 |
| 1 | 기존 격리 경계의 새 WORK에서 old/new fd regression1회 | 300초 | pipe read/write, regular/directory, closed fd, named FIFO와 synthetic F_GETPATH 오류 전파, extracted path_of + audit + subprocess 양성/음성 비교 |
| 2 | 기준 소스 `controller.py … acquire base` | 300초 | 정확한 OLD 재구성·입력 보존 |
| 3 | 기준 소스 `controller.py … canary base` | 300초 | 기존 격리·primitive·lock·Git/runtime 대조 |
| 4 | 기준 소스 `controller.py … collect base` | 300초 | 원문 collection/occurrence 보존, 기존 seed20 모두 각1회 존재, loader 오류 없음 |
| 5 | 기준 소스 `controller.py … smoke base` | 1,200초 | 동일 collection, 기존20개 모두 pass |
| 6 | 현재 후보 `controller.py … collect p1-controls` | 300초 | default776+factory49의 정확한 목록825 occurrences, control25 각1회 존재 |
| 7 | 현재 후보 `controller.py … focused p1-controls` | 1,200초 | 기존control24+OLD1 모두 pass; 미관측 fault 실패 검사 포함 |
| 8 | 현재 후보 `controller.py … focused p1` | 1,200초 | 같은 collection hash, 기존P1b16개 각1회 모두 pass |

entry collection은 선택과 무관한 동일 source/controls의 수집값이므로 control25와 P1b16에 한 번만 결속한다. 같은 identity의 불필요한 collect 재실행은 하지 않는다. 별도 focused input의 selection만 각각 미리 고정했다. P1b 원래 실패 ID의 Git/non-Git installed status를 다시 관측하되 실패를 새 성공으로 덮어쓰지 않고 양쪽 결과를 함께 기록한다. fd regression은 전체 observer 실행이 아닌 추출 함수 및 audit/subprocess 대조이고 F_GETPATH 오류 주입은 합성이다. full observer의 fault·lock 보장은 기존25개 대조 범위로 확인한다.

#### Budget Amendment And Stop Rule — Proposed Only

현재 소비는 이 batch Reviewer3/4, controller2/6·9.893/4,500초, 원인 진단1회다. 이 복구안은 남은 Reviewer1회를 P2 대신 통제 delta review에 사용하고 controller7회를 추가한다. 따라서 **controller 누적 상한9회·5,100초** 승인이 필요하다(새 고정 상한 합계4,800초 + 이미 소비한9.893초; 5,100초는 누적 한도다). fd 회귀 진단은 원인 진단과 구분한 추가1회·300초다. 이전 P1a6회와 오래된 실패/검토 소비 이력은 삭제하거나 초기화하지 않는다. shared ordinary-assertion correction은0/1 그대로이며 이번 복구에서는 사용할 수 없다.

원래 전체 마감은2026-10-10 11:00:28 UTC(20:00:28 KST) 그대로다. 검토 시작 전7,500초 이상, 검토 후 실행 시작 전5,700초 이상이 남아야 시작한다. 단계별 고정 상한과 원래 마감 모두 지킨다. controller는 child cleanup을 소유하며 parent는 해당 상한+30초까지만 기다린다. 이를 넘기면 controller PID와 cleanup 미확인 상태를 남기고 다음 단계를 시작하지 않는다. 보존 중인 controller를 조기 kill해서 성공을 꾸미지 않으며 Driver가 해당 process와 fixture를 확인해야 한다. 이것은 timeout을 PASS로 바꾸는 예외가 아니다.

검토 blocker, 인증/과금 경로 불일치, 입력 drift, 격리·계약·정책 변경 필요, collection/import/config 오류, 테스트 non-pass/skip/unfinished, 보존 문제, timeout·남은 process·예산 부족이면 즉시 다음 실행을 중단한다. 자동 retry, 슬롯 덮어쓰기, source 교체, identity 검사 완화, 범위 밖 보정은 없다. 검토의 조건부 권고를 변경 없이 충족할 수 없다면 Driver가 처분과 새 보정안을 기록하고 재승인 경계를 판단한다.

현재 확인한 것은 source102 불변, control1개·2행 차이, 기준 소스101+controls11의 입력 대조,20/25/16 선택 개수, helper/observer 및 생성 child 코드의 정적 compile, input/dispatch hash 정합이다. Product tests·fd 회귀·canary·Reviewer는 실행하지 않았다. GFM 렌더와 git diff --check는 기록 저장 후 확인한다. 기존 P1b15 pass·1 failure 및 P2 미착수 상태는 그대로다. 새 runtime execution root는 아직 만들지 않았다. 구현 checkout·기존 실행 경계·기준 복사본은 위 근접 소비자 때문에 유지한다.

이 계획의 실행 승인은 위 추가 횟수·누적 예산·정확한 입력과 순서를 포함해야 한다. 승인 뒤에도 P1b 재검증 결과 보고에서 멈추며 P2 구현, 전체 제품 자격 검증, Owner 결과 수락/Done, 활성화, 실제 adopter 적용과 Git publication은 포함하지 않는다.


### Owner-Authorized Recovery Execution — Independent Review Completed

Owner는 제안된 예산 변경을 포함해 검토·재검증을 실행하고 P1b 결과 보고까지 진행하도록 승인했다. 실패 시 재시도하지 않고 P2에 착수하지 않는 조건이다. 첫 Claude 실행 요청은 자동 승인 검토가 구체적인 비공개 패킷 외부 전송에 대한 명시적 승인이 필요하다고 판단해 process 생성 전에 차단했다. 이때 입력은 그대로였고 Claude·fd·controller 실행은0회였다. Owner는 이어서 정확한 패킷의 Claude 서비스 전송과 기존 범위 재개를 명시적으로 승인했다. 이 승인 후에만 아래1회를 실행했다. 차단을 우회하거나 미승인 재시도하지 않았다.

검토 입력은256,323 bytes, SHA-256 `e78c4b236731bba13b818ad426146f9402eee4ec9078baa5d2d2d3defd8c3fd4`다. 기준 revision은238514686078ce1564010a7b69013f48a635c57c이며 uncommitted observer2행 delta와 기존 Product102 map 불변을 구분했다. diff 밖의 helpers·templates·통제 원문·factory test·부분 task record와 생략한 전체 map/목록은 패킷에 명시했다.

CLI2.1.296, 로그인 claude.ai / firstParty / pro 확인 후 fresh static session을 사용했다. API/provider override는 없었고 계정 이메일·token은 기록하지 않았다. 실제 모델 `claude-opus-5-5`, session `ffc05282-5cdf-461c-98aa-9974545e853d`, 경과267.072초, exit0, is_error=false, timeout 없음, group 부재, 입력 불변 PASS였다. tools/MCP0·tool use0이며 Reviewer가 테스트를 실행하거나 해시를 재계산한 것은 아니다. Driver와 별도 모델·fresh context지만 동일 계정/host의 패킷 기반 정적 검토라는 한계가 있다. 이 batch의 Reviewer4/4를 소비했다.

#### Reviewer Response — Verbatim

````markdown
# 독립 정적 검토 결과: observer 보정 및 복구 실행안

**판정: 제공된 바이트의 정적 범위에서 차단 사항(blocker)은 찾지 못했습니다.** 다만 아래 준비 조건을 Driver가 처분에 기록해야 하며, 복구 전체를 소진시킬 수 있는 미검증 위험이 하나 있습니다(N2). 이 판정은 Owner 수락이나 실행 승인이 아닙니다. 실행과 해시 재계산은 하지 않았습니다.

## 1. Blocker
없음.

## 2. FIFO 처리 평가 (observer `path_of` 2행)

- **일반 파일·디렉터리**: `os.fstat`는 패치 대상이 아니고 부작용이 없습니다. 이후 `F_GETPATH` 경로는 그대로이므로 기존 관측과 오류 전파가 유지됩니다.
- **무효 fd**: `os.fstat`가 먼저 `OSError(EBADF)`를 냅니다. 구판의 `fcntl` EBADF와 같은 오류 계열이고, 조용히 무시되지 않습니다.
- **익명 pipe**: `None`을 반환해 `emit`과 audit이 건너뜁니다. `observed_write`의 `path_of(fd) == fault["path"]` 비교도 False라서 short-write가 잘못 적용되지 않습니다.
- **미관측 fault**: 정상 종료와 exit 0 경로의 `require(fault is None …)`는 변하지 않았으므로, FIFO로 가려진 fault는 성공이 되지 않습니다. 비영 `SystemExit`에서는 observer가 미관측을 따로 보고하지 않지만, 이는 기존 동작이고 테스트 쪽 `-SIGKILL` 기대가 잡습니다.
- **named FIFO는 재현된 반례보다 넓게 제외됩니다.** 구판은 vnode가 있는 named FIFO에 대해 경로를 반환했을 가능성이 있습니다. 이 경우 target 내부 named FIFO의 fd 기반 이벤트(write/fsync/fchmod/flock, audit open(int))가 새로 누락됩니다. 경로 기반 open/unlink/rename 이벤트는 유지됩니다.
  - 고정 25/16 범위에서는 영향 근거를 찾지 못했습니다. fixture `snapshot`과 runner 보존 로직이 특수 파일을 거부하고, 통제 시나리오는 일반 파일만 씁니다.
  - "EBADF이면서 FIFO일 때만 제외"하는 더 좁은 보정이 가능하지만, 이는 observer 해시를 바꾸므로 이번 범위 밖의 후속 과제입니다.
- **socket, kqueue 등 다른 fd 종류**: 여전히 예외로 실패합니다(fail-closed). 관측 누락은 아니지만, 같은 유형의 실패가 재발할 수 있습니다.

## 3. fd 회귀 검증의 타당성

- 기대값은 코드와 정합합니다.
  - pipe: 구판 EBADF, 신판 `None`.
  - regular는 `regular`, directory는 `.`.
  - 합성 `OSError(EPERM)`은 `PermissionError`로 전파됩니다.
  - closed fd는 양쪽 모두 EBADF입니다.
- audit/subprocess 프로브도 유효합니다. `capture_output`의 `io.open(int fd)`가 `open` audit을 내고, 구판은 child 생성 전 `Popen.__init__`에서 EBADF로 빠지며, 신판은 FIFO 2건 이상을 본 뒤 정상 완료합니다.
- 한계는 세 가지입니다.
  - 실제 `emit`/`active` 경로가 아니라 추출 함수 검증입니다.
  - Product가 이 OSError를 `65 HV2-WORKSPACE-TARGET`으로 바꾼다는 인과는 여전히 추론이며, 실제 확인은 P1b16 재관측에 달려 있습니다.
  - "fault를 FIFO 경로에 지정하면 실패한다"는 종단 음성 통제는 25개에도 없습니다. 위 2절의 코드 판독에만 근거합니다.

## 4. 기준 소스 → 현재 후보 qualification의 건전성

- `controller.completed`는 controls 해시맵, runtime, Git, system config의 동일성만 요구합니다. 두 template의 해당 값이 같으므로 prerequisite는 통과합니다.
- `run-recovery.py`의 `want` 비교는 controller가 기록하는 inputs 14개 키, 명령 순서, 환경, PATH 합성과 일치합니다.
- collection 결속, occurrence, 20/25/16 선택, 실패 증거 부재 검사는 runner 출력 형식과 맞습니다.
- canary가 `SOURCE/hv2`를 쓰므로 기준 소스에서 실행하는 것이 맞고, canary를 약화할 필요가 없습니다.
- 한계 두 가지는 보고에 명시해야 합니다.
  - 쓰기 거부 probe는 기준 복사본의 SOURCE/CONTROLS 경로에서만 관측됩니다. 현재 후보 경로의 격리는 동일 정책 바이트, default-deny 구조, 사후 바이트 대조에 의존합니다.
  - smoke20은 observer를 쓰지 않으므로 이번 delta의 증거가 아닙니다. controller prerequisite를 충족하는 기준 revision 결과일 뿐입니다. 결과 문구(`limits`, 최종 print)는 이를 올바르게 구분합니다.

## 5. Nonblocker와 위험

- **N1. dispatch.json이 묶여 있지 않습니다.** 게이트는 `plan_sha256`과 `review_sha256`만 확인합니다. `fd-regression.py`와 template의 무결성은 같은 디렉터리의 `dispatch.json`에 의존하는데, 그 해시는 코드로 강제되지 않습니다. template의 `source_digest`와 plan snapshot의 대조도 없습니다.
- **N2. `os.mkfifo`가 `test.sb`에서 허용되는지 관측된 적이 없습니다.** 이전 진단은 pipe/regular/directory만 다뤘습니다. 거부되면 `start.json`이 이미 기록된 뒤라서, 재시도 없이 복구 전체가 1단계에서 소진됩니다. fail-closed이지만 Owner가 알고 수용해야 할 위험입니다.
- **N3. 처분 시간 여유가 0입니다.** 7,500초는 1,800초와 5,700초의 합입니다. 검토가 상한을 다 쓰면 Driver 처분과 실행 승인에 쓸 시간이 없습니다. 이 경우 5,700초 게이트에서 안전하게 정지합니다.
- **N4. fd 회귀가 보존 대상인 b01 경계에 씁니다.** 출력 위치가 `exec/diagnostics/recovery-fd-01`입니다. 기존 증거 해시는 유지되지만 보존 디렉터리의 구성이 늘어납니다.
- **N5. supervision 만료 시 경과 시간이 남지 않습니다.** `supervision-stop.json`에 시간이 없고 `step-N-finish`도 기록되지 않습니다. controller는 새 세션이 아니라 parent 프로세스 그룹에 남습니다.
- **N6. base collection의 ID 목록은 고정되지 않습니다.** 비어 있지 않은지와 seed 20개가 각 1회인지만 확인합니다.
- **N7. `review-authorization.json`은 이름과 달리 승인이 아닙니다.** 리뷰 슬롯 소비 기록입니다. 복구 스크립트에는 Owner 실행 승인이나 예산 수정안을 기계적으로 확인하는 절차가 없고, 인간 게이트에 의존합니다.
- **N8. 환경 완전 일치 검사는 취약하지만 안전합니다.** `raw(sys.executable)`과 환경 일치 검사는 `start.json` 이전에 실패하므로 슬롯을 소비하지 않습니다. 고정된 전체 경로와 정확한 환경으로 기동해야 합니다.

## 6. 예산 회계

- 수치는 정합합니다. controller는 2+7=9회, 9.893+4,800=4,809.893초로 5,100초 이하입니다. Reviewer는 4/4, fd는 진단 1회와 회귀 1회입니다.
- 실행 전제 시간도 맞습니다. 300+4,800+7×30=5,310초로 5,700초 미만입니다.
- 기존 상한(6회/4,500초)을 넘으므로 Owner의 명시적 수정 승인이 필요합니다.
- P1a 6회 이력과 assertion correction 0/1은 초기화되지 않습니다.

## 7. 준비 조건

1. Driver 처분에 `dispatch.json`, `run-recovery.py`, `fd-regression.py`의 해시를 함께 기록하고, 기동 직전에 재확인합니다(N1).
2. N2 위험과 named FIFO 범위 확대를 Owner 실행 승인 요청에 명시합니다.
3. fd 회귀의 구판 named FIFO 관측값을 결과 보고에 그대로 기록합니다. 구판이 경로를 반환했다면 이를 관측 범위 축소로 보고합니다.
4. 기준 복사본의 `source_digest`가 원래 base qualification의 값과 같은지 처분에 기록합니다. 다르면 그 사유를 적습니다.
5. 결과 보고에서 다음을 구분합니다.
   - smoke20은 기준 revision의 결과입니다.
   - 경계 probe는 기준 경로에서 관측된 것입니다.
   - P1b 원 실패와 재관측 결과를 병기합니다.
   - non-Git subcase는 이번이 첫 관측입니다.
6. 실제 반환된 모델과 세션의 정체는 Driver가 `review-meta.json`에서 확인합니다. 스크립트는 모델을 assert하지 않습니다.

## 8. 검토 한계

- 도구, 실행, 해시 재계산 없이 패킷 텍스트만 검토했습니다.
- 다음 파일은 원문을 보지 못했습니다: `dispatch.json`, `review-identity.json`, `execution-plan.json` 전체, `baseline-inputs.json`, `prefix-oracle.json`, 825 ID 목록, 소스 맵, Product 구현, 기준 소스 파일.
- macOS sandbox의 실제 동작(mkfifo, F_GETPATH)과 CPython 3.14.7의 subprocess 세부는 일반 지식에 근거한 판단입니다.
- 호출 환경이 작업 디렉터리와 계정 컨텍스트를 자동으로 주입했으나 검토에 쓰지 않았습니다.
- P2, 전체 qualification, Owner 수락, 활성화는 범위 밖입니다.
````

#### Driver Disposition And Readiness

| ID | Disposition | 근거·조치 |
| --- | --- | --- |
| Blocker 없음 | accept bounded verdict | 정적 통제 delta/실행안의 판정만 채택한다. 실제 통과와 Owner 수락으로 바꾸지 않는다 |
| FIFO 범위 | accept limitation | named FIFO fd 이벤트도 제외됨을 기존 준비 기록에서 공개했고 Owner는 그 고정 보정·회귀 실행안을 승인했다. raw named FIFO old/new 값을 결과에 남긴다. 더 좁은 보정으로 바꾸지 않는다 |
| N1 / 준비1 | accept external binding check | dispatch·runner·fd helper hash를 아래에 기록하고 기동 직전 직접 재확인한다. 각 template.source_files가 해당 plan snapshot과 동일하고 source_digest가 그 canonical map digest임을 확인했다. machine gate만으로 Owner 승인을 증명한다고 보지 않는다 |
| N2 / 준비2 | accept bounded runtime risk | mkfifo의 실제 sandbox 허용은 아직 미관측이다. Owner가 승인한 고정 fd 회귀에 포함된 작업이며, 이 불확실성을 진행 안내로 명시했다. 정책/기대값/횟수를 바꾸지 않고 실제 거부 시 원래 no-retry 조건으로 중단한다. Reviewer의 권고 자체를 추가 승인 의무로 바꾸지 않는다 |
| N3 | accept conservative gate | 검토는267.072초에 끝났고 원래 마감까지 충분한 시간이 남았다. 실제 실행 전5,700초 gate를 다시 적용한다. 상한을 늘리지 않는다 |
| N4 | accept named output boundary | 승인된 기존 경계의 새 diagnostic WORK에만 쓴다. 기존 실패/입력 파일의 hash map은 계속 검사한다. 같은 root 아래 새 디렉터리가 생기는 사실과 기존 증거 불변을 구분한다 |
| N5 | accept limitation | supervision 만료는 PASS가 아니며 PID/정지 사유를 보존하고 다음 단계를 금지한다. Driver가 launch/관측 시간과 process 상태를 추가 기록해야 한다. 실행 전 고정 helper를 바꾸지 않는다 |
| N6 | accept bounded collection | 기준 복사본112개 전체 파일 목록·bytes·mode가 고정됐다. base collection은 실제 전체 목록/중복을 보존하고 seed20 각1회만 실행한다. 전체 suite 또는 현재 후보의 base20 통과라고 보고하지 않는다 |
| N7 | revise naming interpretation | review-authorization 파일은 실제 CLI 호출·슬롯 소비 기록이다. 권한은 이번 Owner의 명시 승인에서 오며 agent 파일이 생성하지 않는다 |
| N8 | accept exact launch | pinned absolute Python·-I/-S/-B·명시 env·cwd로 시작한다. 불일치 시 STOP하며 임의 환경으로 재시도하지 않는다 |
| 준비3 | accept | old named FIFO 관측이 path를 반환하면 새 fd 관측 범위 축소를 그대로 보고한다 |
| 준비4 | accept / compared | 새 기준 source101 digest는197699720edcfeda3a246e9120014444f64826984516ab9df95a2bdffedc6d36이다. 이전 P1a base102의91ec8d63…과 다르다. 이전 map에는 당시 추가한 test_entry_window_transition.py1개와 수정된 development README가 있었고, 새 map은 정확한 BASE101이다. 공유 Product/test 기준 파일은 나머지 모두 동일하다. 새 source를 옛 source와 같다고 주장하지 않는다 |
| 준비5 | accept | 기준20/current25/current16, 기준 경로 boundary probe, 원래15pass1failure와 재관측, 해당 method의 non-Git installed status 첫 관측을 구분한다 |
| 준비6 | verified | meta의 실제 model/session과 도구 부재·입력 보존을 확인했다 |

기동 전 고정 identity: dispatch SHA-256 `28109660e68591919b7e1d6d55bb429d7f45c65e9079453f84cbb73db95a5f5d`, run-recovery.py `fd3da7c4beef47680f1fcb261287af823c8eb0bbdc13de629ba2c85f0d95ff88`, fd-regression.py `f12ebbf0534ab3b72af3efe524a4c96bab80a480a695a6618464d70f5a907f2a`, execution-plan `b013bb1e342a95b31345ea93619c761e31c4d5189639a7e46b152f093be2dd5c`, Reviewer 원문 `de457dbb059df80e43169fd1916241172b6021acd5aaac95037f7a4bed364026`이다. source/controls/helper 수정 없이 준비 조건을 처분했다.

다음은 이미 승인된 fd1회 → controller7회 순서다. 원래 deadline과 수정된 누적9회·5,100초 상한을 적용하며 no-retry다. 아직 fd·controller는 실행하지 않았고 P1b 결과는15pass1failure, P2는 미착수다. 검토 원문과 처분의 기록 저장/GFM 검사는 제품 테스트 증거가 아니다.


### Recovery Actual Result — Base Qualification Passed; Stopped On Current Root Drift

Owner가 승인한 고정 실행안을 수행했고, 아래 실패 이후에는 재시도하지 않았다. P2도 착수하지 않았다. 성공한 사전 검증과 미실행 P1b를 구분한다.

| 단계 | 실제 결과 |
| --- | --- |
| 독립 검토 | 앞 절의267.072초·exit0, blocker 없음, Reviewer 누적4/4 |
| fd 회귀 | exit0·0.132614초, timeout 없음, process group 부재, old/new 기대값 일치 |
| 기준 acquire | exit0·0.645초, 정확한 OLD와 입력 보존 |
| 기준 canary | exit0·0.652초, 기존 named boundary/primitive/lock/Git/runtime 검사 통과 |
| 기준 collect | exit0·0.458초, 실제776 occurrences, factory 없음, seed20 각1회 |
| 기준 smoke20 | exit0·65.142초(controller),20/20 pass, failures/errors/skips/unstarted/unfinished0 |
| 현재 collect p1-controls | controller 외곽 exit1·0.077361초, config 단계에서 root membership/type drift, child·슬롯·parent inputs/result 생성 전 중단 |
| 현재 focused control25 | 미실행 |
| 현재 focused P1b16 | 미실행 |

fd 대조에서 구판 pipe read/write는 각각 errno9, 신판은 각각 None이었다. regular는 양쪽 regular, directory는 양쪽 '.'였다. closed fd는 양쪽 errno9, 신판의 합성 regular F_GETPATH 거부는 PermissionError/errno1로 전파됐다. extracted path_of + audit + subprocess는 구판 errno9/관측 FIFO1개, 신판 returncode0/관측 FIFO2개 및 정확한 stdout pipe-ok·stderr pipe-err였다. 실제 emit/active 전체 경로와 Product status의 종단 재관측은 여기서 실행하지 않았다.

**named FIFO의 관측 범위는 실제로 줄었다.** 구판은 path named-fifo를 반환했고 신판은 None이었다. 이는 이번2행 후보의 명시된 동작이며 숨기지 않는다. mkfifo는 이번 sandbox에서 허용됐지만, FIFO에 fault를 지정한 종단 음성 검사는 없고 current control25도 아래 root 실패로 실행하지 못했다. 기준 canary의 기존 primitive/fault/lock 대조만 통과했다. 이 결과를 현재 전체 통제 또는 P1b 제품의 qualification PASS로 확대하지 않는다.

#### Exact Stop Cause And Driver Responsibility

현재 SOURCE root의 입력 목록은16개였고 실행 시17개였다. 추가 항목은 `.idea` directory 하나이며 누락·기존 항목 type 변경은 없었다. 디렉터리 metadata의 생성 시각은2026-10-10 06:23:48.156177 UTC다. 생성 주체는 확인하지 않았으며 IDE 설정이라는 용도를 근거로 자동 제외하거나 지우지 않았다. 현재 Product/test source102와 보존 source map 및 control files의 bytes/mode는 모두 그대로였다.

핵심 실패 출력:

```text
controller.py main -> common.config -> verify_source_root
RuntimeError: source root membership/type drift
STOP: RuntimeError missing controller evidence; no retry
```

첫 줄의 root 비교가 실제 원인이다. 두 번째 STOP은 parent evidence가 생기기 전에 controller가 종료된 것을 외곽 helper가 보고한 결과다. collection/import/Product assertion 실패로 혼동하지 않는다. 이 단계는 child 생성과 실행 슬롯 생성 전이므로 새 collection이나 현재16개 결과가 없다.

Driver의 실행 전 대조는 계획에 든 파일의 bytes/mode와 baseline 전체 membership을 확인했지만, 현재 SOURCE의 즉시 루트 목록을 controller 진입 전에 직접 재대조하지 않았다. 따라서 `.idea`가 이미 추가된 상태를 사전 검토/기동에서 놓쳤고 기준4단계를 끝낸 뒤 controller의 정확한 root gate에서 발견됐다. 이는 이번 준비 절차의 한계이며, 사전 검사가 전체 입력 구조를 검증했다고 주장하지 않는다. 검사 기준을 완화하거나 이 변경을 정당화해 자동 재시도하지 않았다.

#### Accounting, Preservation And P1b Report

추가 controller 호출은5회(성공한 parent result4개 + 시작 단계 실패1회)이며 누적7/9회다. 성공한 새 controller 기록의 시간 합계는66.897초, 이전9.893초를 더한 parent-reported 누적은76.790초다. 실패한 시작의 controller receipt 시간은 unavailable이며 외곽 관측0.077361초를 별도로 보존했다. 이 실패를0초·미소비로 처리하지 않는다. 새5회 외곽 시간 합계도 private stop-summary에 있다. 누적 상한5,100초와 이전 P1a6회 이력, shared assertion correction0/1, 원래11:00:28 UTC 마감은 초기화하지 않는다. 미사용 controller2회가 있어도 no-retry 중단 조건을 우선한다.

fd와 성공한4단계는 입력 보존·자연 종료·group 부재를 기록했다. 실패 controller와 dispatcher도 종료했다. sandbox 안의 process 조회는 OS 권한 때문에 사용할 수 없어, 별도 읽기 전용 조회에서 관련 Python 검증 프로세스가 없음을 확인했다. 실패는 child 생성 전 traceback으로도 확인된다. supervisor timeout이나 남은 실행으로 보고하지 않는다.

모든 기존 보호 증거와 source/control bytes/mode를 재대조했다. `.idea`는 읽기 전용 metadata/name 확인만 했으며 수정·이동·삭제하지 않았다. old failure fixture와15pass1failure 결과, 원문 검토, 새 fd stdout, base4단계의 inputs/results/collection/counts, 실패 시작 argv/env/stdout·외곽 종료를 보존했다. runtime whole-recovery PASS 파일은 생성되지 않았다. 기록과 보존 검사는 제품 재실행이 아니다.

현재 P1b 보고는 **재검증 미완료**다. 이전 유효 실행은15pass1failure 그대로이며 원래 실패 ID의 installed Git status 및 뒤 non-Git subcase는 이번에 재관측하지 않았다. observer pipe 보정의 한정 회귀와 기준 revision smoke20이 통과했을 뿐, 현재 P1b16 또는 current control25 통과를 주장할 수 없다. P2·P3/P4·활성화·실제 적용·Owner 결과 수락/Done·Git publication은 수행하지 않았다.

구현 checkout, 원래 실패 경계, 새 기준 복사본과 새 qualification root는 Owner 실패 처분 및 잠재적인 entry 단계 재개의 구체적 소비자 때문에 유지한다. 새 qualification의 기준4단계를 버리거나 다시 수행할 필요가 있다고 단정하지 않는다. 재개를 별도로 승인한다면 `.idea`를 보존한 채 정확한 current root inventory를 검토·고정하고, 실제 명령 전 전체 root 대조를 갖춘 entry 단계 한정 실행안을 만들어 기존 controls/runtime/Git/증거의 재사용 조건을 확인해야 한다. 이는 후속 제안이며 지금 승인되거나 실행된 것이 아니다.


## P1b Verified And P2 Candidate Preparation — 2026-10-10

The Owner ran the exact previously authorized entry-resume command after the agent tool failed to start it, then requested result inspection. Recorded controller evidence shows collection825, control25/25 and foundation16/16, each natural exit0, no failed/error/skipped/unstarted/unfinished cases, process-group absence and preserved inputs. The original installed-reader failure passed for both the Git and non-Git subcases. The three new controller durations are0.454,20.228 and12.324seconds; cumulative reported109.796seconds plus1second reserved for an earlier startup failure. Controller calls10/10 and reviewer calls4/4 are exhausted. These are P1b results, not Owner result acceptance or P2 qualification.

The Owner subsequently said “계속하자”, paused with “잠깐 일시정지하자”, then resumed with “다시 시작하자”. This resumed the authorized P2 candidate authoring; it did not reset finite review/execution caps. A recoverable private supplement now holds an overlay for product.py, view.py and test_entry_window_transition.py. Current source runtime/tests remain at the verified P1b revision. Candidate behavior covers exact predecessor admission, one-way transition and bounded N/binding.next prefixes, S6 replay durability/content comparison, local manifest checks, same-entry lifecycle, schema3 detach and retired-entry handling.

The factory has21 proposed P2 methods,13 inherited plus8 added. Anticipated collection is776 default+57 factory=833, subject to actual loader verification. Static syntax/embedded-program compilation, control/foundation/shared-factory AST preservation,102 source-file and11 control-file preservation, and patch applicability/whitespace checks passed. No P2 product import, test, reviewer call, source installation, activation or Git action occurred. Full19-prefix/executor coverage, schema2 parent/worker cases, remaining default-fixture migration and later qualification remain open; this is a first focused candidate, not P2 completion.

The private PLAN/command/input supplement proposes at most2 additional1800-second no-tool reviews and4 controller calls (two collect300+focused1200 pairs, at most one existing shared ordinary-assertion correction). Cumulative call limits would become reviewer6 and controller14, keeping the5100-second controller cap and original20:00:28 KST deadline. The first review includes the new fixed test-program execution design; result R1 stays separate. Source/control/ownership/billing drift, boundary failures or unmet time gates stop execution. This is a proposal awaiting Owner approval, not an execution authorization.

Input identity: P1b-relative three-file delta SHA-256 `6d0f718106b313f220f4a3dec09397d874815b091a6373ea116d61f7d8cc08c2`; proposed102-file source map digest `c4fcfc9e49062e59ca6767247b4e87479517134187c75f943735f3112dbcf0d8`; review packet SHA-256 `4680b6b7e13f4007d36efcabef3b9ab42a74193208969b60857efdfdcf9ab563`. This delta includes the existing untracked factory and differs from the entire tracked Git diff; the private identity record preserves both bases. Candidate bytes are retained outside the implementation checkout for P2 review/execution and Owner disposition until accepted changes have recoverable custody. The implementation checkout and verification root have that concrete reuse purpose and are retained. No new progress owner or registry is created.


## P2 Added Budget Authorization And First Static Review — 2026-10-10

The Owner approved the proposed bounded P2 batch with “진행하자”: at most2 additional no-tool reviews,4 controller calls, one previously unused shared ordinary-assertion correction, the unchanged5100-second controller cap and20:00:28 KST deadline. This covers the reviewed candidate, bounded in-scope corrections, guarded three-file installation and first focused verification; it grants no activation, result acceptance, P3/P4, control expansion or Git action. The first review combines the candidate reading with R0 of its new fixed test program/execution design as proposed; result R1 remains separate.

Fresh reviewer `claude-opus-5-5`, session `cf440502-56da-4ccb-88f6-b8548913d32d`, completed in343.492seconds, exit0, no timeout, group absent. Authentication was `claude.ai / firstParty / pro`; no tool/MCP was available or used. Before/after input checks passed. This consumes review5/6 in this batch lineage. It is static inference, not executed P2 evidence. The exact reviewed packet digest remains `4680b6b7e13f4007d36efcabef3b9ab42a74193208969b60857efdfdcf9ab563`; its complete packet retains the pre-correction candidate bytes, and its input identity was retained with the review.

### Reviewer Response — Verbatim

````text
# P2 후보 정적 검토 결과 (R0, no-tool)

**판정: 현재 packet 그대로는 첫 focused 실행 준비가 되지 않았습니다.** 신규 8개 테스트 중 4개가 packet에 실린 코드만으로 확정적으로 `KeyError`가 납니다(B1). 그 밖에 기존 테스트 1개의 실패 가능성이 높고(B2), 비보정 대상 STOP으로 이어질 수 있는 시간·보존 한도 위험이 있습니다(B3).

아래 내용은 모두 packet 텍스트에 대한 **코드 추론**입니다. 실행, hash 재계산, 외부 조회는 하지 않았습니다. packet 내 실행 결과는 승계된 P1b뿐입니다.

## 1. Blocker (첫 focused 전 처분 필요)

### B1. `verify_workspace_product()` 반환 키와 신규 assertion 불일치 (확정적, 테스트 결함)

`verify_workspace_product`는 `binding_ref`, `launcher_sha256`, `release_path`, `inventory` 네 키만 반환합니다. `_entry_replay_result`의 `result["product"]`도 같은 값입니다. 신규 테스트가 여기에 없는 키를 읽습니다.

| 테스트 | 문제 접근 | 결과 |
| --- | --- | --- |
| `test_local_drift_after_s5_is_nonpass_with_b1_preserved` | `state['pending']`, `state['binding']['operation_id']` | `KeyError` |
| `test_changed_truth_replay_reports_unavailable_and_keeps_binding` | `result['product']['pending']` | `KeyError` |
| `test_same_entry_update_rollback_and_exact_repair` | `verify_workspace_product(target)['binding']['active_release']` (첫 줄 포함 3회) | init 직후 `KeyError`, 본문 미도달 |
| `test_retired_collision_blocks_completed_transition_replay` | `state['binding']['operation_id']` | `KeyError` |

- 이대로 실행하면 4건이 error가 되고, 1회뿐인 shared correction이 제품 결함이 아닌 테스트 결함에 소비됩니다.
- 수정 방향은 테스트 쪽입니다. `binding_ref['id']`가 곧 operation_id이고, pending이 없다는 것은 `verify_workspace_product` 성공 자체로 함의됩니다. `active_release`는 `_workspace_observe` 같은 명시적 내부 seam에서 읽을 수 있습니다.
- 제품 반환 형태를 넓히는 쪽은 `require_workspace_runtime`의 동등 비교 등 계약면이 달라지므로 권하지 않습니다.
- assertion 의미는 약화되지 않습니다. 다만 수정 후 hash와 delta를 다시 기록해야 하고, 수정된 bytes는 이번 검토 범위 밖이 됩니다.

### B2. `test_source_operation_matrix`의 init 교차 2건: exit 65가 아니라 70일 가능성 높음

- `new-source` + `--source OLD` 경로는 `workspace_init_preview` → `workspace_candidate(OLD)`로 들어갑니다.
- `ENTRY_MANAGED_PATHS` 순회 중 `adapters/colvia-work`가 OLD에 없으면 `_require_kind`의 `path.lstat()`이 `FileNotFoundError`를 냅니다.
- 이 경로에는 `OSError`를 `ContractError`로 바꾸는 래핑이 없습니다. CLI `main`의 `except Exception`이 받아 `HV2-INTERNAL`, exit 70이 됩니다. 테스트는 65와 `HV2-WORKSPACE-PRODUCT`를 기대합니다.
- 반대 방향(`old-source` + 후보 source)도 OLD 코드가 같은 구조라면 동일합니다. OLD 원문은 packet에 없어 확인하지 못했습니다.
- 전제는 OLD 트리에 `adapters/colvia-work/`가 없다는 것입니다. baseline 29개 literal 목록상 그렇습니다.
- 제품이 "관리 멤버가 없는 source"를 안정적 non-pass로 거부해야 하는지, 테스트 기대가 틀린 것인지는 Driver 처분이 필요합니다. 계약 해석이 걸리면 `needs-user`입니다.
- 이 테스트는 기존 13개에 속하지만 한 번도 실행된 적이 없고 selection에 포함되어 있습니다.

### B3. 신규 `checkpoint()` 증폭으로 인한 timeout과 보존 한도 STOP 위험 (추정, 실행 근거 없음)

- 이번 delta가 넣은 `checkpoint()`는 crossing apply 1회당 약 50회 호출됩니다(staging 멤버 30개마다, `_entry_append_file` 내부 6회×2 등).
- 매 호출이 `_workspace_observe`(2회 완전 관측, release 전체 재검증), `_lifecycle_truth`, `workspace_candidate(source)`를 다시 수행합니다.
- observer 아래에서는 target 내부 builtin `open`마다 audit 이벤트가 기록되고 event log가 fsync됩니다. apply 1회당 수만 건의 이벤트와 수 MB의 events 파일이 생길 것으로 추정합니다.
- 영향 1: `test_transition_new_root_write_prefixes_recover`는 9개 사례(OLD init + kill apply + recovery)가 하나의 180초 coordinator deadline을 공유합니다. timeout은 PLAN상 correction 대상이 아니고 자동 재시도도 없습니다.
- 영향 2: 이 테스트에서 subtest가 하나라도 실패하면 runner `preserve()`가 `self.base` 전체 크기를 셉니다. 64MiB를 넘으면 `preservation_stop` → `os._exit(87)`로 **run 전체가 중단**되고 나머지 테스트는 unstarted가 됩니다.
- 수치는 계산이 아닌 추정입니다. 실행 전에 Driver가 근거 있는 상한 산정을 기록하거나, 통제를 바꾸지 않고 닫을 수 있는 완화를 택해야 합니다. 예: staging 루프의 checkpoint 빈도 조정, 사례를 별도 테스트 ID로 분리. 후자는 ID 추가이므로 selection 재기록이 필요합니다.
- 완화가 통제나 timeout 변경을 요구하면 PLAN 규칙대로 STOP입니다.

## 2. 비차단 우려

- **N1. truth 변경 replay의 `degraded`/exit 10 (Owner 결정 필요)**
  - DR-0004는 "unavailable/non-pass"만 정했고 classification과 exit는 정하지 않았습니다.
  - `degraded`는 기존에 무결성 실패 의미로 쓰입니다. 검증된 정상 binding을 함께 반환하면 소비자가 오해할 수 있습니다.
  - 전환 후 일상적인 Work/intent 활동만 있어도 모든 과거 전환 replay가 10이 됩니다.
  - 같은 "비교 non-pass"인데 baseline drift는 `fail`/65입니다. 그 메시지(`...baseline differs`)에는 B1이 이미 게시되었고 cutover가 완료되었다는 표시가 없어, 운영자가 전환 실패로 읽을 수 있습니다. DR의 "product state와 project-result verification은 구분" 요구에 비추어 결과 형태를 정리할 필요가 있습니다.

- **N2. selection에 없는 C0-V 핵심 음성 사례**
  - S6 직후 rollback 거부(`first transition cannot roll back`). 코드에는 있으나 테스트가 없습니다. matrix의 rollback은 S0의 old target뿐입니다.
  - allowlist 밖 checkout-1 predecessor와 planning-1 predecessor 거부.
  - Git index가 `colvia`를 추적하거나 ignore가 가리는 상태에서의 전환 admission. init 쪽만 P1에서 다뤘습니다.
  - S5에서 exact O가 다시 나타나는 경우와 S3b(0600 완전본) 합성 사례.
  - 첫 focused 범위로는 수용할 수 있으나 PLAN 잔여 표에 명시하기를 권합니다.

- **N3. S5 + `binding.next` 존재 + exact O 재출현 시 복구 경로 막힘**
  - prefix가 S4로 분류되어 `allowed=False`가 되고, 영구 거부됩니다.
  - 보존 측면에서는 안전하지만, DR 표의 "re-observe S4 and repeat"와 맞는지 처분이 필요합니다.

- **N4. `test_same_entry_update_rollback_and_exact_repair`의 범위**
  - 복사 source fixture 자체는 유효합니다. `workspace_candidate`는 관리 29개 경로만 읽고 mode를 요구하지 않습니다.
  - 다만 docs만 바뀌어 launcher bytes가 같으므로, same-window의 `colvia` 교체 경로(`_replace_product_file`)는 실행되지 않습니다.
  - repair도 launcher 손상 1종만 다룹니다.

- **N5. `old_local` 프로그램의 위치**
  - "fixed program은 모듈 상수" 주석과 달리 메서드 내부 literal이고, argv에 `scope`가 추가되었습니다.
  - allowlist 검증이 있어 수용할 만하지만, 신규 subprocess 형태로 이번 R0에서 승인받은 것임을 기록해 두십시오.
  - OLD installed executor 증거가 아니라는 표시는 적절합니다.

- **N6. 숫자 불일치**
  - PLAN은 "foundation 16/16"이라 하는데 `factory_counts.EntryFoundationTests`는 11입니다.
  - P1b selection 구성이 무엇이었는지 한 줄 해명이 필요합니다.

- **N7. reviewer argv와 PLAN 산문 불일치**
  - `command-plan.json`의 `reviewer_argv`에 `--safe-mode`, `--restricted`가 있으나 PLAN 산문의 옵션 목록에는 없습니다.
  - 이 플래그들이 실제로 유효한지는 확인하지 못했습니다.

- **N8. `view.py`의 `hv2` 문구**
  - `hv2 view intent ...`, `hv2 view candidates`, "Harness v2" 표제가 entry-1에서도 그대로 나옵니다.
  - C2 범위라면 잔여 항목으로 명시하십시오.

## 3. 요청된 점검 항목별 소견

| 항목 | 소견 |
| --- | --- |
| intent required-ref 해석 | `_resolve_workspace_intent(..., require_current=False)` → `acceptances[...]["confirmation"]`의 required `document_refs`/`evidence_refs`와 revision `scope`를 NFC+casefold 포함관계로 검사. `view.py`의 사용 방식과 일치. schema-2 local parent도 `mode == "local"`로 포함됨. 결함 없음 |
| S6 durability / non-pass | N: file sync → fchmod → sync → parent sync 뒤에만 O unlink. `binding.next`: sync 후 B0 재확인, `os.replace`, 양쪽 directory sync. replay 시 재-fsync. 남은 `binding.next`, B1 mode≠0600, N mode≠0755 거부는 코드와 테스트 기대가 일치. 결과 형태는 N1 참조 |
| direct append 소유·mode | `O_CREAT\|O_EXCL\|O_NOFOLLOW` 0600, umask 사전 거부, fd/path identity와 nlink==1 재확인. 초기 apply에서 기존 occupant는 `recover or not exists`로 거부. 실행 가능 부분 prefix 거부. DR 표와 부합 |
| 첫 old rollback 거부 | preview, `_switch_binding_receipt`, `_entry_retirement` 세 곳에서 거부. S6 후 거부는 코드만 있고 테스트 없음(N2) |
| under-guard collision | 완료 replay는 guard 안에서 preflight 재실행 후 `_refuse_retired_entry`. same-window는 모든 checkpoint에서 재검사. 전환 중 O는 prefix 표가 관할. 문제 없음 |
| 명령 경계·예산 | `collect p2`, `focused p2`, `p2-correction`, `correction` 모두 `ENTRY_MODE_SLOTS`에 존재. 3,110.796초 ≤ 5,100초, 6,600초 + 여유 ≤ 6,900초 산술 일치. selection 21 = EntryProductTests 21(기존 13 + 신규 8) 일치 |

## 4. 확인하지 못한 근거 (packet에 없음)

- **`errors.py`**: 테스트가 `b'HV2-WORKSPACE-CONTRACT: wrong file type: colvia'`처럼 "CODE: detail" 연속 문자열을 기대합니다. CLI JSON은 `code`와 `message`가 별도 필드이므로, `message`가 code 접두를 포함해야 성립합니다. `ContractError`가 `ValueError` 계열이 아니라는 점도 전제입니다. `_require_kind` 오류의 실제 code도 볼 수 없었습니다.
- **`jsonio.py`**: `_sync_fd`가 `os.fsync` 속성 호출이어야 합니다. `fcntl` 기반이면 `test_local_baseline...`의 `fsync-after` 집합 assertion과 기존 `('fsync-after','colvia')` fault가 관측되지 않습니다. `write_new_bytes`가 최종 경로에 직접 쓰는지도 미확인입니다.
- **OLD source의 API**: `snapshot(..., verified_launcher_sha256=)` 단독 호출, `WorkStore._runtime`의 `inventory_id` 허용, `WorkspaceIntentStore.prepare/apply`와 `publish` 시그니처, draft 필드 검증, scope에 `hv2`/`colvia`를 둔 Work publish 허용 여부를 볼 수 없었습니다. 하나라도 다르면 `old_local` fixture가 error가 되고 신규 테스트 3개가 영향을 받습니다.
- **입력 파일**: `entry-p2-template.json`, `starting-inputs.json`, `common.py`, `prefix-oracle.json`, `baseline-inputs.json` 원문이 없습니다. template의 selection이 `test-selection.json`과 같은지, bound 사본 규칙이 `config`와 맞는지 검증하지 못했습니다.
- **기타 미열람 코드**: `workspace.py`의 `_exists`/`inspect_root`/`safe_target`, `work.py`의 `_visible_truth`/`_regular_files`/`work_graph`, `colvia` launcher 원문.
- **수치**: 모든 SHA-256, 예상 collection 833, 실제 소요 시간은 검증하지 않았습니다.

## 5. 권고 처분

1. B1은 `revise`입니다. 테스트 4개의 키 접근을 수정하고 hash, delta, selection을 다시 기록하십시오.
2. B2는 `revise` 또는 `needs-user`입니다. 제품 거부 code를 정할지 테스트 기대를 고칠지 결정하십시오.
3. B3은 실행 전에 상한 산정 근거를 기록하거나 완화하십시오. 통제나 timeout 변경이 필요하면 STOP입니다.
4. N1은 Owner에게 명시적으로 결정을 요청하십시오.
5. 위 수정 뒤의 bytes는 이번 검토를 받지 않은 상태입니다. 추가 reviewer 호출은 Owner 승인이 필요합니다.

첫 focused가 전부 통과하더라도 PLAN의 잔여 항목(19개 prefix 대응, parent/worker, executor matrix, default suite), P3/P4, Owner 결과 수락이 남습니다. 이 검토는 P2 완료나 Owner 수락을 뜻하지 않습니다.
````

### Driver Disposition And Authorized In-Scope Corrections

| Finding | Disposition | Evidence and action |
| --- | --- | --- |
| B1 | revise | Confirmed the public verifier returns only four proof keys. Fixed the four tests to use verified internal observation where binding/pending is required, without extending the public API. Driver also found the same invalid `product["binding"]` access in `_entry_replay_result` itself and replaced it with `binding_ref["id"]`. Both are static defects; no failed P2 run is claimed. |
| B2 | revise | Inspected both complete candidate readers. Missing managed members raise `FileNotFoundError` before mutation. New source now maps OSError in candidate loading to the existing Product error65 with preservation guidance. Exact retained OLD remains unmodified; its cross-source fixture explicitly expects historical `HV2-INTERNAL`70/`FileNotFoundError` and exact preservation. That OLD case is not evidence of a typed entry fence or stable Product65. This is bounded input-error handling, not a new supported source window. |
| B3 | revise | Split the nine physical prefix subcases into nine fixed IDs, each with its own existing180-second coordinator and failure-fixture directory. All former assertions and fault tuples remain. No checkpoint, observer, timeout,64MiB preservation limit or policy was weakened. This removes nine-case aggregation; it is not a measured per-case performance guarantee. The first run must establish actual cost, and any timeout/preservation STOP remains non-retriable under this batch. |
| N1 | revise / defend | The Owner-approved PLAN already proposed transient `degraded`/exit10 for unavailable historical comparison while returning the verified proof. Retain that bounded implementation mapping; no new durable state or writer gate is introduced. Add explicit B1-current/cutover-complete preservation wording to S6 baseline mismatch, which remains Product65. Add ordinary source status/pass observation after changed-truth replay to distinguish the historical comparison from current Product readiness. No broader claim about user-facing contract activation is made. |
| N2 | revise | Add first-entry rollback refusal and synthetic S5 re-observation of exact O/S4 recovery. Remaining outside-allowlist/planning predecessor, transition-specific index/ignore, full physical-prefix and parent/worker cells remain required before a P2 exit claim. Existing init coverage is not substituted for them. |
| N3 | defend | The accepted sequence syncs O's retirement before creating binding.next. A re-observed S4 without binding staging can be retried and is now covered explicitly. O plus already-created binding.next is not listed as a supported physical prefix; retain refusal rather than silently extend recovery to that composite state. No power-loss ordering or authorship guarantee is claimed. If the Owner later wants that additional combination, it needs a contract disposition, not an unrecorded repair. |
| N4 | revise | The second source fixture now changes an inert comment in the launcher bytes, so update and rollback exercise actual launcher replacement; assert the root bytes after each direction. Repair coverage remains explicitly launcher damage only. |
| N5 | accept | Record the method-local fixed OLD program and its closed `a/hv2/colvia` argument allowlist as the new R0-reviewed subprocess form. Clarify the source comment; it is an OLD API fixture with a verified runtime seam, not an OLD installed invocation. |
| N6 | accept | P1b16 means11 EntryFoundationTests plus5 existing default test IDs. The factory class alone has11. |
| N7 | accept | Actual invocation retained `--safe-mode` and `--restricted`; exit0 and startup tools/MCP empty are observed. The exact argv, not the abbreviated PLAN option prose, identifies the call. |
| N8 | accept | Current view wording/commands belong to P3/C2 and remain open. This P2 delta changes only collision fields in view. |
| Unavailable dependencies | revise | Driver inspected errors.py and jsonio.py: CLI JSON keeps code/message separate; `_sync_fd` calls `os.fsync` before platform fullfsync. Corrected combined-string assertions to exact JSON fields. Inspected retained OLD candidate/snapshot/store signatures; keep their source identity and test-seam limits. Add these exact dependencies and changed inputs to the remaining result-review packet. No runtime observation is claimed by this reading. |

The adjusted P2 selection has31 IDs: the former21 minus one aggregated prefix ID plus nine one-case IDs plus two new bounded cases. Expected factory67+default776=843 occurrences; actual loader comparison remains mandatory. Control/foundation/shared-factory ASTs and all102 current source inputs/11 frozen controls remain unchanged. Static compile (including the fixed OLD literal), exact patch applicability and whitespace checks pass. These corrections precede any P2 test and do not consume the shared post-failure correction.

Current P1b originals for the three prospective edits are preserved outside the implementation checkout, with readback/hash checks, for the named P2 installation/reversal consumer until accepted changes have recoverable custody. Updated P1b-relative delta SHA-256 `b36cac28c75077d0087d8d99476fadb1ccac76498a64c0ee9b9c51ac16d09768`; proposed source map digest `af0923f83869188cfacd82bccf06939010711064f45c1e7e9463ebec1b426289`. The earlier packet/result remains the reviewed revision; these corrected bytes are Driver changes, not retrospectively reviewer-approved. Under the approved batch, their actual result and dispositions go to the remaining R1 call; any new execution boundary or unresolved contract expansion stops before execution.

## P2 First Focused Result And Recovery Stop — 2026-10-10

The Owner-approved first P2 candidate was installed into the three named source files. The exact tested source map digest is `af0923f83869188cfacd82bccf06939010711064f45c1e7e9463ebec1b426289`; Git base remains `238514686078ce1564010a7b69013f48a635c57c`. No commit, push, activation, adopter operation or P2 acceptance occurred.

### Executed Evidence

The fixed CPython3.14.7 controller used the previously approved `-I -S -B` bootstrap, source cwd, allowlisted environment and sandbox. Exact argv/cwd/environment and input hashes are in `p2-preparation-01/p2-collect-start.json` and `p2-focused-start.json` in the existing private bundle; these identify the executed command, not an inferred example.

| Invocation | Actual result |
| --- | --- |
| `controller.py entry-p2-template.json INPUT_SHA collect p2` | exit0;0.465s parent;843 discovered=776 default+67 factory; exact occurrence comparison passed;31 selected IDs each occur once |
| `controller.py entry-p2-bound.json INPUT_SHA focused p2` | runner exit1/controller outer exit2;249.688s parent,249.741622s outer;31 run,30 pass,0 failures,1 error;skip/expected-failure/unexpected-success/unstarted/unfinished0 |

Both runs naturally completed with process group absent and inputs unchanged. Focused `execution_pass=false`; this is a failed suite, not P2 success. The bound collection hash and unchanged-field check are recorded in `p2-collection-binding.json`. Runtime/source identities and actual counts are consolidated in `p2-observed-result.json`.

Essential failure output:

```text
ERROR: test_fresh_init_collision_before_any_write
  test_entry_window_transition.py:716
    target=self.directory('negative-'+kind+'-'+name)
  test_entry_window_transition.py:284
    p = self.base / name; p.mkdir(); return p
FileExistsError: [Errno 17] File exists: .../negative-file-HV2
Ran 31 tests in 249.358s
FAILED (errors=1)
```

This error occurs while constructing the second negative fixture, before its product call. Read-only stat of preserved `negative-file-hv2` and `negative-file-HV2` returned the same device/inode, confirming the case-alias fixture collision. The positive init and first lowercase-file branch were reached, but the remaining uppercase-file/directory/dangling-link cases do not have passing evidence. The runner preserved the596,083-byte failed fixture at `focused-p2/work/failures/0`; the named consumer is this unresolved failure diagnosis/recovery until disposition and verified replacement evidence exist. Other30 recorded pass outcomes support only their own assertions and seam limits.

### Driver Disposition And Proposed Correction

Driver accepts this as a test setup defect. The approved PLAN limits automatic correction to ordinary product assertions; this error is outside that exception. Shared correction remains0/1. No correction was applied and no controller was retried.

Prepared `fixture-correction-proposed.patch` changes exactly two lines: enumerate the four existing cases and prefix each temporary directory name with its index. The actual tested names/types/IDs/assertions remain identical. Patch SHA-256 `7306378a6baf90d4fbd0e5ec2ac8fdadb93784a84a9c114b6f329870d84a2667`; proposed factory SHA-256 `6bb137784f82c9fdcfda5bec0f6817f68d443f4c34112b4ec88c3450e225392b`. Static syntax and exact patch applicability pass. This is not a reproduced post-fix pass.

### Result Review Block

A fixed R1 packet was prepared, SHA-256 `fd2f7b752ccf00df06975ce1393a6050b6b656a67f8eff85ac638fb92ba55fea`, containing current source, actual failure evidence, prior review/Driver disposition, dependencies, frozen controls and the unexecuted two-line proposal. The remaining review invocation was rejected by automatic approval review before process creation. The initial stated reason was lack of permission for P2 and external Claude transfer. The Driver checked the subsequent 17:19 proposal for up to two Claude reviews and the Owner's17:20 “진행하자” approval, supplied that evidence and requested reconsideration of the same action. The second review again rejected it, stating that the supplied approval evidence was agent-generated and did not establish authorization for private-source/result transfer to Claude. No further invocation or alternative transmission was attempted.

No reviewer session/auth observation/response exists for this blocked R1; `review-02` was not created. Actual reviewer usage remains5/6. This is an approval-review block, not a Claude verdict or runtime failure. The Owner must explicitly authorize the stated private source/test/result data and Claude destination before another attempt. Prior completed review01 remains the only P2 reviewer response; it is retained verbatim above and does not qualify the later runtime result.

### Budget, Preservation And Next Owner Decision

Controller usage12/14; cumulative parent time359.949s plus prior failed-start reservation1s=360.949s against5100s. Reviewer5/6; correction0/1. Source102/control11 and174 prior evidence files were hash-checked unchanged after the failed run. The three tested candidate files remain preserved outside the implementation checkout; pre-P2 originals are in `pre-p2-source/`. Original implementation and verification worktrees are retained for the concrete proposed correction/review use, not eligible for retirement now.

`fixture-recovery-proposal.md` in the same private bundle makes the next decision concrete: explicitly allow the exact two-line fixture correction as the sole shared correction, use the remaining collect/focused pair (300/1200s), then send the exact private result packet to the existing Claude subscription no-tool review (1800s). Existing14/6 call caps and20:00:28 KST deadline remain; no additional budget is assumed. If authorized, the new complete batch requires3390s remaining. Another failure/drift/timeout stops without retry. The blocked failed-result packet stays historical; later results require their own exact packet.

Full19 prefix, all4 executor/writer cells, parent/worker and current-window default-fixture coverage remain incomplete, along with P3/P4 and Owner result acceptance. Toolstead STATUS is unchanged: this source task remains the sole progress owner and no phase/Done/activation decision was made.

## P2 Fixture Recovery And Final Bounded R1 — 2026-10-10

### Owner Authorization And Exact Change

After the previous stop report, the Driver explicitly requested the exact two-line fixture correction, one remaining collection/focused pair, and transfer of the private P2 source/test/result packet to the existing Claude subscription service for the final review. The Owner replied “계속하자”. This approves the named fixture-error exception and external review scope; it is not result acceptance, DR amendment acceptance, P2 Done, activation or Git authorization. The previous automatic approval block was not bypassed: a new explicit Owner request preceded the successful invocation.

Applied only the proposed two-line test change with patch SHA-256 `7306378a6baf90d4fbd0e5ec2ac8fdadb93784a84a9c114b6f329870d84a2667`. It indexes the four fixture directories, while preserving tested names/types,31 selected IDs and all assertion ASTs. No product or control code changed in this correction. Before changing source/candidate, the failed factory bytes were preserved at `fixture-recovery-01/failed-factory.py` outside the source checkout; readback SHA-256 `571a0bd99931aaf480e13fe9de50503fc767043d0c13db3a12bcf21d5c06615d`. Corrected source/candidate/readback SHA-256 `6bb137784f82c9fdcfda5bec0f6817f68d443f4c34112b4ec88c3450e225392b`,102337 bytes. The current102-file source map digest is `18c2b62e6b12c589ecb5a030696c9518cdaa31934f7b66c8ec3bd7c8e6267a4b`; Git base remains `238514686078ce1564010a7b69013f48a635c57c`.

### Executed Correction Evidence

Exact commands, cwd, runtime and seven-field parent environment are in `fixture-recovery-01/collect-start.json` and `focused-start.json` of the existing private bundle. They use the unchanged reviewed controller/bootstrap/sandbox and CPython3.14.7, with child source/OLD/controls read-only and network denied. No ad-hoc reproduction or extra suite ran.

| Invocation | Observed result |
| --- | --- |
| `controller.py entry-correction-template.json INPUT_SHA collect p2-correction` | exit0,0.453s parent,0.507869s outer;843 occurrences=776 default+67 factory |
| `controller.py entry-correction-bound.json INPUT_SHA focused correction` | runner/controller exit0,247.994s parent,248.063174s outer;31 selected/run/pass;error/failure/skip/expected-failure/unexpected-success/unstarted/unfinished0 |

Both have natural completion, process-group absence, input preservation and `execution_pass=true`. The Driver compared the full failed-run/current collection objects: all fields except the deliberately changed source digest are equal, including default/factory lists, ordered occurrences and duplicate counts. Selected-file bytes are identical between runs. Actual collection hash is bound to the focused invocation. This full-object check is Driver-executed evidence; the no-tool reviewer did not receive the collection original and therefore did not independently repeat it.

The formerly failing case now passes, including its uppercase-file, directory and dangling-link branches. The before result remains30 pass/1 fixture error; it was not overwritten or reclassified. The failure fixture and exact pre-fix factory remain retained for the named failure/review/Owner-disposition consumer until the disposition and recoverable custody end condition is met.

### R1 Request And Actual Identity

The final bounded review received the exact corrected source and pre/post execution results, prior review/Driver dispositions, accepted DR, dependency excerpts, controls and two-line patch. Packet SHA-256 `9bc0192e9c4f41701e0cb16932e080376a2a5bfe1df405a8d998475cdffa8d66`,713297 bytes. It identifies the whole tracked diff digest separately from untracked factory/control inputs; the current bound invocation identifies all102 source inputs. Earlier packets remain historical and were not overwritten.

Actual reviewer: `claude-opus-5-5`, fresh session `3e1736c7-1708-48d9-afbb-d64b1de736bc`; Claude Code2.1.296, requested `opus`/`medium`. Non-secret auth check before invocation: loggedIn=true, authMethod=`claude.ai`, apiProvider=`firstParty`, subscriptionType=`pro`. No API/provider override was present. No tools/MCP at startup and0 tool calls; no source editing/test execution permitted. Runtime129.582s, exit0, timeout=false, process group absent, post-review input check PASS. Driver/reviewer models and sessions differ, but the reviewer only saw the bounded Driver-supplied packet; it did not independently recalculate hashes, inspect omitted source, re-run tests or authenticate Owner instructions.

### Reviewer Response Verbatim

# P2 focused 보정 결과 검토 (R1, no-tool, 6/6 최종)

**판정**
- **보정 focused 31건**: 차단 사항 없음. "focused 31/31 pass, 범위 한정 증거"로 기록해도 됩니다.
- **전체 P2**: 완료·종료 주장은 불가합니다. 아래 B1–B5가 닫혀야 합니다.
- 이 검토는 Owner 수락이 아닙니다.

근거 구분: 실행 결과는 packet에 전사된 파일을 읽은 것이고, 저는 hash 재계산이나 재실행을 하지 않았습니다. 코드 관련 소견은 모두 정적 추론입니다.

## 1. 보정 focused 결과 (관측 증거)

- **실행 결과**: 31 run, 31 pass이며 error·failure·skip·unstarted·unfinished가 모두 0입니다. exit 0, 자연 종료, group 부재, 입력 보존이 `result.json`·`counts.json`·`executed.jsonl`에서 서로 일치합니다.
- **선택 동일성**: `selected.json` hash가 실패 run과 보정 run에서 같습니다(6a96ae…). ID 삭제나 교체는 없습니다.
- **patch 범위**: patch는 정확히 두 줄입니다. 파일 크기 증가분(102303→102337, +34B)이 patch 문자 수(19+15)와 일치합니다(정적 산술).
- **충돌 해소**: 네 디렉터리명이 index로 구분되어 case-insensitive 충돌이 사라집니다. 대상 이름 `hv2`/`HV2`, 종류, assertion은 그대로입니다.
- **새로 얻은 증거**: 첫 run에서 실행되지 못한 대문자 file, directory, dangling-link 경로가 이번에 처음 실행되었습니다.
- **예산**: 누적 시간 360.949+0.453+247.994=609.396초로 산술이 맞습니다. controller 14/14, correction 1/1, reviewer 6/6이 소진되었습니다.
- **B3 우려**: 최장 테스트가 28.9초(한도 180초), 전체가 248초(한도 1200초)여서 이번 실행에서는 나타나지 않았습니다. 성능 보증은 아닙니다.

## 2. 전체 P2 종료를 막는 사항

기존에 명시된 gap은 모두 유지하고, 이번에 구체화한 내용을 더합니다.

- **B1. 19 prefix 미충족.**
  - kill 9건은 N-01, N-02(2건), N-03, N-04, O-01, B-02, B-03, B-05의 after edge만 다룹니다. 19개 ID 중 7개입니다.
  - 미실행: 모든 before edge, S3-01 rename, N-05, O-02, B-01, B-04, B-06, B-07.
  - S1·S2는 합성 tear와 `InjectedCrash`뿐입니다.
  - oracle은 "각 실제 연산의 before/after"를 요구합니다.
- **B2. 전환 증거가 전부 non-Git target입니다.**
  - `_OLD_PROGRAM_BASE`가 non-Git topology를 강제합니다.
  - S1 전 `colvia` index·ignore admission(`_entry_absence_admission`, `_visible_truth`)을 Git target 전환에서 실행한 증거가 없습니다.
  - Git target의 S6 local baseline 비교도 실행 증거가 없습니다.
- **B3. executor×writer matrix.**
  - late-lock은 OLD independent-source detach 1개 cell뿐입니다.
  - `installed-old`는 P2 선택에서 한 번도 쓰이지 않았습니다.
  - `installed-new`의 update/rollback/detach(`require_workspace_runtime` 경로)도 없습니다.
  - Work/intent/candidate writer cell이 없습니다.
- **B4. parent/worker.**
  - schema-2 parent baseline과 required-ref 사례가 없습니다.
  - worker/orphan 허용, old ticket·proof 거부, 새 baseline 성공의 실행 증거가 없습니다.
- **B5. 전환 이후 target의 lifecycle.**
  - update/rollback/repair와 schema-3 detach 테스트는 모두 fresh entry-1 init target에서만 실행됩니다.
  - schema-2 retirement receipt와 checkout-1 release가 history에 남은 target의 mixed-history detach·repair·update는 실행되지 않았습니다. DR 필수 qualification 항목입니다.
  - 코드상 `_detach_plan_shape`가 혼합 membership을 처리하는 것으로 읽히지만 정적 추론입니다.

default suite의 fixture 이관, P3/P4, Owner 결과 수락도 그대로 남아 있습니다.

## 3. 비차단 우려

1. **Owner 결정 미결 (N1).** truth 변경 replay의 `degraded`/exit 10은 DR-0004와 v2.1에 정의된 mapping이 아닙니다. Driver는 PLAN 승인으로 갈음했지만, PLAN 스스로 "검토 대상"이라고 적었습니다. 테스트 통과는 구현과 기대가 일치한다는 뜻일 뿐이므로 명시적 Owner 처분이 필요합니다.
2. **Owner 결정 미결 (N3).** O 재출현과 `binding.next` 동시 존재 시 영구 거부가 됩니다. Driver의 방어는 "O 제거 sync 후 staging 생성" 순서에 기대는데, `sync_directory`는 EINVAL/ENOTSUP일 때 `unavailable`을 반환하고 호출부가 이를 무시합니다(정적 추론). 계약 처분 대상입니다.
3. **약한 oracle.** 아래 테스트는 `HV2-WORKSPACE-PRODUCT` 코드 계열만 확인합니다. 이 코드는 거의 모든 거부에 쓰이므로, 통과는 "거부+보존"만 입증하고 거부 사유는 입증하지 않습니다.
   - `fresh_init_collision`
   - `s6_rejects_*`
   - late collision
   - invalid prefix 5건 중 4건
   - matrix의 rollback/repair/detach
4. **`fresh_init_collision`의 범위.** preview 호출만 하므로 "before any write"가 apply 경로에서 검증된 것은 아닙니다. 관측 이름 assertion은 P1 foundation에만 있습니다.
5. **D1-A/lifecycle 충돌 범위.**
   - 충돌 진단: P2에서 status와 doctor만 실행되었고 `view`는 미실행입니다.
   - 충돌 시 lifecycle 거부: detach preview와 완료 replay만 실행되었고, live entry-1의 update/rollback/repair 거부는 미실행입니다.
6. **검토 순서.** 첫 실행 전 Driver 수정(B1/B2/B3/N2/N4 반영분)은 사전 검토 없이 실행되었고, 이번이 첫 열람입니다. `workspace_candidate`의 OSError→65 래핑, 9개 ID 분리, 추가 2건에서 정적으로 결함은 찾지 못했습니다.
7. **수정 금지 유지.** 예산이 모두 소진되었으므로 위 항목 때문에 source를 고치거나 재실행하려면 새 Owner 승인이 필요합니다.

## 4. 누락 증거

- **collection 동일성**: `collect-p2-correction/collection.json` 원문이 없습니다. "843개 순서·occurrence 동일"은 Driver 진술이고, 제가 본 것은 개수와 selected hash뿐입니다.
- **수정 전 원문 보존**: 수정 전 테스트 원문(571a0b…)을 별도 보존했다는 readback 증거가 없습니다. factory는 untracked라 Git custody도 없습니다.
- **증거 파일 수**: 이전 증거 파일 수가 174에서 210으로 늘어난 내역 설명이 없습니다.
- **Owner 승인**: "계속하자"는 Driver가 작성한 JSON으로만 제시되어 독립 확인할 수 없습니다.
- **미열람 원문**: `entry-correction-template.json`, OLD source, `work.py`·`intent.py`·`workspace.py` 발췌 외 부분, `colvia` launcher.
- **범위 밖**: power-loss 지속성과 비계측 CLI 동작은 어떤 실행으로도 입증되지 않았습니다.

## 5. 권고 처분 (Owner 자문)

- 보정 focused 결과는 "31/31, fixture 보정 1회 후, 범위 한정"으로 수락 기록할 수 있습니다. 실패 run(30/1) 증거는 그대로 보존하십시오.
- P2 Done, activation, P3 진입 근거로는 쓰지 마십시오. B1–B5와 N1/N3 처분을 다음 계획의 명시 항목으로 올리십시오.

### Driver Dispositions

No source change or additional test/reviewer call follows this R1. The finite correction/controller/reviewer budgets are exhausted. Reviewer advice is not an Owner decision.

| Finding | Disposition | Driver conclusion and remaining boundary |
| --- | --- | --- |
| Bounded focused verdict | accept | Record31/31 after one fixture correction, with normal completion/cleanup and preserved inputs. This does not qualify full P2 or admit P3/activation. |
| R1-B1 physical prefixes | accept with count correction | Nine kill tests select eight distinct numbered IDs (N-01,N-02,N-03,N-04,O-01,B-02,B-03,B-05), not seven; N-02 appears twice. This arithmetic correction does not close the substantive gap. Full19-ID/before-after sequence, remaining directory-sync/publication edges and S1/S2 execution distinctions remain open. |
| R1-B2 Git transition | accept | Current exact-old transition fixture forces non-Git. Git index/ignore admission and Git local S6 baseline comparison are unverified. |
| R1-B3 executor/writer cells | accept | One independent OLD detach late-lock case and source-operation cases do not establish four-executor or Work/intent/candidate writer coverage. |
| R1-B4 parent/worker | accept | Schema2 parent/required-ref and worker/orphan, old ticket/proof refusal and new retained baseline success remain open. |
| R1-B5 mixed-history lifecycle | accept | Same-entry update/rollback/repair and schema3 detach passed on fresh entry targets. Those results do not prove lifecycle behavior on a target retaining the actual checkout-1→entry-1 history. Add this explicit gap to the remaining P2 scope. |
| R1-N1 replay result mapping | needs-user | Keep `degraded`/exit10 and unavailable transition-content field as the currently tested implementation candidate only. PLAN execution approval is not exact DR mapping acceptance. Recommend an explicit named Owner disposition before full P2 closure; verified B1 and current Work checks must remain usable. |
| R1-N2 (prior N3) O plus binding.next / sync unavailable | revise; needs-user | Withdraw the prior unconditional implication that call ordering alone proves this composite impossible. Static inspection confirms `sync_directory` may return unavailable on EINVAL/ENOTSUP, and the transition calls do not inspect that return. Current code preserves/refuses O+binding.next; no executed counterexample or power-loss proof is claimed. The unavailable-sync and supported-recovery boundary needs an explicit contract disposition and bounded verification proposal, not an automatic source fix. |
| R1-N3 diagnostic oracle specificity | accept | Code-family+preservation assertions prove those observations only. They do not independently establish every intended diagnostic reason; strengthen exact reason/observation assertions in a separately approved follow-up. |
| R1-N4 fresh init scope | accept | Collision cases exercised preview. Their test name is not proof of apply-path refusal. Keep that limitation explicit. |
| R1-N5 collision consumers | accept | P2 evidence covers status/doctor and specified detach/replay paths; view and live update/rollback/repair collision cells remain unverified. |
| R1-N6 Driver changes before execution | accept with scope clarification | The approved batch allowed bounded Driver corrections before the first run, and reserved R1 for later review. These bytes were not independently pre-reviewed; this R1 first inspected them and found no static defect in the named changes. Do not retrospectively describe pre-run approval or a fresh R0. |
| R1-N7 exhausted limits | accept | No further correction, execution, review, P3 or qualification begins under this batch. |
| Missing collection/pre-fix custody/174→210 explanation | revise record, not reviewer claim | Driver readback checked both factory hashes before and after, compared full collection objects and retained210 prior evidence files. The36 added entries are existing run records: collect-p1-controls4, focused-p1-controls9, focused-p1 9, collect-p2 4, focused-p2 10. They were added to the preservation map, not newly generated runtime evidence. These checks were not independently performed by the reviewer. |
| Owner instruction visibility and omitted inputs | accept limitation | The actual human request exists in this chat; the no-tool reviewer cannot independently authenticate it from the packet. Missing OLD source, launcher and unexcerpted dependency bodies remain outside that review. No extra review is claimed or automatically required merely to duplicate a prior check. |
| Power-loss / non-instrumented coverage | accept | Neither process-kill tests nor this no-tool R1 establish power-loss persistence or uninstrumented full-CLI qualification. |

### Final Preservation And Next Bounded Decision

After review, Driver rechecked current source102, controls11, runtime/Git/config, exact OLD and210 prior evidence files unchanged; before/corrected factory readbacks and collection/selection comparisons passed. Prior failure results and the new passing slots are distinct. Source remains uncommitted on `codex/colvia-brand-transition`; no commit/push/PR/merge, adopter update, DR activation, P2 Done or Owner result acceptance occurred. No STATUS update is proposed because the owning source task remains in progress and no phase decision changed.

Actual cumulative controller14/14, reviewer6/6 and correction1/1. Controller time608.396s plus the retained1s failed-start reservation=609.396/5100s. Remaining wall time does not authorize more calls. The absolute deadline remains2026-10-10 20:00:28 KST for this exhausted batch.

Next scope should first obtain exact Owner dispositions for the replay exit mapping and unavailable-directory-sync/composite-prefix recovery boundary, then define a new finite P2 verification slice covering the remaining cells without claiming full readiness from this focused pass. That is a proposal, not new execution authorization. Both source and verification checkouts have this concrete near-term reuse; current candidate, failed factory, P1b originals and required failure evidence have durable custody outside the source checkout, so neither checkout is retired now.

## D3 Design Candidate Preparation — 2026-10-10

Following the bounded R1 result, the Owner said “계속하자”. The Driver continued read-only analysis and prepared the next exact decision/review proposal. This is not acceptance of previously nonexistent D3 wording or an increase to the exhausted reviewer/controller limits.

Recommended D3-A revision1.0 now makes two R1 dispositions concrete: historical truth-change comparison uses transient `degraded`/exit10 while retaining the verified current binding; required transition directory synchronization must succeed or stop with `HV2-WORKSPACE-PRODUCT`/exit65, preserving the observed prefix/current binding. It explicitly preserves/refuses B0+exact O+executable N+nonempty binding.next, rather than claiming that composite physically impossible or expanding automatic recovery. The operational cost is a possible separately authorized external recovery/disposition. Existing supported S4 reappearance without nonempty binding staging remains intact.

Static inspection includes the indirect directory-sync calls in workspace/jsonio helpers. The proposal therefore requires closure of the admitted transition's required sync paths rather than wrapping only the O-unlink call; unrelated shared helper behavior remains outside scope. Current source does not implement that strict rule. No unavailable-sync counterexample, runtime import, product command, new test or new Reviewer call ran during this preparation.

Exact proposed append text: private supplement `contracts-d3-01/amendment-draft.md`, SHA-256 `c0b575419e4374a71db4545e36f3569f95c15ffbf744deca3a2ff8238dec16ea`. It is not appended to DR-0004, not Accepted and not activation. `contracts-d3-01/PLAN.md` records the practical choices, limitations and next action. Fixed private review packet SHA-256 `7aa7082fcfffe14fd03ddea798292b158e4107ae5692e5d3697b4330abf547e3`,141945 bytes, includes the draft, current accepted DR, previous R1/Driver dispositions, inherited result and named current code excerpts. Full source identity and omitted-source limits are separate in `input-identity.json`. Source base/current map remain `238514686078ce1564010a7b69013f48a635c57c` / `18c2b62e6b12c589ecb5a030696c9518cdaa31934f7b66c8ec3bd7c8e6267a4b`; controls11 remain unchanged. Static syntax/GFM checks are preparation evidence only.

Next proposed batch is one fresh Claude no-tool static design review, at most1800s, using the existing subscription path, with exact auth/input checks and verbatim response/Driver disposition in this task. It requires an explicit reviewer allowance6→7; controller14/14 andcorrection1/1 remain exhausted. Existing20:00:28 KST deadline stays fixed and review start requires more than1830s remaining. No automatic retry, source/test/control edit, DR acceptance, execution root, runtime test, P3, qualification or Git action is included. Exact argv/output/limits are prepared in `command-plan.json`; the runner has not been invoked and no review/owner-authorization output exists.

The existing P2 collection/focused/correction slots are already consumed. A later implementation/test plan must explicitly resolve the suitable execution boundary and input/slot/control policy; reusing a consumed slot, overwriting prior failures or relabeling P2 as P3 is not authorized by this proposal. Full P2 gaps from R1 remain open.

This task remains the sole progress owner; Toolstead STATUS and DR acceptance state are unchanged. The durable preparation supplement serves the next D3 review/Owner decision and does not create another Work or acceptance ledger. Existing source and verification roots remain in use for that concrete next scope; prior originals/candidates/failure evidence remain preserved.

## D3 Review Authorization And Pre-launch Block — 2026-10-10

At 09:21:02 UTC the Owner said “승인” to the proposed D3-A static review: one additional no-tool Claude call, maximum1800s, with the existing absolute deadline and no product/test/control/runtime/DR acceptance or Git action. The Driver recorded that authorization against the exact proposal and packet identities in the private supplement. Reviewer allowance is now7, while actual completed calls remain6; controller14/14 and correction1/1 remain unchanged.

The attempted fixed runner launch was rejected by automatic approval review before process creation. Stated reason: transmission of a private design packet to the external Claude service was not sufficiently authorized because trusted user content did not explicitly identify this payload and destination. No authentication check, reviewer process, external packet transmission, review output, runtime test or source change occurred. The Driver did not retry or use an alternate path. The exact packet remains141945 bytes, SHA-256 `7aa7082fcfffe14fd03ddea798292b158e4107ae5692e5d3697b4330abf547e3`.

The outstanding request is explicit permission to send that packet—private D3-A candidate, current DR-0004, source excerpts, prior reviewer/Driver records and test-result summary—to Anthropic Claude through the installed CLI and existing subscription for this single no-tool review. This is permission for the external transfer only within the already bounded review scope, not design acceptance. The unchanged deadline still requires more than1830s remaining at launch. Existing source/verification checkouts and all required inputs remain retained for the same near-term review and remaining P2 work.

## D3-A Static Review And Driver Disposition — 2026-10-10

### Authorization And Actual Execution

After the pre-launch block, the Owner explicitly authorized sending the linked private packet containing D3-A, DR, source excerpts, prior review and test summaries to Anthropic Claude through the existing subscription CLI, for one no-tool static review up to30 minutes. That direct instruction supplies the payload/destination authorization previously requested. Automatic approval allowed this subsequent launch. The earlier blocked attempt did not create a reviewer process or consume a reviewer call.

Exact reviewed draft remains D3-A revision1.0, SHA-256 `c0b575419e4374a71db4545e36f3569f95c15ffbf744deca3a2ff8238dec16ea`; packet141945 bytes, SHA-256 `7aa7082fcfffe14fd03ddea798292b158e4107ae5692e5d3697b4330abf547e3`. The packet retains its preparation-time proposed-budget labels; actual subsequent Owner authorization is recorded separately here and in the run authorization. Those old labels do not establish that the executed call lacked approval. The no-tool reviewer could not independently authenticate the Owner's chat.

Fixed command/runtime: `/opt/homebrew/bin/python3 -I -S -B contracts-d3-01/run-review.py`, using the exact `command-plan.json` argv and supplement working directory. CLI2.1.296, requested `opus`/medium, actual `claude-opus-5-5`, fresh session `e7c403fc-5695-4c06-bbe2-28a31de0ed26`. Authentication was freshly observed as `claude.ai / firstParty / pro`, no provider/key override; no secrets or account email were recorded. Safe/restricted mode, tools and MCP lists empty, setting sources empty, dontAsk, no-session-persistence. One natural completion in167.084s, exit0, timeout=false, process group absent,0 tool uses,0 invalid stream rows. All bound inputs/source102/controls11/prior evidence210 and tracked-diff identity passed the before/after checks. This is static review only: no runtime import, product command, test or reproduced counterexample. The earlier31/31 remains inherited evidence for the earlier selected bytes.

### Reviewer Response — Verbatim

# D3-A revision 1.0 정적 검토 (no-tool)

## 판정

- **설계 방향**: 세 경계 모두 DR-0004 및 D1-A/D2-A v2.1과 근본적으로 충돌하지 않습니다.
- **revision 1.0 문안 그대로의 수락**: 권고하지 않습니다. 아래 B1–B3 세 곳을 고친 revision 1.1이 필요합니다.
- **구현·자격검증·활성화**: 어느 것도 준비되지 않았습니다.
- **Owner 수락 여부**: 이 검토는 Owner 수락이 아닙니다. packet은 "추가 review 예산 미승인"이라고 적혀 있으므로, 7번째 호출의 승인 여부는 Driver가 별도로 기록해야 합니다.

근거 구분은 다음과 같습니다.

- **정적 추론**: 코드 관련 소견은 모두 발췌문을 읽은 결과입니다. hash 재계산, 실행, 재현은 하지 않았습니다.
- **상속된 결과**: 31/31은 exit 10 경로를 포함한 이전 bytes의 한정 증거입니다. D3-S-A에 대해서는 실행 증거가 전혀 없습니다.

## 1. D3-R-A: 과거 비교 exit 10

정합합니다.

- **DR 문구와의 관계**: DR의 "unavailable/non-pass, not successful; B1 유지; 현재 record 작업 차단 금지"를 `degraded`/10으로 구체화한 것이며, 범위를 넓히지 않습니다.
- **전역 degraded 여부**: 발췌 범위에서 이 분류는 `_entry_replay_result`의 응답에서만 생깁니다. 영속 필드가 없으므로 status/doctor로 번지지 않습니다.
- **우선순위**: 코드 순서가 문안과 일치합니다. 충돌 거부(65)와 sync가 먼저 오고 truth 비교가 그 뒤입니다.

비차단 보완점은 세 가지입니다.

1. **소비자 구분 규칙**: exit 10은 v2.1의 detach 진단에도 쓰입니다. D1-A처럼 "exit 10 단독이 아니라 `transition_content_verification` 필드로 구분한다"는 한 문장이 필요합니다.
2. **truth 일치 시 불일치 거부(65)의 의미**: 전환 뒤 publish 전의 정상적인 local 편집도 replay에서 65가 됩니다. 이는 replay 시점의 관측이며, 당시 S6 실패의 증명이 아니라고 명시해야 합니다.
3. **비교 도중 truth 변경**: 현재 코드는 이 경우 10이 아니라 65를 냅니다. 문안에는 이 경우가 없습니다.

## 2. D3-S-A: 필수 directory sync

실패 시 65, B1 전후 보존, 영속 bit 없음, T-A 유지라는 골격은 정합합니다. 완전한 receipt에서 sync만 실패한 경우는 torn이 아닌 complete-file prefix이므로 T-A를 약화하지 않습니다.

### 차단 B1: S1 전 점검이 선택 사항(may)임

- receipt는 `write_new_bytes`가 파일을 만든 **뒤에** 부모 디렉터리를 sync합니다.
- sync가 지속적으로 unavailable인 환경에서는 receipt가 남은 채 65가 됩니다. 일방향 S1을 넘었고, 재시도도 같은 지점에서 계속 실패합니다.
- 결과는 지원되는 전진 복구가 없는 고착입니다. 현재 소스에서는 조용히 완료되던 환경이 이렇게 바뀝니다.
- **최소 수정**: 이미 존재하는 관련 디렉터리의 guard 내 sync 점검을 S1 전 **필수(must)** 로 바꿉니다. 실패 시 receipt 없이 거부합니다. "디렉터리 생성 금지"와 "이후 모든 sync 결과 재확인"은 유지합니다. 정확한 경로와 구현은 계획으로 미룹니다.
- **남는 한계**: 점검 통과 뒤의 일시적 I/O 오류는 여전히 S1 이후 65가 될 수 있습니다.

### 차단 B2: Scope 문단이 실제 범위보다 좁음

- Scope는 "S4–S6 rows"라고 적었지만 D3-S-A는 receipt, candidate, release, N까지, 즉 S1–S3도 다룹니다.
- **최소 수정**: v2.1처럼 보충 대상을 정확히 열거합니다. S1–S6 행 전체와, C0-T-A가 "기존 메커니즘 유지"라고 한 receipt/staging 단계의 sync 결과 처리가 포함됩니다.
- **숨은 계약 확장의 명명**: directory sync 미지원 환경이 전환 불가가 됩니다. 이는 사실상 새 admission 제한이므로 Owner 인지 항목으로 올려야 합니다.

### 명확화 강력 권고

발췌에서 확인한 간접 경로 기준입니다.

- **재시도 시 sync 생략 지점**: 두 곳에서 "완전한 prefix는 sync 생략 근거가 아님" 조항과 현재 코드가 어긋납니다.
  - `if _exists(old)` 안의 root sync는 O가 이미 없으면 건너뜁니다.
  - `if not _exists(release)` 안의 release sync는 release가 이미 있으면 건너뜁니다.
  - 문안에 "이미 관측된 prefix의 필수 sync도 무조건 재수행"을 명시하십시오.
- **`writer_guard`의 `locks` sync**: 모든 작업이 공유하는 경로입니다. 범위 안인지 밖인지 문안에 없습니다. 범위 밖으로 명시하고 B1의 점검으로 덮는 쪽을 권고합니다.
- **결과를 버리는 helper**: `_write_exact`는 `write_new_bytes`의 `directory_fsync` 반환을 버립니다. `_durable_directory`는 sync 두 번의 결과를 모두 버립니다. direct call만 감싸서는 규칙이 구현되지 않습니다.
- **same-entry와의 공유 구간**: receipt, staging, release 단계는 same-entry update와 같은 함수 구간입니다. "same-entry 불변"을 유지하면 한 함수 안에 엄격·관대 두 동작이 생깁니다. 의도된 것임을 문안에 적으십시오.
- **replay의 재sync 집합**: exact-current replay가 다시 수행할 sync 목록이 정해져 있지 않습니다. 또한 충돌 거부가 재sync보다 먼저라는 순서를 명시하십시오.
- **뒤따른 operation이 있는 경우**: 더 새 binding이 생긴 뒤에는 옛 operation의 sync 미확인 상태를 관측할 수 없다는 한계를 적으십시오.
- **실패 단계 식별자**: 이전 R1의 약한 oracle 우려를 피하려면 메시지에 oracle ID(S1-02…B-06) 같은 안정 토큰을 넣도록 계획 요건으로 두십시오.
- **표시 한계**: B1 뒤 sync 실패는 그 호출의 출력에만 나타납니다. status/doctor는 pass를 보입니다. 또한 OSError 뒤 재시도 성공이 앞선 변경의 지속을 증명하지 않습니다.

## 3. O + binding.next 복합 거부

정합합니다.

- **DR과의 관계**: DR 표에는 O 존재와 binding staging이 함께 있는 행이 없습니다. "bounded prefix 외에는 보존·거부" 원칙과 v2.1의 "unexpected O/N combination 불인정"에 부합합니다.
- **성격**: "O가 다시 보이면 S4 재관측"이라는 기존 문장을 좁혀 읽는 것이므로 Owner의 명시적 인지가 필요합니다. 문안이 이를 요구하고 있어 적절합니다.

### 차단 B3: "nonempty `binding.next`" 정의가 모호함

- 0바이트 `binding.next`는 B-02 직후의 유효한 prefix입니다. 문언상으로는 "nonempty"가 아니어서 지원 범위로 읽힙니다.
- 현재 코드는 길이와 무관하게 member가 있으면 거부합니다(`allowed or not names`).
- **최소 수정**: "operation staging 디렉터리에 `binding.next`가 길이와 무관하게(0바이트 포함) 존재"하면 미지원으로 정의합니다. "디렉터리 부재 또는 비어 있음"만 지원 S4 재관측으로 둡니다.

### 운영 비용

- 이 상태에서는 B0, O, N, schema-2 receipt가 공존합니다. 구·신 writer가 모두 막히고 외부 복원이나 처분만 남습니다.
- D3-S-A가 발생 가능성을 줄이지만 없애지는 못합니다. sync 성공 뒤의 전원 손실이나 Git의 `hv2` 복원 같은 비협조 변경이 남습니다.
- 운영자가 수동 처분한 뒤에는 표와 일치하는 prefix를 제품이 구분하지 못합니다. N 충돌 사례와 같은 한계임을 명시하면 좋습니다.

## 4. 결론을 제한하는 미제공 의존

계약 결론 자체를 막는 것은 없습니다. 다만 다음 본문과 테스트 원문이 없어 아래 항목은 확인하지 못했습니다.

- **`_lifecycle_truth`**: truth 범위에 전환 자체의 산출물이 포함되는지 여부.
- **`_entry_absence_admission(owned_prefix=True)`**: 복구 경로에서 `_entry_transition_prefix`를 실제로 호출하는지 여부. "현재 코드가 복합 상태를 거부한다"는 Driver 진술은 여기에 달려 있습니다.
- **`_ensure_parent`, `_init_partial_tree`, `_replace_product_file`**: 내부 sync나 디렉터리 생성이 있는지 여부.
- **`_workspace_observe`**: pending을 어떻게 도출하는지.

## 5. 준비 상태 구분

| 단계 | 상태 |
| --- | --- |
| 설계 | B1–B3을 반영한 revision 1.1이면 Owner 판단에 올릴 수 있습니다. 1.0 bytes 그대로는 권고하지 않습니다. |
| 구현 | 미착수입니다. 현재 소스는 sync 반환을 무시하고(간접 helper 포함), 재시도 생략 지점이 두 곳 있습니다. |
| 자격검증 | 없습니다. unavailable/OSError, B1 전후, 재시도, 복합 상태 보존 테스트가 새로 필요합니다. 불변 oracle 개정도 별도 승인이 필요합니다. 변경된 bytes에는 31/31을 승계할 수 없습니다. |
| 활성화 | 불가합니다. 이전 R1의 B1–B5, P3/P4, C2 후속 문서, Owner 결과 수락이 모두 남아 있습니다. power-loss 지속성은 미입증입니다. |

### Driver Disposition — Separate From Reviewer And Owner

The Driver does not accept revision1.0 as final design and does not apply findings to source or DR automatically. The reviewed draft and packet remain unchanged. The following dispositions are recommendations for the next exact revision, not Owner acceptance.

| Finding | Disposition | Reason, correction and limit |
| --- | --- | --- |
| B1 optional pre-S1 sync check | accept recommendation; needs-user for admission restriction | Make the bounded under-guard check of relevant existing directories mandatory before publishing the first receipt. A persistently unsupported directory sync should be refused before S1 where observable. Keep no probe-created directories and recheck each later required sync. This mitigates a predictable one-way trap; it cannot prove later newly created directories will support sync or prevent transient post-S1 failures. It is a new environmental admission restriction to acknowledge explicitly, not a proof that every prior allowed environment was qualified. |
| B2 S4–S6 scope mismatch | accept | Name Admission And Quiescence, all S1–S6 durable rows including S3a/S3b, receipt/candidate/staging/release sync processing and Physical Publication. Explain the narrow sync-result supplement to C0-T-A while preserving its receipt/staging mechanism and torn-byte limit. This is a wording defect in revision1.0. |
| B3 nonempty binding.next ambiguity | accept | Replace file-length language with member-presence language: any binding.next member, including a zero-byte file, beside exact O is unsupported. Only absent or empty operation staging is compatible with supported S4 re-observation; unknown members and wrong types still refuse. Current `_entry_binding_stage` checks directory member names, independent of file length. |
| R-A consumer and historical meaning | accept clarification | Distinguish the historical comparison response by its operation/context and transition_content_verification field, not exit10 alone. A replay-time content mismatch is a current observation, not proof the original S6 failed. Truth changing during comparison keeps the current65 refusal and B1 preservation; do not silently remap it to10. |
| Retry sync closure and reused helpers | accept | Existing complete receipt/release/entry prefixes do not authorize skipping required sync. Driver confirmed ignored results in `_write_exact` and `_durable_directory`, conditional release sync, and root sync inside the O-exists branch. The implementation plan must enumerate direct and indirect calls plus missing-on-retry paths. No fix or fault execution occurred. |
| Guard and same-entry scope | revise toward explicit separation; needs-user | Keep the shared guard's creation/locking protocol and unrelated same-entry semantics unchanged. Specify transition-only mandatory under-guard checks, including relevant already-existing lock/root paths where required, without describing guard acquisition as zero-write. A pre-check of other directories does not prove lock-directory sync. The exact bounded path list and strict-helper plumbing must be fixed before implementation. |
| Exact-current replay sync set and precedence | accept | The next candidate/implementation map must enumerate the set and sequence, retain identity/prefix/collision refusal before sync, and cover surviving publication parents rather than guessing absent staging paths. An older operation must not certify or rewrite a newer binding as its own B1. |
| Failure diagnostics and historical visibility | accept with boundary | Require stable per-step identifiers mapped to the fixed operation oracle without silently revising that oracle. A post-B1 sync failure is per-invocation evidence; status/doctor may independently pass current product verification and that is not retrospective sync qualification. A later retry cannot prove earlier power-loss durability. No new persistent bit or global state. |
| Composite operational cost | accept; needs-user | Retaining unsupported O plus any binding.next can leave both writer generations blocked and require separately authorized external recovery/disposition. Program-visible table compliance cannot establish provenance after manual restoration. The contract should say this without granting restoration authority. |
| Omitted dependency bodies | accept reviewer limitation; revise one inferred dependency | Driver read `_lifecycle_truth`: it enumerates intents/work and planning/candidates.json, not transition product outputs. `_entry_absence_admission` does not call the prefix verifier; `_workspace_observe` calls `_entry_transition_prefix`, and `_switch_preflight` obtains that observation before recovery proceeds. Thus that particular call dependency is different from the reviewer's tentative statement. This is additional Driver static inspection, not reviewer verification or an executed counterexample. Unreviewed dependency/test bodies remain a limit. |
| Design/implementation/qualification/activation | accept | Direction is coherent, but revision1.0 requires correction. Strict D3-S-A implementation and fault qualification have not started. Existing historical-comparison code is not “all D3 implementation unstarted”; only the new strict-sync behavior is unimplemented. No Owner design/result acceptance, full P2 completion or activation follows. |

### Next Exact Owner Decision And Stop Boundary

The next bounded slice is documentation-only: prepare one D3-A revision1.1 candidate incorporating the three blockers and the above clarifications, with a short exact-delta/disposition table and an explicit replay/preflight scope. Completion means a concrete reviewable candidate, internal clause consistency and rendered Markdown checks, preserving revision1.0 and accepted DR bytes. Do not append Accepted text or begin implementation until the Owner chooses the exact resulting bytes. No second reviewer call is included; a fresh external review, if requested, needs its own finite allowance. Stop if closing the scope requires new recovery support, a persistence field, a changed physical oracle or runtime execution.

The material Owner choices are: transient historical-comparison exit10; transition-only mandatory sync with known unsupported environments refused before first receipt and possible preserved failure after S1; and unsupported O plus any binding.next (zero-byte included) with external recovery cost. Exact paths, failure identifiers and replay synchronization set still need concrete revision/implementation planning, so this record does not request acceptance of revision1.0.

Actual cumulative reviewer7/7, controller14/14 and correction1/1 are exhausted. No further calls or tests are authorized by remaining wall time. Source, controls, accepted DR and the reviewed candidate remain unchanged; only this existing task records the outcome. No STATUS, Done, Git, adopter update, P3/P4 or activation action occurred. Source and verification worktrees remain in use for the concrete D3 revision and remaining P2 scope. Durable candidate/original/failure evidence custody is unchanged; no worktree is eligible for retirement at this point.

## D3-A Revision 1.1 Candidate Prepared — 2026-10-10

The Owner explicitly requested revision1.1 incorporating the three corrections and Driver dispositions, with changes and acceptance items summarized and without code changes or additional tests. The Driver prepared two documents in the existing private supplement, leaving revision1.0, its review/packet and accepted DR bytes unchanged:

- `contracts-d3-01/amendment-draft-v1.1.md`: exact proposed amendment, SHA-256 `4ed3f202e46d5c517c0e5de725ed1d3a056715e7c812b0158895942fd23dd23b`.
- `contracts-d3-01/revision-1.1-decision.md`: Korean change/disposition summary and exact Owner decision items, SHA-256 `08ac6eefd7903bc871167f5a73f0841e50aa905908751fbc430f1cf3d59f950e`.

The candidate makes pre-S1 sync checks mandatory for the bounded existing paths under the acquired guard; names all S1–S6 rows and the retained C0-T-A receipt/staging sync handling; and defines unsupported O plus binding.next by member presence, including zero-byte files. It preserves the existing mechanism, torn-byte limit and external-recovery authority boundary. The documented preflight can reject a known unsupported environment before the first receipt, but does not guarantee support for future directories or prevent preserved failure after S1.

Driver clarifications cover exit10 consumer identity versus comparison-time65, current mismatch versus historical S6 meaning, complete-prefix retry sync, indirect helper scope, the finite exact-current replay directory roles, guard/same-entry separation, stable diagnostic/oracle mapping without changing the oracle, and later status/newer-binding/power-loss limitations. The preflight/replay sets are design requirements; exact call-site ordering, scoped wrappers/error translation and verification commands remain a separately authorized implementation plan. An older historical invocation gains no sync authority over a newer binding. No new persisted field or recovery capability is proposed.

Owner acceptance, if chosen later, must identify the revision1.1 bytes and four decision groups: historical result mapping; mandatory transition sync and environmental admission restriction; retry/replay and guard/same-entry scope; and the unsupported-composite/external-recovery cost. This request authorizes preparation, not acceptance. Revision1.1 has not had a new independent review or runtime verification; reviewer7/7, controller14/14 and correction1/1 remain exhausted and unchanged. No new reviewer or product/test execution ran. Prior31/31 remains historical selected evidence only.

Document verification: inspected revision1.1 against the recorded findings/dispositions and unchanged clauses; candidate hash matches the decision summary; GFM rendering and local links passed with no literal emphasis delimiters outside code. Checked source102, controls11 and prior evidence210 unchanged, as well as the original reviewed inputs/DR and tracked source diff. The existing task remains the sole progress owner; no STATUS, Accepted/Done, Git, installation, P3/P4 or activation change. Both checkouts remain required for the concrete design decision and remaining P2 scope; unique originals, candidates and failure evidence retain durable custody.

## D3-A Owner Acceptance And Next Plan — 2026-10-10

The Owner explicitly accepted the four D3-A revision1.1 groups and requested an append to the existing DR plus the next implementation/verification plan, without code changes or test execution. This is actual design acceptance of SHA-256 `4ed3f202e46d5c517c0e5de725ed1d3a056715e7c812b0158895942fd23dd23b`, not authorization to execute that next plan.

DR-0004 now has the named Accepted (Amended) D3-A record beginning at line279. All59,025 prior bytes remain identical, SHA-256 `f0d0d9c1376cd7eb50f2139abbf756b807666f32111d7ecdb43218c0c961429c`. The quoted accepted input reconstructs to the exact revision1.1 hash; the complete appended DR is SHA-256 `86bce9d1906b55ef31d8f8e47a0e75d7341021d3eff5a70ffac9c5597a5bf25e`. Historical proposed/header labels remain unchanged and the acceptance record explicitly supplies their current status. Revision1.0 review and revision1.1's absence of a new independent review remain correctly separated. An initial append-helper syntax error occurred before any write; readback confirmed the old DR hash before the corrected append succeeded. No product or controller invocation was involved.

The private supplement `contracts-d3-01/implementation-verification-plan.md`, SHA-256 `e626e878320cbf567e7cbf32e9d6ca5f436049041816b1b06a9b5ad16c3a75e9`, proposes two-file authoring in product.py and the existing entry-transition tests. It maps direct/indirect sync paths, preflight/publication/recovery/replay ordering, exact-current identity, shared-helper isolation and stable diagnostics to the accepted clauses. It leaves jsonio/workspace/guard, schemas and frozen controls11/oracle unchanged; inability to close scope inside those limits is a stop condition.

Verification proposal:40 new literal-method cases (15 fixed sync fault points times unavailable/EIO plus10 behavior cases) and the existing31, hence71 selected and883 total discovery anticipated, not executed or collected. The plan includes actual-prefix/byte/mode/diagnostic assertions and states the limits of instrumented evidence. Frozen base/control evidence remains historical; a proposed new execution root at `/Users/kyungseo/dev-home/agent-worktrees/hv2-reference-private-colvia-d3-verification-20261010-b03` needs its own actual acquisition/canary/base collection/smoke prerequisites, followed by entry collection/focused. No root was created. Registered worktrees and destination absence were inspected. The retained baseline source copy is a named future consumer for that new boundary.

Proposed execution allowance is6 controller calls with3,600s total plus2 Claude no-tool calls with3,600s total, no correction/retry. A separately approved new150-minute wall window would begin at R0, with exact UTC deadline and per-step remaining-budget gates. The earlier20:00:28 KST deadline and consumed7/7 review,14/14 controller,1/1 correction budgets are not extended or reused by this plan. The first recommended approval is authoring/static preparation only; fixed candidate/IDs/call-site map/new invocation bytes and explicit private-packet external-transfer scope must precede execution approval. No reviewer/test/runtime import/discovery ran in this turn.

Verification of this documentation result: GFM rendering and links/identifiers/budget arithmetic checked; exact accepted-input reconstruction and old-DR-prefix preservation passed; source102, controls11 and prior evidence210 plus unchanged reviewed inputs other than the authorized DR append passed. Source tracked diff remained identical. Existing task remains the only progress owner. STATUS/roadmap update is not needed: this refines the in-progress private transition's contract and does not change Toolstead's current phase or global direction. The D3 slice supplements the existing P2 plan; C2 successor documentation remains future activation work. Full P2, P3/P4, complete suites/artifact qualification, result acceptance, deployment and Git actions remain open and unperformed. Source/verification/baseline-copy boundaries retain concrete near-term consumers and required durable custody, so no checkout is retired.


## D3 Two-File Authoring And Static Freeze — 2026-10-10

Owner actual request: “첫 승인 단위부터 진행하자. product.py와 기존 전환 테스트 파일을 작성하고 정적 확인까지 수행해줘. 테스트나 Claude 검토는 실행하지 말고, 후보와 실행 입력을 고정한 뒤 변경 내용과 검증 계획을 보고해줘.”

승인 범위의 authoring을 완료했다. `src/hv2ref/product.py`와 기존 `tests/test_entry_window_transition.py`만 source map에서 바꿨고, 기존 two-file bytes와 후보는 아래 durable preparation 경로에 보존했다. 전환 전용 mandatory directory sync·under-guard admission·complete-prefix retry·exact-current replay를 구현 후보에 연결했다. 일반 same-entry 경로와 shared guard/jsonio/workspace, fixed controls/oracle은 변경하지 않았다. Composite 거부와 historical truth10/비교 중 drift65는 기존 의미를 유지한다.

- 결과 보고: `/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-01/REPORT.md`.
- 정적 call-site/path/token/oracle map: `/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-01/call-site-map.md`.
- Input identity: `/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-01/input-identity.json`, source102 digest `d8cb4ca0e379ec63631f956638f56f117c8d8d1a1c221d24ecbaaf8e5ce37e9e`. Product SHA-256 `7c5797f7bdfb1ed3ccde0506f90a470ee7bd9526048b8d0be093569e2bb7cdae`, test SHA-256 `35209043f38e221b9b3d1a289ed5cc6903b95f87ffdfdfbe66c75dfeb5222bc0`.
- 신규40 literal methods와 기존31 선택을 합한71개를 고정했다. Syntax/AST와 patch 적용 가능성을 확인했고, 기존 method/helper·control/old-fixture/foundation·factory/timeout AST는 유지됐다. 실제 discovery가 아니며883은 예상 occurrence 수다. 기존 default 중복177개를 보존하고 선택71개는 각각1회를 요구한다.
- Runtime/Git/system-config·base source101·controls11·accepted DR·이전 증거210개는 bytes/mode 또는 해당 고정 hash로 확인했다. `.idea` 내부는 읽지 않았다. Product/test import, discovery, 테스트, Claude 호출, 새 실행 root 생성은0회다.
- `/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-01/execution-plan.json`에 새 root b03와6개 controller argv, input hashes, 환경/timeout/output, R0/R1 검토 argv를 고정했다. Collection은 AST·이전 수집에서 계산한 예상 identity이며 actual result가 아니다. 다음 실제 수집의 전체 bytes/IDs/occurrences/기존 duplicates가 일치할 때만 미리 고정한 smoke/focused 입력을 사용한다. 불일치는 STOP이다.

다음 제안은 별도 Owner 실행·private code/DR/test/result 외부 전송 승인 후 R0→6controller→R1, controller3,600초+review3,600초·새150분 창이다. 이전20:00:28 KST 마감과 소진14controller/7review/1correction은 그대로다. 새 실행 retry/correction은0회다. 이 기록은 그 예산 승인이나 실제 결과 수락이 아니다. R1 packet과 실제 model/session은 실행 결과가 생긴 뒤 기록한다.

D3 runtime qualification, 전체P2, P3/P4, C2 활성화, 실제 adopter/Git lifecycle은 미완료다. 새 Work/STATUS cascade는 없다. Source/baseline/기존 실행 경계는 후속 P2/D3 검토·미해결 증거 소비자로 유지한다. 후보/전후 bytes/고정 입력은 요청된 다음 검토·실행 소비가 끝난 뒤 보존 규칙에 따라 재평가한다.


## D3 Execution Approval And R0 Stop — 2026-10-10

Owner actual request: “제안한 R0 검토 → 6단계 실행 → R1 검토를 승인해. 고정한 private 코드·DR·테스트·결과의 Claude 전송도 승인하니 최대 150분, 자동 재시도 0회로 진행하고 실패나 입력 불일치가 나오면 보존한 뒤 멈춰서 보고해줘.”

승인대로 R0 한 번만 실행했다. 기존 구독 `claude.ai / firstParty / pro`, CLI2.1.296, 실제 model `claude-opus-5-5`, session `0cf3ab1e-198a-4408-8981-834b7ca0f74c`, no-tools/no-MCP·tool use0, exit0, 471.695초, timeout 없음, process group 부재와 입력 전후 일치를 확인했다. R0 시작 `2026-10-10T10:30:20.925768+00:00`, 고정 deadline `2026-10-10T13:00:20.925768+00:00`. 예산은 최대150분·retry0였으며 차단 뒤 잔여 slot을 사용하지 않는다.

고정 패킷 SHA-256 `6b63a0796efca72dec328eba5d4e5249c7fbae35d3b03faba5e5fe48b18bc5aa`, source102 digest `d8cb4ca0e379ec63631f956638f56f117c8d8d1a1c221d24ecbaaf8e5ce37e9e`. Exact source/tests/DR의 identity는 기존 `/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-01/input-identity.json` 그대로다. 추가 read-only source 확인의 path/hash와 처분은 `/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-01/execution-01/r0-static-disposition-checks.json` 및 `/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-01/execution-01/r0-disposition.json`이다. 새로운 product/test/controls 변경은 없다.

### Reviewer Response — Verbatim

# D3-A R0 정적 검토 결과

**결론: 실행 전 확인이 필요한 조건부 차단 3건(B1~B3)이 있습니다. 코드 추적에서 "반드시 실패한다"고 확정된 결함은 찾지 못했습니다.**

도구 호출, 실행, import는 하지 않았고 패킷 본문만 읽었습니다. 아래는 모두 정적 추론이며 D3 런타임 결과는 없습니다. 검토 모델은 claude-opus-5-5입니다.

## 1. 차단 항목

### B1. 고정 child의 CLI 호출 계약을 패킷만으로 확인할 수 없음

- **위치:** `D3_SYNC_PROGRAM`의 `args = ['d3-fixed-cli', '--source-checkout', 'update', ...]`와 `cli.main()` 직접 호출.
- **근거:** `cli.parser()`, launcher `colvia`, `observer.py`의 `new-source` 호출 방식이 패킷에 없습니다. 기존 31개는 observer를 거치는데, D3 child는 `cli.main()`을 in-process로 직접 부릅니다. `--source-checkout`을 launcher나 observer가 소비하고 `parser()`가 받지 않는 구조라면 argparse가 `SystemExit(2)`를 냅니다.
- **실패 양상:** stderr는 `StringIO`로 리다이렉트된 채 버려지고 stdout은 비어, `d3_run`의 `json.loads(data)`가 원인 불명 오류로 끝납니다. 신규 40개 전부가 해당하며, 재시도 0회 예산에서 불투명한 증거만 남기고 STOP합니다.
- **최소 조치:** Driver가 실행 없이 `cli.parser()`의 `--source-checkout` 정의와 observer `new-source` 경로를 읽어 R0 처분에 기록합니다. parser가 받으면 코드 변경은 필요 없습니다. 받지 않으면 해당 인자를 제거해야 하고, 이는 새 후보·새 hash입니다.
- **부수 사항:** REPORT의 "실제 CLI 호출"은 `cli.main` in-process 호출이지 launcher 경유가 아닙니다. 표현을 한정하십시오.

### B2. DR이 요구한 "complete-prefix retry" 결함 주입이 없음

- **위치:** `test_d3_complete_prefix_retry_resynchronizes`와 child `matches()`.
- **근거:** D3-A 수락 문안은 fault 검증이 unavailable, OSError, pre-S1, post-S1/pre-B1, post-B1, complete-prefix retry, exact-current replay를 구분하도록 요구합니다. retry 테스트는 성공 경로의 sync 발생만 관측합니다.
- **결과:** 다음은 한 번도 assert되지 않습니다.
  - `d3-sync:recovery:*` 토큰 전체
  - 복구 호출에서 다시 실행되는 `admission` 단계
  - `_entry_resync_release` 실패 시 65
- **구조적 한계:** 현재 selector로는 이 지점을 겨냥할 수 없습니다. 예를 들어 `release_parent`는 `new_mode is None`을 요구해 after-launcher prefix에서 매칭되지 않습니다.
- **최소 조치(택1):**
  - (a) recovery 전용 selector 1개와 unavailable/oserror 2개 메서드를 추가합니다. 새 후보이며 73 ID, 입력·예상 hash 재고정이 필요합니다.
  - (b) 71개를 유지하되 "retry 중 sync 실패→65는 정적 추론만"임을 R0 처분, R1 패킷, Owner 보고에 명시합니다.
- **판단 주체:** 문안 대비 미충족이므로 (b)로 진행할지는 Owner가 정할 사항입니다.

### B3. 예상 collection 근거가 패킷에 없고 내역 표기가 소스와 다름

- **위치:** "Collection Expectation Limits" 절과 `static-checks.json`.
- **불일치:** 패킷은 factory 107을 "control/old-fixture 20 + product 71 + foundation 16"으로 적었습니다. 소스를 세면 EntryControlTests 24 + OldFixtureTests 1 = 25, EntryProductTests 71, EntryFoundationTests 11입니다. 합계 107과 기존 67(25+31+11)은 맞습니다.
- **검증 불가 항목:** 다음 파일 본문이 패킷에 없어 세 hash와 ordered ID를 확인할 수 없습니다.
  - `collection-expectation.json` (`fcd0806b…`)
  - `base-smoke-proposed-input.json` (`53b012b9…`)
  - `entry-focused-proposed-input.json` (`f8d0ec19…`)
- **최소 조치:** Driver가 예상 `factory_ids`가 Control→OldFixture→Product→Foundation 순서, 클래스 내 메서드명 알파벳순, 25/71/11 구성인지 정적으로 대조하고 산문 표기를 정정합니다. 순서가 틀려도 collect 단계에서 안전하게 STOP하지만 실행 창은 소모됩니다.
- **부수 사항:** `existing_methods_preserved: 40`은 의미가 모호합니다. 테스트 31 + helper 9로 추정되므로 라벨을 명확히 하십시오.

## 2. 정적 추적으로 일치를 확인한 항목

### 전환 전용 범위와 간접 helper

- `transition = bool(plan["remove"])` 분기 밖의 `_durable_directory`, `_write_exact`, `sync_directory(release.parent/operation)`, `_replace_product_file` 호출 순서는 기존과 같습니다.
- `_entry_write_exact`는 `_ensure_parent`의 숨은 mkdir/sync를 제거했고, 파일 recipe(xb, flush, `_sync_fd`, 기존 bytes 비교+fsync)를 유지합니다.
- 전환 경로에 남은 비엄격 directory sync는 `writer_guard`의 locks 하나뿐이며, DR이 명시적으로 제외한 범위입니다.

### Admission

- under-guard preflight와 `_visible_truth` 뒤, 첫 receipt 전에 실행됩니다.
- 순서는 target→home→product→receipts→releases→locks→(존재 시) staging입니다.
- `_entry_sync_paths`가 모든 검증을 마친 뒤에 probe를 시작하며 디렉터리를 만들지 않습니다.

### Prefix recovery

- 완성된 release는 `_entry_resync_release`가 다시 sync합니다.
- 기존 receipt, N, 부재한 O, 기존 staging/binding 디렉터리 모두 무조건 재-sync됩니다.
- 기존 31개와의 상호작용도 추적했습니다. 이들의 기대 메시지와 보존은 유지되는 것으로 읽힙니다.
  - staging tear: admission의 `_init_partial_tree`가 같은 메시지를 냅니다.
  - prefix 01~09, S4 재관측, late collision, `fsync-after` receipt kill 지점.

### Replay 집합과 순서

- 거부(product/prefix/collision) → `_entry_sync_paths(replay=True)` 검증 → N/B1 file sync → 깊이 내림차순·UTF-8 순 directory sync → 제품 재관측 → truth 비교 순입니다.
- `binding_ref.id != operation_id`이면 sync에 진입하지 않습니다.
- 테스트 oracle `d3_replay_paths`의 집합과 정렬 키가 제품과 일치합니다.

### B1 오류 보존

- B1 replace 뒤 두 sync와 replay는 `b1=True`입니다.
- 실패 시 `verify_workspace_product`는 read-only이므로 `rows[index+1:] == []` 단언과 충돌하지 않습니다.
- B1 mode 0600과 빈 entry-op 조건에서 `verified`가 나오는 것으로 읽힙니다.

### Composite

- 0바이트와 complete `binding.next` 모두 guard 전 preflight의 `_entry_binding_stage(allowed=False)`에서 거부됩니다. 메시지가 정확히 일치하고 `rows == []`입니다.
- 이 두 테스트는 D3 이전 코드에서도 통과할 기존 거부의 보존 증거입니다. 신규 로직의 증거로 보고하지 마십시오.

### Selector 15×2

- 각 selector의 occurrence 1이 의도한 호출과 일치함을 호출 순서로 확인했습니다. role은 `selector.replace('_','-')`, phase는 `publication`(admission 2종 제외)입니다.
- `staged/'.'` 재확인 sync는 occurrence 2 이상으로 밀려 간섭하지 않습니다.
- 오류 문자열 `unavailable:22`, `oserror:5`도 일치합니다.

### 71-ID 선택

- 기존 31 + 신규 40(fault 30 + 기타 10) = 71이며, 소스의 `EntryProductTests` 메서드 71개와 1:1입니다. 중복 def는 없습니다.
- `factory_members`가 default ID와의 겹침을 금지하므로 default 쪽 중복 177은 선택에 유입되지 않습니다.

### 6-controller 경계

- `allowed()`가 base의 acquire/canary/collect/smoke와 entry의 `collect-p2`, `focused-p2`를 허용합니다.
- `completed()` 체인(acquire→canary→smoke-base)의 controls/runtime/git 동일성 조건을 두 입력이 충족합니다.
- `require_new_collection`은 phase와 digest가 달라 통과합니다. ancestor는 9개로 맞습니다.
- 예산 합은 300×3 + 1200 + 300 + 1200 = 3,600초입니다. 전체 창은 3,600 + 3,600 + 180 + 1,620 = 9,000초로 맞습니다.
- focused의 실효 상한은 controller가 budget−20초에서 끊으므로 약 1,180초입니다.

## 3. 비차단 지적

| # | 위치 | 내용 | 권고 |
|---|---|---|---|
| N1 | `_entry_sync_admission` | 복구 호출(receipt 존재)에서도 토큰이 `admission`입니다. call-map의 "첫 receipt 전" 설명과 다르고, 같은 release 디렉터리를 admission과 recovery로 두 번 sync합니다. | call-map에 명시 |
| N2 | `_entry_sync_paths`, `_entry_resync_release` | `_require_kind`와 `iterdir`의 raw `OSError`는 `_entry_sync` 범위 밖이라 exit 70이 됩니다. 비협조 경쟁에서만 발생합니다. | 한계 기록 |
| N3 | `test_d3_same_entry_scope_unchanged` | jsonio receipt-parent 1지점만 주입합니다. product-alias 비전환 sync와 `_replace_product_file`은 정적 동일성만 있고, 비교 대상도 신 코드끼리입니다. | "정적 근거"로 표기 |
| N4 | 커버리지 | 다음이 미검증입니다: `verification=unavailable` 분기, `staging-directory-*`와 `switch-directory-*` role, `release-directory` 외 replay role. | R1 한계에 포함 |
| N5 | `d3_fault` | 실패 후 정확한 retry의 성공을 확인하지 않습니다. 13개 지점 모두 정적으로는 복구 가능해 보입니다. | 한계 기록 |
| N6 | `change_truth` | `.hrn/intents`가 OLD fixture에 존재하고 `_record_tree`가 identity+drafts 형태를 수용한다고 가정합니다. `work.py`가 패킷에 없어 확인 불가이며, 틀리면 exit 70이나 다른 메시지가 납니다. | B1과 함께 정적 확인 |
| N7 | role 명칭 | 같은 payload 디렉터리가 replay/admission에서는 `release-member-directory`, recovery에서는 `release-directory`입니다. | 토큰 표에 다대일 명시 |
| N8 | 시간 | 신규 40개 실측이 없습니다. 기존 평균(31개 248초)으로 추정하면 총 500~600초 안팎이지만 보장이 아닙니다. | 계획의 STOP 규칙 유지 |
| N9 | `_entry_append_file` | `target`이 필수 kw-only로 추가됐습니다. 패킷 범위의 호출자는 2곳뿐이나 다른 테스트 파일의 직접 호출 여부는 확인할 수 없습니다. | grep 수준 정적 확인 |

## 4. 증거 구분

- **정적 근거(본 검토와 `static-checks.json`):** 구문·AST 범위, 호출 순서 추적, selector와 토큰 일치, controller 전제조건, 산술.
- **역사적 런타임(재사용 불가):** focused 31/31과 247.994초는 digest `18c2b62e…`, factory `6bb13778…`의 결과이며 현재 bytes를 qualify하지 않습니다.
- **런타임 미확보:** D3 동작 전체, 71 선택의 실제 수집과 통과, 883 discovery, 예상 collection hash, sandbox 내 directory fsync 동작, 소요 시간.
- **범위 밖(변동 없음):** 전원 손실 지속성, fullfsync, full 19-prefix, four-executor.

본 검토는 Owner 수락이나 실행 승인이 아닙니다. B1~B3의 처분은 Driver가 기록하고, B2의 (b) 선택 여부는 Owner 권한입니다.

### Driver Disposition And Stop

B1 accept: parser()에 --source-checkout 옵션이 없고 launcher가 제거하는 인자임을 확인했다. 새 child의 in-process cli.main 호출은 이를 그대로 전달하므로 argparse SystemExit(2)가 정적으로 예상된다. 재현 실행은 하지 않았다. B2 accept: 완성 prefix의 retry test는 성공만 관측하고 unavailable/EIO→65 검증이 없다. 두 건을 blocking으로 유지하고 중단한다. B3 revise: 패킷 산문의20+71+16은 오류이며 실제25+71+11=107이다. AST/고정 factory 순서 및 proposed 입력 차이는 일치했다. 원 패킷은 수정하지 않고 이 처분으로 정정한다.

N1/N2/N3/N4/N5/N7/N8은 설명·미검증 한계로 accept했다. Recovery에도 admission phase가 실행되며, topology read 오류는 directory-sync catch 밖이다. Same-entry test는 신 후보끼리 jsonio receipt parent1지점만 비교하고, verification=unavailable·기타 role/path·fault 후 실제 retry는 미검증이다. Recovery release-directory token은 inventory descendant에도 쓰인다. 신규 시간 추정은 실측이 아니다. N6/N9는 defend(static): OLD bootstrap이 intents를 만들고 _record_tree가 identity+drafts를 허용한다. src/tests의 _entry_append_file 호출자는2곳이며 target keyword를 전달한다. 모든 Driver 처분은 테스트 실행이나 Owner 결과 수락을 뜻하지 않는다.

결과: R0 1회, controller0/6, R1 0/1, retry0, discovery/test0, new execution root0. 누적 reviewer8/controller14/기존correction1. Source102/base101/controls11·기존 증거210개·review 입력 bytes를 보존했다. `/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-01/execution-01/STOP-REPORT.md`가 사람이 읽는 결과다. 다음 제안은 별도 승인 뒤 test child 인자/진단 보정·retry fault2개 추가·73 ID/새입력 고정의 authoring이며 지금은 실행하지 않았다. 새 실행은 새 후보와 예산의 명시적 승인 뒤에만 제안한다. 기존150분 승인을 자동 재시도로 사용하지 않는다.

진행 Work와 STATUS는 그대로다. Source/base/이전 실행 경계와 이번 frozen candidate/review는 B1/B2 처분과 다음 후보 비교에 필요해 유지한다. Reviewer raw stream은 해당 unresolved review-boundary 확인의 소비자가 끝나면 ordinary record 규칙에 따라 재평가하며 영구 tracked deliverable로 승격하지 않는다. Full P2/P3/P4·C2 활성화·실제 adopter/제품 결과 수락은 미완료다.


## D3 R0 Findings Authoring Correction — 2026-10-10

Owner actual request: “ㄱㄱ”. 직전 제안인 child 인자/진단 보정, complete-prefix retry fault2개 추가,73개 선택 ID와 새 입력 고정의 authoring만 승인한 것으로 적용했다. 별도 실행/Claude 전송 승인은 받지 않았으며 이전 R0 stop과 원래 실행 창은 그대로다.

### Driver Implementation And Evidence

B1 accept 구현: 고정 child의 direct cli.main argv에서 launcher 전용 --source-checkout을 제거했다. SystemExit와 빈/잘못된/non-object JSON은 원래 stdout/stderr/CLI 종료 코드를 diagnostic envelope에 남긴다. d3_run은 diagnostic을 먼저 거부하므로 뜻밖의 오류를 expected65로 통과시키지 않는다. Source parser와 launcher를 정적으로 대조했으며 runtime 재현/해결 통과를 주장하지 않는다.

B2 accept 구현: test_d3_complete_prefix_retry_sync_unavailable과 test_d3_complete_prefix_retry_sync_oserror를 추가했다. after-launcher로 만든 S5/B0에서 새 entry0755·old 부재·exact release/receipt·빈 switch operation과 binding-stage 부재를 확인한다. 고정 recovery_release selector는 admission receipt → admission release → recovery receipt → recovery release 순서를 path/state/occurrence로 구별한다. 오류 이후 CLI65·d3-sync:recovery:release-directory·B1 no, 전체 snapshot 동일성, 후속 sync/publication 부재를 요구한다. 주입 도달·실제 exit/보존·실패 뒤 추가 retry는 실행하지 않았다.

B3 revise 구현: 새 packet에는 control24+old-fixture1+product73+foundation11=factory109, default776+factory109=885라고 적고 전체 collection expectation과 네 invocation 파일을 포함했다. 과거 packet의20+71+16 오류는 원본을 바꾸지 않고 이전 처분과 새 보완으로 정정한다. 기존 R0 원문과 N1–N9 Driver 처분을 새 packet에 그대로 포함했다.

승인한 변경은 tests/test_entry_window_transition.py 한 파일이다. 기존71개 test method 본문, 그 이전31개 test/helpers, control/old-fixture/foundation 클래스·factory 구조·timeout 및 product/shared controls는 AST와 hash로 유지됐다. Static command `/opt/homebrew/bin/python3 -I -S -B /private/tmp/check-d3-r0-fixes.py`, Python3.14.7, exit0. `compile()`/AST만 실행했으며 product/test import0·discovery0·test0·reviewer0이다. 반영 전 git apply --check --whitespace=error-all과 반영 뒤 git diff --check exit0. 테스트 pass/fail 수는 unavailable이다.

### Fixed Input And Next Proposal

Git base `238514686078ce1564010a7b69013f48a635c57c`, source digest `cc1455f6fe756d3eedab8a96301119f7a8223b07d8c781fc7a6b094ca3f01833`, 전체 tracked-base diff SHA-256 `c3c0a89c3c641e17e3376edbc09950cd1e923a67ac3063e01a038dc6c2fe8b66`. Untracked 테스트는 Git diff 외 full candidate/source map으로 고정했다. 테스트 SHA-256 `ff4bc8828a61db3633ec45c73bcd05d9607ac8bffc8e88ff8544ff78cbef8c74`, product unchanged `7c5797f7bdfb1ed3ccde0506f90a470ee7bd9526048b8d0be093569e2bb7cdae`. Packet bytes `942972`, SHA-256 `e784c84f711fe25b21cc545d7b638fb888b3997bc9e25b36f1e6371f028f9c79`. Inputs/commands/selection/collection의 정확한 경로와 hashes는 `/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-02/input-identity.json`, `/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-02/review-inputs.json`, `/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-02/execution-plan.json`에 있다. 사람이 읽는 결과는 [보완 보고서](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-02/REPORT.md)다.

Base101/entry102/controls11/runtime/Git/system-config·이전 evidence210개와 authoring-01 전체 기록을 확인했다. 새 expected collection885는 정적 예상이며 실제 수집값이 아니다. 차후 collect가 frozen bytes/ordered ID/occurrence/duplicates와 정확히 같을 때만 smoke/focused 입력을 사용할 수 있다. 불일치 시 STOP, 자동 재고정 금지다.

다음은 별도 승인 대상인 새 R0→6controller→R1: 최대150분, controller6회3,600초·review2회각1,800초, retry0. 이전 stop의 잔여 시간/호출을 쓰지 않는다. 현재 누적 reviewer8/controller14/correction1이며 제안 누적 최대10/20이다. Private 코드·DR·테스트·결과의 Claude 전송도 별도 승인 대상으로 남겼다. 새 root는 부재·미등록이며 생성0, 새 R0/R1 호출0, controller0, auth CLI0. 예산·중단·runtime/환경/출력 경계는 실행 제안에 고정했다.

기존 Work만 갱신하고 STATUS·commit·push는 변경하지 않는다. Full P2/P3/P4·C2 활성화·실제 adopter·제품 결과 수락은 미완료다. Source/base/이전 실행 경계는 다음 P2/D3 검토와 미해결 실패 증거에 필요해 유지한다. 새 테스트 전후 bytes·고정 packet은 Owner/후속 R0와 reversal custody용 durable 경로에 보존했으며 해당 의존성 종료 후 중복 보존을 재평가한다. 새 실행 환경은 생성하지 않았다.


## D3 Corrected Candidate Authorized Execution And Reviews — 2026-10-10

### Actual Owner Scope And Input

Owner actual request: “새 후보의 R0 → 6단계 실행 → R1과 private 자료의 Claude 전송을 승인해. 최대 150분, 자동 재시도 0회로 진행하고 실패나 입력 불일치가 나오면 보존한 뒤 멈춰서 보고해줘.”. Authoring-02의 고정 후보·private 코드/DR/테스트/결과 전송·R0→6controller→R1을 승인한 범위로 실행했다. 최대150분·retry0·첫 실패/입력 불일치 STOP, 새로운 보정이나 자동 재시도는 허용하지 않았다. Source 변경0, 실제 retry0, 전체P2/제품 결과의 Owner 수락은 아직 없다.

Git base `238514686078ce1564010a7b69013f48a635c57c`, 전체 tracked diff SHA-256 `c3c0a89c3c641e17e3376edbc09950cd1e923a67ac3063e01a038dc6c2fe8b66`, source102 digest `cc1455f6fe756d3eedab8a96301119f7a8223b07d8c781fc7a6b094ca3f01833`. Untracked test full bytes는 기존 authoring-02 input-identity/source-map/candidate로 고정했다. R0 packet SHA-256 `e784c84f711fe25b21cc545d7b638fb888b3997bc9e25b36f1e6371f028f9c79`, R1 actual packet SHA-256 `5fd9339d1eb816c621da90044b30b6250b3dd1e9acf052bf89e1d2608398e828`. 정확한 입력/출력 목록과 hashes는 `/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-02/review-inputs.json`, `/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-02/review-r1-inputs.json`이다.

Actual authorization `/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-02/execution-01/authorization.json`, window `/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-02/execution-01/window.json`. Start `2026-10-10T10:53:00.634253+00:00`, deadline `2026-10-10T13:23:00.634253+00:00`. Original11:00:28Z와 이전 stop13:00:20Z는 별도 역사적 마감이며 새 창의 권한/마감으로 재사용하지 않았다. Frozen authoring plan의 당시 미승인 표시는 바꾸지 않고 실제 승인과 창을 이 기록에 분리했다.

R0/R1 모두 Claude Code2.1.296, 구독 authMethod claude.ai / apiProvider firstParty / subscriptionType pro, opus/medium 요청, fresh session·no-tools/no-MCP·tool use0, 각max1,800초였다. 실제 model `claude-opus-5-5` / `claude-opus-5-5`, session `a22df087-c14d-4699-8364-36a8648fef51` / `5521e602-7db5-4ec4-a99e-70ea0d6c826d`. 실행된 정확한 argv와 cwd는 각 review-r0/review-r1 authorization.json에, 실제 exit/time/boundary는 meta.json에 기록했다. 두 검토 exit0, 각313.733/85.347초, timeout없음, group부재/입력전후 동일성PASS. Reviewer 정적 판단은 실행 허가·Owner 수락이 아니다.

### R0 Reviewer Response — Verbatim

# D3 보정 후보 R0 정적 검토 결과

**결론: 확정 차단 항목은 찾지 못했습니다. 이전 B1·B2·B3는 정적으로 해소된 것으로 읽힙니다.**

도구·실행·import 없이 패킷 본문만 읽었고, 아래는 모두 정적 추론입니다. D3 런타임 결과는 없으며, 이 검토는 실행 승인이나 Owner 수락이 아닙니다. 검토 모델은 claude-opus-5-5입니다.

## 1. 이전 차단 항목 재확인

### B1 — child CLI 인자: 해소
- **위치:** `D3_SYNC_PROGRAM`의 `args`, `cli.parser()`, launcher `colvia`.
- **근거:** launcher가 `--source-checkout`을 `del sys.argv[1]`로 소비하고, `parser()`에는 그 인자가 없습니다. 보정된 argv의 인자는 모두 `update` subparser에 정의돼 있습니다.
- **호출 경로:** `main()` → `run()` → `_workspace_switch(installed=False)`로 이어집니다. stdin 대체물은 `.buffer`를 제공하고, 확인 토큰은 JSON 왕복 뒤에도 같은 canonical bytes에서 나옵니다.
- **진단:** `SystemExit`·비JSON·비객체 출력이 envelope에 남고, `d3_run`이 exit 비교보다 먼저 `diagnostic is None`을 요구합니다. argparse 실패가 기대 65로 계산될 경로는 없습니다.

### B2 — complete-prefix 재시도 fault: 해소 (한계 있음)
- **위치:** `matches()`의 `recovery_release`, `d3_complete_prefix_retry_fault`, `_entry_resync_release`.
- **호출 순서 (after-launcher prefix 기준):**
  1. admission이 receipts, 이어서 release를 sync합니다.
  2. 기존 receipt의 `_entry_write_exact`가 receipts를 두 번째로 sync합니다.
  3. `_entry_resync_release`가 깊이 내림차순으로 release 하위 디렉터리 6개를 sync합니다.
  4. release 루트 sync에서 주입됩니다.
- **selector 조건:** 주입 시점에 release 1회, receipts 2회, 순서, `s == initial_facts`가 모두 성립합니다.
- **기대값 일치:** 토큰 `d3-sync:recovery:release-directory`, `unavailable:22`/`oserror:5`, `B1 publication observed=no; current product verification=not-requested`, 이후 sync 부재, snapshot 동일 단언이 제품 코드와 맞습니다.
- **기존 40개 간섭 없음:** dict가 매번 평가되지만 `and` 단락으로 빈 `max()`에 도달하지 않습니다. 성공 재시도 테스트에서는 hit만 기록되고 주입은 없습니다.

### B3 — 개수와 입력: 해소
- **factory:** 소스 메서드와 예상 `factory_ids`를 대조했습니다. Control 24 + OldFixture 1 + Product 73 + Foundation 11 = 109이고, 클래스 순서와 알파벳순이 맞습니다.
- **선택 73:** 기존 31 + 이전 D3 40 + 신규 2이며 소스의 `EntryProductTests` 메서드와 1:1입니다. 중복은 없습니다.
- **입력 결속:** 네 입력의 hash가 실행 계획 argv와 일치합니다. `collection_sha256`도 base `31838e46…`, entry `86d3faaf…`로 예상 파일과 일치합니다.
- **확인하지 못한 것:** default 776은 하나씩 세지 않았고 843−67 산술에 의존합니다. SHA-256 값은 어느 것도 재계산하지 못했습니다.

## 2. 그 밖에 정적으로 확인한 항목

- **전환 전용 범위:** `transition = bool(plan["remove"])` 분기 밖의 same-entry 경로는 기존 helper를 그대로 씁니다. 전환 경로의 비엄격 sync는 `writer_guard`의 locks뿐이며 DR이 제외한 범위입니다.
- **Replay와 B1:** 거부 → 경로 검증 → N/B1 file sync → 깊이 내림차순 directory sync → 재관측 → truth 비교 순입니다. 더 새 binding이면 sync에 진입하지 않습니다. B1 뒤 실패 시 재검증은 read-only입니다.
- **Composite:** 0바이트와 complete `binding.next` 모두 guard 전 preflight에서 거부되고 `rows == []`입니다.
- **6-controller 경계:** `allowed()`가 여섯 mode/slot을 모두 허용합니다. `completed()` 체인의 controls·runtime·git 동일성도 두 입력이 충족합니다. ancestor는 9개입니다.
- **예산:** controller 300×3 + 1,200 + 300 + 1,200 = 3,600초, 외곽 대기 3,780초, 전체 9,000초로 맞습니다. 누적 상한 reviewer 10·controller 20도 맞습니다.

## 3. 비차단 지적

| # | 위치 | 내용 | 권고 |
|---|---|---|---|
| N10 | `recovery_release` | 주입 지점은 recovery 단계의 7번째 sync입니다. 앞선 하위 디렉터리 6개도 같은 토큰을 쓰지만 테스트는 그 구간을 단언하지 않습니다. | R1 한계에 기록. 단언 추가는 새 후보이므로 지금 바꾸지 않음 |
| N11 | recovery 커버리지 | DR이 명시한 "O 부재 시 root 재-sync"와 recovery의 `release-parent`·`release-operation-parent`·`new-entry-parent`는 성공 경로 관측만 있고 fault는 없습니다. | Owner 보고에 명시 |
| N12 | `static-checks.json` | `prior71_test_bodies_unchanged: true`는 맞지만 공용 child가 바뀌어 기존 D3 40개도 처음 실행되는 bytes입니다. | 표현 한정 |
| N13 | `d3_run` | `json.loads(bytes)`의 `UnicodeDecodeError`는 잡지 않습니다. 실패는 하되 메시지가 덜 친절합니다. | 변경 불필요 |
| N14 | `static-checks.json` command | 정적 검사 스크립트 `/private/tmp/check-d3-r0-fixes.py`의 bytes와 hash가 보존 목록에 없습니다. | 사본과 hash 기록 |
| N15 | `execution-plan.json` | 패킷은 "실행·외부 검토 미승인" 상태로 고정돼 있습니다. `original_deadline_utc`(11:00:28Z)와 이전 창 마감(13:00:20Z)도 다릅니다. | 이번 R0의 실제 승인·시작 시각·새 마감을 처분에 기록 |
| N16 | entry `source_root_entries` | `.git`, `.idea`까지 정확히 일치해야 합니다. 루트에 항목 하나만 생겨도 collect에서 STOP입니다. | 실행 직전 재확인 |
| N17 | 패킷 범위 | `work.py`, `observer.py`, `canary.py`, `acquire.py`가 없고 `jsonio`·`workspace`는 발췌입니다. 이전 N6(`_record_tree` 가정)는 여전히 확인 불가입니다. | 한계 유지 |

이전 N1~N9 처분은 제품 bytes가 같으므로 그대로 유효합니다.

## 4. 증거 구분

- **정적 근거:** 본 검토의 호출 순서 추적, selector·토큰 대조, ID·순서 대조, controller 전제조건, 산술. `static-checks.json`의 AST 결과.
- **역사적 런타임(재사용 불가):** focused 31/31, 247.994초는 digest `18c2b62e…`의 결과이며 현재 후보를 qualify하지 않습니다.
- **런타임 미확보:**
  - child dispatch 성공과 fault 도달
  - exit 65와 보존 결과
  - sandbox 안 directory fsync의 `pass` 반환
  - 885 수집과 collection hash
  - 73개 통과와 소요 시간(실효 상한 약 1,180초)
- **범위 밖:** 전원 손실 지속성, 실패 후 성공 재시도, `verification=unavailable` 분기, 전체 P2.

실행 여부와 N11 한계의 수용은 Driver 처분과 Owner 권한입니다.

### Driver R0 Disposition

B1/B2/B3는 accept로 처분했다. 보정한 CLI 인자·진단, S5 recovery fault, 정확한73 ID가 정적으로 일치했으므로 차단0건으로 판단하고 Owner가 승인한6단계만 진행했다.

N10/N11/N12/N13/N15/N16/N17은 범위 또는 증거 한계로 accept했다. 모든 recovery role을 fault로 검증하지는 않았고, 기존 D3 40개도 변경된 child bytes로는 이번에 처음 실행했다. UnicodeDecodeError의 진단 한계는 유지했다. 실제 승인과 새 창은 과거 계획과 분리해 기록했다. 정확한 root 항목·파일·hash 조건은 각 단계에서 확인했다. Reviewer가 보지 못한 work/observer/canary/acquire와 공용 모듈 발췌 범위도 독립 검토의 한계로 남겼다.

N14는 revise로 처분했다. 일회성 static script의 command/runtime/exit/assertions와 현재 hash를 기록하되 재현 근거로 주장하지 않았다. 구체적인 후속 소비자가 없는 영구 사본은 추가하지 않았다. 상세 처분은 `/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-02/execution-01/r0-disposition.json`이다.

### Actual Six-Step Execution

입력에 고정한 Python3.14.7 Cellar binary와 `-I -S -B`, fixed bootstrap/controller, 허용된 mode/slot, 입력hash, 지정 cwd/environment, sandbox profile 및 출력 경계를 그대로 사용했다. 각 실제 명령과 runtime/environment는 `/Users/kyungseo/dev-home/agent-worktrees/hv2-reference-private-colvia-d3-verification-20261010-b03/exec/runs/<mode-slot>/inputs.json`의 command에 있다.

첫3단계와 entry collect의 상한은 각각300초, smoke/focused는 각각1,200초였다. Controller 합계 상한은3,600초/6회다. Parent wrapper는 각 시작 전 verify()를 통과한 뒤 start 기록과 프로세스를 만들었다. 별도의 before-check receipt는 없으며, 이 호출 순서와 실제 after_input_check 기록을 구분한다.

| 단계 | 결과 | 소요 시간 |
| --- | --- | --- |
| 1. acquire-base | exit0 / PASS | 0.659초 |
| 2. canary-base | exit0 / PASS | 0.656초 |
| 3. collect-base | exit0 / PASS | 0.463초 |
| 4. smoke-base | exit0 / PASS | 66.525초 |
| 5. collect-p2 | exit0 / PASS | 0.459초 |
| 6. focused-p2 | exit0 / PASS | 413.425초 |

모든 실행의 natural_completion/group_absent/inputs_unchanged_or_acquired_exact는 true, reason은 null이었다. Base 수집은776개이며 hash는 `31838e463b5c55346574a4c84c9bc543ac69c00751cac2b9909d927bc48e6c1f`다. Entry 수집은885개이며 hash는 `86d3faafb6b319decf2f82a00e131f98eaec37b6a70dacf9cd16c50ca5219497`다. Parent에서 실제 파일 hash를 재계산하고 entry의 ordered ID/occurrence/duplicates 전체를 고정 예상치와 대조했다.

Seed20은 selected/run20·pass20, focused73은 selected/run73·pass73(기존31 + D3 신규42)이었다. Failure/error/skip/expected_failure/unexpected_success/unstarted/unfinished는 모두0이다. 각 선택 ID의 occurrence는1이며 실행 순서도 일치했다. Canary 결과는 고정 canary의 exit0 범위로 보고한다. 예기치 않은 실행 실패는 없었고 자동 재시도는0회다.

### R1 Reviewer Response — Verbatim

# D3 R1 실제 결과 검토

**결론: 기록된 6단계 출력에서 차단 항목은 찾지 못했습니다.** 여섯 단계 모두 통과로 기록됐고, 입력·후보 identity가 고정값과 일치합니다. 도구·실행 없이 패킷 본문만 대조했고, SHA-256은 빈 파일 해시 하나를 빼고는 재계산하지 못했습니다. 이 검토는 Owner 수락이 아닙니다 (검토 모델 claude-opus-5-5).

## 1. 기록된 6단계 결과

| 단계 | exit / pass | 초 | 대조 결과 |
|---|---|---|---|
| acquire-base | 0 / true | 0.659 | OLD 101개, `old_verified`가 baseline-inputs hash `f1ee1072…`와 일치 |
| canary-base | 0 / true | 0.656 | stdout은 빈 파일 (`e3b0c442…`는 빈 입력 해시가 맞음) |
| collect-base | 0 / true | 0.463 | 776개, `31838e46…` — 예상과 문자 단위 일치 |
| smoke-base | 0 / true | 66.525 | 20/20 pass, 선택 20개가 입력 selection과 집합 일치 |
| collect-p2 | 0 / true | 0.459 | 885개, `86d3faaf…` — 예상과 문자 단위 일치 |
| focused-p2 | 0 / true | 413.425 | 73/73 pass; failure·error·skip·expected-failure·unstarted·unfinished 모두 0 |

- **공통 필드:** 여섯 단계 모두 `natural_completion`, `group_absent`, `inputs_unchanged_or_acquired_exact`가 true이고 `reason`은 null입니다.
- **73개 선택:** `selected.json`, `executed.jsonl`, stdout의 START/STOP을 하나씩 세어 고정 selection과 1:1임을 확인했습니다. 각 ID는 occurrence 1회, outcome은 모두 `['pass']`입니다.
- **identity 결속:** invocation hash 네 개(`10fe2114…`, `53b012b9…`, `0d2ffbb9…`, `a7e7dd6c…`)가 실행 계획과 같습니다. entry의 source digest는 `cc1455f6…`, base는 `19769972…`이고, controls 11개·runtime·Git·system config는 여섯 `inputs.json`에서 동일합니다.
- **슬롯과 경계:** 사용한 mode/slot은 계획의 여섯 개뿐이고 ancestor는 9개입니다.
- **시간과 호출 수:** 창 시작 10:53:00Z, focused 종료 11:07:37Z, 마감 13:23:00Z입니다. controller 합계는 약 482초(상한 3,600초)입니다. controller 6회, 재시도 0회, 이번 창 리뷰 2회째로 누적 10/20 안입니다.

## 2. 런타임 증거와 추론의 구분

- **직접 기록된 런타임 사실:** exit code, 수집 수와 hash 문자열, 테스트별 pass와 소요 시간, counts, 입력 불변.
- **pass와 테스트 코드를 결합한 추론(직접 기록 아님):**
  - fault가 실제로 주입 지점에 도달했다는 것. `len(injected) == 1`, `occurrences == 1`, 주입 뒤 `rows == []` 단언이 통과했다는 데서 나옵니다.
  - sandbox 안 directory fsync가 `pass`를 반환했다는 것. `test_d3_normal_sync_set_and_order`의 전 행 `pass` 단언에서 나옵니다.
  - child CLI dispatch 성공(이전 B1)과 recovery-release selector 도달(이전 B2). `diagnostic is None`, 토큰 `d3-sync:recovery:release-directory`, 순서 단언의 통과에서 나옵니다.
- **정황 근거:** fault 테스트 시간이 주입 단계 깊이에 따라 늘어납니다(admission·receipt 약 0.9초, release 약 3.3초, binding 4.3~5.0초). 추론과 어긋나지 않지만 증명은 아닙니다.
- **정적 근거(변동 없음):** R0의 호출 순서 추적, selector·토큰 대조, `static-checks.json`의 AST 결과. R1에서 다시 검증하지 않았습니다.

## 3. 비차단 지적

| # | 위치 | 내용 | 최소 조치 |
|---|---|---|---|
| R1-1 | `focused-p2/work/EntryProductTests/*/N-d3-sync.log` | child envelope(rows, injected, before/after)가 패킷에 없어 fault 도달은 2절의 추론에만 의존합니다. | 해당 로그 목록과 hash를 처분에 기록. 재실행 불필요 |
| R1-2 | `canary-base` | stdout이 비었고 `boundary-positive.json`과 `canary.py`가 패킷에 없습니다. 경계 통제의 내용은 확인하지 못했고 근거는 exit 0뿐입니다. | boundary 파일 hash 기록, 표현을 "canary exit 0"으로 한정 |
| R1-3 | 두 collect의 `collection.json` | 실제 bytes 없이 child stdout의 hash 문자열만 있습니다. smoke·focused의 runner가 독립 재수집 뒤 같은 hash를 요구하고 통과했으므로 보강은 됩니다. | Driver가 parent 쪽에서 파일 hash를 재계산해 기록 |
| R1-4 | `*-finish.json`의 `after_input_check` | 검사 대상이 패킷에 정의돼 있지 않습니다. N16 처분의 "매 단계 전/후 재확인" 중 "전" 기록은 보이지 않습니다. | 검사 항목 목록을 처분에 한 줄로 명시 |
| R1-5 | `focused-p2/work` | `suite-events.jsonl`, `preservation*.json`, `identity-stop.json`, `failures/`의 부재가 명시되지 않았습니다. 정상 통과면 없어야 합니다. | 부재 확인을 기록 |
| R1-6 | R0 처분 N14 | 정적 스크립트는 `/private/tmp`의 현재 hash만 남아 재현 근거가 아닙니다. 처분에도 그렇게 적혀 있습니다. | 변경 불필요, 한계 유지 |

## 4. R0 처분 확인

- **B1·B2·B3:** "런타임 미검증"으로 남았던 부분은 73/73 통과로 해소 방향의 증거가 생겼습니다. 다만 2절의 추론 한계가 붙습니다.
- **N10·N11:** 그대로 유효합니다. recovery의 하위 디렉터리 6개 구간, `release-parent`·`release-operation-parent`·`new-entry-parent`, O 부재 시 root 재-sync의 fault는 이번에도 주입되지 않았습니다. 성공 경로 관측만 있습니다.
- **N12:** 기존 D3 40개는 변경된 child bytes로 이번에 처음 실행됐고 모두 통과했습니다.
- **후보 동결:** `source_edits_after_freeze: 0`은 focused의 입력 불변과 digest 일치와 어긋나지 않습니다.

## 5. 이 결과가 보여주지 않는 것

- 전원 손실 지속성, 물리 flush와 fullfsync, 실제 파일시스템의 unavailable 재현.
- fault 뒤 성공 재시도, `verification=unavailable` 분기, staging·switch-directory role과 `release-directory` 외 replay role의 fault.
- same-entry는 jsonio receipt-parent 한 지점만 주입됐고, 비교 기준도 같은 신 코드입니다.
- composite 두 건은 guard 전 기존 거부의 보존 증거이며 신규 로직의 증거가 아닙니다.
- 전체 P2(full 19-prefix, four-executor, parent/worker, Git 전환), P3/P4, C2 활성화, 실제 adopter 적용.
- 과거 31/31(digest `18c2b62e…`)은 이번 후보의 근거가 아닙니다.

결과 수락과 N11 한계의 수용 여부는 Driver 처분과 Owner 권한입니다.

### Driver R1 Disposition And Actual Result Boundary

R1의 차단 지적은0건이다. 비차단 지적은 다음과 같이 처분했으며 재실행이나 소스 변경은 하지 않았다.

- R1-1 accept: 기존 child envelope51개를 읽고 절대 path/hash·exit·rows/injection 요약을 `/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-02/execution-01/r1-disposition.json`에 기록했다. Exit65인 fault envelope34개에서 실제 주입1건, 실패 snapshot과 반환 후 snapshot의 동일성, 이후 sync 부재를 직접 확인했다. Complete-prefix recovery fault2개도 포함된다. 이는 Reviewer의 직접 확인이 아니라 R1 이후 Driver의 읽기 전용 추가 근거다. Same-entry unavailable의 exit0은 별도 기존 동작으로 구분했다.
- R1-2 accept: canary boundary-positive 파일 hash, probe 목록, OLD chmod의 한계를 처분에 기록했다. 이를 더 넓은 보안 검증으로 주장하지 않는다.
- R1-3 accept: 두 실제 collection 파일의 hash를 다시 계산하고 고정 예상치와 일치함을 확인했다.
- R1-4 accept: 검사 목록을 명시했다. Packet과 모든 manifest 자료/accepted DR, source102/base101의 bytes/type/link-count/mode/size·src/tests 파일 목록·root 항목, controls11/runtime/Git/config, 이전 evidence210개와 authoring-01 전체 hash, tracked-base diff·실제 candidate bytes, step input hash와 collection gate, R1 입력 전후 hash다. 별도 before-check receipt를 소급 생성하지 않았다.
- R1-5 accept: focused의 suite-events.jsonl, preservation.jsonl, preservation*.json, identity-stop.json, failures/가 없음을 확인했다. 이 상태를 만들기 위한 삭제는 하지 않았다.
- R1-6 accept limit: 임시 static script의 현재 hash는 복구나 재실행의 보증이 아니다.

승인한 실행·검토 batch는 완료됐다. R0=1, controller=6, R1=1, retry=0이며 누적은 reviewer10/controller20/과거 correction1이다. Controller 실측 합계는 482.187초, review 합계는 399.080초다. R0 시작부터 R1 종료까지는 980.178초이며, R1은 `2026-10-10T11:09:20.811801+00:00`에 마감 전에 끝났다.

최종 결과는 `/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-02/execution-01/completion-result.json`, 사람이 읽는 결과는 [실행 보고서](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-02/execution-01/REPORT.md)에 있다. 동결 후 source/API/테스트 변경0건, 입력과 기존 증거 보존 PASS, commit/push/STATUS 변경0건이다.

N10/N11 등의 미검증 fault 조합, 물리 durability/fullfsync, 실제 unavailable, 실패 후 성공 retry, verification-unavailable, same-entry 비교 범위의 한계가 남아 있다. Full19-prefix·four-executor/all-writer·parent/worker·Git 전환 등을 포함한 전체P2, 후속P3/P4/C2 및 실제 adopter 검증도 미완료다. 이번 통과를 그 범위의 완료나 Owner의 결과 수락으로 승격하지 않는다.

### Custody And Retention

Source/control worktree와 이전 실행 경계는 진행 중인 P2 후속 및 기존 실패 증거의 소비자가 있어 유지한다. 새 b03 경계와 child/boundary 자료는 Owner의 결과 확인 및 R1-1/R1-2 근거 확인용이며 영구 review deliverable이 아니다. 해당 소비가 끝나고 필요한 결과가 보존됐음을 확인하면 재현 가능한 실행 환경과 중복 raw 자료를 재평가한다.

원시 review stream도 현재 review 경계 확인과 Owner 처분의 소비가 끝나면 같은 규칙을 적용한다. 이번 고정 candidate/packet/실제 결과·검토 원문·Driver 처분은 durable 경로와 기존 Work에 보존했다. 진행 중인 source나 사용 중인 checkout을 정리하지 않았으며 branch/commit/push 권한을 추가로 사용하지 않았다.


## D3 Batch Owner Acceptance And Next P2 Proposal — 2026-10-10

Owner actual request: “좋아. 이번 검증 배치 결과는 수락할게. 남은 P2에서 다음으로 진행할 한정 범위와 완료 기준, 필요한 실행·검토 예산을 제안해줘.”

### Accepted Result

Owner가 authoring-02의 R0→6단계→R1 검증 배치 결과를 수락했다. 대상은 source digest `cc1455f6fe756d3eedab8a96301119f7a8223b07d8c781fc7a6b094ca3f01833`, seed20/20·focused73/73, 실제 collection885 일치, 두 review 차단0건, 자동 재시도0회다. 완료 결과 `/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/contracts-d3-01/authoring-02/execution-01/completion-result.json`의 SHA-256은 `4f8cc771cc78f8597518d88bb649c151ca5005ae92cfdbcdb745323e322825ad`다. R0/R1 packet 및 검토 원문·Driver 처분은 기존 고정 기록을 유지한다. 그 문서의 “Owner acceptance pending”은 작성 시점의 상태이며 이 명시적 수락 기록이 현재 상태를 보충한다.

이 수락은 해당 배치의 결과 수락이다. 전체 P2/Work Done, 미검증 항목의 면제, C2 활성화·배포·adopter 전환·Git 행위 또는 다음 실행의 승인이 아니다. STATUS나 기존 결과 파일을 소급 수정하지 않는다.

### Recommended Bounded Slice

다음 제안은 **B1–B6 binding publication의 실제 중단·복구 검증**이다. 여기서 B1–B6는 prefix-oracle의 행 ID이며, 새 활성 binding 자체를 뜻하는 “B1”과 구분한다. 출발점은 기존 named after-launcher seam으로 만든 S5: 새 colvia는 완전한0755 파일, old hv2는 부재, 기존 binding은 B0, receipt/release는 완전하며 binding staging은 아직 없는 상태다.

고정 observer로 다음 실제 호출의 전후를 구분해 종료한다: binding staging 준비와 directory sync, binding.next의 exclusive0600 create, write/short-write, file/staging sync, binding replace, product/staging 두 parent sync. Write 길이는1·중간·L−1과 완성 길이로 구분하고, zero-byte는 create 직후 중단으로 관측한다. 실제 event/path/occurrence 목록을 먼저 고정하며 존재하지 않는 syscall이나 대표1건을 전체 호출의 증거로 세지 않는다.

현재 전환 prefix 테스트9개 중 binding 관련 증거는 binding.next open 뒤·1byte write 뒤·binding replace 뒤 중단이다. 이 세 건의 통과를 B1–B6 전체 완료로 확대하지 않는다. 새 사례는 최대32개, 회귀 선택은 기존 prefix9개로 제한하여 focused 선택 상한은41개다. 정확한 개수와 ID는 authoring 후 AST·관측 trace·정적 대조로 고정한다. 실제 호출을 빠짐없이 다루는 데32개를 넘겨야 하면 사례를 생략하지 않고 실행 전에 범위/예산 재제안으로 멈춘다.

수정 후보는 기존 tests/test_entry_window_transition.py와 이 Work의 계획/결과 기록이다. 새 테스트 helper는 test-local로 한정하며 기존73개 테스트 본문·공용 child/helper·factory 구조를 유지한다. Product, observer/controller/policy/oracle 변경이 필요하면 자동 수정하지 않고 원인과 별도 변경안을 보고한다. 새 production fault hook, schema 또는 복구 권한은 추가하지 않는다.

### Completion Criteria

1. B1–B6의 실제 event/path/occurrence와 각 전후 상태·예상 결과를 유한 목록으로 고정한다. 중단은 observer의 의도한 SIGKILL과 마지막 event로 확인한다. Observer가 감싸는 Python 호출의 증거이지 전원 손실의 증거는 아니다.
2. Replace 전에는 B0와 정확한 staging prefix를 보존하고, 동일 plan/token/candidate의 복구로 S6에 도달한다. Replace 후에는 완전한 B1·mode0600·binding.next 부재를 확인하고 같은 요청의 replay가 현재 binding을 되돌리지 않는다. 모든 경우 N은 완전한0755이고 O는 부재여야 한다.
3. Project truth·일반 파일·receipt·release를 전후 대조한다. 합법적인 binding/staging 변경과 허용된 lock anchor만 구분하며 그 밖의 변경을 허용하지 않는다. 정상 replay 뒤 추가 재실행은 자동 반복 예산으로 만들지 않는다. 각 테스트의 고정 recovery/replay 절차와 배치 자동 재시도는 서로 다르다.
4. 고정 selection의 모든 ID가 실제 collection에 정확히1회 등장하고, 선택된 새 사례와 회귀9개가 모두 pass한다. Failure/error/skip/expected-failure/unstarted/unfinished는0, 입력 전후 동일성은 PASS여야 한다. 의도한 child SIGKILL은 예상 결과이며, 이 단언 실패나 통제·입력 실패는 STOP이다.
5. 새 R0와 실제 결과 R1의 차단 사항을 Driver가 처분하고 Owner가 이 한정 결과를 수락한다. 위 조건을 충족해도 full19-prefix나 전체P2 완료로 표시하지 않는다.

### Proposed Budget And Approval Gates

먼저 별도 authoring 승인으로 테스트/유한 사례표/정확한 ID·입력·명령을 작성하고 정적 검사를 한다. 지금은 이 제안만 기록하며 테스트 작성이나 실행은 하지 않는다. 후보 고정 후 실제 실행·private 자료 Claude 전송 승인을 받는다.

| 항목 | 제안 상한 |
| --- | --- |
| 후보와 보정 | 새 후보1개, 자동 보정·재시도0회 |
| R0 / R1 | fresh no-tool Claude 각1회·각20분, 총40분 |
| Controller | 새 경계의 acquire/canary/base collect/seed20 smoke/entry collect/focused, 총6회 |
| Controller 시간 | acquire/canary/두 collect 각300초, smoke/focused 각1,200초: 합계3,600초(60분) |
| 전체 실행·검토 창 | R0 시작부터120분; 외곽 대기/정리/기록을 위한20분 포함 |
| 실제 테스트 선택 | 신규 최대32 + 기존 prefix9, focused 최대41개 |

직전 배치의 focused73은413.425초, R0/R1은313.733/85.347초였으므로120분은 실측 예측이 아니라 보수적인 상한 제안이다. 이전150분 창과 소진 호출은 재사용하지 않는다. 승인 시 누적 상한은 reviewer10→12, controller20→26이다. 각 단계 전 남은 최악 상한과 정리 여유를 확인하고, 첫 예기치 않은 실패·입력 불일치·시간/출력/보존 한계에 보존 후 중단한다. 자동 재검토나 source 수정 후 재실행은 없다.

현재 controller는 focused-p2 슬롯을 이미 사용했으며, 남은 correction 슬롯을 새 기능 검증에 전용하지 않는다. 통제물을 바꾸지 않는 새 비-Git 실행 경계를 승인된 agent-worktrees root 아래에 제안하고 정확한 경로·부재·미등록·runtime·명령·출력 위치는 authoring 단계에서 고정한다. 따라서6회에는 새 경계의 선행 통제 확인이 포함된다. 기존73 전체나 complete suite를 이번 focused 범위에 다시 넣지 않는다.

### Remaining Scope And Custody

이번 다음 제안에서 S1/S2 tear·staging 전체, S3 publication, N/O의 남은 중단 구간과 B7의 빈 staging retirement, four-executor/all-writer·late-lock 전체, Git admission/ignore, parent/worker 및 mixed-history lifecycle은 제외한다. D3의 N10/N11 등 나머지 fault 조합과 물리 durability/fullfsync도 완료로 간주하지 않는다. 이후 P2 범위와 P3/P4/C2는 별도로 남는다.

현재 source/control worktree는 진행 중인 P2 때문에 유지한다. b03 실행 자료의 구체적인 다음 소비자는 B1–B6 selector 작성에 사용할 기존9개 prefix observer trace와 실패 직전 상태 관측이다. 새 사례표/selector가 고정돼 해당 자료의 소비가 끝나면 재현 가능한 실행 환경과 중복 raw 자료를 재평가한다. 수락된 최소 결과·검토 원문·처분·입력 custody는 유지하며 지금 checkout 이동·삭제·새 실행 경계 생성은 하지 않는다.


## B1–B6 Test Authoring And Fixed Execution Inputs — 2026-10-10

Owner actual request: “좋아. 제안한 B1–B6 범위의 테스트 작성·정적 확인·실행 입력 확정까지 승인할게. 완료 후 정확한 테스트 목록과 명령, 입력 해시를 보고해줘. 실제 실행과 Claude 전송은 그때 별도로 승인할게.”

### Authored Scope And Static Result

승인한 범위에서 tests/test_entry_window_transition.py에 test-local helper1개와 테스트28개를 추가했다. 기존73개 test 본문·기존 모든 helper·공용 child·factory 구조·다른 클래스는 AST가 같고 제품 및 control11개는 hash가 같다. 새 테스트28개와 기존 transition_prefix_01~09 회귀9개, 합계37개를 선택했다. 테스트 수집·실행·controller·Claude/auth 호출은0회다.

B-01 directory preparation11개(기존 staging mkdir-before, .hrn/staging 준비 parent/self sync 전후, 새 operation mkdir 전후 및 parent/self sync 전후), B-02 exclusive open2개, B-03 write-before/full/1/mid/L−1의5개, B-04 file/staging sync4개, B-05 replace2개, B-06 양쪽 parent sync4개다. 정상 경로의25개 관측 전후 지점과 short-write3개이며 기존 staging mkdir는 FileExistsError를 일으켜 mkdir-after가 없다. 읽기 전용 open·close·F_FULLFSYNC·B7 retirement 내부 지점은 선택하지 않는다. B0 recheck는 replace-before의 정확한 B0 snapshot 및 변경 없는 코드의 호출 순서로 확인하며 별도 read 중단의 증거는 아니다.

각 case는 기존 named after-launcher seam의 S5로 시작하고 고정 observer event/path/occurrence의 SIGKILL과 마지막 완전한 event, PID/PGID·25행 순서 prefix를 단언한다. B0/B1·staging prefix의 bytes/type/mode와 전체 target snapshot을 대조하고, 동일 request/token/candidate로 교체 전1회 recovery 또는 교체 후1회 replay를 수행하도록 작성했다. 새로운 binding/receipt 기대 bytes는 product 생성 helper를 호출하지 않고 record shape에서 독립 구성한다. N0755·O부재·B1/0600·binding.next 부재와 정확한 empty staging을 최종 단언한다.

Python3.14.7 AST/compile 정적 검사 exit0, git diff --check 및 변경 patch reverse-check --whitespace=error-all exit0. Base101/entry102 source 목록·mode/size/hash, controls11, runtime/Git/system-config, 이전 authoring-02의61개 파일을 읽기 전용 대조했다. 기존 수락 배치 prefix06의 actual O-unlink 이후 recovery trace25개와 새 selector 순서/occurrence가 일치했다. 이 trace 대조는 과거 runtime 자료의 정적 활용이며 새 named-seam 경로의 도달·복구·시간·테스트 PASS는 아직 unavailable이다. AST/compile는 product/test import나 discovery가 아니다.

작성 보조 작업 중 잘못 옮긴 copy-guard hash 때문에 쓰기 전에1회 중단됐고, freeze 보조 스크립트의 실행 전 구문 오류1건을 수정했다. 원본 hash 보존 후 올바른 작성 결과를 반영했다. 이는 허가되지 않은 테스트/검토 실행이나 batch 자동 재시도가 아니며 향후 실행의 retry0 조건은 그대로다.

### Exact Inputs And Proposed Commands

전체 ID37개·28개 selector/기대 상태는 [작성 보고서](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/binding-prefix-01/REPORT.md), [ID 목록](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/binding-prefix-01/test-selection.json), [사례표](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/binding-prefix-01/case-matrix.json)에 있다. 정확한6개 controller argv·2개 review argv·cwd·환경·출력·상한은 [실행 계획](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/binding-prefix-01/execution-plan.json)과 [명령 목록](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/binding-prefix-01/COMMANDS.md)에 고정했다.

- Source102 digest: `b3a4336e8f020ad76ce13702964e90e724c041e85ffaa24c638a8463f25b1142`.
- Test file SHA-256: `db23ef74818e115130f30f71ddf7588ea05db7a9992b0732663d03a58f4353ac`.
- Git base: `238514686078ce1564010a7b69013f48a635c57c`; tracked-base diff SHA-256: `c3c0a89c3c641e17e3376edbc09950cd1e923a67ac3063e01a038dc6c2fe8b66`. 새 테스트 파일은 untracked이므로 이 diff 밖이며 source map과 R0 packet의 full bytes로 별도 고정했다.
- R0 packet SHA-256: `8d33b5848c2670f9ac57b825f801ebae83aab8884eab1101b71b5e3c39d43fbe`, bytes 930240. 아직 전송하지 않았다.
- 전체 준비 입력 manifest SHA-256: `5629c31d06f7244547b9d32925449190190af88b6335d2d5f02098d02d3bc6b7`; [manifest](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/binding-prefix-01/prepared-manifest.json). 네 invocation·selection·case matrix·execution plan 등의 full hash는 보고서와 manifest에 있다.

Factory137=control24+old fixture1+product101+foundation11, default776과 합한 수집913은 정적 예상이다. 실제 새 collection의 canonical bytes/hash/ID 순서/occurrence가 고정 예상치와 일치해야 smoke/focused를 실행할 수 있다. 선택37개는 각1회이며 기존 default 중복은 역사와 동일하게 보존한다. 불일치 시 자동 재고정하지 않는다.

새 실행 경계 제안은 `/Users/kyungseo/dev-home/agent-worktrees/hv2-reference-private-colvia-binding-verification-20261010-b04`다. 부재·미등록·상위 Git/authority 부재를 확인했으며 생성하지 않았다. 순서는 R0→acquire→canary→base collect→seed20 smoke→entry collect→focused37→R1이다. 총120분, reviewer2회 각20분, controller6회 합계60분, 외곽 대기/정리/기록20분, 자동 보정·재시도0회다. 이전150분 창이나 소진 slot을 재사용하지 않는다. 누적 제안 상한은 reviewer12/controller26이고 이번 실행 수는0이다.

실행과 private 자료의 Claude 전송은 다음 별도 Owner 승인 대상이다. 각 review 전 실제 subscription auth 경로와 model/session/tool 경계를 확인한다. R1 packet은 실제 결과 뒤 정해진 구성으로 생성해 hash를 기록하므로 지금 존재하지 않는다. 첫 뜻밖의 실패·입력/수집 불일치·timeout·출력/보존 한계에서 보존 후 중단하며 자동 수정·재실행·selection 축소·slot 교체는 없다.

### Limits And Custody

이번 fixture에는 진행 중인 local/parent/worker Work가 없으며 typed truth는 비어 있다. 일반 파일·format·receipt·release와 그 빈 상태의 정확한 보존은 검사하지만 transition_content_verification은 not-applicable을 기대한다. 실제 Work/adopter 전환, full19-prefix/전체P2·four-executor, B7·물리 durability/fullfsync·P3/P4/C2는 별도 미완료다.

기존 Work에만 이 기록을 추가하며 STATUS·commit·push·Work Done을 바꾸지 않는다. Source/control checkout은 진행 중인 P2에 사용해 유지한다. b03 실행 환경과 trace는 계획된 R0의 selector 검토 시 원시 근거 확인용으로 유지하고, 그 처분 후 소비가 끝난 재현 가능 환경·중복 raw를 재평가한다. 준비 자료의 소비자는 Owner exact 실행 승인과 계획된 R0/R1이다. 새 before/full source tree는 만들지 않았고 이전 full test candidate + 이번 patch + packet의 exact test bytes로 복원 자료를 보존한다. 이 보존은 영구 추적·commit 승인이 아니다.


## B1–B6 Authorized Execution And Reviews — 2026-10-10

Owner actual request: “좋아. 고정한 B1–B6 후보의 R0 → 6단계 실행 → R1과 private 자료의 Claude 전송을 승인해. 최대 120분, 자동 재시도 0회로 진행하고 실패나 입력 불일치가 나오면 보존한 뒤 멈춰서 보고해줘.”

### Actual Execution And Evidence

승인한 R0 → 6단계 실행 → R1을 완료했다. Seed20/20, focused37/37(신규28+회귀9), 두 검토 차단0건이다. 자동 재시도0회이며 전체P2 완료나 Owner의 결과 수락을 뜻하지 않는다.

## Actual Results

| 단계 | 결과 | 소요 초 |
| --- | --- | --- |
| acquire-base | PASS | 0.652 |
| canary-base | PASS | 0.666 |
| collect-base | 776개, 고정 hash 일치 | 0.457 |
| smoke-base | 20/20 PASS | 65.901 |
| collect-p2 | 913개, 고정 hash 일치 | 0.461 |
| focused-p2 | 37/37 PASS | 395.41 |

선택된 ID는 모두 occurrence1회이며 실패·error·skip·expected failure·미시작·미완료0이다. 6단계 모두 자연 종료·process group 부재·입력 불변을 확인했다. Controller 합계 463.547초, R0 318.812초, R1 66.253초다. R0 시작부터 R1 종료까지 954.116초(약15분54초)로120분 창 안이다.

신규 B0 사례23개는 같은 요청으로1회 recovery하여 updated, B1 사례5개는 --recover 없이1회 replay하여 replayed였다. 실제 마지막 event/path/occurrence와 short-write1/263/526바이트, full527바이트를 기존 출력에서 확인했다. 최종 B1 mode0600·binding.next 부재·old hv2 부재를 확인했다. SIGKILL returncode, 중단 직후 exact snapshot·lock 해제는 통과한 테스트 단언의 증거이며 별도의 raw returncode/snapshot 기록은 없다.

## Reviews And Driver Dispositions

R0/R1 실제 모델은 claude-opus-5-5이며 fresh session은 각각 `8ae8d784-9d34-410e-887e-3be072491cff`, `ed575274-4b36-4f75-a140-ff8254e84e1c`다. Subscription claude.ai/firstParty/pro를 각 호출 전 확인했다. 두 호출 모두 tools/MCP/실제 tool use0, exit0, 입력 불변 PASS다.

R0 C1은 과거 실측의 보수적 투영645.597초에50% 여유를 더한968.396초로 실행 상한의 여유를 확인했다. 실제 focused395.410초였다. C2는 각 controller 시작 기록의 umask0022와 Popen 직전 assertion으로 확인했다. 고정 source/controls/argv를 바꾸지 않았다.

R1의 비차단 G1–G4는 재실행 없이 처분했다. 여섯 start record의 umask값, 기존 staging mkdir-after 부재, canary의 named denials10개와 child inheritance를 읽기 전용으로 확인했다. Reviewer가 제안한 가장 이른 kill trace는22417에서 끝나므로, 다음 parent-sync-before trace의 실제22418–22421을 사용했다. F_FULLFSYNC canary 실행은 물리 durability 증명이 아니다.

설명 보정: binding/receipt record shape는 독립적으로 구성하지만 candidate_ref와 preview request는 제품 산출값이다. 독립성은 이 범위로 제한한다. 고정된 작성 보고서와 packet은 소급 수정하지 않고 이 기록과 기존 Work에 현재 처분을 남긴다.

[실제 결과](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/binding-prefix-01/execution-01/completion-result.json), [28개 관측 자료](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/binding-prefix-01/execution-01/case-observations.json), [R0 처분](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/binding-prefix-01/execution-01/r0-disposition.json), [R1 처분과 근거](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/binding-prefix-01/execution-01/r1-disposition.json).

## Identity And Limits

Source digest: `b3a4336e8f020ad76ce13702964e90e724c041e85ffaa24c638a8463f25b1142`. 실제 entry collection913 SHA-256: `ddc52e590c0447df1c8b3ccc6cf630476b5801c0857e55c1cf449b639bd39ccb`.

R1 actual-results packet SHA-256: `ee75276aaf4a4b420006a43dd1cdc7a4463c226eee4fdd42f594877a6ce3d760`. [고정 실행 명령](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/binding-prefix-01/COMMANDS.md), [고정 준비 입력](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/binding-prefix-01/prepared-manifest.json), [R0 원문](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/binding-prefix-01/review-r0/review.md), [R1 원문](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/binding-prefix-01/review-r1/review.md).

이번 결과는 계측된 Python 호출 경계에서의 B1–B6 중단과 해당 fixture의 복구/replay 증거다. Typed truth가 비어 있고 진행 중인 Work가 없어 transition_content_verification은 not-applicable이다. 실제 Work/adopter, full19-prefix/전체P2, four-executor, Git 대상, B7 retirement, 후속 child 재동기화 순서, 물리 durability/fullfsync, P3/P4/C2는 미완료다.

결과 수락은 Owner에게 남는다. Source/control checkout은 진행 중인 P2에 필요해 유지한다. b04 실행 환경·case events와 b03의 인용 trace/timing은 이번 결과 확인·근거 검토용으로 유지하고, 소비 종료 뒤 재현 가능한 환경과 중복 raw를 재평가한다. 최소 결과·검토 원문·처분·입력은 실행 경계 밖에 보존했다. Source 변경·commit·push·STATUS 변경은 없었다.

### Reviewer R0 Response — Verbatim

# R0 검토 결과 — B1–B6 binding-publication 후보 (28 신규 + 9 회귀)

**결론: 테스트 소스에서 정적으로 확인되는 차단 결함은 찾지 못했습니다. 다만 실행 전에 소스 변경 없이 닫아야 할 조건이 2건(C1, C2) 있습니다.**

이 검토는 도구를 쓰지 않은 정적 판독이며, Owner 수락이 아닙니다. 이 후보에 대한 새 실행 결과는 없습니다.

## 실행 전 조건

**C1. focused-p2 1,200초 예산의 근거가 packet에 없습니다.**
- 신규 28개는 각각 OLD init, in-process S5 준비, 계측된 kill child, 계측된 후속 child를 실행합니다. 회귀 9개도 계측 child가 2개씩입니다.
- observer는 이벤트마다 로그를 fsync합니다. 상속 trace에서는 recovery child 하나가 B1 직후까지 약 35,900 이벤트였습니다.
- controller는 1,180초에 중단하므로 테스트당 평균 약 32초가 한도입니다. 초과하면 재시도 없이 슬롯을 잃습니다.
- 최소 조치: b03 `executed.jsonl`에서 prefix_01–09의 실제 소요 초를 읽어 37건 합계를 투영하고 Work에 기록하십시오. 여유가 불충분하면 실행 전에 계획(예산 또는 분할)을 Owner에게 다시 승인받아야 합니다.

**C2. 디렉터리 모드 `0o755` 기대값이 umask 022에 의존하는데 계획이 이를 고정하지 않습니다.**
- `binding_prefix_case`는 `Path.mkdir()`로 만든 staging 디렉터리를 `('directory', 0o755)`로 단정합니다.
- 제품의 `_entry_umask`는 0600 보존만 요구하므로 umask 027/077에서도 제품은 진행하고 테스트만 실패합니다.
- `parent_environment`에는 umask 항목이 없습니다.
- 최소 조치: 각 controller 호출 직전에 umask가 0022임을 확인·기록하는 precondition을 추가하고, 다르면 시작 전에 중단하십시오.

## 비차단 권고 (R0 처분에 기록, 이번 후보는 변경 불필요)

- **N1. 기존 staging의 mkdir-after 부재를 직접 단정하지 않습니다.** `keys`에 `('mkdir-after', '.hrn/staging')`가 없어서 그 행이 생겨도 걸러집니다. occurrence 이동과 witness 순서 비교로 간접 검출될 뿐입니다. 후속 수정 시 해당 행 0건과 S5의 `.hrn/staging` 존재를 명시 단정하십시오.
- **N2. S5 시작 상태의 추가 항목 집합을 정확히 단정하지 않습니다.** 단정하는 것은 colvia, receipt, release, B0, hv2 부재, entry staging 부재입니다. `switch-entry-transition` 빈 디렉터리 존재 같은 나머지는 이후 `expected == snapshot` 비교로만 고정됩니다.
- **N3. 후속 child의 이벤트를 버립니다.** B-06 after 셀의 replay 재동기화나 recovery 재-sync는 이 28건이 증명하지 않고 D3 테스트에 의존합니다. R1에서 과대 해석하지 않도록 하십시오.
- **N4. "독립 literal"은 부분적입니다.** B1과 receipt의 형태는 테스트 literal이지만 `candidate_ref`와 `preview['request']`는 제품 산출값입니다.
- **N5. source root 이름 드리프트 위험.** entry의 `source_root_entries`에 `.idea`가 있으므로 실행 창 동안 IDE나 `.DS_Store` 생성이 없도록 하십시오.
- **N6. collect 게이트 비교 대상.** `stdout.log`가 아니라 `collection.json` 바이트 해시로 대조하십시오 (entry `ddc52e59…`, base `31838e46…`).

## 정적으로 확인한 사항

- **개수:** 신규 28 = B1 11 + B2 2 + B3 5 + B4 4 + B5 2 + B6 4이고, 25 셀 + short-write 3입니다. 회귀 9를 더해 선택 37이며 중복은 없습니다.
- **수집 913:** default 776은 ID 목록을 클래스별로 직접 세어 일치를 확인했습니다 (중복 occurrence 122 + 55 포함). factory 137 = 24 + 1 + 101 + 11이고, EntryProductTests 101 = 신규 28 + 기존 73입니다.
- **매핑 일치:** test method의 stop index, `flow` 25행, case-matrix, trace-map의 event/path/occurrence가 모두 일치합니다. open flags 2818과 mode 384도 맞습니다.
- **occurrence 선택자:** 제품 코드 경로와 맞습니다. 예를 들어 `.hrn` fsync 3번째는 guard, admission, staging durable 순서의 세 번째입니다. 잘못된 셀이 선택되면 `starts == 1`과 witness 순서 동등성 단정이 검출합니다.
- **partial write:** 1, 중간, L−1 모두 단일 `os.write`의 truncation과 `_entry_file_prefix`의 0600 leading-prefix 규칙에 부합합니다.
- **recovery와 replay:** B0 셀은 `--recover` 1회로 `updated`, B1 셀은 `--recover` 없이 1회로 `replayed`가 됩니다. 제품은 완료 후 staging 디렉터리를 지우지 않으므로 `completed` 기대와 맞습니다.
- **6단계 계획:** argv bootstrap이 `common.BOOTSTRAP`과 같고, mode/slot 허용, 입력 해시 4종, 예산(300×4 + 1200×2 = 3600, 외곽 +180, 창 7200), 누적 한도(26/12)가 정합합니다.
- **변경 범위:** patch는 순수 추가(+210행)입니다. 제품과 controls 11개의 해시 표기는 packet 내 모든 위치에서 일치합니다.

## 상속 trace에만 의존하는 사항

- 25행의 occurrence는 prefix_06 recovery child에서 얻은 값입니다. 그때의 시작 상태는 실제 unlink kill 직후였고, 새 테스트는 named seam `after-launcher`로 S5를 만듭니다. 네임스페이스는 같다고 추론되지만 새 실행의 단정으로만 확정됩니다.
- 테스트 `canonical`과 `ref`가 제품의 `canonical_json_bytes`, `record_ref`와 같다는 점은 기존 테스트 관행과 trace의 527바이트로만 뒷받침됩니다.
- 0바이트와 1바이트 `binding.next` 복구는 prefix_07/08의 과거 통과에 근거합니다.

## packet만으로 확인할 수 없는 사항

- `cli.py`, `work.py`, `jsonio`/`workspace` 전체, `COMMANDS.md`가 packet에 없습니다. 그래서 `--recover` 없는 성공 replay의 exit 0 매핑은 검증하지 못했습니다. 기존 테스트는 이 경로를 충돌 거절(65)로만 지나갔습니다.
- 다음도 검증하지 못했습니다: before 파일 + patch → `db23ef74…` 해시 연쇄, 이전 배치 61개 파일 보존, 실행 root 부재, R0/R1 CLI 플래그의 유효성.
- 실제 모델과 세션 식별은 stream 메타데이터로 기록하십시오. 제 자기 보고는 증거가 아닙니다.
- 이번 범위는 물리 내구성(fullfsync), B-07 retirement, 비어 있지 않은 truth/Work, 전체 P2를 증명하지 않습니다.

### Driver R0 Disposition

차단 소스 결함0건. C1 accept: 과거 prefix9 실측합과 가장 느린 사례, complete-S5 recovery proxy를 읽어 projection645.597초, 50% 여유 포함968.3955초를 산출했다. 실제 예산 보장이 아닌 보수적 추정이며 상한은 늘리지 않았다. C2 accept: 실행 parent의 umask0022를 각 start record에 기록하고 실제 Popen 직전 다시 같은 값인지 assertion했다. 추가 측정값을 별도 receipt로 저장한 것은 아니며 소급 생성하지 않는다. 이 precondition은 task-local outer supervision에만 추가했고 고정 argv/input/controller/product를 바꾸지 않았다.

N1/N2/N3 accept limitation: 기존 staging mkdir-after 부재와 S5 추가 항목 집합의 독립 단정, 후속 child resync 순서는 새 테스트가 직접 모두 증명하지 않는다. N4 revise wording: record shape만 독립 literal이고 candidate_ref/preview request는 product-derived다. N5 accept: 매 경계 root 목록·type drift 검사. N6 accept: 실제 collection.json bytes/hash로 gate를 검사했다. 생략된 전체 CLI/work/shared code, patch 연쇄, 이전61개 보존 등 Driver-only 확인을 Reviewer 독립 검증으로 바꾸지 않는다.

### Reviewer R1 Response — Verbatim

# R1 검토 결과 — B1–B6 binding-publication 실제 실행 (28 신규 + 9 회귀)

**결론: 제출된 실제 출력에서 차단 결함은 찾지 못했습니다. 다만 R0 처분 C2(umask 확인)의 실행 기록이 packet에 없어 Work에 보완 기록이 필요합니다.**

이 검토는 도구 없이 packet만 읽은 것이며 Owner 수락이 아닙니다. 해시는 packet에 적힌 값끼리 대조했을 뿐 재계산하지 않았습니다.

## 보완이 필요한 사항 (비차단)

**G1. C2 처분의 "매 controller Popen 직전 umask 0022 확인" 기록이 packet에 없습니다.**
- 여섯 개 `*-finish.json`에는 `outer_exit`, `outer_seconds`, `ended_utc`, `after_input_check`만 있습니다.
- focused-p2는 `('directory', 0o755)` 단정이 28건 모두 통과했으므로 간접적으로 뒷받침됩니다. 나머지 5단계는 근거가 없습니다.
- 최소 조치: Driver가 가진 확인 기록을 Work에 첨부하십시오. 없다면 C2를 "focused-p2에 한해 간접 확인"으로 낮춰 적으십시오. 재실행은 필요 없습니다.

**G2. N1(기존 staging의 mkdir-after 부재)은 여전히 직접 단정이 아닙니다.**
- 관측된 sequence 간격으로는 mkdir-after 행이 없는 것과 정합합니다. `.hrn/staging` mkdir-before 22417 → `.hrn` fsync-before 22422는 간격 5이고, operation 쪽은 mkdir-before 22429 → mkdir-after 22431 → fsync-before 22435로 after 행만큼 1이 더 깁니다.
- 이것은 제 산술 추론입니다. 최소 조치: 보존된 `…staging_mkdir_before-2.events`에서 seq 22418–22421을 읽기 전용으로 확인해 Work에 한 줄 기록하십시오.

**G3. `canary-base/work/canaries.json`이 packet에 없습니다.**
- canary는 `result.json`(exit 0)과 `boundary-positive.json`으로만 확인했습니다. named denial과 `F_FULLFSYNC` 실행 여부의 실제 값은 보지 못했습니다.

**G4. N4 처분("설명 수정")의 반영 여부를 확인할 수 없습니다.**
- packet의 REPORT는 R0 이전에 고정된 판입니다. 수정 문구는 Work에 남기십시오.

## 새 실행으로 확인된 사항

**6단계 controller**

| 단계 | exit | 소요 초 | 비고 |
| --- | --- | --- | --- |
| acquire-base | 0 | 0.652 | files 101, `old_verified` = baseline-inputs 해시 `f1ee1072…` |
| canary-base | 0 | 0.666 | stdout 비어 있음 |
| collect-base | 0 | 0.457 | 776건, `31838e46…` |
| smoke-base | 0 | 65.901 | 20/20 통과 |
| collect-p2 | 0 | 0.461 | 913건, `ddc52e59…` |
| focused-p2 | 0 | 395.41 | 37/37 통과 |

- 여섯 단계 모두 `execution_pass`, `natural_completion`, `group_absent`, `inputs_unchanged_or_acquired_exact`가 true입니다. 외곽 `after_input_check`도 모두 PASS입니다.
- 실행 순서, mode/slot, 입력 해시 4종, 예산(300×4, 1200×2)이 계획과 같습니다. 재시도와 slot 대체는 보이지 않습니다.
- focused-p2는 11:49:07Z에 끝났고 창 기한은 13:34:35Z입니다.

**수집 913**
- 두 `collection.json`의 해시가 고정 기대값과 같습니다(N6 충족). 수집 건수는 base 776, p2 913입니다.
- 내역 913 = 776 + 137과 EntryProductTests 101 = 28 + 73은 R0의 정적 계수이며 이번에 다시 세지 않았습니다. `factory_ids` 목록은 기대값과 일치합니다.

**선택 37건**
- `selected.json`, `executed.jsonl`, stdout이 모두 37건 통과이고 중복이 없습니다. failures, errors, skips, unstarted, unfinished는 0입니다.
- C1: 실제 395.41초로 투영 645.6초와 중단 한도 1,180초 안입니다. 회귀 9건은 11.05–13.24초로 b03과 비슷합니다.

**28건 kill 관측 (Driver 추출본 기준)**
- 마지막 이벤트의 event/path와 scenario의 occurrence가 28건 모두 case-matrix와 같습니다.
- `kill_event_count`가 상속 trace의 sequence와 25개 지점 모두 같습니다(22417 … 35898). named seam으로 만든 S5와 과거 unlink-kill S5가 같은 이벤트 흐름을 낸다는 점이 이번 실행에서 확인됐습니다.
- open detail은 flags 2818, mode 384입니다. write-before requested는 527입니다.
- short write는 written 1 / 263 / 526이고 full은 527입니다.
- replace detail의 `from`은 `binding.next`입니다.
- 모든 행의 pgid가 47729로 같고 pid는 케이스마다 다릅니다.

**recovery와 replay**
- B0 셀 23건은 후속 결과가 `updated`입니다. B1 셀 5건(replace-after와 B6 4건)은 `replayed`입니다.
- R0에서 검증하지 못한 "`--recover` 없는 replay의 exit 0"은 이 5건의 통과로 이 fixture에 한해 확인됐습니다.
- 28건 모두 최종 binding 해시가 `fc1b90b2…`로 같고 mode는 0600입니다. `binding.next`와 `hv2`는 없습니다.
- `transition_content_verification`은 모두 `not-applicable`입니다.
- receipt 해시가 케이스마다 다른 것은 plan의 `target_fingerprint`가 대상 경로에 의존하기 때문으로 추론합니다.

**변경 범위**
- controls 11개 해시가 여섯 `inputs.json`과 두 `collection.json`에서 동결값과 같습니다.
- source digest는 `b3a4336e…`이고 제품 `product.py`는 `7c5797f7…`입니다.
- `source_root_entries`가 일치하므로 N5의 `.idea` 드리프트는 없었습니다.

## 통과한 단정으로만 뒷받침되는 사항 (원자료 미확인)

- kill child의 `-SIGKILL` returncode
- kill 직후 스냅샷의 정확한 동등성
- S5 시작 상태 단정
- witness 순서 동등성과 `starts == 1`
- 전체 스냅샷 보존
- lock 해제

이 항목들은 `outcome: pass`로만 증명됩니다. 별도로 보존된 값이 없고, `case-observations.json`도 Driver의 사후 추출입니다. 이벤트 원본은 제가 보지 못했습니다.

## 이 결과로 주장할 수 없는 것

- **전체 P2 완료.** 19-prefix 전체, S1/S2/S3/N/O 단계의 before/after, B-07 retirement, four-executor, Git 대상은 범위 밖입니다.
- **비어 있지 않은 truth와 Work.** fixture는 `truth_refs == []`이고 선택된 local/parent/worker Work가 없습니다. Work 보존에 대한 증거가 아닙니다.
- **물리 내구성.** 관측한 것은 계측된 Python 호출 경계와 프로세스 kill입니다. 전원 손실이나 `F_FULLFSYNC`의 영속성은 증명하지 않습니다.
- **후속 child의 재동기화 순서(N3).** 후속 이벤트는 보존만 했고 분석하지 않았습니다. D3 재동기화 순서는 이 28건이 자격을 주지 않습니다.
- **B-05의 B0 recheck 내부 중단.** replace-before 스냅샷과 정적 코드 순서에만 의존합니다.
- **독립 literal의 범위(N4).** `candidate_ref`와 `preview['request']`는 제품 산출값입니다.
- **packet 밖 사항.** `cli.py`/`work.py` 전체, patch 해시 연쇄, 이전 배치 61개 파일 보존은 Driver 확인에만 의존합니다.
- **이 R1 호출의 모델·세션 식별.** stream 메타데이터로 기록하십시오. 제 자기 보고는 증거가 아닙니다.

### Driver R1 Disposition And Acceptance Boundary

차단 지적0건. G1 accept: 기존6개 `*-start.json`의 `observed_parent_umask=0022`와 timestamp/path/hash를 [R1 처분](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/binding-prefix-01/execution-01/r1-disposition.json)에 기록했다. 즉시 launch guard는 실제 supervisor 코드와 호출 성공 순서의 근거이며 별도 두 번째 측정 receipt가 있는 것으로 주장하지 않는다.

G2 accept with correction: staging_mkdir_before trace는 의도적으로 seq22417에서 끝나므로 Reviewer가 제안한22418–22421을 그 파일에서 읽을 수 없다. staging_parent_sync_before trace의 실제22417–22422는 mkdir-before → audit mkdir → open-before .hrn → audit open → open-after .hrn → fsync-before .hrn이다. 새28개 기존 trace에서 staging mkdir-after0건을 확인했으며, 가장 이른 kill1개는 호출 전까지만 관측하고 나머지27개는 해당 시도 이후를 관측했다. Test source는 수정하지 않았다.

G3 accept: canaries.json에서 named denial10개 값1, child_inheritance named-probes-pass, fullfsync executed를 직접 확인해 path/hash/실제 값을 처분에 남겼다. 이는 R1 이후 Driver의 읽기 전용 확인이며 fullfsync의 물리 영속성이나 OLD data-write 전체를 증명하지 않는다.

G4 accept: 현재 설명은 record shape만 독립 구성하고 candidate_ref/preview request는 product-derived라는 것이다. Frozen pre-R0 REPORT/packet을 소급 수정하지 않고 이 Work와 실행 보고서가 현재 설명을 보충한다.

승인된 batch는 R0=1/controller=6/R1=1/retry=0, 누적 reviewer12/controller26으로 완료됐다. Source/control/input 변경0건이며 실제 실행 창은 954.116초다. 실제 R1 모델/session은 meta.json으로 식별했다. 결과 수락은 아직 Owner에게 남고 전체P2/Work Done·STATUS·C2 활성화·Git 행위로 승격하지 않는다.


## B1–B6 Owner Acceptance And Next P2 Proposal — 2026-10-10

Owner actual request: “좋아. 이번 B1–B6 검증 배치 결과는 수락할게. 남은 P2에서 다음으로 진행할 한정 범위와 완료 기준, 필요한 실행·검토 예산을 제안해줘.”

### Accepted Result

Owner가 고정 binding-prefix-01의 R0→6단계→R1 결과를 수락했다. Source digest는 `b3a4336e8f020ad76ce13702964e90e724c041e85ffaa24c638a8463f25b1142`, 결과는 seed20/20·focused37/37(신규28+회귀9), 실제 collection913 일치, R0/R1 차단0건, retry0이다. `binding-prefix-01/execution-01/completion-result.json` SHA-256은 `3f22e0cf1656968bdb819f14c7f8b72930ba926510501cd99ec3af574ae0f28c`다. 기존 결과/보고서의 acceptance pending은 작성 당시 상태이며 이 명시적 기록이 현재 수락을 보충한다. Frozen 입력·리뷰·결과 원본을 소급 수정하지 않는다.

이 수락은 해당 한정 batch 결과에 적용한다. 전체P2/Work Done, 남은 검증의 면제, C2 활성화·adopter 적용·Git 행위나 다음 구현/실행의 승인은 아니다.

### Recommended Next Slice

다음은 N-01~N-05와 O-01~O-02의 실제 중단·복구 검증이다. N은 새 root colvia, O는 기존 root hv2를 뜻한다. 시작점은 기존 after-release seam으로 만든 S3: 새 release/receipt는 완전하고 B0/O는 그대로이며 N은 아직 없다. 실행은 동일 plan/token/candidate의 명시적 recovery로 시작한다.

범위는 N exclusive create0600, write 전후와1/mid/L−1 short-write, executable mode 변경 전 file sync, fchmod0755 전후, mode 변경 후 file sync와 root sync, exact O의 unlink 전후와 후속 root sync다. 정상 경로의 before/after16개와 추가 short-write3개, 신규19개를 예상한다. Zero-byte는 exclusive open 직후 중단으로 관측한다. 실제 event/path/occurrence·같은 경로의 첫/두 번째 sync를 authoring에서 고정한다. 읽기 함수·fstat 내부 중단, 새 손상/alias/경쟁 사례를 이 숫자에 숨기지 않는다.

신규 상한24개 + 기존 transition_prefix_01~09 회귀9개로 focused 상한33개를 제안한다. 현재 예상은19+9=28개다. 예상19와 확정 ID를 구분하며 실제 호출을 빠짐없이 묶는 데24개를 넘기면 생략하지 않고 재제안으로 멈춘다. B1–B6 신규28개 전부나 D3 전체73개를 근거 없이 재실행하지 않는다.

수정 범위는 tests/test_entry_window_transition.py의 새 test-local helper/사례와 이 Work 기록이다. 기존101개 product test 본문, 기존 helper·공용 child·factory, 제품, observer/controller/policy/oracle은 유지한다. 제품/제어 변경이나 기존 테스트 수정이 필요하면 별도 범위로 보고한다. 이전 B1–B6 검토의 비차단 의견을 이번 명목으로 자동 반영하지 않는다.

### Completion Criteria

1. S3 준비 상태와 실제 각 호출의 event/path/occurrence, before/after 예상 bytes/mode/namespace를 유한 목록으로 고정한다. Observer의 의도한 SIGKILL과 마지막 완전한 event를 확인한다. 두 번의 N file sync와 root sync는 각각 구분한다.
2. N은 생성 전 부재, 생성 후 완전한 write 전까지 정확한 canonical launcher prefix0600, chmod 후 완전한 bytes0755여야 한다. O는 unlink 전 정확한 기존 bytes/mode로 남고 unlink 후 부재여야 한다. 모든 선택 중단 지점에서 B0가 유지되고 receipt/release·일반 파일·format·truth 상태는 보존돼야 한다.
3. 고정 동일 요청으로 후속 recovery1회를 실행하여 N0755/O부재/B1 mode0600/binding.next 부재에 도달하고, 허용한 launcher/binding/staging 변화 밖의 전체 fixture bytes/type/mode를 보존한다. 새로운 fault 뒤 반복 retry 루프는 추가하지 않는다.
4. 기존처럼 빈 typed truth/no active Work fixture로 제한한다. Product 결과의 not-applicable과 파일 snapshot 보존을 구분하며 실제 local/parent/worker Work 보존을 주장하지 않는다. 중단 시 returncode와 snapshot 동등성이 단언 기반인지 별도 저장값인지 결과 보고에서 구분한다.
5. 확정 selection이 실제 collection에 각1회 존재하고 모두 pass해야 한다. Failure/error/skip/expected failure/미시작/미완료0, 입력 전후 동일성 PASS, R0/R1 지적 처분 및 Owner의 이 한정 결과 수락이 완료 조건이다. 통과만으로 전체P2를 완료하지 않는다.

### Proposed Execution And Review Budget

| 항목 | 제안 상한 |
| --- | --- |
| Authoring | 새 후보1개, 테스트·사례표·명령·입력 고정 및 정적 검사. 실제 호출 제외 |
| R0 / R1 | fresh no-tool Claude 각1회·각20분, 합계40분 |
| Controller | 새 비-Git 경계의 acquire/canary/base collect/seed20 smoke/entry collect/focused, 총6회 |
| Controller 시간 | acquire/canary/두 collect 각300초, smoke/focused 각1,200초: 합계60분 |
| 전체 실행·검토 창 | R0 시작부터120분, 외곽 대기·정리·기록20분 포함 |
| 자동 보정·재시도 | 0회 |

B1–B6 batch의 실제 focused37은395.410초, prefix 회귀9개는 각11.051~13.244초였다. 이 수치는 다음 budget 판단의 참고값이며 새 사례 시간의 보장이 아니다. 작성 완료 때 새 사례 수·경로와 고정 runtime을 기준으로 보수적 시간 투영을 다시 제시한다. Parent umask0022는 각 controller 시작 전 확인·기록하고 다르면 값을 바꾸지 않고 중단한다. Canary 세부 결과·실제 collection bytes·start records도 다음 R1 packet에 포함할 수 있도록 입력 구성을 고정한다.

현재 누적 reviewer12/controller26이므로 승인 시 다음 누적 상한은14/32다. 이전 실행 창과 소진 focused-p2/correction 슬롯을 전용하지 않는다. 새 비-Git 실행 root는 승인된 agent-worktrees 경로 아래에서 authoring 단계에 부재·미등록·ancestor를 확인하고 정확한 path로 제시한다. 지금 root 생성·테스트 작성·실행·Claude 호출은 하지 않는다.

다음 승인 단위는 테스트 작성·정적 확인·입력 확정까지다. 그 결과의 정확한 ID/명령/hash를 보고한 뒤 실제 R0→6단계→R1 및 private 자료 전송을 별도로 승인받는다. 첫 뜻밖의 실패·입력 불일치·시간/출력/보존 한계에서 보존 후 중단한다. 이 두 gate는 Owner가 요청한 한정 계획과 기존 실행 경계를 유지하기 위한 것이다.

### Remaining P2 And Custody

S1/S2/S3 전체 physical matrix, B7 empty-directory retirement, four-executor/all-writer·late-lock, Git admission/ignore, 실제 local/parent/worker와 mixed-history lifecycle, D3의 남은 fault 조합은 별도 미완료다. 현재 제품은 binding staging을 자동 제거하지 않으므로 B7을 새 rmdir 기능 추가로 해석하지 않는다. P3/P4/C2·실제 adopter·물리 durability/fullfsync도 별도다.

Source/control checkout은 진행 중인P2에 필요해 유지한다. b04 실행 자료의 구체적인 다음 소비자는 N/O selector 작성에 사용할 prefix01~09의 실제 observer trace/timing이다. Selector/입력을 고정하고 관련 검토가 끝나면 재현 가능한 실행 환경·중복 raw의 보존 필요를 재평가한다. 과거 수락 결과와 고유 실패/복구 자료의 보존은 별도이며 이번 제안으로 checkout 이동·삭제나 새 실행 환경 생성을 하지 않는다. STATUS·commit·push·Work Done은 변경하지 않는다.


## N/O Test Authoring And Fixed Execution Inputs — 2026-10-10

Owner actual request: “좋아. 제안한 N-01~N-05, O-01~O-02 범위의 테스트 작성·정적 확인·실행 입력 확정까지 승인할게. 완료 후 정확한 테스트 목록과 명령, 입력 해시를 보고해줘. 실제 실행과 Claude 전송은 그때 별도로 승인할게.”

### Authored Scope And Static Evidence

tests/test_entry_window_transition.py에 새 test-local helper1개와 N/O 테스트19개를 추가했다. N-01 open2, N-02 write-before/full/1/mid/L−1의5, N-03 chmod 전 file sync2, N-04 fchmod2, N-05 chmod 후 file/root sync4, O-01 unlink2, O-02 root sync2다. 정상 경로16개+short-write3개이고 기존 transition_prefix_01~09 회귀9개를 더해 focused28개다. 승인 상한24신규/33focused 이내다.

기존 named after-release seam으로 S3를 준비한다. 초기 전체 snapshot에 inventory/payload·literal receipt shape·directory로 열거한 정확한 delta만 더해 준비 상태를 단언한다. Candidate payload/ref와 preview request는 product-derived이며 완전히 독립된 product 의미 oracle이라는 주장은 하지 않는다. 새N 부재, exactO0755, B0, 완전한 release/receipt와 empty switch staging으로 시작한다.

각 실제 SIGKILL은 마지막 완전한 event·PID/PGID·global occurrence와16개 호출의 순서 prefix에 결속한다. Open flags0600, write length, chmod0755, N0600 prefix→full0755, O unlink 전후와 B0 및 나머지 bytes/type/mode를 단언한다. 동일 request/token/candidate의 후속 recovery1회로 N0755/O부재/B1 mode0600/binding.next 부재 및 exact empty binding staging에 도달해야 한다. Root mode도 보존한다. Returncode·중단 snapshot 동등성은 테스트 단언이며 별도 raw 저장값이 있다고 보고하지 않는다.

Pinned Python3.14.7 -I -S -B AST/compile 정적 검사 exit0. 기존101개 test 본문·기존 helper·globals/child 문자열·다른 클래스·factory는 AST가 같다. 제품·controls11·base source101은 hash가 같고 entry source102 중 테스트1개만 바뀌었다. Runtime/Git/system config와 이전 준비/수락 자료120개 파일도 보존했다. 수집·test/controller·Claude/auth 호출은0회다.

첫 정적 검사에서 검사기의 AST 목록이 새 helper의 로컬 expected dictionary Delete 구문을 허용하지 않아 중단됐다. 그 검사기를 보완한 뒤 exit0을 확인했으며 후보 source는 바뀌지 않았다. 이는 product/test 실행 실패나 batch 재시도가 아니다.

기존 b04 prefix07 initial-apply trace와16개 event/path/occurrence가 정적으로 일치한다. Root fsync1은 admission,2는 N publication,3은 O retirement이며 N file sync1/2는 chmod 전/후다. 새 테스트는 named S3에서 recovery로 진입하므로 동일 selector 도달·복구·시간·PASS는 아직 unavailable이다. 실제 실행에서 전체 순서와 occurrence를 모두 확인해야 한다.

### Exact Candidate And Commands

[작성 보고서](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/REPORT.md), [전체 ID28개](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/test-selection.json), [사례별 selector/상태](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/case-matrix.json), [정확한 명령](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/COMMANDS.md), [실행 계획](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/execution-plan.json)에 고정했다.

- Source102 digest: `65abd844fa49ccce5d106390eec7c8631e338fcb11ac755f11b4186450601635`.
- Test file SHA-256: `33d6e5c4c54991b1279d4bc76aec34eba5ae3fd782836b32cdc8fb7acc85e560`.
- Git base: `238514686078ce1564010a7b69013f48a635c57c`; tracked diff SHA-256: `c3c0a89c3c641e17e3376edbc09950cd1e923a67ac3063e01a038dc6c2fe8b66`. 테스트는 untracked여서 diff 밖이며 source map/full packet으로 별도 식별한다.
- R0 packet SHA-256: `883da3430947f51eb78c6dbb3890c4dcbd1cd4788fee08d27f05329d7cdaa906`, 937273bytes. 아직 전송하지 않았다.
- 준비 입력19개 manifest SHA-256: `a3b3efe0f5eb935d9ffcd6fea119e2a2a7fb59814dc17bceb19d957cd43a76a7`; [manifest](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/prepared-manifest.json). 네 invocation/selection/plan 등의 full hash는 보고서와 manifest에 있다.

Factory156=control24+old fixture1+product120+foundation11, default776을 합한 예상 collection932는 정적 추정이다. 실제 collect canonical bytes/hash/ordered ID/occurrence가 고정 기대값과 일치해야 다음 단계로 진행한다. 기존 default 중복을 그대로 유지하고 focused28개는 각1회여야 한다. 불일치 시 expectation을 바꾸지 않고 중단한다.

새 비-Git 실행 root 후보는 `/Users/kyungseo/dev-home/agent-worktrees/hv2-reference-private-colvia-launcher-verification-20261010-b05`다. 부재·미등록·상위 Git/authority 부재를 확인했고 생성하지 않았다. 고정 순서는 R0→acquire→canary→base collect→seed20 smoke→entry collect→focused28→R1이다. 기존 사용 슬롯이나 correction 슬롯을 전용하지 않는다.

### Budget And Separate Execution Gate

별도 승인 후 R0 시작부터 최대120분: fresh no-tool R0/R1 각20분=40분, controller6회 합계60분(acquire/canary/두 collect 각300초, smoke/focused 각1200초), 외곽 대기/정리/기록20분이다. 자동 보정·재시도0회. 누적 제안 상한 review14/controller32이며 현재 실행은0회다. 기존 prefix9 실측108.795초와 최대13.244초, 추가 준비 proxy5.781초를 새19개 각각에 적용해470.270초,50% 여유 포함705.405초를 추정했다. Focused child1180초 대비474.595초 여유지만 보장 상한이 아니다. Timeout이면 보존 후 중단한다.

각 controller 준비/시작 직전에 parent umask0022를 확인하고 기록하며 다른 값을 변경하지 않는다. 각 Claude 호출 전 subscription claude.ai/firstParty/pro 경로를 재확인하고 다르거나 불명확하면 중단한다. Opus는 요청 alias이며 실제 model/session/tool 제약은 실행 결과에서 기록한다. R1은 실제 결과 뒤 생성하고 six start records/umask, canary 개별 denial/inheritance, actual collection bytes/selected/executed와 R0 처분을 포함한다. 아직 R1 packet/hash는 없다.

실제 R0→6단계→R1과 private 코드·DR·test·결과의 Claude 전송은 별도 Owner 승인 대상이다. 첫 뜻밖의 실패·입력/수집 불일치·timeout·출력/보존 한계에서 보존 후 중단하며 자동 수정·재시도·selection 축소·slot 교체는 없다.

### Limits And Preservation

빈 typed truth/no active Work fixture의 파일 보존이며 local content comparison은 not-applicable이다. 실제 local/parent/worker Work나 adopter 보존, fullP2/S1S2S3/B7/four-executor·all-writer, 새 alias/경쟁/fault 조합, P3/P4/C2, physical durability/fullfsync는 별도다. 기존 B1–B6 테스트28개 전체나 D3 전체73개를 재실행 대상으로 추가하지 않았다.

Source/control checkout은 진행 중인 P2에 필요해 유지한다. 새 입력/packet의 소비자는 Owner exact 승인과 계획된 R0/R1이며 이전 packet의 exact test section+이번 patch+새 packet이 복원 경계를 이룬다. 새 full source/before tree는 없다. b04 raw trace의 selector 검토 소비가 끝난 후 재현 가능 환경·중복 raw 보존을 재평가한다. 기존 Work만 추가 기록하고 STATUS·commit·push·Work Done은 바꾸지 않는다.


## N/O Authorized Execution Stopped At R0 — 2026-10-10

Owner actual request: “좋아. 고정한 N/O 후보의 R0 → 6단계 실행 → R1과 private 자료의 Claude 전송을 승인해. 최대 120분, 자동 보정·재시도 0회로 진행하고 실패나 입력 불일치가 나오면 보존한 뒤 멈춰서 보고해줘.”

### Actual Execution And Stop

고정 N/O 후보의 R0 호출이 Claude session 사용 한도로 실패하여 승인한 stop rule에 따라 중단했다. 실제 검토 verdict는 없고 controller6단계와 R1은 시작하지 않았다. 자동 보정·재시도는0회다.

## Actual Failure

- R0 시작: `2026-10-10T12:16:53.775599+00:00`; 종료: `2026-10-10T12:16:56.059178+00:00`.
- Exit1, is_error=true, 소요2.283초. CLI2.1.296의 오류 원문은 아래와 같다.

> You've hit your session limit · resets 10:50pm (Asia/Seoul)

CLI가 안내한 reset은 2026-10-10 22:50 Asia/Seoul이다. 해당 시각에 자동 재개하지 않는다. API result의 duration_api_ms=0, modelUsage={}였으며 이것을 private packet의 미전송이나 무과금 보증으로 해석하지 않는다. 실제 검토 응답이 없어 코드 결함 여부나 reviewer 승인 여부는 판단할 수 없다.

Auth는 호출 전 claude.ai/firstParty/pro subscription임을 확인했다. 요청 model alias는 opus, startup-reported model은 `claude-opus-5-5`, session은 `7ee114b2-2df7-4534-9b5f-0541ef4ec377`다. 정상 검토를 수행한 실제 모델로 주장하지 않는다. Tools/MCP/실제 tool use0, 종료 process group 부재, 호출 전후 입력 동일성 PASS다.

## Preserved State

Source digest `65abd844fa49ccce5d106390eec7c8631e338fcb11ac755f11b4186450601635`와 test SHA-256 `33d6e5c4c54991b1279d4bc76aec34eba5ae3fd782836b32cdc8fb7acc85e560`는 그대로다. Frozen manifest19개·source maps·controls·runtime·기존 근거의 해시를 다시 확인했다. 신규 실행 root b05는 만들지 않았으며 테스트 수집·smoke·focused·R1은0회다. 제품·제어·테스트 source 변경0건, STATUS·commit·push·Work Done 변경0건이다.

[중단 결과](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/execution-01/stopped-result.json), [호출 metadata](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/review-r0/meta.json), [오류 원문](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/review-r0/review.md), [고정 후보 보고서](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/REPORT.md), [고정 입력](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/prepared-manifest.json).

누적 reviewer invocation은13회(이번 실패1회 포함), 완료된 review는기존12회, controller는기존26회다. 이번 허용 창은 실패로 중단됐으며 아직 남은 시간이나 R1 슬롯을 새 R0 승인으로 전용하지 않는다.

## Recovery Boundary

권장 경로는 사용 한도 해제 뒤 동일 후보의 hash를 확인하고 새 R0부터 재개하는 것이다. 실패한 호출 자료를 덮어쓰지 않도록 새 review output/window와 정확한 호출 예산을 제시해 Owner의 재개 승인을 받아야 한다. 이 기록은 재시도나 새 승인이 아니며 다른 model/API billing 경로로 바꾸지 않는다. 현재 후보의 재작성 필요를 입증하는 결과도 없다.

실패 기록의 소비자는 Owner의 원인 확인과 재개 계획이다. Source/control checkout은 진행 중인 P2에, b04 trace는 아직 끝나지 않은 selector 검토에 필요해 유지한다. 새 b05 root는 부재라 정리 대상이 없다. 재개 계획과 처분이 확정되면 중복 raw의 필요를 재평가한다.

### Reviewer Service Response — Verbatim, Not A Review Verdict

You've hit your session limit · resets 10:50pm (Asia/Seoul)

### Driver Disposition And Owner Boundary

needs-user for resumption: subscription 사용 한도가 원인인 서비스 실행 실패로 분류한다. 코드 지적이나 승인 verdict로 취급하지 않는다. 승인한 첫 실패 중단 조건을 적용하여 R0 호출1회 뒤 멈췄고 source 보정·자동 재시도·controller·R1은0회다. 프로세스 종료와 입력 보존을 확인하고 결과를 기록했다. 자동 review retry, API/모델 대체, 남은 R1 slot 전용을 하지 않는다. 사용 한도 해제 뒤 새 실행/output/window 계획과 별도 Owner 승인으로 재개할 수 있다. 이 실패 기록은 검증 통과 checkpoint·결과 수락·전체P2 완료가 아니다.


## N/O Resume-01 Stopped At R0 — 2026-10-10

Owner actual request: “한도가 해제됐으니 동일한 N/O 후보로 새 R0부터 재개해줘. 기존 실패 기록은 보존하고, 새 실행 창에서 R0 → 6단계 → R1과 Claude 전송을 승인할게. 최대 120분, 자동 보정·재시도 0회로 진행하고 실패나 입력 불일치가 나오면 멈춰서 보고해줘.”

### Actual Execution And Stop

별도 재개 승인으로 시작한 새 실행 창에서도 동일 N/O 후보의 R0 호출이 Claude session 사용 한도로 실패하여 중단했다. 기존 실패 기록은 그대로 보존했다. 실제 검토 verdict는 없고 controller6단계와 R1은 시작하지 않았다. 자동 보정·재시도는0회다.

## Actual Failure

- R0 시작: `2026-10-10T12:27:28.417399+00:00`; 종료: `2026-10-10T12:27:30.703685+00:00`.
- Exit1, is_error=true, 소요2.286초. CLI2.1.296의 오류 원문은 아래와 같다.

> You've hit your session limit · resets 10:50pm (Asia/Seoul)

CLI가 안내한 reset은 2026-10-10 22:50 Asia/Seoul이다. 해당 시각에 자동 재개하지 않는다. API result의 duration_api_ms=0, modelUsage={}였으며 이것을 private packet의 미전송이나 무과금 보증으로 해석하지 않는다. 실제 검토 응답이 없어 코드 결함 여부나 reviewer 승인 여부는 판단할 수 없다.

Auth는 호출 전 claude.ai/firstParty/pro subscription임을 확인했다. 요청 model alias는 opus, startup-reported model은 `claude-opus-5-5`, session은 `706f62c2-dbd8-4568-bd23-ec8d85176eae`다. 정상 검토를 수행한 실제 모델로 주장하지 않는다. Tools/MCP/실제 tool use0, 종료 process group 부재, 호출 전후 입력 동일성 PASS다.

## Preserved State

Source digest `65abd844fa49ccce5d106390eec7c8631e338fcb11ac755f11b4186450601635`와 test SHA-256 `33d6e5c4c54991b1279d4bc76aec34eba5ae3fd782836b32cdc8fb7acc85e560`는 그대로다. 원본 frozen 입력19개와 재개 envelope4개·source maps·controls·runtime·기존 실패 기록10개·이전 근거의 해시를 다시 확인했다. 신규 실행 root b05는 만들지 않았으며 테스트 수집·smoke·focused·R1은0회다. 제품·제어·테스트 source 변경0건, STATUS·commit·push·Work Done 변경0건이다.

[중단 결과](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/resume-01/execution-01/stopped-result.json), [호출 metadata](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/resume-01/review-r0/meta.json), [오류 원문](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/resume-01/review-r0/review.md), [고정 후보 보고서](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/REPORT.md), [고정 후보 입력](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/prepared-manifest.json), [보존한 이전 실패](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/execution-01/REPORT.md).

누적 reviewer invocation은14회(이전 실패1회와 별도 승인된 이번 실패1회 포함), 완료된 review는기존12회, controller는기존26회다. 이번 창의 R0 호출은1회, 자동 재시도는0회다. 이번 허용 창은 실패로 중단됐으며 아직 남은 시간이나 R1 슬롯을 새 R0 승인으로 전용하지 않는다.

## Recovery Boundary

현재 연결된 Claude CLI가 한도 해제를 반영한 뒤 동일 후보의 hash를 확인하고 새 R0부터 재개하는 경로가 남는다. 이번 호출 시점에는 여전히 한도 오류를 반환했으며 인증 경로 자체는 subscription claude.ai/firstParty/pro였다. 실패한 호출 자료를 덮어쓰지 않도록 새 review output/window와 정확한 호출 예산을 제시해 Owner의 재개 승인을 받아야 한다. 이 기록은 재시도나 새 승인이 아니며 다른 model/API billing 경로로 바꾸지 않는다. 현재 후보의 재작성 필요를 입증하는 결과도 없다.

실패 기록의 소비자는 Owner의 원인 확인과 재개 계획이다. Source/control checkout은 진행 중인 P2에, b04 trace는 아직 끝나지 않은 selector 검토에 필요해 유지한다. 새 b05 root는 부재라 정리 대상이 없다. 재개 계획과 처분이 확정되면 중복 raw의 필요를 재평가한다.

### Reviewer Service Response — Verbatim, Not A Review Verdict

You've hit your session limit · resets 10:50pm (Asia/Seoul)

### Driver Disposition And Owner Boundary

needs-user for resumption: subscription 사용 한도가 원인인 서비스 실행 실패로 분류한다. 코드 지적이나 승인 verdict로 취급하지 않는다. 별도 재개 승인의 새 창에서 첫 실패 중단 조건을 적용하여 R0 호출1회 뒤 멈췄고 source 보정·자동 재시도·controller·R1은0회다. 프로세스 종료와 입력 보존을 확인하고 결과를 기록했다. 자동 review retry, API/모델 대체, 남은 R1 slot 전용을 하지 않는다. 사용 한도 해제 뒤 새 실행/output/window 계획과 별도 Owner 승인으로 재개할 수 있다. 이 실패 기록은 검증 통과 checkpoint·결과 수락·전체P2 완료가 아니다.


## N/O Resume-02 Stopped At R0 — 2026-10-10

Owner actual request: “Claude CLI에서도 한도가 해제된 걸 확인했어. 동일한 N/O 후보로 새 R0 → 6단계 → R1과 Claude 전송을 다시 승인할게. 기존 실패 기록은 보존하고, 새 창에서 최대 120분·자동 보정 및 재시도 0회로 진행해줘. 실패나 입력 불일치가 나오면 즉시 멈춰서 보고해줘.”

### Actual Execution And Stop

별도 재개 승인으로 시작한 새 실행 창에서도 동일 N/O 후보의 R0 호출이 Claude session 사용 한도로 실패하여 중단했다. 기존 실패 기록은 그대로 보존했다. 실제 검토 verdict는 없고 controller6단계와 R1은 시작하지 않았다. 자동 보정·재시도는0회다.

## Actual Failure

- R0 시작: `2026-10-10T12:36:25.899451+00:00`; 종료: `2026-10-10T12:36:28.182447+00:00`.
- Exit1, is_error=true, 소요2.283초. CLI2.1.296의 오류 원문은 아래와 같다.

> You've hit your session limit · resets 10:50pm (Asia/Seoul)

CLI가 안내한 reset은 2026-10-10 22:50 Asia/Seoul이다. 해당 시각에 자동 재개하지 않는다. API result의 duration_api_ms=0, modelUsage={}였으며 이것을 private packet의 미전송이나 무과금 보증으로 해석하지 않는다. 실제 검토 응답이 없어 코드 결함 여부나 reviewer 승인 여부는 판단할 수 없다.

Auth는 호출 전 claude.ai/firstParty/pro subscription임을 확인했다. 요청 model alias는 opus, startup-reported model은 `claude-opus-5-5`, session은 `253fb0b3-7683-45c3-ad25-85f9a237843a`다. 정상 검토를 수행한 실제 모델로 주장하지 않는다. Tools/MCP/실제 tool use0, 종료 process group 부재, 호출 전후 입력 동일성 PASS다.

## Preserved State

Source digest `65abd844fa49ccce5d106390eec7c8631e338fcb11ac755f11b4186450601635`와 test SHA-256 `33d6e5c4c54991b1279d4bc76aec34eba5ae3fd782836b32cdc8fb7acc85e560`는 그대로다. 원본 frozen 입력19개와 재개 envelope4개·source maps·controls·runtime·기존 실패 및 재개 기록25개·이전 근거의 해시를 다시 확인했다. 신규 실행 root b05는 만들지 않았으며 테스트 수집·smoke·focused·R1은0회다. 제품·제어·테스트 source 변경0건, STATUS·commit·push·Work Done 변경0건이다.

[중단 결과](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/resume-02/execution-01/stopped-result.json), [호출 metadata](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/resume-02/review-r0/meta.json), [오류 원문](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/resume-02/review-r0/review.md), [고정 후보 보고서](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/REPORT.md), [고정 후보 입력](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/prepared-manifest.json), [보존한 최초 실패](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/execution-01/REPORT.md), [보존한 resume-01 실패](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/resume-01/execution-01/REPORT.md).

누적 reviewer invocation은15회(이전 실패2회와 별도 승인된 이번 실패1회 포함), 완료된 review는기존12회, controller는기존26회다. 이번 창의 R0 호출은1회, 자동 재시도는0회다. 이번 허용 창은 실패로 중단됐으며 아직 남은 시간이나 R1 슬롯을 새 R0 승인으로 전용하지 않는다.

## Recovery Boundary

Owner는 Claude CLI에서 한도 해제를 확인했다고 알렸지만, 이번 고정 opus 요청은 여전히 같은 오류를 반환했다. 인증 경로는 subscription claude.ai/firstParty/pro였고 정상 검토는 없었다. 사용자 확인 요청과 이 고정 검토 요청의 model/account/context 차이는 조사하지 않았으므로 원인을 추정하지 않는다. 추가 재시도보다 그 차이를 읽기 전용으로 확인하는 계획이 다음 후보이며, 이번에는 실패 시 중단 지시에 따라 새 진단 호출·설정 변경을 하지 않는다. 실패한 호출 자료를 덮어쓰지 않도록 새 review output/window와 정확한 호출 예산을 제시해 Owner의 재개 승인을 받아야 한다. 이 기록은 재시도나 새 승인이 아니며 다른 model/API billing 경로로 바꾸지 않는다. 현재 후보의 재작성 필요를 입증하는 결과도 없다.

실패 기록의 소비자는 Owner의 원인 확인과 재개 계획이다. Source/control checkout은 진행 중인 P2에, b04 trace는 아직 끝나지 않은 selector 검토에 필요해 유지한다. 새 b05 root는 부재라 정리 대상이 없다. 재개 계획과 처분이 확정되면 중복 raw의 필요를 재평가한다.

### Reviewer Service Response — Verbatim, Not A Review Verdict

You've hit your session limit · resets 10:50pm (Asia/Seoul)

### Driver Disposition And Owner Boundary

needs-user for resumption: subscription 사용 한도가 원인인 서비스 실행 실패로 분류한다. 코드 지적이나 승인 verdict로 취급하지 않는다. 별도 재개 승인의 새 창에서 첫 실패 중단 조건을 적용하여 R0 호출1회 뒤 멈췄고 source 보정·자동 재시도·controller·R1은0회다. 프로세스 종료와 입력 보존을 확인하고 결과를 기록했다. 자동 review retry, API/모델 대체, 남은 R1 slot 전용을 하지 않는다. 사용 한도 해제 뒤 새 실행/output/window 계획과 별도 Owner 승인으로 재개할 수 있다. 이 실패 기록은 검증 통과 checkpoint·결과 수락·전체P2 완료가 아니다.


## N/O Resume-03 Runtime And Review Completed — 2026-10-10

Owner actual request: “22:50 이후 /usage에서 현재 세션 한도가 초기화된 걸 확인했어. 동일한 N/O 후보로 새 R0 → 6단계 → R1과 Claude 전송을 승인할게. 기존 실패 기록은 보존하고, 새 창에서 최대 120분·자동 보정 및 재시도 0회로 진행해줘. 실패나 입력 불일치가 나오면 즉시 멈춰서 보고해줘.”

승인된 동일 N/O 후보의 R0 → 6단계 → R1을 완료했다. R0·R1 모두 blocker 0, smoke 20/20, focused 28/28(신규19 + 회귀9) PASS다. 자동 보정·재시도는0회이며 이번 결과에 대한 Owner 수락은 아직 없다.

## Actual Results

| 단계 | 결과 | 초 |
| --- | --- | --- |
| acquire-base | PASS | 0.852 |
| canary-base | PASS | 0.665 |
| collect-base | PASS | 0.461 |
| smoke-base | PASS | 64.841 |
| collect-p2 | PASS | 0.466 |
| focused-p2 | PASS | 294.268 |

Baseline collection은776개, 후보 collection은932개다. 후보 collection SHA-256 `9f49a5e2836b11cb97f301864104a1eb48a4489edd4c9a15b908e51120cc2479`가 고정 기대값과 일치했다. Smoke와 focused 모두 실패·오류·skip·미시작·미완료0이다. 신규19개는 N-01~N-05·O-01~O-02의16개 호출 경계와 short write3개를 검사했다.

19건 모두 동일 요청으로1회 복구해 `updated`와 B1 최종 상태를 확인했다. SIGKILL·정확한 S3 준비 delta·중단 시점 전체 fixture/B0 보존·lock-free는 통과한 테스트 단언에 근거한다. 별도 killed snapshot·child returncode 원본을 저장한 결과로 주장하지 않는다.

Recovery 로그에서 기존 colvia를 여는 flags258(`O_RDWR|O_NOFOLLOW`)에 O_CREAT/O_TRUNC가 없고, zero 두 건·short one/middle/last의 write 요청이 각각5702·5702·5701·2851·1바이트임을 관측했다. 최종 바이트 일치 단언과 함께 prefix 이후 잔여 쓰기를 뒷받침한다. ftruncate/lseek는 hook 밖이므로 truncate 부재를 모든 호출에 대한 직접 관측으로 주장하지 않는다. Recovery의 N/O 이후 전체 resync·binding publication 순서는 이번 발췌로 검증하지 않았다.

Canary는 named denial10개, child inheritance, non-git/primary/linked-worktree topology를 통과했다. OLD_MODE는 metadata-write 거부 범위다. 여섯 launch 모두 사전·spawn 직전 umask0022를 기록했고, controller·review 모두 자연 종료와 process group 부재, 입력 검증 PASS를 기록했다.

## Review Identity And Disposition

두 검토 모두 Claude CLI2.1.296, claude.ai/firstParty/pro subscription 경로, 실제 모델 `claude-opus-5-5`, fresh session, tools/MCP/실제 tool use0으로 수행했다. Codex Driver와 다른 모델이지만 같은 제공 packet에 의존한 검토이며 reviewer는 hash를 재계산하지 못했다. Driver의 입력 검증과 no-tool reviewer의 정적 판단을 구분한다.

- R0: session `58a7f047-143b-4e62-b897-d4b1da934810`, 188.036초, exit0, blocker0. [원문](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/resume-03/review-r0/review.md), [Driver 처분](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/resume-03/execution-01/r0-disposition.json).
- R1: session `4ce85fc2-445e-4fc0-adb8-cb5ac9d6ecff`, 90.835초, exit0, blocker0. [원문](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/resume-03/review-r1/review.md), [Driver 처분](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/resume-03/execution-01/r1-disposition.json).

R0 조건은 실행 근거와 운영 gate로 닫았다. R1 잔여 격차는 위 근거 한계로 accept했다. 소스 수정·추가 실행은 하지 않았다. Reviewer 판단을 Owner 수락이나 전체P2 완료로 전환하지 않는다.

## Exact Inputs And Budget

- Source digest: `65abd844fa49ccce5d106390eec7c8631e338fcb11ac755f11b4186450601635`.
- Test SHA-256: `33d6e5c4c54991b1279d4bc76aec34eba5ae3fd782836b32cdc8fb7acc85e560`.
- Base revision: `238514686078ce1564010a7b69013f48a635c57c`; tracked base diff SHA-256: `c3c0a89c3c641e17e3376edbc09950cd1e923a67ac3063e01a038dc6c2fe8b66`.
- R0 packet: `ba6bd2a636673bea800f704469e7ac26037469e9f6063a02c279a947b06dd270`.
- R1 packet: `c89957e3e149e34d99f2d8ebe414e826cc4942eaa12a7e0c6a763de4f622f2e3`.

[정확한 실행 명령·cwd·runtime·상한](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/resume-03/execution-plan.json), [실행 결과](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/resume-03/execution-01/result.json), [19건 관측](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/resume-03/execution-01/case-observations.json), [R1 입력 목록](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/resume-03/review-r1-inputs.json). Runtime은 고정 CPython3.14.7이고 controller는300초4회·1200초2회, review는1200초2회 상한이다. 총 창은 `2026-10-10T13:55:09.098873+00:00`부터120분이며 R1 종료까지733.525초(약12.23분)였다. 이번 창의 reviewer2회/controller6회로 승인 상한을 지켰다. 누적 reviewer 호출17회는 완료14회와 이전 한도 실패3회이며, controller 호출은32회다.

## Preservation And Remaining Scope

원본 고정 입력19개와 이번 재개 입력4개, 이전 실패 관련40개 파일, source·controls·runtime·기존 근거의 해시를 보존했다. 제품·테스트·control 변경0건, STATUS·commit·push·Work Done 변경0건이다. 본 Work에는 실행 및 검토 기록만 추가한다.

Nonempty truth나 local/parent/worker Work 보존, 전원 손실 내구성, S1/S2 전체 matrix·B-07·4-executor·P3/P4·실제 adopter 적용은 이번 결과로 검증되지 않았다. Full P2는 미완료다. 다음 단계는 이 N/O 범위 결과의 Owner 판단과 남은 P2 범위 확정이다.

Source/control checkout은 진행 중인 P2 때문에 유지한다. 새 b05 실행 경계는 이 결과의 Owner 검토에 필요한 trace를 읽을 수 있도록 유지하며, 결과 처분과 다음 범위가 정해지면 남은 소비자를 확인해 정리한다. Raw trace·실행 복사본을 기본 영구 산출물로 추가하지 않는다. 기존 실패 기록은 요청대로 그대로 보존했다.

### R0 Reviewer Response — Verbatim

# N/O Resume-03 R0 검토 결과

**결론: 고정 후보로 6단계 진행을 막는 구체적 blocker는 찾지 못했습니다.** 다만 이 판단은 packet 본문만 읽은 정적 추론이며, 해시·바이트·수집 수는 재계산하지 못했습니다. 아래 R-1~R-6은 소스 수정 없이 R1 증거나 운영 게이트로 닫아야 하는 조건입니다.

## 1. 증거 구분

| 구분 | 내용 | 한계 |
| --- | --- | --- |
| 정적 추론 (이번 검토) | patch, 전체 테스트 파일, `product.py` 전문, 발췌된 jsonio/workspace, controls를 읽고 추적 | SHA-256은 하나도 재계산하지 못함. `work.py`, `intent.py`, `cli.py`와 jsonio/workspace 나머지 본문은 packet에 없음 |
| 과거 실행 trace | b04 `prefix_07` initial-apply 이벤트 16행, prefix 9개 소요 시간, d3 proxy 5.781초 | 다른 후보 바이트·다른 진입 경로(initial apply)의 기록이며 이 후보의 실행 증거가 아님 |
| 새 런타임 증거 | 없음 | 수집·테스트·controller 0회. 기대 932와 hash `9f49a5e2…`는 기대값일 뿐임 |

## 2. 정적으로 확인된 항목

- **patch 형태**: `@@ -1216,6 +1216,193` 순수 삽입 187행(헬퍼 1 + 테스트 19)이고 삭제 행이 없습니다. 기존 101개 본문·헬퍼·product·controls 11개가 "불변"이라는 것은 이 형태와 일치하지만, 해시 동일성은 `static-checks.json`의 주장으로만 확인됩니다.
- **수집 수**: packet의 `factory_ids`를 직접 세면 Control 24, Old 1, Product 120(기존 101 + 신규 19), Foundation 11로 156입니다. default 776은 세지 못했고, 776 + 156 = 932 산술만 맞습니다.
- **ID 순서**: 신규 19개의 삽입 위치(`test_late_new_entry…` 뒤, `test_live_collision…` 앞)와 내부 알파벳 순서가 `loadTestsFromTestCase` 정렬과 일치합니다.
- **focused 28개**: 19 + 9, 중복 없음, 모두 factory ID에 존재합니다. `focused`/`collect`의 `p2` slot은 `ENTRY_MODE_SLOTS`에 있습니다.
- **16 edge와 short 3 대응**: `product.py`의 S3 recovery 경로를 따라가면 `flow`의 16행과 순서·global occurrence가 맞습니다.
  - root fsync 1회차는 `_entry_sync_admission`, 2회차는 N publication, 3회차는 O retirement입니다.
  - colvia fsync 1/2회차는 `fchmod` 전후입니다.
  - release가 이미 있으므로 `durable(staging)`은 건너뛰고, `_entry_resync_release`에는 root sync가 없습니다.
  - open flags 2818 = `O_RDWR|O_NOFOLLOW|O_CREAT|O_EXCL`, mode 384/493 = 0600/0755입니다.
- **short write**: observer가 첫 `os.write`를 k바이트로 자르고 `write-after`에서 kill합니다. `requested`는 전체 길이, `written`은 k이며 one/middle/last는 1/2851/5701입니다.
- **selector 구조는 fail-closed**: kill은 정의상 occurrence번째 match에서 일어나므로 `len(matches)==occurrence`는 자명합니다. 실제 보호는 `seen`을 0행부터 세는 `witnessed` 순서 대조, O_CREAT 시작점 1개, 전체 snapshot에서 나옵니다. 앞쪽에 예상 밖 동일 이벤트가 있으면 번호가 밀려 실패합니다.
- **killed prefix와 recovery**: 19개 지점의 기대 상태(N 부재/zero/prefix 0600/full 0600/full 0755, O 유무, B0 바이트 동일, lock free)가 DR의 S3·S3a·S3b·S4·S5 표와 맞습니다. 이후 `--recover` 호출은 1회뿐이고 `updated`, B1 0600, `binding.next` 부재, 빈 entry staging, hv2 부재를 단언합니다.
- **6단계 계획**: resume-03의 argv·input hash·cwd·slot·timeout이 원본 계획과 같습니다. 달라진 것은 review cwd/output과 누적 계수뿐입니다.
- **상한 산술**: 15+2=17, 26+6=32, 2400+3600+1200=7200이고, 외곽 대기 합 3780의 초과분 180은 관리 여유에 들어 있습니다. `ANCESTOR_0..8` 9개 구성도 새 root 경로와 맞습니다.

## 3. 위험과 최소 조치 (소스 수정 불필요)

**R-1. exact S3 delta는 한 번도 실행된 적 없는 가장 강한 새 단언입니다.**
- 기존 binding 테스트는 "initial 항목 보존"만 봐서 추가 항목을 검출하지 않았습니다. 새 `s3 == snapshot`은 처음으로 전체 일치를 요구합니다.
- 암묵 전제는 세 가지입니다: OLD init 직후 `.hrn/locks`, `writer.lock`, `.hrn/staging`(및 init staging)이 이미 존재할 것, release/receipt 파일이 0644이고 디렉터리가 0755일 것(umask 0022 의존), release 안의 `payload/colvia`도 0644일 것.
- 기존 D3 테스트가 `.hrn/locks`와 `.hrn/staging`의 사전 존재를 조건부로 다루고 있어, 첫 번째 전제는 packet 안에서 확정되지 않습니다.
- 어긋나면 거짓 실패이지 거짓 통과는 아닙니다. 다만 19개가 같은 헬퍼를 쓰므로 한꺼번에 실패하고 재시도 0회로 창이 끝납니다.
- 조치: Owner가 이 동반 실패 가능성을 알고 진행합니다. 실패 시 R1 packet에 `failures/` 사본의 실제 S3 snapshot과 기대의 차이 키를 그대로 넣습니다.

**R-2. selector 도달성은 packet에 없는 본문에 의존합니다.**
- `_stable_file`, `_visible_truth`, `_exists`, `classify_target`, `inspect_root`, `write_new_bytes`가 target의 `colvia`나 `.`에 `os.open`/`os.fsync`를 추가로 호출하지 않는다는 것은 확인하지 못했습니다.
- initial-apply trace에서는 그런 호출이 없었지만, recovery 경로는 `_entry_admission` 대신 `_entry_absence_admission(owned_prefix=True)`를 탑니다.
- 어긋나면 `witnessed` 대조나 "requested fault was not observed"로 실패합니다.
- 조치: R1에 19개 kill `.events`의 flow 행(seq, event, path, 번호)을 원문으로 넣어 trace-map 16행과 대조합니다.

**R-3. recovery 호출의 이벤트는 단언되지 않습니다.**
- 두 번째 `self.call`의 events를 버리므로, DR이 요구하는 "truncate 없이 재개방, 누락 바이트만 append"는 최종 바이트 일치로만 간접 확인됩니다. truncate 후 전체 재기록과 구분되지 않습니다.
- 조치: WORK에 남는 recovery `.events`에서 short 3건과 open-after/write-before 건의 colvia open flags(O_CREAT·O_TRUNC 없음)와 `write-before.requested == 전체 − k`를 R1에 실측으로 넣습니다. 넣지 못하면 "unavailable"로 명시합니다. 테스트 강화는 이번 창 밖의 별도 승인 사항입니다.

**R-4. umask 0022는 controller가 강제하지 않습니다.**
- `controller.py`에는 umask 확인이 없고, product의 `_entry_umask`는 0600 보존만 봅니다. 게이트는 Driver 기록뿐입니다.
- 조치: 여섯 번 모두 spawn 직전 관측값을 launch record에 남기고, 불일치 시 변경 없이 STOP합니다(계획과 동일). R1은 이 기록이 없으면 mode 단언의 전제를 미확인으로 처리해야 합니다.

**R-5. 입력 불일치로 인한 STOP 요인이 있습니다.**
- entry `source_root_entries`에 `.idea`(directory)와 `.git`(file)이 고정되어 있고, `tests/`와 `src/`는 membership이 정확히 일치해야 합니다.
- IDE가 `.idea`를 지우거나 다시 만들거나 `tests/` 아래에 파일을 만들면 `config()` 단계에서 멈춥니다.
- 조치: 실행 창 동안 해당 worktree의 IDE와 인덱서를 닫고, 각 단계 전 manifest 확인을 유지합니다.

**R-6. 예산은 통과 가능해 보이나 상한 증명은 아닙니다.**
- 계산은 맞습니다: 19 × (13.244 + 5.781) + 108.795 = 470.270, × 1.5 = 705.405, 여유 474.595초.
- 신규 케이스는 OLD init child, in-process S3 준비(29개 멤버마다 checkpoint), kill child, recovery child로 구성됩니다. 기존 prefix 케이스(11~13초)보다 in-process 준비만큼 길 것이고 5.781초 proxy는 경로가 달라 근거가 약합니다.
- 1180초를 넘으려면 신규 평균이 약 56초여야 하므로 가능성은 낮다고 봅니다.
- 조치 없음. timeout 시 보존 후 STOP하는 현행 규칙으로 충분합니다.

## 4. 범위 밖으로 유지할 것 (R1에서 추론 금지)

- 빈 typed truth와 `not-applicable`은 실제 local/parent/worker Work 보존을 증명하지 않습니다.
- 관측은 Python 호출 경계입니다. `os.read`, `close`, `F_FULLFSYNC` 내부는 hook 밖이며, 전원 손실 내구성과 full P2는 증명되지 않습니다.
- N-05 `root_sync_after`와 O-01 `unlink_before`는 snapshot이 같고 이벤트로만 구분됩니다.
- candidate payload/ref와 preview request는 product-derived이므로 receipt·B1 기대값은 형태만 독립입니다.
- SIGKILL returncode는 테스트 단언일 뿐 별도 raw 저장값이 없습니다.

## 5. Driver 처분용 요약

- **blocker**: 없음 (정적 범위 내).
- **R1 packet에 반드시 포함할 것**:
  - R-1: 실패 시 실제 S3 snapshot과 기대의 차이.
  - R-2: kill events의 flow 행 원문.
  - R-3: recovery events의 open flags와 write 길이, 또는 unavailable 명시.
  - R-4: umask 기록 6건.
  - 그 외: 실제 collection bytes/hash와 `9f49a5e2…`의 일치 여부, `executed.jsonl` 28행의 개별 소요 시간.
- 이 검토는 Owner 수락이나 결과 수락이 아닙니다.

### R0 Driver Disposition

R-1/R-2/R-3/R-4/R-6 accept; R-5 revise: IDE를 임의 종료하지 않고 매 단계 고정 manifest 확인을 유지했다. 기존 Owner 실행 승인이 이 고정 후보의 실패 가능성을 포함하므로 재승인을 요구하지 않았다. 실패 시 R1 진행이라는 reviewer의 조건부 제안은 채택하지 않고 최초 실패 즉시 중단 계약을 유지했다. 실제6단계는 모두 통과했다.

### R1 Reviewer Response — Verbatim

# N/O Resume-03 R1 검토 결과

**결론: 실제 6단계 결과에서 고정 후보에 대한 구체적 blocker는 찾지 못했습니다.** 28/28 통과와 R0 조건 R-1~R-6의 실측 증거가 packet 안에서 서로 일치합니다. 다만 저는 SHA-256을 하나도 재계산하지 못했고, 일부 단언은 원본 저장값 없이 "테스트 통과"로만 증명됩니다. 이 검토는 Owner 수락이나 결과 수락이 아닙니다.

## 1. 증거 구분

| 구분 | 내용 | 한계 |
| --- | --- | --- |
| 새 런타임 증거 | 6개 controller의 result·stdout·counts·executed, 두 collection.json 본문, canary 2종, launch record 6건, kill·recovery event 원본 행 | event는 선택 행만 발췌, 전체 파일은 hash로만 식별 |
| 테스트 단언으로만 증명 | SIGKILL returncode, S3 exact delta, killed-prefix 전체 snapshot 일치, B0 유지, lock free | 별도 저장된 snapshot·returncode 없음 |
| Driver 파생 | case-observations.json의 global_occurrence와 최종 파일 hash, 각 `after_input_check: PASS` | Driver의 읽기 전용 추출이며 독립 검증 아님 |
| 정적 추론 | 기존 101개 본문·helper가 이전 판과 동일하다는 주장(patch 순수 삽입 + static-checks) | 런타임은 "고정된 manifest 바이트로 실행됨"까지만 증명 |
| 과거 trace | b04 prefix_07 initial-apply 16행 | 이번에 recovery 경로 실측으로 대체됨 |

## 2. 6단계 실제 결과

| 단계 | exit·자연 종료·group 부재 | 초 | 핵심 관측 |
| --- | --- | --- | --- |
| acquire-base | 0 / true / true | 0.852 | files 101, old_verified `f1ee1072…` |
| canary-base | 0 / true / true | 0.665 | 10개 named denial 모두 1(EPERM), 3개 topology, fullfsync executed |
| collect-base | 0 / true / true | 0.461 | 776, `31838e46…` (smoke input의 고정값과 일치) |
| smoke-base | 0 / true / true | 64.841 | 20/20 pass, skip·unstarted·unfinished 0 |
| collect-p2 | 0 / true / true | 0.466 | 932, `9f49a5e2…` (기대값과 일치) |
| focused-p2 | 0 / true / true | 294.268 | 28/28 pass, discovered 932, skip·unstarted·unfinished 0 |

- **수집**: p2 collection의 factory_ids는 Control 24 + Old 1 + Product 120 + Foundation 11 = 156이고, 신규 19개가 예상 위치에 있습니다. default 776과 더해 932입니다.
- **focused 선택**: selected.json 28개가 신규 19 + 회귀 9와 일치하고 중복이 없습니다.
- **source 동일성**: collect-p2와 focused-p2 모두 source_digest `65abd844…`이고 `inputs_unchanged_or_acquired_exact: true`입니다. controller가 실행 전후에 test·product·controls 11개의 고정 hash를 검증했다는 뜻입니다.
- **umask와 상한**: launch record 6건 모두 `observed_parent_umask`와 `immediate_launch_umask`가 0022이고 gate PASS입니다. controller 누적은 27→32로 상한 32에 정확히 닿았고, review는 15+2=17입니다.
- **창**: 13:55:09 시작, focused 종료 14:05:19로 120분 창 안입니다. R0는 claude-opus-5-5, tool 0회, 188초였습니다.
- **예산(R-6)**: 신규 19개는 9.16~10.34초(합 약 183.7초), 회귀 9개는 11.38~13.49초(합 약 110.1초)입니다. 합계 약 293.8초로 stdout의 293.816초와 맞고, 추정 705초보다 크게 낮습니다.

## 3. R0 조건별 실측 판정

**R-1 (exact S3 delta): 닫힘, 단 단언 기반.**
- 19개가 모두 통과했으므로 `s3 == snapshot`의 암묵 전제 세 가지가 이 fixture와 umask 0022에서 성립했습니다.
- 실제 S3 snapshot 원본은 packet에 없습니다.

**R-2 (selector 도달성): 닫힘.**
- 19개 kill event가 flow 16행과 일치합니다.
  - root fsync 1회차 seq 5802(admission), 2회차 25151(N publication), 3회차 30536(O retirement).
  - colvia 생성 open은 seq 11704, flags 2818, mode 384이고 항상 colvia open의 1회차입니다.
  - colvia fsync는 17079(chmod 전), 22454(chmod 후)이고 fchmod는 19766, hv2 unlink는 30530입니다.
- R0가 우려한 추가 open은 실제로 있습니다. `flags 256, mode 511`인 colvia 읽기 open이 checkpoint마다 2회씩 나타납니다.
- 이 open들은 모두 생성 open 뒤에 오고, 테스트가 O_CREAT 없는 open을 대조에서 제외하므로 번호가 밀리지 않습니다. `colvia`와 `.`에 대한 추가 fsync는 없었습니다.
- 19개 모두 `kill_event_count`가 마지막 행의 seq와 같습니다. fault 지점 이후 기록이 없다는 원본 수준의 보강 증거입니다.
- 모든 case의 seq가 서로 동일해 경로가 결정적이고, kill과 recovery의 pid는 서로 다르며 pgid는 동일합니다.

**R-3 (truncate 없는 append): Python 호출 경계에서 닫힘.**
- N이 부재한 n01_open_before만 recovery에서 flags 2818로 새로 생성합니다.
- 나머지 18건의 재개방은 flags 258(O_RDWR|O_NOFOLLOW)이고 O_CREAT·O_EXCL·O_TRUNC가 없습니다.
- recovery의 `write-before.requested`는 정확히 잔여 길이입니다.

  | kill 시점 | 이미 쓴 바이트 | recovery requested |
  | --- | --- | --- |
  | zero (open_after, write_before) | 0 | 5702 |
  | one | 1 | 5701 |
  | middle | 2851 | 2851 |
  | last | 5701 | 1 |
  | full 이후 | 5702 | write 없음 |

- 잔여분만 썼는데 최종 bytes 일치 단언이 통과했으므로, 전체 재기록이 아니라 prefix 보존 후 append입니다.
- chmod_after 이후 지점의 recovery에는 fchmod가 없고 fsync만 있습니다. 코드의 mode 0600 조건과 맞습니다.
- 한계: observer는 `ftruncate`·`lseek`를 hook하지 않습니다. truncate 부재는 직접 관측이 아니라 길이와 최종 bytes에서 나온 추론입니다.

**R-4 (umask): 닫힘.** 6건 모두 두 시점 0022로 기록됐습니다. mode 단언(0600·0644·0755)의 전제가 확인됩니다.

**R-5 (입력 drift): 관측된 drift 없음.**
- Driver는 IDE를 닫지 않는 쪽으로 revise했습니다.
- p2 collection의 `source_root_entries`에 `.idea`와 `.git`이 그대로 있고, 6단계 모두 입력 검증을 통과했습니다.

## 4. Blocker는 아닌 잔여 격차

1. **recovery의 N/O 이후 구간이 원본으로 제시되지 않았습니다.**
   - 발췌는 colvia IO뿐입니다. recovery 중 hv2 unlink, root fsync 2·3회차, binding.next 생성과 replace 행이 packet에 없습니다.
   - 최종 상태(`old_entry_absent`, binding mode 0600, `binding_next_absent`, binding hash 19건 동일)는 Driver 추출과 통과 단언으로 확인됩니다. 순서와 재동기화는 미검증입니다.
   - 조치: 이 구간을 주장하려면 `-4.events`의 해당 행을 추가 발췌하거나, 결과 보고에 "recovery resync 순서 미검증"을 명시합니다. 테스트 변경은 별도 승인 사항입니다.

2. **kill 시점 snapshot과 returncode의 원본이 없습니다.** B0 유지, 전체 fixture 보존, `-SIGKILL`은 통과한 단언에만 의존합니다. 결과 보고에서 "단언으로 확인"이라고 표기하면 됩니다.

3. **receipt hash가 case마다 다릅니다.** plan에 target 경로 fingerprint가 들어가므로 예상된 차이입니다. 이상 징후가 아닙니다.

4. **canary의 OLD 보호는 metadata-write(chmod) 거부만 증명합니다.** packet이 스스로 명시한 한계이고, data-write 전반에 대한 증명은 아닙니다.

## 5. 이 결과로 추론하면 안 되는 것

- **Work 보존**: 19건 모두 `transition_content_verification`이 `not-applicable`, `work_ids: []`입니다. nonempty truth나 local·parent·worker Work 보존은 증명되지 않았습니다.
- **물리 내구성**: fsync event는 Python 호출 경계의 기록입니다. 전원 손실 내구성과 F_FULLFSYNC 내부는 증명되지 않았습니다.
- **full P2**: 이번 범위는 N-01~N-05, O-01~O-02의 16 edge + short 3과 회귀 9개입니다. S1·S2 전체 matrix, B-07, 4-executor, P3·P4, 실제 adopter 적용은 범위 밖입니다.
- **oracle 독립성**: candidate payload·ref와 preview request는 product-derived입니다. 독립적으로 조립된 것은 record shape와 delta뿐입니다.

## 6. Driver 처분용 요약

- **blocker**: 없음.
- **최소 조치(소스 수정 불필요)**: 결과 보고에 4절의 1번과 2번 한계를 그대로 적습니다.
- **재시도·보정 필요**: 없음.

### R1 Driver Disposition And Actual Owner Boundary

R1-gap-1~4 accept: 전체 recovery resync 순서 미검증, snapshot/SIGKILL의 단언 근거, 정상적인 receipt hash 차이, OLD_MODE metadata-write 범위를 위 보고서에 명시했다. 추가 소스 변경·review·test 호출은0회다. Owner가 승인한 것은 이번 실행과 private Claude 전송이며, 아직 이 결과의 수락·Work Done·전체P2 완료·commit/push는 승인되지 않았다.


## N/O Owner Acceptance And Remaining P2 Plan — 2026-10-10

Owner actual request: “좋아. 이번 N/O 범위의 결과를 명시한 한계와 함께 수락할게. 남은 P2 항목을 정리하고 다음 최소 실행 범위와 검증 계획을 제안해줘. 추가 실행이나 commit·push는 아직 하지 마.”

### Accepted Result And Limits

Owner가 resume-03의 N/O 한정 결과를 명시한 한계와 함께 수락했다. [실행 결과](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/resume-03/execution-01/result.json) SHA-256은 `0f50e5a8089bfaea295d2f542ea05c75e692b819fbde429d09842379ecded520`, [보고서](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/launcher-prefix-01/resume-03/execution-01/REPORT.md) SHA-256은 `03ae536d950fff1f98db38c21822abbd02c1e1d75a00c7db7ce054c9ef9073be`다. Source digest `65abd844fa49ccce5d106390eec7c8631e338fcb11ac755f11b4186450601635`, test SHA-256 `33d6e5c4c54991b1279d4bc76aec34eba5ae3fd782836b32cdc8fb7acc85e560`의 고정 후보가 대상이다. R0/R1 blocker0, smoke20/20, focused28/28(신규19+회귀9), 실제 collection932/hash 일치, 보정·재시도0의 결과다.

기존 결과 파일과 reviewer 원문은 작성 당시의 acceptance pending 상태를 유지한다. 이 후속 수락 기록이 현재 Owner 판단을 보충하며, 고정 입력·결과·과거 실패3회를 소급 수정하지 않는다. 이 수락은 전체P2/Work Done, 새 실행·검토·코드 변경, C2 활성화·adopter 적용·commit/push의 승인이 아니다.

수락에 포함된 한계는 그대로 유지한다: SIGKILL·S3 및 killed-prefix 전체 snapshot·B0 보존은 통과 단언에 근거하며 별도 raw snapshot/returncode가 없다. Recovery의 전체 resync 순서, nonempty truth/local·parent·worker 보존, 물리 내구성은 미검증이다. Observer가 감싼 Python 호출과 선택 event 행으로 한정하며 ftruncate/lseek/F_FULLFSYNC 내부 전체를 관측했다고 주장하지 않는다. Payload/ref·preview request는 product-derived이고, OLD_MODE canary는 metadata-write 거부 범위다.

### Remaining P2 Map

아래는 새 backlog나 병렬 Work가 아니라 이 기존 Work의 남은 검증 범위다. 과거 통과는 각 고정 후보에 귀속되며 현 후보 전체의 재qualification을 뜻하지 않는다.

| 영역 | 현재 근거 | 남은 완료 조건 |
| --- | --- | --- |
| N-01~N-05 / O-01~O-02 | 이번16 edge+short3, 19건 결과 수락 | 한정 범위 수락 완료. 전체 복구 resync·실제 Work·전원 손실 주장으로 확대하지 않음 |
| B-01~B-06 | 이전 신규28+회귀9, 37/37 결과 수락 | 당시 후보의 한정 결과 유지; 현재 전체P2 수락으로 확대하지 않음 |
| S3-01 release publication | 기존 prefix 회귀의 정상 rename/sync trace, named seam 준비 | rename 전후와 source/destination parent sync 전후의 실제 kill·보존·단일 복구6건: 다음 추천 |
| S1-01~02 / S2-01~02 | receipt4길이·staging inventory/launcher8조합 synthetic tear와 named seam 근거 | 각 실제 receipt/staging 생성·write·sync 경계, 모든 inventory-derived member/dir와 완전 prefix 복구·torn refusal. C-buffered write는 현 os.write hook 밖이므로 미관측과 합성을 구분하고 필요한 관측기 변경을 별도 제안 |
| B-07 empty staging | 현 구현은 S6에서 빈 operation directory를 유지; DR은 retain/remove 허용 | oracle의 retirement 표현과 실제 retain 경로를 명시적으로 대조·처분하고 unknown member/B1+binding.next 거부 근거 연결. rmdir 기능을 추가하라는 요구로 해석하지 않음 |
| Four-executor / all-writer / late-lock | 한정 source-operation과 OLD independent detach late-lock cell | OLD/NEW × installed/independent의 상태별 cell, Work/intent/candidate/lifecycle writer의 S0 positive 및 under-lock 거부·보존 근거 |
| Git admission / local / parent / worker | 현재 전환 fixture는 non-Git·빈 truth/no active Work | index/alias/descendant/ignore 거부, local/schema2 parent baseline·required-ref와 S6 비교, worker/orphan 허용·old ticket/proof 거부·human rebind/new baseline 성공 |
| Mixed-history lifecycle | fresh entry-1에서 한정 update/rollback/repair/schema3 detach 근거 | 실제 OLD→NEW history를 보유한 target의 lifecycle과 독립 detach audit |
| D3 / diagnostic 잔여 | D3-A 설계 수락 및 한정73/73 결과 수락 | 미주입 recovery 하위dir·release parent/operation/new-entry/root sync fault, fault 뒤 명시적 성공 복구·verification-unavailable 등. 정확한 거부 사유, fresh-init apply, view/live update·rollback·repair collision cell도 남음 |

Default fixture 이관과 source/test caller closure는 통합 시 확인할 항목이다. P3의 현행 설명·normative successor/C2, P4의 고정 후보 normal/parent-O·artifact qualification, 실제 adopter 적용은 P2 한정 검증과 별도다. 미검증 범위를 전부 이번 다음 slice에 합치지 않는다.

### Recommended Next Slice — S3 Release Publication Only

추천은 `S3-01`의 정상 publication 경로에서 rename과 양쪽 parent sync 전후6개를 검증하는 것이다. S1/S2 전체는 member별 matrix와 C-buffered write 관측 한계가 있고, B-07은 우선 retain/remove 의미의 처분이 필요하다. S3는 기존 observer가 rename과 fsync를 이미 관측하므로 제품·관측기 변경 없이 한정 검증을 설계할 수 있으며, 수락한 N/O 앞의 release 게시 공백을 채운다. 이 판단은 소스와 기존 로그의 읽기 전용 대조이며 새 실행 결과가 아니다.

시작점은 기존 `after-staged-payload` named seam으로 만든 완전한 S2 staging이다. Receipt와 candidate inventory/payload가 완전하고 O/B0는 유지되며 published release와 N은 없는 상태를 정확히 확인한다. 같은 plan/token/candidate로 recovery에 진입해 다음 지점에서 중단한다.

| 사례 | 대상·관측 | 중단 직후 기대 |
| --- | --- | --- |
| S3-rename-before | `os.rename(staged, release)` 직전 | staged 완전·release 부재, O/B0 유지·N 부재 |
| S3-rename-after | 같은 rename 직후 | staged 부재·release 완전, 빈 switch operation 유지, O/B0 유지·N 부재 |
| S3-release-sync-before/after | `.hrn/product/releases` fsync 전/후 | 위 publication namespace와 정확한 bytes/type/mode 보존 |
| S3-operation-sync-before/after | `.hrn/staging/switch-<operation_id>` fsync 전/후 | 위 publication namespace와 정확한 bytes/type/mode 보존 |

Source에서 rename 뒤 `release-parent` → `release-operation-parent` 순서를 확인했고, b05의 기존 `test_transition_prefix_01_recovers` initial-apply event에서 해당6행을 관측했다. 해당 event 파일 SHA-256은 `116c39c601ee95a43a3a6fb2fded128fc72662c7f85db9956e6619b93445942e`다. 이 trace는 S2-prepared recovery의 event occurrence를 확정하지 않으며, authoring에서 전체 선행 호출을 대조해 global occurrence를 고정하고 실제 run에서 일치 여부를 검증한다. `rename` event의 path는 destination이고 detail.from이 source라는 기존 observer 계약을 따른다.

수정 제안은 `tests/test_entry_window_transition.py`에 test-local helper와 신규6개 사례를 추가하고 이 Work에 기록하는 범위다. 기존 product test120개와 helper/factory, 제품·controls11·policy·oracle·DR은 유지한다. 신규6+기존 prefix01~09 회귀9로 focused15개를 제안하며, 단순 추가라면 예상 collection은932→938이다. 이는 authoring 전 예상치이며 exact ID·collection bytes/hash가 아니다. 숨은 추가 edge·관측기 변경·제품 수정이나6개를 넘는 사례가 필요하면 범위를 재제안한다. 기존 N/O19·binding28·D3 전체를 이유 없이 재실행하지 않는다.

### Completion Criteria And Verification

1. S2 준비의 허용 delta를 inventory-derived 유한 경로와 bytes/type/mode로 열거한다. Named seam 실행 결과 전체를 그대로 기대값으로 삼지 않는다. Receipt/release record shape와 snapshot delta를 독립적으로 조립하되 product-derived payload/ref의 한계를 적는다.
2. 6개 event/path/from/global occurrence와 선행 호출 순서를 고정한다. 의도한 SIGKILL·마지막 완전한 event·PID, rename 전후 namespace를 확인하고 O/B0·receipt·format·일반 파일·빈 truth의 정확한 보존을 비교한다. 관측 불가능한 edge는 pass로 대체하지 않는다.
3. 각 중단 뒤 동일 요청으로 명시적 recovery1회만 수행해 N0755/O부재/B1 mode0600/빈 binding staging·binding.next 부재에 도달한다. Release의 정확한 bytes/type/mode를 보존하고 나머지 fixture는 허용 delta 밖에서 바뀌지 않아야 한다. 후속 recovery는 테스트 절차이며 batch 자동 재시도가 아니다.
4. Fixed selection15개가 실제 collection에 각1회 있고 모두 pass해야 한다. Failure/error/skip/expected failure/unstarted/unfinished0, 입력 전후 동일성, 6회 spawn 직전 umask0022, canary와 process-group 종료 확인을 요구한다.
5. R0는 exact 후보·독립 기대값·selector·예산을, R1은 실제 collection/개별 결과·6개 kill 및 recovery selected event 원문·canary 세부·launch 기록을 검토한다. Snapshot/SIGKILL이 단언 기반인지 raw 값인지 분리하고 전체 recovery resync나 full S1/S2를 주장하지 않는다. Driver 처분 후 Owner가 이 S3 한정 결과를 별도로 수락해야 종료한다.

### Proposed Budget And Approval Gates

지금 승인된 범위는 N/O 수락 기록과 다음 계획뿐이다. 테스트 authoring·discovery·실행·Claude 전송은 하지 않는다. 다음 승인 단위는 테스트6개·사례표·정확한 ID/명령/입력 준비와 정적 확인이다. 그 결과의 고정 후보와 충분한 시간 예측을 보고한 뒤 실제 실행·private Claude 전송 승인을 받는다.

| 항목 | 제안 상한 |
| --- | --- |
| 후보 / 테스트 | 새 후보1개, 신규6+회귀9=focused15 제안 |
| R0 / R1 | fresh no-tool Claude 각1회·20분, 총40분 |
| Controller | acquire/canary/base collect/smoke20/entry collect/focused, 총6회 |
| Controller 시간 | 짧은4단계 각300초, smoke/focused 각1,200초: 총60분 |
| 전체 창 | R0 시작부터120분, 외곽 대기·정리·기록20분 포함 |
| 자동 보정 / 재시도 | 0회 |

이번 수락 batch의 focused28은294.268초, 신규19개는 개별 약9.16~10.34초였다. 이는 예산 참고값이지 S3 시간 보장이 아니다. Authoring 때 S2 준비·recovery 경로와 실제 선택 수를 기준으로 다시 산정한다. 고정 control이 요구하는 선행 acquire/canary/collection/smoke를 지키기 위해6회로 잡았고, 새 경계는 `/Users/kyungseo/dev-home/agent-worktrees/` 아래에서 exact path·부재·미등록·ancestor를 authoring 시 확인한다. 기존 소진 slot이나 correction slot을 전용하지 않으며 지금 새 root를 만들지 않는다.

현재 누적 reviewer invocation17회(완료14·과거 실패3), controller32회다. 위 제안이 별도 승인되면 다음 누적 상한은 reviewer19/controller38이다. 과거 실패·남은 시간은 새 호출 권한이 아니다. 첫 예상 밖 실패·입력 불일치·auth 경로 불일치·시간/출력/보존 한계에서 보존 후 중단한다. Product/control/계약 변경이 필요해져도 자동 확장하지 않는다.

### Preservation And Current Stop

Source/control checkout은 진행 중인 P2에 필요하다. b05의 기존 prefix01 initial-apply trace와 timing은 다음 S3 selector·예산 authoring의 구체적 소비 입력으로 유지한다. 새 S3 후보와 selector 검토가 끝나면 소비 종료 여부와 고유자료·기존 입력 manifest 의존성을 확인해 실행 복사본/중복 raw 정리를 판단한다. 최소 수락 결과·review 원문·처분·기존 실패 기록은 보존하며, 이번 요청으로 checkout 이동/삭제나 새 실행 환경을 만들지 않는다.

이번 변경은 이 Work의 수락·잔여 범위·제안 append뿐이다. Test import/discovery, controller/test, Claude 호출, 제품·테스트·control·DR·STATUS 수정, Work Done, commit/push는0회다. 읽기 전용 source/기존 결과 해시 대조와 문서 GFM·whitespace 검증만 수행한다.


## S3 Test Authoring And Frozen Execution Inputs — 2026-10-10

Owner actual request: “좋아. S3 신규 6개와 기존 회귀 9개 범위로 테스트·사례표·정확한 입력과 실행 계획 작성, 정적 확인까지 승인할게. 기존 제품·통제 코드는 유지하고, 실제 테스트·Claude 검토 호출·commit·push는 하지 마. 후보가 고정되면 결과와 실행 승인 범위를 보고해줘.”

### Authored Result

기존 tests/test_entry_window_transition.py에 test-local helper1개와 S3 신규6개를 추가했다. Rename 전후2, release-parent fsync 전후2, switch-operation-parent fsync 전후2다. 기존 prefix01~09 회귀9개를 그대로 선택해 focused15개로 고정했다. [보고서](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-publication-01/REPORT.md), [전체 ID15개](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-publication-01/test-selection.json), [사례표](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-publication-01/case-matrix.json), [정확한 명령](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-publication-01/COMMANDS.md), [실행 계획](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-publication-01/execution-plan.json).

완전한 S2를 기존 after-staged-payload named seam으로 준비하되, 준비 결과를 기대값으로 복사하지 않고 초기 snapshot에 receipt·inventory·payload와 parent directory의 정확한 허용 delta를 조립해 비교한다. Record shape/delta는 test-local이고 candidate payload/ref·preview request는 product-derived이다. S1/S2 파일 생성의 실제 중단 증거로 주장하지 않는다.

동일 요청의 recovery에서6개 지점을 SIGKILL하고 마지막 완전한 event·PID/PGID·global occurrence·순서와 rename source/destination을 확인한다. Rename 전은 staged 완전/release 부재, rename 후는 staged 부재/release 완전/empty switch operation이어야 하며 모든 kill에서 O/B0·receipt·일반 파일·format·빈 truth를 보존하고 N은 없어야 한다. 동일 plan/token/candidate의 후속 recovery1회로 N0755/O부재/B1 mode0600/binding.next 부재 및 empty binding staging에 도달한다. 허용 delta 밖 전체 bytes/type/mode와 root mode도 비교한다. SIGKILL·snapshot은 단언 기반이며 별도 raw 저장값을 가정하지 않는다.

### Static Checks And Selector Limits

Pinned CPython3.14.7 -I -S -B AST/compile 정적 검사 exit0. 기존120개 product test와 모든 기존 helper/global/child/다른 클래스/factory를 AST로 대조해 보존했다. Entry source102 중 테스트1개만 변경했고 product·controls11·base101·runtime/Git/system config 및 이전 자료225개 파일 hash를 유지했다. [정적 결과](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-publication-01/static-checks.json), [후보 patch](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-publication-01/candidate.patch).

새 recovery의 global occurrence는 rename1, release-parent fsync2, switch-operation fsync34로 고정했다. Operation의 앞선33회는 admission1 + durable(operation) self1 + durable(staged) parent1 + inventory1/payload29의 staged-root 재방문30이다. 기존 b05 initial-apply trace의 operation publication은33회차이며, S2 준비 뒤 recovery에서는 기존 operation admission1회가 추가된다는 정적 추론이다. [기존6행과 도출](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-publication-01/trace-map.json)에 구분했다. 새 실행의 도달성·상태·복구·시간은 아직 unavailable이고 불일치 시 단언 실패로 중단한다.

Default776 + factory162(control24/old1/product126/foundation11) = 예상 collection938이다. 실제 discovery가 아니라 이전 collection bytes와 새 AST로 계산한 기대값이다. Canonical 기대 hash는 `c6029732250ed310811b88cbacc0bbb3d8cbf13ff02ed7e1c31137d425188cb3`이며 실제 collect가 그대로 일치해야 focused15개를 실행할 수 있다. Existing default 중복과 ordered occurrence를 보존하고 선택15개는 각1회여야 한다.

### Exact Candidate

- Source102 digest: `0ba034b5e4131801b0a66ba1a95a90e06ce7c7196a1355ac6c52e9a46e650d5c`.
- Test SHA-256: `d2a052d69827d4ce8c2e488fa783bee0d4f5aa732a5b3e0096eadbb6694aab4d`.
- Git base: `238514686078ce1564010a7b69013f48a635c57c`; tracked diff SHA-256: `c3c0a89c3c641e17e3376edbc09950cd1e923a67ac3063e01a038dc6c2fe8b66`. Untracked test는 source map과 packet 전문으로 별도 식별한다.
- R0 packet: `8c5ef373822769f09b9f0d6329ade6f5f42a54d6ee91ac0d3d228e9fe7a4da06`, 964495bytes, 아직 미전송.
- 준비 입력19개 manifest: `05738a403c6f412c627e2ffda99495c89d3b395f8486b34cc386d5071a2132be`; [prepared-manifest.json](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-publication-01/prepared-manifest.json).

이전 exact test bytes는 launcher-prefix-01의 R0 packet에 있고 새 patch/packet과 함께 복원 가능하다. Source 전체나 before tree 사본을 추가하지 않았다. 실행 root 후보 `/Users/kyungseo/dev-home/agent-worktrees/hv2-reference-private-colvia-s3-verification-20261010-b06`는 부재·미등록·ancestor 비-Git/비-authority를 확인했으며 생성하지 않았다.

### Proposed Execution Approval

다음 별도 승인 범위는 고정 후보의 R0 → acquire/canary/base collect/smoke20/entry collect/focused15 → R1, private 코드·DR·test·결과의 Claude 전송이다. Fresh no-tool R0/R1 각20분, controller6회 합계60분(짧은4단계 각300초, smoke/focused 각1200초), 외곽 대기·정리·기록20분을 포함해 R0 시작부터120분이다. 자동 보정·재시도0회, 누적 제안 상한 reviewer19/controller38이다. 현재 authoring에서 실행한 호출은0회다.

기존 prefix9 합계110.067초 + 신규6 × (기존 prefix 최대13.493초 + N/O 최대10.341초) = 253.071초,50% 여유 포함379.606초다. Focused child1180초 대비800.394초 여유인 계획용 추정이며 보장 상한은 아니다. 실제 benchmark는 하지 않았다.

각 controller 준비/직전 umask0022를 관측·기록하고 다르면 변경 없이 STOP한다. 각 review 전 claude.ai/firstParty/pro subscription 경로를 확인하고 다른/불명확한 경로면 중단한다. Opus alias와 실제 model/session을 구분하며 tools/MCP/tool use0, cap·process group 종료·입력 전후 동일성을 요구한다. R1은 실제 결과 뒤 만들고6개 kill/recovery selected event 원문/전체 원본 hash, collection bytes·selected/executed/counts, canary 세부와6개 launch 기록·R0 처분을 포함한다. 현재 R1 packet/hash는 없다.

첫 예상 밖 실패·입력/수집 불일치·timeout·출력/보존 한계에서 보존 후 중단하며 자동 source 수정·재시도·선택 축소·slot 변경은 하지 않는다. 기존 소진 slot이나 correction slot을 새 검증에 전용하지 않는다.

### Remaining Boundary And Custody

이번 fixture는 빈 truth/no active Work이고 transition_content_verification은 not-applicable이다. S1/S2 전체, B7, 전체 recovery resync, 새 fault/alias/경쟁 조합, four-executor/all-writer, Git/local/parent/worker, mixed-history lifecycle, fullP2/P3/P4/C2/adopter·물리 durability는 별도다. 수락한 N/O19·binding28·D3 전체를 재실행 범위에 추가하지 않았다.

Source/control checkout은 진행 중인P2에, b05 initial-apply trace는 계획된 S3 selector R0에 필요해 유지한다. 새 입력/packet의 소비자는 Owner exact 승인과 R0/R1이며 소비 종료 뒤 재현 가능한 환경과 중복 raw의 보존 필요를 재평가한다. 기존 실패 기록을 보존했고 checkout 이동/삭제·새 실행 환경 생성은 없다. Test import/discovery, controller/test, Claude/auth 호출, 제품·control·DR·STATUS·Work Done·commit/push 변경은0회다. 이 Work에만 authoring 기록을 추가한다.


## S3 Execution Stopped Before R0 — 2026-10-10

Owner actual request: “좋아. 고정된 S3 후보로 R0 검토 → 실행 6회 → R1 검토까지 승인할게. 전체 120분 상한, 재시도·후보 수정 없이 첫 실패나 입력 변경 시 중단해줘. 제품·통제 코드 변경과 commit·push는 하지 말고 결과와 한계를 보고해줘.”

실행 전/중단 후 고정19개·이전225개 및 source/control/runtime 해시 대조 PASS. Claude claude.ai/firstParty/pro 인증 경로와 CLI2.1.296 확인 뒤 R0 실행 요청이 process 생성 전에 자동 승인 검토에서 거부되었다.

자동 승인 검토 사유 원문:

> R0 실행은 고정 packet의 민감할 수 있는 소스·테스트 자료를 Claude 외부 서비스로 전송하는 행위인데, 해당 구체 payload와 destination에 대한 명시적 승인이 충분히 확인되지 않습니다.

Reviewer response: unavailable, 실제 reviewer process 시작0회. Driver disposition: 첫 실패 중단 조건에 따라 재시도/우회 없이 STOP. R0→6회→R1 작업 승인은 기록하되 명시적인 private payload/destination 전송 승인 확인을 요청한다. Owner 결과 수락은 아직 없다.

실제 review/controller0회, 자동 승인 거부1회, 누적 실제 review17/controller32 유지. 새120분 window·b06 실행 root·R0/R1 output 미생성. 제품·통제·테스트·DR·STATUS·Work Done·commit/push 변경0회. Collection938/focused15/selector/중단 상태와 recovery는 여전히 미검증이다.

[중단 보고서와 정확한 재개 범위](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-publication-01/execution-01/REPORT.md), [기계 기록](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-publication-01/execution-01/result.json). R0 packet SHA-256 `8c5ef373822769f09b9f0d6329ade6f5f42a54d6ee91ac0d3d228e9fe7a4da06`와 prepared manifest를 변경하지 않았다. 기존 source/control은 진행 중인P2, b05 trace는 미완료 S3 R0용으로 유지한다. 새 checkout은 생성하지 않았으며 기존 고정/복원 자료는 durable Toolstead 경로에 보존했다. 이 절은 성공 checkpoint나 완료 판정이 아닌 중단 기록이다.


## S3 Resumed Execution And Review Result — 2026-10-10

Owner actual request: “좋아. 고정 R0 packet의 비공개 소스·테스트·DR·통제 자료와 이후 R1 실제 결과를 Anthropic Claude 서비스에 전송하는 것을 명시적으로 승인할게. 같은 후보로 R0 → 실행 6회 → R1을 재개해줘. 전체 120분 상한, 첫 실패나 입력 변경 시 중단, 재시도·후보 수정·제품·통제 코드 변경·commit·push 금지는 그대로 유지해줘.”

### Driver Result And Limits

고정 R0→6회→R1 완료, 653.695초/7200초. R0/R1 blocker0, smoke20/20, focused15/15(신규S3 6+회귀9), 실제collection938/hash일치, skip/error/failure/unstarted/unfinished0. Candidate/source/product/control/test 수정·재시도·commit/push0. 두 reviewer actual model claude-opus-5-5, auth claude.ai/firstParty/pro, tools/MCP/tool use0·입력 전후 보존·process-group 종료 PASS. 누적 review19(완료16/과거실패3)/controller38. 이전 자동 승인 거부는 미호출 기록으로 별도 보존했다.

신규6개 모두 complete-S2 preparation, 의도한 S3 kill, O/B0/N부재 보존과 동일 요청 recovery1회 성공을 단언했다. 원문 event에서 rename 전 releases1/operation33 및 선택 occurrence1/2/34를 대조했다. SIGKILL returncode/kill snapshot은 테스트 단언 기반이며 별도 raw snapshot으로 주장하지 않는다. Payload/ref/request는 product-derived이다. 빈 truth/no active Work, physical durability/fullP2/전체recovery resync와 나머지P2/P3/P4/adopter는 미검증이다.

[보고서](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-publication-01/execution-resume-01/REPORT.md), [기계 결과](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-publication-01/execution-resume-01/result.json), [실제6개 관측](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-publication-01/execution-resume-01/case-observations.json). R1 packet SHA-256 `ccb72837fe00be5cebc01e68a01722c92627e8fad935083aef0c3f07e775a94d`. R1 비차단5건은 Driver 처분 및 [읽기 전용 보완](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-publication-01/execution-resume-01/r1-driver-supplement.json)에 기록했다. Base-only canary와 목록 밖 docs/.idea 미봉인 한계를 유지한다. 보완 자료는 추가 reviewer 검토 대상이 아니다. 기존 고정19/이전225/source/control/runtime/이전중단 기록을 보존했다. Source/control은 진행 중P2, b06 실행 copy는 Owner S3 결과평가/원문대조의 가까운 소비가 남아 유지한다. Owner 처분 후 보존·정리 조건을 재평가한다. Full source/archive/raw 중복 백업은 생성하지 않았다.

### R0 Verbatim Reviewer Response

````text
# S3-01 R0 검토 결과

**판정: 이 고정 후보의 실행을 막을 구체적 차단 사유는 정적 검토에서 찾지 못했습니다.** 다만 아래 내용은 패킷 텍스트만 읽은 정적 추론이며, 해시 재계산·discovery·테스트 실행은 하지 않았습니다. 이 응답은 Owner 수락이 아닙니다.

## 1. 증거 구분

| 구분 | 내용 | 상태 |
| --- | --- | --- |
| 과거 실행 trace (b05, initial apply) | rename 1회차, releases fsync 2회차, operation fsync **33**회차 (seq 49354→49366) | 해당 과거 후보에 대한 관측일 뿐, 이번 후보의 증거가 아님 |
| 정적 추론 (이번 검토) | complete-S2 recovery에서 1 / 2 / **34** | `product.py` 호출 경로를 따라가 재유도, 미실행 |
| 새 runtime 증거 | 없음 | collection 938, focused 15, kill·recovery 결과 모두 미관측 |

## 2. Selector 1/2/34 재유도

`workspace_switch_apply(recover=True)`를 complete-S2 상태에서 따라간 결과 패킷의 유도와 일치합니다.

- **releases fsync = 2회차**: `_entry_sync_admission`에서 1회, `os.rename` 직후 `_entry_sync(release.parent)`가 2회차입니다. `writer_guard`, receipt 재동기화, `checkpoint()`는 releases를 sync하지 않습니다.
- **operation fsync = 34회차**:
  - admission 1회 (operation 디렉터리가 이미 있어 `_entry_sync_paths`에 `switch-operation`으로 포함)
  - `durable(operation)` self 1회
  - `durable(staged)` parent 1회
  - 멤버 30개마다 `reversed(parents)`의 첫 원소 `.`이 `durable(staged)`를 다시 호출해 parent(operation) sync 30회
  - publication 1회
- **33과 34의 차이**: initial apply에서는 admission 시점에 operation이 없어 admission 항이 0입니다. 같은 모델로 과거 trace의 33과 seq 간격(rename 사이 audit 1행, 각 fsync 앞 open 3행)이 재현되므로 모델과 과거 관측이 일관됩니다.
- **rename = 1회차**: dst가 `releases/<rid>`인 rename은 하나뿐이고, `detail.from`은 staged 상대 경로입니다.
- **before/after 독립 계수**: observer가 `event == fault.event`일 때만 세므로 독립입니다.

**오계수 시 fail-closed 여부**
- 실제 횟수가 더 많으면 rename 전에 kill되어 `assertEqual(1, len(starts))`가 실패합니다.
- 실제 횟수가 더 적으면 fault가 관측되지 않아 observer가 `requested fault was not observed`로 끝나고 `-SIGKILL` 단언이 실패합니다.
- stop 2~5는 rename 이후 keyed 행의 연속성 단언으로 "publication sync"임을 runtime에서 확인합니다.

## 3. 테스트 로직 확인

- **S2 delta**: receipt와 staged 30멤버, 그 부모 디렉터리만 추가됩니다. 파일 0644, 디렉터리 0755는 parent umask 0022에 의존합니다.
- **kill 시점 상태**: stop 0은 S2, stop 1~5는 staged가 release로 옮겨진 S3이며 operation은 빈 디렉터리로 남습니다. O/B0 bytes, root mode, N 부재, lock 해제를 단언합니다.
- **후속 recovery**: 동일 request/token으로 1회 호출하고 `updated`, B1 0600, N 0755, O 부재, 빈 `entry-…` 디렉터리, `binding.next` 부재를 전체 snapshot으로 대조합니다.
- **경로 신규성**: S3에서의 후속 recovery는 기존 N/O 사례와 같은 하류 경로입니다. complete-S2에서의 성공 recovery는 이번이 처음 실행되는 경로입니다.
- **oracle 독립성**: payload, release ref, preview request, `verify_workspace_release`는 product 유래입니다. 독립 조립은 record shape와 delta 구조뿐이라는 패킷의 한계 표기가 정확합니다.
- **변경 범위**: patch는 `@@ -1403,6 +1403,138` 단일 hunk의 순수 추가이고, 전체 파일의 해당 블록과 일치합니다.
- **ID 배치**: 새 6개는 factory 정렬상 `test_old_detach_…`와 `test_retired_collision…` 사이에 각 1회 있습니다. factory 합계는 24+1+126+11=162, 776+162=938로 산술이 맞습니다.
- **계획 정합**: controls 11개와 product 해시 문자열은 4개 input, identity, expectation 사이에서 일치합니다. 6단계의 mode/slot은 `ENTRY_MODE_SLOTS`와 선행조건(`completed`)에 맞습니다. 예산 합계는 3600+2400+1200=7200초입니다.

## 4. 비차단 지적과 최소 조치

후보 bytes는 바꾸지 않고 절차와 기록으로 처리할 수 있는 항목입니다.

1. **collection 해시가 미실행 기대값에 묶여 있습니다.** `entry-focused-input`의 `c6029732…`는 정적 조립값입니다. 불일치하면 runner가 focused를 스스로 거부하고 collect-p2 슬롯은 소모됩니다. default 776개 목록과 canonical 직렬화 동일성은 제가 검증하지 못했습니다.
   - 조치: collect-p2 직후 실제 `collection.json` 해시를 focused 전에 대조하고, 불일치 시 계획대로 STOP합니다(재결속 금지 유지).
2. **umask 0022는 control 코드가 기록하거나 강제하지 않습니다.** `controller.py`와 `inputs.json`에 umask 필드가 없습니다.
   - 조치: 6회 모두 실제 spawn하는 바로 그 부모 프로세스에서 관측·기록합니다. 불일치 시 변경하지 말고 STOP합니다.
3. **source root 즉시 항목 drift 위험이 있습니다.** `source_root_entries`에 `.idea`가 고정돼 있고, `.DS_Store` 같은 새 root 항목이 생기면 `config()`가 전·후 검사에서 실패합니다.
   - 조치: 실행 창 동안 해당 worktree를 Finder나 IDE로 건드리지 않습니다.
4. **예산 proxy의 성격.** 새 사례의 첫 recovery는 30멤버 루프와 멤버별 `checkpoint()`를 계측 하에서 다시 수행하므로 N/O보다 prefix 사례의 계측 구간에 가깝습니다. stop 0은 이 구간을 두 번 수행합니다. 사례당 23.8초는 타당한 계획값이지만 상한은 아닙니다.
   - 3배(약 71초)로 잡아도 합계 약 539초로 1180초 안이고, 실질적으로 더 좁은 테스트별 coordinator 180초와 child 150초 안입니다. 추가 benchmark는 필요 없고, timeout 시 보존 후 STOP이면 충분합니다.
5. **실패 보존 한도.** 사례당 events 파일 2개(과거 seq 약 5만 행 기준 각 수 MB~10여 MB)가 fixture에 포함됩니다. 다수가 동시에 실패하면 64/256MiB 보존 한도에서 `exit 87`이 날 수 있습니다. 기존 stop 규칙으로 처리되므로 R1에서 원인을 혼동하지 않도록 구분해 기록합니다.
6. **R1 증거 추출.** stop 0/1 사례에서도 raw events에서 rename-before 직전의 누적 횟수(releases 1, operation 33)를 뽑아 포함하면 34 유도가 6개 전부에서 runtime 관측으로 바뀝니다. 테스트 수정은 필요 없습니다.
7. **승인 상태 표기.** 패킷과 `execution-plan`은 "Prepared only / NOT AUTHORIZED / not sent"로 적혀 있습니다. 이 R0 호출에 대한 Owner 실행·전송 승인은 패킷 밖에서 따로 기록돼야 하며, 저는 확인할 수 없습니다.
8. **문구.** `collection-expectation.gate`의 "before smoke/focused"는 실제 순서(smoke-base가 collect-p2보다 앞)와 어긋납니다. entry 해시 gate는 focused에만 적용됩니다. 기록상 주석으로 충분합니다.

## 5. 검증하지 못한 것

- 모든 SHA-256과 `test_before`→patch→현재 파일의 해시 연쇄. 기존 120개 본문·helper 불변은 patch가 추가 전용이라는 형태로만 확인했습니다.
- default 776개의 실제 개수·순서, 938 collection, 기대 canonical bytes.
- `claude` CLI 플래그의 유효성, 실제 모델·세션·도구 목록. alias와 실제 모델은 Driver가 stream에서 기록해야 하며, 이 응답의 자기 서술은 증거가 아닙니다.
- complete-S2 recovery의 실제 도달성과 kill 전후 상태. F_GETPATH 경로 정규화는 b05 과거 관측에만 근거합니다.
- 전원 손실·F_FULLFSYNC 내구성, 비어 있지 않은 truth와 Work 보존, full P2/P3/P4. 이 범위에서는 추론하지 않습니다.
````

### Driver R0 Disposition

````json
{
  "blocking_findings": 0,
  "driver_disposition": "accept nonblocking procedural observations; no candidate change",
  "execution_allowed": true,
  "items": [
    {
      "action": "Base collection hash gates smoke; actual entry collection hash gates focused, mismatch STOP without rebinding.",
      "disposition": "accept",
      "id": 1
    },
    {
      "action": "Observe parent umask and immediate spawn umask each six calls, require0022 without correction.",
      "disposition": "accept",
      "id": 2
    },
    {
      "action": "Verify exact root entries before/after every call; no Finder/IDE access.",
      "disposition": "accept",
      "id": 3
    },
    {
      "action": "Keep fixed timeout and no benchmark or retries.",
      "disposition": "accept",
      "id": 4
    },
    {
      "action": "Record fixture-preservation exit87 separately if encountered; STOP.",
      "disposition": "accept",
      "id": 5
    },
    {
      "action": "Extract pre-rename releases/operation fsync counts from all six existing event logs for R1; no new test.",
      "disposition": "accept",
      "id": 6
    },
    {
      "action": "Owner explicit execution and Anthropic egress authorization stored in execution-resume-01/authorization.json; frozen prepared text remains historical.",
      "disposition": "accept",
      "id": 7
    },
    {
      "action": "Clarify entry hash gate applies focused only; base hash independently gates smoke.",
      "disposition": "accept",
      "id": 8
    }
  ],
  "owner_result_acceptance": false,
  "review_sha256": "5916250e02635c5c124db6be6eadcfcac52942bfbef4d9ee857ccf06da89f43e"
}

````

### R1 Verbatim Reviewer Response

````text
# S3-01 R1 검토 결과

**판정: 이 고정 후보의 6단계 실제 결과에서 구체적 차단 사유는 찾지 못했습니다.** 판정 범위는 신규 6개와 회귀 9개 단언이 다루는 부분에 한정되며, 아래 비차단 지적 5건은 재실행 없이 기록 보강으로 처리할 수 있습니다. 저는 패킷 텍스트만 읽었고 해시 재계산·실행은 하지 않았습니다. 이 응답은 Owner 수락이 아닙니다.

## 1. 증거 구분

| 구분 | 내용 | 이번 R1에서의 상태 |
| --- | --- | --- |
| 과거 trace (b05, initial apply) | operation fsync 33회차가 publication, seq 49354→49366 | 변동 없음. 이번 후보의 증거가 아님 |
| 정적 추론 (R0) | complete-S2 recovery에서 1 / 2 / 34 | 아래 runtime 관측으로 대체됨 |
| 새 runtime 관측 | 6개 kill events와 6개 recovery events 발췌, collection, counts, canary, launch 기록 | 이번 패킷에서 직접 확인 |
| 테스트 단언으로만 뒷받침 | SIGKILL returncode, kill 시점 전체 snapshot 일치, O/B0 bytes | raw로 따로 보존되지 않음 (case-observations의 한계 표기와 일치) |

## 2. 6단계 실제 결과

| 단계 | exit / 시간 | 확인 내용 |
| --- | --- | --- |
| acquire-base | 0 / 0.647s | files 101, `old_verified`가 baseline-inputs 해시 `f1ee1072…`와 일치 |
| canary-base | 0 / 0.653s | 10개 named denial 모두 errno 1, fullfsync executed, child 상속 pass, stdout 0바이트 |
| collect-base | 0 / 0.449s | 776개, `31838e46…`로 base-smoke-input의 고정값과 일치 |
| smoke-base | 0 / 65.2s | 20/20 pass, skip·unstarted·unfinished 0 |
| collect-p2 | 0 / 0.460s | 938개, `c6029732…`로 정적 기대값과 일치 |
| focused-p2 | 0 / 193.8s | 15/15 pass, discovered 938, selected 15, run 15, skip 0 |

- **실행 통제**: 6회 모두 `natural_completion`, `group_absent`, `after_input_check: PASS`입니다. controls 11개 해시는 모든 inputs.json과 두 collection.json에서 동일합니다.
- **launch 기록**: 6회 모두 parent umask와 직전 umask가 0022이고, argv·cwd·환경은 execution-plan과 일치합니다. 누적 controller 33→38(상한 38), 재시도 0입니다.
- **시간**: focused 종료가 14:52:44Z로 창 시작 후 약 9분입니다. `required_worst_case_remaining_seconds` 감소(5100→2550)도 계획 산술과 맞습니다.
- **collection bytes**: 실제 default 776 + factory 162 = 938입니다. 신규 6개 ID는 `test_old_detach_…`와 `test_retired_collision…` 사이에 각 1회 있고, focused 15개는 모두 occurrence 1입니다.
- **예산**: 신규 6개 합계 약 85초, 회귀 9개 약 108초로 계획 추정 253초 안입니다. `rename_before`만 18.8초인 것은 recovery가 30멤버 루프를 다시 수행하기 때문이며, R0 지적 4와 부합합니다.

## 3. Selector 1/2/34의 runtime 확인

6개 kill events 발췌에서 동일하게 관측됩니다.

- **rename 이전**: releases fsync 1회(seq 3057), operation fsync 33회입니다. 33회의 구성은 admission 1(3072), `durable(operation)` self 1(4537), `durable(staged)` parent 1(4544), 멤버 재방문 30(6163…48017)으로 R0 유도와 행 단위로 맞습니다.
- **publication 구간**: rename 1회차(49893/49895), releases 2회차(49899/49900), operation 34회차(49904/49905)가 연속합니다.
- **kill 지점**: 각 사례의 마지막 행은 49893, 49895, 49899, 49900, 49904, 49905로 scenario의 fault와 정확히 일치합니다. PID는 단일하고 PGID는 controller 그룹(60922)입니다.
- **33과 34의 구분**: 과거 trace의 33은 initial apply의 publication 회차입니다. 이번에 관측된 33은 complete-S2 recovery의 rename 이전 누적치입니다. 숫자가 같을 뿐 의미가 다르며, 이번 publication 회차는 34로 실측됐습니다.
- **stop 0의 추가 관측**: `rename_before`의 recovery events는 결함 없이 S2에서 끝까지 진행하면서 같은 1/33→1/2/34 순서를 한 번 더 보여줍니다.

## 4. kill 상태와 recovery

- **N 부재**: recovery events에서 `colvia`가 flags 2818(O_CREAT|O_EXCL 포함), mode 0600으로 열리고 open-after가 뒤따릅니다. 배타 생성이 성공했으므로 recovery 시작 시점에 N이 없었다는 runtime 근거가 됩니다.
- **recovery 응답**: 6건 모두 `updated`, `not-applicable`, binding_ref `fc1b90b2…`입니다. 응답 inventory의 `product.py` 해시 `7c5797f7…`는 고정 product 해시와 같습니다(product가 계산한 값).
- **최종 상태**: Driver 추출 기준 B1 mode 0600, `binding.next` 부재, O 부재입니다. receipt 해시가 사례마다 다른 것은 plan의 `target_fingerprint`가 경로에 의존하기 때문에 정상입니다.
- **recovery 1회**: 파일 번호가 old-fixture 1, kill scenario 2 / log 3, recovery events 4 / response 5로 이어져 테스트 코드의 호출 2회와 맞습니다.

## 5. R0 처분 8건의 이행

- **1, 8 (해시 gate)**: base 해시가 smoke를, entry 해시가 focused를 gate했고 둘 다 실제값과 일치했습니다.
- **2 (umask)**: 6회 기록이 있습니다. 다만 Driver의 자기 관측이며 control 코드가 강제한 값은 아닙니다. fixture의 0644/0755 단언 통과가 간접 근거입니다.
- **3 (root 항목)**: `config()` 전후 검사가 통과했습니다.
- **4, 5 (timeout, exit 87)**: 재시도 없음, exit 87 미발생입니다.
- **6 (rename 이전 횟수)**: 6개 사례 모두 1/33으로 추출됐습니다.
- **7 (승인)**: authorization.json의 packet 해시 `8c5ef373…`와 plan 해시 `3a5f6228…`가 패킷 표기와 일치합니다. Owner 신원과 실제 발화는 제가 확인할 수 없습니다.

## 6. 비차단 지적과 최소 조치

1. **kill 시점의 O/B0 raw 근거가 발췌에 없습니다.** recovery 발췌에 `hv2`의 unlink 행과 `binding.json`의 replace 행이 빠져 있어, kill 시점 O 존재와 B0는 단언에만 의존합니다.
   - 조치: 기존 `-4.events`에서 `unlink-before hv2`, `replace-before .hrn/product/binding.json` 행을 읽기 전용으로 추가 추출합니다.
2. **recovery scenario(`-4.json`)가 패킷에 없습니다.** "동일 argv·token"은 테스트 코드와 통과 결과에 의존합니다.
   - 조치: 6개 `-4.json`의 해시와 argv를 기록에 추가합니다.
3. **실패 산출물의 부재가 명시돼 있지 않습니다.** `failures/`, `preservation.jsonl`, `suite-events.jsonl`, `identity-stop.json`이 없다는 것은 counts로만 추정됩니다.
   - 조치: 두 실행 디렉터리의 목록을 1회 기록합니다.
4. **canary는 base SOURCE(b02)만 probe했습니다.** entry SOURCE(brand-transition)의 쓰기 거부는 직접 probe되지 않았습니다. 같은 `test.sb`와 사후 `config()` 검사에 의존하며, 목록 밖 `docs/` 하위와 `.idea` 내용은 봉인 대상이 아닙니다.
   - 조치: 한계로 기록합니다. 후보 변경은 필요 없습니다.
5. **누적 reviewer 17회와 prior-stop의 호출 소모 여부는 패킷으로 검증할 수 없습니다.**
   - 조치: Driver 원장을 근거로 명시합니다.

## 7. 추론하지 않는 것

- 비어 있지 않은 truth와 Work의 보존: fixture의 `truth_refs`가 `[]`이고 검증 결과가 `not-applicable`입니다.
- full P2/P3/P4, 19-prefix 전체, S1/S2 생성과 C-buffered write, B-07, Git·parent·worker·mixed-history, four-executor.
- 전원 손실과 물리 내구성: 관측된 것은 Python 호출 경계와 SIGKILL뿐입니다. canary의 `fullfsync: executed`는 호출 가능성만 보여줍니다.
- recovery 재동기화 순서의 완전성, adopter 적용, 기술적 activation.
- 기존 120개 본문과 helper의 불변: 추가 전용 patch, 정적 검사, 입력 해시 gate로만 뒷받침됩니다.
- 실제 모델·세션 정체: 이 응답의 자기 서술은 증거가 아니며 Driver가 stream에서 기록해야 합니다.
````

### Driver R1 Disposition

````json
{
  "blocking_findings": 0,
  "driver_disposition": "accept bounded result and nonblocking limits; no candidate changes or replay",
  "items": [
    {
      "action": "Recorded original unlink hv2 and replace binding before/after lines for six recovery logs. Exact killed O/B0 bytes remain assertions.",
      "disposition": "accept",
      "id": 1
    },
    {
      "action": "Recorded six recovery scenario hashes/argv and verified exact argv/entry/target and stdin bytes match kill request. Recovery fault is null.",
      "disposition": "accept",
      "id": 2
    },
    {
      "action": "Recorded smoke/focused root/work directory lists and absence of eight enumerated failure artifact paths per run.",
      "disposition": "accept",
      "id": 3
    },
    {
      "action": "Document base-only canary source probe and unsealed docs/.idea contents; no expanded probe.",
      "disposition": "accept",
      "id": 4
    },
    {
      "action": "Cumulative19 actual reviewer invocations/16 completed/3 prior failed from Driver Work ledger. Prior pre-process auto-review denial counted separately; controller38.",
      "disposition": "accept",
      "id": 5
    }
  ],
  "owner_result_acceptance": false,
  "review_sha256": "eda049f54d152a09d002b929744838125a9a7b2f37118650c804ab1aaac65307",
  "supplement_independent_review": false,
  "supplement_path": "/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-publication-01/execution-resume-01/r1-driver-supplement.json",
  "supplement_sha256": "0df7c930022f87ebfb91e131743e66e1c31dd33cf3055ffe0b09a170e3954236"
}

````

### Actual Owner Decision Boundary

Owner는 위 인용대로 실행·private Claude 전송과 시간/중단 조건을 승인했다. 이 S3 결과의 수락은 아직 받지 않았다. Reviewer verdict/Driver 처분으로 Owner acceptance·Work Done·fullP2 완료·STATUS 변경을 대체하지 않는다.


## S3 Owner Acceptance And Remaining P2 Plan — 2026-10-11

Owner actual request: “좋아. 이번 S3 결과를 명시한 한계와 함께 수락할게. 남은 P2 항목을 정리하고 다음 최소 실행 범위와 검증 계획을 제안해줘. 추가 실행이나 commit·push는 아직 하지 마.”

### Accepted Scope

Owner가 고정 S3 후보의 R0→6회→R1 결과를 명시한 한계와 함께 수락했다. R0/R1 blocker0, smoke20/20, focused15/15(신규S3 6+회귀9), collection938/hash일치, R0부터R1까지653.695초라는 한정 결과다. [보고서](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-publication-01/execution-resume-01/REPORT.md), [결과](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-publication-01/execution-resume-01/result.json), [R1 후 Driver 보완](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-publication-01/execution-resume-01/r1-driver-supplement.json). Result SHA-256 `2280176cb3a8a06f2feb6d4e7544a7e4a30c1ae70a4ee5f6a72d255459960b07`, report SHA-256 `2968c115ef1055918a364b65b821f0de4b9573781c13925a1159817fb2cc0680`를 유지한다.

SIGKILL/kill snapshot의 단언 근거, product-derived payload/ref/request, 빈 truth/no active Work, base SOURCE만 직접 canary probe한 점, 목록 밖 docs/.idea 미봉인, post-R1 보완의 Driver-only 근거, 물리 durability/fullP2/adopter 미검증을 그대로 유지한다. 과거 report의 acceptance pending은 작성 당시 상태로 보존하고 이 후속 Owner 기록이 현재 판단을 보충한다. 수락을 Work Done·전체P2 완료·새 실행/검토·C2 activation·Git publication 권한으로 확대하지 않는다.

### Remaining P2 Map

이 표는 기존 Work의 잔여 범위를 정리한 것이며 새 Work나 별도 backlog를 만들지 않는다. 과거 PASS는 해당 후보와 assertion 범위의 근거이고 현 후보 전체 qualification을 뜻하지 않는다.

| 영역 | 현재 근거 | 남은 완료 조건 |
| --- | --- | --- |
| S3 정상 publication | 이번6개 rename/양쪽 parent sync 전후 kill·보존·동일 요청 recovery 결과 수락 | 해당 한정 slice 수락 완료. Sync 오류/전체 recovery resync까지 닫힌 것으로 보지 않음 |
| N/O, B-01~B-06 | 이전 N/O19+회귀9와 binding28+회귀9 결과 수락 | 각 기존 한정 결과 유지. 이유 없는 일괄 재실행이나 fullP2 수락으로 확대하지 않음 |
| S1/S2 실제 생성·write·sync | receipt4길이, inventory/launcher8 synthetic tears와 named seam 근거 | inventory-derived 모든 member/dir의 실제 edge, complete-prefix recovery/torn refusal. C-buffered write와 os.write hook 범위를 구분하고 관측 변경은 별도 승인 |
| B-07 empty staging | S3 및 기존 D3 replay에 빈 staging 유지와 synthetic retirement 관측; DR은 empty directory retain/remove 허용 | oracle의 retirement 문구 처분, retain 경로와 unknown member/B1+binding.next 거부 coverage 연결. 제품 rmdir 추가 요구로 해석하지 않음 |
| D3 sync 실패·복구 | 한정73/73와 정상 S3 결과 수락; initial-apply publication faults 및 recovery release-root fault 근거 | complete-S2 recovery publication의 두 parent sync 실패 뒤 보존/동일 요청 성공복구4건을 다음 slice로 추천. Existing-release subtree/parent·N/root 오류, 전체 resync, post-B1 verification-unavailable 등은 별도 |
| Four-executor/all-writer/late-lock | 제한된 source operation/OLD independent detach late-lock | OLD/NEW×installed/independent 상태별 cell, intent/Work/candidate/lifecycle writer의 S0 positive 및 under-lock 거부·보존 |
| Git admission/local/parent/worker | 현 prefix fixture non-Git·빈 truth | index/alias/descendant/ignore 거부, schema1 local/schema2 parent baseline·required-ref/S6 비교, worker/orphan·old ticket/proof·명시적 rebind/new baseline |
| Mixed-history lifecycle/diagnostic | fresh entry-1의 한정 lifecycle/refusal | 실제 OLD→NEW 이력의 update/rollback/repair/detach·독립 audit, 정확한 거부 사유, fresh-init apply 및 view/live collision cell |
| 통합 closure | 개발 후보와 별도 테스트 factory | default fixture 이관과 source/test proof caller closure. P3 현행 문서/normative successor 및 P4 exact candidate normal/parent-O/artifact qualification은 별도 phase |

### Recommended Next Slice — S3 Publication Sync Failure Recovery

추천은 complete-S2 recovery가 release를 rename한 뒤 두 부모 directory sync에서 실패하는4개 사례다. 수락한 S3와 같은 구간의 오류 처리를 검증하므로 제품·controls11·prefix oracle·DR·기존 D3 fixed child를 바꾸지 않는 범위로 설계할 수 있다. S1/S2 전체는 관측기 범위 논의가 필요하고 B-07은 oracle 문구 처분이 선행하므로 이번 최소 runtime slice에 섞지 않는다.

| 신규 사례 | 고정 기존 D3 selector | 주입 결과 | 기대 상태 |
| --- | --- | --- | --- |
| release-parent unavailable | release_parent | unavailable:EINVAL | S3 namespace, B0/O 유지, N 부재, exit65 |
| release-parent OSError | release_parent | OSError(EIO) | 동일 |
| switch-operation-parent unavailable | release_operation_parent | unavailable:EINVAL | 동일 |
| switch-operation-parent OSError | release_operation_parent | OSError(EIO) | 동일 |

기존 D3_SYNC_PROGRAM은 이 selector와 fault를 이미 허용한다. Complete-S2에서는 admission 때 release가 없으므로 두 selector는 그때 맞지 않고, rename 뒤 release 존재/N부재에서 첫 match한다. 이는 현재 source/고정 child를 읽은 정적 추론이며 새 runtime 증거가 아니다. 이번 selector occurrence는 D3 wrapper match1이며, SIGKILL observer의 global fsync2/34와 다른 계수다. 실제 packet에서는 alias/path/facts/order로 둘을 구분해야 한다.

### Proposed Authoring Boundary And Completion Criteria

1. `tests/test_entry_window_transition.py`에 test-local helper와 신규4개 method만 추가하는 authoring을 제안한다. 기존 product test126개·기존 helper/factory/global fixed child, product/control/DR/oracle은 보존한다. 기존 after-staged-payload seam을 사용하되 준비 snapshot을 그대로 기대값으로 복사하지 않고 finite S2 delta를 독립 조립한다. Payload/ref/request의 product-derived 한계는 유지한다.
2. 동일 요청의 recover=True 호출에서 선택한 sync에만1회 오류를 주입한다. 실제 alias/path/selector match1과 rename 뒤의 release 존재·staged부재·N부재·O/B0/receipt를 확인한다. Exact `d3-sync:publication:release-parent` 또는 `release-operation-parent`, errno별 message, HV2-WORKSPACE-PRODUCT/exit65, B1 observed=no/current verification=not-requested를 검사한다.
3. 오류가 발생한 snapshot과 호출 종료 snapshot이 같고 후속 sync row가 없음을 검사한다. 추가 namespace/content publication이 없다는 판단은 종료 snapshot 대조에 근거하며, 중간 write 전체를 별도 syscall trace로 관측했다고 주장하지 않는다. 독립 조립한 S3 delta로 초기/준비 상태와도 비교한다. 일반 파일·format·빈 truth·receipt·O/B0·root mode와 staging/release의 bytes/type/mode를 보존해야 한다. 예상 오류는 테스트 절차이며 batch 실패가 아니다. 예상 진단/보존과 다르면 첫 실패로 중단한다.
4. fault를 넣지 않은 동일 plan/token/candidate 요청으로 recovery1회만 수행한다. Existing release와 두 부모의 필요한 resync가 receipt sync 뒤, N 생성/진행 전에 수행됨을 실제 trace에서 확인하고 S6의 N0755/O부재/B1 mode0600/empty staging·binding.next 부재 및 허용 delta 밖 보존을 대조한다. 전체 inventory subtree resync 순서 qualification으로 확대하지 않는다. 이 명시적 후속 호출은 자동 재시도가 아니다.
5. Focused 제안은 신규4 + 수락한 S3 정상6 + 기존 `test_d3_normal_sync_set_and_order` positive1 =11개다. D3 관측 경로의 무오류 control과 같은 publication 구간의 SIGKILL 회귀를 포함한다. 기존 N/O19·binding28·D3 전체를 추가하지 않는다. 단순 추가라면 collection938→942가 예상되지만 정확한 IDs/canonical collection hash는 authoring 후 고정한다.
6. R0는 정확한 후보·주입 위치·독립 기대값·positive control·예산을, R1은 실제11개 결과/모든4개 오류 및 후속 raw envelope·6회 launch·canary·collection bytes를 검토하도록 제안한다. 테스트0실패/error/skip/미시작/미종료, 입력 전후 일치와 process-group 종료가 완료 조건이다. 제품/control 변경이 필요하면 자동 수정하지 않고 범위를 재제안한다.

### Proposed Approval And Execution Gates

현재 승인은 수락 기록·잔여 항목 정리·계획 제안뿐이다. 다음 승인 단위는 신규4개 테스트와 사례표/정확한 입력/명령·정적 확인 작성이다. 그 후보가 고정된 뒤 실제 실행 및 해당 private packet의 Anthropic Claude 전송을 별도로 승인받는다. 이번 요청으로 authoring·discovery·Claude/auth·controller·제품 실행은 하지 않는다.

별도 실행 승인 시 제안 상한은 fresh no-tool R0/R1 각1회·20분, acquire/canary/base collect/smoke20/entry collect/focused11의 controller6회·합계60분, 외곽 정리/기록20분을 합쳐 새120분 창이다. 후보1개·보정0·재시도0, 첫 예상 밖 실패/입력 drift/collection 불일치/시간·출력·보존 한계에서 중단한다. 현재 누적review19/controller38은 유지하며 새 승인 시 제안 상한은21/44다. 이전 창의 남은 시간이나 사용한 slot은 재사용 권한이 아니다.

S3 신규6개의 실제 합계는 약85초였지만 새4개 fault+recovery의 상한 보장이 아니다. Authoring 때 기존 D3 실제 개별 timing과 S3 trace를 사용해 fixed child150초/각 test coordinator180초/focused child1180초 및 전체 예산 적합성을 정적으로 산정한다. 새 benchmark는 별도 실행 승인 전에는 하지 않는다. 새 unused execution root는 approved agent-worktrees 아래에서 exact path/부재/미등록을 고정하며 지금 생성하지 않는다.

### Preservation And Current Stop

S3 Owner 평가 소비는 이번 수락으로 끝났다. b06의 정상 S36개 trace와 timing은 위4개 fault selector·성공 resync·예산 authoring 및 예정 R0의 구체적 비교 입력으로 가까운 재사용 계획이 있어 유지한다. 다음 후보 고정/R0 처분 때 이 소비 종료와 frozen manifest의 원본 경로 의존성을 다시 확인해 재현 가능한 실행 copy/중복 raw 정리 여부를 판단한다. Source/control checkout은 아직 진행 중인P2에 필요하다. b05도 기존 보존 manifest 의존성과 고유 자료를 확인하기 전 임의 삭제하지 않는다. 새 full source/archive/raw 사본은 만들지 않는다.

이번 변경은 이 Work의 수락·계획 append뿐이다. 고정 S3 결과/packet·과거 실패/승인거부·원문·처분은 그대로 유지한다. Source/test/control/DR/STATUS/Work Done 변경, 신규 Work, test import/discovery/controller/Claude 호출, commit/push는0회다. 문서 GFM·whitespace와 읽기 전용 hash/AST 확인만 수행한다.


## S3 Sync Failure Test Authoring And Frozen Inputs — 2026-10-11

Owner actual request: “좋아. 신규 4개와 기존 회귀 7개 범위로 테스트·사례표·정확한 입력과 실행 계획 작성, 정적 확인까지 승인할게. 제품·통제 코드는 유지하고 실제 테스트·Claude 검토 호출·commit·push는 하지 마. 후보가 고정되면 결과와 실행 승인 범위를 보고해줘.”

### Authored Candidate And Static Result

tests/test_entry_window_transition.py에 test-local helper1개와 신규4개 method를 추가했다. Complete-S2 recovery의 release-parent/switch-operation-parent 각각 unavailable:EINVAL·OSError:EIO를 주입하는4개다. 기존 S3 정상6과 D3 normal-sync positive1을 회귀로 선택해 focused11개로 고정했다. [보고서](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-01/REPORT.md), [사례표](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-01/case-matrix.json), [정확한11개 ID](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-01/test-selection.json), [입력/실행 계획](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-01/execution-plan.json), [명령](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-01/COMMANDS.md).

기존 named seam으로 완전한 S2를 만들되 초기 snapshot에 literal record shape와 inventory-derived30멤버 delta를 독립 조립한다. 동일 요청 recovery의 기존 D3 wrapper selector match1에서만 오류를 주입한다. Exact exit65/code/phase/role/errno·B1 observed=no/current verification=not-requested, 실제 path/facts와 마지막 sync row, injection/종료 snapshot의 정확한S3 일치를 검사한다. O/B0·receipt·일반파일·빈 truth/root mode를 보존하고 N은 없어야 한다. 중간 write 전체를 독립 syscall로 관측했다고 주장하지 않는다.

이어 fault 없는 동일 plan/token/candidate의 recovery1회로 updated/S6에 도달해야 한다. Existing receipt sync 뒤, N-present sync 앞에서 release root→release parent→switch operation sync를 확인한다. N0755/O부재/B1 mode0600/empty staging/binding.next 부재와 전체 허용 delta 밖 보존을 대조한다. New fault runtime은 미실행이며 예상 오류+후속 recovery는 batch 자동 재시도가 아니다. Payload/ref/request는 product-derived이고 빈 truth/no active Work 한계를 유지한다.

Pinned CPython3.14.7 -I -S -B AST/compile 정적 검사 PASS. 기존126개 product method와 모든 기존 helper/module globals/fixed child/다른class/factory를 보존했다. Source102 중 test1개만 변경했고 product·controls11·oracle·DR·base101/runtime/Git/system config는 유지했다. 이전345개 자료 hash도 보존했다. [정적 확인](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-01/static-checks.json), [추가 patch](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-01/candidate.patch).

Expected collection은 default776+factory166(control24/old1/product130/foundation11)=942이며 실제 discovery는 아니다. 정확한 기대 hash는 `65c979c2864456994c49fed41575a6655fd8f44e51293113a2152d00f7529535`다. 실제 base hash는 smoke를, entry hash는 focused를 gate하며 불일치하면 입력 재결속 없이 STOP한다.

D3 selector match1은 S2 admission에 release가 없어 일치하지 않고 rename 후 published release/N부재에서 처음 일치한다는 정적 추론이다. 이전 S3의 global os.fsync2/34와 다른 계수다. [이전 trace 연결](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-01/trace-map.json)은 정상 S3 관측이며 새 오류 도달성/보존/복구 PASS가 아니다.

### Frozen Identity

- Git base `238514686078ce1564010a7b69013f48a635c57c`; tracked diff SHA-256 `c3c0a89c3c641e17e3376edbc09950cd1e923a67ac3063e01a038dc6c2fe8b66`. Untracked test는 full packet/source map으로 별도 식별한다.
- Test SHA-256 `358f8cd137ce9f011acad744df9b391463a80c465a840f53df0242e6fc26e26b`; source102 digest `bf6a9666a181ce25ee52c0ad5b3639479ee4d6a7b0f1aa1a137890352dfcb998`.
- Execution plan SHA-256 `904446fbf01ee9c748590aa0e420b383b7514a3240fe86c113603e6bc32235d4`.
- R0 packet SHA-256 `3cf00d2d65092f8769ebc140c3aa9cbde5f10b0b3fda5a0102c3b059dc8a15ac`, 980297bytes. 준비만 했으며 미전송이다.
- 준비 입력19개 [manifest](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-01/prepared-manifest.json) SHA-256 `a28321af0f8226c709be3f3dcc634dcfdbea9febd19bdc09ca04a58b530d27cf`.

이전 exact test bytes는 수락한 S3 R0 packet에 있고 이번 patch/packet으로 복원할 수 있다. 새 root `/Users/kyungseo/dev-home/agent-worktrees/hv2-reference-private-colvia-s3-sync-verification-20261011-b07`는 부재·미등록·ancestor 비-Git/비-authority를 확인했으며 생성하지 않았다. Source/control checkout은 진행 중P2, b06 normal trace와 b03 timing은 이 후보/예정 R0의 구체적 입력으로 유지한다. Full source/archive/raw 사본은 추가하지 않았다.

### Separate Execution And Egress Approval Scope

다음 승인 대상은 이 고정 후보의 R0→acquire/canary/base collect/smoke20/entry collect/focused11→R1과 비공개 source/test/DR/control/result의 Anthropic Claude 전송이다. R0/R1 fresh no-tool 각1회20분, controller6회60분(300초4회+1200초2회), 외곽정리/기록20분을 포함해 R0 시작부터120분이다. 후보1개·보정/재시도0. 현재 누적review19(완료16/과거실패3)/controller38이고 승인 시 제안 상한21/44다. 과거 자동 승인 거부는 process 시작 전 기록이며 CLI invocation과 구분한다.

이전 실제 timing으로 계산한 실행 proxy179.247초,50% 여유 포함268.871초로 focused child1180초 대비911.130초 여유다. 신규 경로의 시간 보장이 아니며 test coordinator180초/child150초도 그대로다. 추가 benchmark는 하지 않았다. 각 review 전 구독 claude.ai/firstParty/pro 경로, actual model/session/tools/MCP와 process-group 종료, 매controller 준비/직전 umask0022·입력 전후 동일성을 확인해야 한다.

R1은 실제4개 failure+4개 recovery 원문 envelope/snapshot/진단, paired stdin identity, 회귀6개 event와 D3 positive envelope,6단계 actual outputs/collection/canary/launch와 R0 처분으로 실행 뒤 생성한다. 현재 R1 packet/hash는 없다. 첫 예상 밖 failure/input mismatch/collection drift/timeout/output·preservation limit에서 보존 후 STOP하며 수정·재시도·선택 축소·slot 재사용은 하지 않는다.

### Current Stop And Limits

새4개는 simulated sync failure이며 실제 storage fault·SIGKILL·power-loss 검증이 아니다. S1/S2전체/B7/otherD3/full-resync/four-executor/Git/local/parent/worker/mixed-history/P3/P4/C2/adopter/fullP2는 미검증이다. Base-only SOURCE canary와 목록 밖 docs/.idea 미봉인 범위를 유지한다. Reviewer는 제공 packet 밖 전체CLI/work/intent 코드나 hash를 도구로 검증하는 역할이 아니다.

이번 authoring에서 product/test import·discovery/controller/test·Claude/auth 호출0회다. Product/control/DR/oracle/STATUS/Work Done/commit/push 변경0회. Test 신규 helper+4개와 이 Work 기록 및 private 준비 입력만 작성했다. 후보는 이제 고정됐으며 실행·전송은 별도 승인 전까지 하지 않는다.


## S3 Sync Failure R0 Stop — 2026-10-11

### Actual Owner Authorization

“좋아. 고정 후보로 R0 → 실행 6회 → R1까지 승인할게. 비공개 packet과 실제 결과의 Anthropic Claude 전송도 명시적으로 승인해. 전체 120분 상한, 첫 예상 밖 실패나 입력 변경 시 중단하고 재시도·후보 수정·제품·통제 코드 변경·commit·push 없이 결과와 한계를 보고해줘.”

### Driver Result And Limits

R0 완료 뒤 차단 B1 1건을 수용하고 STOP했다. 신규 recovery helper는 B1 뒤 replay까지 포함한 product receipt sync를 2회로 단언한다. 제품 흐름과 기존 회귀의 B1 필터를 읽어 전체3회/pre-B1 2회라는 지적을 확인했다. 정적 추론이며 실행 재현은 아니다. 제안은 신규 sync 필터에 `and not r['facts']['b1']`를 추가하는 한 줄 수정과 설명/파생 입력 재고정이다. 이번에는 적용하지 않았다.

R0 125.847초, 중단 기록까지 207.075초/7200초. 실제 controller0/R1 0, smoke20/focused11/collection942 모두 미실행. 후보·제품·통제·테스트 수정/재시도/commit/push0. 고정19개·이전345개 및 source/control/runtime 입력 보존 PASS. Actual model claude-opus-5-5, session 4d43c5c9-3ea7-4a47-b030-035adbe6c7c8, claude.ai/firstParty/pro, tools/MCP/tool use0, exit0, process-group 종료 확인. 누적 review20(완료17/과거호출실패3)/controller38. 정상 종료된 blocker review를 CLI 호출 실패로 세지 않는다.

[중단 보고서](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-01/execution-01/REPORT.md), [기계 결과](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-01/execution-01/result.json), [Driver 처분](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-01/execution-01/r0-disposition.json). Source/control은 진행 중P2 및 좁은 보정 재사용을 위해 유지한다. 새 b07 root/R1 packet은 미생성이며 새 정리 대상은 없다. 고정 packet/patch와 이전 입력은 보존했다. 이 절은 성공 checkpoint 또는 완료 판정이 아닌 중단 기록이다.

### R0 Verbatim Reviewer Response

````text
# R0 정적 검토 결과: 차단 1건, 현재 후보로는 실행 불가

신규 4개 테스트가 모두 같은 지점에서 실패하도록 작성돼 있습니다. 재시도·소스 보정이 0회이므로 이 후보(`358f8cd1…`)를 그대로 실행하면 focused 단계에서 STOP으로 창을 소진합니다. 아래는 전부 packet 정독에 의한 정적 추론이며 실행 증거가 아닙니다.

## 차단 B1 — recovery 순서 단언이 B1 이후 replay sync까지 센다

**위치**: `release_sync_failure_case`의 no-fault recovery 블록.

```python
syncs = [r for r in recovered['rows'] if r['alias'] == 'product']
receipt_syncs = [j for j, r in enumerate(syncs) if r['path'] == '.hrn/product/receipts']
self.assertEqual(2, len(receipt_syncs), ...)
```

**근거** (변경 없는 `product.py`): S3에서 S6까지 복구하는 한 번의 호출에서 `.hrn/product/receipts`는 product alias로 3회 sync됩니다.

1. `_entry_sync_admission`의 `receipts`.
2. `_entry_write_exact`가 기존 receipt를 재확인한 뒤의 `receipt-parent`.
3. B1 publish 후 `_entry_replay_result` → `_entry_sync_paths(..., replay=True)`의 `receipts` (phase=replay, `b1=True`).

따라서 `assertEqual(2, …)`는 3으로 실패합니다. 설령 통과해도 `last_receipt`가 B1 이후 행이 되어 `last_receipt < j < first_new` 구간이 비게 됩니다.

기존 코드도 이 구분을 전제로 합니다. `test_d3_complete_prefix_retry_resynchronizes`는 `not r['facts']['b1']`로 걸러내고, `test_d3_current_replay_sync_set_and_retired_staging`은 replay 집합에 receipts를 포함합니다.

**최소 수정** (테스트 한 줄, 제품·D3_SYNC_PROGRAM·기존 helper 불변):

```python
syncs = [r for r in recovered['rows'] if r['alias'] == 'product' and not r['facts']['b1']]
```

수정 후에는 B1 이전 receipts sync가 정확히 2회이고, 그 뒤 `_entry_resync_release`의 깊이 역순으로 release root → `.hrn/product/releases` → switch operation이 각 1회, N 생성 뒤 첫 root sync(`first_new`)보다 앞에 옵니다. 나머지 단언은 그대로 성립합니다.

**수정에 따른 재고정 대상**: test SHA, source digest, `candidate.patch`, `entry-collect-input.json`, `entry-focused-input.json`, `entry_expected_sha256`(collection에 `source_digest`가 들어감), `execution-plan.json`의 argv 해시, `input-identity.json`, `static-checks.json`, review packet. REPORT의 "sync 2회" 문구는 "B1 관측 이전 2회"로 한정해야 합니다.

## 차단 아님으로 확인한 항목

- **Selector match 1**: complete S2 admission 시 `release` 디렉터리가 없어 두 selector 모두 불일치합니다. rename 뒤 첫 `_entry_sync(release.parent)`와 `_entry_sync(operation)`이 각각 첫 match이고, 그 행의 selectors는 단일 원소입니다. 이 계수는 observer의 global fsync 2/34와 별개입니다.
- **진단 문자열**: role은 `release-parent` / `release-operation-parent`, 실패 상세는 `unavailable:22` / `oserror:5`, 나머지는 `observed=no`, `not-requested`로 `_entry_sync`의 f-string과 일치합니다. exit 65, `HV2-WORKSPACE-PRODUCT`도 맞습니다. `cli.py`는 packet에 없어, 메시지가 그대로 전달된다는 점은 기존 `d3_composite`의 exact 비교에 기대는 추론입니다.
- **실패 시 보존**: 기대 facts, `expected_s3 == injection.snapshot == after`, 주입 행이 마지막 행(이후 sync 없음), O/B0/receipt/lock, 요청·token·candidate ref 단언이 흐름과 일치합니다.
- **S2/S3/S6 delta**: 기존 `release_publication_case`와 같은 유한 구성입니다(30멤버, key rename, 완료 delta). receipt·payload·ref·request는 제품 유래임이 명시돼 있습니다.
- **변경 범위**: patch는 순수 삽입 1 hunk(+142줄)이고 `D3_SYNC_PROGRAM`은 건드리지 않습니다. "기존 126개와 helper 불변"은 `static-checks.json`의 주장이며 제가 독립 대조한 것은 아닙니다.
- **수량**: 776 + 166(24/1/130/11) = 942, focused 11개입니다. 신규 4개의 정렬 위치는 `test_release_s3_rename_before` 뒤, `test_retired_…` 앞입니다.
- **예산 산술**: 85.332 + 5.083 + 4×22.208 = 179.247초, ×1.5 = 268.8705초, 여유 911.1295초. 창은 2400 + 3600 + 1200 = 7200초이고 outer wait 초과분 180초는 관리 여유 안입니다.
- **한계 표기**: 중간 write 미관측, 물리 내구성 미주장, 빈 truth / active Work 없음은 주석·REPORT·case-matrix에 일관됩니다.

## 비차단 메모

- `entry_expected_sha256`(`65c979…`)과 base collection 해시는 이 검토에서 재계산하지 못했습니다. 불일치 시 STOP 게이트가 있어 수용 가능합니다.
- recovery 단언은 release 하위 member 디렉터리 resync와 admission 구간 순서를 보지 않습니다. 이미 "full subtree 아님"으로 한정돼 있습니다.
- packet은 "Prepared only, not sent"라고 적혀 있는데 저는 이 호출을 받았습니다. 이 호출의 Owner 전송 승인 여부는 제가 확인할 수 없으니 Driver가 기록해야 합니다.
- `--safe-mode`, `--restricted` 플래그의 유효성은 제가 확인할 수 없습니다.

Owner 수락 여부는 제 판단 범위 밖입니다.
````

### Driver R0 Disposition

````json
{
  "blocking_findings": 1,
  "decision": "STOP; no controllers, R1, correction or retry",
  "execution_allowed": false,
  "findings": [
    {
      "correction_authorized": false,
      "disposition": "accept",
      "driver_check": "Read product.py _entry_sync_admission, _entry_write_exact, _entry_sync_paths, _entry_replay_result, final workspace_switch_apply return and existing test_d3_complete_prefix_retry_resynchronizes. Matches reviewer analysis.",
      "evidence_kind": "static inference; not reproduced by executing this candidate",
      "finding": "New recovery helper counts all product receipt sync rows including post-B1 replay; asserts two although source flow has three. last_receipt is then after first_new.",
      "id": "B1",
      "minimal_proposed_change": "Filter recovered product sync rows by not r[\"facts\"][\"b1\"] before counting and ordering; describe the two receipt syncs as pre-B1. Not applied."
    }
  ],
  "nonblocking_dispositions": [
    {
      "disposition": "accept",
      "id": "N1",
      "note": "Reviewer did not recompute collection hashes. Driver frozen-input hash checks pass; actual collection remains unexecuted."
    },
    {
      "disposition": "accept",
      "id": "N2",
      "note": "Recovery checks cover specified release/parent order only, not full subtree or admission order."
    },
    {
      "disposition": "accept",
      "id": "N3",
      "note": "Frozen prepared-only wording records authoring-time status. Current separate authorization.json records explicit Owner execution/private Anthropic transmission authorization; frozen packet remains unchanged."
    },
    {
      "disposition": "accept",
      "id": "N4",
      "note": "CLI exit0/init tools=[]/MCP=[]/tool_use0 observed; do not infer independently verified safe-mode/restricted flag semantics."
    }
  ],
  "review_sha256": "6c369d6648ccb225bd26c16748494ea55e9561d64c6708d1ac17ff027ae3d191",
  "round": "R0"
}

````

### Owner Decision Boundary

Owner는 실행·전송 및 중단 조건을 승인했다. 후보 보정 또는 이 결과의 수락은 아직 승인하지 않았다. R1 응답은 미호출로 unavailable이다. 기존에 수락한 S3 결과와 별개이며 fullP2·Work Done·STATUS 변경은 없다. 보정 authoring과 새 입력 고정 후 실행 재승인이 다음 경계다.


## S3 Sync Failure One-Line Correction And Refreeze — 2026-10-11

### Actual Owner Authorization

“좋아. 신규 테스트 필터 한 줄 보정과 관련 설명·파생 입력 재고정, 정적 확인까지 승인할게. 제품·통제 코드와 기존 회귀는 유지하고 실제 테스트·Claude 호출·commit·push는 하지 마. 후보가 고정되면 결과와 새 실행 승인 범위를 보고해줘.”

### Corrected Candidate And Static Evidence

신규 helper `release_sync_failure_case`의 product sync 필터에 `and not r['facts']['b1']` 한 조건을 추가했다. 중단된 후보와 비교해 소스는 정확히 이 한 줄만 달라졌다. Receipt sync의 2회 단언과 release root→release parent→switch operation 순서 검사는 B1 이전 행만 대상으로 한다. B1 뒤 replay receipt sync1회는 계수에서 제외하지만 모든 recovery row의 PASS 단언은 필터 앞에 그대로 남는다. 기존 회귀의 pre-B1 구분과 일치한다. 제품·통제 코드 결함 수정이 아니라 신규 테스트의 검사 범위 보정이다.

Pinned CPython3.14.7 -I -S -B AST/compile 정적 확인 PASS. 중단 후보 기준130개 product test method·다른 helper·factory·다른 class·module globals·D3 fixed child는 그대로다. 수락한 S3 baseline의126개와 기존 helper 불변도 대조했다. Source102 중 테스트1개만 달라졌고 product·controls11·base101·runtime/Git/system config·승인DR을 유지했다. 이전 후보/검토/중단 기록을 포함한376개 자료 hash를 보존했다.

이 확인은 정적 증거이며 R0 finding의 실행 재현 또는 보정 후 PASS가 아니다. 실제 product/test import·discovery·test/controller·Claude/auth 호출0회, commit/push0회다. Source 필터 한 줄과 설명·파생 입력·이 Work 기록만 변경했다. STATUS/Work Done·Owner 결과 수락은 바꾸지 않았다.

### Frozen Inputs

[보고서](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-02/REPORT.md), [한 줄 patch](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-02/candidate.patch), [정적 확인](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-02/static-checks.json), [사례표](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-02/case-matrix.json), [정확한11개 선택](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-02/test-selection.json), [실행 계획](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-02/execution-plan.json), [8개 명령](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-02/COMMANDS.md), [manifest](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-02/prepared-manifest.json).

- Test SHA-256 `29350076f7805c4845d7242978d0a42f5fed0524974290236def12f3c3aa9aab`.
- Source102 digest `8e6b1df1840be8ce194d9e1e271b0c432dac09abc02a0c443e2b9b6cee73d117`; Git base `238514686078ce1564010a7b69013f48a635c57c`; tracked diff `c3c0a89c3c641e17e3376edbc09950cd1e923a67ac3063e01a038dc6c2fe8b66`. Untracked test 전문은 packet/source map으로 별도 식별한다.
- Expected collection942 hash `e49476f72e2b147bbc14c9372a207d515579cdc8127ee9c3c2c518f3a6c5c4ff`. 실제 수집 결과가 아니다. 4개 신규 + 7개 기존 회귀의 focused11개 선택은 유지했다.
- Plan SHA-256 `73fbb51f61113975e2b8a64323fb1e19293d057104a5a8baef050b6caa7110a0`.
- R0 packet SHA-256 `58a1a34fd7d55f03f77cb695f3419208ebd66c657acdc84f5fcf13fc3163fd72`, 982903bytes. 전문 test/product/jsonio/workspace·controls11·DR·입력과 이전 R0 원문/메타·Driver 처분·중단 결과를 포함한다. 새 reviewer 호출은 없다.
- 준비 입력19개 manifest SHA-256 `556c7572fd2d62ed102e9c5d21f76a2c6e0b4eb998b435498521bec108968ad6`.

직전 exact test bytes는 중단 후보의 R0 packet에 있고 이번 한 줄 patch와 새 전문 packet으로 복원 가능하다. 새 root `/Users/kyungseo/dev-home/agent-worktrees/hv2-reference-private-colvia-s3-sync-verification-20261011-b08`는 부재·미등록·ancestor 비-Git/비-authority를 확인했으며 생성하지 않았다. Source/control은 진행 중P2와 예정 검토에, b06 정상 trace/b03 timing은 frozen 입력에 필요해 유지한다. 새 정리 대상은 없고 full source/archive/raw 중복 백업은 만들지 않았다. Owner 처분과 구체 소비 종료 뒤 기존 의존성과 보존 조건을 다시 확인한다.

### New Execution Approval Scope

새 승인 대상은 이 고정 후보의 R0→acquire/canary/base collect/smoke20/entry collect/focused11→R1, 그리고 비공개 source/test/DR/control 및 실제 결과의 Anthropic Claude 전송이다. 직전 실행 승인은 중단된 후보에 대한 것이며 이번 보정 실행에 재사용하지 않는다.

새120분 창은 R0 시작부터다. Fresh no-tool R0/R1 각1회20분, controller6회60분(300초4회+1200초2회), 외곽정리/기록20분이며 외곽 wait 여유180초도 관리 여유 안이다. 현재 누적review20(정상완료17/과거호출실패3)/controller38, 새 제안 상한22/44. 후보1개·보정0·재시도0, 첫 예상 밖 실패/입력 변경/collection mismatch/timeout/output·보존 한계에서 중단한다. 예상 주입 오류와 테스트 내부의 고정된 동일 요청 recovery1회는 batch 재시도가 아니다.

각 review 직전 claude.ai/firstParty/pro 경로를 확인하고 actual model/session/tools/MCP·입력 전후 보존·process-group 종료를 기록해야 한다. 각 controller parent umask0022는 준비와 spawn 직전 관측·기록한다. 실제 base collection hash가 smoke를, entry 기대 hash가 focused를 gate하며 불일치 시 재결속하지 않는다.

R1은 실제4개 failure+4개 recovery raw envelope·paired stdin identity,6개 회귀 kill/recovery trace와 D3 positive1개 envelope, 실제6단계 결과·collection·counts·canary·launch·R0 처분으로 생성한다. Pre-B1 receipt2회와 post-B1 replay1회 구분을 보여주며 all-row PASS 검사도 유지한다. 지금 R1 packet/hash는 없다.

### Limits

Historical timing proxy179.247초/50% 여유 포함268.871초는 그대로이며 새 benchmark나 시간 보장이 아니다. 신규4개 도달성·상태 보존·복구는 미실행이다. Simulated sync fault는 물리 장치 오류·전원 손실 durability를 검증하지 않는다. 빈 truth/no active Work, product-derived payload/ref/request, full-subtree resync 미검증과 기존 base-only canary/목록 밖 docs/.idea 미봉인 한계를 유지한다. Whole CLI/work/intent는 review packet에 포함하지 않았다. 전체P2/P3/P4/C2/adopter와 나머지 matrix 수락은 별도다. 보정된 후보는 고정됐으며 새 실행·전송 승인 전까지 중단한다.


## Corrected S3 Candidate R0 Session-Limit Stop — 2026-10-11

### Actual Owner Authorization

“좋아. 보정된 고정 후보로 R0 → 실행 6회 → R1까지 승인할게. 비공개 packet과 실제 결과의 Anthropic Claude 전송도 승인해. 전체 120분 상한, 첫 예상 밖 실패나 입력 변경 시 중단하고 재시도·후보 수정·제품·통제 코드 변경·commit·push 없이 결과와 한계를 보고해줘.”

### Driver Result

고정 후보의 R0 호출이 2.285초 뒤 exit1/is_error=true로 실패했다. Claude 세션 한도 오류이며 후보 검토 결과는 unavailable이다. 첫 예상 밖 실패 중단 조건을 적용해 재시도/controller/R1은0회다. Smoke20/focused11/collection942는 실제 실행·수집하지 않았다. 제품·통제·테스트·후보 수정/commit/push0회다.

고정 입력19개·이전 자료376개·source/control/runtime을 전후 대조해 보존했다. Claude 인증은 claude.ai/firstParty/pro, CLI 2.1.296 (Claude Code), session aa322c27-11e1-49df-a279-80ee6cb75b1d. Startup model은 claude-opus-5-5지만 modelUsage가 비어 있어 내용 검토 모델 실행을 확인할 수 없다. Tools/MCP/tool use0, group 종료와 입력 전후 일치 확인. 누적 review21(완료17/호출실패4)/controller38. 중단 기록까지 94.378초/7200초. Stream subtype success만으로 성공 취급하지 않았다.

[중단 보고서](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-02/execution-01/REPORT.md), [기계 결과](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-02/execution-01/result.json). R0 packet SHA-256 `58a1a34fd7d55f03f77cb695f3419208ebd66c657acdc84f5fcf13fc3163fd72`. 새b08 root와 R1 packet은 미생성이며 새 정리 대상이 없다. Source/control과 frozen 입력은 진행 중P2 및 같은 후보 후속 검토를 위해 보존한다. 이 절은 성공 checkpoint나 완료 판정이 아닌 중단 기록이다.

### Verbatim CLI Response — No Substantive Review

````text
You've hit your session limit · resets 3:50am (Asia/Seoul)
````

### Driver Disposition

````json
{
  "blocking_findings": null,
  "decision": "STOP after first unexpected CLI failure; no retry, controllers or R1",
  "disposition": "accept observed service-limit error as execution stop; not a candidate finding",
  "execution_allowed": false,
  "recovery_boundary": "Keep exact candidate; a fresh execution window and Owner authorization are needed after service availability returns. Do not automatically resume or switch billing/provider/model.",
  "reset_time": "CLI reported 3:50am Asia/Seoul; availability after reset not verified",
  "response_sha256": "de49ce0286f9a028043493488b25c028fee082116b6f9e6da303cf0493b19f6c",
  "review_findings": "unavailable; session limit before substantive review",
  "round": "R0"
}

````

### Owner Decision Boundary

Owner는 위 실행·전송과 중단 조건을 승인했다. 실패 뒤 재시도 또는 이후 자동 재개는 승인하지 않았다. CLI 표시 reset3:50am(Asia/Seoul) 이후 실제 사용 가능 여부는 미확인이다. 다음은 사용 가능 시 동일 후보의 새 실행창·별도 output slot·누적 호출 기록을 명시한 재승인이다. 후보의 정적 보정 결과는 유지되지만 수정 후 review/runtime 검증은 unavailable이다. STATUS/Work Done·Owner 결과 수락·fullP2 완료로 처리하지 않는다.


## Corrected S3 Candidate Resumed R0 Session-Limit Stop — 2026-10-11

### Actual Owner Authorization

“승인”

승인 문맥: 직전 보고의 동일 보정 후보에 대한 새 R0→실행6회→R1 및 Anthropic Claude 전송 승인. 새120분, 첫 예상 밖 실패/입력변경 중단, 재시도/후보수정/제품통제변경/commit/push 금지. 새 review output과 window만 사용하고 후보·controller 입력은 그대로 유지.

### Driver Result

고정 후보의 R0 호출이 2.294초 뒤 exit1/is_error=true로 실패했다. Claude 세션 한도 오류이며 후보 검토 결과는 unavailable이다. 첫 예상 밖 실패 중단 조건을 적용해 재시도/controller/R1은0회다. Smoke20/focused11/collection942는 실제 실행·수집하지 않았다. 제품·통제·테스트·후보 수정/commit/push0회다.

고정 입력19개·이전 자료376개·직전 중단11개·source/control/runtime을 전후 대조해 보존했다. 새 실행 메타데이터는 review 출력 경로와 누적 호출 수만 달리하고 후보·controller 입력은 그대로다. Claude 인증은 claude.ai/firstParty/pro, CLI 2.1.296 (Claude Code), session 9341d2cf-9afd-436e-8ab0-e9697c43c2e2. Startup model은 claude-opus-5-5지만 modelUsage가 비어 있어 내용 검토 모델 실행을 확인할 수 없다. Tools/MCP/tool use0, group 종료와 입력 전후 일치 확인. 누적 review22(완료17/호출실패5)/controller38. 중단 기록까지 31.835초/7200초. Stream subtype success만으로 성공 취급하지 않았다.

[중단 보고서](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-02/execution-resume-01/REPORT.md), [기계 결과](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/release-sync-fault-02/execution-resume-01/result.json). R0 packet SHA-256 `58a1a34fd7d55f03f77cb695f3419208ebd66c657acdc84f5fcf13fc3163fd72`. 새b08 root와 R1 packet은 미생성이며 새 정리 대상이 없다. Source/control과 frozen 입력은 진행 중P2 및 같은 후보 후속 검토를 위해 보존한다. 이 절은 성공 checkpoint나 완료 판정이 아닌 중단 기록이다.

### Verbatim CLI Response — No Substantive Review

````text
You've hit your session limit · resets 3:50am (Asia/Seoul)
````

### Driver Disposition

````json
{
  "blocking_findings": null,
  "decision": "STOP after first unexpected CLI failure; no retry, controllers or R1",
  "disposition": "accept observed service-limit error as execution stop; not a candidate finding",
  "execution_allowed": false,
  "recovery_boundary": "Keep exact candidate; a fresh execution window and Owner authorization are needed after service availability returns. Do not automatically resume or switch billing/provider/model.",
  "reset_time": "CLI reported 3:50am Asia/Seoul; availability after reset not verified",
  "response_sha256": "de49ce0286f9a028043493488b25c028fee082116b6f9e6da303cf0493b19f6c",
  "review_findings": "unavailable; session limit before substantive review",
  "round": "R0"
}

````

### Owner Decision Boundary

Owner는 위 실행·전송과 중단 조건을 승인했다. 실패 뒤 재시도 또는 이후 자동 재개는 승인하지 않았다. CLI 표시 reset3:50am(Asia/Seoul) 이후 실제 사용 가능 여부는 미확인이다. 다음은 사용 가능 시 동일 후보의 새 실행창·별도 output slot·누적 호출 기록을 명시한 재승인이다. 후보의 정적 보정 결과는 유지되지만 수정 후 review/runtime 검증은 unavailable이다. STATUS/Work Done·Owner 결과 수락·fullP2 완료로 처리하지 않는다.


## Remaining P2 Driver Batch And Deferred External Review Plan — 2026-10-11

### Owner Direction And Current State

Owner actual request: “Claude 사용량이 회복될 때까지 외부 리뷰를 연기한다. 기존 승인 설계 안에서 남은 P2를 묶어 진행할 범위와 종료 조건을 먼저 제시해줘. Driver 자체 점검과 검증으로 진행하고, 외부 리뷰 대기 항목과 미해결 사항을 기록해. 설계 변경·검증 기준 완화·기존 차단 지적 우회는 하지 마. 변경이 모이면 Claude가 누적 diff와 결과를 한 번에 검토하도록 준비하고, 그전에는 최종 수락·활성화·실제 적용을 하지 마. 중간 커밋도 함께 준비해줘.”

외부 리뷰는 Owner 지시에 따라 연기한다. Claude/auth 호출·사용량 재확인·자동 재시도·예약을 하지 않는다. 새 진행 방식은 Driver 자체 점검과 격리된 검증 결과를 누적한 뒤 Claude가 누적 diff와 결과를 한 번에 검토하도록 준비하는 것이다. 기존 기록의 R0/R1 선행 gate는 각 과거 실행의 역사로 보존한다. 앞으로 승인될 Driver 묶음에는 `external review: deferred by Owner`를 명시하며, 과거 blocker를0으로 바꾸거나 reviewer 승인처럼 보이는 기록을 만들지 않는다.

이번 요청의 “먼저 제시”에 따라 이 단계는 계획·대기 항목 기록·중간 커밋 준비다. 아래 묶음의 구현·실행 상한을 확인받기 전 신규 코드 수정/제품·test import/discovery/controller 실행은 하지 않는다. Commit 준비는 stage/commit/push 실행과 별개다. 현재 단계는 PLAN이며, 다음 전이는 이 묶음 범위 승인 → Driver authoring/static check → exact candidate freeze → bounded execution이다. Owner가 이미 결정한 외부 리뷰 연기를 다시 승인받을 필요는 없다.

기존 소유자는 이 CHORE-20261009-002 한 개의 source development record다. Runtime typed Work를 새로 만들거나 Toolstead STATUS를 이행 장부로 복제하지 않는다. Disposition은 진행 중 C1/P2이며 서비스 한도에 막힌 호출 기록이 개발 Work Done/Failed를 뜻하지 않는다. Toolstead의 다른 dirty 변경은 이번 범위에서 제외한다.

### Batch Scope And Order

한 P2 묶음을 아래3개 검증 단위로 진행한다. 이는 새 기능/설계 결정이 아니라 기존 accepted DR-0004와 D3-A revision1.1, closed C1 file inventory의 미완료 조건을 구현·검증에 연결하는 범위다. 각 단위는 식별 가능한 후보와 결과를 남기며 매 단위마다 Claude 호출 또는 Owner 최종 수락을 요구하지 않는다.

| 단위 | 진행 범위 | Driver 종료 조건 | 별도 판단이 필요한 경계 |
| --- | --- | --- | --- |
| A. Prefix, preservation and recovery | 먼저 보정된 S3 sync4개+회귀7개를 실행해 R0-B1 처분의 runtime 증거를 확보한다. 이어 기존 관측 범위 안의 S1/S2 생성·sync/tear refusal, D3 existing-release/parent/N/root 오류 후 보존·동일 요청 recovery, B-07 retain 경로·unknown member/B1+binding.next 거부를 연결한다 | 새 사례마다 실제 주입 지점·오류·허용 state delta·보존·명시적 recovery를 대조한다. B1 이전 receipt2회와 이후 replay1회를 raw envelope로 분리하고 모든 row PASS 단언을 유지한다 | C-buffered write를 os.write hook으로 관측했다고 하지 않는다. Oracle retirement와 DR retain/remove 허용의 불일치는 처분 대기다. 관측기/정책/oracle 변경이 필요하면 해당 cell을 보류한다 |
| B. Executors and writer fences | OLD/NEW × installed/independent의 상태별 matrix, intent/Work/candidate/lifecycle writer의 S0 positive와 pending-prefix 거부, late-lock 재검사 | 같은 실행기·유효 요청의 S0 성공을 갖춘 거부 증거, 정확한 원인/진단/bytes-mode 보존, 실제 lock 대기·획득 순서의 witness, OLD 원본 불변 | 단순 실행기/권한/요청 오류를 fencing 성공으로 세지 않는다. 고정 observer로 witness가 불가능한 cell은 unavailable로 남긴다 |
| C. Admission, history and integration | Git index/alias/descendant/ignore admission, schema1 local/schema2 parent baseline·required-ref·S6 비교, worker/orphan/old ticket/proof·명시적 rebind, mixed OLD→NEW lifecycle·독립 detach audit, 필요한 fixture/caller closure와 정확한 diagnostics | 승인된 positive/refusal matrix의 실행 결과와 권위·truth 보존, 변경된 proof caller/fixture와 직접 회귀의 closure, 각 미실행 cell의 이유 | 실제 adopter·사용자 저장소에는 실행하지 않는다. Synthetic Git commit/worktree는 승인된 EXEC 내부 fixture 동작에만 한정한다. P3 normative successor·P4 전체 qualification·활성화는 별도다 |

현재 S3 정상6, N/O19, binding28과 D373의 이전 수락은 각각 당시 후보와 assertion의 근거로 유지한다. 변경 영향이 없다는 대조 없이 현 후보의 PASS로 이월하지 않으며, 이유 없는 전수 재실행도 하지 않는다. 현재 보정11개는 아직 미실행이다.

### Allowed Edits And Fixed Boundaries

우선 테스트와 test-local helper·사례표·입력·기록으로 공백을 메운다. Runtime 결함이 재현되면 closed C1 inventory 안에서 accepted contract를 충족시키는 최소 수정만 후보로 포함한다. 계약 의미·schema·지원 predecessor·거부/복구 정책·권위·검증 기대값을 바꾸어 실패를 없애지 않는다. `jsonio.py`, `errors.py`, `umbrella.py`, package/의존성, DR의 accepted 내용, controls11와 sandbox/network/credential 경계는 수정 범위 밖이다.

기존 회귀 assertion의 삭제·완화·skip·expected failure 전환·선택 축소로 통과시키지 않는다. 새 test-local 관측 코드도 실행기/명령/입출력 경계를 고정하고 Driver가 먼저 읽어 검증해야 한다. Controls11/oracle의 변경이 필요하면 E 경로의 별도 범위·검토 조건을 제시하고 그 부분은 실행하지 않는다. B-07 문구를 유리한 의미로 몰래 교체하거나 제품 rmdir를 억지로 추가하지 않는다.

R0-B1은 `수정됨 / 정적 확인 / runtime 확인 대기 / 외부 확인 대기`로 유지한다. A의 첫11개가 통과하고 raw pre/post-B1 구분을 확인한 뒤에만 `Driver runtime 확인 완료 / 외부 확인 대기`로 옮긴다. 그 전에는 의존하는 새 recovery 사례의 실행 근거로 사용하지 않는다. Reviewer가 지적한 실패 조건을 피하기 위해 테스트를 제거하거나 분모만 바꾸지 않는다.

### Verification Gates And Proposed Bounds

각 단위는 authoring 중 정적 대조를 거쳐 한 후보를 고정한다. 고정 입력에는 base revision+diff hash, untracked input bytes의 식별, source/control/runtime/Git/config, exact selected IDs와 expected ordered collection, argv/cwd/environment/output/caps가 들어간다. Authoring 자체 점검, 실제 실행, Driver 해석, 외부 리뷰 대기를 구분한다. 테스트 실행 중에는 후보를 수정하지 않는다.

첫 A 실행은 현재 S3 보정11개와 고정 candidate를 그대로 사용한다. 과거 `execution_allowed=false` R0 처분을 고치지 않고 새 Owner-deferred-review 실행 계획에 Driver preflight의 별도 허용 근거를 기록한다. 최초 acquire/canary/base collect/smoke20/entry collect/focused11의6단계를 모두 유지한다.

묶음 실행 상한 제안: A의 S3 선행 후보1개 + 잔여 A/B/C 각1개, 최대4개의 고정 후보, 후보당 기존6단계 controller1회씩(300초4회+1200초2회=3600초), 총24호출/실행 cap14,400초, 행정·보존60분을 더한 실제 검증 창 총5시간. 현재 누적controller38이므로 이 승인 묶음의 제안 상한62다. Claude 호출은0이며 현재 누적22(완료17/호출실패5)을 유지한다. Authoring 시간과 실행 시간은 별도로 기록한다. 각 후보의 exact ID/예상 시간은 실행 전에 고정하며, 기존 focused child1180초/각 test coordinator180초/child150초를 늘리지 않는다. 4후보/기존 cap 안에 들어가지 않는 matrix는 미해결로 남기고 확장을 별도 제안한다.

A의 나머지 범위가 첫 후보에 함께 들어가는 것처럼 가장하지 않는다. 선행11개 결과가 의존 gate이며 이후 누적 테스트 authoring과 exact freeze를 한다. 승인된 각 단위 내에서는 Driver가 이 기술 gate를 직접 확인하고 진행하며, gate 통과마다 다시 외부 리뷰를 호출하지 않는다. 이 범위에 실패한 후보의 자동 수정·재실행은 포함하지 않는다. 첫 예상 밖 실패/입력 drift/격리 실패/미관측 selector/timeout/보존 한계에서는 실행 묶음을 중단하고 결과를 보존한다. 같은 immutable 후보의 collection과 실제 선택을 검증하며 불일치에 맞춰 기대 hash를 재결속하지 않는다.

종료 시 selected=executed, 실패/error/skip/unstarted/unfinished0, 실제 의도한 positive/refusal 원인, 입력 전후 보존, cleanup/process-group absence, output 보존을 확인한다. 필수 cell이 unavailable 또는 미해결이면 `Driver 부분 검증 / P2 open`으로 보고하며 P2 완료로 부르지 않는다. S1/S2 synthetic tear는 actual process kill과, sync 성공은 물리 durability와, 빈 truth는 실제 local/parent preservation과 분리한다.

### External Review Queue And Open Items

| 항목 | 현재 상태 | 누적 리뷰에 제공할 내용 / 해소 조건 |
| --- | --- | --- |
| S3 R0-B1 pre/post-B1 계수 | 보정·정적 확인 완료, 실행/외부 재확인 대기 | 원 지적/Driver 수용/한 줄 diff, 실제 failure+recovery envelope 및 receipt 계수·순서, all-row PASS 결과 |
| 보정 후보 R0 두 번의 quota 중단 | 검토 unavailable; 테스트0 | 두 error 원문/exit/session과 실제 호출 수. No-blocker로 세지 않음 |
| D3-A revision1.1 세부 구현·잔여 resync | accepted design, 제한된 실행 근거 | 누적 runtime diff와 실제 오류/보존/recovery, post-B1 verification-unavailable 및 역사 비교 한계 |
| S1/S2 buffered write와 전체 member/dir 경계 | 부분 근거, 관측 공백 | 실제/합성/unavailable별 matrix; 미지원 관측은 외부 리뷰/별도 controls 처분 전 open |
| B-07 retirement/retain 의미 | DR은retain/remove 허용, oracle 문구 처분 미결 | DR/oracle/제품 행위 비교와 retain·negative 증거; 해석 처분 없이 obligation 삭제 금지 |
| All-writer/late-lock 및 Git/local/parent/worker/mixed-history | 일부 cell만 근거, 잔여 matrix | 같은 요청 positive+refusal, lock witness, 실제 baseline/authority 및 history 감사 결과 |
| Canary/증거 한계 | base-only SOURCE 직접 probe, 목록 밖 docs/.idea 미봉인, snapshot·kill 중 일부 단언 근거 | 기존 한계를 그대로 표시하고 확대되는 주장 금지 |
| 전체 qualification/activation/application | 미수행 | 누적 Claude 검토 이후에도 별도 P3/P4와 정확한 Owner 수락·활성화·실제 적용 승인 필요 |

기록은 이 Work 안에서 식별자·상태·Driver 처분·증거 위치·다음 해소 조건만 갱신한다. `외부 리뷰 대기`, `미해결 blocker`, `관측 불가`를 서로 구분하며, 기다리고 있다는 이유로 defect를 nonblocking으로 바꾸지 않는다.

### Cumulative Review Packet

변경이 모이면 기존 base `238514686078ce1564010a7b69013f48a635c57c`부터 마지막 중간 commit 또는 후보까지의 누적 diff와 새 untracked 입력, 설계 기준·controls 신원, 사례별 결과·실패/미완료 목록, 기존 finding→수정→Driver 증거 대응표를 하나의 진입 packet으로 준비한다. Reviewer에게는 원문 finding과 실제 실패를 숨기지 않고 전체 누적 변경 및 핵심 구현/테스트 문맥을 제공한다. Packet digest는 최종 입력이 정해진 뒤 계산한다.

Claude 가용성 회복만으로 자동 호출하지 않는다. Owner의 외부 리뷰 연기 해제 또는 해당 누적 검토 지시를 받은 뒤 실제 구독 경로와 fresh session을 확인한다. 논리적으로 한 번의 누적 리뷰를 목표로 하되 입력/출력/context 상한을 넘으면 조용히 누락·요약하지 않고 전송 범위를 다시 제시한다. Reviewer는 findings를 보고하고 Driver가 accept/revise/defend/needs-user를 기록한다. 그 뒤에도 Owner 최종 수락·C2 activation·adopter 적용은 별도이며 이번 묶음으로 하지 않는다.

### Intermediate Commit Preparation

현재 source branch는 `codex/colvia-brand-transition`, HEAD는 `238514686078ce1564010a7b69013f48a635c57c`다. Tracked13 path 변경과 untracked20 file, 합계33 path를 읽기 전용으로 확인했다. 현재 tracked binary diff SHA-256은 `c3c0a89c3c641e17e3376edbc09950cd1e923a67ac3063e01a038dc6c2fe8b66`이며 untracked 파일은 포함하지 않으므로 이것만을 누적 입력의 완전한 신원으로 쓰지 않는다. Rename은 삭제/추가 양쪽 경로를 함께 다룬다.

현재까지의 commit 후보 path inventory(최종 stage 목록은 Driver 검증 뒤 다시 확정):

```text
adapters/colvia-work/SKILL.md
adapters/harness-v2-work/SKILL.md
colvia
docs/decisions/DR-0004-colvia-managed-entry-and-one-way-transition.md
docs/development/CHORE-20261009-001-colvia-entry-contract.md
docs/development/CHORE-20261009-002-colvia-verification-controls.md
docs/development/README.md
docs/development/colvia-brand-transition-plan.md
docs/development/colvia-entry-implementation-plan.md
docs/development/verification/colvia-entry/README.md
docs/development/verification/colvia-entry/acquire.py
docs/development/verification/colvia-entry/acquire.sb
docs/development/verification/colvia-entry/base-seed-ids.json
docs/development/verification/colvia-entry/baseline-inputs.json
docs/development/verification/colvia-entry/canary.py
docs/development/verification/colvia-entry/common.py
docs/development/verification/colvia-entry/controller.py
docs/development/verification/colvia-entry/observer.py
docs/development/verification/colvia-entry/prefix-oracle.json
docs/development/verification/colvia-entry/runner.py
docs/development/verification/colvia-entry/test.sb
hv2
src/hv2ref/candidates.py
src/hv2ref/cli.py
src/hv2ref/intent.py
src/hv2ref/product.py
src/hv2ref/view.py
src/hv2ref/work.py
src/hv2ref/workspace.py
tests/fixtures/product_plain_auditor.py
tests/test_checkout_window_transition.py
tests/test_entry_window_transition.py
tests/test_general_work.py
```

검증 묶음이 멈출 수 있는 지점에 도달하면 이 source branch의 해당 작업 변경만 대상으로 중간 commit을 준비한다. Toolstead의 무관 dirty 파일, EXEC/OLD 경계, private raw packet/fixtures를 편의상 stage하지 않는다. 새 파일이 필요하면 위 목록과의 차이·이유를 먼저 기록한다. Git-ignored 필수 결과는 durable 보존 위치와 소비자를 확인하되 영구 Git 추적이나 full source 복사를 기본으로 추가하지 않는다.

실제 commit 전에는 source diff·최종 path 목록·Driver 검증 결과/미해결 사항·외부 리뷰 대기·disclosure 확인과 정확한 commit message를 제시한다. 이번 요청은 준비이며 stage/commit/push는 하지 않는다. Commit은 복구 가능한 개발 중간 상태일 뿐 제품 수락/활성화/통합/배포를 뜻하지 않는다. 제안 메시지는 다음과 같고 실제 포함 범위에 맞춰 최종 확정한다.

```text
feat: Colvia 전환 구현과 P2 검증 중간 상태를 보존

승인된 entry-1 전환 설계의 구현과 Driver 검증 결과를 보존한다.
외부 누적 리뷰와 미해결 P2 항목은 대기 상태로 유지한다.
최종 수락, 계약 활성화 및 실제 적용은 포함하지 않는다.

Co-authored-by: Claude Opus 5.5 <noreply@anthropic.com>
Co-authored-by: Codex <noreply@openai.com>
```

이 후보 묶음에는 Claude Opus5.5의 기존 실질 검토·보정 기여와 Codex 구현/검증 기여가 있어 dual attribution을 제안한다. Commit 이후 최종 trailer를 검증한다. 아직 존재하지 않는 commit SHA를 packet에 쓰지 않으며 commit이 생기면 이전 입력 신원을 소급 변경하지 않고 새 HEAD/diff 기준을 후속 기록으로 추가한다.

### Completion And Stop

이번 준비 단계의 종료 조건은 위 범위·검증/시간 상한·open/외부 대기 목록·누적 리뷰/commit 준비가 기존 Work에 기록되고, 실제 파일/해시·문서 링크/GFM/whitespace와 이전 기록 보존을 확인하는 것이다. 이 계획에 대한 승인 전에는 구현·테스트·Claude·stage/commit/push를 하지 않는다.

진행 묶음의 종료는 `승인 범위 Driver 검증 완료 + 누적 리뷰/commit 준비` 또는 `명시한 중단 사유와 미완료 상태 보존`이다. 어느 경우도 Owner 최종 수락·P2 Done·C2 활성화·실제 적용을 뜻하지 않는다. 설계 결정이 필요한 항목, 기존 차단 우회, 검증 기준 완화, controls/격리 확장, 입력 변경, 첫 예상 밖 실행 실패 또는 시간/출력/보존 상한 초과가 발생하면 종속 실행을 중단한다. 불명확한 기준을 Driver 편의대로 채우지 않는다.

Source/control checkout은 진행 중P2와 이 계획의 구체적 재사용 대상이므로 유지한다. 새 실행 checkout은 이 계획 작성에서 만들지 않았다. 기존 결과·review 원문·실패·고정 입력·Work 앞부분을 보존했다. 이번 변경은 이 Work의 계획 append뿐이며 코드·DR·controls·STATUS·Git history를 바꾸지 않았다.


## P2 Driver Batch Stop And Deferred Review — 2026-10-11

### Authorization And Outcome

Owner actual approval: “좋아. 제안한 P2 Driver 검증 묶음을 승인할게. 후보 최대 4개·controller 24회·검증과 기록 5시간 상한으로 진행해줘. 첫 예상 밖 실패나 입력 변경 시 중단하고, 설계 변경·기준 완화·차단 지적 우회는 하지 마. Claude 리뷰는 연기하고 누적 diff·결과·미해결 항목과 중간 커밋안을 준비해줘. 실제 커밋·최종 수락·활성화·적용은 별도 승인으로 남겨줘.”

결과는 `STOP / Driver 부분 검증 / P2 open`이다. 첫 후보는 통과했지만 두 번째 후보에서 새 테스트의 기대·요청 구성 오류와 first-failure 집행 공백이 드러나 중단했다. 실패 후보는 수정하거나 재실행하지 않았다. B/C 후보는 authoring·실행하지 않았다. `최대4후보` 승인은 실패 뒤 남은 횟수로 재시작할 권한이 아니다.

| 구분 | 실제 결과 | 근거 범위 |
| --- | --- | --- |
| 후보1: 기존 S3 보정 | controller6 PASS, smoke20/20, focused11/11; fail/error/skip/unstarted/unfinished0 | 기존 후보 테스트 SHA `293500…`의 직접 실행. 새 후보2 전체에 이월하지 않음 |
| 후보1: R0-B1 | Driver runtime 확인 완료 / 외부 확인 대기 | 실패4+동일 요청 복구4 raw envelope 대조. B1 이전 product receipt sync2회, 이후 replay1회, 복구 전체 sync row PASS |
| 후보2: Remaining A | acquire/canary/base collect/smoke20/entry collect PASS; focused non-pass | 실제 ordered collection955개가 고정 예상과 일치한 뒤 selected60개 시작 |
| 후보2 집중 실행 | completed9: PASS4/FAIL5, unfinished1, unstarted50 | SIGTERM으로 runner `counts.json` 미생성. 이 수치는 `executed.jsonl`과 stdout START행을 Driver가 재구성한 것으로 native summary가 아님 |
| 실행 경계 | controller exit2, child exit-15, natural completion=false; process group 없음; 입력 전후 PASS | 종료는 성공이 아닌 의도적 중단. 불완전 실행을 qualification으로 세지 않음 |
| 묶음 상한 | 후보2/4, controller12/24, 누적controller38→50; 검증 실행 약11분4초 | 2026-10-10 15:45:38 UTC 시작, 15:56:42 UTC 실행 중단. 최종 기록 시간은 최종 보고 메타데이터로 별도 확인 |
| Claude/Git/적용 | 새 Claude/auth0, stage/commit/push0, 최종 수락·활성화·실제 적용0 | 과거review22(완료17/호출실패5)는 역사로 유지 |

### Driver Findings And Disposition

| ID | 관측과 원인 | 처분 / 필요한 후속 |
| --- | --- | --- |
| DRIVER-A1 | `test_completed_staging_unknown_members_preserved`의 switch 사례가 정확히 `HV2-WORKSPACE-PRODUCT / unknown switch staging member; preserve`로 거부했고 raw before=after였다. 다만 새 단언이 sync row 전체0을 요구했다. 실제 workspace `.hrn`, workspace `.hrn/locks`, jsonio `.hrn/locks`의 lock 준비 sync3회는 모두PASS, product sync0이다 | accept: 테스트 기대 오류. 현재 테스트는 FAIL로 보존한다. 계약에 근거해 허용되는 lock 준비와 product publication을 구분하는 정확한 단언안을 검토해야 한다. entry 하위 사례는 첫 단언 실패로 미실행 |
| DRIVER-A2 | 기존 admission root/locks × unavailable/oserror4개는 receipt 생성 전에 올바르게 실패·보존했다. 이번에 추가한 무조건 `recover=True` 호출은 모두 `no pending lifecycle to recover` exit65였다 | accept: 새 복구 요청 구성 오류. receipt 전 재착수와 pending receipt의 exact recovery를 구분해야 한다. 오류를 감추기 위한 기대값 변경이나 제품 recovery 완화는 하지 않음 |
| DRIVER-C1 | 고정 runner는 `TextTestRunner(...).run(...)`에 fail-fast가 없고 이번 parent supervisor는 전체 controller 종료만 기다렸다. 첫FAIL 뒤 즉시 suite가 멈추지 않았다 | needs-user: strict first-test failure 집행 미충족. 모니터가 발견해 정확한 runner PID/PPID/PGID를 확인하고 그 그룹에SIGTERM을 보냈다. 첫 실패 이후 추가8개 완료+1개 시작. 새 테스트 controller는 이후0. 다음 실행 전 중단 장치의 범위·검증을 별도 설계해야 하며 controls11을 몰래 변경하지 않음 |

위 원인은 보존된 raw envelope와 현재 source를 읽어 대조한 Driver 진단이다. 실패 traceback은 suite 종료 summary 전에 중단되어 unavailable이며, 추가 재현 실행은 하지 않았다. 현재 증거로 제품 runtime 결함을 확정하지 않는다. PASS4는 binding-directory parent/self × 오류2종의 새 exact recovery 단언까지 완료했지만, 후보2 전체는 non-pass다.

후보2 변경은 `tests/test_entry_window_transition.py` 하나: 새 test method13개, 기존 helper2개에 no-fault recovery 단언 추가, D3 fixed child에 S5 recovery selector4개 추가다. 기존166 test method 본문은 AST 대조로 동일했다. 제품·controls11·DR·schema·의존성·격리 정책은 변경하지 않았다. Test SHA는 `25fdef9f88ce1d6d3d07476c016a53e9c8141f05f6e4219ac6430eb85d7c96bb`다. 실패 뒤 source 수정0이며 이 후보의 변경 patch와 입력 신원을 보존한다.

### Deferred And Unresolved Work

- A: 신규 payload28개 ×4 tear 길이, S5 recovery4지점 ×2오류, candidate/receipt/publication sync 복구의 나머지는 미실행/미완료다. 기존 assertion 또는 예전 결과만으로 신규 단언 PASS를 선언하지 않는다.
- S1/S2 C-buffered write의 실제 syscall 중단 관측, 전체 member/dir 실제 interruption은 여전히 부분/unavailable이다. Synthetic tear와 실제 process kill을 구분한다.
- B-07은 DR의 retain/remove 허용과 oracle retirement 문구의 처분이 미해결이다. Unknown staging negative1개는 raw 보존 거부를 관측했지만 새 테스트FAIL이며 obligation을 해소하지 않는다.
- B: four-executor/state·all-writer·late-lock의 남은 matrix는 시작하지 않았다. 과거 late-lock 단일 사례와 전체 writer coverage를 구분한다.
- C: Git admission/index/ignore/alias, schema1 local/schema2 parent, worker/orphan/old proof·ticket/rebind, mixed lifecycle/history 및 caller closure의 남은 범위는 시작하지 않았다.
- P3/P4 qualification, Owner 최종 수락, C2 활성화, 실제 adopter 적용은 계속 별도다. Toolstead STATUS의 broader focus·Work 상태를 바꾸지 않는다. 기존 source Work 진행 중 상태도 Done으로 바꾸지 않는다.

### Cumulative Review And Commit Preparation

[Batch report](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-01/REPORT.md), [machine result](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-01/result.json), [candidate1 raw disposition](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-01/candidate-01/result.json), [candidate2 failures](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-01/candidate-02/result.json)에서 실제 결과와 한계를 확인한다. [누적 리뷰 진입 packet](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-01/CUMULATIVE-REVIEW.md)과 [중간 commit 준비](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-01/COMMIT-PREPARATION.md)에는 현재 base부터의 정확한 누적 diff·untracked input identity·파일 목록·미해결 사항을 연결한다. SHA는 실제 최종 파일 생성 뒤 manifest에 기입하며 존재하지 않는 commit을 만들지 않는다.

외부 리뷰는 여전히 Owner가 연기했다. Claude 사용량/auth를 조회하거나 자동 재개하지 않는다. 현재 packet은 로컬 검토 준비이며 실제 단일 호출 전 전체 payload 크기와 context 상한을 확인해야 한다. 큰 입력을 조용히 누락하지 않는다. Reviewer가 검토하더라도 findings·Driver 처분·Owner 결정을 분리한다.

Commit 후보 목록33 path와 dual trailer 메시지는 준비하되 현재 `VALIDATE fail / commit not ready`다. “검증 실패 상태에서는 commit하지 않는다”는 현재 recovery 규칙을 유지한다. 실패 후보를 묵시적으로 제외하거나 rollback하여 검증된 것처럼 만들지 않는다. 이번 Owner 요청도 실제 commit을 별도 승인으로 남겼으므로 stage/commit은 없다.

### Recovery Boundary And Preservation

권고하는 다음 범위는 DRIVER-A1/A2의 테스트 기대·요청 분기 보정안과 DRIVER-C1의 첫 실패 중단 보장안을 먼저 한 묶음으로 준비하는 것이다. 이 단계의 완료 기준은 accepted contract·기존 assertions를 보존하는 diff, exact 중단 방식, 관측 한계, 별도 실행 상한을 검토 가능하게 제시하는 것이다. controls 변경이 필요하면 기존 E 경로 범위로 따로 명시한다. 승인 전 후보 수정/실행을 재개하지 않는다. 현재 남은 횟수·5시간 창을 새 후보 실행 권한으로 재사용하지 않는다.

Source/control checkout은 ongoing P2에 사용 중이다. 후보1 실행 경계는 S3 보정 raw의 외부 검토, 후보2 실행 경계는 미해결 실패와 중단 기록의 Owner·Claude 검토에 필요해 유지한다. Required ignored inputs/results는 durable Toolstead private bundle 및 승인된 agent-worktree root에 존재하며 임시 디렉터리가 유일한 사본이 아니다. 실행 fixture 보존은 영구 Git 추적을 뜻하지 않는다. Owner 처분 및 검토·복구 의존성이 끝나면 보존 필요를 다시 평가한다. 이 중단에서는 checkout 제거·branch 삭제·파일 정리를 하지 않았다.


## P2 Continuation Readiness And Control Boundary — 2026-10-11

Owner actual request: “Claude 외부 리뷰는 사용량 회복 후 누적 변경을 대상으로 진행하자. 기존 승인 설계와 P2 파일 범위 안에서 남은 구현·테스트 작성·집중 검증을 계속해. Driver 자체 점검 결과와 외부 리뷰 대기 사항을 기록하고, 범위 내 단계 전환은 재승인 없이 진행해. 설계·통제 변경, 검증 기준 완화, 입력 보존 문제나 예상 밖 검증 실패가 발생하면 멈추고 보고해. 최종 수락·활성화·실제 적용은 외부 리뷰 이후로 남겨두고, 중간 커밋은 변경 목록과 메시지를 준비해서 승인 요청해.”

기존 P2 범위의 계속 진행·내부 단계 전환은 승인됐다. 그러나 앞서 발견된 DRIVER-C1은 고정 controls11의 `runner.py`에 fail-fast가 없어 첫 실패 뒤 후속 test를 시작하는 실행 통제 결함이다. 현재 파일에 승인된 fail-fast 옵션/외부 설정 경로가 없음을 읽기 전용으로 확인했다. 테스트 파일의 monkeypatch 또는 새 wrapper로 우회하면 통제 변경 경계를 숨기므로 실행하지 않는다. 통제 변경 시 중단하라는 이번 Owner 조건에 따라 새 구현·검증을 재개하기 전에 멈췄다. 이전 실패를 새 검증 실패로 세지 않는다.

[한 줄 통제 변경 제안과 검증 조건](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-01/continuation-readiness-01/PROPOSAL.md) 및 [proposed diff](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-01/continuation-readiness-01/runner-failfast-proposal.patch)를 준비했다. 변경은 `TextTestRunner(..., failfast=True)` 추가 제안이며 아직 적용하지 않았다. 정상적인 current-test 정리·실패 증거 보존과 다음 selected test 미시작을 구분해 검증해야 한다. 새로운 controls 신원에 old PASS를 이월하지 않는다. 실제 합성 검증용 exact 명령·입력·상한은 별도 준비가 필요하다.

Driver read-only 점검: 현재 누적33 path bytes/deletion·HEAD·빈 index가 직전 packet과 일치한다. 제품/test/control 변경0, 새 controller0, Claude/auth0, stage/commit/push0이다. 이 Work append와 로컬 proposed patch만 추가했다. 원 실행 입력·FAIL·raw 결과와 이전 Work bytes는 그대로 보존했다. 이전 누적 packet은 당시 Work의 frozen diff를 담은 역사로 유지하며 이번 append를 소급 반영하지 않는다.

외부 리뷰는 누적 변경 대상으로 계속 대기한다. 미완료 A/B/C 및 DRIVER-A1/A2는 통제 선행 blocker 뒤에 남는다. 현재 중간 commit 목록33개와 메시지는 준비돼 있지만 VALIDATE fail이므로 실행 승인 요청 상태로 올리지 않았다. 통제 변경 범위가 해소되고 기존 P2 검증이 통과하면 최종 diff·변경 목록·메시지로 commit 승인을 요청한다. 최종 수락·활성화·실제 적용은 외부 리뷰 뒤에도 Owner 결정으로 남는다.

Source/control 및 이전 두 실행 경계는 ongoing P2, 미해결 실패, 예정된 누적 검토에 필요해 유지한다. Required ignored evidence의 durable 위치와 기존 cumulative patch가 존재함을 확인했고 cleanup은 하지 않았다.


## P2 Failfast Resume And B Control Boundary Stop — 2026-10-11

### Owner Authorization And Result

Owner actual request: “승인해. runner의 failfast=True 한 줄 보정과 검증 준비를 진행하고, 기존 승인 범위의 P2 작성·집중 검증은 이어서 진행해. 추가 통제·설계 변경이나 예상 밖 실패가 생기면 멈춰서 보고하고, 중간 커밋은 목록과 메시지를 준비해 승인 요청해.”

승인된 runner 한 줄 보정과 A의 요청·기대값 보정을 적용하고 A를 통과했다. 이어 B를 작성·검증했지만 NEW installed candidate의 정상 대조군이 예상 밖 오류를 반환해 첫 실패에서 중단했다. C는 작성·실행하지 않았다. 과거 batch01 실패와 first-failure 집행 공백은 역사로 보존하며 이번 결과로 소급 통과시키지 않는다.

| Candidate | Actual Result | Boundary |
| --- | --- | --- |
| A: approved failfast + corrected preservation/recovery | controller6 PASS; smoke20/20, focused64/64; error/fail/skip/unstarted/unfinished0 | 실제 runner probe4, corrected A1/A2, D3 recovery, S3 회귀, synthetic member tears112개를 포함 |
| B: executor and writer fences | acquire/canary/base collect/smoke20/entry collect PASS; focused12 중8 PASS/1 FAIL/3 unstarted; unfinished0 | native counts·traceback summary 생성. 전체 B는 FAIL이며 pending-prefix 가족별 검사와 C 완료를 주장하지 않음 |
| First-failure behavior | 첫 실패가 마지막 시작·완료 테스트. 이후 테스트 시작0. Controller exit2/child exit1, natural completion=true, group_absent=true | 이전 수동 SIGTERM과 달리 failfast를 통한 자연 종료. 실패를 정상 성공으로 분류하지 않음 |
| Budget | 후보2/3, controller12/18, cumulative50→62; 재시도0, Claude/auth0 | 4시간 창은2026-10-10 16:13:57 UTC부터. 실행 종료16:37:44 UTC. 실패 이후 남은 횟수를 재시작 권한으로 사용하지 않음 |

### Applied Changes And A Evidence

`runner.py`는 `TextTestRunner`에 `failfast=True` 한 인자만 추가했다. SHA는 `6d569b1de5fd5e1ee71b84b7fbdd5cf7c4976a0ccb2f2ee629f5bb66effb1073`에서 `10f5b228d9ef40694fa5cb2a1b59d7cc85dfb5526a910485f3042c96d3381148`로 바뀌었다. 나머지 controls10·제품 runtime·DR·schema·network/sandbox/time cap은 변경하지 않았다. 기존 baseline source는 그대로 보존하고 새 bounded baseline에는 동일 한 줄만 반영했다.

A1은 unknown switch staging refusal 때 허용되는 정확한 lock 준비 sync3개와 product sync0을 구분하고 before=after를 유지한다. Entry staging branch는 sync0을 유지한다. A2는 receipt 생성 전 admission 오류에서 일반 apply, pending receipt가 생긴 뒤에는 recover를 사용하되 같은 preview/request/token과 복구 전체 sync PASS를 단언한다. 이전 FAIL5를 숨기는 skip/expected-failure나 제품 계약 완화는 없다. 이번64개 직접 실행으로 수정 assertion을 확인했다.

실제 runner probe는 failure/error/subtest 각각 selected2/run1/unstarted1, 정상 대조군 selected2/run2/unstarted0을 확인했다. 실패 fixture 보존·cleanup·counts·executed/unstarted/unfinished·traceback marker와 sentinel 미시작을 검사했다. 실제 config/OLD admission 뒤에 synthetic discovery/selection만 대체했다는 한계를 명시하며 sandbox나 전체 collection 독립 qualification으로 확대하지 않는다.

Payload28개 × zero/one/middle/last4종 =112개의 합성 tear는 정확한 refusal와 bytes/mode 보존을 확인했다. S5의 release/operation/new-entry/old-retirement parent4지점 × unavailable/oserror2종은 실패 전후 snapshot 일치와 같은 요청으로 성공 복구를 확인했다. C-buffered write의 실제 중단이나 전원 손실 내구성 증거는 아니다.

A test SHA: `eb6984d13b66cc1f4dece516c92bc709264dbe446e4bb68293ef2a6015f0a8c9`. A result: [candidate-01/result.json](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-02/candidate-01/result.json), SHA `b009fb91da243618279567769bed0c2e05714112642193e64281adaf363f163c`.

### B Partial Evidence And Driver Finding

B는 test-local helper 및 test9개만 추가했고 기존224 method AST는 그대로였다. Test SHA: `0d9dcf9776aa298f7b1066d8d613e90eb8dc5fee030f7d4c9703e352b6f1982b`. Collection968/default776/factory192, focused12를 실행 전에 고정했다.

통과8개는 four-executor entry boundary1, OLD installed candidate/intent/Work/lifecycle late-lock4, 기존 local baseline cutover/replay1, OLD independent detach late-lock1, source-operation matrix1이다. 각 새 late-lock에는 같은 writer 계열의 정상 S0 성공, 실제 lock-attempt→대기→lock-acquired, NEW receipt 기록 이후 OLD의 under-lock 재검사·정확한 오류, receipt 외 snapshot 보존 assertion이 있다. Installed NEW가 S0에 없거나 S5 binding 불일치로 bootstrap을 거부하는 상태와 source record 명령의 parser 거부는 writer fence 성공으로 세지 않는다.

`DRIVER-B1 / needs-user`: `test_writer_family_candidate_pending_fence`의 OLD installed positive는 `saved`로 성공했지만, NEW installed positive는 `HV2-INTERNAL / RuntimeError` exit70이었다. Pending-prefix loop에는 진입하지 않았다. 실제 event에서 candidate file `replace-after` seq16389와 planning/staging parent sync를 관측했고 결과파일은 OLD positive와 같은1282 bytes이며 SHA `201fc3235e8cffc1594bd3b7cd2615c8997bdca925735832b52007852c1e18b2`다. 따라서 no-write refusal나 rollback 성공으로 기록하지 않는다.

정적 대조: `candidates._candidate_bytes()`는 게시 후 결과를 읽을 때 `os.open(..., dir_fd=fd)`를 사용한다. NEW selector의 고정 observer는 `observed_open()`에서 dir_fd를 거부하고 RuntimeError를 낸다. OLD selector는 flock만 계측하므로 이 경로의 정상 대조군을 통과했다. 관측기와 제품의 읽기 방식 충돌이 유력하지만 CLI가 exception type만 기록해 내부 traceback은 unavailable이다. 이 진단은 정적 추론이며 observer 없는 실행 또는 추가 재현으로 확정하지 않았다. 제품 runtime 결함을 확정하거나 회복 성공으로 바꾸지 않는다.

첫 실패 이후 intent/lifecycle/Work family3개는 미시작이며 native unstarted 목록에 있다. 실패한 candidate family 내부의 prefix4개와 이후 family의 정상·거부 subcase도 미실행이다. 현재 네 계열 대표 draft/add/publish/detach 외 모든 writer action까지 검증한 것은 아니다.

Runner는 실패 fixture5,632,832 bytes를 보존했고 원본 fixture와 사본의 전체 bytes/mode/link/directory map을 읽기 전용으로 대조해 일치했다. Test/controller의 frozen source·control·OLD·runtime·DR·HEAD 및 prior evidence2672개 불변을 확인했다. [B native result와 raw 신원](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-02/candidate-02/result.json), [batch result](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-02/result.json), [STOP](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-02/STOP.json).

### Remaining Work And Recovery Gate

- S1/S2 buffered write 실제 관측과 전체 syscall matrix, B-07 retirement/retain 해석은 미해결이다. Oracle·DR 의미는 변경하지 않았다.
- B의 pending-prefix/all-writer 잔여 matrix는 위 실패 때문에 완료되지 않았다. Candidate 파일을 게시한 오류 사례를 fencing 증거로 사용하지 않는다.
- C Git admission/ignore/alias, schema1 local/schema2 parent baseline/required-ref, worker/orphan/old ticket/proof/rebind, mixed history/caller closure는 이번 resume에서 작성·실행하지 않았다. Read-only 참고 대조만 했다.
- P3/P4·Owner 최종 수락·활성화·실제 adopter 적용은 외부 리뷰 이후 별도다. 새 Claude 호출/인증 조회/전송은0이다.

권고 순서는 먼저 제한된 진단으로 RuntimeError의 정확한 발생점을 확인하고, 필요하면 descriptor-relative read 관측을 지원하는 최소 observer 통제 변경을 별도 검토·승인하는 것이다. 제품 보안 읽기를 약화하거나 dir_fd를 그냥 통과시켜 관측했다고 주장하지 않는다. Probe/allowlist/경계/부정 사례와 고정 입력을 포함한 통제 변경·실행안을 준비한 뒤 새 승인 범위에서 진행해야 한다. 이번에는 observer 변경, 우회 실행, 테스트 기대 완화, 실패 후 재시도/새 후보 실행을 하지 않았다.

### Commit Preparation, Review And Retention

[누적 리뷰 packet](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-02/CUMULATIVE-REVIEW.md), [commit 파일·메시지](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-02/COMMIT-PREPARATION.md), [결과 요약](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-02/REPORT.md)을 로컬에 준비했다. 새 누적 입력은 현재33 path 전부의 diff·untracked bytes를 포함한다. 과거 packet은 그대로 유지한다. 단일 Claude context 적합성은 미확인으로 남기며 실제 review 재개 전 검토 입력/명령·auth·model/session 경계를 정해야 한다.

중간 commit은 요청대로 정확한 목록과 메시지를 준비하되 현재 validation FAIL이다. Toolstead Recovery의 “검증 실패 상태로 checkpoint 생성” 금지와 실제 commit 별도 승인 경계를 따른다. Owner가 이 실패 상태를 포함하는 보존용 commit 예외를 명시적으로 승인하기 전 stage/commit/push는 없다. 정상 검증 checkpoint로 오인되도록 실패 파일을 제외하거나 rollback하지 않는다.

Tracking: 이 기존 source Work에 append만 했고 Work Done·DR 상태 변경은 없다. Toolstead STATUS 변경은 필요 없음: 최종 수락·통합·적용에 따른 broader 상태 변화가 없다. 기존 branch/HEAD/index를 유지했다. Source/control 및 두 실행 경계는 미해결 P2·Owner 판단·예정된 누적 리뷰의 입력으로 계속 사용하므로 유지한다. Required ignored 원본·결과·실패 사본은 Toolstead private bundle와 승인된 agent-worktree root에 있으며 tmp가 유일한 사본이 아니다. 이 의존성이 끝날 때 보존과 cleanup 적격성을 재평가한다.


## P2 Consolidated Completion Map And Continued Stop — 2026-10-11

### Latest Owner Direction

Owner는 Claude 사용량 회복 전 이번 P2의 R0 → 실행 → R1 외부 리뷰 대기를 유예하고, 기존 승인 설계·파일 범위 내 구현·테스트·집중 검증·기록과 단계 전환을 허용했다. 새 모델/API 대체 호출, 통제·계약·격리·검증 기준 변경, 기존 예산 초기화, 기존 blocker 우회는 허용하지 않았다. 안정된 checkpoint에서만 commit 파일·결과·미검증 범위·규정 trailer를 제시해 승인을 받는다. 직전 실패 상태 보존 commit의 예외 제안은 승인되지 않았고 현재 승인 요청 대상으로 계속 제시하지 않는다.

### Consolidated Development Completion Criteria

| P2 범위 | 확인된 근거 | 남은 완료 기준 |
| --- | --- | --- |
| A: 보존·복구와 failfast | 이전 A 후보 focused64/64 PASS. 수정 A1/A2·S3 회귀·실제 runner probe4·합성 tear112·S5 복구 오류8 포함 | 통과 결과는 해당 후보와 실제 assertion에 한정한다. 현재 B는 기존224 method AST를 보존했지만 A 전체의 B 후보 재실행 결과는 아니다 |
| A: 관측·해석 미해결 | 합성 tear와 한정된 syscall 관측은 있음 | S1/S2 실제 buffered-write 관측 공백과 전체 member/dir matrix, B-07 retain/retirement 의미 처분. 통제·oracle·계약 변경이 필요한 부분은 별도 판단 전 open |
| B: 실행기·writer fence | focused12 중8 PASS/1 FAIL/3 미시작. four-executor entry, OLD installed late-lock4 및 직접 회귀3 PASS | NEW candidate 정상 대조군 오류 해결 후 pending-prefix4개 및 intent/lifecycle/Work 계열을 확인한다. 남은 writer action/state cell은 유효한 동일 요청 positive, 정확한 refusal, bytes/mode 보존, 실제 lock witness를 충족해야 한다 |
| C: admission·baseline·history | 이전 개별 근거는 역사로 유지. 이번 resume에서는 작성·실행 없음 | Git index/alias/descendant/ignore, schema1 local/schema2 parent·required-ref, worker/orphan/old ticket/proof·rebind, mixed OLD→NEW lifecycle·detach audit, 직접 fixture/caller closure의 잔여 cell 작성·집중 검증 |
| P2 개발 완료 | 부분 검증이며 P2 open | 필수 cell을 실제 결과와 연결하고 fail/error/skip/unstarted/unfinished0, 입력·truth 보존과 종료를 확인한다. 필수 미해결·관측 불가가 남으면 완료로 처리하지 않는다 |
| 외부 리뷰·최종 결정 | Driver 자체 점검만 수행, Claude 신규 호출0 | 누적 diff·원문 finding·Driver 처분·실제 결과/한계를 Claude 복귀 후 검토. 독립 리뷰·Owner 최종 수락·활성화·실제 적용과 구분. P3/P4로 자동 확장하지 않음 |

### Existing Blocker And Minimum Recovery Proposal

`DRIVER-B1 / needs-user`는 계속 유효하다. `candidates._candidate_bytes()`는 게시 후 `os.open(..., dir_fd=fd)`로 결과를 읽지만 현재 NEW observer는 dir_fd를 거부한다. 원인 후보는 이 충돌이며 내부 traceback/추가 재현은 없어 정적 추론으로 남긴다. 후보 파일 게시와 parent sync 후 exit70이므로 실패를 no-write refusal로 해석하지 않는다.

기존에 명시적으로 승인된 보정은 A1/A2와 runner의 `failfast=True` 한 줄이다. 이 보정은 적용·검증됐으며 observer 보정 권한으로 확장되지 않는다. 외부 리뷰 대기 유예는 이 통제 변경 경계를 없애지 않는다. 이번 지시에 따라 남은 조건과 고정 입력을 읽기 전용으로 대조하고 기록만 갱신했다. 새 제품/test/control 수정, controller 실행, 실패 재시도는 없다.

최소 복구 범위 제안은 기존 observer의 descriptor-relative 읽기 관측 호환성을 다루는 것이다. 제품의 안전한 dir_fd 읽기는 유지하고, observer가 실제 descriptor-relative 경로와 반환 fd를 관측하도록 하되 상대 쓰기·관측 우회나 sandbox 권한 확대를 허용하지 않는다. 승인 판단에는 해당 한 함수의 정확한 delta, 기존 실행 경계 안의 정상 읽기·거부·관측 보존 probe, 실패한 NEW positive와 pending-prefix의 재검증 목록·명령을 함께 제시해야 한다. 새 검증 체계나 full-suite 재실행은 복구안에 포함하지 않는다. 현재 이 안은 복구 범위 제안이며 구현·검증된 patch 또는 실행 가능한 승인 packet은 아니다.

### Existing Budget, Review Input And Commit Gate

기존 batch02 후보2/3, controller12/18, 누적62/68을 유지한다. 남은 산술 상한은 후보1개/controller6회이며 실패 STOP 이후의 자동 재개 권한이 아니다. 기존 deadline은2026-10-10 20:13:57.688320 UTC(2026-10-11 05:13:57 KST)다. 시간·횟수·retry0을 초기화하거나 늘리지 않았다. B 복구·통제 확인·C 전체가 남은 한 후보와 기존 cap 안에 들어간다는 근거는 아직 없으므로 완료를 약속하거나 추가 후보를 만들지 않는다.

직전 누적 packet의33 path manifest와 diff는 그 시점의 고정 입력으로 보존한다. 이번 변경은 이 Work의 reporting-only append이며, 기존 packet에는 이 addendum과 before/after 신원을 연결한다. 기존 실행 결과의 frozen input identity를 현재 문서 hash로 바꾸지 않는다. 향후 안정된 checkpoint에서 cumulative 입력과 commit 목록·메시지를 다시 확정한다. 직전 commit 메시지는 역사적 초안이며 이번 턴의 commit 승인 요청이 아니다.

실패 raw·원본 fixture·보존 사본과 이전 source diff는 기존 durable bundle/agent-worktree에 유지한다. 그 입력을 사용하는 미해결 진단과 누적 리뷰가 남아 있어 checkout을 유지한다. 이번 문서 append도 durable bundle에 정확한 bytes로 보존한다. Work Done·STATUS·DR 상태·index·HEAD 변경, stage·commit·push·PR·merge, 외부 auth/review는 없다.


## P2 Observer Dir-Fd Resume And Budget Stop — 2026-10-11

### Authorization And Applied Scope

Owner actual request: “observer의 dir_fd 읽기 관측 보정과 집중 검증을 승인해. 제품 계약과 격리·검증 기준은 유지하고, 기존 예산 안에서 B 복구 후 남은 P2를 이어가. 추가 통제 변경이나 예상 밖 실패, 예산 부족이 생기면 멈춰 보고하고, Claude 리뷰와 커밋 승인은 별도로 남겨둬.”

기존 남은 후보1개/controller6회 안에서 candidate03을 실행했다. 이전 STOP·예산·결과는 보존하고 이번 Owner 승인만 별도 연결했다. Budget reset은 없다. Source 변경은 observer와 기존 test 파일의 probe 추가뿐이다. 제품 runtime·계약·schema·sandbox/network/credential·나머지 controls10은 그대로다. 기존 baseline은 보존하고 승인된 root 아래 새112파일 bounded baseline에는 동일 observer delta만 적용했다.

Observer는 single-component, no-follow, 읽기 전용 flags의 dir_fd 호출만 새로 지원한다. Parent와 opened descriptor의 path/inode를 대조하고 original open에는 원래 dir_fd를 그대로 전달한다. `open-before`, native audit, `open-after`에 실제 descriptor-relative 경로를 연결한다. 상대 쓰기·unsafe component·nofollow 누락은 거부한다. 기존 namespace writer·fault·lock의 계약은 바꾸지 않았다. Test-local synthetic dispatch probe5개를 추가했으며 이전237 method AST는 그대로다.

Observer SHA: `b41f14a620fed1b34ed0b5b20b6adf226d30698c5f6129e497c489e7fc22d77e`. Test SHA: `dac31c645f694637180b891b374391048fdb6f5b745e713e3927df729dc53b84`. [고정 입력·변경 목록](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-02/candidate-03/authoring.json), [observer delta](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-02/candidate-03/observer.py.patch), [test delta](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-02/candidate-03/test_entry_window_transition.py.patch).

### Actual Execution And Failure

| 범위 | 결과와 한계 |
| --- | --- |
| 준비5단계 | acquire/canary/base collect/smoke20/entry collect PASS. 실제 collection973/default776/factory197은 고정 기대값과 일치 |
| observer 새 probe5개 | 읽기(str/bytes/Path 및 nested fd), 상대 mutation flags 거부, symlink/unsafe component 거부, open-before/open-after fault 모두 PASS. 실제 observer config·hooks·fault를 사용하고 마지막 product dispatch만 고정 synthetic 코드로 대체한 통제 증거 |
| focused23 | 5 PASS/1 FAIL/17 unstarted, error/skip/unfinished0. 첫 실패 이후 test 시작0, native summary와 preservation 생성 |
| B recovery | 전체12개 미시작. 앞선 B RuntimeError가 해결됐다고 주장하지 않음 |
| 기존 회귀5개 | cross-WORK 실패 이후 lock/primitive/context/unobserved-fault 회귀5개 미시작 |
| 종료·보존 | controller exit2/child exit1, natural completion=true, group_absent=true, 입력 불변. 실패 fixture 사본의 bytes/mode/link/dir map 일치 |
| 사용량 | batch 후보3/3, controller18/18, 누적68/68. 이번 controller6회, Claude/auth0. 시간 deadline은2026-10-11 05:13:57 KST 그대로지만 실행 횟수는 소진 |

`DRIVER-B2 / needs-user`: `test_observer_rejects_cross_work_target`는 선행 `collect-p1-controls/work`의 존재를 가정한다. 이번 고정 P2 경로는 `collect-p2/work`를 만들므로 observer child를 시작하기 전 fixture 존재 assertion에서 실패했다. 두 경로의 실제 존재 여부, source723행과 native traceback을 읽기 전용으로 확인했다. 제가 기존 회귀를 선정할 때 선행 fixture 의존성을 확인하지 못한 Driver 준비 오류다. 제품 오류나 dir_fd observer 거부를 재현한 결과가 아니다.

[실제 결과와 raw27개 신원](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-02/candidate-03/result.json), [새 STOP](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-02/candidate-03/STOP.json). 기존 B 실패 원문과 후보02 결과는 그대로다. 실패 후 source 보정·테스트 재실행·다음 후보는0이다. 이전2946개 입력/증거 신원과 각 단계 입력 전후 불변을 확인했다.

### Concrete Recovery Proposal — Not Applied

실패한 test의 선행 경로 선택만 현재 P2 실행 slot에 맞춘다. P1 경로와 기존 존재/다른 WORK/정확한 오류/쓰기 없음 assertion은 유지한다. 실패 test를 제거하거나 skip하지 않는다.

```diff
-            value['target'] = str(work_root.parent.parent / 'collect-p1-controls' / 'work')
+            collection_slot = 'collect-p2' if work_root.parent.name == 'focused-p2' else 'collect-p1-controls'
+            value['target'] = str(work_root.parent.parent / collection_slot / 'work')
```

[적용하지 않은 patch](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-02/candidate-03/recovery-proposal.patch), [정확한18개 선택·hash·예산 제안](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-02/candidate-03/recovery-proposal.json). Proposed test SHA `61d6d0c30274fc6b5fc8e0d37a6c6819662d1b2c6ea2be1b28d2892d8a58a43d`. 새 observer 변경은 이 복구안에 없다. 위 실패1개와 미시작17개를 집중 검증하고, 이미 통과한 새 probe5개는 source/control/probe AST 불변 대조 후 이전 후보 근거로 재사용한다. 동일 후보에서23개가 통과했다고 합산하지 않는다.

기존6단계·동일 runtime/격리·300초 준비 cap·1200초 smoke/focused cap·coordinator180초/child150초·failfast를 유지한다. 필요한 추가 예산은 후보1개, controller6회다. 승인 시 누적 한도는 후보4개/batch controller24회/전체controller74회가 되며 기존 시작·deadline·사용 횟수를 초기화하지 않는다. Exact frozen input과 새 실행 root는 승인 후 준비하며, 남은 시간으로 전체 gate·보존이 불가능하면 실행하지 않는다. 이 제안은 C 전체 검증 예산이나 예상 밖 실패 재시도를 포함하지 않는다.

### Development, Review, Commit And Retention

P2는 미완료다. Observer의 위5개 자체 probe 통과와 B 복구 성공은 구분한다. S1/S2 실제 관측·B-07 처분·B 잔여 전체 matrix·C의 admission/baseline/worker/history/caller closure는 남아 있다. P3/P4·독립 외부 리뷰·최종 수락·활성화·adopter 적용은 별도다.

안정된 checkpoint가 아니므로 commit 승인 요청을 하지 않는다. 이전33 path 목록·dual trailer 초안은 역사로 남기며 이번 source/test/Work delta와 실행 결과를 누적 리뷰 진입점에 연결한다. Source Work append만 기록하고 Work Done·STATUS·DR·HEAD·index·stage/commit/push/PR/merge는 변경하지 않는다.

Source/control과 후보03 실행 경계는 미해결 실패 분석 및 예정된 누적 리뷰에서 계속 사용한다. Raw27개, native failure copy와 고정 입력은 durable bundle/agent-worktree root에 보존돼 있고 이번 Work append의 exact bytes도 bundle에 보존한다. 고유 원본을 tmp에만 두지 않았다. 이전 후보들과 새 baseline도 현재 복구/리뷰 의존성이 남아 있어 유지하며 의존성 종료 뒤 cleanup 적격성을 재평가한다.


## P2 Fixture Recovery Pass And Intermediate Checkpoint — 2026-10-11

### Owner Authorization And Execution Window

Owner의 “계속하자” 및 “참고로 Claude도 리셋되었어. 계속해”는 직전 구체 제안인 fixture 경로 보정·추가 후보1개/controller6회 범위로 해석했다. 재개 시 원래 deadline(2026-10-11 05:13:57 KST)이 지났음을 확인해 시간을 임의 초기화하지 않았다. Owner가 별도 질문에 “검증 창을90분 연장”으로 답해2026-10-11 01:14:31~02:44:31 UTC(10:14:31~11:44:31 KST)를 추가 승인했다. 이전 사용량68과 시작·deadline 기록은 유지한다. Claude quota 회복은 외부 리뷰 호출 승인으로 취급하지 않았으며 새 auth/review0이다.

승인된 patch는 `focused-p2`에서 기존 `collect-p2/work`를 사용하게 하는 test-local 경로 선택뿐이다. P1 경로, 기존 WORK 존재·다른 WORK·정확한 거부 진단·쓰기 없음 assertion을 유지했다. Source test SHA `61d6d0c30274fc6b5fc8e0d37a6c6819662d1b2c6ea2be1b28d2892d8a58a43d`. Observer·다른 controls·제품 runtime·계약·격리는 바꾸지 않았다. 변경 전후 class method AST 대조에서 이 method1개만 달랐다. 초안 authoring 검사에서 containing function까지 비교한 bookkeeping 오류는 freeze 전에 검사 대상을 바로잡았으며 제품/통제 테스트 실행은 아니었다.

### Actual Result And Finding Dispositions

| 범위 | 실제 결과 |
| --- | --- |
| 전체 실행 gate6개 | acquire/canary/base collect/smoke20/entry collect/focused18 PASS. Collection973/default776/factory197 일치 |
| focused18 | 18 PASS; fail/error/skip/expected-failure/unexpected-success/unstarted/unfinished0 |
| fixture 및 관측 회귀6개 | cross-WORK refusal, lock pause, primitive file/namespace fault, context identity, unobserved fault refusal PASS |
| B12개 | four-executor boundary, OLD installed late-lock4, local baseline/OLD independent late-lock/source-operation 회귀3, candidate/intent/lifecycle/Work family4 PASS |
| 후보03 probe5개 | 실제 당시 결과를 보존·재사용. Observer와 probe AST 불변을 대조했지만 후보04에서 재실행한 것으로 합산하지 않음 |
| 입력·종료 | 이전3044개 입력/증거 불변, 각 단계 입력 보존 PASS, 자연 종료·process group 부재 확인. Focused159.265초 |
| 예산 | 추가6회 전부 사용. 후보4/4, batch controller24/24, 전체 누적74/74. 시간 연장 내 종료했으나 횟수 소진으로 추가 실행 중단 |

`DRIVER-B1`: Driver runtime recovery 확인 완료 / 외부 리뷰 대기. OLD·NEW installed candidate positive 모두 `saved`였고, NEW candidate 게시 뒤 `.hrn/planning/candidates.json`의 실제 dir_fd read `open-after`를 관측했다. 이전 후보02의 게시 후 RuntimeError 결과는 그대로 보존하며 소급 통과시키지 않는다. 네 writer family 각각 OLD/NEW 정상 대조군 및 OLD pending prefix4종의 정확한 거부·요청/bytes/mode 보존을 확인했다. 이는 draft/add/publish/detach 대표 동작의 범위이며 모든 writer action을 검증한 것은 아니다.

`DRIVER-B2`: Driver runtime recovery 확인 완료 / 외부 리뷰 대기. 기존 cross-WORK test가 실제 P2 선행 WORK를 대상으로 observer의 정확한 경계 거부를 확인했다. 이전 실패를 숨기기 위한 test 삭제·skip·assertion 완화는 없다.

[후보04 결과·필수 raw 신원](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-02/candidate-04/result.json), [고정 test delta](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-02/candidate-04/candidate.patch), [실행 plan](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-02/candidate-04/execution-plan.json). Synthetic fixtures만 실행했으며 실제 adopter 데이터·프로젝트 적용은 없다.

### Remaining P2 And Separate Decisions

| 남은 범위 | 완료 경계 |
| --- | --- |
| A 관측·해석 | S1/S2 실제 buffered-write 관측 및 전체 member/dir matrix, B-07 retain/retirement 의미 처분은 open. 이전 A64 PASS와 합성 tear는 해당 assertion 근거로 유지 |
| B 전체 matrix | 이번 대표4명령군 외 action/state의 공백을 기존 요구에 대조해야 함. B12 PASS를 전체 all-writer 완료로 확대하지 않음 |
| C admission/baseline/history | Git index/alias/descendant/ignore, schema1/schema2 parent·required-ref, worker/orphan/old ticket/proof·rebind, mixed history/detach 및 caller closure의 잔여 matrix. 이번 추가 예산에는 C authoring/실행 없음 |
| 외부 누적 리뷰 | Claude quota 회복은 Owner가 알렸으나 실제 auth·model/session·입력 context 검증과 호출은 별도 승인 대기. Driver 점검은 독립 리뷰가 아님 |
| 최종 결과 | P2 open. P3/P4·최종 수락·계약 활성화·실제 적용은 별도 승인 |

### Intermediate Commit Preparation And Preservation

이번 B 복구의 한정된 검증 범위는 통과한 checkpoint 후보이므로33 path의 현재 소스·테스트·필요 기록과 메시지를 commit 승인용으로 준비한다. 전체 P2/전체 suite/external review 완료를 주장하지 않는다. [정확한 파일·메시지·검증과 미검증 범위](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-02/candidate-04/COMMIT-PREPARATION.md)와 [누적 리뷰 입력](/Users/kyungseo/dev-home/vibe/toolstead/temp/hv2-integrated-plan-20261008/colvia-verification-bundle-20261009/p1b-p2-batch-01/p2-preparation-01/driver-p2-batch-02/candidate-04/CUMULATIVE-REVIEW.md)을 참조한다. 이전 실패 상태 예외 commit 제안 대신 이번 복구 결과와 남은 P2를 명시한다. 실제 stage/commit/push/PR/merge는 없다.

고정 입력과 이전 오류·보존 사본은 변경하지 않았다. Source 및 baseline/실행 경계는 예정된 누적 리뷰와 남은 P2에서 사용할 입력이 있어 유지한다. Work의 새 append bytes와 누적 untracked 입력도 durable bundle에 보존한다. 임시 실행 산출물은 Git 대상에 넣지 않는다. 소비 의존성이 끝나면 중복 산출물·실행 환경의 cleanup 적격성을 다시 판단한다. Work Done·STATUS·DR 상태·HEAD·index는 유지한다.
