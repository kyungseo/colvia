"""Pure observation policy and scope decisions; display never grants write scope."""
from dataclasses import dataclass, replace
from pathlib import PurePosixPath, PureWindowsPath
import hashlib

from .codec import canonical_bytes, require
from .tree import canonical_entries, logical_path


@dataclass(frozen=True)
class PolicySource:
    origin: str
    raw: bytes

    def __post_init__(self):
        require(type(self.origin) is str and 0<len(self.origin)<=32768 and '\x00' not in self.origin,
                'invalid-policy-origin')
        require(type(self.raw) is bytes and len(self.raw)<=4*1024*1024,'policy-source-limit')

    @property
    def digest(self): return hashlib.sha256(self.raw).hexdigest()

    def occurrences(self):
        # Repeated lines keep distinct occurrence indices. No normalization of
        # escapes, CRLF, trailing spaces, comments or source order is permitted.
        return tuple((self.origin,self.digest,n,line) for n,line in enumerate(self.raw.splitlines(keepends=True)))


@dataclass(frozen=True)
class Policy:
    sources: tuple[PolicySource,...]
    config: tuple[tuple[str,str],...]
    tool: str

    def __post_init__(self):
        require(type(self.sources) is tuple and len(self.sources)<=100000 and
                all(type(s) is PolicySource for s in self.sources),'invalid-policy-sources')
        require(len({s.origin for s in self.sources})==len(self.sources),'duplicate-policy-origin')
        require(sum(len(s.raw) for s in self.sources)<=64*1024*1024,'policy-total-limit')
        require(type(self.config) is tuple and all(type(p) is tuple and len(p)==2 and
                all(type(v) is str for v in p) for p in self.config),'invalid-policy-config')
        require(type(self.tool) is str and 0<len(self.tool)<=1024,'invalid-policy-tool')

    @property
    def digest(self):
        return hashlib.sha256(canonical_bytes(dict(
            sources=[dict(origin=s.origin,sha256=s.digest,size=len(s.raw)) for s in self.sources],
            config=[list(p) for p in self.config],tool=self.tool))).hexdigest()


def relocated_policy(policy, before, after):
    # Called after checking the registration's sealed location evidence.
    # Translate only the repository's own config origin. Values, order,
    # global exclusions and other origins keep their exact comparisons.
    if before is None or after is None or before['path'] == after['path']:
        return policy
    cls = PurePosixPath if before['path'].startswith('/') else PureWindowsPath
    old = 'file:' + str(cls(before['path']) / 'config') + ' '
    new = 'file:' + str(cls(after['path']) / 'config') + ' '
    return replace(policy, config=tuple((new+k[len(old):] if k.startswith(old) else k, v)
                                        for k, v in policy.config))


def literal_root_directory(raw:bytes) -> str:
    """Only Git's literal root-relative directory syntax, never a guessed glob."""
    require(raw.endswith(b'\n') and not raw.endswith(b'\r\n'),'policy-change-not-equivalent')
    line=raw[:-1]
    require(line.endswith(b'/') and not any(c in line for c in b'!*?[]\\\r\x00') and
            not line.startswith(b'#') and line.strip()==line,'policy-change-not-equivalent')
    anchored=line.startswith(b'/')
    path=line[1:-1] if anchored else line[:-1]
    # An unanchored one-component pattern matches at every depth in Git.
    require(anchored or b'/' in path,'policy-change-not-equivalent')
    try: text=path.decode('utf-8')
    except UnicodeError: require(False,'policy-change-not-equivalent')
    require(logical_path(text)==text,'policy-change-not-equivalent')
    return text


def policy_transition(previous:Policy,current:Policy,*,verified_structural:frozenset[str],
                      protected:frozenset[str],info_origin='git:info/exclude',
                      approved_policy_paths=frozenset()) -> str:
    """A policy-edit plan permits union observation, not hiding old membership.

    The application must observe all `protected` paths even if now ignored and
    compare the resulting union. This function never updates an active baseline.
    Structural proof is fresh for this observation even when digests are equal.
    """
    require(previous.tool==current.tool and previous.config==current.config,'observation-context-changed')
    before={s.origin:s for s in previous.sources};after={s.origin:s for s in current.sources}
    common=set(before)&set(after)
    require(tuple(k for k in before if k in common)==tuple(k for k in after if k in common),'policy-origin-order-changed')
    changed=[key for key in dict.fromkeys((*before,*after)) if before.get(key)!=after.get(key)]
    if set(before)!=set(after):
        require(all(key.startswith('workspace:') and key[len('workspace:'):] in approved_policy_paths for key in changed),
                'policy-origin-order-changed')
    if not changed:return 'same'
    if all(key.startswith('workspace:') and key[len('workspace:'):] in approved_policy_paths for key in changed):
        return 'approved-policy-edit-union-required'
    require(changed==[info_origin],'policy-change-not-equivalent')
    old,new=before[info_origin].raw,after[info_origin].raw
    require(not old or old.endswith(b'\n'),'policy-change-not-equivalent')
    require(new.startswith(old) and len(new)>len(old),'policy-change-not-equivalent')
    lines=new[len(old):].splitlines(keepends=True)
    require(lines and len(lines)<=10000,'policy-change-not-equivalent')
    for line in lines:
        path=literal_root_directory(line)
        require(path in verified_structural,'structural-proof-required')
        require(not any(p==path or p.startswith(path+'/') for p in protected),'boundary-swallows-protected')
    return 'equivalent-structural-append'


def changed_paths(before,after) -> tuple[str,...]:
    first={e['path']:e for e in canonical_entries(before)}
    second={e['path']:e for e in canonical_entries(after)}
    return tuple(sorted(p for p in first.keys()|second.keys() if first.get(p)!=second.get(p)))


def verify_scope(before,after,approved:frozenset[str]) -> tuple[str,...]:
    for path in approved: require(logical_path(path)==path,'invalid-scope-path')
    first={e['path']:e for e in canonical_entries(before)}
    second={e['path']:e for e in canonical_entries(after)}
    changed=changed_paths(before,after)
    require(set(changed)<=approved,'outside-scope-change')
    opaque={p for p,e in (*first.items(),*second.items()) if e['kind']!='regular'}
    require(not any(p==q or p.startswith(q+'/') or q.startswith(p+'/') for p in approved for q in opaque),
            'opaque-edit-not-supported')
    return changed
