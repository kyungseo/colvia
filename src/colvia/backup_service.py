"""Pinned logical backup publication with no activation or result acceptance.

The qualified native no-replace primitive publishes a fresh user-selected file.
The last-export receipt is local lifecycle metadata, not a semantic history edit.
Interrupted attempts remain uniquely named diagnostic files until their owner
can safely clean them; they never replace an earlier verified backup.
"""
import os,stat,time,uuid,sys
from pathlib import Path
from .backup import ExportReader,ExportBudget,write_export,audit_requirements,_header,MAGIC
from .codec import RecordError,canonical_bytes,require
from .graph import GraphAudit
from .platforms import exclusive
from .platforms.posix import open_directory
from .storage.sqlite import _token


def _signature(info):
    return info.st_dev,info.st_ino,info.st_mode,info.st_nlink,info.st_size,info.st_mtime_ns,info.st_ctime_ns


def export_size(project,audit):
    header=canonical_bytes(_header(project,audit.root,**audit_requirements(audit)))
    count=len(MAGIC)+4+len(header)
    for ref in audit.refs():count+=5+len(canonical_bytes(ref.as_dict()))+ref.byte_length
    # Exact frame body cost plus conservative bounded final manifest reserve.
    return count+1024


def _verify(directory,name,*,root,audit,byte_limit,cancelled):
    fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=directory)
    try:
        info=os.fstat(fd)
        require(stat.S_ISREG(info.st_mode) and info.st_nlink==1,'backup-file-identity')
        with os.fdopen(os.dup(fd),'rb') as stream:
            reader=ExportReader(stream,ExportBudget(audit.count,byte_limit))
            require(reader.root==root,'backup-root-mismatch')
            expected=iter(audit.refs());count=0
            for ref,_ in reader.objects():
                require(not cancelled(),'export-cancelled')
                require(ref==next(expected,None),'backup-object-mismatch');count+=1
            require(reader.complete and count==audit.count and next(expected,None) is None,'backup-incomplete')
        require(_signature(info)==_signature(os.fstat(fd))==_signature(os.stat(name,dir_fd=directory,follow_symlinks=False)),
                'backup-file-changed')
        return reader.manifest,info
    finally:os.close(fd)


def export_backup(authority,*,destination,scratch,operation,graph_budget,registry,cancelled=lambda:False,
                  checkpoint=lambda phase:None):
    """Returns publication and receipt status separately after an uncertain tail.

    A returned publication is exact readable-after-flush evidence, not proof of
    the storage medium, continued availability, off-device location or secrecy.
    """
    if sys.platform=='win32':
        from .windows_backup import export_backup as native_export
        return native_export(authority,destination=destination,scratch=scratch,operation=operation,graph_budget=graph_budget,
                             registry=registry,cancelled=cancelled,checkpoint=checkpoint)
    from .platforms.darwin_effects import _flush
    _token(operation);destination=Path(destination);scratch=Path(scratch)
    require(exclusive.available(),'backup-publication-platform-unavailable')
    require(destination.is_absolute() and destination.name not in ('','.','..'),'backup-destination-required')
    require(scratch.is_absolute() and scratch.is_dir(),'backup-scratch-required')
    directory=open_directory(destination.parent);audit=None;store=None
    prepared='.colvia-export-'+operation+'-'+uuid.uuid4().hex
    try:
        try:os.stat(destination.name,dir_fd=directory,follow_symlinks=False)
        except FileNotFoundError:pass
        else:raise RecordError('backup-destination-exists')
        store=authority.store(readonly=True);pinned=store.root().ref
        audit=GraphAudit(scratch/(operation+'-audit.sqlite3'),graph_budget)
        audit.run(pinned,store.load,registry,cancelled=cancelled,require_known=True)
        estimate=export_size(store.project,audit)
        space=os.fstatvfs(directory)
        require(space.f_bavail*space.f_frsize>=estimate,'backup-insufficient-space')
        fd=os.open(prepared,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=directory)
        with os.fdopen(fd,'wb') as stream:
            manifest=write_export(stream,project=store.project,audit=audit,load=store.load,cancelled=cancelled)
            stream.flush();_flush(stream.fileno())
        checkpoint('flushed')
        checked,info=_verify(directory,prepared,root=pinned,audit=audit,byte_limit=estimate,cancelled=cancelled)
        require(checked==manifest,'backup-manifest-mismatch')
        checkpoint('verified')
        require(not cancelled(),'export-cancelled')
        # This also checks active generation/fence, without demanding the latest
        # root still equals the pinned historical snapshot.
        store.root()
        require(_signature(info)==_signature(os.stat(prepared,dir_fd=directory,follow_symlinks=False)),'backup-file-changed')
        exclusive.rename(directory,prepared,directory,destination.name)
        # Directory pathname still refers to the same opened destination.
        current=open_directory(destination.parent)
        try:require((os.fstat(current).st_dev,os.fstat(current).st_ino)==(os.fstat(directory).st_dev,os.fstat(directory).st_ino),'backup-directory-changed')
        finally:os.close(current)
        checkpoint('published')
        receipt=dict(version=1,operation=operation,project=store.project,instance=store.instance,
                     root=pinned.as_dict(),verified_ns=time.time_ns(),manifest=manifest,destination=str(destination),
                     file_identity=[info.st_dev,info.st_ino],bytes=info.st_size)
        result=dict(published=True,receipt_saved=False,root=pinned.as_dict(),bytes=info.st_size,
                    manifest=manifest,destination=str(destination))
        try:
            checkpoint('receipt')
            path=authority.root/'last-export.json'
            with authority.files.exclusion(authority.root/'lifecycle.lock'):
                require(authority.pointer_value()['instance']==store.instance,'backup-instance-changed')
                try:before=authority.files.read(path)
                except FileNotFoundError:authority.files.create(path,canonical_bytes(receipt))
                else:authority.files.replace(path,canonical_bytes(receipt),before)
            result['receipt_saved']=True
        except (OSError,RecordError):
            # Already published. Do not turn a receipt failure into instructions
            # to re-export, overwrite or automatically remove that file.
            result['receipt_unavailable']='backup-receipt-unavailable'
        return result
    finally:
        if audit is not None:audit.close()
        if store is not None:store.close()
        os.close(directory)


def backup_status(authority):
    from .codec import decode_canonical,ObjectRef
    try:value=decode_canonical(authority.files.read(authority.root/'last-export.json'))
    except FileNotFoundError:return dict(verified_export_recorded=False)
    require(type(value) is dict and set(value)=={'version','operation','project','instance','root','verified_ns','manifest','destination','file_identity','bytes'} and
            value['version']==1 and value['project']==authority.project and type(value['verified_ns']) is int and value['verified_ns']>0,'invalid-backup-receipt')
    root=ObjectRef.parse(value['root']);current=authority.pointer_value()
    result=dict(verified_export_recorded=True,verified_ns=value['verified_ns'],same_instance=value['instance']==current['instance'],
                destination_availability='not_checked')
    if result['same_instance']:
        store=authority.store(readonly=True)
        try:result['different_root']=store.root().ref!=root
        finally:store.close()
    return result
