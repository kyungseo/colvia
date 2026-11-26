"""Native, disposable Windows check copies. Publication sources are independent."""
import ctypes as C
from contextlib import contextmanager
import hashlib
import shutil
from uuid import uuid4

from .bodies import body_bytes
from .codec import RecordError, require
from .group_records import windows_path


def _streams(api, handle, *, directory):
    # NTFS regular files have one unnamed data stream. Directories have no
    # data stream unless one has been added. Any additional stream refuses.
    raw = C.create_string_buffer(1024)
    if not api.GetFileInformationByHandleEx(handle, 7, raw, len(raw)):
        require(directory and C.get_last_error() == 38, 'group-candidate-streams-unavailable')
        return
    next_offset = int.from_bytes(raw.raw[:4], 'little')
    size = int.from_bytes(raw.raw[4:8], 'little')
    require(not directory and next_offset == 0 and raw.raw[24:24+size] == '::$DATA'.encode('utf-16-le'),
            'group-candidate-unexpected-stream')


def entries(parts):
    files = {}
    directories = {'.'}
    spellings = {}
    for entry in parts[5]:
        require(entry['kind'] == 'regular', 'group-windows-entry-kind-unsupported')
        path = windows_path(entry['path'])
        pieces = path.split('/')
        for length in range(1, len(pieces) + 1):
            name = '/'.join(pieces[:length])
            require(spellings.setdefault(name.casefold(), name) == name, 'path-collision')
            if length < len(pieces):
                directories.add(name)
        files[path] = entry
    require(files.keys().isdisjoint(directories), 'path-collision')
    return files, directories


def _original(port, entry):
    observer = port.observer
    path = observer.resolve_selected(port.root, entry['path'], verify_path=True)
    require(path is not None, 'group-baseline-file-missing')
    with observer.opened(path, read=True) as (handle, state):
        require(not state['directory'] and state['links'] == 1 and state['size'] == entry['size'],
                'group-baseline-content-changed')
        _streams(port.api, handle, directory=False)
        with port.files._stream_handle(handle) as stream:
            while chunk := stream.read(1024*1024):
                yield chunk


def snapshot(port, root, files, directories):
    """Validate exact names, kinds and bytes and return native stamps."""
    stamps = {}
    observer = port.observer

    def visit(path, relative):
        is_directory = relative in directories
        with observer.opened(path, read=not is_directory) as (handle, state):
            require(state['directory'] == is_directory, 'group-candidate-content-changed')
            _streams(port.api, handle, directory=is_directory)
            stamps[relative] = observer.stamp(relative, state)
            if is_directory:
                names = observer.names(path, len(files) + len(directories))
                for name in names:
                    logical = windows_path(name if relative == '.' else relative + '/' + name)
                    require(logical in files or logical in directories, 'group-candidate-content-changed')
                    visit(path / name, logical)
                require(names == observer.names(path, max(1, len(names))), 'group-candidate-content-changed')
            else:
                expected = files[relative]
                require(state['links'] == 1 and state['size'] == expected['size'], 'group-candidate-content-changed')
                observed, _ = observer.regular(path, state, limit=expected['size'], mode=expected['mode'],
                                               cancelled=lambda: False)
                require(observed == {k: v for k, v in expected.items() if k != 'path'},
                        'group-candidate-content-changed')

    visit(root, '.')
    require(stamps.keys() == files.keys() | directories, 'group-candidate-content-changed')
    return stamps


@contextmanager
def disposable_copy(service, port, parts):
    require(port.locked, 'effect-lock-required')
    records, directories = entries(parts)
    parent = service.authority / 'group-checks'
    try:
        port.files.private_directory(parent)
    except FileNotFoundError:
        port.files.create_directory(parent)
    trial = parent / uuid4().hex
    root = trial / 'files'
    scratch = trial / 'scratch'
    for path in (trial, root, scratch):
        port.files.create_directory(path)
    identity = port.files.directory_identity(trial)
    try:
        for name in sorted(directories - {'.'}, key=lambda path: (path.count('/'), path)):
            port.files.create_directory(root / name)
        baseline = {entry['path']: entry for entry in parts[4]}
        bodies = parts[7]
        for name, expected in records.items():
            chunks = body_bytes(bodies[name], service.store.load) if name in bodies else _original(port, baseline[name])
            with port.files.create_stream(root / name) as stream:
                size = 0
                digest = hashlib.sha256()
                for chunk in chunks:
                    size += len(chunk)
                    require(size <= expected['size'], 'group-baseline-content-changed')
                    digest.update(chunk)
                    stream.write(chunk)
                require(size == expected['size'] and digest.hexdigest() == expected['sha256'],
                        'group-baseline-content-changed')
        before = snapshot(port, root, records, directories)
    except OSError as error:
        raise RecordError('group-check-environment-unavailable') from error

    def unchanged():
        try:
            return snapshot(port, root, records, directories) == before
        except (OSError, RecordError):
            return False

    def clean():
        try:
            require(port.files.directory_identity(trial) == identity, 'group-check-directory-changed')
            # On Windows the supported Python versions do not recurse into a
            # junction. The caller has already verified the Job is empty.
            shutil.rmtree(trial)
        except (OSError, RecordError):
            return False
        return True

    yield root, scratch, unchanged, clean
