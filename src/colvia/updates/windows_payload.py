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
