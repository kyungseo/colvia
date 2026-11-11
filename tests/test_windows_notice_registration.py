"""Exercise interrupted registry updates off Windows without touching a user registry."""
from contextlib import nullcontext
import importlib.util
import hashlib
import json
import os
import copy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Interrupted(BaseException):
    """Simulate a process exit before the in-process rollback."""


class Registry:
    HKEY_CURRENT_USER = 1
    REG_SZ = 1

    def __init__(self):
        self.keys = {}
        self.interrupt_on = None
        self.interrupt_at = None
        self.calls = 0

    def CreateKey(self, hive, key):
        self.keys.setdefault(key, {})
        self.interrupt(("create", key))
        return nullcontext(key)

    def DeleteKey(self, hive, key):
        if self.values(key)[0]:
            raise OSError("key has children")
        del self.keys[key]
        self.interrupt(("delete", key))

    def SetValueEx(self, key, name, reserved, kind, value):
        self.keys[key][name] = (value, kind)
        self.interrupt(("set", name))

    def DeleteValue(self, key, name):
        if name not in self.keys[key]:
            raise FileNotFoundError(name)
        del self.keys[key][name]
        self.interrupt(("delete-value", name))

    def interrupt(self, point):
        self.calls += 1
        if self.interrupt_on == point or self.interrupt_at == self.calls:
            self.interrupt_on = None
            self.interrupt_at = None
            raise Interrupted()

    def values(self, key):
        if key not in self.keys:
            return None
        children = {name.rsplit("\\", 1)[1] for name in self.keys if name.rpartition("\\")[0] == key}
        return children, self.keys[key].copy()


class RegistrationRecovery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = Path(self.tmp.name).resolve()
        self.reg = Registry()
        spec = importlib.util.spec_from_file_location("notice_test_target", ROOT / "distribution/windows/notices.py")
        self.n = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, winreg=self.reg):
            spec.loader.exec_module(self.n)
        self.n.owned_values = self.reg.values
        self.old, self.new = 'a' * 64, 'b' * 64
        self.app, cls = self.n.windows_notice_identity(self.store)
        self.app_key = self.n.BASE + "\\AppUserModelId\\" + self.app
        self.server = self.n.BASE + "\\CLSID\\" + cls + "\\LocalServer32"
        self.n.windows_notice_manager = self.manager
        def observe(path):
            for part in (path, *path.parents):
                if part.is_symlink():
                    raise ValueError("synthetic reparse refusal")
            st = path.stat()
            return {"directory": path.is_dir(), "links": st.st_nlink}
        self.n.windows_path_observation = observe
        self.folder = self.store / "notification-tools"
        self.folder.mkdir()
        self.icons = []
        for data in (b"old verified image", b"new verified image"):
            identity = hashlib.sha256(data).hexdigest()
            (self.folder / (identity + ".png")).write_bytes(data)
            self.icons.append(identity)

    def manager(self, store):
        value, kind = self.reg.keys[self.server][""]
        self.assertEqual(kind, self.reg.REG_SZ)
        return Path(value.split('"')[1])

    def change(self, digest, icon=None):
        self.n.change_registration(self.store, digest, icon=icon)

    def test_rejected_switch_restores_previous_command(self):
        self.change(self.old)
        def verify(store):
            result = self.manager(store)
            if result.stem == self.new:
                raise ValueError("injected verification failure")
            return result
        self.n.windows_notice_manager = verify
        with self.assertRaisesRegex(ValueError, "injected"):
            self.change(self.new)
        self.assertEqual(self.manager(self.store).stem, self.old)
        self.assertFalse((self.store / "notice-registration.pending").exists())

    def test_interrupted_create_and_remove_recover_on_next_request(self):
        self.reg.interrupt_on = ("set", "")
        with self.assertRaises(Interrupted):
            self.change(self.old)
        self.change(self.old)
        self.assertEqual(self.manager(self.store).stem, self.old)
        self.reg.interrupt_on = ("delete", self.app_key)
        with self.assertRaises(Interrupted):
            self.change(None)
        self.change(None)
        self.assertEqual(self.reg.keys, {})

    def test_recovery_preserves_foreign_value_and_pending_evidence(self):
        self.reg.interrupt_on = ("set", "")
        with self.assertRaises(Interrupted):
            self.change(self.old)
        self.reg.keys[self.server]["foreign"] = ("keep", 1)
        with self.assertRaises(ValueError):
            self.change(None)
        self.assertIn("foreign", self.reg.keys[self.server])
        self.assertTrue((self.store / "notice-registration.pending").exists())

    def prepare_state(self, previous):
        self.reg.keys.clear()
        self.reg.interrupt_at = self.reg.interrupt_on = None
        (self.store / "notice-registration.pending").unlink(missing_ok=True)
        if previous is not None:
            self.change(*previous)
        self.reg.calls = 0

    def transitions(self):
        return [(None, (self.old, self.icons[0])),
                ((self.old, None), (self.old, self.icons[0])),
                ((self.old, self.icons[0]), (self.new, self.icons[1])),
                ((self.old, self.icons[0]), (None, None))]

    def test_all_registry_mutation_interruptions_recover_exact_state(self):
        for previous, target in self.transitions():
            self.prepare_state(previous); self.change(*target)
            expected = copy.deepcopy(self.reg.keys); count = self.reg.calls
            for cut in range(1, count + 1):
                with self.subTest(previous=previous, target=target, cut=cut):
                    self.prepare_state(previous); self.reg.interrupt_at = cut
                    with self.assertRaises(Interrupted): self.change(*target)
                    self.assertTrue((self.store / "notice-registration.pending").exists())
                    self.change(*target)
                    self.assertEqual(self.reg.keys, expected)
                    self.assertFalse((self.store / "notice-registration.pending").exists())

    def test_journal_publication_and_retirement_interruptions(self):
        journal = self.store / "notice-registration.pending"
        original = self.n.replace_json
        for previous, target in self.transitions():
            self.prepare_state(previous); self.change(*target); expected = copy.deepcopy(self.reg.keys)
            self.prepare_state(previous)
            def after_publication(*args, **kwargs):
                original(*args, **kwargs); raise Interrupted()
            with patch.object(self.n, "replace_json", side_effect=after_publication):
                with self.assertRaises(Interrupted): self.change(*target)
            self.change(*target); self.assertEqual(self.reg.keys, expected)
            self.prepare_state(previous)
            unlink = Path.unlink
            def before_retirement(path, *args, **kwargs):
                if path == journal: raise Interrupted()
                return unlink(path, *args, **kwargs)
            with patch.object(Path, "unlink", before_retirement):
                with self.assertRaises(Interrupted): self.change(*target)
            self.assertEqual(self.reg.keys, expected)
            self.change(*target); self.assertEqual(self.reg.keys, expected)
            self.assertFalse(journal.exists())

    def test_interrupted_recovery_retains_original_previous(self):
        self.change(self.old, self.icons[0])
        previous = copy.deepcopy(self.reg.keys)
        self.reg.interrupt_on = ("set", "IconUri")
        with self.assertRaises(Interrupted): self.change(self.new, self.icons[1])
        journal = self.store / "notice-registration.pending"; raw = journal.read_bytes()
        self.reg.interrupt_on = ("set", "")
        with self.assertRaises(Interrupted): self.change(self.new, self.icons[1])
        self.assertEqual(journal.read_bytes(), raw)
        # A failing new request still leaves the exact prior committed state after recovery.
        with self.assertRaises((OSError, ValueError)): self.change(self.new, "c" * 64)
        self.assertEqual(self.reg.keys, previous)
        self.assertFalse(journal.exists())

    def test_legacy_pending_record_is_recovered(self):
        self.reg.interrupt_on = ("set", "")
        with self.assertRaises(Interrupted): self.change(self.old)
        journal = self.store / "notice-registration.pending"
        self.n.replace_json(journal, {"previous": None, "requested": self.old})
        self.change(self.new, self.icons[1])
        self.assertEqual(self.manager(self.store).stem, self.new)
        self.assertIn("IconUri", self.reg.keys[self.app_key])
        self.assertFalse(journal.exists())

    def test_bad_journal_is_read_only_and_preserved(self):
        bad = [[], {"previous": {"manager": self.old, "icon": None}, "requested": None},
               {"schema": True, "previous": None, "requested": None},
               {"schema": 2.0, "previous": None, "requested": None},
               {"schema": 2, "previous": {"manager": self.old, "icon": "../foreign"}, "requested": None},
               {"schema": 2, "previous": None, "requested": {"manager": self.new, "icon": None, "extra": 1}},
               {"schema": 2, "previous": None, "requested": False}]
        journal = self.store / "notice-registration.pending"
        for value in bad:
            self.prepare_state((self.old, None)); before = copy.deepcopy(self.reg.keys)
            self.n.replace_json(journal, value); raw = journal.read_bytes()
            with self.assertRaises(ValueError): self.change(None)
            self.assertEqual(self.reg.keys, before); self.assertEqual(journal.read_bytes(), raw)

    def test_foreign_values_during_recovery_are_preserved(self):
        for name, value in [("IconUri", ("outside.png", 1)), ("DisplayName", ("Other", 1)),
                            ("CustomActivator", ("foreign", 1)), ("IconUri", (str(self.folder/(self.icons[0]+".png")), 2)),
                            ("Extra", ("keep", 1))]:
            self.prepare_state((self.old, None))
            self.reg.interrupt_on = ("set", "IconUri")
            with self.assertRaises(Interrupted): self.change(self.new, self.icons[0])
            self.reg.keys[self.app_key][name] = value; before=copy.deepcopy(self.reg.keys)
            with self.assertRaises(ValueError): self.change(None)
            self.assertEqual(before,self.reg.keys); self.assertTrue((self.store/"notice-registration.pending").exists())

    def test_failed_icon_switch_restores_exact_legacy_values(self):
        self.change(self.old); previous=copy.deepcopy(self.reg.keys)
        def verify(store):
            result=self.manager(store)
            if result.stem==self.new: raise ValueError("rejected")
            return result
        self.n.windows_notice_manager=verify
        with self.assertRaisesRegex(ValueError,"rejected"): self.change(self.new,self.icons[0])
        self.assertEqual(previous,self.reg.keys)

    def test_missing_previous_image_does_not_block_disable_or_rollback(self):
        self.change(self.old,self.icons[0]); previous=copy.deepcopy(self.reg.keys)
        (self.folder/(self.icons[0]+".png")).unlink()
        def verify(store):
            result=self.manager(store)
            if result.stem==self.new: raise ValueError("rejected")
            return result
        self.n.windows_notice_manager=verify
        with self.assertRaisesRegex(ValueError,"rejected"):self.change(self.new,self.icons[1])
        self.assertEqual(previous,self.reg.keys)
        self.change(None);self.assertEqual({},self.reg.keys)

    def test_same_pair_noop_rechecks_image_and_retains_files_on_disable(self):
        self.change(self.old,self.icons[0]); self.reg.calls=0
        self.change(self.old,self.icons[0]);self.assertEqual(self.reg.calls,0)
        image=self.folder/(self.icons[0]+".png");image.write_bytes(b"damaged")
        with self.assertRaises(ValueError): self.change(self.old,self.icons[0])
        self.change(None);self.assertTrue(image.exists())
        with self.assertRaises(ValueError): self.change(self.old, self.icons[0])
        self.assertEqual(self.reg.keys, {})

    def test_source_pin_and_unsafe_file_refusals_before_publication(self):
        source=self.store/"image.png";source.write_bytes(b"new source")
        identity=hashlib.sha256(source.read_bytes()).hexdigest()
        before=set(self.folder.iterdir())
        with self.assertRaises(ValueError):self.n.retained_copy(self.store,source,suffix=".png",expected="d"*64)
        self.assertEqual(before,set(self.folder.iterdir()))
        self.assertEqual(identity,self.n.retained_copy(self.store,source,suffix=".png",expected=identity))
        dest=self.folder/(identity+".png");dest.write_bytes(b"foreign")
        with self.assertRaises(ValueError):self.n.retained_copy(self.store,source,suffix=".png",expected=identity)
        self.assertEqual(dest.read_bytes(),b"foreign")
        dest.unlink();dest.symlink_to(source)
        with self.assertRaises(ValueError):self.n.retained_copy(self.store,source,suffix=".png",expected=identity)
        dest.unlink();os.link(source,dest)
        with self.assertRaises(ValueError):self.n.retained_copy(self.store,source,suffix=".png",expected=identity)

    def test_registration_uses_packaged_pin_before_changing_registry(self):
        with patch.object(self.n,"exclusive_file_lock",return_value=nullcontext()), \
             patch.object(self.n,"retained_copy",return_value=self.icons[0]) as retain, \
             patch.object(self.n,"change_registration") as change:
            self.n.ICON_SHA256=self.icons[0]
            self.n.registration(self.store,self.store/"manager.exe",enable=True)
            self.assertEqual(retain.call_args_list[0].args[1].name,"notice-icon.png")
            self.assertEqual(retain.call_args_list[0].kwargs["expected"],self.icons[0])
            self.assertEqual(change.call_args.kwargs["icon"],self.icons[0])

    def test_image_drift_after_registry_write_restores_previous(self):
        self.change(self.old, self.icons[0]); previous = copy.deepcopy(self.reg.keys)
        def drift(store):
            result = self.manager(store)
            if result.stem == self.new:
                (self.folder / (self.icons[1] + ".png")).write_bytes(b"changed after apply")
            return result
        self.n.windows_notice_manager = drift
        with self.assertRaises(ValueError): self.change(self.new, self.icons[1])
        self.assertEqual(previous, self.reg.keys)
        self.assertFalse((self.store / "notice-registration.pending").exists())

    def test_all_restore_mutation_interruptions_preserve_original_journal(self):
        journal = self.store / "notice-registration.pending"
        for previous, target in self.transitions():
            self.prepare_state(previous); prior = copy.deepcopy(self.reg.keys)
            self.change(*target); committed = copy.deepcopy(self.reg.keys); apply_count = self.reg.calls
            for apply_cut in range(1, apply_count + 1):
                self.prepare_state(previous); self.reg.interrupt_at = apply_cut
                with self.assertRaises(Interrupted): self.change(*target)
                partial = copy.deepcopy(self.reg.keys); raw = journal.read_bytes()
                record = json.loads(raw)
                self.reg.calls = 0
                # End recovery before a new request can publish its journal.
                with patch.object(self.n, "replace_json", side_effect=Interrupted()):
                    with self.assertRaises(Interrupted): self.change(*target)
                restore_count = self.reg.calls
                self.assertEqual(self.reg.keys, prior)
                for restore_cut in range(1, restore_count + 1):
                    with self.subTest(previous=previous, target=target, apply_cut=apply_cut, restore_cut=restore_cut):
                        self.reg.keys = copy.deepcopy(partial)
                        self.n.replace_json(journal, record)
                        self.reg.calls = 0; self.reg.interrupt_at = restore_cut
                        with self.assertRaises(Interrupted): self.change(*target)
                        self.assertEqual(journal.read_bytes(), raw)
                        self.change(*target)
                        self.assertEqual(self.reg.keys, committed)
                        self.assertFalse(journal.exists())
