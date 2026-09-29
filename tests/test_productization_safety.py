from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from hv2ref.workspace import runtime_supported
from hv2ref.errors import ContractError
from hv2ref.jsonio import canonical_json_bytes, load_json
from hv2ref.product import source_root

from tests.test_productization import git_commit_all


def exact_snapshot(root: Path) -> dict[str, tuple[object, ...]]:
    paths = [root, *sorted(root.rglob("*"), key=lambda path: path.as_posix())]
    result: dict[str, tuple[object, ...]] = {}
    for path in paths:
        relative = "." if path == root else path.relative_to(root).as_posix()
        if path.is_symlink():
            result[relative] = ("symlink", os.readlink(path))
        elif path.is_dir():
            result[relative] = ("directory", path.stat().st_mode & 0o777)
        elif path.is_file():
            result[relative] = (
                "file",
                hashlib.sha256(path.read_bytes()).hexdigest(),
                path.stat().st_mode & 0o777,
            )
    return result


def unexpected_pack_paths(root: Path) -> list[str]:
    """Allow the exact regular Git pack index, keeping other residue visible."""
    return sorted(
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.name in {"packs", "adapters", "providers"}
        and not (path.relative_to(root).as_posix() == ".git/objects/info/packs"
                 and path.is_file() and not path.is_symlink())
    )


class SingleHomeRuntimeTests(unittest.TestCase):
    """Installation-shaped fixtures, not evidence that a lifecycle installer ran."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="workspace-runtime-")
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name).resolve() / "project"
        self.target.mkdir()
        self.source = source_root()
        self.seed()

    def seed(self):
        from hv2ref.product import workspace_candidate
        from hv2ref.workspace import bootstrap_root, target_fingerprint
        from hv2ref.work import record_ref
        self.candidate = workspace_candidate(self.source)
        # Explicitly test the verifier using isolated Python and a fixture launcher.
        # This class supplies a fixture launcher; separate tests run actual installed entry.
        self.candidate["payload"]["hv2"] = self.launcher().encode()
        self.inventory = self.candidate["inventory"]
        for item in self.inventory["entries"]:
            data = self.candidate["payload"][item["path"]]
            item.update(sha256=hashlib.sha256(data).hexdigest(), size_bytes=len(data))
        digest = hashlib.sha256(canonical_json_bytes(self.inventory)).hexdigest()
        self.ref = {"id": "product-release-" + digest[:24], "sha256": digest, "inventory_id": "worker-1"}
        self.fmt = {"record_type": "workspace-format", "format_version": 1, "authority_home_id": "home-a",
                    "created_at": "2026-01-01T00:00:00Z", "lineage": None}
        self.plan = {"record_type": "lifecycle-plan", "schema_version": 1, "operation_id": "init-a", "action": "init",
                     "authority_home_id": "home-a", "expected_binding_ref": None, "candidate_release": self.ref,
                     "format_sha256": hashlib.sha256(canonical_json_bytes(self.fmt)).hexdigest(),
                     "truth_refs": [], "remove": [], "preserve": [], "created_at": self.fmt["created_at"],
                     "target_fingerprint": target_fingerprint(self.target)}
        bootstrap_root(self.target, self.plan, self.fmt)
        self.product = self.target / ".hrn/product"
        self.release = self.product / "releases" / self.ref["id"]
        for name, data in self.candidate["payload"].items():
            path = self.release / "payload" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        self.save(self.release / "inventory.json", self.inventory)
        self.binding = {"record_type": "product-binding", "schema_version": 1, "authority_home_id": "home-a",
                        "active_release": self.ref, "prior_release": None, "operation_id": "init-a"}
        self.save(self.product / "binding.json", self.binding)
        self.receipt = {"record_type": "lifecycle-receipt", "schema_version": 1, "operation_id": "init-a",
                        "plan": self.plan, "prior_binding_ref": None, "result_binding_ref": record_ref(self.binding, "operation_id")}
        (self.product / "receipts").mkdir()
        self.save(self.product / "receipts/init-a.json", self.receipt)
        (self.target / "hv2").write_bytes(self.candidate["payload"]["hv2"])
        (self.target / "hv2").chmod(0o755)

    @staticmethod
    def save(path, value):
        path.write_bytes(canonical_json_bytes(value))

    @staticmethod
    def launcher():
        return '''#!/usr/bin/env python3
WORKSPACE_INVENTORY_ID = "worker-1"
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json
root = Path(__file__).resolve().parent
binding = json.loads((root / ".hrn/product/binding.json").read_text())
payload = root / ".hrn/product/releases" / binding["active_release"]["id"] / "payload"
sys.path.insert(0, str(payload / "src"))
from hv2ref.product import require_workspace_runtime
from hv2ref.work import WorkStore, record_ref, snapshot, make_manifest
from hv2ref.intent import WorkspaceIntentStore
from hv2ref.errors import ContractError
mode = sys.argv[1]
if mode == "foreign-module":
    import importlib.util
    spec = importlib.util.spec_from_file_location("hv2ref.work", sys.argv[2])
    module = importlib.util.module_from_spec(spec)
    sys.modules["hv2ref.work"] = module
    spec.loader.exec_module(module)
if mode == "foreign-package":
    import hv2ref
    hv2ref.__path__.append(sys.argv[2])
try:
    target = Path(sys.argv[2]) if mode == "target" else root
    observed = require_workspace_runtime(target)
    if mode == "write":
        intent = WorkspaceIntentStore(root)
        draft = {"record_type":"intent-draft","schema_version":1,"authority_home_id":"home-a","intent_id":"intent-a",
                 "revision_id":"draft-a","sequence":1,"prior_revision_ref":None,"actor":"agent","acceptance_authority":"owner",
                 "observed_at":"2026-01-01T00:00:00Z","facets":{k:{"status":"known","value":"fixture"} for k in
                 ("acceptance_oracle","destination","expected_outcome","forbidden_scope","goal","scope")},"gaps":[],"statements":[],"route":"direct-entry"}
        intent.publish_draft(draft)
        p = intent.prepare("intent-a",record_ref(draft,"revision_id"),actor="owner",reason="fixture",request_id="accept-a",observed_at=draft["observed_at"])
        graph = intent.apply(p["ticket"],confirm_token=p["confirm_token"])
        selected = graph["selections"][graph["current"]["selection_ref"]["id"]]
        intent_ref = {"authority_home_id":"home-a","kind":"intent","id":"intent-a","revision_ref":selected["revision_ref"],
                      "acceptance_ref":selected["acceptance_ref"],"selection_ref":graph["current"]["selection_ref"]}
        identity = {"record_type":"work-identity","schema_version":1,"authority_home_id":"home-a","work_id":"work-a","work_type":"change",
                    "created_at":draft["observed_at"],"acceptance_authority":"owner","lineage":None}
        tree = snapshot(root,verified_launcher_sha256=observed["launcher_sha256"])
        manifest = make_manifest(tree,tree,scope=["a"])
        import hashlib
        from hv2ref.jsonio import canonical_json_bytes
        digest = hashlib.sha256(canonical_json_bytes(manifest)).hexdigest()
        revision = {"record_type":"work-revision","schema_version":1,"authority_home_id":"home-a","work_id":"work-a","record_id":"revision-a",
                    "observed_at":draft["observed_at"],"observed_scope":["fixture"],"unavailable_scope":[],"author":"agent","operation":"start",
                    "expected_prior_selection":None,"intent_ref":intent_ref,"scope":["a"],"document_refs":[],"evidence_refs":[],
                    "result_refs":{"manifest":{"id":digest,"sha256":digest}},"progress":"active","next_action":"edit a","relations":[],
                    "rebind_from":None,"execution_context":{"mode":"local","attempt_id":"attempt-a"}}
        graph = WorkStore(root).publish(identity,revision,manifest,selection_id="selection-a",operation_id="start-a")
        observed = {"work_state":graph["state"],"binding_ref":observed["binding_ref"]}
    print(json.dumps(observed))
except ContractError as exc:
    print(exc.code + ": " + exc.message)
    sys.exit(65)
'''

    def run_runtime(self, mode="runtime", *args, isolated=True, env=None, launcher=None):
        import sys
        command = [sys.executable] + (["-I"] if isolated else []) + [str(launcher or self.target / "hv2"), mode, *map(str, args)]
        return subprocess.run(command, text=True, capture_output=True, env=env, timeout=45, cwd=self.target)

    def check_product(self):
        from hv2ref.product import verify_workspace_product
        return verify_workspace_product(self.target)

    def assert_product_refused(self):
        before = exact_snapshot(self.target)
        with self.assertRaises(ContractError): self.check_product()
        self.assertEqual(before, exact_snapshot(self.target))

    def test_inventory_exact_25_paths_and_no_retired_modules(self):
        from hv2ref.product import SERIAL_MANAGED_PATHS, workspace_candidate
        candidate = workspace_candidate(self.source)
        self.assertEqual(27, len(SERIAL_MANAGED_PATHS))
        self.assertNotIn("src/hv2ref/state.py", candidate["payload"])
        self.assertNotIn("src/hv2ref/carrier.py", candidate["payload"])
        self.assertNotIn("src/hv2ref/parallel.py", candidate["payload"])

    def test_exact_initial_product_verification_is_read_only(self):
        before = exact_snapshot(self.target)
        result = self.check_product()
        self.assertEqual(self.receipt["result_binding_ref"], result["binding_ref"])
        self.assertEqual(before, exact_snapshot(self.target))

    def test_fixture_launcher_imports_writer_runtime_without_retired_modules(self):
        result = self.run_runtime()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(self.receipt["result_binding_ref"], json.loads(result.stdout)["binding_ref"])

    def test_real_default_runtime_connects_intent_and_work_writers(self):
        result = self.run_runtime("write")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("active", json.loads(result.stdout)["work_state"])
        self.assertTrue((self.target / ".hrn/work/work-a/current.json").is_file())
        self.assertTrue((self.target / ".hrn/intents/intent-a/current.json").is_file())

    def test_source_writer_default_cannot_impersonate_installed_runtime(self):
        from hv2ref.work import WorkStore
        from hv2ref.intent import WorkspaceIntentStore
        before = exact_snapshot(self.target)
        with self.assertRaises(ContractError): WorkStore(self.target)._runtime()
        with self.assertRaises(ContractError): WorkspaceIntentStore(self.target).work_store._runtime()
        self.assertEqual(before, exact_snapshot(self.target))

    def test_nonisolated_python_is_refused(self):
        result = self.run_runtime(isolated=False)
        self.assertEqual(65, result.returncode, result.stdout + result.stderr)
        self.assertIn("isolated", result.stdout)

    def test_environment_cannot_shadow_isolated_runtime(self):
        shadow = Path(self.temp.name) / "shadow";shadow.mkdir()
        (shadow / "hv2ref").mkdir();(shadow / "hv2ref/__init__.py").write_text("raise RuntimeError('shadowed')\n")
        (shadow / "sitecustomize.py").write_text("raise RuntimeError('site override')\n")
        env = dict(os.environ, PYTHONPATH=str(shadow), PYTHONHOME=str(shadow))
        result = self.run_runtime(env=env)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_foreign_loaded_module_is_refused_even_with_same_source_bytes(self):
        result = self.run_runtime("foreign-module", self.source / "src/hv2ref/work.py")
        self.assertEqual(65, result.returncode, result.stdout + result.stderr)
        self.assertIn("outside bound payload", result.stdout)

    def test_extra_package_import_path_is_refused(self):
        result = self.run_runtime("foreign-package", self.source / "src/hv2ref")
        self.assertEqual(65, result.returncode, result.stdout + result.stderr)
        self.assertIn("package search path", result.stdout)

    def test_worker_launcher_cannot_mutate_control(self):
        git_init_existing = lambda: subprocess.run(["git", "init", "-q", str(self.target)], check=True, capture_output=True)
        git_init_existing();git_commit_all(self.target, "fixture installation")
        worker = Path(self.temp.name) / "worker"
        subprocess.run(["git", "-C", str(self.target), "worktree", "add", "--detach", str(worker)], check=True, capture_output=True)
        result = self.run_runtime("target", self.target, launcher=worker / "hv2")
        self.assertEqual(65, result.returncode, result.stdout + result.stderr)
        self.assertIn("control launcher", result.stdout)
        result = self.run_runtime(launcher=worker / "hv2")
        self.assertEqual(65, result.returncode, result.stdout + result.stderr)

    def test_binding_unknown_or_boolean_schema_is_refused(self):
        for value in [True, 2]:
            self.binding["schema_version"] = value;self.save(self.product / "binding.json", self.binding)
            self.assert_product_refused()

    def test_unimplemented_later_binding_is_refused(self):
        self.binding["prior_release"] = self.ref;self.save(self.product / "binding.json", self.binding)
        self.assert_product_refused()

    def test_receipt_nested_boolean_cannot_equal_integer_schema(self):
        self.receipt["plan"]["schema_version"] = True
        self.save(self.product / "receipts/init-a.json", self.receipt)
        self.assert_product_refused()

    def test_missing_or_orphan_receipt_is_refused(self):
        path = self.product / "receipts/init-a.json";data = path.read_bytes();path.unlink()
        self.assert_product_refused();path.write_bytes(data)
        (self.product / "receipts/extra.json").write_bytes(data)
        self.assert_product_refused()

    def test_root_ready_without_binding_never_passes_product_verification(self):
        (self.product / "binding.json").unlink()
        self.assert_product_refused()

    def test_unknown_empty_product_or_payload_directory_is_refused(self):
        for parent in [self.product, self.release, self.release / "payload"]:
            path = parent / "extra";path.mkdir();self.assert_product_refused();path.rmdir()

    def test_payload_corruption_and_unlisted_release_are_refused(self):
        path = self.release / "payload/docs/REFERENCE.md";data = path.read_bytes()
        path.write_bytes(data + b"drift\n");self.assert_product_refused();path.write_bytes(data)
        (self.product / "releases/product-release-aaaaaaaaaaaaaaaaaaaaaaaa").mkdir()
        self.assert_product_refused()

    def test_symlink_payload_file_and_directory_are_refused(self):
        for path in [self.release / "payload/README.md", self.release / "payload/docs"]:
            moved = path.with_name(path.name + "-saved");path.rename(moved);path.symlink_to(moved.name)
            self.assert_product_refused();path.unlink();moved.rename(path)

    def test_inventory_duplicate_and_order_and_missing_entries_are_refused(self):
        import copy
        original = copy.deepcopy(self.inventory)
        cases = [original["entries"][:-1], list(reversed(original["entries"])), original["entries"] + [original["entries"][0]]]
        for entries in cases:
            value = dict(original, entries=entries);self.save(self.release / "inventory.json", value);self.assert_product_refused()

    def test_full_release_hash_is_checked_not_just_id_prefix(self):
        self.binding["active_release"] = dict(self.ref, sha256=self.ref["sha256"][:24] + "0" * 40)
        self.save(self.product / "binding.json", self.binding);self.assert_product_refused()

    def test_modified_or_nonexecutable_launcher_is_refused(self):
        path = self.target / "hv2";data = path.read_bytes()
        path.write_bytes(data + b"# drift\n");self.assert_product_refused();path.write_bytes(data)
        path.chmod(0o644);self.assert_product_refused()

    def test_ignored_product_bytes_are_refused_even_when_tracked(self):
        subprocess.run(["git", "init", "-q", str(self.target)], check=True, capture_output=True)
        git_commit_all(self.target, "fixture installation")
        (self.target / ".gitignore").write_text(".hrn/product/\n")
        self.assert_product_refused()

    def test_product_reader_does_not_claim_full_truth_validation(self):
        (self.target / ".hrn/work/unverified").mkdir()
        result = self.check_product()
        self.assertNotIn("classification", result)
        self.assertNotIn("record_verification", result)


    def test_nonscalar_init_inventory_window_has_contract_error(self):
        for value in ([], {}, None, True, 1):
            self.plan["candidate_release"]["inventory_id"] = value
            self.save(self.product / "init-plan.json", self.plan)
            self.assert_product_refused()


        # The write-side init validator independently rejects nonscalar windows.
        from hv2ref.workspace import bootstrap_root, target_fingerprint
        fresh = Path(self.temp.name) / "fresh";fresh.mkdir()
        before = exact_snapshot(fresh)
        for value in ([], {}):
            self.plan["candidate_release"]["inventory_id"] = value
            self.plan["target_fingerprint"] = target_fingerprint(fresh)
            with self.assertRaises(ContractError): bootstrap_root(fresh, self.plan, self.fmt)
            self.assertEqual(before, exact_snapshot(fresh))

    def test_primary_git_default_writers_and_record_only_commit(self):
        subprocess.run(["git", "init", "-q", str(self.target)], check=True, capture_output=True)
        git_commit_all(self.target, "fixture installation")
        result = self.run_runtime("write")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("active", json.loads(result.stdout)["work_state"])
        git_commit_all(self.target, "fixture intent and Work records")
        changed = subprocess.check_output(["git", "-C", str(self.target), "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"], text=True).splitlines()
        self.assertTrue(changed)
        self.assertTrue(all(path.startswith((".hrn/intents/", ".hrn/work/")) for path in changed), changed)
        self.assertTrue(any(path.startswith(".hrn/intents/") for path in changed))
        self.assertTrue(any(path.startswith(".hrn/work/") for path in changed))
        result = self.run_runtime()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(self.receipt["result_binding_ref"], json.loads(result.stdout)["binding_ref"])

    def test_hardlinked_product_file_or_launcher_is_refused(self):
        for index, path in enumerate([self.target / "hv2", self.release / "payload/docs/REFERENCE.md"]):
            outside = Path(self.temp.name) / ("shared-" + str(index))
            os.link(path, outside)
            self.assert_product_refused()
            outside.unlink()


    def test_contract_inventory_bytes_sizes_and_paths_are_strict(self):
        import copy
        from hv2ref.product import _serial_inventory, verify_workspace_release, workspace_candidate
        before=exact_snapshot(self.target);a=workspace_candidate(self.source);b=workspace_candidate(self.source)
        self.assertEqual(a,b);self.assertEqual(before,exact_snapshot(self.target))
        path=self.release/"inventory.json";original=path.read_bytes()
        path.write_bytes(json.dumps(self.inventory).encode()+b"\n")
        with self.assertRaisesRegex(ContractError,"HV2-JSON-NONCANONICAL"):self.check_product()
        path.write_bytes(original)
        for value in (True,-1):
            inventory=copy.deepcopy(self.inventory);inventory["entries"][0]["size_bytes"]=value
            with self.subTest(size=value),self.assertRaisesRegex(ContractError,"invalid inventory digest or size"):_serial_inventory(inventory)
        for value in ("../escape","/absolute","docs/../README.md","docs/./REFERENCE.md"):
            inventory=copy.deepcopy(self.inventory);inventory["entries"][0]["path"]=value
            with self.subTest(path=value),self.assertRaisesRegex(ContractError,"unknown inventory path"):_serial_inventory(inventory)
        # Bind the altered inventory completely so the payload-size oracle is reached.
        inventory=copy.deepcopy(self.inventory);inventory["entries"][0]["size_bytes"]+=1
        digest=hashlib.sha256(canonical_json_bytes(inventory)).hexdigest()
        altered=self.release.with_name("product-release-"+digest[:24]);shutil.copytree(self.release,altered)
        self.save(altered/"inventory.json",inventory)
        with self.assertRaisesRegex(ContractError,"payload.*mismatch|payload.*digest|payload.*size"):
            verify_workspace_release(altered)


class ActualWorkspaceInitTests(unittest.TestCase):
    """Actual managed launcher/CLI with disposable targets, not a substituted launcher."""
    TIME = "2026-01-01T00:00:00Z"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="workspace-init-");self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve();self.target = self.base / "project";self.target.mkdir()
        (self.target / "a").write_bytes(b"before\n")
        self.source = source_root()

    def call(self, command, value=None, *, env=None, launcher=None, expected=0):
        result = subprocess.run([str(launcher or self.source / "hv2"), *(["--source-checkout"] if launcher is None else []), *map(str, command)],
                                input=canonical_json_bytes(value) if value is not None else None,
                                capture_output=True, cwd=self.target, env=env, timeout=45)
        if expected is not None: self.assertEqual(expected, result.returncode, (result.stdout + result.stderr).decode(errors="replace"))
        return result

    def preview(self, *, target=None, source=None):
        target = target or self.target;source = source or self.source
        result = self.call(["init", "--profile", "worker-1", "--target", target, "--source", source,
                            "--authority-home-id", "home-a", "--operation-id", "init-a", "--observed-at", self.TIME])
        return json.loads(result.stdout)

    def apply_init(self, preview, *, recover=False, point=None, expected=0, source=None):
        args = ["init", "--profile", "worker-1", "--target", self.target, "--source", source or self.source,
                "--apply", "--input", "-", "--confirm", preview["confirm_token"]]
        if recover: args.append("--recover")
        if point: args += ["--inject-at", point]
        return self.call(args, preview["request"], expected=expected)

    def installed(self, args, value=None, *, expected=0, env=None):
        return self.call(args, value, launcher=self.target / "hv2", expected=expected, env=env)

    def draft(self):
        return {"record_type":"intent-draft","schema_version":1,"authority_home_id":"home-a","intent_id":"intent-a",
                "revision_id":"draft-a","sequence":1,"prior_revision_ref":None,"actor":"agent","acceptance_authority":"owner",
                "observed_at":self.TIME,"facets":{k:{"status":"known","value":"fixture"} for k in
                ("acceptance_oracle","destination","expected_outcome","forbidden_scope","goal","scope")},"gaps":[],"statements":[],"route":"direct-entry"}

    def accept_intent(self):
        from hv2ref.work import record_ref
        draft=self.draft();self.installed(["intent","draft"],draft)
        value={"intent_id":"intent-a","revision_ref":record_ref(draft,"revision_id"),"actor":"owner","reason":"fixture",
               "request_id":"intent-accept-a","observed_at":self.TIME}
        prepared=json.loads(self.installed(["intent","prepare"],value).stdout)
        graph=json.loads(self.installed(["intent","apply","--confirm",prepared["confirm_token"]],prepared["ticket"]).stdout)
        selected=graph["selections"][graph["current"]["selection_ref"]["id"]]
        return {"authority_home_id":"home-a","kind":"intent","id":"intent-a","revision_ref":selected["revision_ref"],
                "acceptance_ref":selected["acceptance_ref"],"selection_ref":graph["current"]["selection_ref"]}

    def complete_work(self, work_id="work-a", intent_ref=None):
        from hv2ref.product import verify_workspace_product
        from hv2ref.work import snapshot, make_manifest
        intent=intent_ref if intent_ref is not None else self.accept_intent();launcher=verify_workspace_product(self.target)["launcher_sha256"]
        identity={"record_type":"work-identity","schema_version":1,"authority_home_id":"home-a","work_id":work_id,"work_type":"change",
                  "created_at":self.TIME,"acceptance_authority":"owner","lineage":None}
        base=snapshot(self.target,verified_launcher_sha256=launcher);prior=None
        for number,operation in [(1,"start"),(2,"submit-result")]:
            if number == 2: (self.target/"a").write_bytes(b"after\n")
            manifest=make_manifest(base,snapshot(self.target,verified_launcher_sha256=launcher),scope=["a"])
            digest=hashlib.sha256(canonical_json_bytes(manifest)).hexdigest()
            revision={"record_type":"work-revision","schema_version":1,"authority_home_id":"home-a","work_id":work_id,"record_id":f"revision-{number}",
                      "observed_at":self.TIME,"observed_scope":["fixture"],"unavailable_scope":[],"author":"agent","operation":operation,
                      "expected_prior_selection":prior,"intent_ref":intent,"scope":["a"],"document_refs":[],"evidence_refs":[],
                      "result_refs":{"manifest":{"id":digest,"sha256":digest}},"progress":"active" if number==1 else "review",
                      "next_action":"owner review","relations":[],"rebind_from":None,"execution_context":{"mode":"local","attempt_id":f"attempt-{number}"}}
            value={"identity":identity,"revision":revision,"manifest":manifest,"selection_id":f"selection-{number}","operation_id":f"publish-{number}"}
            graph=json.loads(self.installed(["work","publish"],value).stdout);prior=graph["current"]["selection_ref"]
        prepared=json.loads(self.installed(["work","prepare"],{"work_id":work_id,"action":"accept","actor":"owner","reason":"fixture",
                           "request_id":"accept-"+work_id,"observed_at":self.TIME,"revision_ref":None,"supersedes":None}).stdout)
        graph=json.loads(self.installed(["work","apply","--confirm",prepared["confirm_token"]],prepared["ticket"]).stdout)
        self.assertEqual("completed",graph["state"])


    def test_document_port_status_and_doctor_expose_verified_docs_read_only(self):
        self.apply_init(self.preview());before=exact_snapshot(self.target)
        for command in ("status","doctor"):
            result=json.loads(self.installed([command]).stdout)
            self.assertEqual("pass",result["classification"])
            root=self.target/result["documentation_root"]
            self.assertEqual(self.target/".hrn/product/releases"/json.loads((self.target/".hrn/product/binding.json").read_text())["active_release"]["id"]/"payload/docs",root)
            for name in ("README.md","GENERAL-WORK.md","GETTING-STARTED.md"):self.assertTrue((root/name).is_file())
            self.assertIn(result["documentation_root"]+"/README.md",result["next_action"])
            self.assertEqual(before,exact_snapshot(self.target))
        (root/"REFERENCE.md").write_bytes(b"changed\n");before=exact_snapshot(self.target)
        result=json.loads(self.call(["status","--target",self.target],expected=10).stdout)
        self.assertEqual("degraded",result["classification"]);self.assertNotIn("documentation_root",result)
        self.assertEqual(before,exact_snapshot(self.target))

    def test_document_port_agent_publication_resumes_original_request(self):
        from hv2ref.work import record_ref
        self.apply_init(self.preview());self.complete_work()
        home=self.target/".hrn/work/work-a"
        current=json.loads((home/"current.json").read_bytes())
        final=home/"selections"/(current["selection_ref"]["id"]+".json")
        selected=json.loads(final.read_bytes());final.unlink()
        (home/"decisions"/(selected["decision_ref"]["id"]+".json")).unlink()
        first=json.loads((home/"selections/selection-1.json").read_bytes())
        current["selection_ref"]=record_ref(first)
        (home/"current.json").write_bytes(canonical_json_bytes(current))
        before=exact_snapshot(self.target)
        result=json.loads(self.installed(["status"],expected=14).stdout)
        self.assertEqual(["work-a"],result["pending_work"])
        self.assertIn("original publish request",result["next_action"])
        self.assertNotIn("original ticket",result["next_action"])
        self.assertEqual(before,exact_snapshot(self.target))
        revision=json.loads((home/"revisions/revision-2.json").read_bytes())
        manifest=json.loads((home/"results"/(revision["result_refs"]["manifest"]["id"]+".json")).read_bytes())
        identity=json.loads((home/"identity.json").read_bytes())
        request={"identity":identity,"revision":revision,"manifest":manifest,"selection_id":"selection-2","operation_id":"publish-2"}
        graph=json.loads(self.installed(["work","publish"],request).stdout)
        self.assertEqual("review",graph["state"])
        self.assertEqual([],graph["pending_selections"])
        result=json.loads(self.installed(["status"]).stdout)
        self.assertEqual([],result["pending_work"])

    def test_document_port_managed_payload_generic_disclosure_guard(self):
        import re
        from hv2ref.product import SERIAL_MANAGED_PATHS
        self.apply_init(self.preview());rid=json.loads((self.target/".hrn/product/binding.json").read_text())["active_release"]["id"]
        release=self.target/".hrn/product/releases"/rid
        inventory=json.loads((release/"inventory.json").read_text());self.assertEqual(list(SERIAL_MANAGED_PATHS),[x["path"] for x in inventory["entries"]])
        pattern=re.compile(r"HV2-REPO-IMPL|HV2-PROD-00|OWNER-LOCAL|FEAT-20[0-9]{6}|run-000[0-9]|Claude R[0-9]|/(?:Users|home)/|[a-z0-9]+-reference-private")
        hits=[]
        for relative in SERIAL_MANAGED_PATHS:
            if pattern.search((release/"payload"/relative).read_text(errors="replace")):hits.append(relative)
        self.assertEqual([],hits)

    def test_document_port_local_links_resolve(self):
        import re
        docs=[self.source/"README.md",self.source/"AGENTS.md",self.source/"CLAUDE.md",*sorted((self.source/"docs").glob("*.md"))]
        for doc in docs:
            for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)",doc.read_text()):
                if "://" in link or link.startswith("#"):continue
                resolved=(doc.parent/link.split("#",1)[0]).resolve()
                self.assertTrue(resolved.is_relative_to(self.source.resolve()),f"outside repository: {doc.name}: {link}")
                self.assertTrue(resolved.exists(),f"{doc.name}: {link}")

    def test_document_port_source_and_installed_help_hide_injection(self):
        for command in ("init","update","rollback","detach","repair"):
            result=self.call([command,"--help"])
            self.assertNotIn(b"--inject-at",result.stdout)
        self.apply_init(self.preview())
        for args in (["--help"],["update","--help"],["rollback","--help"],["detach","--help"],["intent","--help"],["work","--help"]):
            result=self.installed(args);self.assertNotIn(b"--inject-at",result.stdout)
            self.assertNotIn(b"--legacy-baseline",result.stdout)
        result=self.installed(["repair","--help"],expected=None)
        self.assertNotEqual(0,result.returncode)

    def test_document_port_workspace_error_codes_are_documented(self):
        import ast
        import re
        paths=[self.source/"hv2",*[self.source/"src/hv2ref"/name for name in ("workspace.py","work.py","product.py","cli.py","jsonio.py")]]
        token=r"HV2-[A-Z0-9]+(?:-[A-Z0-9]+)*"
        codes={c for c in re.findall(token,"\n".join(p.read_text() for p in paths))
               if c.startswith(("HV2-WORKSPACE-","HV2-WORK-","HV2-JSON-","HV2-LOCK-","HV2-PARENT-","HV2-IMMUTABLE-")) or c=="HV2-INTERNAL"}
        # Audit the intent reader/writer and shared facet validators.
        source=(self.source/"src/hv2ref/intent.py").read_text()
        tree=ast.parse(source)
        start=next(n.lineno for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="workspace_intent_graph")
        shared={"_validate_facet","_exact_keys","_require_text"}
        selected=[ast.get_source_segment(source,n) for n in tree.body if getattr(n,"lineno",0)>=start or isinstance(n,ast.FunctionDef) and n.name in shared]
        codes.update(re.findall(token,"\n".join(selected)))
        self.assertGreater(len(codes),35)
        reference=(self.source/"docs/REFERENCE.md").read_text()
        documented=set(re.findall(token,reference))
        self.assertEqual([],sorted(codes-documented))

    def test_document_port_unsupported_runtime_guidance_is_read_only(self):
        from hv2ref.product import workspace_status
        self.apply_init(self.preview());before=exact_snapshot(self.target)
        with mock.patch("hv2ref.product.sys.version_info",__import__("collections").namedtuple("version_info","major minor micro releaselevel serial")(3,14,8,"final",0)):
            result=workspace_status(self.target)
        self.assertEqual("unsupported",result["classification"])
        self.assertIn("3.14.6",result["next_action"])
        self.assertIn(result["documentation_root"]+"/README.md",result["next_action"])
        self.assertEqual(before,exact_snapshot(self.target))

    def test_port_product_response_producer_tracks_executing_release(self):
        from hv2ref.product import SERIAL_MANAGED_PATHS, verify_workspace_product
        origin=self.source
        def instrument(destination,label):
            for name in SERIAL_MANAGED_PATHS:
                path=destination/name;path.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(origin/name,path)
            path=destination/"src/hv2ref/cli.py";source=path.read_text();needle="def _print(value: object) -> None:\n"
            self.assertEqual(1,source.count(needle))
            source=source.replace(needle,needle+f'    if isinstance(value, dict): value = {{**value, "fixture_runtime": {label!r}}}\n')
            path.write_text(source);return destination
        prior=instrument(self.base/"prior-source","prior");candidate=instrument(self.base/"candidate-source","candidate")
        controller=instrument(self.base/"control-source","source-only")
        for installed_rollback in (False,True):
            with self.subTest(installed_rollback=installed_rollback):
                self.target=self.base/("installed-first-hop" if installed_rollback else "source-first-hop");self.target.mkdir()
                subprocess.run(["git","init","-q",str(self.target)],check=True,capture_output=True)
                self.source=prior;self.candidate=candidate
                self.apply_init(self.preview());initial=verify_workspace_product(self.target)
                up=self.switch_preview(installed=True)
                self.assertEqual("prior",up["fixture_runtime"])
                updated=json.loads(self.switch_apply(up,installed=True).stdout)
                self.assertEqual("prior",updated["fixture_runtime"]);self.assertEqual("updated",updated["classification"])
                self.assertEqual(up["request"]["candidate_release"],json.loads((self.target/".hrn/product/binding.json").read_bytes())["active_release"])
                current=json.loads(self.installed(["status"]).stdout)
                self.assertEqual("candidate",current["fixture_runtime"]);self.assertEqual("pass",current["classification"])
                self.source=candidate if installed_rollback else controller
                expected_producer="candidate" if installed_rollback else "source-only"
                down=self.switch_preview("rollback",operation="rollback-a",installed=installed_rollback)
                self.assertEqual(expected_producer,down["fixture_runtime"])
                rolled=json.loads(self.switch_apply(down,installed=installed_rollback).stdout)
                self.assertEqual(expected_producer,rolled["fixture_runtime"]);self.assertEqual("rolled-back",rolled["classification"])
                self.assertEqual(initial["release_path"],verify_workspace_product(self.target)["release_path"])
                current=json.loads(self.installed(["status"]).stdout)
                self.assertEqual("prior",current["fixture_runtime"]);self.assertEqual("pass",current["classification"])

    def test_port_product_launcher_collision_and_link_preserve_project(self):
        for kind in ("file","link"):
            with self.subTest(kind=kind):
                self.target=self.base/kind;self.target.mkdir();preview=self.preview()
                external=self.base/(kind+"-external");external.write_bytes(b"project-owned\n")
                if kind=="file":(self.target/"hv2").write_bytes(b"project-owned\n")
                else:(self.target/"hv2").symlink_to(external)
                before=exact_snapshot(self.target)
                result=self.call(["init","--profile","worker-1","--target",self.target,"--source",self.source,"--authority-home-id","home-a","--operation-id","init-a","--observed-at",self.TIME],expected=65)
                for response in (result,self.apply_init(preview,expected=65)):
                    error=json.loads(response.stdout);self.assertEqual("HV2-WORKSPACE-PRODUCT",error["code"])
                    self.assertIn("preexisting launcher is not owned",error["message"])
                self.assertEqual(before,exact_snapshot(self.target));self.assertEqual(b"project-owned\n",external.read_bytes())

    def test_port_product_source_symlink_rejected_before_payload_read(self):
        from hv2ref.product import workspace_candidate, workspace_init_preview, workspace_init_apply
        candidate=self.switch_candidate()
        preview=workspace_init_preview(candidate,self.target,authority_home_id="home-a",operation_id="init-a",created_at=self.TIME)
        shutil.rmtree(candidate/"docs");(candidate/"docs").symlink_to(self.source/"docs",target_is_directory=True)
        before=exact_snapshot(self.target);read=Path.read_bytes;opened=os.open;external_reads=[]
        def watched(path):
            return isinstance(path,(str,bytes,os.PathLike)) and Path(os.fsdecode(path)).is_relative_to(candidate/"docs")
        def spy(path):
            if watched(path):external_reads.append(("read_bytes",str(path)))
            return read(path)
        def spy_open(path,*args,**kwargs):
            if watched(path):external_reads.append(("os.open",str(path)))
            return opened(path,*args,**kwargs)
        with mock.patch.object(Path,"read_bytes",spy),mock.patch("os.open",spy_open):
            for action in (lambda:workspace_candidate(candidate),
                           lambda:workspace_init_preview(candidate,self.target,authority_home_id="home-a",operation_id="init-a",created_at=self.TIME),
                           lambda:workspace_init_apply(candidate,self.target,preview["request"],confirm_token=preview["confirm_token"])):
                with self.assertRaises(ContractError) as error:action()
                self.assertEqual("HV2-WORKSPACE-CONTRACT",error.exception.code)
                self.assertEqual("wrong file type: docs",error.exception.message)
                self.assertEqual(before,exact_snapshot(self.target))
        self.assertEqual([],external_reads)

    def test_port_product_home_and_filesystem_root_are_refused(self):
        from hv2ref.workspace import classify_target
        from hv2ref.product import workspace_init_preview
        for target in (Path.home(),Path("/")):
            for action in (lambda:classify_target(target,mutation=True),
                           lambda:workspace_init_preview(self.source,target,authority_home_id="home-a",operation_id="init-a",created_at=self.TIME)):
                with self.subTest(target=target),self.assertRaises(ContractError) as error:action()
                self.assertEqual("HV2-WORKSPACE-TARGET",error.exception.code)
                self.assertIn("filesystem root and home",error.exception.message)

    def test_port_product_tamper_and_unknown_member_are_read_only_nonpass(self):
        for kind in ("payload","unknown"):
            with self.subTest(kind=kind):
                self.target=self.base/kind;self.target.mkdir();self.apply_init(self.preview())
                binding=json.loads((self.target/".hrn/product/binding.json").read_bytes())
                if kind=="payload":path=self.target/".hrn/product/releases"/binding["active_release"]["id"]/"payload/README.md"
                else:path=self.target/".hrn/product/unowned.txt"
                path.write_bytes(b"tamper\n");before=exact_snapshot(self.target)
                for command in ("status","doctor"):
                    result=json.loads(self.call([command,"--target",self.target],expected=10).stdout)
                    self.assertEqual("degraded",result["classification"])
                    self.assertEqual("HV2-WORKSPACE-PRODUCT",result["error_code"])
                    self.assertIn("payload digest mismatch" if kind=="payload" else "unknown product member",result["message"])
                    self.assertNotIn("documentation_root",result);self.assertEqual(before,exact_snapshot(self.target))

    def test_port_product_launcher_drift_blocks_rollback_without_binding_change(self):
        self.apply_init(self.preview());self.candidate=self.switch_candidate();self.switch_apply(self.switch_preview())
        down=self.switch_preview("rollback",operation="rollback-a")
        binding=(self.target/".hrn/product/binding.json").read_bytes()
        (self.target/"hv2").write_bytes(b"tamper\n");before=exact_snapshot(self.target)
        error=json.loads(self.switch_apply(down,expected=65).stdout)
        self.assertEqual("HV2-WORKSPACE-PRODUCT",error["code"]);self.assertIn("launcher differs",error["message"])
        self.assertEqual(binding,(self.target/".hrn/product/binding.json").read_bytes());self.assertEqual(before,exact_snapshot(self.target))

    def test_port_product_init_preserves_unrelated_secret_without_read(self):
        from hv2ref.product import workspace_init_preview, workspace_init_apply
        secret=self.target/"customer-production-secret.txt";secret.write_bytes(b"DISPOSABLE_SECRET_SENTINEL\n")
        original=secret.read_bytes();read=Path.read_bytes;opened=os.open;reads=[]
        def spy(path):
            if path==secret:reads.append(str(path))
            return read(path)
        def spy_open(path,*args,**kwargs):
            if isinstance(path,(str,bytes,os.PathLike)) and Path(os.fsdecode(path))==secret:reads.append(str(path))
            return opened(path,*args,**kwargs)
        with mock.patch.object(Path,"read_bytes",spy),mock.patch("os.open",spy_open):
            preview=workspace_init_preview(self.source,self.target,authority_home_id="home-a",operation_id="init-a",created_at=self.TIME)
            workspace_init_apply(self.source,self.target,preview["request"],confirm_token=preview["confirm_token"])
        self.assertEqual([],reads);self.assertEqual(original,secret.read_bytes())

    def test_actual_preview_apply_replay_and_read_only_status(self):
        from hv2ref.product import SERIAL_MANAGED_PATHS
        before=exact_snapshot(self.target);preview=self.preview();self.assertEqual(before,exact_snapshot(self.target))
        primary=self.target;self.target=self.base/"second-preview";self.target.mkdir()
        second_before=exact_snapshot(self.target);second=self.preview()
        self.assertEqual(second_before,exact_snapshot(self.target))
        self.assertEqual(preview["request"]["plan"]["candidate_release"],second["request"]["plan"]["candidate_release"])
        self.assertNotEqual(preview["request"]["plan"]["target_fingerprint"],second["request"]["plan"]["target_fingerprint"])
        self.target=primary
        result=json.loads(self.apply_init(preview).stdout);self.assertEqual("initialized",result["classification"])
        fmt=json.loads((self.target/".hrn/format.json").read_text())
        self.assertEqual(preview["request"]["plan"]["authority_home_id"],fmt["authority_home_id"])
        for folder in ("work","intents"):self.assertEqual([],list((self.target/".hrn"/folder).iterdir()))
        release=self.target/".hrn/product/releases"/preview["request"]["plan"]["candidate_release"]["id"]
        for name in SERIAL_MANAGED_PATHS:self.assertEqual((self.source/name).read_bytes(),(release/"payload"/name).read_bytes())
        self.assertFalse(any(p.name.startswith(".harness-v2") for p in self.target.iterdir()))
        before=exact_snapshot(self.target)
        for command in ("status","doctor"):
            result=self.installed([command],expected=None);self.assertEqual(0 if runtime_supported() else 16,result.returncode,result.stdout)
            data=json.loads(result.stdout);self.assertEqual("non-git",data["topology"]);self.assertEqual(before,exact_snapshot(self.target))
        self.assertTrue(json.loads(self.apply_init(preview).stdout)["replayed"])
        self.assertEqual(before,exact_snapshot(self.target))

    def test_actual_non_git_cli_intent_to_work_completion(self):
        self.apply_init(self.preview());self.complete_work()

    def test_actual_primary_git_cli_intent_to_work_completion(self):
        subprocess.run(["git","init","-q",str(self.target)],check=True,capture_output=True)
        self.apply_init(self.preview());git_commit_all(self.target,"fixture installation")
        self.complete_work();git_commit_all(self.target,"fixture completed Work")
        result=self.installed(["status"],expected=None);self.assertEqual(0 if runtime_supported() else 16,result.returncode,result.stdout)
        self.assertEqual({"work-a":"completed"},json.loads(result.stdout)["work_states"])
        releases=self.target/".hrn/product/releases"
        self.assertEqual([],list(releases.rglob("*.pyc")))
        self.assertEqual([],list(releases.rglob("__pycache__")))

    def test_exact_init_recovery_after_every_owned_prefix(self):
        points=("after-plan","after-format","after-ignore","after-intents","after-work","after-staged-inventory","after-staged-payload",
                "after-release","after-receipt","after-launcher-bytes","after-launcher","after-binding")
        for point in points:
            with self.subTest(point=point):
                self.target=self.base/point;self.target.mkdir();preview=self.preview()
                self.apply_init(preview,point=point,expected=75)
                if point != "after-binding": self.apply_init(preview,expected=65)
                self.apply_init(preview,recover=True)
                result=self.installed(["status"],expected=None);self.assertEqual(0 if runtime_supported() else 16,result.returncode,result.stdout)
                bindings=list((self.target/".hrn/product").glob("binding*.json"));self.assertEqual([self.target/".hrn/product/binding.json"],bindings)
                self.assertEqual(preview["request"]["plan"]["candidate_release"],json.loads(bindings[0].read_text())["active_release"])

    def test_unowned_root_prefixes_are_preserved_not_adopted(self):
        for point in ("after-root","after-product-dir"):
            with self.subTest(point=point):
                self.target=self.base/point;self.target.mkdir();preview=self.preview();self.apply_init(preview,point=point,expected=75)
                before=exact_snapshot(self.target);self.apply_init(preview,recover=True,expected=65);self.assertEqual(before,exact_snapshot(self.target))

    def test_wrong_token_and_changed_plan_leave_fresh_target_untouched(self):
        import copy
        preview=self.preview();before=exact_snapshot(self.target)
        wrong=copy.deepcopy(preview);wrong["confirm_token"]="0"*16;self.apply_init(wrong,expected=65)
        wrong=copy.deepcopy(preview);wrong["request"]["format"]["authority_home_id"]="different";self.apply_init(wrong,expected=65)
        self.assertEqual(before,exact_snapshot(self.target))

    def test_source_changed_after_preview_is_refused_before_root_creation(self):
        from hv2ref.product import SERIAL_MANAGED_PATHS
        source=self.base/"source";source.mkdir()
        for name in SERIAL_MANAGED_PATHS:
            p=source/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(self.source/name,p)
        preview=self.preview(source=source);before=exact_snapshot(self.target)
        with (source/"README.md").open("ab") as f:f.write(b"changed\n")
        self.apply_init(preview,source=source,expected=65);self.assertEqual(before,exact_snapshot(self.target))

    def test_preexisting_launcher_old_home_or_ignored_product_refuse(self):
        for kind in ("launcher","old","ignored"):
            self.target=self.base/kind;self.target.mkdir()
            if kind=="launcher":(self.target/"hv2").write_text("preserve\n")
            if kind=="old":(self.target/".harness-v2").mkdir()
            if kind=="ignored":
                subprocess.run(["git","init","-q",str(self.target)],check=True,capture_output=True)
                (self.target/".gitignore").write_text(".hrn/\n")
            before=exact_snapshot(self.target)
            if kind=="ignored":
                preview=self.preview();self.apply_init(preview,expected=65)
            else:
                self.call(["init","--profile","worker-1","--target",self.target,"--authority-home-id","home-a","--operation-id","init-a","--observed-at",self.TIME],expected=65)
            self.assertEqual(before,exact_snapshot(self.target))

    def test_recovery_preserves_unknown_and_torn_staged_bytes(self):
        preview=self.preview();self.apply_init(preview,point="after-staged-inventory",expected=75)
        rid=preview["request"]["plan"]["candidate_release"]["id"]
        inventory=self.target/".hrn/staging/init-init-a"/rid/"inventory.json"
        inventory.write_bytes(b"torn");before=exact_snapshot(self.target)
        self.apply_init(preview,recover=True,expected=65);self.assertEqual(before,exact_snapshot(self.target))

    def test_launcher_without_binding_fails_and_source_can_diagnose(self):
        preview=self.preview();self.apply_init(preview,point="after-launcher",expected=75)
        before=exact_snapshot(self.target);self.installed(["status"],expected=65)
        result=self.call(["status","--target",self.target],expected=14);self.assertEqual("partial",json.loads(result.stdout)["classification"])
        self.assertNotIn("documentation_root",json.loads(result.stdout))
        self.assertEqual(before,exact_snapshot(self.target));self.apply_init(preview,recover=True)

    def test_production_launcher_ignores_environment_and_project_source_shadow(self):
        self.apply_init(self.preview());shadow=self.target/"src/hv2ref";shadow.mkdir(parents=True)
        (shadow/"__init__.py").write_text("raise RuntimeError('untrusted project module')\n")
        env=dict(os.environ,PYTHONPATH=str(self.target/"src"),PYTHONHOME=str(self.base/"absent"))
        result=self.installed(["status"],expected=None,env=env);self.assertEqual(0 if runtime_supported() else 16,result.returncode,result.stdout+result.stderr)

    def test_tampered_importable_module_is_rejected_before_execution(self):
        preview=self.preview();self.apply_init(preview)
        rid=preview["request"]["plan"]["candidate_release"]["id"]
        p=self.target/".hrn/product/releases"/rid/"payload/src/hv2ref/cli.py"
        sentinel=self.base/"executed";p.write_text(f"from pathlib import Path\nPath({str(sentinel)!r}).touch()\n")
        self.installed(["status"],expected=65);self.assertFalse(sentinel.exists())

    def test_removed_commands_are_absent_in_source_and_installed_parser(self):
        self.apply_init(self.preview()); before=exact_snapshot(self.base)
        old=("build-release","verify-release","init-target","transition","resume","verify-state",
             "activate-parallel","register-item","claim-work","reassign-claim","finalize-work",
             "verify-repository","init-intent-home","create-intent-draft","show-intent","accept-intent","verify-intent")
        for entry in (self.call,self.installed):
            help_text=entry(["--help"]).stdout.decode()
            for command in old:
                with self.subTest(entry=entry.__name__,command=command):
                    result=entry([command],expected=2)
                    self.assertIn("invalid choice: '"+command+"'",result.stderr.decode())
                    self.assertNotIn("following arguments are required",result.stderr.decode())
                    self.assertNotIn(command,help_text)
                    self.assertEqual(before,exact_snapshot(self.base))

    def test_source_lifecycle_requires_explicit_profile(self):
        before=exact_snapshot(self.base)
        for command in (["init","--target",self.target],["update","--target",self.target,"--source",self.source],
                        ["rollback","--target",self.target],["detach","--target",self.target]):
            with self.subTest(command=command[0]):
                result=self.call(command,expected=65); error=json.loads(result.stdout)
                self.assertEqual("HV2-WORKSPACE-COMMAND",error["code"])
                self.assertEqual("source lifecycle requires explicit worker-1 profile; use retained old source for human-1",error["message"])
                self.assertEqual(before,exact_snapshot(self.base))
        result=self.call(["status","--target",self.target],expected=15)
        self.assertEqual("uninitialized",json.loads(result.stdout)["classification"])
        self.assertEqual(before,exact_snapshot(self.base))

    def test_real_worker_launcher_cannot_write_control_or_itself(self):
        subprocess.run(["git","init","-q",str(self.target)],check=True,capture_output=True)
        self.apply_init(self.preview());git_commit_all(self.target,"fixture install")
        worker=self.base/"worker";subprocess.run(["git","-C",str(self.target),"worktree","add","--detach",str(worker)],check=True,capture_output=True)
        for target in (self.target,worker):
            before=exact_snapshot(self.target)
            self.call(["intent","draft","--target",target],self.draft(),launcher=worker/"hv2",expected=65)
            self.assertEqual(before,exact_snapshot(self.target))

    def test_installed_machine_input_rejects_unknown_fields_without_truth_write(self):
        self.apply_init(self.preview());before=exact_snapshot(self.target)
        self.installed(["work","prepare"],{"surprise":True},expected=65)
        self.assertEqual(before,exact_snapshot(self.target))


    def test_source_diagnostics_never_succeed_for_root_only_prefixes(self):
        for point,code in [("after-root",10),("after-product-dir",10),("after-plan",14),("after-format",14)]:
            self.target=self.base/point;self.target.mkdir();preview=self.preview()
            self.apply_init(preview,point=point,expected=75);before=exact_snapshot(self.target)
            result=json.loads(self.call(["status","--target",self.target],expected=code).stdout)
            self.assertNotIn("documentation_root",result)
            self.assertEqual(before,exact_snapshot(self.target))

    def test_unknown_published_product_member_blocks_recovery_without_changes(self):
        preview=self.preview();self.apply_init(preview,point="after-receipt",expected=75)
        (self.target/".hrn/product/unknown").mkdir();before=exact_snapshot(self.target)
        self.apply_init(preview,recover=True,expected=65)
        self.assertEqual(before,exact_snapshot(self.target))


    def test_init_preflight_rejects_product_symlink_before_reading_plan(self):
        from hv2ref.product import workspace_init_preview
        import hv2ref.workspace as workspace
        preview=self.preview();outside=self.base/"outside";outside.mkdir()
        (outside/"init-plan.json").write_bytes(canonical_json_bytes(preview["request"]["plan"]))
        (self.target/".hrn").mkdir();(self.target/".hrn/product").symlink_to(outside,target_is_directory=True)
        before=exact_snapshot(self.target)
        with mock.patch.object(workspace,"_file_json",wraps=workspace._file_json) as reader:
            with self.assertRaises(ContractError):
                workspace_init_preview(self.source,self.target,authority_home_id="home-a",operation_id="init-a",created_at=self.TIME)
            self.assertEqual(0,reader.call_count)
        self.assertEqual(before,exact_snapshot(self.target))

    def test_launcher_rejects_nonscalar_inventory_without_traceback(self):
        preview=self.preview();self.apply_init(preview)
        rid=preview["request"]["plan"]["candidate_release"]["id"]
        release=self.target/".hrn/product/releases"/rid;data=canonical_json_bytes([]);digest=hashlib.sha256(data).hexdigest()
        (release/"inventory.json").write_bytes(data);new_id="product-release-"+digest[:24];release.rename(release.with_name(new_id))
        binding_path=self.target/".hrn/product/binding.json";binding=json.loads(binding_path.read_text())
        binding["active_release"]={"id":new_id,"sha256":digest,"inventory_id":"worker-1"};binding_path.write_bytes(canonical_json_bytes(binding))
        result=self.installed(["status"],expected=65);self.assertNotIn(b"Traceback",result.stderr)


    def test_import_root_stdlib_shadow_is_rejected_before_execution(self):
        import py_compile
        for module in ("argparse", "fcntl", "tempfile", "argparse-bytecode"):
            with self.subTest(module=module):
                self.target=self.base/module;self.target.mkdir();preview=self.preview();self.apply_init(preview)
                rid=preview["request"]["plan"]["candidate_release"]["id"]
                import_root=self.target/".hrn/product/releases"/rid/"payload/src"
                sentinel=self.base/(module+"-executed")
                data=f"from pathlib import Path\nPath({str(sentinel)!r}).touch()\nraise RuntimeError('shadow executed')\n"
                if module.endswith("-bytecode"):
                    raw=self.base/"shadow.py";raw.write_text(data)
                    py_compile.compile(str(raw),cfile=str(import_root/"argparse.pyc"),doraise=True)
                else:(import_root/(module+".py")).write_text(data)
                result=self.installed(["status"],expected=None)
                self.assertFalse(sentinel.exists(),result.stdout+result.stderr)
                self.assertEqual(65,result.returncode,result.stdout+result.stderr)

    def test_missing_home_never_imports_project_source(self):
        self.apply_init(self.preview());(self.target/".hrn").rename(self.base/"lost-home")
        package=self.target/"src/hv2ref";package.mkdir(parents=True)
        (package/"__init__.py").write_text("")
        sentinel=self.base/"project-source-executed"
        (package/"cli.py").write_text(f"from pathlib import Path\nPath({str(sentinel)!r}).touch()\nraise RuntimeError('project source executed')\n")
        result=self.installed(["status"],expected=None)
        self.assertFalse(sentinel.exists(),result.stdout+result.stderr)
        self.assertEqual(65,result.returncode,result.stdout+result.stderr)

    def test_source_requires_explicit_profile_for_workspace_descendants(self):
        self.apply_init(self.preview()); child=self.target/"sub"; child.mkdir()
        alias=self.base/"child-alias"; alias.symlink_to(child,target_is_directory=True)
        before=exact_snapshot(self.base)
        for target in (child,alias):
            with self.subTest(target=target):
                result=self.call(["init","--target",target,"--apply"],expected=65)
                error=json.loads(result.stdout)
                self.assertEqual("HV2-WORKSPACE-COMMAND",error["code"])
                self.assertEqual("source lifecycle requires explicit worker-1 profile; use retained old source for human-1",error["message"])
                self.assertEqual(before,exact_snapshot(self.base))


    def test_explicit_developer_flags_cannot_bypass_installed_home(self):
        self.apply_init(self.preview());before=exact_snapshot(self.target)
        for flag in ("--source-checkout","--legacy-baseline"):
            with self.subTest(flag=flag):
                self.installed([flag,"status"],expected=2)
                self.assertEqual(before,exact_snapshot(self.target))

    def test_diagnostic_probe_cannot_enter_workspace(self):
        self.apply_init(self.preview()); before=exact_snapshot(self.base)
        result=self.call(["durability-probe","--root",self.target/".hrn"],expected=65)
        error=json.loads(result.stdout)
        self.assertEqual("HV2-WORKSPACE-COMMAND",error["code"])
        self.assertEqual("diagnostic probe cannot enter workspace",error["message"])
        self.assertEqual(before,exact_snapshot(self.base))

    def switch_candidate(self):
        import shutil
        from hv2ref.product import SERIAL_MANAGED_PATHS
        candidate=self.base/"candidate"
        for name in SERIAL_MANAGED_PATHS:
            p=candidate/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(self.source/name,p)
        with (candidate/"hv2").open("a") as f:f.write("\n# Candidate launcher fixture.\n")
        return candidate

    def switch_preview(self,action="update",*,source=None,operation="switch-a",installed=False):
        args=[action,"--operation-id",operation,"--observed-at",self.TIME]
        if action=="update":args += ["--source",source or self.candidate]
        if installed: result=self.installed(args)
        else: result=self.call([*args,"--profile","worker-1","--target",self.target])
        return json.loads(result.stdout)

    def switch_apply(self,preview,*,source=None,recover=False,point=None,expected=0,installed=False):
        plan=preview["request"];args=[plan["action"],"--apply","--input","-","--confirm",preview["confirm_token"]]
        if plan["action"]=="update":args += ["--source",source or self.candidate]
        if recover:args += ["--recover"]
        if point:args += ["--inject-at",point]
        if installed:return self.installed(args,plan,expected=expected)
        return self.call([*args,"--profile","worker-1","--target",self.target],plan,expected=expected)

    def test_actual_update_rollback_round_trip_preserves_truth_and_runs_both_launchers(self):
        from hv2ref.product import verify_workspace_product
        for git in (False,True):
            with self.subTest(git=git):
                self.target=self.base/("git-switch" if git else "plain-switch");self.target.mkdir();(self.target/"a").write_bytes(b"before\n")
                if git:subprocess.run(["git","init","-q",str(self.target)],check=True,capture_output=True)
                self.apply_init(self.preview());self.complete_work();self.candidate=self.switch_candidate()
                initial=verify_workspace_product(self.target);truth={k:v for k,v in exact_snapshot(self.target).items() if k.startswith((".hrn/work/",".hrn/intents/"))}
                before=exact_snapshot(self.target);up=self.switch_preview(installed=True);self.assertEqual(before,exact_snapshot(self.target))
                self.assertEqual("updated",json.loads(self.switch_apply(up,installed=True).stdout)["classification"])
                updated=verify_workspace_product(self.target);self.assertNotEqual(initial["launcher_sha256"],updated["launcher_sha256"])
                self.assertEqual(truth,{k:v for k,v in exact_snapshot(self.target).items() if k.startswith((".hrn/work/",".hrn/intents/"))})
                self.assertEqual(up["request"]["candidate_release"],json.loads((self.target/".hrn/product/binding.json").read_text())["active_release"])
                self.assertEqual(0 if runtime_supported() else 16,self.installed(["status"],expected=None).returncode)
                down=self.switch_preview("rollback",operation="rollback-a",installed=True)
                self.assertEqual("rolled-back",json.loads(self.switch_apply(down,installed=True).stdout)["classification"])
                final=verify_workspace_product(self.target);self.assertEqual(initial["launcher_sha256"],final["launcher_sha256"])
                self.assertEqual(initial["release_path"],final["release_path"]);self.assertNotEqual(initial["binding_ref"],final["binding_ref"])
                self.assertEqual(0 if runtime_supported() else 16,self.installed(["status"],expected=None).returncode)
                self.assertEqual(truth,{k:v for k,v in exact_snapshot(self.target).items() if k.startswith((".hrn/work/",".hrn/intents/"))})
                before=exact_snapshot(self.target);self.assertEqual("replayed",json.loads(self.switch_apply(up).stdout)["classification"])
                self.assertEqual(before,exact_snapshot(self.target))

    def test_switch_recovers_every_published_prefix_with_changed_launcher(self):
        import sys
        self.candidate=self.switch_candidate()
        for point in ("after-receipt","after-staged-inventory","after-staged-payload","after-release","after-launcher","after-binding"):
            with self.subTest(point=point):
                self.target=self.base/point;self.target.mkdir();self.apply_init(self.preview());up=self.switch_preview()
                binding_path=self.target/".hrn/product/binding.json";prior_binding=binding_path.read_bytes()
                self.switch_apply(up,point=point,expected=75)
                if point!="after-binding":self.assertEqual(prior_binding,binding_path.read_bytes())
                before=exact_snapshot(self.target)
                status=json.loads(self.call(["status","--target",self.target],expected=None).stdout)
                self.assertEqual("partial" if point!="after-binding" else ("pass" if runtime_supported() else "unsupported"),status["classification"])
                if point!="after-binding":self.assertNotIn("documentation_root",status)
                else:self.assertIn("documentation_root",status)
                self.assertEqual(before,exact_snapshot(self.target))
                if point!="after-binding":self.switch_apply(up,expected=65)
                self.switch_apply(up,recover=True)
                self.assertEqual(up["request"]["candidate_release"],json.loads(binding_path.read_text())["active_release"])
                down=self.switch_preview("rollback",operation="rollback-a")
                self.switch_apply(down,point="after-launcher",expected=75)
                self.assertEqual(65,self.installed(["status"],expected=None).returncode)
                self.switch_apply(down,recover=True)
                self.assertEqual(0 if runtime_supported() else 16,self.installed(["status"],expected=None).returncode)

    def test_switch_rejects_source_binding_truth_and_token_drift_without_writes(self):
        import copy
        self.apply_init(self.preview());self.candidate=self.switch_candidate();up=self.switch_preview()
        bad=copy.deepcopy(up);bad["confirm_token"]="0"*16;before=exact_snapshot(self.target)
        self.switch_apply(bad,expected=65);self.assertEqual(before,exact_snapshot(self.target))
        with (self.candidate/"hv2").open("a") as f:f.write("# changed\n")
        self.switch_apply(up,expected=65);self.assertEqual(before,exact_snapshot(self.target))
        self.candidate=self.switch_candidate();self.accept_intent();before=exact_snapshot(self.target)
        self.switch_apply(up,expected=65);self.assertEqual(before,exact_snapshot(self.target))
        fresh=self.switch_preview();self.switch_apply(fresh)
        old=copy.deepcopy(up);old["request"]["operation_id"]="stale-operation";old["confirm_token"]=hashlib.sha256(canonical_json_bytes(old["request"])).hexdigest()[:16]
        before=exact_snapshot(self.target);self.switch_apply(old,expected=65);self.assertEqual(before,exact_snapshot(self.target))

    def test_switch_pending_work_decision_and_selection_block_preview_and_apply(self):
        for form in ("decision","selection"):
            with self.subTest(form=form):
                self.target=self.base/form;self.target.mkdir();(self.target/"a").write_bytes(b"before\n")
                self.apply_init(self.preview());self.candidate=self.switch_candidate();self.complete_work();up=self.switch_preview()
                home=self.target/".hrn/work/work-a";current=json.loads((home/"current.json").read_bytes())
                selection=home/"selections"/(current["selection_ref"]["id"]+".json")
                value=json.loads(selection.read_bytes());current["selection_ref"]=value["parent_selection_ref"]
                (home/"current.json").write_bytes(canonical_json_bytes(current))
                if form=="decision":selection.unlink()
                before=exact_snapshot(self.target)
                result=self.call(["update","--profile","worker-1","--target",self.target,"--source",self.candidate,"--operation-id","blocked","--observed-at",self.TIME],expected=65)
                self.assertIn("pending Work",result.stdout.decode());self.switch_apply(up,expected=65)
                status=json.loads(self.installed(["status"],expected=14).stdout)
                self.assertEqual(["work-a"],status["pending_work"])
                self.assertIn("documentation_root",status)
                self.assertIn("original ticket",status["next_action"])
                self.assertIn("confirmation token",status["next_action"])
                self.assertEqual(before,exact_snapshot(self.target))

    def test_switch_pending_intent_acceptance_and_selection_block(self):
        for form in ("acceptance","selection"):
            with self.subTest(form=form):
                self.target=self.base/form;self.target.mkdir();self.apply_init(self.preview());self.candidate=self.switch_candidate()
                self.accept_intent();up=self.switch_preview();home=self.target/".hrn/intents/intent-a"
                current=json.loads((home/"current.json").read_bytes());(home/"current.json").unlink()
                if form=="acceptance":(home/"selections"/(current["selection_ref"]["id"]+".json")).unlink()
                before=exact_snapshot(self.target)
                result=self.call(["update","--profile","worker-1","--target",self.target,"--source",self.candidate,"--operation-id","blocked","--observed-at",self.TIME],expected=65)
                self.assertIn("pending intent",result.stdout.decode());self.switch_apply(up,expected=65)
                status=json.loads(self.installed(["status"],expected=14).stdout)
                self.assertEqual(["intent-a"],status["pending_intent"])
                self.assertIn("documentation_root",status)
                self.assertIn("original ticket",status["next_action"])
                self.assertIn("confirmation token",status["next_action"])
                self.assertEqual(before,exact_snapshot(self.target))

    def test_pending_switch_blocks_record_writers_and_other_lifecycle(self):
        self.apply_init(self.preview());self.candidate=self.switch_candidate();up=self.switch_preview()
        self.switch_apply(up,point="after-receipt",expected=75);before=exact_snapshot(self.target)
        self.installed(["intent","draft"],self.draft(),expected=65)
        self.call(["rollback","--profile","worker-1","--target",self.target,"--operation-id","other","--observed-at",self.TIME],expected=65)
        self.assertEqual(before,exact_snapshot(self.target));self.switch_apply(up,recover=True)

    def test_switch_unknown_and_torn_published_bytes_are_preserved(self):
        for kind in ("unknown","torn-receipt","torn-staging"):
            with self.subTest(kind=kind):
                self.target=self.base/kind;self.target.mkdir();self.apply_init(self.preview());self.candidate=self.switch_candidate();up=self.switch_preview()
                self.switch_apply(up,point="after-staged-inventory" if kind=="torn-staging" else "after-receipt",expected=75)
                if kind=="unknown":(self.target/".hrn/product/unknown").mkdir()
                elif kind=="torn-receipt":(self.target/".hrn/product/receipts/switch-a.json").write_bytes(b'{')
                else:(self.target/".hrn/staging/switch-switch-a"/up["request"]["candidate_release"]["id"]/"inventory.json").write_bytes(b'{')
                before=exact_snapshot(self.target);self.switch_apply(up,recover=True,expected=65);self.assertEqual(before,exact_snapshot(self.target))

    def test_switch_receipt_fork_or_orphan_is_not_selected_by_filename(self):
        import copy
        from hv2ref.product import _switch_binding_receipt, _workspace_observe
        self.apply_init(self.preview());self.candidate=self.switch_candidate();up=self.switch_preview()
        prior=_workspace_observe(self.target)["binding"];self.switch_apply(up)
        for kind in ("fork","orphan"):
            with self.subTest(kind=kind):
                plan=copy.deepcopy(up["request"]);plan["operation_id"]="extra"
                _,receipt=_switch_binding_receipt(plan,prior)
                if kind=="orphan":receipt["prior_binding_ref"]["id"]="missing"
                path=self.target/".hrn/product/receipts/extra.json";path.write_bytes(canonical_json_bytes(receipt))
                before=exact_snapshot(self.target);result=self.call(["status","--target",self.target],expected=10)
                self.assertEqual("degraded",json.loads(result.stdout)["classification"]);self.assertEqual(before,exact_snapshot(self.target));path.unlink()

    def test_switch_rejects_ignored_future_release_before_receipt(self):
        subprocess.run(["git","init","-q",str(self.target)],check=True,capture_output=True)
        self.apply_init(self.preview());self.candidate=self.switch_candidate();up=self.switch_preview()
        (self.target/".gitignore").write_text("/.hrn/product/releases/"+up["request"]["candidate_release"]["id"]+"/\n")
        before=exact_snapshot(self.target);self.switch_apply(up,expected=65);self.assertEqual(before,exact_snapshot(self.target))

    def test_switch_rejects_operation_reuse_and_unsupported_rollback_target(self):
        import copy
        self.apply_init(self.preview());self.candidate=self.switch_candidate();up=self.switch_preview();self.switch_apply(up)
        bad=copy.deepcopy(up);bad["request"]["created_at"]="later";bad["confirm_token"]=hashlib.sha256(canonical_json_bytes(bad["request"])).hexdigest()[:16]
        before=exact_snapshot(self.target);self.switch_apply(bad,expected=65)
        self.call(["rollback","--profile","worker-1","--target",self.target,"--to","other-release","--operation-id","rollback-a","--observed-at",self.TIME],expected=65)
        self.assertEqual(before,exact_snapshot(self.target))


    def test_switch_case_alias_operation_is_refused_before_receipt(self):
        self.apply_init(self.preview());self.candidate=self.switch_candidate();up=self.switch_preview()
        up["request"]["operation_id"]="INIT-A"
        up["confirm_token"]=hashlib.sha256(canonical_json_bytes(up["request"])).hexdigest()[:16]
        before=exact_snapshot(self.target);self.switch_apply(up,expected=65)
        self.call(["update","--profile","worker-1","--target",self.target,"--source",self.candidate,"--operation-id","INIT-A","--observed-at",self.TIME],expected=65)
        self.assertEqual(before,exact_snapshot(self.target))


    def test_switch_invalidates_old_ticket_and_each_release_can_write_intent(self):
        from hv2ref.work import record_ref
        self.apply_init(self.preview());self.candidate=self.switch_candidate();draft=self.draft()
        self.installed(["intent","draft"],draft)
        value={"intent_id":"intent-a","revision_ref":record_ref(draft,"revision_id"),"actor":"owner","reason":"fixture",
               "request_id":"accept-before-switch","observed_at":self.TIME}
        prepared=json.loads(self.installed(["intent","prepare"],value).stdout)
        up=self.switch_preview();self.switch_apply(up)
        before=exact_snapshot(self.target)
        self.installed(["intent","apply","--confirm",prepared["confirm_token"]],prepared["ticket"],expected=65)
        self.assertEqual(before,exact_snapshot(self.target))
        value["request_id"]="accept-after-switch"
        prepared=json.loads(self.installed(["intent","prepare"],value).stdout)
        self.installed(["intent","apply","--confirm",prepared["confirm_token"]],prepared["ticket"])
        down=self.switch_preview("rollback",operation="rollback-a");self.switch_apply(down)
        draft["intent_id"]="intent-after-rollback"
        self.installed(["intent","draft"],draft)

    def test_malformed_rollback_to_reference_is_contract_error(self):
        self.apply_init(self.preview());self.candidate=self.switch_candidate();up=self.switch_preview();self.switch_apply(up)
        down=self.switch_preview("rollback",operation="rollback-a");down["request"]["candidate_release"]=[]
        before=exact_snapshot(self.target)
        result=self.call(["rollback","--profile","worker-1","--target",self.target,"--to","wrong","--apply","--input","-","--confirm",down["confirm_token"]],down["request"],expected=65)
        self.assertEqual("HV2-WORKSPACE-SWITCH-INPUT",json.loads(result.stdout)["code"])
        self.assertEqual(before,exact_snapshot(self.target))


    def test_switch_preserves_binding_permissions(self):
        import stat
        self.apply_init(self.preview());self.candidate=self.switch_candidate()
        binding=self.target/".hrn/product/binding.json";binding.chmod(0o640)
        up=self.switch_preview();self.switch_apply(up);self.assertEqual(0o640,stat.S_IMODE(binding.stat().st_mode))
        down=self.switch_preview("rollback",operation="rollback-a");self.switch_apply(down)
        self.assertEqual(0o640,stat.S_IMODE(binding.stat().st_mode))

    def test_published_release_is_an_explicit_recovery_source_when_original_drifts(self):
        for point in ("after-release","after-launcher"):
            with self.subTest(point=point):
                self.target=self.base/point;self.target.mkdir();self.apply_init(self.preview());self.candidate=self.switch_candidate()
                up=self.switch_preview();self.switch_apply(up,point=point,expected=75)
                with (self.candidate/"hv2").open("a") as f:f.write("# original source changed\n")
                before=exact_snapshot(self.target);self.switch_apply(up,recover=True,expected=65)
                self.assertEqual(before,exact_snapshot(self.target))
                payload=self.target/".hrn/product/releases"/up["request"]["candidate_release"]["id"]/"payload"
                self.switch_apply(up,recover=True,source=payload)
                self.assertEqual(0 if runtime_supported() else 16,self.installed(["status"],expected=None).returncode)

    def test_rollback_recovers_all_distinct_publication_prefixes_and_can_toggle(self):
        from hv2ref.product import verify_workspace_product
        for point in ("after-receipt","after-release","after-launcher","after-binding"):
            with self.subTest(point=point):
                self.target=self.base/point;self.target.mkdir();self.apply_init(self.preview());self.candidate=self.switch_candidate()
                up=self.switch_preview();self.switch_apply(up);q=verify_workspace_product(self.target)["release_path"]
                down=self.switch_preview("rollback",operation="rollback-a");self.switch_apply(down,point=point,expected=75)
                self.switch_apply(down,recover=True)
                again=self.switch_preview("rollback",operation="rollback-b");self.switch_apply(again)
                self.assertEqual(q,verify_workspace_product(self.target)["release_path"])

    def test_stray_release_is_preserved_without_publishing_receipt(self):
        self.apply_init(self.preview());self.candidate=self.switch_candidate();up=self.switch_preview()
        (self.target/".hrn/product/releases/stray").mkdir()
        before=exact_snapshot(self.target);self.switch_apply(up,expected=65)
        self.assertEqual(before,exact_snapshot(self.target))
        self.assertFalse((self.target/".hrn/product/receipts/switch-a.json").exists())


    def repair_preview(self, *, backup=None, source=None, expected=0):
        r=self.call(["repair","--target",self.target,"--source",source or self.source,"--backup",backup or self.base/"backup",
                     "--operation-id","repair-a","--observed-at",self.TIME],expected=expected)
        return json.loads(r.stdout)

    def repair_apply(self, preview, *, source=None, recover=False, point=None, expected=0):
        args=["repair","--target",self.target,"--source",source or self.source,"--apply","--input","-","--confirm",preview["confirm_token"]]
        if recover: args.append("--recover")
        if point: args += ["--inject-at",point]
        return self.call(args,preview["request"],expected=expected)

    def repair_damage(self):
        from hv2ref.product import verify_workspace_product
        release=Path(verify_workspace_product(self.target)["release_path"])
        (release/"payload/src/hv2ref/work.py").write_bytes(b"preserve edited source\n")
        (release/"payload/docs/GENERAL-WORK.md").unlink()
        (release/"inventory.json").write_bytes(b"damaged inventory\n")
        (self.target/"hv2").write_bytes(b"broken launcher\n")
        return release


    def test_repair_backup_physical_identity_aliases(self):
        from hv2ref.product import _repair_backup_path
        source = self.base / "repair-source"; source.mkdir()
        # Identity comparison oracle: Linux has distinct directory spellings;
        # model a filesystem returning the same device/inode for an alias.
        # Native case/normalization admission is separate execution evidence.
        real_stat = Path.stat
        for protected in (self.target, source):
            for relation in ("inside", "equal", "ancestor"):
                alias = self.base / (protected.name + "-alias-" + relation); alias.mkdir()
                represented = protected.parent if relation == "ancestor" else protected
                identity = real_stat(represented)
                backup = alias / "backup" if relation == "inside" else alias
                before = exact_snapshot(self.target)
                def alias_stat(path, *args, **kwargs):
                    if path == alias: return identity
                    return real_stat(path, *args, **kwargs)
                with self.subTest(root=protected.name, relation=relation):
                    with mock.patch.object(Path, "stat", new=alias_stat):
                        with self.assertRaisesRegex(ContractError, "backup must be outside"):
                            _repair_backup_path(backup, self.target, source)
                    self.assertEqual(before, exact_snapshot(self.target))
        outside = self.base / "external-backup"
        self.assertEqual(outside, _repair_backup_path(outside, self.target, source))
        self.assertFalse(outside.exists())

    def test_repair_exact_active_preserves_completed_truth_and_originals(self):
        from hv2ref.product import verify_workspace_product
        self.apply_init(self.preview());self.complete_work();before=exact_snapshot(self.target)
        release=self.repair_damage();preview=self.repair_preview();damaged=exact_snapshot(self.target)
        self.assertEqual(damaged,exact_snapshot(self.target));self.repair_apply(preview)
        after=exact_snapshot(self.target)
        for name,value in before.items():
            if '/staging/' not in name and '/locks/' not in name:self.assertEqual(value,after[name],name)
        backup=Path(preview["request"]["backup"])
        for f in preview["request"]["files"]:
            if f["before"]:
                data=(backup/"original"/f["path"]).read_bytes()
                self.assertEqual(f["before"]["sha256"],hashlib.sha256(data).hexdigest())
        receipt=json.loads((backup/"receipt.json").read_bytes())
        self.assertEqual(receipt["prior_binding_ref"],receipt["result_binding_ref"])
        self.assertEqual(receipt["result_binding_ref"],verify_workspace_product(self.target)["binding_ref"])
        before=exact_snapshot(self.target);saved=exact_snapshot(backup)
        self.repair_apply(preview,recover=True);self.assertEqual(before,exact_snapshot(self.target));self.assertEqual(saved,exact_snapshot(backup))
        self.assertEqual(0 if runtime_supported() else 16,self.installed(["status"],expected=None).returncode)

    def test_repair_missing_launcher_and_mode_only(self):
        for form in ("missing","mode"):
            with self.subTest(form=form):
                self.target=self.base/form;self.target.mkdir();self.apply_init(self.preview())
                if form=="missing":(self.target/"hv2").unlink()
                else:(self.target/"hv2").chmod(0o644)
                preview=self.repair_preview(backup=self.base/(form+"-backup"));self.repair_apply(preview)
                self.assertEqual(0o755,(self.target/"hv2").stat().st_mode & 0o7777)
                self.assertEqual(0 if runtime_supported() else 16,self.installed(["status"],expected=None).returncode)

    def test_repair_resumes_all_complete_publication_prefixes(self):
        for point in ("after-backup-request","after-backup","after-file","after-receipt"):
            with self.subTest(point=point):
                self.target=self.base/point;self.target.mkdir();self.apply_init(self.preview());self.repair_damage()
                preview=self.repair_preview(backup=self.base/(point+"-backup"))
                self.repair_apply(preview,point=point,expected=75)
                self.repair_apply(preview,recover=True)
                self.assertEqual(0 if runtime_supported() else 16,self.installed(["status"],expected=None).returncode)

    def test_repair_allows_pending_work_and_intent_without_changing_records(self):
        for form in ("work-decision","work-selection","intent-acceptance","intent-selection"):
            with self.subTest(form=form):
                self.target=self.base/form;self.target.mkdir();(self.target/"a").write_bytes(b"before\n");self.apply_init(self.preview())
                if form.startswith("work"):
                    self.complete_work();home=self.target/".hrn/work/work-a";current=json.loads((home/"current.json").read_bytes())
                    selection=home/"selections"/(current["selection_ref"]["id"]+".json")
                    current["selection_ref"]=json.loads(selection.read_bytes())["parent_selection_ref"]
                    (home/"current.json").write_bytes(canonical_json_bytes(current))
                    if form.endswith("decision"):selection.unlink()
                else:
                    self.accept_intent();home=self.target/".hrn/intents/intent-a";current=json.loads((home/"current.json").read_bytes())
                    (home/"current.json").unlink()
                    if form.endswith("acceptance"):(home/"selections"/(current["selection_ref"]["id"]+".json")).unlink()
                truth={k:v for k,v in exact_snapshot(self.target).items() if '/work/' in k or '/intents/' in k}
                self.repair_damage();preview=self.repair_preview(backup=self.base/(form+"-backup"));self.repair_apply(preview)
                self.assertEqual(truth,{k:v for k,v in exact_snapshot(self.target).items() if '/work/' in k or '/intents/' in k})
                result=self.installed(["status"],expected=14);self.assertEqual("partial",json.loads(result.stdout)["classification"])

    def test_repair_refuses_pending_lifecycle_metadata_damage_and_inactive_damage(self):
        from hv2ref.product import verify_workspace_product
        for form in ("pending","binding","receipt","inactive"):
            with self.subTest(form=form):
                self.target=self.base/form;self.target.mkdir();self.apply_init(self.preview());self.candidate=self.switch_candidate()
                old=Path(verify_workspace_product(self.target)["release_path"]);up=self.switch_preview()
                if form=="pending":self.switch_apply(up,point="after-receipt",expected=75)
                elif form=="binding":(self.target/".hrn/product/binding.json").write_bytes(b"{")
                elif form=="receipt":(self.target/".hrn/product/receipts/init-a.json").write_bytes(b"{")
                else:
                    self.switch_apply(up);(old/"payload/hv2").write_bytes(b"old damage")
                before=exact_snapshot(self.target)
                self.repair_preview(backup=self.base/(form+"-backup"),source=self.candidate if form=="inactive" else None,expected=65)
                self.assertEqual(before,exact_snapshot(self.target));self.assertFalse((self.base/(form+"-backup")).exists())

    def test_repair_refuses_unknown_symlink_hardlink_and_missing_directory(self):
        from hv2ref.product import verify_workspace_product
        for form in ("unknown","symlink","hardlink","directory"):
            with self.subTest(form=form):
                self.target=self.base/form;self.target.mkdir();self.apply_init(self.preview());release=Path(verify_workspace_product(self.target)["release_path"])
                if form=="unknown":(release/"payload/unknown").mkdir()
                elif form=="symlink":(self.target/"hv2").unlink();(self.target/"hv2").symlink_to(self.source/"hv2")
                elif form=="hardlink":(self.target/"hv2").unlink();os.link(release/"payload/hv2",self.target/"hv2")
                else:shutil.rmtree(release/"payload/docs")
                before=exact_snapshot(self.target);self.repair_preview(backup=self.base/(form+"-backup"),expected=65)
                self.assertEqual(before,exact_snapshot(self.target))

    def test_repair_preview_apply_drift_never_overwrites(self):
        import copy
        for form in ("token","truth","file","source","path","backup"):
            with self.subTest(form=form):
                self.target=self.base/form;self.target.mkdir();self.apply_init(self.preview());self.repair_damage()
                preview=self.repair_preview(backup=self.base/(form+"-backup"));source=None
                if form=="token":preview["confirm_token"]="wrong"
                elif form=="truth":
                    # A real new draft is published before damaging runtime; here a
                    # malformed independent truth file is enough to require refusal.
                    (self.target/".hrn/intents/unknown.json").write_bytes(b"{}")
                elif form=="file":(self.target/"hv2").write_bytes(b"new user edit")
                elif form=="source":source=self.switch_candidate()
                elif form=="path":
                    preview=copy.deepcopy(preview);preview["request"]["files"][0]["path"]="../outside"
                    preview["confirm_token"]=hashlib.sha256(canonical_json_bytes(preview["request"])).hexdigest()[:16]
                else:Path(preview["request"]["backup"]).mkdir()
                before=exact_snapshot(self.target);self.repair_apply(preview,source=source,expected=65)
                self.assertEqual(before,exact_snapshot(self.target))

    def test_repair_preserves_torn_unknown_backup_and_new_drift(self):
        for form in ("torn","unknown","target"):
            with self.subTest(form=form):
                self.target=self.base/form;self.target.mkdir();self.apply_init(self.preview());self.repair_damage()
                preview=self.repair_preview(backup=self.base/(form+"-backup"));self.repair_apply(preview,point="after-backup",expected=75)
                backup=Path(preview["request"]["backup"])
                if form=="torn":(backup/"request.json").write_bytes(b"{")
                elif form=="unknown":(backup/"unknown").mkdir()
                else:(self.target/"hv2").write_bytes(b"new change after backup")
                before=exact_snapshot(self.target);saved=exact_snapshot(backup)
                self.repair_apply(preview,recover=True,expected=65)
                self.assertEqual(before,exact_snapshot(self.target));self.assertEqual(saved,exact_snapshot(backup))

    def test_repair_requires_external_new_backup_and_actual_source_entry(self):
        self.apply_init(self.preview());self.repair_damage()
        for backup in (self.target/"backup",self.source/"backup",self.base):
            self.repair_preview(backup=backup,expected=65)
        # Restoring the launcher must not expose repair as an installed command.
        preview=self.repair_preview();self.repair_apply(preview)
        self.installed(["repair"],expected=2)

    def test_repair_after_update_uses_only_exact_active_candidate(self):
        from hv2ref.product import verify_workspace_product
        self.apply_init(self.preview());self.candidate=self.switch_candidate();up=self.switch_preview();self.switch_apply(up)
        binding=verify_workspace_product(self.target)["binding_ref"];self.repair_damage()
        self.repair_preview(expected=65)
        preview=self.repair_preview(source=self.candidate);self.repair_apply(preview,source=self.candidate)
        self.assertEqual(binding,verify_workspace_product(self.target)["binding_ref"])


    def test_repair_healthy_target_is_read_only_noop_refusal(self):
        self.apply_init(self.preview());before=exact_snapshot(self.target)
        result=self.repair_preview(expected=65)
        self.assertIn("needs no repair",result["message"])
        self.assertEqual(before,exact_snapshot(self.target));self.assertFalse((self.base/"backup").exists())

    def test_repair_rejects_changed_binding_and_source_before_backup(self):
        self.apply_init(self.preview());(self.target/"hv2").chmod(0o644);preview=self.repair_preview()
        (self.target/"hv2").chmod(0o755)
        self.candidate=self.switch_candidate();up=self.switch_preview();self.switch_apply(up)
        before=exact_snapshot(self.target)
        self.repair_apply(preview,source=self.candidate,expected=65)
        self.assertEqual(before,exact_snapshot(self.target));self.assertFalse((self.base/"backup").exists())

    def test_repair_malformed_confirmation_shapes_are_contract_errors(self):
        import copy
        self.apply_init(self.preview());self.repair_damage();preview=self.repair_preview()
        for field in ("files","plan","backup","product_observation"):
            bad=copy.deepcopy(preview);bad["request"][field]=None
            bad["confirm_token"]=hashlib.sha256(canonical_json_bytes(bad["request"])).hexdigest()[:16]
            before=exact_snapshot(self.target);self.repair_apply(bad,expected=65)
            self.assertEqual(before,exact_snapshot(self.target))

    def test_repair_rejects_worker_topology_without_touching_control(self):
        # Use a disposable fixture linked worktree inside the container boundary.
        subprocess.run(["git","init","-q",str(self.target)],check=True,capture_output=True)
        subprocess.run(["git","-C",str(self.target),"-c","user.name=Fixture","-c","user.email=fixture@example.invalid","commit","--allow-empty","-qm","fixture"],check=True,capture_output=True)
        worker=self.base/"worker"
        subprocess.run(["git","-C",str(self.target),"worktree","add","--detach",str(worker),"HEAD"],check=True,capture_output=True)
        self.apply_init(self.preview());self.repair_damage();before=exact_snapshot(self.target)
        control=self.target;self.target=worker
        result=self.repair_preview(expected=65)
        self.assertIn("linked-worktree",result["message"])
        self.assertEqual(before,exact_snapshot(control));self.assertFalse((self.base/"backup").exists())


    def detach_preview(self, *, installed=False, expected=0):
        args=["detach","--target",self.target,"--operation-id","detach-a","--observed-at",self.TIME]
        if not installed:args += ["--profile","worker-1"]
        r=self.installed(args,expected=expected) if installed else self.call(args,expected=expected)
        return json.loads(r.stdout)

    def detach_apply(self, preview, *, installed=False, recover=False, point=None, expected=0):
        args=["detach","--target",self.target,"--apply","--input","-","--confirm",preview["confirm_token"]]
        if not installed:args += ["--profile","worker-1"]
        if recover:args.append("--recover")
        if point:args += ["--inject-at",point]
        r=self.installed(args,preview["request"],expected=expected) if installed else self.call(args,preview["request"],expected=expected)
        return json.loads(r.stdout)

    def plain_detach(self, *, expected=0):
        auditor=self.base/"detached-auditor.py"
        if not auditor.exists():shutil.copy2(self.source/"tests/fixtures/product_plain_auditor.py",auditor)
        env=os.environ.copy();env["PYTHONPATH"]=str(self.base/"no-product-package");env["PYTHONDONTWRITEBYTECODE"]="1"
        before=exact_snapshot(self.target)
        result=subprocess.run([sys.executable,"-I","-B",str(auditor),str(self.target)],capture_output=True,env=env,timeout=45)
        self.assertEqual(expected,result.returncode,(result.stdout+result.stderr).decode())
        self.assertEqual(before,exact_snapshot(self.target));return json.loads(result.stdout)


    def forged_detach_launcher(self):
        self.apply_init(self.preview()); preview = self.detach_preview()
        self.detach_apply(preview, point="after-receipt", expected=75)
        foreign = b"project-owned launcher, not the installed release\n"
        (self.target / "hv2").write_bytes(foreign)
        plan = preview["request"]
        entry = next(e for e in plan["remove"] if e["path"] == "hv2")
        entry.update(sha256=hashlib.sha256(foreign).hexdigest(), size_bytes=len(foreign))
        receipt_path = self.target / ".hrn/detached.json"
        receipt = json.loads(receipt_path.read_bytes()); receipt["plan"] = plan
        receipt_path.write_bytes(canonical_json_bytes(receipt))
        preview["confirm_token"] = hashlib.sha256(canonical_json_bytes(plan)).hexdigest()[:16]
        return preview

    def test_detach_review_forged_launcher_receipt_cannot_recover(self):
        preview = self.forged_detach_launcher(); before = exact_snapshot(self.target)
        self.detach_apply(preview, recover=True, expected=65)
        self.assertEqual(before, exact_snapshot(self.target))
        self.assertTrue((self.target / "hv2").is_file())

    def test_detach_review_plain_reader_rejects_forged_launcher_origin(self):
        self.forged_detach_launcher()
        self.assertEqual("degraded", self.plain_detach(expected=10)["classification"])

    def test_detach_review_removal_race_is_bounded_without_further_deletion(self):
        from hv2ref.product import workspace_detach_apply
        for operation, point in (("unlink", "after-receipt"), ("rmdir", "after-files")):
            with self.subTest(operation=operation):
                self.target = self.base / operation; self.target.mkdir()
                self.apply_init(self.preview()); preview = self.detach_preview()
                self.detach_apply(preview, point=point, expected=75)
                before = exact_snapshot(self.target); original = getattr(Path, operation)
                def fail_removal(path, *args, **kwargs):
                    if path == self.target / "hv2" or self.target / ".hrn/product" in path.parents:
                        raise OSError("fixture removal race")
                    return original(path, *args, **kwargs)
                with mock.patch.object(Path, operation, new=fail_removal):
                    with self.assertRaisesRegex(ContractError, "HV2-WORKSPACE-DETACH"):
                        workspace_detach_apply(self.target, preview["request"], confirm_token=preview["confirm_token"], recover=True)
                self.assertEqual(before, exact_snapshot(self.target))
                self.detach_apply(preview, recover=True)

    def test_detach_review_installed_nongit_and_source_git(self):
        for git in (False, True):
            with self.subTest(git=git):
                self.target = self.base / ("cross-git" if git else "cross-nongit"); self.target.mkdir()
                if git: subprocess.run(["git", "init", "-q", str(self.target)], check=True, capture_output=True)
                self.apply_init(self.preview()); self.accept_intent()
                preview = self.detach_preview(installed=not git)
                self.assertEqual("detached", self.detach_apply(preview, installed=not git)["classification"])
                self.assertEqual("detached", self.plain_detach()["classification"])

    def test_detach_review_partial_clone_is_readable_but_cannot_resume(self):
        subprocess.run(["git", "init", "-q", str(self.target)], check=True, capture_output=True)
        self.apply_init(self.preview()); self.accept_intent(); preview = self.detach_preview()
        self.detach_apply(preview, point="after-launcher", expected=75)
        git_commit_all(self.target, "fixture partial detach")
        clone = self.base / "partial-clone"
        subprocess.run(["git", "clone", "-q", str(self.target), str(clone)], check=True, capture_output=True)
        self.target = clone; before = exact_snapshot(self.target)
        self.assertEqual("partial", self.plain_detach(expected=14)["classification"])
        self.detach_apply(preview, recover=True, expected=65)
        self.assertEqual(before, exact_snapshot(self.target))

    def test_detach_port_plain_audit_and_document_preservation(self):
        from hv2ref.product import verify_workspace_product
        subprocess.run(["git","init","-q",str(self.target)],check=True,capture_output=True)
        guide=self.target/"project-guide.md";guide.write_text("Project-authored recovery notes.\n")
        self.apply_init(self.preview());self.complete_work()
        bound=verify_workspace_product(self.target);release=Path(bound["release_path"])
        before=exact_snapshot(self.target);preview=self.detach_preview(installed=True)
        self.assertEqual("preview",preview["classification"]);self.assertEqual(before,exact_snapshot(self.target))
        self.assertEqual(bound["binding_ref"],preview["request"]["expected_binding_ref"])
        managed_doc=str((release/"payload/docs/MANUAL-OPERATION.md").relative_to(self.target))
        self.assertIn(managed_doc,[e["path"] for e in preview["request"]["remove"]])
        self.assertIn("Before detach, retain a trusted independent source/manual",(self.source/"docs/REFERENCE.md").read_text())
        detached=self.detach_apply(preview,installed=True);self.assertEqual("detached",detached["classification"])
        self.assertFalse((self.target/managed_doc).exists());self.assertEqual(b"Project-authored recovery notes.\n",guide.read_bytes())
        after=exact_snapshot(self.target)
        for name,value in before.items():
            if name=="hv2" or name==".hrn/product" or name.startswith(".hrn/product/"):continue
            self.assertEqual(value,after[name],name)
        status=json.loads(self.call(["status","--target",self.target]).stdout)
        self.assertEqual("detached",status["classification"]);self.assertNotIn("documentation_root",status)
        self.assertNotIn("initializ",status["next_action"].lower())
        self.assertEqual("read retained project truth with an independent trusted source; no active product runtime remains",status["next_action"])
        raw=(self.target/".hrn/detached.json").read_bytes();self.assertNotIn(b"reinitializ",raw.lower())
        before=exact_snapshot(self.target);replay=self.detach_apply(preview,recover=True)
        self.assertTrue(replay["replayed"]);self.assertEqual(before,exact_snapshot(self.target))
        plain=self.plain_detach();self.assertEqual("detached",plain["classification"]);self.assertFalse(plain["mutation_authorized"])

    def test_detach_port_interruption_diagnostics_and_exact_source_recovery(self):
        for point in ("after-receipt","after-launcher"):
            with self.subTest(point=point):
                self.target=self.base/point;self.target.mkdir();(self.target/"a").write_bytes(b"before\n")
                subprocess.run(["git","init","-q",str(self.target)],check=True,capture_output=True)
                init=self.preview();self.apply_init(init);self.complete_work();initial=exact_snapshot(self.target)
                truth={k:v for k,v in initial.items() if k.startswith((".hrn/work/",".hrn/intents/"))}
                preview=self.detach_preview();self.detach_apply(preview,point=point,expected=75)
                before=exact_snapshot(self.target)
                status=json.loads(self.call(["status","--target",self.target],expected=14).stdout)
                doctor=json.loads(self.call(["doctor","--target",self.target],expected=14).stdout)
                self.assertEqual(status,doctor);self.assertEqual("partial",status["classification"])
                self.assertEqual("preserve remaining files; use the exact original detach request and confirmation token with --recover from an independent trusted source",status["next_action"])
                if (self.target/"hv2").exists():
                    self.assertEqual(status,json.loads(self.installed(["status"],expected=14).stdout))
                    rejected=self.installed(["detach","--target",self.target,"--apply","--input","-","--confirm",preview["confirm_token"],"--recover"],preview["request"],expected=2)
                    self.assertIn(b"unrecognized arguments: --recover",rejected.stderr)
                from hv2ref.product import workspace_detach_apply
                with self.assertRaises(ContractError) as error:
                    workspace_detach_apply(self.target,preview["request"],confirm_token=preview["confirm_token"],recover=True,installed=True)
                self.assertEqual("HV2-WORKSPACE-PRODUCT",error.exception.code)
                self.assertEqual("detach recovery requires independent source",error.exception.message)
                fresh={"request":{**init["request"],"plan":{**init["request"]["plan"],"operation_id":"other"}}}
                fresh["confirm_token"]=hashlib.sha256(canonical_json_bytes(fresh["request"])).hexdigest()[:16]
                fresh_error=json.loads(self.apply_init(fresh,expected=65).stdout)
                self.assertEqual("HV2-WORKSPACE-PRODUCT",fresh_error["code"])
                self.assertEqual("different initialization plan",fresh_error["message"])
                original_init=json.loads(self.apply_init(init,recover=True,expected=65).stdout)
                self.assertEqual("HV2-WORKSPACE-PRODUCT",original_init["code"])
                self.assertEqual("root is not ready",original_init["message"])
                self.assertEqual(before,exact_snapshot(self.target))
                for command in (["init","--profile","worker-1","--target",self.target,"--source",self.source,"--authority-home-id","home-a","--operation-id","other","--observed-at",self.TIME],
                                ["update","--profile","worker-1","--target",self.target,"--source",self.source,"--operation-id","other","--observed-at",self.TIME],
                                ["rollback","--profile","worker-1","--target",self.target,"--operation-id","other","--observed-at",self.TIME],
                                ["detach","--profile","worker-1","--target",self.target,"--operation-id","other","--observed-at",self.TIME]):
                    error=json.loads(self.call(command,expected=65).stdout)
                    self.assertEqual("HV2-WORKSPACE-PRODUCT",error["code"])
                    # A fresh init plan is separately refused; original init replay above exercises the detached-root gate.
                    self.assertEqual("different initialization plan" if command[0]=="init" else "root is not ready",error["message"])
                    self.assertEqual(before,exact_snapshot(self.target))
                error=self.detach_apply(preview,expected=65)
                self.assertEqual("HV2-WORKSPACE-PRODUCT",error["code"])
                self.assertEqual("detach already started; exact source recovery required",error["message"])
                self.assertEqual(before,exact_snapshot(self.target))
                result=self.detach_apply(preview,recover=True);self.assertEqual("detached",result["classification"])
                self.assertTrue((self.target/".hrn/detached.json").is_file())
                after=exact_snapshot(self.target)
                for name,value in initial.items():
                    if name=="hv2" or name==".hrn/product" or name.startswith(".hrn/product/"):continue
                    self.assertEqual(value,after[name],name)
                self.assertEqual(truth,{k:v for k,v in exact_snapshot(self.target).items() if k.startswith((".hrn/work/",".hrn/intents/"))})

    def test_port_intent_cli_help_is_bounded_and_noninteractive(self):
        self.apply_init(self.preview()); before = exact_snapshot(self.target)
        root = self.installed(["--help"]).stdout.decode()
        self.assertIn("intent", root); self.assertIn("status", root)
        help_text = self.installed(["intent", "--help"]).stdout.decode()
        for command in ("draft", "prepare", "apply"): self.assertIn(command, help_text)
        for old in ("init-intent-home", "create-intent-draft", "show-intent", "accept-intent", "verify-intent", "interview"):
            self.assertNotIn(old, root.lower() + help_text.lower())
        for command in ("draft", "prepare", "apply"):
            help_text = self.installed(["intent", command, "--help"]).stdout.decode()
            self.assertIn("--input", help_text)
            if command == "apply": self.assertIn("--confirm", help_text)
        self.assertEqual(before, exact_snapshot(self.target))

    def test_port_intent_cli_files_bind_exact_acceptance_and_plain_reading(self):
        from hv2ref.work import record_ref
        self.apply_init(self.preview()); draft = self.draft(); input_path = self.base / "request.json"
        input_path.write_bytes(canonical_json_bytes(draft))
        graph = json.loads(self.installed(["intent", "draft", "--input", input_path]).stdout)
        self.assertIsNone(graph["current"]); self.assertEqual({}, graph["acceptances"])
        revision_ref = record_ref(draft, "revision_id")
        request = {"intent_id":"intent-a","revision_ref":revision_ref,"actor":"owner","reason":"fixture","request_id":"file-accept","observed_at":self.TIME}
        input_path.write_bytes(canonical_json_bytes(request)); before = exact_snapshot(self.target)
        prepared = json.loads(self.installed(["intent", "prepare", "--input", input_path]).stdout)
        self.assertEqual(before, exact_snapshot(self.target)); self.assertEqual(revision_ref, prepared["ticket"]["target_revision_ref"])
        input_path.write_bytes(canonical_json_bytes(prepared["ticket"]))
        refused = self.installed(["intent", "apply", "--input", input_path, "--confirm", "wrong"], expected=65)
        self.assertEqual("HV2-WORK-RECORD", json.loads(refused.stdout)["code"])
        self.assertEqual("confirmation token mismatch", json.loads(refused.stdout)["message"])
        self.assertEqual(before, exact_snapshot(self.target))
        graph = json.loads(self.installed(["intent", "apply", "--input", input_path, "--confirm", prepared["confirm_token"]]).stdout)
        selected = graph["selections"][graph["current"]["selection_ref"]["id"]]
        accepted = graph["acceptances"][selected["acceptance_ref"]["id"]]
        self.assertEqual(revision_ref, selected["revision_ref"])
        self.assertEqual(prepared["ticket"], accepted["confirmation"])
        before = exact_snapshot(self.target)
        result = subprocess.run([sys.executable, "-I", "-B", str(self.source / "tests/fixtures/intent_plain_auditor.py"), str(self.target), "intent-a"], capture_output=True, check=True)
        plain = json.loads(result.stdout); self.assertEqual("pass", plain["classification"])
        self.assertEqual("selected-chain-only", plain["scope"]); self.assertEqual(revision_ref, plain["revision_ref"])
        self.assertEqual(graph["current"]["selection_ref"], plain["selection_ref"])
        status = json.loads(self.installed(["status"]).stdout); self.assertEqual(1, status["intent_count"])
        self.assertEqual(status, json.loads(self.call(["status", "--target", self.target]).stdout))
        self.assertEqual(before, exact_snapshot(self.target))

    def test_port_intent_cli_plain_reader_rejects_digest_and_rebound_selection(self):
        from hv2ref.work import record_ref
        self.apply_init(self.preview()); self.accept_intent()
        home = self.target / ".hrn/intents/intent-a"; draft_path = home / "drafts/draft-a.json"
        def audit(expected, reason):
            before = exact_snapshot(self.target)
            result = subprocess.run([sys.executable, "-I", "-B", str(self.source / "tests/fixtures/intent_plain_auditor.py"), str(self.target), "intent-a"], capture_output=True)
            self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
            value = json.loads(result.stdout); self.assertEqual(reason, value["reason"])
            self.assertEqual(before, exact_snapshot(self.target))
        original = draft_path.read_bytes(); draft = load_json(draft_path, require_canonical=True)
        draft["actor"] = "tampered"; draft_path.write_bytes(canonical_json_bytes(draft))
        audit(1, "ref-digest-or-id"); draft_path.write_bytes(original)
        next_draft = self.draft(); next_draft.update(revision_id="draft-b", sequence=2, prior_revision_ref=record_ref(self.draft(), "revision_id"))
        self.installed(["intent", "draft"], next_draft)
        current_path = home / "current.json"; current = load_json(current_path, require_canonical=True)
        selection_path = home / "selections" / (current["selection_ref"]["id"] + ".json")
        selection = load_json(selection_path, require_canonical=True)
        selection["revision_ref"] = record_ref(next_draft, "revision_id"); selection_path.write_bytes(canonical_json_bytes(selection))
        current["selection_ref"] = record_ref(selection, "selection_id"); current_path.write_bytes(canonical_json_bytes(current))
        # All three content hashes are valid; the old acceptance still binds draft-a.
        audit(1, "acceptance-selection-binding")


    def test_port_intent_cli_plain_reader_nonobject_ticket_is_json_failure(self):
        from hv2ref.work import record_ref
        self.apply_init(self.preview()); self.accept_intent()
        home = self.target / ".hrn/intents/intent-a"
        current_path = home / "current.json"; current = load_json(current_path, require_canonical=True)
        selection_path = home / "selections" / (current["selection_ref"]["id"] + ".json")
        selection = load_json(selection_path, require_canonical=True)
        acceptance_path = home / "acceptances" / (selection["acceptance_ref"]["id"] + ".json")
        originals = {p:p.read_bytes() for p in (current_path, selection_path, acceptance_path)}
        for invalid in (None, [], "not-an-object", True, 7):
            with self.subTest(confirmation=invalid):
                for p, raw in originals.items(): p.write_bytes(raw)
                acceptance = load_json(acceptance_path, require_canonical=True)
                acceptance["confirmation"] = invalid; acceptance_path.write_bytes(canonical_json_bytes(acceptance))
                selection = load_json(selection_path, require_canonical=True)
                selection["acceptance_ref"] = record_ref(acceptance, "acceptance_id")
                selection_path.write_bytes(canonical_json_bytes(selection))
                current["selection_ref"] = record_ref(selection, "selection_id")
                current_path.write_bytes(canonical_json_bytes(current))
                before = exact_snapshot(self.target)
                result = subprocess.run([sys.executable, "-I", "-B", str(self.source / "tests/fixtures/intent_plain_auditor.py"), str(self.target), "intent-a"], capture_output=True)
                self.assertEqual(1, result.returncode)
                self.assertNotIn(b"Traceback", result.stderr)
                self.assertEqual({"classification":"fail", "scope":"selected-chain-only", "reason":"ticket-type"}, json.loads(result.stdout))
                self.assertEqual(before, exact_snapshot(self.target))


    def test_port_residue_pending_ticket_survives_scratch_loss_but_not_required_record_loss(self):
        self.apply_init(self.preview()); self.complete_work(); self.candidate = self.switch_candidate()
        switch = self.switch_preview(installed=True)
        home = self.target / ".hrn/work/work-a"
        current_path = home / "current.json"; current = load_json(current_path, require_canonical=True)
        selection_path = home / "selections" / (current["selection_ref"]["id"] + ".json")
        selection = load_json(selection_path, require_canonical=True)
        decision_path = home / "decisions" / (selection["decision_ref"]["id"] + ".json")
        ticket = load_json(decision_path, require_canonical=True)["confirmation"]
        token = hashlib.sha256(canonical_json_bytes(ticket)).hexdigest()[:16]
        current["selection_ref"] = selection["parent_selection_ref"]
        current_path.write_bytes(canonical_json_bytes(current)); selection_path.unlink()
        shutil.rmtree(self.target / ".hrn/staging")
        before = exact_snapshot(self.target)
        for command in ("status", "doctor"):
            status = json.loads(self.installed([command], expected=14).stdout)
            self.assertEqual("partial", status["classification"])
            self.assertEqual(["work-a"], status["pending_work"])
            self.assertIn("original ticket", status["next_action"])
        errors = [json.loads(self.switch_apply(switch, installed=True, expected=65).stdout),
                  json.loads(self.installed(["update", "--source", self.candidate, "--operation-id", "blocked", "--observed-at", self.TIME], expected=65).stdout),
                  self.detach_preview(installed=True, expected=65)]
        for error in errors:
            self.assertEqual(error["code"], "HV2-WORKSPACE-PRODUCT")
            self.assertEqual(error["message"], "pending Work blocks lifecycle")
        self.assertEqual(before, exact_snapshot(self.target))
        self.assertFalse((self.target / ".hrn/staging").exists())
        graph = json.loads(self.installed(["work", "apply", "--confirm", token], ticket).stdout)
        self.assertEqual("completed", graph["state"])
        scratch = self.target / ".hrn/staging/unrelated"; scratch.parent.mkdir(exist_ok=True); scratch.write_bytes(b"preserve me\n")
        graph = json.loads(self.installed(["work", "apply", "--confirm", token], ticket).stdout)
        self.assertEqual("completed", graph["state"])
        self.assertEqual(b"preserve me\n", scratch.read_bytes())
        self.assertEqual("pass", json.loads(self.installed(["status"]).stdout)["classification"])
        decision_path.unlink(); before = exact_snapshot(self.target)
        status = json.loads(self.installed(["status"], expected=10).stdout)
        self.assertEqual("degraded", status["classification"])
        self.assertNotIn("resume", status.get("next_action", "").lower())
        error = json.loads(self.installed(["work", "apply", "--confirm", token], ticket, expected=65).stdout)
        self.assertEqual(error["code"], "HV2-WORK-RECORD")
        self.assertEqual(error["message"], "missing or changed referenced record")
        self.assertEqual(before, exact_snapshot(self.target))

    def test_port_residue_scratch_is_preserved_and_linked_staging_is_not_authority(self):
        self.apply_init(self.preview()); self.complete_work()
        scratch = self.target / ".hrn/staging/user-scratch"; scratch.mkdir(); (scratch / "partial").write_bytes(b"unknown bytes\n")
        before = exact_snapshot(self.target)
        self.assertEqual("pass", json.loads(self.installed(["status"]).stdout)["classification"])
        self.assertEqual(before, exact_snapshot(self.target))
        staging = self.target / ".hrn/staging"; staging.rename(self.base / "preserved-staging")
        outside = self.base / "outside"; outside.mkdir(); (outside / "sentinel").write_bytes(b"external\n")
        staging.symlink_to(outside, target_is_directory=True); before = exact_snapshot(self.base)
        status = json.loads(self.call(["status", "--target", self.target], expected=10).stdout)
        self.assertEqual("degraded", status["classification"])
        self.assertEqual(status["error"], "HV2-WORKSPACE-CONTRACT")
        self.assertEqual(status["message"], "wrong file type: staging")
        error = self.detach_preview(expected=65)
        self.assertEqual(error["code"], "HV2-WORKSPACE-PRODUCT")
        self.assertEqual(error["message"], "root is not ready")
        self.assertEqual(before, exact_snapshot(self.base))

    def test_port_residue_detach_recreated_launcher_and_remaining_release_are_preserved(self):
        from hv2ref.product import verify_workspace_product
        for form in ("file", "symlink", "directory", "release"):
            with self.subTest(form=form):
                self.target = self.base / form; self.target.mkdir(); self.apply_init(self.preview()); self.accept_intent()
                release = Path(verify_workspace_product(self.target)["release_path"])
                preview = self.detach_preview(); self.detach_apply(preview, point="after-launcher", expected=75)
                launcher = self.target / "hv2"
                external = self.base / (form + "-external"); external.write_bytes(b"outside\n")
                if form == "file": launcher.write_bytes(b"user-owned\n")
                elif form == "symlink": launcher.symlink_to(external)
                elif form == "directory": launcher.mkdir()
                else: (release / "payload/README.md").write_bytes(b"changed release\n")
                before = exact_snapshot(self.base)
                status = json.loads(self.call(["status", "--target", self.target], expected=10).stdout)
                self.assertEqual("degraded", status["classification"])
                error = self.detach_apply(preview, recover=True, expected=65)
                expected_code = "HV2-WORK-CONTENT" if form == "symlink" else "HV2-WORKSPACE-PRODUCT"
                expected_message = ("unsupported file type: hv2" if form == "symlink" else
                                    "hardlinked product file: " + str(launcher) if form == "directory" else
                                    "detach remaining bytes changed; preserve")
                self.assertEqual(error["code"], expected_code)
                self.assertEqual(error["message"], expected_message)
                self.assertEqual(status["error_code"], expected_code)
                self.assertEqual(status["message"], expected_message)
                self.assertEqual(before, exact_snapshot(self.base))

    def test_port_residue_foreign_detach_authority_and_linked_home_are_refused(self):
        original = self.target; self.apply_init(self.preview()); self.accept_intent()
        preview = self.detach_preview(); self.detach_apply(preview, point="after-receipt", expected=75)
        foreign = self.base / "foreign"; foreign.mkdir(); self.target = foreign
        args = ["init", "--profile", "worker-1", "--target", foreign, "--source", self.source, "--authority-home-id", "foreign-home", "--operation-id", "init-foreign", "--observed-at", self.TIME]
        foreign_init = json.loads(self.call(args).stdout); self.apply_init(foreign_init)
        foreign_preview = self.detach_preview(); self.detach_apply(foreign_preview, point="after-receipt", expected=75)
        self.target = original; receipt = original / ".hrn/detached.json"; original_receipt = receipt.read_bytes()
        receipt.write_bytes((foreign / ".hrn/detached.json").read_bytes())
        before = exact_snapshot(self.base)
        self.assertEqual("degraded", json.loads(self.call(["status", "--target", original], expected=10).stdout)["classification"])
        error = self.detach_apply(preview, recover=True, expected=65)
        self.assertEqual(error["code"], "HV2-WORKSPACE-PRODUCT")
        self.assertEqual(error["message"], "detach plan identity/format")
        self.assertEqual(before, exact_snapshot(self.base))
        for form in ("operation", "truth-ref"):
            with self.subTest(contradiction=form):
                value = json.loads(original_receipt)
                if form == "operation": value["operation_id"] = "contradictory-operation"
                else: value["plan"]["truth_refs"][0]["sha256"] = "0" * 64
                receipt.write_bytes(canonical_json_bytes(value)); before = exact_snapshot(self.base)
                status = json.loads(self.call(["status", "--target", original], expected=10).stdout)
                self.assertEqual("degraded", status["classification"])
                error = self.detach_apply(preview, recover=True, expected=65)
                message = "detach receipt does not bind plan" if form == "operation" else "detach preserve/truth mismatch"
                self.assertEqual(error["code"], "HV2-WORKSPACE-PRODUCT")
                self.assertEqual(error["message"], message)
                self.assertEqual(before, exact_snapshot(self.base))
        receipt.write_bytes(original_receipt)
        home = original / ".hrn"; home.rename(self.base / "preserved-home"); home.symlink_to(foreign / ".hrn", target_is_directory=True)
        before = exact_snapshot(self.base)
        result = self.call(["status", "--target", original], expected=10)
        self.assertNotIn(b"Traceback", result.stderr)
        status = json.loads(result.stdout)
        self.assertEqual(status["error"], "HV2-WORKSPACE-CONTRACT")
        self.assertEqual(status["message"], "wrong file type: .hrn")
        error = self.detach_apply(preview, recover=True, expected=65)
        self.assertEqual(error["code"], "HV2-WORKSPACE-CONTRACT")
        self.assertEqual(error["message"], "wrong file type: .hrn")
        self.assertEqual(before, exact_snapshot(self.base))
        home.unlink(); home.symlink_to(self.base / "preserved-home", target_is_directory=True)
        before = exact_snapshot(self.base)
        error = self.detach_apply(preview, recover=True, expected=65)
        self.assertEqual(error["code"], "HV2-WORKSPACE-CONTRACT")
        self.assertEqual(error["message"], "wrong file type: .hrn")
        self.assertEqual(before, exact_snapshot(self.base))

    def test_review_switch_rejects_home_link_before_format_read(self):
        from hv2ref.product import workspace_switch_apply
        self.apply_init(self.preview()); self.candidate=self.switch_candidate(); preview=self.switch_preview()
        home=self.target/".hrn"; retained=self.base/"retained-home"; home.rename(retained)
        foreign=self.base/"foreign-home"; foreign.mkdir(); (foreign/"format.json").write_bytes(b'{"foreign":true}')
        for kind in ("same-home-link","foreign-home-link","regular-file"):
            with self.subTest(kind=kind):
                if kind=="regular-file": home.write_bytes(b"not a directory")
                else: home.symlink_to(retained if kind=="same-home-link" else foreign,target_is_directory=True)
                before=exact_snapshot(self.base)
                with mock.patch("hv2ref.workspace._file_json",side_effect=AssertionError("read before root guard")) as read:
                    with self.assertRaises(ContractError) as caught:
                        workspace_switch_apply(self.target, preview["request"], source=self.candidate, confirm_token=preview["confirm_token"])
                    self.assertEqual("HV2-WORKSPACE-CONTRACT",caught.exception.code)
                    self.assertEqual("wrong file type: .hrn",caught.exception.message)
                    read.assert_not_called()
                self.assertEqual(before,exact_snapshot(self.base))
                home.unlink()

    def test_review_repair_rejects_home_link_before_format_read(self):
        from hv2ref.product import workspace_repair_apply
        self.apply_init(self.preview()); self.repair_damage(); preview=self.repair_preview()
        home=self.target/".hrn"; retained=self.base/"retained-home"; home.rename(retained)
        foreign=self.base/"foreign-home"; foreign.mkdir(); (foreign/"format.json").write_bytes(b'{"foreign":true}')
        for kind in ("same-home-link","foreign-home-link","regular-file"):
            with self.subTest(kind=kind):
                if kind=="regular-file": home.write_bytes(b"not a directory")
                else: home.symlink_to(retained if kind=="same-home-link" else foreign,target_is_directory=True)
                before=exact_snapshot(self.base)
                with mock.patch("hv2ref.workspace._file_json",side_effect=AssertionError("read before root guard")) as read:
                    with self.assertRaises(ContractError) as caught:
                        workspace_repair_apply(self.source, self.target, preview["request"], confirm_token=preview["confirm_token"])
                    self.assertEqual("HV2-WORKSPACE-CONTRACT",caught.exception.code)
                    self.assertEqual("wrong file type: .hrn",caught.exception.message)
                    read.assert_not_called()
                self.assertEqual(before,exact_snapshot(self.base))
                home.unlink()

    def test_review_partial_init_refuses_installed_intent_and_work_writes(self):
        preview = self.preview(); self.apply_init(preview, point="after-launcher", expected=75)
        before = exact_snapshot(self.target)
        for command, value in ((["intent", "draft"], self.draft()), (["work", "publish"], {})):
            with self.subTest(command=command):
                error = json.loads(self.installed(command, value, expected=65).stdout)
                self.assertEqual("HV2-WORKSPACE-LAUNCHER", error["code"])
                self.assertEqual(before, exact_snapshot(self.target))
        self.apply_init(preview, recover=True)
        self.assertEqual("pass", json.loads(self.installed(["status"]).stdout)["classification"])

    def test_port_vertical_installed_cycle_git_truth_and_zero_pack(self):
        from hv2ref.product import verify_workspace_product
        from hv2ref.work import read_work
        def git(*args):
            return subprocess.run(["git", *args], cwd=self.target, capture_output=True, text=True, check=True).stdout.strip()
        git("init", "-b", "main")
        note = self.target / "docs/project-note.md"; note.parent.mkdir(); note.write_bytes(b"project owned decision remains\n")
        git_commit_all(self.target, "fixture initial project")
        self.apply_init(self.preview()); self.complete_work()
        initial = verify_workspace_product(self.target)
        truth = {k:v for k,v in exact_snapshot(self.target).items() if k.startswith((".hrn/work/", ".hrn/intents/"))}
        self.assertEqual(read_work(self.target, "work-a")["state"], "completed")
        self.assertIn(".hrn", git("status", "--short"))
        probe = self.target / ".hrn/staging/git-ignore-probe"; probe.write_bytes(b"disposable\n")
        self.assertEqual(git("check-ignore", ".hrn/staging/git-ignore-probe"), ".hrn/staging/git-ignore-probe")
        git_commit_all(self.target, "fixture accepted work and installation")
        self.assertEqual(git("status", "--short"), "")
        self.candidate = self.switch_candidate(); up = self.switch_preview(installed=True)
        binding = (self.target / ".hrn/product/binding.json").read_bytes()
        self.switch_apply(up, point="after-receipt", expected=75)
        self.assertEqual(binding, (self.target / ".hrn/product/binding.json").read_bytes())
        self.assertEqual(json.loads(self.installed(["status"], expected=14).stdout)["classification"], "partial")
        self.assertEqual(json.loads(self.switch_apply(up, recover=True).stdout)["classification"], "updated")
        self.assertEqual(load_json(self.target / ".hrn/product/binding.json", require_canonical=True)["active_release"], up["request"]["candidate_release"])
        self.assertNotEqual(git("status", "--short"), "")
        self.assertEqual(truth, {k:v for k,v in exact_snapshot(self.target).items() if k.startswith((".hrn/work/", ".hrn/intents/"))})
        git_commit_all(self.target, "fixture recovered update")
        down = self.switch_preview("rollback", operation="vertical-rollback", installed=True)
        self.assertEqual(json.loads(self.switch_apply(down, installed=True).stdout)["classification"], "rolled-back")
        final = verify_workspace_product(self.target)
        self.assertEqual(final["release_path"], initial["release_path"])
        self.assertNotEqual(final["binding_ref"], initial["binding_ref"])
        self.assertEqual(truth, {k:v for k,v in exact_snapshot(self.target).items() if k.startswith((".hrn/work/", ".hrn/intents/"))})
        git_commit_all(self.target, "fixture forward rollback")
        preview = self.detach_preview(installed=True)
        self.assertEqual(self.detach_apply(preview, installed=True)["classification"], "detached")
        self.assertEqual(self.plain_detach()["classification"], "detached")
        self.assertEqual(read_work(self.target, "work-a")["state"], "completed")
        self.assertEqual(truth, {k:v for k,v in exact_snapshot(self.target).items() if k.startswith((".hrn/work/", ".hrn/intents/"))})
        self.assertEqual(note.read_bytes(), b"project owned decision remains\n")
        self.assertFalse((self.target / "hv2").exists())
        self.assertEqual([], unexpected_pack_paths(self.target))
        git_commit_all(self.target, "fixture detach preserves project truth")
        self.assertEqual(git("status", "--short"), "")
        self.assertEqual(git("rev-list", "--count", "HEAD"), "5")

    def test_port_representation_multiple_work_identity_and_local_authority(self):
        from hv2ref.work import read_work
        self.apply_init(self.preview())
        self.complete_work("work-a")
        intent_ref = read_work(self.target, "work-a")["revisions"]["revision-1"]["intent_ref"]
        self.complete_work("work-b", intent_ref=intent_ref)
        before = exact_snapshot(self.target)
        status = json.loads(self.installed(["status"]).stdout)
        self.assertEqual(status["work_states"], {"work-a":"completed", "work-b":"completed"})
        self.assertEqual(before, exact_snapshot(self.target))
        for work_id in ("work-a", "work-b"):
            graph = read_work(self.target, work_id)
            self.assertEqual(graph["identity"]["authority_home_id"], "home-a")
            self.assertEqual(graph["identity"]["acceptance_authority"], "owner")
            self.assertEqual(graph["identity"]["work_id"], work_id)
        graph = read_work(self.target, "work-a")
        identity = {**graph["identity"], "work_type":"investigation"}
        revision = graph["revisions"]["revision-1"]
        manifest = graph["manifests"][revision["result_refs"]["manifest"]["id"]]
        error = json.loads(self.installed(["work", "publish"], {"identity":identity,"revision":revision,"manifest":manifest,"selection_id":"conflict","operation_id":"conflict"}, expected=65).stdout)
        self.assertEqual(error["code"], "HV2-WORK-RECORD")
        self.assertEqual(error["message"], "immutable Work identity mismatch")
        self.assertEqual(before, exact_snapshot(self.target))
        truth = b"".join(p.read_bytes() for root in (self.target / ".hrn/work", self.target / ".hrn/intents") for p in root.rglob("*.json"))
        for old_default in (b"PROJECT-LOCAL-EVIDENCE-001", b"PROJECT-LOCAL-FINALIZER-001", b"PROJECT-LOCAL-WRITER-001"):
            self.assertNotIn(old_default, truth)

    def test_review_detach_rejects_home_link_before_format_read(self):
        from hv2ref.product import workspace_detach_apply
        self.apply_init(self.preview()); self.accept_intent()
        preview = self.detach_preview(); self.detach_apply(preview, point="after-receipt", expected=75)
        home = self.target / ".hrn"; retained = self.base / "retained-home"
        home.rename(retained); home.symlink_to(retained, target_is_directory=True)
        before = exact_snapshot(self.base)
        with mock.patch("hv2ref.workspace._file_json", side_effect=AssertionError("format read attempted before home type guard")) as read:
            with self.assertRaises(ContractError) as caught:
                workspace_detach_apply(self.target, preview["request"], confirm_token=preview["confirm_token"], recover=True)
            self.assertEqual(caught.exception.code, "HV2-WORKSPACE-CONTRACT")
            self.assertEqual(caught.exception.message, "wrong file type: .hrn")
            read.assert_not_called()
        self.assertEqual(before, exact_snapshot(self.base))

    def test_port_residue_installed_real_resume_preserves_unrelated_scratch(self):
        self.apply_init(self.preview()); self.complete_work()
        home = self.target / ".hrn/work/work-a"
        current_path = home / "current.json"; current = load_json(current_path, require_canonical=True)
        selection_path = home / "selections" / (current["selection_ref"]["id"] + ".json")
        original_selection = selection_path.read_bytes()
        selection = load_json(selection_path, require_canonical=True)
        decision_path = home / "decisions" / (selection["decision_ref"]["id"] + ".json")
        ticket = load_json(decision_path, require_canonical=True)["confirmation"]
        token = hashlib.sha256(canonical_json_bytes(ticket)).hexdigest()[:16]
        current["selection_ref"] = selection["parent_selection_ref"]
        current_path.write_bytes(canonical_json_bytes(current)); selection_path.unlink()

        scratch = self.target / ".hrn/staging/unrelated"
        scratch.write_bytes(b"preserve during real resume\n")
        prior = current_path.read_bytes()
        graph = json.loads(self.installed(["work", "apply", "--confirm", token], ticket).stdout)
        self.assertEqual("completed", graph["state"])
        self.assertNotEqual(prior, current_path.read_bytes())
        self.assertEqual(original_selection, selection_path.read_bytes())
        self.assertEqual(b"preserve during real resume\n", scratch.read_bytes())
        self.assertEqual("pass", json.loads(self.installed(["status"]).stdout)["classification"])

    def test_port_binding_missing_referenced_intent_blocks_lifecycle_before_switch(self):
        for git in (False, True):
            with self.subTest(git=git):
                self.target = self.base / ("missing-git" if git else "missing-plain"); self.target.mkdir(); (self.target / "a").write_bytes(b"before\n")
                if git: subprocess.run(["git", "init", "-q", str(self.target)], check=True, capture_output=True)
                self.apply_init(self.preview()); self.complete_work(); self.candidate = self.switch_candidate()
                prepared = self.switch_preview(installed=True)
                home = self.target / ".hrn/intents/intent-a"
                home.rename(self.base / ("preserved-intent-git" if git else "preserved-intent-plain"))
                before = exact_snapshot(self.target)
                binding = (self.target / ".hrn/product/binding.json").read_bytes()
                status = json.loads(self.installed(["status"], expected=10).stdout)
                self.assertEqual("degraded", status["classification"])
                self.assertEqual("object directory missing or incorrectly spelled", status["message"])
                args = ["update", "--source", self.candidate, "--operation-id", "blocked", "--observed-at", self.TIME]
                for refused in (self.installed(args, expected=65), self.switch_apply(prepared, installed=True, expected=65)):
                    value = json.loads(refused.stdout)
                    self.assertEqual("HV2-WORK-RECORD", value["code"])
                    self.assertEqual("object directory missing or incorrectly spelled", value["message"])
                self.assertEqual(binding, (self.target / ".hrn/product/binding.json").read_bytes())
                self.assertEqual(before, exact_snapshot(self.target))

    def test_port_binding_clone_and_linked_worker_preserve_tracked_truth_without_staging(self):
        subprocess.run(["git", "init", "-q", str(self.target)], check=True, capture_output=True)
        self.apply_init(self.preview()); self.complete_work(); self.candidate = self.switch_candidate()
        inherited = self.switch_preview(installed=True)
        inherited_detach = self.detach_preview(installed=True)
        git_commit_all(self.target, "fixture complete workspace")
        origin = self.target; clone = self.base / "clone"; worker = self.base / "worker"
        subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(origin), "worktree", "add", "--detach", str(worker)], check=True, capture_output=True)
        truth = {k:(v[0],v[1],bool(v[2] & 0o111)) for k,v in exact_snapshot(origin).items() if k.startswith((".hrn/work/", ".hrn/intents/")) and v[0] != "directory"}
        for target, topology, control in ((clone, "primary", True), (worker, "linked-worktree", False)):
            with self.subTest(topology=topology):
                self.target = target
                self.assertFalse((target / ".hrn/staging").exists())
                self.assertFalse((target / ".hrn/locks").exists())
                before = exact_snapshot(target)
                status = json.loads(self.installed(["status"]).stdout)
                self.assertEqual("pass", status["classification"])
                self.assertEqual(topology, status["topology"])
                self.assertEqual(control, status["authoritative_control"])
                self.assertEqual({"work-a":"completed"}, status["work_states"])
                self.assertEqual(1, status["intent_count"])
                self.assertEqual(status, json.loads(self.call(["status", "--target", target]).stdout))
                launcher = target / "hv2"
                self.assertFalse(launcher.is_symlink()); self.assertTrue(launcher.stat().st_mode & 0o111)
                self.assertEqual((origin / "hv2").read_bytes(), launcher.read_bytes())
                self.assertEqual(truth, {k:(v[0],v[1],bool(v[2] & 0o111)) for k,v in exact_snapshot(target).items() if k.startswith((".hrn/work/", ".hrn/intents/")) and v[0] != "directory"})
                self.assertEqual(before, exact_snapshot(target))
        self.target = worker; before_origin = exact_snapshot(origin); before_worker = exact_snapshot(worker)
        for target in (origin, worker):
            draft = self.draft(); draft["intent_id"] = "worker-attempt"
            self.call(["intent", "draft", "--target", target], draft, launcher=worker / "hv2", expected=65)
        self.assertEqual(before_origin, exact_snapshot(origin)); self.assertEqual(before_worker, exact_snapshot(worker))
        def unsupported(result):
            value = json.loads(result.stdout)
            self.assertEqual("HV2-WORKSPACE-TARGET", value["code"])
            self.assertEqual("mutation unsupported: linked-worktree", value["message"])
        for command in ("update", "rollback", "detach"):
            args = [command, "--operation-id", "worker-blocked", "--observed-at", self.TIME]
            if command == "update": args += ["--source", self.candidate]
            unsupported(self.installed(args, expected=65))
        unsupported(self.switch_apply(inherited, installed=True, expected=65))
        unsupported(self.installed(["detach", "--apply", "--input", "-", "--confirm", inherited_detach["confirm_token"]], inherited_detach["request"], expected=65))
        self.assertEqual(before_origin, exact_snapshot(origin)); self.assertEqual(before_worker, exact_snapshot(worker))
        self.target = clone; before = exact_snapshot(clone)
        refused = self.switch_apply(inherited, installed=True, expected=65)
        self.assertEqual("HV2-WORKSPACE-PRODUCT", json.loads(refused.stdout)["code"])
        self.assertEqual("lifecycle target changed", json.loads(refused.stdout)["message"])
        self.assertEqual(before, exact_snapshot(clone))
        own = self.switch_preview(installed=True)
        self.assertEqual("updated", json.loads(self.switch_apply(own, installed=True).stdout)["classification"])
        down = self.switch_preview("rollback", operation="clone-rollback", installed=True)
        self.assertEqual("rolled-back", json.loads(self.switch_apply(down, installed=True).stdout)["classification"])
        self.assertEqual(truth, {k:(v[0],v[1],bool(v[2] & 0o111)) for k,v in exact_snapshot(clone).items() if k.startswith((".hrn/work/", ".hrn/intents/")) and v[0] != "directory"})
        self.assertEqual("detached", self.detach_apply(self.detach_preview(installed=True), installed=True)["classification"])
        self.assertEqual(before_origin, exact_snapshot(origin)); self.assertEqual(before_worker, exact_snapshot(worker))

    def test_port_authority_root_and_format_forms_preserve_bytes(self):
        cases = ("root-missing", "root-link", "root-file", "format-missing", "format-link", "format-directory", "format-malformed", "format-identity")
        for form in cases:
            with self.subTest(form=form):
                self.target = self.base / form; self.target.mkdir()
                if getattr(self, "authority_git", False): subprocess.run(["git", "init", "-q", str(self.target)], check=True, capture_output=True)
                self.apply_init(self.preview())
                root = self.target / ".hrn"; fmt = root / "format.json"
                if form.startswith("root-"):
                    saved = self.base / (form + "-saved"); root.rename(saved)
                    if form == "root-link": root.symlink_to(saved, target_is_directory=True)
                    if form == "root-file": root.write_bytes(b"not a directory\n")
                elif form == "format-missing": fmt.unlink()
                elif form == "format-link":
                    saved = self.base / (form + "-saved"); fmt.rename(saved); fmt.symlink_to(saved)
                elif form == "format-directory": fmt.unlink(); fmt.mkdir()
                elif form == "format-malformed": fmt.write_bytes(b"{\n")
                else:
                    value = load_json(fmt, require_canonical=True); value["authority_home_id"] = "another-home"
                    fmt.write_bytes(canonical_json_bytes(value))
                before = exact_snapshot(self.base)
                source = json.loads(self.call(["status", "--target", self.target], expected=15 if form == "root-missing" else 10).stdout)
                if form == "root-missing":
                    # Both supported target kinds now route to the same new reader.
                    from hv2ref.product import workspace_status
                    self.assertEqual("uninitialized", source["classification"])
                    self.assertEqual(workspace_status(self.target), source)
                else:
                    self.assertEqual("degraded", source["classification"])
                    self.assertEqual("HV2-JSON-SYNTAX" if form == "format-malformed" else "HV2-WORKSPACE-CONTRACT", source["error"])
                    if form == "format-identity": self.assertEqual("init plan/format mismatch", source["message"])
                    if form == "format-missing": self.assertEqual("not an exact bootstrap prefix", source["message"])
                installed = json.loads(self.installed(["status"], expected=65 if form.startswith("root-") else 10).stdout)
                if form.startswith("root-"): self.assertEqual("HV2-WORKSPACE-LAUNCHER", installed["code"])
                else: self.assertEqual(source, installed)
                self.assertEqual(before, exact_snapshot(self.base))

    def test_port_authority_record_graph_forms_preserve_bytes(self):
        for kind, oid in (("intents", "intent-a"), ("work", "work-a")):
            for form in ("home-link", "home-file", "missing", "link", "directory", "malformed", "wrong-authority", "wrong-id"):
                with self.subTest(kind=kind, form=form):
                    self.target = self.base / (kind + "-" + form); self.target.mkdir()
                    (self.target / "a").write_bytes(b"before\n")
                    if getattr(self, "authority_git", False): subprocess.run(["git", "init", "-q", str(self.target)], check=True, capture_output=True)
                    self.apply_init(self.preview()); self.complete_work()
                    home = self.target / ".hrn" / kind / oid; identity = home / "identity.json"
                    if form.startswith("home-"):
                        saved = self.base / (kind + "-" + form + "-saved"); home.rename(saved)
                        if form == "home-link": home.symlink_to(saved, target_is_directory=True)
                        else: home.write_bytes(b"not a directory\n")
                    elif form == "missing": identity.unlink()
                    elif form == "link":
                        saved = self.base / (kind + "-" + form + "-saved"); identity.rename(saved); identity.symlink_to(saved)
                    elif form == "directory": identity.unlink(); identity.mkdir()
                    elif form == "malformed": identity.write_bytes(b"{\n")
                    else:
                        value = load_json(identity, require_canonical=True)
                        value["authority_home_id" if form == "wrong-authority" else ("intent_id" if kind == "intents" else "work_id")] = "another"
                        identity.write_bytes(canonical_json_bytes(value))
                    before = exact_snapshot(self.base)
                    source = json.loads(self.call(["status", "--target", self.target], expected=10).stdout)
                    self.assertEqual("degraded", source["classification"])
                    self.assertEqual("HV2-JSON-SYNTAX" if form == "malformed" else ("HV2-WORKSPACE-CONTRACT" if form in ("home-link", "home-file", "link", "directory") else ("HV2-INTENT-RECORD" if kind == "intents" and form == "missing" else "HV2-WORK-RECORD")), source["error_code"])
                    if kind == "intents" and form == "missing":
                        self.assertEqual("partial intent identity", source["message"])
                    self.assertEqual(source, json.loads(self.installed(["status"], expected=10).stdout))
                    self.assertEqual(before, exact_snapshot(self.base))

    def test_port_authority_actual_permission_denial_remains_unavailable(self):
        self.assertNotEqual(0, os.geteuid(), "permission oracle requires a non-root runner")
        for subject in ("root", "format", "intent", "work"):
            with self.subTest(subject=subject):
                self.target = self.base / subject; self.target.mkdir(); (self.target / "a").write_bytes(b"before\n")
                self.apply_init(self.preview()); self.complete_work()
                path = self.target / {"root":".hrn", "format":".hrn/format.json", "intent":".hrn/intents/intent-a/identity.json", "work":".hrn/work/work-a/identity.json"}[subject]
                before = exact_snapshot(self.base); mode = path.stat().st_mode & 0o777; path.chmod(0)
                try:
                    with self.assertRaises(PermissionError):
                        if subject == "root": list(path.iterdir())
                        else: path.read_bytes()
                    source = json.loads(self.call(["status", "--target", self.target], expected=10).stdout)
                    self.assertEqual("degraded", source["classification"])
                    if subject in ("root", "format"):
                        self.assertEqual("HV2-WORKSPACE-UNAVAILABLE", source["error"])
                    else:
                        self.assertEqual("HV2-INTENT-UNAVAILABLE" if subject == "intent" else "HV2-WORK-UNAVAILABLE", source["error_code"])
                        self.assertIn("read permission denied", source["message"])
                        self.assertNotIn("malformed", source["message"])
                    installed = json.loads(self.installed(["status"], expected=65 if subject == "root" else 10).stdout)
                    if subject == "root": self.assertEqual("HV2-WORKSPACE-LAUNCHER", installed["code"])
                    else: self.assertEqual(source, installed)
                finally: path.chmod(mode)
                self.assertEqual(before, exact_snapshot(self.base))

    def test_port_authority_stat_and_read_faults_are_not_syntax_errors(self):
        from hv2ref.product import workspace_status
        from hv2ref.cli import main as cli_main
        self.apply_init(self.preview()); self.complete_work(); before = exact_snapshot(self.base)
        for relative in (".hrn/format.json", ".hrn/intents/intent-a/identity.json", ".hrn/work/work-a/identity.json"):
            for operation in ("lstat", "read_bytes"):
                with self.subTest(path=relative, operation=operation):
                    victim = self.target / relative; original = getattr(Path, operation)
                    def denied(path, *args, **kwargs):
                        if path == victim: raise PermissionError("fixture denied " + relative)
                        return original(path, *args, **kwargs)
                    with mock.patch.object(Path, operation, new=denied):
                        status = workspace_status(self.target); self.assertEqual("degraded", status["classification"])
                        expected = "HV2-WORKSPACE-UNAVAILABLE" if relative.endswith("format.json") else ("HV2-INTENT-UNAVAILABLE" if "/intents/" in relative else "HV2-WORK-UNAVAILABLE")
                        self.assertEqual(expected, status.get("error", status.get("error_code")))
                        for argv, target in ((["hv2", "status", "--target", str(self.target)], None), (["hv2", "status"], self.target)):
                            with mock.patch("sys.argv", argv), mock.patch("hv2ref.cli._print") as printed:
                                self.assertEqual(10, cli_main(workspace_target=target)); self.assertEqual(status, printed.call_args.args[0])
                    self.assertEqual(before, exact_snapshot(self.base))

    def test_port_authority_git_shape_matrix_matches_non_git_safety(self):
        self.authority_git = True
        try:
            self.test_port_authority_root_and_format_forms_preserve_bytes()
            self.test_port_authority_record_graph_forms_preserve_bytes()
        finally:
            self.authority_git = False

    def test_port_recovery_missing_plan_never_reissues_detached_authority(self):
        init=self.preview();self.apply_init(init);self.accept_intent()
        detach=self.detach_preview();self.detach_apply(detach,point="after-receipt",expected=75)
        for name in ("binding.json","init-plan.json"):(self.target/".hrn/product"/name).unlink()
        before=exact_snapshot(self.target)
        status=json.loads(self.call(["status","--target",self.target],expected=10).stdout)
        self.assertEqual("degraded",status["classification"])
        self.assertEqual("HV2-WORKSPACE-PRODUCT",status["error_code"])
        self.assertEqual("not an exact detach file-removal prefix",status["message"])
        import copy
        fresh=copy.deepcopy(init);fmt=fresh["request"]["format"];plan=fresh["request"]["plan"]
        fmt["authority_home_id"]="other";plan.update(authority_home_id="other",operation_id="other",format_sha256=hashlib.sha256(canonical_json_bytes(fmt)).hexdigest())
        fresh["confirm_token"]=hashlib.sha256(canonical_json_bytes(fresh["request"])).hexdigest()[:16]
        for response in (self.apply_init(fresh,expected=65),self.apply_init(init,recover=True,expected=65),
                         self.call(["init","--profile","worker-1","--target",self.target,"--source",self.source,"--authority-home-id","other","--operation-id","other","--observed-at",self.TIME],expected=65)):
            error=json.loads(response.stdout);self.assertEqual("HV2-WORKSPACE-PRODUCT",error["code"])
            self.assertEqual("no durable ownership plan; preserve existing root",error["message"])
        self.assertEqual(before,exact_snapshot(self.target))

        # The legacy compound loss is intentionally not a valid new-format prefix.
        self.target=self.base/"legacy-compound";self.target.mkdir();self.apply_init(self.preview())
        detach=self.detach_preview();self.detach_apply(detach,point="after-receipt",expected=75)
        (self.target/"hv2").unlink()
        for name in ("binding.json","init-plan.json"):(self.target/".hrn/product"/name).unlink()
        shutil.rmtree(self.target/".hrn/product/releases");before=exact_snapshot(self.target)
        status=json.loads(self.call(["status","--target",self.target],expected=10).stdout)
        self.assertEqual("degraded",status["classification"]);self.assertEqual("not an exact detach file-removal prefix",status["message"])
        error=self.detach_apply(detach,recover=True,expected=65)
        self.assertEqual("not an exact detach file-removal prefix",error["message"]);self.assertEqual(before,exact_snapshot(self.target))

    def test_port_recovery_missing_plan_and_exact_detach_prefix_are_distinct(self):
        self.apply_init(self.preview());(self.target/".hrn/product/init-plan.json").unlink()
        before=exact_snapshot(self.target)
        status=json.loads(self.call(["status","--target",self.target],expected=10).stdout)
        self.assertEqual("degraded",status["classification"]);self.assertEqual("integrity-failure",status["root_classification"])
        self.assertEqual("HV2-WORKSPACE-CONTRACT",status["error"])
        self.assertEqual("format/product without initialization plan",status["message"])
        self.assertEqual(["format.json","product/init-plan.json"],status["paths"])
        self.assertEqual("preserve bytes; malformed or torn files require explicit manual disposition",status["recovery"])
        self.assertEqual(status,json.loads(self.installed(["status"],expected=10).stdout))
        self.assertEqual(before,exact_snapshot(self.target))
        self.target=self.base/"prefix";self.target.mkdir();self.apply_init(self.preview());self.accept_intent()
        preview=self.detach_preview();self.detach_apply(preview,point="after-receipt",expected=75)
        from hv2ref.product import _detach_order
        order,_=_detach_order(preview["request"])
        for name in order[:4]:(self.target/name).unlink()
        before=exact_snapshot(self.target)
        status=json.loads(self.call(["status","--target",self.target],expected=14).stdout)
        self.assertEqual("partial",status["classification"]);self.assertEqual(order[4:],status["remaining_files"])
        self.assertIn("original detach request",status["next_action"]);self.assertNotIn("init",status["next_action"])
        self.assertEqual(before,exact_snapshot(self.target))
        extra=self.target/".hrn/product/unexpected";extra.write_bytes(b"preserve\n");blocked=exact_snapshot(self.target)
        status=json.loads(self.call(["status","--target",self.target],expected=10).stdout)
        self.assertEqual("HV2-WORKSPACE-PRODUCT",status["error_code"]);self.assertEqual("unknown detach member; preserve",status["message"])
        error=self.detach_apply(preview,recover=True,expected=65);self.assertEqual("unknown detach member; preserve",error["message"])
        self.assertEqual(blocked,exact_snapshot(self.target))
        extra.unlink()  # Fixture restores only the deliberately introduced unknown member.
        result=self.detach_apply(preview,recover=True);self.assertEqual("detached",result["classification"])
        self.assertFalse((self.target/"hv2").exists());self.assertFalse((self.target/".hrn/product").exists())
        self.assertTrue((self.target/".hrn/detached.json").is_file())
        for name,value in before.items():
            if name==".hrn/product" or name.startswith(".hrn/product/"):continue
            self.assertEqual(value,exact_snapshot(self.target)[name],name)

    def test_port_recovery_detach_receipt_semantic_type_is_preserved_and_rejected(self):
        self.apply_init(self.preview());preview=self.detach_preview();self.detach_apply(preview,point="after-receipt",expected=75)
        path=self.target/".hrn/detached.json";receipt=json.loads(path.read_bytes());receipt["plan"]["created_at"]=7
        path.write_bytes(canonical_json_bytes(receipt));before=exact_snapshot(self.target)
        status=json.loads(self.call(["status","--target",self.target],expected=10).stdout)
        self.assertEqual("degraded",status["classification"]);self.assertEqual("HV2-WORKSPACE-PRODUCT",status["error_code"])
        self.assertEqual("detach plan identity/format",status["message"])
        error=self.detach_apply(preview,recover=True,expected=65)
        self.assertEqual("HV2-WORKSPACE-PRODUCT",error["code"]);self.assertEqual("detach plan identity/format",error["message"])
        self.assertEqual(before,exact_snapshot(self.target))

    def test_port_recovery_existing_root_refuses_authority_reissue(self):
        prepared=self.preview();(self.target/".hrn").mkdir();before=exact_snapshot(self.target)
        response=self.call(["init","--profile","worker-1","--target",self.target,"--source",self.source,"--authority-home-id","home-a","--operation-id","init-a","--observed-at",self.TIME],expected=65)
        error=json.loads(response.stdout);self.assertEqual("HV2-WORKSPACE-PRODUCT",error["code"])
        self.assertEqual("no durable ownership plan; preserve existing root",error["message"])
        applied=json.loads(self.apply_init(prepared,expected=65).stdout)
        self.assertEqual(error,applied)
        self.assertEqual(before,exact_snapshot(self.target))

    def test_port_recovery_installed_launcher_cannot_init_another_target(self):
        self.apply_init(self.preview());other=self.base/"other";other.mkdir();(other/"a").write_bytes(b"other project\n")
        before=exact_snapshot(self.target);other_before=exact_snapshot(other)
        args=["init","--profile","worker-1","--target",other,"--source",self.source,"--authority-home-id","other","--operation-id","other","--observed-at",self.TIME]
        for prefix in ([],["--source-checkout"],["--legacy-baseline"]):
            response=self.installed(prefix+args,expected=2)
            self.assertIn(b"invalid choice",response.stderr);self.assertIn(b"'init'",response.stderr)
            self.assertEqual(before,exact_snapshot(self.target));self.assertEqual(other_before,exact_snapshot(other))

    def test_port_recovery_init_race_preserves_user_launcher_and_partial_prefix(self):
        from hv2ref.product import workspace_init_apply, workspace_status
        from hv2ref.workspace import bootstrap_root
        preview=self.preview();before=exact_snapshot(self.target);user_launcher=b"project-created launcher\n"
        calls=[]
        def create_after_bootstrap(*args,**kwargs):
            result=bootstrap_root(*args,**kwargs);calls.append(True)
            (self.target/"hv2").write_bytes(user_launcher)
            return result
        with mock.patch("hv2ref.workspace.bootstrap_root",side_effect=create_after_bootstrap):
            with self.assertRaises(ContractError) as error:
                workspace_init_apply(self.source,self.target,preview["request"],confirm_token=preview["confirm_token"])
        self.assertEqual([True],calls);self.assertEqual("HV2-WORKSPACE-PRODUCT",error.exception.code)
        self.assertEqual("launcher without durable init receipt",error.exception.message)
        self.assertEqual(user_launcher,(self.target/"hv2").read_bytes())
        self.assertTrue((self.target/".hrn/product/init-plan.json").is_file())
        self.assertFalse((self.target/".hrn/product/binding.json").exists())
        after=exact_snapshot(self.target)
        for name,value in before.items():self.assertEqual(value,after[name],name)
        status=workspace_status(self.target);self.assertEqual("partial",status["classification"])
        self.assertNotIn("documentation_root",status);self.assertIn("manual preservation",status["next_action"])
        error=json.loads(self.apply_init(preview,recover=True,expected=65).stdout)
        self.assertEqual("launcher without durable init receipt",error["message"])
        self.assertEqual(after,exact_snapshot(self.target))

    def test_detach_installed_git_and_source_nongit_preserve_truth_and_project(self):
        for git in (False,True):
            with self.subTest(git=git):
                self.target=self.base/("git" if git else "nongit");self.target.mkdir();(self.target/"a").write_bytes(b"before\n")
                (self.target/"authored.md").write_text("project-authored document\n");(self.target/".env").write_text("DISPOSABLE_SECRET_SENTINEL=fixture\n")
                if git:subprocess.run(["git","init","-q",str(self.target)],check=True,capture_output=True)
                self.apply_init(self.preview());self.complete_work();before=exact_snapshot(self.target)
                preview=self.detach_preview(installed=git);self.assertEqual(before,exact_snapshot(self.target))
                result=self.detach_apply(preview,installed=git);self.assertEqual("detached",result["classification"])
                self.assertFalse((self.target/"hv2").exists());self.assertFalse((self.target/".hrn/product").exists())
                after=exact_snapshot(self.target)
                for name,value in before.items():
                    if name=="hv2" or name.startswith(".hrn/product/") or name==".hrn/product":continue
                    self.assertEqual(value,after[name],name)
                raw=(self.target/".hrn/detached.json").read_bytes();receipt=json.loads(raw)
                self.assertEqual(preview["request"],receipt["plan"]);self.assertIsNone(receipt["result_binding_ref"])
                self.assertNotIn(b"DISPOSABLE_SECRET_SENTINEL",raw)
                status=json.loads(self.call(["status","--target",self.target]).stdout)
                self.assertEqual("detached",status["classification"]);self.assertEqual("verified",status["record_verification"])
                self.assertNotIn("documentation_root",status)
                plain=self.plain_detach();self.assertEqual("detached",plain["classification"])
                self.assertEqual(2,len(plain["selected"]));self.assertFalse(plain["mutation_authorized"])
                self.assertEqual("not-reimplemented",plain["full_record_semantics"])
                before=exact_snapshot(self.target);self.detach_apply(preview,recover=True)
                self.assertEqual(before,exact_snapshot(self.target))

    def test_detach_each_removal_phase_is_pending_until_product_is_absent(self):
        for point in ("after-receipt","after-launcher","after-file","after-files","after-directory","after-product"):
            with self.subTest(point=point):
                self.target=self.base/point;self.target.mkdir();self.apply_init(self.preview());self.accept_intent()
                preview=self.detach_preview();self.detach_apply(preview,point=point,expected=75)
                complete=point=="after-product"
                result=json.loads(self.call(["status","--target",self.target],expected=0 if complete else 14).stdout)
                self.assertEqual("detached" if complete else "partial",result["classification"])
                self.assertNotIn("documentation_root",result)
                self.assertEqual(result["classification"],self.plain_detach(expected=0 if complete else 14)["classification"])
                if point=="after-receipt":
                    self.assertTrue((self.target/"hv2").exists());self.assertTrue((self.target/".hrn/product/binding.json").exists())
                    before=exact_snapshot(self.target);self.installed(["intent","draft"],self.draft(),expected=65);self.assertEqual(before,exact_snapshot(self.target))
                self.detach_apply(preview,recover=True);self.assertEqual("detached",self.plain_detach()["classification"])

    def test_detach_refuses_pending_work_intent_and_product(self):
        for form in ("work","intent","product"):
            with self.subTest(form=form):
                self.target=self.base/form;self.target.mkdir();(self.target/"a").write_bytes(b"before\n");self.apply_init(self.preview())
                if form=="work":
                    self.complete_work();home=self.target/".hrn/work/work-a";current=json.loads((home/"current.json").read_bytes())
                    selection=json.loads((home/"selections"/(current["selection_ref"]["id"]+".json")).read_bytes())
                    current["selection_ref"]=selection["parent_selection_ref"];(home/"current.json").write_bytes(canonical_json_bytes(current))
                elif form=="intent":self.accept_intent();(self.target/".hrn/intents/intent-a/current.json").unlink()
                else:
                    self.candidate=self.switch_candidate();up=self.switch_preview();self.switch_apply(up,point="after-receipt",expected=75)
                before=exact_snapshot(self.target);self.detach_preview(expected=65);self.assertEqual(before,exact_snapshot(self.target))
                self.assertFalse((self.target/".hrn/detached.json").exists())

    def test_detach_preview_drift_and_unsafe_files_are_preserved(self):
        for form in ("truth","launcher","unknown","symlink","hardlink","token"):
            with self.subTest(form=form):
                self.target=self.base/form;self.target.mkdir();self.apply_init(self.preview());preview=self.detach_preview()
                if form=="truth":self.accept_intent()
                elif form=="launcher":(self.target/"hv2").write_bytes(b"user changed launcher")
                elif form=="unknown":(self.target/".hrn/product/user-data").mkdir()
                elif form=="symlink":(self.target/"hv2").unlink();(self.target/"hv2").symlink_to(self.source/"hv2")
                elif form=="hardlink":
                    from hv2ref.product import verify_workspace_product
                    release=Path(verify_workspace_product(self.target)["release_path"]);(self.target/"hv2").unlink();os.link(release/"payload/hv2",self.target/"hv2")
                else:preview["confirm_token"]="wrong"
                before=exact_snapshot(self.target);self.detach_apply(preview,expected=65);self.assertEqual(before,exact_snapshot(self.target))
                self.assertFalse((self.target/".hrn/detached.json").exists())

    def test_detach_recovery_refuses_unknown_torn_drift_and_nonprefix_loss(self):
        for form in ("unknown","torn","truth","ignore","nonprefix","remaining"):
            with self.subTest(form=form):
                self.target=self.base/form;self.target.mkdir();self.apply_init(self.preview());self.accept_intent();preview=self.detach_preview()
                self.detach_apply(preview,point="after-receipt",expected=75)
                if form=="unknown":(self.target/".hrn/product/extra").mkdir()
                elif form=="torn":(self.target/".hrn/detached.json").write_bytes(b"{")
                elif form=="truth":(self.target/".hrn/intents/intent-a/identity.json").write_bytes(b"{}\n")
                elif form=="ignore":(self.target/".hrn/.gitignore").write_bytes(b"*\n")
                elif form=="nonprefix":(self.target/".hrn/product/binding.json").unlink()
                else:(self.target/"hv2").write_bytes(b"new launcher edits")
                before=exact_snapshot(self.target);self.detach_apply(preview,recover=True,expected=65)
                self.assertEqual(before,exact_snapshot(self.target));self.plain_detach(expected=10)
                self.call(["status","--target",self.target],expected=10)

    def test_detach_invalid_plan_cannot_delete_project_or_preserved_paths(self):
        import copy
        self.apply_init(self.preview());preview=self.detach_preview()
        for form in ("outside","truth","candidate","preserve","binding","schema","null"):
            bad=copy.deepcopy(preview);plan=bad["request"]
            if form=="outside":plan["remove"][0]["path"]="../outside"
            elif form=="truth":plan["remove"][0]["path"]=".hrn/format.json"
            elif form=="candidate":plan["candidate_release"]={}
            elif form=="preserve":plan["preserve"]=[]
            elif form=="binding":plan["expected_binding_ref"]["sha256"]="0"*64
            elif form=="schema":plan["schema_version"]=True
            else:bad["request"]=None
            bad["confirm_token"]=hashlib.sha256(canonical_json_bytes(bad["request"])).hexdigest()[:16]
            before=exact_snapshot(self.target);self.detach_apply(bad,expected=65);self.assertEqual(before,exact_snapshot(self.target))

    def test_detach_completed_state_is_readable_after_git_clone_without_product(self):
        subprocess.run(["git","init","-q",str(self.target)],check=True,capture_output=True)
        self.apply_init(self.preview());self.complete_work();preview=self.detach_preview();self.detach_apply(preview)
        subprocess.run(["git","-C",str(self.target),"add","."],check=True,capture_output=True)
        subprocess.run(["git","-C",str(self.target),"-c","user.name=Fixture","-c","user.email=fixture@example.invalid","commit","-qm","detached fixture"],check=True,capture_output=True)
        clone=self.base/"clone";subprocess.run(["git","clone","-q",str(self.target),str(clone)],check=True,capture_output=True)
        self.target=clone;before=exact_snapshot(self.target)
        self.assertEqual("detached",self.plain_detach()["classification"])
        self.assertEqual("detached",json.loads(self.call(["status","--target",self.target]).stdout)["classification"])
        self.detach_apply(preview,recover=True,expected=65);self.assertEqual(before,exact_snapshot(self.target))

    def test_detach_cannot_be_revived_by_init_or_exact_repair(self):
        self.apply_init(self.preview());initial=self.preview();preview=self.detach_preview();self.detach_apply(preview)
        before=exact_snapshot(self.target)
        self.apply_init(initial,recover=True,expected=65)
        self.call(["init","--profile","worker-1","--target",self.target,"--source",self.source,"--authority-home-id","other","--operation-id","other","--observed-at",self.TIME],expected=65)
        self.repair_preview(expected=65)
        self.assertEqual(before,exact_snapshot(self.target))

    def test_detach_without_receipt_is_degraded_and_unknown_format_not_pass(self):
        for form in ("absent","version","extra"):
            with self.subTest(form=form):
                self.target=self.base/form;self.target.mkdir();self.apply_init(self.preview());preview=self.detach_preview();self.detach_apply(preview)
                if form=="absent":(self.target/".hrn/detached.json").unlink()
                else:
                    path=self.target/".hrn/format.json";fmt=json.loads(path.read_bytes())
                    if form=="version":fmt["format_version"]=2
                    else:fmt["extra"]=True
                    path.write_bytes(canonical_json_bytes(fmt))
                before=exact_snapshot(self.target);self.plain_detach(expected=10)
                self.call(["status","--target",self.target],expected=11 if form=="version" else 10)
                self.assertEqual(before,exact_snapshot(self.target))

    def test_detach_multiple_releases_remove_only_managed_files(self):
        self.apply_init(self.preview());self.candidate=self.switch_candidate();up=self.switch_preview();self.switch_apply(up)
        self.complete_work();preview=self.detach_preview();self.assertGreater(len(preview["request"]["remove"]),50)
        self.detach_apply(preview);self.assertEqual("detached",self.plain_detach()["classification"])
        self.assertEqual(b"after\n",(self.target/"a").read_bytes())

    def test_detach_new_truth_or_reappearing_product_invalidates_completed_receipt(self):
        for form in ("truth","product"):
            with self.subTest(form=form):
                self.target=self.base/form;self.target.mkdir();self.apply_init(self.preview());self.accept_intent();preview=self.detach_preview();self.detach_apply(preview)
                if form=="truth":(self.target/".hrn/intents/intent-a/unknown.json").write_bytes(b"{}\n")
                else:(self.target/".hrn/product").mkdir();(self.target/".hrn/product/unowned").write_bytes(b"preserve me")
                before=exact_snapshot(self.target);self.detach_apply(preview,recover=True,expected=65);self.assertEqual(before,exact_snapshot(self.target));self.plain_detach(expected=10)

    def test_detach_receipt_must_be_git_visible_before_any_removal(self):
        subprocess.run(["git","init","-q",str(self.target)],check=True,capture_output=True)
        self.apply_init(self.preview());preview=self.detach_preview()
        (self.target/".gitignore").write_text("/.hrn/detached.json\n")
        before=exact_snapshot(self.target);self.detach_apply(preview,expected=65);self.assertEqual(before,exact_snapshot(self.target))

    def test_detach_recovery_requires_same_plan_and_explicit_source(self):
        import copy
        self.apply_init(self.preview());preview=self.detach_preview();self.detach_apply(preview,point="after-receipt",expected=75)
        before=exact_snapshot(self.target);self.detach_apply(preview,expected=65)
        bad=copy.deepcopy(preview);bad["request"]["operation_id"]="another";bad["confirm_token"]=hashlib.sha256(canonical_json_bytes(bad["request"])).hexdigest()[:16]
        self.detach_apply(bad,recover=True,expected=65);self.assertEqual(before,exact_snapshot(self.target));self.detach_apply(preview,recover=True)


    def test_detach_and_repair_source_module_dispatch_is_defined_before_main(self):
        self.apply_init(self.preview());(self.target/"hv2").chmod(0o644)
        result=subprocess.run([sys.executable,"-B","-m","hv2ref.cli","repair","--target",str(self.target),"--source",str(self.source),
                               "--backup",str(self.base/"backup"),"--operation-id","repair-a","--observed-at",self.TIME],capture_output=True,timeout=45)
        self.assertEqual(0,result.returncode,(result.stdout+result.stderr).decode());self.repair_apply(json.loads(result.stdout))
        result=subprocess.run([sys.executable,"-B","-m","hv2ref.cli","detach","--profile","worker-1","--target",str(self.target),
                               "--operation-id","detach-a","--observed-at",self.TIME],capture_output=True,timeout=45)
        self.assertEqual(0,result.returncode,(result.stdout+result.stderr).decode());self.assertEqual("preview",json.loads(result.stdout)["classification"])


    def test_contract_cli_classification_and_future_format_preserve_target(self):
        self.apply_init(self.preview());before=exact_snapshot(self.target)
        self.installed(["work","apply"],expected=2)
        self.installed(["work","publish"],{},expected=65)
        self.assertEqual(before,exact_snapshot(self.target))
        fmt=self.target/".hrn/format.json";original=json.loads(fmt.read_bytes())
        for change,code,classification in (({"future":True},10,"degraded"),({"format_version":2},11,"incompatible")):
            fmt.write_bytes(canonical_json_bytes({**original,**change}));before=exact_snapshot(self.target)
            result=self.call(["status","--target",self.target],expected=code)
            self.assertEqual(json.loads(result.stdout)["classification"],classification)
            self.installed(["intent","draft"],self.draft(),expected=65)
            self.assertEqual(before,exact_snapshot(self.target))
        fmt.write_bytes(canonical_json_bytes(original))

    def test_contract_detached_truth_stays_readable_but_writers_refuse(self):
        from hv2ref.work import WorkStore, read_work
        self.apply_init(self.preview());self.complete_work();self.detach_apply(self.detach_preview())
        before=exact_snapshot(self.target)
        self.assertEqual(read_work(self.target,"work-a")["state"],"completed")
        with self.assertRaises(ContractError):
            WorkStore(self.target).prepare("work-a",action="accept",actor="owner",reason="cannot revive",request_id="after-detach",observed_at=self.TIME)
        self.call(["rollback","--profile","worker-1","--target",self.target,"--operation-id","after-detach","--observed-at",self.TIME],expected=65)
        self.assertEqual(before,exact_snapshot(self.target))


class InventoryDeclarationTests(unittest.TestCase):
    """Read-only release/window boundary; worker lifecycle is qualified separately."""

    def read_window(self, value, *, legacy=False):
        from hv2ref.product import _launcher_inventory_window
        return _launcher_inventory_window(value, allow_legacy=legacy)

    def test_worker_literal_and_legacy_absence(self):
        self.assertEqual(self.read_window(b'WORKSPACE_INVENTORY_ID = "worker-1"\n'), "worker-1")
        self.assertEqual(self.read_window(b'print("legacy")\n', legacy=True), "human-1")
        with self.assertRaises(ContractError):
            self.read_window(b'print("legacy")\n')

    def test_candidate_code_is_not_executed(self):
        data = b'WORKSPACE_INVENTORY_ID = "worker-1"\nraise RuntimeError("must not execute")\n'
        self.assertEqual(self.read_window(data), "worker-1")

    def test_unknown_dynamic_duplicate_and_nested_declarations_refused(self):
        cases = [
            'WORKSPACE_INVENTORY_ID = "human-1"',
            'WORKSPACE_INVENTORY_ID = "worker-2"',
            'WORKSPACE_INVENTORY_ID = str("worker-1")',
            'if True:\n    WORKSPACE_INVENTORY_ID = "worker-1"',
            'WORKSPACE_INVENTORY_ID = "worker-1"\nWORKSPACE_INVENTORY_ID = "worker-1"',
        ]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ContractError):
                self.read_window(case.encode(), legacy=True)

    def test_other_binding_forms_refused(self):
        name = "WORKSPACE_INVENTORY_ID"
        forms = [
            f'{name}, other = ("worker-1", 1)', f'{name}: str = "worker-1"',
            f'{name} += "x"', f'del {name}', f'import os as {name}',
            f'from os import path as {name}', f'def f():\n    global {name}',
            f'({name} := "worker-1")', f'for {name} in []:\n    pass',
            f'with open("x") as {name}:\n    pass',
            f'match value:\n    case {{"x": {name}}}: pass',
            f'match value:\n    case [*{name}]: pass',
            f'match value:\n    case {{**{name}}}: pass',
            f'try: pass\nexcept Exception as {name}: pass',
            f'def {name}(): pass', f'class {name}: pass', f'def f({name}): pass',
            f'def f[{name}](): pass', f'def f[**{name}](): pass',
            f'def f[*{name}](): pass',
        ]
        for form in forms:
            for prefix in ('', f'{name} = "worker-1"\n'):
                with self.subTest(form=form, prefix=bool(prefix)), self.assertRaises(ContractError):
                    self.read_window((prefix + form).encode(), legacy=True)

    def test_oversized_malformed_and_parser_failures_refused(self):
        for data in (b'#' * (1024 * 1024 + 1), b'if (', b'\x00', 'not bytes'):
            with self.subTest(data_type=type(data)), self.assertRaises(ContractError):
                self.read_window(data, legacy=True)
        for error in (SyntaxError, RecursionError, MemoryError, ValueError):
            with self.subTest(error=error), mock.patch('hv2ref.product.ast.parse', side_effect=error), self.assertRaises(ContractError):
                self.read_window(b'pass', legacy=True)

    def write_release(self, root, launcher):
        from hv2ref.product import workspace_candidate
        candidate = workspace_candidate(source_root())
        candidate['payload']['hv2'] = launcher
        inventory = candidate['inventory']
        inventory['inventory_id'] = 'human-1'
        for entry in inventory['entries']:
            data = candidate['payload'][entry['path']]
            entry.update(sha256=hashlib.sha256(data).hexdigest(), size_bytes=len(data))
        raw = canonical_json_bytes(inventory)
        release = root / ('product-release-' + hashlib.sha256(raw).hexdigest()[:24])
        for name, data in candidate['payload'].items():
            p = release / 'payload' / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        (release / 'inventory.json').write_bytes(raw)
        return release

    def test_old_exact_release_remains_readable(self):
        from hv2ref.product import verify_workspace_release
        with tempfile.TemporaryDirectory() as tmp:
            release = self.write_release(Path(tmp), b'print("old human launcher")\n')
            before = exact_snapshot(release)
            self.assertEqual(verify_workspace_release(release)['inventory']['inventory_id'], 'human-1')
            self.assertEqual(before, exact_snapshot(release))

    def test_rehashed_mispackaged_release_is_refused_without_writes(self):
        from hv2ref.product import verify_workspace_release
        with tempfile.TemporaryDirectory() as tmp:
            release = self.write_release(Path(tmp), b'WORKSPACE_INVENTORY_ID = "worker-1"\n')
            before = exact_snapshot(release)
            with self.assertRaisesRegex(ContractError, 'declaration differs'):
                verify_workspace_release(release)
            self.assertEqual(before, exact_snapshot(release))


class InventoryWindowLifecycleTests(unittest.TestCase):
    """Worker window lifecycle only; worker Work semantics are a separate gate."""

    TIME = "2026-01-01T00:00:00Z"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="window-lifecycle-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.target = self.root / "project"
        self.target.mkdir()
        self.source = source_root()

    def initialize(self, target=None):
        from hv2ref.product import workspace_init_preview, workspace_init_apply
        target = target or self.target
        preview = workspace_init_preview(self.source, target, authority_home_id="home-a", operation_id="init-a", created_at=self.TIME)
        return workspace_init_apply(self.source, target, preview['request'], confirm_token=preview['confirm_token'])

    def changed_source(self):
        from hv2ref.product import SERIAL_MANAGED_PATHS
        source = self.root / 'candidate'
        if source.exists(): return source
        for name in SERIAL_MANAGED_PATHS:
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.source / name, path)
        with (source / 'README.md').open('a') as f: f.write('\nCandidate fixture.\n')
        return source

    def update_preview(self, target=None):
        from hv2ref.product import workspace_switch_preview
        return workspace_switch_preview(target or self.target, action='update', source=self.changed_source(), operation_id='update-a', created_at=self.TIME)

    def test_candidate_declaration_binds_inventory(self):
        from hv2ref.product import workspace_candidate
        candidate = workspace_candidate(self.source)
        self.assertEqual('worker-1', candidate['inventory']['inventory_id'])
        self.assertEqual(27, len(candidate['inventory']['entries']))
        self.assertEqual(candidate['release_ref']['sha256'], hashlib.sha256(canonical_json_bytes(candidate['inventory'])).hexdigest())
        source = self.changed_source()
        launcher = source / 'hv2'
        launcher.write_bytes(launcher.read_bytes().replace(b'WORKSPACE_INVENTORY_ID = "worker-1"', b'# missing declaration'))
        with self.assertRaises(ContractError): workspace_candidate(source)

    def test_fresh_init_read_only_status_and_declared_window(self):
        from hv2ref.product import workspace_status
        self.initialize()
        before = exact_snapshot(self.target)
        result = workspace_status(self.target)
        self.assertEqual('pass', result['classification'])
        binding = load_json(self.target / '.hrn/product/binding.json')
        self.assertEqual('worker-1', binding['active_release']['inventory_id'])
        self.assertEqual(before, exact_snapshot(self.target))

    def test_source_profile_is_explicit_and_old_profile_refused(self):
        from hv2ref.cli import parser, run
        with self.assertRaises(SystemExit):
            parser().parse_args(['init', '--profile', 'human-1', '--target', str(self.target)])
        args = parser().parse_args(['init', '--target', str(self.target)])
        with self.assertRaisesRegex(ContractError, 'explicit worker-1'):
            run(args)
        self.assertEqual('worker-1', parser().parse_args(['init', '--profile', 'worker-1', '--target', str(self.target)]).profile)
        self.assertEqual([], list(self.target.iterdir()))

    def test_worker_window_round_trip_and_replay(self):
        from hv2ref.product import workspace_switch_preview, workspace_switch_apply, verify_workspace_product
        self.initialize()
        original = verify_workspace_product(self.target)['inventory']
        up = self.update_preview()
        workspace_switch_apply(self.target, up['request'], source=self.changed_source(), confirm_token=up['confirm_token'])
        down = workspace_switch_preview(self.target, action='rollback', source=None, operation_id='rollback-a', created_at=self.TIME)
        workspace_switch_apply(self.target, down['request'], confirm_token=down['confirm_token'])
        self.assertEqual(original, verify_workspace_product(self.target)['inventory'])
        before = exact_snapshot(self.target)
        self.assertEqual('replayed', workspace_switch_apply(self.target, down['request'], confirm_token=down['confirm_token'])['classification'])
        self.assertEqual(before, exact_snapshot(self.target))

    def test_downgrade_plan_refused_before_any_write(self):
        from hv2ref.product import workspace_switch_apply
        self.initialize()
        preview = self.update_preview()
        plan = preview['request']
        plan['candidate_release']['inventory_id'] = 'human-1'
        plan['action'] = 'rollback'
        before = exact_snapshot(self.target)
        with self.assertRaisesRegex(ContractError, 'switches only to worker-1'):
            workspace_switch_apply(self.target, plan, confirm_token=hashlib.sha256(canonical_json_bytes(plan)).hexdigest()[:16])
        self.assertEqual(before, exact_snapshot(self.target))

    def test_history_binding_cannot_regress_window(self):
        from hv2ref.product import _switch_binding_receipt
        from hv2ref.work import record_ref
        prior = {'record_type':'product-binding','schema_version':1,'authority_home_id':'home-a',
                 'active_release':{'id':'product-release-'+'a'*24,'sha256':'a'*64,'inventory_id':'worker-1'},
                 'prior_release':None,'operation_id':'prior-a'}
        plan = {'expected_binding_ref':record_ref(prior,'operation_id'),
                'candidate_release':{'id':'product-release-'+'b'*24,'sha256':'b'*64,'inventory_id':'human-1'},
                'action':'update','authority_home_id':'home-a','operation_id':'next-a'}
        with self.assertRaisesRegex(ContractError, 'history cannot return'):
            _switch_binding_receipt(plan, prior)

    def test_update_prefix_recovery_preserves_truth(self):
        from hv2ref.product import workspace_switch_apply, verify_workspace_product
        from hv2ref.errors import InjectedCrash
        for point in ('after-receipt','after-staged-inventory','after-staged-payload','after-release','after-launcher','after-binding'):
            with self.subTest(point=point):
                target = self.root / point
                target.mkdir();self.initialize(target)
                truth = (target / '.hrn/format.json').read_bytes()
                preview = self.update_preview(target)
                with self.assertRaises(InjectedCrash):
                    workspace_switch_apply(target, preview['request'], source=self.changed_source(), confirm_token=preview['confirm_token'], inject_at=point)
                result = workspace_switch_apply(target, preview['request'], source=self.changed_source(), confirm_token=preview['confirm_token'], recover=True)
                self.assertIn(result['classification'], ('updated','replayed'))
                self.assertEqual(truth, (target / '.hrn/format.json').read_bytes())
                self.assertEqual('worker-1', verify_workspace_product(target)['inventory']['inventory_id'])

    def test_exact_repair_and_detach(self):
        from hv2ref.product import workspace_repair_preview, workspace_repair_apply, workspace_detach_preview, workspace_detach_apply, workspace_detached_status
        self.initialize()
        truth = (self.target / '.hrn/format.json').read_bytes()
        (self.target / 'hv2').write_bytes(b'damaged\n')
        preview = workspace_repair_preview(self.source,self.target,self.root/'backup',operation_id='repair-a',created_at=self.TIME)
        workspace_repair_apply(self.source,self.target,preview['request'],confirm_token=preview['confirm_token'])
        self.assertEqual((self.source / 'hv2').read_bytes(), (self.target / 'hv2').read_bytes())
        preview = workspace_detach_preview(self.target,operation_id='detach-a',created_at=self.TIME)
        workspace_detach_apply(self.target,preview['request'],confirm_token=preview['confirm_token'])
        self.assertEqual('detached',workspace_detached_status(self.target)['classification'])
        self.assertEqual(truth,(self.target/'.hrn/format.json').read_bytes())

    def test_serial_window_is_not_revived_by_root_reader(self):
        from hv2ref.workspace import _validate_plan_shape
        self.initialize()
        plan = load_json(self.target / '.hrn/product/init-plan.json')
        plan['candidate_release']['inventory_id'] = 'serial-1'
        with self.assertRaises(ContractError): _validate_plan_shape(plan)


if __name__ == "__main__":
    unittest.main()
