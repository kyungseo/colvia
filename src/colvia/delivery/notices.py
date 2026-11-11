"""Original outcome details and a one-shot notification emission boundary.

Platform emission is an explicitly supplied qualified port. Core stores intent
before calling it, never repeats an ambiguous emission, and never interprets a
click or emitter response as Work acceptance. No OS adapter is selected here.
"""
from ..codec import require,RecordError
from ..records import record,link,head_summary
from ..graph import validate_closure
from ..work import work_key
from ..storage.sqlite import _token
from .service import notice_key,key


def emission_key(delivery):_token(delivery);return 'notice-emission:'+delivery

class Notices:
    def __init__(self,delivery):self.delivery=delivery;self.service=delivery.service;self.store=delivery.store
    def event(self,delivery,*,ref=None,load=None):
        load=load or self.store.load;ref=ref or self.store.head(notice_key(delivery));require(ref is not None,'notice-not-found')
        validate_closure([ref],load,self.service.registry,self.service.closure)
        event=self.delivery.obj(ref,load)
        require(ref.kind=='notice.event' and event.payload['delivery']==delivery and
            event.payload['project']==self.store.project and event.payload['instance']==self.store.instance,'notice-identity-mismatch')
        state,request=self.delivery.read(delivery,load)
        require(state.payload['phase']=='finished' and link(state,'outcome')==link(event,'outcome') and
            link(state,'authorization')==link(event,'authorization') and link(state,'attempt')==link(event,'attempt') and
            request.payload['receiver']==event.payload['receiver'],'notice-outcome-mismatch')
        return event,state,request
    def details(self,delivery,*,project,instance,event_ref):
        require(project==self.store.project and instance==self.store.instance,'notice-route-mismatch')
        event,state,request=self.event(delivery,ref=event_ref)
        require(self.store.head(notice_key(delivery))==event.ref,'notice-route-mismatch')
        outcome=self.delivery.obj(link(event,'outcome'));kind=outcome.payload['kind']
        if kind in ('observed','submitted'):
            head,_,result,_=head_summary(link(outcome,'head'),self.store.load)
            original=dict(kind=kind,title=head.payload['title'],state=head.payload['phase'],summary=result.payload['summary'] if result else None,
                files=result.payload['changed'] if result else [])
        else:
            from ..execution.journal import ExecutionJournal
            executed=self.delivery.obj(link(outcome,'execution'))
            _,_,_,_,history=ExecutionJournal(self.service).read(executed.payload['run'],ref=executed.ref)
            original=dict(kind='executed',run=executed.payload['run'],status=history.terminal,
                document_write_effect=history.effect(),work_submitted=False)
        try:current=self.service.view(request.payload['work'])
        except RecordError as exc:current=dict(unavailable=exc.code)
        try:self.service.workspace.verify();connected=True
        except (OSError,RecordError):connected=False
        return dict(work=request.payload['work'],original=original,current=current,workspace_connected=connected,
            next_action='review_in_project' if connected else 'reconnect_project',click_accepts=False)
    def emit(self,*,operation,delivery,port):
        event,_,_=self.event(delivery);emission=emission_key(delivery)
        require(self.store.head(emission) is None,'notice-emission-already-attempted')
        port.check(event.payload['receiver'])
        intent=record('notice.emission',dict(delivery=delivery,phase='intent'),{'event':('decision',event.ref),'previous':('provenance',None)})
        def validate(view):
            require(view.head(notice_key(delivery))==event.ref,'notice-event-changed');self.event(delivery,ref=event.ref,load=view)
        # A lost acknowledgement here never authorizes calling the port.
        self.store.commit_heads(operation=operation+'-intent',expected={emission:None},changes={emission:intent[0]},objects=[intent],validate=validate)
        try:
            # Route fields only: neither result text nor local paths enter a banner.
            status=port.emit(dict(project=event.payload['project'],instance=event.payload['instance'],
                delivery=delivery,event=event.ref.as_dict(),receiver=event.payload['receiver']))
            require(status in ('emitted','failed','unknown'),'notice-port-result')
        except Exception:status='unknown'
        outcome=record('notice.emission',dict(delivery=delivery,phase=status),{'event':('decision',event.ref),'previous':('provenance',intent[0])})
        self.store.commit_heads(operation=operation+'-result',expected={emission:intent[0]},changes={emission:outcome[0]},objects=[outcome],validate=validate)
        return dict(delivery=delivery,notification=status,accepted=False)
