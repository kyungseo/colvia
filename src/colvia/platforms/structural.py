"""Fresh POSIX proof of Git metadata and registered nested-workspace boundaries."""
from dataclasses import dataclass
from pathlib import Path
import os,stat,sys

from ..binding import Topology,WorkspaceRegistration
from ..codec import RecordError,require
from ..tree import logical_path
from .posix import descriptor_location,directory_location,identity,location,open_directory,stamp


@dataclass(frozen=True)
class StructuralProof:
    boundaries: dict
    containers: frozenset[str]
    nested: frozenset[str]


def prove(topology:Topology,registrations:tuple[WorkspaceRegistration,...],*,previous_containers=frozenset(),protected=frozenset()):
    if sys.platform=='win32':
        from .windows_structural import prove as native
        return native(topology,registrations,previous_containers=previous_containers,protected=protected)
    require(topology.kind=='git','git-topology-required')
    root=Path(topology.root.path)
    require(location(root)==topology.root,'workspace-location-changed')
    registered={(r.root,r.gitdir) for r in registrations}
    nested={}
    for member in topology.members:
        path=Path(member.root.path)
        if path==root or not path.is_relative_to(root):continue
        relative=path.relative_to(root).as_posix()
        require(logical_path(relative)==relative,'noncanonical-structural-path')
        require((member.root,member.gitdir) in registered,'nested-workspace-registration-required')
        current,live=directory_location(path)
        require(current==member.root,'structural-boundary-changed')
        require(not any(p==relative or p.startswith(relative+'/') for p in protected),'boundary-swallows-protected')
        nested[relative]=live
    # Nested workspaces cannot contain one another in a single outer observation.
    require(not any(a!=b and b.startswith(a+'/') for a in nested for b in nested),'ambiguous-nested-workspace')
    containers={}
    candidates={str(Path(p).parent) for p in nested}|set(previous_containers)
    for relative in sorted(candidates):
        if relative=='.':continue  # Never classify the whole project as a container.
        require(logical_path(relative)==relative,'invalid-structural-container')
        path=root/relative
        try:fd=open_directory(path)
        except FileNotFoundError:
            # An absent former container has no current effect; no reusable proof.
            continue
        try:
            before=os.fstat(fd);children=[]
            with os.scandir(fd) as scan:
                for item in scan:
                    require(len(children)<10000,'structural-entry-limit')
                    children.append(item.name)
            valid=True
            for name in children:
                child=relative+'/'+name
                info=os.stat(name,dir_fd=fd,follow_symlinks=False)
                if child not in nested or not stat.S_ISDIR(info.st_mode) or identity(info)!=nested[child]:
                    valid=False;break
            # A regular sibling does not invalidate individual workspace roots;
            # it only prevents the parent-directory exception.
            require(valid or relative not in previous_containers,'structural-container-changed')
            if valid and (children or relative in previous_containers):
                require(not any(p==relative or p.startswith(relative+'/') for p in protected),'boundary-swallows-protected')
                containers[relative]=descriptor_location(path,fd)
            with os.scandir(fd) as scan:after=sorted(i.name for i in scan)
            require(sorted(children)==after and stamp('',before)==stamp('',os.fstat(fd)),'structural-observation-changed')
        finally:os.close(fd)
    boundaries=dict(nested)
    for relative,observed in containers.items():
        require(directory_location(root/relative)==observed,'structural-boundary-changed')
        boundaries[relative]=observed[1]
        for child in tuple(boundaries):
            if child.startswith(relative+'/'):del boundaries[child]
    marker=root/'.git';info=marker.lstat()
    require(not stat.S_ISLNK(info.st_mode) and (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)),
            'unsafe-git-marker')
    boundaries['.git']=identity(info)
    return StructuralProof(boundaries,frozenset(containers),frozenset(nested))
