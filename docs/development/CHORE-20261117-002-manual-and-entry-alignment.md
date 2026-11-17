# CHORE-20261117-002 · Align the public and installed Colvia guides

Status: The Owner accepted the local revision and verification on 2026-11-17. A local documentation commit is proposed.

## Purpose and scope

Use the bilingual manual structure and three commits ending at `ac4f800`. Keep the existing README links for architecture and troubleshooting. The Owner approved updating public, installed and agent entry guidance, retaining the earlier profile’s material and URLs, adding a private reporting route, examining Windows command bytes, and checking the documentation that will ship. Existing review and this scoped plan serve as the planning input. The local work and handoff have a 120-minute ceiling.

The earlier source tag and distribution release were verified before this change. The source’s public `v0.1.0` tag points to `e10285c` and the separate downloads repository publishes the pre-release. The affected Windows update example was in the repository manual on `52e88c3`. The matching released Windows ZIPs contain the official installer rerun guidance and no backspace character in the manuals.

## Implementation boundary

Public entry links point to the current manual. The repository index routes earlier section links to the preserved index. Earlier-profile packaging keeps the historical index and agent entries at their original installed paths. The SQLite Preview bundle uses the bilingual topic pages and installed guide indexes. The work does not change runtime commands, authority, support promises, or publication policy.

The Owner will relay the result review. Source commit, push, tag changes, and deployment remain separate decisions.


## Verification

- Local GFM rendering checked 62 documents and installed entries, including 970 relative links and all 94 forwarding anchors in the repository documentation index. The rendered text contained no stray emphasis markers. No unexpected control characters were found. The four English and Korean Windows status and update examples matched the intended command bytes.
- Rendered all 32 Mermaid blocks in the English and Korean architecture, overview and Work guides with local Chromium.
- The focused installer-bundle, earlier-profile source-layout and ordinary-Work checks passed 25 distinct tests. After the final guide edits, 24 bundle and source-layout tests passed. All 30 files read by the earlier profile's source packager match the baseline bytes. The three moved source documents keep their installed names and modes. Earlier-profile preparation and its exact-input tests require the retained source checkout with both archived agent entries. The public checkout preserves the earlier manual links.
- Reused the public v0.1.0 inputs to assemble local unsigned ZIPs for macOS ARM64, Windows x64 and Windows ARM64. Each contains 21 guide files and the current agent guide. All other member paths, stored modes and SHA-256 entries match the published archives. The installed index links to the command that displays the installed version.
- The English and Korean manual retains language-specific directory-tree labels and compatibility anchors. The manual's paired instructions cover user-account scope, access refusal, pending notification delivery, and the missing worktree procedure.

Verification covers local rendering, package assembly and the focused checks. Use the existing installation and update results for the published v0.1.0. The new guide revision awaits manual result review.


## Manual review follow-up

Both manual reviews used the same source base and reviewed file set. The Owner authorized applying their supported findings.

- The bilingual guides identify the removal recovery directory and explain the space used by retained installation files. The report tutorial adds an optional submission notification and explains the user's separate decision after review.
- The Git troubleshooting entry covers both connection preview and commands in an already connected project. It explains missing and bare worktree entries, with read-only inspection and recovery guidance for the maintainer.
- The two reference pages preserve inbound notification, resume and review anchors. The source repository retains forwarding pages for earlier paths still linked by development records. Package links lead to pages included in the Preview guide inventory.
- The folder-move guidance and platform evidence distinguish a same-volume ordinary-folder move on Windows ARM64 with official v0.1.0 from the analogous x64 hardware trial with an isolated 0.1.0 build. Both used manager commands and checked existing Work. Windows Git checkout moves and agent-led Windows moves require separate evidence.
- The packaged architecture and reference headings use Preview wording. The guides use the recorded Codex sandbox configuration value and preserve the submission and recovery conditions while aligning Korean terminology.

Focused checks passed 31 tests. The final local GFM check covered 68 documents or installed entries and 1,000 local links. The checked Windows command examples match the intended bytes. The 32 Mermaid blocks are byte-identical to their previously rendered inputs. Each final unsigned platform ZIP includes the corrected guides and legacy reference anchors. The non-guide inventory matches the published v0.1.0 archives. Device results are inherited from the cited Windows tests.
