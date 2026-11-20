# Read-only project status

Ask what needs your attention in a connected project. The initial view uses the current Work records without requiring priorities, prerequisites or a separate dashboard. The [Work guide](../../manual/en/work.md#project-status) and [command reference](../../manual/en/reference.md#the-project-launcher) describe the user entry.

## What the view reads

One published root supplies the Work heads, associated plans, decisions, submissions and progress notes. Review means a pending submission. An active revision has a recorded change request for the submission it references. A paused review is counted as paused. A progress note or a newer explicit resumption action supplies the next step. Planned Work stays distinct from pending review. A row for another workspace identifies that boundary.

The screen and JSON use the same rows. Within a scan window, review comes first, followed by revisions, ongoing Work, paused Work and plans. Equivalent rows have a stable Work ID order. Each page contains up to 20 actions. The reader looks at up to 200 head-map keys per window and caps detail reads per row and window. Counts apply to the displayed rows. Unreadable details and partial pages warn that other review requests may exist. A change of published root invalidates the cursor.

The agent keeps the project, workspace, Work and submission reference behind the title. It can open the recorded revision and compare its submission hash even when another version has since arrived. Identical titles may need a short clarification. Looking at a row neither authorizes an action nor checks working files.

## Verification

The [focused tests](../../tests/test_foundation_project_status.py) cover one-line and partial views, duplicate titles and historical content, resume and pause, unreadable details, cursor invalidation and traversal. A retained v0.3.0 synthetic project distinguished a pending review, a change request, a progress note and a pause with no priority or dependency data. The human and JSON results agreed and the original database and backup digests matched after the queries. Synthetic bundle checks cover the installed guide, its size limit and manual links. No new storage format is required.

Candidate priority and explicit dependency records are tracked in the [P2 follow-up](product-evidence-and-followups.md#p2-candidate-priority-project-status-and-dependencies).
