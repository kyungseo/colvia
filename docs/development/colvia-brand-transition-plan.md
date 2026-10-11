# Colvia Brand And Launcher Transition Plan

Date: 2026-10-09
Status: Preliminary plan; no contract activation or implementation approval

## C0 Handoff — 2026-10-09

The Owner approved C0 preparation after this preliminary R0. Subsequent technical progress belongs to [CHORE-20261009-001](CHORE-20261009-001-colvia-entry-contract.md); [DR-0004](../decisions/DR-0004-colvia-managed-entry-and-one-way-transition.md) owns the proposed exact contract. This note and its review retain historical input meaning. Approval did not activate a runtime contract or authorize implementation.

## Purpose And Ownership

The Owner selected Colvia as the product brand and requested a comprehensive transition plan, Claude review, then sequential execution. The chosen direction is to replace the managed `hv2` launcher with `colvia`, retaining `HV2-`, `.hrn/`, and the internal `hv2ref` package. A permanent second launcher, global manager, package distribution mechanism, new runtime or Enterprise product is outside this request.

This source-only note owns the preliminary technical plan and its review under Contributing. It is not a runtime Work, accepted decision, task selection record or publication permission. After exact plan approval, allocate one source development record and link this note as its R0 input; that record owns subsequent progress. Repository/namespace operations and private adopter approvals remain outside this source note. No external private planning record is needed to understand or implement this proposal.

## Observed Starting Point

Read-only inspection of the current source found:

| Surface | Current behavior and implication |
| --- | --- |
| Root launcher `hv2` | A regular, verified file; installed execution compares its bytes with the active release and requires the exact control-launcher path. A symlink or wrapper is not an equivalent rename |
| `src/hv2ref/product.py` | `SERIAL_MANAGED_PATHS` holds 29 paths. Packaging, release verification, root observation, init, switch, repair and detach select `hv2` explicitly |
| History inventories | The 27- and 28-path sets are derived from the current set. Changing the current tuple without preserving explicit old sets would also change the old-history reader |
| `src/hv2ref/work.py` | Snapshot and Git proof exclude only a verified launcher; worker/current-window admission also enumerates inventory IDs. Changing only packaging would misclassify managed code or invalidate proof |
| `src/hv2ref/view.py` and `cli.py` | Commands and the managed adapter path are emitted to users/agents; parser identity and examples use old names |
| Managed adapter | `adapters/harness-v2-work/SKILL.md` is shipped. Its proposed new path is `adapters/colvia-work/SKILL.md`; old retained releases retain the old path |
| Source manuals | Both `manual/en/` and `manual/ko/` need current entry and recovery parity even though they are outside the 29-file managed set |
| Current lifecycle | Independent source execution with explicit `--source-checkout` already exists. An old installed launcher need not implement its own replacement |
| Accepted contracts | DR-0002 owns the exact technical baseline. DR-0003's accepted Public Preview intake explicitly preserves `hv2`; that clause needs a named amendment, not a silent index edit |

This is static source inspection. It proves neither transition feasibility nor compatibility. Historical test counts and old passing summaries do not qualify the proposed change.

## Proposed Contract Decisions

The implementation entry gate must fix and obtain Owner acceptance of all rows below in a new source decision that names the replaced DR-0002 baseline clauses and DR-0003 `hv2` preservation clause only. Preserve original decisions and acceptance byte ranges/digests; use explicit supersession/navigation pointers outside protected ranges rather than rewriting past acceptance. Unaffected intake criteria remain unchanged. Current normative documents may change in C2 only under the new accepted exact baseline. Reserve a decision ID only after checking live and retained IDs.

| Decision | Proposal and bound |
| --- | --- |
| User entry | One managed root `colvia`, with no permanent alias. Retain old `hv2` only in immutable historical releases or a validated incomplete transition prefix |
| Inventory window | Introduce a new explicitly named window; choose its exact ID in the contract Draft. Old checkout-1 readers cannot understand the new launcher path, so do not reuse checkout-1 or claim same-window bidirectional compatibility |
| History | Freeze an explicit window-to-(path set, launcher path, adapter path) table for human-1, worker-1, umbrella-1, planning-1 and checkout-1 plus the new window; new readers preserve old records' meaning and reject unknown windows. Do not derive old sets by substituting names in the new set. Do not rewrite prior release payloads, bindings, receipts or accepted records |
| Supported transition | Direct managed transition from verified checkout-1 only for the first slice. Older installations first need a separately qualified supported path to checkout-1. Mixed retained histories remain readable. Do not invent attach or an export/import migration |
| Transition executor | An exact independent new source drives preview/apply/recover. Retain the exact old source for recovery of old pending operations. No automatic downloading, ambient PATH resolution or execution of a candidate during packaging |
| Old pending operations | Quiesce writers. Refuse migration with an unfinished lifecycle receipt, repair or detach; recover it using its matching source first. For the first slice propose no active linked-worker or unintegrated acceptance/application ticket across cutover; list and refuse pending executable operations without mutation. C0 must distinguish these from ordinary saved candidate ideas, which must not block migration merely for being unselected. Extend transition-through support only with source-grounded preservation proof and explicit scope approval; never silently discard or re-authorize records |
| Downgrade | Propose one-way entry into the new window. Refuse rollback to checkout-1/older after the first durable new-window transition receipt; within-new-window rollback remains required, but it is unavailable as a meaningful prior-release recovery immediately after installing the first new-window release. Explain independent-source repair/recovery and detach/plain reading as recovery paths, without calling detach/re-init a rollback |
| Existing user file | If root `colvia`, including a case-equivalent name on a case-insensitive filesystem, is unowned, modified, linked or ambiguous, refuse without mutation. The adapter lives inside the managed release payload, not an independently installed project-root skill path; use exact release-tree ownership checks. Never assume an absent installed launcher means a free target. After successful migration, a reappearing root `hv2` is not automatically managed: propose stable refusal with byte preservation for this first slice; C0 must define affected operations and old-record proof, rather than deleting or excluding it silently |
| State and IDs | Keep `.hrn/`, `HV2-`, `hv2ref`, record IDs, authority IDs, lineage identifiers and schemas unless the transition contract proves a precise schema extension necessary. Error guidance explains that Colvia still reports stable `HV2-` codes |
| Public-facing text | README, help, current manuals and verified adapter discovery consistently identify Colvia and `./colvia`. Historical generation contracts and past evidence keep their original names. No change in maturity, platform or capability claims |

The exact new window and any switch/detach plan schema changes remain open. R0 approval of this plan alone does not accept those technical choices. In particular, prove how a stale old lifecycle executable fails safely on every new durable prefix before authorizing implementation.

## Transition State Design Required Before Coding

Produce a small table specifying, for each step, on-disk launcher names/bytes, binding state, durable receipt state, permitted reader/writer, repeat behavior and refusal behavior. Required boundaries:

1. Before preview and after preview: no writes; capture exact old binding/release, new release and target identity.
2. First durable transition receipt, with old launcher and binding intact.
3. Partial and complete candidate staging, then published release. Finish rejectable preflight checks (including root collision, exact old launcher, pending operations and complete candidate validation) before the first durable receipt; re-observe required state under the writer guard without treating preflight as a race guarantee.
4. Publication of the verified new launcher while old state still exists.
5. Retirement of only the byte-matching, verified old root launcher and publication of the new binding; choose and justify the order. Do not assume a multi-file atomic rename exists. Do not freeze the sequence above as the mutation order: if old writers can run while old launcher/binding still match, C0 must design an earlier safe interlock and show every resulting prefix.
6. Completed transition and idempotent replay; both names present, missing names, modified names and interrupted prefix observations must be unambiguous.

Old and new launchers temporarily coexisting is an implementation prefix, not a supported alias policy. Do not allow either installed runtime to write in an inconsistent prefix. The independent trusted source must resume exactly or return a stable non-pass while preserving every byte it cannot safely own. Test each durable mutation boundary, not only existing injection labels. Include process termination at newly introduced mutation boundaries where the design depends on durable ordering; distinguish it from simulated exceptions and power-loss guarantees.

After a durable transition receipt, a failure must be recoverable forward under the accepted one-way rule. If that cannot be demonstrated, stop and revise the contract before implementation. Do not weaken verification or substitute manual record edits.

## C0 Evidence Tables

The prefix table crosses every durable state with four executors: old installed launcher, old independent source, new installed launcher, new independent source. Cite actual old-source checks for each permitted/read-only/refused result; a plausible fail-closed story is not proof. No runtime implementation starts while an old writer can mutate a new incomplete prefix. Fix the mutation order and irreversible boundary in the contract, not in a later code review.

A second table crosses target states (normal checkout-1, unfinished old lifecycle, new transition prefix, completed new window and older retained windows) with source identity and init/update/rollback/repair/detach/read operations. Each cell names supported behavior or a stable refusal diagnostic. Identify where only the retained old source works, and distinguish historical reading from lifecycle mutation support. An old installation deferred from migration cannot consume new-window releases; do not call it generally unsupported or forbid a separately qualified old-window fix.

## Implementation Slices And Completion Criteria

| Slice | Scope | Required exit evidence |
| --- | --- | --- |
| C0: Contract | New transition decision and named supersession clauses; window/path mapping with baseline-derived legacy fixtures; four-executor prefix proof; source/target/command support matrix; irreversible boundary, pending/worker and reappearing-root policy; source task/runner plan | A separately identified contract R0 and Driver dispositions; source-line evidence that old writers refuse every new durable prefix; exact Owner contract/plan acceptance before runtime edits |
| C1: Core transition | `hv2` to `colvia`; product lifecycle, bootstrap/CLI, runtime seam, snapshot/worker proof and consumer allowlists, independent auditors | Focused positive/refusal/interruption tests; no project truth rewrite; no unsafe execution prefix; historical mixed inventory read |
| C2: User surfaces | Managed adapter rename, current managed docs, README/AGENTS/CLAUDE, help and next-action text, EN/KO source manuals and capabilities claims | Exact packaged inventory; installed discovery and first-work/resume/recovery actions; translation/claim parity and no stale executable instruction in current paths |
| C3: Qualification | Freeze cumulative candidate after code/docs converge; normal and parent-optimized complete regression plus exact-artifact lifecycle scenarios | Exact candidate/runtime/runner identity, test selection and executed IDs/results, drift check; new assertions distinguished from historical evidence |
| C4: Result review | Claude R1 of final diff and evidence, Driver disposition, generic adopter impact | Owner result acceptance; remaining limits and reusable qualification anchor identified; source publication/adopter application still separately authorized |

C1 and C2 form one qualified change. Do not ship a renamed launcher with an old managed adapter or stale recovery instructions. User-facing prose can be drafted early, but no intermediate mixed release is an install candidate. An inventory classifies launcher invocations, adapter paths and current brand tokens as current instruction, frozen history, old-window fixture or unresolved. Stable `hv2ref` and `HV2-` identifiers are classified by rule, not individually. Do not pursue zero occurrences of `hv2`.

## Validation Plan

Planning prose: check links, rendered Markdown, explicit open decisions, source authority and sanitized disclosure. No product suite is needed for this preliminary note.

For implementation, Maintaining classifies this as lifecycle/record/recovery risk. The new window and launcher path invalidate a prose-only exemption; require complete normal and parent-optimized regression on the fixed candidate, in addition to focused iteration. C0 records baseline collection and test-selection rules, runtime executable/build/digest, runner/policy, write/output boundary and duration budget before execution. Final discovered/executed IDs and counts are fixed against the implemented candidate at C3; do not pretend new tests already exist in C0. No new dependency or unbounded shell permission is implied. Retain credentials out of the test process, deny network, and constrain all writes to synthetic targets under the approved execution boundary. A worktree is not a sandbox. Set a measured duration plus explicit margin; exhaustion is incomplete, not pass, and never silently raises the limit.

Required scenario matrix:

| Group | Cases and preservation assertions |
| --- | --- |
| Fresh installation | Git and non-Git targets; root collision/link/unsafe path/unsupported runtime refusal; packaged identity and mode; colvia-only successful entry |
| Migration | Exact checkout-1 source/target; mixed old retained releases; preview drift/token/source changes; all durable prefixes and replay; stale old source/launcher commands after the new receipt; same result or stable refusal |
| Runtime and workers | Ordinary intent/Work/candidates; active linked worker read/submission/integration; CRLF and attributes proof; verified launcher exclusion; active/pending ticket preservation or explicit refusal; no accidental launcher content in project evidence |
| Lifecycle after migration | Within-window update/rollback using a second synthetic new-window candidate; cross-window downgrade refusal; exact repair of old and new prefix damage; schema/version pair checks; detach and plain-reader invariance with old/new history |
| Safety | Project-authority bytes and secret sentinels unchanged by lifecycle; modified/unowned launcher preserved; drift/concurrent writer refusal; no outside-boundary writes/network; independent auditor observes retained truth |
| User experience | Installed view selects correct current manual/adapter; first-work and fresh-session resume examples in EN/KO; broken/missing launcher recovery; error code explanation; source and installed invocation are distinct |

R1 includes static reasoning about old-reader behavior; a test suite whose expected paths were changed wholesale is insufficient. Before C1 edits, derive legacy fixtures from the fixed baseline and record their digests for the identified transition-test consumer. Keep old-source negative controls and immutable legacy fixtures so both implementations do not share the same mistaken assumption. No actual adopter data, private project identity or credentials enters this source.

## Risk, Reversal And Stop Conditions

L3 planning risk: names participate in managed ownership and proof. Repository display rename is operationally separate from installation migration. Source-only edits can be reverted before application; once new-window receipts exist, ordinary old-window rollback is proposed to be unsupported. Preserve independently runnable recovery source and retained releases before any target application. The old recovery baseline is revision `238514686078ce1564010a7b69013f48a635c57c`; C0 records a recoverable acquisition method and exact artifact/source digest, and separately fixes the new candidate. A deferred old installation keeps that qualified old support path; a new-window candidate does not become an old-window repair candidate. Any later old-window maintenance needs separate qualification. Before the first real one-way migration, the target owner must preserve an external whole-target copy (including `.hrn/`, required uncommitted/ignored data and Git/worktree relationships) and verify restoration on an isolated copy. This is target recovery preparation, distinct from retaining product source; it does not authorize restoring over live concurrent work. C0 places either minimal relevant namespace checks or explicit Owner acceptance of remaining renaming risk before any actual adopter mutation. Do not promise an OS crash or rollback guarantee not demonstrated by the exact candidate.

Stop on an unresolved contract/schema choice, unexpected source drift, missing recovery source, unsafe/unowned target, failed integrity or isolation check, unsupported runtime, exhausted budget or inability to retain required state. Record the failed observation and one bounded recovery proposal; no deletion, force operation or repeated unapproved mutation. Source result acceptance does not require every private adopter to migrate unless explicitly added to its completion criteria.

## Planning Authorization And Next Gate

On 2026-10-09 the Owner requested the integrated plan update, comprehensive Colvia brand cleanup planning, Claude review before execution, and deeper inspection. This authorizes this note and its static review. It does not accept the unresolved transition contract or authorize Git publication, repository settings changes, actual adopter mutation or public release. The next technical gate is C0 exact contract/plan review and Owner acceptance.

## Preliminary Review

### Request And Input Identity

Preliminary plan R0, executed 2026-10-09, separate from the future C0 exact-contract R0. The Owner explicitly authorized transmitting the fixed 39,830-byte packet to the Claude subscription service. Codex was Driver; a fresh Claude Code invocation reviewed only selected input, with tools/MCP/slash commands/session persistence disabled. Authentication observed: `claude.ai` / `firstParty` / `pro`; no credential or account identity recorded. Actual model reported `claude-opus-5-5` (Claude Opus 5.5), session `06ca73d8-60e3-4c5a-b8e5-c2fd77a55bf0`; exit 0, 226.18 seconds, no stderr, 600-second limit. No tests or reproduction ran. Context independence is limited to a fresh session and Driver-selected packet; it is not an independent full-repository audit.

Base revision: `238514686078ce1564010a7b69013f48a635c57c`. Tracked diff was empty, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. The reviewed untracked plan was outside that diff: SHA-256 `b8bb561c4f07245f51ab2ee1bcf208f93358f9a56e7325c064488edab0a0ac91`. Packet SHA-256: `11dc8f059a2e2d69013a0d2f53e04bb9e93aa167778873a61ec680d371811d2c`. Source excerpts were taken from that base in product.py, hv2, Maintaining and the development index, with whole-file hashes recorded in the packet. All six input-file hashes matched immediately before recording the result. The Driver's attempted Contributing lines 150–166 were beyond the file length and supplied no text; do not claim the reviewer verified that procedure. Future C0 review must supply real authority ranges, DR bodies and the missing preflight/init/repair/detach/worker consumers.

The operational sequence was supplied as a generic synopsis, not private repository identifiers or a full operations document. Its readiness assessment is bounded to that synopsis. The response below is verbatim; subsequent plan edits above reflect Driver dispositions and have not received another Claude review.

### Reviewer Response — Verbatim

````text
# Colvia 전환 예비 계획 R0 검토

## 판정

**조건부 수정 요구입니다.** 방향은 타당하고 C0 준비의 입력으로 쓸 수 있지만, 아래 F1–F4가 C0 종료 조건에 들어가기 전에는 런타임 코딩 근거로 쓸 수 없습니다. 이 판정은 정적 검토이며 Owner 수락이 아닙니다. 실행·테스트는 하지 않았으므로 어떤 항목도 "통과"가 아닙니다.

**증거 한계**
- 관찰: 추적 diff 다이제스트는 빈 입력의 SHA-256과 같습니다. 검토 대상은 미추적 계획 1건입니다.
- 관찰: 29개 경로와 27/28 파생 집합은 `product.py:48-62`와 일치합니다.
- 미제공: `work.py`, `view.py`, `cli.py`, 어댑터, DR-0002/0003 본문, `_switch_preflight`, init/repair/detach 본문. `CONTRIBUTING.md:150-166`은 내용이 비어 있습니다.
- 따라서 계획 21–26행과 10행의 소유 주장은 검증하지 못했습니다.

## 주요 발견

**F1 (High) 이름이 바뀌면 기존 fail-closed 인터록이 사라집니다.**
- 관찰: 현행 전환은 같은 경로의 런처를 교체한 뒤 바인딩을 게시합니다(`product.py:833-839`). 런처는 창 일치와 "루트 런처 = 바인딩 릴리스 바이트"를 요구합니다(`hv2:60-62, 85-86`).
- 추론: 그래서 현행 after-launcher 접두 상태는 구·신 양쪽에서 실행이 거부됩니다. 개명 후에는 첫 영수증(계획 54행)부터 새 런처 게시(56행)까지 구 `hv2`와 구 바인딩이 서로 일치하므로 구 런타임이 그대로 실행됩니다.
- 증거 없음: 구 런타임이 미지의 미완료 영수증 아래에서 쓰기를 거부하는지. 계획 47행이 증명을 요구하지만 C0 종료 증거(68행)에는 없습니다.
- 교정: C0 산출물에 접두 상태별 표를 넣습니다. 실행자 4종(구 설치 런처, 구 독립 소스, 신 설치 런처, 신 독립 소스)의 결과를 구 소스 행 번호로 인용합니다. 57행의 순서 선택은 이 표로 C0에서 확정합니다. 구 런처를 무력화하는 변이(바인딩 전환 또는 구 런처 은퇴)가 다른 루트 변이보다 먼저 올 수 있는지도 검토합니다. 구 런타임이 쓸 수 있는 접두 상태가 하나라도 남으면 구현 금지입니다.

**F2 (High) 소스 × 대상 상태 × 명령 지원 표가 없습니다.**
- 관찰: 런처는 창 리터럴 하나만 선언합니다(`MAINTAINING.md:85`). 패키징은 현재 집합만 읽고(`product.py:180-186`), 미지의 창은 거부합니다(`:66`).
- 추론: 신 소스는 checkout-1 후보를 만들 수 없습니다. 미적용·보류 채택처는 구 소스로만 수리·분리되며 사실상 동결됩니다.
- 계획 39–41행과 99행은 이 결과를 명시하지 않습니다. 97행의 "복구 소스 보존"에는 식별자가 없습니다.
- 교정: C0에 표 하나를 둡니다. 대상 상태는 checkout-1 정상, 미완료 수명주기, 전환 접두, 신규 창, 이전 창입니다. 명령은 init/update/rollback/repair/detach/읽기이고 각 칸은 지원 또는 거부 코드입니다. 구 복구 소스는 Identity의 base revision과 다이제스트로 고정하고 취득 절차를 적습니다. "보류 = 마이그레이션 전까지 갱신 없음"도 명문화합니다.

**F3 (High) 롤백 경계의 실제 의미가 과대 표현될 수 있습니다.**
- 관찰: 롤백은 보존된 릴리스만 사용합니다(`product.py:794, 813-814`).
- 추론: 전환 직후에는 신규 창 릴리스가 하나뿐입니다. 42행의 "창 내 롤백 유지"는 첫 Colvia 릴리스 결함의 복구 수단이 아니며, 실제 복구는 독립 소스로 하는 전진 갱신뿐입니다. 또 귀환 불가 지점이 영수증이면 디스크가 아직 구 상태 그대로인데도 전진만 허용됩니다.
- 교정:
  1. 귀환 불가 지점을 C0에 명시합니다.
  2. 거부 가능한 검사(충돌, 구 런처 바이트, 미완료 작업, 후보 전체 검증)는 모두 첫 영수증 이전에 끝낸다고 규정합니다.
  3. 89행 롤백 시험에는 두 번째 합성 신규 창 후보가 필요함을 적습니다.
  4. 운영 계획에는 실제 변이 전에 `.hrn`을 포함한 대상 전체의 복원 검증된 외부 사본을 게이트로 추가합니다. 계획의 "independent recovery source"는 제품 소스이지 대상 백업이 아닙니다.

**F4 (Medium-High) 구 경로 집합 동결에 독립 오라클이 필요합니다.**
- 관찰: 구 집합은 현재 집합에서 파생됩니다(`product.py:61-62, 67`). 런처 경로도 `payload/hv2`(`:186, :214`)와 `hv2`(`:799, :833-835`)로 하드코딩되어 있습니다.
- 추론: 필요한 것은 경로 집합만이 아니라 창 → (경로 집합, 런처 경로, 어댑터 경로) 매핑입니다. 구·신 구현이 같은 치환 실수를 공유하면 테스트가 잡지 못합니다. 93행은 방향만 있고 픽스처 출처가 없습니다.
- 교정: 5개 창과 신규 창을 리터럴 표로 고정합니다. 레거시 픽스처는 C1 편집 전에 base revision에서 생성하고 다이제스트를 기록합니다. 신 집합에서 치환으로 구 집합을 계산하는 것은 금지합니다.
- 참고(추론): 구 런처는 `entries["hv2"]`를 무조건 조회합니다(`hv2:80-81`). checkout-1을 재사용하면 안정적 거부가 아닌 예외가 날 수 있으므로 37행의 신규 창 결정은 타당합니다.

**F5 (Medium) 미완료 티켓과 연결 워커 정책이 미결인데 범위는 넓습니다.**
- 관찰: 41행은 "보존 증명 또는 중단"으로 열려 있습니다. 88행은 활성 워커가 전환을 통과하는 시험을 전제합니다. `work.py`가 없어 증명 가능성은 판단할 수 없습니다.
- 교정: 첫 슬라이스 기본값은 "활성 연결 워커, 미통합 티켓, 미결 후보가 하나라도 있으면 목록과 함께 무변이 거부"로 둡니다. 관통 지원은 C0가 소스 행으로 보존을 증명할 때만 추가합니다. 완료된 과거 기록은 기록된 창의 제외 규칙으로 읽습니다.

**F6 (Medium) 완료 후 루트 `hv2`와 충돌 조건이 미정입니다.**
- 관찰: 36행과 58행은 접두 상태만 다룹니다. 완료 뒤 사용자 파일이나 과거 Git 체크아웃으로 `hv2`가 다시 나타나는 경우의 의미가 없습니다.
- 교정: 신규 창에서 루트 `hv2`는 비관리 프로젝트 파일로 정합니다. 증명에서 제외하지 않고 update/rollback/repair/detach가 건드리지 않습니다. 대안은 안정적 거부이며, 어느 쪽이든 음성 대조를 추가합니다. 대소문자 무시 파일시스템에서 `colvia` 변형 이름 충돌도 거부 사례로 명시합니다.
- 추론: 제공된 switch 코드에서 루트에 쓰는 관리 파일은 런처뿐입니다. 43행의 "새 어댑터 경로 충돌"이 페이로드 밖 경로를 뜻하는지 밝히고, 아니면 삭제합니다.

**F7 (Medium) 저장소 개명 후 "현재 내비게이션 갱신"이 출하 경로를 건드릴 수 있습니다.**
- 관찰: README, AGENTS, CLAUDE, `docs/*`는 관리 경로입니다(`product.py:49-53`). 문서 변경도 릴리스 정체성을 바꿉니다(`MAINTAINING.md:89`). 74행은 혼합 중간 릴리스를 금지합니다.
- 교정: 개명 직후 편집은 비출하 파일로 한정하고, 관리 경로는 C2로 미룹니다.
- 개명 사전 점검에 배포 키, 앱 설치, 포크, URL 고정 소비자를 추가합니다. 확인이 안 되면 Owner가 수락한 잔여 위험으로 기록합니다. 구 이름 재사용 금지와 "되돌리기 = 재개명"도 적습니다.

**F8 (Medium) DR 개정 방식이 모호합니다.**
- 관찰: 32행은 "개정"과 "원본 바이트 보존"을 함께 요구합니다.
- 교정: 지정 조항만 대체하는 신규 결정 레코드로 확정합니다. 원본 파일은 바이트 동일성을 다이제스트로 확인하고 색인에는 포인터만 추가합니다.
- "미지·사용자 수정 바이트의 삭제 0건"(`docs/development/README.md:142`)이 구 런처 은퇴에도 적용됨을 명시합니다. 은퇴는 바이트가 일치하는 검증된 런처에만 허용합니다.

**F9 (Medium) 이름 확정 시점과 일방향성이 결합됩니다.**
- 추론: 공개 상표·도메인 확인은 별도로 미뤄져 있습니다. 이후 이름이 다시 바뀌면 두 번째 일방향 창 전환이 필요합니다.
- 교정: 브랜드 재논의 없이, Owner가 C0에서 이 잔여 위험을 명시 수락하거나 첫 실제 채택처 변이 전에 최소 확인을 하도록 게이트 위치만 정합니다. 레지스트리 선점은 필요 없습니다.

**F10 (Low) 과잉·조기 명세입니다.**
- 80행: C0에 "정확한 테스트 수"를 적는 것은 이릅니다. C0에는 base 기준선과 선택 규칙만, 실행 ID는 C3에 기록합니다.
- 74행: 전수 분류는 런처 호출, 어댑터 경로, 브랜드 토큰으로 한정합니다. `hv2ref`와 `HV2-`는 규칙 단위로 분류합니다.
- 60행: 프로세스 종료 시험은 새로 생기는 변이 경계로 한정합니다.
- 68행의 "R0"는 이번 예비 R0와 이름이 겹치므로 입력 정체성을 구분합니다.

## 일방향 전환 평가

**정당합니다.** 구 런처와 구 리더는 신규 창을 읽지 못합니다(`hv2:60-62`, `product.py:66`). 같은 창이면 양방향 호환이 의무이고, checkout-1도 첫 영수증 이후 다운그레이드를 거부한 선례가 있습니다(`MAINTAINING.md:87`). 역방향 전환기를 만드는 쪽이 오히려 과잉입니다. 다만 근거는 레코드 비호환이 아니라 런처 경로와 리더의 한계입니다. 그 비용(F3)을 계약에 정직하게 적어야 합니다.

## 선택 사항

- 첫 채택처 적용 뒤 관찰 보류 지점을 두고 다음 대상으로 진행합니다.
- 마이그레이션 완료 안내에 "프로젝트 소유 진입 파일의 `./hv2`와 구 어댑터 참조는 자동 수정되지 않음"을 넣습니다.
- 후속 우선순위(작업 지속 계약 검토 → 운영 진입 검증 → 로컬 규칙 정리) 순서는 타당합니다. 각각 별도 릴리스 정체성으로 유지하고 C2에 묶지 않습니다.

## 준비 상태

| 대상 | 평가 |
| --- | --- |
| (a) 비공개 저장소 개명 | **조건부 가능.** 기술 계약과 독립적이고 되돌릴 수 있습니다. 조건은 Owner의 정확한 대상 문자열 별도 승인(계획 103행은 이를 승인하지 않음), 직전 재확인, F7 반영, 실패 시 실제 결과를 관찰한 뒤에만 재시도입니다. |
| (b) C0 계약 준비 | **착수 가능.** C0 종료에는 F1–F6과 F8 산출물이 필요합니다. |
| (c) 런타임 구현 | **불가.** 신규 창 ID, 변이 순서, 구 리더 증명, 지원 표, 귀환 불가 지점, 워커 정책, 스키마 변경 여부가 미결입니다. |
| (d) 실제 채택처 변이 | **불가.** C3/C4와 Owner 결과 수락, 대상별 승인·정지, 복원 검증 사본, 구·신 복구 소스 식별이 모두 선행되어야 합니다. |

## 최종 권고

계획의 골격(신규 창, 구 집합 동결, 독립 소스 실행, 영구 별칭 없음, C1+C2 단일 자격 변경)은 유지하십시오. Driver는 F1–F4를 C0 종료 증거 행에 명시적으로 추가하고, F5·F6은 좁은 기본값(거부)으로 결정하십시오. F10의 과잉 요구는 줄이십시오. 저장소 개명은 F7 조건 아래 C0와 병행할 수 있습니다. 런타임 코딩은 C0에 대한 별도 검토와 Owner의 정확한 수락 이후에만 시작해야 합니다.
````

### Driver Disposition

| Finding | Disposition | Applied correction or limit |
| --- | --- | --- |
| F1 | accept | C0 must provide four-executor source-grounded prefix proof, choose ordering/interlock and prohibit coding with a writable inconsistent prefix. This is an unresolved design risk, not a reproduced defect |
| F2 | revise | Added source/target/command table and exact old baseline/recovery identity requirement. Deferred old installations cannot use new-window candidates; this does not prohibit separately qualified old-window maintenance or prove all old installations frozen |
| F3 | accept | Explicit first-release rollback limit, pre-receipt preflight, second synthetic candidate, and restoration-verified external target backup before actual one-way migration; no claim that product source alone backs up target data |
| F4 | accept | Explicit per-window inventory/launcher/adapter mapping and baseline-derived legacy fixture provenance before C1; no new-to-old name substitution oracle |
| F5 | revise | Narrow default refusal for active linked workers/pending executable operations. Ordinary unselected candidate ideas are durable planning records and do not become a new migration blocker merely because unresolved |
| F6 | revise | First-slice proposal is preserved, stable refusal for a reappearing old root launcher, with exact affected operations to be decided in C0; case-equivalent colvia collisions and actual managed payload boundary added. No extra project-root adapter installation invented |
| F7 | accept | Private operational plan restricts immediate navigation edits to non-shipped surfaces, defers managed edits to C2 and adds external key/app/fork/pinned-URL dependency checks without reading credentials |
| F8 | revise | New decision names superseded clauses; protect original accepted decision/ranges/digests and unaffected criteria. Do not freeze every current normative document forever: C2 updates its exact baseline under the new accepted decision. Retire only verified byte-matching old managed launcher |
| F9 | accept | Put minimal namespace review or explicit residual naming-risk acceptance before actual adopter mutation; no blanket registry reservation or legal-clearance claim |
| F10 | accept | C0 baseline/selection rules versus C3 final IDs/counts separated; token inventory and process-termination tests bounded; preliminary plan R0 distinguished from exact-contract R0 |

Optional suggestions: accept a first-adopter observation stop before the second; explain that project-owned entries are not automatically edited; preserve independent follow-up scopes. The operational record owns those target-specific actions.

### Owner Decision And Remaining Gate

The Owner authorized the review packet transmission, not a reviewer verdict or the new technical contract. Runtime implementation, exact new window/schema, lifecycle ordering, actual application, Git and publication remain unapproved. The corrected plan is ready to prepare C0; C0's exact artifacts still require their own R0, Driver disposition and Owner acceptance. No product code or installed state changed in this preliminary planning round.
