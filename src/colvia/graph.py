"""Fixed-schema operation closures and disk-backed complete graph inspection.

Schemas and operation policies are product code, not values supplied by records.
An audit's derived index is disposable and is never a second authority. It pins
an immutable root; the loader remains responsible for generation checks per page.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import sys
import sqlite3
from typing import Callable, Iterable, Mapping

from .codec import (Envelope, ObjectRef, decode_envelope, require,
                    validate_schema, verify_object)


@dataclass(frozen=True)
class Schema:
    kind: str
    version: int
    fields: Mapping[str, str]
    payload: Callable[[dict], None]
    # Per-field allowed kinds; None permits an opaque extension, never a role change.
    targets: Mapping[str, frozenset[str] | None]

    local: Callable[[Envelope], None] | None = None
    content: Callable[[ObjectRef, Callable[[ObjectRef], bytes]], None] | None = None

    def check(self, obj: Envelope) -> None:
        require(set(self.fields) == set(self.targets), 'schema-target-fields')
        validate_schema(obj, kind=self.kind, version=self.version,
                        fields=self.fields, validate_payload=self.payload)
        for name, indices in obj.payload['links'].items():
            kinds = self.targets[name]
            for index in indices:
                require(kinds is None or obj.edges[index].ref.kind in kinds,
                        'dependency-kind-mismatch')
        if self.local is not None:
            self.local(obj)


class Registry:
    def __init__(self, schemas: Iterable[Schema]):
        self._schemas = {}
        for schema in schemas:
            key = (schema.kind, schema.version)
            require(key not in self._schemas, 'duplicate-schema')
            self._schemas[key] = schema

    def inspect(self, ref: ObjectRef, raw: bytes, *, required: bool) -> Envelope | None:
        verify_object(ref, raw)
        if ref.kind == 'body.chunk':
            require(ref.version == 1 or not required, 'unknown-required-kind')
            return None
        obj = decode_envelope(ref, raw)
        schema = self._schemas.get((ref.kind, ref.version))
        require(schema is not None or not required, 'unknown-required-kind')
        if schema is not None:
            schema.check(obj)
        return obj

    def content(self, ref: ObjectRef, load: Callable[[ObjectRef], bytes]) -> None:
        schema = self._schemas.get((ref.kind, ref.version))
        if schema is not None and schema.content is not None:
            schema.content(ref, load)


@dataclass(frozen=True)
class ClosurePolicy:
    # Every known object reached by this operation must have an entry. Each tuple
    # selects fixed schema fields, not edge roles guessed from external input.
    fields: Mapping[tuple[str, int], frozenset[str]]
    depth: int = 64
    references: int = 1_000_000
    metadata_bytes: int = 512 * 1024 * 1024

    def check(self, registry: Registry) -> None:
        require(0 <= self.depth <= 64 and 0 < self.references <= 1_000_000 and
                0 < self.metadata_bytes <= 512*1024*1024, 'invalid-closure-budget')
        for key, fields in self.fields.items():
            schema = registry._schemas.get(key)
            require(schema is not None and fields <= schema.fields.keys(), 'invalid-operation-schema')
            # All decision/integrity fields are compulsory. Provenance/display can
            # be requested by an operation, but cannot demote required content.
            mandatory = {name for name, role in schema.fields.items()
                         if role in ('decision', 'integrity')}
            require(mandatory <= fields, 'operation-omits-required-field')


def validate_closure(roots: Iterable[ObjectRef], load: Callable[[ObjectRef], bytes],
                     registry: Registry, policy: ClosurePolicy) -> None:
    """Selected operation only; never silently truncate a required dependency."""
    policy.check(registry)
    pending = [(ref, 0) for ref in roots]
    seen: dict[ObjectRef, int] = {}
    size = 0
    while pending:
        require(len(pending) + len(seen) <= policy.references, 'decision-reference-limit')
        ref, depth = pending.pop()
        require(depth <= policy.depth, 'decision-depth-limit')
        # Revisit a shared node reached by a longer path so a shortcut cannot hide
        # an over-depth path. Raw bytes are immutable and still verified on load.
        previous = seen.get(ref)
        if previous is not None and previous >= depth:
            continue
        seen[ref] = depth
        raw = load(ref)
        obj = registry.inspect(ref, raw, required=True)
        if previous is None and ref.kind != 'body.chunk':
            size += len(raw)
            require(size <= policy.metadata_bytes, 'decision-metadata-limit')
        if obj is None:
            continue
        key = (ref.kind, ref.version)
        require(key in policy.fields, 'operation-schema-unavailable')
        for field in policy.fields[key]:
            pending.extend((obj.edges[i].ref, depth+1) for i in obj.payload['links'][field])
    for ref in seen:
        registry.content(ref, load)


@dataclass(frozen=True)
class AuditBudget:
    objects: int
    edges: int
    total_bytes: int

    def check(self):
        require(all(type(n) is int and n > 0 for n in
                    (self.objects, self.edges, self.total_bytes)), 'invalid-audit-budget')


class _AuditLoader:
    """Fresh audit-only map summaries; no persistent authority or byte cache."""
    def __init__(self, db, load, cancelled):
        self.db, self.load, self.cancelled = db, load, cancelled
        self.map_summaries = self
        db.execute('CREATE TABLE map_checks (kind TEXT, version INTEGER, size INTEGER, '
                   'digest TEXT, prefix BLOB, entries INTEGER, bytes INTEGER, refs INTEGER, '
                   'PRIMARY KEY(kind,version,size,digest,prefix))')

    def __call__(self, ref):
        require(not self.cancelled(), 'audit-cancelled')
        return self.load(ref)

    @staticmethod
    def key(ref, prefix):
        return (ref.kind, ref.version, ref.byte_length, ref.sha256, bytes(prefix))

    def get(self, ref, prefix):
        require(not self.cancelled(), 'audit-cancelled')
        return self.db.execute('SELECT entries,bytes,refs FROM map_checks WHERE '
                              'kind=? AND version=? AND size=? AND digest=? AND prefix=?',
                              self.key(ref, prefix)).fetchone()

    def put(self, ref, prefix, summary):
        self.db.execute('INSERT INTO map_checks VALUES(?,?,?,?,?,?,?,?)',
                        (*self.key(ref, prefix), *summary))


class GraphAudit:
    """Complete reachable graph, bounded RAM and explicit caller resource budget.

    The scratch path must be a fresh caller-owned durable path. Retain it while an
    export consumes refs(); callers may remove it after all consumers close it.
    This is generic reachability/integrity, not an operation capability approval.
    """
    def __init__(self, path: Path, budget: AuditBudget):
        budget.check()
        path = Path(path)
        require(path.is_absolute(), 'audit-path-required')
        for parent in path.parents:
            require(not parent.is_symlink(), 'symlink-audit-path')
        if sys.platform == 'win32':
            # SQLite's rollback journal adds eight UTF-16 code units. Refuse
            # before creating either file; do not disable journaling to fit.
            require(len(str(path).encode('utf-16-le')) // 2 + len('-journal') <= 259,
                    'audit-path-too-long')
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        self.path, self.budget = path, budget
        self.db = sqlite3.connect(path)
        try:
            self.db.execute('PRAGMA cache_size=-2048')
            self.db.executescript('''
                CREATE TABLE nodes (digest TEXT PRIMARY KEY, kind TEXT, version INTEGER,
                    size INTEGER, required INTEGER NOT NULL DEFAULT 0, scanned INTEGER NOT NULL DEFAULT 0, remaining INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE edges (parent TEXT, child TEXT, PRIMARY KEY(parent,child));
                CREATE INDEX children ON edges(child);
                CREATE INDEX pending ON nodes(scanned);
                CREATE TABLE ready (digest TEXT PRIMARY KEY);
            ''')
        except BaseException:
            self.db.close()
            raise
        self.count = self.edge_count = self.total = 0
        self.complete = False
        self.root = None

    def close(self):
        self.db.close()

    @staticmethod
    def _ref(row):
        return ObjectRef(row[1], row[2], row[3], row[0])

    def _add(self, ref, *, required=False):
        row = self.db.execute('SELECT digest,kind,version,size FROM nodes WHERE digest=?',
                              (ref.sha256,)).fetchone()
        if row:
            require(self._ref(row) == ref, 'conflicting-reference')
            if required: self.db.execute('UPDATE nodes SET required=1 WHERE digest=?',(ref.sha256,))
            return
        self.count += 1
        self.total += ref.byte_length
        require(self.count <= self.budget.objects and self.total <= self.budget.total_bytes,
                'audit-resource-limit')
        self.db.execute('INSERT INTO nodes(digest,kind,version,size,required) VALUES(?,?,?,?,?)',
                        (ref.sha256, ref.kind, ref.version, ref.byte_length, int(required)))

    def run(self, root: ObjectRef, load: Callable[[ObjectRef], bytes], registry: Registry,
            *, cancelled: Callable[[], bool] = lambda: False, require_known=False):
        require(self.root is None, 'audit-already-started')
        self.root = root
        self._add(root,required=require_known)
        while True:
            rows = self.db.execute('SELECT digest,kind,version,size FROM nodes WHERE scanned=0 LIMIT 128').fetchall()
            if not rows:
                break
            for row in rows:
                require(not cancelled(), 'audit-cancelled')
                ref = self._ref(row)
                obj = registry.inspect(ref, load(ref), required=False)
                if obj is not None:
                    for edge in obj.edges:
                        self._add(edge.ref, required=(ref.kind,ref.version) in registry._schemas and
                                  edge.role in ('decision','integrity'))
                        cur = self.db.execute('INSERT OR IGNORE INTO edges VALUES(?,?)',
                                              (ref.sha256, edge.ref.sha256))
                        self.edge_count += cur.rowcount
                        require(self.edge_count <= self.budget.edges, 'audit-edge-limit')
                self.db.execute('UPDATE nodes SET scanned=1 WHERE digest=?', (ref.sha256,))
            self.db.commit()
        # Kahn elimination on disk permits deep histories without recursion/depth64.
        self.db.execute('UPDATE nodes SET remaining=(SELECT count(*) FROM edges WHERE parent=nodes.digest)')
        self.db.execute('INSERT INTO ready SELECT digest FROM nodes WHERE remaining=0')
        removed = 0
        while True:
            require(not cancelled(), 'audit-cancelled')
            rows = self.db.execute('SELECT digest FROM ready LIMIT 128').fetchall()
            if not rows:
                break
            for (digest,) in rows:
                self.db.execute('DELETE FROM ready WHERE digest=?', (digest,))
                # Avoid collecting high fan-in in Python; SQLite applies updates.
                self.db.execute('UPDATE nodes SET remaining=remaining-1 WHERE digest IN '
                                '(SELECT parent FROM edges WHERE child=?)', (digest,))
                self.db.execute('INSERT OR IGNORE INTO ready SELECT n.digest FROM nodes n '
                                'JOIN edges e ON e.parent=n.digest WHERE e.child=? AND n.remaining=0', (digest,))
                removed += 1
            self.db.commit()
        require(removed == self.count, 'reference-cycle')
        # Complete declared resource preflight precedes secondary content checks.
        content_load = _AuditLoader(self.db, load, cancelled)
        cursor = self.db.execute('SELECT digest,kind,version,size,required FROM nodes')
        while rows := cursor.fetchmany(128):
            for row in rows:
                require(not cancelled(), 'audit-cancelled')
                ref=self._ref(row)
                if require_known and row[4]: registry.inspect(ref,load(ref),required=True)
                registry.content(ref, content_load)
            self.db.commit()
        self.complete = True
        return self

    def refs(self):
        require(self.complete, 'audit-incomplete')
        cursor = self.db.execute('SELECT digest,kind,version,size FROM nodes ORDER BY kind,version,digest')
        while rows := cursor.fetchmany(128):
            for row in rows:
                yield self._ref(row)

    def required_kinds(self):
        """Fixed required schema vocabulary, independent of enabled execution."""
        require(self.complete, 'audit-incomplete')
        rows=self.db.execute('SELECT DISTINCT kind,version FROM nodes WHERE required=1 OR digest=? ORDER BY kind,version',
                             (self.root.sha256,))
        return tuple((kind,version) for kind,version in rows)
