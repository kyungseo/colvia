"""One bounded document conversation over an already admitted runtime channel.

The channel must own its verified process, bounded IO and observed closure. This
adapter never launches a process, changes permissions, accepts Work or persists
model text/account data. Unknown notifications and native tool items refuse.
"""
import time
from ..codec import require,RecordError
from ..execution.guards import wire_bytes,checked_payload
from .bounded_rpc import FrameSink,checked_frame
from .codex_documents import PROFILE

STARTUP=frozenset(('remoteControl/status/changed','account/updated','thread/started',
    'thread/status/changed','turn/started'))
ITEMS=frozenset(('dynamicToolCall','reasoning','agentMessage','userMessage'))
NOTIFICATIONS=STARTUP|frozenset(('item/started','item/completed','item/agentMessage/delta',
    'item/reasoning/textDelta','item/reasoning/summaryTextDelta','item/reasoning/summaryPartAdded',
    'thread/tokenUsage/updated','turn/completed'))

class DocumentSession:
    def __init__(self,gate,policy,channel,*,cwd):
        policy.bind(gate.grant.payload['contract'])
        self.gate=gate;self.policy=policy;self.channel=channel;self.cwd=cwd
        self.sink=FrameSink(channel.write,deadline=gate.deadline)
        self.sequence=0;self.consumed=set();self.held=[];self.failed=False;self.stopped=False
        self.incoming_bytes=0;self.incoming_count=0;self.thread=None;self.turn=None
    def health(self,*,allow_cancel=False):
        require(not self.failed and not self.sink.partial,'protocol_refused')
        require(allow_cancel or not self.stopped,'cancelled')
        require(time.monotonic()<self.gate.deadline,'deadline')
        self.channel.check()  # bounded diagnostic/drift check, no raw output
        self.gate.observe_live(allow_cancel=allow_cancel)
    def send(self,value,*,allow_cancel=False):
        self.health(allow_cancel=allow_cancel)
        raw=checked_frame(value,deadline=self.gate.deadline)
        require(self.sink.bytes_sent+len(raw)<=1048576 and self.sink.frames_sent<32,'protocol_limit')
        try:self.sink.send(value)
        except BaseException:self.failed=True;raise
    def next(self,deadline,*,allow_cancel=False):
        self.health(allow_cancel=allow_cancel)
        message=self.channel.read(min(deadline,self.gate.deadline))
        # The transport bounds shape/depth before returning decoded data.
        size=len(wire_bytes(message));self.incoming_bytes+=size;self.incoming_count+=1
        require(self.incoming_bytes<=1048576 and self.incoming_count<=4096,'protocol_limit')
        require(type(message) is dict,'protocol_shape')
        self.health(allow_cancel=allow_cancel)
        return message
    def notification(self,message,*,preflight=False):
        require(type(message) is dict and set(message)<= {'method','params'} and 'method' in message,'protocol_notification')
        method=message['method'];value=message.get('params',{})
        require(type(method) is str and method in (STARTUP if preflight else NOTIFICATIONS) and type(value) is dict,'protocol_notification')
        if method=='remoteControl/status/changed':require(value.get('status')=='disabled','protocol_remote_control')
        if 'threadId' in value and self.thread is not None:require(value['threadId']==self.thread,'caller_mismatch')
        if 'turnId' in value and self.turn is not None:require(value['turnId']==self.turn,'caller_mismatch')
        if method in ('item/started','item/completed'):
            item=value.get('item');require(type(item) is dict and item.get('type') in ITEMS,'protocol_native_item')
        if method in ('thread/started','turn/started'):
            name=method.split('/')[0];item=value.get(name)
            require(type(item) is dict and type(item.get('id')) is str,'protocol_identity')
            expected=self.thread if name=='thread' else self.turn
            if expected is not None:require(item['id']==expected,'caller_mismatch')
        if method=='turn/completed':
            require(value.get('threadId')==self.thread and type(value.get('turn')) is dict and
                value['turn'].get('id')==self.turn,'caller_mismatch')
            return value['turn']
        return None
    def request(self,method,params,*,seconds=30):
        require(method not in self.consumed,'protocol_duplicate_request')
        allow_cancel=method=='turn/interrupt'
        self.health(allow_cancel=allow_cancel)
        self.gate.append('rpc-reserved',dict(method=method));self.consumed.add(method)
        self.sequence+=1;ident=self.sequence
        try:
            self.send(dict(id=ident,method=method,params=params),allow_cancel=allow_cancel)
            deadline=min(self.gate.deadline,time.monotonic()+seconds)
            while time.monotonic()<deadline:
                message=self.next(deadline,allow_cancel=allow_cancel)
                if 'method' not in message and type(message.get('id')) is int and message['id']==ident:
                    require(set(message)=={'id','result'} and type(message['result']) is dict,'protocol_response')
                    return message['result']
                if method=='turn/interrupt' or (method=='turn/start' and message.get('method')=='item/tool/call'):
                    require(len(self.held)<8,'protocol_held_limit');self.held.append(message)
                else:self.notification(message,preflight=True)
            raise TimeoutError('deadline')
        except BaseException:self.failed=True;raise
    def begin(self):
        self.request('initialize',dict(clientInfo=dict(name='colvia_documents',title='Colvia',version='1'),capabilities=dict(experimentalApi=True)))
        self.send({'method':'initialized'})
        config=self.request('config/read',dict(cwd=self.cwd,includeLayers=False))
        account=self.request('account/read',dict(refreshToken=False))
        models=self.request('model/list',dict(limit=100,includeHidden=True))
        admission=self.policy.admit(self.gate.grant.payload['contract'],config.get('config'),account,models)
        del account,config,models
        self.gate.append('admission',admission)
        response=self.request('thread/start',dict(model=self.policy.model,modelProvider='openai',cwd=self.cwd,
            approvalPolicy='never',permissions=PROFILE,ephemeral=True,environments=[],runtimeWorkspaceRoots=[],
            allowProviderModelFallback=False,
            baseInstructions='Use only the supplied document tools. The external Host owns every file effect.',
            developerInstructions='Read the declared IDs once, write the approved range once, then verify DOC-LINKS, DOC-GFM and DOC-CLAIMS. Await each response. No parallel calls or retries.',
            dynamicTools=self.policy.tools(self.gate.grant.payload['contract'])))
        require(response.get('model')==self.policy.model and type(response.get('thread')) is dict,'protocol_thread')
        self.thread=response['thread'].get('id');require(type(self.thread) is str and 0<len(self.thread.encode())<256,'protocol_identity')
        response=self.request('turn/start',dict(threadId=self.thread,
            input=[dict(type='text',text=self.gate.grant.payload['request']['prompt'])],model=self.policy.model,
            effort='low',environments=[],permissions=PROFILE))
        require(type(response.get('turn')) is dict,'protocol_turn')
        self.turn=response['turn'].get('id');self.gate.bind(self.thread,self.turn)
    def reply(self,message,result,*,success=True,allow_cancel=False):
        require(type(message.get('id')) in (int,str),'protocol_reply_identity')
        if not allow_cancel:result=self.gate.checked_reply(result)
        else:require(result==dict(ok=False,effect_status='not_started',reason='cancelled') and success is False,'protocol_cancel_reply')
        text=checked_payload(result,deadline=self.gate.deadline).decode()
        self.send(dict(id=message['id'],result=dict(contentItems=[dict(type='inputText',text=text)],success=success)),allow_cancel=allow_cancel)
    def event(self,*,allow_cancel=False):
        self.health(allow_cancel=allow_cancel)
        return self.held.pop(0) if self.held else self.next(self.gate.deadline,allow_cancel=allow_cancel)
    def run(self,controller):
        require(not self.stopped,'cancelled')
        try:return self._run(controller)
        except BaseException as exc:
            # A clean cancel is not corrupt transport. Preserve one metadata-only
            # interrupt within the original deadline; never extend the grant.
            if isinstance(exc,RecordError) and exc.code in ('cancelled','execution-cancel-requested','delivery-cancelled') and not self.failed and not self.sink.partial:
                self.stopped=True
            else:self.failed=True
            raise
    def _run(self,controller):
        self.begin()
        while True:
            message=self.event()
            if message.get('method')=='item/tool/call':
                require(set(message)=={'id','method','params'} and type(message['id']) in (int,str),'protocol_callback')
                reservation=self.gate.reserve(message['params'])
                result=controller.dispatch(reservation)
                self.reply(message,result)
                history=self.gate.journal.read(self.gate.run)[-1]
                if len(history.completed_refs)==5:
                    self.gate.authority()
                    writes=[w['result']['value'] for w in history.workers.values() if w['intent']['value']['role']=='write']
                    self.gate.append('seal',dict(completed_refs=history.completed_refs,result_identity=writes[0]['after']))
            else:
                completed=self.notification(message)
                if completed is not None:
                    history=self.gate.journal.read(self.gate.run)[-1]
                    require(completed.get('status')=='completed' and history.seal is not None,'protocol_premature_completion')
                    return 'completed'  # process closure and terminal publication remain Host-owned
    def interrupt(self):
        require(self.thread is not None and self.turn is not None,'protocol_interrupt_identity')
        self.request('turn/interrupt',dict(threadId=self.thread,turnId=self.turn),seconds=15)
        deadline=min(self.gate.deadline,time.monotonic()+15);calls=0
        while time.monotonic()<deadline:
            message=self.event(allow_cancel=True)
            if message.get('method')=='item/tool/call':
                calls+=1;require(calls<=8,'protocol_held_limit')
                self.gate.refuse('cancelled')
                self.reply(message,dict(ok=False,effect_status='not_started',reason='cancelled'),success=False,allow_cancel=True)
            else:
                completed=self.notification(message)
                if completed is not None:
                    require(completed.get('status')=='interrupted','protocol_interrupt_unconfirmed')
                    return 'interrupted'
        raise TimeoutError('deadline')
