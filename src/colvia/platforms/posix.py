"""POSIX native identities and no-follow snapshots behind the observation port."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import base64
import hashlib
import os
import stat

from ..binding import NativeLocation
from ..codec import RecordError, canonical_bytes, require
from ..tree import canonical_entries, logical_path


def identity(info):
    require(info.st_ino>0,'file-identity-unavailable')
    return str(info.st_dev),str(info.st_ino)


def open_directory(path: Path):
    require(os.name=='posix','platform-adapter-unavailable')
    path=Path(path)
    require(path.is_absolute() and all(part not in ('.','..') for part in path.parts),'absolute-native-path-required')
    fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY)
    try:
        for component in path.parts[1:]:
            child=os.open(component,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            os.close(fd);fd=child
        return fd
    except BaseException:
        os.close(fd);raise


def location(path: Path) -> NativeLocation:
    fd=open_directory(path)
    try:
        volume,file_id=identity(os.fstat(fd))
        return NativeLocation(str(path),volume,file_id)
    finally:os.close(fd)


@dataclass(frozen=True)
class ObservationBudget:
    entries: int
    read_bytes: int


@dataclass(frozen=True)
class NativeStamp:
    native_path: str
    volume: str
    file_id: str
    mode: int
    size: int
    mtime_ns: int
    ctime_ns: int


def stamp(native,info):
    volume,file_id=identity(info)
    return NativeStamp(native,volume,file_id,info.st_mode,info.st_size,info.st_mtime_ns,info.st_ctime_ns)


@dataclass(frozen=True)
class Snapshot:
    root: NativeLocation
    entries: tuple[dict,...]
    stamps: tuple[NativeStamp,...]
    bytes_read: int
    inventory: tuple[NativeStamp,...] = ()
    git_blobs: tuple[tuple[str,str],...] = ()


def snapshot(root: Path, budget: ObservationBudget, *, admit=lambda _:True,
             protected=frozenset(), boundaries=None, cancelled=lambda:False,
             reject_nested_git=False, git_algorithm=None, opaque_entries=None) -> Snapshot:
    """Prune only caller-proved native structural boundaries, not name guesses.

    The caller owns Git/policy verification. `boundaries` maps exact native relative
    paths to expected (device,inode) pairs. All other directories, including ignored
    ones, are enumerated so an old protected path cannot disappear under a rule.
    """
    require(type(budget.entries) is int and 0<budget.entries<=1_000_000 and
            type(budget.read_bytes) is int and budget.read_bytes>=0,'invalid-observation-budget')
    require(git_algorithm in (None,'sha1','sha256'),'unsupported-git-object-format')
    opaque_entries=dict(opaque_entries or {})
    boundaries=dict(boundaries or {})
    for path,pair in boundaries.items():
        require(logical_path(path)==path and type(pair) is tuple and len(pair)==2,'invalid-boundary')
    root=Path(root);rootfd=open_directory(root);rootinfo=os.fstat(rootfd)
    root_location=NativeLocation(str(root),*identity(rootinfo))
    entries=[];stamps=[];inventory=[];git_blobs=[];visited=0;read_bytes=0;metadata_bytes=0;aliases=set()
    def listing(fd,limit):
        names=[]
        with os.scandir(fd) as scan:
            for item in scan:
                require(len(names)<limit,'observation-entry-limit')
                names.append(item.name)
        return sorted(names,key=os.fsencode)
    # Recursive calls retain only directory descriptors; cap depth before OS limits.
    def visit(fd,parts,depth):
        nonlocal visited,read_bytes,metadata_bytes
        require(depth<=128,'observation-depth-limit')
        before=os.fstat(fd)
        names=listing(fd,budget.entries-visited)
        for name in names:
            require(not cancelled(),'observation-cancelled')
            native='/'.join((*parts,name));logical=logical_path(native)
            require(logical.casefold() not in aliases,'path-collision')
            aliases.add(logical.casefold())
            info=os.stat(name,dir_fd=fd,follow_symlinks=False)
            visited+=1;require(visited<=budget.entries,'observation-entry-limit')
            if native in boundaries:
                require(not any(p==logical or p.startswith(logical+'/') for p in protected),'boundary-swallows-protected')
                require(identity(info)==boundaries[native] and not stat.S_ISLNK(info.st_mode),'structural-boundary-changed')
                continue
            require(not reject_nested_git or name!='.git','unregistered-nested-git')
            inventory.append(stamp(native,info))
            if native in opaque_entries:
                pair,entry=opaque_entries[native]
                require(stat.S_ISDIR(info.st_mode) and identity(info)==pair,'opaque-entry-changed')
                require(entry['path']==logical and entry['kind']=='gitlink','invalid-opaque-entry')
                canonical_entries([entry])
                metadata_bytes+=len(canonical_bytes(entry))
                require(metadata_bytes<=512*1024*1024,'observation-metadata-limit')
                entries.append(entry);stamps.append(stamp(native,info))
                continue
            if stat.S_ISDIR(info.st_mode):
                child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
                try:
                    require(identity(os.fstat(child))==identity(info),'directory-replaced')
                    visit(child,(*parts,name),depth+1)
                    require(identity(os.stat(name,dir_fd=fd,follow_symlinks=False))==identity(info),'directory-replaced')
                finally:os.close(child)
                continue
            if not (admit(logical) or logical in protected):
                continue
            initial=stamp(native,info)
            if stat.S_ISREG(info.st_mode):
                require(read_bytes+info.st_size<=budget.read_bytes,'observation-byte-limit')
                filefd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=fd)
                try:
                    require(stamp(native,os.fstat(filefd))==initial,'file-observation-changed')
                    digest=hashlib.sha256();size=0
                    blob=hashlib.new(git_algorithm) if git_algorithm else None
                    if blob is not None:blob.update(b'blob '+str(info.st_size).encode('ascii')+b'\0')
                    while raw:=os.read(filefd,1024*1024):
                        size+=len(raw);read_bytes+=len(raw)
                        require(read_bytes<=budget.read_bytes,'observation-byte-limit')
                        require(not cancelled(),'observation-cancelled');digest.update(raw)
                        if blob is not None:blob.update(raw)
                    require(size==info.st_size and stamp(native,os.fstat(filefd))==initial,'file-observation-changed')
                finally:os.close(filefd)
                entry=dict(path=logical,kind='regular',mode='100755' if info.st_mode & 0o111 else '100644',
                           size=size,sha256=digest.hexdigest())
                if blob is not None:git_blobs.append((logical,blob.hexdigest()))
            elif stat.S_ISLNK(info.st_mode):
                target=os.fsencode(os.readlink(name,dir_fd=fd))
                entry=dict(path=logical,kind='symlink',mode='120000',target=base64.b64encode(target).decode('ascii'))
                if git_algorithm:
                    blob=hashlib.new(git_algorithm);blob.update(b'blob '+str(len(target)).encode('ascii')+b'\0'+target)
                    git_blobs.append((logical,blob.hexdigest()))
            else:raise RecordError('unsupported-entry-type')
            require(stamp(native,os.stat(name,dir_fd=fd,follow_symlinks=False))==initial,'file-observation-changed')
            metadata_bytes+=len(canonical_bytes(entry))
            require(metadata_bytes<=512*1024*1024,'observation-metadata-limit')
            entries.append(entry);stamps.append(initial)
        require(names==listing(fd,len(names)) and
                stamp('',before)==stamp('',os.fstat(fd)),'directory-observation-changed')
    try:
        visit(rootfd,(),0)
        require(location(root)==root_location,'root-observation-changed')
        result=canonical_entries(entries)
        return Snapshot(root_location,tuple(result),tuple(stamps),read_bytes,tuple(inventory),tuple(git_blobs))
    finally:os.close(rootfd)
