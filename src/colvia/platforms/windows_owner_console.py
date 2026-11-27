"""Foreground, standard-account console for explicit product decisions on native x64."""
import ctypes as C
from ctypes import wintypes as W
from contextlib import contextmanager
from hashlib import file_digest
from pathlib import Path
import sys

from ..codec import require


def _function(dll, name, result, *arguments):
    fn = getattr(dll, name)
    fn.restype = result
    fn.argtypes = list(arguments)
    return fn


def _ok(result):
    if not result:
        raise C.WinError(C.get_last_error())
    return result


def _standard_token(kernel, security):
    token = W.HANDLE()
    process = W.HANDLE(-1)
    open_token = _function(security, 'OpenProcessToken', W.BOOL, W.HANDLE, W.DWORD, C.POINTER(W.HANDLE))
    _ok(open_token(process, 0x0008, C.byref(token)))  # TOKEN_QUERY only
    try:
        query = _function(security, 'GetTokenInformation', W.BOOL, W.HANDLE, C.c_int,
                          C.c_void_p, W.DWORD, C.POINTER(W.DWORD))
        used = W.DWORD()
        for kind in (20, 29):  # elevation, AppContainer
            flag = W.DWORD()
            _ok(query(token, kind, C.byref(flag), C.sizeof(flag), C.byref(used)))
            require(not flag.value, 'parallel-standard-console-required')
        elevation_type = W.DWORD()
        _ok(query(token, 18, C.byref(elevation_type), C.sizeof(elevation_type), C.byref(used)))
        require(elevation_type.value == 1, 'parallel-standard-console-required')
        restricted = _function(security, 'IsTokenRestricted', W.BOOL, W.HANDLE)
        require(not restricted(token), 'parallel-standard-console-required')
        size = W.DWORD()
        query(token, 25, None, 0, C.byref(size))
        require(0 < size.value <= 4096, 'parallel-standard-console-required')
        label = C.create_string_buffer(size.value)
        _ok(query(token, 25, label, size.value, C.byref(used)))
        sid = C.cast(label, C.POINTER(C.c_void_p))[0]
        subcount = _function(security, 'GetSidSubAuthorityCount', C.POINTER(C.c_ubyte), C.c_void_p)
        sub = _function(security, 'GetSidSubAuthority', C.POINTER(W.DWORD), C.c_void_p, W.DWORD)
        count = subcount(sid)[0]
        require(count > 0 and sub(sid, count - 1)[0] == 0x2000, 'parallel-standard-console-required')
        in_job = W.BOOL()
        _ok(_function(kernel, 'IsProcessInJob', W.BOOL, W.HANDLE, W.HANDLE,
                      C.POINTER(W.BOOL))(process, None, C.byref(in_job)))
        if in_job.value:
            flags = W.DWORD()
            _ok(_function(kernel, 'QueryInformationJobObject', W.BOOL, W.HANDLE, C.c_int,
                          C.c_void_p, W.DWORD, C.POINTER(W.DWORD))(
                              None, 4, C.byref(flags), C.sizeof(flags), C.byref(used)))
            require(flags.value == 0, 'parallel-standard-console-required')
    finally:
        _ok(_function(kernel, 'CloseHandle', W.BOOL, W.HANDLE)(token))


class OwnerConsole:
    def __init__(self):
        from .windows_group_workers import native_required
        native_required()
        import msvcrt
        self.kernel = C.WinDLL('kernel32', use_last_error=True)
        self.security = C.WinDLL('advapi32', use_last_error=True)
        _standard_token(self.kernel, self.security)
        mode = _function(self.kernel, 'GetConsoleMode', W.BOOL, W.HANDLE, C.POINTER(W.DWORD))
        for stream in (sys.stdin, sys.stdout, sys.stderr):
            require(stream is not None and stream.isatty(), 'parallel-interactive-console-required')
            handle = msvcrt.get_osfhandle(stream.fileno())
            _ok(mode(handle, C.byref(W.DWORD())))
        self.input_handle = msvcrt.get_osfhandle(sys.stdin.fileno())

    def show(self, text):
        text.encode(sys.stdout.encoding, errors='strict')
        print(text, flush=True)

    def ask(self, text):
        _ok(_function(self.kernel, 'FlushConsoleInputBuffer', W.BOOL, W.HANDLE)(self.input_handle))
        self.show(text)
        try:
            return input()
        except (EOFError, KeyboardInterrupt):
            return ''


@contextmanager
def pinned_codex(files):
    from .windows_group_workers import PINNED
    from .windows_paths import local_appdata
    version, expected = PINNED['codex']
    path = Path(local_appdata()) / 'Programs' / 'OpenAI' / 'Codex' / version / 'bin' / 'codex.exe'
    api = files.api
    with api.ancestors(path), api.opened(path, access=0x80000080, share=1) as handle:
        before = api.state(handle, path)
        require(not before['directory'] and before['links'] == 1, 'group-worker-executable-unqualified')
        with files._stream_handle(handle) as stream:
            require(file_digest(stream, 'sha256').hexdigest() == expected, 'group-worker-executable-unqualified')
        require(api.state(handle, path) == before, 'group-worker-executable-unqualified')
        yield {'codex': dict(path=str(path), version=version, sha256=expected)}

