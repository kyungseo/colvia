# macOS receiver selection and ordinary Work journey

Owner authorized implementation, bounded corrections, focused checks and Claude review on 2026-11-05. Driver: Codex. Result acceptance pending.

## Boundary
Start at PR52 merged source. Preserve previous failures and usage, reuse macOS and Windows ARM64 notification-click evidence. No commits/publication/x64 external checks/adopter changes. Do not alter account-wide registration or install into the real home during source checks. Existing authenticated model subscriptions may process synthetic inputs only.

Expected 2–4 elapsed hours including review/model waits; stop at 6 hours. Estimate is judgment, not measured throughput. Two static Claude reviews, 180 seconds each. Behavior observations: at most 6 chats/12 messages and 20 minutes total model wait. Stop communication/auth/unknown-termination failures without retry. Do not inflate previous evidence into autonomous guest agent success.

## Proposed correction
Native notification sender currently registers its own bundle but does not verify the OS-selected or already-running receiver. Multiple same-ID trial apps can open the wrong event store. Before authorization or posting, check that the app resides under the actual login account's standard Colvia bin, not an overridden HOME; refuse a running same-ID receiver elsewhere; register only this checked app; recheck selected receiver before notification. Do not delete registrations, kill apps, or weaken verification. Refusal leaves the Work/inbox available. Add a read-only receiver check mode for diagnosis. Native checks reduce ambiguity at posting time, not a guarantee against subsequent OS selection changes.

## Selected evidence
Focused synthetic checks: correct receiver; relocated/fake home; running old app; no selection; selected other app; check does not register or request permission; post/authorize blocked before side effects; native compile. Existing event integrity and two-project click tests reused, with focused regression where touched. Package/inventory checks only for changed installed surfaces.

Observe normal-language first request, result submission, fresh-chat resume and single acceptance via Codex and Claude Code in dedicated synthetic folders. Model actions restricted to scoped commands; preserve authority boundaries, do not fabricate human acceptance. If host notification cannot be safely reached without actual account installation/registration change, report that dependent step separately rather than calling a simulated click passed.

## Review and state
Plan review pending. One owning record; private packet, bounded logs and synthetic fixtures retained only for this task's qualification/recovery until acceptance and later candidate reuse decision.

## Plan review disposition

Claude Opus 5.5, subscription static review, 70.62 seconds; no tools. Accepted pure decision tests, self-PID exclusion, fail-closed unresolvable paths, exact realpath equality, receiver-side guard, separate refusal code, and manager timeout mapping. Registration occurs only after location/running checks, followed by selection recheck before authorization and again before posting. No retry/poll registration loop. Defended allowing first enable when no selection exists: registration is the existing explicit enable/post action, then selection must match before permission or posting. Read-only check never registers. Fixture builds keep the existing distinct bundle ID and compile a fixed expected path; no production runtime override. Synthetic acceptance will be labelled, never counted as Owner acceptance. Existing two-second notification trigger retained; OS routing can change after check.

### Verbatim plan review

# Plan review: macOS receiver selection and the ordinary Work journey

**Verdict:** The direction is sound and stays within scope. Four gaps need fixing before implementation, because each could produce a false pass or a boundary violation. The rest are small tightenings.

## P1: fix before implementing

**1. Several listed tests cannot run without breaking the boundary.**
- **Problem:**
  - The "correct receiver" positive case needs an app at the real login account's Colvia bin. That means installing into the real home.
  - "Selected other app" needs Launch Services to prefer a different same-ID app. That means an account-wide registration change.
  - "Running old app" started with `open` also registers that copy.
  - The plan does not say how these run during source checks.
- **Correction:**
  - Put the decision logic in a pure function, for example `receiverVerdict(expectedURL, selectedURL, runningApps[], selfPID)`. Unit-test every case against it in a test-only compile target.
  - Do not add a runtime environment variable or flag that lets production accept a different expected root. That would weaken the check.
  - Exercise the real OS queries only through the read-only check mode.
  - Start any "running elsewhere" fixture by running its binary directly, never with `open` or Launch Services.
  - If the real-home positive path and real selection cannot be reached safely, report them as dependent and unverified, as you already plan for the notification click.

**2. The running-receiver check will match its own process.**
- **Problem:** `--post` and `--authorize` run inside the `ColviaWork.app` bundle, so `runningApplicationsWithBundleIdentifier:` always includes the current process.
- **Correction:**
  - Exclude the process's own PID.
  - Treat another instance at the identical resolved path (the open Work window) as acceptable.
  - Refuse when another instance has a nil or unresolvable `bundleURL`.
  - Add a test for "self only" and one for "same-path window already open".

**3. The order of side effects is underspecified, and registration may not take effect immediately.**
- **Problem:** `LSRegisterURL` is itself an account-wide side effect. Its effect on which app Launch Services selects can lag.
- **Correction:** Use this order:
  1. Validate the event ID.
  2. Check the bundle path against the login account's bin.
  3. Check running same-ID apps. Refuse before any registration.
  4. Call `LSRegisterURL` for this app only.
  5. Recheck the selected receiver, with a short bounded retry of about 1–2 s for registration lag.
  6. Call `requestAuthorization`. Doing this after the recheck means a refused case never shows a permission prompt.
  7. Recheck the selected receiver and running apps again just before `addNotificationRequest`.
- **Note:** The current code calls `[NSApplication sharedApplication]` and creates the notification center before any check. Move the checks ahead of both.
- **Test oracle:** For "blocked before side effects", compare `lsregister -dump` before and after (read-only), and confirm no authorization request is made.

**4. Path identity must be exact, not a prefix match.**
- **Problem:** "Resides under" could be read as a prefix match.
- **Correction:**
  - Derive the home directory from `getpwuid_r(getuid())->pw_dir`. Do not use `NSHomeDirectory` or `CFCopyHomeDirectoryURL`, which can honor `HOME`.
  - Refuse when `geteuid() != getuid()`.
  - Resolve both the expected path (`<pw_dir>/<standard>/bin/ColviaWork.app`) and the actual bundle path with `realpath`, then compare for equality. Alternatively compare `st_dev`/`st_ino`.
  - A translocated (quarantined) path will correctly be refused.
- **Tests to add:** a symlinked home, a sibling directory `bin2/`, a nested `bin/x/ColviaWork.app`, and a case-only path difference.

## P2: tighten

**5. Say which API defines the "selected receiver" and what it can't guarantee.**
- `NSWorkspace URLForApplicationWithBundleIdentifier:` (or the first result of `LSCopyApplicationURLsForBundleIdentifier`) is the best available proxy. It is not a guaranteed match for how the notification system routes clicks.
- State this in the plan and in the read-only check's output. Without it, a passing check reads as proof of routing.
- Treat a nil result ("no selection") as refusal before registration. Do not register and hope.

**6. Add a receiver-side self-check (small, and the same concern).**
- The remaining risk is that selection changes after posting. Today a wrong receiver runs its own bundle-relative `colvia-manage`.
- Fix: in `show:` or `readDetail`, run the same path and identity check before launching the reader. On failure, display `missing`.
- This fails closed on the wrong event store with no redesign. Add one fixture test using the pure verdict function.

**7. Give receiver refusal its own exit code.**
- Today `post` returns 1 for every failure, and `notice_command` passes the code through.
- Use a dedicated code, for example 3 for "receiver refused".
- Make sure the manager's caller treats it as "notification unavailable; the Work/inbox stays valid". It should neither retry nor roll back the Work record.
- Test that a refusal leaves the Work item readable from the inbox.

**8. The check mode must be provably read-only.**
- Do not call `LSRegisterURL`, `currentNotificationCenter`, `requestAuthorization`, or `getNotificationSettings` in check mode.
- Print only paths and a verdict. Use an exit code for each verdict.
- Prove it with the `lsregister -dump` diff and the notification-settings state before and after.

**9. Who performs "single acceptance" is ambiguous.**
- "Single acceptance via Codex and Claude Code" can be read as the model accepting the work.
- State that the model must not run the acceptance command for the human.
- Either the owner performs it, or it is labelled synthetic acceptance in the record and is not counted as human acceptance.
- Also check the budget: two agents × (first request, result, fresh-chat resume, acceptance) needs at least 4 chats and about 8 messages, within your 6/12 limit. With no retries, one failure exhausts that path, so record it as stopped, not passed.

## P3: optional, low cost

**10. Uncaught timeout in `manager.py`.** `subprocess.TimeoutExpired` is not an `OSError`, so a timeout in `notice_command` raises uncaught. Add it to the except list and map it to 65 or the refusal code.

**11. The 2 s trigger widens the race window.** A `nil` trigger posts immediately and narrows the gap between the final recheck and delivery. Only change it if it doesn't disturb the existing click evidence. Otherwise leave it and note the residual risk.

**12. Ambiguous test name.** "Running old app" could mean an old build at the correct path (acceptable) or a copy elsewhere (refuse). Split it into two cases.

## Test gaps (summary)

**Decision logic, via the pure function:**
- Self-only process
- Same-path window open
- Nil `bundleURL`
- Nil selection
- Path edge cases: symlink, sibling, nested, case-only, translocated
- Effective UID differs from real UID

**Side-effect oracles:**
- `lsregister -dump` diff for check mode and for every refusal
- No authorization request on refusal

**Remaining paths:**
- Receiver-side self-check shows `missing` when it fails
- Distinct refusal exit code, with the inbox still available
- Manager timeout path
- Separate reporting for the real-home positive path and for selection and click routing, if they are unreachable within the boundary

## Focused verification checkpoint

First constrained run: 39 passed, 1 error before installed fixture creation because the default interpreter was outside the supported patch list. New native receiver and packaging tests passed. Preserve that failure; rerun only the unexecuted notification-history test with the existing qualified CPython 3.14.7. Network denied and fixture writes confined to durable task storage.

## Result review disposition and final source state

Claude Opus 5.5 performed the second static review in 82.96 seconds using changed hunks and synthetic summaries only. Full-file transmission was rejected by automatic approval review before execution; the packet was reduced to approved excerpts and that transmission was allowed. The review was not a full-source audit. Plan and result reviews both used the existing Pro subscription without reviewer tools. No independent third review followed the corrections below.

- Accept: bind source-built fixture apps to an explicit, distinct compiled bundle identity; reject production identity and mismatched fixture identities. Reject relative/control-character fixture paths before writing build output.
- Revise: manager and native app now both check the real login account's notification location. An overridden HOME is refused for production notices rather than silently redirected to another event store. Ordinary project use is not changed. Actual installation in the standard account location and its first enable remain unverified.
- Accept: distinguish receiver mismatch from an unreadable event, propagate manager mismatch to the detail message, and avoid bilingual duplicate output from the manager's check command.
- Accept: recheck on the main queue before posting; recheck authorization-only success after the permission callback. Keep the existing bounded wait and delayed trigger.
- Defend with an explicit limit: registration happens only after location/running checks, followed by a selection check. A later refusal can leave that permitted registration. No automatic repeat registration or repost is introduced; transient selection lag may still refuse first enable. This is a remaining native observation item, not a claim of production success.
- Targeted caller evidence replaces a full-suite rerun: the exact native refusal code produces one notification attempt and `unavailable`, while existing result/inbox preservation passes. No Work schema, acceptance, writer or Windows implementation changed. Changed argparse and timeout paths have focused checks.
- Inherited guide mismatch: a byte diff contained only two accepted large-file paragraphs missing from the installed guide. The generator synchronized those paragraphs; it now reports equality. Final isolated update checks the installed guide and reference against source bytes and opens View.

### Verbatim result review

# Static review: receiver binding fix (hunks only)

**Overall:** The core design fails closed and is mostly sound: realpath equality, reject other same-ID copies, re-check before posting, and refuse unresolvable bundles. But the evidence does not show that the production path works for a real account. Several caller-facing behavior changes are also not covered by the "unchanged modules" reason for skipping a full rerun. Nothing here amounts to user acceptance. All agent approvals and positive native policy results are synthetic.

## Correctness / safety findings

**High: production positive path is unverified, and manager and binary may compute different locations.**
- The binary now derives the expected location from `getpwuid_r().pw_dir`.
- The manager uses `store / "bin/ColviaWork.app"`. How `store` is computed is not shown. If it comes from `Path.home()`/`HOME`, a `--store`-style option or a test override, it can differ from `pw_dir`.
- If they differ, `notice-enable`/`notice-post` will always return 3 for that install. This fails safe but is functionally broken.
- The account observation (standard app absent, another same-ID receiver running, selection mismatch) means `expectedReceiver()` returned nil or mismatched. No production build has ever produced a positive verdict.
- Needed:
  - Show how `store` is derived.
  - Add a test that the manager's install target equals the binary's expected path when `HOME ≠ pw_dir`.

**High: fixture gating is weaker than claimed.**
- `fixture_flag` is gated only on `if fixture_root`. A `Path` is always truthy, so any production caller that passes a non-None `fixture_root` (e.g., the store) bakes a fixture path into a production binary. That binary then trusts that path instead of the account path.
- The claim "compiled in only for existing unique fixture IDs" is not visible in this hunk. There is no existence check and no bundle-ID check. Callers are unknown.
- Recommended:
  - Have the fixture build `#error` or refuse at runtime when `bundleIdentifier` equals the production ID.
  - Add a packaging test asserting the production binary contains no fixture path string (and that `COLVIA_FIXTURE_APP` was undefined).

**Medium: exit code 3 now reaches callers whose handling is not shown.**
- `notice_command` (≈L304) returns the child's return code. `notice-post`/`notice-detail` can now get 3 in cases that previously returned 0 (e.g., another same-ID copy running).
- Only the `notice-enable`/`notice-check` branch prints a refusal message. The post and detail paths are silent.
- Any caller that treats non-zero as a failure, records it or retries now behaves differently.
- The skipped full rerun ("Work records, acceptance logic unchanged") is therefore weakly justified: those modules didn't change, but their inputs did. Also unknown: whether 3 already had another meaning in `main`.

**Medium: registration happens before the final selection check, and the post-registration check can flake.**
- `LSRegisterURL(..., true)` mutates the LaunchServices database before `receiverReady(YES)`. A refusal after registration still leaves a registration behind.
- The LaunchServices database update is not guaranteed to be visible to `URLForApplicationWithBundleIdentifier` right away. This can cause spurious 3s on first enable.
- No retry or settle logic and no test for this ordering.

**Medium: reader-side guard returns `missing`.**
- When `receiverReady(YES)` fails, `readDetail` reports the detail as missing, not as a receiver mismatch. That misattributes the failure to the user.
- It also blocks detail viewing whenever any other same-ID copy is running at another path, including a stale one. That is fail-closed but undocumented in the user-facing message.

**Low–Medium: checks in the async completion block.**
- `receiverReady(YES)` is called inside a completion handler, likely on a background queue. `NSRunningApplication` is thread-safe, but its list refreshes via the main run loop, so it may be stale. Acceptable, but note it.
- The check-to-`addNotificationRequest` gap plus the 2 s delayed trigger leaves a TOCTOU window for selection or launch changes. You already acknowledge this: a query match does not guarantee click routing.
- Unknown: whether `--authorize` (`event == nil`) reaches the L159 check at all, and whether the wait loop has its own bound below the manager's 30/35 s timeouts.

**Low: fixture define quoting.**
- `json.dumps(..., ensure_ascii=False)` is C-compatible for `"` and `\`, but not for control characters (JSON `\u00XX` is not a valid C universal character name below U+00A0).
- The fixture path is not realpath'd at build time; this is fine because runtime resolves it.
- Unknown: whether `json` is imported in `macos.py`.

**Low: output and messaging.**
- `notice-check` prints the binary's English line and then the manager's Korean line, giving mixed and doubled output.
- The Korean message for code 3 ("close other-location windows") is misleading when the cause is a selection mismatch, a missing install or `HOME ≠ pw_dir`.
- `--check-receiver` never registers, so a fresh install returns 3 until `notice-enable`. This is correct for a check-only command but worth documenting.

**Low: App Translocation / quarantine.** A quarantined copy runs from a randomized path and is refused. This is fine but undocumented.

**OK as written:**
- `getuid != geteuid` refusal.
- `NSNull` for unresolvable running bundles leads to rejection.
- Own PID is excluded, and same-path siblings are allowed.
- The `@COLVIA_FIXTURE_APP` macro idiom.
- `subprocess.run` timeout kills the child.
- `TimeoutExpired` is now caught in both manager paths.

## Test / evidence gaps

1. **No production-build positive run.** All positive native policy results are synthetic. Real-account click routing with this binary is unverified, as you state.
2. **`receiverVerdict` matrix not shown as unit-tested:**
   - mismatched running path
   - `NSNull` entry
   - selection nil or mismatch
   - `requireSelection = NO` vs `YES`
   - Only "relocated binary refused before registration" is evidenced natively.
3. **Not exercised:**
   - post-registration refusal
   - async-block refusal (result 3 propagation through `dispatch_async`)
   - reader-guard refusal
4. **Interpreter nondeterminism.** The harness let a pinned parent select a newer child interpreter. The pass depends on the CPython 3.14.7 path. The harness should pin the child via `sys.executable` (or equivalent) explicitly. Keep both failures recorded, as you did.
5. **No full or core rerun despite changed exit-code semantics and argparse choices.** The inherited full-suite and macOS/Windows click evidence predates code 3, so it does not cover these changes.
6. **Codex 15.48 s denial.** The denial layer is unknown and the raw transport failure was not retained. This is correctly not counted as a pass or as acceptance. Retain transport logs next time.
7. **Synthetic behavior trials.** These do not count as Owner acceptance. The draft response being longer than ideal is an open UX item.
8. **Guide sync.** No evidence that only the two already-accepted paragraphs changed. A byte-diff of the installed guide before and after is needed.

## Unknown (outside the provided hunks)

- How `store` is derived.
- Callers of `build_notice_app` and their `fixture_root` values.
- Wait-loop bounds and the initial `result` value.
- Whether `--authorize` reaches the pre-post check.
- Any other uses of exit code 3.
- Callers of `notice_command`.
- How fixture bundle IDs are assigned.

**Excluded as stated:** result acceptance, Git, x64, publication, actual installation.

## Verification and remaining boundaries

47 distinct focused unit tests passed across the baseline-selected checks and post-review changed checks. The first runtime-admission error and the subsequent child-interpreter mismatch are retained as failures; they are not counted as passes. The latter was traced to the Homebrew executable reporting an `opt` child path that selected a newer interpreter. The stable CPython 3.14.7 parent/child path passed the remaining installed-history check. Native production and fixture builds compiled, fixture ad-hoc signature verification passed, and a relocated binary refused check/authorize/post. Native positive decisions use synthetic inputs; no new real-account permission prompt or click was exercised.

Changed English/Korean prose passed GFM rendering without stray emphasis, local source links passed, and managed payload bytes include the diagnostic reference and synchronized guide. Existing macOS and Windows ARM64 clicks are inherited observations of the earlier candidate, not qualification of this changed binary. The test-only account-path checks are macOS-specific and skipped on other platforms.

The controlled Claude journey prepared and approved one synthetic plan, wrote and submitted a report, then used a fresh chat to recover it and finish with one explicitly synthetic acceptance. Draft: 47.12 seconds; resume: 33.10 seconds. No real Owner acceptance is inferred, and the longer draft response remains a UX observation. These project-only tools intentionally exclude shell/source exploration, so they do not measure unconstrained CLI behavior or arbitrary-source-search latency.

Codex reported project-tool access denial after 15.48 seconds; the tool server received no calls and neither a report nor a Work was created. Raw transport failure detail was not retained, so the denial layer remains unknown. No retry was made. Its fresh-chat/acceptance path remains unobserved.

Disposition: source correction and focused evidence ready for Owner review; the entire proposed host journey is not complete. Remaining: resolve the scoped Codex tool admission offline before any separately authorized retry; decide the exact installed candidate/standard account receiver before actual notification enable/click. Keep x64 external confirmation, installation/adopter changes, Git and publication outside this task. Existing failures and consumption are unchanged; this bundle used two static reviews and three behavior calls, with behavior wait 95.70 seconds. No VM was resumed.

## Retention and impact

Keep this uncommitted task checkout and the final signed fixture, review excerpts, results, scripts and synthetic projects until Owner disposition and the next candidate's reuse/recovery decision. Previous candidate evidence remains at its original location. Intermediate binaries and the rejected full-file review packet have no ongoing consumer after final verification and may be removed under standing cleanup authority. Generic impact: this candidate is intended to refuse misrouted macOS notices more clearly; no actual adopter update has occurred. No commit or publication is authorized by these checks.

## Owner acceptance — 2026-11-05

Owner accepted the bounded source correction and focused evidence and authorized the next confirmation bundle. This source task is complete with its recorded limits: no post-correction independent rereview; Codex behavior and actual production receiver clicks remain separate. Follow-up confirmation is owned by CHORE-20261105-002. No Git/publication or adopter deployment is implied.
