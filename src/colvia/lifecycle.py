"""Ordered detach with durable intents and a project-wide external-effect barrier.

A manager provides exactly owned routing, entry blocks and locator changes. This
service does not discover arbitrary files, grant permissions, delete history or
interpret a disappeared file as a completed operation. Each failed effect stays
pending until an explicit recovery call observes the prepared native identities.
"""
import hashlib
from .codec import canonical_bytes,require
from .graph import Schema,validate_closure
from .records import record,link,fields,text,application_registry,operation_closure
from .connection import PROJECT_KEY,Connections
from .effects import PENDING,guard
from .storage.sqlite import _token

ORDER={'routing':0,'entry':1,'locator':2}


def owned_block(current,installed):
    """Remove only the exact installed block; preserve all surrounding bytes."""
    require(type(current) is bytes and type(installed) is bytes and 0<len(installed)<=1024*1024,
            'detach-owned-block-required')
    require(current.count(installed)==1,'detach-entry-edited-or-ambiguous')
    return current.replace(installed,b'',1)


def describe_manifest(m):
    return [dict(role=s['role'],root=s['root'],path=s['path'],pre=s['native']['items'][0]['pre'],
                 post=s['native']['items'][0]['post'],native=s['native']['items'][0]['pre_native'],
                 root_identity=s['native']['root'],authority_identity=s['native']['authority']) for s in m['steps']]


def _plan(p):
    fields(p,{'operation','manifest','statement','preview_sha256'});_token(p['operation']);text(p['statement'])
    require(p['links']=={'binding':[0]},'invalid-detach-links')
    m=p['manifest']
    require(type(m) is dict and set(m)=={'operation','steps'} and m['operation']==p['operation'] and
            type(m['steps']) is list and 0<len(m['steps'])<=128,'invalid-detach-manifest')
    roles=[];targets=[];native_kinds=set()
    for s in m['steps']:
        require(type(s) is dict and set(s)=={'role','root','path','native'} and s['role'] in ORDER,'invalid-detach-step')
        _token(s['root'])
        from .tree import logical_path
        require(logical_path(s['path'])==s['path'] and type(s['native']) is dict,'invalid-detach-path')
        from .worker_records import schemas as worker_schemas
        check=next(schema for schema in worker_schemas() if schema.kind=='worker.manifest')
        check.payload({**s['native'],'links':{}})
        from .worker_records import native_identity_kind
        native_kinds.add(native_identity_kind(s['native']['root']))
        require(len(native_kinds)==1,'mixed-effect-native-identity')
        require(len(s['native']['items'])==1 and s['native']['items'][0]['path']==s['path'] and
                s['native']['application']==p['operation']+'-'+str(len(roles)), 'invalid-detach-native-plan')
        roles.append(ORDER[s['role']]);targets.append((s['root'],s['path']))
    require(roles==sorted(roles) and roles[-1]==ORDER['locator'] and len(targets)==len(set(targets)),
            'invalid-detach-order')
    require(p['preview_sha256']==hashlib.sha256(canonical_bytes(describe_manifest(m))).hexdigest(),'detach-preview-manifest-mismatch')


def _state(p):
    fields(p,{'operation','next','phase'});_token(p['operation'])
    require(type(p['next']) is int and 0<=p['next']<=128 and p['phase'] in ('ready','intent','completed'),
            'invalid-detach-state')
    require(p['links']['plan']==[0] and len(p['links']['previous']) in (0,1),'invalid-detach-links')



def _integration(p):
    import base64
    from .tree import logical_path
    fields(p,{'entries'})
    require(p['links']=={'binding':[0],'workspace':[1]} and type(p['entries']) is list and 0<len(p['entries'])<=128,'invalid-integration-config')
    seen=set();total=0
    for e in p['entries']:
        require(type(e) is dict and set(e)=={'role','root','path','owned','existed','mode'} and e['role'] in ('entry','locator') and
                e['root'] in ('project','locator') and logical_path(e['path'])==e['path'] and type(e['existed']) is bool and
                e['mode'] in ('100644','100755'),'invalid-integration-entry')
        require((e['root'],e['path']) not in seen,'duplicate-integration-entry');seen.add((e['root'],e['path']))
        try:raw=base64.b64decode(e['owned'],validate=True)
        except (ValueError,TypeError):require(False,'invalid-integration-body')
        require(base64.b64encode(raw).decode()==e['owned'] and 0<len(raw)<=1024*1024,'invalid-integration-body')
        total+=len(raw);require(total<=8*1024*1024,'integration-body-limit')

def schemas():
    result=[]
    for action in ('detach','connect'):
        plan='lifecycle.'+action+'-plan';state='lifecycle.'+action+'-state'
        result.extend([Schema(plan,1,{'binding':'decision'},_plan,{'binding':frozenset({'project.binding'})}),
            Schema(state,1,{'plan':'decision','previous':'provenance'},_state,
                   {'plan':frozenset({plan}),'previous':frozenset({state})})])
    result.append(Schema('project.integration',1,{'binding':'decision','workspace':'decision'},_integration,{'binding':frozenset({'project.binding'}),'workspace':frozenset({'workspace.registration'})}))
    return result


def key(operation):_token(operation);return 'detach:'+operation


class Detach:
    action="detach"
    completed="detached"
    question="Colvia 연결을 해제할까요? 파일과 작업 기록은 보존합니다."
    def key(self,operation):
        _token(operation);return self.action+":"+operation
    def __init__(self,store,port):
        self.store=store;self.port=port;self.registry=application_registry();self.closure=operation_closure(self.registry)
    def _load(self,ref,load=None):
        loader=load or self.store.load
        return self.registry.inspect(ref,loader(ref),required=True)
    def _receipt(self,binding,preview):
        return hashlib.sha256(canonical_bytes(dict(project=self.store.project,instance=self.store.instance,
            action=self.action,binding=binding.as_dict(),preview=preview))).hexdigest()
    def preview(self,changes):
        binding,_=Connections(self.store).binding();preview=self.port.preview(changes)
        return dict(receipt=self._receipt(binding,preview),steps=[s['role'] for s in preview],
                    question=self.question)
    def begin(self,*,operation,changes,receipt,statement):
        _token(operation);text(statement)
        with self.port.exclusion():
            binding,_=Connections(self.store).binding();preview=self.port.preview(changes)
            require(receipt==self._receipt(binding,preview),'detach-review-changed')
            require(self.store.head(PENDING) is None,'external-effect-pending')
            require(self.store.head(self.key(operation)) is None,'detach-already-started')
            manifest=self.port.prepare(operation,changes)
            require(describe_manifest(manifest)==preview,'detach-preview-manifest-mismatch')
            plan=record('lifecycle.'+self.action+'-plan',dict(operation=operation,manifest=manifest,statement=statement,preview_sha256=hashlib.sha256(canonical_bytes(preview)).hexdigest()),
                        {'binding':('decision',binding)})
            state=record('lifecycle.'+self.action+'-state',dict(operation=operation,next=0,phase='ready'),
                         {'plan':('decision',plan[0]),'previous':('provenance',None)})
            def validate(view):
                guard(view);require(view.head(PROJECT_KEY)==binding,'detach-binding-changed')
                require(self.port.preview(changes)==preview,'detach-files-changed')
                validate_closure([state[0]],view,self.registry,self.closure)
            self.store.commit_heads(operation=operation+'-reserve',expected={self.key(operation):None,PENDING:None},
                changes={self.key(operation):state[0],PENDING:state[0]},objects=[plan,state],validate=validate)
        return dict(operation=operation,state='pending',next=0)
    def advance(self,operation,*,event=lambda _:None):
        """One ordered step per call; explicit re-entry is recovery, not retry."""
        with self.port.exclusion():
            ref=self.store.head(self.key(operation));require(ref is not None,'detach-not-found')
            state=self._load(ref);plan=self._load(link(state,'plan'));m=plan.payload['manifest']
            require(state.payload['operation']==operation==plan.payload['operation'],'detach-identity-mismatch')
            validate_closure([ref],self.store.load,self.registry,self.closure)
            if state.payload['phase']=='completed':return dict(operation=operation,state=self.completed)
            n=state.payload['next'];require(n<len(m['steps']),'invalid-detach-state')
            binding=link(plan,'binding')
            def check(view,expected):
                guard(view,expected_effect=expected);require(view.head(PROJECT_KEY)==binding,'detach-binding-changed')
            def publish(previous,phase,index,suffix,finish=False):
                pair=record('lifecycle.'+self.action+'-state',dict(operation=operation,next=index,phase=phase),
                            {'plan':('decision',plan.ref),'previous':('provenance',previous)})
                def validate(view):
                    check(view,previous);validate_closure([pair[0]],view,self.registry,self.closure)
                expected={self.key(operation):previous,PENDING:previous};changes={self.key(operation):pair[0],PENDING:None if finish else pair[0]}
                if finish and self.action=='detach':expected[PROJECT_KEY]=binding;changes[PROJECT_KEY]=None
                self.store.commit_heads(operation=operation+suffix,expected=expected,changes=changes,objects=[pair],validate=validate)
                return pair[0]
            require(self.store.head(PENDING)==ref,'detach-pending-mismatch')
            # Later targets must still be pre; earlier targets must remain post.
            # This also detects edits to preserved outside-block bytes.
            for i in range(len(m['steps'])):
                actual=self.port.state(m,i)
                require(actual==('post' if i<n else 'pre') or
                        (i==n and state.payload['phase']=='intent' and actual in ('post','evacuated')),'detach-files-changed')
            if state.payload['phase']=='ready':
                ref=publish(ref,'intent',n,f'-intent-{n}');event('intent')
            def live():
                require(self.store.head(PENDING)==ref and self.store.head(PROJECT_KEY)==binding,'detach-authority-changed')
            live();self.port.apply(m,n,before_effect=live,event=event)
            require(self.port.state(m,n)=='post','detach-step-unconfirmed');event('applied')
            done=n+1==len(m['steps'])
            for i in range(n+1):require(self.port.state(m,i)=='post','detach-files-changed')
            publish(ref,'completed' if done else 'ready',n+1,f'-done-{n}',finish=done)
            return dict(operation=operation,state=self.completed if done else 'pending',next=n+1)


class ConnectFiles(Detach):
    """Reuse ordered identity-preserving effects; retain the project binding."""
    action='connect'
    completed='connected'
    question='이 폴더에 Colvia를 적용할까요? 기존 작업 파일과 규칙은 보존합니다.'
