# General Work Development Slice

Status: development machine CLI with local record writing, worker publication, human baseline refresh and exact worker result application. N4 has recorded bounded synthetic qualification; this is not evidence of actual worker-1 adoption or qualification of later modified release bytes.
The default writer verifies an isolated installed applied binding. Tests may explicitly supply a verifier double. Actual source init and
installed launcher tests exercise intent and Work commands plus update/rollback round trips; exact active repair is available from independent source. Receipt-bound detach and a bounded independent auditor are implemented; actual worker-1 adoption remains unverified.
Only explicit source-checkout and installed single-home entry modes remain. Generation runtime, readers and commands are removed.

`work.py` observes the whole project independently of an individual Work's exact file scope. Git snapshots include tracked files
(including ignored tracked files) and non-ignored untracked files. Missing tracked files are absent from the snapshot and explicit
in a result diff. Non-Git snapshots include all regular files. The root metadata directories and a caller-verified managed launcher
are excluded. Symlinks, special files, case aliases, nested repositories/authorities and unresolved index entries fail closed,
including unsupported objects inside ignored directories. This strict scan can be expensive in large generated trees; cost is not measured yet.

The ignore fingerprint hashes project ignore contents, common-directory info/exclude and effective global ignore contents with stable
labels, never absolute machine paths. Ignore files inside a parent-excluded directory do not change the fingerprint. Noncanonical `.GITIGNORE` spelling is unsupported.
External global-ignore symlinks resolve to regular contents; project symlinks remain unsupported. A new self-ignoring cache whose
parent was not excluded can change effective policy and is explicitly non-pass.

Policy-changing results, including `.gitignore` edits, are unsupported in this slice. Preserve the change for separate human policy
review; do not silently establish a baseline and call the change accepted. An accepted project decision outside the Work writer must
precede a new baseline. That review is not implemented or automated here, and no new Core approval record is added. Two observations must agree; this detects ordinary drift
but does not promise a filesystem transaction or stop an outside writer. HEAD-only commits do not change content freshness.

Manifests bind complete sorted before/after trees and exact changes. They reject extra fields, boolean integers, bad digests,
case aliases, out-of-scope changes and incomplete worker provenance. Named Git refs are existing project-owned retention references;
the product neither creates nor manages refs. Exact ref names are required (no DWIM fallback), Git replacement objects are disabled,
and promisor/partial clones or alternate object stores are explicitly unsupported. Every content Git command disables lazy fetching;
refusing configured remote-object dependencies also covers Git versions that ignore that environment setting. Worker source verification checks retained-ref reachability, base-to-candidate ancestry, the exact whole tracked diff and all project commit paths/blob bytes/modes, including unchanged paths. Managed launcher exclusion requires the control-verified digest in both commits. It does not apply patches, move HEAD, refresh the index or create an acceptance decision.

Recovery observation distinguishes full result, mixed pre/post, unknown changed content and outside drift. The content-only
`all_changed_paths_pre` observation cannot authorize cancellation: actual ignored occupants and safe ancestors must also pass
`preflight_changed_paths`. Record graph, human authority, current intent, active executing release, document/evidence references
and pending exclusivity must still be verified under the shared guard. No current observation is a completion record.

The local writer enumerates all Work records, derives completed only from a selected accepted revision, and supports exact complete-file
crash-prefix replay, local cancellation, rework, human rebind and revoke. A new-format intent graph and internal writer verify accepted draft/selection
bindings. The installed serial CLI uses WorkspaceIntentStore and WorkStore. Integration tests create and accept intents,
then complete and rebind Work through these stores. Worker application requires the exact human acceptance ticket and retained Git sources. The installed verifier callback must be read-only and verify
actual loaded-release provenance; there is no permissive default. Required external references and full content are rechecked before publication. Installed lifecycle and machine confirmation are implemented; read-only human view/confirmation and a manual narrative-review adapter are implemented development candidates; human comprehension remains unvalidated. Thread tests alone do not establish multi-process usefulness or power-loss behavior.

The record writer rejects checkpoint/rework baselines that differ from the preceding selected result, including outside-scope drift.
A checkpoint does not approve the preceding result. Rework after a rejected result retains that historical result as its next baseline;
the human view shows the initial baseline, rejected submissions, checkpoint/rework history and human rebind baseline changes,
not only the last manifest diff. The final confirmation always binds the full result tree. Manifest views expose metadata; they do not reconstruct historical content bytes.
Ignore-policy changes are refused across every existing Work revision; a human rebind does not bypass this restriction.
Human rebind can explicitly select a different content baseline for a newly accepted intent, under the same acceptance authority.
The first pilot must enforce one editing Work procedurally throughout the serial pilot; this API does not enforce
which process may edit ordinary project files.

Human reject/revoke/cancel grant no new result authority and never change project bytes. They verify the historical intent graph and
identity but allow stale live documents and a newer current intent. Accept/rebind still require current intent, references and full content.
A pending agent selection prevents a second human decision before any decision bytes are written. Apply also validates the planned
selection together with the decision before publication. A historical exact replay does not move current or redo a result.

New Work identity publication and current-selector replacement use same-filesystem staging beneath the existing `.hrn/staging/`.
A killed process can leave preserved staging debris without invalidating authoritative Work records. Complete identity/manifest/revision/
selection/current prefixes are tested; torn immutable record bytes still fail closed and require explicit manual preservation/recovery.
The reader validates every Work revision's actual historical intent acceptance, not merely the shape of the reference.
A durable selection whose result has drifted, or a pending rebind whose baseline has drifted, still requires exact restoration;
there is no generalized cancellation of published selections. Unrecoverable original bytes remain a visible blocked operation.

The internal intent writer publishes drafts without granting authority, binds acceptance to the complete confirmation ticket, and selects
only the exactly accepted draft. All drafts within one intent retain the same acceptance authority. A later draft can resolve a material gap;
an unresolved material gap cannot be accepted. Draft and acceptance IDs cannot be reused for different bytes.
Any pending Work decision or selection blocks new intent mutation. Any pending intent acceptance or selection blocks new Work mutations
and other intent mutations. Exact immutable draft replay and already-published acceptance replay do not move current. Staging publication
keeps temporary identity/current bytes outside intent homes. Interrupted acceptance requires the same binding and required reference bytes;
restoring those exact prerequisites is the supported recovery, not deleting or cancelling an acceptance record.

New intent drafts retain a single linear predecessor chain. Even with no unresolved gaps, acceptance requires at least one known facet;
an entirely unknown/deferred intent cannot grant Work authority. Sequence types are validated before predecessor arithmetic. Historical
completed Work replay is read-only and remains available during unrelated intent publication. Update/rollback blocks binding changes for either pending Work or pending intent. The exact lifecycle
plan also binds every current truth file; preview drift requires a new preview, and a pending lifecycle
requires its original exact prerequisites. Exact repair and receipt-bound detach are described below.


### Default runtime gate

`WorkStore(target)` and `WorkspaceIntentStore(target)` now default to the installed
applied-lifecycle verifier. Source execution fails that gate. Tests may still pass an
explicit verifier double. The new installed machine CLI calls these writers. Installation-shaped runtime
fixtures remain narrower evidence than the separate actual init and CLI tests.


## Installed Machine Commands (Development)

The isolated installed launcher exposes `hv2 intent draft|prepare|apply` and
`hv2 work publish|prepare|apply`. Each accepts canonical JSON from `--input PATH`
or stdin (the default). `apply` also requires `--confirm TOKEN`. Prepare returns
`ticket` and `confirm_token`; apply consumes only that exact ticket object.
This is an agent/programmatic interface, separate from the read-only human view/adapter.

Intent draft input is a full typed draft. Intent prepare requires
`intent_id`, `revision_ref`, `actor`, `reason`, `request_id`, `observed_at`, with optional `document_refs` (omitted means an empty list). Unknown fields are rejected.
Work publish requires `identity`, `revision`, `manifest`, `selection_id`,
`operation_id` (the latter two are null only for a rebind proposal). Work prepare
requires `work_id`, `action`, `actor`, `reason`, `request_id`, `observed_at`,
`revision_ref`, `supersedes`, with explicit null for unused optional references.

Installed `status` and `doctor` are read-only and validate product plus all typed
records. They label pending publication, worker topology and runtime support.
They do not attest fresh project content or acceptance of a later unsubmitted edit.
The runtime version gate accepts final, GIL-enabled CPython 3.14.6 or 3.14.7. Unknown/partial roots never
return a successful status code. A broken launcher needs independent source
inspection; the installed entry cannot repair its own missing binding.

Installed startup never guesses source-checkout mode when `.hrn` is missing. Invoke an independent
trusted source launcher with `--source-checkout` for init or diagnostic commands. Source init/update/rollback/detach
commands require the explicit `planning-1` profile; repair has no profile option and requires the exact active release, refusing older windows. Removed generation commands are parser errors;
there is no legacy fallback mode.
Confirmation tokens bind request bytes; they are not independent evidence of human authorization.

Update/rollback support preserves typed Work/intent records and project results. A product switch
changes the binding and may change launcher bytes, so existing confirmation tickets become stale
and must be prepared again. A pending product receipt is a planned operation, not a completed switch.
Only exact independent-source recovery can finish a partially published lifecycle.


## Independent Exact Repair

If the launcher or active payload is damaged, invoke a trusted independent source:

```sh
/path/to/exact-source/hv2 --source-checkout repair --target /path/to/project \
  --source /path/to/exact-source --backup /path/to/new-external-backup \
  --operation-id repair-1 --observed-at 2026-01-01T00:00:00Z
/path/to/exact-source/hv2 --source-checkout repair --target /path/to/project \
  --source /path/to/exact-source --apply --input request.json --confirm TOKEN
```

Save the preview's `request` object for the apply input, and use its confirmation
token. The backup directory must be new and outside both project and source. It
stores the exact request, original bytes, and final lifecycle receipt. Keep it in
durable storage until you have reviewed the repair. The tool does not delete it.
No backup registry is written into the authority home.

Repair restores only the active release's exact bytes, including its inventory
and launcher; source must match the bound release digest. It does not change
binding, Work, intent, or project results. Pending Work/intent is allowed, but
pending product switches, damaged metadata, unsafe file kinds, unknown members,
and missing directories require preservation and manual investigation. A stopped
repair can resume with the same input/token and `--recover`; new edits or torn
backup bytes are refused. The installed launcher cannot invoke this operation.


## Detach Without Removing Project Truth

Use the installed `hv2 detach --operation-id detach-1 --observed-at TIME` to
preview. Save its `request` object, then run `hv2 detach --apply --input request.json
--confirm TOKEN`. An independent source can use the same command with explicit
`--source-checkout`, `--profile planning-1`, and `--target /path/to/project`.

Detach writes `.hrn/detached.json` before removing anything. It removes the verified
launcher and managed product files, then their empty directories. Format, ignore
rules, intent, Work, project results and authored documents remain. Unknown bytes,
changed files or pending product/Work/intent publication block a new detach.

After an interruption the launcher may be gone. Use an independent trusted source
with the exact input/token and `--recover`. A receipt with remaining planned files
or directories is `partial`; it becomes `detached` only when removal is complete.
Unknown, changed or out-of-order remnants are preserved for manual investigation.
No recursive deletion is used. Detached projects cannot be reinitialized; attaching
a detached authority is a separate future operation.

An independent source's status/doctor validates the preserved Work/intent graphs.
For a product-free, stdlib-only byte audit, copy `tests/fixtures/product_plain_auditor.py`
from a trusted source before removal (or obtain it independently) and run it with
`python -I -B product_plain_auditor.py /path/to/project`. The auditor verifies the
receipt inventory and selected references; it does not reimplement the whole Work
state machine and never authorizes new mutation. It also supports read-only audit
of a clone; recovery remains bound to the original target fingerprint.

Later patches, prereleases and free-threaded builds are rejected. Other OS or distributor builds matching the accepted version conditions may execute; that is not a claim that they have been qualified. See [Security and Support](SECURITY-AND-SUPPORT.md).


## Observation Limits And Human Acceptance

`observed_scope` and `unavailable_scope` describe what the author observed and could not observe. A nonempty `unavailable_scope` is not itself a degraded graph or an automatic acceptance refusal. An empty array is not proof that acceptance criteria passed. This author-declared field differs from an advisory unavailable reference observation in the view and from an authority read failure such as HV2-WORK-UNAVAILABLE or HV2-INTENT-UNAVAILABLE, which remains degraded and refuses writes. The selected revision digest binds these observations; acceptance copies them into the new selection record. The decision and ticket do not directly contain these arrays.

The human declares important criteria in the accepted intent's acceptance oracle or referenced brief. Before requesting acceptance, the agent maps every unavailable item to those criteria and presents its effect; it must not silently discard or classify an item as unimportant. The human decides whether a limit is outside scope, requires more evidence, or requires a new scope/intent acceptance. Undeclared or unresolved important criteria block the operational acceptance request, even when the CLI could prepare a ticket.

Use existing required document references and required control-required evidence references for conditions that can be checked as accessible bytes/digests. Those guards do not establish a document's truth or semantic completeness. Reader failure, malformed authority, missing/stale required references and result-content mismatch retain their existing refusal behavior; observation prose cannot waive those guards. Most document-quality decisions remain human judgments.

The current confirmation view does not directly list these observation arrays. Before a human decision, present the Work view for the exact selected revision together with its confirmation view, explaining every unavailable item in the human's language. If the revision/selection changes, prepare the paired views and ticket again. Follow the managed adapter for the operating procedure. This is a human review contract, not authentication or a new runtime policy gate.


## Worker Publication Development Checkpoint

Run the control project's installed `./hv2 work publish --worker /path/to/linked-worker --input REQUEST` for an isolated-worktree submit-result. The locator is command input, not a stored registry. The unchanged request fields bind identity, revision, manifest, selection_id and operation_id. The worker must be registered in the same Git common directory, its HEAD must be the retained candidate commit, and its complete observed content must match the committed result. Its copied launcher must match the control-verified bytes. The worker's own launcher cannot mutate control authority.

Start and baseline rebind run on control without --worker. Their manifest base and result are equal, with one current control commit retained by existing refs. A new same-intent worker rebind preserves scope/ignore policy, remains an unselected proposal, and needs the Work acceptance authority's separate rebind prepare/apply. This selects an active baseline and does not accept a result. Local same-intent rebind remains unsupported. A record-only commit does not invalidate an already proposed baseline if content, refs, intent and product remain current.

Submission records review state and leaves control project bytes, HEAD and index unchanged. Control must still match the selected baseline. Required intent documents/evidence must not overlap the worker diff; use a separate output or obtain a human revision of intent boundaries first. A required Work reference changed by the result is checked against the retained post blob; other required references are checked on control. Result acceptance must later recheck these and validate live references after application.

Worker accept prepare checks the pre-image and retained post blobs without applying bytes. Apply records the human decision durably before replacing only the manifest changes; add/delete/executable-mode changes leave HEAD, index and refs unchanged. Completion is selected only after the whole result and required live references match. An interrupted acceptance resumes only remaining pre-images from retained control Git objects, even if the worker directory is unavailable. Neither images, unsafe occupants, changed ignore policy or outside drift block recovery and preserve bytes. An open accept with no durable selection can instead be explicitly rejected only while every changed path is still pre; outside drift and stale intent do not grant new authority and do not prevent that cancellation. Mixed application cannot be cancelled. A durable result selection is never repaired by reapplying content. Historical completed replay is read-only. Human worker baseline rebind uses the existing D→S→current publication with repeated live/ref checks and exact recovery; it has no new cancellation path. Preserve changed bytes before restoring prerequisites and replaying the same ticket. A passing submission fixture alone is not qualification for real parallel adoption, multi-process races or final result integration. Separate bounded N4 process/integration evidence is summarized in [Security and Support](SECURITY-AND-SUPPORT.md); real worker use remains unverified.


## Worker Review Observations

The read-only view separates the retained base/candidate from current control content. Before acceptance, whole_base_matches can be true while whole_result_matches is false; this is the expected pre-application state. A changed reference is shown against the retained candidate with its separate control observation. A missing/deleted/oversized/unverified candidate reference stays unavailable or stale. Worker-observed evidence remains unverified on control. The advisory reference limit remains 4 MiB.

Confirmation observations distinguish a new acceptance, pending D recovery, a durable result selection, baseline refresh and all-pre cancellation. They do not provide an aggregate permission to apply. Reject/revoke do not require current document agreement; cancelling a worker accept still needs safe all-pre occupants and no durable result selection. The graph and apply enforce those conditions independently.

A worker rebind view compares previous baseline to proposed baseline and, when present, previous submitted candidate to proposed baseline. It lists matches to currently completed Works' changed-path post entries, with exact revision/decision references. Content equality does not prove cause, timing or attribution. In-scope changes with unproven origin remain explicit even when a matching completed entry exists. The decision selects a baseline only, never a completed result. Read the current adapter for the human-language explanation; the project Work narrative remains primary.

## Direct-Child Umbrella

The umbrella-1 candidate adds a bounded parent acceptance contract. Ordinary intent drafts and Work revisions keep schema1 and their existing inputs. Only a parent draft uses schema2 with `composition`; only its Work revisions use schema2 with `umbrella_evidence`. Every version has exact keys. Identity, ticket, decision, selection, current and manifest remain version1. This is a development contract; use the exact candidate's validation receipt before deployment.

Composition has `parent` (qualified Work identity) and a nonempty `required_children` array of `{work, intent}` qualified identities. All are in one home. Sort by Work ID UTF-8 bytes; reject aliases, duplicates, self references and nested umbrella children. Child revisions must declare exactly the intended parent relation. Required membership does not add reverse dependency edges or a scheduler. A dropped completed child's historical parent relation can remain.

Each evidence child row contains `work`, exact `intent_ref`, and `selection_ref`, `revision_ref`, `decision_ref`, `manifest_ref`. Presence of digests is insufficient: the selected accept ticket, result and current accepted child intent must identify the same chain. Child A's historical complete-tree snapshot need not equal today's tree after child B edits the same file.

Start/rebind capture currently eligible completed children and use `integration_document=null`; an empty or partial initial capture is permitted. The same guarded publication checks both control content and child references. Checkpoint/rework retain those children. Submit-result copies the selected baseline children exactly, covers every required child, and names an integration document. Changed child results require human rebind/baseline refresh before verification and resubmission. The usual worker mode supports same-intent human baseline refresh; local mode still requires a new accepted intent for rebind.

The integration path must be a required `document_refs` entry with role=result. At least one required `evidence_refs` entry must be control-required. One project-authored report may serve both roles. Bind the real verification command, inputs, child snapshot, result and limits in that report; references and hashes do not prove that an oracle actually ran or that its claims are true. Core verifies chains and bytes, while the human judges the result.

An accepted parent intent cannot remove composition or change parent identity. A selected parent Work cannot rebind to ordinary intent or downgrade to schema1. Unaccepted orphan drafts do not establish a role. Replanning changes parent intent acceptance and human Work rebind; unchanged children need no new acceptance merely because the required set changed.

Publish/prepare/apply share the predicate. Apply checks again before decision, selection and current publication. Pending parent decision/selection blocks other control Work writes in both local and worker modes. Exact retry and supported cancellation remain available; there is no new per-child lock, lease or quarantine. Reject/revoke do not require current child readiness. A durable accept selection cannot be cancelled; restore exact prerequisites and resume. Corrupt external edits fail closed and require separately authorized exact restoration, never record deletion or force unlock.

Historical chain validation is separate from today's readiness. A later child revision/revoke does not undo a completed parent. `view work ID` shows declared identities, captured/submitted/current references, first selected capture and unmet reasons in a dedicated review section. Before first capture, change timing is unknown. A view observation does not accept the parent or waive content, runtime, authority or required-reference checks.


## Umbrella Input Protection

A parent worker result must not rewrite a required document or evidence input bound to a captured child intent. The same preflight protection already applies to the parent intent. Overlap is refused before result publication or content application; use a separate output, or have the human revise the affected intent and refresh the Work baseline. Required child current/live checks remain in force through publication. This restriction does not prevent children from successively modifying the same output file when it is not such a required intent input.

Writer validation is fail-closed for the authority home: existing Work relation and pending-intent checks already read across that home, and umbrella records add historical child-reference validation. A damaged unrelated authority record can therefore block an ordinary writer. This is not a per-Work isolation guarantee, and no new index or separate synchronization document is required.
