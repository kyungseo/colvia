"""Receiver decisions and refusal before OS registration; no notification is posted."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

@unittest.skipUnless(sys.platform == "darwin", "macOS native source")
class NativeReceiverTests(unittest.TestCase):
    def test_identity_selection_running_and_relocated_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            harness = root / "receiver.m"
            source = ROOT / "distribution/notification/WorkWindow.m"
            harness.write_text('#define main receiver_app_main\n#include "' + str(source) + '"\n#undef main\n' + r'''
int main(void) { @autoreleasepool {
    NSString *p = @"/test/bin/ColviaWork.app", *q = @"/other/bin/ColviaWork.app";
    if (fixtureIdentityMatches(@"org.colvia.work.notice", @"org.colvia.work.notice")) return 20;
    if (!fixtureIdentityMatches(@"org.colvia.work.notice.fixture.a", @"org.colvia.work.notice.fixture.a")) return 21;
    if (fixtureIdentityMatches(@"org.colvia.work.notice.fixture.a", @"org.colvia.work.notice.fixture.b")) return 22;
    if (!receiverVerdict(p,p,p,@[],YES)) return 10;
    if (!receiverVerdict(p,p,p,@[p],YES)) return 11;
    if (receiverVerdict(p,p,p,@[q],YES)) return 12;
    if (receiverVerdict(p,p,p,@[NSNull.null],YES)) return 13;
    if (receiverVerdict(p,p,q,@[],YES)) return 14;
    if (receiverVerdict(p,p,nil,@[],YES)) return 15;
    if (!receiverVerdict(p,p,nil,@[],NO)) return 16;
    if (receiverVerdict(nil,p,p,@[],YES)) return 17;
    if (receiverVerdict(p,nil,p,@[],YES)) return 18;
    for (NSString *other in @[@"/test/bin2/ColviaWork.app",@"/test/bin/x/ColviaWork.app",@"/test/bin/colviawork.app"])
        if (receiverVerdict(other,p,p,@[],YES)) return 19;
    return 0;
}}
''')
            flags = ["/usr/bin/xcrun", "clang", "-fobjc-arc", "-framework", "AppKit", "-framework", "UserNotifications", "-framework", "CoreServices"]
            for input_path, output in ((harness, root/"test"), (source, root/"app")):
                build = subprocess.run([*flags, str(input_path), "-o", str(output)], capture_output=True, timeout=45)
                self.assertEqual(build.returncode, 0, build.stderr.decode())
            self.assertEqual(subprocess.run([str(root/"test")], timeout=5).returncode, 0)
            for args in (("--check-receiver",), ("--authorize",), ("--post", "a"*32)):
                proc = subprocess.run([str(root/"app"), *args], env=dict(os.environ, HOME=str(root)), capture_output=True, timeout=10)
                self.assertEqual(proc.returncode, 3, proc.stderr)
            self.assertEqual(subprocess.run([str(root/"app"), "--post", "bad"], capture_output=True, timeout=5).returncode, 1)

class ReceiverPackagingTests(unittest.TestCase):
    def test_production_has_no_fixture_override_and_fixture_is_compile_time(self):
        spec = importlib.util.spec_from_file_location("macos_receiver_builder", ROOT/"distribution/macos.py")
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as tmp, patch.object(subprocess, "run") as run:
            root = Path(tmp)
            for name, fixture in (("production",None), ("fixture",root/"store")):
                mod.build_notice_app(ROOT, root/name, fixture_root=fixture)
                clang = run.call_args_list[-3].args[0]
                macros = [arg for arg in clang if arg.startswith("-DCOLVIA_FIXTURE_APP=")]
                self.assertEqual(len(macros), int(fixture is not None))
                if fixture:
                    self.assertIn(str(fixture/"bin/ColviaWork.app"), macros[0])
                    self.assertTrue(any(arg.startswith('-DCOLVIA_FIXTURE_ID="org.colvia.work.notice.fixture.') for arg in clang))
                else:
                    self.assertFalse(any(arg.startswith('-DCOLVIA_FIXTURE_ID=') for arg in clang))

    def test_fixture_path_rejected_before_build_output(self):
        spec = importlib.util.spec_from_file_location("macos_receiver_badpath", ROOT/"distribution/macos.py")
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as tmp, patch.object(subprocess, "run") as run:
            root=Path(tmp)
            for fixture in (Path("relative"),root/"bad\x01name"):
                with self.assertRaises(ValueError):mod.build_notice_app(ROOT,root/"output",fixture_root=fixture)
                self.assertFalse((root/"output").exists())
            run.assert_not_called()

@unittest.skipUnless(sys.platform == "darwin", "macOS account and manager paths")
class ManagerReceiverTests(unittest.TestCase):
    def test_post_refusal_and_timeout_are_unavailable(self):
        spec = importlib.util.spec_from_file_location("receiver_manager", ROOT/"distribution/manager.py")
        manager = importlib.util.module_from_spec(spec); spec.loader.exec_module(manager)
        manager.CONFIG = {"profiles":{"continuation-1":{"release":{"id":"test"}}},"notice_app":{}}
        with patch.object(manager,"validate_payload"), patch.object(manager,"notice_members",return_value={}), patch.object(manager,"notice_matches",return_value=True), patch("hv2ref.continuation.notification_detail",return_value="Review is available"), patch.object(manager.subprocess,"run") as run:
            run.return_value.returncode=3
            self.assertEqual(manager.notice_command(Path("/synthetic"),"notice-post","a"*32),3)
            run.side_effect=subprocess.TimeoutExpired("receiver",30)
            self.assertEqual(manager.notice_command(Path("/synthetic"),"notice-post","a"*32),65)

    def test_check_command_is_distinct_from_enable_and_handles_timeout(self):
        spec = importlib.util.spec_from_file_location("receiver_manager_check", ROOT/"distribution/manager.py")
        manager = importlib.util.module_from_spec(spec); spec.loader.exec_module(manager)
        manager.CONFIG = {"notice_app":{},"fixture_root":"/synthetic"}
        with patch.object(manager,"store_root",return_value=Path("/synthetic")), patch.object(manager,"runtime_path"), patch.object(manager,"verify_runtime"), patch.object(manager,"notice_members",return_value={}), patch.object(manager,"notice_matches",return_value=True), patch.object(manager.subprocess,"run") as run, patch.object(sys,"argv",["colvia-manage","notice-check"]):
            run.return_value.returncode=3
            self.assertEqual(manager.main(),3)
            self.assertEqual(run.call_args.args[0][-1],"--check-receiver")
            run.side_effect=subprocess.TimeoutExpired("receiver",35)
            self.assertEqual(manager.main(),65)

    def test_production_location_does_not_follow_overridden_home(self):
        from types import SimpleNamespace
        spec = importlib.util.spec_from_file_location("receiver_location", ROOT/"distribution/manager.py")
        manager = importlib.util.module_from_spec(spec); spec.loader.exec_module(manager)
        manager.CONFIG = {"fixture_root":None}
        with patch("pwd.getpwuid",return_value=SimpleNamespace(pw_dir="/synthetic-account")), patch.dict(os.environ,HOME="/other-account"):
            self.assertTrue(manager.notice_location_matches(Path("/synthetic-account/Library/Application Support/Colvia")))
            self.assertFalse(manager.notice_location_matches(Path("/other-account/Library/Application Support/Colvia")))
        with patch.object(manager.os,"geteuid",return_value=manager.os.getuid()+1):
            self.assertFalse(manager.notice_location_matches(Path("/synthetic-account/Library/Application Support/Colvia")))

    def test_native_refusal_is_one_attempt_and_inbox_fallback(self):
        from hv2ref import continuation
        with tempfile.TemporaryDirectory() as tmp:
            store=Path(tmp).resolve(); manager=store/"colvia-manage";manager.write_text("fixture")
            with patch.object(continuation,"_click_receiver",return_value=(store,manager)), patch.object(continuation,"record_notification",return_value="a"*32) as record, patch.object(subprocess,"run",return_value=subprocess.CompletedProcess([],3)) as run:
                self.assertEqual(continuation._notify_recorded(store,None,"key",1,"done",detail_required=True),"unavailable")
                record.assert_called_once();run.assert_called_once()
