# DR-0009 · Explicit Work dependencies

Status: Draft for Owner decision. The implementation is a source candidate.

## User decision and evidence

Record a dependency when a person says that one existing Work needs another Work’s accepted result. Record a removal or replacement on the same basis. The recorder declares whether they entered the request directly or relayed it as an agent. Retain the relevant instruction, the operation, both Work references and the prior relationship revision. This evidence describes a reported request. It provides no independent proof of the speaker’s identity. The relation cannot grant permission to start, change scope, submit, accept or commit.

A proposal identifies the project, store instance, current endpoint heads, direction and previous graph revision. A replacement includes the old and new prerequisite in one atomic change. Duplicate, cyclic or contradictory dependencies cannot be admitted, including cycles through the existing parent submission requirements. Two concurrent proposals from the same graph revision cannot publish incompatible results. Neither Work head is rewritten.

## Reading and compatibility

Use one captured project root to read both directions. Show the current accepted plan, submission and decision, including the retained authorization for a valid worker acceptance. Archive preserves the accepted result. Reopening it restores the wait. Discarding or replacing a Work calls for a new dependency choice. Unavailable evidence remains unknown. Existing parent submission conditions retain their own meaning and evidence.

The active edges and previous event share one immutable revision. Both directions are derived from that bounded set. First use adds a schema requirement to subsequent reads, writes and backup restores. Before the first save, explain the consequence for older installations. Looking up or previewing a relationship leaves compatibility unchanged.

[Implementation and checks](../development/FEAT-20261120-003-work-dependencies.md) · [Work guide](../../manual/en/work.md#work-dependencies)
