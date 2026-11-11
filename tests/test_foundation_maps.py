import random
import unittest
from colvia.codec import Edge, RecordError, decode_envelope, encode_envelope, object_ref
from colvia.maps import build_map, map_get, map_update, read_map


class PersistentMapTests(unittest.TestCase):
    def test_update_order_split_collapse_and_rebuild(self):
        values = {f'work-{i}': object_ref('body.chunk', 1, str(i).encode()) for i in range(900)}
        tree = build_map(values.items()); storage = dict(tree.objects)
        keys = list(values); random.Random(74).shuffle(keys)
        incremental = build_map([]); storage.update(incremental.objects)
        for offset in range(0,len(keys),47):
            changes = {k:values[k] for k in keys[offset:offset+47]}
            incremental = map_update(incremental.root, changes, storage.__getitem__)
            storage.update(incremental.objects)
        self.assertEqual(tree.root, incremental.root)
        self.assertEqual(values, read_map(tree.root, storage.__getitem__))
        for key in ('work-0','work-899','absent'):
            self.assertEqual(values.get(key), map_get(tree.root, key, storage.__getitem__))
        shrunk = map_update(tree.root, {k:None for k in keys[12:]}, storage.__getitem__)
        storage.update(shrunk.objects)
        self.assertEqual('map.leaf', shrunk.root.kind)
        self.assertEqual(build_map((k,values[k]) for k in keys[:12]).root, shrunk.root)

    def test_selected_lookup_does_not_scan_other_heads(self):
        values = {f'work-{i}':object_ref('body.chunk', 1, str(i).encode()) for i in range(3000)}
        tree = build_map(values.items()); storage = dict(tree.objects); calls=[]
        def read(ref): calls.append(ref); return storage[ref]
        self.assertEqual(values['work-72'], map_get(tree.root, 'work-72', read))
        self.assertLessEqual(len(calls),9)
        self.assertLess(len(calls),len(storage))

    def test_roles_and_duplicate_keys_refuse(self):
        value = object_ref('body.chunk',1,b'x')
        with self.assertRaises(RecordError): build_map([('x',value),('x',value)])
        for key in ('','x\x00','\ud800','한'):
            with self.assertRaises(RecordError): build_map([(key,value)])
        tree = build_map([('x',value)]); obj=decode_envelope(tree.root,dict(tree.objects)[tree.root])
        ref,raw=encode_envelope('map.leaf',1,obj.payload,(Edge('display',value),))
        with self.assertRaisesRegex(RecordError,'edge-role-mismatch'): map_get(ref,'x',lambda _:raw)

    def test_noop_preserves_root_and_semantics_ignore_storage_order(self):
        values = [('b',object_ref('body.chunk',1,b'b')),('a',object_ref('body.chunk',1,b'a'))]
        tree = build_map(values); storage = dict(reversed(tree.objects))
        self.assertEqual(tree.root, map_update(tree.root, {'missing':None}, storage.__getitem__).root)
        self.assertEqual(tree.root,build_map(reversed(values)).root)


if __name__ == '__main__': unittest.main()
