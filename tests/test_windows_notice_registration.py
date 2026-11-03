"""Exercise interrupted registry updates off Windows without touching a user registry."""
from contextlib import nullcontext
import importlib.util
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

    def CreateKey(self, hive, key):
        self.keys.setdefault(key, {})
        return nullcontext(key)

    def DeleteKey(self, hive, key):
        assert not self.values(key)[0]
        del self.keys[key]
        self.interrupt(("delete", key))

    def SetValueEx(self, key, name, reserved, kind, value):
        self.keys[key][name] = (value, kind)
        self.interrupt(("set", name))

    def interrupt(self, point):
        if self.interrupt_on == point:
            self.interrupt_on = None
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

    def manager(self, store):
        value, kind = self.reg.keys[self.server][""]
        self.assertEqual(kind, self.reg.REG_SZ)
        return Path(value.split('"')[1])

    def change(self, digest):
        self.n.change_registration(self.store, digest)

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
