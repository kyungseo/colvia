# Concepts

The project owns meaning and history; removable product code reads and publishes that history.

```text
Human accepts intent -> Agent proposes Work and result -> Human accepts exact result
                                  |                              |
                            pending is not current        selected acceptance
                                                          derives completed
```

The diagram shows the default human acceptance path. The [delegation-1 candidate](#delegation-1-implementation-candidate) adds only the exact ordinary-worker accept exception; intent and parent acceptance remain human.

## One Authority Home

`.hrn/format.json` identifies the project authority and format. `.hrn/intents/` contains drafts, human acceptances, and selections. `.hrn/work/` contains Work identities, revisions, decisions, selections, and result manifests. Current pointers select verified references; filenames and timestamps do not determine authority.

`.hrn/product/` contains release inventories, payloads, binding, and lifecycle receipts. The root `colvia` launches the bound runtime. They can be removed by verified detach while project truth remains. `.hrn/staging/` and `.hrn/locks/` are regenerable scratch, not a second authority.

## Intent And Work

Intent records describe the goal, boundaries, evidence, and acceptance authority. Drafting proposes meaning; acceptance binds the exact draft and its prerequisites. Work refers to accepted intent and preserves the initial baseline, later submissions, rework, and human rebind history.

A result manifest binds full before/after content and exact scoped changes. Content freshness is separate from Git commit identity, so a HEAD-only commit does not invalidate unchanged content. A serial result is already present in the control checkout when submitted. For worker results, explicit human acceptance records the exact decision before applying the retained scoped changes to control; interrupted application follows the bounded recovery contract. This is not unattended acceptance or scheduling.

The human authority of a Work must agree with its referenced intent. A stale intent or document reference cannot silently authorize acceptance. Pending publication and failed verification remain visible. See [General Work](GENERAL-WORK.md) and [Workspace Contract](WORKSPACE-CONTRACT.md).

## Collaboration Boundary

The shared guard serializes cooperating record writers. It does not authenticate role names or prevent unrelated processes from editing files. Serial use requires one editing Work by procedure. General multi-worker efficiency, revalidation cost and usefulness still need project-specific evidence. See [Security and Support](SECURITY-AND-SUPPORT.md) for current limits and historical observations.

## Candidate Before Work

A candidate keeps an idea, reason and deferral condition before execution. The human may record one next choice; an agent recommendation is read-only. Accepted intent defines the authorized task, and Work records its actual progress and result. Candidate selection never substitutes for either. `./colvia view candidates` follows verified links to show actual Work state and labels a linked choice as consumed. See [Candidate Planning](REFERENCE.md#candidate-planning).

## Delegation-1 Implementation Candidate

This retained heading explains the delegation-1 behavior inherited by continuation-1. For current lifecycle commands and authorization boundaries, follow [Continuation-1](README.md#continuation-1). Historical versions keep their original meaning. A verified installation, document or passing check does not prove human authorization, host authentication or general readiness.

The Owner remains the Work and intent owner. A delegate is an exact actor label declared by an Owner-accepted ordinary intent draft; it does not identify an authenticated person or model. The grant names one qualified Work, action `accept`, execution mode `isolated-worktree` and the exact scope-path set. No grant means the existing Owner-only flow.

The durable accept decision consumes the grant, before content application and selected completion. Exact recovery uses the original actor/ticket. Cancellation or later revocation does not refund that use. A new selection, request ID or same-grant baseline refresh cannot reset it. New lawful delegation requires new Owner-accepted intent content and the ordinary rebind/submission rules. Parent integration remains a separate human acceptance.

## Following A Result

A Work result answers “what was accepted?” Its continuation answers “what next did the human select?” The answer can be a proposal, an existing Work or explicit none; undecided is a different state. Choosing a proposal does not accept its intent. Choosing a Work does not start or complete it. Withdrawal returns to undecided and preserves the earlier history.

On resume, connect the project plan item → Work → accepted result → remaining items → selected follow-up. Use the existing narrative, not a second tracker. Valid candidate and Work choices can disagree; show both and let the human resolve the next action. See [Work Follow-Up](REFERENCE.md#work-follow-up) for pending, freshness and the 256-operation limit.
