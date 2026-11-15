"""Local APFS file-effect port with exclusive moves and retained originals.

This port never accepts Work or decides authority. The caller must hold its lock,
reserve a durable effect, and validate whole-tree dependencies around each step.
Unknown outcomes preserve every remaining file. No cleanup or rollback API exists.
"""
from contextlib import contextmanager
import fcntl,hashlib,os,stat,sys
from pathlib import Path
from ..codec import RecordError,require
from ..storage.sqlite import _token
from ..tree import logical_path
from .posix import open_directory
from .exclusive import available,rename


from .darwin_location import filesystem


def local_apfs(fd):
    require(sys.platform=='darwin' and available(),'effect-writer-unavailable')
    info=filesystem(fd)
    # MNT_LOCAL from the native SDK; do not infer local semantics from a path.
    require(info.fstype==b'apfs' and info.flags&0x1000,'effect-filesystem-unqualified')


def identity(info):
    require(info.st_ino>0 and hasattr(info,'st_birthtime'),'effect-native-identity-unavailable')
    birth=getattr(info,'st_birthtime_ns',round(info.st_birthtime*1_000_000_000))
    return dict(volume=str(info.st_dev),inode=str(info.st_ino),birth_ns=birth)


def _private(info):
    require(stat.S_ISDIR(info.st_mode) and info.st_uid==os.getuid() and info.st_mode&0o077==0,'unsafe-effect-staging-directory')


def _name(directory,logical):
    found=None;aliases=set()
    with os.scandir(directory) as entries:
        for entry in entries:
            require(len(aliases)<1_000_000,'observation-entry-limit')
            value=logical_path(entry.name);alias=value.casefold()
            require(alias not in aliases,'path-collision');aliases.add(alias)
            if alias==logical.casefold():
                require(value==logical,'worker-path-alias');found=entry.name
    return logical if found is None else found


def _stat(directory,name):
    try:return os.stat(name,dir_fd=directory,follow_symlinks=False)
    except FileNotFoundError:return None


def inspect(directory,name,path):
    info=_stat(directory,name)
    if info is None:return None,None
    require(stat.S_ISREG(info.st_mode) and info.st_nlink==1,'effect-file-not-single-regular')
    fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=directory)
    try:
        before=os.fstat(fd);native=identity(before)
        require(native==identity(info),'effect-file-changed')
        digest=hashlib.sha256();size=0
        while raw:=os.read(fd,1024*1024):digest.update(raw);size+=len(raw)
        after=os.fstat(fd);current=os.stat(name,dir_fd=directory,follow_symlinks=False)
        signature=lambda st:(identity(st),st.st_size,st.st_mtime_ns,st.st_ctime_ns,st.st_mode,st.st_nlink)
        require(signature(before)==signature(after)==signature(current) and size==before.st_size,'effect-file-changed')
        return dict(path=path,kind='regular',mode='100755' if before.st_mode&0o111 else '100644',size=size,sha256=digest.hexdigest()),native
    finally:os.close(fd)


def _flush(fd):
    os.fsync(fd)
    fcntl.fcntl(fd,51)  # F_FULLFSYNC: failure remains an uncertain effect.


class DarwinEffects:
    def __init__(self,root,authority):
        self.root=Path(root);self.authority=Path(authority);self.locked=False
        with self._root() as fd,self._authority() as other:
            local_apfs(fd);local_apfs(other)
            require(os.fstat(fd).st_dev==os.fstat(other).st_dev,'effect-staging-volume-mismatch')
            self.root_identity=identity(os.fstat(fd));self.authority_identity=identity(os.fstat(other))
            # Staging must not become part of the project's observed content tree.
            require(not self.authority.is_relative_to(self.root) and not self.root.is_relative_to(self.authority),'effect-staging-overlaps-workspace')

    @contextmanager
    def _root(self):
        fd=open_directory(self.root)
        try:
            if hasattr(self,'root_identity'):require(identity(os.fstat(fd))==self.root_identity,'effect-root-changed')
            yield fd
        finally:os.close(fd)

    @contextmanager
    def _authority(self):
        fd=open_directory(self.authority)
        try:
            _private(os.fstat(fd))
            if hasattr(self,'authority_identity'):require(identity(os.fstat(fd))==self.authority_identity,'effect-authority-changed')
            yield fd
        finally:os.close(fd)

    @contextmanager
    def exclusion(self,*,create=True):
        require(not self.locked,'effect-lock-reentry')
        with self._authority() as directory:
            fd=os.open('effect.lock',os.O_RDWR|os.O_NOFOLLOW|(os.O_CREAT if create else 0),0o600,dir_fd=directory)
            acquired=False
            try:
                info=os.fstat(fd)
                require(stat.S_ISREG(info.st_mode) and info.st_nlink==1 and info.st_uid==os.getuid() and info.st_mode&0o077==0,'unsafe-effect-lock')
                try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);acquired=True
                except BlockingIOError:raise RecordError('effect-busy') from None
                require(identity(info)==identity(os.stat('effect.lock',dir_fd=directory,follow_symlinks=False)),'effect-lock-replaced')
                os.fsync(directory);self.locked=True
                yield
            finally:
                self.locked=False
                if acquired:fcntl.flock(fd,fcntl.LOCK_UN)
                os.close(fd)

    @contextmanager
    def _stage(self,application,*,create=False,expected=None):
        _token(application)
        with self._authority() as root:
            if create:
                try:os.mkdir('effects',0o700,dir_fd=root);os.fsync(root)
                except FileExistsError:pass
            area=os.open('effects',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=root)
            try:
                _private(os.fstat(area))
                if create:
                    try:os.mkdir(application,0o700,dir_fd=area)
                    except FileExistsError:raise RecordError('effect-staging-already-exists') from None
                    os.fsync(area)
                directory=os.open(application,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=area)
                try:
                    _private(os.fstat(directory));current=identity(os.fstat(directory))
                    if expected is not None:require(current==expected,'effect-staging-replaced')
                    yield directory,current
                finally:os.close(directory)
            finally:os.close(area)

    @contextmanager
    def destination(self,path,ancestors,*,create=False,check_identity=True):
        require(logical_path(path)==path,'invalid-worker-path')
        with self._root() as root:
            directory=os.dup(root)
            try:
                parts=path.split('/');prefix=[]
                for part in parts[:-1]:
                    prefix.append(part);logical='/'.join(prefix);name=_name(directory,part);current=_stat(directory,name)
                    require(logical in ancestors,'unplanned-effect-ancestor')
                    expected=ancestors[logical]
                    if current is None:
                        if not create:yield None,None;return
                        require(expected is None,'effect-ancestor-missing')
                        os.mkdir(name,0o755,dir_fd=directory);os.fsync(directory)
                        current=os.stat(name,dir_fd=directory,follow_symlinks=False)
                    require(stat.S_ISDIR(current.st_mode),'unsafe-effect-ancestor')
                    if check_identity and expected is not None:require(identity(current)==expected,'effect-ancestor-changed')
                    child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=directory)
                    require(identity(os.fstat(child))==identity(current),'effect-ancestor-changed')
                    os.close(directory);directory=child
                yield directory,_name(directory,parts[-1])
            finally:os.close(directory)

    def _ancestors(self,changes):
        result={}
        with self._root() as root:
            for item in changes:
                directory=os.dup(root);prefix=[];missing=False
                try:
                    for part in item['path'].split('/')[:-1]:
                        prefix.append(part);logical='/'.join(prefix)
                        if missing:result[logical]=None;continue
                        name=_name(directory,part);info=_stat(directory,name)
                        if info is None:missing=True;result[logical]=None;continue
                        require(stat.S_ISDIR(info.st_mode),'unsafe-effect-ancestor')
                        result[logical]=identity(info)
                        child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=directory)
                        require(identity(os.fstat(child))==result[logical],'effect-ancestor-changed')
                        os.close(directory);directory=child
                finally:os.close(directory)
        return result

    def inspect_target(self,path,ancestors):
        with self.destination(path,ancestors) as (directory,name):
            return inspect(directory,name,path) if directory is not None else (None,None)

    def prepare(self,application,changes,body):
        """Only reproducible post bodies are written before effect reservation."""
        require(self.locked,'effect-lock-required');ancestors=self._ancestors(changes);items=[]
        with self._stage(application,create=True) as (stage,native):
            for number,item in enumerate(changes):
                path=item['path'];post_name=f'{number:06d}.post';evacuated=f'{number:06d}.original'
                with self.destination(path,ancestors) as (directory,name):
                    observed,pre_native=inspect(directory,name,path) if directory is not None else (None,None)
                    require(observed==item['pre'],'worker-destination-baseline-changed')
                post_native=None
                if item['post'] is not None:
                    fd=os.open(post_name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=stage)
                    try:
                        for raw in body(path):
                            remaining=memoryview(raw)
                            while remaining:
                                count=os.write(fd,remaining);require(count>0,'effect-short-write');remaining=remaining[count:]
                        os.fchmod(fd,0o755 if item['post']['mode']=='100755' else 0o644);_flush(fd)
                    finally:os.close(fd)
                    actual,post_native=inspect(stage,post_name,path)
                    require(actual==item['post'],'effect-staged-body-mismatch');os.fsync(stage)
                items.append({**item,'post_name':post_name,'evacuated_name':evacuated,'pre_native':pre_native,'post_native':post_native})
            os.fsync(stage)
            return dict(application=application,root=self.root_identity,authority=self.authority_identity,stage=native,ancestors=ancestors,items=items)

    def state(self,manifest,index):return self.inspect_state(manifest,index)['state']

    def inspect_state(self,manifest,index):
        """Read actual entries; preserve late writes to the same retained original."""
        require(self.locked,'effect-lock-required');item=manifest['items'][index];path=item['path']
        require(manifest['root']==self.root_identity and manifest['authority']==self.authority_identity,'effect-port-identity-mismatch')
        with self._stage(manifest['application'],expected=manifest['stage']) as (stage,_):
            with self.destination(path,manifest['ancestors']) as (directory,name):
                current,native=inspect(directory,name,path) if directory is not None else (None,None)
            saved,saved_native=inspect(stage,item['evacuated_name'],path)
            staged,staged_native=inspect(stage,item['post_name'],path)
            if saved is not None:require(saved_native==item['pre_native'],'effect-evacuated-file-changed')
            modified=saved is not None and saved!=item['pre']
            if staged is not None:require(staged==item['post'] and staged_native==item['post_native'],'effect-staged-file-changed')
            if current==item['pre'] and native==item['pre_native'] and saved is None:
                require(staged==item['post'] and staged_native==item['post_native'],'effect-staged-file-missing');return dict(state='pre',retained_original_modified=False)
            if current==item['post'] and native==item['post_native'] and staged is None:
                require(saved_native==item['pre_native'] and (saved is None)==(item['pre'] is None),'effect-evacuated-file-missing')
                return dict(state='post',retained_original_modified=modified)
            if current is None and item['pre'] is not None and saved is not None and saved_native==item['pre_native']:
                require(staged==item['post'] and staged_native==item['post_native'],'effect-staged-file-missing');return dict(state='evacuated',retained_original_modified=modified)
            require(not modified,'effect-evacuated-file-changed')
            raise RecordError('effect-path-unknown')

    def retained_original_matches(self,manifest,index):
        """Verify the saved original even after a separate reverse effect."""
        require(self.locked,'effect-lock-required');item=manifest['items'][index]
        require(manifest['root']==self.root_identity and manifest['authority']==self.authority_identity,'effect-port-identity-mismatch')
        with self._stage(manifest['application'],expected=manifest['stage']) as (stage,_):
            saved,native=inspect(stage,item['evacuated_name'],item['path'])
            return saved==item['pre'] and native==item['pre_native']

    def _attached(self,path,ancestors,directory,*,check_identity=True):
        # Held descriptors prevent symlink traversal, but a renamed parent must
        # still be detected rather than silently writing into a detached tree.
        with self.destination(path,ancestors,check_identity=check_identity) as (current,_):
            require(current is not None and identity(os.fstat(current))==identity(os.fstat(directory)),'effect-ancestor-changed')

    def apply_one(self,manifest,index,*,before_effect=lambda:None,event=lambda name:None):
        """One original request only; a failed call never silently retries itself."""
        state=self.state(manifest,index);item=manifest['items'][index];path=item['path']
        if state=='post':
            self.sync(manifest,index);return
        with self._stage(manifest['application'],expected=manifest['stage']) as (stage,_):
            with self.destination(path,manifest['ancestors'],create=True) as (directory,name):
                if state=='pre' and item['pre'] is not None:
                    before_effect();event('before-evacuate');self._attached(path,manifest['ancestors'],directory)
                    rename(directory,name,stage,item['evacuated_name']);event('after-evacuate')
                    self._attached(path,manifest['ancestors'],directory)
                    saved,native=inspect(stage,item['evacuated_name'],path)
                    if saved!=item['pre'] or native!=item['pre_native']:
                        # Preserve a racing edit. Return only into a vacant name.
                        try:rename(stage,item['evacuated_name'],directory,name)
                        except (OSError,RecordError):pass
                        raise RecordError('effect-evacuated-file-changed')
                    fd=os.open(item['evacuated_name'],os.O_RDONLY|os.O_NOFOLLOW,dir_fd=stage)
                    try:_flush(fd)
                    finally:os.close(fd)
                if item['post'] is not None:
                    before_effect();event('before-install');self._attached(path,manifest['ancestors'],directory)
                    rename(stage,item['post_name'],directory,name);event('after-install')
                    self._attached(path,manifest['ancestors'],directory)
                    fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=directory)
                    try:_flush(fd)
                    finally:os.close(fd)
                os.fsync(directory);os.fsync(stage)
        require(self.state(manifest,index)=='post','effect-post-state-required')

    def sync(self,manifest,index):
        """Re-establish durability after a crash before publishing completion."""
        require(self.state(manifest,index)=='post','effect-post-state-required')
        item=manifest['items'][index]
        with self._stage(manifest['application'],expected=manifest['stage']) as (stage,_):
            if item['pre'] is not None:
                fd=os.open(item['evacuated_name'],os.O_RDONLY|os.O_NOFOLLOW,dir_fd=stage)
                try:_flush(fd)
                finally:os.close(fd)
            with self.destination(item['path'],manifest['ancestors']) as (directory,name):
                if item['post'] is not None:
                    fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=directory)
                    try:_flush(fd)
                    finally:os.close(fd)
                if directory is not None:os.fsync(directory)
            os.fsync(stage)
        require(self.state(manifest,index)=='post','effect-post-state-required')

    def cancellable(self,manifest,index):
        """Cancellation needs intact user preimages, not reproducible staged posts."""
        require(self.locked,'effect-lock-required');item=manifest['items'][index]
        require(manifest['root']==self.root_identity and manifest['authority']==self.authority_identity,'effect-port-identity-mismatch')
        with self._stage(manifest['application'],expected=manifest['stage']) as (stage,_):
            require(_stat(stage,item['evacuated_name']) is None,'worker-cancel-requires-all-pre')
            with self.destination(item['path'],manifest['ancestors'],check_identity=False) as (directory,name):
                current,native=inspect(directory,name,item['path']) if directory is not None else (None,None)
                if directory is not None:self._attached(item['path'],manifest['ancestors'],directory,check_identity=False)
            return current==item['pre']
