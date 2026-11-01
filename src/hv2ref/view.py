"""Read-only human projection. No authority, publication or runtime mutation seam."""
from __future__ import annotations

import hashlib
import os
import re
import shlex
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
                   verify_worker_sources, observe_recovery, preflight_changed_paths, _bound_delegation)

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
    if sys.platform == "win32":
        from .jsonio import windows_bounded_bytes
        return windows_bounded_bytes(path, READ_LIMIT)
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
    if graphs is not None: return status, *graphs
    if status["classification"] in ("degraded", "uninitialized", "incompatible", "unstable"):
        return status, {}, {}
    # Partial bootstrap has no readable authority yet; pending records and detach do.
    if not (target / ".hrn/format.json").is_file(): return status, {}, {}
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


def _delegation_observation(target, graph, revision, intents, works):
    """Advisory recorded conditions, never an authorization or a prepared ticket.

The supplied graphs come from strict shared readers. Live evidence/content and
caller authentication remain outside these observations; apply checks its guard.
"""
    from .intent import _resolve_workspace_intent
    identity = graph["identity"]
    grant, key = _bound_delegation(identity, revision, intents)
    if grant is None:
        return None
    bound, _ = _resolve_workspace_intent(intents[revision["intent_ref"]["id"]],
                                        revision["intent_ref"]["id"], revision["intent_ref"])
    consumed = []
    for decision in graph["decisions"].values():
        ticket = decision["confirmation"]
        if ticket["actor"] != identity["acceptance_authority"]:
            prior = _resolve(graph["revisions"], ticket["target_revision_ref"])
            _, used_key = _bound_delegation(identity, prior, intents)
            if key is not None and used_key == key:
                consumed.append(record_ref(decision))
    revoked = []; ordinary_ancestry = True
    ref = graph["current"]["selection_ref"] if graph["current"] else None
    while ref is not None:
        selected = _resolve(graph["selections"], ref)
        ancestor = _resolve(graph["revisions"], selected["revision_ref"])
        ordinary_ancestry &= ancestor["schema_version"] == 1
        decision = _resolve(graph["decisions"], selected["decision_ref"], nullable=True)
        if decision is not None and decision["confirmation"]["action"] == "revoke":
            accepted = _resolve(graph["decisions"], decision["confirmation"]["supersedes_decision_ref"])
            prior = _resolve(graph["revisions"], accepted["confirmation"]["target_revision_ref"])
            _, revoked_key = _bound_delegation(identity, prior, intents)
            if key is not None and revoked_key == key:
                revoked.append(record_ref(decision))
        ref = selected["parent_selection_ref"]
    blockers = []
    if key is None: blockers.append("grant names another Work")
    if consumed: blockers.append("delegation already consumed")
    if revoked: blockers.append("selected revoke bars this delegation draft")
    if not bound["is_current"]: blockers.append("stale intent selection")
    intent = intents[revision["intent_ref"]["id"]]
    if intent["pending_acceptances"] or intent["pending_selections"]:
        blockers.append("intent publication pending")
    if graph["pending_decisions"] or graph["pending_selections"]:
        blockers.append("Work publication pending")
    if revision["record_id"] != _current_revision(graph):
        blockers.append("displayed revision is not current")
    if graph["state"] != "review" or revision["operation"] != "submit-result":
        blockers.append("new accept needs an undecided submitted result")
    if (revision["schema_version"] != 1 or not ordinary_ancestry
            or revision["execution_context"]["mode"] != "isolated-worktree"
            or set(revision["scope"]) != set(grant["scope"])):
        blockers.append("delegated Work scope/mode/role differs")
    try:
        WorkStore(target)._pending_guard(works, identity["work_id"], content_write=True)
    except ContractError as exc:
        blockers.append(exc.message)
    return {"grant_ref": revision["intent_ref"], "Owner": identity["acceptance_authority"],
            "declared_delegate": grant["delegate_actor"],
            "consumed_decisions": sorted(consumed, key=lambda r: r["id"]),
            "selected_revoke_barriers": revoked,
            "current_record_conditions": "blocked" if blockers else "no recorded blocker observed",
            "blockers": sorted(set(blockers)),
            "limit": "Advisory only. Live documents/content, runtime, caller and guarded apply remain required; historical acceptance is unchanged."}


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
    actors = []
    for child in evidence["children"]:
        child_graph = works[child["work"]["id"]]
        child_revision = _resolve(child_graph["revisions"], child["revision_ref"])
        decision = _resolve(child_graph["decisions"], child["decision_ref"])
        grant, _ = _bound_delegation(child_graph["identity"], child_revision, intents)
        actors.append({"work": child["work"], "actual_acceptance_actor": decision["confirmation"]["actor"],
                       "Owner": child_graph["identity"]["acceptance_authority"],
                       "grant_ref": child["intent_ref"] if grant is not None else None,
                       "acceptance_delegation": grant})
    lines += fields({"포착된 하위 수락의 역사적 주체와 근거": actors})
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
    lines += _continuation(target, graph, works)
    if rid is None: return lines
    _require(rid in graph["revisions"], "view revision not found")
    r = graph["revisions"][rid]; manifest = _resolve(graph["manifests"], r["result_refs"]["manifest"])
    lines += ["", "## Selected revision fields (recorded at publication)" if rid == current else "## Historical or unselected proposal", "", "Recorded progress and next_action are historical agent fields, not a new action request or the current derived Work state.", ""]
    lines += fields({key: r[key] for key in ("record_id", "author", "operation", "progress", "scope", "next_action", "observed_scope", "unavailable_scope", "relations", "rebind_from", "execution_context")})
    if r["schema_version"] == 2:
        lines += _umbrella_lines(target, r, graph, works, intents)
    try:
        bound = read_workspace_intent(target, r["intent_ref"]["id"], r["intent_ref"], require_current=False)
        lines += fields({"bound_intent_current": bound["is_current"], "acceptance_delegation": bound["acceptance_delegation"]})
        observed = _delegation_observation(target, graph, r, intents, works)
        if observed is not None:
            lines += fields({"current_delegation_conditions": observed})
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



def _continuation(target, base, works):
    from .continuation import current_snapshot, resolve_snapshot
    state = base["continuation"]
    wid = base["identity"]["work_id"]
    lifecycle = fields({"source_work": wid, "source_work_state": base["state"],
                        "source_work_current_selection": base["current"]})
    if state is None:
        return ["", "## 후속 선택과 사용량 — 확인 불가", ""] + lifecycle + [
            "- 검증된 Work 상태와 손상된 후속 기록은 별개입니다. 손상된 기록은 보존하세요.",
            "- 미정, 후속 없음, 사용량 0 또는 잔여 횟수로 추정하지 않습니다. 모든 공식 작성은 차단됩니다."]
    choice = state["effective_choice"]; ticket = state["effective_ticket"]
    labels = {"proposal": "후속 제안 — 아직 Work 아님", "work": "기존 Work 선택", "none": "후속 작업 없음"}
    lines = ["", "## 후속 선택 — " + text(wid), "",
             "- 상태: " + (labels[choice["kind"]] if choice else "미정"),
             "- 이 선택은 대상 실행이나 결과 수락을 승인하지 않습니다.",
             "- 명령: " + code("view continuation " + wid) + "; " + code("continuation --help")]
    lines += lifecycle + fields({"current": state["current"], "usage": state["usage"]})
    if state["usage"]["normal_remaining"] == 0:
        lines += ["- 일반 선택·철회 256회 한도에 도달했습니다. 새 일반 연산은 거부하며 기존 정확한 발행 재개·취소는 허용합니다. 이력을 삭제하거나 사용량을 초기화하지 마세요."]
    if ticket:
        lines += fields({"recorded_choice": choice, "owner_statement": ticket["owner_statement"],
                         "reason": ticket["reason"], "source_snapshot": ticket["source"],
                         "source_selection": "current" if current_snapshot(base) == ticket["source"] else "historical/stale"})
        bound = read_workspace_intent(target, ticket["source"]["intent_ref"]["id"],
                                      ticket["source"]["intent_ref"], require_current=False)
        lines += fields({"source_bound_intent_current": bound["is_current"]})
        if choice["kind"] == "work":
            selected = choice["target"]; other = works[selected["object"]["id"]]
            recorded = resolve_snapshot(selected, other)
            live_snapshot = current_snapshot(other)
            live = resolve_snapshot(live_snapshot, other)
            purpose = lambda rev: (rev["intent_ref"], set(rev["scope"]), rev["execution_context"]["mode"])
            comparison = ("selection-current" if selected == live_snapshot else
                          "target-progressed" if purpose(recorded) == purpose(live) else "target-purpose-changed")
            bound = read_workspace_intent(target, live["intent_ref"]["id"], live["intent_ref"], require_current=False)
            lines += fields({"target_observation": comparison, "target_current": live_snapshot,
                             "target_state": other["state"], "target_bound_intent_current": bound["is_current"],
                             "target_pending": other["pending_decisions"] + other["pending_selections"],
                             "target_continuation_pending": (other["continuation"]["pending"]
                                                             if other["continuation"] is not None else "unavailable")})
            lines += ["- 현재 요청과 대상 Work·intent의 기존 권한을 확인하세요. 진행·거절·철회·목적 변경으로 자동 재선택하지 않습니다."]
        lines += ["", "### 선택 근거의 현재 관찰", ""] + references(target, ticket)
        changed = [ref["path"] for ref in ticket["document_refs"]
                   if ref["required"] and reference_observation(target, ref) != "matches"]
        if changed:
            lines += ["- 필수 선택 근거가 변경되었거나 확인 불가합니다. 이 근거로 실행을 정당화하지 마세요."] + fields({"changed_required_refs": changed})
    if state["pending"]:
        pending = state["choices"][state["pending"]]
        lines += ["", "### 발행 중 — 선택 완료 아님", ""] + fields({"pending_choice_ref": record_ref(pending),
                  "action": pending["confirmation"]["action"], "request_id": pending["confirmation"]["request_id"]})
        lines += ["- 원래 ticket의 정확한 발행을 재개하거나 미해결 일반 선택을 명시적으로 취소하세요. 취소 발행 중에는 그 취소만 재개합니다."]
    lines += ["", "### 보존된 선택 이력 — 시간순 아님", ""]
    for cid, item in sorted(state["choices"].items()):
        t = item["confirmation"]
        lines += fields({"choice": record_ref(item), "action": t["action"], "request_id": t["request_id"],
                         "cancelled_by": state["cancelled"].get(cid),
                         "selected_history": "selection-" + _digest(t) in state["chain"]})
    return lines


def _continuation_confirmation(target, ticket, works, product):
    from .continuation import ContinuationStore, validate_ticket as validate_continuation_ticket, records
    validate_continuation_ticket(ticket)
    wid = ticket["source"]["object"]["id"]
    _require(wid in works, "continuation source Work unavailable")
    base = works[wid]; state = base["continuation"]; choice, selection = records(ticket)
    lines = ["## 후속 선택 확인 — Owner 판단 필요", "",
             "- 조회는 승인·적용·완료가 아닙니다. 대상 Work의 실행 권한도 부여하지 않습니다.", ""]
    lines += fields(ticket) + fields({"confirm_token": _digest(ticket)[:16], "usage": state["usage"]})
    lines += references(target, ticket)
    applied = selection["record_id"] in state["chain"]
    cancelled = choice["record_id"] in state["cancelled"]
    lines += fields({"already_applied": applied, "cancelled": cancelled})
    if applied or cancelled:
        lines += ["- 이미 해결된 정확한 ticket입니다. 재시도는 과거 선택을 current로 올리지 않으며 일반 사용량을 더 쓰지 않습니다."]
    else:
        try:
            _require(product is not None, "verified active product unavailable")
            _require(product["inventory"]["inventory_id"] in ("continuation-1", "windows-2", "official-execution-1"), "continuation-capable runtime required")
            runtime = {key: product[key] for key in ("binding_ref", "launcher_sha256")}
            runtime["inventory_id"] = product["inventory"]["inventory_id"]
            store = ContinuationStore(target)
            store._check(ticket, works, runtime, existing=choice["record_id"] in state["choices"])
            _, _, usage = store._prospective(base, state, ticket)
            lines += fields({"advisory_observation": "matches", "prospective_usage": usage})
        except (ContractError, KeyError, OSError, ValueError) as exc:
            lines += fields({"advisory_observation": "unavailable or refused", "reason": getattr(exc, "message", str(exc))})
    lines += ["", "- apply는 공유 writer guard 안에서 조건을 다시 확인합니다. 이 화면은 실행 준비 완료나 승인을 판정하지 않습니다."]
    return lines


def _confirmation(target, ticket, works, intents, product):
    if isinstance(ticket, dict) and ticket.get("record_type") == "continuation-confirmation-ticket":
        return _continuation_confirmation(target, ticket, works, product)
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
        lines += ["- Read the proposed intent content before deciding: " + code("view intent " + key + " --revision " + ticket["target_revision_ref"]["id"])]
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
            work_graph(graph["identity"], graph["revisions"], decisions, graph["selections"], graph["manifests"], graph["current"], intent_graphs=intents)
            existing = [v for v in graph["selections"].values() if v["decision_ref"] == record_ref(decision)]
            selection = existing[0] if existing else {**{k: r[k] for k in _RECORD_BASE | _PROVENANCE}, "schema_version": 1, "record_type": "work-selection", "record_id": "selection-" + _digest(ticket), "observed_at": ticket["observed_at"], "parent_selection_ref": ticket["expected_selection_ref"], "revision_ref": ticket["target_revision_ref"], "decision_ref": record_ref(decision), "operation_id": ticket["request_id"]}
            work_graph(graph["identity"], graph["revisions"], decisions, graph["selections"] | {selection["record_id"]: selection}, graph["manifests"], graph["current"], intent_graphs=intents)
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


def render_candidates(target, *, works: dict, intents: dict, brief=False) -> tuple[list[str], dict]:
    from .candidates import read_candidates, check_link, _selected_revision, MAX_CANDIDATES, MAX_DECISIONS, MAX_BYTES
    from .jsonio import canonical_json_bytes
    try:
        observed = read_candidates(target)
    except ContractError as exc:
        return ['', '## 후보 계획 — 확인 불가', '', '- 후보 목록이 비었다는 뜻이 아닙니다. 원본을 보존하고 독립된 신뢰 source로 확인하세요.',
                '- code: ' + code(exc.code), '- 이유: ' + text(exc.message)], {'available': False, 'error_code': exc.code, 'message': exc.message}
    store = observed['store']
    lines = ['', '## 후보 계획 — 실행 승인 아님', '', '- 기록된 Owner 선택은 agent 기록이며 인증이 아닙니다. 추천만 하는 조회는 쓰지 않습니다.',
             '- 명령: ' + code('view candidates') + '; ' + code('candidate --help'),
             '- 이 control checkout/branch의 기록만 읽습니다. 다른 branch의 기록은 포함하지 않습니다.',
             '- 후보 기록 digest: ' + code(observed['sha256'] or 'none')]
    if brief:
        lines = ['', '## 다음 작업 후보', '', '이 작업 공간에 기록된 계획입니다. 시작할 때 목표·범위와 실행 승인을 확인합니다.']
    if not observed['present']:
        return lines + ['- 이 checkout에는 후보 기록이 없습니다. 다른 branch일 수 있습니다.'], observed
    count = len(store['candidates']); decisions = len(store['decisions']); size = len(canonical_json_bytes(store))
    if not brief: lines += [f'- 한도: 후보 {count}/{MAX_CANDIDATES}, 결정 {decisions}/{MAX_DECISIONS}, bytes {size}/{MAX_BYTES}.']
    if count >= MAX_CANDIDATES * .8 or decisions >= MAX_DECISIONS * .8 or size >= MAX_BYTES * .8:
        lines += ['- 한도 근접: 초과 쓰기는 미저장으로 거부합니다. 이력을 삭제하지 말고 지원 한도/후속 제품 판단을 요청하세요.']
    for cid, row in sorted(store['candidates'].items()):
        if brief:
            disposition = {'open': '검토 중', 'deferred': '보류', 'absorbed': '다른 계획에 반영', 'rejected': '채택하지 않음'}.get(row['disposition'], row['disposition'])
            lines += ['', '### ' + text(row['title']) + ' (' + code(cid) + ')', '- 상태: ' + text(disposition), '- 목적: ' + text(row['purpose']), '- 기대 효과: ' + text(row['expected_effect']), '- 최근 이유: ' + text(row['reason'])]
        else:
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
    if not brief: lines += ['', '- 제품은 우선순위 점수·조건 충족·자동 재개를 판단하지 않습니다. Agent 추천과 저장된 선택, 실제 Work 권한을 구분하세요.']
    return lines, observed


_WORK_STATE_LABELS = {"empty": "선택된 기록 없음", "planned": "계획됨",
                      "active": "진행 중으로 기록됨", "review": "결과 검토 대기",
                      "rework": "재작업 단계", "completed": "결과 수락 완료",
                      "rejected": "반려 기록", "revoked": "수락 철회 기록"}


def _work_state_label(state):
    return _WORK_STATE_LABELS.get(state, "기타(" + text(state) + ")")


def _work_label(wid, graph, intents, *, graph_details=True):
    """Label verified selected data only; optional prose never masks view status."""
    title = None
    revision = None
    if graph_details:
        try:
            selected = _resolve(graph["selections"], graph["current"]["selection_ref"])
            revision = _resolve(graph["revisions"], selected["revision_ref"])
            ref = revision["intent_ref"]
            intent = intents[ref["id"]]
            from .intent import _resolve_workspace_intent
            observed, bound = _resolve_workspace_intent(intent, ref["id"], ref)
            draft = _resolve(intent["drafts"], bound["revision_ref"])
            goal = draft["facets"]["goal"]
            if goal["status"] == "known" and isinstance(goal.get("value"), str):
                value = " ".join(goal["value"].split())
                if value:
                    title = ("" if observed["is_current"] else "이전 목표: ") + text(value[:60] + ("…" if len(value) > 60 else ""))
        except (ContractError, KeyError, ValueError, TypeError, AttributeError, IndexError):
            pass
        if title is None and isinstance(revision, dict):
            scope = revision.get("scope")
            if isinstance(scope, list) and scope and all(isinstance(path, str) and path for path in scope):
                path = scope[0]
                title = "범위: " + text(path[:60] + ("…" if len(path) > 60 else ""))
                if len(scope) > 1:
                    title += " 외 " + str(len(scope) - 1) + "개"
    return (title or "제목 확인 필요") + " (" + code(wid) + ")"


def _problem_explanations(blockers, works, intents, *, graph_details):
    lines = []
    for wid in sorted(blockers.get("continuation_unavailable", {})):
        label = _work_label(wid, works.get(wid), intents, graph_details=graph_details)
        lines += ["- " + label + ": 후속 계획·선택 기록을 읽을 수 없습니다."]
    for key, label in (("pending_work", "작업 기록 처리"), ("pending_intent", "목표 기록 처리"),
                       ("pending_continuation", "후속 계획·선택 기록 처리")):
        if key in blockers:
            lines += ["- " + label + (" 상태를 확인할 수 없습니다." if blockers[key] == "확인 불가" else "가 아직 끝나지 않았습니다.")]
    if "lifecycle_ready" in blockers:
        lines += ["- Colvia 설치·갱신·제거 전에 미해결 기록이나 충돌을 확인해야 합니다."]
    for key in ("message", "reason"):
        if isinstance(blockers.get(key), str):
            lines += ["- 확인된 이유: " + text(blockers[key])]
    explanations = {
        "official_execution": "실행 기록을 읽을 수 없거나 아직 해결되지 않은 실행이 있습니다.",
        "pending_lifecycle": "Colvia 설치·갱신·복구·제거 중 끝나지 않은 처리가 있습니다.",
        "planning": "다음 작업 후보와 선택 기록을 확인할 수 없습니다.",
        "runtime_supported": "현재 실행 환경이 Colvia의 지원 조건을 충족하지 않습니다.",
        "pending_detach": "Colvia 제거 처리가 아직 끝나지 않았습니다.",
        "remaining_files": "제거 처리에서 정리할 파일이 남아 있습니다.",
        "remaining_directories": "제거 처리에서 정리할 폴더가 남아 있습니다.",
        "record_verification": "작업·목표 기록의 검증을 완료하지 못했습니다.",
        "paths": "확인이 필요한 파일 경로가 있습니다.",
        "recovery": "복구 상태와 필요한 조치를 확인해야 합니다.",
        "root_classification": "프로젝트 기록의 기본 구성을 확인해야 합니다.",
        "product_verification": "설치된 Colvia 파일의 검증 결과를 확인해야 합니다.",
        "retired_entry_collision": "이전 실행 진입점과 충돌하는 파일이 있습니다.",
        "error_code": "점검 오류가 발생했습니다. 아래 진단 상세에 오류 코드가 있습니다.",
        "error": "점검 오류가 발생했습니다. 아래 진단 상세에 오류 내용이 있습니다.",
    }
    explained = {"continuation_unavailable", "pending_work", "pending_intent", "pending_continuation",
                 "lifecycle_ready", "message", "reason"}
    for key in blockers:
        if key not in explained:
            lines += ["- " + explanations.get(key, "추가 확인 항목이 있습니다: " + text(key))]
    return lines


def _cli_command(target, installed, command, *arguments):
    launcher = Path(target) / "colvia" if installed else Path(__file__).parents[2] / "colvia"
    args = [str(launcher)] + ([] if installed else ["--source-checkout"])
    args += [command] + ([] if installed else ["--target", str(target)]) + list(arguments)
    if sys.platform == "win32":
        args = [sys.executable, "-I", "-B", *args]
        return "& " + " ".join("'" + arg.replace("'", "''") + "'" for arg in args)
    return shlex.join(args)


def _view_command(target, installed, kind, object_id):
    return _cli_command(target, installed, "view", kind, object_id)


def _display_command(target, installed, command, *arguments):
    """Short POSIX examples run from the displayed project; exact commands stay separate."""
    if installed and sys.platform != "win32":
        return "./colvia " + shlex.join([command, *arguments])
    return _cli_command(target, installed, command, *arguments)


def render_help(target, *, installed=False):
    """Static guidance: no project observation, input consumption or writer."""
    commands = [("작업 현황", ()), ("작업 내용과 검토할 결과", ("work", "WORK_ID")),
                ("기록된 후속 계획", ("continuation", "WORK_ID")),
                ("다음 작업 후보", ("candidates",)), ("목표와 범위", ("intent", "INTENT_ID")),
                ("기술 상세·전체 ID·직접 조회 명령", ("--details",)),
                ("확인할 결정의 상세", ("confirmation", "--input", "TICKET_FILE"))]
    lines = ["# Colvia 도움말", "", "## 말로 물어보기", "",
             "작업 제목이나 ID에 알고 싶은 내용을 붙여 물어보세요.", "",
             '- “작업 진행 화면 개선의 진행 상황과 후속 계획을 보여줘.”',
             '- “다음 작업 후보를 비교하고 하나를 추천해줘.”', "",
             "## 직접 조회하기", ""]
    if installed and sys.platform != "win32":
        lines += ["아래 명령은 프로젝트 폴더에서 실행하세요.", ""]
    for label, args in commands:
        lines += ["- " + label + ": " + code(_display_command(target, installed, "view", *args))]
    lines += ["", "WORK_ID는 작업 제목 옆 괄호의 ID로, INTENT_ID는 기술 상세의 intent 값으로 바꾸세요.",
              "TICKET_FILE에는 준비된 결정 티켓 파일 경로를 넣으세요.", "",
              "짧은 별칭은 " + code(_display_command(target, installed, "?")) + "입니다. 셸에서 ?를 파일명으로 해석하지 않도록 따옴표를 붙이세요.",
              "이 도움말은 조회 안내입니다. 프로젝트 상태는 작업 현황에서 확인하세요."]
    return "\n".join(lines) + "\n"


def _normal_overview(status, product):
    """Only omit raw diagnostics for an explicitly healthy verified observation."""
    runtime, planning = status.get("runtime"), status.get("planning")
    execution = status.get("official_execution")
    return (status.get("classification") == "pass" and status.get("authoritative_control") is True
            and all(status.get(k) == [] for k in ("pending_work", "pending_intent", "pending_continuation"))
            and status.get("lifecycle_ready") is not False and not status.get("continuation_unavailable")
            and isinstance(runtime, dict) and runtime.get("supported") is True
            and isinstance(planning, dict) and planning.get("available") is True
            and (execution is None or isinstance(execution, dict) and execution.get("available") is True
                 and execution.get("ready_for_new_grant") is True)
            and not any(status.get(key) for key in ("error", "error_code", "message", "reason", "paths", "recovery", "product_verification", "pending_lifecycle", "retired_entry_collision", "root_classification"))
            and status.get("record_verification") in (None, "verified")
            and bool(product))


def _work_overview(wid, graph, intents, works):
    lines = ["### " + _work_label(wid, graph, intents), "",
             "- 상태: " + _work_state_label(graph.get("state"))]
    if graph.get("pending_decisions") or graph.get("pending_selections"):
        lines += ["- 확인 필요: 작업 기록 처리가 끝나지 않았습니다."]
    state = graph.get("continuation")
    if not isinstance(state, dict):
        return lines + ["- 후속 계획: 기록을 읽을 수 없습니다.", ""]
    choice = state.get("effective_choice")
    if choice is None:
        follow = "아직 정하지 않음"
    elif choice.get("kind") == "none":
        follow = "후속 작업 없음으로 선택됨"
    elif choice.get("kind") == "proposal":
        goal = " ".join(str(choice.get("goal", "내용 확인 필요")).split())
        follow = "제안 — " + text(goal[:80] + ("…" if len(goal) > 80 else ""))
    elif choice.get("kind") == "work":
        selected = choice.get("target", {})
        target_id = selected.get("object", {}).get("id", "확인 불가")
        other = works.get(target_id)
        recorded = dict(other, current={"selection_ref": selected["selection_ref"]}) if other and "selection_ref" in selected else None
        follow = "작업 연결 기록 — " + _work_label(target_id, recorded, intents)
    else:
        follow = "선택 내용 확인 필요"
    lines += ["- 후속 계획: " + follow]
    ticket = state.get("effective_ticket")
    if ticket:
        from .continuation import current_snapshot
        try:
            if current_snapshot(graph) != ticket["source"]:
                lines += ["- 확인 필요: 후속 선택 이후 이 작업의 기록이 바뀌었습니다."]
            if choice and choice.get("kind") == "work":
                selected = choice["target"]
                other = works.get(selected["object"]["id"])
                if other is None or current_snapshot(other) != selected:
                    lines += ["- 확인 필요: 연결된 작업의 현재 기록을 다시 확인해야 합니다."]
        except (ContractError, KeyError, TypeError, ValueError, AttributeError):
            lines += ["- 확인 필요: 후속 선택과 현재 작업 기록의 일치 여부를 확인할 수 없습니다."]
    elif choice is not None:
        lines += ["- 확인 필요: 후속 선택과 현재 작업 기록의 일치 여부를 확인할 수 없습니다."]
    if state.get("pending"):
        lines += ["- 확인 필요: 후속 선택 기록 처리가 끝나지 않았습니다."]
    remaining = state.get("usage", {}).get("normal_remaining")
    if type(remaining) is not int:
        lines += ["- 확인 필요: 후속 선택의 남은 횟수를 확인할 수 없습니다."]
    elif remaining == 0:
        lines += ["- 확인 필요: 후속 선택 횟수를 모두 사용했습니다."]
    return lines + [""]


def _project_summary(status, works, intents, *, graph_details, target, compact=False, diagnostics_only=False):
    """Use the existing observation, including readable retained graphs; no scan."""
    classification = status["classification"]
    descriptions = {
        "pass": "설치와 작업 기록의 기본 점검을 통과했습니다.",
        "partial": "끝나지 않은 처리나 확인할 수 없는 항목이 있습니다.",
        "degraded": "일부 기록이 손상되었거나 읽을 수 없습니다.",
        "uninitialized": "Colvia 설치 상태를 확인할 수 없습니다.",
        "incompatible": "프로젝트 기록이 현재 Colvia 버전과 호환되지 않습니다.",
        "unsupported": "현재 실행 환경은 Colvia 지원 조건을 충족하지 않습니다.",
        "conflict": "프로젝트 상태에 충돌이 있습니다.",
        "stale": "현재 프로젝트 상태와 저장된 기록이 일치하지 않습니다.",
        "unstable": "확인하는 동안 프로젝트 상태가 바뀌어 결과를 확정할 수 없습니다.",
        "detached": "Colvia가 제거된 상태입니다.",
    }
    work_states = status.get("work_states")
    intent_count = status.get("intent_count")
    # Empty fallback graphs can mean unreadable/bootstrap state, not verified zero.
    work_count = len(work_states) if isinstance(work_states, dict) else len(works) if works else None
    intent_count = intent_count if type(intent_count) is int else len(intents) if intents else None
    counts = "작업 " + (str(work_count) + "개" if work_count is not None else "확인 불가")
    counts += " / 목표 " + (str(intent_count) + "개" if intent_count is not None else "확인 불가")
    blockers = {}
    for key in ("error_code", "error", "reason", "message", "paths", "recovery",
                "root_classification", "product_verification", "pending_lifecycle",
                "retired_entry_collision", "continuation_unavailable"):
        if status.get(key): blockers[key] = status[key]
    if status.get("record_verification") not in (None, "verified"):
        blockers["record_verification"] = status["record_verification"]
    for key in ("pending_work", "pending_intent", "pending_continuation"):
        value = status.get(key)
        if value is None: blockers[key] = "확인 불가"
        elif value: blockers[key] = value
    if status.get("lifecycle_ready") is False:
        blockers["lifecycle_ready"] = False
    planning = status.get("planning")
    if isinstance(planning, dict) and planning.get("available") is False:
        blockers["planning"] = {k: v for k, v in planning.items()
                                if k in {"available", "error_code", "message"}}
    execution = status.get("official_execution")
    if isinstance(execution, dict) and (execution.get("available") is False or
                                      execution.get("ready_for_new_grant") is False):
        blockers["official_execution"] = "확인 불가 또는 미해결 실행 있음; 아래 세부 정보의 공식 실행 항목 참조"
    if status.get("runtime", {}).get("supported") is False:
        blockers["runtime_supported"] = False
    detaching = classification == "partial" and "remaining_files" in status and "remaining_directories" in status
    if detaching:
        descriptions["partial"] = "Colvia 제거가 진행 중입니다."
        blockers["pending_detach"] = status["receipt"]["operation_id"]
        for key in ("remaining_files", "remaining_directories"):
            if status[key]: blockers[key] = status[key]
    if diagnostics_only:
        return (["### 진단 상세", "", "원인 확인에 필요한 기록값입니다.", ""] + fields(blockers) + [""]) if blockers else []
    location_kind = {"primary": "기본 worktree", "linked-worktree": "연결 worktree",
                     "non-git": "프로젝트 폴더", "subdirectory": "저장소 안의 폴더",
                     "submodule": "서브모듈", "separate-git-dir": "worktree",
                     "nested-repository": "중첩 저장소"}.get(status.get("topology"))
    location = code(str(target)) + (" (" + location_kind + ")" if location_kind else "")
    state_map = {key: graph.get("state") for key, graph in works.items()}
    distribution_known = graph_details and work_count is not None and len(works) == work_count and all(state_map.values())
    if distribution_known:
        groups = {state: sum(value == state for value in state_map.values()) for state in set(state_map.values())}
        progress = " · ".join(_work_state_label(state) + " " + str(groups[state]) + "개" for state in sorted(groups)) or "등록된 작업 없음"
    else:
        progress = "상태별 분포 확인 불가"
    attention = {key for key, graph in works.items() if graph_details and
                 (graph.get("state") in ("review", "rejected", "revoked") or graph.get("pending_decisions") or graph.get("pending_selections"))}
    for key in ("pending_work", "pending_continuation"):
        attention.update(status.get(key) or [])
    attention.update(status.get("continuation_unavailable") or {})
    attention_known = distribution_known and all(isinstance(status.get(key), list)
                                                 for key in ("pending_work", "pending_continuation"))
    if attention:
        attention_text = ", ".join(_work_label(key, works.get(key), intents, graph_details=graph_details) for key in sorted(attention))
        if not attention_known:
            attention_text += " (전체 확인 불가)"
    else:
        attention_text = "해당 작업 없음" if attention_known else "확인 불가"
    issue = classification not in ("pass", "detached") or bool(blockers)
    if compact:
        lines = ["## 한눈에 보기", "", "- " + counts + " · " + progress + ".",
                 "- 프로젝트 경로: " + location]
        if issue:
            lines += ["- 먼저 확인: " + (descriptions.get(classification, "프로젝트 상태를 확인해야 합니다.") if classification != "pass" else "확인할 항목이 있습니다.") + " 아래 기술 상세에 원인과 기록값이 있습니다."]
            lines += _problem_explanations(blockers, works, intents, graph_details=graph_details)
        elif not works and work_count == 0:
            lines += ["- " + ("등록된 목표를 바탕으로 시작할 작업을 물어보세요." if intent_count else "원하는 작업을 설명하면 목표와 범위부터 정리할 수 있습니다.")]
        if attention:
            lines += ["- 확인할 작업: " + str(len(attention)) + "개" + (" (전체 확인 불가)" if not attention_known else "") + ". 아래 상태와 확인 필요 항목을 보세요."]
        elif not attention_known:
            lines += ["- 확인할 작업: 확인 불가."]
        missing = sorted(attention - works.keys())
        if missing:
            lines += ["- 추가 확인할 작업 기록: " + ", ".join(code(wid) for wid in missing)]
        return lines + [""]
    lines = ["## 한눈에 보기", ""]
    if issue:
        lines += ["- 먼저 확인: " + (descriptions.get(classification, "확인하지 못한 항목이 있습니다.") if classification != "pass" else "추가로 확인할 사항이 있습니다.") + " 문제·미확인 항목은 아래에 모두 표시합니다."]
    lines += ["- 작업 진행(기록 기준): " + progress + ".",
              "- 확인할 작업: " + attention_text + ".",
              "- " + ("읽을 수 있는 기록: " if issue else "등록된 기록: ") + counts + "."]
    if not issue:
        lines += ["- 설치·기록 점검: " + descriptions.get(classification, "상세 참조")]
    if issue:
        request_hint = "현재 프로젝트에서 확인하지 못한 내용과 다음 확인 방법을 물어보세요."
    elif work_count == 0:
        request_hint = ("등록된 목표를 바탕으로 어떤 작업을 시작할 수 있는지 물어보세요." if intent_count
                        else "원하는 작업을 설명하고 목표와 범위를 정리해 달라고 요청하세요.")
    elif work_count is None:
        request_hint = "현재 프로젝트의 작업 기록과 확인할 사항을 물어보세요."
    else:
        request_hint = "작업 제목이나 ID를 넣어 진행 상황과 후속 계획을 물어보세요."
    lines += ["- 더 알아보기: " + request_hint]
    lines += ["- 프로젝트 경로: " + location,
              ("- 자세히 보기: 아래 목표·작업 목록" + ("과 진단 상세" if blockers else "") + "를 확인하세요. 직접 조회 명령도 별도로 제공합니다.") if graph_details and (works or intents) else "- 자세히 보기: 아래 프로젝트 세부 정보에서 확인한 내용과 추가 확인이 필요한 항목을 볼 수 있습니다.", ""]
    if blockers:
        lines += ["### 문제·미확인 항목 상세", ""]
        lines += _problem_explanations(blockers, works, intents, graph_details=graph_details)
        lines += ["", "#### 진단 상세", "", "원인 확인에 필요한 기록값입니다.", ""] + fields(blockers) + [""]
    return lines


def render_view(target, *, kind=None, object_id=None, revision=None, ticket=None, installed=False, details=False):
    """Return GFM and exit status; make no filesystem changes even on degraded input."""
    try:
        _require(not details or (kind is None and revision is None and ticket is None), "--details requires project view without selector, revision or input")
        target = safe_target(target)
        _require(kind in (None, "intent", "work", "continuation", "confirmation", "candidates"), "unknown view kind")
        _require((kind in ("intent", "work", "continuation")) == (object_id is not None), "view object ID required only for intent/work/continuation")
        _require(revision is None or kind in ("intent", "work"), "revision requires intent/work")
        _require((kind == "confirmation") == (ticket is not None), "confirmation requires ticket input")
        for attempt in range(2):
            status, works, intents = before = _observe(target)
            classification = status["classification"]
            readable_continuation_damage = bool(status.get("continuation_unavailable")) and kind in (None, "work", "continuation", "intent")
            graph_details = classification not in ("degraded", "uninitialized", "incompatible", "unstable") or readable_continuation_damage
            lines = ["# Colvia — project review", "", "Read-only observation; human acceptance and exact application remain separate.", ""]
            product = _product(target)
            if kind is None:
                normal = _normal_overview(status, product)
                show_raw = details or not normal
                lines = ["# 작업 현황", "", "작업 기록을 기준으로 보여드립니다.", ""]
                lines += _project_summary(status, works, intents, graph_details=graph_details, target=target, compact=True)
                if not installed:
                    lines += ["- 조회 출처: 독립된 소스에서 프로젝트를 확인했습니다.", ""]
                if not normal and status.get("classification") == "pass":
                    lines += ["- 먼저 확인: 환경·진입 정보는 아래 기술 상세에서 확인하세요.", ""]
                if graph_details:
                    for wid, graph in sorted(works.items()):
                        lines += _work_overview(wid, graph, intents, works)
                    if not works:
                        lines += ["등록된 작업이 없습니다." if status.get("work_states") == {} else "작업 목록을 확인할 수 없습니다.", ""]
                    candidate_lines, observed_candidates = render_candidates(target, works=works, intents=intents, brief=not show_raw)
                    if isinstance(observed_candidates, dict) and observed_candidates.get("present") is False and not observed_candidates.get("error_code"):
                        lines += ["등록된 다음 작업 후보는 아직 없습니다. 필요하면 다음 할 일을 함께 정리할 수 있습니다.", ""]
                    else:
                        lines += candidate_lines
                footer = "더 알아보기 · " + code(_display_command(target, installed, "help"))
                if not show_raw:
                    footer += " · " + ("기술 상세·안내 문서: " if product else "기술 상세: ") + code(_display_command(target, installed, "view", "--details"))
                if installed and sys.platform != "win32":
                    footer += " (프로젝트 폴더에서 실행)"
                lines += ["", footer, ""]
                if not show_raw:
                    if before == _observe(target): return "\n".join(lines) + "\n", EXITS.get(classification, 0)
                    continue
                lines += ["## 프로젝트 세부 정보", "", "기술 상세와 직접 조회 명령입니다.", ""]
                if product:
                    from .product import WINDOW_ADAPTERS
                    entry_root = (Path(product["release_path"]).relative_to(target) / "payload").as_posix()
                    lines += ["### 안내 문서", "", "- manual: " + code(entry_root + "/docs/README.md"),
                              "- natural_language_adapter: " + code(entry_root + "/" + WINDOW_ADAPTERS[product["inventory"]["inventory_id"]]), ""]
                lines += _project_summary(status, works, intents, graph_details=graph_details, target=target, diagnostics_only=True)
            lines += fields({"target": str(target), "entry": "installed launcher; target release observed separately" if installed else "independent source; not the bound release", "status": {k: v for k, v in status.items() if k in {"classification", "topology", "authoritative_control", "pending_work", "pending_intent", "pending_continuation", "next_action", "error_code", "reason", "message", "lifecycle_ready", "retired_entry_collision", "continuation_unavailable", "official_execution"}}})
            if kind is None:
                extra_keys = {"error", "paths", "recovery", "root_classification", "product_verification", "pending_lifecycle", "record_verification", "planning", "remaining_files", "remaining_directories"}
                lines += fields({k: v for k, v in status.items() if k in extra_keys})
            if "runtime" in status: lines += fields({"runtime_supported": status["runtime"].get("supported", "unavailable")})
            if product and kind is not None:
                from .product import WINDOW_ADAPTERS
                root = (Path(product["release_path"]).relative_to(target) / "payload").as_posix()
                lines += ["", "## Next entry", ""] + fields({"manual": root + "/docs/README.md", "natural_language_adapter": root + "/" + WINDOW_ADAPTERS[product["inventory"]["inventory_id"]]})
            if graph_details:
                if status.get("planning", {}).get("available") is False and kind not in (None, "candidates"):
                    candidate_lines, _ = render_candidates(target, works=works, intents=intents)
                    lines += candidate_lines
                if kind == "work":
                    _require(object_id in works, "Work not found"); lines += _work(target, works[object_id], revision, product, intents, works)
                elif kind == "continuation":
                    _require(object_id in works, "Work not found")
                    lines += _continuation(target, works[object_id], works)
                elif kind == "intent":
                    _require(object_id in intents, "intent not found"); lines += _intent(target, intents[object_id], revision)
                elif kind == "confirmation": lines += _confirmation(target, ticket, works, intents, product)
                elif kind == "candidates":
                    candidate_lines, _ = render_candidates(target, works=works, intents=intents)
                    lines += candidate_lines
                else:
                    lines += ["", "## Intents", ""]
                    query_commands = []
                    for key, g in sorted(intents.items()):
                        lines += fields({"intent": key, "current_accepted_revision": _current_revision(g), "drafts": list(g["drafts"]), "pending": g["pending_acceptances"] + g["pending_selections"]})
                        query_commands += ["- 목표 " + code(key) + ": " + code(_view_command(target, installed, "intent", key))]
                    if not intents: lines += ["- No accepted intent or draft. Ask your agent to clarify the goal and propose an intent." if status.get("intent_count") == 0 else "- 목표 목록을 확인할 수 없습니다."]
                    lines += ["", "## Works", ""]
                    for key, g in sorted(works.items()):
                        label = _work_label(key, g, intents)
                        lines += ["### " + label, "", "- 작업 상태(기록 기준): " + _work_state_label(g["state"]) + "."]
                        state = g["continuation"]
                        choice = state["effective_choice"] if state is not None else None
                        lines += fields({"work": key, "stored_state": g["state"], "current_revision": _current_revision(g),
                                         "pending": g["pending_decisions"] + g["pending_selections"],
                                         "continuation": ("unavailable" if state is None else choice["kind"] if choice else "undecided"),
                                         "pending_continuation": state["pending"] if state is not None else "unavailable",
                                         "continuation_usage": state["usage"] if state is not None else "unavailable"})
                        query_commands += ["- 작업 조회 — " + label + ": " + code(_view_command(target, installed, "work", key)),
                                           "- 후속 기록 조회 — " + label + ": " + code(_view_command(target, installed, "continuation", key))]
                    if not works: lines += ["- No Work. Start only after the human has accepted an intent." if status.get("work_states") == {} else "- 작업 목록을 확인할 수 없습니다."]
                    if query_commands:
                        lines += ["", "## 직접 조회 명령", "", "명령을 직접 사용하는 경우 아래 내용을 사용할 수 있습니다.", ""] + query_commands
            elif kind in ("work", "continuation"):
                lines += ["", "## 후속 선택과 사용량 — 확인 불가", "",
                          "- 손상·미확인 기록을 보존하세요. 미정, 사용량 0 또는 잔여 횟수로 추정하지 않습니다."]
            if before == _observe(target): return "\n".join(lines) + "\n", EXITS.get(classification, 0)
        return "# Observation unstable\n\nPreserve records and retry; no current-state claim is available.\n", 10
    except (ContractError, OSError, ValueError, KeyError, RecursionError) as exc:
        return "# Review unavailable\n\n" + "\n".join(fields({"code": getattr(exc, "code", "HV2-VIEW-UNAVAILABLE"), "reason": getattr(exc, "message", str(exc)), "next_action": "preserve files; inspect using an independent trusted source"})) + "\n", 65

    except (TypeError, AttributeError, IndexError) as exc:
        return "# Review unavailable\n\nInternal observation error: " + text(type(exc).__name__) + ". Preserve records; no current-state claim.\n", 70


def run(args, *, installed):
    details = getattr(args, "details", False)
    if details and (args.kind is not None or args.revision is not None or args.input is not None):
        return "# View unavailable\n\n--details는 선택자, --revision, --input 없이 프로젝트 전체 조회에 사용하세요.\n", 65
    try:
        ticket = None
        details = getattr(args, "details", False)
        _require(not details or (args.kind is None and args.revision is None and args.input is None), "--details requires project view without selector, revision or input")
        if args.input is not None:
            raw = sys.stdin.buffer.read(READ_LIMIT + 1) if args.input == "-" else bounded_bytes(Path(args.input))
            ticket = decode_json_bytes(raw, require_canonical=True)
        return render_view(args.target, kind=args.kind, object_id=args.object_id, revision=args.revision, ticket=ticket, installed=installed, details=details)
    except (ContractError, OSError, ValueError) as exc:
        return "# Confirmation unavailable\n\n" + text(getattr(exc, "message", str(exc))) + "\n", 65
