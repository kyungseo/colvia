"""Concrete workspace port; domain Work services receive this as an interface."""
from contextlib import contextmanager
from pathlib import Path
import sys
from .binding import resolve,require_registered,same_plain_location,revalidates,creation_identity_changed
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
        from .connection_identity import PROJECT_IDENTITY
        self.store.pin_workspace_location(PROJECT_IDENTITY, self.store.head(PROJECT_IDENTITY))
        reference,registration,bound=self.connections.workspace(self.workspace)
        from .connection_boundary import workspace_topology
        topology=workspace_topology(self.root,self.git)
        current=topology.common if topology.kind=='git' else topology.root
        locator=self.locator_reader()
        if locator==bound.locator and topology.kind==bound.kind and revalidates(bound.location,current):
            from .connection_boundary import ConnectionBoundaryError
            raise ConnectionBoundaryError('connection-identity-review-required',topology.root.path)
        if locator==bound.locator and topology.kind==bound.kind and any(
                creation_identity_changed(old,new) for old,new in (
                    (bound.location,current),(registration.root,topology.root),(registration.gitdir,topology.gitdir))):
            from .connection_boundary import ConnectionBoundaryError
            raise ConnectionBoundaryError('connection-creation-identity-changed',topology.root.path)
        registrations=self.connections.registrations(topology)
        resolved=resolve(locator,bound,topology,registrations)
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

    @contextmanager
    def selected_reader(self, *, verify_path=False):
        _, topology, _ = self.verify()
        root = Path(topology.root.path)
        windows_git = sys.platform == 'win32' and self.git and topology.kind == 'git'
        index = self.git.index(root) if windows_git else {}
        modes = {p: e.mode for p, e in index.items() if e.mode in ('100644', '100755')}

        def read(paths, byte_limit):
            entries = selected(root, paths, byte_limit=byte_limit, modes=modes, verify_path=verify_path)
            if index:
                from .platforms.posix import Snapshot
                from .adapters.opaque_git import placeholders
                entries = placeholders(self.git, root, index, Snapshot(topology.root, entries, (), 0)).entries
            return entries

        yield read
        require(location(root) == topology.root, 'workspace-location-changed')
        if verify_path and windows_git:
            require(self.git.index(root) == index, 'git-observation-changed')
        self.verify()

    def selected(self, paths):
        with self.selected_reader() as read:
            return read(paths, self.budget.read_bytes)
