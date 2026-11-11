"""Exact encoded-frame gate for the bounded document RPC capability.

Method vocabulary belongs to this protocol adapter, not Work acceptance.
Caller supplies a bounded transport; no process or network is created here.
"""
import json,time
from ..codec import RecordError,require
from ..execution.guards import checked_payload,reject_duplicate_keys

METHODS=frozenset(('initialize','config/read','account/read','model/list','thread/start','turn/start','turn/interrupt'))

def checked_frame(value,*,deadline):
    raw=checked_payload(value,limit=1048575,deadline=deadline,protocol=True)+b'\n'
    try:
        frame=json.loads(raw,object_pairs_hook=reject_duplicate_keys)
        require(type(frame) is dict,'content_rejected')
        if 'method' in frame:
            method=frame['method'];require(type(method) is str,'content_rejected')
            if method=='initialized':require(set(frame)=={'method'},'content_rejected')
            else:
                require(set(frame)=={'id','method','params'} and type(frame['id']) is int and
                        type(frame['params']) is dict and method in METHODS,'content_rejected')
                if method=='turn/start':checked_payload(frame['params']['input'],deadline=deadline)
        else:
            require(set(frame)=={'id','result'} and type(frame['id']) in (int,str),'content_rejected')
            checked_payload(frame['id'],deadline=deadline)
            result=frame['result']
            require(type(result) is dict and set(result)=={'contentItems','success'} and type(result['success']) is bool,'content_rejected')
            items=result['contentItems']
            require(type(items) is list and len(items)==1 and type(items[0]) is dict and
                    set(items[0])=={'type','text'} and items[0]['type']=='inputText' and type(items[0]['text']) is str,'content_rejected')
            checked_payload(json.loads(items[0]['text'],object_pairs_hook=reject_duplicate_keys),deadline=deadline)
    except (ValueError,TypeError,KeyError,UnicodeError,RecursionError):raise RecordError('content_rejected') from None
    if time.monotonic()>=deadline:raise TimeoutError('deadline')
    return raw

class FrameSink:
    def __init__(self,write,*,deadline):
        self.write=write;self.deadline=deadline;self.partial=False;self.bytes_sent=0;self.frames_sent=0
    def send(self,value):
        require(not self.partial,'protocol_refused')
        raw=checked_frame(value,deadline=self.deadline);offset=0
        # Any failed sink call may have written bytes before raising. Keep the
        # latch until closure; never finish a failed frame with a later reply.
        while offset<len(raw):
            if time.monotonic()>=self.deadline:raise TimeoutError('deadline')
            self.partial=True
            count=self.write(raw[offset:offset+16384])
            require(type(count) is int and 0<count<=min(16384,len(raw)-offset),'protocol_refused')
            offset+=count;self.bytes_sent+=count
        self.frames_sent+=1;self.partial=False


class JsonLines:
    """Bounded inbound transport only; decoded data never grants capabilities.

    Error text and bytes stay out of persistent diagnostics. The concrete
    adapter still validates each response, unsolicited request and notification.
    """
    def __init__(self,*,limit=1048576,queue_limit=1024):
        require(type(limit) is int and 0<limit<=1048576 and type(queue_limit) is int and 0<queue_limit<=1024,'protocol_limit')
        self.limit=limit;self.queue_limit=queue_limit;self.buffer=b'';self.queue=[]
        self.queued_bytes=0;self.failed=False;self.eof=False
    def feed(self,raw):
        require(not self.failed and not self.eof,'protocol_refused')
        try:
            require(type(raw) is bytes and len(raw)<=65536,'protocol_chunk_limit')
            self.buffer+=raw
            while b'\n' in self.buffer:
                line,self.buffer=self.buffer.split(b'\n',1)
                require(len(line)<self.limit,'protocol_frame_limit')
                if not line:continue
                value=json.loads(line,object_pairs_hook=reject_duplicate_keys,
                    parse_constant=lambda value:(_ for _ in ()).throw(ValueError('nonfinite')))
                require(type(value) is dict,'protocol_shape')
                todo=[(value,0)];nodes=0
                while todo:
                    item,depth=todo.pop();nodes+=1
                    require(depth<=16 and nodes<=4096,'protocol_shape_limit')
                    if type(item) is dict:
                        require(all(type(k) is str for k in item),'protocol_shape')
                        todo.extend((v,depth+1) for pair in item.items() for v in pair)
                    elif type(item) is list:todo.extend((v,depth+1) for v in item)
                    elif type(item) is str:item.encode('utf-8')
                    else:require(item is None or type(item) is bool or (type(item) is int and abs(item)<2**64),'protocol_shape')
                require(len(self.queue)<self.queue_limit and self.queued_bytes+len(line)<self.limit,'protocol_queue_limit')
                self.queue.append((value,len(line)));self.queued_bytes+=len(line)
            require(len(self.buffer)<self.limit,'protocol_frame_limit')
        except (ValueError,TypeError,UnicodeError,RecursionError):
            self.failed=True
            raise RecordError('protocol_refused') from None
    def pop(self):
        require(not self.failed,'protocol_refused')
        if not self.queue:return None
        value,size=self.queue.pop(0);self.queued_bytes-=size;return value
    def finish(self):
        require(not self.failed and not self.eof,'protocol_refused')
        self.eof=True
        if self.buffer:
            self.failed=True
            raise RecordError('protocol_truncated_frame')
