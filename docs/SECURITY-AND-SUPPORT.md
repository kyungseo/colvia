# Security And Support

Continuation-1 profile; see [authorization and qualification](README.md#continuation-1).

This development candidate assumes one trusted local OS account and cooperating agents. Logical actor and acceptance-authority strings are declarations, not authentication. Confirmation tokens bind request bytes; they do not prove a human approved them. File checks and locks do not defend against an adversarial process with the same account bypassing the protocol.

## Runtime And Scope

Mutation requires final, GIL-enabled CPython 3.14.6 or 3.14.7; there are no third-party runtime dependencies. The gate checks the Python version and build mode. An OS or distributor build can pass it and execute even if that combination has not been qualified. Read-only diagnostics can report a rejected runtime while mutation remains blocked.

Runtime And Scope in this document remains the authority for the allowed CPython version/build-mode; the native-entry examples and admission text refer to it. Windows-2 adds an actual OS/process-runtime gate and the native local NTFS mutation-path gate to that requirement. Its initial policy permits native Windows 11 ARM64 with an ARM64 64-bit CPython process and Windows 11 x64 with an x64 64-bit CPython process on local NTFS. Standard-user local/guest NTFS is the initial supported qualification environment; elevated execution is not qualified. Standard-user evidence does not introduce a new administrator-token check/refusal at each writer entry. Filesystem admission is not evidence-only: before filesystem mutation verify actual native local NTFS for target, staging, lock/scratch, external backup, other written/removed paths and existing files with mandatory write-capable flushes under Workspace's Windows Native Observation And Publication; remote, non-NTFS and unknown paths are non-pass. Do not add a fixed-drive-type restriction. Emulated architecture pairs, 32-bit processes, POSIX compatibility runtimes and other operating systems are not admitted for Windows-2 mutation. Verify actual conditions; a profile name, executable path or version string alone is insufficient. Read-only diagnostics may report unsupported or unknown conditions without authorizing writes. This Windows-only restriction does not change existing macOS defaults or reinterpret old windows.

Policy scope is not environment qualification. State the exact observed edition/build, architectures, filesystem, shell, Git, CPython and artifact/runner tuple and any unobserved follow-up. Use the fixed windows-2 content-mode, worker-application, lifecycle and detach6 rules; do not claim full worker mode parity, POSIX permission equivalence, general same-account race protection or power-loss persistence. The existing explicit unchanged-CRLF exception is extended to windows-2 only with its unchanged proof and exclusions; qualification still must verify it. Never use current support prose to relabel historical evidence.

### Historical Observations

The following summaries describe earlier source/runtime combinations. Qualification of the current checkout needs evidence for that candidate. N4 is the name of an earlier bounded worker-integration development stage, not a runtime profile or an operation to run. The complete qualification inputs and private-use records behind these summaries are unavailable in this source checkout. Its bundled historical receipts belong to an older generation; the later results below rely on different records.

A contributor cannot reuse these summaries as a regression anchor. Reuse requires access to the exact recoverable evidence listed in [Evidence Reuse And Selection](MAINTAINING.md#evidence-reuse-and-selection). When that evidence is unavailable, choose new checks for the intended claim or leave the claim unverified. This does not require a complete regression for every documentation edit.

Recorded historical combinations:

| Historical combination | Reported observation and limit |
| --- | --- |
| Linux container, recorded CPython 3.14.6 build | Reported qualification covered that container test scope; this is not native-platform acceptance or qualification of this checkout. |
| macOS arm64, recorded Homebrew CPython 3.14.7 build | Recorded N4 source: 424 unique tests passed in each of normal and parent-optimized modes, without timeout substitution, under the fixed Seatbelt policy allowing literal /dev/fd listing. Parent optimization does not imply optimized launcher/auditor children. Earlier 353-test calibrated results remain historical. |
| macOS arm64, recorded pyenv CPython 3.14.6 build | Not qualified; the version gate still admits it. The complete normal run retained one assertion failure. |
| Linux CPython 3.14.7, Windows, and other OS/distributor builds | Unqualified; matching the version gate does not qualify them. |

For the macOS 3.14.6 failure, targeted reruns did not reproduce it. The original failing path was not captured, so the cause remains unknown. An Owner risk decision closed the operational follow-up for that historical run, with reopening on recurrence. The failed run remains recorded as failed and the combination remains unqualified. A new candidate requires its own qualification; the earlier risk decision applies only to the historical run.

Verify a candidate against its exact artifact receipt. The historical results above apply to their recorded source; a later release, including one with changed managed documentation, needs evidence assessed for that artifact. Ordinary-user latency, actual worker-1 adoption, anonymous onboarding, production scale and public distribution are outside the scope of the candidate’s synthetic qualification. The bounded private-use observation below covers only its reported use cases.

Control authority can reside in a primary Git checkout or supported standalone non-Git target. Linked workers cannot publish control truth. Submodules, nested repositories/authorities, separate Git directories, partial clones, alternates, unsafe links, and ambiguous topology are refused within the documented checks. Supported work content excludes ignored untracked files but includes tracked ignored files. See [General Work](GENERAL-WORK.md). Unchanged raw CRLF checkout entries can be verified only against unchanged pure-LF blobs with explicit retained text/eol=crlf attributes and exact deterministic byte reconstruction. Only verified active checkout-1, entry-1, delegation-1 or continuation-1 enables this unchanged-CRLF exception. Snapshot hashes and changed-path application remain byte-exact. Changed converted files, attribute changes, external transforms and arbitrary filters are outside this exception; see the unchanged-CRLF contract in General Work. This adds no Windows or general filter qualification, and an exact old/new-artifact compatibility check is still required before an adopter update.

## Data And Recovery

Do not place credentials or secrets in typed records, documents, command examples, or evidence. Product releases inventory an exact managed set. Init preserves unrelated project files; detach removes only verified managed bytes. Unknown and damaged state is preserved with a non-success result. Exact recovery handles documented prefixes, not arbitrary corruption or power-loss atomicity.

Historical private-use reports describe two accepted document Works on human-1 and later worker-1 installation and bounded document continuation, including an existing-file follow-up. Those records are not included here. General usability, real-project multi-worker efficiency and qualification of this checkout remain unverified by those bounded observations. Generation 1/2 support and migration are removed; archived tests and contracts remain historical material. See [Capability Declaration](../PRODUCT-CAPABILITIES.json), [Reference](REFERENCE.md), and [Operations](OPERATIONS.md).

Runtime qualification uses an explicit patch allowlist, not a minimum-version promise. Later 3.14 patches, 3.15, prereleases and free-threaded builds require separate qualification. Historical receipts retain their original runtime identity.

The retained entry-1 contract admits only the exact allowlisted checkout-1 predecessor and makes S1 one-way; same-window compatibility remains bidirectional. Exact qualification is required for each changed pair. Paired schema 2 switch and schema 3 detach boundaries fence audited old writers; literal old history and paired detach schemas 1/2 remain readable. This is a cooperating-runtime compatibility boundary, not protection against arbitrary historical or malicious local code.

Stop cooperating writers and retain exact sources/request/token and restoration-verified external recovery material before a transition. Torn first receipt/S2 files and unsupported O-plus-binding.next combinations can leave no product recovery; external restoration/disposition needs separate authorization. Scoped retired-entry occupants are preserved, never automatically executed or deleted. Mandatory directory-sync checks and injected failures do not prove power-loss persistence or fullfsync behavior. Healthy current status does not retrospectively clear failed sync or unavailable historical content comparison. See [Operations](OPERATIONS.md#entry-1-transition).

## Delegation-1 Implementation Candidate

Continuation-1 inherits the delegation-1 behavior described below. Follow [Continuation-1](README.md#continuation-1) for current lifecycle commands and authorization requirements. Historical versions retain their original meaning. Human authorization comes from the Owner’s actual decision; host authentication and general readiness require their own evidence.

The grant is checked within the existing trusted local OS account shared by Owner and delegate. Core checks actor spelling, exact accepted intent, scope, mode, selected ancestry, one-use historical decisions and revocation. The label does not authenticate the human, model or process supplying it, and Core cannot establish whether an external worker changed its payload. Host enforcement of caller identity and payload integrity, and actual provider use, need their own evidence.

The candidate inherits prior content, evidence, lock, durability and unsupported-state limits. No grant authorizes parent/intent/continuation decisions, broader scope, Git or lifecycle operations. Report static review, synthetic API tests, sandboxed installed execution, normal/parent-O regression, physical fault observation and real adopter experience separately. Each establishes only its tested or observed scope. Qualification of delegation-1 or a newly packaged release needs evidence for that candidate; historical entry qualification does not carry over.

## Continuation Boundary

Continuation shares the trusted local account and serialized writer guard. Actor labels are declarations, not authenticated identities. Project-wide pending/unknown-integrity refusal is intentional; an unrelated malformed continuation can block all official writers, including repair/detach. Exact active repair is only an exception for valid classifiable pending state. Moving a pending home does not rebind recovery. Bounded records, nonrecursive target reading and usage displays do not provide a scheduler, adversarial filesystem isolation or unlimited retention. Exact process/synthetic checks and real fresh-session use require their separately identified evidence.
