"""Windows job ordering with an explicit native-API double; no child is launched."""
import ctypes as C
from types import SimpleNamespace
import unittest
from colvia.codec import RecordError
from colvia.platforms.windows_job import JobAPI,command_line,environment_block


class APIStub(JobAPI):
    def __init__(self,fail=None):
        self.calls=[];self.fail=fail;self.W=SimpleNamespace(HANDLE=C.c_void_p,DWORD=C.c_uint32)
        class Startup(C.Structure):_fields_=[('cb',C.c_uint32),('flags',C.c_uint32),('stdin',C.c_void_p),('stdout',C.c_void_p),('stderr',C.c_void_p)]
        class Extended(C.Structure):_fields_=[('startup',Startup),('attributes',C.c_void_p)]
        class Process(C.Structure):_fields_=[('process',C.c_void_p),('thread',C.c_void_p),('pid',C.c_uint32)]
        class Basic(C.Structure):_fields_=[('flags',C.c_uint32)]
        class Limits(C.Structure):_fields_=[('basic',Basic)]
        class Accounting(C.Structure):_fields_=[('active',C.c_uint32)]
        self.ExtendedStartup,self.Process,self.Limits,self.Accounting=Extended,Process,Limits,Accounting
    def ok(self,result):
        if not result:raise OSError('synthetic API refusal')
        return result
    def CreateJobObjectW(self,*_):self.calls.append('job');return 1000
    def SetInformationJobObject(self,job,kind,limits,size):
        assert limits._obj.basic.flags==0x2000;self.calls.append('kill-on-close');return 1
    def InitializeProcThreadAttributeList(self,attrs,count,flags,size):size._obj.value=64;return 1 if attrs else 0
    def UpdateProcThreadAttribute(self,attrs,flags,key,handles,size,*_):
        assert key==0x20002 and tuple(handles)==(10,11,12);self.calls.append('only-stream-handles');return 1
    def DeleteProcThreadAttributeList(self,*_):self.calls.append('delete-attributes')
    def SetHandleInformation(self,h,mask,flags):self.calls.append(('inherit',h,flags));return 0 if self.fail=='clear' and flags==0 else 1
    def CreateProcessW(self,exe,cmd,pa,ta,inherit,flags,env,cwd,startup,info):
        assert flags==0x08080404 and inherit and exe==r'C:\tools\git.exe'
        info._obj.process=2000;info._obj.thread=3000;info._obj.pid=4000
        self.calls.append('created-suspended');return 1
    def AssignProcessToJobObject(self,*_):self.calls.append('assign');return 0 if self.fail=='assign' else 1
    def ResumeThread(self,*_):self.calls.append('resume');return 0xffffffff if self.fail=='resume' else 1
    def TerminateProcess(self,*_):self.calls.append('terminate-process');return 0 if self.fail=='stop' else 1
    def TerminateJobObject(self,*_):self.calls.append('terminate-job');return 1
    def WaitForSingleObject(self,*_):return 0
    def QueryInformationJobObject(self,job,kind,info,*_):info._obj.active=0;return 1
    def GetExitCodeProcess(self,h,code):code._obj.value=0;return 1
    def close(self,h):self.calls.append(('close',h))


class WindowsJobTests(unittest.TestCase):
    def start(self,api,**kwargs):return api.start([r'C:\tools\git.exe','status'],r'C:\project',{'SYSTEMROOT':r'C:\Windows'},(10,11,12),**kwargs)
    def test_exact_application_no_shell_and_environment_alias_refusal(self):
        exe,line=command_line([r'C:\Program Files\Git\git.exe','a&b','a b','quote"here'])
        self.assertEqual(r'C:\Program Files\Git\git.exe',exe);self.assertIn('"a b"',line)
        for args in (['git'],[r'C:\x.cmd'],[r'C:\x.exe','bad\0arg']):
            with self.assertRaises(RecordError):command_line(args)
        for env in ({'PATH':'one','Path':'two'},{'x':'bad\0'},{1:'wrong'}):
            with self.assertRaises(RecordError):environment_block(env)
        self.assertEqual('A=one\0B=two\0\0',environment_block({'B':'two','A':'one'}))
    def test_resume_only_after_job_assignment_and_inheritance_reset(self):
        api=APIStub();child=self.start(api,created=lambda pid:api.calls.append(('pid',pid)))
        self.assertLess(api.calls.index('assign'),api.calls.index('resume'))
        self.assertLess(api.calls.index(('inherit',12,0)),api.calls.index('resume'))
        self.assertLess(api.calls.index(('pid',4000)),api.calls.index('assign'))
        self.assertNotIn(('close',1000),api.calls);self.assertEqual(0,child.code());child.close()
        self.assertIn(('close',1000),api.calls);self.assertIn(('close',2000),api.calls)
    def test_assignment_failure_never_resumes_suspended_child(self):
        api=APIStub('assign')
        with self.assertRaises(OSError):self.start(api)
        self.assertNotIn('resume',api.calls);self.assertIn('terminate-process',api.calls)
        for h in (1000,2000,3000):self.assertIn(('close',h),api.calls)
    def test_resume_failure_terminates_owned_job_and_closes_handles(self):
        api=APIStub('resume')
        with self.assertRaisesRegex(RecordError,'resume-failed'):self.start(api)
        self.assertIn('terminate-job',api.calls)
        for h in (1000,2000,3000):self.assertIn(('close',h),api.calls)
    def test_inheritance_reset_failure_closes_owned_resources_and_never_resumes(self):
        api=APIStub('clear')
        with self.assertRaisesRegex(RecordError,'cleanup-unknown'):self.start(api)
        self.assertNotIn('resume',api.calls);self.assertIn('terminate-process',api.calls)
        for h in (1000,2000,3000):self.assertIn(('close',h),api.calls)
    def test_failed_created_journal_stops_exact_suspended_process(self):
        api=APIStub()
        def fail(_):raise OSError('synthetic journal full')
        with self.assertRaises(OSError):self.start(api,created=fail)
        self.assertNotIn('resume',api.calls);self.assertIn('terminate-process',api.calls)


if __name__=='__main__':unittest.main()
