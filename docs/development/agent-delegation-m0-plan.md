# Delegated Acceptance M0 Plan

- Status: M0 result ready for Owner decision; Claude R0/R1 and bounded correction reviews complete with no remaining material M0 finding. Product contract and implementation remain unaccepted.
- Date: 2026-10-16.
- Source baseline: `d86bd1fd7754144e5c8538712724ae78571941bf`, remotely reconfirmed on 2026-10-16.
- Owner direction: prepare the delegated-acceptance M0 contract and bounded implementation plan; preserve extension paths for multiple backends, independent projects and fuller agents. On the same date, require Claude Code plan/result review for this work and ensuing work.
- Roles: Codex Driver; Claude Code Reviewer; human Owner accepts material policy, scope and results.
- Progress owner: this source-only preliminary note. No development record ID or runtime Work is allocated yet. This note follows the pre-task review route in [Contributing](../../CONTRIBUTING.md#review-and-execute).
- Effect: none on current runtime, existing candidate selection, accepted contracts, Git publication or adopter installations.

## Practical Conclusion

Proceed first with the contract for one delegated acceptance of one ordinary isolated-worker Work. Keep the execution backend, the process lifetime, and selection of a follow-up separate. The first implementation must connect the complete Work reader/writer and installed compatibility surface; a writer-only exception is insufficient.

Design the extension boundaries now. Implement only the one-home, one-Work, one-grant contract after its bounded plan is accepted. Backend names, provider credentials, process handles and central portfolio state must not become Core authority. Multiple projects remain independently usable without a coordinator.

Continuation remains a separate candidate and retains its existing portfolio priority. M0 preparation does not select it, move it behind Agent work, or turn it into a technical prerequisite for delegated acceptance. Scheduling M1 is an explicit Owner choice. See [DR-0001](../decisions/DR-0001-work-continuation-selection-and-recovery.md).

## M0 Scope And Completion

This round produces a reviewable contract recommendation and an implementation plan, not a running agent or an activated authority exception.

| Included | Excluded |
| --- | --- |
| Reconcile the earlier acceptance design with the exact current source | Product source implementation, real home mutation, candidate/Work/STATUS changes |
| Define grant, one-use, re-selection, revocation, recovery and CONT boundaries | New intent acceptance by agents, Git authority, parent delegation, redelegation |
| Enumerate all reader/writer/window impacts and exact proposed schema | Scheduler, daemon, multi-backend implementation, central project registry |
| Inspect one host candidate using official documentation and local protocol export | Model calls for a worker, host execution pilot, authentication changes |
| Claude R0 plan review, Driver dispositions, bounded corrections, Claude R1 result review | Commit, push, PR, merge, release, adopter application |
| Document implementation test obligations and remaining host qualification | Treating static checks or historical test passes as new runtime support |

M0 completes technically when these recommendations, source mapping, compatibility choice, host evidence limits and bounded next-stage gates are internally consistent, links/rendering pass, and review findings have explicit dispositions. Owner result acceptance remains separate. Any material unresolved contract choice is identified rather than silently defaulted.

The source development procedure requires R0 before execution approval and R1 before result acceptance. The Owner has authorized M0 preparation and this review cycle. M1/M2 remain a future plan requiring their own exact execution authorization. Continuing reviews use the same Driver/Reviewer/Owner separation.

## Authority And Extension Boundaries

```text
Owner accepts exact intent + bounded grant
                  |
                  v
Core: resolve authority -> validate Work graph -> publish decision -> apply result
                  ^
                  | exact payload; no caller-supplied authorization verdict
Host boundary: bound caller + action + immutable payload -> narrow Core operation
                  ^
                  |
Backend adapter: request / observe / stop / collect execution evidence
                  ^
                  |
Optional coordinator: selects a target's existing entry; target revalidates locally

CONT: follow-up choice only; no new grant, execution or result-acceptance authority
```

These are responsibility boundaries, not a commitment to separate services, classes or packages.

| Boundary | Stable meaning to establish now | First implementation | Extension trigger |
| --- | --- | --- | --- |
| Core authority | Qualified home/object/revision references; Owner and acting delegate differ | One explicit grant, action accept, ordinary isolated-worker | Additional authority actions need a separate contract/version |
| Host authorization | Caller binding is checked outside Core; Core independently checks stored authority | One separately qualified local path | A second host must pass the same denial/recovery obligations |
| Backend | Provider/model and session handles are execution metadata | No backend dependency in Core; one prototype path after approval | Actual second backend, not a generic plugin SDK first |
| Execution | Work survives attempt/process replacement; termination is not acceptance | Reuse existing attempt identity semantics; no new lifetime store | Observed restart/stop/reconnect need justifies a supervisor |
| Project | Home identity scopes authority; local path is a locator, not identity | One home, no cross-home write | Multiple independent targets with target-local checks |
| Coordination | No central accepted-result or grant truth | No registry/dispatch service | Repeated real need plus explicit cross-project policy |
| Review | Findings inform a decision; review PASS cannot accept a Work | Claude reviews this plan/result | Optional review integration retains the same authority separation |

Backend capability evidence belongs to the host adapter. Unsupported or unknown capability must refuse the requested mode; no silent downgrade to broader filesystem access or human-identity execution. An execution handle is opaque and may be replaced without changing the grant. Automatic retry/fallback after an ambiguous Core write is prohibited; first reconcile durable Core state.

Do not add unused extension fields, arbitrary action arrays, provider discriminators to Core truth, a universal task object, a second completion ledger or a global service locator. Use a few internal functions around verified authority resolution; only extract a module when current dependency/cycle or testing pressure requires it. Future flexibility comes from independent meanings and fail-closed version transitions.

## Proposed Grant Contract

| Principle | Required meaning |
| --- | --- |
| I1 Authority | Owner unchanged; only exact Owner intent acceptance activates a grant. |
| I2 Binding | Match home, Work, exact draft, delegate, ordinary mode and revision scope. |
| I3 Action | Accept only; no other Owner action is inherited. |
| I4 Freshness | New authority requires current intent; historical binding has separate limits. |
| I5 One Use | First lawful durable delegated decision consumes K, including after cancel/revoke. |
| I6 Payload | Host binds actual immutable full ticket, not a command prefix/path. |
| I7 Existing Checks | Preserve baseline, manifest, evidence, CAS, guard, pending and bytes/modes. |
| I8 Recovery | Owner-approved same-decision recovery retains original actor/identity. |
| I9 No Inheritance | Relations, actor names and parent approval create no grant. |
| I10 Truth | Readers share verified Core meaning; execution/review status is not completion. |
| I11 Compatibility | Establish reader/writer/window/rollback admission before first new record. |
| I12 Bounded Failure | Unknown authority, drift or unavailable evidence stop new use and preserve state. |

The first unit is one synthetic authority home, one ordinary isolated-worker Work, one delegate distinct from the Owner, and two exact text paths. For the first host/quality qualification, propose a delegate execution distinct from the result-producing execution and a protected fixed oracle. This first-pilot policy awaits Owner acceptance; distinct actor/model names do not prove independence. Core-only records cannot authenticate execution separation. The two paths permit a meaningful mixed-application recovery case. No real adopter data, network effect, deployment or secrets enter the fixture.

### Proposed Persisted Shape

For review, propose a new ordinary `intent-draft` schema version 3. Recheck the unused number before implementation; a collision stops allocation. Version 1 ordinary and version 2 composition records retain their exact historical bytes and interpretation.

Schema 3 has exactly the existing ordinary-draft keys plus `acceptance_delegation`. It does not carry `composition`. The field is mandatory and is the following non-null exact object. No delegation uses existing ordinary schema 1; grant removal uses a fresh accepted schema-1 draft. This avoids a second no-grant encoding:

```json
{
  "action": "accept",
  "delegate_actor": "delegate-1",
  "execution_mode": "isolated-worktree",
  "scope": ["docs/first.txt", "docs/second.txt"],
  "work": {
    "authority_home_id": "home-1",
    "id": "work-1",
    "kind": "work"
  }
}
```

Use existing identifier, canonical path, exact-key, duplicate/alias and canonical JSON rules. Grant home must equal the containing intent's home. Grant scope is nonempty and duplicate-free. Compare its canonical path SET with the target Work REVISION's `scope` set (`work.py:595,726,792`); both must match exactly. This is the allowed path boundary, not the changed-path set. `validate_manifest` (`work.py:320–349`) already permits actual changes that are a subset of revision scope: changing one allowed path is valid, an extra path is refused, and mode-only changes retain current manifest/content checks. The two-path crash fixture changes both paths to exercise mixed recovery. No wildcard or grant-to-revision subset authority is added. The delegate is distinct from the unchanged acceptance authority. Proposed schema-3 `delegate_actor` uses the existing ASCII Id grammar `[A-Za-z0-9][A-Za-z0-9_-]{0,95}` as an opaque local role ID; backend/session/provider identity is mapped by the host, not stored in this ID. Existing Owner and historical actor strings retain exact-string authorization and unchanged bytes. At draft parse/publication, compare the delegate with draft.acceptance_authority: reject exact equality and, when the Owner string is wholly ASCII, ASCII-case-insensitive equality (fold only A–Z to a–z). At bind/use, first require exact equality between Work identity acceptance_authority and the bound draft's acceptance_authority, then repeat those delegate/Owner comparisons. These are schema-3 validity rules shared by ALL historical/prospective readers and writers, not a writer-only rule. No Unicode normalization/casefold or runtime Unicode database determines historical grant validity; non-ASCII Owner strings remain supported and unchanged. This limited collision refusal is not Unicode lookalike protection, principal authentication or proof of execution separation. The host must bind the actual caller to the exact declared delegate ID. Work existence is checked when binding/using the grant, not during draft publication.

The constant fields `action`, `execution_mode` and `work.kind` bind this exact capability. Other values are rejected and require a separately accepted schema extension; they are not configurable future actions.

Ordinary accepted revisions may move between v1 and v3. Preserve `umbrella.check_intent_role`: accepted composition cannot become ordinary; orphan drafts do not fix a role. Existing lawful ordinary-to-composition promotion remains subject to current composition rules and creates no parent grant (v2 has no delegation). Do not reject a whole historical draft collection merely because v2/v3 drafts coexist. Composition-plus-delegation is a separate future contract. Use the accepted selection chain, not version rank or draft timestamps.

The provisional M0 conclusion is that existing Work identity/revision and ticket/decision schemas need no added delegation fields: ticket.intent_ref matches revision.intent_ref, including exact draft revision ID/digest; Work/home and actual actor are already bound. Their existing exact references carry the proposed authority and replay identity. Every normal/historical/prospective path must verify this provisional conclusion in M1; a concrete counterexample returns the revised schema impact for review rather than adding optional fields silently. A delegated target must be an ordinary schema-1 Work revision, with no schema-2 revision in its selected ancestry. A grant does not change ordinary Work into composition Work. After lawful parent/composition promotion, an ordinary grant naming the same Work ID cannot restore eligibility. Preserve selected-role rules; `work.kind == work` alone does not establish ordinary Work. Cover this in V04/V21. Replace the current schema-2 equality shortcut with an explicit validated intent-role classification, not a numeric inequality.

### Use, Revocation And Recovery

The one-use identity is K = (authority home, Work ID, intent ID, exact draft revision ID + digest). Full intent acceptance/selection references separately prove approved binding and currentness. Changing request ID, acceptance ID, selection ID, backend or attempt cannot reset K.

Authorization predicate: the Owner actor retains existing action checks. A different actor is eligible only when it exactly equals the verified grant delegate, action is `accept`, supersedes_decision_ref is null, and every delegation condition passes. Rebind, reject/cancellation and revoke remain Owner-only; an exact historical replay preserves its already validated original actor. A grant for one Work does not remove ordinary Owner authority on other Works sharing that intent; grant target/scope checks govern delegated eligibility, not an invented grant inheritance.

Count lawful delegated accept decisions over the complete verified Work decision history, including unselected, cancelled and revoked decisions. The first durable valid decision consumes K. Exact same-decision replay is not a new use; a second distinct delegated decision for K is invalid. Malformed or unauthorized records invalidate the graph rather than consuming a grant or being ignored.

| Event | Proposed meaning |
| --- | --- |
| Grant exists only in an unaccepted draft | No delegated authority |
| Owner accepts grant and Work binds exact current intent | Eligible for its one new delegated accept after all existing checks |
| Intent current changes or grant is removed | No new use; earlier lawful history retains its meaning |
| Consumed draft explicitly reselected | Still consumed |
| Unconsumed draft explicitly reaccepted | Same grant may reactivate; exact Work binding/rebind is still required |
| Owner directly accepts | Does not consume a delegated decision, but normal Work lifecycle prevents another accept |
| Owner accept then revoke | A separate historical revocation barrier disqualifies old K, including after same-K baseline-refresh rebind and new submit-result. K is not falsely marked consumed; fresh draft and lawful Work transition required |
| Delegate accept then revoke/cancel | K remains consumed; revoke is not a bytes rollback |
| Owner ordinary reject, then lawful baseline-refresh rebind/new result | If K is neither consumed nor barred by selected revoke, it stays eligible; proposed policy for explicit Owner acceptance (V11) |
| Owner accept cancelled by Owner cancellation-reject before durable selection | No delegated consumption or selected-revoke barrier; unused K remains eligible after lawful worker transition. Proposed policy, not implicit approval (V11) |
| New draft grants again | New K is possible only with Owner acceptance and valid Work transition; no implicit reopening |
| Pending decision | Stop new delegated calls; resolve the exact decision through Owner-authorized recovery before intent mutation |

Currentness-based revocation is not irrevocable deletion of a historical grant: explicit reacceptance may reactivate an unused grant. This consequence must be accepted as part of the contract. The first design adds no clock/TTL authority and no permanent revocation ledger.

Define explanatory cutpoints S0=before durable decision, S1=decision/all-pre, S2=mixed, S3=all-post/no selection, S4=selection/no current, S5=current published. These are not new persisted states. Preserve S0–S5 behavior: before decision, refuse without mutation; after durable decision/all-pre, consume and permit only authorized same-decision recovery or lawful cancellation; mixed/all-post state cannot be cancelled; selection/current recovery preserves identity; completed historical replay cannot promote an old result. A host stop request proves neither process termination nor absence of a durable decision.

Historical validation proves exact accepted grant binding, actor/home/Work/revision scope/action, lawful Work transitions and unique delegated K. It cannot reconstruct whether an intent selection was current at decision publication: intent and Work histories have no cross-object total order. Enforce currentness in prepare and again under the apply writer guard for NEW authority. Plain historical reading cannot prove that a writer actually performed that runtime check; actor claims are not authentication.

The Work-prefix predicate is reconstructible: walk the selection ancestry ending at the candidate ticket's `expected_selection_ref`; for each selected revoke resolve the superseded accept and its revision, then derive K only when that exact draft actually contains a grant for that Work. A schema-1/no-grant draft or grant naming another Work creates no delegated-K barrier here. If candidate K matches, refuse a NEW delegated decision even if no delegate consumed K. For this isolated-worker unit, same-K baseline-refresh rebind followed by new submit-result, or same-draft re-selection, does not remove this barrier. The `rework` operation itself is forbidden for isolated workers (`work.py:800`); local-mode rework is outside this first unit. Earlier decisions use their own prefixes, so later revocation cannot retroactively invalidate them. This adds an eligibility predicate without changing one-use consumption. Pending revocation first follows existing pending protection. Fresh K requires a new accepted draft and lawful Work transition. V17 covers both Owner/delegate prior accept, same-K baseline-refresh rebind/new result and fresh-K rebind. V11 distinguishes Owner ordinary reject and cancellation of an Owner accept from cancellation of a delegated accept: only the latter already consumed K.

Duplicate delegated decisions for K are checked across the complete history. Shared-intent changes may affect other Works; no automatic rebind hides that consequence.

Recovery requires human approval for the trusted host to replay EXACT original delegated ticket bytes, retaining delegate actor and decision ID. The delegate gets no automatic retry/recovery permission. New cancellation-reject and revoke tickets always use Owner actor. Core cannot authenticate the human caller; the host must establish that recovery path. The unchanged Core decision retains no proof of separate Owner recovery authorization; that evidence belongs to host qualification (M3/V23), not another Core authority ledger. Unavailable exact replay returns for explicit recovery planning; never replace actor or mint a new accept to bypass it.

## Core Integration And CONT

A single verified authority resolver supplies historical and prospective contexts to Work graph validation. Core reconstructs it from exact records; external callers cannot inject a trusted boolean/map that bypasses resolution. Shape/ref checks precede semantic authorization. Intent parsing must not recursively read Work.

| Current source seam | Required change or check |
| --- | --- |
| `intent.py:workspace_intent_graph`, `_resolve_workspace_intent`, draft publication | New ordinary variant and validated grant context; reject unknown fields/roles; admission before first draft write |
| `work.py:work_graph`, `read_work` | Owner or exact lawful delegate validation; full-history one-use; each delegated decision's own Work-prefix revocation barrier, including historical reads; no circular resolution |
| `WorkStore.publish` | Prospective first/new revision included in context, not only existing graph |
| `WorkStore.prepare/apply` | Same decision validator; guard-protected fresh intent/binding/selection/evidence/content checks |
| `WorkStore._all/_intent` | Shared and independent reads agree; mode/composition compatibility remains explicit |
| `view.py` provisional graph | Proposed graphs share the same historical/prefix validator; actual actor, Owner, grant reference and current eligibility versus historical acceptance shown distinctly |
| `product.py` status/baseline/lifecycle; `candidates.py` admission | All shared/fallback graph paths remain consistent; pending and damaged-state handling preserved |
| `umbrella.py` relationships | Recommend a lawful current delegated child completion may satisfy existing required-child predicates; display its actual delegate and grant. Parent acceptance remains human; Owner combinations unchanged |
| Launcher, inventory, runtime checks and plain auditors | New support window and exact transition/recovery coverage; auditor limitations remain honest |

For Owner adoption, recommend treating a properly validated delegated ordinary child acceptance as a real completed child for existing capture/evaluate/check_history predicates. No second child acceptance is required just because its actor is delegated. Parent view must expose child delegate/grant; the parent's existing integration evidence, currentness and human acceptance remain required. Changing/revoking a child affects current readiness under existing rules, not sealed parent history. This is explicit proposed policy, not inherited authority. V21 covers successful readiness, stale/revoked/pending child refusal, displayed actor and denial of delegated parent accept. Static basis: `umbrella.py:_child_chain/capture/check_history/evaluate` use strict Work graphs and exact accept-chain/currentness evidence; they do not grant parent acceptance.

CONT consumes validated Work state. It neither reimplements delegated authority nor infers authority from an agent's completed execution. Its current Draft requires the source Work Owner for continuation decisions; this grant adds no select/withdraw/cancel-pending authority to CONT and no agent priority change.

Before activation, explicitly amend the broad human-finalization clauses in the development index (L-4 and onboarding), agent/adapter guidance, General Work and related normative contract surfaces for this exact ordinary-Work accept exception. Do not silently reinterpret L-4 as CONT-only. All other prohibitions remain. The new accepted decision must identify exact affected document revisions and effective scope.

Prepare two explicit decision vehicles before implementation authorization: a new source DR titled “Delegated Ordinary Work Acceptance,” allocating the next unused local ID only when that Draft is created, and a named DR-0003 amendment for intake criteria. This M0 note reserves no DR number: retained files/history were checked, but concurrent allocation must be rechecked at creation. The product DR names affected DR-0004 effective successor-set clauses and inherited DR-0002 meaning, exact proposed bytes and activation conditions. The DR-0003 amendment names L-4 and onboarding criteria 4/10/13 plus any related clause found by final impact checking. Preserve accepted historical snapshots.

Proposed amendment text for Owner review: “Human authority remains the default. An Owner-accepted exact intent-bound grant may permit a named delegate one ordinary isolated-worker result acceptance under the separately accepted delegated-acceptance contract. It grants no continuation finalization/reprioritization, intent acceptance, rebind, reject, revoke, lifecycle, Git or parent authority. Single writer means one serialized cooperating Core writer under the existing guard; multiple authorized decision actors do not authorize concurrent same-Work content editing or uncoordinated finalizers.” The human provider-null route remains supported. This is proposed text, not an effective exception.

CONT and acceptance may touch the same reader/window code. Before either implementation, compare the other active plan/branch and choose an explicit integration base; do not create competing window numbers or stale tests. A combined release is possible if separately authorized, not required as a dependency or permission shortcut. The existing linear window rank creates a release integration ordering constraint: freeze rank/predecessor and actual branch order with the Owner before write-capable implementation. Conceptual independence does not imply independently mergeable transitions.

## Compatibility And Reversal Recommendation

Use a new semantic inventory window. The current Maintaining contract requires bidirectional meaning within one window; schema-3 drafts fail old exact-version readers even before acceptance. A same-window feature switch is not the recommended alternative under that contract.

Provisional label `delegation-1` is explanatory, not allocated or active. Its exact inventory, rank, predecessor, paired lifecycle plan/receipt version, old-writer refusal and pending recovery design must be fixed together in the implementation plan before the first write-capable fixture. Do not assume the current lifecycle schema 2 or detach schema 3 can safely contain the new window.

The transition must refuse a reader/writer/rollback target that cannot interpret the new window before changing it. A newly named inventory alone is insufficient: retained old sources, repair/switch replay, detach and plain reading must be exercised. Same-new-window rollback needs Q-created truth read by P. Root format is not changed unless a concrete requirement demonstrates it.

Required combinations: old Owner-only truth/new runtime; new draft before acceptance/old runtime; new truth/new runtime; new truth/incompatible rollback target; same-window compatible rollback; pending Work/intent/lifecycle; exact old-source recovery of retained old operation; detach with preserved authority and intelligible plain evidence. No history deletion, grant scrubbing or automatic bytes rollback.

M1 and M2 form one atomic deliverable for support/release purposes. A partial Core result is only synthetic contract evidence. Real-home adoption remains separately authorized after complete reader, installed, recovery and host qualification. Reversal cost is low for this plan, high after new durable authority/window receipts exist.

## First Host Feasibility Path

Inspect Codex App Server as one candidate for a client-owned, narrow delegated-accept tool. This selects an inspection path, not a permanent backend/product or a live pilot. Official documentation exposes experimental client-handled dynamic tools, command approvals and sandbox read restrictions. Local CLI is `codex-cli 0.162.1`; help advertises protocol schema export. No model/agent execution is needed for M0.

Proposed path: the host associates a tool call with its admitted execution and bound delegate; it obtains immutable canonical ticket bytes, checks exact home/Work/revisions/action/actor/scope/evidence digest and target, then invokes only the matching Core operation. The model does not choose an Owner identity or obtain a generic privileged shell. Core revalidates current state under its writer guard.

App Server command approval alone does not establish this contract: a command/path preview does not prove immutable file payload, caller identity, or denial of other write paths. Experimental dynamic tools are a candidate transport, not an authorization guarantee. No session-wide approval, arbitrary shell pass-through or automatic permission expansion qualifies.

The worker/delegate must lack a direct write path to control authority, managed runtime, Git administrative state, host policy and approval configuration. The trusted host owns the constrained control call. A cooperating same-account promise is not principal isolation. If the selected host cannot establish the required boundary, report host qualification unavailable and stop at Core-only evidence; do not impersonate the Owner as fallback.

For M0, inspect the exported local protocol for dynamic-tool request arguments and session IDs, sandbox policy, command approval and interrupt messages. Compare with the fetched official sections. Do not start an app-server, turn, worker or reviewer-as-worker. M3 must still execute payload substitution, Owner spoofing, wrong home/action, direct filesystem bypass, duplicate/ambiguous call and Owner same-decision recovery tests.

Official sources:
- [Dynamic tool calls](https://learn.chatgpt.com/docs/app-server#dynamic-tool-calls-experimental)
- [Command execution approvals](https://learn.chatgpt.com/docs/app-server#command-execution-approvals)
- [Sandbox read access](https://learn.chatgpt.com/docs/app-server#sandbox-read-access-readonlyaccess)
- [Interrupt a turn](https://learn.chatgpt.com/docs/app-server#interrupt-a-turn)

The 2026-10-16 local export differs from fetched documentation: `TurnStartParams.SandboxPolicy` exposes readOnly.networkAccess and workspaceWrite writableRoots/networkAccess/excludeSlashTmp/excludeTmpdirEnvVar, but no readOnlyAccess/access/readableRoots/includePlatformDefaults. A search of all 447 generated schemas found no occurrences of exactly these four names: `ReadOnlyAccess`, `readOnlyAccess`, `readableRoots`, `includePlatformDefaults`. The statement that `access` is absent is limited to the exported `TurnStartParams.SandboxPolicy` shape, not the entire export. This does not prove every other local permission mechanism absent; the documented restricted-read shape is not established for this selected protocol/version. The export does contain `FileSystemSandboxEntry.access` (read/write/deny) under command `additionalPermissions`, named `permissions` profiles, and an `externalSandbox` variant. These are present but unqualified alternative surfaces, not approved fallbacks; M3 must establish their actual enforcement before use. Command `additionalPermissions`/policy-amendment requests must be denied or surfaced to the Owner, never auto-approved by the delegated path. Do not send unknown keys or broaden access as fallback. The first live host pilot remains unavailable until an exact supported restriction mechanism and direct-bypass denial are qualified in a separately authorized test. No automatic CLI upgrade or alternative-backend substitution is authorized. DynamicToolSpec and argument transport exist; the host must still validate actual arguments. A schema entry does not enforce Colvia policy.

The static feasibility conclusion cannot exceed “a candidate transport and policy surface exist.” Exact payload enforcement, denial of every relevant alternate path, termination and recovery remain unexecuted.

## Bounded Execution Plan

| Step | Work and evidence | Bound and gate |
| --- | --- | --- |
| R0 | Fresh Claude Code static review of this plan and exact bounded source excerpts | No reviewer tools or source edits; subscription authentication checked; 10-minute process limit, at most two follow-up correction rounds before reporting unresolved issues |
| M0-A | Resolve findings; finalize grant/CONT/window/extension recommendations | Changes confined to this note and private review support; no source runtime or normative activation |
| M0-B | Export local experimental App Server protocol; inspect only required message definitions | One export, 60-second timeout; local CLI only; durable task directory; no model call or daemon; one corrected invocation only for a documented command/environment error |
| M0-C | Verify source anchors, internal/relative links, GFM rendering, claim limits and diff | Static document checks; no product test suite needed for this non-shipped note |
| R1 | Fresh Claude Code static review of result, R0 dispositions and actual check evidence | Same restrictions; no self-issued acceptance; bounded corrections and recheck before Owner result decision |
| Next | Present exact bounded implementation proposal and unresolved admission items | No automatic M1/M2 start |

R0/R1 request, exact input identity, actual model/session, final response and Driver dispositions are retained separately from Owner decisions. Successful reviewer transport is not a product test pass. No inherited fixture pass qualifies delegation.

## Next Implementation Boundary

Delegation stages: M1=Core contract implementation; M2=readers and installed/window compatibility; M3=actual host qualification and bounded judgment-quality observation. These are not CONT milestone names.

The next plan is one bounded source task: implement the ordinary one-use contract and all affected reader/installed compatibility paths together, with R0 before execution and R1 before acceptance. It excludes a production host engine, multi-project service and actual adopter use.

Expected source files: `src/hv2ref/intent.py`, `work.py`, `view.py`, `product.py`, `candidates.py`, relevant `umbrella.py`/CLI paths, `colvia`, `PRODUCT-CAPABILITIES.json`, managed adapter and affected contract docs. Add no runtime module without identifying its inventory/launcher consequences. Tests use the existing intent, Work/recovery, view-sharing, candidate, umbrella, product/window, worker-process and plain-auditor families. New focused delegation tests may be one file. This list is an impact envelope, not permission to edit every file.

The scenario IDs below name the obligations in this note; they are not reported test results. They are grouped as follows:
1. Core V01–V11/V17–V21/V25: existing Owner behavior; exact grant success; actor/home/Work/scope/action refusal; freshness and evidence; no duplicate K or reselection reset; explicit reactivation; Owner/delegate revoke cases; deterministic concurrent requests; prospective graph; shared readers; ordinary child/human parent; malformed data.
2. Recovery V12–V16: decision/all-pre cancellation; mixed refusal; all-post/selection/current cutpoints; mode/outside/neither/source drift; supported versus out-of-band pending mutation.
3. Compatibility V24: every combination above, including draft-before-acceptance and retained writer/rollback behavior.
4. Host/quality V22–V23/V26: actual payload gate and Owner recovery; later shadow quality and Owner effort. Never aggregate these as passed from Core-only tests.

| ID | Required scenario |
| --- | --- |
| V01 | Existing Owner-only behavior and historical reading |
| V02 | Exact grant, one delegated accept, correct bytes, unchanged Git refs |
| V03 | Wrong actor, Work or home, separately refused before writes |
| V04 | Scope mismatch/alias/wildcard or non-ordinary mode refused |
| V05 | Undelegated action refused in Core, not only CLI |
| V06 | Changed intent current refuses new authority; history still readable |
| V07 | Missing/replaced required evidence and worker-only claim refused |
| V08 | Prepare/apply drift in intent/binding/selection/content refused |
| V09 | Second decision for K with a new request/ticket refused |
| V10 | Re-selection of consumed draft does not reset K |
| V11 | Unused reactivation and new draft follow exact binding/Work transitions |
| V12 | Durable decision/all-pre interruption, lawful cancellation and consumption |
| V13 | Mixed application: cancellation refused, exact forward recovery |
| V14 | All-post/selection/current cutpoints and no-promotion replay |
| V15 | Neither/mode/outside drift and unavailable source remain visible |
| V16 | Supported pending mutation blocked; out-of-band mutation distinguished |
| V17 | Owner/delegate accept then revoke: old-K baseline-refresh rebind/new result refused, fresh-K transition |
| V18 | Deterministic concurrent requests permit at most one lawful new use |
| V19 | Prospective first/new revision gets complete verified context |
| V20 | Shared/fallback readers, candidates/status/lifecycle agree; shared intent impact |
| V21 | Delegated ordinary child, human parent, no inherited authority |
| V22 | Actual host rejects Owner spoofing, payload swap and action/home expansion |
| V23 | Owner-authorized exact delegated-ticket recovery, same actor/decision |
| V24 | Full old/new window, draft-before-acceptance and rollback/recovery matrix |
| V25 | Unknown schema, malformed/partial grant fail visibly across entries |
| V26 | Separate judgment quality from actual Owner effort/wait observations |

Negative cases compare authority bytes, project bytes/modes and Git refs/index. Crash cases compare the exact allowed prefix and forbid extra writes. Test currentness and authorization through every public entry, including direct library calls; only CLI checking is insufficient.

Actor freeze notes from the final review: use the source `_RECORD_ID` grammar (`work.py:598`) with full-string matching and no Unicode IGNORECASE. “Historical readers” above means updated readers validating historical records; pre-schema-3 runtimes must refuse schema-3 truth under the compatibility rules. Limited label collision refusal deliberately does not trim existing Owner whitespace and does not provide lookalike checking for non-ASCII Owner labels. These known limits do not replace host caller authentication.

Before approving M1 execution, freeze: exact schema/window and lifecycle transition; source-owned decision/amendment set; task file scope; synthetic input/oracle; focused test IDs; runtime/runner and filesystem/network denial; timeout and total budget based on measured runtime; full normal/parent-optimized regression and exact-artifact matrix; preservation and stop conditions. This M0 note does not invent uncalibrated test time limits.

Standard full-suite templates from Maintaining are `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -v` and its `python3 -B -O` counterpart, executed only after the isolated runtime and child behavior are fixed. Existing native qualification used GIL-enabled CPython 3.14.7; that history is not fresh qualification. Use targeted iterations, then the required complete matrix once the candidate is frozen.

If the host cannot enforce the gate, the Owner can still authorize a clearly labeled Core-only experiment. That does not claim automatic Agent acceptance, human-work reduction or a supported backend.

## Current Evidence And Disposition

- Read-only source inspection: current decisions compare actor with unchanged Work acceptance authority; prospective graph calls exist in publish, prepare and apply; intent reader currently accepts draft versions 1/2.
- Current contract: activated entry-1; CONT DR-0001 remains Draft. Normative preparation labels are resolved by the activation record, not by filenames or timestamps.
- Official host documentation: fetched on 2026-10-16; protocol surfaces above observed. Local CLI version/help executed successfully; sandbox PATH-alias warning does not constitute a failed model call.
- Local protocol export: executed once on CLI 0.162.1, exit 0, 0.194 seconds; 447 JSON schemas generated. DynamicToolCallParams requires arguments/callId/threadId/tool/turnId; ThreadStartParams has dynamicTools; command approvals and TurnInterruptParams exist. Local protocol evidence only, not runtime enforcement.
- Product behavior tests, delegated execution, host enforcement, quality and efficiency: not executed.
- R0: Claude Opus 5.5 initial conditional, then fresh-session follow-up pass-with-notes; B1–B5 resolved. R0 follow-up F1–F6 addressed before R1. R1: fresh Claude Opus 5.5 pass-with-notes, suitable for Owner M0 decision, not M1 readiness/approval. Final correction reviews confirmed F1/F2 and F3–F5, then closed actor I-1/I-2 with no remaining material finding. Exact responses, reviewed revisions, actual model/session and Driver dispositions are retained in the private review support; no review verdict substitutes for Owner acceptance.
- Owner: M0 preparation and Claude plan/result review authorized; exact resulting contract, implementation, Git and adopter actions not yet accepted.

Keep this plan/worktree for the immediate review and bounded implementation decision. Preserve unique review inputs/responses in the designated durable task directory. Delete only generated protocol bulk and transport envelopes once required conclusions and exact relevant excerpts are retained and no active process uses them. No existing source checkout, private planning history or unrelated worktree is cleaned up.

## Owner M0 Adoption And Next Planning Scope — 2026-10-16

The Owner adopted the M0 result and authorized concrete window-transition and test-execution planning, Claude Code R0 and corrections. The preceding complete M0 bytes (SHA-256 `41861df1ffd24423ceeeae2d4b4a64edebd2990cd528049ebfc01a523c0fb0bf`) are retained as the accepted revision. This supersedes the earlier pending-result status only; it does not activate a product contract or authorize implementation. This M0 record is now historical. The [bounded implementation plan](agent-delegation-implementation-plan.md) is the sole current progress owner for the next planning scope.
