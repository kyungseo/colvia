"""Closed, payload-free storage vocabulary for official execution schema v2.

These validators inspect metadata, never recover live execution authority. They
must remain usable after expiry, detach, and loss of the external recovery store.
"""
import hashlib
import os
import re

from .errors import ContractError
from .jsonio import canonical_json_bytes

VERSION = 2
POLICY = 'payload-minimal-1'
REASONS = frozenset('input_shape caller_mismatch scope_mismatch order_mismatch content_rejected document_drift recovery_unavailable storage_failed spawn_failed worker_failed verifier_failed protocol_refused cancelled deadline closure_unconfirmed worker_budget_consumed diagnostic_limit internal_error'.split())
PHASES = frozenset('prepare callback_preflight recovery reservation spawn worker verification closure'.split())
VERIFIERS = ('DOC-LINKS', 'DOC-GFM', 'DOC-CLAIMS')
METHODS = frozenset(('initialize', 'config/read', 'account/read', 'model/list', 'thread/start', 'turn/start', 'turn/interrupt'))
CLOSED = frozenset(('completed', 'interrupted', 'revoked-before-launch', 'operator-resolved-unknown'))
AVAILABILITY = frozenset(('not_checked', 'not_required', 'present', 'missing', 'mismatch', 'orphan_candidate'))
EFFECTS = frozenset(('none', 'applied', 'unknown'))
MAX_INT = (1 << 63) - 1
EVENT_FIELDS = {
    'granted': 'grant scope_sha256 recovery_locator_sha256',
    'admission': 'pass account_type model_id effort policy_digest',
    'runtime-reserved': 'ordinal host_pid host_birth',
    'runtime-started': 'ordinal pid birth',
    'runtime-spawn-failed': 'ordinal reason reaped',
    'runtime-child': 'pid birth',
    'rpc-reserved': 'method',
    'bound': 'ordinal established',
    'recovery-ready': 'output_id recovery_ordinal original_identity original_sha256 byte_count',
    'callback-reserved': 'callback_id ordinal tool file_ids verifier_id expected_identity',
    'worker-spawn-intent': 'callback_id worker_ordinal role code_identity',
    'worker-started': 'worker_ordinal pid birth',
    'worker-spawn-failed': 'worker_ordinal reason reaped',
    'worker-result': 'worker_ordinal success effect before after verifier_id verifier_pass reason',
    'worker-closed': 'worker_ordinal returncode group_absent birth_absent',
    'callback-completed': 'callback_id success result_ref closure_ref failure_code',
    'callback-aborted-before-spawn': 'callback_id reason',
    'callback-refused': 'callback_id tool phase reason current_call_effect',
    'revoked': 'reason',
    'effect-unknown': 'reason callback_id',
    'diagnostic': 'source phase reason byte_count',
    'seal': 'result_identity completed_refs',
    'processes-closed': 'runtime_ref group_absent final_scan_confirmed children',
    'terminal': 'status stop_reason document_write_effect effect_refs closure_refs',
    'operator-resolved-unknown': 'grant journal_head previous_status documents process_absence recovery_availability action',
}


def need(condition, code):
    if not condition:
        raise ContractError('HV2-OFFICIAL-EXECUTION', code)


def exact(value, fields, code='v2-record-fields'):
    keys = fields.split() if isinstance(fields, str) else fields
    need(type(value) is dict and set(value) == set(keys), code)


def integer(value, minimum=0, maximum=MAX_INT):
    need(type(value) is int and minimum <= value <= maximum, 'v2-integer')


def boolean(value):
    need(type(value) is bool, 'v2-boolean')


def choice(value, values):
    need(type(value) is str and value in values, 'v2-enum')


def sha(value):
    need(type(value) is str and re.fullmatch(r'[0-9a-f]{64}', value) is not None, 'v2-digest')


def digest(value):
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def local_id(value, *, document=False):
    pattern = r'[A-Za-z0-9]{1,64}' if document else r'[A-Za-z0-9][A-Za-z0-9_-]{0,95}'
    need(type(value) is str and re.fullmatch(pattern, value) is not None, 'v2-local-id')


def store_id(value):
    need(type(value) is str and re.fullmatch(r'[0-9a-f]{32}', value) is not None, 'v2-store-id')


def path(value):
    # Historical paths are lexical metadata: no filesystem lookup/recovery scan.
    need(type(value) is str and 0 < len(value.encode('utf-8')) <= 4096 and
         value.startswith('/') and not value.startswith('//') and
         not any(c in value for c in ('\x00', '\r', '\n')) and os.path.normpath(value) == value,
         'v2-path')


def birth(value, *, nullable=False):
    if value is None and nullable:
        return
    need(type(value) is str and re.fullmatch(
        r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [ 0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-6][0-9] [0-9]{4}', value) is not None,
        'v2-process-birth')


def identity(value, *, nullable=False):
    if nullable and value is None:
        return
    exact(value, 'dev ino mode nlink size mtime_ns ctime_ns sha256', 'v2-document-identity')
    for key in ('dev', 'ino', 'mtime_ns', 'ctime_ns'):
        integer(value[key])
    integer(value['mode'], 0, 0o7777)
    integer(value['size'], 0, 131072)
    need(type(value['nlink']) is int and value['nlink'] == 1, 'v2-document-links')
    sha(value['sha256'])


def refs(value):
    need(type(value) is list and len(value) <= 16, 'v2-reference-list')
    for item in value:
        integer(item, 1, 8192)
    need(len(set(value)) == len(value) and value == sorted(value), 'v2-reference-order')


def grant_record(value, target=None, grant=None):
    exact(value, 'record_type schema_version grant policy_version target scope recovery_locator', 'v2-grant-fields')
    need(value['record_type'] == 'official-execution-grant' and
         type(value['schema_version']) is int and value['schema_version'] == VERSION and
         value['policy_version'] == POLICY, 'v2-grant-version')
    sha(value['grant']); path(value['target'])
    need((target is None or value['target'] == str(target)) and (grant is None or value['grant'] == grant), 'v2-grant-binding')
    scope = value['scope']
    exact(scope, 'work_id documents read_ids output_id limits installation resources recovery_store_id')
    local_id(scope['work_id']); store_id(scope['recovery_store_id'])
    docs, ids = scope['documents'], scope['read_ids']
    need(type(docs) is dict and 1 <= len(docs) <= 8 and type(ids) is list and 1 <= len(ids) <= 8, 'v2-document-count')
    for item in ids:
        local_id(item, document=True)
    local_id(scope['output_id'], document=True)
    need(len(set(ids)) == len(ids) and set(ids) == set(docs) and scope['output_id'] in ids, 'v2-document-set')
    paths, identities = set(), set()
    for key, item in docs.items():
        exact(item, 'path view original_identity')
        path(item['path']); identity(item['original_identity'])
        need(item['path'] not in paths, 'v2-document-path-alias'); paths.add(item['path'])
        original = item['original_identity']; inode = (original['dev'], original['ino'])
        need(inode not in identities, 'v2-document-identity-alias'); identities.add(inode)
        if key == scope['output_id']:
            exact(item['view'], 'kind ranges')
            need(item['view']['kind'] == 'replace-range', 'v2-output-view')
            ranges = item['view']['ranges']
            need(type(ranges) is list and len(ranges) == 1 and type(ranges[0]) is list and len(ranges[0]) == 2, 'v2-output-range')
            start, end = ranges[0]
            integer(start, 0, original['size']); integer(end, 0, original['size'])
            need(start < end, 'v2-output-range')
        else:
            need(item['view'] == {'kind': 'full'}, 'v2-reference-view')
    limits = scope['limits']
    exact(limits, 'seconds expires_wall_ns worker_limit')
    integer(limits['seconds'], 30, 600); integer(limits['expires_wall_ns'], 1)
    integer(limits['worker_limit'], 1, 5)
    need(limits['worker_limit'] in (1, 5), 'v2-worker-limit')
    exact(scope['installation'], 'release_digest binding_digest work_scope_digest')
    exact(scope['resources'], 'python_digest worker_digest parser_digest profile_digest app_server_digest')
    for item in (*scope['installation'].values(), *scope['resources'].values()):
        sha(item)
    locator = value['recovery_locator']
    exact(locator, 'store_id grant recovery_ordinal')
    store_id(locator['store_id']); sha(locator['grant']); integer(locator['recovery_ordinal'], 1, 1)
    need(locator['grant'] == value['grant'] and locator['store_id'] == scope['recovery_store_id'], 'v2-recovery-binding')
    return value


def event(kind, value):
    choice(kind, EVENT_FIELDS)
    exact(value, EVENT_FIELDS[kind], 'v2-event-fields')
    for key in ('ordinal', 'callback_id', 'worker_ordinal', 'recovery_ordinal'):
        if key in value and not (kind == 'effect-unknown' and key == 'callback_id' and value[key] is None):
            integer(value[key], 1, 8192)
    for key in ('pid', 'host_pid'):
        if key in value:
            integer(value[key], 2, (1 << 31) - 1)
    for key in ('birth', 'host_birth'):
        if key in value:
            birth(value[key], nullable=kind in ('runtime-started', 'worker-started'))
    for key in ('reason', 'stop_reason', 'failure_code'):
        if key in value and value[key] is not None:
            choice(value[key], REASONS)
        elif key in value:
            need(kind in ('worker-result', 'callback-completed', 'terminal'), 'v2-required-reason')
    for key in ('pass', 'reaped', 'established', 'success', 'group_absent', 'birth_absent', 'final_scan_confirmed', 'process_absence'):
        if key in value:
            boolean(value[key])
    if 'phase' in value:
        choice(value['phase'], PHASES)
    if 'byte_count' in value:
        integer(value['byte_count'])
    for key in ('grant', 'scope_sha256', 'recovery_locator_sha256', 'policy_digest', 'code_identity', 'original_sha256', 'journal_head'):
        if key in value:
            sha(value[key])
    for key in ('original_identity', 'result_identity'):
        if key in value:
            identity(value[key])
    for key in ('expected_identity', 'before', 'after'):
        if key in value:
            identity(value[key], nullable=True)
    for key in ('completed_refs', 'effect_refs', 'closure_refs'):
        if key in value:
            refs(value[key])
    if kind == 'admission':
        need(value['pass'] is True and value['account_type'] == 'chatgpt' and
             value['model_id'] == 'gpt-6.1-sol' and value['effort'] == 'low', 'v2-admission')
    elif kind == 'rpc-reserved':
        choice(value['method'], METHODS)
    elif kind == 'callback-reserved':
        choice(value['tool'], ('read', 'write', 'verify'))
        need(type(value['file_ids']) is list and len(value['file_ids']) <= 8, 'v2-file-ids')
        for item in value['file_ids']:
            local_id(item, document=True)
        if value['verifier_id'] is not None:
            choice(value['verifier_id'], VERIFIERS)
    elif kind == 'worker-spawn-intent':
        choice(value['role'], ('read', 'write', 'verify'))
    elif kind == 'worker-result':
        choice(value['effect'], EFFECTS)
        if value['verifier_id'] is not None:
            choice(value['verifier_id'], VERIFIERS)
        if value['verifier_pass'] is not None:
            boolean(value['verifier_pass'])
    elif kind == 'worker-closed':
        integer(value['returncode'], -255, 255)
    elif kind == 'callback-completed':
        if value['result_ref'] is not None:
            integer(value['result_ref'], 1, 8192)
        integer(value['closure_ref'], 1, 8192)
    elif kind == 'callback-refused':
        choice(value['tool'], ('read', 'write', 'verify', 'invalid'))
        need(value['current_call_effect'] == 'not_started', 'v2-refusal-effect')
    elif kind == 'diagnostic':
        choice(value['source'], ('runtime', 'worker', 'host'))
    elif kind == 'recovery-ready':
        local_id(value['output_id'], document=True)
    elif kind == 'processes-closed':
        integer(value['runtime_ref'], 1, 8192)
        need(type(value['children']) is list and len(value['children']) <= 256, 'v2-children')
        for child in value['children']:
            exact(child, 'pid birth absent')
            integer(child['pid'], 2, (1 << 31) - 1); birth(child['birth']); boolean(child['absent'])
    elif kind == 'terminal':
        choice(value['status'], ('completed', 'interrupted', 'revoked-before-launch', 'unknown'))
        choice(value['document_write_effect'], EFFECTS)
        need((value['stop_reason'] is None) == (value['status'] == 'completed'), 'v2-terminal-reason')
    elif kind == 'operator-resolved-unknown':
        choice(value['previous_status'], ('incomplete', 'unknown'))
        choice(value['recovery_availability'], AVAILABILITY)
        need(value['action'] == 'record-unknown-resolution' and value['process_absence'] is True, 'v2-resolution')
        need(type(value['documents']) is dict and 1 <= len(value['documents']) <= 8, 'v2-resolution-documents')
        for key, item in value['documents'].items():
            local_id(key, document=True); identity(item, nullable=True)
    return value


def project_grant(spec, grant):
    """Only this allowlist crosses from the immutable live spec into history."""
    need(digest(spec) == grant, 'v2-live-grant-binding')
    request, documents, work = spec['request'], spec['documents'], spec['work']
    scope = {
        'work_id': request['work_id'],
        'documents': {key: {'path': item['path'], 'view': item['view'],
                            'original_identity': spec['document_identities'][key]}
                      for key, item in documents['files'].items()},
        'read_ids': request['read_ids'], 'output_id': request['documents']['output'],
        'limits': {key: request[key] for key in ('seconds', 'expires_wall_ns', 'worker_limit')},
        'installation': {'release_digest': digest(work['inventory']), 'binding_digest': digest(work['product_ref']),
                         'work_scope_digest': digest(work['scope'])},
        'resources': {'python_digest': documents['python_sha256'], 'worker_digest': documents['worker_sha256'],
                      'parser_digest': documents['parser_sha256'], 'profile_digest': documents['profile_template_sha256'],
                      'app_server_digest': request['runtime']['sha256']['BIN']},
        'recovery_store_id': spec['host_control']['store_id'],
    }
    value = {'record_type': 'official-execution-grant', 'schema_version': VERSION, 'grant': grant,
             'policy_version': POLICY, 'target': spec['target'], 'scope': scope,
             'recovery_locator': {'store_id': spec['host_control']['store_id'], 'grant': grant, 'recovery_ordinal': 1}}
    grant_record(value)
    # Detach mutable references. The live spec remains in memory, never a log.
    import json
    return json.loads(canonical_json_bytes(value))
