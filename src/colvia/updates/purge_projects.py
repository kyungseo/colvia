"""Resolve the owner workspace from account records before complete removal."""
from contextlib import closing
from pathlib import Path

from ..codec import RecordError, decode_envelope, require
from ..connection import Connections, PROJECT_KEY
from ..connection_boundary import _integration_workspace
from ..effects import PENDING
from ..maps import scan_map
from ..records import link


def project_list(home, setup, exclude_unavailable=False):
    projects = []
    for project in home.projects():
        authority = home.authority(project)
        with closing(authority.store(readonly=True)) as store:
            require(store.head(PENDING) is None and not home.files.exists(authority.root/'pending.json'),
                    'purge-project-operation-pending')
            binding = store.head(PROJECT_KEY)
            integration, workspace = _integration_workspace(store)
            phases = {}
            for key, ref in scan_map(store.root().heads, store.load):
                if key.startswith('work:'):
                    phase = decode_envelope(ref, store.load(ref)).payload['phase']
                    phases[phase] = phases.get(phase, 0) + 1
            row = dict(project=project, instance=store.instance, records=store.root().ref.as_dict(),
                       work_states=phases)
            if binding is None:
                row.update(state='detached')
            elif store.needs_rebind() or workspace is None or integration != binding:
                _, bound = Connections(store).binding()
                row.update(state='excluded' if exclude_unavailable else 'unavailable',
                           recorded_location=bound.location.path, reason='purge-project-ownership-unconfirmed')
            else:
                _, current, bound = Connections(store).workspace(workspace.workspace)
                row.update(root=current.root.path, kind=bound.kind)
                if bound.kind == 'git':
                    row['common_directory'] = bound.location.path
        if 'state' not in row:
            try:
                _, opened, service, changes = setup.detach_context(project, Path(row['root']))
                with closing(opened):
                    receipt = service.preview(changes)['receipt']
                row.update(state='connected', detach_receipt=receipt,
                           managed_paths=[dict(root=c['root'], path=c['path']) for c in changes])
            except (OSError, RecordError) as exc:
                row.update(state='excluded' if exclude_unavailable else 'unavailable',
                           reason=getattr(exc, 'code', type(exc).__name__))
        projects.append(row)
    return projects


def detach_approved(home, setup, row, operation, checkpoint):
    """Both management locks are held. The detach ledger survives partial file effects."""
    from ..lifecycle import Detach

    authority = home.authority(row['project'])
    with closing(authority.store()) as store:
        require(store.instance == row['instance'], 'purge-project-replaced')
        port = setup._detach_port(authority, dict(project=Path(row['root']),
                                  locator=Path(row.get('common_directory', row['root']))))
        service = Detach(store, port)
        if store.head(service.key(operation)) is None:
            require(store.root().ref.as_dict() == row['records'], 'purge-project-changed')
            _, opened, starting, changes = setup.detach_context(row['project'], Path(row['root']))
            with closing(opened):
                starting.begin(operation=operation, changes=changes, receipt=row['detach_receipt'],
                               statement='Approved complete removal')
        for _ in range(len(row['managed_paths']) + 1):
            result = service.advance(operation)
            checkpoint('project-step')
            if result['state'] == 'detached':
                state = service.registry.inspect(store.head(service.key(operation)),
                                                 store.load(store.head(service.key(operation))), required=True)
                ref = link(state, 'plan')
                manifest = service.registry.inspect(ref, store.load(ref), required=True).payload['manifest']
                additions = set()
                for step in manifest['steps']:
                    native = step['native']
                    stage = authority.root / 'effects' / native['application']
                    additions.add(stage.relative_to(home.root).as_posix())
                    for item in native['items']:
                        for key in ('evacuated_name', 'post_name'):
                            additions.add((stage / item[key]).relative_to(home.root).as_posix())
                return additions
        raise RecordError('purge-detach-incomplete')
