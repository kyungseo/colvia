"""Canonical, platform-independent content trees; no filesystem traversal.

Native spelling/identity and materialization permissions belong to observation
adapters. This module never follows or writes a symlink or a submodule.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
import hashlib
import re
import unicodedata
from typing import Callable, Iterable

from .codec import (Edge, ObjectRef, RecordError, canonical_bytes, decode_envelope,
                    encode_envelope, require, validate_schema)

PATH_RULE = 'utf8-nfc-16.0.0-v1'
UNICODE_VERSION = '16.0.0'
ENTRY_LIMIT = 1_000_000
TREE_BYTES_LIMIT = 512 * 1024 * 1024
LEAF_ENTRIES = 128
TRIE_DEPTH = 8
_HEX = re.compile(r'[0-9a-f]+\Z', re.ASCII)


def logical_path(native: str) -> str:
    require(unicodedata.unidata_version == UNICODE_VERSION, 'path-rules-unavailable')
    require(type(native) is str, 'invalid-path')
    path = unicodedata.normalize('NFC', native)
    require(path and not path.startswith('/') and '\\' not in path and
            not re.match(r'^[A-Za-z]:', path), 'invalid-path')
    require(not any(unicodedata.category(c) in ('Cc', 'Cs') for c in path), 'invalid-path')
    parts = path.split('/')
    require(all(p not in ('', '.', '..') and len(p.encode('utf-8')) <= 255
                for p in parts) and len(path.encode('utf-8')) <= 4096, 'path-size-or-component')
    return path


def _digest(value: object, length=64) -> None:
    require(type(value) is str and len(value) == length and _HEX.fullmatch(value) is not None,
            'invalid-content-digest')


def validate_entry(value: object) -> None:
    require(type(value) is dict and type(value.get('path')) is str, 'invalid-entry')
    require(logical_path(value['path']) == value['path'], 'noncanonical-path')
    kind = value.get('kind')
    if kind == 'regular':
        require(set(value) == {'path', 'kind', 'mode', 'size', 'sha256'} and
                type(value['mode']) is str and value['mode'] in ('100644', '100755') and
                type(value['size']) is int and 0 <= value['size'] <= 0x7FFFFFFFFFFFFFFF,
                'invalid-regular-entry')
        _digest(value['sha256'])
    elif kind == 'symlink':
        require(set(value) == {'path', 'kind', 'mode', 'target'} and value['mode'] == '120000' and
                type(value['target']) is str, 'invalid-link-entry')
        try:
            target = base64.b64decode(value['target'], validate=True)
        except (ValueError, UnicodeError):
            raise RecordError('invalid-link-target') from None
        require(target and b'\x00' not in target and
                base64.b64encode(target).decode('ascii') == value['target'], 'invalid-link-target')
    elif kind == 'gitlink':
        require(set(value) == {'path', 'kind', 'mode', 'algorithm', 'oid'} and
                value['mode'] == '160000' and value['algorithm'] in ('sha1', 'sha256'),
                'invalid-gitlink-entry')
        _digest(value['oid'], 40 if value['algorithm'] == 'sha1' else 64)
    else:
        raise RecordError('unknown-entry-kind')


def canonical_entries(entries: Iterable[dict]) -> list[dict]:
    result, seen, aliases = [], set(), set()
    size = 0
    for entry in entries:
        require(len(result) < ENTRY_LIMIT, 'tree-entry-limit')
        validate_entry(entry)
        path = entry['path']
        alias = path.casefold()
        require(path not in seen and alias not in aliases, 'path-collision')
        seen.add(path); aliases.add(alias)
        raw = canonical_bytes(entry)
        size += len(raw)
        require(size <= TREE_BYTES_LIMIT, 'tree-metadata-limit')
        # Detach from caller-owned mutable dictionaries before hashing.
        result.append(dict(entry))
    for path in seen:
        parts = path.split('/')
        require(not any('/'.join(parts[:i]).casefold() in aliases for i in range(1, len(parts))),
                'path-ancestor-conflict')
    return sorted(result, key=lambda e: e['path'].encode('utf-8'))


@dataclass(frozen=True, slots=True)
class TreeObjects:
    root: ObjectRef
    objects: tuple[tuple[ObjectRef, bytes], ...]


def _path_hash(path: str) -> bytes:
    return hashlib.sha256(path.encode('utf-8')).digest()


def _build(entries: list[dict], path_hash: Callable[[str], bytes]) -> TreeObjects:
    objects = {}

    def emit(kind, payload, edges=()):
        ref, raw = encode_envelope(kind, 1, payload, edges)
        objects[ref] = raw
        return ref

    def node(group, depth):
        if len(group) <= LEAF_ENTRIES:
            try:
                return emit('tree.leaf', dict(path_rule=PATH_RULE, links={}, entries=group))
            except RecordError as exc:
                if exc.code != 'metadata-size-limit':
                    raise
        require(depth < TRIE_DEPTH, 'tree-prefix-overflow')
        buckets = {}
        for entry in group:
            digest = path_hash(entry['path'])
            require(type(digest) is bytes and len(digest) == 32, 'invalid-path-hash')
            buckets.setdefault(digest[depth], []).append(entry)
        keys = sorted(buckets)
        edges = tuple(Edge('integrity', node(buckets[key], depth + 1)) for key in keys)
        return emit('tree.branch', dict(path_rule=PATH_RULE, links={'children': list(range(len(keys)))},
                                       buckets=keys), edges)

    root = node(entries, 0)
    return TreeObjects(root, tuple(sorted(objects.items(), key=lambda pair: pair[0].sha256)))


def build_tree(entries: Iterable[dict]) -> TreeObjects:
    return _build(canonical_entries(entries), _path_hash)


def read_tree(root: ObjectRef, load: Callable[[ObjectRef], bytes]) -> list[dict]:
    """Verify shape, ordering and complete entries, not just the root digest."""
    entries = []
    stack = [(root, ())]
    refs = 0
    metadata_bytes = 0
    while stack:
        ref, prefix = stack.pop()
        refs += 1
        require(refs <= ENTRY_LIMIT and len(prefix) <= TRIE_DEPTH, 'tree-reference-limit')
        require(ref.kind in ('tree.leaf', 'tree.branch') and ref.version == 1,
                'unknown-required-tree-kind')
        raw = load(ref)
        metadata_bytes += len(raw)
        require(metadata_bytes <= TREE_BYTES_LIMIT, 'tree-metadata-limit')
        obj = decode_envelope(ref, raw)
        payload = obj.payload
        leaf = ref.kind == 'tree.leaf'

        def check(p):
            require(set(p) == {'path_rule', 'links', 'entries' if leaf else 'buckets'} and
                    p['path_rule'] == PATH_RULE, 'invalid-tree-payload')
        validate_schema(obj, kind=ref.kind, version=1,
                        fields={} if leaf else {'children': 'integrity'}, validate_payload=check)
        if leaf:
            group = payload['entries']
            require(type(group) is list and len(group) <= LEAF_ENTRIES, 'invalid-leaf')
            verified = canonical_entries(group)
            require(group == verified, 'unordered-leaf')
            for entry in group:
                require(tuple(_path_hash(entry['path'])[:len(prefix)]) == prefix, 'wrong-tree-bucket')
            entries.extend(group)
            require(len(entries) <= ENTRY_LIMIT, 'tree-entry-limit')
        else:
            keys = payload['buckets']
            require(type(keys) is list and 0 < len(keys) <= 256 and
                    all(type(k) is int and 0 <= k <= 255 for k in keys) and
                    keys == sorted(set(keys)) and
                    payload['links']['children'] == list(range(len(keys))), 'invalid-branch')
            require(len(prefix) < TRIE_DEPTH, 'tree-prefix-overflow')
            stack.extend((edge.ref, (*prefix, key)) for key, edge in zip(keys, obj.edges))
    entries = canonical_entries(entries)
    require(build_tree(entries).root == root, 'noncanonical-tree-shape')
    return entries


def replace_entries(root: ObjectRef, load: Callable[[ObjectRef], bytes],
                    replacements: Iterable[dict], deletions: Iterable[str] = ()) -> TreeObjects:
    """Reference implementation; persistent object deduplication happens in storage."""
    current = {entry['path']: entry for entry in read_tree(root, load)}
    remove = list(deletions)
    require(len(remove) == len(set(remove)), 'duplicate-deletion')
    for path in remove:
        require(logical_path(path) == path and path in current, 'unknown-deletion')
        del current[path]
    changes = canonical_entries(replacements)
    require(not set(remove).intersection(e['path'] for e in changes), 'conflicting-edit')
    current.update((entry['path'], entry) for entry in changes)
    return build_tree(current.values())


def entry_at(root: ObjectRef, path: str, load: Callable[[ObjectRef], bytes]):
    """Verify the selected immutable path, not an unrelated historical tree.

    Whole-tree canonicality is checked at publication/import. A selected query
    verifies every traversed digest, role, bucket and local entry; it is not a
    substitute for the whole-tree admission check.
    """
    require(logical_path(path)==path,'noncanonical-path')
    digest=_path_hash(path);ref=root;prefix=()
    while True:
        require(ref.kind in ('tree.leaf','tree.branch') and ref.version==1,'unknown-required-tree-kind')
        obj=decode_envelope(ref,load(ref));leaf=ref.kind=='tree.leaf'
        def check(p):
            require(set(p)=={'path_rule','links','entries' if leaf else 'buckets'} and p['path_rule']==PATH_RULE,'invalid-tree-payload')
        validate_schema(obj,kind=ref.kind,version=1,fields={} if leaf else {'children':'integrity'},validate_payload=check)
        if leaf:
            group=obj.payload['entries'];require(type(group) is list and len(group)<=LEAF_ENTRIES,'invalid-leaf')
            require(group==canonical_entries(group),'unordered-leaf')
            require(all(tuple(_path_hash(e['path'])[:len(prefix)])==prefix for e in group),'wrong-tree-bucket')
            return next((e for e in group if e['path']==path),None)
        keys=obj.payload['buckets']
        require(type(keys) is list and 0<len(keys)<=256 and all(type(k) is int and 0<=k<=255 for k in keys)
                and keys==sorted(set(keys)) and obj.payload['links']['children']==list(range(len(keys))),'invalid-branch')
        require(len(prefix)<TRIE_DEPTH,'tree-prefix-overflow')
        bucket=digest[len(prefix)]
        if bucket not in keys:return None
        ref=obj.edges[keys.index(bucket)].ref;prefix=(*prefix,bucket)
