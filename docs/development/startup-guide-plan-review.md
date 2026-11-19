# Short startup guide for connected projects

The Owner selected a shorter first read and a subsequent Preview containing the merged pre-Git credential check. Starting source: `eed271ad5aa665f0002c9eded69d82f224da9ce0`. The current entry has 365 lines, 3,871 whitespace-delimited words and 24,976 bytes. Source and installed file names differ. The approved Git guard and the registered P2 complete-removal candidate have distinct scopes.

## Plan review

Driver: Codex. Reviewer: Claude Opus 5.5, fresh Claude Pro CLI with tools disabled. Static review of the following summary, without access to the repository or tests. Request SHA-256: `2a2195c6ec6e70e3634def13aeccc734ea028e60cfa26c5c7a2595fd6e41a778`.

Static plan review only. No tools or files. Colvia public base eed271ad5aa665f0002c9eded69d82f224da9ce0. Owner selected shorter startup guidance plus the already merged pre-Git credential gate for a subsequent Preview. Judge this plan, not unprovided code. Return PASS, CONDITIONAL or BLOCK with compact actionable findings.
Today the verified project launcher guide returns one 365-line English adapter. The managed entry acquires the existing lease, verifies slot manifest digest, finds one fixed inventory name, verifies size and digest, and decodes UTF-8 without opening any Work. Bundle assembly currently adds only that fixed adapter. Old connected folders already call bare guide and ordinary list.
Plan: keep bare guide and JSON response shape; allow a finite set of optional topic words, mapped to fixed bundled agent documents using the same verified read (never caller-supplied filenames). Keep entry sufficiently self-contained to run the verified launcher, read project rules, find all relevant Work including pagination, select exact IDs/state and current decision, handle unknown or ambiguous cases, and route new work. Preserve no-Work small edit conditions, before-plan content/authorization, exact acceptance and no implicit Git approval. Read new-task planning, access and recovery, execution/submission/revision, optional management including Git and notifications at their relevant step. Use existing wording where binding. Avoid hidden link dependencies and ensure workflows with special notification or Git steps choose the right procedure BEFORE mutation. A refused lookup is not an empty Work. Keep old commands and connected project entry text compatible.
Verify all old substantive instructions retained, topic links and state routes, concise default versus baseline; verified reads in assembled synthetic ZIP incl unknown/tampered topics and no record access, JSON/text forms, existing folder fresh lookup followed by deferred submit/recovery. Distinguish deterministic CLI/fixture evidence from observation of an actual fresh agent if unavailable. Record changed risks, reuse credential/OS evidence, compare archive changes to accepted inputs before signing. Existing complete removal candidate remains P2.

### Reviewer response

# Verdict: CONDITIONAL

The plan's direction is sound. It keeps the fixed-inventory verified read, never accepts caller filenames, avoids record access, treats a refused lookup as distinct from empty Work, preserves the no-Work, authorization and Git rules, and separates CLI evidence from fresh-agent observation. The gaps below are specification holes that should be closed before implementation or signing. None of them requires a redesign.

## Findings

**C1: Assembly and manifest scope is implied, not stated (P1)**
- The plan does not say that bundle assembly and the slot manifest change.
- State that every topic document is a fixed inventory entry with size and digest in the manifest, and is added by assembly.
- If a mapped topic's entry is missing, the read must fail closed with a distinct error. It must not fall back to the default.
- Add synthetic ZIP cases for:
  - a tampered topic document
  - a missing topic document
  - a topic document that is present but unlisted

**C2: Topic argument contract is undefined (P1)**
- Specify the exact grammar:
  - the allowed words
  - case handling
  - whether only one topic or several are allowed
  - how empty, path-like, flag-like or extra arguments are treated
- Unknown or invalid input should produce a deterministic, non-zero, fixed error in both JSON and text forms. It should list the valid topics and echo no file paths.
- State whether the JSON shape is unchanged or additive, for example a topic or document identifier. Old parsers must still accept bare-guide output byte-shape-compatibly.

**C3: Launcher and bundle version skew (P1)**
- A new default guide may tell the agent to run `guide <topic>`. On an older launcher that can't serve topics, that command fails, and the agent could improvise or skip a binding step.
- Two options:
  - Make the default say what to do if a topic call errors: stop and report, and never proceed to mutation.
  - Or gate topic references on a capability the launcher reports.
- Test both skew pairs:
  - an old launcher with a new bundle
  - a new launcher with an old slot that has no topic entries

**C4: The "before mutation" routing needs an explicit gate in the default (P1)**
- It is not enough for the default to *mention* the Git and notification topics.
- Before any mutation, the default must require the agent to identify whether the workflow involves Git, notifications or management. If it does, the agent must read that topic first.
- The Git topic must match the merged pre-Git credential gate exactly and reuse its wording.
- Add a check that no topic document grants or implies Git approval, and that the default restates "no implicit Git approval" itself rather than only linking to it.

**C5: Retention proof method (P1)**
- "All old substantive instructions retained" needs an artifact: a mapping of each binding clause in the 365-line baseline to its new location (default or a specific topic).
- Binding wording should be verbatim and checked mechanically, for example with a fixture diff of quoted clauses.
- Clauses needed before the first mutation must live in the default, not only in a topic. This covers:
  - no-Work small edits
  - plan content and authorization
  - exact acceptance
  - the refused-versus-empty lookup distinction
  - pagination
  - handling of unknown or ambiguous cases
- Avoid duplicating binding text across topics unless the duplicates are checked for identity.

**C6: Compatibility of old connected entry text (P2)**
- Old folders' entry text may refer to content that now moves out of the default, such as section names or "the guide says…".
- Verify each such reference still resolves in the new default, or is covered by an explicit pointer there.
- The fresh-lookup-then-deferred-submit or recovery test should use the *unchanged* old entry text.

**C7: Define "concise" (P2)**
- Set a line or byte budget for the default and report it next to the 365-line baseline.
- Otherwise "concise default versus baseline" cannot fail.

**C8: Signing comparison scope (P2)**
- The pre-signing comparison against accepted inputs should list:
  - each added inventory entry and its digest
  - the manifest diff
  - confirmation that no other archive members changed
- Reused credential and OS evidence should be cited by its identifier and scope. Note where the change could invalidate it; launcher argument parsing is the likely place.

**C9: Evidence labeling (P2)**
- This is already planned; make it explicit in the record.
- If no fresh-agent observation happens, the routing claims stay "fixture-verified only". Mark that as a residual risk for the Preview rather than treating it as closed.

## Unchanged

The existing complete removal candidate stays at P2 and is not affected by this plan.

## Conditions to reach PASS

- Specify C1 through C5 in the plan.
- Add the listed synthetic ZIP and skew tests to the verification list.

## Driver disposition and proposed implementation

- C1, C2 accept. Keep bare guide and its JSON object. Provide exactly one optional lowercase topic from a closed list: plan, work, revision, recovery, git, management, execution. Use a shared list of fixed inventory names for the parser/verified reader and assembly. Unknown/malformed topic input must not open a file or echo arbitrary user input. Keep normal help. Missing, unlisted or changed topics fail closed.
- C3, C6 accept. Reuse the unchanged managed project entry block. Check the old bare invocation and rejection of a topic on the old parser, plus new-reader/old-inventory refusal. Require the calling agent to stop a dependent action when the applicable guide cannot be verified. Normal execution uses one pinned slot.
- C4, C5 accept. Retain the binding baseline clauses in topic pages; map old sections to topics and compare moved paragraphs. The short entry must distinguish empty, partial and failed lookups, qualify small edits, use exact scope/acceptance and require applicable guides before changes. Git guard wording stays intact. If a notification is requested, read management before choosing the submission path.
- C7 accept. Target at most 75 lines and 5,000 UTF-8 bytes for the default. Measure actual results independently of wrapping.
- C8, C9 accept. Compare actual package members and digests before signing, allowing only explained differences from the prior release including the already merged credential gate. Note pending release copy in the Git/architecture guides and diagram. Distinguish source, assembled fixture and actual agent observations. Review the result separately. Existing Windows credential and Git evidence remains bounded to its original cases.
- Verification scope: focused CLI/parser and slot integrity tests; synthetic ZIP checks across the three supported targets and a bounded connection/resume scenario; link and prose checks for affected instructions. Expected local work including one static result review: 35–55 minutes, suggested cumulative stop at 75 minutes after implementation approval. Production signing, approval of exact release inputs and publishing are later release operations.

The prior patch release assembly verified 22 guide inputs and required all non-guide inventory rows to equal the predecessor. This release also needs updated product modules. At release preparation, derive the changed payload from the exact accepted source, prove the shipped credential and guide modules match it per platform, and compare every unaffected member and mode against the accepted predecessor. The previous guide-only assembly is not suitable as-is.
