# Verified startup and on-demand agent guidance

The Owner approved local implementation, focused verification and one static result review on 2026-11-19. The cumulative implementation limit is 75 minutes. The [reviewed plan and dispositions](startup-guide-plan-review.md) and [P1 intake](product-evidence-and-followups.md#p1-short-guide-at-the-start-of-a-new-chat) define the scope. Start revision: `eed271ad5aa665f0002c9eded69d82f224da9ce0`. Product signing, release and changes to existing installations require separate decisions.

The Windows project wrapper forwards argument tokens to the native executable, which passes them to the selected product. Topic handling lives in the shared Python product. Verify the platform package and reuse existing native evidence for unchanged forwarding. Distinguish a Windows-targeted package check on macOS from a Windows process run.

## Baseline guide coverage

Original lines 1–40 and 104–126 now inform the short entry; 41–102 form the plan topic; 128–178 and 327–331 supply recovery; 180–230 and 302–304 supply work; 232–281 supply revision; 293 supplies git; 294–300 and 306–325 supply management; 283–291 and 334–365 supply execution. Replace former same-page navigation with verified topic commands. Keep entry decisions and cross-topic prerequisites on the default path.

## Result and verification

The bare agent guide is 70 lines and 4,366 UTF-8 bytes (baseline 365 lines and 24,976 bytes). One optional topic uses the same pinned slot, inventory and digest checks. Both successful forms retain the original JSON field. The two manual reference pages document the command. Project entry blocks and native binaries need no change. Public release notes and removal of pending labels in shipped manuals belong to the release freeze. Product ZIPs signed for distribution and installation on a user's account were outside this check.

CPython 3.14.7, macOS ARM64. Eight distinct focused unittest methods passed across BundleTests, ManagedEntryTests and ProjectLauncherTests/VerifiedEntryArgumentTests. Covered byte identity, three synthetic target archives, staged topic access, bare and structured output, invalid input, tampered/missing/unlisted files, no project record open for guide, command forwarding and existing manager argument handling. The changed boundaries passed again after review (four methods). Markdown from eight agent guides and two manual pages rendered with GFM. The original binding sections in the topic files passed a baseline text comparison, with old in-page links replaced by topic instructions.

A synthetic connected folder kept its original entry block. Separate host-interpreter processes loaded the staged lib and managed slot with a fixture runtime identity. From startup they discovered the sole active Work without a supplied ID, read the retained scope and checks, fetched the work topic, submitted, retrieved the exact review and opened recovery on demand. This exercises CLI routing; an independent fresh agent conversation was not observed. The previous parser accepted bare guide and refused a topic; the new reader refused loose content in the old inventory. Bootstrap inspection rejected missing and unlisted ZIP members and same-size changed bytes.

Windows x64: the retained v0.1.1 ZIP SHA-256 matched the previously recorded artifact (`e6cc7bb845e02ca4f48f9a09381f95283d8c7f5e1af6b83e9524d2adafaa6e47`). The Windows storage reader and generated project launcher source matched its members. Native launcher source is unchanged from v0.1.1. This change routes fixed ASCII topic words in shared Python and reads UTF-8 through the pre-existing verified path. The x64 and ARM64 archives were staged on macOS; no native Windows process ran for this task. At release freeze recheck the actual native binary and runtime identities against the predecessor. A changed binary, quoting or platform reader would require a new evidence decision.

## Result review

Claude Opus 5.5, a separate Claude Pro subscription CLI session with tools disabled, reviewed the relevant diff, new topics and reported synthetic results. Packet SHA-256: `d70aa8c8cf5b313827f08fe592b1cb7bcc99a5d15eb11fb7de283da0716fed57`. The Driver checked all input files against their pre-review hashes before applying corrections.

# Review: Colvia startup guide split onto verified topics (base `eed271ad`)

## Verdict: **CONDITIONAL**

The implementation is sound. Topic resolution uses a fixed allowlist with no path input. Each read is checked against the manifest and hash. An unlisted file in an old slot is refused. Bundling and the CLI path stay narrow. The two conditions below are small, but they bear on the stated goals: verified topics on demand, and reading the right topic before any notification.

I could not compare against the baseline, so I could not confirm that details were "moved mechanically per recorded coverage". I took the recorded coverage as given. My estimate is that the bare guide is about 70 lines, close to the limit, which is consistent with the passing test.

## Conditions

**C1. Confirm the installer does not copy `adapters/colvia-work/*` wholesale** (packaging and startup safety)
- `foundation_bundle.py` now places seven topic `.md` files beside `SKILL.md` in `adapters/colvia-work/`.
- If the unchanged installer copies that directory into a host skill location, unverified copies of the topic files will sit next to the skill. An agent could read them directly instead of through `guide TOPIC`, which bypasses the manifest and hash check this change adds.
- If the installer copies only `SKILL.md` by explicit path, no change is needed. Record that fact.
- Otherwise, choose one:
  - put the topics in a sibling path such as `adapters/colvia-work-topics/`, updating `GUIDE_FILES` to match; or
  - change the installer to copy `SKILL.md` only.

**C2. Add the notification step to `work.md`** (correctness after the split)
- `work.md` says "Submit the reviewable result automatically when the approved work is ready."
- For a requested notification, though, `delivery prepare/start/run` *replaces* ordinary submit (see `management.md`).
- Today only the bare guide's table row ("read it **before submission**") prevents a wrong ordinary submit. An agent working mainly from `guide work` has no local reminder.
- Suggested fix: add one line to the submit bullet in `work.md`: *"If a result notification was requested, read `guide management` before submitting; its delivery path replaces ordinary submit."*

## Non-blocking findings

1. **Test portability on Windows:** `tests/test_foundation_bundle.py`, `test_verified_guide_from_staged_bundle`
   - `read_text()` uses the locale encoding and universal newlines.
   - `entry.guide()` decodes the raw bytes as UTF-8 with no newline translation.
   - On a Windows checkout (cp1252 locale, or `autocrlf` producing CRLF), the comparison can fail, partly because of the `’` characters.
   - Fix: use `read_bytes().decode('utf-8')`.
2. **Unmapped OS errors:** `managed_entry.py`, `guide()`
   - Only `FileNotFoundError` is mapped to `managed-guide-unavailable`.
   - `IsADirectoryError`, `NotADirectoryError` and `PermissionError` on the topic path would surface differently, possibly as a traceback.
   - Fix: catch `OSError`, unless `home.files.read` already wraps these errors.
3. **Misleading error for a misplaced flag:**
   - `./colvia guide work --json` now fails with `invalid-guide-topic`, and the message lists topics.
   - The real problem is the position of `--json`.
   - Option: when `extras` starts with `-`, report "options go before the command group".
4. **Message language:** the `invalid-guide-topic`, `managed-guide-unavailable` and `managed-guide-changed` messages are Korean only.
   - This matches the existing `failure()` pattern, but English users get a Korean hint.
   - Track it with the existing localization work if one exists.
5. **Lazy import:** `presentation.failure` imports `TOPIC_NAMES` inside the function.
   - `guide_topics` has no imports, so a module-level import is safe and simpler.
6. **No size guard for topics:** add a test asserting each topic file is ≤128 KiB, the read cap in `guide()`. Growth would then fail in CI rather than at runtime.
7. **Inconsistent headings:** topic files open at mixed levels.
   - `#` in git, management and plan.
   - `##` in execution, recovery, revision and work.
   - This is cosmetic and an expected side effect of a mechanical move. Normalize it in a later pass if wanted.

## Verified as correct (static)

- **No traversal or option injection.**
  - `topic in GUIDE_FILES` gates every lookup.
  - `''`, `WORK`, `../private`, `--private` and multiple topics are all refused.
  - The tests show `private` never appears in the output.
- **CLI compatibility.**
  - For non-`guide` groups, `parse_known_args` plus `error('unrecognized arguments: …')` matches `parse_args` behavior and exit code 2.
  - `manage` with REMAINDER is unaffected.
- **Read-only guarantee.**
  - Both bare `guide` and `guide TOPIC` run without `workspace()`, which the test enforces with a patch.
  - `--json` output is unchanged in shape.
- **Old-slot behavior.** A new skill paired with an old slot fails closed through argparse, and the bare guide says to stop and report when a topic cannot be verified. An old slot never serves a loose unlisted file.
- **Single source of names.** The builder and reader share `GUIDE_FILES`, and `guide_topics.py` is packaged through the `src/colvia` tree.
- **Bare guide safety content.** The following stay in the bare guide, unconditionally:
  - the complete-list rule before inferring an empty project or a unique match;
  - the disclosure that plan capture saves file contents and may enter backups;
  - the separation of acceptance from Git, publication and notification authority;
  - the ban on fallback records and workarounds.
- **Authority.** I found no new implicit action or authority in the topic text as presented.

## Evidence gaps (acknowledged, in line with the chosen scope)

No Windows process was executed and no fresh LLM was observed. The Windows conclusions rest on synthetic staging and on path handling that is platform-neutral. Signing and publishing were out of scope.

### Driver disposition

- C1 accept/verify: initial installation and release update both pass the verified archive to `stage_archive` under the installation slot. Project setup writes the selected launcher, connection metadata and managed guidance blocks in AGENTS/CLAUDE. No guide directory is installed into a host skill directory. The connected-folder fixture used the original entry block. Keep topics in the verified slot.
- C2 accept/fix: the work topic itself now directs the agent to the management topic before submission with a requested notification. The delivery route replaces ordinary submission. The package-level test verifies this instruction.
- Portability and bounds accept: compare exact UTF-8 bytes decoded without universal newline translation. Each of the eight real documents is already passed through the 128 KiB production read limit in the test. Scope of this check is the staged candidate.
- OS errors revise: missing and wrong-kind path errors use the unavailable guide message. Preserve explicit access-denied and integrity diagnostics. Unexpected OS failures are handled by the existing CLI error boundary.
- CLI hint and import accept: invalid topics list valid words and explain placement of --json; use the module-level topic constant. Retain the current Korean diagnostic convention and existing Markdown section headings. Product-wide localization and cosmetic heading normalization were not selected.
- Checks against the final edits were performed by the Driver. The review verdict remains conditional; the two conditions were addressed and documented, with no second reviewer invocation. Local implementation and checks are ready for Owner acceptance. Retain the topic checkout and bounded private inputs for the next commit and release preparation.
