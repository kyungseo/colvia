import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


@unittest.skipUnless(sys.platform == "darwin", "requires macOS system tools")
class ReadOnlyVerifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.root = self.base / "runtime"
        self.root.mkdir()
        self.file = self.root / "code"
        self.file.write_bytes(b"code")
        self.file.chmod(0o400)
        (self.root / "link").symlink_to("code")
        self.root.chmod(0o500)
        self.addCleanup(self.root.chmod, 0o700)
        self.scratch = self.base / "checks"
        self.scratch.mkdir(mode=0o500)
        self.addCleanup(self.scratch.chmod, 0o700)
        self.objects = self.base / "objects"
        self.objects.write_text("Directory|500|.|\nRegular File|400|./code|\nSymbolic Link|-|./link|code\n")
        self.hashes = self.base / "files"
        self.hashes.write_text(hashlib.sha256(b"code").hexdigest() + "  code\n")

    def verify(self):
        script = Path(__file__).resolve().parents[1] / "distribution/verify-macos-tree.sh"
        completed = subprocess.run(["/bin/bash", script, self.root, self.objects, self.hashes, self.scratch],
                                   capture_output=True, timeout=10)
        self.assertEqual(list(self.scratch.iterdir()), [])
        return completed.returncode

    def test_read_only_success_and_tampered_bytes(self):
        self.assertEqual(self.verify(), 0)
        self.file.chmod(0o600)
        self.assertNotEqual(self.verify(), 0)
        self.file.write_bytes(b"wrong")
        self.file.chmod(0o400)
        self.assertNotEqual(self.verify(), 0)

    def test_link_count_target_and_malformed_name(self):
        os.link(self.file, self.base / "second")
        self.assertNotEqual(self.verify(), 0)
        (self.base / "second").unlink()
        self.root.chmod(0o700)
        link = self.root / "link"
        link.unlink()
        link.symlink_to("other")
        self.root.chmod(0o500)
        self.assertNotEqual(self.verify(), 0)
        self.root.chmod(0o700)
        link.unlink()
        link.symlink_to("code")
        (self.root / "extra\nrow").touch()
        self.root.chmod(0o500)
        self.assertNotEqual(self.verify(), 0)

    def test_missing_unexpected_and_duplicate(self):
        initial = self.objects.read_text()
        for bad in (initial + "Directory|500|./other|\n", initial.splitlines(True)[0], initial + initial, initial.rstrip(),
                    "".join(reversed(initial.splitlines(True)))):
            with self.subTest(catalog=bad):
                self.objects.write_text(bad)
                self.assertNotEqual(self.verify(), 0)
