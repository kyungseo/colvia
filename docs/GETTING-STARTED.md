# Getting Started

This guide takes a fresh Git project from no Harness v2 state to one human-accepted intent. It does not require an agent provider,
network service, global install, or user-level agent setting.

Document authority and currentness: [Documentation Index](README.md).

## 1. Check The Prerequisites

You need Git and CPython `3.14.6`. A contribution checkout is the trusted source directory containing `hv2`, `src/hv2ref/`, and
the repository documentation. An installed immutable release is not a contribution source and cannot initialize another project.

Run the source launcher against the fresh Git project:

```sh
./hv2 doctor --target /path/to/project
```

Before initialization, `doctor` reports `classification: uninitialized` and exits `15`; that is the expected pre-init outcome. A
different Python version is `unsupported`, not equivalent support.

## 2. Preview, Then Initialize

Preview has no project-byte mutation:

```sh
./hv2 init --target /path/to/project
```

Apply the exact candidate only after reviewing the target and release reference (ID and SHA-256):

```sh
./hv2 init --target /path/to/project --apply
```

Initialization creates a removable product binding, one project-owned item authority home, and a separate project-owned intent
authority home. It does not infer an existing authority home. If `.harness-v2/` or `.harness-v2-intents/` already exists without a
binding, initialization stops with `HV2-PRODUCT-ATTACH-REQUIRED`.

## 3. Confirm The Current State

```sh
cd /path/to/project
./hv2 status
./hv2 doctor
```

Success is `classification: pass`. The output names the active release reference (ID and SHA-256), authority-home identities, bounded capability
declarations, and the next action. `doctor` is read-only.

## 4. Record The First Intent

Create `intent.json` in the project with a complete, human-authored request:

```json
{
  "acceptance_authority": "PROJECT-LOCAL-ACTOR-001",
  "actor": "PROJECT-LOCAL-ACTOR-001",
  "facets": {
    "acceptance_oracle": {"status": "known", "value": ["the selected task passes its named verification"]},
    "destination": {"status": "known", "value": "this project"},
    "expected_outcome": {"status": "known", "value": ["one exact revision is accepted"]},
    "forbidden_scope": {"status": "known", "value": ["unrelated project files"]},
    "goal": {"status": "known", "value": "record the first bounded task"},
    "scope": {"status": "known", "value": ["one project-local task"]}
  },
  "gaps": [],
  "statements": [
    {"kind": "human-decision", "owner": "PROJECT-LOCAL-ACTOR-001", "text": "The owner will accept or reject the exact revision."}
  ]
}
```

Create a draft:

```sh
./hv2 create-intent-draft \
  --target . \
  --intent-id INTENT-001 \
  --sequence 1 \
  --observed-at 2026-08-23T12:00:00Z \
  --input intent.json
```

`--sequence 1` creates `revision-0001`; later drafts use the next contiguous sequence. `--observed-at` is persisted evidence text,
not a currentness selector. The implementation requires a non-empty value but does not certify the timestamp format.

Review the complete output. Acceptance is a human gate, not an agent self-approval. Use the returned `revision_sha256`:

```sh
./hv2 accept-intent \
  --target . \
  --intent-id INTENT-001 \
  --revision-id revision-0001 \
  --revision-sha256 <returned-sha256> \
  --acceptance-id acceptance-0001 \
  --actor PROJECT-LOCAL-ACTOR-001 \
  --observed-at 2026-08-23T12:01:00Z
```

Verify the selected intent:

```sh
./hv2 verify-intent --target . --intent-id INTENT-001
```

## When To Stop

- An unresolved material gap blocks acceptance. Clarify it; do not hide it with imperative wording.
- A digest, actor, or supersede mismatch is a contradiction. Do not select the newest file by recency.
- `degraded`, `partial`, `incompatible`, `conflict`, `stale`, or `unsupported` is not success. Follow the reported recovery path.
- This first path records accepted intent. It does not claim that an agent completed or finalized the requested project work.
- For provider-null state operation and plain-file recovery, continue with [Manual Operation](MANUAL-OPERATION.md).
