"""Bounded Git child observation. Timeout never means not-applied.

All stdin/stdout/stderr and start/exit observations live in caller-owned durable
scratch. No signal, retry, authentication, network or shell is used. A missing
spawn result or unclosed process group leaves the caller's effect pending.
"""
from pathlib import Path
from dataclasses import dataclass
import os,stat,subprocess,time,uuid,math
from contextlib import contextmanager
from ..codec import canonical_bytes,require
from ..storage.files import PosixFiles
from .darwin_execution import process_birth,group_absent

@dataclass(frozen=True)
class Result:
    code:int
    stdout:bytes
    stderr:bytes

@contextmanager
def opened(path,write=False):
    fd=os.open(path,(os.O_WRONLY if write else os.O_RDONLY)|os.O_NOFOLLOW)
    try:
        info=os.fstat(fd);current=Path(path).lstat()
        require(stat.S_ISREG(info.st_mode) and info.st_nlink==1 and
                (info.st_dev,info.st_ino)==(current.st_dev,current.st_ino),'git-child-file-changed')
        if write:require(info.st_size==0,'git-child-output-not-empty')
        with os.fdopen(fd,'wb' if write else 'rb',closefd=False) as stream:yield stream
    finally:os.close(fd)

class GitChild:
    def __init__(self,root):
        self.root=Path(root);self.files=PosixFiles();self.files.private_directory(self.root)
    def run(self,args,*,cwd,env,input_bytes=b'',input_path=None,seconds=30,limit=16*1024*1024,event=lambda *_:None):
        require(type(seconds) in (int,float) and 0<seconds<=30 and 0<limit<=128*1024*1024,'git-child-budget')
        area=self.root/uuid.uuid4().hex;self.files.create_directory(area)
        def note(name,value):self.files.create(area/name,canonical_bytes(value))
        note('intent.json',dict(args=args,cwd=str(cwd),seconds_limit_ns=math.ceil(seconds*1000000000),limit=limit));event('spawn-intent',str(area))
        if input_path is None:
            self.files.create(area/'stdin',input_bytes);input_path=area/'stdin'
        require(Path(input_path).is_absolute() and '..' not in Path(input_path).parts and
                (Path(input_path).parent==area or Path(input_path).is_relative_to(self.root.parent)),'git-child-input-outside-staging')
        for name in ('stdout','stderr'):self.files.create(area/name,b'')
        process=None
        with opened(input_path) as stdin,opened(area/'stdout',True) as stdout,opened(area/'stderr',True) as stderr:
            process=subprocess.Popen(args,cwd=cwd,env=env,stdin=stdin,stdout=stdout,stderr=stderr,start_new_session=True,close_fds=True)
            # Popen owns the direct PID even if a short-lived child exits before
            # ps observes its birth. A final wait plus absent group is required.
            birth=process_birth(process.pid)
            note('started.json',dict(pid=process.pid,birth=birth));event('started',str(area))
            deadline=time.monotonic()+seconds
            while process.poll() is None:
                if time.monotonic()>=deadline or any((area/n).stat().st_size>limit for n in ('stdout','stderr')):
                    note('pending.json',dict(pid=process.pid,birth=birth,reason='deadline-or-output-limit'))
                    require(False,'git-child-outcome-unknown')
                time.sleep(min(.02,max(0,deadline-time.monotonic())))
            code=process.wait();self.files.flush_file(stdout.fileno());self.files.flush_file(stderr.fileno())
        closed=group_absent(process.pid)
        note('exited.json',dict(pid=process.pid,birth=birth,code=code,group_absent=closed));event('exited',str(area))
        require(closed,'git-child-closure-unavailable')
        return Result(code,self.files.read(area/'stdout',limit),self.files.read(area/'stderr',limit))
    def closed(self,area):
        from ..codec import decode_canonical
        area=Path(area);require(area.parent==self.root,'foreign-git-child')
        try:started=decode_canonical(self.files.read(area/'started.json'))
        except FileNotFoundError:return False
        # Exit files are historical observations, not permanent closure verdicts.
        # A timed-out child can exit later. No PID or PGID is signalled here.
        require(type(started) is dict and set(started)=={'pid','birth'} and
                type(started['pid']) is int and started['pid']>1,'git-child-identity-invalid')
        return group_absent(started['pid'])
