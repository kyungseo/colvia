# Block recognizable credentials before Colvia Git integration

Started on 2026-11-18 from `69a540a3ffec9725bff6aa7753680c0b0e4b0460`. The Owner selected the [P0 intake](git-precommit-credential-check-followup.md) and delegated the handling of unsafe previews and uninspectable files. Source implementation checked locally; Owner acceptance is pending. Pseudonymous copies are a separate candidate.

## Scope and decisions

Screen the immutable accepted postimages and commit message locally before preparing a candidate. Preserve the previous execution guard's decisions. Share its strong token patterns and keep Git-specific literal assignment, reference and text handling separate. Include selected filenames and user-supplied commit metadata. Use only synthetic tests. Known patterns are bounded and cannot classify arbitrary passwords in prose or arbitrary encodings. No new account, OS changes, provider call or hook is required.

Retain Work bytes, unrelated staging, divergent partial-staging refusal, immutable object checks, and recovery of a previously started operation. Refuse new uninspectable content. For deletions and replacements, inspect the previous blob through the bounded read-only Git port. For a protected or uninspectable previous blob, the reviewed output identifies the omission and the deletion or replacement. Keep that exact display and commit bound to the existing receipt. Existing records remain intact. An old candidate needing a different display requires fresh preparation and review.

## Protected project paths

For additions and modifications, screen the exact basename `.env`, `.env.local`, `.env.production` and any `secrets` ancestor in the canonical project-relative path, case-insensitively. Templates outside those directories use the ordinary content check. Deletions withhold the old blob by path, including unstructured contents. Refuse a nonempty byte-identical replacement elsewhere in the same candidate when deleting a protected file. This check does not track arbitrary copies or purge history. Earlier preview formats require compatibility screening before display or apply.

The next path-policy revision adds `.netrc`, `_netrc`, Terraform state and its plain or numeric-timestamp backup suffixes. In `.npmrc`, inspect each assignment to `_authToken`, `_auth`, `_password`, `password`, and inline `key`, including registry-scoped credentials. Permit empty values and whole npm environment references. File paths such as `keyfile` remain shareable. Prepare and apply recheck older receipts, using the new policy to protect old content.

## Review and qualification

The plan review covered durable child input/output, encoded reverse binary patches, filter settings, preview identity, previous candidate compatibility and interrupted operations. Driver incorporated the preimage and output controls, used the existing no-filter write and digest checks, and retained the old record format. Local qualification covers the exact source checkout, synthetic inputs and isolated repositories. Native Windows x64 and ARM64 qualification and Owner acceptance are separate from source verification. No publication decision.

The result review identified ordinary source and schema false positives, missing key shapes, the timing of the workspace check, legacy preview availability, and a file replaced by a directory. The revised implementation checks the live workspace inside the effect lock, exposes a status summary for a historical legacy receipt, and includes new children in the replacement preview. Tests cover environment lookups and source references, schema fields, private-key headers, literal settings, and actual Git trees containing a synthetic old credential.

Local results: 23 final credential and integration checks passed. A separate real-Git tree replacement check passed. Earlier evidence covers 72 Git boundary checks and two bundle checks; these groups overlap. Windows protocol tests used native API doubles on macOS. Before shipping, check one blocked candidate and one credential-removing change with unrelated staging on each native Windows architecture. Retain existing recovery qualification for unaffected boundaries.

Path-policy delta: six focused cases passed, plus one protected-deletion case on the Windows protocol double. Coverage includes exact nested names, case variants and near misses, examples with references and literal credentials, a previously tracked file, opaque-text deletion, an exact same-candidate move, and refusal to redisplay or apply a v1 preview showing old contents. Real Git ran on macOS. No native Windows installation or release was performed for this delta.

Development-config delta: nine distinct focused test methods passed across the initial eight and the post-review checks. Native macOS Git and one Windows protocol-double case covered refusal before object creation, safe deletion, old v2 approval refusal, npm literal-to-reference edits, and exact copies of a removed or replaced sensitive npm blob. Static plan and result review completed. The result review identified the in-place replacement plus copy case; the Driver corrected it and exercised both paths. A comparison with the installed INI reader added regression coverage for key whitespace, BOM and escaped comment delimiters. Personal credentials and native Windows installations were outside these checks.
