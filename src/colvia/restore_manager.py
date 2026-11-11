"""Logical restore composition, separate from runtime recovery and rebind.

Prepare verifies/imports into an unselected generation. Apply preserves a logical
backup of the current root, switches generations, and leaves the new instance
inspection-only. No work files, locators or host grants are imported as authority.
"""
from pathlib import Path
import hashlib,os,uuid
from contextlib import ExitStack,nullcontext
from .codec import canonical_bytes,decode_canonical,ObjectRef,require
from .backup import ImportedSnapshot,ExportBudget,supported_requirements
from .backup_service import export_backup
from .graph import AuditBudget
from .records import application_registry
from .maps import map_get
from .effects import PENDING
from .storage.authority import Authority
from .storage.sqlite import _token

LIMIT=64*1024**3
GRAPH=AuditBudget(2_000_000,8_000_000,LIMIT)

class RestoreManager:
    def __init__(self,home,*,lease=None):self.home=home;self.lease=lease
    def _runtime(self):return self.lease.hold() if self.lease else nullcontext()
    def prepare(self,*,operation,archive,cancelled=lambda:False):
        _token(operation);archive=Path(archive);home=self.home
        require(archive.is_absolute(),'restore-archive-required')
        for path in (archive,*archive.parents):require(not path.is_symlink(),'restore-archive-symlink')
        with home.files.exclusion(home.root/'management.lock'),self._runtime():
            area=home.root/'operations'/operation;home.files.create_directory(area)
            home.files.create(area/'restore-intent.json',canonical_bytes(dict(version=1,operation=operation)))
            registry=application_registry();caps=supported_requirements(registry)
            with ExitStack() as cleanup:
                with home.files.read_stream(archive,LIMIT) as stream:
                    snapshot=ImportedSnapshot(area/'import.sqlite3',stream,budget=ExportBudget(2_000_000,LIMIT),graph_budget=GRAPH,
                        registry=registry,capabilities=caps,writable_capabilities=caps)
                    cleanup.callback(snapshot.close)
                # The file adapter checks identity again on stream exit.
                project=snapshot.header['project'];require(str(uuid.UUID(project))==project,'invalid-project-id')
                location=home.root/'authorities'/project;created=not os.path.lexists(location)
                authority=Authority.create(location,project=project,instance=str(uuid.uuid4()),generation='empty',files=home.files) if created else home.authority(project)
                store=authority.store(readonly=True)
                try:
                    require(store.head(PENDING) is None,'manager-project-effect-pending')
                    require(not authority.files.exists(authority.root/'pending.json'),'manager-project-activation-pending')
                    old_root=store.root().ref;old_pointer=authority.pointer_value()
                finally:store.close()
                instance=str(uuid.uuid4());generation='restore-'+operation
                authority.import_candidate(generation,snapshot,operation=operation+'-import',instance=instance,cancelled=cancelled)
                plan=dict(version=1,operation=operation,project=project,created=created,old_pointer=old_pointer,old_root=old_root.as_dict(),
                    instance=instance,generation=generation,target_root=snapshot.header['root'],export_manifest=snapshot.manifest,
                    runtime=home.slots.selection()[1])
                home.files.create(area/'restore.json',canonical_bytes(plan))
                return dict(state='prepared',operation=operation,project=project,receipt=hashlib.sha256(canonical_bytes(plan)).hexdigest(),
                    question='현재 기록을 별도 보존하고 이 내보내기 기록으로 복원할까요? 복원 뒤 프로젝트 연결을 다시 확인합니다.')
    def _read(self,operation):
        _token(operation);plan=decode_canonical(self.home.files.read(self.home.root/'operations'/operation/'restore.json',4*1024*1024))
        require(plan['version']==1 and plan['operation']==operation,'restore-operation-mismatch')
        return plan,hashlib.sha256(canonical_bytes(plan)).hexdigest()
    @staticmethod
    def _target(plan,store):
        require(store.root().ref==ObjectRef.parse(plan['target_root']),'restore-target-changed')
        require(store.head(PENDING) is None,'imported-effect-inspection-only')
    def apply(self,*,operation,receipt,checkpoint=lambda _:None):
        home=self.home;plan,expected=self._read(operation);require(receipt==expected,'restore-review-changed')
        with home.files.exclusion(home.root/'management.lock'),self._runtime():
            require(home.slots.selection()[1]==plan['runtime'],'runtime-selection-changed')
            authority=home.authority(plan['project']);require(authority.pointer_value()==plan['old_pointer'],'restore-source-changed')
            source=authority.store(readonly=True)
            try:
                require(source.root().ref==ObjectRef.parse(plan['old_root']),'restore-source-changed')
                require(source.head(PENDING) is None,'manager-project-effect-pending')
                area=home.root/'operations'/operation;scratch=area/'backup-scratch';home.files.create_directory(scratch)
                saved=export_backup(authority,destination=home.root/'backups'/(operation+'.colvia-export'),scratch=scratch,
                    operation=operation+'-before',graph_budget=GRAPH,registry=application_registry())
                require(saved['published'] and saved['root']==plan['old_root'],'restore-backup-unconfirmed')
                checkpoint('backed-up')
                def effects(root):require(map_get(root.heads,PENDING,source.load) is None,'manager-project-effect-pending')
                authority.activate_restore(operation+'-switch',target_generation=plan['generation'],instance=plan['instance'],
                    expected_root=ObjectRef.parse(plan['old_root']),target_root=ObjectRef.parse(plan['target_root']),
                    validate_effects=effects,validate_target=lambda store:self._target(plan,store),checkpoint=checkpoint)
                home.files.create(area/'restore-completed.json',canonical_bytes(dict(version=1,pointer=authority.pointer_value(),root=plan['target_root'])))
                return dict(state='restored-needs-rebind',project=plan['project'],records_preserved=True,workspace_files_changed=False)
            finally:source.close()
    def resume(self,*,operation,receipt):
        home=self.home;plan,expected=self._read(operation);require(receipt==expected,'restore-review-changed')
        with home.files.exclusion(home.root/'management.lock'),self._runtime():
            require(home.slots.selection()[1]==plan['runtime'],'runtime-selection-changed')
            authority=home.authority(plan['project'])
            pending=authority.root/'pending.json'
            if not authority.files.exists(pending):
                status=self.inspect(operation)
                require(status['state'] in ('restored-needs-rebind','restored-and-rebound'),'restore-recovery-not-pending')
                return status
            require(decode_canonical(authority.files.read(pending))==dict(version=1,operation=operation+'-switch'),'restore-operation-mismatch')
            def effects(root):
                source=authority.store(readonly=True)
                try:require(map_get(root.heads,PENDING,source.load) is None,'manager-project-effect-pending')
                finally:source.close()
            authority.recover(operation+'-switch',complete=True,validate_effects=effects,validate_target=lambda store:self._target(plan,store))
            return self.inspect(operation)

    def inspect(self,operation):
        plan,_=self._read(operation);authority=self.home.authority(plan['project']);pointer=authority.pointer_value()
        if authority.files.exists(authority.root/'pending.json'):return dict(state='recovery-required',project=plan['project'])
        if pointer==plan['old_pointer']:return dict(state='not-activated',project=plan['project'])
        if pointer['instance']==plan['instance'] and pointer['generation']==plan['generation']:
            store=authority.store(readonly=True)
            try:return dict(state='restored-needs-rebind' if store.needs_rebind() else 'restored-and-rebound',project=plan['project'])
            finally:store.close()
        return dict(state='subsequently-changed',project=plan['project'])
