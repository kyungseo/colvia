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


class LifecycleObservationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="lifecycle-observation-")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.target = self.base / "project"
        self.target.mkdir()
        self.home = self.base / "home"
        self.xdg = self.base / "xdg"
        self.home.mkdir()
        self.xdg.mkdir()
        environment = mock.patch.dict(os.environ, {"HOME": str(self.home), "XDG_CONFIG_HOME": str(self.xdg)})
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

    def test_retired_occupants_are_not_opened_or_traversed(self):
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
        for form in ("file", "directory", "symlink", "dangling", "fifo"):
            with self.subTest(form=form):
                if form == "directory":
                    retired.mkdir(); (retired / "sentinel").write_bytes(b"private directory sentinel\n")
                elif form == "symlink": retired.symlink_to(external)
                elif form == "dangling": retired.symlink_to(self.base / "absent")
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
                    else: retired.unlink()

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
                with mock.patch.dict(os.environ):
                    if location == "home": os.environ.pop("XDG_CONFIG_HOME", None)
                    elif location == "empty-xdg": os.environ["XDG_CONFIG_HOME"] = ""
                    ignore = (self.xdg if location == "xdg" else self.home / ".config") / "git/ignore"
                    ignore.parent.mkdir(parents=True, exist_ok=True)
                    ignore.write_bytes(b"")
                    def transient():
                        ignore.write_text(self.truth + "\n")
                        ignore.write_bytes(b"")
                    self.policy_refusal(transient)
                    self.observe()

    def test_default_ignore_creation_and_symlink_target_are_observed(self):
        ignore = self.xdg / "git/ignore"
        ignore.parent.mkdir()
        self.policy_refusal(lambda: ignore.write_bytes(b""))
        ignore.unlink()
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

    def test_exact_candidate_update_recovery_and_replay(self):
        source = product.source_root()
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
                    target = self.base / f"lifecycle-{is_git}-{recover}"
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
