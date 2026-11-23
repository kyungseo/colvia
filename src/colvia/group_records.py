"""Version-pinned grouped decisions; legacy pairs and bounded member maps."""
import hashlib
from .codec import require, canonical_bytes
from .graph import Schema
from .records import fields, one, text, link, head_summary, record, MAP_KINDS, TREE_KINDS
from .storage.sqlite import _token, MAX_TOKEN_LENGTH
from .binding import _uuid
from .tree import logical_path, read_tree, build_tree
from .maps import read_map, build_map
from .worker_state import path_namespace, transitions


MAX_MEMBERS = 8
MEMBER_FIELDS = {'head':'heads', 'approval':'approvals', 'completed':'completed'}


def pinned_group_version(obj):
    require(all(edge.ref.version==obj.ref.version for edge in obj.edges
                if edge.ref.kind.startswith('group.')), 'group-record-version-mismatch')


def pinned_decision_version(obj):
    auth=link(obj,'authorization')
    require(auth is not None and auth.kind=='group.authorization' and
            (obj.ref.version,auth.version) in ((2,1),(3,2)), 'group-decision-version-required')


def member_refs(obj,field,plan,load):
    require(obj.ref.version==plan.ref.version, 'group-record-version-mismatch')
    works=plan.payload['works']
    if obj.ref.version==1:
        return [link(obj,field+str(i)) for i in range(2)]
    values=read_map(link(obj,MEMBER_FIELDS[field]),load,entry_limit=len(works))
    kind='work.approval' if field=='approval' else 'work.head'
    require(set(values)==set(works) and all(ref.kind==kind for ref in values.values()), 'group-member-map-mismatch')
    return [values[work] for work in works]


def member_links(version,field,works,refs=None):
    if version==1:
        require(len(works)==2, 'group-two-distinct-works-required')
        return {field+str(i):('decision',refs[i] if refs is not None else None) for i in range(2)},[]
    require(version==2 and 2<=len(works)<=MAX_MEMBERS,'group-member-count-unsupported')
    if refs is None: return {MEMBER_FIELDS[field]:('decision',None)},[]
    require(len(refs)==len(works),'group-member-map-mismatch')
    mapping=build_map(zip(works,refs))
    return {MEMBER_FIELDS[field]:('decision',mapping.root)},list(mapping.objects)


def union_limits(before,after,scope,changes):
    """Bound the whole union before candidate checks or native staging."""
    from .bodies import submission_size
    require(len(scope)<=100000 and len(changes)<=100000,'group-union-path-limit')
    selected=set(scope)
    submission_size([e['size'] for entries in (before,after) for e in entries
                     if e['path'] in selected and e['kind']=='regular'])
    # Conservative macOS stat identity widths exceed the native 64-bit values.
    # Include full envelope/ancestor/item overhead before preparing any stage.
    native=dict(volume='9'*32,inode='9'*32,birth_ns=10**32-1)
    ancestors={}
    items=[]
    for i,item in enumerate(changes):
        parts=item['path'].split('/')
        for j in range(1,len(parts)): ancestors['/'.join(parts[:j])]=native
        items.append(dict(item,post_name=f'{i:06d}.post',evacuated_name=f'{i:06d}.original',
                          pre_native=native if item['pre'] is not None else None,
                          post_native=native if item['post'] is not None else None))
    record('worker.manifest',dict(application='x'*MAX_TOKEN_LENGTH,root=native,authority=native,stage=native,
                                 ancestors=ancestors,items=items),{})


def key(group): _token(group); return 'group:'+group

def member_key(work): _token(work); return 'group-member:'+work

def application_key(application): _token(application); return 'group-application:'+application


def get(ref, load):
    from .records import application_registry
    return application_registry().inspect(ref, load(ref), required=True)


def digest(value): return hashlib.sha256(canonical_bytes(value)).hexdigest()


def definitions(checks):
    require(type(checks) is list and 1 <= len(checks) <= 20, 'group-check-definitions-required')
    names=[]
    for check in checks:
        require(type(check) is dict and set(check)=={'name','argv','cwd','env','timeout_seconds','output_bytes'}, 'group-invalid-check')
        text(check['name'],128); names.append(check['name'])
        require(type(check['argv']) is list and 1 <= len(check['argv']) <= 100, 'group-invalid-check-argv')
        for arg in check['argv']: text(arg,4096)
        require(check['argv'][0].startswith('/'), 'group-check-executable-absolute')
        require(check['cwd']=='.' or logical_path(check['cwd'])==check['cwd'], 'group-invalid-check-cwd')
        env=check['env']; require(type(env) is dict and 'TMPDIR' not in env and len(env)<=32, 'group-invalid-check-env')
        for name,value in env.items():
            require(type(name) is str and name and name.replace('_','').isalnum() and not name[0].isdigit(), 'group-invalid-check-env')
            require(type(value) is str and len(value)<=4096 and '\x00' not in value, 'group-invalid-check-env')
        require(type(check['timeout_seconds']) is int and 1<=check['timeout_seconds']<=600, 'group-invalid-check-timeout')
        require(type(check['output_bytes']) is int and 1024<=check['output_bytes']<=1048576, 'group-invalid-check-output-limit')
    require(len(names)==len(set(names)), 'group-duplicate-check')


def _plan(p):
    fields(p,{'group','works','sources','destination','checks','acknowledgement'})
    _token(p['group']); _uuid(p['destination']); text(p['acknowledgement'])
    require(type(p['works']) is list and len(p['works'])==2 and p['works']==sorted(set(p['works'])), 'group-two-distinct-works-required')
    require(type(p['sources']) is list and len(p['sources'])==2 and len(set([*p['sources'],p['destination']]))==3, 'group-three-workspaces-required')
    for value in p['works']: _token(value)
    for value in p['sources']: _uuid(value)
    definitions(p['checks'])
    for name in ('head0','head1','baseline','destination_registration','backup_root'): one(p,name)


def _member(p):
    fields(p,{'group','work'}); _token(p['group']); _token(p['work']); one(p,'plan')


def _approval(p):
    fields(p,{'statement'}); text(p['statement'])
    for name in ('plan','approval0','approval1'): one(p,name)


def _candidate(p):
    fields(p,{'group'}); _token(p['group'])
    for name in ('approval','head0','head1','tree','after'): one(p,name)


def _evidence(p):
    fields(p,{'name','definition','exit_code','outcome','tree_unchanged','elapsed_ns','environment_inputs'})
    text(p['name'],128); text(p['definition'],64)
    require(p['outcome'] in ('exited','timeout','unavailable','output-limit','interrupted'), 'group-invalid-check-outcome')
    require((type(p['exit_code']) is int)==(p['outcome']=='exited'), 'group-invalid-check-exit')
    if p['outcome']!='exited': require(p['exit_code'] is None, 'group-invalid-check-exit')
    require(type(p['tree_unchanged']) is bool and type(p['elapsed_ns']) is int and p['elapsed_ns']>=0, 'group-invalid-check-evidence')
    require(p['environment_inputs']=='system runtime and approved environment; ignored and opaque files excluded', 'group-invalid-check-environment')
    for name in ('candidate','stdout','stderr'): one(p,name)


def _review(p):
    fields(p,set())
    for name in ('candidate','evidence'): one(p,name)


def _authorization(p):
    fields(p,{'application','request','request_digest','receipt','actor','statement'})
    _token(p['application']); _token(p['request']); text(p['actor'],256); text(p['statement'])
    for k in ('request_digest','receipt'): require(type(p[k]) is str and len(p[k])==64 and all(c in '0123456789abcdef' for c in p[k]), 'group-invalid-request')
    one(p,'review')


def _dissolution(p):
    fields(p,{'group','statement'}); _token(p['group']); text(p['statement'])
    for name in ('plan','selection'): one(p,name)


def _effect(p):
    fields(p,{'application','state'}); _token(p['application'])
    require(p['application'].startswith('group-') and p['state'] in ('pending','completed','cancelled'), 'group-invalid-effect')
    for name in ('authorization','manifest'): one(p,name)
    for name in ('progress','previous','completed0','completed1'): one(p,name,True)
    require(all(bool(p['links'][k])==(p['state']=='completed') for k in ('completed0','completed1')),'group-completion-pair-required')


def _plan_v2(p):
    fields(p,{'group','works','sources','destination','checks','acknowledgement'})
    _token(p['group']); _uuid(p['destination']); text(p['acknowledgement'])
    require(type(p['works']) is list and 2<=len(p['works'])<=MAX_MEMBERS and
            all(type(w) is str for w in p['works']) and p['works']==sorted(set(p['works'])), 'group-member-count-unsupported')
    require(type(p['sources']) is list and len(p['sources'])==len(p['works']) and
            all(type(w) is str for w in p['sources']) and
            len(set([*p['sources'],p['destination']]))==len(p['works'])+1,'group-distinct-workspaces-required')
    for value in p['works']: _token(value)
    for value in p['sources']: _uuid(value)
    definitions(p['checks'])
    for name in ('heads','baseline','destination_registration','backup_root'): one(p,name)


def _approval_v2(p):
    fields(p,{'statement'}); text(p['statement'])
    for name in ('plan','approvals'): one(p,name)


def _candidate_v2(p):
    fields(p,{'group'}); _token(p['group'])
    for name in ('approval','heads','tree','after'): one(p,name)


def _effect_v2(p):
    fields(p,{'application','state'}); _token(p['application'])
    require(p['application'].startswith('group-') and p['state'] in ('pending','completed','cancelled'), 'group-invalid-effect')
    for name in ('authorization','manifest'): one(p,name)
    for name in ('progress','previous','completed'): one(p,name,True)
    require(bool(p['links']['completed'])==(p['state']=='completed'),'group-completion-set-required')


def schemas():
    def schema(kind, validator, targets, content, version=1):
        return Schema(kind,version,{k:('provenance' if k in ('previous','backup_root') else 'integrity' if k in ('tree','after','baseline','manifest','progress','stdout','stderr') else 'decision') for k in targets},validator,
                      {k:frozenset(v) for k,v in targets.items()},local=pinned_group_version,content=content)
    legacy = [
        schema('group.plan',_plan,dict(head0=['work.head'],head1=['work.head'],baseline=['observation.snapshot'],destination_registration=['workspace.registration'],backup_root=['state.root']),validate_plan),
        schema('group.member',_member,dict(plan=['group.plan']),validate_member),
        schema('group.approval',_approval,dict(plan=['group.plan'],approval0=['work.approval'],approval1=['work.approval']),validate_approval),
        schema('group.candidate',_candidate,dict(approval=['group.approval'],head0=['work.head'],head1=['work.head'],tree=TREE_KINDS,after=MAP_KINDS),validate_candidate),
        schema('group.evidence',_evidence,dict(candidate=['group.candidate'],stdout=['body.complete'],stderr=['body.complete']),validate_evidence),
        schema('group.review',_review,dict(candidate=['group.candidate'],evidence=MAP_KINDS),validate_review),
        schema('group.authorization',_authorization,dict(review=['group.review']),validate_authorization),
        schema('group.dissolution',_dissolution,dict(plan=['group.plan'],selection=['group.plan','group.approval','group.candidate','group.review']),validate_dissolution),
        schema('group.effect',_effect,dict(authorization=['group.authorization'],manifest=['worker.manifest'],progress=['worker.progress'],previous=['group.effect'],completed0=['work.head'],completed1=['work.head']),validate_effect),
    ]
    modern = [
        schema('group.plan',_plan_v2,dict(heads=MAP_KINDS,baseline=['observation.snapshot'],destination_registration=['workspace.registration'],backup_root=['state.root']),validate_plan,2),
        schema('group.member',_member,dict(plan=['group.plan']),validate_member,2),
        schema('group.approval',_approval_v2,dict(plan=['group.plan'],approvals=MAP_KINDS),validate_approval,2),
        schema('group.candidate',_candidate_v2,dict(approval=['group.approval'],heads=MAP_KINDS,tree=TREE_KINDS,after=MAP_KINDS),validate_candidate,2),
        schema('group.evidence',_evidence,dict(candidate=['group.candidate'],stdout=['body.complete'],stderr=['body.complete']),validate_evidence,2),
        schema('group.review',_review,dict(candidate=['group.candidate'],evidence=MAP_KINDS),validate_review,2),
        schema('group.authorization',_authorization,dict(review=['group.review']),validate_authorization,2),
        schema('group.dissolution',_dissolution,dict(plan=['group.plan'],selection=['group.plan','group.approval','group.candidate','group.review']),validate_dissolution,2),
        schema('group.effect',_effect_v2,dict(authorization=['group.authorization'],manifest=['worker.manifest'],progress=['worker.progress'],previous=['group.effect'],completed=MAP_KINDS),validate_effect,2),
    ]
    return legacy+modern



def plan_for(ref,load):
    """Fixed-depth chain; history never substitutes for a current selection."""
    obj=get(ref,load)
    for _ in range(6):
        if obj.ref.kind=='group.plan': return obj
        field={'group.member':'plan','group.approval':'plan','group.candidate':'approval','group.review':'candidate','group.authorization':'review','group.effect':'authorization'}.get(obj.ref.kind)
        require(field is not None, 'group-record-required'); obj=get(link(obj,field),load)
    require(False,'group-chain-limit')


def validate_plan(ref,load):
    p=get(ref,load); baseline=get(link(p,'baseline'),load); before=read_tree(link(baseline,'tree'),load)
    require(baseline.payload['kind']=='git' and link(baseline,'workspace')==link(p,'destination_registration') and
            get(link(p,'destination_registration'),load).payload['workspace']==p.payload['destination'], 'group-destination-mismatch')
    scopes=[]
    for i,head in enumerate(member_refs(p,'head',p,load)):
        h,plan,_,_=head_summary(head,load)
        require(h.payload['phase']=='planned' and not h.payload['archived'] and link(h,'context') is None and
                plan.payload['work']==p.payload['works'][i] and plan.payload['workspace']==p.payload['sources'][i], 'group-planned-member-required')
        from .work import WorkService
        WorkService(None,None)._validate_head(h.ref,load)
        original=get(link(plan,'baseline'),load)
        require(link(get(link(original,'workspace'),load),'project')==link(get(link(p,'destination_registration'),load),'project'),'group-common-project-required')
        require(all(link(original,k)==link(baseline,k) for k in ('tree','policy')) and
                original.payload['kind']=='git' and original.payload['common']==baseline.payload['common'] and
                original.payload['opaque']==baseline.payload['opaque'], 'group-common-baseline-required')
        require(not set(scopes).intersection(plan.payload['scope']), 'group-overlapping-scopes')
        scopes.extend(plan.payload['scope'])
    path_namespace(scopes+[e['path'] for e in before])
    if p.ref.version==2: require(len(scopes)<=100000,'group-union-path-limit')


def validate_member(ref,load):
    member=get(ref,load); plan=get(link(member,'plan'),load)
    require(member.payload['group']==plan.payload['group'] and member.payload['work'] in plan.payload['works'], 'group-member-mismatch')


def validate_approval(ref,load):
    approval=get(ref,load); plan=get(link(approval,'plan'),load)
    heads=member_refs(plan,'head',plan,load); approvals=member_refs(approval,'approval',plan,load)
    for head,ref in zip(heads,approvals):
        _,wp,_,_=head_summary(head,load)
        a=get(ref,load)
        require(a.ref.version==1 and link(a,'plan')==wp.ref and all(a.payload[k]==wp.payload[k] for k in ('work','workspace')) and a.payload['statement']==approval.payload['statement'], 'group-approval-mismatch')


def candidate_parts(ref,load):
    candidate=get(ref,load); approval=get(link(candidate,'approval'),load); plan=get(link(approval,'plan'),load)
    baseline=get(link(plan,'baseline'),load); before=read_tree(link(baseline,'tree'),load)
    after={e['path']:e for e in before}; bodies={}; scopes=[]; members=[]
    from .work import WorkService
    validator=WorkService(None,None)
    heads=member_refs(candidate,'head',plan,load); original_heads=member_refs(plan,'head',plan,load)
    approvals=member_refs(approval,'approval',plan,load)
    for i,head in enumerate(heads):
        h,wp,result,_=head_summary(head,load)
        validator._validate_head(h.ref,load)
        original=head_summary(original_heads[i],load)[1]
        require(h.payload['phase']=='review' and not h.payload['archived'] and link(h,'context') is None and
                wp.ref==original.ref and result is not None and result.ref.version==1 and link(result,'approval')==approvals[i], 'group-exact-review-members-required')
        scope=wp.payload['scope']; scopes.extend(scope)
        observed=get(link(result,'observation'),load); entries={e['path']:e for e in read_tree(link(observed,'tree'),load)}
        for path in scope:
            after.pop(path,None)
            if path in entries: after[path]=entries[path]
        bodies.update(read_map(link(result,'after'),load)); members.append((h,wp,result))
    after=sorted(after.values(),key=lambda e:e['path'].encode())
    path_namespace(scopes+[e['path'] for e in before]+[e['path'] for e in after])
    changes=transitions(before,after,scopes)
    if plan.ref.version==2: union_limits(before,after,scopes,changes)
    require(not any(c['path'].split('/')[-1].casefold()=='.gitignore' for c in changes), 'worker-policy-edit-unsupported')
    require(candidate.payload['group']==plan.payload['group'], 'group-candidate-mismatch')
    return candidate,approval,plan,baseline,before,after,changes,bodies,members


def validate_candidate(ref,load):
    candidate,_,_,_,_,after,_,bodies,_=candidate_parts(ref,load)
    require(link(candidate,'tree')==build_tree(after).root and read_map(link(candidate,'after'),load)==bodies, 'group-union-mismatch')


def passed(evidence):
    p=evidence.payload
    return p['outcome']=='exited' and p['exit_code']==0 and p['tree_unchanged']


def validate_evidence(ref,load):
    e=get(ref,load); plan=plan_for(link(e,'candidate'),load)
    definitions_={c['name']:c for c in plan.payload['checks']}; definition=definitions_.get(e.payload['name'])
    require(definition is not None and e.payload['definition']==digest(definition), 'group-check-definition-mismatch')
    require(sum(get(link(e,k),load).payload['size'] for k in ('stdout','stderr'))<=definition['output_bytes'], 'group-check-log-limit')


def validate_review(ref,load):
    review=get(ref,load); candidate=link(review,'candidate'); plan=plan_for(candidate,load)
    entries=read_map(link(review,'evidence'),load)
    require(set(entries)=={c['name'] for c in plan.payload['checks']}, 'group-required-checks-missing')
    for name,e in entries.items():
        require(e.kind=='group.evidence' and e.version==review.ref.version, 'group-check-evidence-required'); evidence=get(e,load)
        require(evidence.payload['name']==name and link(evidence,'candidate')==candidate, 'group-check-candidate-mismatch')


def require_checks(review,load):
    validate_review(review.ref,load)
    for _,_,result in candidate_parts(link(review,'candidate'),load)[-1]:
        require(all(c['status']=='passed' for c in result.payload['checks']),'group-member-required-check-not-passed')
    for ref in read_map(link(review,'evidence'),load).values():
        validate_evidence(ref,load); require(passed(get(ref,load)), 'group-required-check-not-passed')


def request_digest(review,receipt,request,actor,statement,application):
    return digest(dict(review=review.as_dict(),receipt=receipt,request=request,actor=actor,statement=statement,application=application))


def validate_authorization(ref,load):
    auth=get(ref,load); review=get(link(auth,'review'),load); require_checks(review,load)
    p=auth.payload
    require(p['request_digest']==request_digest(review.ref,p['receipt'],p['request'],p['actor'],p['statement'],p['application']), 'group-request-mismatch')
    return auth,review


def validate_decision(ref,load):
    decision=get(ref,load); pinned_decision_version(decision); authorization=link(decision,'authorization')
    require(authorization is not None and authorization.kind=='group.authorization' and decision.payload['action']=='accept', 'group-decision-authorization-required')
    auth,review=validate_authorization(authorization,load)
    members=candidate_parts(link(review,'candidate'),load)[-1]
    require(any(decision.payload['work']==p.payload['work'] and decision.payload['workspace']==p.payload['workspace'] and
                link(decision,'result')==r.ref for _,p,r in members) and decision.payload['statement']==auth.payload['statement'], 'group-decision-mismatch')


def validate_effect(ref,load):
    effect=get(ref,load); auth,review=validate_authorization(link(effect,'authorization'),load)
    require(effect.payload['application']==auth.payload['application'],'group-application-mismatch')
    changes=candidate_parts(link(review,'candidate'),load)[6]; manifest=get(link(effect,'manifest'),load)
    require(manifest.payload['application']==effect.payload['application'] and
            [{k:item[k] for k in ('path','pre','post')} for item in manifest.payload['items']]==list(changes), 'group-effect-union-mismatch')
    if effect.payload['state']=='completed':
        from .work import WorkService
        members=candidate_parts(link(review,'candidate'),load)[-1]
        group_plan=plan_for(ref,load); completed=member_refs(effect,'completed',group_plan,load)
        for i,(old,plan,result) in enumerate(members):
            h,p,r,d=head_summary(completed[i],load)
            require(h.payload['phase']=='completed' and p.ref==plan.ref and r.ref==result.ref and
                    link(h,'previous')==old.ref and link(d,'authorization')==auth.ref,'group-completion-pair-mismatch')
            WorkService(None,None)._validate_head(h.ref,load)
    progress=link(effect,'progress')
    if progress:
        p=get(progress,load)
        require(p.payload['application']==effect.payload['application'] and p.payload['index']<len(changes), 'group-progress-mismatch')


def validate_dissolution(ref,load):
    obj=get(ref,load); plan=get(link(obj,'plan'),load)
    require(obj.payload['group']==plan.payload['group'] and plan_for(link(obj,'selection'),load).ref==plan.ref,'group-dissolution-mismatch')
