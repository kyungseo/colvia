"""Pure worker byte-state decisions; no filesystem or authority effects.

An observation is not an acceptance, and a progress marker is not evidence of
current bytes. External-effect recovery adds evacuation identity evidence in the
writer port; an absent path here never means that evacuation was successful.
"""
from dataclasses import dataclass
from .codec import require
from .observation import verify_scope, changed_paths
from .tree import canonical_entries, logical_path


def path_namespace(paths):
    """Reject component aliases and file/ancestor collisions across both images."""
    exact=set(); prefixes={}
    for path in paths:
        require(type(path) is str and logical_path(path)==path,'invalid-worker-path')
        exact.add(path)
        parts=path.split('/')
        for end in range(1,len(parts)+1):
            prefix='/'.join(parts[:end]);alias=prefix.casefold()
            require(alias not in prefixes or prefixes[alias]==prefix,'worker-path-alias')
            prefixes[alias]=prefix
    for path in exact:
        parts=path.split('/')
        require(not any('/'.join(parts[:end]) in exact for end in range(1,len(parts))),
                'worker-path-type-conversion')


@dataclass(frozen=True)
class ContentState:
    paths: tuple[tuple[str,str],...]
    outside: tuple[str,...]

    @property
    def all_pre(self):return not self.outside and all(state=='pre' for _,state in self.paths)
    @property
    def all_post(self):return not self.outside and all(state=='post' for _,state in self.paths)
    @property
    def resumable(self):return not self.outside and all(state in ('pre','post') for _,state in self.paths)


def transitions(before,after,scope):
    before=canonical_entries(before);after=canonical_entries(after)
    scope=list(scope)
    require(scope and len(scope)==len(set(scope)),'invalid-worker-scope')
    path_namespace([e['path'] for e in before]+[e['path'] for e in after]+scope)
    changed=verify_scope(before,after,frozenset(scope))
    first={e['path']:e for e in before};second={e['path']:e for e in after}
    return tuple({'path':path,'pre':first.get(path),'post':second.get(path)} for path in changed)


def classify(before,after,current,scope):
    """Use full content trees. Neither unknown bytes nor outside drift can pass."""
    before=canonical_entries(before);after=canonical_entries(after);current=canonical_entries(current)
    changes=transitions(before,after,scope)
    observed={e['path']:e for e in current}
    changed={item['path'] for item in changes}
    outside=tuple(path for path in changed_paths(before,current) if path not in changed)
    states=[]
    for item in changes:
        entry=observed.get(item['path'])
        states.append((item['path'],'pre' if entry==item['pre'] else 'post' if entry==item['post'] else 'unknown'))
    return ContentState(tuple(states),outside)


def require_initial(before,after,current,scope):
    state=classify(before,after,current,scope)
    require(state.all_pre,'worker-destination-baseline-changed')
    return state
