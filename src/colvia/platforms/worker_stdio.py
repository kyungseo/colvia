"""Bounded duplex exchange with an already admitted document worker.

This helper does not spawn, kill or certify closure. Its owner must do that even
when exchange raises. Stderr is counted, never retained in a durable record.
"""
import os,selectors,time
from ..codec import require,RecordError

def exchange(process,request,*,deadline,cancelled=lambda:False):
    require(type(request) is bytes and 0<len(request)<=131072,'worker_request_size')
    require(type(deadline) in (int,float),'worker_deadline')
    out=bytearray();err_bytes=0;offset=0
    with selectors.DefaultSelector() as selector:
        for stream,label,event in ((process.stdin,'in',selectors.EVENT_WRITE),
                (process.stdout,'out',selectors.EVENT_READ),(process.stderr,'err',selectors.EVENT_READ)):
            os.set_blocking(stream.fileno(),False);selector.register(stream,event,label)
        while selector.get_map():
            if time.monotonic()>=deadline:raise TimeoutError('deadline')
            require(not cancelled(),'cancelled')
            for key,_ in selector.select(min(.1,max(0,deadline-time.monotonic()))):
                if key.data=='in':
                    try:count=os.write(key.fileobj.fileno(),request[offset:offset+16384])
                    except BlockingIOError:continue
                    except BrokenPipeError:raise RecordError('worker_input_incomplete') from None
                    require(count>0,'worker_input_incomplete');offset+=count
                    if offset==len(request):selector.unregister(key.fileobj);key.fileobj.close()
                else:
                    try:raw=os.read(key.fileobj.fileno(),65536)
                    except BlockingIOError:continue
                    if not raw:selector.unregister(key.fileobj);continue
                    if key.data=='out':
                        require(len(out)+len(raw)<=131072,'worker_output_limit');out.extend(raw)
                    else:
                        err_bytes+=len(raw);require(err_bytes<=1048576,'worker_stderr_limit')
        require(offset==len(request),'worker_input_incomplete')
        process.wait(timeout=max(.001,deadline-time.monotonic()))
    return bytes(out),err_bytes
