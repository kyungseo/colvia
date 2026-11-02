"""Work-local follow-up choices. Publication never grants target execution authority."""
from __future__ import annotations

import copy
from datetime import datetime
import os
import re
import stat
import sys
from pathlib import Path
from typing import Any

from .errors import ContractError, InjectedCrash
from .jsonio import canonical_json_bytes, decode_json_bytes
from . import work
from .workspace import safe_target, target_fingerprint, writer_guard

NORMAL_LIMIT = 256
RECORD_LIMIT = 512
TOTAL_BYTES = 20 * 1024 * 1024
TICKET_BYTES = 24 * 1024
CHOICE_BYTES = 32 * 1024
SMALL_BYTES = 4 * 1024
DEPTH_LIMIT = 16
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}\Z")
_TIME = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z\Z")
_BASE = {"record_type", "schema_version", "authority_home_id", "work_id"}
_TICKET = {"record_type", "schema_version", "source",
           "expected_continuation_selection_ref", "action", "choice",
           "supersedes_choice_ref", "actor", "owner_statement", "reason",
           "request_id", "observed_at", "product_binding_ref",
           "target_fingerprint", "document_refs"}


def require(ok: bool, message: str, code: str = "HV2-CONTINUATION") -> None:
    if not ok:
        raise ContractError(code, message)


def exact(value: Any, keys: set[str]) -> dict:
    require(isinstance(value, dict) and set(value) == keys, "unknown or missing continuation fields")
    return value


def identifier(value: Any) -> None:
    require(isinstance(value, str) and _ID.fullmatch(value) is not None, "invalid continuation identifier")


def text(value: Any, limit: int = 2048) -> None:
    require(isinstance(value, str) and "\x00" not in value, "invalid continuation text")
    try:
        size = len(value.encode("utf-8", errors="strict"))
    except UnicodeError as exc:
        raise ContractError("HV2-CONTINUATION", "continuation text is not UTF-8") from exc
    require(1 <= size <= limit, "continuation text size exceeded")


def bounded_bytes(value: Any, limit: int) -> bytes:
    raw = canonical_json_bytes(value)
    require(len(raw) <= limit, "continuation byte limit exceeded")
    decode_json_bytes(raw, require_canonical=True)
    stack = [(value, 1)]
    while stack:
        item, depth = stack.pop()
        require(depth <= DEPTH_LIMIT, "continuation depth limit exceeded")
        if isinstance(item, dict):
            stack.extend((v, depth + 1) for v in item.values())
        elif isinstance(item, list):
            stack.extend((v, depth + 1) for v in item)
    return raw


def reference(value: Any, *, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    exact(value, {"id", "sha256"})
    identifier(value["id"])
    require(work._sha(value["sha256"]), "invalid continuation reference digest")


def qualified(value: Any) -> None:
    exact(value, {"authority_home_id", "kind", "id"})
    identifier(value["authority_home_id"]); identifier(value["id"])
    require(value["kind"] == "work", "continuation target must be a Work")


def snapshot_shape(value: Any) -> dict:
    exact(value, {"object", "revision_ref", "selection_ref", "intent_ref"})
    qualified(value["object"])
    reference(value["revision_ref"]); reference(value["selection_ref"])
    work.validate_intent_ref(value["intent_ref"])
    require(value["object"]["authority_home_id"] == value["intent_ref"]["authority_home_id"],
            "Work snapshot and intent have different homes")
    return value


def validate_ticket(value: Any) -> dict:
    exact(value, _TICKET)
    require(value["record_type"] == "continuation-confirmation-ticket"
            and type(value["schema_version"]) is int and value["schema_version"] == 1,
            "unsupported continuation ticket")
    snapshot_shape(value["source"])
    reference(value["expected_continuation_selection_ref"], nullable=True)
    reference(value["supersedes_choice_ref"], nullable=True)
    reference(value["product_binding_ref"])
    for key in ("actor",):
        text(value[key])
    for key in ("owner_statement", "reason"):
        text(value[key], 4096)
    identifier(value["request_id"])
    stamp = value["observed_at"]
    require(isinstance(stamp, str) and _TIME.fullmatch(stamp) is not None, "invalid UTC timestamp")
    try:
        datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise ContractError("HV2-CONTINUATION", "invalid UTC calendar timestamp") from exc
    require(work._sha(value["target_fingerprint"]), "invalid target fingerprint")
    refs = value["document_refs"]
    require(isinstance(refs, list) and len(refs) <= 16, "document reference limit exceeded")
    paths = []
    for ref in refs:
        exact(ref, {"path", "sha256", "role", "required"})
        path = work.project_path(ref["path"])
        require(len(path.encode("utf-8")) <= 1024 and path not in ("colvia", "hv2"),
                "managed launcher or oversized path cannot be document evidence")
        require(work._sha(ref["sha256"]) and type(ref["required"]) is bool, "invalid document reference")
        text(ref["role"])
        paths.append(path)
    work._path_set(paths)
    action = value["action"]
    require(action in ("select", "withdraw", "cancel-pending"), "unknown continuation action")
    choice = value["choice"]
    if action == "select":
        require(isinstance(choice, dict) and "kind" in choice, "selection requires a choice")
        kind = choice["kind"]
        if kind == "proposal":
            exact(choice, {"kind", "goal", "scope", "next_step", "decision_needed"})
            for key in ("goal", "scope", "next_step", "decision_needed"):
                text(choice[key], 4096)
        elif kind == "work":
            exact(choice, {"kind", "target"})
            snapshot_shape(choice["target"])
            require(choice["target"]["object"]["authority_home_id"] == value["source"]["object"]["authority_home_id"],
                    "cross-home continuation is unsupported")
        else:
            exact(choice, {"kind"})
            require(kind == "none", "unknown continuation choice")
        require(value["supersedes_choice_ref"] is None, "normal select cannot supersede pending")
    elif action == "withdraw":
        require(choice is None and value["supersedes_choice_ref"] is None, "invalid withdrawal")
    else:
        require(choice is None and value["supersedes_choice_ref"] is not None and refs == [],
                "cancellation must identify one pending choice and carry no document refs")
    bounded_bytes(value, TICKET_BYTES)
    return value


def records(ticket: dict) -> tuple[dict, dict]:
    validate_ticket(ticket)
    source = ticket["source"]["object"]
    base = {"schema_version": 1, "authority_home_id": source["authority_home_id"], "work_id": source["id"]}
    digest = work._digest(ticket)
    choice = {**base, "record_type": "continuation-choice", "record_id": "choice-" + digest,
              "confirmation": copy.deepcopy(ticket)}
    selection = {**base, "record_type": "continuation-selection", "record_id": "selection-" + digest,
                 "parent_selection_ref": copy.deepcopy(ticket["expected_continuation_selection_ref"]),
                 "choice_ref": work.record_ref(choice)}
    bounded_bytes(choice, CHOICE_BYTES); bounded_bytes(selection, SMALL_BYTES)
    return choice, selection


def current_record(identity: dict, ref: dict | None) -> dict:
    return {"record_type": "continuation-current", "schema_version": 1,
            "authority_home_id": identity["authority_home_id"], "work_id": identity["work_id"],
            "selection_ref": copy.deepcopy(ref)}


def current_snapshot(graph: dict) -> dict:
    require(graph["current"] is not None, "source or target has no current Work selection")
    selected = work._resolve(graph["selections"], graph["current"]["selection_ref"])
    revision = work._resolve(graph["revisions"], selected["revision_ref"])
    return {"object": {"authority_home_id": graph["identity"]["authority_home_id"],
                       "kind": "work", "id": graph["identity"]["work_id"]},
            "selection_ref": copy.deepcopy(graph["current"]["selection_ref"]),
            "revision_ref": copy.deepcopy(selected["revision_ref"]),
            "intent_ref": copy.deepcopy(revision["intent_ref"])}


def resolve_snapshot(value: dict, graph: dict) -> dict:
    snapshot_shape(value)
    require(value["object"] == {"authority_home_id": graph["identity"]["authority_home_id"],
                                "kind": "work", "id": graph["identity"]["work_id"]},
            "snapshot Work identity mismatch")
    selection = work._resolve(graph["selections"], value["selection_ref"])
    revision = work._resolve(graph["revisions"], value["revision_ref"])
    require(selection["revision_ref"] == value["revision_ref"] and revision["intent_ref"] == value["intent_ref"],
            "snapshot revision/intent does not match selected Work")
    require(graph["current"] is not None, "snapshot Work has no current")
    ref = graph["current"]["selection_ref"]
    seen = set()
    while ref is not None:
        require(ref["id"] not in seen, "Work selection cycle")
        seen.add(ref["id"])
        if ref == value["selection_ref"]:
            return revision
        ref = work._resolve(graph["selections"], ref)["parent_selection_ref"]
    raise ContractError("HV2-CONTINUATION", "snapshot is not selected Work history")


def _tree(home: Path) -> dict[str, bytes]:
    from .workspace import _require_kind
    if not home.exists() and not home.is_symlink():
        return {}
    _require_kind(home, True)
    result = {}
    total = 0
    for member in home.iterdir():
        if member.name in ("choices", "selections"):
            _require_kind(member, True)
            members = list(member.iterdir())
            require(len(members) <= RECORD_LIMIT, "continuation record count exceeded")
            require(len({p.name.casefold() for p in members}) == len(members), "continuation filename alias")
            for path in members:
                require(path.suffix == ".json", "unknown continuation member")
                identifier(path.stem)
                result[path.relative_to(home).as_posix()] = _read_file(path, CHOICE_BYTES if member.name == "choices" else SMALL_BYTES)
        else:
            require(member.name == "current.json", "unknown continuation member: " + member.name)
            result[member.name] = _read_file(member, SMALL_BYTES)
        total = sum(len(data) for data in result.values())
        require(total <= TOTAL_BYTES, "continuation total byte limit exceeded")
    return result


def _read_file(path: Path, limit: int) -> bytes:
    from .workspace import _require_kind
    _require_kind(path, False)
    if sys.platform == "win32":
        # Reuse the binary native path/handle and repeated-content observation.
        # POSIX stat/fd stamps are not interchangeable on Windows.
        from .jsonio import windows_bounded_bytes
        data = windows_bounded_bytes(path, limit)
    else:
        before = path.lstat()
        require(stat.S_ISREG(before.st_mode) and before.st_size <= limit, "continuation file size/type invalid")
        def stamp(value):
            return (value.st_dev, value.st_ino, value.st_mode, value.st_size,
                    value.st_mtime_ns, value.st_ctime_ns, value.st_nlink)
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as handle:
            require(stamp(os.fstat(handle.fileno())) == stamp(before), "continuation input descriptor changed")
            data = handle.read(limit + 1)
            require(stamp(os.fstat(handle.fileno())) == stamp(before), "continuation descriptor changed while reading")
        require(len(data) <= limit and stamp(path.lstat()) == stamp(before), "continuation file changed while reading")
    value = decode_json_bytes(data, require_canonical=True)
    bounded_bytes(value, limit)
    return data


def graph(identity: dict, data: dict[str, dict], *, snapshot_resolver=None) -> dict:
    """Validate the complete bounded graph, including every unselected record."""
    choices, selections = {}, {}
    total = 0
    for path, value in data.items():
        category = path.split("/")[0]
        if path == "current.json":
            exact(value, _BASE | {"selection_ref"})
            require(value["record_type"] == "continuation-current", "wrong current record kind")
            reference(value["selection_ref"], nullable=True)
            limit = SMALL_BYTES
        elif category == "choices" and path.endswith(".json"):
            exact(value, _BASE | {"record_id", "confirmation"})
            expected, _ = records(value["confirmation"])
            require(value == expected, "choice identity or fields differ from exact ticket")
            require(path == "choices/" + value["record_id"] + ".json", "choice filename mismatch")
            require(value["confirmation"]["actor"] == identity["acceptance_authority"],
                    "only the source Owner may choose continuation")
            choices[value["record_id"]] = value
            limit = CHOICE_BYTES
        elif category == "selections" and path.endswith(".json"):
            exact(value, _BASE | {"record_id", "parent_selection_ref", "choice_ref"})
            require(value["record_type"] == "continuation-selection", "wrong selection record kind")
            identifier(value["record_id"])
            reference(value["choice_ref"]); reference(value["parent_selection_ref"], nullable=True)
            require(path == "selections/" + value["record_id"] + ".json", "selection filename mismatch")
            selections[value["record_id"]] = value
            limit = SMALL_BYTES
        else:
            raise ContractError("HV2-CONTINUATION", "unknown continuation record path")
        require(type(value["schema_version"]) is int and value["schema_version"] == 1,
                "unknown continuation schema")
        require(value["authority_home_id"] == identity["authority_home_id"] and value["work_id"] == identity["work_id"],
                "continuation directory identity mismatch")
        total += len(bounded_bytes(value, limit))
    require(total <= TOTAL_BYTES and len(choices) <= RECORD_LIMIT and len(selections) <= RECORD_LIMIT,
            "continuation collection limit exceeded")
    require(all(len({key.casefold() for key in entries}) == len(entries) for entries in (choices, selections)),
            "continuation record ID alias")
    current = data.get("current.json")
    require(current is not None or not choices and not selections, "unavailable-current: canonical current is missing")
    current_ref = current["selection_ref"] if current else None
    normal = [c for c in choices.values() if c["confirmation"]["action"] != "cancel-pending"]
    require(len(normal) <= NORMAL_LIMIT, "normal operation quota exceeded")
    requests = set()
    cancelled = {}
    prior_normal = set()
    for choice in choices.values():
        ticket = choice["confirmation"]
        req = ticket["request_id"].casefold()
        require(req not in requests, "duplicate or aliased continuation request ID")
        requests.add(req)
        if snapshot_resolver is not None:
            snapshot_resolver(ticket["source"])
            if ticket["action"] == "select" and ticket["choice"]["kind"] == "work":
                snapshot_resolver(ticket["choice"]["target"])
        if ticket["action"] == "cancel-pending":
            original = work._resolve(choices, ticket["supersedes_choice_ref"])
            old = original["confirmation"]
            require(old["action"] != "cancel-pending", "cannot cancel cancellation")
            require(original["record_id"] not in cancelled, "more than one cancellation")
            require(old["source"] == ticket["source"] and
                    old["expected_continuation_selection_ref"] == ticket["expected_continuation_selection_ref"],
                    "cancellation changed source or prior")
            require(old["product_binding_ref"] == ticket["product_binding_ref"] and
                    old["target_fingerprint"] == ticket["target_fingerprint"],
                    "cancellation changed binding/location")
            cancelled[original["record_id"]] = choice["record_id"]
        else:
            prior = work._digest(ticket["expected_continuation_selection_ref"])
            require(prior not in prior_normal, "competing normal choices at one prior")
            prior_normal.add(prior)
    cancelled_selections = set()
    for cid in cancelled:
        cancelled_selections.add("selection-" + work._digest(choices[cid]["confirmation"]))
    for selection in selections.values():
        choice = work._resolve(choices, selection["choice_ref"])
        _, expected = records(choice["confirmation"])
        require(selection == expected, "selection does not match exact choice")
        parent = selection["parent_selection_ref"]
        if parent is not None:
            work._resolve(selections, parent)
            require(parent["id"] not in cancelled_selections, "cancelled selection cannot be a parent")
    chain = []
    ref = current_ref
    while ref is not None:
        selection = work._resolve(selections, ref)
        require(ref["id"] not in chain and ref["id"] not in cancelled_selections, "invalid selected continuation chain")
        chain.append(ref["id"])
        ref = selection["parent_selection_ref"]
    chain.reverse()
    effective = None
    effective_ticket = None
    for sid in chain:
        ticket = work._resolve(choices, selections[sid]["choice_ref"])["confirmation"]
        if ticket["action"] == "select":
            effective, effective_ticket = ticket["choice"], ticket
        elif ticket["action"] == "withdraw":
            require(effective is not None, "withdrawal from undecided is invalid")
            effective, effective_ticket = None, None
        # cancellation advances current while retaining the prior effective evidence.
    pending = []
    for cid, choice in choices.items():
        if cid in cancelled:
            continue
        ticket = choice["confirmation"]
        sid = "selection-" + work._digest(ticket)
        if sid in chain:
            continue
        require(ticket["expected_continuation_selection_ref"] == current_ref, "unexplained continuation orphan/fork")
        pending.append(cid)
        if ticket["action"] == "withdraw":
            require(effective is not None, "already-undecided")
    require(len(pending) <= 1, "competing pending continuation operations")
    allowed = set(chain) | cancelled_selections | {"selection-" + work._digest(choices[cid]["confirmation"]) for cid in pending}
    require(set(selections) <= allowed, "unexplained continuation selection")
    usage = {"normal_limit": NORMAL_LIMIT, "normal_used": len(normal), "normal_remaining": NORMAL_LIMIT - len(normal)}
    return {"choices": choices, "selections": selections, "current": current, "chain": chain,
            "pending": pending[0] if pending else None, "cancelled": cancelled,
            "effective_choice": copy.deepcopy(effective), "effective_ticket": copy.deepcopy(effective_ticket),
            "usage": usage, "data": data}


def read_continuation(target: Path, work_id: str, *, _source_graph=None, _topology_observation=None,
                      _intent_graph_reader=None) -> dict:
    """Read without initialization, and never recursively expand target continuations."""
    target = safe_target(target)
    readers = {}
    if _topology_observation is not None:
        readers["_topology_observation"] = _topology_observation
    if _intent_graph_reader is not None:
        readers["_intent_graph_reader"] = _intent_graph_reader
    try:
        source = (_source_graph if _source_graph is not None else
                  work.read_work(target, work_id, _with_continuation=False, **readers))
        home, authority = work._authority_directory(target, "work", work_id)
        require(source["identity"]["authority_home_id"] == authority, "continuation home changed")
        raw = _tree(home / "continuation")
        data = {path: decode_json_bytes(value, require_canonical=True) for path, value in raw.items()}
        bases = {work_id: source}
        def resolve(value):
            wid = value["object"]["id"]
            if wid not in bases:
                bases[wid] = work.read_work(target, wid, _with_continuation=False, **readers)
            return resolve_snapshot(value, bases[wid])
        result = graph(source["identity"], data, snapshot_resolver=resolve)
        for wid, before in bases.items():
            after = work.read_work(target, wid, _with_continuation=False, **readers)
            require({k: v for k, v in before.items() if k != "continuation"} == after,
                    "source/target Work changed while reading continuation")
        require(raw == _tree(home / "continuation"), "continuation changed while reading")
        paths = [(home / "continuation" / path).relative_to(target).as_posix() for path in data]
        if paths:
            work._visible_truth(target, paths, _topology_observation=_topology_observation)
        return result
    except (OSError, ValueError, RecursionError) as exc:
        raise ContractError("HV2-CONTINUATION-UNAVAILABLE", "continuation is unreadable, malformed or unstable") from exc


def require_no_pending(target: Path, *, works: dict | None = None, except_operation: tuple[str, str] | None = None) -> dict:
    if works is None:
        works = work.WorkStore(target)._all()
    for wid, base in works.items():
        state = base.get("continuation")
        if state is None:
            state = read_continuation(target, wid, _source_graph=base)
        pending = state["pending"]
        require(pending is None or except_operation == (wid, pending),
                "continuation publication pending; recover or cancel that exact operation",
                "HV2-CONTINUATION-PENDING")
    return works


class ContinuationStore:
    """Installed Owner writer; runtime doubles are only an explicit test seam."""

    def __init__(self, target: Path, runtime_check=None):
        self.work_store = work.WorkStore(target, runtime_check)
        self.target = self.work_store.target

    def _runtime(self):
        runtime = self.work_store._runtime()
        require(runtime.get("inventory_id") in ("continuation-1", "windows-2", "official-execution-1", "official-execution-2"), "continuation writing requires a continuation-capable current runtime")
        return runtime

    def _observe(self):
        return self.work_store._all()

    def _guard(self, works, *, operation=None):
        from .intent import require_no_pending_intents
        require_no_pending_intents(self.target)
        for base in works.values():
            require(not base["pending_decisions"] and not base["pending_selections"], "pending Work blocks continuation")
        require_no_pending(self.target, works=works, except_operation=operation)

    def _check(self, ticket, works, runtime, *, existing=False):
        from .intent import read_workspace_intent
        wid = ticket["source"]["object"]["id"]
        require(wid in works, "source Work unavailable")
        base = works[wid]
        state = base["continuation"]
        require(ticket["actor"] == base["identity"]["acceptance_authority"], "source Owner authority required")
        resolve_snapshot(ticket["source"], base)
        require(runtime["binding_ref"] == ticket["product_binding_ref"], "continuation binding changed")
        require(target_fingerprint(self.target) == ticket["target_fingerprint"], "continuation target moved or differs")
        prior = state["current"]["selection_ref"] if state["current"] else None
        require(prior == ticket["expected_continuation_selection_ref"], "stale continuation current")
        choice, _ = records(ticket)
        require(choice["record_id"] not in state["cancelled"], "cancelled original cannot resume")
        if ticket["action"] == "cancel-pending":
            old = work._resolve(state["choices"], ticket["supersedes_choice_ref"])
            require(old["confirmation"]["action"] != "cancel-pending", "cannot cancel cancellation")
            require(ticket["source"] == old["confirmation"]["source"] and
                    ticket["expected_continuation_selection_ref"] == old["confirmation"]["expected_continuation_selection_ref"],
                    "cancellation changed original source/prior")
            require(runtime["binding_ref"] == old["confirmation"]["product_binding_ref"]
                    and ticket["target_fingerprint"] == old["confirmation"]["target_fingerprint"],
                    "original pending binding/location changed")
            require(state["pending"] in (old["record_id"], choice["record_id"]), "original choice is not pending")
            self._guard(works, operation=(wid, state["pending"]))
        else:
            self._guard(works, operation=(wid, choice["record_id"]) if existing else None)
            require(current_snapshot(base) == ticket["source"], "source Work selection changed")
            if ticket["action"] == "withdraw":
                require(state["effective_choice"] is not None, "already-undecided")
            if ticket["action"] == "select" and ticket["choice"]["kind"] == "work":
                selected = ticket["choice"]["target"]
                other = works.get(selected["object"]["id"])
                require(other is not None and current_snapshot(other) == selected, "target Work selection changed")
                read_workspace_intent(self.target, selected["intent_ref"]["id"], selected["intent_ref"], require_current=True)
            work._live_external_refs(self.target, {"document_refs": ticket["document_refs"], "evidence_refs": []},
                                     runtime["launcher_sha256"], verified_inventory_id=runtime.get("inventory_id"))
        for item in state["choices"].values():
            old = item["confirmation"]
            if old["request_id"].casefold() == ticket["request_id"].casefold():
                require(old == ticket, "request ID reused with different bytes")
        return base, state

    @staticmethod
    def _prospective(base, state, ticket):
        choice, selection = records(ticket)
        data = dict(state["data"])
        data.setdefault("current.json", current_record(base["identity"], None))
        for kind, record in (("choices", choice), ("selections", selection)):
            path = kind + "/" + record["record_id"] + ".json"
            require(path not in data or data[path] == record, "immutable continuation collision")
            data[path] = record
        # Validate both the interrupted prefix and the final state before first write.
        result = graph(base["identity"], data)
        data["current.json"] = current_record(base["identity"], work.record_ref(selection))
        graph(base["identity"], data)
        return choice, selection, result["usage"]

    def prepare(self, work_id: str, *, action: str, actor: str, owner_statement: str,
                reason: str, request_id: str, observed_at: str, choice: dict | None = None,
                document_refs: list | None = None, supersedes_choice_ref: dict | None = None) -> dict:
        runtime = self._runtime()
        works = self._observe()
        require(work_id in works, "source Work unavailable")
        base = works[work_id]; state = base["continuation"]
        source = current_snapshot(base)
        prior = state["current"]["selection_ref"] if state["current"] else None
        value = copy.deepcopy(choice)
        if isinstance(value, dict) and value.get("kind") == "work" and "target_work_id" in value:
            exact(value, {"kind", "target_work_id"})
            identifier(value["target_work_id"])
            require(value["target_work_id"] in works, "target Work unavailable")
            value = {"kind": "work", "target": current_snapshot(works[value["target_work_id"]])}
        if action == "cancel-pending":
            require(supersedes_choice_ref is not None, "cancellation requires exact pending choice")
            old = work._resolve(state["choices"], supersedes_choice_ref)["confirmation"]
            source = copy.deepcopy(old["source"])
            prior = copy.deepcopy(old["expected_continuation_selection_ref"])
        ticket = {"record_type": "continuation-confirmation-ticket", "schema_version": 1,
                  "source": source, "expected_continuation_selection_ref": prior,
                  "action": action, "choice": value, "supersedes_choice_ref": supersedes_choice_ref,
                  "actor": actor, "owner_statement": owner_statement, "reason": reason,
                  "request_id": request_id, "observed_at": observed_at,
                  "product_binding_ref": runtime["binding_ref"], "target_fingerprint": target_fingerprint(self.target),
                  "document_refs": copy.deepcopy(document_refs) if document_refs is not None else []}
        validate_ticket(ticket)
        cid = "choice-" + work._digest(ticket)
        self._check(ticket, works, runtime, existing=cid in state["choices"])
        _, _, prospective = self._prospective(base, state, ticket)
        return {"ticket": ticket, "ticket_sha256": work._digest(ticket), "confirm_token": work._digest(ticket)[:16],
                "usage": state["usage"], "prospective_usage": prospective}

    def apply(self, ticket: dict, *, confirm_token: str, inject_at: str | None = None) -> dict:
        from .workspace import _durable_directory
        validate_ticket(ticket)
        require(confirm_token == work._digest(ticket)[:16], "continuation confirmation token mismatch")
        require(inject_at in (None, "after-directories", "after-initial-current", "after-choice",
                              "after-selection", "after-staged-current", "after-current"), "unknown continuation crash point")
        choice, selection = records(ticket)
        wid = ticket["source"]["object"]["id"]
        with writer_guard(self.target):
            runtime = self._runtime(); works = self._observe()
            require(wid in works, "source Work unavailable")
            state = works[wid]["continuation"]
            require(ticket["target_fingerprint"] == target_fingerprint(self.target), "continuation target moved or differs")
            existing = state["choices"].get(choice["record_id"])
            if existing is not None:
                require(existing == choice, "immutable continuation collision")
                if choice["record_id"] in state["cancelled"]:
                    return {**state, "replay": "cancelled"}
                if selection["record_id"] in state["chain"]:
                    return {**state, "replay": "resolved"}
            base, state = self._check(ticket, works, runtime, existing=existing is not None)
            self._prospective(base, state, ticket)
            home = self.target / ".hrn/work" / wid / "continuation"
            paths = ["current.json", "choices/" + choice["record_id"] + ".json",
                     "selections/" + selection["record_id"] + ".json"]
            work._preflight_publication(self.target, [(home / p).relative_to(self.target).as_posix() for p in paths])
            def check():
                fresh_runtime = self._runtime()
                require(runtime == fresh_runtime, "continuation runtime changed")
                return self._check(ticket, self._observe(), fresh_runtime, existing=True)
            check()
            for directory in (home, home / "choices", home / "selections"):
                _durable_directory(directory)
            if inject_at == "after-directories":
                raise InjectedCrash(inject_at)
            if state["current"] is None:
                work._publish_immutable(home / "current.json", current_record(base["identity"], None))
            if inject_at == "after-initial-current":
                raise InjectedCrash(inject_at)
            check()
            work._publish_immutable(home / "choices" / (choice["record_id"] + ".json"), choice)
            if inject_at == "after-choice":
                raise InjectedCrash(inject_at)
            check()
            work._publish_immutable(home / "selections" / (selection["record_id"] + ".json"), selection)
            if inject_at == "after-selection":
                raise InjectedCrash(inject_at)
            check()
            work._publish_current(self.target, home / "current.json",
                                  current_record(base["identity"], work.record_ref(selection)), inject_at)
            if inject_at == "after-current":
                raise InjectedCrash(inject_at)
            return read_continuation(self.target, wid)
