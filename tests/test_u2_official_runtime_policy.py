"""Focused binding tests; not live sandbox or product qualification."""
import importlib.util
import os
import sys
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "docs/development/verification/u2-host/official_runtime_policy.py"
SPEC = importlib.util.spec_from_file_location("official_policy", SOURCE)
policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(policy)


class OfficialRuntimePolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("COLVIA_TEST_ROOT"))
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.bindings = {}
        for name in sorted(policy.PARAMETERS):
            path = self.root / name
            if name == "CODEX_RULES_FILE":
                path = self.root / "CODEX_RULES_DIR" / "default.rules"
            if name == "SESSION":
                path = self.root / "RUNTIME" / "SESSION"
            if name in policy.DIRECTORIES:
                path.mkdir(mode=0o700)
            else:
                path.write_text("synthetic fixture\n")
            self.bindings[name] = str(path)
        Path(self.bindings["CODE_MODE_HOST"]).chmod(0o700)
        Path(self.bindings["BIN"]).chmod(0o700)
        # X_OK includes the outer sandbox policy; use its already-admitted interpreter.
        self.bindings["BIN"] = str(Path(sys.executable).resolve())
        self.guard = self.root / "protected"
        self.guard.mkdir(mode=0o700)
        (self.guard / "document").write_text("protected synthetic\n")

    def launch(self, **kwargs):
        return policy.prepare_launch(self.bindings, ["app-server", "--listen", "stdio://"], protected=[str(self.guard)], **kwargs)

    def test_rules_file_outside_directory_refused(self):
        other = self.root / "outside.rules"
        other.write_text("synthetic rule")
        self.bindings["CODEX_RULES_FILE"] = str(other)
        with self.assertRaisesRegex(policy.PolicyRefusal, "rules-file-parent"):
            self.launch()

    def test_rules_directory_is_protected_overlap(self):
        with self.assertRaisesRegex(policy.PolicyRefusal, "protected-overlap"):
            policy.prepare_launch(self.bindings, [], protected=[self.bindings["CODEX_RULES_DIR"]])

    def test_helper_without_execute_mode_refused(self):
        Path(self.bindings["CODE_MODE_HOST"]).chmod(0o600)
        with self.assertRaisesRegex(policy.PolicyRefusal, "helper-not-executable"):
            self.launch()

    def test_fixed_policy_and_argument_array(self):
        result = self.launch()
        self.assertEqual(result["policy_sha256"], policy.POLICY_SHA256)
        self.assertEqual(result["argv"][-4:], [self.bindings["BIN"], "app-server", "--listen", "stdio://"])
        self.assertEqual(result["argv"].count("-D"), len(policy.PARAMETERS))

    def test_missing_and_extra_parameters(self):
        original = dict(self.bindings)
        for name in policy.PARAMETERS:
            self.bindings = {k: v for k, v in original.items() if k != name}
            with self.assertRaisesRegex(policy.PolicyRefusal, "parameter-set"):
                self.launch()
        self.bindings = dict(original, EXTRA="/synthetic")
        with self.assertRaisesRegex(policy.PolicyRefusal, "parameter-set"):
            self.launch()

    def test_session_outside_runtime(self):
        self.bindings["SESSION"] = str(self.guard)
        with self.assertRaisesRegex(policy.PolicyRefusal, "session-containment"):
            self.launch()

    def test_session_cannot_equal_runtime(self):
        self.bindings["SESSION"] = self.bindings["RUNTIME"]
        with self.assertRaisesRegex(policy.PolicyRefusal, "session-containment"):
            self.launch()

    def test_protected_runtime_overlap(self):
        with self.assertRaisesRegex(policy.PolicyRefusal, "protected-overlap"):
            policy.prepare_launch(self.bindings, [], protected=[self.bindings["SESSION"]])

    def test_credential_inside_readable_root(self):
        credential = Path(self.bindings["PYROOT"]) / "credential"
        credential.write_text("synthetic credential")
        self.bindings["CODEX_AUTH"] = str(credential)
        with self.assertRaisesRegex(policy.PolicyRefusal, "credential-root-overlap"):
            self.launch()

    def test_symlink_parent_and_leaf(self):
        alias = self.root / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        self.bindings["CODEX_CONFIG"] = str(alias / "CODEX_CONFIG")
        with self.assertRaisesRegex(policy.PolicyRefusal, "path-alias"):
            self.launch()

    def test_hardlink_to_protected_file(self):
        Path(self.bindings["CODEX_AUTH"]).unlink()
        os.link(self.guard / "document", self.bindings["CODEX_AUTH"])
        with self.assertRaisesRegex(policy.PolicyRefusal, "protected-file-alias"):
            policy.prepare_launch(self.bindings, [], protected=[str(self.guard / "document")])

    def test_non_executable_binary(self):
        candidate = self.root / "BIN"
        candidate.chmod(0o600)
        self.bindings["BIN"] = str(candidate)
        with self.assertRaisesRegex(policy.PolicyRefusal, "binary-executable"):
            self.launch()

    def test_policy_drift(self):
        alternate = self.root / "policy.sb"
        alternate.write_bytes(policy.POLICY.read_bytes() + b"\n(allow default)\n")
        with self.assertRaisesRegex(policy.PolicyRefusal, "policy-drift"):
            self.launch(policy_path=alternate)

    def test_invalid_path_spelling_and_type(self):
        original = self.bindings["BIN"]
        for value in [original + "/../BIN", "relative", "", None, original + "\n"]:
            self.bindings["BIN"] = value
            with self.assertRaises(policy.PolicyRefusal):
                self.launch()

    def test_kind_missing_and_private_runtime(self):
        self.bindings["BIN"] = str(self.guard)
        with self.assertRaisesRegex(policy.PolicyRefusal, "path-kind"):
            self.launch()
        self.bindings["BIN"] = str(self.root / "missing")
        with self.assertRaisesRegex(policy.PolicyRefusal, "path-unavailable"):
            self.launch()
        self.bindings["BIN"] = str(self.root / "BIN")
        Path(self.bindings["SESSION"]).chmod(0o755)
        with self.assertRaisesRegex(policy.PolicyRefusal, "runtime-private"):
            self.launch()

    def test_closed_input_shapes_and_no_content_mutation(self):
        before = {p: p.read_bytes() for p in self.root.iterdir() if p.is_file()}
        with self.assertRaisesRegex(policy.PolicyRefusal, "protected-set"):
            policy.prepare_launch(self.bindings, [], protected=[])
        with self.assertRaisesRegex(policy.PolicyRefusal, "argument-array"):
            policy.prepare_launch(self.bindings, "app-server", protected=[str(self.guard)])
        self.launch()
        self.assertEqual(before, {p: p.read_bytes() for p in before})


if __name__ == "__main__":
    unittest.main()
