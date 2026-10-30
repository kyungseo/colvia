"""Synthetic guard-policy history fixtures, not lifecycle or model qualification."""
from pathlib import Path
import hashlib
import sys
import tempfile
import unittest
from unittest import mock

from hv2ref.errors import ContractError
from hv2ref.jsonio import canonical_json_bytes
from hv2ref import product, workspace
from hv2ref.official_documents import EffectJournal
from hv2ref.official_state import read_capsule


@unittest.skipUnless(sys.platform == "darwin", "official execution is macOS-only")
class OfficialGuardHistoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

    def fixture(self, initial, active="official-execution-1", *, bootstrap=True):
        target = self.root / initial
        target.mkdir()
        fmt = {"record_type": "workspace-format", "format_version": 1,
               "authority_home_id": "synthetic", "created_at": "2026-01-01T00:00:00Z", "lineage": None}
        release = {"id": "product-release-" + "a" * 24, "sha256": "a" * 64, "inventory_id": initial}
        plan = {"record_type": "lifecycle-plan", "schema_version": 7 if initial == "official-execution-1" else 6 if initial == "windows-2" else 5 if initial == "continuation-1" else 4 if initial == "delegation-1" else 1,
                "operation_id": "init-a", "action": "init", "target_fingerprint": workspace.target_fingerprint(target),
                "authority_home_id": "synthetic", "expected_binding_ref": None, "candidate_release": release,
                "format_sha256": hashlib.sha256(canonical_json_bytes(fmt)).hexdigest(), "truth_refs": [],
                "remove": [], "preserve": [], "created_at": "2026-01-01T00:00:00Z"}
        if bootstrap:
            workspace.bootstrap_root(target, plan, fmt)
        else:
            # Selector-only Windows fixture on macOS; no Windows writer invocation.
            folder = target / ".hrn/product"
            folder.mkdir(parents=True)
            (folder / "init-plan.json").write_bytes(canonical_json_bytes(plan))
        if active is not None:
            # Deliberately only a policy hint. It must never establish binding authority.
            (target / ".hrn/product/binding.json").write_bytes(canonical_json_bytes({"active_release": {"inventory_id": active}}))
        return target

    def capsule(self, target):
        # Minimal read_capsule fixture; not a prepared or executed runtime grant.
        spec = {"target": str(target)}
        grant = hashlib.sha256(canonical_json_bytes(spec)).hexdigest()
        folder = target / ".hrn/executions" / grant
        folder.mkdir(parents=True)
        (folder / "grant.json").write_bytes(canonical_json_bytes({"record_type": "official-execution-grant", "schema_version": 1, "grant": grant, "spec": spec}))
        journal = EffectJournal(folder / "journal.jsonl", create=True)
        journal.append("granted", {"grant": grant})
        return grant, journal

    def test_all_legacy_posix_init_histories_select_current_official_barrier(self):
        for initial in ("human-1", "worker-1", "umbrella-1", "planning-1", "checkout-1", "entry-1", "delegation-1", "continuation-1"):
            with self.subTest(initial=initial):
                target = self.fixture(initial)
                self.assertEqual(workspace._guard_runtime_window(target), "official-execution-1")

    def test_incomplete_capsule_blocks_and_closed_capsule_releases_guard(self):
        target = self.fixture("planning-1")
        grant, journal = self.capsule(target)
        self.assertEqual(read_capsule(target, grant)["status"], "incomplete")
        with self.assertRaisesRegex(ContractError, "unresolved-execution-blocks-operation"):
            with workspace.writer_guard(target):
                self.fail("open capsule entered writer body")
        journal.append("terminal", {"status": "revoked-before-launch"})
        self.assertEqual(read_capsule(target, grant)["status"], "revoked-before-launch")
        with workspace.writer_guard(target):
            self.assertEqual(workspace._guard_runtime_window(target), "official-execution-1")
            # The guard is not authority: a forged hint still fails the real verifier.
            with self.assertRaises(ContractError):
                product.require_workspace_runtime(target)

    def test_ordinary_and_windows_histories_are_not_promoted_by_other_hints(self):
        target = self.fixture("planning-1", active="continuation-1")
        self.assertEqual(workspace._guard_runtime_window(target), "planning-1")
        target = self.fixture("windows-2", bootstrap=False)
        self.assertEqual(workspace._guard_runtime_window(target), "windows-2")
        target = self.fixture("official-execution-1", active=None)
        self.assertEqual(workspace._guard_runtime_window(target), "official-execution-1")

    def test_malformed_binding_hint_is_preserved_and_refused(self):
        target = self.fixture("planning-1")
        path = target / ".hrn/product/binding.json"
        path.write_bytes(b"{malformed")
        with self.assertRaises(ContractError):
            workspace._guard_runtime_window(target)
        self.assertEqual(path.read_bytes(), b"{malformed")

    def test_window_change_while_acquiring_guard_refuses_before_body(self):
        target = self.fixture("planning-1")
        with mock.patch.object(workspace, "_guard_runtime_window", side_effect=["official-execution-1", "planning-1"]):
            with self.assertRaisesRegex(ContractError, "workspace policy changed while acquiring guard"):
                with workspace.writer_guard(target):
                    self.fail("drift entered writer body")
