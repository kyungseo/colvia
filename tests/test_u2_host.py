"""Preflight classifier checks are not live host permission qualification."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

from tests.fixtures import u2_host as fixture

_SPEC = importlib.util.spec_from_file_location("u2_qualification_host", Path(__file__).resolve().parents[1] / "docs/development/verification/u2-host/host.py")
host = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(host)


class U2PublicHistoryAllocationTests(unittest.TestCase):
    """Data contracts only; these do not qualify live admission or a new binary."""

    def test_public_history_replacement_mapping(self):
        for version in range(42, 58):
            with self.subTest(version=version):
                expected = ({"home": "synthetic-reference-a-regression",
                             "work": "synthetic-operations-guide-regression"}
                            if version == 57 else
                            {"home": "synthetic-reference-a",
                             "work": "synthetic-operations-guide-check"})
                self.assertEqual(host.u2_allocation(version)["replacement_work"], expected)

    def test_public_history_replacement_versions(self):
        versions = {version for version, allocation in host.codex.U2_ALLOCATIONS.items()
                    if "replacement_work" in allocation}
        self.assertEqual(versions, set(range(41, 58)))

    def test_public_history_v41_preserved(self):
        self.assertEqual(host.u2_allocation(41)["replacement_work"],
                         {"home": "u2-synthetic-h04-20261025",
                          "work": "synthetic-h04-same-thread"})


class U2HostTests(unittest.TestCase):
    def test_h03_permission_routes(self):
        name = "colvia-u2-worker"
        for label, response in (("minimal", fixture.config_response()),
                                ("schema-null-defaults", fixture.with_schema_null_defaults(fixture.config_response()))):
            with self.subTest(case=label):
                before = deepcopy(response)
                observation = host.policy_observation(response, name, fixture.profile())
                self.assertEqual(observation["reasons"], [])
                self.assertEqual(response, before)
                self.assertEqual(observation["normalized_profile_sha256"], host.digest(host.canonical(fixture.profile())))
        changes = [
            ("legacy-effective", lambda x: x["config"].update(sandbox_mode="workspace-write")),
            ("legacy-layer", lambda x: x["layers"][0]["config"].update(sandbox_mode="read-only")),
            ("inheritance", lambda x: x["config"]["permissions"][name].update(extends=":read-only")),
            ("extra-root-read", lambda x: x["config"]["permissions"][name]["filesystem"].update({":root": "read"})),
            ("new-write", lambda x: x["config"]["permissions"][name]["filesystem"].update({"/synthetic/outside": "write"})),
            ("network", lambda x: x["config"]["permissions"][name]["network"].update(enabled=True)),
            ("unix-sockets", lambda x: x["config"]["permissions"][name]["network"].update(dangerously_allow_all_unix_sockets=True)),
            ("unknown-policy-field", lambda x: x["config"]["permissions"][name].update(unknown_policy=None)),
            ("wrong-profile", lambda x: x["config"].update(default_permissions=":workspace")),
            ("active-mcp", lambda x: x["config"]["mcp_servers"]["node_repl"].update(enabled=True)),
            ("unknown-mcp", lambda x: x["config"]["mcp_servers"].update(unknown={"enabled": False})),
            ("feature-reenabled", lambda x: x["config"]["features"].update(apps=True)),
            ("web-reenabled", lambda x: x["config"].update(web_search="live")),
            ("plugin-enabled", lambda x: x["config"]["plugins"]["synthetic-plugin@synthetic-market"].update(enabled=True)),
            ("plugin-not-explicitly-disabled", lambda x: x["config"]["plugins"].update(unknown={})),
        ]
        for label, change in changes:
            with self.subTest(case=label):
                response = fixture.with_schema_null_defaults(fixture.config_response())
                change(response)
                self.assertTrue(host.policy_observation(response, name, fixture.profile())["reasons"])
        with self.subTest(case="missing-layer-observation"):
            response = fixture.config_response()
            del response["layers"]
            with self.assertRaises(host.HostRefusal):
                host.policy_observation(response, name, fixture.profile())
        for label, frame in (("config-fallback", {"method": "configWarning", "params": {}}),
                             ("server-exec", {"id": 9, "method": "item/commandExecution/requestApproval", "params": {}}),
                             ("wrong-response-id", {"id": 8, "result": {}})):
            with self.subTest(case=label):
                client = object.__new__(host.StdioClient)
                client.sequence = 0
                client.events = []
                sent = []
                client.send = sent.append
                client.receive = lambda: frame
                with self.assertRaises(host.HostRefusal):
                    client.request("config/read", {})
                self.assertFalse(any("decision" in message or "permissions" in message for message in sent))
                if label == "server-exec":
                    self.assertIn("error", sent[-1])
        with self.subTest(case="no-model-turn-route"):
            client = object.__new__(host.StdioClient)
            with self.assertRaises(host.HostRefusal):
                client.request("turn/start", {"input": []})

        # Current RPC implementation rejects late warnings, unknown requests,
        # duplicate JSON keys and notification floods without a model provider.
        for frame in ({"method": "configWarning", "params": {}},
                      {"method": "unknown/notification", "params": {}},
                      {"method": "item/commandExecution/requestApproval", "id": 7, "params": {}}):
            client = object.__new__(host.LiveClient)
            client.event_counts, client.events = {}, []
            client.failed, client.callback, client.on_event = False, None, None
            sent = []; client.send = sent.append
            with self.subTest(live_frame=frame["method"]), self.assertRaises(host.HostRefusal):
                client.event(frame)
        client.event_counts = {"turn/completed": 20_000}
        with self.assertRaises(host.HostRefusal):
            client.event({"method": "turn/completed", "params": {}})
        with self.assertRaises(host.HostRefusal):
            host.reject_duplicate_keys([("id", 1), ("id", 2)])
        import os
        import tempfile
        worker = fixture.worker_module()
        for kind in ("symlink", "hardlink", "ancestor-symlink"):
            with self.subTest(alias=kind), tempfile.TemporaryDirectory() as raw:
                root = Path(raw).resolve(); spec = fixture.documents(host, root)
                output = root / "output.md"; prior = output.read_bytes()
                if kind == "hardlink":
                    os.link(output, root / "alias.md")
                elif kind == "symlink":
                    output.unlink(); output.symlink_to(root / "reference.md")
                else:
                    (root / "alias").symlink_to(root, target_is_directory=True)
                    spec["files"]["Output"]["path"] = str(root / "alias/output.md")
                with self.assertRaises((worker.WorkerRefusal, OSError)):
                    worker.execute(spec, {"tool": "u2_write_file", "arguments": {"file_id": "Output", "expected_sha256": spec["files"]["Output"]["sha256"], "content": "forbidden"}})
                self.assertFalse((root / "Output.swap").exists())
                if kind != "symlink":
                    self.assertEqual(output.read_bytes(), prior)
        # Real child cleanup is distinct from actual worker Seatbelt qualification.
        import subprocess
        import sys
        process = subprocess.Popen([sys.executable, "-I", "-S", "-B", "-c", "import time; time.sleep(30)"],
                                   env=host.closed_environment(), start_new_session=True)
        cleanup = host.end_process(process)
        self.assertTrue(cleanup["process_group_absent"])
        self.assertIsNotNone(process.returncode)

    def test_h01_admission_binding(self):
        import tempfile
        for field, value in (("threadId", "foreign"), ("turnId", "foreign"), ("callId", "unknown"),
                             ("namespace", "owner"), ("tool", "u2_shell")):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as raw:
                a, b, prepared, inputs, call = fixture.admitted(host, Path(raw).resolve())
                before = b.path.read_bytes()
                call[field] = value
                with self.assertRaises(host.HostRefusal):
                    a.callback(call)
                self.assertEqual(b.path.read_bytes(), before)
        for field in ("actor", "home", "action", "scope_identity", "work"):
            with self.subTest(identity=field), tempfile.TemporaryDirectory() as raw:
                a, b, _, _, call = fixture.admitted(host, Path(raw).resolve())
                a.identity[field] = "owner-spoof"
                before = b.path.read_bytes()
                with self.assertRaises(host.HostRefusal):
                    a.callback(call)
                self.assertEqual(b.path.read_bytes(), before)
        with tempfile.TemporaryDirectory() as raw:
            a, b, _, _, call = fixture.admitted(host, Path(raw).resolve())
            self.assertEqual(a.callback(call), ("u2_read_file", {"file_ids": ["Output"]}))
            with self.assertRaises(host.HostRefusal):
                a.callback(call)
            self.assertEqual(b.read()["counts"]["host-dispatch"], 1)

    def test_h02_payload_binding(self):
        import json
        import tempfile
        for mutation in ("packet-bytes", "actor", "home", "action", "result", "token"):
            with self.subTest(case=mutation), tempfile.TemporaryDirectory() as raw:
                a, b, _, _, call = fixture.admitted(host, Path(raw).resolve())
                packet = fixture.ticket_packet(host)
                original = host.core_bytes(packet)
                expected = host.digest(original)
                result_id = a.identity["result_identity"]
                if mutation == "packet-bytes":
                    original += b" "
                elif mutation == "result":
                    result_id = "wrong-result"
                elif mutation == "token":
                    packet["confirm_token"] = "0" * 16
                    original = host.core_bytes(packet); expected = host.digest(original)
                else:
                    key = "authority_home_id" if mutation == "home" else mutation
                    packet["ticket"][key] = "foreign"
                    packet["confirm_token"] = host.digest(host.core_bytes(packet["ticket"]))[:16]
                    original = host.core_bytes(packet); expected = host.digest(original)
                core = fixture.FakeCore(packet)
                with self.assertRaises(host.HostRefusal):
                    host.Acceptance(a.identity, original, expected, result_id, "h" * 32, core, b)
                self.assertEqual(core.calls, [])
        with tempfile.TemporaryDirectory() as raw:
            a, b, prepared, inputs, _ = fixture.admitted(host, Path(raw).resolve())
            a.completed = True
            prepared["manifest"]["snapshot"]["initial_input"][0]["text"] = "replaced"
            with self.assertRaises(host.HostRefusal):
                a.bind("thread-1", prepared, [{"type": "text", "text": "original", "text_elements": []}])

    def test_h04_single_use(self):
        import tempfile
        with tempfile.TemporaryDirectory() as raw:
            a, b, _, _, call = fixture.admitted(host, Path(raw).resolve())
            a.sealed = True
            call.update(tool="u2_accept", arguments={"handle": "h" * 32})
            a.callback(call)
            packet = fixture.ticket_packet(host)
            body = host.core_bytes(packet)
            core = fixture.FakeCore(packet)
            gate = host.Acceptance(a.identity, body, host.digest(body), a.identity["result_identity"], "h" * 32, core, b)
            self.assertTrue(gate.apply(call["arguments"], a, a.identity["result_identity"], True)["accepted"])
            self.assertEqual([entry[0] for entry in core.calls], ["prepare", "apply"])
            with self.assertRaises(host.HostRefusal):
                gate.apply(call["arguments"], a, a.identity["result_identity"], True)
            self.assertEqual(sum(item[0] == "apply" for item in core.calls), 1)
        for change in ("revoked", "other-work", "new-ticket", "result-swap", "active-writer"):
            with self.subTest(case=change), tempfile.TemporaryDirectory() as raw:
                a, b, _, _, call = fixture.admitted(host, Path(raw).resolve())
                a.sealed = True
                call.update(tool="u2_accept", arguments={"handle": "h" * 32})
                a.callback(call)
                packet = fixture.ticket_packet(host); body = host.core_bytes(packet); core = fixture.FakeCore(packet)
                gate = host.Acceptance(a.identity, body, host.digest(body), a.identity["result_identity"], "h" * 32, core, b)
                result, no_writers = a.identity["result_identity"], True
                if change == "revoked": core.refuse_prepare = True
                if change == "other-work": a.identity["work"] = "other"
                if change == "new-ticket": core.packet["ticket"]["request_id"] = "other"
                if change == "result-swap": result = "other"
                if change == "active-writer": no_writers = False
                with self.assertRaises((host.HostRefusal, RuntimeError)):
                    gate.apply(call["arguments"], a, result, no_writers)
                self.assertFalse(any(item[0] == "apply" for item in core.calls))

    def test_h05_human_recovery_gate(self):
        import tempfile
        with tempfile.TemporaryDirectory() as raw:
            b = fixture.budget(host, Path(raw).resolve())
            cases = {}
            for index in range(1, 6):
                packet = fixture.ticket_packet(host)
                packet["ticket"]["request_id"] = "recovery-" + str(index)
                packet["confirm_token"] = host.digest(host.core_bytes(packet["ticket"]))[:16]
                cases["S" + str(index)] = {"packet": packet, "ticket_sha256": host.digest(host.core_bytes(packet["ticket"])),
                    "actor": "delegate-synthetic", "process_group_absent": True, "pending_observed": index != 5,
                    "decision_observed": True, "current_published": index == 5,
                    "actual_current": "published" if index == 5 else "previous", "expected_current": "published",
                    "before_replay": {"pending": index != 5, "bytes": "synthetic-state-" + str(index)}}
            packet = {"cases": cases}; digest = host.digest(host.core_bytes(packet))
            decision = {"packet_sha256": digest, "ticket_sha256s": [cases[key]["ticket_sha256"] for key in sorted(cases)],
                        "actor": "delegate-synthetic", "decision": "replay-once", "owner_message_id": "synthetic-human-message"}
            for field in decision:
                changed = deepcopy(decision); changed[field] = None
                with self.subTest(field=field), self.assertRaises(host.HostRefusal):
                    host.RecoveryGate(packet, digest, changed, b)
            for case_id, field, value in [("S1", "pending_observed", False), ("S5", "pending_observed", True),
                                           ("S5", "current_published", False), ("S5", "actual_current", "other"),
                                           ("S3", "decision_observed", False), ("S4", "process_group_absent", False)]:
                bad = deepcopy(packet); bad["cases"][case_id][field] = value
                bad_digest = host.digest(host.core_bytes(bad)); owner = {**decision, "packet_sha256": bad_digest}
                with self.subTest(case=case_id, field=field), self.assertRaises(host.HostRefusal):
                    host.RecoveryGate(bad, bad_digest, owner, b)
            gate = host.RecoveryGate(packet, digest, decision, b)
            core = fixture.FakeCore(cases["S1"]["packet"])
            gate.replay("S1", core, cases["S1"]["before_replay"])
            with self.assertRaises(host.HostRefusal):
                gate.replay("S1", core, cases["S1"]["before_replay"])
            with self.assertRaises(host.HostRefusal):
                gate.replay("S2", core, {"pending": False})
            self.assertEqual(len(core.calls), 1)
            self.assertEqual(core.calls[0][0], "apply")
            self.assertEqual(core.calls[0][1], cases["S1"]["packet"]["ticket"])

    def test_recovery_observation_ignores_atime_and_rejects_mutation(self):
        import os
        import tempfile
        from contextlib import contextmanager
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw).resolve() / "document.md"
            path.write_bytes(b"fixed bytes")
            os.utime(path, ns=(1, path.stat().st_mtime_ns))
            expected = {str(path): {"sha256": host.digest(b"fixed bytes"), "mode": path.stat().st_mode & 0o7777}}
            self.assertEqual(host.fixed_file_observation([str(path)]), expected)
            original = os.fdopen
            @contextmanager
            def changed(fd, mode):
                with original(fd, mode) as stream:
                    class Reader:
                        def fileno(self): return stream.fileno()
                        def read(self):
                            result = stream.read()
                            path.write_bytes(b"changed during read")
                            return result
                    yield Reader()
            with patch.object(host.os, "fdopen", changed), self.assertRaises(host.HostRefusal):
                host.fixed_file_observation([str(path)])
            alias = path.parent / "alias.md"; alias.symlink_to(path)
            with self.assertRaises(host.HostRefusal): host.fixed_file_observation([str(alias)])

    def test_h06_pre_submit_iteration(self):
        import tempfile
        worker = fixture.worker_module()
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve(); spec = fixture.documents(host, root)
            oracle = {"tool": "u2_verify", "arguments": {"verifier_id": "DOC-CLAIMS"}}
            failed = worker.execute(spec, oracle)
            self.assertFalse(failed["pass"])
            before_reference = (root / "reference.md").read_bytes()
            changed = worker.execute(spec, {"tool": "u2_write_file", "arguments": {"file_id": "Output",
                "expected_sha256": spec["files"]["Output"]["sha256"], "content": "# Draft\n\nVerified reference fact.\n"}})
            spec["files"]["Output"].update(sha256=changed["sha256"], identity=changed["identity"])
            passed = worker.execute(spec, oracle)
            self.assertTrue(passed["pass"])
            self.assertEqual(failed["oracle_sha256"], passed["oracle_sha256"])
            self.assertEqual((root / "reference.md").read_bytes(), before_reference)
            self.assertFalse((root / "Output.swap").exists())
            self.assertEqual((root / "output.md").stat().st_mode & 0o777, 0o600)
            # A stale prior digest fails before creating a new swap.
            with self.assertRaises(worker.WorkerRefusal):
                worker.execute(spec, {"tool": "u2_write_file", "arguments": {"file_id": "Output", "expected_sha256": "0" * 64, "content": "bad"}})
            self.assertFalse((root / "Output.swap").exists())
        rendered = worker.DocumentHTML(); rendered.feed('<p>**broken** Korean <code>**code**</code></p>')
        self.assertTrue(rendered.literal_emphasis)
        rendered = worker.DocumentHTML(); rendered.feed('<p><strong>정상 강조</strong> 입니다.</p><pre><code>**code**</code></pre>')
        self.assertFalse(rendered.literal_emphasis)

    def test_h07_resume_budget(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as raw:
            a, b, _, _, _ = fixture.admitted(host, Path(raw).resolve())
            state = b.read()
            cp = {"approval": b.anchor["approval"], "work": b.anchor["work"], "input_identity": b.anchor["input_identity"],
                  "journal_seq": len(state["rows"]) - 1, "journal_sha256": state["prev"], "sealed": False, "pending": False}
            resumed = host.Budget(b.directory, b.anchor_sha256)
            self.assertEqual(resumed.resume_check(cp, b.anchor["input_identity"])["counts"], state["counts"])
            with self.assertRaises(host.HostRefusal):
                resumed.resume_check(cp, "different input")
            for field in ("sealed", "pending"):
                changed = {**cp, field: True}
                with self.subTest(field=field), self.assertRaises(host.HostRefusal):
                    resumed.resume_check(changed, b.anchor["input_identity"])
            original = b.path.read_bytes()
            for kind, subject, start in (
                ("generation", {"thread": "thread-1", "turn": "foreign-turn", "plan": "plan-1", "generation": 2}, "synthetic-01"),
                ("turn", {"thread": "thread-1", "plan": "new-plan"}, "synthetic-02")):
                if start.endswith("02"):
                    b.reserve("start", {"reason": "resume"}, "synthetic", start)
                before_refusal = b.path.read_bytes()
                with self.subTest(journal=kind), self.assertRaises(host.HostRefusal):
                    b.reserve(kind, subject, "synthetic", start)
                self.assertEqual(b.path.read_bytes(), before_refusal)
            b.reserve("control", {"endpoint": "models"}, "synthetic", "synthetic-01")
            before_refusal = b.path.read_bytes()
            with self.assertRaises(host.HostRefusal):
                b.reserve("control", {"endpoint": "models"}, "synthetic", "synthetic-01")
            self.assertEqual(b.path.read_bytes(), before_refusal)
            original = b.path.read_bytes()
            for bad in (b"", original[:-1], original.replace(b'"candidate":"' + b"a" * 64, b'"candidate":"' + b"c" * 64, 1)):
                b.path.write_bytes(bad)
                with self.assertRaises(host.HostRefusal):
                    host.Budget(b.directory, b.anchor_sha256)
            b.path.write_bytes(original)
            lock = host.ControllerLock(b.directory / "controller.lock")
            try:
                with self.assertRaises(host.HostRefusal):
                    host.ControllerLock(b.directory / "controller.lock")
            finally:
                lock.close()
            paused = b.reserve("pause", {"reason": "owner-only"})
            self.assertEqual(b.read()["active_ms"], paused["at_ms"])
            with self.assertRaises(host.HostRefusal):
                b.reserve("generation", {"thread": "thread-1", "turn": "turn-1", "plan": "plan-1", "generation": 2}, "synthetic", "synthetic-01")
            b.reserve("resume", {"pause_seq": paused["seq"]}, allow_closeout=True)
            self.assertEqual(b.read()["counts"]["generation"], 1)

    def test_h08_stop_boundaries(self):
        import tempfile
        for reason in ("owner-stop", "new-scope", "new-ticket", "revoke", "repeat-no-evidence"):
            with self.subTest(reason=reason), tempfile.TemporaryDirectory() as raw:
                a, b, _, _, call = fixture.admitted(host, Path(raw).resolve())
                b.reserve("stop", {"reason": reason}, allow_closeout=True)
                before = b.path.read_bytes()
                with self.assertRaises(host.HostRefusal):
                    a.callback(call)
                self.assertEqual(b.path.read_bytes(), before)
        with tempfile.TemporaryDirectory() as raw:
            a, b, _, _, call = fixture.admitted(host, Path(raw).resolve())
            a.sealed = True
            for tool in ("u2_read_file", "u2_write_file", "u2_verify"):
                with self.subTest(postseal=tool), self.assertRaises(host.HostRefusal):
                    a.callback({**call, "tool": tool})
            for index in range(2):
                b.reserve("correction", {"index": index})
            with self.assertRaises(host.HostRefusal):
                b.reserve("correction", {"index": 2})
            for text in ("Bearer synthetic-token-value-123456", "sk-syntheticsecret1234567890", "/Users/synthetic/private.txt", "person@example.invalid"):
                with self.subTest(exposure=text.split()[0]), self.assertRaises(host.HostRefusal):
                    host.safe_text(text)
            host.safe_text("Approved name person@example.invalid", ["person@example.invalid"])
        self.assertNotIn("OPENAI_API_KEY", host.closed_environment())
        self.assertNotIn("PYTHONPATH", host.closed_environment())
        self.assertNotIn("HTTPS_PROXY", host.closed_environment())


        # A pre-existing run is foreign evidence, including a directory without
        # result.json. Refusal must neither write into it nor retain the lock.
        from unittest.mock import Mock, patch
        import contextlib
        import io
        for command in ("live-smoke", "recover"):
            with self.subTest(existing_run=command), tempfile.TemporaryDirectory() as raw:
                root = Path(raw).resolve(); run = root / "already-owned"; run.mkdir()
                sentinel = run / "evidence"; sentinel.write_bytes(b"preserve")
                packet = host.core_bytes({"cases": {}}); decision = host.core_bytes({})
                spec = {"version": 1, "command": command, "budget_directory": str(root / "budget"),
                        "budget_anchor_sha256": "a" * 64, "run": str(run), "packet": "packet", "owner_decision": "decision",
                        "packet_sha256": host.digest(packet), "owner_decision_sha256": host.digest(decision), "seconds": 60}
                budget = Mock(); budget.directory = root / "budget"; lock = Mock()
                read = lambda path, *args: packet if str(path) == "packet" else decision
                with patch.object(host, "load_host_spec", return_value=spec), patch.object(host, "Budget", return_value=budget), \
                     patch.object(host, "ControllerLock", return_value=lock), patch.object(host, "control_read", side_effect=read), \
                     patch.object(host, "RecoveryGate"), patch.object(host, "LiveSession") as launch, \
                     contextlib.redirect_stdout(io.StringIO()):
                    code = host.recovery_command("spec") if command == "recover" else host.run_live_command(command, "spec")
                self.assertEqual(code, 2); lock.close.assert_called_once(); launch.assert_not_called()
                self.assertEqual(list(run.iterdir()), [sentinel]); self.assertEqual(sentinel.read_bytes(), b"preserve")
        # Timeout and failed process-record persistence still close the exact
        # child and preserve metadata without recording raw stderr.
        import subprocess
        import time
        for mode in ("timeout", "process-record-failure", "success"):
            with self.subTest(core_cleanup=mode), tempfile.TemporaryDirectory() as raw:
                root = Path(raw).resolve(); process = Mock(pid=123456, returncode=0)
                process.stdin, process.stdout, process.stderr = io.BytesIO(), io.BytesIO(), io.BytesIO()
                if mode == "timeout":
                    process.communicate.side_effect = subprocess.TimeoutExpired(["synthetic"], 1, output=b"partial", stderr=b"private error")
                else:
                    process.communicate.return_value = (b'{"ok":true}', b"")
                core = object.__new__(host.InstalledCore)
                core.spec = {"python": "/synthetic/python", "launcher": "/synthetic/colvia", "cwd": str(root), "env": {}}
                core.run, core.deadline, core.invocations, core.validate = root, time.monotonic() + 60, 0, Mock()
                original_save = host.durable_private
                def save(path, value):
                    if mode == "process-record-failure" and path.name.endswith("-process.json"):
                        raise OSError("synthetic persistence failure")
                    original_save(path, value)
                with patch.object(host.subprocess, "Popen", return_value=process), \
                     patch.object(host.contracts, "end_process", return_value={"exit_code": 0, "process_group_absent": True}) as ended, \
                     patch.object(host.contracts, "durable_private", side_effect=save):
                    if mode == "success":
                        self.assertEqual(core.invoke("prepare", {"synthetic": True}), {"ok": True})
                    else:
                        with self.assertRaises(host.HostRefusal if mode == "timeout" else OSError):
                            core.invoke("prepare", {"synthetic": True})
                ended.assert_called_once_with(process)
                self.assertTrue(all(getattr(process, name).closed for name in ("stdin", "stdout", "stderr")))
                import json
                metadata_raw = (root / "core-001-metadata.json").read_bytes(); metadata = json.loads(metadata_raw)
                self.assertTrue(metadata["process_group_absent"])
                self.assertEqual(metadata["interrupted"], mode == "timeout")
                self.assertEqual(metadata["output_complete"], mode == "success")
                self.assertNotIn(b"private error", metadata_raw)
                if mode == "timeout":
                    self.assertEqual(metadata["stderr_sha256"], host.digest(b"private error"))
                if mode == "process-record-failure":
                    process.communicate.assert_not_called()


        for role in ("live", "worker"):
            for mode in ("spawn-failure", "process-record-failure"):
                with self.subTest(startup_cleanup=(role, mode)), tempfile.TemporaryDirectory() as raw:
                    import sys
                    root = Path(raw).resolve(); process = Mock(pid=123456, returncode=0)
                    process.stdin, process.stdout, process.stderr = io.BytesIO(), io.BytesIO(), io.BytesIO()
                    selector = Mock(); opened_stderr = []
                    def spawn(*args, **kwargs):
                        if hasattr(kwargs["stderr"], "close"):
                            opened_stderr.append(kwargs["stderr"])
                        if mode == "spawn-failure":
                            raise OSError("synthetic spawn failure")
                        return process
                    original_save = host.durable_private
                    def save_startup(path, value):
                        if mode == "process-record-failure" and path.name == "process.json":
                            raise OSError("synthetic process record failure")
                        original_save(path, value)
                    if role == "worker":
                        worker_spec = fixture.documents(host, root)
                        for name in ("run", "scratch"):
                            (root / name).mkdir()
                        template = root / "worker.sb.in"
                        template.write_text('; @@ANCESTOR_METADATA_LITERALS@@\n; @@APPROVED_INPUT_READ_LITERALS@@\n; @@EXACT_WRITE_TARGET_AND_SWAP@@ only for write operation, omitted for read and all verifiers.\n')
                        for name in ("worker.py", "parser.js"):
                            (root / name).write_text("synthetic")
                        controller = object.__new__(host.DocumentController)
                        controller.contract_version = 1
                        controller.spec = {**worker_spec, "scratch": str(root / "scratch"), "python": sys.executable,
                            "worker": str(root / "worker.py"), "worker_sha256": "a" * 64,
                            "parser": str(root / "parser.js"), "profile_template": str(template),
                            "profile_template_sha256": host.digest(template.read_bytes())}
                        controller.files, controller.run, controller.budget = worker_spec["files"], root / "run", Mock()
                        controller.sealed, controller.active, controller.sequence = False, None, 0
                        controller.deadline = time.monotonic() + 60
                        controller.oracle_sha256, controller.phase, controller.start = "a" * 64, "synthetic", "synthetic-01"
                        controller.budget.check_worker_result.return_value = 30
                    with patch.object(host.subprocess, "Popen", side_effect=spawn), \
                         patch.object(host.selectors, "DefaultSelector", return_value=selector), \
                         patch.object(host.os, "set_blocking"), patch.object(host.codex if role == "live" else host.contracts, "durable_private", side_effect=save_startup), \
                         patch.object(host.codex if role == "live" else host.contracts, "end_process", return_value={"exit_code": 0, "process_group_absent": True}) as ended:
                        with self.assertRaises(OSError):
                            if role == "live":
                                host.LiveClient(["synthetic"], root, root, time.monotonic() + 60, {})
                            else:
                                controller.dispatch("u2_verify", {"verifier_id": "DOC-CLAIMS"})
                    if mode == "spawn-failure":
                        ended.assert_not_called()
                    else:
                        ended.assert_called_once_with(process)
                        pipe_names = ("stdin", "stdout", "stderr") if role == "live" else ("stdin", "stdout")
                        self.assertTrue(all(getattr(process, name).closed for name in pipe_names))
                    if role == "live":
                        selector.close.assert_called_once()
                        evidence = json.loads((root / "startup-failure-metadata.json").read_bytes())
                        self.assertEqual(evidence["runtime_started"], mode != "spawn-failure")
                    else:
                        self.assertTrue(opened_stderr[0].closed)
                        self.assertIsNone(controller.active)
                        evidence = json.loads((root / "run/worker-001/failure.json").read_bytes())
                        self.assertEqual(evidence["worker_started"], mode != "spawn-failure")
                        self.assertFalse(evidence["effect_unknown"])


class U2ClockEpochTests(unittest.TestCase):
    def setup_epoch(self, root):
        import json
        import time
        wall, monotonic = time.time_ns() // 1_000_000, time.monotonic_ns()
        old = host.Budget.create(root / "old", {"version": 1, "approval": "approved", "work": "work",
            "candidate": "a" * 64, "source_identity": "source-a", "input_identity": "input-a",
            "origin_wall_ms": wall, "origin_monotonic_ns": monotonic, "total_deadline_ms": wall + 50_000_000})
        old.reserve("build", {"input": "one"}); old.reserve("build", {"input": "two"})
        old.reserve("correction", {"input": "one"})
        old.reserve("pause", {"reason": "owner-only"})
        state = old.read()
        accounting = {"version": 1, "approval": "approved", "work": "work", "active_ms": 8_000_000,
                      "total_cap_ms": 57_600_000, "uncertainty_reserve_ms": 858_141, "closeout_reserve_ms": 1_200_000}
        checkpoint = {"version": 1, "approval": "approved", "work": "work", "input_identity": "input-a",
                      "journal_seq": len(state["rows"]) - 1, "journal_sha256": state["prev"],
                      "sealed": False, "pending": False, "process_ids": []}
        host.durable_private(root / "accounting.json", accounting)
        host.durable_private(root / "checkpoint.json", checkpoint)
        recovery = {"owner_message_id": "explicit-owner", "predecessor": {"directory": str(old.directory),
            "anchor_sha256": old.anchor_sha256, "journal_sha256": host.digest(old.path.read_bytes()),
            "last_seq": len(state["rows"]) - 1, "last_sha256": state["prev"]},
            "accounting": {"path": str(root / "accounting.json"), "sha256": host.digest((root / "accounting.json").read_bytes())},
            "checkpoint": {"path": str(root / "checkpoint.json"), "sha256": host.digest((root / "checkpoint.json").read_bytes())},
            "carry_active_ms": 8_000_000, "total_cap_ms": 57_600_000, "uncertainty_reserve_ms": 858_141, "closeout_reserve_ms": 1_200_000,
            "transition": {"old_candidate": "a" * 64, "old_source_identity": "source-a", "old_input_identity": "input-a",
                           "new_candidate": "b" * 64, "new_source_identity": "source-b", "new_input_identity": "input-b"}}
        wall, monotonic = time.time_ns() // 1_000_000, time.monotonic_ns()
        anchor = {"version": 2, "approval": "approved", "work": "work", "candidate": "b" * 64,
                  "source_identity": "source-b", "input_identity": "input-b", "origin_wall_ms": wall,
                  "origin_monotonic_ns": monotonic, "total_deadline_ms": wall + 49_600_000, "recovery": recovery}
        packet = {"version": 1, "destination": str(root / "new"), "anchor": anchor}
        return old, packet

    def test_clock_epoch_preserves_usage_counts_and_old_bytes(self):
        import tempfile
        import time
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve(); old, packet = self.setup_epoch(root)
            original = {name: (old.directory / name).read_bytes() for name in ("anchor.json", "journal.jsonl")}
            origin_mono = time.monotonic_ns
            # A clock discontinuity still refuses v1; only explicit recovery starts a new epoch.
            with patch.object(host.time, "monotonic_ns", side_effect=lambda: origin_mono() + 6_000_000_000):
                with self.assertRaisesRegex(host.HostRefusal, "clock drift"):
                    host.Budget(old.directory, old.anchor_sha256)
                packet["anchor"]["origin_monotonic_ns"] = host.time.monotonic_ns()
                packet["anchor"]["origin_wall_ms"] = host.time.time_ns() // 1_000_000
                packet["anchor"]["total_deadline_ms"] = packet["anchor"]["origin_wall_ms"] + 49_600_000
                host.durable_private(root / "packet.json", packet)
                current = host.Budget.recover_clock(root / "packet.json")
                state = current.read()
                self.assertEqual(state["counts"]["build"], 2)
                self.assertEqual(state["counts"]["correction"], 1)
                self.assertLessEqual(state["remaining_ms"], 49_600_000)
                self.assertIsNone(state["paused_at"])
                current.reserve("build", {"input": "third"})
                current.reserve("correction", {"input": "second"})
                for kind in ("build", "correction"):
                    before = current.path.read_bytes()
                    with self.subTest(cap=kind), self.assertRaises(host.HostRefusal):
                        current.reserve(kind, {"input": "excess"})
                    self.assertEqual(before, current.path.read_bytes())
                with self.assertRaises(host.HostRefusal):
                    host.Budget.recover_clock(root / "packet.json")
                current.reserve("stop", {"reason": "explicit"}, allow_closeout=True)
                with self.assertRaises(host.HostRefusal):
                    current.reserve("start", {}, "clock", "clock-01")
                for name, value in original.items():
                    self.assertEqual((old.directory / name).read_bytes(), value)

    def test_clock_epoch_rejects_bad_inputs_and_writer(self):
        import json
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve(); old, packet = self.setup_epoch(root)
            mutations = [
                ("low-carry", lambda a: a["recovery"].update(carry_active_ms=1)),
                ("cap-increase", lambda a: a["recovery"].update(total_cap_ms=57_600_001)),
                ("reserve-removal", lambda a: a["recovery"].update(uncertainty_reserve_ms=0)),
                ("predecessor-sha", lambda a: a["recovery"]["predecessor"].update(journal_sha256="0" * 64)),
                ("predecessor-seq", lambda a: a["recovery"]["predecessor"].update(last_seq=0)),
                ("input-transition", lambda a: a.update(input_identity="other")),
                ("work", lambda a: a.update(work="other")),
                ("clock", lambda a: a.update(origin_monotonic_ns=a["origin_monotonic_ns"] - 6_000_000_000)),
                ("new-unknown-field", lambda a: a.update(unknown=True)),
            ]
            for index, (name, change) in enumerate(mutations):
                bad = deepcopy(packet); change(bad["anchor"])
                path = root / (str(index) + ".json"); host.durable_private(path, bad)
                with self.subTest(bad=name), self.assertRaises(host.HostRefusal):
                    host.Budget.recover_clock(path)
                self.assertFalse((root / "new").exists())
            for field in ("sealed", "pending", "process_ids"):
                bad = deepcopy(packet); cp = json.loads((root / "checkpoint.json").read_bytes())
                cp[field] = [os.getpid()] if field == "process_ids" else True
                path = root / (field + ".json"); host.durable_private(path, cp)
                bad["anchor"]["recovery"]["checkpoint"] = {"path": str(path), "sha256": host.digest(path.read_bytes())}
                q = root / (field + "-packet.json"); host.durable_private(q, bad)
                with self.subTest(checkpoint=field), self.assertRaises(host.HostRefusal):
                    host.Budget.recover_clock(q)
            host.durable_private(root / "valid.json", packet)
            lock = host.ControllerLock(old.directory / "controller.lock")
            try:
                with self.assertRaises(host.HostRefusal):
                    host.Budget.recover_clock(root / "valid.json")
            finally:
                lock.close()
            original = old.path.read_bytes()
            for bad in (original[:-1], original.replace(b'"kind":"build"', b'"kind":"stage"', 1)):
                old.path.write_bytes(bad)
                with self.assertRaises(host.HostRefusal):
                    host.Budget.recover_clock(root / "valid.json")
            old.path.write_bytes(original)


class U2FdControllerTests(unittest.TestCase):
    def setup_controller(self, root):
        import time
        import os
        from types import SimpleNamespace
        wall = time.time_ns() // 1_000_000
        budget = host.Budget.create(root / "budget", {"version": 1, "approval": "approved", "work": "work",
            "candidate": "a" * 64, "source_identity": "source", "input_identity": "input",
            "origin_wall_ms": wall, "origin_monotonic_ns": time.monotonic_ns(), "total_deadline_ms": wall + 57_600_000})
        budget.reserve("proxy-start", {"slot": "s4"})
        controller = host.PreparedFdController(budget, "s4", root, root / "s", ["1.1.1.1"],
            {"host": "chatgpt.com", "addresses": ["1.1.1.1"], "resolution_count": 1})
        controller.proxy = SimpleNamespace(pid=os.getpid(), poll=lambda: None)
        controller.deadline = time.monotonic() + 10
        spec = {"transport": controller.runtime_transport(), "candidate": budget.anchor["candidate"], "work": "work",
                "journal_anchor_sha256": budget.anchor_sha256, "phase": "clock", "start": "clock-01"}
        host.durable_private(root / "spec.json", spec)
        runtime = {"spec": str(root / "spec.json"), "spec_sha256": host.digest((root / "spec.json").read_bytes())}
        budget.reserve("start", {"runtime_spec_sha256": runtime["spec_sha256"]}, "clock", "clock-01")
        controller.register_runtime(runtime, SimpleNamespace(pid=os.getpid(), poll=lambda: None))
        budget.reserve("runtime-entered", {"start": "clock-01"}, "clock", "clock-01")
        budget.reserve("control", {"endpoint": "policy"}, "clock", "clock-01")
        request = {"version": 1, "request_id": 0, "nonce": controller.nonce, "candidate": budget.anchor["candidate"],
                   "work": "work", "slot": "s4", "anchor_sha256": budget.anchor_sha256,
                   "reservation_sha256": controller.reservation, "proxy_pid": os.getpid(), "runtime_pid": os.getpid(),
                   "start": "clock-01", "spec_sha256": runtime["spec_sha256"], "runtime_sequence": 0, "host": "chatgpt.com", "port": 443}
        return budget, controller, request

    def close_controller(self, controller):
        controller.proxy.poll = lambda: 0
        controller.close()

    def test_fd_controller_rejects_unbound_request_before_tcp(self):
        import tempfile
        import os
        import socket
        from unittest.mock import patch
        with tempfile.TemporaryDirectory(dir=os.environ["PREPARED_SOCKET_ROOT"]) as raw:
            root = Path(raw).resolve(); budget, controller, request = self.setup_controller(root)
            try:
                for field, value in (("nonce", "wrong"), ("candidate", "wrong"), ("work", "other"), ("slot", "s6"),
                    ("anchor_sha256", "wrong"), ("reservation_sha256", "wrong"), ("proxy_pid", 1), ("runtime_pid", 1),
                    ("spec_sha256", "wrong"), ("runtime_sequence", 1), ("host", "elsewhere"), ("port", 80),
                    ("request_id", 1), ("version", True)):
                    bad = dict(request); bad[field] = value
                    with self.subTest(field=field), patch.object(socket, "socket", side_effect=AssertionError("TCP before admission")), self.assertRaises(host.HostRefusal):
                        controller._request(bad)
                budget.reserve("pause", {"reason": "owner-only"})
                with patch.object(socket, "socket", side_effect=AssertionError("TCP after pause")), self.assertRaises(host.HostRefusal):
                    controller._request(request)
                self.assertEqual(controller.next, 0)
            finally:
                self.close_controller(controller)

    def test_fd_controller_reserves_transfers_once_and_revokes_same_lease(self):
        import tempfile
        import os
        import socket
        import array
        import json
        from unittest.mock import patch
        with tempfile.TemporaryDirectory(dir=os.environ["PREPARED_SOCKET_ROOT"]) as raw:
            root = Path(raw).resolve(); budget, controller, request = self.setup_controller(root)
            passed, peer = socket.socketpair(); peer.settimeout(1)
            observed = []
            class SyntheticTcp:
                def settimeout(self, value): pass
                def connect(self, target):
                    rows = [json.loads(line) for line in (root / "fd-events.jsonl").read_bytes().splitlines()]
                    assert rows[-1]["kind"] == "fd-reserved"
                    observed.append(target)
                def getpeername(self): return ("1.1.1.1", 443)
                def dup(self): return passed.dup()
                def fileno(self): return passed.fileno()
                def close(self): passed.close()
            received = None
            try:
                with patch.object(socket, "socket", return_value=SyntheticTcp()):
                    controller._request(request)
                raw, ancillary, flags, _ = controller.proxy_channel.recvmsg(8192, socket.CMSG_SPACE(4))
                self.assertEqual(flags, 0); self.assertEqual(json.loads(raw)["request"], request)
                fds = array.array("i"); fds.frombytes(ancillary[0][2]); self.assertEqual(len(fds), 1)
                received = socket.socket(fileno=fds[0]); received.sendall(b"A"); self.assertEqual(peer.recv(1), b"A")
                self.assertEqual(observed, [("1.1.1.1", 443)])
                with patch.object(socket, "socket", side_effect=AssertionError("replayed TCP")), self.assertRaises(host.HostRefusal):
                    controller._request(request)
                controller.revoke("clock-01")
                self.assertEqual(peer.recv(1), b"")
                with self.assertRaises(OSError): received.sendall(b"B")
                self.assertEqual(controller.leases, {})
                rows = [json.loads(line) for line in (root / "fd-events.jsonl").read_bytes().splitlines()]
                self.assertEqual([row["kind"] for row in rows[-3:]], ["fd-reserved", "fd-issued", "fd-revoked"])
            finally:
                if received: received.close()
                passed.close(); peer.close(); self.close_controller(controller)


if __name__ == "__main__":
    unittest.main()


class U2ContinuousEpochTests(U2ClockEpochTests):
    def setup_continuation(self, root):
        import time
        import json
        old, first_packet = self.setup_epoch(root)
        host.durable_private(root / "first.json", first_packet)
        previous = host.Budget.recover_clock(root / "first.json")
        previous.reserve("proxy-start", {"slot": "s4"})
        previous.reserve("start", {"fixture": True}, "clock", "clock-01")
        previous.reserve("runtime-entered", {"start": "clock-01"}, "clock", "clock-01")
        stop = previous.reserve("stop", {"reason": "runtime stdout closed"}, allow_closeout=True)
        previous.reserve("process-ended", {"process_group_absent": True, "exit_code": 1}, "clock", "clock-01", allow_closeout=True)
        state = previous.read()
        approval = {"version": 1, "owner_message_id": "specific-owner", "failure_class": "pre-auth-config-root-missing",
            "stop_seq": stop["seq"], "stop_sha256": state["rows"][stop["seq"]]["sha256"],
            "failure_evidence": {"path": str(root / "failure.json"), "sha256": ""},
            "effects_zero": True, "processes_and_fds_absent": True, "input_stable": True, "pending": False,
            "allowed_next_start": "clock-02"}
        host.durable_private(root / "failure.json", {"synthetic": "missing config root before auth"})
        approval["failure_evidence"]["sha256"] = host.digest((root / "failure.json").read_bytes())
        host.durable_private(root / "resume.json", approval)
        carry = 9_000_000
        accounting = {"version": 1, "approval": "approved", "work": "work", "active_ms": carry,
            "total_cap_ms": 86_400_000, "uncertainty_reserve_ms": 858_141, "closeout_reserve_ms": 1_200_000}
        cp = {"version": 1, "approval": "approved", "work": "work", "input_identity": "input-b",
            "journal_seq": len(state["rows"])-1, "journal_sha256": state["prev"], "sealed": False, "pending": False, "process_ids": []}
        host.durable_private(root / "accounting3.json", accounting); host.durable_private(root / "checkpoint3.json", cp)
        def ref(name):
            return {"path": str(root/name), "sha256":host.digest((root/name).read_bytes())}
        recovery = {"owner_message_id":"specific-owner", "predecessor": {"directory":str(previous.directory),
            "anchor_sha256":previous.anchor_sha256,"journal_sha256":host.digest(previous.path.read_bytes()),
            "last_seq":len(state["rows"])-1,"last_sha256":state["prev"]},
            "accounting":ref("accounting3.json"),"checkpoint":ref("checkpoint3.json"),"resume_authorization":ref("resume.json"),
            "carry_active_ms":carry,"total_cap_ms":86_400_000,"uncertainty_reserve_ms":858_141,"closeout_reserve_ms":1_200_000,
            "transition":{"old_candidate":"b"*64,"old_source_identity":"source-b","old_input_identity":"input-b",
                "new_candidate":"c"*64,"new_source_identity":"source-c","new_input_identity":"input-c"}}
        wall=time.time_ns()//1_000_000
        anchor={"version":3,"approval":"approved","work":"work","candidate":"c"*64,"source_identity":"source-c","input_identity":"input-c",
            "origin_wall_ms":wall,"origin_monotonic_ns":host.continuous_ns(),"activity_clock":"mach_continuous_time_ns",
            "total_deadline_ms":wall+86_400_000-carry,"recovery":recovery}
        return previous,{"version":1,"destination":str(root/"new3"),"anchor":anchor}

    def test_continuous_exact_resume_keeps_bytes_counts_and_phase_slots(self):
        import tempfile
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw).resolve(); old,packet=self.setup_continuation(root)
            before=old.path.read_bytes();host.durable_private(root/"packet3.json",packet)
            current=host.Budget.recover_clock(root/"packet3.json")
            state=current.read();self.assertFalse(state["stopped"])
            self.assertEqual(state["counts"]["start"],1);self.assertEqual(state["counts"]["build"],2)
            self.assertEqual(old.path.read_bytes(),before)
            current.reserve("proxy-start",{"slot":"s4","start_id":"s4-02"})
            current.reserve("start",{},"clock","clock-02")
            with self.assertRaises(host.HostRefusal):current.reserve("start",{},"clock","clock-01")
            with self.assertRaises(host.HostRefusal):current.reserve("proxy-start",{"slot":"s4","start_id":"s4-02"})
            current.reserve("proxy-start",{"slot":"s6","start_id":"s6-01"})
            with self.assertRaises(host.HostRefusal):current.reserve("proxy-start",{"slot":"s6","start_id":"s6-01"})
            for _ in range(3):current.reserve("build",{})
            with self.assertRaises(host.HostRefusal):current.reserve("build",{})
            current.reserve("stop",{"reason":"later failure"},allow_closeout=True)
            with self.assertRaises(host.HostRefusal):current.reserve("control",{},"clock","clock-02")

    def test_continuous_resume_rejects_changed_decision_and_clock(self):
        import tempfile,json
        from unittest.mock import patch
        mutations=[("effects_zero",False),("pending",True),("processes_and_fds_absent",False),("input_stable",False),
            ("stop_sha256","0"*64),("owner_message_id","foreign"),("allowed_next_start","synthetic-01"),
            ("failure_class","unknown-send")]
        for key,value in mutations:
            with self.subTest(key=key),tempfile.TemporaryDirectory() as raw:
                root=Path(raw).resolve();old,packet=self.setup_continuation(root)
                decision=json.loads((root/"resume.json").read_bytes());decision[key]=value
                host.durable_private(root/"changed.json",decision)
                packet["anchor"]["recovery"]["resume_authorization"]={"path":str(root/"changed.json"),"sha256":host.digest((root/"changed.json").read_bytes())}
                host.durable_private(root/"packet3.json",packet)
                with self.assertRaises(host.HostRefusal):host.Budget.recover_clock(root/"packet3.json")
                self.assertFalse((root/"new3").exists())
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw).resolve();old,packet=self.setup_continuation(root);host.durable_private(root/"packet3.json",packet)
            current=host.Budget.recover_clock(root/"packet3.json")
            now=host.continuous_ns
            with patch.object(host.codex,"continuous_ns",side_effect=lambda:now()+6_000_000_000):
                with self.assertRaisesRegex(host.HostRefusal,"clock drift"):current.read()
            with patch.object(host.codex,"continuous_ns",return_value=0):
                with self.assertRaises(host.HostRefusal):current.read()
            pause=current.reserve("pause",{"reason":"owner-only"})
            with self.assertRaises(host.HostRefusal):current.reserve("start",{},"clock","clock-02")
            current.reserve("resume",{"pause_seq":pause["seq"]},allow_closeout=True)
            self.assertIsNone(current.read()["paused_at"])

    def test_budget_snapshot_waits_for_normal_writer_and_shared_readers(self):
        import tempfile,threading,time,fcntl,os
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw).resolve();old,packet=self.setup_continuation(root);host.durable_private(root/"packet3.json",packet)
            current=host.Budget.recover_clock(root/"packet3.json")
            fd=host.checked_open(current.lock_path,os.O_RDWR);fcntl.flock(fd,fcntl.LOCK_EX)
            results=[]
            thread=threading.Thread(target=lambda:results.append(current.read()))
            thread.start();time.sleep(0.05);self.assertTrue(thread.is_alive())
            os.close(fd);thread.join(timeout=2);self.assertFalse(thread.is_alive());self.assertEqual(len(results),1)
            fd=host.checked_open(current.lock_path,os.O_RDWR);fcntl.flock(fd,fcntl.LOCK_SH)
            try:self.assertFalse(current.read()["stopped"])
            finally:os.close(fd)


class U2NativeTransitionTests(unittest.TestCase):
    def setup_native_epoch(self, root):
        import json
        old,packet=U2ContinuousEpochTests().setup_continuation(root)
        anchor=packet["anchor"]; recovery=anchor["recovery"]
        attempts={"proxy-start":1,"offline-start":10,"offline-thread":10,"offline-turn":10,"build":3,"correction":5,"review":3}
        recovery.update(total_cap_ms=100_800_000,prior_attempts=attempts)
        accounting=json.loads((root/"accounting3.json").read_bytes());accounting.update(total_cap_ms=100_800_000,prior_attempts=attempts)
        host.durable_private(root/"accounting4.json",accounting)
        recovery["accounting"]={"path":str(root/"accounting4.json"),"sha256":host.digest((root/"accounting4.json").read_bytes())}
        decision=json.loads((root/"resume.json").read_bytes());decision.update(failure_class="native-transition-after-correction06",launch_mode="trusted-native-runtime",launch_contract_sha256="d"*64,approval_plan_sha256="e"*64)
        host.durable_private(root/"decision4.json",decision)
        recovery["resume_authorization"]={"path":str(root/"decision4.json"),"sha256":host.digest((root/"decision4.json").read_bytes())}
        anchor.update(version=4,launch_mode="trusted-native-runtime",launch_contract_sha256="d"*64,approval_wall_ms=anchor["origin_wall_ms"],run_deadline_ms=anchor["origin_wall_ms"]+43_200_000,total_deadline_ms=anchor["origin_wall_ms"]+100_800_000-recovery["carry_active_ms"])
        packet["destination"]=str(root/"new4")
        return old,packet

    def test_native_epoch_preserves_attempts_and_content_reserve(self):
        import tempfile
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw).resolve();old,packet=self.setup_native_epoch(root);before=old.path.read_bytes()
            host.durable_private(root/"packet4.json",packet);current=host.Budget.recover_clock(root/"packet4.json")
            state=current.read();self.assertEqual(state["counts"]["correction"],5);self.assertEqual(state["counts"]["review"],3)
            self.assertLessEqual(state["remaining_ms"],43_200_000)
            current.reserve("correction",{"class":"source"})
            with self.assertRaises(host.HostRefusal):current.reserve("correction",{"class":"source"})
            for _ in range(2):current.reserve("correction",{"class":"content"})
            with self.assertRaises(host.HostRefusal):current.reserve("correction",{"class":"content"})
            current.reserve("review",{})
            with self.assertRaises(host.HostRefusal):current.reserve("review",{})
            self.assertEqual(old.path.read_bytes(),before)

    def test_native_epoch_rejects_mode_contract_deadline_and_refund(self):
        import tempfile
        for key,value in (("launch_mode","unknown"),("launch_contract_sha256","f"*64),("run_deadline_ms",1),("approval_wall_ms",True)):
            with self.subTest(key=key),tempfile.TemporaryDirectory() as raw:
                root=Path(raw).resolve();_,packet=self.setup_native_epoch(root);packet["anchor"][key]=value
                host.durable_private(root/"packet4.json",packet)
                with self.assertRaises(host.HostRefusal):host.Budget.recover_clock(root/"packet4.json")
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw).resolve();_,packet=self.setup_native_epoch(root)
            packet["anchor"]["recovery"]["prior_attempts"]["correction"]=3
            host.durable_private(root/"packet4.json",packet)
            with self.assertRaises(host.HostRefusal):host.Budget.recover_clock(root/"packet4.json")

    def test_native_artifact_modes_and_aliases(self):
        import tempfile,os
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw).resolve();p=root/"artifact";p.write_bytes(b"synthetic")
            for mode,executable in [(0o755,True),(0o700,True),(0o644,False),(0o600,False)]:
                p.chmod(mode);self.assertEqual(host.artifact_read(p,executable=executable),b"synthetic")
            for mode in (0o777,0o775,0o664,0o666,0o4755):
                p.chmod(mode)
                actual=p.stat().st_mode & 0o7777
                print("artifact fixture requested="+oct(mode)+" actual="+oct(actual))
                if mode==0o4755 and actual!=mode:
                    self.assertEqual(actual,0o755)  # OS did not materialize the optional setuid fixture.
                    continue
                self.assertEqual(actual,mode)
                for executable in (True,False):
                    with self.assertRaises(host.HostRefusal):host.artifact_read(p,executable=executable)
            p.chmod(0o755)
            with self.assertRaises(host.HostRefusal):host.control_read(p)
            alias=root/"alias";alias.symlink_to(p)
            with self.assertRaises(host.HostRefusal):host.artifact_read(alias,executable=True)
            os.link(p,root/"hard")
            with self.assertRaises(host.HostRefusal):host.artifact_read(p,executable=True)

    def test_native_launch_contract_and_protected_metadata(self):
        import tempfile,os
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw).resolve();runtime={"launch_mode":"trusted-native-runtime"}
            for key in ("binary","spec","launch_contract"):
                runtime[key]=str(root/key)
            host.durable_private(root/"binary",{"synthetic":True});(root/"binary").chmod(0o755);candidate=host.digest((root/"binary").read_bytes())
            host.durable_private(root/"role",{"synthetic":True});(root/"role").chmod(0o644);role={"path":str(root/"role"),"sha256":host.digest((root/"role").read_bytes())}
            env={"HOME":"synthetic","PATH":"/usr/bin:/bin"};identity={"argv":[runtime["binary"],"--role","runtime","--spec",runtime["spec"]],"cwd":str(root/"cwd"),"environment_keys":sorted(env)}
            contract={"version":1,"launch_mode":"trusted-native-runtime","candidate":candidate,"source_identity":"source","launches":{runtime["spec"]:identity},"roles":{k:role for k in ("worker","verifier","proxy")}}
            host.durable_private(root/"launch_contract",contract);sha=host.digest((root/"launch_contract").read_bytes())
            spec={"version":2,"root":str(root),"candidate":candidate,"source_identity":"source","launch_identity":identity,"launch_mode":"trusted-native-runtime","launch_contract":runtime["launch_contract"],"launch_contract_sha256":sha,"journal_anchor_sha256":"epoch"}
            host.durable_private(root/"spec",spec)
            for key in ("binary","spec","launch_contract"):runtime[key+"_sha256"]=host.digest(Path(runtime[key]).read_bytes())
            anchor={"version":4,"launch_mode":"trusted-native-runtime","candidate":candidate,"source_identity":"source","launch_contract_sha256":sha}
            host.validate_native_launch(runtime,spec,anchor,"epoch",env)
            for key,value in (("launch_mode","unknown"),("launch_contract_sha256","0"*64),("version",1)):
                changed=dict(spec);changed[key]=value
                with self.assertRaises(host.HostRefusal):host.validate_native_launch(runtime,changed,anchor,"epoch",env)
            with self.assertRaises(host.HostRefusal):host.validate_native_launch(runtime,spec,anchor,"epoch",{**env,"CODEX_API_KEY":"synthetic"})
            before=host.protected_auth_metadata(root)
            host.durable_private(root/"auth.json",{"synthetic":True})
            self.assertNotEqual(before,host.protected_auth_metadata(root))


class U2NetworkRecoveryTests(unittest.TestCase):
    def test_frozen_peer_selection_and_legacy_order(self):
        addresses=["172.64.155.209","104.18.32.47"]
        legacy={"host":"chatgpt.com","addresses":addresses,"resolution_count":1}
        self.assertEqual(host.frozen_network_peer(5,addresses,legacy),addresses[0])
        evidence={**legacy,"selected_peer":"104.18.32.47"}
        self.assertEqual(host.frozen_network_peer(6,addresses,evidence),addresses[1])
        self.assertEqual(evidence["addresses"],addresses)

    def test_frozen_peer_rejects_drift_and_absent_approval(self):
        addresses=["172.64.155.209","104.18.32.47"]
        valid={"host":"chatgpt.com","addresses":addresses,"resolution_count":1,"selected_peer":"104.18.32.47"}
        for key,bad in [("host","other.invalid"),("selected_peer",addresses[0]),("resolution_count",2),("addresses",list(reversed(addresses)))]:
            with self.assertRaises(host.HostRefusal):host.frozen_network_peer(6,addresses,{**valid,key:bad})
        with self.assertRaises(host.HostRefusal):host.frozen_network_peer(6,[addresses[0]],{**valid,"addresses":[addresses[0]]})
        with self.assertRaises(host.HostRefusal):host.frozen_network_peer(6,["127.0.0.1",addresses[1]],{**valid,"addresses":["127.0.0.1",addresses[1]]})
        with self.assertRaises(host.HostRefusal):host.frozen_network_peer(5,addresses,valid)

    def test_network_launch_contract_and_protected_metadata(self):
        import tempfile,os
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw).resolve();runtime={"launch_mode":"trusted-native-runtime"}
            for key in ("binary","spec","launch_contract"):
                runtime[key]=str(root/key)
            host.durable_private(root/"binary",{"synthetic":True});(root/"binary").chmod(0o755);candidate=host.digest((root/"binary").read_bytes())
            host.durable_private(root/"role",{"synthetic":True});(root/"role").chmod(0o644);role={"path":str(root/"role"),"sha256":host.digest((root/"role").read_bytes())}
            env={"HOME":"synthetic","PATH":"/usr/bin:/bin"};identity={"argv":[runtime["binary"],"--role","runtime","--spec",runtime["spec"]],"cwd":str(root/"cwd"),"environment_keys":sorted(env)}
            contract={"version":2,"network":{"host":"chatgpt.com","port":443,"peer":"104.18.32.47"},"launch_mode":"trusted-native-runtime","candidate":candidate,"source_identity":"source","launches":{runtime["spec"]:identity},"roles":{k:role for k in ("worker","verifier","proxy")}}
            host.durable_private(root/"launch_contract",contract);sha=host.digest((root/"launch_contract").read_bytes())
            spec={"version":2,"root":str(root),"candidate":candidate,"source_identity":"source","launch_identity":identity,"launch_mode":"trusted-native-runtime","launch_contract":runtime["launch_contract"],"launch_contract_sha256":sha,"journal_anchor_sha256":"epoch"}
            host.durable_private(root/"spec",spec)
            for key in ("binary","spec","launch_contract"):runtime[key+"_sha256"]=host.digest(Path(runtime[key]).read_bytes())
            anchor={"version":6,"launch_mode":"trusted-native-runtime","candidate":candidate,"source_identity":"source","launch_contract_sha256":sha}
            host.validate_native_launch(runtime,spec,anchor,"epoch",env)
            for key,value in (("launch_mode","unknown"),("launch_contract_sha256","0"*64),("version",1)):
                changed=dict(spec);changed[key]=value
                with self.assertRaises(host.HostRefusal):host.validate_native_launch(runtime,changed,anchor,"epoch",env)
            with self.assertRaises(host.HostRefusal):host.validate_native_launch(runtime,spec,anchor,"epoch",{**env,"CODEX_API_KEY":"synthetic"})
            before=host.protected_auth_metadata(root)
            host.durable_private(root/"auth.json",{"synthetic":True})
            self.assertNotEqual(before,host.protected_auth_metadata(root))



class U2PrefaceRecoveryTests(unittest.TestCase):
    def test_remaining_transport_capacity_preserves_consumed_starts(self):
        events=[{"kind":"start","phase":"clock"} for _ in range(3)]
        state={"events":events,"counts":{"control":2}}
        self.assertEqual(host.phase_transport_limit(state,"s4",7),40)
        self.assertEqual(host.phase_transport_limit(state,"s4",6),32)
        self.assertEqual(host.phase_transport_limit(state,"s6",7),88)

    def test_preface_recovery_keeps_exact_dns_peer(self):
        addresses=["172.64.155.209","104.18.32.47"]
        evidence={"host":"chatgpt.com","addresses":addresses,"selected_peer":addresses[1],"resolution_count":1}
        self.assertEqual(host.frozen_network_peer(7,addresses,evidence),addresses[1])
        with self.assertRaises(host.HostRefusal):host.frozen_network_peer(7,[addresses[0]],{**evidence,"addresses":[addresses[0]]})

    def test_preface_launch_contract_and_protected_metadata(self):
        import tempfile,os
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw).resolve();runtime={"launch_mode":"trusted-native-runtime"}
            for key in ("binary","spec","launch_contract"):
                runtime[key]=str(root/key)
            host.durable_private(root/"binary",{"synthetic":True});(root/"binary").chmod(0o755);candidate=host.digest((root/"binary").read_bytes())
            host.durable_private(root/"role",{"synthetic":True});(root/"role").chmod(0o644);role={"path":str(root/"role"),"sha256":host.digest((root/"role").read_bytes())}
            env={"HOME":"synthetic","PATH":"/usr/bin:/bin"};identity={"argv":[runtime["binary"],"--role","runtime","--spec",runtime["spec"]],"cwd":str(root/"cwd"),"environment_keys":sorted(env)}
            contract={"version":2,"network":{"host":"chatgpt.com","port":443,"peer":"104.18.32.47"},"launch_mode":"trusted-native-runtime","candidate":candidate,"source_identity":"source","launches":{runtime["spec"]:identity},"roles":{k:role for k in ("worker","verifier","proxy")}}
            host.durable_private(root/"launch_contract",contract);sha=host.digest((root/"launch_contract").read_bytes())
            spec={"version":2,"root":str(root),"candidate":candidate,"source_identity":"source","launch_identity":identity,"launch_mode":"trusted-native-runtime","launch_contract":runtime["launch_contract"],"launch_contract_sha256":sha,"journal_anchor_sha256":"epoch"}
            host.durable_private(root/"spec",spec)
            for key in ("binary","spec","launch_contract"):runtime[key+"_sha256"]=host.digest(Path(runtime[key]).read_bytes())
            anchor={"version":7,"launch_mode":"trusted-native-runtime","candidate":candidate,"source_identity":"source","launch_contract_sha256":sha}
            host.validate_native_launch(runtime,spec,anchor,"epoch",env)
            for key,value in (("launch_mode","unknown"),("launch_contract_sha256","0"*64),("version",1)):
                changed=dict(spec);changed[key]=value
                with self.assertRaises(host.HostRefusal):host.validate_native_launch(runtime,changed,anchor,"epoch",env)
            with self.assertRaises(host.HostRefusal):host.validate_native_launch(runtime,spec,anchor,"epoch",{**env,"CODEX_API_KEY":"synthetic"})
            before=host.protected_auth_metadata(root)
            host.durable_private(root/"auth.json",{"synthetic":True})
            self.assertNotEqual(before,host.protected_auth_metadata(root))




class U2LiteRecoveryTests(unittest.TestCase):
    def test_remaining_transport_capacity_and_peer(self):
        events=[{"kind":"start","phase":"clock"} for _ in range(4)]
        state={"events":events,"counts":{"control":3}}
        self.assertEqual(host.phase_transport_limit(state,"s4",8),40)
        self.assertEqual(host.phase_transport_limit(state,"s6",8),88)
        addresses=["172.64.155.209","104.18.32.47"]
        evidence={"host":"chatgpt.com","addresses":addresses,"selected_peer":addresses[1],"resolution_count":1}
        self.assertEqual(host.frozen_network_peer(8,addresses,evidence),addresses[1])
        with self.assertRaises(host.HostRefusal):host.frozen_network_peer(8,[addresses[0]],{**evidence,"addresses":[addresses[0]]})

    def test_both_encodings_keep_all_four_callback_admissions(self):
        import tempfile
        from copy import deepcopy
        for lite in (False,True):
            for name,args in [("u2_read_file",{"file_ids":["Output"]}),("u2_write_file",{"file_id":"Output","content":"Synthetic."}),("u2_verify",{}),("u2_accept",{})]:
                with tempfile.TemporaryDirectory() as d:
                    a,b,prepared,inputs,call=fixture.admitted(host,Path(d))
                    changed=deepcopy(prepared)
                    changed["manifest"]["snapshot"]["context"]["model"].update(use_responses_lite=lite,used_fallback_model_metadata=False)
                    # Core maps the native functions namespace to the registered dynamic handler;
                    # the app callback keeps that handler's original None namespace.
                    fresh=host.Admission(a.identity,a.source,a.candidate,a.template,a.tools,b,a.phase,a.start)
                    fresh.bind("thread-1",changed,inputs);fresh.bind_turn("turn-1")
                    call.update(tool=name,arguments=args)
                    fresh.sealed=(name=="u2_accept")
                    fresh.callback(call)


class U2NotificationRecoveryTests(unittest.TestCase):
    def client(self):
        c=object.__new__(host.LiveClient);c.event_counts,c.events={},[];c.failed=False;c.callback=None;c.on_event=None;c.initialized=True;c.rpc_stage="thread/start";c.send=lambda value:None
        return c
    def frame(self):
        return {"method":"remoteControl/status/changed","emittedAtMs":1234,"params":{"status":"disabled","serverName":"synthetic-name","installationId":"synthetic-id","environmentId":None}}
    def test_initial_disabled_once_without_identity_forwarding(self):
        import json
        c=self.client();seen=[];c.on_event=lambda *args:seen.append(args);c.event(self.frame());self.assertFalse(seen);self.assertNotIn("synthetic",json.dumps(c.events));self.assertEqual(c.event_counts,{"remoteControl/status/changed":1})
        with self.assertRaises(host.HostRefusal):c.event(self.frame())
    def test_active_unknown_schema_phase_and_requests_fail(self):
        import copy
        for case in ("enabled","connecting","error","extra","missing","environment","identity","late","early","request","unknown","warning","timestamp-bool","timestamp-negative","timestamp-null"):
            c=self.client();v=copy.deepcopy(self.frame())
            if case in ("enabled","connecting","error"):v["params"]["status"]=case
            elif case=="extra":v["params"]["extra"]=True
            elif case=="missing":del v["params"]["serverName"]
            elif case=="environment":v["params"]["environmentId"]="synthetic"
            elif case=="identity":v["params"]["installationId"]=123
            elif case=="late":c.rpc_stage="turn/prepare"
            elif case=="early":c.initialized=False
            elif case=="request":v["id"]=1
            elif case=="unknown":v["method"]="unknown/notification"
            elif case=="warning":v["method"]="configWarning"
            elif case=="timestamp-bool":v["emittedAtMs"]=True
            elif case=="timestamp-negative":v["emittedAtMs"]=-1
            elif case=="timestamp-null":v["emittedAtMs"]=None
            with self.subTest(case=case),self.assertRaises(host.HostRefusal):c.event(v)
    def test_metadata_bounds_and_no_params(self):
        c=self.client();v=self.frame();c.event(v);self.assertEqual(set(c.events[0]),{"method","request","stage"})
        for method in ("x"*129,"bad\nmethod"):
            with self.assertRaises(host.HostRefusal):c.event({"method":method})


class U2BootstrapRecoveryTests(U2NotificationRecoveryTests):
    def account(self):
        return {"method":"account/updated","params":{"authMode":"chatgpt","planType":"pro"},"emittedAtMs":1234}
    def test_account_once_without_forwarding(self):
        import json
        c=self.client();seen=[];c.on_event=lambda *args:seen.append(args);c.event(self.account());self.assertFalse(seen);self.assertNotIn("planType",json.dumps(c.events))
        with self.assertRaises(host.HostRefusal):c.event(self.account())
    def test_account_rejects_changed_unknown_extra_and_late(self):
        import copy
        for case in ("api","unknown","null","extra","missing","early","late","request","timestamp-bool","timestamp-negative","timestamp-overflow","params-list"):
            c=self.client();v=copy.deepcopy(self.account())
            if case=="api":v["params"]["authMode"]="apikey"
            elif case=="unknown":v["params"]["planType"]="unknown"
            elif case=="null":v["params"]["planType"]=None
            elif case=="extra":v["params"]["accountId"]="synthetic"
            elif case=="missing":del v["params"]["planType"]
            elif case=="early":c.initialized=False
            elif case=="late":c.rpc_stage="turn/start"
            elif case=="request":v["id"]=1
            elif case=="timestamp-bool":v["emittedAtMs"]=True
            elif case=="timestamp-negative":v["emittedAtMs"]=-1
            elif case=="timestamp-overflow":v["emittedAtMs"]=2**63
            elif case=="params-list":v["params"]=[]
            with self.subTest(case=case),self.assertRaises(host.HostRefusal):c.event(v)

    def test_account_route_rejects_other_origin_and_changes(self):
        import copy
        value={"account":{"type":"chatgpt","email":None,"planType":"pro"},"requiresOpenaiAuth":True,"workspaceRouting":{"chatgptAccountId":"synthetic","backendOrigin":"https://chatgpt.com","accountRoutingOverride":"NO_CONSTRAINT"}}
        self.assertIsNone(host.LiveClient.validate_account_result(value))
        for case in ("origin","missing","duplicate-shape","plan","api","requires"):
            v=copy.deepcopy(value)
            if case=="origin":v["workspaceRouting"]["backendOrigin"]="https://other.example"
            elif case=="missing":v["workspaceRouting"]=None
            elif case=="duplicate-shape":v["workspaceRouting"]["extra"]=True
            elif case=="plan":v["account"]["planType"]="unknown"
            elif case=="api":v["account"]["type"]="apiKey"
            elif case=="requires":v["requiresOpenaiAuth"]=False
            with self.subTest(case=case),self.assertRaises(host.HostRefusal):host.LiveClient.validate_account_result(v)


class U2RpcFailureMetadataTests(unittest.TestCase):
    def test_rpc_refusal_keeps_only_bounded_metadata(self):
        import json
        c=object.__new__(host.LiveClient);c.failed=False;c.sequence=0;c.send=lambda value:None
        c.receive=lambda:{"id":1,"error":{"code":-32600,"message":"synthetic-private-account-detail"}}
        with self.assertRaises(host.HostRefusal):c.request("initialize",{})
        self.assertEqual(c.rpc_failure["error_code"],-32600);self.assertTrue(c.rpc_failure["id_matches"])
        self.assertEqual(c.rpc_failure["error_message_sha256"],host.digest(b"synthetic-private-account-detail"))
        self.assertNotIn("synthetic-private-account-detail",json.dumps(c.rpc_failure))


class U2FixtureNoticeTests(unittest.TestCase):
    MESSAGE = ("Under-development features enabled: skip_host_skill_discovery. "
               "Under-development features are incomplete and may behave unpredictably. "
               "To suppress this warning, set `suppress_unstable_features_warning = true` in "
               "/synthetic/fixture/home/config.toml.")

    def client(self, bound=True):
        c = object.__new__(host.LiveClient)
        c.failed, c.initialized, c.account_bootstrap_validated = False, True, True
        c.sequence, c.event_counts, c.events = 0, {}, []
        c.callback, c.on_event, c.send = None, None, lambda value: None
        c.fixture_notice_message = self.MESSAGE
        c.fixture_notice_thread = "thread-1" if bound else None
        c.fixture_notice_pending_thread = None
        c.fixture_notice_started, c.fixture_notice_prepared = bound, False
        c.fixture_notice_pending, c.fixture_notices = True, []
        c.rpc_stage = "turn/prepare" if bound else "initialized"
        return c

    def frame(self):
        return {"method": "warning", "params": {"message": self.MESSAGE, "threadId": "thread-1"}}

    def test_exact_notice_records_hash_without_forwarding(self):
        c = self.client()
        c.on_event = lambda *args: self.fail("notice forwarded")
        c.event(self.frame())
        self.assertEqual(len(c.fixture_notices), 1)
        self.assertTrue(c.fixture_notices[0]["thread_bound"])
        self.assertEqual(c.fixture_notices[0]["message_sha256"], host.digest(self.MESSAGE.encode()))
        self.assertNotIn("message", c.fixture_notices[0])
        with self.assertRaises(host.HostRefusal): c.event(self.frame())
        self.assertTrue(c.failed)

    def test_default_and_nonmatching_notices_fail_closed(self):
        cases = ["default", "other-feature", "extra-feature", "other-path", "suffix", "thread", "early",
                 "late", "idle", "uninitialized", "account", "request", "extra-envelope", "extra-param",
                 "missing", "null", "long", "timestamp-bool", "timestamp-negative", "jsonrpc"]
        for case in cases:
            with self.subTest(case=case):
                c, v = self.client(), self.frame()
                if case == "default": c.fixture_notice_message = None
                elif case == "other-feature": v["params"]["message"] = self.MESSAGE.replace("skip_host_skill_discovery", "code_mode")
                elif case == "extra-feature": v["params"]["message"] = self.MESSAGE.replace("skip_host_skill_discovery", "code_mode, skip_host_skill_discovery")
                elif case == "other-path": v["params"]["message"] = self.MESSAGE.replace("/synthetic/fixture", "/synthetic/other")
                elif case == "suffix": v["params"]["message"] += "extra"
                elif case == "thread": v["params"]["threadId"] = "wrong"
                elif case == "early": c.rpc_stage = "account/read"
                elif case == "late": c.rpc_stage = "turn/startPrepared"
                elif case == "idle": c.fixture_notice_pending = False
                elif case == "uninitialized": c.initialized = False
                elif case == "account": c.account_bootstrap_validated = False
                elif case == "request": v["id"] = 1
                elif case == "extra-envelope": v["extra"] = 1
                elif case == "extra-param": v["params"]["extra"] = 1
                elif case == "missing": del v["params"]["threadId"]
                elif case == "null": v["params"] = None
                elif case == "long": v["params"]["message"] = "x" * 4097
                elif case == "timestamp-bool": v["emittedAtMs"] = True
                elif case == "timestamp-negative": v["emittedAtMs"] = -1
                elif case == "jsonrpc": v["jsonrpc"] = "1.0"
                with self.assertRaises(host.HostRefusal): c.event(v)
                self.assertTrue(c.failed)

    def test_other_warning_categories_remain_rejected(self):
        for method in ("configWarning", "error", "unknown/notification"):
            with self.subTest(method=method):
                with self.assertRaises(host.HostRefusal): self.client().event({"method": method, "params": {}})

    def test_notice_before_and_after_thread_response(self):
        for early in (True, False):
            with self.subTest(early=early):
                c = self.client(False)
                frames = ([self.frame()] if early else []) + [{"id": 1, "result": {"thread": {"id": "thread-1"}}}]
                it = iter(frames); c.receive = lambda: next(it)
                c.request("thread/start", {"ephemeral": True})
                frames = ([] if early else [self.frame()]) + [{"id": 2, "result": {"handle": "synthetic"}}]
                it = iter(frames); c.receive = lambda: next(it)
                c.request("turn/prepare", {"threadId": "thread-1"})
                self.assertTrue(c.fixture_notices[0]["thread_bound"])
                self.assertFalse(c.fixture_notice_pending)
                with self.assertRaises(host.HostRefusal): c.event(self.frame())

    def test_native_first_notice_at_each_start_boundary(self):
        for order in ("before-response", "after-response-drain", "during-prepare"):
            with self.subTest(order=order):
                c = self.client(False)
                c.native_notifications = True
                frames = ([self.frame()] if order == "before-response" else []) + [
                    {"id": 1, "result": {"thread": {"id": "thread-1"}}}]
                it = iter(frames); c.receive = lambda: next(it)
                c.request("thread/start", {"ephemeral": True})
                if order == "after-response-drain":
                    self.assertFalse(c.fixture_notice_pending)
                    import time
                    c.buffer = b"\n"; c.deadline = time.monotonic() + 1
                    c._poll = lambda seconds: None
                    def late_notice():
                        c.buffer = b""
                        return self.frame()
                    c.receive = late_notice
                    c.drain(seconds=0)
                frames = ([self.frame()] if order == "during-prepare" else []) + [
                    {"id": 2, "result": {"handle": "synthetic"}}]
                it = iter(frames); c.receive = lambda: next(it)
                c.request("turn/prepare", {"threadId": "thread-1"})
                self.assertEqual(len(c.fixture_notices), 1)
                self.assertTrue(c.fixture_notices[0]["thread_bound"])
                self.assertFalse(c.fixture_notice_pending)
                with self.assertRaises(host.HostRefusal): c.event(self.frame())

    def test_native_post_response_notice_rejects_drift_and_late_phase(self):
        for case in ("foreign-thread", "content", "unbound", "not-started", "prepared",
                     "later-phase", "duplicate", "no-account", "fixture-only"):
            with self.subTest(case=case):
                c = self.client(False); c.native_notifications = True
                c.receive = lambda: {"id": 1, "result": {"thread": {"id": "thread-1"}}}
                c.request("thread/start", {"ephemeral": True})
                value = self.frame()
                if case == "foreign-thread": value["params"]["threadId"] = "other"
                elif case == "content": value["params"]["message"] += "extra"
                elif case == "unbound": c.fixture_notice_thread = None
                elif case == "not-started": c.fixture_notice_started = False
                elif case == "prepared": c.fixture_notice_prepared = True
                elif case == "later-phase": c.rpc_stage = "turn/startPrepared"
                elif case == "duplicate": c.event(self.frame())
                elif case == "no-account": c.account_bootstrap_validated = False
                elif case == "fixture-only": c.native_notifications = False
                with self.assertRaises(host.HostRefusal): c.event(value)
                self.assertTrue(c.failed)

    def test_unbound_mismatch_and_missing_notice_stop_before_consume(self):
        c = self.client(False)
        frames = iter([self.frame(), {"id": 1, "result": {"thread": {"id": "wrong"}}}])
        c.receive = lambda: next(frames)
        with self.assertRaises(host.HostRefusal): c.request("thread/start", {"ephemeral": True})
        self.assertTrue(c.failed)
        with self.assertRaises(host.HostRefusal): c.request("turn/prepare", {"threadId": "wrong"})
        c = self.client(); c.receive = lambda: {"id": 1, "result": {"handle": "synthetic"}}
        with self.assertRaises(host.HostRefusal): c.request("turn/prepare", {"threadId": "thread-1"})
        self.assertTrue(c.failed)

    def test_policy_binds_exact_fixture_binary_and_root(self):
        import tempfile
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve(); (root / "cwd").mkdir()
            binary = root / "codex-prepared-tool-plan-fixture"; binary.write_bytes(b"synthetic executable")
            argv = [str(binary), str(root)]
            self.assertIsNone(host.prepared_fixture_notice_message([], None, None, None))
            with self.assertRaises(host.HostRefusal): host.prepared_fixture_notice_message(argv, root / "cwd", root, host.FIXTURE_NOTICE_POLICY)
            with patch.object(host.codex, "FIXTURE_NOTICE_BUILD_SHA256", host.digest(binary.read_bytes())):
                self.assertTrue(host.prepared_fixture_notice_message(argv, root / "cwd", root, host.FIXTURE_NOTICE_POLICY).endswith(str(root / "home/config.toml") + "."))
                with self.assertRaises(host.HostRefusal): host.prepared_fixture_notice_message(argv, root, root, host.FIXTURE_NOTICE_POLICY)
                with self.assertRaises(host.HostRefusal): host.prepared_fixture_notice_message(argv, root / "cwd", root, "allow-all")
                live = root / "codex-prepared-tool-plan-live"; live.write_bytes(binary.read_bytes())
                with self.assertRaises(host.HostRefusal): host.prepared_fixture_notice_message([str(live), str(root)], root / "cwd", root, host.FIXTURE_NOTICE_POLICY)
                alias = root / "alias"; alias.symlink_to(binary)
                with self.assertRaises(host.HostRefusal): host.prepared_fixture_notice_message([str(alias), str(root)], root / "cwd", root, host.FIXTURE_NOTICE_POLICY)
                binary.write_bytes(b"changed")
                with self.assertRaises(host.HostRefusal): host.prepared_fixture_notice_message(argv, root / "cwd", root, host.FIXTURE_NOTICE_POLICY)


class U2FixtureNotificationFlowTests(unittest.TestCase):
    def rate(self):
        fields = ("limitName", "normalModelSlug", "primary", "secondary", "credits",
                  "individualLimit", "spendControlReached", "planType", "rateLimitReachedType")
        return {"method": "account/rateLimits/updated",
                "params": {"rateLimits": {"limitId": "codex", **dict.fromkeys(fields)}}}

    def active_client(self):
        c = U2FixtureNoticeTests().client()
        c.fixture_flow = host.FixtureNotificationFlow()
        f = c.fixture_flow
        f.response("thread/start", {"thread": {"id": "thread-1"}})
        f.response("turn/prepare", {})
        f.before_request("turn/startPrepared", {"threadId": "thread-1"})
        c.rpc_stage = "turn/startPrepared"
        c.event({"method": "turn/started", "params": {"threadId": "thread-1", "turn": {"id": "turn-1"}}})
        return c

    def test_repeated_sparse_rates_do_not_forward_account_data(self):
        c = self.active_client(); c.on_event = lambda *args: self.fail("account metadata forwarded")
        before = deepcopy(c.fixture_flow.__dict__)
        for _ in range(3): c.event(self.rate())
        self.assertEqual(c.fixture_flow.rate_updates, 3)
        self.assertEqual(c.fixture_flow.thread, before["thread"])
        self.assertEqual(c.fixture_flow.turn, before["turn"])
        self.assertFalse(c.fixture_flow.completed)
        for event in c.events:
            self.assertEqual(set(event), {"method", "request", "stage"})

    def test_rate_schema_phase_and_default_rejections_record_failure(self):
        cases = ("default", "early", "uninitialized", "account", "id", "extra", "jsonrpc", "timestamp",
                 "missing", "null", "extra-param", "extra-snapshot", "limit", "nonnull")
        for case in cases:
            with self.subTest(case=case):
                c, v = self.active_client(), self.rate()
                if case == "default": c.fixture_flow = None
                elif case == "early": c.fixture_flow.consuming = False
                elif case == "uninitialized": c.initialized = False
                elif case == "account": c.account_bootstrap_validated = False
                elif case == "id": v["id"] = 1
                elif case == "extra": v["extra"] = True
                elif case == "jsonrpc": v["jsonrpc"] = "1.0"
                elif case == "timestamp": v["emittedAtMs"] = True
                elif case == "missing": del v["params"]["rateLimits"]["credits"]
                elif case == "null": v["params"] = None
                elif case == "extra-param": v["params"]["threadId"] = "thread-1"
                elif case == "extra-snapshot": v["params"]["rateLimits"]["unknown"] = None
                elif case == "limit": v["params"]["rateLimits"]["limitId"] = "other"
                elif case == "nonnull": v["params"]["rateLimits"]["primary"] = {"usedPercent": 0}
                with self.assertRaises(host.HostRefusal): c.event(v)
                self.assertTrue(c.failed)
                self.assertEqual(c.notification_failure["params_sha256"], host.digest(host.wire_bytes(v.get("params"))))
                self.assertNotIn("params", c.notification_failure)
                with self.assertRaises(host.HostRefusal): c.event(self.rate())

    def test_foreign_identity_duplicates_and_incomplete_flow_rejected(self):
        frames = [
            {"method": "thread/status/changed", "params": {"threadId": "foreign"}},
            {"method": "thread/tokenUsage/updated", "params": {"threadId": "thread-1", "turnId": "foreign"}},
            {"method": "turn/started", "params": {"threadId": "thread-1", "turn": {"id": "turn-1"}}},
            {"method": "turn/completed", "params": {"threadId": "thread-1", "turn": {"id": "turn-1", "status": "failed"}}},
            {"method": "unknown/notification", "params": {"private": "not retained"}},
            {"method": "item/completed", "params": {"threadId": "thread-1", "turnId": "turn-1", "item": {"type": "agentMessage", "text": "wrong"}}},
        ]
        for frame in frames:
            with self.subTest(method=frame["method"]):
                c = self.active_client()
                with self.assertRaises(host.HostRefusal): c.event(frame)
                self.assertTrue(c.failed)
                self.assertNotIn("not retained", str(c.notification_failure))
        c = self.active_client()
        with self.assertRaises(host.HostRefusal): c.fixture_flow.verify_complete()
        with self.assertRaises(host.HostRefusal): c.fixture_flow.response("turn/startPrepared", {"turn": {"id": "foreign"}})
        c.event({"method": "turn/completed", "params": {"threadId": "thread-1", "turn": {"id": "turn-1", "status": "completed"}}})
        with self.assertRaises(host.HostRefusal): c.event({"method": "turn/completed", "params": {"threadId": "thread-1", "turn": {"id": "turn-1", "status": "completed"}}})

    def test_complete_rpc_trace_with_response_before_or_after_events(self):
        for response_first in (True, False):
            with self.subTest(response_first=response_first):
                c = U2FixtureNoticeTests().client(False); c.fixture_flow = host.FixtureNotificationFlow()
                frames = iter([
                    {"method": "thread/started", "params": {"thread": {"id": "thread-1", "ephemeral": True}}},
                    U2FixtureNoticeTests().frame(),
                    {"id": 1, "result": {"thread": {"id": "thread-1"}}},
                    {"id": 2, "result": {"handle": "synthetic"}},
                ])
                c.receive = lambda: next(frames)
                c.request("thread/start", {"ephemeral": True})
                c.request("turn/prepare", {"threadId": "thread-1"})
                start = {"method": "turn/started", "params": {"threadId": "thread-1", "turn": {"id": "turn-1"}}}
                item = {"threadId": "thread-1", "turnId": "turn-1", "item": {"id": "message-1", "type": "agentMessage", "text": "Prepared proof complete."}}
                events = [start, self.rate(), {"method": "thread/tokenUsage/updated", "params": {"threadId": "thread-1", "turnId": "turn-1"}},
                          {"method": "item/started", "params": item}, {"method": "item/completed", "params": item}, self.rate(),
                          {"method": "turn/completed", "params": {"threadId": "thread-1", "turn": {"id": "turn-1", "status": "completed", "error": None}}}]
                response = {"id": 3, "result": {"turn": {"id": "turn-1"}}}
                frames = iter(([response] + events) if response_first else (events + [response]))
                c.request("turn/startPrepared", {"threadId": "thread-1"})
                if response_first:
                    for v in frames: c.event(v)
                self.assertTrue(c.fixture_flow.verify_complete()["completed_once"])
                c.fixture_flow.before_request("thread/read", {"threadId": "thread-1"})
                c.rpc_stage = "thread/read"
                c.event({"method": "thread/status/changed", "params": {"threadId": "thread-1"}})
                self.assertFalse(c.failed)

    def test_policy_cannot_enable_without_exact_build_notice_binding(self):
        from unittest.mock import patch
        with patch.object(host.subprocess, "Popen") as spawn:
            with self.assertRaises(host.HostRefusal):
                host.LiveClient([], Path("/unused"), Path("/unused"), 0, {}, fixture_notifications=True)
            spawn.assert_not_called()


class U2NativeNotificationTests(unittest.TestCase):
    def snapshot(self):
        return U2FixtureNotificationFlowTests().rate()["params"]["rateLimits"]

    def active(self):
        c = U2FixtureNoticeTests().client()
        c.native_notifications = True
        c.fixture_flow = host.NativeNotificationFlow()
        f = c.fixture_flow
        f.response("thread/start", {"thread": {"id": "thread-1"}})
        f.before_request("turn/prepare", {"threadId": "thread-1"}); f.response("turn/prepare", {})
        f.before_request("turn/startPrepared", {"threadId": "thread-1"})
        c.rpc_stage = "turn/startPrepared"
        c.event({"method": "turn/started", "params": {"threadId": "thread-1", "turn": {"id": "turn-1"}}})
        return c

    def test_real_rate_shapes_remain_metadata_only(self):
        c = self.active(); c.on_event = lambda *args: self.fail("rate forwarded")
        value = self.snapshot(); value.update(primary={"usedPercent": 42, "windowDurationMins": 300, "resetsAt": 1792830000},
            secondary={"usedPercent": 7, "windowDurationMins": 10080, "resetsAt": None},
            planType="pro", credits={"hasCredits": False, "unlimited": False, "balance": "0.00"},
            individualLimit={"limit": "100.0", "used": "12", "remainingPercent": 88, "resetsAt": 1792830000}, spendControlReached=False)
        before = deepcopy(value)
        for snapshot in [value, value, self.snapshot()]:
            c.event({"method": "account/rateLimits/updated", "params": {"rateLimits": snapshot}})
        self.assertEqual(value, before); self.assertEqual(c.fixture_flow.rate_updates, 3)
        self.assertFalse(c.fixture_flow.completed)
        self.assertTrue(all(set(x)=={"method","request","stage"} for x in c.events))

    def test_malformed_or_exhausted_rates_stop(self):
        for change in [lambda x:x.update(primary={"usedPercent": True,"windowDurationMins":300,"resetsAt":None}),
                       lambda x:x.update(primary={"usedPercent":100,"windowDurationMins":300,"resetsAt":None}),
                       lambda x:x.update(primary={"usedPercent":1,"windowDurationMins":False,"resetsAt":None}),
                       lambda x:x.update(spendControlReached=True), lambda x:x.update(spendControlReached=0),
                       lambda x:x.update(rateLimitReachedType="rate_limit_reached"), lambda x:x.update(planType=[]),
                       lambda x:x.update(credits={"hasCredits":True,"unlimited":False,"balance":"private-text"}),
                       lambda x:x.update(individualLimit={"limit":"10","used":"10","remainingPercent":0,"resetsAt":1}),
                       lambda x:x.update(extra=1), lambda x:x.update(limitName="x"*257)]:
            c=self.active(); value=self.snapshot(); change(value)
            with self.assertRaises(host.HostRefusal):c.event({"method":"account/rateLimits/updated","params":{"rateLimits":value}})
            self.assertTrue(c.failed); self.assertEqual(set(c.notification_failure),{"method","stage","error_type","params_bytes","params_sha256"})

    def test_native_turn_completion_and_next_turn_identity(self):
        c=self.active(); f=c.fixture_flow
        c.event({"method":"item/completed","params":{"threadId":"thread-1","turnId":"turn-1","item":{"type":"agentMessage","text":"2026-10-24 08:00:00 UTC"}}})
        c.event({"method":"turn/completed","params":{"threadId":"thread-1","turn":{"id":"turn-1","status":"completed","error":None}}})
        self.assertTrue(f.verify_complete()["completed_once"])
        f.before_request("thread/read",{"threadId":"thread-1"})
        f.before_request("turn/prepare",{"threadId":"thread-1"}); f.response("turn/prepare",{})
        self.assertEqual(f.thread,"thread-1"); self.assertIsNone(f.turn); self.assertFalse(f.completed)
        f.before_request("turn/startPrepared",{"threadId":"thread-1"})
        c.event({"method":"turn/started","params":{"threadId":"thread-1","turn":{"id":"turn-2"}}})
        with self.assertRaises(host.HostRefusal):c.event({"method":"turn/completed","params":{"threadId":"thread-1","turn":{"id":"turn-1","status":"completed","error":None}}})

    def test_native_phase_and_duplicate_completion_rejected(self):
        for case in ("early-rate","foreign-thread","foreign-turn","double-complete"):
            c=self.active(); f=c.fixture_flow
            with self.assertRaises(host.HostRefusal):
                if case=="early-rate":
                    f.consuming=False; c.event({"method":"account/rateLimits/updated","params":{"rateLimits":self.snapshot()}})
                elif case=="foreign-thread":c.event({"method":"thread/status/changed","params":{"threadId":"other"}})
                elif case=="foreign-turn":c.event({"method":"item/completed","params":{"threadId":"thread-1","turnId":"other","item":{"type":"agentMessage","text":"message"}}})
                else:
                    v={"method":"turn/completed","params":{"threadId":"thread-1","turn":{"id":"turn-1","status":"completed","error":None}}};c.event(v);c.event(v)
            self.assertTrue(c.failed)

    def test_native_notice_identity_and_default_boundary(self):
        from unittest.mock import patch
        runtime={"binary":"/synthetic/native","spec":"/synthetic/run/spec.json","binary_sha256":host.digest(b"candidate")}
        anchor={"version":13,"candidate":runtime["binary_sha256"],"launch_contract_sha256":"a"*64}
        spec={"root":"/synthetic/run","candidate":anchor["candidate"],"launch_contract_sha256":"a"*64,
              "launch_identity":{"cwd":"/synthetic/run/cwd","argv":[runtime["binary"],"--role","runtime","--spec",runtime["spec"]]}}
        with patch.object(host.Path,"resolve",lambda p,**kwargs:p),patch.object(host.codex,"artifact_read",return_value=b"candidate"):
            c=U2FixtureNoticeTests().client();host.bind_native_notifications(c,runtime,spec,anchor)
            self.assertIsInstance(c.fixture_flow,host.NativeNotificationFlow)
            self.assertIn("/synthetic/run/home/config.toml",c.fixture_notice_message)
            for key,value in [("version",12),("candidate","0"*64),("launch_contract_sha256","b"*64)]:
                bad={**anchor,key:value}
                with self.assertRaises(host.HostRefusal):host.bind_native_notifications(c,runtime,spec,bad)
            bad=deepcopy(spec);bad["launch_identity"]["cwd"]="/other"
            with self.assertRaises(host.HostRefusal):host.bind_native_notifications(c,runtime,bad,anchor)
        c=U2FixtureNoticeTests().client();c.native_notifications=True;c.fixture_notice_prepared=True;c.fixture_notice_pending=False
        c._fixture_notice_before_request("turn/prepare",{"threadId":"thread-1"})
        self.assertFalse(c.fixture_notice_pending)
        with self.assertRaises(host.HostRefusal):c._fixture_notice_before_request("turn/prepare",{"threadId":"other"})


class U2McpRecovery17Tests(U2NativeNotificationTests):
    def test_v14_native_notice_binding(self):
        from unittest.mock import patch
        runtime={"binary":"/synthetic/native","spec":"/synthetic/run/spec.json","binary_sha256":host.digest(b"candidate")}
        anchor={"version":14,"candidate":runtime["binary_sha256"],"launch_contract_sha256":"a"*64}
        spec={"root":"/synthetic/run","candidate":anchor["candidate"],"launch_contract_sha256":"a"*64,
              "launch_identity":{"cwd":"/synthetic/run/cwd","argv":[runtime["binary"],"--role","runtime","--spec",runtime["spec"]]}}
        with patch.object(host.Path,"resolve",lambda p,**kwargs:p),patch.object(host.codex,"artifact_read",return_value=b"candidate"):
            client=U2FixtureNoticeTests().client();host.bind_native_notifications(client,runtime,spec,anchor)
            self.assertIsInstance(client.fixture_flow,host.NativeNotificationFlow)


class U2PrelaunchRecovery18Tests(U2NativeNotificationTests):
    def test_v15_native_notice_binding(self):
        from unittest.mock import patch
        runtime={"binary":"/synthetic/native","spec":"/synthetic/run/spec.json","binary_sha256":host.digest(b"candidate")}
        anchor={"version":15,"candidate":runtime["binary_sha256"],"launch_contract_sha256":"a"*64}
        spec={"root":"/synthetic/run","candidate":anchor["candidate"],"launch_contract_sha256":"a"*64,
              "launch_identity":{"cwd":"/synthetic/run/cwd","argv":[runtime["binary"],"--role","runtime","--spec",runtime["spec"]]}}
        with patch.object(host.Path,"resolve",lambda p,**kwargs:p),patch.object(host.codex,"artifact_read",return_value=b"candidate"):
            client=U2FixtureNoticeTests().client();host.bind_native_notifications(client,runtime,spec,anchor)
            self.assertIsInstance(client.fixture_flow,host.NativeNotificationFlow)


class U2ConnectionContract19Tests(unittest.TestCase):
    def test_v15_transport_budget_keeps_six_prior_clock_starts(self):
        state={"events":[{"kind":"start","phase":"clock"} for _ in range(6)],
               "counts":{"control":6,"generation":0}}
        self.assertEqual(host.phase_transport_limit(state,"s4",15),40)
        self.assertEqual(host.phase_transport_limit(state,"s6",15),88)
        self.assertEqual(host.phase_transport_limit(state,"s4",14),40)


class U2NativeModerationMetadataTests(unittest.TestCase):
    def active(self):
        return U2NativeNotificationTests().active()

    def frame(self):
        return {"method":"turn/moderationMetadata","params":{"threadId":"thread-1","turnId":"turn-1","metadata":{"synthetic":True,"opaque":[1,"bounded"]}}}

    def test_bounded_metadata_is_not_forwarded_or_authoritative(self):
        c=self.active();c.on_event=lambda *args:self.fail("metadata forwarded")
        frame=self.frame();before=deepcopy(frame)
        c.event(frame);c.event(frame)
        self.assertEqual(frame,before);self.assertEqual(len(c.fixture_flow.moderation_metadata),2)
        self.assertFalse(c.fixture_flow.completed)
        self.assertEqual(set(c.fixture_flow.moderation_metadata[0]),{"bytes","sha256"})
        self.assertNotIn("opaque",str(c.fixture_flow.moderation_metadata))
        with self.assertRaises(host.HostRefusal):c.event(frame)

    def test_moderation_budget_resets_only_after_completed_turn(self):
        c=self.active(); f=c.fixture_flow; frame=self.frame()
        for turn in ("turn-1", "turn-2", "turn-3"):
            frame["params"]["turnId"]=turn
            c.event(frame); c.event(frame)
            self.assertEqual(len(f.moderation_metadata),2)
            with self.assertRaises(host.HostRefusal):
                f.event(frame["method"],frame["params"])
            c.event({"method":"item/completed","params":{"threadId":"thread-1","turnId":turn,"item":{"type":"agentMessage","text":"Synthetic completed turn."}}})
            c.event({"method":"turn/completed","params":{"threadId":"thread-1","turn":{"id":turn,"status":"completed","error":None}}})
            f.before_request("thread/read",{"threadId":"thread-1"})
            f.before_request("turn/prepare",{"threadId":"thread-1"})
            self.assertEqual(f.moderation_metadata,[])
            self.assertEqual(f.thread,"thread-1")
            with self.assertRaises(host.HostRefusal):
                f.event(frame["method"],frame["params"])
            if turn=="turn-3":break
            f.response("turn/prepare",{})
            f.before_request("turn/startPrepared",{"threadId":"thread-1"})
            next_turn="turn-"+str(int(turn[-1])+1)
            c.event({"method":"turn/started","params":{"threadId":"thread-1","turn":{"id":next_turn}}})
            with self.assertRaises(host.HostRefusal):
                f.event(frame["method"],frame["params"])

    def test_malformed_foreign_or_out_of_phase_metadata_is_rejected(self):
        for case in ["foreign-thread","foreign-turn","extra","oversize","unprepared","not-consuming","not-started","completed","request","bad-timestamp","fixture-only"]:
            with self.subTest(case=case):
                c=self.active();v=self.frame()
                if case=="foreign-thread":v["params"]["threadId"]="other"
                elif case=="foreign-turn":v["params"]["turnId"]="other"
                elif case=="extra":v["params"]["extra"]=1
                elif case=="oversize":v["params"]["metadata"]="x"*65537
                elif case=="unprepared":c.fixture_flow.prepared=False
                elif case=="not-consuming":c.fixture_flow.consuming=False
                elif case=="not-started":c.fixture_flow.started=False
                elif case=="completed":c.fixture_flow.completed=True
                elif case=="request":v["id"]=1
                elif case=="bad-timestamp":v["emittedAtMs"]=True
                elif case=="fixture-only":c.fixture_flow=host.FixtureNotificationFlow()
                with self.assertRaises(host.HostRefusal):c.event(v)
                self.assertTrue(c.failed)


class U2ClockErrorDiagnosticTests(unittest.TestCase):
    def frame(self):
        return {"method":"error","params":{"error":{"message":"prepared tool plan: unexpected tool identity","codexErrorInfo":"badRequest","additionalDetails":None,"misalignment":None},"willRetry":False,"threadId":"thread-1","turnId":"turn-1"}}

    def test_safe_diagnostic_still_rejects_runtime_error(self):
        c=U2NativeNotificationTests().active();c.clock_error_diagnostics=True
        c.on_event=lambda *args:self.fail("error forwarded")
        with self.assertRaises(host.HostRefusal):c.event(self.frame())
        self.assertTrue(c.failed);self.assertTrue(c.clock_error_evidence["text_recorded"])
        self.assertEqual(c.clock_error_evidence["message"],self.frame()["params"]["error"]["message"])
        self.assertFalse(c.fixture_flow.completed)

    def test_private_or_invalid_diagnostic_is_never_saved(self):
        for case in ["path","email","credential","url","oversize","foreign","request","not-clock","completed","extra","bad-time"]:
            with self.subTest(case=case):
                c=U2NativeNotificationTests().active();c.clock_error_diagnostics=True;v=self.frame()
                if case=="path":v["params"]["error"]["message"]="cannot read /Users/synthetic/private"
                elif case=="email":v["params"]["error"]["message"]="synthetic@example.invalid"
                elif case=="credential":v["params"]["error"]["message"]="Bearer syntheticcredential000000000"
                elif case=="url":v["params"]["error"]["message"]="https://example.invalid/private"
                elif case=="oversize":v["params"]["error"]["message"]="x"*4097
                elif case=="foreign":v["params"]["turnId"]="other"
                elif case=="request":v["id"]=1
                elif case=="not-clock":c.clock_error_diagnostics=False
                elif case=="completed":c.fixture_flow.completed=True
                elif case=="extra":v["params"]["extra"]=1
                elif case=="bad-time":v["emittedAtMs"]=True
                with self.assertRaises(host.HostRefusal):c.event(v)
                self.assertTrue(c.failed);self.assertNotIn("message",getattr(c,"clock_error_evidence",{}))


class U2NativeEnumProjectionTests(unittest.TestCase):
    def test_fixed_verifier_enum_matches_native_string_inference(self):
        self.assertEqual(host.native_document_schema({"enum":["DOC-LINKS","DOC-GFM","DOC-CLAIMS"]}), {"type":"string","enum":["DOC-LINKS","DOC-GFM","DOC-CLAIMS"]})


class U2OvernightCorrectionTests(unittest.TestCase):
    """Synthetic offline checks; never evidence of a new native/provider run."""
    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

    def test_remaining_turns_uses_current_epoch_and_preserves_acceptance(self):
        import json
        from types import SimpleNamespace
        class Captured(Exception):
            pass
        for version, used, remaining in ((56, 11, 2), (56, 12, None), (57, 15, 2), (57, 16, None), (1, 12, 28)):
            with self.subTest(version=version, used=used):
                session = object.__new__(host.LiveSession)
                session.budget = SimpleNamespace(anchor={"version": version}, read=lambda: {
                    "events": [{"kind": "turn", "phase": "h10"}] * used,
                    "counts": {"turn": 999}})
                session.phase, session.owner_text, session.spec = "h10", "Synthetic", {}
                session.admission = SimpleNamespace(identity=fixture.identity())
                session.documents = SimpleNamespace(progress=lambda: {})
                captured = []
                def turn(inputs):
                    captured.append(json.loads(inputs[1]["text"]))
                    raise Captured()
                session.turn = turn
                with self.assertRaises(Captured if remaining else host.HostRefusal):
                    session.iterate()
                self.assertEqual([v["remaining_turns"] for v in captured], [remaining] if remaining else [])
        accepted = host.trusted_turn_input("Synthetic", fixture.identity(), {}, 1, "sealed-handle")
        self.assertEqual(json.loads(accepted[1]["text"])["phase"], "sealed-accept-only")
        self.assertEqual(json.loads(accepted[1]["text"])["remaining_turns"], 1)

    def test_remaining_turns_rejects_invalid_unknown_or_wrong_phase(self):
        from types import SimpleNamespace
        for version, phase in ((True, "h10"), (0, "h10"), ("56", "h10"), (58, "h10"), (56, "synthetic")):
            with self.subTest(version=version, phase=phase):
                session = object.__new__(host.LiveSession)
                session.budget = SimpleNamespace(anchor={"version": version}, read=lambda: {"events": []})
                session.phase = phase
                with self.assertRaises(host.HostRefusal):
                    session.iterate()

    def test_delegated_actor_reserved_labels_and_identity_preservation(self):
        for actor in ("owner", "OWNER", "Human", "HUMAN", "ＯＷＮＥＲ", " owner", "human ", "delegate\x00", "", None, 1):
            with self.subTest(actor=actor):
                with self.assertRaises(host.HostRefusal):
                    host.Admission({**fixture.identity(), "actor": actor}, "s", "c", "t", [], None, "synthetic", "synthetic-01")
        identity = {**fixture.identity(), "actor": "Delegate-Synthetic"}
        admitted = host.Admission(identity, "s", "c", "t", [], None, "synthetic", "synthetic-01")
        self.assertEqual(admitted.identity, identity)
        self.assertEqual(admitted.identity_hash, host.digest(host.wire_bytes(identity)))

    def test_acceptance_publication_hides_partial_json(self):
        import json, os, stat, threading
        from unittest.mock import patch
        started, release = threading.Event(), threading.Event()
        original, errors = host.os.fdopen, []
        class Delayed:
            def __init__(self, stream): self.stream = stream
            def __enter__(self): self.stream.__enter__(); return self
            def __exit__(self, *args): return self.stream.__exit__(*args)
            def __getattr__(self, name): return getattr(self.stream, name)
            def write(self, data):
                started.set()
                if not release.wait(5): raise TimeoutError("synthetic scheduling gap")
                return self.stream.write(data)
        def fdopen(fd, mode, *args, **kwargs):
            stream = original(fd, mode, *args, **kwargs)
            return Delayed(stream) if mode == "wb" else stream
        def publish():
            try: host.publish_acceptance_request(self.root, {"command": "synthetic"})
            except BaseException as error: errors.append(error)
        with patch.object(host.os, "fdopen", side_effect=fdopen):
            thread = threading.Thread(target=publish); thread.start()
            try:
                self.assertTrue(started.wait(5))
                self.assertFalse((self.root / "accept-request.json").exists())
                self.assertTrue((self.root / "accept-request.json.partial").exists())
            finally:
                release.set(); thread.join(5)
        self.assertFalse(thread.is_alive()); self.assertEqual(errors, [])
        final = self.root / "accept-request.json"
        self.assertEqual(json.loads(host.control_read(final)), {"command": "synthetic"})
        self.assertEqual(stat.S_IMODE(final.stat().st_mode), 0o600)
        self.assertEqual(final.stat().st_nlink, 1)
        self.assertFalse((self.root / "accept-request.json.partial").exists())
        original = final.read_bytes()
        with self.assertRaises(host.HostRefusal): host.publish_acceptance_request(self.root, {"replacement": True})
        self.assertEqual(final.read_bytes(), original)

    def test_acceptance_kernel_no_clobber_and_partial_retention(self):
        from unittest.mock import patch
        import os
        original = host.os.fsync
        inserted = False
        def fsync(fd):
            nonlocal inserted
            original(fd)
            if not inserted:
                inserted = True
                host.durable_private(self.root / "accept-request.json", {"winner": True})
        with patch.object(host.os, "fsync", side_effect=fsync):
            with self.assertRaises(OSError): host.publish_acceptance_request(self.root, {"loser": True})
        self.assertEqual((self.root / "accept-request.json").read_bytes(), host.canonical({"winner": True}))
        partial = self.root / "accept-request.json.partial"
        self.assertEqual(partial.read_bytes(), host.canonical({"loser": True}))
        # A stale partial is a recovery condition, not an automatic retry.
        (self.root / "accept-request.json").unlink()
        with self.assertRaises(host.HostRefusal): host.publish_acceptance_request(self.root, {"retry": True})
        self.assertEqual(partial.read_bytes(), host.canonical({"loser": True}))

    def u2_budget(self, content_corrections=2):
        """Real journal/validator with a synthetic allocation and real stopped v1 parent."""
        import time
        from unittest.mock import patch
        old_root = self.root / "old"; old_root.mkdir()
        old = fixture.budget(host, old_root)
        old.reserve("stop", {"reason": "synthetic"}, allow_closeout=True)
        prior = old.read()
        now = time.time_ns() // 1_000_000
        cfg = deepcopy(host.u2_allocation(31))
        cfg["content_corrections"] = content_corrections
        cfg.update(parent_version=1, parent_rows=len(prior["rows"]), parent_counts=prior["counts"],
                   turns=2, prior_cap_ms=7_200_000, total_cap_ms=7_200_000, run_deadline_ms=now + 7_200_000)
        cfg["parent"] = {"anchor_sha256": old.anchor_sha256, "journal_sha256": host.digest(host.control_read(old.path)),
                         "last_seq": len(prior["rows"]) - 1, "last_sha256": prior["prev"]}
        self.enterContext(patch.dict(host.U2_ALLOCATIONS, {31: cfg}))
        def reference(name, value):
            path = self.root / (name + ".json"); host.durable_private(path, value)
            return {"path": str(path), "sha256": host.digest(host.control_read(path))}
        recovery = {"owner_message_id": cfg["owner_message_id"], "predecessor": {**cfg["parent"], "directory": str(old.directory)},
            "carry_active_ms": 1000, "total_cap_ms": cfg["total_cap_ms"], "uncertainty_reserve_ms": 858141,
            "closeout_reserve_ms": 1200000, "prior_attempts": cfg["prior_attempts"],
            "transition": {**{"old_" + k: old.anchor[k] for k in ("candidate", "source_identity", "input_identity")},
                           **{"new_" + k: old.anchor[k] for k in ("candidate", "source_identity", "input_identity")}}}
        recovery["accounting"] = reference("accounting", {"version": 1, "approval": old.anchor["approval"], "work": old.anchor["work"],
            "active_ms": 1000, "total_cap_ms": cfg["total_cap_ms"], "uncertainty_reserve_ms": 858141,
            "closeout_reserve_ms": 1200000, "prior_attempts": cfg["prior_attempts"]})
        recovery["checkpoint"] = reference("checkpoint", {"version": 1, "approval": old.anchor["approval"], "work": old.anchor["work"],
            "input_identity": old.anchor["input_identity"], "journal_seq": cfg["parent"]["last_seq"],
            "journal_sha256": prior["prev"], "sealed": False, "pending": False, "process_ids": []})
        recovery["resume_authorization"] = reference("authorization", {"version": 1, "owner_message_id": cfg["owner_message_id"],
            "approval_plan_sha256": cfg["approval_plan_sha256"], "failure_evidence": reference("failure", cfg["parent"]),
            "u2_policy": host.u2_policy(31), "allowed_starts": cfg["starts"], "launch_contract_sha256": "a" * 64})
        anchor = {**old.anchor, "version": 31, "origin_wall_ms": now, "origin_monotonic_ns": host.continuous_ns(),
            "approval_wall_ms": now, "run_deadline_ms": cfg["run_deadline_ms"], "total_deadline_ms": now + 7_199_000,
            "activity_clock": "mach_continuous_time_ns", "launch_mode": "trusted-native-runtime", "launch_contract_sha256": "a" * 64,
            "direct_tool_policy": {"version": 1, "mode": "direct", "model": "gpt-6-astra", "profiles": ["clock", "u2"], "approval": old.anchor["approval"]},
            "recovery": recovery}
        b = host.Budget.create(self.root / "new", anchor)
        b.reserve("proxy-start", {"slot": "s4", "start_id": cfg["proxy_start"]})
        phase, start = "synthetic", "synthetic-01"
        binding = {k: anchor[k] for k in ("launch_mode", "launch_contract_sha256", "approval", "direct_tool_policy")}
        binding["epoch_sha256"] = b.anchor_sha256
        b.reserve("start", {"execution_binding": binding}, phase, start)
        b.reserve("runtime-entered", {"start": start}, phase, start)
        for endpoint in ("models", "accounts"): b.reserve("control", {"endpoint": endpoint}, phase, start)
        b.reserve("thread", {"request": 1}, phase, start)
        b.reserve("thread-bound", {"request": 1, "thread": "synthetic-thread"}, phase, start)
        def begin(number):
            plan = "plan-" + str(number)
            b.reserve("input", {"plan": plan, "input_sha256": "a" * 64, "manifest_sha256": "b" * 64}, phase, start)
            b.reserve("turn", {"thread": "synthetic-thread", "plan": plan}, phase, start)
            subject = {"thread": "synthetic-thread", "turn": "turn-" + str(number), "plan": plan}
            b.reserve("generation", {**subject, "generation": 1}, phase, start)
            for kind in ("dispatch", "host-dispatch"):
                b.reserve(kind, {**subject, "call": "call-" + str(number)}, phase, start)
            return subject
        return b, begin

    def check_content_correction_cap(self, cap):
        b, begin = self.u2_budget(content_corrections=cap)
        first = begin(1)
        correction = {"class": "content", "oracle_sha256": "c" * 64, "failure": "d" * 64}
        b.reserve("correction", correction, "synthetic", "synthetic-01")
        b.reserve("worker-result", {"tool": "u2_verify", "result_sha256": "a" * 64,
            "result_identity": "b" * 64, "oracle_sha256": "c" * 64}, "synthetic", "synthetic-01")
        b.reserve("generation", {**first, "generation": 2}, "synthetic", "synthetic-01")
        begin(2)
        if cap == 2:
            b.reserve("correction", {**correction, "failure": "e" * 64}, "synthetic", "synthetic-01")
        before = b.path.read_bytes()
        with self.assertRaisesRegex(host.HostRefusal, "U2 cap/stop"):
            b.reserve("correction", {**correction, "failure": "f" * 64}, "synthetic", "synthetic-01")
        self.assertEqual(b.path.read_bytes(), before)
        self.assertEqual(b.read()["counts"]["correction-content"], cap)

    def test_content_correction_one_cap_refuses_second_distinct_failure(self):
        self.check_content_correction_cap(1)

    def test_content_correction_historical_two_cap_is_preserved(self):
        self.check_content_correction_cap(2)

    def test_worker_preflight_real_validator_cap_and_journal_unchanged(self):
        b, begin = self.u2_budget()
        first = begin(1)
        subject = {"tool": "u2_verify", "result_sha256": "a" * 64, "result_identity": "b" * 64, "oracle_sha256": "c" * 64}
        before = b.path.read_bytes()
        self.assertEqual(b.check_worker_result(subject, "synthetic", "synthetic-01", 300), 300)
        self.assertEqual(b.path.read_bytes(), before)
        b.reserve("worker-result", subject, "synthetic", "synthetic-01")
        b.reserve("generation", {**first, "generation": 2}, "synthetic", "synthetic-01")
        begin(2); before = b.path.read_bytes()
        with self.assertRaisesRegex(host.HostRefusal, "U2 cap/stop"):
            b.check_worker_result(subject, "synthetic", "synthetic-01", 300)
        self.assertEqual(b.path.read_bytes(), before)
        with self.assertRaisesRegex(host.HostRefusal, "U2 cap/stop"):
            b.reserve("worker-result", subject, "synthetic", "synthetic-01")
        self.assertEqual(b.path.read_bytes(), before)

    def test_worker_preflight_timeout_margin_and_stop(self):
        from unittest.mock import patch
        b, begin = self.u2_budget(); begin(1)
        subject = {"tool": "u2_write_file", "result_sha256": "a" * 64, "result_identity": "b" * 64, "oracle_sha256": "c" * 64}
        before = b.path.read_bytes(); state = b.read()
        for room in (20_000, 25_000):
            with patch.object(b, "_read_locked", return_value={**state, "remaining_ms": b.execution_reserve_ms() + room}):
                if room == 20_000:
                    with self.assertRaises(host.HostRefusal): b.check_worker_result(subject, "synthetic", "synthetic-01", 300)
                else:
                    self.assertEqual(b.check_worker_result(subject, "synthetic", "synthetic-01", 300), 5)
        self.assertEqual(b.path.read_bytes(), before)
        b.reserve("stop", {"reason": "synthetic"}, allow_closeout=True); before = b.path.read_bytes()
        with self.assertRaises(host.HostRefusal): b.check_worker_result(subject, "synthetic", "synthetic-01", 300)
        self.assertEqual(b.path.read_bytes(), before)

    def controller(self):
        import sys, time
        from unittest.mock import Mock
        spec = fixture.documents(host, self.root)
        for name in ("run", "scratch"): (self.root / name).mkdir()
        template = self.root / "worker.sb.in"
        template.write_text('; @@ANCESTOR_METADATA_LITERALS@@\n; @@APPROVED_INPUT_READ_LITERALS@@\n; @@EXACT_WRITE_TARGET_AND_SWAP@@ only for write operation, omitted for read and all verifiers.\n')
        for name in ("worker.py", "parser.js"): (self.root / name).write_text("synthetic")
        c = object.__new__(host.DocumentController)
        c.contract_version = 1
        c.spec = {**spec, "scratch": str(self.root / "scratch"), "python": sys.executable,
            "worker": str(self.root / "worker.py"), "worker_sha256": "a" * 64,
            "parser": str(self.root / "parser.js"), "profile_template": str(template),
            "profile_template_sha256": host.digest(template.read_bytes()), "allowed_identifiers": []}
        c.files, c.run, c.budget = spec["files"], self.root / "run", Mock()
        c.budget.anchor = {"version": 31}
        c.budget.check_worker_result.return_value = 30
        c.sealed, c.active, c.sequence = False, None, 0
        c.deadline = time.monotonic() + 60
        c.oracle_sha256, c.phase, c.start = "a" * 64, "synthetic", "synthetic-01"
        c.last_failure, c.correction_open, c.written_ids, c.verifiers = None, False, set(), {}
        return c

    def test_worker_rejection_prevents_spawn_without_refunding_correction(self):
        from unittest.mock import patch
        c = self.controller(); c.last_failure = "b" * 64
        c.budget.check_worker_result.side_effect = host.HostRefusal("synthetic cap")
        with patch.object(host.subprocess, "Popen") as spawn:
            with self.assertRaises(host.HostRefusal):
                c.dispatch("u2_write_file", {"file_id": "Output", "expected_sha256": c.files["Output"]["sha256"], "content": "Synthetic"})
        spawn.assert_not_called()
        self.assertEqual(c.budget.reserve.call_args.args[0], "correction")
        self.assertEqual(c.budget.reserve.call_count, 1)
        self.assertTrue(c.correction_open)
        self.assertEqual((self.root / "output.md").read_text(), "# Draft\n\nRequired claim is missing.\n")

    def diagnostic_case(self, failure):
        import io, json
        from unittest.mock import Mock, patch
        c = self.controller()
        process = Mock(pid=123456, returncode=0, stdin=io.BytesIO(), stdout=io.BytesIO())
        def communicate(data, timeout):
            request = json.loads(data)
            (self.root / "output.md").write_text(request["arguments"]["content"])
            observed, _ = host.file_record(self.root / "output.md")
            if failure == "postcondition": observed["sha256"] = "0" * 64
            return host.canonical({"ok": True, "result": observed}), b""
        process.communicate.side_effect = communicate
        original_check = c.check_files
        calls = 0
        def check():
            nonlocal calls
            calls += 1
            if failure == "postcheck" and calls == 2: raise host.HostRefusal("synthetic postcheck")
            original_check()
        original_error = OSError("synthetic journal I/O")
        if failure in ("append", "diagnostic"):
            c.budget.reserve.side_effect = original_error
        original_save = host.durable_private
        def save(path, value):
            if failure == "diagnostic" and path.name == "journal-failure.json": raise RuntimeError("synthetic diagnostic I/O")
            original_save(path, value)
        with patch.object(host.subprocess, "Popen", return_value=process) as spawn, \
             patch.object(host.contracts, "end_process", return_value={"process_group_absent": True}), \
             patch.object(c, "check_files", side_effect=check), patch.object(host.contracts, "durable_private", side_effect=save):
            with self.assertRaises(OSError if failure in ("append", "diagnostic") else host.HostRefusal) as raised:
                c.dispatch("u2_write_file", {"file_id": "Output", "expected_sha256": c.files["Output"]["sha256"], "content": "Synthetic changed"})
        self.assertEqual(spawn.call_count, 1)
        self.assertEqual(process.communicate.call_count, 1)
        self.assertIsNone(c.active)
        self.assertEqual((self.root / "output.md").read_text(), "Synthetic changed")
        self.assertTrue((c.run / "worker-001/request.json").is_file())
        if failure == "diagnostic":
            self.assertIs(raised.exception, original_error)
            self.assertIsInstance(raised.exception.__cause__, RuntimeError)
            return
        record = json.loads((c.run / "worker-001/journal-failure.json").read_bytes())
        self.assertEqual(record["effect_applied"], None if failure == "postcondition" else True)
        self.assertEqual(record["journal_outcome"], "unconfirmed" if failure == "append" else "not_attempted")
        self.assertEqual(record["effect_applied_unjournaled"], True if failure == "postcheck" else None)
        self.assertEqual(c.budget.reserve.call_count, 1 if failure == "append" else 0)

    def test_worker_applied_but_append_unconfirmed_diagnostic(self): self.diagnostic_case("append")
    def test_worker_applied_postcheck_failure_diagnostic(self): self.diagnostic_case("postcheck")
    def test_worker_unknown_effect_postcondition_failure_diagnostic(self): self.diagnostic_case("postcondition")
    def test_worker_diagnostic_failure_preserves_original_exception(self): self.diagnostic_case("diagnostic")
