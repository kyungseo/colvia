"""Stage a signed, normalized regular-file ZIP in a fresh immutable slot.

This is a source packaging format, not an extractor for arbitrary upstream Python
archives. A release builder must normalize those archives before signing. Target
identity and manifest identity come from verified TUF custom metadata. Staging
never activates a slot, changes PATH, installs an app or runs its interpreter.
"""
import hashlib,os,re,stat,zipfile
from pathlib import Path
from ..codec import require,decode_canonical
from ..tree import logical_path,canonical_entries
from ..storage.sqlite import _token
from ..storage.files import platform_files
from ..worker_state import path_namespace
from .slots import verify_slot
from .space import STAGING_ALLOWANCE, require_space, write_space


def descriptor(custom,*,channel,os_name,architecture):
    require(type(custom) is dict and set(custom)=={'colvia'},'release-descriptor-required')
    d=custom['colvia']
    require(type(d) is dict and set(d)=={'version','channel','os','architecture','release','sequence','manifest_sha256'} and
            type(d['version']) is int and d['version']==1 and type(d['sequence']) is int and d['sequence']>=1,
            'invalid-release-descriptor')
    for v in (channel,d['channel'],d['release']):_token(v)
    require((d['channel'],d['os'],d['architecture'])==(channel,os_name,architecture),'release-descriptor-mismatch')
    require(type(d['manifest_sha256']) is str and re.fullmatch('[0-9a-f]{64}',d['manifest_sha256']),'release-manifest-identity')
    return dict(d)


def _portable(path):
    require(logical_path(path)==path,'package-path-noncanonical')
    # One portable release namespace; Windows aliases/ADS are refused on macOS too.
    for p in path.split('/'):
        require(not p.endswith((' ','.')) and not any(c in p for c in ':<>"|?*') and
                p.split('.')[0].upper() not in {'CON','PRN','AUX','NUL',*[f'COM{i}' for i in range(1,10)],*[f'LPT{i}' for i in range(1,10)]},
                'package-path-unportable')
    return path


def stage_archive(archive,*,root,slot,target,channel,os_name,architecture,files=None,cancelled=lambda:False):
    """Target is the trusted downloader result; recheck its bytes on the held fd."""
    _token(slot);archive=Path(archive);root=Path(root);files=files or platform_files()
    require(type(target) is dict and type(target.get('length')) is int and 0<target['length']<=2*1024**3 and
            type(target.get('sha256')) is str and re.fullmatch('[0-9a-f]{64}',target['sha256']),'invalid-package-target')
    d=descriptor(target.get('custom'),channel=channel,os_name=os_name,architecture=architecture)
    for p in (archive,*archive.parents,root,*root.parents,root/'slots'):require(not p.is_symlink(),'package-path-symlink')
    files.private_directory(root)
    require(archive.is_absolute() and root.is_absolute() and (root/'slots').is_dir(),'package-parent-required')
    destination=root/'slots'/slot;require(not destination.exists(),'package-slot-exists')
    with files.read_stream(archive,2*1024**3) as source:
        before=os.fstat(source.fileno());require(stat.S_ISREG(before.st_mode) and before.st_size==target['length'],'package-file-mismatch')
        digest=hashlib.sha256()
        while raw:=source.read(1024*1024):
            require(not cancelled(),'package-cancelled');digest.update(raw)
        require(digest.hexdigest()==target['sha256'],'package-digest-mismatch');source.seek(0)
        with zipfile.ZipFile(source) as bundle:
            items=bundle.infolist();require(0<len(items)<=100001,'package-entry-limit');names=[];total=0
            for item in items:
                require(not item.is_dir() and not item.flag_bits&1 and item.compress_type in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED) and not item.extra,
                        'package-entry-unsupported')
                require(item.orig_filename==item.filename,'package-path-truncated')
                mode=item.external_attr>>16
                require(stat.S_IFMT(mode) in (0,stat.S_IFREG) and not mode&0o7000,'package-entry-not-regular')
                names.append(_portable(item.filename));total+=item.file_size
                require(0<=item.file_size<=1024**3 and total<=4*1024**3,'package-size-limit')
            require(len(names)==len(set(names)) and 'manifest.json' in names,'package-duplicate-or-missing-manifest')
            path_namespace(names)
            manifest_info=bundle.getinfo('manifest.json');require(manifest_info.file_size<=4*1024**2,'package-manifest-limit')
            manifest_raw=bundle.read(manifest_info)
            require(hashlib.sha256(manifest_raw).hexdigest()==d['manifest_sha256'],'package-manifest-mismatch')
            manifest=decode_canonical(manifest_raw);require(type(manifest) is dict and 'inventory' in manifest,'invalid-slot-manifest')
            inventory=canonical_entries(manifest['inventory']);indexed={e['path']:e for e in inventory}
            require(all(e['kind']=='regular' for e in inventory) and set(names)==set(indexed)|{'manifest.json'},'package-inventory-mismatch')
            require(all(manifest.get(k)==d[k] for k in ('release','sequence','os','architecture')),'package-release-mismatch')
            require_space(root/'slots', total + STAGING_ALLOWANCE, 'slot-expand', code='package-space-unavailable')
            with write_space(root/'slots', 'slot-expand'):
                files.create_directory(destination)
                for item in items:
                    require(not cancelled(),'package-cancelled');path=destination/item.filename
                    parent=destination
                    for part in item.filename.split('/')[:-1]:
                        parent=parent/part
                        try:files.create_directory(parent)
                        except FileExistsError:files.private_directory(parent)
                    expected=None if item.filename=='manifest.json' else indexed[item.filename]
                    size=len(manifest_raw) if expected is None else expected['size'];sha=d['manifest_sha256'] if expected is None else expected['sha256']
                    require(item.file_size==size,'package-file-length-mismatch')
                    count=0;h=hashlib.sha256()
                    with files.create_stream(path,executable=expected is not None and expected['mode']=='100755') as output:
                        with bundle.open(item) as incoming:
                            while raw:=incoming.read(1024*1024):
                                require(not cancelled(),'package-cancelled');count+=len(raw);require(count<=size,'package-file-length-mismatch');h.update(raw)
                                view=memoryview(raw)
                                while view:
                                    written=output.write(view);require(written>0,'package-short-write');view=view[written:]
                        require(count==size and h.hexdigest()==sha,'package-content-mismatch')

    verified=verify_slot(root,slot,d['manifest_sha256'],os_name=os_name,architecture=architecture,files=files,cancelled=cancelled)
    return verified
