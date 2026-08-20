from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.intent import IntentStore, classify_entry
from hv2ref.jsonio import canonical_json_bytes, load_json, sha256_file


def known(value: object) -> dict[str, object]:
    return {"status": "known", "value": value}


def unresolved(status: str = "unknown", owner: str = "OWNER-LOCAL-001") -> dict[str, str]:
    return {"owner": owner, "status": status}


def content(*, gaps: list[dict[str, object]] | None = None, vacuous: bool = False) -> dict[str, object]:
    facets: dict[str, object]
    if vacuous:
        facets = {
            "acceptance_oracle": unresolved(),
            "destination": unresolved("deferred"),
            "expected_outcome": unresolved(),
            "forbidden_scope": unresolved("deferred"),
            "goal": unresolved(),
            "scope": unresolved(),
        }
    else:
        facets = {
            "acceptance_oracle": known(["focused and full suites pass"]),
            "destination": known("private reference implementation"),
            "expected_outcome": known(["accepted intent is exact-revision bound"]),
            "forbidden_scope": known(["public promotion", "adopter mutation"]),
            "goal": known("preserve a human-accepted intent"),
            "scope": known(["standalone intent records"]),
        }
    return {
        "acceptance_authority": "OWNER-LOCAL-001",
        "actor": "OWNER-LOCAL-001",
        "facets": facets,
        "gaps": [] if gaps is None else gaps,
        "statements": [
            {"kind": "fact", "owner": "DR-831", "text": "StateStore remains unchanged"},
            {"kind": "human-decision", "owner": "OWNER-LOCAL-001", "text": "A-minimal is approved"},
            {"kind": "assumption", "owner": "OWNER-LOCAL-001", "text": "future item linking may change vocabulary"},
        ],
    }


def gap(gap_id: str, *, depends_on: list[str] | None = None, material: bool = True, status: str = "unresolved") -> dict[str, object]:
    return {
        "depends_on": [] if depends_on is None else depends_on,
        "gap_id": gap_id,
        "material": material,
        "owner": "OWNER-LOCAL-001",
        "status": status,
    }


class GuidedIntentFormationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.target = Path(self.temp.name)
        self.store = IntentStore(self.target)
        self.store.initialize("AUTH-HOME-INTENT-001", "2026-08-19T10:00:00+09:00")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def draft(self, sequence: int = 1, **overrides: object) -> dict[str, object]:
        draft_content = content()
        draft_content.update(overrides)
        return self.store.create_draft(
            intent_id="INTENT-001",
            sequence=sequence,
            observed_at=f"2026-08-19T10:0{sequence}:00+09:00",
            content=draft_content,
        )

    def accept(self, draft: dict[str, object], **overrides: object) -> dict[str, object]:
        arguments: dict[str, object] = {
            "acceptance_id": f"acceptance-{draft['sequence']:04d}",
            "actor": "OWNER-LOCAL-001",
            "intent_id": "INTENT-001",
            "observed_at": "2026-08-19T10:10:00+09:00",
            "revision_id": draft["revision_id"],
            "revision_sha256": draft["revision_sha256"],
            "supersedes_ref": None,
        }
        arguments.update(overrides)
        return self.store.accept(**arguments)

    def test_non_consequential_entry_creates_no_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            result = classify_entry("non-consequential", [])
            self.assertEqual({"artifact_required": False, "route": "non-consequential"}, result)
            self.assertEqual([], list(target.iterdir()))

    def test_direct_entry_acceptance_and_manual_reader(self) -> None:
        draft = self.draft()
        self.assertEqual("direct-entry", draft["route"])
        accepted = self.accept(draft)
        verified = self.store.verify("INTENT-001")
        self.assertEqual("pass", verified["classification"])
        self.assertEqual("revision-0001", verified["current_accepted_revision_id"])
        self.assertTrue(verified["actionable"])
        self.assertEqual(accepted["selection_ref"], verified["current_selection_ref"])

    def test_gap_graph_routes_bounded_and_dependency_ordered(self) -> None:
        bounded = self.store.create_draft(
            "BOUNDED", 1, "2026-08-19T10:01:00+09:00", content(gaps=[gap("G1"), gap("G2")])
        )
        ordered = self.store.create_draft(
            "ORDERED", 1, "2026-08-19T10:02:00+09:00", content(gaps=[gap("G1"), gap("G2", depends_on=["G1"])])
        )
        self.assertEqual("bounded-clarification", bounded["route"])
        self.assertEqual("dependency-ordered-clarification", ordered["route"])

    def test_gap_graph_cycle_and_missing_dependency_are_red(self) -> None:
        for intent_id, gaps in (
            ("CYCLE", [gap("G1", depends_on=["G2"]), gap("G2", depends_on=["G1"])]),
            ("MISSING", [gap("G1", depends_on=["NOPE"])]),
        ):
            with self.subTest(intent_id=intent_id), self.assertRaises(ContractError):
                self.store.create_draft(intent_id, 1, "2026-08-19T10:01:00+09:00", content(gaps=gaps))

    def test_missing_required_facet_and_ownerless_unknown_are_red(self) -> None:
        missing = content()
        del missing["facets"]["acceptance_oracle"]
        with self.assertRaises(ContractError):
            self.store.create_draft("MISSING", 1, "2026-08-19T10:01:00+09:00", missing)
        ownerless = content()
        ownerless["facets"]["goal"] = {"status": "unknown"}
        with self.assertRaises(ContractError):
            self.store.create_draft("OWNERLESS", 1, "2026-08-19T10:01:00+09:00", ownerless)

    def test_unaccepted_and_interrupted_draft_remain_readable_not_actionable(self) -> None:
        with self.assertRaises(InjectedCrash):
            self.store.create_draft(
                "INTERRUPTED", 1, "2026-08-19T10:01:00+09:00", content(), inject_at="after-draft"
            )
        resumed = self.store.create_draft("INTERRUPTED", 1, "2026-08-19T10:01:00+09:00", content())
        self.assertEqual("revision-0001", resumed["revision_id"])
        shown = self.store.show("INTERRUPTED", "revision-0001")
        self.assertEqual("draft-unaccepted", shown["state"])
        self.assertFalse(shown["actionable"])
        self.assertIsNone(self.store.verify("INTERRUPTED")["current_accepted_revision_id"])

    def test_wrong_digest_and_actor_are_red(self) -> None:
        draft = self.draft()
        with self.assertRaises(ContractError):
            self.accept(draft, revision_sha256="0" * 64)
        with self.assertRaises(ContractError):
            self.accept(draft, actor="AGENT-SELF")

    def test_material_gap_blocks_acceptance(self) -> None:
        draft = self.store.create_draft(
            "GAPPED", 1, "2026-08-19T10:01:00+09:00", content(gaps=[gap("G1")])
        )
        with self.assertRaises(ContractError):
            self.store.accept(
                "GAPPED", draft["revision_id"], draft["revision_sha256"], "acceptance-0001",
                "OWNER-LOCAL-001", "2026-08-19T10:02:00+09:00"
            )

    def test_revision_race_binds_only_named_revision(self) -> None:
        first = self.draft()
        second = self.draft(sequence=2)
        self.accept(first)
        verified = self.store.verify("INTENT-001")
        self.assertEqual("revision-0001", verified["current_accepted_revision_id"])
        self.assertEqual("draft-unaccepted", self.store.show("INTENT-001", second["revision_id"])["state"])

    def test_second_acceptance_requires_exact_supersede_and_reacceptance(self) -> None:
        first = self.draft()
        accepted = self.accept(first)
        second = self.draft(sequence=2)
        self.assertEqual("revision-0001", self.store.verify("INTENT-001")["current_accepted_revision_id"])
        with self.assertRaises(ContractError):
            self.accept(second, acceptance_id="acceptance-0002")
        self.accept(second, acceptance_id="acceptance-0002", supersedes_ref=accepted["selection_ref"])
        self.assertEqual("revision-0002", self.store.verify("INTENT-001")["current_accepted_revision_id"])

    def test_acceptance_interruption_is_partial_and_exact_retry_recovers(self) -> None:
        draft = self.draft()
        with self.assertRaises(InjectedCrash):
            self.accept(draft, inject_at="after-acceptance")
        partial = self.store.verify("INTENT-001")
        self.assertEqual("partial", partial["classification"])
        self.assertEqual(["acceptance-0001"], partial["pending_acceptance_ids"])
        self.assertIsNone(partial["current_accepted_revision_id"])
        self.accept(draft)
        self.assertEqual("pass", self.store.verify("INTENT-001")["classification"])

    def test_selection_interruption_preserves_prior_current_and_retry_switches(self) -> None:
        first = self.draft()
        first_acceptance = self.accept(first)
        second = self.draft(sequence=2)
        with self.assertRaises(InjectedCrash):
            self.accept(
                second,
                acceptance_id="acceptance-0002",
                supersedes_ref=first_acceptance["selection_ref"],
                inject_at="after-selection",
            )
        partial = self.store.verify("INTENT-001")
        self.assertEqual("partial", partial["classification"])
        self.assertEqual("revision-0001", partial["current_accepted_revision_id"])
        self.assertEqual(["selection-0002"], partial["pending_selection_ids"])
        self.assertEqual("selection-pending", self.store.show("INTENT-001", "revision-0002")["state"])
        self.accept(second, acceptance_id="acceptance-0002", supersedes_ref=first_acceptance["selection_ref"])
        self.assertEqual("revision-0002", self.store.verify("INTENT-001")["current_accepted_revision_id"])

    def test_pending_selection_rejects_new_acceptance_and_exact_retry_recovers(self) -> None:
        first = self.draft()
        first_acceptance = self.accept(first)
        second = self.draft(sequence=2)
        with self.assertRaises(InjectedCrash):
            self.accept(
                second,
                acceptance_id="acceptance-0002",
                supersedes_ref=first_acceptance["selection_ref"],
                inject_at="after-selection",
            )
        partial = self.store.verify("INTENT-001")
        with self.assertRaisesRegex(ContractError, "HV2-INTENT-SELECTION-RECOVERY"):
            self.accept(
                second,
                acceptance_id="acceptance-0003",
                supersedes_ref=first_acceptance["selection_ref"],
            )
        self.assertEqual(partial, self.store.verify("INTENT-001"))
        self.assertFalse(
            (
                self.target
                / ".harness-v2-intents"
                / "INTENT-001"
                / "acceptances"
                / "acceptance-0003.json"
            ).exists()
        )
        self.accept(second, acceptance_id="acceptance-0002", supersedes_ref=first_acceptance["selection_ref"])
        self.assertEqual("pass", self.store.verify("INTENT-001")["classification"])

    def test_vacuous_acceptance_is_red(self) -> None:
        draft = self.store.create_draft("VACUOUS", 1, "2026-08-19T10:01:00+09:00", content(vacuous=True))
        with self.assertRaises(ContractError):
            self.store.accept(
                "VACUOUS", draft["revision_id"], draft["revision_sha256"], "acceptance-0001",
                "OWNER-LOCAL-001", "2026-08-19T10:02:00+09:00"
            )

    def test_partial_acceptance_tamper_is_red(self) -> None:
        draft = self.draft()
        accepted = self.accept(draft)
        acceptance_path = self.target / ".harness-v2-intents" / "INTENT-001" / "acceptances" / "acceptance-0001.json"
        value = load_json(acceptance_path, require_canonical=True)
        value["accepted_facets"] = ["goal"]
        acceptance_path.write_bytes(canonical_json_bytes(value))
        with self.assertRaises(ContractError):
            self.store.verify("INTENT-001")
        self.assertIsNotNone(accepted)

    def test_abandoned_drafts_never_become_current_by_recency(self) -> None:
        self.draft()
        self.draft(sequence=2)
        verified = self.store.verify("INTENT-001")
        self.assertEqual(["revision-0001", "revision-0002"], verified["draft_revision_ids"])
        self.assertIsNone(verified["current_accepted_revision_id"])

    def test_extra_tree_and_reference_tamper_fail_closed(self) -> None:
        draft = self.draft()
        self.accept(draft)
        extra = self.target / ".harness-v2-intents" / "INTENT-001" / "latest.json"
        extra.write_bytes(b"{}\n")
        with self.assertRaises(ContractError):
            self.store.verify("INTENT-001")

    def test_symlinked_intent_home_member_is_red(self) -> None:
        with tempfile.TemporaryDirectory() as external_dir:
            alias = self.target / ".harness-v2-intents" / "ALIASED"
            alias.symlink_to(Path(external_dir), target_is_directory=True)
            with self.assertRaises(ContractError):
                self.store.create_draft("ALIASED", 1, "2026-08-19T10:01:00+09:00", content())

    def test_existing_state_tree_is_not_touched(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            existing = target / ".harness-v2" / "sentinel.json"
            existing.parent.mkdir()
            existing.write_bytes(b'{"generation":1}\n')
            before = sha256_file(existing)
            store = IntentStore(target)
            store.initialize("AUTH-OTHER", "2026-08-19T10:00:00+09:00")
            store.create_draft("NO-TOUCH", 1, "2026-08-19T10:01:00+09:00", content())
            self.assertEqual(before, sha256_file(existing))

    def test_same_input_is_byte_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as left_dir, tempfile.TemporaryDirectory() as right_dir:
            paths = []
            for directory in (left_dir, right_dir):
                store = IntentStore(Path(directory))
                store.initialize("AUTH-DETERMINISTIC", "2026-08-19T10:00:00+09:00")
                store.create_draft("SAME", 1, "2026-08-19T10:01:00+09:00", content())
                paths.append(Path(directory) / ".harness-v2-intents" / "SAME" / "drafts" / "revision-0001.json")
            self.assertEqual(paths[0].read_bytes(), paths[1].read_bytes())

    def test_cli_is_non_interactive_and_exposes_bounded_operations(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "hv2ref.cli", "--help"],
            cwd=Path(__file__).parents[1],
            env={**os.environ, "PYTHONPATH": "src"},
            capture_output=True,
            check=True,
            text=True,
        )
        for command in ("init-intent-home", "create-intent-draft", "show-intent", "accept-intent", "verify-intent"):
            self.assertIn(command, result.stdout)
        self.assertNotIn("interview", result.stdout.lower())

    def test_cli_end_to_end_uses_files_and_exact_refs(self) -> None:
        repository = Path(__file__).parents[1]
        environment = {**os.environ, "PYTHONPATH": "src"}
        input_path = self.target / "intent-input.json"
        input_path.write_bytes(canonical_json_bytes(content()))

        def run(*arguments: str) -> dict[str, object]:
            result = subprocess.run(
                [sys.executable, "-m", "hv2ref.cli", *arguments],
                cwd=repository,
                env=environment,
                capture_output=True,
                check=True,
                text=True,
            )
            return json.loads(result.stdout)

        cli_target = self.target / "cli-target"
        run(
            "init-intent-home", "--target", str(cli_target), "--authority-home-id", "AUTH-CLI",
            "--observed-at", "2026-08-19T10:00:00+09:00",
        )
        draft = run(
            "create-intent-draft", "--target", str(cli_target), "--intent-id", "CLI-INTENT",
            "--sequence", "1", "--observed-at", "2026-08-19T10:01:00+09:00", "--input", str(input_path),
        )
        shown = run(
            "show-intent", "--target", str(cli_target), "--intent-id", "CLI-INTENT",
            "--revision-id", "revision-0001",
        )
        self.assertEqual("draft-unaccepted", shown["state"])
        run(
            "accept-intent", "--target", str(cli_target), "--intent-id", "CLI-INTENT",
            "--revision-id", "revision-0001", "--revision-sha256", str(draft["revision_sha256"]),
            "--acceptance-id", "acceptance-0001", "--actor", "OWNER-LOCAL-001",
            "--observed-at", "2026-08-19T10:02:00+09:00",
        )
        verified = run("verify-intent", "--target", str(cli_target), "--intent-id", "CLI-INTENT")
        self.assertEqual("revision-0001", verified["current_accepted_revision_id"])

        audited = subprocess.run(
            [sys.executable, "-I", "tests/fixtures/intent_plain_auditor.py", str(cli_target), "CLI-INTENT"],
            cwd=repository,
            env=os.environ,
            capture_output=True,
            check=True,
            text=True,
        )
        plain = json.loads(audited.stdout)
        self.assertEqual("pass", plain["classification"])
        self.assertEqual("revision-0001", plain["revision_id"])


if __name__ == "__main__":
    unittest.main()
