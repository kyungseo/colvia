"""Raw checkout evidence with a bounded unchanged explicit CRLF exception."""
from __future__ import annotations

import json
import unittest

from hv2ref.errors import ContractError, InjectedCrash

from hv2ref.work import make_manifest, read_work, snapshot
import test_worktree_execution as fixtures


class UnchangedCrlfTests(unittest.TestCase):
    def setUp(self):
        fixtures.WorkerPublicationTests.setUp(self)
        from hv2ref.work import WorkStore
        # Explicit window double for proof tests; installed cases are separate.
        self.store = WorkStore(self.target, lambda target: {
            "binding_ref": self.binding.copy(), "launcher_sha256": None,
            "inventory_id": "checkout-1"})
    git = fixtures.WorkerPublicationTests.git
    commit_control = fixtures.WorkerPublicationTests.commit_control
    bind = fixtures.WorkerPublicationTests.bind
    baseline = fixtures.WorkerPublicationTests.baseline
    start_and_result = fixtures.WorkerPublicationTests.start_and_result
    accept_intent = fixtures.WorkerPublicationTests.accept_intent
    proposal = fixtures.WorkerPublicationTests.proposal
    publish = fixtures.WorkerPublicationTests.publish
    prepare = fixtures.WorkerPublicationTests.prepare
    apply = fixtures.WorkerPublicationTests.apply
    bytes = fixtures.WorkerPublicationTests.bytes

    def crlf_input(self):
        (self.target / ".gitattributes").write_bytes(b"*.bat text eol=crlf\n")
        (self.target / "unchanged.bat").write_bytes(b"@echo off\r\necho fixture\r\n")

    def test_unchanged_crlf_start_submit_accept_keeps_exact_checkout_bytes(self):
        self.crlf_input()
        raw = (self.target / "unchanged.bat").read_bytes()
        result = self.start_and_result()
        self.assertEqual(raw, (self.worker / "unchanged.bat").read_bytes())
        self.assertNotEqual(raw.decode(), self.git(self.target, "show", "retained-base:unchanged.bat"))
        self.assertEqual("review", self.publish(result, worker=self.worker)["state"])
        self.assertEqual("completed", self.apply(self.prepare())["state"])
        self.assertEqual(raw, (self.target / "unchanged.bat").read_bytes())
        self.assertEqual(result[1]["result"], snapshot(self.target))

    def baseline_from_current(self, scope=None):
        scope = scope or ["a"]
        oid = self.git(self.target, "rev-parse", "HEAD")
        self.git(self.target, "branch", "-f", "retained-base", oid)
        tree = snapshot(self.target)
        manifest = make_manifest(tree, tree, scope=scope, base_commit=oid, candidate_commit=oid,
                                 base_retention_ref="refs/heads/retained-base", candidate_retention_ref="refs/heads/retained-base")
        proposal = self.proposal(); proposal[0]["scope"] = scope
        return self.bind(proposal, manifest)

    def refused_start_unchanged(self, proposal):
        before = self.bytes()
        with self.assertRaises(ContractError):
            self.publish(proposal)
        after = self.bytes()
        # A first writer may create its ordinary empty scratch lock on refusal.
        # Project content, authority and every pre-existing byte must stay exact.
        if ".hrn/locks/writer.lock" not in before:
            self.assertEqual(b"", after.pop(".hrn/locks/writer.lock", b""))
        self.assertEqual(before, after)
        self.assertFalse((self.target / ".hrn/work/work-a").exists())

    def canonical_blob_then_checkout(self, attributes):
        # Commit the blob before attributes so unsupported filters are never run
        # by fixture setup. Only the attributes file is staged afterward.
        (self.target / "unchanged.bat").write_bytes(b"@echo off\necho fixture\n")
        self.commit_control()
        (self.target / ".gitattributes").write_bytes(attributes)
        self.git(self.target, "add", ".gitattributes")
        self.git(self.target, "commit", "-qm", "fixture attributes")
        (self.target / "unchanged.bat").write_bytes(b"@echo off\r\necho fixture\r\n")

    def test_requires_explicit_committed_text_and_crlf(self):
        self.canonical_blob_then_checkout(b"*.bat eol=crlf\n")
        self.refused_start_unchanged(self.baseline_from_current())

    def test_global_attributes_cannot_supply_missing_committed_policy(self):
        self.canonical_blob_then_checkout(b"# no committed conversion rule\n")
        external = self.target.parent / "global-attributes"
        external.write_bytes(b"*.bat text eol=crlf\n")
        self.git(self.target, "config", "core.attributesFile", str(external))
        self.refused_start_unchanged(self.baseline_from_current())

    def test_info_attributes_cannot_supply_or_override_retained_policy(self):
        self.crlf_input(); proposal = self.baseline()
        (self.target / ".git/info/attributes").write_bytes(b"*.bat text eol=crlf\n")
        self.refused_start_unchanged(proposal)

    def test_unsupported_committed_attributes_do_not_execute_filter(self):
        self.canonical_blob_then_checkout(b"*.bat text eol=crlf filter=fixture\n")
        marker = self.target.parent / "filter-ran"
        self.git(self.target, "config", "filter.fixture.clean", "touch " + str(marker))
        self.git(self.target, "config", "filter.fixture.smudge", "touch " + str(marker))
        self.refused_start_unchanged(self.baseline_from_current())
        self.assertFalse(marker.exists())
        for unsupported in (b"working-tree-encoding=UTF-8", b"ident", b"crlf=input"):
            with self.subTest(attribute=unsupported.decode()):
                (self.target / ".gitattributes").write_bytes(b"*.bat text eol=crlf " + unsupported + b"\n")
                self.git(self.target, "add", ".gitattributes")
                self.git(self.target, "commit", "-qm", "unsupported fixture attribute")
                self.refused_start_unchanged(self.baseline_from_current())
                self.assertFalse(marker.exists())

    def test_external_filter_override_is_not_ignored_or_executed(self):
        self.crlf_input(); proposal = self.baseline()
        external = self.target.parent / "global-attributes"
        external.write_bytes(b"*.bat filter=fixture\n")
        marker = self.target.parent / "filter-ran"
        self.git(self.target, "config", "core.attributesFile", str(external))
        self.git(self.target, "config", "filter.fixture.clean", "touch " + str(marker))
        self.git(self.target, "config", "filter.fixture.smudge", "touch " + str(marker))
        self.refused_start_unchanged(proposal)
        self.assertFalse(marker.exists())

    def test_mixed_bare_cr_and_content_drift_are_not_normalized(self):
        self.crlf_input(); self.commit_control()
        for raw in (b"@echo off\r\necho fixture\n", b"@echo off\recho fixture\r", b"@echo off\r\necho changed\r\n"):
            with self.subTest(raw=raw):
                (self.target / "unchanged.bat").write_bytes(raw)
                self.refused_start_unchanged(self.baseline_from_current())

    def edited_result(self, path, raw):
        self.crlf_input()
        start = self.baseline(); scope = sorted({"a", path}); start[0]["scope"] = scope
        self.publish(start)
        self.git(self.target, "worktree", "add", "-q", "-b", "retained-candidate", str(self.worker), start[1]["base_commit"])
        (self.worker / path).write_bytes(raw)
        self.git(self.worker, "add", path); self.git(self.worker, "commit", "-qm", "fixture result")
        manifest = make_manifest(start[1]["base"], snapshot(self.worker), scope=scope,
                                 base_commit=start[1]["base_commit"], candidate_commit=self.git(self.worker, "rev-parse", "HEAD"),
                                 base_retention_ref="refs/heads/retained-base", candidate_retention_ref="refs/heads/retained-candidate")
        result = self.proposal("submit-result"); result[0]["scope"] = scope
        return self.bind(result, manifest)

    def test_changed_crlf_file_is_still_refused_without_record_or_content_write(self):
        result = self.edited_result("unchanged.bat", b"@echo off\r\necho changed\r\n")
        before = self.bytes(); graph = read_work(self.target, "work-a")
        with self.assertRaises(ContractError):
            self.publish(result, worker=self.worker)
        self.assertEqual(before, self.bytes()); self.assertEqual(graph, read_work(self.target, "work-a"))

    def test_committed_attribute_change_blocks_exception_even_if_effective_rule_matches(self):
        result = self.edited_result(".gitattributes", b"*.bat text eol=crlf\n# changed policy bytes\n")
        before = self.bytes()
        with self.assertRaises(ContractError):
            self.publish(result, worker=self.worker)
        self.assertEqual(before, self.bytes())

    def test_nested_unicode_path_uses_nul_delimited_attribute_observations(self):
        self.crlf_input()
        directory = self.target / "nested tools"; directory.mkdir()
        path = directory / "한글 script.bat"
        (self.target / "unchanged.bat").rename(path)
        raw = path.read_bytes()
        result = self.start_and_result(); self.publish(result, worker=self.worker)
        self.assertEqual("completed", self.apply(self.prepare())["state"])
        self.assertEqual(raw, path.read_bytes())

    def test_shared_blob_does_not_share_attribute_permission_between_paths(self):
        self.crlf_input()
        other = self.target / "no-conversion.txt"
        other.write_bytes(b"@echo off\necho fixture\n")
        self.commit_control()
        other.write_bytes(b"@echo off\r\necho fixture\r\n")
        self.refused_start_unchanged(self.baseline_from_current())

    def test_lf_and_binary_entries_remain_byte_exact(self):
        self.crlf_input()
        binary = b"\x00\r\n\xff\x80binary\n"
        (self.target / "asset.bin").write_bytes(binary)
        result = self.start_and_result(); self.publish(result, worker=self.worker)
        self.assertEqual("completed", self.apply(self.prepare())["state"])
        self.assertEqual(binary, (self.target / "asset.bin").read_bytes())
        self.assertEqual(b"worker result\n", (self.target / "a").read_bytes())
        self.assertEqual(result[1]["result"], snapshot(self.target))

    def test_recovery_retains_crlf_and_refuses_outside_drift(self):
        self.crlf_input(); result = self.start_and_result(); self.publish(result, worker=self.worker)
        prepared = self.prepare(); raw = (self.target / "unchanged.bat").read_bytes()
        with self.assertRaises(InjectedCrash):
            self.apply(prepared, inject_at="after-decision")
        (self.target / "unchanged.bat").write_bytes(raw.replace(b"fixture", b"drift"))
        before = self.bytes()
        with self.assertRaises(ContractError):
            self.apply(prepared)
        self.assertEqual(before, self.bytes())
        (self.target / "unchanged.bat").write_bytes(raw)
        self.worker.rename(self.worker.with_name("worker-unavailable"))
        self.assertEqual("completed", self.apply(prepared)["state"])
        self.assertEqual(raw, (self.target / "unchanged.bat").read_bytes())
        self.assertEqual(result[1]["result"], snapshot(self.target))

    def test_verified_window_gate_and_view_share_the_same_proof(self):
        from hv2ref.work import verify_worker_sources
        from hv2ref.view import _worker_inspection
        self.crlf_input(); manifest = self.baseline()[1]
        for window in (None, 'human-1', 'worker-1', 'umbrella-1', 'planning-1', 'unknown'):
            with self.subTest(window=window), self.assertRaises(ContractError):
                verify_worker_sources(self.target, manifest, verified_inventory_id=window)
            observed = _worker_inspection(self.target, manifest, {'launcher_sha256':None,'inventory':{'inventory_id':window}})
            self.assertIsNotNone(observed['source_error'])
        self.assertEqual({},verify_worker_sources(self.target, manifest, verified_inventory_id='checkout-1'))
        self.assertIsNone(_worker_inspection(self.target, manifest, {'launcher_sha256':None,'inventory':{'inventory_id':'checkout-1'}})['source_error'])
        self.assertEqual({},verify_worker_sources(self.target,manifest,verified_inventory_id='entry-1'))
        self.assertIsNone(_worker_inspection(self.target,manifest,{'launcher_sha256':None,'inventory':{'inventory_id':'entry-1'}})['source_error'])
        self.assertEqual({},verify_worker_sources(self.target,manifest,verified_inventory_id='delegation-1'))
        self.assertIsNone(_worker_inspection(self.target,manifest,{'launcher_sha256':None,'inventory':{'inventory_id':'delegation-1'}})['source_error'])

    def test_empty_info_attributes_allowed_and_symlink_refused(self):
        self.crlf_input(); proposal = self.baseline()
        info = self.target/'.git/info/attributes'; info.write_bytes(b'')
        from hv2ref.work import verify_worker_sources
        self.assertEqual({},verify_worker_sources(self.target,proposal[1],verified_inventory_id='checkout-1'))
        outside=self.target.parent/'empty-attrs';outside.write_bytes(b'')
        info.unlink();info.symlink_to(outside)
        self.refused_start_unchanged(proposal)

    def test_core_conversion_and_text_auto_do_not_supply_explicit_policy(self):
        self.canonical_blob_then_checkout(b'*.bat text=auto eol=crlf\n')
        self.refused_start_unchanged(self.baseline_from_current())
        (self.target/'.gitattributes').write_bytes(b'# no policy\n')
        self.git(self.target,'add','.gitattributes');self.git(self.target,'commit','-qm','remove policy')
        self.git(self.target,'config','core.autocrlf','true')
        self.git(self.target,'config','core.eol','crlf')
        self.refused_start_unchanged(self.baseline_from_current())

    def test_mode_only_change_does_not_use_unchanged_exception(self):
        self.crlf_input();start=self.baseline();start[0]['scope']=['a','unchanged.bat'];self.publish(start)
        self.git(self.target,'worktree','add','-q','-b','retained-candidate',str(self.worker),start[1]['base_commit'])
        (self.worker/'unchanged.bat').chmod(0o755)
        self.git(self.worker,'update-index','--chmod=+x','unchanged.bat')
        self.git(self.worker,'commit','-qm','mode fixture')
        m=make_manifest(start[1]['base'],snapshot(self.worker),scope=start[0]['scope'],base_commit=start[1]['base_commit'],candidate_commit=self.git(self.worker,'rev-parse','HEAD'),base_retention_ref='refs/heads/retained-base',candidate_retention_ref='refs/heads/retained-candidate')
        result=self.proposal('submit-result');result[0]['scope']=start[0]['scope']
        before=self.bytes()
        with self.assertRaises(ContractError):self.publish(self.bind(result,m),worker=self.worker)
        self.assertEqual(before,self.bytes())

    def test_cr_and_nul_blobs_are_ineligible_for_conversion_exception(self):
        from hv2ref.work import _unchanged_crlf_matches
        import hashlib
        for blob in (b'x\r\ny\n',b'x\x00y\n'):
            raw=blob.replace(b'\n',b'\r\n');entry={'path':'unchanged.bat','kind':'file','mode':'file','size_bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
            entries={'base':{'unchanged.bat':entry},'result':{'unchanged.bat':entry}}
            tables={'pre':{'unchanged.bat':('100644','a'*40)},'post':{'unchanged.bat':('100644','a'*40)}}
            self.assertFalse(_unchanged_crlf_matches(self.target,{},tables,entries,'unchanged.bat',blob,entry))

    def test_missing_git_capability_refuses_without_writes(self):
        from unittest import mock
        import hv2ref.work as work
        self.crlf_input();proposal=self.baseline();original=work._git
        def no_source(target,*args,**kwargs):
            if 'check-attr' in args:raise ContractError('HV2-WORK','simulated unsupported check-attr --source')
            return original(target,*args,**kwargs)
        with mock.patch.object(work,'_git',side_effect=no_source):self.refused_start_unchanged(proposal)

    def test_pending_attribute_drift_refuses_resume_then_restoration_completes(self):
        self.crlf_input();result=self.start_and_result();self.publish(result,worker=self.worker);ticket=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(ticket,inject_at='after-decision')
        info=self.target/'.git/info/attributes';info.write_bytes(b'*.bat -text\n');before=self.bytes()
        with self.assertRaises(ContractError):self.apply(ticket)
        self.assertEqual(before,self.bytes());info.unlink()
        self.assertEqual('completed',self.apply(ticket)['state'])
        info.write_bytes(b'*.bat -text\n');before=self.bytes();graph=read_work(self.target,'work-a')
        self.assertEqual(graph,self.apply(ticket));self.assertEqual(before,self.bytes())

    def test_pending_capability_drift_refuses_then_exact_resume_completes(self):
        from unittest import mock
        import hv2ref.work as work
        self.crlf_input();result=self.start_and_result();self.publish(result,worker=self.worker);ticket=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(ticket,inject_at='after-decision')
        original=work._git
        def no_source(target,*args,**kwargs):
            if 'check-attr' in args:raise ContractError('HV2-WORK','simulated unsupported check-attr --source')
            return original(target,*args,**kwargs)
        before=self.bytes()
        with mock.patch.object(work,'_git',side_effect=no_source),self.assertRaises(ContractError):self.apply(ticket)
        self.assertEqual(before,self.bytes())
        self.assertEqual('completed',self.apply(ticket)['state'])

    def test_pending_can_cancel_without_restoring_live_attributes_when_all_paths_pre(self):
        from hv2ref.work import record_ref
        self.crlf_input();result=self.start_and_result();self.publish(result,worker=self.worker);ticket=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(ticket,inject_at='after-decision')
        (self.target/'.git/info/attributes').write_bytes(b'*.bat -text\n')
        graph=read_work(self.target,'work-a');decision=graph['decisions'][graph['pending_decisions'][0]]
        cancel=self.prepare('reject',supersedes=record_ref(decision))
        self.assertFalse(self.apply(cancel)['pending_decisions'])
        self.assertEqual(b'before\n',(self.target/'a').read_bytes())

    def test_entry_window_capability_retains_exact_crlf_completion(self):
        self.store.runtime_check=lambda target:{'binding_ref':self.binding.copy(),'launcher_sha256':None,'inventory_id':'entry-1'}
        self.test_unchanged_crlf_start_submit_accept_keeps_exact_checkout_bytes()

    def test_delegation_window_capability_retains_exact_crlf_completion(self):
        # Keep the original checkout-1 and entry-1 doubles alongside the new window.
        self.store.runtime_check=lambda target:{'binding_ref':self.binding.copy(),'launcher_sha256':None,'inventory_id':'delegation-1'}
        self.test_unchanged_crlf_start_submit_accept_keeps_exact_checkout_bytes()


class InstalledUnchangedCrlfTests(unittest.TestCase):
    setUp = fixtures.InstalledWorkerPublicationTests.setUp
    TIME = fixtures.InstalledWorkerPublicationTests.TIME
    draft = fixtures.InstalledWorkerPublicationTests.draft
    accept_intent = fixtures.InstalledWorkerPublicationTests.accept_intent
    installed = fixtures.InstalledWorkerPublicationTests.installed
    preview = fixtures.InstalledWorkerPublicationTests.preview
    apply_init = fixtures.InstalledWorkerPublicationTests.apply_init
    call = fixtures.InstalledWorkerPublicationTests.call
    git = fixtures.InstalledWorkerPublicationTests.git
    prepare_worker_result = fixtures.InstalledWorkerPublicationTests.prepare_worker_result

    def test_installed_start_submit_accept_preserves_crlf_and_readable_history(self):
        (self.target / ".gitattributes").write_bytes(b"*.bat text eol=crlf\n")
        raw = b"@echo off\r\necho fixture\r\n"
        (self.target / "unchanged.bat").write_bytes(raw)
        prepared = self.prepare_worker_result()
        result = json.loads(self.installed(["work", "apply", "--confirm", prepared["confirm_token"]], prepared["ticket"]).stdout)
        self.assertEqual("completed", result["state"])
        self.assertEqual(raw, (self.target / "unchanged.bat").read_bytes())
        self.assertEqual("pass", json.loads(self.installed(["status"]).stdout)["classification"])
        view = self.installed(["view", "work", "work-a"]).stdout.decode().replace("\\_", "_")
        self.assertIn("Stored state: completed", view)
        self.assertIn("whole_result_matches: True", view)
        self.assertIn("retained_sources: verified local commit/blob observations", view)
