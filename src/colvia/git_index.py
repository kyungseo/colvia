"""Bounded Git index v2/v3 codec for separate, approved integration.

The live index is never refreshed. Disposable accelerators are dropped; unknown
representations refuse. Original bytes stay in the integration recovery record.
Specification: https://git-scm.com/docs/index-format
"""
from dataclasses import dataclass,replace
import hashlib,struct
from .codec import RecordError,require
from .tree import logical_path

LIMIT=128*1024*1024
MODES={0o100644,0o100755,0o120000,0o160000}
DISPOSABLE={b'TREE',b'EOIE',b'IEOT',b'FSMN',b'UNTR'}

@dataclass(frozen=True)
class Entry:
    native:bytes
    mode:int
    oid:bytes
    stat:tuple=(0,)*10
    assume:bool=False
    extended:int=0
    @property
    def logical(self):
        try:value=self.native.decode('utf-8')
        except UnicodeError:raise RecordError('git-path-encoding-unavailable') from None
        return logical_path(value)
    @property
    def content(self):return self.mode,self.oid

@dataclass(frozen=True)
class Index:
    algorithm:str
    entries:tuple
    version:int=2
    def by_path(self):return {e.logical:e for e in self.entries}


def _digest(algorithm):
    require(algorithm in ('sha1','sha256'),'unsupported-git-object-format')
    return hashlib.new(algorithm)


def validate_entries(entries,size):
    previous=None;aliases=set();names=set()
    for e in entries:
        require(type(e) is Entry and e.mode in MODES and len(e.oid)==size and any(e.oid),'invalid-index-entry')
        require(type(e.native) is bytes and 0<len(e.native)<=4096 and b'\0' not in e.native,'invalid-index-name')
        path=e.logical;require(previous is None or previous<e.native,'unordered-index')
        require(path.casefold() not in aliases,'index-path-collision')
        require(not any('/'.join(path.casefold().split('/')[:i]) in names for i in range(1,len(path.split('/')))),
                'index-parent-collision')
        require(type(e.assume) is bool and e.extended in (0,0x2000,0x4000,0x6000),'unsupported-index-flags')
        require(len(e.stat)==10 and all(type(n) is int and 0<=n<=0xffffffff for n in e.stat),'invalid-index-stat')
        previous=e.native;aliases.add(path.casefold());names.add(path.casefold())
    require(len(entries)<=1_000_000,'index-entry-limit')


def parse(raw,algorithm='sha1'):
    digest=_digest(algorithm);size=digest.digest_size
    require(type(raw) is bytes and 12+size<=len(raw)<=LIMIT,'invalid-index-size')
    body=raw[:-size];require(hashlib.new(algorithm,body).digest()==raw[-size:],'index-checksum-mismatch')
    sig,version,count=struct.unpack('!4sII',body[:12])
    require(sig==b'DIRC' and version in (2,3) and count<=1_000_000,'unsupported-index-format')
    offset=12;entries=[]
    for _ in range(count):
        start=offset;require(offset+42+size<len(body),'truncated-index')
        stats=struct.unpack('!10I',body[offset:offset+40]);offset+=40
        oid=body[offset:offset+size];offset+=size
        flags=struct.unpack('!H',body[offset:offset+2])[0];offset+=2
        require(flags&0x3000==0,'unmerged-index')
        ext=0
        if flags&0x4000:
            require(version==3 and offset+2<=len(body),'invalid-index-extension-flags')
            ext=struct.unpack('!H',body[offset:offset+2])[0];offset+=2
            require(ext!=0 and ext&~0x6000==0,'unsupported-index-flags')
        end=body.find(b'\0',offset,min(offset+4097,len(body)))
        require(end>=offset,'invalid-index-name')
        name=body[offset:end];require(flags&0xfff==min(len(name),0xfff),'index-name-length-mismatch')
        offset=start+((end-start+1+7)//8)*8
        require(offset<=len(body) and not any(body[end:offset]),'invalid-index-padding')
        entries.append(Entry(name,stats[6],oid,stats,bool(flags&0x8000),ext))
    seen=set()
    while offset<len(body):
        require(offset+8<=len(body),'truncated-index-extension')
        sig,length=struct.unpack('!4sI',body[offset:offset+8]);offset+=8
        require(sig in DISPOSABLE and sig not in seen and offset+length<=len(body),'unsupported-index-extension')
        seen.add(sig);offset+=length
    validate_entries(entries,size)
    return Index(algorithm,tuple(entries),version)


def emit(index):
    size=_digest(index.algorithm).digest_size;entries=tuple(sorted(index.entries,key=lambda e:e.native))
    validate_entries(entries,size);version=3 if any(e.extended for e in entries) else 2
    out=bytearray(struct.pack('!4sII',b'DIRC',version,len(entries)))
    for e in entries:
        stats=list(e.stat);stats[6]=e.mode
        flags=min(len(e.native),0xfff)|(0x8000 if e.assume else 0)|(0x4000 if e.extended else 0)
        raw=struct.pack('!10I',*stats)+e.oid+struct.pack('!H',flags)
        if e.extended:raw+=struct.pack('!H',e.extended)
        raw+=e.native+b'\0';raw+=b'\0'*((-len(raw))%8);out.extend(raw)
    out.extend(hashlib.new(index.algorithm,out).digest());require(len(out)<=LIMIT,'index-size-limit')
    return bytes(out)


def integrate(index,head,selected):
    """I1 keeps unrelated entries; the candidate tree comes from HEAD only.

    head/selected map canonical paths to entries or None for selected deletions.
    A selected partial staging state that is neither HEAD nor accepted refuses.
    """
    current=index.by_path()
    # Rewriting the index changes its timestamp. Retaining an old stat cache
    # can turn racily-clean entries into trusted-clean entries. Preserve content
    # and flags, but invalidate all stat caches (including unrelated entries).
    updated={path:replace(e,stat=(0,)*10) for path,e in current.items()};candidate=dict(head)
    for path,after in selected.items():
        require(logical_path(path)==path,'invalid-index-selection')
        before=head.get(path);staged=current.get(path)
        for e in (before,staged,after):
            require(e is None or e.mode in (0o100644,0o100755),'opaque-git-edit-not-supported')
        require(staged is None or not staged.assume and staged.extended==0,'selected-index-flags-not-supported')
        content=lambda e:None if e is None else e.content
        require(content(staged) in (content(before),content(after)),'selected-partial-staging-conflict')
        if after is None:updated.pop(path,None);candidate.pop(path,None)
        else:
            require(after.logical==path,'index-selection-path-mismatch')
            clean=replace(after,stat=(0,)*10,assume=False,extended=0)
            updated[path]=clean;candidate[path]=clean
    new=Index(index.algorithm,tuple(updated.values()));tree=Index(index.algorithm,tuple(candidate.values()))
    # Validation includes selected-vs-unselected file/directory collisions.
    return emit(new),emit(tree)
