"""Check the native host as well as the executing Windows process architecture."""
import ctypes as C
import sys


def native_x64():
    if sys.platform != 'win32':
        return False
    api = C.WinDLL('kernel32', use_last_error=True)
    api.GetCurrentProcess.argtypes = []
    api.GetCurrentProcess.restype = C.c_void_p
    api.IsWow64Process2.argtypes = [C.c_void_p, C.POINTER(C.c_ushort), C.POINTER(C.c_ushort)]
    api.IsWow64Process2.restype = C.c_int
    process, machine = C.c_ushort(), C.c_ushort()
    return bool(api.IsWow64Process2(api.GetCurrentProcess(), C.byref(process), C.byref(machine))
                and process.value == 0 and machine.value == 0x8664)
