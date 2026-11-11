# P5–P6 partial result review disposition

Status: four review findings reproduced with synthetic execution/process doubles, then corrected; 49 focused optimized checks pass. This is a source checkpoint, not completion of P5 or installed qualification. The stopped native sandbox lane has not been retried.

The fresh Claude CLI static review used a fixed 49-input packet with no input drift. Its verbatim response, actual model/session identity, original failures and the corrected result remain in the existing private Work evidence. It did not execute tests or authorize effects. Native process closure, concrete model-runtime launch/channel wiring and the P4 reviewed-source lifetime decision remain open.

| Finding | Driver disposition | Correction and evidence |
| --- | --- | --- |
| F1 cancel during write | Accept. | Already-admitted writes wait for bounded result and closure evidence despite a cancel. New admission and document replies remain refused. The synthetic counterexample changed from unknown effect to applied evidence with closure and no reply. Deadline termination remains a possible unknown effect, not a promised rollback. |
| F2 cancellation blocks interrupt | Accept with original deadline retained. | A clean cancellation in the session loop sets stopped rather than protocol-failed. Only metadata interruption can continue; partial/protocol failures stay latched. No deadline extension or new turn is allowed. A cancel inside run now reaches confirmed interruption without a document reply. |
| F3 previously started child | Accept. | Delivery claim checks the execution head inside its publication validation before taking the barrier. A standalone completed run leaves the delivery queued and cancellable rather than permanently owning the project. |
| F4 primary error masked | Accept. | Result-publication errors retain the original exchange failure as their cause; closure still runs. A separate closure failure chains through publication failure. Exception details are not serialized into runtime replies or records. |

The initial 25-check counterexample run had exactly four failures matching these findings. After source correction, the combined controller/session/nested delivery/submission/notice/source-CLI run passed 49 checks, with no input drift. Tests use doubles for process and notice effects. No actual model, installation, OS notification or permission-sensitive retry was performed.

Validation context routing is implemented by the store's validation context variable: selected head reads during validation become tracked CAS expectations. Existing store tests remain applicable. Native exclusive/no-follow primitives retain their earlier source evidence; this reviewer did not independently recheck those omitted modules.

Do not describe a formal run ending revoked or operator-resolved-unknown as a completed document task. Details retain its terminal reason. Runtime resource roots must be verified immutable; preflight hashes alone cannot protect a path replaced between verification and process loading. Actual capability qualification must verify effective permissions/model overrides, not only requested configuration.
