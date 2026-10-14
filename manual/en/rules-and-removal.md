# Extend Project Rules And Remove Colvia

This page describes the unactivated `entry-1` candidate. Use requires separate exact-artifact qualification and installation approval; the historical checkout-1 exercise below does not qualify these commands.

[Manual home](README.md) · [한국어](../ko/rules-and-removal.md)

Keep project-specific instructions in files the project owns. Colvia supplies common guidance and a managed adapter, which helps an agent turn your request into the supported workflow. Removing the installed runtime removes that guidance from the project; it does not remove your own instructions or project history.

Use this guide when adding a project rule, adapting how an agent works, reviewing a runtime update, or leaving Colvia. The examples are proposed instructions to adapt with the project Owner. They are not an automatic extension mechanism or a tested native-agent integration.

## 1. Identify Who Owns Each File

| Material | Where it belongs | Update and removal behavior |
| --- | --- | --- |
| Common rules and adapter source | The independent Colvia source checkout | Changed through source maintenance; detaching another project leaves this checkout intact |
| Installed common rules and adapter | The verified release under `.hrn/product/` | Managed by runtime lifecycle; included in exact detach removal |
| Project rules and local agent guidance | Existing project instructions or a project-owned document | Updated or retired by the project Owner's authorized change; detach leaves them intact |
| Agent entry | Project `AGENTS.md`, `CLAUDE.md`, or the existing equivalent | Points to the current managed adapter and local rules; detach does not rewrite these pointers |
| Accepted history and authored documents | `.hrn/` authority and referenced project documents | Preserved by detach; removal is not permission to rewrite history |

Use `./colvia view` to find the current installed manual and adapter. Do not copy a release-directory path into the project entry or edit installed payload files. Changed or unexpected product bytes can block lifecycle operations. A separate user/global agent rule is also outside detach; its owner decides any change, including effects on other projects.

## 2. Add A Small Project Rule

First check the existing rule for this situation. Extend its relevant section if one exists. Record the purpose, responsible maintainer, applicable changes, source section/revision, local choices and how to check the result. Use the project's current document layout; no new rule directory or registry is required.

For a CLI project, a proposed rule might say: when a CLI option changes, include the usage page and affected examples in the authorized scope, then report which commands and checks changed. The exact page and checks come from that project's code and documentation. This example does not mandate CLI checks for unrelated projects.

Show the proposed rule and entry-pointer diff to the Owner. Follow [Check Before Writing](../../docs/REFERENCE.md#check-before-writing) before applying it: a required document reference or submitted result can require a new acceptance or supported rework first. Record the outcome in the existing Work narrative when authorized; do not create a second progress log.

## 3. Adapt The Agent's Instructions

A local adapter can be a short project-owned section that tells the agent which rule to read and what to explain. Start there before creating a separate file. If the instructions need their own page, this is an illustrative layout, not a required directory structure:

```text
AGENTS.md
  -> ./colvia view -> current managed adapter
  -> docs/agent-guide.md -> relevant project rule and checks
```

For example, `docs/agent-guide.md` could contain this proposed instruction:

```text
For an authorized CLI change, read the project's CLI documentation rule.
Identify the affected usage page and examples before editing.
At result review, explain changed commands, executed checks and remaining limits.
Use the existing Work narrative; follow its scope and reference requirements.
```

Add a short pointer from the existing agent entry to the relevant instructions in `docs/agent-guide.md` for CLI changes. Keep genuinely tool-specific instructions in that tool's entry. Do not duplicate the full managed adapter. Local instructions cannot grant acceptance, change immutable records, bypass integrity checks or turn a runtime refusal into permission. If the instructions conflict, show the conflict to the Owner before acting.

Check that the pointer resolves and ask a fresh session to explain which instructions it read and when they apply. Record an unavailable session check as untested. A Markdown pointer does not prove that a particular tool loads it automatically; native skill packaging or discovery needs that tool's own setup and verification.

## 4. Review A Runtime Update

A runtime update changes the managed release and the path reported by `./colvia view`. It does not update local rules or adapters. Compare the previously adopted source section/revision, the new guidance and the project's current rule. Retain intentional local choices, show conflicts and seek the appropriate authorization for project edits. If the old source cannot be recovered, report the uncertainty instead of calling the comparison complete.

Treat runtime installation and local rule edits as separate changes requiring their respective authorization. Check pending work and document-reference effects before changing either; update authorization is not permission to alter a submitted result. After an authorized update, confirm the current adapter path, relevant local pointers and the affected checks. Preserve old referenced versions where history or recovery needs them.

For a checkout-1→entry-1 transition, only the exact allowlisted predecessor is supported. Stop cooperating writers and retain exact old/new sources, original request/token and restoration-verified external recovery material before applying. S1, the first durable switch receipt, is one-way: no rollback to checkout-1 or earlier, even before new records exist. Local/parent manifest and captured-child reference checks can block admission; old worker results need separate Git approval, explicit same-intent worker rebind and resubmission. Runtime does not edit project entry pointers or perform Git actions. See [Entry-1 transition](../../docs/OPERATIONS.md#entry-1-transition).

Torn first receipt/S2 files and unsupported O-plus-binding.next prefixes may have no supported product recovery; preserve them and obtain separate external recovery/disposition approval. OLD pending init/repair/detach requires the matching retained OLD source and original request, not a new entry-1 request. A scoped retired `hv2` occupant is preserved: otherwise-valid live diagnostics report conflict/12 and lifecycle calls refuse65; after schema-3 detach loses its binding, source diagnostics instead use degraded/10 with the collision error. Neither a confirmation display nor a healthy current status certifies historical comparison or earlier synchronization. Current detach uses paired schema3; paired1/2 history remains readable but its recovery belongs to matching OLD source.

## 5. Remove Colvia And Finish Project Entry Cleanup

The exact command and recovery contract is in [Operations](../../docs/OPERATIONS.md#detach). In the current development candidate, completed detach does not support reinstallation over retained authority or an attach operation. Decide before approving removal how to continue project work without Colvia and read the retained history; do not delete history to make installation possible.

1. **Prepare the exit.** Identify the current installation and pending Work, intent or lifecycle operations; resolve those operations through their supported paths. Before approval, decide how unfinished Work and results awaiting a decision will be handled: detach does not block every unfinished Work state. Identify only the affected entry pointers, local rules, tool-specific instructions and hooks that call Colvia, and propose what will survive or be replaced. While the runtime is available, use Check Before Writing to trace whether retained records reference the entry and rule files to be edited in step 5, and include that finding in the proposed edits. Review project-instruction edits separately and complete any authorized pre-detach edits under Check Before Writing before preparing the request; leave removal of `./colvia view` pointers until step 5. Secure compatible independent source and useful manuals outside the target before applying detach; retain required historical/reference bytes. Do not run an all-repository cleanup.
2. **Review the preview.** Have the agent prepare the exact detach request and explain its removal/preservation list. Keep the original request and confirmation token outside the target before applying it. As a precaution, defer further project edits until completed detach is verified, including during partial recovery; publishing their Work records can change the truth bound by the request. If observed state changes before removal begins, stop and prepare the appropriate new request for approval.
3. **Approve and apply the exact operation.** The Owner authorizes the target and request. Apply once using the documented confirmation. On a partial failure, retain the original request and confirmation token and use the specified independent-source recovery. Keep the target directory at its original path; a copy or clone is for read-only inspection, not the recovery target. Do not treat a missing launcher as proof of completed detach or start ad hoc deletion.
4. **Verify removal and preservation.** Confirm the detached state through the independent-source checks; neither receipt presence nor launcher absence proves completion. The launcher and managed product files are removed; `.hrn/detached.json`, format, planning, intent/Work history, authored documents and ignored scratch are retained. Keep the exact inputs still needed for replay or recovery.
5. **Finish the approved project edits.** Remove or replace the authorized obsolete Colvia calls in the entry pointers, tool-specific instructions and hooks identified in step 1, including `./colvia view` and managed-adapter instructions. Record the verified completed detach and retained-history location as facts; do not write conditional instructions that skip checks. Retain applicable project rules and document how work will continue. Preserve required historical/reference bytes; if a referenced rule must stay fixed, keep it and propose a separate current instruction. Do not delete a tool directory or global configuration just because it contains a Colvia pointer.
6. **Check re-entry.** Confirm that the new entry's links resolve, a new session is no longer told to invoke the removed runtime, remaining hooks do not invoke it, and retained history is available for read-only use. Report a pending project edit or an untested session explicitly. Successful runtime removal alone does not mean entry cleanup is complete.

Project entries need to distinguish an expected completed detach from an unexpected broken installation. Keep useful non-Colvia instructions in `AGENTS.md`/`CLAUDE.md`; do not add an automatic fallback that silently ignores a missing runtime.

## Basis And Limits

This guide explains the current [Repository-Owned Rules](../../docs/REFERENCE.md#repository-owned-rules), [project-entry preparation](../../docs/GETTING-STARTED.md#prepare-project-agent-entry), [detach contract](../../docs/WORKSPACE-CONTRACT.md#receipt-bound-detach) and [retained-history operation](../../docs/MANUAL-OPERATION.md). It is a repository-only guide, outside the installed payload. This page refers to source guidance newer than the practice release identified in the manual README; that installed release may lack these added sections. Before detach, use `./colvia view` to locate and check the verified documents for the actual target. Do not assume this guide updates the installed release.

The example local adapter and the complete human/agent exit sequence have not been tested in a native agent session. Document checks and synthetic lifecycle tests do not establish that a person understood the guide or that every agent follows these instructions.

[Manual home](README.md)
