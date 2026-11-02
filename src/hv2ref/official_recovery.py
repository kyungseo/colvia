"""Explicit private recovery storage, outside capsules and runtime read scopes.

No discovery by locator, no fallback root, and no replay or automatic original
cleanup. Status inspection never calls this module without an explicit root.
"""
from pathlib import Path
import hashlib
import os
import stat

from . import official_schema as schema
from .jsonio import canonical_json_bytes, decode_json_bytes, sync_directory

need = schema.need
MARKER = 'store.json'
MANIFEST_FIELDS = 'schema_version store_id grant recovery_ordinal original_identity original_sha256 original_mode byte_count'


def private_directory(path):
    path = Path(path)
    need(path.is_absolute() and path.resolve(strict=True) == path and str(path) == os.path.normpath(str(path)),
         'recovery-directory-alias')
    info = path.lstat()
    need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) == 0o700,
         'recovery-directory-private')
    return path


def read_private(path, limit):
    path = Path(path)
    need(path.resolve(strict=True) == path, 'recovery-file-alias')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_uid == os.getuid() and
             stat.S_IMODE(before.st_mode) == 0o600 and before.st_size <= limit, 'recovery-file-private')
        raw = stream.read(limit + 1)
        after = os.fstat(stream.fileno()); observed = path.lstat()
        key = lambda i: (i.st_dev, i.st_ino, i.st_mode, i.st_uid, i.st_nlink, i.st_size, i.st_mtime_ns, i.st_ctime_ns)
        need(key(before) == key(after) == key(observed) and len(raw) <= limit, 'recovery-file-drift')
    return raw


def root_record(path, *, target=None, worker_root=None, runtime_root=None, output=None):
    """Check an operator-provisioned root and marker; create neither."""
    root = private_directory(path)
    for ancestor in (root, *root.parents):
        need(ancestor.name != '.git' and not os.path.lexists(ancestor / '.git') and
             not ((ancestor / 'HEAD').is_file() and (ancestor / 'objects').is_dir() and (ancestor / 'refs').is_dir()),
             'recovery-inside-git')
    for protected in (target, worker_root, runtime_root):
        if protected is not None:
            p = Path(protected)
            need(not (root == p or root in p.parents or p in root.parents), 'recovery-root-overlap')
    if output is not None:
        parent = Path(output).parent
        need(parent.resolve(strict=True) == parent and root.stat().st_dev == parent.stat().st_dev,
             'recovery-output-device')
    raw = read_private(root / MARKER, 4096)
    marker = decode_json_bytes(raw, require_canonical=True)
    schema.exact(marker, 'schema_version store_id')
    need(type(marker['schema_version']) is int and marker['schema_version'] == 1, 'recovery-marker-version')
    schema.store_id(marker['store_id'])
    info = root.lstat()
    return {'path': str(root), 'store_id': marker['store_id'], 'dev': info.st_dev,
            'ino': info.st_ino, 'uid': info.st_uid, 'mode': stat.S_IMODE(info.st_mode)}


def document_observation(path, *, absent=False):
    """Observe the full local identity used by v2, without retaining body text."""
    path = Path(path)
    if absent and not os.path.lexists(path):
        need(path.is_absolute() and path.parent.resolve(strict=True) == path.parent, 'document-parent-alias')
        return None, None
    need(path.is_absolute() and path.resolve(strict=True) == path, 'document-observation-alias')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= 131072, 'document-observation-kind-size')
        raw = stream.read(131073)
        key = lambda i: (i.st_dev, i.st_ino, i.st_mode, i.st_nlink, i.st_size, i.st_mtime_ns, i.st_ctime_ns)
        need(len(raw) <= 131072 and key(before) == key(os.fstat(stream.fileno())) == key(path.lstat()), 'document-observation-drift')
    identity = {'dev': before.st_dev, 'ino': before.st_ino, 'mode': stat.S_IMODE(before.st_mode),
                'nlink': before.st_nlink, 'size': before.st_size, 'mtime_ns': before.st_mtime_ns,
                'ctime_ns': before.st_ctime_ns, 'sha256': hashlib.sha256(raw).hexdigest()}
    schema.identity(identity)
    return identity, raw


def manifest_record(value, locator, original):
    schema.exact(value, MANIFEST_FIELDS)
    need(type(value['schema_version']) is int and value['schema_version'] == 1 and
         all(value[k] == locator[k] for k in ('store_id', 'grant', 'recovery_ordinal')) and
         value['original_identity'] == original and value['original_sha256'] == original['sha256'] and
         type(value['original_mode']) is int and value['original_mode'] == original['mode'] and
         type(value['byte_count']) is int and value['byte_count'] == original['size'], 'recovery-manifest-binding')
    schema.identity(value['original_identity'])
    return value


def inspect(value, root):
    """Availability is diagnostic and cannot alter historical status/effect."""
    try:
        observed = root_record(root)
        locator = value['recovery_locator']
        need(observed['store_id'] == locator['store_id'], 'recovery-store-mismatch')
        base = Path(root) / 'recovery'
        grant_root = base / locator['grant']
        ready = value['history'].ready
        if not os.path.lexists(base):
            return 'not_required' if ready is None else 'missing'
        private_directory(base)
        if not os.path.lexists(grant_root):
            return 'not_required' if ready is None else 'missing'
        private_directory(grant_root)
        members = list(grant_root.iterdir())
        if ready is None:
            return 'orphan_candidate' if members else 'not_required'
        ordinal = str(locator['recovery_ordinal'])
        if not members:
            return 'missing'
        need({p.name for p in members} == {ordinal}, 'recovery-object-set')
        object_root = private_directory(grant_root / ordinal)
        names = {p.name for p in object_root.iterdir()}
        if not names:
            return 'missing'
        need(names <= {'manifest.json', 'original.bin'}, 'recovery-object-files')
        if names != {'manifest.json', 'original.bin'}:
            return 'missing' if 'original.bin' not in names else 'mismatch'
        manifest = decode_json_bytes(read_private(object_root / 'manifest.json', 8192), require_canonical=True)
        expected = ready['value']['original_identity']
        manifest_record(manifest, locator, expected)
        raw = read_private(object_root / 'original.bin', 131072)
        need(len(raw) == manifest['byte_count'] and hashlib.sha256(raw).hexdigest() == manifest['original_sha256'],
             'recovery-original-mismatch')
        return 'present'
    except (OSError, ValueError, schema.ContractError):
        return 'mismatch'


def inspect_transient(value, root):
    """Explicit-root, read-only presence diagnostics; never grant cleanup authority."""
    try:
        observed = root_record(root)
        locator = value['recovery_locator']
        need(observed['store_id'] == locator['store_id'], 'transient-store-mismatch')
        container = Path(root) / 'transient'
        base = container / locator['grant']
        if not os.path.lexists(container):
            return {'transient_presence': 'absent', 'cleanup_marker_presence': 'absent'}
        private_directory(container)
        if not os.path.lexists(base):
            return {'transient_presence': 'absent', 'cleanup_marker_presence': 'absent'}
        private_directory(base)
        marker = base / 'cleanup.json'
        present = os.path.lexists(marker)
        if present:
            read_private(marker, 8192)
        return {'transient_presence': 'present', 'cleanup_marker_presence': 'present' if present else 'absent'}
    except (OSError, ValueError, schema.ContractError):
        return {'transient_presence': 'unavailable', 'cleanup_marker_presence': 'unavailable'}


def publish_private(path, raw):
    """Exclusive durable publication. Failed partials remain for investigation."""
    path = Path(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    sync_directory(path.parent)
    need(read_private(path, max(len(raw), 1)) == raw, 'recovery-publication-drift')


def create_private(path):
    path = Path(path)
    path.mkdir(mode=0o700)
    sync_directory(path.parent)
    return private_directory(path)


def child_container(parent, name):
    parent = private_directory(parent)
    path = parent / name
    if not os.path.lexists(path):
        create_private(path)
    return private_directory(path)


def save_original(spec, grant, original_identity):
    """After accepted write preflight, before reservation and spawn intent."""
    recorded = spec['host_control']
    output = spec['request']['documents']['output']
    path = spec['documents']['files'][output]['path']
    observed = root_record(recorded['path'], target=spec['target'], worker_root=spec['request']['worker_root'],
                           runtime_root=spec['runtime_root'], output=path)
    need(observed == recorded, 'recovery-root-drift')
    identity, raw = document_observation(path)
    need(identity == original_identity, 'recovery-document-drift')
    base = child_container(recorded['path'], 'recovery')
    grant_root = create_private(base / grant)
    object_root = create_private(grant_root / '1')
    locator = {'store_id': recorded['store_id'], 'grant': grant, 'recovery_ordinal': 1}
    manifest = dict(schema_version=1, **locator, original_identity=identity,
                    original_sha256=identity['sha256'], original_mode=identity['mode'], byte_count=len(raw))
    publish_private(object_root / 'original.bin', raw)
    publish_private(object_root / 'manifest.json', canonical_json_bytes(manifest))
    current, _ = document_observation(path)
    need(current == identity and root_record(recorded['path'], output=path) == recorded, 'recovery-after-publication-drift')
    return {'output_id': output, 'recovery_ordinal': 1, 'original_identity': identity,
            'original_sha256': identity['sha256'], 'byte_count': len(raw)}


def cleanup_transient(value, recorded_root):
    """Only automatic closed executions qualify; originals are never removed."""
    need(value['schema_version'] == 2 and value['status'] in ('completed', 'interrupted', 'revoked-before-launch'),
         'transient-cleanup-requires-automatic-closure')
    root = Path(recorded_root['path']); base = root / 'transient' / value['grant']
    pending = []
    try:
        need(root_record(root) == recorded_root, 'cleanup-root-drift')
        if not os.path.lexists(root / 'transient'): return False
        private_directory(root / 'transient')
        if not os.path.lexists(base): return False
        private_directory(base)
        members = sorted(base.iterdir())
        need(len(members) <= 6, 'cleanup-member-count')
        for slot in members:
            need(slot.name.startswith('worker-') and len(slot.name) == 10 and slot.name[7:].isdigit(), 'cleanup-slot-name')
            ordinal = int(slot.name[7:]); schema.integer(ordinal, 1, 5); pending.append(ordinal)
        for slot in members:
            private_directory(slot)
            files = list(slot.iterdir())
            need({p.name for p in files} <= {'spec.json', 'worker.sb'}, 'cleanup-unexpected-file-preserve')
            # Validate the entire slot before deleting any of its content.
            for member in files: read_private(member, 1048576)
            for member in files: member.unlink()
            sync_directory(slot); slot.rmdir(); sync_directory(base)
            pending.remove(int(slot.name[7:]))
        base.rmdir(); sync_directory(base.parent)
        return False
    except (OSError, ValueError, schema.ContractError):
        # This marker is diagnostic only. Failure to store it still reports pending.
        try:
            private_directory(base)
            marker = {'schema_version': 1, 'grant': value['grant'], 'pending_ordinals': sorted(set(pending)), 'reason': 'storage_failed'}
            publish_private(base / 'cleanup.json', canonical_json_bytes(marker))
        except (OSError, ValueError, schema.ContractError):
            pass
        return True
