"""Group and member projections from one immutable published root."""
from .codec import require, RecordError
from .records import link, head_summary
from .maps import map_get, read_map
from .effects import PENDING
from .tree import read_tree
from . import group_records as gr


def snapshot(ref,heads,load,workspace,*,details=True):
    selected=gr.get(ref,load); plan=gr.plan_for(ref,load); group=plan.payload['group']; members=[]
    candidate=None; review=None
    if ref.kind=='group.effect':
        auth=gr.get(link(selected,'authorization'),load); review=gr.get(link(auth,'review'),load)
    elif ref.kind=='group.review': review=selected
    if review: candidate=gr.get(link(review,'candidate'),load)
    elif ref.kind=='group.candidate': candidate=selected
    stale=False
    candidate_heads=gr.member_refs(candidate,'head',plan,load) if candidate else None
    for i,work in enumerate(plan.payload['works']):
        current=map_get(heads,'work:'+work,load); require(current is not None,'group-member-head-missing')
        if ref.kind=='group.effect' and selected.payload['state']=='completed':
            current_head,_,_,decision=head_summary(current,load)
            require(current_head.payload['phase']=='completed' and decision is not None and link(decision,'authorization')==link(selected,'authorization'),'group-terminal-selection-mismatch')
        h,p,r,_=head_summary(candidate_heads[i] if candidate else current,load)
        if candidate and ref.kind!='group.effect': stale=stale or h.ref!=current
        before={}; after={}
        if details:
            baseline=gr.get(link(p,'baseline'),load); before={e['path']:e for e in read_tree(link(baseline,'tree'),load)}
            after={e['path']:e for e in read_tree(link(gr.get(link(r,'observation'),load),'tree'),load)} if r else before
        source=gr.get(link(gr.get(link(p,'baseline'),load),'workspace'),load)
        item=dict(source_path=source.payload['root']['path'],source_path_retained=True,work=work,title=p.payload['title'],workspace=p.payload['workspace'],head=h.ref.as_dict(),plan=p.ref.as_dict(),
                  state=h.payload['phase'],goal=p.payload['goal'],scope=p.payload['scope'],checks=p.payload['checks'],excludes=p.payload['excludes'])
        if r:
            item.update(reported_checks=r.payload['checks'],revision=r.payload['revision'],submission=r.ref.as_dict(),summary=r.payload['summary'],
                        files=[dict(path=path,before=before.get(path),after=after.get(path)) for path in r.payload['changed']] if details else [],
                        submitted_paths=r.payload['changed'][:5],submitted_file_count=len(r.payload['changed']))
        members.append(item)
    checks=[]
    if review:
        for name,e in read_map(link(review,'evidence'),load).items():
            value=gr.get(e,load)
            from .bodies import body_bytes
            logs={}; log_metadata={}
            if details:
                for channel in ('stdout','stderr'):
                    descriptor=gr.get(link(value,channel),load)
                    log_metadata[channel]=dict(size=descriptor.payload['size'],sha256=descriptor.payload['sha256'],truncated=descriptor.payload['size']>4096)
                    prefix=bytearray()
                    for chunk in body_bytes(link(value,channel),load):
                        prefix.extend(chunk[:4096-len(prefix)])
                        if len(prefix)==4096: break
                    logs[channel]=prefix.decode('utf-8',errors='replace')
            checks.append(dict(name=name,status='passed' if gr.passed(value) else 'blocked',**{k:v for k,v in value.payload.items() if k not in ('links','name')},evidence=e.as_dict(),logs=logs,log_metadata=log_metadata))
    count=len(members)
    if ref.kind=='group.plan': state='planned'; bucket='plan'; action=f'{count}개 계획과 통합 검사 범위 승인하기'
    elif ref.kind=='group.effect':
        state=selected.payload['state']; bucket='unavailable' if state=='pending' else 'continue'
        action='반영 현황 확인 후 같은 요청으로 재개하기 — 수락 전' if state=='pending' else f'{count}개 결과 수락과 원래 폴더 반영 완료'
        require(state!='pending' or map_get(heads,PENDING,load)==ref,'group-pending-selection-mismatch')
    elif candidate:
        state='review' if review and all(c['status']=='passed' for c in checks) and all(c['status']=='passed' for m in members for c in m.get('reported_checks',[])) and not stale else 'checks-required'
        bucket='review' if state=='review' else 'unavailable'
        action=f'{count}개 제출본과 통합 검사 결과를 보고 함께 수락·반영하기' if state=='review' else '최신 제출본으로 통합 후보와 필수 검사 준비하기'
    else: state='approved'; bucket='continue'; action='각 작업 폴더에서 승인된 계획 진행하기'
    return dict(kind='work-group',work=group,work_group=group,title=' + '.join(m['title'] for m in members),group=bucket,
                workspace=plan.payload['destination'],here=workspace==plan.payload['destination'],state=state,next_action=action,
                members=members,member_count=count,required_checks=plan.payload['checks'],checks=checks,stale=stale,
                destination=plan.payload['destination'],head=ref.sha256,accepted=count if state=='completed' else 0)


def view(service,group):
    root=service.store.root(); ref=map_get(root.heads,gr.key(group),service.store.load); require(ref is not None,'group-not-found')
    require(gr.plan_for(ref,service.store.load).payload['destination']==service.destination.workspace,'group-wrong-destination')
    value=snapshot(ref,root.heads,service.store.load,service.destination.workspace)
    if ref.kind!='group.effect': value['dissolve_receipt']=service._receipt('dissolve',group,ref)
    if ref.kind=='group.plan': value['receipt']=service._receipt('approve',group,ref)
    if ref.kind=='group.review' and value['state']=='review': value['receipt']=service._receipt('accept',group,ref)
    value['destination_path']=str(service.destination.root)
    if ref.kind=='group.effect':
        from .group_effects import _parts, _manifest, _states, _live
        from .storage.sqlite import ValidationView
        effect,auth,review,parts=_parts(service,ref,service.store.load)
        value.update(application=effect.payload['application'],request=auth.payload['request'],receipt=auth.payload['receipt'],actor=auth.payload['actor'],statement=auth.payload['statement'])
        value['blocked']=None
        try:
            port=service._port()
            with port.exclusion(create=False):
                if effect.payload['state']=='pending': _live(service,ValidationView(root,service.store.load),effect,auth,parts)
                states=_states(service,port,effect,parts)
                value['paths']=[dict(path=item['path'],state=state) for item,state in zip(parts[6],states)]
        except (OSError,RecordError) as error:
            value['blocked']=error.code if isinstance(error,RecordError) else 'effect-path-unavailable'
    require(service.store.root().ref==root.ref,'group-view-changed')
    return value


def content(service,group,work,path):
    from .bodies import body_bytes
    root=service.store.root(); selected=service._selected(group)
    if selected.ref.kind=='group.effect': selected=gr.get(link(gr.get(link(selected,'authorization'),service.store.load),'review'),service.store.load)
    candidate=gr.get(link(selected,'candidate'),service.store.load) if selected.ref.kind=='group.review' else selected
    require(candidate.ref.kind=='group.candidate','group-candidate-required')
    members=gr.candidate_parts(candidate.ref,service.store.load)[-1]
    chosen=[(p,r) for _,p,r in members if p.payload['work']==work]; require(len(chosen)==1,'group-member-required')
    plan,result=chosen[0]; require(path in plan.payload['scope'],'group-path-outside-scope')
    value=dict(group=group,work=work,path=path,submission=result.ref.as_dict(),revision=result.payload['revision'])
    for name,obj,field in [('before',plan,'before'),('after',result,'after')]:
        ref=map_get(link(obj,field),path,service.store.load)
        if ref is None: value[name]=None; continue
        descriptor=gr.get(ref,service.store.load); info={k:descriptor.payload[k] for k in ('size','sha256')}
        if info['size']<=65536:
            try: info['text']=b''.join(body_bytes(ref,service.store.load)).decode('utf-8')
            except UnicodeDecodeError: info['binary']=True
        else: info['text_unavailable']='content exceeds text preview limit'
        value[name]=info
    require(service.store.root().ref==root.ref,'group-view-changed'); return value
