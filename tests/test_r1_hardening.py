from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import hv2ref.jsonio as jsonio
from hv2ref.carrier import PAYLOAD_PATH, build_release, verify_release
from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.jsonio import canonical_json_bytes, decode_json_bytes, load_json, replace_bytes, sha256_file
from hv2ref.state import StateStore, _base, _ref


SEAL = {
    "authority_home_id": "7d854f54-6538-4cd4-8961-2e2f50ef9653",
    "created_at": "2026-08-09T08:00:00Z",
    "inventory_id": "inventory-0001",
    "release_id": "release-0001",
}


class HardeningFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source.md"
        self.source.write_bytes(b"generation 1 production contract\n")
        self.release = self.root / "release"
        build_release(self.source, self.release, SEAL)
        self.target = self.root / "target"
        self.target.mkdir()
        self.store = StateStore(self.target)
        self.store.initialize(SEAL["authority_home_id"], "item-0001", "2026-08-09T08:01:00Z")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def transition(self, operation: str, sequence: int, **kwargs):
        return self.store.transition(
            item_id="item-0001",
            operation=operation,
            sequence=sequence,
            observed_at=f"2026-08-09T08:{sequence + 1:02d}:00Z",
            actor="OWNER-LOCAL-001",
            release_root=self.release if operation == "create" else None,
            **kwargs,
        )

    def create(self):
        return self.transition("create", 1)

    def rewrite(self, path: Path, value: dict) -> None:
        path.write_bytes(canonical_json_bytes(value))

    def rechain_create(self, *, accepted: bool | None = None, outcome: str | None = None) -> None:
        base = self.target / ".harness-v2/items/item-0001/generations/1"
        acceptance_path = base / "acceptances/acceptance-create-0001.json"
        result_path = base / "attempts/attempt-create-0001/result.json"
        revision_path = base / "revisions/revision-0001.json"
        pointer_path = base / "pointer-assertions/pointer-assertion-0001.json"
        binding_path = base / "binding-receipts/binding-attempt-create-0001.json"
        active_path = base / "active-pointer.json"

        acceptance = load_json(acceptance_path, require_canonical=True)
        if accepted is not None:
            acceptance["accepted"] = accepted
        self.rewrite(acceptance_path, acceptance)

        result = load_json(result_path, require_canonical=True)
        result["acceptance_ref"] = _ref(acceptance["record_id"], acceptance_path.read_bytes())
        if outcome is not None:
            result["outcome"] = outcome
        self.rewrite(result_path, result)

        revision = load_json(revision_path, require_canonical=True)
        revision["acceptance_ref"] = result["acceptance_ref"]
        revision["result_ref"] = _ref(result["record_id"], result_path.read_bytes())
        self.rewrite(revision_path, revision)

        pointer = load_json(pointer_path, require_canonical=True)
        pointer["revision_ref"] = _ref(revision["record_id"], revision_path.read_bytes())
        self.rewrite(pointer_path, pointer)

        binding = load_json(binding_path, require_canonical=True)
        binding["result_ref"] = revision["result_ref"]
        binding["revision_ref"] = pointer["revision_ref"]
        self.rewrite(binding_path, binding)

        active = load_json(active_path, require_canonical=True)
        active["pointer_assertion_ref"] = _ref(pointer["record_id"], pointer_path.read_bytes())
        active["revision_ref"] = pointer["revision_ref"]
        self.rewrite(active_path, active)


class SemanticIntegrityTests(HardeningFixture):
    def test_acceptance_false_remains_red_after_digest_rechain(self) -> None:
        self.create()
        self.rechain_create(accepted=False)
        with self.assertRaisesRegex(ContractError, "HV2-ACCEPTANCE-OUTCOME"):
            self.store.verify("item-0001")

    def test_failed_outcome_remains_red_after_digest_rechain(self) -> None:
        self.create()
        self.rechain_create(outcome="failed")
        with self.assertRaisesRegex(ContractError, "HV2-ACCEPTANCE-OUTCOME|HV2-REVISION-OUTCOME"):
            self.store.verify("item-0001")

    def test_target_payload_tamper_is_red(self) -> None:
        self.create()
        (self.target / "docs/GENERATION-1-CONTRACT.md").write_bytes(b"replacement\n")
        with self.assertRaisesRegex(ContractError, "HV2-PAYLOAD-DIGEST"):
            self.store.verify("item-0001")

    def test_pointer_fork_is_red(self) -> None:
        self.create()
        self.transition("update", 2)
        base = self.target / ".harness-v2/items/item-0001/generations/1/pointer-assertions"
        source = base / "pointer-assertion-0002.json"
        fork = load_json(source, require_canonical=True)
        fork["record_id"] = "pointer-assertion-fork"
        fork["pointer_assertion_id"] = "pointer-assertion-fork"
        self.rewrite(base / "pointer-assertion-fork.json", fork)
        with self.assertRaisesRegex(ContractError, "HV2-POINTER-HISTORY-CONTRADICTION"):
            self.store.verify("item-0001")

    def test_stale_resume_cannot_rewind_tip(self) -> None:
        self.create()
        with self.assertRaises(InjectedCrash):
            self.transition("update", 2, inject_at="after_pointer_assertion")
        self.store.resume("item-0001", "update", 2)
        self.transition("update", 3)
        with self.assertRaisesRegex(ContractError, "HV2-RESUME-NOT-TIP"):
            self.store.resume("item-0001", "update", 2)
        self.assertEqual("revision-0003", self.store.verify("item-0001")["current_revision_id"])

    def test_interruption_resume_and_binding_are_persisted(self) -> None:
        self.create()
        with self.assertRaises(InjectedCrash):
            self.transition("update", 2, inject_at="after_pointer_assertion")
        base = self.target / ".harness-v2/items/item-0001/generations/1"
        self.assertTrue((base / "interruptions/interruption-attempt-update-0002-after-pointer-assertion.json").is_file())
        self.store.resume("item-0001", "update", 2)
        self.assertTrue((base / "resumes/resume-attempt-update-0002.json").is_file())
        binding = load_json(base / "binding-receipts/binding-attempt-update-0002.json", require_canonical=True)
        self.assertEqual("unfinalized", binding["git_state"])

    def test_all_in_process_abort_points_have_forward_path(self) -> None:
        points = (
            "after_intent",
            "after_stage",
            "after_acceptance",
            "after_result",
            "after_revision",
            "after_pointer_assertion",
            "after_switch",
        )
        for point in points:
            with self.subTest(point=point), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                source = root / "source.md"
                source.write_bytes(b"production contract\n")
                release = root / "release"
                build_release(source, release, SEAL)
                target = root / "target"
                target.mkdir()
                store = StateStore(target)
                store.initialize(SEAL["authority_home_id"], "item-0001", "2026-08-09T09:00:00Z")
                call = dict(
                    item_id="item-0001",
                    operation="create",
                    sequence=1,
                    observed_at="2026-08-09T09:01:00Z",
                    actor="OWNER-LOCAL-001",
                    release_root=release,
                )
                with self.assertRaises(InjectedCrash):
                    store.transition(**call, inject_at=point)
                if point in {"after_pointer_assertion", "after_switch"}:
                    store.resume("item-0001", "create", 1)
                else:
                    changed_time = {**call, "observed_at": "2026-08-09T09:02:00Z"}
                    with self.assertRaisesRegex(ContractError, "HV2-IMMUTABLE-CONTRADICTION"):
                        store.transition(**changed_time)
                    store.transition(**call)
                self.assertEqual("revision-0001", store.verify("item-0001")["current_revision_id"])

    def test_rollback_source_is_digest_bound_and_intent_is_rollback(self) -> None:
        self.create()
        self.transition("update", 2)
        self.transition("rollback", 3, rollback_revision="revision-0001")
        base = self.target / ".harness-v2/items/item-0001/generations/1"
        intent = load_json(base / "attempts/attempt-rollback-0003/intent.json", require_canonical=True)
        currentness = load_json(base / "assertions/currentness/assertion-currentness-0003.json", require_canonical=True)
        intent_facet = load_json(base / "assertions/intent/assertion-intent-0003.json", require_canonical=True)
        self.assertEqual("revision-0001", intent["rollback_source_ref"]["id"])
        self.assertEqual(intent["rollback_source_ref"], currentness["value"]["forward_rollback_of"])
        self.assertEqual("rollback", intent_facet["value"]["operation"])


class CarrierAndInputBoundaryTests(HardeningFixture):
    def test_root_member_symlinks_are_rejected_before_external_read(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "generation-1-contract.md").write_bytes(b"outside\n")
        shutil.rmtree(self.release / "payload")
        (self.release / "payload").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ContractError, "HV2-CARRIER-ROOT-MEMBER-TYPE"):
            verify_release(self.release)

    def test_lexical_path_alias_is_rejected(self) -> None:
        inventory_path = self.release / "inventory.json"
        release_path = self.release / "release.json"
        inventory = load_json(inventory_path, require_canonical=True)
        inventory["entries"][0]["path"] = "payload/./generation-1-contract.md"
        self.rewrite(inventory_path, inventory)
        release = load_json(release_path, require_canonical=True)
        release["inventory_ref"]["sha256"] = sha256_file(inventory_path)
        self.rewrite(release_path, release)
        with self.assertRaisesRegex(ContractError, "HV2-CARRIER-UNSAFE-PATH"):
            verify_release(self.release)

    def test_empty_payload_directory_is_rejected(self) -> None:
        (self.release / "payload/empty").mkdir()
        with self.assertRaisesRegex(ContractError, "HV2-CARRIER-EMPTY-DIRECTORY"):
            verify_release(self.release)

    def test_invalid_seal_leaves_no_partial_output(self) -> None:
        output = self.root / "bad-release"
        with self.assertRaisesRegex(ContractError, "HV2-CARRIER-SEAL"):
            build_release(self.source, output, {"release_id": "only"})
        self.assertFalse(output.exists())

    def test_item_id_and_sequence_are_bounded(self) -> None:
        for item_id in ("", "../../escaped", "a/b", ".", "a" * 65):
            with self.subTest(item_id=item_id), self.assertRaisesRegex(ContractError, "HV2-ITEM-ID"):
                StateStore(self.root / "other").initialize(SEAL["authority_home_id"], item_id, "2026-08-09T00:00:00Z")
        for sequence in (-1, 0, 10000, True):
            with self.subTest(sequence=sequence), self.assertRaisesRegex(ContractError, "HV2-SEQUENCE"):
                self.store.transition(
                    item_id="item-0001",
                    operation="create",
                    sequence=sequence,
                    observed_at="2026-08-09T00:00:00Z",
                    actor="OWNER-LOCAL-001",
                    release_root=self.release,
                )

    def test_operation_specific_options_fail_closed(self) -> None:
        with self.assertRaisesRegex(ContractError, "HV2-ROLLBACK-OPTION"):
            self.transition("update", 2, rollback_revision="revision-0001")
        with self.assertRaisesRegex(ContractError, "HV2-RELEASE-OPTION"):
            self.store.transition(
                item_id="item-0001",
                operation="update",
                sequence=2,
                observed_at="2026-08-09T08:03:00Z",
                actor="OWNER-LOCAL-001",
                release_root=self.release,
            )


class JsonAndClassificationTests(HardeningFixture):
    def test_writer_rejects_nonfinite_and_reader_normalizes_limits(self) -> None:
        with self.assertRaisesRegex(ContractError, "HV2-JSON-EMISSION"):
            canonical_json_bytes({"value": float("inf")})
        huge_integer = b'{"value": ' + b"9" * 1100 + b"}\n"
        with self.assertRaisesRegex(ContractError, "HV2-JSON-LIMIT"):
            decode_json_bytes(huge_integer)
        deep = ("[" * 140 + "0" + "]" * 140 + "\n").encode()
        with self.assertRaisesRegex(ContractError, "HV2-JSON-LIMIT"):
            decode_json_bytes(deep)

    def test_damaged_staging_is_reported_without_poisoning_canonical_state(self) -> None:
        self.create()
        staged = next((self.target / ".harness-v2/staging/attempt-create-0001/records").rglob("*.json"))
        staged.write_bytes(staged.read_bytes() + b" ")
        result = self.store.verify("item-0001")
        self.assertEqual("pass", result["classification"])
        self.assertEqual("damaged", result["staging_inventories"][0]["status"])

    def test_temp_residue_is_visible_and_nonfinalizable(self) -> None:
        self.create()
        residue = self.target / ".harness-v2/items/item-0001/generations/1/.active-pointer.json.hv2-tmp"
        residue.write_bytes(b"residue")
        result = self.store.verify("item-0001")
        self.assertEqual("degraded", result["classification"])
        self.assertFalse(result["finalizable"])

    def test_nonempty_unavailable_scope_is_degraded_and_nonwritable(self) -> None:
        generation_path = self.target / ".harness-v2/items/item-0001/generation-assertions/generation-assertion-0001.json"
        selector_path = self.target / ".harness-v2/items/item-0001/active-generation.json"
        generation = load_json(generation_path, require_canonical=True)
        generation["unavailable_scope"] = ["target-repository:probe"]
        self.rewrite(generation_path, generation)
        selector = load_json(selector_path, require_canonical=True)
        selector["generation_assertion_ref"] = _ref(generation["record_id"], generation_path.read_bytes())
        self.rewrite(selector_path, selector)

        result = self.store.verify("item-0001")
        self.assertEqual("degraded", result["classification"])
        self.assertFalse(result["writable"])
        self.assertIn("generation-assertion-0001.json:unavailable-scope", result["degraded_reasons"])

    def test_canonical_tree_extra_paths_are_degraded(self) -> None:
        self.create()
        extras = (
            self.target / ".harness-v2/items/item-0001/notes.txt",
            self.target / ".harness-v2/notes.json",
            self.target / ".harness-v2/items/item-0002/identity.json",
        )
        for path in extras:
            with self.subTest(path=path.relative_to(self.target).as_posix()):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"extra\n")
                result = self.store.verify("item-0001")
                self.assertEqual("degraded", result["classification"])
                self.assertFalse(result["writable"])
                self.assertTrue(any(reason.startswith("canonical-tree-extra:") for reason in result["degraded_reasons"]))
                path.unlink()

    def test_fullfsync_classification_is_explicit(self) -> None:
        with (
            mock.patch.object(jsonio.sys, "platform", "darwin"),
            mock.patch.object(jsonio.os, "fsync"),
            mock.patch.object(jsonio.fcntl, "F_FULLFSYNC", 51, create=True),
            mock.patch.object(jsonio.fcntl, "fcntl") as fullfsync,
        ):
            self.assertEqual("pass", jsonio._sync_fd(7)["fullfsync"])
            fullfsync.side_effect = OSError(5, "io")
            self.assertEqual("error:5", jsonio._sync_fd(7)["fullfsync"])
        with (
            mock.patch.object(jsonio.sys, "platform", "darwin"),
            mock.patch.object(jsonio.os, "fsync"),
            mock.patch.object(jsonio.fcntl, "F_FULLFSYNC", None, create=True),
        ):
            self.assertEqual("unavailable", jsonio._sync_fd(7)["fullfsync"])

    def test_new_ancestor_chain_is_directory_synced(self) -> None:
        destination = self.root / "ancestor-a/ancestor-b/ancestor-c/value.json"
        with mock.patch.object(jsonio, "sync_directory", return_value="pass") as sync:
            jsonio._ensure_parent(destination)
        expected = [
            mock.call(self.root),
            mock.call(self.root / "ancestor-a"),
            mock.call(self.root / "ancestor-a"),
            mock.call(self.root / "ancestor-a/ancestor-b"),
            mock.call(self.root / "ancestor-a/ancestor-b"),
            mock.call(self.root / "ancestor-a/ancestor-b/ancestor-c"),
        ]
        self.assertEqual(expected, sync.call_args_list)

    def test_replace_temp_is_created_in_destination_parent(self) -> None:
        destination = self.root / "same-parent/value.txt"
        destination.parent.mkdir()
        destination.write_bytes(b"old\n")
        original_replace = jsonio.os.replace
        observed: list[tuple[Path, Path]] = []

        def capture(source, target):
            observed.append((Path(source), Path(target)))
            return original_replace(source, target)

        with (
            mock.patch.object(jsonio, "_sync_fd", return_value={"fsync": "pass", "fullfsync": "not-applicable"}),
            mock.patch.object(jsonio, "sync_directory", return_value="pass"),
            mock.patch.object(jsonio.os, "replace", side_effect=capture),
        ):
            replace_bytes(destination, b"new\n")
        self.assertEqual(1, len(observed))
        self.assertEqual(observed[0][0].parent, observed[0][1].parent)
        self.assertEqual(destination.parent, observed[0][0].parent)

    def test_unknown_canonical_json_role_is_red(self) -> None:
        path = self.target / ".harness-v2/items/item-0001/generations/1/orphan.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        self.rewrite(path, {"schema_generation": 1})
        with self.assertRaisesRegex(ContractError, "HV2-CANONICAL-JSON-ROLE"):
            self.store.verify("item-0001")

    def test_cli_distinguishes_usage_contract_and_classification(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")

        def cli(*args: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [sys.executable, "-m", "hv2ref.cli", *args],
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )

        usage = cli("transition")
        self.assertEqual(2, usage.returncode)
        contract = cli(
            "transition",
            "--target",
            str(self.target),
            "--item-id",
            "item-0001",
            "--operation",
            "create",
            "--sequence",
            "0",
            "--observed-at",
            "2026-08-09T00:00:00Z",
            "--actor",
            "OWNER-LOCAL-001",
            "--release",
            str(self.release),
        )
        self.assertEqual(65, contract.returncode)

        authority_path = self.target / ".harness-v2/authority.json"
        authority = load_json(authority_path, require_canonical=True)
        authority["future"] = True
        self.rewrite(authority_path, authority)
        degraded = cli("verify-state", "--target", str(self.target), "--item-id", "item-0001")
        self.assertEqual(10, degraded.returncode)


if __name__ == "__main__":
    unittest.main()
