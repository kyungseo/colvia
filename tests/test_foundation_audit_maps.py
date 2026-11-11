"""Whole-history audits share validation without trusting saved cache or changing limits."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from colvia.codec import ObjectRef, RecordError, object_ref, decode_envelope, encode_envelope, Edge
from colvia.maps import build_map, map_update, verify_map
from colvia.graph import GraphAudit, AuditBudget, _AuditLoader


class AuditMapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='audit-map-')
        self.audit = GraphAudit(Path(self.tmp.name)/'audit.sqlite3', AuditBudget(10000,10000,10000000))
        self.storage = {}; self.calls = []
        self.loader = _AuditLoader(self.audit.db, self.read, lambda: False)

    def tearDown(self):
        self.audit.close(); self.tmp.cleanup()

    def read(self, ref):
        self.calls.append(ref)
        return self.storage[ref]

    def tree(self, count=300):
        value = object_ref('body.chunk', 1, b'value')
        tree = build_map((f'key-{i}', value) for i in range(count))
        self.storage.update(tree.objects)
        return tree, value

    def test_shared_subtrees_validated_once_and_updated_root_still_checked(self):
        tree, value = self.tree()
        verify_map(tree.root, self.loader)
        self.assertEqual(len(tree.objects), len(self.calls))
        updated = map_update(tree.root, {'extra': value}, self.storage.__getitem__)
        self.storage.update(updated.objects)
        self.calls.clear(); verify_map(updated.root, self.loader)
        self.assertLess(len(self.calls), len(tree.objects)//2)
        self.assertIn(updated.root, self.calls)

    def test_cached_subtree_keeps_full_reference_prefix_and_resource_limits(self):
        tree, _ = self.tree(); verify_map(tree.root, self.loader)
        altered = ObjectRef(tree.root.kind,tree.root.version,tree.root.byte_length+1,tree.root.sha256)
        self.assertIsNone(self.loader.get(altered, ()))
        self.assertIsNone(self.loader.get(tree.root, (1,)))
        with patch('colvia.maps.MAP_BYTES_LIMIT', 1), self.assertRaisesRegex(RecordError,'map-read-limit'):
            verify_map(tree.root, self.loader)
        with patch('colvia.maps.MAP_LIMIT', 1), self.assertRaisesRegex(RecordError,'map-read-limit'):
            verify_map(tree.root, self.loader)

    def test_cached_child_cannot_hide_wrong_bucket_or_parent_count(self):
        tree, _ = self.tree(); verify_map(tree.root, self.loader)
        obj=decode_envelope(tree.root,self.storage[tree.root])
        payload=dict(obj.payload); payload['count']+=1
        bad, raw=encode_envelope(tree.root.kind,1,payload,obj.edges); self.storage[bad]=raw
        with self.assertRaisesRegex(RecordError,'map-count-mismatch'): verify_map(bad,self.loader)
        edges=list(obj.edges); edges[0]=Edge('integrity',edges[-1].ref)
        bad, raw=encode_envelope(tree.root.kind,1,obj.payload,tuple(edges)); self.storage[bad]=raw
        with self.assertRaisesRegex(RecordError,'wrong-map-bucket'): verify_map(bad,self.loader)

    def test_cancelled_cached_read_refuses(self):
        tree, _ = self.tree(); verify_map(tree.root,self.loader)
        self.loader.cancelled=lambda:True
        with self.assertRaisesRegex(RecordError,'audit-cancelled'):verify_map(tree.root,self.loader)


if __name__=='__main__':unittest.main()
