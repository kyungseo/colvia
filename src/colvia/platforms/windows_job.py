"""Owned Windows child/job handles for bounded subprocess closure.

This is process containment, NOT a filesystem/network sandbox or permission grant.
A child starts suspended, joins its own non-breakaway job, then resumes. Only the
three explicit stream handles inherit. No PID lookup, shell or PATH resolution.
"""
import ctypes as C
import subprocess
from ..codec import RecordError,require
from ..storage.windows import API,local_path


def command_line(args):
    require(type(args) in (list,tuple) and args and all(type(a) is str and '\0' not in a for a in args),'windows-child-arguments')
    executable=local_path(args[0]);require(executable.lower().endswith('.exe'),'windows-native-executable-required')
    value=subprocess.list2cmdline(args)
    require(len(value.encode('utf-16-le'))//2<32767,'windows-child-command-limit')
    return executable,value


def environment_block(env):
    require(type(env) is dict and len(env)<=4096,'windows-child-environment')
    require(all(type(k) is str and type(v) is str for k,v in env.items()),'windows-child-environment')
    seen=set();entries=[]
    for key,value in sorted(env.items(),key=lambda kv:kv[0].casefold()):
        require(type(key) is str and key and '=' not in key and '\0' not in key and type(value) is str and '\0' not in value,'windows-child-environment')
        require(key.casefold() not in seen,'windows-child-environment-alias');seen.add(key.casefold());entries.append(key+'='+value)
    raw='\0'.join(entries)+'\0\0'
    require(len(raw.encode('utf-16-le'))<=2*1024*1024,'windows-child-environment-limit')
    return raw


class JobAPI(API):
    def __init__(self):
        super().__init__();W=self.W
        class Startup(C.Structure):
            _fields_=[('cb',W.DWORD),('reserved',W.LPWSTR),('desktop',W.LPWSTR),('title',W.LPWSTR),
                ('x',W.DWORD),('y',W.DWORD),('xsize',W.DWORD),('ysize',W.DWORD),('xchars',W.DWORD),('ychars',W.DWORD),
                ('fill',W.DWORD),('flags',W.DWORD),('show',W.WORD),('reserved2size',W.WORD),('reserved2',C.c_void_p),
                ('stdin',W.HANDLE),('stdout',W.HANDLE),('stderr',W.HANDLE)]
        class ExtendedStartup(C.Structure):_fields_=[('startup',Startup),('attributes',C.c_void_p)]
        class Process(C.Structure):_fields_=[('process',W.HANDLE),('thread',W.HANDLE),('pid',W.DWORD),('tid',W.DWORD)]
        class BasicLimit(C.Structure):
            _fields_=[('process_time',C.c_longlong),('job_time',C.c_longlong),('flags',W.DWORD),('minimum',C.c_size_t),
                ('maximum',C.c_size_t),('active',W.DWORD),('affinity',C.c_size_t),('priority',W.DWORD),('scheduling',W.DWORD)]
        class IO(C.Structure):_fields_=[(name,C.c_ulonglong) for name in ('read_ops','write_ops','other_ops','read_bytes','write_bytes','other_bytes')]
        class Limits(C.Structure):
            _fields_=[('basic',BasicLimit),('io',IO),('process_memory',C.c_size_t),('job_memory',C.c_size_t),('peak_process',C.c_size_t),('peak_job',C.c_size_t)]
        class Accounting(C.Structure):
            _fields_=[('user',C.c_longlong),('kernel',C.c_longlong),('period_user',C.c_longlong),('period_kernel',C.c_longlong),
                      ('page_faults',W.DWORD),('total',W.DWORD),('active',W.DWORD),('terminated',W.DWORD)]
        self.Startup,self.ExtendedStartup,self.Process,self.Limits,self.Accounting=Startup,ExtendedStartup,Process,Limits,Accounting
        for name,result,args in (
            ('CreatePipe',W.BOOL,(C.POINTER(W.HANDLE),C.POINTER(W.HANDLE),C.c_void_p,W.DWORD)),
            ('CreateJobObjectW',W.HANDLE,(C.c_void_p,W.LPCWSTR)),
            ('SetInformationJobObject',W.BOOL,(W.HANDLE,C.c_int,C.c_void_p,W.DWORD)),
            ('AssignProcessToJobObject',W.BOOL,(W.HANDLE,W.HANDLE)),
            ('QueryInformationJobObject',W.BOOL,(W.HANDLE,C.c_int,C.c_void_p,W.DWORD,C.c_void_p)),
            ('TerminateJobObject',W.BOOL,(W.HANDLE,W.UINT)),('TerminateProcess',W.BOOL,(W.HANDLE,W.UINT)),
            ('InitializeProcThreadAttributeList',W.BOOL,(C.c_void_p,W.DWORD,W.DWORD,C.POINTER(C.c_size_t))),
            ('UpdateProcThreadAttribute',W.BOOL,(C.c_void_p,W.DWORD,C.c_size_t,C.c_void_p,C.c_size_t,C.c_void_p,C.c_void_p)),
            ('DeleteProcThreadAttributeList',None,(C.c_void_p,)),
            ('SetHandleInformation',W.BOOL,(W.HANDLE,W.DWORD,W.DWORD)),
            ('CreateProcessW',W.BOOL,(W.LPCWSTR,W.LPWSTR,C.c_void_p,C.c_void_p,W.BOOL,W.DWORD,C.c_void_p,W.LPCWSTR,C.c_void_p,C.POINTER(Process))),
            ('ResumeThread',W.DWORD,(W.HANDLE,)),('WaitForSingleObject',W.DWORD,(W.HANDLE,W.DWORD)),
            ('GetExitCodeProcess',W.BOOL,(W.HANDLE,C.POINTER(W.DWORD)))):
            self.bind(self.kernel,name,result,args)

    def pipe(self):
        read=self.W.HANDLE();write=self.W.HANDLE();self.ok(self.CreatePipe(C.byref(read),C.byref(write),None,0))
        return read.value,write.value

    def read_pipe(self,handle,limit):
        require(type(limit) is int and 0<limit<=65536,'windows-pipe-read-limit')
        raw=C.create_string_buffer(limit);count=self.W.DWORD()
        if not self.ReadFile(handle,raw,limit,C.byref(count),None):
            error=C.get_last_error()
            if error==109:return b''
            raise C.WinError(error)
        require(count.value<=limit,'windows-pipe-read-limit');return raw.raw[:count.value]

    def write_pipe(self,handle,raw):
        require(type(raw) is bytes and 0<len(raw)<=65536,'windows-pipe-write-limit')
        value=C.create_string_buffer(raw);count=self.W.DWORD();self.ok(self.WriteFile(handle,value,len(raw),C.byref(count),None))
        require(0<count.value<=len(raw),'windows-pipe-write-limit');return count.value

    def start(self,args,cwd,env,streams,*,created=lambda *_:None):
        executable,line=command_line(args);cwd=local_path(cwd);environment=C.create_unicode_buffer(environment_block(env))
        require(len(streams)==3 and len(set(streams))==3,'windows-child-stream-handles')
        job=self.CreateJobObjectW(None,None);self.ok(job)
        info=self.Process();attributes=None;initialized=False;assigned=False;inherited=[];transferred=False
        try:
            limits=self.Limits();limits.basic.flags=0x2000 # KILL_ON_JOB_CLOSE; no breakaway.
            self.ok(self.SetInformationJobObject(job,9,C.byref(limits),C.sizeof(limits)))
            needed=C.c_size_t();self.InitializeProcThreadAttributeList(None,1,0,C.byref(needed))
            require(0<needed.value<=1024*1024,'windows-child-attribute-size')
            attributes=C.create_string_buffer(needed.value)
            self.ok(self.InitializeProcThreadAttributeList(attributes,1,0,C.byref(needed)));initialized=True
            handles=(self.W.HANDLE*3)(*streams)
            for h in streams:self.ok(self.SetHandleInformation(h,1,1));inherited.append(h)
            self.ok(self.UpdateProcThreadAttribute(attributes,0,0x20002,handles,C.sizeof(handles),None,None))
            startup=self.ExtendedStartup();startup.startup.cb=C.sizeof(startup);startup.startup.flags=0x100
            startup.startup.stdin,startup.startup.stdout,startup.startup.stderr=streams
            startup.attributes=C.cast(attributes,C.c_void_p)
            # CREATE_SUSPENDED | CREATE_UNICODE_ENVIRONMENT | EXTENDED_STARTUPINFO_PRESENT | CREATE_NO_WINDOW.
            self.ok(self.CreateProcessW(executable,C.create_unicode_buffer(line),None,None,True,0x08080404,
                                       environment,cwd,C.byref(startup),C.byref(info)))
            created(int(info.pid))
            # Remove temporary inheritable flags before any child instruction can
            # run; failure here is handled while the child remains suspended.
            for h in inherited:self.ok(self.SetHandleInformation(h,1,0))
            inherited=[]
            self.DeleteProcThreadAttributeList(attributes);initialized=False
            self.ok(self.AssignProcessToJobObject(job,info.process));assigned=True
            require(self.ResumeThread(info.thread)!=0xffffffff,'windows-child-resume-failed')
            self.close(info.thread);info.thread=None
            child=Child(self,job,info.process,int(info.pid));transferred=True
            return child
        except BaseException:
            if info.process:
                # This exact owned process may still be suspended if assignment
                # failed. Never leave a suspended orphan or guess another PID.
                result=self.TerminateJobObject(job,1) if assigned else self.TerminateProcess(info.process,1)
                if not result or self.WaitForSingleObject(info.process,5000)!=0:
                    raise RecordError('windows-child-spawn-closure-unknown') from None
            raise
        finally:
            cleanup=[]
            for h in inherited:cleanup.append(lambda h=h:self.ok(self.SetHandleInformation(h,1,0)))
            if initialized:cleanup.append(lambda:self.DeleteProcThreadAttributeList(attributes))
            if info.thread:cleanup.append(lambda:self.close(info.thread))
            if not transferred:
                if info.process:cleanup.append(lambda:self.close(info.process))
                cleanup.append(lambda:self.close(job))
            failure=None
            for action in cleanup:
                try:action()
                except BaseException as exc:failure=exc
            if failure is not None:raise RecordError('windows-child-cleanup-unknown') from failure



class Child:
    def __init__(self,api,job,process,pid):self.api,self.job,self.process,self.pid=api,job,process,pid
    def active(self):
        value=self.api.Accounting();self.api.ok(self.api.QueryInformationJobObject(self.job,1,C.byref(value),C.sizeof(value),None));return value.active
    def exited(self):
        result=self.api.WaitForSingleObject(self.process,0)
        require(result in (0,258),'windows-child-wait-failed');return result==0
    def code(self):
        require(self.exited() and self.active()==0,'windows-child-closure-unproven')
        code=self.api.W.DWORD();self.api.ok(self.api.GetExitCodeProcess(self.process,C.byref(code)));return int(code.value)
    def contains_process(self, pid, executable):
        """Verify the waiting process belongs to this exact job and image."""
        a = self.api
        require(type(pid) is int and 1 < pid <= 0xffffffff and pid != self.pid,
                'windows-child-identity-invalid')
        for name, result, args in (
            ('OpenProcess', a.W.HANDLE, (a.W.DWORD, a.W.BOOL, a.W.DWORD)),
            ('IsProcessInJob', a.W.BOOL, (a.W.HANDLE, a.W.HANDLE, C.POINTER(a.W.BOOL))),
            ('QueryFullProcessImageNameW', a.W.BOOL,
             (a.W.HANDLE, a.W.DWORD, a.W.LPWSTR, C.POINTER(a.W.DWORD))),
        ):
            a.bind(a.kernel, name, result, args)
        process = a.OpenProcess(0x101000, False, pid)
        a.ok(process)
        try:
            member = a.W.BOOL()
            a.ok(a.IsProcessInJob(process, self.job, C.byref(member)))
            if not member.value or a.WaitForSingleObject(process, 0) != 258:
                return False
            path = C.create_unicode_buffer(32768)
            length = a.W.DWORD(len(path))
            a.ok(a.QueryFullProcessImageNameW(process, 0, path, C.byref(length)))
            image = path.value
            if image.startswith('\\\\?\\'):
                image = image[4:]
            with a.ancestors(image), a.ancestors(executable), a.opened(image, share=1) as live, a.opened(executable, share=1) as known:
                return a.state(live, image)['identity'] == a.state(known, executable)['identity']
        finally:
            a.close(process)

    def stop(self):self.api.ok(self.api.TerminateJobObject(self.job,1))
    def close(self):
        try:self.api.close(self.process)
        finally:self.api.close(self.job)
