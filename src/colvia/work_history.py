"""Read one Work's recorded decisions and context in publication order."""
import json

from . import progress, work_lifecycle
from .codec import RecordError, require
from .maps import map_get
from .records import application_registry, head_summary, link
from .storage.sqlite import _token

WINDOW = 100
PAGE_BYTES = 16 * 1024**2
LABELS = {
    'plan': '계획', 'approve': '범위 승인', 'scope': '범위 추가 승인', 'progress': '진행 메모',
    'submit': '제출', 'accept': '수락', 'request-changes': '수정 요청',
    'pause': '일시정지', 'resume': '재개', 'discard': '폐기', 'replace': '대체',
    'other-change': '작업 기록', 'note-removed': '메모 연결', 'issue': '기록 상태',
}


class PageReader:
    """Cache immutable metadata for one page; never read file bodies."""
    def __init__(self, store):
        self.store = store
        self.cache = {}
        self.size = 0
        self.registry = application_registry()

    def load(self, ref):
        if ref not in self.cache:
            require(self.size + ref.byte_length <= PAGE_BYTES, 'work-history-read-limit')
            self.cache[ref] = self.store.load(ref)
            self.size += ref.byte_length
        return self.cache[ref]

    def object(self, ref, kind):
        require(ref is not None and ref.kind == kind, 'work-history-record-mismatch')
        return self.registry.inspect(ref, self.load(ref), required=True)

    def publication(self, ref):
        root = self.object(ref, 'state.root')
        require(root.payload['project'] == self.store.project, 'work-history-record-mismatch')
        return root

    def selection(self, root, work):
        heads = link(root, 'heads')
        return (map_get(heads, 'work:' + work, self.load), map_get(heads, 'progress:' + work, self.load))


def _head_event(reader, work, current, previous):
    head, plan, result, decision = head_summary(current, reader.load)
    require(head.payload['work'] == work and link(head, 'previous') == previous,
            'work-history-record-mismatch')
    prior = reader.object(previous, 'work.head') if previous else None
    if prior:
        require(all(prior.payload[k] == head.payload[k] for k in ('work', 'workspace')),
                'work-history-record-mismatch')

    def changed(role):
        return link(head, role) != (link(prior, role) if prior else None)

    def event(kind, source, statement, **extra):
        item = dict(kind=kind, source=source.sha256, head=current.sha256, plan=plan.ref.sha256,
                    text=statement, **extra)
        if result and kind in ('accept', 'request-changes', 'submit'):
            item.update(submission=result.ref.sha256, revision=result.payload['revision'])
        return item

    if current.version == 2:
        work_lifecycle.validate_content(current, reader.load)
        p = head.payload
        return event(p['action'], current, p['reason'], next_action=p['next_action'], target=p['target'])
    if decision and changed('decision'):
        auth = link(decision, 'authorization')
        extra = {}
        if auth:
            from .worker_records import validate_authorization
            authorization, binding = validate_authorization(auth, reader.load)
            require(decision.payload['action'] == 'accept' and link(binding,'result') == result.ref
                    and link(binding,'plan') == plan.ref and binding.payload['work'] == work
                    and binding.payload['source'] == head.payload['workspace'], 'worker-decision-authorization-mismatch')
            extra.update(authority=authorization.payload['authority'], authorization=auth.sha256)
        return event(decision.payload['action'], decision.ref, decision.payload['statement'], **extra)
    if result and changed('result'):
        return event('submit', result.ref, result.payload['summary'])
    approval = link(head, 'approval')
    if approval and changed('approval'):
        approved = reader.object(approval, 'work.approval')
        if approval.version in (2, 3):
            require(link(approved,'basis') == previous, 'scope-history-mismatch')
            return event('scope', approval, approved.payload['statement'], reason=approved.payload['reason'])
        return event('approve', approval, approved.payload['statement'])
    if changed('plan'):
        return event('plan', plan.ref, plan.payload['goal'])
    if prior and not changed('context'):
        phases = prior.payload['phase'], head.payload['phase']
        if phases == ('approved', 'active') or (
            phases == ('completed', 'completed') and head.payload['archived'] != prior.payload['archived']
        ):
            return None  # Start and archive carry an existing decision without revising it.
    return event('other-change', current, '다른 작업 기록 변경')


def _note_event(reader, work, head, prior_head, note, prior_note):
    saved = reader.object(note, 'work.progress')
    active = progress.validate_content(note, reader.load)
    require(saved.payload['work'] == work and link(saved, 'previous') == prior_note
            and active.ref in (prior_head, head), 'progress-work-mismatch')
    return dict(kind='progress', source=note.sha256, head=active.ref.sha256,
                plan=link(active, 'plan').sha256, note={k:saved.payload[k] for k in progress.NOTE_FIELDS})


def _issue(code):
    if code in ('object-unavailable', 'root-unavailable', 'unknown-required-kind'):
        return 'unavailable'
    if code == 'work-history-read-limit':
        return 'read-limit'
    return 'invalid'


def history(store, work, *, limit=20, cursor=None):
    _token(work)
    require(type(limit) is int and 1 <= limit <= 20, 'invalid-page-limit')
    latest = store.root()
    reader = PageReader(store)

    def position(before, slot=0):
        return dict(root=latest.ref.sha256, work=work, before=before, slot=slot)

    start = position(None) if cursor is None else cursor
    require(type(start) is dict and set(start) == {'root', 'work', 'before', 'slot'}
            and start['root'] == latest.ref.sha256 and start['work'] == work
            and type(start['slot']) is int and start['slot'] in (0, 1), 'work-history-cursor')
    if start['before'] is not None:
        _token(start['before'])
    location = start
    items = []
    more = None
    stopped = None
    sequence = operation = None
    try:
        require(map_get(latest.heads, 'work:' + work, reader.load) is not None, 'work-not-found')
        where = latest.ref
        if start['before'] is not None:
            where = map_get(latest.operations, start['before'], reader.load)
            require(where is not None, 'work-history-cursor')
        current = reader.publication(where)
        selected = reader.selection(current, work)
        for _ in range(WINDOW):
            sequence, operation = current.payload['sequence'], current.payload['operation']
            if selected[0] is None:
                break
            previous = reader.publication(link(current, 'previous'))
            require(previous.payload['sequence'] + 1 == sequence, 'invalid-root-lineage')
            older = reader.selection(previous, work)
            if location['slot']:
                require(selected[1] != older[1], 'work-history-cursor')
            for slot in range(location['slot'], 2):
                new, old = selected[slot], older[slot]
                if new == old:
                    continue
                location = position(location['before'], slot)
                if len(items) == limit:
                    more = location
                    break
                source = new or current.ref
                try:
                    if slot == 0:
                        item = _head_event(reader, work, new, old)
                    elif new is None:
                        item = dict(kind='note-removed', source=source.sha256, text='진행 메모 연결 해제')
                    else:
                        item = _note_event(reader, work, selected[0], older[0], new, old)
                except RecordError as exc:
                    if exc.code == 'work-history-read-limit':
                        raise
                    item = dict(kind='issue', source=source.sha256, issue=_issue(exc.code), code=exc.code)
                if item:
                    items.append(dict(sequence=sequence, operation=operation, open=location, **item))
            if more or older[0] is None:
                break
            location = position(operation)
            current, selected = previous, older
        else:
            more = location
    except RecordError as exc:
        if exc.code in ('work-not-found', 'work-history-cursor'):
            raise
        if exc.code == 'work-history-read-limit' and location != start:
            more = location
        else:
            stopped = dict(sequence=sequence, operation=operation, issue=_issue(exc.code), code=exc.code)
    require(store.root().ref == latest.ref, 'list-changed')
    issue = next((row['code'] for row in items if row['kind'] == 'issue'), None)
    unavailable = stopped['code'] if stopped else issue
    return dict(kind='work-history', work=work, root=latest.ref.sha256, items=items,
                continuation=cursor is not None, partial=bool(more or unavailable), unavailable=unavailable,
                stopped=stopped, next=more)


def _issue_label(issue):
    return {'unavailable': '기록을 확인할 수 없습니다.', 'invalid': '기록 연결 또는 내용이 일치하지 않습니다.',
            'read-limit': '이 기록이 한 번에 읽을 수 있는 범위를 넘었습니다.'}[issue]


def render(page, printable):
    lines = [printable(page['work']) + ' · 기록된 순서 (최신순)']
    for item in page['items']:
        label = LABELS.get(item['kind'], '작업 기록')
        if item.get('authority') == 'delegated':
            label = '위임 수락'
        if 'revision' in item:
            label += f" · 제출본 {item['revision']}판"
        if item['kind'] == 'issue':
            text = _issue_label(item['issue']) + f" (기록 순번 {item['sequence']})"
        elif 'note' in item:
            labels = ('진행', '검사', '남은 일', '다음 행동')
            text = ' · '.join(label + ' ' + printable(item['note'][key])
                              for label, key in zip(labels, progress.NOTE_FIELDS))
        else:
            text = printable(item['text'])
        for key, field in [('reason','사유'), ('target','대체 Work'), ('next_action','다음 행동')]:
            if item.get(key):
                text += ' · ' + field + ' ' + printable(item[key])
        lines.append(label + ' · ' + text + ' [' + item['source'][:12] + ']')
    if page['stopped']:
        stop = page['stopped']
        location = f" · 기록 순번 {stop['sequence']}" if stop['sequence'] is not None else ''
        lines.append('이전 기록 조회 중단' + location + ' · ' + _issue_label(stop['issue']))
    if page['partial']:
        lines.append('현재 페이지에 표시된 기록을 기준으로 확인하세요.')
    if page['next']:
        lines.append('이전 기록 · --cursor ' + json.dumps(page['next'], separators=(',', ':')))
    return '\n'.join(lines)
