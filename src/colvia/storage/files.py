"""Small lifecycle-file primitives for qualified POSIX storage adapters.

Windows needs its own qualified locking/replace adapter; source success here is
not Windows qualification. No cache reset, application setting or OS grant occurs.
"""
from contextlib import contextmanager
import os
from pathlib import Path
import stat
import sys
import time
import uuid

from ..codec import RecordError, require


class PosixFiles:
    def __init__(self):
        require(os.name=='posix','platform-files-adapter-unavailable')

    def private_directory(self,path):
        path=Path(path)
        for parent in (path,*path.parents):require(not parent.is_symlink(),'symlink-lifecycle-path')
        info=path.lstat()
        require(stat.S_ISDIR(info.st_mode) and info.st_uid==os.getuid() and info.st_mode&0o077==0,'lifecycle-root-not-private')

    def create_directory(self,path):
        path=Path(path)
        for parent in path.parents:require(not parent.is_symlink(),'symlink-lifecycle-path')
        path.mkdir(mode=0o700);self.private_directory(path);self.sync_directory(path.parent)

    def directory_identity(self,path):
        self.private_directory(path);info=Path(path).lstat()
        return [info.st_dev,info.st_ino]

    def publish_directory(self,source,destination,identity):
        from ..platforms.exclusive import rename
        source=Path(source);destination=Path(destination)
        require(source.parent==destination.parent and source!=destination,'lifecycle-publication-parent')
        require(self.directory_identity(source)==identity,'lifecycle-directory-changed')
        for parent in source.parents:require(not parent.is_symlink(),'symlink-lifecycle-path')
        directory=os.open(source.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:
            parent=source.parent.lstat();opened=os.fstat(directory)
            require((parent.st_dev,parent.st_ino)==(opened.st_dev,opened.st_ino),'lifecycle-parent-changed')
            require(self.directory_identity(source)==identity,'lifecycle-directory-changed')
            try:rename(directory,source.name,directory,destination.name)
            except (OSError,RecordError) as exc:
                raise RecordError('lifecycle-directory-publication-unconfirmed') from exc
            after=source.parent.lstat()
            require((after.st_dev,after.st_ino)==(opened.st_dev,opened.st_ino) and self.directory_identity(destination)==identity and not os.path.lexists(source),'lifecycle-directory-publication-unconfirmed')
        finally:os.close(directory)

    def flush_file(self,fd):
        os.fsync(fd)
        if sys.platform=='darwin':
            import fcntl
            command=getattr(fcntl,'F_FULLFSYNC',None)
            require(command is not None,'lifecycle-fullsync-unavailable')
            fcntl.fcntl(fd,command)

    def read(self,path:Path,limit=16384):
        for parent in path.parents: require(not parent.is_symlink(),'symlink-lifecycle-path')
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
        try:
            info=os.fstat(fd)
            require(stat.S_ISREG(info.st_mode) and info.st_nlink==1 and info.st_size<=limit,
                    'invalid-lifecycle-file')
            raw=os.read(fd,limit+1)
            signature=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_mode,s.st_nlink)
            require(len(raw)<=limit and len(raw)==info.st_size and
                    signature(info)==signature(os.fstat(fd))==signature(path.lstat()),'lifecycle-file-changed')
            return raw
        finally: os.close(fd)

    @contextmanager
    def read_stream(self,path,limit):
        path=Path(path)
        for parent in path.parents:require(not parent.is_symlink(),'symlink-lifecycle-path')
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
        with os.fdopen(fd,'rb') as stream:
            before=os.fstat(stream.fileno())
            require(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_size<=limit,'invalid-lifecycle-file')
            signature=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_mode,s.st_nlink)
            def verify():
                require(signature(before)==signature(os.fstat(stream.fileno()))==signature(path.lstat()),'lifecycle-file-changed')
            verify();yield stream;verify()

    @contextmanager
    def create_stream(self,path,*,executable=False):
        path=Path(path)
        for parent in path.parents:require(not parent.is_symlink(),'symlink-lifecycle-path')
        fd=os.open(path,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o700 if executable else 0o600)
        with os.fdopen(fd,'w+b') as stream:
            yield stream
            stream.flush();self.flush_file(stream.fileno())
        self.sync_directory(path.parent)

    def sync_directory(self,path:Path):
        fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try: os.fsync(fd)
        finally: os.close(fd)

    def _write_new(self,path:Path,raw:bytes,*,executable=False):
        for parent in path.parents: require(not parent.is_symlink(),'symlink-lifecycle-path')
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o700 if executable else 0o600)
        try:
            view=memoryview(raw)
            while view:
                written=os.write(fd,view)
                require(written>0,'lifecycle-short-write'); view=view[written:]
            self.flush_file(fd)
        finally: os.close(fd)
        self.sync_directory(path.parent)

    def exists(self,path:Path):
        try:self.read(path)
        except FileNotFoundError:return False
        return True

    def create(self,path:Path,raw:bytes,*,executable=False):
        from ..platforms.exclusive import available,rename
        require(available(),'lifecycle-exclusive-publication-unavailable')
        for parent in path.parents:require(not parent.is_symlink(),'symlink-lifecycle-path')
        try:path.lstat()
        except FileNotFoundError:pass
        else:raise FileExistsError(str(path))
        temporary=path.parent/(path.name+'.prepared-'+uuid.uuid4().hex)
        self._write_new(temporary,raw,executable=executable)
        directory=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:
            parent=path.parent.lstat();opened=os.fstat(directory)
            require((parent.st_dev,parent.st_ino)==(opened.st_dev,opened.st_ino),'lifecycle-parent-changed')
            try:rename(directory,temporary.name,directory,path.name)
            except RecordError as exc:
                if exc.code=='effect-destination-occupied':raise FileExistsError(str(path)) from exc
                raise
            except OSError as exc:raise RecordError('lifecycle-create-outcome-unknown') from exc
        finally:os.close(directory)

    def replace(self,path:Path,raw:bytes,expected:bytes):
        require(self.read(path)==expected,'lifecycle-pointer-conflict')
        temporary=path.parent/(path.name+'.prepared-'+uuid.uuid4().hex)
        self.create(temporary,raw)
        require(self.read(path)==expected,'lifecycle-pointer-conflict')
        os.replace(temporary,path)
        try:
            self.sync_directory(path.parent)
            require(self.read(path)==raw,'lifecycle-replace-unconfirmed')
        except (OSError,RecordError) as exc:raise RecordError('lifecycle-replace-durability-unknown') from exc

    def remove(self,path:Path,expected:bytes):
        require(self.read(path)==expected,'lifecycle-pointer-conflict')
        path.unlink(); self.sync_directory(path.parent)

    @contextmanager
    def exclusion(self,path:Path,timeout=5,*,shared=False):
        import fcntl
        fd=os.open(path,(os.O_RDONLY if shared else os.O_RDWR)|os.O_NOFOLLOW)
        locked=False
        try:
            info=os.fstat(fd)
            require(stat.S_ISREG(info.st_mode) and info.st_nlink==1,'unsafe-lifecycle-lock')
            deadline=time.monotonic()+timeout
            while True:
                try:
                    fcntl.flock(fd,(fcntl.LOCK_SH if shared else fcntl.LOCK_EX)|fcntl.LOCK_NB); locked=True; break
                except BlockingIOError:
                    if time.monotonic()>=deadline: raise RecordError('lifecycle-busy') from None
                    time.sleep(min(0.02,max(0,deadline-time.monotonic())))
            current=path.lstat()
            require((current.st_dev,current.st_ino)==(info.st_dev,info.st_ino),'lifecycle-lock-replaced')
            yield
        finally:
            if locked: fcntl.flock(fd,fcntl.LOCK_UN)
            os.close(fd)


def platform_files():
    if sys.platform=='win32':
        from .windows import WindowsFiles
        return WindowsFiles()
    return PosixFiles()
