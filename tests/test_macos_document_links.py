"""macOS-only precise source documentation checks; no installer or model calls.

The portable checker and its target-policy assertions remain unchanged.  Windows
precise parsing is unavailable here, not qualified by these macOS observations.
"""
from contextlib import contextmanager
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from tests import test_productization_safety as safety

SOURCE = Path(__file__).resolve().parents[1]
PARSER = SOURCE / "runtime/official/marked.umd.js"
# Independently pinned bundled marked 17.0.5; update only with parser review.
PARSER_SHA256 = "0db7abc826b5ac76f6ed11951ae34074ba50438ce6ea8d52889203779e5cbbad"


@contextmanager
def precise_links():
    # Import only after the macOS test-class guard has admitted execution.
    from hv2ref import official_worker
    if Path(official_worker.__file__).resolve() != SOURCE / "src/hv2ref/official_worker.py":
        raise AssertionError("source parser adapter required")
    parser = official_worker.GFM(str(PARSER), PARSER_SHA256)
    try:
        def extract(text):
            if "\x00" in text:
                raise ValueError("NUL document input")
            document = official_worker.DocumentHTML()
            document.feed(parser.render(text))
            document.close()
            return document.links
        yield extract
    finally:
        parser.close()


def check_documents(case):
    """Use the real common target assertions, replacing only link extraction."""
    method = safety.ActualWorkspaceInitTests.test_document_port_local_links_resolve
    owner = sys.modules[method.__module__]
    with precise_links() as extract, mock.patch.object(
            owner, "markdown_links_outside_fences", wraps=extract) as renderer:
        method(case)
        return renderer.call_count


@unittest.skipUnless(sys.platform == "darwin", "macOS JavaScriptCore required; Windows precise check unverified")
class MacOSGFMDocumentLinkTests(unittest.TestCase):
    def fixture(self, text):
        holder = tempfile.TemporaryDirectory(prefix="macos-document-links-")
        self.addCleanup(holder.cleanup)
        base = Path(holder.name).resolve()
        self.source = base / "source"
        self.source.mkdir()
        (self.source / "docs").mkdir()
        for name in ("README.md", "AGENTS.md", "CLAUDE.md"):
            (self.source / name).write_text("")
        (self.source / "README.md").write_text(text)
        (self.source / "docs/ok.md").write_text("# Part\n")
        (base / "outside.md").write_text("outside")
        return base

    def test_source_documents_resolve_read_only(self):
        self.source = SOURCE
        docs = [SOURCE / name for name in ("README.md", "AGENTS.md", "CLAUDE.md")]
        docs += sorted((SOURCE / "docs").glob("*.md"))
        def snapshot():
            return {str(p): (hashlib.sha256(p.read_bytes()).hexdigest(),
                            p.stat().st_mode, p.stat().st_mtime_ns) for p in docs}
        before = snapshot()
        self.assertEqual(len(docs), check_documents(self))
        with precise_links() as extract:
            self.assertGreater(sum(len(extract(p.read_text())) for p in docs), 0)
        self.assertEqual(before, snapshot())

    def test_gfm_detects_known_misses_and_link_forms(self):
        cases = [
            ("`[example](missing.md)` [r](y.md)", ["y.md"]),
            ("- `a\n    - [r](y.md) `c", ["y.md"]),
            ('<a title="`"> [r](y.md) <b title="`">', ["y.md"]),
            ("> `a\n> b` [r](y.md) `c", ["y.md"]),
            ("`a\n\u2028\nb` [r](y.md) `c", ["y.md"]),
            ("[r][dest]\n\n[dest]: y.md", ["y.md"]),
            ("![r](y.png)", ["y.png"]),
            ('<a href="y.md">r</a>', ["y.md"]),
            ("<https://example.invalid/>", ["https://example.invalid/"]),
        ]
        with precise_links() as extract:
            for text, expected in cases:
                with self.subTest(text=text):
                    self.assertEqual(expected, extract(text))

    def test_valid_links_and_code_examples(self):
        self.fixture("`[example](missing.md)` [valid](docs/ok.md#part) [here](#part) <https://example.invalid/>\n\n[r][ok]\n\n[ok]: docs/ok.md\n")
        self.assertEqual(4, check_documents(self))

    def test_parser_discovered_missing_and_outside_targets_fail(self):
        cases = [
            ("[r][missing]\n\n[missing]: missing.md", "missing.md"),
            ("- `a\n    - [r](missing.md) `c", "missing.md"),
            ('<a href="../outside.md">r</a>', "outside repository"),
            ("![r](../outside.md)", "outside repository"),
        ]
        for text, message in cases:
            with self.subTest(text=text):
                self.fixture(text)
                with self.assertRaisesRegex(AssertionError, message):
                    check_documents(self)

    def test_wrong_parser_hash_is_an_error(self):
        from hv2ref.official_worker import WorkerRefusal
        with mock.patch.object(sys.modules[__name__], "PARSER_SHA256", "0" * 64):
            with self.assertRaisesRegex(WorkerRefusal, "parser-drift"):
                with precise_links():
                    self.fail("wrong parser accepted")

    def test_missing_parser_and_engine_failure_do_not_fallback(self):
        from hv2ref import official_worker
        base = self.fixture("[valid](docs/ok.md)")
        owner = sys.modules[safety.ActualWorkspaceInitTests.test_document_port_local_links_resolve.__module__]
        with mock.patch.object(owner, "markdown_links_outside_fences") as fallback:
            with mock.patch.object(sys.modules[__name__], "PARSER", base / "missing.js"):
                with self.assertRaises(FileNotFoundError):
                    check_documents(self)
            with mock.patch.object(official_worker, "GFM", side_effect=OSError("engine unavailable")):
                with self.assertRaisesRegex(OSError, "engine unavailable"):
                    check_documents(self)
            fallback.assert_not_called()

    def test_render_failure_closes_context_and_propagates(self):
        from hv2ref import official_worker
        self.fixture("[valid](docs/ok.md)")
        engine = mock.Mock()
        engine.render.side_effect = official_worker.WorkerRefusal("render failure")
        with mock.patch.object(official_worker, "GFM", return_value=engine):
            with self.assertRaisesRegex(official_worker.WorkerRefusal, "render failure"):
                check_documents(self)
        engine.close.assert_called_once_with()

    def test_nul_input_fails_before_render_and_closes(self):
        from hv2ref import official_worker
        self.fixture("prefix\x00[r](missing.md)")
        engine = mock.Mock()
        with mock.patch.object(official_worker, "GFM", return_value=engine):
            with self.assertRaisesRegex(ValueError, "NUL document input"):
                check_documents(self)
        engine.render.assert_not_called()
        engine.close.assert_called_once_with()

    def test_existing_target_policy_rejects_encoded_path_and_bare_email(self):
        # Keep the shared target policy; do not add URL decoding or URI waivers.
        for text in ("[r](<docs/한 글.md>)", "person@example.invalid"):
            with self.subTest(text=text):
                self.fixture(text)
                (self.source / "docs/한 글.md").write_text("exists")
                with self.assertRaises(AssertionError):
                    check_documents(self)
