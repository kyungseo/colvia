"""Read the Windows user data location without changing settings or permissions."""
import ctypes as C
import sys
from ..codec import require
from ..storage.windows import local_path


class GUID(C.Structure):
    _fields_=[('a',C.c_uint32),('b',C.c_uint16),('c',C.c_uint16),('d',C.c_ubyte*8)]


def local_appdata():
    require(sys.platform=='win32','windows-native-unavailable')
    shell=C.WinDLL('shell32');ole=C.WinDLL('ole32')
    get=shell.SHGetKnownFolderPath
    get.argtypes=[C.POINTER(GUID),C.c_uint32,C.c_void_p,C.POINTER(C.c_void_p)]
    get.restype=C.c_int32
    free=ole.CoTaskMemFree;free.argtypes=[C.c_void_p];free.restype=None
    key=GUID(0xf1b32785,0x6fba,0x4fcf,(C.c_ubyte*8)(0x9d,0x55,0x7b,0x8e,0x7f,0x15,0x70,0x91))
    output=C.c_void_p()
    result=get(C.byref(key),0,None,C.byref(output))
    try:
        require(result==0 and output.value,'windows-local-user-data-unavailable')
        return local_path(C.wstring_at(output))
    finally:
        if output.value:free(output)
