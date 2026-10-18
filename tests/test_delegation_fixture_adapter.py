"""Fixture adapter regression checks; mocked CLI calls do not qualify product gates."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest import mock


class DelegationFixtureAdapterTests(unittest.TestCase):
    def setUp(self):
        spec=importlib.util.spec_from_file_location("delegation_fixture_adapter",Path(__file__).parent/"fixtures/delegation_process.py")
        self.helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.helper)
        self.target=Path("/synthetic-control")
        self.before=(sys.argv,sys.stdin,sys.stdout)
        self.addCleanup(self.assert_restored)

    def assert_restored(self):
        for expected,actual in zip(self.before,(sys.argv,sys.stdin,sys.stdout)):self.assertIs(expected,actual)

    def emit(self,code,value):
        def run(*args,**kwargs):
            print(json.dumps(value));raise SystemExit(code)
        return run

    def test_normal_seven_routes_use_cli_without_injection_lookup(self):
        routes=(("intent","draft"),("intent","prepare"),("intent","apply"),
                ("work","publish"),("work","prepare"),("work","apply"),("candidate","add"))
        from hv2ref.work import WorkStore
        self.assertFalse(hasattr(WorkStore,"publish_draft"))
        for kind,action in routes:
            with self.subTest(kind=kind,action=action):
                value={"fixture":"한국어","route":[kind,action]}
                options={"confirm":"confirmation"} if action=="apply" else {"worker":Path("/synthetic-worker")} if (kind,action)==("work","publish") else {}
                expected=[str(self.target/"colvia"),kind,action,"--input","-"]
                if "confirm" in options:expected += ["--confirm",options["confirm"]]
                if "worker" in options:expected += ["--worker",str(options["worker"])]
                def run(path,*,run_name):
                    self.assertEqual(str(self.target/"colvia"),path);self.assertEqual("__main__",run_name)
                    self.assertEqual(expected,sys.argv);self.assertEqual(value,json.loads(sys.stdin.buffer.read()))
                    print(json.dumps({"returned":value}));raise SystemExit(0)
                with mock.patch.object(self.helper.runpy,"run_path",side_effect=run) as cli:
                    self.assertEqual({"returned":value},self.helper.installed_call(self.target,kind,action,value,**options))
                    cli.assert_called_once()
                self.assert_restored()

    def test_three_injection_routes_forward_to_original_and_restore(self):
        from hv2ref.errors import InjectedCrash
        from hv2ref.intent import WorkspaceIntentStore
        from hv2ref.work import WorkStore
        for kind,action,cls,method in (("intent","draft",WorkspaceIntentStore,"publish_draft"),
                ("intent","apply",WorkspaceIntentStore,"apply"),("work","apply",WorkStore,"apply")):
            with self.subTest(kind=kind,action=action):
                point="after-draft" if action=="draft" else "after-acceptance" if kind=="intent" else "after-decision"
                forward={} if action=="draft" else {"confirm_token":"token"}
                owner=object();payload={"synthetic":True}
                def original(obj,*args,**kwargs):
                    self.assertIs(owner,obj);self.assertEqual((payload,),args)
                    self.assertEqual({**forward,"inject_at":point},kwargs)
                    return "original-result"
                original_mock=mock.Mock(side_effect=original)
                def run(*args,**kwargs):
                    self.assertEqual("original-result",getattr(cls,method)(owner,payload,**forward))
                    print(json.dumps({"classification":"injected-crash","code":"HV2-INJECTED-CRASH","point":point}))
                    raise SystemExit(75)
                with mock.patch.object(cls,method,original_mock):
                    with mock.patch.object(self.helper.runpy,"run_path",side_effect=run),self.assertRaises(InjectedCrash) as caught:
                        self.helper.installed_call(self.target,kind,action,payload,inject_at=point)
                    self.assertEqual(point,caught.exception.point);self.assertIs(original_mock,getattr(cls,method))
                original_mock.assert_called_once();self.assert_restored()

    def test_invalid_injection_never_calls_cli_or_changes_stdio(self):
        for kind,action,point in (("work","publish","after-home"),("work","prepare","after-decision"),
                ("candidate","add","after-record"),("intent","prepare","after-decision"),
                ("work","apply",""),("work","apply"," "),("work","apply",False),("work","apply",7)):
            with self.subTest(kind=kind,action=action,point=point):
                with mock.patch.object(self.helper.runpy,"run_path") as cli,self.assertRaises(RuntimeError):
                    self.helper.installed_call(self.target,kind,action,{},inject_at=point)
                cli.assert_not_called();self.assert_restored()

    def test_product_refusal_preserved_but_fixture_errors_are_not_refusals(self):
        from hv2ref.errors import ContractError
        refusal={"classification":"fail","code":"HV2-EXPECTED","message":"exact refusal"}
        with mock.patch.object(self.helper.runpy,"run_path",side_effect=self.emit(65,refusal)),self.assertRaises(ContractError) as caught:
            self.helper.installed_call(self.target,"work","publish",{})
        self.assertEqual((refusal["code"],refusal["message"]),(caught.exception.code,caught.exception.message))
        cases=[(70,{"classification":"internal-error"}),(2,{}),(True,{}),(None,{}),
            (75,{"classification":"injected-crash","code":"HV2-INJECTED-CRASH","point":"after-decision"}),
            (65,{"classification":"internal-error","code":"HV2-INTERNAL","message":"error"}),(65,{"classification":"fail","code":3,"message":"error"}),(0,[])]
        for code,value in cases:
            with self.subTest(code=code,value=value),mock.patch.object(self.helper.runpy,"run_path",side_effect=self.emit(code,value)),self.assertRaises(RuntimeError):
                self.helper.installed_call(self.target,"work","publish",{})
            self.assert_restored()
        for result in ({"classification":"injected-crash","code":"HV2-INJECTED-CRASH","point":"wrong"},
                {"classification":"fail","code":"HV2-INJECTED-CRASH","point":"after-decision"}):
            with mock.patch.object(self.helper.runpy,"run_path",side_effect=self.emit(75,result)),self.assertRaises(RuntimeError):
                self.helper.installed_call(self.target,"work","apply",{},inject_at="after-decision")
            self.assert_restored()

    def test_unexpected_cli_exception_restores_patch_and_stdio(self):
        from hv2ref.work import WorkStore
        original=WorkStore.apply
        with mock.patch.object(self.helper.runpy,"run_path",side_effect=ValueError("synthetic CLI error")),self.assertRaisesRegex(ValueError,"synthetic CLI error"):
            self.helper.installed_call(self.target,"work","apply",{},inject_at="after-decision")
        self.assertIs(original,WorkStore.apply);self.assert_restored()

    def test_pre_cli_failures_preserve_stdio_and_never_run_cli(self):
        with mock.patch.object(self.helper.runpy,"run_path") as cli,self.assertRaises(ValueError):
            self.helper.installed_call(self.target,"work","publish",{"invalid":float("nan")})
        cli.assert_not_called();self.assert_restored()
        broken=mock.MagicMock();broken.__enter__.side_effect=RuntimeError("patch setup failed")
        with mock.patch.object(self.helper.runpy,"run_path") as cli:
            with mock.patch.object(self.helper.mock.patch,"object",return_value=broken),self.assertRaisesRegex(RuntimeError,"patch setup failed"):
                self.helper.installed_call(self.target,"work","apply",{},inject_at="after-decision")
        cli.assert_not_called();self.assert_restored()
