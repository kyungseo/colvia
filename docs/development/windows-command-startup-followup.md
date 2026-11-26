# Windows fixed startup cost

Status: Owner approved registration on 2026-11-25. Design and implementation await selection.

The managed entry now verifies the selected runtime inventory once for ordinary and grouped Work. [Phase C](PATCH-20261125-002-read-path-efficiency-phase-c.md) measured about 0.44–0.49 seconds for that pass on Windows x64. The native launcher validates the selected slot separately. Use [Phase D](PATCH-20261125-003-read-path-efficiency-phase-d.md) to measure the fixed costs through the launcher, including Python startup and runtime validation.

Revisit if the measured cost of those recurring fixed steps exceeds five seconds on native Windows. Count how many separate commands run in a real grouped review before estimating the user impact. Compare fewer CLI calls, a bounded resident process, and a verified cross-process handoff of runtime evidence. Evaluate the costs of process startup, trust establishment, and operating a long-lived process separately.

Any selected design must bind requests to the intended local endpoint and current runtime. Preserve refusal when identity, ownership, runtime files or slot selection change. Keep runtime locks scoped to requests. Define shutdown, update, uninstall, recovery and resume behavior. The [notification detail task](PATCH-20261121-001-windows-notice-detail-latency.md) may benefit from shared evidence.
