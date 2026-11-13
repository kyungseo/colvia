"""Free space for a particular update write, reported for its actual destination."""
import errno
import os
from contextlib import contextmanager
from pathlib import Path
import shutil

from ..codec import RecordError


STAGING_ALLOWANCE = 16 * 1024**2


class SpaceError(RecordError):
    def __init__(self, code, path, phase, *, required=None, available=None):
        super().__init__(code)
        self.diagnostic = dict(phase=phase, volume=_volume(path))
        if required is not None:
            self.diagnostic['required_bytes'] = required
        if available is not None:
            self.diagnostic['available_bytes'] = available


def _volume(path):
    path = Path(path)
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes

        get_volume = ctypes.WinDLL('kernel32').GetVolumePathNameW
        get_volume.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        get_volume.restype = wintypes.BOOL
        buffer = ctypes.create_unicode_buffer(32768)
        if get_volume(str(path), buffer, len(buffer)):
            return buffer.value
    return path.anchor


def require_space(path, required, phase, *, code='update-space-insufficient'):
    try:
        available = shutil.disk_usage(path).free
    except OSError:
        raise SpaceError('update-space-query-unavailable', path, phase, required=required) from None
    if available < required:
        raise SpaceError(code, path, phase, required=required, available=available)


@contextmanager
def write_space(path, phase):
    try:
        yield
    except OSError as error:
        if error.errno != errno.ENOSPC and getattr(error, 'winerror', None) not in (39, 112):
            raise
        raise SpaceError('update-disk-full', path, phase) from error
