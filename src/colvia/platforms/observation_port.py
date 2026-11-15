"""Select native observation implementations without changing record semantics."""
import sys


def location(path):
    if sys.platform=='win32':
        from .windows_observation import Observer
        return Observer().location(path)
    from .posix import location as native
    return native(path)


def directory_location(path):
    """Persistent location and a live pair from one native observation."""
    if sys.platform=='win32':
        current=location(path)
        return current,(current.volume,current.file_id)
    from .posix import directory_location as native
    return native(path)


def snapshot(root,budget,**options):
    if sys.platform=='win32':
        from .windows_observation import Observer
        return Observer().snapshot(root,budget,**options)
    from .posix import snapshot as native
    options.pop('modes',None)
    return native(root,budget,**options)


def selected(root,paths,*,byte_limit,modes=None):
    if sys.platform=='win32':
        from .windows_observation import Observer
        return Observer().selected(root,paths,byte_limit=byte_limit,modes=modes)
    from .selected import selected as native
    return native(root,paths,byte_limit=byte_limit)


def capture(root,path,expected,store,import_id):
    if sys.platform=='win32':
        from .windows_observation import Observer
        return Observer().capture(root,path,expected,store,import_id)
    from .selected import capture as native
    return native(root,path,expected,store,import_id)


def entry_identity(path):
    if sys.platform=='win32':
        from .windows_observation import Observer
        port=Observer()
        with port.opened(path) as (_,info):return port.identity(info)
    from .posix import identity
    return identity(path.lstat())


def file_stamp(path):
    if sys.platform=='win32':
        from .windows_observation import Observer
        port=Observer()
        with port.opened(path) as (_,info):return port.stamp('',info)
    from .posix import stamp
    return stamp('',path.lstat())
