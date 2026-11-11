"""Separate Git candidate preparation and exact ref/index effects on local macOS.

No checkout, reset, refresh, hooks, filter, network, key creation or automatic
retry. The application journal must reserve the project barrier before effects.
"""
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
import hashlib,os,stat,sys,uuid
from ..adapters.git import read_file,_absolute
from ..codec import RecordError,canonical_bytes,decode_canonical,require
from ..git_index import Entry,Index,parse,emit,integrate,LIMIT
from ..platforms.posix import location,stamp,open_directory
from ..platforms.selected import selected
from ..storage.files import PosixFiles
from ..storage.sqlite import _token
from .darwin_execution import process_birth,group_absent
from .git_child import GitChild


def digest(raw):return hashlib.sha256(raw).hexdigest()
def file_identity(info):
    require(stat.S_ISREG(info.st_mode) and info.st_nlink==1,'git-unsafe-effect-file')
    return dict(scheme='macos-inode-v1',value=f'{info.st_dev}:{info.st_ino}:{int(info.st_birthtime*1_000_000_000)}')

def file_id(path):return file_identity(path.lstat())

def absent(path):
    try:path.lstat()
    except FileNotFoundError:return True
    return False

from .git_candidate import GitCandidate

class DarwinGit(GitCandidate):
    file_id=staticmethod(file_id)
    @staticmethod
    def index_mode(path):return stat.S_IMODE(path.lstat().st_mode)
    @staticmethod
    def require_inactive_hook(path):
        info=path.lstat();require(not stat.S_ISLNK(info.st_mode) and not info.st_mode&0o111,'git-hooks-require-manual-integration')
    def __init__(self,root,scratch,git,*,create=True):
        require(sys.platform=='darwin','git-integration-platform-unavailable')
        self.root=Path(root);self.scratch=Path(scratch);self.git=git;self.files=PosixFiles();self.locked=False
        self.files.private_directory(self.scratch);self.root_identity=asdict(location(self.root))
        for name in ('children','hooks'):
            path=self.scratch/name
            if absent(path):
                require(create,'git-staging-unavailable');self.files.create_directory(path)
            self.files.private_directory(path)
        require(not any((self.scratch/'hooks').iterdir()),'git-hooks-staging-not-empty')
        self.children=GitChild(self.scratch/'children')
        self.env={**self.git.env,'GIT_NO_REPLACE_OBJECTS':'1','GIT_NO_LAZY_FETCH':'1'}

    def acquire_index(self,m):
        self.verify_manifest(m);require(all(absent(p) for p in self.locks(m)),'git-child-lock-present')
        path=self.lock_path(m);fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        try:self.files.flush_file(fd)
        finally:os.close(fd)
        self.files.sync_directory(path.parent)
        return dict(native=file_id(path),pid=os.getpid(),birth=process_birth(os.getpid()))

    def owned_lock(self,m,owner):
        path=self.lock_path(m);require(not absent(path) and file_id(path)==owner['native'],'git-index-lock-not-owned')
        return path

    def replace_index(self,m,owner,*,live):
        path=self.owned_lock(m,owner);require(self.inspect_outcome(m)==('new','old'),'git-index-preimage-changed');require(all(absent(p) for p in self.locks(m)),'git-child-lock-present')
        raw=self.files.read(self.scratch/m['operation']/'i1',LIMIT);fd=os.open(path,os.O_WRONLY|os.O_NOFOLLOW)
        try:
            require(file_id(path)==owner['native'],'git-index-lock-not-owned')
            require(file_identity(os.fstat(fd))==owner['native'],'git-index-lock-not-owned')
            os.fchmod(fd,m['context'].get('index_mode') if m['context'].get('index_mode') is not None else 0o600)
            os.ftruncate(fd,0);view=memoryview(raw)
            while view:
                n=os.write(fd,view);require(n>0,'git-index-short-write');view=view[n:]
            self.files.flush_file(fd)
        finally:os.close(fd)
        require(self.inspect_outcome(m)==('new','old'),'git-index-preimage-changed');self.owned_lock(m,owner);live()
        os.replace(path,path.with_name('index'));self.files.sync_directory(path.parent)
        self.check_post(m)

    def flush_native(self,path):
        directory=open_directory(path.parent)
        try:
            fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=directory)
            try:
                before=os.fstat(fd);require(stat.S_ISREG(before.st_mode),'git-durability-file-unavailable');self.files.flush_file(fd)
                after=os.stat(path.name,dir_fd=directory,follow_symlinks=False)
                require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),'git-durability-file-changed')
            finally:os.close(fd)
            os.fsync(directory)
        finally:os.close(directory)

    def release_owned(self,m,owner):
        path=self.owned_lock(m,owner)
        require(all(absent(p) for p in self.locks(m)),'git-child-lock-present')
        current=process_birth(owner['pid'])
        require(owner['pid']==os.getpid() and current==owner['birth'] or
                current!=owner['birth'] and group_absent(owner['pid']),'git-lock-owner-still-live')
        path.unlink();self.files.sync_directory(path.parent)

    def recovery_ready(self,m,owner,child):
        require(all(absent(p) for p in self.locks(m)),'git-child-lock-present')
        if child is not None:require(self.children.closed(self.scratch/'children'/child),'git-child-closure-unavailable')
        if owner is not None:
            current=process_birth(owner['pid'])
            require(owner['pid']==os.getpid() and current==owner['birth'] or
                    current!=owner['birth'] and group_absent(owner['pid']),'git-lock-owner-still-live')

    def recover_index(self,m,owner,*,live):
        require(self.inspect_outcome(m)==('new','old'),'git-index-preimage-changed');live()
        path=self.lock_path(m)
        if absent(path):
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
            try:self.files.flush_file(fd)
            finally:os.close(fd)
            self.files.sync_directory(path.parent)
        else:self.owned_lock(m,owner)
        # Re-adopt an exactly owned lock in place. Deleting it before reacquiring
        # introduced an avoidable crash window; absent locks still use O_EXCL.
        require(self.inspect_outcome(m)==('new','old'),'git-index-preimage-changed')
        return dict(native=file_id(path),pid=os.getpid(),birth=process_birth(os.getpid()))


    def finalize_index(self,m,owner,*,live):
        live();require(self.lock_absent(m),'git-index-lock-not-owned')
