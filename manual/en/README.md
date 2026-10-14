# Your First Project With Colvia

This page describes the unactivated `entry-1` candidate. Use requires separate exact-artifact qualification and installation approval; the historical checkout-1 exercise below does not qualify these commands.

[Start the tutorial](getting-started.md) · [Key concepts](concepts.md)

[한국어](../ko/README.md)

When you return to an AI-assisted project, the conversation may no longer tell you which request you approved or whether the result was accepted. Colvia keeps those records with the project. You decide the scope and accept the result; the agent prepares the records and carries out the authorized work.

This guide takes one small project from preparation to its first completed Work, then shows how to resume from its files without the old conversation. You will build a Python task-list CLI that adds and lists tasks. You do not need to write Colvia JSON yourself.

## Before You Start

Use a fresh, disposable practice project in a durable directory, a working Git installation, and final, GIL-enabled CPython **3.14.6 or 3.14.7**. The `python3` command used by the launcher must resolve to that supported runtime. Later patches, prereleases and free-threaded builds are rejected.

You also need an independently supplied, trusted and qualified Colvia source checkout for the `entry-1` profile, plus an agent that can read local files and run approved commands. This private development edition does not provide a public installer or download location. Ask the maintainer for a source checkout and a separate qualification receipt identifying that exact entry-1 artifact. Its preview must match that receipt, not the historical checkout-1 digest below. This documentation candidate does not supply the new qualification receipt. Confirm that the receipt covers the environment you will use; this guide's synthetic exercise is not that qualification.

The examples address Codex in an existing project conversation. They are suggested requests, not recorded transcripts or evidence that a particular prompt reliably produces the same agent behavior. Your project instructions and permissions still apply.

## The Shortest Path

| Read | What you will do | What to check before continuing |
| --- | --- | --- |
| [Prepare the project](getting-started.md) | Set up the project, install Colvia and write the initial plan | Installation is healthy; no intent or Work has been created by installation |
| [Complete the first Work](first-work.md) | Approve one request, implement its scope and review its result | The accepted result is selected; current files match it |
| [Resume in a new session](resume.md) | Read the project and Colvia records without the old conversation | Explain what is complete, what is unverified and what needs a new decision |
| [Key concepts](concepts.md) | Look up ownership, terms and common stops | Distinguish a proposal, an accepted request and a completed Work |

Follow the first three pages in order. Open the concepts page when a term is unfamiliar. The tutorial uses one local editing Work; it does not introduce worker worktrees or parallel execution.

## What Was Checked

For the historical checkout-1 candidate on 2026-10-05, the preparation, actual source installation, typed intent acceptance, local Work submission/acceptance, and read-only resumption were executed in a synthetic Git project on macOS with CPython 3.14.7. Four tests checked the example CLI: empty listing, ordered add/list, blank-task refusal without writing, and read-only listing. Separate new CLI processes read the completed records and unchanged result.

The acceptance decisions in that exercise were scripted. A fresh independent agent session and a real person's comprehension were **not tested**. Windows, Linux, cloud deployment, malformed task-data recovery and general onboarding usability were not tested in this exercise. Runtime admission and operating-system qualification are different; see [Security and Support](../../docs/SECURITY-AND-SUPPORT.md).

This is a repository-only review edition. It is not copied into an installed project's managed payload. Within an installed project, `./colvia view` identifies the current installed manual and adapter; `./colvia status` reports the verified `documentation_root`. Those installed documents remain the operating reference. The relative links below work in this source checkout or a complete copy of it.

## Keep These References Nearby

- [Extend project rules and remove Colvia](rules-and-removal.md): local instructions, runtime updates and entry cleanup after detach.
- [Installed setup procedure](../../docs/GETTING-STARTED.md): installation and project preparation.
- [Command reference](../../docs/REFERENCE.md): exact commands, input contracts and diagnostics.
- [Operations](../../docs/OPERATIONS.md): update, recovery, repair and removal.
- [Key concepts](concepts.md#when-to-stop): short guidance when the first path cannot continue.

Linked technical and operating documents under `docs/` are in English.

Historical exercise — Edition: private development, `checkout-1`; checked 2026-10-05.

| Historical checkout-1 exercise identity | Value |
| --- | --- |
| Source revision | `2536c3106494d2b409e522ff4decb39f88d4aaf5` |
| Release SHA-256 | `a5a9c5b408e40cd0bfdd6bf3c5d8d23676c138504e278417ecb656729c1b8456` |

The source revision and digest identify the historical Harness v2 checkout-1 exercise, not the current entry-1 source or these manual pages. The pages are outside that commit and managed release. Preserve those old identities as historical evidence; do not use them to approve an entry-1 installation. Compare the new preview only with its separately supplied exact entry-1 qualification receipt. A different HEAD is not itself release qualification.

---

[Start the tutorial](getting-started.md) · [Key concepts](concepts.md)
