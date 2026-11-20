"""Append exact file permissions to an ordinary Work before submission or during an explicitly requested revision."""
from dataclasses import asdict
from fnmatch import fnmatchcase
from hashlib import sha256
from ntpath import isreserved
import stat
import unicodedata

from .bodies import BODY_LIMIT, descriptor, submission_size
from .codec import RecordError, canonical_bytes, decode_envelope, require
from .credentials import protected_git_path
from .graph import Schema
from .maps import build_map, map_get, read_map, scan_map
from .progress import eligible
from .records import fields, head_summary, identity, link, one, record, text
from .rework import MAX_HEADS, PathIndex, SubmissionBlocked, attribution
from .tree import entry_at, logical_path, read_tree
from .storage.sqlite import _token


class PathRefusal(RecordError):
    def __init__(self, code, path):
        super().__init__(code)
        self.path = path


def delta_paths(edit, create):
    paths = [*edit, *create]
    require(paths and len(paths) <= 100000, 'invalid-scope')
    seen = PathIndex(())
    for path in paths:
        require(logical_path(path) == path, 'invalid-scope-path')
        parts = path.casefold().split('/')
        if (any(p in ('.git', '.colvia', '.colvia-link.json') or
                any(c in p for c in '*?[]:<>|"') or p.endswith(('.', ' ')) or
                isreserved(p) for p in parts)
                or path.casefold() in ('colvia', 'colvia.cmd', 'colvia.ps1', 'colvia.exe', 'agents.md', 'claude.md') or protected_git_path(path)):
            raise PathRefusal('scope-protected-path', path)
        if seen.overlaps(path):
            raise PathRefusal('scope-path-overlap', path)
        seen.add(path)
    return paths


def validate_delta(plan, edit, create, checks):
    paths = delta_paths(edit, create)
    require(len(plan.payload['scope']) + len(paths) <= 100000, 'invalid-scope')
    taken = PathIndex(plan.payload['scope'])
    for path in paths:
        if taken.overlaps(path):
            raise PathRefusal('scope-path-overlap', path)
        for exclusion in plan.payload['excludes']:
            rule = exclusion.rstrip('/').casefold()
            if fnmatchcase(path.casefold(), rule) or path.casefold().startswith(rule + '/'):
                raise PathRefusal('scope-protected-path', path)
    combined = plan.payload['checks'] + checks
    require(len(combined) <= 100 and len(set(combined)) == len(combined), 'invalid-plan-criteria')
    for check in checks:
        text(check, 2048)


def validate_payload(payload, extra=()):
    fields(payload, {'work', 'workspace', 'statement', 'reason', 'edit', 'create', 'checks', *extra})
    identity(payload)
    for k in ('statement', 'reason'):
        text(payload[k], 2048)
        require(payload[k].strip() and payload[k].isprintable(), 'invalid-record-text')
    for k in ('edit', 'create', 'checks'):
        require(type(payload[k]) is list and all(type(v) is str for v in payload[k]), 'invalid-scope')
    for k in ('edit', 'create'):
        require(payload[k] == sorted(set(payload[k])), 'invalid-scope')
    one(payload, 'plan')
    one(payload, 'basis')


def reworking(head):
    return (head.payload['phase'] == 'active' and not head.payload['archived']
            and link(head, 'context') is None and link(head, 'result') is not None
            and link(head, 'decision') is not None)


def rework_schema():
    from .records import MAP_KINDS
    targets = {name: frozenset({kind}) for name, kind in (
        ('plan', 'work.plan'), ('basis', 'work.head'), ('submission', 'work.submission'),
        ('decision', 'work.decision'), ('submitted_plan', 'work.plan'))}
    targets['peer_heads'] = MAP_KINDS

    def check(payload):
        validate_payload(payload, ('operation',))
        _token(payload['operation'])
        for role in targets:
            one(payload, role)

    roles = dict.fromkeys(targets, 'decision')
    # Historical lookup only. Audits/backups retain provenance; an ordinary
    # write need not validate the bodies of unrelated historical Works.
    roles['peer_heads'] = 'provenance'
    return Schema('work.approval', 3, roles, check, targets, content=validate_content)


def schema():
    return Schema('work.approval', 2, {'plan':'decision', 'basis':'decision'}, validate_payload,
                  {'plan':frozenset({'work.plan'}), 'basis':frozenset({'work.head'})},
                  content=validate_content)


def validate_content(ref, load):
    amendment = decode_envelope(ref, load(ref))
    p = amendment.payload
    basis, prior, result, decision = head_summary(link(amendment, 'basis'), load)
    if ref.version == 3:
        require(reworking(basis) and decision.payload['action']=='request-changes'
                and link(amendment,'submission')==result.ref
                and link(amendment,'decision')==decision.ref
                and decision.payload['statement'].strip()
                and map_get(link(amendment, 'peer_heads'), 'work:' + p['work'], load) == basis.ref
                and link(amendment,'submitted_plan')==link(result,'plan'), 'rework-scope-binding')
    else:
        require(eligible(basis), 'scope-first-submission-only')
    planref = link(amendment, 'plan')
    plan = decode_envelope(planref, load(planref))
    validate_delta(prior, p['edit'], p['create'], p['checks'])
    require(all(plan.payload[k] == prior.payload[k] for k in ('title','goal','work','workspace','excludes'))
            and all(p[k] == prior.payload[k] for k in ('work','workspace'))
            and link(plan,'baseline') == link(prior,'baseline')
            and plan.payload['scope'] == sorted(prior.payload['scope'] + p['edit'] + p['create'])
            and plan.payload['checks'] == prior.payload['checks'] + p['checks'], 'scope-history-mismatch')
    before = read_map(link(prior,'before'), load)
    after = read_map(link(plan,'before'), load)
    require(after.keys() == before.keys() | set(p['edit']) and
            all(after[k] == v for k,v in before.items()), 'scope-history-mismatch')
    baseline = decode_envelope(link(prior,'baseline'), load(link(prior,'baseline')))
    require(baseline.payload['common'] == baseline.payload['gitdir'], 'scope-primary-workspace-only')
    entries = read_tree(link(baseline,'tree'), load)
    originals = {e['path']:e for e in entries}
    occupied = PathIndex(originals)
    require(all(not occupied.overlaps(path) for path in p['create']), 'scope-original-conflict')
    for path in p['edit']:
        original = originals.get(path)
        body = descriptor(after[path], load(after[path])).payload
        require(original and original['kind'] == 'regular' and
                all(original[k] == body[k] for k in ('sha256','size')), 'scope-history-mismatch')


def validate_active_link(ref, load):
    """An amendment starts at its exact approved Work; later heads may carry it."""
    head = decode_envelope(ref, load(ref))
    approval = link(head, 'approval')
    if approval is not None and approval.version == 3:
        # Full backup audit calls schema content directly without WorkService.
        head_summary(ref, load)
    if approval is None or not (eligible(head) and approval.version == 2
                                or reworking(head) and approval.version == 3):
        return
    previous = link(head, 'previous')
    require(previous is not None, 'scope-history-mismatch')
    amendment = decode_envelope(approval, load(approval))
    if previous == link(amendment, 'basis') and approval.version == 3:
        require(reworking(head) and link(head, 'result') == link(amendment, 'submission')
                and link(head, 'decision') == link(amendment, 'decision'), 'scope-history-mismatch')
    elif previous != link(amendment,'basis'):
        prior = decode_envelope(previous, load(previous))
        require(link(prior,'approval') == approval and link(prior,'plan') == link(head,'plan')
                and all(prior.payload[k] == head.payload[k] for k in ('work','workspace')),
                'scope-history-mismatch')


def history(head, load):
    amendments = []
    approval = link(head, 'approval')
    while approval is not None and approval.version in (2,3):
        require(len(amendments) < 64, 'decision-depth-limit')
        validate_content(approval, load)
        amendment = decode_envelope(approval, load(approval))
        basis = decode_envelope(link(amendment,'basis'), load(link(amendment,'basis')))
        amendments.append((amendment, basis))
        approval = link(basis, 'approval')
    return amendments


def peer_heads(head_map, work, load):
    selected = {}
    for key, ref in scan_map(head_map, load):
        if key.startswith('work:') and key != 'work:' + work:
            require(len(selected) < MAX_HEADS, 'scope-peer-read-limit')
            require(ref.kind == 'work.head', 'scope-peer-history-uncertain')
            selected[key] = ref
    return selected


def check_open_peer_scopes(service, head, snapshot, paths):
    proposed = PathIndex(paths)
    for key, peer_ref in peer_heads(snapshot.heads, head.payload['work'], service.store.load).items():
        peer, plan, _, _ = head_summary(peer_ref, service.store.load)
        require(key == 'work:' + peer.payload['work'], 'scope-peer-history-uncertain')
        if (peer.payload['workspace'] == head.payload['workspace']
                and peer.payload['phase'] in ('approved', 'active', 'paused', 'review')):
            for path in plan.payload['scope']:
                if proposed.overlaps(path):
                    raise PathRefusal('scope-peer-overlap', path)


def changed_peer_path(service, submitted, previous, paths):
    # Each submission lists cumulative changes from its own plan baseline.
    # Compare revisions so a later restoration counts, while an unchanged
    # historical edit carried forward in a new revision does not.
    current = set(submitted.payload['changed'])
    prior = set(previous.payload['changed']) if previous else set()
    for path in sorted(current ^ prior):
        if paths.overlaps(path):
            return path
    both = [p for p in current & prior if paths.overlaps(p)]
    if both:
        now = service._object(link(submitted, 'observation'))
        then = service._object(link(previous, 'observation'))
        for path in sorted(both):
            if entry_at(link(now, 'tree'), path, service.store.load) != entry_at(link(then, 'tree'), path, service.store.load):
                return path


def check_peer_submissions(service, head, snapshot):
    """Compare each newly submitted peer revision with paths granted before it."""
    approval = link(head, 'approval')
    if approval is None or approval.version != 3:
        return
    load = service.store.load
    grants = []
    while approval.version == 3:
        require(len(grants) < 64, 'decision-depth-limit')
        amendment = service._object(approval)
        paths = PathIndex(amendment.payload['edit'] + amendment.payload['create'])
        issued_at = map_get(snapshot.operations, amendment.payload['operation'], load)
        require(issued_at is not None and issued_at.kind == 'state.root', 'scope-peer-history-uncertain')
        sealed_heads = link(service._object(issued_at), 'heads')
        require(link(amendment, 'peer_heads') == sealed_heads, 'scope-peer-history-uncertain')
        grants.append((sealed_heads, paths))
        basis = service._object(link(amendment, 'basis'))
        approval = link(basis, 'approval')
    current = peer_heads(snapshot.heads, head.payload['work'], load)
    steps = 0
    for saved_heads, paths in grants:
        saved = peer_heads(saved_heads, head.payload['work'], load)
        require(saved.keys() <= current.keys(), 'scope-peer-history-uncertain')
        for key, peer_ref in current.items():
            old_head = saved.get(key)
            if old_head == peer_ref:
                continue
            peer = service._object(peer_ref)
            require(key == 'work:' + peer.payload['work'], 'scope-peer-history-uncertain')
            previous = service._object(old_head) if old_head else None
            if previous:
                require(all(previous.payload[k] == peer.payload[k] for k in ('work', 'workspace')),
                        'scope-peer-history-uncertain')
            if peer.payload['workspace'] != head.payload['workspace']:
                continue
            stop = link(previous, 'result') if previous else None
            cursor = link(peer, 'result')
            while cursor != stop:
                steps += 1
                require(steps <= MAX_HEADS, 'scope-peer-read-limit')
                require(cursor is not None, 'scope-peer-history-uncertain')
                submitted = service._object(cursor)
                require(all(submitted.payload[k] == peer.payload[k] for k in ('work', 'workspace')),
                        'scope-peer-history-uncertain')
                previous_ref = link(submitted, 'previous')
                older = service._object(previous_ref) if previous_ref else None
                if older:
                    require(older.ref.kind == 'work.submission'
                            and all(older.payload[k] == submitted.payload[k] for k in ('work','workspace'))
                            and older.payload['revision'] + 1 == submitted.payload['revision'],
                            'scope-peer-history-uncertain')
                path = changed_peer_path(service, submitted, older, paths)
                if path:
                    raise SubmissionBlocked('scope-peer-overlap', [dict(path=path, change='proof-mismatch', peer_work=peer.payload['work'])],
                        '추가 승인한 경로에 다른 작업이 제출한 변경이 있습니다.',
                        '두 작업의 제출본과 파일을 보존하세요. 필요하면 이 작업을 일시정지하고 별도 Work에서 이어가세요.')
                cursor = previous_ref


def review(service, work, edit, create, checks, reason):
    edit, create = sorted(edit), sorted(create)
    snapshot = service.store.root()
    headref, head = service._head(work)
    require(eligible(head) or reworking(head), 'scope-first-submission-only')
    plan = service._object(link(head,'plan'))
    validate_delta(plan, edit, create, checks)
    revision = None
    if reworking(head):
        result = service._object(link(head, 'result'))
        request = service._object(link(head, 'decision'))
        require(request.payload['action'] == 'request-changes' and request.payload['statement'].strip(),
                'rework-decision-required')
        require(len(history(head, service.store.load)) < 64, 'decision-depth-limit')
        revision = result.payload['revision']
        carried = attribution(result, service.store.load)
        excluded = PathIndex(carried)
        for peer in set(carried.values()):
            peer_plan = service._object(link(service._object(peer), 'plan'))
            for path in peer_plan.payload['scope']:
                excluded.add(path)
        for path in edit + create:
            if excluded.overlaps(path):
                raise PathRefusal('scope-peer-overlap', path)
        check_open_peer_scopes(service, head, snapshot, edit + create)
        check_peer_submissions(service, head, snapshot)
    text(reason, 2048)
    require(reason.strip() and reason.isprintable(), 'invalid-record-text')
    _, entries, observed = service._observe_from_plan(plan, edit + create)
    require(observed.topology.common == observed.topology.gitdir, 'scope-primary-workspace-only')
    originals = {e['path']:e for e in entries}
    occupied = PathIndex(originals)
    current = {e['path']:e for e in observed.snapshot.entries}
    inventory = {logical_path(s.native_path).casefold():s for s in observed.snapshot.inventory}
    git = service.workspace.git if observed.topology.kind == 'git' else None
    root = service.workspace.root
    ignored = set()
    if git:
        spellings = set(edit + create)
        for path in edit + create:
            parent, _, name = path.rpartition('/')
            item = inventory.get(path.casefold())
            directory = inventory.get(parent.casefold())
            if item:
                spellings.add(item.native_path)
            elif directory:
                spellings.add(directory.native_path + '/' + name)
        # Git ignore patterns may preserve a different Unicode spelling from the filesystem.
        spellings.update(unicodedata.normalize('NFD', p) for p in tuple(spellings))
        ignored = git.ignored(root, sorted(spellings))
    tracked = PathIndex(git.tracked_for_creation(root)) if git and create else None
    witnesses = {}
    edit_set = set(edit)
    for path in edit + create:
        if path in ignored:
            raise PathRefusal('scope-protected-path', path)
        parents = []
        parts = path.split('/')
        for n in range(1,len(parts)):
            ancestor = '/'.join(parts[:n])
            item = inventory.get(ancestor.casefold())
            if not item or logical_path(item.native_path) != ancestor or not stat.S_ISDIR(item.mode):
                raise PathRefusal('scope-parent-uncertain', path)
            parents.append([item.volume, item.file_id])
        item = inventory.get(path.casefold())
        if path in edit_set and path in originals:
            if (not item or originals[path]['kind'] != 'regular' or current.get(path) != originals[path]
                    or not stat.S_ISREG(item.mode) or originals[path]['size'] > BODY_LIMIT):
                raise PathRefusal('scope-original-changed', path)
            witness = [originals[path], item.volume, item.file_id]
        elif path not in edit_set:
            if item or occupied.overlaps(path) or (tracked and tracked.overlaps(path)):
                raise PathRefusal('scope-create-occupied', path)
            # Some native aliases (e.g. Windows short names) are not in the directory listing.
            try:
                (root / path).lstat()
            except FileNotFoundError:
                pass
            else:
                raise PathRefusal('scope-create-occupied', path)
            witness = None
        else:
            raise PathRefusal('scope-original-unavailable', path)
        witnesses[path] = [parents, witness]
    submission_size([originals[p]['size'] for p in plan.payload['scope'] + edit if p in originals])
    delta = dict(edit=edit, create=create, checks=checks, reason=reason)
    basis = [delta, witnesses, observed.policy.digest, asdict(observed.topology.root)]
    if revision is not None:
        require(service.store.root().ref == snapshot.ref, 'scope-preview-stale')
    digest = sha256(canonical_bytes(basis)).hexdigest()
    receipt = service._receipt('scope-add:' + digest, work, headref)
    version = 3 if revision is not None else 2
    first = f'schema:work.approval:{version}' not in service.store.requirements()['read']
    preview = dict(work=work, state='active', scope_preview=True, title=head.payload['title'],
                   scope=plan.payload['scope'], existing_checks=plan.payload['checks'], excludes=plan.payload['excludes'],
                   first_scope_addition=first, receipt=receipt, **delta)
    if revision is not None:
        preview.update(revision=revision, revision_request=request.payload['statement'])
    return preview, head, plan, observed, snapshot


def apply(service, work, operation, edit, create, checks, reason, receipt, statement):
    def inspect():
        return review(service, work, edit, create, checks, reason)
    preview, head, prior, observed, snapshot = inspect()
    require(preview['receipt'] == receipt, 'scope-preview-stale')
    delta = {key:preview[key] for key in ('edit','create','checks','reason')}
    store = service.store
    with store.import_attempt(operation, 'scope-addition'):
        newmap, objects, _ = service.workspace.capture(delta['edit'], observed, operation)
        local = dict(objects)
        additions = read_map(newmap, lambda ref: local[ref] if ref in local else store.load(ref))
        before = read_map(link(prior,'before'), store.load)
        merged = build_map((before | additions).items())
        data = {k:v for k,v in prior.payload.items() if k != 'links'}
        data.update(scope=sorted(data['scope']+delta['edit']+delta['create']), checks=data['checks']+checks)
        plan = record('work.plan', data, {'baseline':('integrity',link(prior,'baseline')),
                                         'before':('integrity',merged.root)})
        proof={'plan':('decision',plan[0]), 'basis':('decision',head.ref)}
        old_result,decision=link(head,'result'),link(head,'decision')
        if old_result:
            result=service._object(old_result)
            proof.update(submission=('decision',old_result),decision=('decision',decision),
                         submitted_plan=('decision',link(result,'plan')), peer_heads=('provenance', snapshot.heads))
        payload = dict(work=work, workspace=data['workspace'], statement=statement, **delta)
        if old_result:
            payload['operation'] = operation
        approval = record('work.approval', payload, proof, version=3 if old_result else 2)
        updated = service._head_record(plan[0], data, 'active', approval=approval[0], result=old_result, decision=decision, previous=head.ref)
        def recheck():
            require(inspect()[0]['receipt'] == receipt, 'scope-preview-stale')
        service._publish(operation, work, head.ref, updated, [*objects,*merged.objects,plan,approval],
                         import_id=operation, recheck=recheck, pinned_root=snapshot.ref if old_result else None)
    return dict(work=work, state='active', scope_added=True, **delta)

