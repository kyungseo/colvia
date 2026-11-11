"""Pure connection identity decisions; filesystem/Git observations are adapter inputs.

A locator is not authority. Resolution neither creates records nor changes host
permissions. New linked workspaces remain unregistered until an authorized writer
publishes their identity under the authority's expected generation/root.
"""
from __future__ import annotations
from dataclasses import dataclass
import uuid

from .codec import decode_canonical, require

LOCATOR_LIMIT = 16 * 1024


def _uuid(value):
    require(type(value) is str, 'invalid-identity')
    try: parsed=uuid.UUID(value)
    except (ValueError,AttributeError):
        require(False,'invalid-identity')
    require(str(parsed)==value,'noncanonical-identity')


def _nonce(value):
    require(type(value) is str and len(value)==64 and all(c in '0123456789abcdef' for c in value),
            'invalid-binding-nonce')


@dataclass(frozen=True)
class NativeLocation:
    path: str
    volume: str
    file_id: str

    def __post_init__(self):
        for text,limit in ((self.path,32768),(self.volume,256),(self.file_id,256)):
            require(type(text) is str and 0<len(text)<=limit and '\x00' not in text,'invalid-native-identity')


_ASCII_CASE = str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')


def same_plain_path(left: str, right: str) -> bool:
    """Compare local drive-path ASCII spelling; no filesystem alias resolution."""
    if left==right:return True
    def drive(path):
        return len(path)>=3 and path[0] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' and path[1:3]==':\\'
    return drive(left) and drive(right) and left.translate(_ASCII_CASE)==right.translate(_ASCII_CASE)


def same_plain_location(left: NativeLocation, right: NativeLocation) -> bool:
    """Compare plain locations without changing persisted location/index bytes.

    Local Windows drive paths may vary in ASCII case only; native volume and
    file identity (including creation identity) remain exact. Git identity,
    POSIX paths, Unicode, separators and aliases retain their existing rules.
    Callers obtain identities through the no-reparse observer. Case-sensitive
    Windows directory trees are not qualified by this spelling-only comparison.
    """
    if left==right:return True
    if type(left) is not NativeLocation or type(right) is not NativeLocation:return False
    return (left.volume==right.volume and left.file_id==right.file_id and
            same_plain_path(left.path,right.path))


@dataclass(frozen=True)
class Membership:
    root: NativeLocation
    gitdir: NativeLocation


@dataclass(frozen=True)
class Topology:
    kind: str
    root: NativeLocation
    common: NativeLocation | None = None
    gitdir: NativeLocation | None = None
    members: tuple[Membership,...] = ()

    def __post_init__(self):
        require(self.kind in ('git','plain') and type(self.root) is NativeLocation,'invalid-topology')
        require(type(self.members) is tuple and all(type(m) is Membership for m in self.members),'invalid-membership')
        if self.kind=='plain':
            require(self.common is None and self.gitdir is None and not self.members,'invalid-plain-topology')
        else:
            require(type(self.common) is NativeLocation and type(self.gitdir) is NativeLocation,'git-topology-unavailable')
            require(len(self.members)<=10000 and len({m.root for m in self.members})==len(self.members),
                    'ambiguous-membership')
            require(sum(m.root==self.root and m.gitdir==self.gitdir for m in self.members)==1,
                    'workspace-not-in-git-membership')


@dataclass(frozen=True)
class Locator:
    project: str
    instance: str
    epoch: int
    nonce: str
    workspace: str | None = None

    def __post_init__(self):
        _uuid(self.project); _uuid(self.instance); _nonce(self.nonce)
        require(type(self.epoch) is int and self.epoch>=1,'invalid-binding-epoch')
        if self.workspace is not None: _uuid(self.workspace)

    @classmethod
    def parse(cls, raw:bytes, *, kind:str):
        require(type(raw) is bytes and len(raw)<=LOCATOR_LIMIT,'locator-size-limit')
        require(kind in ('git','plain'),'invalid-topology')
        value=decode_canonical(raw)
        keys={'locator_version','project_uuid','authority_instance_uuid','binding_epoch','binding_nonce'}
        if kind=='plain': keys.add('workspace_uuid')
        require(type(value) is dict and set(value)==keys and
                type(value['locator_version']) is int and value['locator_version']==1,'invalid-locator')
        return cls(value['project_uuid'],value['authority_instance_uuid'],value['binding_epoch'],
                   value['binding_nonce'],value.get('workspace_uuid'))

    def payload(self):
        value=dict(locator_version=1,project_uuid=self.project,authority_instance_uuid=self.instance,
                   binding_epoch=self.epoch,binding_nonce=self.nonce)
        if self.workspace is not None:value['workspace_uuid']=self.workspace
        return value


@dataclass(frozen=True)
class ProjectBinding:
    locator: Locator
    kind: str
    location: NativeLocation
    # A Git project binding has no one shared workspace ID.
    def __post_init__(self):
        require(self.kind in ('git','plain') and type(self.location) is NativeLocation,'invalid-project-binding')
        require((self.locator.workspace is None)==(self.kind=='git'),'locator-workspace-shape')


@dataclass(frozen=True)
class WorkspaceRegistration:
    workspace: str
    root: NativeLocation
    gitdir: NativeLocation | None

    def __post_init__(self):
        _uuid(self.workspace)
        require(type(self.root) is NativeLocation and (self.gitdir is None or type(self.gitdir) is NativeLocation),
                'invalid-workspace-registration')


@dataclass(frozen=True)
class Resolution:
    project: str
    workspace: str | None
    registration_required: bool
    observation: Topology


def resolve(locator: Locator, binding: ProjectBinding, observed: Topology,
            registrations: tuple[WorkspaceRegistration,...]) -> Resolution:
    require(type(registrations) is tuple and all(type(w) is WorkspaceRegistration for w in registrations),
            'invalid-workspace-registrations')
    require(len({w.workspace for w in registrations})==len(registrations) and
            len({w.root for w in registrations})==len(registrations),'ambiguous-workspace-registration')
    require(locator==binding.locator,'stale-or-foreign-binding')
    require(observed.kind==binding.kind,'project-topology-changed')
    identity=observed.common if observed.kind=='git' else observed.root
    same=same_plain_location if observed.kind=='plain' else lambda left,right:left==right
    require(same(identity,binding.location),'project-location-changed')
    matches=[w for w in registrations if same(w.root,observed.root)]
    require(len(matches)<=1,'ambiguous-workspace-registration')
    if not matches:
        require(observed.kind=='git','workspace-identity-unavailable')
        # Membership and common-dir identity already prove same project. A read
        # may show that registration is needed; it cannot claim another workspace.
        return Resolution(locator.project,None,True,observed)
    workspace=matches[0]
    require(workspace.gitdir==observed.gitdir,'workspace-location-changed')
    if observed.kind=='plain':
        require(locator.workspace==workspace.workspace,'workspace-binding-mismatch')
    return Resolution(locator.project,workspace.workspace,False,observed)


def require_registered(resolution: Resolution) -> str:
    require(not resolution.registration_required and resolution.workspace is not None,'workspace-registration-required')
    return resolution.workspace


def require_connection_root(selected: NativeLocation, observed: Topology) -> None:
    require(selected==observed.root,'connect-workspace-root-required')
