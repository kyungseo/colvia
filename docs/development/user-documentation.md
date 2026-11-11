# Writing the Colvia user guides

These guidelines cover repository READMEs, `manual/` and the user sections of `docs/README.md`.

Write for someone who opened the page to make a decision or do one thing. Lead with the outcome, show a realistic request and explain what the reader gets back. Use a fresh chat, a changed file or a pending decision to show when a project record matters. Give a first-time reader the shortest path to a result. Put prerequisites before commands.

## Page roles

- `README.md` is the English repository introduction; `README.ko.md` is its Korean counterpart. The repository README introduces Colvia, shows a concrete task, then offers a first step. Cover the everyday scope, advanced or optional features, target environments and a link to the limits section, what changes on connection and what is preserved or lost on exit. Describe the human decision and relevant limits where they affect the example. Link to the manual for procedures.
- The first exercise guides the reader through one small project. Installation, updates, recovery and removal have their own page. Explain which changes affect one project and which affect other projects on the same device.
- Put implementation details in the architecture or operations reference. Move earlier exercise identities and results to development records; user pages link there when useful. Keep unfinished release checks and review logs in development records. Separate existing behavior, tested environments and future directions.
- Write English and Korean for their own readers. Keep examples, numbers, conditions, decision authority and destinations equivalent. Use natural language in examples and real commands in command blocks. Label an illustrative exchange instead of presenting it as observed output.

## Conditions and evidence

State the available behavior and what the reader needs to do. Keep conditions that change a decision or action: prerequisites, authority, scope, recovery, destructive effects and known limits. Missing validation does not by itself mean a feature is unsupported; removing a caveat must not broaden a support or behavior claim.

Keep general environments and limits in `manual/en/work-guide.md#limits-en` and its Korean counterpart `#limits-ko`, which also generate the installed chapters. Other pages link there. Repeat a specific condition next to the action it changes, especially before deletion or disconnection. Do not scatter test histories or lists of unmeasured benefits through user flows. Keep necessary technical evidence and citations in the documents whose readers need them; this rule is not a reason to remove evidence from research or technical references.

Keep agent and operator contracts precise. An editorial pass on user guides does not change agent behavior, acceptance authority or the meaning of runtime records.

## Navigation

Use Korean then English at the repository entries and the two manual indexes. Link the alternate language and show the current language as text. Each guide begins with its title and a link back to its own language index. Finish sequential lessons with the next useful action. Reference pages return to the index or link to a related topic. Keep a stable anchor or a forwarding link when a section moves.

The installed README is authored in `distribution/README-installed.md` and copied to `README.md` only during explicit source preparation. Its relative links are checked at the installed destination, not beside the source template. Never package the public root README directly. The installed README and documentation index are bilingual in a fixed file inventory. Keep language switches at their entry points. Generate the first exercise, project setup and feature chapters from the repository manuals. Every installed link should resolve inside the distribution.

## Review before delivery

Check both directions: no claim beyond the capability definitions, and no caveat that does not affect the reader’s decision or action. Check links and anchors from the file where readers open them, including installed copies. Check both languages against the capability definitions and current evidence before changing a support claim. Render Mermaid, light and dark SVG, and Korean Markdown emphasis. Keep a public support promise separate from a development build or an isolated observation.
