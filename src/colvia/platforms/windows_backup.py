"""Native no-replace backup destination, independent of the private authority ACL.

The selected parent is never chmod'ed or re-ACL'ed. Only the newly created backup
gets the current user's private ACL. Network/reparse/non-NTFS destinations refuse.
Native ARM64/x64 qualification is separate from portable protocol tests.
"""
from contextlib import contextmanager,ExitStack
from pathlib import Path
import os,shutil
from ..codec import require
from ..storage.windows import WindowsFiles,local_path


class Destination:
    def __init__(self,parent,*,files=None):
        self.parent=Path(parent);self.files=files or WindowsFiles();self.api=self.files.api

    def __enter__(self):
        self.stack=ExitStack();a=self.api
        try:
            self.stack.enter_context(a.ancestors(self.parent))
            self.handle=self.stack.enter_context(a.opened(self.parent,share=3))
            self.original=a.state(self.handle,self.parent)
            require(self.original['directory'],'backup-parent-not-directory')
            return self
        except BaseException:self.stack.close();raise

    def __exit__(self,*exc):self.stack.close()

    def check(self):
        require(self.api.state(self.handle,self.parent)['identity']==self.original['identity'],'backup-directory-changed')
        with self.api.opened(self.parent,share=3) as current:
            require(self.api.state(current,self.parent)['identity']==self.original['identity'],'backup-directory-changed')

    def path(self,name):
        require(type(name) is str and name and Path(name).name==name and name not in ('.','..'),'backup-invalid-name')
        return self.parent/name

    def exists(self,name):
        self.check()
        try:
            with self.api.opened(self.path(name),share=1) as h:self.api.state(h,self.path(name))
        except FileNotFoundError:return False
        return True

    def free_bytes(self):self.check();return shutil.disk_usage(self.parent).free

    def stamp(self,name):
        self.check();path=self.path(name)
        with self.api.opened(path,share=1) as h:
            info=self.api.state(h,path);self.api.private(h)
            require(not info['directory'] and info['links']==1,'backup-file-identity')
            return info

    @contextmanager
    def create(self,name):
        self.check();a=self.api;path=self.path(name)
        with a.security() as sd,a.opened(path,access=0xc0020080,share=0,disposition=1,security=sd) as h:
            before=a.state(h,path);a.private(h)
            require(not before['directory'] and before['links']==1,'backup-file-identity')
            with self.files._stream_handle(h,write=True) as stream:
                yield stream
                stream.flush();a.ok(a.FlushFileBuffers(h))
            require(a.state(h,path)['identity']==before['identity'],'backup-file-changed')
        self.files.sync_directory(self.parent);self.check()

    def read(self,name,limit):return self.files.read_stream(self.path(name),limit)

    def publish(self,prepared,name,expected):
        require(self.stamp(prepared)==expected,'backup-file-changed')
        self.check()
        # No REPLACE_EXISTING, COPY_ALLOWED, reboot scheduling or privilege change.
        self.api.ok(self.api.MoveFileExW(local_path(self.path(prepared)),local_path(self.path(name)),8))
        self.files.sync_directory(self.parent);self.check()
        info=self.stamp(name)
        require(info['identity']==expected['identity'] and info['size']==expected['size'],'backup-published-file-changed')
