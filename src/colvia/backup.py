"""Versioned logical backup framing; no installation, path extraction or activation.

Writers use a complete GraphAudit pinned at one root. Readers stream into a caller's
unpublished candidate and certify completion only after EOF and manifest checks.
Whole-graph and capability validation remain mandatory before candidate activation.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import BinaryIO, Callable, Iterable

from .codec import (ObjectRef, canonical_bytes, decode_canonical, decode_envelope,
                    require, verify_object)
from .graph import GraphAudit

MAGIC = b'COLVIA\x00EXPORT\x00\x01'
FRAME_HEADER_LIMIT = 16384


def _write(stream, raw):
    view = memoryview(raw)
    while view:
        n = stream.write(view)
        require(type(n) is int and 0 < n <= len(view), 'export-write-incomplete')
        view = view[n:]


def _read(stream, size):
    parts = []
    left = size
    while left:
        raw = stream.read(left)
        require(type(raw) is bytes and 0 < len(raw) <= left, 'export-truncated')
        parts.append(raw); left -= len(raw)
    return b''.join(parts)


def schema_requirement(kind,version):
    return f'schema:{kind}:{version}'


def supported_requirements(registry):
    return {'foundation-v1',schema_requirement('body.chunk',1),
            *(schema_requirement(kind,version) for kind,version in registry._schemas)}


def audit_requirements(audit):
    values=sorted({'foundation-v1',*(schema_requirement(kind,version) for kind,version in audit.required_kinds())})
    # v1 schema readers and writers share this vocabulary. Runtime execution
    # permission is deliberately absent. Future write-only capabilities have a
    # separate header field and cannot silently become read requirements.
    return dict(read_requirements=values,write_requirements=list(values))


def _header(project, root, read_requirements, write_requirements):
    require(type(project) is str and 0 < len(project) <= 160 and
            all(c.isascii() and (c.isalnum() or c in '-_.') for c in project), 'export-project')
    for requirements in (read_requirements,write_requirements):
        require(type(requirements) is list and len(requirements)<=256 and
                all(type(r) is str and 0 < len(r) <= 160 and r.isascii() for r in requirements) and
                requirements == sorted(set(requirements)), 'export-requirements')
    return dict(format=1, project=project, root=root.as_dict(),
                read_requirements=read_requirements,write_requirements=write_requirements)


def write_export(stream: BinaryIO, *, project: str, audit: GraphAudit,
                 load: Callable[[ObjectRef], bytes], read_requirements=None, write_requirements=None,
                 cancelled: Callable[[], bool] = lambda: False) -> dict:
    require(audit.complete and audit.root is not None, 'audit-incomplete')
    derived=audit_requirements(audit)
    for name,supplied in (('read_requirements',read_requirements),('write_requirements',write_requirements)):
        require(supplied is None or supplied==derived[name],'export-requirements-mismatch')
    header = canonical_bytes(_header(project, audit.root, **derived))
    require(len(header) <= FRAME_HEADER_LIMIT, 'export-header-limit')
    digest = hashlib.sha256(); size = count = 0
    def emit(raw):
        nonlocal size
        _write(stream, raw); digest.update(raw); size += len(raw)
    emit(MAGIC); emit(len(header).to_bytes(4,'big')); emit(header)
    for ref in audit.refs():
        require(not cancelled(), 'export-cancelled')
        raw = load(ref); verify_object(ref, raw)
        encoded = canonical_bytes(ref.as_dict())
        emit(b'O'); emit(len(encoded).to_bytes(4,'big')); emit(encoded); emit(raw)
        count += 1
    require(count == audit.count, 'export-object-count')
    manifest = dict(objects=count, bytes=size, sha256=digest.hexdigest())
    tail = canonical_bytes(manifest)
    _write(stream, b'M'+len(tail).to_bytes(4,'big')+tail)
    # Durable destination publication/fsync and re-read belong to the caller.
    return manifest


@dataclass(frozen=True)
class ExportBudget:
    objects: int
    total_bytes: int


class ExportReader:
    def __init__(self, stream: BinaryIO, budget: ExportBudget):
        require(type(budget.objects) is int and budget.objects>0 and
                type(budget.total_bytes) is int and budget.total_bytes>0, 'invalid-export-budget')
        self.stream, self.budget = stream, budget
        self.digest = hashlib.sha256(); self.size = 0
        self.complete = False; self.started = False
        require(self._take(len(MAGIC)) == MAGIC, 'unknown-export-format')
        header = self._metadata()
        require(type(header) is dict and set(header)=={'format','project','root','read_requirements','write_requirements'} and
                type(header['format']) is int and header['format']==1, 'invalid-export-header')
        self.root = ObjectRef.parse(header['root'])
        require(_header(header['project'],self.root,header['read_requirements'],header['write_requirements'])==header, 'invalid-export-header')
        self.header = header

    def _take(self, size):
        require(self.size+size <= self.budget.total_bytes, 'export-resource-limit')
        raw = _read(self.stream,size)
        self.digest.update(raw); self.size += size
        return raw

    def _metadata(self):
        size = int.from_bytes(self._take(4),'big')
        require(0 < size <= FRAME_HEADER_LIMIT, 'export-header-limit')
        return decode_canonical(self._take(size))

    def objects(self) -> Iterable[tuple[ObjectRef,bytes]]:
        require(not self.started, 'export-already-read')
        self.started = True
        count = 0; previous = None; root_seen = False
        while True:
            # The final marker and manifest are not part of the preceding digest.
            require(self.size+1 <= self.budget.total_bytes, 'export-resource-limit')
            marker = _read(self.stream,1)
            if marker == b'M':
                size = int.from_bytes(_read(self.stream,4),'big')
                require(0 < size <= FRAME_HEADER_LIMIT, 'export-header-limit')
                require(self.size+5+size <= self.budget.total_bytes, 'export-resource-limit')
                manifest = decode_canonical(_read(self.stream,size))
                require(type(manifest) is dict and set(manifest)=={'objects','bytes','sha256'} and
                        type(manifest['objects']) is int and type(manifest['bytes']) is int and
                        manifest == dict(objects=count,bytes=self.size,sha256=self.digest.hexdigest()),
                        'export-manifest-mismatch')
                require(root_seen, 'export-root-missing')
                require(self.stream.read(1) == b'', 'export-trailing-bytes')
                self.manifest=manifest
                self.complete = True
                return
            require(marker == b'O', 'export-frame-kind')
            self.digest.update(marker); self.size += 1
            count += 1
            require(count <= self.budget.objects, 'export-object-limit')
            ref = ObjectRef.parse(self._metadata())
            order = (ref.kind,ref.version,ref.sha256)
            require(previous is None or previous < order, 'export-order-or-duplicate')
            previous = order
            raw = self._take(ref.byte_length); verify_object(ref,raw)
            if ref == self.root: root_seen = True
            yield ref,raw


class ImportedSnapshot:
    """Unpublished streaming import with complete integrity and capability checks.

    Uses a fresh disk-backed audit index to retain incoming bytes. It never
    changes an active store or interprets archive paths as filesystem paths.
    """
    def __init__(self, path, stream, *, budget, graph_budget, registry, capabilities,
                 writable_capabilities=None, cancelled=lambda:False):
        self.audit = GraphAudit(path,graph_budget)
        self.registry = registry
        self.header = None
        self.complete = False
        db = self.audit.db
        db.execute('CREATE TABLE incoming (digest TEXT PRIMARY KEY,kind TEXT,version INTEGER,size INTEGER,data BLOB)')
        try:
            reader = ExportReader(stream,budget)
            require(set(reader.header['read_requirements']) <= set(capabilities), 'import-capability-unavailable')
            require(reader.root.kind=='state.root' and reader.root.version==1,'import-root-kind')
            batch_bytes = batch_count = 0
            for ref,raw in reader.objects():
                require(not cancelled(),'import-cancelled')
                if batch_count and (batch_bytes+len(raw)>4*1024*1024 or batch_count>=64):
                    db.commit(); batch_bytes=batch_count=0
                db.execute('INSERT INTO incoming VALUES(?,?,?,?,?)',
                           (ref.sha256,ref.kind,ref.version,ref.byte_length,raw))
                batch_bytes+=len(raw); batch_count+=1
            db.commit()
            require(reader.complete,'import-incomplete')
            self.header=reader.header;self.manifest=reader.manifest
            self.audit.run(reader.root,self.load,registry,cancelled=cancelled,require_known=True)
            derived=audit_requirements(self.audit)
            require(all(self.header[name]==value for name,value in derived.items()),'import-requirements-mismatch')
            self.writable=set(self.header['write_requirements'])<=set(writable_capabilities or ())
            # Reject extra unreferenced objects rather than importing hidden data.
            count=db.execute('SELECT count(*) FROM incoming').fetchone()[0]
            require(count==self.audit.count,'import-unreachable-objects')
            root=decode_envelope(reader.root,self.load(reader.root))
            require(root.payload.get('project')==reader.header['project'],'import-project-mismatch')
            self.complete=True
        except BaseException:
            db.rollback(); self.audit.close()
            raise

    def load(self,ref):
        row=self.audit.db.execute('SELECT kind,version,size,data FROM incoming WHERE digest=?',(ref.sha256,)).fetchone()
        require(row is not None and (row[0],row[1],row[2])==(ref.kind,ref.version,ref.byte_length), 'import-object-unavailable')
        raw=bytes(row[3]); verify_object(ref,raw)
        return raw

    def objects(self):
        require(self.complete,'import-incomplete')
        for ref in self.audit.refs():
            yield ref,self.load(ref)

    def close(self):
        self.audit.close()
