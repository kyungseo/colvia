"""Explicit advisory Work dependencies in a project-local immutable revision."""
import hashlib
import time

from .codec import RecordError, canonical_bytes, require
from .effects import guard
from .graph import Schema
from .maps import map_get
from .records import application_registry, fields, head_summary, link, one, record, text
from .storage.sqlite import _token

KIND = 'planning.dependency'
KEY = 'project:work-dependencies'
MAX_EDGES = 256
ROLES = ('dependent', 'removed', 'added')
LABELS = {'accepted': '수락됨', 'waiting': '수락 대기', 'reassign': '선행 조건 재지정 필요',
          'recheck': '하위 결과 재확인 필요', 'unknown': '확인 불가'}


def _names(dependent, removed, added):
    _token(dependent)
    names = [dependent]
    for name in (removed, added):
        if name is not None:
            _token(name)
            names.append(name)
    require(len(names) > 1 and len({n.casefold() for n in names}) == len(names),
            'invalid-dependency-selection')
    return names


def _edges(rows):
    require(type(rows) is list and len(rows) <= MAX_EDGES, 'dependency-limit')
    for row in rows:
        require(type(row) is list and len(row) == 2, 'invalid-dependency-graph')
        _names(row[0], None, row[1])
    edges = {tuple(row) for row in rows}
    require(rows == [list(edge) for edge in sorted(edges)], 'invalid-dependency-graph')
    names = {name for edge in edges for name in edge}
    require(len(names) == len({n.casefold() for n in names}), 'invalid-dependency-selection')
    return edges


def transition(previous, dependent, removed, added):
    edges = set(previous)
    if removed is not None:
        require((dependent, removed) in edges, 'dependency-not-present')
        edges.remove((dependent, removed))
    if added is not None:
        require((dependent, added) not in edges, 'dependency-already-present')
        edges.add((dependent, added))
    rows = [list(edge) for edge in sorted(edges)]
    _edges(rows)
    return rows


def _basis(project, instance, refs, previous):
    parts = [KIND, project, instance, previous.sha256 if previous else None,
             [r.sha256 if r else None for r in refs]]
    return hashlib.sha256(canonical_bytes(parts)).hexdigest()


def payload(p):
    fields(p, {'project','instance',*ROLES,'edges','operation','basis','request','recorder','authority','time'})
    for key in ('project','instance','operation'):
        _token(p[key])
    _names(*(p[k] for k in ROLES))
    _edges(p['edges'])
    require(p['authority'] == 'reported-dependency-request' and p['recorder'] in ('agent','operator'),
            'invalid-dependency-authority')
    text(p['request'], 2048)
    require(p['request'].strip() and type(p['time']) is int and p['time'] > 0, 'invalid-dependency-request')
    for k in ROLES:
        one(p, k, k != 'dependent')
        require(bool(p['links'][k]) == (p[k] is not None), 'invalid-dependency-selection')
    one(p,'previous',True)


def _inspect(ref, load):
    return application_registry().inspect(ref, load(ref), required=True)


def validate(ref, load):
    obj = _inspect(ref, load)
    p = obj.payload
    refs = [link(obj,k) for k in ROLES]
    for key, selected in zip(ROLES, refs):
        if selected:
            head = _inspect(selected, load)
            require(head.payload['work'] == p[key], 'dependency-endpoint-mismatch')
    previous = link(obj,'previous')
    prior = _inspect(previous,load).payload if previous else None
    require(not prior or prior['project'] == p['project'], 'dependency-project-mismatch')
    rows = transition(_edges(prior['edges']) if prior else set(), *(p[k] for k in ROLES))
    require(rows == p['edges'] and p['basis'] == _basis(p['project'],p['instance'],refs,previous),
            'invalid-dependency-graph')
    check_graph(rows)
    return obj


def schema():
    roles = {k:'decision' for k in ROLES}
    targets = {k:frozenset({'work.head'}) for k in ROLES}
    return Schema(KIND,1,dict(roles,previous='provenance'),payload,
                  dict(targets,previous=frozenset({KIND})),content=validate)


def check_graph(rows, children=None):
    """Follow explicit requirements and, during admission, existing parent submission gates."""
    neighbors = {}
    spellings = {}
    for dependent, prerequisite in rows:
        neighbors.setdefault(dependent,set()).add(prerequisite)
    visiting, visited = set(), set()
    visits = 0
    def visit(name):
        nonlocal visits
        require(spellings.setdefault(name.casefold(), name) == name, 'invalid-dependency-selection')
        require(name not in visiting,'dependency-cycle')
        if name in visited:
            return
        visiting.add(name)
        explicit = neighbors.get(name,set())
        implicit = set(children(name)) if children else set()
        require(not explicit.intersection(implicit),'dependency-composition-duplicate')
        visits += len(explicit) + len(implicit)
        require(visits <= MAX_EDGES, 'dependency-limit')
        for other in explicit | implicit:
            visit(other)
        visiting.remove(name)
        visited.add(name)
    for name in neighbors:
        visit(name)


def _snapshot(project, heads, load):
    ref = map_get(heads, KEY, load)
    if not ref:
        return None, []
    require(ref.kind == KIND, 'invalid-dependency-graph')
    event = validate(ref,load)
    require(event.payload['project'] == project, 'dependency-project-mismatch')
    return ref, event.payload['edges']


def composition_children(name, head, load):
    ref = head('composition:'+name)
    if not ref:
        return ()
    require(ref.kind == 'composition.declaration','invalid-dependency-graph')
    declaration = _inspect(ref,load)
    require(declaration.payload['parent']==name,'invalid-dependency-graph')
    return declaration.payload['children']


def check_composition_change(parent, before, after, project):
    """Only newly selected children can introduce a duplicate or a mixed cycle."""
    ref = before.head(KEY)
    if not ref:
        return
    load = GraphReader(after)
    old = set(composition_children(parent, before.head, load))
    new = set(composition_children(parent, after.head, load)) - old
    if not new:
        return
    require(ref.kind == KIND, 'invalid-dependency-graph')
    event = _inspect(ref, load)
    require(event.payload['project'] == project, 'dependency-project-mismatch')
    neighbors = {}
    names = {}
    for dependent, prerequisite in event.payload['edges']:
        neighbors.setdefault(dependent, set()).add(prerequisite)
        names[dependent.casefold()] = dependent
        names[prerequisite.casefold()] = prerequisite
    if not neighbors:
        return
    for name in new | {parent}:
        require(names.get(name.casefold(), name) == name, 'invalid-dependency-selection')
    require(not new.intersection(neighbors.get(parent, ())), 'composition-dependency-duplicate')
    pending = list(new)
    seen = set()
    visits = 0
    while pending:
        child = pending.pop()
        require(child != parent, 'dependency-cycle')
        if child in seen:
            continue
        seen.add(child)
        successors = neighbors.get(child, set()).union(composition_children(child, after.head, load))
        visits += len(successors)
        require(visits <= MAX_EDGES, 'dependency-limit')
        pending.extend(successors - seen)


class GraphReader:
    """Bound admission reads independently of result body sizes."""
    def __init__(self, load):
        self.load = load
        self.objects = 0
        self.size = 0

    def __call__(self, ref):
        self.objects += 1
        self.size += ref.byte_length
        require(self.objects <= 8192 and self.size <= 16 * 1024**2, 'dependency-limit')
        return self.load(ref)


def _proposal(store, dependent, removed, added):
    _names(dependent, removed, added)
    root = store.root()
    load = GraphReader(store.load)
    head = lambda key: map_get(root.heads, key, load)
    prev, rows = _snapshot(store.project, root.heads, load)
    expected = {KEY:prev}
    refs = []
    titles = {}
    for name in (dependent, removed, added):
        ref = head('work:'+name) if name else None
        if name:
            require(ref is not None and ref.kind == 'work.head','dependency-work-required')
            obj = _inspect(ref,load)
            require(obj.payload['work'] == name,'dependency-endpoint-mismatch')
            if added and name in (dependent,added):
                require(obj.payload['phase'] != 'discarded','dependency-discarded')
            expected['work:'+name] = ref
            titles[name] = obj.payload['title']
        refs.append(ref)
    after = transition(_edges(rows),dependent,removed,added)
    def pinned(key):
        expected[key] = head(key)
        return expected[key]
    def children(name):
        endpoint = head('work:' + name)
        require(endpoint and endpoint.kind == 'work.head' and
                _inspect(endpoint, load).payload['work'] == name, 'dependency-endpoint-mismatch')
        return composition_children(name, pinned, load)
    check_graph(after, children)
    basis = _basis(store.project,store.instance,refs,prev)
    return (dict(kind='dependency-preview',dependent=dependent,removed=removed,added=added,titles=titles,
                 basis=basis,first_project_dependency=prev is None),expected,refs,after)


def preview(store, dependent, removed, added):
    return _proposal(store,dependent,removed,added)[0]


def apply(store, dependent, removed, added, *, basis, request, recorder, operation):
    intent = dict(dependent=dependent,removed=removed,added=added,basis=basis,request=request,
                  recorder=recorder,operation=operation)
    def replay():
        saved = store.operation_result(operation)
        if saved is None:
            return None
        root = _inspect(saved[1],store.load)
        ref = map_get(link(root,'heads'),KEY,store.load)
        require(ref is not None and ref.kind == KIND,'dependency-operation-conflict')
        e = validate(ref,store.load)
        require(e.payload['project']==store.project and all(e.payload[k]==v for k,v in intent.items()),
                'dependency-operation-conflict')
        return dict(kind='dependency-change',**intent,event=ref.sha256,replayed=True)
    try:
        done = replay()
        if done:
            return done
        shown,expected,refs,rows = _proposal(store,dependent,removed,added)
        require(shown['basis'] == basis,'dependency-preview-stale')
        links = {k:('decision',r) for k,r in zip(ROLES,refs)}
        links['previous'] = ('provenance',expected[KEY])
        ref,raw = record(KIND,dict(**intent,authority='reported-dependency-request',
                                   project=store.project,instance=store.instance,time=int(time.time()),edges=rows),links)
        def check(load):
            guard(load)
            validate(ref,load)
        store.commit_heads(operation=operation,expected=expected,changes={KEY:ref},objects=[(ref,raw)],validate=check)
        return dict(kind='dependency-change',**intent,event=ref.sha256,replayed=False)
    except RecordError as exc:
        if exc.code in ('store-outcome-unknown','dependency-operation-conflict'):
            raise
        done = replay()
        if done:
            return done
        raise


class SnapshotReader:
    def __init__(self, heads, load):
        self.heads = heads
        self.load = load

    def __call__(self, ref):
        return self.load(ref)

    def head(self, key):
        return map_get(self.heads, key, self.load)


def _outcome(name, heads, load):
    ref = map_get(heads,'work:'+name,load)
    require(ref is not None,'dependency-work-required')
    head,plan,result,decision = head_summary(ref,load)
    p = head.payload
    require(p['work']==name,'dependency-endpoint-mismatch')
    info = dict(work=name,title=p['title'],state=p['phase'],archived=p['archived'],status='waiting')
    if ref.version == 2:
        from .work_lifecycle import validate_content
        validate_content(ref,load)
    if p['phase']=='discarded':
        replacement = link(head, 'replacement')
        info.update(status='reassign', replacement=p.get('target') or None)
        if replacement:
            info['replacement_title'] = _inspect(replacement, load).payload['title']
    elif p['phase']=='active' and decision:
        info['revision_requested'] = True
    if p['phase']=='completed':
        require(result and decision and decision.payload['action']=='accept','acceptance-required')
        from .composition import validate_context
        reader = SnapshotReader(heads,load)
        validate_context(head, plan, result, reader)
        status = 'accepted'
        try:
            validate_context(head, plan, result, reader, live=True)
        except RecordError as exc:
            if exc.code not in {'composition-child-changed', 'composition-child-membership-stale',
                                'composition-declaration-stale', 'composition-membership-stale'}:
                raise
            status = 'recheck'
            info['reason'] = exc.code
        auth = link(decision,'authorization')
        if auth and auth.kind=='group.authorization':
            from .group_records import validate_decision
            validate_decision(decision.ref,load)
            require(decision.payload['work']==name and decision.payload['workspace']==p['workspace'] and
                    link(decision,'result')==result.ref,'group-decision-member-mismatch')
        elif auth:
            from .worker_records import validate_authorization
            _,binding = validate_authorization(auth,load)
            require(link(binding,'result')==result.ref and link(binding,'plan')==plan.ref and
                    binding.payload['work']==name and binding.payload['source']==p['workspace'],
                    'worker-decision-authorization-mismatch')
        info.update(status=status,plan=plan.ref.sha256,submission=result.ref.sha256,
                    revision=result.payload['revision'],decision=decision.ref.sha256)
        if auth:
            info['authorization'] = auth.sha256
    return info


def parent_gate(head, heads, load):
    """Summarize existing parent submission requirements using the parent's selected captures."""
    from .composition import refs
    context = link(head, 'context')
    if not context or context.kind != 'composition.binding':
        return None
    try:
        parent = head.payload['work']
        reader = SnapshotReader(heads, load)
        binding = _inspect(context, load)
        declaration = _inspect(link(binding, 'declaration'), load)
        require(reader.head('composition:' + parent) == declaration.ref and
                declaration.payload['parent'] == binding.payload['parent'] == parent and
                link(declaration, 'plan') == link(head, 'plan'), 'composition-parent-mismatch')
        children = declaration.payload['children']
        captures = {}
        for ref in refs(binding, 'captures'):
            capture = _inspect(ref, load)
            child = capture.payload['child']
            require(child in children and child not in captures, 'composition-capture-identity')
            captures[child] = capture
        counts = dict(waiting=0, rebind=0, bound=0)
        for child, expected_plan in zip(children, refs(declaration, 'children')):
            current = _outcome(child, heads, load)
            require(current['status'] not in ('reassign','recheck'), 'composition-child-changed')
            if current['status'] != 'accepted':
                counts['waiting'] += 1
                continue
            captured = captures.get(child)
            matches = captured and current['plan'] == expected_plan.sha256 and all(
                link(captured, key).sha256 == current[field]
                for key, field in [('plan','plan'), ('result','submission'), ('decision','decision')])
            counts['bound' if matches else 'rebind'] += 1
        return counts
    except RecordError as exc:
        return dict(error=exc.code)


def gate_line(gate):
    if 'error' in gate:
        return '상위 Work 제출 조건 · 하위 결과 확인 불가'
    return f"상위 Work 제출 조건 · 수락 대기 {gate['waiting']}건 · 연결 확인 필요 {gate['rebind']}건 · 연결됨 {gate['bound']}건"


def relations(rows, work, heads, load, *, offset=0, limit=20, next_item=None):
    pairs = [('requires',b) for a,b in rows if a==work]
    pairs.extend(('required_by',a) for a,b in rows if b==work)
    require(type(offset) is int and 0 <= offset <= len(pairs),'invalid-dependency-cursor')
    items = []
    outcomes = {}
    def outcome(name):
        if name not in outcomes:
            try:
                outcomes[name] = _outcome(name,heads,load)
            except RecordError as exc:
                outcomes[name] = dict(work=name,status='unknown',error=exc.code)
        return outcomes[name]
    for direction,name in pairs[offset:offset+limit]:
        if next_item is not None and not next_item():
            break
        peer = outcome(name)
        result = peer if direction == 'requires' else outcome(work)
        items.append(dict(direction=direction,work=name,title=peer.get('title',name),
                          result=result,peer_unavailable='error' in peer))
    return dict(items=items,more=offset+len(items)<len(pairs))


def show(store, work, cursor=None):
    from .project_status import ReadBudget, ROW_BYTES, WINDOW_BYTES
    _token(work)
    root = store.root()
    budget = ReadBudget(store)
    load = budget.load
    selected = map_get(root.heads, 'work:' + work, load)
    require(selected is not None, 'dependency-work-required')
    try:
        _, rows = _snapshot(store.project, root.heads, load)
    except RecordError as exc:
        require(store.root().ref == root.ref, 'list-changed')
        return dict(kind='dependency-show', work=work, items=[], more=False, error=exc.code, next=None)
    offset = 0
    if cursor is not None:
        require(isinstance(cursor,dict) and set(cursor)=={'root','work','offset'} and
                cursor['root']==root.ref.sha256 and cursor['work']==work,'invalid-dependency-cursor')
        offset = cursor['offset']
    budget.row = 0
    selected_head = _inspect(selected, load)
    require(selected.kind == 'work.head' and selected_head.payload['work'] == work, 'dependency-endpoint-mismatch')
    gate = parent_gate(selected_head, root.heads, load)
    def next_item():
        budget.row = 0
        return budget.total + ROW_BYTES <= WINDOW_BYTES
    page = relations(rows, work, root.heads, load, offset=offset, next_item=next_item)
    if gate is not None:
        page['parent_submission'] = gate
    require(store.root().ref == root.ref,'list-changed')
    return dict(kind='dependency-show',work=work,**page,
                next=dict(root=root.ref.sha256,work=work,offset=offset+len(page['items'])) if page['more'] else None)


def history(store, work, cursor=None):
    from .project_status import ReadBudget, ROW_BYTES, WINDOW_BYTES
    _token(work)
    root = store.root()
    budget = ReadBudget(store)
    load = budget.load
    require(map_get(root.heads,'work:'+work,load) is not None,'dependency-work-required')
    ref = map_get(root.heads,KEY,load)
    if cursor is not None:
        # Continue only at a genuine, immutable project operation and its previous event.
        require(type(cursor) is dict and set(cursor)=={'root','work','operation'}
                and cursor['root']==root.ref.sha256 and cursor['work']==work,'invalid-dependency-cursor')
        _token(cursor['operation'])
        before = map_get(root.operations, cursor['operation'], load)
        require(before is not None, 'invalid-dependency-cursor')
        # The operation map pins its before-root in this lineage, including after restore.
        previous_root = _inspect(before, load)
        ref = map_get(link(previous_root, 'heads'), KEY, load)
    entries = []
    last = None
    for _ in range(20):
        if not ref:
            break
        require(ref.kind==KIND,'invalid-dependency-graph')
        if last is not None and budget.total + ROW_BYTES > WINDOW_BYTES:
            break
        budget.row = 0
        event = validate(ref,load)
        p = event.payload
        require(p['project']==store.project,'dependency-project-mismatch')
        if work in (p[k] for k in ROLES):
            entries.append(dict(event=ref.sha256,**{k:p[k] for k in
                                (*ROLES,'request','recorder','authority','time','operation')}))
        last = p['operation']
        ref = link(event,'previous')
    require(store.root().ref == root.ref,'list-changed')
    return dict(kind='dependency-history',items=entries,
                next=dict(root=root.ref.sha256,work=work,operation=last) if ref else None)


def lines(view, printable):
    result = []
    for item in view['items']:
        name = printable(item.get('title',item['work']))
        outcome = item['result']
        status = LABELS[outcome['status']]
        if outcome['status'] in ('accepted', 'recheck'):
            status += f" · 제출본 {outcome['revision']}판"
        elif item.get('continuing_during_revision'):
            status += ' · 진행 중인 작업의 선행 결과를 다시 검토 중'
        elif outcome.get('revision_requested'):
            status += ' · 수정 요청'
        elif outcome.get('state') in ('paused','review'):
            status += ' · '+{'paused':'일시정지','review':'검토 중'}[outcome['state']]
        if outcome.get('archived'):
            status += ' · 보관됨'
        if outcome.get('replacement'):
            status += ' · 대체 Work ' + printable(outcome.get('replacement_title', outcome['replacement']))
        if item['peer_unavailable'] and item['direction'] == 'required_by':
            status += ' · 상대 작업 확인 불가'
        direction = '필요한 결과' if item['direction']=='requires' else '이 결과가 필요한 작업'
        result.append(direction+' · '+name+' · '+status)
    if view.get('parent_submission'):
        result.append(gate_line(view['parent_submission']))
    if view['more']:
        result.append('일부 관계만 표시합니다. 해당 Work의 의존 관계에서 나머지를 확인하세요.')
    return result


def render(value,printable):
    import json
    if value['kind'] in ('dependency-show','dependency-history'):
        if value['kind']=='dependency-history':
            parts = [f"{item['dependent']} · 해제 {item['removed'] or '—'} · 추가 {item['added'] or '—'} · "
                     + ('에이전트가 전달한 요청' if item['recorder']=='agent' else '호출자가 직접 입력했다고 밝힌 요청')
                     + ' · ' + printable(item['request']) for item in value['items']]
            if not parts:
                parts = ['이 구간에 해당 Work의 변경 기록이 없습니다.']
        elif value.get('error'):
            parts = ['의존 관계 기록을 확인할 수 없습니다.']
        else:
            parts = lines(value,printable) or ['기록된 의존 관계가 없습니다.']
        if value['next']:
            parts.append('더 보기 · --cursor '+json.dumps(value['next'],separators=(',',':')))
        return '\n'.join(parts)
    titles = value.get('titles',{})
    name = lambda k: printable(titles.get(value[k],value[k]))
    parts = [name('dependent')]
    if value['removed']:
        parts.append('선행 조건 해제 · '+name('removed'))
    if value['added']:
        parts.append('수락 결과 필요 · '+name('added'))
    if value['kind'] == 'dependency-preview':
        parts.append('기준값 · ' + value['basis'])
    if value.get('first_project_dependency'):
        parts.append('첫 저장 후에는 의존 관계를 지원하지 않는 버전에서 이 프로젝트와 새 백업을 열 수 없습니다. 해제해도 호환성은 복원되지 않습니다.')
    if value.get('replayed'):
        parts.append('이전에 기록한 변경입니다.')
    return '\n'.join(parts)
