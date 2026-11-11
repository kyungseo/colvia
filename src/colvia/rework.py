"""Flat, immutable attribution of submitted peer additions during ordinary rework.

Content agreement is not authorship or acceptance. Existing plans remain fixed;
only regular additions with a v1 submitted peer proof can augment comparison.
"""
from dataclasses import asdict
from .codec import RecordError,require
from .maps import read_map,scan_map
from .records import link,head_summary,decode_policy
from .tree import read_tree,canonical_entries
from .observation import changed_paths

MAX_PEERS=16
MAX_CANDIDATES=32
MAX_PATHS=1000
MAX_HEADS=1000
DISPLAY_LIMIT=30
CONTEXT=('root','kind','common','gitdir','containers','nested','opaque')


class PathIndex:
    """Exact and ancestor queries linear in path depth, not scope cross-products."""
    def __init__(self,paths):
        self.exact=set();self.ancestors=set()
        for path in paths:self.add(path)
    def add(self,path):
        folded=path.casefold();self.exact.add(folded);parts=folded.split('/')
        self.ancestors.update('/'.join(parts[:n]) for n in range(1,len(parts)))
    def overlaps(self,path):
        folded=path.casefold();parts=folded.split('/')
        return folded in self.ancestors or any('/'.join(parts[:n]) in self.exact for n in range(1,len(parts)+1))


def eligible_path(path):
    # Ordinary observation has no shared agent-instruction classifier. Exclude
    # hidden paths and these known entry names; never claim arbitrary semantic detection.
    names={'agents.md','agents.override.md','claude.md','claude.local.md','gemini.md'}
    return not any(p.startswith('.') or p in names for p in path.casefold().split('/'))


def attribution(result,load):
    if result is None or result.ref.version==1:return {}
    require(result.ref.version==2,'unknown-required-kind')
    values=read_map(link(result,'attribution'),load,entry_limit=MAX_PATHS)
    require(0<len(values)<=MAX_PATHS and len(set(values.values()))<=MAX_PEERS,'attribution-limit')
    require(all(ref.kind=='work.submission' and ref.version==1 for ref in values.values()),'peer-attribution-nested')
    return values


class ProofMismatch(RecordError):
    def __init__(self,code,paths=()):super().__init__(code);self.paths=tuple(sorted(set(paths)))


def _proof_entries(service,plan,adopted,load,baseline,entries,after_entries,registration,policy,context):
    """One semantic proof for sealed audit/import and current live diagnosis."""
    def check(ok,code,paths=()):
        if not ok:raise ProofMismatch(code,paths)
    check(registration==link(baseline,'workspace'),'attribution-registration-mismatch')
    check(policy==decode_policy(link(baseline,'policy'),load),'attribution-policy-changed')
    check(all(context[k]==baseline.payload[k] for k in CONTEXT),'attribution-context-changed')
    check(0<len(adopted)<=MAX_PATHS and len(set(adopted.values()))<=MAX_PEERS,'attribution-limit')
    before={e['path']:e for e in entries};after={e['path']:e for e in after_entries}
    baseline_index=PathIndex(before);scope_index=PathIndex(plan.payload['scope'])
    groups={};adopted_index=PathIndex(())
    for path,ref in adopted.items():
        check(not adopted_index.overlaps(path),'attribution-path-overlap',[path])
        adopted_index.add(path);groups.setdefault(ref,[]).append(path)
    # No two revisions of one peer may silently advance carried attribution.
    peers={};work_ids=set()
    for ref,paths in groups.items():
        check(ref.kind=='work.submission' and ref.version==1,'peer-attribution-nested',paths)
        peer=service._object(ref,load);pp=service._object(link(peer,'plan'),load)
        check(pp.payload['work']!=plan.payload['work'] and pp.payload['work'] not in work_ids,'attribution-peer-ambiguous',paths)
        work_ids.add(pp.payload['work']);peers[ref]=(pp,peer)
    added=[]
    for ref,paths in groups.items():
        pp,peer=peers[ref]
        check(pp.payload['workspace']==plan.payload['workspace'],'attribution-workspace-mismatch',paths)
        check(not any(scope_index.overlaps(p) for p in pp.payload['scope']),'attribution-scope-overlap',paths)
        service._validate_result(pp,peer,load)
        pb,pentries=service._baseline(pp,load);po=service._object(link(peer,'observation'),load)
        check(link(pb,'workspace')==link(po,'workspace')==link(baseline,'workspace'),'attribution-registration-mismatch',paths)
        check(link(pb,'policy')==link(po,'policy')==link(baseline,'policy'),'attribution-policy-changed',paths)
        check(all(po.payload[k]==pb.payload[k]==baseline.payload[k] for k in CONTEXT),'attribution-context-changed',paths)
        pbefore={e['path'] for e in pentries};pafter={e['path']:e for e in read_tree(link(po,'tree'),load)}
        mismatches=[p for p in pp.payload['scope'] if after.get(p)!=pafter.get(p)]
        check(not mismatches,'attribution-peer-scope-changed',mismatches)
        peer_scope=frozenset(pp.payload['scope']);peer_changed=frozenset(peer.payload['changed'])
        for path in paths:
            check(path not in before and path not in pbefore and path in peer_scope and path in peer_changed,'attribution-not-added',[path])
            entry=pafter.get(path)
            check(entry is not None and entry['kind']=='regular' and entry==after.get(path) and eligible_path(path),'attribution-entry-mismatch',[path])
            check(not baseline_index.overlaps(path) and not scope_index.overlaps(path),'attribution-path-overlap',[path])
            added.append(entry)
    return canonical_entries([*entries,*added])


def effective_entries(service,plan,result,load):
    """Immutable proof; never consult current heads or the live filesystem."""
    baseline,entries=service._baseline(plan,load)
    if result.ref.version==1:return entries
    adopted=attribution(result,load);previous=link(result,'previous')
    require(previous is not None,'attribution-rework-required');older=service._object(previous,load)
    require(older.payload['work']==plan.payload['work'] and link(older,'plan')==plan.ref and
            older.payload['revision']+1==result.payload['revision'],'submission-sequence-mismatch')
    carried=attribution(older,load)
    require(all(adopted.get(p)==ref for p,ref in carried.items()),'attribution-protection-removed')
    observation=service._object(link(result,'observation'),load)
    return _proof_entries(service,plan,adopted,load,baseline,entries,read_tree(link(observation,'tree'),load),
                          link(observation,'workspace'),decode_policy(link(observation,'policy'),load),observation.payload)


def changes(before,after,scope=None):
    first={e['path']:e for e in before};second={e['path']:e for e in after}
    return [dict(path=p,change='addition' if p not in first else 'deletion' if p not in second else 'modification')
            for p in changed_paths(before,after) if scope is None or p in scope]


def bounded(items):
    return dict(items=items[:DISPLAY_LIMIT],total=len(items),omitted=max(0,len(items)-DISPLAY_LIMIT))


class SubmissionBlocked(RecordError):
    def __init__(self,code,items,reason,next_action=None):
        super().__init__(code)
        self.details={'status':'blocked',**bounded(items),'reason':reason,
            'next_action':next_action or '표시된 변경의 출처와 범위를 확인해 주세요. 승인되지 않은 변경은 보존한 채 별도 계획으로 다루며, 현재 작업의 범위를 넓혀야 한다면 그 차이만 확인합니다.'}


def _policy_items(previous,current):
    before={s.origin:s for s in previous.sources};after={s.origin:s for s in current.sources}
    def label(origin):
        if origin.startswith('workspace:'):return origin[len('workspace:'):]
        return 'Git info/exclude' if origin=='git:info/exclude' else 'Git 전역 제외 파일'
    items=[dict(path=label(p),change='addition' if p not in before else 'deletion' if p not in after else 'modification')
           for p in sorted(before.keys()|after.keys()) if before.get(p)!=after.get(p)]
    return items or [dict(path='Git 관측 설정 또는 작업 폴더 연결',change='modification')]


def _context_items(previous,current):
    items=[]
    for field in ('containers','nested'):
        before=set(previous[field]);after=set(current[field])
        items.extend(dict(path=p,change='addition' if p in after else 'deletion',reason='structural-context-changed') for p in sorted(before^after))
    labels={'root':'작업 폴더 위치','kind':'프로젝트 종류','common':'Git 공용 위치','gitdir':'Git 작업 폴더 연결','opaque':'링크·submodule 상태'}
    items.extend(dict(path=label,change='modification',reason='structural-context-changed') for field,label in labels.items() if previous[field]!=current[field])
    return items


def _live_proof(service,plan,adopted,baseline,original,current):
    registration,_,_=service.workspace.verify()
    context={k:(asdict(getattr(current.topology,k)) if getattr(current.topology,k) else None) for k in ('root','common','gitdir')}
    context.update(kind=current.topology.kind,containers=sorted(current.structural.containers),nested=sorted(current.structural.nested),opaque=[[p,list(v)] for p,v in current.opaque])
    try:
        return _proof_entries(service,plan,adopted,service.store.load,baseline,original,current.snapshot.entries,registration,current.policy,context)
    except ProofMismatch as exc:
        if exc.code=='attribution-policy-changed':items=_policy_items(decode_policy(link(baseline,'policy'),service.store.load),current.policy)
        elif exc.code=='attribution-context-changed':items=_context_items(baseline.payload,context)
        elif exc.code=='attribution-registration-mismatch':items=[dict(path='작업 폴더 등록 정보',change='modification')]
        else:
            deltas={i['path']:i for i in changes(original,current.snapshot.entries)}
            items=[deltas.get(p,dict(path=p,change='proof-mismatch')) for p in exc.paths]
        if exc.code=='attribution-peer-ambiguous':
            for item in items:
                if item['path'] in adopted:
                    peer=service._object(adopted[item['path']]);pp=service._object(link(peer,'plan'))
                    item.update(peer_title=pp.payload['title'],peer_work=pp.payload['work'])
        reasons={'attribution-context-changed':'등록된 작업 폴더 경계나 프로젝트 연결 구조가 달라졌습니다.',
                 'attribution-registration-mismatch':'작업 폴더 등록 정보가 대조한 기준과 다릅니다.',
                 'attribution-peer-ambiguous':'이전에 대조한 작업의 다른 제출본이 함께 필요해 자동으로 이어갈 수 없습니다. 기존 근거를 새 판본으로 바꾸지 않았습니다.',
                 'attribution-peer-scope-changed':'다른 작업의 승인 범위 전체가 대조한 제출본과 일치하지 않습니다.',
                 'attribution-policy-changed':'파일을 포함하거나 제외하는 정책이 달라 추가 파일을 구분하지 못했습니다.',
                 'attribution-path-overlap':'추가 파일의 경로가 기존 보호 범위와 겹칩니다.'}
        raise SubmissionBlocked(exc.code,items,reasons.get(exc.code,'추가 파일의 제출 근거를 현재 상태와 일치한다고 확인하지 못했습니다.'),
            '현재 수정본과 다른 작업의 파일을 보존하세요. 기존 대조 근거를 자동으로 갱신하지 않습니다. 변경 이유와 새 작업 범위가 필요한지 확인한 뒤 이어갈 방법을 정합니다.') from exc


def select(service,head,plan,current):
    """Live discovery, bounded current heads only. No records are written."""
    load=service.store.load;baseline,original=service._baseline(plan)
    previous=service._object(link(head,'result')) if link(head,'result') else None
    carried=attribution(previous,load);entries=effective_entries(service,plan,previous,load) if carried else original
    scope=frozenset(plan.payload['scope']);scope_index=PathIndex(scope)
    outside=[i for i in changes(entries,current.snapshot.entries) if i['path'] not in scope]
    adopted=dict(carried);pinned={}
    if not outside:
        if adopted:entries=_live_proof(service,plan,adopted,baseline,original,current)
        return entries,adopted,pinned,None
    if previous is None or head.payload['phase']!='active' or link(head,'decision') is None:
        raise SubmissionBlocked('outside-scope-change',outside,'처음 제출하는 작업의 범위 밖 변경입니다.')
    decision=service._object(link(head,'decision'));require(decision.payload['action']=='request-changes','rework-decision-required')
    offending=[i for i in outside if i['change']!='addition' or not eligible_path(i['path'])]
    if offending:
        for item in offending:
            item['requirement']='unchanged-from-original' if item['change']!='addition' else 'separate-scope-decision'
            if item['path'] in carried:
                peer=service._object(carried[item['path']]);pp=service._object(link(peer,'plan'))
                item.update(attributed=True,peer_work=pp.payload['work'],peer_title=pp.payload['title'],peer_revision=peer.payload['revision'],requirement='match-peer-submission')
        carried_change=any(i.get('attributed') for i in offending)
        raise SubmissionBlocked('outside-scope-change',offending,'보호된 파일이 바뀌었습니다. 파일별 대조 조건을 확인해 주세요.' if carried_change else '기존 보호 파일의 변경·삭제 또는 자동 구분할 수 없는 파일이 있습니다.',
            '현재 수정본과 변경된 파일을 모두 보존하세요. 파일마다 표시한 대조 조건을 확인하세요. 자동 복원하지 않으며, 바뀐 내용을 유지하려면 새 작업 범위를 별도로 확인합니다.' if carried_change else None)
    require(len(outside)+len(carried)<=MAX_PATHS,'attribution-limit')
    if current.policy!=decode_policy(link(baseline,'policy'),load):
        raise SubmissionBlocked('attribution-policy-changed',_policy_items(decode_policy(link(baseline,'policy'),load),current.policy),'파일을 포함하거나 제외하는 정책이 달라 추가 파일을 구분하지 못했습니다.')
    current_entries={e['path']:e for e in current.snapshot.entries};wanted={i['path'] for i in outside};matches={p:[] for p in wanted};structural_skips={}
    index=PathIndex(e['path'] for e in entries)
    overlap=[i for i in outside if index.overlaps(i['path']) or scope_index.overlaps(i['path'])]
    if overlap:raise SubmissionBlocked('outside-scope-change',overlap,'추가 파일의 경로가 기존 보호 범위와 겹칩니다.')
    root=service.store.root().ref;count=0;candidates_read=0
    for key,ref in scan_map(service.store.root().heads,load):
        if not key.startswith('work:'):continue
        count+=1;require(count<=MAX_HEADS,'attribution-discovery-limit')
        if key=='work:'+plan.payload['work']:continue
        ph,pp,pr,_=head_summary(ref,load)
        if ph.payload['workspace']!=plan.payload['workspace'] or ph.payload['phase'] not in ('review','completed') or pr is None or pr.ref.version!=1:continue
        candidates=wanted.intersection(pp.payload['scope'])
        if not candidates:continue
        candidates_read+=1;require(candidates_read<=MAX_CANDIDATES,'attribution-discovery-limit')
        if any(scope_index.overlaps(p) for p in pp.payload['scope']):continue
        po=service._object(link(pr,'observation'));pafter={e['path']:e for e in read_tree(link(po,'tree'),load)}
        if any(current_entries.get(p)!=pafter.get(p) for p in pp.payload['scope']):continue
        pb,pentries=service._baseline(pp);pbase={e['path'] for e in pentries}
        if link(pb,'policy')!=link(po,'policy') or link(pb,'policy')!=link(baseline,'policy'):continue
        if link(pb,'workspace')!=link(baseline,'workspace') or link(po,'workspace')!=link(baseline,'workspace'):continue
        if any(po.payload[k]!=pb.payload[k] or po.payload[k]!=baseline.payload[k] for k in CONTEXT):
            causes=_context_items(pb.payload,po.payload)+_context_items(baseline.payload,po.payload)
            for path in candidates:structural_skips[path]=causes
            continue
        for path in candidates:
            entry=pafter.get(path)
            if path not in pbase and path in pr.payload['changed'] and entry and entry['kind']=='regular':matches[path].append((key,ref,pr.ref))
    require(service.store.root().ref==root,'attribution-heads-changed')
    unresolved=[{**i,'reason':('structural-context-changed' if i['path'] in structural_skips else 'unattributed-addition') if not matches[i['path']] else 'ambiguous-addition'} for i in outside if len(matches[i['path']])!=1]
    if unresolved:
        causes={i['path']:i for u in unresolved if u['reason']=='structural-context-changed' for i in structural_skips[u['path']]}
        reason='다른 작업의 제출 근거는 있지만 등록된 작업 폴더 경계나 연결 구조가 달라 추가 파일을 대조하지 못했습니다.' if causes else '추가 파일을 현재 내용과 일치하는 다른 작업의 제출 근거로 확인하지 못했습니다.'
        raise SubmissionBlocked('outside-scope-change',unresolved+list(causes.values()),reason)
    for path,values in matches.items():
        key,headref,resultref=values[0];adopted[path]=resultref;pinned[key]=headref
    require(len(set(adopted.values()))<=MAX_PEERS,'attribution-limit')
    entries=_live_proof(service,plan,adopted,baseline,original,current)
    return entries,adopted,pinned,root


def attribution_summary(service,result):
    values=attribution(result,service.store.load)
    return {'meaning':'다른 작업의 제출 근거와 현재 파일을 대조한 추가 파일이며, 이 작업의 수정·수락 대상은 아닙니다.',
            **bounded([{'path':p,'work':service._object(ref).payload['work']} for p,ref in sorted(values.items())])}


def resume_context(service,head,plan):
    decision=service._object(link(head,'decision'));result=service._object(link(head,'result'))
    value={'approved_request':decision.payload['statement'],'approved_scope':plan.payload['scope'],
           'checks':plan.payload['checks'],'last_submitted_revision':result.payload['revision'],
           'last_submission_status':'retained-history-not-pending-review',
           'check_execution_status':'not-established-by-this-read',
           'diagnosis_basis':'current observation; not a replay of a past failure',
           'next_action':'이미 승인한 수정 범위는 다시 승인받지 않습니다. 남은 검사를 수행하고 같은 작업에 수정본을 제출하세요.'}
    try:
        carried=attribution(result,service.store.load);_,_,current=service._observe_from_plan(plan,carried)
        previous=service._object(link(result,'observation'))
        value['differences']=bounded(changes(read_tree(link(previous,'tree'),service.store.load),current.snapshot.entries,frozenset(plan.payload['scope'])))
        _,adopted,_,_=select(service,head,plan,current)
        value['submission_check']={'status':'scope-checked','attributed_additions':bounded([{'path':p} for p in sorted(adopted)]),
                                   'all_checks_must_pass':bool(adopted)}
    except SubmissionBlocked as exc:
        value['submission_check']={'error':exc.code,**exc.details};value['next_action']=exc.details['next_action']
    except (RecordError,OSError) as exc:
        code=exc.code if isinstance(exc,RecordError) else 'workspace-access-unavailable'
        value['submission_check']={'status':'unavailable','error':code}
        value['next_action']='현재 변경을 안전하게 대조하지 못했습니다. 진단 원인을 확인하고 파일·기록을 보존한 채 중단하세요.'
    return value
