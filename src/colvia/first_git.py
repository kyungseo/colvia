"""Create an empty repository only as part of an approved first connection."""
from configparser import ConfigParser, Error as ConfigError
from dataclasses import asdict
from pathlib import Path
import os
import uuid
import time

from .adapters.git import read_file
from .binding import NativeLocation
from .storage.sqlite import _token
from .git_registration import _registration_plan, _REVIEW_SECONDS, register_locked
from .managed_entry import configured_git
from .codec import canonical_bytes, decode_canonical, require
from .platforms.observation_port import location
from .platforms.owned_install_files import capture, move, present
from .platforms.process import run
from .project_setup import sha
from .storage.authority import Authority

_LIMIT = 8 * 1024 * 1024


def reservation_path(home, native):
    identity = canonical_bytes([native.volume, native.file_id])
    return home.root / ('first-git-' + sha(identity) + '.json')


def check_reservation(home, native, operation):
    path = reservation_path(home, native)
    if home.files.exists(path):
        require(operation is not None and home.files.read(path) == canonical_bytes(operation),
                'first-git-connection-pending')


def tool_identity(setup):
    require(setup.git is not None, 'git-prerequisite-required')
    return dict(path=str(setup.git.executable), sha256=setup.git.sha256, version=setup.git.version)


def unavailable_reason(home, basis):
    root = Path(basis['root'])
    if basis['topology']['root']['volume'] != location(home.root).volume:
        return 'effect-staging-volume-mismatch'
    if root.is_relative_to(home.root) or home.root.is_relative_to(root):
        return 'effect-staging-overlaps-workspace'
    return None


def git_preview(setup, plain, *, executable=None, expires_at=None):
    basis = plain['plan']
    require(basis['topology']['kind'] == 'plain', 'first-git-unconnected-folder-required')
    reason = unavailable_reason(setup.home, basis)
    require(reason is None, reason)
    registration = None
    question = '등록한 Git으로 빈 main 브랜치를 만들고 이 폴더를 연결할까요?'
    if executable is None:
        git = tool_identity(setup)
    else:
        require(setup.git is None and setup.runtime_lease is not None, 'first-git-use-registration')
        now = int(time.time())
        expiry = now + _REVIEW_SECONDS if expires_at is None else expires_at
        require(type(expiry) is int and 0 < expiry-now <= _REVIEW_SECONDS, 'git-registration-review-changed')
        registration, _, previous, _ = _registration_plan(setup.home,setup.runtime_lease,executable,expiry)
        require(previous is None, 'git-registration-replacement-required')
        git = dict(path=registration['executable'], sha256=registration['sha256'])
        question = '선택한 Git을 이 계정에 등록하고, 빈 main 브랜치를 만들어 이 폴더를 연결할까요? 등록이 끝나면 연결을 중단해도 계정에 남습니다.'
    plan = dict(action='first-connect-git', branch='main', git=git, registration=registration, basis=basis)
    paths = [c['path'] for c in basis['changes'] if c['role'] != 'locator']
    return dict(plan=plan, receipt=sha(canonical_bytes(plan)),
                files=['.git/', *paths, '.git/colvia/connection.json'],
                question=question+' 기존 자료는 스테이징하지 않습니다.')


def project_plan(setup, basis, operation):
    return setup._plan(basis['root'], basis['project'], basis['instance'], basis['workspace'],
                       basis['nonce'], reservation=operation)


def begin(setup, operation, plan, receipt, statement):
    basis = plan['basis']
    if setup.runtime_lease is not None:
        setup.git = configured_git(setup.home)
    registration = plan.get('registration')
    actual = git_preview(setup, dict(plan=project_plan(setup, basis, None)),
                         executable=registration['executable'] if registration else None,
                         expires_at=registration['expires_at'] if registration else None)
    require(actual['receipt'] == receipt, 'connect-review-changed')
    area = setup.home.root / 'operations' / operation
    files = setup.home.files
    files.create_directory(area)
    files.create(area/'first-git.json', canonical_bytes(dict(plan=plan, receipt=receipt, statement=statement)))
    native = NativeLocation(**basis['topology']['root'])
    files.create(reservation_path(setup.home, native), canonical_bytes(operation))
    return dict(operation=operation, state='pending', project=basis['project'])


def read_request(files, area):
    request = decode_canonical(files.read(area/'first-git.json', _LIMIT))
    plan = request['plan']
    require(plan['action'] == 'first-connect-git' and sha(canonical_bytes(plan)) == request['receipt'],
            'connect-journal-changed')
    return request


def cancel(setup, operation):
    # Cancellation releases only this operation's reservation. Neither account
    # settings nor anything in the project directory is rolled back.
    _token(operation)
    with setup.management():
        files = setup.home.files
        area = setup.home.root/'operations'/operation
        request = read_request(files, area)
        basis = request['plan']['basis']
        marker = area/'cancelled.json'
        if not present(marker):
            require(not present(setup.home.root/'authorities'/basis['project'])
                    and not present(area/'completed.json'), 'first-git-cancel-too-late')
            files.create(marker, canonical_bytes(dict(operation=operation, receipt=request['receipt'])))
        release_reservation(setup.home, basis, operation)
        return dict(operation=operation, state='cancelled', project=basis['project'])


def release_reservation(home, basis, operation):
    native = NativeLocation(**basis['topology']['root'])
    path = reservation_path(home, native)
    ticket = canonical_bytes(operation)
    if present(path) and home.files.read(path) == ticket:
        home.files.remove(path, ticket)


# With an empty template Git creates HEAD, config, and six empty administration directories.
_LAYOUT = {'': {'HEAD','config','objects','refs'}, 'objects': {'info','pack'},
           'refs': {'heads','tags'}, 'objects/info': set(), 'objects/pack': set(),
           'refs/heads': set(), 'refs/tags': set()}


def empty_repository(path, *, integrating=False):
    for rel, expected in _LAYOUT.items():
        directory = path / rel
        location(directory)
        missing = expected.copy()
        for entry in directory.iterdir():
            if integrating and not rel and entry.name == 'colvia':
                continue
            require(entry.name in missing, 'first-git-repository-changed')
            missing.remove(entry.name)
        require(not missing, 'first-git-repository-changed')
    head = read_file(path/'HEAD', 128)
    require(head.rstrip(b'\r\n') == b'ref: refs/heads/main', 'first-git-repository-changed')
    raw = read_file(path/'config', 4096)
    parser = ConfigParser(interpolation=None, strict=True)
    try:
        parser.read_string(raw.decode('ascii'))
        core = dict(parser['core'])
    except (ValueError, KeyError, UnicodeError, ConfigError):
        core = {}
    allowed = {'filemode','logallrefupdates','ignorecase','precomposeunicode','symlinks','bare'}
    require(not parser.defaults() and parser.sections() == ['core'] and core.pop('repositoryformatversion', None) == '0'
            and core.get('bare') == 'false' and set(core) <= allowed
            and all(value in ('true','false') for value in core.values()), 'first-git-repository-changed')
    return sha(canonical_bytes([sha(head),sha(raw)]))


def publish_repository(files, source, target, identity, expected_root):
    """Rename no-replace on the qualified volume, with the destination directory pinned."""
    if hasattr(files, 'api'):
        from .platforms.windows_rename import RenameAPI
        api = RenameAPI()
        with api.ancestors(source), api.ancestors(target), api.opened(target.parent):
            require(asdict(location(target.parent)) == expected_root, 'connect-topology-changed')
            with api.opened(source, access=0x10080, share=1) as handle:
                state = api.state(handle,source)
                require(state['directory'] and list(state['identity']) == identity, 'first-git-repository-changed')
                api.rename(handle,target)
        files.sync_directory(target.parent)
        files.sync_directory(source.parent)
    else:
        from .platforms.posix import open_directory, descriptor_location
        from .platforms.exclusive import rename
        left = open_directory(source.parent)
        try:
            right = open_directory(target.parent)
            try:
                require(asdict(descriptor_location(target.parent,right)[0]) == expected_root, 'connect-topology-changed')
                st = os.stat(source.name, dir_fd=left, follow_symlinks=False)
                require([st.st_dev,st.st_ino] == identity, 'first-git-repository-changed')
                rename(left,source.name,right,target.name)
            finally:
                os.close(right)
        finally:
            os.close(left)


def seed_repository(setup, area):
    files = setup.home.files
    seed = area / ('seed-' + uuid.uuid4().hex)
    files.create_directory(seed)
    files.create_directory(seed/'.git')
    env = {key:value for key,value in setup.git.env.items() if not key.upper().startswith('GIT_')}
    env.update(HOME=str(seed), USERPROFILE=str(seed), XDG_CONFIG_HOME=str(seed), GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_SYSTEM=os.devnull, GIT_CONFIG_GLOBAL=os.devnull,
               GIT_TERMINAL_PROMPT='0', LC_ALL='C')
    with setup.git.guard_executable():
        result = run([str(setup.git.executable), '-c', 'core.hooksPath='+os.devnull,
                      '-c','init.defaultBranch=main','init','--quiet','--template=','.'],
                     cwd=seed, env=env, output_limit=8192)
    require(result.code == 0, 'first-git-init-incomplete')
    repo = seed/'.git'
    # Older Git can ignore init.defaultBranch. Normalize only this new private
    # repository's unborn HEAD, before sealing it or exposing it to the project.
    head = read_file(repo/'HEAD', 128)
    if head.rstrip(b'\r\n') != b'ref: refs/heads/main':
        require(head.startswith(b'ref: refs/heads/'), 'first-git-repository-changed')
        files.replace(repo/'HEAD', b'ref: refs/heads/main\n', head)
    return dict(seed=seed.name, identity=files.directory_identity(repo), digest=empty_repository(repo))


def prepare_repository(setup, area, plan, event):
    files = setup.home.files
    basis = plan['basis']
    root = Path(basis['root'])
    destination = root/'.git'
    seal = area/'repository.json'
    if not files.exists(seal):
        require(not os.path.lexists(destination), 'first-git-repository-changed')
        prepared = seed_repository(setup, area)
        files.create(seal, canonical_bytes(prepared))
        event('first-git-prepared')
    prepared = decode_canonical(files.read(seal))
    stage = area/prepared['seed']/'.git'
    identity = prepared['identity']
    if not os.path.lexists(destination):
        require(files.directory_identity(stage) == identity and empty_repository(stage) == prepared['digest'],
                'first-git-repository-changed')
        require(canonical_bytes(project_plan(setup,basis,area.name)) == canonical_bytes(basis),
                'connect-review-changed')
        publish_repository(files, stage, destination, identity, basis['topology']['root'])
        event('first-git-published')
    require(not os.path.lexists(stage) and files.directory_identity(destination) == identity
            and empty_repository(destination, integrating=os.path.lexists(area/'connect.json')) == prepared['digest'],
            'first-git-repository-changed')


def prepare_authority(setup, area, plan, operation, statement, event):
    files = setup.home.files
    target = setup.home.root/'authorities'/plan['project']
    if not os.path.lexists(target):
        current = project_plan(setup, plan, operation)
        require(canonical_bytes(current) == canonical_bytes(plan), 'connect-review-changed')
        # Publish a complete authority. An interrupted build remains private to this operation.
        stage = area / ('authority-' + uuid.uuid4().hex)
        candidate = Authority.create(stage, project=plan['project'], instance=plan['instance'], generation='initial', files=files)
        # No external files are applied until the fully prepared authority is published.
        setup._prepare_connection(candidate,plan,operation,statement)
        event('first-git-authority-prepared')
        move(files, stage, target, capture(files, stage), verified_tree=True)
    authority = setup.home.authority(plan['project'])
    require(authority.pointer_value()['instance'] == plan['instance'], 'connect-authority-changed')
    return authority


def resume(setup, area, operation, event):
    files = setup.home.files
    request = read_request(files, area)
    plan = request['plan']
    basis = plan['basis']
    if present(area/'cancelled.json'):
        release_reservation(setup.home, basis, operation)
        require(False, 'first-git-cancelled')
    root = Path(basis['root'])
    native = location(root)
    require(asdict(native) == basis['topology']['root'], 'connect-topology-changed')
    reservation = reservation_path(setup.home, native)
    ticket = canonical_bytes(operation)
    if files.exists(area/'completed.json'):
        release_reservation(setup.home, basis, operation)
        return dict(operation=operation, state='connected', project=basis['project'])
    if not files.exists(reservation):
        require(not os.path.lexists(root/'.git') and
                sha(canonical_bytes(project_plan(setup, basis, None))) == sha(canonical_bytes(basis)),
                'connect-review-changed')
        files.create(reservation, ticket)
    check_reservation(setup.home, native, operation)
    if not os.path.lexists(root/'.git'):
        require(canonical_bytes(project_plan(setup, basis, operation)) == canonical_bytes(basis),
                'connect-review-changed')
    if setup.runtime_lease is not None:
        setup.git = configured_git(setup.home)
    registration = plan['registration']
    if registration and setup.git is None:
        require(not files.exists(area/'registration.json'), 'managed-git-changed')
        register_locked(setup.home,setup.runtime_lease,registration,sha(canonical_bytes(registration)),approved=True)
        setup.git = configured_git(setup.home)
    selected = tool_identity(setup)
    require(all(selected.get(k)==v for k,v in plan['git'].items()), 'managed-git-changed')
    if registration and not files.exists(area/'registration.json'):
        files.create(area/'registration.json',canonical_bytes(selected))
        event('first-git-registered')
    journal = area/'connect.json'
    authority_path = setup.home.root/'authorities'/basis['project']
    if present(journal) and present(authority_path):
        # The connection owns its ordered effects now. Git clients may already
        # have staged unrelated files; preserve them and recheck native identity.
        sealed = decode_canonical(files.read(area/'repository.json'))
        require(files.directory_identity(root/'.git') == sealed['identity'],
                'first-git-repository-changed')
    else:
        prepare_repository(setup, area, plan, event)
    if not os.path.lexists(journal):
        git_plan = project_plan(setup, basis, operation)
        require(git_plan['topology']['kind'] == 'git' and git_plan['locator_root'] == str(root/'.git')
                and git_plan['changes'][:-1] == basis['changes'][:-1]
                and git_plan['entry'] == basis['entry'], 'connect-review-changed')
        files.create(journal, canonical_bytes(dict(version=1, operation=operation, plan=git_plan,
                     receipt=sha(canonical_bytes(git_plan)), statement=request['statement'])))
        event('first-git-connect-planned')
    record = decode_canonical(files.read(journal, _LIMIT))
    require(record['operation'] == operation and sha(canonical_bytes(record['plan'])) == record['receipt'],
            'connect-journal-changed')
    prepare_authority(setup, area, record['plan'], operation, request['statement'], event)
    event('first-git-authority-ready')
    result = setup._resume_locked(operation, event=event)
    if result['state'] == 'connected':
        event('first-git-files-connected')
        files.create(area/'completed.json', canonical_bytes(dict(project=basis['project'])))
        release_reservation(setup.home, basis, operation)
    return result
