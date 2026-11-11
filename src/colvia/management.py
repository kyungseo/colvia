"""User-data management composition; no host settings or network by default.

The manager owns registered authority directories and pre-update logical backups.
Runtime selection holds an exclusive lease while it checks every retained store;
managed transactions share that lease. A runtime rollback never rolls data back.
"""
from pathlib import Path
import hashlib,uuid
from .codec import canonical_bytes,decode_canonical,require
from .storage.authority import Authority
from .storage.sqlite import _token
from .storage.files import platform_files
from .updates.slots import RuntimeSlots
from .updates.lease import open_managed_store
from .effects import PENDING
from .records import application_registry
from .graph import AuditBudget
from .backup_service import export_backup

class ManagerHome:
    def __init__(self,root,*,os_name,architecture,files=None):
        self.root=Path(root);self.files=files or platform_files();self.files.private_directory(self.root)
        self.os_name=os_name;self.architecture=architecture
        value=decode_canonical(self.files.read(self.root/'home.json'))
        require(value==dict(version=1,os=os_name,architecture=architecture),'manager-home-platform-mismatch')
        self.slots=RuntimeSlots(self.root/'runtime',os_name=os_name,architecture=architecture,files=self.files)
        for name in ('authorities','operations','backups'):self.files.private_directory(self.root/name)
    @classmethod
    def create(cls,root,*,os_name,architecture,files=None):
        root=Path(root);files=files or platform_files()
        require((os_name,architecture) in (('macos','arm64'),('windows','arm64'),('windows','x64')),'manager-platform-unavailable')
        files.create_directory(root)
        for name in ('authorities','operations','backups'):files.create_directory(root/name)
        RuntimeSlots.create(root/'runtime',os_name=os_name,architecture=architecture,files=files)
        files.create(root/'management.lock',b'')
        files.create(root/'home.json',canonical_bytes(dict(version=1,os=os_name,architecture=architecture)))
        return cls(root,os_name=os_name,architecture=architecture,files=files)
    def authority(self,project):
        require(type(project) is str and str(uuid.UUID(project))==project,'invalid-project-id')
        return Authority(self.root/'authorities'/project,project=project,files=self.files)
    def projects(self):
        names=[]
        for path in (self.root/'authorities').iterdir():
            require(len(names)<4096,'manager-project-count-limit')
            require(str(uuid.UUID(path.name))==path.name,'manager-project-entry-unavailable')
            authority=self.authority(path.name);names.append(authority.project)
        return tuple(sorted(names))
    def store(self,project,*,readonly=False):
        return open_managed_store(self.authority(project),self.slots,readonly=readonly)
    def requirements(self):
        readers=set();writers=set();states=[]
        for project in self.projects():
            authority=self.authority(project);store=authority.store(readonly=True)
            try:
                require(store.head(PENDING) is None,'manager-project-effect-pending')
                require(not authority.files.exists(authority.root/'pending.json'),'manager-project-activation-pending')
                requirements=store.requirements();readers.update(requirements['read']);writers.update(requirements['write'])
                states.append(dict(project=project,pointer=authority.pointer_value(),root=store.root().ref.as_dict()))
            finally:store.close()
        return readers,writers,states
    def update(self,*,operation,target,expected_selection,recovery=False,replacement=False,checkpoint=lambda _:None,activation_guard=lambda:None,expected_states=None,entry_activation=None):
        _token(operation)
        with self.files.exclusion(self.root/'management.lock'):
            if self.files.exists(self.root/'native-update.json'):
                pending=decode_canonical(self.files.read(self.root/'native-update.json'))
                require(pending['target']==target and entry_activation is not None,'native-entry-update-pending')
            if self.files.exists(self.root/'notice-app.pending'):
                pending=decode_canonical(self.files.read(self.root/'notice-app.pending'))
                require(pending['target']==target and entry_activation is not None,'notice-app-update-pending')
            area=self.root/'operations'/operation;self.files.create_directory(area)
            self.files.create(area/'intent.json',canonical_bytes(dict(version=1,operation=operation,target=target,
                selection_sha256=hashlib.sha256(expected_selection).hexdigest(),recovery=recovery,replacement=replacement)))
            def preflight(candidate):
                # RuntimeSlots holds the exclusive lease. No managed-store
                # transaction can publish between these reads and activation.
                read,write,states=self.requirements()
                require(expected_states is None or states==expected_states,'manager-review-state-changed')
                require(read<=candidate.read_capabilities and write<=candidate.write_capabilities,'runtime-capability-unavailable')
                destination=self.root/'backups'/operation;self.files.create_directory(destination)
                backups=[]
                for row in states:
                    authority=self.authority(row['project']);scratch=area/row['project'];self.files.create_directory(scratch)
                    result=export_backup(authority,destination=destination/(row['project']+'.colvia-export'),scratch=scratch,
                        operation=operation+'-'+row['project'],graph_budget=AuditBudget(2_000_000,8_000_000,64*1024**3),registry=application_registry())
                    require(result['published'] and result['root']==row['root'],'manager-backup-unconfirmed');backups.append(result)
                require(self.requirements()==(read,write,states),'manager-project-state-changed')
                self.files.create(area/'prepared.json',canonical_bytes(dict(version=1,states=states,backups=backups)))
                checkpoint('backed-up');activation_guard()
                if entry_activation is not None:entry_activation()
                activation_guard();return read,write
            result=self.slots.activate(target,expected_selection=expected_selection,read_requirements=(),write_requirements=(),
                                       recovery=recovery,replacement=replacement,before_activate=preflight)
            checkpoint('activated')
            self.files.create(area/'completed.json',canonical_bytes(dict(version=1,selection=result)))
            return dict(state='updated',records_preserved=True,settings_preserved=True,recovery_available=result['recovery'] is not None)
    def inspect_update(self,operation):
        """Inspect an interrupted update without retrying or restoring old data."""
        _token(operation);area=self.root/'operations'/operation
        intent=decode_canonical(self.files.read(area/'intent.json'));raw,state=self.slots.selection()
        require(intent['operation']==operation,'manager-update-identity-mismatch')
        if self.files.exists(area/'completed.json'):
            completed=decode_canonical(self.files.read(area/'completed.json'))
            return dict(state='completed' if completed['selection']==state else 'subsequently-changed')
        if hashlib.sha256(raw).hexdigest()==intent['selection_sha256']:return dict(state='not-activated')
        if state['selected']==intent['target'] and self.files.exists(area/'prepared.json'):
            prepared=decode_canonical(self.files.read(area/'prepared.json',4*1024*1024))
            _,_,states=self.requirements()
            require(states==prepared['states'],'manager-update-followup-required')
            self.slots.verify(state['selected']);return dict(state='activated-unrecorded',records_preserved=True)
        return dict(state='unknown')
