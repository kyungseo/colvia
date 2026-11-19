"""No-follow reads of exact logical paths, independent of Git ignore policy."""
from contextlib import contextmanager
import base64,hashlib,os,stat
from ..codec import RecordError,require
from ..tree import logical_path
from .posix import open_directory,stamp


@contextmanager
def parent(root,path,*,verify_path=False):
    require(logical_path(path)==path,'invalid-scope-path')
    fd=open_directory(root)
    try:
        parts=path.split('/')
        for n,part in enumerate(parts):
            names={};aliases=set()
            with os.scandir(fd) as scan:
                for entry in scan:
                    require(len(names)<1_000_000,'observation-entry-limit')
                    canonical=logical_path(entry.name)
                    require(canonical.casefold() not in aliases,'path-collision')
                    names[canonical]=entry.name;aliases.add(canonical.casefold())
            if verify_path and n:
                require(aliases.isdisjoint({'.git', '.colvia-link.json'}), 'progress-nested-project')
            name=names.get(part)
            if name is None:
                yield None,None;return
            if n==len(parts)-1:
                yield fd,name;return
            try:child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            except OSError:raise RecordError('unsafe-scope-ancestor') from None
            os.close(fd);fd=child
    finally:os.close(fd)


def selected(root,paths,*,byte_limit,verify_path=False):
    result=[];used=0
    for path in sorted(paths):
        with parent(root,path,verify_path=verify_path) as (directory,name):
            if directory is None:
                if verify_path:
                    with parent(root,path,verify_path=True) as (again,_):
                        require(again is None, 'file-observation-changed')
                continue
            info=os.stat(name,dir_fd=directory,follow_symlinks=False);before=stamp(name,info)
            if stat.S_ISLNK(info.st_mode):
                raw=os.fsencode(os.readlink(name,dir_fd=directory))
                entry=dict(path=path,kind='symlink',mode='120000',target=base64.b64encode(raw).decode('ascii'))
            elif stat.S_ISREG(info.st_mode):
                require(used+info.st_size<=byte_limit,'observation-byte-limit')
                fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=directory)
                try:
                    require(stamp(name,os.fstat(fd))==before,'file-observation-changed')
                    digest=hashlib.sha256();size=0
                    while raw:=os.read(fd,1024*1024):
                        used+=len(raw);size+=len(raw);require(used<=byte_limit,'observation-byte-limit');digest.update(raw)
                    require(size==info.st_size and stamp(name,os.fstat(fd))==before,'file-observation-changed')
                    entry=dict(path=path,kind='regular',mode='100755' if info.st_mode&0o111 else '100644',size=size,sha256=digest.hexdigest())
                finally:os.close(fd)
            else:raise RecordError('scope-entry-not-regular')
            require(stamp(name,os.stat(name,dir_fd=directory,follow_symlinks=False))==before,'file-observation-changed')
            if verify_path:
                with parent(root,path,verify_path=True) as (again,leaf):
                    require(again is not None and os.path.samestat(os.fstat(directory),os.fstat(again))
                            and stamp(leaf,os.stat(leaf,dir_fd=again,follow_symlinks=False))==before,
                            'file-observation-changed')
            result.append(entry)
    return tuple(result)


def capture(root,path,expected,store,import_id):
    from ..bodies import ingest_body
    require(expected['kind']=='regular','opaque-edit-not-supported')
    with parent(root,path) as (directory,name):
        require(directory is not None,'body-observation-changed')
        info=os.stat(name,dir_fd=directory,follow_symlinks=False);before=stamp(name,info)
        require(stat.S_ISREG(info.st_mode) and ('100755' if info.st_mode&0o111 else '100644')==expected['mode'],'body-observation-changed')
        fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=directory)
        with os.fdopen(fd,'rb',closefd=True) as stream:
            require(stamp(name,os.fstat(stream.fileno()))==before,'body-observation-changed')
            result=ingest_body(stream,store,import_id,expected_size=expected['size'],expected_sha256=expected['sha256'])
            require(stamp(name,os.fstat(stream.fileno()))==before,'body-observation-changed')
        require(stamp(name,os.stat(name,dir_fd=directory,follow_symlinks=False))==before,'body-observation-changed')
        return result
