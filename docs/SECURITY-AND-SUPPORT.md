# Security And Support

This development candidate assumes one trusted local OS account and cooperating agents. Logical actor and acceptance-authority strings are declarations, not authentication. Confirmation tokens bind request bytes; they do not prove a human approved them. File checks and locks do not defend against an adversarial process with the same account bypassing the protocol.

## Runtime And Scope

Mutation requires final, GIL-enabled CPython 3.14.6 or 3.14.7; there are no third-party runtime dependencies. This is a version/build-mode gate, not an operating-system or distributor-build qualification check. Read-only diagnostics can expose a rejected runtime without admitting mutation. Other operating systems or distributor builds matching these conditions may execute without having been qualified.

### Historical Observations

The following summaries describe earlier source/runtime combinations, not a qualification of the current checkout. N4 names an earlier bounded worker-integration development stage; it is not a runtime profile or an operation to run. The complete qualification inputs and private-use records referenced here are not bundled in this source checkout. The source-only historical receipts belong to an older generation and do not substantiate these later results.

A contributor cannot reuse these summaries as a regression anchor. Reuse requires access to the exact recoverable evidence listed in [Evidence Reuse And Selection](MAINTAINING.md#evidence-reuse-and-selection). When that evidence is unavailable, choose new checks for the intended claim or leave the claim unverified. This does not require a complete regression for every documentation edit.

Recorded historical combinations:

| Historical combination | Reported observation and limit |
| --- | --- |
| Linux container, recorded CPython 3.14.6 build | Reported qualification covered that container test scope; this is not native-platform acceptance or qualification of this checkout. |
| macOS arm64, recorded Homebrew CPython 3.14.7 build | Recorded N4 source: 424 unique tests passed in each of normal and parent-optimized modes, without timeout substitution, under the fixed Seatbelt policy allowing literal /dev/fd listing. Parent optimization does not imply optimized launcher/auditor children. Earlier 353-test calibrated results remain historical. |
| macOS arm64, recorded pyenv CPython 3.14.6 build | Not qualified; the version gate still admits it. The complete normal run retained one assertion failure. |
| Linux CPython 3.14.7, Windows, and other OS/distributor builds | Unqualified; matching the version gate does not qualify them. |

For the macOS 3.14.6 failure, targeted reruns did not reproduce it, but the original failing path was not captured and the cause remains unknown. The failure is retained and was operationally closed for that historical run by an Owner risk decision, with reopening on recurrence. That decision is not a standing qualification waiver for a new candidate. This does not turn that whole run into a pass or qualify that combination.

These historical results belong to their recorded source, not automatically to the current checkout or a later release with changed managed documentation. Verify a candidate against its exact artifact receipt. That synthetic qualification does not establish ordinary-user latency, actual worker-1 adoption, anonymous onboarding, production scale, or public distribution. The separate bounded private-use observation below does not expand those support claims.

Control authority can reside in a primary Git checkout or supported standalone non-Git target. Linked workers cannot publish control truth. Submodules, nested repositories/authorities, separate Git directories, partial clones, alternates, unsafe links, and ambiguous topology are refused within the documented checks. Supported work content excludes ignored untracked files but includes tracked ignored files. See [General Work](GENERAL-WORK.md). Unchanged raw CRLF checkout entries can be verified only against unchanged pure-LF blobs with explicit retained text/eol=crlf attributes and exact deterministic byte reconstruction. Only verified active checkout-1 enables this unchanged-CRLF exception. Snapshot hashes and changed-path application remain byte-exact. Changed converted files, attribute changes, external transforms and arbitrary filters are outside this exception; see the unchanged-CRLF contract in General Work. This adds no Windows or general filter qualification, and an exact old/new-artifact compatibility check is still required before an adopter update.

## Data And Recovery

Do not place credentials or secrets in typed records, documents, command examples, or evidence. Product releases inventory an exact managed set. Init preserves unrelated project files; detach removes only verified managed bytes. Unknown and damaged state is preserved with a non-success result. Exact recovery handles documented prefixes, not arbitrary corruption or power-loss atomicity.

Historical private-use reports describe two accepted document Works on human-1 and later worker-1 installation and bounded document continuation, including an existing-file follow-up. Those records are not included here. They do not establish general usability, real-project multi-worker efficiency or qualification of this checkout. Generation 1/2 support and migration are removed; archived historical tests or retained contracts do not establish current support. See [Capability Declaration](../PRODUCT-CAPABILITIES.json), [Reference](REFERENCE.md), and [Operations](OPERATIONS.md).

Runtime qualification uses an explicit patch allowlist, not a minimum-version promise. Later 3.14 patches, 3.15, prereleases and free-threaded builds require separate qualification. Historical receipts retain their original runtime identity.

Checkout-1 is a forward transition from planning-1; same-window compatibility remains bidirectional. Exact qualification is required for each changed pair. Detach plan/receipt schema 2 blocks legacy planning-1 recovery of new detach prefixes; paired schema 1 history remains readable. This is a cooperating-runtime compatibility boundary, not protection against malicious local code.
