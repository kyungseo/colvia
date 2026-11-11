"""Platform-exclusive rename port. Never fall back to overwriting a target.

Darwin source support uses renameatx_np(RENAME_EXCL), declared in the SDK's
sys/stdio.h. Other platforms require their own qualified implementation.
"""
import ctypes,errno,os,stat,sys
from ..codec import RecordError,require


def available():
    return sys.platform=='darwin' and hasattr(ctypes.CDLL(None,use_errno=True),'renameatx_np')


def _component(name):
    require(type(name) is str and name not in ('','.','..') and '/' not in name and '\\' not in name and '\x00' not in name,
            'invalid-native-component')


def rename(source_fd,source_name,destination_fd,destination_name):
    """Move one directory entry only if the destination is absent atomically.

    The caller owns the no-follow descriptors, native identities, authorization,
    journal and recovery protocol. Success here is not a completed Work.
    """
    require(available(),'exclusive-rename-unavailable')
    _component(source_name);_component(destination_name)
    for fd in (source_fd,destination_fd):
        require(type(fd) is int and stat.S_ISDIR(os.fstat(fd).st_mode),'invalid-directory-handle')
    require(os.fstat(source_fd).st_dev==os.fstat(destination_fd).st_dev,'effect-staging-volume-mismatch')
    function=ctypes.CDLL(None,use_errno=True).renameatx_np
    function.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint]
    function.restype=ctypes.c_int
    if function(source_fd,os.fsencode(source_name),destination_fd,os.fsencode(destination_name),4)!=0:
        error=ctypes.get_errno()
        if error in (errno.EEXIST,errno.ENOTEMPTY):raise RecordError('effect-destination-occupied')
        if error in (errno.ENOTSUP,errno.EINVAL,errno.EXDEV):raise RecordError('exclusive-rename-unavailable')
        raise OSError(error,os.strerror(error))
    # A sync error after rename is an unknown external outcome for the caller.
    os.fsync(destination_fd)
    if source_fd!=destination_fd:os.fsync(source_fd)
