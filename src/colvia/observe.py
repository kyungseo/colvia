"""Application observation port for plain/Git workspaces.

Observations do not connect projects, register workspaces, advance a Work baseline
or write Git. Callers supply the authority's verified workspace registrations.
"""
from dataclasses import dataclass,replace
from pathlib import Path
import stat

from .adapters.git import discover
from .adapters.opaque_git import inspect_gitlink,placeholders
from .binding import WorkspaceRegistration
from .codec import require
from .observation import Policy,policy_transition
from .platforms.posix import ObservationBudget,Snapshot
from .platforms.observation_port import snapshot
from .platforms.structural import StructuralProof,prove
from .tree import logical_path


@dataclass(frozen=True)
class Observation:
    topology:object
    snapshot:Snapshot
    policy:Policy
    structural:StructuralProof
    opaque:tuple = ()


def observe(root:Path,budget:ObservationBudget,*,git=None,registrations:tuple[WorkspaceRegistration,...]=(),
            protected=frozenset(),previous_containers=frozenset(),previous_policy=None,
            approved_policy_paths=frozenset(),cancelled=lambda:False):
    topology=discover(root,git)
    actual_root=Path(topology.root.path)
    opaque={};opaque_state={};opaque_bytes=0
    if topology.kind=='plain':
        proof=StructuralProof({},frozenset(),frozenset())
        policy=Policy((),(),'plain-observation-v1')
        result=snapshot(actual_root,budget,protected=protected,cancelled=cancelled,reject_nested_git=True)
        require(discover(root,git)==topology,'project-topology-changed')
    else:
        proof=prove(topology,registrations,previous_containers=previous_containers,protected=protected)
        index=git.index(actual_root)
        for indexed in index.values():
            if indexed.mode=='160000':
                opaque[indexed.native_path],opaque_state[indexed.path],used=inspect_gitlink(
                    git,actual_root,indexed,ObservationBudget(budget.entries,budget.read_bytes-opaque_bytes))
                opaque_bytes+=used
        inventory=snapshot(actual_root,ObservationBudget(budget.entries,0),admit=lambda _:False,
            boundaries=proof.boundaries,cancelled=cancelled,reject_nested_git=True,opaque_entries=opaque)
        native=[s.native_path for s in inventory.inventory if not stat.S_ISDIR(s.mode)]
        policy=git.policy(topology,inventory.inventory)
        ignored=git.ignored(actual_root,native)
        admitted={logical_path(p) for p in native}-ignored|set(index)|set(protected)
        result=snapshot(actual_root,ObservationBudget(budget.entries,budget.read_bytes-opaque_bytes),admit=lambda p:p in admitted,protected=protected,
                        boundaries=proof.boundaries,cancelled=cancelled,reject_nested_git=True,opaque_entries=opaque,
                        modes={p:e.mode for p,e in index.items() if e.mode in ('100644','100755')})
        require(inventory.inventory==result.inventory,'observation-inventory-changed')
        result=placeholders(git,actual_root,index,result)
        for indexed in index.values():
            if indexed.mode=='160000':
                proof_now,state_now,used=inspect_gitlink(git,actual_root,indexed,
                    ObservationBudget(budget.entries,budget.read_bytes-opaque_bytes-result.bytes_read))
                opaque_bytes+=used
                require(proof_now==opaque[indexed.native_path] and state_now==opaque_state[indexed.path],'gitlink-observation-changed')
        result=replace(result,bytes_read=result.bytes_read+opaque_bytes)
        require(git.policy(topology,result.inventory)==policy,'observation-policy-changed')
        require(git.index(actual_root)==index and git.topology(actual_root)==topology,'git-observation-changed')
        again=prove(topology,registrations,previous_containers=previous_containers,protected=protected)
        require(again==proof,'structural-observation-changed')
    if previous_policy is not None:
        policy_transition(previous_policy,policy,verified_structural=proof.containers|proof.nested,
                          protected=frozenset(protected),approved_policy_paths=approved_policy_paths)
    return Observation(topology,result,policy,proof,tuple(sorted(opaque_state.items())))
