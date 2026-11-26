"""Store-backed causal journal. This module never spawns or writes user files.

The qualified host owns filesystem/process observations and exact transmission
approval. Persisted grants or a reopened journal do not reconstruct a live host.
"""
from pathlib import PurePosixPath
import time
from ..codec import require,canonical_bytes
from ..records import record,link,head_summary
from ..connection import workspace_key
from ..work import work_key
from ..maps import read_map,build_map,map_update
from ..graph import validate_closure
from ..bodies import descriptor
from ..effects import PENDING,guard
from ..storage.sqlite import _token
from .history import History
from . import schema
from .records import history_bounds

AUTHORITY_EVENTS=frozenset(('runtime-reserved','admission','bound','recovery-ready','callback-reserved','worker-spawn-intent','seal'))

def is_authority_event(kind,value):
    return kind in AUTHORITY_EVENTS or (kind=='rpc-reserved' and value.get('method')!='turn/interrupt')

def key(run):_token(run);return 'execution:'+run

def prepared_key(run):_token(run);return 'execution-prepared:'+run

def cancel_key(run):_token(run);return 'execution-cancel:'+run

class ExecutionJournal:
    def __init__(self,service):self.service=service;self.store=service.store
    def obj(self,ref,load=None):return self.service._object(ref,load)
    def grant(self,ref,load):
        validate_closure([ref],load,self.service.registry,self.service.closure)
        grant=self.obj(ref,load);require(ref.kind=='execution.grant','execution-grant-required')
        h,p,_,_=head_summary(link(grant,'head'),load);self.service._validate_head(h.ref,load)
        require(h.payload['phase']=='active' and h.payload['work']==grant.payload['work'] and h.payload['workspace']==grant.payload['workspace'],'execution-active-work-required')
        require(link(h,'context') is None or link(h,'context').kind=='composition.membership','execution-parent-not-supported')
        registration=self.obj(link(grant,'registration'),load)
        require(registration.payload['workspace']==grant.payload['workspace'],'execution-registration-mismatch')
        contract=grant.payload['contract'];scope=contract['scope'];root=PurePosixPath(contract['target'])
        require(contract['target']==registration.payload['root']['path'],'execution-target-registration-mismatch')
        # Qualified host verifies native identity; these are additional immutable
        # scope and body checks, also available after detach/expiry.
        output=PurePosixPath(scope['documents'][scope['output_id']]['path'])
        require(output.is_relative_to(root) and str(output.relative_to(root)) in p.payload['scope'],'execution-output-outside-scope')
        require(not any(part.casefold()=='.git' for part in output.relative_to(root).parts) and
                output.name.casefold() not in ('.gitignore','.gitattributes'),'execution-policy-output-refused')
        paths={item['path'] for item in scope['documents'].values()}
        for name in grant.payload['request']['link_metadata']:
            target=PurePosixPath(name)
            require(target.is_relative_to(root) and target!=root and name not in paths and
                not any(part.casefold() in ('.git','.colvia') for part in target.relative_to(root).parts),
                'execution-link-metadata-outside-scope')
        bodies=read_map(link(grant,'bodies'),load)
        require(set(bodies)==set(scope['documents']),'execution-input-body-set')
        for name,ref in bodies.items():
            body=descriptor(ref,load(ref));expected=scope['documents'][name]['original_identity']
            require(body.payload['size']==expected['size'] and body.payload['sha256']==expected['sha256'],'execution-input-body-mismatch')
        return grant
    def live(self,grant,view):
        from ..group_guard import guard as group_guard
        group_guard(view,grant.payload['work'])
        require(view.head(work_key(grant.payload['work']))==link(grant,'head') and
                view.head(workspace_key(grant.payload['workspace']))==link(grant,'registration'),'execution-dependency-changed')
    def prepare(self,*,operation,run,contract,request,bodies,objects=(),import_id=None):
        schema.grant_record(contract);schema.request_record(request,contract)
        from .guards import checked_payload
        checked_payload(request['prompt']);checked_payload(request['claims']);checked_payload(request['approved_external_links'])
        ref,head=self.service._head(contract['scope']['work_id'])
        registration=self.store.head(workspace_key(head.payload['workspace']))
        pair=record('execution.grant',dict(run=run,work=head.payload['work'],workspace=head.payload['workspace'],contract=contract,request=request),
            {'head':('decision',ref),'registration':('decision',registration),'bodies':('integrity',bodies)})
        def validate(view):
            from ..configuration import require_enabled
            guard(view);require_enabled(view,'official-execution');self.live(self.grant(pair[0],view),view)
        self.store.commit_heads(operation=operation,expected={prepared_key(run):None},changes={prepared_key(run):pair[0]},objects=[*objects,pair],import_id=import_id,validate=validate)
        return dict(run=run,receipt=self.service._receipt('execution-start',head.payload['work'],pair[0]),state='prepared')
    def _row(self,history,kind,value):
        row=dict(seq=len(history.rows)+1,previous=history.rows[-1]['sha256'] if history.rows else '0'*64,kind=kind,value=value)
        row['sha256']=schema.digest(row);return row
    def _state(self,run,grant,authorization,history_ref,owner,history,previous=None):
        return record('execution.state',dict(run=run,status=history.terminal or 'incomplete',effect=history.effect(),completed=len(history.completed_refs)),
            {'grant':('decision',grant),'authorization':('decision',authorization),'history':('integrity',history_ref),'owner':('decision',owner),'previous':('provenance',previous)})
    def start(self,*,operation,run,receipt,statement,parent=None):
        from ..records import text
        text(statement);ref=self.store.head(prepared_key(run));require(ref is not None,'execution-grant-required')
        grant=self.grant(ref,self.store.load)
        require(receipt==self.service._receipt('execution-start',grant.payload['work'],ref),'execution-stale-start-receipt')
        if parent is not None:
            owner=self.obj(parent);require(parent.kind=='effect.owner' and owner.payload['kind']=='delivery-attempt','execution-parent-owner-required')
        auth=record('execution.authorization',dict(run=run,statement=statement),{'grant':('decision',ref)})
        owner=record('effect.owner',dict(kind='execution-run',identifier=run,key=key(run)),{'identity':('decision',ref),'parent':('decision',parent)})
        history=History(grant.payload['contract']);contract=history.grant
        row=self._row(history,'granted',dict(grant=contract['grant'],scope_sha256=schema.digest(history.scope),recovery_locator_sha256=schema.digest(contract['recovery_locator'])))
        history.apply(row);event=record('execution.event',dict(run=run,row=row),{'grant':('decision',ref),'result':('integrity',None),'resolution':('decision',None)})
        mapping=build_map([('00000001',event[0])]);size=len(canonical_bytes(row))
        h=record('execution.history',dict(run=run,count=1,bytes=size),{'events':('integrity',mapping.root),'previous':('provenance',None)})
        state=self._state(run,ref,auth[0],h[0],owner[0],history)
        def validate(view):
            from ..configuration import require_enabled
            guard(view,expected_effect=parent);require_enabled(view,'official-execution');self.live(grant,view)
            if parent is not None:
                from ..delivery.service import DeliveryService
                DeliveryService(self.service).execution_parent(parent,grant,view,view=view,admission=True)

            require(view.head(prepared_key(run))==ref,'execution-grant-changed')
            require(time.time_ns()<contract['scope']['limits']['expires_wall_ns'],'execution-deadline')
            validate_closure([state[0]],view,self.service.registry,self.service.closure)
        self.store.commit_heads(operation=operation,expected={key(run):None,PENDING:parent},changes={key(run):state[0],PENDING:owner[0]},
            objects=[auth,owner,event,*mapping.objects,h,state],validate=validate)
        return self.status(run)
    def read(self,run,load=None,ref=None):
        load=load or self.store.load;ref=ref or self.store.head(key(run));require(ref is not None,'execution-not-found')
        validate_closure([ref],load,self.service.registry,self.service.closure)
        state=self.obj(ref,load);require(ref.kind=='execution.state' and state.payload['run']==run,'execution-state-mismatch')
        grant=self.grant(link(state,'grant'),load);h=self.obj(link(state,'history'),load);owner=self.obj(link(state,'owner'),load)
        require(grant.payload['run']==run and h.payload['run']==run and owner.payload['kind']=='execution-run' and
                owner.payload['key']==key(run) and link(owner,'identity')==grant.ref,'execution-owner-mismatch')
        auth=self.obj(link(state,'authorization'),load);require(auth.payload['run']==run and link(auth,'grant')==grant.ref,'execution-authorization-mismatch')
        if link(owner,'parent') is not None:
            from ..delivery.service import DeliveryService
            DeliveryService(self.service).execution_parent(link(owner,'parent'),grant,load)

        events=read_map(link(h,'events'),load);require(set(events)=={f'{i:08d}' for i in range(1,h.payload['count']+1)},'execution-history-sequence')
        history=History(grant.payload['contract']);size=0
        for name in sorted(events):
            event=self.obj(events[name],load);require(events[name].kind=='execution.event' and event.payload['run']==run and link(event,'grant')==grant.ref,'execution-event-grant-mismatch')
            result=link(event,'result')
            if result is not None:
                body=descriptor(result,load(result));expected=event.payload['row']['value']['after']
                require(body.payload['size']==expected['size'] and body.payload['sha256']==expected['sha256'],'execution-result-body-mismatch')
            resolution=link(event,'resolution')
            if resolution is not None:
                decision=self.obj(resolution,load);prior=self.obj(link(decision,'history'),load)
                require(decision.payload['run']==run and link(decision,'grant')==grant.ref and
                    decision.payload['observation']==event.payload['row']['value'],'execution-resolution-binding')
                prefix=read_map(link(prior,'events'),load)
                require(prior.payload['run']==run and prior.payload['count']==len(history.rows) and
                    prefix=={k:v for k,v in events.items() if k<name},'execution-resolution-history-mismatch')
            history.apply(event.payload['row']);size+=len(canonical_bytes(event.payload['row']))
        require(size==h.payload['bytes'],'execution-history-size-mismatch')
        require((state.payload['status'],state.payload['effect'],state.payload['completed'])==
                (history.terminal or 'incomplete',history.effect(),len(history.completed_refs)),'execution-checkpoint-mismatch')
        return state,grant,h,owner,history
    def append(self,*,operation,run,kind,value,result_body=None,objects=(),import_id=None,expected_state=None):
        require(kind not in ('granted','operator-resolved-unknown'),'execution-special-publication-required')
        return self._append(operation=operation,run=run,kind=kind,value=value,result_body=result_body,objects=objects,import_id=import_id,expected_state=expected_state)
    def _append(self,*,operation,run,kind,value,result_body=None,objects=(),import_id=None,resolution=None,reobserve=None,expected_state=None):
        require(kind!='granted','execution-special-publication-required')
        require((kind=='operator-resolved-unknown')==(resolution is not None and callable(reobserve)),'execution-resolution-publication-required')
        state,grant,h,owner,history=self.read(run);require(history.terminal not in schema.CLOSED,'execution-already-terminal')
        require(expected_state is None or state.ref==expected_state,'execution-state-changed')
        row=self._row(history,kind,value);history.apply(row);size=h.payload['bytes']+len(canonical_bytes(row));history_bounds(len(history.rows),size)
        event=record('execution.event',dict(run=run,row=row),{'grant':('decision',grant.ref),'result':('integrity',result_body),'resolution':('decision',resolution)})
        mapping=map_update(link(h,'events'),{f'{row["seq"]:08d}':event[0]},self.store.load)
        newhistory=record('execution.history',dict(run=run,count=len(history.rows),bytes=size),{'events':('integrity',mapping.root),'previous':('provenance',h.ref)})
        newstate=self._state(run,grant.ref,link(state,'authorization'),newhistory[0],owner.ref,history,state.ref)
        closed=history.terminal in schema.CLOSED
        completing=kind=="terminal" and value["status"]=="completed"
        def validate(view):
            guard(view,expected_effect=owner.ref);self.live(grant,view)
            if link(owner,'parent') is not None:
                from ..delivery.service import DeliveryService
                request=DeliveryService(self.service).execution_parent(link(owner,'parent'),grant,view,view=view,
                    admission=is_authority_event(kind,value))
                if completing:
                    from ..delivery.service import cancel_key as parent_cancel
                    require(view.head(parent_cancel(request.payload["delivery"])) is None,"execution-cancel-requested")
            if completing:
                require(view.head(cancel_key(run)) is None,"execution-cancel-requested")
            if is_authority_event(kind,value):
                require(view.head(cancel_key(run)) is None,'execution-cancel-requested')
                require(time.time_ns()<history.scope['limits']['expires_wall_ns'],'execution-deadline')
            if reobserve is not None:
                require(reobserve()==value,'execution-resolution-observation-changed')
                decision=self.obj(resolution,view)
                require(link(decision,'history')==h.ref,'execution-resolution-history-mismatch')
            self.read(run,view,newstate[0])
        self.store.commit_heads(operation=operation,expected={key(run):state.ref,PENDING:owner.ref},
            changes={key(run):newstate[0],**({PENDING:link(owner,'parent')} if closed else {})},objects=[*objects,event,*mapping.objects,newhistory,newstate],import_id=import_id,validate=validate)
        return self.status(run)
    def cancel(self,*,operation,run,reason):
        schema.choice(reason,schema.REASONS);state,grant,_,owner,history=self.read(run)
        require(history.terminal not in schema.CLOSED,'execution-already-terminal');old=self.store.head(cancel_key(run))
        if old is not None:
            previous=self.obj(old);require(previous.payload['reason']==reason and link(previous,'grant')==grant.ref,'execution-cancel-request-differs')
            return dict(run=run,cancel_requested=True,effects_stopped=False)
        pair=record('execution.cancel',dict(run=run,reason=reason),{'grant':('decision',grant.ref)})
        def validate(view):
            require(view.head(PENDING)==owner.ref,'execution-owner-changed')
            require(view.head(key(run))==state.ref,'execution-state-changed')
        self.store.commit_heads(operation=operation,expected={cancel_key(run):None,key(run):state.ref},changes={cancel_key(run):pair[0]},objects=[pair],validate=validate)
        return dict(run=run,cancel_requested=True,effects_stopped=False)
    def status(self,run):
        state,grant,_,_,history=self.read(run)
        return dict(run=run,work=grant.payload['work'],status=history.terminal or 'incomplete',document_write_effect=history.effect(),
            completed=len(history.completed_refs),cancel_requested=self.store.head(cancel_key(run)) is not None,accepted=False)

    def cancel_requested(self,run,owner=None):
        if self.store.head(cancel_key(run)) is not None:return True
        if owner is None:owner=self.read(run)[3]
        parent=link(owner,'parent')
        if parent is None:return False
        from ..delivery.service import cancel_key as delivery_cancel
        parent=self.obj(parent)
        return self.store.head(delivery_cancel(parent.payload['identifier'])) is not None
