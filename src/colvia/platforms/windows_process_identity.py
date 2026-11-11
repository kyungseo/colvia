"""Read process creation identity; never signal, privilege-escalate or adopt a PID."""
import ctypes as C
import sys
from ..codec import require


def process_birth(pid):
    require(sys.platform=='win32' and type(pid) is int and pid>1,'windows-process-identity-unavailable')
    k=C.WinDLL('kernel32',use_last_error=True)
    k.OpenProcess.argtypes=[C.c_uint32,C.c_int,C.c_uint32];k.OpenProcess.restype=C.c_void_p
    k.CloseHandle.argtypes=[C.c_void_p];k.CloseHandle.restype=C.c_int
    k.WaitForSingleObject.argtypes=[C.c_void_p,C.c_uint32];k.WaitForSingleObject.restype=C.c_uint32
    k.GetProcessTimes.argtypes=[C.c_void_p,*([C.POINTER(C.c_uint64)]*4)];k.GetProcessTimes.restype=C.c_int
    handle=k.OpenProcess(0x101000,False,pid) # QUERY_LIMITED_INFORMATION | SYNCHRONIZE
    if not handle:
        error=C.get_last_error()
        if error==87:return None # No such PID, not access denial.
        raise C.WinError(error)
    try:
        status=k.WaitForSingleObject(handle,0);require(status in (0,258),'windows-process-wait-unavailable')
        if status==0:return None
        creation,exit,kernel,user=(C.c_uint64() for _ in range(4))
        if not k.GetProcessTimes(handle,C.byref(creation),C.byref(exit),C.byref(kernel),C.byref(user)):
            raise C.WinError(C.get_last_error())
        return str(creation.value)
    finally:
        if not k.CloseHandle(handle):raise C.WinError(C.get_last_error())
