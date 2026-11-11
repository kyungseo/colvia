"""Retained preparation attempts; a pending marker selects exactly one area.

Unpublished staging never changes live files. Interrupted areas remain evidence;
a fresh area is permitted only after the caller checks the unchanged live input.
"""
import uuid
from ..codec import canonical_bytes,decode_canonical,require


def pending_area(files,pending,operations,base,operation,target):
    raw=files.read(pending);value=decode_canonical(raw)
    require(type(value) is dict and set(value)=={'version','operation','target','area'} and
            type(value['version']) is int and value['version']==1 and value['operation']==operation and
            value['target']==target,'file-update-pending-mismatch')
    name=value['area']
    require(type(name) is str and (name==base or
        (name.startswith(base+'-') and len(name)==len(base)+33 and
         all(c in '0123456789abcdef' for c in name[len(base)+1:]))),'file-update-area-invalid')
    area=operations/name;files.private_directory(area)
    return area,raw


def fresh_area(files,operations,base,operation,target):
    area=operations/base
    # No rename/delete of an interrupted attempt, and no reuse of partial bytes.
    if area.exists():area=operations/(base+'-'+uuid.uuid4().hex)
    files.create_directory(area)
    return area,canonical_bytes(dict(version=1,operation=operation,target=target,area=area.name))
