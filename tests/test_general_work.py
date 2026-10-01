from __future__ import annotations

import copy
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from hv2ref.errors import ContractError
from hv2ref.jsonio import canonical_json_bytes
from hv2ref.work import make_manifest, observe_recovery, project_path, snapshot, validate_manifest, validate_tree, preflight_changed_paths, verify_worker_sources


class ContentContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="hv2-content-")
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name).resolve()
        self.target = root / "target"
        self.target.mkdir()
        self.home = root / "home"
        self.home.mkdir()
        self.env = patch.dict(os.environ, {"HOME": str(self.home), "XDG_CONFIG_HOME": str(self.home / ".config")})
        self.env.start()
        self.addCleanup(self.env.stop)

    def git(self, *args):
        if args and args[0] == "commit":
            args = ("-c", "maintenance.auto=false", "-c", "gc.auto=0", *args)
        return subprocess.run(["git", "-C", str(self.target), *args], capture_output=True, check=True).stdout

    def init(self):
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")

    def write(self, path, data=b"one\n"):
        target = self.target / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return target

    def rehash(self, tree):
        tree["sha256"] = hashlib.sha256(canonical_json_bytes({k: v for k, v in tree.items() if k != "sha256"})).hexdigest()
        return tree

    def result(self):
        self.write("a")
        base = snapshot(self.target)
        self.write("a", b"two\n")
        result = snapshot(self.target)
        return make_manifest(base, result, scope=["a"])

    def test_non_git_membership_does_not_apply_ignore(self):
        self.write(".gitignore", b"build/\n")
        self.write("build/output")
        self.write(".hrn/truth.json")
        self.write("hv2")
        tree = snapshot(self.target)
        self.assertEqual([e["path"] for e in tree["entries"]], [".gitignore", "build/output", "hv2"])
        self.assertEqual(tree["ignore_fingerprint"], hashlib.sha256(b"no-git-v1").hexdigest())
        validate_tree(tree)

    def test_git_tracks_ignored_and_nonignored_untracked(self):
        self.init()
        self.write(".gitignore", b"*.log\n")
        self.write("tracked.log")
        self.git("add", "-f", "tracked.log")
        self.write("ignored.log")
        self.write("untracked")
        self.write(".hrn/truth.json")
        tree = snapshot(self.target)
        self.assertEqual([e["path"] for e in tree["entries"]], [".gitignore", "tracked.log", "untracked"])

    def test_deleted_tracked_is_absent_and_explicit_change(self):
        self.init()
        path = self.write("a")
        self.git("add", "a")
        base = snapshot(self.target)
        path.unlink()
        manifest = make_manifest(base, snapshot(self.target), scope=["a"])
        self.assertIsNone(manifest["changes"][0]["post"])
        self.assertEqual(manifest["changes"][0]["pre"]["path"], "a")

    def test_scope_never_limits_membership_and_outside_change_refused(self):
        manifest = self.result()
        self.write("outside")
        current = snapshot(self.target)
        self.assertFalse(observe_recovery(manifest, current)["whole_result_matches"])
        with self.assertRaises(ContractError):
            make_manifest(manifest["base"], current, scope=["a"])

    def test_new_ignored_output_does_not_stale_git_result(self):
        self.init()
        self.write(".gitignore", b"build/\n")
        manifest = self.result()
        self.write("build/output")
        self.assertTrue(observe_recovery(manifest, snapshot(self.target))["whole_result_matches"])

    def test_changed_gitignore_requires_new_baseline(self):
        self.init()
        self.write(".gitignore", b"build/\n")
        before = snapshot(self.target)
        self.write(".gitignore", b"other/\n")
        with self.assertRaises(ContractError):
            make_manifest(before, snapshot(self.target), scope=[".gitignore"])

    def test_info_exclude_change_is_bound_even_without_membership_change(self):
        self.init()
        self.write("a")
        before = snapshot(self.target)
        (self.target / ".git/info/exclude").write_text("unused-pattern\n")
        after = snapshot(self.target)
        self.assertEqual(before["entries"], after["entries"])
        self.assertNotEqual(before["ignore_fingerprint"], after["ignore_fingerprint"])

    def test_default_global_ignore_and_explicit_config_are_bound(self):
        self.init()
        self.write("a.tmp")
        before = snapshot(self.target)
        default = self.home / ".config/git/ignore"
        default.parent.mkdir(parents=True)
        default.write_text("*.tmp\n")
        after = snapshot(self.target)
        self.assertNotEqual(before["ignore_fingerprint"], after["ignore_fingerprint"])
        self.assertEqual(after["entries"], [])
        alternate = self.home / "rules"
        alternate.write_bytes(default.read_bytes())
        self.git("config", "core.excludesFile", str(alternate))
        self.assertEqual(after, snapshot(self.target))

    def test_ignore_source_paths_are_not_recorded(self):
        self.init()
        self.write("a")
        content = canonical_json_bytes(snapshot(self.target))
        self.assertNotIn(os.fsencode(self.home), content)
        self.assertNotIn(os.fsencode(self.target), content)

    def test_head_only_change_keeps_snapshot_and_reader_does_not_touch_index(self):
        self.init()
        self.write("a")
        self.git("add", "a")
        before = snapshot(self.target)
        self.git("commit", "-qm", "fixture")
        index = self.target / ".git/index"
        index_before = (index.read_bytes(), index.stat().st_mtime_ns)
        self.assertEqual(before, snapshot(self.target))
        self.assertEqual(index_before, (index.read_bytes(), index.stat().st_mtime_ns))
        self.assertFalse((self.target / ".git/index.lock").exists())
        self.assertFalse((self.target / ".hrn").exists())

    def test_launcher_only_excluded_with_exact_proof(self):
        self.write("hv2", b"launcher\n")
        digest = hashlib.sha256(b"launcher\n").hexdigest()
        self.assertEqual(len(snapshot(self.target)["entries"]), 1)
        self.assertEqual(snapshot(self.target, verified_launcher_sha256=digest)["entries"], [])
        with self.assertRaises(ContractError):
            snapshot(self.target, verified_launcher_sha256="0" * 64)

    def test_symlink_special_and_nested_git_are_not_silently_excluded(self):
        self.init()
        self.write(".gitignore", b"build/\n")
        self.write("a")
        link = self.target / "build/link"
        link.parent.mkdir()
        link.symlink_to(self.target / "a")
        with self.assertRaises(ContractError):
            snapshot(self.target)
        link.unlink()
        os.mkfifo(link)
        with self.assertRaises(ContractError):
            snapshot(self.target)
        link.unlink()
        (link.parent / ".git").mkdir()
        with self.assertRaises(ContractError):
            snapshot(self.target)

    def test_tracked_gitlink_is_refused(self):
        self.init()
        self.write("a")
        self.git("add", "a")
        self.git("commit", "-qm", "fixture")
        oid = self.git("rev-parse", "HEAD").strip().decode()
        self.git("update-index", "--add", "--cacheinfo", "160000," + oid + ",module")
        with self.assertRaises(ContractError):
            snapshot(self.target)

    def test_case_alias_and_non_nfc_paths_are_rejected(self):
        self.write("a/x")
        # Portable manifest counterexample; macOS commonly aliases actual paths.
        tree = snapshot(self.target)
        entry = copy.deepcopy(tree["entries"][0])
        entry["path"] = "A/y"
        tree["entries"].append(entry)
        self.rehash(tree)
        with self.assertRaises(ContractError):
            validate_tree(tree)
        for path in ["/a", "a/../b", "a//b", "./a", "a\\b", "a\x00", ".hrn/a", "nested/.git/config", "e\u0301"]:
            with self.subTest(path=path), self.assertRaises(ContractError):
                project_path(path)

    def test_tree_schema_digest_order_duplicate_bool_unknown_fail(self):
        self.write("a")
        self.write("b")
        tree = snapshot(self.target)
        variants = []
        t = copy.deepcopy(tree); t["policy_version"] = True; variants.append(t)
        t = copy.deepcopy(tree); t["entries"][0]["size_bytes"] = True; variants.append(t)
        t = copy.deepcopy(tree); t["extra"] = 0; variants.append(t)
        t = copy.deepcopy(tree); t["entries"].reverse(); variants.append(t)
        t = copy.deepcopy(tree); t["entries"].append(t["entries"][0]); variants.append(t)
        t = copy.deepcopy(tree); t["entries"][0]["path"] = "b/c"; variants.append(t)
        for variant in variants:
            self.rehash(variant)
            with self.subTest(variant=variant), self.assertRaises(ContractError):
                validate_tree(variant)
        tree["sha256"] = "0" * 64
        with self.assertRaises(ContractError):
            validate_tree(tree)

    def test_manifest_exact_diff_and_deep_copy(self):
        manifest = self.result()
        for change in [[], [{"path": "a", "pre": None, "post": None}]]:
            bad = copy.deepcopy(manifest); bad["changes"] = change
            with self.assertRaises(ContractError):
                validate_manifest(bad)
        base = copy.deepcopy(manifest["base"])
        clone = make_manifest(base, manifest["result"], scope=["a"])
        base["entries"].clear()
        self.assertTrue(clone["base"]["entries"])

    def test_worker_ref_shape_all_or_none_and_not_existence_claim(self):
        manifest = self.result()
        for fields in [{"base_commit": "1" * 40}, {"base_commit": "1" * 40, "candidate_commit": "2" * 40, "base_retention_ref": "refs/heads/base", "candidate_retention_ref": "refs/heads/../bad"}]:
            bad = {**manifest, **fields}
            with self.assertRaises(ContractError):
                validate_manifest(bad)
        manifest.update(base_commit="1" * 40, candidate_commit="2" * 64, base_retention_ref="refs/heads/base", candidate_retention_ref="refs/tags/candidate")
        validate_manifest(manifest)
        self.assertEqual(observe_recovery(manifest, manifest["base"])["authority_verification"], "required")

    def test_mode_only_change_is_a_result_change(self):
        path = self.write("a")
        path.chmod(0o644)
        base = snapshot(self.target)
        path.chmod(0o755)
        manifest = make_manifest(base, snapshot(self.target), scope=["a"])
        self.assertEqual(manifest["changes"][0]["pre"]["mode"], "100644")
        self.assertEqual(manifest["changes"][0]["post"]["mode"], "100755")

    def test_partial_apply_resume_whole_check_and_cancel_with_outside_drift(self):
        self.write("a"); self.write("b")
        base = snapshot(self.target)
        self.write("a", b"two\n"); self.write("b", b"two\n")
        manifest = make_manifest(base, snapshot(self.target), scope=["a", "b"])
        self.write("b")
        mixed = observe_recovery(manifest, snapshot(self.target))
        self.assertEqual(mixed["changed_paths"], {"a": "post", "b": "pre"})
        self.assertTrue(mixed["content_resume_possible"])
        self.assertFalse(mixed["whole_result_matches"])
        self.write("outside")
        self.assertFalse(observe_recovery(manifest, snapshot(self.target))["content_resume_possible"])
        self.write("a")
        cancel = observe_recovery(manifest, snapshot(self.target))
        self.assertTrue(cancel["all_changed_paths_pre"])
        self.assertTrue(cancel["outside_drift"])
        self.assertFalse(cancel["whole_result_matches"])

    def test_neither_pre_nor_post_is_never_resumable(self):
        manifest = self.result()
        self.write("a", b"third\n")
        report = observe_recovery(manifest, snapshot(self.target))
        self.assertFalse(report["content_resume_possible"])
        self.assertFalse(report["all_changed_paths_pre"])
        self.assertEqual(report["changed_paths"], {"a": "neither"})

    def test_missing_added_path_can_cancel_but_ignored_occupant_needs_live_preflight(self):
        self.init()
        self.write(".gitignore", b"*.cache\n")
        base = snapshot(self.target)
        self.write("new")
        manifest = make_manifest(base, snapshot(self.target), scope=["new"])
        (self.target / "new").unlink()
        self.assertTrue(observe_recovery(manifest, snapshot(self.target))["all_changed_paths_pre"])
        # The pure classifier deliberately does not authorize physical path writes.
        self.assertEqual(observe_recovery(manifest, snapshot(self.target))["authority_verification"], "required")

    def test_two_observations_must_agree(self):
        self.write("a")
        before = snapshot(self.target)
        self.write("a", b"two\n")
        after = snapshot(self.target)
        with patch("hv2ref.work._snapshot_once", side_effect=[before, after]), self.assertRaises(ContractError):
            snapshot(self.target)

    def test_linked_worktree_snapshot_is_read_only_and_has_no_authority_claim(self):
        self.init()
        self.write("a")
        self.git("add", "a")
        self.git("commit", "-qm", "fixture")
        # Disposable test target, not an agent-managed development checkout.
        linked = Path(self.temp.name).resolve() / "fixture-linked"
        self.git("worktree", "add", "--detach", str(linked), "HEAD")
        tree = snapshot(linked)
        self.assertEqual([e["path"] for e in tree["entries"]], ["a"])
        self.assertFalse((linked / ".hrn").exists())

    def test_physical_preflight_catches_ignored_occupant_for_added_path(self):
        self.init()
        self.write(".gitignore", b"*.cache\n")
        base = snapshot(self.target)
        self.write("new.cache")
        self.git("add", "-f", "new.cache")
        manifest = make_manifest(base, snapshot(self.target), scope=["new.cache"])
        self.git("rm", "--cached", "-f", "new.cache")
        self.write("new.cache", b"unreviewed occupant\n")
        report = observe_recovery(manifest, snapshot(self.target))
        self.assertTrue(report["all_changed_paths_pre"])
        self.assertEqual(preflight_changed_paths(self.target, manifest), {"new.cache": "neither"})

    def test_preflight_refuses_symlink_ancestor_and_launcher_diff(self):
        base = snapshot(self.target)
        self.write("dir/a")
        result = snapshot(self.target)
        manifest = make_manifest(base, result, scope=["dir/a"])
        (self.target / "dir/a").unlink()
        (self.target / "dir").rmdir()
        (self.target / "dir").symlink_to(self.home, target_is_directory=True)
        with self.assertRaises(ContractError):
            preflight_changed_paths(self.target, manifest)
        manifest = copy.deepcopy(manifest)
        manifest["result"]["entries"][0]["path"] = "hv2"
        self.rehash(manifest["result"])
        manifest["changes"][0]["path"] = "hv2"
        manifest["changes"][0]["post"]["path"] = "hv2"
        with self.assertRaises(ContractError):
            preflight_changed_paths(self.target, manifest, verified_launcher_sha256="0" * 64)

    def worker_manifest(self):
        self.init()
        self.write("a")
        self.git("add", "a")
        self.git("commit", "-qm", "base fixture")
        base_commit = self.git("rev-parse", "HEAD").strip().decode()
        self.git("tag", "base-fixture")
        base = snapshot(self.target)
        self.write("a", b"two\n")
        self.write("new")
        self.git("add", "a", "new")
        self.git("commit", "-qm", "candidate fixture")
        candidate = self.git("rev-parse", "HEAD").strip().decode()
        self.git("tag", "candidate-fixture")
        return make_manifest(base, snapshot(self.target), scope=["a", "new"], base_commit=base_commit, candidate_commit=candidate, base_retention_ref="refs/tags/base-fixture", candidate_retention_ref="refs/tags/candidate-fixture")

    def test_worker_sources_roundtrip_without_head_index_or_refs_mutation(self):
        manifest = self.worker_manifest()
        refs = self.git("show-ref")
        head = self.git("rev-parse", "HEAD")
        index = (self.target / ".git/index").read_bytes()
        sources = verify_worker_sources(self.target, manifest)
        self.assertEqual(sources, {"a": {"pre": b"one\n", "post": b"two\n"}, "new": {"pre": None, "post": b"one\n"}})
        self.assertEqual(self.git("show-ref"), refs)
        self.assertEqual(self.git("rev-parse", "HEAD"), head)
        self.assertEqual((self.target / ".git/index").read_bytes(), index)

    def test_missing_moved_retention_ref_or_mismatched_blob_fails(self):
        manifest = self.worker_manifest()
        self.git("tag", "-d", "candidate-fixture")
        with self.assertRaises(ContractError):
            verify_worker_sources(self.target, manifest)
        self.git("tag", "candidate-fixture", manifest["base_commit"])
        with self.assertRaises(ContractError):
            verify_worker_sources(self.target, manifest)
        self.git("tag", "-f", "candidate-fixture", manifest["candidate_commit"])
        manifest["result"]["entries"][0]["sha256"] = "0" * 64
        manifest["changes"][0]["post"]["sha256"] = "0" * 64
        self.rehash(manifest["result"])
        with self.assertRaises(ContractError):
            verify_worker_sources(self.target, manifest)

    def test_case_only_tracked_rename_never_silently_disappears(self):
        self.init()
        self.git("config", "core.ignorecase", "true")
        path = self.write("A")
        self.git("add", "A")
        self.git("commit", "-qm", "case fixture")
        path.rename(self.target / "temporary-name")
        (self.target / "temporary-name").rename(self.target / "a")
        with self.assertRaises(ContractError):
            snapshot(self.target)
        self.write("a", b"changed\n")
        with self.assertRaises(ContractError):
            snapshot(self.target)

    def test_gitignore_inside_parent_ignored_cache_does_not_change_policy(self):
        self.init()
        self.write(".gitignore", b".pytest_cache/\nbuild/\n")
        before = snapshot(self.target)
        self.write(".pytest_cache/.gitignore", b"*\n")
        self.write(".pytest_cache/value")
        self.write("build/vendor/.gitignore", b"*.log\n")
        self.assertEqual(before, snapshot(self.target))

    def test_self_ignoring_cache_policy_is_visible_and_not_rebaselined_silently(self):
        self.init()
        before = snapshot(self.target)
        self.write("cache/.gitignore", b"*\n")
        self.write("cache/value")
        after = snapshot(self.target)
        self.assertNotEqual(before["ignore_fingerprint"], after["ignore_fingerprint"])
        with self.assertRaisesRegex(ContractError, "human policy review"):
            make_manifest(before, after, scope=[])

    def test_noncanonical_ignore_spelling_is_explicitly_unsupported(self):
        self.init()
        self.write(".GITIGNORE", b"*.cache\n")
        with self.assertRaises(ContractError):
            snapshot(self.target)

    def test_promisor_and_alternates_fail_before_blob_read(self):
        manifest = self.worker_manifest()
        self.git("config", "remote.fixture.promisor", "true")
        with self.assertRaisesRegex(ContractError, "promisor"):
            verify_worker_sources(self.target, manifest)
        with self.assertRaisesRegex(ContractError, "promisor"):
            snapshot(self.target)
        self.git("config", "--unset", "remote.fixture.promisor")
        alternate = self.target / ".git/objects/info/alternates"
        alternate.parent.mkdir(parents=True, exist_ok=True)
        alternate.write_bytes(b"")
        with self.assertRaisesRegex(ContractError, "alternates"):
            verify_worker_sources(self.target, manifest)

    def test_exact_ref_not_dwim_and_replace_objects_disabled(self):
        manifest = self.worker_manifest()
        self.git("replace", manifest["candidate_commit"], manifest["base_commit"])
        self.assertEqual(verify_worker_sources(self.target, manifest)["a"]["post"], b"two\n")
        self.git("replace", "-d", manifest["candidate_commit"])
        self.git("branch", "refs/tags/candidate-fixture", manifest["candidate_commit"])
        self.git("tag", "-d", "candidate-fixture")
        with self.assertRaises(ContractError):
            verify_worker_sources(self.target, manifest)

    def test_group_execute_bit_does_not_disagree_with_git_mode(self):
        self.init()
        path = self.write("a")
        path.chmod(0o654)
        tree = snapshot(self.target)
        self.assertEqual(tree["entries"][0]["mode"], "100644")
        self.git("add", "a")
        self.assertTrue(self.git("ls-files", "--stage").startswith(b"100644 "))

    def test_external_ignore_symlink_hashes_contents_without_path_provenance(self):
        self.init()
        self.write("a.tmp")
        rules = self.home / "dotfile-rules"
        rules.write_text("*.tmp\n")
        link = self.home / ".config/git/ignore"
        link.parent.mkdir(parents=True)
        link.symlink_to(rules)
        tree = snapshot(self.target)
        self.assertEqual(tree["entries"], [])
        self.assertNotIn(os.fsencode(self.home), canonical_json_bytes(tree))
        rules.write_text("*.other\n")
        self.assertNotEqual(tree["ignore_fingerprint"], snapshot(self.target)["ignore_fingerprint"])

    def test_preflight_subdirectory_and_permission_fail_closed(self):
        manifest = self.result()
        child = self.target / "child"; child.mkdir()
        self.init()
        with self.assertRaises(ContractError):
            preflight_changed_paths(child, manifest)
        with patch("hv2ref.work._stable_file", side_effect=PermissionError), self.assertRaises(ContractError):
            preflight_changed_paths(self.target, manifest)

    def test_policy_drift_does_not_offer_content_only_pre_success(self):
        manifest = self.result()
        current = copy.deepcopy(manifest["base"])
        current["ignore_fingerprint"] = "0" * 64
        self.rehash(current)
        self.assertFalse(observe_recovery(manifest, current)["all_changed_paths_pre"])

    def test_symlinked_git_object_store_is_not_durable_control_evidence(self):
        manifest = self.worker_manifest()
        objects = self.target / ".git/objects"
        moved = self.home / "borrowed-objects"
        objects.rename(moved)
        objects.symlink_to(moved, target_is_directory=True)
        with self.assertRaisesRegex(ContractError, "object directory"):
            verify_worker_sources(self.target, manifest)

    def test_descendant_authority_is_not_outer_project_content(self):
        self.write("nested/.hrn/format.json", b"{}\n")
        with self.assertRaises(ContractError):
            snapshot(self.target)


class WorkerWholeSourceTests(unittest.TestCase):
    setUp = ContentContractTests.setUp
    git = ContentContractTests.git
    init = ContentContractTests.init
    write = ContentContractTests.write
    worker_manifest = ContentContractTests.worker_manifest
    rehash = ContentContractTests.rehash

    def test_extra_metadata_commit_is_not_hidden_by_manifest(self):
        manifest = self.worker_manifest()
        self.write(".hrn/work/hidden.json", b"hidden\n")
        self.git("add", ".hrn"); self.git("commit", "-qm", "hidden fixture")
        manifest["candidate_commit"] = self.git("rev-parse", "HEAD").strip().decode()
        self.git("tag", "-f", "candidate-fixture")
        with self.assertRaisesRegex(ContractError, "whole Git diff"):
            verify_worker_sources(self.target, manifest)

    def test_omitted_tracked_project_change_is_refused(self):
        manifest = self.worker_manifest()
        self.write("extra", b"not in manifest\n")
        self.git("add", "extra"); self.git("commit", "-qm", "extra fixture")
        manifest["candidate_commit"] = self.git("rev-parse", "HEAD").strip().decode()
        self.git("tag", "-f", "candidate-fixture")
        with self.assertRaisesRegex(ContractError, "whole Git diff"):
            verify_worker_sources(self.target, manifest)

    def test_unchanged_untracked_entry_cannot_forge_commit_baseline(self):
        manifest = self.worker_manifest()
        entry = {"path":"not-committed","mode":"100644","size_bytes":1,"sha256":hashlib.sha256(b"x").hexdigest()}
        for side in ["base", "result"]:
            manifest[side]["entries"].append(copy.deepcopy(entry))
            manifest[side]["entries"].sort(key=lambda e:e["path"].encode())
            self.rehash(manifest[side])
        validate_manifest(manifest)
        with self.assertRaisesRegex(ContractError, "whole commit membership"):
            verify_worker_sources(self.target, manifest)

    def test_no_changes_still_verifies_every_baseline_blob(self):
        manifest = self.worker_manifest()
        tree = copy.deepcopy(manifest["result"])
        tree["entries"][0]["sha256"] = "0"*64; self.rehash(tree)
        baseline = make_manifest(tree,tree,scope=[],base_commit=manifest["candidate_commit"],candidate_commit=manifest["candidate_commit"],base_retention_ref="refs/tags/candidate-fixture",candidate_retention_ref="refs/tags/candidate-fixture")
        with self.assertRaisesRegex(ContractError, "whole commit content"):
            verify_worker_sources(self.target, baseline)

    def test_unrelated_identical_commit_tree_is_not_ancestry(self):
        manifest = self.worker_manifest()
        tree = self.git("rev-parse", manifest["candidate_commit"]+"^{tree}").strip().decode()
        unrelated = self.git("commit-tree", tree, "-m", "unrelated fixture").strip().decode()
        self.git("tag", "-f", "candidate-fixture", unrelated); manifest["candidate_commit"] = unrelated
        with self.assertRaises(ContractError): verify_worker_sources(self.target, manifest)

    def test_record_only_new_baseline_and_verified_launcher_are_allowed(self):
        self.init(); launcher = self.write("hv2",b"fixture launcher\n"); launcher.chmod(0o755)
        self.write("a"); self.write(".hrn/record",b"first\n")
        self.git("add","."); self.git("commit","-qm","initial fixture")
        self.write(".hrn/record",b"second\n");self.git("add",".hrn");self.git("commit","-qm","record only fixture")
        oid=self.git("rev-parse","HEAD").strip().decode();self.git("tag","retained")
        sha=hashlib.sha256(launcher.read_bytes()).hexdigest(); tree=snapshot(self.target,verified_launcher_sha256=sha)
        manifest=make_manifest(tree,tree,scope=["a"],base_commit=oid,candidate_commit=oid,base_retention_ref="refs/tags/retained",candidate_retention_ref="refs/tags/retained")
        before=(self.git("show-ref"),self.git("rev-parse","HEAD"),(self.target/".git/index").read_bytes())
        self.assertEqual({},verify_worker_sources(self.target,manifest,verified_launcher_sha256=sha))
        self.assertEqual(before,(self.git("show-ref"),self.git("rev-parse","HEAD"),(self.target/".git/index").read_bytes()))
        with self.assertRaisesRegex(ContractError,"launcher differs"):
            verify_worker_sources(self.target,manifest,verified_launcher_sha256="0"*64)


if __name__ == "__main__":
    unittest.main()
