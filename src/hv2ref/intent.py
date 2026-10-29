from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .errors import ContractError, InjectedCrash


INTENT_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
FACET_KEYS = {
    "acceptance_oracle",
    "destination",
    "expected_outcome",
    "forbidden_scope",
    "goal",
    "scope",
}
STATEMENT_KINDS = {"assumption", "fact", "human-decision", "unknown"}


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


def validate_delegation(value: Any, authority: str, owner: str) -> dict[str, Any]:
    """Exact ordinary accept capability; actor labels do not authenticate callers."""
    from .work import _keys, _require, _identifier, _qualified, _path_set, _text
    _keys(value, {"action", "delegate_actor", "execution_mode", "scope", "work"})
    _text(owner); _identifier(value["delegate_actor"])
    delegate = value["delegate_actor"]
    _require(delegate != owner and (not owner.isascii() or delegate.lower() != owner.lower()),
             "delegate and Owner must be distinct")
    _require(value["action"] == "accept" and value["execution_mode"] == "isolated-worktree",
             "unsupported delegated action or execution mode")
    _qualified(value["work"], kind="work")
    _require(value["work"]["authority_home_id"] == authority, "cross-home delegation")
    _require(isinstance(value["scope"], list) and bool(value["scope"]), "delegation scope must be nonempty")
    _path_set(value["scope"])
    return value


def workspace_intent_graph(data: dict[str, Any], intent_id: str, authority: str) -> dict[str, Any]:
    """Validate all new-format intent records, including unpublished prefixes."""
    from .work import _require, _keys, _identifier, _text, _resolve, _digest, validate_ticket
    identity = data.get("identity.json")
    if identity is None:
        raise ContractError("HV2-INTENT-RECORD", "partial intent identity")
    base = {"record_type", "schema_version", "authority_home_id", "intent_id"}
    _keys(identity, base)
    _require(identity["record_type"] == "intent-identity" and identity["authority_home_id"] == authority and identity["intent_id"] == intent_id and type(identity["schema_version"]) is int and identity["schema_version"] == 1, "intent identity differs from root")
    drafts, acceptances, selections = [{p.split("/")[1][:-5]: v for p, v in data.items() if p.startswith(folder + "/")} for folder in ("drafts", "acceptances", "selections")]
    for group, kind, id_key, extra in [
        (drafts, "intent-draft", "revision_id", {"acceptance_authority", "actor", "facets", "gaps", "statements", "observed_at", "prior_revision_ref", "revision_id", "route", "sequence"}),
        (acceptances, "intent-acceptance", "acceptance_id", {"acceptance_id", "confirmation"}),
        (selections, "intent-selection", "selection_id", {"acceptance_ref", "prior_selection_ref", "revision_ref", "selection_id"}),
    ]:
        _require(len({key.casefold() for key in group}) == len(group), "intent record ID case collision")
        for key, record in group.items():
            version = record.get("schema_version") if isinstance(record, dict) else None
            _require(type(version) is int and version in ((1, 2, 3) if kind == "intent-draft" else (1,)), "unsupported intent record version")
            _keys(record, base | extra | ({"composition"} if version == 2 else {"acceptance_delegation"} if version == 3 else set()))
            _require(record["record_type"] == kind and record[id_key] == key and record["authority_home_id"] == authority and record["intent_id"] == intent_id, "intent record type/identity mismatch")
            if version == 2:
                from .umbrella import validate_composition
                validate_composition(record["composition"], authority)
            if version == 3:
                validate_delegation(record["acceptance_delegation"], authority, record["acceptance_authority"])
            _identifier(key)
    for draft in drafts.values():
        _require(type(draft["sequence"]) is int and draft["sequence"] > 0, "draft sequence must be a positive integer")
    _require(len({d["sequence"] for d in drafts.values()}) == len(drafts), "draft history must be linear with one root")
    for draft in drafts.values():
        for key in ("acceptance_authority", "actor", "observed_at"):
            _text(draft[key])
        facets = _exact_keys(draft["facets"], FACET_KEYS, "HV2-INTENT-FACETS")
        for name, value in facets.items(): _validate_facet(name, value)
        _require(isinstance(draft["statements"], list), "intent statements array")
        for statement in draft["statements"]:
            _keys(statement, {"kind", "owner", "text"})
            _require(statement["kind"] in STATEMENT_KINDS, "unknown statement kind")
            _text(statement["owner"]); _text(statement["text"])
        gaps = draft["gaps"]
        _require(isinstance(gaps, list), "gap array required")
        edges = {}
        for gap in gaps:
            _keys(gap, {"depends_on", "gap_id", "material", "owner", "status"})
            _identifier(gap["gap_id"]); _text(gap["owner"])
            _require(type(gap["material"]) is bool and gap["status"] in ("resolved", "unresolved"), "invalid gap")
            _require(isinstance(gap["depends_on"], list), "gap dependencies array")
            for dep in gap["depends_on"]: _identifier(dep)
            _require(len(set(gap["depends_on"])) == len(gap["depends_on"]) and gap["gap_id"] not in edges, "duplicate gap/dependency")
            edges[gap["gap_id"]] = set(gap["depends_on"])
        _require(all(deps <= edges.keys() for deps in edges.values()), "missing gap dependency")
        todo = dict(edges)
        while todo:
            leaves = {k for k, v in todo.items() if not v}
            _require(bool(leaves), "gap cycle")
            todo = {k: v - leaves for k, v in todo.items() if k not in leaves}
        unresolved = {g["gap_id"] for g in gaps if g["material"] and g["status"] == "unresolved"}
        route = "dependency-ordered-clarification" if any(edges[g] & unresolved for g in unresolved) else "bounded-clarification" if unresolved else "direct-entry"
        _require(draft["route"] == route, "intent route does not follow gap graph")
        prior = _resolve(drafts, draft["prior_revision_ref"], nullable=True)
        _require(type(draft["sequence"]) is int and draft["sequence"] == (prior["sequence"] + 1 if prior else 1), "draft sequence/prior mismatch")
    _require(len({d["acceptance_authority"] for d in drafts.values()}) <= 1, "intent acceptance authority cannot change")
    request_ids = set()
    for acceptance in acceptances.values():
        t = validate_ticket(acceptance["confirmation"])
        _require(t["object"] == {"authority_home_id": authority, "kind": "intent", "id": intent_id}, "intent ticket object mismatch")
        _require(acceptance["acceptance_id"] == "acceptance-" + _digest(t), "acceptance ID does not bind ticket")
        draft = _resolve(drafts, t["target_revision_ref"])
        if not any(facet["status"] == "known" for facet in draft["facets"].values()):
            raise ContractError("HV2-INTENT-VACUOUS-ACCEPTANCE", draft["revision_id"])
        _require(t["actor"] == draft["acceptance_authority"] and not any(g["material"] and g["status"] == "unresolved" for g in draft["gaps"]), "intent cannot be accepted")
        prior_selection = _resolve(selections, t["expected_selection_ref"], nullable=True)
        from .umbrella import check_intent_role
        check_intent_role(_resolve(drafts, prior_selection["revision_ref"]) if prior_selection else None, draft)
        _require(t["request_id"] not in request_ids, "intent request ID reused")
        request_ids.add(t["request_id"])
    children = {}; selected_acceptances = set()
    for key, selection in selections.items():
        prior = _resolve(selections, selection["prior_selection_ref"], nullable=True)
        parent = prior["selection_id"] if prior else None
        _require(parent not in children, "intent selection fork")
        children[parent] = key
        acceptance = _resolve(acceptances, selection["acceptance_ref"])
        _resolve(drafts, selection["revision_ref"])
        _require(acceptance["acceptance_id"] not in selected_acceptances, "acceptance selected twice")
        selected_acceptances.add(acceptance["acceptance_id"])
        ticket = acceptance["confirmation"]
        _require(ticket["expected_selection_ref"] == selection["prior_selection_ref"] and ticket["target_revision_ref"] == selection["revision_ref"], "intent selection differs from accepted revision")
    chain = []; node = children.get(None)
    while node is not None:
        _require(node not in chain, "intent selection cycle")
        chain.append(node); node = children.get(node)
    _require(len(chain) == len(selections), "disconnected intent selection")

    current = data.get("current.json")
    current_id = None
    if current is not None:
        _keys(current, base | {"selection_ref"})
        _require(current["record_type"] == "intent-current" and type(current["schema_version"]) is int and current["schema_version"] == 1 and current["authority_home_id"] == authority and current["intent_id"] == intent_id, "invalid intent selector")
        current_id = _resolve(selections, current["selection_ref"])["selection_id"]
    pending_selections = chain[chain.index(current_id) + 1:] if current_id else chain[:]
    pending_acceptances = set(acceptances) - selected_acceptances
    _require(len(pending_selections) <= 1 and len(pending_acceptances) <= 1, "conflicting pending intent publication")
    _require(not (pending_selections and pending_acceptances), "pending intent selection and new acceptance conflict")
    for aid in pending_acceptances:
        _require(acceptances[aid]["confirmation"]["expected_selection_ref"] == (current["selection_ref"] if current else None), "pending intent acceptance is stale")
    return {"data": data, "identity": identity, "drafts": drafts, "acceptances": acceptances, "selections": selections, "chain": chain, "current": current, "pending_acceptances": sorted(pending_acceptances), "pending_selections": pending_selections}


def read_workspace_intent_graph(target: Path, intent_id: str, *, _topology_observation=None) -> dict[str, Any]:
    from .work import _authority_directory, _record_tree, _visible_truth, _require
    from .workspace import safe_target
    target = safe_target(target)
    try:
        home, authority = _authority_directory(target, "intents", intent_id)
        folders = {"drafts", "acceptances", "selections"}
        data = _record_tree(home, folders)
        _require(data == _record_tree(home, folders), "unstable intent observation")
        truth_paths = [(home.relative_to(target) / path).as_posix() for path in data]
        if _topology_observation is None:
            _visible_truth(target, truth_paths)
        else:
            _visible_truth(target, truth_paths, _topology_observation=_topology_observation)
        return workspace_intent_graph(data, intent_id, authority)
    except PermissionError as exc:
        raise ContractError("HV2-INTENT-UNAVAILABLE", "Intent read permission denied: " + str(target / ".hrn/intents" / intent_id)) from exc
    except (OSError, ValueError, RecursionError) as exc:
        raise ContractError("HV2-INTENT-RECORD", "workspace intent unavailable or unstable: " + str(target / ".hrn/intents" / intent_id)) from exc


def read_workspace_intent(target: Path, intent_id: str, expected_ref: dict[str, Any], *, require_current: bool = True) -> dict[str, Any]:
    """Resolve an exact published acceptance; latest intent is required for new authority."""
    from .work import _resolve, validate_intent_ref, _live_external_refs
    validate_intent_ref(expected_ref)
    graph = read_workspace_intent_graph(target, intent_id)
    observed, bound = _resolve_workspace_intent(graph, intent_id, expected_ref, require_current=require_current)
    if require_current:
        _live_external_refs(target, _resolve(graph["acceptances"], bound["acceptance_ref"])["confirmation"], None)
    return observed


def _resolve_workspace_intent(graph: dict[str, Any], intent_id: str, expected_ref: dict[str, Any],
                              *, require_current: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    """Resolve each exact binding against a verified graph; perform no live reads."""
    from .work import _require, _resolve, validate_intent_ref
    validate_intent_ref(expected_ref)
    current = graph["current"]
    _require(current is not None, "intent has no published acceptance")
    if require_current:
        _require(not graph["pending_acceptances"] and not graph["pending_selections"], "intent publication pending")
        _require(expected_ref["selection_ref"] == current["selection_ref"], "stale intent selection")
    bound = _resolve(graph["selections"], expected_ref["selection_ref"])
    _require(graph["chain"].index(bound["selection_id"]) <= graph["chain"].index(current["selection_ref"]["id"]), "intent reference is not yet published")
    _require(expected_ref == {"authority_home_id": graph["identity"]["authority_home_id"], "kind": "intent", "id": intent_id, "revision_ref": bound["revision_ref"], "acceptance_ref": bound["acceptance_ref"], "selection_ref": expected_ref["selection_ref"]}, "intent binding mismatch")
    draft = _resolve(graph["drafts"], bound["revision_ref"])
    return {"acceptance_authority": draft["acceptance_authority"], "composition": draft.get("composition"), "acceptance_delegation": draft.get("acceptance_delegation"), "intent_ref": expected_ref, "is_current": expected_ref["selection_ref"] == current["selection_ref"]}, bound


def workspace_intents(target: Path, *, _graph_reader=None) -> dict[str, Any]:
    from .workspace import _require_kind
    from .work import _require
    root = target / ".hrn/intents"
    if not root.exists() and not root.is_symlink(): return {}
    _require_kind(root, True)
    names = [p.name for p in root.iterdir()]
    _require(len({n.casefold() for n in names}) == len(names), "intent ID case collision")
    return {name: (read_workspace_intent_graph(target, name) if _graph_reader is None else _graph_reader(name)) for name in names}


def require_no_pending_intents(target: Path, *, except_id: str | None = None) -> dict[str, Any]:
    from .work import _require
    graphs = workspace_intents(target)
    for key, graph in graphs.items():
        if key != except_id:
            _require(not graph["pending_acceptances"] and not graph["pending_selections"], "pending intent publication blocks mutation")
    return graphs


class WorkspaceIntentStore:
    """Internal new-format intent writer. Runtime verification remains a required seam."""

    def __init__(self, target: Path, runtime_check=None):
        from .work import WorkStore
        self.work_store = WorkStore(target, runtime_check)
        self.target = self.work_store.target

    def _guard_pending(self, intent_id: str | None = None) -> dict[str, Any]:
        from .work import _require
        from .continuation import require_no_pending
        works = self.work_store._all()
        require_no_pending(self.target, works=works)
        for graph in works.values():
            _require(not graph["pending_decisions"] and not graph["pending_selections"], "pending Work blocks intent mutation")
        return require_no_pending_intents(self.target, except_id=intent_id)

    def publish_draft(self, draft: dict[str, Any], *, inject_at: str | None = None) -> dict[str, Any]:
        from .workspace import writer_guard, _file_json, validate_format, _durable_directory
        from .work import _require, _identifier, _canonical_record_bytes, _publish_immutable, _publish_object_home, _preflight_publication
        from .errors import InjectedCrash
        _require(inject_at in (None, "after-staged-identity", "after-home", "after-draft"), "unknown intent crash point")
        _require(isinstance(draft, dict), "intent draft object required")
        iid = draft.get("intent_id"); rid = draft.get("revision_id")
        _identifier(iid); _identifier(rid)
        _canonical_record_bytes(draft)
        with writer_guard(self.target):
            runtime = self.work_store._runtime()
            authority = validate_format(_file_json(self.target / ".hrn/format.json"))["authority_home_id"]
            identity = {"record_type": "intent-identity", "schema_version": 1, "authority_home_id": authority, "intent_id": iid}
            graphs = workspace_intents(self.target)
            graph = graphs.get(iid)
            if graph and rid in graph["drafts"]:
                _require(graph["drafts"][rid] == draft, "draft ID reused with changed bytes")
                return graph  # Immutable replay cannot change authority or selection.
            self._guard_pending()
            data = dict(graph["data"]) if graph else {"identity.json": identity}
            data["drafts/" + rid + ".json"] = draft
            workspace_intent_graph(data, iid, authority)
            if draft["schema_version"] == 2: self.work_store._umbrella_runtime(runtime)
            if draft["schema_version"] == 3: self.work_store._delegation_runtime(runtime)
            _preflight_publication(self.target, [f".hrn/intents/{iid}/identity.json", f".hrn/intents/{iid}/drafts/{rid}.json"])
            self.work_store._runtime_equal(runtime)
            root = self.target / ".hrn/intents"; _durable_directory(root)
            _require(not any(p.name.casefold() == iid.casefold() and p.name != iid for p in root.iterdir()), "intent ID case alias")
            home = _publish_object_home(self.target, "intents", iid, identity, inject_at)
            _publish_immutable(home / "drafts" / (rid + ".json"), draft)
            if inject_at == "after-draft": raise InjectedCrash(inject_at)
            return read_workspace_intent_graph(self.target, iid)

    @staticmethod
    def _accepted_data(graph: dict[str, Any], ticket: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        from .work import _digest, record_ref, validate_ticket, _require
        validate_ticket(ticket)
        _require(ticket["object"]["kind"] == "intent", "intent acceptance ticket required")
        base = {k: graph["identity"][k] for k in ("schema_version", "authority_home_id", "intent_id")}
        acceptance = {**base, "record_type": "intent-acceptance", "acceptance_id": "acceptance-" + _digest(ticket), "confirmation": ticket}
        selection = {**base, "record_type": "intent-selection", "selection_id": "selection-" + _digest(ticket), "prior_selection_ref": ticket["expected_selection_ref"], "revision_ref": ticket["target_revision_ref"], "acceptance_ref": record_ref(acceptance, "acceptance_id")}
        data = dict(graph["data"])
        for path, record in (("acceptances/" + acceptance["acceptance_id"] + ".json", acceptance), ("selections/" + selection["selection_id"] + ".json", selection)):
            _require(path not in data or data[path] == record, "intent immutable record collision")
            data[path] = record
        workspace_intent_graph(data, base["intent_id"], base["authority_home_id"])
        return data, acceptance, selection

    def prepare(self, intent_id: str, revision_ref: dict[str, str], *, actor: str, reason: str, request_id: str, observed_at: str, document_refs: list | None = None, evidence_refs: list | None = None) -> dict[str, Any]:
        from .workspace import target_fingerprint
        from .work import _digest, _live_external_refs
        runtime = self.work_store._runtime()
        graph = read_workspace_intent_graph(self.target, intent_id)
        self._guard_pending(intent_id)
        ticket = {"record_type": "confirmation-ticket", "schema_version": 1, "authority_home_id": graph["identity"]["authority_home_id"], "object": {"authority_home_id": graph["identity"]["authority_home_id"], "kind": "intent", "id": intent_id}, "action": "accept", "actor": actor, "reason": reason, "request_id": request_id, "observed_at": observed_at, "target_fingerprint": target_fingerprint(self.target), "target_revision_ref": revision_ref, "expected_selection_ref": graph["current"]["selection_ref"] if graph["current"] else None, "intent_ref": None, "product_binding_ref": runtime["binding_ref"], "document_refs": document_refs if document_refs is not None else [], "evidence_refs": evidence_refs if evidence_refs is not None else [], "execution_mode": None, "supersedes_decision_ref": None}
        self._accepted_data(graph, ticket)
        if graph["drafts"][revision_ref["id"]]["schema_version"] == 2: self.work_store._umbrella_runtime(runtime)
        if graph["drafts"][revision_ref["id"]]["schema_version"] == 3: self.work_store._delegation_runtime(runtime)
        _live_external_refs(self.target, ticket, runtime["launcher_sha256"], verified_inventory_id=runtime.get("inventory_id"))
        return {"ticket": ticket, "confirm_token": _digest(ticket)[:16]}

    def apply(self, ticket: dict[str, Any], *, confirm_token: str, inject_at: str | None = None) -> dict[str, Any]:
        from .workspace import writer_guard, target_fingerprint
        from .work import _require, _digest, record_ref, validate_ticket, _publish_immutable, _publish_current, _canonical_record_bytes, _live_external_refs, _preflight_publication
        from .errors import InjectedCrash
        _require(inject_at in (None, "after-acceptance", "after-selection", "after-staged-current", "after-current"), "unknown intent crash point")
        validate_ticket(ticket)
        _require(ticket["object"]["kind"] == "intent", "intent ticket required")
        _require(confirm_token == _digest(ticket)[:16], "confirmation token mismatch")
        _require(ticket["target_fingerprint"] == target_fingerprint(self.target), "ticket target moved or differs")
        iid = ticket["object"]["id"]
        with writer_guard(self.target):
            runtime = self.work_store._runtime()
            graph = read_workspace_intent_graph(self.target, iid)
            aid = "acceptance-" + _digest(ticket)
            selected = [s for s in graph["selections"].values() if s["acceptance_ref"]["id"] == aid]
            if selected and selected[0]["selection_id"] not in graph["pending_selections"]:
                return graph  # No historical selection promotion and no content revalidation.
            self._guard_pending(iid)
            _require(runtime["binding_ref"] == ticket["product_binding_ref"], "active binding changed")
            expected = graph["current"]["selection_ref"] if graph["current"] else None
            _require(ticket["expected_selection_ref"] == expected, "stale intent confirmation")
            data, acceptance, selection = self._accepted_data(graph, ticket)
            if graph["drafts"][ticket["target_revision_ref"]["id"]]["schema_version"] == 2: self.work_store._umbrella_runtime(runtime)
            if graph["drafts"][ticket["target_revision_ref"]["id"]]["schema_version"] == 3: self.work_store._delegation_runtime(runtime)
            current = {**graph["identity"], "record_type": "intent-current", "selection_ref": record_ref(selection, "selection_id")}
            for value in (acceptance, selection, current): _canonical_record_bytes(value)
            _live_external_refs(self.target, ticket, runtime["launcher_sha256"], verified_inventory_id=runtime.get("inventory_id"))
            home = self.target / ".hrn/intents" / iid
            _preflight_publication(self.target, [f".hrn/intents/{iid}/acceptances/{aid}.json", f".hrn/intents/{iid}/selections/{selection['selection_id']}.json", f".hrn/intents/{iid}/current.json"])
            _publish_immutable(home / "acceptances" / (aid + ".json"), acceptance)
            if inject_at == "after-acceptance": raise InjectedCrash(inject_at)
            self.work_store._runtime_equal(runtime)
            _live_external_refs(self.target, ticket, runtime["launcher_sha256"], verified_inventory_id=runtime.get("inventory_id"))
            _publish_immutable(home / "selections" / (selection["selection_id"] + ".json"), selection)
            if inject_at == "after-selection": raise InjectedCrash(inject_at)
            _publish_current(self.target, home / "current.json", current, inject_at)
            if inject_at == "after-current": raise InjectedCrash(inject_at)
            return read_workspace_intent_graph(self.target, iid)
