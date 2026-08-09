from __future__ import annotations

import os
import re
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Any

from .carrier import PAYLOAD_PATH, verify_release
from .errors import ContractError, InjectedCrash
from .jsonio import (
    canonical_json_bytes,
    load_json,
    replace_json,
    sha256_bytes,
    sha256_file,
    write_new_bytes,
    write_new_json,
)


FACETS = ("intent", "lifecycle", "relations", "currentness", "continuation", "evidence", "ownership")
OPERATIONS = {"create", "update", "rollback", "detach"}
ITEM_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
BASE_KEYS = {
    "item_id",
    "observed_at",
    "observed_scope",
    "record_id",
    "record_type",
    "schema_generation",
    "unavailable_scope",
}
TYPE_EXTRA_KEYS = {
    "generation-assertion": {"generation", "state"},
    "facet-assertion": {"facet", "value"},
    "acceptance": {"accepted", "actor", "attempt_id", "proposal_inventory_sha256"},
    "attempt-intent": {
        "actor",
        "attempt_id",
        "operation",
        "prior_revision_ref",
        "release_ref",
        "rollback_source_ref",
        "requested_revision_id",
        "target_item_id",
    },
    "attempt-result": {"acceptance_ref", "attempt_id", "outcome", "proposal_inventory_sha256"},
    "revision": {
        "acceptance_ref",
        "attempt_ref",
        "facet_refs",
        "operation",
        "result_ref",
        "revision_id",
        "status",
        "tombstone_ref",
    },
    "pointer-assertion": {"attempt_id", "pointer_assertion_id", "prior_pointer_ref", "revision_ref"},
    "tombstone": {"prior_revision_ref", "reason", "tombstone_id"},
    "interruption": {"attempt_id", "exit_code", "injected_at", "pointer_before"},
    "resume": {"attempt_id", "pointer_after", "pointer_before", "revision_ref"},
    "binding-receipt": {"attempt_id", "git_state", "payload_sha256", "result_ref", "revision_ref"},
    "release-binding": {"carrier_sha256", "inventory_id", "inventory_sha256", "payload_entries", "release_id"},
}


def _ref(record_id: str, data: bytes) -> dict[str, str]:
    return {"id": record_id, "sha256": sha256_bytes(data)}


def _base(record_type: str, record_id: str, item_id: str, observed_at: str) -> dict[str, Any]:
    return {
        "item_id": item_id,
        "observed_at": observed_at,
        "observed_scope": ["target-repository", f"item:{item_id}"],
        "record_id": record_id,
        "record_type": record_type,
        "schema_generation": 1,
        "unavailable_scope": [],
    }


def _write_exact(path: Path, data: bytes) -> None:
    if path.exists() or path.is_symlink():
        if path.is_symlink() or not path.is_file() or path.read_bytes() != data:
            raise ContractError("HV2-IMMUTABLE-CONTRADICTION", str(path))
        return
    write_new_bytes(path, data)


class StateStore:
    def __init__(self, target_root: Path):
        self.target_root = target_root.resolve()
        self.root = self.target_root / ".harness-v2"

    def _item_root(self, item_id: str) -> Path:
        if not isinstance(item_id, str) or ITEM_ID_PATTERN.fullmatch(item_id) is None:
            raise ContractError("HV2-ITEM-ID", repr(item_id))
        return self.root / "items" / item_id

    @staticmethod
    def _validate_operation_sequence(operation: str, sequence: int) -> None:
        if operation not in OPERATIONS:
            raise ContractError("HV2-OPERATION", repr(operation))
        if type(sequence) is not int or not 1 <= sequence <= 9999:
            raise ContractError("HV2-SEQUENCE", repr(sequence))

    def initialize(self, authority_home_id: str, item_id: str, observed_at: str) -> dict[str, Any]:
        if self.root.exists() or self.root.is_symlink():
            raise ContractError("HV2-STABLE-ID-REUSE", str(self.root))
        item_root = self._item_root(item_id)
        authority = {
            "authority_home_id": authority_home_id,
            "authority_kind": "private-reference-target",
            "created_at": observed_at,
            "lineage": [],
        }
        write_new_json(self.root / "authority.json", authority)
        write_new_bytes(self.root / ".gitignore", b"staging/\n")
        identity = {"item_id": item_id, "item_type": "minimum-production-vertical", "lineage": [], "schema_generation": 1}
        write_new_json(item_root / "identity.json", identity)
        generation_id = "generation-assertion-0001"
        generation = _base("generation-assertion", generation_id, item_id, observed_at)
        generation.update({"generation": 1, "state": "active"})
        generation_bytes = canonical_json_bytes(generation)
        write_new_bytes(item_root / "generation-assertions" / f"{generation_id}.json", generation_bytes)
        selector = {
            "generation": 1,
            "generation_assertion_ref": _ref(generation_id, generation_bytes),
            "schema_generation": 1,
        }
        write_new_json(item_root / "active-generation.json", selector)
        return {"authority_home_id": authority_home_id, "generation": 1, "item_id": item_id}

    def _active_pointer(self, item_id: str) -> dict[str, Any] | None:
        path = self._item_root(item_id) / "generations" / "1" / "active-pointer.json"
        return load_json(path, require_canonical=True) if path.exists() else None

    def _record_path(self, item_id: str, record_type: str, record_id: str, facet: str | None = None) -> Path:
        base = self._item_root(item_id) / "generations" / "1"
        if record_type == "facet-assertion":
            if facet is None:
                raise ValueError("facet is required")
            return base / "assertions" / facet / f"{record_id}.json"
        if record_type == "acceptance":
            return base / "acceptances" / f"{record_id}.json"
        if record_type == "attempt-intent":
            return base / "attempts" / record_id.removeprefix("intent-") / "intent.json"
        if record_type == "attempt-result":
            return base / "attempts" / record_id.removeprefix("result-") / "result.json"
        if record_type == "revision":
            return base / "revisions" / f"{record_id}.json"
        if record_type == "pointer-assertion":
            return base / "pointer-assertions" / f"{record_id}.json"
        if record_type == "tombstone":
            return base / "tombstones" / f"{record_id}.json"
        if record_type == "interruption":
            return base / "interruptions" / f"{record_id}.json"
        if record_type == "resume":
            return base / "resumes" / f"{record_id}.json"
        if record_type == "binding-receipt":
            return base / "binding-receipts" / f"{record_id}.json"
        if record_type == "release-binding":
            return base / "release-bindings" / f"{record_id}.json"
        raise ValueError(record_type)

    def _values_for(
        self,
        operation: str,
        sequence: int,
        release: dict[str, Any] | None,
        prior_values: dict[str, Any] | None,
        rollback_values: dict[str, Any] | None,
        rollback_source_ref: dict[str, str] | None,
    ) -> dict[str, Any]:
        if operation == "rollback":
            if rollback_values is None or rollback_source_ref is None:
                raise ContractError("HV2-ROLLBACK-SOURCE", "missing prior accepted values")
            values = {facet: rollback_values[facet] for facet in FACETS}
            values["intent"] = {"operation": "rollback", "sequence": sequence}
            values["currentness"] = {
                "forward_rollback_of": rollback_source_ref,
                "selected_by": "active-pointer",
                "sequence": sequence,
            }
            values["continuation"] = {"mode": "manual-provider-null", "rollback": "forward-only"}
            values["evidence"] = dict(values["evidence"])
            values["evidence"]["sequence"] = sequence
            return values
        common_evidence = dict(prior_values["evidence"]) if prior_values is not None else {}
        common_evidence.update({"production_identity_series": "HV2-PROD-001", "sequence": sequence})
        if release is not None:
            entries = release["payload_entries"]
            if len(entries) != 1 or entries[0]["path"] != PAYLOAD_PATH:
                raise ContractError("HV2-PAYLOAD-CONTRACT", repr(entries))
            common_evidence.update(
                {
                    "carrier_sha256": release["carrier_sha256"],
                    "payload_sha256": entries[0]["sha256"],
                    "release_id": release["release_id"],
                }
            )
        lifecycle = "detached" if operation == "detach" else "active"
        return {
            "intent": {"operation": operation, "sequence": sequence},
            "lifecycle": {"state": lifecycle},
            "relations": {"refs": []},
            "currentness": {"selected_by": "active-pointer", "sequence": sequence},
            "continuation": {"mode": "plain" if operation == "detach" else "manual-provider-null"},
            "evidence": common_evidence,
            "ownership": {"finalizer": "OWNER-LOCAL-001", "writer": "HV2-REPO-IMPL-001"},
        }

    def _load_revision_values(self, item_id: str, revision_id: str) -> tuple[dict[str, Any], dict[str, str]]:
        revision_path = self._record_path(item_id, "revision", revision_id)
        revision = load_json(revision_path, require_canonical=True)
        if revision.get("status") != "completed":
            raise ContractError("HV2-ROLLBACK-SOURCE", f"not-completed:{revision_id}")
        values = {}
        for facet, ref in revision["facet_refs"].items():
            path = self._record_path(item_id, "facet-assertion", ref["id"], facet)
            if sha256_file(path) != ref["sha256"]:
                raise ContractError("HV2-REF-DIGEST", ref["id"])
            values[facet] = load_json(path, require_canonical=True)["value"]
        return values, _ref(revision_id, revision_path.read_bytes())

    def _interrupt(
        self,
        *,
        item_id: str,
        attempt_id: str,
        point: str,
        observed_at: str,
        pointer_before: dict[str, str] | None,
    ) -> None:
        record_id = f"interruption-{attempt_id}-{point.replace('_', '-')}"
        record = _base("interruption", record_id, item_id, observed_at)
        record.update(
            {
                "attempt_id": attempt_id,
                "exit_code": 75,
                "injected_at": point,
                "pointer_before": pointer_before,
            }
        )
        _write_exact(self._record_path(item_id, "interruption", record_id), canonical_json_bytes(record))
        raise InjectedCrash(point)

    def _persist_binding_receipt(
        self,
        *,
        item_id: str,
        attempt_id: str,
        observed_at: str,
        revision_ref: dict[str, str],
        result_ref: dict[str, str],
        payload_sha256: str,
    ) -> None:
        record_id = f"binding-{attempt_id}"
        record = _base("binding-receipt", record_id, item_id, observed_at)
        record.update(
            {
                "attempt_id": attempt_id,
                "git_state": "unfinalized",
                "payload_sha256": payload_sha256,
                "result_ref": result_ref,
                "revision_ref": revision_ref,
            }
        )
        _write_exact(self._record_path(item_id, "binding-receipt", record_id), canonical_json_bytes(record))

    def _land_payload(self, stage_root: Path, expected_sha256: str) -> None:
        staged_payload = stage_root / "project" / "docs" / "GENERATION-1-CONTRACT.md"
        target_payload = self.target_root / "docs" / "GENERATION-1-CONTRACT.md"
        if staged_payload.exists():
            data = staged_payload.read_bytes()
            if sha256_bytes(data) != expected_sha256:
                raise ContractError("HV2-PAYLOAD-DIGEST", "staged")
            _write_exact(target_payload, data)
        if target_payload.is_symlink() or not target_payload.is_file() or sha256_file(target_payload) != expected_sha256:
            raise ContractError("HV2-PAYLOAD-DIGEST", "target")

    def transition(
        self,
        *,
        item_id: str,
        operation: str,
        sequence: int,
        observed_at: str,
        actor: str,
        release_root: Path | None = None,
        rollback_revision: str | None = None,
        inject_at: str | None = None,
    ) -> dict[str, Any]:
        self._validate_operation_sequence(operation, sequence)
        if (operation == "rollback") != (rollback_revision is not None):
            raise ContractError("HV2-ROLLBACK-OPTION", operation)
        if release_root is not None and operation != "create":
            raise ContractError("HV2-RELEASE-OPTION", operation)
        admission = self.verify(item_id)
        if not admission["writable"]:
            raise ContractError("HV2-NONWRITABLE", admission["classification"])
        active = self._active_pointer(item_id)
        if operation == "create" and active is not None:
            raise ContractError("HV2-CREATE-ACTIVE", active["revision_ref"]["id"])
        if operation != "create" and active is None:
            raise ContractError("HV2-NO-ACTIVE", operation)
        if operation == "detach" and admission.get("lifecycle") == "detached":
            raise ContractError("HV2-ALREADY-DETACHED", item_id)
        release = verify_release(release_root) if release_root is not None else None
        authority = load_json(self.root / "authority.json", require_canonical=True)
        if release is not None and release["authority_home_id"] != authority["authority_home_id"]:
            raise ContractError("HV2-AUTHORITY-HOME", release["authority_home_id"])
        if operation == "create" and release is None:
            raise ContractError("HV2-RELEASE-REQUIRED", operation)

        suffix = f"{sequence:04d}"
        attempt_id = f"attempt-{operation}-{suffix}"
        intent_id = f"intent-{attempt_id}"
        result_id = f"result-{attempt_id}"
        acceptance_id = f"acceptance-{operation}-{suffix}"
        revision_id = f"revision-{suffix}"
        pointer_id = f"pointer-assertion-{suffix}"
        item_root = self._item_root(item_id)
        generation_root = item_root / "generations" / "1"
        prior_revision_ref = active["revision_ref"] if active else None
        prior_values = None
        if prior_revision_ref is not None:
            prior_values, _ = self._load_revision_values(item_id, prior_revision_ref["id"])
        rollback_values = None
        rollback_source_ref = None
        if rollback_revision is not None:
            rollback_values, rollback_source_ref = self._load_revision_values(item_id, rollback_revision)
        release_ref = None if release is None else {"id": release["release_id"], "sha256": release["carrier_sha256"]}

        intent = _base("attempt-intent", intent_id, item_id, observed_at)
        intent.update(
            {
                "attempt_id": attempt_id,
                "actor": actor,
                "operation": operation,
                "prior_revision_ref": prior_revision_ref,
                "release_ref": release_ref,
                "rollback_source_ref": rollback_source_ref,
                "requested_revision_id": revision_id,
                "target_item_id": item_id,
            }
        )
        intent_bytes = canonical_json_bytes(intent)
        intent_path = self._record_path(item_id, "attempt-intent", intent_id)
        _write_exact(intent_path, intent_bytes)
        if inject_at == "after_intent":
            self._interrupt(
                item_id=item_id,
                attempt_id=attempt_id,
                point=inject_at,
                observed_at=observed_at,
                pointer_before=None if active is None else active["pointer_assertion_ref"],
            )

        values = self._values_for(operation, sequence, release, prior_values, rollback_values, rollback_source_ref)
        stage_root = self.root / "staging" / attempt_id
        stage_entries = []
        facet_records: list[tuple[str, str, Path, bytes]] = []
        for facet in FACETS:
            assertion_id = f"assertion-{facet}-{suffix}"
            assertion = _base("facet-assertion", assertion_id, item_id, observed_at)
            assertion.update({"facet": facet, "value": values[facet]})
            data = canonical_json_bytes(assertion)
            canonical_path = self._record_path(item_id, "facet-assertion", assertion_id, facet)
            relative = canonical_path.relative_to(self.root).as_posix()
            staged = stage_root / "records" / relative
            _write_exact(staged, data)
            stage_entries.append({"path": f"records/{relative}", "sha256": sha256_bytes(data), "size_bytes": len(data)})
            facet_records.append((facet, assertion_id, canonical_path, data))

        acceptance = _base("acceptance", acceptance_id, item_id, observed_at)
        acceptance.update({"accepted": True, "actor": actor, "attempt_id": attempt_id, "proposal_inventory_sha256": "PENDING"})
        acceptance_path = self._record_path(item_id, "acceptance", acceptance_id)

        facet_refs = {facet: _ref(record_id, data) for facet, record_id, _, data in facet_records}
        tombstone_record = None
        tombstone_ref = None
        if operation == "detach":
            tombstone_id = f"tombstone-{suffix}"
            tombstone = _base("tombstone", tombstone_id, item_id, observed_at)
            tombstone.update({"prior_revision_ref": prior_revision_ref, "reason": "logical-detach", "tombstone_id": tombstone_id})
            tombstone_bytes = canonical_json_bytes(tombstone)
            tombstone_path = self._record_path(item_id, "tombstone", tombstone_id)
            relative = tombstone_path.relative_to(self.root).as_posix()
            staged = stage_root / "records" / relative
            _write_exact(staged, tombstone_bytes)
            stage_entries.append({"path": f"records/{relative}", "sha256": sha256_bytes(tombstone_bytes), "size_bytes": len(tombstone_bytes)})
            tombstone_record = (tombstone_path, tombstone_bytes)
            tombstone_ref = _ref(tombstone_id, tombstone_bytes)

        if operation == "create":
            source_payload = release_root / PAYLOAD_PATH
            payload_data = source_payload.read_bytes()
            staged_payload = stage_root / "project" / "docs" / "GENERATION-1-CONTRACT.md"
            _write_exact(staged_payload, payload_data)
            stage_entries.append(
                {
                    "path": "project/docs/GENERATION-1-CONTRACT.md",
                    "sha256": sha256_bytes(payload_data),
                    "size_bytes": len(payload_data),
                }
            )

        stage_entries.sort(key=lambda entry: entry["path"].encode("utf-8"))
        stage_inventory = {"attempt_id": attempt_id, "entries": stage_entries, "record_type": "staging-inventory", "schema_generation": 1}
        stage_inventory_bytes = canonical_json_bytes(stage_inventory)
        _write_exact(stage_root / "inventory.json", stage_inventory_bytes)
        proposal_sha = sha256_bytes(stage_inventory_bytes)
        if inject_at == "after_stage":
            self._interrupt(
                item_id=item_id,
                attempt_id=attempt_id,
                point=inject_at,
                observed_at=observed_at,
                pointer_before=None if active is None else active["pointer_assertion_ref"],
            )

        acceptance["proposal_inventory_sha256"] = proposal_sha
        acceptance_bytes = canonical_json_bytes(acceptance)
        _write_exact(acceptance_path, acceptance_bytes)
        if inject_at == "after_acceptance":
            self._interrupt(
                item_id=item_id,
                attempt_id=attempt_id,
                point=inject_at,
                observed_at=observed_at,
                pointer_before=None if active is None else active["pointer_assertion_ref"],
            )

        self._verify_stage(stage_root)
        result = _base("attempt-result", result_id, item_id, observed_at)
        result.update(
            {
                "acceptance_ref": _ref(acceptance_id, acceptance_bytes),
                "attempt_id": attempt_id,
                "outcome": "validated",
                "proposal_inventory_sha256": proposal_sha,
            }
        )
        result_bytes = canonical_json_bytes(result)
        result_path = self._record_path(item_id, "attempt-result", result_id)
        _write_exact(result_path, result_bytes)
        if inject_at == "after_result":
            self._interrupt(
                item_id=item_id,
                attempt_id=attempt_id,
                point=inject_at,
                observed_at=observed_at,
                pointer_before=None if active is None else active["pointer_assertion_ref"],
            )

        for _, _, path, data in facet_records:
            _write_exact(path, data)
        if tombstone_record is not None:
            _write_exact(tombstone_record[0], tombstone_record[1])
        if release is not None:
            release_binding_id = f"release-binding-{release['release_id']}"
            release_binding = _base("release-binding", release_binding_id, item_id, observed_at)
            release_binding.update(
                {
                    "carrier_sha256": release["carrier_sha256"],
                    "inventory_id": release["inventory_id"],
                    "inventory_sha256": release["inventory_sha256"],
                    "payload_entries": release["payload_entries"],
                    "release_id": release["release_id"],
                }
            )
            _write_exact(
                self._record_path(item_id, "release-binding", release_binding_id),
                canonical_json_bytes(release_binding),
            )
        revision = _base("revision", revision_id, item_id, observed_at)
        revision.update(
            {
                "acceptance_ref": _ref(acceptance_id, acceptance_bytes),
                "attempt_ref": _ref(intent_id, intent_bytes),
                "facet_refs": facet_refs,
                "operation": operation,
                "result_ref": _ref(result_id, result_bytes),
                "revision_id": revision_id,
                "status": "completed",
                "tombstone_ref": tombstone_ref,
            }
        )
        revision_bytes = canonical_json_bytes(revision)
        revision_path = self._record_path(item_id, "revision", revision_id)
        _write_exact(revision_path, revision_bytes)
        if inject_at == "after_revision":
            self._interrupt(
                item_id=item_id,
                attempt_id=attempt_id,
                point=inject_at,
                observed_at=observed_at,
                pointer_before=None if active is None else active["pointer_assertion_ref"],
            )

        pointer = _base("pointer-assertion", pointer_id, item_id, observed_at)
        pointer.update(
            {
                "attempt_id": attempt_id,
                "pointer_assertion_id": pointer_id,
                "prior_pointer_ref": None if active is None else active["pointer_assertion_ref"],
                "revision_ref": _ref(revision_id, revision_bytes),
            }
        )
        pointer_bytes = canonical_json_bytes(pointer)
        pointer_path = self._record_path(item_id, "pointer-assertion", pointer_id)
        _write_exact(pointer_path, pointer_bytes)
        if inject_at == "after_pointer_assertion":
            self._interrupt(
                item_id=item_id,
                attempt_id=attempt_id,
                point=inject_at,
                observed_at=observed_at,
                pointer_before=None if active is None else active["pointer_assertion_ref"],
            )

        selector = {
            "pointer_assertion_ref": _ref(pointer_id, pointer_bytes),
            "revision_ref": _ref(revision_id, revision_bytes),
            "schema_generation": 1,
        }
        active_path = generation_root / "active-pointer.json"
        replace_json(active_path, selector)
        if inject_at == "after_switch":
            self._interrupt(
                item_id=item_id,
                attempt_id=attempt_id,
                point=inject_at,
                observed_at=observed_at,
                pointer_before=None if active is None else active["pointer_assertion_ref"],
            )
        payload_sha256 = values["evidence"].get("payload_sha256")
        if not isinstance(payload_sha256, str):
            raise ContractError("HV2-PAYLOAD-DIGEST", "missing-evidence")
        self._land_payload(stage_root, payload_sha256)
        self._persist_binding_receipt(
            item_id=item_id,
            attempt_id=attempt_id,
            observed_at=observed_at,
            revision_ref=_ref(revision_id, revision_bytes),
            result_ref=_ref(result_id, result_bytes),
            payload_sha256=payload_sha256,
        )
        verified = self.verify(item_id)
        return {
            "attempt_id": attempt_id,
            "binding_completion": "complete",
            "classification": verified["classification"],
            "operation": operation,
            "pointer_assertion_id": pointer_id,
            "revision_id": revision_id,
        }

    def resume(self, item_id: str, operation: str, sequence: int) -> dict[str, Any]:
        self._validate_operation_sequence(operation, sequence)
        suffix = f"{sequence:04d}"
        attempt_id = f"attempt-{operation}-{suffix}"
        revision_id = f"revision-{suffix}"
        pointer_id = f"pointer-assertion-{suffix}"
        revision_path = self._record_path(item_id, "revision", revision_id)
        pointer_path = self._record_path(item_id, "pointer-assertion", pointer_id)
        result_path = self._record_path(item_id, "attempt-result", f"result-{attempt_id}")
        stage_root = self.root / "staging" / attempt_id
        for path in (revision_path, pointer_path, result_path, stage_root / "inventory.json"):
            if not path.is_file():
                raise ContractError("HV2-RESUME-EVIDENCE", str(path))
        self._verify_stage(stage_root)
        revision = load_json(revision_path, require_canonical=True)
        pointer = load_json(pointer_path, require_canonical=True)
        result = load_json(result_path, require_canonical=True)
        intent_path = self._record_path(item_id, "attempt-intent", f"intent-{attempt_id}")
        intent = load_json(intent_path, require_canonical=True)
        if intent.get("operation") != operation or revision.get("operation") != operation:
            raise ContractError("HV2-RESUME-OPERATION", operation)
        if revision.get("result_ref") != _ref(result["record_id"], result_path.read_bytes()):
            raise ContractError("HV2-RESUME-RESULT", attempt_id)
        acceptance_ref = result.get("acceptance_ref")
        if not isinstance(acceptance_ref, dict) or set(acceptance_ref) != {"id", "sha256"}:
            raise ContractError("HV2-REF-SHAPE", repr(acceptance_ref))
        acceptance_path = self._record_path(item_id, "acceptance", acceptance_ref["id"])
        if not acceptance_path.is_file() or sha256_file(acceptance_path) != acceptance_ref["sha256"]:
            raise ContractError("HV2-REF-DIGEST", acceptance_ref["id"])
        acceptance = load_json(acceptance_path, require_canonical=True)
        if (
            acceptance.get("accepted") is not True
            or acceptance.get("attempt_id") != attempt_id
            or result.get("outcome") != "validated"
            or acceptance.get("proposal_inventory_sha256") != result.get("proposal_inventory_sha256")
            or revision.get("acceptance_ref") != acceptance_ref
        ):
            raise ContractError("HV2-PROPOSAL-BINDING", attempt_id)
        if pointer["revision_ref"] != _ref(revision_id, revision_path.read_bytes()):
            raise ContractError("HV2-RESUME-REVISION", revision_id)
        current = self._active_pointer(item_id)
        binding_path = self._record_path(item_id, "binding-receipt", f"binding-{attempt_id}")
        already_selected = current is not None and current["revision_ref"]["id"] == revision_id
        if already_selected and binding_path.exists():
            raise ContractError("HV2-RESUME-ALREADY-CURRENT", revision_id)
        expected_prior = pointer["prior_pointer_ref"]
        current_pointer_ref = None if current is None else current["pointer_assertion_ref"]
        if not already_selected and expected_prior != current_pointer_ref:
            raise ContractError("HV2-RESUME-NOT-TIP", revision_id)
        selector = {
            "pointer_assertion_ref": _ref(pointer_id, pointer_path.read_bytes()),
            "revision_ref": _ref(revision_id, revision_path.read_bytes()),
            "schema_generation": 1,
        }
        if not already_selected:
            replace_json(self._item_root(item_id) / "generations" / "1" / "active-pointer.json", selector)
        evidence_ref = revision["facet_refs"]["evidence"]
        evidence_path = self._record_path(item_id, "facet-assertion", evidence_ref["id"], "evidence")
        if sha256_file(evidence_path) != evidence_ref["sha256"]:
            raise ContractError("HV2-REF-DIGEST", evidence_ref["id"])
        evidence = load_json(evidence_path, require_canonical=True)["value"]
        payload_sha256 = evidence.get("payload_sha256")
        if not isinstance(payload_sha256, str):
            raise ContractError("HV2-PAYLOAD-DIGEST", "resume-evidence")
        self._land_payload(stage_root, payload_sha256)
        resume_id = f"resume-{attempt_id}"
        resume_record = _base("resume", resume_id, item_id, intent["observed_at"])
        resume_record.update(
            {
                "attempt_id": attempt_id,
                "pointer_after": selector["pointer_assertion_ref"],
                "pointer_before": current_pointer_ref,
                "revision_ref": selector["revision_ref"],
            }
        )
        _write_exact(self._record_path(item_id, "resume", resume_id), canonical_json_bytes(resume_record))
        self._persist_binding_receipt(
            item_id=item_id,
            attempt_id=attempt_id,
            observed_at=intent["observed_at"],
            revision_ref=selector["revision_ref"],
            result_ref=_ref(result["record_id"], result_path.read_bytes()),
            payload_sha256=payload_sha256,
        )
        verified = self.verify(item_id)
        return {
            "attempt_id": attempt_id,
            "binding_completion": "complete-after-resume",
            "classification": verified["classification"],
            "pointer_assertion_id": pointer_id,
            "revision_id": revision_id,
        }

    def _verify_stage(self, stage_root: Path) -> dict[str, Any]:
        inventory_path = stage_root / "inventory.json"
        inventory = load_json(inventory_path, require_canonical=True)
        if set(inventory) != {"attempt_id", "entries", "record_type", "schema_generation"}:
            raise ContractError("HV2-STAGING-INVENTORY-SCHEMA", str(stage_root))
        if (
            inventory["record_type"] != "staging-inventory"
            or type(inventory["schema_generation"]) is not int
            or inventory["schema_generation"] != 1
        ):
            raise ContractError("HV2-STAGING-INVENTORY-GENERATION", str(stage_root))
        paths = []
        folded: set[str] = set()
        for entry in inventory["entries"]:
            if set(entry) != {"path", "sha256", "size_bytes"}:
                raise ContractError("HV2-STAGING-ENTRY-SCHEMA", repr(entry))
            if (
                not isinstance(entry["path"], str)
                or not isinstance(entry["sha256"], str)
                or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])
                or type(entry["size_bytes"]) is not int
                or entry["size_bytes"] < 0
            ):
                raise ContractError("HV2-STAGING-ENTRY-TYPE", repr(entry))
            relative = PurePosixPath(entry["path"])
            if (
                relative.is_absolute()
                or any(part in {"", ".", ".."} for part in relative.parts)
                or str(relative) != entry["path"]
                or unicodedata.normalize("NFC", entry["path"]) != entry["path"]
            ):
                raise ContractError("HV2-STAGING-UNSAFE-PATH", entry["path"])
            folded_path = entry["path"].casefold()
            if folded_path in folded:
                raise ContractError("HV2-STAGING-PATH-COLLISION", entry["path"])
            folded.add(folded_path)
            path = stage_root.joinpath(*relative.parts)
            if path.is_symlink() or not path.is_file():
                raise ContractError("HV2-STAGING-ENTRY-TYPE", entry["path"])
            data = path.read_bytes()
            if len(data) != entry["size_bytes"] or sha256_bytes(data) != entry["sha256"]:
                raise ContractError("HV2-STAGING-ENTRY-DIGEST", entry["path"])
            paths.append(entry["path"])
        if paths != sorted(paths, key=lambda value: value.encode("utf-8")) or len(paths) != len(set(paths)):
            raise ContractError("HV2-STAGING-ENTRY-ORDER", repr(paths))
        actual_files: list[str] = []
        for directory, dirnames, filenames in os.walk(stage_root, followlinks=False):
            dirnames.sort()
            for name in dirnames:
                child = Path(directory) / name
                if child.is_symlink() or not child.is_dir():
                    raise ContractError("HV2-STAGING-ENTRY-TYPE", str(child))
            for name in sorted(filenames):
                file_path = Path(directory) / name
                if file_path == inventory_path:
                    continue
                if file_path.is_symlink() or not file_path.is_file():
                    raise ContractError("HV2-STAGING-ENTRY-TYPE", str(file_path))
                actual_files.append(file_path.relative_to(stage_root).as_posix())
        if actual_files != paths:
            raise ContractError("HV2-STAGING-INVENTORY-COVERAGE", repr(actual_files))
        return {"attempt_id": inventory["attempt_id"], "entry_count": len(paths), "inventory_sha256": sha256_file(inventory_path)}

    def verify(self, item_id: str) -> dict[str, Any]:
        authority_path = self.root / "authority.json"
        item_root = self._item_root(item_id)
        identity_path = item_root / "identity.json"
        generation_path = item_root / "active-generation.json"
        active_path = item_root / "generations" / "1" / "active-pointer.json"
        if not authority_path.is_file() or not identity_path.is_file() or not generation_path.is_file():
            raise ContractError("HV2-ROOT-INCOMPLETE", item_id)
        authority = load_json(authority_path, require_canonical=True)
        identity_record = load_json(identity_path, require_canonical=True)
        generation = load_json(generation_path, require_canonical=True)
        degraded: list[str] = []
        incompatible: list[str] = []
        if set(authority) != {"authority_home_id", "authority_kind", "created_at", "lineage"}:
            degraded.append("authority.json:unknown-member")
        if set(identity_record) != {"item_id", "item_type", "lineage", "schema_generation"}:
            degraded.append("identity.json:unknown-member")
        if identity_record.get("item_id") != item_id:
            raise ContractError("HV2-ITEM-IDENTITY", repr(identity_record.get("item_id")))
        if (
            type(identity_record.get("schema_generation")) is not int
            or identity_record.get("schema_generation") != 1
            or type(generation.get("schema_generation")) is not int
            or generation.get("schema_generation") != 1
        ):
            incompatible.append("selector-or-identity-generation")
        if set(generation) != {"generation", "generation_assertion_ref", "schema_generation"}:
            degraded.append("active-generation.json:unknown-member")
        if type(generation.get("generation")) is not int or generation.get("generation") != 1:
            incompatible.append("active-generation.json:generation")

        records: dict[tuple[str, str], tuple[str, Path, dict[str, Any]]] = {}
        for path in sorted(item_root.rglob("*.json")):
            if path in {identity_path, generation_path, active_path}:
                continue
            value = load_json(path, require_canonical=True)
            record_type = value.get("record_type")
            record_id = value.get("record_id")
            if not isinstance(record_type, str):
                raise ContractError("HV2-CANONICAL-JSON-ROLE", str(path))
            if type(value.get("schema_generation")) is not int or value.get("schema_generation") != 1:
                incompatible.append(f"{path.name}:schema-generation")
                continue
            if record_type not in TYPE_EXTRA_KEYS:
                incompatible.append(f"{path.name}:record-type")
                continue
            allowed = BASE_KEYS | TYPE_EXTRA_KEYS[record_type]
            missing = BASE_KEYS - set(value)
            if missing:
                raise ContractError("HV2-ASSERTION-REQUIRED-FIELD", f"{path}:{sorted(missing)}")
            missing_type = TYPE_EXTRA_KEYS[record_type] - set(value)
            if missing_type:
                raise ContractError("HV2-RECORD-REQUIRED-FIELD", f"{path}:{sorted(missing_type)}")
            unknown = set(value) - allowed
            if unknown:
                degraded.append(f"{path.name}:unknown:{','.join(sorted(unknown))}")
            if not isinstance(value.get("observed_scope"), list) or not isinstance(value.get("unavailable_scope"), list):
                raise ContractError("HV2-ASSERTION-SCOPE", str(path))
            if value["unavailable_scope"]:
                degraded.append(f"{path.name}:unavailable-scope")
            if value.get("item_id") != item_id:
                raise ContractError("HV2-RECORD-ITEM", str(path))
            if not isinstance(record_id, str) or not record_id:
                raise ContractError("HV2-RECORD-ID-TYPE", repr(record_id))
            record_identity = (record_type, record_id)
            if record_identity in records:
                raise ContractError("HV2-RECORD-ID-REUSE", f"{record_type}:{record_id}")
            if record_type == "generation-assertion":
                expected_path = item_root / "generation-assertions" / f"{record_id}.json"
            elif record_type == "facet-assertion":
                expected_path = self._record_path(item_id, record_type, record_id, value.get("facet"))
            else:
                expected_path = self._record_path(item_id, record_type, record_id)
            if path != expected_path:
                raise ContractError("HV2-RECORD-PATH", f"{path}:{expected_path}")
            records[record_identity] = (record_type, path, value)

        staging_root = self.root / "staging"
        expected_files = {
            self.root / ".gitignore",
            authority_path,
            identity_path,
            generation_path,
            *(path for _, path, _ in records.values()),
        }
        if active_path.exists():
            expected_files.add(active_path)
        expected_paths = set(expected_files)
        for expected_file in expected_files:
            parent = expected_file.parent
            while parent != self.root:
                expected_paths.add(parent)
                parent = parent.parent
        if staging_root.exists():
            expected_paths.add(staging_root)
        actual_paths = {
            path
            for path in self.root.rglob("*")
            if path == staging_root or staging_root not in path.parents
        }
        for path in sorted(actual_paths - expected_paths):
            degraded.append(f"canonical-tree-extra:{path.relative_to(self.root).as_posix()}")
        for path in sorted(expected_paths - actual_paths):
            degraded.append(f"canonical-tree-missing:{path.relative_to(self.root).as_posix()}")

        staging: list[dict[str, Any]] = []
        if staging_root.exists():
            for directory in sorted(path for path in staging_root.iterdir() if path.is_dir()):
                if not (directory / "inventory.json").exists():
                    staging.append({"attempt_id": directory.name, "status": "residue-without-inventory"})
                    continue
                try:
                    verified_stage = self._verify_stage(directory)
                    verified_stage["status"] = "sealed"
                    staging.append(verified_stage)
                except ContractError as exc:
                    staging.append({"attempt_id": directory.name, "error_code": exc.code, "status": "damaged"})
        temp_residues = sorted(path.relative_to(self.root).as_posix() for path in self.root.rglob("*.hv2-tmp"))
        if temp_residues:
            degraded.extend(f"temp-residue:{path}" for path in temp_residues)

        if incompatible:
            return {
                "authority_home_id": authority.get("authority_home_id"),
                "classification": "incompatible",
                "current_revision_id": None,
                "degraded_reasons": degraded,
                "finalizable": False,
                "incompatible_reasons": incompatible,
                "item_id": item_id,
                "lifecycle": None,
                "record_count": len(records),
                "staging_inventories": staging,
                "writable": False,
            }

        def verify_ref(ref: Any, expected_type: str) -> dict[str, Any]:
            if not isinstance(ref, dict) or set(ref) != {"id", "sha256"}:
                raise ContractError("HV2-REF-SHAPE", repr(ref))
            if not isinstance(ref["id"], str) or not isinstance(ref["sha256"], str):
                raise ContractError("HV2-REF-SHAPE", repr(ref))
            if not re.fullmatch(r"[0-9a-f]{64}", ref["sha256"]):
                raise ContractError("HV2-REF-SHAPE", repr(ref))
            ref_identity = (expected_type, ref["id"])
            if ref_identity not in records:
                raise ContractError("HV2-REF-MISSING", ref["id"])
            actual_type, path, value = records[ref_identity]
            if actual_type != expected_type or sha256_file(path) != ref["sha256"]:
                raise ContractError("HV2-REF-DIGEST", ref["id"])
            return value

        generation_assertion = verify_ref(generation["generation_assertion_ref"], "generation-assertion")
        if generation_assertion.get("generation") != 1 or generation_assertion.get("state") != "active":
            raise ContractError("HV2-GENERATION-ASSERTION", item_id)

        pointer_records: dict[str, dict[str, Any]] = {}
        revisions_by_attempt: dict[str, tuple[dict[str, Any], dict[str, str]]] = {}
        binding_by_attempt: dict[str, dict[str, Any]] = {}
        for _, record_path, record in records.values():
            record_type = record["record_type"]
            if record_type == "attempt-result":
                acceptance = verify_ref(record["acceptance_ref"], "acceptance")
                if acceptance.get("accepted") is not True or record.get("outcome") != "validated":
                    raise ContractError("HV2-ACCEPTANCE-OUTCOME", record["record_id"])
                if acceptance.get("attempt_id") != record.get("attempt_id"):
                    raise ContractError("HV2-ATTEMPT-BINDING", record["record_id"])
                if acceptance.get("proposal_inventory_sha256") != record.get("proposal_inventory_sha256"):
                    raise ContractError("HV2-PROPOSAL-BINDING", record["record_id"])
            elif record_type == "revision":
                acceptance = verify_ref(record["acceptance_ref"], "acceptance")
                intent = verify_ref(record["attempt_ref"], "attempt-intent")
                result = verify_ref(record["result_ref"], "attempt-result")
                if record.get("status") != "completed" or acceptance.get("accepted") is not True or result.get("outcome") != "validated":
                    raise ContractError("HV2-REVISION-OUTCOME", record["record_id"])
                if result.get("acceptance_ref") != record.get("acceptance_ref"):
                    raise ContractError("HV2-REVISION-RESULT-BINDING", record["record_id"])
                attempt_id = intent.get("attempt_id")
                if (
                    not isinstance(attempt_id, str)
                    or attempt_id != acceptance.get("attempt_id")
                    or attempt_id != result.get("attempt_id")
                    or intent.get("requested_revision_id") != record.get("revision_id")
                    or intent.get("target_item_id") != item_id
                    or intent.get("operation") != record.get("operation")
                ):
                    raise ContractError("HV2-ATTEMPT-BINDING", record["record_id"])
                if acceptance.get("proposal_inventory_sha256") != result.get("proposal_inventory_sha256"):
                    raise ContractError("HV2-PROPOSAL-BINDING", record["record_id"])
                if set(record["facet_refs"]) != set(FACETS):
                    raise ContractError("HV2-FACET-COVERAGE", record["record_id"])
                for facet, ref in record["facet_refs"].items():
                    assertion = verify_ref(ref, "facet-assertion")
                    if assertion["facet"] != facet:
                        raise ContractError("HV2-FACET-REF", facet)
                    value = assertion.get("value")
                    if not isinstance(value, dict):
                        raise ContractError("HV2-FACET-VALUE", facet)
                    if facet == "intent" and (value.get("operation") != record["operation"] or type(value.get("sequence")) is not int):
                        raise ContractError("HV2-FACET-VALUE", facet)
                    if facet == "lifecycle" and value.get("state") not in {"active", "detached"}:
                        raise ContractError("HV2-FACET-VALUE", facet)
                    if facet == "relations" and not isinstance(value.get("refs"), list):
                        raise ContractError("HV2-FACET-VALUE", facet)
                    if facet == "currentness" and (
                        value.get("selected_by") != "active-pointer" or type(value.get("sequence")) is not int
                    ):
                        raise ContractError("HV2-FACET-VALUE", facet)
                    if facet == "continuation" and value.get("mode") not in {"manual-provider-null", "plain"}:
                        raise ContractError("HV2-FACET-VALUE", facet)
                    if facet == "evidence" and (
                        not isinstance(value.get("payload_sha256"), str)
                        or re.fullmatch(r"[0-9a-f]{64}", value["payload_sha256"]) is None
                    ):
                        raise ContractError("HV2-FACET-VALUE", facet)
                    if facet == "ownership" and set(value) != {"finalizer", "writer"}:
                        raise ContractError("HV2-FACET-VALUE", facet)
                if record["tombstone_ref"] is not None:
                    verify_ref(record["tombstone_ref"], "tombstone")
                rollback_source_ref = intent.get("rollback_source_ref")
                if record["operation"] == "rollback":
                    source_revision = verify_ref(rollback_source_ref, "revision")
                    if source_revision.get("status") != "completed":
                        raise ContractError("HV2-ROLLBACK-SOURCE", record["record_id"])
                elif rollback_source_ref is not None:
                    raise ContractError("HV2-ROLLBACK-SOURCE", record["record_id"])
                revisions_by_attempt[attempt_id] = (record, _ref(record["record_id"], record_path.read_bytes()))
            elif record_type == "pointer-assertion":
                verify_ref(record["revision_ref"], "revision")
                if record["prior_pointer_ref"] is not None:
                    verify_ref(record["prior_pointer_ref"], "pointer-assertion")
                pointer_records[record["record_id"]] = record
            elif record_type == "binding-receipt":
                verify_ref(record["revision_ref"], "revision")
                verify_ref(record["result_ref"], "attempt-result")
                if record.get("git_state") != "unfinalized":
                    raise ContractError("HV2-BINDING-RECEIPT", record["record_id"])
                binding_by_attempt[record["attempt_id"]] = record
            elif record_type == "resume":
                verify_ref(record["revision_ref"], "revision")
                verify_ref(record["pointer_after"], "pointer-assertion")
                if record["pointer_before"] is not None:
                    verify_ref(record["pointer_before"], "pointer-assertion")
            elif record_type == "interruption":
                if record.get("exit_code") != 75 or record.get("injected_at") not in {
                    "after_intent",
                    "after_stage",
                    "after_acceptance",
                    "after_result",
                    "after_revision",
                    "after_pointer_assertion",
                    "after_switch",
                }:
                    raise ContractError("HV2-INTERRUPTION-RECORD", record["record_id"])
                if record["pointer_before"] is not None:
                    verify_ref(record["pointer_before"], "pointer-assertion")

        release_bindings = {
            record["release_id"]: record
            for record_type, _, record in records.values()
            if record_type == "release-binding"
        }
        current_revision = None
        lifecycle = None
        active = None
        if active_path.exists():
            active = load_json(active_path, require_canonical=True)
            if set(active) != {"pointer_assertion_ref", "revision_ref", "schema_generation"}:
                degraded.append("active-pointer.json:unknown-member")
            if type(active.get("schema_generation")) is not int or active.get("schema_generation") != 1:
                incompatible.append("active-pointer.json:schema-generation")
            pointer = verify_ref(active["pointer_assertion_ref"], "pointer-assertion")
            revision = verify_ref(active["revision_ref"], "revision")
            if pointer["revision_ref"] != active["revision_ref"]:
                raise ContractError("HV2-POINTER-CONTRADICTION", item_id)
            current_revision = revision["revision_id"]
            lifecycle_ref = revision["facet_refs"]["lifecycle"]
            lifecycle = verify_ref(lifecycle_ref, "facet-assertion")["value"].get("state")

        if pointer_records:
            children: dict[str | None, list[str]] = {}
            for pointer_id, pointer in pointer_records.items():
                prior = pointer["prior_pointer_ref"]
                prior_id = None if prior is None else prior["id"]
                children.setdefault(prior_id, []).append(pointer_id)
            if len(children.get(None, [])) != 1 or any(len(child_ids) > 1 for child_ids in children.values()):
                raise ContractError("HV2-POINTER-HISTORY-CONTRADICTION", "fork-or-root")
            tips = [pointer_id for pointer_id in pointer_records if pointer_id not in children]
            if len(tips) != 1 or active is None or active["pointer_assertion_ref"]["id"] != tips[0]:
                raise ContractError("HV2-POINTER-HISTORY-CONTRADICTION", "active-not-tip")
        elif active is not None:
            raise ContractError("HV2-POINTER-HISTORY-CONTRADICTION", "active-without-history")

        selected_revision_refs = {pointer["revision_ref"]["id"] for pointer in pointer_records.values()}
        for attempt_id, (revision, revision_ref) in revisions_by_attempt.items():
            binding = binding_by_attempt.get(attempt_id)
            if revision["record_id"] in selected_revision_refs:
                if binding is None or binding.get("revision_ref") != revision_ref or binding.get("result_ref") != revision["result_ref"]:
                    raise ContractError("HV2-BINDING-RECEIPT", attempt_id)
            intent = verify_ref(revision["attempt_ref"], "attempt-intent")
            release_ref = intent.get("release_ref")
            if revision["operation"] == "create":
                if not isinstance(release_ref, dict) or set(release_ref) != {"id", "sha256"}:
                    raise ContractError("HV2-RELEASE-BINDING", intent["record_id"])
                release_binding = release_bindings.get(release_ref["id"])
                if release_binding is None or release_binding.get("carrier_sha256") != release_ref["sha256"]:
                    raise ContractError("HV2-RELEASE-BINDING", intent["record_id"])
            elif release_ref is not None:
                raise ContractError("HV2-RELEASE-BINDING", intent["record_id"])
            if revision["operation"] == "rollback" and intent["rollback_source_ref"]["id"] not in selected_revision_refs:
                raise ContractError("HV2-ROLLBACK-SOURCE", revision["record_id"])

        if active is not None:
            current = verify_ref(active["revision_ref"], "revision")
            evidence = verify_ref(current["facet_refs"]["evidence"], "facet-assertion")["value"]
            target_payload = self.target_root / "docs" / "GENERATION-1-CONTRACT.md"
            if (
                target_payload.is_symlink()
                or not target_payload.is_file()
                or sha256_file(target_payload) != evidence["payload_sha256"]
            ):
                raise ContractError("HV2-PAYLOAD-DIGEST", "target")

        classification = "incompatible" if incompatible else "degraded" if degraded else "pass"
        return {
            "authority_home_id": authority.get("authority_home_id"),
            "classification": classification,
            "current_revision_id": current_revision,
            "degraded_reasons": degraded,
            "finalizable": classification == "pass",
            "incompatible_reasons": incompatible,
            "item_id": item_id,
            "lifecycle": lifecycle,
            "record_count": len(records),
            "staging_inventories": staging,
            "writable": classification == "pass",
        }
