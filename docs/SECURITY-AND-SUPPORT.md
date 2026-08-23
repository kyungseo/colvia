# Security And Support

Document authority and currentness: [Documentation Index](README.md).

## Trust Profile

This D1 candidate is bounded to one trusted local OS account. Actor and finalizer values are logical declarations used for contract
checks; they are not authentication, authorization, signatures, or tenant isolation.

The product layer reads a fixed managed-source path list. It does not scan project files to discover secrets, copy environment files,
or upload content. `status` inspects product binding and named authority files. `doctor` repeats that check and adds runtime identity
and Git availability.

Do not place credentials or secret values in intent, state, evidence, command arguments, receipts, examples, or support packets.
Readable examples and real secret-bearing configuration must remain separate. If a future adapter needs a credential, that adapter
must declare its own admission, storage, access, failure, and removal boundary.

## Control Semantics

The core distinguishes four meanings:

| Meaning | What it promises |
| --- | --- |
| warning | the product reports risk; it does not stop an external action |
| approval | the product requires an explicit user signal such as `--apply` for its own mutation |
| block | the product returns non-zero before its own protected mutation |
| proxy | an external enforcement layer acts and must provide its own evidence |

Text cannot turn a warning into a physical block. The core does not own an execution sandbox or privileged command broker.

## Current Runtime Tuple

| Surface | Current D1 Claim | Fallback |
| --- | --- | --- |
| CPython | `3.14.6`, standard library only | plain read; other versions are `unsupported` until observed |
| Git | local project and caller-owned worktrees/commits | plain files remain readable, but Git-profile operations are unavailable |
| Network | not required by Core operation | none required |
| Agent provider | not required and not certified by this candidate | manual/provider-null path |
| Git host, CI, tracker, knowledge provider | no support claim | manual operation |
| Same-repository parallel work | bounded trusted-local contract | single actor/finalizer |
| Enterprise multi-project operation | unavailable | separate post-Core extension program |

`PRODUCT-CAPABILITIES.json` at the contribution-source root is the machine-readable declaration. After initialization, status reads
the copy under the exact active release and embeds it in the result. File presence alone is not support evidence. A support claim
needs product, version, tier, configuration, observed result, date, and fallback.

## Untrusted Input And Symlinks

Release inventories accept only the fixed relative managed path set. Source files, release files, product roots, and target Git
markers reject symlink substitution at their protected boundary. Root escape, absolute managed paths, unexpected release files,
digest mismatch, and product-tree extras fail closed.

This does not make arbitrary project content safe. Treat external prose, patches, dependencies, and generated artifacts as untrusted
until the project’s own review and execution policy admits them.
