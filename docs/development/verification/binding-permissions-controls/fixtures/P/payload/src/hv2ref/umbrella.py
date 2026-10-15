"""Pure same-home umbrella contracts over already validated authority graphs.

No filesystem access, current pointer, scheduler or acceptance writer lives here.
Callers still verify runtime, live bytes, parent baseline and human authority.
"""
from __future__ import annotations

import copy
from typing import Any

from .errors import ContractError
from .work import (_keys, _qualified, _require, _resolve, project_path,
                   validate_intent_ref, validate_ref)


def validate_composition(value: Any, authority: str, *, parent_work: str | None = None) -> dict:
    _keys(value, {"parent", "required_children"})
    _qualified(value["parent"], kind="work")
    _require(value["parent"]["authority_home_id"] == authority, "umbrella parent home differs")
    if parent_work is not None:
        _require(value["parent"]["id"] == parent_work, "umbrella parent Work differs")
    rows = value["required_children"]
    _require(isinstance(rows, list) and bool(rows), "umbrella requires nonempty child set")
    names = []
    for row in rows:
        _keys(row, {"work", "intent"})
        _qualified(row["work"], kind="work"); _qualified(row["intent"], kind="intent")
        _require(row["work"]["authority_home_id"] == row["intent"]["authority_home_id"] == authority,
                 "umbrella child home differs")
        _require(row["work"]["id"].casefold() != value["parent"]["id"].casefold(), "umbrella self child")
        names.append(row["work"]["id"])
    _require(len({name.casefold() for name in names}) == len(names), "umbrella child duplicate or case alias")
    _require(names == sorted(names, key=lambda s: s.encode("utf-8")), "umbrella children must be canonical")
    return value


def validate_evidence(value: Any, authority: str, *, submitted: bool) -> dict:
    _keys(value, {"children", "integration_document"})
    _require(isinstance(value["children"], list), "umbrella evidence children array required")
    names = []
    for row in value["children"]:
        _keys(row, {"work", "intent_ref", "selection_ref", "revision_ref", "decision_ref", "manifest_ref"})
        _qualified(row["work"], kind="work"); validate_intent_ref(row["intent_ref"])
        _require(row["work"]["authority_home_id"] == row["intent_ref"]["authority_home_id"] == authority,
                 "umbrella evidence home differs")
        for key in ("selection_ref", "revision_ref", "decision_ref", "manifest_ref"):
            validate_ref(row[key])
        _require(row["manifest_ref"]["id"] == row["manifest_ref"]["sha256"], "umbrella manifest ID must be digest")
        names.append(row["work"]["id"])
    _require(len({name.casefold() for name in names}) == len(names), "umbrella evidence duplicate or case alias")
    _require(names == sorted(names, key=lambda s: s.encode("utf-8")), "umbrella evidence must be canonical")
    if submitted:
        project_path(value["integration_document"])
    else:
        _require(value["integration_document"] is None, "umbrella baseline has result document")
    return value


def _published_work_selection(graph: dict, ref: dict) -> dict:
    selection = _resolve(graph["selections"], ref)
    current = graph["current"]
    _require(current is not None, "child has no published selection")
    cursor = _resolve(graph["selections"], current["selection_ref"])
    seen = set()
    while True:
        _require(cursor["record_id"] not in seen, "child selection cycle")
        seen.add(cursor["record_id"])
        if cursor == selection:
            return selection
        _require(cursor["parent_selection_ref"] is not None, "child selection is not yet published")
        cursor = _resolve(graph["selections"], cursor["parent_selection_ref"])


def _child_chain(composition: dict, declared: dict, evidence: dict,
                 works: dict, intents: dict, *, current: bool) -> None:
    wid = declared["work"]["id"]
    _require(evidence["work"] == declared["work"], "child evidence identity differs")
    _require(wid in works, "required child is unavailable")
    graph = works[wid]
    identity = graph["identity"]
    _require({"authority_home_id": identity["authority_home_id"], "kind": "work", "id": identity["work_id"]}
             == declared["work"], "child graph identity differs")
    selection = _published_work_selection(graph, evidence["selection_ref"])
    revision = _resolve(graph["revisions"], evidence["revision_ref"])
    decision = _resolve(graph["decisions"], evidence["decision_ref"])
    _resolve(graph["manifests"], evidence["manifest_ref"])
    for record in (selection, revision, decision):
        _require(record["authority_home_id"] == identity["authority_home_id"]
                 and record["work_id"] == wid, "foreign child chain member")
    ticket = decision["confirmation"]
    _require(selection["revision_ref"] == evidence["revision_ref"]
             and selection["decision_ref"] == evidence["decision_ref"]
             and ticket["action"] == "accept"
             and ticket["target_revision_ref"] == evidence["revision_ref"]
             and ticket["object"] == declared["work"]
             and ticket["intent_ref"] == evidence["intent_ref"]
             and revision["intent_ref"] == evidence["intent_ref"]
             and revision["result_refs"]["manifest"] == evidence["manifest_ref"], "child accepted chain differs")
    parents = [r["target"] for r in revision["relations"] if r["relation"] == "parent"]
    _require(parents == [composition["parent"]], "child must declare exactly this parent")
    ref = evidence["intent_ref"]
    _require({k: ref[k] for k in ("authority_home_id", "kind", "id")} == declared["intent"], "child intent identity differs")
    _require(ref["id"] in intents, "child intent unavailable")
    intent = intents[ref["id"]]
    _require(intent["identity"]["authority_home_id"] == ref["authority_home_id"]
             and intent["identity"]["intent_id"] == ref["id"], "child intent graph identity differs")
    bound = _resolve(intent["selections"], ref["selection_ref"])
    accepted = _resolve(intent["acceptances"], ref["acceptance_ref"])
    draft = _resolve(intent["drafts"], ref["revision_ref"])
    _require(bound["revision_ref"] == ref["revision_ref"] and bound["acceptance_ref"] == ref["acceptance_ref"]
             and accepted["confirmation"]["target_revision_ref"] == ref["revision_ref"], "child intent acceptance differs")
    _require(intent["current"] is not None, "child intent never selected")
    _require(intent["chain"].index(bound["selection_id"]) <= intent["chain"].index(intent["current"]["selection_ref"]["id"]),
             "child intent selection is not yet published")
    _require("composition" not in draft and revision["schema_version"] == 1, "nested umbrella unsupported")
    if current:
        _require(not graph["pending_decisions"] and not graph["pending_selections"], "child publication pending")
        _require(graph["current"]["selection_ref"] == evidence["selection_ref"] and graph["state"] == "completed", "child completion changed")
        _require(not intent["pending_acceptances"] and not intent["pending_selections"], "child intent pending")
        _require(intent["current"]["selection_ref"] == ref["selection_ref"], "child intent changed")


def capture(composition: dict, works: dict, intents: dict) -> dict:
    """Observe eligible direct children; missing/incomplete never becomes ready.

Inputs must come from strict graph readers. Required document bytes are checked
by the caller in the same guarded snapshot before publication/acceptance.
"""
    validate_composition(composition, composition["parent"]["authority_home_id"])
    captured, unavailable = [], []
    for declared in composition["required_children"]:
        wid = declared["work"]["id"]
        try:
            _require(wid in works and works[wid]["current"] is not None, "required child is unavailable")
            graph = works[wid]; selected = _resolve(graph["selections"], graph["current"]["selection_ref"])
            revision = _resolve(graph["revisions"], selected["revision_ref"])
            row = {"work": declared["work"], "intent_ref": revision["intent_ref"],
                   "selection_ref": graph["current"]["selection_ref"], "revision_ref": selected["revision_ref"],
                   "decision_ref": selected["decision_ref"], "manifest_ref": revision["result_refs"]["manifest"]}
            _require(row["decision_ref"] is not None, "child not accepted")
            _child_chain(composition, declared, row, works, intents, current=True)
            captured.append(copy.deepcopy(row))
        except ContractError as exc:
            unavailable.append({"work": copy.deepcopy(declared["work"]), "reason": str(exc)})
    return {"children": captured, "unavailable": unavailable}


def check_history(composition: dict, evidence: dict, works: dict, intents: dict, *, submitted: bool) -> None:
    """Check sealed reference chains; future child drift cannot revoke history."""
    authority = composition["parent"]["authority_home_id"]
    validate_composition(composition, authority); validate_evidence(evidence, authority, submitted=submitted)
    required = {row["work"]["id"]: row for row in composition["required_children"]}
    names = {row["work"]["id"] for row in evidence["children"]}
    _require(names <= required.keys(), "evidence has undeclared child")
    if submitted:
        _require(names == required.keys(), "required child evidence missing")
    for row in evidence["children"]:
        _child_chain(composition, required[row["work"]["id"]], row, works, intents, current=False)


def evaluate(composition: dict, evidence: dict, works: dict, intents: dict,
             *, document_refs: list, evidence_refs: list) -> dict:
    """Derive the reference predicate only; never grant parent acceptance.

Malformed graphs propagate failure. Normal unmet prerequisites return reasons.
The writer must additionally enforce parent baseline, live references, runtime,
permissions and exact content application, including on interruption retries.
"""
    try:
        check_history(composition, evidence, works, intents, submitted=True)
        captured = capture(composition, works, intents)
        _require(not captured["unavailable"], "required child is not currently eligible")
        _require(captured["children"] == evidence["children"], "captured child results changed")
        path = evidence["integration_document"]
        _require(any(r["path"] == path and r["required"] and r["role"] == "result" for r in document_refs),
                 "required integration result reference missing")
        _require(any(r["required"] and r["verification"] == "control-required" for r in evidence_refs),
                 "required execution evidence reference missing")
        return {"ready": True, "reasons": [], "checked_scope": "child-chain-and-reference-contract"}
    except ContractError as exc:
        return {"ready": False, "reasons": [str(exc)], "checked_scope": "child-chain-and-reference-contract"}


def check_intent_role(previous_accepted: dict | None, proposed: dict) -> None:
    """Preserve role across accepted revisions, never across orphan drafts.

The caller resolves previous_accepted through the acceptance/selection chain.
This helper must not be fed the most recent draft by sequence or filename.
"""
    if previous_accepted is not None and "composition" in previous_accepted:
        _require("composition" in proposed, "accepted umbrella intent cannot become ordinary")
        _require(proposed["composition"]["parent"] == previous_accepted["composition"]["parent"],
                 "accepted umbrella intent cannot change parent identity")


def check_baseline_binding(composition: dict | None, revision: dict, previous_selected: dict | None,
                           works: dict, intents: dict, *, current: bool) -> None:
    """Check the authority half of a parent baseline against strict input graphs.

The writer must pair this with existing control/manifest byte checks under its
shared guard. History uses current=False; publication, rebind acceptance and
result acceptance use current=True. Reject/revoke do not run the current gate.
Previous_selected is resolved from expected_prior_selection, not recency.
"""
    is_parent = revision["schema_version"] == 2
    if previous_selected is not None and previous_selected["schema_version"] == 2:
        _require(is_parent and composition is not None, "selected parent cannot become ordinary")
    _require(is_parent == (composition is not None), "Work schema and intent composition differ")
    if composition is None:
        return
    validate_composition(composition, revision["authority_home_id"], parent_work=revision["work_id"])
    evidence = revision["umbrella_evidence"]
    operation = revision["operation"]
    submitted = operation == "submit-result"
    check_history(composition, evidence, works, intents, submitted=submitted)
    if operation not in ("start", "rebind"):
        _require(previous_selected is not None and previous_selected["schema_version"] == 2,
                 "umbrella result needs a selected parent baseline")
        _require(evidence["children"] == previous_selected["umbrella_evidence"]["children"],
                 "child evidence differs from selected baseline; human rebind required")
    if not current:
        return
    if operation in ("start", "rebind"):
        _require(evidence["children"] == capture(composition, works, intents)["children"],
                 "parent baseline child capture changed")
    elif submitted:
        outcome = evaluate(composition, evidence, works, intents,
                           document_refs=revision["document_refs"], evidence_refs=revision["evidence_refs"])
        _require(outcome["ready"], "; ".join(outcome["reasons"]))


def bound_composition(revision: dict, intents: dict) -> dict | None:
    """Resolve composition from the exact accepted draft already bound by Work."""
    ref = revision["intent_ref"]
    _require(ref["id"] in intents, "Work intent unavailable")
    draft = _resolve(intents[ref["id"]]["drafts"], ref["revision_ref"])
    return draft.get("composition")


def prior_revision(revision: dict, graph: dict | None) -> dict | None:
    if revision["expected_prior_selection"] is None:
        return None
    _require(graph is not None, "prior parent Work unavailable")
    selection = _resolve(graph["selections"], revision["expected_prior_selection"])
    return _resolve(graph["revisions"], selection["revision_ref"])


def check_work_histories(works: dict, intents: dict) -> None:
    """Cross-check all parent evidence without imposing today's child state."""
    for graph in works.values():
        for revision in graph["revisions"].values():
            check_baseline_binding(bound_composition(revision, intents), revision,
                                   prior_revision(revision, graph), works, intents, current=False)
