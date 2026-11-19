# Save progress before the first submission

An explicit save on active ordinary Work retains a short account of what was done, what was checked, what remains and the next proposed action. A fresh chat can compare approved files against that note. These summaries enter the project backup. The agent reads all pages of the Work list before picking a single match and asks by title when several fit. A sign-off stops work; it cannot submit or accept a result.

## Storage and compatibility

The latest note has its own reference in the existing store, bound to the approved active Work and to its predecessor. Publication compares the current Work and note references atomically. The Work, approval and submission receipts retain their normal meanings. Note creation enables a required record capability on that project. Readers that support v0.2.0 only refuse the new store and backup. Retain an earlier backup if returning to that reader matters.

Only approved paths are observed, up to 128, with per-file and aggregate byte limits. Unreadable paths are reported separately from unchanged files. Stored hashes describe the bytes at observation; the note contains no file bodies. More paths than the limit are reported as an unavailable count. After the first submission use the established review and revision paths.

## Verification boundary

The focused tests cover save, lookup, differences, binding, duplicate or stale requests, interrupted writes, a racing submission, and backup import with compatible and older readers. Platform fixtures exercise the common CLI and the observation algorithm. Native Windows installation and release qualification are separate. The release note for a candidate containing this change is “Save progress on an active Work and pick up in a new chat before the first submission.” No released version is assigned here.

A fresh read-only Codex chat located the sole active Work without its identifier, distinguished an unchecked sum from a changed report, and asked once before saving at sign-off. The command trace had no write attempt and a subsequent view matched the initial note and Work. Static intent checks cover explicit, negative and compound requests in the guide. Three platform-shaped ZIP fixtures staged successfully with matching guide and source bytes.

Two existing tests also fail on the unchanged source tree: a candidate-page test double rejects the display argument, and a peer attribution test expects a different error when required check results are missing. These failures are independent of notes; retain them in the regression report.

## Review and disposition

The result reviewer identified a potential change of the active Work reference while the same approval remains valid. Rebinding an active Work as a child and then removing it reproduced the failed lookup. The candidate now compares the plan and approval attached to the note with the current ones; both operations still bind new writes to the current Work and latest note. Repeating the composition round trip recovered the note, refused the earlier receipt and allowed a fresh save. A note under another approval is historical. If file observation fails but the project binding can still be verified, the view keeps the note and marks the comparison unavailable. An invalid connection still refuses access.

The agent checks whether this is the first note in the project and explains the earlier-version limit before saving. Multiple matches and ambiguous endings use the same targeting rules in both languages. A second Windows handle checks native identity and file stamps. A synthetic adapter and staged Windows archives exercise this code path; native Windows remains a release qualification item. A separate two-process check restored a backup produced by unchanged v0.2.0 code, preserved the exact Work head and added a note with the candidate reader.
