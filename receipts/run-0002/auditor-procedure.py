#!/usr/bin/env python3
"""Contract-derived blind audit. Imports only the Python standard library."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


CAPSULE = Path(__file__).resolve().parent
TARGET = CAPSULE / "target"
STATE = TARGET / ".harness-v2"
CONTRACT = CAPSULE / "ACCEPTED-CONTRACT.md"
ITEM = "item-0001"
FACETS = {"intent", "lifecycle", "relations", "currentness", "continuation", "evidence", "ownership"}
BASE = {
    "item_id",
    "observed_at",
    "observed_scope",
    "record_id",
    "record_type",
    "schema_generation",
    "unavailable_scope",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def duplicate_reject(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise AssertionError(f"duplicate key: {key}")
        result[key] = value
    return result


def load(path: Path):
    raw = path.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf"), path
    assert raw.endswith(b"\n") and not raw.endswith(b"\n\n") and b"\r" not in raw, path
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=duplicate_reject)
    canonical = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    assert canonical == raw, path
    return value, raw


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=TARGET, check=True, text=True, capture_output=True).stdout.strip()


def main() -> None:
    contract_bytes = CONTRACT.read_bytes()
    payload_bytes = (TARGET / "docs/GENERATION-1-CONTRACT.md").read_bytes()
    assert contract_bytes == payload_bytes
    assert git("status", "--porcelain") == ""
    tracked = set(git("ls-files").splitlines())
    assert ".harness-v2/staging" not in "\n".join(tracked)
    assert not (STATE / "staging").exists()

    authority, _ = load(STATE / "authority.json")
    assert set(authority) == {"authority_home_id", "authority_kind", "created_at", "lineage"}
    assert authority["authority_home_id"] == "7d854f54-6538-4cd4-8961-2e2f50ef9653"
    identity, _ = load(STATE / f"items/{ITEM}/identity.json")
    assert identity["item_id"] == ITEM and identity["schema_generation"] == 1

    records = {}
    type_counts = {}
    item_root = STATE / f"items/{ITEM}"
    selectors = {
        item_root / "identity.json",
        item_root / "active-generation.json",
        item_root / "generations/1/active-pointer.json",
    }
    for path in sorted(item_root.rglob("*.json")):
        if path in selectors:
            continue
        value, raw = load(path)
        if "record_type" not in value:
            continue
        assert BASE <= set(value), path
        assert value["schema_generation"] == 1, path
        assert isinstance(value["observed_scope"], list) and isinstance(value["unavailable_scope"], list), path
        record_id = value["record_id"]
        identity = (value["record_type"], record_id)
        assert identity not in records, identity
        records[identity] = {"path": path, "raw": raw, "value": value}
        type_counts[value["record_type"]] = type_counts.get(value["record_type"], 0) + 1

    def ref(value, expected_type):
        assert isinstance(value, dict) and set(value) == {"id", "sha256"}, value
        record = records[(expected_type, value["id"])]
        assert record["value"]["record_type"] == expected_type, value
        assert digest(record["raw"]) == value["sha256"], value
        return record["value"]

    active_generation, _ = load(item_root / "active-generation.json")
    assert active_generation["generation"] == 1
    ref(active_generation["generation_assertion_ref"], "generation-assertion")

    for record in records.values():
        value = record["value"]
        kind = value["record_type"]
        if kind == "attempt-result":
            ref(value["acceptance_ref"], "acceptance")
        elif kind == "revision":
            ref(value["acceptance_ref"], "acceptance")
            ref(value["attempt_ref"], "attempt-intent")
            assert set(value["facet_refs"]) == FACETS
            for facet, facet_ref in value["facet_refs"].items():
                assertion = ref(facet_ref, "facet-assertion")
                assert assertion["facet"] == facet
            if value["tombstone_ref"] is not None:
                ref(value["tombstone_ref"], "tombstone")
        elif kind == "pointer-assertion":
            ref(value["revision_ref"], "revision")
            if value["prior_pointer_ref"] is not None:
                ref(value["prior_pointer_ref"], "pointer-assertion")

    active, _ = load(item_root / "generations/1/active-pointer.json")
    pointer = ref(active["pointer_assertion_ref"], "pointer-assertion")
    revision = ref(active["revision_ref"], "revision")
    assert pointer["revision_ref"] == active["revision_ref"]
    assert revision["revision_id"] == "revision-0004"
    lifecycle = ref(revision["facet_refs"]["lifecycle"], "facet-assertion")
    continuation = ref(revision["facet_refs"]["continuation"], "facet-assertion")
    assert lifecycle["value"]["state"] == "detached"
    assert continuation["value"]["mode"] == "plain"

    revisions = sorted(record["value"]["revision_id"] for record in records.values() if record["value"]["record_type"] == "revision")
    assert revisions == ["revision-0001", "revision-0002", "revision-0003", "revision-0004"]
    operations = sorted(record["value"]["operation"] for record in records.values() if record["value"]["record_type"] == "attempt-intent")
    assert operations == ["create", "detach", "rollback", "update"]
    assert type_counts == {
        "acceptance": 4,
        "attempt-intent": 4,
        "attempt-result": 4,
        "facet-assertion": 28,
        "generation-assertion": 1,
        "pointer-assertion": 4,
        "revision": 4,
        "tombstone": 1,
    }
    for relative in tracked:
        if relative.startswith(".harness-v2/") or relative == "docs/GENERATION-1-CONTRACT.md":
            assert (TARGET / relative).is_file() and not (TARGET / relative).is_symlink(), relative
    forbidden = {"packs", "adapters", "providers", "src", "tests"}
    assert not any(path.name in forbidden for path in TARGET.rglob("*"))
    commit_messages = git("log", "-5", "--format=%B")
    assert git("rev-list", "--count", "HEAD") == "5"
    assert commit_messages.count("Co-authored-by: Codex <noreply@openai.com>") == 5

    receipt = {
        "artifact_id": "HV2-MPV-BLIND-AUDIT-001",
        "auditor_input": {
            "accepted_contract_sha256": digest(contract_bytes),
            "implementation_source": "not-provided",
            "project_cli": "not-provided",
            "runtime_transcript": "not-provided",
            "target_head": git("rev-parse", "HEAD"),
        },
        "authority_home_id": authority["authority_home_id"],
        "classification": "pass",
        "current_revision_id": revision["revision_id"],
        "git_commit_count": 5,
        "git_status": "clean",
        "lifecycle": lifecycle["value"]["state"],
        "payload_sha256": digest(payload_bytes),
        "plain_continuation": continuation["value"]["mode"],
        "record_count": len(records),
        "staging_observation": "absent-in-fresh-clone-not-used-as-binding-or-cleanup-proof",
        "tool_inventory": ["CPython-stdlib-isolated", "git", "sha256-hashlib"],
        "verdict": "pass",
        "zero_pack_provider": True,
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
