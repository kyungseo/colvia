"""Bounded no-follow runtime inventories; expected content comes from qualification.

Cold verification hashes bytes. Hot verification compares every path and stat
identity captured by the cold check. Neither check isolates hostile same-user
writes after observation; the trusted owner holds the installed runtime lease.
"""
import hashlib,os,stat
from ..codec import require
from .darwin_runtime_policy import canonical_existing

MAX_ENTRIES=32768
MAX_BYTES=2*1024*1024*1024
MAX_DEPTH=32

def signature(info):
    return (info.st_dev,info.st_ino,info.st_uid,info.st_mode,info.st_nlink,
            info.st_size,info.st_mtime_ns,info.st_ctime_ns)

def inventory(root,*,content):
    root=canonical_existing(str(root),True);rows=[];identities={};total=0;pending=[(root,'',0)]
    while pending:
        directory,prefix,depth=pending.pop()
        require(depth<=MAX_DEPTH,'execution-runtime-tree-depth')
        before=directory.lstat();require(stat.S_ISDIR(before.st_mode),'execution-runtime-tree-kind')
        identities[prefix]=signature(before)
        with os.scandir(directory) as scan:
            names=[]
            for item in scan:
                require(len(rows)+len(pending)+len(names)<MAX_ENTRIES,'execution-runtime-tree-count')
                names.append(item.name)
        for name in sorted(names):
            path=directory/name;relative=prefix+'/'+name if prefix else name;info=path.lstat()
            require(not any(c in relative for c in ('\x00','\n','\r')),'execution-runtime-tree-path')
            mode=stat.S_IMODE(info.st_mode)
            if stat.S_ISDIR(info.st_mode):
                rows.append(dict(path=relative,kind='directory',mode=mode));pending.append((path,relative,depth+1))
            else:
                require(stat.S_ISREG(info.st_mode) and info.st_nlink==1,'execution-runtime-tree-kind')
                total+=info.st_size;require(total<=MAX_BYTES,'execution-runtime-tree-bytes')
                row=dict(path=relative,kind='file',mode=mode,size=info.st_size)
                if content:
                    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
                    try:
                        require(signature(os.fstat(fd))==signature(info),'execution-runtime-tree-drift')
                        digest=hashlib.sha256();size=0
                        while raw:=os.read(fd,1024*1024):
                            size+=len(raw);require(size<=info.st_size,'execution-runtime-tree-drift');digest.update(raw)
                        require(size==info.st_size and signature(os.fstat(fd))==signature(info),'execution-runtime-tree-drift')
                        row['sha256']=digest.hexdigest()
                    finally:os.close(fd)
                require(signature(path.lstat())==signature(info),'execution-runtime-tree-drift')
                identities[relative]=signature(info);rows.append(row)
        require(signature(directory.lstat())==signature(before),'execution-runtime-tree-drift')
    return sorted(rows,key=lambda row:row['path']),identities


def ancestor_instructions(directory):
    for parent in (directory,*directory.parents):
        require(not any(os.path.lexists(parent/name) for name in ('.git','AGENTS.md','AGENTS.override.md')),
                'execution-runtime-ancestor-instructions')


def session_directories(session,previous=None):
    directories={name:canonical_existing(str(session/name),True) for name in ('cwd','tmp','log','sqlite')}
    require(all(path==session/name and stat.S_ISDIR((session/name).lstat().st_mode) for name,path in directories.items()),'execution-runtime-session-alias')
    identities={}
    for name,path in {'session':session,**directories}.items():
        info=path.lstat();require(info.st_uid==os.getuid() and stat.S_IMODE(info.st_mode)&0o077==0,
                                'execution-runtime-session-private')
        identities[name]=(info.st_dev,info.st_ino,info.st_uid,info.st_mode)
    ancestor_instructions(directories['cwd'])
    if previous is None:
        require(set(os.listdir(session))==set(directories),'execution-runtime-session-shape')
        require(all(not os.listdir(path) for path in directories.values()),'execution-runtime-session-not-empty')
    else:require(identities==previous,'execution-runtime-session-replaced')
    return directories,identities
