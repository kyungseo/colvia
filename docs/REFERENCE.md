# Reference

Document authority and currentness: [Documentation Index](README.md).

## Single-Home Development Commands

The current development profile is `worker-1` with one `.hrn/` home. It exposes a machine interface plus a read-only human view and manual natural-language adapter. An installed project uses `./hv2`. An independent contribution source uses `./hv2 --source-checkout` explicitly.
A source path or a successful test suite is not permission to modify an adopter.

| Entry | Command | Input and effect |
| --- | --- | --- |
| Independent source | `init --profile worker-1 --target PATH --source PATH --authority-home-id ID --operation-id ID --observed-at TIME` | Preview only; save its `request` and token. Apply with the same target/source/profile plus `--apply --input FILE --confirm TOKEN`. |
| Installed or independent source | `status`, `doctor` | Read-only product and complete record-graph diagnostics. Source accepts `--target PATH`. Healthy product output derives `documentation_root` and its README entry from the verified active release. |
| Installed | `update --source PATH --operation-id ID --observed-at TIME` | Preview a candidate; `--apply --input FILE --confirm TOKEN` applies the exact request. |
| Installed | `rollback [--to RELEASE] --operation-id ID --observed-at TIME` | Preview a receipt-backed release; apply the exact request and token. |
| Installed | `detach --operation-id ID --observed-at TIME` | Preview exact managed removal; apply the exact request and token. Project truth remains. |
| Independent source | `update`, `rollback`, `detach` with `--profile worker-1 --target PATH` | Exact original request/token plus `--apply --recover` resumes a supported publication prefix. Preserve unknown/torn bytes. |
| Independent source | `repair --target PATH --source PATH --backup NEW_EXTERNAL_PATH --operation-id ID --observed-at TIME` | Preview restoration of the exact active product. Apply its request/token; interrupted repair uses `--recover`. Installed repair is not exposed. |
| Installed | `intent draft`, `intent prepare`, `intent apply` | Canonical JSON from `--input FILE` or stdin. Apply additionally needs `--confirm TOKEN`. |
| Installed | `work publish [--worker PATH]`, `work prepare`, `work apply` | Canonical JSON from `--input FILE` or stdin. Worker result publish requires the registered linked worker path; start/baseline rebind omit it. Apply additionally needs `--confirm TOKEN`. Worker accept records the decision before exact file application and selects completion only after whole-result checks; human baseline rebind is separate. |

See [General Work](GENERAL-WORK.md) for exact machine input fields and recovery constraints, and [Workspace Contract](WORKSPACE-CONTRACT.md)
for record and lifecycle boundaries. Apply consumes the preview's `request` or prepare's `ticket`, not the outer response envelope.
Preview/prepare does not grant permission; the human decides acceptance. Confirmation tokens bind bytes, not OS identity.

`documentation_root` is project-relative and derived, not another stored authority or document registry. It appears only after product and
record verification succeeds (possibly with pending record publication or unsupported local runtime clearly classified). Pending product,
detached, degraded, or unrecognized state does not invent an active document root. Documentation availability is not a claim that a user read
it or that project-authored documents were accepted. Before detach, retain a trusted independent source/manual if needed.
For a pending Work publication without a decision, preserve and retry the exact original publish request after restoring its prerequisites.
For a pending Work decision or intent acceptance, preserve the original ticket and confirmation token, restore the required runtime/content/document
preconditions, then retry the same apply. Do not invent a replacement decision to bypass pending records. The narrowly supported local or all-pre worker cancellation of a pending Work acceptance follows [General Work](GENERAL-WORK.md); this advice does not remove that contract. An unsupported runtime must be
replaced with final, GIL-enabled CPython 3.14.6 or 3.14.7 before mutation. Single-home mutation entries, root creation, and the shared writer guard enforce implementation, explicit version membership, final release level and GIL-enabled build before writing. This is a trusted-local support check, not interpreter authentication. Status reports these actions without modifying records or manufacturing recovery input.

## Single-Home Paths And Outcomes

`.hrn/format.json` identifies the format and authority. `.hrn/intents/` and `.hrn/work/` contain project-owned truth.
`.hrn/product/` and the root `hv2` are removable runtime material. `.hrn/detached.json` preserves the removal plan and receipt.
`.hrn/staging/` and `.hrn/locks/` are scratch, never selectors. Names, timestamps and path recency cannot choose authority.

| Exit | Meaning |
| ---: | --- |
| 0 | Successful command, including preview, initialized/updated/rolled-back/replayed, or completed detach. It is not admission or write authorization. |
| 10 / 11 / 12 / 13 | degraded / incompatible / conflict / stale |
| 14 / 15 / 16 | partial / uninitialized / unsupported runtime or topology classification |
| 65 | Contract failure; preserve state and inspect the named boundary. Argument-parser usage errors may instead exit 2. |
| 70 | Unexpected internal failure; preserve source, input, and state for investigation. |
| 75 | Bounded test crash injection; not a normal user operation. |

Status/doctor validates records and product identity, not fresh unsubmitted content or real-project adoption. A `detached` result is
readable retained history with mutation refused. Ordinary project edits are not prevented by these diagnostics or logical actor names.

## Single-Home Error Reference

These codes report the violated boundary. Do not repair them by deleting authority, selecting a newer filename, or changing a record hash.
If the launcher is unavailable, inspect from an independent trusted source. Runtime failures are not downgraded to successful observations.

| Codes | Meaning and next action |
| --- | --- |
| `HV2-WORKSPACE-TARGET`, `HV2-WORKSPACE-UNAVAILABLE` | Unsupported target topology, unsafe path, or unavailable observation. Confirm the intended primary/non-Git control root and preserve inaccessible bytes. |
| `HV2-WORKSPACE-RUNTIME` | Mutation requires final, GIL-enabled CPython 3.14.6 or 3.14.7. Preserve the target and use that runtime; read-only diagnostics remain available. |
| `HV2-WORKSPACE-CONTRACT`, `HV2-WORKSPACE-VERSION`, `HV2-WORKSPACE-UNKNOWN` | Invalid root/prefix, unsupported format, or unknown authoritative member. Preserve the folder and inspect the exact format; do not initialize over it. |
| `HV2-WORKSPACE-INVENTORY`, `HV2-WORKSPACE-RELEASE`, `HV2-WORKSPACE-PRODUCT`, `HV2-WORKSPACE-LAUNCHER` | Product inventory, binding, loaded release, or launcher cannot be verified. Use matching trusted source and read-only diagnostics; exact active repair is only for its supported damage boundary. |
| `HV2-WORKSPACE-PLAN`, `HV2-WORKSPACE-RECEIPT`, `HV2-WORKSPACE-TRUTH` | Lifecycle plan, publication chain, or preserved truth contradicts the requested operation. Preserve all records and original input; recover only the exact valid pending prefix. |
| `HV2-WORKSPACE-INIT`, `HV2-WORKSPACE-INIT-INPUT`, `HV2-WORKSPACE-INIT-OPTION` | Init preconditions, exact preview request/token, or option combination is invalid. Re-preview only a fresh supported target; use exact source recovery for a known owned prefix. |
| `HV2-WORKSPACE-SWITCH-INPUT`, `HV2-WORKSPACE-SWITCH-OPTION` | Update/rollback input or target differs from its bound plan. Preserve pending publication; do not substitute another operation's input. |
| `HV2-WORKSPACE-REPAIR`, `HV2-WORKSPACE-REPAIR-INPUT` | Exact source, external backup, restoration plan, or token is unsuitable. Preserve backup and target, then use the exact supported repair/recovery procedure. |
| `HV2-WORKSPACE-DETACH`, `HV2-WORKSPACE-DETACH-INPUT` | Removal plan/token, managed membership, or remaining deletion prefix cannot be verified. Preserve remaining files and use independent-source exact recovery; no recursive cleanup. |
| `HV2-WORKSPACE-CLI-INPUT`, `HV2-WORKSPACE-COMMAND` | Machine fields or command do not match the chosen entry; source lifecycle profile and probe boundaries are also checked. Consult this release's help and exact input. |
| `HV2-WORK-CONTENT` | Content, Git evidence, scope, or ignore policy is unsafe, unavailable, or stale. Re-observe the actual control result and resolve drift before requesting acceptance. |
| `HV2-WORK-UNAVAILABLE`, `HV2-INTENT-UNAVAILABLE` | The corresponding record reader was denied filesystem read access. Preserve bytes and restore authorized read access; this does not establish malformed records or authorize repair. Other graph and I/O failures retain their existing diagnostics. |
| `HV2-WORK-RECORD`, `HV2-INTENT-RECORD` | Typed graph, exact reference, authority, expected current selection, or publication prerequisite does not match. Preserve records; do not hand-edit selectors to make them current. |
| `HV2-INTENT-FACETS`, `HV2-INTENT-FACET`, `HV2-INTENT-FACET-OWNER`, `HV2-INTENT-FACET-STATUS`, `HV2-INTENT-FACET-VALUE`, `HV2-INTENT-VACUOUS-ACCEPTANCE` | Required facet shape/owner is invalid or all facets remain unknown/deferred. Correct a draft and obtain a new exact human acceptance. Unresolved material gaps also prevent acceptance. |
| `HV2-JSON-BOM`, `HV2-JSON-CR`, `HV2-JSON-DUPLICATE-KEY`, `HV2-JSON-EMISSION`, `HV2-JSON-EOF`, `HV2-JSON-LIMIT`, `HV2-JSON-NONCANONICAL`, `HV2-JSON-NONFINITE`, `HV2-JSON-SYNTAX`, `HV2-JSON-UTF8` | Input is not permitted canonical JSON or cannot be emitted safely. Correct proposed input; preserve malformed persisted bytes for investigation. |
| `HV2-PARENT-TYPE`, `HV2-IMMUTABLE-EXISTS` | A parent is not a safe directory, or an immutable destination already exists (including a concurrent publication). Preserve bytes, stop conflicting writers, and inspect exact state before retrying the original operation. Do not delete the destination merely to make a retry succeed. |
| `HV2-INTERNAL` | Unexpected internal failure. Preserve the source version, exact non-secret input, diagnostic output, and target state for investigation. Do not treat this as successful recovery. |
| `HV2-LOCK-ANCHOR` | Writer lock anchor is linked, replaced, or wrong-type. Stop concurrent mutation and investigate the local guard; lock bytes are not authority. |

## Source Utilities

`classify-intent-entry --consequence consequential|non-consequential [--input FILE]` classifies provided gaps without publishing records. An input file has exactly one `gaps` field. `durability-probe --root PATH` writes disposable diagnostic files to an explicitly chosen scratch directory; it refuses a workspace root or descendant. It is not a read-only status command.

Generation commands and `--legacy-baseline` are removed. A source init/update/rollback/detach call without `--profile worker-1` fails instead of selecting an old profile. Installed commands select their bound profile. Source help and installed help deliberately expose different operations.

## Human Review

`./hv2 view` lists verified intent/Work state and current release entry paths. Use `view intent ID [--revision ID]`, `view work ID [--revision ID]`, or `view confirmation --input FILE|-`. Independent source: `hv2 --source-checkout view --target PATH ...`. These commands write GFM to stdout without publishing files, locks, caches or decisions. Imported view errors are GFM with a nonzero exit; bootstrap failures remain JSON/65. Status/doctor and machine commands retain their JSON contracts.

Confirmation consumes canonical ticket bytes, not the prepare response envelope. Observations are advisory and may be unavailable or stale; there is no aggregate permission-to-apply result. Apply checks prerequisites again. A completed record does not prove current project files match. Work comparisons list path/mode/size/digest changes, not historical text bytes; rebind discontinuities are not attributed to the Work.

Document bodies remain project Markdown. The view displays role, path, recorded digest and current observation; open those documents or have your agent explain them. Advisory reads reject links, special/unstable inputs and files over 4 MiB. A Core-readable large file can therefore be unavailable in the view. Worker-observed evidence is not reverified on control.

The worker-1 runtime does not support serial-1 or unknown inventory windows. Independent-source reading retains valid human-1 history, but new candidate creation and execution require worker-1. The installed worker-1 launcher refuses a human-1 binding with HV2-WORKSPACE-LAUNCHER/65. Source --profile human-1 or serial-1 is a parser error/2. Use the independent new source for a reviewed human-1 transition; old binaries are not upgraded by copying a launcher. See [Transition From Human-1](GETTING-STARTED.md#transition-from-human-1).

Command syntax/argument errors retain argparse stderr and exit2; the GFM error contract begins after argument parsing. The default human view omits the managed file inventory; status/doctor retain machine diagnostics.


Paths and digests use dynamically delimited GFM code spans; ordinary punctuation stays readable in raw stdout. Control characters are visible escapes and literal backslashes are distinguished. The view summarizes status before details and separates intent documents from Work revision documents. Revision progress/next_action are recorded historical fields, not the current derived Work state. Selected history follows the parent chain and includes the human action, actor and reason; the separate decision list is not chronological.

Confirmation advisory checks include required ticket references and, for Work accept/rebind, required bound intent references. The bounded reader may be stricter than Core, so an unavailable observation is not proof of a Core refusal. Worker-observed evidence is not reverified on control. Reject/revoke do not require live reference agreement. Worker accept cancellation still requires all changed paths pre and no durable result selection. There is no aggregate readiness grant. View-internal type/attribute/index failures return GFM with exit70; argument errors remain argparse/2 and pre-import launcher errors remain JSON/65.

The bounded reader requires searchable and listable physical ancestors from `/`, exact spelling, no symlink ancestor, and a regular single-link file. A macOS `/tmp` or `/var` alias can therefore be refused: use the real physical path to an authorized ticket or canonical stdin. Do not weaken the Core or remove files to bypass an unavailable observation.

Later patches, prereleases and free-threaded builds are rejected. Other OS or distributor builds matching the accepted version conditions may execute; that is not a claim that they have been qualified. See [Security and Support](SECURITY-AND-SUPPORT.md).

In status, `supported_baseline` retains the historical first qualified version; it is not a minimum version. `supported_versions` is the exhaustive patch allowlist.

In status, `runtime.supported` reports the version gate, not OS/build qualification. A `classification: pass` result does not establish that this OS/build or an actual adopter has been qualified.


For result acceptance, pair `./hv2 view work ID --revision REVISION_ID` with `./hv2 view confirmation --input FILE` (or `-`) for the same selected revision. Work details contain `observed_scope` and `unavailable_scope`; the confirmation view does not directly repeat these arrays. Explain all unavailable items against the human's declared acceptance criteria before applying the exact ticket. Nonempty observation text alone does not make a graph degraded, and an empty list does not prove verification. Required-reference and live-content refusals remain mandatory. See [General Work](GENERAL-WORK.md#observation-limits-and-human-acceptance) and the current managed adapter.

The author-declared `unavailable_scope`, an advisory reference observation labeled unavailable, and a `*-UNAVAILABLE` authority-read error are different. The last remains a degraded/write-refusal condition; neither observation prose nor an advisory display waives it.


Worker Work/confirmation views distinguish control baseline from retained candidate and partial application. Changed Work references display candidate and live-control observations separately. Human baseline refresh compares old baseline/candidate with the proposed baseline and labels content matches without attributing their cause. These read-only observations do not authorize an action or replace guarded validation. See [Worker Review Observations](GENERAL-WORK.md#worker-review-observations).
