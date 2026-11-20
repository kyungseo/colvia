"""Inventory verification over the Windows native-handle file port.

Manifest modes are logical release metadata on Windows. No POSIX owner/execute
bits stand in for native SID/DACL, reparse, link or file-identity verification.
"""
from pathlib import Path
import hashlib,os
from ..codec import require
from .package import _portable


def verify_inventory(root,expected,manifest_raw,manifest_sha256,files,*,cancelled=lambda:False):
    root=Path(root);a=files.api;expected={e['path']:e for e in expected}
    wanted=set(expected)|{'manifest.json'};stamps={};directories={}
    def enumerate_tree():
        names=[];stack=[root];seen=0
        while stack:
            directory=stack.pop()
            with a.ancestors(directory),a.opened(directory,share=1) as h:
                state=a.state(h,directory);a.private(h)
                require(state['directory'],'slot-directory-not-private')
                relative=directory.relative_to(root).as_posix()
                if relative in directories:require(directories[relative]==state,'slot-directory-changed')
                else:directories[relative]=state
                with os.scandir(directory) as iterator:
                    entries=list(iterator)
                for item in entries:
                    seen+=1;require(seen<=120000,'slot-entry-limit');require(not cancelled(),'observation-cancelled')
                    path=Path(item.path);name=_portable(path.relative_to(root).as_posix())
                    with a.opened(path,share=1) as child:
                        info=a.state(child,path);a.private(child)
                        if info['directory']:stack.append(path)
                        else:
                            require(info['links']==1 and name in wanted,'slot-inventory-mismatch')
                            names.append(name)
                require(a.state(h,directory)==state,'slot-directory-changed')
        require(set(names)==wanted and len(names)==len(wanted),'slot-inventory-mismatch')
    enumerate_tree()
    for name in sorted(wanted):
        expected_size=len(manifest_raw) if name=='manifest.json' else expected[name]['size']
        expected_hash=manifest_sha256 if name=='manifest.json' else expected[name]['sha256']
        path=root/name;digest=hashlib.sha256();count=0
        with a.ancestors(path),a.opened(path,share=1) as h:
            before=a.state(h,path);a.private(h)
            require(not before['directory'] and before['links']==1 and before['size']==expected_size,'slot-inventory-mismatch')
            with files.read_stream(path,expected_size) as stream:
                while raw:=stream.read(1024*1024):
                    require(not cancelled(),'observation-cancelled');count+=len(raw)
                    require(count<=expected_size,'slot-inventory-mismatch');digest.update(raw)
            require(a.state(h,path)==before,'slot-file-changed');stamps[name]=before
        require(count==expected_size and digest.hexdigest()==expected_hash,'slot-inventory-mismatch')
    enumerate_tree()
    for name,before in stamps.items():
        path=root/name
        with a.ancestors(path),a.opened(path,share=1) as h:require(a.state(h,path)==before,'slot-file-changed')


def verify_pinned_inventory(root, expected, manifest_raw, manifest_sha256, files, *, cancelled=lambda: False):
    """Keep files and their directory chain open until their final checks."""
    from contextlib import ExitStack
    class HandleBudget(Exception):
        pass

    checks = {item['path']: (item['size'], item['sha256']) for item in expected}
    checks['manifest.json'] = (len(manifest_raw), manifest_sha256)
    limit = 2048
    api = files.api
    root = Path(root)

    def inspect(stack):
        stack.enter_context(api.ancestors(root))
        opened = []
        directories = []
        found = set()

        def pin(path, access):
            require(not cancelled(), 'observation-cancelled')
            if len(opened) >= limit:
                raise HandleBudget()
            handle = stack.enter_context(api.opened(path, access=access, share=1))
            state = api.state(handle, path)
            api.private(handle)
            opened.append((path, handle, state))
            return handle, state

        _, root_state = pin(root, 0x20080)
        require(root_state['directory'], 'slot-directory-not-private')
        pending = [root]
        while pending:
            directory = pending.pop()
            with os.scandir(directory) as it:
                names = []
                for entry in it:
                    if len(names) >= limit:
                        raise HandleBudget()
                    names.append(entry.name)
                names.sort()
            directories.append((directory, names))
            for name in names:
                path = directory / name
                relative = _portable(path.relative_to(root).as_posix())
                if relative not in checks:
                    _, state = pin(path, 0x20080)
                    require(state['directory'], 'slot-inventory-mismatch')
                    pending.append(path)
                    continue
                handle, state = pin(path, 0x80020000)
                size, wanted = checks[relative]
                require(not state['directory'] and state['links'] == 1 and state['size'] == size, 'slot-inventory-mismatch')
                digest = hashlib.sha256()
                count = 0
                with files._stream_handle(handle) as stream:
                    while chunk := stream.read(1024 * 1024):
                        require(not cancelled(), 'observation-cancelled')
                        count += len(chunk)
                        require(count <= size, 'slot-inventory-mismatch')
                        digest.update(chunk)
                require(count == size and digest.hexdigest() == wanted, 'slot-inventory-mismatch')
                found.add(relative)
        require(found == set(checks), 'slot-inventory-mismatch')
        for directory, names in directories:
            with os.scandir(directory) as it:
                require(sorted(entry.name for entry in it) == names, 'slot-directory-changed')
        for path, handle, before in opened:
            require(not cancelled(), 'observation-cancelled')
            require(api.state(handle, path) == before, 'slot-file-changed')
            api.private(handle)

    try:
        with ExitStack() as stack:
            inspect(stack)
    except HandleBudget:
        return verify_inventory(root, expected, manifest_raw, manifest_sha256, files, cancelled=cancelled)
