"""Bounded POSIX pipe channel for an already admitted runtime process.

This adapter does not launch, terminate or qualify a runtime. The Host retains
process identity, cancellation, closure and the external-effect journal. No raw
stderr is retained or forwarded; protocol frames pass through bounded JsonLines.
"""
import os,selectors,time
from ..codec import RecordError,require
from ..adapters.bounded_rpc import JsonLines

class RuntimeChannel:
    def __init__(self,process,*,deadline,diagnostic_limit=1048576):
        require(os.name=='posix','runtime-channel-unavailable')
        require(type(deadline) in (int,float) and deadline>time.monotonic(),'deadline')
        require(type(diagnostic_limit) is int and 0<diagnostic_limit<=1048576,'protocol_limit')
        self.process=process;self.deadline=deadline;self.limit=diagnostic_limit
        self.lines=JsonLines();self.diagnostic_bytes=0;self.failed=False;self.closed=False
        self.output_eof=False;self.selector=selectors.DefaultSelector()
        try:
            for stream,label in ((process.stdout,'out'),(process.stderr,'err')):
                os.set_blocking(stream.fileno(),False);self.selector.register(stream,selectors.EVENT_READ,label)
            os.set_blocking(process.stdin.fileno(),False)
        except BaseException:self.selector.close();raise
    def _guard(self):
        require(not self.closed and not self.failed,'protocol_refused')
        require(time.monotonic()<self.deadline,'deadline')
    def _pump(self,timeout,*,writable=False):
        self._guard()
        if writable:self.selector.register(self.process.stdin,selectors.EVENT_WRITE,'in')
        ready=False
        try:
            for key,_ in self.selector.select(timeout):
                if key.data=='in':ready=True;continue
                try:raw=os.read(key.fd,65536)
                except BlockingIOError:continue
                if not raw:
                    self.selector.unregister(key.fileobj)
                    if key.data=='out':self.output_eof=True;self.lines.finish()
                elif key.data=='out':self.lines.feed(raw)
                else:
                    self.diagnostic_bytes+=len(raw)
                    require(self.diagnostic_bytes<=self.limit,'protocol_diagnostic_limit')
                    raise RecordError('protocol_diagnostic')
        except BaseException:self.failed=True;raise
        finally:
            if writable:self.selector.unregister(self.process.stdin)
        return ready
    def check(self):
        self._pump(0)
    def write(self,raw):
        self._guard();require(type(raw) is bytes and 0<len(raw)<=16384,'protocol_chunk_limit')
        try:
            while True:
                self.check()
                try:
                    count=os.write(self.process.stdin.fileno(),raw)
                    require(count>0,'protocol_write_incomplete');return count
                except BlockingIOError:
                    self._pump(min(.1,max(0,self.deadline-time.monotonic())),writable=True)
        except BaseException:self.failed=True;raise
    def read(self,deadline):
        require(type(deadline) in (int,float),'deadline')
        limit=min(deadline,self.deadline)
        try:
            while True:
                self.check()
                value=self.lines.pop()
                if value is not None:return value
                require(not self.output_eof,'protocol_eof')
                require(time.monotonic()<limit,'deadline')
                self._pump(min(.1,max(0,limit-time.monotonic())))
        except BaseException:self.failed=True;raise
    def close(self):
        if not self.closed:self.selector.close();self.closed=True
