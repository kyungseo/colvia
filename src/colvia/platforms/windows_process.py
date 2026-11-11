"""Bounded in-memory read-command transport using owned Windows Job/pipes.

No temporary files or global permissions. This transport alone does not prove
that a caller's command is read-only and is not an official-execution sandbox.
"""
import threading,time
from ..codec import require,RecordError
from .process import ProcessResult
from .windows_job import JobAPI


def run(args,*,cwd,env,input_bytes=b'',seconds=10,output_limit=64*1024*1024,api=None):
    require(type(input_bytes) is bytes and len(input_bytes)<=4*1024*1024,'process-input-limit')
    require(type(seconds) in (int,float) and 0<seconds<=60 and type(output_limit) is int and 0<output_limit<=128*1024*1024,'invalid-process-budget')
    a=api or JobAPI();child=None;owned=set();threads=[];errors=[];lock=threading.Lock();failed=threading.Event()
    output=[bytearray(),bytearray()];count=[0];closed=False;deadline=time.monotonic()+seconds
    def report(error):
        with lock:errors.append(error)
        failed.set()
    def reader(handle,index):
        try:
            while raw:=a.read_pipe(handle,65536):
                with lock:
                    require(count[0]+len(raw)<=output_limit,'process-output-limit')
                    count[0]+=len(raw);output[index].extend(raw)
        except BaseException as error:report(error)
        finally:
            try:a.close(handle)
            except BaseException as error:report(error)
    def writer(handle):
        try:
            offset=0
            while offset<len(input_bytes):offset+=a.write_pipe(handle,input_bytes[offset:offset+65536])
        except BaseException as error:report(error)
        finally:
            try:a.close(handle)
            except BaseException as error:report(error)
    def worker(target,*args):
        thread=threading.Thread(target=target,args=args,daemon=True);thread.start();threads.append(thread);owned.remove(args[0])
    try:
        stdin=a.pipe();owned.update(stdin)
        stdout=a.pipe();owned.update(stdout)
        stderr=a.pipe();owned.update(stderr)
        child=a.start(args,str(cwd),env,(stdin[0],stdout[1],stderr[1]))
        for h in (stdin[0],stdout[1],stderr[1]):a.close(h);owned.remove(h)
        worker(reader,stdout[0],0);worker(reader,stderr[0],1);worker(writer,stdin[1])
        while True:
            if failed.is_set():raise errors[0]
            if child.exited() and child.active()==0 and all(not t.is_alive() for t in threads):
                with lock:
                    if errors:raise errors[0]
                closed=True;break
            require(time.monotonic()<deadline,'process-timeout');failed.wait(min(.01,max(0,deadline-time.monotonic())))
        return ProcessResult(child.code(),bytes(output[0]),bytes(output[1]))
    finally:
        closure_error=None
        if child is not None:
            try:
                if not closed:
                    child.stop();end=time.monotonic()+5
                    while not (child.exited() and child.active()==0):
                        require(time.monotonic()<end,'windows-child-closure-unknown');time.sleep(.01)
            except BaseException as error:closure_error=error
            finally:
                try:child.close()
                except BaseException as error:closure_error=error
        # Job closure releases child pipe ends. Worker threads own parent ends;
        # never close an in-flight synchronous IO handle from another thread.
        end=time.monotonic()+5
        for thread in threads:thread.join(max(0,end-time.monotonic()))
        for handle in owned:
            try:a.close(handle)
            except BaseException as error:closure_error=error
        if any(t.is_alive() for t in threads):raise RecordError('windows-pipe-closure-unknown')
        if closure_error is not None:raise RecordError('windows-child-closure-unknown') from closure_error
