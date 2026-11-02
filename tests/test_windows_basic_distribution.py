"""Windows management dispatch and native request-file boundaries."""
import argparse
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest import mock

SOURCE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("windows_manage", SOURCE / "distribution/windows/manage.py")
manage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(manage)


class ProjectLauncherTests(unittest.TestCase):
    def dispatch(self, args, *, same_launcher=True):
        target = SOURCE / "synthetic-project"
        entry = {"workspace_source": mock.Mock(), "windows_runtime_observation": lambda: {"supported": True},
                 "regular_bytes": lambda p: b"known" if same_launcher or p == manage.CORE / "colvia" else b"changed"}
        options = argparse.Namespace(command="project", target=target, args=args)
        child = mock.Mock(return_value=argparse.Namespace(returncode=13))
        with (mock.patch.object(sys, "platform", "win32"),
              mock.patch.object(sys, "flags", argparse.Namespace(isolated=1)),
              mock.patch.object(sys, "dont_write_bytecode", True),
              mock.patch.object(sys, "argv", ["manage.py", str(SOURCE / "synthetic-store")]),
              mock.patch.object(manage, "arguments", return_value=options),
              mock.patch.object(manage.runpy, "run_path", return_value=entry),
              mock.patch.object(manage.subprocess, "run", child)):
            if same_launcher and args == ["--", "intent", "draft"]:
                self.assertEqual(13, manage.main())
                child.assert_called_once_with([sys.executable, "-I", "-B", str(target / "colvia"), "intent", "draft"],
                                              cwd=target, check=False)
            else:
                with self.assertRaises(ValueError):
                    manage.main()
                child.assert_not_called()
        entry["workspace_source"].assert_called_once_with(target)

    def test_uses_verified_project_entry_and_returns_actual_status(self):
        self.dispatch(["--", "intent", "draft"])

    def test_checks_launcher_and_rejects_a_second_target(self):
        self.dispatch(["--", "intent", "draft"], same_launcher=False)
        self.dispatch(["--", "intent", "draft", "--tar=another-project"])

@unittest.skipUnless(sys.platform == "win32", "requires the native Windows test root")
class RequestLocationTests(unittest.TestCase):
    def test_only_publishes_new_requests_outside_the_project(self):
        import os
        import tempfile

        with tempfile.TemporaryDirectory(dir=os.environ["COLVIA_NATIVE_TEST_ROOT"]) as work:
            base = Path(work)
            project = base / "Project with spaces"
            project.mkdir()
            outside = base / "outside"
            outside.mkdir()
            authority = outside / ".hrn"
            authority.mkdir()
            for location in (outside / ".." / project.name, project.with_name(project.name.swapcase()), authority):
                with self.subTest(location=location):
                    with self.assertRaises(ValueError):
                        manage.save_request(location / "request.json", {"step": 1}, project)
            destination = outside / "request.json"
            manage.save_request(destination, {"step": 1}, project)
            with self.assertRaises(FileExistsError):
                manage.save_request(destination, {"step": 2}, project)
            self.assertEqual(destination.read_bytes(), manage.canonical({"step": 1}))
            self.assertEqual(list(project.iterdir()), [])
            self.assertEqual(list(authority.iterdir()), [])
            self.assertEqual(list(outside.glob(".pending-*")), [])
