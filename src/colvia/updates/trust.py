"""Pinned TUF verification adapter; activation is deliberately separate.

The only bootstrap call is explicit creation of an absent trust directory with
an externally pinned root. Existing installations never fall back to bootstrap.
Fixed test clocks belong to the test updater factory, not a user option.
"""
import hashlib,os,stat,sys,time,datetime
from pathlib import Path,PurePosixPath
from urllib.parse import urlsplit
from ..codec import require,RecordError,canonical_bytes,decode_canonical
from ..storage.files import platform_files
from .space import require_space, write_space

PINNED_TUF='7.0.1'
ROLES=('root','timestamp','snapshot','targets')

def _url(value):
    p=urlsplit(value)
    require(p.scheme=='https' and p.hostname and not p.username and not p.password and
            not p.query and not p.fragment,'invalid-update-origin')
    return value.rstrip('/')+'/'

def _target(value):
    require(type(value) is str and 0<len(value)<=512 and value.isascii() and
            not value.startswith('/') and all(part not in ('','.','..') for part in value.split('/')) and
            all(c.isalnum() or c in '-_./' for c in value),'invalid-update-target')
    return value

def updater_factory(**kwargs):
    try:
        import tuf
        from tuf.ngclient import Updater
    except ImportError:raise RecordError('update-verifier-unavailable') from None
    require(tuf.__version__==PINNED_TUF,'update-verifier-version')
    return Updater(**kwargs)

def _versions(updater):
    # This small private API seam is covered against the exact pinned client.
    trusted=updater._trusted_set
    return {role:getattr(trusted,role).version for role in ROLES}

class Trust:
    def __init__(self,root,*,metadata_url,target_url,fetcher,files=None,
                 clock_ns=time.time_ns,factory=updater_factory):
        self.root=Path(root);self.files=files or platform_files()
        require(self.root.is_absolute() and self.root.is_dir() and not self.root.is_symlink(),'trust-store-unavailable')
        for parent in self.root.parents:require(not parent.is_symlink(),'trust-path-symlink')
        self.metadata_url=_url(metadata_url);self.target_url=_url(target_url)
        require(fetcher is not None,'bounded-update-fetcher-required')
        self.fetcher=fetcher;self.clock_ns=clock_ns;self.factory=factory
        self.state()
    def state(self):
        try:raw=self.files.read(self.root/'state.json')
        except FileNotFoundError:raise RecordError('update-trust-repair-required') from None
        s=decode_canonical(raw)
        require(type(s) is dict and set(s)=={'version','anchor_sha256','verified_ns','versions','metadata_url','target_url'} and
                type(s['version']) is int and s['version']==1 and type(s['verified_ns']) is int and s['verified_ns']>=0 and
                type(s['versions']) is dict and set(s['versions'])==set(ROLES) and
                all(type(v) is int and v>=0 for v in s['versions'].values()) and
                s['metadata_url']==self.metadata_url and s['target_url']==self.target_url and
                type(s['anchor_sha256']) is str and len(s['anchor_sha256'])==64 and
                all(c in '0123456789abcdef' for c in s['anchor_sha256']),'invalid-trust-state')
        return raw,s
    @classmethod
    def initialize(cls,root,*,anchor,anchor_sha256,metadata_url,target_url,fetcher,
                   files=None,clock_ns=time.time_ns,factory=updater_factory):
        require(type(anchor) is bytes and len(anchor)<=512*1024 and
                hashlib.sha256(anchor).hexdigest()==anchor_sha256,'bootstrap-anchor-mismatch')
        root=Path(root);files=files or platform_files()
        require(root.is_absolute(),'absolute-trust-path-required')
        for parent in root.parents:require(not parent.is_symlink(),'trust-path-symlink')
        metadata_url=_url(metadata_url);target_url=_url(target_url)
        # Exclusive root creation is the first-install claim. Partial roots are
        # retained for authenticated repair, never erased and retried as new.
        files.create_directory(root);files.create_directory(root/'metadata')
        files.create(root/'update.lock',b'')
        updater=factory(metadata_dir=str(root/'metadata'),metadata_base_url=metadata_url,
                        target_base_url=target_url,fetcher=fetcher,bootstrap=anchor)
        version=updater._trusted_set.root.version
        state=dict(version=1,anchor_sha256=anchor_sha256,verified_ns=0,
                   versions=dict(root=version,timestamp=0,snapshot=0,targets=0),
                   metadata_url=metadata_url,target_url=target_url)
        files.create(root/'state.json',canonical_bytes(state));files.sync_directory(root.parent)
        return cls(root,metadata_url=metadata_url,target_url=target_url,fetcher=fetcher,
                   files=files,clock_ns=clock_ns,factory=factory)
    def stage(self,target,*,destination,max_bytes=512*1024*1024,cancelled=lambda:False,already_present=lambda _:False):
        _target(target);destination=Path(destination)
        require(destination.is_absolute() and not destination.exists(),'update-stage-exists')
        require(type(max_bytes) is int and 0<max_bytes<=2*1024**3,'update-size-limit')
        with self.files.exclusion(self.root/'update.lock'):
            old,state=self.state();now=self.clock_ns()
            require(type(now) is int and now>=state['verified_ns'],'update-clock-rollback')
            require((self.root/'metadata/root.json').is_file(),'update-trust-repair-required')
            updater=self.factory(metadata_dir=str(self.root/'metadata'),metadata_base_url=self.metadata_url,
                target_base_url=self.target_url,fetcher=self.fetcher,bootstrap=None)
            updater.refresh()
            versions=_versions(updater)
            require(all(versions[r]>=state['versions'][r] for r in ROLES),'update-version-rollback')
            state=dict(state,verified_ns=now,versions=versions)
            # Preserve learned monotonic counters before any activation/download.
            self.files.replace(self.root/'state.json',canonical_bytes(state),old)
            info=updater.get_targetinfo(target)
            require(info is not None,'update-target-unavailable')
            require(target in updater._trusted_set.targets.targets,'delegated-update-target-unavailable')
            require(info.length<=max_bytes and 'sha256' in info.hashes,'update-target-limit')
            require(not cancelled(),'update-cancelled')
            for parent in destination.parents:require(not parent.is_symlink(),'update-stage-symlink')
            expiry=min(int(getattr(updater._trusted_set,role).expires.timestamp()*1_000_000_000) for role in ROLES)
            description=dict(path=target,length=info.length,sha256=info.hashes['sha256'],
                custom=info.unrecognized_fields.get('custom'),versions=versions,verified_ns=now,
                expires_ns=expiry,metadata=self.metadata_digests(versions))
            if already_present(description):
                return dict(description,staged=None)
            if sys.platform == 'win32':
                require_space(destination.parent, info.length, 'target-download')
            name=target
            if updater._trusted_set.root.consistent_snapshot:
                parent,sep,base=name.rpartition('/');name=parent+sep+next(iter(info.hashes.values()))+'.'+base
            count=0
            with write_space(destination.parent, 'target-download'):
                with self.files.create_stream(destination) as stream:
                    chunks=iter(self.fetcher.fetch(self.target_url+name))
                    try:
                        for chunk in chunks:
                            require(not cancelled(),'update-cancelled')
                            require(type(chunk) is bytes and len(chunk)<=1024*1024,'update-chunk-limit')
                            count+=len(chunk);require(count<=info.length,'update-target-limit');stream.write(chunk)
                    finally:
                        if hasattr(chunks,'close'):chunks.close()
                    stream.flush();stream.seek(0);info.verify_length_and_hashes(stream)

            # Return a verified staging description, never an installed release.
            return dict(description,staged=str(destination))

    def _read_root_history(self,version,*,current):
        # The exception is tied to verified state, never inferred from filenames
        # or alias identity. Every older/future version retains strict reads.
        require(type(version) is int and version>0 and type(current) is int and current>0,'invalid-root-version')
        relative=Path('root_history')/(str(version)+'.root.json')
        versioned=self.root/'metadata'/relative
        try:
            if version!=current:return self.files.read(versioned,512*1024)
            alias=self.root/'metadata/root.json'
            alias_reader=getattr(self.files,'read_known_alias_pair',None)
            if alias_reader is not None:return alias_reader(versioned,alias,512*1024)
            raw=self.files.read(versioned,512*1024)
            if alias.is_symlink():require(os.readlink(alias)==str(relative),'update-root-cache-changed')
            else:require(self.files.read(alias,512*1024)==raw,'update-root-cache-changed')
            return raw
        except FileNotFoundError:raise RecordError('update-root-cache-unavailable') from None

    def metadata_digests(self,versions):
        result={}
        for role in ROLES:
            if role=='root':raw=self._read_root_history(versions['root'],current=versions['root'])
            else:raw=self.files.read(self.root/'metadata'/(role+'.json'),16*1024*1024)
            result[role]=hashlib.sha256(raw).hexdigest()
        return result

    def activation_check(self,download):
        # Reuse the exact verified metadata, not another network refresh. A new
        # refresh or expired timestamp makes this prepared activation stale.
        with self.files.exclusion(self.root/'update.lock'):
            _,state=self.state();now=self.clock_ns()
            require(type(now) is int and now>=state['verified_ns'],'update-clock-rollback')
            require(download['verified_ns']==state['verified_ns'] and download['versions']==state['versions'],'update-preparation-stale')
            require(type(download['expires_ns']) is int and now<download['expires_ns'],'update-preparation-expired')
            require(set(download['metadata'])==set(ROLES),'update-preparation-invalid')
            require(self.metadata_digests(state['versions'])==download['metadata'],'update-metadata-changed')
            info=self.verified_cached_target(download['path'],state,now)
            require(download['length']==info.length and download['sha256']==info.hashes.get('sha256') and
                    download['custom']==info.unrecognized_fields.get('custom'),'update-prepared-target-changed')


    def verified_cached_target(self,target,state,now):
        """Reauthenticate saved metadata before a recovered preparation activates.

        The versioned root chain starts at the retained externally pinned anchor.
        This uses the pinned TUF verifier, never local cryptographic code, and
        cannot fetch, refresh, advance counters or initialize another root.
        """
        import tuf
        from tuf.ngclient._internal.trusted_metadata_set import TrustedMetadataSet
        from tuf.ngclient.config import EnvelopeType
        require(tuf.__version__==PINNED_TUF,'update-verifier-version')
        _target(target);folder=self.root/'metadata/root_history';candidates=[]
        for path in folder.iterdir():
            require(len(candidates)<10000,'update-root-history-limit')
            parts=path.name.split('.')
            require(len(parts)==3 and parts[0].isdigit() and str(int(parts[0]))==parts[0] and
                    int(parts[0])>0 and parts[1:]==['root','json'],'update-root-history-invalid')
            candidates.append((int(parts[0]),path))
        anchor=None;history={v:p for v,p in candidates}
        for version,path in sorted(candidates):
            raw=self._read_root_history(version,current=state['versions']['root'])
            if hashlib.sha256(raw).hexdigest()==state['anchor_sha256']:
                anchor=(version,raw);break
        require(anchor is not None,'update-anchor-history-unavailable')
        first,raw=anchor;last=state['versions']['root']
        require(first<=last and last-first<10000,'update-root-history-limit')
        trusted=TrustedMetadataSet(raw,EnvelopeType.METADATA)
        trusted.reference_time=datetime.datetime.fromtimestamp(now/1_000_000_000,datetime.timezone.utc)
        require(trusted.root.version==first,'update-root-history-invalid')
        for version in range(first+1,last+1):
            require(version in history,'update-root-history-unavailable')
            trusted.update_root(self._read_root_history(version,current=last))
        trusted.update_timestamp(self.files.read(self.root/'metadata/timestamp.json',16*1024*1024))
        trusted.update_snapshot(self.files.read(self.root/'metadata/snapshot.json',16*1024*1024))
        trusted.update_targets(self.files.read(self.root/'metadata/targets.json',16*1024*1024))
        require({role:getattr(trusted,role).version for role in ROLES}==state['versions'],'update-version-rollback')
        info=trusted.targets.targets.get(target);require(info is not None,'update-target-unavailable')
        return info
