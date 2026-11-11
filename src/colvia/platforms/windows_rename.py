"""Exact-handle, no-replace move on local NTFS; never copy/delete fallback.

Native ARM64/x64 execution remains a qualification step. The caller owns the
journal and decides recovery from the retained source/destination, not an exit
code. This primitive neither changes an ACL nor enables a privilege.
"""
from contextlib import ExitStack
from pathlib import PureWindowsPath
import ctypes as C,hashlib
from ..codec import require
from ..storage.windows import API,WindowsFiles,local_path


class RenameInfo(C.Structure):
    # Windows DWORD is always 32 bits, even on a non-Windows test host.
    _fields_=[('flags',C.c_uint32),('directory',C.c_void_p),
              ('length',C.c_uint32),('name',C.c_uint16*1)]


def rename_info(target):
    # Win32 FileRenameInfo accepts an absolute DOS target with RootDirectory
    # NULL. The caller holds every ancestor without FILE_SHARE_DELETE so the
    # validated target parent cannot be substituted while this call runs.
    name=local_path(target)
    raw=name.encode('utf-16-le')
    value=C.create_string_buffer(max(C.sizeof(RenameInfo),RenameInfo.name.offset+len(raw)+2))
    header=RenameInfo.from_buffer(value);header.flags=0;header.directory=None;header.length=len(raw)
    C.memmove(C.addressof(value)+RenameInfo.name.offset,raw,len(raw))
    return value


class RenameAPI(API):
    def __init__(self):
        super().__init__()
        self.bind(self.kernel,'SetFileInformationByHandle',self.W.BOOL,
                  (self.W.HANDLE,C.c_int,C.c_void_p,self.W.DWORD))
    def rename(self,source,target):
        value=rename_info(target)
        # FileRenameInfo=3; flags zero means ReplaceIfExists FALSE. No
        # FILE_RENAME_POSIX_SEMANTICS, delayed reboot or cross-volume fallback.
        self.ok(self.SetFileInformationByHandle(source,3,value,len(value)))


class ExactMove:
    def __init__(self,*,api=None,files=None):
        self.api=api or RenameAPI();self.files=files or WindowsFiles(api=self.api)
    def move(self,source,target,*,expected,limit=128*1024*1024,before_effect=lambda:None,event=lambda _:None):
        source=PureWindowsPath(local_path(source));target=PureWindowsPath(local_path(target));a=self.api
        require(source!=target and source.parent!=source and target.parent!=target,'windows-rename-path-invalid')
        require(type(limit) is int and 0<=limit<=1024**3,'windows-rename-byte-limit')
        with ExitStack() as stack:
            stack.enter_context(a.ancestors(str(source)))
            stack.enter_context(a.ancestors(str(target)))
            parent=stack.enter_context(a.opened(str(target.parent),access=0x80,share=3))
            parent_info=a.state(parent,str(target.parent));require(parent_info['directory'],'windows-rename-parent-invalid')
            # DELETE + GENERIC_READ + attributes; deny concurrent writes and
            # deletes. A conflicting existing handle causes an ordinary refusal.
            handle=stack.enter_context(a.opened(str(source),access=0x80010080,share=1))
            info=a.state(handle,str(source));require(not info['directory'] and info['links']==1 and
                not info.get('symlink') and info['size']<=limit,'windows-rename-source-invalid')
            require(info['identity'][0]==parent_info['identity'][0],'effect-staging-volume-mismatch')
            digest=hashlib.sha256();size=0
            with self.files._stream_handle(handle) as stream:
                while raw:=stream.read(1024*1024):
                    size+=len(raw);require(size<=limit,'windows-rename-byte-limit');digest.update(raw)
            actual=dict(identity=list(info['identity']),size=size,sha256=digest.hexdigest())
            require(size==info['size'] and actual==expected and a.state(handle,str(source))==info,
                    'windows-rename-source-changed')
            before_effect();event('before-native-move')
            require(a.state(parent,str(target.parent))['identity']==parent_info['identity'] and
                    a.state(handle,str(source))==info,'windows-rename-source-changed')
            a.rename(handle,str(target));event('after-native-move')
            # An exception after rename is an unknown effect, never a license
            # to repeat it or replace a competing destination.
            after=a.state(handle,str(target))
            require(after['identity']==info['identity'] and after['size']==info['size'] and
                    after['write']==info['write'] and after['links']==1,'windows-rename-result-changed')
            require(a.state(parent,str(target.parent))['identity']==parent_info['identity'],'windows-rename-parent-changed')
            return actual
