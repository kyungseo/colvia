#!/usr/bin/env python3
"""Generation 1 blind audit using only sealed inputs and the Python standard library."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


if not __debug__:
    raise SystemExit("HV2-AUDIT-OPTIMIZED-MODE-FORBIDDEN")


CAPSULE = Path(__file__).resolve().parent
TARGET = CAPSULE / "target"
STATE = TARGET / ".harness-v2"
CONTRACT = CAPSULE / "ACCEPTED-CONTRACT.md"
EXPECTED_PATH = CAPSULE / "EXPECTED.json"
STAGING_AUDIT_PATH = CAPSULE / "STAGING-AUDIT.json"
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


class AuditError(Exception):
    pass


def require(condition: bool, code: str, detail: object = "") -> None:
    if not condition:
        raise AuditError(f"{code}: {detail}")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def duplicate_reject(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "HV2-AUDIT-DUPLICATE-KEY", key)
        result[key] = value
    return result


def reject_constant(value: str):
    raise AuditError(f"HV2-AUDIT-NONFINITE: {value}")


def load(path: Path):
    raw = path.read_bytes()
    require(len(raw) <= 4 * 1024 * 1024, "HV2-AUDIT-JSON-LIMIT", path)
    require(not raw.startswith(b"\xef\xbb\xbf"), "HV2-AUDIT-BOM", path)
    require(raw.endswith(b"\n") and not raw.endswith(b"\n\n") and b"\r" not in raw, "HV2-AUDIT-EOF", path)
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=duplicate_reject, parse_constant=reject_constant)
        canonical = (
            json.dumps(value, allow_nan=False, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
    except (RecursionError, UnicodeError, ValueError) as exc:
        raise AuditError(f"HV2-AUDIT-JSON: {path}:{type(exc).__name__}") from exc
    require(canonical == raw, "HV2-AUDIT-NONCANONICAL", path)
    return value, raw


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=TARGET, check=True, text=True, capture_output=True).stdout.strip()


def main() -> int:
    expected, expected_bytes = load(EXPECTED_PATH)
    staging_audit, staging_audit_bytes = load(STAGING_AUDIT_PATH)
    item_id = expected["item_id"]
    item_root = STATE / f"items/{item_id}"
    contract_bytes = CONTRACT.read_bytes()
    payload_path = TARGET / expected["payload_path"]
    payload_bytes = payload_path.read_bytes()

    require(digest(staging_audit_bytes) == expected["staging_audit_sha256"], "HV2-AUDIT-STAGING-SEAL")
    require(staging_audit["classification"] == "sealed-live-target-input", "HV2-AUDIT-STAGING-CLASS")
    require(staging_audit["damaged_count"] == 0, "HV2-AUDIT-STAGING-DAMAGED")
    require(digest(contract_bytes) == expected["accepted_contract_sha256"], "HV2-AUDIT-CONTRACT")
    require(digest(payload_bytes) == expected["payload_sha256"], "HV2-AUDIT-PAYLOAD")
    require(contract_bytes == payload_bytes, "HV2-AUDIT-CONTRACT-PAYLOAD")
    require(git("status", "--porcelain") == "", "HV2-AUDIT-GIT-DIRTY")
    require(git("remote") == "", "HV2-AUDIT-GIT-REMOTE")

    tracked = set(git("ls-files").splitlines())
    require(not any(path.startswith(".harness-v2/staging/") for path in tracked), "HV2-AUDIT-STAGING-TRACKED")
    require(not (STATE / "staging").exists(), "HV2-AUDIT-CLONE-STAGING-PRESENT")

    authority, _ = load(STATE / "authority.json")
    identity, _ = load(item_root / "identity.json")
    active_generation, _ = load(item_root / "active-generation.json")
    active, _ = load(item_root / "generations/1/active-pointer.json")
    require(authority["authority_home_id"] == expected["authority_home_id"], "HV2-AUDIT-AUTHORITY")
    require(identity["item_id"] == item_id and identity["schema_generation"] == 1, "HV2-AUDIT-ITEM")
    require(active_generation["generation"] == 1, "HV2-AUDIT-GENERATION")

    selectors = {
        item_root / "identity.json",
        item_root / "active-generation.json",
        item_root / "generations/1/active-pointer.json",
    }
    records = {}
    type_counts = {}
    for path in sorted(item_root.rglob("*.json")):
        if path in selectors:
            continue
        value, raw = load(path)
        require(isinstance(value.get("record_type"), str), "HV2-AUDIT-JSON-ROLE", path)
        require(BASE <= set(value), "HV2-AUDIT-BASE", path)
        require(value["schema_generation"] == 1, "HV2-AUDIT-SCHEMA", path)
        require(value["item_id"] == item_id, "HV2-AUDIT-RECORD-ITEM", path)
        require(isinstance(value["observed_scope"], list), "HV2-AUDIT-SCOPE", path)
        require(value["unavailable_scope"] == [], "HV2-AUDIT-UNAVAILABLE", path)
        record_identity = (value["record_type"], value["record_id"])
        require(record_identity not in records, "HV2-AUDIT-RECORD-REUSE", record_identity)
        records[record_identity] = {"path": path, "raw": raw, "value": value}
        type_counts[value["record_type"]] = type_counts.get(value["record_type"], 0) + 1

    expected_tracked = {
        ".harness-v2/.gitignore",
        ".harness-v2/authority.json",
        "README.md",
        expected["payload_path"],
        *(path.relative_to(TARGET).as_posix() for path in selectors),
        *(record["path"].relative_to(TARGET).as_posix() for record in records.values()),
    }
    require(tracked == expected_tracked, "HV2-AUDIT-TREE-COVERAGE", sorted(tracked ^ expected_tracked))

    def ref(value, expected_type):
        require(isinstance(value, dict) and set(value) == {"id", "sha256"}, "HV2-AUDIT-REF-SHAPE", value)
        require(re.fullmatch(r"[0-9a-f]{64}", value["sha256"]) is not None, "HV2-AUDIT-REF-DIGEST-SHAPE", value)
        record = records.get((expected_type, value["id"]))
        require(record is not None, "HV2-AUDIT-REF-MISSING", value)
        require(digest(record["raw"]) == value["sha256"], "HV2-AUDIT-REF-DIGEST", value)
        return record["value"]

    generation = ref(active_generation["generation_assertion_ref"], "generation-assertion")
    require(generation["generation"] == 1 and generation["state"] == "active", "HV2-AUDIT-GENERATION-ASSERTION")

    pointers = {}
    revisions = {}
    bindings = {}
    releases = {}
    operations = []
    for record in records.values():
        value = record["value"]
        kind = value["record_type"]
        if kind == "attempt-result":
            acceptance = ref(value["acceptance_ref"], "acceptance")
            require(acceptance["accepted"] is True and value["outcome"] == "validated", "HV2-AUDIT-OUTCOME", value["record_id"])
            require(
                acceptance["attempt_id"] == value["attempt_id"]
                and acceptance["proposal_inventory_sha256"] == value["proposal_inventory_sha256"],
                "HV2-AUDIT-PROPOSAL",
                value["record_id"],
            )
        elif kind == "revision":
            acceptance = ref(value["acceptance_ref"], "acceptance")
            result = ref(value["result_ref"], "attempt-result")
            intent = ref(value["attempt_ref"], "attempt-intent")
            require(result["acceptance_ref"] == value["acceptance_ref"], "HV2-AUDIT-REVISION-RESULT", value["record_id"])
            require(
                intent["attempt_id"] == acceptance["attempt_id"] == result["attempt_id"]
                and intent["requested_revision_id"] == value["revision_id"]
                and intent["operation"] == value["operation"],
                "HV2-AUDIT-ATTEMPT",
                value["record_id"],
            )
            require(set(value["facet_refs"]) == FACETS, "HV2-AUDIT-FACETS", value["record_id"])
            for facet, facet_ref in value["facet_refs"].items():
                assertion = ref(facet_ref, "facet-assertion")
                require(assertion["facet"] == facet and isinstance(assertion["value"], dict), "HV2-AUDIT-FACET", facet)
            if value["tombstone_ref"] is not None:
                ref(value["tombstone_ref"], "tombstone")
            revisions[value["revision_id"]] = value
            operations.append((intent["attempt_id"], value["operation"]))
        elif kind == "pointer-assertion":
            ref(value["revision_ref"], "revision")
            if value["prior_pointer_ref"] is not None:
                ref(value["prior_pointer_ref"], "pointer-assertion")
            pointers[value["pointer_assertion_id"]] = value
        elif kind == "binding-receipt":
            ref(value["revision_ref"], "revision")
            ref(value["result_ref"], "attempt-result")
            require(value["git_state"] == "unfinalized", "HV2-AUDIT-BINDING-GIT", value["record_id"])
            bindings[value["attempt_id"]] = value
        elif kind == "release-binding":
            releases[value["release_id"]] = value
        elif kind == "resume":
            ref(value["revision_ref"], "revision")
            ref(value["pointer_after"], "pointer-assertion")
            if value["pointer_before"] is not None:
                ref(value["pointer_before"], "pointer-assertion")
        elif kind == "interruption":
            require(value["exit_code"] == 75, "HV2-AUDIT-INTERRUPTION", value["record_id"])
            if value["pointer_before"] is not None:
                ref(value["pointer_before"], "pointer-assertion")

    children = {}
    for pointer_id, pointer in pointers.items():
        prior = pointer["prior_pointer_ref"]
        prior_id = None if prior is None else prior["id"]
        children.setdefault(prior_id, []).append(pointer_id)
    require(len(children.get(None, [])) == 1, "HV2-AUDIT-POINTER-ROOT")
    require(all(len(child_ids) == 1 for child_ids in children.values()), "HV2-AUDIT-POINTER-FORK")
    tips = [pointer_id for pointer_id in pointers if pointer_id not in children]
    require(len(tips) == 1 and active["pointer_assertion_ref"]["id"] == tips[0], "HV2-AUDIT-POINTER-TIP")

    active_pointer = ref(active["pointer_assertion_ref"], "pointer-assertion")
    current = ref(active["revision_ref"], "revision")
    require(active_pointer["revision_ref"] == active["revision_ref"], "HV2-AUDIT-ACTIVE-CONTRADICTION")
    lifecycle = ref(current["facet_refs"]["lifecycle"], "facet-assertion")["value"]["state"]
    continuation = ref(current["facet_refs"]["continuation"], "facet-assertion")["value"]["mode"]
    evidence = ref(current["facet_refs"]["evidence"], "facet-assertion")["value"]
    require(evidence["payload_sha256"] == expected["payload_sha256"], "HV2-AUDIT-EVIDENCE-PAYLOAD")

    selected_revisions = {pointer["revision_ref"]["id"] for pointer in pointers.values()}
    for _, operation in operations:
        require(operation in {"create", "update", "rollback", "detach"}, "HV2-AUDIT-OPERATION", operation)
    for revision_id in selected_revisions:
        revision = revisions[revision_id]
        intent = ref(revision["attempt_ref"], "attempt-intent")
        binding = bindings.get(intent["attempt_id"])
        require(binding is not None and binding["revision_ref"] == _ref_from_record(records[("revision", revision_id)]), "HV2-AUDIT-BINDING", revision_id)
        if revision["operation"] == "create":
            release_ref = intent["release_ref"]
            release = releases.get(release_ref["id"])
            require(release is not None and release["carrier_sha256"] == release_ref["sha256"], "HV2-AUDIT-RELEASE", revision_id)
        if revision["operation"] == "rollback":
            source = intent["rollback_source_ref"]
            require(source["id"] in selected_revisions, "HV2-AUDIT-ROLLBACK", revision_id)

    require(sorted(revisions) == expected["revision_ids"], "HV2-AUDIT-REVISION-ORACLE", sorted(revisions))
    require([operation for _, operation in sorted(operations)] == expected["operations"], "HV2-AUDIT-OPERATION-ORACLE")
    require(type_counts == expected["record_type_counts"], "HV2-AUDIT-COUNT-ORACLE", type_counts)
    require(current["revision_id"] == expected["current_revision_id"], "HV2-AUDIT-CURRENT")
    require(lifecycle == expected["lifecycle"] and continuation == expected["continuation"], "HV2-AUDIT-CONTINUATION")
    require(git("rev-list", "--count", "HEAD") == str(expected["git_commit_count"]), "HV2-AUDIT-GIT-COUNT")
    require(git("rev-parse", "HEAD") == expected["target_head"], "HV2-AUDIT-GIT-HEAD")
    require(git("rev-parse", "HEAD^{tree}") == expected["target_tree"], "HV2-AUDIT-GIT-TREE")

    receipt = {
        "artifact_id": expected["audit_artifact_id"],
        "auditor_input": {
            "accepted_contract_sha256": digest(contract_bytes),
            "expected_sha256": digest(expected_bytes),
            "staging_audit_sha256": digest(staging_audit_bytes),
            "target_head": expected["target_head"],
        },
        "authority_home_id": authority["authority_home_id"],
        "classification": "pass",
        "current_revision_id": current["revision_id"],
        "git_commit_count": expected["git_commit_count"],
        "git_status": "clean",
        "git_tree": expected["target_tree"],
        "lifecycle": lifecycle,
        "payload_sha256": digest(payload_bytes),
        "plain_continuation": continuation,
        "record_count": len(records),
        "staging_observation": "sealed-live-target-input-verified-separately",
        "tool_inventory": [f"CPython-{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}-stdlib-isolated", "git", "sha256-hashlib"],
        "verdict": "pass",
        "zero_pack_provider": True,
    }
    print(json.dumps(receipt, allow_nan=False, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _ref_from_record(record):
    return {"id": record["value"]["record_id"], "sha256": digest(record["raw"])}


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        print(json.dumps({"classification": "fail", "code": "HV2-AUDIT-FAIL", "message": str(exc)}, sort_keys=True))
        raise SystemExit(1) from None
