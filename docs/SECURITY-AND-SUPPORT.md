# Security And Support

This development candidate assumes one trusted local OS account and cooperating agents. Logical actor and acceptance-authority strings are declarations, not authentication. Confirmation tokens bind request bytes; they do not prove a human approved them. File checks and locks do not defend against an adversarial process with the same account bypassing the protocol.

## Runtime And Scope

Mutation requires final, GIL-enabled CPython 3.14.6 or 3.14.7; there are no third-party runtime dependencies. This is a version/build-mode gate, not an operating-system or distributor-build qualification check. Read-only diagnostics can expose a rejected runtime without admitting mutation. Other operating systems or distributor builds matching these conditions may execute without having been qualified.

Qualification evidence is limited to the exact source/runtime combinations in their immutable receipts:

| Combination | Evidence classification |
| --- | --- |
| Linux container, recorded CPython 3.14.6 build | Qualified for the recorded container test scope; this is not native-platform acceptance. |
| macOS arm64, recorded Homebrew CPython 3.14.7 build | Recorded N4 source: 424 unique tests passed in each of normal and parent-optimized modes, without timeout substitution, under the fixed Seatbelt policy allowing literal /dev/fd listing. Parent optimization does not imply optimized launcher/auditor children. Earlier 353-test calibrated results remain historical. |
| macOS arm64, recorded pyenv CPython 3.14.6 build | Not qualified; the version gate still admits it. The complete normal run retained one assertion failure. |
| Linux CPython 3.14.7, Windows, and other OS/distributor builds | Unqualified; matching the version gate does not qualify them. |

For the macOS 3.14.6 failure, targeted reruns did not reproduce it, but the original failing path was not captured and the cause remains unknown. The failure is retained and operationally closed by an Owner risk decision, with reopening on recurrence. This does not turn that whole run into a pass or qualify that combination.

These results belong to their recorded source, not automatically to the current checkout or a later release with changed managed documentation. Verify a candidate against its exact artifact receipt. That synthetic qualification does not establish ordinary-user latency, actual worker-1 adoption, anonymous onboarding, production scale, or public distribution. The separate bounded private-use observation below does not expand those support claims.

Control authority can reside in a primary Git checkout or supported standalone non-Git target. Linked workers cannot publish control truth. Submodules, nested repositories/authorities, separate Git directories, partial clones, alternates, unsafe links, and ambiguous topology are refused within the documented checks. Supported work content excludes ignored untracked files but includes tracked ignored files. See [General Work](GENERAL-WORK.md).

## Data And Recovery

Do not place credentials or secrets in typed records, documents, command examples, or evidence. Product releases inventory an exact managed set. Init preserves unrelated project files; detach removes only verified managed bytes. Unknown and damaged state is preserved with a non-success result. Exact recovery handles documented prefixes, not arbitrary corruption or power-loss atomicity.

Bounded worker execution and recovery have recorded synthetic qualification. Two private document Works were accepted on the earlier human-1 runtime. Subsequent private evidence records worker-1 installation and bounded worker document continuation, including an existing-file follow-up; this does not establish general usability or real-project multi-worker efficiency. Real-project multi-worker efficiency is not established. Generation 1/2 support and migration are removed; archived historical tests or retained contracts do not establish current support. See [Capability Declaration](../PRODUCT-CAPABILITIES.json), [Reference](REFERENCE.md), and [Operations](OPERATIONS.md).

Runtime qualification uses an explicit patch allowlist, not a minimum-version promise. Later 3.14 patches, 3.15, prereleases and free-threaded builds require separate qualification. Historical receipts retain their original runtime identity.
