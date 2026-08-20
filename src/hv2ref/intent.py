from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .errors import ContractError, InjectedCrash
from .jsonio import canonical_json_bytes, load_json, replace_json, sha256_bytes, sha256_file, write_new_json


INTENT_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
REVISION_ID_PATTERN = re.compile(r"revision-([0-9]{4})")
ACCEPTANCE_ID_PATTERN = re.compile(r"acceptance-([0-9]{4})")
SELECTION_ID_PATTERN = re.compile(r"selection-([0-9]{4})")
FACET_KEYS = {
    "acceptance_oracle",
    "destination",
    "expected_outcome",
    "forbidden_scope",
    "goal",
    "scope",
}
CONTENT_KEYS = {"acceptance_authority", "actor", "facets", "gaps", "statements"}
STATEMENT_KINDS = {"assumption", "fact", "human-decision", "unknown"}

AUTHORITY_KEYS = {"authority_home_id", "authority_kind", "created_at", "record_type", "schema_generation"}
IDENTITY_KEYS = {"authority_home_id", "intent_id", "record_type", "schema_generation"}
DRAFT_KEYS = {
    "acceptance_authority",
    "actor",
    "authority_home_id",
    "facets",
    "gaps",
    "intent_id",
    "observed_at",
    "prior_revision_ref",
    "record_type",
    "revision_id",
    "route",
    "schema_generation",
    "sequence",
    "statements",
}
ACCEPTANCE_KEYS = {
    "acceptance_id",
    "accepted",
    "actor",
    "authority_home_id",
    "intent_id",
    "observed_at",
    "record_type",
    "revision_ref",
    "schema_generation",
    "supersedes_selection_ref",
}
SELECTION_KEYS = {
    "acceptance_ref",
    "authority_home_id",
    "intent_id",
    "prior_selection_ref",
    "record_type",
    "revision_ref",
    "schema_generation",
    "selection_id",
}
CURRENT_KEYS = {"authority_home_id", "intent_id", "schema_generation", "selection_ref"}


def _require_identifier(value: object, code: str) -> str:
    if not isinstance(value, str) or INTENT_ID_PATTERN.fullmatch(value) is None:
        raise ContractError(code, repr(value))
    return value


def _require_text(value: object, code: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(code, repr(value))
    return value


def _exact_keys(value: object, expected: set[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        actual = sorted(value) if isinstance(value, dict) else type(value).__name__
        raise ContractError(code, repr(actual))
    return value


def _ref(record_id: str, data: bytes) -> dict[str, str]:
    return {"id": record_id, "sha256": sha256_bytes(data)}


def _write_exact_json(path: Path, value: Any, code: str) -> bytes:
    data = canonical_json_bytes(value)
    if path.exists() or path.is_symlink():
        if path.is_symlink() or not path.is_file() or path.read_bytes() != data:
            raise ContractError(code, str(path))
        return data
    write_new_json(path, value)
    return data


def _validate_ref(value: object, code: str) -> dict[str, str]:
    ref = _exact_keys(value, {"id", "sha256"}, code)
    _require_text(ref["id"], code)
    if not isinstance(ref["sha256"], str) or re.fullmatch(r"[0-9a-f]{64}", ref["sha256"]) is None:
        raise ContractError(code, repr(ref["sha256"]))
    return ref


def _validate_facet(name: str, value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError("HV2-INTENT-FACET", name)
    status = value.get("status")
    if status == "known":
        facet = _exact_keys(value, {"status", "value"}, "HV2-INTENT-FACET")
        item = facet["value"]
        if item is None or item == "" or item == {} or (item == [] and name != "forbidden_scope"):
            raise ContractError("HV2-INTENT-FACET-VALUE", name)
        return facet
    if status in {"unknown", "deferred"}:
        facet = _exact_keys(value, {"owner", "status"}, "HV2-INTENT-FACET")
        _require_text(facet["owner"], "HV2-INTENT-FACET-OWNER")
        return facet
    raise ContractError("HV2-INTENT-FACET-STATUS", f"{name}:{status}")


def _validate_gap_graph(gaps: object) -> list[dict[str, Any]]:
    if not isinstance(gaps, list):
        raise ContractError("HV2-INTENT-GAPS", type(gaps).__name__)
    normalized: list[dict[str, Any]] = []
    ids: set[str] = set()
    for raw in gaps:
        gap = _exact_keys(raw, {"depends_on", "gap_id", "material", "owner", "status"}, "HV2-INTENT-GAP")
        gap_id = _require_identifier(gap["gap_id"], "HV2-INTENT-GAP-ID")
        if gap_id in ids:
            raise ContractError("HV2-INTENT-GAP-ID", gap_id)
        ids.add(gap_id)
        if type(gap["material"]) is not bool or gap["status"] not in {"resolved", "unresolved"}:
            raise ContractError("HV2-INTENT-GAP", gap_id)
        _require_text(gap["owner"], "HV2-INTENT-GAP-OWNER")
        if not isinstance(gap["depends_on"], list) or any(not isinstance(item, str) for item in gap["depends_on"]):
            raise ContractError("HV2-INTENT-GAP-DEPENDENCY", gap_id)
        dependencies = sorted(set(gap["depends_on"]), key=lambda item: item.encode("utf-8"))
        if len(dependencies) != len(gap["depends_on"]) or gap_id in dependencies:
            raise ContractError("HV2-INTENT-GAP-DEPENDENCY", gap_id)
        normalized.append({**gap, "depends_on": dependencies})
    normalized.sort(key=lambda item: item["gap_id"].encode("utf-8"))
    by_id = {item["gap_id"]: item for item in normalized}
    for item in normalized:
        if any(dependency not in by_id for dependency in item["depends_on"]):
            raise ContractError("HV2-INTENT-GAP-DEPENDENCY", item["gap_id"])
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(gap_id: str) -> None:
        if gap_id in visiting:
            raise ContractError("HV2-INTENT-GAP-CYCLE", gap_id)
        if gap_id in visited:
            return
        visiting.add(gap_id)
        for dependency in by_id[gap_id]["depends_on"]:
            visit(dependency)
        visiting.remove(gap_id)
        visited.add(gap_id)

    for gap_id in sorted(by_id):
        visit(gap_id)
    return normalized


def classify_entry(consequence: str, gaps: list[dict[str, Any]]) -> dict[str, Any]:
    if consequence == "non-consequential":
        if gaps:
            raise ContractError("HV2-INTENT-NONCONSEQUENTIAL-GAPS", str(len(gaps)))
        return {"artifact_required": False, "route": "non-consequential"}
    if consequence != "consequential":
        raise ContractError("HV2-INTENT-CONSEQUENCE", consequence)
    normalized = _validate_gap_graph(gaps)
    unresolved = [item for item in normalized if item["material"] and item["status"] == "unresolved"]
    unresolved_ids = {item["gap_id"] for item in unresolved}
    dependency_bound = any(any(dep in unresolved_ids for dep in item["depends_on"]) for item in unresolved)
    if dependency_bound:
        route = "dependency-ordered-clarification"
    elif unresolved:
        route = "bounded-clarification"
    else:
        route = "direct-entry"
    return {"artifact_required": True, "route": route}


def _normalize_content(content: object) -> dict[str, Any]:
    value = _exact_keys(content, CONTENT_KEYS, "HV2-INTENT-CONTENT")
    actor = _require_text(value["actor"], "HV2-INTENT-ACTOR")
    authority = _require_text(value["acceptance_authority"], "HV2-INTENT-AUTHORITY")
    facets = _exact_keys(value["facets"], FACET_KEYS, "HV2-INTENT-FACETS")
    normalized_facets = {name: _validate_facet(name, facets[name]) for name in sorted(FACET_KEYS)}
    if not isinstance(value["statements"], list):
        raise ContractError("HV2-INTENT-STATEMENTS", type(value["statements"]).__name__)
    statements = []
    for raw in value["statements"]:
        statement = _exact_keys(raw, {"kind", "owner", "text"}, "HV2-INTENT-STATEMENT")
        if statement["kind"] not in STATEMENT_KINDS:
            raise ContractError("HV2-INTENT-STATEMENT-KIND", repr(statement["kind"]))
        _require_text(statement["owner"], "HV2-INTENT-STATEMENT-OWNER")
        _require_text(statement["text"], "HV2-INTENT-STATEMENT-TEXT")
        statements.append(dict(statement))
    statements.sort(key=lambda item: (item["kind"], item["owner"], item["text"]))
    gaps = _validate_gap_graph(value["gaps"])
    return {
        "acceptance_authority": authority,
        "actor": actor,
        "facets": normalized_facets,
        "gaps": gaps,
        "statements": statements,
    }


class IntentStore:
    def __init__(self, target_root: Path):
        self.target_root = target_root.resolve()
        self.root = self.target_root / ".harness-v2-intents"

    def _intent_root(self, intent_id: str) -> Path:
        path = self.root / _require_identifier(intent_id, "HV2-INTENT-ID")
        if path.is_symlink():
            raise ContractError("HV2-INTENT-PATH", str(path))
        return path

    def _load_authority(self) -> dict[str, Any]:
        if self.root.is_symlink() or not self.root.is_dir():
            raise ContractError("HV2-INTENT-HOME-INCOMPLETE", str(self.root))
        path = self.root / "authority.json"
        if path.is_symlink() or not path.is_file():
            raise ContractError("HV2-INTENT-HOME-INCOMPLETE", str(path))
        authority = _exact_keys(load_json(path, require_canonical=True), AUTHORITY_KEYS, "HV2-INTENT-AUTHORITY-RECORD")
        if authority["record_type"] != "intent-authority-home" or authority["schema_generation"] != 1:
            raise ContractError("HV2-INTENT-AUTHORITY-RECORD", str(path))
        _require_identifier(authority["authority_home_id"], "HV2-INTENT-AUTHORITY-HOME-ID")
        return authority

    def initialize(self, authority_home_id: str, observed_at: str) -> dict[str, Any]:
        _require_identifier(authority_home_id, "HV2-INTENT-AUTHORITY-HOME-ID")
        _require_text(observed_at, "HV2-INTENT-OBSERVED-AT")
        if self.root.exists() or self.root.is_symlink():
            raise ContractError("HV2-INTENT-HOME-REUSE", str(self.root))
        authority = {
            "authority_home_id": authority_home_id,
            "authority_kind": "guided-intent-standalone",
            "created_at": observed_at,
            "record_type": "intent-authority-home",
            "schema_generation": 1,
        }
        write_new_json(self.root / "authority.json", authority)
        return {"authority_home_id": authority_home_id, "classification": "pass"}

    def _load_identity(self, intent_id: str, authority: dict[str, Any]) -> dict[str, Any]:
        path = self._intent_root(intent_id) / "identity.json"
        if path.is_symlink() or not path.is_file():
            raise ContractError("HV2-INTENT-IDENTITY", intent_id)
        identity = _exact_keys(load_json(path, require_canonical=True), IDENTITY_KEYS, "HV2-INTENT-IDENTITY")
        if (
            identity["record_type"] != "intent-identity"
            or identity["schema_generation"] != 1
            or identity["authority_home_id"] != authority["authority_home_id"]
            or identity["intent_id"] != intent_id
        ):
            raise ContractError("HV2-INTENT-IDENTITY", intent_id)
        return identity

    def _draft_path(self, intent_id: str, revision_id: str) -> Path:
        if REVISION_ID_PATTERN.fullmatch(revision_id) is None:
            raise ContractError("HV2-INTENT-REVISION-ID", revision_id)
        return self._intent_root(intent_id) / "drafts" / f"{revision_id}.json"

    def _load_draft(self, intent_id: str, revision_id: str, authority: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
        path = self._draft_path(intent_id, revision_id)
        if path.is_symlink() or not path.is_file():
            raise ContractError("HV2-INTENT-DRAFT", revision_id)
        data = path.read_bytes()
        draft = _exact_keys(load_json(path, require_canonical=True), DRAFT_KEYS, "HV2-INTENT-DRAFT")
        if (
            draft["record_type"] != "intent-draft"
            or draft["schema_generation"] != 1
            or draft["authority_home_id"] != authority["authority_home_id"]
            or draft["intent_id"] != intent_id
            or draft["revision_id"] != revision_id
        ):
            raise ContractError("HV2-INTENT-DRAFT", revision_id)
        normalized = _normalize_content({key: draft[key] for key in CONTENT_KEYS})
        if any(draft[key] != normalized[key] for key in CONTENT_KEYS):
            raise ContractError("HV2-INTENT-DRAFT-NORMALIZATION", revision_id)
        expected_route = classify_entry("consequential", draft["gaps"])["route"]
        if draft["route"] != expected_route:
            raise ContractError("HV2-INTENT-ROUTE", revision_id)
        return draft, _ref(revision_id, data)

    def create_draft(
        self,
        intent_id: str,
        sequence: int,
        observed_at: str,
        content: object,
        inject_at: str | None = None,
    ) -> dict[str, Any]:
        authority = self._load_authority()
        intent_id = _require_identifier(intent_id, "HV2-INTENT-ID")
        if type(sequence) is not int or not 1 <= sequence <= 9999:
            raise ContractError("HV2-INTENT-SEQUENCE", repr(sequence))
        _require_text(observed_at, "HV2-INTENT-OBSERVED-AT")
        normalized = _normalize_content(content)
        route = classify_entry("consequential", normalized["gaps"])["route"]
        intent_root = self._intent_root(intent_id)
        identity_path = intent_root / "identity.json"
        revision_id = f"revision-{sequence:04d}"
        if sequence == 1:
            prior_ref = None
            identity = {
                "authority_home_id": authority["authority_home_id"],
                "intent_id": intent_id,
                "record_type": "intent-identity",
                "schema_generation": 1,
            }
            _write_exact_json(identity_path, identity, "HV2-INTENT-ID-REUSE")
        else:
            self.verify(intent_id)
            self._load_identity(intent_id, authority)
            prior_id = f"revision-{sequence - 1:04d}"
            _, prior_ref = self._load_draft(intent_id, prior_id, authority)
        draft = {
            **normalized,
            "authority_home_id": authority["authority_home_id"],
            "intent_id": intent_id,
            "observed_at": observed_at,
            "prior_revision_ref": prior_ref,
            "record_type": "intent-draft",
            "revision_id": revision_id,
            "route": route,
            "schema_generation": 1,
            "sequence": sequence,
        }
        draft_bytes = canonical_json_bytes(draft)
        _write_exact_json(self._draft_path(intent_id, revision_id), draft, "HV2-INTENT-DRAFT-CONTRADICTION")
        if inject_at is not None:
            if inject_at != "after-draft":
                raise ContractError("HV2-INTENT-INJECT-POINT", inject_at)
            raise InjectedCrash(inject_at)
        return {**draft, "revision_sha256": sha256_bytes(draft_bytes)}

    def _current(self, intent_id: str, authority: dict[str, Any]) -> dict[str, Any] | None:
        path = self._intent_root(intent_id) / "current-selection.json"
        if not path.exists():
            return None
        if path.is_symlink() or not path.is_file():
            raise ContractError("HV2-INTENT-CURRENT", str(path))
        current = _exact_keys(load_json(path, require_canonical=True), CURRENT_KEYS, "HV2-INTENT-CURRENT")
        if (
            current["authority_home_id"] != authority["authority_home_id"]
            or current["intent_id"] != intent_id
            or current["schema_generation"] != 1
        ):
            raise ContractError("HV2-INTENT-CURRENT", intent_id)
        _validate_ref(current["selection_ref"], "HV2-INTENT-CURRENT")
        return current

    def accept(
        self,
        intent_id: str,
        revision_id: str,
        revision_sha256: str,
        acceptance_id: str,
        actor: str,
        observed_at: str,
        supersedes_ref: dict[str, str] | None = None,
        inject_at: str | None = None,
    ) -> dict[str, Any]:
        authority = self._load_authority()
        self._load_identity(intent_id, authority)
        draft, revision_ref = self._load_draft(intent_id, revision_id, authority)
        if revision_ref["sha256"] != revision_sha256:
            raise ContractError("HV2-INTENT-REVISION-DIGEST", revision_id)
        if actor != draft["acceptance_authority"]:
            raise ContractError("HV2-INTENT-ACCEPTANCE-ACTOR", actor)
        _require_text(observed_at, "HV2-INTENT-OBSERVED-AT")
        match = ACCEPTANCE_ID_PATTERN.fullmatch(acceptance_id)
        if match is None:
            raise ContractError("HV2-INTENT-ACCEPTANCE-ID", acceptance_id)
        selection_id = f"selection-{match.group(1)}"
        if any(item["material"] and item["status"] == "unresolved" for item in draft["gaps"]):
            raise ContractError("HV2-INTENT-MATERIAL-GAP", revision_id)
        if not any(value["status"] == "known" for value in draft["facets"].values()):
            raise ContractError("HV2-INTENT-VACUOUS-ACCEPTANCE", revision_id)
        records = self._records(intent_id, authority)
        current = self._current(intent_id, authority)
        if current is not None:
            current_selection = records["selections"].get(current["selection_ref"]["id"])
            if current_selection is None or current_selection[1] != current["selection_ref"]:
                raise ContractError("HV2-INTENT-CURRENT", intent_id)
        if current is None:
            if supersedes_ref is not None:
                raise ContractError("HV2-INTENT-SUPERSEDE", "no-current")
            prior_selection_ref = None
        else:
            supplied = _validate_ref(supersedes_ref, "HV2-INTENT-SUPERSEDE")
            if supplied != current["selection_ref"]:
                raise ContractError("HV2-INTENT-SUPERSEDE", "stale-current")
            prior_selection_ref = supplied
        if inject_at is not None and inject_at not in {"after-acceptance", "after-selection"}:
            raise ContractError("HV2-INTENT-INJECT-POINT", inject_at)
        if records["selections"] and selection_id not in records["selections"] and current is None:
            raise ContractError("HV2-INTENT-SELECTION-RECOVERY", selection_id)
        if current is not None:
            pending_selection_ids = sorted(
                existing_id
                for existing_id, (selection, _) in records["selections"].items()
                if selection["prior_selection_ref"] == current["selection_ref"]
            )
            if pending_selection_ids and pending_selection_ids != [selection_id]:
                raise ContractError("HV2-INTENT-SELECTION-RECOVERY", selection_id)
        intent_root = self._intent_root(intent_id)
        acceptance = {
            "acceptance_id": acceptance_id,
            "accepted": True,
            "actor": actor,
            "authority_home_id": authority["authority_home_id"],
            "intent_id": intent_id,
            "observed_at": observed_at,
            "record_type": "intent-acceptance",
            "revision_ref": revision_ref,
            "schema_generation": 1,
            "supersedes_selection_ref": prior_selection_ref,
        }
        acceptance_path = intent_root / "acceptances" / f"{acceptance_id}.json"
        acceptance_bytes = _write_exact_json(acceptance_path, acceptance, "HV2-INTENT-ACCEPTANCE-CONTRADICTION")
        if inject_at == "after-acceptance":
            raise InjectedCrash(inject_at)
        selection = {
            "acceptance_ref": _ref(acceptance_id, acceptance_bytes),
            "authority_home_id": authority["authority_home_id"],
            "intent_id": intent_id,
            "prior_selection_ref": prior_selection_ref,
            "record_type": "intent-selection",
            "revision_ref": revision_ref,
            "schema_generation": 1,
            "selection_id": selection_id,
        }
        selection_path = intent_root / "selection-assertions" / f"{selection_id}.json"
        selection_bytes = _write_exact_json(selection_path, selection, "HV2-INTENT-SELECTION-CONTRADICTION")
        if inject_at == "after-selection":
            raise InjectedCrash(inject_at)
        selection_ref = _ref(selection_id, selection_bytes)
        replace_json(
            intent_root / "current-selection.json",
            {
                "authority_home_id": authority["authority_home_id"],
                "intent_id": intent_id,
                "schema_generation": 1,
                "selection_ref": selection_ref,
            },
        )
        return {"acceptance_ref": _ref(acceptance_id, acceptance_bytes), "revision_ref": revision_ref, "selection_ref": selection_ref}

    def _records(self, intent_id: str, authority: dict[str, Any]) -> dict[str, Any]:
        intent_root = self._intent_root(intent_id)
        self._load_identity(intent_id, authority)
        drafts: dict[str, tuple[dict[str, Any], dict[str, str]]] = {}
        draft_root = intent_root / "drafts"
        if draft_root.is_symlink() or not draft_root.is_dir():
            raise ContractError("HV2-INTENT-TREE", str(draft_root))
        for path in sorted(draft_root.glob("*.json")):
            if path.is_symlink() or not path.is_file():
                raise ContractError("HV2-INTENT-DRAFT", str(path))
            draft, ref = self._load_draft(intent_id, path.stem, authority)
            drafts[path.stem] = (draft, ref)
        if not drafts:
            raise ContractError("HV2-INTENT-DRAFT", "empty")
        expected_sequences = list(range(1, len(drafts) + 1))
        actual_sequences = sorted(draft["sequence"] for draft, _ in drafts.values())
        if actual_sequences != expected_sequences:
            raise ContractError("HV2-INTENT-REVISION-CHAIN", repr(actual_sequences))
        for sequence in actual_sequences:
            draft, _ = drafts[f"revision-{sequence:04d}"]
            expected_prior = None if sequence == 1 else drafts[f"revision-{sequence - 1:04d}"][1]
            if draft["prior_revision_ref"] != expected_prior:
                raise ContractError("HV2-INTENT-REVISION-CHAIN", draft["revision_id"])

        acceptances: dict[str, tuple[dict[str, Any], dict[str, str]]] = {}
        acceptance_root = intent_root / "acceptances"
        if acceptance_root.exists():
            if acceptance_root.is_symlink() or not acceptance_root.is_dir():
                raise ContractError("HV2-INTENT-TREE", str(acceptance_root))
            for path in sorted(acceptance_root.glob("*.json")):
                if path.is_symlink() or not path.is_file():
                    raise ContractError("HV2-INTENT-ACCEPTANCE", str(path))
                data = path.read_bytes()
                value = _exact_keys(load_json(path, require_canonical=True), ACCEPTANCE_KEYS, "HV2-INTENT-ACCEPTANCE")
                if (
                    value["record_type"] != "intent-acceptance"
                    or value["schema_generation"] != 1
                    or value["acceptance_id"] != path.stem
                    or ACCEPTANCE_ID_PATTERN.fullmatch(path.stem) is None
                    or value["authority_home_id"] != authority["authority_home_id"]
                    or value["intent_id"] != intent_id
                    or value["accepted"] is not True
                ):
                    raise ContractError("HV2-INTENT-ACCEPTANCE", str(path))
                revision_ref = _validate_ref(value["revision_ref"], "HV2-INTENT-ACCEPTANCE")
                if revision_ref["id"] not in drafts or drafts[revision_ref["id"]][1] != revision_ref:
                    raise ContractError("HV2-INTENT-ACCEPTANCE-REF", path.stem)
                draft = drafts[revision_ref["id"]][0]
                if value["actor"] != draft["acceptance_authority"]:
                    raise ContractError("HV2-INTENT-ACCEPTANCE-ACTOR", path.stem)
                if any(item["material"] and item["status"] == "unresolved" for item in draft["gaps"]):
                    raise ContractError("HV2-INTENT-MATERIAL-GAP", path.stem)
                if not any(facet["status"] == "known" for facet in draft["facets"].values()):
                    raise ContractError("HV2-INTENT-VACUOUS-ACCEPTANCE", path.stem)
                if value["supersedes_selection_ref"] is not None:
                    _validate_ref(value["supersedes_selection_ref"], "HV2-INTENT-SUPERSEDE")
                acceptances[path.stem] = (value, _ref(path.stem, data))

        selections: dict[str, tuple[dict[str, Any], dict[str, str]]] = {}
        selection_root = intent_root / "selection-assertions"
        if selection_root.exists():
            if selection_root.is_symlink() or not selection_root.is_dir():
                raise ContractError("HV2-INTENT-TREE", str(selection_root))
            for path in sorted(selection_root.glob("*.json")):
                if path.is_symlink() or not path.is_file():
                    raise ContractError("HV2-INTENT-SELECTION", str(path))
                data = path.read_bytes()
                value = _exact_keys(load_json(path, require_canonical=True), SELECTION_KEYS, "HV2-INTENT-SELECTION")
                if (
                    value["record_type"] != "intent-selection"
                    or value["schema_generation"] != 1
                    or value["selection_id"] != path.stem
                    or SELECTION_ID_PATTERN.fullmatch(path.stem) is None
                    or value["authority_home_id"] != authority["authority_home_id"]
                    or value["intent_id"] != intent_id
                ):
                    raise ContractError("HV2-INTENT-SELECTION", str(path))
                acceptance_ref = _validate_ref(value["acceptance_ref"], "HV2-INTENT-SELECTION")
                revision_ref = _validate_ref(value["revision_ref"], "HV2-INTENT-SELECTION")
                if acceptance_ref["id"] not in acceptances or acceptances[acceptance_ref["id"]][1] != acceptance_ref:
                    raise ContractError("HV2-INTENT-SELECTION-REF", path.stem)
                if revision_ref["id"] not in drafts or drafts[revision_ref["id"]][1] != revision_ref:
                    raise ContractError("HV2-INTENT-SELECTION-REF", path.stem)
                acceptance = acceptances[acceptance_ref["id"]][0]
                if acceptance["revision_ref"] != revision_ref or acceptance["supersedes_selection_ref"] != value["prior_selection_ref"]:
                    raise ContractError("HV2-INTENT-SELECTION-REF", path.stem)
                if value["prior_selection_ref"] is not None:
                    _validate_ref(value["prior_selection_ref"], "HV2-INTENT-SELECTION")
                selections[path.stem] = (value, _ref(path.stem, data))

        expected_paths = {intent_root, intent_root / "identity.json", draft_root}
        expected_paths.update(self._draft_path(intent_id, revision_id) for revision_id in drafts)
        if acceptances:
            expected_paths.add(acceptance_root)
            expected_paths.update(acceptance_root / f"{record_id}.json" for record_id in acceptances)
        if selections:
            expected_paths.add(selection_root)
            expected_paths.update(selection_root / f"{record_id}.json" for record_id in selections)
        current_path = intent_root / "current-selection.json"
        if current_path.exists():
            expected_paths.add(current_path)
        actual_paths = set(intent_root.rglob("*")) | {intent_root}
        if actual_paths != expected_paths:
            extra = sorted(str(path.relative_to(intent_root)) for path in actual_paths - expected_paths)
            missing = sorted(str(path.relative_to(intent_root)) for path in expected_paths - actual_paths)
            raise ContractError("HV2-INTENT-TREE", f"extra={extra}:missing={missing}")
        return {"acceptances": acceptances, "drafts": drafts, "selections": selections}

    def verify(self, intent_id: str) -> dict[str, Any]:
        authority = self._load_authority()
        for path in self.root.iterdir():
            if path.name == "authority.json":
                if path.is_symlink() or not path.is_file():
                    raise ContractError("HV2-INTENT-HOME-TREE", str(path))
            elif path.is_symlink() or not path.is_dir() or INTENT_ID_PATTERN.fullmatch(path.name) is None:
                raise ContractError("HV2-INTENT-HOME-TREE", str(path))
        records = self._records(intent_id, authority)
        selections = records["selections"]
        current = self._current(intent_id, authority)
        current_revision = None
        current_ref = None
        pending_selection_ids: list[str] = []
        if selections:
            children: dict[str | None, list[str]] = {}
            for selection_id, (selection, _) in selections.items():
                prior = selection["prior_selection_ref"]
                prior_id = None if prior is None else prior["id"]
                if prior is not None and (prior_id not in selections or selections[prior_id][1] != prior):
                    raise ContractError("HV2-INTENT-SELECTION-CHAIN", selection_id)
                children.setdefault(prior_id, []).append(selection_id)
            if len(children.get(None, [])) != 1 or any(len(values) > 1 for values in children.values()):
                raise ContractError("HV2-INTENT-SELECTION-CHAIN", "fork-or-root")
            tips = [selection_id for selection_id in selections if selection_id not in children]
            if len(tips) != 1:
                raise ContractError("HV2-INTENT-SELECTION-CHAIN", "tip")
            tip_id = tips[0]
            if current is None:
                pending_selection_ids = sorted(selections)
            else:
                current_id = current["selection_ref"]["id"]
                current_selection = selections.get(current_id)
                if current_selection is None or current_selection[1] != current["selection_ref"]:
                    raise ContractError("HV2-INTENT-SELECTION-CHAIN", "current-ref")
                current_ref = current["selection_ref"]
                current_revision = current_selection[0]["revision_ref"]["id"]
                cursor = tip_id
                while cursor != current_id:
                    pending_selection_ids.append(cursor)
                    prior = selections[cursor][0]["prior_selection_ref"]
                    if prior is None:
                        raise ContractError("HV2-INTENT-SELECTION-CHAIN", "current-not-ancestor")
                    cursor = prior["id"]
        elif current is not None:
            raise ContractError("HV2-INTENT-SELECTION-CHAIN", "current-without-selection")
        selected_acceptance_ids = {selection[0]["acceptance_ref"]["id"] for selection in selections.values()}
        pending_acceptance_ids = sorted(set(records["acceptances"]) - selected_acceptance_ids)
        classification = "partial" if pending_acceptance_ids or pending_selection_ids else "pass"
        return {
            "actionable": current_revision is not None,
            "authority_home_id": authority["authority_home_id"],
            "classification": classification,
            "current_accepted_revision_id": current_revision,
            "current_selection_ref": current_ref,
            "draft_revision_ids": sorted(records["drafts"]),
            "intent_id": intent_id,
            "pending_acceptance_ids": pending_acceptance_ids,
            "pending_selection_ids": sorted(pending_selection_ids),
        }

    def show(self, intent_id: str, revision_id: str) -> dict[str, Any]:
        authority = self._load_authority()
        records = self._records(intent_id, authority)
        if revision_id not in records["drafts"]:
            raise ContractError("HV2-INTENT-DRAFT", revision_id)
        draft, revision_ref = records["drafts"][revision_id]
        current = self._current(intent_id, authority)
        accepted = any(value[0]["revision_ref"] == revision_ref for value in records["acceptances"].values())
        current_revision = None
        current_ancestors: set[str] = set()
        if current is not None:
            current_selection = records["selections"].get(current["selection_ref"]["id"])
            if current_selection is None or current_selection[1] != current["selection_ref"]:
                raise ContractError("HV2-INTENT-CURRENT", intent_id)
            current_revision = current_selection[0]["revision_ref"]["id"]
            cursor: dict[str, str] | None = current["selection_ref"]
            while cursor is not None:
                current_ancestors.add(cursor["id"])
                cursor = records["selections"][cursor["id"]][0]["prior_selection_ref"]
        selected_ids = {
            selection_id
            for selection_id, (selection, _) in records["selections"].items()
            if selection["revision_ref"] == revision_ref
        }
        if revision_id == current_revision:
            state = "accepted-current"
        elif selected_ids & current_ancestors:
            state = "accepted-superseded"
        elif selected_ids:
            state = "selection-pending"
        elif accepted:
            state = "accepted-unselected"
        else:
            state = "draft-unaccepted"
        return {
            "actionable": state == "accepted-current",
            "draft": draft,
            "revision_ref": revision_ref,
            "route": draft["route"],
            "state": state,
            "unresolved": [gap for gap in draft["gaps"] if gap["status"] == "unresolved"],
        }
