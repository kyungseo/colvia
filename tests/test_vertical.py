from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from hv2ref.carrier import build_release
from hv2ref.errors import InjectedCrash
from hv2ref.state import StateStore


SEAL = {
    "authority_home_id": "7d854f54-6538-4cd4-8961-2e2f50ef9653",
    "created_at": "2026-08-08T12:00:00Z",
    "inventory_id": "inventory-0001",
    "release_id": "release-0001",
}


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, check=True, text=True, capture_output=True)
    return result.stdout.strip()


class MinimumProductionVertical(unittest.TestCase):
    def test_create_update_interruption_rollback_detach_git_zero_pack(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "generation-1-contract.md"
            source.write_bytes(b"real project-owned generation 1 contract\n")
            release = root / "hv2-reference-release"
            build_release(source, release, SEAL)

            target = root / "target"
            target.mkdir()
            git(target, "init", "-b", "main")
            git(target, "config", "user.name", "Harness v2 Local Fixture")
            git(target, "config", "user.email", "harness-v2-fixture@example.invalid")
            (target / "README.md").write_text("# Disposable private target\n", encoding="utf-8")
            git(target, "add", "README.md")
            git(target, "commit", "-m", "fixture: initialize disposable target")

            store = StateStore(target)
            store.initialize(SEAL["authority_home_id"], "item-0001", "2026-08-08T12:01:00Z")
            created = store.transition(
                item_id="item-0001",
                operation="create",
                sequence=1,
                observed_at="2026-08-08T12:02:00Z",
                actor="OWNER-LOCAL-001",
                release_root=release,
            )
            self.assertEqual("complete", created["binding_completion"])
            self.assertIn(".harness-v2", git(target, "status", "--short"))
            ignored_probe = target / ".harness-v2/staging/attempt-create-0001/inventory.json"
            self.assertEqual(str(ignored_probe.relative_to(target)), git(target, "check-ignore", str(ignored_probe.relative_to(target))))
            git(target, "add", ".harness-v2", "docs/GENERATION-1-CONTRACT.md")
            git(target, "commit", "-m", "fixture: finalize create binding")
            self.assertEqual("", git(target, "status", "--short"))

            with self.assertRaises(InjectedCrash):
                store.transition(
                    item_id="item-0001",
                    operation="update",
                    sequence=2,
                    observed_at="2026-08-08T12:03:00Z",
                    actor="OWNER-LOCAL-001",
                    inject_at="after_pointer_assertion",
                )
            self.assertEqual("revision-0001", store._active_pointer("item-0001")["revision_ref"]["id"])
            resumed = store.resume("item-0001", "update", 2)
            self.assertEqual("complete-after-resume", resumed["binding_completion"])
            self.assertEqual("revision-0002", store.verify("item-0001")["current_revision_id"])
            self.assertNotEqual("", git(target, "status", "--short"))
            git(target, "add", ".harness-v2")
            git(target, "commit", "-m", "fixture: finalize resumed update")

            rolled_back = store.transition(
                item_id="item-0001",
                operation="rollback",
                sequence=3,
                observed_at="2026-08-08T12:04:00Z",
                actor="OWNER-LOCAL-001",
                rollback_revision="revision-0001",
            )
            self.assertEqual("revision-0003", rolled_back["revision_id"])
            self.assertTrue((target / ".harness-v2/items/item-0001/generations/1/revisions/revision-0001.json").is_file())
            git(target, "add", ".harness-v2")
            git(target, "commit", "-m", "fixture: finalize forward rollback")

            detached = store.transition(
                item_id="item-0001",
                operation="detach",
                sequence=4,
                observed_at="2026-08-08T12:05:00Z",
                actor="OWNER-LOCAL-001",
            )
            self.assertEqual("revision-0004", detached["revision_id"])
            final = store.verify("item-0001")
            self.assertEqual("pass", final["classification"])
            self.assertEqual("detached", final["lifecycle"])
            self.assertEqual("revision-0004", final["current_revision_id"])
            self.assertTrue((target / "docs/GENERATION-1-CONTRACT.md").is_file())
            self.assertFalse(any(path.name in {"packs", "adapters", "providers"} for path in target.rglob("*")))
            git(target, "add", ".harness-v2")
            git(target, "commit", "-m", "fixture: finalize logical detach")
            self.assertEqual("", git(target, "status", "--short"))
            self.assertEqual("5", git(target, "rev-list", "--count", "HEAD"))


if __name__ == "__main__":
    unittest.main()
