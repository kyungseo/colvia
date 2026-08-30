from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from hv2ref.carrier import _safe_relative_path, build_release, verify_release
from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.jsonio import canonical_json_bytes, decode_json_bytes, exclusive_file_lock, load_json, sha256_file
from hv2ref.state import StateStore, _base


SEAL = {
    "authority_home_id": "7d854f54-6538-4cd4-8961-2e2f50ef9653",
    "created_at": "2026-08-08T12:00:00Z",
    "inventory_id": "inventory-0001",
    "release_id": "release-0001",
}


class ContractFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source.md"
        self.source.write_bytes(b"real generation 1 contract payload\n")
        self.release = self.root / "release"
        build_release(self.source, self.release, SEAL)
        self.target = self.root / "target"
        self.target.mkdir()
        self.store = StateStore(self.target)
        self.store.initialize(SEAL["authority_home_id"], "item-0001", "2026-08-08T12:01:00Z")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def create(self) -> dict:
        return self.store.transition(
            item_id="item-0001",
            operation="create",
            sequence=1,
            observed_at="2026-08-08T12:02:00Z",
            actor="OWNER-LOCAL-001",
            release_root=self.release,
        )


class JsonAndCarrierRedTests(ContractFixture):
    def test_advisory_lock_anchor_rejects_symlink_and_wrong_type(self) -> None:
        lock_path = self.root / "staging/locks/active-integration.switch.lock"
        lock_path.parent.mkdir(parents=True)
        outside = self.root / "outside-lock"
        outside.write_bytes(b"")
        lock_path.symlink_to(outside)
        with self.assertRaisesRegex(ContractError, "HV2-LOCK-ANCHOR"):
            with exclusive_file_lock(lock_path):
                self.fail("symlink lock anchor was admitted")
        lock_path.unlink()
        lock_path.mkdir()
        with self.assertRaisesRegex(ContractError, "HV2-LOCK-ANCHOR"):
            with exclusive_file_lock(lock_path):
                self.fail("directory lock anchor was admitted")

    def test_unserializable_json_is_stable_contract_error(self) -> None:
        with self.assertRaisesRegex(ContractError, "HV2-JSON-EMISSION"):
            canonical_json_bytes({"value": object()})

    def test_duplicate_key_is_red(self) -> None:
        with self.assertRaisesRegex(ContractError, "HV2-JSON-DUPLICATE-KEY"):
            decode_json_bytes(b'{"a": 1, "a": 2}\n')

    def test_bom_is_red(self) -> None:
        with self.assertRaisesRegex(ContractError, "HV2-JSON-BOM"):
            decode_json_bytes(b"\xef\xbb\xbf{}\n")

    def test_missing_or_double_eof_lf_is_red(self) -> None:
        for data in (b"{}", b"{}\n\n"):
            with self.subTest(data=data), self.assertRaisesRegex(ContractError, "HV2-JSON-EOF"):
                decode_json_bytes(data)

    def test_nonfinite_json_is_red(self) -> None:
        with self.assertRaisesRegex(ContractError, "HV2-JSON-NONFINITE"):
            decode_json_bytes(b'{"value": NaN}\n')

    def test_noncanonical_carrier_json_is_red(self) -> None:
        release_path = self.release / "release.json"
        value = load_json(release_path)
        release_path.write_text(json.dumps(value, sort_keys=False) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ContractError, "HV2-JSON-NONCANONICAL"):
            verify_release(self.release)

    def test_payload_tamper_is_red(self) -> None:
        (self.release / "payload" / "generation-1-contract.md").write_bytes(b"tampered\n")
        with self.assertRaisesRegex(ContractError, "HV2-CARRIER-ENTRY-DIGEST"):
            verify_release(self.release)

    def test_inventory_tamper_is_red_before_release_identity(self) -> None:
        inventory = load_json(self.release / "inventory.json", require_canonical=True)
        inventory["entries"][0]["size_bytes"] += 1
        (self.release / "inventory.json").write_bytes(canonical_json_bytes(inventory))
        with self.assertRaisesRegex(ContractError, "HV2-CARRIER-ENTRY-DIGEST"):
            verify_release(self.release)

    def test_boolean_size_is_not_integer(self) -> None:
        inventory_path = self.release / "inventory.json"
        release_path = self.release / "release.json"
        inventory = load_json(inventory_path, require_canonical=True)
        inventory["entries"][0]["size_bytes"] = True
        inventory_path.write_bytes(canonical_json_bytes(inventory))
        release = load_json(release_path, require_canonical=True)
        release["inventory_ref"]["sha256"] = sha256_file(inventory_path)
        release_path.write_bytes(canonical_json_bytes(release))
        with self.assertRaisesRegex(ContractError, "HV2-CARRIER-ENTRY-TYPE"):
            verify_release(self.release)

    def test_extra_root_entry_is_red(self) -> None:
        (self.release / "unexpected.txt").write_text("unexpected\n", encoding="utf-8")
        with self.assertRaisesRegex(ContractError, "HV2-CARRIER-ROOT-COVERAGE"):
            verify_release(self.release)

    def test_unsafe_paths_are_red(self) -> None:
        for value in ("../escape", "/absolute", "payload/../escape"):
            with self.subTest(value=value), self.assertRaisesRegex(ContractError, "HV2-CARRIER-UNSAFE-PATH"):
                _safe_relative_path(value)

    def test_deterministic_carrier_is_byte_identical(self) -> None:
        second = self.root / "release-second"
        build_release(self.source, second, SEAL)
        for relative in ("release.json", "inventory.json", "payload/generation-1-contract.md"):
            self.assertEqual((self.release / relative).read_bytes(), (second / relative).read_bytes())


class StateContractRedTests(ContractFixture):
    def test_after_pointer_interruption_is_structured_resumable_nonpass(self) -> None:
        self.create()
        with self.assertRaises(InjectedCrash):
            self.store.transition(
                item_id="item-0001",
                operation="update",
                sequence=2,
                observed_at="2026-08-08T12:03:00Z",
                actor="OWNER-LOCAL-001",
                inject_at="after_pointer_assertion",
            )
        result = self.store.verify("item-0001")
        self.assertEqual("degraded", result["classification"])
        self.assertFalse(result["writable"])
        self.assertTrue(result["resumable"])
        self.assertEqual(
            {
                "attempt_id": "attempt-update-0002",
                "operation": "update",
                "point": "after_pointer_assertion",
                "resume_action": "resume --target <project> --item-id item-0001 --operation update --sequence 2",
                "sequence": 2,
            },
            result["interruption"],
        )
        self.assertEqual("revision-0002", self.store.resume("item-0001", "update", 2)["revision_id"])

    def test_after_switch_interruption_is_structured_resumable_nonpass(self) -> None:
        self.create()
        with self.assertRaises(InjectedCrash):
            self.store.transition(
                item_id="item-0001",
                operation="update",
                sequence=2,
                observed_at="2026-08-08T12:03:00Z",
                actor="OWNER-LOCAL-001",
                inject_at="after_switch",
            )
        result = self.store.verify("item-0001")
        self.assertEqual("degraded", result["classification"])
        self.assertEqual("after_switch", result["interruption"]["point"])
        self.assertTrue(result["resumable"])
        self.assertEqual("revision-0002", self.store.resume("item-0001", "update", 2)["revision_id"])

    def test_later_recoverable_interruption_survives_earlier_same_attempt_abort_record(self) -> None:
        self.create()
        call = {
            "item_id": "item-0001",
            "operation": "update",
            "sequence": 2,
            "observed_at": "2026-08-08T12:03:00Z",
            "actor": "OWNER-LOCAL-001",
        }
        with self.assertRaises(InjectedCrash):
            self.store.transition(**call, inject_at="after_stage")
        with self.assertRaises(InjectedCrash):
            self.store.transition(**call, inject_at="after_pointer_assertion")
        result = self.store.verify("item-0001")
        self.assertTrue(result["resumable"])
        self.assertEqual("after_pointer_assertion", result["interruption"]["point"])
        self.assertEqual("revision-0002", self.store.resume("item-0001", "update", 2)["revision_id"])

    def test_resumed_attempt_with_deleted_binding_receipt_is_not_reclassified_as_resumable(self) -> None:
        self.create()
        with self.assertRaises(InjectedCrash):
            self.store.transition(
                item_id="item-0001",
                operation="update",
                sequence=2,
                observed_at="2026-08-08T12:03:00Z",
                actor="OWNER-LOCAL-001",
                inject_at="after_switch",
            )
        self.store.resume("item-0001", "update", 2)
        binding = self.target / ".harness-v2/items/item-0001/generations/1/binding-receipts/binding-attempt-update-0002.json"
        binding.unlink()
        with self.assertRaisesRegex(ContractError, "HV2-BINDING-RECEIPT"):
            self.store.verify("item-0001")
        with self.assertRaisesRegex(ContractError, "HV2-BINDING-RECEIPT"):
            self.store.resume("item-0001", "update", 2)
        self.assertFalse(binding.exists())

    def test_interruption_without_sealed_staging_is_nonresumable(self) -> None:
        self.create()
        with self.assertRaises(InjectedCrash):
            self.store.transition(
                item_id="item-0001",
                operation="update",
                sequence=2,
                observed_at="2026-08-08T12:03:00Z",
                actor="OWNER-LOCAL-001",
                inject_at="after_pointer_assertion",
            )
        shutil.rmtree(self.target / ".harness-v2/staging")
        result = self.store.verify("item-0001")
        self.assertEqual("degraded", result["classification"])
        self.assertFalse(result["resumable"])
        self.assertIsNone(result["interruption"])
        self.assertIn("interrupted-unresumable:attempt-update-0002:staging-evidence", result["degraded_reasons"])
        with self.assertRaisesRegex(ContractError, "HV2-NONWRITABLE"):
            self.store.resume("item-0001", "update", 2)

    def test_resume_rejects_unrelated_degraded_state_before_mutation(self) -> None:
        self.create()
        with self.assertRaises(InjectedCrash):
            self.store.transition(
                item_id="item-0001",
                operation="update",
                sequence=2,
                observed_at="2026-08-08T12:03:00Z",
                actor="OWNER-LOCAL-001",
                inject_at="after_pointer_assertion",
            )
        authority_path = self.target / ".harness-v2/authority.json"
        authority = load_json(authority_path, require_canonical=True)
        authority["unknown_member"] = True
        authority_path.write_bytes(canonical_json_bytes(authority))
        pointer_before = self.store._active_pointer("item-0001")
        with self.assertRaisesRegex(ContractError, "HV2-NONWRITABLE"):
            self.store.resume("item-0001", "update", 2)
        self.assertEqual(pointer_before, self.store._active_pointer("item-0001"))

    def test_detached_item_rejects_generic_transition_before_mutation(self) -> None:
        self.create()
        self.store.transition(
            item_id="item-0001",
            operation="detach",
            sequence=2,
            observed_at="2026-08-08T12:03:00Z",
            actor="OWNER-LOCAL-001",
        )
        pointer_before = self.store._active_pointer("item-0001")
        for operation, sequence, rollback_revision in (
            ("update", 3, None),
            ("rollback", 3, "revision-0001"),
            ("detach", 3, None),
        ):
            with self.subTest(operation=operation), self.assertRaisesRegex(
                ContractError, "HV2-ALREADY-DETACHED"
            ):
                self.store.transition(
                    item_id="item-0001",
                    operation=operation,
                    sequence=sequence,
                    observed_at="2026-08-08T12:04:00Z",
                    actor="OWNER-LOCAL-001",
                    rollback_revision=rollback_revision,
                )
            self.assertEqual(pointer_before, self.store._active_pointer("item-0001"))

    def test_canonical_record_symlink_is_rejected_before_read(self) -> None:
        self.create()
        revision = self.target / ".harness-v2/items/item-0001/generations/1/revisions/revision-0001.json"
        outside = self.root / "outside-revision.json"
        outside.write_bytes(revision.read_bytes())
        revision.unlink()
        revision.symlink_to(outside)
        with self.assertRaisesRegex(ContractError, "HV2-CANONICAL-SYMLINK"):
            self.store.verify("item-0001")

    def test_actual_replace_temp_suffix_is_named_residue(self) -> None:
        residue = self.target / ".harness-v2/items/item-0001/active-generation.json.hv2-tmp-deadbeef"
        residue.write_bytes(b"residue\n")
        result = self.store.verify("item-0001")
        self.assertIn(
            "temp-residue:items/item-0001/active-generation.json.hv2-tmp-deadbeef",
            result["degraded_reasons"],
        )

    def test_stable_root_reuse_is_red(self) -> None:
        with self.assertRaisesRegex(ContractError, "HV2-STABLE-ID-REUSE"):
            self.store.initialize(SEAL["authority_home_id"], "item-0001", "2026-08-08T12:03:00Z")

    def test_authority_home_mismatch_is_red(self) -> None:
        release = load_json(self.release / "release.json", require_canonical=True)
        release["authority_home_id"] = "different-home"
        (self.release / "release.json").write_bytes(canonical_json_bytes(release))
        with self.assertRaisesRegex(ContractError, "HV2-AUTHORITY-HOME"):
            self.create()

    def test_missing_assertion_required_field_is_red(self) -> None:
        generation_path = self.target / ".harness-v2/items/item-0001/generation-assertions/generation-assertion-0001.json"
        generation = load_json(generation_path, require_canonical=True)
        generation.pop("unavailable_scope")
        generation_path.write_bytes(canonical_json_bytes(generation))
        selector_path = self.target / ".harness-v2/items/item-0001/active-generation.json"
        selector = load_json(selector_path, require_canonical=True)
        selector["generation_assertion_ref"]["sha256"] = sha256_file(generation_path)
        selector_path.write_bytes(canonical_json_bytes(selector))
        with self.assertRaisesRegex(ContractError, "HV2-ASSERTION-REQUIRED-FIELD"):
            self.store.verify("item-0001")

    def test_unknown_additive_member_is_degraded_nonwritable(self) -> None:
        authority_path = self.target / ".harness-v2/authority.json"
        authority = load_json(authority_path, require_canonical=True)
        authority["future_member"] = {"preserve": True}
        authority_path.write_bytes(canonical_json_bytes(authority))
        result = self.store.verify("item-0001")
        self.assertEqual("degraded", result["classification"])
        self.assertFalse(result["writable"])
        self.assertFalse(result["finalizable"])
        with self.assertRaisesRegex(ContractError, "HV2-NONWRITABLE"):
            self.create()

    def test_unknown_generation_is_incompatible(self) -> None:
        identity_path = self.target / ".harness-v2/items/item-0001/identity.json"
        identity = load_json(identity_path, require_canonical=True)
        identity["schema_generation"] = 2
        identity_path.write_bytes(canonical_json_bytes(identity))
        result = self.store.verify("item-0001")
        self.assertEqual("incompatible", result["classification"])
        self.assertIsNone(result["current_revision_id"])

    def test_reference_digest_mismatch_is_red(self) -> None:
        self.create()
        lifecycle = self.target / ".harness-v2/items/item-0001/generations/1/assertions/lifecycle/assertion-lifecycle-0001.json"
        value = load_json(lifecycle, require_canonical=True)
        value["value"]["state"] = "corrupt"
        lifecycle.write_bytes(canonical_json_bytes(value))
        with self.assertRaisesRegex(ContractError, "HV2-REF-DIGEST"):
            self.store.verify("item-0001")

    def test_unreferenced_newer_currentness_does_not_select_current(self) -> None:
        self.create()
        path = self.target / ".harness-v2/items/item-0001/generations/1/assertions/currentness/assertion-currentness-9999.json"
        record = _base("facet-assertion", "assertion-currentness-9999", "item-0001", "2099-01-01T00:00:00Z")
        record.update({"facet": "currentness", "value": {"selected_by": "timestamp", "sequence": 9999}})
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(canonical_json_bytes(record))
        result = self.store.verify("item-0001")
        self.assertEqual("revision-0001", result["current_revision_id"])

    def test_same_local_id_in_different_record_kind_is_valid(self) -> None:
        path = self.target / ".harness-v2/items/item-0001/generations/1/assertions/relations/generation-assertion-0001.json"
        record = _base("facet-assertion", "generation-assertion-0001", "item-0001", "2026-08-08T12:02:30Z")
        record.update({"facet": "relations", "value": {"refs": []}})
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(canonical_json_bytes(record))
        self.assertEqual("pass", self.store.verify("item-0001")["classification"])

    def test_interruption_before_switch_preserves_prior_active(self) -> None:
        self.create()
        with self.assertRaises(InjectedCrash):
            self.store.transition(
                item_id="item-0001",
                operation="update",
                sequence=2,
                observed_at="2026-08-08T12:03:00Z",
                actor="OWNER-LOCAL-001",
                inject_at="after_pointer_assertion",
            )
        self.assertEqual("revision-0001", self.store._active_pointer("item-0001")["revision_ref"]["id"])
        resumed = self.store.resume("item-0001", "update", 2)
        self.assertEqual("revision-0002", resumed["revision_id"])
        self.assertEqual("revision-0002", self.store.verify("item-0001")["current_revision_id"])

    def test_staging_tamper_blocks_resume(self) -> None:
        self.create()
        with self.assertRaises(InjectedCrash):
            self.store.transition(
                item_id="item-0001",
                operation="update",
                sequence=2,
                observed_at="2026-08-08T12:03:00Z",
                actor="OWNER-LOCAL-001",
                inject_at="after_pointer_assertion",
            )
        staged = next((self.target / ".harness-v2/staging/attempt-update-0002/records").rglob("*.json"))
        staged.write_bytes(staged.read_bytes() + b" ")
        result = self.store.verify("item-0001")
        self.assertEqual("degraded", result["classification"])
        self.assertFalse(result["resumable"])
        with self.assertRaisesRegex(ContractError, "HV2-NONWRITABLE"):
            self.store.resume("item-0001", "update", 2)

    def test_resume_preflight_corruption_preserves_prior_pointer(self) -> None:
        self.create()
        with self.assertRaises(InjectedCrash):
            self.store.transition(
                item_id="item-0001",
                operation="update",
                sequence=2,
                observed_at="2026-08-08T12:03:00Z",
                actor="OWNER-LOCAL-001",
                inject_at="after_pointer_assertion",
            )
        acceptance = self.target / ".harness-v2/items/item-0001/generations/1/acceptances/acceptance-update-0002.json"
        value = load_json(acceptance, require_canonical=True)
        value["actor"] = "tampered"
        acceptance.write_bytes(canonical_json_bytes(value))
        with self.assertRaisesRegex(ContractError, "HV2-REF-DIGEST"):
            self.store.resume("item-0001", "update", 2)
        self.assertEqual("revision-0001", self.store._active_pointer("item-0001")["revision_ref"]["id"])

    def test_detach_is_logical_and_preserves_payload_history(self) -> None:
        self.create()
        self.store.transition(
            item_id="item-0001",
            operation="detach",
            sequence=2,
            observed_at="2026-08-08T12:03:00Z",
            actor="OWNER-LOCAL-001",
        )
        result = self.store.verify("item-0001")
        self.assertEqual("detached", result["lifecycle"])
        self.assertTrue((self.target / "docs/GENERATION-1-CONTRACT.md").is_file())
        self.assertTrue((self.target / ".harness-v2/items/item-0001/generations/1/revisions/revision-0001.json").is_file())
        self.assertTrue((self.target / ".harness-v2/items/item-0001/generations/1/tombstones/tombstone-0002.json").is_file())


if __name__ == "__main__":
    unittest.main()
