"""Explicit decisions about an independent Work. Selecting a Work is read-only."""
import hashlib
import time

from . import progress
from .codec import canonical_bytes, decode_envelope, require
from .effects import guard
from .execution.schema import CLOSED as EXECUTION_CLOSED
from .graph import Schema
from .maps import map_get, scan_map
from .records import _head, fields, head_summary, link, one, record, text
from .work import work_key

PREFIX = 'work-lifecycle:'
ONGOING = ('planned', 'approved', 'active', 'review', 'paused')
CARRIED = ('plan', 'approval', 'result', 'decision', 'context')
ACTIONS = ('pause', 'resume', 'discard', 'replace')
EXTRA = ('action', 'reason', 'next_action', 'origin', 'files', 'target')

def resulting_phase(action, phase, origin):
    if action == 'pause':
        require(phase in ('active', 'review'), 'work-not-pausable')
        return 'paused'
    if action == 'resume':
        require(phase == 'paused' and origin in ('active', 'review'), 'work-not-paused')
        return origin
    require(action in ('discard', 'replace') and phase in ONGOING, 'work-not-discardable')
    return 'discarded'

def short(value):
    text(value, 2048)
    require(value.strip() and value.isprintable(), 'invalid-record-text')

def schema(base):
    targets = dict(base.targets, replacement=frozenset({'work.head'}))
    return Schema('work.head', 2, dict(base.fields, replacement='decision'),
                  validate_payload, targets, content=validate_content)

def validate_payload(p):
    fields(p, {'work','workspace','title','phase','archived', *EXTRA})
    require(p['action'] in ACTIONS and p['origin'] in ONGOING[:-1], 'invalid-lifecycle-state')
    # The inherited record must still satisfy the exact original phase contract.
    _head({**{k:v for k,v in p.items() if k not in EXTRA}, 'phase':p['origin'],
           'links':{k:v for k,v in p['links'].items() if k!='replacement'}})
    require(not p['archived'] and not p['links']['context'], 'lifecycle-independent-work-only')
    short(p['reason'])
    if p['next_action'] != '':
        short(p['next_action'])
    one(p, 'previous')
    one(p, 'replacement', True)
    require(isinstance(p['target'], str) and bool(p['target']) == bool(p['links']['replacement'])
            == (p['action']=='replace'), 'invalid-replacement')
    progress.validate_fingerprints(p['files'])
    if p['action'] != 'pause':
        require(not p['files'], 'invalid-progress-files')

def validate_content(ref, load):
    head = decode_envelope(ref, load(ref))
    prior,plan,_,_ = head_summary(link(head,'previous'), load)
    p = head.payload
    origin = prior.payload.get('origin') if prior.payload['phase']=='paused' else prior.payload['phase']
    require(p['origin']==origin and p['phase']==resulting_phase(p['action'],prior.payload['phase'],origin)
            and all(prior.payload[k]==p[k] for k in ('work','workspace','title'))
            and all(link(prior,k)==link(head,k) for k in CARRIED), 'lifecycle-history-mismatch')
    if p['action']=='pause':
        require(set(p['files'])==set(plan.payload['scope'][:progress.MAX_PATHS]), 'invalid-progress-files')
    if p['action']=='replace':
        target,_,_,_=head_summary(link(head,'replacement'),load)
        require(target.payload['work']==p['target'] and p['target']!=p['work']
                and target.payload['phase'] in ONGOING and not link(target,'context'), 'invalid-replacement')

def available(service, head, snapshot):
    from .group_guard import guard as group_guard
    group_guard(service.store,head.payload['work'])
    require(not link(head,'context'), 'lifecycle-independent-work-only')
    grant = service.store.head('grant:'+head.payload['work'])
    require(not grant or service._object(grant).payload['state']!='active', 'lifecycle-grant-in-use')
    guard(service.store)
    for key, ref in scan_map(snapshot.heads, service.store.load):
        if key.startswith('execution-prepared:') and ref.kind=='execution.grant':
            grant_record = service._object(ref)
            if link(grant_record,'head')==head.ref:
                run = service.store.head('execution:'+grant_record.payload['run'])
                if run is None:
                    deadline=grant_record.payload['contract']['scope']['limits']['expires_wall_ns']
                    require(time.time_ns() >= deadline, 'lifecycle-execution-prepared')
                else:
                    require(service._object(run).payload['status'] in EXECUTION_CLOSED, 'lifecycle-execution-prepared')
        if key.startswith('delivery-prepared:') and ref.kind=='delivery.request':
            request = service._object(ref)
            if link(request,'head')==head.ref and request.payload['action']!='inspect':
                state = service.store.head('delivery:'+request.payload['delivery'])
                if state:
                    require(service._object(state).payload['phase'] in ('finished','cancelled','failed'),
                            'lifecycle-delivery-prepared')
                else:
                    require(time.time_ns() >= request.payload['deadline_ns'], 'lifecycle-delivery-prepared')
        if key.startswith('application:') and ref.kind=='worker.binding':
            binding = service._object(ref)
            require(link(binding,'source_head')!=head.ref and binding.payload['destination']!=head.payload['workspace'],
                    'lifecycle-application-prepared')

def proposal(service, work, action, reason, next_action='', target=''):
    require(action in ACTIONS, 'invalid-lifecycle-state')
    short(reason)
    if next_action: short(next_action)
    require(bool(target)==(action=='replace') and target!=work, 'invalid-replacement')
    store=service.store
    snapshot=store.root()
    current, head=service._head(work)
    available(service,head,snapshot)
    phase=head.payload['phase']
    origin=head.payload['origin'] if phase=='paused' else phase
    state=resulting_phase(action,phase,origin)
    plan=service._object(link(head,'plan'))
    scope=plan.payload['scope']
    files=progress.fingerprints(service.workspace,scope)
    before=link(plan,'before')
    changed=[]
    for path,actual in files.items():
        body=map_get(before,path,store.load)
        original=service._object(body).payload['sha256'] if body else progress.MISSING
        status=progress.difference(original,actual)
        if status!='unchanged':changed.append(dict(path=path,status=status))
    replacement=None
    if target:
        replacement,other=service._head(target,same_workspace=False)
        require(other.payload['phase'] in ONGOING, 'invalid-replacement')
        available(service,other,snapshot)
    note=store.head('progress:'+work)
    registration,_,_=service.workspace.verify()
    shown=dict(work=work,title=head.payload['title'],action=action,reason=reason,next_action=next_action,target=target,
               from_state=phase,to_state=state,scope=scope,files=files,changes_from_plan=changed,
               unobserved_paths=len(scope)-len(files),lifecycle_preview=True)
    if replacement:
        shown.update(target_title=other.payload['title'],target_state=other.payload['phase'])
    if phase=='paused':
        shown['since_pause']=[dict(path=p,status=progress.difference(v,files[p]))
                              for p,v in head.payload['files'].items()]
    # Positions in a different Work never constitute a new scope approval.
    basis=dict(proposal=shown,head=current.as_dict(),registration=registration.as_dict(),
               target_head=replacement.as_dict() if replacement else None,note=note.as_dict() if note else None)
    digest=hashlib.sha256(canonical_bytes(basis)).hexdigest()
    shown['receipt']=service._receipt('lifecycle:'+digest,work,current)
    require(store.root().ref==snapshot.ref,'lifecycle-preview-stale')
    return shown,head,replacement,snapshot

def apply(service, work, action, reason, next_action, target, receipt, operation):
    shown,old,replacement,snapshot=proposal(service,work,action,reason,next_action,target)
    require(receipt==shown['receipt'],'lifecycle-preview-stale')
    p=old.payload
    origin=p['origin'] if p['phase']=='paused' else p['phase']
    data=dict(work=work,workspace=p['workspace'],title=p['title'],archived=False,phase=shown['to_state'],
              action=action,origin=origin,reason=reason,next_action=next_action,target=target,
              files=shown['files'] if action=='pause' else {})
    edges={k:('decision',link(old,k)) for k in CARRIED}
    edges.update(previous=('provenance',old.ref),replacement=('decision',replacement))
    pair=record('work.head',data,edges,version=2)
    def validate(view):
        guard(view)
        from .group_guard import guard as group_guard
        group_guard(view,work)
        if target: group_guard(view,target)
        require(view.root().ref==snapshot.ref,'lifecycle-preview-stale')
        service._validate_head(pair[0],view)
        validate_content(pair[0],view)
        service.workspace.verify()
        require(progress.fingerprints(service.workspace,shown['scope'])==shown['files'],'lifecycle-preview-stale')
    service.store.commit_heads(operation=operation,expected={work_key(work):old.ref,PREFIX+work:service.store.head(PREFIX+work)},
        changes={work_key(work):pair[0],PREFIX+work:pair[0]},objects=[pair],validate=validate)
    return dict(work=work,state=data['phase'],lifecycle_action=action,target=target)

def detail(service, work, head):
    store=service.store
    snapshot = store.root()
    last=store.head(PREFIX+work)
    value={}
    if last:
        event=service._object(last)
        require(event.ref.kind=='work.head' and event.ref.version==2 and event.payload['work']==work,'lifecycle-history-mismatch')
        value['lifecycle']={k:event.payload[k] for k in ('action','reason','origin','next_action','target')}
        if head.payload['phase']=='paused' and head.payload['workspace']==service.workspace.workspace:
            saved=head.payload['files']
            value['since_pause']=progress.compare_files(service.workspace,sorted(saved),saved)
    sources=[]
    for key,ref in scan_map(snapshot.heads,store.load):
        if key.startswith(PREFIX):
            event=service._object(ref)
            if event.payload['target']==work:
                sources.append(event.payload['work'])
    if sources:value['replaces']=sources
    note=store.head('progress:'+work)
    if note and not progress.eligible(head):
        obj=service._object(note)
        require(obj.payload['work']==work and obj.payload['workspace']==head.payload['workspace'],'progress-work-mismatch')
        value['saved_progress']={k:obj.payload[k] for k in progress.NOTE_FIELDS}
    require(store.head(work_key(work))==head.ref and store.root().ref==snapshot.ref,'lifecycle-preview-stale')
    return value
