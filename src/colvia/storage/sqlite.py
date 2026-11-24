"""One immutable store generation with short transactions and head CAS.

Authority resolution and active-pointer fencing are supplied by the lifecycle
adapter. SQL projections are never accepted in place of a verified root/map.
"""
from __future__ import annotations

from contextlib import ExitStack,contextmanager,nullcontext
from contextvars import ContextVar
from dataclasses import dataclass
from functools import wraps
import os
from pathlib import Path
import sqlite3
import stat
import sys
import threading
import time
import weakref
from typing import Callable, Iterable
from urllib.parse import quote

from ..codec import (CHUNK_LIMIT, Edge, ObjectRef, RecordError, PublicationRefused, decode_envelope,
                     encode_envelope, require, validate_schema, verify_object)
from ..maps import build_map, map_get, map_update

SCHEMA_VERSION = 1
BATCH_BYTES = 4 * 1024 * 1024
BATCH_OBJECTS = 64
BUSY_SECONDS = 5
_PROCESS_LOCKS = weakref.WeakValueDictionary()
_PROCESS_LOCKS_GUARD = threading.Lock()
_VALIDATIONS = ContextVar("colvia_validation_views", default={})
_OPERATION_READS = ContextVar("colvia_operation_reads", default=None)
_IMMUTABLE_PAGES = ContextVar("colvia_immutable_pages", default=None)
_PAGE_BYTES = 4 * 1024 * 1024
_PAGE_READS = 64
_PAGE_SECONDS = .15
_METADATA_REUSE_BYTES = 2 * 1024 * 1024
_METADATA_REUSE_ENTRIES = 2048
_PROOF_REUSE_ENTRIES = 8192


class _ImmutablePages:
    """Short read-only transactions during an explicitly pure record walk."""
    def __init__(self, store, stack):
        self.store = store
        self.stack = stack
        self.thread = threading.get_ident()
        self.closed = False
        self.reads = 0
        self.size = 0
        self.started = 0.0

    def flush(self):
        if self.reads:
            self.reads = self.size = 0
            self.stack.close()

    def read(self, query, size):
        if size > _PAGE_BYTES:
            self.flush()
            with self.store._transaction():
                return query()
        if self.reads == _PAGE_READS or self.size + size > _PAGE_BYTES or (
                self.reads and time.monotonic() - self.started >= _PAGE_SECONDS):
            self.flush()
        if not self.reads:
            self.stack.enter_context(self.store._transaction(_page=True))
            self.started = time.monotonic()
        self.reads += 1
        self.size += size
        return query()


def _active_page():
    page = _IMMUTABLE_PAGES.get()
    if page is not None and page.thread == threading.get_ident() and not page.closed:
        return page
    return None


class _VerifiedObjects:
    """Bounded reuse of successful immutable reads. Body chunks stay transient."""
    def __init__(self, *, entries=_METADATA_REUSE_ENTRIES):
        self.entries = entries
        self.metadata = {}
        self.body_proofs = set()
        self.remaining = _METADATA_REUSE_BYTES
        self.closed = False
        self.needs_guard = False

    def read(self, ref, read):
        if self.closed or getattr(ref, 'kind', None) == 'body.chunk':
            return read(ref)
        if ref in self.metadata:
            self.needs_guard = True
            return self.metadata[ref]
        raw = read(ref)
        if type(raw) is bytes and len(self.metadata) < self.entries and len(raw) <= self.remaining:
            self.metadata[ref] = raw
            self.remaining -= len(raw)
        return raw

    def close(self):
        self.closed = True
        self.metadata.clear()
        self.body_proofs.clear()


def reuse_operation_reads(method):
    @wraps(method)
    def run(service, *args, **kwargs):
        if not isinstance(service.store, GenerationStore):
            return method(service, *args, **kwargs)
        with service.store.reuse_operation_reads():
            return method(service, *args, **kwargs)
    return run


def fresh_view_reads(method):
    @wraps(method)
    def read(service, *args, **kwargs):
        if _OPERATION_READS.get() is None:
            return method(service, *args, **kwargs)
        token = _OPERATION_READS.set(None)
        try:
            return method(service, *args, **kwargs)
        finally:
            _OPERATION_READS.reset(token)
    return read


def _process_lock(identity):
    # Separate read-only/writable connections in one process must not overlap
    # transactions on the qualified macOS VFS. Inter-process exclusion remains
    # SQLite's job. Entries live only while an open handle holds the lock.
    with _PROCESS_LOCKS_GUARD:
        lock = _PROCESS_LOCKS.get(identity)
        if lock is None:
            lock = threading.RLock()
            _PROCESS_LOCKS[identity] = lock
        return lock

def runtime_capabilities():
    from ..backup import supported_requirements
    from ..records import application_registry
    return frozenset(supported_requirements(application_registry()))


_SCHEMA = (
    "CREATE TABLE restore_origin (singleton INTEGER PRIMARY KEY CHECK(singleton=1), operation TEXT NOT NULL, root TEXT NOT NULL, manifest TEXT NOT NULL, complete INTEGER NOT NULL CHECK(complete IN (0,1))) STRICT",
    "CREATE TABLE requirements (role TEXT NOT NULL CHECK(role IN ('read','write')), capability TEXT NOT NULL, PRIMARY KEY(role,capability)) STRICT",
    '''CREATE TABLE generation (
        singleton INTEGER PRIMARY KEY CHECK(singleton=1),
        project TEXT NOT NULL, instance TEXT NOT NULL, generation TEXT NOT NULL,
        fence TEXT, quiescent TEXT, needs_rebind INTEGER NOT NULL CHECK(needs_rebind IN (0,1))
    ) STRICT''',
    '''CREATE TABLE objects (
        digest TEXT PRIMARY KEY, kind TEXT NOT NULL, version INTEGER NOT NULL,
        size INTEGER NOT NULL, data BLOB NOT NULL,
        published INTEGER NOT NULL CHECK(published IN (0,1)),
        CHECK(size=length(data))
    ) STRICT''',
    '''CREATE TABLE current_root (
        singleton INTEGER PRIMARY KEY CHECK(singleton=1),
        digest TEXT NOT NULL REFERENCES objects(digest)
    ) STRICT''',
    '''CREATE TABLE imports (
        id TEXT PRIMARY KEY, owner TEXT NOT NULL,
        state TEXT NOT NULL CHECK(state IN ('active','published','abandoned'))
    ) STRICT''',
    '''CREATE TABLE claims (
        import_id TEXT NOT NULL REFERENCES imports(id),
        digest TEXT NOT NULL REFERENCES objects(digest),
        PRIMARY KEY(import_id,digest)
    ) STRICT''',
    '''CREATE TABLE operations (
        id TEXT PRIMARY KEY, before_root TEXT NOT NULL REFERENCES objects(digest),
        after_root TEXT NOT NULL REFERENCES objects(digest)
    ) STRICT''',
    '''CREATE TRIGGER object_bytes_immutable BEFORE UPDATE OF digest,kind,version,size,data ON objects
        BEGIN SELECT RAISE(ABORT,'immutable-object'); END''',
    '''CREATE TRIGGER published_no_demote BEFORE UPDATE OF published ON objects
        WHEN OLD.published=1 AND NEW.published<>1
        BEGIN SELECT RAISE(ABORT,'published-object'); END''',
    '''CREATE TRIGGER published_no_delete BEFORE DELETE ON objects WHEN OLD.published=1
        BEGIN SELECT RAISE(ABORT,'published-object'); END''',
    '''CREATE TRIGGER generation_identity_immutable BEFORE UPDATE OF project,instance,generation ON generation
        BEGIN SELECT RAISE(ABORT,'immutable-generation'); END''',
    '''CREATE TRIGGER retirement_fence_monotonic BEFORE UPDATE OF fence ON generation
        WHEN OLD.fence IS NOT NULL AND (NEW.fence IS NULL OR NEW.fence<>OLD.fence)
        BEGIN SELECT RAISE(ABORT,'retired-generation'); END''',
)


MAX_TOKEN_LENGTH = 160


def _token(value):
    require(type(value) is str and 0 < len(value) <= MAX_TOKEN_LENGTH and value[0].isascii() and value[0].isalnum() and
            all(c.isascii() and (c.isalnum() or c in '-_.') for c in value), 'invalid-store-id')


def _identity(path: Path):
    if sys.platform=='win32':
        from .windows import WindowsFiles
        return WindowsFiles().identity(path)
    require(path.is_absolute(), 'absolute-store-path-required')
    for part in (*reversed(path.parents), path):
        info = part.lstat()
        require(not stat.S_ISLNK(info.st_mode), 'symlink-store-path')
    info = path.lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'unsafe-store-file')
    return info.st_dev, info.st_ino


def _settings(db):
    require(sqlite3.sqlite_version_info >= (3,37,0), 'sqlite-version-unsupported')
    if not db.execute("SELECT sqlite_compileoption_used('OMIT_LOAD_EXTENSION')").fetchone()[0]:
        db.setconfig(sqlite3.SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION, False)
        require(not db.getconfig(sqlite3.SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION),
                'sqlite-extension-loading-enabled')
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA trusted_schema=OFF')
    db.execute('PRAGMA synchronous=EXTRA')
    if sys.platform == 'darwin': db.execute('PRAGMA fullfsync=ON')
    require(db.execute('PRAGMA foreign_keys').fetchone()[0] == 1 and
            db.execute('PRAGMA synchronous').fetchone()[0] == 3 and
            db.execute('PRAGMA journal_mode').fetchone()[0].lower() == 'delete' and
            db.execute('PRAGMA trusted_schema').fetchone()[0] == 0 and
            (sys.platform != 'darwin' or db.execute('PRAGMA fullfsync').fetchone()[0] == 1),
            'sqlite-settings-unavailable')


class StorageError(RecordError):
    """Structured engine facts, without SQL, paths, or exception messages."""
    def __init__(self, code, diagnostic):
        super().__init__(code)
        self.diagnostic = diagnostic


class StoragePublicationRefused(StorageError, PublicationRefused):
    pass


def _refused(exc):
    refused=(StoragePublicationRefused(exc.code, exc.diagnostic)
             if isinstance(exc, StorageError) else PublicationRefused(exc.code))
    for name in ('directory','workspace','preparation_state'):
        if hasattr(exc,name):setattr(refused,name,getattr(exc,name))
    return refused


_SQL_BASES = ('ERROR', 'INTERNAL', 'PERM', 'ABORT', 'BUSY', 'LOCKED', 'NOMEM',
              'READONLY', 'INTERRUPT', 'IOERR', 'CORRUPT', 'NOTFOUND', 'FULL',
              'CANTOPEN', 'PROTOCOL', 'EMPTY', 'SCHEMA', 'TOOBIG', 'CONSTRAINT',
              'MISMATCH', 'MISUSE', 'NOLFS', 'AUTH', 'FORMAT', 'RANGE', 'NOTADB',
              'NOTICE', 'WARNING')
_SQL_NAMES = {name: getattr(sqlite3, name) for name in dir(sqlite3)
              if any(name == 'SQLITE_' + base or name.startswith('SQLITE_' + base + '_')
                     for base in _SQL_BASES) and type(getattr(sqlite3, name)) is int}


def _sql_error(exc, path, *, uncertain=False, stage='transaction'):
    raw_name=getattr(exc,'sqlite_errorname',None)
    raw_code=getattr(exc,'sqlite_errorcode',None)
    numeric=raw_code if type(raw_code) is int and 0 <= raw_code <= 0x7fffffff else None
    name=raw_name if type(raw_name) is str and raw_name in _SQL_NAMES and _SQL_NAMES[raw_name] == numeric else 'SQLITE_ERROR'
    diagnostic={'stage':stage if stage in ('open','configure','begin','transaction','commit','recovery') else 'transaction',
                'sqlite_code':numeric, 'sqlite_name':name if name == raw_name and numeric is not None else None}
    if uncertain: code='store-outcome-unknown'
    elif name.startswith(('SQLITE_BUSY','SQLITE_LOCKED')): code='store-busy'
    elif name == 'SQLITE_READONLY_ROLLBACK': code='recovery-required'
    elif name == 'SQLITE_READONLY_DBMOVED': code='store-file-replaced'
    elif name.startswith(('SQLITE_CORRUPT','SQLITE_NOTADB')): code='store-corrupt'
    elif name.startswith('SQLITE_FULL'): code='store-full'
    else: code='store-io-unavailable'
    return StorageError(code,diagnostic)


def _row_ref(row):
    return ObjectRef(row['kind'], row['version'], row['size'], row['digest'])


@dataclass(frozen=True, slots=True)
class Root:
    ref: ObjectRef
    heads: ObjectRef
    operations: ObjectRef
    sequence: int


class ValidationView:
    """One immutable root and the exact head read set used by a validator.

    It remains callable for immutable object loads. Application validators use
    head()/root() for mutable state; public reads on another handle to the same
    inode in this synchronous context are routed here too. A validator must not
    spawn concurrent work or query SQL directly.
    """
    def __init__(self, root, load, *, check_chunk=None):
        self.snapshot = root
        self._check_chunk = check_chunk
        self.load = load
        self.reads = {}
        self.full_root_read = False
        self._body_proofs = None

    def __call__(self, ref): return self.load(ref)

    @contextmanager
    def reuse_immutable_objects(self, *, published_proofs=None):
        """Reuse a publication's exact bytes and body proofs within its validator."""
        if self._body_proofs is not None:
            yield
            return
        source = self.load
        memo = _VerifiedObjects()
        self._body_proofs = set() if published_proofs is None else published_proofs
        self.load = lambda ref: memo.read(ref, source)
        try:
            yield
        finally:
            self.load = source
            self._body_proofs = None
            memo.close()

    def verify_chunk(self, ref):
        if self._body_proofs is None or (ref.kind, ref.version) != ('body.chunk', 1):
            return False
        if ref not in self._body_proofs:
            if self._check_chunk is None:
                verify_object(ref, self.load(ref))
            else:
                self._check_chunk(ref)
            self._remember_body_proof(ref)
        return True

    def verify_body(self, ref):
        if self._body_proofs is None:
            return False
        if ref not in self._body_proofs:
            from ..bodies import body_bytes, descriptor
            if self._check_chunk is None:
                for _ in body_bytes(ref, self):
                    pass
            else:
                for edge in descriptor(ref, self.load(ref)).edges:
                    self.verify_chunk(edge.ref)
            self._remember_body_proof(ref)
        return True

    def _remember_body_proof(self, ref):
        if len(self._body_proofs) < _PROOF_REUSE_ENTRIES:
            self._body_proofs.add(ref)

    def head(self, key):
        if key not in self.reads:
            self.reads[key] = map_get(self.snapshot.heads, key, self.load)
        return self.reads[key]

    def root(self):
        self.full_root_read = True
        return self.snapshot


class SnapshotBudget(Exception):
    """The ordinary screen can fall back to separately guarded reads."""


class _RecordSnapshot:
    """Read published objects and heads from one guarded transaction."""

    def __init__(self, store, *, bounded=False):
        self.project = store.project
        self.instance = store.instance
        self._load = store._load
        self._requirements = store._requirements
        self._root = store._root()
        self._memo = _VerifiedObjects() if bounded else None
        self._started = time.monotonic()
        self._read_count = self._read_bytes = 0

    def load(self, ref):
        require(self._load is not None, 'record-snapshot-closed')
        if self._memo is None:
            return self._load(ref)
        return self._memo.read(ref, self._bounded_load)

    def _bounded_load(self, ref):
        self._read_count += 1
        self._read_bytes += ref.byte_length
        if (self._read_count > 1024 or self._read_bytes > 8 * 1024 * 1024
                or time.monotonic() - self._started >= .2):
            raise SnapshotBudget
        return self._load(ref)

    def head(self, key):
        return map_get(self.root().heads, key, self.load)

    def root(self):
        require(self._load is not None, 'record-snapshot-closed')
        return self._root

    def requirements(self):
        require(self._load is not None, 'record-snapshot-closed')
        return self._requirements()

    def close(self):
        self._load = None
        self._requirements = None
        if self._memo is not None:
            self._memo.close()


class GenerationStore:
    def __init__(self, path: Path, *, project: str, instance: str, generation: str,
                 readonly: bool = False, active_check: Callable[[], None],
                 _retirement_operation: str|None = None,
                 write_check: Callable[[], None] = lambda: None, reader_capabilities=None, writer_capabilities=None,
                 transaction_scope=nullcontext, read_active_check=None):
        for value in (project, instance, generation): _token(value)
        self.path = Path(path)
        self.project, self.instance, self.generation = project, instance, generation
        self.readonly, self.active_check = readonly, active_check
        self.write_check = write_check
        self.transaction_scope=transaction_scope
        self._write_epoch=0
        self.read_active_check = active_check if read_active_check is None else read_active_check
        self.reader_capabilities=frozenset(runtime_capabilities() if reader_capabilities is None else reader_capabilities)
        self.writer_capabilities=frozenset(runtime_capabilities() if writer_capabilities is None else writer_capabilities)
        require(_retirement_operation is None or readonly, "retired-read-only")
        self._retirement_operation = _retirement_operation
        self._workspace_location = None
        self.identity = _identity(self.path)
        self.process_lock = _process_lock(self.identity)
        uri = self.path.as_uri() + ('?mode=ro' if readonly else '?mode=rw')
        require(self.process_lock.acquire(timeout=BUSY_SECONDS),'store-busy')
        self.db = None
        stage = 'open'
        try:
            self.db = sqlite3.connect(uri, uri=True, timeout=BUSY_SECONDS, isolation_level=None)
            self.db.row_factory = sqlite3.Row
            stage = 'configure'
            _settings(self.db)
            with self._transaction():
                require(self.db.execute('PRAGMA user_version').fetchone()[0] == SCHEMA_VERSION,
                        'unknown-store-schema')
                actual = {row[0] for row in self.db.execute(
                    "SELECT sql FROM sqlite_schema WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%'")}
                require(actual == set(_SCHEMA), 'store-schema-mismatch')
                self._root()
        except BaseException as exc:
            if self.db is not None: self.db.close()
            if isinstance(exc,sqlite3.Error): raise _sql_error(exc,self.path,stage=stage) from None
            raise
        finally:
            self.process_lock.release()

    @classmethod
    def create(cls, path: Path, *, project: str, instance: str, generation: str,
               active_check: Callable[[], None], reader_capabilities=None, writer_capabilities=None, needs_rebind=False):
        require(type(needs_rebind) is bool,'invalid-rebind-state')
        for value in (project, instance, generation): _token(value)
        path = Path(path)
        require(path.is_absolute() and path.parent.is_dir(), 'store-parent-required')
        for parent in (path.parent, *path.parents):
            require(not parent.is_symlink(), 'symlink-store-path')
        from .files import platform_files
        platform_files().create(path,b'')
        # Failure leaves a diagnostic candidate file; never reuse or remove it implicitly.
        db = sqlite3.connect(path, isolation_level=None)
        try:
            _settings(db)
            db.execute('BEGIN IMMEDIATE')
            for statement in _SCHEMA: db.execute(statement)
            db.execute(f'PRAGMA user_version={SCHEMA_VERSION}')
            db.execute('INSERT INTO generation VALUES(1,?,?,?,NULL,NULL,?)', (project,instance,generation,int(needs_rebind)))
            db.executemany('INSERT INTO requirements VALUES(?,?)',[(role,cap) for role in ('read','write') for cap in ('foundation-v1','schema:state.root:1','schema:map.leaf:1')])
            empty = build_map([])
            for ref, raw in empty.objects:
                db.execute('INSERT INTO objects VALUES(?,?,?,?,?,1)',
                           (ref.sha256,ref.kind,ref.version,ref.byte_length,raw))
            ref, raw = encode_envelope('state.root', 1,
                dict(project=project,sequence=0,operation=None,links={'heads':[0],'operations':[1],'previous':[]}),
                (Edge('integrity',empty.root),Edge('integrity',empty.root)))
            db.execute('INSERT INTO objects VALUES(?,?,?,?,?,1)',
                       (ref.sha256,ref.kind,ref.version,ref.byte_length,raw))
            db.execute('INSERT INTO current_root VALUES(1,?)',(ref.sha256,))
            db.execute('COMMIT')
        finally:
            db.close()
        return cls(path,project=project,instance=instance,generation=generation,active_check=active_check,
                   reader_capabilities=reader_capabilities,writer_capabilities=writer_capabilities)

    def close(self):
        page = self._current_page()
        if page is not None:
            page.flush()
        memo = self._operation_read_cache()
        if memo is not None:
            memo.close()
        require(self.process_lock.acquire(timeout=BUSY_SECONDS),'store-busy')
        try: self.db.close()
        finally: self.process_lock.release()

    def pin_workspace_location(self, key, ref):
        expected = (key, ref)
        if self._workspace_location is None:
            self._workspace_location = expected
        require(self._workspace_location == expected, 'workspace-location-changed')

    def _guard(self, *, write=False, lifecycle=False, permitted_fence=None):
        require(_identity(self.path) == self.identity, 'store-file-replaced')
        (self.active_check if write else self.read_active_check)()
        row = self.db.execute('SELECT * FROM generation WHERE singleton=1').fetchone()
        require(row is not None and (row['project'],row['instance'],row['generation']) ==
                (self.project,self.instance,self.generation), 'store-generation-mismatch')
        rows=self.db.execute('SELECT role,capability FROM requirements').fetchall()
        require({r['capability'] for r in rows if r['role']=='read'}<=self.reader_capabilities,'store-reader-capability-unavailable')
        if write:require({r['capability'] for r in rows if r['role']=='write'}<=self.writer_capabilities,'store-writer-capability-unavailable')
        allowed=permitted_fence or self._retirement_operation
        require(row['fence'] is None or (allowed is not None and row['fence']==allowed), 'generation-retired')
        require(not write or lifecycle or row['quiescent'] is None, 'generation-quiescent')
        if write and not lifecycle:
            require(not row['needs_rebind'],'instance-rebind-required')
            self.write_check()
        if write and self._workspace_location is not None:
            key, ref = self._workspace_location
            require(map_get(self._root().heads, key, self._load) == ref, 'workspace-location-changed')

    @contextmanager
    def _transaction(self, *, write=False, lifecycle=False, retiring=None, _page=False):
        page = _active_page()
        if page is not None and not _page:
            page.flush()
        with self.transaction_scope():
            with self._transaction_inner(write=write,lifecycle=lifecycle,retiring=retiring):
                if write:
                    self._write_epoch += 1
                yield
        memo = self._operation_read_cache()
        if memo is not None:
            memo.needs_guard = False

    @contextmanager
    def _transaction_inner(self, *, write=False, lifecycle=False, retiring=None):
        require(not write or not self.readonly, 'store-readonly')
        committing = False
        stage = 'begin'
        started = time.monotonic()
        require(self.process_lock.acquire(timeout=BUSY_SECONDS),'store-busy')
        try:
            remaining = max(0,int((BUSY_SECONDS-(time.monotonic()-started))*1000))
            require(remaining > 0, 'store-busy')
            self.db.execute(f'PRAGMA busy_timeout={remaining}')
            self.db.execute('BEGIN IMMEDIATE' if write else 'BEGIN')
            stage = 'transaction'
            self._guard(write=write,lifecycle=lifecycle)
            yield
            self._guard(write=write,lifecycle=lifecycle,permitted_fence=retiring)
            committing = True
            stage = 'commit'
            self.db.execute('COMMIT')
        except BaseException as exc:
            rollback_failed = False
            rolled_back = False
            if self.db.in_transaction:
                try:
                    self.db.execute('ROLLBACK')
                    rolled_back = not self.db.in_transaction
                except sqlite3.Error: rollback_failed = True
            if isinstance(exc, sqlite3.Error):
                busy_rollback = rolled_back and getattr(exc,'sqlite_errorname','').startswith(('SQLITE_BUSY','SQLITE_LOCKED'))
                raise _sql_error(exc,self.path,uncertain=(committing and not busy_rollback) or rollback_failed,stage=stage) from None
            if rollback_failed: raise RecordError('store-outcome-unknown') from None
            if write and not committing and rolled_back and isinstance(exc,RecordError) and exc.code!='store-outcome-unknown':
                raise _refused(exc) from exc
            raise
        finally:
            self.process_lock.release()

    def _require_visible(self, row, ref, import_id):
        require(row is not None and _row_ref(row)==ref, 'object-unavailable')
        if not row['published']:
            require(import_id is not None and self.db.execute(
                'SELECT 1 FROM claims WHERE import_id=? AND digest=?',(import_id,ref.sha256)).fetchone() is not None,
                'object-unpublished')

    def _load(self, ref, import_id=None):
        row = self.db.execute('SELECT * FROM objects WHERE digest=?',(ref.sha256,)).fetchone()
        self._require_visible(row, ref, import_id)
        raw = bytes(row['data']); verify_object(ref,raw)
        if ref.kind != 'body.chunk': decode_envelope(ref,raw)
        return raw

    def _operation_read_cache(self):
        scope = _OPERATION_READS.get()
        if scope is not None and scope[0] is self and scope[1] == threading.get_ident() and not scope[2].closed:
            return scope[2]
        return None

    @contextmanager
    def reuse_operation_reads(self):
        """Share published metadata only within one explicit synchronous operation."""
        if self.readonly or self._operation_read_cache() is not None:
            yield
            return
        memo = _VerifiedObjects()
        token = _OPERATION_READS.set((self, threading.get_ident(), memo))
        try:
            yield
            if memo.needs_guard and not memo.closed:
                # Verify the selected store if no live transaction followed the
                # final cached read, as can happen when returning a receipt.
                with self._transaction():
                    pass
        finally:
            memo.close()
            _OPERATION_READS.reset(token)

    def _current_page(self):
        page = _active_page()
        return page if page is not None and page.store is self else None

    @contextmanager
    def immutable_reads(self):
        previous = _active_page()
        if previous is not None:
            if previous.store is self:
                yield
                return
            previous.flush()
        with ExitStack() as stack:
            page = _ImmutablePages(self, stack)
            token = _IMMUTABLE_PAGES.set(page)
            try:
                yield
            finally:
                page.closed = True
                _IMMUTABLE_PAGES.reset(token)

    def _immutable_read(self, read, size):
        page = self._current_page()
        if page is not None:
            return page.read(read, size)
        with self._transaction():
            return read()

    def _load_guarded(self, ref, import_id=None):
        return self._immutable_read(lambda: self._load(ref, import_id), ref.byte_length)

    def _chunk_identity(self, ref):
        def check():
            row = self.db.execute('SELECT kind,version,size,digest,published,length(data) AS actual_size '
                                  'FROM objects WHERE digest=?',(ref.sha256,)).fetchone()
            self._require_visible(row, ref, None)
            require(row['actual_size']==ref.byte_length,'object-identity-mismatch')
        return self._immutable_read(check, 0)

    def _dependency_published(self, ref):
        def read():
            row=self.db.execute('SELECT published FROM objects WHERE digest=?',(ref.sha256,)).fetchone()
            require(row is not None,'object-unavailable')
            return bool(row['published'])
        return self._immutable_read(read, 0)

    def load(self, ref: ObjectRef, *, import_id=None) -> bytes:
        memo = self._operation_read_cache()
        if memo is not None and import_id is None:
            return memo.read(ref, self._load_guarded)
        return self._load_guarded(ref, import_id)

    def _put(self, ref, raw, *, published):
        verify_object(ref,raw)
        if ref.kind != 'body.chunk': decode_envelope(ref,raw)
        self.db.execute('INSERT OR IGNORE INTO objects VALUES(?,?,?,?,?,?)',
                        (ref.sha256,ref.kind,ref.version,ref.byte_length,raw,int(published)))
        row=self.db.execute('SELECT * FROM objects WHERE digest=?',(ref.sha256,)).fetchone()
        require(_row_ref(row)==ref and bytes(row['data'])==raw,'object-collision')
        if published and not row['published']:
            self.db.execute('UPDATE objects SET published=1 WHERE digest=?',(ref.sha256,))

    def _root(self):
        row=self.db.execute('SELECT o.* FROM current_root r JOIN objects o ON o.digest=r.digest WHERE r.singleton=1').fetchone()
        require(row is not None and row['published']==1,'root-unavailable')
        return self._decode_root(_row_ref(row), self._load)

    def _decode_root(self, ref, load):
        obj=decode_envelope(ref,load(ref))
        def check(p):
            require(set(p)=={'project','sequence','operation','links'} and p['project']==self.project and
                    type(p['sequence']) is int and p['sequence']>=0 and
                    p['links']['heads']==[0] and p['links']['operations']==[1] and
                    p['links']['previous']==([] if p['sequence']==0 else [2]),
                    'invalid-state-root')
            if p['sequence']==0: require(p['operation'] is None,'invalid-root-operation')
            else: _token(p['operation'])
        validate_schema(obj,kind='state.root',version=1,
                        fields={'heads':'integrity','operations':'integrity','previous':'provenance'},validate_payload=check)
        require(all(e.ref.kind in ('map.leaf','map.branch') and e.ref.version==1 for e in obj.edges[:2]),'invalid-root-map')
        if obj.payload['sequence']:
            require(obj.edges[2].ref.kind=='state.root' and obj.edges[2].ref.version==1,'invalid-previous-root')
        return Root(ref,obj.edges[0].ref,obj.edges[1].ref,obj.payload['sequence'])

    def root(self):
        view = _VALIDATIONS.get().get(self.identity)
        if view is not None: return view.root()
        with self._transaction(): return self._root()

    def workspace_verification_stamp(self):
        """Confirm authority state for the middle of a read-only observation."""
        with self._transaction():
            return self._root().ref, self._write_epoch, self.db.execute('PRAGMA data_version').fetchone()[0]

    def head(self, key):
        view = _VALIDATIONS.get().get(self.identity)
        if view is not None: return view.head(key)
        with self._transaction(): return map_get(self._root().heads,key,self._load)

    @contextmanager
    def read_snapshot(self):
        require(self.readonly, 'record-snapshot-readonly-required')
        with self._read_snapshot() as snapshot:
            yield snapshot

    @contextmanager
    def _read_snapshot(self, *, bounded=False):
        page = _active_page()
        if page is not None:
            page.flush()
        require(not self.db.in_transaction, 'record-snapshot-already-open')
        with self._transaction():
            snapshot = _RecordSnapshot(self, bounded=bounded)
            try:
                yield snapshot
            finally:
                snapshot.close()

    def has_active_imports(self):
        with self._transaction():
            return self.db.execute("SELECT 1 FROM imports WHERE state='active' LIMIT 1").fetchone() is not None

    def begin_import(self, import_id: str, owner: str):
        _token(import_id); _token(owner)
        with self._transaction(write=True):
            require(self.db.execute('SELECT 1 FROM imports WHERE id=?',(import_id,)).fetchone() is None,
                    'import-already-exists')
            self.db.execute('INSERT INTO imports VALUES(?,?,?)',(import_id,owner,'active'))

    @contextmanager
    def import_attempt(self, import_id: str, owner: str, *, can_abandon=lambda: True):
        """Close only this newly created attempt on a confirmed refusal.

        Not a historic cleanup API. Unknown storage outcomes and interruptions
        retain their active import. A caller may also withhold abandonment
        until its subprocess outcome is known. Chunks and claims are never reclaimed here.
        """
        _token(import_id);_token(owner)
        # Check operation identity and create together. A failed/replayed begin
        # is outside the handler and cannot abandon somebody else's import.
        with self._transaction(write=True):
            require(map_get(self._root().operations,import_id,self._load) is None and
                    self.db.execute('SELECT 1 FROM operations WHERE id=?',(import_id,)).fetchone() is None,
                    'operation-already-recorded')
            require(self.db.execute('SELECT 1 FROM imports WHERE id=?',(import_id,)).fetchone() is None,
                    'import-already-exists')
            self.db.execute('INSERT INTO imports VALUES(?,?,?)',(import_id,owner,'active'))
        try:
            yield
        except RecordError as exc:
            # Even a pre-publication engine refusal can report corruption or
            # replaced storage: never attempt another write to close it here.
            known=exc.code!='store-outcome-unknown' and not isinstance(exc,StorageError) and can_abandon()
            if known:
                try:
                    if self.operation_result(import_id) is not None:
                        exc.preparation_state='published'
                    else:
                        self._abandon_current_import(import_id,owner)
                except Exception as closing:
                    exc.preparation_state='unconfirmed'
                    exc.add_note('Preparation state not confirmed: '+type(closing).__name__)
            raise

    def _abandon_current_import(self,import_id,owner):
        # Private to the live context above; not a recovery command.
        with self._transaction(write=True):
            require(map_get(self._root().operations,import_id,self._load) is None and
                    self.db.execute('SELECT 1 FROM operations WHERE id=?',(import_id,)).fetchone() is None,
                    'import-outcome-already-published')
            changed=self.db.execute("UPDATE imports SET state='abandoned' WHERE id=? AND owner=? AND state='active'",
                                    (import_id,owner))
            require(changed.rowcount==1,'import-attempt-changed')

    def stage(self, import_id: str, objects: Iterable[tuple[ObjectRef,bytes]]):
        batch=[]; size=0
        for ref,raw in objects:
            require(len(batch)<BATCH_OBJECTS and ref.kind=='body.chunk' and ref.version==1,'invalid-staging-batch')
            size+=len(raw); require(size<=BATCH_BYTES,'staging-batch-limit')
            verify_object(ref,raw); batch.append((ref,raw))
        with self._transaction(write=True):
            row=self.db.execute('SELECT state FROM imports WHERE id=?',(import_id,)).fetchone()
            require(row is not None and row['state']=='active','import-not-active')
            for ref,raw in batch:
                self._put(ref,raw,published=False)
                self.db.execute('INSERT OR IGNORE INTO claims VALUES(?,?)',(import_id,ref.sha256))

    def commit_heads(self, *, operation: str, expected: dict[str,ObjectRef|None],
                     changes: dict[str,ObjectRef|None], objects: Iterable[tuple[ObjectRef,bytes]]=(),
                     import_id: str|None=None, validate: Callable[[Callable[[ObjectRef],bytes]],None],
                     descriptor_only=False, _rebind=False, _no_active_imports=False):
        """Rebase unrelated heads, but refuse any changed expected/shared dependency.

        The application supplies one fixed operation validator; it must validate
        its complete required closure before a user decision can be published.
        The supplied callable also exposes head()/root() against a fixed snapshot;
        those reads become final CAS conditions. No SQL or asynchronous validator
        reads are allowed by the application contract.
        """
        _token(operation)
        require(set(changes)<=set(expected),'missing-expected-head')
        require(not descriptor_only or import_id is None,'descriptor-only-cannot-import')
        incoming={}; size=0
        for ref,raw in objects:
            require(ref.kind!='body.chunk','chunks-require-staging')
            require(not descriptor_only or ref.kind!='body.complete','descriptor-only-cannot-import')
            verify_object(ref,raw); decode_envelope(ref,raw)
            require(ref not in incoming or incoming[ref]==raw,'object-collision')
            incoming[ref]=raw; size+=len(raw)
            require(size<=16*1024*1024,'publication-metadata-limit')
        def load(ref):
            if ref in incoming:
                return incoming[ref]
            # Only body chunks can carry staged import claims.
            return self.load(ref, import_id=import_id if ref.kind == 'body.chunk' else None)
        # Hash/semantic verification is paged before the short publication lock.
        # The final transaction rechecks the exact heads, generation, immutable
        # object identities and import claims. No body bytes are rewritten there.
        with self._transaction(): observed = self._root()
        view = ValidationView(observed, load, check_chunk=self._chunk_identity if descriptor_only else None)
        context = _VALIDATIONS.set({**_VALIDATIONS.get(), self.identity:view})
        try:
            memo = self._operation_read_cache()
            # Staged chunks and incoming descriptors have publication-local
            # visibility. A refused publication must not lend their proofs.
            reuse = nullcontext()
            if memo is not None or descriptor_only:
                published_proofs = None
                if memo is not None and not descriptor_only and import_id is None and not any(
                        ref.kind == 'body.complete' for ref in incoming):
                    published_proofs = memo.body_proofs
                reuse = view.reuse_immutable_objects(published_proofs=published_proofs)
            with reuse:
                validate(view)
        except RecordError as exc:
            # Validation precedes the publication transaction. Unknown storage
            # outcomes must never be reclassified, even through a read callback.
            if exc.code != "store-outcome-unknown":raise _refused(exc) from exc
            raise
        finally: _VALIDATIONS.reset(context)
        pending=[(ref,True) for ref in changes.values() if ref is not None]
        seen=set(); required=set(); metadata=0
        with self.immutable_reads():
            while pending:
                ref,mandatory=pending.pop()
                if mandatory:required.add(f'schema:{ref.kind}:{ref.version}')
                if ref in seen: continue
                seen.add(ref)
                require(len(seen)<=1_000_000,'publication-reference-limit')
                # Publication performs its own fresh reads and claim checks, outside
                # both the operation cache and the validator's mutable head view.
                if ref.kind=='body.chunk' and descriptor_only:
                    self._chunk_identity(ref)
                    continue
                raw=incoming[ref] if ref in incoming else self._load_guarded(ref, import_id)
                if ref.kind!='body.chunk':
                    published=ref not in incoming and self._dependency_published(ref)
                    metadata+=len(raw); require(metadata<=512*1024*1024,'publication-closure-limit')
                    if not published:
                        pending.extend((edge.ref,edge.role in ('decision','integrity')) for edge in decode_envelope(ref,raw).edges)
        require(required<=self.reader_capabilities and required<=self.writer_capabilities,'publication-capability-unavailable')
        with self._transaction(write=True,lifecycle=_rebind):
            if _rebind:
                row=self.db.execute('SELECT needs_rebind,quiescent,fence FROM generation').fetchone()
                require(row['needs_rebind']==1 and row['quiescent'] is None and row['fence'] is None,'instance-rebind-not-pending')
                self.write_check()
            if _no_active_imports:
                require(self.db.execute("SELECT 1 FROM imports WHERE state='active' LIMIT 1").fetchone() is None,
                        'identity-import-pending')
            old=self._root()
            require(not view.full_root_read or old.ref==observed.ref,'validation-root-conflict')
            for key,ref in view.reads.items():
                require(map_get(old.heads,key,self._load)==ref,'head-conflict')
            require(map_get(old.operations,operation,self._load) is None,'operation-already-recorded')
            for key,ref in expected.items():
                require(map_get(old.heads,key,self._load)==ref,'head-conflict')
            if import_id is not None:
                row=self.db.execute('SELECT state FROM imports WHERE id=?',(import_id,)).fetchone()
                require(row is not None and row['state']=='active','import-not-active')
            for ref in seen:
                if ref in incoming:
                    self._put(ref,incoming[ref],published=True)
                else:
                    row=self.db.execute('SELECT kind,version,size,digest,published FROM objects WHERE digest=?',
                                        (ref.sha256,)).fetchone()
                    require(row is not None and _row_ref(row)==ref,'object-unavailable')
                    require(row['published'] or (import_id is not None and self.db.execute(
                        'SELECT 1 FROM claims WHERE import_id=? AND digest=?',(import_id,ref.sha256)).fetchone()),
                        'object-unpublished')
                    if not row['published']:
                        self.db.execute('UPDATE objects SET published=1 WHERE digest=?',(ref.sha256,))
            self.db.executemany('INSERT OR IGNORE INTO requirements VALUES(?,?)',[(role,cap) for role in ('read','write') for cap in required])
            updated=map_update(old.heads,changes,self._load)
            for ref,raw in updated.objects:
                self._put(ref,raw,published=True)
                self._require_kind(ref)
            operations=map_update(old.operations,{operation:old.ref},self._load)
            for opref,opraw in operations.objects:
                self._put(opref,opraw,published=True)
                self._require_kind(opref)
            ref,raw=encode_envelope('state.root',1,
                dict(project=self.project,sequence=old.sequence+1,operation=operation,links={'heads':[0],'operations':[1],'previous':[2]}),
                (Edge('integrity',updated.root),Edge('integrity',operations.root),Edge('provenance',old.ref)))
            self._put(ref,raw,published=True)
            self.db.execute('UPDATE current_root SET digest=? WHERE singleton=1',(ref.sha256,))
            self.db.execute('INSERT INTO operations VALUES(?,?,?)',(operation,old.ref.sha256,ref.sha256))
            if import_id is not None:
                self.db.execute("UPDATE imports SET state='published' WHERE id=?",(import_id,))
                self.db.execute('DELETE FROM claims WHERE import_id=?',(import_id,))
            if _rebind:self.db.execute('UPDATE generation SET needs_rebind=0 WHERE singleton=1')
            result=Root(ref,updated.root,operations.root,old.sequence+1)
        return result

    def _require_kind(self,ref):
        cap=f'schema:{ref.kind}:{ref.version}'
        require(cap in self.reader_capabilities and cap in self.writer_capabilities,'publication-capability-unavailable')
        self.db.executemany('INSERT OR IGNORE INTO requirements VALUES(?,?)',[(role,cap) for role in ('read','write')])

    def _requirements(self):
        rows=self.db.execute('SELECT role,capability FROM requirements ORDER BY capability').fetchall()
        return {role:[row['capability'] for row in rows if row['role']==role] for role in ('read','write')}

    def requirements(self):
        with self._transaction():
            return self._requirements()

    def operation_result(self, operation: str) -> tuple[ObjectRef,ObjectRef] | None:
        """Confirm the projected completion against the captured root's lineage.

        Each immutable object is read under a short guarded transaction. Long
        history lookup has an explicit bound and is not the normal Work view.
        """
        _token(operation)
        with self._transaction():
            current=self._root()
            before=map_get(current.operations,operation,self._load)
            row=self.db.execute('SELECT * FROM operations WHERE id=?',(operation,)).fetchone()
            if before is None:
                require(row is None,'operation-index-mismatch')
                return None
            require(row is not None,'operation-index-unavailable')
            result=[]
            for column in ('before_root','after_root'):
                obj=self.db.execute('SELECT * FROM objects WHERE digest=?',(row[column],)).fetchone()
                require(obj is not None,'operation-root-unavailable')
                result.append(_row_ref(obj))
        require(result[0]==before,'operation-index-mismatch')
        parent=self._decode_root(before,self.load)
        after=self._decode_root(result[1],self.load)
        obj=decode_envelope(after.ref,self.load(after.ref))
        require(after.sequence==parent.sequence+1 and obj.payload['operation']==operation and
                obj.edges[2].ref==before and after.sequence<=current.sequence,'operation-index-mismatch')
        remaining=current.sequence-after.sequence
        require(remaining<=1_000_000,'operation-history-unavailable')
        cursor=current
        for _ in range(remaining):
            envelope=decode_envelope(cursor.ref,self.load(cursor.ref))
            previous=self._decode_root(envelope.edges[2].ref,self.load)
            require(previous.sequence==cursor.sequence-1,'invalid-root-lineage')
            cursor=previous
        require(cursor.ref==after.ref,'operation-index-mismatch')
        return tuple(result)

    @classmethod
    def recover_journal(cls, path, *, project, instance, generation, operation, active_check):
        """Lifecycle-only SQLite rollback; never expose a writable retired handle.

        The caller owns lifecycle exclusion and the exact persisted plan. SQLite
        may restore pages when first reading; no application SQL mutation occurs.
        """
        for value in (project,instance,generation,operation): _token(value)
        path=Path(path); identity=_identity(path)
        journal=Path(str(path)+'-journal')
        try:
            _identity(journal)
        except FileNotFoundError: pass
        lock=_process_lock(identity)
        require(lock.acquire(timeout=BUSY_SECONDS),'store-busy')
        db=None
        try:
            active_check()
            db=sqlite3.connect(path.as_uri()+'?mode=rw',uri=True,
                               timeout=BUSY_SECONDS,isolation_level=None)
            _settings(db)
            row=db.execute('SELECT project,instance,generation,fence FROM generation WHERE singleton=1').fetchone()
            require(row is not None and tuple(row[:3])==(project,instance,generation) and
                    row[3] in (None,operation),'store-generation-mismatch')
            require(_identity(path)==identity,'store-file-replaced')
            active_check()
        except sqlite3.Error as exc:
            raise _sql_error(exc,path,stage='recovery') from None
        finally:
            if db is not None: db.close()
            lock.release()

    def quiesce(self, operation: str, expected_root: ObjectRef,
                validate_effects: Callable[[Root],None]):
        _token(operation)
        observed=self.root()
        require(observed.ref==expected_root,'lifecycle-root-conflict')
        validate_effects(observed)
        with self._transaction(write=True,lifecycle=True):
            require(self._root().ref==expected_root,'lifecycle-root-conflict')
            row=self.db.execute('SELECT quiescent FROM generation WHERE singleton=1').fetchone()
            require(row['quiescent'] is None,'lifecycle-already-pending')
            self.db.execute('UPDATE generation SET quiescent=? WHERE singleton=1',(operation,))

    def cancel_quiescence(self, operation: str, expected_root: ObjectRef):
        _token(operation)
        with self._transaction(write=True,lifecycle=True):
            require(self._root().ref==expected_root,'lifecycle-root-conflict')
            row=self.db.execute('SELECT quiescent FROM generation WHERE singleton=1').fetchone()
            require(row['quiescent']==operation,'lifecycle-operation-mismatch')
            self.db.execute('UPDATE generation SET quiescent=NULL WHERE singleton=1')

    def retire(self, operation: str, expected_root: ObjectRef):
        _token(operation)
        with self._transaction(write=True,lifecycle=True,retiring=operation):
            require(self._root().ref==expected_root,'lifecycle-root-conflict')
            row=self.db.execute('SELECT quiescent FROM generation WHERE singleton=1').fetchone()
            require(row['quiescent']==operation,'lifecycle-operation-mismatch')
            self.db.execute('UPDATE generation SET fence=? WHERE singleton=1',(operation,))

    def needs_rebind(self):
        with self._transaction():return bool(self.db.execute('SELECT needs_rebind FROM generation').fetchone()[0])

    def lifecycle_state(self):
        with self._transaction():
            row=self.db.execute('SELECT fence,quiescent FROM generation WHERE singleton=1').fetchone()
            return dict(row)
