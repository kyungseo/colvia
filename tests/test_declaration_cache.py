"""Declaration reuse must not reuse filesystem observations or failed parses."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from hv2ref import product, work
from hv2ref.errors import ContractError

ENTRY = b'WORKSPACE_INVENTORY_ID = "continuation-1"\n'
OLD = b'WORKSPACE_INVENTORY_ID = "checkout-1"\n'


class DeclarationCacheTests(unittest.TestCase):
    def setUp(self):
        product._cached_launcher_inventory_window.cache_clear()
        self.addCleanup(product._cached_launcher_inventory_window.cache_clear)

    def test_entry_declaration_remains_legacy_readable_only(self):
        value=b'WORKSPACE_INVENTORY_ID = "entry-1"\n'
        self.assertEqual('entry-1',product._launcher_inventory_window(value,allow_legacy=True))
        with self.assertRaises(ContractError):product._launcher_inventory_window(value,allow_legacy=False)

    def test_same_bytes_reuse_parse_but_modes_are_separate(self):
        with patch.object(product.ast, 'parse', wraps=product.ast.parse) as parse:
            for data, mode, expected in ((ENTRY, False, 'continuation-1'),
                                         (bytes(bytearray(ENTRY)), False, 'continuation-1'),
                                         (ENTRY, True, 'continuation-1'), (OLD, True, 'checkout-1')):
                self.assertEqual(expected, product._launcher_inventory_window(data, allow_legacy=mode))
            self.assertEqual(3, parse.call_count)
            with self.assertRaises(ContractError):
                product._launcher_inventory_window(OLD)
            self.assertEqual(4, parse.call_count)

    def test_changed_bytes_and_rebinding_cannot_hit(self):
        self.assertEqual('continuation-1', product._launcher_inventory_window(ENTRY, allow_legacy=True))
        self.assertEqual('checkout-1', product._launcher_inventory_window(OLD, allow_legacy=True))
        with self.assertRaises(ContractError):
            product._launcher_inventory_window(ENTRY + b'del WORKSPACE_INVENTORY_ID\n')

    def test_eviction_keeps_recent_inputs_and_bounds_retained_bytes(self):
        values = [ENTRY + ('# %s\n' % i).encode() for i in range(5)]
        with patch.object(product.ast, 'parse', wraps=product.ast.parse) as parse:
            for value in values[:4]: product._launcher_inventory_window(value)
            product._launcher_inventory_window(values[0])
            product._launcher_inventory_window(values[4])
            product._launcher_inventory_window(values[0])
            self.assertEqual(5, parse.call_count)
            product._launcher_inventory_window(values[1])
            self.assertEqual(6, parse.call_count)
        info = product._cached_launcher_inventory_window.cache_info()
        self.assertEqual(4, info.currsize)
        self.assertEqual(4, info.maxsize)
        large = ENTRY + b'#' + b'x' * (1024 * 1024 - len(ENTRY) - 2) + b'\n'
        self.assertEqual('continuation-1', product._launcher_inventory_window(large))
        with self.assertRaises(ContractError): product._launcher_inventory_window(large + b' ')
        self.assertEqual(4, product._cached_launcher_inventory_window.cache_info().currsize)

    def test_invalid_or_custom_arguments_keep_original_behavior(self):
        class UnhashableBytes(bytes):
            __hash__ = None
        class UnhashableMode:
            __hash__ = None
            def __bool__(self): return True
        with patch.object(product.ast, 'parse', wraps=product.ast.parse) as parse:
            for _ in range(2):
                self.assertEqual('continuation-1', product._launcher_inventory_window(UnhashableBytes(ENTRY)))
                self.assertEqual('checkout-1', product._launcher_inventory_window(OLD, allow_legacy=UnhashableMode()))
            self.assertEqual(4, parse.call_count)
        for value in (None, [], bytearray(ENTRY), memoryview(ENTRY), ENTRY.decode()):
            with self.subTest(value=type(value)), self.assertRaises(ContractError):
                product._launcher_inventory_window(value)
        self.assertEqual(0, product._cached_launcher_inventory_window.cache_info().currsize)

    def test_failed_parses_are_retried(self):
        for error in (SyntaxError, RecursionError, MemoryError, ValueError):
            with patch.object(product.ast, 'parse', side_effect=error) as parse:
                for _ in range(2):
                    with self.assertRaises(ContractError): product._launcher_inventory_window(ENTRY)
                self.assertEqual(2, parse.call_count)
        self.assertEqual(0, product._cached_launcher_inventory_window.cache_info().currsize)
        self.assertEqual('continuation-1', product._launcher_inventory_window(ENTRY))

    def test_current_file_read_and_race_refusal_survive_warm_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'launcher'
            path.write_bytes(ENTRY)
            self.assertEqual('continuation-1', product._launcher_inventory_window(product._serial_file(path), allow_legacy=True))
            path.write_bytes(OLD)
            self.assertEqual('checkout-1', product._launcher_inventory_window(product._serial_file(path), allow_legacy=True))
            path.write_bytes(ENTRY)
            native = work._stable_file
            calls = []
            def changing(p):
                value = native(p)
                calls.append(1)
                if len(calls) == 1: path.write_bytes(OLD)
                return value
            with patch.object(work, '_stable_file', changing), self.assertRaises(ContractError):
                product._launcher_inventory_window(product._serial_file(path), allow_legacy=True)
            self.assertEqual(OLD, path.read_bytes())

    def test_candidate_still_reads_and_rejects_links_and_unknown_members(self):
        import os
        import shutil
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source'
            for name in product.CONTINUATION_MANAGED_PATHS:
                dest = source / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(product.source_root() / name, dest)
            first = product.workspace_candidate(source)
            self.assertEqual('continuation-1', first['inventory']['inventory_id'])
            launcher = source / 'colvia'
            raw = launcher.read_bytes()
            launcher.write_bytes(raw.replace(b'WORKSPACE_INVENTORY_ID = "continuation-1"', b'WORKSPACE_INVENTORY_ID = "checkout-1"'))
            with self.assertRaises(ContractError): product.workspace_candidate(source)
            launcher.write_bytes(raw)
            for kind in ('hardlink', 'symlink'):
                backup = root / kind
                launcher.rename(backup)
                if kind == 'hardlink': os.link(backup, launcher)
                else: launcher.symlink_to(backup)
                with self.assertRaises(ContractError): product.workspace_candidate(source)
                launcher.unlink()
                backup.rename(launcher)
            release = root / first['release_ref']['id']
            (release / 'payload').mkdir(parents=True)
            (release / 'inventory.json').write_bytes(product.canonical_json_bytes(first['inventory']))
            for name, data in first['payload'].items():
                path = release / 'payload' / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            self.assertEqual(first['release_ref'], product.verify_workspace_release(release)['release_ref'])
            readme = release / 'payload/README.md'
            original = readme.read_bytes()
            readme.write_bytes(original + b'changed\n')
            with self.assertRaises(ContractError): product.verify_workspace_release(release)
            readme.write_bytes(original)
            unknown = release / 'unknown'
            unknown.write_bytes(b'preserve\n')
            with self.assertRaises(ContractError): product.verify_workspace_release(release)
            self.assertEqual(b'preserve\n', unknown.read_bytes())
