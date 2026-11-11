"""Windows logical export protocol using a native destination port."""
from pathlib import Path
import uuid,time
from .codec import RecordError,require,canonical_bytes
from .graph import GraphAudit
from .backup import ExportReader,ExportBudget,write_export
from .storage.sqlite import _token
from .platforms.windows_backup import Destination


def export_backup(authority,*,destination,scratch,operation,graph_budget,registry,
                  cancelled=lambda:False,checkpoint=lambda _:None,port=Destination):
    from .backup_service import export_size
    _token(operation);destination=Path(destination);scratch=Path(scratch)
    require(destination.is_absolute() and destination.name not in ('','.','..'),'backup-destination-required')
    require(scratch.is_absolute() and scratch.is_dir(),'backup-scratch-required')
    prepared='.colvia-export-'+uuid.uuid4().hex[:16]
    with port(destination.parent) as files:
        require(not files.exists(destination.name),'backup-destination-exists')
        store=authority.store(readonly=True);audit=None
        try:
            pinned=store.root().ref
            audit=GraphAudit(scratch/('a-'+uuid.uuid4().hex[:16]+'.db'),graph_budget)
            audit.run(pinned,store.load,registry,cancelled=cancelled,require_known=True)
            estimate=export_size(store.project,audit)
            require(files.free_bytes()>=estimate,'backup-insufficient-space')
            with files.create(prepared) as stream:
                manifest=write_export(stream,project=store.project,audit=audit,load=store.load,cancelled=cancelled)
            checkpoint('flushed');before=files.stamp(prepared)
            with files.read(prepared,estimate) as stream:
                reader=ExportReader(stream,ExportBudget(audit.count,estimate));expected=iter(audit.refs());count=0
                require(reader.root==pinned,'backup-root-mismatch')
                for ref,_ in reader.objects():
                    require(not cancelled(),'export-cancelled');require(ref==next(expected,None),'backup-object-mismatch');count+=1
                require(reader.complete and count==audit.count and next(expected,None) is None and reader.manifest==manifest,'backup-incomplete')
            require(files.stamp(prepared)==before,'backup-file-changed');checkpoint('verified')
            require(not cancelled(),'export-cancelled');store.root()
            files.publish(prepared,destination.name,before);checkpoint('published')
            receipt=dict(version=1,operation=operation,project=store.project,instance=store.instance,root=pinned.as_dict(),
                verified_ns=time.time_ns(),manifest=manifest,destination=str(destination),file_identity=list(before['identity']),bytes=before['size'])
            result=dict(published=True,receipt_saved=False,root=pinned.as_dict(),bytes=before['size'],manifest=manifest,destination=str(destination))
            try:
                checkpoint('receipt')
                with authority.files.exclusion(authority.root/'lifecycle.lock'):
                    require(authority.pointer_value()['instance']==store.instance,'backup-instance-changed')
                    path=authority.root/'last-export.json'
                    try:old=authority.files.read(path)
                    except FileNotFoundError:authority.files.create(path,canonical_bytes(receipt))
                    else:authority.files.replace(path,canonical_bytes(receipt),old)
                result['receipt_saved']=True
            except (OSError,RecordError):result['receipt_unavailable']='backup-receipt-unavailable'
            return result
        finally:
            if audit is not None:audit.close()
            store.close()
