"""Metadata-only causal vocabulary for first-format bounded execution.

These validators inspect metadata, never recover live execution authority. They
must remain usable after expiry, detach, and loss of the external recovery store.
"""
import hashlib
import os
import re

from ..codec import RecordError,canonical_bytes as canonical_json_bytes

VERSION = 1
POLICY = 'bounded-document-1'
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
    'admission': 'pass capability_digest policy_digest',
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
        raise RecordError(code)


def exact(value, fields, code='execution-record-fields'):
    keys = fields.split() if isinstance(fields, str) else fields
    need(type(value) is dict and set(value) == set(keys), code)


def integer(value, minimum=0, maximum=MAX_INT):
    need(type(value) is int and minimum <= value <= maximum, 'execution-integer')


def boolean(value):
    need(type(value) is bool, 'execution-boolean')


def choice(value, values):
    need(type(value) is str and value in values, 'execution-enum')


def sha(value):
    need(type(value) is str and re.fullmatch(r'[0-9a-f]{64}', value) is not None, 'execution-digest')


def digest(value):
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def local_id(value, *, document=False):
    pattern = r'[A-Za-z0-9]{1,64}' if document else r'[A-Za-z0-9][A-Za-z0-9_-]{0,95}'
    need(type(value) is str and re.fullmatch(pattern, value) is not None, 'execution-local-id')


def store_id(value):
    need(type(value) is str and re.fullmatch(r'[0-9a-f]{32}', value) is not None, 'execution-store-id')


def path(value):
    # Historical paths are lexical metadata: no filesystem lookup/recovery scan.
    need(type(value) is str and 0 < len(value.encode('utf-8')) <= 4096 and
         value.startswith('/') and not value.startswith('//') and
         not any(c in value for c in ('\x00', '\r', '\n')) and os.path.normpath(value) == value,
         'execution-path')


def birth(value, *, nullable=False):
    if value is None and nullable:
        return
    need(type(value) is str and re.fullmatch(
        r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [ 0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-6][0-9] [0-9]{4}', value) is not None,
        'execution-process-birth')


def identity(value, *, nullable=False):
    if nullable and value is None:
        return
    exact(value, 'dev ino mode nlink size mtime_ns ctime_ns sha256', 'execution-document-identity')
    for key in ('dev', 'ino', 'mtime_ns', 'ctime_ns'):
        integer(value[key])
    integer(value['mode'], 0, 0o7777)
    integer(value['size'], 0, 131072)
    need(type(value['nlink']) is int and value['nlink'] == 1, 'execution-document-links')
    sha(value['sha256'])


def refs(value):
    need(type(value) is list and len(value) <= 16, 'execution-reference-list')
    for item in value:
        integer(item, 1, 8192)
    need(len(set(value)) == len(value) and value == sorted(value), 'execution-reference-order')


def grant_record(value, target=None, grant=None):
    exact(value, 'record_type schema_version grant policy_version target scope recovery_locator capability', 'execution-grant-fields')
    need(value['record_type'] == 'execution-contract' and
         type(value['schema_version']) is int and value['schema_version'] == VERSION and
         value['policy_version'] == POLICY, 'execution-grant-version')
    sha(value['grant']); path(value['target'])
    need((target is None or value['target'] == str(target)) and (grant is None or value['grant'] == grant), 'execution-grant-binding')
    scope = value['scope']
    exact(scope, 'work_id documents read_ids output_id limits resources recovery_store_id')
    local_id(scope['work_id']); store_id(scope['recovery_store_id'])
    docs, ids = scope['documents'], scope['read_ids']
    need(type(docs) is dict and 1 <= len(docs) <= 8 and type(ids) is list and 1 <= len(ids) <= 8, 'execution-document-count')
    for item in ids:
        local_id(item, document=True)
    local_id(scope['output_id'], document=True)
    need(len(set(ids)) == len(ids) and set(ids) == set(docs) and scope['output_id'] in ids, 'execution-document-set')
    paths, identities = set(), set()
    for key, item in docs.items():
        exact(item, 'path view original_identity')
        path(item['path']); identity(item['original_identity'])
        need(item['path'] not in paths, 'execution-document-path-alias'); paths.add(item['path'])
        original = item['original_identity']; inode = (original['dev'], original['ino'])
        need(inode not in identities, 'execution-document-identity-alias'); identities.add(inode)
        if key == scope['output_id']:
            exact(item['view'], 'kind ranges')
            need(item['view']['kind'] == 'replace-range', 'execution-output-view')
            ranges = item['view']['ranges']
            need(type(ranges) is list and len(ranges) == 1 and type(ranges[0]) is list and len(ranges[0]) == 2, 'execution-output-range')
            start, end = ranges[0]
            integer(start, 0, original['size']); integer(end, 0, original['size'])
            need(start < end, 'execution-output-range')
        else:
            need(item['view'] == {'kind': 'full'}, 'execution-reference-view')
    limits = scope['limits']
    exact(limits, 'seconds expires_wall_ns worker_limit')
    integer(limits['seconds'], 30, 600); integer(limits['expires_wall_ns'], 1)
    integer(limits['worker_limit'], 1, 5)
    need(limits['worker_limit'] in (1, 5), 'execution-worker-limit')
    exact(scope['resources'], 'python_digest worker_digest parser_digest profile_digest runtime_digest')
    for item in scope['resources'].values():
        sha(item)
    capability=value['capability']
    exact(capability,'identity policy_digest protocol observation_format')
    sha(capability['identity']);sha(capability['policy_digest'])
    need(capability['protocol']=='bounded-document-rpc-1','execution-protocol-unavailable')
    need(capability['observation_format']=='posix-document-process-1','execution-observation-unavailable')
    locator = value['recovery_locator']
    exact(locator, 'store_id grant recovery_ordinal')
    store_id(locator['store_id']); sha(locator['grant']); integer(locator['recovery_ordinal'], 1, 1)
    need(locator['grant'] == value['grant'] and locator['store_id'] == scope['recovery_store_id'], 'execution-recovery-binding')
    return value


def event(kind, value):
    choice(kind, EVENT_FIELDS)
    exact(value, EVENT_FIELDS[kind], 'execution-event-fields')
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
            need(kind in ('worker-result', 'callback-completed', 'terminal'), 'execution-required-reason')
    for key in ('pass', 'reaped', 'established', 'success', 'group_absent', 'birth_absent', 'final_scan_confirmed', 'process_absence'):
        if key in value:
            boolean(value[key])
    if 'phase' in value:
        choice(value['phase'], PHASES)
    if 'byte_count' in value:
        integer(value['byte_count'])
    for key in ('grant', 'scope_sha256', 'recovery_locator_sha256', 'policy_digest', 'capability_digest', 'code_identity', 'original_sha256', 'journal_head'):
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
        need(value['pass'] is True, 'execution-admission')
    elif kind == 'rpc-reserved':
        choice(value['method'], METHODS)
    elif kind == 'callback-reserved':
        choice(value['tool'], ('read', 'write', 'verify'))
        need(type(value['file_ids']) is list and len(value['file_ids']) <= 8, 'execution-file-ids')
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
        need(value['current_call_effect'] == 'not_started', 'execution-refusal-effect')
    elif kind == 'diagnostic':
        choice(value['source'], ('runtime', 'worker', 'host'))
    elif kind == 'recovery-ready':
        local_id(value['output_id'], document=True)
    elif kind == 'processes-closed':
        integer(value['runtime_ref'], 1, 8192)
        need(type(value['children']) is list and len(value['children']) <= 256, 'execution-children')
        for child in value['children']:
            exact(child, 'pid birth absent')
            integer(child['pid'], 2, (1 << 31) - 1); birth(child['birth']); boolean(child['absent'])
    elif kind == 'terminal':
        choice(value['status'], ('completed', 'interrupted', 'revoked-before-launch', 'unknown'))
        choice(value['document_write_effect'], EFFECTS)
        need((value['stop_reason'] is None) == (value['status'] == 'completed'), 'execution-terminal-reason')
    elif kind == 'operator-resolved-unknown':
        choice(value['previous_status'], ('incomplete', 'unknown'))
        choice(value['recovery_availability'], AVAILABILITY)
        need(value['action'] == 'record-unknown-resolution' and value['process_absence'] is True, 'execution-resolution')
        need(type(value['documents']) is dict and 1 <= len(value['documents']) <= 8, 'execution-resolution-documents')
        for key, item in value['documents'].items():
            local_id(key, document=True); identity(item, nullable=True)
    return value



def request_record(value,contract):
    """Closed local request data. Exposure checks run before publication, not
    retrospectively when an old granted request is inspected after expiry."""
    exact(value,'prompt claims approved_external_links link_metadata','execution-request-fields')
    need(len(canonical_json_bytes(value))<=1048576,'execution-request-size')
    need(type(value['prompt']) is str and 0<len(value['prompt'].encode('utf-8'))<=65536,'execution-prompt-size')
    scope=contract['scope'];output=scope['output_id'];claims=value['claims']
    need(type(claims) is dict and set(claims)=={output},'execution-claims-coverage')
    rule=claims[output];need(type(rule) is dict,'execution-claim-fields');optional={'exact_view_sha256'} if 'exact_view_sha256' in rule else set()
    exact(rule,{'required','forbidden','evidence'}|optional,'execution-claim-fields')
    if optional:sha(rule['exact_view_sha256'])
    for field in ('required','forbidden'):
        need(type(rule[field]) is list and len(rule[field])<=256 and all(type(v) is str and 0<len(v)<=4096 for v in rule[field]),'execution-claim-strings')
    need(bool(rule['required']) and type(rule['evidence']) is list and 1<=len(rule['evidence'])<=256,'execution-claims-empty')
    for evidence in rule['evidence']:
        exact(evidence,'file_id quote');need(type(evidence['file_id']) is str and evidence['file_id'] in scope['documents'] and type(evidence['quote']) is str and 0<len(evidence['quote'])<=4096,'execution-claim-evidence')
    links=value['approved_external_links']
    need(type(links) is list and len(links)<=256 and all(type(v) is str and 0<len(v)<=4096 for v in links) and len(set(links))==len(links),'execution-link-list')
    metadata=value['link_metadata'];need(type(metadata) is dict and len(metadata)<=256,'execution-link-metadata')
    for name,entry in metadata.items():
        path(name);exact(entry,'identity mode size mtime_ns sha256 anchors')
        need(type(entry['identity']) is list and len(entry['identity'])==2,'execution-link-identity')
        for n in entry['identity']:integer(n)
        integer(entry['mode'],0,0o7777);integer(entry['size']);integer(entry['mtime_ns'])
        if entry['sha256'] is not None:sha(entry['sha256'])
        anchors=entry['anchors'];need(type(anchors) is list and len(anchors)<=256 and all(type(v) is str and len(v)<=4096 for v in anchors),'execution-link-anchors')
        need(entry['sha256'] is not None or not anchors,'execution-link-evidence-missing')
    need(len(canonical_json_bytes(value))<=1048576,'execution-request-size')
    return value
