"""Work-local follow-up choices. Publication never grants target execution authority."""
from __future__ import annotations

import copy
from contextlib import contextmanager
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


# Delivery uses the existing verified continuation module so old release
# inventories, rollback manifests and launchers keep their exact path sets.
def _delivery_require(condition, message):
    if not condition:
        raise ContractError("COLVIA-DELIVERY", message)


def _delivery_observe(target, wid):
    from .product import require_workspace_runtime
    from .intent import require_no_pending_intents
    identifier(wid)
    runtime = require_workspace_runtime(target)
    _delivery_require(runtime["inventory_id"] in ("continuation-1", "windows-2", "official-execution-2"),
                      "이 배포본에서는 작업을 맡길 수 없습니다.")
    store = work.WorkStore(target)
    graphs = store._all()
    require_no_pending_intents(target)
    require_no_pending(target, works=graphs)
    _delivery_require(wid in graphs, "지정한 Work를 찾을 수 없습니다.")
    graph = graphs[wid]
    _delivery_require(graph["state"] == "active" and graph["current"]
                      and not any(g["pending_decisions"] or g["pending_selections"] for g in graphs.values()),
                      "활성 작업과 미처리 결정을 확인해 주세요.")
    ref = graph["current"]["selection_ref"]
    revision = graph["revisions"][graph["selections"][ref["id"]]["revision_ref"]["id"]]
    store._intent(revision, graph["identity"])
    _delivery_require(revision["schema_version"] == 1 and revision["execution_context"]["mode"] == "local",
                      "이 기능은 로컬 일반 Work에서 사용할 수 있습니다.")
    from .intent import read_workspace_intent_graph
    from .view import _work_label
    iid = revision["intent_ref"]["id"]
    label = _work_label(wid, graph, {iid: read_workspace_intent_graph(target, iid)})
    return {"project": str(target), "work_id": wid, "label":label, "binding": runtime["binding_ref"],
            "home": graph["identity"]["authority_home_id"], "selection": ref,
            "intent": revision["intent_ref"], "scope": revision["scope"]}, graph


def _submission_manifest(target, payload, graph):
    if "manifest" in payload:  # Existing packets retain their original digest and replay rules.
        return payload["manifest"]
    revision = payload["revision"]
    selected = graph["current"]["selection_ref"]
    _delivery_require(revision["expected_prior_selection"] == selected, "제출 기준이 달라졌습니다.")
    baseline = work._resolve(graph["revisions"], work._resolve(graph["selections"], selected)["revision_ref"])
    _delivery_require(graph["state"] == "active" and graph["identity"]["work_type"] == "local-edit"
                      and baseline["operation"] in ("start", "rework")
                      and revision["intent_ref"]["id"] == graph["identity"]["work_id"]
                      and baseline["execution_context"] == revision["execution_context"] == {"mode": "local", "attempt_id": "ordinary"},
                      "일반 파일 작업의 현재 시작점과 제출 대상을 확인해 주세요.")
    before = work._resolve(graph["manifests"], baseline["result_refs"]["manifest"])["result"]
    runtime = work.WorkStore(target)._runtime()
    live = work.snapshot(target, verified_launcher_sha256=runtime["launcher_sha256"],
                         verified_inventory_id=runtime.get("inventory_id"))
    manifest = work.make_manifest(before, live, scope=revision["scope"])
    _delivery_require(bool(manifest["changes"]), "제출할 파일 변경이 없습니다.")
    work._ordinary_manifest_size(manifest)
    digest = work._digest(manifest)
    _delivery_require(revision["result_refs"]["manifest"] == {"id": digest, "sha256": digest},
                      "검토한 뒤 파일이 달라졌습니다. 현재 변경을 다시 확인해 주세요.")
    return manifest


def _delivery_validate(target, request):
    from time import time
    fields = {"work_id", "action", "payload", "expires", "ask", "notify"}
    if isinstance(request, dict) and "detail_required" in request:
        fields.update(("detail_required", "receiver_at_preview"))
        _delivery_require(request["detail_required"] is True and request.get("notify") is True
                          and type(request.get("receiver_at_preview")) is bool and request.get("action") == "submit", "결과 상세 알림 요청을 확인해 주세요.")
    exact(request, fields)
    wid, action, payload = request["work_id"], request["action"], request["payload"]
    _delivery_require(type(request["expires"]) is int and time() < request["expires"] <= time()+86400,
                      "24시간 이내의 유효 기한을 지정해 주세요.")
    _delivery_require(type(request["ask"]) is bool and type(request["notify"]) is bool, "안내 옵션을 확인해 주세요.")
    observed, graph = _delivery_observe(target, wid)
    if action == "summary":
        _delivery_require(payload is None, "작업 요약에는 추가 입력이 필요하지 않습니다.")
    elif action == "submit":
        keys = {"identity","revision","selection_id","operation_id"}
        compact = isinstance(payload, dict) and "manifest" not in payload
        if compact:
            _delivery_require(request.get("detail_required") is True, "결과 상세 제출 경로를 확인해 주세요.")
        exact(payload, keys if compact else keys | {"manifest"})
        revision = work.validate_work_record(payload["revision"])
        for field in ("selection_id","operation_id"):
            identifier(payload[field])
        _delivery_require(payload["identity"] == graph["identity"] and revision["work_id"] == wid
                          and revision["schema_version"] == 1 and revision["operation"] == "submit-result"
                          and revision["expected_prior_selection"] == observed["selection"]
                          and revision["intent_ref"] == observed["intent"] and revision["scope"] == observed["scope"]
                          and revision["execution_context"]["mode"] == "local",
                          "현재 Work의 승인된 범위와 제출 결과를 대조해 주세요.")
        manifest = _submission_manifest(target, payload, graph)
        if not compact:
            work.validate_manifest(manifest, scope=revision["scope"])
    elif action == "execute":
        from .product import require_workspace_runtime
        _delivery_require(require_workspace_runtime(target)["inventory_id"] == "official-execution-2",
                          "공식 문서 실행은 해당 macOS 배포본에서 사용할 수 있습니다.")
        from .official_entry import prepare
        exact(payload, {"spec","confirm_token"})
        spec = payload["spec"]
        _delivery_require(isinstance(spec, dict) and isinstance(spec.get("request"), dict) and isinstance(payload["confirm_token"],str), "공식 실행 미리보기를 확인해 주세요.")
        _delivery_require(spec["request"].get("work_id") == wid and spec.get("target") == str(target)
                          and type(spec["request"].get("expires_wall_ns")) is int
                          and spec["request"]["expires_wall_ns"] <= request["expires"] * 10**9,
                          "공식 실행의 Work·프로젝트·기한을 확인해 주세요.")
        checked = prepare(target, spec["request"])
        _delivery_require(checked["spec"] == spec and checked["confirm_token"] == payload["confirm_token"],
                          "공식 실행 미리보기가 달라졌습니다.")
    else:
        _delivery_require(False, "선택할 수 있는 단계는 요약, 준비한 결과 제출, 공식 문서 실행입니다.")
    plan = {"version": 1, "route": "local-work-inbox", "source": observed, "request": request}
    if len(canonical_json_bytes(plan)) > 1024 * 1024:
        message = "맡길 요청이 1 MiB를 넘습니다."
        if request.get("detail_required"):
            message += " 초안은 그대로입니다. 알림 없이 검토용으로 제출할 수 있습니다."
        _delivery_require(False, message)
    return plan


def _delivery_db(target, *, create=False, read=False):
    from .workspace import delivery_folder
    import sqlite3
    # Keep the local mailbox outside all project snapshots and rollback inventories.
    folder = delivery_folder(target)
    if not os.path.lexists(folder) and not create:
        return None
    if create:
        folder.mkdir(mode=0o700, exist_ok=True)
    def plain(p, is_dir):
        info = p.lstat()
        return ((stat.S_ISDIR(info.st_mode) if is_dir else stat.S_ISREG(info.st_mode) and info.st_nlink == 1)
                and not (getattr(info, "st_file_attributes", 0) & 0x400)
                and (os.name == "nt" or (info.st_uid == os.getuid() and info.st_mode & 0o077 == 0)))
    _delivery_require(plain(folder, True) and folder.resolve() == folder, "수신함 위치와 접근 권한을 확인해 주세요.")
    p = folder / "inbox.db"
    if create:
        try: fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError: pass
        else: os.close(fd)
    if not os.path.lexists(p):
        return None
    _delivery_require(plain(p, False), "수신함 파일을 확인해 주세요.")
    for extra in folder.iterdir():
        _delivery_require(extra.name in ("inbox.db","inbox.db-journal","effect.lock") and plain(extra, False),
                          "수신함에 확인이 필요한 파일이 있습니다.")
    db = sqlite3.connect(p.as_uri() + ("?mode=ro" if read else "?mode=rw"), uri=True, timeout=5)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA trusted_schema=OFF")
    if create:
        with db:
            db.execute("""CREATE TABLE IF NOT EXISTS delivery
                (id TEXT PRIMARY KEY, wid TEXT NOT NULL, plan TEXT NOT NULL, phase TEXT NOT NULL,
                 epoch INTEGER NOT NULL, used INTEGER NOT NULL, expires INTEGER NOT NULL,
                 result TEXT, notice TEXT NOT NULL, changed INTEGER NOT NULL)""")
            db.execute("""CREATE UNIQUE INDEX IF NOT EXISTS one_active ON delivery ((1))
                WHERE phase IN ('queued','question','running','reconcile')""")
    return db


@contextmanager
def _delivery_fence(target):
    """Exclude a live effect while explicitly closing an uncertain receipt."""
    from .workspace import delivery_folder
    anchor = delivery_folder(target) / "effect.lock"
    fd = os.open(anchor, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        opened = os.fstat(fd)
        linked = anchor.lstat()
        _delivery_require(stat.S_ISREG(linked.st_mode) and os.path.samestat(opened, linked)
                          and opened.st_nlink == 1 and not (getattr(linked, "st_file_attributes", 0) & 0x400)
                          and (os.name == "nt" or (opened.st_uid == os.getuid() and opened.st_mode & 0o077 == 0)),
                          "실행 잠금 파일을 확인해 주세요.")
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise ContractError("COLVIA-DELIVERY", "실행 작업자가 사용 중입니다. 기존 결과를 확인해 주세요.") from error
        yield
    finally:
        os.close(fd)


def _delivery_close_token(row, now):
    if row["used"] == 1 and row["phase"] in ("running", "reconcile") and row["expires"] <= now:
        return work._digest(["close-unknown", row["id"], row["epoch"], row["phase"], row["expires"]])
    return None


def _delivery_effect_ids(request):
    payload = request["payload"]
    if request["action"] == "submit":
        return {("operation", payload["operation_id"]), ("selection", payload["selection_id"]),
                ("revision", payload["revision"]["record_id"])}
    if request["action"] == "execute":
        return {("grant", payload["confirm_token"])}
    return set()


def _delivery_command(target, key, epoch):
    import subprocess
    # Launcher rechecks the installed modules; the child receives no inherited terminal.
    launcher = str(target / "colvia")
    with open(launcher, "rb") as stream:
        use_shell_launcher = sys.platform == "darwin" and stream.readline(32) == b"#!/bin/sh\n"
    prefix = [launcher] if use_shell_launcher else [sys.executable, "-I", "-B", launcher]
    options = {"creationflags": subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
    return subprocess.Popen(prefix + ["handoff", "_step", key, "--epoch", str(epoch)], cwd=target,
                            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            close_fds=True, **options)


def _notice_store(store, *, create):
    """Private local click index, separate from project snapshots and approval records."""
    from contextlib import closing
    import sqlite3
    root = Path(store)
    _delivery_require(root.is_dir() and root.resolve(strict=True) == root, "알림 저장소를 확인해 주세요.")
    folder = root / "notification-events"
    if create:
        folder.mkdir(mode=0o700, exist_ok=True)
    def plain(path, directory):
        st = path.lstat()
        return ((stat.S_ISDIR(st.st_mode) if directory else stat.S_ISREG(st.st_mode) and st.st_nlink == 1)
                and not getattr(st, "st_file_attributes", 0) & 0x400
                and (os.name == "nt" or st.st_uid == os.getuid() and st.st_mode & 0o077 == 0))
    _delivery_require(plain(folder, True) and folder.resolve(strict=True) == folder, "알림 저장소를 확인해 주세요.")
    path = folder / "events.db"
    if create:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            pass
        else:
            os.close(fd)
    _delivery_require(plain(path, False) and all(
        f.name in ("events.db", "events.db-journal") and plain(f, False) for f in folder.iterdir()
    ), "알림 인덱스를 확인해 주세요.")
    conn = sqlite3.connect(path.as_uri() + ("?mode=rw" if create else "?mode=ro"), uri=True, timeout=3)
    try:
        conn.execute("PRAGMA trusted_schema=OFF")
        if create:
            conn.execute("CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, entry BLOB NOT NULL)")
        else:
            conn.execute("PRAGMA query_only=ON")
    except Exception:
        conn.close()
        raise
    return closing(conn)


def _notice_anchor(path):
    st = path.lstat()
    _delivery_require(stat.S_ISDIR(st.st_mode) and not getattr(st, "st_file_attributes", 0) & 0x400
                      and path.resolve(strict=True) == path, "프로젝트 위치를 확인해 주세요.")
    return [st.st_dev, st.st_ino]


def record_notification(store, target, db, key, epoch, phase):
    """Called after the receipt commit. Never copy a confirmation token into the OS index."""
    import hashlib
    import json
    import secrets
    row = db.execute("SELECT rowid AS receipt_number,* FROM delivery WHERE id=? AND epoch=? AND phase=?",
                     (key, epoch, phase)).fetchone()
    _delivery_require(row is not None and phase in ("question","done","stopped","reconcile"),
                      "알림을 요청한 접수 기록을 확인해 주세요.")
    receipt = _delivery_public(row)
    source = json.loads(row["plan"])["source"]
    target = safe_target(target)
    _delivery_require(str(target) == source["project"], "프로젝트 연결을 확인해 주세요.")
    entry = {"project":str(target), "anchor":_notice_anchor(target), "home":source["home"],
             "binding":source["binding"], "work":receipt["work_id"], "row":row["receipt_number"],
             "receipt_digest":hashlib.sha256(key.encode("ascii")).hexdigest(), "epoch":epoch,
             "phase":phase, "result_digest":work._digest(receipt["result"])}
    event_id = secrets.token_hex(16)
    with _notice_store(store, create=True) as conn, conn:
        conn.execute("INSERT INTO events(id,entry) VALUES (?,?)", (event_id, canonical_json_bytes(entry)))
    return event_id


@contextmanager
def _notice_pinned_project(target, anchor):
    """Pin the physical POSIX directory and check displayed authority through that handle."""
    from contextlib import ExitStack
    import hashlib
    if os.name == "nt":
        from . import jsonio
        with ExitStack() as held:
            pinned = set()
            def pin(directory):
                if directory in pinned:
                    return
                handle = jsonio._windows_open(directory, share=3)
                held.callback(jsonio._windows_api().CloseHandle, handle)
                state = jsonio._windows_handle_state(handle)
                _delivery_require(state["directory"], "작업 폴더를 확인해 주세요.")
                pinned.add(directory)
            for directory in reversed((target, *target.parents)):
                pin(directory)
            _delivery_require(_notice_anchor(target) == anchor, "프로젝트 연결을 확인해 주세요.")
            def windows_matches(parts, expected):
                path = target.joinpath(*parts)
                for directory in reversed(path.relative_to(target).parents):
                    pin(target / directory)
                data = jsonio.windows_bounded_bytes(path, jsonio.MAX_JSON_BYTES)
                _delivery_require(hashlib.sha256(data).hexdigest() == expected, "알림과 작업 기록을 대조해 주세요.")
            yield windows_matches
        return
    _delivery_require(os.name == "posix", "이 환경의 알림 상세 조회는 준비 중입니다.")
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY
    with ExitStack() as opened:
        root_fd = os.open(target, flags)
        opened.callback(os.close, root_fd)
        info = os.fstat(root_fd)
        _delivery_require([info.st_dev, info.st_ino] == anchor, "프로젝트 연결을 확인해 주세요.")
        def matches(parts, expected):
            with ExitStack() as dirs:
                parent = root_fd
                for component in parts[:-1]:
                    parent = os.open(component, flags, dir_fd=parent)
                    dirs.callback(os.close, parent)
                fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
                with os.fdopen(fd, "rb") as stream:
                    st = os.fstat(fd)
                    _delivery_require(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and
                                      hashlib.file_digest(stream, "sha256").hexdigest() == expected,
                                      "알림과 작업 기록을 대조해 주세요.")
        yield matches


def notification_detail(store, event_id):
    """Read exactly the clicked event. Do not switch to a newer submission or run project code."""
    import hashlib
    import json
    from contextlib import closing
    from .product import verify_workspace_product
    from .view import _work_state_label
    _delivery_require(isinstance(event_id, str) and re.fullmatch("[0-9a-f]{32}", event_id),
                      "알림 기록을 찾을 수 없습니다.")
    with _notice_store(store, create=False) as index:
        found = index.execute("SELECT entry FROM events WHERE id=?", (event_id,)).fetchone()
    _delivery_require(found is not None, "알림 기록을 찾을 수 없습니다.")
    entry = decode_json_bytes(found[0], require_canonical=True)
    target = safe_target(Path(entry["project"]))
    def verify():
        _delivery_require(str(target) == entry["project"] and _notice_anchor(target) == entry["anchor"]
                          and verify_workspace_product(target)["binding_ref"] == entry["binding"],
                          "알림을 보냈던 프로젝트 연결을 확인해 주세요.")
    verify()
    db = _delivery_db(target, read=True)
    _delivery_require(db is not None, "수신함 기록을 확인해 주세요.")
    with closing(db), _notice_pinned_project(target, entry["anchor"]) as matches:
        row = db.execute("SELECT * FROM delivery WHERE rowid=?", (entry["row"],)).fetchone()
        _delivery_require(row is not None and hashlib.sha256(row["id"].encode("ascii")).hexdigest()
                          == entry["receipt_digest"], "접수 기록이 달라졌습니다.")
        receipt = _delivery_public(row)
        plan = json.loads(row["plan"])
        source = plan["source"]
        _delivery_require(source["home"] == entry["home"] and source["binding"] == entry["binding"]
                          and source["project"] == str(target) and receipt["work_id"] == entry["work"]
                          and row["epoch"] >= entry["epoch"], "알림과 작업 기록을 대조해 주세요.")
        graph = work.read_work(target, entry["work"])
        _delivery_require(graph["identity"]["authority_home_id"] == entry["home"], "작업 연결을 확인해 주세요.")
        question = entry["phase"] == "question"
        selection = source["selection"]
        if question:
            _delivery_require(plan["request"]["ask"] and entry["epoch"] == 1, "질문 기록을 확인해 주세요.")
            message = "이 단계를 이어갈지 확인해 주세요."
        else:
            _delivery_require(isinstance(receipt.get("result"), dict) and isinstance(receipt["result"].get("message"), str)
                              and work._digest(receipt["result"]) == entry["result_digest"],
                              "이 알림의 결과를 확인할 수 없습니다.")
            message = receipt["result"]["message"]
            if "selection" in receipt["result"]:
                selection = receipt["result"]["selection"]
        ref = work._resolve(graph["selections"], selection)["revision_ref"]
        revision = work._resolve(graph["revisions"], ref)
        lines = [source["label"].replace("`", ""), "", "알림 당시의 " + ("질문" if question else "결과"), message]
        if not question:
            if receipt["result"].get("view"):
                lines.append(receipt["result"]["view"])
            else:
                lines += ["작업 범위 · " + ", ".join(revision["scope"])]
                lines.extend("결과 문서 · " + v["path"] for v in revision["document_refs"])
                lines.extend("검증 기록 · " + v["path"] for v in revision["evidence_refs"])
        submitted = not question and plan["request"]["action"] == "submit" and "selection" in receipt["result"]
        if submitted:
            lines.append("당시 제출 내용 · " + revision["next_action"])
        current_ref = work._resolve(graph["selections"], graph["current"]["selection_ref"])["revision_ref"]
        current_revision = work._resolve(graph["revisions"], current_ref)
        lines += ["", "현재 상태", _work_state_label(graph["state"])]
        if question:
            lines.append(receipt["message"] if receipt["status"] == "question"
                         else "이 질문은 닫혔습니다. " + receipt["message"])
        if not question and not submitted:
            lines.append("접수 상태 · " + receipt["message"])
            if graph["current"]["selection_ref"] != selection:
                lines.append("이 알림 이후 작업 기록이 갱신됐습니다.")
        if submitted and ref != current_ref:
            lines.append("이전 제출에 대한 알림입니다.")
        if graph["state"] == "review":
            lines.append("현재 검토할 내용 · " + current_revision["next_action"])
            lines.append("같은 프로젝트 대화에서 이 작업의 검토할 결과를 보여 달라고 하세요. 확인한 뒤 마무리하거나 고칠 부분을 알려 주세요.")
        elif graph["state"] == "active":
            lines.append("이어서 할 일 · " + current_revision["next_action"])
            lines.append("같은 프로젝트 대화에서 이 작업을 어디까지 했는지 물어보세요.")
        identifier(entry["work"])
        root = (".hrn", "work", entry["work"])
        matches((".hrn","product","binding.json"), entry["binding"]["sha256"])
        matches((*root,"identity.json"), work._digest(graph["identity"]))
        matches((*root,"current.json"), work._digest(graph["current"]))
        for selected, revision_ref in ((selection, ref), (graph["current"]["selection_ref"], current_ref)):
            matches((*root,"selections",selected["id"] + ".json"), selected["sha256"])
            matches((*root,"revisions",revision_ref["id"] + ".json"), revision_ref["sha256"])
    verify()
    return "\n".join(lines)


def windows_notice_identity(store):
    import uuid
    value = uuid.uuid5(uuid.NAMESPACE_URL, "colvia:work-notice:" + str(Path(store).resolve(strict=True)).casefold())
    return "Colvia.Work." + value.hex, "{" + str(value).upper() + "}"


def windows_notice_manager(store):
    import hashlib
    import winreg
    from .jsonio import windows_path_observation
    app, cls = windows_notice_identity(store)
    root = "Software" + chr(92) + "Classes" + chr(92)
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, root + "AppUserModelId" + chr(92) + app) as reg:
        _delivery_require(winreg.QueryValueEx(reg, "CustomActivator") == (cls, winreg.REG_SZ),
                          "알림 연결을 확인해 주세요.")
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, root + "CLSID" + chr(92) + cls + r"\LocalServer32") as reg:
        command, kind = winreg.QueryValueEx(reg, "")
    match = re.fullmatch(r'"([^"]+)" notice-activate', command)
    _delivery_require(kind == winreg.REG_SZ and match is not None, "알림 앱 등록을 확인해 주세요.")
    path = Path(match[1])
    _delivery_require(path.parent == store / "notification-tools" and re.fullmatch(r"[0-9a-f]{64}\.exe", path.name),
                      "알림 앱 위치를 확인해 주세요.")
    state = windows_path_observation(path)
    _delivery_require(not state["directory"] and state["links"] == 1, "알림 앱 파일을 확인해 주세요.")
    with path.open("rb") as stream:
        _delivery_require(hashlib.file_digest(stream, "sha256").hexdigest() == path.stem,
                          "알림 앱 버전을 확인해 주세요.")
    return path


def _click_receiver():
    python = Path(sys.executable)
    if os.name == "nt" and re.fullmatch(r"python-[0-9a-f]{24}", python.parent.name):
        store = python.parent.parent
        try:
            return store, windows_notice_manager(store)
        except FileNotFoundError:
            return None
    if (sys.platform == "darwin" and len(python.parents) >= 5
            and python.parts[-3:] == ("python", "bin", "python3.14")
            and python.parents[3].name == "runtimes"):
        store = python.parents[4]
        return store, store / "bin/colvia-manage"
    return None


def _notify_recorded(target, db, key, epoch, phase, *, detail_required=False):
    """Only a managed sender can open the result belonging to this receipt."""
    import sqlite3
    import subprocess
    try:
        receiver = _click_receiver()
    except (OSError, ValueError, ContractError):
        return "unavailable"
    if receiver is None:
        return "unavailable" if detail_required else _delivery_notify()
    store, manager = receiver
    try:
        _delivery_require(manager.resolve(strict=True) == manager, "관리 도구 위치를 확인해 주세요.")
        event = record_notification(store, target, db, key, epoch, phase)
        call = subprocess.run([str(manager), "notice-post", "--event", event], stdin=subprocess.DEVNULL,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=40)
        return "api_returned" if call.returncode == 0 else "unavailable"
    except (ContractError, OSError, ValueError, KeyError, sqlite3.Error, subprocess.SubprocessError):
        return "unavailable"


def _delivery_notify():
    import subprocess
    if sys.platform == "darwin":
        args = ["/usr/bin/osascript", "-e", 'display notification "프로젝트 채팅에서 물어보세요: “맡긴 작업에 질문이나 결과가 있어?”" with title "Colvia · 맡긴 작업 소식"']
    elif os.name == "nt":
        # Fixed local UI only. No registration, script file, policy bypass or input interpolation.
        import ctypes
        buf = ctypes.create_unicode_buffer(32768)
        size = ctypes.windll.kernel32.GetSystemDirectoryW(buf, len(buf))
        if not 0 < size < len(buf): return "unavailable"
        shell = Path(buf.value) / "WindowsPowerShell/v1.0/powershell.exe"
        code = ("$ErrorActionPreference='Stop';Add-Type -AssemblyName System.Windows.Forms;"
                "Add-Type -AssemblyName System.Drawing;$n=New-Object System.Windows.Forms.NotifyIcon;"
                "try {$n.Icon=[Drawing.SystemIcons]::Information;$n.Visible=$true;"
                "$n.ShowBalloonTip(3500,'Colvia: Work update','Ask in your project chat: \"Any questions or results on the work I handed off?\"',[Windows.Forms.ToolTipIcon]::Info);"
                "Start-Sleep -Milliseconds 3800} finally {$n.Dispose()}")
        args = [str(shell), "-NoProfile", "-NonInteractive", "-Command", code]
    else: return "unavailable"
    try:
        result = subprocess.run(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                timeout=12, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    except (OSError, subprocess.TimeoutExpired):
        return "unavailable"
    return "api_returned" if result.returncode == 0 else "unavailable"


def _delivery_report(target, plan):
    action = plan["request"]["action"]
    payload = plan["request"]["payload"]
    if action == "summary":
        from .view import render_view
        view, code = render_view(target, kind="work", object_id=plan["source"]["work_id"], installed=True)
        _delivery_require(code == 0, "작업을 조회할 수 없습니다.")
        if len(view) > 32768:
            view = view[:32700].rpartition("\n")[0] + "\n상세는 현재 Work에서 이어서 확인하세요."
        return {"message":"작업 현황을 정리했습니다.", "view":view}
    if action == "submit":
        manifest = (payload["manifest"] if "manifest" in payload else
                    _submission_manifest(target, payload, work.read_work(target, plan["source"]["work_id"])))
        graph = work.WorkStore(target).publish(payload["identity"],payload["revision"],manifest,
                    selection_id=payload["selection_id"],operation_id=payload["operation_id"])
        _delivery_require(graph["state"] == "review", "제출된 결과 기록을 확인해 주세요.")
        return {"message":"결과를 제출했습니다. 검토해 주세요.", "selection":graph["current"]["selection_ref"]}
    from .official_entry import execute
    observed = execute(target,payload["spec"],payload["confirm_token"])
    from .official_state import public_status, read_capsule
    receipt = public_status(read_capsule(target, payload["confirm_token"]))
    _delivery_require(observed.get("head") == receipt["head"] and receipt.get("status") == "completed" and receipt.get("process_observation") == "closed",
                      "실행 기록과 문서 반영 상태를 확인해 주세요.")
    return {"message":"문서 실행 결과가 준비됐습니다.", "head":observed["head"], "effect":observed["document_write_effect"]}


def _delivery_public(row):
    import json,time
    state = row["phase"]
    if state in ("queued","question","running") and row["expires"] <= time.time():
        state = "expired" if row["used"] == 0 else "reconcile"
    plan = json.loads(row["plan"])
    _delivery_require(work._digest(plan)==row["id"] and plan["source"]["work_id"]==row["wid"]
                      and row["used"] in (0,1) and type(row["epoch"]) is int,
                      "수신함과 접수 원본을 대조해 주세요.")
    messages = {"queued":"맡긴 작업의 시작을 기다립니다.", "question":"이 단계를 이어갈까요? 계속 또는 중단을 선택하세요.",
                "running":"승인한 단계에 진입했습니다. 결과가 늦으면 기존 실행 기록을 확인하세요.",
                "expired":"기한이 끝났습니다. 접수 기록을 확인해 마무리하세요.", "done":"결과가 준비됐습니다.", "stopped":"작업을 중단했습니다.",
                "unresolved":"실제 반영 여부를 확인할 수 없어 접수를 닫았습니다. 이력은 수신함에 보관했습니다.",
                "reconcile":"기존 작업 기록과 문서 반영 상태를 확인해 주세요."}
    return {"id":row["id"],"work_id":row["wid"],"status":state,"message":messages[state],
            "result":json.loads(row["result"]) if row["result"] else None,"notification":row["notice"],
            "reserved_steps":row["used"],"step_limit":1,"expires":row["expires"],
            "close_token":_delivery_close_token(row, time.time()),
            "action":plan["request"]["action"],"scope":plan["source"]["scope"],
            "label":plan["source"]["label"], "question_id":(row["id"]+".1") if state=="question" else None}


def require_delivery_idle(target):
    from contextlib import closing
    db = _delivery_db(target, read=True)
    if db is not None:
        with closing(db):
            active = db.execute("SELECT id FROM delivery WHERE phase IN ('queued','question','running','reconcile') LIMIT 1").fetchone()
        _delivery_require(active is None, "먼저 맡긴 Work를 마무리한 뒤 프로젝트 연결을 변경해 주세요.")


def delivery_inbox(target, wid=None):
    import sqlite3
    try:
        return _delivery_rows(target, wid)
    except (sqlite3.Error, KeyError, TypeError, ValueError, OSError) as error:
        raise ContractError("COLVIA-INBOX", "수신함 기록을 확인해 주세요. 기존 기록을 보존했습니다.") from error


def _delivery_rows(target, wid=None):
    from contextlib import closing
    db = _delivery_db(safe_target(target),read=True)
    if db is None: return []
    with closing(db):
        if wid is None:
            rows=db.execute("SELECT * FROM delivery ORDER BY changed DESC, rowid DESC LIMIT 20")
        else:
            identifier(wid)
            rows=db.execute("SELECT * FROM delivery WHERE wid=? ORDER BY changed DESC, rowid DESC LIMIT 20",(wid,))
        return [_delivery_public(row) for row in rows]


def _delivery_recover(target, row, plan):
    """Only positive evidence can turn an interrupted receipt into a result."""
    req = plan["request"]
    if req["action"] == "submit":
        data = req["payload"]
        graph = work.read_work(target, row["wid"])
        selection = graph["selections"].get(data["selection_id"])
        if (selection and data["selection_id"] not in graph["pending_selections"]
                and selection["operation_id"] == data["operation_id"]
                and selection["revision_ref"] == work.record_ref(data["revision"])
                and graph["revisions"].get(data["revision"]["record_id"]) == data["revision"]):
            return {"message":"기존 기록에서 결과 제출을 확인했습니다.", "selection":work.record_ref(selection)}
    if req["action"] == "execute":
        from .official_state import public_status, read_capsule
        receipt = public_status(read_capsule(target, req["payload"]["confirm_token"]))
        if receipt["status"] == "completed" and receipt.get("process_observation") == "closed":
            return {"message":"기존 기록에서 공식 실행 완료를 확인했습니다.", "head":receipt["head"],
                    "effect":receipt["document_write_effect"]}
    return None


def _delivery_preview(plan):
    request = plan["request"]
    source = plan["source"]
    preview = {"label": source["label"], "action": request["action"], "scope": source["scope"],
               "expires": request["expires"], "step_limit": 1, "question_before_step": request["ask"],
               "device_notice": request["notify"]}
    if request.get("detail_required"):
        preview["notification_target"] = "이 Work의 제출 결과 상세"
        preview["receiver_available_at_preview"] = request["receiver_at_preview"]
        preview["notification_limit"] = "결과는 프로젝트 수신함에 남습니다. 기기 알림 전송 여부는 제출 후 확인합니다."
    return {"preview": preview, "plan": plan, "confirm_token": work._digest(plan), "steps": 1,
            "recipient": "이 Work의 로컬 수신함", "meaning": "확인한 작업과 범위만 맡깁니다."}


def prepare_delivery(target, request):
    if isinstance(request, dict) and request.get("detail_required") is True:
        try:
            receiver = _click_receiver()
            available = receiver is not None and receiver[1].is_file() and receiver[1].resolve() == receiver[1]
        except (OSError, ValueError, ContractError):
            available = False
        request = dict(request, receiver_at_preview=available)
    return _delivery_preview(_delivery_validate(target, request))


def delivery_command(target, args, value=None):
    if args.action == "show" or args.action == "start":
        from contextlib import closing
        key = args.key
        _delivery_require(type(key) is str and re.fullmatch(r"[a-f0-9]{64}",key), "접수 확인값을 확인해 주세요.")
        if args.action == "start":
            if isinstance(value, dict) and "plan" in value:
                plan = value["plan"]
                _delivery_require(type(plan) is dict and work._digest(plan) == key
                                  and isinstance(plan.get("source"), dict) and isinstance(plan.get("request"), dict)
                                  and all(k in plan["source"] for k in ("label", "scope"))
                                  and all(k in plan["request"] for k in ("action", "expires", "ask", "notify"))
                                  and (not plan["request"].get("detail_required") or type(plan["request"].get("receiver_at_preview")) is bool)
                                  and value == _delivery_preview(plan), "확인한 알림 미리보기가 바뀌었습니다.")
                value = plan
            _delivery_require(type(value) is dict and work._digest(value)==key and value.get("source",{}).get("project")==str(target),
                              "이 프로젝트의 정확한 미리보기를 지정해 주세요.")
        db = _delivery_db(target,read=True)
        if db is not None:
            with closing(db):
                row = db.execute("SELECT * FROM delivery WHERE id=?", (key,)).fetchone()
            if row is not None:
                return _delivery_public(row)
        _delivery_require(args.action != "show", "접수된 Work를 찾을 수 없습니다.")
        with writer_guard(target):
            return _delivery_dispatch(target, args, value)
    if args.action == "close-unknown":
        from contextlib import closing
        db = _delivery_db(target, read=True)
        _delivery_require(db is not None, "해당 작업의 수신함을 찾을 수 없습니다.")
        with closing(db), _delivery_fence(target), writer_guard(target):
            return _delivery_dispatch(target, args, value)
    return _delivery_dispatch(target, args, value)


def _delivery_dispatch(target, args, value):
    import json, sqlite3, time
    from contextlib import closing
    now=lambda: int(time.time())
    target=safe_target(target)
    if args.action=="prepare":
        return prepare_delivery(target, value)
    key=args.key
    _delivery_require(type(key) is str and re.fullmatch(r"[a-f0-9]{64}",key), "접수 확인값을 확인해 주세요.")
    if args.action == "start":
        _delivery_require(value == _delivery_validate(target,value["request"]), "미리보기가 달라졌습니다.")
    db=_delivery_db(target,create=args.action=="start")
    _delivery_require(db is not None, "해당 작업의 수신함을 찾을 수 없습니다.")
    with closing(db):
        db.execute("BEGIN IMMEDIATE")
        row=db.execute("SELECT * FROM delivery WHERE id=?",(key,)).fetchone()
        if args.action=="start":
            _delivery_require(type(value) is dict and work._digest(value)==key and value.get("source",{}).get("project")==str(target),
                              "이 프로젝트의 정확한 접수 미리보기가 필요합니다.")
            if row is not None:
                return _delivery_public(row)
            _delivery_require(value==_delivery_validate(target,value["request"]), "미리보기가 달라졌습니다.")
            req=value["request"]
            effect_ids = _delivery_effect_ids(req)
            if effect_ids:
                for prior in db.execute("SELECT plan FROM delivery WHERE wid=? AND phase='unresolved'", (req["work_id"],)):
                    _delivery_require(effect_ids.isdisjoint(_delivery_effect_ids(json.loads(prior["plan"])["request"])),
                                      "같은 실행이 미확인 상태로 종결됐습니다. 기존 Work 기록을 확인해 주세요.")
            try:
                db.execute("INSERT INTO delivery VALUES (?,?,?,'queued',1,0,?,NULL,'none',?)",
                           (key,req["work_id"],canonical_json_bytes(value).decode(),req["expires"],now()))
            except sqlite3.IntegrityError:
                raise ContractError("COLVIA-DELIVERY","먼저 맡긴 작업의 상태를 확인해 주세요.") from None
            epoch=1
        else:
            _delivery_require(row is not None, "접수된 Work를 찾을 수 없습니다.")
            plan=json.loads(row["plan"]); request=plan["request"];epoch=row["epoch"]
            _delivery_require(work._digest(plan)==key and row["wid"]==plan["source"]["work_id"], "접수 기록을 확인해 주세요.")
            if args.action in ("inspect", "close-unknown"):
                if args.action == "close-unknown":
                    _delivery_require(bool(args.confirm) and args.confirm == _delivery_close_token(row, now()),
                                      "기한이 지난 접수의 최신 확인값이 필요합니다.")
                if row["used"] == 0 and row["phase"] in ("queued","question","reconcile") and row["expires"] <= now():
                    db.execute("UPDATE delivery SET phase='stopped',epoch=epoch+1,changed=? WHERE id=?",(now(),key))
                elif row["phase"] in ("reconcile","running","unresolved") and row["used"] == 1:
                    try:
                        result = _delivery_recover(target,row,plan)
                    except (OSError, ValueError, ContractError):
                        result = None
                    if result is not None:
                        db.execute("UPDATE delivery SET phase='done',epoch=epoch+1,result=?,changed=? WHERE id=?",
                                   (json.dumps(result,ensure_ascii=False),now(),key))
                    elif args.action == "close-unknown":
                        db.execute("UPDATE delivery SET phase='unresolved',epoch=epoch+1,changed=? WHERE id=?", (now(),key))
                    elif plan["request"]["action"]=="summary" and row["expires"]<=now():
                        db.execute("UPDATE delivery SET phase='stopped',epoch=epoch+1,changed=? WHERE id=?",(now(),key))
                db.commit()
                return _delivery_public(db.execute("SELECT * FROM delivery WHERE id=?",(key,)).fetchone())
            if args.action=="stop":
                if row["phase"] in ("queued","question"):
                    db.execute("UPDATE delivery SET phase='stopped',epoch=epoch+1,changed=? WHERE id=?",(now(),key))
                elif row["phase"]=="running":
                    db.execute("UPDATE delivery SET phase='reconcile',epoch=epoch+1,changed=? WHERE id=?",(now(),key))
                db.commit()
                return _delivery_public(db.execute("SELECT * FROM delivery WHERE id=?",(key,)).fetchone())
            if args.action=="answer":
                _delivery_require(row["phase"]=="question" and args.question==key+".1" and row["expires"]>now(),
                                  "현재 질문과 유효 기한을 확인해 주세요.")
                _delivery_require(plan==_delivery_validate(target,request),"작업이나 승인 범위가 바뀌었습니다.")
                epoch+=1
                db.execute("UPDATE delivery SET phase='queued',epoch=?,notice='none',changed=? WHERE id=?",(epoch,now(),key))
            elif args.action=="_step":
                if row["phase"]!="queued" or args.epoch!=epoch: return {"status":"already-handled"}
                if row["expires"]<=now():
                    db.execute("UPDATE delivery SET phase='stopped',changed=? WHERE id=?",(now(),key));db.commit()
                    return {"status":"expired"}
                question=request["ask"] and epoch==1
                if question:
                    db.execute("UPDATE delivery SET phase='question',notice=?,changed=? WHERE id=?",
                               ("attempted" if request["notify"] else "off",now(),key))
                else:
                    reserved = db.execute("UPDATE delivery SET phase='running',used=1,changed=? WHERE id=? AND used=0 AND phase='queued' AND epoch=?",(now(),key,epoch))
                    _delivery_require(reserved.rowcount == 1, "이미 예약한 단계입니다.")
                db.commit()
                if not question:
                    entered_effect = False
                    try:
                        with _delivery_fence(target):
                            _delivery_require(_delivery_validate(target,request)==plan,"작업·범위 변경")
                            # Fence cancellation before effect; after this point preserve uncertain effects.
                            latest=db.execute("SELECT phase,epoch FROM delivery WHERE id=?",(key,)).fetchone()
                            if tuple(latest) != ("running",epoch):
                                with db:
                                    db.execute("UPDATE delivery SET phase='stopped',changed=? WHERE id=? AND phase='reconcile' AND epoch=?",(now(),key,epoch+1))
                                return {"status":"stopped-before-effect"}
                            _delivery_require(now() < request["expires"], "승인 기한이 끝났습니다.")
                            entered_effect = request["action"] != "summary"
                            result=_delivery_report(target,plan)
                            phase="done"
                    except Exception:
                        phase = "reconcile" if entered_effect else "stopped"
                        result = {"message":"실행 기록과 문서 반영 상태를 대조해 주세요." if entered_effect else "단계 실행 전에 중단했습니다. 작업 상태와 기한을 확인해 주세요."}
                    with db:
                        updated=db.execute("UPDATE delivery SET phase=?,result=?,notice=?,changed=? WHERE id=? AND phase='running' AND epoch=?",
                            (phase,json.dumps(result,ensure_ascii=False),"attempted" if request["notify"] else "off",now(),key,epoch))
                    if updated.rowcount!=1: return {"status":"inspect-existing-effect"}
                if request["notify"]:
                    notify = _notify_recorded(target, db, key, epoch, "question" if question else phase,
                                              detail_required=request.get("detail_required", False))
                    with db: db.execute("UPDATE delivery SET notice=? WHERE id=? AND epoch=? AND notice='attempted'",(notify,key,epoch))
                return {"status":"recorded"}
            else: raise ContractError("COLVIA-DELIVERY","알 수 없는 작업입니다.")
        db.commit()
        try: _delivery_command(target,key,epoch)
        except OSError:
            with db: db.execute("UPDATE delivery SET phase='stopped',epoch=epoch+1 WHERE id=? AND phase='queued' AND epoch=?",(key,epoch))
        return _delivery_public(db.execute("SELECT * FROM delivery WHERE id=?",(key,)).fetchone())
