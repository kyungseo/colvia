"""Approve Git adoption for an idle, already-connected ordinary workspace."""
from contextlib import closing, nullcontext
from dataclasses import asdict
from pathlib import Path
import hashlib
import secrets
import uuid

from .adapters.git import discover, read_file
from .binding import Locator, Membership, ProjectBinding, WorkspaceRegistration
from .codec import ObjectRef, RecordError, canonical_bytes, decode_canonical, decode_envelope, require
from .connection import Connections, PROJECT_KEY, location_key, workspace_key
from .connection_boundary import _check_ancestor_markers, check_connection_boundary
from .effects import PENDING, guard
from .first_git import empty_repository, publish_repository, seed_repository, tool_identity
from .git_transition_record import KEY, KIND
from .maps import scan_map
from .move_setup import _check_idle
from .platforms.observation_port import location, snapshot
from .platforms.owned_install_files import present
from .platforms.posix import ObservationBudget
from .platforms.structural import prove
from .project_setup import ProjectSetup, b64, sha
from .records import head_summary, link, record, text
from .storage.sqlite import _token


LIMIT = 8 * 1024 * 1024
MARKER = '.colvia-link.json'
NAMESPACE = 'colvia'
GIT_MARKER = 'colvia/connection.json'
CHANGED = 'git-transition-review-changed'


def _digest(value):
    return sha(canonical_bytes(value))


def _file_hash(path):
    if present(path):
        return sha(read_file(path, 64 * 1024 * 1024))
    return None


def _repository(git, top, inventory):
    root = Path(top.root.path)
    admin = root/'.git'
    require(top.common == top.gitdir and Path(top.common.path) == admin and
            top.members == (Membership(top.root, top.gitdir),), 'git-transition-single-root-required')
    for name in ('index.lock', 'HEAD.lock', 'packed-refs.lock', 'MERGE_HEAD', 'CHERRY_PICK_HEAD',
                 'REVERT_HEAD', 'rebase-apply', 'rebase-merge', 'sequencer', 'BISECT_LOG'):
        require(not present(admin/name), 'git-transition-git-busy')
    index = git.index(root)
    require(all(entry.mode != '160000' for entry in index.values()), 'git-transition-single-root-required')
    require(all(path.casefold() != MARKER for path in git.tracked_for_creation(root)), 'git-transition-tracked-locator')
    refs = git._run(root, ('for-each-ref', '--format=%(refname) %(objectname)')).stdout
    return dict(location=asdict(top.common), head=_file_hash(admin/'HEAD'), refs=sha(refs),
                index=_file_hash(admin/'index'), config=_file_hash(admin/'config'),
                policy=git.policy(top, inventory).digest)


def _observation(setup, store, root, workspace, original_binding):
    top = discover(root, setup.git)
    require(top.root == workspace.root, 'git-transition-folder-changed')
    _check_ancestor_markers(top, setup.git)
    check_connection_boundary(setup.home, setup.git, top, overlap_code='connect-project-overlap',
                              own=(store.project, store.instance, original_binding))
    boundaries = {}
    if top.kind == 'git':
        require(top.common == top.gitdir and top.members == (Membership(top.root, top.gitdir),)
                and Path(top.common.path) == root/'.git', 'git-transition-single-root-required')
        boundaries = prove(top, (WorkspaceRegistration(workspace.workspace, top.root, top.gitdir),)).boundaries
    observation = snapshot(root, ObservationBudget(100000, 2 * 1024**3), boundaries=boundaries,
                           admit=lambda path: path != MARKER, reject_nested_git=True, reject_nested_colvia=True)
    inventory = [row for row in observation.inventory if row.native_path != MARKER]
    # Each canonical JSON record is one line. This also bounds peak encoding memory.
    fingerprint = hashlib.sha256()
    for row in inventory:
        fingerprint.update(canonical_bytes(row.native_path) + b'\n')
    for entry in observation.entries:
        fingerprint.update(canonical_bytes(entry) + b'\n')
    files = fingerprint.hexdigest()
    repository = _repository(setup.git, top, inventory) if top.kind == 'git' else None
    sample = {e['path']: _digest(e) for e in observation.entries[:16]}
    return top, files, repository, sample


def _transition(value, phase, new=None, prior=None, *, review=None, statement=None):
    old = ObjectRef.parse(value['plan']['integration'])
    return record(KIND, dict(operation=value['operation'], phase=phase,
                  receipt=review['receipt'] if review else value['receipt'], statement=statement or value['statement'],
                  observed=review['observed'] if review else None),
                  {'old': ('decision', old), 'new': ('decision', new), 'prior': ('decision', prior)})


class GitTransition(ProjectSetup):
    def _candidate(self, authority, store, root):
        _check_idle(store)
        require(not present(authority.root/'pending.json'), 'git-transition-lifecycle-pending')
        require(store.head(KEY) is None, 'git-transition-already-converted')
        initial = store.root().ref
        connections = Connections(store)
        project, binding = connections.binding()
        require(binding.kind == 'plain', 'git-transition-plain-required')
        wref, workspace, _ = connections.workspace(binding.locator.workspace)
        require(Path(workspace.root.path) == root and location(root) == workspace.root and
                location(self.home.root).volume == workspace.root.volume, 'git-transition-folder-changed')
        old = read_file(root/MARKER, 16384)
        require(Locator.parse(old, kind='plain') == binding.locator, 'stale-or-foreign-binding')
        integration = store.head('project:integration')
        require(integration is not None, 'managed-integration-unavailable')
        config = decode_envelope(integration, store.load(integration))
        require(link(config, 'binding') == project and link(config, 'workspace') == wref, 'managed-integration-stale')
        completed = 0
        for key, ref in scan_map(store.root().heads, store.load):
            if key.startswith('workspace:'):
                require(key == workspace_key(workspace.workspace) and ref == wref, 'git-transition-single-root-required')
            if key.startswith('work:'):
                head, _, _, _ = head_summary(ref, store.load)
                require(head.payload['phase'] in ('completed', 'discarded'), 'git-transition-unfinished-work')
                completed += 1
        if self.runtime_lease is not None:
            slot = self.runtime_lease.verified
            capability = 'schema:' + KIND + ':1'
            require(capability in slot.read_capabilities and capability in slot.write_capabilities,
                    'runtime-capability-unavailable')
        git = tool_identity(self)
        top, files, repository, sample = _observation(self, store, root, workspace, project)
        require(not present(root/'.git'/NAMESPACE), 'git-transition-foreign-locator')
        # Bind consent to the exact old locator that the retained-original adapter can retire.
        change = dict(role='locator', root='project', path=MARKER, before=old, after=None)
        retire = self._detach_port(authority, dict(project=root)).preview([change])
        require(store.root().ref == initial, CHANGED)
        return dict(version=1, authority=authority.pointer_value(), state=initial.as_dict(),
                    binding=project.as_dict(), workspace=wref.as_dict(), workspace_id=workspace.workspace,
                    integration=integration.as_dict(), root=asdict(top.root), git=git, files=files, sample=sample,
                    repository=repository, history_count=completed, retire=retire)

    def preview(self, project, root):
        authority = self.home.authority(project)
        with self.runtime_lease.hold() if self.runtime_lease else nullcontext():
            with closing(authority.store(readonly=True)) as store:
                plan = self._candidate(authority, store, Path(root))
        action = '현재 Git 저장소를 사용합니다.' if plan['repository'] else '빈 Git 저장소(main)를 만듭니다.'
        return dict(state='review', plan=plan, receipt=_digest(plan), question=action+
                    ' 기존 작업 기록과 스테이징을 보존하고 이 폴더의 연결을 Git으로 전환할까요?')

    def start(self, *, operation, plan, receipt, statement, checkpoint=lambda phase: None):
        _token(operation)
        text(statement)
        require(len(operation) <= 100 and _digest(plan) == receipt, CHANGED)
        with self.management():
            authority = self.home.authority(plan['authority']['project'])
            with closing(self.home.store(authority.project) if self.runtime_lease else authority.store()) as store:
                require(self._candidate(authority, store, Path(plan['root']['path'])) == plan, CHANGED)
                area = self.home.root/'operations'/operation
                self.home.files.create_directory(area)
                value = dict(operation=operation, plan=plan, receipt=receipt, statement=statement,
                             nonce=secrets.token_hex(32))
                self.home.files.create(area/'transition.json', canonical_bytes(value))
                checkpoint('intent')
                return self._apply(authority, store, area, value, checkpoint)

    def resume(self, operation, *, checkpoint=lambda phase: None, preview=False, cancel=False,
               receipt=None, statement=None):
        _token(operation)
        with self.management():
            area = self.home.root/'operations'/operation
            require(present(area/'transition.json'), 'git-transition-no-intent')
            value = decode_canonical(self.home.files.read(area/'transition.json', LIMIT))
            plan = value['plan']
            require(value['operation'] == operation and _digest(plan) == value['receipt'], CHANGED)
            authority = self.home.authority(plan['authority']['project'])
            require(authority.pointer_value() == plan['authority'], CHANGED)
            with closing(self.home.store(authority.project) if self.runtime_lease else authority.store()) as store:
                cancelled = present(area/'cancelled.json') or store.operation_result(operation+'-cancel') is not None
                if cancel:
                    if not cancelled:
                        self._cancel(authority, store, area, value)
                    return dict(state='cancelled', operation=operation, project=store.project)
                require(not cancelled, 'git-transition-cancelled')
                if preview or receipt is not None:
                    review = self._changed_review(store, area, value)
                    if preview:
                        return review
                    text(statement)
                    require(receipt == review['receipt'], CHANGED)
                    prior = store.head(PENDING)
                    updated = _transition(value, 'confirmed', prior=prior, review=review, statement=statement)
                    store.commit_heads(operation='confirm-'+uuid.uuid4().hex, expected={KEY: prior, PENDING: prior},
                                       changes={KEY: updated[0], PENDING: updated[0]}, objects=[updated],
                                       validate=lambda view: guard(view, expected_effect=prior), _no_active_imports=True)
                return self._apply(authority, store, area, value, checkpoint)

    def _cancel(self, authority, store, area, value):
        plan = value['plan']
        root = Path(plan['root']['path'])
        files = self.home.files
        operation = value['operation']
        reservation = store.head(PENDING)
        def verify():
            require(not present(area/'retire.json') and asdict(location(root)) == plan['root'],
                    'git-transition-cancel-too-late')
            # A private prepared directory still at its sealed source proves
            # that our exclusive publication of it has never taken place.
            for seal in ('seed.json', 'namespace.json'):
                if present(area/seal):
                    data = decode_canonical(files.read(area/seal))
                    stage = area/data['seed']/'.git' if seal == 'seed.json' else area/data['name']
                    require(present(stage) and files.directory_identity(stage) == data['identity'],
                            'git-transition-cancel-too-late')
            old, bound = Connections(store).binding()
            require(old.as_dict() == plan['binding'], 'git-transition-cancel-too-late')
            change = dict(role='locator', root='project', path=MARKER,
                          before=canonical_bytes(bound.locator.payload()), after=None)
            port = self._detach_port(authority, dict(project=root))
            require(port.preview([change]) == plan['retire'], 'git-transition-cancel-too-late')
        verify()
        if reservation is None:
            require(store.operation_result(operation+'-reserve') is None, 'git-transition-cancel-too-late')
            files.create(area/'cancelled.json', canonical_bytes(dict(receipt=value['receipt'])))
            return
        require(reservation.kind == KIND and store.head(KEY) == reservation, 'git-transition-cancel-too-late')
        saved = decode_envelope(reservation, store.load(reservation))
        require(saved.payload['operation'] == operation and link(saved,'old').as_dict() == plan['integration'],
                'git-transition-cancel-too-late')
        def check(view):
            guard(view, expected_effect=reservation)
            verify()
        store.commit_heads(operation=operation+'-cancel', expected={KEY:reservation, PENDING:reservation},
                           changes={KEY:None, PENDING:None}, validate=check, _no_active_imports=True)

    def _changed_review(self, store, area, value):
        plan = value['plan']
        root = Path(plan['root']['path'])
        prior = store.head(PENDING)
        require(prior is not None and prior.kind == KIND and store.head(KEY) == prior, CHANGED)
        approval = decode_envelope(prior, store.load(prior))
        require(approval.payload['operation'] == value['operation'] and
                link(approval, 'old').as_dict() == plan['integration'] and tool_identity(self) == plan['git'], CHANGED)
        old, _ = Connections(store).binding()
        _, workspace, _ = Connections(store).workspace(plan['workspace_id'])
        top, files, repository, sample = _observation(self, store, root, workspace, old)
        if plan['repository']:
            require(top.kind == 'git' and asdict(top.common) == plan['repository']['location'], CHANGED)
        elif top.kind == 'git':
            require(present(area/'seed.json'), 'git-transition-external-init')
            seed = decode_canonical(self.home.files.read(area/'seed.json'))
            require(not present(area/seed['seed']/'.git') and
                    self.home.files.directory_identity(root/'.git') == seed['identity'], 'git-transition-external-init')
        observed = dict(files=files, git=_digest(repository))
        receipt = _digest([value['receipt'], prior.as_dict(), observed])
        initial = plan['repository']
        if initial is None and present(area/'initial-git.json'):
            initial = decode_canonical(self.home.files.read(area/'initial-git.json'))['repository']
        git_changed = [field for field in ('head','refs','index','config','policy')
                       if (repository or {}).get(field) != (initial or {}).get(field)]
        staged = []
        if top.kind == 'git':
            raw = self.git._run(root, ('diff','--cached','--no-ext-diff','--no-renames','--name-only','-z')).stdout
            staged = [path.decode('utf-8') for path in raw.split(b'\0') if path]
            require(_file_hash(root/'.git/index') == repository['index'], CHANGED)
        # Examples from the intersection of two bounded samples are exact;
        # the complete inventory digest also detects additions and removals.
        examples = sorted(path for path in plan['sample'].keys() & sample.keys()
                          if plan['sample'][path] != sample[path])
        return dict(state='review', root=str(root), observed=observed, receipt=receipt,
                    changes_since_first_review=dict(working_files=files != plan['files'], examples=examples,
                        git_fields=git_changed, staged_count=len(staged), staged_examples=staged[:16]),
                    question='현재 작업 파일과 Git 상태를 그대로 보존하며 같은 전환을 이어갈까요?')

    def _apply(self, authority, store, area, value, checkpoint):
        plan = value['plan']
        operation = value['operation']
        root = Path(plan['root']['path'])
        result = dict(state='converted', project=store.project, workspace=plan['workspace_id'], operation=operation)
        pending = _transition(value, 'pending')
        current = store.head(KEY)
        if current is not None:
            saved = decode_envelope(current, store.load(current))
            require(saved.ref.kind == KIND and saved.payload['operation'] == operation and
                    link(saved, 'old').as_dict() == plan['integration'], CHANGED)
            if saved.payload['phase'] == 'completed':
                require(store.operation_result(operation+'-publish') is not None and
                        saved.payload['receipt'] == value['receipt'], CHANGED)
                return result
        else:
            require(self._candidate(authority, store, root) == plan, CHANGED)
            def reserve(view):
                guard(view)
                require(view.root().ref.as_dict() == plan['state'], CHANGED)
            store.commit_heads(operation=operation+'-reserve', expected={KEY: None, PENDING: None},
                               changes={KEY: pending[0], PENDING: pending[0]}, objects=[pending],
                               validate=reserve, _no_active_imports=True)
            checkpoint('reserved')
        reservation = store.head(KEY)
        approved = decode_envelope(reservation, store.load(reservation)).payload['observed']
        def live():
            require(store.head(PENDING) == store.head(KEY) == reservation and
                    store.head(PROJECT_KEY).as_dict() == plan['binding'] and
                    location(root) == native_root and tool_identity(self) == plan['git'], CHANGED)
        connections = Connections(store)
        old_ref, old_binding = connections.binding()
        _, workspace, _ = connections.workspace(plan['workspace_id'])
        native_root = workspace.root
        live()
        locator = Locator(store.project, store.instance, old_binding.locator.epoch + 1, value['nonce'])
        files = self.home.files
        def sealed(filename, prepare):
            path = area/filename
            if not present(path):
                files.create(path, canonical_bytes(prepare()))
            return decode_canonical(files.read(path, LIMIT))

        def observe():
            live()
            top, content, repository, _ = _observation(self, store, root, workspace, old_ref)
            require(content == (approved['files'] if approved else plan['files']), CHANGED)
            if plan['repository']:
                require(repository is not None and repository['location'] == plan['repository']['location'] and
                        _digest(repository) == (approved['git'] if approved else _digest(plan['repository'])), CHANGED)
            elif approved and approved['git'] != _digest(None):
                require(_digest(repository) == approved['git'], CHANGED)
            return top, repository

        top, repository = observe()
        if plan['repository'] is None:
            if top.kind == 'git':
                require(present(area/'seed.json'), 'git-transition-external-init')
            seed = sealed('seed.json', lambda: seed_repository(self, area))
            stage = area/seed['seed']/'.git'
            if top.kind == 'plain':
                require(files.directory_identity(stage) == seed['identity'] and empty_repository(stage) == seed['digest'], CHANGED)
                publish_repository(files, stage, root/'.git', seed['identity'], plan['root'])
                checkpoint('repository-published')
            require(not present(stage) and files.directory_identity(root/'.git') == seed['identity'], CHANGED)
            if not approved or approved['git'] == _digest(None):
                require(empty_repository(root/'.git', integrating=present(area/'namespace.json')) == seed['digest'], CHANGED)
            top, repository = observe()
            initial_git = sealed('initial-git.json', lambda: dict(digest=_digest(repository), repository=repository))
            if not approved or approved['git'] == _digest(None):
                require(_digest(repository) == initial_git['digest'], CHANGED)
        require(top.kind == 'git', CHANGED)
        def prepare_namespace():
            require(not present(root/'.git'/NAMESPACE), 'git-transition-foreign-locator')
            raw = canonical_bytes(locator.payload())
            # An interrupted native atomic create can leave a temporary file.
            # Keep that private directory out of Git and select a clean one.
            for index in range(128):
                directory = area/('new-locator-' + str(index))
                if not present(directory):
                    files.create_directory(directory)
                files.private_directory(directory)
                names = {p.name for p in directory.iterdir()}
                path = directory/'connection.json'
                if not names:
                    files.create(path, raw)
                elif names != {'connection.json'} or files.read(path) != raw:
                    continue
                return dict(name=directory.name, identity=files.directory_identity(directory))
            raise RecordError('git-transition-staging-limit')
        ns = sealed('namespace.json', prepare_namespace)
        stage = area/ns['name']
        dest = root/'.git'/NAMESPACE
        if present(stage):
            require(files.read(stage/'connection.json') == canonical_bytes(locator.payload()) and
                    {p.name for p in stage.iterdir()} == {'connection.json'}, CHANGED)
            publish_repository(files, stage, dest, ns['identity'], asdict(top.common))
            checkpoint('locator-published')
        def verify_namespace():
            require(not present(stage) and files.directory_identity(dest) == ns['identity'] and
                    files.read(dest/'connection.json') == canonical_bytes(locator.payload()), CHANGED)
        verify_namespace()
        port = self._detach_port(authority, dict(project=root))
        with port.exclusion():
            def prepare_retirement():
                change = dict(role='locator', root='project', path=MARKER,
                              before=canonical_bytes(old_binding.locator.payload()), after=None)
                require(port.preview([change]) == plan['retire'], CHANGED)
                return port.prepare('transition-'+uuid.uuid4().hex, [change])
            manifest = sealed('retire.json', prepare_retirement)
            def before_effect():
                live()
                verify_namespace()
            if port.state(manifest, 0) != 'post':
                port.apply(manifest, 0, before_effect=before_effect, event=checkpoint)
            require(port.state(manifest, 0) == 'post', CHANGED)
        checkpoint('plain-locator-retired')
        top, final_repository = observe()
        require(final_repository == repository, CHANGED)
        def verify_publication():
            verify_namespace()
            require(observe() == (top, repository), CHANGED)
        self._publish(store, value, reservation, locator, top, workspace, verify_publication)
        checkpoint('published')
        return result

    def _publish(self, store, value, pending, locator, top, workspace, verify_namespace):
        plan = value['plan']
        operation = value['operation']
        binding = ProjectBinding(locator, 'git', top.common)
        registration = WorkspaceRegistration(workspace.workspace, top.root, top.gitdir)
        new = record('project.binding', dict(locator=locator.payload(), kind='git',
                     location=asdict(top.common), registration_policy='same-project'), {})
        wref = record('workspace.registration', dict(workspace=workspace.workspace, root=asdict(top.root),
                      gitdir=asdict(top.gitdir)), {'project': ('decision', new[0])})
        anchors, objects = Connections(store)._initial_identity(operation, new[0], wref[0], binding,
                                                               registration, primary=True)
        previous = ObjectRef.parse(plan['integration'])
        entries = decode_envelope(previous, store.load(previous)).payload['entries']
        old_marker, = [entry for entry in entries if entry['role'] == 'locator']
        require(old_marker['path'] == MARKER, 'managed-integration-stale')
        entries = [dict(entry, path=GIT_MARKER, owned=b64(canonical_bytes(locator.payload())))
                   if entry is old_marker else entry for entry in entries]
        integration = record('project.integration', dict(entries=entries),
                             {'binding': ('decision', new[0]), 'workspace': ('decision', wref[0])})
        done = _transition(value, 'completed', integration[0], prior=pending)
        changes = {PROJECT_KEY: new[0], workspace_key(workspace.workspace): wref[0],
                   location_key(top.root): wref[0], 'project:integration': integration[0],
                   **anchors, KEY: done[0], PENDING: None}
        original = Connections(store).workspace_record(workspace.workspace)[1]
        if original.root != workspace.root:
            changes[location_key(original.root)] = None
        expected = {key: store.head(key) for key in changes}
        def check(view):
            guard(view, expected_effect=pending)
            from .graph import validate_closure
            from .records import application_registry, operation_closure
            verify_namespace()
            require(not present(Path(top.root.path)/MARKER), CHANGED)
            registry = application_registry()
            validate_closure([done[0], *anchors.values()], view, registry, operation_closure(registry))
            require(view.head(KEY) == pending and view.head('project:integration') == previous
                    and view.head(PROJECT_KEY).as_dict() == plan['binding'], CHANGED)
        store.commit_heads(operation=operation+'-publish', expected=expected, changes=changes,
                           objects=[new, wref, *objects, integration, done], validate=check, _no_active_imports=True)


