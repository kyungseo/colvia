"""Concrete workspace port; domain Work services receive this as an interface."""
from pathlib import Path
import sys
from .adapters.git import discover
from .binding import resolve,require_registered,same_plain_location
from .bodies import submission_size
from .codec import require
from .connection import Connections
from .maps import build_map
from .observe import observe
from .platforms.posix import ObservationBudget
from .platforms.observation_port import location,selected,capture


class LocalWorkspace:
    def __init__(self,store,root:Path,workspace:str,*,locator_reader,git=None,budget=None):
        self.store=store;self.root=Path(root);self.workspace=workspace
        self.locator_reader=locator_reader;self.git=git
        self.budget=budget or ObservationBudget(100000,2*1024*1024*1024)
        self.connections=Connections(store)

    def verify(self):
        reference,registration,bound=self.connections.workspace(self.workspace)
        topology=discover(self.root,self.git)
        registrations=self.connections.registrations(topology)
        resolved=resolve(self.locator_reader(),bound,topology,registrations)
        require(require_registered(resolved)==self.workspace,'wrong-workspace')
        require(same_plain_location(topology.root,registration.root) if topology.kind=='plain' else
                topology.root==registration.root,'workspace-location-changed')
        return reference,topology,registrations

    def observe(self,**options):
        reference,topology,registrations=self.verify()
        result=observe(self.root,self.budget,git=self.git,registrations=registrations,**options)
        require(result.topology==topology,'workspace-observation-changed')
        self.verify()
        return reference,result

    def capture(self,paths,observed,import_id):
        self.verify()
        entries={e['path']:e for e in observed.snapshot.entries}
        objects=[];bodies={};sizes=[]
        for path in sorted(paths):
            if path not in entries:continue
            entry=entries[path];require(entry['kind']=='regular','opaque-edit-not-supported')
            sizes.append(entry['size']);submission_size(sizes)
            ref,raw=capture(Path(observed.topology.root.path),path,entry,self.store,import_id)
            bodies[path]=ref;objects.append((ref,raw))
        mapping=build_map(bodies.items());objects.extend(mapping.objects)
        require(self.selected(paths)==tuple(e for e in observed.snapshot.entries if e['path'] in paths),'body-observation-changed')
        return mapping.root,objects,sum(sizes)

    def selected(self,paths):
        _,topology,_=self.verify()
        index=self.git.index(Path(topology.root.path)) if sys.platform=='win32' and self.git and topology.kind=='git' else {}
        result=selected(Path(topology.root.path),paths,byte_limit=self.budget.read_bytes,
                        modes={p:e.mode for p,e in index.items() if e.mode in ('100644','100755')})
        if index:
            from .platforms.posix import Snapshot
            from .adapters.opaque_git import placeholders
            result=placeholders(self.git,Path(topology.root.path),index,Snapshot(topology.root,result,(),0)).entries

        require(location(Path(topology.root.path))==topology.root,'workspace-location-changed')
        self.verify()
        return result
