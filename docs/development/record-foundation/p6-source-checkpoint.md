# P6 delivery source checkpoint

Status: partial source integration; no runner, installed notification or Owner
result acceptance. The grouped plan and disposition remain the scope owner.

## Exact submission

Delivery requests bind one Work/head, workspace registration, action, deadline,
prepared submission or execution grant, and optional receiver identity. Starting
requires the exact displayed request and retained human statement. One outstanding
request remains the project floor. Claiming an effectful step requires the native
lock and publishes an immutable attempt/owner; ordinary Work writers cannot bypass
that owner. Pure status inspection takes no pending effect ownership.

Ordinary and delivery submission share capture, scope, retained-content and
composition checks. A delivery recaptures current entries and changed paths before
publishing the prepared Work review head, delivery outcome, outstanding/owner
release and optional notice event in one store transaction. It never accepts Work.
Changed prepared bytes, outside-scope changes, wrong receipts, unheld locks,
duplicate attempts and cancellation refuse. A notice event is only a record;
no OS notification was emitted.

The first fixture omitted required check reports and correctly refused. After
fixing that input, historical request reading incorrectly called a composition
transition check that needs current head access. The code now keeps historical
validation separate and runs the live transition check in the publication view.
Original failures remain preserved. The corrected delivery/ordinary/barrier run
passed 26 optimized checks with fixed inputs. The effect lock is an explicit test
double here; native lock mechanics have separate evidence.

## Remaining integration

Nested execution ownership/cancellation, exact outcome inbox and notice emission
intent/result handling remain. Complete P5 runtime transport/launch qualification
is independent and partly held by the recorded native sandbox failure. No general
success, automatic recovery, actual notification or release qualification follows
from these source checks.


## Nested ownership and source entry

Execution can borrow a delivery attempt only when its exact grant, Work head,
registration, authorization, deadline and active outstanding selection match.
Parent cancellation prevents further child admission and is observed by the live
callback/worker paths. It does not suppress already-started evidence. Known child
closure returns ownership to the parent; final delivery outcome publication
releases it. Unknown children cannot be cleared by parent completion/cancellation.
Cancelling a claimed but unstarted step verifies absence of a started child and
preserves the human cancellation statement.

The notice detail service binds project and authority instance, original delivery
outcome and current Work separately. Later acceptance does not rewrite the original
review snapshot. Missing connection changes the guidance while preserving the
original result. Emission records intent before calling a supplied port; lost
intent acknowledgement makes zero emitter calls, and any ambiguous outcome forbids
a retry. Tests use recording/failing ports, never the OS.

Source-only commands now prepare/start/run/view/cancel the ordinary prepared step,
read its original notice details, and inspect/cancel formal execution records.
The source entry does not expose an unqualified model launch or OS emitter. Existing
ordinary Work remains the result-acceptance path. Focused nested/inbox/journal and
source-CLI/session checks passed with fixed inputs; their suites overlap. Source
CLI tests use actual fresh Python processes and local effect locks, not installed
launchers. The concrete model runtime channel/launch remains unfinished, and the
native sandbox attempt remains held. Grouped static review is next, not result
acceptance or a release-support declaration.

The grouped partial result review and Driver corrections are in [result disposition](p5-p6-result-disposition.md). Source CLI submission/reopen and the corrected cancellation/nested ownership paths pass 49 focused optimized checks. Actual notice emission remains held; P5 runtime/process integration is incomplete.

## Managed native-detail route source

A private event-ID router now adapts the existing opaque 32-hex native event token
to the exact project, authority instance and retained notice object. The manager's
`notice-detail` command validates the graph again, reports the original submitted
result separately from current state and preserves historical detail when the
workspace connection disappears. Neither a click nor detail inspection accepts
work. A route-write failure after emission intent becomes unknown and cannot
silently resend. Focused real-store fixtures used only a named recording receiver;
no OS notification, app registration or installed click was performed.

The platform emitter, installed receiver alias/package and final native click
qualification are still separate integration work. A route fixture must not be
reported as end-to-end notification success.

### Native receiver source composition

Windows now reuses the native callback/detail window through the foundation Go entry. A bounded event ID opens the verified current manager, whose receiver identity check binds the retained executable to the exact owned registration. User-scoped registration has a durable intent, partial-state validation and explicit resume; foreign registry values refuse without reset. Fixed toast publication uses the owned Job transport, and a non-zero/unknown result never triggers automatic re-emission. Registry fixtures and cross-builds do not qualify actual Windows callbacks, consent or toast delivery.

macOS now packages the four fixed signed-app files, retains originals during updates and holds a barrier across runtime selection. First-install interruption and explicit resume are covered with inert app bytes. Registration/consent and emission are separate explicit manager actions. The macOS receiver continues to validate its standard location and OS selection. No new app signing, registration, launch or notification was executed.

Evidence: `p7-native-notice-callback-build` Go test plus three cross-builds passed (8.326 s, Windows not executed); `p6-windows-receiver-registration` passed (1.807 s); `p6-windows-receiver-composition` passed (16.985 s); `p6-macos-receiver-package-lifecycle` passed (5.999 s). Source composition still requires installed native-platform qualification. The previous native-execution failure and exhausted behavior-session budget are unchanged.
