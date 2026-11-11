"""Bounded observed-process control for the qualified Darwin execution port.

The Host journals admission before launch and stores identities immediately after.
This port does not journal, authorize commands, or prove hostile daemon containment.
Birth observations have the operating system's one-second precision.
"""
import io,os,signal,subprocess,sys,time
from ..codec import RecordError,require
from ..execution import schema
from .process import run
from .darwin_execution import process_birth,group_absent

# A scan must get a useful complete window, never a tail of the TERM slice.
SCAN_SECONDS=.25

class DarwinProcesses:
    def __init__(self):
        require(sys.platform=='darwin','execution-process-port-unavailable');self._pipes={}
    def scan(self,*,seconds=5):
        result=run(['/bin/ps','-axo','pid=,ppid=,pgid=,lstart='],cwd='/',
            env={'LC_ALL':'C','TZ':'UTC0'},seconds=seconds,output_limit=8*1024*1024)
        require(result.code==0 and not result.stderr,'execution-process-scan-unavailable')
        try:lines=result.stdout.decode('ascii').splitlines()
        except UnicodeError:raise RecordError('execution-process-scan-unavailable') from None
        require(len(lines)<=100000,'execution-process-scan-limit');rows={}
        for line in lines:
            fields=line.split(None,3)
            require(len(fields)==4 and all(v.isdecimal() for v in fields[:3]),'execution-process-scan-shape')
            pid,ppid,pgid=map(int,fields[:3]);schema.integer(pid,1,(1<<31)-1)
            schema.integer(ppid,0,(1<<31)-1);schema.integer(pgid,0,(1<<31)-1)
            fields[3]=fields[3].strip();schema.birth(fields[3])
            require(pid not in rows,'execution-process-scan-duplicate')
            rows[pid]=dict(ppid=ppid,pgid=pgid,birth=fields[3])
        return rows
    def observe(self,process,known,*,seconds=5):
        rows=self.scan(seconds=seconds);group={pid for pid,row in rows.items() if row['pgid']==process.pid}
        for pid in known:
            if pid in rows:require(known[pid]['birth']==rows[pid]['birth'],'execution-pid-reuse')
        require(not group or any(pid in known and rows[pid]['birth']==known[pid]['birth'] for pid in group),'execution-group-identity-unavailable')
        owned={process.pid}|group
        # Bound the ancestry closure by the already bounded snapshot size.
        while True:
            require(len(owned)<=257,'execution-observed-process-limit')
            newer={pid for pid,row in rows.items() if row['ppid'] in owned}
            if newer<=owned:break
            owned|=newer
        for pid in owned:
            if pid in rows:
                if pid in known:require(known[pid]['birth']==rows[pid]['birth'],'execution-pid-reuse')
                known[pid]=rows[pid]
        return rows
    def launch(self,argv,*,cwd,env):
        # argv/environment/resource identity must already be qualified by Host.
        if not (type(argv) in (list,tuple) and bool(argv) and all(type(v) is str and '\x00' not in v for v in argv)):
            raise OSError('execution-launch-argv')
        process=subprocess.Popen(argv,cwd=cwd,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,start_new_session=True,close_fds=True,bufsize=0)
        self._pipes[id(process)]=(process,(process.stdin,process.stdout,process.stderr))
        return process
    def admit_io(self,process):
        owned=self._pipes.get(id(process))
        require(owned is not None and owned[0] is process and all(type(s) is io.FileIO for s in owned[1]) and
            all(a is b for a,b in zip(owned[1],(process.stdin,process.stdout,process.stderr))),'execution-owned-pipes-required')
    def close_io(self,process):
        owned=self._pipes.get(id(process))
        require(owned is not None and owned[0] is process and all(type(s) is io.FileIO for s in owned[1]),'execution-owned-pipes-required')
        _,streams=self._pipes.pop(id(process));error=None
        for stream in streams:
            try:
                if not stream.closed:stream.close()
            except BaseException as exc:
                if error is None:error=exc
        if error is not None:raise error
    def identity(self,process):
        return dict(pid=process.pid,birth=process_birth(process.pid) or None)
    def abort_owned(self,process,*,seconds=2):
        # Popen checks its unreaped child under its own waitpid lock. Never
        # signal a PID/group reconstructed from history on this fallback path.
        process.kill();process.wait(timeout=seconds)
    def stop(self,process,known,*,seconds=10):
        require(type(seconds) in (int,float) and 4*SCAN_SECONDS<=seconds<=20,'execution-stop-budget')
        require(process.pid in known and bool(known[process.pid]['birth']),'execution-runtime-identity-unavailable')
        started=time.monotonic();deadline=started+seconds;term_end=started+seconds/2
        rows=self.observe(process,known,seconds=min(5,seconds/4))
        def survivors():return [pid for pid in known if pid in rows]
        for sig in (signal.SIGTERM,signal.SIGKILL):
            require(time.monotonic()<deadline,'execution-stop-deadline')
            group=[pid for pid,row in rows.items() if row['pgid']==process.pid]
            # Refuse signaling a group with no matching admitted/observed member.
            require(not group or any(pid in known and rows[pid]['birth']==known[pid]['birth'] for pid in group),'execution-group-identity-unavailable')
            if group:
                try:os.killpg(process.pid,sig)
                except ProcessLookupError:pass
            for pid,old in known.items():
                row=rows.get(pid)
                if row and row['birth']==old['birth'] and row['pgid']!=process.pid:
                    try:os.kill(pid,sig)
                    except ProcessLookupError:pass
            slice_end=term_end if sig==signal.SIGTERM else deadline
            while True:
                remaining=slice_end-time.monotonic()
                if remaining<SCAN_SECONDS:break
                process.poll();rows=self.observe(process,known,seconds=SCAN_SECONDS)
                if not survivors() and group_absent(process.pid):
                    require(process.poll() is not None,'execution-parent-not-reaped')
                    return dict(returncode=process.returncode,group_absent=True,final_scan_confirmed=True,
                        children=[dict(pid=pid,birth=old['birth'],absent=True) for pid,old in sorted(known.items()) if pid!=process.pid])
                if time.monotonic()>=slice_end:break
                time.sleep(min(.02,max(0,slice_end-time.monotonic())))
        raise RecordError('execution-process-closure-unconfirmed')
