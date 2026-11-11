"""Live callback admission over a persistent journal, without process launch.

Only a fresh run can create this binding. The native port must hold the common
lock and reobserve runtime resources, documents and the whole project outside the
one output before admission. Call IDs and rejected input never enter history.
"""
import copy,time,uuid
from ..codec import RecordError,PublicationRefused,require
from ..effects import PENDING
from .guards import checked_payload
from . import schema

STEPS=(('document_read','read',None),('document_write','write',None),
       *(('document_verify','verify',name) for name in schema.VERIFIERS))

class CallbackGate:
    def __init__(self,journal,run,native):
        self.journal=journal;self.run=run;self.native=native
        _,grant,_,owner,history=journal.read(run)
        require(len(history.rows)==1,'execution-live-restore-refused')
        native.assert_held(grant,owner)
        self.grant=grant;self.owner=owner;self.scope=grant.payload['contract']['scope']
        limits=self.scope['limits']
        self.deadline=time.monotonic()+min(limits['seconds'],max(0,(limits['expires_wall_ns']-time.time_ns())/1e9))
        self.thread=self.turn=None;self.seen=set();self.calls=0
        self.failed=False
        native.startup(grant,history,self.deadline)

    def append(self,kind,value,**kwargs):
        # A commit failure is not permission to replay the event under a new ID.
        require(not self.failed,'execution-publication-uncertain')
        try:
            return self.journal.append(operation='execution-event-'+uuid.uuid4().hex,
                run=self.run,kind=kind,value=value,**kwargs)
        except PublicationRefused:
            # A different closure event may still be recorded. Do not replay
            # the refused event or clear a genuinely uncertain acknowledgement.
            raise
        except BaseException:
            self.failed=True
            raise

    def observe_live(self,*,allow_cancel=False):
        require(not self.failed,'execution-publication-uncertain')
        _,grant,_,owner,history=self.journal.read(self.run)
        require(grant.ref==self.grant.ref and owner.ref==self.owner.ref and
            self.journal.store.head(PENDING)==owner.ref,'execution-live-owner-changed')
        self.journal.live(grant,self.journal.store)
        require(history.terminal is None and history.runtime_close is None,'execution-authority-closed')
        require(time.monotonic()<self.deadline and time.time_ns()<self.scope['limits']['expires_wall_ns'],'deadline')
        if not allow_cancel:require(not self.journal.cancel_requested(self.run,owner),'cancelled')
        self.native.assert_held(grant,owner)
        self.native.preflight(grant,history)
        return history

    def authority(self):
        history=self.observe_live();history.active();return history

    def bind(self,thread,turn):
        self.authority()
        require(self.thread is None and self.turn is None and
            all(type(s) is str and 0<len(s.encode('utf-8'))<256 for s in (thread,turn)),'caller_mismatch')
        self.append('bound',dict(ordinal=1,established=True))
        self.thread,self.turn=thread,turn

    def reserve(self,envelope):
        """Return a persisted callback reservation, never permission to accept Work."""
        history=self.authority();self.calls+=1
        require(self.calls<=8 and self.thread is not None and history.pending is None and
            len(history.completed_refs)<5 and len(history.workers)<self.scope['limits']['worker_limit'],'order_mismatch')
        require(type(envelope) is dict and set(envelope) in (
            {'threadId','turnId','callId','tool','arguments'},
            {'threadId','turnId','callId','tool','arguments','namespace'}),'input_shape')
        require(envelope['threadId']==self.thread and envelope['turnId']==self.turn and
            envelope.get('namespace') is None,'caller_mismatch')
        call=envelope['callId']
        require(type(call) is str and 0<len(call.encode('utf-8'))<256 and call not in self.seen,'caller_mismatch')
        checked_payload(envelope,limit=65536,deadline=self.deadline)
        step=len(history.completed_refs);tool,role,verifier=STEPS[step]
        args=envelope['arguments'];output=self.scope['output_id']
        require(envelope['tool']==tool and type(args) is dict,'input_shape')
        if step==0:require(args=={'file_ids':self.scope['read_ids']},'scope_mismatch')
        elif step==1:
            require(set(args)=={'file_id','expected_sha256','content'} and args['file_id']==output and
                args['expected_sha256']==self.scope['documents'][output]['original_identity']['sha256'] and
                type(args['content']) is str and len(args['content'].encode('utf-8'))<=65536,'scope_mismatch')
        else:require(args=={'verifier_id':verifier},'order_mismatch')
        # Composition/exposure checking occurs before recovery or worker intent.
        self.native.callback_preflight(self.grant,history,tool,args,self.deadline)
        if role=='write':
            metadata=self.native.save_original(self.grant,history)
            self.append('recovery-ready',metadata)
        callback=history.next_callback
        self.append('callback-reserved',dict(callback_id=callback,ordinal=step+1,tool=role,
            file_ids=self.scope['read_ids'] if role=='read' else [output] if role=='write' else [],
            verifier_id=verifier,expected_identity=self.scope['documents'][output]['original_identity'] if role=='write' else None))
        self.seen.add(call)
        return dict(callback_id=callback,tool=tool,arguments=copy.deepcopy(args))

    def refuse(self,reason,role='invalid',phase='callback_preflight'):
        schema.choice(reason,schema.REASONS)
        history=self.journal.read(self.run)[-1]
        self.append('callback-refused',dict(callback_id=history.next_callback,tool=role,phase=phase,
            reason=reason,current_call_effect='not_started'))
        return dict(ok=False,worker_admitted=False,effect_status='not_started',reason=reason)

    def complete(self):
        # Closure and result evidence remain recordable after cancel/expiry.
        history=self.journal.read(self.run)[-1];callback=history.pending
        require(callback is not None,'execution-no-pending-callback')
        item=history.callbacks[callback];ordinal=item['worker']
        if ordinal is None:
            self.append('callback-aborted-before-spawn',dict(callback_id=callback,reason='worker_failed'))
            return False
        worker=history.workers[ordinal]
        if worker['failure'] is not None:
            value=dict(callback_id=callback,success=False,result_ref=None,
                closure_ref=worker['failure']['seq'],failure_code='spawn_failed')
        else:
            require(worker['result'] is not None and worker['close'] is not None,'closure_unconfirmed')
            value=dict(callback_id=callback,success=worker['result']['value']['success'],
                result_ref=worker['result']['seq'],closure_ref=worker['close']['seq'],
                failure_code=worker['result']['value']['reason'])
        self.append('callback-completed',value)
        return value['success']

    def checked_reply(self,value):
        # Do not send read content after a cancellation/expiry observed at reply.
        self.authority()
        require(self.journal.read(self.run)[-1].pending is None,'closure_unconfirmed')
        checked_payload(value,limit=64000,deadline=self.deadline)
        return value
