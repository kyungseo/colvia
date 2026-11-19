"""Append exact file permissions to an ordinary Work before its first submission."""
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
from .maps import build_map, read_map
from .progress import eligible
from .records import fields, head_summary, identity, link, one, record, text
from .rework import PathIndex
from .tree import logical_path, read_tree


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


def validate_payload(payload):
    fields(payload, {'work', 'workspace', 'statement', 'reason', 'edit', 'create', 'checks'})
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


def schema():
    return Schema('work.approval', 2, {'plan':'decision', 'basis':'decision'}, validate_payload,
                  {'plan':frozenset({'work.plan'}), 'basis':frozenset({'work.head'})},
                  content=validate_content)


def validate_content(ref, load):
    amendment = decode_envelope(ref, load(ref))
    p = amendment.payload
    basis, prior, _, _ = head_summary(link(amendment, 'basis'), load)
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
    if not eligible(head) or approval.version != 2:
        return
    previous = link(head, 'previous')
    require(previous is not None, 'scope-history-mismatch')
    amendment = decode_envelope(approval, load(approval))
    if previous != link(amendment,'basis'):
        prior = decode_envelope(previous, load(previous))
        require(link(prior,'approval') == approval and link(prior,'plan') == link(head,'plan')
                and all(prior.payload[k] == head.payload[k] for k in ('work','workspace')),
                'scope-history-mismatch')


def history(head, load):
    amendments = []
    approval = link(head, 'approval')
    while approval is not None and approval.version == 2:
        require(len(amendments) < 64, 'decision-depth-limit')
        validate_content(approval, load)
        amendment = decode_envelope(approval, load(approval))
        basis = decode_envelope(link(amendment,'basis'), load(link(amendment,'basis')))
        amendments.append((amendment, basis))
        approval = link(basis, 'approval')
    return amendments


def review(service, work, edit, create, checks, reason):
    edit, create = sorted(edit), sorted(create)
    headref, head = service._head(work)
    require(eligible(head), 'scope-first-submission-only')
    plan = service._object(link(head,'plan'))
    validate_delta(plan, edit, create, checks)
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
    digest = sha256(canonical_bytes([delta,witnesses,observed.policy.digest,asdict(observed.topology.root)])).hexdigest()
    receipt = service._receipt('scope-add:' + digest, work, headref)
    first = 'schema:work.approval:2' not in service.store.requirements()['read']
    preview = dict(work=work, state='active', scope_preview=True, title=head.payload['title'],
                   scope=plan.payload['scope'], existing_checks=plan.payload['checks'], excludes=plan.payload['excludes'],
                   first_scope_addition=first, receipt=receipt, **delta)
    return preview, head, plan, observed


def apply(service, work, operation, edit, create, checks, reason, receipt, statement):
    def inspect():
        return review(service, work, edit, create, checks, reason)
    preview, head, prior, observed = inspect()
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
        approval = record('work.approval', dict(work=work, workspace=data['workspace'], statement=statement, **delta),
                          {'plan':('decision',plan[0]), 'basis':('decision',head.ref)}, version=2)
        updated = service._head_record(plan[0], data, 'active', approval=approval[0], previous=head.ref)
        def recheck():
            require(inspect()[0]['receipt'] == receipt, 'scope-preview-stale')
        service._publish(operation, work, head.ref, updated, [*objects,*merged.objects,plan,approval],
                         import_id=operation, recheck=recheck)
    return dict(work=work, state='active', scope_added=True, **delta)

