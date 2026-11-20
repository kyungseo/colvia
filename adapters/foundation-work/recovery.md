## Access failures

If a command reports `stale-or-bare-worktree`, inspect the repository with
`git worktree list --porcelain`. Show the flagged entry and ask the person
to verify whether its folder moved, its drive is unavailable, or the folder
is gone. An entry marked `bare` is a separate Git layout; don't treat it
as a missing worktree. Keep the registration and related records until the maintainer has
confirmed the exact recovery or cleanup and preserved any needed data.

Use the guide from the installed launcher. If its list filter is unknown, verify that the launcher and guide belong to the same installation before continuing.

Use the actual command result, not an assumed permission setting:

| Observation | Meaning and next step |
| --- | --- |
| No narrow-access request tool in this session | No request was made. Do not report an OS denial or invent a settings control. |
| Host explicitly reports the command was not started | Report that start refusal. This observation establishes no current record state. |
| A started command times out, is interrupted or returns missing/damaged output | Its outcome is unknown. Inspect the Work or known operation read-only before considering another mutation; missing JSON alone is not a host denial. |
| The person declines a tool request | Stop that action. Do not seek a bypass. |
| Colvia reports a file or storage access failure | It may concern an input, output, runtime or record store. Identify only what the actual diagnostic establishes. |
| Complete `ordinary list --list-mode all` exits 0 with `items: []` and `next: null` | This verified connection has no Work. A failed query never establishes that. |

`workspace-registration-required` needs the manager's connection preview; it is
not an empty Work list. A non-null `next` means there are more pages. A new folder
without a verified connection must use that preview before any record writes.
For an interrupted first connection, use the original operation ID with `connect-resume`. If setup stopped before connection files were prepared, the person may instead cancel the reservation with `connect-cancel OPERATION` and request a fresh preview. This preserves Git state and account registration. See `guide management`.
For `connection-move-review-required`, use the installed manager's
`move-preview` with the existing project ID and new absolute root. Review the
verified old and new locations. Use the exact canonical preview and receipt
only after the person approves the move. Inspect `move-status` before resuming
an interrupted operation with the same ID. Keep the connection file and
record store intact. A copy, overlap or unverified identity requires diagnosis.

Use the host's actual denial details and verified connection information to locate
the required path and read/write/execute access. Colvia's generic error does not
identify the denied path. If the path or cause is unavailable, say so instead of
assuming the record directory. Explain the smallest known action briefly; show an
exact private path only when the person needs it to authorize or perform that action.

Only use a narrow-access mechanism actually available in the current host and
covered by authorization. Verify the returned path, access mode and duration;
a partial grant is not the full requested grant. Do not add network access or
assume a turn grant survives the turn or a new conversation. Do not enable trial
features, change host settings, install tools, switch to full access, or substitute
a source launcher to work around missing access. If no supported narrow path is
available, stop the affected writes and name the missing capability.

A grant alone does not authorize retrying a stopped command. Before reconsidering
a mutation, inspect its current Work, or its operation if the ID is known, using the
applicable read-only command; some changes may already have happened. Keep unknown effects unknown and
follow existing recovery and retry authorization. Do not create an untracked
fallback result or claim that chat text was recorded or submitted. Successful
reads alone do not establish write access. Another host's successful run does not
establish this host's permissions.

For a stopped update, use `manage --json update-status OPERATION_ID` to inspect
the prepared release and receipt before an explicitly authorized resume. A
missing preparation or expired verification needs diagnosis, not a new download
loop. Preserve interrupted Git integration locks; do not remove `index.lock` or
make another commit while recovery is pending.

If the same folder gained a Git repository, follow the connected-folder transition in `guide management`. A location change and a change of repository kind have different previews.
