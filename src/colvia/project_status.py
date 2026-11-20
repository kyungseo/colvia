"""Project overview from one published root. Reading never observes workspace files."""
from .codec import RecordError, require
from .maps import map_get, scan_map
from . import progress, work_lifecycle, work_dependencies
from .records import application_registry, head_summary, link

WINDOW = 200
ROW_BYTES = 4 * 1024**2
WINDOW_BYTES = 16 * 1024**2
GROUPS = {
    'review': '내 검토',
    'revision': '수정 요청',
    'continue': '이어갈 일',
    'paused': '일시정지',
    'plan': '계획',
    'unavailable': '확인 필요',
}


class ReadBudget:
    def __init__(self, store):
        self.store = store
        self.total = self.row = 0

    def load(self, ref):
        require(self.row + ref.byte_length <= ROW_BYTES, 'status-detail-limit')
        self.row += ref.byte_length
        self.total += ref.byte_length
        return self.store.load(ref)


def _row(key, ref, heads, load, workspace):
    head, plan, result, decision = head_summary(ref, load)
    p = head.payload
    require(key == 'work:' + p['work'], 'wrong-work-head')
    if ref.version == 2:
        work_lifecycle.validate_content(ref, load)
    state = p['phase']
    if p['archived'] or state in ('completed', 'discarded'):
        return None
    item = dict(work=p['work'], title=p['title'], workspace=p['workspace'],
                here=p['workspace'] == workspace, state=state, head=ref.sha256, plan=plan.ref.sha256)
    if p.get('action') == 'resume':
        item['resumed'] = True
    if result:
        item.update(revision=result.payload['revision'], submission=result.ref.sha256)
        paths = result.payload['changed']
        item['submitted_paths'] = paths[:5]
        item['submitted_file_count'] = len(paths)
    if state == 'review':
        group, action = 'review', f"제출본 {item['revision']}판 검토하기"
    elif state == 'paused':
        group, action = 'paused', p['next_action'] or '재개할 때 중단 사유 확인하기'
        item['reason'] = p['reason']
    elif state == 'active' and decision:
        group, action = 'revision', decision.payload['statement']
        item.update(reason=action, decision=decision.ref.sha256)
    elif state == 'planned':
        group, action = 'plan', '계획과 범위 살펴보기'
    elif state == 'approved':
        group, action = 'continue', '승인한 범위에서 시작하기'
    else:
        require(state == 'active', 'invalid-work-state')
        group, action = 'continue', p.get('next_action') or '승인 범위에서 이어가기'
        note = map_get(heads, 'progress:' + p['work'], load) if progress.eligible(head) else None
        if note:
            require(note.kind == 'work.progress', 'wrong-progress-head')
            saved = application_registry().inspect(note, load(note), required=True)
            require(all(saved.payload[k] == p[k] for k in ('work', 'workspace')), 'progress-work-mismatch')
            progress.validate_content(note, load)
            if not p.get('next_action') or link(saved, 'active') == ref:
                action = saved.payload['next_action']
    gate = work_dependencies.parent_gate(head, heads, load)
    if gate is not None:
        item['parent_submission'] = gate
    item.update(group=group, next_action=action)
    return item


def _cursor(root, after, offset):
    key = after.encode().hex() if after else ''
    return f'{root}:{offset}:{key}'


def _position(cursor, root):
    if cursor is None:
        return None, 0
    require(isinstance(cursor, str) and len(cursor) <= 2120, 'list-changed-or-invalid-cursor')
    try:
        _, position, key = cursor.split(':')
        offset = int(position)
        after = bytes.fromhex(key).decode() or None
    except (ValueError, UnicodeError):
        raise RecordError('list-changed-or-invalid-cursor') from None
    require((after is not None or offset > 0) and 0 <= offset < WINDOW and cursor == _cursor(root, after, offset),
            'list-changed-or-invalid-cursor')
    return after, offset


def project_status(store, workspace, *, limit=20, cursor=None):
    require(type(limit) is int and 1 <= limit <= 20, 'invalid-page-limit')
    root = store.root()
    after, offset = _position(cursor, root.ref.sha256)
    budget = ReadBudget(store)
    try:
        _, dependencies = work_dependencies._snapshot(store.project,root.heads,budget.load)
        relation_error = None
    except RecordError as exc:
        dependencies, relation_error = [], exc.code
    rows = []
    last = None
    more = False
    for index, (key, ref) in enumerate(scan_map(root.heads, store.load, after=after)):
        if index == WINDOW or WINDOW_BYTES - budget.total < ROW_BYTES:
            more = True
            break
        last = key
        if not key.startswith('work:'):
            continue
        budget.row = 0
        try:
            row = _row(key, ref, root.heads, budget.load, workspace)
            if row and dependencies:
                related = work_dependencies.relations(dependencies,row['work'],root.heads,budget.load,limit=4)
                if related['items']:
                    if row['state'] == 'active':
                        for relation in related['items']:
                            result = relation['result']
                            if relation['direction'] == 'requires' and result.get('revision_requested'):
                                relation['continuing_during_revision'] = True
                    row['dependencies'] = related
        except RecordError as exc:
            row = dict(work=key[5:], group='unavailable', error=exc.code,
                       next_action='기록을 확인한 뒤 다시 조회하기')
        if row is not None:
            rows.append(row)
    rows.sort(key=lambda row: (tuple(GROUPS).index(row['group']), row['work']))
    require(not offset or offset < len(rows), 'list-changed-or-invalid-cursor')
    page = rows[offset:offset + limit]
    next_cursor = None
    if offset + len(page) < len(rows):
        next_cursor = _cursor(root.ref.sha256, after, offset + len(page))
    elif more:
        next_cursor = _cursor(root.ref.sha256, last, 0)
    require(store.root().ref == root.ref, 'list-changed')
    counts = {group: sum(item['group'] == group for item in page) for group in GROUPS}
    work_partial = bool(cursor or next_cursor or counts['unavailable'])
    dependency_partial = bool(relation_error or any(
        item.get('parent_submission', {}).get('error') or
        item.get('dependencies', {}).get('more') or
        any(peer['peer_unavailable'] or peer['result']['status'] == 'unknown'
            for peer in item.get('dependencies', {}).get('items', []))
        for item in page))
    return dict(kind='project-status', project=store.project, root=root.ref.sha256,
                items=page, counts=counts, next=next_cursor,
                dependency_error=relation_error,
                work_partial=work_partial, dependency_partial=dependency_partial,
                partial=work_partial or dependency_partial)


def render(value, printable):
    def short(text):
        safe = printable(text)
        return safe if len(safe) <= 72 else safe[:71] + '…'

    lines = []
    items = value['items']
    if len(items) > 1:
        counts = value['counts']
        lines.append(' · '.join(f'{label} {counts[group]}건' for group, label in GROUPS.items() if counts[group]))
    if value.get('work_partial', value['partial']):
        lines.append('일부 기록만 표시합니다. 다른 검토 요청이 있을 수 있습니다.')
    if value.get('dependency_error'):
        lines.append('의존 관계 기록을 확인할 수 없습니다.')
    for item in items:
        title = short(item.get('title', item['work']))
        if item.get('resumed'):
            title += ' (재개)'
        place = ' (다른 작업 폴더)' if item.get('here') is False else ''
        reason = item.get('reason')
        reason = short(reason) + ' · ' if reason and reason != item['next_action'] else ''
        lines.append(f"{GROUPS[item['group']]} · {title}{place} — {reason}{short(item['next_action'])}")
        if item.get('parent_submission'):
            lines.append('  ' + work_dependencies.gate_line(item['parent_submission']))
        if item.get('dependencies'):
            lines.extend('  '+line for line in work_dependencies.lines(item['dependencies'],short))
    if not items and not value['partial']:
        lines.append('현재 검토하거나 이어갈 Work가 없습니다. 저장한 후보를 보거나 새 작업을 시작할 수 있습니다.')
    if value['next']:
        lines.append('더 보기 · project status --cursor ' + value['next'])
    return '\n'.join(lines)
