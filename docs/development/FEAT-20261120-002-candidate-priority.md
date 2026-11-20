# Candidate priority and reported user requests

The [read-only project overview](FEAT-20261120-001-project-status.md) uses existing Work records. This change lets a person also rank an open candidate. The [Work guide](../../manual/en/work.md#candidate-priority) describes how to set, change or clear a priority.

## Decision and evidence

The recorder declares its role. The source of authority for this operation is a reported user request to order candidates. The evidence is the relevant request text, with an optional separate rationale. A request reported by an agent is marked as such. The CLI does not independently authenticate chat messages or the operator's identity. Work approvals, acceptance receipts and worker grants confer no authority here. A rank carries no permission to start a Work or change any other record.

Each change appends a typed event with candidate version, previous event, old and new levels, recording time, operation and the basis used for the preview. The basis covers the project, store instance, candidate version, prior priority and requested value. Applying it checks both heads atomically. The same operation and intent can replay the recorded result even after a later change. Readers distinguish unset from low. Clearing a priority keeps the earlier events.

Queries and a no-op leave the format requirements alone. The first change adds the priority schema to the read and write requirements. Backups include the exact event history. A reader that does not support that schema must refuse the changed project and new backups. Clearing all priorities retains that requirement. For a first effective change, the installed guide requires agreement to this compatibility consequence before applying the preview. This is an agent interaction rule; the CLI exposes the flag and warning. The original candidate and any linked Work keep their own identities and lifecycle.

The ranked view reads bounded windows. Inside a window it sorts open candidates by level and stable candidate ID. A partial result marks its coverage. The agent follows cursors from the same root and merges by the same key before describing a global order. A changed root invalidates the cursor.

## Verification

The [focused tests](../../tests/test_foundation_candidate_priority.py) check setting, changing, clearing, reported provenance, refusal of stale or unrelated receipts, concurrent edits, exact retry, linked Work preservation, partial ordering, and backup restore with an older-reader boundary. The packaging checks cover installed agent guidance and the bilingual manual. Installation and public release are separate decisions.
