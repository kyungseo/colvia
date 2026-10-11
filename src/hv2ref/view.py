"""Read-only human projection. No authority, publication or runtime mutation seam."""
from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
import stat
import sys
import unicodedata

from .errors import ContractError
from .intent import WorkspaceIntentStore, workspace_intents, read_workspace_intent
from .jsonio import decode_json_bytes
from .product import _workspace_status_observation, verify_workspace_product
from .workspace import safe_target, target_fingerprint
from .work import (WorkStore, _digest, _resolve, _require, project_path, record_ref,
                   snapshot, validate_ticket, work_graph, _RECORD_BASE, _PROVENANCE,
                   verify_worker_sources, observe_recovery, preflight_changed_paths)

READ_LIMIT = 4 * 1024 * 1024
EXITS = {"degraded": 10, "incompatible": 11, "conflict": 12, "stale": 13,
         "partial": 14, "uninitialized": 15, "unsupported": 16, "unstable": 10}


def _visible(value: object) -> str:
    # Literal backslashes remain distinguishable from rendered control escapes.
    return "".join("\\\\" if c == "\\" else "\\u" + format(ord(c), "04x")
                   if unicodedata.category(c).startswith("C") else c for c in str(value))


def text(value: object) -> str:
    """Readable CommonMark text; never raw markup or terminal controls."""
    out = []
    for c in _visible(value):
        if c in "&<>": out.append({"&": "&amp;", "<": "&lt;", ">": "&gt;"}[c])
        elif c in "\\`*_{}[]()!|#~": out.append("\\" + c)
        else: out.append(c)
    rendered = "".join(out)
    # GFM auto-links URLs/emails even when surrounding link punctuation is escaped.
    rendered = re.sub(r"(?i)\b(https?|ftp):", r"\1&#58;", rendered)
    rendered = re.sub(r"(?i)\b(www)\.", r"\1&#46;", rendered)
    return rendered.replace("@", "&#64;")


def code(value: str) -> str:
    """Dynamic code delimiters keep paths copyable and punctuation inert in GFM."""
    value = _visible(value)
    longest = max((len(part) for part in re.findall(r"`+", value)), default=0)
    fence = "`" * (longest + 1)
    return fence + " " + value + " " + fence


def fields(value, depth=0):
    prefix = "  " * depth + "- "
    if isinstance(value, dict):
        lines = []
        for key, item in value.items():
            if isinstance(item, (dict, list)) and item:
                lines += [prefix + text(key) + ":"] + fields(item, depth + 1)
            else:
                if isinstance(item, str) and (key in {"path", "target", "manual", "documentation_root", "natural_language_adapter", "sha256"} or str(key).endswith("_sha256")):
                    shown = code(item)
                elif isinstance(item, str) and item in {"none", "True", "False", "[]", "{}"}:
                    shown = text(item) + " (string)"
                else: shown = text("none" if item is None else item)
                lines.append(prefix + text(key) + ": " + shown)
        return lines
    if isinstance(value, list):
        lines = []
        for i, item in enumerate(value, 1):
            if isinstance(item, (dict, list)):
                lines += [prefix + "Entry " + str(i) + ":"] + fields(item, depth + 1)
            else: lines += fields(item, depth)
        return lines or [prefix + "none"]
    return [prefix + text(value)]


def _stamp(s):
    return s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns


def bounded_bytes(path: Path) -> bytes:
    """Descriptor-relative no-follow reads; exact spelling, regular single-link files only."""
    path = Path(os.path.abspath(path))
    fd = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:-1]:
            _require(part in os.listdir(fd), "view path spelling differs")
            nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd); fd = nxt
        if path.name not in os.listdir(fd): raise FileNotFoundError(path.name)
        leaf = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        try:
            before = os.fstat(leaf)
            _require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= READ_LIMIT,
                     "view input is linked, special or exceeds 4 MiB")
            data = bytearray()
            while len(data) <= READ_LIMIT:
                chunk = os.read(leaf, min(65536, READ_LIMIT + 1 - len(data)))
                if not chunk: break
                data.extend(chunk)
            _require(len(data) <= READ_LIMIT and _stamp(before) == _stamp(os.fstat(leaf)), "view input changed or oversized")
            _require(_stamp(before) == _stamp(os.stat(path.name, dir_fd=fd, follow_symlinks=False)), "view input replaced")
            return bytes(data)
        finally:
            os.close(leaf)
    finally:
        os.close(fd)


def reference_observation(target, ref, *, evidence=False):
    if evidence and ref["verification"] == "worker-observed":
        return "worker-observed; not reverified on control"
    try:
        relative = project_path(ref["path"])
        path = target / relative
        first = bounded_bytes(path)
        if first != bounded_bytes(path): return "unavailable: changed during observation"
        return "matches" if hashlib.sha256(first).hexdigest() == ref["sha256"] else "stale"
    except FileNotFoundError:
        return "missing"
    except (ContractError, OSError, ValueError):
        return "unavailable: missing, unsafe, oversized or unstable"


def _candidate_reference(target, ref, candidate, *, evidence=False):
    if evidence and ref["verification"] == "worker-observed":
        return reference_observation(target, ref, evidence=True)
    if candidate is None or ref["path"] not in {c["path"] for c in candidate["manifest"]["changes"]}:
        return reference_observation(target, ref, evidence=evidence)
    if candidate["source_error"]: return "unavailable: retained candidate could not be verified"
    post = candidate["sources"][ref["path"]]["post"]
    if post is None: return "missing in retained candidate (deleted result)"
    if len(post) > READ_LIMIT: return "unavailable: candidate reference exceeds 4 MiB advisory limit"
    return "matches retained candidate" if hashlib.sha256(post).hexdigest() == ref["sha256"] else "stale: retained candidate digest differs"


def _worker_inspection(target, manifest, product):
    """Read-only observations; deliberately no aggregate permission to proceed."""
    result = {"manifest": manifest, "sources": {}, "source_error": None, "content": None, "content_error": None}
    try:
        _require(product is not None, "no verified active product")
        result["sources"] = verify_worker_sources(target, manifest, verified_launcher_sha256=product["launcher_sha256"], verified_inventory_id=product["inventory"]["inventory_id"])
    except (ContractError, OSError, ValueError) as exc:
        result["source_error"] = getattr(exc, "message", str(exc))
    try:
        _require(product is not None, "no verified active product")
        current = snapshot(target, verified_launcher_sha256=product["launcher_sha256"], verified_inventory_id=product["inventory"]["inventory_id"])
        observed = observe_recovery(manifest, current)
        physical = preflight_changed_paths(target, manifest, verified_launcher_sha256=product["launcher_sha256"], verified_inventory_id=product["inventory"]["inventory_id"])
        _require(physical == observed["changed_paths"], "physical occupants differ from visible snapshot")
        result["content"] = {**observed, "whole_base_matches": current == manifest["base"]}
    except (ContractError, OSError, ValueError) as exc:
        result["content_error"] = getattr(exc, "message", str(exc))
    return result


def _worker_observation_lines(candidate):
    lines = ["## Worker control and candidate (advisory)", "",
             "Control baseline and retained candidate are separate. Before acceptance, control normally still contains the baseline.", ""]
    lines += fields({"base_commit": candidate["manifest"]["base_commit"], "candidate_commit": candidate["manifest"]["candidate_commit"],
                     "retained_sources": candidate["source_error"] or "verified local commit/blob observations"})
    if candidate["content_error"]: lines += fields({"content_observation": "unavailable", "reason": candidate["content_error"]})
    else:
        obs = candidate["content"]
        lines += fields({k: obs[k] for k in ("whole_base_matches", "whole_result_matches", "changed_paths", "outside_drift", "policy_matches")})
    return lines + ["- These observations do not grant acceptance, recovery or cancellation. Apply checks the exact records and live prerequisites again.", ""]


def _baseline_review(graph, revision, manifest, works):
    prior = _resolve(graph["selections"], revision["expected_prior_selection"])
    old = _resolve(graph["revisions"], prior["revision_ref"])
    previous = _resolve(graph["manifests"], old["result_refs"]["manifest"])
    lines = ["## Human baseline refresh — not result acceptance", "",
             "This decision selects an active baseline only; it does not accept the worker result or complete the Work.", ""]
    lines += fields({"intent_binding": "same accepted intent" if old["intent_ref"] == revision["intent_ref"] else "different accepted intent"})
    lines += ["### Previous baseline to proposed baseline", ""] + _changes(previous["base"], manifest["base"])
    if old["operation"] == "submit-result":
        lines += ["### Previous submitted candidate to proposed baseline", "", "The previous candidate is a separate recorded result, not automatically carried into this baseline.", ""] + _changes(previous["result"], manifest["base"])
    before = {e["path"]: e for e in previous["base"]["entries"]}
    after = {e["path"]: e for e in manifest["base"]["entries"]}
    lines += ["### Content matches do not establish origin", ""]
    for path in sorted(before.keys() | after.keys()):
        if before.get(path) == after.get(path): continue
        matches = []
        for wid, other in sorted(works.items()):
            if other["state"] != "completed": continue
            selected = _resolve(other["selections"], other["current"]["selection_ref"])
            r = _resolve(other["revisions"], selected["revision_ref"])
            m = _resolve(other["manifests"], r["result_refs"]["manifest"])
            # A coincidental absent path or unchanged file is not an applied change.
            if any(c["path"] == path and c["post"] == after.get(path) for c in m["changes"]):
                matches.append({"work": wid, "revision_ref": selected["revision_ref"], "decision_ref": selected["decision_ref"]})
        lines += fields({"path": path, "scope_note": "IN-SCOPE CHANGE; origin unproven" if path in revision["scope"] else "outside Work scope; origin unproven",
                         "completed_changed_path_matches": matches or "none", "meaning": "content equality only; cause and timing unproven"})
    return lines


def references(target, obj, candidate=None):
    lines = []
    for kind in ("document_refs", "evidence_refs"):
        lines.append("### " + kind.replace("_", " ").title() + "\n")
        if not obj.get(kind): lines.append("- none")
        for ref in obj.get(kind, []):
            observation = _candidate_reference(target, ref, candidate, evidence=kind == "evidence_refs")
            changed = candidate is not None and ref["path"] in {c["path"] for c in candidate["manifest"]["changes"]} and not (kind == "evidence_refs" and ref["verification"] == "worker-observed")
            extra = {"reference_location": "retained candidate; not control live", "control_observation": reference_observation(target, ref, evidence=kind == "evidence_refs")} if changed else {}
            lines += fields({**ref, **extra, "observation": observation})
        lines.append("")
    return lines


def _observe(target):
    status, graphs = _workspace_status_observation(target)
    if status["classification"] in ("degraded", "uninitialized", "incompatible", "unstable"):
        return status, {}, {}
    # Partial bootstrap has no readable authority yet; pending records and detach do.
    if not (target / ".hrn/format.json").is_file(): return status, {}, {}
    if graphs is not None: return status, *graphs
    return status, WorkStore(target)._all(), workspace_intents(target)


def _product(target):
    try: return verify_workspace_product(target)
    except (ContractError, OSError, ValueError): return None


def _live(target, manifest, product):
    if product is None: return "unavailable: no verified active product"
    try:
        observed = snapshot(target, verified_launcher_sha256=product["launcher_sha256"], verified_inventory_id=product["inventory"]["inventory_id"])
        return "matches stored result" if observed == manifest["result"] else "stale: current files differ from stored result"
    except (ContractError, OSError, ValueError): return "unavailable: current content observation failed"


def _current_revision(graph):
    if not graph["current"]: return None
    return graph["selections"][graph["current"]["selection_ref"]["id"]]["revision_ref"]["id"]


def _changes(before, after):
    a = {e["path"]: e for e in before["entries"]}; b = {e["path"]: e for e in after["entries"]}
    rows = []
    for path in sorted(a.keys() | b.keys()):
        if a.get(path) != b.get(path): rows += fields({"path": path, "before": a.get(path), "after": b.get(path)})
    return rows or ["- no path/mode/size/digest changes"]


def _umbrella_lines(target, revision, graph, works, intents):
    from .umbrella import bound_composition, capture, check_baseline_binding, prior_revision
    composition = bound_composition(revision, intents)
    if composition is None: return []
    captured = capture(composition, works, intents)
    evidence = revision["umbrella_evidence"]
    lines = ["", "## 상위 작업과 필수 하위 작업", "",
             "저장된 수락 결과와 지금의 하위 작업 상태를 구분합니다. 이 화면은 수락 권한을 부여하지 않습니다.", ""]
    lines += fields({"부모 Work": composition["parent"]["id"], "필수 하위 작업": composition["required_children"],
                     "이 판본의 기준점 또는 제출 근거": evidence,
                     "현재 참조 가능한 결과": captured["children"], "현재 미충족 이유": captured["unavailable"]})
    first = {}
    ref = graph["current"]["selection_ref"] if graph["current"] else None
    chain = []
    while ref:
        selected = _resolve(graph["selections"], ref); chain.append(selected); ref = selected["parent_selection_ref"]
    for selected in reversed(chain):
        record = _resolve(graph["revisions"], selected["revision_ref"])
        for child in record.get("umbrella_evidence", {}).get("children", []):
            first.setdefault(child["work"]["id"], child["intent_ref"])
    lines += fields({"선택 이력에서 처음 포착한 요청 판본": first or "unknown — 아직 선택된 포착 기록 없음"})
    if revision["operation"] != "submit-result":
        lines += ["- 아직 결과 제출 판본이 아닙니다. 기준점을 새로 맞춰야 하는지는 현재 결과 참조와 비교합니다."]
    else:
        try:
            check_baseline_binding(composition, revision, prior_revision(revision, graph), works, intents, current=True)
            for child in evidence["children"]:
                ref = child["intent_ref"]
                read_workspace_intent(target, ref["id"], ref)
            lines += ["- 하위 결과 참조 조건: 충족. 문서 원문·실행 근거·통합 결과·실행 환경과 사람의 판단은 별도 확인합니다."]
        except ContractError as exc:
            lines += ["- 현재 하위 결과 참조 조건: 미충족 — " + text(exc.message)]
    lines += ["- 완료 뒤 하위 작업이 바뀌어도 과거 수락은 자동 취소되지 않습니다.",
              "- 처음 포착하기 전 변경 여부는 unknown입니다. 시각만으로 구성 수락 이후의 변경이라고 추정하지 않습니다."]
    return lines


def _work(target, graph, rid, product, intents, works):
    current = _current_revision(graph)
    rid = rid or current
    lines = ["## Work " + text(graph["identity"]["work_id"]), "",
             "Stored state: " + text(graph["state"]) + ". Current files are a separate observation.", ""]
    lines += fields({"authority": graph["identity"]["acceptance_authority"], "current_selection": graph["current"],
                     "pending_decisions": graph["pending_decisions"], "pending_selections": graph["pending_selections"]})
    for orphan in graph["orphan_revisions"]:
        lines += fields({"unselected_proposal": orphan, "operation": graph["revisions"][orphan]["operation"]})
    if rid is None: return lines
    _require(rid in graph["revisions"], "view revision not found")
    r = graph["revisions"][rid]; manifest = _resolve(graph["manifests"], r["result_refs"]["manifest"])
    lines += ["", "## Selected revision fields (recorded at publication)" if rid == current else "## Historical or unselected proposal", "", "Recorded progress and next_action are historical agent fields, not a new action request or the current derived Work state.", ""]
    lines += fields({key: r[key] for key in ("record_id", "author", "operation", "progress", "scope", "next_action", "observed_scope", "unavailable_scope", "relations", "rebind_from", "execution_context")})
    if r["schema_version"] == 2:
        lines += _umbrella_lines(target, r, graph, works, intents)
    try:
        bound = read_workspace_intent(target, r["intent_ref"]["id"], r["intent_ref"], require_current=False)
        lines += fields({"bound_intent_current": bound["is_current"]})
        if not bound["is_current"]:
            lines.append("- A newer intent is already accepted. Historical completion is unchanged. To continue work under that intent: human Work rebind, new submit-result, then new human accept.")
    except ContractError as exc:
        lines += fields({"bound_intent": "unavailable", "reason": exc.message})
    ig = intents[r["intent_ref"]["id"]]
    acceptance = _resolve(ig["acceptances"], r["intent_ref"]["acceptance_ref"])["confirmation"]
    lines += ["", "## Bound intent documents", ""] + references(target, acceptance)
    if any(ref["required"] and reference_observation(target, ref) != "matches" for ref in acceptance["document_refs"]):
        lines += ["- Required intent document changed or unavailable: related publication/acceptance is blocked. Restore it or obtain new intent acceptance, Work rebind, new submit-result and new human accept."]
    candidate = _worker_inspection(target, manifest, product) if r["execution_context"]["mode"] == "isolated-worktree" else None
    lines += ["", "## Work revision documents and evidence", ""] + references(target, r, candidate)
    if candidate:
        lines += _worker_observation_lines(candidate)
        if r["operation"] == "rebind": lines += _baseline_review(graph, r, manifest, works)
    else:
        lines += ["## Current files (advisory)", "", "- " + text(_live(target, manifest, product)), ""]
    # Follow exact parent references, including human decisions; never timestamps.
    chain = []; ref = graph["current"]["selection_ref"] if graph["current"] else None
    while ref:
        selection = _resolve(graph["selections"], ref); chain.append(selection); ref = selection["parent_selection_ref"]
    chain.reverse()
    lines += ["## Selected history", ""]
    previous = None; first = None; seen = set()
    for selection in chain:
        revision = _resolve(graph["revisions"], selection["revision_ref"])
        m = _resolve(graph["manifests"], revision["result_refs"]["manifest"])
        first = first or m["base"]
        lines += fields({"selection": selection["record_id"], "revision": revision["record_id"], "operation": revision["operation"], "decision": selection["decision_ref"]})
        if selection["decision_ref"]:
            decision = _resolve(graph["decisions"], selection["decision_ref"])
            ticket = decision["confirmation"]
            lines += fields({"selected_decision": {k: ticket[k] for k in ("action", "actor", "reason", "supersedes_decision_ref")}})
        if revision["record_id"] not in seen:
            if revision["operation"] == "rebind" and previous is not None:
                lines += ["", "#### Rebind discontinuity (not attributed to this Work)", ""] + _changes(previous, m["base"])
            if revision["operation"] == "submit-result":
                lines += ["", "#### Submitted base to result (metadata only)", ""] + _changes(m["base"], m["result"])
            if revision["operation"] == "rework": lines += ["- Rework retains the rejected/revoked result as its baseline; project bytes were not undone."]
            seen.add(revision["record_id"])
        previous = m["result"]
    if first:
        lines += ["", "### Initial baseline to displayed result (metadata only)", ""] + _changes(first, manifest["result"])
    lines += ["", "### Displayed revision base to result (metadata only)", ""] + _changes(manifest["base"], manifest["result"])
    lines += ["", "## Decision and cancellation records (not chronological)", ""]
    for decision in graph["decisions"].values():
        t = decision["confirmation"]
        lines += fields({"decision": decision["record_id"], **{k: t[k] for k in ("action", "actor", "reason", "target_revision_ref", "supersedes_decision_ref")}})
    lines += ["", "Manifest records do not store content bytes. These lists are not a historical text diff."]
    return lines


def _intent(target, graph, rid):
    current = _current_revision(graph)
    lines = ["## Intent " + text(graph["identity"]["intent_id"]), ""]
    lines += fields({"current_acceptance_selection": graph["current"], "pending_acceptances": graph["pending_acceptances"], "pending_selections": graph["pending_selections"]})
    for key, draft in graph["drafts"].items():
        lines += fields({"revision": key, "label": "current accepted" if key == current else "not current (draft or historical)"})
    chosen = rid or current
    if chosen:
        _require(chosen in graph["drafts"], "view intent revision not found")
        lines += ["", "### Current accepted narrative" if chosen == current else "### Draft or historical narrative — not current", ""] + fields(graph["drafts"][chosen])
    elif not rid:
        for draft in graph["drafts"].values(): lines += ["", "### Unaccepted draft", ""] + fields(draft)
    if current:
        s = _resolve(graph["selections"], graph["current"]["selection_ref"])
        acceptance = _resolve(graph["acceptances"], s["acceptance_ref"])
        lines += ["", "## Current acceptance documents (separate from draft)", ""] + references(target, acceptance["confirmation"])
    lines += ["", "Proposed acceptance documents appear only in the confirmation ticket view."]
    return lines


def _confirmation(target, ticket, works, intents, product):
    validate_ticket(ticket)
    lines = ["## Confirmation — human decision required", "", "Display is not acceptance, application or completion.", ""]
    candidate = None
    if ticket["object"]["kind"] == "work" and ticket["execution_mode"] == "isolated-worktree":
        g = works.get(ticket["object"]["id"]); _require(g is not None, "ticket Work not found")
        r = _resolve(g["revisions"], ticket["target_revision_ref"])
        candidate = _worker_inspection(target, _resolve(g["manifests"], r["result_refs"]["manifest"]), product)
    lines += fields(ticket) + fields({"confirm_token": _digest(ticket)[:16]}) + references(target, ticket, candidate)
    checks = []
    def check(label, fn):
        try:
            result = fn(); checks.append({"check": label, "observation": "matches" if result is None else result})
        except (ContractError, KeyError, OSError, ValueError) as exc:
            checks.append({"check": label, "observation": "unavailable or refused", "reason": getattr(exc, "message", str(exc))})
    def required_references(obj, candidate=None):
        failed = []
        for kind in ("document_refs", "evidence_refs"):
            for ref in obj.get(kind, []):
                if not ref["required"]: continue
                if kind == "evidence_refs" and ref["verification"] == "worker-observed": continue
                observed = _candidate_reference(target, ref, candidate, evidence=kind == "evidence_refs")
                if observed not in ("matches", "matches retained candidate"): failed.append(ref["path"] + ": " + observed)
        _require(not failed, "required references: " + "; ".join(failed))
    if ticket["action"] in ("accept", "rebind"):
        check("required ticket references (advisory reader)", lambda: required_references(ticket, candidate))
    else:
        checks.append({"check": "required live references", "observation": "not required for reject/revoke; no new result authority"})
    check("target fingerprint", lambda: _require(ticket["target_fingerprint"] == target_fingerprint(target), "ticket target differs"))
    check("active binding", lambda: _require(product is not None and product["binding_ref"] == ticket["product_binding_ref"], "binding changed or unavailable"))
    kind = ticket["object"]["kind"]; key = ticket["object"]["id"]
    if kind == "intent":
        graph = intents.get(key)
        _require(graph is not None, "ticket intent not found")
        lines += ["- Read the proposed intent content before deciding: " + code("hv2 view intent " + key + " --revision " + ticket["target_revision_ref"]["id"])]
        store = WorkspaceIntentStore(target)
        check("pending publications", lambda: (store._guard_pending(key), None)[1])
        check("expected selection", lambda: _require(ticket["expected_selection_ref"] == (graph["current"]["selection_ref"] if graph["current"] else None), "selection changed"))
        check("actor, material gaps and acceptance graph", lambda: (store._accepted_data(graph, ticket), None)[1])
        applied = any(s["acceptance_ref"]["id"] == "acceptance-" + _digest(ticket) and sid not in graph["pending_selections"] for sid, s in graph["selections"].items())
    else:
        graph = works.get(key); _require(graph is not None, "ticket Work not found")
        store = WorkStore(target); decision = store._decision(ticket)
        r = _resolve(graph["revisions"], ticket["target_revision_ref"])
        check("execution mode", lambda: _require(ticket["execution_mode"] == r["execution_context"]["mode"], "ticket execution mode differs"))
        if candidate:
            lines += _worker_observation_lines(candidate)
            if r["operation"] == "rebind": lines += _baseline_review(graph, r, candidate["manifest"], works)
            if ticket["action"] in ("accept", "rebind"):
                check("retained worker sources", lambda: _require(candidate["source_error"] is None, candidate["source_error"] or "sources unavailable"))
            def content_phase():
                _require(candidate["content_error"] is None, candidate["content_error"] or "content unavailable")
                obs = candidate["content"]
                if ticket["action"] == "reject" and ticket["supersedes_decision_ref"]:
                    _require(obs["all_changed_paths_pre"], "cancellation refused: some changed path is not pre or policy differs")
                    return "all changed paths pre; outside drift does not block cancellation; open D and no durable S still required"
                if ticket["action"] == "rebind":
                    _require(obs["whole_base_matches"], "proposed baseline differs from control")
                    return "baseline matches; result is not accepted"
                if ticket["action"] != "accept": return "no content application for reject/revoke"
                selected = any(v["decision_ref"] == record_ref(decision) for v in graph["selections"].values())
                if selected:
                    _require(obs["whole_result_matches"], "selected result differs; no content reapplication")
                    return "result matches selected decision; historical replay does not reapply files"
                if decision["record_id"] in graph["decisions"]:
                    _require(obs["content_resume_possible"], "recovery blocked by outside drift, policy or changed-path bytes")
                    return "pending decision; only remaining pre-images may be applied after guarded verification"
                _require(obs["whole_base_matches"], "new acceptance requires control baseline; pre-applied result is refused")
                return "control matches baseline; candidate is not yet applied"
            if ticket["action"] in ("accept", "rebind") or ticket["supersedes_decision_ref"]:
                check("worker content phase (advisory)", content_phase)
        check("pending publications", lambda: store._pending_guard(works, key, content_write=ticket["execution_mode"] == "isolated-worktree" and ticket["action"] == "accept"))
        check("expected selection", lambda: _require(graph["current"] is not None and graph["current"]["selection_ref"] == ticket["expected_selection_ref"], "selection changed"))
        def proposed_graph():
            decisions = graph["decisions"] | {decision["record_id"]: decision}
            work_graph(graph["identity"], graph["revisions"], decisions, graph["selections"], graph["manifests"], graph["current"])
            existing = [v for v in graph["selections"].values() if v["decision_ref"] == record_ref(decision)]
            selection = existing[0] if existing else {**{k: r[k] for k in _RECORD_BASE | _PROVENANCE}, "schema_version": 1, "record_type": "work-selection", "record_id": "selection-" + _digest(ticket), "observed_at": ticket["observed_at"], "parent_selection_ref": ticket["expected_selection_ref"], "revision_ref": ticket["target_revision_ref"], "decision_ref": record_ref(decision), "operation_id": ticket["request_id"]}
            work_graph(graph["identity"], graph["revisions"], decisions, graph["selections"] | {selection["record_id"]: selection}, graph["manifests"], graph["current"])
        check("actor and decision/selection graph", proposed_graph)
        check("not cancelled", lambda: _require(not any(d["confirmation"]["action"] == "reject" and d["confirmation"]["supersedes_decision_ref"] == record_ref(decision) for d in graph["decisions"].values()), "cancelled decision cannot resume"))
        def bound_intent():
            observed = read_workspace_intent(target, r["intent_ref"]["id"], r["intent_ref"], require_current=False)
            _require(observed["acceptance_authority"] == graph["identity"]["acceptance_authority"], "intent authority differs")
            if ticket["action"] in ("accept", "rebind"):
                _require(observed["is_current"], "intent changed; rebind then resubmit required")
            return "current" if observed["is_current"] else "historical; no new authority"
        check("bound intent", bound_intent)
        if r["schema_version"] == 2:
            from .umbrella import bound_composition, check_baseline_binding, prior_revision
            check("부모 기준점과 하위 결과 참조", lambda: check_baseline_binding(
                bound_composition(r, intents), r, prior_revision(r, graph), works, intents,
                current=ticket["action"] in ("accept", "rebind")))
            lines += _umbrella_lines(target, r, graph, works, intents)
        if ticket["action"] in ("accept", "rebind"):
            manifest = _resolve(graph["manifests"], r["result_refs"]["manifest"])
            if candidate is None: checks.append({"check": "whole result", "observation": _live(target, manifest, product)})
            intent = intents[r["intent_ref"]["id"]]
            acceptance = _resolve(intent["acceptances"], r["intent_ref"]["acceptance_ref"])
            check("required bound intent references (advisory reader)", lambda: required_references(acceptance["confirmation"]))
            if candidate and ticket["action"] == "accept":
                def intent_overlap():
                    changed = [unicodedata.normalize("NFC", c["path"].casefold()) for c in manifest["changes"]]
                    for category in ("document_refs", "evidence_refs"):
                        for ref in acceptance["confirmation"][category]:
                            path = unicodedata.normalize("NFC", ref["path"].casefold())
                            _require(not ref["required"] or not any(path == c or path.startswith(c + "/") or c.startswith(path + "/") for c in changed), "worker diff overlaps required intent input")
                check("required intent input boundary", intent_overlap)
            lines += ["## Bound intent documents", ""] + references(target, acceptance["confirmation"])
        applied = any(s["decision_ref"] == record_ref(decision) and sid not in graph["pending_selections"] for sid, s in graph["selections"].items())
    if applied: lines += ["", "This exact ticket is already applied. Checks below concern prerequisites for a new application; they do not revoke the historical decision or redo completion."]
    lines += ["", "### Advisory observations", ""] + fields(checks)
    lines += fields({"already_applied": applied})
    lines += ["", "Apply revalidates under its own guard. No aggregate readiness or authorization is granted by this view."]
    return lines


def render_candidates(target, *, works: dict, intents: dict) -> tuple[list[str], dict]:
    from .candidates import read_candidates, check_link, _selected_revision, MAX_CANDIDATES, MAX_DECISIONS, MAX_BYTES
    from .jsonio import canonical_json_bytes
    try:
        observed = read_candidates(target)
    except ContractError as exc:
        return ['', '## 후보 계획 — 확인 불가', '', '- 후보 목록이 비었다는 뜻이 아닙니다. 원본을 보존하고 독립된 신뢰 source로 확인하세요.',
                '- code: ' + code(exc.code), '- 이유: ' + text(exc.message)], {'available': False, 'error_code': exc.code, 'message': exc.message}
    store = observed['store']
    lines = ['', '## 후보 계획 — 실행 승인 아님', '', '- 기록된 Owner 선택은 agent 기록이며 인증이 아닙니다. 추천만 하는 조회는 쓰지 않습니다.',
             '- 명령: ' + code('hv2 view candidates') + '; ' + code('hv2 candidate --help'),
             '- 이 control checkout/branch의 기록만 읽습니다. 다른 branch의 기록은 포함하지 않습니다.',
             '- 후보 기록 digest: ' + code(observed['sha256'] or 'none')]
    if not observed['present']:
        return lines + ['- 이 checkout에는 후보 기록이 없습니다. 다른 branch일 수 있습니다.'], observed
    count = len(store['candidates']); decisions = len(store['decisions']); size = len(canonical_json_bytes(store))
    lines += [f'- 한도: 후보 {count}/{MAX_CANDIDATES}, 결정 {decisions}/{MAX_DECISIONS}, bytes {size}/{MAX_BYTES}.']
    if count >= MAX_CANDIDATES * .8 or decisions >= MAX_DECISIONS * .8 or size >= MAX_BYTES * .8:
        lines += ['- 한도 근접: 초과 쓰기는 미저장으로 거부합니다. 이력을 삭제하지 말고 지원 한도/후속 제품 판단을 요청하세요.']
    for cid, row in sorted(store['candidates'].items()):
        lines += ['', '### ' + text(cid) + ' — ' + text(row['title']), '- 목적: ' + text(row['purpose']), '- 기대 효과: ' + text(row['expected_effect']), '- 후보 처분: ' + text(row['disposition']), '- 최근 이유: ' + text(row['reason'])]
        linked_work = False; bad_link = False; linked_intent = False; intent_ids = set()
        for ref in row['links']:
            try:
                g = check_link(ref, store['authority_home_id'], works, intents, current=False)
                same = _selected_revision(g) == ref['revision_ref']
                label = 'current' if same else 'historical link; current revision differs'
                if ref['kind'] == 'work':
                    linked_work = True
                    lines += ['- 관련 Work: ' + text(ref['id']) + ' / 실제 상태: ' + text(g['state']) + ' / ' + text(label), '- 선택 소진: 이 후보로 다시 착수하지 말고 실제 Work의 다음 행동 또는 새 후속 후보를 검토하세요.']
                else:
                    linked_intent = True; intent_ids.add(ref['id'])
                    lines += ['- 관련 intent: ' + text(ref['id']) + ' / ' + text(label)]
            except ContractError as exc:
                bad_link = True
                lines += ['- 관련 대상 확인 불가: ' + text(ref['id']) + ' / ' + text(exc.message)]
        inferred_works = []
        if not linked_work and intent_ids:
            for wid, graph in sorted(works.items()):
                if any((r.get('intent_ref') or {}).get('id') in intent_ids for r in graph['revisions'].values()):
                    inferred_works.append(wid)
                    lines += ['- 이 intent를 사용한 Work: ' + text(wid) + ' / 실제 상태: ' + text(graph['state'])]
            if inferred_works:
                lines += ['- 후보 연결 미완료: Work를 다시 만들지 말고 기존 Work의 범위·현재 revision을 확인한 뒤 link를 재시도하세요. 연결은 자동 저장하지 않습니다.']
        if row['disposition'] == 'deferred' and not linked_work and not inferred_works:
            lines += ['- 재개 조건: ' + text(row['resume_condition'] or '미정 — 자동 재개하지 않음')]
        elif row['disposition'] == 'deferred':
            lines += ['- deferred는 과거 후보 기록입니다. 현재 진행과 재개 판단은 실제 Work에서 확인하세요.']
        if row['related_candidates']: lines += ['- 관련 후보: ' + text(', '.join(row['related_candidates']))]
        if store['selected'] == cid:
            decisions_for_selection = [d for d in store['decisions'] if d['request']['action'] == 'select' and d['request']['candidate_id'] == cid]
            latest = decisions_for_selection[-1]['request']
            lines += ['- 기록된 Owner 선택 (agent 기록, 인증 아님): ' + text(latest['reason']), '- 발화 근거: ' + text(latest['owner_statement'])]
            if bad_link: lines += ['- 다음 행동: 연결 확인 필요; 새 실행 승인이나 준비 완료로 해석하지 마세요.']
            elif not linked_work and not inferred_works: lines += ['- 다음 행동: ' + ('수락된 intent의 currentness와 범위를 확인하고 Work 준비.' if linked_intent else 'intent 구체화·Owner 수락 필요. 선택만으로 실행하지 않습니다.')]
    lines += ['', '- 제품은 우선순위 점수·조건 충족·자동 재개를 판단하지 않습니다. Agent 추천과 저장된 선택, 실제 Work 권한을 구분하세요.']
    return lines, observed


def render_view(target, *, kind=None, object_id=None, revision=None, ticket=None, installed=False):
    """Return GFM and exit status; make no filesystem changes even on degraded input."""
    try:
        target = safe_target(target)
        _require(kind in (None, "intent", "work", "confirmation", "candidates"), "unknown view kind")
        _require((kind in ("intent", "work")) == (object_id is not None), "view object ID required only for intent/work")
        _require(revision is None or kind in ("intent", "work"), "revision requires intent/work")
        _require((kind == "confirmation") == (ticket is not None), "confirmation requires ticket input")
        for attempt in range(2):
            status, works, intents = before = _observe(target)
            classification = status["classification"]
            lines = ["# Harness v2 — project review", "", "Read-only observation; human acceptance and exact application remain separate.", ""]
            lines += fields({"target": str(target), "entry": "installed launcher; target release observed separately" if installed else "independent source; not the bound release", "status": {k: v for k, v in status.items() if k in {"classification", "topology", "authoritative_control", "pending_work", "pending_intent", "next_action", "error_code", "reason", "lifecycle_ready", "retired_entry_collision"}}})
            if "runtime" in status: lines += fields({"runtime_supported": status["runtime"].get("supported", "unavailable")})
            product = _product(target)
            if product:
                from .product import WINDOW_ADAPTERS
                root = str(Path(product["release_path"]).relative_to(target) / "payload")
                lines += ["", "## Next entry", ""] + fields({"manual": root + "/docs/README.md", "natural_language_adapter": root + "/" + WINDOW_ADAPTERS[product["inventory"]["inventory_id"]]})
            if classification not in ("degraded", "uninitialized", "incompatible", "unstable"):
                if status.get("planning", {}).get("available") is False and kind not in (None, "candidates"):
                    candidate_lines, _ = render_candidates(target, works=works, intents=intents)
                    lines += candidate_lines
                if kind == "work":
                    _require(object_id in works, "Work not found"); lines += _work(target, works[object_id], revision, product, intents, works)
                elif kind == "intent":
                    _require(object_id in intents, "intent not found"); lines += _intent(target, intents[object_id], revision)
                elif kind == "confirmation": lines += _confirmation(target, ticket, works, intents, product)
                elif kind == "candidates":
                    candidate_lines, _ = render_candidates(target, works=works, intents=intents)
                    lines += candidate_lines
                else:
                    candidate_lines, _ = render_candidates(target, works=works, intents=intents)
                    lines += candidate_lines
                    lines += ["", "## Intents", ""]
                    for key, g in sorted(intents.items()): lines += fields({"intent": key, "current_accepted_revision": _current_revision(g), "drafts": list(g["drafts"]), "pending": g["pending_acceptances"] + g["pending_selections"]})
                    if not intents: lines += ["- No accepted intent or draft. Ask your agent to clarify the goal and propose an intent."]
                    lines += ["", "## Works", ""]
                    for key, g in sorted(works.items()): lines += fields({"work": key, "stored_state": g["state"], "current_revision": _current_revision(g), "pending": g["pending_decisions"] + g["pending_selections"]})
                    if not works: lines += ["- No Work. Start only after the human has accepted an intent."]
            if before == _observe(target): return "\n".join(lines) + "\n", EXITS.get(classification, 0)
        return "# Observation unstable\n\nPreserve records and retry; no current-state claim is available.\n", 10
    except (ContractError, OSError, ValueError, KeyError, RecursionError) as exc:
        return "# Review unavailable\n\n" + "\n".join(fields({"code": getattr(exc, "code", "HV2-VIEW-UNAVAILABLE"), "reason": getattr(exc, "message", str(exc)), "next_action": "preserve files; inspect using an independent trusted source"})) + "\n", 65

    except (TypeError, AttributeError, IndexError) as exc:
        return "# Review unavailable\n\nInternal observation error: " + text(type(exc).__name__) + ". Preserve records; no current-state claim.\n", 70


def run(args, *, installed):
    try:
        ticket = None
        if args.input is not None:
            raw = sys.stdin.buffer.read(READ_LIMIT + 1) if args.input == "-" else bounded_bytes(Path(args.input))
            ticket = decode_json_bytes(raw, require_canonical=True)
        return render_view(args.target, kind=args.kind, object_id=args.object_id, revision=args.revision, ticket=ticket, installed=installed)
    except (ContractError, OSError, ValueError) as exc:
        return "# Confirmation unavailable\n\n" + text(getattr(exc, "message", str(exc))) + "\n", 65
