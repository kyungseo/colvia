# Record foundation

For the design of project identity, storage, backup, Git integration and updates, start with the [implementation contracts](implementation-contracts.md). For behavior observed on a particular platform or release, start with [product evidence and follow-ups](../product-evidence-and-followups.md#record-foundation-verification). A design requirement and an observed result answer different questions.

| Question | Where to look |
| --- | --- |
| How do the parts fit together? | [Layers and dependencies](structure.md#layers-and-dependencies) assigns responsibilities to modules. The [S1–S11 decision table](structure.md#s1s11-disposition) retains its original Korean wording. |
| What must survive an interruption or a move? | [Storage and recovery](implementation-contracts.md#c3--store-bodies-limits-and-recovery) and the [connection identity check](connection-identity-revalidation.md) describe the boundaries. The [connection-scope proposal](connection-edge-scope.md#first-release-recommendations-and-follow-ups) distinguishes first-release recommendations from follow-ups. Its dated decisions remain in Korean. |
| What did the platform checks cover? | The [regression map](validation.md) distinguishes planned checks from observations. The [runtime and distribution record](runtime-and-extension.md#supply-candidate-and-vm-reuse) gives the supply and candidate conditions. The verification criteria and supply procedure are in English. Dated observations and review inputs retain their original language. |
| Why was a decision made? | The [development task](../FEAT-20261106-002-record-foundation.md) links the dated plans, reviews and checkpoints. Cite the original wording for a decision and the pinned input for a review. |

Use the [repository language conventions](../document-ownership.md#document-language) for new technical text here. Apply the convention by section. Each of the five translated references links to the revision with its original wording. Use the English explanations for navigation and technical reading. The dated decisions, review inputs and observations retain their original authority.
