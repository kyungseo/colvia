"""C2 identity properties and adversarial tree readers; synthetic bytes only."""
import base64
import hashlib
import random
import unittest
from unittest.mock import patch

from colvia.codec import Edge, RecordError, decode_envelope, encode_envelope
from colvia.tree import (PATH_RULE, _build, build_tree, canonical_entries, logical_path,
                         read_tree, replace_entries)


def regular(path, raw=b'body', mode='100644'):
    return dict(path=path, kind='regular', mode=mode, size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def loader(tree):
    return dict(tree.objects).__getitem__


class PathTests(unittest.TestCase):
    def test_normalizes_without_materializing(self):
        self.assertEqual('한글/보고서.md', logical_path('한글/보고서.md'))
        self.assertEqual('x'*255, logical_path('x'*255))
        for path in ('', '/', '/a', 'C:/a', 'C:a', '..', 'a/../b', 'a//b', './a',
                     'a\\b', 'a\x00b', 'a\nb', '\ud800', 'x'*256, 'a/'):
            with self.subTest(path=repr(path)), self.assertRaises(RecordError): logical_path(path)

    def test_normalization_and_case_collisions_refuse(self):
        for entries in ([regular('A'), regular('a')], [regular('x'), regular('x')],
                        [regular('한글'), regular('한글')],
                        [regular('Dir'), regular('dir/x')]):
            with self.assertRaises(RecordError): build_tree(entries)
        with patch('colvia.tree.unicodedata.unidata_version', 'future'):
            with self.assertRaisesRegex(RecordError, 'path-rules-unavailable'): logical_path('x')

    def test_exact_union_and_opaque_identity(self):
        entries = [regular('report.md', b'\xef\xbb\xbfhi\r\n'),
                   dict(path='link', kind='symlink', mode='120000', target=base64.b64encode(b'../outside').decode()),
                   dict(path='vendor', kind='gitlink', mode='160000', algorithm='sha256', oid='a'*64)]
        tree = build_tree(entries)
        self.assertEqual(canonical_entries(entries), read_tree(tree.root, loader(tree)))
        for change in (dict(entries[0], size=True), dict(entries[0], extra=1),
                       dict(entries[1], mode='100644'), dict(entries[2], algorithm='unknown')):
            with self.assertRaises(RecordError): build_tree([change])


class TreeProperties(unittest.TestCase):
    def test_order_and_incremental_rebuild_are_identical(self):
        entries = [regular(f'folder/f-{i:04}.md', str(i).encode()) for i in range(513)]
        tree = build_tree(entries)
        shuffled = entries[:]; random.Random(273).shuffle(shuffled)
        self.assertEqual(tree, build_tree(shuffled))
        self.assertEqual(canonical_entries(entries), read_tree(tree.root, loader(tree)))
        removed = [e['path'] for e in entries[100:]]
        shrunk = replace_entries(tree.root, loader(tree), [], removed)
        self.assertEqual('tree.leaf', shrunk.root.kind)
        self.assertEqual(build_tree(entries[:100]), shrunk)
        restored = replace_entries(shrunk.root, loader(shrunk), entries[100:])
        self.assertEqual(tree, restored)
        edited = replace_entries(tree.root, loader(tree), [regular(entries[0]['path'], b'new')])
        self.assertEqual(build_tree([regular(entries[0]['path'], b'new'), *entries[1:]]), edited)

    def test_empty_and_exact_split_boundary(self):
        for count, kind in ((0, 'tree.leaf'), (128, 'tree.leaf'), (129, 'tree.branch')):
            tree = build_tree(regular(f'f{i}') for i in range(count))
            self.assertEqual(kind, tree.root.kind)
            self.assertEqual(count, len(read_tree(tree.root, loader(tree))))

    def test_hash_prefix_overflow_is_explicit(self):
        entries = canonical_entries(regular(f'f{i}') for i in range(129))
        with self.assertRaisesRegex(RecordError, 'tree-prefix-overflow'):
            _build(entries, lambda _: b'\x00'*32)

    def test_unnecessary_branch_and_wrong_bucket_refused(self):
        leaf = build_tree([regular('a')])
        for key in (hashlib.sha256(b'a').digest()[0], (hashlib.sha256(b'a').digest()[0]+1)%256):
            ref, raw = encode_envelope('tree.branch', 1,
                dict(path_rule=PATH_RULE, links={'children':[0]}, buckets=[key]),
                (Edge('integrity', leaf.root),))
            objects = dict(leaf.objects); objects[ref] = raw
            with self.assertRaises(RecordError): read_tree(ref, objects.__getitem__)

    def test_reader_checks_leaf_order_and_roles(self):
        leaf = build_tree([regular('a'), regular('b')])
        obj = decode_envelope(leaf.root, loader(leaf)(leaf.root))
        obj.payload['entries'].reverse()
        ref, raw = encode_envelope('tree.leaf', 1, obj.payload)
        with self.assertRaisesRegex(RecordError, 'unordered-leaf'):
            read_tree(ref, lambda _: raw)
        tree = build_tree(regular(f'f{i}') for i in range(129))
        obj = decode_envelope(tree.root, loader(tree)(tree.root))
        ref, raw = encode_envelope('tree.branch', 1, obj.payload,
                                  tuple(Edge('display', e.ref) for e in obj.edges))
        with self.assertRaisesRegex(RecordError, 'edge-role-mismatch'):
            read_tree(ref, lambda _: raw)

    def test_resource_limits_do_not_return_partial_trees(self):
        with patch('colvia.tree.ENTRY_LIMIT', 2):
            with self.assertRaisesRegex(RecordError, 'tree-entry-limit'):
                build_tree(regular(f'f{i}') for i in range(3))
        with patch('colvia.tree.TREE_BYTES_LIMIT', 1):
            with self.assertRaisesRegex(RecordError, 'tree-metadata-limit'):
                build_tree([regular('a')])


if __name__ == '__main__': unittest.main()
