"""Candidate ordering records a reported user decision, independently of Work authority."""
from datetime import datetime, timezone
import hashlib

from .codec import RecordError, canonical_bytes, decode_envelope, require
from .graph import Schema
from .maps import map_get, scan_map
from .records import application_registry, fields, link, one, record, text
from .storage.sqlite import _token

KIND = 'planning.priority'
LEVELS = ('high', 'normal', 'low', 'unset')
LABELS = dict(zip(LEVELS, ('높음', '보통', '낮음', '미지정')))
BASIS = 'reported-user-request'
SCAN_WINDOW = 200


def change_basis(project, instance, candidate, selected, previous, level):
    parts = [KIND, project, instance, candidate, selected.sha256,
             previous.sha256 if previous else None, level]
    return hashlib.sha256(canonical_bytes(parts)).hexdigest()


def validate_payload(p):
    fields(p, {'project', 'instance', 'candidate', 'old', 'new', 'recorder', 'authority', 'request',
               'reason', 'as_of', 'basis', 'operation'})
    for key in ('project', 'instance', 'candidate', 'operation'):
        _token(p[key])
    require(p['old'] in LEVELS and p['new'] in LEVELS and p['old'] != p['new'],
            'invalid-candidate-priority')
    require(p['recorder'] in ('agent', 'operator') and p['authority'] == BASIS,
            'invalid-priority-source')
    text(p['request'], 2048)
    require(p['request'].strip(), 'priority-request-required')
    if p['reason'] is not None:
        text(p['reason'], 2048)
    require(type(p['as_of']) is int and 0 < p['as_of'] <= 253402300799, 'invalid-priority-time')
    require(isinstance(p['basis'], str) and len(p['basis']) == 64
            and all(c in '0123456789abcdef' for c in p['basis']), 'invalid-priority-basis')
    one(p, 'candidate')
    one(p, 'previous', True)


def validate_content(ref, load):
    event = decode_envelope(ref, load(ref))
    p = event.payload
    selected = link(event, 'candidate')
    candidate = decode_envelope(selected, load(selected))
    require(candidate.payload['candidate'] == p['candidate'] and candidate.payload['state'] == 'open',
            'priority-candidate-mismatch')
    previous = link(event, 'previous')
    require(p['basis'] == change_basis(p['project'], p['instance'], p['candidate'],
                                       selected, previous, p['new']), 'invalid-priority-basis')
    old = 'unset'
    if previous:
        prior = decode_envelope(previous, load(previous)).payload
        require((prior['project'], prior['candidate']) == (p['project'], p['candidate']),
                'priority-candidate-mismatch')
        old = prior['new']
    require(old == p['old'], 'priority-history-mismatch')


def schema():
    return Schema(KIND, 1, {'candidate': 'decision', 'previous': 'provenance'}, validate_payload,
                  {'candidate': frozenset({'planning.candidate'}), 'previous': frozenset({KIND})},
                  content=validate_content)


def current_event(store, candidate, ref):
    if ref is None:
        return None
    event = application_registry().inspect(ref, store.load(ref), required=True)
    require(ref.kind == KIND and event.payload['candidate'] == candidate
            and event.payload['project'] == store.project, 'priority-candidate-mismatch')
    return event


def preview(store, candidate, level):
    _token(candidate)
    require(level in LEVELS, 'invalid-candidate-priority')
    heads = store.root().heads
    selected = map_get(heads, 'candidate:' + candidate, store.load)
    require(selected is not None, 'candidate-not-found')
    obj = application_registry().inspect(selected, store.load(selected), required=True)
    require(selected.kind == 'planning.candidate' and obj.payload['candidate'] == candidate,
            'wrong-candidate')
    require(obj.payload['state'] == 'open', 'priority-candidate-closed')
    previous = map_get(heads, 'priority:' + candidate, store.load)
    event = current_event(store, candidate, previous)
    before = event.payload['new'] if event else 'unset'
    basis = change_basis(store.project, store.instance, candidate, selected, previous, level)
    return (dict(kind='priority-preview', candidate=candidate, title=obj.payload['title'],
                 old=before, new=level, basis=basis,
                 first_project_priority='schema:' + KIND + ':1' not in store.requirements()['read']), selected, previous)


def entry(event):
    previous = link(event, 'previous')
    return {**{k: v for k, v in event.payload.items() if k != 'links'},
            'event_ref': event.ref.sha256, 'candidate_ref': link(event, 'candidate').sha256,
            'previous_ref': previous.sha256 if previous else None}


def apply(store, candidate, level, *, basis, request, reason, recorder, operation):
    from .effects import guard
    _token(candidate)
    require(recorder in ('agent', 'operator'), 'invalid-priority-source')
    text(request, 2048)
    require(request.strip(), 'priority-request-required')
    if reason is not None:
        text(reason, 2048)
    intent = dict(candidate=candidate, new=level, basis=basis, request=request,
                  reason=reason, recorder=recorder, operation=operation)
    key = 'priority:' + candidate

    def replay():
        result = store.operation_result(operation)
        if result is None:
            return None
        root = decode_envelope(result[1], store.load(result[1]))
        event = current_event(store, candidate, map_get(link(root, 'heads'), key, store.load))
        require(event is not None and all(event.payload[k] == v for k, v in intent.items()),
                'priority-operation-conflict')
        return dict(kind='priority-change', change=entry(event), replayed=True)

    try:
        done = replay()
        if done:
            return done
        shown, selected, previous = preview(store, candidate, level)
        require(basis == shown['basis'], 'priority-preview-stale')
        if shown['old'] == level:
            return dict(kind='priority-unchanged', candidate=candidate, new=level)
        ref, raw = record(KIND, dict(**intent, project=store.project, instance=store.instance, old=shown['old'], authority=BASIS,
                                     as_of=int(datetime.now(timezone.utc).timestamp())),
                          {'candidate': ('decision', selected), 'previous': ('provenance', previous)})
        registry = application_registry()
        def validate(load):
            guard(load)
            registry.inspect(ref, load(ref), required=True)
            validate_content(ref, load)
        store.commit_heads(operation=operation, expected={key: previous, 'candidate:'+candidate: selected},
                           changes={key: ref}, objects=[(ref, raw)], validate=validate)
        return dict(kind='priority-change', change=entry(decode_envelope(ref, raw)), replayed=False)
    except RecordError as exc:
        if exc.code in ('head-conflict', 'operation-already-recorded', 'priority-preview-stale'):
            done = replay()
            if done:
                return done
            if exc.code == 'head-conflict':
                raise RecordError('priority-preview-stale') from exc
        raise


def history(store, candidate, *, limit=20, cursor=None):
    _token(candidate)
    require(type(limit) is int and 1 <= limit <= 100, 'invalid-page-limit')
    heads = store.root().heads
    require(map_get(heads, 'candidate:' + candidate, store.load) is not None, 'candidate-not-found')
    latest = map_get(heads, 'priority:' + candidate, store.load)
    rows = []
    offset = 0
    if cursor is not None:
        require(isinstance(cursor, dict) and set(cursor) == {'priority', 'offset'}
                and latest and cursor['priority'] == latest.sha256 and type(cursor['offset']) is int
                and 0 < cursor['offset'] <= 1_000_000, 'list-changed-or-invalid-cursor')
        offset = cursor['offset']
    ref = latest
    skipped = 0
    while ref and len(rows) < limit:
        event = current_event(store, candidate, ref)
        if skipped < offset:
            skipped += 1
        else:
            rows.append(entry(event))
        ref = link(event, 'previous')
    require(not offset or rows, 'list-changed-or-invalid-cursor')
    return dict(kind='priority-history', candidate=candidate, items=rows,
                next=dict(priority=latest.sha256, offset=offset + len(rows)) if ref else None)


def ranked(planning, *, limit=20, cursor=None, display=False):
    """Sort a bounded scan window; the agent can merge windows from the same root."""
    store = planning.store
    root = store.root()
    after, offset = None, 0
    require(type(limit) is int and 1 <= limit <= 100, 'invalid-page-limit')
    if cursor is not None:
        require(type(cursor) is dict and set(cursor) == {'ranked_root', 'after', 'offset'}
                and cursor['ranked_root'] == root.ref.sha256
                and (cursor['after'] is None or isinstance(cursor['after'], str))
                and type(cursor['offset']) is int and 0 <= cursor['offset'] < SCAN_WINDOW,
                'list-changed-or-invalid-cursor')
        after, offset = cursor['after'], cursor['offset']
    window = []
    more = False
    last = None
    for index, (key, _) in enumerate(scan_map(root.heads, store.load, after=after)):
        if index == SCAN_WINDOW:
            more = True
            break
        last = key
        if key.startswith('candidate:'):
            name = key[len('candidate:'):]
            candidate = planning.candidate(name, display=display)
            if candidate['state'] == 'open':
                window.append(candidate)
    window.sort(key=lambda row: (LEVELS.index(row['priority']), row['candidate']))
    require(not offset or offset < len(window), 'list-changed-or-invalid-cursor')
    items = window[offset:offset + limit]
    next_cursor = None
    if offset + len(items) < len(window):
        next_cursor = dict(ranked_root=root.ref.sha256, after=after, offset=offset+len(items))
    elif more:
        next_cursor = dict(ranked_root=root.ref.sha256, after=last, offset=0)
    require(store.root().ref == root.ref, 'list-changed')
    return dict(kind='ranked-candidates', items=items, next=next_cursor,
                partial=bool(cursor is not None or next_cursor), root=root.ref.sha256)


def render(value, printable, relation):
    import json
    kind = value['kind']
    if kind == 'priority-preview':
        line = f"{printable(value['title'])} · {LABELS[value['old']]} → {LABELS[value['new']]}"
        if value['first_project_priority'] and value['old'] != value['new']:
            line += '\n첫 순위를 저장하면 이 기능을 지원하지 않는 구버전에서는 이 프로젝트와 이후 백업을 열 수 없습니다. 순위를 모두 지워도 마찬가지입니다.'
        return line
    if kind == 'priority-unchanged':
        return '현재 순위와 같습니다 · ' + LABELS[value['new']]
    if kind == 'ranked-candidates':
        lines = []
        for row in value['items']:
            line = LABELS[row['priority']] + ' · ' + printable(row['title'])
            if row.get('linked_work'):
                line += ' · ' + relation(row.get('linked_title'), row['linked_work'], row['linked_state'])
            lines.append(line)
        if value['partial']:
            lines.append('일부 후보만 표시합니다. 전체 순위는 모든 페이지를 확인해 주세요.')
        elif not lines:
            lines.append('열린 후보가 없습니다.')
    else:
        rows = [value['change']] if kind == 'priority-change' else value['items']
        lines = []
        for row in rows:
            source = '에이전트가 전달한 사용자 요청' if row['recorder'] == 'agent' else '호출자가 직접 입력했다고 밝힌 요청'
            when = datetime.fromtimestamp(row['as_of'], timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
            lines.append(f"{when} · {LABELS[row['old']]} → {LABELS[row['new']]} · {source} · {printable(row['request'])}")
            if row['reason']:
                lines.append('사유 · ' + printable(row['reason']))
        if not lines:
            lines.append('순위 변경 기록이 없습니다.')
    if value.get('replayed'):
        lines.append('이전에 처리한 요청입니다. 현재 순위는 후보 목록에서 확인하세요.')
    if value.get('next'):
        lines.append('더 보기 · --cursor ' + json.dumps(value['next'], separators=(',', ':')))
    return '\n'.join(lines)
