"""Bounded overlap checks for independent manager connect and rebind."""
from contextlib import closing
from pathlib import Path

from .adapters.git import discover
from .binding import Locator, same_plain_path
from .codec import RecordError, canonical_bytes, decode_envelope, require
from .connection import Connections, PROJECT_KEY, location_key, workspace_key, workspace_payload
from .maps import map_get, scan_map
from .platforms.observation_port import location
from .records import application_registry, link


class ConnectionBoundaryError(RecordError):
    def __init__(self, code, directory=None):
        super().__init__(code)
        self.directory = directory


def _identity(native):
    return native.volume, native.file_id


def _ancestor_ids(root):
    path = Path(root.path)
    try:
        require(_identity(location(path)) == _identity(root), 'connection-root-changed')
        return {_identity(location(parent)) for parent in path.parents} | {_identity(root)}
    except (OSError, RecordError) as exc:
        raise ConnectionBoundaryError('connect-boundary-unavailable', root.path) from exc


def _present(path):
    try:
        path.lstat()
        return True
    except FileNotFoundError:
        return False


def _check_ancestor_markers(target, git):
    for parent in Path(target.root.path).parents:
        try:
            if _present(parent / '.colvia-link.json'):
                raise ConnectionBoundaryError('connect-ancestor-marker', str(parent))
            if _present(parent / '.git'):
                top = discover(parent, git)
                require(top.kind == 'git' and _identity(top.root) == _identity(location(parent)),
                        'connection-ancestor-git-unavailable')
                if top.common == target.common:
                    continue  # The caller verifies the exact shared locator.
                records = Path(top.common.path) / 'colvia'
                if _present(records):
                    location(records)
                    if _present(records / 'connection.json'):
                        raise ConnectionBoundaryError('connect-ancestor-marker', str(parent))
        except ConnectionBoundaryError:
            raise
        except (OSError, RecordError) as exc:
            raise ConnectionBoundaryError('connect-boundary-unavailable', str(parent)) from exc


def _integration_workspace(store):
    ref = store.head('project:integration')
    if ref is None:
        return None, None
    registry = application_registry()
    config = registry.inspect(ref, store.load(ref), required=True)
    binding, workspace = link(config, 'binding'), link(config, 'workspace')
    obj = registry.inspect(workspace, store.load(workspace), required=True)
    require(obj.ref.kind == 'workspace.registration' and link(obj, 'project') == binding,
            'managed-integration-stale')
    return binding, workspace_payload(obj.payload)


def _git_workspace_roots(connections, binding_ref, binding, integration, git):
    store = connections.store
    require(git is not None, 'git-prerequisite-required')
    integration_binding, workspace = integration
    if integration_binding != binding_ref:
        # A crash may leave the binding published before integration. Find a
        # current workspace in the existing bounded head map only in this case.
        for key, ref in scan_map(store.root().heads, store.load):
            if not key.startswith('workspace:'):
                continue
            record = decode_envelope(ref, store.load(ref))
            if link(record, 'project') == binding_ref:
                _, workspace, _ = connections.workspace(key.split(':', 1)[1])
                break
        else:
            raise RecordError('workspace-registration-required')
    try:
        top = discover(Path(workspace.root.path), git)
        require(top.kind == 'git' and top.common == binding.location and
                top.root == workspace.root and top.gitdir == workspace.gitdir,
                'workspace-location-changed')
        registrations = connections.registrations(top, current_only=True)
        require(workspace in registrations, 'workspace-registration-required')
    except (OSError, RecordError) as exc:
        raise ConnectionBoundaryError('connect-boundary-unavailable', workspace.root.path) from exc
    return tuple(item.root for item in registrations)


def verified_reservation(store, plan, top, published):
    """Prove the operation published the binding and workspace still in use."""
    require(store.project == plan['project'] and store.instance == plan['instance'],
            'connect-reservation-changed')
    connections = Connections(store)
    binding_ref, binding = connections.binding()
    workspace_ref, workspace, _ = connections.workspace(plan['workspace'])
    result = decode_envelope(published[1], store.load(published[1]))
    heads = link(result, 'heads')
    require(binding.locator == Locator.parse(canonical_bytes(plan['locator']), kind=top.kind) and
            binding.location == (top.common if top.kind == 'git' else top.root) and
            workspace.root == top.root and workspace.gitdir == top.gitdir and
            store.head(location_key(workspace.root)) == workspace_ref and
            map_get(heads, PROJECT_KEY, store.load) == binding_ref and
            map_get(heads, workspace_key(workspace.workspace), store.load) == workspace_ref,
            'connect-reservation-changed')
    return store.project, store.instance, binding_ref


def check_connection_boundary(home, git, top, *, overlap_code, historical=False, own=None):
    """Caller holds manager exclusion for any write relying on this check."""
    target = top.root
    target_ids = _ancestor_ids(target)
    reconnect = False
    own_verified = own is None
    try:
        projects = home.projects()
    except (OSError, ValueError) as exc:
        raise ConnectionBoundaryError('connect-boundary-unavailable') from exc
    for project in projects:
        directory = None
        try:
            with closing(home.authority(project).store(readonly=True)) as store:
                binding_ref = store.head(PROJECT_KEY)
                if (project, store.instance, binding_ref) == own:
                    own_verified = True
                    continue
                live = binding_ref is not None and not store.needs_rebind()
                connections = Connections(store)
                binding = connections.binding()[1] if live else None
                if binding is not None:
                    directory = binding.location.path
                integration = _integration_workspace(store) if historical or (binding and binding.kind == 'git') else (None, None)
                integration_binding, previous = integration
                if previous is not None:
                    if historical:
                        reconnect |= (same_plain_path(previous.root.path, target.path) or
                                      _identity(previous.root) == _identity(target))
                    if integration_binding == binding_ref:
                        directory = previous.root.path
                if not live:
                    continue

                if binding.kind == 'plain':
                    workspace_ref, workspace, _ = connections.workspace(binding.locator.workspace)
                    require(workspace.root == binding.location and workspace.gitdir is None and
                            store.head(location_key(workspace.root)) == workspace_ref,
                            'workspace-location-index-mismatch')
                    roots = (workspace.root,)
                else:
                    roots = _git_workspace_roots(connections, binding_ref, binding, integration, git)
                    # A separate authority cannot share the same Git locator,
                    # even if the target worktree has not been registered yet.
                    if top.kind == 'git' and _identity(binding.location) == _identity(top.common):
                        raise ConnectionBoundaryError(overlap_code, roots[0].path)
                for root in roots:
                    occupied_ids = _ancestor_ids(root)
                    if _identity(root) in target_ids or _identity(target) in occupied_ids:
                        raise ConnectionBoundaryError(overlap_code, root.path)
        except ConnectionBoundaryError:
            raise
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise ConnectionBoundaryError('connect-boundary-unavailable', directory) from exc

    require(own_verified, 'connect-reservation-changed')
    require(not reconnect, 'project-reconnect-or-move-review-required')
    _check_ancestor_markers(top, git)
