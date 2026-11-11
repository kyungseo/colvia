"""Bounded POSIX subprocess adapter, without shell or unbounded capture buffers."""
from dataclasses import dataclass
import os,selectors,signal,subprocess,time,sys
from ..codec import RecordError,require


@dataclass(frozen=True)
class ProcessResult:
    code:int
    stdout:bytes
    stderr:bytes


def run(argv,*,cwd,env,input_bytes=b'',seconds=10,output_limit=64*1024*1024):
    if sys.platform=='win32':
        from .windows_process import run as native
        return native(argv,cwd=cwd,env=env,input_bytes=input_bytes,seconds=seconds,output_limit=output_limit)
    require(os.name=='posix','process-adapter-unavailable')
    require(type(input_bytes) is bytes and len(input_bytes)<=4*1024*1024,'process-input-limit')
    require(0<seconds<=60 and 0<output_limit<=128*1024*1024,'invalid-process-budget')
    deadline=time.monotonic()+seconds
    child=subprocess.Popen(argv,cwd=cwd,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,start_new_session=True)
    selector=selectors.DefaultSelector();out=bytearray();err=bytearray();offset=0
    try:
        for stream,label in ((child.stdout,'stdout'),(child.stderr,'stderr')):
            os.set_blocking(stream.fileno(),False);selector.register(stream,selectors.EVENT_READ,label)
        if input_bytes:
            os.set_blocking(child.stdin.fileno(),False);selector.register(child.stdin,selectors.EVENT_WRITE,'stdin')
        else:child.stdin.close()
        while selector.get_map():
            remaining=deadline-time.monotonic()
            require(remaining>0,'process-timeout')
            for key,mask in selector.select(remaining):
                if key.data=='stdin':
                    try:offset+=os.write(key.fd,input_bytes[offset:offset+65536])
                    except BrokenPipeError:offset=len(input_bytes)
                    if offset==len(input_bytes):selector.unregister(key.fileobj);key.fileobj.close()
                else:
                    raw=os.read(key.fd,65536)
                    if not raw:selector.unregister(key.fileobj);key.fileobj.close()
                    else:
                        require(len(out)+len(err)+len(raw)<=output_limit,'process-output-limit')
                        (out if key.data=='stdout' else err).extend(raw)
        try:code=child.wait(timeout=max(0,deadline-time.monotonic()))
        except subprocess.TimeoutExpired:raise RecordError('process-timeout') from None
        return ProcessResult(code,bytes(out),bytes(err))
    finally:
        selector.close()
        if child.poll() is None:
            os.killpg(child.pid,signal.SIGKILL);child.wait(timeout=5)
        for stream in (child.stdin,child.stdout,child.stderr):
            if not stream.closed:stream.close()
