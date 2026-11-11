"""Protect initialized/uninitialized gitlinks without following or editing them.

No Git status/diff/filter commands are used. Compare raw worktree blob identities
with index and HEAD, and freeze submodule policy separately from its commit OID.
"""
from dataclasses import replace
from pathlib import Path
import base64,hashlib,os,stat

from ..codec import require
from ..platforms.posix import ObservationBudget
from ..platforms.observation_port import location,snapshot,entry_identity
from ..tree import canonical_entries
from .git import _text,read_file


def placeholders(git,root,index,result):
    entries={e['path']:e for e in result.entries}
    stamps={s.native_path:s for s in result.stamps}
    for path,indexed in index.items():
        entry=entries.get(path)
        if indexed.mode!='120000' or entry is None or entry['kind']!='regular':continue
        enabled=git._run(root,('config','--bool','--get','core.symlinks'),allowed=(0,1),limit=128)
        require(enabled.code==0 and enabled.stdout.strip()==b'false','opaque-entry-type-changed')
        raw=read_file(root/indexed.native_path,16384)
        require(hashlib.sha256(raw).hexdigest()==entry['sha256'] and len(raw)==entry['size'],'opaque-entry-changed')
        entries[path]=dict(path=path,kind='symlink',mode='120000',target=base64.b64encode(raw).decode('ascii'))
    return replace(result,entries=tuple(canonical_entries(entries.values())))


def inspect_gitlink(git,parent,indexed,budget):
    path=parent/indexed.native_path
    here=location(path);directory_id=(here.volume,here.file_id)
    entry=dict(path=indexed.path,kind='gitlink',mode='160000',algorithm='sha1' if len(indexed.oid)==40 else 'sha256',oid=indexed.oid)
    marker=path/'.git'
    if not os.path.lexists(marker):
        require(not any(path.iterdir()),'uninitialized-gitlink-not-empty')
        require(location(path)==here,'opaque-entry-changed')
        return (directory_id,entry),('uninitialized',),0
    info=marker.lstat()
    require(not stat.S_ISLNK(info.st_mode),'unsafe-git-marker')
    root=git._run(path,('rev-parse','--path-format=absolute','--show-toplevel'),limit=32768).stdout.rstrip(b'\n')
    require(Path(_text(root))==path,'foreign-gitlink-root')
    head=git._run(path,('rev-parse','--verify','HEAD'),limit=256).stdout.strip().decode('ascii')
    require(head==indexed.oid,'gitlink-head-changed')
    index=git.index(path)
    require(not any(e.mode=='160000' for e in index.values()),'nested-gitlink-not-supported')
    tree=git._run(path,('ls-tree','-r','-z','--full-tree','HEAD')).stdout
    expected={}
    for record in tree.split(b'\0'):
        if not record:continue
        parts=record.split(b'\t',1);require(len(parts)==2,'invalid-git-tree')
        header=parts[0].split(b' ');require(len(header)==3,'invalid-git-tree')
        mode,kind,oid=header
        require(kind==b'blob','nested-gitlink-not-supported')
        expected[_text(parts[1])]=(_text(mode),_text(oid))
    require(expected=={e.native_path:(e.mode,e.oid) for e in index.values()},'gitlink-staged-change')
    boundaries={'.git':entry_identity(marker)}
    inventory=snapshot(path,ObservationBudget(budget.entries,0),admit=lambda _:False,boundaries=boundaries,reject_nested_git=True)
    # The policy helper needs only root.path; no top-level membership claim is made.
    from types import SimpleNamespace
    topology=SimpleNamespace(root=here)
    policy=git.policy(topology,inventory.inventory)
    names=[s.native_path for s in inventory.inventory if not stat.S_ISDIR(s.mode)]
    ignored=git.ignored(path,names)
    from ..tree import logical_path
    admitted={logical_path(p) for p in names}-ignored|set(index)
    result=snapshot(path,budget,admit=lambda p:p in admitted,boundaries=boundaries,reject_nested_git=True,
                    git_algorithm=entry['algorithm'],modes={p:e.mode for p,e in index.items() if e.mode in ('100644','100755')})
    require(inventory.inventory==result.inventory,'gitlink-observation-changed')
    result=placeholders(git,path,index,result)
    actual={e['path']:e for e in result.entries};blobs=dict(result.git_blobs)
    require(set(actual)==set(index),'gitlink-untracked-or-missing')
    for key,item in index.items():
        require(actual[key]['mode']==item.mode and blobs.get(key)==item.oid,'gitlink-content-changed')
    require(git.policy(topology,result.inventory)==policy and git.index(path)==index and
            git._run(path,('rev-parse','--verify','HEAD'),limit=256).stdout.strip().decode('ascii')==head and
            location(path)==here,'gitlink-observation-changed')
    return (directory_id,entry),('initialized',head,policy.digest),result.bytes_read
