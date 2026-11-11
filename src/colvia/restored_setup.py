"""Explicit restored-instance routing with preserved owned integration bytes.

The old instance stays historical. This changes the project connection, never
re-accepts an old Work or treats imported process permission as live authority.
"""
from pathlib import Path
import os,shlex,uuid
from .codec import canonical_bytes,decode_canonical,require,ObjectRef
from .binding import Locator,ProjectBinding,WorkspaceRegistration,require_connection_root
from .connection import Connections,PROJECT_KEY,workspace_key,binding_payload
from .connection_boundary import check_connection_boundary, verified_reservation
from .project_setup import ProjectSetup,BLOCK,sha,b64,unpack,topology_value
from .platforms.observation_port import location
from .platforms.project_launcher import project_launcher,project_block
from .adapters.git import discover,read_file
from .records import record,link,application_registry,operation_closure
from .graph import validate_closure
from .lifecycle import ConnectFiles
from .effects import guard,PENDING
from .storage.sqlite import _token

class RestoredSetup(ProjectSetup):
    def _restored_plan(self,project,root,workspace,nonce):
        authority=self.home.authority(project);store=authority.store(readonly=True)
        try:
            require(store.needs_rebind(),'instance-rebind-not-pending');require(store.head(PENDING) is None,'imported-effect-inspection-only')
            old_ref=store.head(PROJECT_KEY);require(old_ref is not None,'restore-binding-unavailable')
            registry=application_registry();obj=registry.inspect(old_ref,store.load(old_ref),required=True);old=binding_payload(obj.payload)
            integration=store.head('project:integration');owned={}
            if integration:
                previous=registry.inspect(integration,store.load(integration),required=True)
                require(link(previous,'binding')==old_ref,'managed-integration-stale')
                owned={(e['root'],e['path']):e for e in previous.payload['entries']}
            root=Path(root);top=discover(root,self.git);require_connection_root(location(root),top)
            require(top.kind==old.kind,'restore-topology-kind-changed')
            check_connection_boundary(self.home, self.git, top, overlap_code='rebind-project-overlap')
            entry,entry_inventory=self._entry()
            locator=Locator(project,store.instance,old.locator.epoch+1,nonce,workspace if top.kind=='plain' else None)
            locator_root=Path(top.common.path) if top.kind=='git' else root
            locator_path='colvia/connection.json' if top.kind=='git' else '.colvia-link.json'
            changes=[];entries=[];unchanged=[]
            def add(role,root_name,path,before,after,owned_bytes,existed,mode):
                entries.append(dict(role=role,root=root_name,path=path,owned=b64(owned_bytes),existed=existed,mode=mode))
                if before!=after:changes.append(dict(role=role,root=root_name,path=path,before=b64(before),after=b64(after),mode=mode))
                else:unchanged.append(dict(root=root_name,path=path,sha256=sha(before),mode=mode))
            for name in ('AGENTS.md','CLAUDE.md'):
                path=root/name
                try:before=read_file(path,1024*1024)
                except FileNotFoundError:before=None
                mode='100755' if self.home.os_name!='windows' and before is not None and path.stat().st_mode&0o111 else '100644'
                previous=owned.get(('project',name))
                if before is not None and b'<!-- colvia:managed:' in before:
                    require(previous is not None,'entry-already-managed-or-ambiguous');part=unpack(previous['owned'])
                    require(before.count(part)==1,'detach-entry-edited-or-ambiguous')
                    after=before;existed=previous['existed']
                else:
                    part=(b'\n' if before and not before.endswith(b'\n') else b'')+project_block(BLOCK,self.home.os_name)
                    after=(before or b'')+part;existed=before is not None
                add('entry','project',name,before,after,part,existed,mode)
            launcher_name,launcher_mode,launcher=project_launcher(entry,self.home.root,self.home.os_name)
            # Do not silently reuse another platform's project entry. Historical
            # data stays readable; integration migration requires its own plan.
            if integration:
                old_launchers={name for owner,name in owned if owner=='project' and name in ('colvia','colvia.cmd','colvia.exe','colvia.ps1')}
                require(not old_launchers or old_launchers=={launcher_name},'restore-platform-integration-review-required')
            try:before=read_file(root/launcher_name,1024*1024)
            except FileNotFoundError:before=None
            if before is not None:
                previous=owned.get(('project',launcher_name));require(previous is not None and before==unpack(previous['owned']),'managed-integration-edited')
                require(self.home.os_name=='windows' or (root/launcher_name).stat().st_mode&0o111,'managed-integration-mode-changed')
            add('entry','project',launcher_name,before,launcher,launcher,False,launcher_mode)
            try:before=read_file(locator_root/locator_path,1024*1024)
            except FileNotFoundError:before=None
            require(before is None or before==canonical_bytes(old.locator.payload()),'stale-or-foreign-binding')
            after=canonical_bytes(locator.payload());add('locator','locator',locator_path,before,after,after,False,'100644')
            return dict(version=1,project=project,instance=store.instance,old_root=store.root().ref.as_dict(),old_binding=old_ref.as_dict(),
                old_integration=None if integration is None else integration.as_dict(),root=str(root),locator_root=str(locator_root),
                topology=topology_value(top),workspace=workspace,locator=locator.payload(),entry=entry_inventory,entries=entries,changes=changes,unchanged=unchanged)
        finally:store.close()
    def preview(self,project,root):
        with self.management():
            plan=self._restored_plan(project,root,str(uuid.uuid4()),os.urandom(32).hex())
            return dict(plan=plan,receipt=sha(canonical_bytes(plan)),files=[c['path'] for c in plan['changes']],
                question='복원한 기록을 이 프로젝트 폴더에 연결할까요? 과거 결과의 수락 기록은 그대로 보존합니다.')
    def start(self,*,operation,plan,receipt,statement):
        _token(operation);require(receipt==sha(canonical_bytes(plan)),'restore-rebind-review-changed')
        require(type(statement) is str and 0<len(statement)<=16384,'connect-statement-required')
        with self.management():
            actual=self._restored_plan(plan['project'],plan['root'],plan['workspace'],plan['locator']['binding_nonce'])
            require(canonical_bytes(actual)==canonical_bytes(plan),'restore-rebind-review-changed')
            area=self.home.root/'operations'/operation;self.home.files.create_directory(area)
            self.home.files.create(area/'rebind.json',canonical_bytes(dict(version=1,operation=operation,plan=plan,receipt=receipt,statement=statement)))
            self._prepare(operation,plan,statement)
        return dict(state='pending',operation=operation)
    def _port(self,authority,plan):
        if self.home.os_name=='windows':
            from .platforms.windows_connect import WindowsRebind as Port
        else:
            from .platforms.darwin_connect import DarwinRebind as Port
        return Port(authority.root,dict(project=Path(plan['root']),locator=Path(plan['locator_root'])))
    def _prepare(self,operation,plan,statement):
        authority=self.home.authority(plan['project']);require(authority.pointer_value()['instance']==plan['instance'],'restore-instance-changed')
        store=authority.store()
        try:
            top=discover(Path(plan['root']),self.git)
            require(canonical_bytes(topology_value(top))==canonical_bytes(plan['topology']),'connect-topology-changed')
            _,entry=self._entry();require(entry==plan['entry'],'managed-entry-changed')
            locations=dict(project=Path(plan['root']),locator=Path(plan['locator_root']))
            for item in plan['unchanged']:
                path=locations[item['root']]/item['path'];raw=read_file(path,1024*1024)
                mode='100755' if self.home.os_name!='windows' and path.stat().st_mode&0o111 else '100644'
                require(sha(raw)==item['sha256'] and mode==item['mode'],'restore-rebind-files-changed')
            locator=Locator.parse(canonical_bytes(plan['locator']),kind=top.kind);connection=Connections(store)
            service = ConnectFiles(store, self._port(authority, plan))
            published = store.operation_result(operation+'-binding')
            if published is None:
                require(store.root().ref==ObjectRef.parse(plan['old_root']),'restore-rebind-review-changed')
                check_connection_boundary(self.home, self.git, top, overlap_code='rebind-project-overlap')
                connection.rebind_restored(operation=operation+'-binding',binding=ProjectBinding(locator,top.kind,top.common if top.kind=='git' else top.root),
                    observed=top,workspace=WorkspaceRegistration(plan['workspace'],top.root,top.gitdir),statement=statement,
                    expected_binding=ObjectRef.parse(plan['old_binding']),verify_topology=lambda:discover(Path(plan['root']),self.git))
            else:
                state_ref = store.head(service.key(operation))
                if state_ref is None or service._load(state_ref).payload['phase'] != 'completed':
                    own = verified_reservation(store, plan, top, published)
                    check_connection_boundary(self.home, self.git, top, overlap_code='connect-resume-project-overlap', own=own)
            binding_ref,binding=connection.binding();require(binding.locator==locator,'restore-rebind-diverged')
            registry=application_registry()
            if store.operation_result(operation+'-integration') is None:
                old=None if plan['old_integration'] is None else ObjectRef.parse(plan['old_integration'])
                require(store.head('project:integration')==old,'managed-integration-stale')
                pair=record('project.integration',dict(entries=plan['entries']),{'binding':('decision',binding_ref),
                    'workspace':('decision',store.head(workspace_key(plan['workspace'])))})
                def check(view):
                    guard(view);require(view.head(PROJECT_KEY)==binding_ref,'restore-rebind-diverged')
                    validate_closure([pair[0]],view,registry,operation_closure(registry))
                store.commit_heads(operation=operation+'-integration',expected={'project:integration':old},changes={'project:integration':pair[0]},objects=[pair],validate=check)
            if store.head(service.key(operation)) is None:
                changes=self._changes(plan);preview=service.preview(changes)
                service.begin(operation=operation,changes=changes,receipt=preview['receipt'],statement=statement)
        finally:store.close()
    def resume(self,operation,*,event=lambda _:None):
        _token(operation)
        with self.management():
            value=decode_canonical(self.home.files.read(self.home.root/'operations'/operation/'rebind.json',8*1024*1024))
            require(value['operation']==operation and value['receipt']==sha(canonical_bytes(value['plan'])),'restore-rebind-journal-changed')
            plan=value['plan'];self._prepare(operation,plan,value['statement']);authority=self.home.authority(plan['project']);store=authority.store()
            try:return ConnectFiles(store,self._port(authority,plan)).advance(operation,event=event)
            finally:store.close()
