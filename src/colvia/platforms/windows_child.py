"""Durable bounded child protocol using exact Windows Job handles.

Only callers with an approved executable/operation may invoke it. Filesystem and
network isolation are NOT supplied by this class. Timeout/termination does not
prove that a command made no external change; effect callers must reconcile.
"""
from pathlib import Path
from contextlib import ExitStack
import time,uuid,math
from ..codec import canonical_bytes,decode_canonical,require,RecordError
from ..storage.windows import WindowsFiles
from .windows_job import JobAPI
from .process import ProcessResult


class WindowsChild:
    def __init__(self,root,*,files=None,api=None,clock=time.monotonic,sleep=time.sleep):
        self.root=Path(root);self.api=api or JobAPI();self.files=files or WindowsFiles(api=self.api)
        self.clock,self.sleep=clock,sleep;self.files.private_directory(self.root)

    def run(self,args,*,cwd,env,input_bytes=b'',input_path=None,seconds=30,limit=16*1024*1024,event=lambda *_:None):
        require(type(seconds) in (int,float) and 0<seconds<=60 and type(limit) is int and 0<limit<=128*1024*1024,'windows-child-budget')
        require(type(input_bytes) is bytes and len(input_bytes)<=4*1024*1024,'process-input-limit')
        if input_path is not None:
            input_path=Path(input_path)
            require(not input_bytes and input_path.is_absolute() and '..' not in input_path.parts and
                    input_path.is_relative_to(self.root.parent),'windows-child-input-outside-staging')
        area=self.root/uuid.uuid4().hex;self.files.create_directory(area)
        def note(name,value):self.files.create(area/name,canonical_bytes(value))
        note('intent.json',dict(args=list(args),cwd=str(cwd),seconds_limit_ns=math.ceil(seconds*1000000000),limit=limit));event('spawn-intent',str(area))
        if input_path is None:self.files.create(area/'stdin',input_bytes);input_path=area/'stdin'
        for name in ('stdout','stderr'):self.files.create(area/name,b'')
        streams=(input_path,area/'stdout',area/'stderr')
        child=None;closed=False;code=None;identities=[];deadline=self.clock()+seconds
        try:
            with ExitStack() as stack:
                handles=[]
                for path,access in zip(streams,(0x80020000,0xc0020080,0xc0020080)):
                    stack.enter_context(self.api.ancestors(path))
                    h=stack.enter_context(self.api.opened(path,access=access,share=1));info=self.api.state(h,path);self.api.private(h)
                    require(not info['directory'] and info['links']==1 and info['size']<=2*1024**3,'windows-child-file-identity')
                    handles.append(h);identities.append(info['identity'])
                child=self.api.start(args,str(cwd),env,tuple(handles),created=lambda pid:note('created.json',dict(pid=pid,suspended=True)))
                note('started.json',dict(pid=child.pid));event('started',child.pid)
                while True:
                    sizes=[self.api.state(h,area/name)['size'] for h,name in zip(handles[1:],('stdout','stderr'))]
                    require(sum(sizes)<=limit,'process-output-limit')
                    if child.exited() and child.active()==0:
                        code=child.code();closed=True;break
                    require(self.clock()<deadline,'process-timeout');self.sleep(0.01)
                for h in handles[1:]:self.api.ok(self.api.FlushFileBuffers(h))
                note('closed.json',dict(pid=child.pid,exit_code=code,job_active=0));event('closed',code)
            for path,expected in zip(streams,identities):
                require(self.files.identity(path)==expected,'windows-child-file-changed')
            out=self.files.read(area/'stdout',limit);err=self.files.read(area/'stderr',limit)
            require(len(out)+len(err)<=limit,'process-output-limit')
            return ProcessResult(code,out,err)
        except BaseException as error:
            if child is not None and not closed:
                try:
                    child.stop();stop_limit=self.clock()+5
                    while not (child.exited() and child.active()==0):
                        require(self.clock()<stop_limit,'windows-child-closure-unknown');self.sleep(0.01)
                    closed=True;note('stopped.json',dict(pid=child.pid,job_active=0,external_effect='unknown'))
                except BaseException as closure:
                    note('unknown.json',dict(pid=child.pid,closure='unproven',external_effect='unknown'))
                    raise RecordError('windows-child-closure-unknown') from closure
            note('failure.json',dict(error=type(error).__name__,code=error.code if isinstance(error,RecordError) else 'native-call-failed',
                                     process_closed=closed,external_effect='unknown' if child else 'inspect-created-record'))
            raise
        finally:
            if child is not None:child.close()


class WindowsGitChild(WindowsChild):
    """Adapt durable Job observations to the shared Git child journal vocabulary."""
    def run(self,*args,event=lambda *_:None,**kwargs):
        area=None
        def journal(phase,value):
            nonlocal area
            if phase=='spawn-intent':area=value;event(phase,area)
            elif phase=='started':event('started',area)
            elif phase=='closed':event('exited',area)
        return super().run(*args,event=journal,**kwargs)
    def closed(self,area):
        area=Path(area);require(area.parent==self.root,'foreign-git-child')
        try:
            started=decode_canonical(self.files.read(area/'started.json'))
            if self.files.exists(area/'unknown.json'):return False
            name='closed.json' if self.files.exists(area/'closed.json') else 'stopped.json'
            final=decode_canonical(self.files.read(area/name))
        except FileNotFoundError:return False
        require(type(started) is dict and set(started)=={'pid'} and type(started['pid']) is int and started['pid']>1,'windows-child-identity-invalid')
        require(type(final) is dict and final.get('pid')==started['pid'] and type(final.get('job_active')) is int and
                final['job_active']==0,'windows-child-closure-invalid')
        # This is an observed zero-active *owned unnamed Job*, not a claim about
        # whichever process later reuses its PID. No PID is signalled/re-adopted.
        return True
