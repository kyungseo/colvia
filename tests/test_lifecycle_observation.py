"""Focused observations for lifecycle Git policy and retired entry preservation."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

from hv2ref import product, work
from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.workspace import git_environment
from platform_fixtures import (fixture_temporary_directory, fixture_directory_link,
                               fixture_unsafe_link, fixture_unlink, posix_mechanism)


class LifecycleObservationTests(unittest.TestCase):
    def setUp(self):
        temporary = fixture_temporary_directory(prefix="lifecycle-observation-")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.target = self.base / "project"
        self.target.mkdir()
        self.home = self.base / "home"
        self.xdg = self.base / "xdg"
        self.home.mkdir()
        self.xdg.mkdir()
        environment = mock.patch.dict(os.environ, {"HOME": str(self.home), "XDG_CONFIG_HOME": str(self.xdg),
                                                   "GIT_CONFIG_GLOBAL": str(self.home / ".gitconfig")})
        environment.start()
        self.addCleanup(environment.stop)
        self.addCleanup(lambda: self.assertIsNone(work._lifecycle_visibility.get()))
        self.git("init", "-q")
        self.truth = ".hrn/work/example/identity.json"
        for name, data in {
            self.truth: b"{}\n", ".hrn/format.json": b"{}\n",
            ".hrn/product/binding.json": b"{}\n", ".hrn/.gitignore": b"",
            "colvia": b"synthetic launcher\n", "content.txt": b"project content\n",
        }.items():
            path = self.target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.target), *args], check=True,
                              capture_output=True, env=git_environment(), timeout=20).stdout

    def observe(self, change=lambda: None):
        with work._lifecycle_git_observation(self.target):
            work._visible_truth(self.target, [self.truth, ".hrn/product/binding.json", "colvia"])
            change()
            work._visible_truth(self.target, [self.truth])

    def policy_refusal(self, change):
        with self.assertRaises(ContractError) as error:
            self.observe(change)
        self.assertEqual("HV2-WORK-RECORD", error.exception.code)
        self.assertEqual("Git policy changed during checkpoint", error.exception.message)
        self.assertIsNone(work._lifecycle_visibility.get())

    def _assert_retired_occupants(self, forms):
        retired = self.target / "hv2"
        external = self.base / "external"
        external.write_bytes(b"private synthetic sentinel\n")
        native_read, native_list = work._stable_file, Path.iterdir
        def guarded_read(path):
            self.assertFalse(path == retired or retired in path.parents, "retired content was opened")
            return native_read(path)
        def guarded_list(path):
            self.assertFalse(path == retired or retired in path.parents, "retired directory was traversed")
            return native_list(path)
        for form in forms:
            with self.subTest(form=form):
                if form == "directory":
                    retired.mkdir(); (retired / "sentinel").write_bytes(b"private directory sentinel\n")
                elif form == "symlink": fixture_unsafe_link(retired, external)
                elif form == "dangling": fixture_directory_link(retired, self.base / "absent")
                elif form == "fifo": os.mkfifo(retired)
                else: retired.write_bytes(b"private retired sentinel\n")
                try:
                    before = retired.lstat()
                    with mock.patch.object(work, "_stable_file", guarded_read), mock.patch.object(Path, "iterdir", guarded_list):
                        with self.assertRaises(ContractError) as error:
                            with work._lifecycle_git_observation(self.target):
                                product._refuse_retired_entry(self.target, "delegation lifecycle")
                    self.assertEqual("HV2-WORKSPACE-PRODUCT", error.exception.code)
                    self.assertIn("retired entry collision; preserve project occupants", error.exception.message)
                    after = retired.lstat()
                    self.assertEqual((before.st_ino, before.st_mode, before.st_size, before.st_mtime_ns),
                                     (after.st_ino, after.st_mode, after.st_size, after.st_mtime_ns))
                    self.assertEqual(b"private synthetic sentinel\n", external.read_bytes())
                finally:
                    if form == "directory": shutil.rmtree(retired)
                    else: fixture_unlink(retired)

    def test_retired_occupants_are_not_opened_or_traversed(self):
        self._assert_retired_occupants(("file", "directory", "symlink", "dangling"))

    @posix_mechanism("filesystem FIFO; other retired occupant forms run on both platforms")
    def test_posix_retired_fifo_is_not_opened(self):
        self._assert_retired_occupants(("fifo",))

    def test_incidental_git_updates_do_not_refuse(self):
        def activity():
            self.git("add", "content.txt")
            (self.target / ".git/FETCH_HEAD").write_bytes(b"synthetic fetch metadata\n")
            lock = self.target / ".git/index.lock"
            lock.write_bytes(b"synthetic lock\n"); lock.unlink()
        self.observe(activity)
        self.assertEqual(b"content.txt\n", self.git("ls-files", "content.txt"))
        self.assertEqual(b"{}\n", (self.target / self.truth).read_bytes())
        self.observe()

    def test_default_ignore_transient_changes_are_refused(self):
        for location in ("xdg", "home", "empty-xdg"):
            with self.subTest(location=location):
                with mock.patch.dict(os.environ), mock.patch.object(Path, "home", return_value=self.base / "other-home"):
                    if location == "home": os.environ.pop("XDG_CONFIG_HOME", None)
                    elif location == "empty-xdg": os.environ["XDG_CONFIG_HOME"] = ""
                    ignore = (self.xdg if location == "xdg" else self.home / ".config") / "git/ignore"
                    ignore.parent.mkdir(parents=True, exist_ok=True)
                    ignore.write_bytes(b"")
                    before_policy = work._policy(self.target, [])
                    def transient():
                        ignore.write_bytes((self.truth + "\n").encode())
                        self.assertEqual((self.truth + "\n").encode(), self.git("check-ignore", "--", self.truth))
                        self.assertNotEqual(before_policy, work._policy(self.target, []))
                        ignore.write_bytes(b"")
                    self.policy_refusal(transient)
                    self.observe()

    def test_default_ignore_creation_and_symlink_target_are_observed(self):
        ignore = self.xdg / "git/ignore"
        ignore.parent.mkdir()
        self.policy_refusal(lambda: ignore.write_bytes(b""))
        ignore.unlink()
        self.observe()

    @posix_mechanism("POSIX file-symlink target observation; default-ignore creation runs on both platforms")
    def test_posix_default_ignore_symlink_target_is_observed(self):
        ignore = self.xdg / "git/ignore"
        ignore.parent.mkdir()
        destination = self.base / "shared-ignore"
        destination.write_bytes(b"")
        ignore.symlink_to(destination)
        def transient():
            destination.write_text(self.truth + "\n"); destination.write_bytes(b"")
        self.policy_refusal(transient)
        self.observe()

    def test_explicit_empty_and_explicit_path_do_not_watch_unused_default(self):
        ignore = self.xdg / "git/ignore"
        ignore.parent.mkdir(); ignore.write_bytes(b"")
        self.git("config", "core.excludesFile", "")
        self.observe(lambda: ignore.write_text(self.truth + "\n"))
        configured = self.base / "configured-ignore"
        configured.write_bytes(b"")
        self.git("config", "core.excludesFile", str(configured))
        self.observe(lambda: ignore.write_bytes(b""))
        def transient():
            configured.write_text(self.truth + "\n"); configured.write_bytes(b"")
        self.policy_refusal(transient)

    def test_actual_git_policy_and_directory_identity_still_refuse(self):
        self.policy_refusal(lambda: self.git("config", "core.ignoreCase", "false"))
        exclude = self.target / ".git/info/exclude"
        previous = exclude.read_bytes()
        def transient():
            exclude.write_text(self.truth + "\n"); exclude.write_bytes(previous)
        self.policy_refusal(transient)
        original = self.target / ".git"
        replacement = self.base / "replacement-git"
        held = self.base / "held-git"
        shutil.copytree(original, replacement)
        def replace():
            original.rename(held); replacement.rename(original)
        self.policy_refusal(replace)
        self.observe()

    def test_initially_hidden_truth_uses_visibility_refusal(self):
        ignore = self.xdg / "git/ignore"
        ignore.parent.mkdir(); ignore.write_text(self.truth + "\n")
        with self.assertRaises(ContractError) as error:
            self.observe()
        self.assertEqual("HV2-WORK-RECORD", error.exception.code)
        self.assertEqual("truth hidden by effective Git ignore policy", error.exception.message)

    def test_non_git_absent_paths_keep_existing_behavior(self):
        plain = self.base / "plain"
        plain.mkdir()
        with work._lifecycle_git_observation(plain):
            work._visible_truth(plain, ["not-yet-published"])
        self.assertIsNone(work._lifecycle_visibility.get())

    def observe_detach(self, change=lambda: None, *, repeat=1):
        from hv2ref.workspace import _DetachTopologyObservation
        topology = _DetachTopologyObservation(self.target)
        try:
            with work._detach_git_observation(self.target, topology):
                for _ in range(repeat):
                    work._visible_truth(self.target, [self.truth, ".hrn/detached.json"],
                                        _topology_observation=topology)
                change()
            topology.finish()
        finally:
            topology.close()

    def test_detach_explicit_topology_batches_visibility_and_keeps_receipt_visible(self):
        receipt = self.target / ".hrn/detached.json"
        receipt.write_bytes(b"synthetic receipt\n")
        original = work._git
        calls = []
        def observe(target, *args, **kwargs):
            calls.append(args)
            return original(target, *args, **kwargs)
        with mock.patch.object(work, "_git", side_effect=observe):
            self.observe_detach(repeat=20)
        self.assertEqual(2, sum(args[0] == "check-ignore" for args in calls))
        self.git("config", "core.excludesfile", "")
        (self.target / ".git/info/exclude").write_text(".hrn/detached.json\n")
        with self.assertRaisesRegex(ContractError, "truth hidden"):
            self.observe_detach()
        self.assertIsNone(work._lifecycle_visibility.get())

    def test_detach_receipt_truth_and_member_changes_refuse_before_next_removal(self):
        receipt = self.target / ".hrn/detached.json"
        receipt.write_bytes(b"synthetic receipt\n")
        for relative in (".hrn/detached.json", self.truth, ".hrn/product/binding.json"):
            path = self.target / relative
            original = path.read_bytes()
            with self.subTest(path=relative):
                def reappear():
                    path.unlink()
                    path.write_bytes(original)
                with self.assertRaisesRegex(ContractError, "inputs changed"):
                    self.observe_detach(reappear)
                self.assertIsNone(work._lifecycle_visibility.get())
                self.observe_detach()

    def test_detach_transient_ignore_and_error_do_not_escape_scope(self):
        receipt = self.target / ".hrn/detached.json"
        receipt.write_bytes(b"synthetic receipt\n")
        ignore = self.target / ".git/info/exclude"
        original = ignore.read_bytes()
        def transient():
            ignore.write_bytes(original + b"\n.hrn/detached.json\n")
            ignore.write_bytes(original)
        with self.assertRaisesRegex(ContractError, "Git policy changed"):
            self.observe_detach(transient)
        self.assertIsNone(work._lifecycle_visibility.get())
        def fail():
            raise RuntimeError("synthetic interruption")
        with self.assertRaisesRegex(RuntimeError, "synthetic interruption"):
            self.observe_detach(fail)
        self.assertIsNone(work._lifecycle_visibility.get())
        self.observe_detach()

    def test_detach_foreign_topology_cannot_borrow_visibility(self):
        from hv2ref.workspace import _DetachTopologyObservation
        receipt = self.target / ".hrn/detached.json"
        receipt.write_bytes(b"synthetic receipt\n")
        shared = _DetachTopologyObservation(self.target)
        foreign = _DetachTopologyObservation(self.target)
        ignore = self.target / ".git/info/exclude"
        original = ignore.read_bytes()
        try:
            with self.assertRaisesRegex(ContractError, "Git policy changed"):
                with work._detach_git_observation(self.target, shared):
                    ignore.write_bytes(original + b"\n.hrn/detached.json\n")
                    with self.assertRaisesRegex(ContractError, "truth hidden"):
                        work._visible_truth(self.target, [".hrn/detached.json"],
                                            _topology_observation=foreign)
                    ignore.write_bytes(original)
        finally:
            ignore.write_bytes(original)
            shared.close()
            foreign.close()
        self.assertIsNone(work._lifecycle_visibility.get())

    def test_detach_next_sweep_and_nonprimary_do_not_inherit_visibility(self):
        from hv2ref.workspace import _DetachTopologyObservation
        receipt = self.target / ".hrn/detached.json"
        receipt.write_bytes(b"first receipt\n")
        self.observe_detach()
        receipt.write_bytes(b"new independently observed receipt\n")
        self.observe_detach()
        plain = self.base / "plain-detach"
        plain.mkdir()
        topology = _DetachTopologyObservation(plain)
        try:
            with work._detach_git_observation(plain, topology):
                self.assertIsNone(work._lifecycle_visibility.get())
                work._visible_truth(plain, ["absent"], _topology_observation=topology)
            topology.finish()
        finally:
            topology.close()
        self.assertIsNone(work._lifecycle_visibility.get())

    def test_exact_candidate_update_recovery_and_replay(self):
        from platform_fixtures import fixture_source
        source = fixture_source()
        candidate = product.workspace_candidate(source)
        variant = self.base / "variant"
        for entry in candidate["inventory"]["entries"]:
            path = variant / entry["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / entry["path"], path)
        with (variant / "colvia").open("a") as handle:
            handle.write("\n# Synthetic previous release.\n")
        native_preflight = product._switch_preflight_records
        for is_git in (False, True):
            for recover in (False, True):
                with self.subTest(git=is_git, recover=recover):
                    target = self.base / f"l{int(is_git)}{int(recover)}"
                    target.mkdir(); (target / "sentinel").write_bytes(b"project sentinel\n")
                    if is_git:
                        subprocess.run(["git", "init", "-q", str(target)], check=True, capture_output=True, timeout=20)
                    init = product.workspace_init_preview(variant, target, authority_home_id="home-a",
                                operation_id="init-a", created_at="2026-01-01T00:00:00Z")
                    product.workspace_init_apply(variant, target, init["request"], confirm_token=init["confirm_token"])
                    packet = product.workspace_switch_preview(target, action="update", source=source,
                                operation_id="switch-a", created_at="2026-01-01T00:00:00Z")
                    calls = []
                    def activity(*args, **kwargs):
                        state = native_preflight(*args, **kwargs)
                        if is_git:
                            lock = target / ".git/index.lock"
                            lock.write_bytes(b"synthetic concurrent Git metadata\n"); lock.unlink()
                        calls.append(state[1])
                        return state
                    options = dict(confirm_token=packet["confirm_token"], source=source)
                    with mock.patch.object(product, "_switch_preflight_records", side_effect=activity):
                        if recover:
                            with self.assertRaises(InjectedCrash) as error:
                                product.workspace_switch_apply(target, packet["request"], inject_at="after-receipt", **options)
                            self.assertEqual("after-receipt", error.exception.point)
                            if is_git:
                                ignore = self.xdg / "git/ignore"
                                ignore.parent.mkdir(parents=True, exist_ok=True)
                                ignore.write_bytes(b"")
                                def truth_bytes():
                                    return {p.relative_to(target).as_posix(): p.read_bytes()
                                            for p in (target / ".hrn").rglob("*") if p.is_file()}
                                before = truth_bytes()
                                def changed_policy(*args, **kwargs):
                                    state = native_preflight(*args, **kwargs)
                                    ignore.write_bytes(b"synthetic-unused-pattern\n"); ignore.write_bytes(b"")
                                    return state
                                with mock.patch.object(product, "_switch_preflight_records", side_effect=changed_policy):
                                    with self.assertRaises(ContractError) as policy_error:
                                        product.workspace_switch_apply(target, packet["request"], recover=True, **options)
                                self.assertEqual("HV2-WORK-RECORD", policy_error.exception.code)
                                self.assertEqual("Git policy changed during checkpoint", policy_error.exception.message)
                                self.assertEqual(before, truth_bytes())
                        result = product.workspace_switch_apply(target, packet["request"], recover=recover, **options)
                        self.assertEqual("updated", result["classification"])
                        replay = product.workspace_switch_apply(target, packet["request"], **options)
                        self.assertEqual("replayed", replay["classification"])
                    self.assertGreater(len(calls), 3)
                    verified = product.verify_workspace_product(target)
                    self.assertEqual(candidate["inventory"], verified["inventory"])
                    self.assertEqual(candidate["release_ref"]["id"], Path(verified["release_path"]).name)
                    self.assertEqual(b"project sentinel\n", (target / "sentinel").read_bytes())
                    self.assertIsNone(work._lifecycle_visibility.get())
