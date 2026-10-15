"""Bounded project planning. No intent, Work or execution authority is granted."""
from __future__ import annotations

import copy
import os
import stat
import tempfile
from itertools import islice
from pathlib import Path
from typing import Any

from .errors import ContractError, InjectedCrash
from .jsonio import canonical_json_bytes, decode_json_bytes, sha256_bytes, sync_directory, _sync_fd
from .workspace import (_durable_directory, _exists, _file_json, _id, _require_kind,
                        _sha, classify_target, safe_target, validate_format, writer_guard)

MAX_CANDIDATES = 100
MAX_DECISIONS = 1000
MAX_BYTES = 1024 * 1024
ACTIONS = ('add', 'amend', 'select', 'defer', 'resume', 'link', 'disposition', 'reopen')
REQUEST_KEYS = {'record_type', 'schema_version', 'authority_home_id', 'request_id',
                'candidate_id', 'action', 'expected_sha256', 'writer', 'owner_statement',
                'reason', 'observed_at', 'payload'}
STORE_KEYS = {'record_type', 'schema_version', 'authority_home_id', 'candidates', 'selected', 'decisions'}
NOTICE = 'Planning only; no execution approval. Any outstanding lifecycle preview must be prepared again after a change.'


def require(ok: bool, message: str, code: str = 'HV2-CANDIDATE-RECORD') -> None:
    if not ok:
        raise ContractError(code, message)


def exact(value: Any, keys: set[str]) -> dict:
    require(isinstance(value, dict) and set(value) == keys, 'unknown or missing candidate fields')
    return value


def short(value: Any, *, empty: bool = False) -> bool:
    return isinstance(value, str) and len(value) <= 2000 and (empty or bool(value.strip()))


def reference(value: Any) -> dict:
    from .work import validate_ref
    exact(value, {'authority_home_id', 'kind', 'id', 'revision_ref'})
    require(_id(value['authority_home_id']) and _id(value['id']) and value['kind'] in ('intent', 'work'), 'invalid planning link')
    validate_ref(value['revision_ref'])
    return value


def request_shape(value: Any) -> dict:
    exact(value, REQUEST_KEYS)
    require(value['record_type'] == 'candidate-request' and type(value['schema_version']) is int and value['schema_version'] == 1, 'unsupported candidate request')
    require(all(_id(value[k]) for k in ('authority_home_id', 'request_id', 'candidate_id')), 'invalid candidate identity')
    require(isinstance(value['action'], str) and value['action'] in ACTIONS, 'unsupported candidate action')
    require(value['expected_sha256'] is None or _sha(value['expected_sha256']), 'invalid prior candidate digest')
    require(all(short(value[k]) for k in ('writer', 'owner_statement', 'reason', 'observed_at')), 'writer, Owner statement, reason and observation are required declarations, not authentication')
    p = value['payload']; action = value['action']
    if action in ('add', 'amend'):
        exact(p, {'title', 'purpose', 'expected_effect', 'related_candidates'})
        require(all(short(p[k]) for k in ('title', 'purpose', 'expected_effect')), 'title, purpose and expected effect required')
        require(isinstance(p['related_candidates'], list) and len(p['related_candidates']) <= MAX_CANDIDATES and all(_id(i) for i in p['related_candidates']) and len(set(p['related_candidates'])) == len(p['related_candidates']), 'invalid related candidate IDs')
    elif action == 'defer':
        exact(p, {'resume_condition'}); require(short(p['resume_condition'], empty=True), 'invalid resume condition; empty means unspecified')
    elif action == 'resume':
        exact(p, {'condition_observation'}); require(short(p['condition_observation']), 'state the condition observation or explicitly unknown')
    elif action == 'link':
        exact(p, {'target'}); reference(p['target'])
    elif action == 'disposition':
        exact(p, {'disposition', 'target'})
        require(p['disposition'] in ('absorbed', 'rejected'), 'unsupported disposition')
        if p['disposition'] == 'absorbed': reference(p['target'])
        else: require(p['target'] is None, 'rejection has no target')
    else:
        exact(p, set())
    return value


def empty_store(authority: str) -> dict:
    return {'record_type': 'candidate-planning', 'schema_version': 1, 'authority_home_id': authority,
            'candidates': {}, 'selected': None, 'decisions': []}


def transition(candidates: dict, selected: str | None, request: dict) -> tuple[dict, str | None, dict, dict]:
    """Pure planning fold. Live link checks are a separate, mutation-time boundary."""
    cid = request['candidate_id']; action = request['action']; p = request['payload']
    rows = copy.deepcopy(candidates); row = rows.get(cid)
    before = {'disposition': row['disposition'] if row else None, 'selected': selected}
    if action == 'add':
        require(row is None and cid.casefold() not in {x.casefold() for x in rows}, 'candidate ID already exists or is a case alias')
        require(len(rows) < MAX_CANDIDATES, 'candidate count limit; not saved; preserve history and request a supported capacity decision', 'HV2-CANDIDATE-LIMIT')
        row = {**copy.deepcopy(p), 'disposition': 'open', 'reason': request['reason'], 'resume_condition': '', 'links': []}
        rows[cid] = row
    else:
        require(row is not None, 'candidate not found')
    if action in ('add', 'amend'):
        require(all(i in rows and i != cid for i in p['related_candidates']), 'related candidate missing or self-reference')
        if action == 'amend': row.update(copy.deepcopy(p))
    elif action in ('select', 'defer', 'resume', 'reopen'):
        require(not any(r['kind'] == 'work' for r in row['links']), 'candidate is linked to a Work; use that Work\'s actual resume/decision flow or record a successor candidate')
        if action == 'select':
            require(row['disposition'] == 'open', 'only open candidates can be selected; explicitly resume deferred candidate first')
            require(selected != cid, 'candidate is already selected; use amend for changed narrative')
            selected = cid
        elif action == 'defer':
            require(row['disposition'] == 'open', 'only open candidates can be deferred')
            row['disposition'] = 'deferred'; row['resume_condition'] = p['resume_condition']
            if selected == cid: selected = None
        elif action == 'resume':
            require(row['disposition'] == 'deferred', 'only a named deferred candidate can resume')
            row['disposition'] = 'open'
        else:
            require(row['disposition'] == 'rejected', 'only an unlinked rejected candidate can be corrected to open')
            row['disposition'] = 'open'
    elif action in ('link', 'disposition'):
        require(row['disposition'] in ('open', 'deferred'), 'terminal candidate cannot receive a new link or disposition')
        target = p['target']
        if action == 'disposition':
            row['disposition'] = p['disposition']
            if selected == cid: selected = None
        if target is not None:
            require(target['authority_home_id'] == request['authority_home_id'], 'cross-home planning links are unsupported')
            same = [r for r in row['links'] if r['kind'] == target['kind']]
            require(not same or same[0]['id'] == target['id'], 'link cannot silently replace a different object; record a successor candidate')
            row['links'] = [r for r in row['links'] if r['kind'] != target['kind']] + [copy.deepcopy(target)]
            row['links'].sort(key=lambda r: r['kind'])
    row['reason'] = request['reason']
    return rows, selected, before, {'disposition': row['disposition'], 'selected': selected}


def validate_store(value: Any, authority: str) -> dict:
    exact(value, STORE_KEYS)
    require(value['record_type'] == 'candidate-planning' and type(value['schema_version']) is int and value['schema_version'] == 1, 'unsupported candidate schema; preserve bytes')
    require(value['authority_home_id'] == authority, 'candidate authority differs')
    require(isinstance(value['decisions'], list) and len(value['decisions']) <= MAX_DECISIONS, 'candidate decision limit', 'HV2-CANDIDATE-LIMIT')
    rows = {}; selected = None; seen = set()
    for event in value['decisions']:
        exact(event, {'request', 'before', 'after'})
        r = request_shape(event['request'])
        require(r['authority_home_id'] == authority and r['request_id'].casefold() not in seen, 'duplicate request identity or wrong authority')
        require((r['expected_sha256'] is None) == (len(seen) == 0), 'invalid first/prior digest presence')
        rows, selected, before, after = transition(rows, selected, r)
        require(event['before'] == before and event['after'] == after, 'candidate transition history differs')
        seen.add(r['request_id'].casefold())
    require(value['candidates'] == rows and value['selected'] == selected, 'candidate projection differs from decision history')
    return value


def _candidate_bytes(path: Path) -> bytes:
    """Bounded no-follow authority read, independent from the human view layer."""
    def stamp(s):
        return s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns
    fd = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:-1]:
            require(part in os.listdir(fd), 'planning path spelling differs')
            nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd); fd = nxt
        require(path.name in os.listdir(fd), 'planning file disappeared')
        leaf = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        try:
            before = os.fstat(leaf)
            require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, 'planning input is linked or special')
            require(before.st_size <= MAX_BYTES, 'candidate byte limit; preserve file', 'HV2-CANDIDATE-LIMIT')
            data = bytearray()
            while len(data) <= MAX_BYTES:
                chunk = os.read(leaf, min(65536, MAX_BYTES + 1 - len(data)))
                if not chunk: break
                data.extend(chunk)
            require(len(data) <= MAX_BYTES and stamp(before) == stamp(os.fstat(leaf)), 'planning input changed or oversized')
            require(stamp(before) == stamp(os.stat(path.name, dir_fd=fd, follow_symlinks=False)), 'planning input replaced')
            return bytes(data)
        finally:
            os.close(leaf)
    finally:
        os.close(fd)


def _read_once(target: Path, authority: str) -> tuple[dict, str | None]:
    directory = target / '.hrn/planning'
    if not _exists(directory): return empty_store(authority), None
    _require_kind(directory, True)
    names = [p.name for p in islice(directory.iterdir(), 3)]
    require(set(names) <= {'candidates.json'}, 'unknown planning member; preserve it')
    if not names: return empty_store(authority), None
    raw = _candidate_bytes(directory / 'candidates.json')
    require(len(raw) <= MAX_BYTES, 'candidate byte limit; preserve file', 'HV2-CANDIDATE-LIMIT')
    value = validate_store(decode_json_bytes(raw, require_canonical=True), authority)
    require(bool(value['decisions']), 'present planning store has no published decision; preserve bytes')
    return value, sha256_bytes(raw)


def read_candidates(target: Path) -> dict:
    try:
        target = safe_target(target)
        authority = validate_format(_file_json(target / '.hrn/format.json'))['authority_home_id']
        first = _read_once(target, authority)
        require(first == _read_once(target, authority), 'candidate store changed during read')
        return {'store': first[0], 'sha256': first[1], 'present': first[1] is not None}
    except (OSError, ValueError, RecursionError) as exc:
        raise ContractError('HV2-CANDIDATE-UNAVAILABLE', 'planning unavailable; preserve bytes, do not treat it as an empty list') from exc


def _graphs(target):
    from .work import WorkStore
    from .intent import workspace_intents
    return WorkStore(target)._all(), workspace_intents(target)


def _selected_revision(graph):
    if graph['current'] is None: return None
    return graph['selections'][graph['current']['selection_ref']['id']]['revision_ref']


def check_link(ref: dict, authority: str, works: dict, intents: dict, *, current: bool) -> dict:
    from .work import record_ref
    reference(ref)
    require(ref['authority_home_id'] == authority, 'link authority differs')
    graph = (works if ref['kind'] == 'work' else intents).get(ref['id'])
    require(graph is not None, 'linked object unavailable')
    revisions = graph['revisions'] if ref['kind'] == 'work' else graph['drafts']
    revision = revisions.get(ref['revision_ref']['id'])
    require(revision is not None and record_ref(revision, 'record_id' if ref['kind'] == 'work' else 'revision_id') == ref['revision_ref'], 'linked revision unavailable or digest differs')
    if current: require(_selected_revision(graph) == ref['revision_ref'], 'link requires current selected/accepted revision')
    return graph


class CandidateStore:
    def __init__(self, target: Path, runtime_verifier=None):
        from .product import require_workspace_runtime
        self.target = safe_target(target)
        self.runtime = runtime_verifier or require_workspace_runtime

    def mutate(self, request: dict, *, inject_at: str | None = None) -> dict:
        from .work import _visible_truth
        request_shape(request)
        require(inject_at in (None, 'after-temporary', 'after-directory', 'before-replace', 'after-replace'), 'unknown candidate interruption point')
        classify_target(self.target, mutation=True)
        with writer_guard(self.target):
            runtime = self.runtime(self.target)
            require(runtime.get('inventory_id') == 'entry-1', 'candidate writing requires an explicitly installed entry-1 release; this request does not authorize update', 'HV2-CANDIDATE-WINDOW')
            observed = read_candidates(self.target); store = observed['store']
            require(store['authority_home_id'] == request['authority_home_id'], 'request authority differs')
            works, intents = _graphs(self.target)
            require(not any(g['pending_decisions'] or g['pending_selections'] for g in works.values()) and not any(g['pending_acceptances'] or g['pending_selections'] for g in intents.values()), 'pending transaction; this call made no new write; read planning to check any prior publication, then recover the original exact Work/intent operation', 'HV2-CANDIDATE-PENDING')
            for event in store['decisions']:
                if event['request']['request_id'].casefold() == request['request_id'].casefold():
                    require(event['request'] == request, 'request ID already used with different bytes')
                    return {'classification': 'unchanged', **observed, 'request_id': request['request_id'], 'notice': NOTICE}
            require(request['expected_sha256'] == observed['sha256'], 'candidate changed; re-read before retry, not saved', 'HV2-CANDIDATE-STALE')
            require(len(store['decisions']) < MAX_DECISIONS, 'decision limit; not saved; retain history and request a supported capacity decision', 'HV2-CANDIDATE-LIMIT')
            target_ref = request['payload'].get('target')
            if target_ref is not None:
                graph = check_link(target_ref, store['authority_home_id'], works, intents, current=True)
                prior = store['candidates'].get(request['candidate_id'], {})
                if target_ref['kind'] == 'intent':
                    for work_ref in (r for r in prior.get('links', []) if r['kind'] == 'work'):
                        work_graph = check_link(work_ref, store['authority_home_id'], works, intents, current=False)
                        current_ref = _selected_revision(work_graph)
                        require(current_ref is not None, 'linked Work has no current revision')
                        work_intent = work_graph['revisions'][current_ref['id']]['intent_ref']
                        require(work_intent['id'] == target_ref['id'] and work_intent['revision_ref'] == target_ref['revision_ref'], 'linked Work current revision uses another intent revision')
                if target_ref['kind'] == 'work':
                    linked_intents = [r for r in prior.get('links', []) if r['kind'] == 'intent']
                    rev = graph['revisions'][target_ref['revision_ref']['id']]
                    require(not linked_intents or (linked_intents[0]['id'] == rev['intent_ref']['id'] and linked_intents[0]['revision_ref'] == rev['intent_ref']['revision_ref']), 'Work does not belong to candidate linked intent revision')
            rows, selected, before, after = transition(store['candidates'], store['selected'], request)
            new = {**store, 'candidates': rows, 'selected': selected, 'decisions': store['decisions'] + [{'request': copy.deepcopy(request), 'before': before, 'after': after}]}
            validate_store(new, store['authority_home_id'])
            raw = canonical_json_bytes(new)
            require(len(raw) <= MAX_BYTES, 'candidate byte limit; not saved; preserve history', 'HV2-CANDIDATE-LIMIT')
            _visible_truth(self.target, ['.hrn/planning/candidates.json'])
            staging = self.target / '.hrn/staging'; _durable_directory(staging)
            fd, name = tempfile.mkstemp(prefix='candidate-', dir=staging); temp = Path(name)
            with os.fdopen(fd, 'wb') as handle:
                handle.write(raw); handle.flush(); _sync_fd(handle.fileno())
            sync_directory(staging)
            def crash(point):
                if inject_at == point: raise InjectedCrash(point)
            crash('after-temporary')
            directory = self.target / '.hrn/planning'; _durable_directory(directory)
            crash('after-directory')
            require(observed == read_candidates(self.target), 'candidate changed before publication', 'HV2-CANDIDATE-STALE')
            require(runtime == self.runtime(self.target), 'runtime changed before candidate publication')
            require((works, intents) == _graphs(self.target), 'Work/intent changed before candidate publication')
            crash('before-replace')
            os.replace(temp, directory / 'candidates.json'); sync_directory(directory); sync_directory(staging)
            crash('after-replace')
            result = read_candidates(self.target)
            require(result['sha256'] == sha256_bytes(raw), 'candidate changed after publication; read before retry')
            return {'classification': 'saved', **result, 'request_id': request['request_id'], 'notice': NOTICE}
