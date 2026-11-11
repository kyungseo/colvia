"""Manager-owned project setup, using retained-original ordered effects.

This source composition does not install a runtime, change host permissions or
choose Git from PATH. The native entry inventory is prepared by the installer.
"""
from pathlib import Path
from dataclasses import asdict
from contextlib import contextmanager,nullcontext
import base64,hashlib,os,shlex,uuid,sys
from .codec import canonical_bytes,decode_canonical,require
from .binding import Locator,ProjectBinding,WorkspaceRegistration,require_connection_root,same_plain_location
from .connection import Connections,PROJECT_KEY,workspace_key,workspace_payload
from .connection_boundary import check_connection_boundary, verified_reservation
from .adapters.git import discover,read_file
from .platforms.observation_port import location
from .platforms.project_launcher import project_launcher,project_block
from .lifecycle import ConnectFiles,Detach,owned_block
from .records import record,application_registry,operation_closure
from .graph import validate_closure
from .effects import guard
from .storage.authority import Authority
from .storage.sqlite import _token

BLOCK=b'<!-- colvia:managed:start -->\nThis project uses Colvia to retain agreed scope, submitted results and human decisions.\nRead `./colvia guide` once, then `./colvia ordinary list` for current work. Use command help only for the next needed action.\nProject rules still apply. An approved task includes preparation of its reviewable result; final result acceptance remains separate.\nDo not quote internal identifiers or instruction paths in normal replies.\n<!-- colvia:managed:end -->\n'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def topology_value(top):
    value=asdict(top);value['members']=list(value['members']);return value
def b64(raw):return None if raw is None else base64.b64encode(raw).decode('ascii')
def unpack(raw):return None if raw is None else base64.b64decode(raw,validate=True)

class ProjectSetup:
    def __init__(self,home,git=None,*,runtime_lease=None):self.home=home;self.git=git;self.runtime_lease=runtime_lease
    @contextmanager
    def management(self):
        # Same lock order as update: management, then runtime. Keep a slot
        # pinned over each short native setup step, never over a user wait.
        with self.home.files.exclusion(self.home.root/'management.lock'):
            with self.runtime_lease.hold() if self.runtime_lease else nullcontext():yield
    def preview(self,root):
        with self.runtime_lease.hold() if self.runtime_lease else nullcontext():return self._preview(root)
    def _entry(self):
        require(sys.platform in ('darwin','win32'),'connect-platform-port-unavailable')
        registry=decode_canonical(self.home.files.read(self.home.root/'entry.json'))
        require(type(registry) is dict and set(registry)=={'version','sha256','os','architecture'} and
                registry['version']==1 and registry['os']==self.home.os_name and registry['architecture']==self.home.architecture,'managed-entry-inventory-invalid')
        entry=self.home.root/'bin'/('colvia.exe' if self.home.os_name=='windows' else 'colvia');raw=self.home.files.read(entry,64*1024*1024)
        require(sha(raw)==registry['sha256'] and (self.home.os_name=='windows' or entry.stat().st_mode&0o111),'managed-entry-changed')
        return entry,registry
    def _plan(self,root,project,instance,workspace,nonce):
        root=Path(root);top=discover(root,self.git);require_connection_root(location(root),top)
        check_connection_boundary(self.home, self.git, top, overlap_code='connect-project-overlap', historical=True)
        entry,inventory=self._entry();launcher_name,launcher_mode,launcher=project_launcher(entry,self.home.root,self.home.os_name);locator=Locator(project,instance,1,nonce,workspace if top.kind=='plain' else None)
        locator_root=Path(top.common.path) if top.kind=='git' else root
        locator_path='colvia/connection.json' if top.kind=='git' else '.colvia-link.json'
        target=locator_root/locator_path;require(not os.path.lexists(target),'project-already-connected-or-repair-required')
        require(not any(os.path.lexists(root/name) for name in ('colvia','colvia.cmd','colvia.exe','colvia.ps1')),'project-launcher-already-present')
        require(self.home.os_name!='windows' or root!=Path(root.anchor),'windows-volume-root-project-unavailable')
        changes=[]
        for name in ('AGENTS.md','CLAUDE.md'):
            path=root/name
            try:before=read_file(path,1024*1024)
            except FileNotFoundError:before=None
            require(before is None or b'<!-- colvia:managed:' not in before,'entry-already-managed-or-ambiguous')
            suffix=(b'\n' if before and not before.endswith(b'\n') else b'')+project_block(BLOCK,self.home.os_name)
            after=(before or b'')+suffix
            mode='100755' if self.home.os_name!='windows' and before is not None and path.stat().st_mode&0o111 else '100644'
            changes.append(dict(role='entry',root='project',path=name,before=b64(before),after=b64(after),mode=mode))
        changes.append(dict(role='entry',root='project',path=launcher_name,before=None,after=b64(launcher),mode=launcher_mode))
        changes.append(dict(role='locator',root='locator',path=locator_path,before=None,after=b64(canonical_bytes(locator.payload())),mode='100644'))
        return dict(version=1,project=project,instance=instance,workspace=workspace,nonce=nonce,topology=topology_value(top),root=str(root),
                    locator_root=str(locator_root),locator=locator.payload(),entry=inventory,changes=changes)
    def _preview(self,root):
        value=self._plan(root,str(uuid.uuid4()),str(uuid.uuid4()),str(uuid.uuid4()),os.urandom(32).hex())
        # Normalize tuple-valued topology members to the canonical JSON shape.
        value=decode_canonical(canonical_bytes(value))
        return dict(plan=value,receipt=sha(canonical_bytes(value)),files=[c['path'] for c in value['changes']],
                    question='이 폴더에 Colvia를 적용할까요? 기존 파일과 규칙을 보존하고 작업 기록은 별도 보관합니다.')
    def _changes(self,plan):
        return [{**c,'before':unpack(c['before']),'after':unpack(c['after'])} for c in plan['changes']]
    def _port(self,authority,plan):
        if self.home.os_name=='windows':
            from .platforms.windows_connect import WindowsConnect as Port
        else:
            from .platforms.darwin_connect import DarwinConnect as Port
        return Port(authority.root,dict(project=Path(plan['root']),locator=Path(plan['locator_root'])))
    def start(self,*,operation,plan,receipt,statement):
        _token(operation);require(type(statement) is str and 0<len(statement)<=16384,'connect-statement-required')
        require(receipt==sha(canonical_bytes(plan)),'connect-review-changed')
        with self.management():
            actual=self._plan(plan['root'],plan['project'],plan['instance'],plan['workspace'],plan['nonce'])
            require(canonical_bytes(actual)==canonical_bytes(plan),'connect-review-changed')
            area=self.home.root/'operations'/operation;self.home.files.create_directory(area)
            self.home.files.create(area/'connect.json',canonical_bytes(dict(version=1,operation=operation,plan=plan,receipt=receipt,statement=statement)))
            authority=Authority.create(self.home.root/'authorities'/plan['project'],project=plan['project'],instance=plan['instance'],generation='initial',files=self.home.files)
            store=authority.store()
            try:
                top=discover(Path(plan['root']),self.git)
                require(canonical_bytes(topology_value(top)) == canonical_bytes(plan['topology']), 'connect-topology-changed')
                locator=Locator.parse(canonical_bytes(plan['locator']),kind=top.kind)
                binding=ProjectBinding(locator,top.kind,top.common if top.kind=='git' else top.root)
                Connections(store).connect(operation=operation+'-binding',binding=binding,observed=top,
                    workspace=WorkspaceRegistration(plan['workspace'],top.root,top.gitdir),verify_topology=lambda:discover(Path(plan['root']),self.git))
                binding_ref=store.head(PROJECT_KEY);entries=[]
                for c in self._changes(plan):
                    owned=c['after'] if c['before'] is None else c['after'][len(c['before']):]
                    entries.append(dict(role=c['role'],root=c['root'],path=c['path'],owned=b64(owned),existed=c['before'] is not None,mode=c['mode']))
                config=record('project.integration',dict(entries=entries),{'binding':('decision',binding_ref),'workspace':('decision',store.head(workspace_key(plan['workspace'])))})
                registry=application_registry()
                def check(view):
                    guard(view);require(view.head(PROJECT_KEY)==binding_ref,'connect-binding-changed')
                    validate_closure([config[0]],view,registry,operation_closure(registry))
                store.commit_heads(operation=operation+'-integration',expected={'project:integration':None},
                    changes={'project:integration':config[0]},objects=[config],validate=check)
                service=ConnectFiles(store,self._port(authority,plan));changes=self._changes(plan);preview=service.preview(changes)
                service.begin(operation=operation,changes=changes,receipt=preview['receipt'],statement=statement)
            finally:store.close()
        return dict(operation=operation,state='pending',project=plan['project'])
    def _resume_context(self,operation,*,readonly=False):
        """Caller owns management/runtime exclusion; never reacquire its locks."""
        _token(operation)
        area=self.home.root/'operations'/operation;raw=self.home.files.read(area/'connect.json',8*1024*1024)
        value=decode_canonical(raw)
        require(value['operation']==operation and value['receipt']==sha(canonical_bytes(value['plan'])),'connect-journal-changed');plan=value['plan']
        authority=self.home.authority(plan['project']);require(authority.pointer_value()['instance']==plan['instance'],'connect-authority-changed')
        store=authority.store(readonly=readonly)
        try:
            published = store.operation_result(operation+'-binding')
            service = ConnectFiles(store, self._port(authority, plan))
            state_ref = store.head(service.key(operation))
            require(published is not None and store.head(PROJECT_KEY) is not None and state_ref is not None,
                    'connect-preparation-incomplete')
            top=discover(Path(plan['root']),self.git)
            require(canonical_bytes(topology_value(top))==canonical_bytes(plan['topology']),'connect-topology-changed')
            _,entry=self._entry();require(entry==plan['entry'],'managed-entry-changed')
            state = service._load(state_ref)
            if state.payload['phase'] != 'completed':
                own = verified_reservation(store, plan, top, published)
                check_connection_boundary(self.home, self.git, top, overlap_code='connect-resume-project-overlap', own=own)
            return authority,store,service,value,raw
        except BaseException:store.close();raise

    def _resume_locked(self,operation,*,event=lambda _:None):
        authority,store,service,_,_=self._resume_context(operation)
        try:return service.advance(operation,event=event)
        finally:store.close()

    def resume(self,operation,*,event=lambda _:None):
        with self.management():return self._resume_locked(operation,event=event)

    def _detach_port(self,authority,locations):
        if self.home.os_name=='windows':
            from .platforms.windows_connect import WindowsDetach as Port
        else:
            from .platforms.darwin_detach import DarwinDetach as Port
        return Port(authority.root,locations)

    def detach_context(self,project,root):
        """Read stored ownership, not a guessed marker or a private trial journal."""
        from .records import link
        authority=self.home.authority(project);store=authority.store()
        try:
            connections=Connections(store);binding_ref,binding=connections.binding()
            top=discover(Path(root),self.git);require_connection_root(location(Path(root)),top)
            require(top.common==binding.location if top.kind=='git' else
                    same_plain_location(top.root,binding.location),'project-location-changed')
            # The managed files belong to the originally connected workspace.
            # Linked workspaces get their own identity, not ownership of these files.
            ref=store.head('project:integration');require(ref is not None,'managed-integration-unavailable')
            obj=application_registry().inspect(ref,store.load(ref),required=True)
            require(link(obj,'binding')==binding_ref,'managed-integration-stale')
            registered=application_registry().inspect(link(obj,'workspace'),store.load(link(obj,'workspace')),required=True)
            registered_root=workspace_payload(registered.payload).root
            require(registered_root==top.root if top.kind=='git' else
                    same_plain_location(registered_root,top.root),'integration-owner-workspace-required')
            locations=dict(project=Path(root),locator=Path(top.common.path) if top.kind=='git' else Path(root));changes=[]
            for e in obj.payload['entries']:
                path=locations[e['root']]/e['path'];current=read_file(path,1024*1024);owned=unpack(e['owned'])
                if e['role']=='entry' and e['path'] in ('AGENTS.md','CLAUDE.md'):
                    after=owned_block(current,owned)
                    if not e['existed'] and not after:after=None
                else:require(current==owned,'managed-integration-edited');after=None
                changes.append(dict(role=e['role'],root=e['root'],path=e['path'],before=current,after=after))
            port=self._detach_port(authority,locations);return authority,store,Detach(store,port),changes
        except BaseException:store.close();raise

    def detach_begin(self,*,operation,project,root,receipt,statement):
        _token(operation)
        with self.management():
            authority,store,service,changes=self.detach_context(project,root)
            try:
                preview=service.preview(changes);require(preview['receipt']==receipt,'detach-review-changed')
                top=discover(Path(root),self.git)
                value=dict(version=1,operation=operation,project=project,instance=authority.pointer_value()['instance'],
                    root=str(Path(root)),locator_root=top.common.path if top.kind=='git' else str(Path(root)))
                area=self.home.root/'operations'/operation;self.home.files.create_directory(area)
                self.home.files.create(area/'detach.json',canonical_bytes(value))
                return service.begin(operation=operation,changes=changes,receipt=receipt,statement=statement)
            finally:store.close()

    def detach_resume(self,operation):
        _token(operation)
        with self.management():
            value=decode_canonical(self.home.files.read(self.home.root/'operations'/operation/'detach.json'))
            require(value['version']==1 and value['operation']==operation,'detach-journal-changed')
            authority=self.home.authority(value['project'])
            require(authority.pointer_value()['instance']==value['instance'],'detach-authority-changed')
            store=authority.store()
            try:
                port=self._detach_port(authority,dict(project=Path(value['root']),locator=Path(value['locator_root'])))
                return Detach(store,port).advance(operation)
            finally:store.close()
