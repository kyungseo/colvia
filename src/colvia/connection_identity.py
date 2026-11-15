"""Immutable location evidence scoped to an exact binding and registration."""
from dataclasses import asdict, replace
from pathlib import PurePosixPath, PureWindowsPath
import re

from .binding import persistent, revalidates
from .codec import Edge, decode_envelope, encode_envelope, require
from .graph import Schema
from .storage.sqlite import _token

PROJECT_IDENTITY = 'connection-identity:project'
ROLES = ('root', 'common', 'gitdir')


def identity_key(workspace):
    from .binding import _uuid
    _uuid(workspace)
    return 'connection-identity:workspace:' + workspace


def payload(value):
    from .connection import native
    require(type(value) is dict and
            set(value) == {'mode', 'locations', 'operation', 'receipt', 'statement', 'links'} and
            value['links'] in ({'binding': [0], 'workspace': [1], 'common': []},
                               {'binding': [0], 'workspace': [1], 'common': [2]}), 'connection-identity-invalid')
    _token(value['operation'])
    require(type(value['locations']) is dict and set(value['locations']) == set(ROLES),
            'connection-identity-invalid')
    locations = {role: native(raw) if raw is not None else None for role, raw in value['locations'].items()}
    require(persistent(locations['root']) and
            all(v is None or persistent(v) for v in locations.values()), 'connection-identity-invalid')
    if value['mode'] == 'initial':
        require(value['receipt'] is None and value['statement'] is None, 'connection-identity-invalid')
    else:
        receipt, statement = value['receipt'], value['statement']
        require(value['mode'] == 'legacy-revalidated' and type(receipt) is str and len(receipt) == 64 and
                all(c in '0123456789abcdef' for c in receipt) and
                type(statement) is str and 0 < len(statement) <= 16384 and '\x00' not in statement,
                'connection-identity-invalid')
    return locations


def schema():
    return Schema('connection.identity', 1, {'binding': 'decision', 'workspace': 'decision', 'common': 'decision'}, payload,
                  {'binding': frozenset({'project.binding'}), 'workspace': frozenset({'workspace.registration'}),
                   'common': frozenset({'connection.identity'})},
                  content=evidence)


def values(binding, workspace):
    return dict(root=workspace.root, gitdir=workspace.gitdir,
                common=binding.location if binding.kind == 'git' else None)


def create(operation, project_ref, workspace_ref, locations, *, receipt=None, statement=None, common=None):
    return encode_envelope('connection.identity', 1, dict(
        mode='initial' if receipt is None else 'legacy-revalidated',
        operation=operation, receipt=receipt, statement=statement,
        locations={k: asdict(v) if v is not None else None for k, v in locations.items()},
        links={'binding': [0], 'workspace': [1], 'common': [] if common is None else [2]}),
        (Edge('decision', project_ref), Edge('decision', workspace_ref)) +
        (() if common is None else (Edge('decision', common),)))


def evidence(ref, load, *, _primary=False):
    if ref.version == 2:
        project, workspace, binding, registration, history = _move_history(ref, load)
        return project, workspace, binding, registration, history[0], history[-1]
    from .connection import binding_payload, workspace_payload, connection_schemas
    obj = decode_envelope(ref, load(ref))
    schema().check(obj)
    project, workspace = (edge.ref for edge in obj.edges[:2])
    b, w = (decode_envelope(r, load(r)) for r in (project, workspace))
    connection_schemas()[0].check(b)
    connection_schemas()[1].check(w)
    require(w.edges[0].ref == project, 'connection-identity-binding-mismatch')
    binding, registration = binding_payload(b.payload), workspace_payload(w.payload)
    old, current = values(binding, registration), payload(obj.payload)
    require(binding.kind == 'git' or (old['root'] == binding.location and
            binding.locator.workspace == registration.workspace), 'connection-identity-binding-mismatch')
    require((old['gitdir'] is None) == (binding.kind == 'plain'), 'connection-identity-binding-mismatch')
    if len(obj.edges) == 3:
        parent_ref = obj.edges[2].ref
        require(not _primary and binding.kind == 'git' and obj.payload['mode'] == 'initial' and
                (parent_ref.version == 2 or revalidates(old['common'], current['common'])),
                'connection-identity-common-invalid')
        parent = evidence(parent_ref, load, _primary=True)
        require(parent[0] == project and parent[5]['common'] == current['common'] and
                (parent_ref.version != 2 or parent[4]['common'] == old['common']),
                'connection-identity-common-invalid')
    for role in ROLES:
        if role == 'common' and len(obj.edges) == 3:
            continue
        a, b = old[role], current[role]
        valid = a == b if obj.payload['mode'] == 'initial' or a is None or persistent(a) else revalidates(a, b)
        require(valid, 'connection-identity-location-mismatch')
    return project, workspace, binding, registration, old, current


def effective(ref, load):
    project, workspace, binding, registration, _, current = evidence(ref, load)
    return project, workspace, replace(binding, location=current['common'] or current['root']), replace(
        registration, root=current['root'], gitdir=current['gitdir'])


def equivalent(ref, load, workspace, first, second, role):
    if first == second:
        return True
    if ref is None:
        return False
    if ref.version == 2:
        _, registered, _, _, history = _move_history(ref, load)
    else:
        _, registered, _, _, old, current = evidence(ref, load)
        history = (old, current)
    if registered != workspace:
        return False
    locations = [asdict(row[role]) for row in history if row[role] is not None]
    return first in locations and second in locations


def contexts_match(first, second, keys, *, load, workspace, anchors=()):
    for role in keys:
        a, b = first[role], second[role]
        if a != b and (role not in ROLES or not any(equivalent(anchor, load, workspace, a, b, role)
                                                  for anchor in anchors if anchor is not None)):
            return False
    return True


def same_directory(old, new):
    if old is None or new is None or (old.volume, old.file_id) != (new.volume, new.file_id):
        return False
    if persistent(old):
        return persistent(new)
    return (PureWindowsPath(old.path).is_absolute() and PureWindowsPath(new.path).is_absolute() and
            re.fullmatch(r'[1-9][0-9]*', old.volume) is not None and
            re.fullmatch(r'(?!0{32}:)[0-9a-f]{32}:[1-9][0-9]*', old.file_id) is not None)


def _move_locations(values, keys):
    from .connection import native
    require(type(values) is dict and set(values) == set(keys), 'connection-move-invalid')
    return {role: native(value) if value is not None else None for role, value in values.items()}


def _move_payload(value):
    require(type(value) is dict and set(value) == {'before', 'after', 'operation', 'receipt', 'statement', 'links'}
            and value['links'] in ({'binding': [0], 'workspace': [1], 'previous': []},
                                   {'binding': [0], 'workspace': [1], 'previous': [2]}),
            'connection-move-invalid')
    _token(value['operation'])
    require(type(value['receipt']) is str and re.fullmatch('[0-9a-f]{64}', value['receipt']) is not None and
            type(value['statement']) is str and 0 < len(value['statement']) <= 16384 and '\x00' not in value['statement'],
            'connection-move-invalid')
    before, after = (_move_locations(value[k], ROLES) for k in ('before', 'after'))
    require(before['root'] != after['root'] and same_directory(before['root'], after['root']),
            'connection-move-identity-changed')
    if before['common'] is None:
        require(before['gitdir'] is None and after['common'] is None and after['gitdir'] is None,
                'connection-move-topology')
    else:
        require(before['common'] == before['gitdir'] and after['common'] == after['gitdir'] and
                same_directory(before['common'], after['common']), 'connection-move-topology')
        for row in (before, after):
            cls = PurePosixPath if persistent(row['root']) else PureWindowsPath
            require(row['common'].path == str(cls(row['root'].path) / '.git'), 'connection-move-topology')
    return before, after


def move_schema():
    return Schema('connection.identity', 2, {'binding': 'decision', 'workspace': 'decision', 'previous': 'provenance'},
                  _move_payload,
                  {'binding': frozenset({'project.binding'}), 'workspace': frozenset({'workspace.registration'}),
                   'previous': frozenset({'connection.identity'})}, content=_move_history)


def create_move(operation, project, workspace, before, after, receipt, statement, previous):
    roles = (Edge('decision', project), Edge('decision', workspace))
    return encode_envelope('connection.identity', 2, dict(
        before={k: asdict(v) if v is not None else None for k, v in before.items()},
        after={k: asdict(v) if v is not None else None for k, v in after.items()},
        operation=operation, receipt=receipt, statement=statement,
        links={'binding': [0], 'workspace': [1], 'previous': [2] if previous else []}),
        roles + ((Edge('provenance', previous),) if previous else ()))


def _move_history(ref, load):
    from .connection import binding_payload, connection_schemas, workspace_payload
    obj = decode_envelope(ref, load(ref))
    move_schema().check(obj)
    project, workspace = (edge.ref for edge in obj.edges[:2])
    b, w = (decode_envelope(r, load(r)) for r in (project, workspace))
    connection_schemas()[0].check(b)
    connection_schemas()[1].check(w)
    require(w.edges[0].ref == project, 'connection-move-binding-mismatch')
    binding, registration = binding_payload(b.payload), workspace_payload(w.payload)
    require(binding.kind == 'git' or
            (binding.location == registration.root and binding.locator.workspace == registration.workspace),
            'connection-move-binding-mismatch')
    history = []
    for _ in range(10000):
        move_schema().check(obj)
        before, after = _move_payload(obj.payload)
        require(tuple(e.ref for e in obj.edges[:2]) == (project, workspace) and
                (before['common'] is None) == (binding.kind == 'plain'),
                'connection-move-binding-mismatch')
        require(not history or history[-1] == after, 'connection-move-lineage-changed')
        if not history:
            history.append(after)
        history.append(before)
        previous = obj.edges[2].ref if len(obj.edges) == 3 else None
        if previous is not None and previous.version == 2:
            obj = decode_envelope(previous, load(previous))
            continue
        if previous is not None:
            b_ref, w_ref, _, _, old, current = evidence(previous, load, _primary=True)
            require((b_ref, w_ref) == (project, workspace) and current == before,
                    'connection-move-lineage-changed')
            history.append(old)
        else:
            require(not persistent(before['root']) and before == values(binding, registration),
                    'connection-move-lineage-changed')
        return project, workspace, binding, registration, tuple(reversed(history))
    require(False, 'connection-move-history-limit')
