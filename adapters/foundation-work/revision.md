## Revising an already submitted result

Use `ordinary revise` once after the person requests a concrete modification to
the reviewed result. That records the request and keeps the original approved
file scope, checks and previous submitted content. A new conversation reads
`ordinary view`: `rework.approved_request`, `approved_scope`, `checks`, scoped
`differences`, and `submission_check`. Do not re-approve a recorded request or
call `plan-review` for an active Work. Ask only about a genuinely changed scope,
ambiguous result or unresolved effect; final acceptance remains a separate decision.

While the Work is active, its last submitted body is retained history, not a
currently pending review. This read does not establish whether checks were run
in another conversation; say that current check evidence needs confirmation,
not that nobody has run them. An unattributed addition means the submitted proof
was not established, not that the file has no possible owner.

The scope diagnosis is a current read, not a replay of an old failure or proof
that all checks passed. When the person asks what changed or where a revision
stands, do not stop at `rework.differences`: it lists changed paths, not text edits.
Read the relevant file in the approved scope in the workspace and its preserved last submitted
body with `ordinary content WORK_ID PATH --revision LAST_SUBMITTED_REVISION`,
using `rework.last_submitted_revision` from that view. Compare the two before describing
the current edit, even when outside-scope changes block submission. For large text,
compare the relevant sections and state the comparison limit. If either body is
unavailable or not readable as text, name that limitation and the observed reason;
do not infer a missing edit or ask for the same scope approval again. Show the
concrete content change briefly, separately from the file-specific submission
blockers and any remaining human decision. This comparison does not prove checks
passed or authorize editing, restoring, submitting or accepting during a read-only
status request.

For an already authorized modification task, execute the remaining planned checks
and submit the modification without a separate submission request.

If the diagnosis is unavailable, do not
invent the cause. If blocked, name the causal files and additions/modifications/
deletions, retain the modified draft and last submission, and explain the next
needed action briefly. Never reset a baseline, ignore outside changes, remove
another Work's files, or ask the person to edit internal record IDs.

A rework may account for regular files added by another approved and submitted
Work in the same workspace when its immutable submission and current content
agree. This does not accept or edit the other Work, and cannot cover unsubmitted
files, overlapping scope, policy changes, or existing outside modifications or
deletions. Such a submission requires all planned checks to have passed. Do not
claim attribution proves who authored the bytes. First submissions and general
external-change recovery are outside this exception. An attributed revision can
be reviewed, accepted, backed up and selected for scope-only Git integration;
applying it to another workspace through worker is not yet supported. Do not
bypass that refusal with a private file-copy script.
