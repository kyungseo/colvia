"""Read-only local readiness, bounded input and unchanged command consumers."""
import argparse
import builtins
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack, redirect_stdout, redirect_stderr
from unittest import mock
from hv2ref import cli, official_entry as entry, official_state as state
from hv2ref.errors import ContractError
from hv2ref.jsonio import canonical_json_bytes

SOURCE = Path(__file__).resolve().parents[1]


class RuntimeDiagnosisTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.home = self.root / "home"; (self.home / ".codex/rules").mkdir(parents=True)
        self.paths = {
            "BIN": self.root / "codex", "CODE_MODE_HOST": self.root / "codex-code-mode-host",
            "CODEX_CONFIG": self.home / ".codex/config.toml",
            "CODEX_AUTH": self.home / ".codex/auth.json",
            "INSTALLATION_ID": self.home / ".codex/installation_id",
            "CODEX_RULES_DIR": self.home / ".codex/rules",
            "CODEX_RULES_FILE": self.home / ".codex/rules/default.rules",
            "GLOBAL_INSTRUCTIONS": self.root / "instructions.md"}
        for key, p in self.paths.items():
            if key != "CODEX_RULES_DIR": p.write_bytes(b"" if key == "CODEX_CONFIG" else key.encode())
        self.value = {"paths": {k: str(v) for k, v in self.paths.items()},
                      "sha256": {k: state.digest(self.paths[k].read_bytes()) for k in entry.PINNED_INPUTS}}
        self.input = self.root / "runtime.json"; self.save(self.value)
        stack = self.enterContext(ExitStack())
        stack.enter_context(mock.patch.object(Path, "home", return_value=self.home))
        stack.enter_context(mock.patch.object(entry, "CLI_SHA256", self.value["sha256"]["BIN"]))
        stack.enter_context(mock.patch.object(entry, "HELPER_SHA256", self.value["sha256"]["CODE_MODE_HOST"]))
        stack.enter_context(mock.patch.dict(os.environ, {}, clear=True))

    def save(self, value):
        self.input.write_bytes(canonical_json_bytes(value))

    def check(self, reason, value=None):
        if value is not None: self.save(value)
        result = entry.diagnose_runtime_input(self.input)
        self.assertEqual("failed", result["local_check"])
        self.assertEqual(reason, result["reason"])
        self.assertNotIn(str(self.root), json.dumps(result))
        self.assertNotIn("SECRET_SENTINEL", json.dumps(result))
        return result

    def test_success_reads_no_credential_contents_or_external_service(self):
        real = Path.read_bytes
        protected = {self.paths["CODEX_AUTH"], self.paths["INSTALLATION_ID"]}
        identities = {(p.stat().st_dev, p.stat().st_ino) for p in protected}
        opened = []
        def watch(fn):
            def call(path, *args, **kwargs):
                if not isinstance(path, int):
                    candidate = Path(path)
                    self.assertNotIn(candidate, protected)
                    try: info = candidate.stat()
                    except FileNotFoundError: pass
                    else: self.assertNotIn((info.st_dev, info.st_ino), identities)
                    opened.append(str(candidate))
                return fn(path, *args, **kwargs)
            return call
        def read(p):
            if p in protected: self.fail("credential content read")
            return real(p)
        with mock.patch.object(Path, "read_bytes", read), \
             mock.patch.object(os, "open", watch(os.open)), \
             mock.patch.object(builtins, "open", watch(builtins.open)), \
             mock.patch.object(io, "open", watch(io.open)), \
             mock.patch.object(subprocess, "Popen", side_effect=AssertionError("process")), \
             mock.patch.object(socket, "socket", side_effect=AssertionError("socket")):
            result = entry.diagnose_runtime_input(self.input)
        self.assertIn(str(self.input), opened)
        self.assertIn(str(self.paths["CODEX_CONFIG"]), opened)
        self.assertEqual("passed", result["local_check"])
        self.assertNotIn("paths", result); self.assertNotIn(str(self.root), json.dumps(result))

    def test_location_and_value_contracts(self):
        changes = [
            ("CODEX_AUTH", self.root / "other-auth", "input-location"),
            ("CODEX_RULES_FILE", self.root / "other-rules", "input-location"),
            ("CODE_MODE_HOST", self.root / "other-helper", "input-location"),
        ]
        for key, path, reason in changes:
            with self.subTest(key=key):
                path.write_bytes(b"fixture")
                v = copy.deepcopy(self.value); v["paths"][key] = str(path)
                self.check(reason, v)
        for field in ("paths", "sha256"):
            for bad in (None, [], 1, False):
                with self.subTest(field=field, bad=bad):
                    v = copy.deepcopy(self.value);v[field]["BIN"] = bad
                    self.check("input-invalid", v)

    def test_pins_config_and_environment_refusals(self):
        v = copy.deepcopy(self.value);v["sha256"]["BIN"] = "0"*64
        self.check("unqualified-cli-helper", v)
        self.save(self.value);self.paths["GLOBAL_INSTRUCTIONS"].write_bytes(b"changed")
        self.check("input-drift")
        self.paths["GLOBAL_INSTRUCTIONS"].write_bytes(b"GLOBAL_INSTRUCTIONS")
        for config, reason in ((b'model_provider = "custom"\n', "config-not-admitted"),
                               (b'instructions = "SECRET_SENTINEL"\n', "config-not-admitted"),
                               (b'[SECRET_SENTINEL', "config-invalid"), (b'\xff', "config-invalid")):
            self.paths["CODEX_CONFIG"].write_bytes(config)
            v=copy.deepcopy(self.value);v["sha256"]["CODEX_CONFIG"]=state.digest(config)
            self.check(reason,v)
        self.paths["CODEX_CONFIG"].write_bytes(b"");self.save(self.value)
        with mock.patch.dict(os.environ, {"CODEX_HOME":"SECRET_SENTINEL"}):
            self.check("environment-not-admitted")

    def test_input_file_rejects_duplicate_deep_large_link_and_fifo(self):
        for raw in (b'{"paths":{},"paths":{},"sha256":{}}\n', b'['*140+b'0'+b']'*140, b' '*65537):
            self.input.write_bytes(raw);self.check("input-invalid")
        self.input.unlink();self.input.symlink_to(self.paths["CODEX_CONFIG"])
        self.check("input-location")
        self.input.unlink();os.mkfifo(self.input)
        with mock.patch.object(os,"open",side_effect=AssertionError("FIFO opened")):
            self.check("input-location")

    def test_credentials_cannot_be_input_or_pinned_content(self):
        with mock.patch.object(os, "open", side_effect=AssertionError("credential opened")):
            r=entry.diagnose_runtime_input(self.paths["CODEX_AUTH"])
        self.assertEqual("credential-input",r["reason"])
        for key in ("GLOBAL_INSTRUCTIONS","CODEX_RULES_FILE"):
            v=copy.deepcopy(self.value);v["paths"][key]=str(self.paths["CODEX_AUTH"])
            self.check("credential-input",v)
        alias=self.root/"hard-auth";os.link(self.paths["CODEX_AUTH"],alias)
        v=copy.deepcopy(self.value);v["paths"]["GLOBAL_INSTRUCTIONS"]=str(alias)
        self.check("credential-input",v)

    def test_exception_details_do_not_escape(self):
        exceptions = [PermissionError("SECRET_SENTINEL"), ValueError("SECRET_SENTINEL"),
                      TypeError("SECRET_SENTINEL"), RuntimeError("SECRET_SENTINEL"),
                      MemoryError("SECRET_SENTINEL"), RecursionError("SECRET_SENTINEL"),
                      AttributeError("SECRET_SENTINEL"), IndexError("SECRET_SENTINEL"),
                      ContractError("unknown","SECRET_SENTINEL")]
        for error in exceptions:
            with self.subTest(error=type(error).__name__), mock.patch.object(entry,"runtime_input",side_effect=error), redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
                result=entry.diagnose_runtime_input(self.input)
                self.assertEqual("failed",result["local_check"])
                self.assertNotIn("SECRET_SENTINEL",json.dumps(result)+out.getvalue()+err.getvalue())


    def test_nonobject_noncanonical_unicode_and_surrogate_input(self):
        for field in ("paths", "sha256"):
            for value in (None, [], "SECRET_SENTINEL", 1):
                v=copy.deepcopy(self.value);v[field]=value
                self.check("input-invalid",v)
        value=copy.deepcopy(self.value);value["paths"]["GLOBAL_INSTRUCTIONS"]="\ud800"
        cases = (
            (json.dumps(self.value).encode()+b"\n", "HV2-JSON-NONCANONICAL"),
            (b"\xff\n", "HV2-JSON-UTF8"),
            ((json.dumps(value,ensure_ascii=True,sort_keys=True,indent=2)+"\n").encode(),
             "HV2-JSON-EMISSION"),
        )
        for raw, code in cases:
            with self.subTest(code=code), mock.patch.object(entry, "runtime_input") as runtime:
                self.input.write_bytes(raw)
                with self.assertRaises(ContractError) as caught:
                    entry._diagnostic_input(self.input)
                self.assertEqual(code, caught.exception.code)
                self.check("input-invalid")
                runtime.assert_not_called()

    def test_exact_size_missing_and_changed_input(self):
        from hv2ref import jsonio
        self.input.write_bytes(b"x"*65536)
        with mock.patch.object(jsonio,"decode_json_bytes",return_value=self.value) as decode:
            self.assertEqual("passed",entry.diagnose_runtime_input(self.input)["local_check"])
            self.assertEqual(65536,len(decode.call_args.args[0]))
        self.input.write_bytes(b"x"*65537)
        with mock.patch.object(jsonio,"decode_json_bytes") as decode:
            self.check("input-invalid")
        decode.assert_not_called()
        self.input.unlink();self.check("input-location")
        self.save(self.value)
        before=self.input.stat()
        from types import SimpleNamespace
        changed=SimpleNamespace(st_dev=before.st_dev,st_ino=before.st_ino,st_size=before.st_size,st_mtime_ns=before.st_mtime_ns+1)
        with mock.patch.object(os,"fstat",side_effect=[before,changed]):
            self.check("input-changed")

    def test_custom_home_refuses_before_opening_any_input(self):
        with mock.patch.dict(os.environ,{"CODEX_HOME":str(self.root/"other-home")}),mock.patch.object(os,"open",side_effect=AssertionError("input opened")):
            self.check("environment-not-admitted")


class DoctorConsumerTests(unittest.TestCase):
    def status(self, profile="continuation-1", classification="pass"):
        return {"classification":classification,"product":{"inventory":{"inventory_id":profile}}}

    def test_default_output_and_exit_codes_remain_workspace_results(self):
        for installed in (None,Path("/fixture")):
            for command in ("doctor","status"):
                for classification,code in (("pass",0),("degraded",10),("partial",14),("unsupported",16)):
                    value=self.status(classification=classification)
                    with self.subTest(installed=installed,command=command,state=classification), \
                         mock.patch("hv2ref.product.workspace_status",return_value=value), \
                         mock.patch.object(sys,"argv",["colvia",command]), redirect_stdout(io.StringIO()) as out:
                        self.assertEqual(code,cli.main(installed))
                        self.assertEqual(json.dumps(value,allow_nan=False,ensure_ascii=False,indent=2,sort_keys=True)+"\n",out.getvalue())

    def test_status_rejects_runtime_input(self):
        for parser in (cli.parser(),cli.workspace_parser(Path("/fixture"))):
            with redirect_stderr(io.StringIO()),self.assertRaises(SystemExit) as err:
                parser.parse_args(["status","--runtime-input","runtime.json"])
            self.assertEqual(2,err.exception.code)

    def test_nonofficial_and_partial_do_not_import_or_read_input(self):
        real=builtins.__import__
        def blocked(name,*a,**kw):
            if "official_" in name: self.fail("official import in unavailable diagnosis")
            return real(name,*a,**kw)
        for profile,classification in (("continuation-1","pass"),("official-execution-2","partial")):
            with mock.patch("hv2ref.product.workspace_status",return_value=self.status(profile,classification)),mock.patch("builtins.__import__",side_effect=blocked):
                args=cli.parser().parse_args(["doctor","--runtime-input","unreadable"])
                result=cli.run(args)
            self.assertEqual("unavailable",result["official_runtime_input"]["local_check"])

    def test_source_and_installed_observation_keep_workspace_exit(self):
        for installed in (None,Path("/fixture")):
            with mock.patch("hv2ref.product.workspace_status",return_value=self.status("official-execution-2")), \
                 mock.patch.object(sys,"platform","darwin"),mock.patch.object(entry,"diagnose_runtime_input",return_value={"local_check":"failed","reason":"input-drift"}) as observe, \
                 mock.patch.object(sys,"argv",["colvia","doctor","--runtime-input","runtime.json"]),redirect_stdout(io.StringIO()) as out:
                self.assertEqual(0,cli.main(installed))
                got=json.loads(out.getvalue())
                self.assertEqual("failed",got["official_runtime_input"]["local_check"])
                self.assertEqual("unobserved",got["official_runtime_input"]["account_connection"])
                observe.assert_called_once_with(Path("runtime.json"))

    def test_workspace_failure_does_not_read_runtime_input(self):
        with mock.patch("hv2ref.product.workspace_status",side_effect=ContractError("fixture","preserve")),mock.patch.object(entry,"diagnose_runtime_input") as observe:
            with self.assertRaises(ContractError):cli.run(cli.parser().parse_args(["doctor","--runtime-input","runtime.json"]))
        observe.assert_not_called()


    def test_unavailable_profile_shapes_platform_and_import_reason(self):
        for extra in ({}, {"product":None}, {"product":[]}, {"product":{"inventory":None}}, {"product":{"inventory":[]}}):
            with mock.patch("hv2ref.product.workspace_status",return_value={"classification":"pass",**extra}),mock.patch.object(entry,"diagnose_runtime_input") as observe:
                result=cli.run(cli.parser().parse_args(["doctor","--runtime-input","unused"]))
                self.assertEqual("unavailable",result["official_runtime_input"]["local_check"])
                self.assertEqual("official-profile-required",result["official_runtime_input"]["reason"])
                observe.assert_not_called()
        with mock.patch("hv2ref.product.workspace_status",return_value=self.status("official-execution-2")),mock.patch.object(sys,"platform","unsupported"):
            result=cli.run(cli.parser().parse_args(["doctor","--runtime-input","unused"]))
        self.assertEqual("platform-unavailable",result["official_runtime_input"]["reason"])
        real=builtins.__import__
        def missing(name,*a,**kw):
            if name=="official_entry":raise ImportError("SECRET_SENTINEL")
            return real(name,*a,**kw)
        with mock.patch("hv2ref.product.workspace_status",return_value=self.status("official-execution-2")),mock.patch.object(sys,"platform","darwin"),mock.patch("builtins.__import__",side_effect=missing):
            result=cli.run(cli.parser().parse_args(["doctor","--runtime-input","unused"]))
        self.assertEqual("official-install-inconsistent",result["official_runtime_input"]["reason"])
        self.assertNotIn("SECRET_SENTINEL",json.dumps(result))


class ManagerDiagnosisTests(unittest.TestCase):
    def setUp(self):
        spec=importlib.util.spec_from_file_location("diagnosis_manager",SOURCE/"distribution/manager.py")
        self.manager=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.manager)
        self.manager.CONFIG={"runtime_id":"fixture","profiles":{"continuation-1":{"release":{"id":"fixture"},"runtime_input_diagnostic":True}}}
        self.args=argparse.Namespace(command="doctor",target=Path("/fixture/project"),profile="continuation-1",apply=False,save=None,backup=None,to=None,input=None,confirm=None,recover=False,json=True,details=False,runtime_input=Path("runtime.json"))

    def test_forwarding_support_marker_and_human_summary(self):
        for supported in (True,False):
            for human in (True,False):
                self.manager.CONFIG["profiles"]["continuation-1"]["runtime_input_diagnostic"]=supported
                self.args.json=not human
                value={"classification":"pass","official_runtime_input":{"local_check":"failed","message":"입력이 바뀌었습니다.","next_action":"출처를 확인하세요."}}
                response=subprocess.CompletedProcess([],0,json.dumps(value).encode(),b"")
                with mock.patch.object(self.manager,"validate_payload"),mock.patch.object(self.manager,"run_lifecycle",return_value=response) as run,redirect_stdout(io.StringIO()) as out:
                    self.assertEqual(0,self.manager.lifecycle(self.args,Path("/fixture/store")))
                argv=run.call_args.args[0]
                self.assertEqual(supported,"--runtime-input" in argv)
                if supported:self.assertEqual(str(Path("runtime.json").absolute()),argv[argv.index("--runtime-input")+1])
                if human:
                    self.assertEqual(1,out.getvalue().count("실행 입력:"))
                    self.assertIn("프로젝트 상태:",out.getvalue())
                    self.assertIn("계정·모델 연결: 미확인",out.getvalue())
                    self.assertEqual(supported,"진단 환경:" in out.getvalue())
                else:self.assertIn("official_runtime_input",json.loads(out.getvalue()))

    def test_status_option_refused_before_integrity_checks(self):
        with mock.patch.object(sys,"argv",["manager","status","--runtime-input","runtime.json"]),mock.patch.object(self.manager,"verify_runtime") as verify,redirect_stderr(io.StringIO()),self.assertRaises(SystemExit) as err:
            self.manager.main()
        self.assertEqual(2,err.exception.code);verify.assert_not_called()

    def test_manager_environment_is_explicitly_scoped(self):
        with mock.patch.object(self.manager,"store_root",return_value=Path("/fixture/store")),mock.patch.dict(os.environ,{"OPENAI_API_KEY":"SECRET_SENTINEL","CODEX_HOME":"SECRET_SENTINEL"}):
            value=self.manager.clean_environment()
        self.assertNotIn("OPENAI_API_KEY",value);self.assertNotIn("CODEX_HOME",value)
        self.assertNotIn("SECRET_SENTINEL",json.dumps(value))


    def test_missing_diagnostic_response_and_unsupported_reason(self):
        for supported in (True,False):
            self.manager.CONFIG["profiles"]["continuation-1"]["runtime_input_diagnostic"]=supported
            for extra in ({}, {"official_runtime_input":{}}, {"official_runtime_input":None}):
                response=subprocess.CompletedProcess([],0,json.dumps({"classification":"pass",**extra}).encode(),b"")
                with mock.patch.object(self.manager,"validate_payload"),mock.patch.object(self.manager,"run_lifecycle",return_value=response),redirect_stdout(io.StringIO()) as out:
                    self.assertEqual(0,self.manager.lifecycle(self.args,Path("/fixture/store")))
                self.assertEqual("diagnostic-response-missing" if supported else "diagnostic-not-supported",json.loads(out.getvalue())["official_runtime_input"]["reason"])


if __name__ == "__main__":
    unittest.main()
