"""Inventory-bound document asset inspection. Not a dispatcher or a grant.

Only the managed entry supplies a verified manifest under its runtime lease.
No paths from this descriptor are followed; fixed role paths are used instead.
"""
import hashlib,os,stat
from pathlib import Path
from ..codec import RecordError,decode_canonical,require

DESCRIPTOR='execution/assets.json'
ASSETS={'worker':('execution/document-worker.pyz',2*1024*1024),
        'parser':('execution/marked.umd.js',2*1024*1024),
        'parser_license':('execution/marked-LICENSE.md',128*1024),
        'profile':('execution/worker.sb.in',128*1024),
        'runtime_profile':('execution/runtime.sb',128*1024)}


def _namespace(location, expected, files):
    # Readiness is not launch authority. Enumerate only this fixed namespace,
    # through a no-follow directory on POSIX; Windows assets remain absent-only.
    if os.name!='posix':
        require(not expected and not files.exists(location/'execution'),'document-assets-invalid')
        return
    from ..platforms.posix import open_directory
    root=open_directory(location)
    try:
        aliases=[]
        with os.scandir(root) as entries:
            for count,entry in enumerate(entries):
                require(count<4096,'document-assets-invalid')
                if entry.name.casefold()=='execution':aliases.append(entry.name)
        require(aliases in ([],['execution']),'document-assets-invalid')
        if not aliases:
            require(not expected,'document-assets-changed');return
        require(bool(expected),'document-assets-invalid')
        try:directory=os.open('execution',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=root)
        except PermissionError:raise
        except OSError as exc:raise RecordError('document-assets-invalid') from exc
        try:
            before=os.fstat(directory);names=set()
            with os.scandir(directory) as entries:
                for count,entry in enumerate(entries):
                    require(count<len(expected),'document-assets-invalid')
                    require(entry.name in expected,'document-assets-invalid')
                    info=entry.stat(follow_symlinks=False)
                    require(stat.S_ISREG(info.st_mode) and info.st_nlink==1,'document-assets-changed')
                    names.add(entry.name)
            require(names==expected,'document-assets-changed')
            signature=lambda v:(v.st_dev,v.st_ino,v.st_mode,v.st_mtime_ns,v.st_ctime_ns)
            require(signature(before)==signature(os.fstat(directory))==signature(os.stat('execution',dir_fd=root,follow_symlinks=False)),'document-assets-changed')
        finally:os.close(directory)
    finally:os.close(root)

def inspect_assets(location,manifest,files,*,platform):
    location=Path(location)
    require((manifest['os'],manifest['architecture'])==platform,'document-assets-platform')
    rows=[r for r in manifest['inventory'] if r['path'].casefold()=='execution' or r['path'].casefold().startswith('execution/')]
    result=dict(kind='execution-readiness',state='absent',dispatch_available=False,
                reason='assets-not-packaged' if platform==('macos','arm64') else 'platform-dispatch-unavailable')
    if not rows:
        _namespace(location,set(),files);return result
    require(platform==('macos','arm64'),'document-assets-platform')
    expected={DESCRIPTOR,*[v[0] for v in ASSETS.values()]}
    require(len(rows)==len(expected) and {r['path'] for r in rows}==expected,'document-assets-invalid')
    _namespace(location,{Path(p).name for p in expected},files)
    indexed={r['path']:r for r in rows}
    def read(path,limit):
        row=indexed[path]
        require(row['kind']=='regular' and row['mode']=='100644' and type(row['size']) is int and 0<row['size']<=limit,'document-assets-invalid')
        try:
            if path==DESCRIPTOR:raw=files.read(location/path,limit)
            else:
                parts=[];size=0
                with files.read_stream(location/path,row['size']) as stream:
                    while chunk:=stream.read(65536):
                        size+=len(chunk);require(size<=row['size'],'document-assets-changed');parts.append(chunk)
                raw=b''.join(parts)
            require(stat.S_IMODE((location/path).lstat().st_mode)&0o111==0,'document-assets-changed')
        except PermissionError:raise
        except (OSError,RecordError,ValueError,TypeError) as exc:raise RecordError('document-assets-changed') from exc
        require(len(raw)==row['size'] and hashlib.sha256(raw).hexdigest()==row['sha256'],'document-assets-changed')
        return raw
    try:descriptor=decode_canonical(read(DESCRIPTOR,65536))
    except RecordError as exc:
        if exc.code.startswith('document-assets-'):raise
        raise RecordError('document-assets-invalid') from exc
    except (ValueError,TypeError) as exc:raise RecordError('document-assets-invalid') from exc
    require(type(descriptor) is dict and set(descriptor)=={'version','os','architecture','resources'} and
            type(descriptor['version']) is int and descriptor['version']==1 and
            (descriptor['os'],descriptor['architecture'])==platform,'document-assets-invalid')
    resources=descriptor['resources']
    require(type(resources) is dict and set(resources)==set(ASSETS),'document-assets-invalid')
    for role,(path,limit) in ASSETS.items():
        row=indexed[path];value=resources[role]
        require(type(value) is dict and type(value.get('size')) is int and value=={key:row[key] for key in ('path','size','sha256','mode')},'document-assets-invalid')
        read(path,limit)
    return dict(result,state='prepared-dispatch-unavailable',assets_verified=True,reason='managed-host-dispatch-unavailable')
