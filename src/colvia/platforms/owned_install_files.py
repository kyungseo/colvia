"""Exact initial-install nodes; no replacement, copying or recursive cleanup.

Callers hold management exclusion and persist their move intent first. Native
uncertainty is retained for explicit inspection, never silently retried.
"""
import hashlib,os,stat
from pathlib import Path
from ..codec import require

LIMIT=64*1024*1024

def present(path):
    """Only actual not-found is absence; denied/indeterminate lookups propagate."""
    try:os.lstat(path)
    except FileNotFoundError:return False
    return True


def _info(files,path):
    path=Path(path)
    if hasattr(files,'api'):
        a=files.api
        with a.ancestors(path),a.opened(path) as handle:
            v=a.state(handle,path);a.private(handle,directory=v['directory'])
            require(v['directory'] or v['links']==1,'initial-node-hardlink')
            return dict(kind='directory' if v['directory'] else 'file',identity=list(v['identity']),mode='100644',permissions=0)
    for parent in (path,*path.parents):require(not parent.is_symlink(),'initial-node-symlink')
    v=path.lstat();directory=stat.S_ISDIR(v.st_mode)
    require(v.st_uid==os.getuid() and (directory or (stat.S_ISREG(v.st_mode) and v.st_nlink==1)),'initial-node-not-regular')
    if directory:files.private_directory(path)
    birth=getattr(v,'st_birthtime_ns',round(getattr(v,'st_birthtime',0)*1_000_000_000))
    require(birth>0,'initial-node-identity-unavailable')
    return dict(kind='directory' if directory else 'file',identity=[v.st_dev,v.st_ino,birth],
                mode='100755' if v.st_mode&0o111 else '100644',permissions=stat.S_IMODE(v.st_mode))

def capture(files,path):
    before=_info(files,path)
    if before['kind']=='directory':return before
    raw=files.read(Path(path),LIMIT)
    require(_info(files,path)==before,'initial-node-changed')
    return dict(before,size=len(raw),sha256=hashlib.sha256(raw).hexdigest())

def move(files,source,destination,expected,*,parent_identities=None,verified_tree=False):
    source=Path(source);destination=Path(destination)
    require(source!=destination and capture(files,source)==expected,'initial-node-changed')
    parents={p:files.directory_identity(p) for p in (source.parent,destination.parent)}
    require(parent_identities is None or all(parents.get(p)==v for p,v in parent_identities.items()),'initial-parent-changed')
    require(all(v[0]==expected['identity'][0] for v in parents.values()),'initial-node-volume-mismatch')
    require(not present(destination),'initial-node-destination-exists')
    if expected['kind']=='directory' and not verified_tree:
        require(not any(source.iterdir()),'initial-directory-not-empty')
    if hasattr(files,'api'):
        from ..storage.windows import local_path
        a=files.api
        with a.ancestors(source),a.ancestors(destination):
            require(capture(files,source)==expected,'initial-node-changed')
            a.ok(a.MoveFileExW(local_path(source),local_path(destination),8))
        for parent in parents:files.sync_directory(parent)
    else:
        from .exclusive import rename
        left=os.open(source.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        right=os.open(destination.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:
            require(list((os.fstat(left).st_dev,os.fstat(left).st_ino))==parents[source.parent] and
                    list((os.fstat(right).st_dev,os.fstat(right).st_ino))==parents[destination.parent],'initial-parent-changed')
            require(capture(files,source)==expected,'initial-node-changed')
            rename(left,source.name,right,destination.name)
        finally:os.close(right);os.close(left)
    require(all(files.directory_identity(p)==v for p,v in parents.items()) and
            not present(source) and capture(files,destination)==expected,'initial-node-move-unconfirmed')

def remove_empty(files,path,expected):
    path=Path(path);require(expected['kind']=='directory' and capture(files,path)==expected,'initial-directory-changed')
    parent=files.directory_identity(path.parent)
    require(not any(path.iterdir()),'initial-directory-not-empty')
    if hasattr(files,'api'):
        from ..storage.windows import local_path
        with files.api.ancestors(path):
            require(capture(files,path)==expected,'initial-directory-changed')
            files.api.ok(files.api.RemoveDirectoryW(local_path(path)))
    else:
        fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:
            require([os.fstat(fd).st_dev,os.fstat(fd).st_ino]==parent and capture(files,path)==expected,'initial-directory-changed')
            os.rmdir(path.name,dir_fd=fd)
        finally:os.close(fd)
    files.sync_directory(path.parent)
    require(files.directory_identity(path.parent)==parent and not present(path),'initial-directory-removal-unconfirmed')
