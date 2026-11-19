"""An explicit, verified location change without editing files in the project."""
from contextlib import closing, nullcontext
from dataclasses import asdict
from pathlib import Path

from .binding import Membership, persistent
from .codec import ObjectRef, RecordError, canonical_bytes, decode_canonical, decode_envelope, require
from .connection import Connections, PROJECT_KEY, location_key, native, workspace_key
from .connection_boundary import _integration_workspace, check_connection_boundary, workspace_topology
from .connection_identity import (PROJECT_IDENTITY, ROLES, create_move, evidence, identity_key,
                                  same_directory, values)
from .delivery.service import OUTSTANDING
from .effects import guard
from .execution.schema import CLOSED as EXECUTION_CLOSED
from .maps import map_get, scan_map
from .platforms.observation_port import location, snapshot
from .platforms.posix import ObservationBudget
from .platforms.structural import prove
from .project_setup import ProjectSetup, sha
from .records import decode_policy, head_summary, link, text
from .observation import relocated_policy
from .storage.sqlite import _token

_LIMIT = 8 * 1024 * 1024


def _ref(value):
    return ObjectRef.parse(value) if value is not None else None


def _locations(raw):
    return {k: native(raw[k]) if raw[k] is not None else None for k in ROLES}


def _record(ref):
    return ref.as_dict() if ref is not None else None


def _check_idle(store):
    guard(store)
    require(not store.needs_rebind() and store.lifecycle_state() == {'fence': None, 'quiescent': None},
            'connection-move-lifecycle-pending')
    require(not store.has_active_imports() and store.head(OUTSTANDING) is None, 'connection-move-work-pending')
    # A prepared absolute operation may be live even before it acquires the
    # effect reservation. Completed historical records remain readable.
    for key, ref in scan_map(store.root().heads, store.load):
        if key.startswith('git-integration:'):
            phase = decode_envelope(ref, store.load(ref)).payload['phase']
            require(phase in ('completed', 'not-applied'), 'connection-move-work-pending')
        elif key.startswith('execution-prepared:'):
            state = store.head('execution:' + key.split(':', 1)[1])
            require(state is not None and state.kind == 'execution.state' and
                    decode_envelope(state, store.load(state)).payload['status'] in EXECUTION_CLOSED,
                    'connection-move-work-pending')
        elif key.startswith('delivery-prepared:'):
            state = store.head('delivery:' + key.split(':', 1)[1])
            require(state is not None and state.kind == 'delivery.state' and
                    decode_envelope(state, store.load(state)).payload['phase'] in ('finished', 'cancelled', 'failed'),
                    'connection-move-work-pending')
        elif ref.kind == 'worker.binding':
            require(False, 'connection-move-work-pending')


class MoveSetup(ProjectSetup):
    def _candidate(self, authority, store, root):
        from .cli import read_locator

        require(not authority.files.exists(authority.root/'pending.json'), 'connection-move-lifecycle-pending')
        _check_idle(store)
        connections = Connections(store)
        project, binding = connections.binding()
        owner, integration = _integration_workspace(store)
        require(owner == project and integration is not None, 'managed-integration-stale')
        workspace, current, _ = connections.workspace(integration.workspace)
        for key, ref in scan_map(store.root().heads, store.load):
            if key.startswith('workspace:') and ref != workspace:
                registered = decode_envelope(ref, store.load(ref))
                require(link(registered, 'project') != project, 'connection-move-topology')
        prior = connections.identity(workspace)
        before = values(binding, current)
        try:
            top = workspace_topology(root, self.git)
        except FileNotFoundError as exc:
            raise RecordError('connection-move-topology') from exc
        require(top.kind == binding.kind and Path(top.root.path) == root, 'connection-move-topology')
        require(read_locator(root, self.git) == binding.locator, 'stale-or-foreign-binding')
        after = {role: getattr(top, role) for role in ROLES}
        require(before['root'] != top.root and same_directory(before['root'], top.root),
                'connection-move-identity-changed')
        try:
            location(Path(before['root'].path))
        except FileNotFoundError:
            pass
        else:
            require(False, 'connection-move-original-present')
        boundaries = {}
        if top.kind == 'git':
            require(top.common == top.gitdir and Path(top.common.path) == root/'.git' and
                    top.members == (Membership(top.root, top.gitdir),) and
                    same_directory(before['common'], top.common) and same_directory(before['gitdir'], top.gitdir),
                    'connection-move-topology')
            require(all(entry.mode != '160000' for entry in self.git.index(root).values()), 'connection-move-topology')
            registration = type(current)(current.workspace, top.root, top.gitdir)
            boundaries = prove(top, (registration,)).boundaries
        inventory = snapshot(root, ObservationBudget(100000, 0), admit=lambda _: False, boundaries=boundaries,
                             reject_nested_git=True, reject_nested_colvia=True)
        if top.kind == 'git':
            policy = self.git.policy(top, inventory.inventory)
            for key, ref in scan_map(store.root().heads, store.load):
                if not key.startswith('work:'):
                    continue
                head, plan, result, _ = head_summary(ref, store.load)
                if head.payload['workspace'] != current.workspace or head.payload['phase'] in ('completed','discarded'):
                    continue
                phase = head.payload['origin'] if head.payload['phase'] == 'paused' else head.payload['phase']
                require(result is None or result.ref.version == 1 or phase != 'active',
                        'connection-move-work-pending')
                baseline = decode_envelope(link(plan, 'baseline'), store.load(link(plan, 'baseline')))
                old = decode_policy(link(baseline, 'policy'), store.load)
                old = relocated_policy(old, baseline.payload['common'], asdict(top.common))
                require(old.config == policy.config and old.tool == policy.tool and
                        tuple(s for s in old.sources if s.origin.startswith('global:')) ==
                        tuple(s for s in policy.sources if s.origin.startswith('global:')),
                        'connection-move-policy-changed')
        check_connection_boundary(self.home, self.git, top, overlap_code='connect-project-overlap',
                                  own=(store.project, store.instance, project))
        require(workspace_topology(root, self.git) == top and read_locator(root, self.git) == binding.locator,
                'connection-move-observation-changed')
        if self.runtime_lease is not None:
            caps = {'schema:connection.identity:2', 'schema:observation.snapshot:2'}
            slot = self.runtime_lease.verified
            require(caps <= slot.read_capabilities and caps <= slot.write_capabilities, 'runtime-capability-unavailable')
        require(not persistent(before['root']) or prior is not None, 'connection-identity-required')
        return dict(version=1, authority=authority.pointer_value(), state=_record(store.root().ref),
                    binding=_record(project), workspace=_record(workspace), workspace_id=current.workspace,
                    anchor=_record(store.head(PROJECT_IDENTITY)), prior=_record(prior),
                    before={k: asdict(v) if v is not None else None for k, v in before.items()},
                    after={k: asdict(v) if v is not None else None for k, v in after.items()})

    def preview(self, project, root):
        with self.runtime_lease.hold() if self.runtime_lease else nullcontext():
            authority = self.home.authority(project)
            with closing(authority.store(readonly=True)) as store:
                anchor = store.root().ref
                plan = self._candidate(authority, store, Path(root))
                require(_ref(plan['state']) == anchor, 'connection-move-observation-changed')
        return dict(state='review', plan=plan, receipt=sha(canonical_bytes(plan)),
                    question='기존 작업과 승인을 보존하면서 표시한 새 폴더를 이 프로젝트의 위치로 확인할까요?')

    def _journal(self, operation):
        _token(operation)
        value = decode_canonical(self.home.files.read(self.home.root/'operations'/operation/'move.json', _LIMIT))
        require(type(value) is dict and set(value) == {'operation', 'plan', 'receipt', 'statement'} and
                value['operation'] == operation and sha(canonical_bytes(value['plan'])) == value['receipt'],
                'connection-move-journal-changed')
        text(value['statement'])
        return value

    def _proof(self, value):
        plan = value['plan']
        return create_move(value['operation'], _ref(plan['binding']), _ref(plan['workspace']),
                           _locations(plan['before']), _locations(plan['after']), value['receipt'],
                           value['statement'], _ref(plan['prior']))

    def _check(self, authority, store, plan):
        require(authority.pointer_value() == plan['authority'] and store.root().ref == _ref(plan['state']),
                'connection-move-review-changed')
        current = self._candidate(authority, store, Path(plan['after']['root']['path']))
        require(canonical_bytes(current) == canonical_bytes(plan), 'connection-move-review-changed')

    def _apply(self, authority, store, value, checkpoint):
        plan = value['plan']
        before, after = (_locations(plan[k]) for k in ('before', 'after'))
        binding, workspace = (_ref(plan[k]) for k in ('binding', 'workspace'))
        current = location_key(after['root'])
        historical = Connections(store).workspace_record(plan['workspace_id'], binding)[1]
        old = location_key(before['root'])
        old_original = location_key(historical.root)
        aliases = store.head(current)
        require(aliases is None or (current == old_original and aliases == workspace),
                'workspace-location-index-conflict')
        expected = {PROJECT_KEY: binding, PROJECT_IDENTITY: _ref(plan['anchor']),
                    identity_key(plan['workspace_id']): _ref(plan['prior']),
                    workspace_key(plan['workspace_id']): workspace,
                    'project:integration': store.head('project:integration'), old: workspace, current: aliases}
        ref, raw = self._proof(value)
        changes = {PROJECT_IDENTITY: ref, identity_key(plan['workspace_id']): ref, current: workspace}
        if old != old_original:
            changes[old] = None
        def validate(view):
            guard(view)
            self._check(authority, store, plan)
            evidence(ref, view)
        store.commit_heads(operation=value['operation'], expected=expected, changes=changes, objects=[(ref, raw)],
                           validate=validate, _no_active_imports=True)
        checkpoint('published')
        return self._status(store, value)

    def _status(self, store, value):
        plan = value['plan']
        result = store.operation_result(value['operation'])
        state = 'pending'
        if result is not None:
            require(result[0] == _ref(plan['state']), 'connection-move-operation-conflict')
            recorded = decode_envelope(result[1], store.load(result[1]))
            ref, _ = self._proof(value)
            require(map_get(link(recorded, 'heads'), PROJECT_IDENTITY, store.load) == ref,
                    'connection-move-operation-conflict')
            state = 'moved' if store.head(PROJECT_IDENTITY) == ref else 'subsequently-changed'
        return dict(state=state, project=store.project, operation=value['operation'],
                    previous=plan['before']['root']['path'], location=plan['after']['root']['path'])

    def start(self, *, operation, plan, receipt, statement, checkpoint=lambda _: None):
        _token(operation)
        text(statement)
        require(sha(canonical_bytes(plan)) == receipt, 'connection-move-review-changed')
        with self.management():
            authority = self.home.authority(plan['authority']['project'])
            with closing(self.home.store(authority.project) if self.runtime_lease else authority.store()) as store:
                self._check(authority, store, plan)
                require(store.operation_result(operation) is None, 'connection-move-operation-conflict')
                area = self.home.root/'operations'/operation
                self.home.files.create_directory(area)
                value = dict(operation=operation, plan=plan, receipt=receipt, statement=statement)
                self.home.files.create(area/'move.json', canonical_bytes(value))
                checkpoint('intent')
                return self._apply(authority, store, value, checkpoint)

    def status(self, operation):
        value = self._journal(operation)
        authority = self.home.authority(value['plan']['authority']['project'])
        require(authority.pointer_value() == value['plan']['authority'], 'connection-move-review-changed')
        with closing(authority.store(readonly=True)) as store:
            return self._status(store, value)

    def resume(self, operation, *, checkpoint=lambda _: None):
        with self.management():
            value = self._journal(operation)
            plan = value['plan']
            authority = self.home.authority(plan['authority']['project'])
            require(authority.pointer_value() == plan['authority'], 'connection-move-review-changed')
            with closing(self.home.store(authority.project) if self.runtime_lease else authority.store()) as store:
                status = self._status(store, value)
                return self._apply(authority, store, value, checkpoint) if status['state'] == 'pending' else status
