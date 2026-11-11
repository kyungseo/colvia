"""Bundle publication in an isolated directory; no registration or app launch."""
import base64
import plistlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

@unittest.skipUnless(sys.platform == "darwin", "macOS atomic bundle publication")
class NoticeBundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.store = self.root / "store"
        (self.store / "bin").mkdir(parents=True, mode=0o700)
        self.stage = self.root / "stage"
        self.stage.mkdir(mode=0o700)
        self.m = module("bundle_manager", "distribution/manager.py")
        self.legacy = {"Contents/Info.plist": b"legacy plist",
                       "Contents/MacOS/ColviaWork": b"legacy binary",
                       "Contents/_CodeSignature/CodeResources": b"legacy signature"}
        self.current = dict(self.legacy, **{"Contents/Resources/Colvia.icns": b"icon"})
        self.m.CONFIG = {"notice_app": self.encode(self.current)}
        self.app = self.store / "bin/ColviaWork.app"

    def encode(self, files):
        return {k: base64.b64encode(v).decode("ascii") for k, v in files.items()}

    def publish_legacy(self):
        self.app.mkdir(mode=0o700)
        for name, raw in self.legacy.items():
            dest = self.app / name
            dest.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            dest.write_bytes(raw)
            dest.chmod(0o500 if name == self.m.NOTICE_BINARY else 0o400)
        return "CONFIG: dict = " + repr({"notice_app": self.encode(self.legacy)})

    def test_current_publication_and_repeat(self):
        self.m.install_notice_app(self.store, self.stage, None)
        self.assertTrue(self.m.notice_matches(self.app, self.current))
        self.m.install_notice_app(self.store, self.stage, None)
        self.assertFalse((self.stage / "ColviaWork.app").exists())

    def test_legacy_upgrade_preserves_old_bundle_at_stage(self):
        old = self.publish_legacy()
        self.m.install_notice_app(self.store, self.stage, old)
        self.assertTrue(self.m.notice_matches(self.app, self.current))
        self.assertTrue(self.m.notice_matches(self.stage / "ColviaWork.app", self.legacy))

    def test_foreign_resource_refuses_and_preserves(self):
        old = self.publish_legacy()
        resource = self.app / "Contents/Resources"
        resource.mkdir(mode=0o700)
        foreign = resource / "foreign"
        foreign.write_bytes(b"preserve")
        with self.assertRaises(ValueError): self.m.install_notice_app(self.store, self.stage, old)
        self.assertEqual(foreign.read_bytes(), b"preserve")
        self.assertFalse((self.stage / "ColviaWork.app").exists())

    def test_missing_current_icon_and_extra_members_refused(self):
        for files in (self.legacy, dict(self.current, **{"Contents/foreign": b"foreign"})):
            with self.subTest(files=list(files)), self.assertRaises(ValueError):
                self.m.notice_members(self.encode(files))

    def test_extra_empty_directory_refused(self):
        self.m.install_notice_app(self.store, self.stage, None)
        (self.app / "Contents/empty").mkdir(mode=0o700)
        self.assertFalse(self.m.notice_matches(self.app, self.current))

    def test_real_signed_fixture_builder_to_manager(self):
        builder = module("bundle_builder", "distribution/macos.py")
        fixture = self.root / 'fixture"with\\slash'
        encoded = builder.build_notice_app(ROOT, self.root / "build", fixture_root=fixture, build_version="2")
        self.assertIn(str(fixture / "bin/ColviaWork.app").encode("utf-8"),
                      base64.b64decode(encoded[self.m.NOTICE_BINARY]))
        self.m.CONFIG = {"notice_app": encoded}
        self.m.install_notice_app(self.store, self.stage, None)
        self.assertTrue(self.m.notice_matches(self.app, self.m.notice_members(encoded)))
        result = subprocess.run(["/usr/bin/codesign", "--verify", "--strict", str(self.app)], capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_fixture_identity_macro_required(self):
        result = subprocess.run(["/usr/bin/xcrun", "clang", "-fsyntax-only", "-fobjc-arc",
            '-DCOLVIA_FIXTURE_APP="/synthetic/app"',
            str(ROOT / "distribution/notification/WorkWindow.m")], capture_output=True, timeout=45)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"COLVIA_FIXTURE_ID", result.stderr)

    def test_production_builder_matches_manager_contract(self):
        builder = module("production_bundle_builder", "distribution/macos.py")
        encoded = builder.build_notice_app(ROOT, self.root / "production", fixture_root=None, build_version="2")
        self.assertEqual(set(encoded), self.m.NOTICE_MEMBERS)
        self.m.CONFIG = {"notice_app": encoded}
        self.m.install_notice_app(self.store, self.stage, None)
        self.assertTrue(self.m.notice_matches(self.app, self.m.notice_members(encoded)))

    def test_builder_refuses_missing_and_foreign_members(self):
        builder = module("invalid_bundle_builder", "distribution/macos.py")
        for case in ("missing", "foreign"):
            with self.subTest(case=case):
                def build(command, **kwargs):
                    if command[:2] == ["/usr/bin/xcrun", "clang"]:
                        Path(command[-1]).write_bytes(b"executable")
                    elif command[:2] == ["/usr/bin/codesign", "--force"]:
                        app = Path(command[-1])
                        signature = app / "Contents/_CodeSignature/CodeResources"
                        signature.parent.mkdir()
                        signature.write_bytes(b"signature")
                        if case == "missing": (app / "Contents/Resources/Colvia.icns").unlink()
                        else: (app / "Contents/Resources/foreign").write_bytes(b"unexpected")
                with patch.object(subprocess, "run", side_effect=build), self.assertRaises(ValueError):
                    builder.build_notice_app(ROOT, self.root / case, fixture_root=None, build_version="2")

    def test_build_version_required_and_invalid_before_output(self):
        builder = module("version_validation", "distribution/macos.py")
        for value in (None, 2, True, "", "0", "01", "+1", " 1", "1\n", "1.0", "10000", "²", "١"):
            with self.subTest(value=value):
                target = self.root / "invalid"
                with self.assertRaises(ValueError):
                    builder.build_notice_app(ROOT, target, fixture_root=None, build_version=value)
                with self.assertRaises(ValueError):
                    builder.prepare(ROOT, self.root / "absent-supply", target,
                                    version="candidate", origin="https://example.invalid",
                                    notice_build_version=value)
                self.assertFalse(target.exists())
        with self.assertRaises(TypeError):
            builder.build_notice_app(ROOT, self.root / "missing", fixture_root=None)
        with self.assertRaises(TypeError):
            builder.prepare(ROOT, self.root / "absent-supply", self.root / "missing",
                            version="candidate", origin="https://example.invalid")
        self.assertFalse((self.root / "missing").exists())

    def test_version_upgrade_changes_only_plist_and_signature(self):
        builder = module("version_upgrade", "distribution/macos.py")
        actual_run = subprocess.run
        unsigned = []
        def capture_compile(command, **kwargs):
            result = actual_run(command, **kwargs)
            if command[:2] == ["/usr/bin/xcrun", "clang"]:
                binary = Path(command[command.index("-o") + 1]).read_bytes()
                self.assertEqual(binary[:4], b"\xcf\xfa\xed\xfe")
                unsigned.append(binary)
            return result
        with patch.object(subprocess, "run", side_effect=capture_compile):
            one = builder.build_notice_app(ROOT, self.root / "v1", fixture_root=None, build_version="1")
            two = builder.build_notice_app(ROOT, self.root / "v2", fixture_root=None, build_version="2")
        self.assertEqual(len(unsigned), 2)
        self.assertEqual(unsigned[0], unsigned[1])
        a, b = (plistlib.loads(base64.b64decode(x["Contents/Info.plist"])) for x in (one, two))
        self.assertEqual(a.pop("CFBundleVersion"), "1")
        self.assertEqual(b.pop("CFBundleVersion"), "2")
        self.assertEqual(a, b)
        self.assertEqual(set(one), self.m.NOTICE_MEMBERS)
        self.assertEqual(set(two), self.m.NOTICE_MEMBERS)
        self.assertEqual(one["Contents/Resources/Colvia.icns"], two["Contents/Resources/Colvia.icns"])
        # codesign binds Info.plist inside the Mach-O signature. CodeResources need not change.
        self.assertNotEqual(one["Contents/MacOS/ColviaWork"], two["Contents/MacOS/ColviaWork"])
        self.m.CONFIG = {"notice_app": one}
        self.m.install_notice_app(self.store, self.stage, None)
        old = "CONFIG: dict = " + repr(self.m.CONFIG)
        next_stage = self.root / "next-stage"
        next_stage.mkdir()
        self.m.CONFIG = {"notice_app": two}
        self.m.install_notice_app(self.store, next_stage, old)
        self.assertTrue(self.m.notice_matches(self.app, self.m.notice_members(two)))
        self.assertTrue(self.m.notice_matches(next_stage / "ColviaWork.app", self.m.notice_members(one)))
        for app in (self.app, next_stage / "ColviaWork.app"):
            self.assertEqual(actual_run(["/usr/bin/codesign", "--verify", "--strict", str(app)],
                                       capture_output=True, timeout=30).returncode, 0)
