"""One approved handoff, with exact atomic submission and no OS notification.

Ordinary Work writers never receive a generic pending-effect bypass. Only the
validated submit request below can publish its retained prepared result while
owning its exact delivery attempt. Execution delegation is validated separately.
"""
import time,uuid
from contextlib import nullcontext
from ..codec import require
from ..records import record,link,head_summary,text
from ..connection import workspace_key,PROJECT_KEY
from ..work import work_key
from ..effects import guard,PENDING
from ..graph import validate_closure
from ..observation import verify_scope
from ..storage.sqlite import _token

OUTSTANDING='delivery:outstanding'

def key(delivery):_token(delivery);return 'delivery:'+delivery
def prepared_key(delivery):_token(delivery);return 'delivery-prepared:'+delivery
def cancel_key(delivery):_token(delivery);return 'delivery-cancel:'+delivery
def notice_key(delivery):_token(delivery);return 'notice:'+delivery

class DeliveryService:
    def __init__(self,service):self.service=service;self.store=service.store
    def obj(self,ref,load=None):return self.service._object(ref,load)
    def request(self,ref,load=None):
        load=load or self.store.load
        validate_closure([ref],load,self.service.registry,self.service.closure)
        request=self.obj(ref,load);require(ref.kind=='delivery.request','delivery-request-required')
        head,plan,_,_=head_summary(link(request,'head'),load);self.service._validate_head(head.ref,load)
        require(request.payload['work']==head.payload['work'] and request.payload['workspace']==head.payload['workspace'],'delivery-work-mismatch')
        registration=self.obj(link(request,'registration'),load)
        require(registration.payload['workspace']==request.payload['workspace'],'delivery-registration-mismatch')
        prepared=link(request,'prepared')
        if prepared is not None:
            self.service._validate_head(prepared,load);candidate,_,result,_=head_summary(prepared,load)
            require(head.payload['phase']=='active' and candidate.payload['phase']=='review' and
                candidate.payload['work']==head.payload['work'] and candidate.payload['workspace']==head.payload['workspace'] and
                link(candidate,'plan')==plan.ref and link(candidate,'previous')==head.ref and
                link(candidate,'approval')==link(head,'approval'),'delivery-prepared-head-mismatch')
        grant=link(request,'grant')
        if grant is not None:
            from ..execution.journal import ExecutionJournal
            value=ExecutionJournal(self.service).grant(grant,load)
            require(link(value,'head')==head.ref and link(value,'registration')==registration.ref and
                value.payload['contract']['scope']['limits']['expires_wall_ns']<=request.payload['deadline_ns'],'delivery-grant-mismatch')
        return request
    def live(self,request,view,*,deadline=True):
        from ..group_guard import guard as group_guard
        group_guard(view,request.payload['work'])
        registration=self.obj(link(request,'registration'),view)
        require(view.head(work_key(request.payload['work']))==link(request,'head') and
            view.head(workspace_key(request.payload['workspace']))==registration.ref and
            view.head(PROJECT_KEY)==link(registration,'project'),'delivery-dependency-changed')
        if deadline:require(time.time_ns()<request.payload['deadline_ns'],'delivery-deadline')
        if link(request,'prepared') is not None:
            from ..composition import validate_transition
            candidate,plan,result,_=head_summary(link(request,'prepared'),view)
            validate_transition(link(request,'head'),candidate,plan,result,view)

    def _state(self,request,authorization,phase,*,attempt=None,owner=None,outcome=None,previous=None):
        return record('delivery.state',dict(delivery=request.payload['delivery'],phase=phase),
            {'request':('decision',request.ref),'authorization':('decision',authorization),'attempt':('decision',attempt),
             'owner':('decision',owner),'outcome':('decision',outcome),'previous':('provenance',previous)})
    def read(self,delivery,load=None,ref=None):
        load=load or self.store.load;ref=ref or self.store.head(key(delivery));require(ref is not None,'delivery-not-found')
        validate_closure([ref],load,self.service.registry,self.service.closure)
        state=self.obj(ref,load);require(ref.kind=='delivery.state' and state.payload['delivery']==delivery,'delivery-state-mismatch')
        request=self.request(link(state,'request'),load);auth=self.obj(link(state,'authorization'),load)
        require(request.payload['delivery']==delivery and auth.payload['delivery']==delivery and link(auth,'request')==request.ref,'delivery-authorization-mismatch')
        if link(state,'attempt') is not None:
            attempt=self.obj(link(state,'attempt'),load);owner=self.obj(link(state,'owner'),load)
            require(attempt.payload['delivery']==delivery and link(attempt,'request')==request.ref and
                link(attempt,'authorization')==auth.ref and owner.payload==dict(kind='delivery-attempt',identifier=delivery,key=key(delivery),links=owner.payload['links']) and
                link(owner,'identity')==attempt.ref and link(owner,'parent') is None,'delivery-owner-mismatch')
        outcome=link(state,'outcome')
        if outcome is not None:
            outcome=self.obj(outcome,load)
            require(outcome.payload['delivery']==delivery and link(outcome,'request')==request.ref,'delivery-outcome-mismatch')
            kind=outcome.payload['kind'];action=request.payload['action']
            require((state.payload['phase'],kind) in (('finished','observed'),('finished','submitted'),('finished','executed'),('cancelled','cancelled'),('failed','failed')),'delivery-outcome-phase')
            if kind=='submitted':require(action=='submit' and link(outcome,'head')==link(request,'prepared'),'delivery-outcome-result')
            if kind=='observed':require(action=='inspect' and link(outcome,'head')==link(request,'head'),'delivery-outcome-result')
            if kind=='executed':
                from ..execution.journal import ExecutionJournal
                from ..execution.schema import CLOSED
                result=self.obj(link(outcome,'execution'),load)
                child,grant,_,owner,history=ExecutionJournal(self.service).read(result.payload['run'],load,result.ref)
                require(action=='execute' and grant.ref==link(request,'grant') and link(owner,'parent')==link(state,'owner') and
                    history.terminal in CLOSED,'delivery-unclosed-execution')
        return state,request
    def prepare(self,*,operation,delivery,work,action,deadline_ns,receiver=None,summary=None,checks=None,grant=None):
        require(action in ('inspect','submit','execute') and type(deadline_ns) is int and
            time.time_ns()<deadline_ns<=time.time_ns()+86400*10**9,'delivery-request-bound')
        ref,head=self.service._head(work);registration,_,_=self.service.workspace.verify()
        require((grant is not None)==(action=='execute'),'delivery-action-input')
        require(action=='submit' or (summary is None and checks is None),'delivery-unexpected-input')
        preparation=(self.service._prepare_submission(operation=operation,work=work,summary=summary,checks=checks)
                     if action=='submit' else nullcontext(None))
        with preparation as capture:
            objects=[];prepared=None
            if capture:
                require(capture['expected']==ref,'delivery-dependency-changed')
                prepared=capture['head'][0];objects=[*capture['objects'],capture['head']]
            pair=record('delivery.request',dict(delivery=delivery,work=work,workspace=head.payload['workspace'],action=action,
                deadline_ns=deadline_ns,steps=1,receiver=receiver),{'head':('decision',ref),'registration':('decision',registration),
                'prepared':('decision',prepared),'grant':('decision',grant)})
            require(len(pair[1])<=1048576,'delivery-request-size')
            def validate(view):
                guard(view);request=self.request(pair[0],view);self.live(request,view)
                if capture:
                    for key,value in capture['pinned'].items():require(view.head(key)==value,'attribution-peer-changed')
                    if capture['pinned_root'] is not None:require(view.root().ref==capture['pinned_root'],'attribution-heads-changed')
                    self.service._recheck_observation(capture['current'],capture['scope'])
            self.store.commit_heads(operation=operation,expected={prepared_key(delivery):None},changes={prepared_key(delivery):pair[0]},
                objects=[*objects,pair],import_id=operation if capture else None,validate=validate)
        return dict(delivery=delivery,work=work,title=head.payload['title'],deadline_ns=deadline_ns,action=action,receiver=receiver,
            receipt=self.service._receipt('delivery-start',work,pair[0]),state='prepared')
    def start(self,*,operation,delivery,receipt,statement):
        ref=self.store.head(prepared_key(delivery));require(ref is not None,'delivery-request-required');request=self.request(ref)
        require(receipt==self.service._receipt('delivery-start',request.payload['work'],ref),'delivery-stale-receipt');text(statement)
        auth=record('delivery.authorization',dict(delivery=delivery,statement=statement),{'request':('decision',ref)})
        state=self._state(request,auth[0],'queued')
        def validate(view):
            guard(view);self.live(request,view);self.read(delivery,view,state[0])
        self.store.commit_heads(operation=operation,expected={key(delivery):None,prepared_key(delivery):ref,OUTSTANDING:None},
            changes={key(delivery):state[0],OUTSTANDING:ref},objects=[auth,state],validate=validate)
        return self.status(delivery)
    def _held(self,effects,request):
        require(effects.locked,'effect-lock-required')
        registration,_,_=self.service.workspace.verify()
        require(registration==link(request,'registration') and effects.root==self.service.workspace.root,'delivery-native-workspace')
        # Concrete port rechecks root and private lock-area identities.
        with effects._root(),effects._authority():pass
    def claim(self,*,operation,delivery,effects):
        state,request=self.read(delivery);require(state.payload['phase']=='queued' and request.payload['action']!='inspect','delivery-not-claimable')
        self._held(effects,request)
        attempt=record('delivery.attempt',dict(delivery=delivery,attempt=uuid.uuid4().hex),
            {'request':('decision',request.ref),'authorization':('decision',link(state,'authorization'))})
        owner=record('effect.owner',dict(kind='delivery-attempt',identifier=delivery,key=key(delivery)),{'identity':('decision',attempt[0]),'parent':('decision',None)})
        new=self._state(request,link(state,'authorization'),'active',attempt=attempt[0],owner=owner[0],previous=state.ref)
        def validate(view):
            guard(view);self.live(request,view);require(view.head(cancel_key(delivery)) is None,'delivery-cancelled')
            if request.payload['action']=='execute':
                from ..execution.journal import key as execution_key
                grant=self.obj(link(request,'grant'),view)
                require(view.head(execution_key(grant.payload['run'])) is None,'delivery-child-already-started')
            self.read(delivery,view,new[0]);self._held(effects,request)
        self.store.commit_heads(operation=operation,expected={key(delivery):state.ref,OUTSTANDING:request.ref,PENDING:None},
            changes={key(delivery):new[0],PENDING:owner[0]},objects=[attempt,owner,new],validate=validate)
        return self.status(delivery)
    def _finish(self,*,operation,state,request,kind,result=None,execution=None,objects=(),recheck=lambda:None,cancellation=None,cancel_observation=()):
        delivery=request.payload['delivery'];phase='finished' if kind in ('observed','submitted','executed') else kind
        outcome=record('delivery.outcome',dict(delivery=delivery,kind=kind),{'request':('decision',request.ref),'head':('decision',result),'execution':('decision',execution)})
        new=self._state(request,link(state,'authorization'),phase,attempt=link(state,'attempt'),owner=link(state,'owner'),outcome=outcome[0],previous=state.ref)
        additions=[*objects,outcome,new];changes={key(delivery):new[0],OUTSTANDING:None};expected={key(delivery):state.ref,OUTSTANDING:request.ref}
        owner=link(state,'owner')
        if cancel_observation:expected[cancel_key(delivery)]=cancel_observation[0]
        if cancellation is not None:
            require(kind=='cancelled' and state.payload['phase']=='queued','delivery-cancel-phase')
            additions.append(cancellation);expected[cancel_key(delivery)]=None;changes[cancel_key(delivery)]=cancellation[0]
        if owner is not None:expected[PENDING]=owner;changes[PENDING]=None
        if kind=='submitted':expected[work_key(request.payload['work'])]=link(request,'head');changes[work_key(request.payload['work'])]=result
        if request.payload['receiver'] is not None and phase=='finished':
            notice=record('notice.event',dict(delivery=delivery,project=self.store.project,instance=self.store.instance,receiver=request.payload['receiver']),
                {'outcome':('decision',outcome[0]),'authorization':('decision',link(state,'authorization')),'attempt':('decision',link(state,'attempt'))})
            additions.append(notice);expected[notice_key(delivery)]=None;changes[notice_key(delivery)]=notice[0]
        def validate(view):
            if owner is not None:guard(view,expected_effect=owner)
            if kind in ('observed','submitted'):
                self.live(request,view);require(view.head(cancel_key(delivery)) is None,'delivery-cancelled')
            # Known execution evidence survives expiry/cancel; it is not a new effect.
            self.read(delivery,view,new[0]);recheck()
        self.store.commit_heads(operation=operation,expected=expected,changes=changes,objects=additions,validate=validate)
        return self.status(delivery)
    def inspect(self,*,operation,delivery):
        state,request=self.read(delivery)
        require(state.payload['phase']=='queued' and request.payload['action']=='inspect','delivery-not-inspection')
        return self._finish(operation=operation,state=state,request=request,kind='observed',result=link(request,'head'))
    def submit(self,*,operation,delivery,effects):
        state,request=self.read(delivery)
        require(state.payload['phase']=='active' and request.payload['action']=='submit','delivery-not-submission');self._held(effects,request)
        prepared=self.obj(link(request,'prepared'));plan=self.obj(link(prepared,'plan'));result=self.obj(link(prepared,'result'))
        from ..rework import attribution,effective_entries
        _,_,current=self.service._observe_from_plan(plan,attribution(result,self.store.load))
        entries=effective_entries(self.service,plan,result,self.store.load)
        scope=frozenset(plan.payload['scope']);changed=verify_scope(entries,current.snapshot.entries,scope)
        observed=self.obj(link(result,'observation'))
        from ..tree import read_tree
        require(tuple(read_tree(link(observed,'tree'),self.store.load))==current.snapshot.entries and
            list(changed)==result.payload['changed'],'delivery-prepared-files-changed')
        def recheck():self._held(effects,request);self.service._recheck_observation(current,scope)
        return self._finish(operation=operation,state=state,request=request,kind='submitted',result=prepared.ref,recheck=recheck)
    def cancel(self,*,operation,delivery,statement):
        state,request=self.read(delivery);text(statement)
        require(state.payload['phase'] in ('queued','active'),'delivery-already-terminal')
        if state.payload['phase']=='queued':
            pair=record('delivery.cancel',dict(delivery=delivery,statement=statement),{'request':('decision',request.ref)})
            return self._finish(operation=operation,state=state,request=request,kind='cancelled',cancellation=pair)
        old=self.store.head(cancel_key(delivery))
        if old is not None:
            previous=self.obj(old);require(link(previous,'request')==request.ref and previous.payload['statement']==statement,'delivery-cancel-differs')
            return self.status(delivery)
        pair=record('delivery.cancel',dict(delivery=delivery,statement=statement),{'request':('decision',request.ref)})
        self.store.commit_heads(operation=operation,expected={key(delivery):state.ref,cancel_key(delivery):None},
            changes={cancel_key(delivery):pair[0]},objects=[pair],validate=lambda view:self.read(delivery,view))
        return self.status(delivery)
    def status(self,delivery):
        state,request=self.read(delivery)
        head,_,_,_=head_summary(link(request,'head'),self.store.load)
        return dict(delivery=delivery,work=request.payload['work'],title=head.payload['title'],action=request.payload['action'],state=state.payload['phase'],
            cancel_requested=self.store.head(cancel_key(delivery)) is not None,accepted=False)

    def execution_parent(self,parent,grant,load=None,*,view=None,admission=False):
        load=load or self.store.load
        owner=self.obj(parent,load);require(parent.kind=='effect.owner' and owner.payload['kind']=='delivery-attempt','execution-parent-owner-required')
        attempt=self.obj(link(owner,'identity'),load);request=self.request(link(attempt,'request'),load)
        auth=self.obj(link(attempt,'authorization'),load)
        require(attempt.ref.kind=='delivery.attempt' and attempt.payload['delivery']==owner.payload['identifier']==request.payload['delivery'] and
            owner.payload['key']==key(request.payload['delivery']) and link(owner,'parent') is None and
            auth.payload['delivery']==request.payload['delivery'] and link(auth,'request')==request.ref and
            request.payload['action']=='execute' and link(request,'grant')==grant.ref and
            link(request,'head')==link(grant,'head') and link(request,'registration')==link(grant,'registration') and
            grant.payload['contract']['scope']['limits']['expires_wall_ns']<=request.payload['deadline_ns'],'execution-parent-request-mismatch')
        if view is not None:
            state,_=self.read(request.payload['delivery'],view,view.head(key(request.payload['delivery'])))
            require(state.payload['phase']=='active' and link(state,'owner')==parent and link(state,'attempt')==attempt.ref and
                view.head(OUTSTANDING)==request.ref,'execution-parent-not-active')
            if admission:
                self.live(request,view)
                require(view.head(cancel_key(request.payload['delivery'])) is None,'delivery-cancelled')
        return request
    def finish_execution(self,*,operation,delivery,run,effects):
        from ..execution.journal import ExecutionJournal,key as execution_key
        from ..execution.schema import CLOSED
        state,request=self.read(delivery)
        require(state.payload['phase']=='active' and request.payload['action']=='execute','delivery-not-execution');self._held(effects,request)
        child,grant,_,owner,history=ExecutionJournal(self.service).read(run)
        require(grant.ref==link(request,'grant') and link(owner,'parent')==link(state,'owner') and history.terminal in CLOSED,'delivery-unclosed-execution')
        def recheck():
            require(self.store.head(execution_key(run))==child.ref,'delivery-execution-changed');self._held(effects,request)
        return self._finish(operation=operation,state=state,request=request,kind='executed',execution=child.ref,recheck=recheck)

    def finish_unstarted_execution(self,*,operation,delivery,effects):
        from ..execution.journal import key as execution_key
        state,request=self.read(delivery)
        require(request.payload['action']=='execute','delivery-not-execution')
        require(state.payload['phase']=='active','delivery-not-active')
        self._held(effects,request);grant=self.obj(link(request,'grant'))
        def recheck():
            self._held(effects,request)
            require(self.store.head(execution_key(grant.payload['run'])) is None,'delivery-child-already-started')
        recheck()
        cancellation=self.store.head(cancel_key(delivery))
        kind='cancelled' if cancellation is not None else 'failed'
        return self._finish(operation=operation,state=state,request=request,kind=kind,recheck=recheck,cancel_observation=(cancellation,))

    def cancel_unstarted(self,*,operation,delivery,effects):
        state,request=self.read(delivery);require(state.payload['phase']=='active','delivery-not-active');self._held(effects,request)
        require(self.store.head(cancel_key(delivery)) is not None,'delivery-cancel-required')
        def recheck():
            self._held(effects,request)
            if request.payload['action']=='execute':
                from ..execution.journal import key as execution_key
                grant=self.obj(link(request,'grant'))
                require(self.store.head(execution_key(grant.payload['run'])) is None,'delivery-child-already-started')
        return self._finish(operation=operation,state=state,request=request,kind='cancelled',recheck=recheck)
    def preview(self,delivery):
        ref=self.store.head(prepared_key(delivery));require(ref is not None,'delivery-request-required');request=self.request(ref)
        head,_,_,_=head_summary(link(request,'head'),self.store.load)
        return dict(delivery=delivery,work=request.payload['work'],title=head.payload['title'],action=request.payload['action'],
            deadline_ns=request.payload['deadline_ns'],receiver=request.payload['receiver'],state='prepared',
            receipt=self.service._receipt('delivery-start',request.payload['work'],ref))
