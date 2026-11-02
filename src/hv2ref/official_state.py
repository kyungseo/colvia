"""Project-owned execution capsules, preserved by lifecycle and plain readers."""
from pathlib import Path
import hashlib
import json
import os
import re
import stat
import subprocess
from .errors import ContractError
from .jsonio import canonical_json_bytes, sync_directory

WINDOW = 'official-execution-2'
MAX_CAPSULE_FILES = 64
MAX_CAPSULE_BYTES = 64 * 1024 * 1024
HISTORY_FILES = 4096
HISTORY_BYTES = 128 * 1024 * 1024
TERMINAL = frozenset({'completed', 'interrupted', 'revoked-before-launch', 'operator-resolved-unknown'})

def need(condition, code):
    if not condition:
        raise ContractError('HV2-OFFICIAL-EXECUTION', code)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(value):
    return canonical_json_bytes(value)

def regular(path, limit=16 * 1024 * 1024):
    path = Path(path)
    need(path.is_absolute() and path.resolve(strict=True) == path, 'path-alias')
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= limit, 'record-file-kind-size')
    raw = path.read_bytes()
    after = path.lstat()
    need((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
         (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), 'record-changed')
    return raw

def load(path):
    from .jsonio import decode_json_bytes
    return decode_json_bytes(regular(path), require_canonical=True)

def directory(path, *, create=False):
    path = Path(path)
    need(path.is_absolute() and path.resolve(strict=False) == path, 'directory-alias')
    if create:
        path.mkdir(mode=0o700)
        sync_directory(path.parent)
    observed = path.lstat()
    need(stat.S_ISDIR(observed.st_mode) and observed.st_uid == os.getuid(), 'directory-kind-owner')
    for part in path.parents:
        need(not part.is_symlink(), 'directory-ancestor-alias')
    return path

def publish(path, value):
    path = Path(path)
    raw = canonical(value)
    need(len(raw) <= (16 * 1024 * 1024 if path.name == 'termination.json' else 2 * 1024 * 1024), 'published-record-size')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    sync_directory(path.parent)
    need(regular(path) == raw, 'publication-drift')

def rename_exclusive(source, destination):
    import ctypes
    native = ctypes.CDLL('/usr/lib/libSystem.B.dylib', use_errno=True)
    rename = native.renameatx_np
    rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    rename.restype = ctypes.c_int
    if rename(-2, os.fsencode(source), -2, os.fsencode(destination), 0x4) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))
    sync_directory(Path(source).parent)
    sync_directory(Path(destination).parent)

def publish_cancel(target, path, value):
    import uuid
    locks = directory(Path(target) / '.hrn/locks')
    staged = locks / ('cancel-' + uuid.uuid4().hex + '.json')
    try:
        publish(staged, value)
        try:
            rename_exclusive(staged, path)
        except FileExistsError:
            need(load(path) == value, 'cancel-request-differs')
    finally:
        if os.path.lexists(staged):
            staged.unlink(); sync_directory(locks)

def publish_receipt(target, path, value):
    """Keep incomplete receipt bytes outside the readable capsule."""
    import uuid
    locks = directory(Path(target) / '.hrn/locks')
    staged = locks / ('receipt-' + uuid.uuid4().hex + '.json')
    try:
        publish(staged, value)
        rename_exclusive(staged, path)
    finally:
        if os.path.lexists(staged):
            staged.unlink(); sync_directory(locks)

def require_capacity(target):
    values = capsules(target)
    need(len(values) < 256, 'execution-history-capacity')
    files = execution_truth(target)
    size = sum((Path(target) / '.hrn' / item['path']).stat().st_size for item in files)
    need(len(files) + MAX_CAPSULE_FILES <= HISTORY_FILES and size + MAX_CAPSULE_BYTES <= HISTORY_BYTES,
         'execution-history-capacity')

def capsule_path(target, grant):
    need(type(grant) is str and re.fullmatch('[a-f0-9]{64}', grant), 'grant-id')
    return Path(target) / '.hrn/executions' / grant

def process_birth(pid):
    need(type(pid) is int and pid > 1, 'process-id')
    # Stable UTC formatting independent of caller locale and host time zone.
    result = subprocess.run(['/bin/ps', '-p', str(pid), '-o', 'lstart='], env={'LC_ALL': 'C', 'TZ': 'UTC0'},
                            capture_output=True, text=True, timeout=3)
    observed = result.stdout.strip()
    need(not result.stderr and ((result.returncode == 0 and bool(observed)) or
                                (result.returncode == 1 and not observed)), 'process-observation-unavailable')
    if observed:
        from .official_schema import birth
        birth(observed)
    return observed

def group_absent(pid):
    try:
        os.killpg(pid, 0)
        return False
    except ProcessLookupError:
        return True
    except PermissionError:
        return False

def read_capsule(target, grant):
    """Read after expiry; never reconstruct authority from a mutable checkpoint."""
    from .official_documents import EffectJournal, observe_journal, journal_identity, require
    root = directory(capsule_path(target, grant))
    value = load(root / 'grant.json')
    need(type(value) is dict and type(value.get('schema_version')) is int, 'grant-record-version')
    if value['schema_version'] == 2:
        from .official_v2 import read_capsule as read_v2
        return read_v2(target, grant, root, value)
    need(set(value) == {'record_type', 'schema_version', 'grant', 'spec'} and
         value['record_type'] == 'official-execution-grant' and value['schema_version'] == 1 and
         value['grant'] == grant == digest(canonical(value['spec'])), 'grant-record')
    need(value['spec']['target'] == str(Path(target)), 'grant-target')
    journal_path = root / 'journal.jsonl'
    rows, journal_mode, observed_identity = observe_journal(journal_path)
    need(rows and rows[0]['kind'] == 'granted' and rows[0]['value'] == {'grant': grant}, 'grant-journal')
    allowed = {'granted', 'runtime-reserved', 'runtime-started', 'runtime-spawn-failed', 'bound', 'callback-reserved',
               'worker-result', 'worker-reserved', 'runtime-child', 'rpc-reserved', 'callback-completed', 'revoked', 'refused', 'effect-unknown',
               'seal', 'processes-closed', 'terminal', 'operator-resolved-unknown'}
    pending = None; completed = 0; seen = set(); terminal = None; sealed = False
    revoked = False; runtime_reserved = False; runtime_started = None; spawn_failed = False; closed = None
    children = []; rpc_methods = set(); workers = 0
    for row in rows[1:]:
        kind, item = row['kind'], row['value']
        need(kind in allowed and kind != 'granted', 'unknown-journal-event')
        need(terminal is None or kind == 'operator-resolved-unknown', 'event-after-terminal')
        if kind == 'runtime-reserved':
            need(not runtime_reserved, 'runtime-reused'); runtime_reserved = True
        elif kind == 'runtime-started':
            need(runtime_reserved and runtime_started is None and not spawn_failed and
                 set(item) == {'pid','birth'} and type(item['pid']) is int and item['pid'] > 1 and
                 (item['birth'] is None or type(item['birth']) is str and bool(item['birth'])), 'runtime-start-order'); runtime_started = item
        elif kind == 'runtime-spawn-failed':
            need(runtime_reserved and runtime_started is None and not spawn_failed and set(item) == {'error_type'}, 'spawn-failure-order')
            spawn_failed = True
        elif kind == 'runtime-child':
            need(runtime_started is not None and type(item['pid']) is int and item['pid'] > 1 and
                 type(item['birth']) is str and bool(item['birth']), 'child-identity')
            children.append(item)
        elif kind == 'rpc-reserved':
            method = item['method']
            need(runtime_started is not None and method in ('account/read','model/list','thread/start','turn/start','turn/interrupt') and method not in rpc_methods, 'rpc-reservation')
            rpc_methods.add(method)
        elif kind == 'worker-reserved':
            need(pending == item['callId'] and item['ordinal'] == workers + 1 and workers < value['spec']['request']['worker_limit'], 'worker-reservation')
            workers += 1
        elif kind == 'callback-reserved':
            need(not revoked and not sealed and pending is None and item['callId'] not in seen, 'callback-reservation-order')
            pending = item['callId']; seen.add(pending)
        elif kind == 'callback-completed':
            need(pending == item['callId'], 'callback-completion-order'); pending = None; completed += 1
        elif kind in ('revoked', 'refused', 'effect-unknown'):
            revoked = True
        elif kind == 'seal':
            need(not revoked and not sealed and pending is None and completed == 5, 'seal-order'); sealed = True
        elif kind == 'processes-closed':
            need(runtime_started is not None and item.get('observed_tree_absent') is True, 'process-close-evidence')
            closed = item
        elif kind == 'terminal':
            need(item['status'] in TERMINAL | {'unknown'}, 'terminal-value')
            if item['status'] in TERMINAL:
                need(not runtime_reserved or spawn_failed or closed is not None, 'terminal-before-process-close')
                need(pending is None, 'terminal-pending-effect')
                need(item['status'] != 'completed' or sealed, 'terminal-unsealed')
            terminal = item['status']
        elif kind == 'operator-resolved-unknown':
            need(terminal in (None, 'unknown') and set(item) == {'grant','journal_head','status','documents','process_absence','action'} and
                 item['grant'] == grant and item['journal_head'] == row['previous'] and item['process_absence'] is True and
                 item['action'] == 'record-unknown-resolution' and item['status'] == (terminal or 'incomplete') and
                 type(item['documents']) is dict and set(item['documents']) == set(value['spec']['documents']['files']), 'resolution-state')
            terminal = 'operator-resolved-unknown'
    journal = None
    if terminal in TERMINAL:
        need(journal_mode in (0o600, 0o644), 'closed-journal-mode')
    else:
        # A historical 0644 observation never becomes live control authority.
        require(not journal_mode & 0o077, 'aliased or nonprivate control file')
        journal = EffectJournal(journal_path)
        require(journal.rows == rows and journal_identity(journal_path.lstat()) == observed_identity,
                'journal-observation-drift')
    marker = None
    if os.path.lexists(root / 'cancel.json'):
        marker = load(root / 'cancel.json')
        need(set(marker) == {'grant', 'reason'} and marker['grant'] == grant and
             type(marker['reason']) is str and 0 < len(marker['reason']) <= 512, 'cancel-marker')
    return {'grant': grant, 'spec': value['spec'], 'root': root, 'journal': journal,
            'rows': rows, 'head': rows[-1]['sha256'], 'completed': completed, 'pending': pending,
            'revoked': revoked, 'sealed': sealed, 'status': terminal or 'incomplete',
            'runtime_reserved': runtime_reserved, 'runtime_started': runtime_started, 'spawn_failed': spawn_failed,
            'processes_closed': closed, 'children': children, 'workers': workers, 'cancel_requested': marker is not None}

def capsules(target):
    root = Path(target) / '.hrn/executions'
    if not os.path.lexists(root):
        return []
    directory(root)
    members = list(root.iterdir())
    need(len(members) <= 256, 'execution-capsule-limit')
    return [read_capsule(target, p.name) for p in sorted(members)]

def require_no_open(target):
    need(all(c['status'] in TERMINAL for c in capsules(target)), 'unresolved-execution-blocks-operation')

def execution_truth(target, *, require_closed=True):
    """Typed capsule check then exact regular-byte inventory; detach preserves it."""
    values = capsules(target)
    if require_closed:
        need(all(c['status'] in TERMINAL for c in values), 'unresolved-execution-blocks-lifecycle')
    root = Path(target) / '.hrn'
    result = []; total = 0
    for capsule in values:
        for p in sorted(capsule['root'].rglob('*')):
            if p.is_dir() and not p.is_symlink():
                directory(p); continue
            raw = regular(p); total += len(raw)
            need(total <= HISTORY_BYTES and len(result) < HISTORY_FILES, 'execution-evidence-limit')
            result.append({'path': p.relative_to(root).as_posix(), 'sha256': digest(raw)})
    return result

def public_status(value):
    result = {key: value[key] for key in ('grant', 'head', 'status', 'completed', 'pending', 'revoked', 'sealed', 'cancel_requested')}
    if value.get('schema_version') == 2:
        result.update(schema_version=2, document_write_effect=value['document_write_effect'],
                      recovery_availability='not_checked', transient_presence='not_checked',
                      cleanup_marker_presence='not_checked')
    return result

def cancel(target, grant, reason):
    value = read_capsule(target, grant)
    need(value['status'] not in TERMINAL, 'execution-already-terminal')
    if value.get('schema_version') == 2:
        from .official_schema import choice, REASONS
        choice(reason, REASONS)
    else:
        need(type(reason) is str and 0 < len(reason) <= 512, 'cancel-reason')
    marker = {'grant': grant, 'reason': reason}
    path = value['root'] / 'cancel.json'
    if os.path.lexists(path):
        need(load(path) == marker, 'cancel-request-differs')
    else:
        publish_cancel(target, path, marker)
    return {'grant': grant, 'cancel_requested': True, 'effects_stopped': False,
            'meaning': 'request recorded; already admitted effects may finish; inspect terminal status'}

def resolution_preview(target, grant, *, host_control_root=None):
    from .official_documents import file_record
    value = read_capsule(target, grant)
    if value.get('schema_version') == 2:
        from .official_v2 import resolution_preview as preview_v2
        return preview_v2(value, host_control_root=host_control_root)
    need(host_control_root is None, 'v1-external-recovery-not-supported')
    need(value['status'] not in TERMINAL, 'resolution-requires-unresolved-state')
    process = value['runtime_started']
    if value['runtime_reserved'] and not value['spawn_failed']:
        need(process is not None, 'process-identity-unavailable-preserve')
        need((process['birth'] is not None or value['processes_closed'] is not None) and
             process_birth(process['pid']) != process['birth'] and group_absent(process['pid']), 'runtime-still-present-or-unknown')
        for child in value['children']:
            # Legacy birth strings can be localized. A present PID is ambiguous
            # even after reuse; representation differences cannot prove absence.
            need(not process_birth(child['pid']), 'observed-child-present')
    # A Host crash can leave a document worker alive independently of App Server.
    for slot in sorted((value['root'] / 'workers').glob('worker-*')):
        if (slot / 'worker-admission.json').exists():
            if not (slot / 'process.json').exists():
                failure = json.loads(regular(slot / 'failure.json')) if (slot / 'failure.json').exists() else {}
                need((failure.get('worker_started') is False and failure.get('spawn_failed_confirmed') is True) or
                     (failure.get('worker_started') is True and failure.get('process_group_absent') is True),
                     'worker-spawn-identity-unavailable')
                continue
            worker = json.loads(regular(slot / 'process.json'))
            need(type(worker.get('birth')) is str and bool(worker['birth']) and
                 process_birth(worker['pid']) != worker['birth'] and group_absent(worker['pid']), 'worker-present-or-unconfirmed')
    observation = {key: file_record(item['path'], limit=131072)[0]
                   for key, item in value['spec']['documents']['files'].items()}
    result = {'grant': grant, 'journal_head': value['head'], 'status': value['status'],
              'documents': observation, 'process_absence': True, 'action': 'record-unknown-resolution'}
    return {'observation': result, 'confirm_token': digest(canonical(result))}

def resolve(target, grant, confirm, *, host_control_root=None):
    from .workspace import writer_guard
    with writer_guard(Path(target), purpose='official-resolution'):
        observed = resolution_preview(target, grant, host_control_root=host_control_root)
        need(confirm == observed['confirm_token'], 'stale-resolution-confirmation')
        value = read_capsule(target, grant)
        value['journal'].append('operator-resolved-unknown', observed['observation'])
        return public_status(read_capsule(target, grant))
