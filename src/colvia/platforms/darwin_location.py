"""Persistent Darwin directory identity from the same no-follow descriptor."""
import ctypes
import struct
import uuid

from ..codec import require

# <sys/attr.h>: ATTR_BIT_MAP_COUNT, ATTR_CMN_RETURNED_ATTRS,
# ATTR_VOL_INFO | ATTR_VOL_UUID, ATTR_CMN_CRTIME.
_RETURNED = 0x80000000
_UUID = 0x00040000
_CRTIME = 0x00000200
_HEADER = struct.Struct('=6I')


class _Statfs(ctypes.Structure):
    # Darwin SDK sys/mount.h, __DARWIN_STRUCT_STATFS64.
    _fields_=[('bsize',ctypes.c_uint32),('iosize',ctypes.c_int32),
        *[(name,ctypes.c_uint64) for name in ('blocks','bfree','bavail','files','ffree')],
        ('fsid',ctypes.c_int32*2),('owner',ctypes.c_uint32),('type',ctypes.c_uint32),
        ('flags',ctypes.c_uint32),('subtype',ctypes.c_uint32),('fstype',ctypes.c_char*16),
        ('mount',ctypes.c_char*1024),('source',ctypes.c_char*1024),
        ('flags_ext',ctypes.c_uint32),('reserved',ctypes.c_uint32*7)]


def filesystem(fd):
    info=_Statfs()
    fn=ctypes.CDLL(None,use_errno=True).fstatfs
    fn.argtypes=(ctypes.c_int,ctypes.POINTER(_Statfs))
    fn.restype=ctypes.c_int
    if fn(fd,ctypes.byref(info))!=0:
        raise OSError(ctypes.get_errno(),'fstatfs failed')
    return info


def _attributes(fd, common, volume, fmt, masks):
    query = struct.pack('=HH5I', 5, 0, _RETURNED | common, volume, 0, 0, 0)
    buf = ctypes.create_string_buffer(_HEADER.size + struct.calcsize(fmt))
    fn = ctypes.CDLL(None, use_errno=True).fgetattrlist
    fn.argtypes = (ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_ulong)
    fn.restype = ctypes.c_int
    require(fn(fd, query, buf, len(buf), 0) == 0, 'persistent-location-unavailable')
    length, *returned = _HEADER.unpack_from(buf)
    require(length == len(buf) and tuple(returned) == masks, 'persistent-location-unavailable')
    return struct.unpack_from(fmt, buf, _HEADER.size)


def persistent_identity(fd, info):
    from ..binding import DARWIN_VOLUME
    fs=filesystem(fd)
    require(fs.fstype==b'apfs' and fs.flags&0x1000,'persistent-location-unavailable')
    raw, = _attributes(fd, 0, 0x80000000 | _UUID, '=16s', (_RETURNED, _UUID, 0, 0, 0))
    seconds, nanos = _attributes(fd, _CRTIME, 0, '=qq', (_RETURNED | _CRTIME, 0, 0, 0, 0))
    require(any(raw) and info.st_ino > 0 and seconds > 0 and 0 <= nanos < 1_000_000_000,
            'persistent-location-unavailable')
    return DARWIN_VOLUME + str(uuid.UUID(bytes=raw)), f'{info.st_ino}:{seconds}:{nanos}'
