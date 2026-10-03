# Concepts

The project owns meaning and history; removable product code reads and publishes that history.

```text
Human accepts intent -> Agent proposes Work and result -> Human accepts exact result
                                  |                              |
                            pending is not current        selected acceptance
                                                          derives completed
```

## One Authority Home

`.hrn/format.json` identifies the project authority and format. `.hrn/intents/` contains drafts, human acceptances, and selections. `.hrn/work/` contains Work identities, revisions, decisions, selections, and result manifests. Current pointers select verified references; filenames and timestamps do not determine authority.

`.hrn/product/` contains release inventories, payloads, binding, and lifecycle receipts. The root `hv2` launches the bound runtime. They can be removed by verified detach while project truth remains. `.hrn/staging/` and `.hrn/locks/` are regenerable scratch, not a second authority.

## Intent And Work

Intent records describe the goal, boundaries, evidence, and acceptance authority. Drafting proposes meaning; acceptance binds the exact draft and its prerequisites. Work refers to accepted intent and preserves the initial baseline, later submissions, rework, and human rebind history.

A result manifest binds full before/after content and exact scoped changes. Content freshness is separate from Git commit identity, so a HEAD-only commit does not invalidate unchanged content. A serial result is already present in the control checkout when submitted. Automatic worker result application is not implemented.

The human authority of a Work must agree with its referenced intent. A stale intent or document reference cannot silently authorize acceptance. Pending publication and failed verification remain visible. See [General Work](GENERAL-WORK.md) and [Workspace Contract](WORKSPACE-CONTRACT.md).

## Collaboration Boundary

The shared guard serializes cooperating record writers. It does not authenticate role names or prevent unrelated processes from editing files. Serial use requires one editing Work by procedure. Multi-worker integration, revalidation cost, and usefulness remain future qualification work.

## Candidate Before Work

A candidate keeps an idea, reason and deferral condition before execution. The human may record one next choice; an agent recommendation is read-only. Accepted intent defines the authorized task, and Work records its actual progress and result. Candidate selection never substitutes for either. `./hv2 view candidates` follows verified links to show actual Work state and labels a linked choice as consumed. See [Candidate Planning](REFERENCE.md#candidate-planning).
