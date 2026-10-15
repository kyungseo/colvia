"""Exact collection and result reporting; no timeout or assertion substitution."""
from collections import deque
import importlib
import os
from pathlib import Path
import shutil
import stat
import sys
import time
import unittest
from types import MappingProxyType
import controller as control_slots
from common import canonical, config, digest, exclusive_json, read_json, regular, require, verify_old, python_command, unlinked_path


def flatten(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from flatten(test)
        else:
            yield test


CONTEXT_FIELDS = frozenset({"schema", "phase", "invocation_path", "invocation_sha256",
    "controls_dir", "observer_sha256", "work_root", "runtime_path", "runtime_sha256", "observer_command_prefix"})


def build_execution_context(c, p, input_path, input_sha, out):
    require(c["phase"] == "entry", "factory context is entry-only")
    out = unlinked_path(out)
    require(out.name == "work" and out.parent.name in control_slots.ENTRY_RUN_NAMES and
            out.parent.parent == p["exec"] / "runs" and out.is_dir(), "factory WORK boundary")
    require(unlinked_path(control_slots.__file__) == p["controls"] / "controller.py", "controller import outside validated controls")
    invocation = unlinked_path(input_path)
    require(digest(regular(invocation)) == input_sha, "context invocation drift")
    runtime = unlinked_path(c["runtime"]["path"])
    require(digest(regular(runtime)) == c["runtime"]["sha256"], "context runtime drift")
    observer = unlinked_path(p["controls"] / "observer.py")
    require(digest(regular(observer)) == c["controls"]["observer.py"], "context observer drift")
    context = {"schema": 1, "phase": "entry", "invocation_path": str(invocation),
        "invocation_sha256": input_sha, "controls_dir": str(p["controls"]),
        "observer_sha256": c["controls"]["observer.py"], "work_root": str(out),
        "runtime_path": str(runtime), "runtime_sha256": c["runtime"]["sha256"],
        "observer_command_prefix": tuple(python_command(c, p, "observer.py"))}
    require(set(context) == CONTEXT_FIELDS and type(context["schema"]) is int and
            all(isinstance(context[k], str) for k in CONTEXT_FIELDS - {"schema", "observer_command_prefix"}) and
            isinstance(context["observer_command_prefix"], tuple), "context shape")
    return MappingProxyType(context)


def factory_members(suite, ordinary):
    require(isinstance(suite, unittest.TestSuite), "factory must return TestSuite")
    tests = list(flatten(suite))
    require(tests and all(isinstance(t, unittest.TestCase) for t in tests), "mandatory entry factory is empty/invalid")
    ids = [t.id() for t in tests]
    require(len(ids) == len(set(ids)), "duplicate factory ID")
    require(not set(ids).intersection(t.id() for t in ordinary), "factory/default ID overlap")
    return tests


def main():
    require(len(sys.argv) == 5, "expected INPUT SHA OUT MODE")
    c, p = config(sys.argv[1], sys.argv[2])
    require(unlinked_path(control_slots.__file__) == p["controls"] / "controller.py", "controller import outside validated controls")
    out, mode = Path(sys.argv[3]), sys.argv[4]
    require(out.is_relative_to(p["exec"] / "runs") and out.is_dir(), "output boundary")
    require(mode in {"collect", "smoke", "focused", "complete-normal", "complete-parent-O", "artifact"}, "runner mode")
    require(bool(sys.flags.optimize) == (mode == "complete-parent-O"), "parent optimization mismatch")
    verify_old(p["old"], read_json(p["controls"] / "baseline-inputs.json"))
    sys.path[:0] = [str(p["source"] / "src"), str(p["source"] / "tests")]
    # config verified the pinned immediate-root names/types before this append.
    sys.path.append(str(p["source"]))
    os.chdir(p["source"])
    loader = unittest.TestLoader()
    ordinary = list(flatten(loader.discover("tests")))
    require(not loader.errors, "collection load errors: " + repr(loader.errors))
    factory_tests = []
    if c["factory"]:
        module = importlib.import_module("test_entry_window_transition")
        suite = module.build_entry_suite(old_source=p["old"], candidate_source=p["source"],
            expected_predecessor=read_json(p["controls"] / "baseline-inputs.json"),
            prefix_oracle=read_json(p["controls"] / "prefix-oracle.json"),
            execution_context=build_execution_context(c, p, sys.argv[1], sys.argv[2], out))
        factory_tests = factory_members(suite, ordinary)
    tests = ordinary + factory_tests
    ids = [t.id() for t in tests]
    require(tests and all(isinstance(x, str) for x in ids), "empty/invalid collection")
    occurrence = {}
    ordered = []
    for name in ids:
        occurrence[name] = occurrence.get(name, 0) + 1
        ordered.append({"id": name, "occurrence": occurrence[name]})
    collection = {"source_digest": c["source_digest"], "source_root_entries": c["source_root_entries"], "controls": c["controls"],
                  "default_ids": [t.id() for t in ordinary], "factory_ids": [t.id() for t in factory_tests],
                  "ordered": ordered, "duplicates": {k: v for k, v in occurrence.items() if v > 1}}
    payload = canonical(collection)
    exclusive_json(out / "collection.json", collection)
    if mode == "collect":
        print("COLLECTED", len(tests), "sha256", digest(payload), flush=True)
        return
    require(isinstance(c["collection_sha256"], str) and digest(payload) == c["collection_sha256"], "collection identity not fixed or changed")
    if mode in {"complete-normal", "complete-parent-O"}:
        require(c["phase"] == "entry" and not c["selection"], "complete suite cannot have selection")
        selected = list(zip(tests, ordered))
    else:
        selection = set(c["selection"])
        occurrence_tokens = {f"{item['id']}#{item['occurrence']}": item["id"] for item in ordered}
        exact_occurrences = bool(selection) and selection <= occurrence_tokens.keys()
        require(selection and (selection <= set(ids) or exact_occurrences), "missing/empty exact selected IDs or occurrences")
        selected_ids = {occurrence_tokens[token] for token in selection} if exact_occurrences else selection
        if out.parent.name == "focused-p1-controls":
            control_ids = {t.id() for t in factory_tests if getattr(t, "verification_stage", None) == "p1-controls"}
            require(selected_ids <= control_ids, "p1-controls cannot select default or product assertions")
        # Bare IDs retain every occurrence; ID#occurrence resumes only the named execution.
        selected = [(t, identity) for t, identity in zip(tests, ordered)
                    if (f"{identity['id']}#{identity['occurrence']}" in selection if exact_occurrences else t.id() in selection)]
    exclusive_json(out / "selected.json", [identity for _, identity in selected])
    identities = {}
    for test, identity in selected:
        identities.setdefault(id(test), deque()).append(identity)
    repeated_objects = {key for key, values in identities.items() if len(values) > 1}
    class Result(unittest.TextTestResult):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.preserved_bytes = 0
            self.active_test = None
            self.identity = None
            self.started_keys = set()
            self.stopped_keys = set()
            self.nonstart_event_seen = False
        def write_row(self, name, row):
            with (out / name).open("ab") as f:
                f.write(canonical(row).replace(b"\n", b" ") + b"\n")
        def active(self, test):
            return self.active_test is not None and (test is self.active_test or
                getattr(test, "test_case", None) is self.active_test)
        def outcome_event(self, test, outcome, **detail):
            if self.active(test):
                if outcome not in self.outcomes:
                    self.outcomes.append(outcome)
            else:
                self.nonstart_event_seen = True
                self.write_row("suite-events.jsonl", {"id": test.id(), "identity": None,
                    "outcome": outcome, "reason": "no-matching-startTest", **detail})
        def startTest(self, test):
            require(self.active_test is None, "overlapping test execution")
            queue = identities.get(id(test))
            require(queue and queue[0]["id"] == test.id(), "unselected or changed test identity")
            # A fixture event can skip an earlier occurrence of the SAME object.
            # Object identity alone cannot tell which occurrence is now running.
            if self.nonstart_event_seen and id(test) in repeated_objects:
                exclusive_json(out / "identity-stop.json", {"reason": "ambiguous-repeated-object-after-fixture-event",
                    "id": test.id(), "remaining_candidates": list(queue)})
                raise RuntimeError("cannot assign a unique selected occurrence")
            self.identity = queue.popleft()
            self.active_test = test
            self.started = time.monotonic()
            self.outcomes = []
            self.started_keys.add((self.identity["id"], self.identity["occurrence"]))
            super().startTest(test)
            print("START", self.identity, flush=True)
        def stopTest(self, test):
            require(test is self.active_test, "stopTest without matching startTest")
            super().stopTest(test)
            # A later skipped subtest must not hide an earlier failure in this row.
            outcome = next((name for name in ("error", "fail", "subtest-failure", "unexpected-success",
                "expected-failure", "skip", "pass") if name in self.outcomes), "incomplete")
            row = {**self.identity, "seconds": round(time.monotonic() - self.started, 3),
                   "outcome": outcome, "outcomes": self.outcomes}
            self.write_row("executed.jsonl", row)
            self.stopped_keys.add((self.identity["id"], self.identity["occurrence"]))
            print("STOP", row, flush=True)
            self.active_test = None
            self.identity = None
        def preservation_row(self, test, status, reason, **detail):
            return {"id": test.id(), "identity": self.identity if self.active(test) else None,
                    "status": status, "reason": reason, **detail}
        def preservation_stop(self, test, reason, **detail):
            row = self.preservation_row(test, "stopped", reason, **detail)
            try:
                self.write_row("preservation.jsonl", row)
                exclusive_json(out / "preservation-stop.json", row)
            finally:
                try:
                    sys.stdout.flush(); sys.stderr.flush()
                finally:
                    os._exit(87)  # Avoid fixture finalizers; no successful-run claim.
        def preserve(self, test):
            source = None
            stage = "root-inspection"
            try:
                roots = [getattr(test, "base", None), getattr(test, "root", None),
                         getattr(getattr(test, "f", None), "base", None),
                         getattr(getattr(getattr(test, "h", None), "f", None), "base", None)]
                source = next((Path(x) for x in roots if x and Path(x).is_dir() and Path(x).resolve().is_relative_to(p["exec"])), None)
                if source is None:
                    self.write_row("preservation.jsonl", self.preservation_row(test, "unavailable", "no-reachable-root"))
                    return
                source = source.resolve()
                if source == out or out.is_relative_to(source):
                    self.write_row("preservation.jsonl", self.preservation_row(test, "unavailable", "root-contains-output", fixture=str(source)))
                    return
                stage = "size-scan"
                size = 0
                def scan_error(exc):
                    raise exc
                for current, dirs, names in os.walk(source, followlinks=False, onerror=scan_error):
                    for name in names:
                        q = Path(current) / name
                        info = q.lstat()
                        require(stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode), "non-file failure fixture")
                        size += info.st_size
                if size > 64 * 1024 * 1024 or self.preserved_bytes + size > 256 * 1024 * 1024:
                    self.preservation_stop(test, "size-cap", fixture=str(source), size=size)
                stage = "copy"
                target = out / "failures" / (str(len(list((out / "failures").glob("*")))) if (out / "failures").exists() else "0")
                target.parent.mkdir(exist_ok=True)
                shutil.copytree(source, target, symlinks=True)
                self.preserved_bytes += size
                stage = "copy-record"
                self.write_row("preservation.jsonl", self.preservation_row(test, "copied", "reachable-root",
                    fixture=str(source), copy=str(target), counted_bytes=size))
            except (OSError, RuntimeError, TypeError, ValueError) as exc:
                self.preservation_stop(test, "preservation-error", stage=stage,
                    fixture=str(source) if source is not None else None, error_type=type(exc).__name__)
        def addSuccess(self, test):
            self.outcome_event(test, "pass"); super().addSuccess(test)
        def addError(self, test, err):
            self.outcome_event(test, "error"); self.preserve(test); super().addError(test, err)
        def addFailure(self, test, err):
            self.outcome_event(test, "fail"); self.preserve(test); super().addFailure(test, err)
        def addSubTest(self, test, subtest, err):
            if err:
                self.outcome_event(test, "subtest-failure"); self.preserve(test)
            super().addSubTest(test, subtest, err)
        def addSkip(self, test, reason):
            self.outcome_event(test, "skip", skip_reason=reason); super().addSkip(test, reason)
        def addExpectedFailure(self, test, err):
            self.outcome_event(test, "expected-failure"); super().addExpectedFailure(test, err)
        def addUnexpectedSuccess(self, test):
            self.outcome_event(test, "unexpected-success"); super().addUnexpectedSuccess(test)
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2, resultclass=Result, failfast=True).run(unittest.TestSuite(t for t, _ in selected))
    unstarted = [identity for _, identity in selected
                 if (identity["id"], identity["occurrence"]) not in result.started_keys]
    unfinished = [identity for _, identity in selected
                  if (identity["id"], identity["occurrence"]) in result.started_keys - result.stopped_keys]
    exclusive_json(out / "unstarted.json", unstarted)
    exclusive_json(out / "unfinished.json", unfinished)
    counts = {"unstarted": len(unstarted), "unfinished": len(unfinished), "discovered": len(tests), "selected": len(selected), "run": result.testsRun,
              "failures": len(result.failures), "errors": len(result.errors), "skips": len(result.skipped),
              "expected_failures": len(result.expectedFailures), "unexpected_successes": len(result.unexpectedSuccesses)}
    exclusive_json(out / "counts.json", counts)
    ok = result.wasSuccessful() and result.testsRun == len(selected) and not result.skipped and not result.expectedFailures and not unstarted and not unfinished
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
