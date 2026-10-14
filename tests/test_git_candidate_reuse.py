"""Installed Git examples with whole-result and authority preservation oracles.

Git operations belong to the fixture operator, never to Work apply. These cases
do not exercise remote hosting or choose a project's branch/authority policy.
"""
from __future__ import annotations
from test_productization_safety import verified_inventory_id
import copy
import hashlib
import html
import json
import re
import subprocess
import unittest

from hv2ref.errors import ContractError
from hv2ref.jsonio import canonical_json_bytes
from hv2ref.product import verify_workspace_product
from hv2ref.work import make_manifest, read_work, snapshot, verify_worker_sources
from hv2ref.workspace import git_environment
from test_productization_safety import exact_snapshot
import test_worktree_execution as fixtures


class InstalledCandidateReuseTests(unittest.TestCase):
    setUp = fixtures.InstalledWorkerPublicationTests.setUp
    TIME = fixtures.InstalledWorkerPublicationTests.TIME
    call = fixtures.InstalledWorkerPublicationTests.call
    installed = fixtures.InstalledWorkerPublicationTests.installed
    preview = fixtures.InstalledWorkerPublicationTests.preview
    apply_init = fixtures.InstalledWorkerPublicationTests.apply_init
    draft = fixtures.InstalledWorkerPublicationTests.draft
    accept_intent = fixtures.InstalledWorkerPublicationTests.accept_intent
    prepare_worker_result = fixtures.InstalledWorkerPublicationTests.prepare_worker_result
    git = fixtures.InstalledWorkerPublicationTests.git

    def observe(self, target):
        return snapshot(target, verified_launcher_sha256=self.launcher, verified_inventory_id=verified_inventory_id(self.target))

    def product_files(self, target):
        # Independent of the runtime's snapshot and ignore handling.
        return {p: value for p, value in exact_snapshot(target).items()
                if p != "." and p.split("/", 1)[0] not in (".git", ".hrn")}

    def refs(self):
        return dict(line.split(" ", 1) for line in self.git(
            self.target, "for-each-ref", "--format=%(refname) %(objectname)").splitlines())

    def index(self):
        entries = {}
        for line in self.git(self.target, "ls-files", "--stage").splitlines():
            entry, path = line.split("\t", 1)
            self.assertEqual("0", entry.split()[-1])
            entries[path] = entry
        return entries

    def verify_sources(self):
        verify_worker_sources(self.target, self.manifest,
                              verified_launcher_sha256=self.launcher,
                              verified_inventory_id="entry-1")

    def accept_a(self):
        prepared = self.prepare_worker_result()
        self.launcher = verify_workspace_product(self.target)["launcher_sha256"]
        self.before_a = read_work(self.target, "work-a")
        self.revision_a = self.before_a["revisions"]["result"]
        self.manifest = self.before_a["manifests"][self.revision_a["result_refs"]["manifest"]["id"]]
        self.c = self.manifest["base_commit"]
        self.k = self.manifest["candidate_commit"]
        self.worker = self.base / "worker"
        # Candidate retention must survive removal of its worker checkout.
        self.git(self.target, "tag", "candidate-retained", self.k)
        before_git = exact_snapshot(self.target / ".git")
        self.accepted = json.loads(self.installed(
            ["work", "apply", "--confirm", prepared["confirm_token"]], prepared["ticket"]).stdout)
        self.assertEqual(before_git, exact_snapshot(self.target / ".git"))
        self.assertEqual("completed", self.accepted["state"])
        self.assertEqual(self.manifest["result"], self.observe(self.target))
        self.assertEqual(self.product_files(self.worker), self.product_files(self.target))
        self.authority_a = exact_snapshot(self.target / ".hrn")
        self.worker_authority = exact_snapshot(self.worker / ".hrn")

    def reuse_a(self):
        self.assertEqual(self.c, self.git(self.target, "rev-parse", "HEAD"))
        self.git(self.target, "diff", "--cached", "--quiet", self.c, "--")
        self.git(self.target, "merge-base", "--is-ancestor", self.c, self.k)
        self.assertEqual("a", self.git(self.target, "diff", "--name-only", self.c, self.k, "--"))
        self.verify_sources()
        before_refs, before_index = self.refs(), self.index()
        before_product = self.product_files(self.target)
        before_commits = set(self.git(self.target, "rev-list", "--all").splitlines())
        branch = self.git(self.target, "symbolic-ref", "HEAD")
        self.git(self.target, "reset", "--soft", self.k)
        self.assertEqual(before_index, self.index())
        self.assertEqual(before_product, self.product_files(self.target))
        self.assertEqual(self.authority_a, exact_snapshot(self.target / ".hrn"))
        self.git(self.target, "restore", "--staged", "--source=" + self.k, "--", "a")
        self.assertEqual(self.k, self.git(self.target, "rev-parse", "HEAD"))
        self.git(self.target, "diff", "--cached", "--quiet", self.k, "--")
        self.assertEqual({p: v for p, v in before_index.items() if p != "a"},
                         {p: v for p, v in self.index().items() if p != "a"})
        self.assertEqual(before_refs | {branch: self.k}, self.refs())
        self.assertEqual(self.c, self.git(self.target, "rev-parse", "ORIG_HEAD"))
        self.assertEqual(before_commits, set(self.git(self.target, "rev-list", "--all").splitlines()))
        self.assertEqual(before_product, self.product_files(self.target))
        self.assertEqual(self.authority_a, exact_snapshot(self.target / ".hrn"))
        self.assertEqual(self.accepted, read_work(self.target, "work-a"))
        self.verify_sources()

    def publish_b(self, operation, manifest, prior=None, worker=None):
        revision = copy.deepcopy(self.revision_a)
        rid = "b-" + operation
        digest = hashlib.sha256(canonical_json_bytes(manifest)).hexdigest()
        revision.update(work_id="work-b", record_id=rid, operation=operation,
                        expected_prior_selection=prior, scope=["b"],
                        progress="review" if operation == "submit-result" else "active",
                        result_refs={"manifest": {"id": digest, "sha256": digest}})
        identity = self.before_a["identity"] | {"work_id": "work-b"}
        value = {"identity": identity, "revision": revision, "manifest": manifest,
                 "selection_id": rid + "-s", "operation_id": rid + "-op"}
        args = ["work", "publish"] + (["--worker", worker] if worker is not None else [])
        return json.loads(self.installed(args, value).stdout)

    def start_b(self, commit):
        self.git(self.target, "tag", "next-base", commit)
        tree = self.observe(self.target)
        manifest = make_manifest(tree, tree, scope=["b"], base_commit=commit,
                                 candidate_commit=commit, base_retention_ref="refs/tags/next-base",
                                 candidate_retention_ref="refs/tags/next-base")
        graph = self.publish_b("start", manifest)
        worker = self.base / "worker-b"
        self.git(self.target, "worktree", "add", "-q", "-b", "worker-b", str(worker), commit)
        self.assertEqual("active", graph["state"])
        self.assertEqual(commit, self.git(worker, "rev-parse", "HEAD"))
        self.assertEqual(tree, self.observe(worker))
        self.assertEqual(self.product_files(self.target), self.product_files(worker))
        self.assertEqual(self.accepted, read_work(self.target, "work-a"))
        after = exact_snapshot(self.target / ".hrn")
        self.assertTrue(all(after.get(p) == value for p, value in self.authority_a.items()))
        self.assertTrue(all(p == "work/work-b" or p.startswith("work/work-b/")
                            for p in set(after) - set(self.authority_a)))
        return graph, worker, manifest

    def check_reader(self, wid):
        view = self.installed(["view", "work", wid]).stdout.decode()
        view = re.sub(r"\\([\\`*_{}\[\]()!|#~])", r"\1", html.unescape(view))
        self.assertIn("whole_result_matches: True", view)
        status = json.loads(self.installed(["status"]).stdout)
        self.assertEqual("pass", status["classification"])
        self.assertFalse(status["pending_work"])
        self.installed(["doctor"])

    def test_candidate_reuse_fast_forward_retirement_and_next_baseline(self):
        self.accept_a()
        integration = self.base / "integration"
        self.git(self.target, "worktree", "add", "-q", "-b", "integration", str(integration), self.c)
        self.reuse_a()
        self.git(integration, "merge", "--ff-only", self.k)
        self.assertEqual(self.k, self.git(integration, "rev-parse", "HEAD"))
        self.assertEqual(self.product_files(self.target), self.product_files(integration))
        self.assertEqual("", self.git(self.worker, "status", "--porcelain", "--untracked-files=all"))
        self.assertEqual("", self.git(self.worker, "ls-files", "--others", "--ignored", "--exclude-standard"))
        self.assertEqual(self.worker_authority, exact_snapshot(self.worker / ".hrn"))
        before_refs = self.refs()
        self.git(self.target, "worktree", "remove", str(self.worker))
        self.assertFalse(self.worker.exists())
        self.assertEqual(before_refs, self.refs())
        self.verify_sources()
        self.assertEqual(self.authority_a, exact_snapshot(self.target / ".hrn"))
        self.start_b(self.k)
        self.check_reader("work-a")
        self.assertEqual({self.c, self.k}, set(self.git(self.target, "rev-list", "--all").splitlines()))

    def test_squash_sync_keeps_second_pr_scope_and_accepted_history(self):
        self.accept_a()
        integration = self.base / "integration"
        self.git(self.target, "worktree", "add", "-q", "-b", "integration", str(integration), self.c)
        self.reuse_a()
        self.git(integration, "merge", "--squash", "--no-commit", self.k)
        self.git(integration, "commit", "-qm", "synthetic squash")
        squash = self.git(integration, "rev-parse", "HEAD")
        self.assertEqual(self.c, self.git(integration, "show", "-s", "--format=%P", squash))
        self.assertEqual(self.git(self.target, "rev-parse", self.k + "^{tree}"),
                         self.git(self.target, "rev-parse", squash + "^{tree}"))
        self.git(self.target, "merge", "--no-ff", "-m", "synthetic integration sync", squash)
        merged = self.git(self.target, "rev-parse", "HEAD")
        self.assertEqual([self.k, squash], self.git(self.target, "show", "-s", "--format=%P", merged).split())
        self.assertEqual(self.git(self.target, "rev-parse", squash + "^{tree}"),
                         self.git(self.target, "rev-parse", merged + "^{tree}"))
        self.assertEqual(self.manifest["result"], self.observe(self.target))
        self.assertEqual(self.authority_a, exact_snapshot(self.target / ".hrn"))
        self.verify_sources()
        graph, worker, baseline = self.start_b(merged)
        (worker / "b").write_bytes(b"second result\n")
        self.git(worker, "add", "--", "b")
        self.git(worker, "commit", "-qm", "synthetic second candidate")
        candidate = self.git(worker, "rev-parse", "HEAD")
        self.git(self.target, "tag", "second-candidate", candidate)
        self.assertEqual(squash, self.git(self.target, "merge-base", squash, candidate))
        self.assertEqual("b", self.git(self.target, "diff", "--name-only", squash + "..." + candidate, "--"))
        self.git(self.target, "diff", "--check", squash + "..." + candidate, "--")
        result = make_manifest(baseline["base"], self.observe(worker), scope=["b"],
                               base_commit=merged, candidate_commit=candidate,
                               base_retention_ref="refs/tags/next-base",
                               candidate_retention_ref="refs/tags/second-candidate")
        self.publish_b("submit-result", result, graph["current"]["selection_ref"], worker)
        prepared = json.loads(self.installed(["work", "prepare"], {
            "work_id": "work-b", "action": "accept", "actor": "owner", "reason": "second fixture result",
            "request_id": "accept-b", "observed_at": self.TIME, "revision_ref": None, "supersedes": None}).stdout)
        before_git = exact_snapshot(self.target / ".git")
        final = json.loads(self.installed(["work", "apply", "--confirm", prepared["confirm_token"]], prepared["ticket"]).stdout)
        self.assertEqual("completed", final["state"])
        self.assertEqual(before_git, exact_snapshot(self.target / ".git"))
        self.assertEqual(self.product_files(worker), self.product_files(self.target))
        self.assertEqual(self.accepted, read_work(self.target, "work-a"))
        after_authority = exact_snapshot(self.target / ".hrn")
        self.assertTrue(all(after_authority.get(p) == value for p, value in self.authority_a.items()
                            if p == "work/work-a" or p.startswith("work/work-a/")))
        self.check_reader("work-b")
        self.assertEqual({self.c, self.k, squash, merged, candidate},
                         set(self.git(self.target, "rev-list", "--all").splitlines()))

        # New manifests chose stable tags before publication; the worker branch
        # can retire after integration without changing exact historical refs.
        product_before = self.product_files(self.target)
        index_before = self.index()
        refs_before = self.refs()
        control_ref = self.git(self.target, "symbolic-ref", "HEAD")
        self.git(self.target, "merge-base", "--is-ancestor", merged, candidate)
        self.git(self.target, "diff", "--cached", "--quiet", merged, "--")
        self.git(self.target, "reset", "--soft", candidate)
        self.git(self.target, "restore", "--staged", "--source=" + candidate, "--", "b")
        self.assertEqual(product_before, self.product_files(self.target))
        self.assertEqual(after_authority, exact_snapshot(self.target / ".hrn"))
        self.assertEqual({p: v for p, v in index_before.items() if p != "b"},
                         {p: v for p, v in self.index().items() if p != "b"})
        self.git(self.target, "diff", "--cached", "--quiet", candidate, "--")
        self.assertEqual("", self.git(worker, "status", "--porcelain", "--untracked-files=all"))
        self.assertEqual("", self.git(worker, "ls-files", "--others", "--ignored", "--exclude-standard"))
        worker_authority = exact_snapshot(worker / ".hrn")
        # Git checkout recreates directory/non-executable permission bits;
        # compare kinds and bytes, while preserving the control's exact modes.
        self.assertEqual({}, {p: (v[:2], after_authority.get(p, ())[:2])
                              for p, v in worker_authority.items()
                              if (v[:1] if v[0] == "directory" else v[:2]) !=
                              (after_authority.get(p, ())[:1] if v[0] == "directory"
                               else after_authority.get(p, ())[:2])})
        self.git(self.target, "worktree", "remove", str(worker))
        self.git(self.target, "branch", "-d", "worker-b")
        expected_refs = refs_before | {control_ref: candidate}
        del expected_refs["refs/heads/worker-b"]
        self.assertEqual(expected_refs, self.refs())
        self.assertFalse(worker.exists())
        verify_worker_sources(self.target, result, verified_launcher_sha256=self.launcher,
                              verified_inventory_id="entry-1")
        self.assertEqual(final, read_work(self.target, "work-b"))
        self.assertEqual(after_authority, exact_snapshot(self.target / ".hrn"))
        self.check_reader("work-b")

        # Keeping the commit through another ref does not replace its exact name.
        self.git(self.target, "tag", "-d", "second-candidate")
        self.assertEqual(candidate, self.git(self.target, "rev-parse", "HEAD"))
        with self.assertRaises(ContractError) as missing_ref:
            verify_worker_sources(self.target, result, verified_launcher_sha256=self.launcher,
                                  verified_inventory_id="entry-1")
        self.assertEqual("HV2-WORK-CONTENT", missing_ref.exception.code)
        self.assertEqual("Git content probe failed: show-ref", missing_ref.exception.message)
        self.assertEqual(final, read_work(self.target, "work-b"))
        self.assertEqual(after_authority, exact_snapshot(self.target / ".hrn"))
        self.git(self.target, "tag", "second-candidate", candidate)
        verify_worker_sources(self.target, result, verified_launcher_sha256=self.launcher,
                              verified_inventory_id="entry-1")

    def test_non_fast_forward_refusal_preserves_acceptance_and_sources(self):
        self.accept_a()
        integration = self.base / "integration"
        self.git(self.target, "worktree", "add", "-q", "-b", "integration", str(integration), self.c)
        (integration / "upstream").write_bytes(b"independent upstream\n")
        self.git(integration, "add", "--", "upstream")
        self.git(integration, "commit", "-qm", "synthetic upstream")
        upstream = self.git(integration, "rev-parse", "HEAD")
        self.reuse_a()
        self.assertEqual(self.c, self.git(self.target, "merge-base", self.k, upstream))
        before_refs, before_index = self.refs(), self.index()
        before_files = self.product_files(self.target)
        upstream_files = self.product_files(integration)
        upstream_index = self.git(integration, "ls-files", "--stage")
        result = subprocess.run(["git", "-c", "maintenance.auto=false", "-c", "gc.auto=0",
                                 "-C", str(integration), "merge", "--ff-only", self.k],
                                capture_output=True, env=git_environment() | {"LC_ALL": "C"}, timeout=30)
        self.assertEqual(128, result.returncode, (result.stdout + result.stderr).decode(errors="replace"))
        self.assertIn(b"Not possible to fast-forward", result.stderr)
        self.assertEqual(upstream, self.git(integration, "rev-parse", "HEAD"))
        self.assertEqual(self.k, self.git(self.target, "rev-parse", "HEAD"))
        self.assertEqual(before_refs, self.refs())
        self.assertEqual(before_index, self.index())
        self.assertEqual(upstream_index, self.git(integration, "ls-files", "--stage"))
        self.assertEqual(upstream_files, self.product_files(integration))
        self.assertEqual(before_files, self.product_files(self.target))
        self.assertEqual(self.authority_a, exact_snapshot(self.target / ".hrn"))
        self.assertEqual(self.accepted, read_work(self.target, "work-a"))
        self.verify_sources()
        self.check_reader("work-a")
        self.assertEqual({self.c, self.k, upstream}, set(self.git(self.target, "rev-list", "--all").splitlines()))
