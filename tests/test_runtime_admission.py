"""Admission doubles and actual installed interpreter observations.

Prerelease and free-threaded rejection use doubles, not those real builds."""
from contextlib import contextmanager
from collections import namedtuple
import json
from pathlib import Path
import subprocess
import sys
import types
import unittest
from unittest import mock

import test_productization_safety as helpers
from hv2ref.errors import ContractError
from hv2ref.jsonio import canonical_json_bytes

MODES = ("implementation-double", "version-double")
WRAPPER = '''import sys,types,collections,runpy
mode=sys.argv[1];launcher=sys.argv[2];sys.argv=sys.argv[2:]
if mode=="implementation-double":sys.implementation=types.SimpleNamespace(**{**vars(sys.implementation),"name":"pypy"})
if mode=="version-double":sys.version_info=collections.namedtuple("version_info","major minor micro releaselevel serial")(3,14,8,"final",0)
runpy.run_path(launcher,run_name="__main__")
'''

@contextmanager
def runtime_double(mode):
    if mode == "implementation-double":
        with mock.patch.object(sys,"implementation",types.SimpleNamespace(**{**vars(sys.implementation),"name":"pypy"})):yield
    else:
        version=namedtuple("version_info","major minor micro releaselevel serial")(3,14,8,"final",0)
        with mock.patch.object(sys,"version_info",version):yield

class RuntimeAdmissionTests(unittest.TestCase):
    def fixture(self):
        t=helpers.ActualWorkspaceInitTests();t.setUp();self.addCleanup(t.doCleanups);return t

    def installed(self,t,mode,args,value=None):
        return subprocess.run([sys.executable,"-I","-B","-c",WRAPPER,mode,str(t.target/"colvia"),*args],
                              input=canonical_json_bytes(value) if value is not None else None,
                              capture_output=True,cwd=t.target,timeout=45)

    def test_status_rejects_both_unsupported_identities_without_blocking_reads(self):
        t=self.fixture();t.apply_init(t.preview());before=helpers.exact_snapshot(t.target)
        for mode in MODES:
            with self.subTest(mode=mode):
                result=self.installed(t,mode,["status"]);self.assertEqual(16,result.returncode,result.stdout+result.stderr)
                value=json.loads(result.stdout);self.assertEqual("unsupported",value["classification"])
                self.assertFalse(value["runtime"]["supported"])
                if sys.platform != "win32":self.assertEqual("unsupported",value["runtime"]["admission_path"])
                self.assertEqual("pypy" if mode=="implementation-double" else "cpython",value["runtime"]["implementation"])
                if sys.platform == "win32":
                    # The Windows launcher refuses before importing product readers.
                    self.assertEqual({"classification", "code", "message", "runtime"}, set(value))
                    self.assertEqual("HV2-WORKSPACE-RUNTIME", value["code"])
                    self.assertEqual("OS/process/Python tuple is outside windows-2 policy", value["message"])
                else:
                    self.assertIn("CPython 3.14.6, 3.14.7 before mutation",value["next_action"])
                    self.assertIn("documentation_root",value)
                self.assertEqual(before,helpers.exact_snapshot(t.target))
        healthy=self.installed(t,"supported-control",["status"])
        self.assertEqual(0,healthy.returncode);self.assertTrue(json.loads(healthy.stdout)["runtime"]["supported"])

    def test_installed_record_entry_gate_precedes_input_and_preserves_truth(self):
        t=self.fixture();t.apply_init(t.preview());before=helpers.exact_snapshot(t.target)
        # Draft is a valid fresh mutation, also observed in the before probe. Other
        # routes deliberately use empty canonical input to verify gate-before-parse.
        commands=[(["intent","draft"],t.draft()),(["intent","prepare"],{}),(["intent","apply","--confirm","unused"],{}),
                  (["work","publish"],{}),(["work","prepare"],{}),(["work","apply","--confirm","unused"],{})]
        for mode in MODES:
            for args,value in commands:
                with self.subTest(mode=mode,command=args[:2]):
                    result=self.installed(t,mode,args,value);self.assertEqual(65,result.returncode,result.stdout+result.stderr)
                    error=json.loads(result.stdout);self.assertEqual("HV2-WORKSPACE-RUNTIME",error["code"])
                    if sys.platform == "win32":
                        self.assertEqual("OS/process/Python tuple is outside windows-2 policy", error["message"])
                    else:
                        self.assertIn("CPython 3.14.6, 3.14.7",error["message"])
                    self.assertEqual(before,helpers.exact_snapshot(t.target))
        success=self.installed(t,"supported-control",["intent","draft"],t.draft())
        self.assertEqual(0,success.returncode,success.stdout+success.stderr)
        self.assertTrue((t.target/".hrn/intents/intent-a/drafts/draft-a.json").is_file())

    def test_source_lifecycle_apply_has_no_writes_under_unsupported_runtime(self):
        from hv2ref.product import workspace_init_apply,workspace_switch_apply,workspace_repair_apply,workspace_detach_apply
        for mode in MODES:
            for action in ("init","update","rollback","repair","detach"):
                with self.subTest(mode=mode,action=action):
                    t=self.fixture();init=t.preview()
                    if action=="init":invoke=lambda:workspace_init_apply(t.source,t.target,init["request"],confirm_token=init["confirm_token"])
                    else:
                        t.apply_init(init)
                        if action in ("update","rollback"):
                            t.candidate=t.switch_candidate();up=t.switch_preview()
                            if action=="update":invoke=lambda:workspace_switch_apply(t.target,up["request"],confirm_token=up["confirm_token"],source=t.candidate)
                            else:
                                t.switch_apply(up);down=t.switch_preview("rollback",operation="rollback-a")
                                invoke=lambda:workspace_switch_apply(t.target,down["request"],confirm_token=down["confirm_token"])
                        elif action=="repair":
                            t.repair_damage();plan=t.repair_preview()
                            invoke=lambda:workspace_repair_apply(t.source,t.target,plan["request"],confirm_token=plan["confirm_token"])
                        else:
                            plan=t.detach_preview();invoke=lambda:workspace_detach_apply(t.target,plan["request"],confirm_token=plan["confirm_token"])
                    before=helpers.exact_snapshot(t.base)
                    with runtime_double(mode),self.assertRaises(ContractError) as error:invoke()
                    self.assertEqual("HV2-WORKSPACE-RUNTIME",error.exception.code)
                    self.assertEqual(before,helpers.exact_snapshot(t.base))

    def test_bootstrap_and_shared_guard_refuse_before_creating_files(self):
        from hv2ref.workspace import bootstrap_root,writer_guard
        for mode in MODES:
            with self.subTest(mode=mode):
                t=self.fixture();preview=t.preview();before=helpers.exact_snapshot(t.target)
                with runtime_double(mode),self.assertRaises(ContractError) as error:
                    bootstrap_root(t.target,preview["request"]["plan"],preview["request"]["format"])
                self.assertEqual("HV2-WORKSPACE-RUNTIME",error.exception.code);self.assertEqual(before,helpers.exact_snapshot(t.target))
                t.apply_init(preview);before=helpers.exact_snapshot(t.target)
                with runtime_double(mode),self.assertRaises(ContractError) as error:
                    with writer_guard(t.target):(t.target/"sentinel").write_bytes(b"must not write")
                self.assertEqual("HV2-WORKSPACE-RUNTIME",error.exception.code);self.assertEqual(before,helpers.exact_snapshot(t.target))


    def test_explicit_allowlist_rejects_future_prerelease_and_free_threaded(self):
        import hv2ref.workspace as workspace
        version_type=namedtuple("version_info","major minor micro releaselevel serial")
        self.assertEqual(((3,14,6),(3,14,7)), workspace.SUPPORTED_PYTHON_VERSIONS)
        cases=[((3,14,6,"final",0),0,True),((3,14,7,"final",0),0,True),
               ((3,14,5,"final",0),0,False),((3,14,8,"final",0),0,False),
               ((3,15,0,"final",0),0,False),((3,14,7,"candidate",1),0,False),
               ((3,14,6,"final",0),1,False),((3,14,7,"final",0),1,False)]
        for version,free_threaded,expected in cases:
            with self.subTest(version=version,free_threaded=free_threaded):
                with mock.patch.object(sys,"version_info",version_type(*version)), mock.patch.object(workspace.sysconfig,"get_config_var",return_value=free_threaded):
                    window = "windows-2" if sys.platform == "win32" else None
                    self.assertIs(expected,workspace.runtime_supported(window))
                    if sys.platform == "win32":
                        self.assertFalse(workspace.runtime_supported())

    def test_runtime_capability_declaration_matches_admission(self):
        from hv2ref.workspace import SUPPORTED_PYTHON_STRINGS
        declaration=json.loads((Path(__file__).resolve().parents[1]/"PRODUCT-CAPABILITIES.json").read_text())["runtime"]
        self.assertEqual(list(SUPPORTED_PYTHON_STRINGS),declaration["supported_versions"])
        self.assertEqual("final",declaration["required_releaselevel"])
        self.assertFalse(declaration["free_threaded_supported"])
        from hv2ref.workspace import MANAGED_MACOS_RUNTIME_DECLARATION
        self.assertEqual(MANAGED_MACOS_RUNTIME_DECLARATION,declaration["managed_macos_candidate"])
        self.assertEqual("legacy-version-allowlist",declaration["supported_versions_scope"])

    def test_actual_installed_child_matches_parent_qualified_version(self):
        t=self.fixture();t.apply_init(t.preview())
        value=json.loads(t.installed(["status"]).stdout)["runtime"]
        self.assertEqual(".".join(map(str,sys.version_info[:3])),value["python"])
        if sys.platform == "darwin" and sys.version_info[:3] == (3, 14, 10):
            from hv2ref.workspace import managed_macos_runtime_supported
            self.assertTrue(managed_macos_runtime_supported())
        else:
            self.assertIn(value["python"],["3.14.6","3.14.7"])
        self.assertTrue(value["supported"])
        self.assertEqual("legacy-version-allowlist",value["supported_versions_scope"])
        expected_path = "windows-window-policy" if sys.platform == "win32" else "managed-macos-exact-tree" if sys.platform == "darwin" and sys.version_info[:3] == (3,14,10) else "legacy-version"
        self.assertEqual(expected_path,value["admission_path"])
        self.assertEqual("3.14.10",value["managed_macos_candidate"]["python"])
        self.assertEqual(["3.14.6","3.14.7"],value["supported_versions"])
        self.assertEqual("3.14.6",value["supported_baseline"])
        self.assertEqual("final",value["required_releaselevel"])
        self.assertFalse(value["free_threaded_supported"])

    def test_admission_path_describes_each_gate_without_rechecking(self):
        from hv2ref import workspace
        with mock.patch.object(workspace, "managed_macos_runtime_supported", side_effect=AssertionError("second verification")):
            self.assertEqual("unsupported",workspace.runtime_admission_path("windows-2",False))
            self.assertEqual("windows-window-policy",workspace.runtime_admission_path("windows-2",True))
            with mock.patch.object(sys,"platform","darwin"), mock.patch.object(sys,"version_info",(3,14,10)):
                self.assertEqual("managed-macos-exact-tree",workspace.runtime_admission_path(None,True))
                self.assertEqual("unsupported",workspace.runtime_admission_path(None,False))
            with mock.patch.object(sys,"version_info",(3,14,7)):
                self.assertEqual("legacy-version",workspace.runtime_admission_path(None,True))
