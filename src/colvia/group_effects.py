"""One native manifest, all terminal decisions, request-keyed forward recovery."""
from uuid import uuid4
from .codec import require, RecordError
from .records import record, link, text
from .graph import validate_closure
from .effects import guard, PENDING
from .work import work_key
from .storage.sqlite import ValidationView, _token
from .worker_state import classify, require_initial
from .bodies import body_bytes
from . import group_records as gr


def request_key(request): _token(request); return 'group-request:'+request


def _parts(service,ref,load):
    validate_closure([ref],load,service.work.registry,service.work.closure)
    effect=service._object(ref,load); require(ref.kind=='group.effect','group-effect-required')
    auth,review=gr.validate_authorization(link(effect,'authorization'),load)
    return effect,auth,review,gr.candidate_parts(link(review,'candidate'),load)


def _manifest(service,effect,load=None):
    obj=service._object(link(effect,'manifest'),load)
    return {k:v for k,v in obj.payload.items() if k!='links'}


def _states(service,port,effect,parts,*,load=None,cancelling=False):
    manifest=_manifest(service,effect,load)
    if cancelling: return tuple('pre' if port.cancellable(manifest,i) else 'unknown' for i in range(len(parts[6])))
    before,after=parts[4:6]; current=service._observe(parts[2],parts[3])
    scope=[path for _,plan,_ in parts[-1] for path in plan.payload['scope']]
    require(not classify(before,after,current.snapshot.entries,scope).outside,'worker-outside-scope-change')
    return tuple(port.state(manifest,i) for i in range(len(parts[6])))


def _live(service,view,effect,auth,parts):
    guard(view,expected_effect=effect.ref)
    group=parts[2].payload['group']; application=effect.payload['application']
    require(view.head(gr.key(group))==effect.ref and view.head(gr.application_key(application))==effect.ref and
            view.head(request_key(auth.payload['request']))==effect.ref,'group-effect-selection-changed')
    service._live_candidate(parts[0],view)


def _next(effect,state,works,progress=None,completed=None):
    links,objects=gr.member_links(effect.ref.version,'completed',works,completed)
    pair=record('group.effect',dict(application=effect.payload['application'],state=state),
        dict(links,authorization=('decision',link(effect,'authorization')),manifest=('integrity',link(effect,'manifest')),
             progress=('integrity',progress if progress is not None else link(effect,'progress')),previous=('provenance',effect.ref)),version=effect.ref.version)
    return pair,objects


def _publish(service,operation,port,effect,auth,review,parts,pair,*,objects=(),heads=None,cancelling=False):
    group=parts[2].payload['group']; app=effect.payload['application']; req=request_key(auth.payload['request'])
    state=service.work.registry.inspect(pair[0],pair[1],required=True).payload['state']
    terminal=state!='pending'
    expected={gr.key(group):effect.ref,gr.application_key(app):effect.ref,req:effect.ref,PENDING:effect.ref}
    changes={gr.key(group):review.ref if cancelling else pair[0],gr.application_key(app):pair[0],req:pair[0],PENDING:None if terminal else pair[0]}
    for h,plan,_ in parts[-1]:
        expected[work_key(plan.payload['work'])]=h.ref
        if heads: changes[work_key(plan.payload['work'])]=heads[plan.payload['work']]
    def validate(view):
        _live(service,view,effect,auth,parts)
        _parts(service,pair[0],view)
        states=_states(service,port,effect,parts,load=view,cancelling=cancelling)
        require(all(s in ({'pre'} if cancelling else {'post'} if terminal else {'pre','post','evacuated'}) for s in states),'group-terminal-state-mismatch')
        if heads:
            from .composition import validate_transition
            from .records import head_summary
            for work,ref in heads.items():
                service.work._validate_head(ref,view)
                h,p,r,_=head_summary(ref,view); validate_transition(expected[work_key(work)],h,p,r,view)
    service.store.commit_heads(operation=operation,expected=expected,changes=changes,objects=[*objects,pair],validate=validate)


def _outcome(effect,parts):
    return dict(group=parts[2].payload['group'],application=effect.payload['application'],state=effect.payload['state'],
                works=parts[2].payload['works'],accepted=len(parts[2].payload['works']) if effect.payload['state']=='completed' else 0)


def _run(service,port,ref,event):
    effect,auth,review,parts=_parts(service,ref,service.store.load)
    def check():
        view=ValidationView(service.store.root(),service.store.load)
        _live(service,view,effect,auth,parts); _states(service,port,effect,parts)
    check()
    previous=link(effect,'progress')
    last=service._object(previous).payload['index'] if previous else -1
    attempt='group-'+uuid4().hex
    for i in range(len(parts[6])):
        if i<=last:
            require(port.state(_manifest(service,effect),i)=='post','group-progress-state-changed'); continue
        try: port.apply_one(_manifest(service,effect),i,before_effect=check,event=event)
        except OSError: raise RecordError('effect-outcome-unknown') from None
        progress=record('worker.progress',dict(application=effect.payload['application'],index=i,stage='verified'),{'previous':('provenance',link(effect,'progress'))})
        pair,mapping=_next(effect,'pending',parts[2].payload['works'],progress[0])
        _publish(service,attempt+'-p'+str(i),port,effect,auth,review,parts,pair,objects=[progress,*mapping])
        effect=service._object(pair[0]); event('progress-published')
    try:
        for i in range(len(parts[6])): port.sync(_manifest(service,effect),i)
    except OSError: raise RecordError('effect-outcome-unknown') from None
    require(all(s=='post' for s in _states(service,port,effect,parts)),'group-terminal-state-mismatch')
    event('before-completion')
    objects=[]; heads={}
    for h,plan,result in parts[-1]:
        decision=record('work.decision',dict(work=plan.payload['work'],workspace=plan.payload['workspace'],action='accept',statement=auth.payload['statement']),
            dict(result=('decision',result.ref),authorization=('decision',auth.ref)),version=auth.ref.version+1)
        head=service.work._head_record(plan.ref,plan.payload,'completed',approval=link(h,'approval'),result=result.ref,decision=decision[0],previous=h.ref)
        objects.extend([decision,head]); heads[plan.payload['work']]=head[0]
    pair,mapping=_next(effect,'completed',parts[2].payload['works'],completed=tuple(heads[w] for w in parts[2].payload['works'])); objects.extend(mapping)
    _publish(service,attempt+'-complete',port,effect,auth,review,parts,pair,objects=objects,heads=heads)
    event('completed')
    return _outcome(service._object(pair[0]),parts)


def execute(service,*,operation,group,application,request,receipt,statement,actor='owner',event=lambda stage:None):
    _token(operation); _token(application); _token(request); text(statement); text(actor,256)
    require(application.startswith('group-'),'group-application-prefix-required')
    port=service._port()
    with port.exclusion():
        saved=service.store.head(request_key(request))
        if saved:
            effect,auth,review,parts=_parts(service,saved,service.store.load)
            require(parts[2].payload['group']==group and auth.payload['request_digest']==gr.request_digest(review.ref,receipt,request,actor,statement,application), 'group-request-mismatch')
            if effect.payload['state']=='completed': return _outcome(effect,parts)
            require(effect.payload['state']=='pending','group-request-cancelled')
            return _run(service,port,effect.ref,event)
        selected=service._selected(group)
        require(selected.ref.kind=='group.review','group-tested-review-required')
        gr.require_checks(selected,service.store.load)
        require(receipt==service._receipt('accept',group,selected.ref),'group-stale-receipt')
        require(service.store.head(gr.application_key(application)) is None and service.store.head('application:'+application) is None,'group-application-already-exists')
        candidate=service._object(link(selected,'candidate'))
        view=ValidationView(service.store.root(),service.store.load); guard(view)
        parts=service._live_candidate(candidate,view,source_files=True); service._initial(parts[2],view); service._prepared(parts[2],view)
        auth=record('group.authorization',dict(application=application,request=request,request_digest=gr.request_digest(selected.ref,receipt,request,actor,statement,application),receipt=receipt,actor=actor,statement=statement),{'review':('decision',selected.ref)},version=selected.ref.version)
        bodies=parts[7]
        def body(path):
            require(path in bodies,'group-post-body-required'); return body_bytes(bodies[path],service.store.load)
        try: prepared=port.prepare(application,parts[6],body)
        except RecordError as error:
            if error.code=='effect-staging-already-exists':
                raise RecordError('group-unreserved-staging-exists') from None
            raise
        event('staging-prepared')
        manifest=record('worker.manifest',prepared,{})
        member_links,mapping=gr.member_links(selected.ref.version,'completed',parts[2].payload['works'])
        pair=record('group.effect',dict(application=application,state='pending'),dict(member_links,authorization=('decision',auth[0]),manifest=('integrity',manifest[0]),progress=('integrity',None),previous=('provenance',None)),version=selected.ref.version)
        expected={gr.key(group):selected.ref,gr.application_key(application):None,request_key(request):None,PENDING:None}
        changes={k:pair[0] for k in expected}
        def validate(view):
            guard(view); service._live_candidate(candidate,view,source_files=True); service._prepared(parts[2],view)
            require(view.head('application:'+application) is None,'group-application-already-exists')
            effect,_,_,_= _parts(service,pair[0],view)
            require(all(s=='pre' for s in _states(service,port,effect,parts,load=view)),'group-initial-state-changed')
        service.store.commit_heads(operation='group-'+uuid4().hex+'-reserve',expected=expected,changes=changes,objects=[auth,manifest,*mapping,pair],validate=validate)
        event('reserved')
        return _run(service,port,pair[0],event)


def cancel(service,*,operation,group):
    selected=service._selected(group); require(selected.ref.kind=='group.effect','group-pending-effect-required')
    port=service._port()
    with port.exclusion():
        effect,auth,review,parts=_parts(service,selected.ref,service.store.load)
        require(effect.payload['state']=='pending','group-pending-effect-required')
        require(all(s=='pre' for s in _states(service,port,effect,parts,cancelling=True)),'worker-cancel-requires-all-pre')
        pair,mapping=_next(effect,'cancelled',parts[2].payload['works'])
        _publish(service,operation,port,effect,auth,review,parts,pair,objects=mapping,cancelling=True)
        return _outcome(service._object(pair[0]),parts)
