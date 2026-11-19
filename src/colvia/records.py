"""Fixed application record schemas and observation serialization for v1."""
from dataclasses import asdict
import base64,io

from .binding import _uuid
from .bodies import ingest_body
from .codec import Edge,decode_envelope,encode_envelope,require
from .connection import connection_schemas,native
from .graph import ClosurePolicy,Schema
from .observation import Policy,PolicySource
from .schemas import foundation_registry
from .storage.sqlite import _token
from .tree import logical_path

TREE_KINDS=frozenset({'tree.leaf','tree.branch'})
MAP_KINDS=frozenset({'map.leaf','map.branch'})


def text(value,limit=16384):
    require(type(value) is str and 0<len(value)<=limit and '\x00' not in value,'invalid-record-text')


def fields(payload,names):require(set(payload)==set(names)|{'links'},'invalid-typed-payload')

def one(payload,name,optional=False):
    values=payload['links'][name]
    require(type(values) is list and len(values) in ((0,1) if optional else (1,)),'invalid-record-link-count')


def identity(payload):_token(payload['work']);_uuid(payload['workspace'])


def _policy(payload):
    fields(payload,{'sources','config','tool'})
    require(type(payload['sources']) is list and len(payload['sources'])<=100000,'invalid-policy-record')
    require(payload['links']['sources']==list(range(len(payload['sources']))),'invalid-policy-record')
    for item in payload['sources']:
        require(type(item) is dict and set(item)=={'origin','sha256','size'},'invalid-policy-record')
        text(item['origin'],32768)
        require(type(item['size']) is int and 0<=item['size']<=4*1024*1024 and
                type(item['sha256']) is str and len(item['sha256'])==64 and all(c in '0123456789abcdef' for c in item['sha256']),
                'invalid-policy-record')
    require(type(payload['config']) is list and all(type(pair) is list and len(pair)==2 and
                all(type(x) is str for x in pair) for pair in payload['config']),'invalid-policy-record')
    text(payload['tool'],1024)


def _observation(payload):
    fields(payload,{'root','kind','common','gitdir','containers','nested','opaque'})
    native(payload['root']);require(payload['kind'] in ('git','plain'),'invalid-observation-kind')
    for name in ('common','gitdir'):
        require((payload[name] is None)==(payload['kind']=='plain'),'invalid-observation-topology')
        if payload[name] is not None:native(payload[name])
    for field in ('containers','nested'):
        require(type(payload[field]) is list and all(type(p) is str for p in payload[field]) and payload[field]==sorted(set(payload[field])),'invalid-structural-record')
        for path in payload[field]:require(logical_path(path)==path,'invalid-structural-record')
    require(type(payload['opaque']) is list and all(type(item) is list and len(item)==2 and type(item[0]) is str and type(item[1]) is list for item in payload['opaque']),'invalid-opaque-record')
    for name in ('tree','policy','workspace'):one(payload,name)


def _observation_v1(payload):
    from .binding import persistent
    _observation(payload)
    require(not any(persistent(native(payload[k])) for k in ('root','common','gitdir') if payload[k] is not None),
            'connection-identity-required')


def observation_identity(obj):
    return link(obj,'identity') if obj.ref.version==2 else None


def _observation_v2(payload):
    _observation({**payload,'links':{k:v for k,v in payload['links'].items() if k!='identity'}})
    one(payload,'identity')


def _observation_identity_content(ref,load):
    from .connection_identity import evidence,ROLES
    obj=decode_envelope(ref,load(ref))
    _observation_v2(obj.payload)
    _,workspace,binding,_,_,locations=evidence(observation_identity(obj),load)
    require(workspace==link(obj,'workspace') and obj.payload['kind']==binding.kind and
            all(obj.payload[k]==(asdict(locations[k]) if locations[k] is not None else None) for k in ROLES),
            'observation-identity-mismatch')


def _plan(payload):
    fields(payload,{'work','workspace','title','goal','scope','checks','excludes'})
    identity(payload);text(payload['title'],256);text(payload['goal'])
    require(type(payload['scope']) is list and 0<len(payload['scope'])<=100000 and
            payload['scope']==sorted(set(payload['scope'])),'invalid-scope')
    for path in payload['scope']:require(logical_path(path)==path,'invalid-scope-path')
    for key in ('checks','excludes'):
        require(type(payload[key]) is list and len(payload[key])<=100,'invalid-plan-criteria')
        for item in payload[key]:text(item,2048)
    require(payload['checks'] and len(set(payload['checks']))==len(payload['checks']),'invalid-plan-criteria')
    for name in ('baseline','before'):one(payload,name)


def _approval(payload):
    fields(payload,{'work','workspace','statement'});identity(payload);text(payload['statement']);one(payload,'plan')


def submission_input(summary,checks):
    """Validate caller input before a submission can stage body bytes."""
    text(summary)
    require(type(checks) is list and len(checks)<=100,'invalid-check-report')
    for item in checks:
        require(type(item) is dict and set(item)=={'name','status','detail'} and
                item['status'] in ('passed','failed','unavailable'),'invalid-check-report')
        text(item['name'],2048);text(item['detail'],4096)


def _submission(payload):
    fields(payload,{'work','workspace','revision','summary','checks','changed'})
    identity(payload);text(payload['summary'])
    require(type(payload['revision']) is int and payload['revision']>0,'invalid-result-revision')
    require(type(payload['changed']) is list and payload['changed']==sorted(set(payload['changed'])),'invalid-changed-paths')
    for path in payload['changed']:require(logical_path(path)==path,'invalid-changed-paths')
    submission_input(payload['summary'],payload['checks'])
    for name in ('plan','approval','observation','after'):one(payload,name)
    one(payload,'previous',True)


def _submission_v2(payload):
    _submission(payload);one(payload,"attribution")


def _submission_content(ref,load):
    from .work import WorkService
    service=WorkService(None,None);result=service._object(ref,load)
    service._validate_result(service._object(link(result,"plan"),load),result,load)


def _decision(payload):
    fields(payload,{'work','workspace','action','statement'});identity(payload);text(payload['statement'])
    require(payload['action'] in ('accept','request-changes'),'invalid-work-decision');one(payload,'result');one(payload,'authorization',True)


def _head(payload):
    fields(payload,{'work','workspace','title','phase','archived'})
    identity(payload);text(payload['title'],256)
    require(payload['phase'] in ('planned','approved','active','review','completed') and type(payload['archived']) is bool,'invalid-work-state')
    one(payload,'plan')
    for name in ('approval','result','decision','previous','context'):one(payload,name,True)
    require(bool(payload['links']['approval'])==(payload['phase']!='planned'),'work-approval-state-mismatch')
    if payload['phase'] in ('review','completed'):require(payload['links']['result'],'work-result-required')
    if payload['phase']=='completed':require(payload['links']['decision'],'work-decision-required')
    if payload['phase'] in ('planned','approved'):require(not payload['links']['result'] and not payload['links']['decision'],'unexpected-work-result')
    if payload['phase']=='review':require(not payload['links']['decision'],'unexpected-work-decision')
    if payload['phase']=='active':require(bool(payload['links']['result'])==bool(payload['links']['decision']),'rework-decision-required')
    require(not payload['archived'] or payload['phase']=='completed','archive-completed-work-only')


def application_registry():
    from .progress import schema as progress_schema
    from .planning import planning_schemas
    from .composition import schemas as composition_schemas
    from .worker_records import schemas as worker_schemas
    from .execution.records import schemas as execution_schemas
    from .delivery.records import schemas as delivery_schemas
    from .configuration import schemas as configuration_schemas
    from .lifecycle import schemas as lifecycle_schemas
    from .git_integration import schemas as git_schemas
    return foundation_registry([progress_schema(),*git_schemas(),*lifecycle_schemas(),*configuration_schemas(),*delivery_schemas(),*connection_schemas(),*planning_schemas(),*composition_schemas(),*worker_schemas(),*execution_schemas(),
        Schema('observation.policy',1,{'sources':'integrity'},_policy,{'sources':frozenset({'body.complete'})}),
        Schema('observation.snapshot',1,{'tree':'integrity','policy':'integrity','workspace':'decision'},_observation_v1,
               {'tree':TREE_KINDS,'policy':frozenset({'observation.policy'}),'workspace':frozenset({'workspace.registration'})}),
        Schema('observation.snapshot',2,{'tree':'integrity','policy':'integrity','workspace':'decision','identity':'decision'},
               _observation_v2,{'tree':TREE_KINDS,'policy':frozenset({'observation.policy'}),
                'workspace':frozenset({'workspace.registration'}),'identity':frozenset({'connection.identity'})},
               content=_observation_identity_content),
        Schema('work.plan',1,{'baseline':'integrity','before':'integrity'},_plan,
               {'baseline':frozenset({'observation.snapshot'}),'before':MAP_KINDS}),
        Schema('work.approval',1,{'plan':'decision'},_approval,{'plan':frozenset({'work.plan'})}),
        Schema('work.submission',1,{'plan':'decision','approval':'decision','observation':'integrity','after':'integrity','previous':'provenance'},_submission,
               {'plan':frozenset({'work.plan'}),'approval':frozenset({'work.approval'}),'observation':frozenset({'observation.snapshot'}),'after':MAP_KINDS,'previous':frozenset({'work.submission'})},
               local=lambda obj:require(link(obj,'previous') is None or link(obj,'previous').version==1,'attribution-protection-removed')),
        Schema('work.submission',2,{'plan':'decision','approval':'decision','observation':'integrity','after':'integrity','previous':'provenance','attribution':'decision'},_submission_v2,
               {'plan':frozenset({'work.plan'}),'approval':frozenset({'work.approval'}),'observation':frozenset({'observation.snapshot'}),'after':MAP_KINDS,'previous':frozenset({'work.submission'}),'attribution':MAP_KINDS},content=_submission_content),
        Schema('work.decision',1,{'result':'decision','authorization':'decision'},_decision,{'result':frozenset({'work.submission'}),'authorization':frozenset({'worker.authorization'})}),
        Schema('work.head',1,{'plan':'decision','approval':'decision','result':'decision','decision':'decision','previous':'provenance','context':'decision'},_head,
               {'plan':frozenset({'work.plan'}),'approval':frozenset({'work.approval'}),'result':frozenset({'work.submission'}),'decision':frozenset({'work.decision'}),'previous':frozenset({'work.head'}),'context':frozenset({'composition.binding','composition.membership'})}),
    ])


def operation_closure(registry):
    return ClosurePolicy({key:frozenset(name for name,role in schema.fields.items() if role in ('decision','integrity'))
                          for key,schema in registry._schemas.items()})


def link(obj,name):
    indices=obj.payload['links'][name]
    return obj.edges[indices[0]].ref if indices else None


def record(kind,payload,links,*,version=1):
    edges=[];indices={}
    for name,(role,ref) in links.items():
        indices[name]=[] if ref is None else [len(edges)]
        if ref is not None:edges.append(Edge(role,ref))
    return encode_envelope(kind,version,{**payload,'links':indices},tuple(edges))


def encode_observation(observed,workspace_ref,store,import_id):
    from .tree import build_tree
    tree=build_tree(observed.snapshot.entries);objects=list(tree.objects);sources=[];edges=[]
    for source in observed.policy.sources:
        ref,raw=ingest_body(io.BytesIO(source.raw),store,import_id,expected_size=len(source.raw),expected_sha256=source.digest)
        objects.append((ref,raw));edges.append(Edge('integrity',ref))
        sources.append(dict(origin=source.origin,sha256=source.digest,size=len(source.raw)))
    pref,praw=encode_envelope('observation.policy',1,dict(sources=sources,config=[list(p) for p in observed.policy.config],
        tool=observed.policy.tool,links={'sources':list(range(len(edges)))}),tuple(edges));objects.append((pref,praw))
    from .binding import persistent
    from .connection import Connections
    top=observed.topology
    links={'tree':('integrity',tree.root),'policy':('integrity',pref),'workspace':('decision',workspace_ref)}
    anchor=Connections(store).identity(workspace_ref)
    if (anchor is not None and anchor.version == 2) or any(persistent(v) for v in (top.root,top.common,top.gitdir)):
        require(anchor is not None,'connection-identity-required')
        links['identity']=('decision',anchor)
    ref,raw=record('observation.snapshot',dict(root=asdict(top.root),kind=top.kind,
        common=asdict(top.common) if top.common else None,gitdir=asdict(top.gitdir) if top.gitdir else None,
        containers=sorted(observed.structural.containers),nested=sorted(observed.structural.nested),opaque=[[p,list(value)] for p,value in observed.opaque]),
        links,version=2 if 'identity' in links else 1)
    objects.append((ref,raw));return ref,objects


def decode_policy(ref,load):
    from .bodies import body_bytes
    obj=decode_envelope(ref,load(ref));application_registry().inspect(ref,load(ref),required=True)
    sources=[]
    for meta,edge in zip(obj.payload['sources'],obj.edges):
        raw=b''.join(body_bytes(edge.ref,load));source=PolicySource(meta['origin'],raw)
        require(len(raw)==meta['size'] and source.digest==meta['sha256'],'policy-body-mismatch');sources.append(source)
    return Policy(tuple(sources),tuple(tuple(p) for p in obj.payload['config']),obj.payload['tool'])


def head_summary(ref,load):
    """Check selected record relationships without traversing body/history graphs."""
    registry=application_registry()
    def get(value,kind):
        obj=registry.inspect(value,load(value),required=True)
        require(obj is not None and value.kind==kind,'wrong-record-kind');return obj
    head=get(ref,'work.head');plan=get(link(head,'plan'),'work.plan')
    def common(obj):
        require(all(obj.payload[k]==head.payload[k] for k in ('work','workspace')),'work-reference-mismatch')
    common(plan);require(head.payload['title']==plan.payload['title'],'work-title-mismatch')
    approval=link(head,'approval')
    if approval is not None:
        obj=get(approval,'work.approval');common(obj)
        require(link(obj,'plan')==plan.ref,'approval-plan-mismatch')
    result=None;decision=None
    if link(head,'result') is not None:
        result=get(link(head,'result'),'work.submission');common(result)
        require(link(result,'plan')==plan.ref and link(result,'approval')==approval,'submission-approval-mismatch')
    if link(head,'decision') is not None:
        decision=get(link(head,'decision'),'work.decision');common(decision)
        require(result is not None and link(decision,'result')==result.ref,'decision-result-mismatch')
        if head.payload['phase']=='completed':require(decision.payload['action']=='accept','acceptance-required')
        elif head.payload['phase']=='active':require(decision.payload['action']=='request-changes','rework-decision-required')
    return head,plan,result,decision
