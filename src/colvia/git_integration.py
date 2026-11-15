"""Separate, explicitly approved Git integration over retained accepted bodies.

Accepting a Work never commits. A candidate retains complete index/diff bytes;
ref/index effects are serialized by the shared project barrier and have explicit
recovery. The native port is platform-specific, the stored decisions are not.
"""
import hashlib,io,base64
from .codec import Edge,encode_envelope,canonical_bytes,require
from .graph import Schema,validate_closure
from .records import record,link,fields,text,application_registry,operation_closure
from .work import WorkService,work_key
from .connection import Connections,PROJECT_KEY,workspace_key
from .effects import PENDING,guard
from .bodies import ingest_body,body_bytes,descriptor
from .maps import map_get
from .tree import entry_at
from .storage.sqlite import _token

PHASES={'prepared','lock-intent','locked','ref-intent','ref-observed','index-intent','completed','not-applied','relock-intent'}

def _plan(p):
    fields(p,{'operation','manifest','works','workspace'});_token(p['operation']);text(p['workspace'])
    require(type(p['works']) is list and 0<len(p['works'])<=128 and len(p['works'])==len(set(p['works'])),'git-work-selection-invalid')
    for w in p['works']:_token(w)
    m=p['manifest'];require(type(m) is dict and set(m)=={'operation','context','paths','new','tree','i1','diff','message','author'} and
                            m['operation']==p['operation'],'git-manifest-invalid')
    require(type(m['paths']) is list and 0<len(m['paths'])<=100000 and m['paths']==sorted(set(m['paths'])),'git-path-selection-invalid')
    from .tree import logical_path
    for path in m['paths']:require(logical_path(path)==path and not any(s.casefold()=='.git' for s in path.split('/')),'git-path-selection-invalid')
    for name in ('new','tree'):
        value=m[name];require(type(value) is str and len(value) in (40,64) and all(c in '0123456789abcdef' for c in value),'git-object-id-invalid')
    for name in ('binding','workspace','i0','i1','diff'):require(len(p['links'][name])==1,'git-plan-reference-invalid')
    require(len(p['links']['accepted'])==len(p['works']),'git-plan-reference-invalid')

def _state(p):
    fields(p,{'operation','phase','sequence','owner','child','child_phase','statement'});_token(p['operation'])
    require(p['phase'] in PHASES and type(p['sequence']) is int and 0<=p['sequence']<=128,'git-state-invalid')
    require(p['child_phase'] in (None,'spawn-intent','started','exited'),'git-child-state-invalid')
    if p['child'] is not None:_token(p['child'])
    if p['owner'] is not None:
        owner=p['owner'];require(type(owner) is dict and set(owner)=={'native','pid','birth'} and
            type(owner['pid']) is int and owner['pid']>1 and type(owner['birth']) is str and bool(owner['birth']),'git-lock-owner-invalid')
        # Native identity is interpreted only by the matching platform port.
        # Core retains its exact typed spelling without imposing POSIX inode
        # fields on Windows or future platforms. Unknown schemes are readable,
        # never permission for a port to skip its equality/ownership checks.
        native=owner['native']
        require(type(native) is dict and set(native)=={'scheme','value'},'git-lock-owner-invalid')
        _token(native['scheme'])
        require(type(native['value']) is str and 0<len(native['value'])<=256 and
                all(33<=ord(c)<=126 for c in native['value']),'git-lock-owner-invalid')
    text(p['statement']);require(len(p['links']['plan'])==1 and len(p['links']['previous'])<=1,'git-state-reference-invalid')

def schemas():
    return [Schema('git.integration-plan',1,{'binding':'decision','workspace':'decision','accepted':'decision',
                    'i0':'integrity','i1':'integrity','diff':'integrity'},_plan,
                   {'binding':frozenset({'project.binding'}),'workspace':frozenset({'workspace.registration'}),
                    'accepted':frozenset({'work.head'}),'i0':frozenset({'body.complete'}),'i1':frozenset({'body.complete'}),'diff':frozenset({'body.complete'})}),
            Schema('git.integration-state',1,{'plan':'decision','previous':'provenance'},_state,
                   {'plan':frozenset({'git.integration-plan'}),'previous':frozenset({'git.integration-state'})})]

def key(operation):_token(operation);return 'git-integration:'+operation

class GitIntegration:
    def __init__(self,store,workspace,port):
        self.store=store;self.workspace=workspace;self.port=port;self.work=WorkService(store,workspace)
        self.registry=application_registry();self.closure=operation_closure(self.registry)
    def obj(self,ref,load=None):
        load=load or self.store.load;return self.registry.inspect(ref,load(ref),required=True)
    def _selected(self,works):
        heads=[];changes={};bodies={}
        for name in works:
            ref,head=self.work._head(name);require(head.payload['phase']=='completed','git-accepted-result-required')
            self.work._validate_head(ref,self.store.load)
            plan=self.obj(link(head,'plan'));result=self.obj(link(head,'result'))
            require(self.work._result_agrees(plan,result),'git-accepted-files-changed');heads.append(ref)
            observed=self.obj(link(result,'observation'));tree=link(observed,'tree')
            for path in result.payload['changed']:
                entry=entry_at(tree,path,self.store.load);body=map_get(link(result,'after'),path,self.store.load)
                require(entry is None or entry['kind']=='regular','opaque-git-edit-not-supported')
                require(path not in changes or changes[path]==entry,'git-selected-results-conflict')
                changes[path]=entry;bodies[path]=body
        require(changes,'git-no-selected-change');return heads,changes,bodies
    def _validate(self,plan,view):
        m=plan.payload['manifest']
        registration=self.obj(link(plan,'workspace'),view);binding=self.obj(link(plan,'binding'),view)
        from dataclasses import asdict
        ref,effective,current=Connections(self.store).workspace(self.workspace.workspace)
        top=m['context']['topology']
        require(ref==registration.ref and plan.payload['workspace']==self.workspace.workspace==registration.payload['workspace'] and
                current.kind==binding.payload['kind']=='git' and top['root']==asdict(effective.root) and
                effective.gitdir is not None and top['gitdir']==asdict(effective.gitdir) and top['common']==asdict(current.location),
                'git-workspace-manifest-mismatch')
        selected={}
        require(view.head(PROJECT_KEY)==link(plan,'binding') and view.head(workspace_key(self.workspace.workspace))==link(plan,'workspace'),
                'git-connection-changed')
        for work,index in zip(plan.payload['works'],plan.payload['links']['accepted'],strict=True):
            ref=plan.edges[index].ref;require(view.head(work_key(work))==ref,'git-accepted-result-changed')
            self.work._validate_head(ref,view)
            head=self.obj(ref,view);require(head.payload['work']==work and head.payload['workspace']==self.workspace.workspace,'git-work-reference-mismatch');require(head.payload['phase']=='completed','git-accepted-result-required')
            result=self.obj(link(head,'result'),view);observed=self.obj(link(result,'observation'),view)
            for path in result.payload['changed']:
                entry=entry_at(link(observed,'tree'),path,view)
                require(path not in selected or selected[path]==entry,'git-selected-results-conflict');selected[path]=entry
        require(m['paths']==sorted(selected) and m['context']['selected']==[selected[p] for p in sorted(selected) if selected[p] is not None],
                'git-selected-result-mismatch')
        for field,expected in [('i0',m['context']['index'] or hashlib.sha256(b'').hexdigest()),('i1',m['i1']),('diff',m['diff'])]:
            ref=link(plan,field);require(descriptor(ref,view(ref)).payload['sha256']==expected,'git-recovery-body-mismatch')
    def _state(self,operation):
        ref=self.store.head(key(operation));require(ref is not None,'git-integration-not-found')
        state=self.obj(ref);plan=self.obj(link(state,'plan'))
        require(state.payload['operation']==operation==plan.payload['operation'],'git-integration-identity-mismatch')
        validate_closure([ref],self.store.load,self.registry,self.closure);return ref,state,plan
    def _receipt(self,ref):return hashlib.sha256(canonical_bytes(dict(project=self.store.project,instance=self.store.instance,plan=ref.as_dict()))).hexdigest()
    def prepare(self,*,operation,works,message,identity):
        _token(operation);require(type(works) is list and 0<len(works)<=128 and len(works)==len(set(works)),'git-work-selection-invalid')
        from .platforms.git_candidate import validate_candidate_input
        validate_candidate_input(message, identity)
        require(self.store.head(PENDING) is None,'external-effect-pending');require(self.store.head(key(operation)) is None,'git-integration-already-exists')
        with self.port.exclusion():
            registration,_,_=self.workspace.verify();binding=self.store.head(PROJECT_KEY)
            heads,changes,bodies=self._selected(works)
            # Git object writes precede the ref/index reservation. Keep the
            # attempt active until a known refusal or this exact publication.
            attempt=operation+'-prepare'
            with self.store.import_attempt(attempt,'git-candidate',can_abandon=lambda: not self.port.child_pending):
                m=self.port.prepare(operation,changes,lambda path:body_bytes(bodies[path],self.store.load),message=message,identity=identity)
                area=self.port.verify_manifest(m);objects=[];refs={}
                for name in ('i0','i1','diff'):
                    raw=self.port.files.read(area/name,128*1024*1024)
                    pair=ingest_body(io.BytesIO(raw),self.store,attempt,expected_size=len(raw),expected_sha256=hashlib.sha256(raw).hexdigest())
                    objects.append(pair);refs[name]=pair[0]
                edges=[Edge('decision',binding),Edge('decision',registration),*[Edge('decision',h) for h in heads],
                       *[Edge('integrity',refs[n]) for n in ('i0','i1','diff')]]
                n=len(heads);links=dict(binding=[0],workspace=[1],accepted=list(range(2,2+n)),i0=[2+n],i1=[3+n],diff=[4+n])
                plan=encode_envelope('git.integration-plan',1,dict(operation=operation,manifest=m,works=works,workspace=self.workspace.workspace,links=links),tuple(edges))
                state=record('git.integration-state',dict(operation=operation,phase='prepared',sequence=0,owner=None,child=None,child_phase=None,statement='Candidate prepared; not approved'),
                             {'plan':('decision',plan[0]),'previous':('provenance',None)})
                def validate(view):
                    guard(view);self._validate(self.obj(plan[0],view),view)
                    validate_closure([state[0]],view,self.registry,self.closure)
                self.port.check(m)
                self.store.commit_heads(operation=attempt,expected={key(operation):None},changes={key(operation):state[0]},objects=[*objects,plan,state],import_id=attempt,validate=validate)
        return self.preview(operation)
    def preview(self,operation):
        _,state,plan=self._state(operation);m=plan.payload['manifest']
        raw=b''.join(body_bytes(link(plan,'diff'),self.store.load))
        return dict(integration=operation,operation=operation,state=state.payload['phase'],files=m['paths'],parent=m['context']['ref'],branch=m['context']['branch'],
            commit=m['new'],message=m['message'],author=m['author'],diff_base64=base64.b64encode(raw).decode('ascii'),diff_sha256=m['diff'],
            receipt=self._receipt(plan.ref),question='이 변경만 Git에 기록할까요? 다른 staging 내용은 그대로 남깁니다.')
    def _advance(self,ref,state,plan,phase,*,owner=None,child=None,child_phase=None,statement=None,reserve=False,finish=False):
        p=state.payload;pair=record('git.integration-state',dict(operation=p['operation'],phase=phase,sequence=p['sequence']+1,
            owner=p['owner'] if owner is None else owner,child=p['child'] if child is None else child,
            child_phase=p['child_phase'] if child_phase is None else child_phase,statement=statement or p['statement']),
            {'plan':('decision',plan.ref),'previous':('provenance',ref)})
        def validate(view):
            guard(view,expected_effect=None if reserve else ref);self._validate(plan,view)
            validate_closure([pair[0]],view,self.registry,self.closure)
        self.store.commit_heads(operation=p['operation']+'-step-'+str(p['sequence']+1),expected={key(p['operation']):ref,PENDING:None if reserve else ref},
            changes={key(p['operation']):pair[0],PENDING:None if finish else pair[0]},objects=[pair],validate=validate)
        return pair[0],self.obj(pair[0])
    def apply(self,operation,*,receipt,statement,event=lambda _:None):
        text(statement)
        with self.port.exclusion():
            ref,state,plan=self._state(operation);m=plan.payload['manifest']
            require(state.payload['phase']=='prepared','git-integration-recovery-required')
            require(receipt==self._receipt(plan.ref),'git-integration-review-changed');self.port.check(m)
            ref,state=self._advance(ref,state,plan,'lock-intent',statement=statement,reserve=True);event('lock-intent')
            if hasattr(self.port,'reconcile_owner'):
                def live_gate():require(self.store.head(PENDING)==ref and self.store.head(key(operation))==ref,'git-effect-authority-changed')
                owner=self.port.acquire_index(m,attempt=dict(head=ref.as_dict(),sequence=state.payload['sequence']),live=live_gate)
            else:owner=self.port.acquire_index(m)
            ref,state=self._advance(ref,state,plan,'locked',owner=owner);event('lock-created');event('locked')
            self.port.check(m)
            ref,state=self._advance(ref,state,plan,'ref-intent');event('ref-intent')
            def live():require(self.store.head(PENDING)==ref and self.store.head(key(operation))==ref,'git-effect-authority-changed')
            def child_event(phase,area):
                nonlocal ref,state
                from pathlib import Path
                ref,state=self._advance(ref,state,plan,'ref-intent',child=Path(area).name,child_phase=phase)
            self.port.update_ref(m,owner,live=live,event=child_event)
            require(self.port.inspect_outcome(m)==('new','old'),'git-ref-update-unconfirmed')
            self.port.flush_ref(m)
            ref,state=self._advance(ref,state,plan,'ref-observed');event('ref-observed')
            ref,state=self._advance(ref,state,plan,'index-intent');event('index-intent')
            self.port.replace_index(m,owner,live=live);event('index-replaced')
            self.port.check_post(m)
            self.port.finalize_index(m,owner,live=live)
            self._advance(ref,state,plan,'completed',finish=True)
        return dict(integration=operation,operation=operation,state='completed',commit=m['new'])
    def recover(self,operation,*,statement,event=lambda _:None):
        text(statement)
        with self.port.exclusion():
            ref,state,plan=self._state(operation);m=plan.payload['manifest'];p=state.payload
            if p['phase']=='completed':return dict(integration=operation,operation=operation,state='completed',commit=m['new'])
            if p['phase']=='not-applied':return dict(integration=operation,operation=operation,state='not-applied')
            require(self.store.head(PENDING)==ref,'git-pending-mismatch')
            self.port.recovery_ready(m,p['owner'],p['child'])
            reconcile=getattr(self.port,'reconcile_owner',None)
            if reconcile is not None and p['phase'] in ('lock-intent','relock-intent'):
                def live_gate():require(self.store.head(PENDING)==ref and self.store.head(key(operation))==ref,'git-effect-authority-changed')
                owner=reconcile(m,p['owner'],attempt=dict(head=ref.as_dict(),sequence=p['sequence']),live=live_gate)
                if owner is not None:
                    ref,state=self._advance(ref,state,plan,'locked' if p['phase']=='lock-intent' else 'index-intent',owner=owner)
                    ref,state,plan=self._state(operation);m=plan.payload['manifest'];p=state.payload
            # A missing child reference precedes Popen. A referenced area with
            # no started identity remains unknown, even if its phase lagged.
            outcome=self.port.inspect_outcome(m)
            if outcome[0]=='old' and outcome[1]!='new' and p['phase'] not in ('ref-observed','index-intent','relock-intent'):
                if not self.port.lock_absent(m):
                    require(p['owner'] is not None,'git-index-lock-unrecorded');self.port.release_owned(m,p['owner'])
                self._advance(ref,state,plan,'not-applied',statement=statement,finish=True)
                return dict(integration=operation,operation=operation,state='not-applied')
            owner=p['owner']
            if outcome in (('new','old'),('new','evacuated')):
                if outcome[1]=='evacuated':require(p['phase'] in ('index-intent','relock-intent'),'git-index-phase-mismatch')
                require(p['owner'] is not None,'git-index-lock-not-owned')
                ref,state=self._advance(ref,state,plan,'relock-intent',statement=statement)
                def live():require(self.store.head(PENDING)==ref and self.store.head(key(operation))==ref,'git-effect-authority-changed')
                if reconcile is not None:
                    owner=self.port.recover_index(m,p['owner'],live=live,attempt=dict(head=ref.as_dict(),sequence=state.payload['sequence']))
                else:owner=self.port.recover_index(m,p['owner'],live=live)
                event('lock-reacquired')
                ref,state=self._advance(ref,state,plan,'index-intent',owner=owner)
                self.port.flush_ref(m)
                self.port.replace_index(m,owner,live=live);event('index-replaced')
            else:require(outcome==('new','new'),'git-external-divergence')
            self.port.check_post(m)
            self.port.finalize_index(m,owner,live=lambda:require(self.store.head(PENDING)==ref,'git-effect-authority-changed'))
            require(self.port.lock_absent(m),'git-index-lock-not-owned')
            self._advance(ref,state,plan,'completed',statement=statement,finish=True)
            return dict(integration=operation,operation=operation,state='completed',commit=m['new'])
