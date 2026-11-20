# Writing the Colvia user guides

These guidelines cover the repository READMEs, `manual/` and the guides shipped with the Colvia Preview. For the language of a particular page, see [Document language](document-ownership.md#document-language).

Write for someone who opened the page to make a decision or do one thing. Lead with the outcome, show a realistic request and explain what the reader gets back. Use a fresh chat, a changed file or a pending decision to show when a project record matters. Give a first-time reader the shortest path to a result. Put prerequisites before commands.

## Page roles

- `README.md` is the English repository introduction; `README.ko.md` is its Korean counterpart. The repository README introduces Colvia, shows a concrete task, then offers a first step. Cover the everyday scope, advanced or optional features, target environments and a link to the limits section, what changes on connection and what is preserved or lost on exit. Describe the human decision and relevant limits where they affect the example. Link to the manual for procedures.
- The first exercise guides the reader through one small project. Installation, updates, recovery and removal have their own page. Explain which changes affect one project and which affect other projects using the same operating-system account’s Colvia installation.
- Put implementation details in the architecture or operations reference. Move earlier exercise identities and results to development records; user pages link there when useful. Keep unfinished release checks and review logs in development records. Separate existing behavior, tested environments and future directions.
- Write English and Korean for their own readers. Keep examples, numbers, conditions, decision authority and destinations equivalent. Use natural language in examples and real commands in command blocks. Label an illustrative exchange instead of presenting it as observed output.

### Examples to consult when revising a guide

Use these pairs when writing new material or editing an existing passage. Choose wording that fits the reader and the record. Keep adding a pair here when it resolves a recurring ambiguity.

| If a draft says | Show the reader | Why |
| --- | --- | --- |
| “Changes were requested” | “The reviewer asked the agent to show the currency next to each amount.” | Name the requester, recipient and requested change when they are known. The reader may be someone other than the original reviewer. |
| “The email draft is scheduled” | “The reviewer accepted revision 2, so the prerequisite for drafting the email is met. Starting the draft is a separate decision.” | Identify the exact result and what its acceptance changes. Starting the draft remains a separate decision. |
| “A proposal is available” | “One proposal is waiting for your review. Ask to see revision 2.” | Give the count, the version and a next action the reader can take in the same chat. Label an illustrated chat reply as an example. |

In Korean, “금액 옆에 통화 단위를 표시해 달라고 요청했습니다” leaves the requester and recipient implicit. When the record supports the roles, use “검토자가 에이전트에게 금액 옆에 통화 단위를 표시해 달라고 요청했습니다.” Use “내가” or “you” for a past decision only when the context establishes who made it. Apply the same distinction in captions, diagram arrows and alt text.

## Conditions and evidence

State the available behavior and what the reader needs to do. Keep conditions that change a decision or action: prerequisites, authority, scope, recovery, destructive effects and known limits. Missing validation does not by itself mean a feature is unsupported; removing a caveat must not broaden a support or behavior claim.

Keep general environments and limits in `manual/en/reference.md#environments` and its Korean counterpart. Other pages link there. Pages for the earlier `.hrn` profile live under `manual/*/earlier-profile/`; the retained installed index is `docs/earlier-profile.md` in source. The `docs/README.md` generator refreshes the earlier-profile anchor links. Repeat a specific condition next to the action it changes, especially before deletion or disconnection. Do not scatter test histories or lists of unmeasured benefits through user flows. Keep necessary technical evidence and citations in the documents whose readers need them; this rule is not a reason to remove evidence from research or technical references.

Keep agent and operator contracts precise. An editorial pass on user guides does not change agent behavior, acceptance authority or the meaning of runtime records.

## Navigation

Use Korean then English at the repository entries and the two manual indexes. Link the alternate language and show the current language as text. Each guide begins with its title and a link back to its own language index. Finish sequential lessons with the next useful action. Reference pages return to the index or link to a related topic. Keep a stable anchor or a forwarding link when a section moves.

For the SQLite Preview, the installed entry is `distribution/foundation-guides/README.md`. The language indexes in the same directory lead to pages from `manual/`. The build’s `guide_sources` defines the installed names. Check language switches and relative links at those destinations. The installation page and platform install scripts are the official HTTPS links allowed in the shipped guides.

The earlier-profile builder uses `distribution/README-installed.md` and preserved copies of the earlier index and agent entries. It maps them to their original installed names. Prepare this inventory through the explicit earlier-profile source process. The public root README and active source docs index stay in the repository.

## Review before delivery

Check both directions: no claim beyond the capability definitions, and no caveat that does not affect the reader’s decision or action. Check links and anchors from the file where readers open them, including installed copies. Check both languages against the capability definitions and current evidence before changing a support claim. Render Mermaid, light and dark SVG, and Korean Markdown emphasis. Keep a public support promise separate from a development build or an isolated observation.

## Check affected guidance

[DR-0008 acceptance and activation](../decisions/DR-0008-development-record-and-documentation-checkpoints.md#acceptance-and-activation) records the accepted scope and effective date of these checks. The table helps identify which guidance and artifacts a change affects. [Maintaining](../MAINTAINING.md#evidence-reuse-and-selection) determines the depth and selection of actual checks by behavior.

Use the rows that match the affected surfaces.

| If the change affects | What to compare |
| --- | --- |
| A source-only explanation or navigation route | Check the changed prose and its rendering. Check equivalent English and Korean instructions for paired pages. For moved pages or sections, check outgoing links at the new location and incoming addresses and anchors from the earlier location. |
| A shipped guide or installed entry | Before freezing the candidate, compare the source with its generated guide, intended installed paths and per-platform packaging map. In each affected ZIP, verify the actual members, bytes and internal link destinations. Use Maintaining to select checks for the affected entry, update, repair or detach consumer. |
| Release-facing guidance | Compare affected instructions and support claims with the release notes and any existing changelog for the same release. Record publication or installation when observed and authorized. |
| A command, permission, recovery or support claim | Compare the implementation or actual help with the applicable evidence. Identify the architecture and build, filesystem and folder type, and command path when they affect the claim. For recovery, confirm the command and location of retained material. |
| A changed host test tool or operator instructions | The maintainer or designated operator checks invocation, byte encoding, approval file permissions, exit codes and log capture against the applicable runbook. |

Use the root `AGENTS.md` and `CLAUDE.md`, the instructions used by the actual project entry, and the installed guide or launcher help when a change affects agents. For people using the project, look at the paired root and manual pages, the documentation index, `CONTRIBUTING`, `SECURITY.md` and the applicable release guidance. Record the relevant surfaces, verified identities and any remaining limits in the owning development or release record. Store private environment details and original failures with the applicable evidence and runbook.
