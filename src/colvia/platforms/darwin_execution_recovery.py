"""Private native recovery copy, bound to one first-format execution grant.

No restore or cleanup operation is provided here. A partial save remains an
orphan candidate; it cannot be reused as a successful recovery reservation.
"""
import hashlib,json,os,stat
from ..codec import canonical_bytes,require,RecordError
from ..records import link
from ..maps import read_map
from ..bodies import body_bytes
from ..execution.guards import reject_duplicate_keys
from .darwin_effects import _flush


def read_private(directory,name,limit):
    fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=directory)
    try:
        before=os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid() and before.st_mode&0o077==0 and
            before.st_nlink==1 and before.st_size<=limit,'execution-recovery-file')
        signature=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        with os.fdopen(os.dup(fd),'rb') as stream:raw=stream.read(limit+1)
        require(len(raw)==before.st_size and signature(before)==signature(os.fstat(fd))==
            signature(os.stat(name,dir_fd=directory,follow_symlinks=False)),'execution-recovery-drift')
        return raw
    finally:os.close(fd)


def publish_private(directory,name,raw):
    fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=directory)
    try:
        remaining=memoryview(raw)
        while remaining:
            count=os.write(fd,remaining);require(count>0,'execution-recovery-short-write');remaining=remaining[count:]
        _flush(fd)
    finally:os.close(fd)
    os.fsync(directory)

class DarwinExecutionRecovery:
    def __init__(self,journal,observer):
        self.journal=journal;self.observer=observer;self.effects=observer.effects
    def name(self,grant):return 'execution-recovery-'+grant.ref.sha256
    def metadata(self,grant):
        contract=grant.payload['contract'];scope=contract['scope'];output=scope['output_id'];original=scope['documents'][output]['original_identity']
        return dict(output_id=output,recovery_ordinal=contract['recovery_locator']['recovery_ordinal'],
            original_identity=original,original_sha256=original['sha256'],byte_count=original['size'])
    def manifest(self,grant,native):
        return dict(version=1,project=self.journal.store.project,instance=self.journal.store.instance,
            grant=grant.ref.as_dict(),locator=grant.payload['contract']['recovery_locator'],
            stage_identity=native,authority_identity=self.effects.authority_identity,original=self.metadata(grant))
    def save_original(self,grant,history):
        require(self.effects.locked,'effect-lock-required')
        require(history.ready is None and history.pending is None and len(history.completed_refs)==1,'execution-recovery-order')
        metadata=self.metadata(grant);scope=grant.payload['contract']['scope'];path=scope['documents'][scope['output_id']]['path']
        require(self.observer.document(path)==metadata['original_identity'],'execution-document-drift')
        refs=read_map(link(grant,'bodies'),self.journal.store.load)
        raw=b''.join(body_bytes(refs[scope['output_id']],self.journal.store.load))
        require(len(raw)==metadata['byte_count'] and hashlib.sha256(raw).hexdigest()==metadata['original_sha256'],'execution-recovery-body-mismatch')
        with self.effects._stage(self.name(grant),create=True) as (stage,native):
            publish_private(stage,'original.bin',raw)
            publish_private(stage,'manifest.json',canonical_bytes(self.manifest(grant,native)))
            require(self.observer.document(path)==metadata['original_identity'],'execution-document-drift')
            require(read_private(stage,'original.bin',131072)==raw,'execution-recovery-drift')
        return metadata
    def inspect(self,grant,history):
        require(self.effects.locked,'effect-lock-required')
        try:
            with self.effects._stage(self.name(grant)) as (stage,native):
                if history.ready is None:return 'orphan_candidate'
                require(set(os.listdir(stage))=={'manifest.json','original.bin'},'execution-recovery-files')
                encoded=read_private(stage,'manifest.json',8192)
                manifest=json.loads(encoded,object_pairs_hook=reject_duplicate_keys)
                require(canonical_bytes(manifest)==encoded and manifest==self.manifest(grant,native),'execution-recovery-manifest')
                require(history.ready['value']==self.metadata(grant),'execution-recovery-history')
                raw=read_private(stage,'original.bin',131072);expected=manifest['original']
                require(len(raw)==expected['byte_count'] and hashlib.sha256(raw).hexdigest()==expected['original_sha256'],'execution-recovery-body-mismatch')
                return 'present'
        except FileNotFoundError:return 'not_required' if history.ready is None else 'missing'
        except (OSError,ValueError,RecordError):return 'mismatch'
