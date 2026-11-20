# Windows notification detail latency

The Owner approved the [revised plan](notice-detail-latency-review.md) on 2026-11-21 against source revision `863de45`. This record owns execution. The approved scope includes an isolated Windows ARM64 baseline and candidate comparison, changes to the detail read path, focused regression checks, restoration, and one static result review. The time budget includes VM and review wait time, with a cumulative limit of 120 minutes.

Measure from the first visible loading message until the window contains the expected Work title and submitted summary. Record activation-to-content separately. Measure five fresh receiver processes, each with two immediate repeats, and report the median, maximum and individual observations. The target on the small connected fixture is a warm median of two seconds or less. A placeholder or successfully completed child process cannot satisfy this check.

Keep the current runtime, authority, generation, capability, event integrity and receiver checks. An external change or retired store must never yield a misleading successful result. Read related records in one short, guarded transaction, release it before live workspace inspection, and preserve existing write behavior. Keep the x64 observation as historical evidence. A briefly visible console is tracked separately. No user machine registration change, commit or publication is included.

The isolated official baseline has a verified connected synthetic project and a submitted result. The external Windows window-text observer checks the two known strings, reporting only match flags and times. The fixture uses its own management root and notification identity.

## Measured outcome

The detail window showed the expected title and summary on every observation. The two-second warm-median target remains unmet; this is a partial correction pending the Owner's decision.

| Loading message to readable content | Official v0.3.0 median / maximum | Benchmark candidate median / maximum |
| --- | --- | --- |
| Fresh receiver process (5) | 13.04 / 13.99 s | 8.70 / 8.85 s |
| Repeat in that process (10) | 13.21 / 13.95 s | 8.09 / 8.65 s |

Each process had two repeat observations. The registered Windows activation callback was exercised on ARM64, with the window text sampled every 25 ms. Activation to readable content on a fresh process had a median of 17.54 s on the baseline and 13.03 s on the candidate. This measurement does not qualify x64 or measure toast delivery.

The final reviewed product includes an extra guard rejecting nested transactions. Three supplementary reads of that exact product took 8.48 s fresh, then 7.97 and 7.94 s warm, all with correct visible text. A separate phase trace on this final product spent 3.27 s entering the manager and 4.47 s in the connected detail route. Those phases included two full runtime verifications of 3.25 s each. The verifier does not hold Windows runtime file identities across the two calls. The candidate retains both verification boundaries. All measured runs restored the synthetic fixture's original selected slot and registration and checked that the Work records were unchanged.

The Owner also observed a console-like window for roughly 0.1–0.2 s immediately before the detail window on three of three attempts. The originating process was not traced. Follow-up should capture the window owner and process lifetime on the normal activation path, then check the same interval independently of the loading-to-text measurement. A separate performance decision is needed before changing how a verified runtime remains trusted between calls.

## Result review and follow-up

R1 was a static review by Claude Opus 5.5, session `4d8826ca-89c8-4c47-ae16-b33730417158`. The input SHA-256 was `7a8644ed96849d05b16421183ca79e856620c403c13620cd8471c0f0aecfeb15`. The private review record retains the complete response. Its verdict follows verbatim.

> **The change is correct as scoped. There are no correctness blockers.** The historical reads now come from one guarded read transaction, and the live reads happen afterward, outside it. Route changes and retirement during the live phase produce a refusal, not a mixed result. The 2 s target is **not met**: the warm median is 8.09 s. This supports no release claim.

- Confirmed the executed-history branch with a real synthetic store and native detail route. A separate existing test covers submitted results. Exercised lifetime and nested-read rejection. The map reader calls the guarded loader before returning even for an empty map.
- Strengthened the pending-writer check and asserted an exact runtime digest refusal. The first stricter fixture lengthened a file and correctly tripped the byte budget before the digest comparison. The corrected fixture changes one byte without changing length and receives the expected digest refusal. The Git adapter disables optional locks. Left the function-local import in place to keep the verified product unchanged.
- The existing checks of 17, 13, and 28 invocations overlap. The four review follow-ups passed across the first run and its single corrected digest test. There is no WAL checkpoint in the supported DELETE-journal configuration. The read lock is released before workspace and Git inspection. A workspace read reflects the instant of observation.
- The reviewed product source hashes match the final trial inputs. The benchmark and final trial ZIP SHA-256 values were `e715affe18a0a9c2d0ddca01ffa6524e2380c84533e3bd4ba16158163ff7149d` and `ebe202d14cb6d0cb898a6a54b3479c2ec128252d55ea13e492ada3928c856d1d`. The trial did not change the native executable. The isolated fixture, exact runtime slots and review evidence are retained for the next latency and console-window diagnosis.

## Notification Center click diagnosis

On the official v0.3.0 isolated Windows ARM64 installation, a mouse click on the synthetic notification body in Windows Notification Center opened the expected title and summary. This used the Windows shell activation path. Three earlier instrumentation attempts did not click the body and do not count as observations. A separate, pre-existing terminal used to run the observer was excluded from the measurements.

After activation, the registered receiver started, followed by its console host. A newly visible Windows Terminal window appeared and disappeared about 0.295 s later. A pseudoconsole window belonged to the receiver PID in the same interval. No new cmd.exe or PowerShell process was observed in that interval. The receiver created its own detail window about 4.53 s after its process first appeared. After loading appeared, the expected text was readable 13.66 s later on this official baseline. The source calls FreeConsole after the launcher's verification step. The unchanged native entry in the measured package has PE subsystem 3 (console). The isolated registration was removed and the original Work root and baseline slot were preserved. This is one ARM64 click; the previous x64 visual observation has no process trace.

The two separately timed Python inventory passes belong to ManagedEntry initialization and to open_managed_store when it opens the project authority through a second RuntimeLease. The native launcher also performs its own checks before launching Python; its elapsed time is outside those two Python timings. The installed manifest lists 507 files. Verifying which event, project, generation and submitted result to read is relevant to a click. Hashing the complete runtime twice is a consequence of using two independently protected general-purpose entry points. Simply reusing the selection pointer leaves same-selection file changes unaccounted for. A full pass alone already exceeds the two-second target. No product code or trust boundary was changed in this diagnosis.

Evaluate a GUI-subsystem activation entry that leaves ordinary CLI behavior intact. For loading, evaluate a narrowly verified read-only path for the persisted original title and summary, followed by a separately identified live-state refresh. Specify the trusted reader and dependencies, generation and update invalidation, receipt-free reads, and stale/wrong-event refusals before replacing any full check. These are design candidates. Their integrity equivalence and latency have not been demonstrated.

## Follow-up plan review

The Owner authorized planning and one static review only. Source base: `863de45`, plus the three reviewed runtime modules from the prior correction. The packet described the observations and proposed design; it supplied no diff or device logs. Packet SHA-256 before and after: `35e03ee48e06bfe0dfd1bc5409fdb2b7122bd7dd285efb36067568d9c0b1958f`. Fresh Claude Pro first-party subscription session `33eb0e87-bac3-47c8-9912-522353ac9441`, model `claude-opus-5-5`, tools disabled, 420 s maximum. No new VM run in this planning round.

### Verbatim reviewer response

# Static plan review

## Smallest defensible next experiment

Run a **phase-attribution trace only**, with no source changes. This is a proposal; no device runs happen this round.

On the ARM64 fixture, run official 0.3.0 and the batching candidate as they are. Take ≥5 cold samples (cold state defined, e.g. after reboot) and ≥10 warm samples. Timestamp each phase from process-creation events and existing content-free logs:

- click
- receiver process start
- manager entry runtime verify (lease 1)
- notice-identity child
- COM registration
- callback
- notice-detail child
- store open (lease 2, including both ~3.25 s inventory passes)
- original-event validation
- render

Also record which process creates the visible conhost or Terminal window: the receiver or a child.

The output is a measured **floor for the minimum trusted read**. If that floor exceeds the gate, neither (A) nor (B) is credible without a new trust proof, and the plan stops for an owner decision.

## Blocking assumptions

1. **The digest requirement conflicts with step 1.** A GUI-subsystem entry is a different PE, so it has a different digest. "Separate entry with the registered digest" cannot hold as written. Changing the registered digest touches old registrations and rollback. This needs an owner decision before any design work.
2. **Pinning under "held native identities" is unproven.** On Windows, open handles with restricted share modes may still not prevent rename of the parent directory or other replacement paths. Option (A) depends on proving which files stay immutable for the read's duration.
3. **The disclosure gate is undefined.** You need to decide which checks must pass before showing the historical title and summary:
   - graph, owner/project, generation, receiver, notice head
   - and whether workspace and Git checks are also required
4. **The source of the console flash is unknown.** It may come from the receiver, from the children, or from both. That determines whether a GUI entry alone gets to zero visible windows.
5. **The 4.5 s pre-loading delay is unattributed.** It may be dominated by identity/COM work that neither A nor B addresses.

## Acceptance revisions

- **Make click-to-readable the primary metric**, with gates of ≤3 s cold and ≤2 s warm median. Add a p90 bound. Keep loading-to-readable as secondary only.
- **State the current gap plainly.** The candidate's 8.09 s warm median fails the gate. Batching is evidence, not a path to acceptance.
- **Define how "zero new visible terminal windows" is detected.** Use window and process creation enumeration for conhost, OpenConsole and WindowsTerminal across the full process tree, not just visual observation.
- **Add a privacy check.** Seed sentinel strings in work titles and summaries, then grep banners and logs to confirm they never appear.
- **Add a stale-reply test.** Activate two different works rapidly and assert that each reply binds only to its own activation ID.
- **Require negative cases** to show nothing readable and write nothing: revoked, retired, foreign and corrupt records.
- **Make the x64 exclusion explicit.** Record "ARM64-only; no x64 claim" in every result artifact.

## Status

Nothing in this plan is approved. Steps 1–3 remain unvalidated designs pending the trace results and an owner decision.

### Driver dispositions and proposed next gate

- **Accept** the measurement-first experiment. **Revise** the suggested repeat of both full sample sets: retain the existing callback samples and actual shell click/terminal trace. Add one process-cold click and one repeat on the connected ARM64 fixture for missing phases only. Define cold as a fresh receiver process with the VM and filesystem warm; a reboot is a different condition. Correlate click, receiver, pre-COM identity, callback, both detail-child verification sites, original-event validation, first correct body and live refresh. The reviewer grouped the verification calls under store open; there is one when constructing ManagedEntry and another when constructing the store lease. The receiver also verifies on its native launch path. Trace values may overlap across parent and child processes and must not be summed blindly. A measured floor on the current reader constrains that design only.
- **Accept** that a dedicated GUI image has a new digest. The registration would bind that new verified digest; preserve app/CLSID and old notification IDs. Test enable/update/rollback/disable with old and new registrations before distribution. The owner has not approved a binary or registration change. **Revise** the speculation about the flash: the real click already identified Windows Terminal and a console host parented by the receiver. The final candidate must still check the receiver and all children for any additional visible windows.
- **Accept** the need to define trust before disclosure. Verify the actual reader and its executable dependencies, local registration/authority, selected runtime and store generation, receiver, routed event and graph/digests, notice head and linked outcome. Only then show the historical result. Current file/Git state may follow with an explicit pending, refreshed or unavailable label. Do not hold a DB read or global update lock across filesystem/Git I/O. A lost permission or invalid, retired, foreign or corrupt route must not disclose title/summary or create an acceptance/write. A legitimate historical outcome while a working folder is disconnected retains its existing meaning. No persistent preview payload or new index in this gate.
- **Accept** narrow investigation of safely reusing held identities. Prove full path/file/dependency coverage, replacement resistance, and update/uninstall/rollback invalidation before claiming equivalent protection. If a safe implementation or the performance floor is out of reach, report which boundary must change and seek an Owner decision. Do not silently turn off a check. No separate reader implementation in the diagnostic.
- **Accept** click-to-correct-title-and-summary as primary. Proposed acceptance for an eventual candidate: process-cold median <=3 s, warm median <=2 s and warm p90 <=3 s (nearest rank; 10 repeat observations). Also report maximum, process-cold individual values, time to first window/loading and time to current-state refresh. Validate with real Notification Center clicks or explicitly label callback-only numbers. No visible console across receiver or child processes, correct newest activation after rapid different Work clicks, no synthetic title/summary sentinel in banner/logs. Reuse negative tests only where the consuming implementation is unchanged. ARM64 results do not qualify x64.
- **Next approval** is diagnostic only. Expected 20–35 minutes, cumulative stop at 50 minutes including VM setup, waiting and restoration. This is an engineering estimate based on the retained working fixture and prior trace; additional instrumentation may be unavailable. Report observed versus inferred timing if a phase cannot be isolated. Preserve the fixture, restore registration and Work, and report the smallest viable change before implementation. Later Windows native qualification, including x64 packaging/behavior, remains a separate decision.

## Two real activations and attribution

The Owner approved the diagnostic gate only. The official Windows ARM64 v0.3.0 receiver and runtime were used throughout. Both clicks were made on the verified body of a synthetic notification in Windows Notification Center. The first started a receiver process; the repeat used the same receiver and detail window, and the observer required a new loading transition before matching the known title and summary. The VM and filesystem were already warm. Each row is one observation.

| Observed interval | First click | Repeat click |
| --- | ---: | ---: |
| Click to visible loading text | 4.45 s | 0.11 s |
| Loading text to correct title and summary | 12.71 s | 13.07 s |
| Click to correct title and summary | 17.16 s | 13.18 s |
| Identity child, included in first-window time | 3.84 s | No identity child |
| Detail child, included in loading time | 12.66 s | 12.95 s |
| New visible Windows Terminal window | 0.27 s | None observed |

Product child durations are elapsed times inside the corresponding GUI intervals. Individual COM registration and callback times are not instrumented. The direct phase trace below was a separate read-only invocation using the same installed modules, project and event. It added timing wrappers in that measurement process and did not modify the installed package. Its wall time was 12.22 s:

- Inventory verification took 2.97 s at managed entry and 2.94 s at authority open, totaling 5.91 s.
- The event and linked outcome were validated twice, 2.57 s and 2.62 s (5.18 s using unrounded values). These are inclusive of the official store guards. They are not an intrinsic cost of checking one event.
- Current Work view plus the subsequent workspace verification took 0.94 s. Nested workspace checks inside the view are included. The remaining roughly 0.18 s covered the other route and setup operations.
- In the prior batching candidate the two inventory passes remained, and the measured warm loading interval was 8.09 s. Delaying live-state refresh alone cannot close the gap. Keep the existing coherent historical snapshot and evaluate a narrowly trusted, read-only first render including receiver identity. Require equivalence of event, authority, generation, digest and receiver protections. Treat the GUI subsystem change as a separately testable part of the same user experience. A 2 s result for a redesigned reader has not been shown.

The final trace was compared byte-for-byte with the guest log after completion. Both bodies matched; the selected runtime bytes, recorded Work root and all three temporary registration keys were checked on restoration. No source implementation, install, update, commit, or release occurred in this gate. Retain these phase measurements and the two screenshot references in the private task directory until the replacement path is checked. ARM64-only observations; no x64 latency claim.

## ARM64 receiver prototype

Clicking a new Windows notification first opens the submitted title and summary. The reader checks the digest carried by that notification, the corresponding event, receiving installation, project and database instance, and the linked delivery records in a read-only transaction. The window identifies the current Work state as pending until an independent workspace read finishes. A newer click invalidates earlier responses queued for the window. A notification created by an older installation has no route digest. This prototype directs its reader to the project.

The console launcher and bundled Python remain in the trial package. Windows activates a separate GUI-subsystem receiver. Its product subprocess starts with console-window creation suppressed. The bundle assembler can check the optional receiver's platform, architecture and GUI subsystem before adding it. The selected runtime still undergoes content and inventory verification. The scoped Windows reader holds file and directory handles while checking the bytes and checking their identities and access controls. Handles close at the end of the verification. No trust decision is cached between clicks.

| Notification Center click to verified title and summary | Observations | Median | Range | Within target |
| --- | ---: | ---: | ---: | ---: |
| New receiver process, 3 s target | 5 | 2.69 s | 2.52–2.89 s | 5/5 |
| Existing receiver process, 2 s target | 10 | 1.50 s | 1.47–1.55 s | 10/10 |

All 15 measured clicks opened the expected synthetic title and summary. The observer detected 0 newly visible console or terminal windows between clicking and the full current-state display. Hidden console host processes were distinguishable from visible windows. The median click-to-current-state times were 5.17 s on first opening and 3.94 s on repeat opening. The VM was running and its filesystem cache was warm. Earlier official ARM64 Notification Center measurements were 17.16 s and 13.18 s, one observation per condition.

One additional real click has an incomplete observation. The trace writer reported a file-open permission error while the host was collecting its log. The fixture restored its baseline. Subsequent runs used separate immutable ready signals and collected the trace after exit. The incomplete click is excluded from all latency and console denominators. The three trial packages contain identical product members, with different sequence numbers in their trial manifests. Each trial restored the selected baseline and disabled its temporary receiver registration. The recorded Work root matched the fixture before and after each trial. The anti-rollback sequence advanced only in the isolated fixture.

Focused checks rejected an altered stored summary, a valid route belonging to a different Work, a changed runtime, unexpected links and a mismatched receiver. They also covered emission of the digest used on click and the older receiver's activation format. The launcher tests passed on the Mac host. The Windows click results are specific to ARM64.

## Prototype result review

The Owner accepted the measured ARM64 prototype. Claude Opus 5.5 performed one static review using the first-party Pro subscription in 309.31 seconds, with no tools or test execution. The existing click measurements were reused. The fixed review packet SHA-256 was `232783c45861866e420ac705c5e4220d5c6cddeabd03cc5223dafee76ab967bb`. The base, patch, reviewed source files and measurement record matched after review. The private trial record retains the verbatim response for the Owner's decision.

The reviewer rated the findings Medium overall and conditionally supported a prototype commit with M1 and M2 recorded. The reviewed configuration is not release-ready. Driver dispositions follow.

- Accept M1. A Windows build using the new launcher source can omit the GUI receiver. New notifications then carry an ID only and the new listener classifies them as old. Require the correct GUI receiver in a distributable Windows package and test the missing-asset case.
- Accept M2 and qualify the compatibility guarantee. The new GUI redirects ID-only toasts to the project. If the old receiver remains registered, its legacy detail request still lacks a digest, so the new binding guarantee does not cover that path. New sends can also require receiver re-registration. Make the upgrade behavior explicit, and keep unbound native clicks from displaying an unverified association. A rollback to an old receiver may ignore a newer notification (L7).
- Revise L1. A current-state lookup failure now replaces the already displayed title and summary. Distinguish a temporary refresh failure from lost trust or revoked access before retaining previously displayed content. Executed outcomes also need wording that reflects the recorded outcome, including cancellation before launch (L5).
- Qualify L2/L4/L6. The code has a bounded database lock wait. A user-visible write timeout was not demonstrated. Both inventory procedures reject unexpected files and can include empty directories; the native timing does not establish which verifier branch ran. Ordinary Work creation refuses an existing Work except for an explicitly approved planned replacement. No cross-lineage current-state counterexample was demonstrated.
- Qualify L3. The normal launcher rejects a forwarded receiver-source option before the argument terminator. Pass the launcher's actual receiver decision to child configuration to avoid inferring it from arbitrary positional arguments.
- Different-Work route substitution and stored content corruption had synthetic rejection evidence. The 15 completed GUI observations used one event. Historical notifications, rollback and rapid clicks on different Works have separate coverage limits. The reviewer did not reproduce a GUI data mix-up.

Owner acceptance covers the earlier prototype measurements. Source corrections, commit and release decisions remain open.

## Windows package requirement after prototype review

The Owner chose to require the dedicated GUI receiver in Windows bundles and to leave existing notifications to manual re-registration and project lookup. The assembler now rejects a missing receiver before creating the output ZIP. The existing architecture and GUI-subsystem checks still apply. Two focused tests covered omission and successful assembly for ARM64 and x64. Omission left no output file. With a matching synthetic receiver, both ZIPs contained the supplied receiver and the separate CLI, and their manifests passed slot validation. These were packaging checks. The accepted 15 ARM64 clicks remain the runtime evidence. Commit and distribution await the Owner's decision.
