"""Read-only, sealed-evidence timing report; no product imports or test dispatch."""
import ast
import json
import math
from pathlib import Path
import re
import sys
from common import canonical, config, digest, exclusive_json, read_json, regular, require, require_isolated


def family(test_id):
    class_name, method = test_id.rsplit(".", 1)
    match = re.fullmatch(r"test_p2_([a-z][0-9])_[0-9]{4}", method)
    if match:
        return class_name + "." + match[1]
    if method == "test_p2_t0_actual_member_trace_and_d3_map":
        return test_id
    if class_name.endswith("DelegationWindowTests"):
        return test_id
    return class_name


def row_kinds(source):
    """Literal AST metadata only; do not import/execute the factory to classify it."""
    path = source / "tests/test_entry_window_transition.py"
    if not path.exists():
        return {}
    values = {}
    for node in ast.parse(regular(path)).body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            try:
                values[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                pass
    result = {}
    for group in ("A1", "A2", "B1", "B2", "C1", "C2", "C3", "C4", "X1"):
        rows = values.get("P2_" + group + "_ROWS") or values.get("P2_" + group + "_CELLS")
        if group == "C4":
            rows = values["P2_C4_MAP"]["rows"]
        if group == "X1":
            rows = values["P2_X1_MAP"]["additional"]
        require(rows, "missing fixed row metadata")
        for index, row in enumerate(rows, 1):
            if isinstance(row, dict):
                name = row["id"]
                kind = str(row.get("kind", "unspecified"))
            else:
                name = "test_p2_" + group.lower() + "_" + str(index).zfill(4)
                kind = str(row[0] if group == "A1" else row[4])
            result["test_entry_window_transition.EntryProductTests." + name] = kind
    for i in range(62):
        result["test_entry_window_transition.EntryProductTests.test_p2_g2_" + str(i+1).zfill(4)] = "fsync-before" if i % 2 == 0 else "fsync-after"
    return result


def selection(collection, source, seeds, known_durations=None):
    known_durations = known_durations or {}
    """Deterministic reviewed selection, frozen after the exact final collection.

Include base seeds, the heavy trace, terminal row per heterogeneous kind and
at least one method per remaining class. Selection never replaces full coverage.
"""
    ids = [row["id"] for row in collection["ordered"]]
    require(not collection["duplicates"] and len(ids) == len(set(ids)), "selection duplicate IDs")
    kinds = row_kinds(source)
    groups = {}
    for test_id in ids:
        groups.setdefault((family(test_id), kinds.get(test_id, "ordinary")), []).append(test_id)
    chosen = set(seeds)
    require(chosen <= set(ids), "base seed absent from final default discovery")
    trace = "test_entry_window_transition.EntryProductTests.test_p2_t0_actual_member_trace_and_d3_map"
    if trace in ids:
        chosen.add(trace)
    for (name, kind), members in groups.items():
        measured = [x for x in members if x in known_durations]
        chosen.add(max(measured,key=lambda x:known_durations[x]) if measured else members[-1] if any(x in kinds for x in members) else members[0])
    return [test_id for test_id in ids if test_id in chosen]


def summarize(ids, durations, kinds, collect_seconds, overhead_seconds=0):
    groups = {}
    for test_id in ids:
        groups.setdefault(family(test_id), []).append(test_id)
    rows = []
    unknown = []
    subtotal = 0.0
    for name, members in sorted(groups.items()):
        samples = {test_id: durations[test_id] for test_id in members if test_id in durations}
        histogram = {}
        for test_id in members:
            key = kinds.get(test_id, "ordinary")
            histogram[key] = histogram.get(key, 0) + 1
        observed_kinds = {kinds.get(test_id, "ordinary") for test_id in samples}
        kind_estimates = {}
        for kind,count in histogram.items():
            observed=[seconds for test_id,seconds in samples.items() if kinds.get(test_id,"ordinary")==kind]
            kind_estimates[kind]=count*max(observed) if observed else None
        missing_kinds = set(histogram)-observed_kinds
        estimate = sum(kind_estimates.values()) if not missing_kinds else None
        if estimate is None:
            unknown.append(name)
        else:
            subtotal += estimate
        rows.append({"family": name, "ids": members, "kind_histogram": histogram,
            "samples": [{"id": test_id, "seconds": seconds, "kind": kinds.get(test_id, "ordinary")} for test_id,seconds in samples.items()],
            "unmeasured_kinds": sorted(missing_kinds), "kind_estimates": kind_estimates, "extrapolated_seconds": estimate,
            "confidence": "low; sample extrapolation is not an actual-duration bound"})
    extrapolated = 2 * (subtotal + collect_seconds + max(0,overhead_seconds-collect_seconds)) + 450
    return {"families": rows, "unmeasured_families": unknown, "measured_family_seconds": subtotal,
        "collect_seconds": collect_seconds, "sample_overhead_seconds": overhead_seconds, "measured_family_estimate_subtotal": extrapolated,
        "complete_estimate": extrapolated if not unknown and all(not r["unmeasured_kinds"] for r in rows) else None,
        "meaning": "A subtotal of the approved estimator, not a lower bound on actual runtime; unknown families are not assigned zero."}


def report(c, p):
    import controller
    controller.completed(c, p, "collect", "final", same_source=True)
    final = p["exec"] / "runs/collect-final"
    collection = read_json(final / "work/collection.json")
    require(digest(regular(final / "work/collection.json")) == c["collection_sha256"], "final collection drift")
    all_ids = [row["id"] for row in collection["ordered"]]
    require(not collection["duplicates"] and len(all_ids) == len(set(all_ids)), "timing duplicate IDs")
    ids = [row["id"] for row in controller.selected_identities(c,collection,"complete-normal")]
    durations = {}
    samples = []
    nonqualifying = []
    overheads = []
    slots = ("smoke-base", "focused-p1") if c["phase"] == "entry" else ("smoke-base", "focused-core", "focused-transition")
    for name in slots:
        anchor = p["exec"] / "runs" / name
        if not (anchor / "inputs.json").exists():
            continue
        inputs = read_json(anchor / "inputs.json")
        mode, slot = name.split("-", 1)
        result = read_json(anchor / "result.json")
        require(result["inputs_sha256"] == digest(regular(anchor / "inputs.json")), "sample parent seal drift")
        qualified = result["execution_pass"] is True
        if qualified:
            controller.completed(c, p, mode, slot, same_source=True)
        else:
            note = {"run":name,"reason":result["reason"],"group_absent":result["group_absent"],"input_unchanged":result["inputs_unchanged_or_acquired_exact"],"used_for_diagnostic_estimate":False}
            nonqualifying.append(note)
            if not result["group_absent"] or result["cleanup_errors"] or not result["inputs_unchanged_or_acquired_exact"]:
                continue
            seals = result.get("partial_child_evidence",{})
            for member,value in seals.items():
                require(digest(regular(anchor / "work" / member)) == value, "partial sample seal drift")
            if not {"collection.json","selected.json","executed.jsonl"} <= set(seals):
                continue
            note["used_for_diagnostic_estimate"] = True
        require(all(inputs[k] == c[k] for k in ("source_digest", "controls", "runtime", "git")), "sample identities differ")
        sample_collection = read_json(anchor / "work/collection.json")
        require(digest(regular(anchor / "work/collection.json")) == inputs["collection_sha256"], "sample collection unbound")
        if inputs["phase"] == "base":
            require(sample_collection["default_ids"] == collection["default_ids"] and not sample_collection["factory_ids"], "base/final ordinary discovery mismatch")
        else:
            require(inputs["collection_sha256"] == c["collection_sha256"], "sample final collection mismatch")
        measured_seconds = 0.0
        for line in regular(anchor / "work/executed.jsonl").splitlines():
            row = json.loads(line)
            require(row["id"] in all_ids and row["occurrence"] == 1 and type(row["seconds"]) in (int,float) and math.isfinite(row["seconds"]) and row["seconds"] >= 0, "invalid sample")
            measured_seconds += row["seconds"]
            if row["outcome"] == "pass":
                durations[row["id"]] = max(durations.get(row["id"], 0), row["seconds"])
        unattributed = max(0,result["seconds"]-measured_seconds)
        if qualified:overheads.append(unattributed)
        samples.append({"qualifying_run":qualified,"run_seconds":result["seconds"],"test_seconds":measured_seconds,"unattributed_seconds":unattributed,"path": str(anchor / "work/executed.jsonl"), "sha256": digest(regular(anchor / "work/executed.jsonl")), "parent_result_sha256": digest(regular(anchor / "result.json"))})
    result = summarize(ids, durations, row_kinds(p["source"]), read_json(final / "result.json")["seconds"], max(overheads,default=0))
    if nonqualifying:result["complete_estimate"] = None
    result["nonqualifying_runs"] = nonqualifying
    result.update({"schema": 1, "lane": p["root"].name, "source_digest": c["source_digest"], "controls": c["controls"],
        "runtime": c["runtime"], "collection_sha256": c["collection_sha256"], "samples": samples,
        "retained_limit_exceeded": c["phase"] == "entry" and result["measured_family_estimate_subtotal"] > 5400,
        "pair_limit_exceeded_by_this_subtotal": result["measured_family_estimate_subtotal"] > 10800})
    policy = read_json(p["controls"] / "campaign.json")
    result["limits_enforced"] = policy["schema"] != 2
    if policy["schema"] == 2:
        result["limit_comparison_meaning"] = "Historical thresholds only; estimates never stop execution or turn unknown durations into zero."
    return result


if __name__ == "__main__":
    require_isolated()
    require(len(sys.argv) == 3, "expected INPUT SHA")
    c,p = config(sys.argv[1],sys.argv[2])
    value = report(c,p)
    path = p["root"].parent / (p["root"].name + "-calibration-report.json")
    exclusive_json(path,value)
    print(canonical({k:value[k] for k in ("lane","measured_family_estimate_subtotal","complete_estimate","retained_limit_exceeded","pair_limit_exceeded_by_this_subtotal","unmeasured_families")}).decode())
