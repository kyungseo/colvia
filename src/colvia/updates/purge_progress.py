"""Publish one purge record under its caller's account or journal lock."""
from contextlib import ExitStack
import os

from ..codec import METADATA_LIMIT, canonical_bytes, decode_canonical, require
from ..platforms.owned_install_files import _info, present
from .purge_inventory import fingerprint


def pending_path(directory, receipt, role):
    return directory / ('.purge-' + receipt + '-' + role + '.pending')


def file_owner(files, path, receipt, stream=None):
    if stream is None:
        identity = _info(files, path)['identity']
    elif hasattr(files, 'api'):
        import msvcrt
        h = msvcrt.get_osfhandle(stream.fileno())
        identity = list(files.api.state(h, path)['identity'])
    else:
        info = os.fstat(stream.fileno())
        birth = getattr(info, 'st_birthtime_ns', round(info.st_birthtime * 1_000_000_000))
        identity = [info.st_dev, info.st_ino, birth]
    return {'receipt': receipt, 'identity': identity}


def read_record(files, path, receipt):
    value = decode_canonical(files.read(path, METADATA_LIMIT))
    require(isinstance(value, dict) and value.pop('_purge_owner', None) == file_owner(files, path, receipt),
            'purge-preparation-changed')
    return canonical_bytes(value)


def publish(files, destination, raw, pending, checkpoint, role, receipt, *, replace=None):
    # A restart can derive the intended bytes before accepting a pending entry.
    # Never glob for old files, truncate an existing file, or infer that an
    # empty/partial file belongs to this operation.
    if not present(pending):
        with files.create_stream(pending) as stream:
            value = decode_canonical(raw)
            value['_purge_owner'] = file_owner(files, pending, receipt, stream)
            stream.write(canonical_bytes(value))
    proof = fingerprint(files, pending)
    require(read_record(files, pending, receipt) == raw, 'purge-preparation-changed')
    checkpoint('publish-' + role)
    require(fingerprint(files, pending) == proof, 'purge-preparation-changed')
    if replace is not None:
        require(read_record(files, destination, receipt) == replace, 'purge-other-operation')
    if hasattr(files, 'api'):
        from ..storage.windows import local_path
        with files.api.ancestors(pending), files.api.ancestors(destination):
            flags = 8 if replace is None else 9
            files.api.ok(files.api.MoveFileExW(local_path(pending), local_path(destination), flags))
    else:
        from ..platforms.exclusive import rename
        with ExitStack() as stack:
            def directory(path):
                fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                stack.callback(os.close, fd)
                return fd
            source = directory(pending.parent)
            target = directory(destination.parent)
            if replace is None:
                rename(source, pending.name, target, destination.name)
            else:
                os.replace(pending.name, destination.name, src_dir_fd=source, dst_dir_fd=target)
    files.sync_directory(destination.parent)
    if destination.parent != pending.parent:
        files.sync_directory(pending.parent)
    require(fingerprint(files, destination) == proof, 'purge-publication-changed')
