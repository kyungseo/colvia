"""Preparation/entry contracts; real bootstrap/runtime lives in isolated artifact checks."""
import ast
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import warnings

SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("distribution_macos", SOURCE / "distribution/macos.py")
macos = importlib.util.module_from_spec(spec)
spec.loader.exec_module(macos)


class MacOSDistributionTests(unittest.TestCase):
    def test_header_is_python_and_preserves_inventory_parser(self):
        from hv2ref.product import _parse_launcher_inventory_window
        entry = (SOURCE / "colvia").read_bytes().split(b"\n", 1)[1]
        data = macos.header("a" * 64) + entry
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            compile(data, "colvia", "exec")
        self.assertEqual("continuation-1", _parse_launcher_inventory_window(data))
        self.assertTrue(data.startswith(b"#!/bin/sh\n"))
        self.assertNotIn(b"eval ", data.split(b"from __future__", 1)[0])

    def test_fixture_entry_diff_is_only_literal_store_location(self):
        a = macos.header("a" * 64)
        b = macos.header("a" * 64, fixture_root=Path("/fixture/Application Support/Colvia"))
        import difflib
        changes = [x for x in difflib.ndiff(a.decode().splitlines(), b.decode().splitlines()) if x[:2] in ("- ", "+ ")]
        self.assertEqual(2, len(changes))
        self.assertIn("store=", changes[0]); self.assertIn("store=", changes[1])

    def test_bad_pin_and_unfixed_origin_refused(self):
        with self.assertRaises(ValueError):
            macos.header("latest")
        with self.assertRaises(ValueError):
            macos.bootstrap({"assets": {}}, "a" * 64, origin="http://example.com/latest")

    def test_unsafe_tar_names_refused(self):
        for name in ("../x", "/x", "a//b", "a/./b", "a\nb", "a b"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                macos.tar_bytes({name: b"x"}, set())

    def test_archive_is_reproducible(self):
        one = macos.tar_bytes({"a": b"text", "bin/b": b"exec"}, {"bin/b"})
        two = macos.tar_bytes({"bin/b": b"exec", "a": b"text"}, {"bin/b"})
        self.assertEqual(one, two)

    def test_windows_cannot_enter_new_macos_tuple(self):
        from hv2ref import workspace
        with patch.object(sys, "platform", "win32"):
            self.assertFalse(workspace.managed_macos_runtime_supported())
            self.assertFalse(workspace.runtime_supported("continuation-1"))
        self.assertEqual(((3, 14, 6), (3, 14, 7)), workspace.SUPPORTED_PYTHON_VERSIONS)

    def test_manager_builder_marker_and_future_import(self):
        raw = (SOURCE / "distribution/manager.py").read_bytes()
        self.assertEqual(1, raw.count(b"CONFIG: dict = {}"))
        raw = b"from __future__ import annotations\n" + raw.split(b"from __future__ import annotations\n", 1)[1]
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            ast.parse(macos.header("a" * 64) + raw)


class MacOSGitEntryTests(unittest.TestCase):
    def test_apple_shim_selects_real_git_without_xcrun(self):
        from hv2ref import workspace
        import subprocess
        observation = subprocess.CompletedProcess([], 0, b"/Applications/Xcode.app/Contents/Developer\n", b"")
        with patch.object(sys, "platform", "darwin"), patch.object(workspace.shutil, "which", return_value="/usr/bin/git"), patch.object(workspace.subprocess, "run", return_value=observation) as run, patch.object(Path, "is_file", return_value=True), patch.object(Path, "resolve", return_value=Path("/Applications/Xcode.app/Contents/Developer/usr/bin/git")), patch.object(Path, "stat", return_value=type("Info", (), {"st_mode": 0o100755})()):
            self.assertEqual("/Applications/Xcode.app/Contents/Developer/usr/bin/git", workspace.git_executable())
            self.assertEqual(["/usr/bin/xcode-select", "-p"], run.call_args.args[0])

    def test_missing_developer_tools_are_unavailable_without_install_prompt(self):
        from hv2ref import workspace
        import subprocess
        observation = subprocess.CompletedProcess([], 2, b"", b"xcode-select: error: unable to get active developer directory")
        with patch.object(sys, "platform", "darwin"), patch.object(workspace.shutil, "which", return_value="/usr/bin/git"), patch.object(workspace.subprocess, "run", return_value=observation), self.assertRaises(FileNotFoundError):
            workspace.git_executable()

    def test_explicit_git_and_windows_keep_existing_selection(self):
        from hv2ref import workspace
        with patch.object(sys, "platform", "darwin"), patch.object(workspace.shutil, "which", return_value="/selected/git"), patch.object(workspace.subprocess, "run") as run:
            self.assertEqual("git", workspace.git_executable());run.assert_not_called()
        with patch.object(sys, "platform", "win32"), patch.object(workspace.subprocess, "run") as run:
            self.assertEqual("git", workspace.git_executable());run.assert_not_called()

    def test_only_exact_config_disable_tuple_crosses_environment_boundary(self):
        from hv2ref import workspace
        import os
        closed = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}
        with patch.dict(os.environ, closed | {"GIT_DIR": "/wrong", "GIT_CONFIG_COUNT": "1"}, clear=True):
            value = workspace.git_environment()
            for key, expected in closed.items():self.assertEqual(expected, value[key])
            self.assertNotIn("GIT_DIR", value);self.assertNotIn("GIT_CONFIG_COUNT", value)
        with patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": "/unexpected"}, clear=True):
            self.assertNotIn("GIT_CONFIG_GLOBAL", workspace.git_environment())

    def test_failed_preview_with_save_preserves_original_error_and_never_writes(self):
        import argparse
        import contextlib
        import io
        import json
        import subprocess
        manager_spec = importlib.util.spec_from_file_location("distribution_manager", SOURCE / "distribution/manager.py")
        manager = importlib.util.module_from_spec(manager_spec);manager_spec.loader.exec_module(manager)
        manager.CONFIG = {"profiles": {"continuation-1": {"release": {"id": "fixture"}}}, "runtime_id": "fixture"}
        args = argparse.Namespace(command="install", profile="continuation-1", target=Path("/fixture/project"), apply=False,
                                  input=None, confirm=None, recover=False, save=Path("/must-not-write"), json=True, details=False, backup=None, to=None)
        error = {"classification": "fail", "code": "HV2-WORKSPACE-TARGET", "message": "original failure"}
        result = subprocess.CompletedProcess([], 65, json.dumps(error).encode(), b"")
        with patch.object(manager, "validate_payload"), patch.object(manager, "clean_environment", return_value={}), patch.object(manager, "run_lifecycle", return_value=result), patch.object(manager, "write_new") as writer, contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(65, manager.lifecycle(args, Path("/fixture")))
            self.assertEqual(error, json.loads(out.getvalue()));writer.assert_not_called()


class ManagedPayloadTests(unittest.TestCase):
    def setUp(self):
        import hashlib
        import tempfile
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.root.chmod(0o700)
        self.spec = importlib.util.spec_from_file_location("distribution_manager_check", SOURCE / "distribution/manager.py")
        self.manager = importlib.util.module_from_spec(self.spec)
        self.spec.loader.exec_module(self.manager)
        files = {"colvia": b"synthetic launcher", "docs/a.md": b"synthetic document"}
        self.manager.CONFIG = {"profiles": {"fixture": {"files": {k: hashlib.sha256(v).hexdigest() for k, v in files.items()}}}}
        for name, raw in files.items():
            p = self.root / name
            p.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            p.write_bytes(raw)
            p.chmod(0o500 if name == "colvia" else 0o400)

    def test_exact_prepared_payload_accepted(self):
        self.manager.validate_payload(self.root, "fixture")

    def test_extra_empty_directory_refused(self):
        (self.root / "unexpected").mkdir(mode=0o700)
        with self.assertRaises(ValueError): self.manager.validate_payload(self.root, "fixture")

    def test_changed_file_mode_refused(self):
        (self.root / "docs/a.md").chmod(0o600)
        with self.assertRaises(ValueError): self.manager.validate_payload(self.root, "fixture")

    def test_symlink_and_shared_file_refused(self):
        import os
        p = self.root / "docs/a.md"
        raw = p.read_bytes()
        p.unlink(); p.symlink_to(self.root / "colvia")
        with self.assertRaises(ValueError): self.manager.validate_payload(self.root, "fixture")
        p.unlink(); p.write_bytes(raw); p.chmod(0o400)
        os.link(p, self.root / "shared")
        with self.assertRaises(ValueError): self.manager.validate_payload(self.root, "fixture")


class ReviewCorrectionTests(unittest.TestCase):
    def test_manifest_and_origin_are_bound_at_build_time(self):
        m = {"assets": {}}
        origin = "https://github.com/example/colvia/releases/download/v1"
        with self.assertRaises(ValueError): macos.bootstrap(m, "a" * 64, origin=origin)
        with self.assertRaises(ValueError): macos.bootstrap(m, macos.digest(macos.canonical(m)), origin=origin.replace("github.com", "githubXcom"))

    def test_runtime_slots_preserve_old_verifier_identity(self):
        self.assertNotEqual(macos.runtime_slot("a" * 64), macos.runtime_slot("b" * 64))
        self.assertIn(macos.runtime_slot("a" * 64).encode(), macos.header("a" * 64))

    def test_relative_fixture_root_refused(self):
        with self.assertRaises(ValueError): macos.header("a" * 64, fixture_root=Path("relative"))

    def test_git_timeout_has_contract_error(self):
        import subprocess
        from hv2ref import workspace
        from hv2ref.errors import ContractError
        with patch.object(sys, "platform", "darwin"), patch.object(workspace.shutil, "which", return_value="/usr/bin/git"), patch.object(workspace.subprocess, "run", side_effect=subprocess.TimeoutExpired("xcode-select", 10)), self.assertRaises(ContractError):
            workspace.git_executable()

    def test_source_developer_override_and_clt_path(self):
        import os
        import subprocess
        from hv2ref import workspace
        selected = Path("/Library/Developer/CommandLineTools/usr/bin/git")
        response = subprocess.CompletedProcess([], 0, b"/Library/Developer/CommandLineTools\n", b"")
        with patch.object(sys, "platform", "darwin"), patch.object(workspace.shutil, "which", return_value="/usr/bin/git"), patch.dict(os.environ, {"DEVELOPER_DIR": "/selected/tools"}), patch.object(workspace.subprocess, "run", return_value=response) as run, patch.object(Path, "is_file", return_value=True), patch.object(Path, "resolve", return_value=selected), patch.object(Path, "stat", return_value=type("Info", (), {"st_mode": 0o100755})()):
            self.assertEqual(str(selected), workspace.git_executable())
            self.assertEqual("/selected/tools", run.call_args.kwargs["env"]["DEVELOPER_DIR"])

    def test_closed_git_cannot_inherit_user_attributes(self):
        import os
        from hv2ref import workspace
        with patch.dict(os.environ, {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "XDG_CONFIG_HOME": "/unexpected/config"}, clear=True):
            env = workspace.git_environment()
            self.assertEqual("/dev/null", env["XDG_CONFIG_HOME"])
            self.assertEqual("1", env["GIT_ATTR_NOSYSTEM"])


class ManagerRemovalTests(unittest.TestCase):
    def setUp(self):
        import tempfile, hashlib
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        spec = importlib.util.spec_from_file_location("removal_manager", SOURCE / "distribution/manager.py")
        self.manager = importlib.util.module_from_spec(spec); spec.loader.exec_module(self.manager)
        self.manager.CONFIG = {"runtime_id": "fixture"}
        raw = b"synthetic retained manager"
        self.identity = hashlib.sha256(raw).hexdigest()
        self.active = self.root / "bin/colvia-manage"
        self.retained = self.root / "tools" / self.identity / "colvia-manage"
        for p in (self.active, self.retained):
            p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(raw)

    def remove(self, token=None):
        import contextlib, io
        with patch.object(self.manager, "store_root", return_value=self.root), patch.object(self.manager, "verify_runtime"), patch.object(sys, "argv", ["manager", "remove-tool", "--apply", "--confirm", token or self.identity]), contextlib.redirect_stdout(io.StringIO()):
            return self.manager.main()

    def test_remove_conflict_preserves_active_recovery_and_other_lock(self):
        (self.root / "activation.lock").mkdir()
        with self.assertRaises(ValueError): self.remove()
        self.assertEqual(self.active.read_bytes(), self.retained.read_bytes())
        self.assertTrue((self.root / "activation.lock").is_dir())

    def test_wrong_confirmation_preserves_active_and_releases_own_lock(self):
        with self.assertRaises(ValueError): self.remove("0" * 64)
        self.assertTrue(self.active.exists()); self.assertTrue(self.retained.exists())
        self.assertFalse((self.root / "activation.lock").exists())

    def test_exact_remove_retains_recovery_and_releases_lock(self):
        self.assertEqual(0, self.remove())
        self.assertFalse(self.active.exists()); self.assertTrue(self.retained.exists())
        self.assertFalse((self.root / "activation.lock").exists())

    def test_bad_notices_refuse_before_release_or_runtime_publication(self):
        import hashlib
        stage = self.root / "staging/test"
        stage.mkdir(parents=True); (self.root / "activation.lock").mkdir()
        (stage / "product.tar").write_bytes(b"payload")
        (stage / "notices.tar").write_bytes(b"changed notices")
        self.manager.CONFIG.update(product_archive_sha256=hashlib.sha256(b"payload").hexdigest(), notices_sha256="0" * 64)
        binary = stage / "runtime/python/bin/python3.14"
        binary.parent.mkdir(parents=True); binary.touch()
        with patch.object(self.manager, "store_root", return_value=self.root), patch.object(self.manager, "verify_runtime"), patch.object(sys, "executable", str(binary)), self.assertRaisesRegex(ValueError, "라이선스"):
            self.manager.activate(stage)
        for name in ("releases", "runtimes"):
            self.assertFalse((self.root / name).exists(), name)


class ManagerReviewTests(unittest.TestCase):
    setUp = ManagerRemovalTests.setUp
    def test_interrupted_publish_preserves_pending_without_partial_final(self):
        path = self.root / "new-file"
        with patch.object(self.manager, "publish_file", side_effect=OSError("synthetic interruption")), self.assertRaises(OSError):
            self.manager.write_new(path, b"complete bytes")
        self.assertFalse(path.exists())
        self.assertEqual([b"complete bytes"], [p.read_bytes() for p in self.root.glob(".pending-*")])
        self.manager.write_new(path, b"complete bytes")
        self.assertEqual(b"complete bytes", path.read_bytes())
        self.assertEqual(1, path.stat().st_nlink)
        with self.assertRaises(FileExistsError): self.manager.write_new(path, b"different")
        self.assertEqual(b"complete bytes", path.read_bytes())

    def test_existing_official_profile_is_retained_without_flag(self):
        import argparse, json
        target = self.root / "project"
        binding = target / ".hrn/product/binding.json"
        binding.parent.mkdir(parents=True)
        binding.write_text(json.dumps({"active_release": {"inventory_id": "official-execution-2"}}))
        self.manager.CONFIG["profiles"] = {"continuation-1": {}, "official-execution-2": {}}
        for action in ("status", "doctor", "repair", "update", "rollback", "remove"):
            args = argparse.Namespace(profile=None, command=action, target=target)
            self.assertEqual("official-execution-2", self.manager.selected_profile(args))
        self.assertEqual("official-execution-2", self.manager.selected_profile(argparse.Namespace(profile=None, command="install", target=target)))

    def test_preview_is_saved_and_warning_does_not_hide_success(self):
        import argparse, contextlib, io, json, subprocess
        (self.root / "requests").mkdir()
        self.manager.CONFIG.update(profiles={"continuation-1": {"release": {"id": "fixture"}}})
        args = argparse.Namespace(command="install", profile=None, target=self.root / "project", apply=False,
            input=None, confirm=None, recover=False, save=None, json=True, details=False, backup=None, to=None)
        value = {"classification": "preview", "request": {"operation_id": "exact"}, "confirm_token": "synthetic"}
        response = subprocess.CompletedProcess([], 0, json.dumps(value).encode(), b"synthetic warning")
        with patch.object(self.manager, "validate_payload"), patch.object(self.manager, "run_lifecycle", return_value=response), contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(0, self.manager.lifecycle(args, self.root))
        shown = json.loads(out.getvalue())
        self.assertEqual(value["request"], json.loads(Path(shown["request_file"]).read_bytes()))
        self.assertEqual(value["confirm_token"], shown["confirm_token"])
        self.assertIn("추가 진단", err.getvalue())


    def test_malformed_binding_keeps_diagnostics_available_and_blocks_writes(self):
        import argparse, json
        target = self.root / "project"; binding = target / ".hrn/product/binding.json"
        binding.parent.mkdir(parents=True)
        self.manager.CONFIG["profiles"] = {"continuation-1": {}, "official-execution-2": {}}
        for raw in ("{", "[]", "{}", json.dumps({"active_release": {"inventory_id": []}})):
            binding.write_text(raw)
            for command in ("status", "doctor"):
                self.assertEqual("continuation-1", self.manager.selected_profile(argparse.Namespace(profile=None, command=command, target=target)))
            with self.assertRaisesRegex(ValueError, "status --details"):
                self.manager.selected_profile(argparse.Namespace(profile=None, command="repair", target=target))

    def test_interrupt_and_termination_close_child_group(self):
        import json, os, signal, subprocess, time
        for sig in (signal.SIGINT, signal.SIGTERM):
            with self.subTest(signal=sig):
                ready = self.root / ("ready-" + str(sig) + ".json")
                child_code = "import os,time,pathlib;p=pathlib.Path(" + repr(str(ready)) + ");q=p.with_suffix('.pending');q.write_text(str(os.getpid()));q.replace(p);time.sleep(60)"
                code = "import importlib.util,os,sys;from pathlib import Path;spec=importlib.util.spec_from_file_location('m'," + repr(str(SOURCE / 'distribution/manager.py')) + ");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.clean_environment=lambda:dict(os.environ);m.run_lifecycle([sys.executable,'-I','-B','-c'," + repr(child_code) + "])"
                parent = subprocess.Popen([sys.executable, "-I", "-B", "-c", code], stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
                try:
                    limit = time.monotonic() + 10
                    while not ready.exists() and time.monotonic() < limit:
                        self.assertIsNone(parent.poll()); time.sleep(.02)
                    self.assertTrue(ready.exists()); child = int(ready.read_text())
                    os.kill(parent.pid, sig); out, err = parent.communicate(timeout=10)
                    self.assertNotEqual(0, parent.returncode)
                    self.assertIn("자식 프로세스 종료를 확인".encode(), err)
                    with self.assertRaises(ProcessLookupError): os.killpg(child, 0)
                finally:
                    if parent.poll() is None: os.killpg(parent.pid, signal.SIGKILL); parent.wait(timeout=5)


    def test_signal_flag_reaches_cleanup_without_async_exception(self):
        import signal, subprocess
        handlers = {}
        proc = unittest.mock.Mock(pid=12345, returncode=-15)
        def register(sig, handler): handlers[sig] = handler
        def first_communication(**kw):
            handlers[signal.SIGTERM](signal.SIGTERM, None)
        proc.communicate.side_effect = [lambda: None]
        calls = 0
        def communicate(**kw):
            nonlocal calls
            calls += 1
            if calls == 1: first_communication(**kw)
            return b"", b""
        proc.communicate.side_effect = communicate
        with patch.object(self.manager.signal, "signal", side_effect=register), patch.object(self.manager.signal, "getsignal", return_value=signal.SIG_DFL), patch.object(self.manager, "clean_environment", return_value={}), patch.object(self.manager.subprocess, "Popen", return_value=proc), patch.object(self.manager.os, "killpg", side_effect=[None, ProcessLookupError]) as kill:
            with self.assertRaisesRegex(ValueError, "자식 프로세스 종료를 확인"):
                self.manager.run_lifecycle(["synthetic"])
            self.assertEqual([unittest.mock.call(12345, signal.SIGTERM), unittest.mock.call(12345, 0)], kill.call_args_list)
            self.assertEqual(2, calls)


    def test_saved_init_request_selects_official_profile_before_binding_exists(self):
        import argparse, json
        self.manager.CONFIG["profiles"] = {"continuation-1": {}, "official-execution-2": {}}
        request = self.root / "init.json"
        request.write_text(json.dumps({"format": {}, "plan": {"candidate_release": {"inventory_id": "official-execution-2"}}}))
        args = argparse.Namespace(profile=None, command="install", apply=True, input=request, target=self.root / "new-project")
        self.assertEqual("official-execution-2", self.manager.selected_profile(args))


    def test_interruption_during_process_handle_creation_uses_cleanup(self):
        import signal
        from types import SimpleNamespace
        calls = []
        child = SimpleNamespace(pid=12345, returncode=0,
                                communicate=lambda **kw: (b"", b""))
        def create(*args, **kwargs):
            signal.getsignal(signal.SIGTERM)(signal.SIGTERM, None)
            return child
        def kill(pid, sig):
            calls.append((pid, sig))
            if sig == 0: raise ProcessLookupError()
        with patch.object(self.manager, "clean_environment", return_value={}), \
             patch.object(self.manager.subprocess, "Popen", side_effect=create), \
             patch.object(self.manager.os, "killpg", side_effect=kill):
            with self.assertRaisesRegex(ValueError, "자식 프로세스 종료를 확인"):
                self.manager.run_lifecycle(["synthetic"])
        self.assertEqual(calls, [(12345, signal.SIGTERM), (12345, 0)])


    def test_repeated_signals_during_timeout_cleanup_do_not_raise(self):
        import signal, subprocess
        handlers = {}; delivered = []
        proc = unittest.mock.Mock(pid=12345, returncode=-15)
        proc.communicate.side_effect = [subprocess.TimeoutExpired("synthetic", .2), (b"", b"")]
        def register(sig, handler):
            # Reproduce the old gap before every handler had become SIG_IGN.
            if handler == signal.SIG_IGN and not delivered:
                delivered.append(signal.SIGHUP)
                handlers[signal.SIGHUP](signal.SIGHUP, None)
            handlers[sig] = handler
        def kill(pid, sig):
            if sig == 0: raise ProcessLookupError()
            for incoming in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
                delivered.append(incoming)
                handlers[incoming](incoming, None)
        with patch.object(self.manager.signal, "signal", side_effect=register), \
             patch.object(self.manager.signal, "getsignal", return_value=signal.SIG_DFL), \
             patch.object(self.manager, "clean_environment", return_value={}), \
             patch.object(self.manager.subprocess, "Popen", return_value=proc), \
             patch.object(self.manager.time, "monotonic", side_effect=[0, 0, 301]), \
             patch.object(self.manager.os, "killpg", side_effect=kill) as stop:
            with self.assertRaisesRegex(ValueError, "자식 프로세스 종료를 확인"):
                self.manager.run_lifecycle(["synthetic"])
        self.assertEqual([signal.SIGINT, signal.SIGTERM, signal.SIGHUP], delivered)
        self.assertEqual([unittest.mock.call(12345, signal.SIGTERM), unittest.mock.call(12345, 0)], stop.call_args_list)
        self.assertEqual([unittest.mock.call(timeout=.2), unittest.mock.call(timeout=2)], proc.communicate.call_args_list)

    def test_short_poll_timeouts_preserve_success_output_and_deadline(self):
        import subprocess
        proc = unittest.mock.Mock(pid=12345, returncode=0)
        proc.communicate.side_effect = [subprocess.TimeoutExpired("synthetic", .2), (b"output", b"warning")]
        with patch.object(self.manager, "clean_environment", return_value={}), \
             patch.object(self.manager.subprocess, "Popen", return_value=proc), \
             patch.object(self.manager.time, "monotonic", side_effect=[0, 0, 299.9]), \
             patch.object(self.manager.os, "killpg") as stop:
            result = self.manager.run_lifecycle(["synthetic"])
        self.assertEqual((0, b"output", b"warning"), (result.returncode, result.stdout, result.stderr))
        self.assertAlmostEqual(.2, proc.communicate.call_args_list[0].kwargs["timeout"])
        self.assertAlmostEqual(.1, proc.communicate.call_args_list[1].kwargs["timeout"])
        stop.assert_not_called()

    def test_deep_json_keeps_diagnostics_and_preserves_binding_and_request(self):
        import argparse
        target = self.root / "project"; binding = target / ".hrn/product/binding.json"
        binding.parent.mkdir(parents=True)
        raw = ("[" * (sys.getrecursionlimit() * 2) + "0" + "]" * (sys.getrecursionlimit() * 2)).encode()
        binding.write_bytes(raw)
        self.manager.CONFIG["profiles"] = {"continuation-1": {}, "official-execution-2": {}}
        for command in ("status", "doctor"):
            self.assertEqual("continuation-1", self.manager.selected_profile(argparse.Namespace(profile=None, command=command, target=target)))
        with self.assertRaisesRegex(ValueError, "status --details"):
            self.manager.selected_profile(argparse.Namespace(profile=None, command="repair", target=target))
        request = self.root / "deep-request.json"; request.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, "status --details"):
            self.manager.selected_profile(argparse.Namespace(profile=None, command="install", target=target, apply=True, input=request))
        self.assertEqual(raw, binding.read_bytes()); self.assertEqual(raw, request.read_bytes())
