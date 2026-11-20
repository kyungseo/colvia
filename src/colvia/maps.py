"""Persistent canonical maps for roots and heads, independent of SQL indexes."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import unicodedata
from typing import Callable, Iterable

from .codec import (Edge, ObjectRef, decode_envelope, encode_envelope,
                    require, validate_schema)
from .tree import PATH_RULE, UNICODE_VERSION

MAP_LIMIT = 1_000_000
MAP_BYTES_LIMIT = 512 * 1024 * 1024
LEAF_LIMIT = 16
DEPTH_LIMIT = 16


def _key(key):
    require(unicodedata.unidata_version == UNICODE_VERSION, 'key-rules-unavailable')
    require(type(key) is str and key and
            not any(unicodedata.category(c) in ('Cc', 'Cs') for c in key) and
            unicodedata.normalize('NFC', key) == key and len(key.encode('utf-8')) <= 1024,
            'invalid-map-key')


def _hash(key):
    raw=hashlib.sha256(key.encode('utf-8')).digest()
    return tuple(n for byte in raw for n in (byte >> 4, byte & 15))


@dataclass(frozen=True, slots=True)
class MapObjects:
    root: ObjectRef
    objects: tuple[tuple[ObjectRef, bytes], ...]


def build_map(items: Iterable[tuple[str, ObjectRef]]) -> MapObjects:
    values = {}
    for key, ref in items:
        _key(key)
        require(key not in values and type(ref) is ObjectRef, 'invalid-map-item')
        values[key] = ref
        require(len(values) <= MAP_LIMIT, 'map-entry-limit')
    objects = {}

    def node(group, depth):
        keys = sorted(group, key=lambda k: k.encode('utf-8'))
        if len(keys) <= LEAF_LIMIT:
            edges = tuple(Edge('decision', group[k]) for k in keys)
            ref, raw = encode_envelope('map.leaf', 1,
                dict(key_rule=PATH_RULE, count=len(keys), keys=keys, links={'values': list(range(len(keys)))}), edges)
        else:
            require(depth < DEPTH_LIMIT, 'map-prefix-overflow')
            buckets = {}
            for key in keys: buckets.setdefault(_hash(key)[depth], {})[key] = group[key]
            keys = sorted(buckets)
            edges = tuple(Edge('integrity', node(buckets[k], depth+1)) for k in keys)
            ref, raw = encode_envelope('map.branch', 1,
                dict(key_rule=PATH_RULE, count=len(group), buckets=keys, links={'children': list(range(len(keys)))}), edges)
        objects[ref] = raw
        return ref
    root = node(values, 0)
    return MapObjects(root, tuple(sorted(objects.items(), key=lambda p:p[0].sha256)))


def _node(ref, raw, prefix):
    require(ref.kind in ('map.leaf', 'map.branch') and ref.version == 1, 'unknown-required-map-kind')
    obj = decode_envelope(ref, raw)
    leaf = ref.kind == 'map.leaf'
    field, values = ('values', 'keys') if leaf else ('children', 'buckets')
    def check(p):
        require(set(p) == {'key_rule', 'links', 'count', values} and p['key_rule'] == PATH_RULE and
                type(p['count']) is int and 0 <= p['count'] <= MAP_LIMIT,
                'invalid-map-payload')
    validate_schema(obj, kind=ref.kind, version=1,
                    fields={field: 'decision' if leaf else 'integrity'}, validate_payload=check)
    keys = obj.payload[values]
    require(type(keys) is list and obj.payload['links'][field] == list(range(len(keys))),
            'invalid-map-links')
    if leaf:
        require(len(keys) <= LEAF_LIMIT and obj.payload['count']==len(keys), 'map-leaf-limit')
        for key in keys:
            _key(key)
            require(tuple(_hash(key)[:len(prefix)]) == prefix, 'wrong-map-bucket')
        require(keys == sorted(set(keys), key=lambda k:k.encode('utf-8')), 'unordered-map-keys')
    else:
        require(len(prefix) < DEPTH_LIMIT and obj.payload['count']>LEAF_LIMIT and 0 < len(keys) <= 16 and
                all(type(k) is int and 0 <= k <= 15 for k in keys) and
                keys == sorted(set(keys)), 'invalid-map-branch')
    return leaf, list(zip(keys, (e.ref for e in obj.edges)))


def map_get(root: ObjectRef, key: str, load: Callable[[ObjectRef], bytes]) -> ObjectRef | None:
    """Verify only the selected map path. Full audit is a separate operation."""
    _key(key)
    prefix = ()
    digest = _hash(key)
    ref = root
    while True:
        leaf, items = _node(ref, load(ref), prefix)
        if leaf:
            return dict(items).get(key)
        bucket = digest[len(prefix)]
        child = dict(items).get(bucket)
        if child is None: return None
        prefix = (*prefix, bucket)
        ref = child


def read_map(root: ObjectRef, load: Callable[[ObjectRef], bytes], *, entry_limit=MAP_LIMIT) -> dict[str, ObjectRef]:
    require(type(entry_limit) is int and 0<entry_limit<=MAP_LIMIT,'invalid-map-entry-limit')
    result = {}
    stack = [(root, ())]
    size, count = 0, 0
    while stack:
        ref, prefix = stack.pop()
        raw = load(ref)
        size += len(raw); count += 1
        require(size <= MAP_BYTES_LIMIT and count <= MAP_LIMIT, 'map-read-limit')
        leaf, items = _node(ref, raw, prefix)
        if leaf:
            for key, value in items:
                require(key not in result, 'duplicate-map-key')
                require(len(result)<entry_limit,'map-entry-limit')
                result[key] = value
            require(len(result) <= MAP_LIMIT, 'map-entry-limit')
        else:
            stack.extend((child, (*prefix, bucket)) for bucket, child in items)
    require(build_map(result.items()).root == root, 'noncanonical-map-shape')
    return result


def map_update(root: ObjectRef, updates: dict[str, ObjectRef | None],
               load: Callable[[ObjectRef], bytes]) -> MapObjects:
    """Path-copy updates with deterministic branch collapse and unchanged reuse."""
    for key, ref in updates.items():
        _key(key)
        require(ref is None or type(ref) is ObjectRef, 'invalid-map-item')
    staged = {}
    def read(ref): return staged[ref] if ref in staged else load(ref)
    def write(kind, payload, edges):
        ref, raw = encode_envelope(kind, 1, payload, edges)
        staged[ref] = raw
        return ref
    def leaf(values):
        keys = sorted(values, key=lambda k:k.encode('utf-8'))
        return write('map.leaf', dict(key_rule=PATH_RULE, count=len(keys), keys=keys,
                     links={'values':list(range(len(keys)))}),
                     tuple(Edge('decision', values[k]) for k in keys))
    def build(values, prefix):
        if len(values) <= LEAF_LIMIT: return leaf(values)
        require(len(prefix) < DEPTH_LIMIT, 'map-prefix-overflow')
        groups = {}
        for key, value in values.items(): groups.setdefault(_hash(key)[len(prefix)], {})[key] = value
        children = {k:build(group, (*prefix, k)) for k, group in groups.items()}
        return branch(children,prefix)
    def branch(children,prefix):
        keys = sorted(children)
        total=0
        for key in keys:
            raw=read(children[key])
            _node(children[key],raw,(*prefix,key))
            total+=decode_envelope(children[key],raw).payload['count']
        require(total<=MAP_LIMIT,'map-entry-limit')
        return write('map.branch', dict(key_rule=PATH_RULE, count=total, buckets=keys,
                     links={'children':list(range(len(keys)))}),
                     tuple(Edge('integrity', children[k]) for k in keys))
    def collapse(children, prefix):
        values = {}
        pending = [(child, (*prefix, key)) for key, child in children.items()]
        while pending:
            ref, path = pending.pop()
            is_leaf, items = _node(ref, read(ref), path)
            if is_leaf:
                values.update(items)
                if len(values) > LEAF_LIMIT: return None
            else:
                pending.extend((child, (*path, key)) for key, child in items)
        return values
    def update(ref, changes, prefix):
        is_leaf, items = _node(ref, read(ref), prefix)
        if is_leaf:
            values = dict(items)
            for key, value in changes.items():
                if value is None: values.pop(key, None)
                else: values[key] = value
            return build(values, prefix)
        children = dict(items)
        groups = {}
        for key, value in changes.items(): groups.setdefault(_hash(key)[len(prefix)], {})[key] = value
        for bucket, group in groups.items():
            path = (*prefix, bucket)
            if bucket in children:
                child = update(children[bucket], group, path)
            else:
                child = build({k:v for k,v in group.items() if v is not None}, path)
            child_leaf, child_items = _node(child, read(child), path)
            if child_leaf and not child_items: children.pop(bucket, None)
            else: children[bucket] = child
        values = collapse(children, prefix)
        return leaf(values) if values is not None else branch(children,prefix)
    result = update(root, updates, ())
    reachable={};pending=[result]
    while pending:
        ref=pending.pop()
        if ref not in staged or ref in reachable:continue
        raw=staged[ref];reachable[ref]=raw
        pending.extend(e.ref for e in decode_envelope(ref,raw).edges if e.ref.kind in ('map.leaf','map.branch'))
    return MapObjects(result, tuple(sorted(reachable.items(), key=lambda p:p[0].sha256)))


def verify_map(root: ObjectRef, load: Callable[[ObjectRef], bytes]) -> None:
    """Validate complete canonical shape with bounded buffers, without a key dict."""
    memo = getattr(load, 'map_summaries', None)
    if memo is not None:
        def checked(ref, prefix):
            cached = memo.get(ref, prefix)
            if cached is not None:
                count, size, refs = cached
            else:
                raw = load(ref)
                leaf, items = _node(ref, raw, prefix)
                count = decode_envelope(ref, raw).payload['count']
                size, refs = len(raw), 1
                require(not prefix or count > 0, 'empty-map-child')
                if not leaf:
                    subtotal = 0
                    for bucket, child in items:
                        entries, child_size, child_refs = checked(child, (*prefix, bucket))
                        subtotal += entries; size += child_size; refs += child_refs
                        require(size <= MAP_BYTES_LIMIT and refs <= MAP_LIMIT, 'map-read-limit')
                    require(subtotal == count, 'map-count-mismatch')
                require(size <= MAP_BYTES_LIMIT and refs <= MAP_LIMIT, 'map-read-limit')
                memo.put(ref, prefix, (count, size, refs))
            require(size <= MAP_BYTES_LIMIT and refs <= MAP_LIMIT, 'map-read-limit')
            return count, size, refs
        checked(root, ())
        return
    pending = [(root, ())]
    total_bytes = refs = 0
    while pending:
        ref, prefix = pending.pop()
        raw = load(ref); total_bytes += len(raw); refs += 1
        require(total_bytes <= MAP_BYTES_LIMIT and refs <= MAP_LIMIT, 'map-read-limit')
        leaf, items = _node(ref, raw, prefix)
        count = decode_envelope(ref, raw).payload['count']
        require(not prefix or count > 0, 'empty-map-child')
        if not leaf:
            subtotal = 0
            for bucket, child in items:
                child_raw = load(child)
                _node(child, child_raw, (*prefix, bucket))
                subtotal += decode_envelope(child, child_raw).payload['count']
                pending.append((child, (*prefix, bucket)))
            require(subtotal == count, 'map-count-mismatch')


def scan_map(root: ObjectRef, load: Callable[[ObjectRef], bytes], *, after: str | None = None):
    """Deterministic bounded traversal for paged lists; never load value graphs."""
    if after is not None:
        _key(after)
    route = _hash(after) if after is not None else ()
    pending=[(root,())];size=count=0
    while pending:
        ref,prefix=pending.pop()
        if after is not None and prefix < route[:len(prefix)]:
            continue
        raw=load(ref);size+=len(raw);count+=1
        require(size<=MAP_BYTES_LIMIT and count<=MAP_LIMIT,'map-read-limit')
        leaf,items=_node(ref,raw,prefix)
        if leaf:
            if after is not None and prefix == route[:len(prefix)]:
                yield from ((key, value) for key, value in items if key > after)
            else:
                yield from items
        else:
            pending.extend((child,(*prefix,key)) for key,child in reversed(items))
