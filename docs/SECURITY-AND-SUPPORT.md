# Security And Support

This document describes the earlier Continuation-1 profile and the listed historical extensions. See its [authorization and qualification](README.md#continuation-1). For the SQLite Preview, use the [current record and access guide](../manual/en/foundation-preview.md) and its [observed environments](development/product-evidence-and-followups.md#record-foundation-verification).

This development candidate assumes one trusted local OS account and cooperating agents. Logical actor and acceptance-authority strings are declarations, not authentication. Confirmation tokens bind request bytes; they do not prove a human approved them. File checks and locks do not defend against an adversarial process with the same account bypassing the protocol.

The managed macOS arm64 distribution separately admits its exact pinned CPython 3.14.10 tree and manifests with isolated entry. `supported_versions` remains the legacy allowlist; `admission_path` reports the current gate. Windows policy is unchanged. Preserve a damaged managed runtime and follow [its recovery procedure](OPERATIONS.md#onboarding-update-recovery-and-removal). Tree identity admits an exact relocated copy and does not authenticate installation provenance.

## Runtime And Scope

The legacy mutation path requires final, GIL-enabled CPython 3.14.6 or 3.14.7. The managed macOS path additionally permits only the exact CPython 3.14.10 tuple and tree described above. There are no third-party runtime dependencies. The selected gate checks its version/build mode and, for managed entry, the complete tree and manifests. An OS or distributor build can pass it and execute even if that combination has not been qualified. Read-only diagnostics can report a rejected runtime while mutation remains blocked.

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

## Official Execution Candidate Boundary

`official-execution-2` is an explicit macOS product candidate, separate from the default `continuation-1` and native Windows qualifications. It binds the existing Work/intent and current document view to a single-use local approval declaration. A fixed official CLI/helper uses normal TLS transport and the accepted OS IPC policy; stronger prepared-native transport claims do not transfer. The Host owns effects and keeps its shared writer lock through observed child termination. Cancel marker publication is the sole concurrent write exception. Unknown effects stay blocking until an explicit observed resolution. Same-account tampering, unseen detached processes, general quality, actual adopter use and Owner acceptance remain separate limits.


## Help and reporting

For an ordinary problem, report the OS and architecture, asset name, step, expected result and actual result. A short example using a practice folder is enough. For a suspected vulnerability, contact the maintainer who supplied your private build privately. Keep credentials, private paths and original project content out of reports. We’ll list a private reporting contact here before public release.

일반 문제라면 운영체제·아키텍처, 받은 파일 이름, 멈춘 단계와 기대했던 결과를 적어 주세요. 연습 폴더에서 재현한 짧은 예시면 충분합니다. 보안 문제는 공개 이슈에 남기지 말고 비공개 배포본을 제공한 담당자에게 따로 알려주세요. 계정 정보·비밀값·개인 경로·프로젝트 원문은 제외해 주세요.

## License

Colvia’s own source and documentation in this revision are licensed under the Apache License, Version 2.0. Third-party software, including the Python runtime and the bundled Markdown parser where supplied, keeps its original license and notices. Earlier published artifacts retain the notices they shipped with.

이 버전의 Colvia 소스와 문서에는 Apache-2.0을 적용합니다. 함께 제공하는 Python과 Markdown 파서 등 제3자 구성요소에는 각각의 원래 라이선스와 고지가 적용됩니다. 아래는 설치본에서도 읽을 수 있는 공식 영문 원문입니다.

<details>
<summary>Apache License, Version 2.0</summary>

```text

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright 2026 Kyungseo Park

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

```

</details>
