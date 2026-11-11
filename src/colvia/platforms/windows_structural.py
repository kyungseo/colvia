"""Windows native identity proof for exact Git and registered worktree boundaries."""
from pathlib import Path
from ..codec import require
from ..tree import logical_path
from .windows_observation import Observer


def prove(topology,registrations,*,previous_containers=frozenset(),protected=frozenset(),observer=None):
    from .structural import StructuralProof
    observer=observer or Observer();root=Path(topology.root.path)
    require(topology.kind=='git','git-topology-required')
    require(observer.location(root)==topology.root,'workspace-location-changed')
    registered={(r.root,r.gitdir) for r in registrations};nested={}
    for member in topology.members:
        path=Path(member.root.path)
        if path==root or not path.is_relative_to(root):continue
        relative=path.relative_to(root).as_posix();require(logical_path(relative)==relative,'noncanonical-structural-path')
        require((member.root,member.gitdir) in registered,'nested-workspace-registration-required')
        require(observer.location(path)==member.root,'structural-boundary-changed')
        require(not any(p==relative or p.startswith(relative+'/') for p in protected),'boundary-swallows-protected')
        nested[relative]=(member.root.volume,member.root.file_id)
    require(not any(a!=b and b.startswith(a+'/') for a in nested for b in nested),'ambiguous-nested-workspace')
    containers=set();candidates={str(Path(p).parent) for p in nested}|set(previous_containers)
    for relative in sorted(candidates):
        if relative=='.':continue
        relative=Path(relative).as_posix();require(logical_path(relative)==relative,'invalid-structural-container')
        path=root/relative
        try:observer.location(path)
        except FileNotFoundError:continue
        with observer.opened(path) as (_,info):
            require(info['directory'],'structural-container-not-directory')
            names=observer.names(path,10000);valid=True
            for name in names:
                child=relative+'/'+name
                with observer.opened(path/name,opaque=True) as (_,item):
                    if child not in nested or not item['directory'] or item.get('symlink') or observer.identity(item)!=nested[child]:valid=False
            require(valid or relative not in previous_containers,'structural-container-changed')
            if valid and (names or relative in previous_containers):
                require(not any(p==relative or p.startswith(relative+'/') for p in protected),'boundary-swallows-protected');containers.add(relative)
            require(names==observer.names(path,len(names)),'structural-observation-changed')
    boundaries=dict(nested)
    for relative in containers:
        here=observer.location(root/relative);boundaries[relative]=(here.volume,here.file_id)
        for child in tuple(boundaries):
            if child.startswith(relative+'/'):del boundaries[child]
    with observer.opened(root/'.git') as (_,info):boundaries['.git']=observer.identity(info)
    require(observer.location(root)==topology.root,'workspace-location-changed')
    return StructuralProof(boundaries,frozenset(containers),frozenset(nested))
