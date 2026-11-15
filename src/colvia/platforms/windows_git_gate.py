"""Journal only our private empty Git gate before its native no-replace move.

The intent is bound to a live integration-state reference, never to age or name
alone. Old operations without this evidence keep their strict refusal behavior.
"""
from pathlib import Path
import re
import uuid
from ..codec import canonical_bytes,decode_canonical,require,ObjectRef
from .git_candidate import absent,digest

EMPTY=digest(b'')
PREFIX='gate-intent-'
FIELDS={'version','operation','manifest','attempt','roots','staged','expected','owner'}


def attempt_valid(value):
    require(type(value) is dict and set(value)=={'head','sequence'},'git-gate-intent-invalid')
    head=ObjectRef.parse(value['head'])
    require(head.kind=='git.integration-state' and head.version==1 and
            type(value['sequence']) is int and 0<value['sequence']<=128,'git-gate-intent-invalid')


def identity_valid(value):
    require(type(value) is list and len(value)==3 and type(value[0]) is int and value[0]>=0 and
            type(value[1]) is str and len(value[1])==32 and all(c in '0123456789abcdef' for c in value[1]) and
            type(value[2]) is int and value[2]>=0,'git-gate-intent-invalid')


def matching(actual,expected):
    return (actual is not None and actual['identity'][:2]==expected['identity'][:2] and
            actual['size']==expected['size']==0 and actual['sha256']==expected['sha256']==EMPTY)


def records(port,m,native):
    area=port.scratch/m['operation'];native.verify_roots();found=[]
    for path in area.iterdir():
        if not path.name.startswith(PREFIX):continue
        suffix=path.name[len(PREFIX):]
        # WindowsFiles.create publishes the final name only after flushing this sibling.
        if re.fullmatch(r'[0-9a-f]{32}\.json\.prepared-[0-9a-f]{32}', suffix):
            continue
        require(len(found)<128,'git-gate-intent-limit')
        require(len(suffix)==37 and suffix.endswith('.json') and
                all(c in '0123456789abcdef' for c in suffix[:-5]),'git-gate-intent-invalid')
        raw=port.files.read(path,16384);value=decode_canonical(raw)
        require(type(value) is dict and set(value)==FIELDS and value['version']==1 and
                value['operation']==m['operation'] and value['manifest']==digest(canonical_bytes(m)) and
                value['roots']==native.roots and value['staged']=='index-lock-'+suffix[:-5],'git-gate-intent-invalid')
        attempt_valid(value['attempt']);expected=value['expected']
        require(type(expected) is dict and set(expected)=={'identity','size','sha256'} and
                expected['size']==0 and expected['sha256']==EMPTY,'git-gate-intent-invalid')
        identity_valid(expected['identity'])
        require(expected['identity'][0]==native.roots[0][0],'git-gate-intent-invalid')
        owner=value['owner']
        require(type(owner) is dict and set(owner)=={'native','pid','birth'} and
                type(owner['pid']) is int and owner['pid']>1 and type(owner['birth']) is str and bool(owner['birth']) and
                owner['native']==dict(scheme='windows-file-id-v1',value=':'.join(str(v) for v in expected['identity'])),
                'git-gate-intent-invalid')
        found.append(value)
    return found


def create(port,m,*,attempt,live):
    attempt_valid(attempt)
    native=port.index_port(m);path=port.lock_path(m);area=port.scratch/m['operation']
    native.verify_roots();live()
    require(absent(path),'git-index-lock-present')
    require(not any(r['attempt']==attempt for r in records(port,m,native)),'git-gate-attempt-already-recorded')
    token=uuid.uuid4().hex;staged=area/('index-lock-'+token)
    port.files.create(staged,b'');expected=native.observe(staged)
    require(expected is not None and matching(expected,expected),'git-index-lock-not-empty')
    owner=port.owner(staged)
    require(owner['native']==dict(scheme='windows-file-id-v1',value=':'.join(str(v) for v in expected['identity'])),
            'git-index-lock-not-owned')
    value=dict(version=1,operation=m['operation'],manifest=digest(canonical_bytes(m)),attempt=attempt,
               roots=native.roots,staged=staged.name,expected=expected,owner=owner)
    raw=canonical_bytes(value);intent=area/(PREFIX+token+'.json')
    live();port.files.create(intent,raw)
    def guard():
        native.verify_roots();live()
        require(port.files.read(intent,16384)==raw,'git-gate-intent-changed')
        require(all(absent(p) for p in port.locks(m)),'git-child-lock-present')
        require(absent(path),'git-index-lock-present')
    observed=port.mover.move(staged,path,expected=expected,before_effect=guard,event=lambda _:None,
                            gate_intent=expected['identity'])
    require(absent(staged) and matching(observed,expected),'git-index-lock-not-owned')
    port.files.sync_directory(path.parent);port.files.sync_directory(area)
    # Confirm the held-handle result; never derive a different owner by reopening.
    require(native.observe(path)==observed and port.files.read(path,1)==b'','git-index-lock-not-owned')
    return dict(owner,native=dict(scheme='windows-file-id-v1',value=':'.join(str(v) for v in observed['identity'])))


def reconcile(port,m,owner,*,attempt,live):
    attempt_valid(attempt);native=port.index_port(m);native.verify_roots();live()
    path=port.lock_path(m)
    if absent(path):return None
    actual=native.observe(path)
    if owner is not None and port.file_id(path)==owner['native']:
        port.owned_lock(m,owner);return None
    eligible=[r for r in records(port,m,native) if r['attempt']==attempt]
    if not eligible:return None  # Legacy owner checks remain authoritative.
    require(len(eligible)==1,'git-gate-intent-ambiguous')
    intent=eligible[0];staged=port.scratch/m['operation']/intent['staged']
    if not absent(staged):return None  # No move proved; a competing lock is not ours.
    require(matching(actual,intent['expected']),'git-gate-foreign-lock')
    port.require_owner_closed(intent['owner'])
    # Reading through the storage primitive also verifies the private gate DACL.
    require(port.files.read(path,1)==b'' and native.observe(path)==actual,'git-gate-foreign-lock')
    native.verify_roots();live()
    port.files.sync_directory(path.parent);port.files.sync_directory(staged.parent)
    require(native.observe(path)==actual,'git-gate-foreign-lock')
    return dict(intent['owner'],native=dict(scheme='windows-file-id-v1',value=':'.join(str(v) for v in actual['identity'])))
